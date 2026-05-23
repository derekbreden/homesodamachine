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
