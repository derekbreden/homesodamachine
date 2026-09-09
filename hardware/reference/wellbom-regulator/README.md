# Wellbom CGA-320 CO2 regulator

The primary regulator that ships with the appliance (`hardware/ledger/bom.md` §4, Amazon
[B0G13P5PMY](https://www.amazon.com/dp/B0G13P5PMY)). It stands on the customer's own CO2
cylinder and is the only thing on this machine the customer threads onto anything: the CGA-320
nut pulls down on the cylinder valve, and the MI4508F4SLF's brass swivel nut pulls down on the
7/16"-20 male flare at the bottom, with the red 1/4" tether running from there to the CO2
bulkhead on the +Y wall of back-top.

Six things the customer is told to find, and each is a station this module states:

| | |
|---|---|
| `inlet()` | the CGA-320 nut, on the customer's right, that goes onto the cylinder |
| `outlet()` | the male flare at the bottom, that the brass nut goes onto |
| `adjustment()` | the fluted black knob on the front, that sets the pressure |
| `shutoff()` | the small knob below it, that opens and closes the gas |
| `relief()` | the pull ring on the lower-left arm |
| `tank_dial()`, `outlet_dial()` | the two dials, which do not read the same thing |

## The two dials

The picture has to say which is which, so both are drawn with their own scales:

- **Cylinder contents**, on the customer's left. 0–3000 psi in red outside, 0–200 bar in black
  inside, `EN562` stamped above the hub. It says how much gas is left.
- **Outlet pressure**, above. 0–230 psi in black inside, 0–16 bar in red outside, with a green
  band across the middle of the scale. It says what is going to the appliance.

Both needles are drawn at rest on zero, which is the state the part ships in.

**The green band is the reason this regulator is the one in the BOM.** On the listing's own front
view it spans roughly **70–95 psi**, and the vendor's recommended pressure for carbonating soda —
80 PSI — sits in the middle of it. The appliance's own WR1110 secondary is a fixed 90 psi, so
the band is the range the customer is asked to set the primary into.

## Where each figure comes from

There is no dimensioned drawing for this part, and the listing publishes none. So:

**Taken at its standard.** These are not read off any picture.

| | | |
|---|---|---|
| CGA-320 thread | 0.825"-14 NGO-RH-EXT (Ø20.96 major) | the connection every USA CO2 beverage cylinder presents |
| CGA-320 nut hex | 1-1/8" across flats (28.575 mm) | the wrench size every CO2 nut, wrench and parts list in the trade names |
| CGA-320 nut length | 1" | |
| outlet thread | 7/16"-20 UNF, Ø11.11 major, Ø9.74 minor | 1/4" SAE 45° male flare |
| outlet cone | 45° to the axis, to a Ø6.4 nose over a Ø4.8 bore | what the MI4508F4SLF's flared tube seats on |
| outlet hex | 9/16" across flats | the hex every 1/4" flare fitting carries |
| dial | 2" | the dial size this whole class of regulator's gauges is sold in |

**Proportion, read off the listing's own front view** (image `71bzwkO3RaL`), scaled so the
7/16"-20 thread in that image measures 11.11 mm across: the gauge case Ø55 × 21 deep at 63 mm
off the body centre; the diaphragm chamber Ø53; the adjustment knob Ø44 over six flutes; the
brass lock ring Ø30 under it; the inlet, outlet and relief arms and every station along them.
That view is marketing art, not a drawing — it is internally consistent to a few percent and no
better. Cross-checks at that scale: the 1/4" barb it ships reads 6.0 against 6.35, and the
overall envelope reads 169 × 63 × 174 mm, which fits inside the listing's 205 × 171 × 119 mm
carton. Reading the same view against the CGA-320 nut instead would put the whole regulator 6%
larger and outside that carton.

**Chosen.** The green band is placed at 70–95 psi, measured off that same front view; the
vendor's separate "Advantages of 0–120 PSI Output" panel draws a green arc over the whole
0–120 range instead, which is that panel's own graphic and not the dial's printing.

**Not modelled.** The lens over each dial and the works behind it; the two case screws on each
dial face; the ON and OFF lettering on the shutoff collar; the internal diaphragm, spring and
seat. The 7/16"-20 thread is drawn as its own minor diameter with one crest ring per turn rather
than as a helix.

## Frame

The frame the regulator hangs in once it is on the cylinder, origin where the bonnet's axis
crosses the inlet and outlet axes:

- **+Y** out of the body's face toward the customer — the adjustment knob.
- **+Z** up — the outlet-pressure dial. **−Z** down — the shutoff and the outlet flare.
- **−X** the inlet, out toward the cylinder. **+X** the cylinder-contents dial.

The regulator is handed and this is the hand it has: standing in front of it, the customer sees
the cylinder on their right, the contents dial on their left, the outlet dial above and the
flare below.

## What the listing says that the BOM does not

- **An outlet shutoff.** A multi-turn knob on the outlet, between the body and the flare, that
  closes the gas without touching the cylinder valve or the pressure setting. The BOM's entry
  does not mention it.
- **The relief figure disagrees with itself.** The vendor's labelled diagram and its comparison
  panel both state that the relief lifts at about **150 psi**, which is what the BOM carries;
  one of the listing's own bullets says instead that it releases above 120 psi.
- **The outlet dial reads to 230 psi**, not to the 120 psi the regulator is rated to put out.
  The rating and the dial's full scale are different numbers.
- The listing price stands at $45.99 against the BOM's $44.99.
- In the box beside the regulator: two nylon cylinder washers, a 1/4" and a 5/16" hose barb with
  their flare nuts, and two hose clamps. This build uses none of them — the MI4508F4SLF takes
  the flare — except that a cylinder washer must be in the nut before it goes on the tank.

## Regenerate

```
tools/cad-venv/bin/python hardware/reference/wellbom-regulator/wellbom_regulator.py
```
