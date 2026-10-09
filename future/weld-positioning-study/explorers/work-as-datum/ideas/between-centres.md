# B. Between centres — the gun is rigid, the work is forced onto it

Status: wave 1, developed. Sketch: `../sketches/between-centres.svg`.
Shares the port-nipple seat with `endcap-compass.md`; differs in which body
is compliant.

## Picture it (as it stands after wave 5)

The gun is held rigidly, and the work is pulled onto a fixed line to meet it.

- **One stiff base.** The rotator and the gun's support share it: a steel or
  aluminium sub-plate with a mast (B0–B2), or the drop-in collar of
  workspace-as-structure's table station with a bridge over its free +Y edge
  (B3).
- **The centre.** A spring-loaded quill comes straight down the tube axis.
  The axis is open up to hole dial ~40 because the gun's body sits off
  toward −Y. The quill carries a live centre or a hardened ball, which drops
  into a countersink on the same port seat as the compass (nipples + seat
  bar).
- **What moves.** The vessel spins between the nest (below) and the centre
  (above). Its top plate's centre is forced onto the quill's axis, and the
  loose tube is clamped into the nest with 30–50 N.
- **Height.** The quill's scale reads the plate-centre height. The gun's Z is
  set to that reading once per tube (B1), or the gun rides the plate face on
  a two-ball rocker (B2).
- **"Fixed"** is the sub-plate or collar. The work moves a fraction of a
  millimetre to meet it. B0 (mast only, tube indicated, one dial reading per
  tube) is kept as the simplest step.

**Sketches:**
- `../sketches/between-centres.svg` (mast + C-arm form, true opening pose);
- `../sketches/xw-collar-centre-and-lid.svg` top panel (the collar-hung
  centre in the table station = B3 / exchange repair W1).

**Major unresolved problems:**
- Face tilt is not followed in B1 (one plate-face reading per tube, or B2).
- The nest rocks slightly if the quill is off the rotator axis (0.08 mm per
  revolution for 0.2 mm).
- The copper ground shoe's side load while the centre forces the tube top is
  unquantified.
- Nipples and seat go on and off every closure.
- B's C-arm route is still needed at hole dial ≥ 50.

## The physical idea

A lathe does not float its tool to follow a wobbling part. It holds the part
between centres so the part turns about a line fixed to the machine, and the
tool stays rigid on the same machine. Here:

- **One rigid base** carries both the rotator and a gun mast: the rotator's
  PET-GF base bolts through its four Ø10 bench-clamp holes onto a steel or
  aluminium sub-plate; the mast stands on the same sub-plate. The bench only
  holds the sub-plate up. "Fixed" means fixed to this sub-plate.
- A **tailstock** hangs from the mast: a C-arm reaches in over the far rim to
  a vertical, spring-loaded quill on the tube axis, carrying a live centre
  point-down. The point drops into the centre socket of the same seat bar used
  in the compass — carried by two 1/4 NPT 316 hex nipples finger-tight in the
  plate's ports.
- The vessel is now held **between the nest (below) and the live centre
  (above)**. It spins about the line joining them. That line is fixed to the
  sub-plate, so the top plate's centre no longer wanders with runout, and the
  quill spring (30–50 N) holds the loose tube down into its nest.
- The **gun** stays on the mast, rigid in the room. Its height is set from
  the plate: the quill's position is the plate-centre height, and the gun's
  Z-slide is set to it and locked (B1), or rides the plate face on a small
  rocker skid (B2).

Compared with the compass: the same plate datum decides where the corner is,
but here the work is moved (a fraction of a millimetre) to meet a rigid gun,
instead of a light gun floating to meet the work. Hand on the trigger, cable
pull and wire conduit all go into the mast, not into a loose tube.

| Freedom | B0 baseline (axis-fixed mast) | B1 between centres | B2 between centres + skid |
|---|---|---|---|
| Radial at the corner | rotator axis + tube runout (indicate each tube) | plate centre forced onto the tailstock axis | same as B1 |
| Height at the corner | set per tube from the work, then locked | set per tube from the quill reading, then locked | followed continuously from the plate face |
| Face tilt | tube face runout (±0.15 at acceptance) | not followed | followed at the dot to ~±0.07 [Est] |
| Gun support | rigid mast | rigid mast | rigid in x, y, angles; free in z on a rail |

**B0, the plain step before the tailstock.** Sub-plate and mast only; the
tube is indicated per the procedure. Height is set from the work once per
tube: a spring plunger with a dial on the gun's Z-slide touches the plate face
~20 mm inboard of the dot; lower the slide until the dial reads the recorded
value, lock, retract the plunger. The same tube gives the same reading for its
second closure. This removes bench flex and the hand from the pose, and moves
the tube-length error from "the dot lands somewhere else" to "one dial
reading per tube".

## Geometry around the gun and joint

*Corrected in wave 2 (hole-dial offset, see `pose_geometry.py`).* At the
scene's opening pose the gun climbs out toward −Y: the housing centre is
~112 mm off the axis on the −Y side, the barrel descends through the sector
−10° to −75° at r ≈ 47–55, and the column above the tube axis is clear. So
the tailstock can come **straight down the axis** from a bridge or an arm
over the +Y side (the side opposite the gun) for hole dials up to ~30–40°;
at steep dials (55°) the barrel's back comes within ~31 mm of the axis at
z ≈ 150 and the quill must come in low from the +Y side instead. The quill
occupies r < 12, z = 25–70; the barrel at those heights is ≥ 47 mm from the
axis.

Rim at 238.4 mm above the bench, joint ~232 mm [Repo]. A mast top ~450 mm above
the sub-plate reaches over the gun body with room for the balancer-free rigid
arm and the cable strain relief.

## How it runs

1. Once: bolt rotator and mast to the sub-plate; align the tailstock quill to
   the rotator axis with the test indicator (its magnetic base on the NEMA 23
   lamination, as the procedure already does [Repo]) to a few hundredths.
   Back the nest's three M3 adjusters off to light non-contact so the top can
   centre on the tailstock.
2. Per tube: load, seat the plate (rim spacer), tack. Nipples in, seat bar on.
   Lower the quill — the live centre finds the socket; the spring takes up
   30–50 N.
3. B1: read the quill scale (plate-centre height), bring the gun's Z-slide to
   that reading plus the recorded offset, lock. B2: release the Z lock; the
   skid rocker lands on the plate face.
4. Dry run with the red dot; weld; stuck wire cut with the gun held rigid by
   the mast.
5. Lift quill, remove seat and nipples, unload.
6. Second closure: invert; the same tube has the same length, so in B1 the Z
   reading repeats to within the two recesses' difference; lower the quill,
   check the reading, weld.
7. Second person: sequence of lower-read-lock, no feel involved.

## Breaking it

**1. What "between centres" really fixes.** The tube's spin axis becomes the
line from the nest centre to the live-centre point. If the quill is off the
rotator axis by e, the tube axis tilts by e/152 mm and the bottom rim rocks on
the nest by about e × 63.5/152 per revolution (0.08 mm for e = 0.2). The top
corner's radius stays fixed in space; only the bottom contact wobbles. The
drive is friction at the nest, now helped by the quill preload. Unresolved:
whether the nest's printed seat tolerates that rocking without walking the
tube; small e makes it moot.

**2. The seat bar and nipples as a centre.** Same error chain as the compass
(`datum_budget.py` §6): the dot's radius relative to the plate edge carries
±0.1 (hole pattern vs OD in one laser program, estimate), ±0.13 (plate slip in
the bore), ±0.07 (nipple centring). The difference from the compass: that
error becomes a small once-per-rev radial sinusoid of a rigid gun, not
disturbance-driven motion of a floating one.

**3. Face tilt in B1.** Not followed. With indicating dropped, the face tilt
is whatever the rim spacer and tube end give, not the ±0.15 acceptance.
*Repair:* keep one face-runout check per tube (cheaper than full indicating),
or go to B2.

**4. B2 skid on a rigid-XY gun.** The gun rides a vertical MGN12 rail on the
mast, counterweighted to leave ~5–10 N on a rocker with two stainless ball
transfers on the plate face at r ≈ 42, ±35° either side of the dot's radius.
The rocker's pivot sits on the dot's radius at r ≈ 34, so tilt about the
tangent line leaves ~28 mm × tilt of error at the dot (≤0.07 mm at 0.14°
face tilt). The rail's friction (0.5–2 N [Est]) against a 5–10 N preload
is a hysteresis band; preloaded carriages are needed so the rail itself adds
no tilt play. The skid balls are well clear of the beam (they are 35° off the
dot's azimuth); the rocker must also clear the wire on the arriving side.

**5. Structure.** A 400 mm 4040 extrusion mast deflects ~0.02 mm under a 10 N
side load (EI estimate); the joints and adjustment stack will dominate.
Derek can weld a steel mast and arm with the X1 Pro itself, and a laser-cut
steel sub-plate is a SendCutSend job he already uses for the end plates.
Unresolved: the PET-GF rotator base between its clamp holes and its race is now
part of the gun-to-axis chain; its creep under a 30–50 N quill preload is small
but unmeasured.

**6. Loads on the work.** 30–50 N down on a tacked plate, through the nest,
balls and race of a rotator that already carries 20 N of vessel [Repo]. Before
tacking, the quill would push the plate down the bore, so it is lowered after
tacking (same constraint as the compass).

**7. Tube change and inversion.** Per tube: nipples, seat, quill, Z. No
indicating, no hand-held height. The second closure uses the same tube, so
height repeats.

**8. Access.** The C-arm and quill take the far side of the interior. The
camera can ride on the C-arm (fixed to the mast, looking across at the dot).
Stuck-wire cutting comes from the tangential side over the lip, as in the
compass.

## Parts (representative)

Same seat as the compass (316 hex nipples, printed seat bar), MT2 live centre
as the tailstock point, a spring-loaded quill (a dowel in a bronze bushing
or an MGN12 carriage with a compression spring), MGN12 rail for B2, a
laser-cut or welded steel sub-plate and mast. Observations in
`../../../sourcing/work-as-datum.md`.

## Contribution and open problems

Contribution: keeps the gun and its cables rigid and still for the whole
session (hand trigger allowed), while the work — not the gun — absorbs runout;
turns per-tube setup into lower-read-lock; clamps the loose tube into the nest
as a side effect.

Open: tailstock-to-axis alignment and whether the nest tolerates the small
rocking; B1 does not follow face tilt; the C-arm's route depends on the pose
family; the rotator base becomes part of the structural chain. B0 (mast
without tailstock) stays useful as the simplest step: it fixes the bench and
cable problems but leaves indicating and a per-tube height set.

---

## Wave 3 — objections and branches

Source: `../../../exchange/workspace-as-structure--on--work-as-datum.md` §3–4.

**Objection: the tailstock need not be a C-arm — accepted.** At the true
opening pose every gun surface stays ≥ 38.8 mm from the tube axis, and ≥ ~21 mm
across grip 30–60, vertical −30…+15 and hole dial ≤ 40. The column closes only
at dial ≥ 50. So the tailstock is a **vertical quill straight down the axis**
from a short bridge over the +Y side of the mouth. It is a drill-press quill
that doesn't depend on the pose family in that range; the C-arm (above) stays
as the form for dial ≥ 50.

**Branch B3 — between centres in the table station (theirs, adopted).**
- The drop-in collar is B's sub-plate; the bridge bolts to it.
- The rotator hangs from the collar on the shelf posts.
- The quill preload runs collar → bridge → quill → plate → tube → nest →
  rotator → shelf → posts → collar, and the bench is outside the loop.
- The quill scale is the per-tube height gauge: crank the shelf to the
  recorded reading, lock, check the dot.

This is the same as my exchange repair W1 with the plunger moved onto the
axis.

**A small disagreement on unloading order.** They say to lift the quill before
dropping the shelf. With a spring quill it isn't needed:
- As the shelf drops, the quill runs to its stop and the ball leaves the
  countersink.
- After a 70 mm drop the seat is ~51 mm below the ball tip (the nipples stand
  18.6 mm above the rim), so the tube slides out underneath.

Lifting first only matters for a rigid-stop quill (W1b), and even then only
if its stop sits lower than the seat's travel.

**What stays uncertain:** the ground shoe's side load on the tube while the
centre forces its top (the leaf preload is 0.75–1.5 mm [Repo]; its force was
not quantified), and face tilt in B1.
