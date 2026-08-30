# Firmware tests

The native suite holds machine policy that does not need, open, reset, or drive a board:

```bash
pio test -e native
```

`test_flavor_selection` checks first-install adoption, established-main-board authority,
absolute/idempotent selection, corrupt storage, and failed-write retry state.
`test_machine_policy` checks the canonical V-A–V-K operation plans, the three-valve ceiling,
the dispense/refill exclusion, every possible off-before-on valve-mask transition, and the
prime/timed-pump deadlines shared with the J9 protocol. `test_pcba_expanders` checks the
logical-to-physical valve map, safe MCP23017 initialization, active-low reed decoding,
cross-expander break-before-make writes, and fail-park behavior. They run on the build host
and are safe with every USB device connected. `test_weld_rotator_policy` checks the purchased
20T:90T drive ratio, speed envelope, exact 380-degree lap count, boot-held pedal lockout,
deadman release, and jog/lap state transitions.

Board builds remain separate because they compile different source trees:

```bash
pio run -e appliance
pio run -e esp32s3_front
pio run -e esp32s3_faucet
pio run -e pcba_bench
pio run -e weld_rotator
```

Building does not open a serial port. Uploading and monitoring do; name the port whenever
more than one board is connected (`tools/boards.py` prints the exact commands).

With the working main board and enclosure display connected, the default live check only observes
the display, touch controller, J9 link, and synchronized/durable flavor state through the
display's native USB port. The optional checks are deliberately explicit: `--animation`
opens the reusable operation lock long enough to measure it; `--toggle` selects the other
flavor, proves main board synchronization and persistence, and restores it; `--prime a|b`
actuates that pump for about one second through the same handlers the glass uses and always
posts a stop request. Each check restores the page, idle rung and lock state it found.

```bash
~/.platformio/penv/bin/python tools/firmware_live_check.py
~/.platformio/penv/bin/python tools/firmware_live_check.py --animation
~/.platformio/penv/bin/python tools/firmware_live_check.py --toggle
~/.platformio/penv/bin/python tools/firmware_live_check.py --prime b
```

With the faucet display connected to J3 and its native USB connected, the faucet check never
drives an actuator. Its default mode proves convergence, both persistence states, request
latency and loop/link-service high-water marks. `--toggle` explicitly selects the other
flavor, waits for both stores, and restores the original selection; the main board makes one
tick for each of those two user-path selections.

```bash
~/.platformio/penv/bin/python tools/firmware_faucet_check.py
~/.platformio/penv/bin/python tools/firmware_faucet_check.py --toggle
```
