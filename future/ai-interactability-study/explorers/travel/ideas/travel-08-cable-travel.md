# travel-08-cable-travel: the cables get their own travel

**Picture it.** The umbilical and the wire conduit leave the grip base and immediately ride a retractable balancer that hangs from a gallows above and behind the gun. The balancer holds their weight with a nearly constant force through its stroke, and the whole hanger can swing, so the gun feels only the cable's own stiffness. Whatever holds or moves the gun now carries the gun and a residual of grams.

Scene: `scenes/travel-08-force-path` (a free-body diagram; rough, all forces are placeholders). The hanger is also drawn as a fixed gallows in `scenes/travel-01-tube-travels`. Calculation: `calc/06-holder-and-flexure-stiffness.mjs`.

## The proposal

Split the force path. Every arrangement in this notebook has the umbilical and wire pulling on the gun at the grip base, "where they run together" **[Derek]**; that pull enters whatever stage carries the gun, and it is exactly the disturbance the stage was meant to be insensitive to. Give the cable its own carrier so its weight and its motion follow the gun without loading it. A constant-force spring balancer (a retractable tool balancer) is an ordinary object.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** the cable weight: the balancer and its gallows. The gun: whatever the arrangement uses.
- **Establishes position:** nothing: this idea does not locate anything.
- **Free:** the balancer's cable pays out and retracts; the hanger may swing. **Restrained:** by the cable's bending and torsional stiffness only.

## What software could command, observe, what stays manual

- **Commands:** none. **Observes:** nothing by default; a load cell in the balancer's line could report cable pull, and the reading could be fed to whatever stage carries the gun as a feed-forward.
- **Manual:** routing.

## What was tried to break it

**1. Unknowns.** *Conflict:* the cable's mass per length, bending stiffness and how much force it puts on the grip are all **[unknown]**; a Prime tool balancer covers 1-3 kg (`sourcing/travel.md` 13, low sales volume). *Change:* weigh the bundle and hang it from a spring scale in the working pose. *Leaves:* stiffness.

**2. Torsion of the fibre.** *Conflict:* beam roll is rotation about the line from the dot to the cable exit **[repo]**. If the cable leaves along that line, rolling the gun twists the fibre about its own axis, and the manual says twisting is strictly forbidden and gives minimum bend radii of 24 cm stored, 35 cm emitting **[manual]** p. 20. *Assumption:* the cable leaves along the roll axis. *Change:* a hanging loop that untwists by gravity (a long free span), or keep roll on the hand-set holder and never actuate it. *Leaves:* the real direction the cable leaves the grip is **[unknown]**. This matters for `travel-03` (roll costs nothing at the dot but may twist the fibre) and for any arrangement that motorises roll.

**3. The balancer's lateral stiffness.** *Conflict:* a hanging cable is a pendulum; a constant-force spring gives no stiffness along the line, but the lateral restoring force is weight times offset over length. *Change:* a long hang (the scene's hanger is 340 mm along the exit line; the length is illustrative). *Leaves:* unmeasured.

**3b. The cable eats the move.** *Conflict:* a stage of stiffness k on the gun side pushing against a cable of lateral stiffness k_ext delivers only k/(k + k_ext) of a commanded move: with the scene's placeholders (0.1 N/mm bending plus a hang term, a 4 N/mm stage) about 3 percent is lost and the residual force leaves a constant offset of about 0.13 mm, changing as the cable moves; a 0.5 N/mm printed flexure would lose about 19 percent. *Assumption:* the placeholders (bundle 1 kg, 100 N/m). *Change:* the fine stage under the work (nothing pulls on it), or a stage 100 times stiffer on the gun side. *Leaves:* the real cable stiffness and hysteresis.

**4. The swing-away.** *Conflict:* in `travel-04` the cables ride the swing. *Change:* the balancer's stroke and the gallows swing take it if the hang is long enough. *Leaves:* open.

## Branches and combinations

- **With travel-04, travel-01, travel-11:** every arrangement that fixes the gun (T1) or lifts it (T4) or rides the tube (T11) needs the cable carried somewhere else.
- **Combination candidate with `freedom`:** the cable as a compliant restraint whose forces are managed rather than removed.

## Unresolved problems and questions for Derek

- Weight of the umbilical + wire conduit + gas hose bundle from the grip to the first support; the force it exerts on the grip at rest in the working pose.
- Which way the cable leaves the grip base.

## Assumptions

- Grip-axis definition **[repo]**; bend radii and twist rule **[manual]**. Hanger length illustrative.

## Sourcing pointers

`sourcing/travel.md`: retractable spring balancer 1-3 kg (13), T-slot for a gallows (18).

## Scene id

`travel-08-force-path`
