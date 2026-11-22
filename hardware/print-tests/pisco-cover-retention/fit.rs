//! Pisco covers for a comparison against the physically tested production receiver.
#[allow(dead_code)]
#[path = "../../printed-parts/enclosure/rear-equipment-caps/stations.rs"]
mod stations;

use anyhow::{Context, Result, ensure};
use hsm_enclosure_numbers::layout::{PISCO_WING_AFT_Y, Station};
use hsm_kernel::{Plane, Profile, Solid, V3, stl_bytes, v2, v3};
use serde_json::json;
use std::{fs, path::Path};

const SOURCE: &str = "hardware/printed-parts/enclosure/rear-equipment-caps/rear-equipment-caps-installed.step.npz";
const OUTPUT: &str = "hardware/print-tests/pisco-cover-retention/parts";
/// Free hook overlap with a receiver chamfer at the nominal installed regulator pose.
const PRELOAD_OVERLAP_Z: f64 = 0.55;
const MARK_HALF_WIDTH: f64 = 1.4;
const MARK_DEPTH: f64 = 0.6;
const MARK_SPACING: f64 = 4.5;

/// Fill the space directly under one retaining face. The overlap joins the pad to the
/// existing nose. Its outside boundaries are the original nose, leaf and wing ends.
fn bearing_fill(st: &Station, side: f64, take_up: f64) -> Result<Solid> {
    let nose_x = st.ledge - stations::REACH;
    let nose_z = st.bearing + stations::catch_air();
    let leaf_z = nose_z - (st.inner - nose_x) * stations::corbel_slope();
    let at = |radius, z| v2(st.axis_x + side * radius, z);
    let section = Profile::polygon(&[
        at(nose_x, nose_z - take_up), at(st.inner, leaf_z - take_up),
        at(st.inner, leaf_z + stations::NOSE_LAND / 2.0),
        at(nose_x, nose_z + stations::NOSE_LAND / 2.0),
    ]);
    Plane::XZ.at(v3(0.0, st.y0, 0.0)).extrude(&section, st.y0 - PISCO_WING_AFT_Y)
}

/// Recess the identification diamonds into the exposed flat back of the cover.
fn identification(x: f64, y: f64, bottom: f64) -> Result<Solid> {
    let r = MARK_HALF_WIDTH;
    let diamond = Profile::polygon(&[v2(-r, 0.0), v2(0.0, -r), v2(r, 0.0), v2(0.0, r)]);
    Plane::XY.at(v3(x, y, bottom - MARK_DEPTH)).extrude(&diamond, 2.0 * MARK_DEPTH)
}

fn main() -> Result<()> {
    let source = hsm_kernel::import::model(SOURCE)?.into_iter()
        .find(|b| b.name == "pisco-snap-cap").context("Pisco cover in the production assembly")?.solid;
    let st = stations::pisco_station();
    let mid_y = (st.y0 + st.y1) / 2.0;
    let bottom = source.bounds().min.z;
    let out = Path::new(OUTPUT);
    fs::create_dir_all(out)?;
    let mut variants = Vec::new();
    for (name, marks, take_up) in [
        ("pisco-one-mark", 1, 0.20),
        ("pisco-two-marks", 2, 0.35),
        ("pisco-three-marks", 3, stations::catch_air() + PRELOAD_OVERLAP_Z),
    ] {
        let west = bearing_fill(&st, -1.0, take_up)?;
        let east = bearing_fill(&st, 1.0, take_up)?;
        let mut held = Solid::union_all(&[source.clone(), west, east])?;
        let added = held.volume() - source.volume();
        let width = st.inner - (st.ledge - stations::REACH);
        let expected = 2.0 * width * (PISCO_WING_AFT_Y - st.y0) * take_up;
        ensure!((added - expected).abs() < 0.001, "{name}: retaining faces must fill their complete span");
        for i in 0..marks {
            let y = mid_y + (f64::from(i) - f64::from(marks - 1) / 2.0) * MARK_SPACING;
            held = held.cut(&identification(st.axis_x, y, bottom)?)?;
        }
        held.check()?;
        ensure!(held.components().len() == 1, "{name}: cap must be a single solid");
        let turned = held.rotate(V3::ZERO, V3::X, 90.0);
        let b = turned.bounds();
        let shift = v3(-(b.min.x + b.max.x) / 2.0, -(b.min.y + b.max.y) / 2.0, -b.min.z);
        fs::write(out.join(format!("{name}.stl")), stl_bytes(&[&turned.translate(shift)])?)?;
        let gap_mm = ((stations::catch_air() - take_up) * 1000.0).round() / 1000.0;
        let take_up_mm = (take_up * 1000.0).round() / 1000.0;
        variants.push(json!({"name":name,"diamonds":marks,"take_up_z_mm":take_up_mm,
            "seated_catch_gap_z_mm":gap_mm,"added_bearing_volume_mm3":added,
            "print_translation_after_x90_mm":[shift.x, shift.y, shift.z]}));
    }
    let doc = json!({"installed_source":SOURCE,"body":"pisco-snap-cap",
        "baseline_catch_gap_z_mm":stations::catch_air(),
        "seated_catch_gap_reference":"Signed vertical gap with the hooks relaxed and the regulator on its nominal installed axis. A negative gap is overlap before the springs bend.",
        "wing_y_mm":[st.y0, PISCO_WING_AFT_Y],
        "mark_depth_mm":MARK_DEPTH,"variants":variants});
    fs::write(out.join("geometry.json"), serde_json::to_string_pretty(&doc)? + "\n")?;
    Ok(())
}
