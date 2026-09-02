#!/usr/bin/env python3
"""Send one line to the main board's console and print what it answers.

    python3 tools/panelcam-console.py /dev/cu.usbserial-10 test 120   # the camera's test screen
    python3 tools/panelcam-console.py /dev/cu.usbserial-10 test off
    python3 tools/panelcam-console.py /dev/cu.usbserial-10 wake
    python3 tools/panelcam-console.py /dev/cu.usbserial-10 status

OPENING THE PORT RESTARTS THE MAIN BOARD. macOS asserts DTR and RTS as it opens
a CH340, whatever pyserial is told to set them to, and that pulse is the Q2/Q3
auto-reset lattice's cue: `status` answers with an uptime of 0 s. A line sent
into the restart arrives with bytes missing — `test 120` once landed as `test`
with nothing after it — so this waits for the banner's last line before it
sends, and for two seconds of silence if no banner comes. The enclosure keeps
its page, and a test screen it is showing, through the restart. Exit 1, saying
so, when there is no board.
"""

import sys
import time

try:
    import serial
except ImportError:
    sys.exit("pyserial not found")

BANNER_END = "type 'help'"


def ask(port, line):
    """The console's reply lines to one command, or None with no board."""
    try:
        s = serial.Serial(port, 115200, timeout=0.05, write_timeout=2)
    except Exception:
        return None
    with s:
        t0 = time.time()
        seen = ""
        quiet_since = t0
        while time.time() - t0 < 6:
            chunk = s.read(4096).decode(errors="replace")
            if chunk:
                seen += chunk
                quiet_since = time.time()
                if BANNER_END in seen:
                    break
            elif time.time() - quiet_since > 2:
                break
        s.reset_input_buffer()
        s.write(("\n" + line + "\n").encode())
        s.flush()
        # `test` waits up to 600 ms for the enclosure's answer before it says anything.
        time.sleep(1.2)
        reply = s.read(8192).decode(errors="replace")
    return [l.strip() for l in reply.splitlines() if l.strip() not in ("", ">", line)]


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("usage: panelcam-console.py <port> <console line…>")
    lines = ask(sys.argv[1], " ".join(sys.argv[2:]))
    if lines is None:
        sys.exit(f"no console on {sys.argv[1]}")
    print("\n".join(lines) if lines else "no answer from the console")
