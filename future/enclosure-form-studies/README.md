# Enclosure form studies

Four exterior forms at one scale, with the installed hardware in the enclosure assembly's
coordinates. The machine display, funnel, pump stations, guides, ports and internal supports use
their existing geometry and placement. The current enclosure uses the published fluted surface;
the alternatives carry geometric flutes over their revised exterior profiles.

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
qualification are not part of these files. The flutes are 4 mm wide, 1.2 mm deep and fade over
5 mm at surface boundaries. Their phase matches the installed vents aft of Y80; the revised
front profiles distribute that phase symmetrically over their own lengths. The alternatives'
exposed interior ledges use the smooth CAD surface.

The current shell triangles come from each piece's `.step.mesh` without further reduction.
The alternatives are tessellated at 0.02 mm linear and 0.08 radian angular tolerance and passed
through `flute_skin.flute`, retaining its triangles without decimation. Coordinates in the
viewer are quantized to 0.001 mm. Hardware hidden in the exterior view uses simplified meshes.
These are viewing geometry, not print files.

## Preview

`enclosure-forms.template.html` contains the rotatable comparison. `models.b64` contains its
compressed geometry. The controls show front, side, top, rear and enlarged corner views, separate printed pieces,
the fixed interior, black or white PET-GF, and the cartridge withdrawn 100 mm along its existing
axis.

To generate the full browser comparison from the local CAD:

```sh
tools/cad-venv/bin/python future/enclosure-form-studies/build_studies.py --output /absolute/output/directory
```

To compose the saved study without rebuilding CAD:

```sh
python3 future/enclosure-form-studies/compose.py /absolute/output/directory
```

The resulting `index.html` retains the full viewing geometry. The conversation comparison uses
rendered detail images; its size limit does not set the geometry's resolution. A mesh cache in
the output directory holds the intermediate study surfaces.

`compose.py --corners /absolute/output/directory` composes the saved close-ups in `renders/`
into the conversation comparison. `surface-fidelity.json` records the triangle-by-triangle
comparison of the packed shell geometry against the published reference and study surfaces.
