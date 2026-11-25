//! Matching hook pockets and an inward-biased cover for the open-end fit trial.
use super::{FILLER_CONTACT_TRAVEL, LENGTH, mirrored_bars, print_part};
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Affine, Plane, Profile, Solid, V2, V3, v2, v3};
use serde_json::json;
use std::{fs, path::Path};

#[path = "solid_pairs.rs"]
mod solid_pairs;

// Dimensions in the end view. Heights are measured from the receiver's flat print face.
const RUNNING_GAP: f64 = 0.22;
const FIRM_OFFSET: f64 = 0.12;
const FREE_TIP_BIAS: f64 = 0.80;
const WIDE_POST_HALF_WIDTH: f64 = 4.0;
const ENTRY_DEPTH: f64 = 6.40;
const NOSE_LENGTH: f64 = 2.55;
const RIM_CHAMFER: f64 = 0.48;

struct Section {
    axis: f64,
    y: f64,
    back_z: f64,
    roof_h: f64,
    rim_h: f64,
    join_h: f64,
    outer_r: f64,
    inner_r: f64,
    trim_r: f64,
}

#[derive(Clone, Copy)]
struct Hook {
    crest_inner_r: f64,
    nose_r: f64,
    lip_r: f64,
}

impl Section {
    fn receiver(&self, trimmed_seat: &Solid, post: &Solid, hook: Hook, offset: f64) -> Result<Solid> {
        let entry_bottom = self.roof_h + ENTRY_DEPTH;
        let return_start = entry_bottom + NOSE_LENGTH;
        let neck_r = hook.nose_r - RUNNING_GAP;
        let lip_h = return_start + (hook.lip_r - hook.nose_r) - offset;
        let cheek = [
            (self.trim_r - 0.02, self.roof_h - 0.05),
            (hook.crest_inner_r - RUNNING_GAP, self.roof_h - 0.05),
            (hook.crest_inner_r - RUNNING_GAP, self.roof_h),
            (neck_r, entry_bottom),
            (neck_r, return_start - RUNNING_GAP - offset),
            (hook.lip_r, lip_h),
            (hook.lip_r, self.rim_h - RIM_CHAMFER),
            (hook.lip_r - RIM_CHAMFER, self.rim_h),
            (self.trim_r - 0.02, self.rim_h),
        ];
        let points: Vec<_> = cheek.iter().map(|&(r, h)| v2(self.axis + r, self.back_z - h)).collect();
        let [right, left] = mirrored_bars(&points, self.axis, self.y)?;
        trimmed_seat.union(&right)?.union(&left)?.union(post)
    }

    /// The open V notches identify the neutral and firm receivers in the filmed comparison.
    fn flange_notches(&self, receiver: &Solid, marks: usize) -> Result<Solid> {
        let edge = receiver.bounds().max.x;
        let mut notches = Vec::new();
        for i in 0..marks {
            let y = self.y + (i as f64 - (marks - 1) as f64 / 2.0) * 3.6;
            let triangle = Profile::polygon(&[v2(edge + 0.2, y - 1.4), v2(edge - 1.2, y), v2(edge + 0.2, y + 1.4)]);
            notches.push(Plane::XY.at(v3(0., 0., self.back_z - self.roof_h - 1.)).extrude(&triangle, self.roof_h + 2.)?);
        }
        receiver.cut_all(&notches)
    }

    /// Shape a spring loaded at its retaining lip. The unloaded length beyond that lip continues at its tangent.
    fn inward_shift(&self, h: f64, lip_h: f64, tip_bias: f64) -> f64 {
        let load_length = self.join_h - lip_h;
        let t = (self.join_h - h).max(0.) / load_length;
        let deflection = if t <= 1.0 { t * t * (3. - t) / 2. } else { (3. * t - 1.) / 2. };
        let tip_deflection = (3. * (self.join_h - self.roof_h) / load_length - 1.) / 2.;
        tip_bias * deflection / tip_deflection
    }

    /// Turning each cross section with the free leaf levels the foot when its camber is straightened.
    fn free_angle(&self, h: f64, lip_h: f64, bias: f64) -> f64 {
        let span = self.join_h - lip_h;
        let t = ((self.join_h - h) / span).clamp(0., 1.);
        let slope = 1.5 * t * (2. - t);
        let tip_deflection = (3. * (self.join_h - self.roof_h) / span - 1.) / 2.;
        (bias * slope / (span * tip_deflection)).atan()
    }

    fn wide_cover(&self, cover: &Solid, hook: Hook, tip_bias: f64, rotate_with_leaf: bool) -> Result<Solid> {
        let bounds = cover.bounds();
        let join_z = self.back_z - self.join_h - FILLER_CONTACT_TRAVEL;
        let spine = cover.intersect(&Solid::cuboid(bounds.min - v3(1., 1., 1.), v3(bounds.max.x + 1., bounds.max.y + 1., join_z)))?;
        let nose_top = self.roof_h + ENTRY_DEPTH;
        let return_start = nose_top + NOSE_LENGTH;
        let lip_h = return_start + hook.lip_r - hook.nose_r;
        let vertices = [
            v2(self.outer_r, self.join_h + 0.05), v2(self.outer_r, self.roof_h),
            v2(hook.crest_inner_r, self.roof_h), v2(hook.nose_r, nose_top),
            v2(hook.nose_r, return_start), v2(self.inner_r, return_start + self.inner_r - hook.nose_r),
            v2(self.inner_r, self.join_h + 0.05),
        ];
        let mut points = Vec::new();
        for (a, b) in vertices.iter().zip(vertices.iter().cycle().skip(1)) {
            let n = ((a.y - b.y).abs() / 0.60).ceil().max(1.) as usize;
            for i in 0..n {
                let mut p = *a + (*b - *a) * (i as f64 / n as f64);
                let shift = self.inward_shift(p.y, lip_h, tip_bias);
                if rotate_with_leaf {
                    let angle = self.free_angle(p.y, lip_h, tip_bias);
                    let mid_r = (self.outer_r + self.inner_r) / 2.;
                    let dr = p.x - mid_r;
                    p = v2(mid_r + dr * angle.cos(), p.y - dr * angle.sin());
                }
                points.push(v2(self.axis + p.x - shift, self.back_z - p.y - FILLER_CONTACT_TRAVEL));
            }
        }
        let [right, left] = mirrored_bars(&points, self.axis, self.y)?;
        spine.union(&right)?.union(&left)
    }

    /// Sample the housing crown at the saddle's own facet stations to retain its original contact height.
    fn housing_post(&self, cover: &Solid, axis_z: f64, nose_z: f64, radius: f64) -> Result<Solid> {
        let mut xs = vec![-WIDE_POST_HALF_WIDTH, 0., WIDE_POST_HALF_WIDTH];
        xs.extend(cover.verts().iter().filter_map(|p| {
            let x = p.x - self.axis;
            (x.abs() < WIDE_POST_HALF_WIDTH && p.z >= nose_z - FILLER_CONTACT_TRAVEL - 1e-5 && p.z < axis_z).then_some(x)
        }));
        xs.sort_by(f64::total_cmp);
        xs.dedup_by(|a, b| (*a - *b).abs() < 1e-6);
        let mut points: Vec<V2> = xs.iter().map(|x| v2(self.axis + x, nose_z + radius - (radius * radius - x * x).sqrt())).collect();
        points.extend([v2(self.axis + WIDE_POST_HALF_WIDTH, self.back_z), v2(self.axis - WIDE_POST_HALF_WIDTH, self.back_z)]);
        Plane::XZ.at(v3(0., self.y - LENGTH / 2., 0.)).extrude(&Profile::polygon(&points), -LENGTH)
    }
}

pub(super) fn write(dir: &Path, cover: &Solid, seat: &Solid, original_post: &Solid, axis: f64, axis_z: f64, y: f64,
                    roof_z: f64, nose_z: f64, housing_radius: f64, receiver_pose: Affine, cover_pose: Affine) -> Result<()> {
    let back_z = seat.bounds().max.z;
    let outer_r = cover.bounds().max.x - axis;
    let inner_r = outer_r - 2.0;
    let root_z = cover.verts().iter().filter(|p| ((p.x - axis) - inner_r).abs() < 1e-5 && p.z < axis_z)
        .map(|p| p.z).reduce(f64::min).context("end of the existing spring-root fillet")?;
    let old_lip_r = outer_r - 2.50;
    let lip_entry_z = seat.verts().iter().filter(|p| ((p.x - axis) - old_lip_r).abs() < 1e-5)
        .map(|p| p.z).reduce(f64::min).context("entry face on the fixed catch")?;
    let s = Section { axis, y, back_z, roof_h: back_z - roof_z, rim_h: back_z - lip_entry_z,
                      join_h: back_z - (root_z + 0.35 + FILLER_CONTACT_TRAVEL), outer_r, inner_r, trim_r: outer_r - 5.65 };
    let old = Hook { crest_inner_r: outer_r - 0.90, nose_r: outer_r - 5.10, lip_r: old_lip_r };
    let wide = Hook { crest_inner_r: inner_r, nose_r: outer_r - 4.00, lip_r: inner_r - 0.20 };
    let bounds = seat.bounds();
    let cut = Solid::cuboid(v3(axis + s.trim_r, bounds.min.y - 1., bounds.min.z - 1.),
                            v3(bounds.max.x + 1., bounds.max.y + 1., roof_z));
    let trimmed = seat.cut_all(&[cut.clone(), cut.mirror(v3(axis, 0., 0.), V3::X)])?;
    let full_post = s.housing_post(cover, axis_z, nose_z, housing_radius)?;
    let biased = s.wide_cover(cover, wide, FREE_TIP_BIAS, false)?;
    let straight = s.wide_cover(cover, wide, 0., false)?;
    let mut parts = serde_json::Map::new();
    parts.insert("cover-wide-preloaded".into(), print_part(dir, "cover-wide-preloaded", &biased, cover_pose)?);
    let mut target_checks = serde_json::Map::new();
    for (family, hook, post, target) in [("matched", old, original_post, cover), ("wide", wide, &full_post, &straight)] {
        let closed = target.translate(V3::Z * FILLER_CONTACT_TRAVEL);
        let crown_interference = closed.shared_volume(post)?;
        ensure!(crown_interference < 1e-5 && closed.gap_within(post, 1.)? < 1e-5, "{family} crown must touch the centered saddle");
        for (name, offset, marks) in [("neutral", 0., 1), ("firm", FIRM_OFFSET, 2)] {
            let receiver = s.flange_notches(&s.receiver(&trimmed, post, hook, offset)?, marks)?;
            let name = format!("receiver-{family}-{name}");
            let overlap = receiver.shared_volume(&closed)?;
            if offset == 0. { ensure!(overlap < 1e-5, "{name}: straight neutral overlap {overlap} mm³"); }
            parts.insert(name.clone(), print_part(dir, &name, &receiver, receiver_pose)?);
            target_checks.insert(name, json!({"straight_target_overlap_mm3": overlap, "axial_retaining_face_interference_mm": offset,
                "centered_radial_capture_mm": hook.lip_r - hook.nose_r, "crest_land_width_mm": outer_r - hook.crest_inner_r,
                "saddle_to_post_interference_mm3": crown_interference, "flange_identification_notches": marks}));
        }
    }
    let dimensions = json!({"purpose": "Print and register the two full-profile snap comparisons at the filmed stop height.",
        "parts": parts, "straight_seated_target": target_checks, "original_cover": "cover.stl",
        "frame": "r is distance from the Pisco centerline. h is the height from the receiver print face; the target cover has closed 0.10 mm from its nominal installed pose.",
        "axis_x_mm": axis, "back_face_z_mm": back_z, "section_length_mm": LENGTH, "pocket_roof_h_mm": s.roof_h,
        "receiver_rim_h_mm": s.rim_h, "spring_join_h_mm": s.join_h, "running_gap_radial_mm": RUNNING_GAP,
        "mark1_integral_post": {"radius_mm":5.0, "width_mm":6.0},
        "mark2_integral_post": {"radius_mm":housing_radius, "width_mm":2.*WIDE_POST_HALF_WIDTH},
        "post_apex_h_mm": back_z - nose_z, "mark2_free_inward_tip_bias_each_mm": FREE_TIP_BIAS,
        "mark2_straightening_model": "Clamped beam with transverse load at the retaining lip and unloaded length beyond it. The model gives a geometric target; movement and retention require the bench test."});
    fs::write(dir.join("flush-geometry.json"), format!("{}\n", serde_json::to_string_pretty(&dimensions)?))?;
    solid_pairs::write(&dir.join("solid-pairs"), &s, cover, &trimmed, &full_post, wide, receiver_pose, cover_pose)
}
