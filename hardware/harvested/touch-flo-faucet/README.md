# Touch-Flo Faucet Teardown + Fabrication Plan

The dispense point of this appliance is a custom three-tube spout (1× carbonated water + 2× flavor) with a factory-grade self-closing spring-piston lever valve harvested from a Touch-Flo–class cold water dispenser faucet. Mixing occurs in the user's glass, not before — see `hardware/requirements.md`. This directory captures the harvest donor, the class of mechanism being harvested, and the fabrication plan for the spout.

## Why harvest

The self-closing spring-return poppet valve on a Touch-Flo faucet is the only off-the-shelf subassembly found that gives consumer-appliance-grade lever action with a clean return-to-closed, in a form factor that mounts through a deck. It is a spring-piston poppet against a silicone seat — not a ceramic disc cartridge. Target patent class: Crystal Mountain US8857669B2.

Building this mechanism from scratch is possible but displaces attention from the rest of the machine. Modifying a three-way faucet (removing the two unwanted knobs) leaves visible plugged bosses. Harvesting the Touch-Flo lever assembly and re-clothing it with our own three-tube spout avoids both problems.

## Harvest donor (primary)

**Westbrass R2031-NL-12 Touch-Flo cold water dispenser faucet** — ASIN `B01N5LVNQA`, ~$19.53, Prime Two-Day.

- Picked as the cheapest Prime-available Touch-Flo for the prototype round — we want a repeatable pattern, not a specific brand. Any Touch-Flo–class faucet with a spring-piston poppet cartridge and a 1/4" compression inlet is substitutable.
- Deck-mount, single-lever, self-closing.
- Inlet: 1/4" compression — matches the project's existing 1/4" compression plumbing; no adapter needed.
- Internal: spring-return poppet against silicone seat (not a ceramic disc cartridge).

The already-owned Westbrass A2031-NL-62 ($32.18) and D203-NL-62 ($52.99) in `hardware/purchases.md` are not the harvest donors — the R2031-NL-12 pattern was chosen after they were purchased, specifically to avoid brand lock-in.

## What gets kept, what gets discarded

**Kept (harvested):**
- Lever assembly (handle + pivot + actuator rod)
- Spring
- Poppet with silicone seat
- Deck-mount escutcheon / shank (the part that passes through the countertop)
- Inlet fitting (1/4" compression body)

**Discarded:**
- Factory spout tube — replaced by our fabricated three-tube spout assembly
- Factory spout tip / nose cap — replaced by matching decorative collars on all three tubes
- Any filter cartridge or aerator (if present on this SKU — these are not on the R2031 base model)

## Three-tube spout — fabrication plan

Target end-state: three visible stainless tubes emerging from the faucet body, gently swept forward to dispense over a glass at the sink. Center tube carries carbonated water from the harvested valve. Flanking tubes carry flavor from the peristaltic pumps.

- **Center tube:** 1/4" OD 304 SS, brazed or compression-joined to the harvested Touch-Flo outlet.
- **Flanking tubes:** 1/8" OD 304 SS, routed parallel to the center tube. These carry flavor from the Kamoer KPHM400 pumps. The project's line-run medium is 1/4" LLDPE hard tubing everywhere (see `docs/plumbing.md`), so each flavor line needs a **1/4" LLDPE → 1/8" SS reducer** inside the shroud to transition from the LLDPE supply to the smaller visible SS tube at the spout. Specific fittings TBD pending the Prime-availability survey.
- **Bends:** each tube takes a small number (2–3) of gentle sweeps to produce the forward angle. Rigid SS in 12" segments is easy to bend by hand around a form with a simple tube bender; intermediate unions are avoided.
- **Decorative tip collars:** short 304 SS compression ferrules slipped over each tube at the dispense end, mimicking the "thickening" / nose cap seen on the Westbrass 8" factory spout. Stainless (not brass) was chosen deliberately so the collar matches the SS tube — the whole spout reads as one material. Ferrule acts as decoration only (not a sealed joint); retention method to be decided during prototyping (press fit, light adhesive, or swage).

The asymmetric diameter (1/4" center + 2× 1/8" flanks) is the intentional design language — carbonated water is the main event, flavor is the accent.

## Prototype round materials

Acquired Apr 23, 2026 — see `hardware/purchases.md` §7 for canonical prices and ASINs. Summary:

- Westbrass R2031-NL-12 Touch-Flo donor (harvest target)
- 1/4" OD × 12" 304 SS tube, 4-pack — center carbonated-water tube stock
- 1/8" OD × 12" 304 SS tube, 4-pack — flanking flavor-tube stock
- 1/4" 304 SS compression ferrules — decorative tip collars for the center tube
- 1/8" 304 SS compression ferrules — decorative tip collars for the flavor tubes

**Deliberately not purchased for v1:**
- 1/8" compression union — gentle bends in 12" rigid tubes don't need mid-run joints. Add only if a bend fails.

**Pending purchase (under research):**
- 1/4" LLDPE → 1/8" SS reducer, Prime-available, ×2 per unit. Either a direct reducing union or a two-piece NPT-middle stack (1/4" LLDPE comp × 1/4" NPT male → 1/4" NPT female × 1/8" OD SS comp). Path decision waiting on the Prime-availability survey.

## Open items

- Physical teardown of the R2031-NL-12 once it arrives — confirm the poppet cartridge is actually removable as a subassembly, not swaged into the body.
- Decide how the three tubes mount together: a printed shroud behind the visible spout section, a brazed bundle, or a machined manifold block.
- Decide how the decorative tip ferrules are retained permanently and cleanly — light crush is the obvious path but may not survive handling; press fit + adhesive is the backup.
- Photograph the factory Westbrass nose cap at close range to measure the "thickening" silhouette we are replicating.
