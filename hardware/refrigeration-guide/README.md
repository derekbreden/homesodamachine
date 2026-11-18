# Refrigeration bench guide

[Refrigeration bench guide](refrigeration-guide.pdf) covers evaporator fabrication,
the Antarctic Star donor, recovery, brazing, pressure test, vacuum, charge and
water-load commissioning in illustrated Letter pages.

The guide uses vector tables and diagrams alongside views of the current CAD.
Copper shows the refrigerant path and blue marks a locator or measurement.
The installed views locate the modeled features. Use the physical seams and
equipment on the bench for the inspections. [Published machine model](https://homesodamachine.com/3d)

## Pages

| Page | Operation |
|---|---|
| 1 | Build the cold loop |
| 2 | Identify the Antarctic Star donor |
| 3 | Reserve both coil tails |
| 4 | Wind the copper coil |
| 5 | Dress the bare wall |
| 6 | Transfer and bond the coil |
| 7 | Route the two exits |
| 8 | Inspect the core before foam |
| 9 | Support before teardown |
| 10 | Trace and tag the donor circuit |
| 11 | Stage the refrigeration bench |
| 12 | Set up the detector |
| 13 | Recover the factory charge |
| 14 | Prove the inert sweep before heat |
| 15 | Cut at the evaporator |
| 16 | Remove the hot-gas branch |
| 17 | Set up pressure and tube probes |
| 18 | Wet rag on each stub |
| 19 | Braze the suction coupling |
| 20 | Pinch-swage the capillary |
| 21 | Pressure-test the inert circuit |
| 22 | Pull vacuum and isolate the pump |
| 23 | Meter the recharge |
| 24 | Account for one gram |
| 25 | Estimate the running coil inventory |
| 26 | Isolate the service set |
| 27 | Place the gas sensor first |
| 28 | Lower the compressor |
| 29 | Seat the condenser and fan |
| 30 | Seat the thermal cutoff |
| 31 | Prove the controls before first start |
| 32 | Check the condenser air path |
| 33 | Read the first powered run |
| 34 | Sweep the actual joint seams |
| 35 | Locate the joints on the machine |
| 36 | Find the high and low seams |
| 37 | Stop on a detector alarm |
| 38 | Repeat the same pull-down window |
| 39 | Look up R600a saturation |
| 40 | Measure the water in the glass |
| 41 | Decide the next gram |
| 42 | Read the cold controls in service |
| 43 | Repair through the full sequence |
| 44 | Save the checks with the unit |

## Responsible sources

- [Cold-core assembly](../assembly/cold-core.md), [handwork](../assembly/handwork.md),
  [coil mandrel](/hardware/printed-parts/cold-core/coil-mandrel/coil_mandrel.rs) and
  [copper feed-throughs](../printed-parts/cold-core/foam-shell/README.md#copper-feed-throughs) supply stock,
  winding datums, probe placement, tail routing and the foam-work handoff.
- [Refrigerant loop](../assembly/refrigerant-loop.md) supplies the circuit order,
  the inert sweep, the pressure and vacuum tests, and the charge trials.
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
- [Intertek constructional report SH10080445-001](https://device.report/m/ba17ebc69382c7509ea70d4e77dfa9bc9ae002417ea8c0af0e913a8b8f89de70),
  U.S. HZB-12/Q refrigerant and charge rating.
- [Secop hermetic service guide](https://www.secop.com/fileadmin/user_upload/technical-literature/guidelines/repair_of_hermetic_refrigeration_systems_05-2018_desg620a202.pdf)
  and [Supco BPV31 product FAQ](https://supco.com/web/supco_live/products/BPV31.html),
  equipment suitability and service closure.
- [NIST isobutane properties](https://webbook.nist.gov/cgi/fluid.cgi?ID=C75285&Action=Page),
  [ORNL void-fraction models](https://info.ornl.gov/sites/publications/Files/Pub57653.pdf)
  and [ASHRAE capillary systems](https://handbook.ashrae.org/Handbooks/R26/SI/r26_ch11/r26_ch11_si.aspx),
  the basis for the inventory example and measurement plan.

Bench instrument references:

- [P3 Kill A Watt P4400 manual](https://www.p3international.com/manuals/p4400_manual.pdf)
  covers the on-hand meter. The first repeatable trace supplies the running comparison.
- [TopTes PT520A manual](https://cdn.shopify.com/s/files/1/0651/5952/8680/files/PT520A.pdf?v=1768791404)
  gives the on-hand locator's settings. [INFICON GAS-Mate manual](https://www.inficon.com/media/5821/download/Operating-Manual---GAS-Mate-%28English%29.pdf?inline=true&language=en&v=1)
  gives the charged-sweep settings. [Whirlpool A3 service manual](https://www.whirlpool.com/content/dam/global/documents/202409/technical-manual-w11105483-revb.pdf)
  covers work-area monitoring.
- [ThermoWorks ThermoPop 2](https://www.thermoworks.com/products/thermopop-2)
  is the recommended immersion probe for dispensed-water samples.

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

Regenerate the CAD plates only when their source views change:

```bash
tools/run -- hsm render --jobs hardware/refrigeration-guide/art/render-jobs.json --json
```

Review the plates and their labeled points before rebuilding the PDF. The builder writes the
delivery PDF and source-hash receipt under `output/pdf/`, and an identical PDF,
cover and catalog sidecar here. Footer links open the responsible GitHub document
or manufacturer source. Shared typography and vector primitives live in
`tools/hsm/fabrication-guides/src/letter.rs`; the editable operations and
vector annotations are in [pages.json](pages.json).

Print one-up, single-sided, Letter borderless, no driver scaling. On the calibrated
Epson ET-8550 photo setup use the **rear feeder**, photographic-glossy media and
high quality. The instructional layer is already centered at 98%; the background
extends 1/4 in outside every edge and its colored bands extend 1/3 in inward.
