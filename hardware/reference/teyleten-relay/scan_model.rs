//! The relay reference models its observed exterior with clean planes, rounded profiles and bores.
use anyhow::{Context, Result};
use hsm_kernel::{Body, Loop, Plane, Profile, Solid, V2, V3, part, v2, v3};
use serde_json::Value;
use std::path::PathBuf;

fn number(v: &Value) -> Result<f64> {
    v.as_f64().context("expected a measured number")
}

fn point(v: &Value) -> Result<V3> {
    Ok(v3(number(&v[0])?, number(&v[1])?, number(&v[2])?))
}

fn xy(v: &Value) -> Result<V2> {
    Ok(v2(number(&v[0])?, number(&v[1])?))
}

fn srgb(c: [f64; 3]) -> [f64; 3] {
    c.map(|x| {
        if x <= 0.04045 {
            x / 12.92
        } else {
            ((x + 0.055) / 1.055).powf(2.4)
        }
    })
}

fn rounded_block(
    center: V2,
    width: f64,
    depth: f64,
    radius: f64,
    lo: f64,
    hi: f64,
) -> Result<Solid> {
    Plane::XY.at(v3(0., 0., lo)).extrude(
        &Profile::new(Loop::rounded_rect(center, width, depth, radius)?),
        hi - lo,
    )
}

fn combine(pieces: Vec<Solid>) -> Result<Solid> {
    let mut iter = pieces.into_iter();
    let mut solid = iter.next().context("a component group needs geometry")?;
    for next in iter {
        solid = solid.union(&next)?;
    }
    Ok(solid)
}

fn terminal_placed(solid: Solid, data: &Value) -> Result<Solid> {
    let center = xy(&data["center_xy_mm"])?;
    Ok(solid
        .rotate(V3::ZERO, V3::Z, number(&data["clock_degrees"])?)
        .translate(v3(center.x, center.y, 0.)))
}

/// The stepped wire face and inclined rear face use the observed housing cross-section.
fn terminal(data: &Value, common: &Value) -> Result<(Solid, Solid)> {
    let points = common["profile_xz_mm"]
        .as_array()
        .context("terminal cross-section")?
        .iter()
        .map(xy)
        .collect::<Result<Vec<_>>>()?;
    let width = number(&common["width_mm"])?;
    let outline = Loop::polygon(&points).fillet(number(&common["profile_radius_mm"])?)?;
    let plane = Plane::new(v3(0., width / 2., 0.), V3::X, -V3::Y)?;
    let mut housing = plane.extrude(&Profile::new(outline), width)?;
    let mut screws = Vec::new();
    for y in common["terminal_y_mm"]
        .as_array()
        .context("terminal spacing")?
    {
        let y = number(y)?;
        for key in ["wire_mouth", "rear_window"] {
            let opening = &common[key];
            let center = xy(&opening["center_yz_mm"])? + v2(y, 0.);
            let profile = Profile::new(Loop::rounded_rect(
                center,
                number(&opening["width_mm"])?,
                number(&opening["height_mm"])?,
                number(&opening["radius_mm"])?,
            )?);
            let cut = Plane::new(v3(number(&opening["closure_x_mm"])?, 0., 0.), V3::Y, V3::X)?
                .extrude(&profile, number(&opening["cut_depth_mm"])?)?;
            housing = housing.cut(&cut)?;
        }
        let well_bottom = number(&common["well_bottom_z_mm"])?;
        let top = number(&common["top_z_mm"])?;
        housing = housing.cut(&Solid::cylinder(
            v3(0., y, well_bottom),
            V3::Z,
            number(&common["well_radius_mm"])?,
            top - well_bottom + 1.,
        )?)?;
        let screw_bottom = number(&common["screw_bottom_z_mm"])?;
        let screw_top = number(&common["screw_top_z_mm"])?;
        let radius = number(&common["screw_radius_mm"])?;
        let screw = Solid::cylinder(
            v3(0., y, screw_bottom),
            V3::Z,
            radius,
            screw_top - screw_bottom,
        )?;
        let slot = Solid::cuboid(
            v3(
                -radius - 0.1,
                y - number(&common["screw_slot_width_mm"])? / 2.,
                number(&common["screw_slot_floor_z_mm"])?,
            ),
            v3(
                radius + 0.1,
                y + number(&common["screw_slot_width_mm"])? / 2.,
                screw_top + 0.1,
            ),
        );
        screws.push(screw.cut(&slot)?);
    }
    Ok((
        terminal_placed(housing, data)?,
        terminal_placed(combine(screws)?, data)?,
    ))
}

fn relay_can(data: &Value) -> Result<Solid> {
    let size = xy(&data["size_xy_mm"])?;
    let radius = number(&data["corner_radius_mm"])?;
    let lo = number(&data["bottom_z_mm"])?;
    let hi = number(&data["top_z_mm"])?;
    let bevel = number(&data["top_bevel_mm"])?;
    let base = Profile::new(Loop::rounded_rect(V2::ZERO, size.x, size.y, radius)?);
    let top = Profile::new(Loop::rounded_rect(
        V2::ZERO,
        size.x - bevel * 2.,
        size.y - bevel * 2.,
        radius - bevel,
    )?);
    let shell = Plane::XY
        .at(v3(0., 0., lo))
        .extrude(&base, hi - bevel - lo)?;
    let crown = Solid::loft(&[
        base.place(&Plane::XY.at(v3(0., 0., hi - bevel))),
        top.place(&Plane::XY.at(v3(0., 0., hi))),
    ])?;
    let center = xy(&data["center_xy_mm"])?;
    Ok(shell
        .union(&crown)?
        .rotate(V3::ZERO, V3::Z, number(&data["clock_degrees"])?)
        .translate(v3(center.x, center.y, 0.)))
}

fn package(data: &Value) -> Result<Solid> {
    let size = xy(&data["size_xy_mm"])?;
    rounded_block(
        xy(&data["center_xy_mm"])?,
        size.x,
        size.y,
        number(&data["corner_radius_mm"])?,
        number(&data["bottom_z_mm"])?,
        number(&data["top_z_mm"])?,
    )
}

/// The cap, header, package bodies and exposed leads keep the substantial control geometry.
fn control(data: &Value) -> Result<(Solid, Solid)> {
    let mut packages = data["packages"]
        .as_array()
        .context("control package bodies")?
        .iter()
        .map(package)
        .collect::<Result<Vec<_>>>()?;
    let cap = &data["jumper_cap"];
    let notch = &cap["notch"];
    packages.push(package(cap)?.cut(&Solid::cuboid(
        point(&notch["min_mm"])?,
        point(&notch["max_mm"])?,
    ))?);
    let leads = data["leads"]
        .as_array()
        .context("exposed control leads")?
        .iter()
        .map(|lead| {
            Ok(Solid::cuboid(
                point(&lead["min_mm"])?,
                point(&lead["max_mm"])?,
            ))
        })
        .collect::<Result<Vec<_>>>()?;
    Ok((combine(packages)?, combine(leads)?))
}

/// The observed solder protrusions use smooth closed envelopes at their measured locations.
fn solder(data: &Value) -> Result<Solid> {
    let center = xy(&data["center_xy_mm"])?;
    let profiles = data["sections"]
        .as_array()
        .context("solder profile sections")?
        .iter()
        .map(|section| {
            let radius = number(&section["radius_mm"])?;
            Ok(Profile::circle(center, radius).place(&Plane::XY.at(v3(
                0.,
                0.,
                number(&section["z_mm"])?,
            ))))
        })
        .collect::<Result<Vec<_>>>()?;
    Solid::loft(&profiles)
}

fn main() -> Result<()> {
    let mut args = std::env::args().skip(1);
    let datums = PathBuf::from(args.next().context("scan datums JSON")?);
    let out = PathBuf::from(args.next().context("reference output directory")?);
    let data: Value = serde_json::from_slice(&std::fs::read(datums)?)?;
    let pcb = &data["pcb"];
    let size = point(&pcb["size_mm"])?;
    let center = point(&pcb["center_mm"])?;
    let outline = Loop::rounded_rect(
        v2(center.x, center.y),
        size.x,
        size.y,
        number(&pcb["corner_radius_mm"])?,
    )?;
    let plane = Plane::new(v3(0., 0., center.z), V3::X, V3::Z)?;
    let mut board = plane.extrude(&Profile::new(outline), size.z)?;
    for hole in data["holes"].as_array().context("mounting holes")? {
        let p = point(&hole["center_mm"])?;
        let radius = number(&hole["radius_mm"])?;
        let bore = Solid::cylinder(
            v3(p.x, p.y, center.z - size.z),
            V3::Z,
            radius,
            size.z * 3.,
        )?;
        let taper_start = number(&pcb["opening_taper_start_z_mm"])?;
        let entry = Solid::cone(
            v3(p.x, p.y, center.z + taper_start),
            V3::Z,
            radius,
            number(&hole["opening_rim_radius_mm"])?,
            size.z - taper_start,
        )?;
        board = board.cut(&bore.union(&entry)?)?;
    }
    let geometry = &data["replica_geometry"];
    let mut pieces = vec![("pcb".to_owned(), srgb([0.08, 0.34, 0.21]), board)];
    for terminal_data in geometry["terminals"]
        .as_array()
        .context("terminal housings")?
    {
        let name = terminal_data["name"].as_str().context("terminal name")?;
        let (housing, screws) = terminal(terminal_data, &geometry["terminal_shape"])?;
        pieces.push((
            format!("{name}-terminals"),
            srgb([0.16, 0.55, 0.78]),
            housing,
        ));
        pieces.push((format!("{name}-screws"), srgb([0.68, 0.70, 0.72]), screws));
    }
    pieces.push((
        "relay-can".to_owned(),
        srgb([0.12, 0.35, 0.72]),
        relay_can(&geometry["relay_can"])?,
    ));
    let (packages, leads) = control(&geometry["control"])?;
    pieces.push((
        "control-components".to_owned(),
        srgb([0.17, 0.17, 0.18]),
        packages,
    ));
    pieces.push(("control-leads".to_owned(), srgb([0.65, 0.67, 0.69]), leads));
    for feature in geometry["solder"]
        .as_array()
        .context("observed solder tips")?
    {
        pieces.push((
            feature["name"].as_str().context("solder group")?.to_owned(),
            srgb([0.65, 0.67, 0.69]),
            solder(feature)?,
        ));
    }
    for (_, _, solid) in &pieces {
        solid.check()?;
    }
    let bodies: Vec<_> = pieces
        .iter()
        .map(|(name, color, solid)| Body {
            name,
            color: Some(*color),
            solid,
        })
        .collect();
    println!("{}", part::write_shown(&out, "teyleten-relay", &bodies)?);
    Ok(())
}
