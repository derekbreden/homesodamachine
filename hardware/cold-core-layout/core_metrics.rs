//! Existing cold-core scorecard readings from the authoritative live solids.
use crate::{Route, core_parts::Piece, core_routes};
use anyhow::{Context, Result};
use hsm_kernel::part::Numbers;
use hsm_kernel::*;
use serde_json::{Value, json};
use std::collections::BTreeMap;

fn number(value: &Value, key: &str) -> Result<f64> {
    value[key]
        .as_f64()
        .with_context(|| format!("measurement number {key}"))
}

fn shared(a: &[&Solid], b: &[&Solid]) -> Result<f64> {
    let mut volume = 0.;
    for a in a {
        for b in b {
            volume += a.shared_volume(b)?;
        }
    }
    Ok(volume)
}

pub fn measure(numbers: &Numbers, pieces: &[Piece], routes: &[Route]) -> Result<Value> {
    let mut bodies: BTreeMap<&str, Vec<&Solid>> = BTreeMap::new();
    for piece in pieces {
        bodies.entry(&piece.name).or_default().push(&piece.fine);
    }
    let card = numbers.get("card")?;
    let touch = number(card, "touch_volume")?;
    let mut skip = vec![];
    for key in ["joined", "rides_on"] {
        for pair in card[key].as_array().context("joined/ride pairs")? {
            skip.push((
                pair[0].as_str().context("pair first name")?,
                pair[1].as_str().context("pair second name")?,
            ));
        }
    }
    let mut body_overlaps = vec![];
    let names: Vec<&str> = bodies.keys().copied().collect();
    for (i, &a) in names.iter().enumerate() {
        for &b in &names[i + 1..] {
            if skip.contains(&(a, b)) {
                continue;
            }
            let volume = shared(&bodies[a], &bodies[b])?;
            if volume > touch {
                body_overlaps.push(json!({"a":a,"b":b,"volume":volume}));
            }
        }
    }
    let tail_names = numbers.get("routing")?["tail_names"]
        .as_array()
        .context("tail names")?;
    let route_rows = numbers.get("routes")?.as_array().context("route rows")?;
    let mut route_overlaps = vec![];
    for route in routes {
        let row = route_rows
            .iter()
            .find(|row| row["name"].as_str() == Some(route.name.as_str()))
            .context("route measurement row")?;
        let exempt = row["exempt"].as_array().context("route exemptions")?;
        for (&name, components) in &bodies {
            if tail_names
                .iter()
                .chain(exempt)
                .any(|n| n.as_str() == Some(name))
            {
                continue;
            }
            let volume = shared(&[&route.fine], components)?;
            if volume > touch {
                route_overlaps.push(json!({"a":route.name,"b":name,"volume":volume}));
            }
        }
    }
    let mut runs: BTreeMap<&str, Vec<&Solid>> = BTreeMap::new();
    for route in routes {
        runs.insert(&route.name, vec![&route.fine]);
    }
    for (&name, components) in &bodies {
        if tail_names.iter().any(|n| n.as_str() == Some(name))
            || name.starts_with("tube-soda-core-")
        {
            runs.insert(name, components.clone());
        }
    }
    let run_names: Vec<&str> = runs.keys().copied().collect();
    let mut run_overlaps = vec![];
    for (i, &a) in run_names.iter().enumerate() {
        for &b in &run_names[i + 1..] {
            let volume = shared(&runs[a], &runs[b])?;
            if volume > touch {
                run_overlaps.push(json!({"a":a,"b":b,"volume":volume}));
            }
        }
    }
    let mut reservoir_walls = serde_json::Map::new();
    let internal = numbers.get("internals")?;
    let station_y = number(internal, "RES_ROD_Y")?;
    let middle_z = (internal["FLOAT_TRAVEL_Z"][0]
        .as_f64()
        .context("travel floor")?
        + internal["FLOAT_TRAVEL_Z"][1]
            .as_f64()
            .context("travel ceiling")?)
        / 2.;
    for (letter, side, name) in [("a", 1., "reservoir-a"), ("b", -1., "reservoir-b")] {
        let Some(components) = bodies.get(name) else {
            continue;
        };
        let far = if side > 0. {
            components
                .iter()
                .map(|s| s.bounds().max.x)
                .fold(f64::NEG_INFINITY, f64::max)
        } else {
            components
                .iter()
                .map(|s| s.bounds().min.x)
                .fold(f64::INFINITY, f64::min)
        };
        let step = 0.05;
        let mut reach = number(internal, "RES_ROD_X")?;
        let mut wall = far.abs();
        while reach < far.abs() + step {
            let x = side * reach;
            let bar = Plane::XY
                .at(v3(x.min(x + side * step), station_y - 0.5, middle_z - 0.5))
                .extrude(&Profile::rect(v2(step / 2., 0.5), step, 1.), 1.)?;
            if shared(&[&bar], components)? > 1e-9 {
                wall = reach;
                break;
            }
            reach += step;
        }
        reservoir_walls.insert(letter.to_owned(), json!(wall));
    }
    let route_metrics: Vec<Value> = routes
        .iter()
        .map(|route| -> Result<Value> {
            let (corners, radii) = core_routes::corner_radii(&route.points, route.bend)?;
            Ok(json!({"name":route.name,"bend":route.bend,"radii":radii,
                  "corner_points":corners.iter().map(|p|p.to_array()).collect::<Vec<_>>(),
                  "points":route.points.iter().map(|p|p.to_array()).collect::<Vec<_>>(),
                  "length":core_routes::developed_length(&route.points, route.bend)?,
                  "reach":(route.points[route.points.len()-1]-route.points[0]).norm()}))
        })
        .collect::<Result<_>>()?;
    Ok(
        json!({"body_overlaps":body_overlaps,"route_overlaps":route_overlaps,
              "run_overlaps":run_overlaps,"reservoir_walls":reservoir_walls,
              "routes":route_metrics,"mouths":numbers.get("mouths")?}),
    )
}
