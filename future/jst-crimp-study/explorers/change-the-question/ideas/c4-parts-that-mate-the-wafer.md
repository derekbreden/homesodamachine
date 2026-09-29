# c4 — Change the part, not the machine: an IDC twin for the XH wafer, and contacts chosen for the machine

A part change. The board's XH wafers stay; what plugs into them is either an
insulation-displacement (IDC) housing that mates the same wafer, if one exists,
or an XH crimp contact chosen, in shape and in supply form, because it suits a
machine. Its board-side sibling, changing the pin map or the housing count
rather than the part, is [c7](c7-straight-across.md). Numbers:
[`../calc/ctq.out.txt`](../calc/ctq.out.txt) §3, §7 [ctq §n];
[`../calc/wave2.out.txt`](../calc/wave2.out.txt) §1–2 [w2 §n];
[`../calc/wave3.out.txt`](../calc/wave3.out.txt) §2 [w3b §n].

## Picture it

The IDC twin, as it would operate if the part exists.

**Where things start.** The ribbon end is split back ~10 mm and each
conductor laid in a printed **comb at 2.5 mm pitch**. There is no strip and
there are no loose contacts. The IDC housing sits in a nest under the comb,
slots up, cavity 1 at the fence.

**What moves.** One slow stroke of a flat pressing plate. The drill press
quill, an arbor press or a lever will do. The plate pushes every conductor
at once down into its pair of IDC blades. The blades slit the insulation and
grip the strands. A cover snaps on behind for strain relief.

**What carries the force.** The IDC blades and the housing, against the nest
floor. It is tens of newtons per conductor [assumption: IDC seating is far
below crimp force].

**How it knows it worked.** The real-wafer tester (see
[`c1`](c1-half-rows.md)) checks order, opens and shorts. A pull on the ribbon
behind the cover checks strain relief.

**What locates what.** The comb's slots locate each conductor over its slot
pair; the housing's own slots locate the blades; the nest is the reference for
fixed. There is no contact to place.

**What the person does.** Lays the ribbon in the comb and presses once.

**Steps covered:** place and crimp, dissolved into the part (if it exists);
splay becomes the comb. **Hands back:** splitting the ribbon end and laying it
in the comb, the press stroke, the test.

**The consequence.** The whole five-step problem would collapse to "split,
comb, press". The step Derek most wants automated disappears into the part:
the housing places every contact on every conductor at once. Derek already
makes this kind of joint with this very ribbon on the 110 IDC keystone, with
the Klein VDV427-300 [repo cable-assemblies.md: the ribbon is one "which a
110 IDC and an XH contact take"; repo tools.md].

## What exists

- **JST makes no IDC version of XH.**
  - The XH catalog is titled "Crimp style and Mating style" [mfr S1, 2025
    edition, as read].
  - JST's catalogs list IDC twins only for other series: **KR** is a "2.0 mm
    pitch … IDC style connector", "Interchangeable with crimp style PH
    connector … utilize the same PH header" [mfr: JST KR catalog, eKR.pdf].
  - Wikipedia's JST table lists interchangeable families for PH (KR, KRD, CR)
    and ZH, and none for XH [source S32].
- **So the precedent exists, but not for this wafer.**
- **A third-party XH-mating IDC housing** was not confirmed. Web search was
  not available to this explorer, and the coordinator's Prime pass found no
  listing on 2026-09-28 [sourcing/amazon-prime.md].
- **Even if one exists, the wire may not qualify.**
  - JST's IDC rule: "When wire is used in insulation displacement connector,
    use wire checked in JST" [mfr S5 §5].
  - KR takes 7-strand AWG #26 or #28 at 0.9–1.0 mm OD [mfr eKR].
  - This ribbon is 60 × 0.08 mm strands at 1.7 mm OD in soft silicone [source
    S29].
  - Fine strands can part around an IDC blade instead of being gripped, and
    silicone gives the slot little support [assumption]. The 110 IDC's
    success with this ribbon is a point for it. A 110 slot is a different
    blade from a 2.5 mm pitch connector's.

## Contacts chosen for the machine, not for the kit

Each XH contact below changes one thing a machine must cope with. Two
properties decide most of it: **open-wing width**, which decides whether open
contacts can sit side by side at a pitch, and **supply form**, which decides
what orients the contact and how often a person refills it.

| Contact | Open width at the insulation barrel | Supply form and refill interval | What it changes for a machine | Evidence |
|---|---|---|---|---|
| **BXH-001T-P0.6**, genuine loose piece | 1.95 mm catalog envelope, if the wings really fit inside it (unmeasured) | bag; a person, a rail or a plate orients each one | Known part. If 1.95 mm holds, open contacts sit side by side at 2.5 mm with 0.55 mm to spare [ctq §3] | $0.0444 at 50, 137,303 at Digi-Key [xh-facts §6]; envelope [mfr S1] |
| **SXH-001T-P0.6** on strip | as BXH | 100 / 500 / 1,000 cut strip: 1.9 / 9.4 / 18.9 units per strip; 8,000 reel: ~151 units [terminal-supply calc §1] | The carrier orients and locates every contact; the pilot holes are the datum. JST's carrier pitch is unpublished | $0.0471 per 100-piece strip at Digi-Key [xh-facts §6] |
| **Clone reels** (CJT A2501-TP, HDGC2501-T) | 2.46–3.0 mm (±0.25) on their drawings | reel of 7,000–15,000: ~170 units | Cheapest. Wing width, lance and pitch vary by maker | $0.0079, 665,523 in stock for CJT at LCSC [xh-facts §6] |
| **Kit contacts** (CQRobot, on hand) | unmeasured; clone drawings suggest 2.46–3.25 mm | loose in the kit bag, 280 per 2P/3P/4P set [sourcing/amazon-prime.md]: ~5 units per set | Wide wings are what terminal-supply's hanging rail and the pocket plates orient by; they are also what collides at 2.5 mm and nests in a bag | on the bench |
| **Any of the above, pre-formed** ([c6](c6-pre-form-the-contact.md)) | 1.96–2.14 mm keyhole [w2 §2]; 1.82–2.05 mm for the tall keyhole or the crimper-made U, 2.3–3.0 mm tall [w3b §2] | loom-order sticks, nose to tail | Open contacts sit at 3.4 mm with room for an ordinary punch and at 2.5 mm without touching; the conductor snaps in; loose contacts stop nesting | [calc w2 §2–5]; untested |
| **SXH-001T-P0.6N**, low insertion force | Shape A, 1.8–1.9 mm end view | as SXH | Eases insertion. JST calls it "less resistant to the vibration" [mfr S1], a poor trade in an appliance with a compressor | [mfr S1] |

**One caliper reading cuts two ways.** The open insulation-wing width of a kit
contact and of a genuine BXH does not say which contact is better; it says
which arrangements each suits:
- **narrow wings** (≤2 mm) suit side-by-side pallets and preloaded housings:
  c1 at 3.4 mm without a lift, c1b in one tack pass, into-the-housing's i2b;
- **wide wings** (≥2.4 mm) are what terminal-supply's hanging rail (a3, a3b),
  its post plate (a6) and machine-that-sees-and-learns' pocket plate (v4b)
  orient contacts by. JST's envelope may mean genuine contacts have no wide
  head to hang from;
- **pre-forming** (c6) lets a wide contact be oriented by its wings first and
  narrowed afterward.

**Würth WR-WTB 2.50 is not an XH option.** Würth's drawing of 646 001 137 22
(2.50 mm female crimp terminal, AWG 28–22, 10,000 per reel) gives a box of
**1.45 × 2.00 mm** in section C-C, against XH's 1.85–1.95 × 2.2–2.4 mm
[mfr: Würth drawing rev H 2017, https://www.we-online.com/components/products/datasheet/64600113722.pdf,
read 2026-09-28; w2 §1]. It would sit loose in an XHP cavity. Its drawing is
still the only public one that dimensions a carrier for a contact of this
class: **pitch 7.10 mm, carrier 3.00 mm wide, pilot hole Ø1.50, contact 7.0 mm
long, 10.8 mm with carrier**. That is a smaller contact's strip; JST's SXH
pitch stays unmeasured until one Digi-Key 100-piece strip is under a caliper.

**Can a carrier load several cavities in one push?** Only if its pitch were a
multiple of 2.5 mm. Würth's 7.10 mm is 0.40 mm off 7.5 [ctq §7], and is also
0.30 mm off every fourth ribbon conductor (6.8 mm) and 0.30 mm off two
half-row pitches. If SXH's own pitch turned out to be 7.5 or 6.8 mm, a strip
could gang-load cavities or half-row pallets directly. The strip remains a good
handle for one contact at a time (terminal-supply's carrier-as-handle).

## Problems worked through

1. **If no XH-mating IDC exists, half of this is empty.**
   - The IDC half is conditional.
   - The contact half stands on its own: measured drawings and prices for
     parts that change what a machine must tolerate.
2. **An IDC housing from an unknown maker is as unknown as a clone contact.**
   The same wafer tester and pull check apply. It would also
   need a vibration soak with this ribbon, because the wire is outside any
   IDC maker's qualified range [assumption].

## Contribution

- It names the one part that would dissolve the whole problem, and why it
  probably does not exist for XH. JST's IDC twin exists for PH, not XH.
- It names what to check if someone finds one: that it mates the wafer, and
  that its slot is qualified for fine-strand wire of this OD.
- It sets out XH contacts by the two properties a machine cares about, open
  width and supply form, and says which arrangements each suits.
- It names the one public carrier drawing of this class (Würth, 7.10 mm) and
  why it is not an XH contact.

## Major unresolved problems

- Existence of an XH-mating IDC housing: unconfirmed.
- IDC on 60-strand silicone ribbon at 2.5 mm pitch: unqualified even if one
  exists.
- Whether genuine JST open wings are really within 1.95 mm, and how wide the
  kit contacts' are: the one measurement that most changes the pallet, preload
  and rail ideas. One BXH and one kit contact under the caliper settle it.
- JST's own SXH carrier pitch, unpublished.

## What rests on assumptions

- IDC force and fine-strand behaviour [assumption].
- The third-party IDC market [assumption; no listing found].
- Refill intervals assume ~53 contacts per unit [terminal-supply calc §1].
