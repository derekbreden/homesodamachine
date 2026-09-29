# p4b Two heads, one person: the person's pace sets the rhythm

Sketch: [`../sketches/p4b-two-heads.svg`](../sketches/p4b-two-heads.svg)
(schematic timeline). Numbers: [`../calc/wave2.out.txt`](../calc/wave2.out.txt) §4
(cited as [calc wave2 §4]), force-and-form's
[`exchange_procedure_w3.out.txt`](../../force-and-form/calc/exchange_procedure_w3.out.txt)
(cited as [calc FP §n]).

**A branch of [p4](p4-person-presents-machine-takes.md), and a combination.** p4's
division of labor stays: the person presents each conductor and inserts each
contact; the machine strips, places the contact, crimps, checks and keeps the
order. What changes is the number of machines: two slow crimp heads side by side,
and the person alternates between them. While head A works on conductor *k*, the
person presents *k*+1 to head B and inserts the crimp head A finished before.

Sources, by name:
- hand-tool-as-press [a1](../../hand-tool-as-press/ideas/a1-squeezer-cradle.md)'s
  squeezer and [a2b](../../hand-tool-as-press/ideas/a2b-gravity-tool-flat.md)'s
  revolver, and its observation that a second head is cheap only because the head
  is a ~$22 hand tool;
- borrowed-machines [b2b](../../borrowed-machines/ideas/b2b-pedal-less-hand-station.md),
  that squeezer developed as one station with a separate strip nozzle;
- into-the-housing [i5](../../into-the-housing/ideas/i5-person-inserts-on-a-sensing-nest.md),
  the sensing insertion nest between the two heads.

## Picture it: J1, nine conductors, two heads

**The bench.** A plate ~500 × 250 mm in front of Derek, left to right:
- **Head A.** A funnel ending at a grounded steel **tip stop** with a beam, a soft
  TPU clamp on a small slide, V-jaws for the strip (or b2b's strip nozzle), and the
  SN-2549 [Prime: iCrimp SN-2549, $22.29] on its side in a1's cradle with a NEMA 17
  Tr8×2 pusher [Prime: $27.99] and a load cell [Prime: bar load cell with HX711,
  $9.99]. The tool's jaws close normal to the plane the person holds the ribbon in,
  so the crimp comes out upright.
  - Contacts come cut free from a revolver of loose kit contacts, one per cycle
    (a2b), or from a post (terminal-supply x1). Each sits in the nest with a 0.3 mm
    blade in its neck against the box's rear face; the pusher closes only until the
    upper jaw's flare touches the wing tips, so the wings stay open.
  - The funnel is a V-trough open at the top, so a crimped conductor lifts out
    upward between the opened jaws.
- **The insertion nest** in the middle: i5's header board, the XHP-9 plugged onto a
  B9B-XH-A whose posts are ESP32 inputs, an LED under each cavity, a
  spring-limited lever with a slotted blade.
- **Head B**, the mirror of head A.
- **The far end.** On a cut loom its cut face sits in a pogo block
  (ribbon-as-pallet a6; P75 pins [Prime: $6.49]); at
  [p6](p6-spool-end-bench-that-grows.md)'s reel the hub lead does the same job.
  Every conductor is a wire to the ESP32.
- **A strip of LEDs** above the bench shows the ribbon cross-section, with the next
  conductor lit and an arrow to the head it goes to.

**The rhythm.**
1. **Present 1 to A.** The person pokes conductor 1 (lit, arrow left) into head A's
   funnel until its copper face touches the grounded tip stop. The stop reads
   continuity to far-end conductor 1: A knows this is the right one before
   anything is cut. A wrong conductor gets a red light, and nothing moves. A's
   clamp takes it; the person lets go.
2. **Present 2 to B**, the same on the right.
3. **A's cycle, ~20–35 s** [estimate]: strip 2.4 mm by clamp-and-pull; a backlit
   frame reads the bare length; the revolver drops a contact into the open nest and
   the pusher closes to wing touch; the clamp feeds forward to the depth the
   camera's reading asks for (the tips stay short of the blade by design); the
   pusher completes the ratchet, logging the curve; the pusher opens to the blade
   and the clamp pulls 20 N through the box; green, jaws open.
4. **Insert 1, present 3.** The person lifts conductor 1's crimp out of A's trough
   and starts it into cavity 1, which is lit. The lever seats it; blade → contact →
   post 1 names the cavity, and a tug proves the latch (i5). The person then
   presents conductor 3 to A, which is free again.
5. And so on: odd conductors to A, even ones to B. The person is always inserting
   one crimp and presenting the next.

**J2.** Key 3 never lights, and 3P-a's third conductor is trimmed when the lights
ask. **J4 and J7.** The person's hands make the crossing at insertion; the tip
stop's identity check at presentation and post continuity at insertion confirm it
twice.

## Minutes

From one task library [calc wave2 §4; estimates]. Today by hand: ~46 minutes.
Fixed per unit: cut, peel, test and label.

| Head cycle | One head | Two heads | Person waits per conductor, two heads |
|---|---|---|---|
| 20 s | 37 min | 28–33 min | 0 s |
| 26 s | 42 min | 30–33 min | 0–3 s |
| 35 s | 50 min | 34 min | 1.5–7.5 s |
| 45 s | 59 min | 39 min | 6.5–12.5 s |

(Present 4–6 s, insert 6–10 s.) One head saves minutes only if its whole cycle is
shorter than the ~31 s of a hand strip, crimp and insert. Two heads make the
person's own present-and-insert pace the rhythm for any cycle up to about twice
that pace: two 30 s machines do what one 15 s machine would.

## What locates what

| Moment | Located | Against |
|---|---|---|
| Present | tip; identity | grounded tip stop and beam at the funnel's end |
| Take | conductor | head's soft clamp: tip offset now known |
| Place | contact | SN anvil nest (lateral, roll) and neck blade (axial) |
| Feed | insulation edge | clamp's forward stop, corrected by the camera's bare length |
| Crimp height | dies | the SN-2549's own dies, if they bottom |
| Insert | cavity | i5 header post continuity |

"Fixed" is each head's plate for its own work, and the nest for insertion.

## What drives the crimp and carries its force

Each head's NEMA 17 on its SN's own handle; the loop closes inside each tool. The
plate, clamps and revolvers carry positioning loads.

## How it knows it worked

Identity at presentation, the force curve per head, the camera frame, the 20 N pull
through the box, and at insertion the cavity's post continuity and the latch tug.
The log keeps the head with every crimp.

## Steps it covers, and what it hands back

- **Automated:** strip, place the contact on the conductor, crimp, force curve,
  proof pull through the box, identity before stripping, the order (lights), cavity
  identity and latch at insertion.
- **Handed back:** cut and peel; present each conductor; insert each contact with
  the lever; fill the revolvers; label.

## Printed and bought

- **Printed:** two cradles, two funnels and troughs, two clamp slides, two
  revolvers, the i5 nest body, the pogo block.
- **Bought** (Prime rows observed 2026-09-28 unless a source is named): two
  SN-2549s ($22.29 each); two NEMA 17 T8×2 ($27.99 each); two bar load cells with
  HX711 ($9.99 for two sets); small servos for clamps, jaws and revolvers [Prime:
  MG90S, $13.88 for four]; B4B–B9B-XH-A headers [source: findchips via
  into-the-housing] or the CQRobot kit's headers; P75 pogo pins ($6.49). Roughly
  $150–250 beyond what the bench has [estimate].

## Problems, and what answers each

1. **Two tools crimp to two heights.** Each SN-2549's dies set its own height, if
   they bottom; the log keeps the head with every crimp; five crimps per head under
   a caliper at the start of a session show whether the two differ. A difference
   inside the window is harmless; one outside it retires that tool's jaws.
2. **The person loses track of which head has which conductor.** The lights say
   which conductor and which head; the tip stop refuses a wrong conductor before
   anything is cut; the nest's post continuity refuses a wrong cavity.
3. **A failed crimp on one head strands the other head's work.** A bad crimp means
   the whole ribbon end is cut back ~6 mm and restarted [calc recovery_length §1],
   taking the other head's crimps on that end with it: 6 mm of loom on a cut loom,
   6 mm of reel at p6.
4. **The crimp cannot come back out through the funnel** (a 1.95 × 2.4 mm box
   against a 1.9 mm funnel). The funnel is a V-trough open at the top; the crimp
   lifts out upward between the opened jaws, as in hand use.
5. **The proof pull's reaction** passes through the soft clamp on the jacket; the
   clamp's stop sets a 30 % squeeze over its 8–10 mm so the copper does not creep
   and fail a good crimp [calc FP §4]. At a reel the reel anchors it.

## Contribution

- **Two slow machines, not one fast one.** The person's rhythm sets the pace.
  Attended minutes fall to ~28–39 a unit against ~46 by hand, with every crimp
  logged, pulled and identity-checked.
- **It only works because the head is cheap**: a ~$22 hand tool closing its own
  force loop. With applicator heads it would cost two applicators.

## Major unresolved problems

- **Whether a 20–35 s head cycle is reachable**, including strip and contact drop;
  at 45 s the person waits 6–12 s per conductor.
- **Clamp-and-pull stripping of silicone**, twice.
- **Kit contacts dropping through a revolver** (hand-tool-as-press a2b's problem),
  twice.
- **The neck length** for a blade that the tips must not reach when the camera sets
  depth: 0.70–0.90 mm needed [calc FP §5]; with a shorter neck the feed stops at
  touch-off instead.
- **Bench width**: two heads and a nest within one person's reach.

## What rests on assumptions

- Head cycle, present and insert times [estimate].
- That two SN-2549s from one listing crimp alike, checked by sample.
