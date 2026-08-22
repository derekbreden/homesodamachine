# The faucet display

The Waveshare ESP32-S3-Touch-LCD-1.47 in the dispense head. Its 172×320 logo is the
glass-facing flavor selector, and its P1 GPIO43 TX / GPIO44 RX pins cross to the controller
PCBA's J3 IO35 RX / IO33 TX pins at 115200 baud.

## Interaction contract

A bright-screen touch-down changes the logo immediately. The handler only updates LVGL state
and appends a small fixed-memory intent; UART framing, acknowledgement and both flash writes
run later from `loop()`. The normal full-screen redraw remains about 40 ms. After 60 seconds
without input the backlight fades to duty 8, and the first touch at that level is consumed by
the wake: it sends no flavor request and does not dirty either store.

The controller's buzzer makes the tick after the absolute selection reaches J3. A fresh tap
carries the audible flag; retries reuse the same token, so a lost response cannot make a
second tick. An offline or sufficiently delayed selection reconciles silently rather than
playing feedback detached from the touch that caused it.

A different controller selection, including one made on the enclosure display, changes the
logo and wakes the backlight. Re-publication of the flavor already shown is a no-op and does
not disturb idle behavior.

## State and persistence

The controller owns flavor truth. This display keeps a cache only so boot can draw the last
logo without waiting for another board. On connection it sends one of two messages:

- `MSG_FLAVOR_SYNC` offers the cached value. Only a controller with no valid stored selection
  adopts it; an established controller answers with its own value.
- `MSG_FLAVOR_SELECT` carries the absolute result of a local touch or USB selection. Requests
  are tokenized and retried idempotently until the controller answers.

Controller persistence is acknowledged separately from selection acceptance. The controller
writes after 500 ms in a quiet idle loop; this display writes its cache after two seconds of
flavor quiet. Failed writes remain pending and are reported in diagnostics. Reconnect sends
the final desired absolute selection, not a backlog of toggles. Until the controller reports
that selection durable, it remains unfinished faucet input and is reasserted after a reconnect;
that pending user input therefore takes precedence over a development-console edit made while
J3 is disconnected.

## USB diagnostics

The native USB console is 115200 baud:

| Command | Result |
|---|---|
| `GET_VERSION` | build identity |
| `GET_STATE` | local/controller flavor, sync, pending and persistence state |
| `GET_DIAG` | touch/UI high-water marks plus J3 frames, retries, queue drops and ack latency |
| `TOGGLE` | exercise the local-first user path |
| `FLAVOR:0` / `FLAVOR:1` | select an absolute flavor through the same path |
| `BL:n` | development-only raw backlight duty |

The safe live check observes this data without opening the controller's reset-capable CH340C
port or driving any load:

```bash
~/.platformio/penv/bin/python tools/firmware_faucet_check.py
```

`--toggle` changes the flavor once, proves controller and cache persistence, and restores the
selection in a `finally` block. It does not run a pump or valve; two controller ticks are the
expected audible result.

Build and flash with an explicit port whenever another board is attached:

```bash
pio run -e esp32s3_faucet
PLATFORMIO_UPLOAD_PORT=/dev/cu.usbmodem... pio run -e esp32s3_faucet -t upload
```
