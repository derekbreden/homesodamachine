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
- Lever
- Entire Touch-Flo body (see valve-body-reference folder)

**Discarded:**
- Mounting plate

## Three-tube spout — fabrication plan

Target end-state: three visible powder coated stainless tubes emerging from the faucet body, bent to dispense over a glass at the sink. Center tube carries carbonated water from the harvested valve. Smaller 1/8 tubes carry flavor from the peristaltic pumps.

- **Center tube:** 3/8" OD 316 SS
- **Rear tubes:** 1/8" OD 316 SS

The asymmetric diameter (3/8" center + 2× 1/8") is the intentional design language — carbonated water is the main event, flavor is the accent.