#!/bin/bash
# autoRain setup script
# Installs and configures all autoRain services

set -e

echo "=========================================="
echo "autoRain System Setup"
echo "=========================================="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "[1/6] Installing dependencies..."
apt update
apt install -y bluetooth bluez bluez-tools pulseaudio pulseaudio-utils alsa-utils beep

echo "[2/6] Installing service scripts..."
mkdir -p /usr/local/bin
cp "$SCRIPT_DIR/scripts/check_bluetooth.sh" /usr/local/bin/
cp "$SCRIPT_DIR/scripts/speaker_power.sh" /usr/local/bin/
chmod +x /usr/local/bin/*.sh

echo "[3/6] Installing systemd services..."
cp "$SCRIPT_DIR/bluetooth/bluetooth-detect.service" /etc/systemd/system/
cp "$SCRIPT_DIR/power/speaker-power.service" /etc/systemd/system/
cp "$SCRIPT_DIR/scripts/autoRain-wait.service" /etc/systemd/system/
cp "$SCRIPT_DIR/scripts/network-check.service" /etc/systemd/system/
cp "$SCRIPT_DIR/scripts/shellinabox-keeper.service" /etc/systemd/system/

systemctl daemon-reload

echo "[4/6] Enabling services..."
systemctl enable bluetooth-detect.service
systemctl enable speaker-power.service
systemctl enable autoRain-wait.service
systemctl enable network-check.service
systemctl enable shellinabox-keeper.service

echo "[5/6] Starting services..."
systemctl start bluetooth-detect.service
systemctl start shellinabox-keeper.service

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Services Started:"
echo "  - Bluetooth Detection: systemctl status bluetooth-detect.service"
echo "  - Auto Rain Wait: systemctl status autoRain-wait.service"
echo "  - Network Check: systemctl status network-check.service"
echo "  - Shellinabox Keeper: systemctl status shellinabox-keeper.service"
echo ""
echo "Workflow:"
echo "  1. Power on → Kernel loads → Bluetooth starts"
echo "  2. 2s after bluetooth.target → Check bluetooth connection"
echo "  3. If no bluetooth → Toggle speaker power"
echo "  4. Device connects → Wait for device, play beep"
echo "  5. Audio ready → Launch autoRain.py workflow"
echo "  6. Network ready → Check ethernet status"
echo "  7. If no ethernet & no WiFi → Start hotspot"
echo ""
