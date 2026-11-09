//! The purchased pump reference uses smooth primitives around its measured mounting and outlet datums.
use anyhow::{Context, Result};
use hsm_kernel::{Body, Loop, Path, Plane, Profile, Seg, Solid, V2, V3, part, v2, v3};
use std::path::PathBuf;

const FRAME: V3 = v3(35., 34., 0.);
const FLANGE_WIDTH: f64 = 62.6;
const FLANGE_DEPTH: f64 = 62.6;
const FLANGE_RADIUS: f64 = 8.;
const SEAT_Z: f64 = -8.;
const FLANGE_TOP_Z: f64 = 0.;
const FLANGE_HOLE_PITCH: f64 = 50.4;
const FLANGE_HOLE_RADIUS: f64 = 1.6;
const HEAD_FRONT_Z: f64 = -47.;
const HEAD_SHOULDER_Z: f64 = -12.;
const HEAD_HALF_WIDTH: f64 = 25.7;
const HEAD_BACK_Y: f64 = -26.;
const HEAD_BACK_RADIUS: f64 = 11.;
const HEAD_FRONT_CROWN_Y: f64 = 28.3;
const HEAD_FRONT_RADIUS: f64 = 52.;
const HEAD_FRONT_CORNER_RADIUS: f64 = 13.;
const ADAPTER_TOP_Z: f64 = 11.8;
const ADAPTER_COLUMN_REACH: f64 = 23.5;
const ADAPTER_COLUMN_OFFSET: f64 = 2.3;
const ADAPTER_COLUMN_RADIUS: f64 = 2.8;
const MOUNT_TOP_Z: f64 = 13.5;
const MOTOR_START_Z: f64 = 20.8;
const MOTOR_END_Z: f64 = 62.55;
const MOTOR_RADIUS: f64 = 17.76146649471765;
const OUTLET_X: f64 = 29.875;
const OUTLET_Z: f64 = -28.5;
const OUTLET_ROOT_Y: f64 = 27.4;
const OUTLET_END_Y: f64 = 32.;
const CASING_RADIUS: f64 = 6.5;
const SLEEVE_RADIUS: f64 = 5.2;
const TUBE_RADIUS: f64 = 3.175;

fn rounded_block(center: V2, width: f64, depth: f64, radius: f64, lo: f64, hi: f64) -> Result<Solid> {
    Plane::XY.at(v3(0., 0., lo))
        .extrude(&Profile::new(Loop::rounded_rect(center, width, depth, radius)?), hi - lo)
}

/// The tube side bows across the width in plan; the side and rear lands stay straight.
fn head_profile(half_width: f64, back: f64, back_radius: f64,
                crown: f64, front_radius: f64, front_corner: f64) -> Result<Profile> {
    let front_center = v2(0., crown - front_radius);
    let right_center = v2(half_width - front_corner,
        front_center.y + ((front_radius - front_corner).powi(2)
                         - (half_width - front_corner).powi(2)).sqrt());
    let tangent = front_center + (right_center - front_center)
        * (front_radius / (front_radius - front_corner));
    let a = v2(-half_width + back_radius, back);
    let b = v2(half_width - back_radius, back);
    let c = v2(half_width, back + back_radius);
    let d = v2(half_width, right_center.y);
    let e = tangent;
    let f = v2(-tangent.x, tangent.y);
    let g = v2(-half_width, right_center.y);
    let h = v2(-half_width, back + back_radius);
    Ok(Profile::new(Loop::new(vec![
        Seg::Line { a, b },
        Seg::Arc { a: b, b: c, c: v2(half_width - back_radius, back + back_radius), ccw: true },
        Seg::Line { a: c, b: d },
        Seg::Arc { a: d, b: e, c: right_center, ccw: true },
        Seg::Arc { a: e, b: f, c: front_center, ccw: true },
        Seg::Arc { a: f, b: g, c: v2(-right_center.x, right_center.y), ccw: true },
        Seg::Line { a: g, b: h },
        Seg::Arc { a: h, b: a, c: v2(-half_width + back_radius, back + back_radius), ccw: true },
    ])?))
}

fn cylinder(x: f64, y: f64, radius: f64, lo: f64, hi: f64) -> Result<Solid> {
    Solid::cylinder(v3(x, y, lo), V3::Z, radius, hi - lo)
}

fn adapter(lo: f64, hi: f64) -> Result<Solid> {
    let c = ADAPTER_COLUMN_REACH;
    let d = ADAPTER_COLUMN_OFFSET;
    let r = ADAPTER_COLUMN_RADIUS;
    let diagonal = r / 2_f64.sqrt();
    let lower = v2(c + diagonal, -d - diagonal);
    let notch = v2(c + (r * r - d * d).sqrt(), 0.);
    let upper = v2(c + diagonal, d + diagonal);
    let quarter = |p: V2, k: usize| match k % 4 {
        0 => p, 1 => v2(-p.y, p.x), 2 => -p, _ => v2(p.y, -p.x),
    };
    // Each circular pair meets in a shallow valley; tangent flats connect adjacent pairs.
    let mut edges = Vec::new();
    for k in 0..4 {
        edges.push(Seg::Arc { a: quarter(lower, k), b: quarter(notch, k),
                             c: quarter(v2(c, -d), k), ccw: true });
        edges.push(Seg::Arc { a: quarter(notch, k), b: quarter(upper, k),
                             c: quarter(v2(c, d), k), ccw: true });
        edges.push(Seg::Line { a: quarter(upper, k), b: quarter(lower, k + 1) });
    }
    let outline = Loop::new(edges)?;
    Plane::XY.at(v3(0., 0., lo)).extrude(&Profile::new(outline), hi - lo)
}

/// The outlet casings turn out of the head before the flexible sleeves begin.
fn outlet(sign: f64) -> Result<Solid> {
    let bend_radius = 10.;
    let start = v3(sign * (OUTLET_X - bend_radius), 5., OUTLET_Z);
    let mid = v3(sign * (OUTLET_X - bend_radius + bend_radius / 2_f64.sqrt()),
                 15. - bend_radius / 2_f64.sqrt(), OUTLET_Z);
    let path = Path::new(start)
        .arc_through(mid, v3(sign * OUTLET_X, 15., OUTLET_Z))?
        .line_to(v3(sign * OUTLET_X, OUTLET_ROOT_Y, OUTLET_Z));
    let plane = Plane::new(start, V3::Z, V3::X * sign)?;
    plane.sweep(&Profile::circle(V2::ZERO, CASING_RADIUS), &path)
}

fn srgb(c: [f64; 3]) -> [f64; 3] {
    c.map(|x| if x <= 0.04045 { x / 12.92 } else { ((x + 0.055) / 1.055).powf(2.4) })
}

fn main() -> Result<()> {
    let out = PathBuf::from(std::env::args().nth(1).context("reference output directory")?);
    std::fs::create_dir_all(&out)?;
    let casing = head_profile(HEAD_HALF_WIDTH, HEAD_BACK_Y, HEAD_BACK_RADIUS,
                              HEAD_FRONT_CROWN_Y, HEAD_FRONT_RADIUS, HEAD_FRONT_CORNER_RADIUS)?;
    let neck = head_profile(23., -24., 7., 27., 50., 9.)?;
    let mut head = rounded_block(v2(0., -0.2), FLANGE_WIDTH, FLANGE_DEPTH, FLANGE_RADIUS,
                                 SEAT_Z, FLANGE_TOP_Z)?
        .union(&Plane::XY.at(v3(0., 0., HEAD_FRONT_Z)).extrude(&casing, HEAD_SHOULDER_Z - HEAD_FRONT_Z)?)?
        .union(&Plane::XY.at(v3(0., 0., HEAD_SHOULDER_Z)).extrude(&neck, SEAT_Z - HEAD_SHOULDER_Z)?)?;
    for x in [-FLANGE_HOLE_PITCH / 2., FLANGE_HOLE_PITCH / 2.] {
        for y in [-FLANGE_HOLE_PITCH / 2., FLANGE_HOLE_PITCH / 2.] {
            head = head.cut(&cylinder(x, y - 0.2, FLANGE_HOLE_RADIUS, SEAT_Z - 0.1, FLANGE_TOP_Z + 0.1)?)?;
        }
    }
    let mut sleeves = Vec::new();
    for sign in [-1., 1.] {
        head = head.union(&outlet(sign)?)?;
        let sleeve = Solid::cylinder(v3(sign * OUTLET_X, OUTLET_ROOT_Y, OUTLET_Z),
                                     V3::Y, SLEEVE_RADIUS, OUTLET_END_Y - OUTLET_ROOT_Y)?;
        let passage = Solid::cylinder(v3(sign * OUTLET_X, OUTLET_ROOT_Y - 0.1, OUTLET_Z),
                                      V3::Y, TUBE_RADIUS, OUTLET_END_Y - OUTLET_ROOT_Y + 0.2)?;
        sleeves.push(sleeve.cut(&passage)?);
    }
    let housing = adapter(FLANGE_TOP_Z, ADAPTER_TOP_Z)?;
    let mount = adapter(ADAPTER_TOP_Z, MOUNT_TOP_Z)?
        .union(&cylinder(0., 0., MOTOR_RADIUS, MOUNT_TOP_Z, MOTOR_START_Z)?)?;
    let mut motor = cylinder(0., 0., MOTOR_RADIUS, MOTOR_START_Z, MOTOR_END_Z)?
        .union(&cylinder(0., 0., 6.2, MOTOR_END_Z, 65.)?)?
        .union(&cylinder(0., 0., 2.5, 65., 66.5)?)?;
    // Flat electrical tabs preserve the rear connection space.
    for sign in [-1., 1.] {
        let tab = Solid::cuboid(v3(-1.8, -0.4, MOTOR_END_Z), v3(1.8, 0.4, 68.5))
            .rotate(V3::ZERO, V3::Z, 45.)
            .translate(v3(sign * 12., -sign * 12., 0.));
        motor = motor.union(&tab)?;
    }
    let mut fasteners = Vec::new();
    for x in [-17., 17.] {
        for y in [-18.7, 18.7] {
            fasteners.push(cylinder(x, y, 2.8, -48.6, HEAD_FRONT_Z)?);
        }
    }
    for (x, y) in [(-23.5, 2.3), (2.3, 23.5), (23.5, -2.3), (-2.3, -23.5)] {
        fasteners.push(cylinder(x, y, 2.7, MOUNT_TOP_Z, 15.)?);
    }
    let primer = cylinder(0., 0.5, 3.7, -48., HEAD_FRONT_Z)?;
    let pieces = [
        ("head", srgb([0.16, 0.16, 0.18]), head),
        ("rotor_housing", srgb([0.9, 0.9, 0.88]), housing),
        ("motor_mount", srgb([0.13, 0.13, 0.15]), mount),
        ("motor_body", srgb([0.74, 0.76, 0.8]), motor),
        ("fasteners", srgb([0.72, 0.74, 0.77]), Solid::compose(&fasteners)),
        ("primer", srgb([0.94, 0.76, 0.02]), primer),
        ("silicone_outlets", srgb([0.89, 0.88, 0.79]), Solid::compose(&sleeves)),
    ];
    let placed: Vec<_> = pieces.into_iter().map(|(name, color, solid)|
        (name, color, solid.translate(FRAME))).collect();
    let bodies: Vec<_> = placed.iter().map(|(name, color, solid)| Body {
        name, color: Some(*color), solid,
    }).collect();
    println!("{}", part::write_shown(&out, "kamoer-kphm400", &bodies)?);
    Ok(())
}
