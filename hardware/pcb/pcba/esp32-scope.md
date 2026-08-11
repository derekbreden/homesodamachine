# ESP32 — what the base controller uses

Board `esp32dev` (ESP32-WROOM-32E), firmware `firmware/src/main.cpp`. A wired GPIO +
UART hub:

- No WiFi, no BLE — the base firmware links no radio. BLE is on the separate ESP32-S3
  config display (`firmware/src_config`); the faucet display is another S3. The base
  ESP32 reaches both over wired UART (RS485 to the config display, TTL UART to the
  faucet).
- Flashed over serial (`pio run -e esp32dev -t upload`): UART0 + EN/IO0.

## Connected pins (`pcba.tsx`)

Pins are assigned by which WROOM edge faces their connector — north-edge GPIO feed the
top connectors, south-edge GPIO the bottom — so each connector's traces comb straight to
its pins instead of crossing the fan.

- I²C: IO21 (SDA), IO22 (SCL) — 4.7k pull-ups to 3V3 on-board (R19/R20); bus serves the two
  MCP23017s and the DS3231, and breaks out at the I2C header (J8)
- UART → RS485 config display: IO32 (TX), IO34 (RX, input-only) — south edge
- UART → faucet display: IO33 (TX), IO35 (RX, input-only) — south edge
- Pumps → on-board DRV8870 H-bridges, single-direction drive: IO17→A.IN1, IO4→B.IN1 (each IN2 is tied to the GND plane, so each bridge drives one way or coasts; IO16/IO18 are the reserved IN2 feeds a reversing respin takes)
- Relays (off-board modules) → IO2, IO19 — IO19 (the compressor relay) does not reach J5 directly: it feeds U15 (74LVC1G08 AND gate), whose other input is the divided MQ-6 DOUT, so a hardware gas trip cuts the compressor regardless of firmware (interlock detail in the `pcba.tsx` GAS block; IO2 is boot-safe into an opto input: the module's LED load holds it low, which download mode also wants)
- Sensors: IO26 (1-wire, 4.7k external pull-up to 3V3 — R9; two probes on the one bus, told apart by family code — DS18B20 `0x28` = tank-wall / compressor setpoint, DS18S20 `0x10` = evaporator-coil / freeze-protect cutout), IO25 (flow), IO27 (backflow signal) — three adjacent south-edge pins — plus IO23 (north edge): the moisture module's switched VCC, driven only while sampling so the drip-pan electrodes sit unpowered between samples
- Status LEDs: IO15 (red/fault), IO12 (green/ready), IO14 (blue/activity) — on-board. IO12/IO14 are active-high to GND; **IO15 is active-low**, hanging off 3V3 through its LED, so the pin idles pulled up and firmware lights it by driving LOW
- Gas dividers: IO39 (AOUT), IO36 (DOUT) — south-edge ADC1, input-only; the divided DOUT node (R3/R4) also feeds the firmware-independent U15 compressor interlock through R25 (0Ω invert-select)
- Buzzer: IO13 (the lone usable east-edge GPIO, not a strapping pin → silent at boot)
- Power / reset: 3V3, V5, GND, EN

Programming: TX0 (IO1), RX0 (IO3), IO0, EN — to the on-board USB-C block. Unconnected:
IO5, IO16, IO18. IO6–IO11 are the module's internal flash.

## SMD block

WROOM-32E + per-VDD 0.1 µF + 10 µF bulk; EN 10k + 1 µF; IO0 10k pull-up. 3V3 from the
on-board AMS1117-3.3 LDO (U9), fed off the 5 V rail (the K7805 12 V→5 V buck).

## USB-C programming block

Flashed over a plain USB-C cable — J14 (USB-C receptacle above the WROOM, opening
flush to the west board edge) + U13 (CH340B USB-UART bridge). Data only: the bridge runs off the board 3V3 (the board is
12 V-powered), USB VBUS powers nothing. CC1/CC2 carry 5.1k Rd (R15/R16); U14 (USBLC6)
clamps D+/D-. Auto-reset is the classic cross-coupled NPN pair off DTR/RTS — Q2 pulls EN,
Q3 pulls IO0 — so esptool resets + enters download mode with no key press; BOOT (SW1) and
RESET (SW2) tacts are the manual overrides. The EN RC (R7/C12) and IO0 pull-up (R8) are
the pull sides.

Strapping pins:
- IO0 — pull-up + BOOT button + auto-reset (boot select)
- IO5 — unconnected; high at boot
- IO15 — MTDO, which gates the ROM boot log on U0TXD. The red status LED pulls up to 3V3 through it, so the pin sits at 3V3 at reset and the boot log prints; a LED to GND here would clamp the pin to ~1.6 V (under the ~2.5 V V_IH) and silence the ROM permanently
- IO2 — relay drive; the opto module's input load holds it low at boot (download-safe)
- IO12 — green status LED; low / floating at boot

Radio unused; the WROOM antenna keepout stays.
