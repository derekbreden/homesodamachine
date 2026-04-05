---
name: Use pyserial directly instead of pio device monitor
description: pio device monitor requires a real tty and fails in Claude Code — use pyserial directly to read/write serial
type: feedback
---

`pio device monitor` fails in Claude Code with `termios.error: (19, 'Operation not supported by device')` because PlatformIO's miniterm requires a real terminal (tty), which this environment doesn't have.

**Instead, use pyserial directly:**

```python
python3 -c "
import serial, time
ser = serial.Serial('/dev/cu.usbserial-10', 115200, timeout=2, dsrdtr=False, rtscts=False)
ser.reset_input_buffer()
# To reset the ESP32:
ser.rts = True; time.sleep(0.1); ser.rts = False
time.sleep(0.2); ser.reset_input_buffer()
# Read output:
start = time.time()
while time.time() - start < 15:
    data = ser.read(1024)
    if data:
        print(data.decode('utf-8', errors='replace'), end='', flush=True)
ser.close()
"
```

**To send commands (e.g. GET_CONFIG):**
```python
ser.write(b'GET_CONFIG\r\n')
ser.flush()
```

**Port names:** ESP32 is typically `/dev/cu.usbserial-*`, S3 and RP2040 are `/dev/cu.usbmodem*`. Check with `ls /dev/cu.usb*`.
