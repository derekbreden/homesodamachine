# Notebook — hand-tool-as-press

## Log, 2026-09-28

- **Context read.** brief, shared-context, working-method, xh-facts,
  prior-art, context sourcing requests, and `hardware/assembly/cable-assemblies.md`.
  I also read `hardware/ledger/tools.md` for the SN-2549, the SN-28B, the
  ESP32 stack, the NEMA 23, the ELP camera and the test indicator.
- **SN family.** One chassis shared across the SN tools, with replaceable
  jaws at $4.99–9.99 [icrimptools.com]. The jaws are held by screws, seated by
  crimping closed, then tightened. The SN-2549 is 8 × 3 × 1 in, 10 oz, with a
  tension wheel [TH3D listing].
- **Printed positioners for the SN-2549 exist** (Ryan Reed, Printables, JST SM
  and Molex SL). They attach through a 20 mm M4 lower-jaw screw with a nut
  [Chief Delphi thread]. The Printables pages returned 403, so the model
  geometry was not seen.
- **WC-110 manual (RS-hosted PDF, extracted with pdftotext).** Flap locator;
  contact "inserted to the stop"; close lightly until held; conductor pushed
  "until insulation stop blade" (German *Iso-Stop Blech*). This pointed to a
  blade as the conductor stop. The SN-2549's single stepped die leaves no gap
  for one in the window, so the blade moved to the neck in front of the
  conductor barrel.
- **Handle force.** Assembly Magazine (95079): people apply 20–50 lbf at a
  crimper's handle, and Pressmaster's tools rose from 23:1 to 50:1 gain.
  Together with "Derek crimps XH by hand with this tool", that bounds grip force
  without measuring the tool.
- **PA-09.** A review says no ratchet, two squeezes, and crimp quality depends
  on feel. Engineer lists it for SXH [xh-facts]. That became a5.
- **Tri-Star CrimpXpress** loads contacts into ordinary hand crimp tools. Its
  mechanism is not described on the product page.
- **SN ratchet release.** A release lug on the pawl between the grips [forum
  post; IWISS video title]. What the tension wheel does inside the tool is
  undocumented.
- **Sourcing seen:**
  - SparkFun TAL220 $12.95 in stock;
  - NFP 5840-31ZY $18.50;
  - Creality Ender-3 V3 SE $199;
  - Progressive Automations PA-14 "ships within 24 hours" (price not
    rendered);
  - StepperOnline pages returned 403.
- **Web search budget.** It ran out near the end of the session. The
  laser-cut steel service (for a4's plates) and small-part Amazon items are
  unverified and sit in `sourcing-requests.md` or are marked [assumption].

## Log, wave 2 (2026-09-28)

- **Read.** into-the-housing's critique of this explorer, the digest, and the
  other eight summaries. From other explorers' files I read terminal-supply
  a2c and into-the-housing i5 for what the combinations borrow, and
  into-the-housing's exchange calc and `handover.md` for the numbers.
- **What the critique changed:**
  - **The lance.** It shares the neck with the blade. Wave 1's 0.3 mm blade
    left −0.10 to +0.20 mm for a brush. The blade is now 0.10 mm steel plus
    polyimide [calc wave2 §1], and the contact case splits on the neck's
    measured length.
  - **Rearward draw catches the lance on the anvil face.** Lift first (R1),
    carry clear then set down (R3), and a ramp on the locator plate. Adopted in
    a1, a2, a2b, a3 and a4b.
  - **The proof pull.** It no longer goes through the blade, which yields
    unbacked at 20 N [calc wave2 §2], or the anvil. It goes to a backed pull
    slot or jig (a2, a6), or to the dies re-closed in a1b.
  - **a3's rolled crimps.** Generalised into the side-entry jaw law
    [calc wave2 §3]. a3's fixture now stands on edge (the critique's a3-e),
    and a4b is the C-frame alternative.
  - **a2c's first latch ties the ribbon to the housing.** a2c now runs in
    batches with a humped one-at-a-time insertion and a stencil blade pusher.
    a2d is the batch-plus-gang-push branch.
  - **Where I part from the critique:**
    - **R2 (proof pull at hold) needs the pawl out.** At the ratchet's first
      tooth the punch sits at an open contact's wing height, well above a
      crimped barrel, so a ratchet tool cannot grip a finished crimp without
      running a full cycle. R2 lives in a1b only.
    - **The C-frame lift.** It comes out 6.3–9.2 mm here rather than 5–7 mm,
      because the arm must pass over the neighbours' crimped boxes (~1.35 mm
      above their axes) and carry an anvil insert [calc wave2 §4].
- **What I found against my own wave-1 a1.** A bare steel blade that touches
  the box is electrically the contact. Strands touching the contact at the
  insulation barrel's mouth, or the die's rear face on a miss, read the same
  as strands at the blade. So wave 1's "touch-off" could not tell depth from
  entry. The insulated front face gives two separate events, amber and green.
  A machine can also skip the blade: touch the tip on a grounded tip plate,
  then feed a set distance (a2).
- **New direction: a6, the foot-closed jig bench.**
  - The coordinator suggested manual jigs that grow into stations. In this
    view the missing piece is a second free hand, so the foot closes the tool
    through a cord.
  - The cord is the same interface a1's worm winch reels later.
  - A two-stage pedal makes the ratchet's first tooth a half-press.
- **Web.**
  - JLCPCB's stencil page gives $3 and 24 h but no thicknesses; the
    capabilities page gives none either.
  - WebSearch was used up. Foot-pedal force limits are labelled [estimate];
    MIL-STD-1472-style tables would settle them but were not fetched.
- **Sketches.** `sketches/wave2_sketches.py` writes `a6-jig-bench.svg` and
  `jaw-law-and-c-frame.svg`.
- **Calc.** `calc/wave2.py` → `wave2.out.txt`, §1–9. Citation keys in the idea
  files: [calc §n] is `hand_tool_press.out.txt`, [calc wave2 §n] is
  `wave2.out.txt`, [ith ex §n] and [ith calc §n] are into-the-housing's
  exchange and insertion calcs.

## Log, wave 3 (2026-09-28)

- **Read.** machine-that-sees-and-learns' reading of this explorer
  ([exchange](../../exchange/machine-that-sees-and-learns--on--hand-tool-as-press-w3.md))
  and its calc; its v1, v5, v7 and v8; change-the-question's c6, c6b and c1c;
  this explorer's own wave-3 exchange on change-the-question (K1–K6, H1–H7) and
  its calc; the Prime pass ([`sourcing/amazon-prime.md`](../../sourcing/amazon-prime.md)).
- **Calc.** `calc/wave3.py` → `wave3.out.txt`, §1–7. It re-derives the
  critique's a4 numbers with its own model and agrees: at a 0.15 mm overtravel a
  15–20 kN/mm loop leaves the stack idle or the dies apart; die contact set at
  preload/k_f + 0.05 mm (0.17–0.28 mm above BDC) gives ~3.6 kN at BDC and
  1.6–2.0 N·m before friction. It adds: a hand lever on the eccentric shaft as a
  motorless die set (15–20 N at 150–200 mm); the stepped pull plate; the flag
  seat's jaw openings; "C tacks for itself" at e = 3.0–3.5 mm.
- **Taken in from the critique:**
  - a1b's proof pull at hold removed (re-closed dies add 4–100 N of grip); the
    position-hold branch rejected (the lance meets the anvil face first);
  - the force wall on the station MCU (a1, a1b, a5);
  - a4's die-contact setting, drive table and Prime parts (500 kg cell, 10:1
    planetary, DITR-0105);
  - the side-entry stand-out as a + 2.7 mm with crimped neighbours (a2, a2b, a3,
    sketches);
  - strip length set from the contact in use (a1, a2b, a6);
  - a5 as a genuine-contact arrangement unless E measures ~1.8 mm; its
    insulation window 0.1–0.3 mm; bend tests;
  - a3's tip picture before the slide-on (W5); a2's tip plate beside it (W9);
    a2b's per-contact measurement (W7); a1b's journal (W8);
  - W3 and W4 folded into a6 as the pull-and-look jig and the record.
- **New files.** a4c (W1), a6c (W2), a6b (K1), a4d (K2). a2b takes K3 (sticks),
  a2d and a3 take K4 (T4 scope), a1b takes K5 (fold station) and K6 (JST lead
  as target).
- **Where this view parts from the critique:** the pull plate. A flat plate needs
  a 0.35–0.5 mm neck, as the critique says. A stepped plate bears on the box's
  rear edges outside the crimped barrel's width (0.12–0.28 mm a side) and above
  its height, where it can be thick and backed; only a tongue in front of the
  barrel's front edge must be thin, and it carries nothing [calc w3 §3]. It
  depends on the box's rear being a clean step, which the same neck photo shows.
- **Own addition to W1:** T's former cut from the SN's own insulation section,
  so the tack is the SN stroke paused and the re-form question narrows to
  re-registration.
- **Sketches.** `sketches/make_sketches.py` (a1, a2, a3 redrawn on edge, a4,
  a5), `wave2_sketches.py` (a6, jaw law), `wave3_sketches.py` (a4c, flag seat,
  a4d, a2b, a2d). Rendered and checked for overlaps with rsvg-convert.
- **Web.** WebSearch unavailable; no new fetches. New Amazon needs are in
  `sourcing-requests.md` under Wave 3.

## Directions set aside, and what would bring them back

- **The 12-ton hydraulic shop press as the closer.** ~118 kN against a
  0.8–2.6 kN crimp, with no force or position control finer than a hand on a
  lever. A die set under it would need its own hard stop and a relief. It comes
  back if a4's die set exists and the press is just a frame to push it,
  person-operated.
- **The WEN drill press quill closing the tool.** It gives a person a lever
  and a depth stop, and no automation. It comes back as an electronics-free a1
  for a person who wants to stop squeezing by hand.
- **Air cylinder on the handle.** 25 mm bore at 6 bar gives ~300 N, enough.
  Set aside because it needs the DeWalt compressor running, unattended, in the
  house. It comes back if a quiet air source exists.
- **Hobby servo straight on the handle.** ~70 N at a 25 mm horn, below a hand.
  It comes back behind a lever or a cord reduction.
- **Strip fed through the SN jaw.** Neighbouring contacts on the strip, 7–9.5 mm
  apart, hit jaw material beside the working nest. Kept as a variant inside a2,
  for when the usable nest is the one at the jaw tip. It also lives in a4 with
  a narrowed die.
- **A tube magazine of loose contacts stacked box-down.** Boxes nest into the
  open insulation wings of the contact below (box 1.95 × 2.4 inside wings
  2.5–3.0 × 2.75–3.2). The revolver disc in a2b replaced it. It comes back if
  a measured kit contact shows the wings narrower than the box.
- **A hobby arm (SO-101 class) holding the crimp module.** The force loop is
  fine inside the module, but ~0.8 kg is beyond a small servo arm's comfortable
  payload, and arm repeatability is coarse next to a belt gantry. It comes back
  with a lighter module, since every other part of a3 transfers.
- **The WC-110 as its own arrangement.** It already has the locator a1 prints.
  In this view it is a tool that drops into a1's cradle ($536.51, Digi-Key 147
  in stock), not a different machine.

- **A rack of pre-loaded SN tools as the contact magazine.** Nine $18–21
  tools, each holding a contact at its first tooth, loaded at leisure, brought
  one by one to the conductors. For a person it buys nothing a locator does
  not. For a gantry it is a3's tool changer with nine crimp modules and nine
  reset problems. It comes back if loading a contact into a tool on the
  machine turns out to be the slow step.
- **A slice of a real housing as a sliding fit gauge.** A contact pushed
  through a thin slice folds its lance; drawn back, the sprung lance catches
  the slice's face. Replaced by the keyhole, which the crimp passes through
  once while the wire leaves by a side slot. It comes back as a closing gauge
  (two halves) if a sliced housing's section is wanted exactly.
- **A proof pull through a ratchet tool re-closed to its first tooth.** The
  punch at the first tooth does not reach a crimped barrel. The pawl-out
  version is set aside too (next entries).
- **Knee lever or hand lever instead of a foot.** A knee lever (sewing-machine
  style) gives less travel and force than a heel-hinged treadle. A hand lever
  gives force but takes back the hand the foot frees. It comes back if the
  bench's height puts a treadle out of reach.
- **Rolled crimps for a person inserting by hand.** Twisting each conductor
  back 90° over 20–35 mm strains the strands 2.3–4× past torsional yield
  [ith ex §8]. A person bending a conductor out of the row gets upright crimps
  anyway (a6).

- **A proof pull with the dies re-closed on the crimp (a1b).** Die friction adds
  4–100 N of grip to a 20 N pull, and the grip side cannot hold the die force
  under 4–13 N [sl w3 §1]. It comes back only with a die-side force measurement
  and a held force under ~10 N, which a hand tool does not give.
- **A pull against the jaw's front face with the dies held open.** The lance
  meets the anvil face first wherever its tip hangs in front of it. It comes
  back if the neck photo shows the lance tip always over a relief whose rear
  end is behind the box's shoulder.
- **"C tacks for itself" (a4c's other order).** Lay-in under the open punch,
  part-stroke tack, look, finish. It needs e = 3.0–3.5 mm and gives up the
  straight-down look. It comes back if the tack's grip turns out too weak to
  carry a contact from T to C.
- **c6's round keyhole as the pre-form in this view.** The SN's B die meets the
  jacket before the tips and never re-forms a round bore [htq §1]. It comes back
  if a sectioned crimp shows the die does turn the tips over, or if the round
  keyhole is qualified as the insulation crimp by pulls and bends.
- **Cutting a4's one-nest die to 6–8 mm for a 3.4 mm row.** Too wide by
  1.5–3.5 mm; a4d's tongue is ≤ 4.45 mm.

## Questions carried

- The neck and barrel lengths on one kit contact, photographed from the side
  under the ELP beside a steel rule: the blade, the pull plate (flat or
  stepped), the lance clearance, the strip length and a5's fit all follow.
- Whether the box's rear edges are a clean step or a sloped transition, and how
  much narrower the crimped conductor barrel is than the box (the stepped pull
  plate).
- The SN-2549 closed one click at a time on an empty contact under the ELP: the
  insulation-first window (a6b, a4c's former, a1b's pre-form).
- The SN-2549's XH insulation profile: a B or not, and its closed height.
- How wide the SN-2549 opens at the XH nest: 3.6–4.9 mm for a flag at h.
- The handle stiffness: the SN-2549 clamped by one handle, a known weight on the
  other.
- One empty stroke of a built die set with the button cell: loop stiffness and
  the stack's knee.
- Which SN nest, and how far from the tip; the jaw-half depth a behind it.
- Contact pull-off from a 0.64 mm post.
- Where the first ratchet tooth falls.
- The jacket's real OD, five split conductors.
- A sliced kit housing's rear-entry section, for the keyhole.
