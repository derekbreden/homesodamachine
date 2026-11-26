//! Guide the long cap into its two axial end stops while leaving the seated bearing planes in place.
use super::number;
use anyhow::{Context, Result};
use hsm_kernel::{Plane, Profile, Solid, V3, reads, v2, v3};
use serde_json::{Value, json};

const LEAD_Y: f64 = 0.80;
const LEAD_Z: f64 = 1.25;

/// Give the rigid aluminum shoulder its own supported bearing on the closing side of the cap.
fn outlet_shoulder(
    cover: &Solid,
    axis: f64,
    axis_z: f64,
    axial: &Value,
    reference: &Value,
) -> Result<(Solid, Value)> {
    let lip = number(axial, "new_rigid_outlet_lip_y_mm")?;
    let mouth = reads::json("hardware/manifold-layout/above-core.json")?["rear_plumbing"]["gas_frame"]["translation_mm"][1]
        .as_f64().context("installed regulator inlet station")?;
    let data = reads::json(
        reference["housing_scan"]
            .as_str()
            .context("fitted Pisco exterior")?,
    )?;
    let outline: Vec<[f64; 2]> =
        serde_json::from_value(data["pisco_rvfup_quarter"]["fitted_exterior"]["profile_z_radius_mm"].clone())?;
    let start = lip - 0.10;
    let end = lip + 1.30;
    // The course midpoint plus half a course, less the preceding modeled cap-to-housing Y registration,
    // selects the aft edge of the deposited land during closure against the conical shoulder.
    let registration = 0.118;
    let axial_shift = 0.12 - registration;
    let radial_rise = 0.216;
    let nose_radius = 9.38;
    let half_width = 3.75;
    let relief_start = lip + 0.63;
    let mut stations = vec![start, end, relief_start, lip + 0.12];
    stations.extend(
        outline
            .iter()
            .map(|p| mouth - p[0] - axial_shift)
            .filter(|y| *y > start && *y < end),
    );
    stations.sort_by(f64::total_cmp);
    stations.dedup_by(|a, b| (*a - *b).abs() < 1e-6);
    let mut profile = vec![v2(0., start - 0.02)];
    let mut radii = Vec::new();
    for y in stations {
        let point = mouth - y - axial_shift;
        let pair = outline
            .windows(2)
            .find(|s| s[0][0] <= point && point <= s[1][0])
            .context("outlet shoulder on the scan")?;
        let (a, b) = (pair[0], pair[1]);
        let fitted = a[1] + (b[1] - a[1]) * (point - a[0]) / (b[0] - a[0]);
        let relief = 0.52 * ((y - relief_start) / (end - relief_start)).clamp(0., 1.);
        let radius = (fitted - radial_rise).max(nose_radius) + relief;
        if radii.is_empty() {
            profile.push(v2(radius, start - 0.02));
        }
        profile.push(v2(radius, y));
        radii.push([y, radius]);
    }
    profile.push(v2(radii.last().unwrap()[1], end + 0.02));
    profile.push(v2(0., end + 0.02));
    let clearance = Plane::XY.at(v3(axis, 0., axis_z)).revolve(
        &Profile::polygon(&profile),
        360.,
        v2(0., 0.),
        v2(0., 1.),
    )?;
    let backed = Solid::cuboid(
        v3(axis - half_width, start, cover.bounds().min.z + 0.7),
        v3(axis + half_width, end, axis_z - 5.),
    )
    .cut(&clearance)?;
    let updated = cover.union(&backed)?;
    let record = json!({"rigid_aluminum_shoulder_y_mm":[start,end],"central_chord_width_mm":2.*half_width,
        "radial_rise_from_fitted_shoulder_mm":radial_rise,"free_y_registration_mm":registration,
        "native_half_course_mm":0.12,"minimum_working_radius_mm":nose_radius,"aft_relief_mm":0.52,
        "inner_profile_y_radius_mm":radii,"added_stock_mm3":updated.volume()-cover.volume()});
    Ok((updated, record))
}

pub(super) fn guides(
    cover: Solid,
    receiver: Solid,
    axis: f64,
    axis_z: f64,
    mouth_z: f64,
    axial: &Value,
    reference: &Value,
) -> Result<(Solid, Solid, Value)> {
    let fore = number(axial, "new_wing_forward_stop_y_mm")?;
    let cb = cover.bounds();
    let fore_cut = Plane::YZ.at(v3(axis + 9., 0., 0.)).extrude(
        &Profile::polygon(&[
            v2(fore - LEAD_Y - 0.04, mouth_z - 0.04 * LEAD_Z / LEAD_Y),
            v2(fore + 0.01, mouth_z - 0.04 * LEAD_Z / LEAD_Y),
            v2(fore + 0.01, mouth_z + LEAD_Z + 0.01 * LEAD_Z / LEAD_Y),
        ]),
        cb.max.x - axis - 7.5,
    )?;
    let cut_receiver = receiver.cut_all(&[fore_cut.clone(), fore_cut.mirror(v3(axis, 0., 0.), V3::X)])?;

    // The aft column bears on the outside corner of the rigid tail. The lead ends above its full-width back.
    let top = cover
        .verts()
        .iter()
        .filter(|p| (p.y - cb.max.y).abs() < 1e-5 && p.x > cb.max.x - 1.1)
        .map(|p| p.z)
        .reduce(f64::max)
        .context("entering edge of the rigid tail facing the rear column")?;
    let aft = cb.max.y;
    let aft_cut = Plane::YZ.at(v3(cb.max.x - 3.3, 0., 0.)).extrude(
        &Profile::polygon(&[
            v2(aft + 0.02, top - LEAD_Z - 0.02 * LEAD_Z / LEAD_Y),
            v2(aft + 0.02, top + 0.02),
            v2(aft - LEAD_Y - 0.02 * LEAD_Y / LEAD_Z, top + 0.02),
        ]),
        3.35,
    )?;
    let cut_cover = cover.cut(&aft_cut)?;
    let (located_cover, shoulder) = outlet_shoulder(&cut_cover, axis, axis_z, axial, reference)?;
    let settings = json!({"fore_and_aft_entry_y_relief_mm":LEAD_Y,"entry_rise_z_mm":LEAD_Z,
        "forward_wing_stop_seated_y_mm":fore,"forward_lead_z_mm":[mouth_z,mouth_z+LEAD_Z],
        "rear_tail_stop_seated_y_mm":aft,"rear_tail_lead_z_mm":[top-LEAD_Z,top],
        "solid_tail_height_on_original_aft_plane_mm":top-LEAD_Z-cb.min.z,
        "forward_removed_stock_mm3":receiver.volume()-cut_receiver.volume(),
        "aft_removed_stock_mm3":cover.volume()-cut_cover.volume(), "outlet_shoulder_bearing":shoulder});
    Ok((located_cover, cut_receiver, settings))
}
