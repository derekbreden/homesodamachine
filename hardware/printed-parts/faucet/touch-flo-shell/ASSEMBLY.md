# Touch-Flo shell + mounting plate sub-assembly

Bench procedure for joining the printed `touch-flo-shell` to the printed
`touch-flo-mounting-plate` with the harvested Touch-Flo valve body
sandwiched between them. This is the sub-assembly that gets handed off
to the countertop install step (gasket + under-counter nut against the
deck) — it does not include the gasket or the deck nut.

## Where this fits in the build

Upstream:

1. Print `touch-flo-shell` (PET-CF, 0.6 mm DUROZZLE TC nozzle, see
   [`print-log.md`](/hardware/printed-parts/faucet/touch-flo-shell/print-log.md) attempt 7 settings).
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
   top surface as the assembly seats. The three tubes + Cat6 hang down
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
|  1  | `touch-flo-shell` (printed, PET-CF) — smooth bottom face, no joinery features | `touch_flo_shell.py` in this directory                            |
|  1  | `touch-flo-mounting-plate` (printed) — smooth top face, no joinery features | [`/hardware/printed-parts/faucet/touch-flo-mounting-plate/`](/hardware/printed-parts/faucet/touch-flo-mounting-plate/) |
|  1  | Touch-Flo valve body + factory shank nut (harvested) | [`/hardware/reference/touch-flo-faucet/`](/hardware/reference/touch-flo-faucet/)            |

No fasteners or printed retention features. The plate is held to the shell by gravity + body friction during sub-assembly handling; once installed in the countertop, the factory shank nut clamps the whole stack (body → plate → TPU gasket → countertop) and that clamp carries every load thereafter.

The two flavor tubes that pass through the pill slot are NOT installed
at this step — they're routed in the downstream "tube routing" step,
which is easier with the shell + plate already joined and the body
clamped.

## Adjacent parts

Two parts in the touch-flo stack aren't joined by this sub-assembly but
sit immediately adjacent to it, so their spec lives here for one-stop
reference:

**Donor faucet body — Westbrass R2031-NL family.** The BOM SKU is
R2031-NL-62 (matte black, B07KH285GJ). Any finish variant in the
R2031-NL series is interchangeable for this build because the finish is
fully hidden by the printed touch-flo-shell — only the mechanism +
shank are exposed. R2031-NL-12 (oil-rubbed bronze, B01N5LVNQA) is the
same mechanism with a different finish. Pick whichever is cheaper /
Prime-available at order time.

**Under-counter plate — SendCutSend 0.060" 304 SS, keyhole design
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
| Flat work surface + clean rag                 | For setting the plate boss-up and pressing the shell down by hand          |
| Rubber mallet (optional)                      | If the press fit needs a gentle tap to fully seat — finger pressure first  |

No soldering iron, no heat-set tooling, no hex driver — this sub-assembly is screw-free.

## Geometry summary

**No joinery features.** The plate is a clean disc with only the
shank hole + pill slot through it. The shell's bottom face is
similarly clean. There is no positive retention or alignment
between the plate and the shell on this sub-assembly.

What holds the parts together:

- During sub-assembly handling (between this bench and the
  faucet-and-umbilical bench): **gravity** holds the shell down on
  the plate, and the harvested body inside the shell's bore
  laterally constrains the plate (the body is rigidly attached to
  the plate via the snug shank nut from Step 1; the body sits in
  the shell's bore with a [0.25 mm](BORE_CLEAR)/side slip-fit, so the plate
  can't slide sideways without dragging the body and shell with
  it). The shell can be lifted straight off the body+plate freely;
  handle the sub-assembly without inverting it until the umbilical
  tubes are routed at the next bench (the tubes through the pill
  slot will then friction-lock the whole stack).
- Once installed in the countertop: the **factory shank nut**
  threaded onto the body's shank from below compresses the entire
  stack — body landing face down onto plate top, plate bottom down
  onto TPU gasket, gasket bottom down onto countertop top. That
  compression is what carries every load for the life of the
  appliance.

Stack-up at the plate-to-shell interface (rear shoulder region):

```
      shell wall (PET-CF) — solid material, no pockets
      └── shell bottom face (smooth)
           └── plate top face (smooth, in contact with shell bottom by gravity)
                └── 4 mm plate (solid material, no holes here)
                     └── plate bottom face (smooth, against TPU gasket)
```

**Plate bottom face must stay flat for the TPU gasket.** The
mounting plate sits *above* the countertop — its top face mates with
the shell bottom (this doc's joint), its bottom face mates with the
TPU `touch-flo-mounting-gasket` that then seals against the
countertop's top surface. The plate's bottom face must stay flat
against the gasket; the current screw-free, dowel-free design keeps
the rear-shoulder region of the plate bottom fully smooth.

The factory shank nut clamps the body's [31.5 mm](BODY_OD) OD bottom
face onto the plate's top face through the plate's Ø 12.6 shank hole.
The shell sits over the body+plate stack; the body inside the shell's
bore provides lateral and rotational constraint (rectangular zone-2
cross-section + lever orientation).

## Pre-flight check

1. **Support material removal.** Confirm the shell's body bore and
   the plate's shank hole + pill slot are all clear of supports and
   stringing.
2. **Body fit.** Dry-fit the harvested body into the shell's bore
   from the bottom (shell oriented bottom-up). The body should
   slide all the way to the bore cove (Z = [19.25 mm](BORE_COVE_Z) in part
   coordinates) without binding. The lever swings in the shell's
   -Y clearance ramp; verify the lever clears at the resting
   position.

## Step 1 — Body into mounting plate

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

## Step 2 — Shell over body

1. Hold the plate + body sub-assembly with the body pointing up. Drop
   the shell down over the body so the body enters the shell's bore
   from the bottom. The shell's -Y lever clearance ramp must align
   with the lever (which you already pointed toward -Y in Step 1).
2. Push the shell down until its bottom face seats flat against the
   plate's top face. There is nothing to press into — the shell just
   slides down over the body and rests on the plate by gravity.
3. Verify the shell's pill slot aligns with the plate's pill slot
   (both at world (0, +[18.93 mm](FLAVOR_TUBE_Y)), X-oriented). They should overlay
   exactly. If they don't, the shell is rotated 180° about the
   shell-center vertical axis — lift it straight up off the plate
   (no resistance, since there's no joinery), rotate, and re-seat.

The sub-assembly is now visually complete but the shell is held to
the plate **only by gravity**. The plate is rigidly attached to the
body (via the shank nut from Step 1), and the body is laterally
held in the shell by the body bore's slip fit — so the shell can't
slide sideways without dragging the plate with it — but the shell
*can* be lifted straight up off the body+plate freely. Handle the
sub-assembly upright (shell up, plate down) until it reaches the
faucet-and-umbilical bench, where the three LLDPE tubes routed
through the pill slot will friction-lock the stack.

## Verification

After the shell is seated:

- **Plate seats flat against shell.** No visible gap at the joint
  line anywhere around the perimeter. A gap means the body is
  fouling the bore — most likely the lever orientation was off, or
  the body wasn't pushed all the way up against the bore floor
  before the shell came down.
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

1. Loosen and remove the factory shank nut from below the plate.
2. Lift the shell straight up off the body + plate. No resistance
   — the shell sits free on the plate.
3. The body lifts up and out of the plate's shank hole.

The shell and plate can be re-mated any number of times without
wear — there's nothing to wear.

## Troubleshooting

| Symptom                                       | Likely cause                                                 | Fix                                                                                    |
| --------------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| Plate-to-shell joint won't close (visible gap) | Body fouling the shell bore (most likely lever orientation), or support material left in the shell bore | Disassemble; verify the body slides all the way to the bore cove with no resistance; re-orient lever to -Y if needed. |
| Lever binds against shell                     | Lever orientation off, or shell -Y ramp printed with a support stub remaining | Disassemble; clear the ramp; re-orient body so lever points to -Y. |
| Shell falls off plate during handling         | Sub-assembly was inverted or jolted before umbilical routing locked the stack | Re-seat; handle upright (shell up) until the umbilical tubes are routed at the next bench. A piece of masking tape across the joint is fine as a transport aid. No design fix needed — the shell is intentionally held by gravity only at this stage. |

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/touch-flo-shell/touch_flo_shell.py`
