//! The full-length Pisco covers compare two roof contact heights with the fitted spring and outlet profile.
#[allow(dead_code)]
#[path = "../../printed-parts/enclosure/rear-equipment-caps/stations.rs"]
mod stations;

use anyhow::{Context, Result, ensure};
use hsm_enclosure_numbers::layout::{PISCO_WING_AFT_Y, Station};
use hsm_kernel::{Plane, Profile, Solid, V3, stl_bytes, v2, v3};
use serde_json::json;
use sha2::{Digest, Sha256};
use std::{fs, path::Path};

const SOURCE: &str = "hardware/printed-parts/enclosure/rear-equipment-caps/rear-equipment-caps-installed.step.npz";
const OUT: &str = "hardware/print-tests/pisco-raised-tip-cover/parts";
const NAME: &str = "pisco-raised-tip-cover";
const HIGHER_NAME: &str = "pisco-raised-tip-cover-040";
const FREE_HOOK_OVERLAP: f64 = 0.55;
const CREST_RISE: f64 = 0.20;
const HIGHER_CREST_RISE: f64 = 0.40;
const CREST_WIDTH: f64 = 0.90;
const MARK_FROM_FRONT: f64 = 6.0;
const MARK_SPACING: f64 = 3.0;

fn sha256(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

fn raised_cover(body: Solid, st: &Station, rise: f64, marks: u32) -> Result<Solid> {
    let nose = st.ledge - stations::REACH;
    let nose_z = st.bearing + stations::catch_air();
    let inner_z = nose_z - (st.inner - nose) * stations::corbel_slope();
    let take_up = stations::catch_air() + FREE_HOOK_OVERLAP;
    let top = st.ceiling - stations::tip_air();
    let shoulder = nose_z + stations::NOSE_LAND;
    let plane = Plane::XZ.at(v3(0.0, st.y0, 0.0));
    let span = st.y0 - PISCO_WING_AFT_Y;
    let mut stock = vec![body];
    for side in [-1.0, 1.0] {
        let at = |radius, z| v2(st.axis_x + side * radius, z);
        let bearing = Profile::polygon(&[
            at(nose, nose_z - take_up),
            at(st.inner, inner_z - take_up),
            at(st.inner, inner_z + stations::NOSE_LAND / 2.0),
            at(nose, nose_z + stations::NOSE_LAND / 2.0),
        ]);
        let crest = Profile::polygon(&[
            at(nose, shoulder),
            at(st.outer - CREST_WIDTH, top + rise),
            at(st.outer, top + rise),
            at(st.outer, top - 0.60),
            at(nose + 0.60, shoulder - 0.20),
        ]);
        stock.push(plane.extrude(&bearing, span)?);
        stock.push(plane.extrude(&crest, span)?);
    }
    let mut cover = Solid::union_all(&stock)?;
    let bottom = cover.bounds().min.z;
    let mark_center = st.y0 + MARK_FROM_FRONT;
    for index in 0..marks {
        let y = mark_center + (f64::from(index) - f64::from(marks - 1) / 2.0) * MARK_SPACING;
        let notch = Solid::cuboid(
            v3(st.axis_x - 2.3, y - 0.65, bottom - 0.10),
            v3(st.axis_x + 2.3, y + 0.65, bottom + 0.65),
        );
        let marked = cover.cut(&notch)?;
        ensure!(cover.volume() - marked.volume() > 3.0, "each mark reaches the cover back");
        cover = marked;
    }
    Ok(cover)
}

fn export(name: &str, file: &str, cover: &Solid, st: &Station, rise: f64, marks: u32) -> Result<()> {
    let out = Path::new(OUT);
    cover.check()?;
    ensure!(cover.components().len() == 1, "the full cover is one connected solid");
    let built = cover.rotate(V3::ZERO, V3::X, 90.0);
    let b = built.bounds();
    let shift = v3(-(b.min.x + b.max.x) / 2.0, -(b.min.y + b.max.y) / 2.0, -b.min.z);
    let bytes = stl_bytes(&[&built.translate(shift)])?;
    fs::write(out.join(format!("{name}.stl")), &bytes)?;
    let manifest = json!({
        "name":name,
        "production_cap":SOURCE,
        "production_source_sha256":sha256(&fs::read(SOURCE)?),
        "stl_sha256":sha256(&bytes),
        "receiver":"hardware/print-tests/rear-equipment-corner/parts/rear-equipment-corner.stl",
        "regulator_mesh_key":"c66fbc2b8f12019ee2085445889e91f329c9e352e3b089e12f7e8024bc6e7939",
        "installed_cover_y_mm":[st.y0, st.y1],
        "installed_wing_y_mm":[st.y0, PISCO_WING_AFT_Y],
        "spring_free_retaining_overlap_mm":FREE_HOOK_OVERLAP,
        "roof_contact_rise_mm":rise,
        "roof_contact_width_mm":CREST_WIDTH,
        "original_tip_z_mm":st.ceiling - stations::tip_air(),
        "nominal_roof_z_mm":st.ceiling,
        "print_translation_after_x90_mm":[shift.x,shift.y,shift.z],
        "volume_mm3":cover.volume(),
        "identification_bars":marks
    });
    let mut manifest = serde_json::to_vec_pretty(&manifest)?;
    manifest.push(b'\n');
    fs::write(out.join(file), manifest)?;
    Ok(())
}

fn main() -> Result<()> {
    fs::create_dir_all(OUT)?;
    let source = hsm_kernel::import::model(SOURCE)?
        .into_iter()
        .find(|body| body.name == "pisco-snap-cap")
        .context("installed Pisco cap")?
        .solid;
    let st = stations::pisco_station();
    for (name, record, rise, marks) in [
        (NAME, "geometry.json", CREST_RISE, 2),
        (HIGHER_NAME, "geometry-040.json", HIGHER_CREST_RISE, 4),
    ] {
        let cover = raised_cover(source.clone(), &st, rise, marks)?;
        export(name, record, &cover, &st, rise, marks)?;
    }
    Ok(())
}
