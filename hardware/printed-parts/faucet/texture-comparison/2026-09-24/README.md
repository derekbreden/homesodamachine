# Sculpted faucet texture comparison

Native BambuStudio 02.08.02.61 estimates for the current Sculpted faucet's saved
four-part PET-GF project. Geometry, placement, 0.4 mm nozzle, temperatures,
speeds, walls, infill and support settings are identical across the candidates.
The source projects are unchanged. These are offline timing studies; none has
been submitted to a printer.

## Physical observation

Derek describes the tee carrier's 0.24 mm surfaces, both flat and rounded, as
smooth but sandy, like very fine-grained sand, with an expensive feel. Its
0.08 mm regions feel like a solid, smooth surface covered in very fine, tiny
fuzz that belongs to the surface and does not rub off. The faucet candidates
have no physical texture observations yet.

## Native time estimates

The faucet plate contains the shell base, shared shell tip, display cover and
above-counter plate. It excludes the lever and separate TPU gasket. Estimates
include the saved startup sequence and supports; times are rounded to minutes.

| Candidate | Model layer schedule | Faucet plate | Added time over baseline |
|---|---|---:|---:|
| Sandy baseline | 0.24 mm throughout | 4 h 31 min | — |
| Fine display cover | Complete cover at 0.08 mm; other parts 0.24 mm | 4 h 51 min | 20 min |
| Fine upper gooseneck | Upper curved portion of base, complete tip and cover at 0.08 mm; remaining base and plate 0.24 mm | 7 h 34 min | 3 h 03 min |
| All fine | All four parts at 0.08 mm | 11 h 41 min | 7 h 10 min |

The baseline retains its saved 0.20 mm first layer. Each fine candidate uses a
0.08 mm first layer across the plate. The remaining layer runs are verified
from actual model-wall extrusion, by object ID. The fine upper gooseneck
requests the base's fine band from print Z 150.24 mm upward; its emitted fine
layers begin above Z 150.32 mm. This covers the curved gooseneck's lowest
print-Z station in the saved orientation. The whole tip and cover use 0.08 mm.

The accepted side-down lever is a separate job:

| Lever schedule | Native estimate |
|---|---:|
| 0.24 mm, saved 0.20 mm first layer | 16 min 38 s |
| 0.08 mm including the first layer | 34 min 50 s |

A fine cover on the four-part plate plus a separately printed fine lever totals
about **5 h 26 min**. An all-fine four-part plate plus the same fine lever totals
about **12 h 16 min**. Combining the lever onto the faucet plate would require
its own packing and slice; these totals are for two jobs.

## Proposed finish arrangement

The sandy finish covers the shell and above-counter plate. The complete
display cover and lever carry the finer finish, putting one bounded accent
around the display and the other on the part operated at every dispense.
The accepted lever's broad contact face prints vertically in its saved
side-down orientation.

The shell base prints 15 degrees from vertical. A height-band boundary follows
the print plane and crosses the assembled shell at a slant; it cannot follow
an arbitrary selected patch or a horizontal shoulder all the way around.
Whole-part boundaries give the two finishes a definite edge. The fine upper
gooseneck is an additional candidate for a larger continuous fine area.

Layer height does not reduce the saved extrusion width. Bed-contact texture
and horizontal top-skin texture are separate from layer-built side surfaces,
so 0.08 mm everywhere is not evidence that every face will reproduce the
carrier's feel. Matching lever prints in one colour and material would provide
a direct tactile comparison on the actual operating surface.

[Polymaker's PET-GF15 technical data sheet](https://fiberon.polymaker.com/wp-content/uploads/TDS_FIBERON-PET-GF15_V1.0_EN.pdf)
also describes slight colour variation with changes in layer time and cooling.
The report establishes no microscopic cause for the observed fuzzy feel.

## Evidence

[Results and hashes](results.json) bind each source project, staged input,
native archive and G-code, and record the actual emitted layer runs and
settings differences. Each candidate retains its native `slice-result.json`.
All six completed slices have a zero return code and an empty warning field.

The slicer normalizes the faucet's prime volume to 45 mm³ and adds
`filament_map_2` on export; both are identical in all four faucet candidates.
After that common normalization, native settings differ only in the intended
layer schedule. The geometry members and placement are checked byte for byte
against the source project.

`compare.py` reproduces the four Sculpted timing candidates, and `lever.py`
reproduces the two lever timings, under
`.cache/prints/2026-09-24-faucet-texture-comparison/`. Both use the project's
CadQuery Python and installed Bambu Studio; neither connects to a printer.
