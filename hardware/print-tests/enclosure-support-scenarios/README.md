# Enclosure support scenarios

This offline plate tests support contact and removal on crops of the production
printed enclosure surfaces. It preserves their print orientation and layer
phase. Each specimen carries a raised family and density label on top stock,
away from the contact surface being examined.

| Family | Production geometry retained | Support arrangement |
| --- | --- | --- |
| R — rail channel | Complete cross-section, local floor, catch, flare and side removal lane; shortened along its length | Trees start on model material inside the channel |
| H — handhold arch | Rounded end, sloping corbel, open seam end, wall junction and underside | Short bed-rooted trees carry the open seam end; the corbelled middle prints without supports |
| P — holed pad | The screenshot's pump-retainer insert post, complete square underside, hole mouth, blind pilot and closing tip, with its wall root | Short bed-rooted trees carry the pad underside |

The rail retains its normal floor-to-catch height. Its distance above the
original enclosure floor is removed. The handhold and pad omit tall empty
space below the working surfaces. The pad retains the complete blind bore and
its closed tip, with excess solid stock above cropped away. These are surface
and removal samples; they do not qualify the full-length rail's removal effort
or the structural capacity of the complete enclosure.

The handhold includes the complete open seam end. Its corbelled center alone
does not generate support contact in the native recipe. The open end provides
the actual supported start over air while retaining the current arch geometry.

## Density comparison

Facing Mark1, columns A, B and C run left to right. The rail row is at the front,
then the handhold row, then the pad row. A uses the current interface spacing,
B the denser spacing and C a solid interface. The exact settings, dimensions
and source bounds belong to [`samples.json`](samples.json), and the prepared
object settings and source hashes to [`preparation.json`](preparation.json).

Density varies within each family. The families retain their corresponding
production support styles and lateral clearance. The native planned top gap
therefore differs between the organic rail/handhold supports and the slim pad
supports. Each family's gap remains common across its density conditions.
[`verification.json`](verification.json) records these actual gaps, the local
rail roots, contact layers, trim, nozzle and complete deposited bed envelope.

The full comparison is an editable plate. Results from the
[initial ceiling screen](../petgf-dense-roofs/README.md) can select the density
conditions to print on these representative shapes. A reduced plate needs its
own native slice because removing objects changes the layer-time cooling.

## Examine the cooled samples

Compare density conditions within each family. Retain the removed support
beside its specimen. Record tree removal, interface peeling, residue, loose
model strands and damage separately. Assess the supported underside before
and after cleanup.

For the rail, use the normal screwdriver approach through the open lane and
note whether the trees lift out together. Feel the catch's sliding bearing and
check for protruding strands. For the handhold, distinguish the supported seam
end from the unsupported corbel and rounded end. For the pad, inspect the
underside around the hole mouth and check whether support material obstructs
the pilot entrance.

## Source locations and files

[`source-links.json`](source-links.json) opens each exact sample region in the
published enclosure model. The material comes from the current production
STLs; neither an enclosure source edit nor an enclosure rebuild is involved.

`samples.rs` crops and labels the exact imported printed triangles in Rust.
`prepare.py` converts the input format, runs that generator and packages native
per-object settings with Mark1's established textured-plate PET-GF recipe.
The prepared native archive is in [`ready/`](ready/); no printer submission is
performed by the generator. Its source profile is the initial ceiling plate's
reviewed Mark1 recipe, including the normal cooling hook.

To regenerate geometry, the editable project and the offline slice:

```sh
tools/cad-venv/bin/python hardware/print-tests/enclosure-support-scenarios/prepare.py --geometry --slice
```

The shared wrapper admits Cargo and slicing. Only finished specimen meshes,
project, native machine archive and concise physical-preparation records are
retained here. The manual comparison adds no ordinary build or commit check.
