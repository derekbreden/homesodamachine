# Diaphragm pump measurements

The G Ganen and IEIK pumps are measurement-only purchases. The production
diaphragm pump is the [SeaFlo SFDP1-013-100-22](/hardware/reference/seaflo-22-pump/README.md),
with the [Mean Well IRM-90-12ST](/hardware/reference/meanwell-irm90/README.md).
The enclosure is designed around that pair.

| Sample | Purchase | Status verified September 16, 2026 |
|---|---|---|
| G Ganen, advertised 12 V / 110 psi / 4.5 L/min | [B07F35PTFR](https://www.amazon.com/dp/B07F35PTFR) | On order; Amazon estimates September 17 |
| IEIK, advertised 12 V / 60 W / 116 psi / 5 L/min | [B07YXTHNRQ](https://www.amazon.com/dp/B07YXTHNRQ) | On order; Amazon estimates September 18 |

Both belong to Amazon order 112-0884852-3444230. Paid amounts and shipment
records live in [purchases.md](/hardware/ledger/purchases.md), with diagnostic
allocation in [inventory.md](/hardware/ledger/inventory.md#diagnostic).
The advertised pressure and free-flow figures are separate endpoints, not a
measured operating point.

## Received-part record

Use the mounting-foot underside as Z = 0, the motor axis as X (positive toward
the pump head), the motor-to-head mating plane as X = 0, and the shaft's
centreline as Y = 0. Record the label, each measured feature and a photograph
with its datum visible. Dimensions include fittings, switch housing and feet;
packaging dimensions do not enter this table.

| Measurement | G Ganen | IEIK |
|---|---|---|
| Received date, model/label and sample identifier | Unmeasured | Unmeasured |
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

The [conditional Plan B](/future/carbonation-plan-b.md) defines which measured
Plan A shortfall would make those further tests useful. No replacement pump is
selected by this sheet.
