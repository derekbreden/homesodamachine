# Notebook: machine-that-sees-and-learns

This is the running log for wave 1. It records what was read, what was
computed, the directions set aside with what would revive them, and questions.

## Read

- **Study context.** `context/brief.md`, `shared-context.md`,
  `working-method.md`, `xh-facts.md`, `prior-art.md` and the context
  `sourcing-requests.md`.
- **Repo camera tooling.** `tools/panelcam.sh`, `tools/panelcam-uvc/uvc.js`,
  `tools/panelcam.targets.conf`.
  - The ELP's focus register has static friction.
  - A 10-unit step does not move it.
  - Where it lands depends on direction by ~60 units, so focus is walked
    upward in 20-unit steps.
  - Full resolution comes only as MJPG over USB 2.0, and YUV arrives torn.
  - macOS grants the camera only to an app (`PanelCamShot.app`).

  All of this carries straight into any cell here.
- **Repo tools ledger** (`hardware/ledger/tools.md`), for the ELP, Revopoint,
  scale, NEMA 23 and ESP32 stack.
  - Its note that the panelcam sits "~33 cm" from the panel does not agree with
    a 4.8 mm lens and the 36 px/mm the targets file implies; that pair implies
    ~12.5 cm [calc: vision_budget §0].
  - One of them is off. A ruler photo settles it, and nothing here depends on
    which.
- **Sibling explorers' idea titles and openings**, to avoid rebuilding their
  presses, supply and insertion mechanics. Cross-links are in the idea files.
- **Web**:
  - LeRobot SO-101 and imitation-learning docs;
  - SO-ARM100 README (BOM cost);
  - Waveshare ST3215 (4096-count sensor);
  - Dobot MG400 (±0.05 mm);
  - OpenPnP feeders and ReferenceHeapFeeder;
  - FlexiBowl;
  - Raspberry Pi HQ camera (raspberrypi.com, Adafruit);
  - Creality Ender-3 V3 SE;
  - Anthropic vision docs (visual tokens = ⌈w/28⌉·⌈h/28⌉; coordinates and
    counts approximate);
  - Anthropic model prices from the claude-api skill's table cached
    2026-09-25.

  The session's web-search allowance ran out early. Everything after that came
  from direct page fetches of known URLs, or is labelled as an estimate or
  assumption.

## Computed

- `calc/vision_budget.py`:
  - px/mm, field, depth of field and diffraction for six camera set-ups;
  - pixels across each crimp feature;
  - crimp-height repeatability by silhouette;
  - non-telecentric scale error;
  - axial and lateral room at the nest;
  - strand height after lay-in.
- `calc/cycle_and_cost.py`:
  - per-crimp and per-unit time for v1 and v6;
  - Claude image cost per call, per unit and per program;
  - log size.
- `calc/campaign.py`:
  - v3 sweep size, time and consumption;
  - samples per level against pull scatter;
  - what force monitoring can see per missing strand;
  - a camera-read steel leaf as a force gauge;
  - proof-load levels.
- `calc/arm_and_feeder.py`:
  - SO-101 tip resolution against XH tolerances;
  - transfers and teaching time;
  - lit-tray taps per pick against pose odds.

## Directions set aside, and what would revive them

- **Depth from focus.** Reading how high a conductor sits in the U from the
  focus value that sharpens it.
  - At 45 px/mm the depth of field is ~4 mm, and the lens lands ±60 units
    depending on direction. Depth resolution would be millimetres, not the
    tenths needed.
  - The side silhouette does the job directly.
  - *Revive if* a set-up with sub-0.5 mm depth of field (C′ or D in the budget)
    shows a repeatable focus curve.
- **Claude measuring dimensions.** Anthropic's docs call Claude's spatial
  outputs approximate. Numbers stay in OpenCV, and Claude judges.
  - *Revive* only as a cross-check that flags a gross disagreement with
    OpenCV.
- **Imaging mid-stroke.** Once the punch surrounds the wings the contact is
  hidden from every side but the box end.
  - The force trace carries the stroke.
  - *Revive if* a press is built with a thin, open-sided die, where a
    silhouette through the die gap might show the wings curling.
- **Crimp without a nest, contact located only by vision on a flat anvil.**
  Vision can find it, but nothing holds it when the punch touches the wings
  off-centre. The nest stays.
  - *Revive if* a punch geometry is found that self-centres a loose contact.
- **Learning the crimp by trial on the machine (reinforcement-style).** Each
  trial costs a contact and a destructive test, and the parameter space is one
  or two knobs. A sweep, v3, finds the window in one night.
  - *Revive if* many coupled knobs appear: two-stage forming, insulation
    height, strip length and insertion depth all at once.
- **A Revopoint MINI 2 scan of every crimp.** 0.02 mm stated [repo: tools.md],
  but slow, with mesh processing per part, and at its accuracy limit on a
  0.9 mm feature.
  - *Revive* as a calibration reference beside the point micrometer for v5's
    silhouette height.
- **Using an H2C as the robot.** Busy ~100 h per unit and not an open G-code
  port.
  - *Revive if* a third printer or an idle period appears.
- **The Bambu Vision Encoder as a camera calibration target.** It is a
  precision pattern plate made for the printer's own camera.
  - Using it to calibrate the cell's stage and camera is untested, and its
    pattern and tolerances were not looked up.
  - *Revive* when building v1b's stage calibration.
- **Ultrasonic in-die crimp verification** (NASA, prior-art §6). It detects
  under-crimps and missing strands during the stroke.
  - Transducers in small XH dies are a research project.
  - *Revive if* the camera and force checks prove blind to a failure that
    matters.
- **A precise desktop arm (MG400 class) in place of the SO-101.** It would
  remove the micro stages at the docks, but not the need for pictures.
  - Price not observed.
  - *Revive* when an arm is wanted for insertion and v2's docks prove fiddly.

## Things that surprised me

- **Silver on silver.** Tinned strands in a tin-plated barrel are the one thing
  a camera is worst at. The design routes around it:
  - the tip is inspected alone on a backlight;
  - stray strands are sought outside the contact's outline on black;
  - strands above the wing tips are sought in silhouette.
- **The destroyed test crimps are the labels.** The camera checks become
  trustworthy only because v3 destroys crimps whose pictures were taken first.
  Without that, "the camera says it's good" means nothing.
- **Force monitoring barely helps on 60-strand wire.** One strand is 1.7 % of
  the copper [calc: campaign §3]. The camera at the stripped tip is the only
  guard against a few cut strands.
- **Claude is cheap per crimp.** ~$1–5 a unit to judge every crimp at
  Opus rates with thinking; much less on borderlines only. Its limits are
  about measurement, not cost.

## Questions for Derek

The explorer's summary goes back to the coordinator as the wave's structured
return; this harness does not let an explorer write `summary.md` itself.

1. **JST's manual.** Would you request JST's XH handling manual (CHM-1-151)
   through their licence form? It emails the crimp height for genuine
   SXH-001T-P0.6. It would be a reference point for v3, which is still needed
   for kit contacts on silicone.
2. **The ELP up close.** At the ELP's nearest focus, how many pixels span a
   millimetre? One photo of a steel rule answers it. Is the panelcam rig about
   12 cm or 33 cm from the panel?
3. **Contact photos.** Could you photograph one kit contact, and one inside a
   kit housing, under the ELP: top and side, on white and on black? That shows:
   - whether the box top is flat enough for a vacuum nozzle;
   - which face the lance is on;
   - how visible the strands are in a laid-in barrel.
4. **The web.** Does the ribbon's web zip apart cleanly by hand, or tear? That
   is Open item 5. It decides between blade, laser and peel for v6's split.
5. **Micrometer.** Is a point (crimp) micrometer welcome on the bench? It is
   what calibrates every silhouette height here.
6. **Contacts for production.** Kit contacts, or genuine SXH (on cut strip or
   reel) or BXH loose? The feeder (strip versus v4) and v3's comparison both
   depend on it.
7. **Teaching an arm.** Does teaching an arm sound like fun or like a chore? v2
   costs ~4–6 hours at the leader arm, plus corrections.
8. **The queue.** Would you like the cell to message your phone with a photo
   and a proposed answer when it is unsure, or would you rather it wait until
   you come to the bench?
9. **Proof pulls.** Every production crimp (~20 N, adds ~15 s), or a sample?
10. **A dedicated printer.** Is a dedicated $199 bed-slinger acceptable as a
    stage, or would you rather build the stage from V-slot and printed parts?

---

# Wave 2

## Read

- The critique of this view by ribbon-as-pallet:
  [`../../exchange/ribbon-as-pallet--on--machine-that-sees-and-learns.md`](../../exchange/ribbon-as-pallet--on--machine-that-sees-and-learns.md),
  with its calc P.
- Every explorer's wave-1 `summary.md`.
- change-the-question's [c1b](../change-the-question/ideas/c1b-tack-first.md)
  and force-and-form's [f9](../force-and-form/ideas/f9-tack-station-feeds-crimp-station.md),
  and force-and-form's wave-2 calc §5 (the insulation crimp on silicone, tack
  grip), §10 (hit and re-touch) and §11 (proof pull on the box's rear face).
- The repo's panelcam files again, for the capture app:
  - the lens parks when a stream starts;
  - cameras are named, never numbered;
  - MJPG only;
  - fixed white balance and exposure.
- **Fetched 2026-09-28:**
  - Klipper's Load_Cell page: HX711 80 SPS, HX717 320 SPS, `trigger_force`,
    `force_safety_limit`;
  - FluidNC's GitHub README: ESP32, YAML config, servos, probe inputs;
  - ntfy's publish docs: attachments, up to three action buttons, http actions;
  - Claude Code's headless docs: `claude -p`, `--output-format json`,
    `--json-schema`, `--resume`, `--allowedTools`, `total_cost_usd`.
- **Failed:** FluidNC's wiki (connection refused). The README carried what was
  needed. No web search was used in this wave.

## Computed

`calc/wave2.py` → `calc/wave2.out.txt`:
1. The box as a roll gauge in the side silhouette, and the crimp-height
   correction.
2. Lateral capture by bundle width; groove-exit error; axial window used by
   strip scatter.
3. Where each control loop closes: travel and force overshoot per decision
   latency, samples through compaction, loop time scales.
4. Camera timing per lighting state; why one stream per run.
5. The tack:
   - forces and drives;
   - anvil stress;
   - wing-contact order in a one-stroke crimp;
   - the grip window;
   - jacket stretch on back-out;
   - cycle time.
6. Coupon grips: bare-copper wrap against a soldered lug.
7. Ask rates, person minutes and supervisor cost per unit by phase.
8. The first day, hour by hour.

## What changed in the ideas, and where it came from

| Idea | Change | From |
|---|---|---|
| v1 | Neighbours held 5 mm up, each lowered by a hinged key, so the side view runs under them | ribbon-as-pallet Break v1-1, Repairs A and B |
| v1 | One hover picture predicts X and Y. X is checked, not searched. Y is read per conductor from tip and edge | ribbon-as-pallet's "X in a funnel"; this view's calc §2 on splayed tips and strip scatter |
| v1 | Proof-pull reaction by supply form; tab cut by drop-shear | ribbon-as-pallet Break v1-2; this view's exchange on terminal-supply |
| v1 | Continuity channel; XH end first | ribbon-as-pallet transfer |
| v1 | Roll from the box's own silhouette | New in this view (calc §1) |
| v1b | Steel-on-steel seat; tail in a cup with a pogo block | ribbon-as-pallet Break v2-1 and v1b note |
| v2 | Steel docks; arm wander corrected to ±2–6 mm; the arm's job shrank; backshell branch | ribbon-as-pallet; borrowed-machines' servo figures |
| v3 | Knob by hit and re-touch; coupon grips; contact-side reaction; ribbon-end coupons; insulation and tack arms | force-and-form wave-2 §10, §5; ribbon-as-pallet Break v3-1, C3 |
| v4 | Lance tilt; sprung nozzle; where a nozzle can deliver; the strip as the other singulator | ribbon-as-pallet; this view's exchange on terminal-supply |
| v4b | 2.05 mm floor; hanging-plate and cassette branches | terminal-supply slot calc; ribbon-as-pallet C4 |
| v5 | Roll flat, box gauge, lance-notched stop, pallet mode | ribbon-as-pallet Breaks v5-1, v5-2, C2 |
| v6 | Split on ribs in an under-width channel; insertion along the wire with the latch seen through the mating face; crossings by tweezer or hand; spool branch | ribbon-as-pallet Breaks v6-1, v6-2, transfers |
| v7 | New: the run | Coordinator's suggestion; digest's least-developed list |
| v8 | New: tack, look, then crimp | c1b and f9, seen from this view |

## Where this view disagrees with the critique

ribbon-as-pallet argues that once the channel and flush cut register every
conductor, "a picture then checks rather than finds".

- For X on a good tip, agreed.
- For Y, no. The flush cut sets the tip, but the window is set by each
  conductor's own torn insulation edge. Strip scatter of ±0.1–0.3 mm uses
  20–120 % of a 0.5–1.0 mm window [calc §2].
- For bad tips, no. A splayed bundle halves the lateral capture, and a 2–3°
  groove exit uses what is left.

The picture's work is on exactly the cases the pallet cannot promise, and on
recognising that they are those cases.

## Directions set aside in wave 2, and what would revive them

- **A tilted side view past in-plane neighbours.**
  - At 9.9–11.9° it mixes ~0.3 mm of crimp width into the height.
  - *Revive* only as a strand-above-wing check, never for height.
- **A capstan grip on coupons.**
  - The jacket shears at the drum entry, and short coupons cannot wrap.
  - *Revive* with ~200 mm coupons, a large rough drum, and a test showing the
    jacket survives 100 N.
- **The Mac closing the force loop.**
  - Fine on an ordinary day, ruinous on a bad one [calc §3].
  - *Revive* as a monitor only.
- **Claude in any second-scale loop.**
  - *Not revived.* It judges borderlines and trends.
- **One app launch per picture for a cell.**
  - Each launch re-parks the ELP's focus.
  - Fine for the panelcam's occasional shots. Not for runs.
- **Rear-face-up insertion from a horizontal pallet.**
  - It leaves a quarter-bend in every conductor, and the housing tethers the
    pallet.
  - *Revive* if the housing, not the conductors, turns through 90°, e.g. a nest
    that rotates after each latch. The tether remains.
- **Tacking a contact held on a 0.64 mm post.**
  - Post grip and tack grip are the same size.
  - *Revive* with a stripper fork pushing the box off the post.

## Things that surprised me

- **The box is a roll gauge.** The contact's own square box, in the same
  silhouette as the crimp, reads roll to a fraction of a degree. Nothing needs
  to be added to see it.
- **Insulation first is already the one-stroke order.** On the clone
  dimensions, a one-stroke crimper meets the insulation wings before the
  conductor wings. A tack is that order with a pause in it.
- **Slowness makes even a slow computer fast enough, on a good day.** At
  0.05 mm/s a 30 ms USB round trip is 1.5 µm. The case for the MCU owning the
  stroke is the bad day, not the typical one.

## Questions for Derek (wave 2)

1. **Control.** Which feels like home for the bench: your own PlatformIO
   firmware on an ESP32 beside a printer as bought, FluidNC, or Klipper?
2. **Claude's say.** May Claude pass a borderline crimp on its own, with every
   such pass logged and later checked against its measurement? Or should it
   only propose?
3. **Phone.** Would you like asks as a push with a photo and three buttons
   (ntfy, self-hosted or with a random topic), through a Claude session you
   follow from the phone, or only at the bench?
4. **The tack test.** Close a kit contact's insulation wings lightly on the
   ribbon with smooth pliers, then pull with a hook and the 0.1 g scale. Does
   it hold ~0.2 N and slide off at ~1–2 N without marking the jacket?
5. **The neck.** Under the ELP, how long is the gap between a kit contact's box
   and its conductor barrel, and where does the lance tip sit? It decides the
   loose-contact proof stop and v8's back-out shoulder.
6. **A running Mac.** Is leaving a Mac awake for a run acceptable, or would you
   rather give the cell its own small computer?
7. **Wave-1 questions still open:** JST's manual; the ELP's px/mm at nearest
   focus; contact photographs; whether the web zips; a point micrometer;
   contacts for production; arm teaching; proof pulls on every crimp or a
   sample; a $199 printer as a stage.

## Wave 3, exchange with hand-tool-as-press

- **Read.** hand-tool-as-press's summary, all eleven idea files, its three calc
  outputs and notebook; into-the-housing's wave-2 critique of it and that
  explorer's exchange calc; force-and-form's wave-2 insulation section;
  ribbon-as-pallet's calc P; the Prime listings.
- **Wrote.** `../../exchange/machine-that-sees-and-learns--on--hand-tool-as-press-w3.md`;
  `calc/w3_on_hand_tool_as_press.py` → `.out.txt` (§1–10);
  `sketches/make_sketches_w3.py` → `w3-t-then-c.svg`; Wave 3 rows in
  `sourcing-requests.md`.
- **Found against this view's own files, to carry into v1, v5 and v8:**
  - The SN-2549 as sold cannot be fed by v1's pallet at 5 mm pitch; its jaw
    spans the neighbours. v8's C hosts divide into narrow-punch hosts (a4 one
    nest, a narrow knee punch) and hosts where the ribbon leaves the pallet.
  - v1's "punch under ~8 mm at the neighbours' height" is ≤ 7.45 mm with
    crimped neighbours and 0.3 mm clearance.
  - v1's key root sets copper (R 24–60 mm; 47–81 % of the bend kept by
    hand-tool-as-press's exchange table): a 5–12° kink 20–30 mm behind every
    contact.
  - The lance tip to design to is 0.24–0.64 mm behind the box, not 0.4–0.6.
  - v8's forming cell belongs under the nest, not in the former's link, and at
    20 kg, not 10: the loose stop carries the servo's excess.
- **Surprise.** JST's own strip-length form, run on the clone drawings, gives
  exactly KONNRA's 1.6–2.1 mm; run backwards from JST's 2.4 mm it gives a
  genuine barrel of ~1.8–2.05 mm, which Engineer's 1.8 mm PA-09 die also
  suggests. The digest's strip-length disagreement may be two barrels.

---

# Final pass

## Read

- borrowed-machines' exchange on this view,
  [`../../exchange/borrowed-machines--on--machine-that-sees-and-learns-w3.md`](../../exchange/borrowed-machines--on--machine-that-sees-and-learns-w3.md),
  with its calc [`exchange_sees_learns_w3.out.txt`](../borrowed-machines/calc/exchange_sees_learns_w3.out.txt).
- borrowed-machines' b1, b1b, b1c, b3 idea files; their `wave2.out.txt` (§1–3,
  §5) and `cycle_and_arm.out.txt` (§2).
- hand-tool-as-press's a4c, a6b, a6c and force-and-form's f9b openings: the
  tack-station pairings this view proposed in its exchange with
  hand-tool-as-press already stand as those explorers' idea files, so this view
  links them instead of duplicating them.
- The Prime listings in `../../sourcing/amazon-prime.md`.
- **Fetched 2026-09-28:** Klipper's API_Server page (`load_cell/dump_force`,
  `angle/dump_angle`, Unix-domain socket, JSON) and Config_Reference
  (`[load_cell]` sensor types CS1237, HX711, HX717, ADS1220, ADS131M0x; the
  `[angle]` section was cut off in the fetch, so which angle chips are read is
  still open).
- The claude-api skill's model table (cached 2026-09-25): Opus 5.5 $4/$20 per
  MTok with cache reads at $0.20; Sonnet 5.5 $2/$10 with $0.20; Haiku 4.5 $1/$5.

## Computed

- `calc/w3_final.py` → `w3_final.out.txt`:
  1. the tack defined against the final insulation crimp (height H_f + 0.2–0.5,
     width +0.1–0.2), lateral squeeze and grip by width, first touches before and
     after a tack;
  2. the tack servo through a 1:1 lever and where its load cell sits;
  3. per-unit machine time for v8, a4c and v9;
  4. v9b's person time on a hand-pumped jack;
  5. how far the conductor barrel is closed if the applicator's own ram makes
     the tack.
- `calc/cycle_and_cost.py`: the press line now uses the crawl rule (9–34 s
  crawl), so v1 is 69–177 s a crimp, 1.1–2.9 h a unit, and v6 2.8–6.6 h; the
  strip line names the contact's own length.
- `calc/wave2.py` §7: cache reads at the skill table's prices; supervisor cost
  $0.2–2.8 a unit.

## What the idea files now hold, and where it came from

| Idea | Content | Source |
|---|---|---|
| v9 (new) | The tack at the anvil of a stopped crank applicator, a contact still on its carrier; T and C one datum; back-out on the carrier; shadow test through a swing-in mirror; branch A1 on b1c's shaft | borrowed-machines' Combination A, developed here |
| v9b (new) | The same by hand on b1b's jack test, a toggle for the tack, the ELP through a hand-swung mirror | borrowed-machines' A0 |
| v8 | Tack height relative to C's final height; former 0.1–0.2 mm wider (disagreeing with "cut to the final crimper's width", with the grip physics); the stroke after a tack meets the conductor wings first; the shadow test; C hosts by what the pallet allows (a4c, f3, a6c, v9); a by-hand version; cell under the nest at 20 kg; lance tip 0.24–0.64 mm | borrowed-machines B-v8-1 to B-v8-4; this view's hand-tool-as-press exchange |
| v1 | Punch ≤ 7.45 mm; an applicator host becomes v9; the gate's shadow test; key-root kink; strip length per contact; steel ceiling; box versus insulation crimp not separable by width or height | borrowed-machines B-v1-1 and table rows 6, 8, 10; this view's hand-tool-as-press exchange |
| v1b | Four ways to give the pallet its axes, including the Ender on its back, two rails, and b3's head on the carriage (Combination D); Prime prices | borrowed-machines B-v1b-1, Combination D |
| v7 | Steel ceiling in every hosted press; crawl by a speed profile on cranks; squeezers need no crawl phase; Klipper's API server subscriptions; IMX298 frame rate from the Prime row; hosting table with a ceiling column, a4c, v9 and b8 rows; ladder rung 0.5 | borrowed-machines B-v7-1 to B-v7-3, Combination C; hand-tool-as-press exchange W4, W8 |
| v3 | Hosts from the jack test to the crank as its own height gauge; $22–39 hand-tool hosts; tack arm relative to the final height; strip-length arm; the tab sheared in an applicator stroke | borrowed-machines Combination B; this view's W6 |
| v4 | The head seals on a tilted top (bellows cup, tilt-cut face, or v4b's pockets) instead of levelling the lance | borrowed-machines B-v4-1 |
| v4b | Contacts lie flat in the pockets, so a rigid nozzle serves; the plate as b3's supply for kit contacts | borrowed-machines Combination F |
| v5 | Mode 2 at an applicator's dwell position; mode 5 with a6's pull jig; lance tip range | borrowed-machines transfers; this view's W3 |
| v6 | Split plunged at the root and drawn to the tip; die-hole blades and twist-on-pull; crossing conductor inserted last | borrowed-machines B-v6-1 to B-v6-3 |
| v2 | Tip wander by approach direction (1.2 mm RSS one way, 6 mm otherwise); Prime rows | borrowed-machines table row 5 |

## Directions set aside in the final pass, and what would revive them

- **The applicator's own ram as the tacker** (stop the crank 0.2–0.5 mm above
  bottom so the insulation crimper forms the tack). The conductor wings have
  already curled 0.12–0.67 mm by then and the barrel's top opening is 0–71 %
  left [calc: w3_final §5], so the straight-down look is partly or wholly shut.
  *Revive* with an applicator whose insulation crimper can be driven ahead of the
  conductor crimper (force-and-form's f6, two blades on two drives), or if a
  jack-test section shows the opening at the stop is wider than estimated.
- **A former cut to the final crimper's own width.** The side squeeze alone
  (3–22 %) can give a grip past the 1.5 N release. *Revive* if v9b's pulls show
  same-width tacks releasing under 1.5 N on this silicone.
- **An absolute tack height (2.3–2.5 mm).** It can fall at or under the final
  insulation height on silicone. Not revived; the relative definition replaces
  it.
- **Two focus slices to find a strand on the barrel floor.** Depth of field is
  0.55–1.5 mm against a 0.3–0.5 mm stand-off. *Revive* with optics whose depth of
  field is under ~0.2 mm (a higher-aperture macro or a telecentric lens), if the
  shadow test fails on tin.
- **A sprung nozzle that levels a barrels-up contact.** The lance is 7–52 N/mm
  as a cantilever. *Revive* if the lance measures under ~1 N/mm on the 0.1 g
  scale.
- **A split with the blade entering at the tip and running to the clamp.** The
  free length is then in compression and buckles at 1.1–2.2 N. Not revived; a
  lid guiding the ribbon would be the only reason to reconsider.
- **A separate file for "T then a one-nest die set" or "T then the foot".**
  hand-tool-as-press holds them as a4c and a6c; this view links them from v8.
- **A bench tack station feeding an applicator.** An applicator has no keyed
  slot for a loose tacked contact. Not revived; the tack moves to the anvil (v9).

## Things that surprised me

- **The applicator's own carrier is the best back-out fixture in the study.**
  A tack releases at 0.4–1.5 N; the tab bends only at 4–12 N along the wire. The
  rear shoulder in an unmeasured neck, v8's hardest part, is not needed there.
- **The stroke after a tack reverses the first touch,** and on silicone the
  untacked stroke can go either way too. What survives is the useful part: the
  jacket is held before compaction.
- **A raised bundle is findable by its shadow** where focus cannot find it.

## Questions for Derek (final pass)

1. **An applicator.** Would you buy an OTP side-feed XH applicator and a reel
   from eBay or Made-in-China (not on Prime, so weeks) to open v9, v9b and the
   jack test? Or stay with kit contacts, where v8 feeds a4c or a6c?
2. **The shadow photograph.** A stripped conductor laid in a kit contact,
   jacket in the insulation barrel, photographed from straight above with one
   LED at about 65° from each side in turn. Does the bundle's shadow show beside
   it? Push one strand down to the floor: does it lose its shadow?
3. **The lance.** One kit contact barrels-up on the 0.1 g scale, a probe on the
   box top: the force at 0.1, 0.3 and 0.6 mm of travel, and whether the lance
   springs back.
4. **A second NEMA 23.** Would a crank or eccentric press get its own NEMA 23
   and DM542T, or share the weld rotator's?
5. **Guards.** On anything built round the shop press, is an interlocked guard
   over the crimper faces acceptable, with the fork's parked position and the
   force-ceiling switch in the same enable line?
6. **Still open from before:** the tack test with pliers and the scale; the neck
   photograph; JST's manual; the ELP's px/mm; whether the web zips; kit contacts
   or strip for production; a point micrometer; a Mac awake for a run or the
   cell's own computer.
