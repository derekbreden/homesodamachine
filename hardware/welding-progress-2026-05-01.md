# Welding progress — Snapshot 2026-05-01

**This is a point-in-time snapshot, not a living document.** Captures the state of laser-welding practice on the X1 Pro after roughly a week of off-and-on practice, on the eve of the second "realistic test fixture" attempt and the start of the 316L production-stock work. Recipe and rationale recorded here for posterity and to feed forward into future conversations. Will go stale; treat as a reference point, not the canonical practice log.

## TL;DR — recipe to try on the second test fixture

What I've been doing today: 75% power, 80Hz frequency, 2mm wobble width, 10 mm/s wire feed, 2s argon pre-/post-flow, ER308L .030 wire, no rise-up / no fall-down configured, no plate prep, no inside argon purge. Got the first test fixture leak-free after 3 weld + water-test iterations.

What I plan to do next, on my last "realistic" test piece:

> Power: 60%
> Wobble width: 2mm, frequency: 80Hz, pattern: circle if available
> Wire feed: 12 mm/s
> Rise-up: 50ms / Fall-Down: 100ms
> Argon: 2s pre, 2s post (unchanged)
> Plate prep: 30s with 120 grit on the cut edge

Then leak-test it like the previous one and iterate.

After that, the plan is to move to 316L stock (vessel tube + endcap plates already in hand) and transition from water testing to air pressure testing once the NPT tapping is figured out. Tapping supplies arrive Saturday 2026-05-02.

## Where this stands now

- Two "realistic test fixtures" purchased before the 316L pricing turned out reasonable: 1/16"-wall (~0.065") × 5" OD 304L tube + 1/4"-thick 304L endcap plates that slip-fit inside the tube ends. ~$80 per fixture, two total. Same wall thickness, same plate thickness, same joint geometry as the 316L production design — only the alloy differs. ER308L .030 wire on these for now; ER316L .030 (STARTECHWELD spool, ACQUIRED 2026-04-27) ready for the 316L production parts.
- **First fixture (today's session):** leak-free after three weld + water-test iterations. Initial weld leaked at many points across both endcaps; second pass closed most leaks down to three; third pass on those three spots closed it. Visible warping on the 1/16" tube wall, less than what was seen on flatter scrap with more heat input — judged acceptable. Retained as a proof artifact.
- **Tack pattern in use:** 8 tacks, picking opposite sides and bisecting (12, 6, 3, 9, then 1.5, 7.5, 4.5, 10.5 o'clock), then bead segments at ~1/8 of circumference each, with minimal overlap into the tacks. This works — do not change.
- **Two issues observed today:**
  1. Wire stuck to the bead 3–4 times across the session, more frequently early and less frequently late as motion got more consistent. The trail-off-as-trigger-releases motion technique was discovered organically and helped.
  2. Thin-wall warping on the 0.065" tube. The C110 copper bar (YTKavq 1/4" × 2" × 12") was used as a chill block but only contacts the curved tube along a tangent line, limiting heat extraction.

## Provenance of the recipe — where these changes came from

The headline recipe above is **not validated personal practice — it is externally-sourced advice that has not yet been tried on the welder.** It came out of a Claude Code conversation on 2026-04-30 / 2026-05-01 between the user and Claude (Opus 4.7). The user described the two issues from today's session (wire sticking, thin-wall warping) and the parameters in use (75% / 80 Hz / 2 mm / 10 mm/s wire feed / 0 ms rise-up / 0 ms fall-down / no plate prep / no inside argon purge). Claude spawned a research agent to pull the X1 Pro manual and parameter pages from XLaserlab's site and to gather published SS-welding recipes from comparable 700 W-class welders. The recipe is the synthesis. The user had not previously consulted the X1 Pro manual's parameter pages and was not aware of several of the parameters (notably Rise-up Time and Fall-Down Time) before this conversation. The next session is the first hands-on test of this recipe.

The plain-English version: I asked Claude for help. Claude had an agent dig up the manual. The recipe is what came back. I haven't tried it yet.

## Context behind each recipe change

### Wire sticking — Fall-Down Time is the high-leverage fix

The X1 Pro exposes **Rise-up Time** (0–1000 ms, soft start) and **Fall-Down Time** (0–1000 ms, soft stop) on the laser power. The user had both at 0 — not a deliberate choice, just unfamiliarity with the parameters. The agent's manual research surfaced them as the published wire-stick remedy. With both at 0, the laser dies instantly while wire is still in the puddle, and the puddle freezes around the wire. Setting Fall-Down to ~100 ms makes laser power decay smoothly so the puddle cools gradually with the wire in it instead of freezing instantly. Per XLaserlab's published wire-stick remedy, this plus correct feed speed is the official path. **The X1 Pro does not have a wire-retract parameter** — Fall-Down is the substitute.

The trail-off motion the user discovered organically during the session — continuing to pull around the curve and away as the trigger releases — is the manual-technique equivalent of Fall-Down Time. The two compound; keep doing the motion even with Fall-Down configured.

### Power 75% → 60%, wire feed 10 → 12 mm/s

The user had been running 75% on feel, adjusted by experimentation across scrap and judged by visible color on the back side of the test pieces. The agent's research surfaced two facts:

1. The X1 Pro is officially **700 W**, not 800 W. XLaserlab catalog, manual download center, and multiple reviewers all agree on 700 W. The project's [marketing/video/first-weld.md](../marketing/video/first-weld.md) records 800 W — worth confirming on the HMI splash on the unit, but the public spec is 700 W.
2. Published recipes (STRION, GWEIKE) for 1.5–2 mm 304 SS on 700 W-class heads converge on **50–70% power**. 0.065" wall = 1.65 mm sits right at the thin end of that range, so the user's 75% is on the hot side relative to the published ranges.

Lower power = lower peak heat into the thin tube wall = less warping. The slight wire-feed bump (10 → 12 mm/s) compensates so total fill per inch of bead stays roughly the same and the comfortable travel-speed range is preserved.

### Wobble pattern — try circle / "O" if menu has it

The user had not explored the X1 Pro's wobble-pattern menu beyond whatever default is in use. XLaserlab does not publicly enumerate the X1 Pro's pattern shapes, but most welders in this OEM tier offer line / circle / figure-8 / zigzag. The conversation surfaced "try circle for fillet welds" as a try-it-and-see lever — circular wobble agitates the puddle uniformly across both sides of the joint and is more forgiving of slight gun-angle drift than line/zigzag. If the menu doesn't have "circle," current pattern is fine.

### Wobble frequency at 80 Hz — the user's observation was correct

The user observed during practice that varying frequency only changed the visible bead pattern, with no apparent effect on heat or penetration. The agent's manual research confirmed this: the 1–100 Hz parameter on the X1 Pro is the galvo wobble rate, not laser pulsing. Pulse-light is a separately selectable mode with its own duty cycle. The observation was correct. Leave frequency at 80 Hz.

### Plate prep — sand the SendCutSend cut edge

The user did no plate prep on today's first fixture — the SendCutSend cut edges went into the joint as-cut. Claude flagged this in the conversation as a likely contributor to wire stick. The SendCutSend laser-cut endcaps carry a recast layer (high-melting oxide + nitride from the N2 cutting gas) on the OD edge, and that edge ends up directly under the weld bead. Unprepped, it causes erratic puddle behavior and contributes to wire stick when the puddle skips over a hot oxide spot. 30 seconds with 80–120 grit on each plate's OD before fitting is standard practice and should be done on every plate, production-side too.

### Inside argon — skip for this stage

The user did not back-purge the inside of the tube during today's session and observed yellow / light brown coloration on the inside (no black scale). Asked in the conversation whether this was acceptable. Confirmed: yellow/brown is chromium oxide under partial protection from the gun's argon migrating through the slip-fit gap between plate and tube ID, and it dissolves cleanly in the post-weld citric-acid passivation soak that's already part of the production flow ([future.md](future.md) carbonation subsystem). Black scale would not dissolve cleanly — that's the line. Yellow/brown is fine for this stage; skip the inside purge.

## What's working — don't change

- Tack pattern: 8 tacks, opposite-side bisecting.
- Bead segment scale: ~1/8 of circumference per bead, minimal overlap into the tacks.
- Trail-off motion: keep doing this even with Fall-Down Time configured — they compound.
- Argon pre/post-flow at 2 s / 2 s: within recommended range.
- Wire feed rate floor: 10 mm/s was already at the lower bound of comfortable; the 12 mm/s recipe nudges up but doesn't push the floor down.

## Open questions / things to watch

1. **700 W vs 800 W on the unit splash.** Doesn't change the recipe (% is %), but matters for any absolute-wattage comparison.
2. **Wobble pattern menu contents.** Confirm whether "circle" is selectable; if not, current pattern is fine.
3. **Internal copper plug.** Suggested by Claude in the conversation as the highest-leverage warp-reduction lever besides power reduction. Cut a ~2" length from the YTKavq C110 1/4" × 2" × 12" bar and drop it inside the tube against the inside face of the plate before welding. Heat dumps through the plate into the copper, away from the thin tube wall. Not part of the headline recipe (the user did not include it in the parameters they planned to take to the next session) but worth trying alongside it on the second fixture.
4. **Travel speed.** Not separately tracked — only "wire feed" speed appears in the parameter set as the user has been using it. If the 60% / 12 mm/s combination feels different in practice, travel speed may need to come down to match the lower power. Iterate.
5. **If wire stick persists after Fall-Down = 100 ms:** check feed-roller tension, contact-tip wear, and wire stickout distance (5–10 mm past the contact tube is the standard window — too short and the wire heats backwards into the tip).

## Equipment + consumables, current state

- **Welder:** XLaserlab X1 Pro 3-in-1 laser welder/cleaner/cutter, ACQUIRED 2026-04-13, single wire feeder included.
- **Filler wire (304L practice):** ER308L .030 across multiple spools, sufficient.
- **Filler wire (316L production):** STARTECHWELD ER316L .030 10-lb spool (B09BKFBXT9), ACQUIRED 2026-04-27.
- **Heat sink:** YTKavq 1/4" × 2" × 12" C110 pure copper flat bar (B0DR2PX6TT), ACQUIRED 2026-04-24 — available for both external chill-bar and internal heat-sink-plug use.
- **Argon:** existing cylinder feeding the welder via RX Weld regulator. Same cylinder is the source for the brazing-purge rig planned for the refrigeration loop.
- **Practice coupons:** 304 SS 4"×6"×1/16" sheets (3-pack ACQUIRED) and 4"×4"×0.04" sheets (ACQUIRED). Used through the past week's flat-coupon practice.
- **Realistic test fixtures:** two pieces total. One consumed today (leak-free, retained as proof). One remaining for the next-session attempt of this recipe.
- **316L production stock (in hand for after the next test):** OnlineMetals #12498 — 5" OD × 0.065" wall 316 welded SS round tube, qty 10, MTRs in hand. SendCutSend 1/4" 316 SS endcap plates with 2-hole pilot pattern (`endcap-circular-2hole.dxf`), qty 20.
- **Tapping supplies:** Amazon order 112-2348373-7907448 ($264.96 delivered) — WEN drill press, Drill America 1/4"-18 NPT tap + tap wrench, Brown & Sharpe tap guide, plus wood-fixture material — arriving Saturday 2026-05-02. After tapping is figured out, the test cycle moves from water testing to air pressure testing.

## What this snapshot is NOT

- Not a living practice log — re-run as a fresh dated snapshot when there's another inflection point worth capturing.
- Not a production-parameter prescription — production parameters will be derived from the next-session 60% recipe outcome plus the 316L transition.
- Not a substitute for hands-on observation — the trail-off motion, the puddle behavior, and the right power for a given joint geometry are felt, not read from a doc.
