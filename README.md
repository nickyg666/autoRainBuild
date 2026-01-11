# 🌧️ autoRain - System Building Blocks for Orange Pi Zero 2

Think of this project as a LEGO set for your computer! We build the foundation first, then add the fun stuff later.

## 🎯 What This Project Does

This is your **system construction kit** that makes your Orange Pi Zero 2 work the way you want it to!

**How it works:**
1. **autoRain** (this project) - Build the foundation 🏗️
2. **PythonSSHLearningCenter** - Add WiFi hotspot + Python learning 🎮

## 🧩 What's Inside - Understanding Each Part

### 🔵 Bluetooth (Wireless Devices)
**What it does:** Connect phones, headphones, speakers wirelessly!

**How it works:**
- System starts
- Waits 2 seconds (gives Bluetooth time to start)
- Checks if anything is connected
- If nothing connected → Toggles speaker power ON/OFF
- If device connects → Plays a little beep!

**Why?** Saves power and only turns on speakers when you need them!

### 🔊 Audio/Speakers (Sound)
**What it does:** Makes sounds play through your speakers!

**How it works:**
- Script checks if speakers are working
- When device connects → Plays a beep to test speakers
- If speakers work → Ready for music/games!
- If not working → Tells you what's wrong

**Why?** Makes sure audio is ready before trying to use it!

### ⚡ Power (Electricity)
**What it does:** Controls power to devices!

**How it works:**
- Uses GPIO pins (special connection points)
- Turns speakers ON or OFF
- Saves battery by turning things off when not used

**Why?** Saves power, makes device last longer on battery!

### 📱 USBmuxd (iPhone USB Cable)
**What it does:** Connects iPhones using USB cable instead of WiFi!

**How it works:**
- Detects when iPhone plugged in via USB
- Lets you access iPhone files and sync
- Faster than WiFi sometimes!

**Why?** Some people like using cables, not wireless!

### 🔐 Palera1n (Apple Device Security)
**What it does:** A special tool for checking Apple devices!

**How it works:**
- You can build this tool from code (source code)
- It compiles (turns into a program you can run)
- Helps with security on Apple devices

**Why?** Advanced tool for people who work with Apple devices a lot!

### 🖥️ Shell Configs (Terminal Settings)
**What it does:** Makes your terminal (the black screen with typing) look and work better!

**How it works:**
- .bashrc = Settings that load every time you open terminal
- .bash_profile = Settings that load when you login
- Can add colors, shortcuts, and helpful commands

**Why?** Makes using the terminal easier and more fun!

## 🎮 The Big Picture - How Everything Works Together

Think of it like building a smart house:

```
┌─────────────────────────────────────────────┐
│         ORANGE PI ZERO 2                │
│                                         │
│  ⚡ POWER ON                           │
│       ↓                                 │
│  📊 KERNEL (OS starts)                │
│       ↓                                 │
│  🔵 BLUETOOTH STARTS                  │
│       ↓ (wait 2 seconds)                 │
│  📱 CHECK DEVICE                         │
│       ↓                                  │
│  ┌──────────┬──────────┐            │
│  │ NO DEVICE │ DEVICE   │            │
│  │   │      │   │       │            │
│  │   ↓      │   ↓       │            │
│  🔊 TOGGLE │ 🎵 BEEP   │            │
│  │ SPEAKER  │  AUDIO    │            │
│  │ POWER    │  READY    │            │
│  └──────────┴──────────┘            │
│       ↓                                  │
│  🖥️ LAUNCH AUTORAIN.PY             │
│       ↓                                  │
│  🎮 START YOUR PROGRAMS!              │
│                                         │
└─────────────────────────────────────────────┘

THEN... NETWORK STUFF:

┌─────────────────────────────────────────────┐
│  🌐 NETWORK CHECK                      │
│       ↓                                  │
│  ┌──────┬──────────┐                │
│  │ HOME  │ WORK/     │                │
│  │       │           │                │
│  │ ↓     │ ↓         │                │
│  ✅     │ ⏳        │                │
│  ETHER  │ WAIT 10s   │                │
│  │       │ ↓         │                │
│  │       │ 📶 START  │                │
│  │       │ HOTSPOT    │                │
│  └──────┴──────────┘                │
│                                         │
│  ✅ ALWAYS: SHELLINABOX RUNNING       │
│     (Browser terminal always available)    │
└─────────────────────────────────────────────┘
```

## 🧩 Why Can't We Include Compiled Files? 📁

Great question! Here's the explanation:

### What is a Compiled File?

Think of it like a cake:

**Code** = Recipe (what to make)
**Compiler** = The chef who bakes the cake
**Compiled File** = The finished cake ready to eat!

### Why Not Include Pre-Compiled Files?

**Analogy:** Imagine you want a chocolate cake:

**Option A:** I bake it and mail it to you
- Might get squished in the mail 📦
- Might get old 🕰
- Might taste different than you expect!

**Option B:** I give you the recipe, YOU bake it
- Perfect cake every time! 🎂
- Fresh and warm!
- Made exactly how YOU want it!

### Same with Code!

Some tools (like Palera1n) need to be built:

**Pre-compiled:** Someone else's build
- Might not work on YOUR exact computer
- Might be old version
- You can't change it!

**From source:** YOU build it yourself
- Works perfectly on YOUR Orange Pi
- Always the latest version
- You can see how it works!

## 🔨 How to Build Things (Step-by-Step)

### Building Palera1n (If Included)

**What it does:** Makes a tool for checking Apple devices

**Steps:**

1. **Get the recipe (download code)**
   ```bash
   cd palera1n
   git clone https://github.com/Nikias11/palera1n.git .
   ```

2. **Get the kitchen ready (install ingredients)**
   ```bash
   sudo apt install -y build-essential
   sudo apt install -y libimobiledevice-dev
   sudo apt install -y libplist-dev
   sudo apt install -y libusbmuxd-dev
   ```

3. **Start cooking (compile the code)**
   ```bash
   make clean    # Clean up old stuff
   make          # This is the compiler working!
   ```
   
   **What you'll see:**
   ```
   Reading recipe files...
   Setting up kitchen...
   Cooking part 1...
   Cooking part 2...
   Putting everything together...
   Done! (Your cake is ready!)
   ```

4. **Serve the dish (install the tool)**
   ```bash
   sudo make install
   ```

### Why This Takes Time

Think about baking a cake from scratch - you don't just push a button! You need to:
- Read all the instructions
- Mix the ingredients properly
- Bake at the right temperature
- Wait for it to be done

Same with compiling! It might take 5-30 minutes on small computers like Orange Pi.

**Tip:** Get a snack while it compiles! 🍪

## 🚀 How to Install Everything

### Option 1: The Easy Way (Recommended!)

```bash
# Go to the project folder
cd autoRain

# Run the magic installer
sudo ./scripts/setup.sh
```

**What happens automatically:**
1. ✅ Downloads all needed tools
2. ✅ Sets up Bluetooth detection
3. ✅ Configures audio/speakers
4. ✅ Sets up power management
5. ✅ Installs USBmuxd
6. ✅ Copies shell settings
7. ✅ Starts all services
8. ✅ Makes them start automatically on boot

### Option 2: Build One Thing at a Time

If you want to learn how each part works:

```bash
# Just want Bluetooth?
sudo bluetooth/install.sh

# Just want audio?
sudo audio/install.sh

# Just want Palera1n?
cd palera1n
make && sudo make install
```

## 📚 Understanding Compiling (For Kids!)

### What is "Compiling"?

Computers understand **machine language** (lots of 0s and 1s).

We write code in **human language** (words like "if", "print", "hello").

A **compiler** is like a translator:
- Takes our human-readable code
- Translates it to machine language
- Creates a file that the computer can run fast!

### Example: Very Simple!

**Our code:**
```python
print("Hello, World!")
```

**After compiling:**
```
01001000 01100001 01110100 01101111...
(millions of 0s and 1s that the computer understands!)
```

### Why Build on Your Own Computer?

Every computer is a little different:
- Different "brain" (CPU)
- Different "body" (hardware)
- Different "language version"

**If I bake a cake and send it to you:**
- Your oven might be different
- Might not cook perfectly!

**If YOU bake the cake using my recipe:**
- Works in YOUR oven perfectly
- You can change the recipe!
- You learn how baking works!

## 🛠️ Troubleshooting

### "make: command not found"
**What this means:** Your kitchen isn't set up yet!

**Fix:**
```bash
sudo apt install -y build-essential
```

### "Missing dependencies"
**What this means:** You're missing recipe ingredients!

**Fix:**
```bash
# Read the README or install script
# It will tell you what to install
sudo apt install -y [list of packages]
```

### "Build takes forever!"
**Is this normal?** YES! Building can take 5-30 minutes!

**What to do:** 
- Go get a snack 🍪
- Watch the progress
- Be patient - it's working!

### "Permission denied"
**What this means:** You're trying to install without being the boss!

**Fix:**
```bash
# Add "sudo" before the command
sudo make install
```

## 📚 Learn More!

### Want to be a system builder?

**Books (Online & Free):**
- Linux From Scratch: https://linuxfromscratch.org/
- Systemd for services: https://freedesktop.org/wiki/software/systemd/

**Practice:**
- Try building small C programs
- Learn how to write shell scripts
- Understand how Linux starts up (boot process)

## 🤝 How to Add New Things

Want to add something cool to autoRain?

**Easy steps:**
1. Create a folder in the right place (bluetooth/, audio/, power/, etc.)
2. Write your code or scripts
3. Add comments explaining what it does
4. Test it to make sure it works
5. Add it to the main setup.sh script
6. Commit and share!

## 🎯 What Comes After This?

**Next step:** Install PythonSSHLearningCenter!

This adds:
- 📶 WiFi hotspot (connect phones, laptops)
- 🖥️ Browser terminal (no SSH needed!)
- 🎮 Python games and learning
- 🎨 Turtle graphics and fun examples

**Together:** A complete coding playground for kids!

## 💡 Cool Things You Can Try

1. **Make Orange Pi a smart speaker**
   - Auto-connect to your phone
   - Play music when you walk in the door

2. **Make it a game server**
   - Friends connect to hotspot
   - Play games together

3. **Make it a security camera**
   - Detect when motion happens
   - Send you a notification

## 🔐 Is This Safe?

**For Your System:**
- ✅ All scripts are documented
- ✅ System security stays intact
- ✅ You control what runs

**For Your Network:**
- ⚠️ Hotspot is open (when you install PythonSSHLearningCenter)
- ⚠️ Use in trusted places (home, classroom)
- ✅ Your personal files stay safe

## 📄 License

Use as you wish! Build whatever you want!

---

## 🌟 Remember:

**Building systems is like being a LEGO master** 🧱
- Follow the instructions
- Take your time
- If something breaks, that's OK!
- Learn from fixing it
- Have fun building!

**You're a system builder now!** 🏗️✨

---

**Made for builders of all ages who want to understand their computers**

## 🔊 Audio Files Included

The following MP3 sounds are included in `audio/sounds/`:
- **ready.mp3** - "Ready to code!" sound (plays when device connects)
- **step1.mp3** - Step 1 completion sound
- **step2.mp3** - Step 2 completion sound
- **complete.mp3** - "All done!" celebration sound
- **retry.mp3** - "Try again!" encouragement sound
- **shutdown.mp3** - System shutdown sound

These are used by:
- `autoRain.py` - Plays ready.mp3 when device connects
- You can use them in your own scripts!
- Just play: `mpg123 /home/orangepi/autoRain/audio/sounds/ready.mp3`

## 🐛 Recent Fixes & Updates

### Audio Path Fix (2026-01-08)
**Problem:** autoRain.py couldn't access PulseAudio at boot time
**Solution:** Updated PULSE_SERVER path from `/run/pulse/native` to `/run/user/1000/pulse/native`
**Files Changed:**
- `autoRain.py` - All audio functions now use correct PulseAudio socket path

**What this fixes:**
- Audio playback works when autoRain starts at boot
- Bluetooth speaker audio playback now works reliably
- No more "audio failed to play" errors in logs

### User Configuration (2026-01-08)
**Users created:**
- `orangepi` - Default user, password: `orangepi`
- `lorenzo` - Admin user with full sudo access, no password required

**Why two users?**
- `orangepi` is the default system user for normal operations
- `lorenzo` is for administrative tasks (sudo NOPASSWD: ALL)

## 📦 Installing Audio Packages

Audio packages available in `audio/install.sh`:
- pulseaudio (main audio system)
- pulseaudio-utils (control tools: pactl, pacmd)
- alsa-utils (aplay, speaker-test)
- alsa-base (low-level audio tools)
- beep (simple beep sounds)
- bluez (Bluetooth audio)
- bluez-tools (bluetoothctl control)

**Note:** This is a COPY script - shows what to install, doesn't actually install.
To install packages, run the script yourself or use:
```bash
sudo apt install -y pulseaudio pulseaudio-utils alsa-utils alsa-base beep bluez bluez-tools pulseaudio-module-bluetooth
```

=======
# autoRainBuild - Hotspot with Shellinabox Captive Portal

Complete setup for an Orange Pi Zero 2 WiFi hotspot with shellinabox terminal as a captive portal.

## Features

- WiFi hotspot with SSID "jailbreakBox" (open network, no password)
- Automatic internet sharing from ethernet connection (end0)
- Captive portal that redirects to shellinabox terminal
- Automatic startup on boot
- Version controlled with git

## System Requirements

- Orange Pi Zero 2 (or similar SBC)
- WiFi adapter (wlan0)
- Ethernet connection (end0) for internet sharing
- Debian-based Linux (tested on Armbian)

## Installation

### 1. Install Required Packages

```bash
sudo apt update
sudo apt install -y git create_ap nginx shellinabox dnsmasq hostapd
```

### 2. Configure Shellinabox (no SSL)

```bash
sudo cp configs/shellinabox /etc/default/shellinabox
sudo systemctl restart shellinabox
sudo systemctl enable shellinabox
```

### 3. Configure Nginx Captive Portal

```bash
sudo cp configs/captive-portal /etc/nginx/sites-available/
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/captive-portal /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Copy Shellinabox CSS Options

```bash
sudo cp -r configs/options-enabled /etc/shellinabox/
```

### 5. Install Hotspot Service

```bash
sudo cp configs/create-ap-hotspot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable create-ap-hotspot.service
```

### 6. Start Services

```bash
sudo systemctl start create-ap-hotspot.service
sudo systemctl status create-ap-hotspot.service
```

### 7. Configure Iptables (if not using iptables-persistent)

The hotspot will configure iptables automatically, but you can make them persistent:

```bash
sudo apt install -y iptables-persistent
# The rules are set by create_ap, so no need to manually add them
```

## Manual Start/Stop

```bash
# Start hotspot
sudo systemctl start create-ap-hotspot.service

# Stop hotspot  
sudo systemctl stop create-ap-hotspot.service

# Check status
sudo systemctl status create-ap-hotspot.service

# List connected clients
sudo create_ap --list-clients wlan0

# View logs
sudo journalctl -u create-ap-hotspot.service -f
```

## Configuration Details

### Hotspot Network
- **SSID:** jailbreakBox
- **Gateway:** 192.168.12.1
- **DHCP Range:** 192.168.12.1 - 192.168.12.254
- **WiFi Interface:** wlan0
- **Internet Source:** end0 (ethernet)

### Captive Portal
- **Port:** HTTP 80 (redirects to nginx)
- **Nginx Port:** 80 (proxies to shellinabox)
- **Shellinabox Port:** 4200 (HTTP only, no SSL)
- **Target:** Terminal login prompt

### Services
- `create-ap-hotspot.service` - Manages WiFi hotspot
- `shellinabox.service` - Provides web-based terminal
- `nginx.service` - Proxies HTTP to shellinabox

## Troubleshooting

### Hotspot not visible
```bash
sudo rfkill unblock wifi
sudo systemctl restart create-ap-hotspot.service
```

### Captive portal not working
```bash
sudo systemctl status shellinabox
sudo systemctl status nginx
curl http://127.0.0.1/  # Test locally
```

### Clients not getting internet
```bash
sudo iptables -t nat -L -n -v  # Check NAT rules
sudo systemctl restart create-ap-hotspot.service
```

### Check wireless interface
```bash
iw dev  # Should show wlan0 as AP mode
ip addr show wlan0  # Should show 192.168.12.1/24
```

## File Locations

- `/etc/default/shellinabox` - Shellinabox daemon configuration
- `/etc/nginx/sites-available/captive-portal` - Nginx captive portal config
- `/etc/systemd/system/create-ap-hotspot.service` - Hotspot systemd service
- `/etc/shellinabox/options-enabled/` - CSS themes for terminal

## Notes

- The hotspot is configured as an open network (no password)
- Internet is automatically shared from ethernet when connected
- Windows devices should show a captive portal popup automatically
- SSH access to the terminal is also available on port 22
- The captive portal provides a full shell via web browser

## Development

To contribute changes:

1. Make changes to config files
2. Test locally
3. Update this README if needed
4. Commit changes with git

```bash
git add .
git commit -m "Description of changes"
```

## License

Use as you wish.
