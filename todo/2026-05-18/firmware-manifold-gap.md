# Firmware ↔ integrated-manifold gap (unit #1 readiness blocker)

**Author:** hourly agent, 2026-05-18
**Status:** recommendation only — not for direct execution
**Audience:** future agents, Derek

## TL;DR

The hardware side of unit #1 is design-complete and procurement-ready (~$619 to provision per [build-readiness-2026-04-26.md](../../hardware/build-readiness-2026-04-26.md)). The firmware is *not* — it still drives the 4-valve prototype topology (2 dispense + 2 clean solenoids on three L298Ns) and openly says so in code:

> // Prototype valve topology (2 dispense valves + 2 clean solenoids on L298N
> // drivers). The integrated-appliance manifold is described in
> // hardware/topology/fluid-topology.md and is not yet implemented here.
> — [firmware/src/main.cpp:16](../../firmware/src/main.cpp)

When unit #1 is built, none of the following will work out of the box: Fill from Hopper, Fill from BiB, Clean Water Fill, Clean Flush, **the requirements-mandated air-purge phases of the cleaning cycle**, or termination-by-level-sensing on any fill or clean operation. The BOM line items for 12 Beduan solenoids, the MCP23017 + ULN2803A driver chain, and the 8 reservoir reed switches are present and accounted for in [bom.md](../../hardware/bom.md); they just have no firmware behind them yet.

This is a **readiness-blocking, work-organizing gap** — not a single bug. Surfacing it here so it doesn't slip into "we'll write it when we get there" when the procurement order goes in.

## What's already designed and bought

Per [hardware/topology/fluid-topology.md](../../hardware/topology/fluid-topology.md) and [hardware/wiring/esp32-pinout.mmd](../../hardware/wiring/esp32-pinout.mmd):

- **12 solenoid valves** V-A … V-K-B (tap, hopper, channel A/B select, bag-A in/out/nozzle, bag-B in/out/nozzle, BiB-A, BiB-B) — Beduan B07NWCQJK9, [bom.md:128](../../hardware/bom.md).
- **Driver chain:** ESP32 → I²C → MCP23017 0x20 (valves on PA[0:7] + PB[0:3]) → 2× ULN2803A → 12 solenoids — [bom.md:18,22](../../hardware/bom.md).
- **Level sensing:** 8 reservoir reeds via MCP23017 0x20 PB[4:7] + MCP23017 0x21 PA[0:3] (1 of these 0x21 reeds is conditional; pinout doc flags 74HC165 or direct-GPIO alternatives), plus 2 carbonator reeds on ESP32 GPIO 17 / 27. Architecture: [printed-parts/cold-core/reservoir/level-sensing.md](../../hardware/printed-parts/cold-core/reservoir/level-sensing.md).
- **Pumps:** Kamoer KPHM400 ×2 on the *retained* L298N Board A; SeaFlo diaphragm via Teyleten relay #2 on GPIO 4. Compressor on Teyleten relay #1 on GPIO 14.
- **11 fluid operations** are spelled out in fluid-topology.md §"Operations — Valve States": Dispense A/B, Fill-from-Hopper A/B, Fill-from-BiB A/B, Clean Water Fill A/B, Clean Flush A/B, Air Purge In A/B, Air Purge Out A/B.

## What firmware actually does today

[firmware/src/main.cpp](../../firmware/src/main.cpp), 3,781 lines:

| Subsystem | Current state |
|---|---|
| Solenoid drive | `A_ENB` GPIO 12 + `B_ENB` GPIO 4 (dispense), `CLEAN_SOL1_PIN` GPIO 27 + `CLEAN_SOL2_PIN` GPIO 17 (fill). Direct ESP32 GPIO → L298N #2/#3, no MCP23017 code. ([main.cpp:24,30,33,34](../../firmware/src/main.cpp)) |
| Pumps | L298N Board A, both Kamoer pumps — matches integrated plan. ✅ |
| Clean cycle | 2 phases: `CLEAN_FILLING` (open clean sol, 10 s) → `CLEAN_FLUSHING` (close clean sol, open dispense, pump, 15 s) × 3 cycles. ([main.cpp:487–496, 1419–1462, 3589–3594](../../firmware/src/main.cpp)) |
| Fill cycle | **None.** No code path for hopper-funnel → reservoir flow. |
| Air-purge phase | **None.** Firmware never opens V-B (hopper gate) with V-C/V-D + V-F/V-I to draw atmospheric air through the peristaltic into the reservoir, nor the symmetric "air out" via the nozzle path. |
| Level sensing | None for reservoirs. No MCP23017 input scanning. Carbonator reeds: planned on GPIO 17 / 27, but **those pins are already claimed for the prototype clean solenoids in current firmware** — see "Pinout conflict" below. |
| Funnel liquid-detect | **None.** Requirements §2 calls for capacitance-based detection of liquid in the funnel tubing; no sensor exists in the BOM and no firmware reads such a thing. |

## Specific gaps, sized for follow-up tickets

### G1 — Pinout conflict (do this before any wiring of unit #1)

Prototype clean solenoids use **GPIO 17** (`CLEAN_SOL2_PIN`) and **GPIO 27** (`CLEAN_SOL1_PIN`) as outputs. The integrated pinout puts the carbonator low / high reed switches on exactly those pins ([wiring/esp32-pinout.mmd:59–60](../../hardware/wiring/esp32-pinout.mmd)). When unit #1 wiring goes in, either:

- a) Drop the prototype `CLEAN_SOL{1,2}_PIN` defines entirely (clean solenoids should move onto the MCP23017 → ULN2803A chain like every other valve), or
- b) Reserve different ESP32 GPIOs explicitly in the pinout doc for whatever the "prototype clean solenoids" become on the integrated build, and update both ends.

Recommend (a) — there are no other surviving uses of L298N Board C in the integrated plan.

### G2 — MCP23017 driver code (precondition for everything else below)

No I²C valve / reed code exists in [firmware/src/main.cpp](../../firmware/src/main.cpp). Needed:

- IODIRA/IODIRB setup for both 0x20 (mixed in/out) and 0x21 (all in).
- GPPU pull-up enable on the reed-input bits.
- A scan routine for the 8 reservoir reed inputs (debounce, change-event semantics).
- A `setValve(name, state)` helper that maps valve symbol → (chip, port, bit) and writes via GPIOA/GPIOB.

Library candidate: Adafruit MCP23017 or hand-rolled (only 5 registers actually used).

### G3 — Valve-state abstraction matching the topology operations

The 11 operations in fluid-topology.md §"Operations — Valve States" are stateless lookup tables — each is "open set S, run pump X." Suggest in firmware:

```cpp
struct ValveOp {
  uint16_t openMask;      // bit per valve, 0x20 + 0x21 packed
  uint8_t  pump;          // 0=none, 1=A, 2=B
  uint8_t  pumpDir;       // forward only per spec
  const char* name;       // for logging
};
```

Then operations become table-driven, not state-spaghetti. A unit-test of "every operation matches fluid-topology.md" can be a simple golden-file check against the markdown.

### G4 — Clean cycle: implement the missing air-purge phases

Requirements §3 says the full cycle is:

1. Tap-water in (open V-A + select V-C/V-D + V-F/V-I, pump off).
2. Water flush (open V-E/V-H + V-G/V-J, pump on).
3. **Air in** (open V-B + V-C/V-D + V-F/V-I, pump on — funnel dry, atmospheric).
4. **Air out** (open V-E/V-H + V-G/V-J, pump on — same as dispense path, no liquid in bag).
5. Repeat.

Firmware today does (1) and (2) only, on a 10 s / 15 s × 3 fixed timer. No termination by level sensing. The peristaltic-as-air-pump trick (a stopped Kamoer cannot pass fluid, a running one can pass atmosphere when the upstream is open to air) is correct and clever but is nowhere in code.

### G5 — Fill cycle: implement, and add the missing capacitance sensor to BOM

Requirements §2: "Liquid in the tubing connected to the funnel is detected via capacitance, and is pumped into the selected flavoring reservoir." There is currently:

- No capacitive liquid-in-tube sensor in [bom.md](../../hardware/bom.md). Candidate parts: XKC-Y25-V (non-contact liquid sensor, clips around clear tubing) or a discrete TTP223 + foil ring. Add a §1 BOM line.
- No firmware code path for funnel→reservoir fill (would use the topology's "Fill from Hopper → Bag A/B" valve sequence + Pump A/B forward).
- Implicit ambiguity: requirements §2 doesn't specify *which* flavor the funnel pours into — UI must let the user pick before pouring, or the system must require selection before initiating the pump.

### G6 — Termination by level sensing instead of timers

The prototype's fixed 10 s / 15 s timers were fine when each reservoir was a Platypus bladder of known geometry. With the printed reservoirs (4 reeds per reservoir, ~13-serving-step granularity per [level-sensing.md](../../hardware/printed-parts/cold-core/reservoir/level-sensing.md)), every fill / clean phase should terminate by reed transition with a **safety-cap timeout**, not a bare timer. This is a behavioral upgrade, not just a wiring upgrade — corner cases: stuck float, lost magnet, both reeds reading same state.

### G7 — Migration plan, not a flag day

The bench prototype is the only working test rig. Avoid landing G2–G6 as one PR that bricks the bench. Order of safe steps:

1. **G2 first**, behind a `#define USE_MCP23017` gate. Bench keeps direct-GPIO solenoids; build verifies MCP23017 talks but doesn't act.
2. **G3** — add the operation table, but keep the existing dispense/clean code paths active. New table is reference only.
3. **G1** alongside G3 — reclaim GPIO 17 / 27 by moving prototype clean solenoids onto MCP23017 (now possible) on the bench. This *is* the flag-day step for the bench; one PR, dedicated test session.
4. **G4** — add the air-purge phases to the clean state machine, with a temporary safety: phase auto-aborts after 30 s regardless of reeds (so a missing G6 doesn't pump-dry-forever).
5. **G6** — wire up reed reads, replace the safety auto-abort with reed transitions.
6. **G5** — last, since it requires a BOM addition the others don't.

## Out of scope for this todo

- Firmware unit tests. [firmware/test/](../../firmware/test/) is the empty PlatformIO placeholder; a separate todo could call out the absence of any test coverage for a 3,781-line file controlling AC mains, refrigeration, water, and food-contact pumps.
- The S3-display config UI and iOS app for invoking Fill / Clean — they exist (search "CLEAN:" / "PRIME:" / `processConfigCommand`); the *fill* command doesn't exist yet because the firmware path doesn't.
- The flavor-selection UX gap in G5 (which flavor is the funnel pouring into?).

## Suggested next concrete step

Open a single tracking issue / doc titled something like "Manifold firmware port — unit #1" that lists G1–G7 as checkboxes, ordered as in G7's migration plan. Don't start writing manifold firmware *after* unit #1 valves are plumbed into the cabinet — the bench is the only place to develop this safely, and the bench's prototype-pin defines stand in the way of even validating MCP23017 + ULN2803A wiring on the bench today.
