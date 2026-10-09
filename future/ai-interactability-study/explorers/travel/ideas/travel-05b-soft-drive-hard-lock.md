# travel-05b-soft-drive-hard-lock: a spring as a gear, a clamp as the precision

Branch of `travel-05-lever-map`, and a reading of Derek's suspension example (bungees holding an axis "steadyish").

**Picture it.** A motor moves an anchor. Between the anchor and the gun is a soft spring, and a second spring runs from the gun to the frame. Move the anchor 10 mm and the gun moves 2 mm: the springs are a gearbox with no teeth. When the gun is where it should be, a clamp on its guide closes and the springs stop mattering: the cable's pull now meets a stiff mount.

Scene: `scenes/travel-05b-soft-drive-hard-lock` (one axis, exaggerated).

## The proposal

Derek's rings-and-bungees example asks whether "precision has to come from the support continuously". One answer in his own list is to *temporarily constrain it*. Read as a mechanism: **position by compliance during setup and trim, precision by a clamp during the weld.** The soft link is a reduction, r = k1/(k1 + k2), that makes the anchor's step count fine; the clamp turns a floppy suspension into a rigid one when it matters.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** unlocked: the guide carries the weight; the springs carry horizontal loads. Locked: the clamp carries the horizontal disturbance.
- **Establishes position:** the anchor count (through the springs) while unlocked; the clamp at the position where it closed.
- **Free / restrained / driven:** free on the guide while unlocked (sliding within a friction dead band); restrained by the clamp; driven only through the springs.

## What software could command, observe, what stays manual

- **Commands:** anchor position and step; clamp open/closed.
- **Observes:** anchor step count and clamp state only. **The gun position is not observed**; the dead band is exactly the gap between what the count says and where the gun is. A camera on the dot or a small scale on the guide would close it.
- **Manual:** choosing springs, cleaning the guide.

## What was tried to break it

**1. Friction.** *Conflict:* a guide with 1 N of friction and springs of 0.5 N/mm in total has a dead band of +-2 mm: the reduction's resolution is worthless. *Assumption:* Coulomb friction of that size (placeholder). *Change:* a low-friction guide (flexure, air, precision rail with light preload), stiffer springs with a bigger anchor stroke, or a dither. *Leaves:* real friction unmeasured.

**2. The disturbance.** *Conflict:* unlocked, 1 N of cable pull moves the gun 2 mm. *Change:* lock before the weld: with a 50 N/mm clamp (placeholder) the same pull is 20 microns. *Leaves:* the clamp's slip, creep, and the shift as it closes: none of these is seen by the software.

**3. No feedback.** *Conflict:* the anchor count is not the gun position. *Change:* a camera on the dot (as in `travel-01`) or a scale on the guide. *Leaves:* observation is again the missing half.

**Wave 3 entries, from use's exchange (`exchange/use--on--travel-w2.md` section 2), answered in `exchange/travel--reply-to-use-w3.md`. Numbers re-run in `calc/13-clamp-relock.mjs` (2000 closures, use's model).**

**4. The clamp is the last handover and nothing looked after it (use).** *Conflict:* the order was soft drive, camera trim through the springs, clamp, weld: the camera's last look came before the clamp, so the size of the clamp's shift is the size of the error. Re-run: 81 % of closures end inside a +-0.10 mm window with no look after the clamp, 95 % with one look-unlock-trim-relock loop (closing scatter 0.05 mm, camera 0.05 mm, hand +-1 mm). *Assumption behind it:* a clamp is a reduction of compliance and its closing is a footnote. *What the change alters:* the scene now has the closing shift (mean and scatter), the look-unlock-trim-relock loop as a button, and the share of 2000 closures inside the window with and without the loop; the state machine around a soft drive gains a relock loop and a bias table. `travel-14-exact-crown`'s lock had the same missing shift and is fixed the same way. *What it leaves uncertain:* the real size and mean of the shift; nothing observes the gun between the last look and the weld.

**5. Friction costs rounds, not accuracy (use).** *Conflict:* my break 1 read a +-2 mm dead band as a lost reduction. Re-run: the loop winds the anchor until the gun breaks out and lands on the band's edge; the median first trim takes 3 rounds at 0.15 N of friction (2 at 0.02 N), 11 % of closures hit the six-round limit at 0.15 N, 23 % at 0.5 N, 43 % at 1 N. *Assumption behind it:* the dead band is a resolution floor. *What the change alters:* the reduction still works, each round costs a look. *What it leaves uncertain:* real friction.

**6. A mean can be learned, a scatter cannot; which clamp to build first (use).** *Conflict:* a clamp that always pushes the same way (mean 0.08 mm) ends 49 % inside the window with no look after the clamp and 82 % with one. *Assumption behind it:* every closing shift is a scatter. *What the change alters, and the answer to use's question (wedge or pinch):* a wedge or cam onto a known side is a bias the AI can learn from logged closures: with mean 0.08 and scatter 0.01 it ends 48 % with no look, 91 % once the mean is learned and removed, 97 % with a look as well; a pinching clamp of scatter 0.05 ends 81 % and 95 %. I would build the wedge, and measure first: an indicator on the shell while a clamp or magic-arm knob closes says in ten minutes which kind it is. *What it leaves uncertain:* whether real clamps have a stable mean.

**7. Derek's bungees fail at the weld once the arm lets go (use, from `use-14-handover-shift` arrangement C).** *Conflict:* released, the rings shed the arm's force 0.77 mm RMS, and a soft spring cannot be nulled better than force noise over stiffness (0.05 N over 0.15 N/mm is 0.33 mm); 1 N moves a 0.15 N/mm support 6.7 mm. *Assumption behind it:* suspension carries and holds. *What the change alters:* nothing in this scene except stating it: the rings carry and hold a neighbourhood; the last stiff element at the weld has to be this scene's clamp or a seat (`travel-04`). `use-14` (theirs) stays the reference for the numbers. *What it leaves uncertain:* the rings' real stiffness.

## Branches and combinations

- **With `travel-04`:** the seat is a *hard* return; this is a *soft* trim followed by a lock: the two can be stacked (soft-drive to a neighbourhood, lock, then rely on the seat when swinging).
- **With `travel-08-cable-travel`:** the cable is the second spring and the disturbance; a balancer removes the disturbance.
- **A wedge onto a stop is a fine stage (wave 3).** A clamp that pushes onto a known datum is a seat; a wedge onto a stepper-driven stop with a preload is an ordinary preloaded fine stage, and the soft gear is what remains when no stop is wanted. `use-14-handover-shift` draws the four arrangements.
- **With `freedom`:** the framing that owns free/restrained is the natural partner; a suspension row could take a "clamp closes in the weld" cell in the allocation matrix.

## Unresolved problems and questions for Derek

- How much friction do his printed guides or rails have; how far does a bungee-hung gun creep?
- Whether he would accept a clamp that closes during the weld and moves the gun a few microns as it closes.
- **Wave 3, question for Derek (from use's exchange):** put the indicator on the gun's shell, tighten a clamp or a magic-arm knob, and read the dot's shift: a push to one side (a wedge, learnable) or a pinch (scatter)? Ten minutes, and it says which clamp to build first.

## Assumptions

- Linear springs, Coulomb friction, linear clamp stiffness; all values on the sliders are **illustrative**.

## Sourcing pointers

`sourcing/travel.md`: MGN12 rail and carriage (5) as a low-friction guide; nothing sourced for springs or clamps.

## Scene id

`travel-05b-soft-drive-hard-lock`
