//! Transfer the full crown of the dispense face along a chord with tangent end fillets.
use anyhow::{ensure, Result};
use hsm_faucet::{display, Gooseneck};
use hsm_faucet_display_cover_numbers as cover_numbers;
use hsm_faucet_numbers::shell::{
    DISPENSE_FACE_THICKNESS, TUBE_SHELL_CENTER_Y, TUBE_SHELL_OUTER_R,
};
use hsm_kernel::*;
use serde_json::json;
use std::path::{Path, PathBuf};

const SEAM_HEIGHT: f64 = 15.0;
const CORNER_RADIUS: f64 = 1.25;
const SEAM_CLEARANCE: f64 = 0.16;
const COVER_FACE_THICKNESS: f64 = 1.45;
const CROWN_BACKING_REACH: f64 = 0.95;
const CUT_OVERRUN: f64 = 0.08;
const PROFILE_REACH: f64 = 15.0;
const WING_OVERLAP_REACH: f64 = 0.34;

struct Seam {
    flat: V2,
    centre: V2,
    on_circle: V2,
}

impl Seam {
    // A centre offset in from both the chord and the round makes the blend tangent to both.
    fn chord(height: f64, circle_radius: f64) -> Self {
        let circle = v2(0.0, TUBE_SHELL_CENTER_Y);
        let fillet_offset = height - CORNER_RADIUS - circle.y;
        let centre_distance = circle_radius - CORNER_RADIUS;
        let half_span = (centre_distance.powi(2) - fillet_offset.powi(2)).sqrt();
        let centre = v2(half_span, height - CORNER_RADIUS);
        let on_circle = circle + (centre - circle) * (circle_radius / centre_distance);
        Self { flat: v2(half_span, height), centre, on_circle }
    }

    fn cap(&self, reach: f64) -> Result<Profile> {
        let Self { flat, centre, on_circle } = *self;
        let radius = on_circle - centre;
        // Continue outside the round so the cut does not run along its curved surface.
        let tangent = v2(reach, on_circle.y - (reach - on_circle.x) * radius.x / radius.y);
        let corner = v2(reach, TUBE_SHELL_CENTER_Y + TUBE_SHELL_OUTER_R + 2.0 * CROWN_BACKING_REACH);
        let left = |p: V2| v2(-p.x, p.y);
        Ok(Profile::new(Loop::new(vec![
            Seg::Line { a: left(flat), b: flat },
            Seg::Arc { a: flat, b: on_circle, c: centre, ccw: false },
            Seg::Line { a: on_circle, b: tangent },
            Seg::Line { a: tangent, b: corner },
            Seg::Line { a: corner, b: left(corner) },
            Seg::Line { a: left(corner), b: left(tangent) },
            Seg::Line { a: left(tangent), b: left(on_circle) },
            Seg::Arc { a: left(on_circle), b: left(flat), c: left(centre), ccw: false },
        ])?))
    }
}

fn load(path: &str, name: &str) -> Result<Solid> {
    let bodies = import::model(Path::new("hardware").join(path))?;
    import::body(&bodies, name).cloned()
}

fn write(dir: &Path, name: &str, color: [f64; 3], stock: &Solid) -> Result<()> {
    part::write_part(dir, name, &[Body { name, color: Some(color), solid: stock }])?;
    Ok(())
}

fn main() -> Result<()> {
    let dir = PathBuf::from(std::env::args_os().nth(1).expect("output directory"));
    std::fs::create_dir_all(&dir)?;
    let neck = Gooseneck::shell();
    let frame = display::tip_plane(&neck)?;
    let local = |solid: &Solid| solid.placed(&frame, &Plane::XY);
    let world = |solid: &Solid| solid.placed(&Plane::XY, &frame);
    let tip = local(&load(
        "printed-parts/faucet/faucet-shell/faucet-shell-tip.step.npz",
        "faucet-shell-tip",
    )?);
    let cover = local(&load(
        "printed-parts/faucet/faucet-display-cover/faucet-display-cover-seated.step.npz",
        "faucet-display-cover-seated",
    )?);
    let display_stock = local(&load("faucet-layout/faucet-assembly.step.npz", "faucet_display")?);

    let tip_seam = Seam::chord(SEAM_HEIGHT, TUBE_SHELL_OUTER_R);
    let cover_seam = Seam::chord(SEAM_HEIGHT + SEAM_CLEARANCE, cover_numbers::neck_clearance_r());
    let mouth = Plane::XZ.at(v3(0.0, DISPENSE_FACE_THICKNESS + CUT_OVERRUN, 0.0));
    let tip_cut = mouth.extrude(&tip_seam.cap(PROFILE_REACH)?, DISPENSE_FACE_THICKNESS + 2.0 * CUT_OVERRUN)?;
    let remaining_tip = tip.cut(&tip_cut)?;
    let front = Plane::XZ.at(v3(0.0, COVER_FACE_THICKNESS, 0.0));
    let tongue = front.extrude(&cover_seam.cap(cover_seam.on_circle.x + WING_OVERLAP_REACH)?, COVER_FACE_THICKNESS)?;
    let crown = Solid::cylinder(
        v3(0.0, -CUT_OVERRUN, TUBE_SHELL_CENTER_Y),
        V3::Y,
        TUBE_SHELL_OUTER_R + CROWN_BACKING_REACH,
        COVER_FACE_THICKNESS + 2.0 * CUT_OVERRUN,
    )?;
    let tongue = tongue.intersect(&crown)?;
    let seated = cover.union(&tongue)?;
    let relaxed = display::relaxed_by(
        &neck, &world(&seated), cover_numbers::BEZEL_N_BOTTOM, cover_numbers::wing_inward,
    )?;
    ensure!(remaining_tip.components().len() == 1 && seated.components().len() == 1
        && relaxed.components().len() == 1, "both trial pieces must remain single solids");

    let added = seated.cut(&cover)?;
    let removed = tip.cut(&remaining_tip)?;
    ensure!(added.volume() > 1.0 && removed.volume() > 1.0, "missing face transfer");
    let mut installation_overlap: f64 = 0.0;
    for step in 0..=16 {
        let reach = f64::from(step) * 0.5;
        let seated_path = [v3(0.0, 0.0, reach), v3(0.0, -2.0 * reach, 8.0)];
        for shift in seated_path {
            let moved = added.translate(shift);
            installation_overlap = installation_overlap
                .max(moved.intersect(&remaining_tip)?.volume())
                .max(moved.intersect(&display_stock)?.volume());
        }
    }
    ensure!(installation_overlap < 1e-4, "the added tab collides along the nominal seat path: {installation_overlap}");
    let tip_world = world(&remaining_tip);
    let cover_world = world(&seated);
    write(&dir, "tip", [0.25, 0.26, 0.28], &tip_world)?;
    write(&dir, "cover", [0.25, 0.26, 0.28], &relaxed)?;
    write(&dir, "cover-seated", [0.50, 0.30, 0.12], &cover_world)?;
    let view = Solid::cuboid(v3(-18.0, -0.05, -14.0), v3(18.0, 24.0, 25.0));
    let clipped_tip = world(&remaining_tip.intersect(&view)?);
    let clipped_cover = world(&seated.intersect(&view)?);
    part::write_shown(&dir, "dispense-face", &[
        Body { name: "tip", color: Some([0.25, 0.26, 0.28]), solid: &clipped_tip },
        Body { name: "cover", color: Some([0.35, 0.53, 0.67]), solid: &clipped_cover },
    ])?;

    let report = json!({
        "purpose": "Records the full-width chord and its tangent blends into the circular dispense face.",
        "seam_n_mm": SEAM_HEIGHT,
        "tip_straight_span_mm": 2.0 * tip_seam.flat.x,
        "cover_straight_span_mm": 2.0 * cover_seam.flat.x,
        "tip_right_tangency_x_n_mm": [tip_seam.on_circle.x, tip_seam.on_circle.y],
        "cover_right_tangency_x_n_mm": [cover_seam.on_circle.x, cover_seam.on_circle.y],
        "corner_radius_mm": CORNER_RADIUS,
        "nominal_seam_clearance_mm": SEAM_CLEARANCE,
        "cover_face_axial_thickness_mm": COVER_FACE_THICKNESS,
        "removed_tip_stock_mm3": removed.volume(),
        "added_cover_stock_mm3": added.volume(),
        "tongue_bond_to_original_cover_mm3": tongue.intersect(&cover)?.volume(),
        "max_added_stock_overlap_along_nominal_installation_mm3": installation_overlap,
        "scope": "Nominal geometric seating and assembly path. Snap force, finish and seating are physical observations.",
    });
    std::fs::write(dir.join("dispense-face.json"), format!("{}\n", serde_json::to_string_pretty(&report)?))?;
    println!("{}", dir.join("dispense-face.json").display());
    Ok(())
}
