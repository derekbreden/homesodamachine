//! The supply reference preserves the manufacturer's mounting ears, drafted case and terminal interfaces.
use anyhow::{Context, Result};
use hsm_kernel::{Body, Loop, Plane, Profile, Seg, Solid, V2, V3, part, v2, v3};
use std::{path::PathBuf, sync::LazyLock};

static PARAMETERS: LazyLock<serde_json::Value> = LazyLock::new(||
    serde_json::from_str(include_str!("replica-parameters.json")).expect("supply parameters"));

fn n(key: &str) -> f64 { PARAMETERS["dimensions_mm"][key].as_f64().expect(key) }

#[derive(Clone, Copy)]
struct Terminal {
    side: f64,
    center_x: f64,
    center_y: f64,
    poles: usize,
    pitch: f64,
    width: f64,
    guard_x: f64,
    guard_top: f64,
}

fn terminals() -> Vec<Terminal> {
    PARAMETERS["terminals"].as_array().expect("terminal rows").iter().map(|row| Terminal {
        side: row["side"].as_f64().expect("side"),
        center_x: row["center_x"].as_f64().expect("center_x"),
        center_y: row["center_y"].as_f64().expect("center_y"),
        poles: row["poles"].as_u64().expect("poles") as usize,
        pitch: row["pitch"].as_f64().expect("pitch"),
        width: row["width"].as_f64().expect("width"),
        guard_x: row["guard_x"].as_f64().expect("guard_x"),
        guard_top: row["guard_top"].as_f64().expect("guard_top"),
    }).collect()
}

fn footprint() -> Result<Profile> {
    let p = [
        v2(-n("width") / 2., -n("side_half_length")),
        v2(-n("width") / 2., n("side_half_length")),
        v2(-n("corner_x"), n("corner_y")),
        v2(-n("taper_x"), n("taper_y")),
        v2(-n("end_half_width"), n("length") / 2.),
        v2(n("end_half_width"), n("length") / 2.),
        v2(n("taper_x"), n("taper_y")),
        v2(n("corner_x"), n("corner_y")),
        v2(n("width") / 2., n("side_half_length")),
        v2(n("width") / 2., -n("side_half_length")),
        v2(n("corner_x"), -n("corner_y")),
        v2(n("taper_x"), -n("taper_y")),
        v2(n("end_half_width"), -n("length") / 2.),
        v2(-n("end_half_width"), -n("length") / 2.),
        v2(-n("taper_x"), -n("taper_y")),
        v2(-n("corner_x"), -n("corner_y")),
    ];
    let mut segs = Vec::new();
    for i in 0..p.len() {
        let (a, b) = (p[i], p[(i + 1) % p.len()]);
        let center = match i {
            3 => Some(v2(-n("end_half_width"), n("length") / 2. - n("ear_radius"))),
            5 => Some(v2(n("end_half_width"), n("length") / 2. - n("ear_radius"))),
            11 => Some(v2(n("end_half_width"), -n("length") / 2. + n("ear_radius"))),
            13 => Some(v2(-n("end_half_width"), -n("length") / 2. + n("ear_radius"))),
            _ => None,
        };
        segs.push(match center {
            Some(c) => Seg::Arc { a, b, c, ccw: false },
            None => Seg::Line { a, b },
        });
    }
    Ok(Profile::new(Loop::new(segs)?.ccw()))
}

fn case_section(half_width: f64, half_length: f64) -> Profile {
    Profile::polygon(&[
        v2(-half_width + n("case_corner"), -half_length),
        v2(half_width - n("case_corner"), -half_length),
        v2(half_width, -half_length + n("case_corner")),
        v2(half_width, half_length - n("case_corner")),
        v2(half_width - n("case_corner"), half_length),
        v2(-half_width + n("case_corner"), half_length),
        v2(-half_width, half_length - n("case_corner")),
        v2(-half_width, -half_length + n("case_corner")),
    ])
}

/// A cylindrical shoulder joins the broad top plane to the drafted side.
fn crown_cut(plane: Plane, center: f64, radius: f64) -> Result<Solid> {
    let z = n("height") - radius;
    let a = v2(center, n("height"));
    let b = v2(center, n("height") + 5.);
    let c = v2(80., n("height") + 5.);
    let d = v2(80., z);
    let e = v2(center + radius, z);
    let profile = Profile::new(Loop::new(vec![
        Seg::Line { a, b }, Seg::Line { a: b, b: c },
        Seg::Line { a: c, b: d }, Seg::Line { a: d, b: e },
        Seg::Arc { a: e, b: a, c: v2(center, z), ccw: true },
    ])?.ccw());
    plane.extrude(&profile, 160.)
}

fn casing() -> Result<Solid> {
    let rise = n("height") - n("base_height");
    let upper = case_section(
        n("case_lower_half_width") - rise * n("case_side_draft").to_radians().tan(),
        n("case_lower_half_length") - rise * n("case_end_draft").to_radians().tan(),
    );
    let lower = case_section(n("case_lower_half_width"), n("case_lower_half_length"));
    let mut case = Solid::loft(&[
        lower.place(&Plane::XY.at(v3(0., 0., n("base_height")))),
        upper.place(&Plane::XY.at(v3(0., 0., n("height")))),
    ])?;
    let across = Plane::new(v3(0., 80., 0.), V3::X, -V3::Y)?;
    let side = crown_cut(across, n("case_side_crown"), n("case_side_round"))?;
    case = case.cut(&side)?.cut(&side.mirror(V3::ZERO, V3::X))?;
    let along = Plane::new(v3(-80., 0., 0.), V3::Y, V3::X)?;
    let end = crown_cut(along, n("case_end_crown"), n("case_end_round"))?;
    case = case.cut(&end)?.cut(&end.mirror(V3::ZERO, V3::Y))?;
    let nominal = Plane::XY.extrude(&Profile::rect(V2::ZERO, n("width"), n("length")), n("height") + 1.)?;
    case.intersect(&nominal)
}

fn guard(terminal: Terminal, x: f64) -> Result<Solid> {
    let profile = Profile::polygon(&[
        v2(43.58, n("base_height")), v2(n("length") / 2., n("base_height")),
        v2(n("length") / 2., n("ledge_height")), v2(43.58, terminal.guard_top),
    ]);
    let guard = Plane::new(v3(x, 0., 0.), V3::Y, V3::X)?.extrude(&profile, 1.2)?;
    Ok(if terminal.side > 0. { guard } else { guard.mirror(V3::ZERO, V3::Y) })
}

fn case_with_ears(terminals: &[Terminal]) -> Result<Solid> {
    let mut ears = Plane::XY.extrude(&footprint()?, n("ledge_height"))?;
    for &terminal in terminals {
        let slot = Plane::XY.at(v3(0., 0., n("base_height")))
            .extrude(&Profile::rect(v2(0., terminal.side * 52.),
                terminal.guard_x * 2., 18.), n("ledge_height") + 1.)?;
        ears = ears.cut(&slot)?;
        ears = ears.union(&guard(terminal, terminal.guard_x)?)?
            .union(&guard(terminal, -terminal.guard_x - 1.2)?)?;
    }
    let board = Plane::XY.at(v3(0., 0., n("terminal_board_bottom_z")))
        .extrude(&footprint()?, n("terminal_board_top_z") - n("terminal_board_bottom_z"))?
        .intersect(&Plane::XY.extrude(&Profile::rect(V2::ZERO,
            n("terminal_board_width"), n("terminal_board_length")), n("height"))?)?;
    let mut case = ears.union(&casing()?)?.union(&board)?;
    for x in [-n("hole_half_width"), n("hole_half_width")] {
        for y in [-n("hole_half_length"), n("hole_half_length")] {
            case = case.cut(&Solid::cylinder(v3(x, y, -1.), V3::Z,
                n("hole_radius"), n("ledge_height") + 2.)?)?;
        }
    }
    Ok(case)
}

fn terminal_body(t: Terminal) -> Result<Solid> {
    let profile = Profile::polygon(&[
        v2(n("terminal_back"), n("terminal_base_z")),
        v2(n("terminal_front"), n("terminal_base_z")),
        v2(n("terminal_front"), n("terminal_shoulder_z")),
        v2(n("terminal_front_shoulder"), n("terminal_shoulder_z")),
        v2(n("terminal_top_half_depth"), n("terminal_top_z")),
        v2(-n("terminal_top_half_depth"), n("terminal_top_z")),
        v2(n("terminal_back"), n("terminal_shoulder_z")),
    ]);
    let plane = Plane::new(v3(t.center_x - t.width / 2., t.center_y, 0.),
        V3::Y * t.side, V3::X * t.side)?;
    let mut block = plane.extrude(&profile, t.width * t.side)?;
    for pole in 0..t.poles {
        let x = t.center_x + (pole as f64 - (t.poles as f64 - 1.) / 2.) * t.pitch;
        block = block.cut(&Solid::cylinder(v3(x, t.center_y, n("screw_well_floor_z")),
            V3::Z, n("screw_well_radius"), n("terminal_top_z") - n("screw_well_floor_z") + 0.5)?)?;
        let mouth_plane = Plane::new(
            v3(x, t.center_y + t.side * (n("terminal_front") + 0.1), 0.),
            V3::X, -V3::Y)?;
        let mouth = mouth_plane.extrude(&Profile::rect(
            v2(0., (n("wire_bottom_z") + n("wire_top_z")) / 2.), n("wire_width"),
            n("wire_top_z") - n("wire_bottom_z")), (n("wire_depth") + 0.1) * t.side)?;
        block = block.cut(&mouth)?;
    }
    Ok(block)
}

fn srgb(c: [f64; 3]) -> [f64; 3] {
    c.map(|x| if x <= 0.04045 { x / 12.92 } else { ((x + 0.055) / 1.055).powf(2.4) })
}

fn main() -> Result<()> {
    let out = PathBuf::from(std::env::args().nth(1).context("reference output directory")?);
    std::fs::create_dir_all(&out)?;
    let terminals = terminals();
    let mut exterior = vec![case_with_ears(&terminals)?];
    for terminal in terminals { exterior.push(terminal_body(terminal)?); }
    let supply = Solid::compose(&exterior);
    println!("{}", part::write_shown(&out, "meanwell-irm90", &[
        Body { name: "meanwell-irm90", color: Some(srgb([0.2, 0.2, 0.24])), solid: &supply },
    ])?);
    Ok(())
}
