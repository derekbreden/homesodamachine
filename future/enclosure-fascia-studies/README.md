# Enclosure fascia studies

A 12 mm flared foot, 44 mm high, around the complete perimeter. Three upper forms combine a
deeper front wall, a tilted machine display, a rounded chamfer and an aft-shifted funnel.

| Form | Display angle from horizontal | Added front depth | Funnel aft |
| --- | --- | --- | --- |
| Foot only | 45° | 0 mm | 0 mm |
| A · Soft sweep | 40° | 18 mm | 32 mm |
| B · Low console | 28° | 40 mm | 44 mm |
| C · Upright crown | 62° | 24 mm | 26 mm |

![The smaller foot and three display forms](renders/comparison.png)

[Side profiles](renders/side.png) · [Display and chamfer](renders/top-front.png) ·
[Front foot](renders/bases.png) · [Rear foot](renders/rear-base.png) ·
[Rear top edges](renders/top-rear.png)

The foot runs from Z −6 to Z 38, with its maximum projection at Z −2. Its profile is identical
at the front, rear and sides. The reference retains the source shell above the foot.

The added front depth extends from the base to the display, with rounded plan corners joining
the existing flanks. The cartridge pull openings, service slots and ventilation openings retain
their original positions. The machine display, its glass and its cover share one rigid rotation
and translation. The funnel and its new roof opening share one aft translation.

Each upper form has a flat display seat between tangent circular transitions into the front
wall and roof. A has 24 mm lower and 30 mm upper radii; B has 30 mm and 44 mm radii; C has
18 mm and 34 mm radii. The remaining top perimeter has an 8 mm inward round. The funnel brim
lands on a flat roof, with 15.1, 24.1 and 37.8 mm between its front edge and the end of the
upper curve in A, B and C respectively.

Surface shading represents 4 mm wide, 1.2 mm deep flutes on approximately 5.1285 mm pitch.
The pattern follows each form's perimeter and fades into the smooth foot and upper edges.

`build_caps.py` constructs the upper surfaces in CadQuery and writes `caps.b64`. Its visible
patch joins the source enclosure at Z 242 and Y 315. The cartridge pull air is cut from the
source front-top and pump-cartridge solids. `cap-readings.json` records CAD validity and the
funnel's flat landing. `fascia.template.html` contains the foot profile, front extension,
hardware transforms, surface shading and rotatable comparison.

`models.b64` contains the exterior faces and opening rims from the source enclosure STEP
files, plus assembly hardware. `sources.json` identifies those files by digest. Positions are
quantized to 0.001 mm and source normals to 0.001. Shared triangle edges subdivide together
before the foot and rear top edges are shaped. The comparison includes front, side, rear,
overhead and detail views, with synchronized cameras and white and black finishes.

These are appearance surfaces. The fixed pump hardware and other internal components retain
their assembly coordinates. Internal wall sections, cartridge construction and travel,
display mounting, funnel tube routing, joints and print qualification are unresolved. The
production parts retain their existing geometry.

Rebuild the source meshes and upper forms with the project's CadQuery environment:

```sh
tools/cad-venv/bin/python future/enclosure-fascia-studies/build_studies.py /absolute/output/directory
```

Rebuild the upper forms and compose the saved source meshes:

```sh
tools/cad-venv/bin/python future/enclosure-fascia-studies/build_caps.py
tools/cad-venv/bin/python future/enclosure-fascia-studies/build_studies.py --compose /absolute/output/directory
```

The output is `enclosure-fascia.html`, an inline visualization fragment.

`browser-checks.json` records rendered envelopes, browser errors and narrow-screen layout.
`interaction-checks.json` records synchronized rotation and zoom. `geometry-checks.json` records
the four-sided flare, its height, full-height front extensions, rigid display transforms,
funnel translations and unchanged fixed hardware.
