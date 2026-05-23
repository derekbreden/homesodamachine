# Touch-Flo shell + mounting plate sub-assembly

Bench procedure for joining the printed `touch-flo-shell` to the printed
`touch-flo-mounting-plate` with the harvested Touch-Flo valve body
sandwiched between them. This is the sub-assembly that gets handed off
to the countertop install step (gasket + under-counter nut against the
deck) — it does not include the gasket or the deck nut.

## Where this fits in the build

Upstream:

1. Print `touch-flo-shell` (PET-CF, 0.6 mm DUROZZLE TC nozzle, see
   [`print-log.md`](print-log.md) attempt 7 settings).
2. Print `touch-flo-mounting-plate` (PETG or PET-CF, same H2C).
3. Harvest the Touch-Flo valve body from the donor faucet per
   [`../../harvested/touch-flo-faucet/README.md`](../../harvested/touch-flo-faucet/README.md).
   Keep the lever, the body, and the factory shank nut. Discard the
   factory mounting plate.

Downstream (at the faucet-and-umbilical bench, see [`../../../assembly/faucet-and-umbilical.md`](../../../assembly/faucet-and-umbilical.md)):

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

Downstream (at the customer's countertop install, supported by the
installer instruction sheet that ships in the bag):

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
|  1  | `touch-flo-shell` (printed, PET-CF)                  | [`generate_step_cadquery.py`](generate_step_cadquery.py)                            |
|  1  | `touch-flo-mounting-plate` (printed) — carries two Ø 4.0 × 5 mm press-fit dowel bosses on its top face | [`../touch-flo-mounting-plate/`](../touch-flo-mounting-plate/) |
|  1  | Touch-Flo valve body + factory shank nut (harvested) | [`../../harvested/touch-flo-faucet/`](../../harvested/touch-flo-faucet/)            |

No fasteners. No heat-set inserts. The plate is retained to the shell by the two integral dowel bosses press-fitting into matching Ø 4.05 × 6 mm pockets in the shell's bottom face. (Superseded the earlier 2× ruthex M3 short heat-set + 2× M3 × 6 mm ULH SHCS retention on 2026-05-22 — that joinery was retention-only too, but added two soldering-iron steps and required McMaster-only $4-6/each ULH screws with a 2 mm hex that stripped easily.)

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
by `generate_dxf.py` in the same directory) is a single-piece
Ø 54.35 mm disc with hole positions that match the TPU mounting
gasket exactly — Ø 12.6 mm shank pocket at the gasket's shank center
and a 13.2 × 6.85 mm pill pocket (long axis along Y) at the gasket's
pill center, 18.925 mm away along +X. Each pocket has its own
open-edge channel extending from the pocket to the disc rim in the
−Y direction (channel widths: 12.6 mm for the shank, 6.85 mm for the
pill). The two channels exit the rim at different X positions and
do not merge. The four corners where the channel walls meet the
rim are rounded with R 1.5 mm fillets — these would otherwise be
sharp acute tips (handling hazard, laser-dross-prone, no help with
alignment); the fillets dull them and give the cylinders a small
lead-in funnel at each channel mouth.

The keyhole design exists because the faucet + umbilical leave the
faucet-and-umbilical build chain as one permanently-attached
sub-assembly — the LLDPE tubes are clamped to the Westbrass body and
never separated again. A solid one-piece disc would force the
installer to thread already-attached tubes through the pill slot
from below. The keyhole's open-edge channels let the installer slide
the plate laterally past the dangling cylinders; both the shank and
the tube bundle enter through their channel mouths at the rim and
seat in their terminal pockets. Once seated, the cylinders sitting
in the narrow channels keep the plate from drifting back out of
alignment under gravity, letting the installer thread the shank nut
one-handed.

Anti-rotation during nut tightening is provided by the cylinders
themselves: any rotational drift of the plate immediately presses the
shank and tube bundle against the channel walls. No silicone bumpers
needed (unlike the prior one-piece-with-closed-pill-slot design that
this iteration supersedes).

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

The two retention features (mirrored across Y=0, at θ = ±45° about
the body center, r = 20 mm from body center — world (14.14, ±14.14)):

- **Plate, top face:** Ø 4.0 mm × 5 mm tall solid cylindrical bosses
  extruded UP, with a 0.5 mm × 45° chamfer at the tip for
  self-alignment.
- **Shell, bottom face:** matching Ø 4.05 × 6 mm deep cylindrical
  pockets. The 0.05 mm diametric CAD clearance is overrun by FDM
  tolerances (boss prints slightly oversize, pocket prints slightly
  undersize) to produce a real press fit when assembled. The extra
  1 mm of pocket depth above the boss tip accommodates FDM
  bottom-layer flatness variance in the pocket floor.

Stack-up at one dowel axis, top to bottom:

```
      shell wall (PET-CF)
      └── ~1 mm empty pocket above boss tip (FDM floor variance)
           └── Ø 4 mm × 5 mm dowel boss in pocket (press fit)
                └── plate top face (boss base)
                     └── 4 mm plate (no holes at this XY)
                          └── plate bottom face (smooth)
```

**Plate bottom face must stay flat for the TPU gasket.** The
mounting plate sits *above* the countertop — its top face mates with
the shell bottom (this doc's joint), its bottom face mates with the
TPU `touch-flo-mounting-gasket` that then seals against the
countertop's top surface. The plate's bottom face is never seen
from below the counter and is never under-counter; only the body's
threaded shank and the three umbilical tubes pass through the
countertop hole. Anything that breaks the flatness of the plate's
bottom face would dish into the gasket and compromise the
countertop seal. This is the constraint that drove the press-fit
choice for the dowels (bosses extend UP from the plate top into the
shell — the plate's bottom face has *no holes at all* at the dowel
positions, fully smooth against the gasket).

**Joinery history.** v1 used 2× ruthex M3 short heat-set inserts in
the shell + 2× ULH M3 × 6 mm SHCS (McMaster 91223A412) coming up
from below through plate counterbores. The ULH (vs standard SHCS)
choice was driven by the same gasket-flatness constraint above: a
standard SHCS head (3 mm tall) protruding from a 1.25 mm counterbore
would have stuck 1.75 mm proud of the plate's bottom face and
dished the gasket; the ULH head (1 mm tall) sat 0.25 mm *sub-flush*
in that same counterbore so the gasket saw a near-flat surface. The
screw design worked, but: (a) the $4-6/each McMaster-only screws
were hard to source and the 2 mm hex stripped easily; (b) the
heat-set step added soldering-iron time to every shell; (c) the
joint was always retention-only — no structural load — so a press
fit does the same job with zero fasteners *and* leaves the plate
bottom face fully smooth (no counterbore dimple, no sub-flush
head — gasket-better than the screw design ever was). Switched on
2026-05-22 (commit `e5aa8a1`).

The body-to-plate joint is independent of the dowel joint: the
factory shank nut clamps the body's 31.5 mm OD bottom face down onto
the plate's top face through the plate's Ø 12.6 shank hole. The
dowel-into-pocket joint is what then captures the body inside the
shell's body bore — the body has nowhere to go because the shell is
anchored to the plate that's already clamped to the body.

## Pre-flight check

1. **Support material removal.** Confirm the shell's body bore, the
   shell's two dowel pockets, and the plate's shank hole and pill
   slot are all clear of supports and stringing. The two Ø 4 mm
   dowel pockets in the shell are small features on the bottom face
   — easy to miss.
2. **Dowel press-fit gauge.** Hold the plate boss-up and try to
   press the shell down onto one boss by hand. It should require
   real finger force — somewhere between "easy slip-fit" (too
   loose, won't retain) and "stuck mid-insertion" (too tight, risk
   cracking the pocket on full assembly). If it slips on with no
   resistance, the press fit is dead and the parts need a re-print
   with adjusted boss/pocket dimensions (probably bump boss to
   Ø 4.05 or pocket to Ø 4.0). If it won't start, the pocket is
   probably blocked by stringing — re-check.
3. **Body fit.** Dry-fit the harvested body into the shell's bore from
   the bottom (shell oriented bottom-up). The body should slide all
   the way to the bore cove (Z = 18.25 in part coordinates) without
   binding. The lever swings in the shell's -X clearance ramp; verify
   the lever clears at the resting position.

## Step 1 — Body into mounting plate

1. Slot the Touch-Flo body's Ø 11 mm threaded shank up through the
   plate's Ø 12.6 shank hole. The body's 31.5 mm OD landing face
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
   profile (31.5 × 17 mm) above 13 mm cannot rotate inside the
   shell's bore that's about to come down on it. The body's
   rotational orientation is set by which way the lever points;
   orient the lever toward -X (the lever-clearance ramp side of the
   shell).

## Step 2 — Shell over body, dowels into pockets

1. Hold the plate + body sub-assembly with the body pointing up. Drop
   the shell down over the body so the body enters the shell's bore
   from the bottom. The shell's -X lever clearance ramp must align
   with the lever (which you already pointed toward -X in Step 1).
2. As the shell descends, the two Ø 4 mm dowel bosses on the plate
   should enter the matching pockets on the shell's bottom face. The
   0.5 mm × 45° chamfers on the boss tips self-align the engagement;
   the bosses don't need pre-aligned by eye if the shell's pill slot
   is roughly aligned to the plate's pill slot at the start.
3. Push the shell down with **steady hand pressure** until its bottom
   face seats flat against the plate's top face. The press fit
   resists insertion — that's the friction that will hold the joint.
   If finger force isn't enough to fully seat, tap the shell's top
   with a rubber mallet (not a steel hammer — risks cracking PET-CF).
4. Verify the shell's pill slot aligns with the plate's pill slot
   (both at world (18.925, 0), Y-oriented). They should overlay
   exactly. If they don't, the shell is rotated 180° about the
   shell-center vertical axis — pull it straight up off the bosses
   (also requires real force, that's intended), rotate, and re-seat.

## Verification

After the shell is fully seated:

- **Plate seats flat against shell.** No visible gap at the joint
  line anywhere around the perimeter. A gap on one side means the
  body is fouling the bore (most likely lever orientation off, or
  body not pushed all the way up before the shell came down) OR the
  dowel pockets didn't fully receive the bosses on one side
  (re-seat with a mallet tap on that side).
- **Sub-assembly survives gentle lift test.** Lift the assembled
  sub-assembly by the shell only — the plate should not separate
  under its own weight + the body's. If it does, the press fit is
  inadequate and the parts need redesign (boss/pocket interference
  adjustment).
- **Body has no rotational play.** Try to rotate the body relative to
  the shell + plate by grabbing the lever and twisting. Should be
  rigid, set by the rectangular zone-2 profile inside the rectangular
  bore.
- **Lever swings freely.** Press the lever toward the -X ramp; it
  should pivot through its full ~18° travel without contacting the
  shell. Release; it should spring back to rest under the factory
  return spring.
- **Pill slot is clear.** Sight down through the pill slot from above
  to below — the shell slot, the body's open -X side, and the plate
  slot should form a continuous opening for the two flavor tubes.

## Disassembly (for service)

Reverse order:

1. Loosen and remove the factory shank nut from below the plate.
2. Pull the shell straight up off the body + plate. The press fit
   on the dowels resists separation; pull hard enough to overcome
   the friction without rocking the shell side-to-side (rocking
   risks snapping a dowel boss off the plate).
3. The body lifts up and out of the plate's shank hole.

The dowel bosses survive multiple insertion / removal cycles, but
each cycle slightly loosens the press fit as the pocket walls take
small plastic deformation. After ~5 reassembly cycles, the joint
will likely no longer self-retain — at that point, re-print the
plate (or shell, whichever feels looser when re-mated). Both parts
are fast to re-print and don't carry any irreplaceable harvested
components.

## Troubleshooting

| Symptom                                       | Likely cause                                                 | Fix                                                                                    |
| --------------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| Shell drops onto plate with no resistance     | Dowel boss undersize, pocket oversize, or both — FDM tolerance smaller than expected on this filament / printer | Re-print the plate with `dowel_pin_radius` bumped 0.025–0.05 mm, or re-print the shell with `dowel_pocket_diameter` reduced by similar. Iterate. |
| Shell won't start onto the bosses             | Pocket blocked by stringing / support remnant, or boss prints far oversize | First clean the pocket with a fingernail or pick. If still stuck, dry-fit one boss-pocket pair alone to gauge; if the boss really is oversize, sand the boss tip lightly with 400-grit until it starts. |
| Shell starts but won't fully seat             | Press fit too tight at the boss base, or boss top hits pocket floor | Verify boss height (5 mm) is less than pocket depth (6 mm). If geometry is correct, the interference is too high — sand the boss OD lightly. |
| Sub-assembly separates under handling weight  | Press fit too loose for the press / printer / filament combo | See "Shell drops onto plate with no resistance" — same fix path. |
| Plate-to-shell joint won't close (visible gap) | Body fouling the shell bore (most likely lever orientation), or support material left in the shell bore | Disassemble; verify the body slides all the way to the bore cove with no resistance; re-orient lever to -X if needed. |
| Lever binds against shell                     | Lever orientation off, or shell -X ramp printed with a support stub remaining | Disassemble; clear the ramp; re-orient body so lever points to -X. |
| Dowel boss snapped off plate during disassembly | Rocked the shell side-to-side instead of pulling straight up | Re-print the plate; pull straight up next time. Single snapped boss + remaining boss usually means the sub-assembly held fine in service — failure was disassembly technique, not design. |
