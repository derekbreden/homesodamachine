# neoFit ACVUS-44 stem check valve

The [ACVUS-44](https://www.freshwatersystems.com/products/stem-reducer-check-valve-1-4-od-x-1-4-od-stem)
is a white acetal check valve with a 1/4-inch OD stem on one end and a 1/4-inch OD tube socket on
the other. Fresh Water Systems sells it as ACVUS-44:10PK. No purchase is recorded.

[`neofit_acvus44_check.py`](neofit_acvus44_check.py) builds its exterior from the silhouette of
FWS's side photograph (`iruw2y9vbn7aaceto1p7`, 1000 × 1000 px), sampled every 2 px down the
axis. The stem's 6.35 mm OD is 106.65 px wide, which sets the scale at 0.0595 mm/px. On that
scale the socket collar is Ø15.8 mm, against the 15.494 mm maximum collar on neoFit's
[ATRU444 sheet](https://assets.freshwatersystems.com/image/upload/s--rN_5qBOD--/nvkzj79bbgumy8drpkff.pdf).

| Feature | From the stem tip, mm | Diameter, mm |
|---|---:|---:|
| Stem | 0–15.6 | 6.35 |
| Collar | 18.0–23.7 | 15.8 |
| Check barrel | 26.0–33.5 | 9.9 |
| Socket body | 35.4–46.4 | 14.1–15.8 |
| Collet | 47.9–50.0 | 13.6 |

The stem enters a host socket up to the collar, 15.6 mm. The socket takes the tube 16.891 mm,
neoFit's 1/4-inch female engagement on the ATRU444 sheet.

Not established by the trace:

- which way the check passes flow: none of FWS's three photographs shows an arrow;
- the dimensions' tolerance: the camera looks slightly up at the part, and the ends are about
  ±0.5 mm;
- the internals, seals, collet teeth and release motion, which are not modelled;
- the cracking pressure and whether the check closes gas-tight.

neoFit's [catalogue](https://assets.freshwatersystems.com/image/upload/s--FacjKp_O--/xa3vlqau7opjabwxmc5o.pdf)
rates its check valves for 0–230 psi working pressure and 34–140 °F, with NBR O-rings.

```sh
tools/cad-venv/bin/python hardware/reference/neofit-acvus44-check/neofit_acvus44_check.py
```
