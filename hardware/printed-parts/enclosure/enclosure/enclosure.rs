//! The enclosure step: every printed piece's files from the declared Box, then the enclosure
//! model the site draws, its pieces in place with the pump dock's purchased tees and elbows.
//!
//!     enclosure [--box <declared Box>] [--piece <piece>]... [<output directory>]
//!
//! It runs at the repository root, or a copy of the files it reads at their repository paths,
//! and writes into `hardware/printed-parts/enclosure/enclosure` unless told otherwise. Each
//! `--piece` names a piece to cut, by its files' name without `enclosure-`; with any, it writes
//! only those pieces and no model. `--box` reads another Box document than the declared one.
use anyhow::{Context, Result, bail, ensure};
use hsm_enclosure::catalog::{elbow_color, tee_color, wall_color};
use hsm_enclosure::plan::Graph;
use hsm_enclosure::quadrant::Quadrant;
use hsm_enclosure::shell::{DISPOSAL_MARGIN, DISPOSAL_RAISE, WALL, shell};
use hsm_enclosure::spec::{Box, ColletPlate};
use hsm_enclosure::{backtop, dock, field, front, fronttop, panel, rear, retainer, structure};
use hsm_enclosure_solid::numbers::BackBottomPrint;
use hsm_enclosure_solid::pieces;
use hsm_enclosure_solid::structure::Silhouette;
use hsm_kernel::write::Body;
use hsm_kernel::{Affine, Solid, V3, v3};
use hsm_model_export::model::{Ref, physical_rows};
use std::path::{Path, PathBuf};

const BOX: &str = "hardware/manifold-layout/enclosure-box.json";
const OUTPUT: &str = "hardware/printed-parts/enclosure/enclosure";
/// The tee's drawing: its manifest names no fine model, so the dock places the drawing.
const TEE: &str = "hardware/reference/tee-connector/tee-connector.step.mesh";
/// The stem elbow's fine model, as its manifest names it.
const ELBOW: &str = "hardware/reference/neofit-stem-elbow/neofit-stem-elbow.fine.step.npz";

/// The pieces the enclosure model shows, in its order: each one's files, and its body's name.
const SHOWN: [(&str, &str); 5] = [
    ("enclosure-front-bottom", "enclosure_front_bottom"),
    ("enclosure-front-top", "enclosure_front_top"),
    ("enclosure-back-bottom", "enclosure_back_bottom"),
    ("enclosure-back-top", "enclosure_back_top"),
    ("enclosure-pump-retainer-seated", "enclosure_pump_retainer"),
];

/// Every piece the step cuts, by its files' name without `enclosure-`.
const PIECES: [&str; 6] = ["front-bottom", "front-top", "back-bottom", "back-top", "pump-retainer", "pump-tube-setting-jig"];
const USAGE: &str = "usage: enclosure [--box <declared Box>] [--piece <piece>]... [<output directory>]";

fn main() -> Result<()> {
    let (mut declared, mut pieces, mut out) = (PathBuf::from(BOX), Vec::new(), None);
    let mut args = std::env::args_os().skip(1);
    while let Some(arg) = args.next() {
        match arg.to_str() {
            Some("--box") => declared = args.next().context(USAGE)?.into(),
            Some("--piece") => {
                let piece = args.next().and_then(|p| p.into_string().ok()).context(USAGE)?;
                ensure!(PIECES.contains(&piece.as_str()), "{piece} is none of the pieces: {}", PIECES.join(", "));
                pieces.push(piece);
            }
            _ if out.is_none() => out = Some(PathBuf::from(arg)),
            _ => bail!(USAGE),
        }
    }
    let out = out.unwrap_or_else(|| PathBuf::from(OUTPUT));
    hsm_kernel::reads::begin();
    let document = read(&declared)?;
    let b = Box::from_document(serde_json::from_slice(&document)?).with_context(|| declared.display().to_string())?;
    std::fs::create_dir_all(&out)?;
    let all = pieces.is_empty();
    cut_pieces(&b, &out, |piece| all || pieces.iter().any(|p| p == piece))?;
    if !all {
        return Ok(());
    }
    let mut rows: Vec<Ref> = SHOWN
        .iter()
        .map(|(file, name)| Ref::stored(&out.join(format!("{file}.step.npz")), 0, name, Some(digits(wall_color()))))
        .collect();
    let parts = dock_parts(&b.pack.collet_plate)?;
    let bodies: Vec<Body> = parts.iter().map(|(name, color, solid)| Body { name, color: Some(*color), solid }).collect();
    rows.extend(Ref::made(&bodies)?);
    drop(bodies);
    drop(parts);
    physical_rows("enclosure", rows, &out)
}

/// The printed pieces `cut` names: the four quadrants on one shared silhouette, the pump
/// retainer relaxed for print and seated for show, and the tube-setting jig.
fn cut_pieces(b: &Box, out: &Path, cut: impl Fn(&str) -> bool) -> Result<()> {
    let color = wall_color();
    let structure = structure::structure(&b.outer);
    let silhouette = Silhouette::new(&structure);
    let field = field::field(&b.outer);
    let front_rails = [field::perimeter_rail(&b.outer, rear::front_plain(&b.outer))];
    if cut("front-bottom") {
        let (g, piece) = front::construction(b, Quadrant::FRONT_BOTTOM);
        pieces::write_front_bottom(out, &g, piece, &silhouette, &field, &front_rails, color)?;
    }
    if cut("front-top") {
        let (g, piece) = front::construction(b, Quadrant::FRONT_TOP);
        let corners = fronttop::front_corners(&b.outer);
        pieces::write_front_top(out, &g, piece, &silhouette, &corners, &field, &front_rails, color)?;
    }
    if cut("back-bottom") {
        let (g, piece) = panel::construction(b);
        let rails = [field::perimeter_rail(&b.outer, vec![])];
        let print = BackBottomPrint { wall: WALL, warning_margin: DISPOSAL_MARGIN, warning_raise: DISPOSAL_RAISE };
        pieces::write_back_bottom(out, &g, piece, &silhouette, &field, &rails, &print, color)?;
    }
    if cut("back-top") {
        let top = backtop::construction(b);
        pieces::write_back_top(out, &top.graph, top.result, top.receiver_field, &silhouette, &field, &top.rails,
                               &top.print, color)?;
    }
    drop(silhouette);
    if cut("pump-retainer") {
        for seated in [false, true] {
            let p = retainer::piece(b, seated);
            pieces::write_retainer(out, &p.graph, p.result, p.name, p.seated, p.color)?;
        }
    }
    if cut("pump-tube-setting-jig") {
        let mut g = Graph::new();
        let plate = &b.pack.collet_plate;
        let jig = dock::tube_setting_jig(&mut g, plate, shell().pump_cartridge_aft_y(&b.pack.pump_trays, plate));
        pieces::write_jig(out, &g, jig, digits(color))?;
    }
    Ok(())
}

/// The dock's purchased parts as installed: each station's tee on its run axis, and the two
/// stem elbows of its return, their stems cut back to the depth each plugs in to.
fn dock_parts(plate: &ColletPlate) -> Result<Vec<(String, [f64; 3], Solid)>> {
    let tee = hsm_kernel::import::bodies(&read(Path::new(TEE))?, TEE)?;
    let elbow = hsm_kernel::import::model(ELBOW)?;
    let mut parts = Vec::new();
    for station in dock::stations(plate) {
        let pose = Affine::from_columns(-V3::X, -V3::Y, V3::Z, at(station.centre));
        for (i, body) in tee.iter().enumerate() {
            parts.push((numbered(&station.tee, i, tee.len()), tee_color(), body.solid.transformed(&pose)));
        }
        for e in &station.elbows {
            let x = -V3::Z;
            let z = v3(e.socket[1], -e.socket[0], 0.);
            let pose = Affine::from_columns(x, z.cross(x), z, at(e.crossing));
            let keep = dock::stem_elbow::hub_back_reach() + e.stem;
            let cutter = Solid::cuboid(v3(-keep - 40., -20., -20.), v3(-keep, 20., 20.));
            for (i, body) in elbow.iter().enumerate() {
                // The collet clears the cutter, so only the stem's body is cut back.
                let solid = if body.solid.bounds().min.x < -keep { body.solid.cut(&cutter)? } else { body.solid.clone() };
                parts.push((numbered(&e.name, i, elbow.len()), elbow_color(), solid.transformed(&pose)));
            }
        }
    }
    Ok(parts)
}

fn read(path: &Path) -> Result<Vec<u8>> {
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    hsm_kernel::reads::read(path, &bytes);
    Ok(bytes)
}

fn at(p: [f64; 3]) -> V3 {
    v3(p[0], p[1], p[2])
}

/// `name`, numbered from one among `count` bodies of the same part.
fn numbered(name: &str, i: usize, count: usize) -> String {
    if count > 1 { format!("{name}/{}", i + 1) } else { name.to_owned() }
}

/// A colour rounded to the decimal places the jig and the enclosure model carry.
fn digits(color: [f64; 3]) -> [f64; 3] {
    color.map(|c| format!("{c:.9}").parse().expect("a formatted number parses"))
}
