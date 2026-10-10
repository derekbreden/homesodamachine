# One PET-GF organizer, Ø4.30 mm drain bore — Mark2

**Why this print:** the received 4 mm drain tube tests a bit too tight in the
accepted L sample's Ø4.20 mm drain bore. This puck is the
[production organizer](../../../hardware/printed-parts/faucet/umbilical-organizer/README.md):
L's three Ø6.65 mm quarter-inch bores and a Ø4.30 mm drain bore, 0.10 mm larger
in diameter. Printer, settings and bed position repeat the
[L job](../fit-trial-mark2/README.md), so the drain bore is the only difference
from the L article.

| Feature | This print | L article |
|---|---|---|
| Soda and both flavor bores | Ø6.65 mm | Ø6.65 mm |
| Drain bore | **Ø4.30 mm** | Ø4.20 mm |
| Stock, signal passage, chamfers | Ø32 × 10 mm, Ø5 mm, 0.4/0.2/0.6 mm | same |

The [physical acceptance record](../../../hardware/printed-parts/faucet/umbilical-organizer/physical-acceptance.json)
holds both reports on the L article. This print has not been submitted.

## Files

- Editable project:
  [`2026-10-09-organizer-d430-petgf-left04-z004-mark2.3mf`](2026-10-09-organizer-d430-petgf-left04-z004-mark2.3mf).
- Native archive to send:
  [`2026-10-09-organizer-d430-petgf-left04-z004-mark2.gcode.3mf`](2026-10-09-organizer-d430-petgf-left04-z004-mark2.gcode.3mf).
- Source mesh: [`parts/umbilical-organizer-q6.65-d4.30.stl`](parts/umbilical-organizer-q6.65-d4.30.stl),
  byte-identical to the production STL.
- Manual preparation: [`../prepare_drain_fit.py`](../prepare_drain_fit.py). It
  does not submit a print. The
  [preparation report](2026-10-09-organizer-d430-petgf-left04-z004-mark2.print.json)
  binds the mesh to its native object and records the settings, archive and
  G-code hashes, emitted layers and bead envelope.

## Print settings

- Printer: **Mark2**, fixed **left 0.4 mm hardened nozzle**, left external
  slot 254, physical PET-GF. The printer reports PET-CF/GFT01, color `161616`.
- Settings source: [`hardware/printed-parts/petgf.3mf`](../../../hardware/printed-parts/petgf.3mf),
  as in the L job.
- Textured PEI; 0.20 mm first layer and 0.24 mm layers above it; 42 layers,
  final commanded Z 10.04 mm for the 10 mm CAD body.
- Two walls; 15% grid infill; profile flow ratio 0.9555. No XY hole or contour
  compensation; 0.15 mm elephant-foot compensation.
- Nozzle 265 °C first layer / 280 °C subsequent layers; bed 80 °C.
- Mark2 Z trim **+0.04 mm**: native textured-plate startup clears to `G29.1 Z0`
  and applies `G29.1 Z0.02` including that trim.
- One puck at the centre of the shared printable area, the L job's middle
  position. No supports, brim or pause.
- Native estimate: **15 min 4 s**, **4.10 g**.

The emitted G-code carries the change: at mid-height the drain hole's innermost
wall path runs at 2.346 mm radius, against 2.296 mm in the L job, 0.10 mm more
in diameter.

## Fit check

Thread the puck onto the received white 4 mm drain tube and the blue and both
black quarter-inch tubes. Hold the puck in one hand and each tube in the other,
and deliberately push and pull it through. The drain should move by hand
without a tool, kinking, flattening or scoring, and stay put when not pushed,
like the L article's quarter-inch bores.
