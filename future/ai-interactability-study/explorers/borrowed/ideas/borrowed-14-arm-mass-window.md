# borrowed-14-arm-mass-window: what the arm carries, what friction forgives, and which bought arms bracket it

Origin: branch of freedom-02-balanced-arm (Derek's monitor-arm example), drawn in wave 2 from the exchange `exchange/borrowed--on--freedom-w2.md` (section 1). Maturity: developed. Scene: `scenes/borrowed-14-arm-mass-window/index.html`.

## Picture it

The same balanced arm as freedom-02, but the payload is a stack of named parts hanging off the tip (gun and shell, the XZ vernier stage, a camera, the fibre's share, a fishing weight) and the spring is drawn as a mechanism: a coil from a point on the arm to a point above the shoulder, as in an Anglepoise lamp. Below it, a strip of bars for bought arms and balancers, each from the mass its listing rates it to the mass it stops at, and a vertical line where the total falls.

## The proposal

freedom-02 splits the job into a weight path (a balanced arm) and a location path (a vernier and a camera). Two questions about the weight path are about mass and both have a bought answer.

1. **What is the payload?** Everything on the tip, including the vernier that does the locating. With two mini linear rails and motors (0.6 kg, illustrative; the listing states no weight), a camera (0.15 kg) and a 0.35 kg fibre share the payload is 2.3 kg, not 1.5. The floor of gas-spring monitor arms (2 kg) is met by the parts, and the 0.5 kg ballast of freedom-02's repair is not needed.
2. **How exactly must the spring match it?** The arm stays put while |spring torque - payload torque| <= joint friction, so the mass mismatch it forgives is friction / (g L cos th): +-0.091 kg for freedom-02's 0.4 N.m and 0.45 m, +-0.051 kg at 0.8 m reach, +-0.45 kg at 2 N.m, +-1.8 kg with the 8 N.m of freedom-02's brake. Grams, not tenths of a kilogram.

Three springs are drawn: freedom-02's gas spring with an error slope; a spring-and-parallelogram with a *plain* coil spring; the same with a *zero-length* spring (a close-wound coil with initial tension or a spring over a pulley). With a zero-length spring the torque is k a b cos(th), exactly proportional to the payload's cos(th), so for the matched payload the balance is exact at every angle and the window is set by friction alone.

## What carries the loads, establishes position, is free, restrained or driven

- Carried: the payload by the spring and parallelogram (or gas spring); the residue by joint friction up to its limit; beyond it the arm rises or sinks until it sticks or reaches a stop.
- Position: not the arm. The vernier and the camera place the dot (freedom-02).
- Free: the arm's angle inside the friction window.
- Driven: nothing in this scene; a small shoulder motor is possible because gravity is cancelled (freedom-02 entry 6).

## Software: command, observe, manual

- Command: nothing here.
- Observe: payload, if a load cell sits in the vernier (then the mismatch in kilograms is a number, not a feeling); shoulder angle by an encoder.
- Manual: weighing the parts, choosing the arm, setting its spring within its rating, trimming with ballast in grams.

## What was tried to break it

1. **The floor is met by the parts, not by ballast.** Counting the vernier's mass the default total is 2.3 kg; with a 0.8 kg gun 1.9 kg, 0.1 kg from the floor. Assumption: the parts weigh what they weigh: unmeasured. Left standing: the tuning range of a listed arm's spring is unchecked.
2. **Friction forgives grams.** At 0.4 N.m and 0.45 m the arm forgives +-0.091 kg. The fibre's share on the arm (0.35 kg here) changing by a quarter is 0.088 kg. The vernier's own travel: moving the 1.2 kg gun 10 mm along the arm changes the shoulder torque by 0.118 N.m, 29 % of the 0.4 N.m friction band. Change: clip the fibre at a fixed place, or give it its own balancer (borrowed-11, travel-08).
3. **The spring changes where the window sits.** For a 1.5 kg payload matched: gas spring -19 to 32 deg, plain coil (40 mm free length) -20 to 29, zero-length -20 to 50 (the whole modelled travel). A payload 0.1 kg too heavy: gas 7 to 50, plain coil -20 to 2, zero-length 25 to 50. The tolerance is the same in all three; where along the travel it holds moves. A heavier payload narrows a gas spring's window: -19..32 at 1.5 kg becomes -10..21 at 2.3 kg, because the error torque scales with the payload (calc/w2-arm.cjs; the gas-spring numbers agree with freedom's calc/20-balanced-arm.js).
4. **A rating is a window on mass and says nothing else.** Rated ranges read from Prime listings observed 2026-09-28/29: RODE PSA1+ 0.25 to 1.2 kg ($112, 2,701 ratings, "1K+ bought"), InnoGear scissor boom 1.5 kg ($19.99, 24,099 ratings, "2K+ bought"), Elgato Wave Mic Arm Pro (gas spring) 3 kg ($179.99), HUANUO monitor arm 2 to 9 kg ($35.99, 16,507 ratings), Tigon balancer 0.5 to 1.5 kg ($39.00). A rating says nothing about balance error, friction, reach or tip stiffness.

## Branches and combinations

- With borrowed-13: a hexapod as the location path weighs about six rails and motors and fills the monitor arm's payload floor.
- With borrowed-15: a sled's keel is a mass that fills the floor and sets a gravity spring.
- With freedom-14/freedom-06: a brake at each joint is freedom-06; a friction budget in grams is this scene's number for it.

## Unresolved problems and questions that need Derek

- Weigh the gun in its shell, the vernier with its motors and the camera; a kitchen scale to 25 g.
- Push the tip of a monitor arm or a mic boom with the EISCO Newton meter at 0.5, 1 and 2 N, note how far it gives and whether it stays: friction and pre-sliding.
- Hang a dummy load of the payload's mass on a borrowed arm: at which angles does it stay put? (freedom-02's own question.)

## Assumptions

- Illustrative: gun and shell 1.2 kg, vernier 0.6 kg, camera 0.15 kg, fibre share 0.35 kg (freedom-02), reach 0.45 m, friction 0.4 N.m (freedom-02), gas-spring error slope 0.15 per rad, spring geometry a = 180 mm and b = 120 mm above the shoulder. One joint in a vertical plane.
- The coil-spring balance is the standard one: torque = k a b cos(th) (1 - l0 / l), l^2 = a^2 + b^2 - 2 a b sin(th).
- Rated ranges, prices, ratings and delivery are from the listings in sourcing/borrowed.md (Prime). The Anglepoise principle was checked against a search result summarising the physics of zero-free-length spring balancing: unchecked against a primary source.

## Sourcing pointers

sourcing/borrowed.md wave 2 (RODE PSA1+, InnoGear, Elgato Wave Mic Arm Pro, FIFINE CS1, Tigon balancer); sourcing/freedom.md (HUANUO, Amazon Basics, mini linear rail).

## Scene

`borrowed-14-arm-mass-window`
