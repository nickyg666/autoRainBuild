#!/bin/bash
# autoRain.py - Main system workflow handler

AUDIO_DIR="/home/orangepi/autoRain/audio/sounds"
READY_SOUND="$AUDIO_DIR/ready.mp3"
BLUETOOTH_CHECK="/usr/local/bin/check_bluetooth.sh"
AUTOLOGIN_SCRIPT="/home/orangepi/.auto_login"

echo "autoRain: Waiting for device connection..."

speaker_test() {
    if pactl list sinks short 2>/dev/null | grep -q "bluez"; then
        return 0
    fi
    if aplay -l 2>/dev/null | grep -q "USB Audio"; then
        return 0
    fi
    return 1
}

play_beep() {
    echo -e "\a"
    if command -v aplay 2>/dev/null; then
        (speaker-test -t sine -f 1000 -l 100 2>/dev/null || true) &
    fi
}

while true; do
    if $BLUETOOTH_CHECK 2>/dev/null; then
        echo "Device connected via Bluetooth!"
        if speaker_test; then
            echo "Audio device ready!"
            play_beep
            if [ -x "$AUTOLOGIN_SCRIPT" ]; then
                exec "$AUTOLOGIN_SCRIPT"
            fi
        else
            echo "Device connected but no audio available"
        fi
    fi
    sleep 2
done
