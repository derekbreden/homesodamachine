//! Solids built as triangles: prisms, drafted prisms, revolutions, boxes, cylinders, cones,
//! spheres, tori and hulls.
//!
//! Each builder makes vertices, triangles, a face index per triangle, and one record per face
//! naming the surface it lies on and the generator line that asked for it. A profile's segments
//! name the curves they came from (`Region`), so an arc becomes one cylinder face when extruded
//! and one torus or sphere when revolved, whatever number of segments the rule cut it into.
use crate::face::{Face, Src, Surface};
use crate::math::{TAU, V2, V3, atan2, cos, radians, sin, tan, v2, v3};
use crate::plane::Plane;
use crate::profile::{Curve, Loop, Pen, Profile, RLoop, Region};
use crate::rule::{arc_angles, axis_frame, canonical_axis, circle_points, plane_frame, ring_angles, ring_count};
use crate::solid::Solid;
use crate::triangulate::triangulate;
use anyhow::{Result, ensure};
use std::collections::HashMap;
use std::panic::Location;

/// A builder's triangles before they are a solid.
pub(crate) struct Part {
    pub verts: Vec<V3>,
    pub tris: Vec<[u32; 3]>,
    pub fids: Vec<u32>,
    pub faces: Vec<Face>,
}

impl Part {
    pub fn solid(self) -> Solid {
        Solid::built(self.verts, self.tris, self.fids, self.faces)
    }
}

pub(crate) fn signed_area(p: &[V2]) -> f64 {
    let n = p.len();
    (0..n).map(|i| p[i].cross(p[(i + 1) % n])).sum::<f64>() * 0.5
}

/// `lp` walked the other way, each segment keeping its curve.
pub(crate) fn reverse(lp: &RLoop) -> RLoop {
    let m = lp.pts.len();
    RLoop {
        pts: lp.pts.iter().rev().copied().collect(),
        seg: (0..m).map(|i| lp.seg[(2 * m - 2 - i) % m]).collect(),
    }
}

/// `lp` without its zero-length segments.
pub(crate) fn clean(lp: &RLoop) -> RLoop {
    let m = lp.pts.len();
    let keep: Vec<usize> = (0..m)
        .filter(|&i| (lp.pts[(i + 1) % m] - lp.pts[i]).norm() > 1e-9)
        .collect();
    RLoop {
        pts: keep.iter().map(|&i| lp.pts[i]).collect(),
        seg: keep.iter().map(|&i| lp.seg[i]).collect(),
    }
}

/// The outer loop counterclockwise about `normal` and the holes clockwise, with their points
/// in the frame `plane_frame(normal)`.
pub(crate) fn orient(loops: &[RLoop], normal: V3) -> (Vec<RLoop>, Vec<Vec<V2>>) {
    let (_, x, y) = plane_frame(normal);
    let mut out = vec![];
    let mut flat = vec![];
    for (i, lp) in loops.iter().enumerate() {
        let mut lp = lp.clone();
        let mut p2: Vec<V2> = lp.pts.iter().map(|p| v2(p.dot(x), p.dot(y))).collect();
        if (i == 0) != (signed_area(&p2) > 0.0) {
            lp = reverse(&lp);
            p2.reverse();
        }
        out.push(lp);
        flat.push(p2);
    }
    (out, flat)
}

pub(crate) fn cleaned(region: &Region) -> Result<Vec<RLoop>> {
    let loops: Vec<RLoop> = region.loops.iter().map(clean).collect();
    for lp in &loops {
        ensure!(lp.pts.len() >= 3, "a profile loop of {} points bounds nothing", lp.pts.len());
    }
    ensure!(!loops.is_empty(), "an empty profile");
    Ok(loops)
}

/// The profile `region` (outer loop first, on a plane of `normal`) swept straight along `vec`.
pub(crate) fn prism(region: &Region, normal: V3, vec: V3, src: Src, op: &'static str) -> Result<Part> {
    ensure!(vec.norm() > 1e-12, "{op} along nothing");
    let up = if vec.dot(normal) > 0.0 { normal.unit() } else { -normal.unit() };
    let (loops, flat) = orient(&cleaned(region)?, up);
    let cap = triangulate(&flat)?;
    let base: Vec<V3> = loops.iter().flat_map(|lp| lp.pts.iter().copied()).collect();
    let n = base.len() as u32;
    let mut verts = base.clone();
    verts.extend(base.iter().map(|&p| p + vec));
    let mut tris = vec![];
    let mut fids = vec![];
    for t in &cap {
        tris.push([t[0], t[2], t[1]]);
        fids.push(0);
    }
    for t in &cap {
        tris.push([t[0] + n, t[1] + n, t[2] + n]);
        fids.push(1);
    }
    let mut faces = vec![
        Face::new(Surface::Plane { p: base[0], n: -up }, op, src),
        Face::new(Surface::Plane { p: base[0] + vec, n: up }, op, src),
    ];
    let mut curve_face: HashMap<u32, u32> = HashMap::new();
    let mut off = 0u32;
    for lp in &loops {
        let m = lp.pts.len() as u32;
        for k in 0..m {
            let (i, j) = (off + k, off + (k + 1) % m);
            let curve = lp.seg[k as usize];
            let f = *curve_face.entry(curve).or_insert_with(|| {
                faces.push(Face::new(
                    side_surface(&region.curves[curve as usize], base[i as usize], base[j as usize], vec),
                    op,
                    src,
                ));
                faces.len() as u32 - 1
            });
            tris.push([i, j, j + n]);
            tris.push([i, j + n, i + n]);
            fids.extend([f, f]);
        }
        off += m;
    }
    Ok(Part { verts, tris, fids, faces })
}

fn side_surface(curve: &Curve, a: V3, b: V3, vec: V3) -> Surface {
    match *curve {
        Curve::Line => {
            let n = (b - a).cross(vec);
            Surface::Plane { p: a, n: n.unit() }
        }
        Curve::Circle { c, axis, r } if canonical_axis(axis).cross(vec.unit()).norm() < 1e-9 => {
            Surface::Cylinder { p: c, d: canonical_axis(axis), r }
        }
        _ => Surface::Free { kind: "EXTRUSION" },
    }
}

/// `prism` with its sides drafted `taper` degrees, as OCCT's draft prism drafts them: the
/// profile carried |vec| along its own normal toward `vec`, its region grown by
/// -|vec| tan(taper) at the far end, so a positive taper narrows it. A line stays straight and
/// its side is a plane; an arc keeps its center and its side is a cone.
pub(crate) fn drafted_prism(
    region: &Region,
    normal: V3,
    vec: V3,
    taper: f64,
    src: Src,
    op: &'static str,
) -> Result<Part> {
    let up = (if vec.dot(normal) > 0.0 { normal } else { -normal }).unit();
    let h = vec.norm();
    ensure!(h > 1e-12, "{op} along nothing");
    let grow = -h * tan(radians(taper));
    let (loops, _) = orient(&cleaned(region)?, up);
    let curves = &region.curves;
    let loops: Vec<RLoop> = loops.iter().map(|lp| finer(lp, curves, up, grow)).collect::<Result<_>>()?;
    let (_, x, y) = plane_frame(up);
    let flat = |pts: &[V3]| -> Vec<V2> { pts.iter().map(|p| v2(p.dot(x), p.dot(y))).collect() };
    let base: Vec<V3> = loops.iter().flat_map(|lp| lp.pts.iter().copied()).collect();
    let tops: Vec<Vec<V3>> = loops
        .iter()
        .map(|lp| drafted(lp, curves, up, grow).into_iter().map(|p| p + up * h).collect())
        .collect();
    let top: Vec<V3> = tops.concat();
    let n = base.len() as u32;
    let under = triangulate(&loops.iter().map(|lp| flat(&lp.pts)).collect::<Vec<_>>())?;
    let over = triangulate(&tops.iter().map(|t| flat(t)).collect::<Vec<_>>())?;
    let mut verts = base.clone();
    verts.extend_from_slice(&top);
    let mut tris = vec![];
    let mut fids = vec![];
    for t in &under {
        tris.push([t[0], t[2], t[1]]);
        fids.push(0);
    }
    for t in &over {
        tris.push([t[0] + n, t[1] + n, t[2] + n]);
        fids.push(1);
    }
    let mut faces = vec![
        Face::new(Surface::Plane { p: base[0], n: -up }, op, src),
        Face::new(Surface::Plane { p: top[0], n: up }, op, src),
    ];
    let mut curve_face: HashMap<u32, u32> = HashMap::new();
    let mut off = 0u32;
    for lp in &loops {
        let m = lp.pts.len() as u32;
        for k in 0..m {
            let (i, j) = (off + k, off + (k + 1) % m);
            let curve = lp.seg[k as usize];
            let f = *curve_face.entry(curve).or_insert_with(|| {
                let (a, b) = (base[i as usize], base[j as usize]);
                let surface = match curves[curve as usize] {
                    Curve::Circle { c, r, .. } => Surface::Cone {
                        p: c,
                        d: up,
                        r,
                        slope: bulge(c, a, b, up) * grow / h,
                    },
                    Curve::Line => {
                        let nrm = (b - a).cross(top[i as usize] - a);
                        Surface::Plane { p: a, n: nrm.unit() }
                    }
                    Curve::Free(_) => Surface::Free { kind: "BSPLINE" },
                };
                faces.push(Face::new(surface, op, src));
                faces.len() as u32 - 1
            });
            tris.push([i, j, j + n]);
            tris.push([i, j + n, i + n]);
            fids.extend([f, f]);
        }
        off += m;
    }
    Ok(Part { verts, tris, fids, faces })
}

/// +1 where the region's outside on the arc from `a` to `b` is away from its center `c`, -1
/// where it is toward it.
fn bulge(c: V3, a: V3, b: V3, up: V3) -> f64 {
    let out = (b - a).cross(up);
    if ((a + b) * 0.5 - c).dot(out) > 0.0 { 1.0 } else { -1.0 }
}

/// The loop's points moved `grow` out of its region in its own plane, each along the normals of
/// the curves it joins, a line's own and an arc's radius, mitred where they meet.
fn drafted(lp: &RLoop, curves: &[Curve], up: V3, grow: f64) -> Vec<V3> {
    let p = &lp.pts;
    let m = p.len();
    let chord: Vec<V3> = (0..m).map(|k| (p[(k + 1) % m] - p[k]).cross(up).unit()).collect();
    let normal = |k: usize, at: V3| -> V3 {
        match curves[lp.seg[k] as usize] {
            Curve::Circle { c, .. } => {
                let u = (at - c).reject(up).unit();
                if u.dot(chord[k]) > 0.0 { u } else { -u }
            }
            _ => chord[k],
        }
    };
    (0..m)
        .map(|k| {
            let (n_in, n_out) = (normal((k + m - 1) % m, p[k]), normal(k, p[k]));
            p[k] + (n_in + n_out) * (grow / (1.0 + n_in.dot(n_out)))
        })
        .collect()
}

/// `lp` with each segment on an arc the draft grows cut as fine as the rule cuts the arc at its
/// far end; refused where the draft closes an arc.
fn finer(lp: &RLoop, curves: &[Curve], up: V3, grow: f64) -> Result<RLoop> {
    let (p, seg) = (&lp.pts, &lp.seg);
    let m = p.len();
    let mut pts = vec![];
    let mut segs = vec![];
    for k in 0..m {
        pts.push(p[k]);
        segs.push(seg[k]);
        let Curve::Circle { c, r, .. } = curves[seg[k] as usize] else { continue };
        let (a, b) = (p[k], p[(k + 1) % m]);
        let far = r + bulge(c, a, b, up) * grow;
        ensure!(far > 1e-9, "a draft that closes an arc of radius {r}");
        let f = (ring_count(far) as f64 / ring_count(r) as f64 - 1e-9).ceil() as usize;
        if f <= 1 {
            continue;
        }
        let (v0, v1) = (a - c, b - c);
        let phi = atan2(v0.cross(v1).dot(up), v0.dot(v1));
        for i in 1..f {
            let t = phi * i as f64 / f as f64;
            pts.push(c + v0 * cos(t) + up.cross(v0) * sin(t));
            segs.push(seg[k]);
        }
    }
    Ok(RLoop { pts, seg: segs })
}

/// Triangles joining ring A to ring B, walking both in angle order.
fn zipper(a: &[u32], a_ang: &[f64], b: &[u32], b_ang: &[f64], closed: bool) -> Vec<[u32; 3]> {
    let (na, nb) = (a.len(), b.len());
    if na == 1 && nb == 1 {
        return vec![];
    }
    if na == 1 {
        let n = if closed { nb } else { nb - 1 };
        return (0..n).map(|k| [a[0], b[(k + 1) % nb], b[k]]).collect();
    }
    if nb == 1 {
        let n = if closed { na } else { na - 1 };
        return (0..n).map(|k| [a[k], a[(k + 1) % na], b[0]]).collect();
    }
    let end = TAU;
    let (last_i, last_j) = if closed { (na, nb) } else { (na - 1, nb - 1) };
    let (mut i, mut j) = (0, 0);
    let mut out = vec![];
    while i < last_i || j < last_j {
        let next_a = if i < last_i { if i + 1 < na { a_ang[i + 1] } else { end } } else { f64::INFINITY };
        let next_b = if j < last_j { if j + 1 < nb { b_ang[j + 1] } else { end } } else { f64::INFINITY };
        if next_a <= next_b {
            out.push([a[i], a[(i + 1) % na], b[j % nb]]);
            i += 1;
        } else {
            out.push([a[i % na], b[(j + 1) % nb], b[j]]);
            j += 1;
        }
    }
    out
}

/// The profile `region` (on a plane holding the axis) turned `degrees` about the axis through
/// `axis_p` along `axis_d`. A full turn puts every ring on the rule's angles.
pub(crate) fn revolve(
    region: &Region,
    axis_p: V3,
    axis_d: V3,
    degrees: f64,
    src: Src,
    op: &'static str,
) -> Result<Part> {
    let turn = radians(degrees);
    let full = (degrees.abs() - 360.0).abs() < 1e-9;
    ensure!(degrees.abs() > 1e-9 && degrees.abs() <= 360.0 + 1e-9, "{op} through {degrees}°");
    let (d, x, y) = axis_frame(axis_d);
    let sense = if axis_d.dot(d) > 0.0 { 1.0 } else { -1.0 };
    let loops = cleaned(region)?;
    let mut far = V3::ZERO;
    for lp in &loops {
        for &p in &lp.pts {
            let rad = (p - axis_p).reject(d);
            if rad.norm() > far.norm() {
                far = rad;
            }
        }
    }
    ensure!(far.norm() > 1e-9, "{op} of a profile on its own axis");
    let u = far.unit();
    let phi = atan2(u.dot(y), u.dot(x));
    let mut oriented: Vec<(RLoop, Vec<V2>)> = vec![];
    for (i, lp) in loops.iter().enumerate() {
        let mut p2 = vec![];
        for &p in &lp.pts {
            let rel = p - axis_p;
            let t = rel.dot(d);
            let rad = rel - d * t;
            let r = if rad.dot(u) >= -1e-9 { rad.norm() } else { -rad.norm() };
            ensure!(r >= -1e-9, "{op} profile crosses its axis at {}:{}", src.file(), src.line());
            p2.push(v2(r.max(0.0), t));
        }
        if (i == 0) != (signed_area(&p2) > 0.0) {
            p2.reverse();
            oriented.push((reverse(lp), p2));
        } else {
            oriented.push((lp.clone(), p2));
        }
    }
    let (a0, a1) = if full {
        (0.0, 0.0)
    } else if sense * turn > 0.0 {
        (phi, phi + turn.abs())
    } else {
        (phi - turn.abs(), phi)
    };
    let mut verts: Vec<V3> = vec![];
    let mut rings: Vec<Vec<(Vec<u32>, Vec<f64>)>> = vec![];
    for (_, p2) in &oriented {
        let mut lr = vec![];
        for q in p2 {
            let (r, t) = (q.x, q.y);
            let ang = if r <= 1e-9 {
                vec![a0]
            } else if full {
                ring_angles(r)
            } else {
                arc_angles(r, a0, a1)
            };
            let base = verts.len() as u32;
            for &a in &ang {
                verts.push(axis_p + d * t + (x * cos(a) + y * sin(a)) * r);
            }
            lr.push(((base..base + ang.len() as u32).collect(), ang));
        }
        rings.push(lr);
    }
    let mut tris = vec![];
    let mut fids = vec![];
    let mut faces: Vec<Face> = vec![];
    let mut curve_face: HashMap<u32, u32> = HashMap::new();
    for ((lp, p2), lr) in oriented.iter().zip(&rings) {
        let m = p2.len();
        for k in 0..m {
            let ((ia, aa), (ib, ab)) = (&lr[k], &lr[(k + 1) % m]);
            if ia.len() == 1 && ib.len() == 1 {
                continue;
            }
            let curve = lp.seg[k];
            let f = *curve_face.entry(curve).or_insert_with(|| {
                faces.push(Face::new(
                    revolve_surface(&region.curves[curve as usize], p2[k], p2[(k + 1) % m], axis_p, d),
                    op,
                    src,
                ));
                faces.len() as u32 - 1
            });
            for t in zipper(ia, aa, ib, ab, full) {
                tris.push(t);
                fids.push(f);
            }
        }
    }
    if !full {
        let flat: Vec<Vec<V2>> = oriented.iter().map(|(_, p2)| p2.clone()).collect();
        let cap = triangulate(&flat)?;
        let first: Vec<u32> = rings.iter().flat_map(|lr| lr.iter().map(|(i, _)| i[0])).collect();
        let last: Vec<u32> = rings.iter().flat_map(|lr| lr.iter().map(|(i, _)| *i.last().unwrap())).collect();
        let w0 = d.cross(x * cos(a0) + y * sin(a0));
        let w1 = d.cross(x * cos(a1) + y * sin(a1));
        let (fs, fe) = (faces.len() as u32, faces.len() as u32 + 1);
        faces.push(Face::new(Surface::Plane { p: verts[first[0] as usize], n: -w0 }, op, src));
        faces.push(Face::new(Surface::Plane { p: verts[last[0] as usize], n: w1 }, op, src));
        for t in &cap {
            tris.push([first[t[0] as usize], first[t[1] as usize], first[t[2] as usize]]);
            fids.push(fs);
        }
        for t in &cap {
            tris.push([last[t[0] as usize], last[t[2] as usize], last[t[1] as usize]]);
            fids.push(fe);
        }
    }
    Ok(Part { verts, tris, fids, faces })
}

fn revolve_surface(curve: &Curve, a: V2, b: V2, axis_p: V3, d: V3) -> Surface {
    let ((r0, t0), (r1, t1)) = ((a.x, a.y), (b.x, b.y));
    match *curve {
        Curve::Line => {
            if (r1 - r0).abs() < 1e-9 {
                Surface::Cylinder { p: axis_p, d, r: r0 }
            } else if (t1 - t0).abs() < 1e-9 {
                Surface::Plane { p: axis_p + d * t0, n: d * (r0 - r1).signum() }
            } else {
                Surface::Cone { p: axis_p + d * t0, d, r: r0, slope: (r1 - r0) / (t1 - t0) }
            }
        }
        Curve::Circle { c, r, .. } => {
            let rel = c - axis_p;
            let tc = rel.dot(d);
            let rc = (rel - d * tc).norm();
            let cc = axis_p + d * tc;
            if rc < 1e-9 {
                Surface::Sphere { c: cc, r }
            } else {
                Surface::Torus { c: cc, d, major: rc, minor: r }
            }
        }
        Curve::Free(_) => Surface::Free { kind: "REVOLUTION" },
    }
}

/// The box from `o` spanning `lx`, `ly`, `lz` along the unit axes `ex`, `ey`, `ez`.
pub(crate) fn cuboid(o: V3, ex: V3, ey: V3, ez: V3, l: V3, src: Src, op: &'static str) -> Part {
    let mut verts = vec![];
    for k in 0..2 {
        for j in 0..2 {
            for i in 0..2 {
                verts.push(o + ex * (i as f64 * l.x) + ey * (j as f64 * l.y) + ez * (k as f64 * l.z));
            }
        }
    }
    let quads = [[0, 2, 3, 1], [4, 5, 7, 6], [0, 1, 5, 4], [2, 6, 7, 3], [0, 4, 6, 2], [1, 3, 7, 5]];
    let normals = [-ez, ez, -ey, ey, -ex, ex];
    let mut tris = vec![];
    let mut fids = vec![];
    let mut faces = vec![];
    for (f, q) in quads.iter().enumerate() {
        tris.push([q[0], q[1], q[2]]);
        tris.push([q[0], q[2], q[3]]);
        fids.extend([f as u32, f as u32]);
        faces.push(Face::new(Surface::Plane { p: verts[q[0] as usize], n: normals[f] }, op, src));
    }
    Part { verts, tris, fids, faces }
}

/// The plane holding the axis through `c` along `a`, its x the axis frame's x and its y `a`.
fn meridian(c: V3, a: V3) -> Plane {
    let a = a.unit();
    let (_, x, _) = axis_frame(a);
    Plane { origin: c, x, y: a, z: x.cross(a) }
}

/// Planes through the facets of the hull of `pts`, each with its corners counterclockwise
/// about its outward normal.
fn hull_faces(pts: &[V3]) -> Result<Vec<(V3, Vec<usize>)>> {
    let n = pts.len();
    ensure!(n >= 4, "a hull of {n} points has no volume");
    let mut lo = pts[0];
    let mut hi = pts[0];
    for &p in pts {
        lo = lo.min(p);
        hi = hi.max(p);
    }
    let eps = 1e-9 * (hi - lo).norm().max(1.0);
    let mut planes: Vec<(V3, f64)> = vec![];
    for i in 0..n {
        for j in i + 1..n {
            for k in j + 1..n {
                let nrm = (pts[j] - pts[i]).cross(pts[k] - pts[i]);
                if nrm.norm() <= eps * eps {
                    continue;
                }
                let nrm = nrm.unit();
                let (mut above, mut below) = (false, false);
                for &p in pts {
                    let s = nrm.dot(p - pts[i]);
                    above |= s > eps;
                    below |= s < -eps;
                }
                if above && below {
                    continue;
                }
                let out = if above { -nrm } else { nrm };
                let off = out.dot(pts[i]);
                if !planes.iter().any(|(m, o)| (*m - out).norm() < 1e-9 && (o - off).abs() < eps) {
                    planes.push((out, off));
                }
            }
        }
    }
    ensure!(planes.len() >= 4, "the hull's points lie in one plane");
    let mut out = vec![];
    for (nrm, off) in planes {
        let on: Vec<usize> = (0..n).filter(|&i| (nrm.dot(pts[i]) - off).abs() <= eps).collect();
        let (_, x, y) = plane_frame(nrm);
        let mut ring: Vec<(V2, usize)> = on.iter().map(|&i| (v2(pts[i].dot(x), pts[i].dot(y)), i)).collect();
        ring.sort_by(|a, b| a.0.x.total_cmp(&b.0.x).then(a.0.y.total_cmp(&b.0.y)));
        // Andrew's monotone chain: the corners, counterclockwise.
        let mut h: Vec<(V2, usize)> = vec![];
        for pass in 0..2 {
            let start = h.len();
            let it: Box<dyn Iterator<Item = &(V2, usize)>> =
                if pass == 0 { Box::new(ring.iter()) } else { Box::new(ring.iter().rev()) };
            for &q in it {
                while h.len() >= start + 2 {
                    let (a, b) = (h[h.len() - 2].0, h[h.len() - 1].0);
                    if (b - a).cross(q.0 - a) <= 1e-12 {
                        h.pop();
                    } else {
                        break;
                    }
                }
                h.push(q);
            }
            h.pop();
        }
        out.push((nrm, h.into_iter().map(|(_, i)| i).collect()));
    }
    Ok(out)
}

pub(crate) fn hull(points: &[V3], src: Src, op: &'static str) -> Result<Part> {
    let mut pts: Vec<V3> = vec![];
    for &p in points {
        if !pts.contains(&p) {
            pts.push(p);
        }
    }
    let facets = hull_faces(&pts)?;
    let mut used = vec![u32::MAX; pts.len()];
    let mut verts = vec![];
    let mut tris = vec![];
    let mut fids = vec![];
    let mut faces = vec![];
    for (f, (nrm, ring)) in facets.iter().enumerate() {
        let idx: Vec<u32> = ring
            .iter()
            .map(|&i| {
                if used[i] == u32::MAX {
                    used[i] = verts.len() as u32;
                    verts.push(pts[i]);
                }
                used[i]
            })
            .collect();
        for k in 1..idx.len() - 1 {
            tris.push([idx[0], idx[k], idx[k + 1]]);
            fids.push(f as u32);
        }
        faces.push(Face::new(Surface::Plane { p: pts[ring[0]], n: *nrm }, op, src));
    }
    Ok(Part { verts, tris, fids, faces })
}

impl Solid {
    /// The axis-aligned box between corners `a` and `b`.
    #[track_caller]
    pub fn cuboid(a: V3, b: V3) -> Solid {
        let (lo, hi) = (a.min(b), a.max(b));
        cuboid(lo, V3::X, V3::Y, V3::Z, hi - lo, Location::caller(), "box").solid()
    }

    /// The profile `region`, on a plane of `normal`, swept straight along `vec`.
    #[track_caller]
    pub fn extrude(region: &Region, normal: V3, vec: V3) -> Result<Solid> {
        Ok(prism(region, normal, vec, Location::caller(), "extrude")?.solid())
    }

    /// The profile `region`, on a plane holding the axis, turned `degrees` about the axis
    /// through `axis_p` along `axis_d`, counterclockwise about `axis_d`.
    #[track_caller]
    pub fn revolve(region: &Region, axis_p: V3, axis_d: V3, degrees: f64) -> Result<Solid> {
        Ok(revolve(region, axis_p, axis_d, degrees, Location::caller(), "revolve")?.solid())
    }

    /// A cylinder of radius `r` standing `h` along `axis` from the center of its base `base`.
    #[track_caller]
    pub fn cylinder(base: V3, axis: V3, r: f64, h: f64) -> Result<Solid> {
        ensure!(r > 0.0 && h != 0.0, "a cylinder of radius {r} and height {h}");
        let a = axis.unit();
        let region = circle_region(base, a, r);
        Ok(prism(&region, a, a * h, Location::caller(), "cylinder")?.solid())
    }

    /// A cone frustum: radius `r1` at `base`, `r2` at `h` along `axis`; either may be 0.
    #[track_caller]
    pub fn cone(base: V3, axis: V3, r1: f64, r2: f64, h: f64) -> Result<Solid> {
        ensure!(h > 0.0 && r1 >= 0.0 && r2 >= 0.0 && r1 + r2 > 0.0, "a cone of radii {r1}, {r2} and height {h}");
        let pl = meridian(base, axis);
        let mut pts = vec![v2(0.0, 0.0)];
        if r1 > 0.0 {
            pts.push(v2(r1, 0.0));
        }
        if r2 > 0.0 {
            pts.push(v2(r2, h));
        }
        pts.push(v2(0.0, h));
        let region = Profile::polygon(&pts).place(&pl);
        Ok(revolve(&region, base, pl.y, 360.0, Location::caller(), "cone")?.solid())
    }

    #[track_caller]
    pub fn sphere(c: V3, r: f64) -> Result<Solid> {
        ensure!(r > 0.0, "a sphere of radius {r}");
        let pl = meridian(c, V3::Z);
        let half = Pen::new(v2(0.0, -r)).arc_center(V2::ZERO, v2(0.0, r), true).close()?;
        let region = Profile::new(half).place(&pl);
        Ok(revolve(&region, c, V3::Z, 360.0, Location::caller(), "sphere")?.solid())
    }

    /// A torus about the axis through `c` along `axis`: its tube of radius `minor` centered
    /// `major` from the axis.
    #[track_caller]
    pub fn torus(c: V3, axis: V3, major: f64, minor: f64) -> Result<Solid> {
        ensure!(major > minor && minor > 0.0, "a torus of radii {major}, {minor}");
        let pl = meridian(c, axis);
        let region = Profile::new(Loop::circle(v2(major, 0.0), minor)).place(&pl);
        Ok(revolve(&region, c, pl.y, 360.0, Location::caller(), "torus")?.solid())
    }

    /// A cylinder turned only `degrees` about its axis, from the axis frame's x direction.
    #[track_caller]
    pub fn cylinder_sector(base: V3, axis: V3, r: f64, h: f64, degrees: f64) -> Result<Solid> {
        ensure!(r > 0.0 && h > 0.0, "a cylinder of radius {r} and height {h}");
        let pl = meridian(base, axis);
        let region = Profile::polygon(&[v2(0.0, 0.0), v2(r, 0.0), v2(r, h), v2(0.0, h)]).place(&pl);
        Ok(revolve(&region, base, pl.y, degrees, Location::caller(), "cylinder")?.solid())
    }

    /// The convex hull of `points`, one plane face per facet plane.
    #[track_caller]
    pub fn hull(points: &[V3]) -> Result<Solid> {
        Ok(hull(points, Location::caller(), "hull")?.solid())
    }

    /// OCCT's wedge in the frame of `plane`: the base `dx` by `dz` on y = 0, the top on y = `dy`
    /// spanning x from `xmin` to `xmax` and z from `zmin` to `zmax`.
    #[allow(clippy::too_many_arguments)]
    #[track_caller]
    pub fn wedge(plane: &Plane, dx: f64, dy: f64, dz: f64, xmin: f64, zmin: f64, xmax: f64, zmax: f64) -> Result<Solid> {
        let local = [
            v3(0.0, 0.0, 0.0),
            v3(dx, 0.0, 0.0),
            v3(0.0, 0.0, dz),
            v3(dx, 0.0, dz),
            v3(xmin, dy, zmin),
            v3(xmax, dy, zmin),
            v3(xmin, dy, zmax),
            v3(xmax, dy, zmax),
        ];
        let w = plane.to_world();
        let pts: Vec<V3> = local.iter().map(|&p| w.point(p)).collect();
        Ok(hull(&pts, Location::caller(), "wedge")?.solid())
    }
}

/// One circle on the rule's points, as a region.
pub(crate) fn circle_region(c: V3, axis: V3, r: f64) -> Region {
    let pts = circle_points(c, axis, r);
    let n = pts.len();
    Region {
        loops: vec![RLoop { pts, seg: vec![0; n] }],
        curves: vec![Curve::Circle { c, axis: canonical_axis(axis), r }],
    }
}

impl Plane {
    /// `profile`, drawn in this plane's coordinates, extruded `distance` along its normal
    /// (against it when negative).
    #[track_caller]
    pub fn extrude(&self, profile: &Profile, distance: f64) -> Result<Solid> {
        ensure!(distance != 0.0, "an extrusion of no length");
        Ok(prism(&profile.place(self), self.z, self.z * distance, Location::caller(), "extrude")?.solid())
    }

    /// `profile` extruded `distance` each way from this plane.
    #[track_caller]
    pub fn extrude_both(&self, profile: &Profile, distance: f64) -> Result<Solid> {
        ensure!(distance > 0.0, "an extrusion of no length");
        let region = profile.place(&self.offset(-distance));
        Ok(prism(&region, self.z, self.z * (2.0 * distance), Location::caller(), "extrude")?.solid())
    }

    /// `profile` extruded `distance` along the normal with its sides drafted `taper` degrees
    /// inward.
    #[track_caller]
    pub fn extrude_drafted(&self, profile: &Profile, distance: f64, taper: f64) -> Result<Solid> {
        let region = profile.place(self);
        Ok(drafted_prism(&region, self.z, self.z * distance, taper, Location::caller(), "extrude")?.solid())
    }

    /// `profile` turned `degrees` about the axis from `axis_start` to `axis_end`, both in this
    /// plane's coordinates, as CadQuery's `revolve` turns it.
    #[track_caller]
    pub fn revolve(&self, profile: &Profile, degrees: f64, axis_start: V2, axis_end: V2) -> Result<Solid> {
        let (p, q) = (self.point(axis_start), self.point(axis_end));
        ensure!((q - p).norm() > 1e-12, "a revolve axis of no length");
        Ok(revolve(&profile.place(self), p, q - p, degrees, Location::caller(), "revolve")?.solid())
    }

    /// A box `l` by `w` by `h` along this plane's x, y and normal, centered on its origin.
    #[track_caller]
    pub fn cuboid(&self, l: f64, w: f64, h: f64) -> Solid {
        let o = self.origin - self.x * (l / 2.0) - self.y * (w / 2.0) - self.z * (h / 2.0);
        cuboid(o, self.x, self.y, self.z, v3(l, w, h), Location::caller(), "box").solid()
    }

    /// A cylinder of radius `r` on this plane's origin, `h` along its normal.
    #[track_caller]
    pub fn cylinder(&self, r: f64, h: f64) -> Result<Solid> {
        ensure!(r > 0.0 && h != 0.0, "a cylinder of radius {r} and height {h}");
        let region = circle_region(self.origin, self.z, r);
        Ok(prism(&region, self.z, self.z * h, Location::caller(), "cylinder")?.solid())
    }
}
