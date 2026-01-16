# Bluetooth Speaker Setup & Configuration

**WORKING BLUEPRINT:** See `fast-bt.sh` for the canonical implementation.

## Hardware & Boot Sequence

### GPIO Speaker Power Button (GPIO 79)
- **Press** (LOW=0): Hold for 3 seconds to power toggle speaker
- **Release** (HIGH=1): Set to 1 after holding to complete toggle
- **Timing**: 3-second hold is critical for reliable speaker boot

```bash
# Power cycle speaker
gpioset gpiochip1 79=0   # Press
sleep 3
gpioset gpiochip1 79=1   # Release
sleep 2                  # Wait for speaker to stabilize
```

### Bluetooth Initialization Sequence

1. **Power Cycle Speaker** (GPIO 79, 3-second hold)
2. **Power On BT Controller**: `bluetoothctl power on`
3. **Enable Discoverable Mode**: `bluetoothctl discoverable on`
4. **Pair Device**: `bluetoothctl pair 11:81:AA:11:88:72`
5. **Connect Device**: `bluetoothctl connect 11:81:AA:11:88:72`

**Key Device MAC**: `11:81:AA:11:88:72`

## System Components

### User Groups (for sudoless access)
- **gpio group**: For GPIO control via gpioset (✅ orangepi is member)
- **bluetooth group**: For bluetoothctl access (✅ orangepi is member)
- **usbmuxd group**: For iOS device communication (✅ orangepi is member)

### Services
- **bluetooth.service**: Core Bluetooth daemon
  - Override file: `/etc/systemd/system/bluetooth.service.d/override.conf`
  - Settings: `KillMode=mixed`, `TimeoutStopSec=10`
  - Issue: Can hang on shutdown if not configured properly

### PulseAudio
- **User service** (systemd --user)
- **Socket**: `/run/user/1000/pulse/native`
- **D-Bus Session**: `/run/user/1000/bus`

### Device Communication
- **usbmuxd**: Manages USB connections to iOS devices
  - Requires root access OR usbmuxd group membership
  - Socket: `/var/run/usbmuxd`

## Configuration

### Systemd Service (autorain.service)
- **User**: orangepi
- **Environment**: XDG_RUNTIME_DIR, PULSE_SERVER, DBUS_SESSION_BUS_ADDRESS
- **PreStart**: Restarts Bluetooth service
- **Execution**: Direct Python (no tmux wrapper)

### Fast Setup (Working Method - fast-bt.sh)
```bash
#!/bin/bash
# Power cycle speaker
sudo gpioset gpiochip1 79=0
sleep 3
sudo gpioset gpiochip1 79=1
sleep 2

# BT operations (requires bluetoothctl)
sudo bluetoothctl power on
sudo bluetoothctl discoverable on
sudo bluetoothctl pair 11*          # Partial MAC matching
sudo bluetoothctl connect 11*
```

## Troubleshooting

### "No default controller available"
- **Cause**: bluetoothd not properly initialized or D-Bus connection issue
- **Fix**: Restart Bluetooth service and wait for hci0 to appear
```bash
sudo systemctl restart bluetooth
sleep 2
hciconfig  # Should show hci0 UP RUNNING
```

### Shutdown Hang
- **Cause**: Bluetooth process stuck in D state (disk sleep)
- **Fix**: Already configured in override.conf with `KillMode=mixed`

### Bluetooth Hardware Not Detected
- **Check**: `hciconfig` should show hci0
- **Check**: `rfkill list` should show bluetooth not hard/soft blocked
- **Check**: Kernel logs for Bluetooth errors: `dmesg | grep -i bluetooth`

## Known Issues

### Kernel Stability
- Orange Pi Zero 2 Bluetooth driver can panic under high load
- Observed: "Opcode 0x408 failed: -107" in dmesg
- Workaround: Keep Bluetooth operations simple and direct

### Device Pairing
- Speaker MAC: `11:81:AA:11:88:72` - device-specific
- Pairing is persistent after first successful pair
- Subsequent connections only need `bluetoothctl connect MAC`

## Implementation Notes

### Why Not Use Managers?
Previous attempts with bluetooth_manager.py and complex connection workflows caused:
- Unnecessary D-Bus complexity
- Timeout issues
- Blocking operations

The simple sequential approach in fast-bt.sh is more reliable because:
- Clear state transitions
- Explicit wait times match hardware requirements
- Easier to debug when issues occur
- Minimal dependencies (just bluetoothctl)

### Audio System Integration
- **PulseAudio**: Runs as user service (systemd --user)
- **Output**: Bluetooth speaker is default sink
- **Volume Control**: Use `pactl set-sink-volume @DEFAULT_SINK@ 2%`
- **Socket**: Always use `unix:/run/user/1000/pulse/native` for user context

## References

- **Kernel Module**: bluetooth (v2.22 on this system)
- **Daemon**: bluetoothd (BlueZ 5.66)
- **Control**: bluetoothctl
- **Hardware Check**: hciconfig, hcitool
- **Process Monitoring**: hciattach (UART attachment at 1500000 baud)
