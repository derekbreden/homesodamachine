#pragma once

// ════════════════════════════════════════════════════════════
//  What this firmware reaches on the main board
// ════════════════════════════════════════════════════════════
//
// Every number here is read off hardware/pcb/pcba/pcba.tsx, the canonical pin
// map, and drawn as hardware/wiring/esp32-pinout.mmd. Only pins this image
// actually drives or reads are named; the main board carries more.

// ── Outputs that reach an actuator ────────────────────────────────────────
// machine.cpp is the only file that drives any of these.
static const int PIN_RELAY_COMPRESSOR = 19;  // U15 interlock -> J5 relay #1
static const int PIN_RELAY_REFILL     = 2;   // J5 relay #2 -> SeaFlo 12 V gate
static const int PIN_PUMP_A           = 17;  // U11 DRV8870 IN1 -> J13.AM1/AM2
static const int PIN_PUMP_B           = 4;   // U12 DRV8870 IN1 -> J13.BM1/BM2
static const int PIN_BUZZ             = 13;  // R5 -> Q1 -> U8

// IN2 sits on the GND plane on both DRV8870s, so IN1 alone carries the drive:
// high drives the bridge one way, low coasts it. PWM on IN1 is fast-decay, and
// an IN1 parked as an input coasts the head on the driver's own pull-down —
// which is what makes a brownout reset safe. ISEN is grounded with no sense
// resistor, so the chip's limit never trips; a Kamoer KPHM400 draws ~0.8 A.
static const int PUMP_PWM_HZ   = 20000;  // above hearing — every sound in the room is mechanical
static const int PUMP_PWM_BITS = 8;      // ledcWrite(255) is a true 100%: the core maps it to full-on

// ── Status LEDs, through 470R (D2/D3/D4) ──────────────────────────────────
// RUN and ERR sit on boot straps, sampled at reset:
//   IO12 MTDI — VDD_SDIO select, low = 3.3 V flash. Its LED runs to GND, which
//     holds it there, so RUN is parked on an internal pull-down between beats.
//   IO15 MTDO — ROM boot log on U0TXD, high = printed. Its LED runs to 3V3
//     (ERR is the one active-low row), so the pin idles high, the LED is dark,
//     and the ROM log prints.
static const int PIN_LED_ERR = 15;  // D2 red   — active low
static const int PIN_LED_RUN = 12;  // D3 green — heartbeat
static const int PIN_LED_ACT = 14;  // D4 blue  — lit while the machine drives something

// ── I2C — R19/R20 4.7k pull-ups to 3V3, out to J8 ─────────────────────────
// U6 (DS3231 clock, 0x68) shares this bus with the MCP23017s at 0x20/0x21.
// machine.cpp parks their output banks and enables the reed-bank pull-ups at
// boot; pcba_expanders.cpp owns their register and physical-output mapping.
static const int PIN_SDA = 21;
static const int PIN_SCL = 22;

// ── Gas dividers — MQ-6 through R1/R2 and R3/R4, ADC1 input-only pins ─────
static const int PIN_GAS_AOUT = 39;  // analog level
static const int PIN_GAS_DOUT = 36;  // LM393 comparator trip

// ── J9, the pair to the enclosure display ─────────────────────────────────
// IO32 -> U7.DI -> the A/B pair and R6's 120R termination -> U7.RO -> IO34.
// D1 clamps the exposed differential pair at J9.
static const int PIN_485_DI  = 32;
static const int PIN_485_RO  = 34;
static const long RS485_BAUD = 460800;  // U7's auto-direction is specified to 500 kbps

// ── J3, direct TTL UART up the faucet umbilical ──────────────────────────
// Main board TX crosses to the faucet's P1 ESP_RXD (GPIO44); main board RX
// crosses from faucet P1 ESP_TXD (GPIO43). R26/R27 provide series damping and
// D10/D11 clamp the main board end of the exposed run.
static const int PIN_FAUCET_TX = 33;
static const int PIN_FAUCET_RX = 35;
static const long FAUCET_BAUD  = 921600;  // direct TTL — no transceiver ceiling
