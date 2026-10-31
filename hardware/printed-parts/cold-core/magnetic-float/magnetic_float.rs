//! The RC62 magnetic float: a PETG envelope, the ASA Aero core and insert fitted inside it, and
//! the magnet seated between them. `magnetic_float.py` holds the numbers and writes them for this
//! program, and writes the design figures from the volumes it prints.
//!
//!     cargo run --release -p hsm-cold-core --bin magnetic-float -- <numbers.json> <out dir>
//!
//! Frame: guide bore on Z, finished bottom at Z = 0. Each piece is written standing on its own
//! print face; the assembly, its half section and its exploded view stand in the float's frame.
use anyhow::Result;
use hsm_cold_core::{Numbers, args};
use hsm_kernel::*;
use serde_json::json;

/// What the exploded view lifts the insert and the magnet by.
const INSERT_LIFT: f64 = 24.0;
const MAGNET_LIFT: f64 = 10.0;

/// The ring between two radii, standing from `bottom` to `top`.
fn annulus(outer: f64, inner: f64, bottom: f64, top: f64) -> Result<Solid> {
    let section = Profile::circle(v2(0.0, 0.0), outer).with_hole(Loop::circle(v2(0.0, 0.0), inner));
    Plane::XY.at(v3(0.0, 0.0, bottom)).extrude(&section, top - bottom)
}

/// The ring with both lower edges cut back 45° by `lead`, so the press fit starts on them.
fn led_annulus(outer: f64, inner: f64, bottom: f64, top: f64, lead: f64) -> Result<Solid> {
    let section = Profile::polygon(&[
        v2(inner + lead, bottom),
        v2(outer - lead, bottom),
        v2(outer, bottom + lead),
        v2(outer, top),
        v2(inner, top),
        v2(inner, bottom + lead),
    ]);
    Plane::XZ.revolve(&section, 360.0, v2(0.0, 0.0), v2(0.0, 1.0))
}

struct Piece {
    name: &'static str,
    material: &'static str,
    solid: Solid,
}

fn build(n: &Numbers) -> Result<Vec<Piece>> {
    let (core_out, core_in) = (n.f("core_outer_radius")?, n.f("core_inner_radius")?);
    let (insert_bottom, lead) = (n.f("insert_bottom")?, n.f("insertion_lead")?);
    let magnet_seat = n.f("magnet_seat")?;
    let envelope = annulus(n.f("outer_radius")?, n.f("bore_radius")?, 0.0, n.f("height")?)?;
    let interior = annulus(core_out, core_in, n.f("floor")?, n.f("roof_bottom")?)?;
    let pocket = annulus(n.f("pocket_outer_radius")?, n.f("pocket_inner_radius")?, magnet_seat, insert_bottom)?;
    let core = led_annulus(core_out, core_in, n.f("floor")?, insert_bottom, lead)?.cut(&pocket)?;
    let insert = led_annulus(core_out, core_in, insert_bottom, n.f("insert_top")?, lead)?;
    let magnet = annulus(
        n.f("magnet_outer_radius")?,
        n.f("magnet_inner_radius")?,
        magnet_seat,
        magnet_seat + n.f("magnet_height")?,
    )?;
    Ok(vec![
        Piece { name: "body-petg", material: "petg", solid: envelope.cut(&interior)? },
        Piece { name: "body-aero", material: "aero", solid: core },
        Piece { name: "insert-aero", material: "aero", solid: insert },
        Piece { name: "magnet", material: "magnet", solid: magnet },
    ])
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let pieces = build(&n)?;
    let color = |p: &Piece| n.color(&format!("color_{}", p.material));
    let (diameter, height) = (n.f("diameter")?, n.f("height")?);
    let half = Solid::cuboid(v3(-diameter / 2.0 - 1.0, -diameter, -1.0), v3(diameter / 2.0 + 1.0, 0.0, height + 1.0));
    let (mut whole, mut section, mut exploded) = (vec![], vec![], vec![]);
    let mut volumes = serde_json::Map::new();
    for p in &pieces {
        let c = color(p)?;
        let bottom = match p.name {
            "body-aero" => n.f("floor")?,
            "insert-aero" => n.f("insert_bottom")?,
            _ => 0.0,
        };
        let print = p.solid.translate(v3(0.0, 0.0, -bottom));
        write_payload(out.join(format!("{}.step.mesh", p.name)), &[Body { name: p.name, color: Some(c), solid: &print }], None, None)?;
        if p.name != "magnet" {
            write_stl(out.join(format!("{}.stl", p.name)), &[&print])?;
        }
        let lift = match p.name {
            "insert-aero" => INSERT_LIFT,
            "magnet" => MAGNET_LIFT,
            _ => 0.0,
        };
        whole.push((p.name, c, p.solid.clone()));
        section.push((p.name, c, p.solid.intersect(&half)?));
        exploded.push((p.name, c, p.solid.translate(v3(0.0, 0.0, lift))));
        volumes.insert(p.name.into(), json!(p.solid.volume()));
    }
    for (file, view) in [("magnetic-float", &whole), ("section", &section), ("exploded", &exploded)] {
        let bodies: Vec<Body> = view.iter().map(|(name, c, s)| Body { name, color: Some(*c), solid: s }).collect();
        write_payload(out.join(format!("{file}.step.mesh")), &bodies, None, None)?;
    }
    println!("{}", json!({ "volume_mm3": volumes }));
    Ok(())
}
