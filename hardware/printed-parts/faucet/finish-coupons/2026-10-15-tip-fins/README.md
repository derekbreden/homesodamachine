# Tip joint fin iteration

One actual tip section tests plain fin walls at the circumferential mating lip,
defect 2 in the [confirmed defect map](../../industrial/defects/2026-10-14.html).
The customer outcome is a clean, intact joint edge after support removal, with
the accepted tip angle and adjacent surface retained. There is **one specimen
and no repeat control**. The current fin work alternates base and tip geometry
between the two printers.

**Mark2 completed job 1341048254, accepted at 01:25:19 CDT on 2026-10-15.** The
[physical result and three photographs](mark2/physical-result/physical-result.json)
record Derek's best observed bottom-side rim finish, with no clear improvement
on the opposite side. Completion reports FINISH at 167/167 without errors.
The [launch receipt](mark2/launch.json)
binds the reviewed archive, resolved external spool and print options to that
job. The opposite printer's preceding launch was more than three minutes earlier.

The section preserves the identified production tip geometry, **−105° X pose**,
original bed contact and full circumference. It ends at original print Z40 mm,
above the complete joint ledge. The source mesh and STEP hashes match the
[identified faucet](../../industrial/prints/2026-10-13-complete-rear-seam-base-tip-mark2/physical-result.json).
The curved male plug, rear scarf seam and ordinary 0.24 mm layers remain present.

## Fin placement and recipe

The joint plane is at **35° to the bed**, with **167.83 mm²** of downward-facing
ledge. Part of its projection already has the curved plug beneath it. The
unmodified [Support Fins engine](https://github.com/gittrahan/support-fins/tree/511d81fc9124075cef142bfb2766bd5e8bfa777d)
provides **eight plain walls** in Full mode, coverage 1.0, downhill enabled,
bed pad off and gripping teeth off. The caller selects the joint plane for
placement; the full tip topology sets the first-hit wall tops, including plug
surfaces below the ledge. A near-midpoint wall serves the low starting lip.
The [engine record](mark2/layout-engine.json) retains every contact line.

The engine's 45° analysis threshold selects this observed defective ledge for
the experiment. It is not a measured PET-GF failure threshold. The
[v6 ramps](../../../../print-tests/petgf-fins/finish-matrix-v6/mark2/physical-result.json)
accepted 35–42.5° surfaces over their tested reach; they do not establish the
unsupported tip edge's finish. The local fin choice specifically addresses
the photographed circumferential lip damage at the retained orientation.

Walls are nominally 1.0 mm with 0.6 mm contact tips and a requested **0.24 mm
vertical gap**. Support-block paint covers only the joint plane and added fin
surfaces. Tree(auto), Default remains enabled elsewhere. The
[stock faucet base result](../2026-10-14-foot-fins-current-angle/stock-vs-tree/mark2/physical-result/physical-result.json)
reports easy release for its eight walls; release on this tip remains a
separate physical result.

The editable native recipe uses **bridge flow 1.25**, **70% fan after three
fan-off bed layers**, **15 mm/s Bridge moves** and overhang limits at most
15 mm/s, retaining the existing 10 mm/s fully overhung-wall limit. Cooling
includes Floating vertical shell and supports. Ordinary supported-wall and
infill speeds retain their saved values. There are no post-slice G-code edits.

## Native review and print

The [native review](mark2/review.json) follows 466 first-skin traces near the
joint plane. Its largest sampled run with no overlap onto deposited bead
footprints in the preceding three courses is **4.19 mm**, at the low lip's
Z15.32 course. The next course's corresponding run is 2.60 mm. These are
geometric bearing measurements; they do not predict strand sag, fusion or
surface quality. All sampled traces and their chronological-neighbour checks
remain in the review.

Native estimate: **36 min 46 s, 9.20 g, 167 layers**. All model/support/brim
beads remain at least **138.31 mm** inside the usable bed boundary, including
arc paths. Mark2 uses external spool 254, black PET-GF, the fixed left hardened
standard-flow 0.4 mm nozzle, Textured PEI and +0.04 mm requested trim
(`G29.1 Z0.02`). Temperatures are 265°C first layer, 280°C normal and 80°C bed.
Timelapse and leveling are On; Flow Dynamics and Nozzle Offset Calibration are Auto.

The [print-only package](mark2/packaging.json) preserves the reviewed native
G-code, SHA-256
`4f09c3174196b49eee803f3c486cc2a0dac6387480a2d99a7768b4e769bea5f9`.
Open it without reslicing. The launch receipt preserves the printer's successful
file acknowledgment and the separate confirmation of the 167-layer job.

The opposite rim side remains rough and appears unsupported to Derek. The
combined material recipe and support arrangement establishes the reported
bottom-side appearance; the result does not isolate cooling, speed, flow or
fin contributions. Release effort and joint fit are not separately reported.
The [next single tip candidate](../2026-10-15-edge-supports/README.md) retains
the fins and adds tree contacts at the seam-side low starting lip.

`prepare.py`, `build-fins.mjs` and `review.py` are manual experiment tools.
They add no build or commit checks. Run the Python tools with the repository's
`tools/cad-venv/bin/python`; preparation preserves any accepted launch.
