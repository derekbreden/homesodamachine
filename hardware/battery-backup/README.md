# Battery Backup

Keeps the dispense path running through a mains outage. The compressor stays off, so the carbonated water in the vessel warms over the outage; CO2 still drives the pour (no power moves the water), and the battery powers only the electronics that sense flow and meter flavor. Pour over ice if desired.

## What the battery carries

Only the dispense-critical subset runs from the battery:

- ESP32 (main) + DIGITEN flow sensor — continuous idle
- Per pour: two solenoid valves held open + one Kamoer peristaltic pump, a few seconds

Shed on battery (not carried): the 120 VAC compressor, the SeaFlo diaphragm pump, the condenser fan, and the ESP32-S3 display. Peak carried load ~2 A; idle ~1.5 W, target ~0.4 W with ESP32 deep-sleep (wake on the flow pin).

## Architecture

- **4S LiFePO4 pack (12.8 V nominal) on the existing 12 V bus.** The Mean Well IRM-90-12 supply is unchanged.
- **Chemistry:** LiFePO4 tolerates standby float, is the safest cell chemistry (consistent with the enclosure's R-600a fire-safety posture), and 4S is a true 12 V battery — a drop-in for the bus. Float at ~13.3–13.6 V (≈80–90% SoC) and mount the pack away from the condenser/compressor heat for 10-year calendar life. The pack cycles only during outages, so calendar life governs, not cycle life.
- **Charger:** the 12 V rail cannot reach the 14.6 V a 4S LiFePO4 needs, so a CC/CV **boost** board tops the pack from the 12 V bus.
- **Transfer:** a main-priority automatic transfer module hands the bus to the pack when the IRM's output drops and blocks the pack from back-feeding the dead supply.
- **Mains-sense:** a logic signal into a spare ESP32 GPIO tells firmware mains is gone. Cleanest source is the IRM's 12 V output presence (keeps AC away from the MCU); the transfer module's status pin works too.
- **Fuse:** inline blade fuse at the pack (~5 A).

## Firmware (blackout mode)

On loss of mains (via the sense input): skip the compressor and the refill-then-rechill interlock so warm pours are allowed; sleep the ESP32-S3 display; watch pack voltage for a low-battery warning and clean cutoff. Deep-sleep the ESP32 between pours (wake on the flow pin) to cut idle draw — every mW of idle removed is pack capacity, and volume, not carried. The DS3231 RTC keeps time on its own coin cell.

## Energy

- Per pour ≈ 0.05 Wh (two solenoids ~7 W + duty-cycled pump, ~10 s).
- Idle dominates runtime: ~1.5 W as-is, ~0.4 W with deep-sleep.
- Runtime ≈ pack Wh ÷ idle W. 18500 4S (~13 Wh) ≈ 8 h at 1.5 W, ~30 h at 0.4 W. 32700 4S (~77 Wh) ≈ days.

## Added volume

Cells dominate; the electronics are minor. 18500 build ≈ 0.09 L (cells + boards); 32700 build ≈ 0.28 L. Both additive to the IRM-90-12.

## Parts

**Cells — 4S (four in series), by runtime:**

| Part | Spec | ASIN | Price | Link |
|---|---|---|---|---|
| 18500 LiFePO4 | ~13 Wh @4S, ~51 cm³ | B0GKGGZJD3 | $29.99 | https://www.amazon.com/dp/B0GKGGZJD3 |
| 32700 LiFePO4 6-pk + 4-slot holder | ~77 Wh @4S, ~240 cm³ | B0GVS4833L | $37.99 | https://www.amazon.com/dp/B0GVS4833L |

**BMS — 4S LiFePO4:**

| Part | Spec | ASIN | Price | Link |
|---|---|---|---|---|
| 4S BMS w/ NTC temperature protection | balance + temp (serves 10-yr goal) | B0DCVV9QR9 | $27.99 | https://www.amazon.com/dp/B0DCVV9QR9 |
| 4S 30 A BMS (3-pk) | balance, no temp, smaller board | B09Z6N4CBN | $9.99 | https://www.amazon.com/dp/B09Z6N4CBN |

**Charger — boost 12 V → 14.6 V CC/CV:**

| Part | Spec | ASIN | Price | Link |
|---|---|---|---|---|
| CC/CV step-up board (2-pk) | set to 14.6 V / low current | B0C6KKYCQH | $11.99 | https://www.amazon.com/dp/B0C6KKYCQH |

**Transfer — mains-priority changeover:**

| Part | Spec | ASIN | Price | Link |
|---|---|---|---|---|
| DC 12 V dual-source ATS | main-priority, switches on loss | B0D9RM3QWR | $13.99 | https://www.amazon.com/dp/B0D9RM3QWR |
| 10 A auto-switch | main-priority, smaller | B0D3QLPPJJ | $8.69 | https://www.amazon.com/dp/B0D3QLPPJJ |

**Mains-sense — logic into ESP32 GPIO:**

| Part | Spec | ASIN | Price | Link |
|---|---|---|---|---|
| PC817 optocoupler module | sense IRM 12 V output, AC stays off the MCU | B0B5373L4P | $6.99 | https://www.amazon.com/dp/B0B5373L4P |
| AC-detect optocoupler module | senses mains directly; confirm 120 V trigger | B0CHJNRZMW | $9.99 | https://www.amazon.com/dp/B0CHJNRZMW |

**Fuse:**

| Part | Spec | ASIN | Price | Link |
|---|---|---|---|---|
| Inline ATO/ATC blade fuse holder (2-pk) | fit ~5 A blade fuse | B0DHSQ9CNP | $3.97 | https://www.amazon.com/dp/B0DHSQ9CNP |

Prices as listed on Amazon 2026-06-08.
