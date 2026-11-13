//! What the display covers share, in the tip frame of `Gooseneck::tip_frame`: x across the neck,
//! s back up it from the tube exit, n out through the glass. The round neck the cover closes on,
//! the lips that snap into the shell's grooves, their inner corners relieved, and the relaxed
//! print, each side standing inward below the bezel by what it springs back from on the neck: a
//! rigid lean (`relaxed`), or a move that varies along the side (`relaxed_by`).
use crate::Gooseneck;
use crate::shell::PAST;
use anyhow::{Result, anyhow, ensure};
use hsm_faucet_numbers::shell::{
    DISPLAY_CLIP_BOTTOM_N, DISPLAY_CLIP_TOP_N, TUBE_SHELL_CENTER_Y, display_clip_s_bottom, display_clip_s_top,
};
use hsm_kernel::*;
use std::collections::HashMap;

/// The tip frame as a plane: a point (x, s, n) of the frame is the plane's (x, y, z).
pub fn tip_plane(neck: &Gooseneck) -> Result<Plane> {
    let (tip, _, normal) = neck.tip_frame();
    Plane::new(tip, V3::X, normal)
}

/// The neck's round profile of radius `r`, about the centre the tube shell is drawn round, swept
/// the gooseneck's whole length and on past the tube exit, so it cuts clean through a cover's
/// face that stands at the exit.
#[track_caller]
pub fn neck_round(neck: &Gooseneck, r: f64) -> Result<Solid> {
    neck.sweep(&Profile::circle(v2(0.0, TUBE_SHELL_CENTER_Y), r), 0.0, neck.length() + PAST)
}

/// How far a relief cutter stands out past the faces it cuts between, into the air.
const STANDOFF: f64 = 0.05;

/// mm between a relief cutter's sections where the neck bends.
const STEP: f64 = 0.5;

/// The lips: `band` less the neck round at radius `r`, each edge where that round meets the
/// clip's two planes chamfered `d` along both faces, as OCCT's chamfer of that distance cuts it.
/// Its section square to the edge is the triangle from the edge to the point `d` out along the
/// plane and the point on the round `d` from the edge.
pub fn lips(band: &Solid, neck: &Gooseneck, r: f64, d: f64) -> Result<Solid> {
    let lips = band.cut(&neck_round(neck, r)?)?;
    let s = (display_clip_s_bottom(), display_clip_s_top());
    let (bottom, top) = (DISPLAY_CLIP_BOTTOM_N, DISPLAY_CLIP_TOP_N);
    let round = Round { c: TUBE_SHELL_CENTER_Y, bend: neck.radius, tip: neck.tip, r };
    let frame = tip_plane(neck)?;
    let mut cutters = vec![];
    for side in [-1.0, 1.0] {
        for (plane, into) in [(bottom, 1.0), (top, -1.0)] {
            cutters.push(round.relief(side, plane, into, s, d)?.placed(&Plane::XY, &frame));
        }
    }
    lips.cut_all(&cutters)
}

/// The neck round in the tip frame: radius `r` about a centre line standing `c` out along n from
/// the gooseneck's, straight for `tip` up from the exit and then bent about the bend's centre,
/// `bend` in along n from the gooseneck's centre line.
struct Round {
    c: f64,
    bend: f64,
    tip: f64,
    r: f64,
}

impl Round {
    /// How far (s, n) lies out from the centre line in the plane square to it.
    fn out(&self, s: f64, n: f64) -> f64 {
        if s <= self.tip {
            n - self.c
        } else {
            (s - self.tip).hypot(n + self.bend) - (self.bend + self.c)
        }
    }

    /// The point's distance from the round's surface, positive outside it.
    fn distance(&self, p: V3) -> f64 {
        p.x.hypot(self.out(p.y, p.z)) - self.r
    }

    /// The edge on the plane at `n`, on the `side` of the neck, at `s`.
    fn edge(&self, side: f64, n: f64, s: f64) -> Result<V3> {
        let g = self.out(s, n);
        ensure!(g.abs() < self.r, "the plane at n {n} misses the neck round at s {s}");
        Ok(v3(side * (self.r * self.r - g * g).sqrt(), s, n))
    }

    /// The chamfer's cutter along the edge on the plane at `n` on the `side` of the neck, the
    /// lip lying `into` along n from that plane, from `s.0` to `s.1` and on past both ends.
    fn relief(&self, side: f64, n: f64, into: f64, s: (f64, f64), d: f64) -> Result<Solid> {
        let (s0, s1) = (s.0 - 2.0 * STANDOFF - d, s.1 + 2.0 * STANDOFF + d);
        let mut stations = vec![s0];
        if self.tip > s0 && self.tip < s1 {
            stations.push(self.tip);
        }
        let from = self.tip.max(s0);
        let steps = ((s1 - from) / STEP).ceil().max(1.0) as usize;
        stations.extend((1..=steps).map(|i| from + (s1 - from) * i as f64 / steps as f64));
        let sections = stations.iter().map(|&s| self.section(side, n, into, s, d)).collect::<Result<Vec<_>>>()?;
        Solid::loft(&sections)
    }

    /// The cutter's section square to the edge at `s`: from the chamfer's two feet out into the
    /// air past the plane and inside the round.
    fn section(&self, side: f64, n: f64, into: f64, s: f64, d: f64) -> Result<Region> {
        let p = self.edge(side, n, s)?;
        let h = 1e-4;
        let t = (self.edge(side, n, s + h)? - self.edge(side, n, s - h)?).unit();
        let across = v3(t.y, -t.x, 0.0) * side;
        let up = V3::Z * into;
        let foot = p + across * d;
        // The point on the round `d` from the edge, swung from the plane's foot into the lip.
        let at = |a: f64| p + (across * a.cos() + up * a.sin()) * d;
        let (mut lo, mut hi) = (0.0, std::f64::consts::PI);
        ensure!(self.distance(at(lo)) > 0.0 && self.distance(at(hi)) < 0.0, "no chamfer foot on the round at s {s}");
        for _ in 0..80 {
            let mid = 0.5 * (lo + hi);
            if self.distance(at(mid)) > 0.0 { lo = mid } else { hi = mid }
        }
        let wall = at(lo);
        let g = 1e-6;
        let grad = v3(
            self.distance(wall + V3::X * g) - self.distance(wall - V3::X * g),
            self.distance(wall + V3::Y * g) - self.distance(wall - V3::Y * g),
            self.distance(wall + V3::Z * g) - self.distance(wall - V3::Z * g),
        );
        // Out from the round, kept in the section's plane.
        let outward = (grad - t * grad.dot(t)).unit();
        let pts = vec![
            foot,
            foot - up * STANDOFF,
            p - (up + across) * STANDOFF,
            wall - outward * STANDOFF,
            wall,
        ];
        if pts.iter().any(|q| !q.x.is_finite()) {
            return Err(anyhow!("a relief section at s {s} is not finite"));
        }
        Ok(Region::polygon(pts))
    }
}

/// The relaxed print: the seated cover's bezel above `bezel_n` as it is, and below it each wing
/// leaned in toward the neck, `slope` across per millimetre down from the bezel, as it springs back
/// from the neck once pressed on. The wings are parted from `open`, the seated cover with its
/// cavity run on up through the bezel, so that no face lies on the plane they are parted on.
pub fn relaxed(neck: &Gooseneck, seated: &Solid, open: &Solid, bezel_n: f64, slope: f64) -> Result<Solid> {
    let frame = tip_plane(neck)?;
    let mut pieces = vec![seated.placed(&frame, &Plane::XY).trim(&Plane::XY.at(v3(0.0, 0.0, bezel_n)))?];
    let open = open.placed(&frame, &Plane::XY);
    for side in [-1.0, 1.0] {
        let half = open.trim(&Plane::new(V3::ZERO, V3::Y, V3::X * side)?)?;
        let wing = half.trim(&Plane::new(v3(0.0, 0.0, bezel_n), V3::X, -V3::Z)?)?;
        let lean = side * slope;
        let t = Affine { m: [[1.0, 0.0, lean, -lean * bezel_n], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]] };
        pieces.push(wing.mapped(&t)?);
    }
    Ok(Solid::union_all(&pieces)?.placed(&Plane::XY, &frame))
}

/// The longest edge the relaxed print's bent faces are split to, in mm.
const BEND_EDGE: f64 = 2.0;

/// How far out from the middle of the neck a side's whole move applies. Inboard of it the move
/// fades to nothing at the middle, where the two sides meet in the cover's end walls.
const BEND_FULL_X: f64 = 8.0;

/// The relaxed print of a cover whose sides spring back by different amounts along their length:
/// the seated cover's bezel above `bezel_n` as it is, and below it every point moved in toward the
/// neck by `inward(s, n)`, which is nothing at the bezel. The lower part is taken from `open`, as
/// `relaxed` takes its wings.
pub fn relaxed_by(neck: &Gooseneck, seated: &Solid, open: &Solid, bezel_n: f64, inward: impl Fn(f64, f64) -> f64) -> Result<Solid> {
    let frame = tip_plane(neck)?;
    let top = seated.placed(&frame, &Plane::XY).trim(&Plane::XY.at(v3(0.0, 0.0, bezel_n)))?;
    let below = open.placed(&frame, &Plane::XY).trim(&Plane::new(v3(0.0, 0.0, bezel_n), V3::X, -V3::Z)?)?;
    let bent = warped(&below, BEND_EDGE, |p| {
        let across = (p.x / BEND_FULL_X).clamp(-1.0, 1.0);
        v3(p.x - across * inward(p.y, p.z), p.y, p.z)
    })?;
    Ok(top.union(&bent)?.placed(&Plane::XY, &frame))
}

/// How far a bent point may stand off a face's surface and the face still keep its record.
const ON_SURFACE: f64 = 1e-9;

/// `solid` carried point for point by `f`, a smooth map that bends, which no affine map gives.
/// Its triangles are first split until no edge is longer than `max_edge`, so a bent face follows
/// `f` that closely. A plane whose points all stay on it keeps its record, as does any face `f`
/// leaves where it is; every other face becomes a free surface, as `Solid::mapped` makes one.
fn warped(solid: &Solid, max_edge: f64, f: impl Fn(V3) -> V3) -> Result<Solid> {
    let (verts, tris, face_of) = refined(solid.verts(), solid.tris(), solid.face_of(), max_edge)?;
    let moved: Vec<V3> = verts.iter().map(|&p| f(p)).collect();
    ensure!(moved.iter().all(|p| p.x.is_finite() && p.y.is_finite() && p.z.is_finite()), "a bend left a point nowhere");
    let mut kept = vec![true; solid.faces().len()];
    for (t, &face) in tris.iter().zip(&face_of) {
        let face = face as usize;
        for &v in t {
            let (was, is) = (verts[v as usize], moved[v as usize]);
            kept[face] &= match solid.faces()[face].surface {
                Surface::Plane { p, n } => (is - p).dot(n).abs() <= ON_SURFACE,
                _ => (is - was).norm() <= ON_SURFACE,
            };
        }
    }
    let faces: Vec<Face> = solid
        .faces()
        .iter()
        .zip(&kept)
        .map(|(face, &kept)| if kept { *face } else { Face { surface: Surface::Free { kind: "BSPLINE" }, ..*face } })
        .collect();
    Solid::from_mesh(&moved, &tris, &face_of, &faces)
}

/// The mesh with every edge longer than `max_edge` halved, and halved again until none is. Each
/// long edge takes one midpoint, which both of its triangles use, so the surface stays closed.
fn refined(verts: &[V3], tris: &[[u32; 3]], face_of: &[u32], max_edge: f64) -> Result<(Vec<V3>, Vec<[u32; 3]>, Vec<u32>)> {
    ensure!(max_edge > 0.0, "a bend's longest edge must be positive");
    let mut verts = verts.to_vec();
    let mut tris = tris.to_vec();
    let mut face_of = face_of.to_vec();
    for _ in 0..64 {
        let mut mids: HashMap<(u32, u32), u32> = HashMap::new();
        let mut next = Vec::with_capacity(tris.len());
        let mut next_face = Vec::with_capacity(tris.len());
        for (t, &face) in tris.iter().zip(&face_of) {
            // The midpoint of each edge `t[k]` to `t[k + 1]` that is too long.
            let mut mid = [None; 3];
            for k in 0..3 {
                let (a, b) = (t[k], t[(k + 1) % 3]);
                let (pa, pb) = (verts[a as usize], verts[b as usize]);
                if (pa - pb).norm() > max_edge {
                    mid[k] = Some(*mids.entry((a.min(b), a.max(b))).or_insert_with(|| {
                        verts.push((pa + pb) * 0.5);
                        (verts.len() - 1) as u32
                    }));
                }
            }
            let pieces: Vec<[u32; 3]> = match mid {
                [None, None, None] => vec![*t],
                [Some(ab), Some(bc), Some(ca)] => vec![[t[0], ab, ca], [ab, t[1], bc], [ca, bc, t[2]], [ab, bc, ca]],
                _ => {
                    // Turn the triangle so its first edge is split and its last is whole.
                    let whole = (0..3).find(|&k| mid[k].is_none() && mid[(k + 1) % 3].is_some()).expect("a split edge follows a whole one");
                    let [a, b, c] = [t[(whole + 1) % 3], t[(whole + 2) % 3], t[whole]];
                    let ab = mid[(whole + 1) % 3].expect("the first edge is split");
                    match mid[(whole + 2) % 3] {
                        Some(bc) => vec![[ab, b, bc], [a, ab, bc], [a, bc, c]],
                        None => vec![[a, ab, c], [ab, b, c]],
                    }
                }
            };
            next_face.extend(std::iter::repeat_n(face, pieces.len()));
            next.extend(pieces);
        }
        if mids.is_empty() {
            return Ok((verts, tris, face_of));
        }
        tris = next;
        face_of = next_face;
    }
    Err(anyhow!("a bend's triangles never came down to edges of {max_edge}"))
}
