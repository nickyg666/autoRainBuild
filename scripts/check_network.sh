#!/bin/bash
# Check network status and manage hotspot

# Wait for system to be ready
sleep 2

# Check if ethernet is connected
if nmcli -t FIELD -f STATE device show end0 | grep -q "connected\|activated"; then
    echo "Ethernet connected - skipping hotspot"
    
    # If connected to WiFi, don't start hotspot
    if nmcli -t FIELD -f TYPE,STATE device | grep -q "wifi.*connected\|activated"; then
        echo "Connected to WiFi - hotspot not needed"
    fi
    exit 0
fi

# No ethernet - wait 10 seconds then start hotspot
echo "No ethernet detected - starting hotspot in 10 seconds..."
sleep 10

# Start hotspot
systemctl start create-ap-hotspot.service
echo "Hotspot started - ready for devices"
