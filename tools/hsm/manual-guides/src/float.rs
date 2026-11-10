//! The float's HTML templates take their changing figures from current design and print evidence.
use anyhow::{Context, Result, ensure};
use serde::Deserialize;
use serde_json::json;
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

#[derive(Deserialize)]
struct Dimensions {
    diameter: f64,
    height: f64,
    guide_bore: f64,
    bench_guide: f64,
    guide_radial_clearance: f64,
    magnet_midplane: f64,
    magnet_seat: f64,
    pocket_depth: f64,
    pocket_roof: f64,
}
#[derive(Deserialize)]
struct Magnet {
    od_mm: f64,
    id_mm: f64,
    thickness_mm: f64,
    source: String,
}
#[derive(Deserialize)]
struct PrintIntent {
    pause_before_layer_z_mm: f64,
}
#[derive(Deserialize)]
struct Design {
    cad_revision: String,
    dimensions_mm: Dimensions,
    magnet: Magnet,
    print_intent: PrintIntent,
}
#[derive(Deserialize)]
struct Recipe {
    layer_height_mm: f64,
    nozzle_c: f64,
    bed_c: f64,
    chamber_c: f64,
    flow_ratio: f64,
    line_width_mm: f64,
    wall_loops: usize,
}
#[derive(Deserialize)]
struct Mapping {
    external_slot: usize,
    nozzle: String,
}
#[derive(Deserialize)]
struct SliceSummary {
    estimated_time_s: f64,
}
#[derive(Deserialize)]
struct Preflight {
    recipe: Recipe,
    material_mapping: Mapping,
    requested_z_trim_mm: f64,
    native_slice_summary: SliceSummary,
}
#[derive(Deserialize)]
struct Trial {
    cad_revision: String,
    expected_first_covering_layer_z_mm: f64,
    expected_pause_before_layer: usize,
    ready_archive_prepared: bool,
    submitted: bool,
}
#[derive(Deserialize)]
struct PrintResult {
    task_id: String,
}
#[derive(Deserialize)]
struct Observations {
    next_trial: Trial,
    paused_print_result: PrintResult,
}
#[derive(Deserialize)]
struct Reach {
    carbonator: f64,
    reservoir: f64,
}
#[derive(Deserialize)]
struct Integration {
    float_cad_revision: String,
    rod_axis_from_inside_wall_mm: f64,
    carbonator_upright_wall_clearance_range_mm: [f64; 2],
    maximum_float_edge_to_reed_center_mm: Reach,
}
fn read<T: serde::de::DeserializeOwned>(path: &Path) -> Result<T> {
    serde_json::from_slice(&std::fs::read(path)?)
        .with_context(|| format!("read float source {}", path.display()))
}
fn escape(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#x27;")
}
fn general(v: f64) -> String {
    hsm_documents::format_number(v, "g").expect("general number format")
}

pub fn author(root: &Path, output: Option<&Path>) -> Result<()> {
    let guide = root.join("hardware/magnetic-float-guide");
    let float = root.join("hardware/printed-parts/cold-core/magnetic-float/all-aero");
    let design: Design = read(&float.join("design.json"))?;
    let preflight: Preflight = read(&float.join("mark2-print/v1/float-preflight.json"))?;
    let observations: Observations = read(&float.join("physical-observations.json"))?;
    let integration: Integration = read(&float.join("integration-check.json"))?;
    ensure!(
        design.cad_revision == observations.next_trial.cad_revision
            && design.cad_revision == integration.float_cad_revision,
        "float design, next trial and integration use different geometry revisions"
    );
    ensure!(
        design.print_intent.pause_before_layer_z_mm
            == observations.next_trial.expected_first_covering_layer_z_mm,
        "float insertion pause differs from the recorded next trial"
    );
    ensure!(
        !observations.next_trial.ready_archive_prepared && !observations.next_trial.submitted,
        "review the float guide's current preparation text against the prepared or submitted job"
    );
    let rod = hsm_cold_core_data::ROD_SPEC;
    let dims = &design.dimensions_mm;
    let recipe = &preflight.recipe;
    let mut fields = BTreeMap::<String, String>::new();
    let mut number = |key: &str, value: f64| {
        fields.insert(key.into(), general(value));
    };
    for (key, value) in [
        ("diameter", dims.diameter),
        ("height", dims.height),
        ("bore", dims.guide_bore),
        ("rod", dims.bench_guide),
        ("magnet_od_mm_g", design.magnet.od_mm),
        ("magnet_id_mm_g", design.magnet.id_mm),
        ("magnet_thickness_mm_g", design.magnet.thickness_mm),
        ("dims_magnet_midplane_g", dims.magnet_midplane),
        ("recipe_nozzle_c", recipe.nozzle_c),
        ("recipe_bed_c", recipe.bed_c),
        ("recipe_chamber_c", recipe.chamber_c),
        ("recipe_flow_ratio_g", recipe.flow_ratio),
        ("layer", recipe.layer_height_mm),
        ("recipe_line_width_mm_g", recipe.line_width_mm),
        ("dims_magnet_seat_g", dims.magnet_seat),
        ("dims_pocket_roof_g", dims.pocket_roof),
        (
            "last_open",
            design.print_intent.pause_before_layer_z_mm - recipe.layer_height_mm,
        ),
        ("first_cover", design.print_intent.pause_before_layer_z_mm),
        (
            "integration_rod_axis_from_inside_wall_mm_g",
            integration.rod_axis_from_inside_wall_mm,
        ),
        ("dims_guide_radial_clearance_g", dims.guide_radial_clearance),
        (
            "integration_carbonator_upright_wall_clearance_range_mm_0_g",
            integration.carbonator_upright_wall_clearance_range_mm[0],
        ),
        (
            "integration_carbonator_upright_wall_clearance_range_mm_1_g",
            integration.carbonator_upright_wall_clearance_range_mm[1],
        ),
        (
            "res_rod_clearance",
            hsm_reservoir_numbers::rod_end_clearance(),
        ),
    ] {
        number(key, value);
    }
    fields.extend([
        (
            "dims_pocket_depth_p2f".into(),
            format!("{:.2}", dims.pocket_depth),
        ),
        (
            "preflight_requested_z_trim_mm_p2f".into(),
            format!("{:.2}", preflight.requested_z_trim_mm),
        ),
        ("design_cad_revision".into(), escape(&design.cad_revision)),
        (
            "mapping_external_slot".into(),
            preflight.material_mapping.external_slot.to_string(),
        ),
        (
            "mapping_nozzle".into(),
            escape(&preflight.material_mapping.nozzle),
        ),
        ("recipe_wall_loops".into(), recipe.wall_loops.to_string()),
        (
            "pause_layer".into(),
            observations
                .next_trial
                .expected_pause_before_layer
                .to_string(),
        ),
        (
            "carb_rod".into(),
            format!(
                "{:.3} ±{:.3} in ({:.2} ±{:.2} mm)",
                rod.finished_length,
                rod.length_tolerance,
                rod.finished_length * 25.4,
                rod.length_tolerance * 25.4
            ),
        ),
        (
            "res_rod".into(),
            format!("{:.3} mm", hsm_reservoir_numbers::rod_length()),
        ),
        (
            "integration_maximum_float_edge_to_reed_center_mm_carbonator_p3f".into(),
            format!(
                "{:.3}",
                integration.maximum_float_edge_to_reed_center_mm.carbonator
            ),
        ),
        (
            "integration_maximum_float_edge_to_reed_center_mm_reservoir_p3f".into(),
            format!(
                "{:.3}",
                integration.maximum_float_edge_to_reed_center_mm.reservoir
            ),
        ),
        (
            "task_id".into(),
            escape(&observations.paused_print_result.task_id),
        ),
        (
            "minutes".into(),
            (preflight.native_slice_summary.estimated_time_s / 60.)
                .round_ties_even()
                .to_string(),
        ),
        ("magnet_source".into(), escape(&design.magnet.source)),
    ]);
    let dest = output.unwrap_or(&guide);
    let mut templates: Vec<PathBuf> = std::fs::read_dir(guide.join("templates"))?
        .filter_map(|e| e.ok().map(|e| e.path()))
        .filter(|p| {
            p.file_name()
                .unwrap()
                .to_string_lossy()
                .ends_with(".html.in")
        })
        .collect();
    templates.sort();
    let mut pages = Vec::new();
    for template in &templates {
        let mut text = std::fs::read_to_string(template)?;
        for (key, value) in &fields {
            text = text.replace(&format!("{{{{{key}}}}}"), value);
        }
        ensure!(
            !text.contains("{{"),
            "unresolved field in {}",
            template.display()
        );
        let name = template
            .file_name()
            .unwrap()
            .to_string_lossy()
            .trim_end_matches(".in")
            .to_owned();
        crate::write(&dest.join(&name), text.as_bytes())?;
        pages.push(name);
    }
    let mut sources = BTreeMap::new();
    for path in templates.into_iter().chain([
        float.join("design.json"),
        float.join("physical-observations.json"),
        float.join("integration-check.json"),
        float.join("mark2-print/v1/float-preflight.json"),
        root.join("tools/hsm/manual-guides/src/float.rs"),
        root.join("hardware/printed-parts/cold-core/reservoir/numbers.rs"),
        root.join("tools/hsm/cold-core-data/src/lib.rs"),
        root.join("tools/magnetic-float-guide/build-recipe-sources.json"),
    ]) {
        sources.insert(
            path.strip_prefix(root)?.to_string_lossy().into_owned(),
            crate::sha(&path)?,
        );
    }
    crate::write_json(
        &dest.join("guide-inputs.json"),
        &json!({"purpose":"Record current float design and evidence used by the authored guide.", "title":"ASA Aero magnetic float build guide","current_cad_revision":design.cad_revision,"current_native_slice_state":"review_pending","pages":pages,"recipe_sources":"../../tools/magnetic-float-guide/build-recipe-sources.json","inputs_sha256":sources}),
    )?;
    println!("{}: {} authored pages", dest.display(), pages.len());
    Ok(())
}
