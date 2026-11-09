# Kamoer pump reference

The purchased pump reference uses smooth primitive solids for the visible hardware.
The owned unit and capture archive are identified in [scan-evidence.json](scan-evidence.json).
The compatibility directory names the pump family.

[scan_model.rs](scan_model.rs) constructs the rounded head, flat mounting flange,
plain motor adapter, cylindrical motor, fasteners, primer and outlet sleeves.
Principal dimensions and connection stations come from the registered observations
and retained part measurements. Flat faces stay planar and the motor stays cylindrical.
The reference omits molded pockets, ribs, lettering, motor vents and scan texture.
The flange retains its mounting holes. The motor retains its bearing boss and electrical tabs.

The flange underside supplies the seating datum. The model retains the assembly's
placement frame, component names and routed outlet stations. The flexible sleeves
use straight nominal tube passages; inserted LLDPE scanning stubs are excluded.
The reference is an exterior placement model. It does not model pump internals.

[scan-registration.json](scan-registration.json) fixes alignment between native captures.
[scan-model-evidence.json](scan-model-evidence.json) retains the capture registration,
barrel fit and reconstruction evidence, identified by its own artifact hashes.
[simplified-model-evidence.json](simplified-model-evidence.json) describes the current
primitive model and its verification. Scan texture and omitted molded details are
not surface targets. Spray thickness and absolute scanner accuracy are unmeasured.

[physical-fit.json](physical-fit.json) contains Derek's physical acceptance evidence
for the associated printed fixture. The [fitted-well audit](fitted-well-audit/README.md)
contains its retained native surface comparison. Those physical articles are separate
from this reference model.

## Manual generation

Run the reference producer from the repository root:

```sh
python3 tools/run.py -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml -p hsm-sandbox --example kamoer-scan -- hardware/reference/kamoer-kphm400
```

The producer needs no scan archive or reconstructed mesh. The normal print build
consumes the frozen reference. [frozen-asset.json](frozen-asset.json) names the STEP,
fine model and viewer payload by digest; generated reference assets stay outside
source control. Publication replaces the reference in the website's existing scenes.
