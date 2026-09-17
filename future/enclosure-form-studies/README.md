# Enclosure form studies

Four exterior forms at one scale, with the installed hardware in the enclosure assembly's
coordinates. The machine display, funnel, pump stations, guides, ports and internal supports use
their existing geometry and placement. All views show smooth surfaces, without the enclosure's
fluting.

| Form | Front outline | Nominal shell envelope |
| --- | --- | --- |
| Current | 12 mm corner radii, flat front | 215 × 462 × 361 mm |
| A · Soft shoulders | 22 mm corner radii, flat front, 6 mm upper rounds | 215 × 462 × 361 mm |
| B · Bowed front | 22 mm corner radii, 6 mm upper rounds and circular crown across the central 159 mm | 215 × 468 × 361 mm |
| C · Crisp bevels | 13 mm vertical corner bevels, 4 mm upper bevels | 215 × 462 × 361 mm |

The envelope figures describe the printed enclosure; the funnel brim and rear fittings extend
beyond it. The four quadrants, pump cartridge and display cover remain separate. B's front crown
continues across the lower front, the fixed sill and the pump cartridge, and terminates on the
existing display plane. A and B also trim the rounded entry edges of the cartridge's side pull
pockets. The pockets' flat bearing faces stay in place.

`build_studies.py` reads the enclosure parts' STEP files, cuts the exterior corner profiles and
adds B's front crown. It writes valid-solid and envelope readings to `geometry-checks.json`.
The installed hardware uses the assembly payload; its cold-core exterior is reduced to convex
hulls for the interior view. The machine display cover comes from its own STEP, placed on the
45° display plane. Display and tube locations are shared across all four views.

These are exterior studies. Full wall-thickness, assembly-motion, support and production-slice
qualification are not part of these files. The browser uses simplified meshes, quantized to
0.02 mm. They are viewing geometry, not print files.

## Preview

`enclosure-forms.template.html` contains the rotatable comparison. `models.b64` contains its
compressed geometry. The controls show front, side, top and rear views, separate printed pieces,
the fixed interior, black or white PET-GF, and the cartridge withdrawn 100 mm along its existing
axis.

To generate a conversation fragment from the local CAD:

```sh
tools/cad-venv/bin/python future/enclosure-form-studies/build_studies.py --output /absolute/output/directory
```

To compose the saved study without rebuilding CAD:

```sh
python3 future/enclosure-form-studies/compose.py /absolute/output/directory
```
