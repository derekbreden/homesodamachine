//! Part 1 of `enclosure`: the functions whose first Python line is in 118–2116 (52), from
//! `print_up` to `back_top_flank_bound`: the piece frames and wall faces, the wago and condenser
//! slot figures, the corner columns and the cavity, the bound ledger and the Z-seam readings.
#![allow(non_snake_case, non_upper_case_globals, dead_code, unused_imports)]
use super::{Box, Bound, BoxReadings, Cx, Pack, PortField, State, _ReadingBounds};
use crate::typed::_enclosure_panel::{self as panel, Solid};
use crate::typed::num::{self, Num};
use crate::typed::py::{self, Args, Kwargs, Py, Tup, Val};
use anyhow::{Context, Result};
use std::rc::Rc;

/// The functions of this part that run typed: the hybrid build replaces exactly these.
pub const CONVERTED: &[&str] = &[];

/// A function of this part as a Python-callable value.
pub fn function(cx: &Rc<Cx>, name: &str) -> Option<Result<Val>> {
    let _ = cx;
    match name {
        _ => None,
    }
}

/// `_c14_pocket_landmarks()`: the right-top landmarks of the C14 pocket outline, each `(x, z)`,
/// as the dict Python returns (`shoulder`, `round_mid`, `tangent_start`, `ear_tangent`, `nose`).
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct C14Landmarks {
    pub shoulder: [f64; 2],
    pub round_mid: [f64; 2],
    pub tangent_start: [f64; 2],
    pub ear_tangent: [f64; 2],
    pub nose: [f64; 2],
}
impl Py for C14Landmarks {
    fn to_py(&self) -> Result<Val> {
        Ok(py::dict([
            ("shoulder", self.shoulder.to_py()?),
            ("round_mid", self.round_mid.to_py()?),
            ("tangent_start", self.tangent_start.to_py()?),
            ("ear_tangent", self.ear_tangent.to_py()?),
            ("nose", self.nose.to_py()?),
        ]))
    }
    fn from_py(value: &Val) -> Result<C14Landmarks> {
        let v = py::snapshot(value)?;
        let at = |key: &str| -> Result<[f64; 2]> { Py::from_py(&py::at(&v, key)?) };
        Ok(C14Landmarks {
            shoulder: at("shoulder")?,
            round_mid: at("round_mid")?,
            tangent_start: at("tangent_start")?,
            ear_tangent: at("ear_tangent")?,
            nose: at("nose")?,
        })
    }
}

/// The build direction of one quadrant, as the sign of the box's Z it grows along: +1.0 for
/// a piece bedded on its Z- face, -1.0 for one bedded on its Z+ face.
pub fn print_up(cx: &Cx, y_side: &str, z_side: &str) -> Result<f64> {
    cx.generated("print_up", crate::py_args![y_side.to_owned(), z_side.to_owned()], vec![])
}

/// Every stated section a FLUTED face stands on, as (what, mm) — what a groove is cut into,
/// read by `flute-backed` against `flute_backing`.
///
/// A SURVEY IS NOT A GATE. Every one of these was measured on the built solids, by ray sweep
/// and again by boolean, and measuring is also what found the three the file did not state:
/// the front face under the display facet's arris, the east bosses' bores where the corner
/// round carries the surface inboard, and a port pocket running off that same tangent. The
/// first two became figures of their own — `facet-arris-backed` and `east_boss_bore_end` —
/// because they are computed rather than typed. This is the rest, stated so that a section
/// thinned in the file goes red here instead of on the next print.
pub fn flute_backed_sections(cx: &Cx) -> Result<[(String, f64); 12]> {
    cx.generated("flute_backed_sections", crate::py_args![], vec![])
}

/// One lug's own axes in a side wall's frame, as `(y, z, x)` — the closed-body
/// height along the row, the lever-hinge axis across it, the wire-entry axis reaching
/// inboard.
pub fn wago_stand(cx: &Cx, size: &str) -> Result<[f64; 3]> {
    cx.generated("wago_stand", crate::py_args![size.to_owned()], vec![])
}

/// How far into the well the lug's butt half goes, which is how far the tower
/// stands off the wall.
pub fn wago_engage(cx: &Cx, size: &str) -> Result<f64> {
    cx.generated("wago_engage", crate::py_args![size.to_owned()], vec![])
}

/// The well's outer half-extents on the wall, as `(y, z)` — the lug's own half plus
/// the wall it is wrapped in and that wall's press clearance.
pub fn wago_half(cx: &Cx, size: &str) -> Result<[f64; 2]> {
    cx.generated("wago_half", crate::py_args![size.to_owned()], vec![])
}

/// How far a lug reaches on ±Y with its levers worked — the closed body plus the
/// swing off each face that hinges one. The 221-420 hinges on both.
pub fn wago_swing(cx: &Cx, size: &str) -> Result<f64> {
    cx.generated("wago_swing", crate::py_args![size.to_owned()], vec![])
}

/// The running clearance on each face of the flange sliding into the groove.
pub fn cond_slot_half(cx: &Cx, sheet: f64) -> Result<f64> {
    cx.generated("cond_slot_half", crate::py_args![sheet], vec![])
}

/// The world Y a station's groove opens at — one millimetre past the swallowed grip, so
/// the flange enters from the bay and the groove never dead-ends on its own flange span.
pub fn cond_slot_mouth(cx: &Cx, face: f64) -> Result<f64> {
    cx.generated("cond_slot_mouth", crate::py_args![face], vec![])
}

/// The ±X interior faces, struck off the stated width alone. `_dims` builds the box on
/// these and every body seated on a flank reads them through the same call, so the wall and
/// the things that stand against it cannot come apart.
pub fn interior_x(cx: &Cx) -> Result<[f64; 2]> {
    cx.generated("interior_x", crate::py_args![], vec![])
}

/// back-top's own interior rear plane — `back_top_wall_t` in from the exterior, where the
/// box's own is one `wall` in.
///
/// `rear_plane_y` is still the interior of the machine and every body is packed to it; this is
/// the plane back-top's own +Y wall and its furniture stand on. back-bottom needs no such
/// figure: its wall is the lip's own skin carried to the slab and already measures the same.
pub fn back_top_wall_face(cx: &Cx) -> Result<f64> {
    cx.generated("back_top_wall_face", crate::py_args![], vec![])
}

/// The section the +Y wall carries at one station — what a fitting's clamped stack is struck
/// from, and the figure `enclosure_assembly.port_clamp_stack` reads it off.
///
/// A RELIEF IS A FACT ABOUT THE WALL, not a note beside it. The CO2 station's barrel cannot take
/// `back_top_wall_t`, so the wall is thinner there and this says so by measuring the same figure
/// the solid is cut on rather than by naming an exception.
pub fn back_wall_t_at(cx: &Cx, x: f64, z: f64) -> Result<f64> {
    cx.generated("back_wall_t_at", crate::py_args![x, z], vec![])
}

/// back-top's own ±X interior faces — `back_top_flank_t` in from the exterior, where the
/// box's own is one `wall` in.
///
/// `interior_x` is still the box's interior and every seated body is packed to it; this is the
/// plane back-top's own flank furniture stands on, and the plane `_dims` reads back against the
/// pack (`back-top-flank-clear`).
///
/// THREE THINGS OUTSIDE BACK-TOP STAND ON THIS PLANE, so `back_top_flank_t` is not back-top's
/// alone to move. `_rail_nominal_foot_face` takes the shallower of this and back-bottom's for
/// the foot the two of them share, and the assembly datums both `SPLIT_COLUMN` and the exposed
/// rib's wall root on it. Changing the section carries all three, which is why `back-top-flank-clear` reads a body's built solid
/// against this face rather than the column it was placed on.
pub fn back_top_flank_face(cx: &Cx) -> Result<[f64; 2]> {
    cx.generated("back_top_flank_face", crate::py_args![], vec![])
}

/// back-bottom's own ±X interior faces — `back_bottom_flank_t` in from the exterior, where
/// the box's own is one `wall` in and the lip's underwall is `2 * wall`.
///
/// NOTHING OUTSIDE THAT PIECE READS THIS. `interior_x` is still the box's interior and
/// `lip_face_x` is still what a body seated low on a flank meets; this is the plane
/// back-bottom's own flank stands on, and the plane `piece_root_faces` hands a feature built
/// on it.
pub fn back_bottom_flank_face(cx: &Cx) -> Result<[f64; 2]> {
    cx.generated("back_bottom_flank_face", crate::py_args![], vec![])
}

/// front-bottom's own ±X interior faces — `front_bottom_flank_t` in from the exterior.
///
/// `lip_face_x` DOES NOT FOLLOW IT. The card that bottoms on the west flank and the copper lane
/// struck off that same plane both keep the face they had, which is what makes the west side a
/// well and not a move; the east side has only the condenser against it and that block reads
/// this plane, so it comes west with the wall.
pub fn front_bottom_flank_face(cx: &Cx) -> Result<[f64; 2]> {
    cx.generated("front_bottom_flank_face", crate::py_args![], vec![])
}

/// The interior face a vent slot is struck from — the plane the cut has to start at for the
/// grille to come out the other side.
///
/// IT IS THE FACE THAT IS THERE AND NOT `lip_face_x`. The airway stands in front-bottom's own
/// bands, and that piece carries `front_bottom_flank_t` down both flanks where the lip's own
/// underwall would leave `2 * wall` — so a slot struck on the lip's plane stops short of the
/// room, and what it leaves is a blind pocket with the wall still closed behind it. Read by
/// the cutter, by the run finder and by the measure, so all three agree about the same wall.
pub fn vent_flank_face(cx: &Cx, sx: f64) -> Result<f64> {
    cx.generated("vent_flank_face", crate::py_args![sx], vec![])
}

/// front-top's own ±X interior faces — `front_top_flank_t` in from the exterior, where the
/// box's own is one `wall` in.
///
/// `interior_x` is still the box's interior, and the bodies and the seams are all struck on it;
/// this is the plane front-top's own flank furniture stands on and the plane its openings are
/// cut to. All four pieces carry their own section in from it, and `_rail_nominal_foot_face`
/// takes the shallower of this and front-bottom's for the foot the two of them share, so the
/// front column's two sections answer to each other.
pub fn front_top_flank_face(cx: &Cx) -> Result<[f64; 2]> {
    cx.generated("front_top_flank_face", crate::py_args![], vec![])
}

/// Where front-top's grown flank face begins: its underside rises at 45° off the seam rim at
/// the box's interior face to the face (`_front_top_flank_bedding_cut`).
pub fn front_top_flank_root_z(cx: &Cx) -> Result<f64> {
    cx.generated("front_top_flank_root_z", crate::py_args![], vec![])
}

/// Where each corbelled valve tray's root corbel meets the bulkhead's aft face (`_valve_trays`):
/// the plate's floor, less the depth it overhangs that face.
pub fn tray_corbel_roots(cx: &Cx, stations: &Val, wall_aft_y: f64) -> Result<Vec<f64>> {
    cx.generated("tray_corbel_roots", crate::py_args![stations.clone(), wall_aft_y], vec![])
}

/// The ±X interior faces BELOW a Z seam, one `wall` inboard of `interior_x`.
///
/// A wall a Z-seam lip stands on is `2 * wall` thick from the floor slab to the lip rim
/// (`_lip_underwall`), so what a body seated low on a flank meets is this plane and not
/// the other one.
pub fn lip_face_x(cx: &Cx) -> Result<[f64; 2]> {
    cx.generated("lip_face_x", crate::py_args![], vec![])
}

/// The six interior planes a feature built on THIS PIECE actually roots on — `inner` with
/// each face that piece carries thicker than the box's own standing where that piece puts it.
///
/// `inner` IS THE BOX'S INTERIOR and every seated body is packed to it, which is what makes it
/// the right frame for a station: a run's lane, an anchor's band and a boss's plan are all struck
/// against the plane the pack stands in. IT IS NOT THE FRAME A RIB STOPS IN. Four faces on this
/// box stand inboard of it on the piece that carries them — back-top's two flanks
/// (`back_top_flank_face`), front-top's (`front_top_flank_face`), back-top's +Y wall
/// (`back_top_wall_face`), and a bottom piece's flanks, which are the lip's own underwall
/// (`lip_face_x`) — so a feature drawn to the box's plane on one of those is drawn to a plane
/// that piece has already filled in.
///
/// WHAT THAT COSTS IS THE ZIP TIE'S CHANNEL. A rib's two ends climb from the bore's crown to the
/// face it roots on and the channel is the room LEFT between them (`_tube_anchors`): measured to
/// a plane the wall stands inboard of, the whole of it comes out inside that wall's own stock,
/// and the rib arrives buried to its crown with nowhere for a tie to pass.
pub fn piece_root_faces(cx: &Cx, inner: [f64; 6], y_side: &str, z_side: &str) -> Result<[f64; 6]> {
    cx.generated("piece_root_faces", crate::py_args![inner, y_side.to_owned(), z_side.to_owned()], vec![])
}

/// Right-top landmarks of the pocket outline: a long flat, a knuckle round, the common
/// external tangent to the ear circle, and the nose.
pub fn _c14_pocket_landmarks(cx: &Cx) -> Result<C14Landmarks> {
    cx.generated("_c14_pocket_landmarks", crate::py_args![], vec![])
}

/// Half extents of the tunnel block: the bore's own section, the inserts' ligaments and the
/// flange pocket's wall, whichever reaches furthest on each axis.
pub fn c14_mount_half(cx: &Cx, bore_w: f64, bore_h: f64, screw_reach: f64) -> Result<[f64; 2]> {
    cx.generated("c14_mount_half", crate::py_args![bore_w, bore_h, screw_reach], vec![])
}

/// The Z of back-top's ceiling's interior face, `back_top_ceiling_t` in from the show face —
/// where the box's own lane (`inner[5]`) is one `wall` in. Every station under the ceiling is
/// struck on the lane; this is the plane the slab presents between its pockets, and the plane a
/// feature standing under the ceiling on this piece may rise to.
pub fn back_top_ceiling_face(cx: &Cx) -> Result<f64> {
    cx.generated("back_top_ceiling_face", crate::py_args![], vec![])
}

/// The slab's added section, unrelieved: between back-top's own flank faces, from the Y
/// telescope's end (`back_flank_start`) to back-top's own +Y face, and from the ceiling's
/// interior face up one millimetre into the top wall it fuses with.
///
/// Struck on stated figures alone (the seam `y_seam`, the lane off `appliance_height`), so the
/// pack can read a body against it before any box is drawn.
pub fn back_top_ceiling_stock(cx: &Cx, y_joint: Option<f64>, lane: Option<f64>) -> Result<Solid> {
    cx.generated("back_top_ceiling_stock", crate::py_args![y_joint, lane], vec![])
}

/// The first Y plane carrying either back piece's full-thickness flank.
///
/// Both back flanks begin past BOTH telescopes. The front half's Y lip runs to
/// `y_joint + lip_len`; `z_lip_y_margin` past that rim is the first plane the closing
/// front half never lands on. Back-bottom's added skin, back-top's nominal section and
/// every seam feature which roots in that section all meet this one plane.
pub fn back_flank_start(cx: &Cx, y_joint: f64) -> Result<f64> {
    cx.generated("back_flank_start", crate::py_args![y_joint], vec![])
}

/// The Box as `_box_spec` writes and reads it: its pack's stations without the placed solids.
///
/// A station is numbers and a body is not, so the description a producer hands another action
/// carries the walls and not the bodies that sized them. Both sides of a comparison between a
/// freshly derived box and a restored one take this form, because the restored one has no
/// solids to compare against.
pub fn documented(cx: &Cx, box_: &Box) -> Result<Box> {
    cx.generated("documented", crate::py_args![box_.clone()], vec![])
}

/// Enter one bound's reading in the ledger, replacing any of the same id.
pub fn record_bound(cx: &Cx, bound: Bound) -> Result<Bound> {
    cx.generated("record_bound", crate::py_args![bound], vec![])
}

/// A cavity with extra room at its supported face, along the piece's build direction.
pub fn _supported_cut(cx: &Cx, cutter: &Solid, up: f64) -> Result<Solid> {
    cx.generated("_supported_cut", crate::py_args![cutter.clone(), up], vec![])
}

/// A section's own points with the first repeated, so the closing edge is DRAWN.
///
/// `Workplane.close()` does not draw it — it reads the last edge's end back off OCCT, which
/// hands it back rebuilt as origin + t·direction, a few 1e-16 from the point that was passed
/// in, and lays the closing edge from there. The wire's first vertex then stands that far off
/// the station the section states. A tangential boolean downstream — the teardrop roofs on
/// their sleeve bore are one — resolves a coordinate that near zero either by inheriting the
/// constructed vertex or by recomputing the intersection, and which it does moves between
/// processes: the same source writes one of two files, and the artifact pointer file ping-pongs
/// between two hashes with nothing in the tree changed. Naming the closing point leaves the
/// vertex exactly where the section put it, and the tie is not there to take.
pub fn _ring(cx: &Cx, section: &Val) -> Result<Vec<Val>> {
    cx.generated("_ring", crate::py_args![section.clone()], vec![])
}

/// The centre one corner column's face arc is swung from — the INTERIOR CORNER.
///
/// THE COLUMN IS THE RELIEF'S CONGRUENT TWIN. The relief outside is a QUARTER TURN of
/// `corner_round` tangent to both outer faces; a mirror is congruent or it is not a mirror,
/// so the face is a quarter turn of the same radius — same arc, same length — and the only
/// place such a turn fits inside the cavity with its ends on the two inner faces is swung
/// from the corner they meet at.
pub fn _column_arc(cx: &Cx, inner: [f64; 6], sx: i64, sy: i64) -> Result<[f64; 2]> {
    cx.generated("_column_arc", crate::py_args![inner, sx, sy], vec![])
}

/// One corner column as a solid over the height span `z`, grown `grow` into the room.
///
/// THE ARC IS THE WHOLE OF IT AND THE CORNER BEHIND IT IS SOLID. The column is everything
/// within `column_round` of the interior corner; `_cavity` takes the difference, so what
/// becomes material is that disc's share of the AIR and the wall keeps the rest. Nothing
/// stands between the column and the cove it rises out of — a second arc back there would
/// be a through slot the column's whole height, and its only free surface is the face.
///
/// Growing swells the disc, which is the offset read on that one surface.
pub fn _corner_column(cx: &Cx, inner: [f64; 6], sx: i64, sy: i64, grow: f64, z: [f64; 2]) -> Result<Solid> {
    cx.generated("_corner_column", crate::py_args![inner, sx, sy, grow, z], vec![])
}

/// One column AND the lip's own skin where it wraps it — the whole of what a body meets
/// at a standing vertical, and the whole of what gives way to one.
///
/// The lip and the wall under it are struck as the cavity's skin (`_lip_band`), so at a
/// vertical they do not stop at the column: they WRAP its face and stand one `wall` further
/// inboard than the pillar does, floor slab to rim. A body reaching into a corner meets that
/// wrap before it meets the column, and a relief measured on the column alone is a relief
/// that leaves the thing actually in the way standing.
///
/// `zj` is that Y column's own seam, so the wrap ends where its lip's rim does. Above it the
/// pillar is the column and nothing else.
pub fn _column_pillar(cx: &Cx, inner: [f64; 6], sx: i64, sy: i64, zj: f64) -> Result<Solid> {
    cx.generated("_column_pillar", crate::py_args![inner, sx, sy, zj], vec![])
}

/// How far along a wall's INNER face a column reaches, from the interior corner.
///
/// Its CUSP stands on that face at one radius — where the quarter turn lands — and the lens
/// closes back toward the corner from there, so a body anywhere on that wall meets the cusp
/// and nothing of the column is further along than it.
pub fn _column_along(cx: &Cx) -> Result<f64> {
    cx.generated("_column_along", crate::py_args![], vec![])
}

/// How far in from a standing vertical a wall's inner face is FLAT — what anything
/// BEARING on that face has to stand clear of.
///
/// The relief rolls the face away `corner_round - wall` from each corner. Where that corner
/// carries a COLUMN the flat ends sooner still: the lens's cusp stands on this face and the
/// section closes back toward the corner from there, so a flange carried past it bears on
/// curve either way. Struck across every corner rather than one, the way `wall_band_corner_y`
/// is, because the ±X walls answer as a pair and a body reads the fence before it knows which
/// end it is at.
pub fn wall_flat_from_corner(cx: &Cx) -> Result<f64> {
    cx.generated("wall_flat_from_corner", crate::py_args![], vec![])
}

/// How far a column reaches out of the cove it rises from, across the corner's diagonal.
///
/// The face stands one radius off the corner there; the cove the wall already turned stands
/// `(corner_round - wall) * (sqrt2 - 1)` off it, and the column is everything between.
pub fn _column_depth(cx: &Cx) -> Result<f64> {
    cx.generated("_column_depth", crate::py_args![], vec![])
}

/// The box's AIR at `inset` in from every interior face — the rounded cavity less the
/// columns standing in its corners.
///
/// Everything that has to stand inside the cavity is held inside this, so a collar or a
/// lip segment meets a column exactly the way it meets a wall. The wall rounds shrink with
/// the inset (square once one reaches zero) and the columns grow by it: one offset, read
/// from the two sides of the same surface.
pub fn _cavity(cx: &Cx, inner: [f64; 6], inset: f64, z: Option<[f64; 2]>) -> Result<Solid> {
    cx.generated("_cavity", crate::py_args![inner, inset, z], vec![])
}

/// One corner pocket with its floor and roof following the cradle rail's groove.
///
/// The floor holds the grip plane through the mouth, then falls 1:1 to the insertion
/// floor. The roof rises 1:1 from the flange's fitted ceiling to the body room's ceiling.
/// Both meet the column's relief walks on the same planes.
pub fn _cradle_relief(cx: &Cx, room: [f64; 6], station: [f64; 6]) -> Result<Solid> {
    cx.generated("_cradle_relief", crate::py_args![room, station], vec![])
}

/// One column's pocket for the body standing in it. Clipped to the PILLAR — the column and
/// the lip's skin wrapping it (`_column_pillar`) — so what a pocket can ever take is that and
/// never the wall behind it or the boss beside it.
///
/// A pocket a cradle rail crosses is floored by that rail's groove to the groove's mouth and
/// by its own insertion floor aft of it (`_cradle_relief`): the room was measured round the
/// flange the groove takes, so the station whose face is the room's own fore plane, whose
/// flange stands inside the room's height, and whose rail crosses the room's width is the one
/// that owns the fore floor. Every other pocket is its box.
pub fn _column_relief(cx: &Cx, inner: [f64; 6], sx: i64, sy: i64, room: [f64; 6], zj: f64, cradle: &[[f64; 6]]) -> Result<Solid> {
    cx.generated("_column_relief", crate::py_args![inner, sx, sy, room, zj, Tup(cradle.to_vec())], vec![])
}

/// The walk one pocket's PRINT-UP FACE takes into the column beyond it — its ceiling where
/// the piece's print up is the box's +Z (`up` = +1), its floor where it is −Z (`up` = −1) —
/// and the piece that decides how much of it survives.
///
/// A POCKET IS A BITE OUT OF A CORNER, and the corner is where its material is: the two faces
/// toward it have column under them the whole height, and the two away from it open on the
/// cavity. Cut flat, that face is a shelf hanging off the corner. Walked in off both HELD
/// faces at `relief_chamfer` it stands one millimetre further up the build axis for every
/// millimetre it reaches away from one, and the column closes back over the pocket a layer at
/// a time. Its height is the pocket's own plan: at `min(width, depth)` the two walks have met.
///
/// IT IS CUT BEFORE THE PIECE FUSES ANYTHING AND AGAIN WITH THE POCKET AFTER EVERYTHING. The
/// first cut walks the shell itself; the second walks any rail or boss that subsequently grew
/// over that same air. This makes the final face a question about the finished piece rather
/// than a figure a row carries, and prevents an overlapping feature from restoring a short flat
/// roof over the pocket.
pub fn _column_relief_rise(cx: &Cx, inner: [f64; 6], sx: i64, sy: i64, room: [f64; 6], zj: f64, up: f64, cradle: &[[f64; 6]]) -> Result<Solid> {
    cx.generated("_column_relief_rise", crate::py_args![inner, sx, sy, room, zj, up, Tup(cradle.to_vec())], vec![])
}

/// How far aft a body standing `reach` inboard of a ±X wall's inner face reaches before
/// the box's own standing-vertical relief curves that wall away from it.
///
/// The cavity is rounded `corner_round - wall` about a centre one radius in from each face,
/// so at a back corner the wall leaves the body's plane along an arc. This is where the arc
/// crosses that plane — and unlike a boss it is a bound at EVERY height, which makes it the
/// aft end of what the band has to give. A body reaching further inboard than the radius is
/// clear of the arc entirely and answers to the +Y wall itself.
///
/// WHERE THAT CORNER CARRIES A COLUMN the arc is no longer what a body meets first: the lens
/// stands in the air the arc left open, and its room-facing side is swung from the corner. The
/// −X wall's back corner carries one and this still reads the arc, because nothing on that
/// flank comes near either — the tap-water cradle stands 9.9 mm off the wall where the lens
/// reaches 9, and every body aft of it stops 20 mm short of the rear plane. The reading this
/// owes a column is owed on the flank whose bodies are IN it.
pub fn wall_band_corner_y(cx: &Cx, reach: f64) -> Result<f64> {
    cx.generated("wall_band_corner_y", crate::py_args![reach], vec![])
}

/// The aftmost station on a ±X wall that carries a boss its whole `mount_boss_out` long.
///
/// THE STANDING CORNER IS THE FENCE HERE. The cavity's vertical corners are relieved
/// `corner_round - wall` for the bed, so from that arc's centre plane aft the wall is no
/// longer at `interior_x`: it curves inboard, a boss on it is shorter than the heat-set it
/// carries, and where the arc crosses the boss tip there is no boss at all. The centre plane
/// is the last station with the whole length under it, and it is a bound at every height, the
/// relief running the box's full standing depth.
///
/// A mounting pattern answers to this; an envelope answers to `wall_band_corner_y`, which is
/// where the same arc crosses the plane the BODY stands on, further aft.
///
/// A COLUMN IN THAT CORNER DOES NOT MOVE THIS. A boss is printed material and so is a lens,
/// so a boss standing inside one comes out of the print as one body with it and keeps only
/// its bore — absorbed, the way the condenser's cradle rail is. What a lens does fence is the
/// BODY hung on that boss, whose own overhang is in air; that is `wall_band_corner_y`.
pub fn wall_boss_aft_limit(cx: &Cx) -> Result<f64> {
    cx.generated("wall_boss_aft_limit", crate::py_args![], vec![])
}

/// The BACK half's free run of the ±X side bands, as `(y0, y1)` — the depth a body hung on
/// that flank has aft of the Y seam.
///
/// ONE Y SPAN CARRIES BOTH CORNER STACKS. They differ in height and share a station, so
/// `y_seam + lip_len`, where a back knuckle's inboard face ends, is the aft face of both at
/// once and no height has to be named to say where they stop. Aft of it the band meets the
/// back corner's own relief (`wall_band_corner_y` at a wall seat's reach), which is the one
/// thing on this flank that stands at every height.
///
/// THE Z-SEAM RAILS ARE NOT IN IT. Each stands in the seam's own storey — so a body standing
/// clear of it in z passes it, and whether one does is a question about a placed pack.
/// `enclosure_assembly.check_east_band` asks that against `seam_bosses`, which carries each
/// piece of furniture's height as well as its station.
///
/// Struck off the stated planes alone, `y_seam` and `rear_plane_y` — so a body reads it
/// before the box that carries it has been sized, the same way it reads the wall itself
/// through `interior_x`.
pub fn east_band_free_y(cx: &Cx) -> Result<[f64; 2]> {
    cx.generated("east_band_free_y", crate::py_args![], vec![])
}

/// The FRONT half's free run of the ±X side bands, as `(y0, y1)` — the run
/// `east_band_free_y` says this half has and is not.
///
/// ITS ENDS ARE THE FRONT WALL AND THE Y SEAM'S OWN CORNER. The rail is the Z seam's
/// furniture on a flank, it lives in the seam's own `z_seam..z_seam + z_rise` storey, and a
/// body under the mouth never meets it — `z-slide-lanes` is what reads a body that stands up
/// into the storey the slide sweeps. So the run is the whole flank, front face to the root a
/// front knuckle takes fore of the seam.
///
/// IT TAKES THE FRONT FACE because it cannot state it. The back half's two ends are both
/// struck on planes the box states about itself — `y_seam` and `rear_plane_y` — but the front
/// wall stands off whatever the pack puts nearest it, so a caller reading this before the box
/// is sized has to say what that is. Everything after it is the same stated chain `_dims`
/// builds the wall on.
pub fn front_band_free_y(cx: &Cx, front_face: f64) -> Result<[f64; 2]> {
    cx.generated("front_band_free_y", crate::py_args![front_face], vec![])
}

/// Everything the seam stands in a ±X side band, as `(y0, y1, z0, z1)` — what each piece of
/// it occupies of that wall, both walls taken together.
///
/// The two corner stacks occupy the overlap from a front knuckle's root to the back flank: the
/// lower from the slab to the Z seam, the upper from its floor to the ceiling. Read from the
/// definitions that BUILD them (`y_stack`, `y_stack_y`, `_z_rail_runs`), so a footprint cannot
/// drift from the geometry it stands for.
///
/// THE HEIGHT IS HALF THE ANSWER. A body hung on a flank clears a stack by standing beside it
/// or by standing over or under it, and a reading with no z in it can only see the first.
/// Outside the stacks' occupied heights, the band is the wall's own air.
///
/// THE RAILS ARE IN THE ANSWER TOO. Each column's hooked rail runs its flanks' straight
/// runs over the seam's own storey, mouth to rim. Both carry their full nominal foot first
/// and place the hook at that foot's inboard edge. Both remain inside `side_band_inset`, so
/// the band the pack keeps covers them. A row per column says so, at the run each column's
/// rail actually takes.
pub fn seam_bosses(cx: &Cx, inner: [f64; 6], y_joint: f64, splits: [f64; 2]) -> Result<Vec<[f64; 4]>> {
    cx.generated("seam_bosses", crate::py_args![inner, y_joint, splits], vec![])
}

/// Whether a placed body's bounding box meets any of `bosses` in BOTH y and z.
pub fn _in_a_boss(cx: &Cx, b: _ReadingBounds, bosses: &[[f64; 4]]) -> Result<bool> {
    cx.generated("_in_a_boss", crate::py_args![b, bosses.to_vec()], vec![])
}

/// The heights in `[z0, z1]` a seam may land on, given the Z spans standing in
/// that column: what the bodies leave open, inset `clear` at each end so the seam
/// plane lands on neither. `[(lo, hi), ...]`, lowest first; a gap too thin to inset
/// is not a band.
///
/// A gap of exactly `2 * clear` IS a band — one height, no slack — because that is
/// what a pack squeezed to its minimum leaves, and refusing it on a rounding bit
/// would refuse a box that closes.
pub fn _open_bands(cx: &Cx, spans: &[[f64; 2]], z0: f64, z1: f64, clear: f64) -> Result<Vec<[f64; 2]>> {
    cx.generated("_open_bands", crate::py_args![spans.to_vec(), z0, z1, clear], vec![])
}

/// `bands` held inside `[lo, hi]` — what falls wholly outside it drops out.
pub fn _clipped(cx: &Cx, bands: &[[f64; 2]], lo: f64, hi: f64) -> Result<Vec<[f64; 2]>> {
    cx.generated("_clipped", crate::py_args![bands.to_vec(), lo, hi], vec![])
}

/// The heights a Z seam may take and leave both its pieces printable.
///
/// The bottom piece runs the floor slab's underside to its seam RIM (`zj + z_rise`,
/// where the station collars stop too); the top piece runs the seam plane to the top
/// wall's outer face. Both print standing on a Z face, so the bed's Z bounds each of
/// them, and each bound is one end of this band.
pub fn _bed_band(cx: &Cx, inner: [f64; 6]) -> Result<[f64; 2]> {
    cx.generated("_bed_band", crate::py_args![inner], vec![])
}

/// The Z-seam lip's own shape over a height span: the cavity's one-`wall` skin.
///
/// `inset` pulls the skin's OUTER surface inboard and keeps its inner one — the lip the
/// box builds stands `slide_slip` off every face the top piece slides along, because a
/// slide the length of a column cannot run printed face on printed face the way a 13 mm
/// drop could. The nominal skin (inset 0) is what the measures read: it is the lane the
/// seam OWNS, a hair wider than the lip standing in it, conservative the way a probe
/// should be.
///
/// THE LIP IS NOT A BOX. It is struck as the cavity's skin (`_cavity`), so it carries the
/// wall rounds at the standing verticals and WRAPS whatever column stands in one — the
/// pillar telescopes into the piece above on the same one wall of overlap every other face
/// uses. A rectangular band drawn to the same figures is neither: it reaches into corners
/// the cavity has rounded away, and it misses the wrap entirely, which is the part that
/// stands furthest inboard.
///
/// `_lip_underwall` is struck from this same figure, so the wall below the mouth and the
/// measures that read the seam's lane come off one shape.
pub fn _lip_band(cx: &Cx, inner: [f64; 6], z: [f64; 2], inset: f64) -> Result<Solid> {
    cx.generated("_lip_band", crate::py_args![inner, z, inset], vec![])
}

/// The seam heights the pack denies ONE Y column's Z seam, as z spans.
///
/// The seam's furniture on a flank is the RAIL: groove, arm and head together span
/// `rail_reach_in` from `interior_x` over the seam's own storey, on the runs that column's
/// rails take, wherever the seam lands. Both channel walls follow the inboard portion of
/// their full nominal feet. So the lane measured is the actual profile on those runs, over
/// the full height of the box — and a body standing in one
/// denies the seam heights that would put the slide through it: from `z_rise` under its foot (the
/// rim would be below it) to one `rail_flare_drop` over its crown, which is how far the arm's
/// under-flare hangs below the seam and therefore how high above a crown a seam can still drop
/// rail through it.
///
/// A Z SEAM IS PER Y COLUMN AND SO IS ITS LANE. `y_span` is that column's half, cut
/// at the Y joint; a body spanning the joint is charged to both columns, as it
/// should be. What holds the rest of the lane open is the pack's own standoffs —
/// `side_band_inset` at the flanks, which the rail stands inside.
pub fn _lip_denied(cx: &Cx, placed: &Val, inner: [f64; 6], y_span: [f64; 2], plate: &Val, y_joint: f64, commons: Option<&Val>) -> Result<Vec<[f64; 2]>> {
    cx.generated("_lip_denied", crate::py_args![placed.clone(), inner, y_span, plate.clone(), y_joint], vec![("commons", commons.cloned().to_py()?)])
}

/// The bottom↔top seam height per Y column: `(front, back)` — the one stated plane,
/// both.
///
/// `stated` is `z_seam`, and what is measured here is what it lands in: the band the bed
/// leaves a column's two pieces (`_bed_band`), each column's own lip lane — the heights
/// the pack leaves the lip's ring (`_lip_denied`) — and the open bands the column's
/// bodies leave, which is what `_report_seams` reads. None of the bounds stops the cut:
/// whatever the readings say, both seam heights come back and the box is cut on them.
pub fn _z_joints(cx: &Cx, placed: &Val, inner: [f64; 6], stated: f64, plate: &Val, y_joint: f64, readings: Option<&BoxReadings>) -> Result<[f64; 2]> {
    cx.generated("_z_joints", crate::py_args![placed.clone(), inner, stated, plate.clone(), y_joint], vec![("readings", readings.cloned().to_py()?)])
}

/// The existing flank envelope, including finite drilled hardware lanes.
pub fn back_top_flank_bound(cx: &Cx, placed: &Val, pack: &Pack, y_joint: f64, splits: [f64; 2], bounds: Option<&Val>) -> Result<Bound> {
    cx.generated("back_top_flank_bound", crate::py_args![placed.clone(), pack.clone(), y_joint, splits], vec![("bounds", bounds.cloned().to_py()?)])
}
