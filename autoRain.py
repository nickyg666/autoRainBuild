#!/usr/bin/env python3
"""
autoRain - Automated iOS Jailbreak System for Orange Pi Zero 2

Boot chain: getty@tty1 (autologin) -> .bash_profile -> autoRain.py

Features:
- Bluetooth speaker connection with power cycle recovery
- Audio prompts for DFU steps
- LED visual feedback via led_controller
- pexpect-based palera1n automation
"""

import subprocess
import time
import pexpect
import sys
import os
import logging
import atexit
import threading

# Add script directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ================= LOGGING =================

LOG_FILE = "/home/orangepi/autoRain.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)

log = logging.getLogger("autorain")

# ================= LED CONTROLLER =================

LED_AVAILABLE = False
led = None

try:
    import led_controller as led
    LED_AVAILABLE = True
    log.info("[led] LED controller loaded")
except ImportError as e:
    log.warning(f"[led] LED controller not available: {e}")


def led_call(func_name, *args, **kwargs):
    """Safely call LED function."""
    if not LED_AVAILABLE or led is None:
        return
    try:
        func = getattr(led, func_name, None)
        if func:
            func(*args, **kwargs)
    except Exception as e:
        log.debug(f"[led] {func_name} error: {e}")


# ================= ENVIRONMENT =================

os.environ["PATH"] = "/usr/sbin:/sbin:/usr/local/sbin:/home/orangepi:" + os.environ.get("PATH", "")
os.environ["PULSE_SERVER"] = "unix:/run/user/1000/pulse/native"

# ================= CONFIG =================

BT_MAC = "11:81:AA:11:88:72"
BT_TIMEOUT = 60  # Max seconds to wait for BT
SPEAKER_POWER_SCRIPT = "/usr/local/bin/speaker-power.sh"

AUDIO_DIR = "/home/orangepi/autoRain/audio/sounds"
READY_MP3 = f"{AUDIO_DIR}/ready.mp3"
STEP1_MP3 = f"{AUDIO_DIR}/step1.mp3"
STEP2_MP3 = f"{AUDIO_DIR}/step2.mp3"
FINISH_MP3 = f"{AUDIO_DIR}/complete.mp3"
RETRY_MP3 = f"{AUDIO_DIR}/retry.mp3"
SHUTDOWN_MP3 = f"{AUDIO_DIR}/shutdown.mp3"

# Fallback to home dir if audio dir doesn't exist
if not os.path.exists(AUDIO_DIR):
    AUDIO_DIR = "/home/orangepi"
    READY_MP3 = f"{AUDIO_DIR}/ready.mp3"
    STEP1_MP3 = f"{AUDIO_DIR}/step1.mp3"
    STEP2_MP3 = f"{AUDIO_DIR}/step2.mp3"
    FINISH_MP3 = f"{AUDIO_DIR}/complete.mp3"
    RETRY_MP3 = f"{AUDIO_DIR}/retry.mp3"
    SHUTDOWN_MP3 = f"{AUDIO_DIR}/shutdown.mp3"

PALERA1N_CMD = "sudo palera1n -l"
MAX_RETRIES = 3

# ================= UTILITY =================

def run_cmd(cmd, timeout=10):
    """Run command and return (success, output)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout
    except subprocess.TimeoutExpired:
        return False, ""
    except Exception as e:
        return False, str(e)


def kill_process(name):
    """Kill processes by name."""
    try:
        result = subprocess.run(["pgrep", "-f", name], capture_output=True, text=True)
        for pid in result.stdout.strip().split('\n'):
            if pid:
                subprocess.run(["sudo", "kill", "-9", pid], capture_output=True)
    except:
        pass


# ================= BLUETOOTH =================

def bt_is_connected():
    """Check if Bluetooth speaker is connected."""
    success, output = run_cmd(["bluetoothctl", "info", BT_MAC])
    return success and "Connected: yes" in output


def bt_connect():
    """Attempt to connect to Bluetooth speaker with a shorter timeout."""
    log.info(f"[bt] Connecting to {BT_MAC}...")
    try:
        result = subprocess.run(
            ["bluetoothctl", "connect", BT_MAC],
            capture_output=True,
            text=True,
            timeout=8  # Wait up to 8 seconds for the connect command
        )
        if result.returncode == 0:
            log.info("[bt] Connect command succeeded")
            return True
        elif "already connected" in result.stdout.lower():
            log.info("[bt] Already connected")
            return True
        else:
            # Log what went wrong for debugging
            output = result.stdout + result.stderr
            if "already" in output.lower():
                log.info("[bt] Speaker already connected")
                return True
            log.debug(f"[bt] Connect output: {output.strip()}")
            return False
    except subprocess.TimeoutExpired:
        log.warning("[bt] Connect command timed out (speaker may still be processing)")
        return False
    except Exception as e:
        log.error(f"[bt] Connect error: {e}")
        return False


def bt_power_cycle():
    """Power cycle the Bluetooth speaker via GPIO 79."""
    log.info("[bt] Power cycling speaker...")
    try:
        subprocess.run(
            ["sudo", SPEAKER_POWER_SCRIPT],
            capture_output=True,
            timeout=10
        )
        log.info("[bt] Power cycle complete, waiting for speaker boot...")
        time.sleep(3)  # Wait for speaker to boot
        return True
    except Exception as e:
        log.error(f"[bt] Power cycle failed: {e}")
        return False


def bt_disconnect():
    """Disconnect from Bluetooth speaker."""
    try:
        subprocess.run(
            ["bluetoothctl", "disconnect", BT_MAC],
            capture_output=True,
            timeout=3
        )
    except:
        pass


def wait_for_bluetooth():
    """
    Block until Bluetooth speaker is connected.
    
    Sequence:
    1. Power cycle speaker to ensure it boots fresh
    2. Wait for full initialization
    3. Rapidly attempt connects immediately after boot
    4. If fails, retry from step 1
    """
    # Set volume early to ensure all audio plays at safe level
    set_volume("2%")
    
    log.info("[bt] === Waiting for Bluetooth speaker ===")
    led_call("boot_bt_waiting")
    
    start_time = time.time()
    cycle_attempt = 0
    
    while time.time() - start_time < BT_TIMEOUT:
        cycle_attempt += 1
        log.info(f"[bt] Power cycle attempt {cycle_attempt}...")
        
        # Power cycle the speaker
        bt_power_cycle()
        
        # After power cycle, the speaker is booting
        # Wait a bit longer for full initialization (speaker-specific timing)
        log.info("[bt] Waiting for speaker to fully boot...")
        time.sleep(2)
        
        # Now attempt rapid connects while speaker is fresh
        for connect_attempt in range(1, 5):
            log.info(f"[bt] Connect attempt {connect_attempt} (after boot {cycle_attempt})...")
            
            # Try to connect
            bt_connect()
            time.sleep(1)  # Wait for connection to establish
            
            # Check if connected
            if bt_is_connected():
                log.info("[bt] ✓ Speaker connected!")
                led_call("boot_bt_connected")
                return True
            
            log.warning(f"[bt] Connect attempt {connect_attempt} failed")
            
            # Disconnect before next attempt to clear Bluetooth state
            if connect_attempt < 4:  # Don't disconnect after last attempt before retry
                bt_disconnect()
                time.sleep(0.5)
        
        # If all rapid connects failed, try next power cycle
        log.warning(f"[bt] All connects failed after boot {cycle_attempt}, will retry...")
        time.sleep(1)
    
    log.error(f"[bt] ✗ Failed to connect after {BT_TIMEOUT}s")
    led_call("palera1n_error")
    return False


# ================= AUDIO =================

def get_pulse_socket():
    """Find PulseAudio socket."""
    paths = [
        "/run/user/1000/pulse/native",
        "/run/pulse/native",
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return paths[0]


def set_volume(level="2%"):
    """Set audio volume."""
    try:
        env = os.environ.copy()
        env["PULSE_SERVER"] = f"unix:{get_pulse_socket()}"
        subprocess.run(
            ["pactl", "set-sink-volume", "@DEFAULT_SINK@", level],
            env=env,
            capture_output=True,
            timeout=2
        )
    except:
        pass


def play_audio(mp3_path, wait=True, wait_time=None):
    """Play audio file via mpg123."""
    if not os.path.exists(mp3_path):
        log.warning(f"[audio] File not found: {mp3_path}")
        return
    
    log.info(f"[audio] Playing {os.path.basename(mp3_path)}")
    
    try:
        env = os.environ.copy()
        env["PULSE_SERVER"] = f"unix:{get_pulse_socket()}"
        
        if wait:
            start = time.time()
            subprocess.run(
                ["mpg123", "-q", mp3_path],
                env=env,
                timeout=30
            )
            # If wait_time specified, ensure we wait at least that long
            if wait_time:
                elapsed = time.time() - start
                if elapsed < wait_time:
                    time.sleep(wait_time - elapsed)
        else:
            subprocess.Popen(
                ["mpg123", "-q", mp3_path],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    except Exception as e:
        log.warning(f"[audio] Playback error: {e}")


# ================= USBMUXD =================

def start_usbmuxd():
    """Start usbmuxd for iOS device communication."""
    log.info("[usb] Stopping existing usbmuxd...")
    kill_process("usbmuxd")
    time.sleep(0.5)
    
    log.info("[usb] Starting usbmuxd...")
    subprocess.Popen(
        ["sudo", "/usr/sbin/usbmuxd", "-f", "-p", "-v"],
        stdout=open("/home/orangepi/autorain-usbmuxd.txt", "w"),
        stderr=subprocess.STDOUT,
        start_new_session=True
    )
    
    # Wait for socket
    for _ in range(20):
        if os.path.exists("/var/run/usbmuxd"):
            log.info("[usb] usbmuxd ready")
            return True
        time.sleep(0.1)
    
    log.warning("[usb] usbmuxd socket not found")
    return False


# ================= PALERA1N =================

def run_palera1n():
    """Run palera1n with pexpect, handling all stages."""
    log.info("[palera1n] Starting palera1n...")
    led_call("boot_ready")
    
    retry_count = 0
    
    while retry_count <= MAX_RETRIES:
        child = pexpect.spawn(PALERA1N_CMD, encoding="utf-8", timeout=None)
        child.logfile = sys.stdout
        
        while True:
            try:
                idx = child.expect([
                    r"Waiting for devices",           # 0
                    r"Entering recovery mode",        # 1
                    r"Press Enter when ready for DFU",# 2
                    r"Booting Kernel",                # 3
                    r"Found PongoOS USB Device",      # 4
                    r"Timed out waiting for download mode",  # 5
                    r"Entering normal mode",          # 6
                    pexpect.EOF,                      # 7
                ], timeout=300)
                
                if idx == 0:
                    log.info("[palera1n] Waiting for device...")
                    led_call("palera1n_waiting")
                    play_audio(READY_MP3, wait_time=2.5)
                
                elif idx == 1:
                    log.info("[palera1n] Recovery mode - device detected!")
                    led_call("palera1n_device_detected")  # Speed up chase!
                    child.sendline("\r")
                
                elif idx == 2:
                    log.info("[palera1n] DFU mode instructions")
                    led_call("palera1n_dfu_step1")
                    play_audio(STEP1_MP3, wait_time=5)
                    child.sendline("")
                    led_call("palera1n_dfu_step2")
                    play_audio(STEP2_MP3, wait_time=10)
                
                elif idx in (3, 4):
                    log.info("[palera1n] Kernel booting - SUCCESS!")
                    led_call("palera1n_booting")
                    play_audio(FINISH_MP3)
                    led_call("palera1n_complete")
                    return True
                
                elif idx == 5:
                    log.warning("[palera1n] DFU timeout - retrying")
                    led_call("palera1n_error")
                    play_audio(RETRY_MP3)
                    retry_count += 1
                    child.close(force=True)
                    break
                
                elif idx == 6:
                    log.info("[palera1n] Normal mode - will reboot to recovery")
                    led_call("palera1n_device_detected")
                    continue
                
                elif idx == 7:
                    log.error("[palera1n] Unexpected exit")
                    led_call("palera1n_error")
                    retry_count += 1
                    break
                    
            except pexpect.TIMEOUT:
                log.error("[palera1n] Timeout waiting for device")
                retry_count += 1
                child.close(force=True)
                break
    
    log.critical("[palera1n] Max retries exceeded")
    play_audio(SHUTDOWN_MP3)
    return False


# ================= CLEANUP =================

def cleanup():
    """Cleanup on exit."""
    log.info("[system] Cleanup...")
    
    # Remove PID file
    try:
        pidfile = "/tmp/autorain.pid"
        if os.path.exists(pidfile):
            os.remove(pidfile)
    except:
        pass
    
    # Stop LEDs
    led_call("cleanup")
    
    # Kill processes
    kill_process("palera1n")
    kill_process("usbmuxd")


def check_already_running():
    """Prevent multiple instances."""
    pidfile = "/tmp/autorain.pid"
    
    if os.path.exists(pidfile):
        try:
            with open(pidfile) as f:
                pid = int(f.read().strip())
            # Check if process exists
            os.kill(pid, 0)
            log.critical(f"[system] Already running (PID {pid})")
            sys.exit(1)
        except (ProcessLookupError, ValueError):
            os.remove(pidfile)
    
    # Write our PID
    with open(pidfile, 'w') as f:
        f.write(str(os.getpid()))


# ================= MAIN =================

def main():
    log.info("=" * 50)
    log.info("autoRain starting")
    log.info("=" * 50)
    
    atexit.register(cleanup)
    check_already_running()
    
    # Start LED controller and show boot animation
    if LED_AVAILABLE and led is not None:
        led.start_pwm()
        time.sleep(0.2)
        led.boot_starting()
    
    # Wait for Bluetooth speaker (BLOCKING)
    if not wait_for_bluetooth():
        log.critical("[system] Cannot proceed without Bluetooth audio")
        log.info("[system] Will keep retrying...")
        while not wait_for_bluetooth():
            time.sleep(5)
    
    # Set up audio
    set_volume("2%")
    
    # Start usbmuxd
    start_usbmuxd()
    
    # Run palera1n
    success = run_palera1n()
    
    if success:
        log.info("[system] Jailbreak complete!")
    else:
        log.error("[system] Jailbreak failed")
    
    cleanup()


if __name__ == "__main__":
    main()
