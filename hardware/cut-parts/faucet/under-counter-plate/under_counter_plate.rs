//! The under-counter plate's laser file, the one SendCutSend cuts it from: its analytic outline as
//! LINE and ARC entities on layer 0 of an R2010 DXF in millimetres. The template carries the
//! format's headers, tables and blocks; every entity in model space is the outline's. It runs by
//! hand when the plate's numbers change, outside the normal build, and leaves the file as it is
//! when its bytes come out the same.
//!
//!     under-counter-plate [<output directory>]
use anyhow::{Result, bail};
use hsm_under_counter_plate_numbers::{Edge, outline};
use std::fmt::Write;
use std::path::PathBuf;

const OUTPUT: &str = "hardware/cut-parts/faucet/under-counter-plate";
const NAME: &str = "under-counter-plate.dxf";

/// `edge` as a DXF entity with `handle`, in the template's model space (block record 0x17).
/// Handles from 0x100 up are the outline's; the template's own end below them.
fn entity(text: &mut String, edge: &Edge, handle: usize) -> std::fmt::Result {
    match edge {
        Edge::Line(a, b) => {
            write!(text, "  0\nLINE\n  5\n{handle:X}\n330\n17\n100\nAcDbEntity\n  8\n0\n100\nAcDbLine\n")?;
            for (base, p) in [(10, a), (11, b)] {
                writeln!(text, "{base:>3}\n{}\n{:>3}\n{}\n{:>3}\n0.0", p[0], base + 10, p[1], base + 20)?;
            }
        }
        Edge::Arc(c, r, start, end) => {
            write!(
                text,
                "  0\nARC\n  5\n{handle:X}\n330\n17\n100\nAcDbEntity\n  8\n0\n100\nAcDbCircle\n 10\n{}\n 20\n{}\n 30\n0.0\n 40\n{}\n100\nAcDbArc\n 50\n{}\n 51\n{}\n",
                c[0], c[1], r, start, end
            )?;
        }
    }
    Ok(())
}

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: under-counter-plate [<output directory>]");
    }
    std::fs::create_dir_all(&out)?;
    let edges = outline();
    let mut body = String::new();
    for (index, edge) in edges.iter().enumerate() {
        entity(&mut body, edge, 0x100 + index)?;
    }
    let text = include_str!("r2010-template.dxf.in")
        .replace("{{ENTITIES}}\n", &body)
        .replace("{{HANDSEED}}", &format!("{:X}", 0x100 + edges.len()));
    let path = out.join(NAME);
    hsm_documents::write_if_changed(&path, &hsm_documents::canonicalize_dxf(text.as_bytes()))?;
    println!("-> {}", path.display());
    Ok(())
}
