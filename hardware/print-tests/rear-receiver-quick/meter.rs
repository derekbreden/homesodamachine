//! This coupon prints the meter's recessed aft shoulder on a permanent slope rooted in the enclosure flank.
use anyhow::{Context, Result, ensure};
use hsm_enclosure_numbers::{Bounds, catalog::running, layout::REAR_SNAP_CHAMFER_SLOPE, shell::BACK_TOP_FLANK_T};
use hsm_kernel::{Solid, import, stl_bytes, v3};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{fs, path::Path};

const SOURCE: &str = "hardware/printed-parts/enclosure/enclosure/enclosure-back-top.step.npz";
const FEATURES: &str = "hardware/printed-parts/enclosure/enclosure/enclosure-back-top.print-features.json";
const PROFILE: &str = "hardware/printed-parts/petgf.profile.json";
const OUT: &str = "hardware/print-tests/rear-receiver-quick/parts";
const NAME: &str = "meter-shoulder-backed";
const CROWN_DEPTH: f64 = 3.9;
const FLANK_LEAD: f64 = 1.2;

fn region(features: &Value, kind: &str, name: &str) -> Result<Bounds> {
    let row = features[kind].as_array().context("production feature regions")?.iter()
        .find(|row| row["name"] == name).with_context(|| format!("missing {name}"))?;
    Ok(serde_json::from_value(row["bounds_source_mm"].clone())?)
}

fn main() -> Result<()> {
    let out = Path::new(OUT);
    fs::create_dir_all(out)?;
    let production = import::model(SOURCE)?;
    let source = import::body(&production, "enclosure-back-top")?;
    let features: Value = serde_json::from_slice(&fs::read(FEATURES)?)?;
    let shoulder = region(&features, "support_regions", "Accessible flow meter aft shoulder")?;
    let pocket = region(&features, "support_free_regions", "Flow meter upper cap pocket")?;
    let (west, flank, fore, aft) = (shoulder[0], pocket[1], pocket[3], shoulder[3]);
    let face = (shoulder[4] + shoulder[5]) / 2.0;
    let run = flank - west;
    let rise = run * REAR_SNAP_CHAMFER_SLOPE;
    let seam = running();
    let taper_end = fore + run - seam;
    ensure!(aft - fore > run, "the fore taper must reach the flank within the shoulder");

    // The flank backs each successive course. The fore taper gives the meter's upper spring room at the step.
    let backing = Solid::hull(&[
        v3(west, fore, face), v3(flank, fore, face), v3(flank, aft, face), v3(west, aft, face),
        v3(west + seam, fore, face + seam * REAR_SNAP_CHAMFER_SLOPE),
        v3(flank, fore, face + seam * REAR_SNAP_CHAMFER_SLOPE),
        v3(flank, taper_end, face + rise), v3(flank, aft, face + rise),
    ])?;
    let profile: Value = serde_json::from_slice(&fs::read(PROFILE)?)?;
    let pitch: f64 = profile["Metadata/project_settings.config"]["layer_height"]
        .as_str().context("PET-GF layer height")?.parse()?;
    let production_bed = source.bounds().max.z;
    let required_bed = face + rise + FLANK_LEAD;
    let bed = production_bed - ((production_bed - required_bed) / pitch).floor() * pitch;
    // Start the section on the aft shoulder, clear of the adjacent catch's end face.
    let low = v3(west, shoulder[2], face - CROWN_DEPTH);
    let high = v3(flank + BACK_TOP_FLANK_T, aft, bed);
    let crop = Solid::cuboid(low, high);
    let stock = source.intersect(&crop)?;
    let sample = stock.union(&backing.intersect(&crop)?)?;
    sample.check()?;
    ensure!(sample.components().len() == 1, "the shoulder and flank must form one part");
    let added = sample.volume() - stock.volume();

    let bytes = stl_bytes(&[&sample])?;
    let sha = format!("{:x}", Sha256::digest(&bytes));
    fs::write(out.join(format!("{NAME}.stl")), bytes)?;
    let data = json!({"part":NAME, "source":SOURCE, "source_sha256":format!("{:x}",Sha256::digest(fs::read(SOURCE)?)),
        "feature_source":FEATURES, "stl_sha256":sha, "print_up_source":[0,0,-1],
        "crop_bounds_source_mm":[low.x,high.x,low.y,high.y,low.z,high.z], "production_bed_z_mm":production_bed,
        "shoulder_face_z_mm":face, "west_edge_x_mm":west, "flank_x_mm":flank, "slope_rise_per_run":REAR_SNAP_CHAMFER_SLOPE,
        "fore_taper_y_mm":[fore, taper_end], "aft_y_mm":aft, "backing_added_mm3":added, "volume_mm3":sample.volume(),
        "purpose":"Check the printed edge and boss-channel crown against the loose strands on the four-notch trial. The slope grows from the flank and its fore end tapers clear of the meter cap."});
    let mut report = serde_json::to_vec_pretty(&data)?;
    report.push(b'\n');
    fs::write(out.join("meter-geometry.json"), report)?;
    Ok(())
}
