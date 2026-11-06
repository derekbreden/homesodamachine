//! The print regions' bounds that the recipes own: the construction plan's conservative bounds
//! for the funnel frame's receivers in each top piece, and for the Y seam's knuckles, from the
//! declared Box.
//!
//!     enclosure-region-bounds [--box <declared Box>]
//!
//! prints `{"receivers": {"front": [xmin, xmax, ymin, ymax, zmin, zmax], "back": [...]},
//! "knuckles": [{"piece", "sx", "z0", "bounds"}, ...]}`: the receivers for the columns that carry
//! them, and every knuckle flank by flank, the lower stack then the upper, bottom to top. It runs
//! at the repository root.
use anyhow::{Context, Result, bail};
use hsm_enclosure_quadrants::funnel;
use hsm_enclosure_quadrants::plan::Graph;
use hsm_enclosure_quadrants::quadrant::Y;
use hsm_enclosure_quadrants::shell::{Y_STACK_HIGH_DEPTH, y_stack_low_depth};
use hsm_enclosure_quadrants::spec::Box;
use hsm_enclosure_quadrants::ystacks::{y_knuckle, y_stack};
use serde_json::{Map, json};
use std::path::PathBuf;

const BOX: &str = "hardware/manifold-layout/enclosure-box.json";
const USAGE: &str = "usage: enclosure-region-bounds [--box <declared Box>]";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let declared = match args.next() {
        None => PathBuf::from(BOX),
        Some(flag) if flag == "--box" => PathBuf::from(args.next().context(USAGE)?),
        Some(_) => bail!(USAGE),
    };
    hsm_kernel::reads::begin();
    let bytes = std::fs::read(&declared).with_context(|| format!("reading {}", declared.display()))?;
    hsm_kernel::reads::read(&declared, &bytes);
    let b = Box::from_document(serde_json::from_slice(&bytes)?).with_context(|| declared.display().to_string())?;
    let mut g = Graph::new();

    let seat = funnel::seat_z(&b.outer);
    let mut receivers = Map::new();
    for (name, col) in [("front", Y::Front), ("back", Y::Back)] {
        if let Some(shape) = funnel::receivers(&mut g, &b.inner, &b.outer, b.pack.funnel, seat, col, None) {
            receivers.insert(name.into(), json!(shape.bounds()));
        }
    }

    let silhouette = g.silhouette(b.outer);
    let (lower, upper) = y_stack(&b.inner);
    let mut knuckles = Vec::new();
    for (x_in, sx) in [(b.inner[0], 1.0), (b.inner[1], -1.0)] {
        for (stack, depth) in [(&lower, y_stack_low_depth()), (&upper, Y_STACK_HIGH_DEPTH)] {
            for row in stack {
                let knuckle = y_knuckle(&mut g, &b.inner, silhouette, x_in, sx, b.y_joint, row, depth);
                knuckles.push(json!({"piece": row.piece.name(), "sx": sx, "z0": row.z0, "bounds": knuckle.bounds()}));
            }
        }
    }
    println!("{}", json!({"receivers": receivers, "knuckles": knuckles}));
    Ok(())
}
