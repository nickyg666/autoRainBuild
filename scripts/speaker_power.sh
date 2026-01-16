#!/bin/bash
# speaker-power.sh - Toggle speaker power button
# Hold low for 3 seconds to toggle power, then release high

BIN="/usr/bin/gpioset"
GPIOCHIP="gpiochip1"
LINE="79"

log() {
    echo "$(date '+%F %T') [speaker-power] $*" >> /home/orangepi/speaker-power.log
}

# Simple power toggle: press and hold for 3 seconds
log "Pressing power button (hold for 3s)..."
$BIN "$GPIOCHIP" "$LINE=0"
sleep 3
$BIN "$GPIOCHIP" "$LINE=1"
log "Power toggle complete"
