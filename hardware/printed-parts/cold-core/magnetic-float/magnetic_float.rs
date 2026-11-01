//! The RC62 magnetic float: a PETG envelope, the ASA Aero core and insert fitted inside it, and
//! the magnet seated between them. `magnetic_float.py` holds the numbers and writes them for this
//! program.
//!
//!     cargo run --release --manifest-path tools/hsm/cold-core/Cargo.toml --bin magnetic-float -- \
//!         <magnetic-float.numbers.json> <out dir>
//!     cargo run --release --manifest-path tools/hsm/cold-core/Cargo.toml --bin magnetic-float -- \
//!         <numbers.json with `check`> --check
//!
//! Frame: guide bore on Z, finished bottom at Z = 0. Each piece is written standing on its own
//! print face; the assembly, its half section and its exploded view stand in the float's frame.
use anyhow::Result;
use hsm_kernel::part::{Numbers, args, write_part, write_shown};
use hsm_kernel::*;
use serde_json::json;

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

/// What `verify.py` asks of the pieces, measured: whether each is one sound solid, and by how
/// much volume they miss the design — every miss zero when the pieces are what the numbers say.
/// `verify.py` writes the lifts the separate pieces are slid in by and the depth of roof the
/// insert must carry under `check`, and asserts on what this prints.
fn check(n: &Numbers, pieces: &[Piece]) -> Result<serde_json::Value> {
    let piece = |name: &str| -> Result<&Solid> {
        pieces.iter().find(|p| p.name == name).map(|p| &p.solid).ok_or_else(|| anyhow::anyhow!("no piece {name}"))
    };
    let (petg, aero, insert, magnet) = (piece("body-petg")?, piece("body-aero")?, piece("insert-aero")?, piece("magnet")?);
    let asked = n.get("check")?;
    let number = |key: &str| asked[key].as_f64().ok_or_else(|| anyhow::anyhow!("check has no number `{key}`"));
    let lifts: Vec<f64> = asked["lifts"].as_array().map(|a| a.iter().filter_map(|x| x.as_f64()).collect()).unwrap_or_default();
    anyhow::ensure!(!lifts.is_empty(), "check has no `lifts`");

    let (core_out, core_in) = (n.f("core_outer_radius")?, n.f("core_inner_radius")?);
    let (floor, roof_bottom, height) = (n.f("floor")?, n.f("roof_bottom")?, n.f("height")?);
    let (insert_bottom, insert_top, lead) = (n.f("insert_bottom")?, n.f("insert_top")?, n.f("insertion_lead")?);
    let (seat, tolerance) = (n.f("magnet_seat")?, n.f("magnet_tolerance")?);
    let envelope = annulus(n.f("outer_radius")?, n.f("bore_radius")?, 0.0, height)?;
    let interior = annulus(core_out, core_in, floor, roof_bottom)?;
    let fill = Solid::union_all(&[aero.clone(), insert.clone(), magnet.clone()])?;
    let pocket = annulus(n.f("pocket_outer_radius")?, n.f("pocket_inner_radius")?, seat, insert_bottom)?;
    let mut allowed = vec![pocket.cut(magnet)?];
    for (bottom, top) in [(floor, insert_bottom), (insert_bottom, insert_top)] {
        allowed.push(annulus(core_out, core_in, bottom, top)?.cut(&led_annulus(core_out, core_in, bottom, top, lead)?)?);
    }
    let allowed = Solid::union_all(&allowed)?;
    let voids = interior.cut(&fill)?;
    let half = n.f("diameter")? / 2.0 + 1.0;
    let open_skin = petg.cut(&Solid::cuboid(v3(-half, -half, roof_bottom), v3(half, half, height + 1.0)))?;
    let largest = annulus(
        n.f("magnet_outer_radius")? + tolerance / 2.0,
        n.f("magnet_inner_radius")? - tolerance / 2.0,
        seat,
        seat + n.f("magnet_height")? + tolerance,
    )?;
    let roof = annulus(core_out, core_in, roof_bottom - number("roof_support_depth")?, roof_bottom)?;

    let mut sound = serde_json::Map::new();
    let mut pair: f64 = 0.0;
    for (i, p) in pieces.iter().enumerate() {
        sound.insert(p.name.into(), json!({ "valid": p.solid.check().is_ok(), "solids": p.solid.components().len() }));
        for q in &pieces[i + 1..] {
            pair = pair.max(p.solid.intersect(&q.solid)?.volume());
        }
    }
    let mut slid = serde_json::Map::new();
    for name in ["body-aero", "insert-aero", "magnet"] {
        let mut most: f64 = 0.0;
        for &lift in &lifts {
            most = most.max(piece(name)?.translate(v3(0.0, 0.0, lift)).intersect(&open_skin)?.volume());
        }
        slid.insert(name.into(), json!(most));
    }
    Ok(json!({
        "pieces": sound,
        "voids_outside_allowed_mm3": voids.cut(&allowed)?.volume(),
        "allowed_outside_voids_mm3": allowed.cut(&voids)?.volume(),
        "fill_outside_interior_mm3": fill.cut(&interior)?.volume(),
        "envelope_left_by_petg_mm3": envelope.cut(&interior)?.cut(petg)?.volume(),
        "largest_pair_overlap_mm3": pair,
        "slid_into_open_skin_mm3": slid,
        "largest_magnet_overlap_mm3": {
            "open_skin": largest.intersect(&open_skin)?.volume(),
            "body-aero": largest.intersect(aero)?.volume(),
            "insert-aero": largest.intersect(insert)?.volume(),
        },
        "roof_unsupported_mm3": roof.cut(insert)?.volume(),
    }))
}

fn main() -> Result<()> {
    if std::env::args().nth(2).as_deref() == Some("--check") {
        let n = Numbers::read(std::env::args().nth(1).unwrap_or_default())?;
        println!("{}", check(&n, &build(&n)?)?);
        return Ok(());
    }
    let (n, out) = args()?;
    let pieces = build(&n)?;
    let (diameter, height) = (n.f("diameter")?, n.f("height")?);
    let half = Solid::cuboid(v3(-diameter / 2.0 - 1.0, -diameter, -1.0), v3(diameter / 2.0 + 1.0, 0.0, height + 1.0));
    let (mut whole, mut section, mut exploded) = (vec![], vec![], vec![]);
    for p in &pieces {
        let c = n.color(&format!("color_{}", p.material))?;
        let bottom = match p.name {
            "body-aero" => n.f("floor")?,
            "insert-aero" => n.f("insert_bottom")?,
            _ => 0.0,
        };
        let print = p.solid.translate(v3(0.0, 0.0, -bottom));
        let body = [Body { name: p.name, color: Some(c), solid: &print }];
        let said = if p.name == "magnet" { write_shown(&out, p.name, &body)? } else { write_part(&out, p.name, &body)? };
        println!("{said}");
        let lift = match p.name {
            "insert-aero" => n.f("insert_lift")?,
            "magnet" => n.f("magnet_lift")?,
            _ => 0.0,
        };
        whole.push((p.name, c, p.solid.clone()));
        section.push((p.name, c, p.solid.intersect(&half)?));
        exploded.push((p.name, c, p.solid.translate(v3(0.0, 0.0, lift))));
    }
    for (file, view) in [("magnetic-float", &whole), ("section", &section), ("exploded", &exploded)] {
        let bodies: Vec<Body> = view.iter().map(|(name, c, s)| Body { name, color: Some(*c), solid: s }).collect();
        println!("{}", write_shown(&out, file, &bodies)?);
    }
    Ok(())
}
