# Bambu Lab H2C toolhead

The model reconstructs the stock moving H2C print head for inspecting its underside against tilted prints. The reference includes the full moving chassis, both hotends and their mounts, the induction latch, the wraparound part cooling duct, both cameras, the flow blocker, the front enhanced fan and shroud, the internal heatsink cooling, the rear centrifugal blower, the extruder, and the local inlet and cable connections. The X beam, rail, and belt have a separate context export. The docked Vortek hotends and the printer-side latch actuator are fixed to the printer and belong to a rack model.

## Build

The [Rust model](h2c_toolhead.rs) uses the HSM sandbox to export named STEP bodies, the corresponding HSM meshes, and bounds.

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
    -p hsm-sandbox --example h2c-toolhead -- /absolute/output/directory
```

Each head export places the active tip at the origin. Positive X is the operator's right, positive Y is toward the back, and positive Z is up. The left-active file represents the Mark2 faucet study with the right induction hotend installed. The right-active file re-datums the stationary right hotend, raises the left hotend, and puts the blocker under the idle left tip. The X-axis context uses the left-active frame.

## Evidence

- Bambu's component drawings identify the assembly, both cameras, the airflow path, and the blocker. The induction heating replacement photos and the production photo establish the asymmetry of the standard left hotend and the right pickup, coil, and latch. [H2C manual](https://csm.bblcdn.com/hub/eff78da43720461787dc8bbe5fa0372d.pdf#page=17) · [Induction assembly service photos](https://wiki.bambulab.com/en/h2c/maintenance/replace-induction-heating-assembly) · [Production head photo](https://3dwithus.com/wp-content/uploads/2026/10/bambu-lab-h2c-extruder-head.webp)
- The FAF012 factory part photos show the rear inlet and the asymmetric, forward-reaching side branches. The nozzle camera service guide locates the camera near the rear bridge of the duct and the toolhead camera on the right outboard side. [Factory duct](https://us.store.bambulab.com/products/part-cooling-fan-air-duct) · [Duct service photos](https://wiki.bambulab.com/en/h2/maintenance/replace-part-cooling-fan-air-duct) · [Nozzle camera service photos](https://wiki.bambulab.com/en/h2/maintenance/replace-nozzle-camera)
- Bambu Studio's H2C reach polygons support the nominal X pitch. The calibration guide supplies a nominal difference between active-tip printing heights. The nozzle-tip and blocker positions in the two stationary poses are reconstructed using these references. [H2C machine profile](https://github.com/bambulab/BambuStudio/blob/master/resources/profiles/BBL/machine/Bambu%20Lab%20H2C%200.4%20nozzle.json) · [Nozzle offset calibration](https://wiki.bambulab.com/en/h2/manual/nozzle-offset-calibration) · [Flow blocker service photos](https://wiki.bambulab.com/en/h2/maintenance/replace-flow-blocker) · [Bambu switching mechanism](https://patents.google.com/patent/CN122401876A/en)
- Published component references include a scan of the stock shared duct, a standard left hotend CAD model, an induction right hotend CAD model, and a scan-derived enhanced-fan back cover. The downloads require account access. This reconstruction uses the public source images and dimensions visible in their listings. [Stock duct scan](https://makerworld.com/en/models/2113625) · [Left hotend](https://3dfinder.io/model/makerworld/1891089-h2s-h2d-nozzle-cad-step-datei) · [Right hotend](https://grabcad.com/library/bambu-lab-h2c-induction-hotend-1) · [Enhanced-fan back cover](https://makerworld.com/en/models/2562914)

[Photo landmarks](photo-landmarks.json) records the image ratios and scale assumptions behind the duct and camera fit. Assembly depths, lower surfaces, and the flow blocker's working height are photo-derived estimates. Use these surfaces to find potential contacts and place physical witnesses on Mark2. Clearance sign-off requires measured underside heights and XY locations in the installed print pose.
