# Kamoer pump reference

The production assembly uses the purchased pump's scan-derived exterior. The unit and
capture archive are identified in [scan-evidence.json](scan-evidence.json). The compatibility
directory names the pump family; the captured unit is the machine's owned Kamoer pump.

The reference shows the molded head and mounting flange, motor adapter and cover, motor can
and end features, fasteners, primer and flexible outlet sleeves. Inserted LLDPE scanning
stubs are excluded. The assembly's routed tubing supplies those connections. Component
colors separate visible materials; they are not additional clearance allowances.

[scan-registration.json](scan-registration.json) fixes rigid alignment between the native
captures. [reconstruct_scan.py](reconstruct_scan.py) selects exposed pump observations and
reconstructs their exterior, retaining disconnected electrical tabs and removing tiny fusion
islands. [scan_model.rs](scan_model.rs) separates visible components and places them in the
reference's compatibility frame. Neither program takes the holder cavity as a shape target.
The normal print build consumes the frozen reference; reconstruction is manual.

[scan-model-evidence.json](scan-model-evidence.json) owns the capture hashes, reconstruction
settings, frame, motor fit and disjoint-point surface comparison. Validation selections use
geometric regions, without discarding observations that disagree with the model. Spray
thickness and absolute scanner accuracy are unmeasured. Closed reconstruction seams and
occluded internals are not an internal pump model. The sleeves describe the captured flexible
pose and do not define rigid fit allowances.

The flange underside supplies the seating datum. The reference retains the assembly's
placement frame and routed outlet stations. [physical-fit.json](physical-fit.json) contains
Derek's physical acceptance evidence for the associated printed fixture; the
[fitted-well audit](fitted-well-audit/README.md) contains its retained native surface comparison.
Those physical articles remain separate evidence from the visible pump reconstruction.

## Manual reconstruction

With the capture archive present and the PyMeshLab runtime installed, use a task-owned run
directory for the intermediate exterior:

```sh
python3 tools/run.py -- tools/cad-venv/bin/python hardware/reference/kamoer-kphm400/reconstruct_scan.py --out .cache/runs/kamoer-reference
python3 tools/run.py -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml -p hsm-sandbox --example kamoer-scan -- .cache/runs/kamoer-reference/observed-exterior.npz hardware/reference/kamoer-kphm400
python3 tools/run.py -- tools/cad-venv/bin/python hardware/reference/kamoer-kphm400/reconstruct_scan.py --validate hardware/reference/kamoer-kphm400/kamoer-kphm400.step.npz --out .cache/runs/kamoer-reference/scan-model-evidence.json
```

The reconstruction command accepts relocated archive and runtime paths. The frozen manifest
names the published STEP, fine model and viewer payload by digest. These reference assets
remain outside source control.
