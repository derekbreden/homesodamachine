# p5 Camshaft: one revolution per conductor

Sketches: [`../sketches/p5-camshaft-layout.svg`](../sketches/p5-camshaft-layout.svg),
[`../sketches/p5-cam-timing.svg`](../sketches/p5-cam-timing.svg) (both schematic).
Numbers: [`../calc/cam_drive.out.txt`](../calc/cam_drive.out.txt) (cited as
[calc cam_drive §n]), [`../calc/wave3.out.txt`](../calc/wave3.out.txt) (cited as
[calc wave3 §n]), force-and-form's
[`exchange_procedure_w3.out.txt`](../../force-and-form/calc/exchange_procedure_w3.out.txt)
(cited as [calc FP §n]).

The per-conductor procedure is laid out around one shaft, so that **the timing
diagram is the machine**. One slow motor turns one camshaft once per conductor,
~40 s a turn. Printed cams run the light motions: press the waiting conductors
down, capture *k*, strip, lay in, pull. A steel eccentric runs the punch. The
cassette from [p1](p1-cassette-and-benches.md) rides past like a typewriter
carriage: an escapement on the shaft advances it one key per turn, and bumps
moulded into the cassette's rack are its program. It collapses p1's benches A
and B (in the B-drop form) into one mechanism with one motor.

Branches: [p5b](p5b-camshaft-squeezes-the-hand-tool.md) (the shaft squeezes an
SN-2549), [p5c](p5c-camshaft-turns-a-knee.md) (the shaft turns a knee in a
small steel C, with [p1d](p1d-lift-once-fin-from-below.md)'s fin from below).

## Picture it: J2 in a cassette, keys 1–6 with key 3 blank

**Loading (person).**
- The person loads the J2 cassette as in p1: 3P-a and 3P-b in the clamp, key 3
  blanked, 3P-a's third conductor trimmed, the end trimmed at the cassette's
  blade slot.
- The person drops it onto the machine's carriage rail and presses start.
- The cassette's underside is a **ratchet rack** printed with it: one tooth per
  key at 2.5 mm, so the teeth line up with the comb by construction. Under key 3
  the rack carries a raised **skip bump**; after key 6 a taller **end bump**.

**One turn of the shaft** (angles illustrate the sequence [calc cam_drive §4]):

| Degrees | What happens | Driven by |
|---|---|---|
| 0–30 | escapement pawl advances the cassette one tooth (2.5 mm) | index cam + pawl |
| 30–70 | slotted presser drops the other conductors; a V-fork rises under key *k* to a fixed height and holds it 5–6 mm behind the strip line | printed face cams |
| 70–130 | V strip jaws close 2.4 mm from the tip, pull 3 mm, open; the slug drops | two printed cams |
| 130–150 | lay-in finger sets *k* into the open contact waiting on the fin; the fin reads *k* through the strands | printed cam |
| 150–170 | V-fork drops away; a spring leaf on the punch stack takes the wire hold | printed cam; leaf |
| 170–240 | punch descends: wings curl, then compaction; stop blocks meet at 236–240 | steel eccentric |
| 240–290 | punch rises | eccentric |
| 290–330 | camera frame; a hook drops behind the box and pulls 15–20 N with the punch up | switch cam; cam |
| 330–360 | presser lifts; a revolver pawl sets the next cut-free contact on the fin | cam + pawl |

**The contact on the fin is already cut free**, as in p1's B-drop form: the
presser drops neighbours where a side-feed strip's track, shear and scrap chute
would be.
- The fin is hardened steel standing 9–10 mm, stepped ~1.45 mm under the
  conductor barrel and 1.8–1.9 mm under the insulation barrel (JST's analog
  crimps 1.50 mm wide [mfr S14]). Free-topped it holds 5.1–6.3 kN [calc wave3
  §2].
- The contact is held on it by a 0.3 mm blade in its neck, fed one per turn by
  a revolver pawl on the shaft (hand-tool-as-press a2b), or sits on a one-pitch
  stub on a pin in its pilot hole.

**The fork opens before the stroke.** It holds the conductor behind the
contact's rear and drops away at 150–170°, so the punch stack never comes down
on it. Between 170° and 240° the open wings, the lay-in finger and a spring leaf
on the punch stack hold the conductor (the "wire hold spring" JST sells for its
MKS-L applicator).

**Key 3.** The skip bump lifts a lever as it arrives. The lever holds the
contact-feed pawl clear and pulls the pin that links the eccentric's rod to the
punch. For one turn the shaft does everything except feed a contact and crimp.
No software decides the empty cavity: the cassette carries the decision in
plastic, as its blanked key already does. A 12 V solenoid [Prime: Heschen
HS-0530B, $7.99] can do the same for looms whose cassettes lack bumps.

**End.** The end bump trips a switch that stops the motor at top dead centre.
The person swaps cassettes, or a magazine drops the next one.

**Knowing it worked.**
- Force against crank angle from foil gauges on the fin holder [Prime: BF350,
  $6.99] or a load cell under the whole lower die, fin holder and stops
  together, so it sits outside the stop loop [calc wave3 §4]. The HX711 at
  80 Hz takes ~190 samples through compaction at 40 s a turn [calc cam_drive
  §4]. A crimp with no wire, no contact or insulation in the barrel has a
  different curve; the stops show as a sharp rise in stiffness, and a crimp that
  climbs steeply before them is high (a doubled contact, a folded conductor).
- Identity at lay-in, through the fin and the far-end pogo block.
- The camera frame at 290° and the proof pull, logged with the cassette ID and
  tooth number.
- On a fail the switch cam stops the shaft at 330°, before the next index, and
  the person sees which key.

## Force: where it comes from and where it goes

- **Crimp height comes from stop blocks.** Steel stop blocks beside the punch
  meet at crimp height; the loop through punch holder, blocks and fin holder is
  ~30 mm of steel, ~670 kN/mm [hand-tool-as-press calc H §4]. Shims under the
  blocks set the height. ±300–600 N of force scatter then moves the height by
  ~±1 µm, against ±20–40 µm at 15 kN/mm with no stops.
- **With stops, a compliant outer loop is the design.** To be sure of reaching
  the stops, the eccentric is set to push past them by a margin *m*
  (0.02–0.10 mm) that covers frame creep, bearing play and shim error. Once the
  stops touch, the rest of the travel squeezes the loop outside them, so the
  frame carries the crimp plus k × *m* at bottom dead centre [calc wave3 §4]:

  | Loop outside the stops | *m* 0.05 | *m* 0.10 | A doubled contact (a rigid 0.2 mm), *m* 0.10 |
  |---|---|---|---|
  | 40 kN/mm | 4.4 kN | 6.4 kN | 14.4 kN |
  | 10 kN/mm | 2.9 kN | 3.4 kN | 5.4 kN |
  | 5 kN/mm | 2.7 kN | 2.9 kN | 3.9 kN |

  (Crimp 2.43 kN, the high case.) So the outer frame, printed or plate, is
  allowed to be springy at 5–10 kN/mm: it pays 1.05–1.4× the crimp every stroke
  and caps a doubled contact at 3.9–5.4 kN by itself. If the frame turns out
  stiffer, one or two DIN 2093 A25 disc springs in the rod, unpreloaded, bring
  the loop to 3–6 kN/mm [calc wave3 §4; assumption: DIN 2093 table values].
  A preloaded stack is not wanted: preload sets a floor that every stroke
  reaches.
- **Drive.** e = 2.5 mm with a 40 mm rod gives a 5 mm stroke, room over the open
  2.75–3.2 mm insulation wings plus the lay-in finger [xh-facts §1 clone
  drawings]. With the frame's wind-up counted, the peak shaft torque is
  1.0–2.3 N·m for loops of 2–40 kN/mm [calc FP §3]. Candidates:
  - a 12 V self-locking worm gearmotor, 40 kg·cm (3.9 N·m), 10 rpm, with an
    AS5600 on the shaft for angle [Prime: Greartisan, $26.99; Prime: AS5600,
    $7.99 for three];
  - a NEMA 17 with a 26.85:1 planetary, 3 N·m permissible, not self-locking
    [Prime: STEPPERONLINE 17HS19-1684S-PG27, $41.91]; the stepper holds
    position while powered;
  - a NEMA 17 worm-gear stepper had no Prime listing [Prime: "NEMA 17 worm-gear
    stepper", none found].
- **Energy per crimp** ~0.13–0.48 J over ~2.4 s [digest; calc cam_drive §4].
- **An obstruction.** The eccentric alone is a displacement source that reaches
  bottom dead centre whatever is in the way; a bare stiff frame would put
  10–20 kN into a doubled contact. The compliant loop caps it (table), a
  switch on the rod spring's travel (if fitted) stops the shaft, and the
  stepper's current limit or the gearmotor's current sense is a second guard.
- Printed parts carry only the light cams, under ~50 N.

## What locates what

| Moment | Located | Against |
|---|---|---|
| Index | cassette | its own rack tooth and the escapement pawl, then the fork |
| Strip, crimp | conductor *k* | V-fork on the frame, rising from below |
| Crimp | contact | fin and neck blade |
| Crimp height | punch | steel stop blocks (shimmed), in a short steel loop |
| Timing | every motion | shaft angle, fixed by the cams |

"Fixed" for position is the frame and the shaft; for crimp height, the stop
blocks' loop alone. The cassette's rack is printed: ±0.05 mm per tooth, perhaps
accumulating over nine teeth [estimate]. It only has to bring *k* inside the
fork's capture; the fork sets position.

## Steps it covers, and what it hands back

- **Covered:** strip, place the contact on the conductor, crimp, look, proof
  pull, identity, index and skip, per conductor. Trim is done at the cassette's
  blade slot by hand lever or a trim bench.
- **Handed back:** cut, peel, load and trim the cassette; supply cut-free
  contacts to the revolver; insert (or bench C); label.
- **Minutes:** p1's person time, ~36 min a unit; the shaft runs ~50 min a unit
  with a cassette magazine [calc person_timeline]. The number of calls on the
  person is the same as p1's.

## Printed and bought

- **Printed:** face cams (PET-CF) and follower levers; presser, fork, lay-in
  finger, strip-jaw carriers; carriage rail; cassettes with racks and bumps.
- **Steel:** the stepped fin and a punch (p1's B-drop routes), stop blocks and
  shims, the eccentric and rod, the plate for the stop loop.
- **Bought** (Prime rows observed 2026-09-28): the gearmotor or planetary
  stepper above; HK1010 needle bearings for the eccentric [Prime: uxcell
  HK1010, $7.79]; 20 mm pillow blocks [Prime: XIKE UCP204, $26.99]; foil gauges
  or a load cell with HX711; roller micro switches [Prime: $5.99]; the 12 V
  solenoid (optional); disc springs only if the frame is stiffer than wanted
  (the Prime Belleville assortment is light-duty stainless [Prime: Hilitchi
  M3–M12]; a DIN 2093 A25 is a catalogue part, not Prime-confirmed).

## Problems, and what answers each

1. **"A camshaft cannot adapt."** It adapts through the cassette: blank keys and
   end bumps are the program, and a different loom is a different cassette.
   What it cannot change is the sequence within a turn: a new strip method means
   new cams.
2. **Printed cams wear.** Under ~50 N at one turn per 40 s, ~53 turns a unit and
   ~3,200 over the program, printed PET-CF under a ball-bearing follower should
   outlast the program [assumption]. The eccentric is steel because it carries
   kilonewtons.
3. **Stops cost surplus force every stroke.** Only in a stiff loop (above); the
   compliant loop is the answer.
4. **Where the load cell goes.** Between the fin and its holder it would sit
   inside the stop loop and move crimp height by ±3–12 µm with force scatter
   [calc wave3 §4]. Under the whole lower die, or as gauges on steel, it does
   not.

## Contribution

- The most literal answer to "the procedure is the machine": a timing diagram cut
  into cams, one motor, no coordination software.
- **The cassette's rack as escapement and program**: the carrier indexes itself
  at its own pitch and tells the machine where the empty cavity is. p1 and p1b's
  slides can read the same bumps as a backstop to the cassette ID.
- **Stops and a soft loop together**: height from the stops, the surplus and
  the obstruction force both set by the loop's softness, the drive at 1–2.3 N·m.
  Any design here is limited by the stop loop and the dies, not by the drive.
- **What a dead stop is and is not.** An applicator's crimp height is also a
  position: its crank's bottom dead centre plus a wedge (JST's CDS applicator
  has dial crimp-height adjustment [xh-facts §2]; an OTP-standard one a wedge
  in 0.02 mm steps [force-and-form, source crimpapplicator.com]). What differs
  between stop blocks and a dial is that a dead stop takes surplus force and a
  kinematic bottom takes none. [p5c](p5c-camshaft-turns-a-knee.md) is the
  kinematic-bottom branch.

## Major unresolved problems

- **The die profile.** The punch's shape and the stepped fin decide the crimp;
  the stops only set its height. Where the steel comes from is force-and-form
  f7's open list.
- **The fin and a cut-free contact supply** (p1, B-drop).
- **Set in waiting conductors** from the presser, as in p1's B-drop: capture
  from below at every key and a 25–30 mm split.
- **Stripping** as everywhere; the strip-pull cam has to allow for silicone's
  stretch, and may need more than 3 mm.
- **Accumulated rack error** on long cassettes (J1, nine teeth) against the
  fork's capture, ±1 mm or so [estimate].
- **The proof pull's reaction** through the cassette clamp (p1's clamp stop sets
  a 15–30 % squeeze [calc FP §4]).

## What rests on assumptions

- Motor torque, gear efficiency, eccentric and rod dimensions.
- Crimp force and compaction travel [xh-facts §4], themselves estimates.
- The margin *m* and the frame's stiffness.
- Printed cam life.
