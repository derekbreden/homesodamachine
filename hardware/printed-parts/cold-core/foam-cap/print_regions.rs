//! foam-cap-print-regions — the local solid-infill regions the cold core's casing and equipment
//! lid print with, written to `fore-snap-print-regions.json`.
//!
//!     foam-cap-print-regions [--out FILE]
//!
//! Each region is a box of full zig-zag infill through a retention feature and the plate or wall
//! that roots it: reservoir A's fore pair's shared base and its aft pair, the pump catches, valve and discharge clips, the casing's M5 hosts and
//! head bearings, and the PCB deck's insert posts. A box intersects existing material and adds no geometry; it
//! is clipped to its piece's current mesh, and the record binds each piece's STEP and STL, so
//! print preparation refuses a piece whose exports have moved since. It reads the cap's numbers
//! and the current print meshes, and starts no generator, slice or printer.

use anyhow::{bail, Context, Result};
use hsm_cold_core_interface as core;
use hsm_cold_core_layout::cap::{Pose, world_to_cap};
use hsm_foam_cap_numbers::{clips, deck, fits, pump, reservoir_a, wells};
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

/// The installation frame and the lid's print frame differ by a quarter-turn about Z.
fn lid_bounds(low: [f64; 3], high: [f64; 3]) -> [f64; 6] {
    let a = world_to_cap(low);
    let b = world_to_cap(high);
    [a[0].min(b[0]), a[0].max(b[0]), a[1].min(b[1]), a[1].max(b[1]), a[2].min(b[2]), a[2].max(b[2])]
}

/// This connector and the lid use quarter-turn placements. The two opposite
/// corners therefore also bound the pocket in the lid's print frame.
fn wago_interior(well: &wells::Well, end: f64) -> [f64; 6] {
    let fit = wells::fit();
    let connector = Pose { rotation: well.rotation, translation: well.translation };
    let [x0, x1, y0, y1, z0, z1] = well.wago.well_cut(fit, end, 0.);
    lid_bounds(connector.point([x0, y0, z0]), connector.point([x1, y1, z1]))
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

    // Reservoir A's fore pair's shared base and its aft pair, carried from the appliance into the
    // cap's own frame.
    let lid = bounds["foam-cap-lid-top"];
    let mut lid_rows = Vec::new();
    for (name, [low, high]) in [("Reservoir A fore direct C2 pair and lid root", reservoir_a::pair().base),
                                ("Reservoir A aft C2 pair and lid root", reservoir_a::aft_body()),
                                ("V-B return clip and lid root", clips::vb_stock_bounds()?),
                                ("V-A feed clip and lid root", clips::va_feed()?.stock_bounds),
                                ("Pump discharge clip and lid root", clips::pump_discharge()?.stock_bounds())] {
        let native = lid_bounds(low, high);
        let clipped = clip(native, lid.0, lid.1);
        if (0..3).any(|axis| clipped[2 * axis + 1] <= clipped[2 * axis]) {
            bail!("the modifier for {name} is outside the current lid bounds");
        }
        let mut row = region(name.into(), native, lid);
        row["world_bounds_mm"] = json!([low[0], high[0], low[1], high[1], low[2], high[2]]);
        lid_rows.push(row);
    }
    let cradle = pump::cradle();
    let s = &cradle.station;
    let cheek = s.cheek();
    let inner = cheek.iter().map(|p| p[0]).fold(f64::INFINITY, f64::min);
    let outer = s.outer + pump::wing::TIP_RELEASE_ROOM;
    let floor = cradle.centre[2] - s.ceiling;
    let mut pocket_exclusions = Vec::new();
    for (side, name) in [(-1., "west"), (1., "east")] {
        let x = |radial: f64| s.axis_x + side * radial;
        let y0 = s.y0 - f.running;
        let y1 = s.y1 + f.running;
        let stock = lid_bounds([x(inner - ROOT), y0 - ROOT, floor - ROOT], [x(cheek[0][0]), y1 + ROOT, cradle.centre[2]]);
        lid_rows.push(region(format!("Pump {name} catch and lid root"), stock, lid));
        let mouth = lid_bounds([x(inner), y0, floor], [x(outer), y1, cradle.centre[2]]);
        pocket_exclusions.push(json!({"name": format!("Pump {name} catch pocket"), "bounds_source_mm": mouth,
            "reason": "The retaining shoulder grows at 45 degrees from continuous stock. The guide and release slot print clear."}));
    }
    let mut trees = Vec::new();
    let mut bridges = Vec::new();
    for well in wells::wells() {
        let name = format!("{} insertion pocket", well.name);
        let interior = wago_interior(&well, 0.);
        let mut blocking = wago_interior(&well, wells::POCKET_OVERRUN);
        let pose = Pose { rotation: well.rotation, translation: well.translation };
        let mouth = world_to_cap(pose.translation);
        let outward = world_to_cap(pose.point([0., 1., 0.]));
        let direction: [i8; 3] = std::array::from_fn(|axis| (outward[axis] - mouth[axis]).round() as i8);
        blocking[5] += f.running;
        pocket_exclusions.push(json!({"name":name,"bounds_source_mm":interior,"blocking_bounds_source_mm":blocking,
            "review_interior":false,"reason":"Keep automatic branches out of this well and its mouth. Its own removable tree starts on the floor."}));
        trees.push(json!({"name":format!("{name} WAGO pocket floor tree"),"shape":"pocket_floor_tree",
            "bounds_source_mm":interior,"print_up_source":[0,0,1],"mouth_direction_source":direction,
            "reason":"One floor-rooted tree spreads beneath the roof and pulls out through the connector mouth."}));
        let [x0, x1, y0, y1, _, roof] = interior;
        bridges.push(json!({"name":name,"bounds_source_mm":[x0,x1,y0-wells::WALL,y1+wells::WALL,roof-f.running,roof+wells::WALL],
            "bridge_print_axis_source":[0,1,0],"reason":"Bridge the narrow opening between its two sidewalls over the removable crown."}));
    }
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
                   "hardware/printed-parts/cold-core/foam-cap/numbers/clips.rs", "hardware/printed-parts/cold-core/foam-cap/numbers/design.rs", "hardware/printed-parts/cold-core/foam-cap/numbers/deck.rs", "hardware/printed-parts/cold-core/foam-cap/numbers/reservoir_a.rs",
                   "hardware/printed-parts/cold-core/foam-cap/numbers/pump.rs", "hardware/printed-parts/cold-core/foam-cap/numbers/wells.rs", "hardware/printed-parts/enclosure/enclosure/numbers/equipment_snap.rs",
                   "hardware/printed-parts/enclosure/enclosure/numbers/junctions.rs",
                   "hardware/printed-parts/cold-core/interface/lib.rs", "hardware/cold-core-layout/layout/cap.rs", "hardware/manifold-layout/above-core.json"];
    let mut source_sha = Map::new();
    for s in sources {
        source_sha.insert(s.into(), json!(sha(&root.join(s))?));
    }
    let frames: Map<String, Value> = paths.iter().map(|(name, _)| (name.to_string(),
        json!("Source STEP/STL coordinates before installed placement; world_bounds_mm, where present, uses appliance coordinates."))).collect();
    let record = json!({
        "scope": "Solid infill through the pump catches, tube seats, casing screw hosts and bearings, and PCB insert posts. The lid keeps both motor-cap pockets clear and carries one removable tree inside each WAGO pocket.",
        "use": "Print preparation for the equipment lid, shell and bottom cap. Modifier boxes set local deposition. The lid's four print-only trees release through the connector mouths.",
        "producer": "hardware/printed-parts/cold-core/foam-cap/print_regions.rs",
        "coordinate_frames": frames, "source_sha256": source_sha, "native_artifact_sha256": meshes,
        "source_stl_sha256": meshes["foam-cap-lid-top"][".stl"], "support_free_regions": pocket_exclusions,
        "removable_support_stock": trees, "bridge_regions": bridges,
        "part_process_overrides": {},
        "pieces": {"foam-cap-lid-top": lid_rows, "foam-cap-bottom": bottom_rows, "foam-shell": shell_rows},
    });
    if let Some(parent) = out.parent() {
        std::fs::create_dir_all(parent)?;
    }
    std::fs::write(&out, serde_json::to_string_pretty(&record)? + "\n")?;
    println!("{}", serde_json::to_string_pretty(&json!({"path": out.display().to_string(),
        "lid": record["pieces"]["foam-cap-lid-top"].as_array().map(|rows| rows.iter().take(2).cloned().collect::<Vec<_>>()),
        "native_artifact_sha256": record["native_artifact_sha256"]}))?);
    Ok(())
}
