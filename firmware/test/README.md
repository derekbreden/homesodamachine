# Firmware tests

The native suite holds machine policy that does not need, open, reset, or drive a board:

```bash
pio test -e native
```

`test_machine_policy` checks the canonical V-A–V-K operation plans, the three-valve ceiling,
the dispense/refill exclusion, every possible off-before-on valve-mask transition, and the
prime/timed-pump deadlines shared with the J9 protocol. `test_pcba_expanders` checks the
logical-to-physical valve map, safe MCP23017 initialization, active-low reed decoding,
cross-expander break-before-make writes, and fail-park behavior. They run on the build host
and are safe with every USB device connected.

Board builds remain separate because they compile different source trees:

```bash
pio run -e appliance
pio run -e esp32s3_front
pio run -e esp32s3_faucet
pio run -e pcba_bench
```

Building does not open a serial port. Uploading and monitoring do; name the port whenever
more than one board is connected (`tools/boards.py` prints the exact commands).

With the working controller and front display connected, the default live check only observes
the display, touch controller, and J9 link through the display's native USB port. The optional
checks are deliberately explicit: `--animation` wakes HOME long enough to measure it and
restores the previous page/idle rung; `--prime a|b` actuates that pump for about one second
through the same handlers the glass uses and always posts a stop request.

```bash
~/.platformio/penv/bin/python tools/firmware_live_check.py
~/.platformio/penv/bin/python tools/firmware_live_check.py --animation
~/.platformio/penv/bin/python tools/firmware_live_check.py --prime b
```
