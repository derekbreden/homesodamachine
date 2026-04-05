---
name: Future Sensing and GPIO Expansion
description: Capacitive liquid/air sensing, hopper integration, GPIO pin audit, and I2C expansion architecture for future system growth
type: project
---

# Future: Capacitive Sensing, Hopper Integration, GPIO Expansion

**Status:** Early brainstorming — no plan, no timeline. Context for future conversations.

## Liquid/Air Detection Needs

Two sensing points per flavor line (4 sensors total for 2-flavor system):

1. **Near the tap** — detects "is primed" (air-to-liquid transition confirms flavor is in the line)
2. **In the hopper** — detects "liquid still needs pumping into bag" (liquid-to-air transition as hopper drains)

## Leading Approach: Capacitive Sensing

- Copper tape pairs wrapped around tubing, no fluid contact
- Water dielectric constant ~80 vs air ~1 — massive signal difference
- Works for both locations with same technique
- Sugar/flavoring concentration doesn't matter — only detecting liquid vs air presence
- **FDC1004**: capacitance-to-digital I2C chip, 4 channels (exactly 2 flavors x 2 locations)
- ESP32 native touch pins could work but dedicated chip gives cleaner threshold

## Other Approaches Considered

- **Pressure-based**: pump pulse → close valve → read curve (sharp step = liquid, slow ramp = air). Richer data but more mechanically complex.
- **Optical**: IR LED + photodetector across tube. Simple, fast, no contact.
- **Thermal**: self-heated thermistor on tube wall, water conducts heat 25x better than air.

Capacitive chosen as sweet spot: no moving parts, no fluid contact, real-time, enormous signal margin.

## Air Purge as Clean Cycle Finishing Step

During cleaning, the bag is filled with water and flushed through the lines multiple times. After the last rinse drains the bag, the pump keeps running — now pulling air through the empty bag/hopper and pushing it through the lines to blow out remaining water. The air source is the drained bag itself, not a separate intake. This requires the hopper system to be in place. The tap-side capacitive sensor would confirm the air blow-through actually cleared the line, giving a definitive "clean complete" signal rather than relying on timed durations.

## Bonus Capabilities from Capacitive Sensing

- Hopper sensor confirms when flavor refill fully transferred to bag (pump can stop)
- Tap sensor confirms air purge has cleared the line (clean cycle complete)
- Tap sensor confirms priming has filled the line with flavor (prime complete)
- Closes the loop on priming, cleaning, and refilling automatically

## GPIO Pin Audit (as of 2026-03-22)

### Currently Used: 18 pins

| GPIO | Function |
|------|----------|
| 4 | Flavor 2 solenoid valve (L298N #2 ENB, PWM) |
| 5 | Flavor 2 pump direction (L298N #2 IN2) |
| 12 | Flavor 1 solenoid valve (L298N #1 ENB, PWM) — strapping pin, must be LOW on boot |
| 13 | Air switch (flavor select, INPUT_PULLUP) |
| 15 | UART1 TX to ESP32-S3 |
| 17 | Clean solenoid flavor 2 (L298N #3, PWM) |
| 18 | Flavor 2 pump direction (L298N #2 IN1) |
| 19 | Flavor 2 pump PWM (L298N #2 ENA) |
| 21 | I2C SDA (DS3231 RTC, addr 0x68) |
| 22 | I2C SCL (DS3231 RTC, addr 0x68) |
| 23 | Flow meter pulse (INPUT_PULLUP, interrupt) |
| 25 | Flavor 1 pump direction (L298N #1 IN1) |
| 26 | Flavor 1 pump direction (L298N #1 IN2) |
| 27 | Clean solenoid flavor 1 (L298N #3, PWM) |
| 32 | UART2 TX to RP2040 |
| 33 | Flavor 1 pump PWM (L298N #1 ENA) |
| 34 | UART1 RX from S3 (input-only) |
| 35 | UART2 RX from RP2040 (input-only) |

### Unavailable

- GPIO 0, 2: strapping pins (risky)
- GPIO 1, 3: USB serial
- GPIO 6-11: internal flash
- GPIO 20, 24, 28-31: **don't exist** on original ESP32

### Actually Free

| GPIO | Capabilities |
|------|-------------|
| 14 | Output/Input/PWM — fully usable |
| 16 | Output/Input/PWM — free if no PSRAM (esp32dev doesn't use it) |
| 36 | **Input-only**, ADC1_CH0 |
| 39 | **Input-only**, ADC1_CH3 |

**Total: 2 output-capable pins, 2 input-only pins.** Extremely tight.

## Expansion Architecture: I2C Bus

The existing I2C bus (GPIO 21/22) currently has only the DS3231 RTC at address 0x68. This is the key expansion path — multiple devices share the same 2 pins:

| Device | I2C Address | Purpose | New GPIO Needed |
|--------|------------|---------|----------------|
| DS3231 RTC | 0x68 | Already installed | 0 (existing) |
| FDC1004 | 0x50 | 4-ch capacitive sensing | 0 |
| MCP23017 | 0x20-0x27 | 16 digital GPIO per chip | 0 |
| PCA9685 | 0x40 | 16-ch PWM driver | 0 |

**All future expansion routes through I2C. No bigger chip needed. No additional MCUs needed.**

### No PWM Actually Needed

Despite using `analogWrite()`, all pumps run at `PUMP_SPEED = 255` (always max, never variable). Pumps are duty-cycled via on/off timing, not PWM speed control. Solenoid valves are also purely on/off. This means:
- **Every current output pin could be driven by MCP23017 digital outputs** — no PCA9685 needed
- Existing pins could theoretically be reclaimed onto an I/O expander if needed
- Future hopper pumps (likely also on/off through MOSFETs) fit the same pattern

### What the Hopper System Will Need

- 1-2 pump controls (on/off) → MCP23017 outputs + MOSFETs
- Additional solenoid valves → MCP23017 outputs
- 4 capacitive sensors → FDC1004 channels
- **Total new ESP32 GPIO: 0** (all via I2C)

## Bottom Line

The RTC inadvertently created the expansion bus for everything that comes next. I2C on GPIO 21/22 is the single expansion path. No architectural change needed — just add I2C devices to the existing bus. GPIO 14 and 16 are held in reserve for anything that absolutely must be native ESP32 output.

Derek's preference to avoid multi-MCU complexity is fully achievable with this architecture.
