# Sourcing requests: change-the-question

Amazon candidates for the coordinator's Prime-confirmation pass. No amazon.com
page was fetched and no Chrome tool was used. Web search was unavailable to
this explorer (the session's search budget was spent), so there are no lead
ASINs. Search terms are given instead. Items already in the context list
([`../../context/sourcing-requests.md`](../../context/sourcing-requests.md))
are not repeated: load cell with HX711, crimp micrometer, JST WC-110, SO-101
kit, and the others.

| Item | Idea | Capability that matters | Search terms |
|---|---|---|---|
| RC LiPo balance extension leads / pigtails, JST-XH, silicone wire | [c2](ideas/c2-buy-the-crimp.md) (b) | **22 AWG** (not 24/26); silicone jacket; lengths 300–600 mm; XH-4 (3S), XH-5 (4S), XH-6 (5S), XH-7 (6S), XH-9 (8S). Record gauge, length, wire colours, and whether wires are bonded flat | `JST-XH balance extension 22AWG silicone 50cm`, `3S balance lead extension 22AWG`, `6S JST XH balance cable 22 AWG`, `8S balance lead XH` |
| Pre-crimped single XH wires (contact crimped on one end) | [c2](ideas/c2-buy-the-crimp.md) (c) | 22 AWG; silicone preferred; black preferred; 300–600 mm; bag quantity | `XH2.54 pre-crimped wire 22AWG`, `JST XH crimped wire single end 22 AWG silicone` |
| XH-mating IDC ("puncture", "piercing") housing, 2.5 mm pitch | [c4](ideas/c4-parts-that-mate-the-wafer.md) | Must mate a B*B-XH-A wafer (box shroud, 2.5 mm, not 2.54 mm KK); IDC slot range covering 1.7 mm OD and fine-stranded 22 AWG. Not found in JST's catalog; a third-party part is unconfirmed | `XH2.54 IDC connector`, `2.5mm pitch IDC wire to board connector XH compatible`, `XH puncture connector no crimp` |
| JST XH extraction / pin removal tool | [c2](ideas/c2-buy-the-crimp.md) (J2 cavity 3) | Releases the XH contact lance through the housing window. Genuine XJ-06 is $63.69 at Digi-Key [xh-facts §2] | `JST XH pin removal tool`, `terminal extraction tool JST XH` |
| HSS square tool blanks, 3 mm or 1/8 in | [c1](ideas/c1-half-rows.md) anvil blade; [c1b](ideas/c1b-tack-first.md) anvil strip | Hardened M2/M42 HSS, ground; 3 × 3 mm or 1/8 in square, 50–100 mm long | `HSS tool blank 1/8 square`, `3mm square HSS lathe tool bit blank` |
| MGN9 or MGN12 linear rail with carriage, 100–200 mm | [c1](ideas/c1-half-rows.md) ram carriage, pallet slide | Preloaded carriage; H-type; short lengths | `MGN12H linear rail 150mm`, `MGN9 rail carriage 100mm` |
| Ball screw SFU1204 or T8 lead screw kit, short | [c1](ideas/c1-half-rows.md) ram; [c1b](ideas/c1b-tack-first.md) tack stroke | ~3 kN at bottom dead centre for c1 (ball screw); a few hundred N for c1b (lead screw is enough) | `SFU1204 ball screw 150mm kit`, `T8 lead screw 100mm nut` |
| Toggle clamp, push-pull, ~100 kgf | [c1b](ideas/c1b-tack-first.md) manual tack stroke | Adjustable stop; push-pull plunger | `push pull toggle clamp 100kg` |
| Solder wire feeder, or a spare 3D-printer extruder for 0.5 mm solder | [c3](ideas/c3-fold-and-solder.md) | Meters 0.5 mm flux-core wire in 1 mm steps | `solder wire feeder stepper`, `automatic solder feeder` |
| 0.5 mm flux-core solder, no-clean | [c3](ideas/c3-fold-and-solder.md) | 0.5 mm diameter; low-flux-percentage option | `0.5mm no clean flux core solder` |

## Wave 2

Status of the wave-1 rows after the coordinator's Prime pass
([`../../sourcing/amazon-prime.md`](../../sourcing/amazon-prime.md), observed
2026-09-28): balance leads (22 AWG silicone, 200–300 mm only), pre-crimped
22 AWG silicone singles (mixed colours, length unstated), the XH extraction
tool (JRready, thin), the HSS blanks, the MGN12/MGN9 rails, the SFU1204 ball
screw, the POWERTEC toggle clamp, 0.5 mm solder and a solder-feed gun are
Prime-confirmed. No XH-mating IDC housing was found.

New rows, for [c6](ideas/c6-pre-form-the-contact.md) and
[c6b](ideas/c6b-by-hand-this-week.md) (pre-forming contacts) and
[c1c](ideas/c1c-crimp-in-the-row.md):

| Item | Idea | Capability that matters | Search terms |
|---|---|---|---|
| Gauge-pin set covering 1.40–1.70 mm in 0.01 or 0.05 mm steps | c6 go/no-go on the keyhole bore; sizing the mandrel | Steel pins, individually marked, ±0.002–0.005 mm class; a partial set spanning 1.40–1.70 is enough | `pin gauge set 1.0-2.0mm`, `plug gauge pins 0.01mm steps`, `precision pin gauge set small diameter` |
| Drill blanks or dowel pins, Ø1.55 and Ø1.60 mm | c6 mandrel | Hardened, ground, 20–40 mm long; a jobber drill's shank also works | `drill blank 1.6mm`, `1.55mm drill bit HSS` (shank as mandrel), `1.6mm dowel pin hardened` |
| Metal-gear hobby servo, 25–35 kg·cm | c6 pre-former lever | Metal gears, ~180°, 5–7 V; torque at 6 V stated | `35kg servo metal gear`, `25kg digital servo metal gear` |
| Precision ground flat stock, O1 or A2, ~3 × 12 mm | c6 nest, c1c box front stop and anvil block | Ground to ±0.02 mm; short lengths | `O1 ground flat stock 1/8 x 1/2`, `precision ground flat stock tool steel` |
| Small spring assortment (compression, 3–5 mm OD) | c1c carriers sprung forward to the box front stop | Light rate, ~0.1–0.5 N at a few mm | `small compression spring assortment 3mm OD` |

Not for Amazon: stainless stencil sheet for laminated carrier walls and nest
plates (JLCPCB stencil service, from $3, ~24 h, per into-the-housing's
source).

## Wave 3

From the exchange with into-the-housing
([`../../exchange/change-the-question--on--into-the-housing-w3.md`](../../exchange/change-the-question--on--into-the-housing-w3.md)).
The Prime-confirmed Accusize pin set stops at 1.52 mm, and the Prime header
listing states no pin section or material [`../../sourcing/amazon-prime.md`].

| Item | Idea | Capability that matters | Search terms |
|---|---|---|---|
| Gauge pins 1.45–1.75 mm (single pins or a partial set) | [c6](ideas/c6-pre-form-the-contact.md), [c6b](ideas/c6b-by-hand-this-week.md): the mandrel (0.08–0.12 mm under the measured jacket, plus springback: 1.56–1.57 mm for a 1.70 mm jacket) and the go and no-go pins (1.57 and 1.62–1.65 mm for a 1.70 mm jacket) [calc wave3 §3] | Hardened, ground, marked; ±0.002–0.005 mm class; 0.01 mm steps | `pin gauge set 1.5-2.0mm`, `plug gage pins 0.060-0.080 inch`, `1.60mm gauge pin` |
| Hardened steel square pins, 0.64 mm (0.025 in), ≥17 mm long | into-the-housing i6b post bed (S2's end), i2d″ steel pocket post | Steel, not brass: stiffness 0.06 mm per N at 8 mm free against 0.12 for brass [calc on_into_the_housing_w3 §10] | `0.025 inch square steel wire`, `0.64mm square steel pin`, `square music wire 0.025` |

Further rows for the settled files (c6, c6b, c7):

| Item | Idea | Capability that matters | Search terms |
|---|---|---|---|
| 22 AWG silicone flat ribbon, 6, 7, 9 or 10 conductors | [c7](ideas/c7-straight-across.md) (c): one loom, one ribbon | Same construction as the BNTECHGO 3P/4P/5P on hand (60 × 0.08 mm tinned strands, 1.7 mm per conductor, black); record conductor count, pitch, spool length, and whether the web peels | `22AWG silicone flat ribbon cable 7 pin`, `BNTECHGO 22 AWG silicone ribbon 10 pin`, `22 AWG parallel silicone wire 9 pin black` |
| Ground tool-steel or HSS flat, ~1.5 × 3 mm section | [c6](ideas/c6-pre-form-the-contact.md): the blade mandrel (1.5–1.6 × ~2.5 mm) | Hardened and ground; a 1.5 mm key or tool bit that needs only one face ground | `1.5mm HSS flat tool bit`, `1/16 x 1/8 ground flat stock`, `HSS parting blade 1.5mm` |

Already Prime-confirmed and cited in the files [`../../sourcing/amazon-prime.md`](../../sourcing/amazon-prime.md): the Heschen HS-0530B 12 V push-pull solenoid (c1, c1c retracting stop), the Engineer PA-09 (c6b's fallback when the SN-2549 opens too little), the Wago 221-415 far-end block and 6-circuit slip ring (c1c electrodes), the DS3235 35 kg·cm servo (c6 pre-former), and the HSS 3 × 3 mm blanks (anvils, jaws).
