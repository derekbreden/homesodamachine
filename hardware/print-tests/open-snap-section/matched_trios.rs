//! Three numbered pairs test how a loaded foot bears on the roof at the filmed wide-crown seat.
use super::{
    ENTRY_DEPTH, FILLER_CONTACT_TRAVEL, FREE_TIP_BIAS, Hook, LENGTH, NOSE_LENGTH, Section,
    mirrored_bars, print_part,
};
use anyhow::{Result, ensure};
use hsm_kernel::{Affine, Plane, Profile, Solid, V2, V3, v2, v3};
use serde_json::{Map, json};
use std::{fs, path::Path};

struct Pair {
    land: f64,
    shoulder_offset: f64,
    key_radius: f64,
}

const PAIRS: [Pair; 3] = [
    Pair {
        land: 2.00,
        shoulder_offset: 0.,
        key_radius: 5.48,
    },
    Pair {
        land: 2.60,
        shoulder_offset: 0.,
        key_radius: 7.30,
    },
    Pair {
        land: 2.60,
        shoulder_offset: -0.12,
        key_radius: 9.12,
    },
];

// Each uninterrupted pair of blades has a different transverse spacing. The outer runners
// stop a wider pair from moving one blade into a narrower slot and the other past the collar.
const BLADE_HALF: f64 = 0.70;
const SIDE_CLEARANCE: f64 = 0.62;
const COLLAR_R: f64 = 9.65;
const COLLAR_TOP: f64 = 28.76;
const TIP_H: f64 = 19.04;
const TIP_BEVEL: f64 = 0.20;
const RUNNER_R: f64 = COLLAR_R + 0.80;
const RUNNER_WIDTH: f64 = 1.10;
const MARK_PITCH: f64 = 3.6;

/// Rotation of a beam cross section about its neutral axis under the retaining-lip load.
pub(super) fn free_angle(s: &Section, h: f64, lip_h: f64, bias: f64) -> f64 {
    let span = s.join_h - lip_h;
    let t = ((s.join_h - h) / span).clamp(0., 1.);
    let slope = 1.5 * t * (2. - t);
    let tip_deflection = (3. * (s.join_h - s.roof_h) / span - 1.) / 2.;
    (bias * slope / (span * tip_deflection)).atan()
}

/// Convert the seated end view to a constant machine-space section, restoring the free cover's pose.
fn contour(s: &Section, rh: &[(f64, f64)], travel: f64) -> Vec<V2> {
    rh.iter()
        .map(|&(r, h)| v2(s.axis + r, s.back_z - h - travel))
        .collect()
}

fn keyed_cover(s: &Section, cover: &Solid, radius: f64, marks: usize) -> Result<Solid> {
    let saddle_h = s.back_z - cover.bounds().min.z - FILLER_CONTACT_TRAVEL;
    let lo = radius - BLADE_HALF;
    let hi = radius + BLADE_HALF;
    let blades = [
        (lo, saddle_h - 0.9),
        (lo, TIP_H + TIP_BEVEL),
        (lo + TIP_BEVEL, TIP_H),
        (hi - TIP_BEVEL, TIP_H),
        (hi, TIP_H + TIP_BEVEL),
        (hi, saddle_h - 0.9),
    ];
    let runners = [
        (RUNNER_R, TIP_H + TIP_BEVEL),
        (RUNNER_R + TIP_BEVEL, TIP_H),
        (RUNNER_R + RUNNER_WIDTH - TIP_BEVEL, TIP_H),
        (RUNNER_R + RUNNER_WIDTH, TIP_H + TIP_BEVEL),
        (RUNNER_R + RUNNER_WIDTH, 29.55),
        (10.20, 32.45),
        (10.20, 33.30),
        (10.20 - RUNNER_WIDTH, 33.30),
        (10.20 - RUNNER_WIDTH, 32.45),
        (RUNNER_R, 29.55),
    ];
    let mut result = cover.clone();
    for feature in [&blades[..], &runners[..]] {
        let [right, left] =
            mirrored_bars(&contour(s, feature, FILLER_CONTACT_TRAVEL), s.axis, s.y)?;
        result = result.union(&right)?.union(&left)?;
    }

    let mut grooves = Vec::new();
    for index in 0..marks {
        let r = (index as f64 - (marks - 1) as f64 / 2.) * MARK_PITCH;
        let points = contour(
            s,
            &[
                (r - 1.16, saddle_h + 0.2),
                (r, saddle_h - 0.85),
                (r + 1.16, saddle_h + 0.2),
            ],
            FILLER_CONTACT_TRAVEL,
        );
        grooves.push(
            Plane::XZ
                .at(v3(0., s.y - LENGTH / 2. - 0.1, 0.))
                .extrude(&Profile::polygon(&points), -LENGTH - 0.2)?,
        );
    }
    result.cut_all(&grooves)
}

fn keyed_receiver(s: &Section, receiver: &Solid, radius: f64) -> Result<Solid> {
    // The collar grows from material inside both catch necks. Its beveled entry stays inside
    // the hooks during insertion. The seating load still goes through the feet and the housing crown.
    let edge_bevel = 0.55;
    let outline = [
        (-COLLAR_R, s.roof_h),
        (COLLAR_R, s.roof_h),
        (COLLAR_R, COLLAR_TOP - edge_bevel),
        (COLLAR_R - edge_bevel, COLLAR_TOP),
        (-COLLAR_R + edge_bevel, COLLAR_TOP),
        (-COLLAR_R, COLLAR_TOP - edge_bevel),
    ];
    let collar = Plane::XZ
        .at(v3(0., s.y - LENGTH / 2., 0.))
        .extrude(&Profile::polygon(&contour(s, &outline, 0.)), -LENGTH)?;
    let half = BLADE_HALF + SIDE_CLEARANCE;
    let slot = Solid::cuboid(
        v3(
            s.axis + radius - half,
            s.y - LENGTH / 2. - 1.,
            s.back_z - COLLAR_TOP - 1.,
        ),
        v3(
            s.axis + radius + half,
            s.y + LENGTH / 2. + 1.,
            s.back_z - TIP_H + 1.,
        ),
    );
    let collar = collar.cut_all(&[slot.clone(), slot.mirror(v3(s.axis, 0., 0.), V3::X)])?;
    receiver.union(&collar)
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
    let mut parts = Map::new();
    let mut settings = Vec::new();
    for (index, pair) in PAIRS.iter().enumerate() {
        let n = index + 1;
        let hook = Hook {
            crest_inner_r: s.outer_r - pair.land,
            ..wide
        };
        let receiver = s.receiver(trimmed, post, hook, pair.shoulder_offset, n)?;
        let receiver = keyed_receiver(s, &receiver, pair.key_radius)?;
        let free = s.wide_cover(original, hook, FREE_TIP_BIAS, true)?;
        let cover = keyed_cover(s, &free, pair.key_radius, n)?;
        let flat = s.wide_cover(original, hook, 0., true)?;
        let straight =
            keyed_cover(s, &flat, pair.key_radius, n)?.translate(V3::Z * FILLER_CONTACT_TRAVEL);
        let overlap = receiver.shared_volume(&straight)?;
        ensure!(
            overlap < 1e-5 && straight.gap_within(post, 1.)? < 1e-5,
            "pair {n}: straight feet must reach the roof with the saddle against the housing crown ({overlap} mm³)"
        );
        let lip_h = s.roof_h + ENTRY_DEPTH + NOSE_LENGTH + hook.lip_r - hook.nose_r;
        let angle = free_angle(s, s.roof_h, lip_h, FREE_TIP_BIAS);
        for (kind, solid, pose) in [
            ("cover", &cover, cover_pose),
            ("receiver", &receiver, receiver_pose),
        ] {
            let name = format!("{kind}-{n}");
            parts.insert(name.clone(), print_part(dir, &name, solid, pose)?);
        }
        settings.push(json!({"number": n, "crest_land_width_mm": pair.land, "retaining_shoulder_offset_mm": pair.shoulder_offset,
            "free_crest_angle_to_roof_deg": angle.to_degrees(), "free_outer_edge_closer_to_roof_mm": pair.land * angle.sin(),
            "key_blade_center_radius_mm":pair.key_radius, "straight_seated_overlap_mm3":overlap}));
    }
    let geometry = json!({"purpose": "Register the six print meshes to the seated Pisco section and identify each marked mate.",
        "assembly_frame":"r = X minus the regulator axis. h = back face Z minus Z. The seated cover moves +Z from its nominal pose.",
        "axis_x_mm":s.axis,"axis_y_mm":s.y,"back_face_z_mm":s.back_z,"cover_seating_travel_mm":FILLER_CONTACT_TRAVEL,
        "section_length_mm":LENGTH,"roof_h_mm":s.roof_h,"join_h_mm":s.join_h,"free_tip_bias_each_mm":FREE_TIP_BIAS,
        "centered_hook_capture_mm":wide.lip_r-wide.nose_r,"centered_post_width_mm":2.*super::WIDE_POST_HALF_WIDTH,
        "keys":{"blade_width_mm":2.*BLADE_HALF,"nominal_slot_side_clearance_mm":SIDE_CLEARANCE,"blade_tip_h_mm":TIP_H,
            "collar_outer_radius_mm":COLLAR_R,"collar_top_h_mm":COLLAR_TOP,"guide_inner_radius_mm":RUNNER_R,
            "guide_width_mm":RUNNER_WIDTH,"guide_clearance_each_side_mm":RUNNER_R-COLLAR_R},
        "marks":"One, two or three V-grooves across the cover back and the same count of V-notches in the receiver flange.",
        "pairs":settings,"parts":parts});
    fs::write(
        dir.join("geometry.json"),
        format!("{}\n", serde_json::to_string_pretty(&geometry)?),
    )?;
    Ok(())
}
