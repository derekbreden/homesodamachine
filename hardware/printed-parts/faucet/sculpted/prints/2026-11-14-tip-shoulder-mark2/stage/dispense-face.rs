//! Transfer the crown of the dispense face to the cover along the rounded trial seam.
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
const STRAIGHT_HALF_SPAN: f64 = 5.0;
const CORNER_RADIUS: f64 = 1.25;
const SEAM_CLEARANCE: f64 = 0.16;
const COVER_FACE_THICKNESS: f64 = 1.45;
const CROWN_BACKING_REACH: f64 = 0.95;
const CUT_OVERRUN: f64 = 0.08;
const PROFILE_REACH: f64 = 15.0;

fn cut_profile() -> Result<Profile> {
    let centre = v2(STRAIGHT_HALF_SPAN, SEAM_HEIGHT + CORNER_RADIUS);
    let tangent = std::f64::consts::FRAC_PI_4;
    let foot = v2(STRAIGHT_HALF_SPAN, SEAM_HEIGHT);
    let rise = centre + v2(tangent.sin(), -tangent.cos()) * CORNER_RADIUS;
    let side = v2(PROFILE_REACH, rise.y + (PROFILE_REACH - rise.x));
    let left = |p: V2| v2(-p.x, p.y);
    Ok(Profile::new(Loop::new(vec![
        Seg::Line { a: left(foot), b: foot },
        Seg::Arc { a: foot, b: rise, c: centre, ccw: true },
        Seg::Line { a: rise, b: side },
        Seg::Line { a: side, b: left(side) },
        Seg::Line { a: left(side), b: left(rise) },
        Seg::Arc { a: left(rise), b: left(foot), c: left(centre), ccw: true },
    ])?))
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

    let profile = cut_profile()?;
    let mouth = Plane::XZ.at(v3(0.0, DISPENSE_FACE_THICKNESS + CUT_OVERRUN, 0.0));
    let tip_cut = mouth.extrude(&profile, DISPENSE_FACE_THICKNESS + 2.0 * CUT_OVERRUN)?;
    let remaining_tip = tip.cut(&tip_cut)?;
    let front = Plane::XZ.at(v3(0.0, COVER_FACE_THICKNESS, 0.0));
    let tongue = front.extrude(&profile.offset(-SEAM_CLEARANCE, false)?, COVER_FACE_THICKNESS)?;
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
                .max(moved.intersect(&display_stock.translate(shift))?.volume());
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

    let measured = removed.bounds();
    let report = json!({
        "purpose": "Records the matching rounded transfer on the dispense face.",
        "seam_n_mm": SEAM_HEIGHT,
        "central_straight_span_mm": 2.0 * STRAIGHT_HALF_SPAN,
        "corner_radius_mm": CORNER_RADIUS,
        "nominal_seam_clearance_mm": SEAM_CLEARANCE,
        "cover_face_axial_thickness_mm": COVER_FACE_THICKNESS,
        "removed_tip_stock_mm3": removed.volume(),
        "removed_tip_bounds_x_s_n_mm": [
            [measured.min.x, measured.min.y, measured.min.z],
            [measured.max.x, measured.max.y, measured.max.z]
        ],
        "added_cover_stock_mm3": added.volume(),
        "tongue_bond_to_original_cover_mm3": tongue.intersect(&cover)?.volume(),
        "max_added_stock_overlap_along_nominal_installation_mm3": installation_overlap,
        "scope": "Nominal geometric seating and assembly path. Snap force, finish and seating are physical observations.",
    });
    std::fs::write(dir.join("dispense-face.json"), format!("{}\n", serde_json::to_string_pretty(&report)?))?;
    println!("{}", dir.join("dispense-face.json").display());
    Ok(())
}
