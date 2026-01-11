#!/bin/bash
# speaker-manager.sh - Audio and Bluetooth speaker management
# Handles speaker power cycle, connection, and audio routing
# Prioritizes headphone jack if detected, otherwise uses Bluetooth speaker

SPEAKER_MAC="11:81:AA:11:88:72"
SPEAKER_POWER="/usr/local/bin/speaker-power.sh"
LOG_FILE="/home/orangepi/speaker-manager.log"

log() {
    echo "$(date '+%F %T') [speaker-manager] $*" | tee -a "$LOG_FILE"
}

# Check if headphone jack is plugged in
check_headphone() {
    # Check via sysfs for jack detection (most reliable)
    if [ -d "/sys/class/sound/card0" ]; then
        for jack in /sys/class/sound/card0/*jack*; do
            if [ -d "$jack" ]; then
                JACK_STATUS=$(cat "$jack/status" 2>/dev/null)
                if [ "$JACK_STATUS" = "plug" ]; then
                    log "Headphone jack detected via sysfs: $jack"
                    return 0
                fi
            fi
        done
    fi
    
    # If no sysfs detection, return false
    # (we'll default to Bluetooth speaker in this case)
    return 1
}

# Set default audio sink
set_audio_sink() {
    local sink_name="$1"
    export PULSE_SERVER="unix:/run/user/1000/pulse/native"
    
    log "Setting default audio sink to: $sink_name"
    
    # Get sink index
    SINK_INDEX=$(pactl list short sinks 2>/dev/null | grep "$sink_name" | head -1 | awk '{print $1}')
    
    if [ -n "$SINK_INDEX" ]; then
        pactl set-default-sink "$SINK_INDEX"
        log "Default sink set to index $SINK_INDEX"
        # Set volume to 2%
        pactl set-sink-volume "$SINK_INDEX" "2%"
        log "Volume set to 2%"
        return 0
    else
        log "WARNING: Could not find sink: $sink_name"
        return 1
    fi
}

# Auto-select best audio output
auto_select_audio_output() {
    log "Checking for available audio outputs..."
    
    # First check for headphone jack
    if check_headphone; then
        log "Headphone detected - routing audio to headphones"
        set_audio_sink "alsa_output" || set_audio_sink "analog"
        return 0
    fi
    
    # Check for Bluetooth speaker
    export PULSE_SERVER="unix:/run/user/1000/pulse/native"
    if pactl list short sinks 2>/dev/null | grep -q "bluez"; then
        log "Bluetooth speaker available - routing audio to speaker"
        set_audio_sink "bluez"
        return 0
    fi
    
    # Fallback to default sink
    log "Using default audio sink"
    pactl set-sink-volume @DEFAULT_SINK@ "2%"
    return 0
}

# Check if speaker is connected
is_speaker_connected() {
    if bluetoothctl info "$SPEAKER_MAC" 2>/dev/null | grep -q "Connected: yes"; then
        return 0
    fi
    return 1
}

# Power cycle the speaker
power_cycle_speaker() {
    log "Power cycling speaker via GPIO"
    
    if [ -x "$SPEAKER_POWER" ]; then
        # Toggle power off
        sudo "$SPEAKER_POWER" 2>&1 | tee -a "$LOG_FILE"
        sleep 1
        
        # Toggle power on
        sudo "$SPEAKER_POWER" 2>&1 | tee -a "$LOG_FILE"
        log "Waiting 5 seconds for speaker to power up and become discoverable"
        sleep 5
    else
        log "ERROR: speaker-power.sh not found at $SPEAKER_POWER"
        return 1
    fi
    
    return 0
}

# Connect to speaker
connect_speaker() {
    log "Attempting to connect to speaker $SPEAKER_MAC"
    
    # Ensure Bluetooth is powered on
    if ! bluetoothctl show | grep -q "Powered: yes"; then
        log "Powering on Bluetooth adapter"
        bluetoothctl power on
        sleep 2
    fi
    
    # Check if device is paired
    if ! bluetoothctl devices | grep -q "$SPEAKER_MAC"; then
        log "Device not paired - scanning and pairing"
        bluetoothctl scan on
        sleep 5
        
        if bluetoothctl pair "$SPEAKER_MAC" 2>/dev/null; then
            log "Successfully paired"
            bluetoothctl trust "$SPEAKER_MAC"
        else
            log "ERROR: Could not pair with device"
            return 1
        fi
    fi
    
    # Attempt connection
    if bluetoothctl connect "$SPEAKER_MAC" 2>&1 | tee -a "$LOG_FILE"; then
        sleep 3
        
        if is_speaker_connected; then
            log "SUCCESS: Speaker connected"
            return 0
        else
            log "FAILED: Speaker did not connect"
            return 1
        fi
    else
        log "FAILED: bluetoothctl connect command failed"
        return 1
    fi
}

# Play test beep
play_test_beep() {
    log "Playing test beep to verify audio"
    
    # Generate and play a beep using paplay
    export PULSE_SERVER="unix:/run/user/1000/pulse/native"
    
    # Generate a 1kHz sine wave beep for 0.2 seconds
    if command -v paplay &> /dev/null; then
        if command -v sox &> /dev/null; then
            sox -n -t wav -p synth 0.2 sine 1000 gain -6 2>/dev/null | paplay 2>/dev/null
            log "Test beep played (via sox + paplay)"
        elif command -v beep &> /dev/null; then
            beep -f 1000 -l 200 2>/dev/null
            log "Test beep played (via beep command)"
        else
            log "WARNING: No audio test tool available"
        fi
    else
        log "WARNING: paplay not available"
    fi
}

# Main speaker setup routine
setup_speaker() {
    log "=== Starting speaker setup ==="
    
    # Check for headphone jack first
    if check_headphone; then
        log "Headphone jack detected - skipping speaker connection"
        auto_select_audio_output
        sleep 2
        play_test_beep
        log "=== Speaker setup complete (using headphones) ==="
        return 0
    fi
    
    # Check if speaker is already connected
    if is_speaker_connected; then
        log "Speaker already connected"
        auto_select_audio_output
        sleep 2
        play_test_beep
        log "=== Speaker setup complete (already connected) ==="
        return 0
    fi
    
    # Power cycle speaker
    power_cycle_speaker
    
    # Wait for speaker to be ready
    log "Waiting 2 seconds before connection attempt"
    sleep 2
    
    # Try to connect
    if connect_speaker; then
        # Connection succeeded, wait for audio sink
        log "Waiting for audio sink to appear..."
        WAIT_COUNT=0
        MAX_WAIT=10
        
        while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
            if pactl list short sinks 2>/dev/null | grep -q "bluez"; then
                log "Audio sink detected"
                break
            fi
            sleep 1
            WAIT_COUNT=$((WAIT_COUNT + 1))
        done
        
        # Set audio output
        auto_select_audio_output
        
        # Wait a bit for audio system to stabilize
        sleep 2
        
        # Play test beep
        play_test_beep
        
        log "=== Speaker setup complete ==="
        return 0
    else
        log "WARNING: Could not connect to speaker"
        log "Will let autoRain.py handle reconnection"
        return 0  # Don't fail, allow system to continue
    fi
}

# Continuous speaker monitoring (for long-running processes)
monitor_speaker() {
    log "Starting continuous speaker monitoring"
    
    while true; do
        if ! check_headphone && ! is_speaker_connected; then
            log "Speaker disconnected - attempting reconnection"
            if [ -x "$SPEAKER_POWER" ]; then
                power_cycle_speaker
                sleep 2
                connect_speaker
                auto_select_audio_output
            fi
        fi
        
        # Re-check audio routing in case headphones were plugged/unplugged
        auto_select_audio_output
        
        # Check every 10 seconds
        sleep 10
    done
}

# Show current status
show_status() {
    echo "=== Speaker Manager Status ==="
    echo ""
    echo "Headphone jack: $(check_headphone && echo "DETECTED" || echo "Not detected")"
    echo "Speaker connected: $(is_speaker_connected && echo "YES" || echo "NO")"
    echo ""
    echo "Bluetooth service:"
    bluetoothctl show | grep -E "Powered|Discoverable|Pairable"
    echo ""
    echo "Audio sinks:"
    export PULSE_SERVER="unix:/run/user/1000/pulse/native"
    pactl list short sinks 2>/dev/null || echo "  (pulseaudio not available)"
    echo ""
    echo "Default sink:"
    pactl get-default-sink 2>/dev/null || echo "  (pulseaudio not available)"
}

case "$1" in
    setup)
        setup_speaker
        ;;
    connect)
        connect_speaker
        auto_select_audio_output
        ;;
    check-headphone)
        check_headphone && echo "YES" || echo "NO"
        ;;
    is-connected)
        is_speaker_connected && echo "YES" || echo "NO"
        ;;
    power-cycle)
        power_cycle_speaker
        ;;
    test-beep)
        play_test_beep
        ;;
    select-audio)
        auto_select_audio_output
        ;;
    monitor)
        monitor_speaker
        ;;
    status)
        show_status
        ;;
    *)
        echo "Speaker Manager - Audio and Bluetooth speaker management"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  setup        - Full speaker setup (check, power cycle, connect, test)"
        echo "  connect      - Connect to Bluetooth speaker"
        echo "  check-headphone - Check if headphone jack is plugged in"
        echo "  is-connected  - Check if Bluetooth speaker is connected"
        echo "  power-cycle  - Power cycle the speaker via GPIO"
        echo "  test-beep    - Play a test beep"
        echo "  select-audio  - Auto-select best audio output"
        echo "  monitor      - Continuous monitoring mode"
        echo "  status       - Show current status"
        echo ""
        exit 1
        ;;
esac
