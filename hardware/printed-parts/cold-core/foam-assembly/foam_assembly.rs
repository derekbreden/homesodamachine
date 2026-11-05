//! The casing stack in its source frame, from the printed parts' authoritative f64 models.
#[path = "../../../cold-core-layout/core_routes.rs"]
#[allow(dead_code)]
mod core_routes;
use anyhow::{Context, Result};
use hsm_kernel::part::{AssemblyBody, Numbers, args, write_assembly};
use hsm_kernel::*;
use serde_json::{Value, json};

struct Piece {
    name: String,
    color: Option<[f64; 3]>,
    fine: Solid,
}

fn point(value: &Value) -> Result<V3> {
    Ok(v3(
        value[0].as_f64().context("translation x")?,
        value[1].as_f64().context("translation y")?,
        value[2].as_f64().context("translation z")?,
    ))
}

fn stack(numbers: &Numbers) -> Result<Vec<Piece>> {
    let mut pieces = vec![];
    for row in numbers
        .get("models")?
        .as_array()
        .context("stack model rows")?
    {
        let name = row["name"].as_str().context("stack body name")?;
        let path = row["model"].as_str().context("explicit fine model path")?;
        let angle = row["rotation_z_degrees"]
            .as_f64()
            .context("stack rotation")?;
        let shift = point(&row["translation"])?;
        let rgb = point(&row["color"])?;
        // Keep every imported component and record slot in order. Composing them would
        // canonicalize face slots that may carry distinct native Manifold constraints.
        for imported in import::model(path)? {
            let mut fine = imported.solid;
            if angle != 0. {
                fine = fine.rotate(V3::ZERO, v3(0., 0., 1.), angle);
            }
            if shift != V3::ZERO {
                fine = fine.translate(shift);
            }
            pieces.push(Piece {
                name: name.to_owned(),
                color: Some(rgb.to_array()),
                fine,
            });
        }
    }
    Ok(pieces)
}

fn number(value: &Value, key: &str) -> Result<f64> {
    value[key]
        .as_f64()
        .with_context(|| format!("foam number {key}"))
}

fn obstacles(numbers: &Numbers, pieces: &[Piece]) -> Result<Vec<(String, Vec<Solid>)>> {
    let mut obstacles = vec![(
        "the foam shell".to_owned(),
        pieces
            .iter()
            .filter(|p| p.name == "foam-shell")
            .map(|p| p.fine.clone())
            .collect(),
    )];
    let dim = numbers.get("envelope")?;
    let cylinder = |radius: &str, span: &str| -> Result<Solid> {
        let z0 = dim[span][0].as_f64().context("envelope floor")?;
        let z1 = dim[span][1].as_f64().context("envelope top")?;
        Solid::cylinder(V3::Z * z0, V3::Z, number(dim, radius)?, z1 - z0)
    };
    let envelope = cylinder("tank_radius", "tank_z")?.union(&cylinder("coil_radius", "coil_z")?)?;
    obstacles.push(("the carbonator".to_owned(), vec![envelope]));
    for row in numbers
        .get("obstacles")?
        .as_array()
        .context("obstacle rows")?
    {
        let shift = point(&row["translation"])?;
        let parts = import::model(row["model"].as_str().context("obstacle fine model")?)?
            .into_iter()
            .map(|part| {
                if shift == V3::ZERO {
                    part.solid
                } else {
                    part.solid.translate(shift)
                }
            })
            .collect();
        obstacles.push((
            row["name"].as_str().context("obstacle name")?.to_owned(),
            parts,
        ));
    }
    Ok(obstacles)
}

fn trimmed(name: &str, fine: &Solid, numbers: &Numbers) -> Result<Solid> {
    if name != "prv-vent" {
        return Ok(fine.clone());
    }
    let b = fine.bounds();
    let high_y = number(numbers.get("routing")?, "prv_flank_y")?;
    let keep = Plane::XY.at(b.min - v3(1., 1., 1.)).extrude(
        &Profile::rect(
            v2((b.max.x - b.min.x + 2.) / 2., (high_y - b.min.y + 1.) / 2.),
            b.max.x - b.min.x + 2.,
            high_y - b.min.y + 1.,
        ),
        b.max.z - b.min.z + 2.,
    )?;
    fine.intersect(&keep)
}

fn main() -> Result<()> {
    let (numbers, out) = args()?;
    let pieces = stack(&numbers)?;
    let ratio = number(numbers.get("presentation")?, "deflection_ratio")?;
    let reduction = number(numbers.get("presentation")?, "simplification_fraction")?;
    let presentation: Vec<Solid> = pieces
        .iter()
        .map(|piece| {
            let b = piece.fine.bounds();
            let size = b.max - b.min;
            piece
                .fine
                .simplified_to(((size.x + size.y + size.z) / 3. * ratio * reduction).max(TOLERANCE))
        })
        .collect::<Result<_>>()?;
    let bodies: Vec<AssemblyBody> = pieces
        .iter()
        .zip(&presentation)
        .map(|(piece, shown)| AssemblyBody {
            name: &piece.name,
            color: piece.color,
            fine: &piece.fine,
            presentation: shown,
        })
        .collect();
    let answer = write_assembly(
        &out,
        "foam-assembly",
        &bodies,
        Some(numbers.get("document")?),
    )?;
    println!("{answer}");

    let obstacles = obstacles(&numbers, &pieces)?;
    let borrowed: Vec<Vec<&Solid>> = obstacles
        .iter()
        .map(|(_, solids)| solids.iter().collect())
        .collect();
    let dim = numbers.get("routing")?;
    let ladder: Vec<f64> = dim["ladder"]
        .as_array()
        .context("bend ladder")?
        .iter()
        .map(|v| v.as_f64().context("bend rung"))
        .collect::<Result<_>>()?;
    let mut routes = vec![];
    for row in numbers.get("routes")?.as_array().context("routes")? {
        let name = row["name"].as_str().context("route name")?;
        let points: Vec<V3> = row["points"]
            .as_array()
            .context("route points")?
            .iter()
            .map(point)
            .collect::<Result<_>>()?;
        let (_, tube) = core_routes::fit_route(
            &points,
            number(dim, "stock_bend")?,
            number(dim, "floor")?,
            &ladder,
            number(dim, "radius")?,
            number(dim, "touch_volume")?,
            &borrowed,
        )?;
        routes.push(Piece {
            name: name.to_owned(),
            color: Some(point(&row["color"])?.to_array()),
            fine: trimmed(name, &tube, &numbers)?,
        });
    }
    let shown: Vec<Solid> = routes
        .iter()
        .map(|route| route.fine.simplified())
        .collect::<Result<_>>()?;
    let bodies: Vec<AssemblyBody> = routes
        .iter()
        .zip(&shown)
        .map(|(route, shown)| AssemblyBody {
            name: &route.name,
            color: route.color,
            fine: &route.fine,
            presentation: shown,
        })
        .collect();
    let document =
        json!({"frame":"foam assembly source","schema":"hsm-cold-core-internal-routes-1"});
    let answer = write_assembly(&out, "internal-routes", &bodies, Some(&document))?;
    println!("{answer}");
    Ok(())
}
