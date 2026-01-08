# autoRain

System configuration and management for Orange Pi Zero 2 - base layer before adding hostapd/shellinabox/PythonSSHLearningCenter.

## 🎯 What This Project Does

This is the **system recreation layer** that configures the base Orange Pi Zero 2 system before adding the WiFi hotspot and learning environment.

**Layer Order:**
1. **autoRain** (this project) - Base system configuration
2. **PythonSSHLearningCenter** - WiFi hotspot + Python learning environment

## 🌟 Features

### System Configurations
- Bluetooth management and profiles
- Audio/speaker management
- Power management
- USB device management (usbmuxd)
- Palera1n installation and setup
- User environment configs (.bash_profile, .bashrc)

### Goals
- Reproducible system setup
- Automated configuration
- Version-controlled system files
- Easy system restoration

## 📂 Project Structure

```
autoRain/
├── system-configs/      # Base system configuration files
│   ├── bash/           # Shell profiles (.bash_profile, .bashrc)
│   └── system/         # System-wide configs
├── bluetooth/           # Bluetooth management
│   ├── configs/        # Bluetooth configs
│   └── scripts/       # Bluetooth management scripts
├── audio/              # Audio/speaker management
│   ├── configs/        # Audio configs (pulseaudio, alsa)
│   └── scripts/       # Audio control scripts
├── power/              # Power management
│   ├── configs/        # Power configs
│   └── scripts/       # Power control scripts
├── palera1n/          # Palera1n setup and config
│   ├── install.sh       # Installation script
│   └── configs/        # Palera1n configs
├── usbmuxd/            # iPhone USB management
│   ├── configs/        # usbmuxd configs
│   └── scripts/       # usbmuxd management
├── scripts/            # General system scripts
│   └── setup.sh       # System setup script
└── README.md           # This file
```

## 🚀 Installation

### Full System Setup

```bash
cd autoRain
sudo ./scripts/setup.sh
```

This will:
- Configure Bluetooth
- Setup audio/speakers
- Configure power management
- Install and setup palera1n
- Configure usbmuxd
- Set up user shell environment

### Individual Component Setup

```bash
# Bluetooth
sudo bluetooth/install.sh

# Audio
sudo audio/install.sh

# Power
sudo power/install.sh

# Palera1n
sudo palera1n/install.sh

# USBmuxd
sudo usbmuxd/install.sh
```

## 🔧 System Requirements

- Orange Pi Zero 2
- Armbian/Debian-based Linux
- Bluetooth adapter
- Audio output (speakers/audio jack)
- Palera1n-compatible device

## 📝 Current Status

**Components implemented:**
- [ ] Bluetooth management
- [ ] Audio/speaker management
- [ ] Power management
- [ ] Palera1n setup
- [ ] USBmuxd management
- [ ] System shell configs

**Status: Project scaffold created, components to be implemented**

## 🎯 Design Philosophy

- **Separation of Concerns**: System layer separate from application layer
- **Modularity**: Each component can be installed independently
- **Reproducibility**: Complete system recreation from scratch
- **Documentation**: Every config explained and documented

## 🔗 Related Projects

- **PythonSSHLearningCenter**: WiFi hotspot + shellinabox + Python learning
  - Installs ON TOP of this base system
  - Provides network access and coding environment

## 🤝 Contributing

This project is the foundation for a complete, reproducible system setup.

To add a new component:
1. Create directory under appropriate category
2. Add installation script
3. Document configuration options
4. Test on clean system

## 📄 License

Use as you wish.

---

**Note**: This is the base system layer. Install PythonSSHLearningCenter after this for complete setup.
