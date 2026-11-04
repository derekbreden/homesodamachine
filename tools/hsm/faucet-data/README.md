# Faucet dimensions and recipes

`faucet-data` supplies the faucet's shared scalar interface, tube centreline
sampling, countertop stack recipes, display-cover recipes, organizer axes and
lever PCHIP stations. Its JSON-lines `--serve` interface is used by the Python
import adapters through `hardware/scripts/_rust_data.py`.

The cover and countertop stack recipes accept the shell's scalar dimensions
and sampled passage sections. The shell and assembly providers supply those
inputs; this program computes each leaf part's derived dimensions, recipe and
document variables. Material colours come from the shared material catalogue.

The under-counter plate's analytic DXF is written directly in Rust. The
`r2010-template.dxf.in` source contains format headers, tables and blocks;
model-space lines and circular arcs are calculated by `counter_plate.rs`.
The writer preserves R2010, millimetre units and layer 0 and replaces a file
only when its bytes differ. Shared document substitution, stable file writing
and number formatting use `hsm-documents`.
