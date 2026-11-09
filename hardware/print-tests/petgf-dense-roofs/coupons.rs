// coupons.rs makes labeled open-front ceilings for the PET-GF interface-density comparison.
use anyhow::Result;
use hsm_kernel::{Body, Font, HAlign, Kind, Plane, Profile, VAlign, v2, v3};
use serde_json::json;

const WIDTH: f64 = 24.;
const DEPTH: f64 = 24.;
const WALL: f64 = 1.68;
const FIRST_LAYER: f64 = 0.20;
const LAYER: f64 = 0.24;
const CEILING_COURSES: f64 = 22.;
const ROOF_COURSES: f64 = 8.;
const LABEL_COURSES: f64 = 2.;

fn main() -> Result<()> {
    let dir = hsm_sandbox::out()?;
    let ceiling = FIRST_LAYER + CEILING_COURSES * LAYER;
    let roof_thickness = ROOF_COURSES * LAYER;
    let top = ceiling + roof_thickness;
    let total = top + LABEL_COURSES * LAYER;
    let font = Font::find("Helvetica Neue", Kind::Bold)?;
    let mut specimens = Vec::new();
    for (id, spacing, x) in [("A", 0.50, 126.), ("B", 0.15, 160.), ("C", 0., 194.)] {
        let stock = Plane::XY.extrude(&Profile::rect(v2(0., 0.), WIDTH, DEPTH), top)?;
        let cavity = Plane::XY.extrude(
            &Profile::rect(v2(0., -WALL / 2. - 0.5), WIDTH - 2. * WALL, DEPTH - WALL + 1.),
            ceiling,
        )?;
        let roof = stock.cut(&cavity)?;
        let label = Plane::XY.text(&font, id, 4., LABEL_COURSES * LAYER + 0.05,
            HAlign::Center, VAlign::Center)?.translate(v3(0., 6., top - 0.05));
        let roof = roof.union(&label)?;
        let name = format!("roof-{id}");
        let written = hsm_kernel::part::write_part(&dir, &name,
            &[Body { name: &name, color: None, solid: &roof }])?;
        specimens.push(json!({"id":id,"interface_spacing_mm":spacing,
            "position_mm":[x,165.,total/2.],"geometry":written}));
    }
    let recipe = json!({"purpose":"Compare support-roof density while holding the PET-GF process and planned Z gap constant.",
        "profile":"hardware/printed-parts/petgf.3mf","printer":"Mark1","connection_key":"H2C",
        "nozzle":"left hardened Standard","nozzle_diameter_mm":0.4,"material":"Polymaker Fiberon PET-GF15",
        "plate":"Textured PEI Plate","z_trim_mm":0.18,"requested_top_z_distance_mm":0.45,
        "interface_layers":2,"interface_pattern":"auto","width_mm":WIDTH,"depth_mm":DEPTH,
        "wall_mm":WALL,"ceiling_bottom_mm":ceiling,"roof_thickness_mm":roof_thickness,
        "label_height_mm":LABEL_COURSES*LAYER,"total_height_mm":total,"layer_height_mm":LAYER,
        "first_layer_mm":FIRST_LAYER,"specimens":specimens});
    std::fs::write(dir.join("geometry.json"), serde_json::to_vec_pretty(&recipe)?)?;
    println!("{}", dir.join("geometry.json").display());
    Ok(())
}
