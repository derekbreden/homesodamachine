//! faucet-print-project — the faucet's four printed parts on one PET-GF plate, in the shared
//! profile's complete settings, and optionally its offline slice. Never contacts a printer.
//!
//!     faucet-print-project [--project P] [--settings-from S] [--z-trim MM] [--slice-output DIR]
//!                          [--slicer PATH]

use anyhow::{bail, Context, Result};
use hsm_faucet_numbers::shell::{PRINT_BASE_BUILD_ROT, PRINT_TIP_BUILD_ROT};
use hsm_print_prep::json::{python_number, Json};
use hsm_print_prep::mesh::{bounds, Mesh};
use hsm_print_prep::profile::{self, relative};
use hsm_print_prep::project::{MeshStyle, Plate};
use hsm_print_prep::{apply, root, rotation_x, sha256_hex, slice};
use std::path::{Path, PathBuf};

/// Millimetres from the centre of the shared printable area. The base takes the left column;
/// the other three parts have their own support and brim space.
const PART_OFFSETS: [[f64; 2]; 4] = [[-80.0, 0.0], [20.0, 47.0], [89.0, 106.0], [43.0, -52.0]];
const PLATE_BORDER: f64 = 20.0;
const TITLE: &str = "Faucet PET-GF";

fn parts(here: &Path) -> Vec<(&'static str, PathBuf, f64)> {
    vec![
        ("faucet-shell-base", here.join("faucet-shell/faucet-shell-base.stl"), -PRINT_BASE_BUILD_ROT.to_degrees()),
        ("faucet-shell-tip", here.join("faucet-shell/faucet-shell-tip.stl"), -PRINT_TIP_BUILD_ROT.to_degrees()),
        ("faucet-display-cover", here.join("faucet-display-cover/faucet-display-cover.stl"), -50.0),
        ("above-counter-plate", here.join("above-counter-plate/above-counter-plate.stl"), 0.0),
    ]
}

fn num(v: f64) -> Json {
    Json::Number(python_number(v), v)
}

fn list(values: &[f64]) -> Json {
    Json::List(values.iter().map(|v| num(*v)).collect())
}

fn text(s: &str) -> Json {
    Json::Text(s.to_string())
}

fn main() -> Result<()> {
    let root = root();
    let here = root.join("hardware/printed-parts/faucet");
    let mut project = here.join("faucet-petgf.3mf");
    let mut settings_from = root.join("hardware/printed-parts/petgf.3mf");
    let mut z_trim = None;
    let mut slice_output: Option<PathBuf> = None;
    let mut slicer = PathBuf::from(slice::SLICER);
    let mut args = std::env::args().skip(1);
    while let Some(arg) = args.next() {
        let mut value = || args.next().with_context(|| format!("{arg} needs a value"));
        match arg.as_str() {
            "--project" => project = PathBuf::from(value()?),
            "--settings-from" => settings_from = PathBuf::from(value()?),
            "--z-trim" => z_trim = Some(value()?.parse::<f64>()?),
            "--slice-output" => slice_output = Some(PathBuf::from(value()?)),
            "--slicer" => slicer = PathBuf::from(value()?),
            _ => bail!("unknown argument {arg}"),
        }
    }
    let settings_from = settings_from.canonicalize()?;
    let profile = profile::load(&settings_from, z_trim, None, &root)?;
    let settings = &profile.settings;
    let get = |key: &str| settings.first_text(key).with_context(|| format!("the profile has no {key}"));
    let number = |key: &str| -> Result<f64> { Ok(get(key)?.trim_end_matches('%').parse()?) };

    let mut plate = Plate::new(TITLE, &profile, "homesodamachine/faucet/");
    plate.filament_maps = Some("1".into());
    plate.build_name = Some("build".into());
    plate.mesh_style = MeshStyle::Element;
    let (low, high) = (profile.usable_low, profile.usable_high);
    let mut rows = Vec::new();
    for (i, (name, source, angle)) in parts(&here).into_iter().enumerate() {
        let payload = std::fs::read(&source).with_context(|| format!("reading {}", source.display()))?;
        let mesh = Mesh::read_stl(&source)?;
        mesh.check_closed_single_body(&source.file_name().unwrap().to_string_lossy())?;
        let center = mesh.center();
        let local: Vec<[f64; 3]> = mesh.vertices.iter().map(|v| [v[0] - center[0], v[1] - center[1], v[2] - center[2]]).collect();
        let rotation = rotation_x(angle);
        let rotated: Vec<[f64; 3]> = local.iter().map(|v| apply(&rotation, *v)).collect();
        let (rlow, rhigh) = bounds(&rotated);
        let plate_center = [(low[0] + high[0]) / 2.0 + PART_OFFSETS[i][0], (low[1] + high[1]) / 2.0 + PART_OFFSETS[i][1], 0.0];
        let translation = [plate_center[0] - (rlow[0] + rhigh[0]) / 2.0, plate_center[1] - (rlow[1] + rhigh[1]) / 2.0, -rlow[2]];
        let placed: Vec<[f64; 3]> = rotated.iter().map(|v| [v[0] + translation[0], v[1] + translation[1], v[2] + translation[2]]).collect();
        let (plow, phigh) = bounds(&placed);
        if plow[0] < low[0] + PLATE_BORDER || plow[1] < low[1] + PLATE_BORDER || phigh[0] > high[0] - PLATE_BORDER || phigh[1] > high[1] - PLATE_BORDER {
            bail!("{name} extends into the {} mm plate border", PLATE_BORDER);
        }
        if phigh[2] > number("printable_height")? {
            bail!("{name} exceeds the printer height");
        }
        let triangles = mesh.faces.len();
        let index = plate.add_object(name, local.clone(), mesh.faces.clone(), &source.file_name().unwrap().to_string_lossy(),
                                     center, rotation, translation, None, Vec::new());
        let obj = &plate.objects[index];
        let error = local.iter().zip(&mesh.vertices)
            .flat_map(|(l, v)| (0..3).map(move |k| (format!("{:.9}", l[k]).parse::<f64>().unwrap() + center[k] - v[k]).abs()))
            .fold(0.0, f64::max);
        rows.push(Json::Map(vec![
            ("name".into(), text(name)), ("plate".into(), num_int(1)),
            ("object_id".into(), text(&obj.object_id.to_string())), ("part_id".into(), text(&obj.part_id.to_string())),
            ("member".into(), text(&obj.member)), ("identify_id".into(), num_int(obj.identify_id as i64)),
            ("source".into(), text(&relative(&source, &root))), ("stl_sha256".into(), text(&sha256_hex(&payload))),
            ("triangles".into(), num_int(triangles as i64)), ("rotation_x_degrees".into(), num(angle)),
            ("source_center_mm".into(), list(&center)), ("build_transform".into(), list(&obj.transform_values())),
            ("plate_translation_mm".into(), list(&translation)), ("plate_origin_mm".into(), list(&[0.0, 0.0, 0.0])),
            ("plate_bounds_mm".into(), Json::List(vec![list(&plow), list(&phigh)])),
            ("watertight".into(), Json::Bool(true)), ("body_count".into(), num_int(1)),
            ("embedded_vertex_error_mm".into(), num(error)),
        ]));
    }
    plate.write(&project)?;
    let settings_payload = plate.settings.dumps() + "\n";
    let line_widths = ["outer_wall_line_width", "inner_wall_line_width", "sparse_infill_line_width",
                       "internal_solid_infill_line_width", "top_surface_line_width", "support_line_width"]
        .iter().map(|k| Ok((k.to_string(), num(number(k)?)))).collect::<Result<Vec<_>>>()?;
    let floats = |key: &str| -> Result<Json> {
        Ok(Json::List(settings.get(key).map(Json::list).unwrap_or(&[]).iter()
            .filter_map(Json::text).map(|s| s.parse::<f64>().map(num)).collect::<Result<_, _>>()?))
    };
    let report = Json::Map(vec![
        ("project".into(), text(&project.file_name().unwrap().to_string_lossy())),
        ("settings_source".into(), text(&relative(&settings_from, &root))),
        ("settings_source_sha256".into(), text(&sha256_hex(&std::fs::read(&settings_from)?))),
        ("settings_sha256".into(), text(&sha256_hex(settings_payload.as_bytes()))),
        ("source_settings_sha256".into(), text(&sha256_hex(&profile.original_payload))),
        ("settings_changes".into(), Json::from_value(&serde_json::Value::Object(profile.changes.clone()))),
        ("printer".into(), text(get("printer_settings_id")?)),
        ("process".into(), text(get("print_settings_id")?)),
        ("filament".into(), settings.get("filament_settings_id").cloned().unwrap_or(Json::Null)),
        ("layer_height_mm".into(), num(number("layer_height")?)),
        ("nozzle_diameter_mm".into(), floats("nozzle_diameter")?),
        ("line_widths_mm".into(), Json::Map(line_widths)),
        ("wall_loops".into(), num_int(number("wall_loops")? as i64)),
        ("sparse_infill_percent".into(), num(number("sparse_infill_density")?)),
        ("sparse_infill_pattern".into(), text(get("sparse_infill_pattern")?)),
        ("saved_profile_filament_density_g_cm3".into(), floats("filament_density")?),
        ("bed_type".into(), text(get("curr_bed_type")?)),
        ("shared_printable_area_mm".into(), Json::List(vec![list(&low), list(&high)])),
        ("printable_area_extruders".into(), Json::List(profile.printable_area_extruders.iter().map(|&i| num_int(i as i64)).collect())),
        ("plate_border_mm".into(), num(PLATE_BORDER)),
        ("plate_count".into(), num_int(1)),
        ("parts".into(), Json::List(rows)),
        ("project_sha256".into(), text(&sha256_hex(&std::fs::read(&project)?))),
        ("settings_preserved_byte_for_byte".into(), Json::Bool(settings_payload.as_bytes() == profile.original_payload.as_slice())),
    ]);
    std::fs::write(project.with_extension("print.json"), report.dumps() + "\n")?;
    println!("{}: four parts on one plate; exact settings {}", project.display(), sha256_hex(settings_payload.as_bytes()));
    if let Some(directory) = slice_output {
        slice::run(&slicer, &project, &directory)?;
        slice::apply_directory(&directory.canonicalize()?, &project.canonicalize()?)?;
    }
    Ok(())
}

fn num_int(v: i64) -> Json {
    Json::Number(v.to_string(), v as f64)
}
