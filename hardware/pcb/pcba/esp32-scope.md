# ESP32 — what the base controller uses

Board `esp32dev` (ESP32-WROOM-32E), firmware `firmware/src/main.cpp`. A wired GPIO +
UART hub:

- No WiFi, no BLE — the base firmware links no radio. BLE is on the separate ESP32-S3
  config display (`firmware/src_config`); the faucet display is another S3. The base
  ESP32 reaches both over wired UART (RS485 to the config display, TTL UART to the
  faucet).
- Flashed over serial (`pio run -e esp32dev -t upload`): UART0 + EN/IO0.

## Connected pins (`mini.tsx`)

- I²C: IO21 (SDA), IO22 (SCL)
- UART → RS485 config display: IO32 (TX), IO34 (RX)
- UART → faucet display: IO33 (TX), IO35 (RX)
- Pumps → on-board DRV8870 H-bridges: IO27/IO25 (pump A IN1/IN2), IO19/IO18 (pump B IN1/IN2)
- Relays (off-board modules) → IO17, IO16. IO26/IO5 are spare (were the L298N's 3rd pump lines)
- Sensors: IO14 (1-wire), IO15 (flow), IO13 (backflow)
- Gas dividers: IO39 (AOUT), IO36 (DOUT)
- Buzzer: IO4
- Power / reset: 3V3, V5, GND, EN

Programming: TX0 (IO1), RX0 (IO3), IO0, EN. Unconnected: IO23, IO2, IO12. IO6–IO11 are
the module's internal flash.

## SMD block

WROOM-32E + per-VDD 0.1 µF + 10 µF bulk; EN 10k + 1 µF; IO0 10k pull-up; 6-pin serial
header (TX0 / RX0 / IO0 / EN / GND / 3V3). 3V3 from the on-board K7803 buck.

Strapping pins:
- IO0 — pull-up + on the header (boot select)
- IO5 — spare (was pump-B 3rd line); high at boot
- IO15 — flow input; high at boot
- IO2, IO12 — unconnected; low / floating at boot

Radio unused; the WROOM antenna keepout stays. No on-board USB, USB-UART bridge, or
auto-program circuit.
