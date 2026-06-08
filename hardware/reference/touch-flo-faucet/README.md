# Touch-Flo Faucet Teardown + Fabrication Plan

The dispense point of this appliance is a custom three-tube spout (1× carbonated water + 2× flavor) with a factory-grade self-closing spring-piston lever valve harvested from a Touch-Flo–class cold water dispenser faucet. Mixing occurs in the user's glass, not before — see [`/hardware/future.md`](/hardware/future.md). This directory captures the harvest donor, the class of mechanism being harvested, and the fabrication plan for the spout.

## Mechanism

The Touch-Flo faucet's self-closing spring-return poppet valve gives consumer-appliance-grade lever action with a clean return-to-closed in a deck-mount form factor. Spring-piston poppet against a silicone seat. Target patent class: Crystal Mountain US8857669B2.

## Harvest donor (primary)

**Westbrass R2031-NL Touch-Flo cold water dispenser faucet** — either R2031-NL-62 (matte black, ASIN `B07KH285GJ`, ~$31.28) or R2031-NL-12 (oil-rubbed bronze, ASIN `B01N5LVNQA`, ~$19.53). Same R2031-NL family with identical mechanism and the same black plastic handle; the finish is covered by the touch-flo-shell. Any Touch-Flo–class faucet with a spring-piston poppet cartridge and a 1/4" compression inlet is substitutable.

- Deck-mount, single-lever, self-closing.
- Inlet: 1/4" compression — matches the project's existing 1/4" compression plumbing.
- Internal: spring-return poppet against silicone seat.

## What gets kept, what gets discarded

**Kept (harvested):**
- Lever
- Entire Touch-Flo body (see valve-body-reference folder)

**Discarded:**
- Mounting plate

## Three-tube dispense head

The dispense head is the printed PET-CF gooseneck of the touch-flo-shell, carrying three LLDPE tubes (1× carbonated water + 2× flavor) routed through its internal dispense channel and exiting at the printed tip. The wet path is LLDPE end to end; no metal tubing is involved in the dispense head, and the dispensed liquid never touches shell material — see [`/hardware/printed-parts/faucet/touch-flo-shell/`](/hardware/printed-parts/faucet/touch-flo-shell/) for the part and [`/hardware/printed-parts/faucet/touch-flo-shell/MATERIAL.md`](/hardware/printed-parts/faucet/touch-flo-shell/MATERIAL.md) for the no-food-contact boundary. Tube routing and the single Siptenk stiffener at the Westbrass upstream port are in [`/hardware/assembly/faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md) step 2.

