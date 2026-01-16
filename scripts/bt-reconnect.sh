#!/bin/bash
# Bluetooth Reconnect Handler
# Triggered on power events to reconnect Bluetooth devices

BT_DEVICE="11:81:AA:11:88:72"
LOG_FILE="/home/orangepi/autoRain.log"

log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [bt-reconnect] $*" >> "$LOG_FILE"
}

log_msg "Bluetooth reconnect triggered"

# Wait for Bluetooth to initialize
sleep 2

# Check if device is already connected
if bluetoothctl info "$BT_DEVICE" 2>/dev/null | grep -q "Connected: yes"; then
    log_msg "Device already connected, no action needed"
    exit 0
fi

# Check if device is known/paired
if ! bluetoothctl devices 2>/dev/null | grep -q "$BT_DEVICE"; then
    log_msg "Device not paired, skipping connection attempt"
    exit 1
fi

# Attempt to connect
log_msg "Attempting to reconnect to $BT_DEVICE"
bluetoothctl connect "$BT_DEVICE" 2>&1 | head -5 >> "$LOG_FILE"

# Wait a bit and verify
sleep 5

if bluetoothctl info "$BT_DEVICE" 2>/dev/null | grep -q "Connected: yes"; then
    log_msg "Reconnection successful"
    exit 0
else
    log_msg "Reconnection failed"
    exit 1
fi
