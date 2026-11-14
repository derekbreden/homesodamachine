//! The print trial adds a short backing to each leading display-pocket corner of the rigid tip.
use anyhow::{Result, ensure};
use hsm_kernel::{Body, Plane, Profile, Solid, V3, import, part, v2, v3};
use hsm_sandbox::{out, part as exported};
use serde_json::json;

const OUTLET_Y: f64 = -133.99672200476698;
const OUTLET_Z: f64 = 180.38874339162197;
const TIP_TURN: f64 = 140.0;
const NECK_CENTER_N: f64 = 4.027512922;
const SHOULDER_RADIUS: f64 = 13.38;
const SHOULDER_INNER_X: f64 = 10.85;
const SHOULDER_WIDTH: f64 = 3.0;
const SHOULDER_START: f64 = 1.55;
const SHOULDER_TAPER: f64 = 3.10;
const SHOULDER_END: f64 = 7.40;
const SHOULDER_ROOT_N: f64 = 7.70;
const SHOULDER_TOP_N: f64 = 10.05;
const TIP: &str = "printed-parts/faucet/faucet-shell/faucet-shell-tip.step";
const COVER: &str = "printed-parts/faucet/faucet-display-cover/faucet-display-cover-seated.step";

fn shoulders() -> Result<Solid> {
    let flank = Plane::YZ.at(v3(SHOULDER_INNER_X, 0.0, 0.0));
    let outline = Profile::polygon(&[
        v2(SHOULDER_START, SHOULDER_ROOT_N),
        v2(SHOULDER_END, SHOULDER_ROOT_N),
        v2(SHOULDER_TAPER, SHOULDER_TOP_N),
        v2(SHOULDER_START, SHOULDER_TOP_N),
    ]);
    let right = flank.extrude(&outline, SHOULDER_WIDTH)?;
    let envelope = Solid::cylinder(
        v3(0.0, SHOULDER_START - 0.3, NECK_CENTER_N),
        V3::Y,
        SHOULDER_RADIUS,
        SHOULDER_END - SHOULDER_START + 0.6,
    )?;
    let right = right.intersect(&envelope)?;
    right.union(&right.mirror(V3::ZERO, V3::X))
}

fn main() -> Result<()> {
    let dir = out()?;
    let (sin, cos) = TIP_TURN.to_radians().sin_cos();
    let frame = Plane::new(v3(0.0, OUTLET_Y, OUTLET_Z), V3::X, v3(0.0, cos, sin))?;
    let into_tip_frame = |solid: &Solid| solid.placed(&frame, &Plane::XY);
    let tip_export = exported(TIP)?;
    let cover_export = exported(COVER)?;
    let tip = into_tip_frame(import::body(&tip_export, "faucet-shell-tip")?);
    let cover = into_tip_frame(import::body(&cover_export, "faucet-display-cover-seated")?);
    let assembly = exported("faucet-layout/faucet-assembly.step")?;
    let display = into_tip_frame(import::body(&assembly, "faucet_display")?);
    let shoulders = shoulders()?;
    let added = shoulders.cut(&tip)?;
    let candidate = tip.union(&shoulders)?;
    ensure!(candidate.components().len() == 1, "the trial tip is not one solid");
    ensure!(!added.is_empty() && added.components().len() == 2, "the trial must add both shoulders");

    let stock_world = candidate.placed(&Plane::XY, &frame);
    let added_world = added.placed(&Plane::XY, &frame);
    part::write_part(&dir, "tip-trial", &[Body { name: "tip-trial", color: tip_export[0].color, solid: &stock_world }])?;
    part::write_part(&dir, "added-shoulders", &[Body { name: "added-shoulders", color: None, solid: &added_world }])?;

    let mut samples = Vec::new();
    for step in 0..=32 {
        let n = f64::from(step) / 4.0;
        samples.push([0.0, n]);
    }
    for step in 1..=32 {
        samples.push([-f64::from(step) / 2.0, 8.0]);
    }
    let mut cover_overlap: f64 = 0.0;
    let mut display_overlap: f64 = 0.0;
    for [s, n] in &samples {
        let shift = v3(0.0, *s, *n);
        cover_overlap = cover_overlap.max(added.intersect(&cover.translate(shift))?.volume());
        display_overlap = display_overlap.max(added.intersect(&display.translate(shift))?.volume());
    }
    ensure!(cover_overlap < 1e-5 && display_overlap < 1e-5, "added stock intersects the sampled installation path");
    let bounds = added.bounds();
    let report = json!({
        "tip_frame": {"origin_xyz_mm": [0.0, OUTLET_Y, OUTLET_Z], "turn_degrees": TIP_TURN},
        "approved_tip_volume_mm3": tip.volume(),
        "trial_tip_volume_mm3": candidate.volume(),
        "added_volume_mm3": added.volume(),
        "added_bounds_x_s_n_mm": [[bounds.min.x, bounds.min.y, bounds.min.z], [bounds.max.x, bounds.max.y, bounds.max.z]],
        "removed_volume_mm3": tip.cut(&candidate)?.volume(),
        "sampled_assembly_translations_s_n_mm": samples,
        "max_added_intersection_with_seated_cover_mm3": cover_overlap,
        "max_added_intersection_with_display_mm3": display_overlap,
    });
    std::fs::write(dir.join("dispense-face-review.json"), format!("{}\n", serde_json::to_string_pretty(&report)?))?;
    println!("{}", dir.join("tip-trial.stl").display());
    Ok(())
}
