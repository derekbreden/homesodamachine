//! Helix sweeps: a profile carried along a helix.
//!
//! A screw motion turns a point about an axis while it rises along it, one pitch per turn
//! (`Solid::screw`). Carried by it rigidly, every copy of the profile is the first one turned and
//! lifted: the helix's own (Frenet) frame, a thread's or a coil's.
//!
//! Carried along the helix through a point in a rotation-minimizing frame instead
//! (`Solid::helix_sweep`), the profile does not spin about the helix's tangent as it goes, and
//! turns against the screw frame by the helix's torsion times its length — OCCT's corrected
//! Frenet sweep, the frame `sweep` carries a profile along lines and arcs in. Its frames come
//! by the same double reflection.
//!
//! The turn is cut by the rule at the profile's farthest reach from the axis, so the outermost
//! fiber holds it. A wall is recorded as a cylinder about the axis when every vertex of it lies
//! at one radius from the axis; otherwise it is a free surface. The two ends are planes.
use crate::build::{Part, cleaned, orient};
use crate::face::{Face, Src, Surface};
use crate::mass::signed_volume;
use crate::math::{TAU, V3, cos, sin};
use crate::plane::Plane;
use crate::profile::{Profile, Region};
use crate::rule::{canonical_axis, ring_count};
use crate::solid::Solid;
use crate::triangulate::triangulate;
use anyhow::{Result, ensure};
use std::collections::HashMap;
use std::panic::Location;

/// `q` turned `angle` radians counterclockwise about the axis through `c` along unit `d`, then
/// lifted `rise` along it.
fn screwed(q: V3, c: V3, d: V3, angle: f64, rise: f64) -> V3 {
    let v = q - c;
    let (s, k) = (sin(angle), cos(angle));
    c + v * k + d.cross(v) * s + d * (d.dot(v) * (1.0 - k) + rise)
}

/// The unit normal a closed polygon winds counterclockwise about.
fn newell(p: &[V3]) -> V3 {
    let c = p.iter().fold(V3::ZERO, |s, &q| s + q) / p.len() as f64;
    let mut n = V3::ZERO;
    for i in 0..p.len() {
        n += (p[i] - c).cross(p[(i + 1) % p.len()] - c);
    }
    n.unit()
}

/// How each copy of the profile is placed.
#[derive(Clone, Copy)]
enum Carry {
    /// Rigidly, by the screw motion.
    Screw,
    /// Along the helix through this point, in a rotation-minimizing frame.
    Minimal(V3),
}

/// One copy's place: where the first copy's origin went, and its frame's three axes.
struct Station {
    o: V3,
    x: V3,
    y: V3,
    z: V3,
}

impl Station {
    fn place(&self, l: V3) -> V3 {
        self.o + self.x * l.x + self.y * l.y + self.z * l.z
    }
}

/// The helix's unit tangent at `p`, turning counterclockwise about `d` when `sense` is positive.
fn tangent(p: V3, c: V3, d: V3, pitch: f64, sense: f64) -> V3 {
    (d.cross(p - c) * sense + d * (pitch / TAU)).unit()
}

/// `region` carried `turns` turns about the axis through `c` along `d` — counterclockwise about
/// `d` when positive — rising `pitch` along `d` per turn, capped at both ends.
#[allow(clippy::too_many_arguments)]
fn helical(region: &Region, carry: Carry, c: V3, d: V3, pitch: f64, turns: f64, src: Src, op: &'static str) -> Result<Part> {
    ensure!(turns.abs() > 1e-12, "a {op} of no turn");
    ensure!(d.norm() > 1e-12, "a {op} about no axis");
    let d = d.unit();
    ensure!(
        pitch.abs() > 1e-12 || turns.abs() < 1.0 - 1e-12,
        "a {op} of a whole turn without rise closes on itself; revolve it"
    );
    let loops = cleaned(region)?;
    let normal = newell(&loops[0].pts);
    let sense = turns.signum();
    let pts = || loops.iter().flat_map(|lp| lp.pts.iter().copied());
    let reach = match carry {
        Carry::Screw => pts().map(|q| (q - c).reject(d).norm()).fold(0.0, f64::max),
        Carry::Minimal(s) => (s - c).reject(d).norm() + pts().map(|q| (q - s).norm()).fold(0.0, f64::max),
    };
    let n = ((ring_count(reach) as f64 * turns.abs() - 1e-9).ceil() as usize).max(1);
    let angle = |i: usize| turns * TAU * i as f64 / n as f64;
    let rise = |i: usize| pitch * turns.abs() * i as f64 / n as f64;

    let g = loops[0].pts.iter().fold(V3::ZERO, |s, &q| s + q) / loops[0].pts.len() as f64;
    let motion = match carry {
        Carry::Screw => d.cross(g - c) * sense + d * (pitch / TAU),
        Carry::Minimal(s) => tangent(s, c, d, pitch, sense),
    };
    let lean = normal.dot(motion.unit());
    ensure!(lean.abs() > 1e-9, "a {op} whose profile's plane holds its own motion");
    let up = if lean > 0.0 { normal } else { -normal };
    let (loops, flat) = orient(&loops, up);
    let cap = triangulate(&flat)?;

    let stations: Vec<Station> = match carry {
        Carry::Screw => (0..=n)
            .map(|i| {
                let (a, r) = (angle(i), rise(i));
                let o = screwed(V3::ZERO, c, d, a, r);
                let turn = |v: V3| screwed(c + v, c, d, a, 0.0) - c;
                Station { o, x: turn(V3::X), y: turn(V3::Y), z: turn(V3::Z) }
            })
            .collect(),
        Carry::Minimal(s) => {
            let p: Vec<V3> = (0..=n).map(|i| screwed(s, c, d, angle(i), rise(i))).collect();
            let t: Vec<V3> = p.iter().map(|&q| tangent(q, c, d, pitch, sense)).collect();
            let mut r = vec![(if t[0].z.abs() < 0.9 { t[0].cross(V3::Z) } else { t[0].cross(V3::X) }).unit()];
            for i in 0..n {
                let v1 = p[i + 1] - p[i];
                let c1 = v1.dot(v1);
                let rl = r[i] - v1 * (2.0 / c1 * v1.dot(r[i]));
                let tl = t[i] - v1 * (2.0 / c1 * v1.dot(t[i]));
                let v2 = t[i + 1] - tl;
                let c2 = v2.dot(v2);
                r.push(if c2 > 1e-30 { rl - v2 * (2.0 / c2 * v2.dot(rl)) } else { rl });
            }
            // Each station's frame (t, r, t × r) carries what the first one holds.
            let (t0, r0) = (t[0], r[0]);
            let s0 = t0.cross(r0);
            let back = |v: V3| crate::math::v3(v.dot(t0), v.dot(r0), v.dot(s0));
            let (bx, by, bz) = (back(V3::X), back(V3::Y), back(V3::Z));
            (0..=n)
                .map(|i| {
                    let (ti, ri) = (t[i], r[i].unit());
                    let si = ti.cross(ri);
                    let fwd = |l: V3| ti * l.x + ri * l.y + si * l.z;
                    let o = p[i] - fwd(back(p[0]));
                    Station { o, x: fwd(bx), y: fwd(by), z: fwd(bz) }
                })
                .collect()
        }
    };

    let mut part = Part { verts: vec![], tris: vec![], fids: vec![], faces: vec![] };
    let mut record: HashMap<u32, u32> = HashMap::new();
    let mut members: Vec<Vec<u32>> = vec![];
    let mut starts = vec![];
    for lp in &loops {
        let m = lp.pts.len() as u32;
        let base = part.verts.len() as u32;
        starts.push(base);
        part.verts.extend_from_slice(&lp.pts);
        for st in &stations[1..] {
            part.verts.extend(lp.pts.iter().map(|&q| st.place(q)));
        }
        for i in 0..n as u32 {
            let (a0, b0) = (base + i * m, base + (i + 1) * m);
            for k in 0..m {
                let k1 = (k + 1) % m;
                let curve = lp.seg[k as usize];
                let f = *record.entry(curve).or_insert_with(|| {
                    part.faces.push(Face::new(Surface::Free { kind: "BSPLINE" }, op, src));
                    members.push(vec![]);
                    part.faces.len() as u32 - 1
                });
                part.tris.push([a0 + k, a0 + k1, b0 + k1]);
                part.tris.push([a0 + k, b0 + k1, b0 + k]);
                part.fids.extend([f, f]);
                members[f as usize].extend([a0 + k, a0 + k1, b0 + k1, b0 + k]);
            }
        }
    }

    // The ends: the profile's own triangles at the first copy, facing back, and at the last.
    let at = |station: usize, j: u32| -> u32 {
        let mut j = j;
        for (lp, &base) in loops.iter().zip(&starts) {
            let m = lp.pts.len() as u32;
            if j < m {
                return base + station as u32 * m + j;
            }
            j -= m;
        }
        unreachable!("a cap index past the profile's points")
    };
    let first = part.faces.len() as u32;
    let last = &stations[n];
    let end_n = last.place(up) - last.place(V3::ZERO);
    part.faces.push(Face::new(Surface::Plane { p: loops[0].pts[0], n: -up }, op, src));
    part.faces.push(Face::new(Surface::Plane { p: last.place(loops[0].pts[0]), n: end_n.unit() }, op, src));
    for t in &cap {
        part.tris.push([at(0, t[0]), at(0, t[2]), at(0, t[1])]);
        part.fids.push(first);
        part.tris.push([at(n, t[0]), at(n, t[1]), at(n, t[2])]);
        part.fids.push(first + 1);
    }

    if signed_volume(&part.verts, &part.tris) < 0.0 {
        for t in &mut part.tris {
            t.swap(1, 2);
        }
        for f in &mut part.faces {
            if let Surface::Plane { n, .. } = &mut f.surface {
                *n = -*n;
            }
        }
    }

    // A wall whose every vertex keeps one distance from the axis is a cylinder about it.
    for (f, ids) in members.iter().enumerate() {
        let radius = |k: &u32| (part.verts[*k as usize] - c).reject(d).norm();
        let r0 = radius(&ids[0]);
        if r0 > 1e-9 && ids.iter().all(|k| (radius(k) - r0).abs() <= 1e-6) {
            part.faces[f].surface = Surface::Cylinder { p: c, d: canonical_axis(d), r: r0 };
        }
    }
    Ok(part)
}

impl Solid {
    /// `region` carried by a screw motion about the axis through `c` along `d`: `turns` turns,
    /// counterclockwise about `d` when positive and clockwise when negative, rising `pitch` along
    /// `d` per turn. Capped at both ends.
    #[track_caller]
    pub fn screw(region: &Region, c: V3, d: V3, pitch: f64, turns: f64) -> Result<Solid> {
        Ok(helical(region, Carry::Screw, c, d, pitch, turns, Location::caller(), "screw")?.solid())
    }

    /// `region` carried along the helix through `start` about the axis through `c` along `d` —
    /// `turns` turns, counterclockwise about `d` when positive, rising `pitch` per turn — in a
    /// rotation-minimizing frame. Capped at both ends.
    #[track_caller]
    pub fn helix_sweep(region: &Region, start: V3, c: V3, d: V3, pitch: f64, turns: f64) -> Result<Solid> {
        let carry = Carry::Minimal(start);
        Ok(helical(region, carry, c, d, pitch, turns, Location::caller(), "helix sweep")?.solid())
    }
}

impl Plane {
    /// `profile`, drawn in this plane's coordinates, carried by a screw motion (`Solid::screw`).
    #[track_caller]
    pub fn screw(&self, profile: &Profile, c: V3, d: V3, pitch: f64, turns: f64) -> Result<Solid> {
        Ok(helical(&profile.place(self), Carry::Screw, c, d, pitch, turns, Location::caller(), "screw")?.solid())
    }

    /// `profile`, drawn in this plane's coordinates, carried along the helix through the plane's
    /// origin in a rotation-minimizing frame (`Solid::helix_sweep`).
    #[track_caller]
    pub fn helix_sweep(&self, profile: &Profile, c: V3, d: V3, pitch: f64, turns: f64) -> Result<Solid> {
        let carry = Carry::Minimal(self.origin);
        Ok(helical(&profile.place(self), carry, c, d, pitch, turns, Location::caller(), "helix sweep")?.solid())
    }
}
