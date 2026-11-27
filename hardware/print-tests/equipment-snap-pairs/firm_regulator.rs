//! Raise the water regulator cover’s fitted bearing toward its housing in the existing three-dot receiver.
use super::three_dot::mesh::{self, Mesh};
use super::{HERE, sha, write_json};
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Affine, V3, reads, v3};
use serde_json::json;
use std::{fs, path::Path};

const COVER: &str = "regulator-snap-cap";
const RECEIVER: &str = "water-regulator-receiver";
const RISE: f64 = 0.40;
const AXIS_TOLERANCE: f64 = 1e-5;

pub(super) fn write() -> Result<()> {
    let parts = Path::new(HERE).join("parts");
    let donor = parts.join("three-dot");
    let out = parts.join("firm-regulator");
    let registration = reads::json(donor.join("geometry.json"))?;
    let station = registration["stations"]
        .as_array()
        .context("equipment stations")?
        .iter()
        .find(|s| s["cover"] == COVER)
        .context("fitted water regulator cover")?;
    let frame = Affine {
        m: serde_json::from_value(station["meshes"][COVER]["assembly_to_stl_matrix_mm"].clone())?,
    };
    let layout = reads::json("hardware/manifold-layout/above-core.json")?;
    let axis = layout["rear_plumbing"]["regulator_mount"]["axis"][1]
        .as_f64()
        .context("regulator axis height")?;
    let saddle_plane = frame.point(v3(0., 0., axis)).x;
    let rise = frame.vector(V3::Z * RISE);
    ensure!(
        (rise.x - RISE).abs() < AXIS_TOLERANCE
            && rise.y.abs() < AXIS_TOLERANCE
            && rise.z.abs() < AXIS_TOLERANCE,
        "installed closing direction must be print +X"
    );

    let source = fs::read(donor.join(format!("{COVER}.stl")))?;
    let receiver = fs::read(donor.join(format!("{RECEIVER}.stl")))?;
    ensure!(
        station["meshes"][COVER]["sha256"] == sha(&source)
            && station["meshes"][RECEIVER]["sha256"] == sha(&receiver),
        "three-dot pair registration changed"
    );
    let mut cap = Mesh::from_corners(&mesh::stl_corners(&source)?);
    // The two lands at the spindle axis give the four edges of the complete bearing,
    // including the steep shoulder between the body and the outlet neck.
    let lands: Vec<_> = cap
        .faces
        .iter()
        .map(|f| f.map(|i| cap.vertices[i]))
        .filter(|f| {
            f.iter()
                .all(|p| (p[0] - saddle_plane).abs() < AXIS_TOLERANCE)
        })
        .flatten()
        .collect();
    ensure!(!lands.is_empty(), "saddle lands at the spindle axis");
    let (lo, hi) = mesh::bounds(&lands);
    let (cap_lo, _) = cap.bounds();
    let mut moves = vec![false; cap.vertices.len()];
    let mut bearing_faces = 0;
    for f in &cap.faces {
        let v = f.map(|i| cap.vertices[i]);
        let inside = v.iter().all(|p| {
            [1, 2]
                .into_iter()
                .all(|a| p[a] >= lo[a] - AXIS_TOLERANCE && p[a] <= hi[a] + AXIS_TOLERANCE)
        });
        let on =
            |axis: usize, plane: f64| v.iter().all(|p| (p[axis] - plane).abs() < AXIS_TOLERANCE);
        if inside
            && !on(0, cap_lo[0])
            && !on(1, lo[1])
            && !on(1, hi[1])
            && !on(2, lo[2])
            && !on(2, hi[2])
        {
            bearing_faces += 1;
            for &i in f {
                moves[i] = true;
            }
        }
    }
    let original_volume = cap.volume();
    for (p, &moving) in cap.vertices.iter_mut().zip(&moves) {
        if moving {
            p[0] += RISE;
        }
    }
    let added = cap.volume() - original_volume;
    ensure!(
        (added - RISE * (hi[1] - lo[1]) * (hi[2] - lo[2])).abs() < 0.001,
        "volume added must cover the full bearing footprint"
    );
    fs::create_dir_all(&out)?;
    let stl = out.join(format!("{COVER}.stl"));
    mesh::write_stl(&stl, &cap.vertices, &cap.faces)?;
    Mesh::read_stl(&stl)?.check_closed_single_body(COVER)?;

    let mut contact =
        reads::json("hardware/printed-parts/enclosure/rear-equipment-caps/contact.json")?;
    let mut selection: [[f64; 3]; 2] =
        serde_json::from_value(contact["roof"]["bounds_source_mm"].clone())?;
    for p in &mut selection {
        p[0] += RISE;
    }
    contact["roof"]["bounds_source_mm"] = json!(selection);
    write_json(&out.join("contact.json"), &contact)?;
    write_json(
        &out.join("geometry.json"),
        &json!({
            "purpose":"Register the raised water regulator bearing to the filmed three-dot cover and receiver.",
            "donor_cover":"../three-dot/regulator-snap-cap.stl","donor_cover_sha256":sha(&source),
            "existing_receiver":"../three-dot/water-regulator-receiver.stl","existing_receiver_sha256":sha(&receiver),
            "cover_sha256":sha(&fs::read(stl)?),"assembly_to_stl_matrix_mm":frame.m,
            "saddle_rise_machine_mm":[0.,0.,RISE],"saddle_rise_print_mm":rise.to_array(),
            "bearing_footprint_print_y_z_mm":[[lo[1],hi[1]],[lo[2],hi[2]]],
            "bearing_triangles":bearing_faces,"added_volume_mm3":added
        }),
    )
}
