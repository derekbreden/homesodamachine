# Refrigeration bench guide

[Refrigeration bench guide](refrigeration-guide.pdf) covers evaporator fabrication,
the Antarctic Star donor, recovery, brazing, pressure test, vacuum, charge and
water-load commissioning in illustrated Letter pages.

The diagrams use coral for the current work, copper for refrigerant tubing and blue
for tools, measurements and movement. They are schematic; dimensions and the
actual donor govern. The page furniture follows the approved Letter drilling and
welding sheets, with the weld-rotator guide's one-picture-per-step approach.

## Pages

| Page | Operation |
|---|---|
| 1 | Cold-loop map, order and picture conventions |
| 2 | Identify the Antarctic Star donor and the U.S. certification rating |
| 3 | Trace the circuit; keep the factory drier and capillary, mark what comes out |
| 4 | Reserve coil stock and the unequal inlet/outlet allowances |
| 5 | Wind and remove the coil from the printed mandrel |
| 6 | Mount the bare-wall probe and calibrated reed bridge; apply foil |
| 7 | Transfer the coil; bond the suction-end probe |
| 8 | Route the two tails and measure protrusion from the shell exits |
| 9 | Isolate power and support the donor during casing removal |
| 10 | Recover the factory charge through qualified process-tube access |
| 11 | Set up the argon purge and verify its open flow paths |
| 12 | Cut the suction line and cap tube at the evaporator; strip the ice-making path |
| 13 | Wrap a wet rag hard against each shell exit before each braze |
| 14 | Braze the suction slip coupling dry under argon |
| 15 | Pinch-swage the coil-inlet stub onto the cap tube and braze it |
| 16 | Pressure-test, pull vacuum and record the isolated hold |
| 17 | Meter the first trial charge from the U.S. rating |
| 18 | Estimate wrapped-coil inventory and see what changes the total |
| 19 | Seal the access and record the charge between trials |
| 20 | First run-up and leak sweep at every joint |
| 21 | Orient and seat the low-mounted MQ-6 module |
| 22 | Lower and fasten the compressor on its grommet/post stacks |
| 23 | Seat the condenser/fan in its rails and aft mount fingers |
| 24 | Seat and inspect the insulated thermal-cutoff clamp |
| 25 | Prove real probe readings, fan/control path and first start |
| 26 | Measure pressure, temperature and cooling under the same water load |
| 27 | Choose and verify the next weighed charge |
| 28 | Verify firmware limits and the loaded refrigeration result |
| 29 | Repair a leak through the full sequence |
| 30 | Keep the per-unit measurements |

## Responsible sources

- [Cold-core assembly](../assembly/cold-core.md), [handwork](../assembly/handwork.md),
  [coil mandrel](/hardware/printed-parts/cold-core/coil-mandrel/coil_mandrel.rs) and
  [copper feed-throughs](../printed-parts/cold-core/foam-shell/README.md#copper-feed-throughs) supply stock,
  winding datums, probe placement, tail routing and the foam-work handoff.
- [Refrigerant loop](../assembly/refrigerant-loop.md) supplies the circuit order,
  the argon purge, the vacuum and recharge targets and the procedure's open items.
- [Donor ice maker](../reference/ice-maker/README.md),
  [compressor](../reference/compressor/README.md) and
  [condenser block](../reference/condenser-block/README.md) supply the actual donor
  evidence for the harvested assembly and its process-tube location.
- [Enclosure assembly](../assembly/enclosure-mechanical.md),
  [mechanical fasteners in the BOM](../ledger/bom.md),
  [fuse clamp](../printed-parts/refrigeration/fuse-clamp/README.md) and
  [mechanical qualification](../mechanical-qualification/README.md) supply mount order, nominal fit and the installed
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
- [Intertek constructional report SH10080445-001](https://device.report/m/ba17ebc69382c7509ea70d4e77dfa9bc9ae002417ea8c0af0e913a8b8f89de70.pdf#page=3),
  U.S. HZB-12/Q refrigerant and charge rating.
- [Secop hermetic service guide](https://www.secop.com/fileadmin/user_upload/technical-literature/guidelines/repair_of_hermetic_refrigeration_systems_05-2018_desg620a202.pdf)
  and [Supco BPV31 product FAQ](https://supco.com/web/supco_live/products/BPV31.html),
  equipment suitability and service closure.
- [NIST isobutane properties](https://webbook.nist.gov/cgi/fluid.cgi?ID=C75285&Action=Page),
  [ORNL void-fraction models](https://info.ornl.gov/sites/publications/Files/Pub57653.pdf)
  and [ASHRAE capillary systems](https://handbook.ashrae.org/Handbooks/R26/SI/r26_ch11/r26_ch11_si.aspx),
  the basis for the inventory example and measurement plan.

## Qualification scope

The certification mass is the first commissioning fill. The inventory example
describes a modeled operating state. Record the installed refrigerant charge
and repeatable water-load results after the physical trials. Qualification of
the flammable-refrigerant service setup and final process-tube closure is open.

## Manual rebuild and printing

This is a committed document, outside the appliance build graph. It imports no CAD
or hardware generators. Rebuild deliberately after reviewing a changed operation:

```bash
tools/run hsm-manual-guides build refrigeration-guide
```

Review every rendered page before committing a rebuild. The builder writes the
delivery PDF and source-hash receipt under `output/pdf/`, and an identical PDF,
cover and catalog sidecar here. Footer links open the responsible GitHub document
or manufacturer source. Shared typography and vector primitives live in
`tools/hsm/fabrication-guides/src/letter.rs`; the editable operations and
schematic drawings are in [pages.json](pages.json).

Print one-up, single-sided, Letter borderless, no driver scaling. On the calibrated
Epson ET-8550 photo setup use the **rear feeder**, photographic-glossy media and
high quality. The instructional layer is already centered at 98%; the background
extends 1/4 in outside every edge and its colored bands extend 1/3 in inward.
