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

## Subassembly procedure

This is a **self-contained subassembly** with no prerequisites
beyond the three parts (TAISHER elbow + SV-125 + printed shroud)
and a tube of 100% RTV silicone caulk. It is built **independently
of the vessel and of any other assembly step**, on the bench, and
can sit ready to use indefinitely after the caulk cures. There is
no urgency to its construction relative to vessel fabrication or
cold-core assembly — the subassembly can be built ahead of time and
shelved.

The LLDPE vent tube and the foam-shell pass-through are **not** part
of this subassembly — the LLDPE is press-fit into the shroud's cap
hole during cold-core build, after the subassembly is threaded into
Port 4 and the vessel is lowered into the foam shell.

1. Thread the SV-125 into the TAISHER M×F 90° street elbow's
   lateral F outlet with Millrose PTFE tape on the threads. Snug
   hand-tight + a turn or two with a wrench on the SV-125's hex.
2. **Pull-test the SV-125.** With the elbow held in the bench vise
   on its M-end shank (no pressure source), pull the SV-125's
   stainless-steel pull-ring straight up against the spring with
   light force. The disc should lift cleanly off the seat and snap
   back when released. A free, snappy pull-ring confirms the disc
   and spring move without binding. This is the **last opportunity
   for manual access to the pull-ring** — the shroud in step 3
   encloses it permanently. If the pull-ring binds or doesn't
   return cleanly, replace the SV-125 before proceeding.
3. Slip the shroud over the SV-125 from the pull-ring end, sliding
   it down past the cap-side opening, past the hex, past the
   discharge side port, until the open end of the shroud seats on
   the smooth ⌀18.8 mm cylindrical section of the elbow.
4. Run a bead of **100% RTV silicone caulk** (e.g., GE Silicone II)
   around the joint between the shroud's open end and the elbow's
   smooth cylinder. Smooth the bead with a wet fingertip to form a
   small fillet. The seal needs to be **foam-tight, not airtight or
   pressure-tight** — only enough to keep the rising body foam from
   intruding through the joint during the ~5 min foam rise. Cured
   foam takes over as the structural seal once it sets.
5. Let the caulk cure at least 20–30 min for skin-over before
   handling, ≥24 h for full cure before the subassembly is
   installed on a vessel.

After cure, the subassembly is ready. It threads into Port 4 of a
finished vessel at [`../../../assembly/pressure-vessel.md`](../../../assembly/pressure-vessel.md)
step 8, replacing the elbow + PRV install on that port.

The LLDPE press-fit and routing through the foam-shell slot happen
later, at [`../../../assembly/cold-core.md`](../../../assembly/cold-core.md)
step 4.

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

1. **Dry-run verification of the silicone caulk seal at the shroud-
   to-elbow joint before unit 001.** Build one subassembly per the
   procedure above, drop it into a clear plastic cup, pour a small
   batch of 2-lb PU foam around it, and slice the cup open after
   cure to confirm no foam intrusion into the cavity. Half an hour
   of bench work; definitive answer. The sealant choice (100% RTV
   silicone) is settled — this dry run validates the bead
   application technique, not the sealant material.

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
