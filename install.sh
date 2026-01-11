#!/bin/bash
# autoRainBuild Installation Script
# This script installs and configures a WiFi hotspot with shellinabox captive portal

set -e

echo "=================================="
echo "autoRainBuild Installation Script"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "[1/7] Installing required packages..."
apt update
apt install -y git create_ap nginx shellinabox dnsmasq hostapd

echo "[2/7] Configuring shellinabox..."
cp "$SCRIPT_DIR/configs/shellinabox" /etc/default/shellinabox
systemctl restart shellinabox
systemctl enable shellinabox

echo "[3/7] Configuring nginx captive portal..."
cp "$SCRIPT_DIR/configs/captive-portal" /etc/nginx/sites-available/
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/captive-portal /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

echo "[4/7] Copying shellinabox CSS options..."
cp -r "$SCRIPT_DIR/configs/options-enabled" /etc/shellinabox/

echo "[5/7] Installing hotspot service..."
cp "$SCRIPT_DIR/configs/create-ap-hotspot.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable create-ap-hotspot.service

echo "[6/7] Starting hotspot service..."
systemctl start create-ap-hotspot.service
sleep 3

echo "[7/7] Verifying installation..."
echo ""
echo "=== Service Status ==="
systemctl status create-ap-hotspot.service --no-pager | head -5
systemctl status shellinabox --no-pager | head -5
systemctl status nginx --no-pager | head -5

echo ""
echo "=== Network Status ==="
iw dev 2>/dev/null || echo "Wireless interface check..."
ip addr show wlan0 2>/dev/null || echo "wlan0 not ready yet (waiting for hotspot...)"

echo ""
echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
echo "Hotspot Details:"
echo "  SSID: jailbreakBox"
echo "  Gateway: 192.168.12.1"
echo "  Captive Portal: http://192.168.12.1"
echo ""
echo "Useful Commands:"
echo "  sudo systemctl status create-ap-hotspot.service"
echo "  sudo create_ap --list-clients wlan0"
echo "  sudo journalctl -u create-ap-hotspot.service -f"
echo ""
