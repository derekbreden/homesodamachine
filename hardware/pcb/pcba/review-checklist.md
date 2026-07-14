# PCBA Review Checklist

A **closed** checklist for reviewing the pcba board. Its purpose is to replace the
open-ended "find problems" prompt — which never terminates, because a review can prove a
*specific* defect present but never prove *no* defect remains — with a finite list you
walk to the end. "Done" means every category below has been consciously visited and marked,
not that an audit stopped finding things.

Point the next review agent at this file. Ask it to walk the list, mark each item, and
report per-item — **not** to hunt open-endedly for novel findings.

## Ground rules for anyone using this list

**Sequence of authority.** Functionality is defined by the repo → the board is designed and
engineered for that functionality → firmware is written *after* the board exists. Firmware is
deliberately unwritten and stays that way until there is a physical board to iterate it on.

**Markdown is driven *from* the board, never *drives* it.** Docs (`bom.md`, wiring schedules,
cable assemblies, pinout notes, snapshots) exist to *record* what the board is, to ease later
firmware work. If a doc and the board disagree, the board is right and the doc is stale —
fix the doc to match the copper, never move copper to match a doc.

**Out of scope here** (each is determined *from* the board, not a constraint *on* it, so it is
not reviewed against on this list): firmware behavior and the firmware/GPIO contract; enclosure,
tray, and mounting. The board's own height/clearance geometry *is* in scope (§5/§6) — the
enclosure that wraps it is not.

**Don't perturb a verified board to satisfy a cosmetic find.** Every change to a packed board
adds a new courtyard, placement, or trace through a dense corner — marginal risk of *introducing*
a defect rises as the board fills. Weigh each proposed change against that.

---

## 1. Electrical correctness — does the schematic do the right thing?

- [ ] **Net connectivity** — every pin lands where it should; no accidental shorts; no floating input that should be driven.
- [ ] **Power rail topology** — each part fed the correct voltage; regulators sized for total load; no rail feeding a part that can't take it.
- [ ] **Pull-ups / pull-downs** — every input needing a defined idle state has one (reset, enable, I²C/UART idle, unused logic inputs).
- [ ] **Decoupling / bypass caps** — one near every power pin; bulk reservoir caps where current is drawn in gulps.
- [ ] **Reference / analog integrity** — ADC references, sensor bias, anything a noisy neighbor could corrupt.
- [ ] **Reset & boot straps** — the MCU comes up in the right mode; strapping pins aren't fighting other functions.
- [ ] **Unused pins** — deliberately tied or left open per each datasheet, not by accident.

## 2. Current, power, and thermal

- [ ] **Trace ampacity** — power traces wide enough for their current (e.g. the 1.6mm F1 inlet series).
- [ ] **Copper-weight assumption** — the whole ampacity math assumes a copper weight (1oz vs 2oz); it must match what is actually ordered.
- [ ] **Connector / terminal current ratings** — screw terminals and headers rated for the amps through them.
- [ ] **Component dissipation & heat** — regulators, driver chips, FETs: how hot, and can the board shed it (copper pours as heatsinks, thermal vias)?
- [ ] **Inrush / transient current** — turn-on surge into bulk caps; pump/motor startup spikes.
- [ ] **Voltage drop** — long/thin traces sagging the rail at a distant load.

## 3. Protection & fault tolerance

- [ ] **Reverse polarity** (Q4).
- [ ] **Overvoltage / surge / TVS** (D8/D9).
- [ ] **ESD on lines leaving the box** (faucet UART, D10/D11).
- [ ] **Overcurrent / fusing** (F1 PPTC).
- [ ] **Inductive kickback** — flyback diodes on every relay, solenoid, motor, buzzer coil.
- [ ] **Fail-safe behavior** — what the board does on brown-out, MCU crash, sensor unplug (gas→compressor interlock).
- [ ] **Back-EMF / motor handling** for the peristaltic pumps.
- [ ] **Latch-up conditions** in mixed-voltage interfaces.

## 4. Signal integrity & EMC

- [ ] **Ground strategy** — solid return paths; no signal crossing a plane split; analog/digital ground handling.
- [ ] **Return-current paths** — every fast signal has a clean path back (source of mystery noise).
- [ ] **Crosstalk** — high-current or switching copper coupling into sensitive signal traces.
- [ ] **I/O filtering** — series R / RC / ferrites on lines leaving the board.
- [ ] **Emissions & immunity** — relevant only if certification is ever pursued; otherwise note as N/A.
- [ ] **Clock / crystal layout** — short, guarded, away from noisy copper.

## 5. Layout & manufacturability (DFM)

- [ ] **Clearances** — copper-to-copper and courtyard-to-courtyard (the "floor" gate).
- [ ] **Trace width / spacing vs. fab minimums** — nothing thinner than the fab can etch.
- [ ] **Via sizes & annular rings** within fab capability.
- [ ] **Solder-mask slivers & silk-on-pad** — the silk audit.
- [ ] **Single- vs. double-sided assembly** — single-side-top is the current constraint; each bottom part adds cost.
- [ ] **Component courtyards & keep-outs** — no collisions; nozzle access for pick-and-place.
  - ⚠️ **Known-open:** U10 appears to hug C15/C16 with ~zero clearance. Suspected footprint/height
    inconsistency — see §6. Confirm the courtyard against the *actual* imported part, not the silk.
- [ ] **Board edge margins** — pours pulled back from the rout.
- [ ] **Fiducials & tooling** — alignment marks present.
- [ ] **Paste / stencil coverage** — every pad that needs solder gets it (the paste count gate).

## 6. Component sourcing, BOM, and footprint fidelity

- [ ] **Every part sourced** — real LCSC/JLC part number (the "sourced" gate).
- [ ] **Stock & lifecycle risk** — in stock, not EOL, second-sources named.
- [ ] **Basic vs. Extended** — assembly cost / feeder-fee awareness.
- [ ] **Footprint matches the *real* part** — the land pattern (and courtyard, and height) must match
      the *actual* package being bought, verified via `tsci import <LCSC#>`, **never** a generic/presumed footprint.
  - This audit has been run ~a dozen times and *keeps* surfacing differences that agents assumed
    couldn't exist from the generic footprint they'd used. Treat "we already checked this" with
    suspicion — re-verify against the import, part by part.
  - ⚠️ **Known-open example:** U10 is a very tall part hugging C15/C16 with no clearance — a likely
    live case where the on-board silk/footprint disagrees with the imported part's true body/height.
- [ ] **Polarity & pin-1 orientation** — diodes, electrolytics, ICs oriented correctly (the orientation audit).
- [ ] **Voltage / temp / tolerance ratings** — every part rated above its actual stress with margin (cap voltage derating especially).

## 7. Documentation — driven *from* the board

Docs exist to *record* the board so later firmware work is easier. They must reflect what the
copper actually is; where they disagree, the doc is wrong.

- [ ] **BOM matches the board** — `ledger/bom.md` parts, counts, and totals reflect the current design.
- [ ] **Wiring & cable-assembly docs match the board** — schedules describe the actual nets/connectors.
- [ ] **Pinout / interface notes reflect actual copper** — recorded *from* the board, not a spec the board is held to (and explicitly not a firmware contract).
- [ ] **Snapshots are honest & dated** — point-in-time audit records not left asserting things a later change superseded; annotate rather than silently drift.
- [ ] **No decision-narrative drift** — docs describe current state only (repo convention): no "was X, now Y," no defending the current choice against unasked alternatives.

---

## Sign-off

The board is "reviewed" when every box above is checked or consciously marked N/A with a reason —
not when a review pass runs out of findings. Past that point, the highest-value verification is a
**physical build**: thermal reality, real noise, actual fault behavior, and true mechanical fit are
things a render-and-gates loop structurally cannot prove, and a static review never will.
