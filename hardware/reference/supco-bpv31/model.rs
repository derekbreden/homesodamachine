//! Reconstructs the capped Supco service valve for the Parts page.
use anyhow::{Context, Result};
use hsm_kernel::{Body, Loop, Plane, Profile, Seg, Solid, V2, V3, part, v2, v3};
use std::path::PathBuf;

const NAME: &str = "supco-bpv31";
const ZINC: [f64; 3] = [0.68, 0.71, 0.73];
const DARK_STEEL: [f64; 3] = [0.035, 0.035, 0.033];
const GASKET_COLOR: [f64; 3] = [0.22, 0.087, 0.056];

// The manufacturer lists the tube and male flare interfaces. The assembled
// shell, saddle and cap proportions are estimated from the product photos.
const INCH_MM: f64 = 25.4;
const TUBE_RADIUS: f64 = INCH_MM * 3. / 16.;
const FLARE_THREAD_RADIUS: f64 = INCH_MM * 7. / 32.;
const BODY_R: f64 = 12.2;
const LUG_R: f64 = 4.05;
const LUG_BLEND_R: f64 = 1.25;
const SCREWS: [V2; 3] = [v2(0., 11.8), v2(-9.2, -8.6), v2(9.2, -8.6)];
const JOINT_GAP: f64 = 0.12;
const SADDLE_BOTTOM: f64 = -8.4;
const BODY_TOP: f64 = 18.;
const SOCKET_FLOOR: f64 = BODY_TOP - 0.6;
const PORT_Z: f64 = 10.6;
const SCREW_SHANK_R: f64 = 1.9;

fn clamp_outline() -> Result<Profile> {
    // Each concave blend is tangent to both the casting envelope and a screw lug.
    let tangent = |lug: V2, side: f64| {
        let distance = lug.norm();
        let body_offset = BODY_R + LUG_BLEND_R;
        let lug_offset = LUG_R + LUG_BLEND_R;
        let axial = (body_offset.powi(2) + distance.powi(2) - lug_offset.powi(2)) / (2. * distance);
        let lateral = (body_offset.powi(2) - axial.powi(2)).sqrt();
        let radial = lug.unit();
        let center = radial * axial + radial.perp() * (side * lateral);
        (
            center.unit() * BODY_R,
            lug + (center - lug).unit() * LUG_R,
            center,
        )
    };
    let arc = |a, b, c, ccw| Seg::Arc { a, b, c, ccw };
    let mut segments = Vec::new();
    let (mut previous, _, _) = tangent(SCREWS[SCREWS.len() - 1], 1.);
    for lug in SCREWS {
        let (body_start, lug_start, blend_start) = tangent(lug, -1.);
        let (body_end, lug_end, blend_end) = tangent(lug, 1.);
        segments.extend([
            arc(previous, body_start, V2::ZERO, true),
            arc(body_start, lug_start, blend_start, false),
            arc(lug_start, lug_end, lug, true),
            arc(lug_end, body_end, blend_end, false),
        ]);
        previous = body_end;
    }
    Ok(Profile::new(Loop::new(segments)?))
}

fn port_turn(profile: &[(f64, f64)]) -> Result<Solid> {
    let profile = Profile::polygon(&profile.iter().map(|&(s, r)| v2(s, r)).collect::<Vec<_>>());
    Plane::new(v3(0., 0., PORT_Z), -V3::Y, V3::Z)?.revolve(&profile, 360., V2::ZERO, v2(1., 0.))
}

fn service_cap() -> Result<Solid> {
    let cap = port_turn(&[
        (14.5, 5.7),
        (14.5, 7.15),
        (15.1, 7.7),
        (16.2, 7.7),
        (17., 7.25),
        (26.5, 6.95),
        (27.4, 6.55),
        (27.7, 5.9),
        (27.7, 0.),
        (25.8, 0.),
        (25.8, 5.7),
    ])?;
    let flute = Profile::new(Loop::rounded_rect(V2::ZERO, 8.8, 1.8, 0.85)?);
    let flutes = (0..8)
        .map(|i| {
            let angle = (f64::from(i) + 0.5) * std::f64::consts::TAU / 8.;
            let radial = v3(angle.cos(), 0., angle.sin());
            Plane::new(v3(0., -21.3, PORT_Z) + radial * 6.65, V3::Y, radial)?.extrude(&flute, 3.)
        })
        .collect::<Result<Vec<_>>>()?;
    cap.cut_all(&flutes)
}

fn hex_socket(center: V3, radius: f64, depth: f64) -> Result<Solid> {
    let points = std::array::from_fn::<_, 6, _>(|i| {
        let angle = i as f64 * std::f64::consts::TAU / 6.;
        v2(angle.cos(), angle.sin()) * radius
    });
    Plane::XY
        .at(center)
        .extrude(&Profile::polygon(&points), depth)
}

fn screw(center: V2) -> Result<Solid> {
    let at = |z| v3(center.x, center.y, z);
    let shank_z = SADDLE_BOTTOM + 1.2;
    let shank = Solid::cylinder(at(shank_z), V3::Z, SCREW_SHANK_R, BODY_TOP - shank_z)?;
    let head = Solid::cylinder(at(BODY_TOP), V3::Z, 3.55, 2.8)?.union(&Solid::cone(
        at(BODY_TOP + 2.8),
        V3::Z,
        3.55,
        3.28,
        0.5,
    )?)?;
    shank
        .union(&head)?
        .cut(&hex_socket(at(BODY_TOP + 1.45), 1.9, 2.4)?)
}

fn saddle_lining() -> Result<Solid> {
    let outer = TUBE_RADIUS - 0.05;
    let inner = outer - 0.42;
    let along_arc = |r, side| v2(r * side * 0.96, r * 0.28);
    let a = along_arc(outer, 1.);
    let b = along_arc(outer, -1.);
    let c = along_arc(inner, -1.);
    let d = along_arc(inner, 1.);
    let strip = Profile::new(Loop::new(vec![
        Seg::Arc {
            a,
            b,
            c: V2::ZERO,
            ccw: true,
        },
        Seg::Line { a: b, b: c },
        Seg::Arc {
            a: c,
            b: d,
            c: V2::ZERO,
            ccw: false,
        },
        Seg::Line { a: d, b: a },
    ])?);
    Plane::YZ.offset(-10.8).extrude(&strip, 21.6)
}

fn main() -> Result<()> {
    let out = PathBuf::from(
        std::env::args()
            .nth(1)
            .context("reference output directory")?,
    );
    std::fs::create_dir_all(&out)?;
    let outline = clamp_outline()?;
    let bore = Solid::cylinder(v3(-16., 0., 0.), V3::X, TUBE_RADIUS, 32.)?;
    let upper = Plane::XY
        .offset(JOINT_GAP / 2.)
        .extrude(&outline, BODY_TOP - JOINT_GAP / 2.)?;
    let lower = Plane::XY
        .offset(SADDLE_BOTTOM)
        .extrude(&outline, -SADDLE_BOTTOM - JOINT_GAP / 2.)?;
    let screw_holes = SCREWS
        .map(|p| {
            Solid::cylinder(
                v3(p.x, p.y, SADDLE_BOTTOM - 1.),
                V3::Z,
                SCREW_SHANK_R + 0.16,
                32.,
            )
        })
        .into_iter()
        .collect::<Result<Vec<_>>>()?;
    let recess = Solid::cylinder(v3(0., 0., SOCKET_FLOOR), V3::Z, 10.4, 1.6)?;
    let stem_boss = Solid::cone(v3(0., 0., SOCKET_FLOOR - 0.12), V3::Z, 4.15, 3.72, 3.25)?;
    let outlet = port_turn(&[
        (10.8, 0.),
        (10.8, 6.3),
        (12.5, 5.25),
        (14.3, 5.25),
        (14.8, FLARE_THREAD_RADIUS),
        (22.8, FLARE_THREAD_RADIUS),
        (24.3, 4.05),
        (24.3, 0.),
    ])?;
    let upper = upper
        .cut(&bore)?
        .cut_all(&screw_holes)?
        .cut(&recess)?
        .union(&stem_boss)?
        .union(&outlet)?;
    let lower = lower.cut(&bore)?.cut_all(&screw_holes)?;
    let stem_z = SOCKET_FLOOR + 3.13;
    let stem = Solid::cylinder(v3(0., 0., stem_z), V3::Z, 3.35, 1.25)?.cut(&hex_socket(
        v3(0., 0., stem_z + 0.25),
        1.8,
        1.5,
    )?)?;
    let screw_a = screw(SCREWS[0])?;
    let screw_b = screw(SCREWS[1])?;
    let screw_c = screw(SCREWS[2])?;
    let cap = service_cap()?;
    let gasket = saddle_lining()?;
    let bodies = [
        Body {
            name: "valve-body",
            color: Some(ZINC),
            solid: &upper,
        },
        Body {
            name: "saddle",
            color: Some(ZINC),
            solid: &lower,
        },
        Body {
            name: "flare-cap",
            color: Some(ZINC),
            solid: &cap,
        },
        Body {
            name: "saddle-gasket",
            color: Some(GASKET_COLOR),
            solid: &gasket,
        },
        Body {
            name: "piercing-screw",
            color: Some(DARK_STEEL),
            solid: &stem,
        },
        Body {
            name: "clamp-screw-back",
            color: Some(DARK_STEEL),
            solid: &screw_a,
        },
        Body {
            name: "clamp-screw-left",
            color: Some(DARK_STEEL),
            solid: &screw_b,
        },
        Body {
            name: "clamp-screw-right",
            color: Some(DARK_STEEL),
            solid: &screw_c,
        },
    ];
    println!("{}", part::write_shown(&out, NAME, &bodies)?);
    Ok(())
}
