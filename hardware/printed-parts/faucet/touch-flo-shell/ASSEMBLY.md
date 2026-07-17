# Touch-Flo shell + mounting plate sub-assembly

Bench procedure for joining the printed `touch-flo-shell` to the printed
`touch-flo-mounting-plate` with the harvested Touch-Flo valve body
sandwiched between them — three M3×12 screws driven up through the
plate's bosses into heat-set inserts in the shell's base pods. This is
the sub-assembly that gets handed off to the countertop install step
(gasket + under-counter nut against the deck) — it does not include the
gasket or the deck nut.

## Where this fits in the build

Upstream:

1. Print `touch-flo-shell` (PET-CF, 0.6 mm DUROZZLE TC nozzle, settings in
   [`print-log.md`](/hardware/printed-parts/faucet/touch-flo-shell/print-log.md)).
2. Print `touch-flo-mounting-plate` (PET-CF, same H2C).
3. Harvest the Touch-Flo valve body from the donor faucet per
   [`/hardware/reference/touch-flo-faucet/README.md`](/hardware/reference/touch-flo-faucet/README.md).
   Keep the lever, the body, and the factory shank nut. Discard the
   factory mounting plate.

Downstream (at the faucet-and-umbilical bench, see [`/hardware/assembly/faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md)):

4. Slide the TPU `touch-flo-mounting-gasket` up the shank from below
   the printed mounting plate, snug against the plate's bottom face.
   The gasket sits permanently between the plate's underside and where
   the countertop top surface will be at the customer's install. The
   customer never touches the gasket.
5. Route the three LLDPE umbilical tubes up through the pill slot
   (passing through both the printed mounting plate and the TPU
   gasket) and clamp them to the Westbrass body's compression ports.
   Tubes are permanently attached at this step — never separated
   again. The sub-assembly + umbilical leaves the bench as one unit.

Downstream (at the customer's countertop install, illustrated on the
printed quick-start sheet in the appliance carton —
[`/marketing/unboxing-and-quickstart.md`](/marketing/unboxing-and-quickstart.md)):

6. Drop the faucet+umbilical assembly into the 1-3/8" countertop hole
   from above. The TPU gasket (already on the shank, between the
   mounting plate and the countertop) compresses against the countertop
   top surface as the assembly seats. The three tubes + signal cable hang down
   through the hole.
7. From below: orient the keyhole under-counter plate so its open-edge
   channels face the dangling umbilical, then slide the plate
   laterally past the cylinders. The shank and the tube bundle enter
   through their respective channel mouths at the rim and seat in
   their terminal pockets; the cylinders in the channels keep the
   plate from drifting back out of alignment.
8. From below: slip the washer onto the shank, then thread and tighten
   the factory shank nut. The nut + washer clamp the keyhole plate up
   against the countertop; the entire stack compresses along the
   shank from the body above to the nut below.

This document covers step 3a — joining the printed parts to the body
into a single rigid sub-assembly.

## Materials

| Qty | Item                                                 | Reference                                                                          |
| --- | ---------------------------------------------------- | ---------------------------------------------------------------------------------- |
|  1  | `touch-flo-shell` (printed, PET-CF) — three base-pod boss holes + insert pockets opening into the foot bottom | `touch_flo_shell.py` in this directory (BASE PODS section)        |
|  1  | `touch-flo-mounting-plate` (printed, PET-CF) — three chamfer-tipped screw bosses on the top face, counterbored from below | [`/hardware/printed-parts/faucet/touch-flo-mounting-plate/`](/hardware/printed-parts/faucet/touch-flo-mounting-plate/) |
|  1  | Touch-Flo valve body + factory shank nut (harvested) | [`/hardware/reference/touch-flo-faucet/`](/hardware/reference/touch-flo-faucet/)            |
|  3  | ruthex M3 short heat-set insert (RX-M3Sx4.0, Ø4.2 knurled brass) | [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §13                |
|  3  | BNUOK M3 × 12 mm SHCS, black oxide                   | [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §13                            |

The three pod screws are the entire shell retention: each M3×12 drives
up from under the plate, through the counterbore and the boss, into a
ruthex insert heat-set in the shell. The factory shank nut clamps the
metal body to the plate only — not the shell. Once installed in the
countertop, the under-counter nut compresses the stack (body → plate →
TPU gasket → countertop) and carries the installed loads.

The two flavor tubes that pass through the pill slot are NOT installed
at this step — they're routed in the downstream "tube routing" step,
which is easier with the shell + plate already joined and the body
clamped.

## Adjacent parts

Two parts in the touch-flo stack aren't joined by this sub-assembly but
sit immediately adjacent to it, so their spec lives here for one-stop
reference:

**Donor faucet body — Westbrass 8" touch-flo family (A2031-NL / R2031-NL,
interchangeable).** The BOM SKU is A2031-NL-62 (matte black, B0BXFW1J38).
Any finish variant in the A2031-NL / R2031-NL series is interchangeable
for this build because the finish is fully hidden by the printed
touch-flo-shell — only the mechanism + shank are exposed. Pick whichever
is cheaper / Prime-available at order time.

**Under-counter plate — SendCutSend 0.060" 316 SS, keyhole design
(order qty 1).** File `touch_flo_under_counter_plate.dxf` (generated
by ``endcap_circular_dxf.py` (different part)` in the same directory) is a single-piece
Ø 54.35 mm disc with hole positions that match the TPU mounting
gasket exactly — Ø 12.6 mm shank pocket at the gasket's shank center
and a [13.4 mm](PILL_L) × [7.05 mm](PILL_W) pill pocket (long axis along X) at the gasket's
pill center, [18.93 mm](FLAVOR_TUBE_Y) away along +Y. Each pocket has its own
open-edge channel extending from the pocket to the disc rim in the
−Y direction (channel widths: 12.6 mm for the shank, [7.05 mm](PILL_W) for the
pill). The two channels exit the rim at different X positions and
do not merge. The four corners where the channel walls meet the
rim are rounded with R 1.5 mm fillets — these would otherwise be
sharp acute tips (handling hazard, laser-dross-prone, no help with
alignment); the fillets dull them and give the cylinders a small
lead-in funnel at each channel mouth.

The faucet + umbilical leaves the faucet-and-umbilical build chain
as one permanently-attached sub-assembly — the LLDPE tubes are
clamped to the Westbrass body. At install, the keyhole's open-edge
channels let the installer slide the plate laterally past the
dangling cylinders; both the shank and the tube bundle enter through
their channel mouths at the rim and seat in their terminal pockets.
Once seated, the cylinders in the narrow channels keep the plate in
alignment under gravity while the installer threads the shank nut
one-handed.

Anti-rotation during nut tightening is provided by the cylinders
themselves: any rotational drift of the plate presses the shank and
tube bundle against the channel walls.

Stack-up: between the countertop underside and the under-counter
shank nut. Distributes the nut's clamping force over a wide area so
the nut doesn't dish or crush the countertop bottom — the printed
mounting plate above the counter is too soft / too small for that
clamping load. Installed during countertop install, not during the
shell + plate + body sub-assembly procedure below.

## Tools

| Item                                          | Reference                                                                  |
| --------------------------------------------- | -------------------------------------------------------------------------- |
| Soldering iron + M3 heat-set tip              | Seats the three ruthex inserts (T18 tip kit + FX-888D — the §13 tooling note in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md)) |
| 2.5 mm hex key                                | Drives the M3×12 SHCS                                                      |
| Flat work surface + clean rag                 | Insert setting and final seating                                           |

## Geometry summary

**The joint.** The shell's foot carries three base pods — two lateral
(±X) and one front (−Y) — each with a blind boss hole opening into the
foot bottom and a ruthex M3 insert pocket stacked above it, the insert
opening facing down onto the hole. The plate carries three matching
bosses rising from its top face, each tipped with a lead-in chamfer
and bored through: a counterbore from the plate bottom (screw-head
recess) and an M3 shank bore up through the boss to the insert. The
bosses register the plate; the screws clamp it. Dimensions live in
`touch_flo_shell.py` (BASE PODS section) and the
[plate README](/hardware/printed-parts/faucet/touch-flo-mounting-plate/README.md).

What holds the parts together:

- From this bench onward: the three **pod screws** clamp the plate up
  against the shell foot — the sub-assembly is rigid and handles in
  any orientation. The body, clamped to the plate by the **shank nut**
  from Step 2, sits in the shell's bore with a [0.25 mm](BORE_CLEAR)/side
  slip-fit.
- Once installed in the countertop: the under-counter nut compresses
  body → plate → TPU gasket → countertop, and that compression carries
  the installed loads; the pod screws keep carrying the shell.

Stack-up at the plate-to-shell interface (rear shoulder region):

```
      shell wall (PET-CF) — solid material, no pockets
      └── shell bottom face (smooth)
           └── plate top face (smooth, clamped to the shell bottom by the pod screws)
                └── 4 mm plate (solid material, no holes here)
                     └── plate bottom face (smooth, against TPU gasket)
```

**Plate bottom face must stay flat for the TPU gasket.** The
mounting plate sits *above* the countertop — its top face mates with
the shell bottom (this doc's joint), its bottom face mates with the
TPU `touch-flo-mounting-gasket` that then seals against the
countertop's top surface. The three screw heads recess fully into
the counterbores, above the bottom plane, so the plate presents an
uninterrupted flat face to the gasket — the counterbore rims are the
only openings.

The factory shank nut clamps the body's [31.5 mm](BODY_OD) OD bottom
face onto the plate's top face through the plate's Ø 12.6 shank hole.
The shell sits over the body+plate stack, screwed to the plate through
the pods; the body inside the shell's bore adds lateral and rotational
constraint (rectangular zone-2 cross-section + lever orientation).

## Pre-flight check

1. **Support material removal.** Confirm the shell's body bore and the
   three boss holes + insert pockets in its foot, and the plate's
   shank hole, pill slot, and counterbores, are all clear of supports
   and stringing.
2. **Body fit.** Dry-fit the harvested body into the shell's bore
   from the bottom (shell oriented bottom-up). The body should
   slide all the way to the bore cove (Z = [19.25 mm](BORE_COVE_Z) in part
   coordinates) without binding. The lever swings in the shell's
   -Y clearance ramp; verify the lever clears at the resting
   position.
3. **Boss fit.** Dry-fit the plate (no body) onto the shell foot:
   all three bosses enter their holes and the plate seats flat
   against the foot under light hand pressure.

## Step 1 — Heat-set inserts into the shell

1. Set the shell foot-up on the work surface.
2. Carry each ruthex insert up through its boss hole on the iron's M3
   tip, opening down, into the Ø 4 pocket above the hole ceiling.
   Press until the insert mouth sits flush with the ceiling — the
   pocket runs deeper than the insert's 4 mm length, leaving relief
   above it.
3. Let each pod cool before moving the shell.

## Step 2 — Body into mounting plate

1. Slot the Touch-Flo body's Ø 11 mm threaded shank up through the
   plate's Ø 12.6 shank hole. The body's [31.5 mm](BODY_OD) OD landing face
   bottoms out on the plate's top face; the shank protrudes ~46 mm
   below the plate's bottom face.
2. Thread the factory shank nut onto the protruding shank from below,
   running it up by hand until it just contacts the plate's bottom
   face.
3. Tighten the nut snug with hand pressure plus a quarter turn with
   pliers (or the factory wrench if it's still around). This is the
   body-to-plate clamp; the gasket and under-counter nut at the deck
   install step take over the long-term clamping load.
4. Confirm the body is rotationally locked — the rectangular zone-2
   profile ([31.5 mm](BODY_RECT_LONG) × [17 mm](BODY_RECT_SHORT)) above [13 mm](BODY_CYL_TOP_Z) cannot rotate inside the
   shell's bore that's about to come down on it. The body's
   rotational orientation is set by which way the lever points;
   orient the lever toward -Y (the lever-clearance ramp side of the
   shell).

## Step 3 — Shell over body

1. Hold the plate + body sub-assembly with the body pointing up. Drop
   the shell down over the body so the body enters the shell's bore
   from the bottom. The shell's -Y lever clearance ramp must align
   with the lever (which you already pointed toward -Y in Step 2).
2. Push the shell down until the three bosses enter their pod holes —
   the chamfered tips funnel them in — and the foot seats flat
   against the plate's top face. The pod pattern matches in exactly
   one orientation: rotated 180°, the front boss lands on solid foot
   and the outlines mismatch.
3. Verify the shell's pill slot aligns with the plate's pill slot
   (both at world (0, +[18.93 mm](FLAVOR_TUBE_Y)), X-oriented). They should overlay
   exactly.

## Step 4 — Screws

1. From below, drop an M3×12 SHCS into each counterbore and thread it
   into its insert with the 2.5 mm hex key.
2. Snug all three in alternation — hand-snug plus a quarter turn, no
   more. The threads live in the brass inserts, the clamped material
   is plastic.
3. Confirm each head sits fully recessed in its counterbore, above
   the plate's bottom face.

The sub-assembly is now rigid — shell, plate, and body move as one
unit in any orientation, ready for the faucet-and-umbilical bench.

## Verification

After the screws are snug:

- **Plate seats flat against shell.** No visible gap at the joint
  line anywhere around the perimeter. A gap means the body is
  fouling the bore (most likely the lever orientation), debris in a
  boss hole, or a screw run home before its boss was fully seated.
- **Screw heads recessed.** Run a fingertip across the plate bottom —
  no head proud of the face.
- **Body has no rotational play.** Try to rotate the body relative to
  the shell + plate by grabbing the lever and twisting. Should be
  rigid, set by the rectangular zone-2 profile inside the rectangular
  bore.
- **Lever swings freely.** Press the lever toward the -Y ramp; it
  should pivot through its full ~18° travel without contacting the
  shell. Release; it should spring back to rest under the factory
  return spring.
- **Pill slot is clear.** Sight down through the pill slot from above
  to below — the shell slot, the body's open -Y side, and the plate
  slot should form a continuous opening for the two flavor tubes.

## Disassembly (for service)

Reverse order:

1. Back the three M3×12 out from below the plate.
2. Lift the shell straight up off the body + plate.
3. Loosen and remove the factory shank nut; the body lifts up and out
   of the plate's shank hole.

The brass inserts take the thread wear — the joint re-mates
indefinitely.

## Troubleshooting

| Symptom                                       | Likely cause                                                 | Fix                                                                                    |
| --------------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| Plate-to-shell joint won't close (visible gap) | Body fouling the shell bore (most likely lever orientation), or support material / stringing in a boss hole | Disassemble; verify the body slides all the way to the bore cove and the no-body boss dry-fit seats flat; clear the offending pod; re-orient lever to -Y if needed. |
| Lever binds against shell                     | Lever orientation off, or shell -Y ramp printed with a support stub remaining | Disassemble; clear the ramp; re-orient body so lever points to -Y. |
| Boss binds entering its hole                  | Stringing or first-layer squish at the hole rim               | Clean the rim; re-run the pre-flight boss dry-fit. |
| Insert spins or pulls out                     | Insert seated cold or shallow                                 | Re-seat with the iron until the mouth is flush with the hole ceiling. |

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/touch-flo-shell/touch_flo_shell.py`
