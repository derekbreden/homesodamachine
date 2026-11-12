//! foam-fill makes the foam-fill test pieces for the printer and the fill model's prediction of a
//! pour in each for the site's /foam page.
mod parts;

use anyhow::{Context, Result, bail};
use hsm_foam::read::{self, Clock};
use hsm_foam::sim::{self, Foam, Pour, Setup};
use hsm_foam::voxel::{self, Grid};
use hsm_kernel::part::write_part;
use hsm_kernel::{Body, Solid};
use parts::{Place, Read};
use serde_json::{Value, json};
use std::path::{Path, PathBuf};

/// The foam as the maker's page and the usual run of two-pound pour foams give it, before any
/// pour here has corrected it. Times count from the start of mixing.
fn prior() -> Foam {
    Foam {
        liquid_density: 1180.,
        expansion: 28.,
        cream: 45.,
        rise_end: 210.,
        rise_shape: 2.,
        viscosity: 0.7,
        cure_exponent: 2.,
        gas_thickening: 3.,
        skin_loss: 0.8,
        skin_depth: 2.5e-3,
        gap_exponent: 2.,
        mobility_cap: 2.5e-5,
    }
}

/// The pieces' colour in a drawing.
const CLEAR_PETG: [f64; 3] = [0.80, 0.88, 0.92];
/// Room above a piece's rim for foam that rises out of it.
const HEADROOM: f64 = 30.;
/// When pouring starts, counted like the foam's clock from the start of mixing.
const POUR_START: f64 = 30.;

struct Piece {
    id: &'static str,
    name: &'static str,
    says: &'static str,
    solid: Solid,
    /// The grid's box and the boxes foam can be in, as the piece is poured.
    bounds: [[f64; 3]; 2],
    active: Vec<[[f64; 3]; 2]>,
    pours: Vec<Pour>,
    places: Vec<Place>,
}

fn pieces() -> Result<Vec<Piece>> {
    let top = parts::TOP + HEADROOM;
    let wall = parts::WALL;

    let column = parts::column()?;
    let side = parts::COLUMN_BORE + 2. * wall;
    let column = Piece {
        id: "column",
        name: "Column",
        says: "One closed tube. It measures the foam itself: how much a gram becomes, and when.",
        solid: column,
        bounds: [[0., 0., 0.], [side, side, top]],
        active: vec![[[0., 0., 0.], [side, side, top]]],
        pours: vec![Pour { at: [side / 2., side / 2., parts::TOP / 2.], grams: 10., start: POUR_START, seconds: 4. }],
        places: parts::column_places(),
    };

    let comb = parts::comb()?;
    let well = parts::WELL + 2. * wall;
    let leg_x = parts::cell_spans().last().expect("cells")[1] + wall;
    let leg_y = parts::leg_spans().last().expect("stations")[1] + wall;
    let cells_back = wall + parts::SUMP_DEPTH + wall;
    let rooms_back = wall + parts::ROOM_DEPTH + wall;
    let comb = Piece {
        id: "comb",
        name: "Comb",
        says: "A pour well at the corner of an L. One leg is cells of five gaps fed from the floor; the other is rooms off the well and two cells fed only over their tops.",
        solid: comb,
        bounds: [[0., 0., 0.], [leg_x, leg_y, top]],
        active: vec![
            [[0., 0., 0.], [well, well, top]],
            [[well - wall, 0., 0.], [leg_x, cells_back, top]],
            [[0., well - wall, 0.], [rooms_back, leg_y, top]],
        ],
        pours: vec![Pour { at: [well / 2., well / 2., parts::TOP / 2.], grams: 45., start: POUR_START, seconds: 8. }],
        places: parts::comb_places(),
    };

    let tray = parts::tray()?;
    let size = [parts::TRAY_LENGTH + 2. * wall, parts::TRAY_WIDTH + 2. * wall, parts::TRAY_GAP + 2. * wall];
    let above = size[2] + 14.;
    let ports = parts::tray_ports();
    let tray = Piece {
        id: "tray",
        name: "Tray",
        says: "Half of the bottom cap's foam space, lying flat as the cap is poured: two ports, and a vent at one end only.",
        solid: tray,
        bounds: [[0., 0., 0.], [size[0], size[1], above]],
        active: vec![[[0., 0., 0.], [size[0], size[1], above]]],
        pours: ports
            .iter()
            .enumerate()
            .map(|(n, port)| Pour { at: [port[0], port[1], size[2] / 2.], grams: 16., start: POUR_START + 6. * n as f64, seconds: 4. })
            .collect(),
        places: parts::tray_places(),
    };
    Ok(vec![column, comb, tray])
}

fn main() -> Result<()> {
    let args: Vec<String> = std::env::args().collect();
    match args.get(1).map(String::as_str) {
        Some("parts") if args.len() == 3 => write_parts(Path::new(&args[2])),
        Some("predict") if args.len() >= 3 => {
            let mut h = 2.;
            let mut only = None;
            let mut rest = args[3..].iter();
            while let Some(flag) = rest.next() {
                match flag.as_str() {
                    "--cell" => h = rest.next().context("--cell takes a size in mm")?.parse()?,
                    "--only" => only = Some(rest.next().context("--only takes a piece")?.clone()),
                    other => bail!("unknown option {other}"),
                }
            }
            predict(Path::new(&args[2]), h, only.as_deref())
        }
        _ => bail!("usage: foam-fill parts <dir> | foam-fill predict <dir> [--cell <mm>] [--only <piece>]"),
    }
}

/// The pieces as the printer takes them: each one's STL, with the model files that draw it.
fn write_parts(dir: &Path) -> Result<()> {
    std::fs::create_dir_all(dir)?;
    for piece in pieces()? {
        let printed = if piece.id == "tray" { parts::tray_as_printed(&piece.solid) } else { piece.solid.clone() };
        let body = Body { name: piece.id.into(), color: Some(CLEAR_PETG), solid: &printed };
        println!("{}", write_part(dir, piece.id, &[body])?);
    }
    Ok(())
}

fn predict(dir: &Path, h: f64, only: Option<&str>) -> Result<()> {
    std::fs::create_dir_all(dir)?;
    let foam = prior();
    let mut listed = vec![];
    for piece in pieces()? {
        if only.is_some_and(|id| id != piece.id) {
            continue;
        }
        eprintln!("{}: {} mm cells", piece.id, h);
        let grid = Grid::covering(piece.bounds[0], piece.bounds[1], h);
        let verts: Vec<[f64; 3]> = piece.solid.verts().iter().map(|p| [p.x, p.y, p.z]).collect();
        let solid = voxel::fill(&grid, &verts, piece.solid.tris());
        let setup = Setup { grid: grid.clone(), solid, active: piece.active.clone(), up: 2, pours: piece.pours.clone(), foam: foam.clone(), log_every: 10. };
        let started = std::time::Instant::now();
        let outcome = sim::run(&setup);
        eprintln!(
            "{}: {} steps, {} solver iterations, {:.0} s",
            piece.id,
            outcome.steps,
            outcome.iterations,
            started.elapsed().as_secs_f64()
        );
        listed.push(write_piece(dir, &piece, &setup, &outcome)?);
    }
    if only.is_none() {
        let index = json!({ "foam": foam_json(&foam), "pours": listed });
        write(dir.join("index.json"), serde_json::to_string(&index)?.as_bytes())?;
    }
    Ok(())
}

fn foam_json(foam: &Foam) -> Value {
    json!({
        "liquid_density_kg_m3": foam.liquid_density,
        "expansion": foam.expansion,
        "cream_s": foam.cream,
        "rise_end_s": foam.rise_end,
        "rise_shape": foam.rise_shape,
        "viscosity_pa_s": foam.viscosity,
        "cure_exponent": foam.cure_exponent,
        "gas_thickening": foam.gas_thickening,
        "skin_loss": foam.skin_loss,
        "skin_depth_mm": foam.skin_depth * 1e3,
        "gap_exponent": foam.gap_exponent,
    })
}

fn write(path: PathBuf, bytes: &[u8]) -> Result<()> {
    std::fs::write(&path, bytes).with_context(|| format!("writing {}", path.display()))
}

/// One piece's files for the page: its mesh, its arrival field, and what the run says of it.
fn write_piece(dir: &Path, piece: &Piece, setup: &Setup, outcome: &sim::Outcome) -> Result<Value> {
    let grid = &setup.grid;
    let foam = &setup.foam;
    let start = setup.pours.iter().map(|p| p.start).fold(f64::INFINITY, f64::min);
    let clock = Clock { start, step: (foam.rise_end - start) / 250. };
    let field = read::pack(grid, &outcome.arrival, &clock);
    write(dir.join(format!("{}.field.gz", piece.id)), &read::gzip(&field)?)?;

    let mut mesh = Vec::with_capacity(piece.solid.tris().len() * 36);
    let verts = piece.solid.verts();
    for tri in piece.solid.tris() {
        for &v in tri {
            let p = verts[v as usize];
            for c in [p.x, p.y, p.z] {
                mesh.extend_from_slice(&(c as f32).to_le_bytes());
            }
        }
    }
    write(dir.join(format!("{}.mesh.gz", piece.id)), &read::gzip(&mesh)?)?;

    let times: Vec<f64> = (0..=((foam.rise_end - start).round() as usize)).map(|s| start + s as f64).collect();
    let round = |v: f64| (v * 10.).round() / 10.;
    let mut places = vec![];
    for place in &piece.places {
        let (kind, unit, series, full) = match place.read {
            Read::Height => ("height", "mm", read::height(grid, &outcome.arrival, 2, place.region, &times), place.region[1][2] - place.region[0][2]),
            Read::Reach => ("reach", "mm", read::reach(grid, &outcome.arrival, 2, place.region, &times), place.region[1][2] - place.region[0][2]),
            Read::Fill => ("fill", "%", read::fill(grid, &outcome.arrival, 2, place.region, &times).iter().map(|f| f * 100.).collect(), 100.),
        };
        let share = read::fill(grid, &outcome.arrival, 2, place.region, &times[times.len() - 1..])[0];
        let volume = read::open_volume(grid, &outcome.arrival, 2, place.region);
        places.push(json!({
            "id": place.id,
            "name": place.name,
            "stands_for": place.stands_for,
            "read": kind,
            "unit": unit,
            "region": place.region,
            "full": full,
            "value": round(*series.last().expect("a reading at the end")),
            "filled_percent": round(share * 100.),
            "air_ml": round(volume * (1. - share) / 1000.),
            "series": series.iter().map(|&v| round(v)).collect::<Vec<_>>(),
        }));
    }
    let last = outcome.samples.last().context("the run sampled nothing")?;
    // Foam that ends above the piece: over its rim, or gone from the grid.
    let rim = piece.solid.bounds().max.z;
    let over_rim = (0..grid.n[2])
        .filter(|&k| grid.centre(0, 0, k)[2] > rim)
        .flat_map(|k| (0..grid.n[1]).flat_map(move |j| (0..grid.n[0]).map(move |i| (i, j, k))))
        .filter(|&(i, j, k)| outcome.arrival[grid.index(i, j, k)].is_finite())
        .count() as f64
        * grid.h.powi(3);
    let summary = json!({
        "id": piece.id,
        "name": piece.name,
        "says": piece.says,
        "cell_mm": grid.h,
        "grid": { "origin": grid.origin, "n": grid.n },
        "clock": { "start_s": clock.start, "step_s": clock.step, "end_s": foam.rise_end },
        "field": format!("{}.field.gz", piece.id),
        "mesh": format!("{}.mesh.gz", piece.id),
        "triangles": piece.solid.tris().len(),
        "pours": setup.pours.iter().map(|p| json!({ "at": p.at, "grams": p.grams, "start_s": p.start, "seconds": p.seconds })).collect::<Vec<_>>(),
        "poured_ml": round(outcome.poured / 1000.),
        "foam_ml": round((last.inside + last.spilled) / 1000.),
        "out_of_the_piece_ml": round((over_rim + last.spilled) / 1000.),
        "times_s": times,
        "foam_ml_series": outcome.samples.iter().map(|s| round((s.inside + s.spilled) / 1000.)).collect::<Vec<_>>(),
        "places": places,
    });
    write(dir.join(format!("{}.json", piece.id)), serde_json::to_string(&summary)?.as_bytes())?;
    Ok(json!({ "id": piece.id, "name": piece.name, "says": piece.says, "file": format!("{}.json", piece.id) }))
}
