# use-11-setup-gauge: aim at a corner you can see

Scene: `scenes/use-11-setup-gauge/index.html`. Origin: swarm. Maturity: rough (arrangement A9 of the notebook).

## Picture it

A translucent teal tube stands in the nest where a tube would. Its wall is missing over a 100 degree window on the weld-station side, above the plate, and a thin yellow line is printed on the plate top at the seam radius. The red dot sits on the line and an outside camera sees both. Toggle to the real tube: the wall closes and the same camera sees only a grey cylinder.

## The proposal

Set the pose on a **stand-in you can see**, weld on the real tube. A gauge tube, printed or machined with the same bore, plate face height and nest fit as a tube, has a window through the wall around the weld station and a target line on the plate at the seam radius. A person (or the coach loop, `use-06-coach-loop`) trims the gun until the dot sits on the line, seen from outside by a camera or an eye; then the real tube is swapped into the same nest and the register carries the pose. Other reference, other sequence: the reference for aiming is not the workpiece but a stand-in for it. This is the setup-block or setting-gauge practice of tool setting: the operation is done on the gauge, the part is made on the machine.

It is a per-campaign tool: it does not remove per-tube aiming, only the first placement and any re-placement after the gun's support has been touched.

## What carries the loads, what establishes position, what is free or restrained

Unchanged from whatever supports the gun in the other scenes (the gun floats in this scene). The gauge sits in the nest like a tube and is carried by the same register; the pilot's 0.20 mm radial clearance and the three screws [repo] locate it.

## What software could command, observe, and what stays manual

- **Command:** the existing rotator (to turn the gauge and see the line all around).
- **Observe:** dot against the printed line from outside; which of gauge and tube is in the nest.
- **Not observable:** the dot on the real tube from outside (blocked by the wall from every viewpoint the scene tries).
- **Manual:** trimming the gun, swapping, checking the gauge against a real tube.

## What was tried to break it

1. **The gauge is not the tube.** *Conflict:* the window and the printed line replace the real corner; a printed line sits some unknown distance from where a real corner would be (printing error, warp, humidity for PET-GF [assumed]). *Assumption:* the stand-in is equivalent. *Change:* the swap error is shown as the gauge's own error (a slider, one to one) plus the register's repeatability (a slider); the gauge is checked against a real tube with the calipers or the Revopoint scanner (the repo says scanning is established [repo tools.md]). *Leaves:* nobody has measured either number.
2. **Line of sight.** *Conflict:* the dot at a 6 mm recess against a wall is invisible from outside (the reference scene's own camera lives above and beyond the far rim). *Change:* the window; the scene's camera inset turns green with the gauge in and red with the real tube in, at every azimuth tried. *Leaves:* real optics, light, fume: not modelled.
3. **The register.** *Conflict:* a gauge and a tube sit in the pilot differently. *Change:* indicate the gauge like a tube; keep the register clearance small (see `use-03-preset-cartridge`). *Leaves:* the difference.
4. **Is it worth it?** *Conflict:* each swap adds its error and a hand step. *Change:* it is meant for set-up and re-set, not per tube; if the gun sits on a seat (`use-02-swing-head`) the gauge is used once per campaign, and if the pose can be found by the dry lap alone the gauge is only a shortcut. It may turn out to be a tool for teaching the AI what "on the seam" looks like before the first real tube.

## Branches and combinations

- Combines with `use-06-coach-loop` (the coach's camera sees the dot through the window; the loop converges on the gauge line) and `use-02-swing-head` (the trim of the fixed pose).
- A machined aluminium ring instead of a printed one (unresolved: which).

## Unresolved problems and questions for Derek

- Would a see-through gauge tube in the nest be acceptable to build and check once per campaign?
- The dot-to-melt offset [unknown]: what "on the line" means for the melt.

## Assumptions

- **[repo]** tube, plate, joint geometry; pilot clearance 0.20 mm; three adjusters; scanning and printing are established.
- **[unknown]** gauge printing error, register difference, dot-to-melt offset.
- Illustrative: the window (100 degrees, above z = 100 mm), error ranges, camera bias.

## Sourcing pointers

None specific; a UVC camera in `sourcing/use.md`.

Scene id: `use-11-setup-gauge`.
