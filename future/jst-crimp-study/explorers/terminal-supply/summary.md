# terminal-supply

*How the contact arrives decides everything downstream.*

This page indexes every arrangement this explorer holds, with the explorer's own one-paragraph picture of each. The idea files carry the development. Paths are relative to this directory.

## Arrangements

### [a1 — A stock side-feed applicator, driven by a slow screw ram](ideas/a1-applicator-slow-ram.md)

A reel feeds a bought OTP-style 'XH2.54' side-feed applicator whose pre-feed leaves the next contact open on the anvil. A ribbon carriage slides conductor k over the carrier into the barrels, steered by the insulation edge as the camera sees it, with the other conductors parked out of the tooling plane. A slow screw or crank drives the ram through its 30-40 mm stroke onto a hard stop on the applicator's own base, with disc springs capping the force; one stroke crimps, shears the tab and feeds the next contact. The frame must open 166-176 mm, so neither 1 t arbor press (139.7 or 150 mm) fits.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die.
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Mounting a reel (8,000 covers ~150 units), emptying scrap, splaying and stripping, parking the other conductors unless the carriage does, and insertion.
- **Major unresolved problems:**
  - What the OTP die does on 60 x 0.08 mm strands in 1.7 mm silicone; whether the insulation crimper cuts it
  - Which contact the OTP die is cut for (clone reels likely)
  - OTP shut height and ram interface unpublished
  - Reel pitch against the feed adjustment
  - Lines of sight at wing height inside the applicator
  - China-post lead time

### [a2 — Strip indexer: the carrier strip is the feeder, the locator and the handle](ideas/a2-strip-indexer.md)

A strip of SXH contacts is indexed by a pin wheel; tapered pins in the neighbours' pilot holes locate the station contact on a steel anvil, and a stepper fence corrects each contact's axial position from a picture of it. A stationary notched lifter bar holds every conductor but k ~5 mm above the fresh contacts, and a lit vane in the 4.1 mm gap backlights the gate. An OTP knife-set punch under a 1 t arbor press, pulled by a lead screw, lands on a hard stop on the anvil block; the downstream carrier drops to shear the tab against a clamped upstream edge, so the kink goes to scrap.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die.
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Threading strips or mounting a reel, emptying scrap, splaying and stripping, insertion, and answering the queue when a ribbon end is stopped.
- **Major unresolved problems:**
  - Whether an OTP knife set keeps punch-to-anvil alignment in a simple holder, and its crimp height on this ribbon
  - Real SXH carrier pitch and pilot-hole geometry
  - Tab stub quality from a one-sided drop-shear
  - Whether a 0.2 mm carrier stays flat in a printed track
  - Crowding within +/-7 mm of the station: vane, clamp finger, lifter notch, punch holder, camera line
  - Lance relief of the knife-set anvil (a flat anvil fits about half the clone range)

### [a2b — The carrier kept as the handle, through inspection and insertion](ideas/a2b-carrier-as-handle.md)

After a2's crimp the carrier is cut either side of the pilot hole, so each contact keeps a 2.3 x 3.0 mm tag with a datum hole on its centreline. A two-point grip (a pin in the hole, fingers on the crimped insulation barrel) holds it with the compliant tab neck out of the loop; cameras measure bend, twist and the box tip's offset from the hole. The proof pull goes to the box's rear face through a slotted plate, and the gripper inserts using the hole plus the measured offset, bends the tag off near the seat, and a fork finishes. A comb sub-variant carries a whole ribbon end on one carrier segment as a docking pallet.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die.
- **Branch of** a2.
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp, insert.
- **What the person still does:** The final ~1 mm of seating by a fork, the housing nest and its indexing, and splay and strip.
- **Major unresolved problems:**
  - Whether the two-point grip fits between neighbours at 2.5 mm pitch
  - Tab stub quality from bend-off beside a housing
  - Whether the box's 0.2 mm walls take a 20 N pull on a plate edge
  - Carrier edge vs rear face at full seat (-0.05 to +0.9 mm), front wall assumed
  - Tags 2.3 mm wide cannot enter 1.5-1.6 mm wire combs: two push phases or no tag in a gang push
  - The comb's 15-30 mm split

### [a2c — The strip gives the hand tool the locator it lacks](ideas/a2c-strip-locator-for-hand-tool.md)

Derek's iCrimp SN-2549 sits in a cradle with a printed clip on its jaw's M4 screw: a fence on the carrier edge and a sprung pin in the pilot hole put the strip's leading contact in the XH nest, as JST's $537 WC-110 flap locator would. An actuator (or Derek's hand) closes one ratchet click so the contact is captive, and a flush cutter parts the tab before any wire exists, so the strip is never twisted and the wire's path is clear. The conductor enters axially and the ratchet completes the crimp. The clip works by hand on day one.

- contacts: carrier strip · steel: SN-2549 or similar hand-tool dies · meeting: conductor brought to a fixed die · usable without a motor.
- **Branch of** a2.
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Threading the strip, splay and strip, presenting the conductor (carriage or hand), and insertion.
- **Major unresolved problems:**
  - The SN-2549's jaw thickness and rear face relative to contact plus tab
  - Whether a one-click capture holds the contact against the 48-158 N cut
  - Whether its XH nest suits genuine SXH or clones
  - Ratchet handle force (unmeasured)

### [a2d — Skip-pitch strip over a crowned anvil: the fresh contacts fall out of the ribbon's plane](ideas/a2d-skip-pitch-crown.md)

A servo punch cuts every other contact off the strip on its way up; the pilot holes stay, and the removed contacts drop into a cup as loose stock. The strip wraps a steel crown of R 25-30 mm whose crest land is the knife-set anvil, so the next kept contact, 14.2 mm of arc upstream, sits rotated 32 deg with its wing tips 0.5-1.2 mm below the station plane; the whole ribbon lies flat, the camera looks level across the station to a fixed backlight, and wrap tension is the hold-down. The punch lands on a stop on the crown block, a downstream drop plate shears the tab, and a slotted pull fork on the crown land lets the carriage proof-pull 20 N before the ribbon moves on.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die.
- **Branch of** a2.
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Mounting a reel (0.89 of one 8,000 reel covers the program), emptying the thinning, reject and scrap cups, splay and strip, and insertion (x2 takes it on).
- **Major unresolved problems:**
  - Real SXH pitch and carrier temper, which set the smallest elastic crown radius
  - Knife-set blade width and protrusion, which set the fan pitch (p >= 2.5-2.8 mm against crimped neighbours' boxes)
  - Seating a knife-set anvil into a crown with its top as the crest land
  - The die outside its applicator, as a2
  - The 9-26 mm split left behind the housing

### [a3 — Loose contacts hang by their insulation wings on a slotted rail](ideas/a3-hanging-rail.md)

Kit contacts poured into a hopper are scooped onto a gently vibrated rail with a stepped slot (2.4 mm at the barrels, 2.05 mm at the box); they hang box-down by their wide wings like screws by their heads, and a brush and height wiper remove the rest. Black rail edges and a light from below make each hanging contact a silhouette whose notch shows which way the U opens; a servo pocket turns the last 180 deg. The contact goes to an anvil with a flap locator, is crimped where it hangs (a3b), leaves on a post (a4, a6), or drops box-first into a rear-face-up housing onto a depth-stop post (x3).

- contacts: loose kit contacts · steel: not applicable · meeting: not applicable (supporting station or module).
- **Automates:** supply contacts.
- **What the person still does:** Tipping in contacts every ~7-14 units, jams the machine could not clear, separating kit housings from contacts, splay and strip, the crimp station itself, and insertion.
- **Major unresolved problems:**
  - The kit contacts' real open-wing widths; genuine JST inside 1.95 mm would fall through
  - Tangle and jam rate
  - Wing damage from vibration
  - Landing accuracy of the tip transfer or the drop into a housing mouth
  - Whether a bought screw presenter (CGOLDENWALL, Prime, thin) can be adapted

### [a3b — Crimp it where it hangs: the rail's end pocket turns the contact to face a sideways punch](ideas/a3b-crimp-where-it-hangs.md)

At the rail's end a hardened turning pocket rotates the hanging contact 90 or 270 deg so its U faces across the rail; through the pocket's cut-away side its floor meets a fixed steel wall beside the rail's line. The ribbon hangs above with its other conductors folded up and clipped; conductor k comes down into the U, a finger presses the insulation toward the floor, and the camera steers depth by the insulation edge. A sideways punch crimps against the wall onto a hard stop, and the crimp lifts out of the open-topped pocket with its conductor.

- contacts: loose kit contacts · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die.
- **Branch of** a3.
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Refilling the hopper, splay and strip, folding and clipping the other conductors, vertical ribbon presentation, and insertion.
- **Major unresolved problems:**
  - A horizontal frame stiff enough for ~3 kN with a local hard stop
  - Whether the contact stays square at the punch's first touch and the floor seats on the wall
  - Seeing strands across the barrels past the pocket's side walls
  - Handling 600 mm looms vertically
  - Genuine contacts inside JST's envelope fall through the slot

### [a4 — Hold the contact by mating it: 0.64 mm square posts](ideas/a4-post-held-contacts.md)

Loose contacts are held by mating them 1.5-1.8 mm onto 0.64 mm square header pins on a printed turret or post bars; box-outline recesses leave only U-up or U-down. A nozzle drops each contact into a loading nest with a lance groove along its floor, and the turret's post spears the box through the nest's front stop while the rear stop takes the push; the magazine fills in loom order with a gap for J2's cavity 3. At the station the post holder floats +/-0.2 mm sideways and in Z, the anvil sets height and the die centres the barrels; release is a pull on the wire, and continuity through the post tells joined from open.

- contacts: either loose or strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die.
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Pouring contacts on the tray (or ~3-5 min per unit of hand loading), splay, strip and conductor presentation, and insertion unless a4b or a4c is used.
- **Major unresolved problems:**
  - The grip of kit contacts on a header pin (0.2-1.6 N estimated from a secondhand Molex figure)
  - Whether clone boxes centre on a post like JST's double-leaf box
  - The box entry's real size and lead-in (sets capture +/-0.1-0.3 mm)
  - The floating holder's design
  - Whether the box walls take 20 N at a fork
  - The Prime header pins' true cross-section

### [a4b — The post goes through the housing first: crimp on its tip, slide the contact home](ideas/a4b-through-cavity-post.md)

An XHP housing and the web clamp ride one X stage past a fixed station; a light under the mating face makes each empty cavity a bright square for the rear camera. A long post runs through cavity k's front opening and stands ~9 mm out of the rear face; a lance-grooved shuttle nest pushes a bare contact onto its tip, and conductor k is crimped there by an anvil and punch 9 mm clear of the housing. A fork then pushes the contact ~14 mm along the post into its cavity while the post withdraws in step; the force trace, a 5 N pull, the post's clean withdrawal and the square going dark confirm the seat.

- contacts: either loose or strip · steel: bought mini-applicator or knife set · meeting: the housing locates the contact.
- **Branch of** a4.
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Pouring contacts, splay, strip and conductor presentation, loading and unloading the housing and ribbon, and the final continuity test.
- **Major unresolved problems:**
  - Conductor k must carry the ~14 mm push at its crimp: an 11-15 mm hump, a web that follows the push, or branch a4c
  - Whether a 0.64 mm post passes straight through the cavity (one flashlight photo)
  - Whether the cavity walls hold a dragged post back more than the box's grip carries it
  - Fork clearance among seated neighbours
  - Front-wall thickness, which sets the push

### [a4c — Every cavity's post at once: bare contacts crimped on a post bed through the housing, one push](ideas/a4c-post-bed-one-push.md)

A PCB drilled at 2.50 mm carries a 0.64 mm steel post for every cavity, each wired to the controller; the housing slides onto them so the posts stand ~9 mm out of its rear face, and bed, housing nest and web clamp form one pallet. Bare contacts go onto the odd post tips from a grooved shuttle, each odd conductor is pressed in (continuity to its post proves the right conductor before the crimp) and crimped beyond the post tips with ordinary dies while the even conductors wait lifted; then a narrow tongue nest loads the even contacts between crimped neighbours and narrow stepped dies crimp them. A backing blade drops behind every barrel and the housing slides 14 mm along all the posts at once, seating every contact on what is then its own header for the continuity and shorts test.

- contacts: either loose or strip · steel: made dies (EDM, machined, laser-cut) · meeting: the housing locates the contact.
- **Branch of** a4b.
- **Combines:** [into-the-housing/i6b](../into-the-housing/summary.md), [into-the-housing/i2b](../into-the-housing/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Splay and strip, loading the housing onto the bed and the ribbon into the root comb and loft, keeping the contact supply filled, and labelling.
- **Major unresolved problems:**
  - Narrow stepped dies for the even pass (made, not bought)
  - The post's path through each cavity
  - Posts 17-19 mm free are soft (1.2-1.7 N/mm); whether the box stays square as the wings curl
  - Front-wall thickness, which sets the 14 mm push
  - Whether laid-in strands close continuity before the crimp

### [a5 — The housing is the fixture: stage a bare contact in its cavity, crimp at the mouth, push home](ideas/a5-housing-as-fixture.md)

A post through cavity k's front opening takes a bare contact from a lance-grooved shuttle nest and pulls it 1.5 mm into the rear mouth, the lance still 0.9 mm outside; the camera measures the depth. The housing nest floats +/-0.2 mm in X and Z, so a fixed anvil rising under the barrels sets the line; seated wires are swept 20-35 deg and waiting conductors wait lifted. Conductor k is laid in and crimped at the mouth, a fork proof-pulls it at 20 N while still unlatched, then pushes it 5.25-5.45 mm home; force, a 5 N pull and the dark square confirm the seat.

- contacts: either loose or strip · steel: any of several · meeting: the housing locates the contact.
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Staging supply (nozzle and shuttle, a3's rail, or Derek at the lit cavity when asked), splay and strip, loading and unloading housing and ribbon, and the continuity test.
- **Major unresolved problems:**
  - Dies within ~1 mm of the housing face, and the lance window there (~0.06 mm on a flat anvil; lance slot otherwise)
  - Conductor k carries the 5.3 mm push as a 6-8 mm hump (or web follows the push, or x3)
  - Mouth clearance, rear-mouth geometry and front-wall thickness (unmeasured)
  - Whether the staged contact stays square as the wings first curl
  - Two-ribbon housings

### [a6 — The post is the gripper: one header pin carries every contact from its supply to the die](ideas/a6-post-is-the-gripper.md)

One travelling post head carries a hardened near-pointed 0.64 mm pin standing 1.5-1.8 mm out of a steel holder whose face is the box-front datum, a stripper, a float of +/-0.2 mm sideways and in Z, a force sensor and a backstop blade. It spears kit contacts lying barrels-up in lance-grooved channels of a tapped pocket plate on a light pad (or the leading contact of a strip, whose tab it cuts before any wire exists), measures each in silhouette on the post, and sets it on an open knife-set die at the die fiducial plus the measured offset. The float's preload is the hold-down, the punch centres the barrels, and the pin retracts to release.

- contacts: either loose or strip · steel: bought mini-applicator or knife set · meeting: a general-purpose arm or gantry hand.
- **Branch of** a4.
- **Combines:** [machine-that-sees-and-learns/v4b](../machine-that-sees-and-learns/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Pouring a unit's contacts on the plate or mounting a strip, splay and strip, insertion (the pin occupies the box front), and the queue.
- **Major unresolved problems:**
  - The grip of a kit contact on a 0.64 mm pin
  - Pocket plate fill rate and pose odds; whether a kit contact rests nose-up or nose-down without a groove
  - The head's small mechanism: retractable pin in a 2 mm holder, two-way float, backstop, force sensing
  - Pin wear over ~3,500 spears
  - The die outside an applicator and its lance relief

### [a7 — If the contacts switch to genuine SXH strip: what changes, arrangement by arrangement](ideas/a7-if-the-contacts-switch-to-strip.md)

A map, not a machine: what a switch to genuine SXH-001T-P0.6 on strip, a clone reel, loose kit or BXH contacts, or pre-formed keyhole contacts (change-the-question c6) does to every arrangement in the study. Pose is given, a carrier must be cut and its stub inspected, the next contact stands beside the die, genuine or pre-formed wings may be narrow enough to preload every cavity (but not to crimp every preloaded contact in one pass), the die must fit the contact, and a JST crimp-height target exists. Tables classify roughly 85 contact-handling arrangements: about half need strip, a fifth need loose, a third take either.

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module).
- **Automates:** —.
- **What the person still does:** The decision itself, buying one strip, and the measurements that settle genuine wing width and die match.
- **Major unresolved problems:**
  - Genuine open-wing and conductor-barrel widths
  - Which contact the OTP applicators and knife sets are cut for
  - Whether kit contacts carry tab stubs (evidence of a clone reel)
  - Lance catch of genuine contacts in kit housings

### [x1 — The post feeds the hand tool: kit contacts into the SN-2549's XH nest with no fingers](ideas/x1-post-feeds-the-hand-tool.md)

a6's post head spears a kit contact from a lance-grooved pocket plate, measures it on the post, and slides it along its own axis into the open XH nest of the SN-2549 lying in hand-tool-as-press a1's cradle, stopping at a jaw fiducial plus the measured offset; the cradle's pusher closes one ratchet click, the pin stays in the box while the conductor enters from behind, and the tool crimps. The motorless form is the post pen: a header pin in a printed pen with a stripper slider, a grooved spear block, and a printed fence on the jaw's M4 screw, giving the SN-2549 an axial locator for loose kit contacts on day one. A stub-pen variant bonds a cut XHP stub (into-the-housing i2d) to the pen face and wires the pin for continuity before the squeeze.

- contacts: loose kit contacts · steel: SN-2549 or similar hand-tool dies · meeting: conductor brought to a fixed die · usable without a motor.
- **Branch of** a6.
- **Combines:** [hand-tool-as-press/a1](../hand-tool-as-press/summary.md), [force-and-form/f1](../force-and-form/summary.md), [borrowed-machines/b2](../borrowed-machines/summary.md), [into-the-housing/i2d](../into-the-housing/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Pouring contacts, split and strip, insertion and the queue; with the pen, everything except the precise axial placement stays with the person.
- **Major unresolved problems:**
  - The SN-2549's jaw front face and nest position relative to the box and neck
  - The ratchet's behaviour on a failed feed
  - The kit contact's grip on the pin
  - The kit bag's box-to-barrel spread, which the pen relies on
  - Whether the SN-2549's XH nest makes a good crimp on this ribbon (unchanged by x1)

### [x2 — Crown station, then sort and push: one web clamp from reel to latched housing](ideas/x2-crown-then-sort.md)

A ribbon carriage on an MGN12 rail holds the web clamp and a 3.5 mm fan comb; at station A (a2d) each conductor is crimped flat over the crown from a thinned reel, then a pull fork on the crown land and the carriage's Y give it a 20 N proof pull. The carriage docks at station B (into-the-housing i6), where a6's post head, with a fork behind the insulation barrel to react the spear, picks each crimped contact by its box front and lowers it 6-10 mm into its slot of a 2.5 mm target comb, lower layer first, centre outward. A backing blade drops behind the row and the nest drives the housing onto it; the cell trace and a per-wire pull-back confirm each latch.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die.
- **Branch of** a2d.
- **Combines:** [into-the-housing/i6](../into-the-housing/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Splay and strip, loading the ribbon end and the housing, trimming J2's and J7's unused conductors (or a snip), labelling, the far-end continuity test, and emptying cups.
- **Major unresolved problems:**
  - Roll of a staged crimped contact against what the 0.60-0.70 mm box entry accepts
  - The 11-26 mm split plus i6's 6-10 mm set step behind the housing
  - a2d's die, pitch and temper questions
  - The fork's tines bearing on crimped insulation barrels

### [x3 — Stage every other cavity, crimp, leave, one push](ideas/x3-stage-crimp-one-push.md)

A floating housing nest and the web clamp ride one X stage past a fixed station: a5's staging post pulls bare contacts from a lance-grooved shuttle 1.5 mm into every odd cavity, and each odd conductor is laid in and crimped at the mouth while the even conductors wait lifted. Then each even contact is staged beneath its lifted conductor between crimped neighbours and crimped by a narrow stepped crimper whose walls land on the anvil's shoulders. After a per-wire 20 N proof pull against a slotted blade, the nest drives the housing 5.25-5.45 mm onto every staged contact at once, so no conductor stores any length.

- contacts: either loose or strip · steel: made dies (EDM, machined, laser-cut) · meeting: the housing locates the contact.
- **Branch of** a5.
- **Combines:** [into-the-housing/i2b](../into-the-housing/summary.md), [into-the-housing/i2](../into-the-housing/summary.md), [into-the-housing/i6](../into-the-housing/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Splay and strip, housing and ribbon load and unload, the contact supply, the far-end continuity test, and labelling.
- **Major unresolved problems:**
  - Narrow stepped dies (3.1 mm step, 0.8 mm walls, +/-0.05 mm)
  - The lance and a flat anvil at the mouth (fits about half the clone range; lance slot otherwise)
  - Whether a crimped contact stays staged at 1.5 mm with the post gone (mouth friction)
  - The web's Y and the per-conductor hump trim
  - Front-wall thickness

## Combinations with other explorers

- x2 = terminal-supply a2d (thinned reel over a crowned anvil) + into-the-housing i6 (sort then push) + terminal-supply a6's post head as the sorting hand, with a fork behind the insulation barrel; branches: loose contacts at the die (a6's head does both jobs), a2b's tag as the handle, i6b's post bed with i6's fingers (into-the-housing's T1)
- x3 = terminal-supply a5 (staging post, lit square) + into-the-housing i2b (stage every other cavity, crimp in place, one push) + i2's floating nest and narrow stepped dies + i6's layer order (into-the-housing's T2)
- a4c = terminal-supply a4b (post through the cavity, crimp on its tip) + into-the-housing i6b (bed of wired posts, one housing move) + i2b's odd-then-even order: bare contacts crimped on posts, identity proven before each crimp, nothing stored
- x1 = terminal-supply a6 (post head) + hand-tool-as-press a1 (SN-2549 squeezer cradle; same fit for force-and-form f1 and borrowed-machines b2); stub-pen variant adds into-the-housing i2d's cut housing stub (T3)
- a6 = terminal-supply a4's post + machine-that-sees-and-learns v4b pocket plate + machine-that-sees-and-learns' loading nest for a4 (a post pushed into a box against a wall)
- K1 (proposed in terminal-supply on borrowed-machines): borrowed-machines b8 spool-fed line supplying a flat end to a2d's crowned station, so the ribbon never folds
- a2d + machine-that-sees-and-learns v1 (gate, visual servo) and v3 (stepper-wedge stop sweep): the watched strip station with a level view and 100 identical contacts for a crimp-height campaign
- a2d's elastic skip-2 crown as the strip feed for into-the-housing i2's strip branch and force-and-form f8 (kept neighbour 1.2-2.0 mm under the housing) (T5)
- a3's hanging rail over a rear-face-up housing with a depth-stop post, staging odd cavities for x3 or into-the-housing i2b (T4)
- The lit cavity square (machine-that-sees-and-learns v6, a4b) as a per-cavity seat check after any gang push: into-the-housing i3, i6, x3 (T6)
- a6's post pick, silhouette and two-way float as the bare-contact pick and wrist specification for into-the-housing i4 (T7)

## Transferable mechanisms

- A lance groove (1.0 mm wide, >= 1.0 mm deep) along every pocket a bare contact lies in barrels-up; without it the contact rocks 8-22 deg on its lance and its box entry stands 0.9-1.7 mm high
- Post capture is set by the box's 0.60-0.70 mm entry: +/-0.08-0.31 mm by pin-tip chamfer; grind the pin near-pointed
- Cut the carrier before the wire exists: once a ratchet click or a post in the box holds the contact, a flush cut from above works and the stub is set from the contact's own rear edge
- Skip-pitch strip: remove every other contact; the pilot holes stay (they belong to the carrier), the next contact is 14.2 mm away, the removed ones are loose stock
- An elastic crowned anvil (R 25-30 mm) drops the next kept contact below the station plane; wrap tension is the hold-down and the view across the station is level
- A flat skip-2 strip already lets a 4P or 5P lie flat beside a narrow knife-set blade (fan pitch 2.5-2.8 mm)
- A pull fork on the anvil land behind the crimped insulation barrel, with the carriage pulling the web through a load cell: a proof pull at the crimp station, before insertion
- One-sided drop-shear against a clamped upstream edge: the kink lands in scrap after the next index
- The post as a pick tool: a pin in the contact's own box, holder face as box-front datum, stripper sleeve release, a float that goes both ways in Z as the hold-down
- Measure every waiting contact and correct by a fence or axis, instead of teaching once per reel
- Reject a bad contact by shearing it without a wire
- Crimp every contact of a housing at one Y when one move seats them; any Y stagger is stored in the finished loom
- Stage depth is a dial from 1.5 mm inside the mouth (5.3 mm push, dies at the housing face) to 7.5 mm out on posts (14 mm push, dies clear)
- A bed of wired posts at 2.50 mm through the housing holds bare contacts for crimping, proves each conductor is in its contact before the crimp, guides the single push and becomes the test header
- A housing nest that floats +/-0.2 mm in X and Z lets a fixed anvil set the line with no per-cavity measurement
- The web clamp rides the housing's stage once a contact latches
- The web can follow a one-at-a-time push instead of storing length in the conductor; the waiting conductors, not strand fatigue, limit it
- Gravity staging into a housing needs a depth-stop post, or the contact slides to its lance's stop (~2.4 mm)
- Two-point grip: a pin in the carrier tag's hole plus fingers on the crimped insulation barrel
- Post pen: a header pin in a printed pen with a stripper slider against a printed fence on the jaw: an axial locator for loose contacts in a cheap hand tool
- A hanging contact over black rail edges lit from below is a silhouette whose notch shows which way the U opens
- Stationary notched lifter bar: the ribbon moves past it and only the conductor in the notch lies at carrier height
- A hard stop in a short steel loop sets crimp height and a preloaded disc-spring stack caps force, so a light actuator on a lever or screw is enough

## Key findings

- [calc: explorers/terminal-supply/calc/w3.py s1] Post capture is set by the box entry (0.60-0.70 mm), not the box inside: +/-0.08-0.13 mm with a 0.1 mm chamfer, +/-0.18-0.31 mm near-pointed; a camera-steered head needs +/-0.04-0.07 mm. The earlier +/-0.4/+/-0.6 mm figure is withdrawn
- [calc w3 s2; into-the-housing exchange_terminal_supply_w3 E] A barrels-up contact on a flat floor rocks 8-22 deg on its lance with its box entry 0.9-1.7 mm high; a 1.0 x >= 1.0 mm lance groove puts the entry at floor + 1.10-1.18 mm
- [calc w3 s3; ith-w3 A, B] The push after a crimp is 5.25-5.45 mm from 1.5 mm staging (a5) and 13.95-14.45 mm from a 9 mm post (a4b); seated one at a time, conductor k carries it as a 6-8 mm or 11-15 mm hump. A single push after every crimp (x3, a4c) stores nothing
- [calc w3 s3] Seated conductors bowed by a web that follows each push see 0.7-1.5 % strand strain, hundreds of bows to failure against at most eight per housing [estimated Coffin-Manson constants]
- [calc w3 s4] A flat anvil's front edge fits between lance and conductor barrel in about half the clone range: -0.30 to +0.10 mm on xh-facts' 2.4-2.6 mm lance tip, -0.34 to +0.26 mm on into-the-housing's 2.24-2.64 mm; the rest need a lance slot
- [calc w3 s5] a2d's punch holder must clear crimped neighbours' boxes (half-width 0.98): fan pitch p >= 2.5-2.8 mm for 2.5-3.0 mm blades, blade standing >= 1.8-1.9 mm out of its holder; at that pitch a flat skip-2 strip already clears 4P and 5P ends
- [calc w3 s6] In x2 the spear on a staged crimp needs a fork: 20-30 mm of free conductor buckles at 0.17-0.39 N against a 0.2-2 N spear; at the 2.5 mm target row the tines clear by +0.30 mm and the holder by +0.52 mm; 2.7-3.2 h per unit
- [calc w3 s7; ith-w3 C, J] At 2.5 mm pitch only narrow stepped dies work in the even pass (+0.20 mm conductor step, +0.17-0.28 mm insulation step); waiting conductors must be lifted for ordinary 3.5-4.0 mm punches; genuine narrow wings allow preloading every cavity but not crimping every preloaded contact in one pass (0.00-0.11 mm)
- [calc w3 s8] Posts 17-19 mm free are 1.2-1.7 N/mm and buckle at 19-24 N; the dies work 1.0-4.5 mm beyond the post tips, so bare neighbour posts never meet them; a 2.54 mm header bed is off +/-0.16 mm on a 9-way
- [calc w3 s9] A 5 N seat pull is 26-34 % of the 14.7-19.6 N retention range; force ladder: 5 N latch test < retention < ~20 N proof pull < 39.2 N pull-out
- [calc wave2 s1-s2, s7] With every other contact removed, the program uses 0.89 of one 8,000 reel ($35 more at LCSC); an elastic R 25-30 mm crown drops the next kept contact's wing tips 0.5-1.2 mm below the plane
- [a7, estimate] Of ~85 contact-handling arrangements across the study, about half need strip and cannot use the kit contacts, about a fifth need loose contacts, about a third take either; pre-formed contacts (change-the-question c6) are a fourth supply
- [source: sourcing/amazon-prime.md] No Prime listing exists for XH strip, OTP applicators or knife sets; the VEVOR AP-1 1 t arbor press (150 mm opening, 81 mm throat, $61.90) takes a knife-set block but not an applicator (166-176 mm)

## Where this view still had trouble

- Genuine JST contacts, if their wings sit inside 1.95 mm, in a fully automated loose path: every wing-as-head orienter (a3's rail, the pocket plate's rejection of barrels-down contacts) fails, and only strip or a camera-checked post pick remains
- Holding a crimped contact for insertion: the post, the housing and a post bed all want the box front, so the post head cannot hand a crimped contact onto a bed post; only fingers on the barrels or a carrier tag remain, and both have unresolved fits at 2.5 mm pitch
- Using the kit contacts in the strip-bound routes (a1, a2, a2d, x2): re-carrying loose contacts on tape was parked, and nothing else puts kit contacts back on a pitch a strip station can index
- A loose-contact magazine that rides a travelling crimp head (force-and-form f4's head going to the wire): this view pictured supplies at fixed stations only
- Die steel: every station here leans on OTP knife sets (no Prime listing, unknown fit to genuine SXH) or on narrow stepped dies someone must make; no cheap, stocked source of fitted die steel was found
- Keeping a staged, crimped contact in a housing mouth at 1.5 mm while its neighbours are crimped, without a post in it: mouth friction is unknown and no mechanism beyond leaving a post in was found
- Splitting and stripping soft silicone: this view hands them back everywhere and did not develop a supply-side answer

## Questions for Derek

- Would you buy one 100-piece SXH-001T-P0.6 strip (Digi-Key 455-1135-100-ND, $4.71)? It settles pitch, pilot hole, tab, genuine wing and conductor-barrel width and contact length for about a dozen explorers. Bent round a ~50 mm bar and released, does it spring back flat (a2d's crown radius)?
- One kit contact laid barrels-up on a card and photographed side-on: does it rock on its lance, nose up or nose down? It decides the lance groove in every bare-contact pocket
- One kit contact latched in a kit housing: how far inside the rear face is the box front, or how thick is the front wall? It sets every push after a crimp (a4b, a5, x3, a4c)
- The SN-2549's XH anvil from the side, and one kit contact side-on: is there a lance relief, and where is the lance tip against the conductor barrel? Flat anvil or lance slot
- Do the CQRobot kit contacts have a small tab stub at the rear of the insulation barrel (cut from a clone reel)?
- Twenty kit contacts on a light pad in one photo: open-wing and box widths for the bag, box-to-barrel spread (the post pen's exposure) and pose odds
- A 0.64 mm header pin pushed into a kit contact, weights hung until it slides off: the grip a4, a4b, a4c, a6 and x1 depend on. Are the Prime-listed header pins really 0.64 mm square?
- An XHP-4 held against a flashlight, square-on from the rear: is there a straight line of light through each cavity (a4b, a4c, a5, x3)?
- How much split behind a housing is acceptable on a finished loom (9-26 mm in a2d and x2, plus i6's set step)?
- Would removing every other contact from a strip be acceptable if it lets the ribbon lie flat?
- Would you try the post pen by hand on the SN-2549?
- For machines: genuine SXH strip, a clone reel (under a cent each), the kit contacts, or pre-formed contacts? a7 sets out what each opens and closes
- Would you request JST's XH handling manual through their licence form for the genuine crimp-height target?
