# Diaphragm pump measurements

The **G Ganen B07F35PTFR** is Derek's selected received diaphragm pump for the
enclosure. Its [measured reference](../g-ganen-pump/README.md) uses three archived
native scan views at unit scale. Derek confirms four identical removable rubber
feet with pads approximately 7 mm thick. Their selected installation uses fully
engaged rail-end positions; raw scan poses remain separate observations.

With `4002` upright and readable, the flow arrow points right, past the `2`.
Installed flow is **enclosure −X**: discharge on −X and suction on +X.
The [integration map](g-ganen-integration.md) names the current consumers;
[print readiness](../../printed-parts/enclosure/print-readiness.md) records the
current build and queue. The power supply reference is
[Mean Well IRM-90-12ST](/hardware/reference/meanwell-irm90/README.md).

| Sample | Purchase | Current record |
|---|---|---|
| G Ganen, advertised 12 V / 110 psi / 4.5 L/min | [B07F35PTFR](https://www.amazon.com/dp/B07F35PTFR) | Received; selected by Derek; measured reference and identical-foot installation |
| IEIK, advertised 12 V / 60 W / 116 psi / 5 L/min | [B07YXTHNRQ](https://www.amazon.com/dp/B07YXTHNRQ) | Ordered; receipt and measurements not recorded |

Both belong to Amazon order 112-0884852-3444230. Paid amounts and shipment
records live in [purchases.md](/hardware/ledger/purchases.md), with allocation in [inventory.md](/hardware/ledger/inventory.md).
The advertised pressure and free-flow figures are separate endpoints, not a
measured operating point.

## Received-part record

Use the mounting-foot underside as Z = 0, the motor axis as X (positive toward
the motor rear), the motor-to-head mating plane as X = 0, and the shaft's
centreline as Y = 0. Record the label, each measured feature and a photograph
with its datum visible. Dimensions include fittings, switch housing and feet;
packaging dimensions do not enter this table.

| Measurement | G Ganen | IEIK |
|---|---|---|
| Received date, model/label and sample identifier | Present September 20; G Ganen identity confirmed by Derek; full label pending | Unmeasured |
| Overall native bounds, mm | Bound to the current [reference manifest](../g-ganen-pump/artifact-manifest.json); sliding-foot pose is stated separately | Unmeasured |
| Motor can diameter and length, mm | Exposed diameter 49.110; straight reference band X=0–76; see measured reference | Unmeasured |
| Foot outline, thickness and opening, mm | One shared foot: nominal 7 mm pad, 18 mm width, R9 nose; visible 4.5 × 6.8 obround slot. [Evidence](../g-ganen-pump/common-foot/README.md) | Unmeasured |
| Selected mounting stations, mm | Slot centres X=9.5/67.5, Y=±38.5; each screw 1.5 outward within its slot. Feet remain movable. | Unmeasured |
| Inlet and outlet barb profiles, mm | Independent measured profiles in the [reference](../g-ganen-pump/README.md); actual insertion and retention checked during assembly | Unmeasured |
| Port-tip coordinates and directions from the datums | Independently measured suction/discharge tips and axes in the reference | Unmeasured |
| Switch/adjuster protrusion and lead exit | Rigid crown/casing features modeled; flexible wire route remains an integration item | Unmeasured |
| Mass, g | Unmeasured | Unmeasured |
| Label current, switch setting and manufacturer inlet-pressure limit | Unrecorded | Unrecorded |

Hydraulic or powered testing has a separate record: supply voltage at the pump,
inlet pressure, outlet pressure, flow, running/start current, switch cut-in/cut-out,
temperature and run duration. Verify each sample's permitted inlet pressure before
connecting it to house pressure. A size match alone does not qualify a pump for
the production water path.

The [conditional Plan B](/future/carbonation-plan-b.md) defines the performance
comparison. Selection and scan geometry do not supply an operating-point test.
