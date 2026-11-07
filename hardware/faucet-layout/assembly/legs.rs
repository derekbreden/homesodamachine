//! The tubes' centrelines through the assembly, leg by leg: the soda tube up the gooseneck, each
//! flavor tube from its tail up through the splay, the pack, the gather, the step over to the
//! organizer and the mounting stack into the faucet, the drain's run, and the cable's return down
//! through the organizer.
use anyhow::{Context, Result, bail, ensure};
use hsm_faucet_assembly_numbers::*;
use hsm_faucet_numbers::interface::FLAVOR_TUBE_DEPTH;
use hsm_faucet_numbers::paths::{self, Kind, LOWER_BUNDLE_X, LOWER_DRAIN_Y};
pub use hsm_faucet_numbers::paths::Leg;
use hsm_faucet_numbers::{P2, P3, shell};
use hsm_kernel::{Path, V3, v3};

fn add(p: P3, by: P3) -> P3 {
    [p[0] + by[0], p[1] + by[1], p[2] + by[2]]
}

fn dist(a: P3, b: P3) -> f64 {
    (a[0] - b[0]).hypot(a[1] - b[1]).hypot(a[2] - b[2])
}

/// `leg` moved by `by`.
pub fn moved(leg: &Leg, by: P3) -> Leg {
    match leg {
        Leg::Line(a, b) => Leg::Line(add(*a, by), add(*b, by)),
        Leg::Arc(a, m, b) => Leg::Arc(add(*a, by), add(*m, by), add(*b, by)),
        Leg::Spline(v) => Leg::Spline(v.iter().map(|q| add(*q, by)).collect()),
        Leg::Hermite(a, b, ta, tb) => Leg::Hermite(add(*a, by), add(*b, by), *ta, *tb),
    }
}

/// `leg` walked the other way.
fn reversed(leg: &Leg) -> Result<Leg> {
    Ok(match leg {
        Leg::Line(a, b) => Leg::Line(*b, *a),
        Leg::Arc(a, m, b) => Leg::Arc(*b, *m, *a),
        _ => bail!("only line and arc legs are walked backwards here"),
    })
}

/// The arc of `radius` that leaves `start` along `tangent` and turns `theta`, anticlockwise when
/// `ccw`: its midpoint, its end and the tangent it ends on.
pub fn arc_from_tangent(start: P2, tangent: P2, radius: f64, theta: f64, ccw: bool) -> [P2; 3] {
    let sign = if ccw { 1.0 } else { -1.0 };
    let perp = if ccw { [-tangent[1], tangent[0]] } else { [tangent[1], -tangent[0]] };
    let center = [start[0] + radius * perp[0], start[1] + radius * perp[1]];
    let rad = [start[0] - center[0], start[1] - center[1]];
    let rot = |v: P2, a: f64| {
        let (c, s) = (a.cos(), a.sin());
        [v[0] * c - v[1] * s, v[0] * s + v[1] * c]
    };
    let mid = rot(rad, sign * theta / 2.0);
    let end = rot(rad, sign * theta);
    [[center[0] + mid[0], center[1] + mid[1]], [center[0] + end[0], center[1] + end[1]], rot(tangent, sign * theta)]
}

/// The gooseneck's two bends and straight tip from `start` along `tan`, in the bend's plane.
fn gooseneck(start: P2, tan: P2, r1: f64, r2: f64) -> ([P2; 2], P2, [P2; 2], P2) {
    let [m1, e1, t1] = arc_from_tangent(start, tan, r1, shell::GN_BEND1_SWEEP_RAD, true);
    let mid = [e1[0] + shell::GN_MID_STRAIGHT_LEN * t1[0], e1[1] + shell::GN_MID_STRAIGHT_LEN * t1[1]];
    let [m2, e2, t2] = arc_from_tangent(mid, t1, r2, shell::GN_BEND2_SWEEP_RAD, true);
    let tip = [e2[0] + shell::GN_TIP_STRAIGHT_LEN * t2[0], e2[1] + shell::GN_TIP_STRAIGHT_LEN * t2[1]];
    ([m1, e1], mid, [m2, e2], tip)
}

/// The soda tube from the port's floor up the gooseneck to the tip.
pub fn soda_legs() -> Vec<Leg> {
    let world = |v: P2| [0.0, PORT_CENTER_DEPTH + v[0], SODA_FAUCET_TUBE_Z_BOTTOM + v[1]];
    let start = [0.0, shell::gn_bend1_z_start() - SODA_FAUCET_TUBE_Z_BOTTOM];
    let (a, mid, b, tip) = gooseneck(start, [0.0, 1.0], shell::gn_bend1_r(), shell::gn_bend2_r());
    let mut legs = vec![Leg::Line(world([0.0, 0.0]), world(start)), Leg::Arc(world(start), world(a[0]), world(a[1]))];
    if shell::GN_MID_STRAIGHT_LEN > 0.0 {
        legs.push(Leg::Line(world(a[1]), world(mid)));
    }
    legs.extend([Leg::Arc(world(mid), world(b[0]), world(b[1])), Leg::Line(world(b[1]), world(tip))]);
    legs
}

/// A flavor tube's step from the mounting stack over to the organizer and back under it, from the
/// plate's underside down to `bottom`, relative to the tube's mount.
pub fn step_legs(s: f64, bottom: f64) -> Vec<Leg> {
    let mut legs = vec![];
    let mut current = [0.0; 3];
    let mount = [flavor_mount_x(s), FLAVOR_TUBE_DEPTH];
    for (dest, z) in [(organizer_flavor_xy(s), MOUNT_RETURN_START_Z), ([return_x(s), FLAVOR_TUBE_DEPTH], ORGANIZER_RETURN_START_Z)] {
        let start = [current[0], current[1], z - UNDER_COUNTER_PLATE_BOTTOM_Z];
        if dist(current, start) > 1e-7 {
            legs.push(Leg::Line(current, start));
        }
        let dx = dest[0] - mount[0] - start[0];
        let dy = dest[1] - mount[1] - start[1];
        let offset = dx.hypot(dy);
        if offset < 1e-7 {
            current = start;
            continue;
        }
        let theta = (1.0 - offset / (2.0 * STEP_BEND_RADIUS)).acos();
        let (ux, uy) = (dx / offset, dy / offset);
        let world = |q: P2| [start[0] + ux * q[0], start[1] + uy * q[0], q[1]];
        let mut local = [0.0, start[2]];
        let mut tangent = [0.0, -1.0];
        for turn in [true, false] {
            let [m, e, t] = arc_from_tangent(local, if turn { [0.0, -1.0] } else { tangent }, STEP_BEND_RADIUS, theta, turn);
            legs.push(Leg::Arc(world(local), world(m), world(e)));
            local = e;
            tangent = t;
        }
        current = [dest[0] - mount[0], dest[1] - mount[1], local[1]];
    }
    let end = [current[0], current[1], bottom - UNDER_COUNTER_PLATE_BOTTOM_Z];
    if dist(current, end) > 1e-7 {
        legs.push(Leg::Line(current, end));
    }
    legs
}

/// A flavor tube's gather from `top` down onto the pack, relative to where it starts gathering.
fn gather_legs(s: f64, top: f64) -> Vec<Leg> {
    let dx = s * hsm_faucet_numbers::interface::FLAVOR_TUBE_X_OFFSET - return_x(s);
    let dy = pack_flavor_depth() - FLAVOR_TUBE_DEPTH;
    let (ux, uy) = (dx / gather_offset(s), dy / gather_offset(s));
    let world = |p: P2| [ux * p[0], uy * p[0], p[1]];
    let [m1, e1, t1] = arc_from_tangent([0.0, 0.0], [0.0, -1.0], UMBILICAL_BEND_RADIUS, gather_theta(s), true);
    let [m2, e2, _] = arc_from_tangent(e1, t1, UMBILICAL_BEND_RADIUS, gather_theta(s), false);
    let gather = gather_start_z();
    let mut at = [0.0, top - gather];
    let mut legs = vec![];
    if top - gather > 1e-9 {
        legs.push(Leg::Line(world(at), world([0.0, 0.0])));
        at = [0.0, 0.0];
    }
    legs.extend([
        Leg::Arc(world(at), world(m1), world(e1)),
        Leg::Arc(world(e1), world(m2), world(e2)),
        Leg::Line(world(e2), world([e2[0], SPLAY_TOP_Z - gather])),
    ]);
    legs
}

/// A flavor tube's splay from the pack out to its tail, relative to the splay's top.
pub fn splay_legs(s: f64) -> Vec<Leg> {
    let world = |p: P2| [p[0], 0.0, p[1]];
    let start = [0.0, 0.0];
    let [m1, e1, t1] = arc_from_tangent(start, [0.0, -1.0], SPLAY_BEND_RADIUS, splay_theta(), s > 0.0);
    let [m2, e2, _] = arc_from_tangent(e1, t1, SPLAY_BEND_RADIUS, splay_theta(), s < 0.0);
    vec![
        Leg::Arc(world(start), world(m1), world(e1)),
        Leg::Arc(world(e1), world(m2), world(e2)),
        Leg::Line(world(e2), world([e2[0], UMBILICAL_TAIL_Z - SPLAY_TOP_Z])),
    ]
}

/// A flavor tube from its mount up through the faucet: its step walked back up, then the faucet's
/// own centreline.
pub fn flavor_run(s: f64) -> Result<Vec<Leg>> {
    let at = [flavor_mount_x(s), FLAVOR_TUBE_DEPTH, UNDER_COUNTER_PLATE_BOTTOM_Z];
    let mut legs = step_legs(s, gather_start_z()).iter().rev().map(|l| reversed(&moved(l, at))).collect::<Result<Vec<_>>>()?;
    legs.extend(paths::path_legs(Kind::Flavor, UNDER_COUNTER_PLATE_BOTTOM_Z, s, None));
    Ok(legs)
}

/// A flavor tube's umbilical: the gather and the splay down to its tail.
pub fn flavor_umbilical(s: f64) -> Vec<Leg> {
    let a = [return_x(s), FLAVOR_TUBE_DEPTH, gather_start_z()];
    let b = [s * hsm_faucet_numbers::interface::FLAVOR_TUBE_X_OFFSET, pack_flavor_depth(), SPLAY_TOP_Z];
    gather_legs(s, gather_start_z()).iter().map(|l| moved(l, a)).chain(splay_legs(s).iter().map(|l| moved(l, b))).collect()
}

/// The drain from its tail up to the plate's underside: an S-bend at each place it steps over.
fn drain_lower() -> Result<Vec<Leg>> {
    let mut legs = vec![];
    let mut current = [DRAIN_TAIL_X, drain_tail_y(), UMBILICAL_TAIL_Z];
    let org = organizer_axis("D");
    for [x, y, z] in [
        [DRAIN_TAIL_X, drain_pack_y(), SPLAY_TOP_Z],
        [DRAIN_TAIL_X, DRAIN_BYPASS_Y, gather_start_z()],
        [org[0], org[1], ORGANIZER_RETURN_START_Z],
        [LOWER_BUNDLE_X, LOWER_DRAIN_Y, MOUNT_RETURN_START_Z],
    ] {
        let (dx, dy) = (x - current[0], y - current[1]);
        let offset = dx.hypot(dy);
        let theta = (1.0 - offset / (2.0 * DRAIN_BEND_RADIUS)).acos();
        let rise = 2.0 * DRAIN_BEND_RADIUS * theta.sin();
        let start = [current[0], current[1], z - rise];
        ensure!(start[2] >= current[2] - 1e-7, "the drain's return arcs run past its vertical run");
        if dist(current, start) > 1e-7 {
            legs.push(Leg::Line(current, start));
        }
        let (ux, uy) = (dx / offset, dy / offset);
        let world = |q: P2| [start[0] + ux * q[0], start[1] + uy * q[0], q[1]];
        let mut local = [0.0, start[2]];
        let mut tangent = [0.0, 1.0];
        for turn in [false, true] {
            let [m, e, t] = arc_from_tangent(local, if !turn { [0.0, 1.0] } else { tangent }, DRAIN_BEND_RADIUS, theta, turn);
            legs.push(Leg::Arc(world(local), world(m), world(e)));
            local = e;
            tangent = t;
        }
        current = [x, y, z];
    }
    if MOUNT_RETURN_LEAD > 1e-7 {
        legs.push(Leg::Line(current, [LOWER_BUNDLE_X, LOWER_DRAIN_Y, UNDER_COUNTER_PLATE_BOTTOM_Z]));
    }
    Ok(legs)
}

/// The drain from its tail up into the faucet, to where it is cut square.
pub fn drain_legs() -> Result<Vec<Leg>> {
    let mut legs = drain_lower()?;
    legs.extend(paths::path_legs(Kind::Drain, UNDER_COUNTER_PLATE_BOTTOM_Z, 1.0, None));
    Ok(legs)
}

/// The cable's free return from the plate's underside down through the organizer.
pub fn ribbon_return() -> Vec<Leg> {
    let xy = shell::SIGNAL_LOWER_EXIT;
    let [cx, cy] = hsm_umbilical_organizer_numbers::CABLE_XY;
    let eased = [cx, cy, ORGANIZER_TOP_Z + 12.0];
    let down = [0.0, 0.0, -1.0];
    let mut legs = vec![];
    if MOUNT_RETURN_LEAD > 1e-7 {
        legs.push(Leg::Line([xy[0], xy[1], UNDER_COUNTER_PLATE_BOTTOM_Z], [xy[0], xy[1], MOUNT_RETURN_START_Z]));
    }
    legs.extend([
        Leg::Hermite([xy[0], xy[1], MOUNT_RETURN_START_Z], eased, down, down),
        Leg::Line(eased, [cx, cy, ORGANIZER_BOTTOM_Z - 10.0]),
    ]);
    legs
}

fn v(p: P3) -> V3 {
    v3(p[0], p[1], p[2])
}

/// The kernel's path along `legs`, each leg from where the last ends. Every path the faucet
/// sweeps leaves each join along the direction it arrived in, so a sweep along it is smooth there
/// with nothing added.
pub fn path(legs: &[Leg]) -> Result<Path> {
    let mut path: Option<Path> = None;
    for leg in legs {
        let start = v(leg.start());
        let p = path.take().unwrap_or_else(|| Path::new(start));
        ensure!((p.at() - start).norm() < 1e-7, "a leg from {start:?}, where the path ends at {:?}", p.at());
        path = Some(match leg {
            Leg::Line(_, b) => p.line_to(v(*b)),
            Leg::Arc(_, mid, b) => p.arc_through(v(*mid), v(*b))?,
            Leg::Spline(points) => p.spline_through(&points.iter().map(|q| v(*q)).collect::<Vec<_>>())?,
            Leg::Hermite(_, b, ta, tb) => p.spline_to(v(*b), v(*ta), v(*tb))?,
        });
    }
    path.context("a path of no legs")
}
