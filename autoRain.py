#!/usr/bin/env python3

import subprocess
import time
import pexpect
import sys
import os
import logging
import atexit
import threading

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

# ================= ENV =================

os.environ["PATH"] = (
    "/usr/sbin:/sbin:/usr/local/sbin:/home/orangepi:" + os.environ.get("PATH", "")
)
os.environ["PULSE_SERVER"] = "unix:/run/user/1000/pulse/native"

# ================= CONFIG =================

BT_DEVICE = "11:81:AA:11:88:72"
BT_RECOVERY_INTERVAL = 6
BT_CHECK_INTERVAL = 2
AUDIO_PATH = "/home/orangepi"
BT_TIMEOUT = 30
SPEAKER_POWER = "/usr/local/bin/speaker-power.sh"
PALERA1N_CMD = "sudo palera1n -l"
USBMUXD_CMD  = "sudo /usr/sbin/usbmuxd -f -p -v"
SHUTDOWN     = "/usr/sbin/poweroff"

READY_MP3    = f"{AUDIO_PATH}/ready.mp3"
STEP1_MP3    = f"{AUDIO_PATH}/step1.mp3"
STEP2_MP3    = f"{AUDIO_PATH}/step2.mp3"
FINISH_MP3   = f"{AUDIO_PATH}/complete.mp3"
RETRY_MP3    = f"{AUDIO_PATH}/retry.mp3"
SHUTDOWN_MP3 = f"{AUDIO_PATH}/shutdown.mp3"

DFU_WAIT_TIME = 4.5
COOLDOWN_TIME = 60
MAX_RETRIES   = 3
RETRY_AUDIO_DELAY = 2

def safe_kill_process(name):
    """Kill all processes by name using pgrep and kill PID."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", name],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        if result.stdout:
            for pid in result.stdout.strip().split('\n'):
                if pid:
                    try:
                        subprocess.run(["sudo", "kill", "-9", pid], 
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
                    except:
                        pass
    except:
        pass

# ================= CLEANUP =================

def power_off_speaker():
    log.info("[bt] Powering speaker OFF (cleanup)")
    try:
        subprocess.run(
            ["sudo", SPEAKER_POWER],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        log.error(f"[bt] Failed to power off speaker: {e}")

def hard_exit(reason):
    log.critical(f"[system] HARD EXIT: {reason}")

    try:
        safe_kill_process("palera1n")
        safe_kill_process("usbmuxd")
    except Exception:
        pass

    try:
        power_off_speaker()
    except Exception:
        pass
    
    # Clean up PID file
    try:
        pidfile = "/tmp/autorain.pid"
        if os.path.exists(pidfile):
            os.remove(pidfile)
    except Exception:
        pass

    log.critical("[system] Exiting now")
    os._exit(0)

# ================= AUDIO =================

def wait_for_audio_sink(timeout=4):
    log.info("[audio] Waiting for PulseAudio + Bluetooth sink")
    start = time.time()

    while time.time() - start < timeout:
        try:
            env = os.environ.copy()
            env["PULSE_SERVER"] = "unix:/run/user/1000/pulse/native"
            out = subprocess.check_output(
                ["pactl", "list", "short", "sinks"],
                stderr=subprocess.DEVNULL,
                text=True,
                env=env,
            )
            if "bluez_sink" in out:
                log.info("[audio] Bluetooth sink detected")
                return True
        except Exception:
            pass
        time.sleep(0.2)

    log.warning("[audio] Timed out waiting for BT sink (continuing anyway)")
    return False

def set_volume():
    try:
        env = os.environ.copy()
        env["PULSE_SERVER"] = "unix:/run/user/1000/pulse/native"
        # Set volume specifically for Bluetooth sink if available, otherwise all sinks
        sinks = subprocess.check_output(["pactl", "list", "short", "sinks"], text=True, env=env)
        bt_sink = None
        for line in sinks.strip().split('\n'):
            if 'bluez' in line:
                bt_sink = line.split('\t')[0]
                break
        
        if bt_sink:
            subprocess.run(["pactl", "set-sink-volume", bt_sink, "2%"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
            log.info(f"[audio] Set Bluetooth sink {bt_sink} to 2%")
        else:
            subprocess.run(
                ["bash", "-c", "pactl list short sinks | awk '{print $1}' | xargs -I{} pactl set-sink-volume {} 2%"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
            )
            log.info("[audio] Set all sinks to 2%")
    except Exception:
        pass

def play(mp3, wait_time=None):
    """Play audio file. If wait_time is specified, block until playback completes OR wait_time expires."""
    log.info(f"[audio] Playing {os.path.basename(mp3)}")
    try:
        env = os.environ.copy()
        env["PULSE_SERVER"] = "unix:/run/user/1000/pulse/native"
        if wait_time is not None:
            # Blocking mode: play file to completion, ensuring at least wait_time total
            start = time.time()
            result = subprocess.run(
                ["mpg123", "-q", mp3],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=wait_time + 10,  # safety margin for long files
                env=env
            )
            elapsed = time.time() - start
            remaining = wait_time - elapsed
            if remaining > 0:
                time.sleep(remaining)
            log.info(f"[audio] {os.path.basename(mp3)} playback complete (total: {elapsed:.1f}s)")
        else:
            # Non-blocking mode: start playback and return immediately
            # File plays to completion in background
            subprocess.Popen(
                ["mpg123", "-q", mp3],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env
            )
    except subprocess.TimeoutExpired:
        log.warning(f"[audio] Playback timeout for {os.path.basename(mp3)}")
    except Exception as e:
        log.warning(f"[audio] Failed to play {os.path.basename(mp3)}: {e}")

# ================= BLUETOOTH =================

def bt_connected():
    try:
        out = subprocess.check_output(
            ["bluetoothctl", "info", BT_DEVICE],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return "Connected: yes" in out
    except subprocess.CalledProcessError:
        return False

def bt_device_known():
    """Check if device is in bluetoothctl devices list (paired/known)"""
    try:
        out = subprocess.check_output(
            ["bluetoothctl", "devices"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return BT_DEVICE in out
    except subprocess.CalledProcessError:
        return False

def power_cycle_speaker():
    log.info("[bt] Initiating speaker power cycle")
    try:
        result = subprocess.run(
            ["sudo", SPEAKER_POWER],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            log.error(f"[bt] Speaker power script failed (code {result.returncode}): {result.stderr}")
            return False
        log.info("[bt] Speaker power cycle completed successfully")
        return True
    except Exception as e:
        log.error(f"[bt] Failed to power cycle speaker: {e}")
        return False
        
def wait_for_bt_background():
     """Background thread function for Bluetooth connection with timeout."""
     BT_GRACE_PERIOD = 0.2
     log.info("let bluez settle")
     time.sleep(BT_GRACE_PERIOD)
     log.info("[bt] Waiting for Bluetooth speaker connection (background)")

     start_time = time.time()
     cycled = False
     max_total_wait = 30  # Allow 30 seconds for background connection attempts
     speaker_boot_time = 3
     retry_interval = 0.5

     while True:
         # Success path - device connected
         if bt_connected():
             log.info("[bt] Speaker connected successfully")
             set_volume()
             play(READY_MP3, wait_time=2.0)
             return

         now = time.time()
         elapsed = now - start_time
         
         # Timeout after max_total_wait - log but don't exit
         if elapsed >= max_total_wait:
             log.warning(f"[bt] Background: Could not connect to speaker after {max_total_wait}s")
             log.warning("[bt] Continuing without speaker - boot sequence can proceed")
             return

         # Check if device is known/paired - if not, power cycle
         if not cycled:
             if bt_device_known():
                 log.info("[bt] Device is known, waiting for auto-connect...")
                 cycled = True
                 continue
             else:
                 log.info("[bt] Device not in bluetoothctl devices, power cycling speaker")
                 if power_cycle_speaker():
                     cycled = True
                     log.info(f"[bt] Waiting {speaker_boot_time}s for speaker to boot")
                     time.sleep(speaker_boot_time)
                     continue
                 else:
                     log.error("[bt] Power cycle failed - waiting for auto-connect anyway")
                     cycled = True
                     continue

         # Regular check interval
         time.sleep(retry_interval)

def wait_for_bt():
     """Start Bluetooth connection in background thread and return immediately."""
     log.info("[bt] Starting Bluetooth connection in background")
     bt_thread = threading.Thread(target=wait_for_bt_background, daemon=True)
     bt_thread.start()
     # Don't wait for it - let it run in background
     log.info("[bt] Continuing with boot sequence while Bluetooth connects in background")
     return True

# ================= USBMUXD =================

def kill_usbmuxd():
    log.info("[usb] Killing any existing usbmuxd")
    safe_kill_process("usbmuxd")
    
def start_usbmuxd():
    log.info("[usb] Starting usbmuxd (foreground)")
    subprocess.Popen(
        ["sudo", "/usr/sbin/usbmuxd", "-f", "-p", "-v"],
        stdout=open("/home/orangepi/autorain-usbmuxd.txt", "w"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    # wait until socket exists (reduced timeout)
    timeout = 2
    while timeout > 0 and not os.path.exists("/var/run/usbmuxd"):
        time.sleep(0.1)
        timeout -= 0.1
    log.info("[usb] usbmuxd ready")

# ================= PALERA1N =================

def run_palera1n():
    log.info("[palera1n] Launching palera1n")
    child = pexpect.spawn(PALERA1N_CMD, encoding="utf-8", timeout=None)
    child.logfile = sys.stdout
    return child

# ================= MAIN =================

def check_already_running():
    """Check if autoRain is already running and exit if so."""
    pidfile = "/tmp/autorain.pid"
    
    # Check PID file
    if os.path.exists(pidfile):
        try:
            with open(pidfile, 'r') as f:
                pid = int(f.read().strip())
            # Check if process with this PID exists and is autoRain
            try:
                with open(f'/proc/{pid}/cmdline', 'r') as f:
                    cmdline = f.read()
                if 'autoRain.py' in cmdline:
                    log.critical(f"[system] autoRain already running (PID: {pid}) - exiting")
                    os._exit(1)
            except (FileNotFoundError, ProcessLookupError, ValueError):
                # Process doesn't exist, remove stale PID file
                os.remove(pidfile)
        except (ValueError, IOError):
            pass
    
    # Write our PID to file
    with open(pidfile, 'w') as f:
        f.write(str(os.getpid()))

def cleanup_pidfile():
    """Clean up PID file on exit."""
    try:
        pidfile = "/tmp/autorain.pid"
        if os.path.exists(pidfile):
            os.remove(pidfile)
            log.info("[system] PID file cleaned up")
    except Exception:
        pass

def main():
    log.info("===== autorain boot sequence start =====")
    
    # Register cleanup function
    atexit.register(cleanup_pidfile)
    
    # Check if already running
    check_already_running()

    wait_for_bt()
    
    # Parallelize audio sink check and usbmuxd startup
    audio_thread = threading.Thread(target=wait_for_audio_sink, daemon=True)
    audio_thread.start()
    
    kill_usbmuxd()
    muxd = start_usbmuxd()
    
    # Wait for audio thread to complete with shorter timeout
    audio_thread.join(timeout=3)
    
    # Set volume BEFORE playing any audio
    set_volume()

    retry_count = 0

    while retry_count <= MAX_RETRIES:
        child = run_palera1n()

        while True:
            idx = child.expect([
                r"Waiting for devices",
                r"Entering recovery mode",
                r"Press Enter when ready for DFU",
                r"Booting Kernel",
                r"Found PongoOS USB Device",
                r"Timed out waiting for download mode",
                r"Entering normal mode",
                pexpect.EOF,
            ])

            if idx == 0:
                log.info("[palera1n] Waiting for device")
                play(READY_MP3, wait_time=2.5)
            elif idx == 1:
                log.info("[palera1n] Recovery mode detected - advancing")
                child.sendline("\r")
            elif idx == 2:
                log.info("[palera1n] DFU step")
                play(STEP1_MP3, wait_time=5)  # 5 sec total: hold home+power, then release power
                child.sendline("")  # simulate releasing power button after 5 seconds
                play(STEP2_MP3, wait_time=10)  # 10 sec total: hold home button for countdown

            elif idx in (3, 4):
                log.info("[palera1n] Kernel boot detected")
                play(FINISH_MP3)
                hard_exit("jailbreak complete")

            elif idx == 5:
                log.warning("[palera1n] Download mode timeout — retrying")
                play(RETRY_MP3)
                retry_count += 1
                child.close(force=True)
                break

            elif idx == 6:
                log.info("[palera1n] Device in normal mode - will reboot to recovery")
                continue

            elif idx == 7:
                log.error("[palera1n] palera1n exited unexpectedly")
                retry_count += 1
                break

        if retry_count > MAX_RETRIES:
            log.critical("[system] Max retries reached — shutting down")
            play(SHUTDOWN_MP3)
            hard_exit("max retries")

if __name__ == "__main__":
    main()
