# Home Soda Machine

## 1. Basic Operation

- Refrigerated carbonated water is provided to a faucet by a built-in carbonator (replacing the external Lillium/Brio units used in the prototype)
- When that flow is detected, we pump flavoring in a parallel line (not the same line as the cold carbonated water)
- There are 2 separate parallel lines, one for each flavor, and each is primed and valve locked so that it is always primed and can be dispensed instantly
- The mixing occurs in the user's cup/glass, not before

## 2. Filling

- The user pours sodastream sucralose sweetened flavoring (no sugar) into a funnel
- That funnel is as close to the front as possible, on the top side of the device
- Liquid in the tubing connected to the funnel is detected via capacitance, and is pumped into the selected flavoring bag

## 3. Cleaning

- The user initiates a clean cycle for a flavoring bag from the iOS app or S3 interface
- The valve allowing tap water into the bag is opened until the bag fills with water, then is closed
- That water is pumped through the normal dispensing route from the bag
- Air is pumped into the bag from the funnel inlet
- That air is pumped through the normal dispensing route from the bag
- The cycle is repeated

## 4. Replacing the pumps

- There are only 2 peristaltic pumps, one dedicated to each flavor, and the valves allow them to be used for multiple purposes
- When the pumps wear out, the user can remove and replace the pump cartridge which contains both pumps
- Nothing else is replaceable (e.g. the bags are permanent fixture the same as all other internal plumbing)

## 5. The hardware that already accomplished all of this in the prototype includes:

| Part | Qty |
|------|----:|
| [ESP32-DevKitC-32E](https://www.amazon.com/dp/B09MQJWQN2) | 1 |
| [Waveshare RP2040 Round LCD (0.99")](https://www.amazon.com/dp/B0CTSPYND2) | 1 |
| [Meshnology ESP32-S3 1.28" Round Rotary Display](https://www.amazon.com/dp/B0G5Q4LXVJ) | 1 |
| [L298N Motor Driver (4-pack)](https://www.amazon.com/dp/B0C5JCF5RS) | 1 |
| [Kamoer Peristaltic Pump](https://www.amazon.com/dp/B09MS6C91D) | 2 |
| [Beduan 12V Solenoid Valve](https://www.amazon.com/dp/B07NWCQJK9) | 10 |
| [DIGITEN Flow Sensor](https://www.amazon.com/dp/B07QQW4C7R) | 1 |
| [Platypus 2L Collapsible Bottle](https://www.amazon.com/dp/B000J2KEGY) | 2 |
| [Silicone Tubing (6m)](https://www.amazon.com/dp/B0BM4KQ6RT) | 1 |
| [KRAUS Air Switch](https://www.amazon.com/dp/B096319GMV) | 1 |

- The RP2040 is smaller display which looks nice mounted flush with paneling in front of the sink.
- The S3 is a larger display, which has a knob and allows easy changing of flavoring ratios or other settings.
- It is expected that both displays will be mounted into the front of the final device, such that they can be "snapped out" and placed elsewhere, with a retracting 1m or 2m cat6 cable connecting them to the device still, but that that they are flush with the front of the device otherwise.
- The ESP32 will maintain all functionality even if both displays are disconnected entirely.
- The KRAUS Air Switch is also expected to be mounted and detachable and flush in the exact same fashion as the displays. However, if it is disconnected, the user will be stuck on whatever flavor was last selected.

## 6. Printed parts

- The FDM printer is a Bambu H2C
- Single Nozzle Printing: 325 mm x 320 mm x 320 mm
- Dual Nozzle Printing: 300 mm x 320 mm x 325 mm
- Layer sizes can be as low as 0.1 mm
- Supported materials (standard): PLA, PETG, TPU, PVA, BVOH, ABS, ASA, PC, PA, PET, PPS, PPA
- Supported materials (carbon/glass fiber reinforced): PLA, PETG, PA, PET, PC, ABS, ASA, PPS
