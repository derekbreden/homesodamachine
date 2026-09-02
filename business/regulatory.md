# Regulatory Posture

Consolidates the regulatory conclusions already reached across prior conversations so they do not need to be re-derived. Primary path is direct-to-consumer sale via homesodamachine.com. Secondary path is big-box retail (Amazon, Walmart, etc.) via the RIGID DV1910E listed-module fallback.

## Sales channels

| Channel | UL / ETL listing | Notes |
|---|---|---|
| Direct-to-consumer (homesodamachine.com) | Not required | Listing is a retailer/insurer requirement, not federal law. |
| Big-box retail (Amazon, Walmart, Home Depot, etc.) | Required | Use RIGID DV1910E listed-module fallback. |

## EPA Section 608 — refrigerant handling

R-600a (isobutane) is carved out of the Section 608 venting prohibition as a natural refrigerant. No technician certification is legally required to vent, cut, braze, evacuate, or recharge the harvested refrigerant loop on this project.

Primary citation: `hardware/reference/ice-maker/README.md` (the line stating the 608 exemption).

Does not apply to: a pivot to an R-134a or other HFC donor. In that case 608 Type I certification applies (open-book online, ~$25, 84% pass).

## EPA SNAP — refrigerant end-use approval

SNAP (Significant New Alternatives Policy, Clean Air Act §612) approves refrigerants for specific product categories. Natural refrigerants are not blanket-exempt from SNAP — approval is granted per end-use.

R-600a is SNAP-approved for this project's end-use category (self-contained commercial refrigeration, which covers countertop refrigerated beverage dispensers). This project's charge (30–50 g) is well under applicable SNAP charge limits.

Approval conditions this project must satisfy at the product level (no third-party listing needed):

- Design per UL 60335-2-89 (hydrocarbon charge handling, enclosure) — compliance, not listing
- Flame symbol (ISO 7010 W021) marking on the unit
- "Flammable refrigerant" text marking on the unit
- Installation / service instructions note the refrigerant and charge mass

## UL 60335-2-89 — hydrocarbon appliance safety

Charge cap for this equipment class is 150 g. Factory donor charge is 30–50 g per unit — well below the limit.

Primary citation: `hardware/reference/ice-maker/README.md` (the line stating charge is "well under the 150 g UL 60335-2-89 limit").

D2C sale does not require this listing. The design follows the standard anyway because the standard codifies what safe handling of hydrocarbon refrigerant in a household appliance actually requires — charge limits, ignition-source containment, marking, service notes. The motivation is not regulatory posture: the appliance is going into kitchens used by friends, family, and customers the founder knows by name (per `marketing/target-market.md` "rings of trust"). Safety is the substance; listing is a credentialing path that's not being pursued separately.

The compressor's terminal block and clip-on PTC start relay/overload module remain under the R-600a donor's own moulded power-box cover. That cover is part of the harvested compressor assembly: it stays intact and securely retained, and the appliance connects only at the donor assembly's factory-external electrical interface without opening or modifying the cover. The current build adds no second sheet-metal shroud. The SEFUSE thermal fuse lies against the outside flank of the donor cover, the MQ-6 sensor sits low in the cabinet and gates the compressor relay, and the Teyleten relay that switches the compressor's AC lives remotely on the +X wall of back-top.

What remains open for an applicable 60335 fire-enclosure claim is **qualification of the retained donor cover**, not implementation of a cover. Before making that claim, record the cover's material markings, condition, retention method, and lead-opening geometry, and review them against the applicable enclosure provisions. A missing, cracked, modified, loose, or incorrectly retained donor cover is a build failure.

## UL 943 — ground-fault protection

Class A GFCI, 6 mA trip threshold, 120 V personnel protection. The 2015 revision of the standard mandates automatic self-test (periodic internal verification with lockout on test failure) for all manufacture from that point forward.

D2C sale does not require this listing. A Class I plumbed appliance — three bonded chassis surfaces (carbonator, compressor body, under-counter plate) returning fault current through the C14 cord per `hardware/wiring/ac-wiring-schedule.md` — carries the shock-protection obligation regardless of certification path. The standard codifies what ground-fault protection in a household appliance actually requires.

An integrated in-appliance GFCI on the AC side is deferred from the current build and held in [`/future/pie-in-the-sky/gfci.md`](/future/pie-in-the-sky/gfci.md), which carries the scoped device, the inline-on-the-AC-side wiring, and the swappable-cord rationale. The current build lands the C14 inlet onto the three mains splices in the +X wall's own Wago wells with no device in series (`enclosure._side_wells`).

## CPSC general safety duty

Federal Consumer Product Safety Commission applies to any consumer product sold in the US. Product must not be unreasonably dangerous. No listing or certification required — this is a general duty of care, independently honored by the project's design practice.

## AIM Act — not applicable

The American Innovation and Manufacturing Act regulates HFCs. R-600a is a hydrocarbon, not an HFC, and is outside the scope of AIM Act phase-down rules, leak-management thresholds (15 lb rule, Jan 2026), and refillable-cylinder requirements.

Applies only if the project pivots to an HFC refrigerant.

## Assembly-time safety — argon purge during brazing

Not a regulation, but load-bearing for the build path described in `hardware/reference/ice-maker/README.md` "Cold core architecture" — wherever the refrigerant loop is opened and brazed.

After the factory R-600a charge is vented, residual hydrocarbon remains dissolved in the compressor oil and pooled in low points of the tubing. When a torch is applied to copper near an oil-soaked compressor pocket, the flame front pulls residual hydrocarbon into itself. Mitigation is to flow low-pressure argon (a few psi, flowing — not static) through the opened loop during and through the braze, sweeping residual fuel out ahead of the heat.

The documented build path reuses the argon cylinder already present for laser welding, with the appropriate purge-side regulator / tubing setup for refrigeration brazing.
