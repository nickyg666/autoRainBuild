# Speaker Power on Reboot/Poweroff

Toggles speaker power during shutdown/reboot events via GPIO 79 momentary button.

## Files

- `/home/orangepi/autoRain/scripts/shutdown-speaker-power.sh` - Shutdown script
- `/etc/systemd/system/shutdown-speaker-power.service` - Shutdown trigger
- `/home/orangepi/autoRain/scripts/bluetooth-boot.sh` - Boot connection script
- `/etc/systemd/system/bluetooth-boot.service` - Boot trigger

## How It Works

1. **On Shutdown:** `shutdown-speaker-power.service` runs before system halt
   - Presses GPIO 79 for 3 seconds
   - Releases to toggle speaker power
   - Marks timestamp in `/tmp/speaker-power-event`

2. **On Boot:** `bluetooth-boot.service` runs after Bluetooth/PulseAudio
   - Checks for recent power event
   - Waits up to 15 seconds for speaker to stabilize
   - Prevents Bluetooth reconnect spam
   - Runs in exact manual TTY environment

## Services

```bash
systemctl status shutdown-speaker-power.service
systemctl status bluetooth-boot.service
```

## Logs

```bash
tail -f /home/orangepi/autoRain.log
journalctl -u shutdown-speaker-power.service -f
journalctl -u bluetooth-boot.service -f
```
