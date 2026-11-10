# WAGO splice reference family

The references show the molded housing, individual closed levers and wire-entry
mouths of the purchased connectors. The seated frame, envelope dimensions and
open-lever clearance stay with the dimensions exposed by `wago_221.py`.

The housing retains the existing model body name. `closed-levers` contains the
orange actuator solids, including the opposed faces of the stacked connector.
Both bodies belong to the fit model. The origin is at the footprint center, the
seating plane is Z = 0 and conductors enter toward +Y.

`wago_221.rs` builds the geometry on the installed `hsm` kernel. Its clean planes,
rounded outlines and shallow sockets represent exterior anatomy. Internal cage
clamps, conductor stops, labeling and microscopic molding texture are omitted.

`replica-evidence.json` identifies the manufacturer sources and distinguishes the
published envelope dimensions from visual estimates of the smaller features.
The official orthographic product images establish the lever windows, thumb-pad
outline, clear housing corners and entry-face arrangement. Their local dimensions
are approximate; a conforming feature that engages a lever pocket or entry mouth
requires a measurement of the received connector. The seated envelope remains the
mounting reference.

`terminal-interfaces.json` owns the shared pole pitch and wire-mouth heights. The
reference generator and installed wiring read these same source-frame datums.

The housing is shown in an opaque neutral color so its surfaces remain readable
in the website viewer. Orange is reserved for the actuators.

## Regeneration

    python3 tools/run.py -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
        -p hsm-sandbox --example wago-221 -- hardware/reference/wago-221

`frozen-asset.json` and `native-queries.json` accompany the exported reference.
