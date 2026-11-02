//! The casing stack in its source frame, from the printed parts' authoritative f64 models.
#[path = "../../../cold-core-layout/core_routes.rs"]
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

fn shared(a: &Solid, b: &[Solid]) -> Result<f64> {
    b.iter()
        .try_fold(0., |total, solid| Ok(total + a.shared_volume(solid)?))
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

fn report(numbers: &Numbers, pieces: &[Piece]) -> Result<Value> {
    let data = numbers.get("report")?;
    let shell = pieces
        .iter()
        .find(|p| p.name == "foam-shell")
        .context("foam shell")?;
    let bottom = pieces
        .iter()
        .find(|p| p.name == "foam-cap-bottom")
        .context("bottom closure")?;
    let co2: Vec<V3> = data["co2_points"]
        .as_array()
        .context("CO2 points")?
        .iter()
        .map(point)
        .collect::<Result<_>>()?;
    let path = core_routes::route_path(&co2, number(numbers.get("routing")?, "stock_bend")?)?;
    let (start, end) = path
        .legs
        .iter()
        .rev()
        .find_map(|leg| match leg {
            Leg::Line { a, b } => Some((*a, *b)),
            _ => None,
        })
        .context("CO2 last straight")?;
    let reach = end - start;
    let co2_probe = Solid::cylinder(
        start,
        reach.unit(),
        number(data, "co2_radius")?,
        reach.norm(),
    )?;
    let mut passages = vec![];
    for probe in data["probes"].as_array().context("passage probes")? {
        let radius = number(probe, "radius")?;
        let shape = if probe["kind"] == "route" {
            let points: Vec<V3> = probe["points"]
                .as_array()
                .context("probe points")?
                .iter()
                .map(point)
                .collect::<Result<_>>()?;
            core_routes::build_route(&points, number(probe, "bend")?, radius)?
        } else {
            Solid::cylinder(
                point(&probe["at"])?,
                V3::Z,
                radius,
                number(probe, "height")?,
            )?
        };
        let b = bottom.fine.bounds();
        let xy = &probe["lower_xy"];
        let lower = Solid::cylinder(
            v3(
                xy[0].as_f64().context("lower x")?,
                xy[1].as_f64().context("lower y")?,
                b.min.z - 2.,
            ),
            V3::Z,
            number(data, "lower_probe_radius")?,
            b.max.z - b.min.z + 4.,
        )?;
        let blocked: Vec<Value> = pieces
            .iter()
            .filter(|p| p.name == "foam-shell" || p.name == "foam-cap-lid-top")
            .map(|part| Ok(json!({"name":part.name,"volume":part.fine.shared_volume(&shape)?})))
            .collect::<Result<_>>()?;
        passages.push(
            json!({"name":probe["name"],"mouth":probe["mouth"],"blocked":blocked,
                             "bottom_open":bottom.fine.shared_volume(&lower)? <= 1e-6}),
        );
    }
    let mut screw_paths = vec![];
    for part in pieces
        .iter()
        .filter(|p| p.name == "foam-cap-lid-top" || p.name == "foam-cap-bottom")
    {
        let bounds = part.fine.bounds();
        for xy in data["screw_xy"].as_array().context("screw stations")? {
            let at = v3(
                xy[0].as_f64().context("screw x")?,
                xy[1].as_f64().context("screw y")?,
                bounds.min.z - 2.,
            );
            let probe = Solid::cylinder(
                at,
                V3::Z,
                number(data, "screw_probe_radius")?,
                bounds.max.z - bounds.min.z + 4.,
            )?;
            screw_paths
                .push(json!({"name":part.name,"xy":xy,"blocked":part.fine.shared_volume(&probe)?}));
        }
    }
    let mut clashes = vec![];
    for i in 0..pieces.len() {
        for j in i + 1..pieces.len() {
            clashes.push(json!({"a":pieces[i].name,"b":pieces[j].name,
                                "volume":pieces[i].fine.shared_volume(&pieces[j].fine)?}));
        }
    }
    Ok(
        json!({"co2":{"start":start.to_array(),"end":end.to_array(),"length":reach.norm(),
                       "blocked":shell.fine.shared_volume(&co2_probe)?},
              "passages":passages,"screw_paths":screw_paths,"clashes":clashes}),
    )
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
    let mut answer = write_assembly(
        &out,
        "foam-assembly",
        &bodies,
        Some(numbers.get("document")?),
    )?;
    answer["bodies"][0]["assembly_report"] = report(&numbers, &pieces)?;
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
    let mut untrimmed = vec![];
    let mut measurements = vec![];
    for row in numbers.get("routes")?.as_array().context("routes")? {
        let name = row["name"].as_str().context("route name")?;
        let points: Vec<V3> = row["points"]
            .as_array()
            .context("route points")?
            .iter()
            .map(point)
            .collect::<Result<_>>()?;
        let (bend, tube) = core_routes::fit_route(
            &points,
            number(dim, "stock_bend")?,
            number(dim, "floor")?,
            &ladder,
            number(dim, "radius")?,
            number(dim, "touch_volume")?,
            &borrowed,
        )?;
        let (corners, radii) = core_routes::corner_radii(&points, bend)?;
        let blocked: Vec<Value> = obstacles
            .iter()
            .map(|(name, solids)| Ok(json!({"name":name,"volume":shared(&tube, solids)?})))
            .collect::<Result<_>>()?;
        measurements.push(json!({"name":name,"bend":bend,"radii":radii,
                                 "length":core_routes::developed_length(&points,bend)?,
                                 "points":corners.iter().map(|p|p.to_array()).collect::<Vec<_>>(),"blocked":blocked}));
        untrimmed.push(tube.clone());
        routes.push(Piece {
            name: name.to_owned(),
            color: Some(point(&row["color"])?.to_array()),
            fine: trimmed(name, &tube, &numbers)?,
        });
    }
    let mut crossings = vec![];
    for i in 0..routes.len() {
        for j in i + 1..routes.len() {
            crossings.push(json!({"a":routes[i].name,"b":routes[j].name,
                                  "volume":untrimmed[i].shared_volume(&untrimmed[j])?}));
        }
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
    let mut answer = write_assembly(&out, "internal-routes", &bodies, Some(&document))?;
    answer["bodies"][0]["route_report"] = json!({"routes":measurements,"crossings":crossings});
    println!("{answer}");
    Ok(())
}
