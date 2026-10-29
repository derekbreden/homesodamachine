# Mark2 foot and first-shoulder material comparison

This unsent material comparison covers the complete foot and first shoulder,
cropped at original print Z33.8 mm. It has **no accepted printer job** and is
not selected for submission. The active Mark2 fin iteration is the
[single tip candidate](../../2026-10-15-tip-fins/README.md), with no repeat control.

| Facing Mark2 | Condition |
| --- | --- |
| A, left | Production material settings and Tree(auto), Default |
| B, right | Native bridge flow 1.25; 70% fan on every model feature after the first three bed layers; Bridge moves at 15 mm/s; Tree(auto), Default |

The customer outcome is an intact plate-mating rim and a clean rear shoulder,
with the accepted adjacent finish retained. Keeping the support method the same
within this plate compares the material recipe on one printer. Mark1's running
[Full-annulus fins versus trees plate](../../2026-10-14-foot-fins-current-angle/full-annulus/mark1/README.md)
compares the support conditions with the bridge recipe on both specimens.
The [stock-fin strand failure](../../2026-10-14-foot-fins-current-angle/stock-vs-tree/mark2/physical-result/physical-result.json)
is an in-progress result from the separate production-recipe plate.

Both specimens retain the source base, −15° pose, original bed contact,
Arachne/solid-foot treatment, eight coarse lip layers, first fine band and rear
scarf seam. This section contains the localized rear shoulder at CAD Z14
(defect 1) and the complete lower rim (defect 3). The source's 0.3 mm outward
rear step and seam are present in both specimens. The second fine band and
upper faucet lie outside this section.

The [G-code review](ready-review.json) confirms B's 70% fan includes Floating
vertical shell as well as wall, bridge and infill features. The sampled rear
shoulder receives 0–9% native fan in A and 70% in B. Its sampled paths contain
walls, infill and one Floating vertical shell segment, with no Bridge-labeled
move; those wall feeds retain their native values. The 15 mm/s Bridge cap
applies to the Bridge features elsewhere in the section. Score the localized
shoulder bead separately from underside sag and rim recovery. The combined
recipe does not isolate the individual flow, fan and speed effects.

The native estimate is **3 h 54 min 14 s and 95.84 g**, before the local Bridge
slowdown. Mark2 uses external spool 254, black PET-GF, fixed left hardened
standard-flow 0.4 mm, Textured PEI and its +0.04 mm requested trim
(`G29.1 Z0.02`). Model/support/brim beads remain at least 90.03 mm inside the
usable bed boundary. Native coordinates, arc and extrusion words are preserved
through the fan/feed treatment; A and all supports retain native fan/feed.

Use the [print-only archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/faucet/finish-coupons/2026-10-14-bridge-transfer/mark2/2026-10-14-faucet-foot-bridge-transfer-petgf-left04-z004-mark2-print-only.gcode.3mf)
without reslicing. G-code SHA-256:
`dd4572ee9439b93fe32d7656107a284c8e2701b38c1146e384626d8e7c98ed78`.
The separate launch receipt will bind an accepted job to this archive.

The [physical assessment](../README.md#physical-assessment) compares retained
skin, loose strands, removal effort, mating fit and the rear shoulder bead using
the existing cleanup tools and mounting plate. A useful result improves the
identified defect without damaging adjacent finish or mating fit. A clean B
alone cannot establish a cure if A does not reproduce the defect. Physical
observations of this pair remain pending.

Run `review-foot-ready.py` manually from the parent directory with
`tools/cad-venv/bin/python` to repeat the saved path review. It sends no printer
commands and adds no build or commit checks.
