//! Catalog reference for the insulated pump-motor disconnect from the mixed receptacle kit.
use anyhow::{Context, Result};
use hsm_kernel::{Loop, Plane, Profile, Region, Seg, Solid, V3, v2, v3};
use hsm_sandbox::{out, show};

const CONTACT_WIDTH: f64 = 5.7;
const CONTACT_LENGTH: f64 = 19.5;
const SHEET: f64 = 0.35;
const NOSE_END: f64 = 8.1;

fn rolled_contact() -> Result<Solid> {
    let outside = CONTACT_WIDTH / 2.;
    let radius = 0.55;
    let inner_radius = radius - SHEET;
    let curl_height = 0.91;
    let center = v2(outside - radius, curl_height);
    let foot = v2(outside, 0.15);
    let outer_start = v2(outside, curl_height);
    let outer_end = v2(center.x - radius, curl_height);
    let inner_start = v2(center.x - inner_radius, curl_height);
    let inner_end = v2(center.x + inner_radius, curl_height);
    let inner_foot = v2(inner_end.x, foot.y);
    let outline = Loop::new(vec![
        Seg::Line {
            a: foot,
            b: outer_start,
        },
        Seg::Arc {
            a: outer_start,
            b: outer_end,
            c: center,
            ccw: true,
        },
        Seg::Line {
            a: outer_end,
            b: inner_start,
        },
        Seg::Arc {
            a: inner_start,
            b: inner_end,
            c: center,
            ccw: false,
        },
        Seg::Line {
            a: inner_end,
            b: inner_foot,
        },
        Seg::Line {
            a: inner_foot,
            b: foot,
        },
    ])?;
    Plane::YZ
        .at(v3(0.16, 0., 0.))
        .extrude(&Profile::new(outline), NOSE_END - 0.16)
}

fn crimp(start: f64, end: f64, width: f64, height: f64) -> Result<Solid> {
    let bottom = 0.10;
    let center = v2(0., bottom + height / 2.);
    let radius = height / 2. - 0.04;
    let profile = Profile::new(Loop::rounded_rect(center, width, height, radius)?).with_hole(
        Loop::rounded_rect(
            center,
            width - 2. * SHEET,
            height - 2. * SHEET,
            radius - SHEET,
        )?,
    );
    let barrel = Plane::YZ
        .at(v3(start, 0., 0.))
        .extrude(&profile, end - start)?;
    barrel.cut(&Solid::cuboid(
        v3(start - 0.1, -0.12, center.y),
        v3(end + 0.1, 0.12, bottom + height + 0.1),
    ))
}

fn contact() -> Result<Solid> {
    let half_width = CONTACT_WIDTH / 2.;
    let blank = Profile::polygon(&[
        v2(0., -half_width + 0.18),
        v2(0.22, -half_width),
        v2(NOSE_END, -half_width),
        v2(10.40, -1.12),
        v2(14.50, -1.12),
        v2(15.70, -1.36),
        v2(CONTACT_LENGTH, -1.36),
        v2(CONTACT_LENGTH, 1.36),
        v2(15.70, 1.36),
        v2(14.50, 1.12),
        v2(10.40, 1.12),
        v2(NOSE_END, half_width),
        v2(0.22, half_width),
        v2(0., half_width - 0.18),
    ]);
    let rail = rolled_contact()?;
    let mut terminal = Plane::XY
        .extrude(&blank, SHEET)?
        .union(&rail)?
        .union(&rail.mirror(V3::ZERO, V3::Y))?;
    for x in [2.02, 5.21] {
        for y in [-1.78, 1.78] {
            terminal = terminal.cut(&Solid::cuboid(
                v3(x, y - 0.72, -0.1),
                v3(x + 0.52, y + 0.72, SHEET + 0.13),
            ))?;
        }
    }
    let detent = Solid::sphere(v3(3.95, 0., -0.18), 0.68)?
        .intersect(&Solid::cuboid(v3(3.15, -0.8, 0.19), v3(4.75, 0.8, 0.70)))?;
    terminal
        .union(&detent)?
        .union(&crimp(11.24, 14.22, 2.45, 1.72)?)?
        .union(&crimp(15.53, CONTACT_LENGTH, 3.36, 2.31)?)
}

fn boot_section(x: f64, width: f64, height: f64, radius: f64) -> Result<Region> {
    let section = Profile::new(Loop::rounded_rect(v2(0., 1.20), width, height, radius)?);
    Ok(section.place(&Plane::YZ.at(v3(x, 0., 0.))))
}

fn boot() -> Result<Solid> {
    let stations = [
        (10.25, 6.25, 3.50, 0.56),
        (10.53, 6.65, 3.87, 0.70),
        (19.85, 6.65, 3.87, 0.70),
        (20.55, 6.40, 3.78, 0.78),
        (22.72, 4.03, 3.51, 1.28),
        (23.52, 3.83, 3.42, 1.36),
        (25.14, 3.98, 3.55, 1.43),
        (28.02, 4.10, 3.69, 1.49),
        (28.64, 3.89, 3.51, 1.40),
        (36.78, 3.73, 3.40, 1.35),
        (37.00, 3.55, 3.23, 1.26),
    ];
    let outside = stations
        .iter()
        .map(|&(x, width, height, radius)| boot_section(x, width, height, radius))
        .collect::<Result<Vec<_>>>()?;
    let wall = 0.33;
    let bore = [
        (10.10, 6.25, 3.50, 0.56),
        (19.85, 6.65, 3.87, 0.70),
        (20.55, 6.40, 3.78, 0.78),
        (22.72, 4.03, 3.51, 1.28),
        (23.52, 3.83, 3.42, 1.36),
        (37.15, 3.55, 3.23, 1.26),
    ]
    .into_iter()
    .map(|(x, width, height, radius)| {
        boot_section(x, width - 2. * wall, height - 2. * wall, radius - wall)
    })
    .collect::<Result<Vec<_>>>()?;
    Solid::loft(&outside)
        .context("insulating boot outer wall")?
        .cut(&Solid::loft(&bore).context("insulating boot cavity")?)
}

fn main() -> Result<()> {
    let dir = out()?;
    let orient = |solid: Solid| solid.rotate(V3::ZERO, V3::Z, 180.);
    let contact = orient(contact()?);
    let boot = orient(boot()?);
    show(
        &dir,
        "female-faston-receptacle",
        &[
            ("stamped-contact", [0.51, 0.53, 0.56], &contact),
            ("insulating-sleeve", [0.76, 0.83, 0.89], &boot),
        ],
    )
}
