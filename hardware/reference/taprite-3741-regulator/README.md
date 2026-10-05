# Taprite 3741 CGA-320 CO2 regulator

The primary regulator that ships with the appliance (`hardware/ledger/bom.md` §4; Draft Warehouse
order 244592, [listing](https://www.draftwarehouse.com/products/co2-primary-soda-regulator-cga320-in-1-4-flare-outlet-with-check-taprite)).
It stands on the customer's own CO2 cylinder and is the only thing on this machine the customer
threads onto anything: the CGA-320 nut pulls down on the cylinder valve.

## It ships set, and the customer sets nothing

[Acceptance](/hardware/assembly/acceptance-and-burn-in.md) step 1 makes up each unit's own
regulator and sets it:

- Taprite's 1/4" flare outlet fitting with its ball check (5436A) comes out of the body's 1/4" NPT
  outlet port, and a gray acetal John Guest PI010822S threads in, sealed as WR1105 IN is
  ([`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md)).
- The unit's red 1/4" LLDPE tether pushes into that PI010822S and stays there: regulator and tether
  ship as one piece, and the tether's other end goes into the CO2 bulkhead on the +Y wall of
  back-top.
- The slotted adjusting screw is turned to **75 psi** (`FACTORY_SET_PSI`) on the regulator's own
  upper gauge, the jam nut is locked over it, and one paint line is drawn across screw, nut and
  bonnet. The unit passes acceptance on that setting and ships at it.

There is no knob and no outlet shutoff. The customer seats a washer in the nut, tightens it onto the
cylinder, pushes the tether's free end into the machine and opens the cylinder valve. The in-machine
WR1105 holds the feed at 3 bar below the 75 psi, and the GASHER check downstream of it is the gas
path's check valve.

## Six things a picture points at

| | |
|---|---|
| `inlet()` | the CGA-320 nut's face, on the customer's right, that goes onto the cylinder |
| `outlet()` | the PI010822S's push-fit mouth at the bottom, where the red tether goes in |
| `adjustment()` | the slotted screw's tip, out the front of the black bonnet: set at the factory, leave it |
| `relief()` | the safety blow-off's vented end, on the upper right of the body |
| `tank_dial()`, `outlet_dial()` | the two dials, which do not read the same thing |

## The two dials

- **Cylinder contents**, on the customer's left: 0–2000 psi in black outside, bar in red inside. A
  CO2 cylinder reads its vapour pressure, about 850 psi at room temperature, for as long as any
  liquid is left, so the needle sits in the green band until the cylinder is nearly empty and then
  falls into the red. That is how the owner tells an empty cylinder from any other fault.
- **Outlet pressure**, above: 0–160 psi in black outside, 0–11 bar in red inside. It reads the
  factory's 75 psi when gas is on.

Both needles are drawn at rest on zero, which is the state the part ships in. The install guide's
startup scene redraws them at 75 and 800 psi.

## Where each figure comes from

**Taprite's own drawings.** The sales drawing 3741_SALES rev C (drawn 1:2: 7" wide, 6" tall, 4.3"
deep) and the parts breakdown 3741 REGULATOR ASSEMBLY rev C, 10-2010, read at 150 px to the real
inch. Off them: the 2-1/4" gauge bezels and their centres 67 mm above and 65 mm out from the body
axis; the inlet nipple and the nut's station on it; the 50 mm bonnet flange, its hex neck and round
nose; the 3/8" slotted screw and jam nut; the blow-off's place on the body; the outlet port's face
23 mm below the axis. The 130 ± 4 psi blow-off and 0–120 psi working range are the drawing's notes.

**Taken at its standard.**

| | | |
|---|---|---|
| CGA-320 thread | 0.825"-14 NGO-RH-EXT (Ø20.96 major) | the connection every USA CO2 beverage cylinder presents |
| CGA-320 nut hex | 1-1/8" across flats (28.575 mm) | the wrench size every CO2 nut, wrench and parts list in the trade names |
| CGA-320 nut length | 1" | |
| outlet push-fit | PI010822S at the repository's nominal 1/4" male-connector envelope | [`jg-pp010822e`](/hardware/reference/jg-pp010822e/) |

**Placed, for the received part to fix.** The contents dial's red band (0–300 psi) and green band
(600–1000 psi), off the drawing and the product photograph. The nut is drawn run up onto the valve,
its face 85.4 mm out, with the nipple's nose 9 mm inside it.

**Not modelled.** The lens over each dial and the works behind it; the dial screws and lettering
other than the scales, units and maker's name; the bonnet's label flat; the internal diaphragm,
spring and seat; the NPT shank inside the outlet port. Threads are plain cylinders.

## Frame

The frame the regulator hangs in once it is on the cylinder, origin where the bonnet's axis crosses
the inlet and outlet axes:

- **+Y** out of the body's face toward the customer — the bonnet and its adjusting screw.
- **+Z** up — the outlet-pressure dial. **−Z** down — the outlet push-fit.
- **−X** the inlet axis, out toward the cylinder — the CGA-320 nut.
- **+X** the cylinder-contents dial.

```sh
tools/cad-venv/bin/python hardware/reference/taprite-3741-regulator/taprite_3741_regulator.py
```

It writes `taprite-3741-regulator.step` and holds the six extremes of that file to the stations it
states.
