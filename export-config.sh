#!/bin/bash
# Export current configuration to autoRainBuild

set -e

echo "Exporting current configuration to autoRainBuild..."

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Backup existing configs
mkdir -p "$SCRIPT_DIR/configs/backup"
mkdir -p "$SCRIPT_DIR/configs/options-enabled"

echo "[1/5] Exporting shellinabox config..."
cp /etc/default/shellinabox "$SCRIPT_DIR/configs/"

echo "[2/5] Exporting nginx captive portal config..."
cp /etc/nginx/sites-available/captive-portal "$SCRIPT_DIR/configs/"

echo "[3/5] Exporting hotspot service..."
cp /etc/systemd/system/create-ap-hotspot.service "$SCRIPT_DIR/configs/"

echo "[4/5] Exporting shellinabox CSS options..."
cp -r /etc/shellinabox/options-enabled/* "$SCRIPT_DIR/configs/options-enabled/"

echo "[5/5] Exporting iptables rules (if available)..."
if [ -f /etc/iptables/rules.v4 ]; then
    cp /etc/iptables/rules.v4 "$SCRIPT_DIR/configs/"
fi

echo ""
echo "Export complete! Configuration files saved to:"
echo "  $SCRIPT_DIR/configs/"
echo ""
echo "You can now commit these changes with git."
