//! Relieve the print-down side of the fitted meter snap and support its exposed working faces.
use super::three_dot::{facet_solid, mesh, write_part};
use super::{HERE, sha, write_json};
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Affine, Plane, Profile, Solid, V3, reads, v2, v3};
use serde_json::{Value, json};
use std::{fs, path::Path};

fn region_bounds(regions: &Value, name: &str) -> Result<[f64; 6]> {
    let row = regions
        .as_array()
        .context("meter support regions")?
        .iter()
        .find(|r| r["name"] == name)
        .with_context(|| format!("missing meter feature {name}"))?;
    Ok(serde_json::from_value(row["bounds_source_mm"].clone())?)
}

/// The complete footprint of a coplanar set of print-down facets on the actual donor.
fn flat_landing(vertices: &[V3], faces: &[[u32; 3]], bounds: [f64; 6]) -> Result<[f64; 6]> {
    let mut lo = [f64::INFINITY; 3];
    let mut hi = [f64::NEG_INFINITY; 3];
    for f in faces {
        let [a, b, c] = f.map(|i| vertices[i as usize]);
        if a.z != b.z || b.z != c.z || (b - a).cross(c - a).z <= 0. {
            continue;
        }
        let centre = ((a + b + c) / 3.).to_array();
        if (0..3).any(|k| centre[k] < bounds[2 * k] || centre[k] > bounds[2 * k + 1]) {
            continue;
        }
        for p in [a, b, c].map(V3::to_array) {
            for k in 0..3 {
                lo[k] = lo[k].min(p[k]);
                hi[k] = hi[k].max(p[k]);
            }
        }
    }
    ensure!(
        lo[0] < hi[0] && lo[1] < hi[1] && lo[2] == hi[2],
        "expected one flat landing"
    );
    Ok([lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]])
}

/// Close the blind triangle between a donor cheek's back and the two original 45° shoulders.
fn fill_splice(
    receiver: &Solid,
    vertices: &[V3],
    faces: &[[u32; 3]],
    area: [f64; 6],
    upper: bool,
) -> Result<(Solid, Value)> {
    let [x0, x1, fore, aft, z0, z1] = area;
    let middle = (fore + aft) / 2.;
    let mut corners = Vec::new();
    for f in faces {
        let p = f.map(|i| vertices[i as usize]);
        let n = (p[1] - p[0]).cross(p[2] - p[0]);
        let centre = (p[0] + p[1] + p[2]) / 3.;
        if centre.x <= x0
            || centre.x >= x1
            || centre.z <= z0
            || centre.z >= z1
            || !p.iter().any(|v| v.y < middle)
            || !p.iter().any(|v| v.y > middle)
            || (n.z > 0.) != upper
            || n.y.abs() > n.norm() * 1e-5
            || (n.x.abs() - n.z.abs()).abs() > n.norm() * 3e-5
        {
            continue;
        }
        corners.extend(p);
    }
    ensure!(
        !corners.is_empty(),
        "expected an enclosed 45° shoulder splice"
    );
    let extent = |k: usize| {
        corners
            .iter()
            .map(|v| v[k])
            .fold([f64::INFINITY, f64::NEG_INFINITY], |[lo, hi], v| {
                [lo.min(v), hi.max(v)]
            })
    };
    let [left, right] = extent(0);
    let [low, high] = extent(2);
    let lap = 0.02;
    let backing = Solid::cuboid(
        v3(left - lap, fore, low - lap),
        v3(right + lap, aft, high + lap),
    );
    let filled = receiver.union(&backing)?;
    let added = filled.volume() - receiver.volume();
    ensure!(
        (added - 0.5 * (right - left) * (high - low) * (aft - fore)).abs() < 0.005,
        "splice must add only the closed triangle ({added} mm³)"
    );
    Ok((
        filled,
        json!({"bounds_machine_mm":[left,right,fore,aft,low,high],"added_mm3":added}),
    ))
}

pub(super) fn write() -> Result<()> {
    let parts = Path::new(HERE).join("parts");
    let donor = parts.join("three-dot");
    let out = parts.join("supported-meter");
    fs::create_dir_all(&out)?;
    let source = fs::read(donor.join("meter-receiver.stl"))?;
    let mut features = reads::json(donor.join("meter-receiver.print-features.json"))?;
    let source_sha = sha(&source);
    ensure!(
        features["source_stl_sha256"] == source_sha,
        "meter feature binding changed"
    );
    let cap_sha = sha(&fs::read(donor.join("meter-snap-cap.stl"))?);
    let mesh = mesh::Mesh::from_corners(&mesh::stl_corners(&source)?);
    let vertices: Vec<V3> = mesh.vertices.iter().map(|&v| v.into()).collect();
    let faces: Vec<_> = mesh.faces.iter().map(|f| f.map(|i| i as u32)).collect();
    let receiver = facet_solid(&vertices, &faces)?;
    let scalars = reads::json("tools/hsm/shared-data/catalog/scalars.json")?;
    let relief = scalars["fits"]["supported_surface"]
        .as_f64()
        .context("supported surface allowance")?;

    let upper = region_bounds(
        &features["support_free_regions"],
        "Flow meter upper cap pocket",
    )?;
    let front = region_bounds(
        &features["support_regions"],
        "Accessible flow meter front lip",
    )?;
    let wire = region_bounds(
        &features["support_regions"],
        "Accessible flow meter wire chamber floor",
    )?;
    // Align to the end walls of the actual printed predecessor, whose STL vertices are float32.
    let [west, east, fore, aft] = [front[0], upper[1], upper[2], upper[3]].map(|v| v as f32 as f64);
    let mut outline = Vec::new();
    for f in &faces {
        let [a, b, c] = f.map(|i| vertices[i as usize]);
        let centre = (a + b + c) / 3.;
        if (b - a).cross(c - a).z > 0.
            && centre.x < east
            && centre.y > fore
            && centre.y < aft
            && centre.z > upper[4]
            && centre.z < upper[5]
        {
            outline.extend([a, b, c].map(|p| v2(p.x, p.z - relief)));
        }
    }
    outline.sort_by(|a, b| a.x.total_cmp(&b.x).then(a.y.total_cmp(&b.y)));
    outline.dedup();
    ensure!(
        outline.first().is_some_and(|p| p.x == west) && outline.last().is_some_and(|p| p.x == east),
        "profile must reach the entrance and the closing stop"
    );
    outline.extend([v2(east, upper[5] + 1.), v2(west, upper[5] + 1.)]);
    let tool = Plane::XZ
        .at(v3(0., fore, 0.))
        .extrude(&Profile::polygon(&outline), fore - aft)?;
    let revised = receiver.cut(&tool)?;
    let removed = receiver.volume() - revised.volume();
    ensure!(
        (removed - (east - west) * (aft - fore) * relief).abs() < 0.01,
        "supported-face relief must cover the complete upper cheek ({removed} mm³)"
    );
    let wire_z = (wire[4] + wire[5]) / 2.;
    let lower = region_bounds(
        &features["support_free_regions"],
        "Flow meter lower cap pocket",
    )?;
    let shelf = flat_landing(
        &vertices,
        &faces,
        [west, east, lower[2], lower[3], wire_z + 0.01, wire[5]],
    )?;
    ensure!(
        shelf[3] > wire[3],
        "long lower cheek backing must extend past the wire floor"
    );
    let wire_end = wire[3] as f32 as f64;
    let (revised, upper_splice) = fill_splice(
        &revised,
        &vertices,
        &faces,
        [upper[0], east, fore, aft, upper[4] - 3., upper[4]],
        true,
    )?;
    let boss = region_bounds(
        &features["support_regions"],
        "Accessible flow meter aft boss channel floor",
    )?;
    let (revised, lower_splice) = fill_splice(
        &revised,
        &vertices,
        &faces,
        [upper[0], east, wire_end, shelf[3], shelf[4], boss[4]],
        false,
    )?;
    let data = write_part(&out, "meter-receiver", &revised, &Affine::IDENTITY)?;
    let mut head_ledges = Vec::new();
    for end in ["fore", "aft"] {
        let name = format!("Accessible flow meter {end} screw-head channel floor");
        let [x0, x1, y0, y1, _, z] = region_bounds(&features["support_regions"], &name)?;
        head_ledges.push((
            end,
            flat_landing(&vertices, &faces, [x0, x1, y0, y1, z, upper[4]])?,
        ));
    }
    let free = features["support_free_regions"]
        .as_array_mut()
        .context("meter exclusions")?;
    free.retain(|r| r["name"] != "Flow meter upper cap pocket");
    for r in free {
        if r["name"] == "Flow meter lower cap pocket" {
            r["name"] = json!("Upward-facing long lower wing seat");
            r["reason"] = json!(
                "The long lower wing bears on a print-up face. Its opposite face is the accessible backing supported above this pocket in machine Z."
            );
        }
    }
    let targets = features["support_regions"]
        .as_array_mut()
        .context("meter targets")?;
    targets.retain(|r| r["name"] != "Accessible flow meter front lip");
    let lip_x = upper[0];
    let support_height = [upper[4] - relief, upper[5] - relief];
    for (name, x) in [
        (
            "Upper wing pilot, approach and retaining lip",
            [west, lip_x],
        ),
        (
            "Upper wing retaining shoulder and running guide",
            [lip_x, east],
        ),
    ] {
        targets.push(json!({"name":name,
            "bounds_source_mm":[x[0], x[1], fore, aft, support_height[0], support_height[1]],
            "reason":"The short upper hook prints over this crown. The open side above the receiver in machine Z lets it lift clear of the lip and out toward the west."}));
    }
    targets.push(json!({"name":"Accessible long lower hook backing",
        "bounds_source_mm":[shelf[0],shelf[1],shelf[2],wire_end,shelf[4]-relief,shelf[5]+relief],
        "reason":"Support the exposed back of the long lower hook through the open west side of the wire chamber. Past the chamber the cheek is solidly backed."}));
    for (end, [x0, x1, y0, y1, z0, z1]) in head_ledges {
        targets.push(json!({"name":format!("Accessible {end} upper screw-head recess ledge"),
            "bounds_source_mm":[x0,x1,y0,y1,z0-relief,z1+relief],
            "reason":"The flat ends of the recess widen at the curved bore. Their support pulls directly out to the west through the empty meter seat."}));
    }

    features["producer"] = json!("equipment-snap-receivers --supported-meter");
    features["source_stl_sha256"] = data["sha256"].clone();
    write_json(&out.join("meter-receiver.print-features.json"), &features)?;
    write_json(
        &out.join("geometry.json"),
        &json!({
            "purpose":"Identify the supported Digiten receiver, its existing three-dot cap and the supported-face allowance in the enclosure print orientation.",
            "previous_receiver":"../three-dot/meter-receiver.stl","previous_receiver_sha256":source_sha,
            "existing_cover":"../three-dot/meter-snap-cap.stl","existing_cover_sha256":cap_sha,
            "print_up_machine":[0,0,-1],"closing_direction_machine":[1,0,0],
            "upper_cheek_relief_machine_mm":[0.,0.,-relief],
            "upper_cheek_relief_footprint_machine_xy_mm":[west,east,fore,aft],
            "upper_cheek_removed_mm3":removed,"cover_stop_x_mm":east,
            "lower_wing_bearing_relief_mm":0.,"exposed_lower_backing_bounds_machine_mm":[shelf[0],shelf[1],shelf[2],wire_end,shelf[4],shelf[5]],
            "closed_splices":{"upper":upper_splice,"lower_aft":lower_splice},
            "mesh":data
        }),
    )
}
