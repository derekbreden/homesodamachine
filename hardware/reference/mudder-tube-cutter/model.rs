//! The Mudder cutter reference shows the pivoted lever, split anvil and steel blade.
use anyhow::Result;
use hsm_kernel::{Loop, Pen, Plane, Profile, Solid, V2, V3, v2, v3};
use hsm_sandbox::{material, out, show};

const LENGTH: f64 = 80.;
const WIDTH: f64 = 23.;
const CLOSED_HEIGHT: f64 = 25.;

// The molded details and display pose use proportions from the product photos.
const DECK_THICKNESS: f64 = 3.4;
const GRIP_THICKNESS: f64 = 3.1;
const BLADE_SLOT: f64 = 1.8;
const PIVOT: V3 = v3(-12.4, 0., 12.5);
const PIVOT_RADIUS: f64 = 2.05;
const OPEN_ANGLE: f64 = 19.;

fn side(outline: Loop, high_y: f64, width: f64) -> Result<Solid> {
    Plane::XZ
        .at(v3(0., high_y, 0.))
        .extrude(&Profile::new(outline), width)
}

fn deck(z: f64, thickness: f64) -> Result<Solid> {
    let profile = Profile::new(Loop::rounded_rect(V2::ZERO, LENGTH, WIDTH, 2.6)?);
    let plate = Plane::XY.offset(z).extrude(&profile, thickness)?;
    plate.fillet(&plate.edges(">Z or <Z")?, 0.48)
}

fn jaw_base() -> Result<Solid> {
    let anvil_outline = Loop::polygon(&[
        v2(-2.5, DECK_THICKNESS - 0.25),
        v2(38.3, DECK_THICKNESS - 0.25),
        v2(37.1, 10.9),
        v2(30.1, 10.9),
        v2(21.1, 6.4),
        v2(10.9, 10.9),
        v2(3.8, 10.9),
    ])
    .fillet(0.46)?;
    let cheek_edge = 10.1;
    let cheek_width = cheek_edge - BLADE_SLOT / 2.;
    let anvil_sides = [
        side(anvil_outline.clone(), cheek_edge, cheek_width)?,
        side(anvil_outline, -BLADE_SLOT / 2., cheek_width)?,
    ];
    let pedestal_outline = Pen::new(v2(-28.2, DECK_THICKNESS - 0.25))
        .line_to(v2(-20.7, 13.7))
        .arc_through(v2(-11.2, 17.4), v2(-6.4, 15.0))?
        .line_to(v2(2.4, DECK_THICKNESS - 0.25))
        .close()?;
    let pedestal = side(pedestal_outline, 6.65, 13.3)?;
    let eyelet_x = -LENGTH / 2. + 2.8;
    let eyelet_z = 2.82;
    let eyelet = Solid::cylinder(v3(eyelet_x, -11.4, eyelet_z), V3::Y, 2.8, 22.8)?;
    let base = deck(0., DECK_THICKNESS)?
        .union(&eyelet)?
        .union(&pedestal)?
        .union(&anvil_sides[0])?
        .union(&anvil_sides[1])?;

    let mut recesses = vec![
        Solid::cylinder(v3(eyelet_x, -12., eyelet_z), V3::Y, 1.25, 24.)?,
        Solid::cylinder(PIVOT - 7. * V3::Y, V3::Y, PIVOT_RADIUS + 0.1, 14.)?,
    ];
    for y in [-5.55, 5.55] {
        for (x, radius) in [(8., 2.05), (33.7, 1.8)] {
            recesses.push(Solid::cylinder(v3(x, y, 5.3), V3::Z, radius, 6.7)?);
        }
    }
    base.cut_all(&recesses)
}

fn lever() -> Result<Solid> {
    let grip_floor = CLOSED_HEIGHT - GRIP_THICKNESS;
    let grip = deck(grip_floor, GRIP_THICKNESS)?;
    let ear_outline = Pen::new(v2(-32.6, grip_floor + 0.2))
        .line_to(v2(-1.0, grip_floor + 0.2))
        .line_to(v2(-4.85, 12.4))
        .arc_through(v2(-13.9, 5.55), v2(-20.4, 10.0))?
        .line_to(v2(-27.7, 18.9))
        .close()?;
    let ears = [
        side(ear_outline.clone(), 10.8, 3.6)?,
        side(ear_outline, -7.2, 3.6)?,
    ];
    let rear_guide = Solid::cuboid(v3(3.5, -7.8, 11.5), v3(10., 7.8, grip_floor + 0.2));
    let front_guide = Solid::cuboid(v3(33.4, -8.9, 12.), v3(38., 8.9, grip_floor + 0.2));
    let blade_mount = Solid::cuboid(v3(29.5, -0.35, 15.7), v3(35., 2.3, grip_floor + 0.2));
    let lever = grip
        .union(&ears[0])?
        .union(&ears[1])?
        .union(&rear_guide)?
        .union(&front_guide)?
        .union(&blade_mount)?;

    let mut cuts = vec![Solid::cylinder(
        PIVOT - 12. * V3::Y,
        V3::Y,
        PIVOT_RADIUS + 0.1,
        24.,
    )?];
    for x in [-35.8, -33.2, -30.6, -28., -25.4] {
        let groove = Profile::new(Loop::slot(v2(x, 0.), 17., 0.62, 90.));
        cuts.push(Plane::XY.offset(CLOSED_HEIGHT - 0.38).extrude(&groove, 0.7)?);
    }
    lever.cut_all(&cuts)
}

fn blade() -> Result<Solid> {
    let blade = Loop::polygon(&[
        v2(9.7, 20.7),
        v2(33.4, 20.7),
        v2(33.4, 12.5),
        v2(21.1, 6.7),
        v2(9.5, 12.1),
        v2(9.5, 15.1),
        v2(11.9, 15.1),
        v2(11.9, 17.4),
        v2(9.7, 17.4),
    ]);
    let profile = Profile::new(blade).with_hole(Loop::circle(v2(22.1, 18.5), 1.28));
    let plate = Plane::XZ.at(v3(0., 0.35, 0.)).extrude(&profile, 0.8)?;
    let screw = Solid::cylinder(v3(31.4, -0.45, 18.6), -V3::Y, 1.15, 0.5)?;
    Ok(Solid::compose(&[plate, screw]))
}

fn spring_leaf() -> Result<Solid> {
    let outline = Loop::rounded_rect(v2(-32.1, 0.), 7.5, 9.3, 0.55)?;
    let profile = Profile::new(outline).with_hole(Loop::circle(v2(-33.1, 0.), 1.42));
    Plane::XY.offset(DECK_THICKNESS).extrude(&profile, 0.5)
}

fn main() -> Result<()> {
    let dir = out()?;
    let polymer = material("M_NEOFIT_ACETAL")?;
    let steel = material("M_STAINLESS")?;
    let pin = Solid::cylinder(PIVOT - 10.73 * V3::Y, V3::Y, PIVOT_RADIUS, 21.46)?;
    let lever = lever()?.rotate(PIVOT, V3::Y, -OPEN_ANGLE);
    let blade = blade()?.rotate(PIVOT, V3::Y, -OPEN_ANGLE);
    show(
        &dir,
        "mudder-tube-cutter",
        &[
            ("jaw-base", polymer, &jaw_base()?),
            ("lever", polymer, &lever),
            ("pivot-pin", polymer.map(|channel| channel * 0.68), &pin),
            ("blade", steel, &blade),
            ("spring-leaf", steel, &spring_leaf()?),
        ],
    )
}
