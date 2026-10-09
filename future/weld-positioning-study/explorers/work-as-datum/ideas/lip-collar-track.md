# C. Riding the tube at the weld — direct follower, and the collar that repairs it

Status: wave 1, moderate depth. Sketch: `../sketches/lip-collar-track.svg`.
Numbers: `../datum_budget.py` §2.

## Picture it (as it stands after wave 5)

The datum is the tube wall itself, read at or near the weld's azimuth.

- **C0.** A stationary carriage (azimuth tethered, weight on a balancer)
  carries the gun. It touches the tube through a rim roller and a pinch pair
  of stainless rollers on the top 2 mm of the lip, 25° ahead of the puddle on
  the cold side. The rotator turns the tube under the rollers.
- **C1.** A collar of two half-rings closed by a stock 5 in exhaust band
  clamp grips the OD 12–30 mm below the plate and turns with the tube. The
  carriage rides the collar's flat top and outer cylinder instead of the
  thin lip.
- **C2** (workspace-as-structure's branch): the wall is mapped on a cold lap
  at the dot's own azimuth with the gun lifted off. The map is replayed
  during the weld by moving the work; C0's pinch stays only as a sensor for
  slow thermal drift.
- **"Fixed"** is the tube wall near the weld.
- This is the member of the family that doesn't need the plate's ports.

**Sketch:** `../sketches/lip-collar-track.svg` (true opening pose; C0 rollers
and C1 collar in section at the weld azimuth).

**Major unresolved problems:**
- A single follower 25° ahead leaves 43% of the runout error and 85% of the
  ovality error.
- The rim's waviness is not the plate face.
- The collar's temperature is unmeasured, and it decides the material.
- C2 needs a real-time stream of table angle.

## C0 — the original: rollers on the lip beside the weld

The most literal work-as-datum: the gun's carriage carries small rollers that
touch the tube right beside the weld and follow it. A stationary carriage
(azimuth held; weight on a balancer or a compliant mount from a mast) with,
on the **arriving side** ~25° ahead of the puddle (cold, unwelded metal on the
first lap):

- one roller on the rim top — height;
- two rollers pinching the lip wall in its top 2 mm, one in the bore and one
  on the OD — radial, with no net radial load on the lip.

The dot is then held relative to the local wall and rim, 27 mm along the seam
from where they are read. This is the classic mechanical seam follower.

### Breaking C0

1. **The lip is soft.** The 6.35 mm lip is unbacked above the plate, and
   between tacks the plate only resists the wall moving *inward*. A ring
   estimate with the shell bending length as effective height gives
   ~30 µm per newton at the rim (`datum_budget.py` §2; plausible range ×0.3–1).
   A single roller pressing with 5 N would move the lip by up to ~0.16 mm —
   the same order as the whole positioning target. The pinch pair cancels the
   net load; the rim roller loads the tube axially, where it is stiff. So the
   contacts survive only as a pinch plus an axial roller.
2. **The rim is not the fillet's base.** The corner lies on the plate's flat
   face; the rim is a saw cut, deburred, whose waviness is unmeasured. The
   plate was set 6.35 mm below it by a spacer that bridges its high points.
   Following the rim adds its waviness to the dot height.
3. **Heat on the second half.** On the first lap the arriving side is cold.
   In the last ~45° (the 20° overlap plus the 25° lead) the rollers run onto
   the start of the bead, welded ~45 s earlier. Roller contacts in the top
   2 mm of the lip stay above the bead crown (the table in the rotation rig
   doc gives a 1.2 mm wire-only leg at 8 mm/s [Repo]), but they run on a warm,
   possibly distorted lip exactly where the bead closes.
4. **It touches a weld-prep surface.** The bore band below the rim is
   prepared for the fillet [Repo, step 3]. Rollers must be stainless and
   clean; they will leave tracks.
5. **Tacks.** Tacks sit in the corner; the contacts in the top 2 mm of the lip
   clear them.

Kept as the original: it needs no ports and reads the wall right where the
beam lands, and a pinch pair is a real mechanism. Its problems are
compliance and rim waviness, not impossibility.

## C1 — repair: a collar that turns with the tube and gives the carriage a clean track

Instead of rolling on the thin lip, clamp a **collar** around the tube OD just
below the plate (z ≈ −12 to −30, where the tube is round and there is a
plate just above it), turning with the tube. The collar's flat top face and
outer cylinder are a wide, stiff running track; the gun's carriage rides it at
the weld azimuth with two rollers on the top face and two on the outer
cylinder, loaded by the carriage's residual weight and a light spring.

- Clamping: two half-rings closed by a stock **5 in lap-joint exhaust band
  clamp**, a high-volume part made for 5.00 in OD tube (400+ bought/month on
  one Prime listing [Obs]). The band supplies the clamp load; the half-rings
  supply the track.
- Height registration at install: three removable fingers hook the rim (rim
  datum), or a gauge reaches through the interior to the plate face (plate
  datum). Fingers come off before welding so nothing stands above the rim.
- Carriage: from the track (r ≈ 80–90, z ≈ −20) up over the lip to the gun
  shell, ~100 mm — short, and at the weld azimuth, so the lever from datum to
  dot is small.
- Nothing slides on the tube. The only tube contact is the clamped collar.

### Breaking C1

1. **Heat at the collar.** 12–30 mm below the fillet, on the wall that
   conducts the bead's heat down, near the weld azimuth. Printed PET-GF there is
   doubtful. Aluminium half-rings (e.g. laser-cut 1/2 in 6061 annulus halves,
   a SendCutSend material) cope, but a laser-cut edge is a poor radial track
   (taper, striations); the top face is mill-rolled plate, a good height track.
2. **Radial datum is the OD at the collar**, so wall-thickness variation and
   the plate's slip gap both enter between the track and the corner. Not
   better than the compass radially.
3. **Install time.** Band clamp and fingers per closure — a minute or two, more
   than dropping the compass seat on two nipples.
4. **Axial slip of the collar** under the carriage's down-load is resisted
   by band-clamp friction; fine unless the clamp is left loose.

### Side effects worth naming (they change the process, not just the pose)

- A metal collar clamped at the **lip's** OD instead (z 0 to +6.35) would
  back and chill the unbacked lip that the procedure says distorts when heat
  dwells [Repo]. That is a new process variable, not free precision.
- A conductive collar gives the continuity shoe a clean ring to wipe instead
  of the scuffed tube stripe. The existing shoe works; this is only an
  observation.

## Where C sits among the three

The compass (A) and between-centres (B) both need the plate's two open,
tapped ports at weld time, which the procedure provides [Repo]. C is the
port-independent member of the family: if a future plate loses its
on-diameter port pair, or fittings are in place, or Derek wants nothing on the
plate face, the datum can come from the tube at the weld azimuth instead.
Its cost is heat, install time and a track that is only as round as the tube
it is clamped to.

Open: collar temperature (unmeasured, decisive for material), rim waviness vs
plate face, whether the pinch pair of C0 is simply good enough without a
collar.

---

## Wave 3 — objections and branches

Source: `../../../exchange/workspace-as-structure--on--work-as-datum.md` §2.

**Objection: a follower ahead of the puddle leaves most of the error — accepted,
with numbers I didn't have.** A single contact at lead angle L corrects the dot
with the wall position at the contact, not at the dot:

| Error type | Left after following | At 25° (C0) | At 25°, symmetric pair ±25° |
|---|---|---|---|
| Once-per-rev runout | 2·sin(L/2) | 0.43 | 0.09 |
| Ovality | 2·sin L | 0.85 | 0.36 |

The trailing contact of a symmetric pair would sit on metal welded ~3 s
earlier, which C0 was designed to avoid. So C0 removes about half the runout
error and very little ovality, while touching the soft lip.

**Branch C2 — map cold at the dot's azimuth, then replay (theirs, adopted).**
1. With the gun lifted off, a probe from the room structure reads the pinch
   pair (radial) and a plate-face skid (height) at lead 0° over one pedalled
   revolution.
2. The map is replayed during the weld by moving the work (X stage and shelf
   Z).
3. C0's live pinch stays on as a sensor for slow thermal drift only (live
   reading minus the map at the contact's azimuth).

What I'd add from my side:
- After a plate-centre datum (W1, the compass hubs, B3), the bulk of the map's
  content is already gone: runout and tube length. What remains is the plate's
  own edge eccentricity to its port pair plus ovality, ±0.1–0.2 mm. A replay
  stage then needs ±0.3 mm of travel, not millimetres.
- The same map can come without contact from the red dot and a camera on a
  dry lap (machine-that-learns' observation layer), leaving the pinch pair for
  drift.

**Objection: C1's collar needs an r ≈ 95 opening in a counter.** True in the
table station. In a free-standing rotator station it doesn't arise. C1 stays
the port-independent continuous follower with its heat problem open.
