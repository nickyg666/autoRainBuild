#!/bin/bash
# Manual Bluetooth Device Repair Script
# Run this ONCE to fix the "Paired: no" issue with Wireless Speaker
# User must manually put speaker in pairing mode when prompted

BT_DEVICE="11:81:AA:11:88:72"
BT_DEVICE_NAME="Wireless Speaker"

echo "=================================================="
echo "Bluetooth Device Repair Tool"
echo "=================================================="
echo ""
echo "This script will:"
echo "  1. Remove the existing device entry"
echo "  2. Pair with the speaker fresh"
echo "  3. Trust the device for auto-connect"
echo ""
echo "BEFORE CONTINUING:"
echo "  - Make sure Bluetooth speaker is POWERED ON"
echo "  - Put speaker in PAIRING MODE (hold pairing button for 3-5 seconds)"
echo "  - Bring speaker within 2 meters of this device"
echo ""
read -p "Press Enter when ready, or Ctrl+C to cancel..."
echo ""

echo "Step 1: Removing old device entry..."
bluetoothctl remove "$BT_DEVICE" 2>&1 | grep -v "Device does not exist" || true
sleep 2

echo ""
echo "Step 2: Pairing with $BT_DEVICE..."
echo "  (Make sure speaker is in pairing mode NOW)"
echo ""

if bluetoothctl pair "$BT_DEVICE"; then
    echo ""
    echo "✓ Pairing successful!"
    sleep 2
else
    echo ""
    echo "✗ Pairing failed. Make sure speaker is:"
    echo "  - Powered ON"
    echo "  - In PAIRING MODE"
    echo "  - Within range"
    exit 1
fi

echo ""
echo "Step 3: Trusting device for auto-connect..."
if bluetoothctl trust "$BT_DEVICE"; then
    echo "✓ Device trusted"
else
    echo "⚠ Failed to trust device, but pairing may still work"
fi

echo ""
echo "Step 4: Testing connection..."
sleep 2
if bluetoothctl connect "$BT_DEVICE" 2>&1 | grep -q "Connection successful"; then
    echo "✓ Connection successful!"
else
    if bluetoothctl info "$BT_DEVICE" 2>/dev/null | grep -q "Connected: yes"; then
        echo "✓ Device is connected"
    else
        echo "⚠ Connection test returned mixed results, but device may still work"
    fi
fi

echo ""
echo "Step 5: Verifying device status..."
bluetoothctl info "$BT_DEVICE" | grep -E "Paired|Bonded|Trusted|Connected"

echo ""
echo "=================================================="
echo "✓ Repair complete!"
echo "=================================================="
echo ""
echo "The device should now auto-connect on boot."
echo "You can test with: bluetoothctl info $BT_DEVICE"
echo ""
