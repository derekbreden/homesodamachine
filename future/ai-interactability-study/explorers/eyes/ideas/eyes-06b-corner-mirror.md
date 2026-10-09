# eyes-06b The corner is a mirror (branch of eyes-06)

Scene: `scenes/eyes-06-dot-as-probe/` mode "A mirror pair". Origin: swarm (eyes framing), branch. Maturity: sketch to developed. The whole idea depends on a surface finish nobody has looked at.

**Picture it.** With the red dot on the plate a couple of millimetres short of the wall, a second red spot sits on the wall above it: the plate has thrown the beam onto the wall. Nudge the dot toward the corner and the two spots slide toward each other; when the dot is on the corner they merge into one. A camera does not need to know where anything is; it counts one spot or two.

## The proposal

An inside corner between a plate and a wall is a dihedral mirror. If the plate is mirror-like at 650 nm, the pilot beam reflects off it and lands on the wall. Geometry (section plane, beam tilted beta from vertical toward the wall): whatever the direct spot's offset from the corner, the pair is always {plate at |s|, wall at |s| cot(beta)}. The two spots merge exactly when the dot is on the corner. The pair separation along the profile is (1 + cot(beta)) |s|: 2.6 |s| at 32 degrees. Which spot is the brighter one (the direct one) tells the sign of s.

The gain matters. Seen from a low camera across the bore, radial error on the plate is compressed to sin(elevation) (0.09 at 5 degrees) while height on the wall is seen at cos(elevation) (1.0). Reading the pair separation instead of the single dot against the corner is 19 times more sensitive from there (calc/dot-probe.mjs; 7 times at 15 degrees, 2.6 at 45). The bounce turns a hard-to-see radial offset into an easy-to-see vertical one and magnifies it by cot(beta).

The same trick applies to the **wire tip**: a metal wire near a two-mirror corner has four images (direct, plate-reflected, wall-reflected, both), which converge as the tip nears the corner.

## What carries loads, what establishes position, what is free or restrained

As eyes-06: any small radial axis; the corner is the reference; nothing else carries anything new.

## What software could command, observe, and what stays manual

- **Command:** the radial axis. **Observe:** one or two spots, their separation along the profile, their relative brightness. **Manual:** deciding the finish assumption; looking at the real plate.

## What was tried to break it

1. **The plate is not a mirror.** Brightness of the bounce relative to the direct spot is reflectance times the specular fraction: 0.6 x spec (reflectance at 650 nm 0.6, illustrative): 0.12 at spec 0.2, 0.30 at 0.5, 0.48 at 0.8. At a rough finish the bounce is too dim to use (a badge in the scene). Assumption: the as-cut plate face and the bore behave like polished stainless. What it leaves uncertain: the plate's finish, and the wall's diffuse fraction that must scatter the bounce toward the camera.
2. **The bounce blurs.** The reflected lobe widens with roughness; over a path of |s|/sin(beta) it spreads a fraction of a millimetre (0.2 mm across at 0.7 specular, |s| = 1.1 mm in the scene). Fine at small offsets, useless at large.
3. **The scanned/scuffed prep.** The joint surfaces are prepped with Scotch-Brite 7447 (**[repo]** pressure-vessel.md), which makes an anisotropic satin finish: reflection goes into a lobe along the scratches. Uncertain whether that helps or kills the bounce.
4. **Safety.** 0.3 mW is small. The real 700 W beam reflects off the same plate onto the wall; this scene draws the pilot only. Nothing here should be tried with the laser emitting.
5. **A grazing camera cannot see the plate spot** (Lambert 0.09 at 5 degrees) but does not need to: the wall spot alone gives the offset (1.6 |s|) and its brightness gives the surface finish's specular fraction.

## Branches and combinations

Parent: `eyes-06-dot-as-probe`. The bounce spot on the wall is *also* an inclinometer: its height per millimetre of offset is cot(beta), so the ratio measures the beam tilt in the section directly (the "partly" cell for grip-axis roll in `eyes-11-what-each-eye-sees`).

## Unresolved problems, questions for Derek

Everything about the surface. **Question for Derek (the cheapest test in this study):** put the red dot on the plate about 3 mm short of the wall, in a dim room. Do you see a second red spot on the wall above it? Does it merge with the first as you move into the corner?

## Assumptions

Geometry exact (mirror reflection) **[derived]**. Reflectance 0.6 at 650 nm **illustrative**. Specular fraction and lobe (2 + 12 x (1 - spec) degrees) **illustrative**. Beam tilt 32 degrees (reference pose, illustrative).

## Sourcing pointers

As eyes-06. No special parts.

## Scene

`eyes-06-dot-as-probe`, mode "A mirror pair". Scene edits: plate finish (specular fraction), tilt, camera direction, pixel size.
