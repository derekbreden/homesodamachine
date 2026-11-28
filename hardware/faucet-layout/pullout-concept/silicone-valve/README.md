# Silicone diaphragm head valve

This concept shuts off soda at the face of the Sculpted pull-out tip. The only made parts the
soda touches are two silicone parts; every printed part stays dry. It takes the machined acetal
valve's place in the grip, on the same soda tube lane, with the same bought solenoid.

[Installed](https://homesodamachine.com/parts#step:faucet-layout%2Fpullout-concept%2Fsilicone-valve%2Finstalled.step) · [Grip cutaway](https://homesodamachine.com/parts#step:faucet-layout%2Fpullout-concept%2Fsilicone-valve%2Finstalled-cutaway.step) · [Valve](https://homesodamachine.com/parts#step:faucet-layout%2Fpullout-concept%2Fsilicone-valve%2Fassembly.step) · [Exploded](https://homesodamachine.com/parts#step:faucet-layout%2Fpullout-concept%2Fsilicone-valve%2Fexploded.step)

## Wet parts

The silicone body carries the tube socket, the supply port with its seat lip, the ring chamber,
three outlet holes and the spout. The diaphragm is a flat silicone disc with a thick centre boss,
a thin web and a clamped rim. Either can be cast in platinum silicone in an SLA-printed mold or
printed in Silicone 40A. A tube shop bends and beads the stainless soda tube and laser-welds it
into a turned stainless hose barb; the hose crimps onto the barb.

[Wet path, open](https://homesodamachine.com/parts#step:faucet-layout%2Fpullout-concept%2Fsilicone-valve%2Fwet-path.step)

## Dry parts

The PET-GF front housing boxes the silicone in and holds the spout through the grip face with a
stainless washer and circlip. The PET-GF rear carrier clamps the diaphragm rim against the body,
stops the pusher, seats the return spring, catches the tube's bead and cups the Ledex 195200-237
solenoid. Two M2 thread-forming screws join the carrier to the housing. The PET-GF pusher is pinned
to the solenoid plunger.

## Opening and closing

Supply water comes up the centre port and presses on the diaphragm boss over the port's area
only. With the power off, the spring holds the boss on the lip. The solenoid pulls the pusher back;
the supply lifts the boss, and water crosses the lip into the ring chamber, runs forward through
the three holes and leaves through the spout. When the solenoid lets go, the spring presses the
boss back onto the lip.

[Closed section](https://homesodamachine.com/parts#step:faucet-layout%2Fpullout-concept%2Fsilicone-valve%2Fsection-closed.step) · [Open section](https://homesodamachine.com/parts#step:faucet-layout%2Fpullout-concept%2Fsilicone-valve%2Fsection-open.step)

The sandbox example `faucet-silicone-valve` generates the views. It prints the spring load, the
pressure the valve holds closed, the pull the solenoid needs against its data sheet, and an
estimate of the pressure lost across the valve at 2 L/min.

## Open questions

Nothing here is made or tested. Formlabs does not publish how Silicone 40A cures, so the
[wetted-surface test](/hardware/printed-parts/cold-core/reservoir/wetted-surface-test.md) of a
printed part also looks for what its cure and wash leave behind. The diaphragm's own stiffness,
its set after long closed periods, the boss's release after standing closed, the solenoid's
holding force in the warm grip and the flow lost across the small port need measurement.
