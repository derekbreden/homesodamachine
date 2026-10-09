# use-05-gates: what software may do alone

Scene: `scenes/use-05-gates/index.html`. Origin: swarm. Maturity: rough. A lens over the swing-head sequence (arrangement A8 in the notebook): the day as a state machine whose transitions have owners.

## Picture it

Twelve boxes snake from PARKED to RETRACTED and back to PARKED, with arrows numbered 1 to 12. Amber arrows need a hand, purple ones can be done by software. Five dashed red boxes underneath are hold states. Click an arrow and a log says whether the machine went or why it refused; flip a sensor and the machine falls into a hold. A three-way policy switch decides which purple arrows may fire with nobody at the bench.

## The proposal

Make attended versus unattended a **policy you can flip**, not an assumption, and make **software's power over the laser a veto, never a command**. A hand fires the laser in every policy; software can move the head and the table, watch the dot and the work lead, and open an inhibit. Policy A: nothing runs without a person. Policy B: head and table may move unattended with the laser physically disabled. Policy C: also red-dot dry laps unattended. In every policy, emission needs a person, closed hardware (key, e-stop released, work clip [manual pp.19, 39]) and a hand on the trigger, and the hardware chain must be open while nobody is at the bench.

Faults are states: a work-lead continuity blink, a lost seat, a dot outside the window, a wire fused into the bead, a person or e-stop absent. Each goes to a hold that only a hand clears, and the laser is inhibited.

## What carries the loads, what establishes position, what is free or restrained

Not a mechanism. Owners: hand (amber), software (purple), hardware chain (closed by a person only). The pedal deadman never commands the laser [repo]; this keeps that rule.

## What software could command, observe, and what stays manual

- **Command:** head swing and plunge (proposed), the existing rotator. Never the laser.
- **Observe (the guards):** indicator TIR under the limit [repo 0.25 mm]; seat contacts closed; work-lead continuity without a blink through the dry lap [repo]; dot inside a window (camera); retract switch reached in time.
- **Veto:** a series contact or inhibit that software can open but not close.
- **Manual:** loading, screws, plate, closing the key/e-stop/clip chain, trigger and pedal, clearing any hold, snipping.

## What was tried to break it

1. **"Software runs everything unattended."** *Conflict:* emission is guarded by goggles, a key, an e-stop and a clip [manual pp.13, 19, 39], and argon at 15 to 20 L/min is an asphyxiation risk [manual p.19]. *Assumption:* automation removes the need for a person. *Change:* attended is a precondition of every emitting transition in every policy.
2. **"A dry lap is harmless, so it can run alone."** *Conflict:* the red dot is 0.3 mW at 630 to 670 nm [manual p.12], but the rotator is a moving mass with a belt and the head is a moving mass over the tube. *Change:* policy is a toggle: B does not allow red-dot laps alone, C does. *Leaves:* the classification of the red dot and what the manual requires for it, which it does not say.
3. **Does the red dot work with the interlock open?** *Conflict:* unattended runs require the hardware chain open, but the red reference light's dependency on the chain is not documented [unknown]. The manual lists a "light switch" separate from the "process switch" on the gun (p.17) and a "light gate open light" option (p.22). *Assumption:* the dot can be on with emission disabled. *Change:* stated as an assumption on the card and in the question list. *Leaves:* one question for Derek at the machine: does the red dot stay on with the key out?
4. **Where can software's veto attach?** *Conflict:* the manual says the DB25 port is "for PLC integration by customers" with no pin list, and RS232 is for "PC-based supervisory software" (p.16), with no protocol given; an external e-stop and the interlock clip exist (pp.19, 39). *Assumption:* a veto exists. *Change:* none possible from documents; it is written as a question for Derek and the vendor, and the scene does not depend on it being answered a particular way (an inhibit could equally be a contact in the work-lead loop, or nothing at all: then policy A and a human veto remain).
5. **The hold list is a first guess.** *Change:* five holds cover the faults the repo and manual name; a real list should come from watching the sequence run.

## Branches and combinations

- Sits over `use-02-swing-head` (the head's states) and `use-03-preset-cartridge` (the indicator guard). Feeds `use-07-two-stations` (whether a dry lap may overlap another tube's preparation).
- Pairs with `use-08-flight-recorder`: the recorder is the observation half; gates are the decision half.

## Unresolved problems and questions for Derek

- Should an AI ever run red-dot laps with nobody at the bench? (Policy C.)
- Does the red dot stay on with the key out? Does the X1 Pro offer an input that can inhibit emission, and would using it be acceptable to the vendor?
- Which faults have actually happened at the bench.

## Assumptions

- **[repo]** the per-weld sequence; continuity blink fails setup; TIR limit; pedal deadman; guarding and argon controls.
- **[manual]** interlock clip and chain (pp.19, 39); red dot 0.3 mW 630 to 670 nm (p.12); RS232 and DB25 undocumented (p.16); argon flow 15 to 20 L/min (p.19).
- **Agent proposals, not repo, not measured:** the three policies, the hold states, which transitions count as motion, the dot-in-window gate.

## Sourcing pointers

None.

Scene id: `use-05-gates`.
