#!/usr/bin/env python3
"""
LED Controller for autoRain - Orange Pi Zero 2 RGB LED Control with Smooth PWM

Working software PWM using per-pin threads with gpiod.
Supports rainbow chase effect with configurable speed.

LED Pin Configuration (from led-pins.conf):
  LED1 (Closest to eth0): R=232, G=75, B=71
  LED2 (Middle):          R=230, G=74, B=233
  LED3 (Farthest):        R=69,  G=73, B=72
"""

import gpiod
import time
import threading
import colorsys
import logging
import atexit

log = logging.getLogger("autorain.led")

# ================= LED PIN CONFIGURATION =================

GPIO_CHIP = "/dev/gpiochip1"

LED1_R, LED1_G, LED1_B = 232, 75, 71
LED2_R, LED2_G, LED2_B = 230, 74, 233
LED3_R, LED3_G, LED3_B = 69, 73, 72

ALL_PINS = [LED1_R, LED1_G, LED1_B, LED2_R, LED2_G, LED2_B, LED3_R, LED3_G, LED3_B]

# ================= GLOBAL STATE =================

_chip = None
_lines = None
_running = False
_pwm_threads = []
_lock = threading.Lock()
_animation_thread = None
_animation_stop = threading.Event()

# Per-LED RGB targets (0-255)
_targets = {
    1: {'r': 0, 'g': 0, 'b': 0},
    2: {'r': 0, 'g': 0, 'b': 0},
    3: {'r': 0, 'g': 0, 'b': 0},
}


# ================= GPIO INIT =================

def _release_sysfs_pins():
    """Release any GPIO pins held by sysfs."""
    for pin in ALL_PINS:
        try:
            with open("/sys/class/gpio/unexport", "w") as f:
                f.write(str(pin))
        except:
            pass


def _init_gpio():
    """Initialize GPIO chip and request all LED lines."""
    global _chip, _lines
    
    if _lines is not None:
        return True
    
    _release_sysfs_pins()
    
    try:
        _chip = gpiod.Chip(GPIO_CHIP)
        config = gpiod.LineSettings(
            direction=gpiod.line.Direction.OUTPUT,
            output_value=gpiod.line.Value.INACTIVE
        )
        _lines = _chip.request_lines(
            consumer="autorain-led",
            config={pin: config for pin in ALL_PINS}
        )
        log.info("[led] GPIO initialized")
        return True
    except Exception as e:
        log.error(f"[led] GPIO init failed: {e}")
        return False


def _cleanup_gpio():
    """Release GPIO resources."""
    global _chip, _lines
    
    if _lines:
        try:
            _lines.set_values({pin: gpiod.line.Value.INACTIVE for pin in ALL_PINS})
            _lines.release()
        except:
            pass
        _lines = None
    
    if _chip:
        try:
            _chip.close()
        except:
            pass
        _chip = None


# ================= PWM ENGINE =================

def _pwm_thread(led_id, pin, color_key):
    """Per-pin PWM thread - toggles based on target value."""
    global _running
    
    while _running:
        with _lock:
            val = _targets[led_id][color_key]
        
        if _lines is None:
            time.sleep(0.01)
            continue
        
        try:
            if val > 0:
                _lines.set_values({pin: gpiod.line.Value.ACTIVE})
                time.sleep(val / 255 * 0.001)
            if val < 255:
                _lines.set_values({pin: gpiod.line.Value.INACTIVE})
                time.sleep((255 - val) / 255 * 0.001)
        except:
            time.sleep(0.001)


def start_pwm():
    """Start PWM engine with per-pin threads."""
    global _running, _pwm_threads
    
    if _running:
        return True
    
    if not _init_gpio():
        return False
    
    _running = True
    _pwm_threads = []
    
    # Create thread for each LED pin
    led_pins = [
        (1, LED1_R, 'r'), (1, LED1_G, 'g'), (1, LED1_B, 'b'),
        (2, LED2_R, 'r'), (2, LED2_G, 'g'), (2, LED2_B, 'b'),
        (3, LED3_R, 'r'), (3, LED3_G, 'g'), (3, LED3_B, 'b'),
    ]
    
    for led_id, pin, color_key in led_pins:
        t = threading.Thread(
            target=_pwm_thread,
            args=(led_id, pin, color_key),
            daemon=True
        )
        _pwm_threads.append(t)
        t.start()
    
    log.info("[led] PWM started (9 threads)")
    return True


def stop_pwm():
    """Stop PWM engine."""
    global _running
    _running = False
    all_off()
    log.info("[led] PWM stopped")


# ================= COLOR CONTROL =================

def set_led(led_id, r, g, b):
    """Set single LED color (0-255 each)."""
    with _lock:
        _targets[led_id]['r'] = max(0, min(255, int(r)))
        _targets[led_id]['g'] = max(0, min(255, int(g)))
        _targets[led_id]['b'] = max(0, min(255, int(b)))


def set_all(r, g, b):
    """Set all LEDs to same color."""
    set_led(1, r, g, b)
    set_led(2, r, g, b)
    set_led(3, r, g, b)


def all_off():
    """Turn all LEDs off."""
    with _lock:
        for led_id in _targets:
            _targets[led_id] = {'r': 0, 'g': 0, 'b': 0}
    
    if _lines:
        try:
            _lines.set_values({pin: gpiod.line.Value.INACTIVE for pin in ALL_PINS})
        except:
            pass


def hue_to_rgb(hue):
    """Convert hue (0.0-1.0) to RGB (0-255)."""
    r, g, b = colorsys.hsv_to_rgb(hue % 1.0, 1.0, 1.0)
    return int(r * 255), int(g * 255), int(b * 255)


# ================= ANIMATION ENGINE =================

def _stop_animation():
    """Signal current animation to stop."""
    _animation_stop.set()


def _wait_animation(timeout=1.0):
    """Wait for animation thread to finish."""
    global _animation_thread
    if _animation_thread and _animation_thread.is_alive():
        _animation_thread.join(timeout=timeout)


def _start_animation(func, *args, **kwargs):
    """Start animation in background thread."""
    global _animation_thread
    
    _stop_animation()
    _wait_animation()
    
    _animation_stop.clear()
    _animation_thread = threading.Thread(
        target=func, args=args, kwargs=kwargs,
        daemon=True, name="led-anim"
    )
    _animation_thread.start()


# ================= EFFECTS =================

def flash_color(r, g, b, times=2, duration=0.3):
    """Flash all LEDs a color."""
    for _ in range(times):
        set_all(r, g, b)
        time.sleep(duration)
        all_off()
        time.sleep(duration / 2)


def flash_red(times=2):
    flash_color(255, 0, 0, times)


def flash_green(times=2):
    flash_color(0, 255, 0, times)


def flash_blue(times=2):
    flash_color(0, 0, 255, times)


def test_colors():
    """Flash red, blue, green to test LEDs."""
    log.info("[led] Color test")
    flash_color(255, 0, 0, 2, 0.4)
    time.sleep(0.2)
    flash_color(0, 0, 255, 2, 0.4)
    time.sleep(0.2)
    flash_color(0, 255, 0, 2, 0.4)


def fade_to(r, g, b, steps=64, delay=0.015):
    """Smoothly fade all LEDs to a color."""
    with _lock:
        r1 = _targets[1]['r']
        g1 = _targets[1]['g']
        b1 = _targets[1]['b']
    
    for i in range(steps + 1):
        if _animation_stop.is_set():
            return
        t = i / steps
        set_all(
            int(r1 + (r - r1) * t),
            int(g1 + (g - g1) * t),
            int(b1 + (b - b1) * t)
        )
        time.sleep(delay)


# ================= RAINBOW CHASE =================

# Global speed modifier for dynamic speed changes
_chase_speed = 50
_chase_speed_lock = threading.Lock()

def set_chase_speed(speed):
    """Dynamically change rainbow chase speed (1-100)."""
    global _chase_speed
    with _chase_speed_lock:
        _chase_speed = max(1, min(100, speed))
    log.info(f"[led] Chase speed set to {speed}")

def get_chase_speed():
    """Get current chase speed."""
    with _chase_speed_lock:
        return _chase_speed

def rainbow_chase(speed=None, duration=None):
    """
    Rainbow chase effect - each LED shows different hue, rotating.
    
    Args:
        speed: 1-100, higher = faster. None = use dynamic _chase_speed
        duration: seconds to run, None = forever
    """
    global _chase_speed
    
    hue = 0.0
    offset = 0.15  # Hue difference between LEDs
    delay = 0.02
    
    start = time.time()
    
    while not _animation_stop.is_set():
        # Use dynamic speed if not specified
        if speed is None:
            with _chase_speed_lock:
                current_speed = _chase_speed
        else:
            current_speed = speed
        
        # Speed controls hue increment (0.001 to 0.02)
        hue_step = 0.001 + (current_speed / 100.0) * 0.019
        
        r1, g1, b1 = hue_to_rgb(hue)
        r2, g2, b2 = hue_to_rgb(hue + offset)
        r3, g3, b3 = hue_to_rgb(hue + offset * 2)
        
        set_led(1, r1, g1, b1)
        set_led(2, r2, g2, b2)
        set_led(3, r3, g3, b3)
        
        hue += hue_step
        time.sleep(delay)
        
        if duration and (time.time() - start) >= duration:
            break


def rainbow_fade(speed=50, duration=None):
    """Rainbow fade - all LEDs same color, cycling through spectrum."""
    hue = 0.0
    hue_step = 0.001 + (speed / 100.0) * 0.019
    delay = 0.02
    
    start = time.time()
    
    while not _animation_stop.is_set():
        r, g, b = hue_to_rgb(hue)
        set_all(r, g, b)
        
        hue += hue_step
        time.sleep(delay)
        
        if duration and (time.time() - start) >= duration:
            break


def pulse_color(r, g, b, speed=50, duration=None):
    """Pulse a color (breathe effect)."""
    import math
    
    phase = 0.0
    phase_step = 0.05 + (speed / 500.0)
    delay = 0.02
    
    start = time.time()
    
    while not _animation_stop.is_set():
        brightness = 0.1 + 0.9 * (0.5 + 0.5 * math.sin(phase))
        set_all(int(r * brightness), int(g * brightness), int(b * brightness))
        
        phase += phase_step
        time.sleep(delay)
        
        if duration and (time.time() - start) >= duration:
            break


# ================= BOOT STAGE ANIMATIONS =================

def boot_starting():
    """System starting - quick color test then chase."""
    log.info("[led] Boot starting")
    if not _running:
        start_pwm()
        time.sleep(0.2)
    test_colors()
    _start_animation(rainbow_chase, speed=70)


def boot_bt_waiting():
    """Waiting for Bluetooth - blue pulse."""
    log.info("[led] BT waiting")
    _start_animation(pulse_color, 0, 100, 255, speed=40)


def boot_bt_connected():
    """Bluetooth connected - green flash, then faster chase."""
    log.info("[led] BT connected")
    _stop_animation()
    _wait_animation()
    flash_green(3)
    set_chase_speed(65)  # Speed up chase
    _start_animation(rainbow_chase)  # Uses dynamic speed


def boot_wifi_connected():
    """WiFi connected - start rainbow chase."""
    log.info("[led] WiFi connected - rainbow chase")
    set_chase_speed(50)
    _start_animation(rainbow_chase)


def boot_ready():
    """System ready for palera1n."""
    log.info("[led] Ready")
    set_chase_speed(65)
    _start_animation(rainbow_chase)


def palera1n_waiting():
    """Waiting for iOS device - cyan pulse."""
    log.info("[led] Waiting for device")
    _start_animation(pulse_color, 0, 255, 255, speed=30)


def palera1n_device_detected():
    """iOS device detected - speed up chase significantly."""
    log.info("[led] Device detected - fast chase!")
    set_chase_speed(85)
    _start_animation(rainbow_chase)


def palera1n_dfu_step1():
    """DFU step 1 - yellow pulse."""
    log.info("[led] DFU step 1")
    _start_animation(pulse_color, 255, 200, 0, speed=60)


def palera1n_dfu_step2():
    """DFU step 2 - orange fast pulse."""
    log.info("[led] DFU step 2")
    _start_animation(pulse_color, 255, 100, 0, speed=80)


def palera1n_booting():
    """Kernel booting - SUPER FAST rainbow!"""
    log.info("[led] Booting kernel - FAST!")
    set_chase_speed(100)  # Maximum speed!
    _start_animation(rainbow_chase)


def palera1n_complete():
    """Jailbreak complete - victory celebration!"""
    log.info("[led] Complete! Victory celebration!")
    _stop_animation()
    _wait_animation()
    
    # 5 seconds of SUPER FAST rainbow
    log.info("[led] 5 seconds of fast rainbow...")
    start = time.time()
    hue = 0.0
    while time.time() - start < 5:
        r, g, b = hue_to_rgb(hue)
        set_all(r, g, b)
        hue += 0.03  # Very fast
        time.sleep(0.01)
    
    # Now LOUD color blinking - flash through all colors
    log.info("[led] Color flash celebration!")
    colors = [
        (255, 0, 0),     # Red
        (255, 128, 0),   # Orange
        (255, 255, 0),   # Yellow
        (0, 255, 0),     # Green
        (0, 255, 255),   # Cyan
        (0, 0, 255),     # Blue
        (128, 0, 255),   # Purple
        (255, 0, 255),   # Magenta
        (255, 255, 255), # White
    ]
    
    # Flash through colors 3 times
    for _ in range(3):
        for r, g, b in colors:
            set_all(r, g, b)
            time.sleep(0.12)
            all_off()
            time.sleep(0.05)
    
    # Final green glow
    flash_green(5)
    set_all(0, 150, 0)


def palera1n_error():
    """Error - red flash and pulse."""
    log.info("[led] Error!")
    _stop_animation()
    _wait_animation()
    flash_color(255, 0, 0, 5, 0.2)
    _start_animation(pulse_color, 255, 0, 0, speed=40)


# ================= CLEANUP =================

def cleanup():
    """Clean shutdown."""
    global _running
    log.info("[led] Cleanup")
    _stop_animation()
    _wait_animation(0.5)
    _running = False
    time.sleep(0.05)
    all_off()
    _cleanup_gpio()


atexit.register(cleanup)


# ================= MAIN =================

if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    
    print("LED Controller")
    print("=" * 40)
    
    start_pwm()
    time.sleep(0.3)
    
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    try:
        if cmd == "test":
            test_colors()
        elif cmd == "red":
            set_all(255, 0, 0)
            time.sleep(3)
        elif cmd == "green":
            set_all(0, 255, 0)
            time.sleep(3)
        elif cmd == "blue":
            set_all(0, 0, 255)
            time.sleep(3)
        elif cmd == "chase":
            print("Rainbow chase (Ctrl+C to stop)...")
            rainbow_chase(speed=50, duration=30)
        elif cmd == "fade":
            print("Rainbow fade (Ctrl+C to stop)...")
            rainbow_fade(speed=50, duration=30)
        elif cmd == "boot":
            boot_starting()
            time.sleep(5)
            boot_bt_waiting()
            time.sleep(3)
            boot_bt_connected()
            time.sleep(2)
            boot_ready()
            time.sleep(5)
        else:
            print("Commands: test, red, green, blue, chase, fade, boot")
    except KeyboardInterrupt:
        print("\nStopped")
    
    cleanup()
