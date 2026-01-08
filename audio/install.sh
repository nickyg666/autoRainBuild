#!/bin/bash
# audio/install.sh - Install all audio packages
# This script installs everything needed for audio/speaker management
# COPY ONLY - doesn't run anything that could affect running system

set -e

echo "=========================================="
echo "Audio Packages Installation"
echo "=========================================="
echo ""
echo "Packages to be installed (if not already):"
echo "  - pulseaudio"
echo "  - pulseaudio-utils"
echo "  - alsa-utils"
echo "  - alsa-base"
echo "  - beep"
echo "  - bluez"
echo "  - bluez-tools"
echo "  - pulseaudio-module-bluetooth"
echo ""
echo "To actually install, run this script or use:"
echo "  sudo apt install -y pulseaudio pulseaudio-utils alsa-utils alsa-base beep bluez bluez-tools pulseaudio-module-bluetooth"
echo ""
echo "=========================================="
