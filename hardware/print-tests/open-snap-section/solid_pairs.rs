//! Open Pisco coupons compare the existing wing-foot bearing width and the backed retaining shoulder.
use super::{
    ENTRY_DEPTH, FILLER_CONTACT_TRAVEL, FREE_TIP_BIAS, Hook, LENGTH, NOSE_LENGTH, RUNNING_GAP,
    Section, WIDE_POST_HALF_WIDTH, print_part,
};
use anyhow::{Result, ensure};
use hsm_kernel::{Affine, Solid, V3, v3};
use serde_json::{Map, json};
use std::{fs, path::Path};

#[path = "guide_contact.rs"]
mod guide_contact;

const DOT_RADIUS: f64 = 1.00;
const DOT_DEPTH: f64 = 0.60;
const DOT_PITCH: f64 = 3.40;
const BACK_MARK_R: f64 = 7.80;

#[derive(Clone, Copy)]
struct Fit {
    foot_width: f64,
    pocket_width: f64,
    shoulder_offset: f64,
    guide_gap: f64,
    guide_blend: f64,
}

const TWO_DOT: Fit = Fit {
    foot_width: 2.60,
    pocket_width: 2.60,
    shoulder_offset: 0.,
    guide_gap: RUNNING_GAP,
    guide_blend: 0.,
};

const FOOT_BEARINGS: [Fit; 3] = [
    Fit {
        foot_width: 2.00,
        pocket_width: 2.00,
        ..TWO_DOT
    },
    TWO_DOT,
    Fit {
        shoulder_offset: -0.12,
        ..TWO_DOT
    },
];

// The filmed two-dot fit holds firmly. These isolate shoulder tension, the fixed entry wall and the cover toe.
const ENTRY_FACES: [Fit; 3] = [
    Fit {
        shoulder_offset: -0.06,
        ..TWO_DOT
    },
    Fit {
        guide_gap: 0.10,
        guide_blend: 1.20,
        ..TWO_DOT
    },
    Fit {
        foot_width: 2.76,
        ..TWO_DOT
    },
];

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
    let back_mark = v3(s.axis + BACK_MARK_R, s.y, original.bounds().min.z);
    let flange_mark = v3(trimmed.bounds().max.x, s.y, s.back_z - s.roof_h / 2.);
    let lip_h = s.roof_h + ENTRY_DEPTH + NOSE_LENGTH + wide.lip_r - wide.nose_r;
    let angle = s.free_angle(s.roof_h, lip_h, FREE_TIP_BIAS);
    for (folder, pairs) in [("solid-pairs", FOOT_BEARINGS), ("next-pairs", ENTRY_FACES)] {
        let dir = dir.join(folder);
        fs::create_dir_all(&dir)?;
        let mut settings = Vec::new();
        let mut parts = Map::new();
        for (index, fit) in pairs.into_iter().enumerate() {
            let n = index + 1;
            let hook = Hook {
                crest_inner_r: s.outer_r - fit.foot_width,
                ..wide
            };
            let pocket = Hook {
                crest_inner_r: s.outer_r - fit.pocket_width,
                ..wide
            };
            let receiver = numbered(
                &s.receiver_with_guide(
                    trimmed,
                    post,
                    pocket,
                    fit.shoulder_offset,
                    fit.guide_gap,
                    fit.guide_blend,
                )?,
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
                parts.insert(name.clone(), print_part(&dir, &name, solid, pose)?);
            }
            let mut setting = json!({"number":n, "crest_land_width_mm":fit.foot_width, "retaining_shoulder_offset_mm":fit.shoulder_offset,
            "free_crest_angle_to_roof_deg":angle.to_degrees(),"free_outer_edge_closer_to_roof_mm":fit.foot_width*angle.sin(),
            "straight_seated_overlap_mm3":overlap});
            if folder == "next-pairs" {
                setting["receiver_guide"] = json!({"reference_foot_width_mm":fit.pocket_width, "offset_from_reference_ramp_mm":fit.guide_gap,
                "blend_length_to_original_nose_mm":fit.guide_blend,"nose_running_gap_mm":RUNNING_GAP});
            }
            settings.push(setting);
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
    }
    guide_contact::write(
        &dir.join("guide-contact"),
        s,
        original,
        trimmed,
        post,
        wide,
        receiver_pose,
        cover_pose,
        back_mark,
        flange_mark,
    )
}
