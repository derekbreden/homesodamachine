//! The purchased pump's frozen reference separates the registered exterior into its visible components.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Body, Solid, V3, import, part, v3};
use std::path::PathBuf;

fn box_between(lo: [f64; 3], hi: [f64; 3]) -> Solid {
    Solid::cuboid(V3::from(lo), V3::from(hi))
}

fn band(solid: &Solid, low: f64, high: f64) -> Result<Solid> {
    solid.intersect(&box_between([-45., -40., low], [45., 45., high]))
}

fn srgb(c: [f64; 3]) -> [f64; 3] {
    c.map(|x| if x <= 0.04045 { x / 12.92 } else { ((x + 0.055) / 1.055).powf(2.4) })
}

/// The identified scan blemish is replaced by the independently fitted barrel surface.
fn clean_motor(motor: &Solid) -> Result<Solid> {
    let patch = box_between([-17., -25., 49.5], [-1., -9., 63.3]);
    let tilt = v3(-0.000518049629291531, -0.00388684904451317, 1.).unit();
    let z = 20.8;
    let base = v3(0.07408880099347936 + (z - 42.) * tilt.x / tilt.z,
                  -0.13976974608396667 + (z - 42.) * tilt.y / tilt.z, z);
    let barrel = Solid::cylinder(base, tilt, 17.76146649471765, (62.55 - z) / tilt.z)?;
    motor.cut(&patch)?.union(&barrel.intersect(&patch)?)
}

fn main() -> Result<()> {
    let mut args = std::env::args().skip(1);
    let input = PathBuf::from(args.next().context("observed exterior NPZ")?);
    let out = PathBuf::from(args.next().context("reference output directory")?);
    let imported = import::model(&input)?;
    if imported.iter().any(|body| body.name == "motor_body") {
        let parts: Vec<_> = imported.into_iter().map(|body| {
            let solid = if body.name == "motor_body" {
                clean_motor(&body.solid.translate(v3(-35., -34., 0.)))?.translate(v3(35., 34., 0.))
            } else { body.solid };
            Ok((body.name, body.color, solid))
        }).collect::<Result<_>>()?;
        let bodies: Vec<_> = parts.iter().map(|(name, color, solid)| Body { name, color: *color, solid }).collect();
        println!("{}", part::write_shown(&out, "kamoer-kphm400", &bodies)?);
        return Ok(());
    }
    let observed = &imported[0].solid;
    let mut outlets = Vec::new();
    for sign in [-1.0_f64, 1.0] {
        let low = (sign * 24.).min(sign * 39.);
        let high = (sign * 24.).max(sign * 39.);
        outlets.push(box_between([low, 27.4, -38.], [high, 45., -19.]));
    }
    let outlet_mask = Solid::compose(&outlets);
    let rigid = observed.cut(&outlet_mask)?;
    let sleeves = observed.intersect(&outlet_mask)?.intersect(&box_between([-40., 27.4, -39.], [40., 32., -18.]))?;
    let head = band(&rigid, -55., 0.)?;
    let housing = band(&rigid, 0., 11.8)?;
    let mount = band(&rigid, 11.8, 20.8)?;
    let motor = clean_motor(&band(&rigid, 20.8, 75.)?)?;

    // Component boundaries follow visible hardware; the scan retains the actual recesses.
    let mut fastener_masks = Vec::new();
    for x in [-17., 17.] {
        for y in [-18.7, 18.7] {
            fastener_masks.push(Solid::cylinder(v3(x, y, -51.), V3::Z, 2.8, 6.)?);
        }
    }
    let head_fasteners = head.intersect(&Solid::compose(&fastener_masks))?;
    let primer_mask = Solid::cylinder(v3(0., 0.5, -51.), V3::Z, 3.7, 4.7)?;
    let primer = head.intersect(&primer_mask)?;
    let head = head.cut(&head_fasteners)?.cut(&primer)?;
    let mut rear_masks = Vec::new();
    for (x, y) in [(-23.5, 2.3), (2.3, 23.5), (23.5, -2.3), (-2.3, -23.5)] {
        rear_masks.push(Solid::cylinder(v3(x, y, 12.), V3::Z, 2.7, 7.)?);
    }
    let rear_fasteners = mount.intersect(&Solid::compose(&rear_masks))?;
    let mount = mount.cut(&rear_fasteners)?;
    let fasteners = Solid::compose(&[head_fasteners, rear_fasteners]);
    let pieces = [
        ("head", srgb([0.16, 0.16, 0.18]), head),
        ("rotor_housing", srgb([0.9, 0.9, 0.88]), housing),
        ("motor_mount", srgb([0.13, 0.13, 0.15]), mount),
        ("motor_body", srgb([0.74, 0.76, 0.8]), motor),
        ("fasteners", srgb([0.72, 0.74, 0.77]), fasteners),
        ("primer", srgb([0.94, 0.76, 0.02]), primer),
        ("silicone_outlets", srgb([0.89, 0.88, 0.79]), sleeves),
    ];
    let placed: Vec<_> = pieces.into_iter().map(|(name, color, solid)|
        (name, color, solid.translate(v3(35., 34., 0.)))).collect();
    for (name, _, solid) in &placed {
        ensure!(!solid.is_empty(), "empty component {name}");
        solid.check()?;
    }
    let bodies: Vec<_> = placed.iter().map(|(name, color, solid)| Body {
        name, color: Some(*color), solid,
    }).collect();
    println!("{}", part::write_shown(&out, "kamoer-kphm400", &bodies)?);
    Ok(())
}
