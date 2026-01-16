#!/bin/bash
# Bluetooth Connectivity Diagnostic Script
# Helps identify why Bluetooth connection is failing

LOG_FILE="/home/orangepi/autoRain.log"
BT_DEVICE="11:81:AA:11:88:72"

echo "=================================================="
echo "Bluetooth Connectivity Diagnostic Report"
echo "=================================================="
echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

echo "1. BLUETOOTH SERVICE STATUS"
echo "=================================================="
systemctl status bluetooth --no-pager | head -10
echo ""

echo "2. BLUETOOTH ADAPTER STATUS"
echo "=================================================="
bluetoothctl show
echo ""

echo "3. PAIRED DEVICES"
echo "=================================================="
bluetoothctl devices
echo ""

echo "4. TARGET DEVICE INFORMATION"
echo "=================================================="
echo "Device MAC: $BT_DEVICE"
if bluetoothctl devices | grep -q "$BT_DEVICE"; then
    echo "Status: PAIRED ✓"
    echo ""
    bluetoothctl info "$BT_DEVICE"
else
    echo "Status: NOT PAIRED ✗"
fi
echo ""

echo "5. DEVICE CONNECTION HISTORY"
echo "=================================================="
tail -20 "$LOG_FILE" | grep -E "bluetooth|Bluetooth|connect" || echo "No recent Bluetooth logs"
echo ""

echo "6. TROUBLESHOOTING STEPS"
echo "=================================================="
echo ""
echo "If device is NOT PAIRED:"
echo "  1. Power on the Bluetooth speaker"
echo "  2. Put speaker in pairing mode"
echo "  3. Run: bluetoothctl"
echo "  4. Then: pair $BT_DEVICE"
echo "  5. Then: trust $BT_DEVICE"
echo "  6. Then: exit"
echo ""

echo "If device IS PAIRED but won't connect:"
echo "  1. Check if device is powered on and in range"
echo "  2. Remove and re-add device:"
echo "     bluetoothctl remove $BT_DEVICE"
echo "     (Then repeat pairing steps above)"
echo "  3. Restart Bluetooth service:"
echo "     sudo systemctl restart bluetooth"
echo "  4. Check dmesg for hardware errors:"
echo "     dmesg | tail -50 | grep -i bluetooth"
echo ""

echo "7. DEVICE POWER AND SIGNAL"
echo "=================================================="
echo "Attempting to connect and check signal..."
bluetoothctl connect "$BT_DEVICE" 2>&1 | head -3
sleep 3
if bluetoothctl info "$BT_DEVICE" 2>/dev/null | grep -q "Connected: yes"; then
    echo "✓ Connection successful!"
    bluetoothctl info "$BT_DEVICE" | grep -E "Connected|RSSI|Class"
else
    echo "✗ Connection failed"
    echo ""
    echo "Debug Info:"
    bluetoothctl info "$BT_DEVICE" | grep -E "Connected|Bonded|Paired|Trusted"
fi
echo ""

echo "=================================================="
echo "End of Diagnostic Report"
echo "=================================================="
