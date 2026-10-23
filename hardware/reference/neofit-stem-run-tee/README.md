# neoFit run-stem tee

**ATRU444-E**, 1/4-inch OD male run stem with two female 1/4-inch push-fit sockets. The native frame has its junction at the origin, stem along −X, opposite socket along +X, and branch socket along −Y. Dimensions are millimetres.

The [manufacturer dimensional sheet](https://assets.freshwatersystems.com/image/upload/s--rN_5qBOD--/nvkzj79bbgumy8drpkff.pdf), ATRU444 row, supplies the 48.006 mm total run length, 21.0058 mm stem projection, 21.0058 mm socket reaches, 15.494 mm maximum collar diameter and 16.891 mm female insertion depth. `dimensions.json` preserves the inch values and datum interpretation. The [product photographs](https://www.freshwatersystems.com/products/neofit-acetal-black-stem-run-tee-1-4-tube-x-stem-1-4) supply the undimensioned exterior transitions. Collar, collet and root details are estimated; internal gripping parts and seals are omitted.

The complete stem remains in the model. In a matching neoFit socket, nominal insertion is 16.891 mm and the stem shoulder stands 4.1148 mm from the host's resting mouth. For another host, use its own depth: the measured JG tee is 11.65 mm from the resting face, and unmeasured valve/check sockets use a 12.7 mm layout estimate (10–15 mm range). These place the shoulder 9.3558 mm and 8.3058 mm from the host mouth respectively. No layout assumes the stem disappears all the way to its shoulder.

`neofit-stem-run-tee.step` and `neofit-stem-run-tee.npz` contain the same native shape. The NPZ keys are `v` and `f`. `neofit_stem_run_tee.py` provides `build()` and `ports()`. This is a component-layout reference; exterior estimates do not establish fit, pressure performance or material qualification.

```sh
PYTHONPATH=. tmp/takeover/cadq "neoFit run-stem tee reference" -- tools/cad-venv/bin/python hardware/reference/neofit-stem-run-tee/neofit_stem_run_tee.py
```
