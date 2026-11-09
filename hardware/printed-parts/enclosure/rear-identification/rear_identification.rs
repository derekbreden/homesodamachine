//! The rear identification tiles: one card per wet port on the rear wall, sliding in its channel
//! with its bore on the port's fitting and the port's word raised through its face, each in its
//! own fitting frame; and the numbers the installed machine places and colours them by.
//!
//!     rear-identification [<output directory>]
use anyhow::{Context, Result, anyhow, ensure};
use hsm_bulkhead_ring_numbers as ring;
use hsm_enclosure_components::{output, port_colors, write_colored_part};
use hsm_kernel::{Body, Loop, Plane, Profile, Seg, Solid, V2, V3, v2, v3};
use serde::Deserialize;
use serde_json::{Value, json};
use std::collections::BTreeMap;

const PROGRAM: &str = "rear-identification";
const FOLDER: &str = "hardware/printed-parts/enclosure/rear-identification";
/// The above-core layout the tiles stand by: the rear wall's grid, its wet ports, the roof and
/// the cards' plan.
const ABOVE_CORE: &str = "hardware/manifold-layout/above-core.json";

/// The cards' thickness, how far each bore's cut runs past both faces, and the words' size in the
/// rings' lettering.
const THICK: f64 = 1.8;
const BORE_OVERRUN: f64 = 0.1;
const WORD_SIZE: f64 = 5.0;

/// The approved running clearance at each vertical edge of a tile's retaining channel.
const SIDE_CLEARANCE: f64 = 0.20;

/// The tile each wet port carries, and the order the tiles are written in.
const PORTS: [(&str, &str); 6] = [
    ("bulkhead-water", "water"),
    ("co2-inlet", "co2"),
    ("bulkhead-drain", "drain"),
    ("bulkhead-carb", "carb"),
    ("bulkhead-flavor-a", "flavor-a"),
    ("bulkhead-flavor-b", "flavor-b"),
];
const ORDER: [&str; 6] = ["water", "co2", "drain", "carb", "flavor-a", "flavor-b"];

/// The words' outlines, set once in the rings' typeface, at their em.
const WORDS: &str = include_str!("label-words.json");

#[derive(Deserialize)]
struct AboveCore {
    fluid_grid: Grid,
    rear_wall: RearWall,
    enclosure: Enclosure,
    rear_identification: Plan,
    rear_plumbing: Plumbing,
}
#[derive(Deserialize)]
struct Grid {
    columns_x_mm: Vec<f64>,
    rows_z_mm: Vec<f64>,
    assignment: Vec<Vec<String>>,
}
#[derive(Deserialize)]
struct RearWall {
    wet_ports: Vec<Port>,
}
#[derive(Deserialize)]
struct Port {
    name: String,
    center_x_mm: f64,
    center_z_mm: f64,
    bore_diameter_mm: f64,
}
#[derive(Deserialize)]
struct Enclosure {
    roof_z_mm: f64,
}
/// The cards' plan: their width and height, the gap between rows, which rows carry their word
/// below the fittings, and how far each fitting's flange reaches below and above its centre.
#[derive(Deserialize)]
struct Plan {
    width_mm: f64,
    height_mm: f64,
    tile_gap_mm: f64,
    text_below_rows: Vec<bool>,
    flange_z_offsets_mm: BTreeMap<String, [f64; 2]>,
}
/// The tap water's bore, which the tile's fitting needs wider than its port's.
#[derive(Deserialize)]
struct Plumbing {
    tap_tile_bore_mm: f64,
}

/// One tile in its own frame: how far its card reaches below and above its centre, its word's
/// centre, its bore's offset and diameter.
struct Tile {
    which: &'static str,
    bottom: f64,
    top: f64,
    word_center: f64,
    bore: [f64; 2],
    bore_diameter: f64,
}

/// Each card fills its row's band down from the roof. Its word stands between the row's
/// fittings' flanges and the card's edge on the side the row is lettered.
fn tiles(a: &AboveCore) -> Result<Vec<Tile>> {
    let plan = &a.rear_identification;
    let port = |name: &str| a.rear_wall.wet_ports.iter().find(|p| p.name == name).with_context(|| format!("no wet port {name}"));
    let which = |name: &str| PORTS.iter().find(|(p, _)| *p == name).map(|(_, w)| *w).with_context(|| format!("no tile labels {name}"));
    let grid = &a.fluid_grid;
    let mut out = vec![];
    for (index, (z, names)) in grid.rows_z_mm.iter().zip(&grid.assignment).enumerate() {
        let top = a.enclosure.roof_z_mm - index as f64 * (plan.height_mm + plan.tile_gap_mm);
        let bottom = top - plan.height_mm;
        let below = *plan.text_below_rows.get(index).context("each card row has a text side")?;
        let flanges = names
            .iter()
            .map(|name| {
                let reach = plan.flange_z_offsets_mm.get(which(name)?).with_context(|| format!("no flange reach for {name}"))?;
                Ok(port(name)?.center_z_mm + reach[if below { 0 } else { 1 }])
            })
            .collect::<Result<Vec<f64>>>()?;
        let flange = if below { flanges.into_iter().min_by(f64::total_cmp) } else { flanges.into_iter().max_by(f64::total_cmp) }
            .context("an empty card row")?;
        let word = (flange + if below { bottom } else { top }) / 2.;
        for (x, name) in grid.columns_x_mm.iter().zip(names) {
            let (p, which) = (port(name)?, which(name)?);
            out.push(Tile {
                which,
                bottom: z - bottom,
                top: top - z,
                word_center: word - z,
                bore: [p.center_x_mm - x, p.center_z_mm - z],
                bore_diameter: if which == "water" { a.rear_plumbing.tap_tile_bore_mm } else { p.bore_diameter_mm },
            });
        }
    }
    Ok(out)
}

/// A tile's card with its bore and its word cut through, its word, and the single-material
/// print's exterior, which joins the word through its full inlay depth.
fn build(tile: &Tile, width: f64, word: &Value, scale: f64) -> Result<(Solid, Solid, Solid)> {
    let (depth, rise) = (ring::WORD_DEPTH, ring::WORD_RAISE);
    let glyphs = word_profiles(word, scale)?
        .iter()
        .map(|p| Plane::XY.extrude(p, depth + rise))
        .collect::<Result<Vec<_>>>()?;
    let letters = Solid::compose(&glyphs).rotate(V3::ZERO, V3::X, 90.0).rotate(V3::ZERO, V3::Z, 180.0);
    let bounds = letters.bounds();
    let word = letters.translate(v3(
        -(bounds.min.x + bounds.max.x) / 2.0,
        THICK - depth - bounds.min.y,
        tile.word_center - (bounds.min.z + bounds.max.z) / 2.0,
    ));
    let blank = Solid::cuboid(v3(-width / 2.0, 0.0, -tile.bottom), v3(width / 2.0, THICK, tile.top));
    let bore = Solid::cylinder(
        v3(tile.bore[0], -BORE_OVERRUN, tile.bore[1]),
        V3::Y,
        tile.bore_diameter / 2.0,
        THICK + 2.0 * BORE_OVERRUN,
    )?;
    let body = blank.cut_all(&[bore.clone(), word.clone()])?;
    let exterior = blank.cut(&bore)?.union(&word)?;
    Ok((body, word, exterior))
}

fn main() -> Result<()> {
    let out = output(PROGRAM, FOLDER)?;
    let path = std::path::Path::new(ABOVE_CORE);
    let bytes = std::fs::read(path).with_context(|| format!("reading {ABOVE_CORE}"))?;
    hsm_kernel::reads::read(path, &bytes);
    let above: AboveCore = serde_json::from_slice(&bytes).with_context(|| format!("parsing {ABOVE_CORE}"))?;
    let words: Value = serde_json::from_str(WORDS)?;
    let scale = WORD_SIZE / words["em_mm"].as_f64().ok_or_else(|| anyhow!("the words name their em"))?;
    let tiles = tiles(&above)?;
    let width = above.rear_identification.width_mm - 2.0 * SIDE_CLEARANCE;
    let mut placed = vec![];
    for which in ORDER {
        let tile = tiles.iter().find(|t| t.which == which).with_context(|| format!("no {which} tile"))?;
        let &(_, word, fluid) = ring::STATIONS.iter().find(|(s, _, _)| *s == which).with_context(|| format!("no {which} station"))?;
        ensure!(words["words"][word].is_array(), "the label words carry no {word}");
        let (body, letters, exterior) = build(tile, width, &words["words"][word], scale)?;
        let (chip, ink) = port_colors(fluid)?;
        let (name, body_name, word_name) = (format!("rear-label-{which}"), format!("bulkhead-ring-{which}"), format!("bulkhead-ring-{which}-word"));
        let bodies = [
            Body { name: &body_name, color: Some(chip), solid: &body },
            Body { name: &word_name, color: Some(ink), solid: &letters },
        ];
        println!("{}", write_colored_part(&out, &name, &bodies, &exterior)?);
        placed.push(json!({"name": name, "body_name": body_name, "word_name": word_name, "chip_color": chip, "word_color": ink}));
    }
    let numbers = json!({"thick": THICK, "width": width, "side_clearance": SIDE_CLEARANCE, "stations": placed});
    std::fs::write(out.join("rear-identification.numbers.json"), serde_json::to_string_pretty(&numbers)? + "\n")?;
    Ok(())
}

/// A word's line and Bézier outlines, with its counters already nested, scaled from its em.
fn word_profiles(word: &Value, scale: f64) -> Result<Vec<Profile>> {
    fn list(v: &Value) -> Result<&Vec<Value>> {
        v.as_array().ok_or_else(|| anyhow!("label contours are a list"))
    }
    let point = |v: &Value| -> Result<V2> {
        let a = v.as_array().ok_or_else(|| anyhow!("a label point has two coordinates"))?;
        ensure!(a.len() == 2, "a label point has two coordinates");
        Ok(v2(
            a[0].as_f64().ok_or_else(|| anyhow!("label X is numeric"))?,
            a[1].as_f64().ok_or_else(|| anyhow!("label Y is numeric"))?,
        ) * scale)
    };
    let outline = |v: &Value| -> Result<Loop> {
        let segs = list(v)?
            .iter()
            .map(|v| {
                let (kind, controls) =
                    v.as_object().and_then(|v| v.iter().next()).ok_or_else(|| anyhow!("a label segment has controls"))?;
                let p = list(controls)?.iter().map(&point).collect::<Result<Vec<_>>>()?;
                Ok(match (kind.as_str(), p.as_slice()) {
                    ("line", &[a, b]) => Seg::Line { a, b },
                    ("quad", &[a, c, b]) => Seg::Quad { a, c, b },
                    ("cubic", &[a, c1, c2, b]) => Seg::Cubic { a, c1, c2, b },
                    _ => return Err(anyhow!("invalid label {kind} segment")),
                })
            })
            .collect::<Result<Vec<_>>>()?;
        Loop::new(segs)
    };
    list(word)?
        .iter()
        .map(|p| {
            Ok(Profile {
                outer: outline(&p["outer"])?,
                holes: list(&p["holes"])?.iter().map(&outline).collect::<Result<Vec<_>>>()?,
            })
        })
        .collect()
}
