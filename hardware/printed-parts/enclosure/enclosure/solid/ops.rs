//! The kernel solids each plan operation stands for.
use crate::plan::{Bounds, Flange, FlankVents, HandholdAir, P2, P3, Seg as PlanSeg, Step};
use anyhow::{Result, ensure};
use hsm_kernel::*;
use manifold_csg::Manifold;
use std::f64::consts::PI;
use std::panic::Location;

fn p2(p: P2) -> V2 {
    v2(p[0], p[1])
}
fn p3(p: P3) -> V3 {
    v3(p[0], p[1], p[2])
}
pub fn corners(b: &Bounds) -> (V3, V3) {
    (v3(b[0], b[2], b[4]), v3(b[1], b[3], b[5]))
}

fn extruded(axis: usize, z: P2, outline: Loop) -> Result<Solid> {
    let (plane, distance) = match axis {
        0 => (Plane::YZ.at(v3(z[0], 0., 0.)), z[1] - z[0]),
        1 => (Plane::XZ.at(v3(0., z[0], 0.)), -(z[1] - z[0])),
        _ => (Plane::XY.at(v3(0., 0., z[0])), z[1] - z[0]),
    };
    plane.extrude(&Profile::new(outline), distance)
}

/// A section extruded over its span; `round` fillets the named vertices, `offset` grows it.
pub fn prism(
    axis: usize,
    span: P2,
    section: &[P2],
    round: Option<(&[usize], f64)>,
    offset: Option<f64>,
) -> Result<Solid> {
    let points: Vec<V2> = section.iter().map(|&p| p2(p)).collect();
    let mut outline = Loop::polygon(&points);
    if let Some((vertices, radius)) = round.filter(|&(_, radius)| radius > 0.) {
        // A plan names vertices; the kernel names the segment ending there.
        let corners: Vec<usize> = vertices
            .iter()
            .map(|&k| (k + points.len() - 1) % points.len())
            .collect();
        outline = outline.fillet_corners(&corners, radius)?;
    }
    if let Some(offset) = offset {
        outline = outline.ccw().offset(offset, true)?;
    }
    extruded(axis, span, outline)
}

pub fn rounded_box(b: &Bounds, radius: f64) -> Result<Solid> {
    let (lo, hi) = corners(b);
    Plane::XY
        .at(v3((lo.x + hi.x) / 2., (lo.y + hi.y) / 2., lo.z))
        .extrude(
            &Profile::new(Loop::rounded_rect(
                V2::ZERO,
                hi.x - lo.x,
                hi.y - lo.y,
                radius,
            )?),
            hi.z - lo.z,
        )
}

fn base(axis: usize, centre: P2, start: f64) -> (V3, V3) {
    let mut p = [0.; 3];
    let mut a = [0.; 3];
    a[axis] = 1.;
    p[axis] = start;
    let other: Vec<_> = (0..3).filter(|&j| j != axis).collect();
    p[other[0]] = centre[0];
    p[other[1]] = centre[1];
    (V3::from(p), V3::from(a))
}

pub fn cylinder(axis: usize, radius: f64, centre: P2, span: P2) -> Result<Solid> {
    let (p, a) = base(axis, centre, span[0]);
    Solid::cylinder(p, a, radius, span[1] - span[0])
}

pub fn cone(axis: usize, centre: P2, radii: P2, span: P2) -> Result<Solid> {
    let (p, a) = base(axis, centre, span[0]);
    Solid::cone(p, a, radii[0], radii[1], span[1] - span[0])
}

/// A cylinder whose circle breaks at its stations as well as its quarter points.
pub fn stationed_cylinder(
    axis: usize,
    radius: f64,
    centre: P2,
    span: P2,
    stations: P2,
) -> Result<Solid> {
    let c = p2(centre);
    let r = radius;
    let mut angles = stations.to_vec();
    angles.extend([0., PI / 2., PI, 3. * PI / 2.]);
    for a in &mut angles {
        *a = a.rem_euclid(2. * PI);
    }
    angles.sort_by(f64::total_cmp);
    angles.dedup_by(|a, b| (*a - *b).abs() < 1e-12);
    angles.push(2. * PI);
    let at = |a: f64| c + v2(r * math::cos(a), r * math::sin(a));
    let mut profile = Pen::new(at(0.));
    for pair in angles.windows(2) {
        profile = profile.arc_through(at((pair[0] + pair[1]) / 2.), at(pair[1]))?;
    }
    extruded(axis, span, profile.close()?)
}

pub fn handhold_cutter(b: &Bounds, radius: f64) -> Result<Solid> {
    let (lo, hi) = corners(b);
    let outline = Loop::polygon(&[
        v2(lo.y, lo.z),
        v2(hi.y, lo.z),
        v2(hi.y, hi.z),
        v2(lo.y, hi.z),
    ])
    .fillet_corners(&[1, 2], radius)?;
    Plane::YZ
        .at(v3(lo.x, 0.0, 0.0))
        .extrude(&Profile::new(outline), hi.x - lo.x)
}

// The handhold's loft takes GCPnts_TangentialDeflection's stations on its ellipses,
// including the adjusted penultimate point, before ruling adjacent sections. OCCT 7.8.1
// algorithm reference:
// https://github.com/Open-Cascade-SAS/OCCT/blob/V7_8_1/src/GCPnts/GCPnts_TangentialDeflection.cxx
fn ellipse_stations(edge: LoftEdge) -> Result<Vec<f64>> {
    let LoftEdge::Conic { c, x, y, t0, t1 } = edge else {
        return Ok(vec![0.0, 1.0]);
    };
    let first = t0.min(t1);
    let last = t0.max(t1);
    let at = |u: f64| c + x * math::cos(u) + y * math::sin(u);
    let step = |u: f64| {
        let tangent = x * (-math::sin(u)) + y * math::cos(u);
        let second = x * (-math::cos(u)) - y * math::sin(u);
        (8.0 * LINEAR / (second.cross(tangent).norm() / tangent.norm())).sqrt()
    };
    let mut du = step(first).min((last - first) / 3.0);
    let mut saved = du;
    let mut u1 = first;
    let mut u2 = first;
    let mut previous = at(first);
    let mut marked = vec![first];
    let mut check_saved = false;
    let mut more = true;
    let mut guard = 0;
    while more {
        guard += 1;
        ensure!(guard < 100000, "handhold ellipse station convergence");
        u2 += du;
        if u2 >= last {
            u2 = last;
            du = u2 - u1;
            saved = du;
        }
        let mut current = at(u2);
        let mut large = false;
        let mut small = false;
        let (fcoef, acoef) = loop {
            let mid = (u1 + u2) * 0.5;
            let p = at(mid);
            let chord = current - previous;
            let half = p - previous;
            let fcoef = if chord.norm() > 1e-7 {
                chord.cross(half).norm() / (chord.norm() * LINEAR)
            } else {
                0.0
            };
            let last_half = current - p;
            let acoef = if last_half.norm() > 1e-7 && half.norm() > 1e-7 {
                last_half.cross(half).norm() / (last_half.norm() * half.norm() * (ANGULAR / 2.0))
            } else {
                0.0
            };
            let coef = fcoef.max(acoef);
            if check_saved && coef < 0.55 {
                check_saved = false;
                du = saved;
                u2 = (u1 + du).min(last);
                current = at(u2);
                continue;
            }
            if coef <= 1.0 {
                if (last - u2).abs() < 1e-9 {
                    marked.push(last);
                    more = false;
                    break (fcoef, acoef);
                }
                if coef >= 0.55 || large {
                    marked.push(u2);
                    previous = current;
                    check_saved = true;
                    break (fcoef, acoef);
                }
                if small {
                    previous = current;
                    break (fcoef, acoef);
                }
                small = true;
                du += ((u2 - u1) * (1.0 - coef)).min(du / 3.0);
                u2 = (u1 + du).min(last);
                current = at(u2);
            } else if coef >= 1.5 {
                if (previous - at(*marked.last().unwrap())).norm() > 1e-7 {
                    marked.push(u1);
                }
                u2 = mid;
                du = u2 - u1;
                current = p;
            } else {
                du *= 0.9;
                u2 = u1 + du;
                current = at(u2);
                large = true;
            }
        };
        du = u2 - u1;
        if more {
            if u1 > first {
                du = if fcoef > acoef {
                    step(u2)
                } else {
                    (du + (du - saved) * (du / saved)).clamp(0.75 * saved, 1.5 * saved)
                };
            }
            if du < 1e-9 {
                du = last - u2;
                if du < 1e-9 {
                    marked.push(last);
                    more = false;
                } else if du / 3.0 > 1e-9 {
                    du /= 3.0;
                }
            }
            u1 = u2;
            saved = du;
        }
    }
    if marked.len() >= 3 {
        let n = marked.len();
        marked[n - 2] = (last + marked[n - 3]) * 0.5;
    }
    if t0 > t1 {
        marked.reverse();
    }
    Ok(marked.into_iter().map(|u| (u - t0) / (t1 - t0)).collect())
}

fn handhold_loft(sections: &[LoftSection]) -> Result<Solid> {
    let sections = compatible(sections)?;
    let mut regions = vec![];
    for section in &sections {
        let mut points = vec![];
        let mut segment = vec![];
        let mut curves = vec![];
        for (k, &edge) in section.edges.iter().enumerate() {
            let stations = match edge {
                LoftEdge::Line { .. } => vec![0.0, 1.0],
                _ => ellipse_stations(edge)?,
            };
            for &t in &stations[..stations.len() - 1] {
                points.push(edge.at(t));
                segment.push(k as u32);
            }
            curves.push(match edge {
                LoftEdge::Line { .. } => Curve::Line,
                _ => Curve::Free("ELLIPSE"),
            });
        }
        regions.push(Region {
            loops: vec![profile::RLoop {
                pts: points,
                seg: segment,
            }],
            curves,
        });
    }
    // Each pair of sections is ruled.
    Solid::loft(&regions)
}

/// The rounded show edges a handhold's opening takes, in the west handhold's frame.
pub fn handhold_air(h: &HandholdAir) -> Result<Solid> {
    let (bed, roof, crown) = (h.bed, h.roof, h.crown);
    let y = h.y;
    let (corner, radius, depth) = (h.corner, h.radius, h.depth);
    let slope = h.slope;
    let height = radius - radius * slope / (1.0_f64 + slope * slope).sqrt();
    let foot = radius - radius / (1.0_f64 + slope * slope).sqrt() + slope * height;
    let tangent_depth = foot - slope * height;
    let mut depths: Vec<f64> = (0..=90)
        .step_by(2)
        .map(|a| radius * (1.0 - math::sin(math::radians(a as f64))))
        .collect();
    depths.extend([0.0, radius, foot, tangent_depth, foot - 0.01, foot + 0.01]);
    depths.sort_by(f64::total_cmp);
    depths.dedup_by(|a, b| *a == *b);
    let (left, right, zl) = (y[0] + corner, y[1] - corner, roof - corner);
    let section = |d: f64, ceiling: bool| -> LoftSection {
        let side = radius - (radius * radius - (radius - d).powi(2)).max(0.0).sqrt();
        let top = if d <= tangent_depth {
            side
        } else {
            ((foot - d) / slope).max(0.0)
        };
        let at = |y, z| v3(d, y, z);
        let line = |a, b| LoftEdge::Line { a, b };
        let arc = |cy, a0, a1| LoftEdge::Conic {
            c: at(cy, zl),
            x: v3(0.0, corner + side, 0.0),
            y: v3(0.0, 0.0, corner + top),
            t0: math::radians(a0),
            t1: math::radians(a1),
        };
        let low = bed - 1.0;
        let mut edges = vec![
            line(at(y[0] - side, low), at(y[1] + side, low)),
            line(at(y[1] + side, low), at(y[1] + side, zl)),
            arc(right, 0.0, 90.0),
        ];
        if ceiling {
            edges.push(line(at(right, roof + top), at(left, roof + top)));
        } else {
            edges.extend([
                line(at(right, roof), at(right, zl)),
                line(at(right, zl), at(left, zl)),
                line(at(left, zl), at(left, roof)),
            ]);
        }
        edges.extend([
            arc(left, 90.0, 180.0),
            line(at(y[0] - side, zl), at(y[0] - side, low)),
        ]);
        LoftSection::new(edges)
    };
    let with_roof: Vec<_> = depths
        .iter()
        .filter(|&&d| d <= foot)
        .map(|&d| section(d, true))
        .collect();
    let returns: Vec<_> = depths
        .iter()
        .filter(|&&d| d >= foot)
        .map(|&d| section(d, false))
        .collect();
    let roof_air = handhold_loft(&with_roof)?;
    let side_air = handhold_loft(&returns)?;
    let basic = handhold_cutter(&[-1.0, h.cutter_depth, y[0], y[1], bed - 1.0, roof], corner)?;
    // The blank's share of the ordinary opening and both rim lofts.
    let end = h.end_stock;
    let blank = Solid::cuboid(v3(0.0, y[0] - end, bed), v3(depth, y[1] + end, crown));
    basic.union(&roof_air)?.union(&side_air)?.intersect(&blank)
}

/// The tools for vent courses whose interior probes clear the stock.
pub fn flank_vent_cuts(v: &FlankVents, stock: &Solid, cutters: &[&Solid]) -> Result<Solid> {
    let columns = &v.columns;
    let courses = &v.courses;
    let clearance = v.clearance;
    let tolerance = v.tolerance;
    let minimum = v.island_min;
    let sides: Vec<f64> = columns.iter().map(|column| column.side).collect();
    let mut present = Vec::new();
    for column in columns {
        let (lo, hi) = corners(&column.probe);
        let occupied = stock
            .intersect(&Solid::cuboid(lo, hi))?
            .components()
            .iter()
            .map(|component| {
                let bounds = component.bounds();
                (bounds.min.z - clearance, bounds.max.z + clearance)
            })
            .collect::<Vec<_>>();
        present.push(
            courses
                .iter()
                .map(|course| {
                    !occupied
                        .iter()
                        .any(|&(lo, hi)| course[0].max(lo) < course[1].min(hi) - tolerance)
                })
                .collect::<Vec<_>>(),
        );
    }
    let mut selected = Vec::new();
    for (i, column) in columns.iter().enumerate() {
        let tools = &column.cutters;
        ensure!(tools.len() == courses.len(), "vent course cutters");
        for k in 0..courses.len() {
            let neighbours = usize::from(i > 0 && sides[i - 1] == sides[i] && present[i - 1][k])
                + usize::from(
                    i + 1 < columns.len() && sides[i + 1] == sides[i] && present[i + 1][k],
                );
            if present[i][k] && neighbours >= minimum.saturating_sub(1) {
                selected.push(cutters[tools[k]].clone());
            }
        }
    }
    if selected.is_empty() {
        return Ok(Solid::empty());
    }
    Ok(Solid::compose(&selected))
}

pub fn bezier_prism(axis: usize, span: P2, segments: &[PlanSeg]) -> Result<Solid> {
    let edges = segments
        .iter()
        .map(|s| match *s {
            PlanSeg::Line(a, b) => Seg::Line { a: p2(a), b: p2(b) },
            PlanSeg::Cubic(a, c1, c2, b) => Seg::Cubic {
                a: p2(a),
                c1: p2(c1),
                c2: p2(c2),
                b: p2(b),
            },
        })
        .collect();
    extruded(axis, span, Loop::new(edges)?)
}

/// The pump skirt's explicit, planar ruled correspondence. Repeated points are collapsed
/// transition vertices, not epsilon edges.
pub fn ruled_stack(sections: &[Vec<P3>], source: &'static Location<'static>) -> Result<Solid> {
    let sections: Vec<Vec<V3>> = sections
        .iter()
        .map(|row| row.iter().map(|&p| p3(p)).collect())
        .collect();
    ensure!(sections.len() >= 2, "a ruled stack needs two sections");
    let n = sections[0].len();
    ensure!(
        n >= 3 && sections.iter().all(|row| row.len() == n),
        "ruled correspondence count"
    );
    let rise = sections.last().unwrap()[0].z - sections[0][0].z;
    ensure!(rise != 0.0, "a ruled stack needs distinct end planes");
    let area: f64 = (0..n)
        .map(|i| {
            let (a, b) = (sections[0][i], sections[0][(i + 1) % n]);
            a.x * b.y - b.x * a.y
        })
        .sum();
    let flip_side = (rise > 0.0) != (area < 0.0);
    let verts: Vec<_> = sections.iter().flatten().copied().collect();
    let mut tris = Vec::new();
    let mut faces = Vec::new();
    let mut face_of = Vec::new();
    let src: Src = source;
    for (i, sense) in [(0, -rise.signum()), (sections.len() - 1, rise.signum())] {
        let row = &sections[i];
        let flat = row.iter().map(|p| v2(p.x, p.y)).collect();
        let cap = hsm_kernel::triangulate::triangulate(&[flat])?;
        let face = faces.len() as u32;
        faces.push(Face::new(
            Surface::Plane {
                p: row[0],
                n: V3::Z * sense,
            },
            "ruled skirt cap",
            src,
        ));
        for mut t in cap {
            t.iter_mut().for_each(|k| *k += (i * n) as u32);
            if sense < 0.0 {
                t.swap(1, 2);
            }
            tris.push(t);
            face_of.push(face);
        }
    }
    for i in 0..sections.len() - 1 {
        for k in 0..n {
            let next = (k + 1) % n;
            let ids = [
                (i * n + k) as u32,
                ((i + 1) * n + k) as u32,
                ((i + 1) * n + next) as u32,
                (i * n + next) as u32,
            ];
            let mut triangles = Vec::new();
            for mut t in [[ids[0], ids[1], ids[2]], [ids[0], ids[2], ids[3]]] {
                if flip_side {
                    t.swap(1, 2);
                }
                let (a, b, c) = (
                    verts[t[0] as usize],
                    verts[t[1] as usize],
                    verts[t[2] as usize],
                );
                if (b - a).cross(c - a).norm() > 1e-12 {
                    triangles.push(t);
                }
            }
            if triangles.is_empty() {
                continue;
            }
            let t = triangles[0];
            let (a, b, c) = (
                verts[t[0] as usize],
                verts[t[1] as usize],
                verts[t[2] as usize],
            );
            let normal = (b - a).cross(c - a).unit();
            ensure!(
                ids.iter()
                    .all(|&j| (verts[j as usize] - a).dot(normal).abs() < 1e-7),
                "the ruled skirt face is no longer planar"
            );
            let face = faces.len() as u32;
            faces.push(Face::new(
                Surface::Plane { p: a, n: normal },
                "ruled skirt",
                src,
            ));
            for t in triangles {
                tris.push(t);
                face_of.push(face);
            }
        }
    }
    Solid::from_mesh(&verts, &tris, &face_of, &faces)
}

pub fn arc_prism(axis: usize, span: P2, start: P2, segments: &[Step]) -> Result<Solid> {
    let mut pen = Pen::new(p2(start));
    for segment in segments {
        pen = match *segment {
            Step::Arc(mid, end) => pen.arc_through(p2(mid), p2(end))?,
            Step::Line(p) => pen.line_to(p2(p)),
        };
    }
    extruded(axis, span, pen.close()?)
}

/// The C14 inlet's flange outline, grown by its clearance, through the rear panel.
pub fn flange(f: &Flange) -> Result<Solid> {
    let a = p2(f.shoulder);
    let m = p2(f.round_mid);
    let q = p2(f.tangent_start);
    let t = p2(f.ear_tangent);
    let nose = p2(f.nose);
    let reflect = |v: V2, x: f64, y: f64| v2(v.x * x, v.y * y);
    let outline = Pen::new(v2(-a.x, a.y))
        .line_to(a)
        .arc_through(m, q)?
        .line_to(t)
        .arc_through(nose, reflect(t, 1., -1.))?
        .line_to(reflect(q, 1., -1.))
        .arc_through(reflect(m, 1., -1.), reflect(a, 1., -1.))?
        .line_to(-a)
        .arc_through(-m, -q)?
        .line_to(-t)
        .arc_through(-nose, reflect(t, -1., 1.))?
        .line_to(reflect(q, -1., 1.))
        .arc_through(reflect(m, -1., 1.), reflect(a, -1., 1.))?
        .close()?;
    let outline = outline.ccw().offset(f.clearance, true)?;
    let z = f.span;
    Plane::XZ
        .at(v3(0., z[0], 0.))
        .extrude(&Profile::new(outline), -(z[1] - z[0]))
}

/// Radial runs `[x0, x1, radius]` turned about a Y axis through `centre` (X, Z).
pub fn turned(centre: P2, runs: &[P3]) -> Result<Solid> {
    let mut profile = vec![v2(runs[0][0], 0.)];
    for a in runs {
        for p in [v2(a[0], a[2]), v2(a[1], a[2])] {
            if (*profile.last().unwrap() - p).norm() > 1e-9 {
                profile.push(p);
            }
        }
    }
    profile.push(v2(runs.last().unwrap()[1], 0.));
    let c = centre;
    Ok(Plane::XY
        .revolve(&Profile::polygon(&profile), 360., V2::ZERO, v2(1., 0.))?
        .rotate(V3::ZERO, V3::Z, 90.)
        .translate(v3(c[0], 0., c[1])))
}

pub fn radial_profile(points: &[P2]) -> Result<Solid> {
    let points: Vec<V2> = points.iter().map(|&p| p2(p)).collect();
    ensure!(!points.is_empty(), "a radial profile has points");
    let mut profile = vec![v2(points[0].x, 0.)];
    profile.extend_from_slice(&points);
    profile.push(v2(points[points.len() - 1].x, 0.));
    Plane::XY.revolve(&Profile::polygon(&profile), 360., V2::ZERO, v2(1., 0.))
}

pub fn stadium(y: f64, z: f64, r: f64, fore: f64, aft: f64, x: P2) -> Result<Solid> {
    let (a, b) = (y - fore, y + aft);
    let outline = Pen::new(v2(a, z - r))
        .line_to(v2(b, z - r))
        .arc_through(v2(b + r, z), v2(b, z + r))?
        .line_to(v2(a, z + r))
        .arc_through(v2(a - r, z), v2(a, z - r))?
        .close()?;
    Plane::YZ
        .at(v3(x[0], 0., 0.))
        .extrude(&Profile::new(outline), x[1] - x[0])
}

pub fn stadium_profile(y: f64, z: f64, fore: f64, aft: f64, points: &[P2]) -> Result<Solid> {
    let rows: Vec<V2> = points.iter().map(|&p| p2(p)).collect();
    let (a, b) = (y - fore, y + aft);
    let mut pieces = Vec::new();
    for pair in rows.windows(2) {
        let (p, q) = (pair[0], pair[1]);
        let length = q.x - p.x;
        if length < 1.0e-8 {
            continue;
        }
        for cy in [a, b] {
            pieces.push(if (p.y - q.y).abs() < 1.0e-8 {
                Solid::cylinder(v3(p.x, cy, z), V3::X, p.y, length)?
            } else {
                Solid::cone(v3(p.x, cy, z), V3::X, p.y, q.y, length)?
            });
        }
        if b - a > 1.0e-8 {
            let outline = [
                v2(p.x, z - p.y),
                v2(q.x, z - q.y),
                v2(q.x, z + q.y),
                v2(p.x, z + p.y),
            ];
            pieces.push(
                Plane::XZ
                    .at(v3(0., a, 0.))
                    .extrude(&Profile::polygon(&outline), -(b - a))?,
            );
        }
    }
    ensure!(!pieces.is_empty(), "a stadium profile has a run");
    let mut result = pieces.remove(0);
    for piece in pieces {
        result = result.union(&piece)?;
    }
    Ok(result)
}

/// A kernel solid as Manifold takes it: float32 positions, its own triangles.
pub fn manifold(s: &Solid) -> Result<Manifold> {
    let vertices: Vec<f32> = s
        .verts()
        .iter()
        .flat_map(|p| p.to_array().map(|x| x as f32))
        .collect();
    let triangles: Vec<u32> = s.tris().iter().flatten().copied().collect();
    Ok(Manifold::from_mesh_f32(&vertices, 3, &triangles)?)
}

/// The shape read back from the float32 positions its STL stores.
pub fn quantized(shape: &Manifold) -> Result<Manifold> {
    let (v, props, t) = shape.to_mesh_f32();
    Ok(Manifold::from_mesh_f32(&v, props, &t)?)
}

/// A finished print stage keeps the positions and surface its STL stores.
pub fn print_solid(shape: &Manifold) -> Result<Solid> {
    let (vertices, stride, triangles) = shape.to_mesh_f32();
    let vertices: Vec<_> = vertices
        .chunks_exact(stride)
        .map(|p| v3(p[0] as f64, p[1] as f64, p[2] as f64))
        .collect();
    let triangles: Vec<_> = triangles
        .chunks_exact(3)
        .map(|t| [t[0], t[1], t[2]])
        .collect();
    let face = Face::new(
        Surface::Free { kind: "PRINT" },
        "print surface",
        std::panic::Location::caller(),
    );
    Solid::from_mesh(&vertices, &triangles, &vec![0; triangles.len()], &[face])
}

/// The binary STL of a fluted print surface.
pub fn print_stl_bytes(shape: &Manifold) -> Vec<u8> {
    let (v, props, t) = shape.to_mesh_f32();
    let mut out = Vec::with_capacity(84 + t.len() / 3 * 50);
    let mut header = [b' '; 80];
    let title = b"hsm enclosure print surface";
    header[..title.len()].copy_from_slice(title);
    out.extend_from_slice(&header);
    out.extend_from_slice(&(t.len() as u32 / 3).to_le_bytes());
    for triangle in t.chunks_exact(3) {
        let points: Vec<_> = triangle
            .iter()
            .map(|&i| {
                let k = i as usize * props;
                v3(v[k] as f64, v[k + 1] as f64, v[k + 2] as f64)
            })
            .collect();
        let normal = (points[1] - points[0]).cross(points[2] - points[0]).unit();
        for value in normal
            .to_array()
            .into_iter()
            .map(|x| x as f32)
            .chain(points.iter().flat_map(|p| p.to_array().map(|x| x as f32)))
        {
            out.extend_from_slice(&value.to_le_bytes());
        }
        out.extend_from_slice(&[0, 0]);
    }
    out
}
