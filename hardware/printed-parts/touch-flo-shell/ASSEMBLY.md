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

Downstream:

4. Route the two flavor tubes up through the pill slot.
5. Slide the TPU `touch-flo-mounting-gasket` over the shank from below.
6. Drop the assembly into the 1-3/8" countertop hole; tighten the
   factory shank nut against the gasket.

This document covers step 3a — joining the printed parts to the body
into a single rigid sub-assembly.

## Materials

| Qty | Item                                                 | Reference                                                                          |
| --- | ---------------------------------------------------- | ---------------------------------------------------------------------------------- |
|  1  | `touch-flo-shell` (printed, PET-CF)                  | [`generate_step_cadquery.py`](generate_step_cadquery.py)                            |
|  1  | `touch-flo-mounting-plate` (printed)                 | [`../touch-flo-mounting-plate/`](../touch-flo-mounting-plate/)                      |
|  1  | Touch-Flo valve body + factory shank nut (harvested) | [`../../harvested/touch-flo-faucet/`](../../harvested/touch-flo-faucet/)            |
|  2  | ruthex M3 short heat-set inserts (Ø 4.6 knurl OD, Ø 4.0 hole, 4 mm length) | Amazon Prime [B09ZHSGHXD](https://www.amazon.com/dp/B09ZHSGHXD) |
|  2  | 316 SS M3 × 8 mm ultra-low-profile socket cap screws (head Ø 5.5 × 1.0 mm, 2 mm hex) | McMaster [91223A413](https://www.mcmaster.com/91223A413/) |

The two flavor tubes that pass through the pill slot are NOT installed
at this step — they're routed in the downstream "tube routing" step,
which is easier with the shell + plate already joined and the body
clamped.

## Tools

| Item                                          | Reference                                                                  |
| --------------------------------------------- | -------------------------------------------------------------------------- |
| Hakko FX-888D soldering station               | Amazon [B0D4DJW54S](https://www.amazon.com/dp/B0D4DJW54S)                  |
| Hakko T18-mount heat-set tip kit, M3 tip used | Amazon [B0CS662NVK](https://www.amazon.com/dp/B0CS662NVK)                  |
| 2 mm hex driver / Allen key                   | Bambu printer toolkit                                                      |
| 3.9 mm drill bit / #29 drill (optional)       | Only if the printed plate's clearance hole prints undersized — see Pre-flight |

## Geometry summary

The two retention features:

- **Shell, bottom face:** two pockets at world (14.14, ±14.14) — i.e.
  on the rear shoulder wall material at θ ≈ ±45°. Each pocket is
  Ø 4.0 × 5 mm deep (sized for the 4 mm insert plus 1 mm relief at the
  top so the insert seats flush, not proud).
- **Plate, both faces:** two clearance holes Ø 3.9 mm at the same XY,
  with Ø 5.7 × 1.25 mm counterbores cut into the plate's bottom face
  for the screw heads. The Ø 5.5 × 1.0 mm head of the
  91223A413 lands fully recessed below the plate's bottom face.

Stack-up at the screw axis, top to bottom:

```
      shell wall (PET-CF)
      └── M3 heat-set insert, top flush with shell bottom face
           └── M3 × 8 mm ULH thread engagement: ~3 mm into insert
                └── plate clearance Ø 3.9, 4 mm thick
                     └── plate counterbore Ø 5.7 × 1.25 mm
                          └── screw head Ø 5.5 × 1.0 (0.25 mm sub-flush)
```

The body-to-plate joint is independent of this screw joint: the
factory shank nut clamps the body's 31.5 mm OD bottom face down onto
the plate's top face through the plate's Ø 12.6 shank hole. The
screws-through-plate-into-shell joint is what then captures the body
inside the shell's body bore — the body has nowhere to go because the
shell is anchored to the plate that's already clamped to the body.

## Pre-flight check

1. **Support material removal.** Confirm the shell's body bore, the
   shell's two insert pockets, and the plate's clearance holes,
   counterbores, shank hole, and pill slot are all clear of supports
   and stringing. The two M3 pockets in the shell are small features
   on the bottom face — easy to miss.
2. **Insert pocket gauge.** A ruthex insert should be a slip fit
   (drops in by gravity to roughly its first knurl) into the cold
   shell pocket, NOT a press fit. If it won't enter, the pocket
   printed undersized — re-slice with a +0.05 mm horizontal expansion
   compensation, don't ream. (Reaming PET-CF leaves loose fibers that
   foul the heat-set cone.)
3. **Plate clearance hole gauge.** An M3 × 8 ULH should drop through
   the plate hole by gravity, with the head landing inside the
   counterbore and seating against the shoulder. If the screw shank
   binds, drill out to 3.9 mm with a sharp #29 bit. If the head sits
   proud of the plate's bottom face, the counterbore printed shallow
   — verify the part is the current revision.
4. **Body fit.** Dry-fit the harvested body into the shell's bore from
   the bottom (shell oriented bottom-up). The body should slide all
   the way to the bore cove (Z = 18.25 in part coordinates) without
   binding. The lever swings in the shell's -X clearance ramp; verify
   the lever clears at the resting position.

## Step 1 — Heat-set inserts into the shell

Set the Hakko FX-888D to **230 °C** with the M3 heat-set tip
installed. PET-CF and PETG both heat-set in the 220–240 °C window;
230 °C is the middle of the band and works for either material.

Orient the shell bottom-face up on a flat work surface. The two insert
pockets are on the rear shoulder of the shell, at world (14.14,
±14.14), visible as Ø 4.0 mm holes flanking the body bore on the +X
side.

For each pocket:

1. Place a ruthex insert flange-down into the pocket so it slip-fits
   into the lead-in. Confirm by eye that it's sitting square — the
   insert's top face should be parallel to the shell bottom face, not
   tilted.
2. Bring the heated tip down vertically into the insert's threaded
   bore. Let the tip pre-heat the insert for ~1 second before
   pressing.
3. Press straight down with **light, steady force**. The insert melts
   the surrounding plastic and sinks under its own weight plus a few
   newtons of finger pressure. Do NOT push hard — speed of descent is
   set by heat transfer, not pressure.
4. Stop when the insert's top face is **flush with or 0.1–0.2 mm
   below** the shell's bottom face. The 1 mm relief above the 4 mm
   insert in the 5 mm pocket is exactly this travel margin — once the
   insert hits the relief, it's fully seated.
5. Withdraw the tip vertically. Hold the shell still for 5–10 seconds
   so the insert sets without rotating or tilting as the surrounding
   plastic re-solidifies.

Common failure modes:

- **Insert tilted in pocket.** Caused by entering the pocket
  off-axis or pressing with the iron at an angle. Re-heat the tilted
  insert and press straight down to correct, or back the insert out
  with the tip while hot, let the pocket solidify, and re-press.
- **Halo of melted plastic around the insert top.** Tip too hot,
  contact time too long, or both. Drop to 220 °C and shorten the
  pre-heat dwell. A small halo is cosmetic and harmless; a deep
  crater means the insert is sitting in soft plastic with reduced
  pull-out strength — extract and re-set with a fresh pocket if
  available, or de-rate the joint expectations.
- **Insert pressed below flush by more than ~0.3 mm.** The plate's
  clearance hole is 3.9 mm and the insert's hole is 3.0 mm; an over-
  recessed insert means the screw threads into open space before
  catching. If the insert sank too far, accept it and use an M3 × 10
  screw at this joint instead — but verify head-to-counterbore
  clearance on the plate (10 mm − 4 mm plate − 0.25 mm sub-flush
  margin = 5.75 mm into the insert, well past the 4 mm insert
  length, will bottom out unless there's clearance below the insert
  in the shell). Default response: re-print the shell.

## Step 2 — Body into mounting plate

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

## Step 3 — Shell over body, screws up from below

1. Hold the plate + body sub-assembly with the body pointing up. Drop
   the shell down over the body so the body enters the shell's bore
   from the bottom. The shell's -X lever clearance ramp must align
   with the lever (which you already pointed toward -X in Step 2).
2. Push the shell down until its bottom face seats flat against the
   plate's top face. The body's 31.5 mm landing is now sandwiched
   between the plate (below) and the shell's body bore floor at
   Z = 18.25 — but in practice the shell sits on the plate, not on
   the body, so the joint geometry is plate-to-shell-bottom-face flat.
3. Verify the shell's pill slot aligns with the plate's pill slot
   (both at world (18.925, 0), Y-oriented). They should overlay
   exactly. If they don't, the shell is rotated 180° about the
   shell-center vertical axis — lift it off, rotate, and re-seat.
4. Insert one M3 × 8 mm ULH screw from below through one of the
   plate's counterbored holes. Thread it up into the corresponding
   heat-set insert in the shell by finger only at first, confirming
   that the screw catches without cross-threading. Repeat for the
   second screw.
5. Snug both screws with the 2 mm hex driver in an alternating
   pattern (a few turns on one, a few on the other) until both are
   firm. **Snug only — no torque spec.** This is a retention joint,
   not a structural one; the body clamp through the shank nut is
   what carries the dispense reaction loads. Over-torquing risks
   stripping the heat-set insert out of the PET-CF.

## Verification

After both screws are snug:

- **Plate seats flat against shell.** No visible gap at the joint
  line anywhere around the perimeter. A gap on one side means the
  body is fouling the bore — most likely the lever orientation was
  off, or the body wasn't pushed all the way up against the bore
  floor before the shell came down.
- **Screw heads fully recessed.** Run a fingertip across the plate's
  bottom face — both heads should sit ≥ 0.2 mm below the surface.
  Required for the gasket to seat flat at the next step.
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

1. Back both M3 ULH screws out with the 2 mm hex. Set them aside.
2. Lift the shell straight up off the body. The body and plate stay
   together at this point because the factory shank nut is still
   clamped.
3. To separate body from plate: loosen and remove the factory shank
   nut from below the plate; the body lifts up and out of the plate's
   shank hole.

The heat-set inserts stay in the shell. They survive an unbounded
number of insertion / removal cycles at the M3 × 8 ULH screw — they
fail only if over-torqued during install.

## Troubleshooting

| Symptom                                       | Likely cause                                                 | Fix                                                                                    |
| --------------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| Screw won't pass through plate hole           | Plate clearance hole printed undersized                      | Drill out to 3.9 mm with a #29 bit. Re-slice with horizontal expansion compensation if recurring. |
| Screw head sits proud of plate bottom face    | Counterbore printed shallow, or wrong screw (head > 1.0 mm)  | Verify part revision; verify screw is 91223A413 (head 1.0 mm), not a standard SHCS (head 3.0 mm). |
| Screw bottoms out before head seats           | Wrong screw length — likely M3 × 10 instead of M3 × 8        | Verify screw is M3 × 8. M3 × 10 would bottom out in the 4 mm insert at this stack-up. |
| Insert tilted in shell pocket after press     | Off-axis entry, off-axis press, or both                      | Re-heat the insert and press straight down. If unrecoverable, extract while hot with the iron tip and re-press a fresh insert (or re-print shell if the pocket itself is degraded). |
| Insert spins in pocket under screw torque     | Pocket walls melted past the knurl during install (over-hot, over-pressed) | Apply a drop of CA glue around the insert top and let cure. If recurring at multiple inserts, drop the iron temp 10 °C. |
| Plate-to-shell joint won't close (visible gap) | Body fouling the shell bore (most likely lever orientation), or support material left in the shell bore | Disassemble; verify the body slides all the way to the bore cove with no resistance; re-orient lever to -X if needed. |
| Lever binds against shell                     | Lever orientation off, or shell -X ramp printed with a support stub remaining | Disassemble; clear the ramp; re-orient body so lever points to -X. |
