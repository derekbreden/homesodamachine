# Tee-carrier sliding trial

Carrier roof clearance trial for the existing front-top. Roof gap 1.25 mm, floor gap 0.25 mm; 0.20 mm bed layer with attached 1 mm brim, then R6 bands at 0.08 mm; six walls in the lower band only; no supports. Full front-top display-receiver integration remains pending.

Native slice and source hashes are in `manifest.json`. Geometry, layers, support paths, nozzle mapping and emitted Z trim pass verification. The printer has accepted this job; physical fit is pending.

The attached brim must be removed before the sliding test. `first-layer-overlap.json` measures emitted roads at Z 0.20, 0.28 and 0.36 mm: the first transition has 99.982% outer-wall footprint coverage and no sampled outer centerline outside the previous-layer footprint. Elephant-foot compensation is zero. These are geometric toolpath checks, not a physical adhesion result.
