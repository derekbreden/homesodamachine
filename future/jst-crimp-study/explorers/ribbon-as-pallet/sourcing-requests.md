# Sourcing requests: ribbon-as-pallet

These are Amazon candidates for the coordinator's Prime-confirmation pass. No
amazon.com page was fetched to make this list. Items already on the shared list
([`../../context/sourcing-requests.md`](../../context/sourcing-requests.md)) are
not repeated: the load cell with HX711, the crimp micrometer, the XH side-feed
applicator, the 2 t press, the SO-101 arm and the ribbon splitter tool.

| # | Item | Serves | Capability that matters | Search terms |
|---|---|---|---|---|
| 1 | NEMA 17 external linear stepper (lead screw through the motor, anti-backlash nut), 150–300 mm, ×2 | [a1](ideas/a1-pallet-tour.md) stage, [a4](ideas/a4-spool-as-magazine.md) X slide, [a6](ideas/a6-housing-as-last-comb.md) insertion push | ≥100 N thrust; 2 mm lead preferred over 8 mm for force and resolution. A non-Amazon example exists at StepperOnline (17E19S1684MB4-300RS, Tr8×8) | `NEMA 17 linear stepper motor T8 lead screw 2mm lead`, `external linear stepper motor 300mm anti-backlash nut` |
| 2 | MGN12 linear rail with MGN12H carriage, 150–250 mm, ×2 | a1 stage (if built from rails and screws instead of item 1) | Preloaded carriage; the length pairs with the screw | `MGN12H linear rail 200mm`, `MGN12 rail carriage preloaded` |
| 3 | Metal-gear hobby servos, 10–20 kg·cm, ×4 | a1 station actuators: guillotine, strip-blade close, insertion clamp, test-port clamp | Metal gears; standard PWM; torque for ~20–50 N through a short lever | `MG996R metal gear servo 4 pack`, `20kg servo metal gear digital` |
| 4 | Hardened dowel pin assortment (3, 4, 6 mm) | [a1b](ideas/a1b-hand-shuttle.md), [a2](ideas/a2-two-pallets-meet.md) kinematic seats (pins laid in pairs as V-grooves) | Hardened, ground, h6 or m6 tolerance | `hardened dowel pin assortment metric 3mm 4mm 6mm` |
| 5 | Chrome steel balls, 6 mm, G10 or better | a1b, a2 kinematic seats | Grade stated | `6mm chrome steel balls G10`, `bearing balls 6mm grade 10` |
| 6 | N52 disc magnets, 6 × 3 mm and 10 × 3 mm | Seat preload in a1b and a2 | Grade stated; enough pull to hold a pallet home | `N52 disc magnets 6x3mm`, `neodymium magnets 10x3mm` |
| 7 | Single-edge razor blades, 0.009 in, 100-pack | [a5](ideas/a5-part-fan-strip-in-the-pallet.md) flush cut, slitters, S1 strip. A non-Amazon source exists at $10 per 100 (American Cutting Edge) | Carbon steel, 0.009 in, with back | `single edge razor blades 0.009 100 pack` |
| 8 | P75 pogo pins, crown head, 100-pack, plus receptacles | a6 far-end test port | 1.0 mm barrel, 1.3 mm head (fits 1.7 mm pitch). A non-Amazon source is Adafruit P75-H2, $4.95 per 10 | `P75-H2 pogo pins 100pcs`, `P75 crown spring test probe with receptacle` |
| 9 | Ratchet crimper with a JST XH nest, ×1–5 (iCrimp or IWISS SN-2549 class) | a2 walking head (jaw cut down to one nest); [a2b](ideas/a2b-gang-press-stop-die.md) harvested dies; [a2d](ideas/a2d-by-hand.md) | XH nest (2.5 mm); steel jaw plates that can be cut down; a jaw layout photo in the listing | `SN-2549 crimping tool XH`, `ratchet crimper JST XH PH 2.5mm` |
| 10 | 12 V linear actuator, ≥300 N, 50 mm stroke | a2 walking head (closes the crimper's handles) | Force rating stated; limit switches built in | `12V linear actuator 50mm stroke 300N`, `mini linear actuator 2 inch stroke high force` |
| 11 | Small two-post guided die set (punch press die set) | a2b gang stroke in the shop press | Two guide posts with bushings; shoe size ~100 × 60 mm; fits under the VEVOR 12 t ram | `two post die set small punch press`, `mini die set guide post 100mm` |
| 12 | Air-over-hydraulic bottle jack, 12 t | a2b automated stroke (swap into the VEVOR press) | Fits the press frame; air input at 90–120 psi; pedal or valve that could be solenoid-driven | `12 ton air hydraulic bottle jack`, `air over hydraulic jack for shop press` |
| 13 | Diode laser engraver module, 5–10 W optical, 445 nm | a5 S5 strip test | Stated optical power; PWM input; fixed focus near 0.5 mm spot | `10W laser module 445nm engraver`, `5W optical laser head PWM` |
| 14 | Coin vibration motors, 3 V, 10-pack | [a2c](ideas/a2c-loose-contact-cassette.md) shaker loading | 10 mm coin, 3 V | `coin vibration motor 10mm 3V` |
| 15 | Smooth-jaw (no teeth) flat pliers, small | a5 S4 pinch-and-pull test | Smooth jaws with a small edge radius | `smooth jaw flat nose pliers`, `jewelry pliers smooth jaw` |

## Added in wave 2 (exchange on machine-that-sees-and-learns)

Items the exchange file
[`../../exchange/ribbon-as-pallet--on--machine-that-sees-and-learns.md`](../../exchange/ribbon-as-pallet--on--machine-that-sees-and-learns.md)
leans on. No amazon.com page was fetched to make this list.

| # | Item | Serves | Capability that matters | Search terms |
|---|---|---|---|---|
| 16 | Feeler gauge set, 0.02–1.00 mm, individual leaves | Stop-block shim stacks for v3 × a2b (crimp-height sweep in 0.02 mm steps) | Leaves marked by thickness; hardened steel; 0.02 mm steps at the thin end | `feeler gauge set 0.02 mm 32 blades`, `metric feeler gauge 0.02-1.00mm` |
| 17 | Non-insulated copper ring or fork terminals for 22 AWG, solderable, 100-pack | v3 coupons: far-end lug soldered to the stripped strands, hooked by a slotted fork for pull-to-failure | Bare tinned copper barrel that takes solder; ring or fork ≥3 mm hole | `non insulated ring terminal 22 AWG bare copper`, `bare copper fork terminal 22-16 AWG` |
| 18 | Small wire straightener, 5–7 rollers, for 1–3 mm wire | Removing spool curl from the ribbon end as it enters the pallet (calc §6 of the exchange) | Adjustable roller offset; groove or flat rollers that take a flat ribbon 7–15 mm wide | `wire straightener 7 roller small`, `wire straightening roller tool 1-3mm` |

## Added for the wave-2 ideas

Amazon candidates for the coordinator's Prime pass. No amazon.com page was
fetched.

| # | Item | Serves | Capability that matters | Search terms |
|---|---|---|---|---|
| 16 | Double-edge razor blades, 100-pack | [a7](ideas/a7-zip-station.md) nicker slivers, [a7b](ideas/a7b-plough-station.md) ploughshares, [a8b](ideas/a8b-spindle-with-touch-off.md) blade tips | ~0.10 mm stainless or carbon; plain (uncoated edge fine) | `double edge safety razor blades 100 pack`, `DE razor blades bulk` |
| 17 | Feeler gauge set with long, separate stainless leaves, 0.05–1.00 mm | [a7](ideas/a7-zip-station.md) tines filed to shape; [a8](ideas/a8-rolling-ring-scorer.md) bottom-blade height (0.25 mm leaf) | Individual leaves ≥100 mm long; stainless; thickness marked | `feeler gauge set 0.05-1.00mm stainless long blades`, `feeler gauge 12 inch blades` |
| 18 | Gauge pin set or drill blanks, 1.00–1.50 mm in 0.05 mm steps | [a8](ideas/a8-rolling-ring-scorer.md) top-blade height gauge (1.45 mm); [a8b](ideas/a8b-spindle-with-touch-off.md) score-radius gauge (1.10–1.20 mm) | Ground, diameter marked, ±0.005 mm or better | `pin gauge set 1.0-1.5mm`, `drill blanks 1.1mm 1.2mm 1.45mm` |
| 19 | 6700ZZ thin-section bearings (10 × 15 × 4 mm), 10-pack | a8b hollow spindle | Standard 6700ZZ | `6700ZZ bearing 10x15x4` |
| 20 | N20 gearmotor, 6 or 12 V, ~60–100 rpm, with encoder | a8b spindle drive | Encoder for turn counting; metal gears | `N20 gear motor encoder 100RPM`, `N20 micro gearmotor 12V 60rpm encoder` |
| 21 | GT2 timing belt (closed loop, 100–200 mm) and 16–20 T pulleys, 3 mm bore | a8b spindle belt | Closed loops in short lengths | `GT2 closed loop belt 158mm`, `GT2 16 tooth pulley 3mm bore` |
| 22 | Small 12/24 V solenoid air valve, 1/8 in ports | [a8](ideas/a8-rolling-ring-scorer.md) slug clearing on the DeWalt compressor line | Normally closed; rated ≥ 100 psi | `12V solenoid air valve 1/8 normally closed`, `mini pneumatic solenoid valve 24V` |
| 23 | Small LED light pad (A5 or smaller) | a7 split silhouette; a8 stub window | Even diffuse light; USB powered | `A5 LED light pad tracing`, `small LED backlight panel USB` |
| 24 | Module 0.5 gear rack pair and pinion | a8 pad drive (if printed ones are too coarse) | Steel or brass; rack length ≥ 50 mm | `module 0.5 gear rack`, `0.5M rack and pinion small` |
| 25 | Phosphor bronze sheet, 0.1–0.2 mm | a8b blade brush; nick-detector contacts | Spring temper | `phosphor bronze sheet 0.1mm`, `phosphor bronze shim stock` |
| 26 | Capsule slip ring, 6 circuits | [a4](ideas/a4-spool-as-magazine.md) spool's inner end as test port | ≥ 6 circuits; low noise; a non-Amazon source is Adafruit 736, $14.95 (procedure-is-the-machine) | `slip ring 6 wire 12.5mm capsule`, `6 channel slip ring 2A` |
| 27 | OTP XH 2.54 crimper-and-anvil ("knife set") without the applicator | [a2](ideas/a2-two-pallets-meet.md) C-frame head; [a2d](ideas/a2d-by-hand.md) hand frame | XH 2.5 mm side-feed dies; listings seen on eBay and AliExpress by terminal-supply (titles only) | `XH2.54 crimping die applicator knife`, `OTP applicator blade XH` |

Non-Amazon routes recorded in the idea files, not for the Prime pass:
- **Laser-cut stainless for the a7 tines.** JLCPCB 304 stainless stencils from
  $3, shipped in about a day (into-the-housing's key findings). Thickness
  options were not observed.
- **Wire-EDM or laser-cut tool steel** for a2's shear comb and a2e's shelf
  face: SendCutSend cuts mild steel up to 12.7 mm in 2–4 days
  (borrowed-machines); quick-turn wire EDM exists at ±0.05 mm (force-and-form).

## Wave 3

Amazon candidates for the coordinator's Prime pass, from the exchange
[`../../exchange/ribbon-as-pallet--on--force-and-form-w3.md`](../../exchange/ribbon-as-pallet--on--force-and-form-w3.md)
(combination K1). No amazon.com page was fetched. The other parts K1 names
(balls, magnets, toggle clamps, the NEMA 17 Tr8×2 motor, the 0.001 mm
indicator, the VEVOR AP-1 arbor press) already have confirmed Prime rows in
[`../../sourcing/amazon-prime.md`](../../sourcing/amazon-prime.md).

| # | Item | Serves | Capability that matters | Search terms |
|---|---|---|---|---|
| 28 | Precision ground tool-steel flat bar (O1 or A2), 1/8–1/4 in × 1/2 in × 6 in | K1's tack rail under the insulation barrels and the shear edge at the contacts' rear | Ground faces (thickness ±0.0005 in class); hardenable. force-and-form's #22 asks for the same family at 1/16 in | `O1 precision ground flat stock 1/4 x 1/2`, `ground flat stock tool steel 1/8 x 1/2` |
| 29 | Mold ejector pins, Ø1.0–1.5 mm, hardened | K1's heavy-station nest (lifts the box out of its slot) | Hardened, ground, headed; 40–80 mm long | `ejector pin 1.5mm`, `mold ejector pin 1mm SKD61` |

Added in the final pass, for the ideas as they stand. No amazon.com page was
fetched.

| # | Item | Serves | Capability that matters | Search terms |
|---|---|---|---|---|
| 30 | NEMA 23 stepper (≥1.9 N·m) with a DM542T-class driver, a second set | [a1](ideas/a1-pallet-tour.md), [a1c](ideas/a1c-crimp-upstream-first-park-after.md), [a4](ideas/a4-spool-as-magazine.md): the applicator's 15 mm crank with its feed kept (2.2–6 N·m at the shaft [procedure-is-the-machine exchange_ribbon_w3 §5]); the bench's own set is in the cap-weld tube rotator | Stated holding torque; driver current to 4.2 A; 24–48 V input. The 10:1 NEMA 23 planetary already has a Prime row | `NEMA 23 stepper motor 2.4Nm`, `DM542T stepper driver`, `NEMA 23 stepper driver kit` |
| 31 | Digital hanging (luggage) scale, 0–50 kg, 10 g resolution | Proof pulls by hand in [a2d](ideas/a2d-by-hand.md), [a10b](ideas/a10b-tacked-row-into-the-hand-tool.md), [a9](ideas/a9-reel-end-docks.md) stage 0 (20 N per conductor; pull-out to 39.2 N) | Peak hold; hook; 10 g steps | `digital luggage scale 50kg peak hold`, `hanging scale 10g resolution hook` |
| 32 | Hardened ground alloy dowel pins, 4–6 mm, h6 or m6 | Kinematic seats in a1b, a2, a2e, a9, a10 (the Prime dowel row is unhardened 304, which dents under 6 mm balls at 1,050–1,700 MPa [calc/final_w3.out.txt §1]) | Hardened (≥58 HRC) and ground; stated tolerance | `hardened dowel pins alloy steel 6mm m6`, `ground hardened dowel pin assortment metric` |

Earlier items still waiting for the Prime pass, which the ideas as they stand
still use (listed by name, since the earlier tables reuse some numbers):
double-edge razor blades (a7's nicker slivers, a7b, a8b); the small wire
straightener (a4, a9); 6700ZZ bearings and GT2 16–20 T pulleys with a 3 mm bore
(a8b); module 0.5 steel racks (a8); phosphor bronze sheet (a8b's brush, a2c's
ground leaves); precision ground tool-steel flat bar (the shear combs, a10's rail
and tack comb); mold ejector pins (a10's nest).
Items the ideas use that the Prime pass confirmed are cited in the idea files as
[Prime: …] rows of [`../../sourcing/amazon-prime.md`](../../sourcing/amazon-prime.md).
