//! foam-cap-print-regions — the local solid-infill regions the cold core's casing and equipment
//! lid print with, written to `fore-snap-print-regions.json`.
//!
//!     foam-cap-print-regions [--out FILE]
//!
//! Each region is a box of full zig-zag infill through a retention feature and the plate or wall
//! that roots it: the fore reservoir pair's shared base, the casing's M5 hosts and head bearings,
//! and the PCB deck's insert posts. A box intersects existing material and adds no geometry; it
//! is clipped to its piece's current mesh, and the record binds each piece's STEP and STL, so
//! print preparation refuses a piece whose exports have moved since. It reads the cap's numbers
//! and the current print meshes, and starts no generator, slice or printer.

use anyhow::{bail, Context, Result};
use hsm_cold_core_interface as core;
use hsm_cold_core_layout::cap::world_to_cap;
use hsm_foam_cap_numbers::{deck, fits, reservoir_a};
use serde_json::{json, Map, Value};
use sha2::{Digest, Sha256};
use std::path::{Path, PathBuf};

const HERE: &str = "hardware/printed-parts/cold-core/foam-cap";
/// The plate or wall each region carries into, past its feature.
const ROOT: f64 = 3.0;

fn sha(path: &Path) -> Result<String> {
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    Ok(Sha256::digest(&bytes).iter().map(|b| format!("{b:02x}")).collect())
}

/// A binary STL's bounds, as its stored single-precision corners give them.
fn stl_bounds(path: &Path) -> Result<([f64; 3], [f64; 3])> {
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    if bytes.len() < 84 {
        bail!("{} is not a binary STL", path.display());
    }
    let count = u32::from_le_bytes([bytes[80], bytes[81], bytes[82], bytes[83]]) as usize;
    if bytes.len() != 84 + count * 50 {
        bail!("{} is not a binary STL", path.display());
    }
    let (mut lo, mut hi) = ([f64::INFINITY; 3], [f64::NEG_INFINITY; 3]);
    for facet in bytes[84..].chunks_exact(50) {
        for corner in 0..3 {
            for axis in 0..3 {
                let at = 12 + corner * 12 + axis * 4;
                let v = f32::from_le_bytes([facet[at], facet[at + 1], facet[at + 2], facet[at + 3]]) as f64;
                lo[axis] = lo[axis].min(v);
                hi[axis] = hi[axis].max(v);
            }
        }
    }
    Ok((lo, hi))
}

fn clip(bounds: [f64; 6], lo: [f64; 3], hi: [f64; 3]) -> [f64; 6] {
    let mut out = [0.0; 6];
    for axis in 0..3 {
        out[2 * axis] = bounds[2 * axis].max(lo[axis]);
        out[2 * axis + 1] = bounds[2 * axis + 1].min(hi[axis]);
    }
    out
}

fn region(name: String, bounds: [f64; 6], mesh: ([f64; 3], [f64; 3])) -> Value {
    json!({"name": name, "machine_bounds_mm": bounds, "applied_source_bounds_mm": clip(bounds, mesh.0, mesh.1),
           "sparse_infill_density": "100%", "sparse_infill_pattern": "zig-zag"})
}

fn square(x: f64, y: f64, half: f64, z0: f64, z1: f64) -> [f64; 6] {
    [x - half, x + half, y - half, y + half, z0, z1]
}

fn main() -> Result<()> {
    let root = std::env::current_dir()?;
    let mut out = root.join(HERE).join("fore-snap-print-regions.json");
    let mut args = std::env::args().skip(1);
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--out" => out = PathBuf::from(args.next().context("--out needs a file")?),
            _ => bail!("usage: foam-cap-print-regions [--out FILE]"),
        }
    }
    let here = root.join(HERE);
    let paths = [("foam-cap-lid-top", here.join("foam-cap-lid-top.stl")), ("foam-cap-bottom", here.join("foam-cap-bottom.stl")),
                 ("foam-shell", root.join("hardware/printed-parts/cold-core/foam-shell/foam-shell.stl"))];
    let mut meshes = Map::new();
    let mut bounds = std::collections::HashMap::new();
    for (name, path) in &paths {
        bounds.insert(*name, stl_bounds(path)?);
        meshes.insert(name.to_string(), json!({".step": sha(&path.with_extension("step"))?, ".stl": sha(path)?}));
    }
    let f = fits();

    // The fore pair's shared base, carried from the appliance into the cap's own frame.
    let [low, high] = reservoir_a::pair().base;
    let world = [low[0], high[0], low[1], high[1], low[2], high[2]];
    let mut native = [f64::INFINITY, f64::NEG_INFINITY, f64::INFINITY, f64::NEG_INFINITY, f64::INFINITY, f64::NEG_INFINITY];
    for x in [low[0], high[0]] {
        for y in [low[1], high[1]] {
            for z in [low[2], high[2]] {
                let p = world_to_cap([x, y, z]);
                for axis in 0..3 {
                    native[2 * axis] = native[2 * axis].min(p[axis]);
                    native[2 * axis + 1] = native[2 * axis + 1].max(p[axis]);
                }
            }
        }
    }
    let lid = bounds["foam-cap-lid-top"];
    let clipped = clip(native, lid.0, lid.1);
    if (0..3).any(|axis| clipped[2 * axis + 1] <= clipped[2 * axis]) {
        bail!("the fore receiver/root modifier is outside the current lid bounds");
    }
    let mut fore = region("Reservoir A fore direct C2 pair and lid root".into(), native, lid);
    fore["world_bounds_mm"] = json!(world);
    let mut lid_rows = vec![fore];
    let (mut shell_rows, mut bottom_rows) = (Vec::new(), Vec::new());

    let bottom = bounds["foam-cap-bottom"];
    for (index, (xy, _)) in core::attachment_stations().iter().enumerate() {
        let [x, y] = *xy;
        shell_rows.push(region(format!("M5 host {}, both inserts, tail and wall root", index + 1),
                               square(x, y, core::SCREW_GUARD_DIAMETER / 2. + ROOT, 0., core::foam_shell_rim_z(&f)), bounds["foam-shell"]));
        bottom_rows.push(region(format!("M5 head pad {} and floor/wall root", index + 1),
                                square(x, y, core::HEAD_CBORE_RADIUS + core::WALL_THICKNESS + ROOT, bottom.0[2], bottom.1[2]), bottom));
    }
    let lid_height = core::foam_cap_lid_height(&f);
    for (index, (xy, _)) in core::lid_attachment_stations().iter().enumerate() {
        lid_rows.push(region(format!("M5 head bearing {} and plate root", index + 1),
                             square(xy[0], xy[1], core::HEAD_CBORE_RADIUS + ROOT, 0., lid_height), lid));
    }
    for (index, column) in deck::columns().iter().enumerate() {
        lid_rows.push(region(format!("pcba insert post {} and plate root", index + 1),
                             square(column.xy[0], column.xy[1], core::DECK_MOUNT_BOSS_RADIUS + ROOT, 0., column.top), lid));
    }

    let sources = ["hardware/printed-parts/cold-core/foam-cap/print_regions.rs", "hardware/printed-parts/cold-core/foam-cap/numbers/lib.rs",
                   "hardware/printed-parts/cold-core/foam-cap/numbers/deck.rs", "hardware/printed-parts/cold-core/foam-cap/numbers/reservoir_a.rs",
                   "hardware/printed-parts/cold-core/interface/lib.rs", "hardware/cold-core-layout/layout/cap.rs", "hardware/manifold-layout/above-core.json"];
    let mut source_sha = Map::new();
    for s in sources {
        source_sha.insert(s.into(), json!(sha(&root.join(s))?));
    }
    let frames: Map<String, Value> = paths.iter().map(|(name, _)| (name.to_string(),
        json!("Source STEP/STL coordinates before installed placement; world_bounds_mm, where present, uses appliance coordinates."))).collect();
    let record = json!({
        "scope": "Finite infill-only modifiers through the fore C2 shared base, all M5 casing hosts/head bearings and PCB insert posts, each with its supporting plate/wall root. No load capacity or lifetime qualification.",
        "use": "Manual print preparation for the equipment lid, shell and bottom cap. Each box intersects existing material and adds no geometry. All other lid walls, infill, pose, features and support settings retain their current recipe.",
        "producer": "hardware/printed-parts/cold-core/foam-cap/print_regions.rs",
        "coordinate_frames": frames, "source_sha256": source_sha, "native_artifact_sha256": meshes,
        "part_process_overrides": {},
        "pieces": {"foam-cap-lid-top": lid_rows, "foam-cap-bottom": bottom_rows, "foam-shell": shell_rows},
    });
    if let Some(parent) = out.parent() {
        std::fs::create_dir_all(parent)?;
    }
    std::fs::write(&out, serde_json::to_string_pretty(&record)? + "\n")?;
    println!("{}", serde_json::to_string_pretty(&json!({"path": out.display().to_string(), "source_bounds_mm": clipped,
        "world_bounds_mm": world, "native_artifact_sha256": record["native_artifact_sha256"]}))?);
    Ok(())
}
