//! These matched receiver and cover trials isolate Pisco tip contact, rigid seating and bridged retaining lands.
#[allow(dead_code)]
#[path = "../../printed-parts/enclosure/rear-equipment-caps/stations.rs"]
mod stations;
mod bridges;
mod locators;

use anyhow::{Context, Result, ensure};
use hsm_enclosure_numbers::{Bounds, catalog::running, layout::{PISCO_WING_AFT_Y, Station}};
use hsm_kernel::{Plane, Profile, Solid, V3, stl_bytes, v2, v3};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{fs, path::Path};

const OUT: &str = "hardware/print-tests/pisco-cover-rocking/parts";
const CAPS: &str = "hardware/printed-parts/enclosure/rear-equipment-caps/rear-equipment-caps-installed.step.npz";
const BACK: &str = "hardware/printed-parts/enclosure/enclosure/enclosure-back-top.step.npz";
const FEATURES: &str = "hardware/print-tests/rear-equipment-corner/parts/rear-equipment-corner.print-features.json";
const CROP: Bounds = [52.0, 104.5, 403.5, 474.31, 302.0, 355.01];
const HEADROOM: f64 = 0.80;
const HOOK_TAKE_UP: f64 = 0.75;

fn brick([x0, x1, y0, y1, z0, z1]: Bounds) -> Solid {
    Solid::cuboid(v3(x0, y0, z0), v3(x1, y1, z1))
}

fn digest(bytes: &[u8]) -> String { format!("{:x}", Sha256::digest(bytes)) }

fn save_json(path: &Path, data: &Value) -> Result<()> {
    let mut bytes = serde_json::to_vec_pretty(data)?;
    bytes.push(b'\n');
    Ok(fs::write(path, bytes)?)
}

fn write_part(out: &Path, name: &str, part: &Solid) -> Result<String> {
    part.check()?;
    ensure!(part.components().len() == 1, "{name} must be a connected part");
    let bytes = stl_bytes(&[part])?;
    fs::write(out.join(format!("{name}.stl")), &bytes)?;
    Ok(digest(&bytes))
}

/// Continue each roof pocket straight up from its existing sidewalls and endwalls.
fn relieve_roof(base: &Solid, st: &Station) -> Result<Solid> {
    let mut result = base.clone();
    for side in [-1.0, 1.0] {
        let at = |r| st.axis_x + side * r;
        let (a, b) = (at(st.neck), at(st.outer + 1.0));
        let pocket = brick([a.min(b), a.max(b), st.y0 - running(), PISCO_WING_AFT_Y + running(),
            st.ceiling - 0.04, st.ceiling + HEADROOM]);
        let next = result.cut(&pocket)?;
        ensure!(result.volume() - next.volume() > 100.0, "each pocket must deepen through its span");
        result = next;
    }
    Ok(result)
}

/// Bring the catching faces to the intermediate preload while preserving their lead-ins.
fn moderate_hook(source: &Solid, st: &Station) -> Result<Solid> {
    let nose_r = st.ledge - stations::REACH;
    let nose_z = st.bearing + stations::catch_air();
    let leaf_z = nose_z - (st.inner - nose_r) * stations::corbel_slope();
    let mut pieces = vec![source.clone()];
    for side in [-1.0, 1.0] {
        let at = |r, z| v2(st.axis_x + side * r, z);
        let section = Profile::polygon(&[
            at(nose_r, nose_z - HOOK_TAKE_UP), at(st.inner, leaf_z - HOOK_TAKE_UP),
            at(st.inner, leaf_z + stations::NOSE_LAND / 2.0),
            at(nose_r, nose_z + stations::NOSE_LAND / 2.0),
        ]);
        pieces.push(Plane::XZ.at(v3(0.0, st.y0, 0.0)).extrude(&section, st.y0 - PISCO_WING_AFT_Y)?);
    }
    Solid::union_all(&pieces)
}

/// The cap carries recessed bars on its flat back and the base carries matching notches on the cut roof edge.
fn mark_pair(base: &mut Solid, cover: &mut Solid, st: &Station, count: usize) -> Result<()> {
    let z = cover.bounds().min.z;
    let mid = (st.y0 + st.y1) / 2.0;
    for i in 0..count {
        let x = CROP[0] + 5.0 + i as f64 * 3.5;
        let y = mid + (i as f64 - (count - 1) as f64 / 2.0) * 3.2;
        let base_cut = brick([x, x + 1.4, CROP[2] - 0.05, CROP[2] + 2.1, CROP[5] - 7.0, CROP[5] + 0.1]);
        let cover_cut = brick([st.axis_x - 2.3, st.axis_x + 2.3, y - 0.65, y + 0.65, z - 0.05, z + 0.60]);
        let next_base = base.cut(&base_cut)?;
        let next_cover = cover.cut(&cover_cut)?;
        ensure!(base.volume() - next_base.volume() > 4.0 && cover.volume() - next_cover.volume() > 3.0,
            "identification notch must reach both parts");
        *base = next_base;
        *cover = next_cover;
    }
    Ok(())
}

/// Intersect the production support regions with the article and give each bridge its own axial infill direction.
fn features(source: &Value, name: &str, sha: &str, bridge: &Value) -> Result<Value> {
    let mut data = json!({"producer":name,"source_stl_sha256":sha,"boundary_overlap_mm":source["boundary_overlap_mm"]});
    for key in ["support_free_regions", "support_regions", "bridge_regions"] {
        let mut kept = Vec::new();
        for entry in source[key].as_array().context("production print regions")? {
            let mut row = entry.clone();
            let mut inside = true;
            for field in ["bounds_source_mm", "blocking_bounds_source_mm"] {
                if let Some(bounds) = row.get_mut(field) {
                    let mut clipped: Bounds = serde_json::from_value(bounds.clone())?;
                    for axis in 0..3 {
                        clipped[axis * 2] = clipped[axis * 2].max(CROP[axis * 2]);
                        clipped[axis * 2 + 1] = clipped[axis * 2 + 1].min(CROP[axis * 2 + 1]);
                        inside &= clipped[axis * 2] < clipped[axis * 2 + 1];
                    }
                    *bounds = json!(clipped);
                }
            }
            if inside { kept.push(row); }
        }
        if key == "bridge_regions" {
            kept.extend(bridge["bridge_regions"].as_array().into_iter().flatten().cloned());
        }
        data[key] = json!(kept);
    }
    Ok(data)
}

fn main() -> Result<()> {
    let out = Path::new(OUT);
    fs::create_dir_all(out)?;
    let st = stations::pisco_station();
    let production_cap = hsm_kernel::import::model(CAPS)?.into_iter()
        .find(|body| body.name == "pisco-snap-cap").context("installed Pisco cover")?.solid;
    let enclosure = hsm_kernel::import::model(BACK)?.into_iter().next().context("production back-top")?.solid;
    let common_base = relieve_roof(&enclosure.intersect(&brick(CROP))?, &st)?;
    let common_cover = moderate_hook(&production_cap, &st)?;
    let source_features: Value = serde_json::from_slice(&fs::read(FEATURES)?)?;
    let mut variants = Vec::new();
    for (index, letter) in ["a", "b", "c", "d"].into_iter().enumerate() {
        let mut bridge = Value::Null;
        let (mut base, mut cover) = match letter {
            "a" => (common_base.clone(), common_cover.clone()),
            "b" => (locators::rear_stops(&common_base, &st)?, locators::front_stops(&common_cover, &st)?),
            _ => {
                let long = letter == "d";
                bridge = bridges::details(&st, long);
                (bridges::receiver(&common_base, &st, long)?, bridges::cover(&production_cap, &st, long)?)
            }
        };
        let mark = index + 1;
        mark_pair(&mut base, &mut cover, &st, mark)?;
        let base_name = format!("pisco-base-{letter}");
        let cover_name = format!("pisco-cover-{letter}");
        let base_sha = write_part(out, &base_name, &base)?;
        let turned = cover.rotate(V3::ZERO, V3::X, 90.0);
        let b = turned.bounds();
        let t = v3(-(b.min.x + b.max.x) / 2.0, -(b.min.y + b.max.y) / 2.0, -b.min.z);
        let cap_sha = write_part(out, &cover_name, &turned.translate(t))?;
        save_json(&out.join(format!("{base_name}.print-features.json")), &features(&source_features, &base_name, &base_sha, &bridge)?)?;
        variants.push(json!({"mark":mark,"letter":letter,"base":base_name,"base_stl_sha256":base_sha,
            "cover":cover_name,"cover_stl_sha256":cap_sha,"print_translation_after_x90_mm":[t.x,t.y,t.z],"bridge":bridge}));
    }
    save_json(&out.join("geometry.json"), &json!({
        "production_back_top":BACK,"back_top_sha256":digest(&fs::read(BACK)?),
        "production_caps":CAPS,"caps_sha256":digest(&fs::read(CAPS)?),"source_corner_features":FEATURES,
        "crop_bounds_mm":CROP,"source_axis_x_mm":st.axis_x,"wing_y_mm":[st.y0,PISCO_WING_AFT_Y],
        "original_roof_z_mm":st.ceiling,"pocket_roof_relief_mm":HEADROOM,"revised_roof_skin_mm":enclosure.bounds().max.z-st.ceiling-HEADROOM,
        "moderate_hook_take_up_z_mm":HOOK_TAKE_UP,"moderate_free_hook_gap_z_mm":stations::catch_air()-HOOK_TAKE_UP,
        "locators":locators::measurements(&st),"variants":variants
    }))
}
