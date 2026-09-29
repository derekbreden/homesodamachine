# Shared context

What every explorer starts from. Each fact carries its source:

- **[Derek]**: Derek's own words.
- **[repo]**: this repository, with the file named.
- **[mfr]**: a manufacturer document, read by the facts pass
  ([`xh-facts.md`](xh-facts.md)).
- **[assumption]**: nobody has measured it.

Old agent-written numbers in the repo are not requirements.

## The product: XH cable ends on flat ribbon

- **What is being made.** Every board-end termination of the appliance's
  low-voltage looms is an XH crimp contact in an XH housing, seated on the main
  board's XH wafers. [repo: `hardware/assembly/cable-assemblies.md`]
- **Wire.** Every loom is **BNTECHGO 22 AWG black silicone flat ribbon**, bought
  as 3P, 4P and 5P on 50 ft (15.2 m) spools. The conductors are webbed side by
  side at **1.7 mm per conductor**, and a 4P + 5P pair lies 15.3 mm across and
  1.7 mm thick. [repo: `cable-assemblies.md`; `hardware/ledger/bom.md` §11]
  - Strand count and strand diameter for the 22 AWG are unrecorded
    [assumption: fine tinned strands, on the order of 60 × 0.08 mm, as the 28 AWG
    sibling is 16 × 0.08 mm per bom.md].
  - Silicone insulation is soft, grippy and tears rather than cuts cleanly.
    Whether the web between conductors peels cleanly without nicking insulation
    is untested (Open item 5 in `cable-assemblies.md`).
- **Contact.** Named in the repo as **SXH-001T-P0.6**: conductor #28 to #22,
  insulation OD 0.9 to 1.9 mm, tin plated. The ribbon's 1.7 mm conductor sits
  mid-range. [repo: `cable-assemblies.md`]
  - The contacts actually on hand come loose in **CQRobot "JST XH 2.54 mm"
    kits** (housings plus loose terminals, 4/5/6/7/9-way, $8–9 per 30–50 sets).
    [repo: `bom.md` §11]
  - Whether those are genuine JST parts is unknown. They are more likely
    compatible clones [assumption].
  - In JST's naming the SXH prefix is the chain (reel, carrier strip) form and
    BXH the loose-piece form. The facts pass checks this.
- **Housing.** XHP-n female housings, n = 4, 5, 6, 7, 9, from the same kits. XH
  pitch is 2.50 mm (the kits say "2.54") [mfr, to be confirmed]. The mating male
  wafers are on the main board. [repo: `bom.md`, `cable-assemblies.md`]

### Per unit

Ten looms end in XH at the board, and the other end of every loom is something
else: Fastons, ferrules into Wago lever nuts, 110 IDC, screw terminals.
[repo: `cable-assemblies.md` § Ribbon pairs, § Assembly schedule]

| Loom | XH housing | Contacts crimped | Ribbon(s) entering the housing |
|---|---|---:|---|
| J1 MANIFOLD A | XHP-9 | 9 | 5P + 4P side by side |
| J2 MANIFOLD B | XHP-6 | 5 | 3P + 3P. **Contact 3 is left empty on purpose** and the conductor that would land there is trimmed, not crimped |
| J3 FAUCET | XHP-4 | 4 | 4P |
| J4 SENSORS | XHP-7 | 7 | 4P + 3P |
| J5 RELAYS | XHP-4 | 4 | 4P |
| J6 REEDS A | XHP-5 | 5 | 5P |
| J7 REEDS B | XHP-7 | 7 | 5P + 3P, one 3P conductor trimmed |
| J9 DISPLAY | XHP-4 | 4 | 4P |
| J11 GAS | XHP-4 | 4 | 4P |
| J13 PUMPS | XHP-4 | 4 | 4P |

That is **53 XH crimps per unit on 14 ribbon ends in 10 housings**. Four
housings take two ribbons laid edge to edge. J4 and J7 use the same 7-way
housing, and a swap between them is a wiring fault, so each loom is labelled at
the housing. Loom lengths run about 100 to 600 mm. [repo]

### Volume and time

- **Program volume.** One unit in Derek's kitchen, then ten units, then the
  Founder Edition run of 50, built one at a time by one person. [repo:
  `future/README.md`] That is about 60 units and **roughly 3,200 XH crimps**
  across the whole program, plus spares and rework.
- **Print time.** "About a week of print time per unit" [Derek]. The ledger
  counts about 100 printer-hours per unit across two printers [repo:
  `hardware/ledger/labor.md`]. At that pace a machine taking **several minutes
  per crimp** still finishes a unit's 53 crimps in an afternoon, unattended.
- **Current labor.** All twelve harness assemblies take 45 attended minutes per
  unit: about 60 terminations of every kind, built a batch at a time. Wiring is
  1 h 35 m of the unit's attended labor. [repo: `hardware/ledger/labor.md`]

## The procedure as it stands, by hand

From `cable-assemblies.md` [repo]:

1. **Cut** the ribbon(s) to the loom's longest leg, plus a service loop.
2. **Splay** the ribbon's conductors at the housing end so each enters its die
   straight. A conductor still webbed to its neighbour enters at an angle.
3. **Strip** to the contact's barrel length (the JST value is in the facts
   pass). The bench stripper is a Klein 11063W, rated AWG 10–20 and used down to
   24.
4. **Place the contact and crimp.** The tool is an **iCrimp SN-2549** ratcheting
   crimper (open-barrel, AWG 28–18, with nests for PH, ZH, XH, VH and Dupont).
   No low-cost tool has a locator, so the contact is placed by hand: close the
   ratchet one click so the contact is captive, feed the wire, complete the
   crimp. JST's own hand tool for this range, **WC-110** (#22–#28, side entry),
   does have a locator.
5. **Insert** each contact into its housing cavity until it latches, in the
   loom's pin order. J2's empty cavity 3 is the guard against landing every
   conductor one position off.
6. **Test** continuity pin to pin, check adjacent shorts, and label the
   assembly by name.

**Derek's priority** is step 4: place the contact on the conductor, hold both in
something that crimps, and crimp. "Really getting the whole procedure automated
would be ideal." [Derek]

## The bench: tools and capabilities on hand

From `hardware/ledger/tools.md` [repo], with what matters here:

- **Printers.** Two **Bambu Lab H2C**: dual-nozzle, left-nozzle envelope
  325 × 320 × 320 mm, with AMS units and a vision/timelapse camera. They print
  PETG, ASA, PET-CF17, PET-GF15 and TPU 90A, with hardened and diamond nozzles
  on hand. They are busy about 100 h per unit printing the appliance. Derek
  likes printing things and building things. [Derek, in the weld study brief]
- **Crimp and wire tools.**
  - iCrimp SN-2549 (XH nest).
  - Taiss SN-28B (Dupont).
  - Haisstronica 22–10 insulated-terminal crimper.
  - Preciva ferrule crimper.
  - Klein 11063W self-adjusting stripper.
  - KATA micro flush cutters and Knipex diagonal cutters.
  - Hakko FX-888D iron and FR-301 desoldering gun.
  - Klein VDV427-300 impact punchdown.
  - VCE modular-plug crimper.
- **Presses and motion.**
  - **VEVOR 12-ton hydraulic shop press**, idle.
  - **WEN 4208T benchtop drill press**.
  - A **NEMA 23 stepper with DM542T driver** and 24 V supply, in the cap-weld
    tube rotator (a deadman pedal feeds the same controller).
  - DeWalt 200 PSI compressor, for air.
  - HOTO electric screwdriver with torque settings.
- **Measurement and sight.**
  - **ELP 16MP autofocus USB camera** (IMX298, UVC, focus and exposure
    commanded from software on this Mac via `tools/panelcam-uvc/`).
  - **Revopoint MINI 2** structured-light scanner (0.02 mm stated).
  - NEIKO digital caliper.
  - 2000 g × 0.1 g scale.
  - Bambu Vision Encoder.
- **Laser.** XLaserlab X1 Pro handheld fiber laser welder, cleaner and cutter
  (kW-class). It is the carbonator's weld station.
- **Software.** The appliance runs ESP32 firmware built with PlatformIO. This
  Mac runs Claude Code with the in-app browser and camera tooling. Software
  that moves motors, reads cameras and logs every cycle is familiar ground.

## Sourcing

Derek values low lead time, low price and real market volume in parts: things
that are in stock, ship in days and are sold in quantity, over quote-and-wait
industrial channels. [Derek, weld study brief] On Amazon only Prime listings
count; non-Prime listings are not read and not mentioned [repo: `CLAUDE.md`].
The study's sourcing rules are in [`working-method.md`](working-method.md).
