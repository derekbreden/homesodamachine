# freedom-14: hand plus guidance (the hand supplies the motion, software supplies a force it can always overrule)

Scene: `scenes/freedom-14-hand-plus-guidance`. Origin: swarm (the thin region "the hand supplies motion while software supplies resistance or guidance", from the digest; uses freedom-01c's soft element as a force source). Depth: rough (statics that do not depend on a hand, plus a simulation with a made-up hand). Every hand number is **illustrative**; nothing about Derek's hand has been measured.

## Picture it

The gun is held by a hand on a passive support that carries the weight (a balancer or the arm of freedom-02), as it is today. On the radial axis a bungee runs from the gun to a small stage; a motor moves the stage's far end. The force on the gun is the bungee's stiffness times its stretch, so software can add a push or a pull of a fraction of a newton to what the hand is doing, and cannot do more than the stroke or a cap allows. A hand that decides to hold still pushes through it. A damper on the support, adjustable, resists fast motions.

## The proposal

Every other arrangement in the study gives software a position to command, and a position command overrules the hand. Give software a **force** instead, in parallel with the hand. Three helps:

- **Centring:** a pull proportional to the eye's error, toward the seam.
- **Wall:** no force inside a band, a push back outside it: silent while the hand is good enough.
- **Damper:** resistance to fast motions, a mechanical low-pass that takes tremor and leaves drift to the hand and the guide.

The arithmetic that does not depend on a hand model: a guide spring K<sub>g</sub> moved through a stroke S, in parallel with a hand of stiffness K<sub>h</sub>, moves the gun by at most K<sub>g</sub>S/(K<sub>h</sub> + K<sub>g</sub>) and never with more than the cap. 0.15 N/mm and 20 mm of stroke is 3 N, a 2 N cap, and against a hand that yields 2 mm per newton (0.5 N/mm) 3.1 mm; 0.2 N moves it 0.3 mm and costs 1.3 mm of bungee stretch. A tense hand (3 N/mm) cuts each figure by about six.

## What carries loads, what establishes position, what is free or restrained

- **Load:** the passive support carries the weight; the hand and the guiding bungee push on top; the umbilical pulls as it does.
- **Position:** the hand, as today; the seam as the eye sees it (the guide's error input).
- **Free:** the hand's motion, everywhere except through the guide's force.
- **Restrained:** softly, by the guide (spring, bounded) and the damper.
- **Driven:** the anchor of the bungee (a motor) and the damper setting; not the gun.

## What software could command, observe, and what stays manual

- **Command:** the anchor position (force = K<sub>g</sub> × stretch), the damper setting, the band width.
- **Observe:** the eye's corner minus dot; the anchor position; optionally a load cell in the bungee.
- **Manual:** the hand holds the gun, watches the dot and pulls the trigger. The operator decides whether to accept a gun that pushes.

## What was tried to break it

**Entry 1. A force moves a relaxed hand only a little.**
- Conflict: 3 N at the extreme of the stroke moves a relaxed hand 3 mm; 0.2 N moves it 0.3 mm; a tense hand six times less.
- Assumption: software should correct the gun's position.
- Change: give software the job of drift (slow), which a fraction of a newton can do, and leave the hand the rest.
- Leaves uncertain: the hand's stiffness at the grip in the working pose (no measurement), and whether it stiffens when it feels a push.

**Entry 2. Two loops on one error.**
- Conflict: the hand already steers by eye (with a delay); a proportional guide adds a second loop with its own delay (the eye's 0.25 s). Asked for 2 N/mm it chatters.
- Change: keep the guide soft and slow, or use the wall (silent inside the band). In the made-up hand of the scene (0.17 mm rms alone) centring gives 0.13 mm, the wall 0.15, the damper 0.16, centring with the damper 0.13, with peak guide forces of 0.1 to 0.2 N.
- Leaves uncertain: everything about a real hand. The order of the helps moves less than the numbers.

**Entry 3. The eye's bias becomes a push.**
- Conflict: a centring pull toward where the eye thinks the seam is holds the gun there; the loop cannot see its own bias (eyes-01).
- Change: prefer the wall; centre only with a bias check (eyes-07, the touch of freedom-12).
- Leaves uncertain: how large a bias a hand would fight.

**Entry 4. A damper is not a corrector.**
- Conflict: it slows what is fast and nothing else; too much slows the hand's own corrections. The corner frequency is K/(2πc): about 2 Hz at 0.05 N·s/mm with K 0.65 N/mm, against a 10 Hz tremor.
- Change: it is the one help that needs no eye and no software. A hand on a rest may already provide it.
- Leaves uncertain: whether a printed damper, an air dashpot or an adjustable damper is worth having.

**Entry 5 (wave 3, from borrowed's exchange, section 5). The damper is a rotary part and the listings give no number. Decision: revised (scene readouts and a lever slider).**
- Conflict: the scene's damper is 0.05 N·s/mm at the grip (a corner near 2 Hz against a 10 Hz tremor). The bought damper is a video fluid head (V504 $56.99, 5 kg; SIRUI VA-5 $99; heads $230 to $265), which acts on translation at the dot through a lever: c at the dot = c rotary / lever². 0.05 N·s/mm at a 202 mm lever is 2.0 N·m·s/rad; at the nose seat's 70 mm it is 0.25; and a head sized to critically damp freedom-08's pendulum (0.13 N·m·s/rad) gives only 0.003 N·s/mm at the dot, a corner near 30 Hz, no filter at all for tremor. The listings give drag steps, not values.
- Assumption: the damper is a free parameter set by the corner frequency.
- Change: the design variable is the lever, not the damping. The scene has a lever slider and two readouts (the rotary value that a chosen dot-space damping needs; what a 0.13 N·m·s/rad head gives at the dot). A spring scale on a fluid head's handle at walking pace, smallest and largest step, measures the drag.
- Leaves uncertain: the drag of a real head; whether one pivot can supply weight (freedom-02), stiffness (freedom-08) and damping.

**Entry 6 (wave 3, from borrowed's exchange, section 5). The same help on a handle: `borrowed-19-haptic-jog`. Decision: answered and kept as two arrangements; the question answered.**
- Conflict: two loops on one error and the eye's bias becoming a push (entries 2 and 3) both come from putting the force on the gun. A brushless gimbal motor with a magnetic encoder and field-oriented control renders a detent every 0.05 mm, a wall past the eye's seam and a capped soft pull on a knob, at $34.88 for a kit, and never touches the gun.
- Assumption: help has to act on the gun to help the hand.
- Change: borrowed asked whether the help should go on the gun, at the same pivot as freedom-08's gravity spring, or on the handle. Answer: on the handle whenever the gun is on a stage (the vernier of freedom-02, freedom-05 or freedom-13): the hand supplies the motion, software supplies the feel, and the motor's torque limit is a physical cap. On the gun only when the hand holds the gun itself and there is no stage: then a bounded bungee force and a rotary damper on the passive support are the only help available, and the guide's authority statics of this file are what is robust. The two stay as separate arrangements; the knob is borrowed's scene.
- Leaves uncertain: whether feel helps a hand at all (needs a printed knob and an afternoon); the motor's cogging against the detents.

**Entry 7 (wave 3, from borrowed's exchange, section 5, second branch). Assist from the hand's own force. Decision: answered (a note).** An e-bike torque sensor or a cobot's hand guiding gives assist proportional to the force on the handle, never a push unless the hand pushes: a load cell in the grip and a stage that moves by an admittance (mm/s per newton, low-passed). A load cell in the grip reads everything that pushes on the gun, the fibre's pull included, so an admittance stage would follow the fibre unless the cell sits between the hand and the gun only; freedom-16's routes say how large that pull is and at what lever. It changes the arrangement (software now moves the stage), so it is a branch, not drawn.

## Branches and combinations

- **freedom-01c:** the soft element as a force source; the hand is the position master, software the force.
- **use-05 (gates):** a force cap is a gate that is physical rather than logical: the hand is always the last word.
- **use-06 (coach loop):** the coach tells the hand which knob; this puts a bounded push on the gun itself.
- **borrowed-09 (hand controller):** the hand as leader; this keeps the hand as the follower's only motion source.

## Unresolved problems, and questions that need Derek's observation

- How far does your relaxed hand yield per newton at the grip, at the working pose? (Push on the gun with the EISCO Newton force meter and read how far it moves, with the gun held on its rest.)
- How large is the drift and tremor of the gun in your hand over a lap? (Phone video with a scale beside the dot.)
- Would you accept a gun that pushes back with 0.2 N, if you could always push through it?

## Assumptions

- Hand stiffness 0.5 N/mm, drift 0.08 mm/s, tremor 0.06 mm at 10 Hz, visual correction gain 0.2 per second with 0.2 s delay and 0.1 mm visual resolution: **illustrative** (chosen so that the hand alone is about 0.17 mm rms). Runout 0.125 mm amplitude once per revolution [repo, acceptance not measurement]. Guide: bungee 0.15 N/mm, stroke 20 mm, cap 2 N, wall band 0.1 mm, eye 4 Hz with 0.03 mm noise.

## Sourcing pointers

`sourcing/freedom.md` wave 2: the EISCO Newton force meter. No voice coil or adjustable damper was searched; a stepper or servo with a spring stands in for the force source.

## Scene

`freedom-14-hand-plus-guidance`. Related, not mine: `borrowed-19-haptic-jog` (entry 6).
