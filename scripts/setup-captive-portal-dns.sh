#!/bin/bash
# Script to add captive portal DNS redirects to dnsmasq

# Wait for create_ap to start dnsmasq
sleep 3

# Find only the newest/active dnsmasq config from create_ap
DNSMASQ_CONF=$(find /tmp -name "dnsmasq.conf" -path "*/create_ap.wlan0.conf.*" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)

if [ -z "$DNSMASQ_CONF" ] || [ ! -f "$DNSMASQ_CONF" ]; then
    exit 0
fi

# Check if we haven't already added redirects
if ! grep -q "Captive Portal DNS Redirects" "$DNSMASQ_CONF" 2>/dev/null; then
    # Add captive portal DNS redirects
    {
        echo ""
        echo "# Captive Portal DNS Redirects"
        echo "# Apple iOS/macOS"
        echo "address=/captive.apple.com/192.168.12.1"
        echo "address=/www.apple.com/192.168.12.1"
        echo "address=/www.appleiphonecell.com/192.168.12.1"
        echo "address=/www.airport.us/192.168.12.1"
        echo "address=/www.ibook.info/192.168.12.1"
        echo "address=/www.itools.info/192.168.12.1"
        echo "address=/www.thinkdifferent.us/192.168.12.1"
        echo ""
        echo "# Android/Google"
        echo "address=/clients3.google.com/192.168.12.1"
        echo "address=/connectivitycheck.android.com/192.168.12.1"
        echo "address=/connectivitycheck.gstatic.com/192.168.12.1"
        echo "address=/clients4.google.com/192.168.12.1"
        echo "address=/android.clients.google.com/192.168.12.1"
        echo "address=/www.gstatic.com/192.168.12.1"
        echo "address=/www.google.com/192.168.12.1"
        echo ""
        echo "# Microsoft Windows NCSI"
        echo "address=/www.msftconnecttest.com/192.168.12.1"
        echo "address=/www.msftncsi.com/192.168.12.1"
    } >> "$DNSMASQ_CONF"
    
    echo "Captive portal DNS redirects added to $DNSMASQ_CONF"
    
    # Get dnsmasq PID from same directory
    DIR=$(dirname "$DNSMASQ_CONF")
    if [ -f "$DIR/dnsmasq.pid" ]; then
        DNMASQ_PID=$(cat "$DIR/dnsmasq.pid")
        if [ -n "$DNMASQ_PID" ] && [ -d "/proc/$DNMASQ_PID" ]; then
            kill -HUP "$DNMASQ_PID" 2>/dev/null
            echo "Reloaded dnsmasq (PID: $DNMASQ_PID)"
        fi
    fi
fi

exit 0
