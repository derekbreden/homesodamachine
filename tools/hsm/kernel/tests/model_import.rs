use anyhow::Result;
use hsm_kernel::{face::Face, import, math::v3, plane::Plane, step::model_bytes, write::{Body, face_json}};
use serde_json::json;
use sha2::{Digest, Sha256};
use std::io::{Cursor, Read, Write};

#[test]
fn a_model_preserves_f64_geometry_identity_and_face_records() -> Result<()> {
    let outer = Plane::XY.cuboid(20.0, 10.0, 5.0);
    let hole = Plane::XY.cylinder(2.0, 8.0)?;
    let part = outer.cut(&hole)?.translate(v3(0.123456789123, 0.234567891234, 0.345678912345));
    let bytes = model_bytes(&[Body { name: "part", color: Some([0.1, 0.2, 0.3]), solid: &part }]);
    let bodies = import::model_bodies(&bytes)?;
    let body = &bodies[0];
    assert_eq!(body.name, "part");
    assert_eq!(body.color, Some([0.1, 0.2, 0.3]));
    assert_eq!(body.solid.verts(), part.verts());
    assert_eq!(body.solid.tris(), part.tris());
    assert_eq!(body.solid.face_of(), part.face_of());
    let before: Vec<_> = part.faces().iter().map(face_json).collect();
    let after: Vec<_> = body.solid.faces().iter().map(face_json).collect();
    assert_eq!(after, before);
    assert!(after.iter().any(|f| f.get("via").is_some()));
    assert!(after.iter().all(|f| f["src"].as_str().unwrap().starts_with("tools/hsm/kernel/tests/")));
    assert_eq!(model_bytes(&[Body { name: &body.name, color: body.color, solid: &body.solid }]), bytes);
    Ok(())
}

#[test]
fn file_and_compressed_model_reads_preserve_the_same_bodies() -> Result<()> {
    let block = Plane::XY.cuboid(3.0, 4.0, 5.0);
    let bytes = model_bytes(&[Body { name: "block", color: None, solid: &block }]);
    let path = std::env::temp_dir().join(format!("hsm-model-{}.npz", std::process::id()));
    std::fs::write(&path, &bytes)?;
    let imported = import::model(&path);
    std::fs::remove_file(path)?;
    assert_eq!(imported?[0].solid.verts(), block.verts());

    let mut source = zip::ZipArchive::new(Cursor::new(bytes))?;
    let mut compressed = zip::ZipWriter::new(Cursor::new(Vec::new()));
    for i in 0..source.len() {
        let mut file = source.by_index(i)?;
        compressed.start_file(file.name()?, zip::write::SimpleFileOptions::default()
            .compression_method(zip::CompressionMethod::Deflated))?;
        let mut data = Vec::new();
        file.read_to_end(&mut data)?;
        compressed.write_all(&data)?;
    }
    let bytes = compressed.finish()?.into_inner();
    let read = import::model_bodies(&bytes)?;
    assert_eq!(read[0].name, "block");
    assert_eq!(read[0].solid.verts(), block.verts());
    Ok(())
}

#[test]
fn a_model_file_read_records_its_actual_digest_for_the_part_store() -> Result<()> {
    let block = Plane::XY.cuboid(3.0, 4.0, 5.0);
    let bytes = model_bytes(&[Body { name: "block", color: None, solid: &block }]);
    let dir = std::env::temp_dir().join(format!("hsm-model-reads-{}", std::process::id()));
    std::fs::create_dir_all(&dir)?;
    let model = dir.join("block.npz");
    let log = dir.join("reads.txt");
    std::fs::write(&model, &bytes)?;
    let child = std::process::Command::new(std::env::current_exe()?)
        .args(["--exact", "model_read_child", "--nocapture"])
        .env("HSM_MODEL_READ_TEST", &model).env("HSM_READS", &log).output()?;
    assert!(child.status.success(), "{}", String::from_utf8_lossy(&child.stderr));
    let recorded = std::fs::read_to_string(&log)?;
    assert!(recorded.starts_with("hsm-reads 1\n"));
    assert!(recorded.lines().any(|line| line == format!("{}\t{:x}", model.display(), Sha256::digest(&bytes))));
    std::fs::remove_dir_all(dir)?;
    Ok(())
}

#[test]
fn model_read_child() -> Result<()> {
    if let Some(path) = std::env::var_os("HSM_MODEL_READ_TEST") { import::model(path)?; }
    Ok(())
}

#[test]
fn every_recorded_surface_and_source_round_trips() -> Result<()> {
    for surface in [
        json!({"kind":"PLANE","p":[1.0,2.0,3.0],"n":[0.0,0.0,1.0]}),
        json!({"kind":"CYLINDER","p":[1.0,2.0,3.0],"d":[0.0,0.0,1.0],"r":2.0}),
        json!({"kind":"CONE","p":[1.0,2.0,3.0],"d":[0.0,0.0,1.0],"r":2.0,"slope":0.25}),
        json!({"kind":"SPHERE","c":[1.0,2.0,3.0],"r":2.0}),
        json!({"kind":"TORUS","c":[1.0,2.0,3.0],"d":[0.0,0.0,1.0],"R":5.0,"r":2.0}),
        json!({"kind":"BSPLINE"}),
    ] {
        let mut record = surface;
        record["op"] = "builder".into();
        record["src"] = "hardware/printed-parts/example/part.rs:42".into();
        record["via"] = "cut at hardware/printed-parts/example/part.rs:53".into();
        let face = Face::from_json(&record)?;
        assert_eq!(face.src.line(), Some(42));
        assert_eq!(face.via.unwrap().src.line(), Some(53));
        assert_eq!(face_json(&face), record);
    }
    let unrecorded = json!({"kind":"BSPLINE","op":"offset","src":null});
    let face = Face::from_json(&unrecorded)?;
    assert!(!face.src.recorded());
    assert!(face.src.file().is_empty());
    assert_eq!(face_json(&face), unrecorded);
    Ok(())
}

#[test]
fn multiple_named_bodies_and_null_sources_survive_model_round_trip() -> Result<()> {
    let block = Plane::XY.cuboid(3.0, 4.0, 5.0);
    let mut faces = block.faces().to_vec();
    faces[0].src = hsm_kernel::face::unknown_src();
    let unknown = hsm_kernel::Solid::from_mesh(block.verts(), block.tris(), block.face_of(), &faces)?;
    let bytes = model_bytes(&[
        Body { name: "part/1", color: None, solid: &unknown },
        Body { name: "Ω lever", color: Some([0.25, 0.5, 0.75]), solid: &block },
    ]);
    let read = import::model_bodies(&bytes)?;
    assert_eq!(read.iter().map(|b| b.name.as_str()).collect::<Vec<_>>(), ["part/1", "Ω lever"]);
    assert_eq!(read[0].color, None);
    assert_eq!(read[1].color, Some([0.25, 0.5, 0.75]));
    assert!(read[0].solid.faces().iter().any(|f| !f.src.recorded() && face_json(f)["src"].is_null()));
    let bodies: Vec<_> = read.iter().map(|b| Body { name: &b.name, color: b.color, solid: &b.solid }).collect();
    assert_eq!(model_bytes(&bodies), bytes);
    Ok(())
}

#[test]
fn a_step_never_substitutes_an_unbound_sibling_model() -> Result<()> {
    let dir = std::env::temp_dir().join(format!("hsm-explicit-model-{}", std::process::id()));
    std::fs::create_dir_all(&dir)?;
    let block = Plane::XY.cuboid(3.0, 4.0, 5.0);
    let bodies = [Body { name: "step body", color: None, solid: &block }];
    let step = hsm_kernel::step::step_bytes(&bodies, "part")?;
    let digest = format!("{:x}", Sha256::digest(&step));
    let payload = hsm_kernel::write::payload_bytes(&bodies, Some(&digest), None);
    let other = block.translate(v3(100.123456789123, 0.0, 0.0));
    let model = model_bytes(&[Body { name: "explicit model", color: None, solid: &other }]);
    let path = dir.join("part.step");
    std::fs::write(&path, &step)?;
    std::fs::write(dir.join("part.step.mesh"), payload)?;
    std::fs::write(dir.join("part.step.npz"), model)?;
    let from_step = import::step(&path)?;
    assert_eq!(from_step[0].name, "step body");
    assert_eq!(from_step[0].solid.bounds(), block.bounds());
    let explicit = import::model(dir.join("part.step.npz"))?;
    assert_eq!(explicit[0].name, "explicit model");
    assert_eq!(explicit[0].solid.verts(), other.verts());
    let mut changed = step;
    changed.push(b'\n');
    std::fs::write(&path, changed)?;
    let rejected = import::step(&path).unwrap_err().to_string();
    assert!(rejected.contains("was not cut from it"), "{rejected}");
    std::fs::remove_dir_all(dir)?;
    Ok(())
}

#[test]
fn payload_import_keeps_supplied_face_records() -> Result<()> {
    let block = Plane::XY.cuboid(3.0, 4.0, 5.0);
    let payload = hsm_kernel::write::payload_bytes(&[Body { name: "block", color: None, solid: &block }], None, None);
    let length = u32::from_le_bytes(payload[..4].try_into()?) as usize;
    let mut header: serde_json::Value = serde_json::from_slice(&payload[4..4 + length])?;
    let faces = hsm_kernel::topo::faces(&block);
    let records: Vec<_> = faces.record.iter().map(|&i| face_json(&block.faces()[i as usize])).collect();
    header["meshes"][0]["faces"] = serde_json::to_value(&records)?;
    let mut head = serde_json::to_vec(&header)?;
    while (head.len() + 4) % 4 != 0 { head.push(b' '); }
    let mut bytes = (head.len() as u32).to_le_bytes().to_vec();
    bytes.extend(head);
    bytes.extend_from_slice(&payload[4 + length..]);
    let read = import::bodies(&bytes, "fixture")?;
    let imported: Vec<_> = read[0].solid.faces().iter().map(face_json).collect();
    assert!(records.iter().all(|record| imported.contains(record)));
    Ok(())
}

#[test]
fn fine_model_queries_cover_separation_containment_contact_and_thin_penetration() -> Result<()> {
    let a = Plane::XY.cuboid(10.0, 10.0, 10.0);
    let far = a.translate(v3(15.0, 0.0, 0.0));
    assert!((a.gap(&far)? - 5.0).abs() < 1e-9);
    assert_eq!(a.shared_volume(&far)?, 0.0);
    let inside = Plane::XY.cuboid(2.0, 2.0, 2.0).translate(v3(0.0, 0.0, 3.0));
    assert!((a.shared_volume(&inside)? - 8.0).abs() < 1e-9);
    assert_eq!(a.gap(&inside)?, 0.0);
    let contact = a.translate(v3(10.0, 0.0, 0.0));
    assert_eq!(a.shared_volume(&contact)?, 0.0);
    assert_eq!(a.gap(&contact)?, 0.0);
    let thin = a.translate(v3(10.0 - 0.00001, 0.0, 0.0));
    assert!((a.shared_volume(&thin)? - 0.001).abs() < 1e-7);
    assert_eq!(a.gap(&thin)?, 0.0);
    Ok(())
}
