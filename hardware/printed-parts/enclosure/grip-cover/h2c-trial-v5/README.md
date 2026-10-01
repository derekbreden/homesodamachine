# H2C grip receiver v5 trial

**Cancelled before submission.** This receiver package is not approved for
printing. The user accepts the curved receiver's printed result and is
coordinating the production design with Grips.

This plate contains the front and back receiver coupons for the constant roof
profile and 3 mm square end walls. The unchanged grip insert from the Mark2 v4
plate fits this receiver in CAD; physical fit and support removal remain to be
tested. Full enclosure printing is held.

The receiver-only native slice passes [preflight](preflight.json) and
[support review](support-audit.json). Estimated duration is **1 hour 1 minute**,
with 28.59 g of black PET-GF using the saved profile's density estimate.

- Production floor-down orientation; fixed left hardened 0.4 mm nozzle.
- H2C requested Z trim +0.18 mm; emitted textured-plate trim +0.16 mm.
- First bed layer 0.20 mm; subsequent layers 0.24 mm.
- Six walls only from print Z 35.0–41.5 mm; saved speeds, wall order and 15% overlap.
- Shared PET-GF tree supports: 0.40 mm XY, 0.45 mm top Z, 0.30 mm bottom Z.
- Both support bodies grow from the bed, with 34.32 mm build-up. Their contact
  envelope stays below the exterior expanding transition.
- Normal Connect options: Timelapse On, Auto bed leveling On, flow calibration
  Auto and nozzle-offset calibration Auto.

The prepared archive is
`.cache/prints/grip-receivers-h2c-v5/ready/grip-receivers-h2c-v5.gcode.3mf`.
Hashes and source identities are in [preparation.json](preparation.json) and
[preflight.json](preflight.json). The import copy has the same hash.

Run the preparation and verification from the repository root:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/enclosure/grip-cover/h2c-trial-v5/prepare.py
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/enclosure/grip-cover/h2c-trial-v5/verify.py
```

The builder refuses to overwrite an existing reviewed project. It prepares files
only; printer submission uses Bambu Connect after the plate is confirmed clear.
