# PGFUN shop guide builder

Run `tools/cad-venv/bin/python tools/gun-positioner-guide/build.py` after
generating the PGFUN assembly and reference meshes. The builder renders
actual CAD, combines the current assembly, purchases, electrical,
commissioning, observation, engineering and firmware instructions, and writes
the PDF, cover, document sidecar and source receipt under
`hardware/gun-positioner-guide/`.

The page furniture comes from `tools/assembly-guides/common.py`. IBM Plex
Sans/Mono are embedded from the shared guide assets. Coral identifies parts
used by an operation; dark grey depicts the printed fixture. Assembly
pictures, parts panels and numbered actions remain together by operation.
The contents and native PDF bookmarks are generated from the final pagination.
Continued pages name their operation or chapter in the running header. A screw
cutting schematic shows the backing nut and sacrificial nut held in the saw vise.

Render every PDF page with Poppler and inspect it after a layout change.
The guide's QA receipt records page coverage and the inspected PDF digest.
