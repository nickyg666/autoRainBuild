# System Configuration Changes by OpenCode

## Bluetooth Service Enhancement
**File**: `/etc/systemd/system/bluetooth.service.d/override.conf`
**Purpose**: Fix shutdown hang issue with bluetoothd
**Changes**:
```
[Service]
KillMode=mixed
TimeoutStopSec=10
```
**Rationale**: Bluetooth daemon can hold USB locks and needs graceful shutdown. `KillMode=mixed` allows SIGTERM grace period before SIGKILL. Prevents system hang on reboot/poweroff.

## autorain.service Simplification
**File**: `/etc/systemd/system/autorain.service`
**Changes**:
- Removed tmux wrapper for cleaner process management
- Removed unnecessary ExecStartPost checks
- Simplified PATH (removed .opencode/bin, removed extraneous paths)
- Added proper user environment variables matching system session
- Direct Python execution: `/usr/bin/python3 /home/orangepi/autoRain/autoRain.py`

**Before**: Used tmux to create persistent session
**After**: Direct execution allows proper systemd cleanup and process supervision

## User Group Memberships
**orangepi user additions**:
- ✅ usbmuxd group (newly created GID 1003) - for iOS USB device communication
- ✅ bluetooth group (existing) - for bluetoothctl commands
- ✅ gpio group (existing) - for GPIO control via gpioset

## Binary Capabilities
**File**: `/usr/local/bin/palera1n`
**Changes**: Added Linux capabilities
```bash
setcap cap_sys_admin,cap_sys_ptrace,cap_sys_module=eip /usr/local/bin/palera1n
```
**Result**: palera1n now executable without sudo (retains root-equivalent abilities via capabilities)

## Files Modified in Repository
**autoRain/**: NO PERSISTENT CHANGES - reverted all Python/service file modifications
- Reason: autoRain.py modifications introduced bluetooth_manager.py which caused stability issues
- Current state: Repository is at last known-good commit (0624947)

## Documentation Created
**New Files in autoRain/**:
- `BLUETOOTH_SETUP.md` - Comprehensive Bluetooth configuration guide
- `SYSTEM_CHANGES.md` - This file, documenting system-level changes

## System-Level Files (Outside Repository)
**Should not be in repo** - These are system configuration files:
- `/etc/systemd/system/autorain.service` - system service definition
- `/etc/systemd/system/bluetooth.service.d/override.conf` - systemd override
- Group memberships in `/etc/group` and `/etc/gshadow`
- Binary capabilities via setcap

**Note**: The repository should document these but not track them.

