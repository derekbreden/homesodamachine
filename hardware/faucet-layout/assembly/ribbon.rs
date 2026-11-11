//! The display's cable, one solid from below the organizer to the PCB: ruled through the mounting
//! stack down to the plate's underside, its free return swept down through the organizer, its
//! spans up the neck, and its rise beside the display.
use crate::Variant;
use crate::legs::{path, ribbon_return};
use anyhow::{Result, ensure};
use hsm_faucet_assembly_numbers::{CABLE_LANE, CABLE_WIDTH, INDUSTRIAL_RIBBON_BLEND_HEIGHT, INDUSTRIAL_RIBBON_SIDE_RUN_N, UNDER_COUNTER_PLATE_BOTTOM_Z};
use hsm_faucet_numbers::paths::{self, Kind, RIBBON_DEPTH, RIBBON_WIDTH};
use hsm_faucet_numbers::{P3, shell};
use hsm_kernel::*;

fn v(p: P3) -> V3 {
    v3(p[0], p[1], p[2])
}

/// A rectangle `width` by `depth` about `origin`, its x on `xdir`, square to `normal`.
fn rect(origin: P3, xdir: P3, normal: P3, width: f64, depth: f64) -> Result<LoftSection> {
    let plane = Plane::new(v(origin), v(xdir), v(normal))?;
    let corners = [v2(-width / 2.0, -depth / 2.0), v2(width / 2.0, -depth / 2.0), v2(width / 2.0, depth / 2.0), v2(-width / 2.0, depth / 2.0)];
    Ok(LoftSection::new((0..4).map(|i| LoftEdge::Line { a: plane.point(corners[i]), b: plane.point(corners[(i + 1) % 4]) }).collect()))
}

/// The cable's own section at `origin`, square to `normal`.
fn section(origin: P3, normal: P3, width: f64) -> Result<LoftSection> {
    rect(origin, [1.0, 0.0, 0.0], normal, width, RIBBON_DEPTH)
}

/// The cable's flat sections through the mounting stack: under the plate, up to the lane's foot,
/// and at the lane's two stations.
fn lower_sections() -> Result<Vec<LoftSection>> {
    let [x, y] = shell::SIGNAL_LOWER_EXIT;
    let angle = shell::SIGNAL_LOWER_EXIT_ANGLE * (std::f64::consts::PI / 180.0);
    let xdir = [angle.cos(), angle.sin(), 0.0];
    let stations = [14.0, shell::SIGNAL_LANE_TOP_Z];
    [-50.0, stations[0] - 1.0, stations[0], stations[1]]
        .iter()
        .map(|&z| rect([x, y, z], xdir, [0.0, 0.0, 1.0], RIBBON_WIDTH, RIBBON_DEPTH))
        .collect()
}

/// A span of the cable up the faucet.
enum Span {
    Extrude(LoftSection, V3),
    Loft(Vec<LoftSection>),
    Sweep(LoftSection, [P3; 3]),
}

/// The tangent of `point` at `t`, by the difference across a micron either side.
fn tangent(point: impl Fn(f64) -> P3, t: f64) -> P3 {
    let (a, b) = (point(t - 0.001), point(t + 0.001));
    [(b[0] - a[0]) / 0.002, (b[1] - a[1]) / 0.002, (b[2] - a[2]) / 0.002]
}

/// The cable's spans from the stack's lane up to where it leaves the passage for the display.
fn spans() -> Result<Vec<Span>> {
    let lower_point = |z: f64| paths::lower_point(z, Kind::Ribbon, 1.0);
    let arc_point = |t: f64| paths::tube_arc_point(t, Kind::Ribbon, 1.0);
    let lower = |z: f64| section(lower_point(z), tangent(lower_point, z), RIBBON_WIDTH);
    let arc = |t: f64| section(arc_point(t), tangent(arc_point, t), paths::positions(t)[4]);
    let transition = |start: f64, end: f64, frame: &dyn Fn(f64) -> Result<LoftSection>| -> Result<Span> {
        let count = (((end - start) / 0.3).ceil() as usize).max(2);
        Ok(Span::Loft((0..=count).map(|i| frame(start + (end - start) * i as f64 / count as f64)).collect::<Result<_>>()?))
    };
    let straight = |z0: f64, z1: f64| -> Result<Span> {
        Ok(Span::Extrude(section(lower_point(z0), [0.0, 0.0, 1.0], RIBBON_WIDTH)?, v3(0.0, 0.0, z1 - z0)))
    };
    let constant = |s0: f64, s1: f64, n: f64| -> Result<Span> {
        let a = paths::JOINT_ANGLE + s0 / paths::water_radius();
        let b = paths::JOINT_ANGLE + s1 / paths::water_radius();
        let start = paths::arc_point(a, 0.0, n);
        let arc = [start, paths::arc_point((a + b) / 2.0, 0.0, n), paths::arc_point(b, 0.0, n)];
        Ok(Span::Sweep(section(start, [0.0, -a.sin(), a.cos()], RIBBON_WIDTH)?, arc))
    };
    let converge = paths::converge_start_s();
    Ok(vec![
        straight(38.8, paths::LOWER_START_Z)?,
        transition(paths::LOWER_START_Z, paths::LOWER_END_Z, &lower)?,
        straight(paths::LOWER_END_Z, paths::arc_start_z())?,
        constant(-paths::JOINT_ANGLE * paths::water_radius(), converge, paths::TIGHT_RIBBON_N)?,
        transition(converge, converge + paths::RIBBON_CONVERGE_LENGTH, &arc)?,
        constant(converge + paths::RIBBON_CONVERGE_LENGTH, shell::ribbon_end_s(), paths::FACE_RIBBON_N)?,
    ])
}

fn dist(a: P3, b: P3) -> f64 {
    (a[0] - b[0]).hypot(a[1] - b[1]).hypot(a[2] - b[2])
}

/// The cable's rise from where it leaves the neck to the PCB's terminal, in the tip frame: along
/// the bend's natural line, round the side of the display, down its side and up into the PCB.
fn display_sections(variant: Variant) -> Result<Vec<LoftSection>> {
    use shell::*;
    let seat_offset = variant.display_feet_n() - DISPLAY_FEET_N;
    let side_run_n = match variant {
        Variant::Sculpted => DISPLAY_RIBBON_SIDE_RUN_N,
        Variant::Industrial => INDUSTRIAL_RIBBON_SIDE_RUN_N,
    };
    let terminal_n = DISPLAY_RIBBON_TOP_N + seat_offset;
    ensure!(terminal_n > side_run_n, "the display terminal must stand above the ribbon's side run");
    let bend_rise = (terminal_n - side_run_n).min(DISPLAY_WIRE_BEND_RADIUS);
    let bend_sweep = (1.0 - bend_rise / DISPLAY_WIRE_BEND_RADIUS).acos();
    let [origin, along, outward] = tip_frame();
    let mut frames: Vec<(P3, P3)> = vec![];
    let natural = |s: f64| {
        let r = gn_bend1_r() + SIGNAL_LANE_CENTER_N;
        let square = (r * r - (s - GN_TIP_STRAIGHT_LEN).powi(2)).sqrt();
        (square - gn_bend1_r(), -(s - GN_TIP_STRAIGHT_LEN) / square)
    };
    let below_board = |n: f64, dn: f64| {
        let blend = INDUSTRIAL_RIBBON_BLEND_HEIGHT;
        let floor = side_run_n - blend;
        if variant == Variant::Industrial && n > floor {
            let u = ((n - floor) / (2.0 * blend)).min(1.0);
            (floor + blend * (2.0 * u - u * u), dn * (1.0 - u))
        } else {
            (n, dn)
        }
    };
    let add = |frames: &mut Vec<(P3, P3)>, p: P3, t: P3| {
        if frames.last().is_none_or(|(q, _)| dist(*q, p) >= 1e-8) {
            frames.push((p, t));
        }
    };
    for s in [DISPLAY_RIBBON_REFERENCE_START_S, (DISPLAY_RIBBON_REFERENCE_START_S + DISPLAY_RIBBON_JOIN_S) / 2.0, DISPLAY_RIBBON_JOIN_S] {
        let (n, slope) = natural(s);
        let (n, dn) = below_board(n, -slope);
        add(&mut frames, [0.0, s, n], [0.0, -1.0, dn]);
    }
    let side = DISPLAY_RIBBON_SIDE_X.signum();
    let side_x = DISPLAY_RIBBON_SIDE_X.abs();
    let r = DISPLAY_RIBBON_SIDE_RADIUS;
    let angle = (1.0 - side_x / (2.0 * r)).acos();
    for phase in 0..2 {
        for step in 0..13 {
            let u = angle * step as f64 / 12.0;
            let turn = if phase == 0 { u } else { angle - u };
            let (x, s) = if phase == 0 {
                (r * (1.0 - u.cos()), DISPLAY_RIBBON_JOIN_S - r * u.sin())
            } else {
                (r * (1.0 - 2.0 * angle.cos() + turn.cos()), DISPLAY_RIBBON_JOIN_S - r * (2.0 * angle.sin() - turn.sin()))
            };
            let (dx, ds) = (turn.sin(), -turn.cos());
            let (mut n, slope) = natural(s);
            let fraction = x / side_x;
            n += -DISPLAY_RIBBON_SIDE_DROP * fraction.powi(4) + DISPLAY_RIBBON_SIDE_LIFT * 4.0 * fraction * (1.0 - fraction);
            let dn = slope * ds - 4.0 * DISPLAY_RIBBON_SIDE_DROP * fraction.powi(3) * dx / side_x
                + 4.0 * DISPLAY_RIBBON_SIDE_LIFT * (1.0 - 2.0 * fraction) * dx / side_x;
            let (n, dn) = below_board(n, dn);
            add(&mut frames, [side * x, s, n], [side * dx, ds, dn]);
        }
    }
    let ([x, s0, n0], [_, ds, dn]) = *frames.last().expect("the cable's frames");
    let run_in = 3.0;
    let m0 = run_in * dn / -ds;
    for step in 1..13 {
        let t = step as f64 / 12.0;
        let n = (2.0 * t.powi(3) - 3.0 * t * t + 1.0) * n0 + (t.powi(3) - 2.0 * t * t + t) * m0 + (-2.0 * t.powi(3) + 3.0 * t * t) * side_run_n;
        let dn = (6.0 * t * t - 6.0 * t) * n0 + (3.0 * t * t - 4.0 * t + 1.0) * m0 + (-6.0 * t * t + 6.0 * t) * side_run_n;
        add(&mut frames, [x, s0 - run_in * t, n], [0.0, -run_in, dn]);
    }
    let side_start = s0 - run_in;
    let pre = display_housing_center_s() + DISPLAY_RIBBON_TERMINAL_Y + DISPLAY_WIRE_BEND_RADIUS * bend_sweep.sin();
    for step in 1..9 {
        add(&mut frames, [x, side_start + (pre - side_start) * step as f64 / 8.0, side_run_n], [0.0, -1.0, 0.0]);
    }
    let mut s = pre;
    for step in 1..17 {
        let t = bend_sweep * step as f64 / 16.0;
        s = pre - DISPLAY_WIRE_BEND_RADIUS * t.sin();
        let n = side_run_n + DISPLAY_WIRE_BEND_RADIUS * (1.0 - t.cos());
        add(&mut frames, [x, s, n], [0.0, -t.cos(), t.sin()]);
    }
    add(&mut frames, [x, s, terminal_n], [0.0, 0.0, 1.0]);
    frames
        .into_iter()
        .map(|([x, s, n], [dx, ds, dn])| {
            let mut center = [0.0; 3];
            let mut tangent = [0.0; 3];
            let mut cross = [0.0; 3];
            for i in 0..3 {
                let q = if i == 0 { x } else { 0.0 };
                center[i] = origin[i] + q + along[i] * s + outward[i] * n;
                let q = if i == 0 { dx } else { 0.0 };
                tangent[i] = q + along[i] * ds + outward[i] * dn;
                let q = if i == 0 { -ds } else { 0.0 };
                cross[i] = q + along[i] * dx;
            }
            if cross.iter().map(|v| v * v).sum::<f64>().sqrt() < 1e-8 {
                cross = [1.0, 0.0, 0.0];
            }
            rect(center, cross, tangent, RIBBON_WIDTH, RIBBON_DEPTH)
        })
        .collect()
}

/// The normal of a region's outer loop, by Newell's sum.
fn normal(region: &Region) -> V3 {
    let p = &region.loops[0].pts;
    (0..p.len()).fold(V3::ZERO, |n, i| n + p[i].cross(p[(i + 1) % p.len()]))
}

/// The whole cable.
pub fn ribbon(variant: Variant) -> Result<Solid> {
    let plate = Plane::new(v3(0.0, 0.0, UNDER_COUNTER_PLATE_BOTTOM_Z), V3::X, V3::Z)?;
    let mounted = Solid::thru_sections(&lower_sections()?, true)?.trim(&plate)?;
    let down = path(&ribbon_return())?;
    let flat = Profile::rect(v2(0.0, 0.0), CABLE_WIDTH, CABLE_LANE);
    let mut parts = vec![mounted, Plane::XY.at(down.legs[0].start()).sweep(&flat, &down)?];
    for span in spans()? {
        parts.push(match span {
            Span::Extrude(section, by) => {
                let region = section.region();
                Solid::extrude(&region, normal(&region), by)?
            }
            Span::Loft(sections) => Solid::thru_sections(&sections, true)?,
            Span::Sweep(section, [a, mid, b]) => Solid::sweep(&section.region(), &Path::new(v(a)).arc_through(v(mid), v(b))?)?,
        });
    }
    parts.push(Solid::thru_sections(&display_sections(variant)?, true)?);
    let cable = Solid::union_all(&parts)?;
    ensure!(cable.components().len() == 1, "the cable is not one solid");
    Ok(cable)
}
