#!/bin/bash
# check_bluetooth.sh - Check if bluetooth device is connected
# Returns 0 if connected, 1 if not

# Check for any connected bluetooth devices
if bluetoothctl info 2>/dev/null | grep -q "Connected: yes"; then
    exit 0
fi

# Check for paired devices that might be connected
if bluetoothctl devices Connected 2>/dev/null | grep -q .; then
    exit 0
fi

exit 1  # No bluetooth device found
