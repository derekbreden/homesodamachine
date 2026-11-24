//! The two outlet collars compare roof contact in the original corner with the same rear collar and regulator.
#[allow(dead_code)]
#[path = "../../printed-parts/enclosure/rear-equipment-caps/stations.rs"]
mod stations;

use anyhow::{Context, Result, ensure};
use hsm_enclosure_numbers::layout::{PISCO_WING_AFT_Y, Station};
use hsm_kernel::{Plane, Profile, Solid, V3, stl_bytes, v2, v3};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{fs, path::Path};

const SOURCE: &str = "hardware/printed-parts/enclosure/rear-equipment-caps/rear-equipment-caps-installed.step.npz";
const OUT: &str = "hardware/print-tests/rear-receiver-quick/parts";
const SECTION_LENGTH: f64 = 12.0;
const FREE_HOOK_OVERLAP: f64 = 0.55;
const CREST_RISE: f64 = 0.20;
const CREST_WIDTH: f64 = 0.90;

fn digest(bytes: &[u8]) -> String { format!("{:x}", Sha256::digest(bytes)) }

/// Each section has the tested three-diamond retaining face, nose, lead-in and spring root.
fn spring_section(source: &Solid, st: &Station, lo: f64, hi: f64, crest: bool) -> Result<Solid> {
    let b = source.bounds();
    let body = source.intersect(&Solid::cuboid(v3(b.min.x - 1.0, lo, b.min.z - 1.0),
                                               v3(b.max.x + 1.0, hi, b.max.z + 1.0)))?;
    let mut solids = vec![body];
    let hook_hi = hi.min(PISCO_WING_AFT_Y);
    let nose = st.ledge - stations::REACH;
    let z = st.bearing + stations::catch_air();
    let inner_z = z - (st.inner - nose) * stations::corbel_slope();
    let take_up = stations::catch_air() + FREE_HOOK_OVERLAP;
    for side in [-1.0, 1.0] {
        let at = |r, z| v2(st.axis_x + side * r, z);
        let fill = Profile::polygon(&[at(nose, z - take_up), at(st.inner, inner_z - take_up),
                                     at(st.inner, inner_z + stations::NOSE_LAND / 2.0),
                                     at(nose, z + stations::NOSE_LAND / 2.0)]);
        let along = |p: &Profile| Plane::XZ.at(v3(0.0, lo, 0.0)).extrude(p, lo - hook_hi);
        solids.push(along(&fill)?);
        if crest {
            let top = st.ceiling - stations::tip_air();
            let shoulder = z + stations::NOSE_LAND;
            let pad = Profile::polygon(&[
                at(nose, shoulder), at(st.outer - CREST_WIDTH, top + CREST_RISE),
                at(st.outer, top + CREST_RISE), at(st.outer, top - 0.60),
                at(nose + 0.60, shoulder - 0.20),
            ]);
            solids.push(along(&pad)?);
        }
    }
    Solid::union_all(&solids)
}

/// Notches on the flat outer back distinguish the front variants when the regulator is installed.
fn mark(s: &Solid, st: &Station, lo: f64, hi: f64, count: usize) -> Result<Solid> {
    let mut part = s.clone();
    let bottom = s.bounds().min.z;
    for i in 0..count {
        let y = (lo + hi)/2.0 + (i as f64 - (count - 1) as f64 / 2.0) * 3.0;
        let cut = Solid::cuboid(v3(st.axis_x - 2.3, y - 0.65, bottom - 0.1),
                                v3(st.axis_x + 2.3, y + 0.65, bottom + 0.65));
        let next = part.cut(&cut)?;
        ensure!(part.volume() - next.volume() > 3.0, "the identification must reach solid stock");
        part = next;
    }
    Ok(part)
}

fn export(name: &str, part: &Solid, span: [f64; 2], marks: usize) -> Result<Value> {
    part.check()?;
    ensure!(part.components().len()==1, "{name} is a connected collar");
    let rotated = part.rotate(V3::ZERO, V3::X, 90.0);
    let b = rotated.bounds();
    let shift = v3(-(b.min.x+b.max.x)/2.0, -(b.min.y+b.max.y)/2.0, -b.min.z);
    let mesh = stl_bytes(&[&rotated.translate(shift)])?;
    fs::write(Path::new(OUT).join(format!("{name}.stl")), &mesh)?;
    Ok(json!({"name":name,"marks":marks,"installed_y_mm":span,"print_translation_after_x90_mm":[shift.x,shift.y,shift.z],
        "stl_sha256":digest(&mesh),"volume_mm3":part.volume()}))
}

fn main() -> Result<()> {
    fs::create_dir_all(OUT)?;
    let source = hsm_kernel::import::model(SOURCE)?.into_iter().find(|b| b.name == "pisco-snap-cap")
        .context("installed Pisco cap")?.solid;
    let st = stations::pisco_station();
    let fore = [st.y0, st.y0 + SECTION_LENGTH];
    let aft = [st.y1 - SECTION_LENGTH, st.y1];
    let mut parts = Vec::new();
    for (name, span, marks, crest) in [("pisco-front-control",fore,1,false),("pisco-front-roof",fore,2,true),
                                      ("pisco-common-rear",aft,0,false)] {
        let plain = spring_section(&source,&st,span[0],span[1],crest)?;
        let part = mark(&plain,&st,span[0],span[1],marks)?;
        parts.push(export(name,&part,span,marks)?);
    }
    let data = json!({"production_cap":SOURCE,"production_source_sha256":digest(&fs::read(SOURCE)?),
        "three_diamond_reference":"6343b3ef52a582988ff37589afacd196ac068471:hardware/print-tests/pisco-cover-retention/parts/pisco-three-marks.stl",
        "reference_receiver":"hardware/print-tests/rear-equipment-corner/parts/rear-equipment-corner.stl",
        "regulator_mesh_key":"c66fbc2b8f12019ee2085445889e91f329c9e352e3b089e12f7e8024bc6e7939",
        "free_retaining_overlap_mm":FREE_HOOK_OVERLAP,"crest_rise_mm":CREST_RISE,"crest_width_mm":CREST_WIDTH,
        "wing_tip_unloaded_z_mm":st.ceiling-stations::tip_air(),"receiver_roof_z_mm":st.ceiling,
        "fore_to_aft_gap_mm":aft[0]-fore[1],"parts":parts});
    let mut json = serde_json::to_vec_pretty(&data)?; json.push(b'\n');
    Ok(fs::write(Path::new(OUT).join("pisco-geometry.json"), json)?)
}
