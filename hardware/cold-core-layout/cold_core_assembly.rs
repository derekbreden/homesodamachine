//! The populated cold core in the foam assembly's source frame.
mod core_fittings;
mod core_metrics;
mod core_parts;
mod core_routes;

use anyhow::{Context, Result};
use core_fittings::{number as f, point as p};
use core_parts::Piece;
use hsm_kernel::part::{AssemblyBody, Numbers, args, write_assembly};
use hsm_kernel::*;

struct Route {
    name: String,
    bend: f64,
    points: Vec<V3>,
    color: Option<[f64; 3]>,
    fine: Solid,
}

fn install_route(name: &str, route: Solid, numbers: &Numbers) -> Result<Solid> {
    if name != "prv-vent" {
        return Ok(route);
    }
    let bounds = route.bounds();
    let keep = Plane::XY.at(bounds.min - v3(1., 1., 1.)).extrude(
        &Profile::rect(
            v2(
                (bounds.max.x - bounds.min.x + 2.) / 2.,
                (f(numbers.get("routing")?, "prv_flank_y")? - bounds.min.y + 1.) / 2.,
            ),
            bounds.max.x - bounds.min.x + 2.,
            f(numbers.get("routing")?, "prv_flank_y")? - bounds.min.y + 1.,
        ),
        bounds.max.z - bounds.min.z + 2.,
    )?;
    route.intersect(&keep)
}

fn routes(numbers: &Numbers, pieces: &[Piece]) -> Result<Vec<Route>> {
    let rows = numbers.get("routes")?.as_array().context("route rows")?;
    let dim = numbers.get("routing")?;
    let tail_names = dim["tail_names"].as_array().context("tail names")?;
    let ladder: Vec<f64> = dim["ladder"]
        .as_array()
        .context("bend ladder")?
        .iter()
        .map(|v| v.as_f64().context("bend ladder rung"))
        .collect::<Result<_>>()?;
    let mut routes = vec![];
    for row in rows {
        let name = row["name"].as_str().context("route name")?;
        let points: Vec<V3> = row["points"]
            .as_array()
            .context("route points")?
            .iter()
            .map(p)
            .collect::<Result<_>>()?;
        let exempt = row["exempt"].as_array().context("route exemptions")?;
        let mut names: Vec<&str> = vec![];
        let mut obstacles: Vec<Vec<&Solid>> = vec![];
        for piece in pieces {
            if piece.name.starts_with("foam-cap")
                || tail_names
                    .iter()
                    .any(|v| v.as_str() == Some(piece.name.as_str()))
                || exempt
                    .iter()
                    .any(|v| v.as_str() == Some(piece.name.as_str()))
            {
                continue;
            }
            // A native compound is one obstacle. Its disjoint components' shared volumes add;
            // their authoritative model slots remain separate and never pass through compose.
            if let Some(index) = names.iter().position(|&name| name == piece.name) {
                obstacles[index].push(&piece.fine);
            } else {
                names.push(&piece.name);
                obstacles.push(vec![&piece.fine]);
            }
        }
        let (bend, fine) = core_routes::fit_route(
            &points,
            f(dim, "stock_bend")?,
            f(dim, "floor")?,
            &ladder,
            f(dim, "radius")?,
            f(dim, "touch_volume")?,
            &obstacles,
        )?;
        let fine = install_route(name, fine, numbers)?;
        routes.push(Route {
            name: name.to_owned(),
            bend,
            points,
            color: Some(p(&row["color"])?.to_array()),
            fine,
        });
    }
    Ok(routes)
}

fn main() -> Result<()> {
    let (numbers, directory) = args()?;
    let pieces = core_parts::build(&numbers)?;
    let routes = routes(&numbers, &pieces)?;
    let measurements = core_metrics::measure(&numbers, &pieces, &routes)?;
    let ratio = f(numbers.get("presentation")?, "deflection_ratio")?;
    let reduction = f(numbers.get("presentation")?, "simplification_fraction")?;
    let mut low = v3(f64::INFINITY, f64::INFINITY, f64::INFINITY);
    let mut high = -low;
    for fine in pieces
        .iter()
        .map(|p| &p.fine)
        .chain(routes.iter().map(|r| &r.fine))
    {
        let bounds = fine.bounds();
        low = v3(
            low.x.min(bounds.min.x),
            low.y.min(bounds.min.y),
            low.z.min(bounds.min.z),
        );
        high = v3(
            high.x.max(bounds.max.x),
            high.y.max(bounds.max.y),
            high.z.max(bounds.max.z),
        );
    }
    let deflection = |size: V3| (size.x + size.y + size.z) / 3. * ratio;
    let global = deflection(high - low).max(TOLERANCE);
    // Each printed casing piece has the part-local viewer budget used by its standalone
    // print payload. The other live bodies use the assembly's viewer budget. Fine data never
    // passes through this presentation choice.
    let presentation: Vec<Solid> = pieces
        .iter()
        .map(|piece| {
            let bounds = piece.fine.bounds();
            let tolerance = if piece.printed_presentation {
                deflection(bounds.max - bounds.min).max(TOLERANCE)
            } else {
                global
            };
            piece
                .fine
                .simplified_to((tolerance * reduction).max(TOLERANCE))
        })
        .chain(routes.iter().map(|route| {
            route
                .fine
                .simplified_to((global * reduction).max(TOLERANCE))
        }))
        .collect::<Result<_>>()?;
    let route_names: Vec<String> = routes.iter().map(|r| format!("line-{}", r.name)).collect();
    let bodies: Vec<AssemblyBody> = pieces
        .iter()
        .zip(&presentation)
        .map(|(piece, shown)| AssemblyBody {
            name: &piece.name,
            color: piece.color,
            fine: &piece.fine,
            presentation: shown,
        })
        .chain(
            routes
                .iter()
                .zip(&route_names)
                .zip(&presentation[pieces.len()..])
                .map(|((route, name), shown)| AssemblyBody {
                    name,
                    color: route.color,
                    fine: &route.fine,
                    presentation: shown,
                }),
        )
        .collect();
    let mut answer = write_assembly(
        &directory,
        "cold-core-assembly",
        &bodies,
        Some(numbers.get("document")?),
    )?;
    answer["bodies"][0]["measurements"] = measurements;
    println!("{answer}");
    Ok(())
}
