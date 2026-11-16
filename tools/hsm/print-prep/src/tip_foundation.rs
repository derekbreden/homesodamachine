//! Stands the Sculpted tip's shoulder on a scaffold and roof, as the base's foot stands on its
//! own. Level scaffold layers of walls rise from the bed under the shoulder's mating ring, clear
//! of the mating plug, and lean out with the plug where its flare runs under the ring. The roof's
//! courses lie parallel to the shoulder over them, the first in level lines each on the scaffold
//! beneath it, and a course of air parts the roof from the shoulder's first course.

use crate::base_foundation::Frame;
use crate::mesh::Mesh;
use crate::sloped_courses::{hatch, level_order, section, Point, Region};
use anyhow::{ensure, Result};

/// The scaffold's and roof's clearance from the plug, as the base's plugs keep from their sockets.
pub const PLUG_CLEAR: f64 = 0.5;
/// How far the roof reaches past the shoulder's rim, as the base's roof reaches past its rim.
pub const LIP: f64 = 2.0;
/// The width of the scaffold's and roof's lines, as the base's.
pub const WIDTH: f64 = 0.62;
/// The roof's courses.
pub const ROOF_COURSES: usize = 3;
/// The scaffold's walls along Y and the ties across them, as the base's scaffold spaces them.
const WALL_PITCH: f64 = 2.5;
const TIE_PITCH: f64 = 10.0;
/// How far a scaffold layer may reach past the layer beneath it.
const LEAN: f64 = 0.18;
/// How far down the slope past the ring the scaffold may stand, to reach the bed clear of the
/// plug's flare.
const REACH: f64 = 7.0;
/// The ledge's faces lie this close to the shoulder plane and face down it within this cosine.
const ON_PLANE: f64 = 0.01;
const FACING: f64 = 0.999;
/// The corners of each ellipse.
const ELLIPSE_POINTS: usize = 720;
/// A scaffold path shorter than this is not laid.
const SHORTEST: f64 = 1.0;
/// How far a region's outline may stray when its points are thinned.
const THIN: f64 = 0.01;

fn sub(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}

fn dot(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

fn cross(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
}

fn length(line: &[Point]) -> f64 {
    line.windows(2).map(|w| (w[1][0] - w[0][0]).hypot(w[1][1] - w[0][1])).sum()
}

/// The shoulder's mating ring: a frame in the shoulder plane centred on the ring, `a` across the
/// slope, `b` up it and `n` along its normal into the tip, and the plug's and rim's radii.
pub struct Ring {
    pub frame: Frame,
    pub inner: f64,
    pub outer: f64,
}

impl Ring {
    /// The ring the posed tip's downward ledge faces make in the shoulder plane through
    /// `origin`, turned `degrees` about X.
    pub fn measure(tip: &Mesh, origin: [f64; 3], degrees: f64) -> Result<Ring> {
        let (s, c) = degrees.to_radians().sin_cos();
        let normal = [0.0, s, c];
        let plane = |p: [f64; 3]| -> Point {
            let d = sub(p, origin);
            [d[0], -d[1] * c + d[2] * s]
        };
        let mut points: Vec<Point> = Vec::new();
        for face in &tip.faces {
            let [p, q, r] = face.map(|i| tip.vertices[i]);
            let n = cross(sub(q, p), sub(r, p));
            let size = dot(n, n).sqrt();
            if size < 1e-12 || -dot(n, normal) / size < FACING {
                continue;
            }
            if [p, q, r].iter().any(|v| dot(sub(*v, origin), normal).abs() > ON_PLANE) {
                continue;
            }
            points.extend([p, q, r].map(plane));
        }
        ensure!(points.len() >= 30, "the tip has no downward ledge in its shoulder plane");
        let (mut lo, mut hi) = ([f64::INFINITY; 2], [f64::NEG_INFINITY; 2]);
        for p in &points {
            for k in 0..2 {
                lo[k] = lo[k].min(p[k]);
                hi[k] = hi[k].max(p[k]);
            }
        }
        let centre = [(lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0];
        let radii: Vec<f64> = points.iter().map(|p| (p[0] - centre[0]).hypot(p[1] - centre[1])).collect();
        let inner = radii.iter().copied().fold(f64::INFINITY, f64::min);
        let outer = radii.iter().copied().fold(0.0, f64::max);
        ensure!(outer - inner > 1.0 && (hi[0] - lo[0] - 2.0 * outer).abs() < 0.05 && (hi[1] - lo[1] - 2.0 * outer).abs() < 0.05,
            "the shoulder's ledge is not a round ring");
        let frame = Frame {
            cx: origin[0] + centre[0],
            cy: origin[1] - centre[1] * c,
            cz: origin[2] + centre[1] * s,
            s,
            c,
            t: s / c,
            rim: [outer, outer],
        };
        Ok(Ring { frame, inner, outer })
    }

    /// The y at or below which the plane `n` along the normal stands over height `z`.
    pub fn plane_y(&self, n: f64, z: f64) -> f64 {
        let f = &self.frame;
        f.cy - f.b_at_height(z, n) * f.c + n * f.s
    }

    /// The height of the plane `n` along the normal over `y`.
    pub fn plane_z(&self, n: f64, y: f64) -> f64 {
        let f = &self.frame;
        let b = (f.cy + n * f.s - y) / f.c;
        f.cz + b * f.s + n * f.c
    }

    /// The ellipse the circle of radius `r` about the ring's axis in the plane `n` stands over,
    /// moved `shift` along Y.
    fn shadow(&self, r: f64, n: f64, shift: f64) -> Region {
        let f = &self.frame;
        let y = f.cy + n * f.s + shift;
        let ring: Vec<Point> = (0..ELLIPSE_POINTS)
            .map(|i| {
                let t = std::f64::consts::TAU * i as f64 / ELLIPSE_POINTS as f64;
                [f.cx + r * t.cos(), y + r * f.c * t.sin()]
            })
            .collect();
        Region::from_rings(&[ring])
    }

    /// What stands over the plate under the roof's ring, whose ceiling is `ceiling` along the
    /// normal, and that with the stretch down the slope past it the scaffold may lean out on.
    pub fn footprint(&self, ceiling: f64) -> (Region, Region) {
        let outer = self.shadow(self.outer + LIP, ceiling, 0.0);
        let annulus = outer.minus(&self.shadow(self.inner + PLUG_CLEAR, ceiling, 0.0));
        let crescent = self.shadow(self.outer + LIP, ceiling, -REACH).minus(&outer);
        let all = annulus.union(&crescent);
        (annulus, all)
    }
}

/// One scaffold layer: its top and height, its paths in the order they are laid (its outline
/// rings closed, then its walls and ties), and the area it stands on.
pub struct Layer {
    pub z: f64,
    pub height: f64,
    pub paths: Vec<Vec<Point>>,
    pub area: f64,
}

/// The beads a level layer of the plate already lays there: each line with its half-width.
pub type Beads = Vec<(Vec<Point>, f64)>;

/// The posed tip's section at `z` with every hole filled: the plug's bore counts as plug.
fn filled_section(tip: &Mesh, z: f64) -> Result<Region> {
    let rings = match section(tip, z) {
        Ok(rings) => rings,
        Err(_) => section(tip, z + 1e-4)?,
    };
    let twice_area = |r: &Vec<Point>| -> f64 {
        (0..r.len()).map(|i| {
            let (p, q) = (r[i], r[(i + 1) % r.len()]);
            p[0] * q[1] - q[0] * p[1]
        }).sum()
    };
    let outer: Vec<Vec<Point>> = rings.into_iter().filter(|r| r.len() >= 3 && twice_area(r) > 0.0).collect();
    Ok(Region::from_rings(&outer))
}

/// The scaffold under the roof's ring, whose ceiling is `ceiling` along the shoulder's normal,
/// in the plate's level `layers` (each its top and height) that stand under it. A layer's stock
/// keeps the plug clearance from the tip's section through the layer, bore included, and from
/// the beads the plate already lays in it, and stands under no part of the plug. Its first layer
/// meets the plate's own `footing` on the bed, the tip's brim, which its second layer may stand
/// on too. Each layer stands on the layer beneath it or leans out from it no further than its
/// lean, and reaches only where the roof, or the scaffold above, stands on it.
pub fn scaffold(ring: &Ring, tip: &Mesh, ceiling: f64, layers: &[(f64, f64)], beads: &[Beads], footing: &Beads) -> Result<Vec<Layer>> {
    ensure!(layers.len() == beads.len(), "every scaffold layer needs the plate's beads in it");
    let (annulus, all) = ring.footprint(ceiling);
    let f = &ring.frame;
    let highest = ring.plane_z(ceiling, f.cy + ceiling * f.s - (ring.outer + LIP) * f.c);
    let count = layers.iter().take_while(|l| l.0 <= highest + 1e-9).count();
    let below = |z: f64| {
        let top = ring.plane_y(ceiling, z);
        Region::from_rings(&[vec![[f.cx - 80.0, f.cy - 80.0], [f.cx + 80.0, f.cy - 80.0], [f.cx + 80.0, top], [f.cx - 80.0, top]]])
    };
    // from the top down: where the scaffold may stand, clear of the plug at its height and of the
    // plug above it
    let mut free = Vec::with_capacity(count);
    let mut overhead = Region::default();
    for &(z, height) in layers[..count].iter().rev() {
        let mut plug = Region::default();
        for at in [z - height + 0.02, z - height / 2.0, z - 0.02] {
            plug = plug.union(&filled_section(tip, at)?).simplified(THIN);
        }
        let under = below(z);
        free.push(all.and(&under).minus(&plug.union(&overhead).offset(PLUG_CLEAR)).simplified(THIN));
        overhead = overhead.union(&plug.and(&under)).simplified(THIN);
    }
    free.reverse();
    // from the bed up: what stands on the bed or on the layer beneath, clear of the plate's beads
    let footing = Region::beads(footing);
    let mut grounded: Vec<Region> = Vec::with_capacity(count);
    for k in 0..count {
        let clear: Beads = beads[k].iter().map(|(line, half)| (line.clone(), half + PLUG_CLEAR)).collect();
        let mut stock = free[k].minus(&Region::beads(&clear));
        if k == 0 {
            stock = stock.minus(&footing);
        } else {
            let beneath = if k == 1 { grounded[0].union(&footing.and(&free[0])) } else { grounded[k - 1].clone() };
            stock = stock.and(&beneath.offset(LEAN));
        }
        grounded.push(stock.simplified(THIN));
    }
    // from the top down again: only what the roof, or the scaffold above, stands on
    let mut needed = vec![Region::default(); count];
    let mut above = Region::default();
    for k in (0..count).rev() {
        let wanted = annulus.and(&below(layers[k].0)).union(&above.offset(LEAN));
        needed[k] = grounded[k].and(&wanted).offset(-WIDTH / 2.0).offset(WIDTH / 2.0).simplified(THIN);
        above = needed[k].clone();
    }
    let mut out = Vec::with_capacity(count);
    let mut at: Option<Point> = None;
    for (k, stock) in needed.into_iter().enumerate() {
        let (z, height) = layers[k];
        let centres = stock.offset(-WIDTH / 2.0);
        let mut paths = Vec::new();
        if !centres.is_empty() {
            let first = k == 0;
            let (lo, hi) = centres.bounds();
            let pitch = if first { WALL_PITCH / 2.0 } else { WALL_PITCH };
            let walls: Vec<Vec<Point>> = ((lo[0] / pitch).floor() as i64..=(hi[0] / pitch).ceil() as i64)
                .map(|j| vec![[j as f64 * pitch, lo[1] - 1.0], [j as f64 * pitch, hi[1] + 1.0]])
                .collect();
            let mut open: Vec<Vec<Point>> = centres.lines_inside(&walls);
            if first || k % 2 == 1 {
                let tie = if first { TIE_PITCH / 2.0 } else { TIE_PITCH };
                let ties: Vec<Vec<Point>> = ((lo[1] / tie).floor() as i64..=(hi[1] / tie).ceil() as i64)
                    .map(|j| vec![[lo[0] - 1.0, j as f64 * tie], [hi[0] + 1.0, j as f64 * tie]])
                    .collect();
                open.extend(centres.lines_inside(&ties));
            }
            open.retain(|l| length(l) >= SHORTEST);
            // the outline rings, each from its point nearest where the nozzle is
            for mut rim in centres.rings() {
                if length(&rim) < SHORTEST {
                    continue;
                }
                if let Some(p) = at {
                    let start = (0..rim.len()).min_by(|&i, &j| {
                        let d = |q: Point| (q[0] - p[0]).hypot(q[1] - p[1]);
                        d(rim[i]).total_cmp(&d(rim[j]))
                    }).unwrap_or(0);
                    rim.rotate_left(start);
                }
                rim.push(rim[0]);
                at = Some(rim[0]);
                paths.push(rim);
            }
            // then the walls and ties, each the nearest next, from its nearer end
            while !open.is_empty() {
                let p = at.unwrap_or(open[0][0]);
                let d = |q: Point| (q[0] - p[0]).hypot(q[1] - p[1]);
                let (i, flip) = (0..open.len())
                    .flat_map(|i| [(i, false), (i, true)])
                    .min_by(|&(i, a), &(j, b)| {
                        let end = |k: usize, back: bool| if back { *open[k].last().unwrap() } else { open[k][0] };
                        d(end(i, a)).total_cmp(&d(end(j, b)))
                    })
                    .unwrap();
                let mut line = open.swap_remove(i);
                if flip {
                    line.reverse();
                }
                at = line.last().copied();
                paths.push(line);
            }
        }
        out.push(Layer { z, height, paths, area: stock.area() });
    }
    Ok(out)
}

/// One roof line: where it starts and ends on the plate, and its bead's height.
pub struct RoofLine {
    pub from: [f64; 3],
    pub to: [f64; 3],
    pub height: f64,
}

/// The roof's courses over the scaffold whose layers top out at `tops_laid`, lowest course
/// first, each `course` thick with its top at `tops` along the normal. The first lies in level
/// lines across the slope, each after the lines just downhill of it and each standing on the
/// scaffold layer beneath it under the ceiling `ceiling`; the second runs up the slope and the
/// third across it at an angle, every line laid climbing. Each course keeps its lines' beads
/// out of `clear`, the plate's other beads at its height.
pub fn roof(ring: &Ring, ceiling: f64, tops: [f64; ROOF_COURSES], course: f64, tops_laid: &[f64], clear: &[Beads; ROOF_COURSES])
    -> Result<Vec<Vec<RoofLine>>> {
    let f = &ring.frame;
    let inner = ring.inner + PLUG_CLEAR + WIDTH / 2.0;
    let outer = ring.outer + LIP;
    let region = Region::ellipse(outer, outer, ELLIPSE_POINTS).minus(&Region::ellipse(inner, inner, ELLIPSE_POINTS));
    let at = |p: Point, n: f64| f.xyz(p[0], p[1], n);
    let laid_under = |y: f64| {
        let limit = ring.plane_z(ceiling, y);
        tops_laid.iter().copied().filter(|z| *z <= limit + 1e-6).fold(0.0, f64::max)
    };
    let keep: Vec<Region> = clear.iter()
        .map(|beads| Region::beads(&beads.iter().map(|(line, half)| (line.clone(), half + PLUG_CLEAR + WIDTH / 2.0)).collect::<Vec<_>>()))
        .collect();
    // the pieces of a line from `from` to `to` that keep out of course `k`'s clearance, each laid
    // the way the line runs
    let pieces = |from: [f64; 3], to: [f64; 3], k: usize| -> Vec<([f64; 3], [f64; 3])> {
        let run = (to[0] - from[0]).hypot(to[1] - from[1]);
        let along = |q: Point| {
            let t = ((q[0] - from[0]).hypot(q[1] - from[1]) / run).clamp(0.0, 1.0);
            (t, [q[0], q[1], from[2] + (to[2] - from[2]) * t])
        };
        keep[k].lines_outside(&[vec![[from[0], from[1]], [to[0], to[1]]]])
            .into_iter()
            .filter(|piece| length(piece) >= SHORTEST)
            .map(|piece| {
                let (ta, a) = along(piece[0]);
                let (tb, b) = along(piece[piece.len() - 1]);
                if ta <= tb { (a, b) } else { (b, a) }
            })
            .collect()
    };
    let mut courses = Vec::with_capacity(ROOF_COURSES);
    let mut first = Vec::new();
    for (a, b) in level_order(&hatch(&region, 0.0, WIDTH, 1.0)) {
        let (from, to) = (at(a, tops[0]), at(b, tops[0]));
        let height = from[2] - laid_under(from[1]);
        ensure!((0.15..=0.6).contains(&height), "a roof line stands {height} over the scaffold");
        first.extend(pieces(from, to, 0).into_iter().map(|(from, to)| RoofLine { from, to, height }));
    }
    courses.push(first);
    for (k, angle) in [(1, 90.0), (2, 45.0)] {
        let lines = hatch(&region, angle, WIDTH, 1.0)
            .into_iter()
            .flatten()
            .flat_map(|(a, b)| pieces(at(a, tops[k]), at(b, tops[k]), k))
            .map(|(from, to)| RoofLine { from, to, height: course })
            .collect();
        courses.push(lines);
    }
    Ok(courses)
}
