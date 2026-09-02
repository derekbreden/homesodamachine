#!/usr/bin/env python3
"""Report a finger to the main board, so both glasses are lit when the shutter opens.

The enclosure panel goes dark 60 s after the last touch and neither display runs a
timer of its own, so an unattended photograph of it is a photograph of an unlit
rectangle. `wake` on the appliance console takes the same entry a reported touch
takes; idleService() publishes the change to both glasses on its next pass.

    python3 tools/panelcam-wake.py /dev/cu.usbserial-10

Silent and exit 0 when there is nothing to talk to: a target with no machine
attached should still take its picture. The console is reached the way
panelcam-console.py reaches it, restart and all.
"""

import importlib.util
import os
import sys

port = sys.argv[1] if len(sys.argv) > 1 else "/dev/cu.usbserial-10"
spec = importlib.util.spec_from_file_location(
    "panelcam_console", os.path.join(os.path.dirname(os.path.abspath(__file__)), "panelcam-console.py"))
console = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(console)
except SystemExit:
    sys.exit(0)   # no pyserial: nothing to talk to
reply = console.ask(port, "wake")
if reply is None:
    sys.exit(0)
print("awake" if any("idle" in l for l in reply) else "no answer from the console")
