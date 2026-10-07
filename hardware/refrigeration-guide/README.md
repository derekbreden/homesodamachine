# Refrigeration bench guide

[Refrigeration bench guide](refrigeration-guide.pdf) is 27 illustrated 8.5 x 11 in
pages, one operation per page. It covers evaporator fabrication, donor preparation,
the vent, argon-purged brazing, vacuum and recharge of the refrigerant circuit,
installed mounts and refrigeration commissioning.

The diagrams use coral for the current work, copper for refrigerant tubing and blue
for tools, measurements and movement. They are schematic; dimensions and the
actual donor govern. The page furniture follows the approved Letter drilling and
welding sheets, with the weld-rotator guide's one-picture-per-step approach.

## Pages

| Page | Operation |
|---|---|
| 1 | Cold-loop map, order and picture conventions |
| 2 | Read and record donor/compressor labels |
| 3 | Trace the circuit; keep the factory drier and capillary, mark what comes out |
| 4 | Reserve coil stock and the unequal inlet/outlet allowances |
| 5 | Wind and remove the coil from the printed mandrel |
| 6 | Mount the bare-wall probe and calibrated reed bridge; apply foil |
| 7 | Transfer the coil; bond the suction-end probe |
| 8 | Route the two tails and measure protrusion from the plug faces |
| 9 | Isolate power and support the donor during casing removal |
| 10 | Clamp the BPV31 on the process tube for life and vent the factory charge |
| 11 | Rig the argon purge to the BPV31 and start low-pressure flow |
| 12 | Cut the suction line and cap tube at the evaporator; strip the ice-making path |
| 13 | Wrap a wet rag hard against each plug face before each braze |
| 14 | Braze the suction slip coupling dry under argon |
| 15 | Pinch-swage the coil-inlet stub onto the cap tube and braze it |
| 16 | Pull vacuum to 500 microns, then hold isolated with no rise |
| 17 | Mass-meter the recharge from factory mass plus the coil allowance |
| 18 | Close and cap the BPV31 as the permanent service point; record the charge |
| 19 | First run-up and leak sweep at every joint |
| 20 | Orient and seat the low-mounted MQ-6 module |
| 21 | Lower and fasten the compressor on its four grommet/post stacks |
| 22 | Seat the condenser/fan in its rails and aft mount fingers |
| 23 | Seat and inspect the insulated thermal-cutoff clamp |
| 24 | Prove real probe readings, fan/control path and first start |
| 25 | Verify firmware limits and the loaded refrigeration result |
| 26 | Repair a leak through the full sequence |
| 27 | Keep the per-unit measurements |

## Responsible sources

- [Cold-core assembly](../assembly/cold-core.md), [handwork](../assembly/handwork.md),
  [coil mandrel](../printed-parts/cold-core/coil-mandrel/coil_mandrel.py) and
  [copper plugs](../printed-parts/cold-core/copper-plugs/README.md) supply stock,
  winding datums, probe placement, tail routing and the foam-work handoff.
- [Refrigerant loop](../assembly/refrigerant-loop.md) supplies the circuit order,
  the argon purge, the vacuum and recharge targets and the procedure's open items.
- [Donor ice maker](../reference/ice-maker/README.md),
  [compressor](../reference/compressor/README.md) and
  [condenser block](../reference/condenser-block/README.md) supply the actual donor
  evidence: what stays, what comes out and the permanent service valve.
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

Manufacturer sources:

- [Harris Stay-Silv 15 technical sheet](https://ch-delivery.lincolnelectric.com/api/public/content/7cdc09a3e3364eca8d9ecb0145977257?v=7aae3e72),
  copper-to-copper use without flux.
- [EPA Section 608 venting rules](https://www.epa.gov/section608/stationary-refrigeration-prohibition-venting-refrigerants),
  end-use-specific venting scope.

## Qualification scope

This guide is a source-reviewed illustrated sequence. It records no completed
circuit build, charge or load test. The 500-micron evacuation target with its
15-minute pumping and isolated windows, the +/-1 g metering tolerance and the
factory-plus-5-15 g starting charge come from the refrigeration procedure; the
charge target itself is settled on first run-up, its open item 1. The proposed
acceptance duration and duty-cycle band do not establish lifetime.

## Manual rebuild and printing

This is a committed document, outside the appliance build graph. It imports no CAD
or hardware generators. Rebuild deliberately after reviewing a changed operation:

Use Python 3 with `reportlab` and `Pillow` (the CAD venv, `tools/cad-venv/bin/python`, has both), and Poppler's `pdftoppm` on `PATH`.

```bash
python3 tools/refrigeration-guide/build.py
pdftoppm -r 150 -png output/pdf/refrigeration-guide.pdf /tmp/refrigeration-page
```

Review every rendered page before committing a rebuild. The builder writes the
delivery PDF and source-hash receipt under `output/pdf/`, and an identical PDF,
cover and catalog sidecar here. Footer links open the responsible GitHub document
or manufacturer source. Shared typography and vector primitives live in
`tools/assembly-guides/common.py`.

Print one-up, single-sided, Letter borderless, no driver scaling. On the calibrated
Epson ET-8550 photo setup use the **rear feeder**, photographic-glossy media and
high quality. The instructional layer is already centered at 98%; the background
extends 1/4 in outside every edge and its colored bands extend 1/3 in inward.
