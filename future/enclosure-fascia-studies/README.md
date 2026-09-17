# Enclosure fascia studies

Four exterior forms around the machine's current display, funnel, pump cartridge and rear
fittings. Each has smooth corners, shoulders and a projecting base, with fluting confined to
broad wall fields.

| Form | Shape |
| --- | --- |
| A · Bell | A broad foot narrows through a continuous cove into straight walls. |
| B · Cushion | The body swells through its middle; rounded fluted fields sit within smooth margins. |
| C · Arch | Full shoulders sweep down toward the front over arched fluted fields. A flared foot balances the crown. |
| D · Plinth | A low projecting base meets the body through a recessed waist. |

![The four enclosure fascia forms](renders/comparison.png)

[Base detail](renders/bases.png)

`fascia.template.html` contains the shape profiles, texture fields, lighting and rotatable
comparison. `models.b64` contains compressed meshes from the current enclosure STEP files and
assembly payload. `sources.json` identifies those source files by digest. The current-outline
view uses the same source geometry with zero displacement.

The exterior displacement fades to zero within 2.6 mm of the nominal perimeter. Hardware
meshes retain their assembly coordinates. The viewing meshes contain the shell's exterior
faces and opening rims; simplified hardware fills the visible cavities. Shared triangle edges
subdivide together before the skin is shaped. The comparison includes front, side, upper and
base-detail views, white and black finishes, and measured shell envelopes at one common scale.

This is appearance geometry. Surface shading represents the flutes. Wall sections, joints,
cartridge motion, printer envelopes and support removal remain unqualified for these forms.

Build the comparison with the project's CadQuery environment:

```sh
tools/cad-venv/bin/python future/enclosure-fascia-studies/build_studies.py /absolute/output/directory
```

Compose the saved meshes after editing the form profiles or presentation:

```sh
tools/cad-venv/bin/python future/enclosure-fascia-studies/build_studies.py --compose /absolute/output/directory
```

The output is `enclosure-fascia.html`, an inline visualization fragment.

`browser-checks.json` records the rendered envelopes, browser errors and narrow-screen layout.
`interaction-checks.json` records synchronized rotation and zoom across the comparison.
