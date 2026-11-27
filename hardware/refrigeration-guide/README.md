# Refrigeration bench guide

[Refrigeration bench guide](https://homesodamachine.com/read/refrigeration-guide/refrigeration-guide.pdf) covers evaporator fabrication,
the Antarctic Star donor, charge removal, brazing, pressure test, vacuum, charge and
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
| 13 | Remove the donor charge outdoors |
| 14 | Prove the inert sweep before heat |
| 15 | Cut at the evaporator |
| 16 | Remove the hot-gas branch |
| 17 | Put the probes on the copper |
| 18 | Wet rag on each stub |
| 19 | Braze the suction coupling |
| 20 | Pinch-swage the capillary |
| 21 | Pressure-test the inert circuit |
| 22 | Pull vacuum and isolate the pump |
| 23 | Weigh in 16.0 g net |
| 24 | Read the gram on the scale |
| 25 | Follow the 16.0 g trial |
| 26 | Time what the wall probe reads |
| 27 | Read both instruments at B |
| 28 | See where the frost ends |
| 29 | Measure the liquid in the glass |
| 30 | Isolate the service set |
| 31 | Place the gas sensor first |
| 32 | Lower the compressor |
| 33 | Seat the condenser and fan |
| 34 | Seat the thermal cutoff |
| 35 | Prove the controls before first start |
| 36 | Check the condenser air path |
| 37 | Read the first powered run |
| 38 | Sweep the actual joint seams |
| 39 | Locate the joints on the machine |
| 40 | Find the high and low seams |
| 41 | Stop on a detector alarm |
| 42 | Repeat the run under the same load |
| 43 | Read the low-side numbers |
| 44 | Check all four glass readings |
| 45 | Decide the next gram |
| 46 | Read the cold controls in service |
| 47 | Repair through the full sequence |
| 48 | Save the checks with the unit |
| 49 | Read the condenser outlet |
| 50 | Check frost near the compressor |
| 51 | Follow the example decisions |

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
  the basis for the charge estimate and tabulated measurement plan.

Bench instrument references:

- [P3 Kill A Watt P4400 manual](https://www.p3international.com/manuals/p4400_manual.pdf)
  covers the on-hand meter. The first repeatable trace supplies the running comparison.
- [TopTes PT520A manual](https://cdn.shopify.com/s/files/1/0651/5952/8680/files/PT520A.pdf?v=1768791404)
  gives the on-hand locator's settings. [INFICON GAS-Mate manual](https://www.inficon.com/media/5821/download/Operating-Manual---GAS-Mate-%28English%29.pdf?inline=true&language=en&v=1)
  gives the charged-sweep settings. [Whirlpool A3 service manual](https://www.whirlpool.com/content/dam/global/documents/202409/technical-manual-w11105483-revb.pdf)
  covers work-area monitoring.
- [ThermoWorks ThermoPop 2](https://www.thermoworks.com/products/thermopop-2)
  is a quick-read option for dispensed-water samples.

## Bench inventory and open items

The [refrigeration purchases](../ledger/purchases.md#6-refrigeration) and [tool ledger](../ledger/tools.md#refrigeration-assembly) record the acquired equipment. The donor retains its capillary, bonded suction line and factory drier. The household donor uses controlled outdoor charge removal. [Household end-use basis](../../business/regulatory.md#epa-section-608--refrigerant-handling)

| Job | On hand | Confirm or obtain |
|---|---|---|
| Copper work | ACR copper, cutters, bender, straightener, flaring tool, Knipex wrench, coupling, torch, filler and prep pads | Verify tail and discharge-tee dimensions on the actual donor before choosing the rejoin. |
| Access and closure | Supco BPV31, flare hardware | Measure the process tube OD and usable straight length. Confirm temporary access for R600a, an outdoor discharge hose and a matched permanent seal. The [Yellow Jacket 61010](https://yellowjacket.com/product/hydrocarbon-charging-kit/) is a documented hydrocarbon tap for its listed tube sizes. Supco's FAQ directs removing its solderless tap after service. [Supco](https://supco.com/web/supco_live/products/BPV31.html) |
| Purge and pressure test | Airgas argon, RX Weld flowmeter, metal metering branch, separate Uniweld RHP400 nitrogen regulator and SENCTRL pressure gauge | Verify the refrigeration-side connection and open argon flow. Confirm the regulator, pressure limit, isolation and gauge for a static test. The RHP400 uses nitrogen. Obtain bubble fluid if needed. [Uniweld](https://www.uniweld.com/product/nitrogen-regulators/) · [Big Blu RT175B](https://www.refrigtech.com/big-blu-brush-on/) |
| Evacuation | Orion pump and manifold are in the ledger | Obtain an A3 vacuum pump, a circuit-side micron gauge and short R600a-compatible manifold hoses. The Orion documentation covers other refrigerants. Equipment that meets these roles includes the [CPS VPS6DU](https://www.cpsproducts.com/product-details/vps6du/), [BluVac+ Micro](https://accutools.com/wp-content/uploads/2017/09/BluVacMicro-Manual.pdf) and [Mastercool 93518-TP](https://mastercool.com/product/r600a-r290-r134a-2-way-aluminum-manifold-gauge-sets-thermoplastic-capillary-hoses/). |
| Weighed fill | Enviro-Safe R600a cans and tap/gauge, Smart Weigh Pro | Weigh the entire sealed detachable transfer path before and after. It stays within the scale's capacity and uses a proved low-loss split at the circuit valve. Pages 23 and 24 give the display targets. |
| Leak checks | TopTes PT520A for cool, isolated localization after clearance. MQ-6 for the appliance interlock. | Obtain the R600a charged-circuit wand and a known reference. Arrange continuous work-area monitoring and the clearance check. [GAS-Mate](https://www.inficon.com/en/products/leak-detectors/gas-mate-combustible-gas-leak-detector) · [R600a TEK-Check reference](https://www.inficon.com/en/products/leak-detectors/tek-check) |
| Water and first run | Kill A Watt P4400, built-in wall and coil probes, stainless DS18B20 bench spare and separate ESP32 | Check the separate immersion reader against an ice-water reference. Use the wall probe for matching pull-down runs. |

## Measurement setup

The blue and red gauges supplied with the Mastercool 93518-TP read pressure for
service and broad trends. Their class 1.6 dial spans are too wide for the direct
charge tables. The bench screens on pages 43 and 49 use an absolute gauge within
0.5 psia of actual local line pressure and an insulated contact reading within
1 °C of actual tube temperature, including contact error. The installed coil
probe stays under the foam for freeze protection. Use separately mounted tube
clips at the paired stations. [Mastercool gauges](https://mastercool.com/product/3-18-gauges-2/) · [Fieldpiece contact-probe manual](https://resources.fieldpiece.com/wp-content/uploads/2020/11/Opman-JL3PC-v21.pdf)

Set the absolute pressure readout to psia with its tare disabled. A calibrated
intrinsically safe WIKA CPG1500 in the 0–300 psia range at 0.1% of span is one
instrument choice. Use an R600a-compatible low-volume connection for the actual
station and keep that fixture in the pressure-tested circuit throughout the
comparison. A and C are needed to justify an addition. B is the compressor-inlet
screen. [WIKA operating instructions](https://www.wika.com/media/Operating-instructions/Operating-instructions/Calibration/Digital-pressure-gauges/oi_cpg1500_en_de.pdf) · [WIKA configurator](https://shop.wika.com/en-us/cpg1500.WIKA)

The printed limits use the warmest plausible saturation temperature at the
upper pressure-bin edge for the B and A temperature floors and the C LOW
column. B allows a lower-bound vapor margin of 5 K, consistent with conservative
small hydrocarbon practice. A flags a clearly warm outlet with at least 10 K
of superheat. C LOW means at most 3 K of subcooling, and C HELD means at least
5 K, using the coldest plausible saturation temperature for HELD. Whole-degree
rounding and both measurement errors are already included in the lookups.
These are prototype comparison screens. Intertek supplies donor design pressure
ratings and charge, and the finished machine supplies the actual load results.
[NIST saturation data used by the tables](https://webbook.nist.gov/cgi/fluid.cgi?PLow=5.5&PHigh=140.5&PInc=1&Digits=8&ID=C75285&Action=Load&Type=SatT&TUnit=C&PUnit=psia&RefState=DEF) · [Embraco small-charge hydrocarbon superheat guidance, §11.5](https://www.embraco.com/wp-content/uploads/2020/07/1593699607eweb-installation-instructions-052020-en.pdf)

## Why the first fill is 16.0 g

The U.S. HZB-12/Q entry in Intertek report SH10080445-001 gives the factory
R600a mass. The nominal EVAP-01 tube has about 86 mL of internal volume before
tail trim and 72 mL in the winding. At an illustrative -10 °C evaporation
temperature and 30 °C liquid-equivalent inlet, the homogeneous and Zivi models
give 0.47 g and 1.44 g in the new coil. Across the modeled -20 to -5 °C evaporation
and 20 to 35 °C inlet window they span about 0.3 to 2.2 g. The calculation uses
the nominal tube bore, inlet enthalpy after the bonded exchanger, and dryout
late in the winding. The removed factory evaporator and bypass also held some
charge, and about 2 mL of liquid at 40 °C represents about 1 g elsewhere in the
circuit. That supports a first trial of 16.0 g with no modeled grams added to
the factory value. [Intertek report](https://device.report/m/ba17ebc69382c7509ea70d4e77dfa9bc9ae002417ea8c0af0e913a8b8f89de70) · [EVAP-01](../cold-core-layout/evaporator-coil-drawing.pdf) · [NIST properties](https://webbook.nist.gov/cgi/fluid.cgi?ID=C75285&Action=Page) · [Void-fraction models](https://info.ornl.gov/sites/publications/Files/Pub57653.pdf)

## Qualification scope

The Section 608 exemption follows the verified household end-use. Confirm the
outdoor discharge location, safe bench setup and compatible equipment before opening
the donor. [Bench setup](https://homesodamachine.com/read/refrigeration-guide/refrigeration-guide.pdf#page=11)

The certification mass is the first commissioning fill. The inventory example
describes a modeled operating state. Record the installed refrigerant charge
and repeatable water-load results after the physical trials. Qualification of
the flammable-refrigerant service setup and final process-tube closure is open.

## Manual rebuild and printing

This document is built by hand, outside the appliance build graph. It imports no CAD
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
