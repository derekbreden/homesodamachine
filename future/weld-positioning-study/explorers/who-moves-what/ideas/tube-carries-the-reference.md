# The tube carries the reference (rim rider, and its measured cousins)

## Picture it (as it now stands)

In each branch the rotating tube, not the room, sets the gun's radial position
and height.

- **3a, contact rider.** A light carriage hangs free from a balancer and is
  located only by its contacts: a tripod of stainless ball transfers on the plate
  face (height and both tilts), two rollers on the tube OD (radial and yaw), and
  a soft tether for travel around the tube, the one harmless freedom. The
  carriage carries the shell through a recipe block.
- **3b, map and replay.** One dry lap maps the corner's radial and height error
  against table angle (camera or indicator). A small X–Z stage replays the map
  during the weld, clocked by the rotator's pulse count.
- **3c, gauge foot.** A retractable foot on the shell touches the plate face and
  the bore once per tube, at 3–4 between-tack angles, and the holder is set to the
  mean. The foot then lifts clear. Nothing rides during the weld.

**Sketch:** `../sketches/s4-rim-rider-section.svg`, a radial section of 3a's
contacts. It is schematic and pose-independent; only the nozzle hint is the proxy.

**Major unresolved problems:**
- **3a clashes with the barrel at the true pose** (wave 5,
  `../wave5_rider_check.py`). The scene's wire approaches from −Y, so the cold,
  arriving side is −Y, and that is the sector the barrel descends through
  (−9° to −80°). Tripod pads at −10° to −40° interfere by 7–14 mm and clear only
  from ≈ −60°. That far upstream a single contact passes 1.0 × eccentricity and
  1.7 × ovality to the dot, no better than a fixed gun. Rim-top and OD contacts
  (sequence-of-use's saddle C) clear the barrel. 3b and 3c are unaffected.
- **The tube's runout harmonics** are unmeasured (3b measures them).
- **Contact temperatures**, and the wall-thickness transfer at the OD.

## The original (wave 1)

**Allocation in one line:** the rotating workpiece positions the gun in X
(radial) and Z (standoff), through contacts on the tube and plate. The room
holds only what the tube cannot, which is the tangential position. The angles are
set on the carriage per recipe. The weight hangs from a balancer.

Sketch: `../sketches/s4-rim-rider-section.svg`. Numbers: `../geometry.py`
(follower offset), `../allocation_calcs.py` section 7.

## Why give position to the work at all

The corner is not where the rotator's axis says it is. It carries each tube's
diameter, the plate's seating depth in its slip fit (±0.005 in radial slip,
depth set by hand at tacking), and runout that the procedure accepts up to
0.25 mm radial and 0.30 mm face TIR. Every other idea measures the corner (camera,
indicator) and moves something to match. This idea lets the corner push the gun
into place continuously, tube after tube, with no per-tube setup of X or Z. That
is the purest form of "the process lives in the equipment": a second person
loads a tube, lowers the carriage, and the geometry is right.

## 3a — contact follower (rim rider)

**Contacts** (see sketch; positions are proposals):

- **Z (and tilts):** omnidirectional skids on the plate face (the tripod in the
  table below). The outer two sit at r ≈ 47 mm, inboard of the ~1.5 mm fillet
  and the tacks and outside the port circle (ports at 19.05 mm ± 5.6 mm), so they
  never cross a hole. All three ride upstream of the station on cold,
  not-yet-welded plate. A 5/8 in stainless ball transfer (CY-15A class, Prime)
  is the representative part.
- **X and yaw:** two rollers on the tube OD below the plate level, straddling or
  both upstream, 30–40 mm apart. Two OD contacts act as a V-block. They register
  the carriage's radial position *and* its yaw to the tube's own local tangent,
  so the room tether no longer sets yaw (see below).
- **Transfer:** the OD registers the bore through the wall (1.65 mm nominal).
  Wall variation, estimated ~0.1 mm, becomes an X error.

**Carriage:** a stiff printed or aluminium bridge that straddles the 6.35 mm
lip, carrying the scan-fit shell through a recipe block (roll, hole tilt).

**Exactly six constraints, all but one from the tube.** The carriage has six
freedoms:

| Freedom | Constrained by |
|---|---|
| Z, and the two tilts | a tripod of ball transfers on the plate face: two at r ≈ 47 mm (~10° and ~40° upstream), one at r ≈ 30 mm (clears the port circle, 13.5–24.6 mm) |
| radial X, and yaw | two rollers on the OD, 30–40 mm apart, both upstream |
| travel around the tube | a soft tether to the rotator base — the harmless freedom (symmetry) |

The tripod registers the gun to the plate's own plane, so a plate tacked slightly
tilted tilts the gun with it. **Preload:** a balancer tuned to leave ~15–25 N of
net weight on the tripod, and a light spring from the tether anchor pulling the
carriage radially onto the OD rollers. The runout moves the spring end by at most
0.25 mm, so the preload hardly changes.

**Tether:** only the one freedom the tube cannot hold. Because of the tube's
symmetry (see notebook), where the carriage sits along the seam does not matter:
the OD roller pair makes its yaw follow the local tangent. The tether's
compliance therefore never reaches the weld. Without the roller pair, the
tether's Y position would *be* the yaw (1.08 mm per degree) and would have to be
precise. An earlier sketch had an X–Z rail float as well as the roller pair.
That combination over-constrains and fights the rollers, so the carriage hangs
free and the contacts do all the locating.

**Operation:** set the recipe block, then lower the carriage onto the loaded
tube. The skid lands on the plate face and the rollers close on the OD. Dry-run
one lap and watch the dot stay in the corner. Weld with pedal and trigger. Lift
the carriage (the tether hinges up) and unload.

### Break it

- **Which runout does a follower actually catch?** A contact offset φ from the
  dot sees the tube at a different angle. For eccentricity (the first harmonic,
  including the tilt that dominates face runout), a single contact 20° upstream
  passes 0.35 × the error to the dot. For ovality (second harmonic), it passes
  0.68 ×. At 30° upstream, ovality passes 1.00 ×, which is no better than a fixed
  gun set at the mean. A pair straddling ±20° and averaged passes only 0.06 ×
  eccentricity and 0.23 × ovality. But the downstream contact rides freshly
  welded plate and OD, which is hot. **The follower's value depends on the tube's
  harmonic content, which has not been measured.** Branch 3b measures it first.
- **Tacks.** Eight tacks sit in the corner. The skid and rollers avoid the corner
  entirely (plate face inboard, OD outside), so the tacks pass underneath. A skid
  *in* the corner, the classic mechanical seam tracker, would ride every tack
  (~1 mm bumps) and is rejected for this joint.
- **Heat.** Upstream contacts ride cold metal except during the final ~20°
  overlap, when the bead's start (welded ~45 s earlier at 8 mm/s) passes under
  them. Plate-face temperature at r = 47 mm there is unknown. Steel ball
  transfers and metal rollers survive heat; their grease may not. Choose dry or
  high-temperature variants, or accept a service interval.
- **Cable forces versus preload.** The preload (~15–25 N net weight on the
  tripod after the balancer; a 10–20 N radial spring onto the OD rollers;
  estimates) must exceed any cable pull, or the umbilical will lift a skid. Repair: hang the
  umbilical and wire conduit from an overhead balancer or boom so their net
  force on the carriage is a few newtons and constant. This is the same repair as
  every idea: separate weight and cable load from location.
- **Which side the gun leans.** The scene's wire approaches the dot from −Y,
  the gun's side. The procedure puts the wire on the arriving side, so the
  arriving, cold side is −Y, and the table turns counter-clockwise from above.
  At the opening pose (hole dial 30) the gun's centre of mass (sequence-of-use's
  proxy) sits at about (−30, −108) mm, ~112 mm from the axis, outside the wall on
  that same −Y side. So the upstream contacts sit under the gun's lean, but the
  weight acts outboard of the plate tripod and must be taken by the balancer
  attached at the centre of mass. At hole dial 65 the centre of mass was over the
  tube centre instead.
- **Friction drag** of the skid and rollers loads the tether tangentially.
  Rolling contacts keep it small. The tether is soft on purpose.
- **Lift-off and stuck wire.** The tube stops with the pedal, and the carriage
  stays seated because it rides the tube. Snip as now. To unload, the carriage
  lifts on the hinged tether; the gun comes out with it.
- **Inverted closure.** The follower rides the upper end only, so it is
  identical.
- **Plate seating error is followed, not corrected.** If a plate is tacked
  tilted, the Z skid follows the plate face, which is what the weld wants.
  The OD rollers follow the tube, not the plate edge, which is also what the
  weld wants.

## 3b — map and replay (measure the tube, let software move the gun)

The contacts are replaced by one dry-run lap. The reference beam and camera (or
the dial indicator on the plate face and OD at the station) record the corner's
X and Z against table angle. The rotator already counts 14,400 pulses per
revolution. A small motorized X–Z stage, under the gun or under the work (see
`still-gun-moving-work.md`), replays the map during the weld, synchronised to the
same pulse count.

- **Allocation:** measurement to a dry run; motion to a 2-axis micro-stage;
  timing to the rotator firmware. Nothing touches the hot metal.
- **It is also the experiment that decides 3a.** One mapped lap per tube shows
  whether the runout is eccentric (easy to follow) or oval (hard), and whether it
  matters beside the process window.
- **Break:** the map assumes reseating and heating do not change the geometry
  between the dry lap and the weld. Tack distortion is already present at the dry
  lap. Heat distortion of the lip during the weld is not captured.

## 3c — gauge foot (the tube sets X and Z once per tube, then steps away)

A retractable foot on the shell touches the plate face and the bore once per
tube, and the shell is locked there. A cam then lifts the foot ~2 mm clear
before the weld. Precision is used only at setup, and nothing rides during the
weld. It is cheap, needs no camera for X/Z, and follows nothing. It is the
minimal version of "the tube carries the reference".

## Contribution / unresolved / assumptions

- **Contribution:** puts the only reference that truly matters (this plate in
  this tube) in charge of X and Z. It removes per-tube setup, which is the
  strongest route to a second operator. It also shows how the tube's symmetry
  plus a V-block on the OD frees the tether from setting yaw.
- **Unresolved:** tube runout harmonics (measure with 3b); contact temperatures;
  whether the wall-thickness transfer is good enough; how the carriage, shell and
  gun together stay light enough to float.
- **Rests on:** repo dimensions for the ports, plate and wall; the proxy nozzle
  position; estimated preloads and masses.

---

## Wave 3 notes (from sequence-of-use)

- **3c gauge foot.** A single touch sets the corner at one table angle, not the
  mean. Touch at 3–4 between-tack angles and set to the mean; that is 3b's map
  taken with a feeler, the same as my exchange branch D-m. Agreed.
- **3c's retract cam** must close its force loop inside the shell, or
  retracting disturbs whatever holds the shell. Agreed.
- **Rim rider and tilt.** In `tilt-cradle-escape-rail.md` at τ ≈ 32°, the gun's
  centre of mass sits in the vertical tangent plane over the arriving side. A
  rider's upstream contacts would then carry the gun's lean directly, a better
  preload geometry than upright, where the weight acts outboard of the plate
  tripod.

---

## Wave 5: 3a at the true opening pose (my own check, `../wave5_rider_check.py`)

**Break.** At dials 45 / 30 / −15 the barrel descends through the sector −9° to
−80° about the tube axis. The nozzle is at r = 55 mm, 11 mm above the plate; the
graduated tube reaches r = 48–49 mm at 28–50 mm up. That is the −Y side, which is
the cold, arriving side when the wire is on it.

| Pad angle | 3a tripod pad column (plate face to +22 mm) | member straddling the lip at rim + 12 mm |
|---|---:|---:|
| −10° | −10.9 mm | −7.8 mm |
| −25° | −14.2 mm | −5.1 mm |
| −40° | −7.4 mm | +1.1 mm |
| −60° | +4.2 mm | +12.7 mm |
| −80° | +15.9 mm | +24.3 mm |
| +25° | +13.4 mm | +20.1 mm |

(Negative means interference.)

*Assumption behind the wave-1 layout:* "~10° and ~40° upstream" was chosen
before the barrel's sector at the true pose was known.

**What each way out costs.**
- **Pads at ≥ 60° upstream** clear, but a single contact there passes
  1.0 × eccentricity and 1.7 × ovality, no better than a fixed gun.
- **Pads downstream (+Y)** clear from +25°, but ride freshly welded plate.
- **Rim-top and OD contacts** (sequence-of-use's saddle C) clear the barrel:
  rollers at r ≈ 62.7 mm on the rim sit ~9 mm clear at −25°. They give up the
  plate-face reference, which was my C5 suggestion to them, so plate tilt relative
  to the rim passes through again.
- **3b (map and replay) and 3c (gauge foot)** have no riding contacts. The gauge
  foot can touch at +25° to +40° at setup, while nothing is hot.

**Where this leaves 3a.** In its plate-face form it does not fit the scene's
opening pose. Its useful residue is 3b, which measures whether following is needed
at all, and 3c. Sequence-of-use's rim-top saddle is the riding form that fits.
