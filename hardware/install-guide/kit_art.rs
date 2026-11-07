//! The install guide's kit page drawings: each supplied item as a hidden-line view of its
//! current model, world Z up, written as the SVG lines the booklet draws in one slate pen.
use anyhow::{Context, Result};
use hsm_kernel::Solid;
use serde_json::Value;
use std::fmt::Write as _;
use std::path::Path;

#[path = "kit-art/props.rs"]
mod props;

const CAMERA: [f64; 3] = [0.8, -1.0, 0.7];

/// Each item and the direction it is seen from.
const VIEWS: [(&str, [f64; 3]); 9] = [
    ("machine", CAMERA),
    ("faucet-and-plate", [0.95, -1.0, 0.55]),
    ("filtered-line", CAMERA),
    ("water-tees", [0.6, -1.0, 0.65]),
    ("regulator-and-tether", [0.15, 1.0, 0.3]),
    ("collet-press", [-0.5, -0.9, 0.85]),
    ("power-cord", CAMERA),
    ("install-guide", CAMERA),
    ("cold-kit", CAMERA),
];

/// A drawing fits this box, centred on the SVG's sheet.
const SHEET: [f64; 2] = [600.0, 450.0];
const FIT: [f64; 2] = [564.0, 414.0];

fn item(name: &str, facts: &Value) -> Result<props::Shown> {
    Ok(match name {
        "machine" => props::machine(facts)?,
        "faucet-and-plate" => props::faucet_and_plate("hardware/faucet-layout/faucet-assembly.step.npz")?,
        "filtered-line" => props::filtered_line()?,
        "water-tees" => props::water_tees("hardware/reference/jg-pp0208e-tee/jg-pp0208e-tee.step.mesh")?,
        "regulator-and-tether" => {
            props::regulator_and_tether("hardware/reference/taprite-3741-regulator/taprite-3741-regulator.step.mesh")?
        }
        "collet-press" => props::collet_press("hardware/printed-parts/collet-press/collet-press.step.npz")?,
        "power-cord" => props::power_cord()?,
        "install-guide" => props::install_guide(),
        "cold-kit" => props::cold_kit()?,
        _ => anyhow::bail!("no kit item {name}"),
    })
}

/// The visible outlines of `bodies` seen from `camera`, as an SVG whose paths carry every
/// transform.
fn line_svg(bodies: &[(String, Solid)], camera: [f64; 3]) -> String {
    let mut vertices = Vec::new();
    let mut triangles = Vec::new();
    for (_, solid) in bodies {
        let offset = vertices.len() as u32;
        vertices.extend(solid.verts().iter().map(|p| [p.x, p.y, p.z]));
        triangles.extend(solid.tris().iter().map(|t| t.map(|i| i + offset)));
    }
    let right = [-camera[1], camera[0], 0.0];
    let edges = hsm_pages::lines::visible_edges(&vertices, &triangles, camera, right, 30.0);
    let paths = hsm_pages::lines::paths(&edges, 0.0025);
    let flat = paths.iter().flatten();
    let left = flat.clone().map(|p| p[0]).fold(f64::INFINITY, f64::min);
    let right = flat.clone().map(|p| p[0]).fold(f64::NEG_INFINITY, f64::max);
    let bottom = flat.clone().map(|p| p[1]).fold(f64::INFINITY, f64::min);
    let top = flat.map(|p| p[1]).fold(f64::NEG_INFINITY, f64::max);
    let scale = (FIT[0] / (right - left)).min(FIT[1] / (top - bottom));
    let (ox, oy) = ((SHEET[0] - (right - left) * scale) / 2.0, (SHEET[1] - (top - bottom) * scale) / 2.0);
    let mut svg = format!(
        "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{w}\" height=\"{h}\" viewBox=\"0 0 {w} {h}\">\n\
         <g fill=\"none\" stroke=\"#46515b\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">\n",
        w = SHEET[0],
        h = SHEET[1]
    );
    for path in &paths {
        svg.push_str("<path d=\"");
        for (i, p) in path.iter().enumerate() {
            let _ = write!(
                svg,
                "{}{}{:.4},{:.4}",
                if i == 0 { "" } else { " " },
                if i == 0 { 'M' } else { 'L' },
                ox + (p[0] - left) * scale,
                oy + (top - p[1]) * scale
            );
        }
        svg.push_str("\"/>\n");
    }
    svg + "</g>\n</svg>\n"
}

fn main() -> Result<()> {
    let out = std::path::absolute(std::env::args().nth(1).unwrap_or_else(|| ".".into()))?;
    let facts_path = Path::new("hardware/manifold-layout/enclosure-assembly.facts.json");
    let bytes = std::fs::read(facts_path).with_context(|| format!("reading {}", facts_path.display()))?;
    hsm_kernel::reads::read(facts_path, &bytes);
    let facts: Value = serde_json::from_slice(&bytes)?;
    let dir = out.join("hardware/install-guide/assets/kit");
    std::fs::create_dir_all(&dir)?;
    for (name, camera) in VIEWS {
        let bodies = item(name, &facts).with_context(|| format!("the kit's {name}"))?;
        std::fs::write(dir.join(format!("{name}.svg")), line_svg(&bodies, camera))?;
    }
    Ok(())
}
