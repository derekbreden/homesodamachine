//! Transfer the selected coupon's free toe, entrance and retaining faces onto the C037 full-size hardware seats.
use super::{COUPONS, HERE, hash, installed, number, two_dot, write_json, write_part};
use anyhow::{Context, Result};
use hsm_kernel::{Affine, Plane, Profile, Solid, V3, reads, v2, v3};
use serde_json::{Value, json};
use std::{fs, path::Path};

/// Locate the relaxed inner toe directly on the triangles of the selected coupon.
fn toe_x(cover: &Solid, axis: f64, z: f64) -> Result<f64> {
    let mut inner = None;
    for tri in cover.tris() {
        let [a, b, c] = tri.map(|i| cover.verts()[i as usize]);
        for (p, q) in [(a, b), (b, c), (c, a)] {
            if p.x > axis && q.x > axis && (p.z > z) != (q.z > z) {
                let x = p.x + (q.x - p.x) * (z - p.z) / (q.z - p.z);
                inner = Some(inner.map_or(x, |r: f64| r.min(x)));
            }
        }
    }
    inner.context("relaxed working face across the coupon's open end")
}

fn cover(accepted: &Solid, donor: &Solid, common: &Value, chosen: &Value) -> Result<Solid> {
    let axis = number(common, "axis_x_mm")?;
    let back = number(common, "back_face_z_mm")?;
    let roof = number(common, "roof_h_mm")?;
    let guide = chosen["cover_intermediate_straight_guide_r_h_mm"][0][1]
        .as_f64()
        .context("end of the three-dot toe lead")?;
    let z1 = back - (0.75 * guide + 0.25 * roof);
    let z2 = back - (0.25 * guide + 0.75 * roof);
    let x1 = toe_x(donor, axis, z1)?;
    let slope = (toe_x(donor, axis, z2)? - x1) / (z2 - z1);
    let x = |z| x1 + slope * (z - z1);
    let low = back - guide - 1.;
    let high = back - roof + 1.;
    let b = accepted.bounds();
    let cut = Plane::XZ.at(v3(0., b.max.y + 1., 0.)).extrude(
        &Profile::polygon(&[v2(axis, low), v2(x(low), low), v2(x(high), high), v2(axis, high)]),
        b.size().y + 2.,
    )?;
    accepted.cut_all(&[cut.clone(), cut.mirror(v3(axis, 0., 0.), V3::X)])
}

/// Two backed additions on each side carry the coupon's lip and its guide at the roof.
fn receiver(accepted: &Solid, common: &Value, chosen: &Value, previous: &Value, y: [f64; 2]) -> Result<Solid> {
    let axis = number(common, "axis_x_mm")?;
    let back = number(common, "back_face_z_mm")?;
    let [lip, flat, pilot]: [[f64; 2]; 3] = serde_json::from_value(chosen["receiver_entrance_r_h_mm"].clone())?;
    let [old_lip, _, old_pilot]: [[f64; 2]; 3] = serde_json::from_value(previous["receiver_entrance_r_h_mm"].clone())?;
    let [roof, blend, _]: [[f64; 2]; 3] = serde_json::from_value(chosen["receiver_guide_r_h_mm"].clone())?;
    let backing = number(common, "spring_wall_thickness_mm")? / 2.;
    let inner = old_pilot[0] - backing / 2.;
    let lip_stock = [old_lip, lip, flat, pilot, [inner, pilot[1]], [inner, old_lip[1]]];
    let roof_stock = [
        roof,
        blend,
        [blend[0] - backing, blend[1]],
        [blend[0] - backing, roof[1] - backing / 2.],
        [roof[0], roof[1] - backing / 2.],
    ];
    let mut added = vec![accepted.clone()];
    for sign in [-1., 1.] {
        for points in [&lip_stock[..], &roof_stock[..]] {
            // The stock joins the archived STL on its existing, single-precision roof and end planes.
            let outline: Vec<_> = points
                .iter()
                .map(|p| v2(f64::from((axis + sign * p[0]) as f32), f64::from((back - p[1]) as f32)))
                .collect();
            added.push(
                Plane::XZ
                    .at(v3(0., y[1], 0.))
                    .extrude(&Profile::polygon(&outline), y[1] - y[0])?,
            );
        }
    }
    Solid::union_all(&added)
}

pub(super) fn write(out: &Path) -> Result<()> {
    let baseline = Path::new(HERE).join("easy-entry");
    let coupons = Path::new(COUPONS).join("easy-entry");
    let full = reads::json(baseline.join("geometry.json"))?;
    let common = reads::json(coupons.join("geometry.json"))?;
    let chosen = common["pairs"]
        .as_array()
        .context("numbered coupons")?
        .iter()
        .find(|p| p["number"] == 3)
        .context("three-dot pair")?;
    let old = |name: &str| installed(&baseline, &full["parts"][name], "assembly_to_stl_matrix_mm", |p| p);
    let new = |name: &str| installed(&coupons, &common["parts"][name], "assembly_to_print_matrix_mm", |p| p);
    let cover = cover(&old("cover")?, &new("cover-3")?, &common, chosen)?;
    let ends: [f64; 2] = serde_json::from_value(full["pocket_y_mm"].clone())?;
    let receiver = receiver(
        &old("receiver")?,
        &common,
        chosen,
        &full["coupon_straight_target"],
        ends.map(|v| f64::from(v as f32)),
    )?;
    let marks = &common["marks"];
    let cover = two_dot::dots(&cover, marks, "cover_group_center_machine_mm", &[-1., 1.], -V3::Z)?;
    let receiver = two_dot::dots(&receiver, marks, "receiver_group_center_machine_mm", &[-1., 1.], V3::X)?;
    fs::create_dir_all(out)?;
    let pose = Affine {
        m: serde_json::from_value(full["parts"]["cover"]["assembly_to_stl_matrix_mm"].clone())?,
    };
    let cover = write_part(out, "cover", &cover, pose)?;
    let receiver = write_part(out, "receiver", &receiver, Affine::IDENTITY)?;
    let mut features = reads::json(baseline.join("receiver.print-features.json"))?;
    features["source_stl_sha256"] = receiver["sha256"].clone();
    let axis = number(&common, "axis_x_mm")?;
    let toe_r = chosen["receiver_guide_r_h_mm"][0][0]
        .as_f64()
        .context("receiver roof guide radius")?;
    for region in features["support_free_regions"]
        .as_array_mut()
        .context("receiver pocket exclusions")?
    {
        let name = region["name"].as_str().unwrap_or("");
        let side = if name == "Pisco west catch pocket" {
            Some((0, -1.))
        } else if name == "Pisco east catch pocket" {
            Some((1, 1.))
        } else {
            None
        };
        if let Some((edge, sign)) = side {
            for bounds in ["bounds_source_mm", "blocking_bounds_source_mm"] {
                region[bounds][edge] = json!(axis + sign * toe_r);
            }
        }
    }
    write_json(&out.join("receiver.print-features.json"), &features)?;
    let mut record = json!({"purpose":"Fit the selected three-dot retaining faces to the complete Pisco cover and receiver tried in C037.",
        "parts":{"cover":cover,"receiver":receiver}, "full_size_source":baseline, "full_size_stl_sha256":[full["parts"]["cover"]["sha256"],full["parts"]["receiver"]["sha256"]],
        "coupon_parts":coupons,"working_profiles":["cover-3.stl","receiver-3.stl"],
        "donor_stl_sha256":[hash(&fs::read(coupons.join("cover-3.stl"))?),hash(&fs::read(coupons.join("receiver-3.stl"))?)],
        "coupon_straight_target":chosen,"centered_hook_capture_mm":chosen["centered_hook_capture_mm"],"marks":marks});
    let middle = number(&common, "axis_y_mm")?;
    let pitch = number(marks, "pitch_mm")?;
    record["marks"]["centers_y_mm"] = json!([middle - pitch, middle, middle + pitch]);
    for field in [
        "cover_body_y_mm",
        "spring_y_mm",
        "pocket_y_mm",
        "pocket_roof_z_mm",
        "print_directions_in_machine",
        "free_inward_tip_bias_mm",
        "spring_wall_thickness_mm",
        "axial_stops",
        "axial_entry_guides",
        "saddle_change_from_previous_full_pair",
        "bearing",
    ] {
        record[field] = full[field].clone();
    }
    write_json(&out.join("geometry.json"), &record)
}
