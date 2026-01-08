#!/bin/bash
# Toggle speaker power
# Used when no bluetooth device is detected

SPEAKER_POWER_PIN=""  # GPIO pin for speaker power (configure for your hardware)

if [ -z "$SPEAKER_POWER_PIN" ]; then
    echo "Speaker power management requires GPIO pin configuration"
    echo "Edit $0 and set SPEAKER_POWER_PIN"
    exit 1
fi

# Export GPIO pin
echo "$SPEAKER_POWER_PIN" > /sys/class/gpio/export 2>/dev/null

# Set direction to output
echo "out" > /sys/class/gpio/gpio$SPEAKER_POWER_PIN/direction

# Toggle power
CURRENT_STATE=$(cat /sys/class/gpio/gpio$SPEAKER_POWER_PIN/value 2>/dev/null || echo "0")

if [ "$CURRENT_STATE" = "1" ]; then
    echo "Turning speakers OFF"
    echo "0" > /sys/class/gpio/gpio$SPEAKER_POWER_PIN/value
else
    echo "Turning speakers ON"
    echo "1" > /sys/class/gpio/gpio$SPEAKER_POWER_PIN/value
fi

exit 0
