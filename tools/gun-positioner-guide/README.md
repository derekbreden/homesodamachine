# PGFUN shop guide builder

Run `tools/run hsm-manual-guides build gun-positioner-guide` after
generating the PGFUN assembly and reference meshes. The native builder projects
the saved meshes, combines the current assembly, purchases, electrical,
commissioning, observation, engineering and firmware instructions, and writes
the PDF, cover, document sidecar and source receipt under
`hardware/gun-positioner-guide/`.

The page furniture comes from `tools/hsm/fabrication-guides/src/letter.rs`. IBM Plex
Sans/Mono are embedded from the shared guide assets. Coral identifies parts
used by an operation; dark grey depicts the printed fixture. Assembly
pictures, parts panels and numbered actions remain together by operation.
The contents and native PDF bookmarks are generated from the final pagination.
Continued pages name their operation or chapter in the running header. A screw
cutting schematic shows the backing nut and sacrificial nut held in the saw vise.

`art gun-positioner-guide --list` lists the operation pictures; `--scenes` selects
them. `--inputs DIR` reads retained fixture inputs for a requested comparison.
`build gun-positioner-guide --reuse-art` keeps the current operation pictures.

Render every PDF page with Poppler and inspect it after a layout change.
`tools/run hsm-manual-guides qa gun-positioner-guide` checks the current guide,
print archive and controller release bindings on request.
