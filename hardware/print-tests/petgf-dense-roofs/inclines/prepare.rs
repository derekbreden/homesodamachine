//! prepare.rs writes and optionally slices the incline comparison plates without contacting a printer.
use anyhow::{Context, Result, ensure};
use hsm_print_prep::{json::Json, mesh::Mesh, profile, project::Plate, refresh, root, sha256_hex, slice};
use serde_json::{Value, json};
use std::path::{Path, PathBuf};

fn main() -> Result<()> {
    let root = root();
    let here = root.join("hardware/print-tests/petgf-dense-roofs/inclines");
    let args: Vec<String> = std::env::args().skip(1).collect();
    let run = PathBuf::from(args.first().context("usage: incline-support-plates RUN_DIRECTORY [--slice]")?);
    std::fs::create_dir_all(&run)?;
    let run = run.canonicalize()?;
    let spec: Value = serde_json::from_slice(&std::fs::read(here.join("matrix.json"))?)?;
    let source = root.join("hardware/printed-parts/petgf.3mf");
    let profile = profile::load(&source, Some(0.04), None, &root)?;
    for declared in spec["plates"].as_array().context("plates")? {
        let name = declared["id"].as_str().context("plate id")?;
        let directory = run.join(name);
        std::fs::create_dir_all(&directory)?;
        let mut plate = Plate::new(name, &profile, "homesodamachine/support-inclines/");
        plate.settings.set("filament_colour", Json::from_value(&json!(["#161616"])));
        plate.settings.set("support_filament", Json::Text("1".into()));
        plate.settings.set("support_interface_filament", Json::Text("1".into()));
        let mut records = Vec::new();
        for (i, row) in declared["samples"].as_array().context("samples")?.iter().enumerate() {
            let id = row["id"].as_str().context("sample id")?;
            let path = here.join("geometry").join(format!("{id}.stl"));
            let mesh = Mesh::read_stl(&path)?;
            mesh.check_closed_single_body(id)?;
            let (lo, hi) = mesh.bounds();
            let center = mesh.center();
            let local = mesh.vertices.iter().map(|v| [v[0]-center[0],v[1]-center[1],v[2]-center[2]]).collect();
            let translation = [118.5 + (i % 3) as f64 * 44., 142. + (i / 3) as f64 * 36., center[2]-lo[2]];
            let mut settings = std::collections::BTreeMap::new();
            for (key, value) in spec["common_object_settings"].as_object().context("common settings")?.iter().chain(row["settings"].as_object().context("sample settings")?.iter()) {
                settings.insert(key.clone(), value.as_str().context("string setting")?.to_string());
            }
            let index = plate.add_object(id, local, mesh.faces.clone(), &format!("{id}.stl"), center, [[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]], translation, None, settings.into_iter().collect());
            let shape = &spec["geometry"];
            let wall = shape["wall_mm"].as_f64().context("wall")?;
            let width = shape["width_mm"].as_f64().context("width")?;
            let low = [wall + 0.1, -width / 2. + 0.1, shape["underside_start_z_mm"].as_f64().context("start")? - 0.25];
            let high = [hi[0] + 0.1, width / 2. - 0.1, hi[2]];
            let (vertices, faces) = refresh::box_mesh([0,1,2].map(|k| low[k]-center[k]), [0,1,2].map(|k| high[k]-center[k]));
            plate.add_part(index, "Inclined underside contact test", vertices, faces, "support_enforcer", vec![], None);
            records.push(json!({"id":id,"source":profile::relative(&path,&root),"source_sha256":sha256_hex(&std::fs::read(&path)?),"angle_from_bed_deg":row["angle_from_bed_deg"],"settings":row["settings"],"plate_center_xy_mm":[translation[0],translation[1]],"dimensions_mm":[hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2]]}));
        }
        let project = directory.join(format!("{name}.3mf"));
        plate.write(&project)?;
        let mut record = json!({"purpose":"Retain the prepared incline comparison, material, printer calibration and native estimate.","project":project.file_name().unwrap().to_string_lossy(),"project_sha256":sha256_hex(&std::fs::read(&project)?),"profile":profile::relative(&source,&root),"profile_sha256":sha256_hex(&std::fs::read(&source)?),"printer":"Mark2","requested_z_trim_mm":0.04,"nozzle":"left hardened Standard 0.4 mm","filament":"black PET-GF external spool","common_object_settings":spec["common_object_settings"],"samples":records,"submitted":false,"physical_result":"pending"});
        if args.iter().any(|a| a == "--slice") {
            let native = directory.join("native");
            slice::run(Path::new(slice::SLICER), &project, &native)?;
            slice::apply_directory(&native, &project)?;
            let result: Value = serde_json::from_slice(&std::fs::read(native.join("result.json"))?)?;
            ensure!(result["return_code"] == 0, "native slice failed");
            let gcode = std::fs::read(native.join("plate_1.gcode"))?;
            let archive = native.join(format!("{name}.gcode.3mf"));
            let paths = refresh::object_toolpaths(&gcode, None)?;
            record["native_result"] = result.clone();
            record["native_toolpaths"] = paths;
            record["trim_commands_mm"] = json!(refresh::trim_commands(&gcode));
            ensure!(refresh::trim_commands(&gcode) == refresh::expected_trims(0.04), "Mark2 trim differs");
            record["archive_sha256"] = json!(sha256_hex(&std::fs::read(&archive)?));
            record["gcode_sha256"] = json!(sha256_hex(&gcode));
            record["estimated_seconds"] = result["sliced_plates"][0]["total_predication"].clone();
        }
        std::fs::write(directory.join("preparation.json"), serde_json::to_vec_pretty(&record)?)?;
        println!("{}", project.display());
    }
    Ok(())
}
