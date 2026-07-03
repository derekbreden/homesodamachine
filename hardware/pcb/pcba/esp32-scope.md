# ESP32 — what the base controller uses

Board `esp32dev` (ESP32-WROOM-32E), firmware `firmware/src/main.cpp`. A wired GPIO +
UART hub:

- No WiFi, no BLE — the base firmware links no radio. BLE is on the separate ESP32-S3
  config display (`firmware/src_config`); the faucet display is another S3. The base
  ESP32 reaches both over wired UART (RS485 to the config display, TTL UART to the
  faucet).
- Flashed over serial (`pio run -e esp32dev -t upload`): UART0 + EN/IO0.

## Connected pins (`mini.tsx`)

Pins are assigned by which WROOM edge faces their connector — north-edge GPIO feed the
top connectors, south-edge GPIO the bottom — so each connector's traces comb straight to
its pins instead of crossing the fan.

- I²C: IO21 (SDA), IO22 (SCL)
- UART → RS485 config display: IO32 (TX), IO34 (RX, input-only) — south edge
- UART → faucet display: IO33 (TX), IO35 (RX, input-only) — south edge
- Pumps → on-board DRV8870 H-bridges: IO18→A.IN2, IO17→A.IN1, IO16→B.IN2, IO4→B.IN1 — north edge, one bus, ordered west-to-east so the four IN traces comb up with no crossing (IN1/IN2 only set H-bridge polarity; firmware picks the forward sense)
- Relays (off-board modules) → IO23, IO19 — north edge
- Sensors: IO26 (1-wire, 4.7k external pull-up to 3V3 — R9), IO25 (flow), IO27 (backflow) — three adjacent south-edge pins
- Status LEDs: IO14 (red/fault), IO2 (green/ready), IO12 (blue/activity) — on-board, active-high to GND, boot-safe
- Gas dividers: IO39 (AOUT), IO36 (DOUT) — south-edge ADC1, input-only
- Buzzer: IO13 (the lone usable east-edge GPIO, not a strapping pin → silent at boot)
- Power / reset: 3V3, V5, GND, EN

Programming: TX0 (IO1), RX0 (IO3), IO0, EN — to the on-board USB-C block. Unconnected:
IO5, IO15. IO6–IO11 are the module's internal flash.

## SMD block

WROOM-32E + per-VDD 0.1 µF + 10 µF bulk; EN 10k + 1 µF; IO0 10k pull-up. 3V3 from the
on-board AMS1117-3.3 LDO (U9), fed off the 5 V rail (the K7805 12 V→5 V buck).

## USB-C programming block

Flashed over a plain USB-C cable — J14 (USB-C receptacle, north edge above the WROOM,
opening flush to the board edge) + U13 (CH340C USB-UART bridge). Data only: the bridge runs off the board 3V3 (the board is
12 V-powered), USB VBUS powers nothing. CC1/CC2 carry 5.1k Rd (R15/R16); U14 (USBLC6)
clamps D+/D-. Auto-reset is the classic cross-coupled NPN pair off DTR/RTS — Q2 pulls EN,
Q3 pulls IO0 — so esptool resets + enters download mode with no key press; BOOT (SW1) and
RESET (SW2) tacts are the manual overrides. The EN RC (R7/C12) and IO0 pull-up (R8) are
the pull sides.

Strapping pins:
- IO0 — pull-up + BOOT button + auto-reset (boot select)
- IO5 — unconnected; high at boot
- IO15 — unconnected; high at boot
- IO2, IO12 — status-LED outputs; low / floating at boot

Radio unused; the WROOM antenna keepout stays.
