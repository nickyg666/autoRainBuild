#!/bin/bash
# backup-orangepi.sh - Create minimal differential backup for quick redeployment
# Only backs up configs and scripts, not large media files

BACKUP_DIR="/home/orangepi/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="orangepi_config_${TIMESTAMP}.tar.gz"
LOG_FILE="/home/orangepi/backup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=== Starting minimal config backup ==="
log "Backup file: $BACKUP_FILE"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup configs only (exclude large files and caches)
log "Creating compressed backup..."

tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    --exclude="*.pyc" \
    --exclude="__pycache__" \
    --exclude=".cache" \
    --exclude="node_modules" \
    --exclude="*.log" \
    --exclude="*.mp3" \
    --exclude="*.zip" \
    --exclude="*.tar.gz" \
    --exclude="backups" \
    --exclude="pipewire" \
    --exclude="autoRainBuild" \
    --exclude="*.db" \
    --exclude=".git" \
    /home/orangepi/*.py \
    /home/orangepi/*.sh \
    /home/orangepi/*.md \
    /home/orangepi/*.txt \
    /home/orangepi/*.json \
    /home/orangepi/.bash* \
    /home/orangepi/.led* \
    /home/orangepi/.profile \
    /home/orangepi/.zshrc \
    /home/orangepi/autoRain \
    /home/orangepi/autoRain/scripts \
    /home/orangepi/python-fun \
    /home/orangepi/utils \
    /home/orangepi/etc \
    /home/orangepi/systemd \
    /etc/systemd/system/gpio71-init.service \
    /etc/systemd/system/leds-off.service \
    /etc/systemd/system/auto-wifi-connect.service \
    /etc/systemd/system/jailbreakbox-ap*.service \
    /etc/modules-load.d/modules.conf 2>/dev/null

BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
log "Backup complete! Size: $BACKUP_SIZE"

# Create restore script
RESTORE_SCRIPT="$BACKUP_DIR/restore_${TIMESTAMP}.sh"
cat > "$RESTORE_SCRIPT" <<'EOF'
#!/bin/bash
# restore-orangepi.sh - Quick restore from backup
# Run this after fresh OS install

set -e

BACKUP_FILE="$1"
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "=== Restoring from backup ==="
echo "Backup: $BACKUP_FILE"
echo ""

# Check if we're root or can use sudo
if [ "$EUID" -ne 0 ]; then
    SUDO="sudo"
else
    SUDO=""
fi

# Stop services that might interfere
echo "Stopping services..."
$SUDO systemctl stop hostapd 2>/dev/null || true
$SUDO systemctl stop dnsmasq 2>/dev/null || true
$SUDO systemctl stop gpio71-init 2>/dev/null || true
$SUDO systemctl stop leds-off 2>/dev/null || true

# Extract backup
echo "Extracting backup..."
$SUDO tar -xzf "$BACKUP_FILE" -C /

# Restore permissions
echo "Restoring permissions..."
$SUDO chown -R orangepi:orangepi /home/orangepi
$SUDO chmod +x /home/orangepi/*.sh 2>/dev/null || true

# Reload systemd
echo "Reloading systemd..."
$SUDO systemctl daemon-reload

# Enable and start custom services
echo "Enabling services..."
$SUDO systemctl enable gpio71-init 2>/dev/null || true
$SUDO systemctl enable leds-off 2>/dev/null || true
$SUDO systemctl enable auto-wifi-connect 2>/dev/null || true
$SUDO systemctl enable jailbreakbox-ap-manager 2>/dev/null || true
$SUDO systemctl enable jailbreakbox-ap 2>/dev/null || true

# Start services
echo "Starting services..."
$SUDO systemctl restart gpio71-init 2>/dev/null || true
$SUDO systemctl restart leds-off 2>/dev/null || true

# Fix LED config permissions
$SUDO chown orangepi:orangepi /home/orangepi/.led_config.json 2>/dev/null || true

echo ""
echo "=== Restore complete ==="
echo "Please reboot for all changes to take effect"
echo ""
echo "After reboot, verify:"
echo "  - GPIO pins are at 0: sudo gpioget gpiochip1 69 71 72 73 74 75 230 232 233"
echo "  - LED aliases work: source ~/.led_aliases && LED1R=1"
echo "  - WiFi is working: nmcli device wifi list"
EOF

chmod +x "$RESTORE_SCRIPT"
log "Restore script created: $RESTORE_SCRIPT"

log "=== Backup complete ==="
echo ""
echo "Backup saved to: $BACKUP_DIR/$BACKUP_FILE"
echo "Size: $BACKUP_SIZE"
echo "Restore script: $RESTORE_SCRIPT"
echo ""
echo "To restore after fresh install:"
echo "  $RESTORE_SCRIPT $BACKUP_FILE"
