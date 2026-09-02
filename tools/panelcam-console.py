#!/usr/bin/env python3
"""Send one line to the main board's console and print what it answers.

    python3 tools/panelcam-console.py /dev/cu.usbserial-10 test 120   # the camera's test screen
    python3 tools/panelcam-console.py /dev/cu.usbserial-10 test off
    python3 tools/panelcam-console.py /dev/cu.usbserial-10 status

OPENING THE PORT RESTARTS THE MAIN BOARD. macOS asserts DTR and RTS as it opens
a CH340, whatever pyserial is told to set them to, and that pulse is the Q2/Q3
auto-reset lattice's cue: `status` answers with an uptime of 0 s. The command
still lands, in the UART's buffer, and the restarted board answers it; the
enclosure display keeps its page, and a test screen it is showing, through
the restart. Exit 1, saying so, when there is no board.
"""

import sys
import time

try:
    import serial
except ImportError:
    sys.exit("pyserial not found")

if len(sys.argv) < 3:
    sys.exit("usage: panelcam-console.py <port> <console line…>")
port, line = sys.argv[1], " ".join(sys.argv[2:])

try:
    s = serial.Serial()
    s.port = port
    s.baudrate = 115200
    s.timeout = 0.05
    s.write_timeout = 2
    s.open()
except Exception as e:
    sys.exit(f"no console on {port}: {e}")

with s:
    time.sleep(0.3)
    s.reset_input_buffer()
    s.write(("\n" + line + "\n").encode())
    s.flush()
    # `test` waits up to 600 ms for the enclosure's answer before it says anything.
    time.sleep(1.2)
    reply = s.read(8192).decode(errors="replace")

lines = [l.strip() for l in reply.splitlines() if l.strip() and l.strip() != line]
print("\n".join(lines) if lines else "no answer from the console")
