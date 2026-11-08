//! The relay reference preserves observed components around its measured PCB mounting datums.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Body, Loop, Plane, Profile, Solid, V3, import, part, v2, v3};
use serde_json::Value;
use std::path::PathBuf;

fn number(v: &Value) -> Result<f64> {
    v.as_f64().context("expected a measured number")
}

fn point(v: &Value) -> Result<V3> {
    Ok(v3(number(&v[0])?, number(&v[1])?, number(&v[2])?))
}

fn srgb(c: [f64; 3]) -> [f64; 3] {
    c.map(|x| if x <= 0.04045 { x / 12.92 } else { ((x + 0.055) / 1.055).powf(2.4) })
}

fn main() -> Result<()> {
    let mut args = std::env::args().skip(1);
    let input = PathBuf::from(args.next().context("observed exterior NPZ")?);
    let datums = PathBuf::from(args.next().context("scan datums JSON")?);
    let out = PathBuf::from(args.next().context("reference output directory")?);
    let data: Value = serde_json::from_slice(&std::fs::read(datums)?)?;
    let measured = import::model(input)?;
    let observed = &measured.first().context("observed exterior is empty")?.solid;
    let pcb = &data["pcb"];
    let size = point(&pcb["size_mm"])?;
    let center = point(&pcb["center_mm"])?;
    let outline = Loop::rounded_rect(v2(center.x, center.y), size.x, size.y,
                                    number(&pcb["corner_radius_mm"])?)?;
    let plane = Plane::new(v3(0., 0., center.z), V3::X, V3::Z)?;
    let mut board = plane.extrude(&Profile::new(outline), size.z)?;
    for hole in data["holes"].as_array().context("mounting holes")? {
        let p = point(&hole["center_mm"])?;
        let bore = Solid::cylinder(v3(p.x, p.y, center.z - size.z), V3::Z,
                                   number(&hole["radius_mm"])?, size.z * 3.)?;
        board = board.cut(&bore)?;
    }
    let mut pieces = vec![("pcb".to_owned(), srgb([0.08, 0.34, 0.21]), board)];
    for component in data["components"].as_array().context("component regions")? {
        let name = component["name"].as_str().context("component name")?;
        let region = Solid::cuboid(point(&component["min_mm"])?, point(&component["max_mm"])?);
        let body = observed.intersect(&region)?;
        ensure!(!body.is_empty(), "empty observed component {name}");
        body.check()?;
        let c = point(&component["color_srgb"])?.to_array();
        pieces.push((name.to_owned(), srgb(c), body));
    }
    for feature in data["underside_features"].as_array().context("observed underside features")? {
        let name = feature["name"].as_str().context("underside feature name")?;
        let points: Vec<_> = feature["hull_vertices_mm"].as_array().context("solder envelope")?
            .iter().map(point).collect::<Result<_>>()?;
        pieces.push((name.to_owned(), srgb([0.65, 0.67, 0.69]), Solid::hull(&points)?));
    }
    let bodies: Vec<_> = pieces.iter().map(|(name, color, solid)| Body {
        name, color: Some(*color), solid,
    }).collect();
    println!("{}", part::write_shown(&out, "teyleten-relay", &bodies)?);
    Ok(())
}
