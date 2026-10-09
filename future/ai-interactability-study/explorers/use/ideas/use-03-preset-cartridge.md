# use-03-preset-cartridge: the tube brings its correction

Scene: `scenes/use-03-preset-cartridge/index.html`. Origin: swarm (framing: the day of use). Maturity: deep.

## Picture it

Two teal nest collars, each carrying a tube on a height ring. One stands on the rotator under a gun that has not moved for the last several tubes. The other stands on a small plinth to the side where a digital gauge touches its rim and a digital indicator touches its side while a hand turns it. A screen says "screw 2: back off 0.85 turn, screw 3: advance 0.34 turn; ring to +0.9 mm". After two rounds the indicator trace flattens, and the whole collar is lifted across and set on the rotator's register.

## The proposal

The tube and its nest travel as one **cartridge**. Setting a tube up (seating it, centring it with the three screws, setting its height) happens at a **presetter** while the previous tube is still on the rotator, and what reaches the rotator is a tube whose seam is already where the fixed gun expects it. The gun is not re-aimed between tubes. Software's role is measurement and advice: a digital gauge reads the rim height, a digital indicator reads the runout of the working end against cartridge angle, and the advisor turns the once-per-turn part of that trace into "advance or back off screw i by so many turns". The out-of-round part of the tube cannot be corrected by any screw and is reported as the floor.

Height (the tube-length spread) is compensated in one of three ways, compared in the scene: a **height ring** under the tube, set at the presetter; a **single z axis on the gun side** (one manual or motorised axis); or not at all.

## What carries the loads, what establishes position, what is free or restrained

- **Loads:** each cartridge stands on a register (a plinth at the presetter, the turntable on the rotator) and carries its tube by the nest; the gun hangs from a fixed post and a shell clamp and is never moved between tubes. The umbilical is out of scope in this scene.
- **Position:** the nest's datum face and register locate the cartridge; the three screws on the collar locate the tube centre; the ring under the tube sets its height. The fixed gun's dot is the reference the whole cartridge is prepared to meet.
- **Free / restrained:** the tube is loose in the nest's pilot (0.20 mm radial clearance [repo]) until the screws touch it; the cartridge may sit anywhere within the register clearance on the rotator (a slider) unless the register is kinematic.
- **Driven:** nothing new (the rotator as today); in the gun-side branch, one z axis.

## What software could command, observe, and what stays manual

- **Command:** the existing rotator; in one branch, a gun-side z axis.
- **Observe:** rim height (gauge); the runout trace at the weld end against angle (indicator plus an angle source: the hand-turned cartridge with an encoder, or the presetter spindle); cartridge ID (a printed pattern read by a camera at each station, so the station loads that cartridge's record: ring setting, screw turns, indicated TIR); cartridge seated (contacts); the dot at the seam on the rotator, as in the other scenes.
- **Not observable here:** plate face TIR (only exists after the plate is seated and tacked, on the station); how well the cartridge sat on the register.
- **Manual:** loading the tube, turning the screws, setting the ring, carrying the cartridge, seating and tacking the plate. **Software advises; a hand moves.**

## What was tried to break it

1. **A threaded height ring tilts the tube.** *Conflict:* a thread with 0.1 mm of clearance over 40 mm of engagement tips the tube by 2.5 mrad; over the 146 mm to the weld that is 0.36 mm at the rim, more than the whole 0.25 mm radial allowance [repo] (`calc/preset_budget.mjs`). *Assumption:* height can be set by a fine-pitch ring for free. *Change:* flat, parallel rings (printed or stacked shims). Their parallelism error d goes 1:1 into face TIR (0.97 d against the 0.30 mm allowance) and 1.15:1 into radial eccentricity at the weld end (2.3 d radial TIR if left alone, but the screws remove it when indicating is done with the ring in place). Ring tilt matters as much as the tube's fit. *Leaves:* nobody has measured a printed ring's parallelism.
2. **The register adds runout after the indicating is finished.** *Conflict:* a cartridge that can sit anywhere within its register clearance c adds up to c to the radial TIR on the rotator. *Assumption:* the presetter's answer transfers intact. *Change:* keep the register clearance in the low hundredths (three balls in three grooves and magnets, not a sliding fit) or verify on the rotator with a quick indicator pass. *Leaves:* what a printed register achieves, and whether a just-welded, hot tube damages a printed nest.
3. **The tube's own out-of-roundness.** *Conflict:* `calc/screw_advisor.mjs`: with a hand accurate to 15 degrees of a turn the advisor converges to a 0.20 mm TIR in one to three rounds unless the tube's out-of-round part o is large (TIR floor is about 2 o; at o = 0.10 mm it never reaches 0.20). A hand accurate to only 60 degrees needs seven rounds on average and leaves a third of runs unconverged at o = 0.08. *Assumption:* centring can always meet the limit. *Change:* the scene reports the floor separately; an out-of-round tube needs a different criterion or a rejected tube. *Leaves:* the real ovality of 0.065 in wall, 5 in OD tube is unknown.
4. **Does presetting save the person any time?** *Conflict:* the second cartridge is prepared by the same person; time moves off the station, not off the hand. The lane scene's readout adds the presetter's load and indicate time back in and the total is about the same. *Assumption:* parallelism means less work. *Change:* what shortens hand time is the advisor (fewer rounds), a seat (no aiming), or a pool of tubes prepared in a batch while nothing else needs hands. Station occupancy does fall; whether that matters depends on whether the station or the person is the bottleneck. *Leaves:* real durations (Derek).
5. **Height by ring or by a gun-side axis.** *Conflict:* both remove the tube-length spread from the dot, and each introduces something: the ring a printed part per tube and a parallelism risk; the axis one actuator and a measurement handover. *Change:* both are in the scene as a radio control (the third option, doing nothing, shows what the spread does to the dot). *Leaves:* the actual spread (see below): if a tube's length varies by only a few tenths of a millimetre, neither is needed.

## Branches and combinations

- **Gun-side z axis** (branch in the scene): a single purple slide under the gun mount moves the gun by the measured length deviation, quantised.
- **Rim-referenced datum:** locating the tube by its rim instead of its far end would remove the tube-length spread without a ring; not drawn here. Another explorer has a scene named `datum-03-rim-crown`; I know it only by its directory name and have not read it.
- Combines with `use-02-swing-head` (the day column "Preset cartridge + swing head" in `use-01-day-lanes`): a head that seats and a cartridge that is pre-set together remove aiming and centring from the station.
- Compare: `use-06-coach-loop` (aiming by a hand on the gun side, with no pre-normalised seam).

## Unresolved problems and questions for Derek

- **Spread of tube length and plate seat depth: unknown.** The slider covers plus or minus 2 mm; a common cut tolerance of 1/16 in is only an assumption, unchecked. Measure ten tubes with the calipers.
- How long indicating takes now and how often it takes more than one attempt (this decides whether any of this is worth a second stand).
- Whether the digital gauge and indicator can be read from software: the sub-$100 Prime indicators list an LCD only; the caliper-style clock/data route and a Mitutoyo Digimatic cable route are described in `sourcing/use.md`.
- **Wave 2: the verify pass belongs with the copper shoe engaged.** The written sequence (guide 46) indicates first and only later engages the ground shoe. If the shoe's sideways drag moves the tube in the nest, both the presetter's indicating and the station's register check are shoe-off readings. Ask Derek to read the indicator at the weld circle with the shoe engaged and disengaged. Drawn as a term in `scenes/use-17-driven-presetter` (with travel-06's driver, borrowed).
- Whether a printed nest survives the heat from a just-welded tube (nobody has measured how hot the nest gets).

## Assumptions

- **[repo]** accepted runout 0.25 mm radial and 0.30 mm face TIR at the working end; nest pilot 0.20 mm and OD guide 0.40 mm radial clearance; three M3 adjusters; 0.0005 in test indicator on a magnetic base; the replaceable 150 mm nest.
- **[derived]** seam 146.05 mm above the tube bottom; ring tilt arithmetic (face 0.97 d, radial 1.15 d); M3 x 0.5 screw tip movement 0.0014 mm per degree.
- **[unknown]** tube length spread, out-of-roundness, printed ring and register accuracy.
- Illustrative: the ring range, hand accuracy, register clearance, the presetter layout, the exaggeration.

## Sourcing pointers

`sourcing/use.md`: Neoteck 0.001 mm digital indicator, Neoteck 1 inch indicator, the Mitutoyo Digimatic data cable and the note about Digimatic-port indicators, a 150 mm 5 micron linear scale kit, AS5600 encoder modules, the SPC and caliper protocols on GitHub (unchecked), UVC camera.

Scene id: `use-03-preset-cartridge`. Numbers: `explorers/use/calc/preset_budget.mjs`, `screw_advisor.mjs`.
