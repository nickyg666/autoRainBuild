# 🚀 Quick Start Guide - autoRain Improvements

## ⚡ In 3 Commands

```bash
# 1. Verify system is ready
/home/orangepi/autoRain/verify-system.sh

# 2. Deploy services
sudo /home/orangepi/autoRain/deploy.sh

# 3. Watch it work!
sudo journalctl -u autorain -f
```

## 📋 What Changed?

### Before
```
autoRain.py → Background Bluetooth thread → Returns immediately
              (audio might not be ready yet)
              ↓
              palera1n starts (speaker might not be connected!)
```

### After
```
autoRain.py → BLOCKS until Bluetooth connected (30s timeout) ✓
              → BLOCKS until audio ready ✓
              → Plays ready.mp3 ✓
              ↓
              palera1n starts (guaranteed working audio!)
```

## 🎯 Key Features Added

✅ **HARD STOP Mode** - Waits for Bluetooth before proceeding  
✅ **Dynamic Audio Detection** - Works on any system  
✅ **Proper Service Setup** - Works at boot  
✅ **Power Event Handling** - Auto-reconnect after sleep  
✅ **Better Logging** - See exactly what's happening  

## 📊 New Files

```
/home/orangepi/autoRain/
├── autoRain.py                          (UPDATED)
├── scripts/
│   ├── autoRain-wait.service           (UPDATED)
│   └── bt-reconnect.sh                 (NEW)
├── power/
│   └── bluetooth-reconnect.service     (NEW)
├── verify-system.sh                     (NEW)
├── deploy.sh                            (NEW)
├── README-UPDATES.md                    (NEW)
├── UPDATES-2026-01-15.md               (NEW)
└── QUICK-START.md                       (NEW - this file)
```

## 🧪 Testing (5 Minutes)

```bash
# 1. Check everything is ready
/home/orangepi/autoRain/verify-system.sh

# 2. Deploy
sudo /home/orangepi/autoRain/deploy.sh

# 3. Reboot and watch
sudo reboot
# Then on another terminal:
sudo journalctl -u autorain -f

# 4. Watch for this in logs:
# [bt] ✓✓✓ SPEAKER CONNECTED SUCCESSFULLY ✓✓✓
# [audio] Playing ready.mp3
```

## 🐛 Troubleshooting (Quick Fixes)

### Service won't start?
```bash
sudo systemctl status autorain
sudo journalctl -u autorain -n 50
```

### No Bluetooth connection?
```bash
# Check Bluetooth status
sudo systemctl status bluetooth
bluetoothctl devices

# Manual test
bluetoothctl connect 11:81:AA:11:88:72
```

### No audio?
```bash
# Test PulseAudio
PULSE_SERVER="unix:/run/user/1000/pulse/native" pactl list short sinks

# Test audio directly
mpg123 /home/orangepi/ready.mp3
```

## 📈 Expected Boot Timeline

```
T=0s    Power on
T=3s    autoRain starts
T=4s    HARD STOP waiting for Bluetooth
T=25s   Bluetooth connected ✓
T=27s   Audio ready, palera1n begins
```

## 🔄 Service Commands

```bash
# Check status
sudo systemctl status autorain

# View logs
sudo journalctl -u autorain -f

# Restart
sudo systemctl restart autorain

# Stop
sudo systemctl stop autorain

# Start
sudo systemctl start autorain
```

## 📚 Full Documentation

For detailed information, see:
- **README-UPDATES.md** - Complete technical guide
- **UPDATES-2026-01-15.md** - Detailed changelog

## ✅ Success Check

Everything is working if:
- ✓ Service starts at boot
- ✓ Bluetooth connects within 30s
- ✓ You hear the "ready" beep
- ✓ palera1n workflow begins
- ✓ Logs show clean status (no errors)

## 💡 Pro Tips

```bash
# Follow logs in real-time during boot
sudo journalctl -u autorain -f --no-pager

# Filter for Bluetooth logs only
grep "\[bt\]" /home/orangepi/autoRain.log | tail -20

# Filter for audio logs only
grep "\[audio\]" /home/orangepi/autoRain.log | tail -20

# Watch service restart (if configured)
sudo journalctl -u autorain -n 0 -f
```

## 🎯 What to Do Next

1. **Deploy:** Run `sudo /home/orangepi/autoRain/deploy.sh`
2. **Test:** Reboot and check logs
3. **Monitor:** Keep an eye on `/home/orangepi/autoRain.log`
4. **Done!** Everything should work automatically

---

**Need help?**
- Check logs: `sudo journalctl -u autorain -f`
- Run verify: `/home/orangepi/autoRain/verify-system.sh`
- Read full docs: `README-UPDATES.md`
