# Gas-chain fit and the shell print

The back-top carries the WR1110 and GASHER cradles, the rigid gas-fitting ceiling
pockets and related hose supports. The WR1110 exterior follows two native MINI 2
scans; its [measurement record](../../../../reference/wr1110-regulator/README.md)
describes the dimensions, evidence and limits. The made-up fittings remain a
physical fit observation. The [source audit](source-audit.json) names the exact
source and stored Box it reads.

| Back-top feature | Modeled part | Printed fit | Remaining observation |
|---|---|---|---|
| WR1110 barrel cradle | Scanned Ø18.87 mm; 35.4 mm straight barrel | Ø19.17 mm; 9.5 mm rib length | Physical seating and tie retention |
| GASHER inlet cradle | Nominal Ø15.5 × 11 mm round inlet boss | Ø15.8 mm; 9.5 mm rib length | Actual boss OD and clear length |
| Gas-fitting ceiling pockets | PI010822S nominal 18.5 mm external reach; PI450822S nominal 26 mm body with insertion bounded by its mate | 2 mm plan air and 1 mm crown air over each envelope | Actual adapters' made-up reaches, steps and maximum diameters |

The WR1110 cradle has 12.95 mm axial margin to each end of its modeled round band.
The GASHER rib has 0.75 mm nominal margin at each end. The modeled tube-mouth spans
are 98.97 mm for WR1110 and 73.5 mm for GASHER. The WR1110 female adapter is seated
at its measured outlet shoulder; its 9.18 mm insertion is a layout assumption,
not a measurement of assembled NPT engagement. The check uses nominal 11 mm insertion.

The assembly scorecard keeps the gas-fit item as a warning. The remaining geometry
observation is the received GASHER boss and the external envelope of both made-up
units, including actual collet reaches from the bearing datum. Actual hose bends,
insertion, wrench handling and tie retention are read on the physical assembly.
Engagement, sealing, material/rating confirmation and operating performance remain
assembly and commissioning qualifications.

Gas fitting uncertainty concerns the back-top's physical fit. It does not prevent
an unpowered enclosure assembly trial or determine the front-top's tee, spring,
release-plate and cartridge geometry. Neither lower quadrant has a direct gas
cradle or fitting-pocket dependency.

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-readiness/gas-chain-shell/audit_source.py
```

The audit parses source constants and the stored Box. It does not build geometry
or release a printer job.
