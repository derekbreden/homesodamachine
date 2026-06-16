# Controller PCB — Fabrication and Assembly

How the consolidated controller board gets made: fabbing the bare 4-layer board, and
populating it. The board profile (from [`README.md`](/hardware/pcb/README.md),
[`netlist.md`](/hardware/pcb/netlist.md), [`bom-board.md`](/hardware/pcb/bom-board.md)):
**100 × 100 mm, 4-layer**, SMD set led by the ESP32-WROOM-32E module (RF, castellated +
exposed ground pad), 2× MCP23017 SOIC-28, 2× ULN2803A SOIC-18, 2× DRV8871 HSOP-8 (exposed
thermal pad), DS3231SN, two buck regulators, RS485 + passives; through-hole set = JST-XH
headers, 2 relays, CR2032 holder, USB-C if THT, AC terminal blocks. No QFN/BGA — the hardest
joints are the two **exposed-pad** types (the WROOM belly pad and the DRV8871 thermal pads),
not fine pitch.

Forward prices are marked *verify*; fab and assembly cost resolve only after a Gerber + BOM +
centroid upload. The working recommendation is stated; the decision is pending the first quote.

## Fabricating the bare board

| House | Bare 4L 100×100 (qty 5 / 10 / 50 / 100) | Turnkey assembly? | Fit |
|---|---|---|---|
| **JLCPCB** (CN) | ~$7 / ~$20–25 / ~$50–70 / ~$90–130 *verify* | Yes — in-house PCBA from LCSC | Excellent. 100×100 4L is its coupon sweet spot. |
| **PCBWay** (CN) | ~$5 flat 5–10pc; ~$1–2/bd at 50–100 *verify* | Yes — turnkey or consignment; strong DFM | Very good. #2; pick for DFM help or a part JLC lacks. |
| **OSH Park** (US) | $10/sq-in incl 3 copies → ~$52/bd proto; Medium Run $2/sq-in | **No assembly** | Marginal — bare boards only; you'd hand-build. |
| **AISLER** (EU) | ~€40–80/set by qty *verify* | Yes — no setup fee | Workable from the US but shipping/cost trails at volume. |
| **Advanced Circuits / Sierra** (US) | Adv Circuits $66-each 4L (MOQ 4); Sierra Turnkey PRO ~$800–1500+ first run *verify* | Adv: bare only; Sierra: full turnkey | US-made; capital-heavy. Only if compliance/speed/supply-chain demands it. |

JLCPCB's assembly model (2026, *verify*): SMT setup ~$8/side (often $0 via a standing
free-assembly promo on ≤6-layer boards) + ~$0.002/joint + **$3 per unique Extended part** +
$3 for a ≤100×100 stencil. This board carries ~8–10 unique Extended lines (the WROOM module,
DRV8871, MCP23017, ULN2803A, DS3231SN, bucks, RS485, coin holder) — roughly $25–40 of one-time
feeder fees per order, which is why the per-board cost falls steeply with batch size.

## Populating the board — placement options

The controller's two defining part types — the **ESP32-WROOM-32E belly/ground pad** and the
two **DRV8871 HSOP exposed thermal pads** — set the placement decision. TI specifies the
DRV8871 thermal-pad solder as compulsory (it is the device's heat path and ground return); a
belly pad cannot be reliably wetted by a soldering iron, which physically cannot reach the
solder under the part.

**Bench reality.** The
[`/hardware/ledger/tools.md`](/hardware/ledger/tools.md) "Soldering & electronics bench" is
hand-solder / through-hole: Hakko FX-888D iron, FR-301 desolder gun, fume extractor,
multimeter, tweezers, cutters, crimpers, helping-hands with magnifier, and a QWORK 300 W
mini heat gun — a heat-shrink tool, **not** a hot-air rework station with a fine nozzle and
airflow control. There is **no reflow oven, no stencil, no solder paste, no hot plate, and no
pick-and-place** in the ledger. The bench can do the through-hole pass and the easy SOIC/
passive SMD subset; it cannot reflow, and it cannot make the two exposed-pad joints.

| Path | What | Capital | Per-board | Fit (10 / 50 / 100) |
|---|---|---|---|---|
| **1 — Outsource SMT to the fab** (JLCPCB PCBA) | Fab places + reflows all SMD incl. the belly/thermal pads; the bench does only the TH pass (JST-XH, relays, CR2032, terminals) | **$0** | a few $ + one-time Extended-part fees | **Best / Best / Best** |
| **2 — In-house stencil + paste + reflow** (no P&P) | Buy a fab-cut stencil + leaded paste + a 200×200 hot plate (~$70–110) or a T-962A oven (~$210–336); hand-place with tweezers, reflow the whole board | ~$100–150 (hot-plate) to ~$240–385 (oven) | cents of paste + ~20–40 min/bd hand-place | viable (slow) / poor / poor |
| **3 — Hand-iron SMD, no reflow** (existing bench) | Drag-solder the SOIC-28/18/16 + passives on the iron you own | $0 | ~45–90 min/bd | **hard stop** — cannot do the WROOM belly pad or DRV8871 thermal pads at any qty |
| **4 — Pick-and-place machine** (Neoden-class) + reflow | Vision-place from feeders; still stencil + reflow | ~$5–7k all-in (machine + feeders + reflow) | low | not justified below ~low-thousands of boards across spins |

Path 3 alone is not viable for this board: the two exposed-pad part types leave the most
thermally critical joints unbacked, regardless of quantity. The documented hand workarounds
(a copper-foil heatsink soldered to the chip back, or feeding solder through a via) are
fragile and not production-repeatable.

## Working recommendation

**Fab and assemble at JLCPCB (Path 1).** Lowest capital at every quantity from 10 to 100, the
4-layer 100 × 100 size is its sweet spot, and machine reflow makes the two exposed-pad joints
correctly — the exact joints the current bench cannot make — at zero capital. The bench then
does what it is equipped for: the through-hole hand-solder pass (JST-XH, relays, CR2032, AC
terminals). Per-board SMT adder is only a few dollars at qty 50–100. Plan: order 5 assembled
to validate, then pilot 10–50, keeping the unique-part count low to limit feeder fees; keep
PCBWay as a backup turnkey path for stockouts or DFM help.

In-house placement enters the picture only if fast board-spin **iteration** becomes the
priority — in which case Path 2's minimal reflow tooling (~$3–8 stencil + ~$30 leaded paste +
~$70–110 hot plate ≈ $100–150) is the cheapest legitimate way to put reflow on the bench for
bringing up one or two prototype boards. A pick-and-place machine (Path 4) does not break even
until the project commits to thousands of in-house boards across many spins, far beyond a
100-unit run.

This supersedes the [`README.md`](/hardware/pcb/README.md) working assumption of "SMD
placement and reflow on our own equipment," which the current
[`tools.md`](/hardware/ledger/tools.md) bench does not support. Acquiring that capability (a
hot plate or oven + stencil + paste) is the prerequisite if Path 2 is ever chosen; until then
the board is a turnkey-fab part.
