# v7 — The run: what drives the motors and cameras, where each loop closes, how a Claude session supervises, and the first day

Explorer: machine-that-sees-and-learns.

Sketches: [`../sketches/w2-v7-stack.svg`](../sketches/w2-v7-stack.svg) (schematic),
[`../sketches/w2-v7-first-day.svg`](../sketches/w2-v7-first-day.svg) (estimated hours).
Numbers: **[calc: wave2 §n]** [`../calc/wave2.out.txt`](../calc/wave2.out.txt) §3, §4,
§7, §8; **[calc: cycle_and_cost §n]** [`../calc/cycle_and_cost.out.txt`](../calc/cycle_and_cost.out.txt);
**[bm W §n]** borrowed-machines'
[`exchange_sees_learns_w3.out.txt`](../../borrowed-machines/calc/exchange_sees_learns_w3.out.txt);
**[calc: w3htp §n]** [`../calc/w3_on_hand_tool_as_press.out.txt`](../calc/w3_on_hand_tool_as_press.out.txt).
**[Prime]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.

Related: it runs [v1](v1-watched-nest.md), [v3](v3-press-that-runs-experiments.md),
[v5](v5-inspection-booth.md), [v6](v6-patient-cell.md),
[v8](v8-tack-look-crimp.md) and [v9](v9-tack-at-the-anvil.md), and hosts other
explorers' stations (table below).

## Picture it

**On the bench.** The stage from [v1b](v1b-printer-as-stage.md) stands over the
station: a nest, a press or tack former, cameras and their lights. Beside it, a
small printed box holds two boards:
- the **stage controller**: the printer's own board as bought, or one of the
  alternatives below;
- the **station MCU**: an ESP32 running firmware Derek builds with PlatformIO,
  as the appliance's own firmware is [repo: CLAUDE.md]. It drives the press
  stepper through its driver, reads the load cell, moves the hobby servos (the
  pallet's key plunger, the tack former, the drop-shear), lights the LED ring
  one LED at a time, reads the far-end port (one input per conductor), and
  watches the e-stop, the lid switch and the force-ceiling switch.

The e-stop, the lid switch and the **force-ceiling switch** cut the stepper
drivers' enable line in hardware; the MCU also reads them.

**On the Mac.** Three programs run under the user's session, kept awake with
`caffeinate` during a run:
- a **capture app** that holds macOS's camera permission, opens each camera's
  stream once for the run, walks focus once, and hands out frames on request;
- the **runner**, a Python process that owns the recipe, the per-conductor
  state machine, the gate thresholds, the journal and the log;
- a **supervisor**: a Claude Code session woken by events. It reads the log,
  drafts the proposal that goes with each question to Derek, notices trends,
  and writes the unit's report.

**Where the ribbon and contact start.** As the station being run says: ribbon
ends in pallets on a shelf; contacts on a pocket plate ([v4b](v4b-pocket-plate.md)),
a strip, or a reel. The runner holds the unit's loom list and knows, for each
ribbon end, the housing, the pin map, J2's empty cavity 3, J7's trimmed
conductor, and the J4/J7 label [repo: shared-context per-unit table].

**What moves, and who moves it.**
- The stage moves on G-code from the runner.
- Keys, former and shear move on servo commands to the station MCU.
- The press moves only as a whole **stroke** that the MCU runs from start to
  finish. The runner asks for "a stroke to the stop, crawl from the taught
  height, check against envelope *n*", and gets the trace back.

**What locates what.** Pictures locate the conductor relative to the contact
(the runner's visual servo). Geometry sets crimp height. No step count is
trusted for either. The reference for "fixed" is whatever the station's
fiducials are on, seen in every frame.

**What drives the crimp and carries its force.** The press stepper, owned by the
MCU, through the press's own frame to its geometric bottom, with a steel force
ceiling in series. Nothing on the Mac is in that loop.

**How it knows the crimp worked.** The judge measures every picture with OpenCV
and compares each number with three bands: pass, borderline, hard fail.
Borderlines go to Claude; hard fails never do. Every crimp's pictures, trace,
numbers, verdicts, threshold version and who decided go into the log.

**What the person does.**
- Loads pallets, contacts and housings, and starts the run.
- Answers the few questions the run asks, at the bench or from the phone.
- Approves threshold changes the supervisor proposes with evidence.
- Is present for commissioning and for campaigns.

**Steps it covers:** control of every station (stroke, servos, lights,
far-end channel); verify (judge, log, audit of Claude verdicts); sequencing
and recovery (recipe, journal, back-out).
**What it hands back:** choosing the control stack; commissioning; answering
asks; approving thresholds; keeping the Mac awake, or giving the cell its own
computer.

## What it is for

Every other idea in this view assumes something that moves motors, takes
pictures, keeps a record and asks Derek a question when it is unsure. This is
that arrangement, and the plug by which another explorer's station joins the
same record and queue.

## A run, as it happens

1. Derek types `cell run unit-14 --ends J3,J5,J9,J11,J13` at the bench, or asks
   the supervisor session to start it. The runner loads the recipe for those
   ends.
2. `cell doctor` runs first: every camera found **by name**, never by index
   (AVFoundation indices move [repo: `tools/panelcam.targets.conf`]); the stage
   and station ports by USB serial number; the MCU's heartbeat; the e-stop loop
   closed; the load cell's zero and noise over 5 s; the lights, each seen in the
   frame.
3. Fiducials are found, the gauge pin gives px/mm, and the calibration record
   is compared with the last one. A camera knocked more than a few pixels is
   re-calibrated before anything moves.
4. For each conductor the runner walks the station's four functions:
   precondition picture, act, postcondition picture, decide. Each act goes into
   the **journal** as an *intent* before it happens and a *result* after.
5. When the judge is unsure it calls Claude. When Claude is unsure, or the
   numbers fall outside what Claude may decide, the runner files an **ask**: it
   parks the conductor, sends the photo and a proposal, and moves on.
6. Derek's phone buzzes with the photo and three buttons. He taps one. The
   runner acts on it when it next reaches that ribbon end.
7. At the end of the unit the supervisor writes a one-page report: retries,
   asks and answers, crimps outside the usual band, drift against earlier
   units, the contact lot, the cost of the Claude calls.

## The bench controllers: three stacks that work

All three keep one rule [calc: wave2 §3]: **the MCU owns every stroke.**
- At a 0.05 mm/s crawl one HX711 sample (80 SPS) is 0.6 µm of travel: ~9–19 N
  of overshoot into a steel loop of 15–30 kN/mm.
- The Mac over USB serial on an ordinary day is 30 ms (1.5 µm, 22–45 N).
- A 0.5 s hiccup is 25 µm, 375–750 N; a stall of seconds is kilonewtons.

So the Mac commands whole strokes and reads their traces. The envelope, the drop
to crawl and the stop-on-fault live in the MCU. **Under all of it sits steel:**
a firmware limit can be wrong (a wrong taught height, a wrong envelope after a
threshold change, a load cell stuck at zero), and then the drive's full thrust
goes into the bottom: ~1.4 kN on a NEMA 23 with a Tr8×2 screw, 4–10 kN through
a ball screw [xh-facts §4], 8–10 kN at a crank's bottom dead centre
[borrowed-machines, procedure-is-the-machine calc §3]. Every hosted press
therefore carries a mechanical ceiling in series with its drive: a disc stack
preloaded above the crimp peak whose travel trips the enable-line switch
(borrowed-machines' [b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md)
rod, hand-tool-as-press's [a4](../../hand-tool-as-press/ideas/a4-dies-in-a-die-set.md)
stack), or, for a hand-tool host, a spring link at ~1.25× the handle's need
(borrowed-machines' [b2](../../borrowed-machines/ideas/b2-hand-crimper-in-a-frame.md)).
Heavy disc springs (DIN 2093) come from industrial suppliers; Prime has only a
light stainless assortment [Prime].

| | Stack A: printer as bought + one ESP32 | Stack B: FluidNC | Stack C: Klipper |
|---|---|---|---|
| Stage | The Ender's own board, G-code over USB: `G1`, `M400`, `M114`, `M84 S0` [assumption: the V3 SE's stock firmware accepts these] | An ESP32 board running FluidNC (e.g. MKS DLC32, $38.50 [Prime]) drives the stage and press axes; YAML config; G-code over USB or WiFi; RC servos, relays and probe inputs [source: [FluidNC](https://github.com/bdring/FluidNC), fetched 2026-09-28] | The Ender's board reflashed to Klipper, or a BTT SKR Pico ($35.99 [Prime]), with a Linux host such as a Raspberry Pi |
| Press, servos, lights, far end | The station ESP32: a stepper library, HX711 or HX717, servo PWM, the LED ring, inputs | A second small MCU reads the load cell and raises FluidNC's probe input at a force threshold, so a stroke is a `G38.2` probe move that stops on force; it streams the trace on its own port | Klipper's load cells (sensor types CS1237, HX711, HX717, ADS1220, ADS131M0x [source: klipper3d.org/Config_Reference.html, fetched 2026-09-28]); `trigger_force` halts a move; `force_safety_limit` [source: [Load_Cell](https://www.klipper3d.org/Load_Cell.html), fetched 2026-09-28]. Servos and lights as Klipper outputs |
| Where the firmware limit lives | The station ESP32, every sample | The force MCU's threshold line into the probe input | Klipper's MCU, through its load-cell endstop |
| Force trace to the Mac | The ESP32's serial stream | The force MCU's serial stream | Klipper's API server: `load_cell/dump_force` ("used to subscribe to force data produced by a load_cell") and `angle/dump_angle` over a Unix-domain socket, JSON messages [source: [API_Server](https://www.klipper3d.org/API_Server.html), fetched 2026-09-28]. Force against crank angle arrives as one stream |
| What Derek maintains | One PlatformIO firmware beside the appliance's, and a stock printer | One YAML file and one small firmware | A Linux host, a Klipper config and its macros |

Which angle-sensor chips Klipper's `[angle]` reads was not confirmed
[assumption: SPI parts of the AS5047 class, not the I²C AS5600].

### The stroke, as the MCU runs it

This is the step Derek most wants automated, so it is spelled out.

1. **Tare** the load cell with the punch open.
2. **Approach** at ~2 mm/s to a **taught crawl position**, at least 0.3 mm
   above where the wing tips can first touch (0.95–1.7 mm above bottom on clone
   dimensions [calc: wave2 §5]). At 2 mm/s one HX711 sample is 25 µm, so the
   drop to crawl comes from position, not from the first force rise.
3. **Crawl** at 0.05–0.1 mm/s to the geometric bottom: 9–34 s, and 160–320
   HX711 samples (640–1,280 HX717) through the last 0.1–0.2 mm.
4. **Check every sample against the envelope** for this contact lot: a band of
   force against position, taught from reference strokes and
   [v3](v3-press-that-runs-experiments.md)'s good crimps.
   - Force rising too early (two contacts, insulation under the conductor
     barrel, a contact seated high): stop, back off, report *fault before
     compaction*.
   - Too little force where compaction should be (no wire): finish to the
     bottom and report. That crimp is scrap either way.
5. **Dwell** half a second, then **return** and hand back the trace.
6. **If the Mac falls silent** (no heartbeat for 1–2 s): before the first wing
   touch, the MCU stops and holds; after it, the MCU **finishes the stroke**
   and holds. A half-formed crimp cannot be rescued and has to be cut out
   anyway, while a finished one can at least be judged. This is a policy
   choice, kept visible.
7. **If the power fails** the stepper stops where it is. On restart the journal
   shows a *stroke intent* with no *result*. The runner raises the punch,
   re-looks, and asks whether to cut back that ribbon end.

**By kind of press:**
- **Screw or knee press to a stop:** the stroke above as written.
- **Crank or eccentric at bottom dead centre** (b1b, v9, a4c): the ram's speed
  falls to zero at bottom, but at a constant turn it passes 0.3 mm above bottom
  at 0.67 mm/s on a 30 s revolution, and one HX711 sample is then 4.9–8.4 µm,
  hundreds of newtons into a stiff obstruction [bm W §5]. The MCU therefore
  **profiles the stepper** so the ram crawls at 0.05–0.1 mm/s from a taught
  *angle*, with the envelope indexed to angle. At 0.05 mm above bottom through
  a 30:1 worm that is 582 microsteps/s. A doubled contact met ~0.2 mm early is
  stopped at ~200–212 N [bm W §5; the 200 N band is an estimate]. With bottom
  set by geometry and the peak capped by the disc stack, the crawl buys trace
  resolution and the early stop; it does not guard the bottom.
- **A hand tool in a squeezer** (hand-tool-as-press's
  [a1](../../hand-tool-as-press/ideas/a1-squeezer-cradle.md)): the handle's
  rising gain makes the die move 0.05–0.13 mm/s at a 2 mm/s grip speed near
  closure, a crawl with no crawl phase [calc: w3htp §2]. The force wall still
  lives on the MCU: a 0.5 s stall on the Mac is 1 mm of grip, 108–857 N at the
  dies.

## The Mac side

### The capture app

The repo's panelcam tooling has already met the ELP's habits
[repo: `tools/panelcam.sh`, `tools/panelcam.targets.conf`]:
- macOS grants the camera only to an app, so a small app bundle holds the
  permission (`PanelCamShot.app` today);
- the lens "parks when the stream starts", and where focus lands depends on the
  direction by ~60 units, so focus is walked upward in steps of 20;
- full resolution comes only as MJPG, and the YUV mode arrives torn;
- white balance and exposure are fixed for repeatable pictures.

For a cell that means **one long-lived capture app** that opens each stream
once per run and walks focus once, handing frames to the runner over a local
socket.

**Stale frames.** A UVC camera buffers frames, so the frame read just after a
light changes may be from before the change. A 1 mm indicator LED in a corner of
each camera's field is driven with the lights and shows in every frame which
lighting state it was taken under; a stale frame is rejected by sight. The
IMX298 M12 module lists MJPEG 4656 × 3496 at 10 fps and 2048 × 1536 at 30 fps
[Prime; the ELP board on hand is unconfirmed], so eight lighting states take
2.6–4.2 s [calc: wave2 §4].

### The runner

- **Recipe.** Per loom: housing, cavity for each conductor, skips (J2's cavity
  3), trimmed conductors (J7), crossings (J4, J7), insertion order separate
  from crimp order (a crossing conductor goes into its cavity last), the label
  text.
- **State per conductor:** waiting, laid, gated, crimped, inspected, pulled,
  then parked, asked or backed out.
- **A station** is four functions, the shape [v6](v6-patient-cell.md) uses:
  `precondition(frame)`, `act(params)`, `postcondition(frame)`,
  `decide(measurements, attempts)` returning accept, retry, back out or ask.
- **Journal.** An append-only file, flushed before each act (*intent*) and after
  (*result*). After a crash the runner never repeats an act. It re-looks at the
  station whose intent has no result and decides from the picture.

### The judge

- **Numbers come only from OpenCV:** edge fits on silhouettes, line fits,
  template matches, blob counts. Anthropic's vision documentation calls
  Claude's coordinates and counts approximate [source: Claude vision docs].
- **Three bands per quantity:** pass; borderline (Claude decides pass, fail or
  ask); hard fail (passed only by Derek through an ask).
- **The borderline call** is a non-interactive `claude -p` with
  `--output-format json` and a `--json-schema` for
  `{verdict: pass|fail|ask, reason, what_to_look_at_next}`. The output includes
  `total_cost_usd`, which the runner logs [source:
  [Claude Code headless docs](https://code.claude.com/docs/en/headless), fetched
  2026-09-28]. The standing instructions and labelled reference crops sit in the
  same cached prefix every time.
- **Every Claude verdict is audited.** A borderline pass is followed by the
  after-crimp measurement and sometimes by a destructive pull, so "of the
  borderlines Claude passed, how many made good crimps" has an answer after a
  few units.

### The log, and where it lives

- One folder per crimp: the crops, one full frame, the force trace, and a
  `record.json` with unit, loom, pin, contact lot, every number, every verdict,
  who decided, and the threshold version. An SQLite index answers questions
  such as "every crimp height from lot 3".
- ~5 MB a crimp, ~0.3 GB a unit, ~16 GB over the program
  [calc: cycle_and_cost §4], on the Mac's disk and a backup drive, not in the
  repository.
- The thresholds are a small versioned file in the cell's own directory.
- The unit's one-page report is what Derek keeps with the unit.

### The queue, and how Derek answers

- **What an ask holds:** the photo or photos, the station, the numbers, what the
  runner proposes, and fixed answers: yes; no; do it by hand; discard this end.
- **To the phone** by ntfy: an HTTP PUT or POST to a topic URL, a JPEG or PNG
  attached (up to 15 MB), and up to three action buttons; an *http* action sends
  a request when tapped [source: [ntfy publish docs](https://docs.ntfy.sh/publish/),
  fetched 2026-09-28].
  - The buttons are yes, no and later; "by hand" and "discard" wait for the
    bench.
  - Each button posts its answer to a **second topic the runner listens to**,
    so no port is opened on the Mac.
  - A public ntfy.sh topic can be read by anyone who knows its name. A long
    random topic name, or a self-hosted ntfy, keeps it private.
- **Or through the supervisor session.** This Claude Code environment says a
  session can be followed from another device and lists push notifications
  among its tools [observed in this session's environment, 2026-09-28; untested
  here]. "Yes, and pass that kind from now on" becomes a proposal to change a
  threshold.
- **Or not at all.** Asks wait at the bench; the runner keeps working on other
  ends.

## The supervisor: what a Claude session does during a run

**Production mode.** The runner owns the machine. Claude comes in two ways.
1. **The per-borderline call** above: stateless, short, bounded by the bands.
2. **A supervisor session**, resumed for each event with
   `claude -p --resume <session>` [source: headless docs]. It wakes on an ask
   filed, a trend alarm, the end of a ribbon end, and the end of the unit.
   - **What it does:** writes each ask's proposal from the labelled examples;
     groups like asks; watches what per-crimp thresholds cannot see (force
     peaks creeping up across units, retries clustered on one pallet slot, asks
     from one contact lot, heights stepping when a lot changes); writes the unit
     report; proposes threshold changes with their evidence.
   - **What it may not do,** enforced by the tools it is given (`--allowedTools`:
     read the log, `cell status`, `cell ask`, `cell pause`, write the report):
     move a motor, resume a paused run, change a threshold, pass a hard fail. It
     may pause the runner on an alarm, file an ask saying why, and wait.

**Commissioning and campaign mode.** Derek is at the bench with an interactive
Claude Code session that has the motion tools (`cell move`, `cell stroke --stop`,
`cell shoot`, `cell pull`). Calibration, reference strokes and
[v3](v3-press-that-runs-experiments.md)'s campaign run this way. The MCU's
limits and the steel ceiling are in force whatever the session asks.

**Why Claude and not only thresholds:** the borderline band, where a threshold
cannot name what it sees ("a strand outside the wing, or a reflection?"); the
ask's proposal in plain words; patterns across units; the report.

**What it costs.** Borderline calls, supervisor events and the unit report come
to ~$0.2–2.8 a unit, by model and by how early in the program it is
[calc: wave2 §7; prices from the claude-api skill's table cached 2026-09-25:
Opus 5.5 $4/$20 per MTok with cache reads at $0.20, Sonnet 5.5 $2/$10 with
$0.20, Haiku 4.5 $1/$5]. The runner logs the actual figure per call.

## How the thresholds learn

- **Labels come from:** Derek's answers; v3's destroyed crimps, photographed
  before they were pulled; after-crimp measurements that confirm or contradict
  a gate's verdict; proof-pull results.
- **After each unit** the supervisor proposes changes with their evidence: "12
  asks on strip length 2.25–2.30 mm, all answered yes, all 12 crimps inside the
  height band: move the strip lower bound from 2.30 to 2.20." Derek approves, and
  the new threshold version is committed.
- **Estimated rates** [calc: wave2 §7]:

  | Phase | Asks per unit | Derek's minutes per unit |
  |---|---:|---:|
  | Day 1, ask-all for the first end | 5–11 | 2–7 |
  | Next few units | 2–3 | 1–2 |
  | After ~5 units of labels | 1–2 | under 1 |

## The first day of running

Sketch: [`../sketches/w2-v7-first-day.svg`](../sketches/w2-v7-first-day.svg).
Times are estimates [calc: wave2 §8].

**Before it.** The booth ([v5](v5-inspection-booth.md), mode 1) has been logging
Derek's hand crimps, so the log, the capture app and the judge already exist.
The station brought up is the tack station ([v8](v8-tack-look-crimp.md)), the
watched nest ([v1](v1-watched-nest.md)), or the tack at the applicator's anvil
([v9](v9-tack-at-the-anvil.md)).

| Hours | What happens | What Claude does | What Derek does |
|---|---|---|---|
| 0–0.5 | `cell doctor`: ports by name, heartbeats, e-stop and ceiling switch, load-cell zero and noise, lights seen | Reads each result and says what is off | Plugs, powers, fixes |
| 0.5–1.25 | Home; walk focus once per view; fiducials; gauge pin to px/mm; calibration 1 saved | Checks the fits, writes the calibration record | Holds the gauge pin |
| 1.25–1.75 | Reference strokes: empty nest ×5, contact but no wire ×5 | Draws the traces, proposes envelope 1 | Approves envelope 1 |
| 1.75–2.5 | Dry lay-ins on a scrap 5P end with no contacts | Reports servo rounds and key drops | Watches the first few |
| 2.5–3.5 | Five scrap crimps, **ask-all** | Proposes a verdict on each | Answers every one at the bench |
| 3.5–4.25 | The five cut open, micrometered and pulled | Records them as the first labels | Cuts, measures, pulls |
| 4.25–5 | Lunch while the log is summarised | Proposes thresholds 2 with evidence | Approves |
| 5–6.5 | Five 4P ends (J3, J5, J9, J11, J13), 20 crimps, **ask-borderline** | Supervises and drafts the asks | Answers |
| 6.5–7.25 | Those ends inserted by hand and tested on the wafer board | Compares the test with the log | Inserts and tests |
| 7.25–7.5 | The day's report | Writes what happened and what is next | Reads it |

**What the day leaves:** calibration 1, envelope 1, thresholds 2, five labelled
crimps, twenty production crimps on the simplest end type (4P into XHP-4, 38 %
of all crimps, no pairs, skips or crossings [digest]).

**What can go wrong on the first day, and how it shows:**

| Trouble | How it shows | Repair |
|---|---|---|
| A camera on another index after a replug | Wrong picture, or none | Cameras matched by name |
| Focus lands elsewhere | Sharpness drops on every frame | Re-walk upward from below |
| Daylight moves the exposure | Silhouette edges shift through the day | A hood; fixed exposure and white balance |
| A frame from before the light changed | The sync LED shows the wrong state | Reject and wait one frame |
| The printer releases its steppers or homes on connect | Stage position jumps | `M84 S0`; re-home and re-find fiducials on reconnect |
| The Mac sleeps | Heartbeat stops | `caffeinate`; the MCU holds |
| Servos brown out the USB hub | A camera drops as a key moves | Servos on their own 5–6 V supply |
| Load cell drifts warm | Zero walks | Tare before every stroke |
| Everything is borderline | Asks pile up | Expected on day 1; ask-all makes it the plan |

## The ladder: builds useful in the week they are made

Each rung reuses the capture app, the runner, the log, the queue and the labels
of the rung before.

0. **The booth on hand crimps** ([v5](v5-inspection-booth.md), mode 1): a
   camera, a light, a blade support, the log. Derek's own crimps get a record
   and the judge its first labels.
   - **0.5, still no motor:** hand-tool-as-press's foot bench
     ([a6](../../hand-tool-as-press/ideas/a6-foot-closed-jig-bench.md)) logs a
     force-against-travel curve for every foot-closed crimp from its cord load
     cell and pulley angle sensor; with the booth's height that is labelled data
     for the envelope and v3's windows. Its keyhole is a hard-fail band that
     needs no judge. On the applicator route,
     [v9b](v9b-tack-by-hand-on-the-jack-test.md)'s hand tack and jack stroke
     are logged by the same capture app.
1. **The tack station, crimp by hand or foot** ([v8](v8-tack-look-crimp.md),
   with hand-tool-as-press's [a6c](../../hand-tool-as-press/ideas/a6c-flags-by-machine-foot-crimp.md)):
   the first motors. The machine places the contact on the conductor and pins
   it; Derek crimps.
2. **The heavy crimp under the same runner:** hand-tool-as-press's one-nest die
   set ([a4c](../../hand-tool-as-press/ideas/a4c-one-nest-behind-a-tack-station.md)),
   force-and-form's knee press ([f3](../../force-and-form/ideas/f3-knee-micropress.md)),
   or the crank applicator with the tack at its anvil ([v9](v9-tack-at-the-anvil.md)).
   Insertion still by hand.
3. **The ends of the procedure:** split and strip stations
   ([v6](v6-patient-cell.md)), then insertion along the wire axis.

## Hosting other explorers' stations

A station from another view plugs in as the same four functions plus a module in
the station MCU's firmware.

| Station | Act the MCU runs | What the runner looks at | Back-out | Ceiling |
|---|---|---|---|---|
| SN-2549 squeezer ([hand-tool-as-press a1](../../hand-tool-as-press/ideas/a1-squeezer-cradle.md), [a1b](../../hand-tool-as-press/ideas/a1b-pawl-out.md)) | Pusher squeeze with envelope; release-lug servo; no crawl phase | Grounded flap blade and far-end continuity; side frame of the nest | Release lug before the force wall; after it, cut back. With a1b's pawl out, the journal's *squeeze intent* with no *result* marks the suspect conductor after a power loss | Spring link ~1.25× handle need |
| Knee micro-press ([force-and-form f3](../../force-and-form/ideas/f3-knee-micropress.md)) | Knee stroke; a 10 N re-touch read by a 0.001 mm indicator (Clockwise DITR-0105, $52.99 [Prime]; RS232 cable not on Prime) | Capture pause picture; re-touch height every crimp | Stop at capture; after the stroke, cut back | Disc stack in the knee's link |
| One-nest die set on an eccentric ([hand-tool-as-press a4c](../../hand-tool-as-press/ideas/a4c-one-nest-behind-a-tack-station.md)) | Fast to ~30° before bottom, slow over the last ~20° indexed to angle; re-touch at 10 N | Seat look under the neighbours; re-touch and silhouette heights | Stop and reverse on early force | a4's disc stack under the lower holder |
| Crank applicator ([borrowed-machines b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md), [v9](v9-tack-at-the-anvil.md)) | Profiled crawl from a taught angle; strain gauges on the rod against angle; dwell stop after bottom | The contact alone; the tacked conductor through the mirror; the dwell silhouette | Before bottom: stop if the curve is wrong; on a failed look, the carrier holds the box while the conductor is drawn out | Disc stack in the rod, switch in the enable line |
| Strip indexer ([terminal-supply a2](../../terminal-supply/ideas/a2-strip-indexer.md)) | Pin wheel, pilot pins, drop-shear servo | The waiting contact; a fence moved along the wire by the picture | Index past the contact | — |
| Pallet stage and far-end port ([ribbon-as-pallet a1](../../ribbon-as-pallet/ideas/a1-pallet-tour.md), [a6](../../ribbon-as-pallet/ideas/a6-housing-as-last-comb.md)) | Stage moves; pogo inputs | Continuity per conductor at every touch | Flush-cut the end 6–10 mm in | — |
| Sensing nest on a real header ([into-the-housing i5](../../into-the-housing/ideas/i5-person-inserts-on-a-sensing-nest.md)) | Lever angle; header posts as inputs | The cavity lit; the post that closes | Extract through the window | — |
| Spool line ([borrowed-machines b8](../../borrowed-machines/ideas/b8-spool-fed-borrowed-line.md)) | As b1b, with the slip ring as the far-end channel | Rip-force trace as one more envelope | An ask ("park this conductor, with a photo") when the belt slips | As b1b |

## Problems, and what answers them

1. **"A Claude session in the loop makes the machine unpredictable."** Claude is
   in none of the millisecond or second loops. The MCU's limits, the steel
   ceiling and the pass and hard-fail bands are fixed. Claude decides only inside
   the borderline band, and every verdict is scored later.
2. **"The Mac does other work, sleeps and updates itself."** `caffeinate` and the
   MCU's heartbeat hold; the journal makes a restart safe; or a small dedicated
   computer (the Pi that stack C needs anyway). Derek's choice.
3. **"Two or three firmwares to look after."** Stack A has one firmware and a
   printer as bought.
4. **"Finishing a stroke when the Mac goes quiet could finish a bad crimp."**
   True. The alternative leaves a half-formed crimp that must be cut out anyway.
   The envelope still stops a stroke that goes wrong.
5. **"A phone service is a third party."** Self-hosted ntfy, or no phone.
6. **"The log is big."** 16 GB over the program fits any disk; full frames can
   be kept only for flagged crimps.

## Contribution

- A concrete shape for the software and electronics every camera idea here
  assumes.
- A line between what is deterministic (steel ceilings, MCU limits, bands,
  geometric bottoms) and what is judged (borderlines, asks, trends), with Claude
  only on the judged side and every judgment audited.
- A first day that is a plan, and a ladder where each rung is useful on its own.
- A common plug for other explorers' stations: four functions, an MCU module and
  a ceiling.

## Major unresolved problems

- **Which stack** suits Derek: his own PlatformIO firmware, FluidNC or Klipper.
- **Which angle sensors** Klipper's `angle/dump_angle` supports, for a crank's
  force-against-angle stream.
- **The ELP's MJPG rate and buffer depth** on the board on hand.
- **The policy on Mac silence mid-stroke** is a choice, not a derivation.
- **Real ask rates** are estimates until a first day is run.
- **The Ender V3 SE's stock firmware** as a plain G-code stage.
- **ntfy privacy:** a random topic, or self-hosting.
- **Heavy disc springs** for the ceilings are not on Prime.

## What rests on assumptions

- Ask and borderline rates [estimate].
- USB latencies of 30 ms typical and 0.5 s on a bad moment [estimate].
- Stock printer firmware accepting `M84 S0` [assumption].
- Model prices from the claude-api skill's table cached 2026-09-25; Haiku's
  cache-read price taken as 0.1× input [assumption].
