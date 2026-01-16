#!/bin/bash
# shutdown-speaker-power.sh - Toggle speaker power on reboot/poweroff
# GPIO 79: momentary button (1=released, 0=pressed)
# Marks power event timestamp to prevent Bluetooth reconnect spam

LOG_FILE="/home/orangepi/autoRain.log"
POWER_EVENT_FILE="/tmp/speaker-power-event"

log_msg() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [shutdown-speaker] $*" | tee -a "$LOG_FILE"
}

log_msg "=== Shutdown: Speaker Power Toggle ==="

# Press button (GPIO 79 = 0) for 3 seconds
log_msg "Pressing speaker power button (GPIO 79) for 3 seconds..."
gpioset gpiochip1 79=0 2>/dev/null || {
    log_msg "Warning: Failed to press button, trying with sudo..."
    sudo gpioset gpiochip1 79=0
}
sleep 3

# Release button (GPIO 79 = 1) to complete the toggle
log_msg "Releasing speaker power button (GPIO 79)"
gpioset gpiochip1 79=1 2>/dev/null || {
    log_msg "Warning: Failed to release button, trying with sudo..."
    sudo gpioset gpiochip1 79=1
}

# Mark power event timestamp to prevent Bluetooth reconnect spam
date +%s > "$POWER_EVENT_FILE"
log_msg "Power event marked at $(date '+%Y-%m-%d %H:%M:%S')"

log_msg "Shutdown speaker power toggle complete"
exit 0
