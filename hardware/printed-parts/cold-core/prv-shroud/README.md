# PRV shroud

3D-printed PETG cup that surrounds the Control Devices SV-125
pressure-relief valve on Port 4 of the carbonator pressure vessel
during the cold-core body foam pour. The shroud preserves the air
cavity the open-port pop-off PRV needs to function — without it,
cured polyurethane foam fills the spring chamber and blocks both the
discharge side port and the bonnet windows, and the valve can't
relieve.

## Why this part exists

The SV-125 (per [`assembly/pressure-vessel.md`](../../../assembly/pressure-vessel.md)
step 8) is installed via a TAISHER 316L 90° street elbow on Port 4
with the valve body extending laterally — fitting the PRV inside
the ~30 mm above-tank elbow envelope rather than protruding
vertically. The body foam pour ([`../foam-shell/`](../foam-shell/))
fills the surrounding foam zone with closed-cell polyurethane,
which would otherwise encase the PRV.

The SV-125 is an open-port pop-off design: the discharge gas exits
**radially through a single side port** in the smooth body cylinder
between the NPT threads and the hex, and the spring chamber above
the hex is open to atmosphere through **two large bonnet windows**.
Both features require ambient-pressure air around them — foam
encasement defeats both, and the valve becomes a non-functioning
plug rather than a safety device.

This shroud is the minimum-mass air pocket that keeps those
features in air. It is **not** a pressure-rated part — the line
downstream of the PRV seat is unpressurized in normal operation,
only briefly elevated during a relief event.

## Geometry

19 mm ID × 23 mm OD × 46 mm overall length, 2 mm wall and 2 mm cap,
single ⌀6.35 mm centered vent hole in the cap.

Reference dimensions measured at the install (SV-125 hand-tight in
the TAISHER M×F 90° elbow, no PTFE torque applied):

| Surface | Diameter |
|---|---|
| TAISHER elbow smooth cylinder OD (the seat surface) | 18.8 mm |
| SV-125 hex outer corners (across points) | 16.0 mm |
| Shroud ID | 19.0 mm |

ID is sized for a 0.1 mm radial slip-fit over the elbow's
controlled-OD smooth cylinder at the seat end (the only good
sealing surface in the stack). Above that, the shroud floats around
the valve body with ~1.5 mm radial gap at the hex and larger gaps
above.

The 44 mm cavity length matches the measured stack from the bottom
of the elbow's smooth cylinder to the very tip of the SV-125
pull-ring with the valve hand-tight in the elbow. After full PTFE
torque the stack shortens by a turn or two; the 2 mm cap thickness
gives a few mm of clearance above the pull-ring at full torque.

## Install procedure

Performed during cold-core assembly, before the body foam pour.
Documented in [`../foam-shell/README.md`](../foam-shell/README.md)
"Body pour" and [`../../../assembly/pressure-vessel.md`](../../../assembly/pressure-vessel.md)
step 8.

1. Install the TAISHER M×F 90° street elbow on Port 4 + the SV-125
   on the elbow's lateral F outlet (pressure-vessel.md step 8).
2. Slip the shroud over the SV-125 from the pull-ring end, sliding
   it down past the cap-side opening, past the hex, past the
   discharge side port, until the open end of the shroud seats on
   the smooth ⌀18.8 mm cylindrical section of the elbow.
3. Run a bead of sealant (see Open items below) around the joint
   between the shroud's open end and the elbow's smooth cylinder.
   The seal needs to be **foam-tight, not airtight or pressure-
   tight** — only enough to keep the rising body foam from
   intruding through the joint. Cured foam takes over as the
   structural seal once it sets. The shroud-on assembly step and
   the foam pour can be days apart; the sealant does not have to
   be fast-cure.
4. Press-fit a length of 1/4" OD LLDPE tubing into the shroud's
   ⌀6.35 vent hole. Route the LLDPE out through the +Z shared slot
   in the outer shell (PRV vent pass-through, see foam-shell
   [Penetrations](../foam-shell/README.md#penetrations)), and leave
   the LLDPE's far end open inside the appliance interior.
5. Proceed with the body foam pour. Foam fills the surrounding zone
   but cannot enter the shroud cavity — the seat at the elbow holds.

## What this part is not

- **Not a pressure boundary.** The shroud is downstream of the PRV
  seat. In normal operation it sees atmospheric pressure. During a
  relief event it sees the brief discharge pressure peak (a few PSI
  at most through the 1/4" LLDPE flow restriction), not vessel
  pressure.
- **Not a sealed cavity.** The shroud + LLDPE keep the **spring
  chamber bonnet windows** in air, so the SV-125's setpoint
  accuracy is preserved — the spring sees ~atmospheric reference
  via the LLDPE-to-appliance-interior path, which is gas-exchanged
  with the cabinet via the condenser-fan path.
- **Not a permanent service interface.** Once foam is poured around
  the shroud, the SV-125 cannot be unscrewed without destroying the
  foam shell. The PRV is a once-installed component in this design;
  if it ever needs replacement, the cold-core foam pour is the
  serviceable boundary.

## Open items

1. **Sealant choice at the shroud-to-elbow joint.** The bead's only
   job is to keep rising body foam out of the cavity for the ~5
   minutes it takes the foam to skin over. Once the foam is set, it
   takes over as the structural seal. The bead can cure as slowly
   as it wants — the shroud-on assembly step and the foam pour can
   be days apart. Candidate sealants under consideration: 100% RTV
   silicone caulk (skins in 20–30 min, fully cures overnight, bonds
   well to both PETG and brass), 5-minute two-part epoxy (rigid, very
   reliable bond, slightly fiddlier), or hot-melt EVA (fastest but
   weakest bond to brass and softens slightly under foam exotherm).
   A small-scale dry run — pour a few mL of mixed foam into a clear
   container with a shroud-on-elbow stub inside, watch for joint
   intrusion through the cure — is the right way to pick before
   committing to unit 001.

## Regression baseline

Geometry is parametric on five scalars (inner_diameter,
wall_thickness, cap_thickness, cavity_length, vent_hole_diameter)
in `generate_step_cadquery.py`. Any change to those is a deliberate
geometry shift and should land with a measured rationale.

| metric | value |
|---|---|
| bbox X | [−11.50, +11.50] mm |
| bbox Y | [−46.00, 0.00] mm |
| bbox Z | [−11.50, +11.50] mm |
| volume | 6548.090 mm³ |
