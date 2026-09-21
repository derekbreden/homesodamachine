# Diaphragm pump measurements

The **G Ganen** is Derek's selected diaphragm pump for the enclosure. The
received sample has three archived native scan views; its mounting, casing and port geometry
are under measurement for the production reference. Derek identified the sample on
September 20, 2026 and confirmed that no caliper measurements were recorded.
Scan-derived dimensions remain pending review. Derek identifies the feet as flexible rubber.
With `4002` upright and readable, the flow arrow points right, past the `2`.
The mapping of that label orientation to the model's signed port coordinates is open.

The generated enclosure still uses the
[SeaFlo SFDP1-013-100-22 reference](/hardware/reference/seaflo-22-pump/README.md)
and is not released for printing with the G Ganen. The pump reference, mounting
and tube routes must agree before that release. The [integration map](g-ganen-integration.md)
names the affected interfaces. The power supply reference is
the [Mean Well IRM-90-12ST](/hardware/reference/meanwell-irm90/README.md).

| Sample | Purchase | Current record |
|---|---|---|
| G Ganen, advertised 12 V / 110 psi / 4.5 L/min | [B07F35PTFR](https://www.amazon.com/dp/B07F35PTFR) | Received; selected by Derek; scanning September 20 |
| IEIK, advertised 12 V / 60 W / 116 psi / 5 L/min | [B07YXTHNRQ](https://www.amazon.com/dp/B07YXTHNRQ) | Ordered; receipt and measurements not recorded |

Both belong to Amazon order 112-0884852-3444230. Paid amounts and shipment
records live in [purchases.md](/hardware/ledger/purchases.md), with diagnostic
allocation in [inventory.md](/hardware/ledger/inventory.md#diagnostic).
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
| Overall length × width × height, mm | Unmeasured | Unmeasured |
| Motor can diameter and length, mm | Unmeasured | Unmeasured |
| Foot outline, thickness and mounting-hole diameter, mm | Unmeasured | Unmeasured |
| Mounting-hole centre spacing and offsets, mm | Unmeasured | Unmeasured |
| Inlet and outlet barb crest/root diameters and usable lengths, mm | Unmeasured | Unmeasured |
| Port-tip coordinates and directions from the datums | Unmeasured | Unmeasured |
| Switch/adjuster protrusion and lead exit | Unmeasured | Unmeasured |
| Mass, g | Unmeasured | Unmeasured |
| Label current, switch setting and manufacturer inlet-pressure limit | Unrecorded | Unrecorded |

Hydraulic or powered testing has a separate record: supply voltage at the pump,
inlet pressure, outlet pressure, flow, running/start current, switch cut-in/cut-out,
temperature and run duration. Verify each sample's permitted inlet pressure before
connecting it to house pressure. A size match alone does not qualify a pump for
the production water path.

The [conditional Plan B](/future/carbonation-plan-b.md) defines the performance
comparison. Selection and scan geometry do not supply an operating-point test.
