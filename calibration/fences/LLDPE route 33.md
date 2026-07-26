---

# User

---

<command-message>relay</command-message>
<command-name>/relay</command-name>
<command-args>LLDPE route 32

I'm not seeing a lot of things in the ASSE 1022 assembly that I expected.

I don't see:

* GAGIRA 316L SS reducing coupling, 3/8" NPT F × 1/4" NPT F
* John Guest PP010822E 1/4" OD × 1/4" NPT male connector
* Basics MTB-0606WP White Barb Tee × Male Branch, 3/8" ID barb × 3/8" ID barb × 3/8" MNPT
* John Guest PP451223W Female Adapter NPTF Polypro, 3/8" NPTF × 3/8" OD PTC
* John Guest PP061208W Reducer Stem Polypro, 3/8" OD stem × 1/4" OD PTC


I'm sure I'm missing something, and its possible I added something extra - I am not recalling instantly how all of these fit together, and I'm not certain that they do. It would be nice to see the complete plan visually, in 3D, and that is what we are trying to do here please.

Please spawn as many agents as you need to do the best you can to estimate precisely the shapes and dimensions of these things.

And spawn agents as needed for help considering how to arrange them, because it is inevitable you will fence yourself in, in ways that are against my wishes, and the more fresh eyes you get on these things, the sooner you can arrive at the correct unboxed-in conclusions.</command-args>

---

# User

---

Relay the contents of another of the user's Claude Code sessions INTO this one. You do it locally: render that session's clean transcript with our shared exporter and read it into context. There is NO cross-session messaging here — you never write to or notify the other session, you just read its transcript off disk.

Session to pull in: **LLDPE route 32

I'm not seeing a lot of things in the ASSE 1022 assembly that I expected.

I don't see:

* GAGIRA 316L SS reducing coupling, 3/8" NPT F × 1/4" NPT F
* John Guest PP010822E 1/4" OD × 1/4" NPT male connector
* Basics MTB-0606WP White Barb Tee × Male Branch, 3/8" ID barb × 3/8" ID barb × 3/8" MNPT
* John Guest PP451223W Female Adapter NPTF Polypro, 3/8" NPTF × 3/8" OD PTC
* John Guest PP061208W Reducer Stem Polypro, 3/8" OD stem × 1/4" OD PTC


I'm sure I'm missing something, and its possible I added something extra - I am not recalling instantly how all of these fit together, and I'm not certain that they do. It would be nice to see the complete plan visually, in 3D, and that is what we are trying to do here please.

Please spawn as many agents as you need to do the best you can to estimate precisely the shapes and dimensions of these things.

And spawn agents as needed for help considering how to arrange them, because it is inevitable you will fence yourself in, in ways that are against my wishes, and the more fresh eyes you get on these things, the sooner you can arrive at the correct unboxed-in conclusions.**

Steps:

1. **Find it.** Run:
   `python3 ~/Developer/claude-code-setup/jsonl2md/jsonl2md.py list-sessions`
   Match LLDPE route 32

I'm not seeing a lot of things in the ASSE 1022 assembly that I expected.

I don't see:

* GAGIRA 316L SS reducing coupling, 3/8" NPT F × 1/4" NPT F
* John Guest PP010822E 1/4" OD × 1/4" NPT male connector
* Basics MTB-0606WP White Barb Tee × Male Branch, 3/8" ID barb × 3/8" ID barb × 3/8" MNPT
* John Guest PP451223W Female Adapter NPTF Polypro, 3/8" NPTF × 3/8" OD PTC
* John Guest PP061208W Reducer Stem Polypro, 3/8" OD stem × 1/4" OD PTC


I'm sure I'm missing something, and its possible I added something extra - I am not recalling instantly how all of these fit together, and I'm not certain that they do. It would be nice to see the complete plan visually, in 3D, and that is what we are trying to do here please.

Please spawn as many agents as you need to do the best you can to estimate precisely the shapes and dimensions of these things.

And spawn agents as needed for help considering how to arrange them, because it is inevitable you will fence yourself in, in ways that are against my wishes, and the more fresh eyes you get on these things, the sooner you can arrive at the correct unboxed-in conclusions. to exactly one title. If it's ambiguous or not listed, show the candidates and ask which — never guess. It's the source, so it must not be this current session. (Add `--cwd <path>` if the session lives in a different project.)

2. **Render its clean transcript.** Run:
   `python3 ~/Developer/claude-code-setup/jsonl2md/jsonl2md.py export-session "<matched title>" --out /tmp`
   It prints the path of the `.md` it wrote. For a very long session, instead grab the tail:
   `python3 ~/Developer/claude-code-setup/jsonl2md/jsonl2md.py delta "<matched title>" --tail 40`
   (prints the last 40 exchanges to stdout — no file).

3. **Read it in.** Read the `.md` it wrote (or use the delta stdout). Then give the user a 2–4 line orientation: what that session was doing and where it left off, and ask what they want to bring over or do with it here.

Pull one session per invocation. Read-only: this never writes to, messages, or disturbs the source session.

To send a message the other way — interject into another live session — use `/relay-send`.

---

# Assistant

---

I'll find that session and pull in its transcript.

---

# Assistant

---

Exact match: **LLDPE route 32**. Exporting.

---

# Assistant

---

**Route 32, relayed.** That session took the task from route 31 — roll the ASSE 1022 assembly 90° about X so its center port faces **−Y** instead of −Z, then route at least one tube to it. It did the roll in `_contents.py` (`vent-tip` now reads normal `(0,-1,0)`), discovered the drip then falls on the **power tray**, slid the fitting chain west to open ~clearance at `fluid-28`'s lane, and authored an 80.6 mm / 4-bend run in `_lines.py`. It declared the water path in the connection inventory, turned the drip-fall into an executable placement rule instead of prose, and got all 7 gates plus both selftests passing.

It left off **mid-clean-build** (clearances measured + thumbnails, the version that gets committed) while sweeping the repo for stale prose still describing the old downward vent. Nothing was committed — the working tree here still carries those edits (`_contents.py`, `_lines.py`, the ASSE reference model, scorecard, and the assembly docs).

Your prompt for this session is the next step: you don't see the GAGIRA 316L reducing coupling, the JG PP010822E, the Basics MTB-0606WP barb tee, the JG PP451223W, or the JG PP061208W in the assembly, and you want the complete fitting chain modeled and visible in 3D.

What do you want to do here — pick up that unfinished clean build and prose sweep first, or go straight at the missing-fittings question (spawn the dimension-estimation and arrangement agents against the current `asse1022_assembly.py`)?

---

# User

---

I want you to add all of these things to the ASSE-1022 assembly. I don't care what the other agent does, because I doubt it will be doing this.

I want you to do it as I asked, spawning agents to research dimensions and shapes for parts, and spawning agents to assist with arranging those parts in an un-boxed-in fashion.

Thanks.

---

# Assistant

---

Two of the five are already in the assembly (`gagira-coupling`, `jg-pp010822e`); three are not. Let me get the full picture before spawning research.

---

# Assistant

---

Now I'll spawn the dimension research. Four agents in parallel — three for the missing parts, one to audit why the two that *are* in the assembly may not be reading as present.

---

# Assistant

---

Four dimension agents are running. While they work, let me establish the arrangement context — where this tee actually has to live.

---

# Assistant

---

Noted — and that's a big unlock. Everything above the foam cap (z > 253.4) is movable: the ASSE chain, both trays, the DC block, and all four rear-panel bulkheads plus the C14. Let me get that in front of the arrangement agents as an explicit permission, since otherwise they'd treat the rear panel as fixed.

---

# Assistant

---

Six agents are out. While they work, let me understand the integration path — how a new reference body enters the pack and what gates it must pass.

---

# Assistant

---

The other session finished and committed (`a37c1752`) — tree is clean apart from a build artifact, so no collision. And I found something material in the stash list that the arrangement agents need:

---

# Assistant

---

Six agents are out and I have the lay of the land. Status while they run:

**On your five parts** — two of them *are* already in the assembly's `build()`: `jg-pp010822e` and `gagira-coupling` ([asse1022_assembly.py:101-102](hardware/reference/asse1022-assembly/asse1022_assembly.py:101)). So the question for those two is why they don't *read* as present — buried inside the brass body, modeled too small, or just lost in the render. An agent is settling that with intersection volumes rather than opinion.

The other three genuinely don't exist anywhere in the repo as geometry. They're the **tap-point branch** — per [bom.md:59-61](hardware/ledger/bom.md:59) and [internal-plumbing.md:150](hardware/assembly/internal-plumbing.md:150), the tee goes *inline in the 3/8" silicone hose* between the FFL38BARB38 and the SeaFlo suction, and its branch necks 3/8" MNPT → PP451223W → PP061208W → 1/4" LLDPE → flow regulator → V-A. So they're not a straight extension of the existing chain; they hang off a hose run that doesn't exist yet.

**Which is where your "boxed in" warning is already earning its keep.** The SeaFlo those parts feed is unplaced, and I found this in your stash list:

```
stash@{0}: enclosure: SeaFlo accurate body dims 80x72x187 (research) + CO2 clearance nudge
           — grows box 12mm & cascades clashes; held for authoring the SeaFlo's real shape
```

The pump's real envelope is **80 × 72 × 187 mm** — longer than the entire ASSE chain — and a previous attempt to pack it at true size didn't fit and got stashed. Meanwhile the service bay above the foam cap is being filled with the ASSE chain (margins already down to 4.71 mm off the C14), two trays, and a DC block. That's packing smallest-first with the biggest body still homeless. I've pushed that to both arrangement agents as the thing to attack, along with your permission to move everything above z = 253.4 including the rear-panel ports and the C14.

Also worth knowing: the other session finished and committed while we talked (`a37c1752`, "the ASSE 1022 vents forward, and water-1 closes on its inlet"), so the tree is clean and we're not fighting it.

I'll report back when the dimension modules land and the arrangement verdicts come in.

---

# User

---

<task-notification>
<task-id>a570cf7f7cfbba186</task-id>
<tool-use-id>toolu_01RWCPYc2u2EsdkK9RF1Amja</tool-use-id>
<output-file>/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/cf7ffd7d-2017-4caf-9a49-23e90eb4a417/tasks/a570cf7f7cfbba186.output</output-file>
<status>completed</status>
<summary>Agent "Audit existing GAGIRA and PP010822E" finished</summary>
<note>A task-notification fires each time this agent stops with no live background children of its own. The user can send it another message and resume it, so the same task-id may notify more than once.</note>
<result>Repo untouched. Here is the audit.

---

## 1. Per-body table (working-tree build, `HSM_SKIP_THUMBNAILS=1`)

| name | X | Y | Z | volume mm³ |
|---|---|---|---|---|
| `jg-pp010822e` | [−36.00, −6.50] | [−7.14, 7.14] | [18.75, 35.25] | 4583.8 |
| `gagira-coupling` | [−17.50, 13.00] | [−12.84, 12.84] | [15.88, 38.12] | 8424.7 |
| `multiplex-asse1022` | [0.00, 65.00] | [−16.50, 16.50] | [0.00, 41.29] | 33293.1 |
| `ffl38barb38` | [51.00, 87.50] | [−11.00, 11.00] | [17.47, 36.53] | 3185.7 |
| `vent-stub` | [27.23, 36.77] | [−4.76, 4.76] | [−2.00, 10.50] | 263.3 |

Assembly bbox X [−36.00, 87.50] Y [−16.50, 16.50] Z [−2.00, 41.29] — matches the README.

**Pairwise exact intersection volume is 0.0000 mm³ for all ten pairs.** Exact gaps (`BRepExtrema_DistShapeShape` via `probe.World.gap`):

| pair | overlap | gap mm |
|---|---|---|
| ptc ↔ coupling | 0.0000 | 0.0000 (coincident faces) |
| ptc ↔ multiplex | 0.0000 | 6.5000 |
| ptc ↔ barb | 0.0000 | 57.5103 |
| ptc ↔ vent-stub | 0.0000 | 35.0881 |
| coupling ↔ multiplex | 0.0000 | 0.0000 (coincident faces) |
| coupling ↔ barb | 0.0000 | 38.0000 |
| coupling ↔ vent-stub | 0.0000 | 15.2194 |
| multiplex ↔ barb | 0.0000 | 0.0000 (nut bore over flare) |
| multiplex ↔ vent-stub | 0.0000 | 0.0000 (stub bore = barb Ø) |
| barb ↔ vent-stub | 0.0000 | 15.8514 |

Stronger check: each body cut by the fused union of the other four loses **nothing** — 100.00% of every body is outside every other body. Nothing is buried. `probe.py selftest` PASSes (50 bodies normalized), so those numbers are trustworthy.

The committed `asse1022-assembly.step` is **byte-identical** to a fresh build, so the PNG is current, not stale.

## 2. Verdict: **rendering/visibility artifact.** Not a geometry bug, not a scale bug.

I projected every body through the viewer's exact thumbnail camera (`/Users/derekbredensteiner/Developer/homesodamachine/web/public/js/viewer/step.js:186-195`) and matched the silhouettes against the PNG pixels. Two independent causes:

**(a) The PP010822E is drawn in a color that is invisible against the viewer background.** Thumbnails always render in x-ray mode (`step.js:194`), where feature edges are opaque `LineBasicMaterial` in the body's own STEP color (`/Users/derekbredensteiner/Developer/homesodamachine/web/public/js/viewer/xray.js:73-81`). The clear color is `0x1a1a2e` = rgb(26,26,46) (`step.js:174`). `BLACK_PP = cq.Color(0.16, 0.16, 0.18)` = rgb(41,41,46) — **ΔB = 0, contrast ratio 1.179:1** (WCAG floor for non-text graphics is 3:1). Measured: the PTC's 297 exclusive silhouette pixels are all within 8/255 of the background, and the dominant values are rgb(23,23,38)/(24,24,39) — *darker* than the background. That faint dark ellipse at the upper-left of the render is the PTC's 0.14-opacity ghost surface. Its edges are not visible at all. For comparison: STAINLESS 9.05:1, BRASS 5.98:1, CLEAR_PVC 13.38:1.

**(b) The GAGIRA coupling *is* drawn, but reads as part of the brass body.** 2021 px silhouette, peak pixel rgb(184,189,199) = exactly STAINLESS. But: 79% of its silhouette is overlapped by the PTC's and the ASSE's; STAINLESS vs BRASS is only **1.51:1** luminance contrast; and it shares STAINLESS with `ffl38barb38` (they share one cached edge material, keyed on hex). A Ø25.67 gray hex butted coaxially and coplanar onto a Ø33 gold hex, at similar luminance, reads as one nut cluster rather than two fittings.

**(c) Framing amplifies both.** The whole assembly is **4.07% of the 400×400 frame**; its screen bbox is 154×96 px. `dist = maxDim * 2.5` at 45° FOV puts a 123.5 mm part inside a 255.8 mm frame — 48% of frame width before the iso diagonal eats more.

Per-body screen budget: ptc 945 px (0.59% of frame), coupling 2021 (1.26%), multiplex 4417 (2.76%), barb 1786 (1.12%), stub 363 (0.23%).

## 3. Not a scale bug

PTC total 29.5 mm (collet Ø14 × 13.5, 9/16" hex × 5.0, shank Ø13.7 × 11.0). Coupling 30.5 mm × 7/8" hex, sockets Ø13.72 / Ø17.15. Both sit inside the 25–30 mm real band. The derived constants check against the thread standards: 1/4 NPT major 0.540" = 13.72 ✓, 3/8 NPT major 0.675" = 17.15 ✓, 9/16" AF → 16.50 AC ✓, 7/8" AF → 25.67 AC ✓. 7/8" is the right hex for a 3/8 FNPT body — a 3/4" hex leaves only 0.95 mm of wall over the Ø17.15 socket vs 2.54 mm at 7/8". First-party dimension tables were not reachable (John Guest's site returns 403; the Swagelok and buyfittingsonline pages omit or 403 the drawings), but nothing in the constants is suspicious. One thing that *does* shrink the PTC: 11.0 of its 29.5 mm are buried in the coupling socket, so only 18.5 mm is exposed.

## 4. Making the upstream stack read

- `/Users/derekbredensteiner/Developer/homesodamachine/hardware/reference/asse1022-assembly/asse1022_assembly.py:51` — `BLACK_PP` must clear 3:1 against `#1a1a2e`. Measured candidates: `0.30,0.30,0.34` → 2.01:1 (still fails); **`0.42,0.44,0.48` → 3.43:1** is the first that passes; `0.45,0.45,0.50` still reads as dark PP. This is a repo-wide issue — every black-PP part colored this way has it. Worth a palette rule: no part color below 3:1 against the viewer background.
- `asse1022_assembly.py:50` — give the coupling its own hue instead of sharing STAINLESS with the barb. Teal `0.25,0.78,0.72` → 8.19:1 vs bg; violet `0.62,0.48,0.85` → 5.07:1. Either separates it from the brass by hue, which luminance alone cannot do here.
- Camera: `step.js:187` and `/Users/derekbredensteiner/Developer/homesodamachine/web/public/js/viewer/scene.js:341` both use `maxDim * 2.5`. Dropping to 1.3–1.5 takes the part from 48% to 81–93% of frame width (roughly doubles apparent size). Better still, fit the projected silhouette rather than the bbox.
- An explode factor on the assembly (push the two upstream fittings further along −X for the render only) would break the coplanar coupling/ASSE joint that makes them read as one body.
- Separately: in the enclosure, `/Users/derekbredensteiner/Developer/homesodamachine/hardware/printed-parts/enclosure/enclosure-assembly/_contents.py:613` recolors the entire chain one brass, so if he was looking at the *enclosure* render, none of the five fittings are distinguishable there by construction. (The chain does survive placement intact — `probe.py boxes` gives `asse1022-assembly x[42.50, 166.00]` = the full 123.5 mm.)

## 5. Other correctness problems found

**(a) Real bug — `multiplex_asse1022.py:45` uses the hex circumradius where the hex is flats-down.**

```
BODY_CENTER_Z = VENT_DROP + HEX_ACROSS_CORNERS / 2.0    # flow axis height off the bbox floor
```

`build()` deliberately clocks the hex flats-down ("a flat faces down so the vent exits a face, not a corner"), so the body's Z half-height is the **apothem** 14.289, not the circumradius 16.5. Measured by slabbing the solid: the body's underside is at **Z = 12.711**, not 10.5. Consequences:

- `VENT_DROP = 10.5  # barb reach below the body bottom` (line 42) — actual reach is **12.711**.
- `VENT_INTO_BODY = 5.0  # extra barb length fused up into the body` (line 43) — actual buried length is **2.789**.
- Knock-on at `asse1022_assembly.py:82`, `top = bfp.VENT_DROP  # the body's underside, where the hose stops` — the stub top lands at 10.500, **2.211 mm below** the underside, leaving 111.1 mm³ of bare vent barb uncovered. That directly contradicts `vent_stub()`'s own docstring ("It covers the barb to the body's underside").

Two fixes. Minimal and geometry-preserving: keep the axis at 27.0 and publish the datum instead of re-deriving it —

```python
HEX_ACROSS_FLATS = HEX_ACROSS_CORNERS * math.sqrt(3) / 2.0   # 28.579
BODY_UNDERSIDE_Z = BODY_CENTER_Z - HEX_ACROSS_FLATS / 2.0    # 12.711
```

then `vent_stub()` reads `top = bfp.BODY_UNDERSIDE_Z`, and the VENT_DROP / VENT_INTO_BODY comments get corrected to 12.711 / 2.789. Or, to keep the constants' stated meanings, `BODY_CENTER_Z = VENT_DROP + HEX_ACROSS_CORNERS * math.sqrt(3) / 4.0` = 24.789 — but that moves the flow axis 2.211 mm relative to the vent tip, so `ASSE1022_POS` / `ASSE1022_ROLL`, the routed `water-1` segment, and the scorecard's `fall vent-tip onto foam-assembly` all shift.

**(b) `asse1022_assembly.py:81`** — `_tip, _axis = bfp.vent()` is a dead unpack; neither value is used.

**(c) `jg_pp010822e.py:37`** — `TUBE_D = 6.35` has no consumer anywhere in `hardware/`; meanwhile `scorecard.py:520` hardcodes the literal `6.35` for that same port. Same shape of problem at `scorecard.py:521`, which hardcodes `9.525` where `ffl38barb38.HOSE_ID` says `9.53`.

**(d)** The PTC is the one hex in the chain clocked differently: it is built on `"XY"` and rotated about Y (`jg_pp010822e.py:69`), landing corners on ±Z / flats on ±Y, while the coupling, the ASSE body and the barb all build on `"YZ"` and land corners on ±Y / flats on ±Z. Cosmetic, but it is the only module in the chain not using the sibling idiom.

**(e)** The GAGIRA coupling has **no through bore** — sockets 11.0 + 13.0 = 24.0 in a 30.5 body leaves 6.5 mm of solid metal plugging the middle. Consistent with the "external envelope only" house style (the ASSE body is solid too), but worth knowing that the 8424.7 mm³ is not metal volume and the solid is not a flow path.

Sources: [Swagelok SS-6-HRCG-4](https://products.swagelok.com/en/c/straights/p/SS-6-HRCG-4), [John Guest PP010822E — Fresh Water Systems](https://www.freshwatersystems.com/products/john-guest-male-connector-nptf-black-polypropylene-1-4-x-1-4-nptf), [John Guest male connector NPTF range](https://www.johnguest.com/us/en/od-tube-fittings/polypropylene-black/threaded-connectors/male-connector-nptf-thread), [316 SS reducing hex coupling 3/8 × 1/4 FNPT](https://www.buyfittingsonline.com/stainless-steel-fittings-high-pressure-reducing-hex-coupling-4500-psi-316ss-3-8-in-x-1-4-in-npt-threads-4031-on/).</result>
<usage><subagent_tokens>146069</subagent_tokens><tool_uses>62</tool_uses><duration_ms>851231</duration_ms></usage>
</task-notification>

---

# Assistant

---

The audit came back decisive. Let me verify its central claim myself before acting on it.

---

# Assistant

---

Verified — the audit is right. `HEX_ACROSS_CORNERS / 2.0` is the circumradius, but `build()` clocks the hex flats-down, so the body's half-height is the apothem (14.289, not 16.5). The underside sits at Z = 12.711 while `vent_stub()` stops its bore at 10.5, leaving bare barb uncovered against its own docstring.

Two fixes here — the colors (which is the literal answer to "I don't see them") and the stub coverage:

---

# Assistant

---

Contained — `VENT_DROP` has one external consumer. Making the underside an explicit datum, which leaves the built solid byte-identical and only extends the stub's bore up to meet it:

---

# Assistant

---

STEP byte-identical, all three terminals unchanged — nothing placed moves. Let me render the thumbnail and confirm the two "missing" parts are actually visible now.

---

# Assistant

---

That's the answer to half your question. Both parts *were* always there — they were invisible:

---

# Assistant

---

**Why you couldn't see them.** The audit projected every body through the viewer's actual thumbnail camera and matched silhouettes against the PNG pixels:

- **PP010822E** — `BLACK_PP` was `(0.16, 0.16, 0.18)` = rgb(41,41,46) against the viewer's `#1a1a2e` ground = rgb(26,26,46). Identical blue channel, **contrast ratio 1.18:1**. Thumbnails render in x-ray, where a body is carried entirely by its edge lines in its own color — so its 297 exclusive pixels were all within 8/255 of the background, some *darker* than it. It was rendering as a hole.
- **GAGIRA coupling** — drawn correctly, but it shared `STAINLESS` with the barb, and stainless-vs-brass is **1.51:1**. A Ø25.67 gray hex butted coplanar onto a Ø33 gold hex at near-identical luminance reads as one nut cluster, not two fittings.

Both fixed in [asse1022_assembly.py:49](hardware/reference/asse1022-assembly/asse1022_assembly.py:49) — the coupling gets a hue the chain uses nowhere else (8.19:1), the PP is carried at a value that clears 3:1. I'll design the full palette once the three new parts land, since they're all white PP and will need to separate from each other too.

**A real bug fell out of it too.** [multiplex_asse1022.py:45](hardware/reference/multiplex-asse1022/multiplex_asse1022.py:45) computed the body's half-height from `HEX_ACROSS_CORNERS / 2` — the circumradius — but `build()` deliberately clocks the hex *flats-down* so the vent exits a face. The real half-height is the apothem, so the underside sits at Z = 12.711, not 10.5. The vent stub was stopping its bore 2.211 mm short, leaving bare barb uncovered against its own docstring. Fixed by publishing `BODY_UNDERSIDE_Z` as a real datum. The multiplex STEP came back **byte-identical** and all three terminals are unchanged — `tube-in (−36, 0, 27)`, `hose-out (87.5, 0, 27)`, `vent-tip (32, 0, −2)` — so nothing placed moved.

One judgment call I want to flag rather than bury: I could instead have made `VENT_DROP` mean what its comment claimed (barb reach *below the underside*), which would drop the flow axis 2.211 mm and cascade into `ASSE1022_POS`, the `water-1` run, and the scorecard's fall rule. I didn't, because both numbers are divided off a spec sheet rather than measured — the README already flags the whole chain PROVISIONAL pending shelf measurement. **When you have the Multiplex in hand, the number to caliper is the exposed vent-barb length below the hex flat.** That settles which reading is real.

Still waiting on the three dimension modules and both arrangement verdicts.

---

# User

---

<task-notification>
<task-id>af7cb814db24f13ad</task-id>
<tool-use-id>toolu_012rTmSEyk6kDp5j5LJaTKBV</tool-use-id>
<output-file>/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/cf7ffd7d-2017-4caf-9a49-23e90eb4a417/tasks/af7cb814db24f13ad.output</output-file>
<status>completed</status>
<summary>Agent "Model JG PP451223W female adapter" finished</summary>
<note>A task-notification fires each time this agent stops with no live background children of its own. The user can send it another message and resume it, so the same task-id may notify more than once.</note>
<result>Done. `hardware/reference/jg-pp451223w/jg_pp451223w.py` builds a valid solid and exports `jg-pp451223w.step` + `.step.png`. Nothing outside that directory was touched, nothing committed.

## The two interface numbers

**TUBE_INSERTION_DEPTH = 22.29 mm (0.878")** — from the collet mouth face (`tube_port()`, X = 36.0) to the internal tube stop. Built as JG's own published `F1 = 0.720"` (18.29 mm, body face → tube stop, 3/8" row) **plus** the 4.0 mm the collet stands proud of the body face. A stem's shoulder therefore lands on the collet face at X = 36.0 and its 3/8" nose occupies X = 36.0 down to X = 13.71.

**THREAD_ENGAGEMENT = 9.53 mm (0.375")** — a 3/8-18 male makes up this far past the NPTF mouth (`thread_port()`, X = 0), i.e. it occupies X = 0 → 9.53. This is the ASME B1.20.1 / Machinery's Handbook "total thread makeup, hand and wrench" for 3/8 NPT.

⚠️ Your brief said "for 3/8 NPT, L1 hand-tight engagement is roughly 0.4 inch". That is wrong. Per ASME B1.20.1 for 3/8-18: **L1 = 0.2400"** (hand-tight), **L2 = 0.4078"** (effective thread), practical hand+wrench makeup **0.375"**. 0.4" is L2, not L1.

## Printed output

```
Bounding box: X [0.00, 36.00]  Y [-12.84, 12.84]  Z [-11.12, 11.12]
Hex 25.67 across corners × 12; barrel Ø19.7 × 14; collet proud 4; total 36 mm
Thread engagement 9.53 mm; tube insertion depth 22.29 mm (tube stop at X = 13.71)
thread_port: at (0.00, 0.00, 0.00) facing (-1, 0, 0)
tube_port:   at (36.00, 0.00, 0.00) facing (1, 0, 0)
Solid valid: True
```
Y/Z extents are the 7/8" hex (25.67 across corners × 22.23 across flats).

## Dimension table

| Constant | mm | inch | Tier | Source |
|---|---|---|---|---|
| `TUBE_STOP_DEPTH` | 18.29 | 0.720" | **a** | John Guest *Fluid System Products Catalog 2025* p.53, "Cavity Dimensional Detail (Inch)", 3/8" row, **F1** (body face → tube stop, one O-ring) |
| `TUBE_BORE_D` | 9.65 | 0.380" | **a** | same table, **ØC** (tube-stop bore) |
| `THROUGH_BORE_D` | 8.89 | 0.350" | **a** | same table, **ØG** (through bore past the stop) |
| `THREAD_PITCH_D` | 15.93 | 0.62701" | **c** | ASME B1.20.1, **E1** for 3/8-18 (pitch Ø at the internal thread's gauge plane = the mouth) |
| `THREAD_TAPER` | 1:16 on Ø | — | **c** | ASME B1.20.1 (1° 47′) |
| `THREAD_ENGAGEMENT` | 9.53 | 0.375" | **c** | ASME B1.20.1 / Machinery's Handbook, hand + wrench makeup, 3/8 NPT |
| `TUBE_INSERTION_DEPTH` | 22.29 | 0.878" | **a + b** | JG F1 (a) + measured collet protrusion (b) |
| `BODY_D` (collet barrel) | 19.7 | 0.775" | **b** | scaled off McMaster **51055K678**'s dimensioned drawing (JG-made acetal 3/8" tube × 1/4 NPTF F, OAL 1.406" as the scale bar); corroborated by JG's published **H = 0.790"** minimum port spacing at 3/8" |
| `COLLET_PROUD` | 4.0 | 0.157" | **b** | same drawing |
| `COLLET_RIM_D` / `NECK_D` / `TIP_D` | 14.8 / 13.6 / 13.2 | — | **b/d** | rim Ø scaled off that drawing (0.573"); the three-step split is shaped to read as a JG collet |
| `LENGTH` | 36.0 | 1.417" | **d** | 51055K678 measures **1.406"**; the 3/8 socket is marginally deeper than its 1/4. Checked for internal consistency: tube stop lands at X = 13.71, leaving 11.5 mm of socket + 2.2 mm of land — geometrically self-consistent |
| `HEX_ACROSS_CORNERS` | 25.67 | 7/8" A/F | **d** | 7/8" is the standard 3/8"-body hex and matches this repo's `gagira_reducing_coupling.py`. Measured JG data points: 11/16" A/F on a **1/4** NPTF female end, 13/16" A/F on a **3/8** NPTF male end — a 3/8 *female* socket needs more meat than either |
| `HEX_LENGTH` | 12.0 | 0.472" | **d** | 51055K678's hex + collar = 0.577"; ours must cover the 3/8 socket |
| `WAIST_D` / `WAIST_LENGTH` | 17.0 / 6.0 | — | **d** | the necked section between hex and barrel on the same drawing (0.235" long) |
| `BODY_LENGTH` | 14.0 | — | **d** | balance of the length budget |
| `SOCKET_DEPTH` | 11.5 | 0.453" | **d** | molded socket ≈ makeup + lead-in/runout |

Published-but-not-modelled (JG cavity table, tier **a**, all measured from the collet-body face): cartridge seat **ØA 0.632" (16.05 mm) × D 0.270" (6.86 mm)**; **O-ring seat ØB 0.547" (13.89 mm), E1 0.465" (11.81 mm)** from the face; **H (minimum port spacing) 0.790" (20.07 mm)**. I deliberately did not cut the ØA/ØB cartridge cavity — doing so would leave the modelled collet as a ring floating free of the body in a single-solid export.

Derived female-thread diameters at the mouth (tier **c**): pitch 15.93 mm, minor 14.80 mm (tap drill 37/64" = 14.68 mm), major 17.06 mm; at 11.5 mm depth all shrink 0.72 mm.

## What I could not pin down

**No dimensioned drawing for PP451223W exists in public.** I checked and came up empty on: the JG *Fluid System Products Catalog 2025* (SKU tables carry bag/box quantities only), the 2012 catalog, the Industrial Division catalog, the JG US **and** GB product pages (SKU/thread/tube-OD tables only, no drawing, no CAD in Resources &amp; Downloads), `tech-spec-od-fittings-v2.pdf`, `how-to-connect-jg-od-fittings.pdf` (no insertion-depth table for OD tube — the only one is for CTS ProLock), Fresh Water Systems, US Plastic, SupplyHouse, Seelye, automationdistribution. Lowe's and Ferguson block automated reads. **McMaster does not stock a plastic 3/8 tube × 3/8 NPTF female** — the closest are 51055K678 (3/8 × 1/4 F, 1.406", 11/16" hex) and 51055K18 (3/8 × 3/8 M, 1.24", 0.56" thread, 13/16" hex).

So: the *internal* PTC geometry is from John Guest's own published drawing; the *thread* geometry is from the governing standard; the *external envelope* is scaled from McMaster's dimensioned drawing of the same-family JG fitting one thread size down. If you can put calipers on the real part, `LENGTH`, `HEX_ACROSS_CORNERS` and `BODY_D` are the three worth measuring.

## Things that will surprise whoever arranges this

- **Collet release needs clearance all the way around.** To pull the stem you push the collet ring *square* against the Ø19.7 body face — so nothing may sit against the collet face, and the Ø19.7 barrel end needs a finger's or the JG release tool's access around its full circumference. Budget ~15 mm radial and keep the last 6 mm of X free.
- **The hex is the widest part and it is at the *thread* end** (X = 0 → 12, Ø25.67 across corners) — unlike the 1/4-female sibling, where the hex (17.46 A/F) is *narrower* than the collet barrel. A 7/8" open-end wrench swinging on it wants ~30 mm of side clearance in the plane normal to X.
- **Minimum straight tube run: ~22.3 mm.** The stem/tube travels that far in a straight line before bottoming, so a bend cannot begin closer than about 30 mm from the collet face.
- **JG's own minimum port spacing at 3/8" is 20.07 mm** — two of these can never be centred closer than that, and with the 7/8" hex on this one it is really 26 mm.
- **NPTF is dryseal** (designed to seal metal-to-plastic without tape), but `assembly/internal-plumbing.md` tapes everything anyway; tape adds ~0.5 turn, so treat 9.53 mm as nominal and allow ±1 mm of axial makeup slop when stacking against the MTB-0606WP branch.
- **Polypropylene is water-only.** JG states these are not suitable for compressed air or vacuum — relevant if this branch ever sees the CO2 side.
- Fresh Water Systems lists "Alt. Part Number: PI050801S" on this product page. That is a data error on their site — PI0508... is a 5/16 acetal part, not an equivalent.</result>
<usage><subagent_tokens>285449</subagent_tokens><tool_uses>154</tool_uses><duration_ms>1435624</duration_ms></usage>
</task-notification>

---

# Assistant

---

The PP451223W module landed — and the agent caught an error in my own brief. I told it 3/8 NPT L1 hand-tight was ~0.4018"; that's **L2** (effective thread). Per ASME B1.20.1, 3/8-18 is L1 = 0.2400", L2 = 0.4078", practical hand+wrench makeup 0.375" = 9.53 mm. I passed that same wrong figure to the tee agent, so let me correct it there before it bakes it in:

---

# Assistant

---

PP451223W verified — hex at the thread end, stepped collet at the PTC end, 36 mm overall, valid solid. Let me learn what declaring new plumbing costs while the rest land:

---

# Assistant

---

Useful precedent found while waiting: the scorecard already has a category for exactly this kind of part — [scorecard.py:128](hardware/printed-parts/enclosure/enclosure-assembly/scorecard.py:128), *"In-line fittings — tube-hung PTC junctions, carried by their lines (no tray, no holder)"*, covering `tee-y-c`, `tee-y-f`, the Y-dividers and the elbows. The MTB tee and its two adapters are the same species: fittings that hang in a run rather than mount to anything. That's real evidence the tee should be its own placed component in the enclosure pack rather than folded into the `asse1022-assembly` reference model — I'll weigh it against the arrangement verdicts when they land.

Three agents still out: the tee's dimensions, the reducer stem's, and both arrangement reads.

---

# User

---

<task-notification>
<task-id>a54052aa08e730e21</task-id>
<tool-use-id>toolu_01Be9N9VPZ1mXTvy2geZ4di5</tool-use-id>
<output-file>/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/cf7ffd7d-2017-4caf-9a49-23e90eb4a417/tasks/a54052aa08e730e21.output</output-file>
<status>completed</status>
<summary>Agent "Arrange tap-point tee chain" finished</summary>
<note>A task-notification fires each time this agent stops with no live background children of its own. The user can send it another message and resume it, so the same task-id may notify more than once.</note>
<result>Analysis complete. No files under `hardware/` were touched — everything below came from read-only `probe.py` queries. (`probe.py selftest` → **PASS**, 50 bodies normalized, 20 routed runs.)

---

# Lead with the bad news: the obvious arrangement is not merely bad, it is arithmetically impossible

**The SeaFlo at its true 80 × 72 × 187 envelope has ZERO valid placements anywhere in this machine, in any of six orientations.**

I voxel-scanned the whole interior (`_dims().inner` = x[−14, 297] × y[−3, 384] × z[0, 331.72], 2 mm grid, every body marked by its bounding box so a "free" result is provably free):

```
=== SeaFlo body 80 x 72 x 187, against the FULL pack ===
  187 along X (80 Y, 72 Z)  : 0 placements
  187 along X (72 Y, 80 Z)  : 0 placements
  187 along Y (80 X, 72 Z)  : 0 placements
  187 along Y (72 X, 80 Z)  : 0 placements
  187 along Z (80 X, 72 Y)  : 0 placements
  187 along Z (72 X, 80 Y)  : 0 placements
```

With **everything above z = 253.4 deleted** (all of it movable per your instruction):

```
  187 along X (80 Y, 72 Z)  : 15120 placements   ... of which below z=253.4: 0
  187 along Y (80 X, 72 Z)  :  3042 placements   ... of which below z=253.4: 0
  187 along X (72 Y, 80 Z)  :     0
  187 along Y (72 X, 80 Z)  :     0
  187 along Z (either)      :     0
```

Read that carefully. Three facts fall out, and they are the frame for everything else:

1. **The service bay is the only home.** Zero placements below the foam cap, in any orientation, even with the bay emptied. The reason is a set of clean numbers:
   - machine corridor depth = foam ymin **200.00** − compressor ymax **133.00** = **67.00 mm**. The pump's *smallest* dimension is 72. **Short by 5.00 mm.**
   - ±X floor slivers: 28 mm. Condenser channel: 21 mm. Floor-stratum-top (154.5) to tray-stack floor (164.8): **10.30 mm**.
2. **It must lie with 72 vertical.** Bay height = 331.72 − 253.40 = **78.32 mm**. 72 fits with 6.32 to spare; 80 does not fit at all — that is why the two "80 Z" rows are zero even with the bay emptied.
3. **You cannot buy your way out in Y.** The corridor's 5 mm deficit would be cured by `FRONT_DEPTH` 200 → 213, but that moves the cold core, and you named the foam shell and the rear panel plane immovable. **X is pinned by the cold core + `SIDE_RIB_INSET`; Y is pinned by the cold core and the fixed rear plane. Height is the only elastic dimension this machine has left.**

And the bay is already full:

```
=== service bay plan occupancy (z 253.4..331.72) ===
  plan cells occupied, aft of y=200 : 0.926
```

**92.6% of the bay's plan is already spoken for** — before the SeaFlo, the drip pan, the flow sensor, the tee, or the pump-outlet chain. The SeaFlo alone wants an exclusive 187 × 80 = 14 960 mm² of *full-height* plan, ~33% of the usable 45 280 mm² (x[0,283] × y[200,360], excluding the 24 mm the rear-panel bodies reach inboard).

**So, plainly: at true component sizes the service bay cannot hold both the electronics shelf and the water deck.** Plan budget: water deck ≈ 28 350 mm² + electronics 19 122 mm² = **47 472 &gt; 45 280**, and that is before a single routing lane, the CO2 drop, the carb riser, either nozzle riser, or service access. It is over by 5% with zero lanes drawn. The stash's "grows box 12 mm &amp; cascades clashes" was not a bug — it was the layout telling you the truth.

Your three ways out, ranked:

- **(a) Raise the ceiling.** Bay 78.32 → ~120 mm buys a second story: water deck below, PCBA (27 tall) + dc-dist (18 tall) on a shelf above the SeaFlo. Costs ~41 mm of appliance height. This is the only option that changes no other subsystem.
- **(b) Move the electronics down.** Machine corridor is 67 deep; `power-tray` is **73.94** deep and `pcba` **73.30** — both miss by ~7 mm. Both are printed trays that have already been reshaped once ("wide-shallow layout, PSU turned 90°"). A ≤ 62 mm-deep respin fits. But the corridor is also refrig-3's only unauthored lane.
- **(c) Question the pump.** A 1.3 GPM / 100 PSI RV diaphragm pump, 187 mm long, to fill a 2 L carbonator. It is the single largest part in the machine with zero valid placements, and nobody has ever asked whether it needs to be that pump. A 60–120 mm class 12 V diaphragm pump at 0.5–1 GPM / 60–100 PSI dissolves this entire problem. **I'd start here.**

---

# 1. The recommendation, committed to

**The tee is its own placed body in the enclosure pack. It sits at world (240, 341, 310), run along ±X, branch pointing −Y (forward).**

```
ASSE barb (169.5, 341, 310) →[38 mm 3/8" hose + clamp]→ TEE run-W (207.5, 341, 310)
                                                          TEE centre (240, 341, 310)
                                                          TEE run-E (272.5, 341, 310) →[hose]→ SeaFlo suction
                                                          TEE branch ↓−Y → PP451223W → PP061208W
                                                          collet mouth ≈ (240, 251, 310), facing −Y
```

That placement requires **flipping the ASSE end-for-end and raising the water deck 5 mm** (see §3). Everything below is probe-verified.

### 1a. Reference assembly, or its own placed body? → **Its own placed body.**

Argument for folding it in: the owner wants one 3D picture, and `internal-plumbing.md` §2 builds this as one continuous chain.

Argument against, which wins: **the tee's pose is not a function of the ASSE.** The reference assembly's two turns exist for one reason — the yaw swaps the chain's ends and the roll lays the vent over so it weeps into a pan. The tee has no opinion about the vent. Fold it in and you drag the tee through `ASSE1022_ROLL`, so the day the vent needs re-aiming, the tap point moves with it for no physical reason. And `asse1022_assembly.py` is a *stack-up* — every station derived from the part upstream of it (`BARREL_UPSTREAM`, `COUPLING_X`, `PTC_X`, `BARB_X`). There is no length to stack for a fitting joined by a compliant hose; you'd have to hand-place it inside a file whose whole discipline is that nothing is hand-placed.

And you lose nothing on the picture. `tee-y-c`, `y-d`, `elbow-noz-a` are all tube-hung PTC fittings placed straight into `_contents.build()` with their own pose functions and no tray. The tee is that same animal. It renders in the same assembly, in the same STEP, with its own color.

**The third option — close-couple through a short nipple — I reject.** The FFL38BARB38 terminates in a *barb*, not a threaded port. "Close-coupled" would mean a ~25 mm hose stub with two worm clamps, which is a hose joint with an irreducible minimum (barb overlap + band width) and is not rigid, so the tee's pose still is not the ASSE's. Worse, it would park the tee's branch stack inside the envelope the vent stub and its 56.6 mm drip fall already own.

### 1b. Tee-first or pump-first? → **Tee-first, decisively.**

The tee has **two hard anchors**: the ASSE barb (whose position is set by the vent-over-pan requirement and the rear bulkhead) and V-A-I at (271.329, 172.275, 198.660) facing +Z, a collet on a tray that is not moving. The pump has **one soft anchor**: a barb on a body with four mounting feet that can face any of four directions, fed by 12 inches of compliant silicone.

More decisive: **the pump's true envelope has zero valid placements today.** Any tee position derived from the pump would be derived from a body that is guaranteed to move. Deriving the pump from the tee is the only direction that doesn't build on sand.

So: place the tee against the ASSE and V-A; the hose and the pump follow. The pump's bay then falls out — see §1e.

### 1c. Branch direction → **−Y (forward), horizontal, at the deck height.**

This is not a free choice; it is the only direction that fits. From the tee's run axis, the branch offset (25–35) plus the stacked adapters (45–60) needs **70–95 mm of clear run**. From (240, 341, 310):

| direction | clear run available | verdict |
|---|---|---|
| −Z down | 310 − 253.4 = **56.6** to the foam cap | ✗ short by 14–39 |
| +Z up | 331.72 − 310 = **21.7** to the ceiling | ✗ |
| +Y aft | 362.21 − 341 = **21.2** to the bulkhead bodies | ✗ |
| +X east | 297 − 240 = **57** to the wall, collet facing the wall | ✗ short, and no finger access |
| **−Y forward** | 341 − 200 = **141** over open bay | **✓** |

−Y also gives the best service ergonomics: the collet mouth at (240, 251, 310) faces into the bay's largest open volume with the whole front bay ahead of it — unlimited straight lead-out, and the collet is grabbable from directly above through the top opening.

**Then the 1/4" LLDPE to V-A-I**, verified as one swept Ø6.35 corridor:

```
(240, 251, 310) −Y 18 → (240, 233, 310) east 49 → (289, 233, 310)
   → down 45 → (289, 233, 265) → west/forward → (289, 172.275, 265)
   → west 17.7 → (271.33, 172.275, 265) → straight down 66 → V-A-I
```

`w.hits(corridor)` → **CLEAR**. Nearest bodies: fluid-18 **8.475**, nozzle-gate **9.475**, foam **9.885**, elbow-noz-a **9.361**, pcba **10.009** (floor is 1.0).

The vertical leg rides the **+X wall pocket**, which is the cleanest lane in the machine:

```
cast (289, 172.3, 331) dir (0,0,-1): Ø6.35 reached the 250 mm cast limit with no contact
cast (289, 226.0, 300) dir (0,0,-1): Ø6.35 reached the 120 mm cast limit with no contact
```

A 250 mm unobstructed drop. The flow regulator (fluid-topology segments 1→2, currently unplaced) goes inline on the −Y lead-out at y ≈ 245–265, x = 240, z = 310 — 45 mm of straight open air, reachable from the top opening.

### 1d. Does the tee fit west of the barb? → **The 56.5 mm is exactly right, and it is not enough. No.**

```
barb tip x = 42.50 ; -X interior wall x = -14.00 -&gt; open X = 56.50 mm
cast west from the barb tip, Ø12.7: reached the 250 mm cast limit with no contact
```

The comment is dead accurate — 56.50 mm, no body between. **But 56.5 mm cannot hold the fitting**, and this is arithmetic, not judgement:

- From the barb tip going west you need free hose before the tee (≥ 15 mm, or the joint is loaded in bending right at the clamp), then the tee's whole run.
- 15 + **50** (optimistic run) = 65 &gt; 56.5 → the tee's west barb tip lands **8.5 mm through the wall**.
- 15 + **65** (realistic run) = 80 → **23.5 mm through the wall**.
- And that is before the *second* hose leg, its clamp, and its bend — the leg that has to reach a 187 mm pump.

The only way it fits west is to turn the hose 90° immediately off the barb, which puts a ~28 mm-radius bend in 1/2" OD silicone directly at a clamped joint — a kink at the worst possible place — and parks the tee in the −X boss-chain band, where `enclosure._dims()`'s rule `iz1 = max(iz1, wall_band_top + pod_stack)` (pod_stack = **17.8**) would push the ceiling up by ~8.6 mm.

Related and worth saying out loud: `_contents.py` documents the barb as facing "WEST into the strip's open end for the SeaFlo suction." **There is no SeaFlo west and there can never be one.** x[−14, 42.5] is 56.5 mm; the pump is 187.

### 1e. Where the pump lands, once the tee is placed

```
-- SeaFlo 187x80x72 at x[55,242] y[200,280] z[254,326]
   (skipping power-tray, pcba, dc-dist)          CLEAR
```

The bay's **front strip**, motor west, pump head east at x ≈ 242 — suction barb ~100 mm from the tee's east run port, discharge ~100 mm from `foam.water-in` (141.5, 200, 223). One caveat the probe surfaces: `foam.co2-in` is at **(141.5, 217.8, 262.9) facing +Z**, inside that strip. The pump must clear that column, or the strip starts aft of y ≈ 226 (shifting it aft costs a 5 mm graze of fluid-28, easily re-routed).

**This is the arrangement that requires the electronics to leave the bay's front strip.** That is the price, and it is the same price the SeaFlo charges under any tee placement.

---

# 2. Probe queries and what they returned

```
probe.selftest                                      → PASS (50 bodies, 20 runs)

_dims().inner   = (-14.0, 297.0, -3.0, 384.0, 0.0, 331.72)
_port_frame()   = (0.0, 296.566, 384.0)

at bulkhead-water.tube-in         (145.000, 359.200, 293.000)  n (0,-1,0)
at asse1022-assembly.tube-in      (166.000, 341.000, 305.000)  n (1,0,0)
at asse1022-assembly.hose-out     ( 42.500, 341.000, 305.000)  n (-1,0,0)
at asse1022-assembly.vent-tip     ( 98.000, 312.000, 305.000)  n (0,-1,0)
at source-select-assembly.V-A-I   (271.329, 172.275, 198.660)  n (0,0,1)     ← the branch's destination
at foam-assembly.water-in         (141.500, 200.000, 223.000)  n (0,-1,0)
at foam-assembly.co2-in           (141.500, 217.800, 262.900)  n (0,0,1)
at power-tray.ac-in               ( 30.000, 212.000, 290.000)
at c14-inlet.mains-in             ( 90.000, 357.000, 295.500)

gap asse1022-assembly c14-inlet        4.711    ← today's tightest neighbour
gap asse1022-assembly bulkhead-water  10.095
gap asse1022-assembly dc-dist         16.222
gap asse1022-assembly power-tray      28.320

barb tip x 42.50 → -X interior wall -14.00 = 56.50 mm  (comment verified exactly)
cast (42.5,341,305) dir (-1,0,0) Ø12.7 → 250 mm limit, no contact

cast up from V-A-I               → Ø6.35 runs 90.51 mm, stopped by fluid-18 at z 289.27
cast up from V-A-I, skip 18      → Ø6.35 runs 135.96 mm, stopped by hopper-funnel at z 334.72
cast (289,172.3,331) dir (0,0,-1)→ 250 mm limit, NO CONTACT          ← the +X chimney
cast (289,226.0,300) dir (0,0,-1)→ 120 mm limit, NO CONTACT
cast (289,172.3,265) dir (-1,0,0)→ runs 38.86, stopped by nozzle-gate at x 250.14
cast (271.33,172.28,265) (0,0,-1)→ runs 66.81, stopped by source-select at z 198.19  ← lands on V-A-I

hits x[-14,24]  y[200,384] z[253.4,331.7]  → CLEAR      ← the whole west lane, 38×184×78, empty
hits x[185,275] y[290,340] z[296,331.7]    → 0.2 mm³ of water-1 only  ← the tee's void
hits x[-14,297] y[300,360] z[322,331.7]    → CLEAR      ← full-width slab over the aft strip
hits x[277,297] y[160,362] z[233,331.7]    → foam (x≤283), fluid-18 grazing x≤277.35
```

Verification of the proposal (all boxes skip the four bodies the plan moves):

```
ASSE re-posed, body x[46,169.5] y[312,355.3] z[293.5,326.5]   → CLEAR
   gap to power-tray 22.995   dc-dist 19.600   pcba 45.410
   gap to fluid-28  22.397    bulkhead-flavor-b 18.187
vent fall from (114,312,310) Ø9.53 → runs 56.60 mm, stopped by foam-assembly
drip pan 70×50 at x[79,149] y[306,356] z[253.4,293]           → CLEAR

TEE run body x[207.5,272.5] y[331,351] z[300,320]             → CLEAR
   gap to fluid-18 4.375   fluid-28 11.385   bulkhead-flavor-a 11.362
BRANCH stack x[230,250] y[251,331] z[300,320]                 → CLEAR
   gap to fluid-18 4.375   fluid-28 4.375   pcba 19.664
hose leg barb→tee x[168,209] y[330,352] z[299,321]            → CLEAR
branch corridor, swept as one Ø6.35 tube                      → CLEAR

water bulkhead body at x=46   → CLEAR
C14 body at x=4 / 6 / 10      → CLEAR (all three)
```

Clearance floor is `CLEARANCE_FLOOR = 1.0`; the tightest number in the proposal is **4.375 mm**.

---

# 3. What I would move, and why

| constant | now | proposed | why |
|---|---|---|---|
| `ASSE1022_YAW` | `180.0` | **`0.0`** | Turns the barb EAST. The chain currently fires its 3/8" outlet into 56.5 mm of dead-end; east of it there is 127.5 mm of open strip. This is the load-bearing change. |
| `ASSE1022_POS` | `(130.0, 314.0, 305.0)` | **`(82.0, 314.0, 310.0)`** | X: puts `tube_in` at 46 (a short pigtail off the relocated bulkhead) and `hose_out` at 169.5. Z: +5 lifts the whole deck clear of the two nozzle risers' 292.4 lane — the *only* thing the tee collided with. |
| `ASSE1022_ROLL` | `-90.0` | unchanged | The vent still weeps −Y; fall grows 51.60 → **56.60 mm**, all clear air. |
| `VENT_STUB_REACH` | `2.0` | re-cut to the new strip | Mechanical consequence of the +5 mm deck. |
| `C14_BACK_X` | `90.0` | **`10.0`** | See §4. |
| `C14_BACK_Z` | `295.0` | **`293.0`** | Rides the port field's floor (`UMBILICAL_Z_FLOOR` 281 + flange half-height 11.75 = 292.75). Does not change the box height — the ceiling is set by the carb bulkhead at 329.72. |
| `WATER_BACK_X` | `145.0` | **`46.0`** | Follows the ASSE inlet west. Nut spans x[34.57, 57.43] vs the C14 flange x[−5.25, 25.25] → **9.32 mm** gap, over `PORT_NUT_GAP` 7.0. |
| *(new)* `TAP_TEE_POS` | — | **`(240.0, 341.0, 310.0)`** | Run ±X, branch −Y. Placed in `_contents.build()` alongside `tee-y-c`/`y-d`, with a `tap_tee_port(port)` accessor so `_lines.py` can anchor both hose legs and the branch. |
| `SEAFLO_DIMS` | (unstashed) | **`(80.0, 72.0, 187.0)`** | Land the stash's research. Place at x[55,242] y[200,280] z[254,326] — *after* the electronics leave the front strip. |
| `_lines.py` `water-1` | 4 bends, 80.6 mm | re-author | Mirrors to the west side. Same class of pigtail. |
| `_lines.py` `fluid-18` / `fluid-28` | `turn_back` 40 / 55 | watch, don't move | At the +5 mm deck they clear by 4.375 mm. Only if the real MTB-0606WP body radius exceeds ~9.4 mm about its run axis do these need moving — see sensitivity below. |

### Sensitivity to the tee's real dimensions

- **Run length 50–65 mm: insensitive.** Available east span = 297 − 169.5 = 127.5, less ~25 hose+clamp each side = 77.5 mm of room for a 50–65 mm run. 12–27 mm of slack.
- **Branch stack 70–95 mm off the run centreline: insensitive.** Pointing −Y it lands the collet anywhere in y ∈ [246, 271]; the bay ahead is open to y = 200 at that height. It only slides where the flow regulator sits.
- **The one sensitive number is the tee body's max radius about its run axis.** At deck z = 310 the risers' crown is 295.63, so radius ≤ 9.4 mm keeps a 5 mm gap. An MTB-0606WP's branch hex is likely ~22–24 across flats (r ≈ 12), which would close to ~2.4 mm — still over the 1.0 floor, but tight. Two fallbacks, in order: **(a)** deck to z = 312 (ASSE body zmax 328.5, still 3.2 under the ceiling — that is the practical maximum); **(b)** move `UMBILICAL_X` 210 → ~175, which walks both risers' aft legs out of the tee's x band entirely and independently shortens the carb riser off (141.5, 200, 46.5).

---

# 4. The C14 corner — yes, there is a clean one, and it helps

**Move it. `C14_BACK_X` 90 → 10, `C14_BACK_Z` 295 → 293.** Body lands at x[−5.25, 25.25] y[360, 384] z[281.25, 304.75]:

```
hits C14 body moved to x=4.0   → CLEAR
hits C14 body moved to x=6.0   → CLEAR
hits C14 body moved to x=10.0  → CLEAR
```

x = 10 leaves 11.75 mm of panel outboard of the flange; x = 6 hard into the corner leaves 7.75. I'd take **10** for edge margin. Either way the body is inside the y[360, 384] panel zone, so it costs the aft strip nothing.

**It helps the water path, three ways:**

1. It is currently the ASSE's **tightest neighbour at 4.711 mm** — closer than the bulkhead it serves. Moving it makes that gap tens of millimetres.
2. `internal-plumbing.md` §2 warns: *"keep the fall's column clear when you dress the C14's cordage through the band under the body."* The C14 at x = 90 puts mains cordage straight through the drip-pan band under the atmospheric vent. **That warning simply disappears** at x = 10 — a hand-dressing instruction is replaced by geometry.
3. It frees x ∈ [25, 184] of the rear panel — 159 mm — so the water bulkhead can sit wherever the ASSE's inlet wants it, which is exactly the freedom the flip needs.

Bonus: `power-tray.ac-in` is at **(30, 212, 290)**. The C14 at x = 10 sits 20 mm from it instead of 60, and the run no longer crosses the machine.

**Do not put it in the +X corner.** x ≈ 275 is geometrically free (the umbilical triangle ends at 236.36), but it drags mains cordage 245 mm across the bay directly over the water deck.

---

# 5. Alternatives I rejected, and why each lost

**(a) Keep the ASSE as posed; put the tee west of the barb.** — Lost on 56.5 vs 65–80 mm. Probe confirmed the 56.5 exactly and confirmed nothing is in it; it is simply too short by 8.5–23.5 mm, before the second hose leg. This is the default answer, and it is wrong.

**(b) Keep the ASSE as posed; turn the hose 90° off the barb and put the tee in the empty west lane (x[−14, 24], verified 100% CLEAR over 38 × 184 × 78).** — Genuinely tempting; it is the largest empty volume in the bay. Lost on three counts: it kinks 1/2" OD silicone at a clamped joint; a 35 mm-wide tee body there has `xmin &lt; 0`, tripping `wall_band_top + pod_stack` and **growing the box 8.6 mm taller**; and it strands the branch at the far west, forcing a ~284 mm cross-machine 1/4" run to reach V-A at x = 271.33.

**(c) Branch pointing −Z, straight down at V-A.** — The most natural-looking answer, since V-A-I faces +Z. Lost on 56.6 vs 70–95 mm: from a deck at 310 there is only 56.6 mm to the foam cap and the stack needs 70–95. Also `cast up from V-A-I` runs **90.51 mm and stops on fluid-18** — the one collet in the machine that must be fed from above sits directly under the one tube lane at that x (fluid-18's lane spans x[271.0, 277.35]; V-A-I is at 271.329). A straight drop was never available.

**(d) Fold the tee into `asse1022-assembly`.** — Lost on parameterization: it would ride `ASSE1022_ROLL`, which exists solely to aim the vent, and it would hand-place a fitting inside a file whose entire discipline is that every station derives from the part upstream of it. No picture is lost by placing it in the pack.

**(e) Close-couple the tee to the FFL38BARB38 with a short nipple.** — Lost on physics: the FFL38BARB38 ends in a barb, so "close-coupled" is a clamped hose stub with an irreducible length, which is neither rigid nor short. It also parks the branch stack inside the vent stub's drip envelope.

**(f) Put the SeaFlo in the machine corridor.** — Lost by **5.00 mm** (67.00 available vs 72 needed) and unfixable, since curing it means moving the cold core. Even if it fit, the corridor is the machine's only cross-machine artery: refrig-1, refrig-2, the unauthored refrig-3 suction leg, and both bag falls (fluid-25 at x[41.3, 47.7], fluid-15 at x[107, 242]) all run through it. Filling it with a 187 mm pump closes the machine's arteries.

**(g) Grow the box in Y for a rear water bay behind the cold core.** — Would solve everything (311 × 87 × 331 of clear volume), and 474 mm outer depth is nothing in a 610 mm cabinet. **Ruled out by your own constraint**: the rear panel plane is fixed and the cold core cannot move. Flagging it only so you know what you are paying for that constraint.

---

# 6. What the design is boxed in by that nobody has questioned

1. **The pump.** A 1.3 GPM / 100 PSI RV diaphragm pump, 187 mm long, to fill a 2 L carbonator. It is the only body in the machine with zero valid placements and it is treated as a fixed input. It is the cheapest thing on this list to change.
2. **The electronics living in the service bay.** They are there because the bay was empty when they were placed. The bay is now the *only* place a 72 mm-thick body fits, and the electronics are the only occupants that are thin (18–40 mm) — thin things belong in thin places. This is exactly backwards.
3. **67 mm.** The machine corridor is simultaneously the only large volume below the cap and the only cross-machine artery, and it is 5 mm short of taking the pump. Nobody has noticed that the entire packing crisis is 5 mm wide.
4. **Height is now the only currency.** X is pinned by the cold core plus `SIDE_RIB_INSET`; Y is pinned by the cold core and the fixed rear plane. Every future volume request — flow sensor, GASHER + WR1110 CO2 chain, pump holders, the drip pan — has to be paid for in box height, and 78.32 mm of bay is all there is. Nothing in the repo says this.
5. **The ASSE's yaw was fitted to a bulkhead X that was itself arbitrary.** `WATER_BACK_X = 145` picked a station; the yaw then pointed the inlet at it; the barb then pointed at a wall 56.5 mm away. Exactly the not-load-bearing decision you suspected. `_contents.py` even documents the consequence as a feature — "the strip's open end ahead of it — 56.5 mm to the −X interior wall" — as room for a hose to a pump that is 187 mm long and cannot be there.
6. **V-A-I sits under fluid-18's lane, to within 0.3 mm.** V-A-I x = 271.329; fluid-18's lane spans x[271.0, 277.35]. The one collet that must be fed from above is directly beneath the one tube lane at that x, and `outer_x` derives from the cold core's east face rather than from anything about V-A. Nobody has flagged it; it is why the V-A feed has to sidestep.
7. **The flow regulator has no home.** fluid-topology segments 1 and 2 split at it; it appears in no pack and no BOM placement. It rides the branch, so it should be placed with the tee — I've reserved (240, 245–265, 310) for it.</result>
<usage><subagent_tokens>225252</subagent_tokens><tool_uses>33</tool_uses><duration_ms>1482351</duration_ms></usage>
</task-notification>

---

# Assistant

---

The arrangement agent came back with something much bigger than tee placement. This is worth stopping on:

**The SeaFlo pump has zero valid placements anywhere in this machine.** Voxel-scanned the full interior at 2 mm, all six orientations, bounding-box marked so a "free" result is provably free:

```
=== SeaFlo 80 × 72 × 187, against the FULL pack ===
  187 along X (80 Y, 72 Z) : 0 placements      187 along Y (80 X, 72 Z) : 0
  187 along X (72 Y, 80 Z) : 0 placements      187 along Y (72 X, 80 Z) : 0
  187 along Z (either)     : 0 placements
```

Delete *everything* above the foam cap and it still has zero placements below z = 253.4. The service bay is the only home it can ever have, it must lie with 72 vertical (bay height is 78.32 mm — 80 doesn't fit in any orientation), and **the bay's plan is already 92.6% occupied** before the pump, the drip pan, the flow sensor, the tee, or the CO2 chain. Water deck ≈ 28,350 mm² + electronics 19,122 mm² = 47,472 against 45,280 available — over by 5% with *zero routing lanes drawn*.

Your stash note said it: "grows box 12mm & cascades clashes." That wasn't a bug to fix. That was the layout reporting that it's full.

Three numbers worth having:
- Machine corridor depth = foam ymin 200 − compressor ymax 133 = **67.00 mm**. The pump's smallest dimension is 72. **Short by 5.00 mm** — and curing it means moving the cold core.
- `power-tray` is 73.94 deep and `pcba` 73.30 — both miss that same 67 mm corridor by ~7 mm.
- X is pinned by the cold core + `SIDE_RIB_INSET`; Y by the cold core and the fixed rear plane. **Height is the only elastic dimension left**, and nothing in the repo says so.

**And directly on your question:** the ASSE's barb currently fires west into 56.5 mm of dead end. `_contents.py:213` documents that as a feature — *"the strip's open end ahead of it… for the stiff silicone to turn in on its way to the SeaFlo."* There is no SeaFlo west and there can never be one; it's 187 mm long into a 56.5 mm pocket. The tee doesn't fit there either — it needs 15 mm of free hose plus a 50-65 mm run, so its west barb lands 8.5-23.5 mm **through the wall**. That's the "boxed in" you predicted, and it traces back to `WATER_BACK_X = 145` picking an arbitrary station, the yaw then pointing the inlet at it, and the barb then pointing at a wall.

On the C14 — **yes, there's a clean corner**: `C14_BACK_X` 90 → 10 verifies CLEAR, leaves 11.75 mm of panel outboard. It's currently the ASSE's *tightest* neighbour at 4.711 mm, and it puts mains cordage straight through the drip-pan band under the atmospheric vent — [internal-plumbing.md](hardware/assembly/internal-plumbing.md) has a hand-dressing warning about exactly that, which the move deletes outright.

I'm holding off implementing the re-pose until the second arrangement agent cross-checks it — it's a big move and I want it challenged, not just agreed with. Meanwhile the reducer stem and tee modules are still building.

---

# User

---

<task-notification>
<task-id>a8bc142e1ce44700f</task-id>
<tool-use-id>toolu_01P6wCEGqC4sWcLGxvYNu98j</tool-use-id>
<output-file>/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/cf7ffd7d-2017-4caf-9a49-23e90eb4a417/tasks/a8bc142e1ce44700f.output</output-file>
<status>completed</status>
<summary>Agent "Model MTB-0606WP barb tee" finished</summary>
<note>A task-notification fires each time this agent stops with no live background children of its own. The user can send it another message and resume it, so the same task-id may notify more than once.</note>
<result>Done. Module written, builds a valid solid, exports cleanly, and mates with the sibling PP451223W at exactly zero shared volume.

**File:** `/Users/derekbredensteiner/Developer/homesodamachine/hardware/reference/basics-mtb-0606wp/basics_mtb_0606wp.py` (+ generated `basics-mtb-0606wp.step`, `.step.png`). Nothing outside that directory touched.

## What I found

The part is the **Thogus TT3666** moulding. Chain: Industrial Specialties Mfg. lists `MTB-38-6M-*` ("3/8" Hose Barb × 3/8" Male NPT Branch Tee") with **MFR# TT3666/N, /P, /PP**; the FWS "Basics" scheme `MTB-&lt;barb 16ths&gt;&lt;thread 16ths&gt;&lt;color&gt;` maps 0606 to that exact configuration; and this repo already ties the discontinued MTB-0604 form to Thogus TT3466 (US Plastic 62806) in `internal-plumbing.md`.

Thogus publishes the drawing: **https://www.thogus.com/media/5wzciqvm/tt-3666_d.pdf** — rev D, "3/8" NPT X 3/8" BARB X 3/8" BARB TEE", with a per-material dimension table (PP / PE / Nylon rows, letters A–J). Rather than eyeball it I pulled the **vector content stream out of the PDF** and read coordinates directly. The views are drawn to scale 3:2 on a B-size sheet (108 pt per part-inch), which I verified against the drawing's own `G` dimension (240.80 pt = 2.2296" vs the table's 2.23 for nylon). Every "drawn" number below is therefore exact to the drafting, not estimated.

**MTB-0606**WP** is White Polypropylene, so I used the `/PP` row, not the `/N` row the views are drawn to.** PP runs ~1% under nylon (G 2.21 vs 2.23) — mould shrinkage.

## Dimension table

Tier: **a** = published drawing for this exact part/size · **b** = series table · **c** = governing standard · **d** = estimated

| Constant | mm | inch | Tier | Source |
|---|---|---|---|---|
| `RUN_LENGTH` | 56.13 | 2.21 | a | TT3666 dim **G**, /PP row — barb tip to barb tip |
| `BARB_ROOT_D` | 9.40 | .370 | a | dim **A** — run body Ø and the root between ridges |
| `BARB_CREST_D` | 10.92 | .430 | a | dim **B** — ridge crest |
| `BARB_TIP_D` | 9.03 | .3556 | a | drawn (undimensioned); measured off the to-scale views |
| `BARB_RIDGES` = 3 | — | — | a | drawn, both legs |
| `RIDGE_PITCH` | 3.94 | .155 | a | the one barb detail the drawing dimensions |
| `LEAD_LENGTH` | 3.96 | .156 | a | drawn — tip cone before the first ridge |
| `BRANCH_NECK_D` | 9.27 | .365 | a | dim **C** — between run body and hex |
| `HEX_ACROSS_FLATS` | 17.53 | .69 | a | dim **J** |
| `HEX_ACROSS_CORNERS` | 20.24 | .797 | derived | AF·2/√3 (drawing draws .8083 for the /N .70 — exact) |
| `HEX_LENGTH` | 6.35 | .25 | a | dim **D** |
| `BRANCH_HEIGHT` | 29.72 | 1.17 | a | dim **F** — **run centerline** to thread free end (verified: the F dimension line runs 520.80→394.40 pt, i.e. from the centerline) |
| `THREAD_LENGTH` | 12.45 | .49 | a | dim **E** — moulded thread, hex face to free end |
| `THREAD_MATE_PITCH_D` | 15.93 | .62701 | c | ASME B1.20.1 E₁, 3/8-18 NPT |
| `THREAD_TAPER` | 1/16 | — | c | ASME B1.20.1 |
| `BRANCH_ENGAGEMENT` | **9.53** | .375 | c | hand + wrench makeup; matches `jg_pp451223w.THREAD_ENGAGEMENT` |
| `THREAD_PROUD` | 2.92 | .115 | derived | `THREAD_LENGTH − BRANCH_ENGAGEMENT` |
| `RUN_BORE_D` | 6.22 | .245 | a | dim **H** — run through-bore |
| `BRANCH_BORE_D` | 10.92 | .430 | a | dim **I** — counterbore inside the threaded stub |
| `BRANCH_BORE_DEPTH` | 16.91 | .666 | a | drawn — in from the free end, then it steps to `RUN_BORE_D` |
| `CLAMP_LAND` | 7.65 | .301 | derived | half-run − barb zone − neck radius (drawn nylon land: .306) |
| wall thickness | 1.59 | .0625 | derived | (A − H)/2 on the run; 1.41 mm at the tip |

**Ridge profile** (from the extracted vector profile, radius from the run axis): tip Ø.3556 → a .156 lead cone to Ø.3759 → three .155-pitch cones each rising root→crest **toward the body** then dropping radially back. Sharp shoulder faces the body (resists pull-off), gradual ramp faces the tip. Crests at .311 / .466 / .620 from the tip, then .306 of smooth land.

**Corrections to your brief:** 0.4018" is **L2 for 1/4"** NPT, not 3/8" L1. Per ASME B1.20.1 (verified against the full table): 3/8-18 NPT has **E₀ = .61201, L1 = .2400, E₁ = .62701, L2 = .4078, K₀ = .5676, h = .04444**, pipe OD .675. Your later correction is what the module uses.

**Thread representation — read this.** The moulded crest cone is **Ø17.12 (.6741") at the hex face → Ø16.46 (.6481") at the free end**, i.e. the drawn taper is 1:18.8, shallower than NPT's 1:16. The module does **not** carry that. It carries the **pitch cone Ø16.11 → Ø15.33**, anchored so Ø15.93 falls exactly where the PP451223W's mouth lands, with a true 1:16 taper. Consequence: **the model understates the real branch OD by ~0.5 mm per side.** Clearance work around the branch thread should add 0.6 mm of radius, or treat 17.12 mm as the real OD at the hex face.

## Printed output

```
Bounding box: X [-28.07, 28.07]  Y [-8.77, 8.77]  Z [-5.46, 29.72]
Run 56.13 tip to tip; 3 ridges Ø10.92 per leg at 3.94 pitch; 7.65 of Ø9.4 land per side
Branch 29.72 to the NPT end; hex 17.53 across flats × 6.35 (top face Z = 17.27)
Thread pitch Ø16.11→Ø15.33 × 12.45; a female runs 9.53 down it, mouth at Z = 20.19, 2.92 proud
barb_a:        (-28.07, 0.00, 0.00) out (-1, 0, 0)
barb_b:        ( 28.07, 0.00, 0.00) out ( 1, 0, 0)
branch_thread: (  0.00, 0.00, 29.72) out ( 0, 0, 1)
Solid valid: True
```
One solid, 32 faces, 5128.9 mm³ ≈ 4.6 g in PP (FWS/ISM list ~0.01 lb). BBox X = G, Y = hex across flats, Z-max = F — all match the researched dimensions exactly.

**Mate verified** against `hardware/reference/jg-pp451223w/`: seating its mouth at Z = 29.72 − 9.53 gives **shared volume 0.000000 mm³, exact solid-to-solid distance 0.000000000 mm** — they share a surface and enclose no volume.

## Could not pin down

- **No drawing or dimensions exist for the FWS "Basics MTB-0606WP" itself.** FWS and NeoSupply publish material/temp/pressure only. So the drawing is tier (a) for the TT3666 moulding, and the claim "MTB-0606WP *is* that moulding" rests on size + configuration + form-match (I zoomed the FWS product photo: three ridges per leg, smooth land at the body, hex at the branch base, tapered NPT — all match) plus ISM's cross-reference. **Not proven by brand:** Thogus lists PP colours as black (PPB) and natural (PPN), no white. The docstring says "dimensions come off the Thogus TT3666 drawing" rather than asserting the brand.
- **Barb tip Ø, lead length, ridge pitch, counterbore depth** have no per-material column — they're drawn on the nylon view. Left at drawn values; PP would run ~0.9% smaller, well inside the drawing's own ±.015" on two-decimal dims.
- **Not modelled** (below resolution): the R.045" fillet at the neck/hex junction, and a ~.010"-tall raised pad on the run opposite the branch.

## Arrangement surprises

1. **The two hexes cannot both be wrenched.** Made up 9.53 mm, the PP451223W's 7/8" hex bottom face lands at **Z = 20.19**; the tee's hex top face is at **Z = 17.27** — a **2.92 mm axial gap**, and the adapter's 22.23 mm AF hex overhangs the tee's 17.53 mm AF by 2.35 mm per side. No jaw fits in there. **Make this joint up on the bench, before the tee goes into the hose line.**
2. **Only 7.65 mm of smooth clamp land per side.** A LOKMAN worm-gear band is typically 8–12.7 mm wide, so the clamp will straddle the last barb ridge (normal practice) — but check the band width; there is no room to seat a wide band purely on the land.
3. **The hose must be straight for the full 28 mm of each leg,** and the tee's own hex sits only **6.2 mm clear** of the run's outer surface — fine for an open-end wrench, tight for a socket.
4. **Crest Ø10.92 into a 9.53 mm ID hose = 1.4 mm diametral interference.** The hose needs warming or lube; it will not go on or come off by hand.
5. **The run bore is 6.22 mm, not 9.53** — this tee necks the 3/8" line down to just under 1/4" ID *on the main path*, not only the branch. Flag to whoever sizes the SeaFlo suction.
6. The branch is on the exact run midpoint, so the tee is symmetric — either leg can face either way — and the hex carries a **corner on the run axis**, flats facing ±Y (CadQuery's `polygon(6, d)` gives that natively, no rotation).</result>
<usage><subagent_tokens>269237</subagent_tokens><tool_uses>115</tool_uses><duration_ms>1805961</duration_ms></usage>
</task-notification>

---

# Assistant

---

The tee agent found the actual manufacturer drawing — it identified the moulding as **Thogus TT3666**, pulled the vector content stream out of the PDF, and read coordinates directly rather than eyeballing. That's real tier-(a) data. And it resolves the one number the arrangement agent flagged as sensitive:

---

# Assistant

---

Tee verified — three ridges per leg, hex at the branch base, NPT taper. And it **resolves the arrangement agent's one open sensitivity favorably**: it had worried the tee's radius about the run axis might be ~12 mm (assuming a 22-24 mm hex), which would have closed the nozzle-riser gap to 2.4 mm. Real hex is 17.53 across flats, so the body extends only 8.77 mm about the run axis — under the 9.4 mm threshold. Gap holds at ~5.6 mm. The proposal survives contact with the real dimensions.

Two findings from the tee worth your attention:

**1. The tee necks the main water path, not just the branch.** Dim H — the run through-bore — is **6.22 mm (.245")**. Your 3/8" ID (9.53 mm) silicone suction line passes through a 6.22 mm orifice on its way to the SeaFlo. That's a 57% area reduction *on the suction side of a diaphragm pump*, which is where restriction actually hurts — it's the classic cavitation/NPSH setup. Consistent with the moulding (9.40 barb root − 2 × 1.59 wall = 6.22), so it's not a modeling error. Worth deciding whether you care before it's in the line.

**2. The tee and the PP451223W cannot both be wrenched.** Made up 9.53 mm, the adapter's 7/8" hex bottom lands at Z = 20.19 and the tee's hex top is at Z = 17.27 — a **2.92 mm axial gap**, with the adapter's 22.23 mm hex overhanging the tee's 17.53 mm by 2.35 mm per side. No jaw fits. **That joint has to be made up on the bench before the tee goes into the hose line** — an assembly-order constraint for `internal-plumbing.md`, not just a geometry note.

Also: crest Ø10.92 into 9.53 mm ID hose is 1.4 mm diametral interference — those barbs need heat or lube, they will not go on by hand.

The agent verified the tee↔PP451223W mate at **0.000000 mm³ shared volume**, so the two stack cleanly. Waiting on the reducer stem and the fresh-eyes cross-check before I compose and place.

---

# User

---

<task-notification>
<task-id>af462d855ce28d575</task-id>
<tool-use-id>toolu_01KGoNQzrMcrPMmsFK3bpJbU</tool-use-id>
<output-file>/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/cf7ffd7d-2017-4caf-9a49-23e90eb4a417/tasks/af462d855ce28d575.output</output-file>
<status>completed</status>
<summary>Agent "Model JG PP061208W reducer stem" finished</summary>
<note>A task-notification fires each time this agent stops with no live background children of its own. The user can send it another message and resume it, so the same task-id may notify more than once.</note>
<result>Built and verified. Final report:

## 1. Dimension table

No published dimensional drawing exists for PP061208W — I exhausted the primary sources (details in §4). Numbers come from two places: JG's own **Cavity Dimensional Detail (Inch)** table (2025 Fluid System Catalog p.52, identical in the older JG USA fluid catalogs) and **photogrammetry on JG's own product photo** for the SKU.

| Constant | Value (mm) | Tier | Source |
|---|---|---|---|
| `STEM_D` | 9.53 | **c** | 3/8" nominal; JG tube tolerance +0.001/−0.004 in (JG *Drinks Dispense &amp; Pure Water Technical Specification*, "Tube tolerances", 1/4"–1/2" band). Photo reads 9.50–9.56 over the whole stem — the scale check. |
| `STEM_LENGTH` | 18.29 | **c** + **d** | JG 3/8" cavity **F1 = 0.720"**. Independently, photo gives 18.2–18.6. |
| `STEM_TIP_CHAMFER` | 0.6 | d | Lead-in visible in the photo; magnitude from comparable JG stems |
| `SHOULDER_D` | 10.35 | d | Photo, 10.25–10.35 |
| `SHOULDER_CONE_LENGTH` / `SHOULDER_LENGTH` | 1.3 / 3.0 | d | Photo profile |
| `BARREL_D` | 15.6 | d | Photo |
| `BODY_D` | 17.3 | d | Photo, 17.28–17.34 (widest point, carries the NSF-51 marking) |
| `BODY_CONE_LENGTH` / `BARREL_CONE_LENGTH` / `MOUTH_COLLAR_LENGTH` | 7.2 / 4.2 / 5.0 | d | Photo profile |
| `COLLET_NECK_D` / `RIM_D` / `TIP_D` | 11.4 / 12.4 / 11.0 | d | Repo's PP451223W 3/8" collet scaled by the JG cavity ØA ratio 13.41/16.05; cross-checks the 11.43 mm 1/4" release ring already in `jg_bulkhead_union.py` |
| `COLLET_NECK/RIM/TIP_LENGTH` → `COLLET_PROUD` | 1.7/0.7/1.0 → **3.4** | d | Same scaling |
| `TUBE_BORE_D` | 6.48 | **c** | JG 1/4" cavity **ØC = 0.255"** |
| `THROUGH_BORE_D` | 5.84 | **c** | JG 1/4" cavity **ØG = 0.230"** |
| `TUBE_STOP_DEPTH` | 14.10 | **c** | JG 1/4" cavity **F1 = 0.555"**, body face → tube stop |
| `TUBE_D` | 6.35 | a | 1/4" nominal |
| `LENGTH` | **42.39** (derived) | d | Photo 41.5–42.5 |
| `TUBE_INSERTION_DEPTH` | **17.50** (derived) | **c**-bracketed | `COLLET_PROUD + F1`; JG's own column H for 1/4" is 0.670" = 17.02 |

Photogrammetry method: scale locked by the stem = 3/8"; a linear perspective taper fitted along the stem (validated — the stem reads 9.50–9.56 over 250 px); foreshortening from a least-squares ellipse fit to the stem's end face, cos φ = 0.62 ± 0.03 (rms 1.6 px over 27 points). Axial numbers carry ≈ ±4%. Diameters carry ≈ ±2% and are the trustworthy half.

## 2. Printed output

```
Bounding box: X [0.00, 42.39]  Y [-8.65, 8.65]  Z [-8.65, 8.65]
Stem Ø9.53 × 18.29; shoulder Ø10.35; collar Ø17.3; collet proud 3.4; total 42.39 mm
Bore steps Ø6.48 (1/4" end) → Ø5.84 (stem); tube stop at X = 24.89
stem_tip:  at (0.00, 0.00, 0.00)   facing (-1, 0, 0)
tube_port: at (42.39, 0.00, 0.00)  facing (1, 0, 0)
Solid valid: True
```
`/Users/derekbredensteiner/Developer/homesodamachine/hardware/reference/jg-pp061208w/jg_pp061208w.py` → `jg-pp061208w.step` + `.step.png` (thumbnail rendered; silhouette matches the JG product photo). Nothing outside that directory was touched.

## 3. The two interface numbers

- **3/8" stem swallowed length = 18.29 mm** (JG 3/8" cavity F1 = 0.720"). The stem does **not** bottom out — it stops when the Ø10.35 shoulder ring lands on the mating PP451223W's collet mouth, tip still ~4 mm short of that fitting's tube stop. So the stacking rule is: *reducer shoulder plane = PP451223W collet-mouth plane*, and the reducer projects **42.39 − 18.29 = 24.10 mm** beyond it.
- **1/4" tube insertion depth = 17.50 mm** from the collet mouth (JG 1/4" cavity F1 14.10 + collet proud 3.40). JG's own catalog column H for 1/4" is 17.02 mm; the model is consistent with the sibling `jg_pp451223w.py`, which derives its insertion depth the same way.

## 4. What I could not pin down

- **No dimensional drawing for PP061208W exists publicly.** Checked: johnguest.com US/GB/CA product pages and their Resources tabs, the 2025 Fluid System Catalog, the UK *Drinks Dispense &amp; Pure Water Product Guide* and *Technical Specification*, `tech-spec-od-fittings-v2.pdf`, the JG Australia Technical Manual, two older JG USA fluid catalogs, the JG pneumatic metric catalog, plus Fresh Water Systems, ESP Water, H2O Distributors, Seelye, WebstaurantStore, Abbeychart, termoidraulicarv, URI, Home Depot, and McMaster. Every one lists only stem OD × tube OD, material, and pressure. JG's per-SKU downloads are catalog/warranty PDFs only.
- **JG publishes no insertion-depth table for inch OD-tube fittings** (its published tables are CTS/PEX only). The cavity table's column H is ambiguous — it is *not* consistently `F1 + collet proud` (the 5/8" and 12mm rows contradict it), so I did not treat H as an insertion depth; I derived insertion depth from F1 + the modeled collet proud instead, and noted H brackets it.
- **Fresh Water Systems' "shipping dimensions" 1.5 × 0.625 × 0.625 in are not the part** — 0.625 in = 15.9 mm is narrower than the measured 17.3 mm body, so the whole triple is auto-generated. I ignored it.
- Everything tier **d** would be improved in one minute with calipers on the physical part (a bag of 10 was delivered Jun 15, order WEBFWS100682118).

## 5. Things that will surprise whoever arranges it

- **No hex, no flats.** It is a plain molded barrel — you cannot wrench it, and there is no flat to index rotation off.
- **The stem is free to rotate in its socket.** PP451223W + PP061208W is a swivel joint, not a rigid one. Whatever the 1/4" collet points at is set by the tube, not by the fittings.
- **The stem can be pushed deeper than its resting position.** Depressing the mating collet lets it travel to ~22.3 mm; it settles back to 18.29 with the shoulder on the collet under pressure. Model the 18.29 resting case but don't design a hard stop that assumes it.
- **Collet release clearance is the real constraint at the 1/4" end.** To pull the tube you must push the Ø12.4 rim square against the body face — you need finger or release-tool access all the way around the mouth. Keep everything out of a ~Ø25 mm × 10 mm-deep cylinder in front of the collet or the joint is not serviceable.
- **Minimum straight tube run:** JG requires the tube to enter square and forbids side loads; its published rule is that clips must sit no closer than 2.5 in (63.5 mm) from the end of a fitting. Budget ≈ 65 mm of straight 1/4" LLDPE off the mouth before the first bend or support.
- **Polypropylene, not acetal** — JG rates PP lower mechanically and explicitly excludes it from compressed air and vacuum. It is the soft member of this stack.
- **The bore genuinely steps** (Ø6.48 → Ø5.84 at X = 24.89), so this fitting is the flow restriction in the branch, upstream of the flow regulator.</result>
<usage><subagent_tokens>265214</subagent_tokens><tool_uses>129</tool_uses><duration_ms>1838871</duration_ms></usage>
</task-notification>

---

# Assistant

---

All three modules build. Now let me compose them — the two adapters thread and plug *directly* onto the tee, which is exactly the "everything that fastens directly onto it" logic the ASSE assembly already uses:

---

# Assistant

---

All the interface constants line up. Writing the composed chain:

---

# Assistant

---

Stack closes at 80.29 mm — inside the 70-95 mm band the arrangement agent budgeted. Let me verify the house rule holds: threaded joints share a surface and no volume.

---

# Assistant

---

Clean: zero interference on all three pairs. The tee↔adapter joint shares a surface exactly (gap 0), and the 0.057 mm on adapter↔reducer is the real radial clearance of a Ø9.53 stem in a Ø9.65 socket bore — JG seals that joint with an O-ring, not a bore fit, so that's physically right.

---

# Assistant

---

That's the picture you were missing. All three parts, stacked as they actually assemble:

---

# Assistant

---

All five parts now exist as geometry. Where the numbers came from, honestly graded:

| part | strongest source | weakest part of the model |
|---|---|---|
| **MTB-0606WP** | **Thogus TT3666 drawing** — agent extracted the PDF's vector content stream and read coordinates directly, verified against the drawing's own scale bar. Used the `/PP` row, not the nylon row the views are drawn to. | Brand identity. Thogus lists PP in black and natural, not white — the *moulding* is certain, "Basics MTB-0606WP **is** that moulding" rests on size + configuration + ISM's cross-reference + form-match on the FWS photo. |
| **PP451223W** | JG's own **Cavity Dimensional Detail** table (2025 catalog p.53) for everything internal — tube stop, bores, insertion depth. Thread geometry from ASME B1.20.1. | External envelope scaled off McMaster's dimensioned drawing of the same JG family one thread size down. `LENGTH`, hex, and body Ø are the three to caliper. |
| **PP061208W** | JG cavity table for the bores and both F1 depths. | **Weakest of the three.** No public drawing exists; the outer profile is photogrammetry off JG's product photo (±4% axial, ±2% diametral). |

You have bags of 10 of each from Jun 15 — **thirty seconds with calipers on the PP061208W's overall length and body Ø would move it from tier (d) to tier (a)**, and it's the one carrying the most estimate.

One thing I want to flag because it changes assembly *order*, not just geometry: the tee↔PP451223W joint has no wrench access once made up — 2.92 mm between hexes, with the adapter's 7/8" overhanging the tee's 11/16" by 2.35 mm a side. That joint gets made up on the bench before the tee ever goes into the hose line. And the reducer above it has no flats at all and swivels in its socket, so nothing on that branch is wrench-work in place.

Still holding the placement until the fresh-eyes agent reports — it's cross-checking a recommendation that would flip the ASSE end-for-end and move two rear-panel ports, and I'd rather have that challenged than just seconded.

---

# User

---

<task-notification>
<task-id>af0c999db97c27b65</task-id>
<tool-use-id>toolu_01Y7VS3M4zWKqV923hMAdWqt</tool-use-id>
<output-file>/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/cf7ffd7d-2017-4caf-9a49-23e90eb4a417/tasks/af0c999db97c27b65.output</output-file>
<status>completed</status>
<summary>Agent "Fresh-eyes upper deck challenge" finished</summary>
<note>A task-notification fires each time this agent stops with no live background children of its own. The user can send it another message and resume it, so the same task-id may notify more than once.</note>
<result>## Top finding, one sentence

**The SeaFlo pump — the single largest body left to place, 188 × 98 × 74 mm — does not fit anywhere in this enclosure as packed, in any orientation, and the only volume in the whole machine that can take it is the bay floor the electronics shelf is sitting on; every other question below is downstream of that.**

```
tools/cad-venv/bin/python hardware/scripts/probe.py selftest   →  PASS (50 bodies, 20 runs)
```

Exhaustive search, every axis-aligned orientation, 2 mm stations, over the whole interior
(x 0–283, y −3–384, z 0–331.72), occupancy = each body's **bounding box** (which *contains*
the solid, so a "free" answer is provably free) plus the shell's measured intrusions:

| envelope | placements in the whole box |
|---|---|
| SeaFlo body-only, 80 × 72 × 187 (the stash's number) | **0** |
| SeaFlo as modelled, `hardware/reference/seaflo-22-pump` 188 × 98 × 74 | **0** |
| + feet splay + isolation mounts, 98 × 82 × 200 | **0** |
| a 80 × 72 × **100** stand-in, for scale | **0** |

Restricted to the service bay (z &gt; 253.4) with the 1 mm grid:

```
as-packed:                 0 placements of 80x72x187
electronics shelf evicted: 204 placements — one orientation only (187,80,72),
                           corner x[0..4] y[200..232] z[253..259]
shelf + ASSE evicted:      492 placements, same single orientation
EMPTY bay:                 9996 placements, still only (187,80,72)
```

Five of the six orientations **do not fit the bay envelope at all** before any content is
considered: 187 exceeds the bay's depth (184 mm, y 200→384) and its height (78.32 mm).
The pump has exactly one pose available — lying flat, long axis along X — and 4.3 mm of
headroom in it.

Verified exactly, on the real solids, not boxes:

```
probe.hits(box(x=(0.0,188.0), y=(200.0,298.0), z=(253.4,327.4)))
   power-tray   214834.3 mm³
   pcba            167.5 mm³
same, skip=("power-tray","pcba","dc-dist")            → CLEAR
probe.hits(box(x=(48,236), y=(200,298), z=(253.4,327.4)),
           skip=("power-tray","pcba","dc-dist"))       → CLEAR
```

So: the SeaFlo's home is the bay's front half, and the electronics shelf is in it. Nothing
can share the bay's height with the pump — 74 of 78.32 mm.

The accounting in one table:

| | bbox volume |
|---|---|
| bay envelope (283 × 184 × 78.32) | 4.078 L |
| power-tray | 0.452 L |
| pcba | 0.180 L |
| asse1022-assembly | 0.176 L |
| dc-dist | 0.023 L |
| **SeaFlo (unplaced)** | **1.363 L** |

The bay is 66.8 % free by volume and still cannot take the pump. That is fragmentation from
packing in ascending order of size.

---

## 2. The free-volume map of the service bay

Bay = x 0–283 (inboard of the 14 mm boss-chain bands at x[−14,0] and [283,297]),
y 200–384, z 253.4–331.72. Shell intrusion inside that box, measured not assumed:

```
probe box (0,283)×(200,384)×(281,331.7) ∩ back pieces → CLEAR
probe box (0,283)×(200,384)×(253.4,331.7) ∩ back pieces
   → enclosure-back-bottom  x[0,283] y[381,384] z[264,280.1]   (rear Z-seam lip, a 3 mm ledge)
```

Every box below verified with `probe.hits`, exact solids:

| | box | size | cm³ | note |
|---|---|---|---|---|
| **A** | x[0,283] y[200,311] z[296.5,331.7] | 283 × 111 × 35.2 | 1106 | **CLEAR.** Dead air over the electronics shelf — but see below, this is the carb riser's only lane |
| **B** | x[0,185] y[200,229.9] z[253.4,331.7] | 185 × 30 × 78.3 | 433 | **CLEAR**, full height. Contains the foam's CO2 top entry at (141.5, 217.8, 262.9) |
| **F** | x[0,185] y[230,304] z[296.5,331.7] | 185 × 74 × 35.2 | 482 | **CLEAR** (part of A, called out because it is over the power tray) |
| **D** | x[0,42.5] y[274,384] z[274,331.7] | 42.5 × 110 × 57.7 | 270 | power-tray corner 1225 mm³; otherwise clear. The strip's west end |
| **C** | x[74,191] y[304,381] z[253.4,280.4] | 117 × 77 × 27 | 243 | **CLEAR.** The band under the ASSE — the drip pan's reserved ground |
| **E** | x[166,283] y[304,360] z[253.4,289] | 117 × 56 × 35.6 | 233 | **CLEAR.** Under the umbilical cluster |
| **G** | x[0,74] y[356,384] z[253.4,331.7] | 74 × 28 × 78.3 | 162 | **CLEAR.** Rear wall west of every panel body |
| **H** | x[237,283] y[356,384] z[253.4,331.7] | 46 × 28 × 78.3 | 101 | **CLEAR.** Rear wall east of every panel body |
| **C′** | x[0,191] y[304,381] z[274,280.4] | 191 × 77 × 6.4 | 94 | **CLEAR** — C widened west over the DC block |

What that map says: **the bay's free volume is a 35 mm slab of air across the top and a
27 mm slab of air across the aft floor.** Neither is 74 mm tall. The bay is a single-storey
floor plan with a whole second storey of air above it, and the one body that has to go in
it needs the storeys merged.

Two caveats on "free":

- **A is not free — it is the carbonated-water riser's lane.** `foam-assembly.carb-water-out`
  is at (141.5, 200, 46.5) facing −Y; `bulkhead-carb.tube-in` is at (210, 359.2, 318.3).
  That line is 1/4" LLDPE inside CARGEN 1/4" ID × 3/8" wall foam = **Ø25.4 mm OD**, insulated
  end to end per `back-panel/README.md` and `internal-plumbing.md` §4.
  ```
  w.cast((210,199,318.3),(0,1,0),dia=25.4) → runs 163.21 mm, stopped by bulkhead-carb
  w.cast((141.5,199,300),(0,1,0),dia=25.4) → runs 133.42 mm, stopped by asse1022-assembly
  w.cast((141.5,199,280),(0,1,0),dia=25.4) → runs  36.72 mm, stopped by power-tray
  ```
  The only clear aft crossing for that Ø25.4 bundle is high, near the carb bulkhead's own
  x/z. It is unrouted, unallocated, and the ASSE is already standing in the x = 141.5 version
  of it.
- **C is the drip pan's.** The vent tip is at (98, 312, 305) and the declared 70 × 50 pan
  footprint therefore sits x 63–133, y 287–337 on the cap.

---

## 3. Findings

### Finding 1 — Is the aft strip a good home for the ASSE chain? No. It is over-committed, and it is a symptom, not the disease.

The strip's usable depth is `power-tray.ymax 303.94 → c14-inlet.ymin 360` = **56.06 mm**.
The ASSE with the vent laid over occupies **43.29 mm** of it (placed box y 312–355.29).
That is 77 % of the corridor, spent on the *smallest* of the water deck's four remaining
bodies.

Measured margins, all exact solid distances:

```
w.gap("asse1022-assembly","c14-inlet")         =  4.711 mm
w.gap("asse1022-assembly","bulkhead-water")    = 10.095 mm
w.gap("water-1","fluid-28")                    =  4.691 mm
w.cast((145,359.2,293),(0,-1,0),dia=6.35)      → runs 11.25 mm, stopped by asse1022-assembly
w.cast((90,357,295.5),(0,-1,0),dia=12.0)       → runs  1.71 mm, stopped by asse1022-assembly
w.cast((90,357,295.5),(0,0,-1),dia=12.0)       → runs  0.00 mm, stopped by asse1022-assembly
```

That last pair is worth reading twice: **the C14's own mains conductors cannot leave their
receptacle in either the forward or the downward direction without hitting the backflow
preventer.** A Ø12 cord bundle gets 1.71 mm forward and 0 mm down. The cord has to leave
sideways and thread around the chain.

Beyond the margins, four things make the pose a trap rather than a tight fit:

1. **Its 3/8" outlet fires into a dead end.** `hose-out` is at (42.5, 341, 305) facing −X,
   with 42.5 mm to x = 0 and 56.5 mm to the −X interior wall. JoyTube 3/8" ID × 1/2" OD
   silicone will not make a useful turn in that. The far end of that hose (`water-2`) is
   already declared blocked in `_lines.BLOCKED` — it "lands on nothing."
2. **The tap-point tee rides that same dead-end hose.** `internal-plumbing.md` open item 3 is
   CLOSED: MTB-0606WP tee inline between FFL38BARB38 and the SeaFlo suction, branch →
   PP451223W → PP061208W → 1/4" LLDPE → V-A. `V-A-I` is at **(271.33, 172.28, 198.66)**.
   Straight-line from the ASSE's barb: **303.7 mm**, across the full width of the machine
   and down two storeys, for a line whose whole job is a trickle.
3. **It blocks the carb riser's aft crossing** (cast above, stopped at y 332.42).
4. **It is the tallest body in the pack** (zmax 321.50) and therefore the second binding term
   on the box ceiling — see Finding 5.

And the placement comment's own PROVISIONAL caveat is real: the 123.5 × 33 × 43.3 envelope
is the reference model's spec-sheet arithmetic, not four parts measured on the bench. A
4.71 mm margin against an unmeasured envelope is not a margin.

**Verdict: over-committed.** The specific decision that is the problem is not "the ASSE lies
along X" — it is *"the ASSE was placed before the SeaFlo it feeds."* The ASSE is the first
component on the water path and it was given a position derived from the rear bulkhead;
but its outlet is a 3/8" stiff hose that must reach a 1.36 L pump, and that pump's position
is the only thing that can legitimately fix the ASSE's.

### Finding 2 — see the map above.

### Finding 3 — The C14 corner. He is right; it is not in one, and it is in the worst possible place instead.

Rear-panel legal field, computed from the real hardware:

- boss-chain / corner-post bands occupy x[−14,0] and x[283,297] at y 367.7–384, z 267–331.7
  (measured: `enclosure-back-top` ∩ interior).
- a Ø22.86 bulkhead **nut** therefore needs 11.43 ≤ x ≤ 271.57
- a 30.5 mm C14 **flange** needs 15.25 ≤ x ≤ 267.75
- `UMBILICAL_Z_FLOOR = 281` (the rear Z-seam lip band) ⇒ lowest nut centre z = 292.43

Current: **C14 at x = 90, z = 295.** That is **74.75 mm east of the west-most legal station**
and 2.25 mm above the floor station. Bottom row, dead centre-west. Not a corner.

The far-west station is empty and clear:

```
probe.hits(box(x=(0.75,31.25), y=(360,384), z=(283.75,307.25)), skip=("c14-inlet",)) → CLEAR
probe.hits(box(x=(9.75,40.25), y=(360,384), z=(283.75,307.25)), skip=("c14-inlet",)) → CLEAR
probe.hits(box(x=(0,74),  y=(356,384), z=(253.4,331.7)))                             → CLEAR
```

I'd put it at **x ≈ 22** (7 mm off the corner post rather than 0.75).

What moving it buys:

- **The 4.71 mm constraint disappears entirely.** ASSE spans x 42.5–166; a C14 at x 22 spans
  x 6.75–37.25 — no overlap in X at all. The ASSE's aft travel would then be bounded only by
  `bulkhead-water` at 10.095 mm.
- **91 mm of rear-panel bottom row frees up** (x 31 → x 122).
- **It gets mains AC out of the drip pan's airspace.** This is the part worth a comment. The
  ASSE 1022's atmospheric vent exists *to weep water* — it is the mechanical telltale for a
  cross-contamination event, per `future.md` "Backflow vent monitoring", and there is a
  moisture sensor under it because water is expected there. The drip column is at x = 98; the
  pan's declared 70 × 50 ground is x 63–133, y 287–337. The C14 body is x 74.75–105.25, and
  `_contents.py` explicitly routes its cordage forward across y 304→360 at x ≈ 90 — **directly
  over the open pan**, in the same band the design has reserved for catching water. That is
  the one place in the machine where line-voltage conductors and a deliberate water drip share
  a volume. Move the C14 west and the cord lane goes with it.

Cost of moving it: essentially nothing — the AC hub is on the power tray at x 24–175.1, so a
C14 at x 22 lands at the tray's west end and the cord run gets *shorter*, not longer.

### Finding 4 — The four rear bulkheads are placed by a packing aesthetic, not by the runs that serve them.

Ports and their sources:

| bulkhead | inboard collet | fed by | comment |
|---|---|---|---|
| `bulkhead-water` | (145, 359.2, 293) | → ASSE `tube-in` at (166, 341, 305), 21 mm east | run leaves the wall, goes **east past** the inlet, then closes back **west** into it — `water-1`, 80.6 mm, 4 bends, to travel 21 mm |
| `bulkhead-flavor-b` | (195.05, 359.2, 292.45) | ← `elbow-noz-b`, +X wall pocket, lane x = 262.18 | 67.1 mm westward jog at the end of the run |
| `bulkhead-flavor-a` | (224.95, 359.2, 292.45) | ← `elbow-noz-a`, +X wall pocket, lane x = 274.18 | 49.2 mm westward jog |
| `bulkhead-carb` | (210, 359.2, **318.3**) | ← `foam-assembly.carb-water-out` (141.5, 200, 46.5) | the longest, coldest, **fattest** line in the machine (Ø25.4 insulated) is given the highest and most distant port |

Both flavor runs arrive from the +X wall pocket and both are then dragged 50–67 mm back
west; the carb line arrives from front-bottom-centre and is sent to the top vertex. Every one
of those jogs exists because the three umbilical holes are a **triangle centred on
UMBILICAL_X = 210** — a cluster chosen in `back-panel/README.md` as "the densest-three-circle
triangle the tube bundle packs into." The bundle is a sleeved run coming down through the
countertop from outside; it fans at the panel regardless. The triangle is serving the
*outside* of the panel, and every run on the *inside* is paying for it.

The bill for the triangle is exact:

```
port_top = max over back_wall_ports of (z + footprint_h/2)
  flavor B  292.43 → 303.86
  flavor A  292.43 → 303.86
  carb      318.29 → 329.72     ← binding
  water     293.00 → 304.43
  C14       295.00 → 306.75
iz1 = port_top + 2.0 = 331.72          ← the box ceiling
```

**The carbonated-water bulkhead's nut sets the height of the entire appliance.** Flatten the
triangle to a row at z = 292.43 and `port_top` drops to 303.86; the ceiling then falls to the
next binding term, `czmax = 321.50` — which is the ASSE. Move the ASSE down too and the box
gets materially shorter, or (the useful direction) the ceiling becomes a number you *choose*
from the contents rather than inherit from a hole pattern.

Recommendation: the bulkheads are movable and should move. Put the two flavor bulkheads
**east under their own lanes** (x ≈ 250 and 272 — box H at x 237–283 is CLEAR), the carb next
to them, the water bulkhead **west** where the ASSE and the SeaFlo's head want to be
(box G at x 0–74 is CLEAR), and the C14 in the west corner. That is: utilities west, umbilical
east, each port under the run that serves it.

### Finding 5 — The thing nobody has questioned

Two, and they are the same thing seen from two ends.

**(a) The bay's height is a derived number that nobody has treated as a design variable.**
78.32 mm of bay is what fell out of a rear-panel hole pattern. The SeaFlo needs 74 of it.
So the fit of the largest body in the machine is currently decided by how three tubes bundle
outside the cabinet. Reverse the dependency — size the bay from the water deck, then place
the ports in it — and the electronics-versus-pump conflict evaporates. Concretely: a bay tall
enough for the SeaFlo (74) plus an electronics deck (40.5) plus clearances needs **≈ 119.5 mm**,
i.e. a ceiling at ≈ 373 instead of 331.72 — **+41 mm on a box that is 337.7 mm tall outside.**
That is the honest price of the contents, and it is a much smaller and more actionable number
than the stash note's "grows box 12mm &amp; cascades clashes." If the power deck can be re-laid
to ≤ 27 mm tall it drops into the already-clear aft band (box C, x 74–191, y 304–381,
z 253.4–280.4) and the growth falls to roughly **+14 mm**.

**(b) The pack has been built in ascending order of size, and the water deck was never
allocated a region at all.** The bay currently holds four bodies totalling 0.83 L of bounding
box, arranged so that a 1.36 L body has zero legal positions in a 4.08 L volume that is
66.8 % empty. Every other subsystem in this machine got a *named region* — Zone A, the machine
corridor, the front column, the bag-fall corridor, the junction column, the +X wall pocket.
The water deck got leftovers. Its four remaining bodies (SeaFlo, ASSE, drip pan, flow sensor)
plus the tee stack and two checks have never been sized as a group against a volume.

Corollary that falls out of the same blind spot: the insulated carb riser. The bag-fall
corridor it would have to climb past the tray stack is
`foam.ymin 200.0 − src.ymax 181.99 = 18.01 mm`, and the insulated line is **Ø25.4**. The
insulation cannot pass the manifold stack anywhere across the box's width, which contradicts
the "insulation continuity from the foam-shell exit to the bulkhead" target in
`internal-plumbing.md` §4. Same disease: a line's *real* diameter never met a lane.

**Answering your specific candidates:** the ASSE does not have to lie along X — but changing
that alone fixes nothing. Whether the electronics and the water deck should share the bay is
the right question, and the answer is **no, they cannot** — the bay's height takes one of them.
The drip pan should absolutely drive the ASSE's pose rather than the reverse: with the C14
gone west, the ASSE can drop and use its **native −Z vent** (no roll at all), dripping straight
into a pan directly beneath the tip, which is what the fitting is designed to do — instead of
a 51.6 mm sideways-and-forward fall past a shelf edge with 4 mm to spare. And yes: the SeaFlo
being unplaced this late means the bay was packed in the wrong order.

---

## 4. If I were laying out this bay from scratch today

Rough, committed. Bay = x 0–283, y 200–384, z 253.4–331.72 (or taller, see below).

| body | position | why / probe evidence |
|---|---|---|
| **SeaFlo 22-series** (188 × 98 × 74) | **x 55–243, y 232–330, z 254–328**, motor axis along X, head (both 3/8" barbs) facing **west** at x = 55 | The only pose that exists. `probe.hits(box(x=(48,236),y=(200,298),z=(253.4,327.4)), skip=shelf) → CLEAR`. y 232 clears the CO2 top entry at (141.5, 217.8, 262.9); y 330 stops 30 mm short of the panel bodies. Isolation-mounted to the foam cap. |
| **ASSE 1022** | **x 2–45, lying along Y, y 245–368, z 285–318, vent NATIVE −Z (no roll)** at ≈ (23, 300, 285) | The west channel is free full height (box D/G). Vent drips ~17 mm straight down into a pan sitting directly beneath it. Inlet at the north end, one short stub off a west water bulkhead. Barb at the south end, aimed east at the SeaFlo head. |
| **Drip pan + moisture plate** (70 × 50, plate 54 × 40 × 1.6) | **x 0–48, y 275–325, on the cap at z 253.4** | Directly under the vent tip, not 51.6 mm away. No cordage over it. |
| **MTB-0606WP tee + PP451223W + PP061208W** | inline on the 3/8" hose at **x ≈ 22**, branch stack (~90–108 mm) hanging **−Y, forward** | `probe.hits(box(x=(13,31), y=(247,341), z=(296,314))) → CLEAR`. Hanging it **−Z** does not work: `probe.hits(box(x=(13,31),y=(332,350),z=(211,305)))` hits `foam-assembly` and `dc-dist`. |
| **Rear-panel water bulkhead** | **x ≈ 22, z ≈ 293** | Box G (x 0–74, y 356–384) is CLEAR. Turns `water-1` from an 80.6 mm 4-bend pigtail into a straight stub. |
| **C14 mains inlet** | **x ≈ 22 is taken by water — put the C14 at x ≈ 250–260, or water east and C14 west** — pick one; the point is *both are corner-station parts and neither is at a corner today* | `probe.hits(box(x=(0.75,31.25),y=(360,384),z=(283.75,307.25))) → CLEAR`; box H (x 237–283) equally clear. Keep mains out of the pan's x-span (63–133). |
| **Umbilical: flavor A / flavor B / carb** | **a flat ROW at z ≈ 292.4**, x ≈ 250 / 272 / 228 | Under the lanes that feed them; kills the 49–67 mm westward jogs; drops `port_top` from 329.72 to 303.86 and releases the ceiling as a design variable. |
| **Electronics (power tray, PCBA, DC block)** | **aft band, y 304–381, z 253.4–280.4** if the power deck can be re-laid ≤ 27 mm tall (box C is CLEAR, 117 × 77 × 27, and C′ widens it west); **otherwise the bay grows ≈ 41 mm and they get their own storey above the SeaFlo** | Not the compressor compartment — that is the isobutane zone with the MQ-6 in it; a PSU and relays do not belong there. |
| **DIGITEN flow sensor** (60 × 22 × 29) | stays in the front column on the carb riser, not in the bay | Its line is `carb-water-out` at (141.5, 200, 46.5). |

The one number to take away: **either 13.5 mm of power-tray height, or ≈ 41 mm of box
height.** Everything else in the bay closes once one of those is chosen.

---

## 5. What I'd do first

**Do not model the tee and its two adapters yet.** Here is the specific reason, not a general
one: the tee is inline in the 3/8" silicone hose *between* `asse1022-assembly.hose-out` and
the SeaFlo suction — that is segment `water-2`, and `_lines.BLOCKED["water-2"]` already says
in the repo's own words that the hose "leaves the ASSE 1022's barb at (42.5, 341, 305) heading
−X … and lands on nothing." Placing three bodies on a hose whose far end does not exist means
hand-picking a station, and all three move the day the pump lands — along with the MAACFLOW,
the GASHER check, the second PP010822E, and segment 1 to `V-A-I`. That is six more bodies
accreting onto a provisional guess.

**First move, in order:**

1. **Place the SeaFlo.** Provisionally is fine — `x 55–243, y 232–330, z 254–328`, head west,
   using the real `hardware/reference/seaflo-22-pump` STEP (188 × 98 × 74, already modelled and
   `shaped`-clean). It is the anchor for `water-2`, `water-3`, the tee, the MAACFLOW, the
   GASHER check and segment 1. Placing it forces the bay conversation instead of deferring it
   a seventh time.
2. **That immediately fails the pack** against `power-tray` (214.8 cm³) — which is the correct
   and useful outcome. It converts "the SeaFlo needs a lane found for it" (requirements.md,
   currently a sentence) into a failing `pack-closes` gate with a named body, which is exactly
   the discipline the scorecard exists to enforce.
3. **Move the C14 to a corner** (one constant, `C14_BACK_X`). Verified clear, costs nothing,
   removes the ASSE's binding 4.71 mm constraint, shortens the AC cord run, and takes mains
   voltage out of the drip pan's airspace.
4. **Then** re-place the ASSE against the SeaFlo's suction barb — with the drip pan's position
   driving the vent's pose rather than the other way round, and probably with no roll at all.
5. **Then** the tee and its two adapters, derived from the hose between two placed ports rather
   than hand-set. Both adapter models already exist (`hardware/reference/jg-pp451223w`,
   `hardware/reference/jg-pp061208w`), as does the tee (`basics-mtb-0606wp`, 56.13 × 17.53 ×
   35.18, branch reaching +Z 29.72 from the run axis), so this step is ten minutes once the
   two endpoints are real.

Nothing under `hardware/` was modified, and nothing was committed. Scratch scripts are in
`/private/tmp/claude-501/.../scratchpad/` (`bay3.py`, `whole.py`, `verify.py`, `exact.py`,
`final.py`) if you want to re-run any of the surveys. `git stash` was read with
`show -p`/`show --stat` only — not applied, not dropped.</result>
<usage><subagent_tokens>250803</subagent_tokens><tool_uses>53</tool_uses><duration_ms>2481641</duration_ms></usage>
</task-notification>

---

# Assistant

---

Both arrangement agents are in. They independently agree the SeaFlo is the root problem — but they disagree on its actual size, which matters. Let me settle that:

---

# Assistant

---

Settled: the reference model is authoritative at **188 × 98 × 74** (the stash's 80 × 72 × 187 was body-only, sans feet). The fresh-eyes agent used the real one. Both got zero placements either way, so the conclusion holds regardless.

Let me document the new assembly and commit the modeling work.

---

# Assistant

---

The enclosure artifacts got touched by the dev-server watcher. Per CLAUDE.md the committed scorecard must carry measured clearances, so let me check what state they're in before committing:

---

# Assistant

---

Only change is the vent stub's box growing 324.5 → 326.711 — exactly the 2.211 mm fix, flowing correctly into the placed world. Let me do the clean build (clearances measured) before committing:

---

# Assistant

---

All 7 gates pass on a clean build with clearances measured. Committing in two pieces, since these are two different changes:

---

# Assistant

---

Committed and pushed — [71fa356c](https://github.com/derekbreden/homesodamachine/commit/71fa356c) (the three fittings + their stack) and [af639af1](https://github.com/derekbreden/homesodamachine/commit/af639af1) (the stub datum + palette).

**Your five parts are all in 3D now.** Two were always there and just invisible; three are newly modeled off manufacturer data and composed into a stack that closes at 80.29 mm with zero interference.

What I did **not** do is place the tap-point assembly in the enclosure, and I want to be straight about why rather than quietly hand you a number. Both arrangement agents, working independently, landed on the same wall:

**The SeaFlo has nowhere to go.** 188 × 98 × 74 (its own reference model, feet included). Exhaustive search, every orientation, 2 mm stations, bounding-box occupancy so a "free" answer is provably free:

- **0 placements** in the entire interior, as packed
- **0 placements** even with the whole service bay emptied of everything movable
- Five of six orientations don't fit the bay *envelope* before any content is considered
- One legal pose exists — flat, long axis along X — with **4.32 mm of headroom**
- The bay is **66.8% free by volume** and still can't take it. That's fragmentation from packing in ascending order of size.

The tee is inline on the hose between the ASSE barb and that pump. `_lines.BLOCKED["water-2"]` already says the hose *"leaves the ASSE 1022's barb at (42.5, 341, 305) heading −X… and lands on nothing."* Placing three bodies on that hose means hand-picking a station that moves the day the pump lands — and the MAACFLOW, GASHER check, and segment 1 to V-A accrete onto the same guess.

The two agents split on this and I'm siding with pump-first. The tee-first argument was "the tee has two hard anchors, the pump has one soft anchor" — but that same agent proved the pump has *zero* legal positions. A body with one available pose is the most rigid thing in the machine, not the most flexible. That reasoning was inverted.

Three other findings worth having regardless:

1. **The carb bulkhead's nut sets your appliance's height.** `port_top` = 329.72 → `iz1` = 331.72. A hole pattern serving the tube bundle *outside* the cabinet is deciding the box ceiling. Flatten the umbilical triangle to a row and the ceiling becomes something you choose from contents instead of inherit.
2. **Mains AC crosses the drip pan.** C14 body spans x 74.75–105.25; the pan's reserved ground is x 63–133. `_contents.py` routes its cordage forward at x ≈ 90, directly over the volume designed to catch water from the backflow vent. Also: a Ø12 cord bundle gets **1.71 mm forward and 0.00 mm down** off the C14 before hitting the ASSE.
3. **The insulated carb riser can't pass the manifold stack** — Ø25.4 line, 18.01 mm gap. Contradicts the insulation-continuity target in `internal-plumbing.md` §4.

---

# Assistant

---

Clear. Electronics come out, pack tight, C14 west. Let me set up tracking for this — it's a real re-layout, not a tweak.

---

# Assistant

---

Starting with the electronics and the C14 — both are removals/moves that stand alone:

---

# Assistant

---

Now I need the SeaFlo's own frame and ports before I can place it:

---

# Assistant

---

The SeaFlo model has no port functions — it can't be routed to without them. Adding them:

---

# Assistant

---

Placing this well is a real packing problem, and I've found a hard constraint neither arrangement agent knew: **the tap-point assembly is 85.75 mm tall, and the bay is 78.32 mm.** Its branch physically cannot stand vertical in this bay — that's why "branch −Y" isn't a preference, it's forced. Let me put the packing search in front of fresh eyes with that constraint stated:

---

# Assistant

---

Expected — `_lines.py` uses the PCBA as a routing datum. Let me see what it's actually measuring:

---

# Assistant

---

The C14 at x = 22 clashes with the printed back-top wall piece (1769.5 mm³) — so the earlier "CLEAR" probe checked the *body* against placed parts, not against the printed wall. Let me find the real legal range:

---

# Assistant

---

Let me stop reverse-engineering the piece API and test the two variables directly. Reverting only the Z change, keeping x = 22:

---

# Assistant

---

The Z change was the culprit, not the X move. Let me confirm the full gate state:

---

# Assistant

---

Those bounding boxes overlap — pump x[95,283] against fluid-18 x[221.77,292.38] at shared z and y. A "0 clash" there is suspicious. Let me re-run without filtering and read the real output:

---

# Assistant

---

I misread a stale scorecard a moment ago — the clash is real and still there. The C14 fix landed (it was the Z change, not the X move), but the pump's east end runs into the two nozzle-flavor lanes. Passing that to the packing agent, since it's a constraint it needs:

---

# Assistant

---

Two of the six done. Where things stand:

**Electronics are out.** `power-tray`, `pcba` and `dc-dist` are no longer placed — they stay declared in the scorecard registry as components without a station, so they read as work still owed rather than vanishing. One real coupling had to be cut: [_lines.py:392](hardware/printed-parts/enclosure/enclosure-assembly/_lines.py:392) used the PCBA's board height as a datum for the nozzle-lane clearance guard, so that guard now checks each body it actually crosses instead of assuming the shelf is there.

**C14 is in the west corner** at x[6.75, 37.25] — was x[74.75, 105.25]. That's it out of the drip pan's ground (x 63–133) entirely, so mains conductors and the backflow vent's deliberate drip no longer share a volume.

Worth recording, because it contradicts what the arrangement agent derived: I also tried lowering it to `C14_BACK_Z = 293` (the agent computed the port field's floor as `UMBILICAL_Z_FLOOR + nut radius` = 292.43). **That clashes with the printed back-top piece by 1769.5 mm³.** The agent had verified x = 22 by probing the C14 *body* against placed parts — but the printed wall is a `piece`, not a placed body, and the probe query it ran never saw it. 295 is clean. The lesson generalizes: any rear-port Z move has to be checked against the printed piece, not just the pack.

**The pump doesn't fit where I put it.** Provisional `SEAFLO_POS = (95, 232)` gives x[95, 283] — and its east end sits on the two nozzle→flavor runs, which climb the +X wall pocket on lanes at x = 274.18 and 262.18:

```
fluid-18 ∩ seaflo-pump: 1165.2 mm³
fluid-28 ∩ seaflo-pump: 3689.6 mm³
```

So the east pocket isn't free space — it's a lane for a 291 mm and a 355 mm run. Either the pump comes west (shrinking the channel the ASSE and tap point need) or those two runs re-route. Both flavor bulkheads are movable now, so re-routing may be the cheaper side; the packing agent has it along with the endpoints for `water-2`/`water-3`.

One correction to something I said earlier in passing: I read a stale scorecard between builds and briefly took the gates as passing. They aren't — the tube-clash gate is red on exactly the two lines above. Nothing is committed in that state.

---

# User

---

> Nothing is committed in that state.

I don't understand why you agents are so afraid of commitment. If we have to roll it back, we roll it back. It's not like there's anyone else using this code for anything where it matters - what matters most is what makes our development and engineering process easier, and if committing partial work helps, we should do it, not avoid it.

---

# Assistant

---

Fair — and it's in your CLAUDE.md, which I should have followed. Committing it.

---

# Assistant

---

A pile of untracked `hardware/assembly/cards/*` files exist that aren't mine — I'll leave those for you to judge and commit only my own changes. First a clean rebuild so the artifacts match the source:

---

# Assistant

---

While that builds, let me find out what those untracked cards are:

---

# Assistant

---

The dev-server keeps winning the build lock. Let me check whether its own rebuild already produced current artifacts:

---

# Assistant

---

The scorecard is stale (20:23 vs my 20:42 edits) — that's what I misread earlier. The dev-server keeps preempting. Let me retry until a build actually lands:

---

# Assistant

---

Still stale. The build is being killed before it writes. Let me look at what's actually holding the lock:

---

# Assistant

---

`HSM_BUILD_LOCK_PROTECT=1` exists exactly for this — it marks a build that must not be superseded. That's what the commit gates use:

---

# Assistant

---

Committed as [5c5ad1e1](https://github.com/derekbreden/homesodamachine/commit/5c5ad1e1) with the red gate stated in the message — you're right that a rollback is cheaper than the hesitation.

Two things worth flagging while the protected build runs:

**The pre-commit hook caught the staleness I'd missed:**
```
pre-commit: enclosure scorecard sidecar may be behind _contents.py — rebuild
```
That's the guard for exactly the mistake I made twice — reading a scorecard written at 20:23 against source edited at 20:42. It warns rather than blocks, so the commit went through, and the protected rebuild will bring the sidecar current.

**There are ~60 untracked files in `hardware/assembly/cards/`** — assembly step cards (`ip-02-water-path.html`, `es-01..07` for the electronics shelf, `rl-01..06` for the refrigerant loop) plus a `cards/img/` tree. They're not mine, but one of them is `img/tap-point.png`, so whatever generates them has already picked up the assembly I added today. That directory is tracked at [60918b9a](https://github.com/derekbreden/homesodamachine/commit/60918b9a), so these are new output sitting alongside committed siblings.

I've left them alone — not out of caution about committing, but because I haven't read 60 files I didn't write, and several describe an electronics shelf I just unplaced. Want me to review and commit them, or is that a generator you'd rather re-run yourself once the deck settles?

---

# User

---

<task-notification>
<task-id>bkl8xir2o</task-id>
<tool-use-id>toolu_01WvtJVnEf7Ute7rcJk39bQo</tool-use-id>
<output-file>/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/cf7ffd7d-2017-4caf-9a49-23e90eb4a417/tasks/bkl8xir2o.output</output-file>
<status>completed</status>
<summary>Background command "Protected clean build of enclosure assembly" completed (exit code 0)</summary>
</task-notification>

---

# Assistant

---

The build completed and printed the full scorecard, but the sidecar mtime never moved. Let me see whether it actually wrote:

---

# Assistant

---

Now the behavior makes sense and it's deliberate: [enclosure_assembly.py:319](hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py:319) hard-exits on a failing gate *before* writing anything, so a headless build never writes an invalid pack. The sidecar on disk is the last valid one. So I can't refresh artifacts until the pack closes.

Let me test a layout with the probe before spending more builds on it:

---

# Assistant

---

Probe says my candidate ASSE, tee and pan positions are all CLEAR — but the pump still fails, and for a reason I hadn't understood:

```
PUMP -> fluid-28  2873.8 mm³  x[191.87, 255.00] y[301.02, 338.00] z[289.27, 295.63]
        fluid-18  1451.9 mm³  x[221.77, 255.00] y[316.02, 338.00] z[289.27, 295.63]
```

The two flavor runs don't just climb the east wall pocket — they **turn aft and cross the back of the bay at z ≈ 292** to reach their bulkheads, which sit at x 195 and 225 while the lanes are at x 262 and 274. That westward jog puts them straight through the pump's volume. And the pump is 74 mm tall in a 78 mm bay, so nothing passes over or under it.

That constrains the pump in **Y** as well as X: usable depth between the CO2 column (y 217.8) and the runs' aft crossing (y 301) is **83 mm**, and the pump is 98 deep. It doesn't fit in either axis while those runs jog west.

---

# Assistant

---

Reported to the packing agent. While it works, one thing I found in the build machinery that you should know about, because it's how my last commit got through:

[enclosure_assembly.py:317](hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py:317) says of a failing pack — *"the sidecar records the failing verdict (gatesPass=false). The pre-commit gate reads that sidecar and blocks the commit — an invalid pack can be inspected but can never land."*

That holds under `HSM_EDITOR`. Headless it doesn't: line 319 exits *before* the write, so the sidecar keeps the **last valid** verdict — `gatesPass: true`, describing a pack that no longer exists. The pre-commit hook then reads a passing sidecar and only emits a soft warning (`sidecar may be behind _contents.py`), so the commit lands. That's exactly what happened with `5c5ad1e1`, and it's also what made me misreport the gates twice — I was reading a scorecard from 20:23 against source edited at 20:42.

---

# Assistant

---

While the agent searches, I worked the arithmetic myself and want to flag what it says, because it constrains the answer hard.

The pump takes the bay's full height (74 of 78.32), so **any run that crosses its plan crosses its volume** — nothing goes over or under. That means the flavor runs and the pump must occupy disjoint X regions, and the tap point's 86 mm branch reach has to fit in whatever L-shaped remainder is left.

The pump is 188 × 98 in a 283 × 160 bay. Push it to a corner and the remainder is a 95-wide strip on one side plus a ~62-deep strip on the other. The tap point needs 86 in one horizontal axis and 56 in the other, so **only the 95-wide strip can take it** — the 62-deep strip can't. That pins the pump to one end of the bay and everything else to the other.

Pump east (x 95→283) puts it on the flavor lanes. Pump west (x 0→188) leaves a 95-wide east strip that could hold the tap point *and* the flavor runs *and* their bulkheads — the direction I'd bet on, but it needs the ASSE and the water bulkhead rehomed too, and the C14 I just moved west sits at y[360,398], behind the bay, so it survives either way.

Committed so far, all pushed:

| commit | what |
|---|---|
| [71fa356c](https://github.com/derekbreden/homesodamachine/commit/71fa356c) | the three fittings + the tap-point stack |
| [af639af1](https://github.com/derekbreden/homesodamachine/commit/af639af1) | vent-stub datum fix + the palette that made your two "missing" parts visible |
| [5c5ad1e1](https://github.com/derekbreden/homesodamachine/commit/5c5ad1e1) | electronics out, C14 west, pump provisionally placed — tube-clash gate red, stated in the message |

Your original ask is done and shipped: all five parts modeled and visible in 3D. What's open is where the tap point *sits*, and that turned out to be gated on a packing problem the parts themselves exposed.

---

# User

---

<task-notification>
<task-id>a83a553d610287ddc</task-id>
<tool-use-id>toolu_011UhD9PM8h2fBzD2qfzwA3Y</tool-use-id>
<output-file>/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/cf7ffd7d-2017-4caf-9a49-23e90eb4a417/tasks/a83a553d610287ddc.output</output-file>
<status>completed</status>
<summary>Agent "Pack the water deck" finished</summary>
<note>A task-notification fires each time this agent stops with no live background children of its own. The user can send it another message and resume it, so the same task-id may notify more than once.</note>
<result>`probe.py selftest` → **PASS** (48 bodies, 20 routed runs). Every number below is from a query I ran against the placed world.

## Answer to your question: **yes, the deck fits. The box does not have to grow.**

The trick is that **the pump parks WEST, not east**, and the bay is deeper than either of us was treating it.

**The bay is 184 mm deep, not 160.** `_dims().inner` gives y1 = 384; the rear-panel bodies only reach inboard at their own x stations (bulkhead barrels y ≥ 362.21, C14 y ≥ 360). Shell-wise, `x[0,283] y[200,384] z[253.4,331.7195]` is clear except two ledges:
- `front-top` seam ledge, **y[220.3, 236.4] z[328.72, 331.70]**, full width — the bay ceiling drops to 328.72 there.
- `back-bottom` rear Z-lip, **y[381,384] z[264,280.1]**, full width.

Nothing intrudes inboard of x = 0 or x = 283 at bay height.

**Why west works.** `fluid-18`/`fluid-28` jog west only as far as their flavor bulkheads — x 224.95 and **195.05**. A pump whose east end stops short of 191 never meets them:

```
probe: gap seaflo fluid-28 = 9.2373     gap seaflo fluid-18 = 36.99
```

## 1. Committed coordinates

```python
# SeaFlo 22-series — yawed 180° about Z: ports EAST, suction AFT, discharge FORWARD.
# Base flat on the foam cap (NOT foam_top + STACK_GAP — see §7).
SEAFLO_YAW = 180.0
SEAFLO_POS = (92.0, 277.0, 253.4)
placed["seaflo-pump"] = _rot(_load(SEAFLO_STEP), (0, 0, 1), SEAFLO_YAW).translate(SEAFLO_POS)
#   box x[3.00, 191.00] y[228.00, 326.00] z[253.40, 327.40]
#   suction   (191, 297, 286.4) x+     discharge (191, 257, 286.4) x+

# ASSE 1022 chain — flow +X, vent native −Z (roll 0), lying along X in the aft strip.
ASSE1022_POS  = (102.0, 345.5, 287.0)
ASSE1022_YAW  = 0.0
ASSE1022_ROLL = 0.0
placed["asse1022-assembly"] = _rot(_rot(
    _load(ASSE1022_STEP), (0,0,1), ASSE1022_YAW), (1,0,0), ASSE1022_ROLL).translate(ASSE1022_POS)
#   box x[66.00, 189.50] y[329.00, 362.00] z[285.00, 328.29]
#   tube_in (66, 345.5, 314) x−   hose_out (189.5, 345.5, 314) x+   vent_tip (134, 345.5, 285) z−

# Tap point — run VERTICAL is not needed; run along Y, branch horizontal −X.
# ROLL FIRST, then yaw (the pump's own order, not the ASSE's):
TAP_POINT_ROLL, TAP_POINT_YAW = -90.0, 90.0
TAP_POINT_POS = (274.5, 277.0, 270.0)
placed["tap-point-assembly"] = _rot(_rot(
    _load(TAP_POINT_STEP), (1,0,0), TAP_POINT_ROLL), (0,0,1), TAP_POINT_YAW).translate(TAP_POINT_POS)
#   box x[194.21, 279.96] y[248.94, 305.06] z[257.16, 282.84]
#   hose_a (274.5, 248.935, 270) y−   hose_b (274.5, 305.065, 270) y+
#   tube_out (194.21, 277.0, 270) x−  (collet faces WEST into the 13 mm channel off the pump)

DRIP_PAN = dict(x=(99.0, 169.0), y=(328.0, 378.0), z=(253.4, 273.4))   # 70 × 50 × 20, on the cap

WATER_BACK_X = 56.0
WATER_BACK_Z = 300.0
# C14_BACK_X = 22.0, C14_BACK_Z = 295.0 unchanged. UMBILICAL_X = 210.0 unchanged.
```

Plus one free change to `_lines.py`: slide the two flavor runs' west jogs aft. **A rectilinear L costs the same length wherever the corner sits**, so this is free:

```python
("fluid-18", "elbow-noz-a", "bulkhead-flavor-a", outer_x, 12.0),   # was 40.0 → jog at y 347.2
("fluid-28", "elbow-noz-b", "bulkhead-flavor-b", outer_x - (od+LANE_CLEAR), 20.0),  # was 55.0 → y 339.2
```

## 2. Probe verification — every body CLEAR, exact solid distances

| body | nearest bodies (mm) | nearest shell piece |
|---|---|---|
| `seaflo` | `foam-assembly` 0.0 (seats on the cap), `drip-pan` 2.0, `fluid-28` **9.24**, `asse` 12.0 | `back-bottom` 3.0, `front-top` 3.0, `back-top` **4.3195** |
| `asse` | `drip-pan` 11.6, `seaflo` 12.0, `bulkhead-water` 13.80, `fluid-28` 14.50, `bulkhead-flavor-b` 18.85 | `back-top` 3.43 |
| `tap-point` | `foam-assembly` 3.765, `discharge` 7.74, `fluid-28` 9.25, `fluid-18` 12.48, `seaflo` 14.39 | `back-bottom` 3.768 |
| `drip-pan` | `foam-assembly` 0.0 (sits on cap), `seaflo` 2.0, `asse` 11.6 | `back-bottom` 3.0 |
| `flow-regulator` (Ø20 × 60 at x[196,256] y 192 z 272) | `fluid-28` 8.97, `nozzle-gate-assembly` 9.20, `foam-assembly` 10.25 | — |

`W.hits()` on every candidate returns nothing. Queries are in `/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/cf7ffd7d-2017-4caf-9a49-23e90eb4a417/scratchpad/s12.py`.

## 3. The vent fall

```
W.cast((134.0, 345.5, 285.0), (0,0,-1), dia=25.0, limit=60, skip=("asse",))
  → Ø25 runs 11.60 mm, stopped by drip-pan   end (134.00, 345.50, 273.40)
same with drip-pan skipped
  → Ø25 runs 31.60 mm, stopped by foam-assembly  end (134.00, 345.50, 253.40)
```
Vent tip (134, 345.5, 285) → 31.6 mm of clear air to the cap, 11.6 mm to a 20 mm-tall pan, Ø25 wide. Nothing between.

## 4. The 1/4" branch corridor to V-A-I — **CLEAR**

```
tube_out(194.21,277,270) → (189,277,270) → (185.5,271,270) → (185.5,192,272)
 → (271.33,192,272) → (271.33,172.28,272) → (271.33,172.28,198.66)   [V-A-I]
W.hits(corridor(..., dia=6.35)) → CLEAR
nearest: seaflo 7.325, nozzle-gate-assembly 11.468, discharge-run 12.166, foam-assembly 13.425
```
The regulator rides the long east leg at y = 192. The vertical drop onto V-A-I was pre-checked: `cast((271.329,172.275,199),(0,0,1),dia=10)` runs 90.27 mm before `fluid-18` — the whole column is open below the lane.

## 5. The two 3/8" hose legs (Ø12.7 = JoyTube 3/8" ID × 1/2" OD) — **both CLEAR**

**ASSE → tee** (drops below the nozzle deck first, then runs east under it):
```
(189.5,345.5,314) → (240,345.5,314) → (240,322,310) → (240,318,272) → (274.5,318,270) → hose_b
CLEAR;  nearest fluid-28 9.418, foam 10.250, bulkhead-carb 10.360, fluid-18 12.005
```
**tee → pump suction** (climbs over the tee's own branch bar, then west into the barb):
```
hose_a → (274.5,222,270) → (256,213,274) → (240,220,292) → (240,264,306) → (232,290,298)
       → (216,297,286.4) → suction(191,297,286.4)
CLEAR;  nearest flow-regulator 4.745, fluid-28 7.352, foam 10.250; shell back-bottom 2.15
```
Tightest bend on either leg is **R ≈ 25 mm (2.0 × OD)**; most corners are R 30–40. The straight over each barb is ≥ 25 mm.

## 6. Plan occupancy and what survives

```
bay envelope x[0,283] y[200,384] z[253.4,331.72] = 4078 cm³
occupied 65.9%   free 34.1% (1391 cm³)
PLAN occupancy 85.7% (448 cm² of 523 cm²)
```

Largest contiguous free boxes:

| cm³ | shape | where |
|---|---|---|
| 277.6 | 134 × 28 × 74 | x[0,134] y[200,228] z[253.4,327.4] |
| 180.9 | 190 × 28 × 34 | x[0,190] y[200,228] z[293.4,327.4] |
| 158.8 | 98 × 54 × 30 | x[0,98] y[326,380] z[253.4,283.4] |
| 134.0 | 92 × 104 × 14 | x[192,284] y[200,304] z[313.4,327.4] |

**Tell him this plainly: the electronics cannot come back into this bay.** Their envelopes are `power-assembly` 151.1 × 73.9 × 40.5, `pcba-assembly` 90.8 × 73.3 × 27.1, `dc-dist-block` 50 × 26 × 18. The deepest free run anywhere is 28 mm (front strip) or 54 mm (aft-west). Even the DC block (26 deep) only fits the aft-west pocket. The survivors are **slabs, not blocks** — cable lanes and small-fitting real estate, nothing more.

## 7. What I could not close

1. **Pump isolation mounts have no height.** With the base flat on the cap the ceiling gap is **4.3195 mm**. At `foam_top + STACK_GAP` (255.9) it is 1.8195, and it **clashes the `front-top` seam ledge by 1.18 mm** whenever ymin &lt; 236.4. So the 2.5 mm of grommet has to come out of the foam cap (a recessed cradle), not from under the base. This is the one number that would justify growing the box: **+10 mm in Z buys a conventional isolation mount and lets the tap point's branch stand vertical** (85.75 vs 78.3195 — short by 7.43, or 17.43 with 5 mm top and bottom).
2. **The carb riser is not lane'd.** A Ø25.4 insulated line cannot cross the bay at x = 141.5 at any height — `cast((141.5,200,z),(0,1,0),dia=25.4)` runs 37.00 mm and stops on the pump at z = 300, 310 and 318.3 alike. One lane does survive: **x ≈ 265, z ≈ 318.3 runs the full 190 mm aft with no contact.** But it cannot get there up the foam's front face — `cast((210,196,50),(0,0,1),dia=25.4)` is stopped immediately by `foam-assembly`, because a Ø25.4 tube centred at y = 196 already overlaps the core's front face. The riser needs its insulation broken, a dedicated front-column channel, or a smaller wall.
3. **`water-3` (discharge → `foam-assembly.water-in`) is sketched, not solved.** My corridor `discharge(191,257,286.4) → (232,257,286.4) → (243,250,276) → (247,215,264) → (190,206,256) → (150,200,243) → (141.5,194,232) → (141.5,194,223) → (141.5,200,223)` probes CLEAR in the bay, but the last two legs pass through the bag-fall corridor at y ≈ 194, where `fluid-15`/`fluid-25` live — that part belongs to whoever authors the segment. **Endpoints for `BLOCKED`:** `water-2` closes on `asse1022-assembly.hose-out (189.5, 345.5, 314) x+` → tap `hose_b (274.5, 305.065, 270) y+`, and tap `hose_a (274.5, 248.935, 270) y−` → `seaflo-pump.suction (191, 297, 286.4) x+`. `water-3` closes on `seaflo-pump.discharge (191, 257, 286.4) x+` → `foam-assembly.water-in (141.5, 200, 223) y−`, with the MAACFLOW → GASHER → PP010822E stack taking the first ~60 mm straight east off the barb.
4. **`WATER_BACK_Z = 300` is untested against the printed pieces.** I moved it off 293 because of your `back-top` finding, but I did not rebuild the back panel with the port at 300 — do that before committing it.</result>
<usage><subagent_tokens>387151</subagent_tokens><tool_uses>50</tool_uses><duration_ms>3882750</duration_ms></usage>
</task-notification>

---

# Assistant

---

The agent solved it — and the key was a fact I had wrong: **the bay is 184 mm deep, not 160.** The rear-panel bodies only reach inboard at their own x stations, not across the full width. With that, the pump parks **west** with its ports facing east, and everything closes. Let me apply it.

---

# Assistant

---

The hook is right that those are computed dimensions that will drift. Rewriting to lean on the geometry rather than restating it:

---

# Assistant

---

That's a direct hit, and the material is worth having read. What I wrote was residue in three separate ways: it justified the position, defended it against `STACK_GAP`, and presented a complete-feeling reason ("so the nozzle runs never meet it") that a later reader would absorb as *the* design driver and stop looking. Rewriting as description:

---

# Assistant

---

Having read that, the same residue is in several things I wrote earlier today. Cleaning them rather than leaving them in your backlog:

---

# Assistant

---

Now the ASSE and the tap point. Let me replace the old placement block:

---

# Assistant

---

A drip pan part already exists. Let me check its size and whether it's placed:

---

# Assistant

---

The real drip pan is **130 × 66 × 22**, not the 70 × 50 the agent assumed — and the aft strip behind the pump is only 58 deep, so it doesn't fit there. The pan is still deferred in the scorecard, so I'll leave it unplaced and flag that rather than invent a footprint:

---

# Assistant

---

`water-1` was authored for the old pose. Let me re-author it for the new inlet:

---

# Assistant

---

The scorecard's PORTS table hardcodes the bulkhead at the *old* `(145.0, …, 293.0)` as literals instead of deriving from the constants. Let me see how widespread that is:

---

# Assistant

---

All five rear-panel ports hardcode x and z as literals — so the C14 port is stale too, at the old x = 90. Let me make them derive from the constants instead of duplicating them:

---

# Assistant

---

Port stations now derive correctly. The remaining failure is geometric — 13.7 mm of Y travel can't hold two R5 bends. Simplest fix is to put the bulkhead at the inlet's own height so the run needs one corner, not two:

---

# Assistant

---

One clash left. Let me find exactly what the water bulkhead is hitting at x = 56:

---

# Assistant

---

Three failures, not one. Let me read the contacts declaration and fix them together:

---

# Assistant

---

**All 7 gates pass.** The pump, the ASSE chain, and the tap point are placed and the pack closes. Let me verify where things actually landed:

---

# Assistant

---

Everything landed where the agent specified. `water-1` collapsed from an 80.6 mm 4-bend pigtail to a short single corner. Let me do the clean build (clearances measured) and commit:

---

# Assistant

---

While that builds, let me fix the prose that still describes the old layout:

---

# Assistant

---

Clean build finished. Now the routing — the tap point splits `water-2` into two segments. Let me look at how the ASSE's terminals reach world coordinates so I can do the same for the tee:

---

# Assistant

---

All six terminals match the agent's coordinates exactly. Now the ports and the runs:

---

# Assistant

---

Both match the agent's coordinates. Now the segments and the runs:

---

# Assistant

---

Now authoring the two hose legs:

---

# Assistant

---

A fold — the tee's forward leg and the suction are on opposite sides in Y, and the 16.4 mm height difference can't hold two R20 bends. Cleanest fix is to stand the tee at the suction's own height. Let me check that it still clears:

---

# Assistant

---

The 16.4 mm height difference can't hold two bends in any rectilinear path. Standing the tee at the suction's own height removes that leg entirely:

---

# Assistant

---

The tee at 286.4 runs into the flavor lanes. Standing it at the ASSE's own barb height instead clears them and removes `water-2`'s z-leg:

---

# Assistant

---

**All 7 gates pass, and the water path is now closed** from the rear bulkhead through the backflow preventer and the tap point to the pump's suction. Clean build then commit:

---

# Assistant

---

Clean build with clearances measured. Let me commit:

---

# Assistant

---

A lot of files I never touched are modified — cold-core sources, assembly docs, foam shell. That's not my work; something else is editing the tree. Let me unstage and commit only my own files:

---

# Assistant

---

Another session committed `91516c83` and is actively editing cold-core files. Staging only mine:

---

# Assistant

---

Pushed as [d343dcb8](https://github.com/derekbreden/homesodamachine/commit/d343dcb8). And the other session committed the cards deck ([3ad86a10](https://github.com/derekbreden/homesodamachine/commit/3ad86a10)) plus a build-lock fix for exactly the contention I was fighting — good thing I left those alone.

---

# Assistant

---

The full-cabinet view is too dense to read. Let me render just the water deck so you can actually see it:

---

# Assistant

---

The thumbnail renderer only resolves paths inside the repo. Rather than churn artifacts, let me draw you the plan view directly.

---

# Assistant

---

Right — and I'd already encoded it: commit `5c5ad1e1` names its own red gate in the message. That commit is the example; a memory file would just be a worse copy of it.

---

**Done.** All five parts you listed are in the model, and the tap point is placed and plumbed.

**On the two you thought were missing** — the GAGIRA coupling and the PP010822E were always in `build()`. They were rendering invisible: black PP at **1.18:1** against the viewer's `#1a1a2e` ground (below the ground's own luminance — it drew as a hole), and the coupling sharing stainless with the barb at **1.51:1** against the brass, so two hexes read as one nut cluster. Fixed in the palette.

**On the three that genuinely didn't exist** — modeled from manufacturer data, not guesses. The tee's dimensions came off the **Thogus TT3666** drawing, read out of the PDF's vector content stream at the sheet's 3:2 scale. The John Guest internals are JG's own published cavity table. The weakest number in the set is the PP061208W's outer profile (photogrammetry, ±4% axial) — you have a bag of ten, and calipers on its overall length would settle it.

**The layout.** Your "remove the electronics" call was what unlocked it. The pump has exactly one pose that fits, and it takes the bay's full height, so nothing shares its column — every line crossing its plan crosses its volume. It parks west; the chain runs the aft strip behind it; the tap point stands east at the chain's own barb height. `water-1` went from an 80.6 mm four-bend pigtail to **21.6 mm and one bend**.

**Three things worth knowing:**

1. **The tap point's branch cannot stand vertical.** It's 85.75 mm tall; the bay is 78.32. Horizontal isn't a preference, it's the only pose available — and that constraint is what killed several otherwise-reasonable layouts.
2. **The rear-panel port table had drifted.** It still carried the water bulkhead at x 145 and the C14 at x 90 after both had moved, because each station was written as a literal in three places. Now read once off the hole the wall is cut for.
3. **The drip pan has no station.** The real part is 130 × 66; the strip behind the pump is 58 deep. It doesn't fit there, so I left it unplaced rather than invent a footprint. Since the pan is the whole reason the vent has a pose, that's worth resolving before the deck sets.

Still open: `water-4` (discharge → carbonator) blocked on the MAACFLOW and GASHER check, and the branch run to V-A waiting on the flow regulator, which has never been placed anywhere.

One caution — another session is actively editing this tree (it landed `91516c83` and the 87-card deck mid-work). I committed only my own files; the cold-core and assembly-doc changes in your working tree are theirs.
