# Quick Start Guide

## Install on New System

1. Clone or copy the autoRainBuild directory
2. Run the installation script:

```bash
cd autoRainBuild
sudo ./install.sh
```

That's it! The script handles everything.

## What Gets Installed

- **WiFi Hotspot**: Open network "jailbreakBox"
- **Captive Portal**: Redirects to shellinabox terminal
- **Internet Sharing**: Automatic from ethernet
- **Auto-start**: Enabled on boot

## Testing

1. Connect WiFi device to "jailbreakBox"
2. Windows should show captive portal popup
3. Terminal should appear in browser
4. Or navigate to: http://192.168.12.1

## Quick Commands

```bash
# Status
sudo systemctl status create-ap-hotspot.service

# Stop/Start
sudo systemctl stop create-ap-hotspot.service
sudo systemctl start create-ap-hotspot.service

# View logs
sudo journalctl -u create-ap-hotspot.service -f

# List connected clients
sudo create_ap --list-clients wlan0
```

## Network Details

- **SSID**: jailbreakBox
- **Gateway**: 192.168.12.1
- **DHCP Range**: 192.168.12.1 - 192.168.12.254
- **WiFi Interface**: wlan0
- **Internet Source**: end0 (ethernet)

## Config File Locations

If you need to manually edit:

- `/etc/default/shellinabox` - Shellinabox settings
- `/etc/nginx/sites-available/captive-portal` - Nginx config
- `/etc/systemd/system/create-ap-hotspot.service` - Hotspot service
- `/etc/shellinabox/options-enabled/` - Terminal CSS themes

## Updating Configuration

After making changes to files in `configs/`, run:

```bash
sudo ./export-config.sh  # Export to files (if you edited system files)
# Or manually copy files to their locations

# Restart services
sudo systemctl restart create-ap-hotspot.service
sudo systemctl restart shellinabox
sudo systemctl reload nginx
```

## Development Workflow

1. Edit config files in `configs/` directory
2. Copy to system locations (or run install.sh)
3. Test locally
4. Commit changes:

```bash
git add .
git commit -m "Description of changes"
```

## Troubleshooting

**Hotspot not visible:**
```bash
sudo rfkill unblock wifi
sudo systemctl restart create-ap-hotspot.service
```

**Captive portal not working:**
```bash
curl http://127.0.0.1/  # Test locally
sudo systemctl restart shellinabox nginx
```

**No internet on clients:**
```bash
sudo iptables -t nat -L -n -v  # Check rules
sudo systemctl restart create-ap-hotspot.service
```

## Notes

- Network is open (no password) - use secure environment
- Terminal provides full shell access
- SSH also available on port 22
- Works with or without ethernet connection
