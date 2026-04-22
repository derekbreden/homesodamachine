# Regulatory Posture

Consolidates the regulatory conclusions already reached across prior conversations so they do not need to be re-derived. Primary path is direct-to-consumer sale via homesodamachine.com. Secondary path is big-box retail (Amazon, Walmart, etc.) via the RIGID DV1910E listed-module fallback.

## Sales channels

| Channel | UL / ETL listing | Notes |
|---|---|---|
| Direct-to-consumer (homesodamachine.com) | Not required | Listing is a retailer/insurer requirement, not federal law. |
| Big-box retail (Amazon, Walmart, Home Depot, etc.) | Required | Use RIGID DV1910E listed-module fallback. See `hardware/future.md`. |

## EPA Section 608 — refrigerant handling

R-600a (isobutane) is carved out of the Section 608 venting prohibition as a natural refrigerant. No technician certification is legally required to vent, cut, braze, evacuate, or recharge the harvested refrigerant loop on this project.

Primary citation: `hardware/ice-maker-teardown.md` (the line stating the 608 exemption).

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

Primary citation: `hardware/ice-maker-teardown.md` (the line stating charge is "well under the 150 g UL 60335-2-89 limit").

This standard governs design compliance regardless of whether a UL listing is pursued. D2C sale does not require the listing but the design should still conform.

## CPSC general safety duty

Federal Consumer Product Safety Commission applies to any consumer product sold in the US. Product must not be unreasonably dangerous. No listing or certification required — this is a general duty of care, independently honored by the project's design practice.

## AIM Act — not applicable

The American Innovation and Manufacturing Act regulates HFCs. R-600a is a hydrocarbon, not an HFC, and is outside the scope of AIM Act phase-down rules, leak-management thresholds (15 lb rule, Jan 2026), and refillable-cylinder requirements.

Applies only if the project pivots to an HFC refrigerant.

## Assembly-time safety — nitrogen purge during brazing

Not a regulation, but load-bearing for Path A execution.

After the factory R-600a charge is vented, residual hydrocarbon remains dissolved in the compressor oil and pooled in low points of the tubing. When a torch is applied to copper near an oil-soaked compressor pocket, the flame front pulls residual hydrocarbon into itself. Mitigation is to flow low-pressure nitrogen (a few psi, flowing — not static) through the opened loop during and through the braze, sweeping residual fuel out ahead of the heat.

A disposable nitrogen cylinder + regulator from a welding supplier is sufficient for a one-off build. This tooling is not in `hardware/bom.md` or `hardware/parts-list.md` yet.
