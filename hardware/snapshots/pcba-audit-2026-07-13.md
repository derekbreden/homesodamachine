# PCBA production-readiness — Snapshot 2026-07-13

**This is a point-in-time snapshot, not a living document.** Board state: commit `ec664903`, rendered 2026-07-13. Re-running this audit later produces a fresh dated file against the then-current board.

## TL;DR

- Render gates **12/12 pass** (clearance floor 0.14 mm, 0 opens, 0 DRC errors), 100 % score (128 pcbPath, 0 auto, 0 deferred), 92/92 parts carry a JLCPCB #. Paste coverage 363/363 top-side SMD pads.
- A fresh-eyes pass over the 2026-07-11 board (thermal, DFM, external-interface protection) found **one fab blocker** and a set of protection/robustness gaps the earlier audit had not reached. This snapshot records the board with them resolved and lists the residual bench and DFM items.
- **Fab blocker (resolved):** the exported solder-paste layer covered only rect pads — 148 of 330 top-side SMD lead pads (all gull-wing SOIC/SSOP leads across U2/U3, U4/U5, U6, U7, U11/U12, U13) had **no paste aperture**. A stencil cut from that layer would place nine ICs on paste-free pads. The `circuit-json-to-gerber` fork now derives F_Paste from `pcb_smtpad` copper, and a `paste-coverage` gate holds it.
- **Protections now on the board:** reverse-polarity P-FET + surge clamp at the J10 12 V inlet; a firmware-independent gas→compressor interlock; a buzzer flyback clamp; faucet-UART series backstop + IO25 flow-input hardening; J4/J7 anti-misplug keying; three assembler fiducials.
- **Residual:** bench-gated polarities/thermals (below) and a handful of cosmetic silk items. *(The faucet-end ESD TVS once listed here as a residual moved on-board later 2026-07-13 — D10/D11 shunt clamps at U1, commit `a8f55a44`; see the Faucet UART section.)*

## Source-data state

- `hardware/pcb/pcba/pcba.tsx` at `ec664903`; `out/pcba.circuit.json` from `bun render-board.ts pcba.tsx` on 2026-07-13.
- Fork `circuit-json-to-gerber` at `2329112` (branch `homesodamachine/through-hole-vias`), consumed via the `overrides` git dependency.
- Off-board loads read from `wiring/ac-wiring-schedule.md`, `wiring/power.mmd`, `hardware/topology/fluid-topology.md`, `ledger/bom.md`, `hardware/future.md` (§Safety, §User-facing).

## Methodology

Three parallel read-only passes over the 2026-07-11 board — thermal/power-integrity (per-part dissipation against documented loads), DFM (paste, exposed-pad/via stitching, fiducials, Z-height/mating, silk), and protection/external-interface (input protection, ESD matrix, misplug, antenna keepout) — then a placement study measuring free space for the resulting additions, then implementation region-by-region against the render scorecard. Each protection circuit was traced pad-by-pad in source, not taken from a summary.

## Changes this pass

| # | On the board | Part(s) — LCSC | Commit |
|---|---|---|---|
| 1 | F_Paste derived from copper + `paste-coverage` gate | (fork + scorecard) | `730ec972`, fork `2329112` |
| 2 | D7 buzzer flyback clamp across the MLT-5020 coil | 1N4148W SOD-123 `C81598` | `ed9c7713` |
| 3 | R21/R22 IO25 flow-input hardening (1 k series + 4.7 k pull-up) | `C11702`, `C25900` | `0544a76e` |
| 4 | J7 REEDS-B keyed to JST-EH (non-intermating with the XH SENSORS loom) | B7B-EH-A `C160254` | `c81e34e7` |
| 5 | Q4 reverse-polarity P-FET + D8 surge clamp + D9 Vgs zener + R23 gate pulldown | AO3407 `C181093`, SMAJ15A `C571368`, BZT52C15 `C173427`, 100 k `C60491` | `59932118` |
| 6 | U15 gas→compressor interlock + R24 pulldown + R25 invert-select + C23 decoupler | 74LVC1G08 `C12512`, 100 k `C60491`, 0 Ω `C17168`, 0.1 µF `C1525` | `261f6cb3` |
| 7 | FID1–FID3 global fiducials (1 mm copper dot) | (bare-copper features) | `7eb423ef` |
| 8 | R26/R27 faucet-UART series backstop (IO33/IO35) | 220 Ω 0402 `C25091` | `9df5986f` |
| 9 | Faucet-end ESD TVS specified at the display connector (docs) | (cable-assembly spec) | `ec664903` |
| 10 | On-board faucet-UART ESD — 2× shunt clamps at U1.IO33/IO35 (supersedes #9 as primary; same day) | ESD9B3.3ST5G SOD-923 `C96512` | `a8f55a44` |

*(Change #4 was reversed 2026-07-14, `20b6efb5`: J7 unified back to XH2.54 7P — the same wafer as
J4 — trading the EH keying for a one-family connector BOM; the misplug guard is now loom labelling,
per `assembly/cable-assemblies.md`.)*

## Protection circuits — as-built (traced in source)

- **Reverse-polarity block (J10 inlet).** `pcba.tsx:1532-1541`. J10.V12 → `net.V12IN` → Q4 **drain**; Q4 **source** → the V12 island; gate → R23 (100 k) → GND; D9 (15 V zener) cathode→source / anode→gate; D8 (SMAJ15A) island→GND. A P-channel body diode points drain→source, so with drain=inlet / source=load it conducts inlet→load in normal polarity (channel then enhances, Vgs ≈ −12 V within the AO3407 ±20 V rating) and blocks load→inlet under reverse polarity. The drain stub carries the ~3.3 A board peak on 1.6 mm copper (ampacity rule `pcba.tsx:312`, gate: 0 narrow). D8 clamps to 24.4 V, under C3's 25 V rating.
- **Gas→compressor interlock.** `pcba.tsx:110-123, 939-961, 1120-1193`. U15 (74LVC1G08 AND). A ← U1.IO19 (firmware compressor command); B ← the divided MQ-6 DOUT node (the ~3.0 V node that also feeds IO36) through R25 (0 Ω invert-select), with R24 (100 k) pulldown **at the gate**; Y → J5.IO19. U1.IO19 and J5.IO19 are separate nets — the ESP reaches the relay only through the gate. Y = A·B → `(IO19, gas) → J5.IO19: (on, clear)→ON, (on, GAS)→OFF, (off, *)→OFF`. Fail-safe: R24 defaults B low, so a broken B-haul, an unpowered/unprogrammed ESP (A low), or an unpowered gate all leave the compressor off. Assumed bench-gated polarities: MQ-6 DOUT HIGH = clear, relay active-HIGH. Invert provisions carried: R25 (0 Ω) in series on B for DOUT polarity; a pin-identical 74LVC1G00 NAND (`C12508`) drops into the same SOT-353 land for an active-LOW relay.

## Thermal (computed; inputs stated — worth bench-verifying at the 40–55 °C shelf ambient, not a 25 °C bench)

- **ULN2803 U4/U5** are the hottest nodes. U4 at 3 simultaneous MANIFOLD-A valves: 3 × 0.46 A × 1.3 V ≈ 1.8 W cold-inrush, settling to ~1.0 W as coils warm; SO-18 θJA ≈ 57–73 °C/W → Tj ≈ 97–113 °C settled and ~140–170 °C during the first seconds of a fill (transiently over the 150 °C limit). U5 (2 valves + the condenser fan on ch5) ≈ 1.1 W settled but fan-warmed **whenever the compressor runs**. Neither part has thermal shutdown. Worth a U4/U5 temperature measurement during a hopper fill and during compressor-on. Fill-state duration is undocumented (`ac-wiring-schedule.md`).
- **DRV8870 U11/U12** exposed pad reaches the GND plane through a single 0.3 mm via (the inner planes are 3V3/5V, not GND; the top V12 island antipads the EP). ~0.5–0.7 W per driver during prime → Tj ~90–140 °C at 40 °C ambient. The part's own 150 °C thermal shutdown backstops it; prime is user-initiated and intermittent. Worth a prime-cycle temperature check.
- **AMS1117 (U9)** 3V3 LDO: 3V3 tally ≈ 90–100 mA, drop 1.7 V → ~0.18 W typ / ~0.29 W at peak, tab θJA ~60–90 °C/W → ΔT ~13–20 °C. Comfortable.
- **K7805** 5 V rail: typical ≈ 0.64 A, worst-case ≈ 1.3 A of its 2 A. Comfortable. The faucet-display 5 V current is the one unmeasured term (even 400 mA stays < 1.5 A).

## Verified consistent / cleared this pass

- The ~5 A SeaFlo diaphragm pump is switched entirely off-board (12 V block → relay #2 → pump); the board sources only the 3.3 V gate (IO2 via J5). No board copper carries it (`ac-wiring-schedule.md:76-79`, `power.mmd:66-68`).
- Bulk/local decoupling holds: each DRV8870 has 10 µF + 0.1 µF local, each ULN a local 0.1 µF, C3 (470 µF/25 V) at board centre feeds the island; valve turn-on is slow (coil L/R ~ms), pump inrush is bridged by the locals + C3 until the 6.7 A supply responds.
- Every capacitor's rated voltage ≥ 2× its rail; the tightest are C3/C15/C17/C19 at 2.08× (25 V on the 12 V island). No cap under 2×.
- Every XH/EH connector opening faces its nearest board edge — looms exit off-board (rotated-courtyard geometry, `component-bodies.ts`). J14 USB-C insertion and J10 top-actuated screw access clear.
- Via-in-pad is POFV (epoxy filled & capped) throughout; no plain via in a pad; annular rings meet JLCPCB DFM.
- Antenna keepout (x[−68.5, −67]) is clear on all three pours and DRC-enforced against signal copper (`clearance.ts`), verified after the IO23 and Q2.C→EN reroutes.
- The mains AC (compressor) is switched off-board through an opto-isolated relay module — only low-voltage control leaves J5. No mains on the PCBA.
- The raw circuit-json DRC "errors" (pad-pad / trace / placement) are tscircuit's unrotated-bounding-box checker against the default centred outline — false positives; the project's own 0.14 mm gate passes.

## DFM notes (passing, flagged for the fab review)

- **Courtyard advisory:** Q4–C5 −0.084 mm and J10–Q4 −0.058 mm — below IPC-7351 nominal (0.25 mm) but copper clears at the 0.14 mm floor and the connector-body gate reports 0 flagged. The SOT-23 sits in the 3.6 mm slot west of J10 by design.
- **Clearance floor 0.14 mm** at the interlock's DOUT inner2→bottom transition via (between IO23's inner1 descent and the IO15→R10 feed) — the board's tightest point; at the gate floor, above JLCPCB's 0.127 mm process minimum.
- **Fiducials:** FID1 (15, −28.3) and FID2 (16, 27.5) sit inside the V12 island, which antipads ~0.5 mm around each netless dot — below JLCPCB's ideal 1 mm fiducial keep-ring (the island floods the east corners). FID3 (−59.5, −34.8) is on open laminate.
- **Silk (cosmetic, open):** 303/309 silk paths are < 0.15 mm line width (0.10 mm imported outlines, 0.12 mm hand-drawn passive marks); D2–D6 status LEDs carry no polarity mark (orientation on CPL + badge only); C3's ref-des sits under its own can. None affect fab; first-article polarity check for D2–D6 rests on CPL.
- **Stock:** U15 `C12512` ~1.3 k (Extended); watch at order time. Prior shallow rows still stand — C3 470 µF, COS13487, J1 9P wafer, DS3231.

## Bench-verify list (source review cannot settle these)

- MQ-6 DOUT trip polarity and relay-module trigger polarity (set the interlock's R25 / NAND-swap provisions).
- Reverse-protection FET sustained current during a dual-pump prime (SOT-23 thermal; step to SOT-89/SOIC-8 — which needs +3 mm — only if it holds near 3.3 A for seconds).
- U4/U5 junction temperature during a hopper fill and during compressor-on, at shelf ambient.
- DRV8870 EP temperature at prime.
- Relay-module 3.3 V drive margin (boot-safety assumes the opto LED load holds IO2 low); MQ-6 DOUT polarity into the interlock; COS13487 DI idle behaviour in ESP reset; solenoid hold current (`ac-wiring-schedule.md:84`, 0.3–0.46 A "measure at bring-up").
- DIGITEN flow output stage: resolved from the datasheet as open-collector (`bom.md:184`), so IO25 swings 0–3.3 V on the ESP pull-up; R22 now pins it firmware-independently. No longer a pre-fab unknown.

## Faucet UART (SIG-6) — two-tier protection

The faucet display is a stock Waveshare ESP32-S3-Touch-LCD-1.47 on a ~1 m umbilical TTL UART to non-5V-tolerant IO33/IO35 — the user-touched external interface. J3's connector housing covers the pin-side laminate, so an on-board TVS at the connector does not fit. As built:

- **Driver-end backstop (this board):** R26/R27 (220 Ω) in series on IO33/IO35 — ESD current limiting into the ESP clamp diodes and edge damping for the 1 m line.
- **Primary ESD (cable assembly):** 2× low-capacitance ESD TVS (ESD9B3.3-class, SOD-923) from IO33 and IO35 to GND at the faucet-display connector end of the umbilical — protection at the user-touch source. Specified in `assembly/cable-assemblies.md` (SIG-6) and `assembly/faucet-and-umbilical.md`.

**Resolved later 2026-07-13 (`a8f55a44`):** the primary clamp moved on-board. D11 (ESD9B3.3ST5G, `C96512`) shunts IO35→GND at R27.pin1 beside the U1.IO35 pad (−58.67, −9); D10 shunts IO33→GND at R26.pin1 (the 220 Ω output — the IO33 pad rim is boxed by the C10/C11 module-cap courtyards and the IO33/IO34 drop column at x −56.5). Both top-side (single-side assembly preserved), each GND pad a via-in-pad straight to the plane, board outline 85.05 × 72.85 unchanged, gates 12/12. R26/R27 remain the series element of the on-board clamp; the cable-end TVS drops to optional defence-in-depth. `cable-assemblies.md` and `faucet-and-umbilical.md` now carry the on-board topology as primary.

## Firmware ↔ board

Unchanged from the 2026-07-11 snapshot and out of scope for this pass: `firmware/src/main.cpp` is the L298N prototype's; the port encodes the interlock's assumed polarities, the GPPU enables, the ≤3-valve simultaneity, and the refill interlock. The board's wiring is self-consistent and boot-safe; nothing exercises it until a board exists.

## Later 2026-07-13 — independent re-audit (F1 PPTC + order spec)

A fresh independent audit re-ran against this board (fitness-for-purpose + JLCPCB manufacturability),
took the gerbers through a byte-level parse + per-layer render (**clean — no blocker; both prior
toolchain bugs, the empty pill-pad paste and the D70 silk-aperture collision, confirmed fixed in the
output**), and added:

- **F1 — 12 V-inlet resettable PPTC** (`SMD1812P200TF16`, `C20812`, 1812, **2 A hold / 4 A trip / 16 V**,
  100 mΩ post-trip), in series at the inlet ahead of Q4: `J10.V12 → net.V12RAW → F1 → net.V12IN → Q4.D →
  V12 island` (traced in source, `pcba.tsx:1728-1733`; V12RAW and V12IN are separate nets bridged only by
  F1 — no bypass). Closes the sustained-fault band the 6.7 A Mean Well supply ignores (a partially-shorted
  valve/pump coil, a stalled Kamoer, a chafed 12 V loom drawing between the ~3.3 A board peak and the
  6.7 A OLP) and protects Q4 (no forward-overcurrent limit of its own) + the V12 copper; auto-recovers, so
  a transient fault is not a dead unit. D8 (SMAJ15A) relocated to the open V12 island by C1/C2 to free the
  slot — still island(V12)→GND. **No board growth (85.05 × 72.85), GATES 12/12.** Commit `76c80142`.
  (Extended, ~33 k stock; no 2 A-hold SMD PPTC is Basic.)
  *(F1 was dropped the next day, 2026-07-14, `5193b708`: the Mean Well supply's own 6.7 A OCP bounds
  inlet overcurrent, so the inlet protection is Q4 + D8 and the board carries no fuse.)*
- **[`order.md`](/hardware/pcb/pcba/order.md)** — the JLCPCB order-form parameters not encoded in the
  gerber/BOM: **POFV epoxy-filled-&-capped vias (must-select — 89 vias are via-in-pad)**, ENIG finish,
  4-layer stackup / 1.6 mm / 1 oz outer, SMT-top + THT assembly, the two gerber-preview sanity checks
  (USB-C cutouts render as slots; corner holes plated), and panelization.
- **Stock-risk / designated second-source checklist** in `pcb/pcba/jlcpcb-parts.md` — the shallow
  Extended parts (C3 ~91 the tightest, plus DS3231, COS13487, SMAJ15A, 74LVC1G08, XH-9P) each get a
  fallback; ~28 unique Extended parts = 28 stock dependencies to re-verify the week of ordering.
- **`FORKS.md`** corrected — the `circuit-json-to-gerber` fork carries the F_Paste-from-copper fix (not
  just the Hershey font), so reverting it to upstream reintroduces the 9-unpasted-IC bug; the
  capacity-autorouter fork is dormant (board is 100 % hand-routed).

**Reaffirmed open (the one real fitness gate):** the **ULN2803 U4/U5 thermal** measurement on a
first-article board, at the 40–55 °C shelf ambient (not a 25 °C bench) and at real fill durations — U4
transiently exceeds Tj(max) at cold-inrush and U5 runs continuously fan-warmed, neither with thermal
shutdown. Deferring it is acceptable **only if the measurement actually happens before committing to
production**. Minor: the gas-interlock fail-safe covers a broken/unplugged sensor but not an MQ-6 drifted
to a false "clear" (a defense-in-depth layer whose primary safety is the low charge + shroud).

## What this snapshot is NOT

- Not the board's requirements — that is `pcb/pcba/requirements.md` and its scorecard.
- Not maintained going forward. **Re-running this audit produces a fresh dated snapshot rather than editing this one.**
