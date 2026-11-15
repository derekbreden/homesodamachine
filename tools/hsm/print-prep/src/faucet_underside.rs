//! Prepares the slicer's temporary base fill and replaces it with the faucet's sloped underside.

use crate::faucet::file_sha;
use crate::faucet_contact::{ContactBand, replace_prediction, write_archive, write_motion_result};
use crate::faucet_recesses::add_blocker;
use crate::ids::md5_hex;
use crate::mesh::{Mesh, bounds};
use crate::refresh::Refreshed;
use crate::{apply, sha256_hex};
use anyhow::{Context, Result, ensure};
use hsm_faucet_numbers::shell::{
    BASE_INSERT_BOTTOM_Z, BASE_POD_CENTERS, BASE_POD_INSERT_DEPTH, BASE_POD_Z_BOTTOM, PRINT_BASE_BUILD_ROT,
    base_pod_hole_dia,
};
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::fs;
use std::path::{Path, PathBuf};

const GCODE: &str = "Metadata/plate_1.gcode";
/// The left nozzle head's height map over the bed, which the stages' crossings clear.
pub const HEAD_MAP: &str = "tools/hsm/print-prep/faucet-underside/left-active-height.npz";
pub const SOURCES: [&str; 5] = [
    "tools/hsm/print-prep/src/faucet_underside.rs",
    "tools/hsm/print-prep/src/filled_base.rs",
    "tools/hsm/print-prep/src/base_foundation.rs",
    "tools/hsm/print-prep/src/sloped_courses.rs",
    HEAD_MAP,
];

pub struct Underside {
    index: usize,
    source: PathBuf,
    rim: [f64; 2],
}

impl Underside {
    /// Keep the base's trees and bridges inside the real part and record its seat in plate coordinates.
    pub fn prepare(r: &mut Refreshed, part: &str, rim: [f64; 2], selection: &Value) -> Result<Self> {
        let row = r.row(part)?;
        let index = row.index;
        let source = row.source.clone();
        let object = &r.plate.objects[index];
        let seat = apply(&object.rotation, object.source_center.map(|c| -c));
        let seat = std::array::from_fn::<_, 3, _>(|axis| seat[axis] + object.translation[axis]);
        let normal = apply(&object.rotation, [0., 0., -1.]);
        let radius = base_pod_hole_dia() / 2.0
            + selection["insert_blocker_radial_clearance_mm"].as_f64().context("insert blocker clearance")?;
        let [under, over]: [f64; 2] = serde_json::from_value(selection["insert_blocker_depth_allowance_mm"].clone())?;
        let depth = [BASE_POD_Z_BOTTOM - under, BASE_INSERT_BOTTOM_Z + BASE_POD_INSERT_DEPTH + over];
        let mut pockets = Vec::new();
        for (i, center) in BASE_POD_CENTERS.into_iter().enumerate() {
            let name = format!("Keep tree support clear of mounting insert {}", i + 1);
            let id = add_blocker(&mut r.plate, index, &name, center, radius, depth)?;
            pockets.push(json!({"part_id": id, "cad_center_mm": center,
                "blocker_radius_mm": radius, "blocker_cad_z_mm": depth}));
        }
        let settings = selection["object_settings"].as_object().context("base support settings")?;
        let object = &mut r.plate.objects[index];
        object.settings.retain(|(key, _)| !settings.contains_key(key));
        for (key, value) in settings {
            object.settings.push((key.clone(), value.as_str().with_context(|| format!("base setting {key}"))?.into()));
        }
        let temperature = |key| crate::profile::first_text(&r.plate.settings, key)
            .with_context(|| format!("the plate has no left-nozzle {key}"));
        r.extra.insert("base_underside".into(), json!({
            "part": part, "rim_semi_axes_mm": rim, "seat_print_world_center_mm": seat,
            "seat_print_world_outward_normal": normal, "bridge_only_pockets": pockets,
            "identify_id": object.identify_id,
            "nozzle_temperature": [temperature("nozzle_temperature")?],
            "nozzle_temperature_initial_layer": [temperature("nozzle_temperature_initial_layer")?],
            "object_settings": settings, "physical_reference": selection["physical_reference"],
        }));
        Ok(Self { index, source, rim })
    }

    /// Give Bambu Studio a filled base in the same pose, restoring the real project meshes in its slice.
    pub fn slice_bands(
        &self, r: &mut Refreshed, scopes: &[(usize, &ContactBand)], project: &Path,
        directory: &Path, slicer: &Path, filled_seam: &Value,
    ) -> Result<Value> {
        ensure!(!directory.exists() || fs::read_dir(directory)?.next().is_none(),
            "the underside slice directory must be empty");
        let filled = self.filled_mesh(r)?;
        let obj = &mut r.plate.objects[self.index];
        let local = filled.vertices.iter().map(|p| std::array::from_fn(|i| p[i] - obj.source_center[i]));
        let original_vertices = std::mem::replace(&mut obj.vertices, local.collect());
        let original_faces = std::mem::replace(&mut obj.faces, filled.faces);
        let original_paint = obj.paint.take();
        let result = (|| {
            crate::faucet::enforce_rear_seam(r, filled_seam)?;
            ContactBand::slice_bands(&mut r.plate, scopes, project, directory, slicer)
        })();
        let obj = &mut r.plate.objects[self.index];
        obj.vertices = original_vertices;
        obj.faces = original_faces;
        obj.paint = original_paint;
        result
    }

    /// The base with closed stock below its mounting face, in the same pose on the plate.
    fn filled_mesh(&self, r: &Refreshed) -> Result<Mesh> {
        let mesh = crate::filled_base::fill(&Mesh::read_stl(&self.source)?, PRINT_BASE_BUILD_ROT.to_degrees(), self.rim)?;
        let row = &r.rows[self.index];
        let object = &r.plate.objects[self.index];
        let placed: Vec<_> = mesh.vertices.iter().map(|p| {
            let local = std::array::from_fn(|i| p[i] - object.source_center[i]);
            let turned = apply(&object.rotation, local);
            std::array::from_fn(|i| turned[i] + object.translation[i])
        }).collect();
        let (lo, hi) = bounds(&placed);
        ensure!((0..3).all(|i| (lo[i] - row.low[i]).abs().max((hi[i] - row.high[i]).abs()) < 0.005),
            "the base fill changed its plate bounds");
        Ok(mesh)
    }

    /// Replace the cooled and mapped slice's fill paths with the shaped scaffold, roof and face.
    pub fn finish(&self, root: &Path, project: &Path, directory: &Path, preparation: &Value) -> Result<Value> {
        let raw = directory.join("plate_1.gcode");
        let head = root.join(HEAD_MAP);
        let (text, mut report) = crate::base_foundation::skin_underside(&fs::read(&raw)?, preparation, &self.source, &head)?;
        let gcode = text.into_bytes();
        fs::write(&raw, &gcode)?;
        let envelope = crate::refresh::object_toolpaths(&gcode, None)?;
        let [[x0, y0], [x1, y1]]: [[f64; 2]; 2] = serde_json::from_value(envelope["extrusion_bounds_xy_mm"].clone())?;
        let [[xmin, ymin], [xmax, ymax]]: [[f64; 2]; 2] = serde_json::from_value(preparation["shared_printable_area_mm"].clone())?;
        report["fit"] = json!({"complete_bead_bounds": envelope,
            "complete_bead_minimum_bed_margin_mm": (x0 - xmin).min(y0 - ymin).min(xmax - x1).min(ymax - y1)});
        report["head_height_map_sha256"] = json!(file_sha(&head)?);
        report["base_stl_sha256"] = json!(file_sha(&self.source)?);
        report["gcode_sha256"] = json!(sha256_hex(&gcode));
        let report_member = serde_json::to_vec_pretty(&report)?;
        let archive = directory.join(format!("{}.gcode.3mf", project.file_stem().context("project stem")?.to_string_lossy()));
        let mut zip = zip::ZipArchive::new(fs::File::open(&archive)?)?;
        let mut replaced = BTreeMap::from([
            (format!("{GCODE}.md5"), md5_hex(&gcode).into_bytes()),
            (GCODE.into(), gcode),
            ("Metadata/hsm_sloped_underside.json".into(), report_member),
        ]);
        let seconds = report["preamble"]["seconds"].as_f64().context("underside motion time")?;
        replace_prediction(&mut zip, &mut replaced, seconds)?;
        write_archive(zip, replaced, &archive, false)?;
        let result_path = directory.join("result.json");
        write_motion_result(&result_path, &result_path, seconds)?;
        report["archive_sha256"] = json!(file_sha(&archive)?);
        fs::write(directory.join("sloped-underside.json"), serde_json::to_vec_pretty(&report)?)?;
        Ok(report)
    }
}
