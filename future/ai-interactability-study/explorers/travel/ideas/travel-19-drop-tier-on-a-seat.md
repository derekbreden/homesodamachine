# travel-19-drop-tier-on-a-seat: travel-01's stack after use's exchange

Origin: combination of `travel-01-tube-travels` and `use-13-work-states` (use's branch of travel-01); both originals stay. Depth: developed. Scene: `scenes/travel-19-drop-tier-on-a-seat`. Calculations: `calc/12-drop-tier-seat.mjs`.

**Picture it.** Under the rotator the stack has a new tier. On the shuttle sits a base plate with three balls and four guide columns; a drop tier rests on the balls at its top stop, is held down by a preload, and slides down to a bottom stop 40 mm below where a switch closes. On the tier ride the short fine Z, then X and Y, then the rotator. To swap, the tier drops, the switch says so, the shuttle takes the tube out; to weld, the shuttle goes in, the tier rises onto its three balls, the fine tier trims. The gun stays where it is.

## The proposal

use's exchange found that travel-01's Z was asked for three jobs: a fine trim (a few millimetres, micron steps, stiff), clearance for the shuttle (the nozzle tip is 5.0 mm above the rim in the kit's pose) and, if a bead must end with the head leaving, the escape. My own stack rule was already "long axes at the bottom with hard stops, the fine axes on top", and applied to Z it gives a **drop tier under the fine tier**: tens of millimetres, hard stops, commanded as states. Two things go beyond use's `use-13`:

1. **The interlock is a switch.** The shuttle is enabled by the tier's bottom-stop switch, so the swap is safe by construction; nothing has to measure the nozzle-to-rim clearance, which nothing does.
2. **The top stop is a three-ball seat, and its tilt is drawn.** Every return to a hard stop tilts everything above it; at r = 61.85 mm a tilt d is a once-per-turn face runout r tan(d) that no fine axis can trim. Ball scatter over ball circle, not the guides' straightness, sets it: 10 micrometres over a 150 mm ring is 0.0038 degree, 4 micrometres peak; a scissor lab jack at 0.3 degree would be 0.32 mm.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** the holder post carries gun, shell and (through the hanger) the cables; shuttle, base plate, balls, tiers and stack carry the rotator and tube.
- **Establishes position:** the shuttle's hard stop (work position) and the balls (vertical, tilt) per landing; the fine tier trims what a camera or touch says after the last approach.
- **Free / restrained / driven:** the tier is guided by four columns, located only at its stops; between them nothing locates it. Driven: shuttle, tier, fine Z, X, Y, rotator.

## What software could command, observe, what stays manual

- **Commands:** tier to its stops, shuttle (only with the tier down), fine axes, rotator; the escape (a drop by what the head must leave).
- **Observes:** four end-stop switches (tier up, tier down, shuttle in, out), step counts of the fine axes, the dot through a camera when it sees it. **Blind:** the seat's tilt (it shows only as a once-per-turn dot error in a dry lap), the nozzle clearance, a fused wire.
- **Manual:** loading, indicating, seating the plate; firing; cutting a fused wire and saying so; the escape distance.

## What was tried to break it

Each entry says it came from use's exchange; the same four are entries 6 to 9 in `travel-01`'s file, where they are answered.

1. **Z's range is bigger than the swap margin (use).** *Conflict:* 8 of the 12 mm of fine Z are shuttle-safe. *Assumption:* Z only trims. *Change:* the drop tier goes first and the bottom switch enables the shuttle; with a 40 mm drop and Z at +6 the rim clears the barrel by 39 mm. *Leaves:* the nozzle margin (kit proxy).
2. **The end of a bead has no owner (use).** *Conflict:* with the gun locked the work must drop: 20 mm along the beam is 28.1 mm of Z, 0.47 s at 60 mm/s, 3.7 mm of seam at 8 mm/s. *Assumption:* the sequence has a lift (unconfirmed). *Change:* the tier owns it; the escape slider starts at 0. *Leaves:* the tier motor's current limit as the fused-wire stop; whether there is a lift.
3. **Tilt is face runout (use).** *Conflict:* 0.05 degree is 0.054 mm peak. *Assumption:* a stop returns flat. *Change:* the seat; I accept 0.0185 degree (0.02 mm peak). *Leaves:* printed grooves, creep, the plate's sag under the rotator; each approach draws the balls again (the Landing radio).
4. **Two approaches, a fused wire (use).** *Conflict:* tack, face check, weld: in, out, in. *Change:* the last trim after the second approach; a hold state that a hand releases. *Leaves:* one approach goes only if the dial can stand opposite the gun.
5. **Own break: the preload has to beat the tier's weight shift.** *Conflict:* the tier carries the rotator, the tube, the fine stack; a magnet or spring preload that seats it must exceed the disturbance of the fine stack's motion and of the rotator's unbalance, or a ball unloads. *Assumption:* the preload is large enough. *Change:* none drawn. *Leaves:* the mass of rotator and tube together (Derek to weigh), the preload, and whether a stepper tier holds.

## Branches and combinations

- Shares its bottom-stop switch idea with `travel-04-return-seat` (three balls, contact continuity); the arm route (`travel-20`, `travel-21`) removes the shuttle and the tier altogether because the arm parks.
- With `travel-15-touch-stack`: the touch routine's stack is this stack; a tier that lands with a tilt puts that tilt into every touch.

## Unresolved problems and questions for Derek

- How do you end a bead today and how far does the head go before the wire is free? Can the dial stand opposite the gun for the face check? What do the rotator, its base and a tube weigh together?
- Nothing here measures the seat's tilt; a dry lap sees its once-per-turn vertical term.

## Assumptions

- Ball scatter, span, stroke, speeds, the 40 mm added height: **illustrative**. Beam vertical component 0.712 and the 5.0 mm tip margin: **[derived]** from the kit's proxy. r = 61.85 mm, TIR 0.30 mm: **[repo]**.

## Sourcing pointers

`sourcing/travel.md`: linear stages that could be the tier (3, 4; stroke and load only, no lift speed or holding force), the scissor jack whose tilt is illustrative (6), balls and magnets (9, 10).

## Scene id

`travel-19-drop-tier-on-a-seat`
