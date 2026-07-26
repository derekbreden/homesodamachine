---

# User

---

<command-message>relay</command-message>
<command-name>/relay</command-name>
<command-args>PCBA placement 2

I'd like you to spawn some agents to consider more broadly the many possible arrangements we might consider here, the things which may fit against each other according to their shapes in ways that this agent has not considered.

I'd like you to consider carefully the "fences" you put up regarding the search space you use, and the levers of freedom you use within that search space. I think this problem is too big for one agent, and so I expect you to spawn help for yourself.

Thanks.</command-args>

---

# User

---

Relay the contents of another of the user's Claude Code sessions INTO this one. You do it locally: render that session's clean transcript with our shared exporter and read it into context. There is NO cross-session messaging here — you never write to or notify the other session, you just read its transcript off disk.

Session to pull in: **PCBA placement 2

I'd like you to spawn some agents to consider more broadly the many possible arrangements we might consider here, the things which may fit against each other according to their shapes in ways that this agent has not considered.

I'd like you to consider carefully the "fences" you put up regarding the search space you use, and the levers of freedom you use within that search space. I think this problem is too big for one agent, and so I expect you to spawn help for yourself.

Thanks.**

Steps:

1. **Find it.** Run:
   `python3 ~/Developer/claude-code-setup/jsonl2md/jsonl2md.py list-sessions`
   Match PCBA placement 2

I'd like you to spawn some agents to consider more broadly the many possible arrangements we might consider here, the things which may fit against each other according to their shapes in ways that this agent has not considered.

I'd like you to consider carefully the "fences" you put up regarding the search space you use, and the levers of freedom you use within that search space. I think this problem is too big for one agent, and so I expect you to spawn help for yourself.

Thanks. to exactly one title. If it's ambiguous or not listed, show the candidates and ask which — never guess. It's the source, so it must not be this current session. (Add `--cwd <path>` if the session lives in a different project.)

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

I'll find that session first.

---

# Assistant

---

Matched exactly one: **PCBA placement 2**. Exporting it.

---

# Assistant

---

Relayed in — and that session had itself relayed in "PCBA placement", so I have the whole arc.

**Where it left off:** the east re-lay landed (`7dd27fd8`, 7/7 gates) — SeaFlo pushed to x[96,283], V-K turned to run *down* the strip, split tucked under its cradle, flavor run moved into the under-pump lane. That opened a **107.7 × 147.6 × 77.3 mm** void west of the pump. Then it measured the electronics into that void and concluded two-level is forced, blaming the **power tray's 151 mm width** (a wide-shallow row built for a bay that no longer exists), and declared its next move: re-lay `power-tray/` into the column.

That last conclusion is exactly the kind of thing worth re-opening before anyone commits to it — it fixed a fence ("tray keeps its wide-shallow topology, PCBA goes on a bridge above") and then optimized inside it. Let me get hard ground truth before I brief anyone.

---

# Assistant

---

Now let me get hard ground truth on the actual free space, rather than trusting the prior session's summary numbers.

---

# Assistant

---

Now the parts and the cavity. Let me get real dimensions rather than the summary's.

---

# Assistant

---

Real envelopes, which reframe the problem:

| part | envelope (mm) |
|---|---|
| power-assembly **as built** | 151.10 × 73.94 × 40.50 |
| — Mean Well IRM-90 alone | 52.00 × 109.00 × 33.50 |
| — Teyleten relay | 70 × 17 × 19 |
| — Wago 221-413 ×3 | 18.8 × 18.6 × 8.4 |
| — ground ring stack | 18 × 17.7 × 14.6 |
| pcba-assembly | 90.82 × 73.30 × 27.10 |

The 151 mm is 4 loosely-related objects holding hands. Let me capture the tool surface before I brief anyone.

---

# Assistant

---

Now the briefing. I'll write the shared ground truth once so each agent reads the same facts rather than my paraphrase of them.

---

# Assistant

---

Four agents, each assigned a **different fence to break** — so they don't duplicate each other's search.

---

# Assistant

---

Dispatched. While they run, here's the frame I built for them — and one thing I verified that changes the problem.

## What I checked before briefing anyone

**The electronics were never placed at all.** `POWER_ASSEMBLY` and `PCBA_ASSEMBLY` are declared at [_contents.py:194](hardware/printed-parts/enclosure/enclosure-assembly/_contents.py:194) and never seated with `_at`. And [scorecard.py:696](hardware/printed-parts/enclosure/enclosure-assembly/scorecard.py:696) still carries a full J1–J14 port table mapped to world by `(x+258.8, y+228.8)`, z=292.5 — putting the board at roughly x[190.8, 275.8] y[192.5, 265.3]. The pump now occupies x[96,283] y[200,298]. **That port table points into the middle of the SeaFlo.** It's a fossil of a pose that predates two re-lays, and it's been quietly sitting in the scorecard.

So this isn't "place a part in the void that opened." It's "the world has moved twice under a placement that was never made."

## The fences

The prior session's closing move was: *the blocker is the tray, not the parts — re-lay `power-tray/` into the column.* That's a real insight arrived at from inside four walls it never tested:

| # | fence held fixed | never tested |
|---|---|---|
| A | electronics live **on the foam cap, west of the pump** | the entire east re-lay was *justified* by this |
| B | both trays lie **flat, board-up, on a horizontal plane** | fixes footprint at its worst case |
| C | the power tray is **one part** carrying PSU + relay + 3 Wagos + ground stack | 151 mm is a `Layout` consequence, not a spec |
| D | the **pump's pose is final** | moved twice already, by this same reasoning |

C is the sharp one. Those four objects have unrelated endpoints — the Wagos want the C14 inlet at the **rear-west corner** (x[6.75,37.25] y[360,398]), the ground stack wants the earth bond the scorecard puts at the **compressor shroud, front floor** (192, 31.5, 78). They're bolted to one plate in the back because they were tidy, and the plate's width is now driving a two-level stack.

## The levers

Volume inventory (all strata, not just the cap) · tray topology and decomposition · body orientation · mounting mode (tray / wall-hung / ceiling-hung / edge-standing / bridge) · component-level vs. assembly-level placement · re-posing the water deck again · and — pending Agent 4 — whether the board outline is even frozen.

## The four agents

Each owns a different fence so they don't converge on the same answer:

1. **Volume census** — sweeps `fit.slab` across every Z band in the whole cavity with `--exact` on the hollow bodies, ignoring the cap's privilege. Breaks A.
2. **Decomposition** — reads the harness docs and re-derives where each of the five components individually wants to live. Breaks C.
3. **Pose & mounting mode** — the orientation × mounting-mode matrix, with connector-exit and thermal constraints. Breaks B.
4. **Constraint archaeology** — adjudicates every constraint as hard / soft / **fossil** / unsupported. Includes the two that could reframe everything: is the PCBA outline actually frozen, and is there any stated rule against a water line running above a live board.

All four are read-only and instructed to quote the query behind every number, per `CLAUDE.md`. I'll synthesize when they report — particularly watching for where the census and the archaeologist disagree, since a volume that's free only because a constraint is a fossil is the most interesting kind.

---

# User

---

<command-message>relay</command-message>
<command-name>/relay</command-name>
<command-args>PCBA placement

I hope my idea about the mounting bosses and everything for the tray being printed on the top of the foam shell (or enclosure walls) was carried forward, and you are not stuck on "we need to land a full existing designed tray in here somewhere".</command-args>

---

# User

---

Relay the contents of another of the user's Claude Code sessions INTO this one. You do it locally: render that session's clean transcript with our shared exporter and read it into context. There is NO cross-session messaging here — you never write to or notify the other session, you just read its transcript off disk.

Session to pull in: **PCBA placement

I hope my idea about the mounting bosses and everything for the tray being printed on the top of the foam shell (or enclosure walls) was carried forward, and you are not stuck on "we need to land a full existing designed tray in here somewhere".**

Steps:

1. **Find it.** Run:
   `python3 ~/Developer/claude-code-setup/jsonl2md/jsonl2md.py list-sessions`
   Match PCBA placement

I hope my idea about the mounting bosses and everything for the tray being printed on the top of the foam shell (or enclosure walls) was carried forward, and you are not stuck on "we need to land a full existing designed tray in here somewhere". to exactly one title. If it's ambiguous or not listed, show the candidates and ask which — never guess. It's the source, so it must not be this current session. (Add `--cwd <path>` if the session lives in a different project.)

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

Important steer — and it lands while the agents are still running, so let me redirect them first.

---

# Assistant

---

This one is the origin of the whole line of work — and it contains two traps my agents could fall into. Sending those now.

---

# Assistant

---

Straight answer: **it was carried, then it was dropped, and I had only half-recovered it.**

Session 1 held your idea properly. After you pushed back twice it measured the real parts instead of the tray boxes, found the Mean Well is 52 × 109 × 33.5 (not the tray's 151 × 74 × 40.5) and the PCBA is **27% fill**, and verified a two-level arrangement against solids. It ended by telling you your idea works as stated — *"the PSU's bosses are short, the board's are tall posts standing beside the PSU rather than on it. What can't be reused is the current 8 mm PCBA tray: its floor cuts straight through the PSU."*

Session 2 lost it. Its closing line was *"that re-layout of `power-tray/` is what I'm doing next"* — the tray back as the object.

And my own fence list an hour ago said the power tray is *one part carrying four things* — i.e. I was proposing to **decompose** the tray when you'd already said to **delete** it. That's the same error one notch shallower. Corrected: I've messaged all three geometry agents to stop asking "where does a 90.82 × 73.30 rectangle fit" and start asking "where can four coplanar boss tops be rooted, with clear air for the rest." For the PCBA that's four bosses on a **78.0 × 66.3 mm** rectangle ([pcba_tray.py:40](hardware/printed-parts/electronics/pcba-tray/pcba_tray.py:40)) and the board free to overhang, bridge, or cantilever past whatever carries them — plus wall-rooted bosses as horizontal studs.

Two things the relay gave me that are worth more than the orientation:

**A measurement trap that would have corrupted every geometry answer.** `fit.py try` at default clearance records **bounding-box** gaps, not solid distances — session 1 read 0.63 mm to a tube run, nearly redesigned around it, and the exact `probe gap` was **58.2 mm**. Long diagonal tube runs have boxes that are mostly air. All three agents now have that warning.

**An unmodeled keep-out sitting on your mounting surface.** [_contents.py:54](hardware/printed-parts/enclosure/enclosure-assembly/_contents.py:54) declares a CO2 entry down through the foam-cap top at **(141.5, 199.8)**. It isn't modeled — probing that column finds only cap slab. So no clearance check defends it, and an agent surveying the cap would mount straight through it. Session 1 also found it's probably *removable*: the foam's front face already carries a shared slot at world x=141.5 for the evaporator stubs, water inlet and PRV vent. I've handed that to the constraint agent and asked it to sweep for **other** declared-but-unmodeled keep-outs, since that's the class of thing the other three will walk through unseeing.

One caveat on reusing session 1's verified arrangement: those numbers predate the east re-lay and the 5 mm `RING_SEAT` rise. It solved against a **55.5–96 mm** west column; the column is now **107.7 × 147.6 × 77.3**. The conclusion "side-by-side is impossible" was true at 96 mm and needs re-deriving at 107.7 — bare arithmetic still says no (52 + 73.3 = 125.3 across, 109 + 90.8 = 199.8 deep), but that's box arithmetic, which is exactly the reasoning you've twice had to correct.

Agents still running; I'll synthesize when they land.

---

# User

---

<task-notification>
<task-id>ab9d15cf4defaab20</task-id>
<tool-use-id>toolu_01QZbXRQgRuPXkHSP8joT86Q</tool-use-id>
<output-file>/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/f6d55805-50ea-4d28-8cc7-57bec2421b42/tasks/ab9d15cf4defaab20.output</output-file>
<status>completed</status>
<summary>Agent "Constraint archaeology" finished</summary>
<note>A task-notification fires each time this agent stops with no live background children of its own. The user can send it another message and resume it, so the same task-id may notify more than once.</note>
<result>I've finished the audit. Here are the verdicts, every one settled against the geometry or a cited file.

## Verdict table

| # | Constraint | Verdict | Evidence |
|---|---|---|---|
| 1 | PCBA outline 85.05 × 72.85 is frozen | **HARD** | `/hardware/ledger/purchases.md:279` — JLCPCB order **W2026071513250534**, placed 2026-07-15, **$702.00 paid**, 10 boards, status `ON-ORDER (in file review)`. `/hardware/pcb/pcba/order.md:86-94` "As ordered — first assembled batch". The tray copies the outline verbatim: `/hardware/printed-parts/electronics/pcba-tray/pcba_tray.py:37-39` hard-codes `_outline_x=(-68,17)`, `_outline_y=(-36.3,36.5)`, `_holes_pcb=((-64.5,33),(13.5,33),(13.5,-33.3),(-64.5,-33.3))`. |
| 2 | The `(x+258.8, y+228.8)`, z=292.5 PCBA port table | **FOSSIL** | `/hardware/printed-parts/enclosure/enclosure-assembly/scorecard.py:694-711`. `probe.py hits --x 190.8,275.8 --y 192.5,265.3 --z 285,293` → `seaflo-pump 29934.8 mm³`, plus `water-6`, `flow-regulator`, `fluid-28`. The volume is occupied. |
| 2b | The `power-tray` port table (`scorecard.py:720-723`) | **FOSSIL** | `probe.py hits --x 30,175 --y 212,286 --z 258.4,290` → `seaflo-pump 120934.3 mm³`. Same fate; nobody has flagged this one. |
| 3 | `asse1022-assembly` `clear power-tray 8.0` | **HARD (and firing)** | `scorecard.py:414-418`: `present and gap &gt;= mn`, so an absent neighbour fails by design. Sidecar `placed` detail: `✗ asse1022-assembly: … clear power-tray inf(&lt;8)`. It is **the only failing placement rule in the pack** — 16/17 rule-carrying components hold. |
| 4 | "No water line above the electronics" | **UNSUPPORTED — the repo says the opposite** | `_lines.py:461-482` deliberately routes `fluid-18/28` *over* "the electronics shelf's board" with a `LANE_CLEAR = 5.65` allowance. The only soak language anywhere is `/hardware/printed-parts/enclosure/README.md:29`: PRV vent "on the warm side where a relief event won't soak anything important" — prose, no check, no keep-out solid. No creepage, IPX, drip or condensation rule exists in `hardware/assembly/`, `scorecard.py`, or `_lines.py`. |
| 5 | Single-point earth at the shelf | **HARD** | `/hardware/wiring/ac-wiring-schedule.md:115,120`: "Single-point chassis ground at the electronics shelf… gives the appliance Class I status". `/hardware/assembly/wiring.md:29-42`. |
| 5b | AC/LV spatial segregation | **UNSUPPORTED** | `/hardware/assembly/wiring.md:5`: "A single zip-tied bundle exiting the electronics shelf carries 16 AWG mains, 12 V power, and 22 AWG signal **in close proximity**." Segregation is stated as *absent*, not required. The only mains-placement rule is relay #1 outside the shroud (`ac-wiring-schedule.md:22`). |
| 6 | "The electronics shelf" | **SOFT — prose, not a region or a part** | Not in `COMPONENTS` (`scorecard.py:115-158`), not in `contents.build()`. `_contents.py:194-196` names the STEPs and nothing imports them. It is *two independent printed trays* (`pcba-tray`, `power-tray`) plus a TBD DC block, always described together. `/hardware/printed-parts/enclosure/README.md:29` lists **"which zone holds the electronics"** as explicitly open. |
| 7 | SeaFlo at x[96,283] | **SOFT — and its stated justification is the electronics** | Three commits, all reasoned from the shelf: `4b4a58f7` "so the bay has a plane for the shelf"; `1b5d8975` "opening a 55.5 mm west column… wide enough to stand the IRM-90 (52 mm) on"; HEAD `7dd27fd8` "That opens 107.7 × 147.6 mm of full-height void west of the pump for the electronics shelf." |
| 8 | CO2 cap-top entry at (141.5, 217.8) | **HARD as a fabricated feature — and already violated** | See below. |

---

## 1. The board is committed

Definitive: **the outline is frozen.** 10 boards at 85.05 × 72.85, $702 paid, in JLC file review as of 2026-07-15 (today is 2026-07-25 — status is `ON-ORDER`, i.e. placed, not yet arrived). `order.md:78-84` records JLC's checkout modifying the panel to 85 × 82.8 with N/S rails and depaneling before delivery, so what arrives is the true 85.05 × 72.85. The tray's four boss centres are the MH coordinates verbatim (`pcba_tray.py:14-18` docstring, `:37-39`). Treat outline, hole pattern, and the J14-west / J10-east orientation as fixed steel. `electronics-shelf.md:63` adds the service rule: "the USB-C programming port (J14) flush at the west board edge, the J10 12 V screw throats facing east, **both edges left reachable**."

## 2. The stale port table — and what it hides

Confirmed dead, both tables. Nothing in the repo *consumes* those coordinates for routing (`_lines._frames()` at `_lines.py:104-118` only builds frames for components in `contents.build()`, and neither is there). They feed exactly one thing: `ports_audit`.

**And here is the gate that passes because the board is unplaced.** `scorecard.py:792`:

```python
elif solid is None or not _on_surface(p.pos, solid, shell, p.diam, tol):
    rows.append((p, "off-surface"))
```

All 21 non-`ok` ports in the sidecar are `pcba` (13), `power-tray` (4), `dc-dist` (3), `compressor-shroud` (1) — the first 20 read `off-surface` *solely because `solids.get(comp)` returns `None`*. `requirements.md:218-222` explains this as "the `pcba.tsx` mapping needs its Z re-solved against the board's real top face" — that narrative is a fossil from when the body was in the pack. Placing the board will not move `located` off 32/37; the coordinates are absolute world literals, unlike every other component's ports which derive through `contents.tee_port()`, `contents.noz_collet()`, `contents.back_port_station()` etc. **The port table must be rewritten as a pose-derived accessor, not edited numerically** — otherwise it silently decouples again on the next move.

## 3. The seven gates, and what turns on

`scorecard.py:1116-1161` + `lines_clear_check` appended at `:1131`:

| Gate | Tests | Newly applies when the two bodies land |
|---|---|---|
| `coverage` | placed set == registry set | **Fails immediately** — `power-tray`/`pcba` are not in `COMPONENTS` (`:115-158`). Registry rows must be added with `kind`/`sourced`/`held`. |
| `pack-closes` | no solid∩solid &gt; 1 mm³ | **Blocks the export** (`enclosure_assembly.py:299`). |
| `lines-clear` | no tube ∩ part/piece/tube | **Blocks the export.** Both trays sit in the band the nozzle lanes and water-4 cross. |
| `clearance-floor` | every pair ≥ **1.0 mm** unless in `TOUCHING_OK` | Applies. A tray resting flat on the foam cap is a 0 mm contact and **must be added to `TOUCHING_OK`** (`scorecard.py:165-177`) or it fails. |
| `pieces-fit-bed` | printed pieces ≤ 325×320×320 | Unaffected (trays are components, not enclosure pieces). |
| `seams-mate` | piece∩piece &lt; 5 mm³ | Unaffected. |
| `parts-sourced` | every component sourced | Both are real designs; add rows and it holds. |

Only `pack-closes` and `lines-clear` block the export. **`CLEARANCE_FLOOR = 1.0` mm is the only clearance rule the electronics must satisfy, and `scorecard.py:72-75` says it is explicitly unratified**: "Provisional… NOT yet ratified… Grow context keep-outs later (tube bend radius, tool/wrench access, condenser airflow) as their own gates." There is **no creepage, no air gap, no water keep-out** anywhere.

**The one non-obvious tripwire** — `_lines.py:470-481`:

```python
LANE_CLEAR = 5.65
crossings = [("the nozzle gate's spade tabs", contents.noz_spade_crown())]
if "pcba" in f:
    crossings.append(("the electronics shelf's board", f["pcba"].bb.zmax))
for what, crown in crossings:
    if deck_z - od / 2.0 - crown &lt; LANE_CLEAR:
        raise ValueError(...)
```

Measured: `deck_z = 292.43`, `od = 6.35`, so **max board crown = 283.605 mm**. Foam-cap top is 258.40; `pcba-assembly.step` is **27.10 mm** tall → zmax **285.50**. **A PCBA tray flat on the cap raises a build error, missing by 1.895 mm.** Worse, the test reads the board's *global* bbox zmax with **no X/Y overlap check** — it fires wherever the board is, even nowhere near the lanes. The comment says "whenever the shelf is on the deck," but the code only tests presence in the frames dict. This is a real wall for anyone who puts the PCBA tray on the cap, and it is over-broad. Note the check reads `f["pcba"]` only — the **power tray (40.5 mm) is not tested at all**.

## 4–5. Water, mains, earth

No water-over-electronics rule exists. The design deliberately runs two flavor lines above the board's plane with a 5.65 mm lane. No condensation or drip keep-out; the only wet telltale is the ASSE drip pan, whose `fall` rule is checked (`scorecard.py:419-423`) and holds at 18.4 mm onto `drip-pan`. Earthing is real and single-point at the shelf, which does constrain the shelf to be reachable by 16 AWG green from the C14, the compressor body, the shroud stud, and the pressure vessel. Mains/LV proximity is documented as *accepted*, not forbidden.

## 6. "The electronics shelf"

Prose. Two trays that are always said together but have no joint geometry, no combined STEP, no registry entry, and no bounding region. `/hardware/wiring/ac-wiring-schedule.md:14` and `electronics-shelf.md:3` both fix it "on the rear-panel C14 inlet's column" — that is the strongest positional statement in the repo, and it is a wiring-length argument, not geometry. It is contradicted at `/hardware/assembly/enclosure-mechanical.md:40` ("seated on the pump-2 column"), and `/hardware/printed-parts/enclosure/README.md:10` still says the shelf "currently has no station," which HEAD's own commit message disproves. `_lines.py:474-475` is the *only* code dependency on the board's placement, and it is presence-gated, so today no route changes if the board moves.

## 7. The SeaFlo's pose

**Not self-justifying.** Every one of its three moves cites the electronics. What *is* load-bearing about x[96,283] is downstream routing that derives from it:

- `_lines.py:502-508` — `seaflo_low_crown()` returns crown 306.4 and window x(239.3, 283.0); `fluid-18` rides `outer_x = 274.175`, `fluid-28` rides `inner_x = 248.125`. Both lanes are computed *from the pump's X*.
- `_lines.py:533-542` — the `over_pump` guard raises if a lane crosses the pump outside that window.
- `_lines.py:215, 256` — water-4 and fluid-1 take `(pump.bb.ymax + vk.bb.ymin) / 2.0` as their lane.
- `_contents.py:327` — `DISCH_CHAIN_POS` takes its X **from** `SEAFLO_POS`, so water-6 leaves the molded barb with no offset (R15.9 hose, 31.8 mm of tangent at stake — the real reason X is sticky).

Verified the claimed void with `fit.py slab --z 258.4,335.7 --size 90.82,73.3 --exact seaflo-pump`: **`107.7 × 147.6 mm  x[-14.0, 93.7] y[176.5, 324.2] z[258.4, 335.7]`** — exact match to the commit message. Caveat the other agents need: **only y[200, 324.2] of that rectangle has the foam cap under it** (107.7 × 124.2). Forward of y=200 there is no floor at that Z. The `power-assembly` at 151.1 mm does *not* fit the largest rectangle in either orientation; the `pcba-assembly` at 90.82 × 73.3 does.

---

## Addendum: the CO2 cap-top entry, and other undefended keep-outs

**The CO2 entry is HARD as a fabricated feature, and it is already violated.**

First, the coordinate in the brief is wrong. `_contents.py:54` says "(141.5, 199.8)" — that is stale by 18 mm. `_FOAM_FACE = contents.FRONT_DEPTH` = **200.0**, and `scorecard.py:521` places the port at `_FOAM_FACE + 17.8` → **(141.5, 217.8, 262.9)**. The whole docstring block `_contents.py:43-54` still quotes the old front face of 182 (carb-water outlet "at (141.5, 182, 46.5)" vs. the real 200.0). Every number in that block is 18 mm off.

Second, the riser is not merely unmodeled — the column is **occupied**:

```
probe.py cast 141.5,217.8,259.0 0,0,1 --dia 6.35
→ Ø6.35 runs 0.00 mm, stopped by seaflo-pump  end (141.50, 217.80, 259.00)

probe.py hits --x 133.5,149.5 --y 209.8,225.8 --z 258.4,340
→ seaflo-pump  3722.0 mm³  z[258.40, 312.21]
```

The pump's base sits flat on the cap (`TOUCHING_OK` includes `("foam-assembly","seaflo-pump")`, `scorecard.py:168`) directly over the bore. `_contents.py:112` claims the pose leaves "the CO2 top entry in open air ahead of it" and `/hardware/printed-parts/enclosure/README.md:10` repeats it. **Both are false at HEAD.** Nothing catches it: the CO2 segment is unrouted, `_lines.BLOCKED` is empty, and `located` scores the port `ok` only because `_on_surface`'s tolerance (bore radius 3.175 + tol 2.0 = 5.175) exceeds the 4.5 mm the port floats above the cap.

**Can it be deleted?** No — not cheaply, and the front slot is not a drop-in substitute. The entry is a real feature of three printed parts and an internal fitting:
- `_cold_core_interface.py:134-145` — the bore through the top cap **and its pour lid**;
- `/hardware/printed-parts/cold-core/foam-shell/README.md:43-44, 253, 368-372` — the line drops inside the cavity and bends 90° at a **PP0308E elbow standing in an 18 mm notch at x=0, cut inward from y=+78.5** — i.e. on the **opposite (+Y) side** of the vessel from the shared front slot;
- the shared −Y slot (`foam-shell/README.md:252-259`, penetrations 5–8) already carries four lines and reaches the **bottom-plate** ports, not the CO2 doorway.

So re-routing CO2 out the front means re-cutting the cap, the lid, the doorway, and re-posing the internal elbow. It is movable, but it is a cold-core redesign, not a deletion. **The cheap fix is to move the pump off the bore, or shift the bore's Y within the cap** — the bore's Y is derived (`co2_inlet_y`, a mid-radius between two foam bands), so it has some freedom.

### Declared-but-unmodeled keep-outs — the full sweep

Ranked by how likely another agent walks through them:

1. **CO2 riser column** at (141.5, 217.8) rising from z 258.4 to the ceiling. Prose only (`_contents.py:54, 112`; `enclosure/README.md:10, 25`). No solid, no check. **Already violated by the SeaFlo.**
2. **PCBA west + east edge access** — `pcba_tray.py:16-18` and `electronics-shelf.md:63`: "Keep the west and east edges unobstructed… USB-C flush on the west edge, the J10 screw throats east." No modeled volume, no check. A tray placed with either edge against a wall is a service defect nothing reports.
3. **PRV vent termination** — `enclosure/README.md:29`: "on the warm side where a relief event won't soak anything important." The `foam-assembly.prv-vent` port exists (`scorecard.py:527`) but the run is unauthored. This is the closest thing to a water-vs-electronics rule and it is one clause of prose.
4. **Condenser airflow** — `CONDENSER_AIRFLOW = 56.0` (`_contents.py:254`) and `enclosure/README.md:24`. Named as a future gate at `scorecard.py:75` and `requirements.md:113`. No intake/exhaust corridor solid exists.
5. **Tool / wrench access at every fastener** — named at `scorecard.py:75`, `requirements.md:113`. One instance is already a *recorded live defect*: `scorecard.py:117` — "The rear screw's driver lane is fouled by the MQ-6 as placed — 1.00 mm behind the shroud's rear face." Prose in a registry note; no gate.
6. **Drip-pan withdrawal travel** — the basin "draws aft… rising at no point in that travel" (`scorecard.py:121`), plus `enclosure-mechanical.md:92`: the deck under it "stays open for the SIG-9 leads and the C14 cordage." No swept-volume check. A tray landing in the aft strip could block it.
7. **Assemblability + service withdrawal generally** — `requirements.md:116-135`: "Today it has **no executable check**."
8. **BPV31 piercing-valve and reservoir-cap service voids** — `enclosure/README.md:29`, listed as open. No geometry.
9. **Tube bend radius** — `_contents.py:264` asserts "the discharge hose's bend radius **is a gate**". It is not: `scorecard.py:75` lists bend radius among the keep-outs to "grow later." Only `_lines` uses `bend` to shape the swept solid.

### Two bookkeeping defects found in passing

- **`scorecard.py:127-128` declares `discharge-chain` twice** with slightly different notes. `reg` dedupes to 36 but `total = len(COMPONENTS)` = 37, so **every goal denominator is inflated by one** and `parts-sourced` reads "37/37" while the pack holds 36 bodies.
- **`requirements.md` carries stale measurements**: `located 84%` (sidecar says 86%), "4.71 mm to the C14" (water-1 now measures 22.64 mm), and ":249" "4 mm between the drip's column and the electronics shelf's rear edge" — a number that cannot exist, since `clear power-tray` reads `inf`.

---

## What actually narrows the search

1. **The board outline, hole pattern, and J14-west/J10-east orientation.** Paid for, in production. Absolutely rigid.
2. **The `fluid-18/28` lane ceiling: any PCBA pose with `bb.zmax &gt; 283.605` raises the build.** On the foam cap that is a hard no at 285.50 unless the check is narrowed to an X/Y-overlapping test (which is what its own comment describes).
3. **`clear power-tray ≥ 8.0 mm` from the ASSE chain**, which also means the power tray must *exist* for `asse1022-assembly` to score placed. It is a lower bound only — it does not pull the tray toward the chain.
4. **`CLEARANCE_FLOOR = 1.0 mm` to every part**, plus a `TOUCHING_OK` entry needed for any tray resting on the cap.
5. **Single-point earth reachable by 16 AWG green** from C14, compressor body, shroud stud, pressure vessel.
6. **The 107.7 × 147.6 void — but only 107.7 × 124.2 of it has a floor.**

## What everyone is obeying for no reason

1. **The `(x+258.8, y+228.8)` z=292.5 port table and its power-tray twin.** Both dead volumes. Not consumed by any route. They pin nothing.
2. **"The shelf lives in Zone B on the foam-cap top, on the C14 column."** `/hardware/printed-parts/enclosure/README.md:29` explicitly lists **"which zone holds the electronics"** as open. The Zone B placement is a wiring-length preference restated in five documents until it reads as a spec.
3. **"The shelf" as one object.** Two independent trays with independent mounts and no joint geometry. Nothing requires them adjacent, coplanar, or coaxial. Splitting them is free and roughly doubles the reachable pose space.
4. **The SeaFlo's current X.** Justified by the electronics in all three of its move commits. If the electronics go elsewhere, x = 189.5 has to re-earn itself from the water chain alone — and the thing that would genuinely resist is `DISCH_CHAIN_POS` tracking `SEAFLO_POS[0]` for the R15.9 hose, not the west column.
5. **Any assumed water/mains keep-out.** Does not exist. If a proposal wants one, it is a *new* requirement to argue for, not an existing wall.
6. **`_contents.py:43-54`'s coordinate block.** Every Y in it is 18 mm stale. Do not read placements out of it.</result>
<usage><subagent_tokens>249068</subagent_tokens><tool_uses>100</tool_uses><duration_ms>1043535</duration_ms></usage>
</task-notification>

---

# Assistant

---

The archaeologist landed, and it's decisive. Forwarding the load-bearing findings to the three still running.

---

# Assistant

---

Before I report a live defect at HEAD, let me settle it myself.

---

# Assistant

---

Both defects verified independently. Reporting.

## Two live defects at HEAD

**1. The SeaFlo is sitting on the CO2 riser.** The cap-top CO2 entry is at (141.5, **217.8**, 262.9) — [scorecard.py:521](hardware/printed-parts/enclosure/enclosure-assembly/scorecard.py:521). My earlier coordinate was wrong because the docstring block at [_contents.py:43](hardware/printed-parts/enclosure/enclosure-assembly/_contents.py:43) is **18 mm stale in Y throughout** (it still quotes a front face of 182 against the real 200.0). Confirmed:

```
probe cast 141.5,217.8,259.0 0,0,1 --dia 6.35
→ Ø6.35 runs 0.00 mm, stopped by seaflo-pump
probe hits --x 133.5,149.5 --y 209.8,225.8 --z 258.4,340
→ seaflo-pump  3722.0 mm³  z[258.40, 312.21]
```

The pump's base is flat on the cap directly over the bore. `_contents.py` still claims the pose leaves the CO2 entry "in open air ahead of it." Nothing catches it: the CO2 segment is unrouted, and the port scores `ok` only because `_on_surface`'s tolerance exceeds the 4.5 mm it floats above the cap.

**2. `discharge-chain` is declared twice** — [scorecard.py:127](hardware/printed-parts/enclosure/enclosure-assembly/scorecard.py:127) and `:128`, two `_c(...)` rows with differing notes. `reg` dedupes to 36 but `total = len(COMPONENTS)` is 37, so **every goal denominator is inflated by one** and `parts-sourced` reads 37/37 over a pack holding 36 bodies.

## The finding that matters most

There is a hard ceiling on the board's crown that nobody knew about — [_lines.py:474](hardware/printed-parts/enclosure/enclosure-assembly/_lines.py:474):

```python
if "pcba" in f:
    crossings.append(("the electronics shelf's board", f["pcba"].bb.zmax))
for what, crown in crossings:
    if deck_z - od / 2.0 - crown < LANE_CLEAR:
        raise ValueError(...)
```

With `deck_z = 292.43`, `od = 6.35`, `LANE_CLEAR = 5.65`, the maximum board crown is **283.605 mm**. The `pcba-assembly` is 27.10 tall, so **flat on the foam cap it raises the build — by 1.895 mm.** It reads the board's *global* bbox zmax with **no X/Y overlap test**, so it fires wherever the board sits.

**And your idea is what clears it.** That 27.10 includes the tray's own `floor_t = 3.0` ([power_tray.py:51](hardware/printed-parts/electronics/power-tray/power_tray.py:51)). Print the bosses into the cap and the floor disappears: board underside at 258.40 + 5.0 standoff = 263.40, crown at **282.50** — inside the limit by 1.105 mm. The tray isn't just surplus; it's the 3 mm that breaks the build. I've asked the pose agent to verify that against real geometry rather than my arithmetic.

## What the audit settled

**Frozen:** the PCBA outline. JLCPCB order W2026071513250534, 10 boards, **$702 paid**, placed 2026-07-15, in file review — [purchases.md:279](hardware/ledger/purchases.md:279). 85.05 × 72.85, holes on the 78.0 × 66.3 rectangle, J14 west / J10 east. That lever is closed.

**Also hard:** single-point earth at the shelf (it's what gives the appliance Class I status) — reachable by 16 AWG green from the C14, compressor body, shroud stud, and pressure vessel. And `CLEARANCE_FLOOR = 1.0 mm`, itself flagged unratified in its own source.

**Fossils, obeyed for nothing:** both port tables — the `pcba` one *and* a `power-tray` twin at `scorecard.py:720` that nobody had flagged, whose volume `hits` reports as 120,934 mm³ of pump. Neither is consumed by any route. "The shelf" as one object — two independent trays, no joint geometry, no registry entry; [enclosure/README.md:29](hardware/printed-parts/enclosure/README.md:29) still lists *which zone holds the electronics* as **open**. And the SeaFlo's X, whose three move commits all cite the electronics as their reason.

**Doesn't exist:** any water-over-electronics rule. The design deliberately routes the flavor lines above the board. And AC/LV segregation — [wiring.md:5](hardware/assembly/wiring.md:5) documents mains, 12 V and signal sharing one zip-tied bundle as accepted.

One correction to my last message: the void is **107.7 × 147.6**, but only **107.7 × 124.2** of it has the foam cap under it — forward of y=200 there is no floor at that Z.

Three agents still running. I'll hold off on fixes until they land, so I'm not editing geometry underneath the census.

---

# User

---

<task-notification>
<task-id>afa47907f1346bc57</task-id>
<tool-use-id>toolu_01K3yPz79gA6ah6v8qLnPhvJ</tool-use-id>
<output-file>/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/f6d55805-50ea-4d28-8cc7-57bec2421b42/tasks/afa47907f1346bc57.output</output-file>
<status>completed</status>
<summary>Agent "Orientation and mounting modes" finished</summary>
<note>A task-notification fires each time this agent stops with no live background children of its own. The user can send it another message and resume it, so the same task-id may notify more than once.</note>
<result>I have the survey. Writing it up now.

## Pose and mounting-mode survey — PCBA and IRM-90 PSU

### 0. What I measured, and what the instruments cannot see

`probe.world()` holds **the pack, the panel bodies, the funnel and the routed tubes — not the enclosure shell** (`hardware/scripts/probe.py:442-466`). So `hits`/`slab`/`fit.check` are blind to walls, seam lips, cross-pin pods, corner posts and the ceiling. I therefore loaded the four printed pieces directly (`enclosure-back-top.step`, `-back-bottom`, `-front-top`, `-front-bottom`) and intersected every candidate volume against them as well. Every "clear" below means *clear of the placed world **and** clear of the real printed box*.

Cavity, from the box's own generator:

```
tools/cad-venv/bin/python -c "...; import enclosure; print(enclosure._dims().inner)"
inner = (-14.0, 297.0, -3.0, 384.0, 0.0, 335.7)
z_joint_back = 267.0   lip_len = 13.1   boss_in = 14.0   wall = 3.0
```

Ceiling **335.70**. Foam-cap top **258.40**. Service bay height **77.30 mm**. That number rules out more poses than any obstacle does.

`fit.py parts` lists `meanwell-irm90` (52.0 × 109.0 × 33.5) but **not** the PCBA or the power tray — they are printed parts, so the PSU was tested with `fit.try`/`fit.check` on the real solid and the PCBA with `probe.hits` on measured envelopes. I passed `clearance=6` on every `fit.check` so near bodies got exact solid distances rather than box gaps, and re-took the headline gaps with `w.gap()`.

---

### 1. The discriminator is a crown gate, not a collision

`_lines.py:470-481` raises when the board's **global bbox zmax** exceeds the nozzle-lane ceiling. Verified:

```
w.at("bulkhead-flavor-a","tube-in") -&gt; (231.93, 359.20, 292.43)
crown ceiling = 292.43 - 6.35/2 - 5.65 = 283.605
```

It reads `f["pcba"].bb.zmax` with **no X/Y overlap test**, so it fires wherever the board is — even though `fluid-18`/`28` themselves run at x[198.9, 292.4], nowhere near the west column. It is dormant today only because the PCBA is declared but never `_at`.

Board stack, measured (`pcba-assembly.step` bbox = 90.82 × 73.30 × **27.10**):

| term | mm | source |
|---|---|---|
| tray floor | 3.00 | `power_tray.py:51`, re-exported `module_tray.py:26` |
| boss standoff | 5.00 | `module_tray.py:28` |
| board | 1.60 | `pcba_tray.py:42` |
| tallest component | **17.50** | **U10, the K7805 5 V buck SIP** — measured off the glb at pcb x[-34.21,-25.69] y[-25.00,-13.40], 8.51 × 11.60 × 17.50; placed at `pcba.tsx:425` |
| **board underside → crown** | **19.10** | 1.6 + 17.5 |

**There are no bottom-side bodies at all** in the glb — the underside carries only THT tails.

Crowns by mode (deck = 258.40):

| PCBA mode | crown | vs 283.605 |
|---|---|---|
| tray on the cap, as built | **285.50** | **+1.895 → build raises** |
| **cap-rooted bosses, standoff 5.0 (no tray floor)** | **282.50** | **−1.105 PASS** |
| cap-rooted bosses, standoff 3.0 | 280.50 | −3.105 PASS |
| tray kept, standoff cut to 3.0 | 283.50 | −0.105 (0.1 mm — not a margin) |
| boss tops recessed to the cap rim 256.4 + 5.0 | 280.50 | −3.105 PASS |
| on edge (73.30 tall) | 331.70 | +48.1 FAIL |
| on end (90.82 tall) | 349.22 | FAIL, and 13.5 mm above the ceiling |
| hung from the ceiling (10 mm drop) | ~325.7 | +42.1 FAIL |
| two-level, board bridged over the PSU | 321.50 | +37.9 FAIL |

**Max board standoff on the cap with no floor under it: 6.105 mm.** The coordinator's arithmetic holds — the owner's idea is not merely tidier, it is what makes the board legal.

Two levers worth naming: swapping U10 for a lower buck buys 1.59 mm (next tallest is C3, 15.91); and the gate itself is one X/Y-overlap test away from not binding a west-column board at all.

The PSU has **no** crown gate — `crossings` names only the nozzle-gate spade tabs and `f["pcba"]`.

---

### 2. Orientation matrix

**Mean Well IRM-90 (52 × 109 × 33.5, 4× M3 on 33 × 98, ~219 g per its README / ~200 g per `electronics-shelf.md:126`)**

| # | orientation | footprint | height | top z on the cap | verdict |
|---|---|---|---|---|---|
| P1 | flat, length along Y | 52 × 109 | 33.5 | 291.90 | **viable** — `fit.py try meanwell-irm90 --bbmin=2,202,258.4 --yaw 0 --clearance 6` → no clash; 42.00 mm to seaflo-pump, 30.62 to drip-pan-rails, 54.25 to c14-inlet |
| P2 | flat, length along X | 109 × 52 | 33.5 | 291.90 | **ruled out** in the west column — `--bbmin=0,210,258.4 --yaw 90` → CLASH seaflo-pump 1081.5 mm³. 109 &gt; the 96 mm the column has |
| P3 | on the 52-face (pitch 90) | 33.5 × 109 | 52 | 310.40 | **viable** — `--bbmin=10,210,258.4 --pitch 90 --clearance 6` → no clash, 52.50 mm to seaflo-pump. Halves the footprint to 3650 mm² |
| P4 | on the long edge (roll 90) | 52 × 33.5 | 109 | 367.40 | **ruled out** — 31.7 mm above the ceiling. `fit` reported "no clash" because the world has no box |
| P5 | standing on a terminal end | 52 × 33.5 or 33.5 × 52 | 109 | 367.40 | **ruled out** on the cap, same reason. **Viable below**: in the machine corridor `hits --x 0,52 --y 140,173.5 --z 30,139` → CLEAR |

Terminal ends are ±Y in the part frame (AC at +Y, DC at −Y). P1 with yaw 0 puts AC toward the rear wall where the C14 is and DC toward the front where the board is — the wiring falls out right.

**PCBA (assembly 90.82 × 73.30 × 27.10; board+components alone 19.10 thick + ~2.5 for tails)**

| # | orientation | footprint | height | crown | verdict |
|---|---|---|---|---|---|
| B1 | flat, long axis X | 90.82 × 73.30 | 27.10 / 19.10 | 285.50 / **282.50** | **viable only bossed** — `hits --x 2,92.82 --y 202,275.3 --z 258.4,285.5` CLEAR, but only 3.2 mm of X left before the pump |
| B2 | flat, long axis Y (yaw 90) | 73.30 × 90.82 | 27.10 / 19.10 | 285.50 / **282.50** | **best** — `hits --x 11,84.3 --y 208,298.82 --z 263.4,282.5` CLEAR of world and of all four printed pieces |
| B3 | on edge, long axis X | 90.82 × 27.10 | 73.30 | 331.70 | ruled out by the crown gate (+48). Solid-clear otherwise |
| B4 | on edge, long axis Y | 27.10 × 90.82 | 73.30 | 331.70 | same. `hits --x 4,31.1 --y 215,305.82 --z 258.4,331.7` CLEAR of world and box — geometry allows it, the gate does not |
| B5/B6 | on end | 73.30 × 27.10 | 90.82 | 349.22 | ruled out twice: gate, and 13.5 mm above the ceiling |
| B7 | inverted, components down | 90.82 × 73.30 | ~21 | ~279.0 | lowest crown of all, but buries all 12 loom faces downward — ruled out on service |

**Every on-edge pose also buries one connector row** — see §4 — so B3/B4 are doubly out.

---

### 3. Mounting-mode matrix (the roots)

**M1 — printed tray on a horizontal plane (status quo).** Costs the board 3.0 mm it does not have. Nothing fastens the tray to anything: `requirements.md` — "every loose internal part floats"; `enclosure-mechanical.md:112` says only "seat flat". *Ruled out for the PCBA by the crown gate; fine for the PSU.*

**M2 — bosses printed into the cold core's cap.** This splits in two and the distinction is decisive.

- **M2a — bosses on the foam-cap *lid*.** Not viable as literally stated. The lid is `build_foam_cap_lid()` (`_foam_cap.py:60-90`): a **2 mm flat plate**, no ribs, no bosses. `cold-core.md:74` uses it as the **pour clamp** — "The screws are the pour clamp… then back the six screws out" — and `bom.md:150` reads *"Printed tooling does not ship: … the foam-pour cap lids."* There is no BOM row for either lid. The geometrically identical bottom lid is described at `cold-core-ring/README.md:33` as "an unsupported plate over pour foam".
- **M2b — bosses as columns *through the cap*, rooted on the cap floor.** This is the viable reading, and it is already the cap's own idiom: `build_foam_cap()` unions `build_attachment_bosses(foam_cap_height)` — **six Ø8.0 columns spanning the full 18 mm cap height**, foam poured around them, trimmed flush. Adding four more for the board and four for the PSU is the same operation. Print geometry is ideal: the cap prints floor-down, so each column rises off the bed at constant section. Their stations in world (verified from `_cold_core_interface.attachment_xy_positions` + the 180° top-cap spin + centre (141.5, 290.5)):

  ```
  (6.343, 206.343) (6.343, 374.657) (276.657, 206.343) (276.657, 374.657)
  (126.500, 204.000) (156.500, 377.000)      screw_boss_size = 8.0
  ```

  Those six are M3 clearance through-holes for the cap screws — a new boss must not land on them, and only two of them fall in the west column, at opposite corners, so they are no use as a board pattern. **Load path caveat:** a new column stands on the cap's 2 mm floor, which bears on the shell's top face; only the six existing stations continue into a threaded insert. The repo states **no allowable load for that plate** (I checked). 219 g on four columns is ~0.5 N each — almost certainly fine — but it is judgement, not a repo fact.
  
  Cost: the cold-core cap becomes board-specific. A connector move reprints a 171 g part that also has to be foam-poured.

**M3 — bolted to a vertical enclosure wall.** I mapped the −X wall band `x[-14,0]` through the bay in 25 mm slices against both back pieces:

| y | what stands there |
|---|---|
| 200–225 | nearly clear (a sliver at x[-14,-8.25]) |
| **225–250** | 13 715 mm³ in the top piece, full height — the Y-seam corner column |
| **250–275** | a post at y[250, 254.7], **full height to x = 0** |
| 275–350 | **only the Z-seam lip, x[-14,-11], z[264, 280.1]** — i.e. **x[-11, 0] is free** |
| **350–375** | a rear-corner post at y[367.7, 375], full height |

So a wall-rooted bracket is possible **only in y ≈ 275–367**, and the hard rule is: **the back column's Z seam sits at z = 267, only 8.6 mm above the cap top, and cuts the bay in half.** A bracket is rooted in the back-**bottom** piece (usable band z 258.4→267, 8.6 mm) *or* the back-**top** piece (usable from the lip rim, z ≥ 280.1) — never both. `SIDE_RIB_INSET = 14` is not advice; it is occupied solid.

**M4 — hung from the cavity ceiling (z = 335.70).** Geometrically the freest volume in the machine — `fit.slab --z 300,335.7 --exact seaflo-pump` returns **109.6 × 331.1 mm** free at x[-14, 95.6] y[-3, 328.1] — and it has the **best print geometry in the matrix**: the back-top piece prints **ceiling-down**, so a boss projecting into the cavity is a vertical column off the bed, exactly the enclosure's own "every boss stands on a post of its own section" rule. `hits --x 2,92.82 --y 210,283.3 --z 308.6,335.7` → CLEAR of world and box. **But** it fails the PCBA crown gate by ~42 mm, and it inverts the assembly order: the electronics descend into the bay with the top piece, dragging every loom. Live for the **PSU**, dead for the board unless the gate is fixed.

**M5 — cantilever / bridge.** Real free volumes exist and I verified them: PCBA over a flat PSU at z[294.4, 321.5] CLEAR; PSU flat 109 × 52 in the **front-top**, over the bag tray, `hits --x 2,111 --y 100,152 --z 292,325.5` → CLEAR of world *and* of `enclosure-front-top`. Neither has a root today, and the board version fails the gate.

**M6 — four bosses, no floor at all.** For the PCBA the mount reduces to **four coplanar tops on a 78.0 × 66.3 rectangle** (`pcba_tray.py:40`), each Ø7.0 with a Ø4.0 × 5.5 heat-set bore (`module_tray._boss_spec`, M3 branch). Everything else the board needs is air. **What it buys: the 3.0 mm floor, which is the whole crown problem.** For the PSU it is four M3 on 33 × 98, and `power_tray.psu_boss_h = 4.0` is already a no-standoff boss — the PSU base bears on the boss tops, so nothing is lost by deleting its floor either.

**M7 — mixed roots.** The idiom transfers unchanged: `module_tray._insert_boss` is a free-standing cylinder with a blind bore; nothing in it references the tray floor. Two constraints, both hard. (a) All four boss tops must be coplanar — a board bolted across two printed bodies inherits their assembly stack-up as board bending. (b) **No boss may span a seam**: not z = 267 (the back Z seam) and not y = 223.3 (the Y seam). A boss half in one piece is not a part.

---

### 4. The real constraints

**Connector access — this is sharper than the port table.** I read the footprints, not the stale world coordinates.

- The 12 JST wafers are **vertical / top-entry**: the JLCPCB `WAFER_XH2_54_*PZZ` bodies measure **5.85 mm deep × 7.0 mm tall** off the glb, asymmetric about the pin row (−2.35/+3.50) — the B\*B-XH-A signature, not the 8.1 mm-deep right-angle part. **Every loom mates along +Z out of the component face** and dresses outboard over the latch wall. That matches `scorecard.py`'s `"z+"` and "looms plug from +Z", and it is the one thing in that fossil table still true.
- **J14 USB-C mates horizontally along −X** — `pcba.tsx:1374`, "west edge above the WROOM, opening flush to the west board edge".
- **J10 KF301 wire throats face +X** — `pcba.tsx:475`, "pcbRotation 90 aims the wire throats at the east board edge, so the field loom feeds in from OUTSIDE the board".
- **All four edges carry cable.** N: J5, J6, J13, J8. S: J3, J4, J9, J7. W: J14, J11. E: J1, J2, J10. No edge may be buried — which independently kills every on-edge pose (the resting edge is a connector row) and every inverted pose.
- `electronics-shelf.md:63` and `pcba_tray.py:16-18` state the rule directly: J14 west, J10 east, **"both edges left reachable"**. Unmodeled and unchecked — a pose with either edge against a wall is a silent defect.
- Note the WROOM antenna overhangs the west board edge by **5.82 mm** (assembly x[-73.82, 17] vs outline x[-68, 17]) and is only 3.10 mm tall — it is why the assembly is 90.82 wide, and it wants air, not a wall.

**Thermal — a real answer, not a caveat.** The repo has **no IRM-90 derating curve, no ambient limit, no orientation note** (I had the reference folder and every mention swept; `bom.md`, `electronics-shelf.md:23`, `ac-wiring-schedule.md:53` are all electrical). It has **no ventilation for the electronics bay** — the only airflow in the machine is the condenser's side-to-side path two zones away, and even those grilles exist in prose with **zero hits** for `grille|louver|vent|slat` in `enclosure.py`. Two ambient figures conflict: ~30–40 °C (`back-panel/README.md:75`) and 40–55 °C (`pcba-audit-2026-07-13.md:47`).

Given that, here is the answer to "the PSU under the board is the worst place for it", labelled as engineering judgement:

*Zone B is a sealed dead-air pocket.* Under stagnation the pocket floats to whatever temperature its total wall area sheds, and the PSU's ~10 W of loss reaches the board whether it sits under it, beside it, or across the bay. **Orientation is a second-order variable here; ventilation is the first-order one.** What "directly under" specifically adds is a plume straight onto the board's underside and the loss of the board's own upward escape — real, but small next to a pocket with no exit. So: *do not stack them* (side by side on the cap costs nothing and removes the plume), and *do not treat orientation as the fix.* Two further judgements: (i) bolting the PSU flat to the cap would conduct its heat into the lid of a refrigerated core — a parasitic compressor load across the insulation the cap exists to provide; **four Ø8 PETG columns through 16 mm of pour foam is a much better thermal path than a flat contact patch**, so M2b is thermally the *right* mount, not a compromise; (ii) the board's own hot spot is U4/U5, and the audit's numbers are for the superseded ULN2803 — the committed TBD62083 DMOS dissipates ~8× less (`uln2803.md:4-7`), so that gate is looser than the audit reads, though still the repo's one named open fitness gate. **What would settle it:** the IRM-90 datasheet derating curve (output vs ambient, plus any mounting-orientation note) and one measured bay ambient during burn-in. Both cheap; neither exists.

**Service access.** Approach is **front** (cabinet door) and **top** (Zone C door, funnel out) — `front-panel/README.md:5`, `future.md:53`. The electronics bay is at the **rear-top with no service door**, and `requirements.md:116-135` names serviceability as an unmeasured, unchecked requirement. Must be reachable on an assembled chassis: **J14** (flashing runs after the back panel is on, `firmware-and-commissioning.md:69`), the **12 V test point** at the DC block, **5 V at J4/J5**, **3V3 at J4/J8**, and the **ground ring stack** during `wiring.md`. Bench-only: PSU AC terminals, Wago levers, BT1. No fuse is serviceable — the board carries none, and the AC-primary fuse is undecided. The consequence for mounting: **the only way into the bay is lifting the back-top piece**, so anything rooted in that piece leaves with it and anything on the cap is exposed by it. For J14/J10 to be reachable in situ the board wants to be on the cap with both X edges facing open air.

**Retention.** No fastener retains either tray to anything today. No captive-fastener rule exists. The only bonded attach in the whole build is the drip-pan rails' VHB 4941, and `bom.md:256` calls it "the only bonded (rather than screwed) mechanical attach in the build". Compressor-running vibration on the electronics is nowhere discussed. Flat + gravity is what the repo currently assumes; every non-flat mode has to invent retention, and that is a cost the matrix should charge them.

---

### 5. The combinations that unlock the most space

**The headline void, verified against the world and all four printed pieces:**

```
probe.py hits --x 0,96 --y 200,326 --z 258.4,335.7    -&gt; CLEAR (96 × 126 × 77.3 mm)
```

At 1 mm resolution the bay offers exactly two maximal rectangles that hold either footprint:

```
fit.slab(z=(258.4,291.9), x=(0,96), y=(200,381), step=1.0, exact=("seaflo-pump",), size=(52,109))
   80.0 × 160.0  x[0,80]  y[200,360]
   96.0 × 126.0  x[0,96]  y[200,326]
```

**Neither holds both flat.** 90.82 + 52 = 142.8 against 96 of X; 73.3 + 109 = 182.3 against 126 (or 160) of Y. That is the arithmetic the whole problem reduces to: **the bay's free plane seats exactly one of the two.**

**① PCBA flat on cap-rooted bosses, yawed 90°, in the west column — the unlock.**
```
probe.py hits --x 11,84.3 --y 208,298.82 --z 263.4,282.5   -&gt; CLEAR (world + all four pieces)
```
Crown **282.50**, clears the gate by 1.105 mm. Both X edges face open air; I checked the approach lanes and the plug column: USB-C lane `--x 30,66 --y 178,208 --z 263,283` CLEAR, J10/loom lane `--x 30,66 --y 298.8,328.8 --z 263,283` CLEAR, 15 mm plug column over the whole board CLEAR. Root: four Ø8 columns through the cap on the 78.0 × 66.3 pattern, M3 heat-sets, `board_standoff = 5.0` unchanged. **Settled by:** fixing the cap-top datum (see below) and confirming the cap plate's allowable load.

**② PSU on the 52-face (P3), sharing the west column — 3650 mm² instead of 5668.**
```
fit.py try meanwell-irm90 --bbmin=10,210,258.4 --pitch 90 --clearance 6   -&gt; no clash, 52.50 mm to seaflo-pump
```
Footprint 33.5 × 109, height 52 (top 310.4, 25 mm under the ceiling). This is the only orientation that lets the PSU and the board share the column without moving the pump — and it stands the brick on edge in a stagnant pocket, which is the better convective attitude of the two. **Settled by:** the IRM-90 orientation note, plus a retention scheme (on edge it needs one; flat it does not).

**③ PSU out of the bay entirely — the machine corridor.** Wholly unclaimed volume behind the compressor:
```
probe.py hits --x 0,100 --y 133,200 --z 3,164.8   -&gt; only fluid-25 (a tube at x[41.32,47.68]) and cold-core-ring
probe.py hits --x 0,52 --y 140,173.5 --z 30,139   -&gt; CLEAR      (PSU standing on end, 109 vertical)
```
This gives the board the whole west column, separates the two heat sources by a zone, and puts the PSU beside the compressor terminal block it feeds. Against it: `_contents.py` reserves the corridor for refrig-3's unauthored run, the mains has to come down from the rear-top C14, and service access is poor. **Settled by:** whether refrig-3 needs that west half, and where the AC hub actually lands.

**Runner-up worth knowing about:** `hits --x 2,111 --y 100,152 --z 292,325.5` → CLEAR of the world **and** of `enclosure-front-top` — a PSU-sized void in the front-top piece over the bag tray, west of the funnel. Unclaimed, but far from the C14 and rootless.

---

### 6. The thing to settle before any of this is dimensioned

The crown margin in the best mode is **1.105 mm**, and the cap-top datum is not certain to that. The CAD stacks **caps + lids, no gaskets** (`foam_assembly.py:85-100`) → 253.4 → top at 258.40. `_cold_core_sync.py:117` stacks **caps + gaskets, no lids** → also 253.4 → also 258.40. They agree only because lid and gasket are both 2.0 mm. If both ship, the top is **262.40** and mode ① fails by 2.9 mm; if neither does, it is **256.40** and mode ① gains 2 mm. `_contents.py:799` already says "the foam tops out at ~263" and `scorecard.py:521` puts co2-in at 262.9. **Resolve 258.4 vs 262.4 first — it flips the verdict on the mode this survey recommends.**

Two smaller corrections found in passing: `_contents.py:54` puts the CO2 top entry at (141.5, 199.8), `:839` at (141.5, 172.8), `scorecard.py:521` at (141.5, 217.8) — the geometry (`_cold_core_interface.co2_inlet_y = −72.75`, top cap spun 180°) puts it at **(141.5, 363.25)**, on the *rear* half of the cap. And `meanwell-irm90/README.md:5` links the power tray to `printed-parts/valve-manifold/`.

I edited nothing; all scratch work is in the session scratchpad.</result>
<usage><subagent_tokens>252356</subagent_tokens><tool_uses>70</tool_uses><duration_ms>1783863</duration_ms></usage>
</task-notification>

---

# Assistant

---

The pose agent's CO2 coordinate contradicts the archaeologist's — and I reported the archaeologist's to you. Settling that now.

---

# Assistant

---

Settled — and I need to correct myself.

---

# Assistant

---

## Correction: I was wrong about the CO2 riser

I told you the SeaFlo was sitting on it. It isn't. I settled it by casting into the foam:

```
cast 141.5,363.25,262 → 0,0,-1   runs 235.00 mm, through to z=27.00
cast 100.0,290.0,262 → 0,0,-1    runs   3.60 mm, stops at z=258.40   (control: solid cap)
```

The bore passes clean through at **(141.5, 363.25)** — the *rear* half of the cap — while the control 73 mm away stops dead on the cap top. The scorecard declares `co2-in` at y=217.8, and `_contents.py` names 199.8 in one place and 172.8 in another. **All three prose figures are wrong; the geometry is at 363.25.** So the pump is not on the riser, and the cap around y≈218 is free. What *is* real: a line rising out of the true bore hits the **drip pan** 18.1 mm up. Still a live conflict, just a different one, and 145 mm from where I put it.

The `discharge-chain` double-declaration stands as reported.

## Your idea: verified — but it's the cap, not the lid

The crown gate arithmetic holds exactly. Tallest component is **U10, the K7805 buck SIP at 17.50 mm**; there are no bottom-side bodies at all.

| PCBA mode | crown | vs 283.605 |
|---|---|---|
| tray on the cap, as built | 285.50 | **+1.895 → build raises** |
| **cap-rooted bosses, standoff 5.0** | **282.50** | **−1.105 PASS** |
| tray kept, standoff cut to 3.0 | 283.50 | −0.105 (not a margin) |
| on edge / on end / hung / bridged | 331.7–349.2 | fail by 38–65 |

Max standoff on the cap with no floor: **6.105 mm**. Deleting the tray floor is what makes the board legal.

**But the lid won't take it.** `build_foam_cap_lid()` is a 2 mm flat plate that serves as the *foam-pour clamp* — [bom.md:150](hardware/ledger/bom.md:150) reads *"Printed tooling does not ship: … the foam-pour cap lids."* It also installs rotated 180°, carries pour and vent holes, and is printed twice.

**The cap itself already does exactly what you described.** `build_foam_cap()` unions `build_attachment_bosses(foam_cap_height)` — **six Ø8.0 columns spanning the full 18 mm cap height, foam poured around them, trimmed flush.** Four more columns on the board's 78.0 × 66.3 pattern is the same operation, printing floor-down at constant section off the bed. Your idea is right; it lands one part below where you named it.

And it's thermally the *better* mount, not a compromise — bolting the PSU flat to the cap would conduct its loss straight into the lid of a refrigerated core. Columns through 16 mm of pour foam is a far worse heat path, which is what you want.

The verified pose: `hits --x 11,84.3 --y 208,298.82 --z 263.4,282.5` → **CLEAR** of the world *and* of all four printed enclosure pieces, with both board edges facing open air and the USB-C and J10 approach lanes checked clear.

## The one number that decides it

The margin is **1.105 mm**, and the cap-top datum isn't certain to that. Two generators disagree: [foam_assembly.py:85](hardware/printed-parts/cold-core/foam_assembly.py:85) stacks caps + lids and no gaskets; `_cold_core_sync.py:117` stacks caps + gaskets and no lids. They both land on 258.40 **only because lid and gasket are each 2.0 mm**. If both ship the top is 262.40 and the mode fails by 2.9 mm; if neither, it's 256.40 and gains 2 mm. That's the first thing to resolve.

## A free win, found in passing

`psu_rot` is 90° — which points the PSU's **AC** block at the tray's empty west end, **132.69 mm** from the Wago it feeds, and its **DC** block at the Wagos. The PSU is mounted end-for-end. Changing `90.0 → 270.0` yields a **byte-identical tray** (both 151.10 × 73.94 × 17.74, both 43.1 cm³ — the hole pattern is 180°-symmetric) and drops that run to 36.06 mm. It trades **97 mm of energized mains conductor for 97 mm of SELV 12 V.** Worth doing regardless of what else happens.

Two other things worth knowing: the ground stack **can't** migrate to the front floor as I speculated — its C14 and shroud-stud bonds ride bundles that must reach the Wagos anyway, so it's free there and expensive anywhere else; beside the G Wago it's 12.0 mm instead of today's 116.78. And `power-tray`, `pcba` and `dc-dist` have **no `_c(...)` registry entry at all** — they have ports, a placement rule and colour-map entries, but the pack does not know they exist.

## What the pair problem actually is

The monolith fits fine on its own (`slab --size 151.1,73.94` returns a 79.7 × 183.5 rectangle). Re-laying it only recovers 13% of hull slack versus today's 18%, because `_build_floor` is a convex hull and can't cut a waist. So "re-lay the tray" — the prior session's plan — buys almost nothing. **The bay's free plane seats exactly one of the two parts**: 90.82 + 52 = 142.8 against 96 of X, 73.3 + 109 = 182.3 against 126 of Y. Splitting is what deletes area, because a split drops the hull.

The most interesting escape found: `hits --x 0,52 --y 140,173.5 --z 30,139` → **CLEAR** — the machine corridor behind the compressor holds the PSU standing on end, out of the bay entirely, giving the board the whole west column and separating the two heat sources by a zone.

The volume census is still running; I'll fold it in and put a concrete proposal to you rather than another survey.

---

# User

---

<task-notification>
<task-id>a08256a0afd8f2fb1</task-id>
<tool-use-id>toolu_01YWdnSU3QACqCoyebRFekwc</tool-use-id>
<output-file>/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/f6d55805-50ea-4d28-8cc7-57bec2421b42/tasks/a08256a0afd8f2fb1.output</output-file>
<status>completed</status>
<summary>Agent "Free-volume census" finished</summary>
<note>A task-notification fires each time this agent stops with no live background children of its own. The user can send it another message and resume it, so the same task-id may notify more than once.</note>
<result>## Volume census — full-cavity survey

**Headline: the fence was wrong. The single largest free volume in the machine is not on the foam cap — it is the front mezzanine over the refrigeration floor, and it holds *both* electronics bodies today with nothing moved.**

---

### 0. Instrument correction you need before reading any number

`probe.world()` holds **contents only**. The enclosure's own walls, seam lips, cross-pin pods, corner posts and refrigeration mounts are not in it, and `fit.slab` bounds its field by `enclosure._dims().inner` — the wall line and nothing else. I loaded the four printed pieces and measured what they put back:

```
shell material inside the wall line: 1018.8 cm3
```
(`scratchpad/shell.py`, fusing `enclosure-{front,back}-{top,bottom}.step` ∩ the inner box)

Every `slab` rectangle that runs to `x[-14` or `,297]` is therefore **not free**. I rebuilt the census with the shell folded in as 1705 measured obstacle boxes (`scratchpad/shell_profile.py` → `census3.py`), and re-checked every ranked candidate with an exact boolean against the shell solid.

### 1. The cavity — verified, not inherited

`enclosure._dims().inner` = **x[-14, 297] y[-3, 384] z[0, 335.7]** — the brief's claim confirmed. It is **not uniform**. Minimum inset from all four walls that clears shell material:

| band | min uniform inset | what bites |
|---|---|---|
| z[0, 60] | none at ≤60 mm | compressor foot mounts `x[14,192] y[0,133] z[0,26.1]`, condenser ears `x[213,297] y[34.5,55.9]` and `y[122.1,143.5]` `z[0,133.6]` |
| z[60, 140] | 28.01 mm | condenser ear columns |
| z[140, 267] | 14.06 mm | corner posts + Z/Y seam lips (front lip rim at **154.0**, `z_joint_front` 140.9) |
| z[267, 281] | 24.96 mm | back Z-seam lip band (`z_joint_back` **267.0** + `lip_len` 13.1 = 280.1) |
| z[281, 300] | 43.95 mm | rear-wall port bosses |
| z[300, 335.7] | none at ≤60 mm | **display facet back wall crosses the full width at y≈48–77**; Y-seam ceiling lip at y[220.3, 236.4] |

Ceiling is 335.7 but the facet's back wall is the real front bound of anything hung from it.

### 2. Ranked inventory

| # | volume | free dims | fits | bounded by | free today? |
|---|---|---|---|---|---|
| **1** | **FRONT MEZZANINE** x[5.9, 279.1] y[1.0, 88.8] **z[154.5, 194.0]** | **273.1 × 87.8 × 39.5** (23 973 mm²) | **PSU flat + PCBA flat + relay + DC block + 3 Wago + gnd stack, all at once** | floor: compressor-shroud 154.5 / condenser 154.0; ceiling: pump-a 194.0, pump-b 196.0; aft: source-select 164.8 at y≥89.1; sides: shell | **YES — `probe.py hits --x=5.9,279.1 --y=1,88.8 --z=154.51,193.99` → CLEAR** |
| **2** | **CEILING PLANE**, front column west of the funnel x[-14, 111.6] y[76.8, 198.5] z[292, 335.7] | 125.6 × 121.7 × 43.7 (15 283 mm²) | PSU flat, PCBA flat (both) | hopper-funnel x≥112.5; seaflo-pump y≥200; display-facet back wall y=76.6; ceiling 335.7 | **YES — `probe.py hits --x=-14,111.6 --y=76.8,198.5 --z=292.01,335.69` → CLEAR** |
| **3** | SERVICE BAY west column x[5.9, 95.6] y[174.5, 324.2] z[258.4, 291.9] | 89.7 × 149.6 × 33.5 — **but only y ≥ 200 has cap under it** (89.7 × 124.2 floored) | **exactly ONE of the two** | seaflo-pump x≥96, drip-pan-rails y≥326, bag-circuit, shell | YES, `hits` CLEAR — but see §3 |
| **4** | MACHINE CORRIDOR behind the compressor x[0, 52] y[140, 173.5] z[30, 139] | 52 × 33.5 × 109 | **PSU standing on end only** | compressor-shroud, foam-assembly, fluid-25 | YES — `probe.py hits --x=0,52 --y=140,173.5 --z=30,139` → CLEAR |
| 5 | pump low-crown window x[239.3, 283] y[221, 277] z[306.4, 335.7] | 43.7 × 56 × 29.3 | nothing whole | **occupied**: fluid-18 1773.5 mm³, fluid-28 1773.5 mm³, seaflo-pump 162.0 mm³ | NO — needs both nozzle runs re-routed |
| 6 | under-pump lane x[5.9, 79.7] y[174.5, 380] z[258.4, 271] | 73.8 × 205.5 × **12.6** | Wagos only | pump underside 271, cap 258.4 | yes, but too short |
| 7 | SeaFlo base-flange shelves (re-derived at the current pose) x≈102–187, y[200,221] and y[277,298], above **z = 266** | 85 × 21 × 64 | nothing | pump base flange | free, **still too shallow in Y — the earlier verdict survives the move** (`scratchpad/heightmap.py seaflo-pump 7`) |

Commands behind #1:
```
$ fit.py slab --z 154.5,194 --step 3
   311.0 ×   90.0 mm  (   27990 mm²)  x[  -14.0,  297.0] y[   -3.0,   87.0] z[154.5,194.0]
$ fit.py slab --z 154.5,188   --size 52,109    --step 3   -&gt; 1 rectangle, 311 × 90
$ fit.py slab --z 154.5,181.6 --size 90.82,73.3 --step 3   -&gt; 1 rectangle, 311 × 90
$ fit.py try meanwell-irm90 --bbmin=8,14,154.6 --yaw 90 --clearance 20
  meanwell-irm90 at (62.5, 40.0, 154.6) yaw 90  x[8.0,117.0] y[14.0,66.0] z[154.6,188.1]
    TIGHT compressor-shroud 0.10, pump-a 5.91      (both exact at clearance 20)
```
The PCBA is a printed part, so `fit.py try` cannot name it; I carried `pcba-assembly.step` under one `cq.Location` through `fit.Part.pose` and checked it with `fit.check` (`scratchpad/vc_all.py`). **All eight bodies placed simultaneously in #1 came back clear of the world, 0.000 cm³ into the shell, tightest pair 1.20 mm** (my layout is naive — 16 184 mm² of parts in a 23 973 mm² footprint, 33 % spare).

**Volumes large enough for BOTH: #1 and #2. Nothing else.**

### 3. The fence, measured

The service-bay west column holds one body, not two — verified with real solids:

- PSU flat, hard west/front `bbmin=(2,201,258.4)` → x[2,54] y[201,310] z[258.4,291.9], **no clash**, resting on the cap.
- PCBA **north** of it `bbmin=(2,312,258.4)` → **CLASH drip-pan-rails 1700 mm³ + drip-pan 22 mm³ + 1.864 cm³ of shell**.
- PCBA **east** of it `bbmin=(56,201,258.4)` → **CLASH seaflo-pump 20 393 mm³**.

So the re-layout of the water deck bought room for one of the two. The other has no home there.

### 4. The reframing (bosses, not trays) — where roots can land

Distance from each mounting point to printable material (`scratchpad/roots.py`, exact solid distances):

| candidate | mounting points | to printed shell | to foam-cap assembly |
|---|---|---|---|
| #1 PSU in the mezzanine | 33 × 98 rect | **16.85 / 23.46 / 24.46 / 56.45 mm** | 143–176 mm |
| #1 PCBA in the mezzanine | MH1–MH4, 78 × 66.3 | **17.46 / 17.46 / 58.90 / 83.75 mm** | 116–182 mm |
| #2 PCBA hung from the ceiling | MH1–MH4 at z=335.7 | **0.00 / 0.00 / 0.00 / 0.00 mm** | 92–140 mm |
| #3 PSU / PCBA on the cap | either pattern | 12–77 mm | **0.00 mm all four** |

This is the honest cost of #1: **its floor is components, not printed material.** `probe.py cast` down from z=154.4 hits `compressor-shroud` at 0 mm over x≈14–192 and `condenser+fan` over x≈213–269 — both **cut-parts / placeholder, not printed** — with a 143 mm shaft at x≈200 and open shafts at x&lt;14 and x&gt;269. Four boss roots in the mezzanine mean either a rail spanning the front-top piece's ±X walls or a cantilever off its front wall, longest unsupported reach **83.75 mm**. #2's roots are free; #3's roots are free and already in the idiom (the drip-pan rails are VHB'd to that same lid, and `hardware/printed-parts/cold-core/foam-cap` is a genuinely printed part — `foam-cap-lid-top.step`).

**A finding that falls straight out of the reframing:** the PCBA tray floor is 8.00 mm of the assembly's 27.10 (`pcba-tray.step` 85.00 × 73.30 × **8.00**; everything above the tray's top face = **19.10 mm**). Deleting the tray and rooting the four bosses in the cap lid drops the crown:

| mount | crown | vs the 283.605 lane ceiling |
|---|---|---|
| tray flat on the cap, as built | 285.50 | **OVER by 1.90** |
| bosses in the lid, 3 mm standoff | 280.50 | OK by 3.10 |
| bosses in the lid, 5 mm standoff | 282.50 | OK by 1.10 |
| bosses in the lid, 8 mm standoff | 285.50 | OVER by 1.90 |

### 5. Constraints folded in

- **Crown ceiling 283.605** (`_lines.py:470-481`; I read it — the `crossings` list carries `f["pcba"].bb.zmax` with **no X/Y overlap test**). #1 crowns at **188.10 (PSU) / 181.70 (PCBA)** — passes by ~100 mm. #2 crowns at 327–335.7 — **trips the check**, though the runs it guards (fluid-18/28) live at x ≥ 199 and #2 is at x ≤ 111.6, so that failure is the bbox artifact, not a real interference. #3 needs the boss-mount above.
- **Cap-datum uncertainty ±4 mm.** #1 and #4 are **immune** — they sit below z=194 and touch nothing cap-borne. #3 is **not**: `UMBILICAL_Z_FLOOR = 281.0` is a hand-set constant off `z_joint_back`, so the lane deck does *not* rise with the cap. At a 262.40 datum the PCBA crown goes 285.50 → 289.50, and even 3 mm bosses land at 284.50 — **still over**. #3 dies at 262.40; #1 does not.
- **CO2 keep-out** — taking your latest correction: the bore is at (141.5, 363.25), rear of the cap. None of my ranked candidates touch that column. #1 and #4 are nowhere near it.
- **Board edge access (USB-C west / J10 east, unmodeled).** #1: both edges in open air, nearest material ≥17 mm — fine geometrically, but service access is *bad*: the mezzanine is inside the front-top piece with the pump row and tray stack 39 mm overhead. #3: west edge ~2 mm off the shell, **east edge 1.69 mm off the seaflo-pump** — J10's screw throats are unreachable. That is a service defect nothing in the build reports.
- **Thermal (my judgment, not a measurement):** #1 puts the PSU 0.10 mm off the compressor shroud and the PCBA 0.60 mm off the condenser — directly in the hot stratum, in the condenser fan's cross-flow. This is the strongest argument against #1 and I have no measured basis for sizing it.

### 6. Two instrument traps worth knowing

- `fit.slab --exact foam-assembly` reports **15 502 mm² free at x[93.7,189.3] y[210,372] z[154.5,194]** — that is the cold core's *insulated interior*, not usable space. `--exact` on a vessel reports its contents as air.
- The as-built power tray (151.10 × 73.94 × **40.50**) does **not** fit in #1: at the shroud floor it clashes `pump-a` by 601 mm³, missing by ~1.1 mm of height. The PSU alone, and the tray re-laid-out under 39 mm, both fit.

Nothing in the repo was edited; all scratch work is in the session scratchpad (`census3.py`, `shell_profile.py`, `roots.py`, `vc_all.py`, `heightmap.py`).</result>
<usage><subagent_tokens>253436</subagent_tokens><tool_uses>103</tool_uses><duration_ms>2339872</duration_ms></usage>
</task-notification>

---

# Assistant

---

All four in. The census overturned the fence — but not in the direction anyone expected.

**The single largest free volume in the machine is not the cap.** It's the **front mezzanine** over the refrigeration floor — x[5.9, 279.1] y[1.0, 88.8] **z[154.5, 194.0]**, 273 × 88 × 39.5, verified CLEAR — and it holds **all eight bodies at once** (PSU, PCBA, both relays, DC block, three Wagos, ground stack) with 33% spare, 0.000 cm³ into the shell, tightest pair 1.20 mm. Nothing has to move.

Its problem is thermal, and it's disqualifying: that pose puts the PSU **0.10 mm off the compressor shroud** and the board **0.60 mm off the condenser**, in the fan's cross-flow. It's the hot stratum. Also its floor is *components*, not printable material — boss roots need an 83.75 mm cantilever off the front-top piece.

The census also settled your column, with solids:

- PSU flat at x[2,54] y[201,310] — **no clash**, seated on the cap
- PCBA north of it — **CLASH** drip-pan-rails 1700 mm³ + shell 1.864 cm³
- PCBA east of it — **CLASH** seaflo-pump 20,393 mm³

**The west column holds exactly one of the two.** The re-lay bought room for one body, not the pair.

And one finding that outranks everything else here: **the column dies if the datum is 262.40.** `UMBILICAL_Z_FLOOR = 281.0` is hand-set off `z_joint_back`, so the lane deck does **not** rise with the cap. At a 262.40 cap top even 3 mm bosses put the crown at 284.50 — still over the 283.605 ceiling. The mezzanine and the corridor are immune (both below z=194); your column is not.

So the 1.105 mm margin isn't the question. **The datum is.** Resolving it before anything else.

---

# Assistant

---

Datum resolved — and the alarm was false.

`build_foam_cap_lid()` extrudes `wall_and_floor_thickness` = **2.0 mm**, and `gasket_thickness` = **2.0 mm**. The two stacks include different parts but land on the same Z:

- **CAD** ([foam_assembly.py:92](hardware/printed-parts/cold-core/foam-assembly/foam_assembly.py:92)): shell → cap → **lid on the cap's mouth** (`zmin = cap_top.zmax`). Top = shell + cap_h + 2.0
- **Shipped** (`_cold_core_sync.py:117`, [bom.md:150](hardware/ledger/bom.md:150)): shell → **gasket 2.0** → cap, **no lid** — it's pour tooling that doesn't ship. Top = shell + 2.0 + cap_h

Identical. **258.40 stands, and the 1.105 mm margin with it.** The "262.40" case needs the lid to both ship *and* stack, and it does neither.

Better than that: in the shipped machine the surface at 258.40 is **the cap's own top face** — not the lid. So your idea lands on the part that already carries six Ø8 through-columns, and the lid/cap ambiguity in your original phrasing resolves itself in favour of the part that works.

(One latent bug for later: the CAD models a part that doesn't ship and omits one that does. They cancel in Z, so nothing downstream is wrong today. And `_cold_core_sync.py:117`'s "the lid nests in the cap mouth" is false — it's a full-footprint plate that cannot nest.)

Landing the two free fixes the survey turned up, starting with the mains one.

---

# Assistant

---

Geometrically identical (43.0541 cm³ both), and the AC block flips from −54.5 mm (the tray's empty west end) to +54.5 mm — 109 mm toward the Wagos it feeds. Now the dedupe.

---

# Assistant

---

Gates pass, and the denominator is fixed (`12/36`, was `/37`). Now the build I'll commit — no skip flags, per `CLAUDE.md`.

---

# Assistant

---

7/7 with clearances measured. Committing.

---

# Assistant

---

Git shows only build artifacts — my source edits aren't listed. Checking.

---

# Assistant

---

HEAD already contains both changes. Something moved under me — checking whether another session is active.

---

# Assistant

---

Another session committed `b62f30c4` mid-flight. Checking whether it swept up my edits.

---

# Assistant

---

Found it — and it's worth flagging.

**Another session is active in this repo right now.** It committed `b62f30c4` ("cards: a band holds its own content…") while I was working, and that commit **swept up both of my uncommitted edits**. The `psu_rot: 90 → 270` change and the `discharge-chain` dedupe are in `origin/main` — attributed to a commit whose message is entirely about card rendering and mentions neither.

So both fixes are landed and pushed, just filed under the wrong heading. Nothing is lost. But its commit is a blanket `add`, so anything I leave uncommitted gets absorbed into whatever it does next.

My rebuilt artifacts are still dirty and HEAD's don't reflect the dedupe. Landing those now so HEAD is self-consistent.

---

# Assistant

---

Committed and pushed, hooks green.

## Where the survey landed

Four agents, four fences, ~950k tokens. The net:

**Your idea is verified and it's the only thing that fits.** PCBA yawed 90° on **cap-rooted columns** at x[11, 84.3] y[208, 298.82], board underside 263.40 — `hits` CLEAR of the world *and* all four printed enclosure pieces, both connector edges facing open Y-lanes. Crown **282.50** against the 283.605 lane ceiling. The tray's 3 mm floor is exactly what breaks it; deleting the tray is what makes it legal.

**The cap is the right root, and it already does this.** `build_foam_cap()` unions six Ø8.0 columns spanning the full 18 mm cap height with foam poured around them. Four more on the board's 78.0 × 66.3 pattern is the same operation, printing floor-down off the bed. (Your "lid or cap" — it has to be the cap. The lid is a 2 mm pour clamp that `bom.md:150` says doesn't ship.)

**The column holds one body, not two.** Verified with solids: PCBA north of a seated PSU clashes the drip-pan rails by 1700 mm³; east of it, the pump by 20,393 mm³. So the PSU needs its own home.

**The biggest volume in the machine isn't the cap** — it's the front mezzanine, z[154.5, 194.0], 273 × 88 × 39.5, which holds *all eight* electronics bodies at once with 33% spare and nothing moved. It's disqualified on thermal: that pose sits the PSU 0.10 mm off the compressor shroud and the board in the condenser fan's cross-flow. Worth knowing it exists.

## The one thing I want your call on

The board must sit low to clear the lane gate — which is why it takes the cap column and the PSU goes elsewhere. **But that gate is over-broad by its own documented intent.** [_lines.py:474](hardware/printed-parts/enclosure/enclosure-assembly/_lines.py:474) tests the board's *global* bbox zmax with no X/Y overlap check, while its comment says it measures "against every placed part it **crosses**." `fluid-18`/`28` run at x ≥ 199; the west column is x ≤ 96. They never meet.

Fixing that check is defensible on the merits — but it also happens to unlock poses for me, so I'd rather do it as its own change with the reasoning visible than quietly bundle it into a placement. Two paths:

**(a) Leave the gate alone.** Board on cap columns in the west column — your vision exactly, passes as-is, no gate touched. PSU rehomed separately.

**(b) Narrow the gate to an X/Y crossing test first**, then place both freely — which reopens the ceiling plane and two-level arrangements that are currently excluded by an artifact.

I'd take **(a)** and do (b) later on its own merits, because (a) delivers the thing you asked for without me editing a check to suit myself.

One operational note: the other session commits with a blanket `add`, so I'll land work in small increments rather than leaving anything sitting in the tree.

---

# User

---

> (b) Narrow the gate to an X/Y crossing test first, then place both freely — which reopens the ceiling plane and two-level arrangements that are currently excluded by an artifact.

This sounds strictly better to me, please do it.

---

# Assistant

---

The user chose (b). Reading the check and the lanes it guards before I touch it.

---

# Assistant

---

Now I understand the geometry. The deck legs run at `outer_x` = 274.175 and `inner_x` = 248.125, from the elbows' pocket columns aft to their climb — the west column is nowhere near them. Three edits.

---

# Assistant

---

Now the build — first confirming no regression, since the board isn't placed yet.

---

# Assistant

---

7/7, both lanes route byte-identical. Now the known-answer control — the guard must still fire when a board really is under a lane.

---

# Assistant

---

All four controls behave. The guard now discriminates on **position**, not just height — and still catches the real case:

| synthetic board | crown | result |
|---|---|---|
| west column | 285.50 (over ceiling) | **routes** — previously raised |
| west column | 282.50 | routes |
| **under a lane** | 285.50 | **RAISES** ✓ |
| under a lane | 275.00 | routes |

Full build and commit.

---

# Assistant

---

Landed as `1066d190` — and note git showed only `_lines.py` changed, no geometry moved. The gate is now a position test.

That reopens the two-level and ceiling arrangements. Measuring the PSU's seat in the west column before I choose between them.

---

# Assistant

---

PSU seats clean at y[240, 349] — aft, under the C14, touching only the cap it sits on. Now the board above it.

---

# Assistant

---

Gate landed. Now the measurements that decide the arrangement:

| pose | result |
|---|---|
| PSU flat, x[2,54] y[250,359] on the cap | clear, >6 mm to C14 (touches only its seat) |
| PSU at y[270,379] | **CLASH** c14-inlet 234 mm³ |
| board yaw 90, x[11,84.3] y[205,295.8] **z[300, 319.1]** | **CLEAR** |
| board same footprint at z[263.4, 282.5] (on the cap) | **CLEAR** |

So both two-level and board-on-cap are now available — the gate was the only thing forbidding the latter.

One thing the geometry says that's worth surfacing before I build: **the board's four posts and the PSU fight for the same cap.** Board bosses sit on a 78.0 × 66.3 rectangle; the PSU occupies x[2,54] × 109 deep in a column only 126 deep. Every arrangement I tried puts at least one post inside the PSU's footprint. Side-by-side doesn't rescue it either — PSU on its 52-face (33.5 wide) plus the board's 73.3 is 106.8 against 96 of column.

So the two genuinely don't share the cap. I'm going to land them as separate increments rather than stall one on the other:

**Now:** board on four short cap-rooted bosses at x[11, 84.3] y[205, 295.8], underside 263.4, crown 282.5 — your vision exactly, verified clear, and legal now that the gate tests position. That means authoring the boss columns into `foam-cap` (which already unions six Ø8 columns through its full 18 mm height, so it's the same operation), adding the missing `_c(...)` registry entries, placing it with `_at`, and re-deriving the port table from the pose instead of the fossil literals.

**Next:** the PSU, with the board placed and constraining it. The live candidates are ceiling-hung above the board (53.2 mm of headroom over the board's crown, roots free off the bed, but it inverts assembly order and hangs 219 g), or out of the bay into the machine corridor.

Starting on the board.

---

# User

---

Please proceed.

---

# Assistant

---

Before I put mounting features on the cap's top face, I need to know which part actually owns that face — the lid/gasket inconsistency bites exactly here.

---

# Assistant

---

Measured, and it's a genuine blocker for the boss work:

```
foam-shell           world z[ 25.00, 238.40]
foam-cap-top         world z[238.40, 256.40]
foam-cap-lid-top     world z[256.40, 258.40]   <- the surface at 258.40
```

**In the CAD, the face everything rests on at 258.40 belongs to the pour lid — the part that doesn't ship.** The cap's own top is at 256.40. In the shipped machine (gasket under the cap, no lid) the cap's rim *is* 258.40, so the envelope is right and nothing downstream is wrong — but I can't author boss columns onto a face the model gives to the wrong part.

So I'm splitting it: **place the board body now** (visible in the 3D you review, and it makes the registry gaps concrete), and author the cap columns after fixing the foam stack. Reading the placement idiom.

---

# Assistant

---

Clear. Implementing the placement — constants, a pose-derived port accessor so the table can never decouple again, and the registry entry.

---

# Assistant

---

Placement and port map both resolve. Now the scorecard — registry entry and the port table off the pose.

---

# Assistant

---

Predicted exactly — the tray seats on the cap, which is a declared contact like the pump's.

---

# Assistant

---

7/7 gates, and `located` moved **86% → 89% (33/37)** — the 13 board ports now resolve on the real solid, which is the proof the pose-derived map is right.

---

# Assistant

---

Landed. Sending the render so you can look rather than read.

---

# Assistant

---

Three commits in, all 7/7 with clearances measured:

| | |
|---|---|
| `1066d190` | the lane gate now tests **position**, not just height |
| `08e353ea` | **the board is placed** — x[11, 84.3] y[205, 295.8] on the cap |
| earlier | scorecard denominators, `psu_rot` mains flip |

The board turned out to have had a colour, a STEP path and fourteen ports but **no placement at all** — the pack didn't know it existed. Its port table was thirteen world literals carrying a transform solved two re-lays ago, pointing into the middle of the pump; they scored `off-surface` only because no solid was there to miss them. Those are now `pcbX`/`pcbY` verbatim from `pcba.tsx` run through `contents.pcba_port`, so moving `PCBA_POS` moves the whole map with it. `located` went **86% → 89%** as the thirteen resolved onto the real board face — that's the check that the pose is right, not my arithmetic.

Orientation is a quarter turn so the two edges that must stay reachable face lanes instead of walls: **USB-C south** into the open band ahead of the cap (you flash J14 with the back panel on), **J10 12 V north** up the strip.

## Two things still open

**The mount.** It's still the 3 mm tray, not cap columns. I stopped short because of what I measured on the way: in the CAD the surface at 258.40 belongs to `foam-cap-lid-top` — the pour lid that `bom.md:150` says doesn't ship — while the cap's own top is at 256.40. The envelope is right (gasket-under-cap and cap-plus-lid both total 253.40), so nothing downstream is wrong, but I won't author boss columns onto a face the model hands to the wrong part. Fixing the foam stack to model what ships is the prerequisite, and it's a cold-core change rather than an electronics one. Dropping the tray also drops the board 3 mm, to crown 282.50.

**The PSU.** It doesn't share the cap with the board — every arrangement puts at least one of the board's four posts inside the PSU's footprint, and side-by-side is 106.8 mm against 96 of column. Live candidates are ceiling-hung above the board (53.2 mm of headroom, roots print free off the bed, but it inverts assembly order and hangs 219 g) or out of the bay entirely into the machine corridor, which `hits --x 0,52 --y 140,173.5 --z 30,139` reports CLEAR.

One operational note: the other session committed `b62f30c4` mid-session and swept two of my uncommitted edits into it, so I've been landing in small increments since. Worth knowing if you see the `psu_rot` change filed under a card-rendering commit.
