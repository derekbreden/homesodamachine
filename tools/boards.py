#!/usr/bin/env python3
"""Which board is on which port, and what to do when one is missing.

Enumeration only — this never OPENS a port. Opening one toggles DTR/RTS, which
on the main board drives the Q2/Q3 auto-reset lattice and reboots it; a tool you
run to find out what is plugged in should not restart what is plugged in.

    tools/boards.py

Run it with any Python that has pyserial — the PlatformIO venv always does:

    ~/.platformio/penv/bin/python tools/boards.py
"""

import sys

try:
    from serial.tools import list_ports
except ImportError:
    sys.exit("pyserial not found — try ~/.platformio/penv/bin/python tools/boards.py")

# USB IDs, as the hosts report them.
CH340    = (0x1A86, 0x7523)   # the main board's own CH340C at J14
ESP32_S3 = (0x303A, 0x1001)   # any ESP32-S3's native USB JTAG/serial

S3_ENVS = [
    ("esp32s3_front",  "4.3B enclosure display"),
    ("esp32s3_faucet", '1.47" faucet display'),
    ("esp32s3_config", '1.28" round rotary display'),
]

# Every S3 reports the same VID:PID, but each reports its own MAC as the USB
# serial number — so a board that has been seen once can be named on sight,
# without opening its port or asking it anything.
#
# Add a board with `tools/boards.py --learn <env>` while it is the only S3 on
# USB. An unlisted S3 is still reported, just unnamed: the list is a
# convenience, and nothing depends on a board being in it.
S3_MACS = {
    "44:1B:F6:86:15:98": "esp32s3_faucet",
    "E8:F6:0A:8E:8B:C8": "esp32s3_front",
}


def main():
    ports = sorted(list_ports.comports(), key=lambda p: p.device)
    pcba = [p for p in ports if (p.vid, p.pid) == CH340]
    s3   = [p for p in ports if (p.vid, p.pid) == ESP32_S3]

    print()
    if pcba:
        for p in pcba:
            print(f"  main board        {p.device}   (CH340C at J14)")
    else:
        print("  main board        NOT FOUND")

    if s3:
        for p in s3:
            env = S3_MACS.get((p.serial_number or "").upper())
            what = dict(S3_ENVS).get(env, "")
            if env:
                print(f"  {what:<17s} {p.device}   (native USB, {p.serial_number})")
            else:
                print(f"  ESP32-S3 board    {p.device}   (native USB, {p.serial_number}"
                      f" — unknown, see S3_MACS)")
    else:
        print("  ESP32-S3 board    NOT FOUND")
    print()

    if pcba and not s3:
        # J9 carries V12 to the display alongside the A/B pair. A current display
        # image can detach its USB PHY without dropping that unswitched rail.
        print("  Ask the externally-powered enclosure display to reattach its USB PHY:")
        print()
        print("    ~/.platformio/penv/bin/python tools/display_usb.py")
        print()
        print("  This is an explicit development command; it never runs at production boot")
        print("  and does not switch the 12 V rail or any load.")
        print()
        print("  If it reports UNREACHABLE, this display image is too old or is not answering")
        print("  on J9. That one boot still needs a physical display reset or V12 power cycle.")
        print("  J9 is [B, A, GND, V12] — the display is fed 12 V from the main board over")
        print("  the same connector as the pair, and J9.V12 runs straight to the V12 island")
        print("  with no relay in it, so firmware cannot remove display power.")
        print()

    if not pcba and not s3:
        print("  Nothing here. The main board needs 12 V at J10 before its CH340C")
        print("  enumerates — USB VBUS powers nothing on it.")
        print()

    if pcba:
        print("  Flash the main board:")
        print(f"    PLATFORMIO_UPLOAD_PORT={pcba[0].device} pio run -e appliance -t upload")
        print(f"    PLATFORMIO_UPLOAD_PORT={pcba[0].device} pio run -e pcba_bench -t upload")
        print()
    if s3:
        known = S3_MACS.get((s3[0].serial_number or "").upper())
        if known:
            print(f"  Flash the S3 on {s3[0].device} — its MAC names it:")
            print(f"    PLATFORMIO_UPLOAD_PORT={s3[0].device} pio run -e {known} -t upload"
                  f"   # {dict(S3_ENVS)[known]}")
        else:
            print(f"  Flash the S3 on {s3[0].device} — pick the env for the board you plugged in:")
            for env, what in S3_ENVS:
                print(f"    PLATFORMIO_UPLOAD_PORT={s3[0].device} pio run -e {env} -t upload"
                      f"   # {what}")
        print()
        print("  A board held into ROM download mode stays there until a plain RESET —")
        print("  esptool's own reset does not reach EN over native USB. A flash that")
        print("  verifies and then never reappears on its link is usually just that.")
        print()

    if pcba and s3:
        print("  ALWAYS name the port with both on USB. PlatformIO picks the S3 otherwise,")
        print("  and esptool drops that panel into download mode before failing on the chip")
        print("  id — leaving it dark until it is reflashed.")
        print()


def learn(env: str) -> int:
    s3 = [p for p in list_ports.comports() if (p.vid, p.pid) == ESP32_S3]
    if len(s3) != 1:
        print(f"need exactly one S3 on USB to learn it; found {len(s3)}")
        return 1
    mac = (s3[0].serial_number or "").upper()
    if not mac:
        print("that S3 reports no serial number, so there is nothing to record")
        return 1
    print(f'add to S3_MACS in {__file__}:\n\n    "{mac}": "{env}",\n')
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--learn":
        sys.exit(learn(sys.argv[2]))
    if len(sys.argv) > 1:
        sys.exit("usage: boards.py [--learn <env>]")
    main()
