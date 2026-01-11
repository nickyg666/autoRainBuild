#!/bin/bash
# jailbreakbox-manager.sh - Unified System Manager
# Combines AP manager, WiFi manager, and LED controller into one service
# Version 1.0

# =============================================
# CONFIGURATION
# =============================================

WIFI_INTERFACE="wlan0"
ETHERNET_INTERFACE="end0"
AP_SSID="jailbreakBox"
AP_IP="10.42.0.1"
STARTUP_DELAY=30
KNOWN_WIFI_SSID="lasagna|IoT|Service|gamestream"

# LED GPIO pins
LED1_R=230 LED1_G=71 LED1_B=74
LED2_R=233 LED2_G=72 LED2_B=75
LED3_R=69  LED3_G=72 LED3_B=233

# State and logging
STATE_DIR="/var/run/jailbreakbox-manager"
STATE_FILE="$STATE_DIR/mode"
LOG_FILE="/var/log/jailbreakbox-manager.log"
PID_DIR="/var/run/jailbreakbox-manager"

# =============================================
# UTILITY FUNCTIONS
# =============================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [jb-manager] $*" | tee -a "$LOG_FILE"
}

init_dirs() {
    mkdir -p "$STATE_DIR" "$PID_DIR"
    touch "$STATE_FILE"
}

# =============================================
# NETWORK DETECTION
# =============================================

is_wifi_connected() {
    nmcli -t -f GENERAL.CONNECTION,GENERAL.STATE device show "$WIFI_INTERFACE" 2>/dev/null | grep -q "connected"
}

is_hostapd_running() {
    systemctl is-active --quiet hostapd
}

is_ethernet_connected() {
    nmcli -t -f STATE,DEVICE device show "$ETHERNET_INTERFACE" 2>/dev/null | grep -q "connected"
}

is_known_wifi_connected() {
    local current_wifi
    current_wifi=$(nmcli -t -f ACTIVE,SSID dev wifi | grep '^yes:' | cut -d: -f2)
    
    for known_ssid in ${KNOWN_WIFI_SSID//|/ }; do
        if [ "$current_wifi" = "$known_ssid" ]; then
            return 0
        fi
    done
    return 1
}

# =============================================
# AP MANAGEMENT
# =============================================

start_ap() {
    log "Starting AP: $AP_SSID"
    
    nmcli device disconnect "$WIFI_INTERFACE" 2>/dev/null
    sleep 1
    
    systemctl stop hostapd 2>/dev/null
    sleep 1
    
    ip link set "$WIFI_INTERFACE" up
    
    systemctl start hostapd
    systemctl start dnsmasq
    
    sleep 3
    
    local ap_active
    ap_active=$(iw dev "$WIFI_INTERFACE" info | grep -q "type AP" && echo "yes" || echo "no")
    
    if [ "$ap_active" = "yes" ]; then
        log "AP started successfully on $WIFI_INTERFACE"
        return 0
    else
        log "Failed to start AP"
        return 1
    fi
}

stop_ap() {
    log "Stopping AP"
    
    nmcli device disconnect "$WIFI_INTERFACE" 2>/dev/null
    systemctl stop hostapd 2>/dev/null
    systemctl stop dnsmasq 2>/dev/null
    
    sleep 1
    log "AP stopped"
}

# =============================================
# LED CONTROL
# =============================================

leds_all_off() {
    gpioset gpiochip1 230=0 71=0 72=0 73=0 74=0 75=0 69=0 233=0 2>/dev/null
}

led1_on() { gpioset gpiochip1 230=1 71=1 74=1 2>/dev/null; }
led1_off() { gpioset gpiochip1 230=0 71=0 74=0 2>/dev/null; }

led2_on() { gpioset gpiochip1 233=1 72=1 75=1 2>/dev/null; }
led2_off() { gpioset gpiochip1 233=0 72=0 75=0 2>/dev/null; }

led3_on() { gpioset gpiochip1 69=1 73=1 233=1 2>/dev/null; }
led3_off() { gpioset gpiochip1 69=0 73=0 233=0 2>/dev/null; }

pulse_green() {
    log "Starting green pulse (hotspot mode)"
    
    pkill -f "led_gpio.py" 2>/dev/null || true
    
    local brightness=0
    local direction=1
    
    while true; do
        gpioset gpiochip1 $LED2_G=$((brightness * 5 / 100)) \
                     $LED2_R=0 $LED2_B=0 2>/dev/null
        
        brightness=$((brightness + direction))
        if [ $brightness -gt 100 ]; then
            direction=-1
        fi
        
        sleep 0.05
    done &
    
    echo $! > "$PID_DIR/pulse.pid"
    log "Green pulse started (PID: $!)"
}

stop_pulse_green() {
    log "Stopping green pulse"
    if [ -f "$PID_DIR/pulse.pid" ]; then
        kill $(cat "$PID_DIR/pulse.pid") 2>/dev/null || true
        rm -f "$PID_DIR/pulse.pid"
    fi
    led2_off
}

chase_rainbow() {
    log "Starting rainbow chase (WiFi mode)"
    
    pkill -f "led_gpio.py" 2>/dev/null || true
    
    python3 /home/orangepi/led_gpio.py 30 &
    echo $! > "$PID_DIR/chase.pid"
    log "Rainbow chase started (PID: $!)"
}

stop_chase_rainbow() {
    log "Stopping rainbow chase"
    if [ -f "$PID_DIR/chase.pid" ]; then
        kill $(cat "$PID_DIR/chase.pid") 2>/dev/null || true
        rm -f "$PID_DIR/chase.pid"
    fi
    pkill -f "led_gpio.py" 2>/dev/null || true
}

# =============================================
# WIFI MANAGEMENT
# =============================================

connect_wifi() {
    log "Scanning for known networks..."
    
    stop_ap
    sleep 3
    
    for network in ${KNOWN_WIFI_SSID//|/ }; do
        log "Attempting to connect to $network"
        
        nmcli device set "$WIFI_INTERFACE" managed yes
        sleep 1
        
        if nmcli connection up "$network" 2>/dev/null; then
            log "Connected to $network"
            return 0
        fi
    done
    
    log "No known networks available"
    return 1
}

# =============================================
# NETWORK MONITOR
# =============================================

network_monitor() {
    log "Starting network monitor"
    
    local current_mode="unknown"
    
    while true; do
        if is_wifi_connected; then
            if [ "$current_mode" != "wifi" ]; then
                log "WiFi connected - switching to rainbow chase"
                stop_pulse_green
                chase_rainbow
                echo "wifi" > "$STATE_FILE"
                current_mode="wifi"
            fi
        
        elif is_hostapd_running; then
            if [ "$current_mode" != "hotspot" ]; then
                log "Hotspot running - starting green pulse"
                stop_chase_rainbow
                pulse_green
                echo "hotspot" > "$STATE_FILE"
                current_mode="hotspot"
            fi
        
        else
            if [ "$current_mode" != "off" ]; then
                log "No network - turning off LEDs"
                stop_pulse_green
                stop_chase_rainbow
                leds_all_off
                echo "off" > "$STATE_FILE"
                current_mode="off"
            fi
        
            # Try to connect to WiFi
            if is_known_wifi_connected; then
                connect_wifi
            else
                start_ap
            fi
        fi
        
        sleep 5
    done
}

# =============================================
# MAIN COMMAND INTERFACE
# =============================================

case "$1" in
    start)
        log "=== Starting JailbreakBox Manager ==="
        init_dirs
        
        pkill -f "jailbreakbox-manager.sh" 2>/dev/null || true
        
        stop_pulse_green
        stop_chase_rainbow
        leds_all_off
        
        sleep $STARTUP_DELAY
        
        network_monitor &
        MONITOR_PID=$!
        echo $MONITOR_PID > "$PID_DIR/monitor.pid"
        log "Network monitor started (PID: $MONITOR_PID)"
        ;;
    
    stop)
        log "=== Stopping JailbreakBox Manager ==="
        
        if [ -f "$PID_DIR/monitor.pid" ]; then
            kill $(cat "$PID_DIR/monitor.pid") 2>/dev/null || true
            rm -f "$PID_DIR/monitor.pid"
        fi
        
        stop_pulse_green
        stop_chase_rainbow
        stop_ap
        leds_all_off
        
        rm -f "$STATE_FILE" "$PID_DIR"/*.pid 2>/dev/null || true
        ;;
    
    restart)
        log "=== Restarting JailbreakBox Manager ==="
        "$0" stop
        sleep 2
        "$0" start
        ;;
    
    status)
        echo "=== JailbreakBox Manager Status ==="
        
        if [ -f "$STATE_FILE" ]; then
            MODE=$(cat "$STATE_FILE" 2>/dev/null)
            echo "Current Mode: $MODE"
        else
            echo "Current Mode: Not initialized"
        fi
        
        echo ""
        echo "Network Status:"
        echo "  WiFi: $(is_wifi_connected && echo 'CONNECTED' || echo 'NOT CONNECTED')"
        echo "  Hotspot: $(is_hostapd_running && echo 'RUNNING' || echo 'NOT RUNNING')"
        echo "  Ethernet: $(is_ethernet_connected && echo 'CONNECTED' || echo 'NOT CONNECTED')"
        
        echo ""
        echo "LED Effects:"
        if [ -f "$PID_DIR/pulse.pid" ]; then
            echo "  Green pulse: Running (PID: $(cat $PID_DIR/pulse.pid))"
        else
            echo "  Green pulse: Not running"
        fi
        
        if [ -f "$PID_DIR/chase.pid" ]; then
            echo "  Rainbow chase: Running (PID: $(cat $PID_DIR/chase.pid))"
        else
            echo "  Rainbow chase: Not running"
        fi
        ;;
    
    wifi)
        log "Switching to WiFi mode"
        stop_ap
        if connect_wifi; then
            stop_pulse_green
            chase_rainbow
            echo "wifi" > "$STATE_FILE"
        else
            log "Failed to connect to WiFi"
        fi
        ;;
    
    hotspot)
        log "Switching to hotspot mode"
        stop_chase_rainbow
        stop_pulse_green
        leds_all_off
        if start_ap; then
            pulse_green
            echo "hotspot" > "$STATE_FILE"
        else
            log "Failed to start hotspot"
        fi
        ;;
    
    off)
        log "Turning off all LEDs"
        stop_pulse_green
        stop_chase_rainbow
        leds_all_off
        echo "off" > "$STATE_FILE"
        ;;
    
    *)
        echo "JailbreakBox Manager - Unified System Manager"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|wifi|hotspot|off}"
        echo ""
        echo "Commands:"
        echo "  start   - Start network monitor with auto LED control"
        echo "  stop    - Stop all services and turn off LEDs"
        echo "  restart - Restart the manager"
        echo "  status  - Show current status"
        echo ""
        echo "Manual modes:"
        echo "  wifi    - Force WiFi mode (rainbow chase)"
        echo "  hotspot - Force hotspot mode (green pulse)"
        echo "  off     - Turn off all LEDs"
        exit 1
        ;;
esac
