#!/bin/bash
# Bluetooth Speaker Connection Script with Power Cycle Support
# Sets up environment exactly like manual TTY execution
# Waits 15s after power event before reconnecting

set -o allexport
export HOME=/home/orangepi
export USER=orangepi
export LOGNAME=orangepi
export SHELL=/bin/bash
export XDG_RUNTIME_DIR=/run/user/1000
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export PULSE_SERVER=unix:/run/user/1000/pulse/native
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/orangepi
set +o allexport

LOG_FILE="/home/orangepi/autoRain.log"
POWER_EVENT_FILE="/tmp/speaker-power-event"
BT_DEVICE="11:81:AA:11:88:72"
BT_DEVICE_NAME="Wireless Speaker"
MAX_RETRIES=5
RETRY_DELAY=3
POWER_WAIT=15

log_msg() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [bluetooth-boot] $*" | tee -a "$LOG_FILE"
}

check_power_event() {
    # Check if we recently triggered a power event
    if [ -f "$POWER_EVENT_FILE" ]; then
        local last=$(cat "$POWER_EVENT_FILE")
        local now=$(date +%s)
        local elapsed=$((now - last))
        
        if [ $elapsed -lt $POWER_WAIT ]; then
            log_msg "Power cycle in progress ($elapsed/${POWER_WAIT}s), waiting..."
            sleep $((POWER_WAIT - elapsed))
            return 0
        fi
    fi
    return 0
}

log_msg "Attempting to connect Bluetooth speaker..."

# Wait for Bluetooth service to be ready
sleep 2

# Ensure Bluetooth adapter is powered on
log_msg "Ensuring Bluetooth adapter is powered on..."
bluetoothctl power on 2>/dev/null
sleep 1

# Enable discovery mode for pairing
log_msg "Enabling discoverable mode..."
bluetoothctl discoverable on 2>/dev/null
sleep 1

# Check if we need to wait after a power event
check_power_event

# First, check if device needs pairing
log_msg "Checking if device is paired..."
if ! bluetoothctl info "$BT_DEVICE" 2>/dev/null | grep -q "Paired: yes"; then
    log_msg "Device not paired, attempting to pair..."
    bluetoothctl pair "$BT_DEVICE" 2>&1 | tee -a "$LOG_FILE"
    sleep 2
fi

# Try to connect to the device
for i in $(seq 1 $MAX_RETRIES); do
    if bluetoothctl connect "$BT_DEVICE" 2>&1 | grep -q "Connection successful"; then
        log_msg "✓ Connected to $BT_DEVICE"
        exit 0
    fi
    
    if bluetoothctl info "$BT_DEVICE" 2>/dev/null | grep -q "Connected: yes"; then
        log_msg "✓ Device already connected"
        exit 0
    fi
    
    log_msg "Connection attempt $i/$MAX_RETRIES failed, retrying..."
    sleep "$RETRY_DELAY"
done

log_msg "⚠ Could not connect to $BT_DEVICE after $MAX_RETRIES attempts"
log_msg "Make sure speaker is powered on and in range"
exit 1
