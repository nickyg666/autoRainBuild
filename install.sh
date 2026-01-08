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

 echo "[1/9] Installing required packages..."
 apt update
 apt install -y git create_ap nginx shellinabox dnsmasq hostapd python3-tk

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

 echo "[5/9] Installing DNS setup script..."
 cp "$SCRIPT_DIR/scripts/setup-captive-portal-dns.sh" /usr/local/bin/
 chmod +x /usr/local/bin/setup-captive-portal-dns.sh

 echo "[6/9] Installing hotspot service..."
 cp "$SCRIPT_DIR/configs/create-ap-hotspot.service" /etc/systemd/system/
 systemctl daemon-reload
 systemctl enable create-ap-hotspot.service

 echo "[7/9] Setting up Python examples..."
 USER="orangepi"
 cp -r "$SCRIPT_DIR/python-fun" "/home/$USER/"
 chown -R "$USER:$USER" "/home/$USER/python-fun"
 cp "$SCRIPT_DIR/scripts/welcome-message.sh" "/home/$USER/.welcome"
 chown "$USER:$USER" "/home/$USER/.welcome"
 echo "/home/$USER/.welcome" >> "/home/$USER/.bashrc"
 chown "$USER:$USER" "/home/$USER/.bashrc"

 echo "[8/9] Setting up user access (passwordless login & sudo)..."
 # Remove password for user
 passwd -d "$USER" 2>/dev/null || true
 # Setup passwordless sudo
 cp "$SCRIPT_DIR/configs/sudoers-nopass.template" "/etc/sudoers.d/$USER-nopass"
 sed -i "s/orangepi/$USER/" "/etc/sudoers.d/$USER-nopass"
 chmod 0440 "/etc/sudoers.d/$USER-nopass"

 echo "[9/9] Starting hotspot service..."
 systemctl start create-ap-hotspot.service
 sleep 3

 echo "[10/10] Verifying installation..."
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
 echo "  Captive Portal: http://192.168.12.1:4200"
 echo ""
 echo "Python Fun:"
 echo "  Location: ~/python-fun/"
 echo "  Examples: games, turtle art, hello world"
 echo ""
 echo "Useful Commands:"
 echo "  sudo systemctl status create-ap-hotspot.service"
 echo "  sudo create_ap --list-clients wlan0"
 echo "  sudo journalctl -u create-ap-hotspot.service -f"
 echo "  cd ~/python-fun && python3 hello.py"
 echo ""
 echo "User Setup:"
 echo "  - Passwordless login configured for $USER"
 echo "  - Passwordless sudo configured for $USER"
 echo "  - Welcome message shows on login"
 echo ""
