#!/usr/bin/env python3
"""Report a finger to the main board, so both glasses are lit when the shutter opens.

The enclosure panel goes dark 60 s after the last touch and neither display runs a
timer of its own, so an unattended photograph of it is a photograph of an unlit
rectangle. `wake` on the appliance console takes the same entry a reported touch
takes; idleService() publishes the change to both glasses on its next pass.

    python3 tools/panelcam-wake.py /dev/cu.usbserial-10

Silent and exit 0 when there is nothing to talk to: a target with no machine
attached should still take its picture.
"""

import sys
import time

try:
    import serial
except ImportError:
    sys.exit(0)

port = sys.argv[1] if len(sys.argv) > 1 else "/dev/cu.usbserial-10"

try:
    s = serial.Serial()
    s.port = port
    s.baudrate = 115200
    s.timeout = 0.05
    s.write_timeout = 2
    # Opening a CH340 on macOS asserts DTR and RTS whatever they were set to, and that
    # restarts the main board through Q2/Q3. The command waits in the UART's buffer and
    # the restarted board answers it; both glasses keep their pages through the restart.
    s.open()
except Exception:
    sys.exit(0)

with s:
    time.sleep(0.3)
    s.reset_input_buffer()
    s.write(b"\nwake\n")
    s.flush()
    time.sleep(0.5)
    reply = s.read(4096).decode(errors="replace")

print("awake" if "idle" in reply else "no answer from the console")
