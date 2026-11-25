//! Open Pisco coupons compare the existing wing-foot bearing width and the backed retaining shoulder.
use super::{
    ENTRY_DEPTH, FILLER_CONTACT_TRAVEL, FREE_TIP_BIAS, Hook, LENGTH, NOSE_LENGTH, Section,
    WIDE_POST_HALF_WIDTH, print_part,
};
use anyhow::{Result, ensure};
use hsm_kernel::{Affine, Solid, V3, v3};
use serde_json::{Map, json};
use std::{fs, path::Path};

const DOT_RADIUS: f64 = 1.00;
const DOT_DEPTH: f64 = 0.60;
const DOT_PITCH: f64 = 3.40;
const BACK_MARK_R: f64 = 7.80;

/// One to three shallow hollows on the outside of the saddle back or the thick receiver flange.
fn numbered(stock: &Solid, count: usize, center: V3, outside: V3) -> Result<Solid> {
    let mut dots = Vec::new();
    for i in 0..count {
        let dy = (i as f64 - (count - 1) as f64 / 2.) * DOT_PITCH;
        let tip = center + V3::Y * dy - outside * DOT_DEPTH;
        let height = DOT_DEPTH + 0.15;
        dots.push(Solid::cone(
            tip,
            outside,
            0.,
            DOT_RADIUS * height / DOT_DEPTH,
            height,
        )?);
    }
    stock.cut_all(&dots)
}

pub(super) fn write(
    dir: &Path,
    s: &Section,
    original: &Solid,
    trimmed: &Solid,
    post: &Solid,
    wide: Hook,
    receiver_pose: Affine,
    cover_pose: Affine,
) -> Result<()> {
    fs::create_dir_all(dir)?;
    let back_mark = v3(s.axis + BACK_MARK_R, s.y, original.bounds().min.z);
    let flange_mark = v3(trimmed.bounds().max.x, s.y, s.back_z - s.roof_h / 2.);
    let pairs = [(2.00, 0.), (2.60, 0.), (2.60, -0.12)];
    let lip_h = s.roof_h + ENTRY_DEPTH + NOSE_LENGTH + wide.lip_r - wide.nose_r;
    let angle = s.free_angle(s.roof_h, lip_h, FREE_TIP_BIAS);
    let mut settings = Vec::new();
    let mut parts = Map::new();
    for (index, (land, shoulder_offset)) in pairs.into_iter().enumerate() {
        let n = index + 1;
        let hook = Hook {
            crest_inner_r: s.outer_r - land,
            ..wide
        };
        let receiver = numbered(
            &s.receiver(trimmed, post, hook, shoulder_offset)?,
            n,
            flange_mark,
            V3::X,
        )?;
        let free = s.wide_cover(original, hook, FREE_TIP_BIAS, true)?;
        let cover = numbered(&free, n, back_mark, -V3::Z)?;
        let straight = s
            .wide_cover(original, hook, 0., true)?
            .translate(V3::Z * FILLER_CONTACT_TRAVEL);
        let overlap = receiver.shared_volume(&straight)?;
        ensure!(
            overlap < 1e-5 && straight.gap_within(post, 1.)? < 1e-5,
            "pair {n}: the flat feet and center saddle must reach their seats ({overlap} mm³ interference)"
        );
        for (kind, solid, pose) in [
            ("cover", &cover, cover_pose),
            ("receiver", &receiver, receiver_pose),
        ] {
            let name = format!("{kind}-{n}");
            parts.insert(name.clone(), print_part(dir, &name, solid, pose)?);
        }
        settings.push(json!({"number":n, "crest_land_width_mm":land, "retaining_shoulder_offset_mm":shoulder_offset,
            "free_crest_angle_to_roof_deg":angle.to_degrees(),"free_outer_edge_closer_to_roof_mm":land*angle.sin(),
            "straight_seated_overlap_mm3":overlap}));
    }
    let geometry = json!({
        "purpose":"Register the six numbered open coupons to the scanned Pisco section and locate the exterior identification dots.",
        "assembly_frame":"r is distance from the regulator axis. h is height above the receiver back face. The seated cover moves +Z from its nominal machine pose.",
        "axis_x_mm":s.axis,"axis_y_mm":s.y,"back_face_z_mm":s.back_z,"cover_seating_travel_mm":FILLER_CONTACT_TRAVEL,
        "section_length_mm":LENGTH,"roof_h_mm":s.roof_h,"join_h_mm":s.join_h,"free_tip_bias_each_mm":FREE_TIP_BIAS,
        "spring_wall_thickness_mm":s.outer_r-s.inner_r,"centered_hook_capture_mm":wide.lip_r-wide.nose_r,
        "centered_post_width_mm":2.*WIDE_POST_HALF_WIDTH,"post_apex_h_mm":s.back_z-post.bounds().min.z,
        "marks":{"form":"Blind conical recesses spaced along Y on the solid saddle back and receiver flange.",
            "opening_diameter_mm":2.*DOT_RADIUS,"depth_mm":DOT_DEPTH,"pitch_mm":DOT_PITCH,
            "cover_group_center_machine_mm":back_mark.to_array(),"receiver_group_center_machine_mm":flange_mark.to_array()},
        "pairs":settings,"parts":parts
    });
    fs::write(
        dir.join("geometry.json"),
        format!("{}\n", serde_json::to_string_pretty(&geometry)?),
    )?;
    Ok(())
}
