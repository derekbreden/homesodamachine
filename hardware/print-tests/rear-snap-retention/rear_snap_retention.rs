//! Complete retention witnesses cropped from actual production print surfaces.
use anyhow::{Context, Result, ensure};
use hsm_kernel::part::{args, write_part, write_shown};
use hsm_kernel::*;
use serde_json::{Value, json};

fn point(v: &Value) -> Result<V3> {
    let a = v.as_array().context("three-vector")?;
    ensure!(a.len() == 3, "three-vector");
    Ok(v3(a[0].as_f64().context("x")?, a[1].as_f64().context("y")?, a[2].as_f64().context("z")?))
}
fn one(path: &str) -> Result<Solid> {
    let mut bodies = import::model(path)?;
    ensure!(bodies.len() == 1, "one production print in {path}");
    Ok(bodies.remove(0).solid)
}
fn centered(s: &Solid) -> Solid {
    let b = s.bounds();
    s.translate(v3(-(b.min.x + b.max.x)/2., -(b.min.y + b.max.y)/2., -b.min.z))
}
fn main() -> Result<()> {
    let (n, out) = args()?;
    let rear = one(n.text("rear_print_model")?)?;
    let lid = one(n.text("lid_print_model")?)?
        .rotate(V3::ZERO, V3::Z, -90.).translate(point(n.get("lid_translation")?)?);
    let caps = import::model(n.text("installed_caps")?)?;
    let mut report = serde_json::Map::new();
    let mut context: Vec<(String, Option<[f64;3]>, Solid)> = vec![];
    for row in n.get("families")?.as_array().context("families")? {
        let name = row["name"].as_str().context("family name")?;
        let clip = Solid::cuboid(point(&row["crop_min"] )?, point(&row["crop_max"])?);
        let seat = (if name == "pump" { &lid } else { &rear }).intersect(&clip)?;
        ensure!(seat.components().len() == 1, "{name}: cropped parent is one solid");
        let print_cap = one(row["cap_print_model"].as_str().context("cap print")?)?;
        let cap = if name == "pump" {
            print_cap.rotate(V3::ZERO, V3::X, -90.)
                .translate(point(&row["cap_translation"])? )
        } else {
            import::body(&caps, row["installed_name"].as_str().context("installed cap")?)?.clone()
        };
        let on = point(&row["on"])?;
        let overlap = seat.shared_volume(&cap)?;
        let blocked = seat.shared_volume(&cap.translate(on * -0.5))?;
        ensure!(overlap < 0.02, "{name}: seated overlap {overlap} mm3");
        ensure!(blocked > 1., "{name}: pullout needs a retaining shoulder ({blocked} mm3)");
        report.insert(name.to_owned(), json!({"seated_intersection_mm3":overlap,
            "blocked_pullout_intersection_mm3":blocked,"pullout_travel_mm":0.5,
            "crop_min":row["crop_min"],"crop_max":row["crop_max"],
            "retention_scope":row["retention_scope"],"physical_result":"Awaiting this trial."}));
        let print_seat = centered(&if name == "pump" {seat.clone()} else {seat.rotate(V3::ZERO,V3::Y,180.)});
        for (suffix, solid) in [("seat", &print_seat), ("cap", &print_cap)] {
            ensure!(solid.components().len() == 1, "{name}-{suffix}: one solid");
            let key = format!("{name}-{suffix}");
            println!("{}",write_part(&out, &key, &[Body{name:&key,color:Some([0.025;3]),solid}])?);
        }
        context.push((format!("{name}-seat"),Some([0.18;3]),seat));
        context.push((format!("{name}-cap"),Some([0.04;3]),cap));
    }
    if n.get("check_fit")?.as_bool().unwrap_or(false) {
        import::visit_model(n.text("assembly_model")?, |_, body| {
            let family = if body.name.starts_with("cold-core/g-ganen-pump/") { Some("pump") }
                else if ["asse1022-assembly","bulkhead-water","gagira-coupling","jg-pi4512f6s","jg-pp061208w","asse-drain-adapter"].contains(&body.name.as_str()) {Some("asse")}
                else if body.name.starts_with("gas-regulator/") || ["co2-inlet","gas-check"].contains(&body.name.as_str()) {Some("pisco")}
                else if body.name.starts_with("digiten-flow/") || ["bulkhead-carb","bulkhead-carb-nut"].contains(&body.name.as_str()) {Some("meter")}
                else if body.name == "flow-regulator" {Some("regulator")} else {None};
            if let Some(family) = family {
                let mut overlaps = serde_json::Map::new();
                for suffix in ["seat","cap"] {
                    let part = &context.iter().find(|p|p.0 == format!("{family}-{suffix}")).unwrap().2;
                    overlaps.insert(suffix.to_owned(), part.shared_volume(&body.solid)?.into());
                }
                report.get_mut(family).unwrap()["hardware_overlap_mm3"][&body.name] = json!(overlaps);
                context.push((body.name,body.color,body.solid));
            }
            Ok(())
        })?;
    }
    let bodies = context.iter().map(|(name,color,solid)|Body{name,color:*color,solid}).collect::<Vec<_>>();
    println!("{}",write_shown(&out,"full-retention-installed",&bodies)?);
    std::fs::write(out.join("fit.json"),serde_json::to_vec_pretty(&report)?)?;
    Ok(())
}
