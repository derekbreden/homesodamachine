# p4 The person presents, the machine takes

Sketch: [`../sketches/p4-present-and-take.svg`](../sketches/p4-present-and-take.svg)
(schematic side view). Numbers: the first calcs in [`../calc/`](../calc/) by name,
[`../calc/wave2.out.txt`](../calc/wave2.out.txt) (cited as [calc wave2 §n]),
force-and-form's
[`exchange_procedure_w3.out.txt`](../../force-and-form/calc/exchange_procedure_w3.out.txt)
(cited as [calc FP §n]).

The smallest machine that does the step Derek most wants automated: a shoebox
station with a funnel.
- **The person** does what hands are good at: holds the loom, splays the
  conductors, pokes one into the funnel, inserts the finished contact into the
  housing.
- **The machine** does what hands are bad at: finds the tip, grips the conductor,
  strips it, puts it into a contact it has already located, crimps it the same way
  every time, and keeps the order: which conductor is next, which cavity it goes
  in.

The division of labor is the design. [p4b](p4b-two-heads-one-person.md) is the
branch with two heads, where the person's minutes fall.

## Picture it: J1, 5P + 4P into an XHP-9

**Before the station.** The person cuts the two ribbons square with a printed
square guide, as in today's step 1 [repo], and peels ~30 mm. A square cut means
every conductor's tip is at the same length: from here **the tip is the
reference.**

**At the station.**
- The person picks "J1" on the station's small screen, or scans the loom label.
- An LED lights **conductor 1** on a printed diagram of the ribbon pair.
- An XHP-9 sits in a printed nest on the station's front with an LED under each
  cavity, the way Yazaki's light-guided insertion shows the next cavity
  [prior-art §5].

**One conductor.**
1. **Present.** The person pokes conductor 1 into the funnel until its tip meets a
   hard stop and breaks a light beam [Prime: IR break-beam pair, 3 mm, $9.99]. The
   person's accuracy only has to be ±2 mm laterally and "all the way in".
2. **Take.** A soft clamp (TPU-padded V jaws on a small slide) closes on the
   insulation ~10 mm behind the tip. Its hard stop sets a 30 % squeeze of the
   jacket over its 8–10 mm, enough for the copper not to creep inside the jacket
   under the proof pull [calc FP §4]. Since the tip was at the stop, the machine
   now knows where the tip is relative to its clamp, and the person lets go.
3. **Strip.** The stop swings clear. V-jaws close 2.4 mm from the tip [mfr S6];
   the clamp slides back 3 mm, pulling the conductor out of its slug; the jaws
   open; the slug drops.
4. **Place.** The station takes one of two forms. Each says where the contact
   comes from and how the crimp leaves.
   - **Strip form.** A shuttle carries a short strip track and a small reel of
     100–200 contacts, and brings the **pre-fed contact** under the work line:
     box forward, barrels open, the carrier running across behind the insulation
     barrel. The V lead-in is a printed upper half whose floor is the carrier
     itself: the carrier is flat and lies in the contact's floor plane [xh-facts
     §1], so the insulation rides on its top face and the strands enter 0.5 mm
     above the conductor barrel's floor, inside its 1.68–1.90 mm open U. After
     the stroke has sheared the tab, the upper lead-in half swings up and the crimp
     leaves upward out of the anvil.
   - **Squeezer form** (hand-tool-as-press
     [a1](../../hand-tool-as-press/ideas/a1-squeezer-cradle.md)). The contact
     arrives cut free, from a revolver of loose kit contacts (hand-tool-as-press
     a2b) or a post (terminal-supply x1). It sits in the SN-2549's XH nest with a
     0.3 mm blade in its neck bearing on the box's rear face. The pusher closes
     only until the upper jaw's flare touches the wing tips, **short of the first
     ratchet tooth**: at that tooth the wing tips are pinched to 1.4–1.6 mm, and a
     1.7 mm jacket meets them edge-on unless the barrel floor is 1.9 mm or wider
     [force-and-form calc wave2 §1]. The tool lies so its jaws close normal to
     the plane the person holds the ribbon in, and the crimp comes out upright.
   - In either form the clamp then slides forward to a hard stop, and the stripped
     end runs axially into the open barrels, as a hand tool's wire goes to its
     wire stop [prior-art §3, WC-110 procedure]. The hard stop sets where the
     insulation edge lands; the chain is tip at the stop, the clamp's grip, the
     clamp's forward stop. A backlit camera frame of the tip after the strip can
     correct the forward stop by the measured bare length [calc wave2 §3].
5. **Crimp.** Strip form: a slow ram (a NEMA 17 on a lead screw and toggle)
   drives the punch to a stop in a short steel loop, logging force and position,
   and the tab shears in the stroke. Squeezer form: a NEMA 17 on a Tr8×2 screw
   [Prime: NEMA 17 with integrated T8×2 lead screw, $27.99] completes the ratchet
   cycle through a load cell [Prime: bar load cell with HX711, $9.99].
6. **Check.**
   - **The proof pull goes through the box, with the dies open.** The punch rises
     (or the squeezer opens to the blade), a blade or hook bears behind the box's
     rear face, and the clamp pulls back against a spring set to 15–20 N, well
     under JST's 39.2 N minimum [xh-facts §1]. Pulling while the dies still held
     the barrels would test 30–400 N of die friction, not the crimp
     (hand-tool-as-press).
   - The camera takes a frame.
   - Green, and the clamp opens. On a fail, red, and the contact is cut off at the
     station's side cutter.
7. **Insert.** The person pulls the crimped conductor out, and the LED under
   **cavity 1** lights. The person pushes the contact home until it clicks; a light
   tug confirms. The station lights conductor 2.

**While the person inserts contact *k*−1, the station is already working on
conductor *k*.** The person's hands and the machine are one conductor apart.

**J2.** After conductor 2 (FAN) the station skips to 3P-a's third conductor, tells
the person to trim it, and lights 3P-b's first conductor for cavity 4. Cavity 3's
LED never lights. **J4.** At cavity 2 the station asks for the 3P's first
conductor (GND). Crossings cost nothing here: the person inserts every contact,
and the station only has to know the order.

## What locates what

| Moment | Located | Against |
|---|---|---|
| Present | tip | hard stop and light beam (frame) |
| Take | conductor | station clamp: tip offset now known |
| Strip | strip line | V-jaws on the frame, 2.4 mm from the stop |
| Place | tip in the barrels | clamp's forward hard stop + V lead-in, corrected by the camera |
| Crimp | contact | strip form: anvil and strip track; squeezer: SN nest and neck blade |
| Crimp height | dies | strip form: stop in a short steel loop; squeezer: the SN's own jaws |

"Fixed" is the station frame. The only thing the person contributes to position
is "tip at the stop". The only reference that travels is the clamp's grip, over
~10 mm and two short moves.

## What drives the crimp and carries its force

Strip form: the ram's motor through a toggle into a punch, the loop closed through
the station's steel frame and its stop. Squeezer form: the NEMA 17 on the SN's own
handle, the loop closed inside the tool.

## How it knows it worked

The force curve against position, the camera frame, the proof pull through the
box, and the order lights (J2's skip, the crossings as lights).

## Steps it covers, and what it hands back

- **Automated:** strip, place the contact on the conductor, crimp, check, and the
  order.
- **Handed back:** cutting square, peeling, presenting each conductor, inserting
  each contact, labelling.
- **Minutes.** One station saves no minutes unless its cycle is shorter than a
  hand crimp. At ~40 s a cycle the person is present for ~54 min a unit and busy
  for ~30 of them; today's estimate by the same method is ~46 [calc
  person_timeline]. What it buys is the fiddly, skill-dependent part done
  identically every time, with a force curve, a frame and a pull for every crimp.
  Idle gaps can hold far-end work. p4b is where the minutes fall.

## Why build it early anyway

- **It is where the crimp gets tuned with a person watching**: force curves,
  bottom height, strip length and the camera's judgement are learned one crimp at
  a time before any machine is trusted alone.
- **It is p1's bench B in waiting.** Turned to face a lead-screw slide instead of a
  person, the same funnel, clamp, strip jaws, contact supply and crimp head take
  conductors from a cassette's lifted key.
- **It works on day one with loose kit contacts** if the squeezer's nest takes a
  contact the person drops in; that puts the person's hands on the contact again.

## Printed and bought

- **Printed:** frame body, funnel, clamp jaws with TPU pads, stop flag, strip-jaw
  carrier, anvil shuttle body or tool cradle, housing nest with LED windows,
  ribbon diagram panel.
- **Bought** (Prime rows observed 2026-09-28): two or three small steppers or
  servos (clamp slide, strip jaws, shuttle) [Prime: MG90S, $13.88 for four];
  the NEMA 17 T8×2 ($27.99); IR break-beam ($9.99); load cell and HX711 ($9.99);
  ring light [Prime: AmScope LED-144W-ZK, $35.99]; LEDs; the ELP camera (on hand).
  Strip form: a narrow anvil and punch (made or harvested; see p1's B-drop steel)
  and contacts on strip [xh-facts §6]. Squeezer form: a dedicated SN-2549 [Prime:
  $22.29].

## Problems, and what answers each

1. **"If the person presents the conductor, the person's placement sets the
   crimp."** The tip at the stop sets it; the person only has to get the conductor
   into the funnel.
2. **Squeezing silicone in the clamp and pulling 3 mm may just stretch the
   insulation.** The clamp's grip is 8–10 mm on a TPU V against a 2.4 mm slug; if
   the pull stretches the jacket behind it, the strip line walks, which is the
   axial-window risk again [calc transfer_capture §3]. Untested; the camera's
   bare-length reading is the check.
3. **The person's tug on the loom disturbs the machine.** Once the clamp has the
   conductor, the person's hold is behind the clamp; a hard pull is a person
   problem, and the proof pull catches a disturbed crimp.
4. **A bad contact cut off at the station shortens the conductor** by ~6 mm [calc
   recovery_length §1]: the person cuts the whole ribbon end back and starts the
   end again.

## Contribution

- **"The tip is the reference, the clamp carries it":** the whole place-the-contact
  problem is solved within ~10 mm of the machine's own parts, with nothing precise
  asked of the person.
- **"The machine keeps the order":** the J2 skip, the J4/J7 crossings and the pin
  order become lights for the person, not mechanisms.
- **The minutes accounting:** a person-paced station is a quality and skill tool,
  not a time saver; time falls when a whole end is loaded at once, or when two heads
  alternate.

## Major unresolved problems

- **Silicone strip by clamp-and-pull** (problem 2).
- **Axial entry into open barrels** without the strands splaying on the barrel's
  rear edge; a bellmouth lead-in helps, unproven.
- **Cycle time**: at 40 s the person waits; p4b answers with two slow heads.

## What rests on assumptions

- A 40 s cycle, 5 s to present, 8 s to insert [estimate].
- Clamp friction on silicone for a 3 mm slug pull.
- A 15–20 N proof pull is harmless to a good crimp (JST's minimum is 39.2 N).
