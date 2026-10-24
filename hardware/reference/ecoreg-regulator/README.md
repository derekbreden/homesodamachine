# Protect-Air EcoReg239KS1245 regulator candidate

The [45 psi EcoReg](https://store.epsgroupllc.com/ecoreg-45-psi-inline-liquid-pressure-regulator-239ks1245/)
is a fixed inline liquid regulator with female 1/4 NPT ports at both ends.
Its published body is **52 mm long and 34 mm maximum diameter**, with
17 mm wrench flats. The long inlet neck is Ø19 mm; the short outlet neck is
Ø20 mm. The body arrow runs from the long neck to the short neck.

The native frame uses **+X flow**, inlet face `(0,0,0)` and outlet face
`(52,0,0)`. The two mouth faces are named in the native body and assembly
STEP files. Axial shoulder locations and the modeled pair of wrench flats
follow the published outline approximately. The plain female socket bores
provide adapter occupancy; thread form and regulator internals are omitted.

The candidate adapter assembly uses the existing nominal JG PP010822E water
reference at each end: 18.5 mm exposed reach and 11 mm assumed thread
engagement each. Its tube mouths are **`(−18.5,0,0)` and `(70.5,0,0)`**, an
**89 mm nominal span**. This is an estimated made-up assembly, not a measured
part stack. The adapter models have an open 6.35 mm display bore; exact tube
insertion is unmeasured, with 12.7 mm retained as an explicit layout estimate.

The technical sheet specifies a Grivory housing, 45 psi preset, and 145 psi
maximum inlet for water. Instructions permit any mounting orientation while
retaining the flow direction. EPS listed **$48, six in stock, usually shipping
within 24 hours**, checked **2026-10-23**. This is a research candidate; it has
no purchase, selection or installation status.

`geometry/ecoreg-regulator.step` is the named-face body assembly;
`geometry/ecoreg-body.npz` is its portable `v`/`f` mesh.
`geometry/ecoreg-with-adapters.step` and `.npz` contain the complete nominal
candidate. Individual body/adapter STEP and NPZ files are also included.
`dimensions.json` records the source PDFs, dimensions, ports and estimates.
`model.py` exposes `library()`, `instances()`, `ports()` and intended `mates()`
without importing production CAD.

Rebuild manually through the CAD queue:

```sh
PYTHONPATH=. tmp/takeover/cadq "EcoReg water regulator reference" -- tools/cad-venv/bin/python hardware/reference/ecoreg-regulator/build.py
```

Sources: [technical data](https://store.epsgroupllc.com/content/pdf/Technical-Data-EcoReg.pdf),
[installation instructions](https://store.epsgroupllc.com/content/pdf/EcoReg-Instructions.pdf),
and the source-linked JG reference recorded in `dimensions.json`.
