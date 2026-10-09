# datum-14-who-owns-the-wobble: the seam map has four owners with different lifetimes

Scene: `scenes/datum-14-who-owns-the-wobble/index.html`. Depth: developed. Origin: branch of `trials-04-seam-map-replay`, combining `datum-02-seam-signature` and `datum-07-touch-off`. Calc: `calc/owners_model.js` (the scene's model, run in node), `calc/map_owners.py` (a first version). Exchange: `exchange/datum--on--trials-w2.md` section 1.

## Picture it

The wobble of the seam at the station, over one turn, drawn as four curves that add: a slate one the rotator owns (printed race, sorted balls, belt), an amber one the way this tube stands in its nest owns, a teal one the tube and plate own, and a pink one that is not the seam at all but what the camera judge gets wrong on this tube. Software sees only their sum, as a map learned by turning the tube. Press an event (a puck lifted and put back, a tube re-seated, turned in its nest, the rotator re-clamped, a tack, a new tube) and the hidden pieces move; the scene shows what one judge lap can tell about it, what replaying the stale map leaves, what a relearn through the judge leaves, and what rebuilding only the moved piece from a few touches leaves.

## The proposal

`trials-04` learns a seam map keyed to the rotator angle. The map is one curve, but it has parts that live for different times:

- **Rig** (rotator error motion at the station): the same for every tube; changes when the rotator is re-clamped or its belt or race is touched.
- **Seat** (tube axis against turntable axis: eccentricity and lean, a first harmonic only): changes at every re-seat of the tube in the nest; changes little when a puck is lifted and put back on its kinematic seats (`trials-01`).
- **Work** (plate offset in the bore, ovality, the pull of the tacks; harmonics 1 to 3): belongs to the tube and turns with it; changes when tacks are made and with a new tube.
- **Judge bias** (glare, tint, tack marks, plate grain: anything the camera gets wrong that repeats with table angle): a station is a fixed point in the room, so an error that depends on table angle must come from the tube, and it turns with the tube.

The parts have signatures a judge can read without ground truth: harmonics 2 and 3 have no seat in them, so a re-seat should leave them alone; a turn of the tube in its nest rotates harmonics 2 and 3 together by k times the turn; a re-clamp changes only the rig's. One judge lap gives each harmonic to about 5.5 micrometres at judge noise 0.03 mm (3.2 at N = 3), so a change of 10 to 20 micrometres is visible from the judge alone. The judge cannot separate the work from its own bias (both turn with the tube), and cannot separate rig, seat and work in the first harmonic.

The one thing the judge cannot supply is an **unlike sensor**. A few touches (a stylus or the wire, `datum-07`) at K azimuths read the corner at the tool with no camera in the reading. Judge minus touch, at the touched azimuths, is the judge's bias for its low harmonics, if the touch noise is smaller than the bias. And a touch-based estimate carries no camera bias into a replayed map.

## What carries the loads, what establishes position, what is free or restrained

Nothing new carries anything; any support that holds the gun still enough to read. Position is established by the corner itself (touches) and by the judge's dot-versus-seam reading. The map is keyed to the rotator angle for the rig and seat pieces; to the tube's own angle for the work and bias pieces. The tube's own angle needs a reference on the work: the plate's two symmetric ports give it modulo 180 degrees (enough for every even harmonic), a tack or a mark gives 360. The register hole in the plate is a blind pocket in the inside face `[repo endcap_circular_dxf.py]`, not visible from the weld side.

## What software could command, observe, and what stays manual

- **Command:** rotator (existing); which azimuth to touch and when (proposed); which pieces to relearn after an event.
- **Observe:** judge harmonics 1 to 3, stored against now; touch readings at K azimuths; judge minus touch.
- **Manual:** fitting the stylus or letting the wire touch (unresolved); a master lap for the rig piece (a ground ring that fits the nest); deciding the weld tolerance (unknown).

## What was tried to break it

Numbers from the scene's model (`calc/owners_model.js`, 400 draws; amplitudes illustrative: rig 0.06 / 0.03, seat 0.20, work 0.06 / 0.05 / 0.02, bias 0.03 / 0 / 0.02 mm; N = 3 laps, judge noise 0.03, K = 8 touches, touch noise 0.02).

1. **The judge's bias is not in `trials-04`'s error.** *Assumption:* the replay is scored against the true seam, with random reading noise. *What the numbers say:* a relearn through the judge leaves 26 micrometres rms, of which 25 are the bias; after a tack, when the tacks add to the bias, 35. More laps do not remove it.
2. **What each event does to a stored map** (rms residual after replay, micrometres, stale map / judge relearn / rebuild the moved piece by touches): lift and return 27 / 26 / 20; re-seat 185 / 26 / 23; turned in the nest 206 / 26 / 28; re-clamped 69 / 26 / 17; tacked 87 / 35 / 17; new tube 193 / 26 / 17. The touch-based rebuild assumes the event is diagnosed correctly; the scene diagnoses from one judge lap and can be wrong.
3. **Time.** A relearn at N = 3 is 146 s at 8 mm/s. The route by diagnosis costs one judge lap (49 s) and then nothing (lift and return), four touches (64 s: re-seat, turn) or K touches (128 s: re-clamp, tack, new tube). So it saves time only for a lift and return. What it buys is attribution and a number for the judge's bias.
4. **The first harmonic is one lump.** Rig, seat, work and bias all put a first harmonic on the trace and one lap cannot split it; the diagnosis rebuilds the lump from four touches. *Left standing:* a re-clamp that changes only the rig's first harmonic is indistinguishable from a re-seat.
5. **A 120 degree turn hides harmonic 3.** Turning the tube in its nest by 120 degrees leaves harmonic 3 unchanged (|e^(-3i 120 deg) - 1| = 0); 100 degrees gives 1.0. The scene turns 100. The fit of one turn to harmonics 2 and 3 needs the rig part of them from a master lap; without it there are more unknowns than numbers.
6. **The touch check has to be quieter than the bias.** Over 300 draws, with a true bias of 25 micrometres, judge minus touch minus the expected noise reads 22 (touch noise 0.005 to 0.02) and 17 (0.04). One tube's reading swings by roughly a third; the scene shows the single-draw value beside the noise floor.

## Branches and combinations

- Branch of `trials-04-seam-map-replay` (its map, split by owner). Uses `datum-02` (harmonic fit, dry-lap signature) and `datum-07` (touch). `trials-01` supplies the puck's lift-and-return behaviour; `trials-17` (trial card) has the nuisance factors this table sorts by lifetime.
- Combines with `datum-19-plate-as-target`: the camera that reads the judge is also the source of the tube's own angle (ports modulo 180 degrees).
- Transferable: a learned map has owners; harmonics that a cause cannot reach are invariants; an unlike sensor at a few azimuths bounds a judge bias that turns with the work.

## Unresolved problems and questions for Derek

- **Bench test that would replace every amplitude:** indicate a tube at the rim near the weld end, turn the tube 100 degrees in its nest, indicate again, and compare the two traces against table angle. The part that stays put in table angle is rig and seat; the part that turned is the tube. (About ten minutes with the Neoteck indicator.)
- Does the camera judge have a bias that repeats with table angle? Plausible sources: tack marks, laser-cut plate edge dross, the rolling direction of the plate (a second-harmonic reflectance change tied to the plate's clock), heat tint. None is measured.
- How the stylus or wire reaches a chosen azimuth without disturbing the seat; whether a wire touch or the nozzle is good enough (`datum-07`: about ten times worse than a stylus).
- Question for the originator (trials): asymmetric puck seats give a unique phase; a symmetric pattern lets the puck be turned 120 degrees on the rig, which separates the rig's piece from the rest in one extra lap. Which is worth more?

## Assumptions

- Amplitudes, noise, times (49 s per lap [repo]; 16 s per touch including the table move: illustrative). Pieces are exact harmonics up to the third. Radial only; height has the same structure. The master lap gives the rig piece at harmonics 2 and 3 to half the touch noise.

## Sourcing pointers

`sourcing/datum.md`: digital indicator with data output (for the indicator log and the turn-in-the-nest test); CR Touch class probe and ruby-ball stylus (from the wave 1 entries).

## Scene id

`datum-14-who-owns-the-wobble`.
