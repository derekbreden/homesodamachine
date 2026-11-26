//! The full bench pair carries the filmed Mark2 profiles on the production Pisco spring and pocket stations.
mod axial_grip;
mod easy_entry;
#[allow(dead_code)]
#[path = "../../../tools/hsm/print-prep/src/mesh.rs"]
mod mesh;
mod two_dot;

use anyhow::{Context, Result, ensure};
use hsm_kernel::{Affine, Face, Plane, Profile, Solid, V3, import, reads, stl_bytes, v2, v3};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{
    fs,
    path::{Path, PathBuf},
};

const HERE: &str = "hardware/print-tests/pisco-wide-snap/parts";
const COUPONS: &str = "hardware/print-tests/open-snap-section/parts";
const RECEIVERS: &str = "hardware/print-tests/equipment-snap-pairs";
const BEARING_LENGTH: f64 = 2.0;
// The upper ring's deposited terraces seat the scanned housing at about +0.03 mm.
const SEATED_HOUSING_RISE: f64 = 0.035;
const PAD_TO_PRINTED_STOP: f64 = -0.0103;

fn number(record: &Value, key: &str) -> Result<f64> {
    record[key]
        .as_f64()
        .with_context(|| format!("missing dimension {key}"))
}

fn limits(points: impl Iterator<Item = f64>) -> Result<[f64; 2]> {
    let t = points.fold([f64::INFINITY, f64::NEG_INFINITY], |a, p| {
        [a[0].min(p), a[1].max(p)]
    });
    ensure!(t[0] < t[1], "feature needs two axial ends");
    Ok(t)
}

fn write_json(path: &Path, value: &Value) -> Result<()> {
    let mut bytes = serde_json::to_vec_pretty(value)?;
    bytes.push(b'\n');
    Ok(fs::write(path, bytes)?)
}

fn hash(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

/// Restore a printed coupon to its machine frame before transferring its prismatic working faces.
fn coupon(parts: &Path, row: &Value, register: impl Fn(V3) -> V3) -> Result<Solid> {
    let file = parts.join(row["stl"].as_str().context("coupon STL")?);
    let mesh = mesh::Mesh::read_stl(&file)?;
    let m: [[f64; 4]; 3] = serde_json::from_value(row["assembly_to_print_matrix_mm"].clone())?;
    let vertices: Vec<_> = mesh
        .vertices
        .iter()
        .map(|p| {
            let unrotate = |k: usize| (0..3).map(|i| m[i][k] * (p[i] - m[i][3])).sum();
            register(v3(unrotate(0), unrotate(1), unrotate(2)))
        })
        .collect();
    let triangles: Vec<_> = mesh.faces.iter().map(|f| f.map(|i| i as u32)).collect();
    Solid::from_mesh(
        &vertices,
        &triangles,
        &vec![0; triangles.len()],
        &[Face::from_json(&Value::Null)?],
    )
}

/// Stretch an open-ended constant section along Y and leave its working XZ contour untouched.
fn along(section: &Solid, y: [f64; 2]) -> Result<Solid> {
    let b = section.bounds();
    let k = (y[1] - y[0]) / b.size().y;
    section.mapped(&Affine {
        m: [
            [1., 0., 0., 0.],
            [0., k, 0., y[0] - k * b.min.y],
            [0., 0., 1., 0.],
        ],
    })
}

/// Lightly support the purchased regulator across the same chord as the wide coupon crown.
fn bearing(axis: f64, z: f64, y: f64, radius: f64, width: f64) -> Result<Solid> {
    let half = width / 2.;
    let centre = z + SEATED_HOUSING_RISE - PAD_TO_PRINTED_STOP;
    let mut xs: Vec<_> = (-32..=32).map(|i| half * f64::from(i) / 32.).collect();
    let base = centre - radius - 0.65;
    let mut pts = vec![v2(axis - half, base), v2(axis + half, base)];
    xs.reverse();
    pts.extend(
        xs.iter()
            .map(|&x| v2(axis + x, centre - (radius * radius - x * x).sqrt())),
    );
    Plane::XZ
        .at(v3(0., y - BEARING_LENGTH / 2., 0.))
        .extrude(&Profile::polygon(&pts), -BEARING_LENGTH)
}

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1).peekable();
    let easy = args.next_if(|v| v == "--easy-entry").is_some();
    let axial = easy || args.next_if(|v| v == "--axial-grip").is_some();
    let numbered_trial = axial || args.next_if(|v| v == "--two-dot-drop").is_some();
    let dots = if easy { 1 } else { 2 };
    let default_out = if easy {
        Path::new(HERE).join("easy-entry")
    } else if axial {
        Path::new(HERE).join("axial-grip")
    } else if numbered_trial {
        Path::new(HERE).join("two-dot-drop")
    } else {
        PathBuf::from(HERE)
    };
    let out = args.next().map(PathBuf::from).unwrap_or(default_out);
    ensure!(
        args.next().is_none(),
        "expected [--two-dot-drop | --axial-grip | --easy-entry] [output directory]"
    );
    fs::create_dir_all(&out)?;
    let coupons = Path::new(COUPONS);
    let base = reads::json(coupons.join("geometry.json"))?;
    let wide = reads::json(coupons.join("flush-geometry.json"))?;
    let spec = reads::json(Path::new(RECEIVERS).join("inputs.json"))?;
    let source = spec["source_model"].as_str().context("enclosure source")?;
    let shell = import::model(source)?;
    let shell = import::body(&shell, "enclosure-back-top")?;
    let fixture = spec["receivers"]
        .as_array()
        .context("fixture cuts")?
        .iter()
        .find(|x| x["name"] == "pisco-receiver")
        .context("Pisco fixture bounds")?;
    let lo: [f64; 3] = serde_json::from_value(fixture["min_mm"].clone())?;
    let hi: [f64; 3] = serde_json::from_value(fixture["max_mm"].clone())?;
    let crop = Solid::cuboid(lo.into(), hi.into());
    let rooted: Vec<_> = shell
        .intersect(&crop)?
        .components()
        .into_iter()
        .filter(|b| (b.bounds().max.z - hi[2]).abs() < 1e-5)
        .collect();
    ensure!(rooted.len() == 1, "one Pisco receiver roots in the roof");
    let seat = &rooted[0];
    let caps_path = base["cover_source"].as_str().context("installed cap model")?;
    let caps = import::model(caps_path)?;
    let cap = import::body(&caps, "pisco-snap-cap")?;
    let b = cap.bounds();
    let axis = number(&wide, "axis_x_mm")?;
    let axis_z = number(&base, "axis_z_mm")?;
    let y = number(&base, "section_y_mm")?;
    let roof_z = number(&base, "pocket_roof_z_mm")?;
    let rim_z = number(&wide, "back_face_z_mm")? - number(&wide, "receiver_rim_h_mm")?;
    let join_z =
        hi[2] - number(&wide, "spring_join_h_mm")? - number(&base, "filler_contact_travel_from_nominal_mm")?;
    let outer = b.max.x - axis;
    let wings_y = limits(
        cap.verts()
            .iter()
            .filter(|p| (p.z - b.max.z).abs() < 1e-5)
            .map(|p| p.y),
    )?;
    let old_lip = axis + outer - 2.50;
    let pockets_y = limits(
        seat.verts()
            .iter()
            .filter(|p| (p.x - old_lip).abs() < 1e-5 && (p.z - rim_z).abs() < 1e-5)
            .map(|p| p.y),
    )?;
    let donor_dir = if easy {
        coupons.join("easy-entry")
    } else if axial {
        coupons.join("next-pairs")
    } else if numbered_trial {
        coupons.join("solid-pairs")
    } else {
        coupons.to_path_buf()
    };
    let numbered = if numbered_trial {
        reads::json(donor_dir.join("geometry.json"))?
    } else {
        Value::Null
    };
    let (free_cover, neutral) = if numbered_trial {
        (
            &numbered["parts"][format!("cover-{dots}")],
            &numbered["parts"][format!("receiver-{dots}")],
        )
    } else {
        (
            &wide["parts"]["cover-wide-preloaded"],
            &wide["parts"]["receiver-wide-neutral"],
        )
    };
    let register = |mut p: V3| {
        for plane in [roof_z, rim_z, join_z, b.max.z] {
            if (p.z - plane).abs() < 2e-6 {
                p.z = plane;
            }
        }
        for x in [axis - outer, axis + outer, axis - outer + 2., axis + outer - 2.] {
            if (p.x - x).abs() < 5e-7 {
                p.x = x;
            }
        }
        p
    };
    let face = coupon(&donor_dir, free_cover, register)?;
    let donor = along(&face, wings_y)?;
    let lower = b.min - v3(1., 1., 1.);
    let upper = b.max + v3(1., 1., 1.);
    let high = Solid::cuboid(v3(lower.x, lower.y, axis_z + 0.10), upper);
    // At the join the spring and the raised outlet lip have an open slot between them.
    let side = Solid::cuboid(v3(axis + outer - 3., lower.y, join_z), upper);
    let body = cap.cut_all(&[high, side.clone(), side.mirror(v3(axis, 0., 0.), V3::X)])?;
    let new_wings = donor.intersect(&Solid::cuboid(v3(lower.x, lower.y, join_z - 0.02), upper))?;
    let width = number(&wide["mark2_integral_post"], "width_mm")?;
    let radius = number(&base, "scanned_housing_radius_mm")?;
    let pad = bearing(axis, axis_z, y, radius, width)?;
    let cover = body.union(&new_wings)?.union(&pad)?;
    let (cover, saddle_change) = if numbered_trial {
        let (raised, change) = two_dot::supported_saddle(&cover, axis, axis_z, &base)?;
        (
            two_dot::dots(
                &raised,
                &numbered["marks"],
                "cover_group_center_machine_mm",
                dots,
                -V3::Z,
            )?,
            change,
        )
    } else {
        (cover, Value::Null)
    };
    let part = coupon(&donor_dir, neutral, register)?;
    let cheeks = along(&part, pockets_y)?;
    // Start inside the old pocket neck and outside every station of the through-passage.
    let cheek_min = axis + outer - 5.40;
    let box_side = |x: f64, z: f64| {
        Solid::cuboid(
            v3(x, pockets_y[0], rim_z - 0.02),
            v3(axis + outer + 0.5, pockets_y[1], z),
        )
    };
    let old = box_side(cheek_min, roof_z);
    let right = cheeks.intersect(&box_side(cheek_min - 0.03, roof_z + 0.02))?;
    let mirror = |s: &Solid| s.mirror(v3(axis, 0., 0.), V3::X);
    let fixed = seat
        .cut_all(&[old.clone(), mirror(&old)])?
        .union(&right)?
        .union(&mirror(&right))?;
    let receiver = if numbered_trial {
        two_dot::dots(
            &fixed,
            &numbered["marks"],
            "receiver_group_center_machine_mm",
            dots,
            V3::X,
        )?
    } else {
        let edge = seat.bounds().max.x;
        let notch = Profile::polygon(&[
            v2(edge + 0.2, y - 1.4),
            v2(edge - 1.2, y),
            v2(edge + 0.2, y + 1.4),
        ]);
        fixed.cut(
            &Plane::XY
                .at(v3(0., 0., roof_z - 1.))
                .extrude(&notch, hi[2] - roof_z + 2.)?,
        )?
    };
    let (cover, receiver, axial_settings) = if axial {
        axial_grip::stops(cover, receiver, axis, axis_z, pockets_y[0], outer)?
    } else {
        (cover, receiver, Value::Null)
    };
    let (cover, receiver, entry_settings) = if easy {
        easy_entry::guides(cover, receiver, axis, axis_z, rim_z, &axial_settings, &base)?
    } else {
        (cover, receiver, Value::Null)
    };
    let turn = Affine {
        m: [[1., 0., 0., 0.], [0., 0., -1., 0.], [0., 1., 0., 0.]],
    };
    let cb = cover.transformed(&turn).bounds();
    let print = Affine::translation(v3(-cb.center().x, -cb.center().y, -cb.min.z)).then_after(&turn);
    let (cap_name, receiver_name) = if numbered_trial {
        ("cover", "receiver")
    } else {
        ("pisco-cover", "pisco-receiver")
    };
    let mut outputs = serde_json::Map::new();
    for (name, solid, transform) in [
        (cap_name, &cover, print),
        (receiver_name, &receiver, Affine::IDENTITY),
    ] {
        solid.check()?;
        ensure!(
            solid.components().len() == 1,
            "{name} must be one connected solid"
        );
        let bytes = stl_bytes(&[&solid.transformed(&transform)])?;
        mesh::Mesh::from_corners(&mesh::stl_corners(&bytes)?).check_closed_single_body(name)?;
        fs::write(out.join(format!("{name}.stl")), &bytes)?;
        let bb = solid.bounds();
        outputs.insert(
            name.into(),
            json!({"stl":format!("{name}.stl"),"sha256":hash(&bytes),"connected_solids":1,
            "volume_mm3":solid.volume(),"installed_bounds_mm":[bb.min.to_array(),bb.max.to_array()],
            "assembly_to_stl_matrix_mm":transform.m}),
        );
    }
    let mut features = reads::json(Path::new(RECEIVERS).join("parts/pisco-receiver.print-features.json"))?;
    features["source_stl_sha256"] = outputs[receiver_name]["sha256"].clone();
    features["producer"] = json!("pisco-wide-snap");
    for row in features["support_free_regions"].as_array_mut().unwrap() {
        let name = row["name"].as_str().unwrap_or("");
        if !name.contains("catch pocket") {
            continue;
        }
        let sign = if name.contains("west") { -1. } else { 1. };
        let mut xs = [axis + sign * (outer - 4.0 - 0.22), axis + sign * (outer - 2.0)];
        xs.sort_by(f64::total_cmp);
        for key in ["bounds_source_mm", "blocking_bounds_source_mm"] {
            row[key][0] = json!(xs[0]);
            row[key][1] = json!(xs[1]);
        }
        row["bounds_source_mm"][2] = json!(pockets_y[0]);
        row["bounds_source_mm"][3] = json!(pockets_y[1]);
    }
    write_json(
        &out.join(format!("{receiver_name}.print-features.json")),
        &features,
    )?;
    let donor_hash = |row: &Value| -> Result<String> {
        Ok(hash(&fs::read(
            donor_dir.join(row["stl"].as_str().context("working coupon STL")?),
        )?))
    };
    let mut record = json!({"purpose":"Transfer the neutral wide Mark2 snap to the production hardware seat and axial stages.",
        "parts":outputs,"production_cover_source":caps_path,"production_receiver_source":source,
        "production_cover_sha256":hash(&fs::read(caps_path)?),"production_receiver_sha256":hash(&fs::read(source)?),
        "coupon_parts":donor_dir,"working_profiles":[free_cover["stl"],neutral["stl"]],
        "donor_stl_sha256":[donor_hash(free_cover)?,donor_hash(neutral)?],
        "cover_body_y_mm":[b.min.y,b.max.y],"spring_y_mm":wings_y,"pocket_y_mm":pockets_y,
        "pocket_roof_z_mm":roof_z,"print_directions_in_machine":{"cover":[0,1,0],"receiver":[0,0,-1]},
        "coupon_straight_neutral_target":wide["straight_seated_target"]["receiver-wide-neutral"],"free_inward_tip_bias_mm":wide["mark2_free_inward_tip_bias_each_mm"],
        "guide_radial_air_mm":wide["running_gap_radial_mm"],"bearing":{"land_width_mm":width,"land_y_mm":[y-BEARING_LENGTH/2.,y+BEARING_LENGTH/2.],
        "housing_radius_mm":radius,"design_housing_rise_mm":SEATED_HOUSING_RISE,"cover_closure_at_printed_stop_mm":PAD_TO_PRINTED_STOP}});
    if numbered_trial {
        record["purpose"] = json!(
            "Test the two-dot wing and receiver profiles over the real Pisco with 0.20 mm more saddle take-up."
        );
        record
            .as_object_mut()
            .unwrap()
            .remove("coupon_straight_neutral_target");
        record["coupon_straight_target"] = numbered["pairs"]
            .as_array()
            .and_then(|rows| rows.iter().find(|r| r["number"] == dots))
            .context("selected numbered coupon settings")?
            .clone();
        record["centered_hook_capture_mm"] = numbered["centered_hook_capture_mm"].clone();
        record["spring_wall_thickness_mm"] = numbered["spring_wall_thickness_mm"].clone();
        record["saddle_change_from_previous_full_pair"] = saddle_change;
        record["marks"] = numbered["marks"].clone();
        record["bearing"]["previous_pair_housing_rise_input_mm"] = record["bearing"]
            .as_object_mut()
            .unwrap()
            .remove("design_housing_rise_mm")
            .context("original housing-rise datum")?;
        record["bearing"]["previous_pair_crest_registration_mm"] = record["bearing"]
            .as_object_mut()
            .unwrap()
            .remove("cover_closure_at_printed_stop_mm")
            .context("original crest datum")?;
    }
    if axial {
        record["purpose"] = json!(
            "Reduce end travel of the purchased regulator at its rigid outlet shoulder with the latest two-dot guide."
        );
        record["axial_stops"] = axial_settings;
        record["pocket_y_mm"][0] = record["axial_stops"]["new_wing_forward_stop_y_mm"].clone();
        record["guide_nose_air_mm"] = record
            .as_object_mut()
            .unwrap()
            .remove("guide_radial_air_mm")
            .unwrap();
    }
    if easy {
        record["purpose"] = json!(
            "Fit the real Pisco with the first push-on coupon profile and guided axial starts at the full cover ends."
        );
        record["axial_entry_guides"] = entry_settings;
        record["centered_hook_capture_mm"] =
            record["coupon_straight_target"]["centered_hook_capture_mm"].clone();
        record.as_object_mut().unwrap().remove("guide_nose_air_mm");
    }
    write_json(&out.join("geometry.json"), &record)?;
    Ok(())
}
