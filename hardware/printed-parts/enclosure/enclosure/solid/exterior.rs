//! The exterior follows its circular columns, seam band and continuous print-oriented upper edge.
use crate::plan::Bounds;
use anyhow::{Result, ensure};
use hsm_enclosure_numbers::exterior::{Contour, Exterior};
use hsm_enclosure_numbers::structure::{Structure, transition};
use hsm_kernel::{Face, Solid, Surface, V3, v3};
use std::f64::consts::{FRAC_PI_2, PI};

/// The flute rail follows the authored walls and keeps the band and curved columns plain.
pub fn presentation(
    b: &hsm_enclosure_numbers::spec::Box,
    mut plain: Vec<Bounds>,
) -> (
    hsm_enclosure_numbers::field::Field,
    hsm_enclosure_numbers::field::Rail,
) {
    use hsm_enclosure_numbers::{
        field::{self, Rail},
        shell::FLUTE_COUNT,
    };
    let mut field = field::field(&b.outer);
    let Some(exterior) = b.exterior else {
        return (field, field::perimeter_rail(&b.outer, plain));
    };
    let mut plan = outline(&b.outer, exterior.contour(), 0.0);
    plan.dedup_by(|a, b| (a.point - b.point).norm() < 1e-9);
    if (plan[0].point - plan.last().unwrap().point).norm() < 1e-9 {
        plan.pop();
    }
    let mut offsets = vec![0.0];
    for i in 0..plan.len() {
        offsets.push(offsets[i] + (plan[(i + 1) % plan.len()].point - plan[i].point).norm());
    }
    let length = *offsets.last().unwrap();
    field.pitch = length / FLUTE_COUNT;
    let count = (length / field.across).ceil() as usize;
    let mut points = vec![];
    let mut normals = vec![];
    let mut distances = vec![];
    let mut edge = 0;
    for i in 0..count {
        let distance = length * i as f64 / count as f64;
        while edge + 1 < plan.len() && offsets[edge + 1] < distance {
            edge += 1;
        }
        let (a, b) = (plan[edge], plan[(edge + 1) % plan.len()]);
        let t = (distance - offsets[edge]) / (offsets[edge + 1] - offsets[edge]);
        let point = a.point + (b.point - a.point) * t;
        let normal = (a.normal + (b.normal - a.normal) * t).unit();
        points.push([point.x, point.y]);
        normals.push([normal.x, normal.y]);
        distances.push(distance);
    }
    let mut band = b.exterior_bounds();
    let centre = b.splits[0] + hsm_enclosure_numbers::catalog::running() / 2.0;
    band[4] = centre - exterior.band_height / 2.0;
    band[5] = centre + exterior.band_height / 2.0;
    plain.push(band);
    (
        field,
        Rail {
            s: distances,
            point: points,
            normal: normals,
            closed: true,
            band: None,
            plain,
        },
    )
}

#[derive(Clone, Copy)]
struct Station {
    point: V3,
    normal: V3,
}

/// The front-right quarter, with the standing circle fixed as the band moves the wall outward.
fn quarter(outer: &Bounds, contour: Contour, delta: f64) -> Vec<Station> {
    let (x, y, middle) = (outer[1], outer[2], (outer[2] + outer[3]) / 2.0);
    let (radius, root, projection) = (contour.radius, contour.root_radius, contour.projection);
    let (cx, cy) = (x + projection - radius, y - projection + radius);
    let d = (projection - delta).max(0.0);
    let reach = (d * (2.0 * (radius + root) - d)).max(0.0).sqrt();
    let (fx, fy, sx, sy) = (cx - reach, y - delta - root, x + delta + root, cy + reach);
    let (tx, ty) = (
        (radius * fx + root * cx) / (radius + root),
        (radius * fy + root * cy) / (radius + root),
    );
    let (ux, uy) = (
        (radius * sx + root * cx) / (radius + root),
        (radius * sy + root * cy) / (radius + root),
    );
    let front = (ty - fy).atan2(tx - fx);
    let (a, b) = ((ty - cy).atan2(tx - cx), (uy - cy).atan2(ux - cx));
    let side = (uy - sy).atan2(ux - sx).rem_euclid(2.0 * PI);
    let roots = hsm_kernel::rule::ring_count(root) / 8;
    let mut points = vec![Station {
        point: v3(0.0, y - delta, 0.0),
        normal: -V3::Y,
    }];
    for i in 0..roots {
        let angle = FRAC_PI_2 + (front - FRAC_PI_2) * i as f64 / roots as f64;
        points.push(Station {
            point: v3(fx + root * angle.cos(), fy + root * angle.sin(), 0.0),
            normal: v3(-angle.cos(), -angle.sin(), 0.0),
        });
    }
    // Shared standing-circle facets keep their angles as the band advances along them.
    for angle in hsm_kernel::rule::arc_angles(radius, -PI, FRAC_PI_2) {
        let angle = angle.clamp(a, b);
        points.push(Station {
            point: v3(cx + radius * angle.cos(), cy + radius * angle.sin(), 0.0),
            normal: v3(angle.cos(), angle.sin(), 0.0),
        });
    }
    for i in 0..roots {
        let angle = side + (PI - side) * i as f64 / roots as f64;
        points.push(Station {
            point: v3(sx + root * angle.cos(), sy + root * angle.sin(), 0.0),
            normal: v3(-angle.cos(), -angle.sin(), 0.0),
        });
    }
    points.push(Station {
        point: v3(x + delta, sy, 0.0),
        normal: V3::X,
    });
    points.push(Station {
        point: v3(x + delta, middle, 0.0),
        normal: V3::X,
    });
    points
}

fn outline(outer: &Bounds, contour: Contour, delta: f64) -> Vec<Station> {
    let quarter = quarter(outer, contour, delta);
    let mut points = quarter[..quarter.len() - 1].to_vec();
    let reflected_y = |s: &Station| Station {
        point: v3(s.point.x, outer[2] + outer[3] - s.point.y, 0.0),
        normal: v3(s.normal.x, -s.normal.y, 0.0),
    };
    points.extend(
        quarter
            .iter()
            .rev()
            .take(quarter.len() - 1)
            .map(reflected_y),
    );
    points.extend(quarter.iter().take(quarter.len() - 1).map(|s| {
        let s = reflected_y(s);
        Station {
            point: v3(-s.point.x, s.point.y, 0.0),
            normal: v3(-s.normal.x, s.normal.y, 0.0),
        }
    }));
    points.extend(
        quarter
            .iter()
            .rev()
            .take(quarter.len() - 1)
            .map(|s| Station {
                point: v3(-s.point.x, s.point.y, 0.0),
                normal: v3(-s.normal.x, s.normal.y, 0.0),
            }),
    );
    points
}

/// The roof and display retain their plane and their existing tangent blend.
fn roof(structure: &Structure, y: f64) -> f64 {
    let profile = &structure.profile;
    if y <= profile.end[0] {
        profile.start[1] + (y - profile.start[0]) * structure.angle.to_radians().tan()
    } else if y < profile.roof[0] {
        let radius = (profile.roof[0] - profile.end[0]) / structure.angle.to_radians().sin();
        structure.outer[5] - radius
            + (radius.powi(2) - (y - profile.roof[0]).powi(2))
                .max(0.0)
                .sqrt()
    } else {
        structure.outer[5]
    }
}

fn edge_drop(radius: f64, depth: f64) -> f64 {
    let (height, foot) = transition(radius);
    let slope = hsm_enclosure_numbers::catalog::outward_per_height();
    if depth <= foot - slope * height {
        radius - (radius.powi(2) - (radius - depth).powi(2)).max(0.0).sqrt()
    } else {
        ((foot - depth) / slope).max(0.0)
    }
}

#[derive(Clone, Copy)]
struct Point {
    point: V3,
    roof: f64,
    influence: f64,
}

fn clip_span(poly: &[Point], span: &[f64]) -> Vec<Point> {
    let mut result = vec![];
    for i in 0..poly.len() {
        let (a, b) = (poly[i], poly[(i + 1) % poly.len()]);
        if a.point.y >= span[0] && a.point.y <= span[1] {
            result.push(a);
        }
        let boundaries = if a.point.y < b.point.y {
            [span[0], span[1]]
        } else {
            [span[1], span[0]]
        };
        for y in boundaries {
            if y <= a.point.y.min(b.point.y) || y >= a.point.y.max(b.point.y) {
                continue;
            }
            // Every slab and adjacent triangle intersects the original edge in the same direction.
            let (a, b) = if a.point.y < b.point.y {
                (a, b)
            } else {
                (b, a)
            };
            let t = (y - a.point.y) / (b.point.y - a.point.y);
            let mut point = a.point + (b.point - a.point) * t;
            point.y = y;
            result.push(Point {
                point,
                roof: a.roof + (b.roof - a.roof) * t,
                influence: a.influence + (b.influence - a.influence) * t,
            });
        }
    }
    result
}

fn bridge(triangles: &mut Vec<[u32; 3]>, a: usize, b: usize, count: usize, inward: bool) {
    for i in 0..count {
        let j = (i + 1) % count;
        let pair = [[a + i, a + j, b + j], [a + i, b + j, b + i]];
        triangles.extend(pair.map(|t| {
            if inward {
                [t[0] as u32, t[2] as u32, t[1] as u32]
            } else {
                t.map(|v| v as u32)
            }
        }));
    }
}

/// The authored envelope is constructed before the cavities, joints and feature cuts.
pub fn envelope(structure: &Structure, contour: Contour) -> Result<Solid> {
    let mut plan = outline(&structure.outer, contour, 0.0);
    plan.dedup_by(|a, b| (a.point - b.point).norm() < 1e-9);
    if (plan[0].point - plan.last().unwrap().point).norm() < 1e-9 {
        plan.pop();
    }
    let count = plan.len();
    let mut points = vec![];
    let mut triangles = vec![];
    for s in &plan {
        points.push(Point {
            point: v3(s.point.x, s.point.y, structure.outer[4]),
            roof: roof(structure, s.point.y),
            influence: 0.0,
        });
    }
    for s in &plan {
        points.push(Point {
            point: v3(
                s.point.x,
                s.point.y,
                roof(structure, s.point.y) - contour.edge_radius,
            ),
            roof: roof(structure, s.point.y),
            influence: 1.0,
        });
    }
    bridge(&mut triangles, 0, count, count, false);
    let (height, foot) = transition(contour.edge_radius);
    let slope = hsm_enclosure_numbers::catalog::outward_per_height();
    let tangent = foot - slope * height;
    let angle = (1.0 - tangent / contour.edge_radius).acos();
    let steps = (angle / 0.025).ceil() as usize;
    let mut depths: Vec<f64> = (1..=steps)
        .map(|i| {
            let angle = angle * i as f64 / steps as f64;
            contour.edge_radius * (1.0 - angle.cos())
        })
        .collect();
    depths.push(foot);
    for depth in depths {
        let start = points.len();
        for s in &plan {
            let p = s.point - s.normal * depth;
            points.push(Point {
                point: v3(
                    p.x,
                    p.y,
                    roof(structure, p.y) - edge_drop(contour.edge_radius, depth),
                ),
                roof: roof(structure, p.y),
                influence: 1.0,
            });
        }
        bridge(&mut triangles, start - count, start, count, false);
    }
    let top = points.len() - count;
    for (start, up) in [(top, true), (0, false)] {
        let flat = points[start..start + count]
            .iter()
            .map(|p| hsm_kernel::v2(p.point.x, p.point.y))
            .collect();
        let cap = hsm_kernel::triangulate::triangulate(&[flat])?;
        triangles.extend(cap.into_iter().map(|t| {
            let t = t.map(|i| i + start as u32);
            if up { t } else { [t[0], t[2], t[1]] }
        }));
    }
    let radius =
        (structure.profile.roof[0] - structure.profile.end[0]) / structure.angle.to_radians().sin();
    let mut cuts = vec![structure.outer[2] - contour.projection - 1.0];
    for angle in
        hsm_kernel::rule::arc_angles(radius, FRAC_PI_2, FRAC_PI_2 + structure.angle.to_radians())
            .into_iter()
            .rev()
    {
        cuts.push(structure.profile.roof[0] + radius * angle.cos());
    }
    cuts.push(structure.outer[3] + contour.projection + 1.0);
    let mut vertices = vec![];
    let mut faces = vec![];
    for triangle in triangles {
        let source: Vec<Point> = triangle.map(|i| points[i as usize]).into();
        let low = source
            .iter()
            .map(|p| p.point.y)
            .fold(f64::INFINITY, f64::min);
        let high = source
            .iter()
            .map(|p| p.point.y)
            .fold(f64::NEG_INFINITY, f64::max);
        for span in cuts
            .windows(2)
            .filter(|span| span[0] <= high && span[1] >= low)
        {
            let polygon = clip_span(&source, span);
            if polygon.len() < 3 {
                continue;
            }
            let start = vertices.len() as u32;
            vertices.extend(polygon.iter().map(|p| {
                v3(
                    p.point.x,
                    p.point.y,
                    p.point.z + p.influence * (roof(structure, p.point.y) - p.roof),
                )
            }));
            for i in 1..polygon.len() - 1 {
                faces.push([start, start + i as u32, start + i as u32 + 1]);
            }
        }
    }
    let record = Face::new(
        Surface::Free { kind: "EXTERIOR" },
        "continuous exterior",
        std::panic::Location::caller(),
    );
    Solid::from_mesh(&vertices, &faces, &vec![0; faces.len()], &[record])
}

/// The band's closed stock overlaps the wall and is cut by the quadrant's later features.
pub fn band(outer: Bounds, centre: f64, exterior: Exterior) -> Result<Solid> {
    ensure!(exterior.valid(), "valid exterior dimensions");
    let contour = exterior.contour();
    let half = exterior.band_height / 2.0;
    let radius =
        (half.powi(2) + exterior.band_projection.powi(2)) / (2.0 * exterior.band_projection);
    let angle = (half / radius).asin();
    let steps = ((2.0 * angle) / 0.015).ceil() as usize;
    let base = outline(&outer, contour, 0.0);
    let count = base.len();
    let mut vertices = vec![];
    let mut triangles = vec![];
    for i in 0..=steps {
        let a = -angle + 2.0 * angle * i as f64 / steps as f64;
        let z = centre + radius * a.sin();
        let delta = (exterior.band_projection - radius + radius * a.cos()).max(0.0);
        vertices.extend(
            outline(&outer, contour, delta)
                .into_iter()
                .map(|p| v3(p.point.x, p.point.y, z)),
        );
        if i > 0 {
            bridge(&mut triangles, (i - 1) * count, i * count, count, false);
        }
    }
    let inner = vertices.len();
    let embed = hsm_enclosure_numbers::shell::WALL / 4.0;
    for z in [centre - half, centre + half] {
        vertices.extend(base.iter().map(|p| {
            let p = p.point - p.normal * embed;
            v3(p.x, p.y, z)
        }));
    }
    bridge(&mut triangles, inner, inner + count, count, true);
    for i in 0..count {
        let j = (i + 1) % count;
        triangles.extend([
            [j as u32, i as u32, (inner + i) as u32],
            [j as u32, (inner + i) as u32, (inner + j) as u32],
            [
                (steps * count + i) as u32,
                (steps * count + j) as u32,
                (inner + count + j) as u32,
            ],
            [
                (steps * count + i) as u32,
                (inner + count + j) as u32,
                (inner + count + i) as u32,
            ],
        ]);
    }
    let record = Face::new(
        Surface::Free {
            kind: "CIRCULAR_BAND",
        },
        "seam band",
        std::panic::Location::caller(),
    );
    Solid::from_mesh(&vertices, &triangles, &vec![0; triangles.len()], &[record])
}
