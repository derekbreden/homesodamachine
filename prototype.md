# Prototype

This documents the prototype dispensing soda under Derek's kitchen sink today — the proof of the dispense path. Refrigerated carbonated water from a Lilium under-counter carbonator. When flow is detected, peristaltic pumps inject Pepsi-made concentrate into the dispensed water at the faucet. Two flavors, primed and valve-locked for instant dispensing. The mixing happens in the user's glass, not before.

The integrated appliance that replaces the Lilium and pulls everything into one enclosure is in [`hardware/future.md`](hardware/future.md). The story of how this got built — failed SodaStream, the business-license wall, the AI design wall — is in [`how-this-got-built.md`](how-this-got-built.md).

<p align="center">
  <img src="docs/photos/display-pepsi-cherry.jpg" width="360" alt="Front panel showing LCD display with Diet Pepsi Cherry logo and air switch buttons">
  <img src="docs/photos/display-mountain-dew.jpg" width="360" alt="Front panel showing LCD display with Diet Mountain Dew logo and air switch buttons">
</p>
<p align="center"><em>The RP2040 round LCD shows the active flavor. An air switch button toggles between flavors.</em></p>

https://github.com/user-attachments/assets/ddd9bcfd-567e-414a-80be-4f5125431bac

<p align="center"><em>Changing flavor images and ratios on the config display, then pouring a glass with both flavors.</em></p>

## How It Works

Cold carbonated water flows from an under-counter carbonator through a dispenser faucet. When you open the faucet, a flow meter detects water movement and the system automatically kicks in:

1. A solenoid valve opens (it stays closed between uses to prevent backflow and keep the lines primed)
2. A peristaltic pump injects concentrate from a collapsible reservoir
3. The pump duty-cycles on/off proportionally to the detected flow rate
4. Concentrate meets the water stream at the faucet spout

A toggle switch (an air switch) selects between two flavors. The small LCD display updates to show which flavor is active.

<p align="center">
  <img src="docs/photos/countertop-annotated.jpg" width="500" alt="Kitchen countertop showing soda dispenser faucet and flavor toggle switch">
</p>
<p align="center"><em>The countertop: a dedicated dispenser faucet and a flavor toggle air switch.</em></p>

### Under the Counter

Everything lives inside the sink cabinet:

<p align="center">
  <img src="docs/photos/under-cabinet.jpg" width="600" alt="Under-cabinet view showing CO2 tank, carbonator, concentrate bag, and control panel">
</p>
<p align="center"><em>Left to right: CO2 tank with dual-gauge regulator, Lilium carbonator, Platypus bag filled with concentrate, and the control panel with pumps and valves.</em></p>

Silicone concentrate lines are zip-tied to the outside of the faucet gooseneck:

<p align="center">
  <img src="docs/photos/faucet-side.jpg" width="400" alt="Side view of dispenser faucet with silicone tubes bundled along the gooseneck">
  <img src="docs/photos/faucet-nozzle.jpg" width="300" alt="Close-up of faucet nozzle showing multi-tube dispensing design">
</p>

### Control panel

<p align="center">
  <img src="docs/photos/panel-closeup.jpg" width="500" alt="Control panel showing ESP32 on DIN rail breakout, two L298N motor drivers, peristaltic pumps, and solenoid valves">
</p>
<p align="center"><em>The control panel: ESP32 on a DIN rail breakout board (top), two L298N motor drivers (red boards), two Kamoer peristaltic pumps, and two solenoid valves (bottom).</em></p>

Firmware architecture, pin assignments, TinyProto inter-board protocol, and build/flash instructions: [`firmware/README.md`](firmware/README.md).

## Parts List

Nearly everything was sourced from Amazon Prime. The only exception is the carbonated water machine.

### Electronics

| Part | Purpose |
|------|---------|
| [ESP32-DevKitC-32E](https://www.amazon.com/dp/B09MQJWQN2) | Main controller |
| [ESP32 DIN Rail Breakout Board](https://www.amazon.com/dp/B0BW4SJ5X2) | Clean wiring for ESP32 GPIOs |
| [Waveshare RP2040 Round LCD (0.99")](https://www.amazon.com/dp/B0CTSPYND2) | Flavor display (128x115 GC9107) |
| [Meshnology ESP32-S3 1.28" Round Rotary Display](https://www.amazon.com/dp/B0G5Q4LXVJ) | Config display (240x240 GC9A01A, touch + encoder) |
| [L298N Dual H-Bridge Motor Driver](https://www.amazon.com/dp/B0C5JCF5RS) x2 (link is a 4-pack) | Drive pumps and solenoid valves |
| [12V 2A Power Supply](https://www.amazon.com/dp/B0DZGTTBGZ) | Powers pumps and valves |

### Pumps and Valves

| Part | Purpose |
|------|---------|
| [Kamoer Peristaltic Pump (400ml/min, 12V)](https://www.amazon.com/dp/B09MS6C91D) x2 | Dispense flavor concentrate |
| [Beduan 12V Solenoid Valve (1/4")](https://www.amazon.com/dp/B07NWCQJK9) x2 | Prevent backflow, keep concentrate lines primed |

### Sensors and Switches

| Part | Purpose |
|------|---------|
| [DIGITEN G3/8" Hall Effect Flow Sensor](https://www.amazon.com/dp/B07QQW4C7R) | Measure water flow rate |
| [KRAUS Garbage Disposal Air Switch (Matte Black)](https://www.amazon.com/dp/B096319GMV) | Flavor toggle (countertop safe, no electricity) |

### Plumbing

| Part | Purpose |
|------|---------|
| [Westbrass Cold Water Dispenser Faucet (Matte Black)](https://www.amazon.com/dp/B07KH285GJ) | Dispensing tap at the counter |
| [Platypus 2L Collapsible Bottle](https://www.amazon.com/dp/B000J2KEGY) x2 | Flavor concentrate reservoirs |
| [Platypus Hydration Drink Tube Kit](https://www.amazon.com/dp/B07N1T6LNW) | Tubing + bite valve for reservoirs |
| 1/4" OD Hard Tubing (PE/PU) | All internal plumbing connections (John Guest push-to-connect fittings) |
| [Silicone Tubing (1/8" ID x 1/4" OD)](https://www.amazon.com/dp/B0BM4KQ6RT) | Pump heads, faucet cosmetic run, cable gland pass-throughs, vibration-dampening segments |
| [Waterdrop 15UC-UF Inline Water Filter](https://www.amazon.com/dp/B085G9TZ4L) | Filters water before carbonation |

### Flavor Concentrates

| Part | Notes |
|------|-------|
| [SodaStream Pepsi Wild Cherry Zero Sugar](https://www.amazon.com/dp/B0G4NRDQB8) | Default ratio 1:20 |
| [SodaStream Diet MTN Dew](https://www.amazon.com/dp/B0CS191QMW) | Default ratio 1:20 |

### Wiring and Connectors

| Part | Purpose |
|------|---------|
| [Dupont Jumper Wires (120-pack M/F, M/M, F/F)](https://www.amazon.com/dp/B0BRTJXND9) | Board-to-board connections |
| [Female Spade Crimp Terminals (60-pack)](https://www.amazon.com/dp/B0B9MZJ2ML) | Motor and valve connections |
| [Male Quick Disconnect Spade Connectors (100-pack)](https://www.amazon.com/dp/B01MZZGAJP) | Motor and valve connections |

### Mounting and Hardware

| Part | Purpose |
|------|---------|
| [Zip Ties (200-pack)](https://www.amazon.com/dp/B0BC1VH4XB) | Secure tubing to faucet, cable management |
| [12"x24" Laminate Shelf](https://www.homedepot.com/p/328395734) | Cut in half and screwed together as mounting panel |
| [#8 x 1/2" Wood Screws (100-pack)](https://www.homedepot.com/p/204275505) | Mount components to panel |
| ~~[Pre-wired 12V LEDs (120-pack, 6 colors)](https://www.amazon.com/dp/B07PVVL2S6)~~ | ~~Flavor indicator LEDs~~ (removed — RP2040 display replaced LEDs) |

### Carbonated Water

| Part | Purpose |
|------|---------|
| [Lilium Under-Sink Carbonated Water Dispenser](https://liliumfaucet.com/products/under-sink-carbonated-soda-maker-sparkling-water-dispenser-with-3-way-faucet) | Cold carbonated water source (not from Amazon) |
| [TAPRITE Dual-Gauge CO2 Regulator](https://www.amazon.com/dp/B00L38DRD0) | CO2 pressure regulation |
| 5 lb CO2 Tank + First Refill | CO2 source (refills ~$25 at welding/homebrew shops) |

### Tools

Most builders will already have these on hand.

| Tool | Purpose |
|------|---------|
| [RYOBI ONE+ 18V Drill/Driver Kit](https://www.homedepot.com/p/326680222) | Drilling and driving screws |
| [RYOBI Drill Bit Set (15-piece)](https://www.homedepot.com/p/315853368) | General-purpose drill bits |
| [Milwaukee 1-1/4" Hole Dozer with Arbor](https://www.homedepot.com/p/202327734) | Countertop holes for faucet and air switch |
| [Wiss 10" Tradesmen Scissors](https://www.homedepot.com/p/313487663) | Cutting tubing and zip ties |
| [Husky Precision Screwdriver Set (7-piece)](https://www.homedepot.com/p/302435926) | Electronics work |
| [Klein Tools 3005CR Ratcheting Crimper (10-22 AWG)](https://www.amazon.com/dp/B07WMB61J5) | Crimp spade terminals |
| [Apple USB-C to USB-C Cable (2m)](https://www.amazon.com/dp/B0DCH5B2HF) | Flash the RP2040 |
| [LISEN USB-C to Micro USB Cable (2-pack)](https://www.amazon.com/dp/B0D3BXM91B) | Flash the ESP32 |

## Cost Breakdown

Prices as of March 2026.

| Part | Price | Qty | Cost |
|------|------:|----:|-----:|
| [ESP32-DevKitC-32E](https://www.amazon.com/dp/B09MQJWQN2) | $11.00 | 1 | $11.00 |
| [ESP32 DIN Rail Breakout Board](https://www.amazon.com/dp/B0BW4SJ5X2) | $25.99 | 1 | $25.99 |
| [Waveshare RP2040 Round LCD (0.99")](https://www.amazon.com/dp/B0CTSPYND2) | $23.99 | 1 | $23.99 |
| [Meshnology ESP32-S3 1.28" Round Rotary Display](https://www.amazon.com/dp/B0G5Q4LXVJ) | $47.76 | 1 | $47.76 |
| [L298N Motor Driver (4-pack)](https://www.amazon.com/dp/B0C5JCF5RS) | $9.99 | 1 | $9.99 |
| [12V 2A Power Supply](https://www.amazon.com/dp/B0DZGTTBGZ) | $9.99 | 1 | $9.99 |
| [Kamoer Peristaltic Pump](https://www.amazon.com/dp/B09MS6C91D) | $32.55 | 2 | $65.10 |
| [Beduan 12V Solenoid Valve](https://www.amazon.com/dp/B07NWCQJK9) | $8.99 | 2 | $17.98 |
| [DIGITEN Flow Sensor](https://www.amazon.com/dp/B07QQW4C7R) | $7.99 | 1 | $7.99 |
| [KRAUS Air Switch](https://www.amazon.com/dp/B096319GMV) | $39.95 | 1 | $39.95 |
| [7mm Momentary Push Buttons (12-pack)](https://www.amazon.com/dp/B0F43GYWJ6) | $7.39 | 1 | $7.39 |
| [Westbrass Dispenser Faucet](https://www.amazon.com/dp/B07KH285GJ) | $31.28 | 1 | $31.28 |
| [Platypus 2L Collapsible Bottle](https://www.amazon.com/dp/B000J2KEGY) | $15.94 | 2 | $31.88 |
| [Platypus Drink Tube Kit](https://www.amazon.com/dp/B07N1T6LNW) | $24.95 | 1 | $24.95 |
| 1/4" OD Hard Tubing (25ft roll) | ~$9.00 | 1 | ~$9 |
| [Silicone Tubing (6m)](https://www.amazon.com/dp/B0BM4KQ6RT) | $12.99 | 1 | $12.99 |
| [Waterdrop Inline Water Filter](https://www.amazon.com/dp/B085G9TZ4L) | $62.99 | 1 | $62.99 |
| [Dupont Jumper Wires (120-pack)](https://www.amazon.com/dp/B0BRTJXND9) | $5.97 | 1 | $5.97 |
| [Female Spade Crimp Terminals (60-pack)](https://www.amazon.com/dp/B0B9MZJ2ML) | $9.99 | 1 | $9.99 |
| [Male Spade Connectors (100-pack)](https://www.amazon.com/dp/B01MZZGAJP) | $5.99 | 1 | $5.99 |
| [TAPRITE CO2 Regulator](https://www.amazon.com/dp/B00L38DRD0) | $92.95 | 1 | $92.95 |
| 5 lb CO2 Tank + First Refill | $139.00 | 1 | $139.00 |
| [Zip Ties (200-pack)](https://www.amazon.com/dp/B0BC1VH4XB) | $3.99 | 1 | $3.99 |
| [12"x24" Laminate Shelf](https://www.homedepot.com/p/328395734) | $12.98 | 1 | $12.98 |
| [#8 x 1/2" Wood Screws (100-pack)](https://www.homedepot.com/p/204275505) | $6.87 | 1 | $6.87 |
| [SodaStream Pepsi Wild Cherry (4-pack)](https://www.amazon.com/dp/B0G4NRDQB8) | $28.99 | 1 | $28.99 |
| [SodaStream Diet MTN Dew (4-pack)](https://www.amazon.com/dp/B0CS191QMW) | ~$29 | 1 | ~$29 |
| **Subtotal (without carbonator)** | | | **~$775** |
| [Lilium Under-Sink Carbonator](https://liliumfaucet.com/products/under-sink-carbonated-soda-maker-sparkling-water-dispenser-with-3-way-faucet) | $1,039.00 | 1 | $1,039.00 |
| **Subtotal (all parts)** | | | **~$1,814** |
| *Tools (if not already owned):* | | | |
| [RYOBI Drill/Driver Kit](https://www.homedepot.com/p/326680222) | $49.97 | 1 | $49.97 |
| [RYOBI Drill Bit Set (15-piece)](https://www.homedepot.com/p/315853368) | $12.97 | 1 | $12.97 |
| [Milwaukee 1-1/4" Hole Dozer with Arbor](https://www.homedepot.com/p/202327734) | $16.47 | 1 | $16.47 |
| [Wiss 10" Tradesmen Scissors](https://www.homedepot.com/p/313487663) | $21.97 | 1 | $21.97 |
| [Husky Precision Screwdriver Set](https://www.homedepot.com/p/302435926) | $4.88 | 1 | $4.88 |
| [Klein Tools 3005CR Ratcheting Crimper](https://www.amazon.com/dp/B07WMB61J5) | $34.96 | 1 | $34.96 |
| [Apple USB-C to USB-C Cable (2m)](https://www.amazon.com/dp/B0DCH5B2HF) | $18.00 | 1 | $18.00 |
| [LISEN USB-C to Micro USB Cable (2-pack)](https://www.amazon.com/dp/B0D3BXM91B) | $7.59 | 1 | $7.59 |
| **Total (with tools)** | | | **~$1,981** |
