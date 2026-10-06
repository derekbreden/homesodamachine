# PGFUN shop guide builder

Run `tools/cad-venv/bin/python tools/gun-positioner-guide/build.py` after
generating the PGFUN assembly and reference meshes. The builder renders
actual CAD, combines the current assembly, purchases, electrical,
commissioning, observation, engineering and firmware instructions, and writes
the PDF, cover, document sidecar and source receipt under
`hardware/gun-positioner-guide/`.

Render every PDF page with Poppler and inspect it after a layout change.
The guide's QA receipt records page coverage and the inspected PDF digest.
