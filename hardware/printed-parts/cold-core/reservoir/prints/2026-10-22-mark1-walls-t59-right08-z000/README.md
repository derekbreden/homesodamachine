# Reservoir floor-junction trial on Mark1

Mark1 accepted task **1364550539** at **11:40:35 CDT / 16:40:35 UTC on October 22, 2026**.
The printer acknowledged `project_file` SUCCESS and entered PREPARE with no
print error or HMS alert. [Launch](launch.json).

The full-height **left reservoir and matching cap** use the walls-only May Water
recipe through Mark1's **right 0.8 mm Standard nozzle**. The selected physical
change is **Arachne wall transition angle 59°**. [Adaptation](adaptation.json).

Derek authorized the print:

> Proceed with a print you think will work. Bed is clear.

**999 requested walls**, zero sparse/top/bottom fill, **flow 1.02**, **255/260 °C**,
**70 °C** bed, **21 mm³/s**, **0.30/0.24 mm** layers and nominal **0.8 mm** lines
are retained. Wall order is inner then outer, with random conditional scarf
seams and 15% seam gap. Ordinary part cooling is 10–20%, the first three layers
are off, local overhang cooling is 90%, and auxiliary cooling is off.
**No brim, zero added user Z trim, and no model or support ironing**.
Stock Textured PEI compensation emits `G29.1 Z-0.02` after the trim reset.
Geometry, placement and Tree(auto)/Default bed-only supports are retained.

The [native comparison](../2026-10-21-mark1-walls-only-right08-z000-a4/physical-result/seam-comparison.json)
shows additional center-wall paths at the floor's perimeter-convergence
junctions. The nominal layer-12 XY pockets total about **2.78 mm²**, approximately
72% smaller than the reported leaking article's slice. Residual modeled pockets
remain. The footprint model is not a measurement of deposited material or proof
of a through-floor water route. This article supplies its own sealing result.

The regenerated current project is byte-identical to the compared candidate,
allowing reuse of its completed native slice. [Slice binding](slice-reuse.json).
Both plates contain only Inner wall, Outer wall and Overhang wall model features;
supports have their own paths. There is no model raster fill, gap fill, brim or
ironing. The left plate estimates **6 h 2 min, 433.03 g and 833 layers**.
Full beads stay at least **70.5 mm** inside the usable bed boundary. All seven
support bodies start at the bed; six have no explicit interface label.
[Native review](native-review.json) · [Packaging](packaging.json).

Start on **A1**, the most depleted loaded matching spool, reporting **6%**.
**A3 reports 100%** and is the only other loaded matching spool. A2 and A4 are
empty. Retain automatic refill and use each spool fully. [Preflight](preflight.json).

The preceding walls-only article has [reported seam leakage](../2026-10-21-mark1-walls-only-right08-z000-a4/physical-result/physical-result.json).
The historical May and September water holds remain scoped to their tested
articles. This trial has **reported bottom leakage and a new vertical-edge defect**.

The foreground Send dialog selected **A1 PETG R** and the mounted right
**0.8 mm Standard** hotend. Timelapse and bed leveling were **On**; flow dynamic
and nozzle offset calibration were **Auto**. Mark2 retained its same idle
finished task for more than 180 seconds before Send.

At **11:43:38 CDT / 16:43:38 UTC**, runtime current/target tray **0 (A1)**
and right-extruder `snow=0` confirmed A1 loaded to the mounted right **0.8 mm**
nozzle. The task was RUNNING at **0/833** with no print error/HMS. Clear live
camera frames show the head moving across the empty plate during startup.
Body/cap first-layer contact is unassessed. Runtime timelapse activation remains
unassessed before deposition. [Startup observation](startup.json).

## Physical result

Derek reports bottom leakage at the same location, possibly worse, and a new
vertical-edge defect. Photos 1–4 show repeated projecting strands beside the
curved wall. Photo 5 shows droplets at the floor's branching junction and
perimeter. The retained task reports **FINISH 833/833**, with no print error/HMS.
This is a failed reported water hold. Water head, hold duration and leak rate
are unreported, so the degree of worsening is unquantified.
[Five photographs and result](physical-result/physical-result.json).

The native wall-path comparison at layers **120, 400 and 700** finds **nine**
continuous extrusion runs at 59°, versus **five** at 10°. Four additional runs
are sub-millimeter segments at the curved-wall end junctions. These extra local
starts/stops are a plausible contributor to the edge bristles; their physical
cause and photo-to-path registration remain unverified. The submitted body
G-code contains no explicit extrusion Z ramps away from nominal layer heights,
despite saved conditional scarf controls.
[Path reading and proposed next trial](physical-result/wall-junction-review.json) ·
[Wall-path comparison](physical-result/wall-paths.png).

The 59° setting has no demonstrated sealing benefit for this article. The
smaller nominal XY pocket metric did not predict a successful water hold.
The proposed next screen restores **10°**, retains walls-only, and tests
**1.05 flow** on the actual floor/lower-wall geometry. This is a proposed
physical extrusion trial; the saved project remains the identified failed
59° / 1.02 recipe. No subsequent print has been started.
