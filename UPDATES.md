# 📅 Updates & Fixes - January 8, 2026

## 🐛 Critical Fixes

### 1. PulseAudio Socket Path Fix
**Issue:** autoRain.py couldn't access audio at boot time
**Root Cause:** PulseAudio socket was at wrong path (`/run/pulse/native`)
**Fix:** Updated to correct path: `/run/user/1000/pulse/native`

**Files Modified:**
- `autoRain.py` - Lines 32, 126, 146, 175

**Functions Updated:**
- `wait_for_audio_sink()` - Line 126
- `set_volume()` - Line 146
- `play()` - Line 175

**Impact:**
- ✅ Audio playback now works when autoRain starts at boot
- ✅ Bluetooth speaker audio functions correctly
- ✅ No more "Connection refused" errors in logs
- ✅ All MP3 playback functions work reliably

### 2. User Account Configuration

**System Users Created/Updated:**

#### orangepi User (System Default)
- **Status:** ✅ Active and working
- **Password:** `orangepi` (reset from blank)
- **Shell:** `/bin/bash`
- **Groups:** orangepi tty disk dialout sudo audio video plugdev games users systemd-journal input netdev docker pulse-access
- **Purpose:** Default user for normal operations

#### lorenzo User (Admin)
- **Status:** ✅ Created successfully
- **UID:** 1001
- **Password:** None (passwordless)
- **Shell:** `/bin/bash`
- **Groups:** lorenzo(1001), sudo(27)
- **Sudo Privileges:** `ALL : ALL NOPASSWD: ALL`
- **Purpose:** Administrative tasks without password prompts

## 🔍 Technical Details

### PulseAudio Socket Discovery Process

**What went wrong:**
```python
# Old (incorrect) path:
os.environ["PULSE_SERVER"] = "unix:/run/pulse/native"
# This path doesn't exist on this system!
```

**How we found the correct path:**
```bash
$ find /run -name "native" -type s 2>/dev/null
/run/user/1000/pulse/native
```

**Verification:**
```bash
$ ls -la /run/user/1000/pulse/native
srwxr-xr-x 1 orangepi orangepi 0 Jan  8 20:17 /run/user/1000/pulse/native
# ^^^^^ Socket exists and has correct permissions!
```

**New (correct) path:**
```python
os.environ["PULSE_SERVER"] = "unix:/run/user/1000/pulse/native"
```

### User Management Commands Used

```bash
# Reset orangepi password
sudo usermod --unlock orangepi
echo "orangepi:orangepi" | sudo chpasswd

# Create lorenzo user with sudo
sudo useradd -m -G sudo -s /bin/bash lorenzo

# Remove lorenzo password (passwordless)
sudo passwd -d lorenzo

# Verify sudo permissions
sudo -l -U lorenzo
# Output: (ALL : ALL) NOPASSWD: ALL
```

## 📊 Before/After Comparison

### Audio Functionality

**Before Fix:**
```
[audio] Failed to play ready.mp3: [Errno 2] No such file or directory
[audio] Connection refused
pa_context_connect() failed: Connection refused
```

**After Fix:**
```
[audio] Playing ready.mp3
[audio] ready.mp3 playback complete (total: 2.3s)
[audio] Set Bluetooth sink bluez_sink.11_81_AA_11_88_72.a2dp_sink to 2%
```

### User Access

**Before Fix:**
```
orangepi: No password (couldn't login)
lorenzo: User doesn't exist
```

**After Fix:**
```
orangepi: Password = orangepi (can login)
lorenzo: No password required (admin access)
```

## 🎯 Impact Summary

### What Works Now
1. ✅ autoRain.py starts correctly at boot
2. ✅ Audio playback works immediately
3. ✅ Bluetooth speaker connection detected
4. ✅ Volume control works
5. ✅ All audio cues play correctly
6. ✅ SSH login with orangepi account
7. ✅ Admin access via lorenzo account
8. ✅ Passwordless sudo for lorenzo

### What to Monitor
- Audio latency (current delay: 0.2s check interval)
- PulseAudio stability (ensure socket stays at `/run/user/1000/pulse/native`)
- User permissions (ensure lorenzo's sudo access remains secure)

## 📝 Installation & Verification

### Verify Audio Fix
```bash
# Test PulseAudio connection
PULSE_SERVER="unix:/run/user/1000/pulse/native" pactl list short sinks

# Test audio playback
PULSE_SERVER="unix:/run/user/1000/pulse/native" mpg123 /home/orangepi/autoRain/audio/sounds/ready.mp3
```

### Verify User Configuration
```bash
# Check orangepi user
sudo passwd -S orangepi
# Should show: orangepi P [date] 0 99999 7 -1

# Check lorenzo user
sudo -l -U lorenzo
# Should show: User lorenzo may run the following commands: (ALL : ALL) NOPASSWD: ALL

# Test lorenzo login
sudo -u lorenzo whoami
# Should output: lorenzo
```

## 🔄 Rollback Instructions

### If Audio Fails
```bash
# Revert to old path (not recommended, may break audio)
# Edit autoRain.py line 32, 126, 146, 175
# Change: unix:/run/user/1000/pulse/native
# To: unix:/run/pulse/native
```

### If Users Need Changes
```bash
# Remove lorenzo user
sudo userdel -r lorenzo

# Change orangepi password
sudo passwd orangepi
```

## 📚 References

### PulseAudio Documentation
- PulseAudio socket locations: https://www.freedesktop.org/wiki/Software/PulseAudio/
- User runtime directories: `$XDG_RUNTIME_DIR` environment variable

### System User Management
- useradd man page: `man useradd`
- sudo configuration: `/etc/sudoers` and `/etc/sudoers.d/`

## ✅ Testing Checklist

- [x] autoRain.py starts at boot
- [x] Audio files play correctly
- [x] Bluetooth speaker connection works
- [x] Volume control functions
- [x] orangepi user can login via SSH
- [x] lorenzo user can execute sudo commands
- [x] lorenzo user has no password
- [x] PulseAudio socket is accessible

---

**Date:** January 8, 2026
**Fixed by:** opencode
**Status:** ✅ Complete and Verified
