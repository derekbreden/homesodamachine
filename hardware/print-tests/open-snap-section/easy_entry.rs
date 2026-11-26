//! Open-ended coupons compare three ways for an unspread wing to start on the receiver mouth.
use super::super::mirrored_bars;
use super::{
    DOT_DEPTH, DOT_PITCH, DOT_RADIUS, ENTRY_DEPTH, FILLER_CONTACT_TRAVEL, FREE_TIP_BIAS, Hook,
    LENGTH, NOSE_LENGTH, Section, TWO_DOT, WIDE_POST_HALF_WIDTH, guide_contact::tight_diagonal,
    numbered, print_part,
};
use anyhow::Result;
use hsm_kernel::{Affine, Solid, V2, V3, v2};
use serde_json::{Map, json};
use std::{fs, path::Path};

const CREST_HEIGHT: f64 = 0.36;
const TOE_BLEND: f64 = 2.40;

struct Entry {
    fit: &'static str,
    pilot_r: f64,
    lip_reduction: f64,
    foot: f64,
}

const PAIRS: [Entry; 3] = [
    Entry {
        fit: "open pilot and shorter retaining lip",
        pilot_r: 10.25,
        lip_reduction: 0.60,
        foot: TWO_DOT.foot_width,
    },
    Entry {
        fit: "open pilot and full retaining lip",
        pilot_r: 10.25,
        lip_reduction: 0.00,
        foot: TWO_DOT.foot_width,
    },
    Entry {
        fit: "wing-side lead-in and full retaining lip",
        pilot_r: 10.80,
        lip_reduction: 0.00,
        foot: 2.00,
    },
];

/// The bevel starts inside the free toe and runs onto solid cheek stock at the existing 45° retaining face.
fn ease_mouth(s: &Section, receiver: &Solid, profile: &[(f64, f64); 3]) -> Result<Solid> {
    let [(crest_r, crest_h), _, (pilot_r, rim_h)] = *profile;
    let outside = s.outer_r + 1.;
    let mut contour = profile.to_vec();
    contour.extend([
        (pilot_r, rim_h + 0.10),
        (outside, rim_h + 0.10),
        (outside, crest_h),
    ]);
    let cutter = contour
        .iter()
        .map(|(r, h)| v2(s.axis + r, s.back_z - h))
        .collect::<Vec<_>>();
    debug_assert!(pilot_r < crest_r);
    receiver.cut_all(&mirrored_bars(&cutter, s.axis, s.y)?)
}

fn guides(s: &Section, control: Hook, hook: Hook) -> (Vec<V2>, Vec<(f64, f64)>) {
    let mut receiver = tight_diagonal(s, control);
    if hook.crest_inner_r == control.crest_inner_r {
        return (vec![], receiver);
    }
    let t = TOE_BLEND / ENTRY_DEPTH;
    let h = s.roof_h + TOE_BLEND;
    let cover_blend = control.crest_inner_r + t * (control.nose_r - control.crest_inner_r);
    let receiver_blend = receiver[0].0 + t * (receiver[1].0 - receiver[0].0);
    receiver[0].0 += hook.crest_inner_r - control.crest_inner_r;
    receiver.insert(1, (receiver_blend, h));
    (vec![v2(cover_blend, h)], receiver)
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
    let control = Hook {
        crest_inner_r: s.outer_r - TWO_DOT.foot_width,
        ..wide
    };
    let lip_h = s.roof_h + ENTRY_DEPTH + NOSE_LENGTH + wide.lip_r - wide.nose_r;
    let angle = s.free_angle(s.roof_h, lip_h, FREE_TIP_BIAS);
    let mut parts = Map::new();
    let mut settings = Vec::new();
    for (index, entry) in PAIRS.iter().enumerate() {
        let dots = index + 1;
        let hook = Hook {
            crest_inner_r: s.outer_r - entry.foot,
            ..wide
        };
        let (cover_guide, receiver_guide) = guides(s, control, hook);
        let cover = s.cover_with_profile(original, hook, FREE_TIP_BIAS, true, &cover_guide)?;
        let receiver = s.receiver_with_profile(trimmed, post, hook, 0., &receiver_guide)?;
        let crest_r = wide.lip_r - entry.lip_reduction;
        let crest_h = lip_h - entry.lip_reduction;
        let mouth = [
            (crest_r, crest_h),
            (crest_r, crest_h + CREST_HEIGHT),
            (entry.pilot_r, s.rim_h),
        ];
        let receiver = ease_mouth(s, &receiver, &mouth)?;
        for (kind, stock, mark, normal, pose) in [
            ("cover", &cover, back_mark, -V3::Z, cover_pose),
            ("receiver", &receiver, flange_mark, V3::X, receiver_pose),
        ] {
            let name = format!("{kind}-{dots}");
            parts.insert(
                name.clone(),
                print_part(dir, &name, &numbered(stock, dots, mark, normal)?, pose)?,
            );
        }
        settings.push(json!({"number":dots,"primary_full_pisco_donor":dots==1,"guide_design":entry.fit,
            "crest_land_width_mm":entry.foot,"free_crest_angle_to_roof_deg":angle.to_degrees(),
            "receiver_entrance_r_h_mm":mouth,"retaining_lip_reduction_mm":entry.lip_reduction,
            "centered_hook_capture_mm":crest_r-hook.nose_r,"receiver_guide_r_h_mm":receiver_guide,
            "cover_intermediate_straight_guide_r_h_mm":cover_guide.iter().map(|p| [p.x,p.y]).collect::<Vec<_>>()}));
    }
    let dimensions = json!({"purpose":"Register the three passive-entry snap coupons and the one-dot full-Pisco donor to the C036 two-dot section.",
        "frame":"r is distance from the Pisco axis. h is height above the flat receiver back. The cover closes toward machine +Z.",
        "axis_x_mm":s.axis,"axis_y_mm":s.y,"back_face_z_mm":s.back_z,"cover_seating_travel_mm":FILLER_CONTACT_TRAVEL,
        "section_length_mm":LENGTH,"roof_h_mm":s.roof_h,"join_h_mm":s.join_h,"free_tip_bias_each_mm":FREE_TIP_BIAS,
        "spring_wall_thickness_mm":s.outer_r-s.inner_r,"cover_reference_lip_h_mm":lip_h,
        "centered_post_width_mm":2.*WIDE_POST_HALF_WIDTH,"post_apex_h_mm":s.back_z-post.bounds().min.z,
        "marks":{"form":"Recessed conical dots on the saddle back and fixed flange.","opening_diameter_mm":2.*DOT_RADIUS,
            "depth_mm":DOT_DEPTH,"pitch_mm":DOT_PITCH,"cover_group_center_machine_mm":back_mark.to_array(),
            "receiver_group_center_machine_mm":flange_mark.to_array()},
        "pairs":settings,"parts":parts});
    fs::write(
        dir.join("geometry.json"),
        format!("{}\n", serde_json::to_string_pretty(&dimensions)?),
    )?;
    Ok(())
}
