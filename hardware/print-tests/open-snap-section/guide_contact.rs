//! Three full-depth guide faces approach the filmed two-dot wing in its loaded position.
use super::{
    DOT_DEPTH, DOT_PITCH, DOT_RADIUS, ENTRY_DEPTH, FILLER_CONTACT_TRAVEL, FREE_TIP_BIAS, Hook,
    LENGTH, NOSE_LENGTH, RUNNING_GAP, Section, TWO_DOT, WIDE_POST_HALF_WIDTH, numbered, print_part,
};
use anyhow::Result;
use hsm_kernel::{Affine, Solid, V2, V3, v2};
use serde_json::{Map, json};
use std::{fs, path::Path};

// Measured outward tip travel after straightening at the accepted two-dot shoulder and printed roof.
const LOADED_TIP: f64 = 0.19645;
const PARALLEL_START: f64 = 2.00;
const PARALLEL_END: f64 = 6.00;

fn diagonal(s: &Section, hook: Hook, at_toe: f64, at_nose: f64) -> Vec<(f64, f64)> {
    vec![
        (hook.crest_inner_r - RUNNING_GAP + at_toe, s.roof_h),
        (hook.nose_r - RUNNING_GAP + at_nose, s.roof_h + ENTRY_DEPTH),
    ]
}

/// The seated guide on the two-dot pair Derek liked in C036.
pub(super) fn tight_diagonal(s: &Section, hook: Hook) -> Vec<(f64, f64)> {
    diagonal(s, hook, 0.402, 0.344)
}

fn parallel_faces(s: &Section, hook: Hook, lip_h: f64) -> (Vec<V2>, Vec<(f64, f64)>) {
    let start = s.roof_h + PARALLEL_START;
    let end = s.roof_h + PARALLEL_END;
    let half_rise = s.free_angle(s.roof_h, lip_h, LOADED_TIP).tan() * (end - start) * 0.5;
    let cover_r = hook.nose_r + 0.060;
    let wall_r = hook.nose_r + 0.215;
    let cover = vec![v2(cover_r - half_rise, start), v2(cover_r + half_rise, end)];
    let receiver = vec![
        (hook.crest_inner_r - 0.10, s.roof_h),
        (wall_r, start - 0.10),
        (wall_r, end - 0.05),
        (hook.nose_r + 0.02, s.roof_h + ENTRY_DEPTH),
    ];
    (cover, receiver)
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
    back_mark: V3,
    flange_mark: V3,
) -> Result<()> {
    fs::create_dir_all(dir)?;
    let hook = Hook {
        crest_inner_r: s.outer_r - TWO_DOT.foot_width,
        ..wide
    };
    let lip_h = s.roof_h + ENTRY_DEPTH + NOSE_LENGTH + hook.lip_r - hook.nose_r;
    let angle = s.free_angle(s.roof_h, lip_h, FREE_TIP_BIAS);
    let (parallel_cover, parallel_receiver) = parallel_faces(s, hook, lip_h);
    let profiles = [
        ("close running fit", vec![], diagonal(s, hook, 0.294, 0.236)),
        (
            "contact at the diagonal course edges",
            vec![],
            tight_diagonal(s, hook),
        ),
        ("parallel bearing", parallel_cover, parallel_receiver),
    ];
    let mut parts = Map::new();
    let mut pairs = Vec::new();
    for (index, (fit, cover_guide, receiver_guide)) in profiles.into_iter().enumerate() {
        let n = index + 1;
        let free = s.cover_with_profile(original, hook, FREE_TIP_BIAS, true, &cover_guide)?;
        let cover = numbered(&free, n, back_mark, -V3::Z)?;
        let receiver = numbered(
            &s.receiver_with_profile(trimmed, post, hook, 0., &receiver_guide)?,
            n,
            flange_mark,
            V3::X,
        )?;
        for (kind, body, pose) in [
            ("cover", &cover, cover_pose),
            ("receiver", &receiver, receiver_pose),
        ] {
            let name = format!("{kind}-{n}");
            parts.insert(name.clone(), print_part(dir, &name, body, pose)?);
        }
        pairs.push(json!({"number":n, "guide_design":fit,"crest_land_width_mm":TWO_DOT.foot_width,
            "retaining_shoulder_offset_mm":0., "free_crest_angle_to_roof_deg":angle.to_degrees(),
            "free_outer_edge_closer_to_roof_mm":TWO_DOT.foot_width*angle.sin(),
            "receiver_guide_r_h_mm":receiver_guide,
            "cover_intermediate_straight_guide_r_h_mm":cover_guide.iter().map(|p| [p.x,p.y]).collect::<Vec<_>>()}));
    }
    let data = json!({"purpose":"Register the three guide-contact pairs and their full-depth running faces to the filmed two-dot receiver.",
        "frame":"r is outward from the Pisco centerline. h is height from the flat receiver back. Each cover closes toward machine +Z.",
        "axis_x_mm":s.axis,"axis_y_mm":s.y,"back_face_z_mm":s.back_z,"cover_seating_travel_mm":FILLER_CONTACT_TRAVEL,
        "section_length_mm":LENGTH,"roof_h_mm":s.roof_h,"join_h_mm":s.join_h,
        "free_tip_bias_each_mm":FREE_TIP_BIAS,"two_dot_additional_loaded_tip_travel_mm":LOADED_TIP,
        "spring_wall_thickness_mm":s.outer_r-s.inner_r,"centered_hook_capture_mm":wide.lip_r-wide.nose_r,
        "centered_post_width_mm":2.*WIDE_POST_HALF_WIDTH,"post_apex_h_mm":s.back_z-post.bounds().min.z,
        "marks":{"form":"Recessed conical dots in the solid saddle back and receiver flange.",
            "opening_diameter_mm":2.*DOT_RADIUS,"depth_mm":DOT_DEPTH,"pitch_mm":DOT_PITCH,
            "cover_group_center_machine_mm":back_mark.to_array(),"receiver_group_center_machine_mm":flange_mark.to_array()},
        "pairs":pairs,"parts":parts});
    fs::write(
        dir.join("geometry.json"),
        format!("{}\n", serde_json::to_string_pretty(&data)?),
    )?;
    Ok(())
}
