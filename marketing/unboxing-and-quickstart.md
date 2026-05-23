# Unboxing and Quick-Start — Design Brief

*Working draft, 2026-05-20. Source: Derek's spoken intent, captured by an agent. Not a spec yet — a design brief that the printed-piece spec, the carton-geometry spec, and the install-kit packing order will all be derived from.*

The customer is unboxing a $7,500 hand-built appliance, one of fifty, signed by the person who built it. The unboxing is the moment the trust-gap argument in [`target-market.md`](target-market.md) "The trust gap" either lands or doesn't. The factory's packing procedure in [`../hardware/assembly/finish-pack-ship.md`](../hardware/assembly/finish-pack-ship.md) is downstream of the experience this brief defines — what goes in the box and what order it gets packed in is whatever serves the customer's experience of opening it.

This brief is the small-batch, hand-built, $7,500 equivalent of what Bambu spent enormous resources doing for the H2C: an unboxing that telegraphs care, restraint, and competence. We are not trying to match Bambu's industrial-design budget. We are trying to clear their bar on the few things that actually matter, by removing everything that doesn't.

---

## Six principles

1. **The box makes it obvious which way to open.** No second-guessing, no rotating the carton to find arrows, no "is this the top?" The TOP face is visually obvious from across the room. The opening procedure (which flap, which seam, which direction) is communicated without words.

2. **The quick-start guide is the first thing the customer sees.** Before the appliance, before the faucet bag, before the install kit, before the welcome letter. The moment they pull off the top of the box, they are looking at the quick-start guide. Ideally the guide covers the entire interior as a flat, unfolded sheet — no creases, no folds, no envelope. The customer's hand is already on it before they realize they're holding it.

3. **Nothing in the quick-start guide that the customer does not need to do.** No legal pages. No safety inserts wedged before the steps. No "thank you for purchasing" preamble. No regulatory text. No specifications. The guide is the install sequence, period. Everything else — safety, regulatory, the welcome letter, the warranty card, the Founder Edition certificate — has its own place and is not in this sheet.

4. **Everything the customer needs to do is in the quick-start guide.** They do not need to open the welcome letter to find a step. They do not need to dig into the install kit to find a sub-instruction. They do not need to scan the QR code to find the missing piece of the procedure. If the customer follows only the quick-start guide, the appliance comes online. If a step depends on a second document, the second document does not exist and that step belongs on the sheet.

5. **Pictures, not paragraphs. Line drawings for everything.** Each step is a line drawing of the actual physical action, oriented from the customer's point of view (looking down at the cabinet floor, looking up at the under-counter, looking at the rear panel). Text is captions, not explanations. The drawings are the spec. If a step cannot be communicated as a line drawing, the step needs to be re-designed until it can.

6. **Color matches between the printed guide and the product.** The drawings are black line art. Each step's hero element — the fitting being connected, the surface being aligned, the cap being removed — is rendered in a deliberate accent color. The matching feature on the appliance itself is the same color. Customer sees "connect the blue tube to the blue ring on the back panel," looks at the back panel, sees one blue ring, plugs in the blue tube. No labels, no part numbers, no decoding. The matching color is the wayfinding. The rest of the appliance is monochrome so the colored accents are unmistakable.

---

## What this means for *this* appliance

The six principles are generic. The product-specific work is figuring out which steps actually belong on the sheet, what gets colored, and what happens during the long thermal pulldown.

### What the customer is actually doing

End-to-end, the customer's install is roughly:

1. Cut the faucet hole in the countertop (or use an existing hole — see [`2026-05-19/countertop-faucet-penetration-gap.md`](../todo/2026-05-19/countertop-faucet-penetration-gap.md)). Mount the faucet through the hole, clamp from below.
2. Slide the appliance into the under-sink cabinet. Route the 3-tube umbilical from the faucet down through the countertop into the appliance's rear-panel umbilical-port cluster. Push each tube into its bulkhead (one of the three carries a blue accent ring — the carbonated-water line).
3. Connect the rear-panel water inlet to the customer's tap-water supply using the install-kit's add-a-tee (threads onto the existing 3/8" angle stop) and 1/4" LLDPE supply line (push-to-connect at the rear panel — no tools).
4. Place the CO2 cylinder in the side gap beside the appliance, secure it, and connect the regulator's tether to the front-panel CO2 inlet.
5. Plug the appliance into a wall outlet via the supplied line cord.
6. Power on. Open the CO2 cylinder valve. Open the water-supply valve.
7. Pour SodaStream concentrate into the hopper, one bottle per flavor, following the appliance's prompts on the config display.
8. Wait approximately 60-90 minutes for cold pulldown ([`../todo/2026-05-20/first-pour-commissioning-gap.md`](../todo/2026-05-20/first-pour-commissioning-gap.md)).
9. Pull the lever. Drink soda.

The sheet is exactly nine steps. Each step is one line drawing.

### The color discipline

Three accent colors, used consistently across the printed sheet and the physical appliance:

- **Blue — carbonated water.** The umbilical's carbonated-water tube ring on the rear panel ([`../hardware/printed-parts/enclosure/back-panel/README.md`](../hardware/printed-parts/enclosure/back-panel/README.md) already commits to this), the matching tube end coming down from the faucet, the same blue on the line drawing for step 2.
- **Red — CO2.** The front-panel CO2 inlet bezel, the matching regulator tether end, the line drawing for step 4. (Red because CO2 is a pressure-and-cylinder story, and customers already associate red with gas-cylinder regulators.)
- **One more color, to be picked — install action.** The cap-removal points (water inlet cap, CO2 inlet cap, BiB cap), the power switch, the cylinder valve handle. The "things the customer's hand actually touches during install." Green is the obvious candidate (safety-positive, clearly visible against printed black). Yellow if a brighter visual pop is wanted.

Everything else on the appliance is monochrome — the printed enclosure in whatever single body color we land on, the rear-panel labels in black, the nameplate signature in matte. Three colors, three meanings, no exceptions. If a fourth color is needed for a fourth thing, the sheet has too many steps.

### The pulldown problem on the sheet

Step 8 above — "wait approximately 60-90 minutes" — is the moment that breaks the "everything you do is on the sheet" principle, because there is nothing to do during the pulldown. This is the highest-stakes step on the sheet, because it is the only one where the customer is waiting and might decide the appliance is broken.

The sheet handles this by making the wait a step rather than a footnote. Step 8 has its own drawing: the appliance on its shelf, the config display showing a progress indicator, a glass of water-with-ice on the counter beside it. Caption: "Your appliance is chilling. The display will show progress. Approximately 60-90 minutes. Pour yourself something else." The drawing legitimizes the wait. The wait is part of the install, not an interruption to it. (See [`../todo/2026-05-20/first-pour-commissioning-gap.md`](../todo/2026-05-20/first-pour-commissioning-gap.md) for why the timeline is what it is and what the firmware needs to do during it.)

### What is *not* on the sheet

Explicitly excluded from the quick-start sheet, and given their own homes elsewhere in the box:

- **Safety / regulatory inserts** (R-600a flame symbol per ISO 7010 W021, flammable-refrigerant marking, 120V 60Hz only warning, CO2 cylinder restraint per [`../todo/2026-05-19/co2-cylinder-restraint-gap.md`](../todo/2026-05-19/co2-cylinder-restraint-gap.md)). These are a separate printed insert with the regulatory text. They live in the install kit box, below the quick-start sheet, so the customer encounters them in due course but they do not pollute the install flow.
- **Founder Edition welcome letter** ([`../hardware/assembly/finish-pack-ship.md`](../hardware/assembly/finish-pack-ship.md) step 6). Hand-signed letterhead, addressed to the customer by name, from Derek. This is its own moment, not part of the install. Lives separately so the customer encounters it as a distinct gesture after install rather than as one more piece of paper in the install flow.
- **Per-unit nameplate / Founder Edition certificate.** The nameplate is on the appliance ([`../hardware/printed-parts/enclosure/nameplate/README.md`](../hardware/printed-parts/enclosure/nameplate/README.md)). The certificate, if there is one, lives with the welcome letter.
- **Warranty / RMA / support contact info.** Lives on the per-unit portal at `homesodamachine.com/u/NNN` (the QR code on the rear-panel nameplate). The welcome letter mentions the portal. The quick-start sheet does not.
- **Detailed troubleshooting.** Lives on the per-unit portal. The quick-start sheet assumes everything works on the first try. If it doesn't, the portal and the Zoom-call support architecture from [`../todo/2026-05-18/install-consult-playbook-gap.md`](../todo/2026-05-18/install-consult-playbook-gap.md) take over.
- **The bill of materials, the BOM cost, the assembly architecture, the "made in" details, the founder's bio.** All interesting to a subset of buyers, none of them install-relevant. Web only, or in a separately-bound owner's book if we ever do one.

The principle: the quick-start sheet is for the install. Every other artifact has its own place. The boundary is hard.

---

## The carton itself

Following from the principles, the physical packaging:

- **Single TOP face, unambiguous.** Top face is visually distinct — different finish, a single embossed mark, the only printed face if the rest of the carton is plain. The customer's eye picks it from across the room. No "this side up" arrows on six faces.
- **Tear-strip or single-pull opening.** A single ribbon-pull or a single tear-strip that opens the top in one motion. Not a tape-cut, not a flap-fold, not a "find the right corner to lift." One motion, one decision.
- **The top opens to reveal the quick-start sheet flat across the entire interior.** No box-within-box. No "lift this to find the guide." The customer pulls the top, the sheet is there, fully visible, every word readable without removing anything.
- **Under the sheet: the appliance, cradled in foam end-caps, oriented with the rear panel toward the carton's marked REAR.** When the customer lifts the appliance out, the front face is toward them, exactly as it will sit in the cabinet. They never see the back of the appliance during unboxing if they don't choose to.
- **Side voids for the faucet bag and the install kit.** Per the existing finish-pack-ship plan, but with the install-kit's contents re-ordered so that the regulatory inserts and welcome letter inside it match the same encounter-order principle (welcome letter on top, regulatory below).
- **Color discipline applies to the carton too.** Plain kraft body, black printing, the same three accent colors used sparingly — a blue ring on the side of the carton where the umbilical bag lives, a red mark where the CO2-related items live. The carton itself teaches the color language before the customer has even opened it.
- **No styrofoam visible.** Molded pulp end-caps or molded EPP foam in a single color. Polyethylene bags only where strictly required, and printed with the same line-drawing aesthetic if printed at all. The "look inside the carton" moment is as designed as the "look at the appliance" moment.

---

## What this brief is *not*

- Not a spec for the carton dimensions, foam end-cap geometry, or print artwork. Those are downstream documents that take this brief as their input.
- Not a draft of the quick-start sheet's actual line drawings. Those need a CAD-aware illustrator pass once the back-panel and front-panel geometries are frozen.
- Not a commitment to a specific accent color for the "install action" third color, or to specific paper stock, or to specific print processes. Those are decisions to be made when the artifact is being produced.
- Not the final word on Step 8 of the sheet. The pulldown-wait wording is a working draft; it depends on the measured pulldown time on unit 001 and on how the firmware ends up displaying progress.

---

## What this brief *commits to*

- The quick-start sheet exists as a single flat unfolded sheet, encountered first, with no other content competing for the customer's attention at the moment they open the box.
- The sheet contains only install steps. Everything else is in a separate artifact with its own place in the box.
- The drawings are the spec. Text is captions.
- Three accent colors. They mean the same thing on the printed sheet as on the appliance. They are used only for those meanings.
- The carton's top face is unambiguous. The opening is one motion.

Everything else — paper stock, fold patterns, accent-color choice, line-drawing style — can be decided downstream once the principles are agreed.

---

## Hooks into existing docs

When this brief becomes a spec, several existing documents will need to update:

- [`../hardware/assembly/finish-pack-ship.md`](../hardware/assembly/finish-pack-ship.md) — packing order and carton geometry get re-derived from this brief instead of being defined independently. The current "install-kit box" structure changes shape because the quick-start sheet leaves the kit and becomes the top-of-carton object.
- [`../hardware/printed-parts/enclosure/back-panel/README.md`](../hardware/printed-parts/enclosure/back-panel/README.md) — already commits to a blue accent ring on the carbonated-water bulkhead. This brief promotes that from a single design decision to part of a three-color system that applies across the whole product, the carton, and the printed materials.
- [`../hardware/printed-parts/enclosure/nameplate/README.md`](../hardware/printed-parts/enclosure/nameplate/README.md) — the QR code's destination (`homesodamachine.com/u/NNN`) inherits the "everything not on the sheet lives here" role and needs to actually exist (the [`../todo/2026-05-18/per-unit-portal-gap.md`](../todo/2026-05-18/per-unit-portal-gap.md) gap is now load-bearing on this brief).
- [`../todo/2026-05-20/first-pour-commissioning-gap.md`](../todo/2026-05-20/first-pour-commissioning-gap.md) — the pulldown timeline is now also a step on the printed sheet, not just a firmware-display concern. The measurement on unit 001 calibrates the sheet's wording.
- [`../todo/2026-05-18/install-consult-playbook-gap.md`](../todo/2026-05-18/install-consult-playbook-gap.md) — the Zoom call's script can assume the customer has the quick-start sheet in front of them and refer to its steps by drawing rather than by re-explaining.
- [`target-market.md`](target-market.md) — the trust-gap section already names "Derek's face, his kitchen, his story" as the brand at Founder Edition. The unboxing experience is now a deliberate extension of that story rather than a generic D2C unboxing.

---

## Open questions for Derek

Things the brief deliberately leaves unresolved, for the next pass:

1. **The third accent color.** Green or yellow for "install action / customer's hand touches this"? Green is the safe and consistent choice; yellow is the high-energy choice. Either works.
2. **Paper stock for the quick-start sheet.** Heavy uncoated card stock so it feels like a keepsake, or thinner gloss for sharper line work? Card stock probably wins on the "the moment they pull off the top" feel.
3. **Whether the welcome letter is in the install-kit box, in its own envelope on top of the appliance under the quick-start sheet, or tucked into the faucet-and-umbilical bag where it travels with the most personal-touch component. The current finish-pack-ship plan has it in the install-kit packet; this brief has not yet committed.
4. **Whether the sheet is bilingual at all (US-only run for Founder Edition per the existing finish-pack-ship.md scope), or English-only with a clean conscience. English-only is fine for the lower-48 ship plan.
5. **The carton's exterior face. Whether the carton itself is intended as photographable for unboxing-video purposes (Bambu does this — the carton arriving at the customer's door is itself a marketing surface). For the Founder Edition's 50-unit run, the answer might still be "plain kraft, the inside is the experience," but it is worth deciding.
