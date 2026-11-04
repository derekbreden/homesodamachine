# Faucet dimensions and recipes

`faucet-data` supplies the faucet's dimensions, sampled tube paths, shell and
assembly recipes, countertop stack, display covers, collars, organizer and vent
seals. Its JSON-lines `--serve` interface is used by Python import adapters
through `hardware/scripts/_rust_data.py`. Authored dimensions and equations live
in Rust; input files remain live inputs. Material colours use `hsm-shared-data`.

The shell's lever clearance uses native GEOS union, topology-preserving
simplification and mitre buffering. `HSM_GEOS_LIBRARY` selects an explicit GEOS C
library; otherwise the loader selects the installed `tools/cad-venv` Shapely
runtime's `.dylibs` or Linux library directory. `geos-library` reports the selected
path and version. The Python package supplies the primitive library only.

The under-counter plate's analytic DXF is written directly in Rust. The
`r2010-template.dxf.in` source contains format headers, tables and blocks;
model-space lines and circular arcs are calculated by `counter_plate.rs`.
The writer preserves R2010, millimetre units and layer 0 and replaces a file
only when its bytes differ. Shared document substitution, stable file writing
and number formatting use `hsm-documents`.

Rust also restores the lever's canonical STL frame and supplies the install
plumbing scenes' dimensions, export specifications, render jobs and deterministic
RGBA PNG encoding. Python retains importable object types, process launchers and
optional CadQuery compatibility builders used by manual native-CAD callers.
