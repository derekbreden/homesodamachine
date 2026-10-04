# Refrigeration bench guide

[Refrigeration bench guide](refrigeration-guide.pdf) is 28 illustrated 8.5 x 11 in
pages, one operation per page. It covers evaporator fabrication, donor preparation,
refrigerant-circuit service, installed mounts and refrigeration commissioning.

The diagrams use coral for the current work, copper for refrigerant tubing and blue
for tools, measurements and movement. They are schematic; dimensions and the
actual donor govern. The page furniture follows the approved Letter drilling and
welding sheets, with the weld-rotator guide's one-picture-per-step approach.

## Pages

| Page | Operation |
|---|---|
| 1 | Cold-loop map, order and picture conventions |
| 2 | Read and record donor/compressor labels |
| 3 | Trace the circuit and mark retained/removed components |
| 4 | Reserve coil stock and the unequal inlet/outlet allowances |
| 5 | Wind and remove the coil from the printed mandrel |
| 6 | Mount the bare-wall probe and calibrated reed bridge; apply foil |
| 7 | Transfer the coil; bond the suction-end probe |
| 8 | Route the two tails and measure protrusion from the plug faces |
| 9 | Isolate power and support the donor during casing removal |
| 10 | Stage the qualified hydrocarbon-service setup |
| 11 | Remove the donor charge through controlled process access |
| 12 | Cut out the factory evaporator and close the harvest bypass |
| 13 | Clear high/low branches and install a compatible new drier |
| 14 | Fit the suction slip coupling without stress |
| 15 | Qualify the capillary-to-coil forming/brazing joint |
| 16 | Qualify plug thermal protection; braze the installed joints |
| 17 | Pressure leak-test the closed circuit |
| 18 | Measure evacuation and isolated absolute-pressure behavior |
| 19 | Meter a qualified charge, including hose inventory |
| 20 | Finish permanent process closure and test the final seal |
| 21 | Orient and seat the low-mounted MQ-6 module |
| 22 | Lower and fasten the compressor on its four grommet/post stacks |
| 23 | Seat the condenser/fan in its rails and aft mount fingers |
| 24 | Seat and inspect the insulated thermal-cutoff clamp |
| 25 | Prove real probe readings, fan/control path and first start |
| 26 | Verify firmware limits and the loaded refrigeration result |
| 27 | Follow diagnosis and the complete repair sequence |
| 28 | Keep the per-unit measurements and qualification scope |

## Responsible sources

- [Cold-core assembly](../assembly/cold-core.md), [handwork](../assembly/handwork.md),
  [coil mandrel](../printed-parts/cold-core/coil-mandrel/coil_mandrel.py) and
  [copper plugs](../printed-parts/cold-core/copper-plugs/README.md) supply stock,
  winding datums, probe placement, tail routing and the foam-work handoff.
- [Refrigerant loop](../assembly/refrigerant-loop.md) supplies the service order,
  project process targets and local qualification hold points.
- [Donor ice maker](../reference/ice-maker/README.md),
  [compressor](../reference/compressor/README.md) and
  [condenser block](../reference/condenser-block/README.md) supply the actual donor
  evidence and the limits of Unit B's recorded teardown.
- [Enclosure assembly](../assembly/enclosure-mechanical.md),
  [mechanical fasteners in the BOM](../ledger/bom.md),
  [fuse clamp](../printed-parts/refrigeration/fuse-clamp/README.md),
  [mechanical qualification](../mechanical-qualification/README.md) and
  [concerns](../concerns.md) supply mount order, nominal fit and the installed
  evidence still required.
- [Firmware commissioning](../assembly/firmware-and-commissioning.md),
  [shipping firmware](../../firmware/src_appliance/README.md),
  [cold policy](../../firmware/lib/machine_policy/cold_policy.h) and
  [acceptance](../assembly/acceptance-and-burn-in.md) supply sensor identity,
  control guards, smoke-test scope and proposed loaded-test defaults.
- [Regulatory](../../business/regulatory.md) records the residential household
  classification basis and its scope.

Manufacturer/service sources checked October 4, 2026:

- [Secop, hermetic-system repair](https://www.secop.com/fileadmin/user_upload/technical-literature/guidelines/repair_of_hermetic_refrigeration_systems_05-2018_desg620a202.pdf),
  especially circuit opening, drier replacement, evacuation equipment and mass charging.
- [Secop, R600a/R290 service](https://www.secop.com/sustainability/natural-refrigerants/compressor-service),
  personnel, separate nitrogen clearing, flowing protection and exhaust arrangement.
- [Supco BPV31 instructions and FAQ](https://supco.com/web/supco_live/products/BPV31.html),
  including removal of solderless temporary access after repair.
- [Uniweld RHP400 specifications](https://www.uniweld.com/product/rhp-special-purpose-series/),
  nitrogen listing and 20-400 PSIG published delivery range.
- [Orion VPH-BN0A-O1/O2 manual](https://orionmotortech.com/cdn/shop/files/new_VPH-BN0A-O1_VPH-BN0A-O2.pdf?v=10939169087783086859),
  named compatible refrigerants. This is not a verified exact-model approval of the owned pump.
- [Harris Stay-Silv 15 technical sheet](https://ch-delivery.lincolnelectric.com/api/public/content/7cdc09a3e3364eca8d9ecb0145977257?v=7aae3e72),
  copper-to-copper use without flux.
- [EPA Section 608 venting rules](https://www.epa.gov/section608/stationary-refrigeration-prohibition-venting-refrigerants),
  end-use-specific handling scope.

## Qualification scope

This guide establishes a source-reviewed illustrated sequence. It contains no new
installed refrigeration, thermal, charge or load acceptance result. Hold points are
attached to their operation: exact HC service-equipment suitability, circuit test
limits, replacement-drier/capillary connection, bypass closure, capillary swage,
printed-plug heat protection, final process closure, isolated-vacuum criterion,
finished-machine charge and installed commissioning evidence. Secop's general
service guidance is not a manual or qualification for the harvested compressor.

The 500-micron evacuation target, 15-minute observation windows and +/-1 g charge
metering target are project process targets. A gauge trace still needs its committed
decay criterion, and metering needs an accepted target plus hose-inventory accounting.
The proposed acceptance duration and duty-cycle band do not establish lifetime.

## Manual rebuild and printing

This is a committed document, outside the appliance build graph. It imports no CAD
or hardware generators. Rebuild deliberately after reviewing a changed operation:

Use Python 3 with `reportlab` and `Pillow`, and Poppler's `pdftoppm` on `PATH`.

```bash
python3 tools/refrigeration-guide/build.py
pdftoppm -r 150 -png output/pdf/refrigeration-guide.pdf /tmp/refrigeration-page
```

Review every rendered page before committing a rebuild. The builder writes the
delivery PDF and source-hash receipt under `output/pdf/`, and an identical PDF,
cover and catalog sidecar here. Footer links open the responsible GitHub document
or primary service source. Shared typography and vector primitives live in
`tools/assembly-guides/common.py`.

Print one-up, single-sided, Letter borderless, no driver scaling. On the calibrated
Epson ET-8550 photo setup use the **rear feeder**, photographic-glossy media and
high quality. The instructional layer is already centered at 98%; the background
extends 1/4 in outside every edge and its colored bands extend 1/3 in inward.
