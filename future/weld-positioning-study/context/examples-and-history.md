# Derek's examples, and what earlier conversations explored

Companion to `shared-context.md`. Four explorers read this from the start; the
other four receive it after their first pass. These examples are starting
points for branching — not finalists, requirements, or the boundaries of the
search.

## Two examples from "Repeat"

Derek, explaining why he had trouble articulating the breadth he sees:

> I have so many ideas that seem stupid at first glance. And so it takes some not insignificant thinking on my part to filter through and think through things at least enough to suggest a defensible version of each idea, because if I don't the conversation turns into a defense where I have to dig in and help solve every problem that is pointed out with my "stupid idea". And maybe by the end of it we end up with something so different that it's unrecognizable from what I originally suggested. But that wasn't really my point, my point was there's a lot of possibilities here. Even within the narrow range of the very specific (and most critical) problem of positioning the gun itself in xyz (forgetting aim for a moment), we have stupid ideas such as:
>
> - arms designed to hold monitors in a position on a desk
> - cutting a hole in a table, mounting the existing welding rotary table in some fashion under that hole

He was illustrating how much room there is even within positioning the gun.

## How the table example developed ("Repeat 2")

Derek on why he likes it:

> I think it does reduce the range of the XYZ problem, it reduces the distance we have to travel in any given X or Y or Z with the gun from our constructed starting point to our fine tuned gun position. It doesn't really totally solve the XYZ problem at all. We still have the entire problem, but it does shrink it, I think.

> What I'm imagining is something screwed into the bottom of the table, maybe metal, maybe motorized, maybe manually height adjusted, and there is at least an opening on one side/face of this "upside down box" for loading/unloading the carbonator tube. I'm imagining something above the hole that moves the gun in X and Y.

When an agent drew a one-sided support:

> if you're going to have just one wall (or tube? square tube?) supporting the adjustable shelf and you're going to mount the gun above precisely where that wall (or whatever) is mounted, we might as well just do all this on the edge of the table instead of a hole in the table, right?
>
> I was imagining 4 rods (or walls or arms or braces or whatever holding each corner of the adjustable shelf. I think my imagination goes there because it seems easier to me to be rigid/stable/consistent, but maybe that's not really true.
>
> I was imagining the gun riding a gantry, the entire gantry sliding in one XY axis on rails on both sides of the hole, and the gun sliding along the gantry in the other XY axis.

> The gantry I imagined was at countertop height. The gun tip is at countertop height. The majority of the gun that is not the tip is enclosed in a custom printed shell, so it is not really "gripped by the base" nor "gripped just above the tip", but is instead "gripped along its length". Scanning is easy. Printing custom shells is easy. This would be one of the few places in any version of "welding arm" that we actually have a lot of prior art establishing our level of expertise as being quite advanced.
>
> And the gun is not tangent to the circumference as it needs to be.
>
> I also imagined no extra shelf under the adjustable shelf.

So the branch as it stood: the rotator on a height-adjustable shelf supported
around its corners beneath the table opening; a low gantry spanning the opening
(Y on rails either side, X along the gantry); a fitted gun shell near countertop
height, gun tangent to the circle. That conversation then produced the
orientation scene and its three rotations. This is one branch; its neighbours
and entirely different arrangements are open.

## The suspension example (Derek, verbatim)

> Imagine if you will:
>
> - One of those metal rubber coated hooks on pegboard walls in garages everywhere
> - Imagine that hook being a complete (openable) loop
> - Imagine that hook hanging from a wire to be held in Z, and suspended from bungees or something stretching in either the X or Y axis, so just two bungees, holding one axis steadyish
> - Imagine one hook around the tip of the gun, and a second hook around the base of the gun (around the umbilical and wire feed)
>   - Can you see how the arm might "grip" (keeping in mind, that "grip" means a complete shell we print with whatever attachments we want to attach to our robot arm anywhere we like on that shell) this in several ways and get entirely different results?
>   - Can you see how a 3rd ring a number of places might reduce the range of motion (or increase the force needed to exercise that range) but at the same time reduce weight further?

Derek calls this broad space **suspension**. Use that word without making him
defend its classification. It includes supports that carry loads, impose
constraints, stretch, move, pivot, slide, roll, lock, or participate in
actuation. It includes different contact conditions between a loop and the gun
or shell. Do not quietly turn every loop into a rigid clamp, every suspension
point into a fixed point, or suspension into an ideal upward force that leaves
everything else unchanged.

He had to explain that example across several exchanges because each
description was interpreted too narrowly. Take apparently stupid ideas far
enough to discover their useful forms. Preserve the original idea alongside
variants that change it; do not present a replacement as what he must have
meant.

What "take it further, break it, and fix it" looks like, in his words:

> For the rings-and-bungees example, "it will sway and lack precision" is a starting observation. Continue into which motion is free, which force causes displacement, what happens at each contact, and whether the support must provide precision continuously. Explore changes in the supports, their anchors, their restraints, their relationship to the actuator, and what happens during setup versus a weld. A useful outcome could retain the compliance, control it, temporarily constrain it, or assign precision elsewhere. Those are examples of the work, not a list to be mechanically exhausted.
>
> Likewise, "a monitor arm is too flexible" needs an actual arrangement behind it. What is it carrying, what is it locating, where is the reference, and what else is supporting or driving the gun? Investigate its useful role and nearby variants. Do not require an ordinary monitor arm by itself to perform every function of the whole machine before the idea can stay in the study.

## The automated-setup vision ("Explore automated tube laser setup", Derek)

> - We have motors controlling XY in this vision
> - We have a motor controlling Z in this vision
> - We have a motor controlling the roll I just describe to an agent. We have another motor controlling the opposite axis of roll that is also relevant, the only other axis we'd want to change here.
> - We have a couple PTZ cameras controllable by software as well
> - We do this setup, and we let an AI iterate for hours or days or weeks, using the cameras and the laser dot to evaluate their work, to improve the software, to get consistent repeatable (dry run) results across multiple tubes

Manual setup and partial arrangements are useful contributions to that goal.
There is no budget.

## What "Welding arm 3" did (context, not a definition of this study)

Derek values the seriousness of that work: its agents developed mechanisms,
sourcing, load estimates, arrangements, and critiques that exposed specific
problems. Its framing — a **fixed holder** for the gun above a turning tube —
plus its rankings, finalist, exhaustive checks and commissioning plan do not
define this assignment.

It produced eight plans from four perspectives (a machine tool, a welding
positioner accessory, a printed object fitted to the gun scan, the first axis of
a future robot), each checked for physics and sourcing, then judged. The
finalist was a "trunnion tool post": a worm rotary table with its axis along the
seam through the dot, two micrometer stages for aim and focus/lift-off, an
aluminium cradle lined with scan-fitted pads, a hand lever working the trigger
through a bicycle brake cable, and a floating steel breadboard shared with the
rotator. Its numeric targets (0.1 mm dot, 0.3 mm focus, etc.) are agent
proposals, and its spending figures do not apply.

Its plans and physics/sourcing checks remain readable for mechanisms, load
estimates and sourcing leads (all agent work, dated 2026-09-25):
`/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/01e39f90-7b46-4609-9f62-a595ec33be48/scratchpad/weld-arm/`
(`BRIEF.md`, `plans/*.md`, `checks/*.md`, `final-plan.md`). Treat every number
there as an agent estimate unless it traces to the repo or the manual.
