//! Print conversions preserve construction identities through Manifold's existing operand runs.
use anyhow::Result;
use hsm_kernel::{Face, Solid, Surface, feature::Feature};
use manifold_csg::{Manifold, MeshGL, MeshGLOptions, reserve_ids};
use std::{collections::{BTreeMap, HashMap}, sync::{Mutex, OnceLock}};

static RUNS: Mutex<BTreeMap<u32, &'static Feature>> = Mutex::new(BTreeMap::new());

/// Explicit comparison runs omit identity bookkeeping on the same construction and engine.
pub fn enabled() -> bool {
    static ENABLED: OnceLock<bool> = OnceLock::new();
    *ENABLED.get_or_init(|| std::env::var_os("HSM_FEATURES_OFF").is_none())
}

/// The same float positions and triangles, with authored identities attached to operand runs.
pub fn manifold(solid: &Solid) -> Result<Manifold> {
    let points: Vec<f32> = solid.verts().iter().flat_map(|p| p.to_array().map(|x| x as f32)).collect();
    let triangles: Vec<u32> = solid.tris().iter().flatten().copied().collect();
    if !solid.faces().iter().any(|f| f.feature.is_some()) {
        return Ok(Manifold::from_mesh_f32(&points, 3, &triangles)?);
    }
    let mut names = HashMap::new();
    let unknown = reserve_ids(1);
    let mut records = RUNS.lock().unwrap_or_else(|e| e.into_inner());
    let mut starts = Vec::new();
    let mut ids = Vec::new();
    let face_ids: Vec<_> = solid.faces().iter().map(|face| {
        if let Some(feature) = face.feature {
            *names.entry(feature.id.as_str()).or_insert_with(|| {
                let id = reserve_ids(1); records.insert(id, feature); id
            })
        } else { unknown }
    }).collect();
    drop(records);
    for (i, &face) in solid.face_of().iter().enumerate() {
        let id = face_ids[face as usize];
        if ids.last() != Some(&id) { starts.push((i * 3) as u32); ids.push(id); }
    }
    starts.push(triangles.len() as u32);
    let mesh = MeshGL::new_with_options(&points, 3, &triangles, MeshGLOptions::new().runs(&starts, &ids))?;
    Ok(Manifold::from_meshgl(&mesh)?)
}

/// Each existing triangle's identity, in the same order used for its STL.
pub fn triangles(shape: &Manifold) -> (Vec<&'static Feature>, Vec<u32>) {
    let mesh = shape.to_meshgl();
    mesh_triangles(&mesh)
}

/// Read identity runs from the same mesh conversion already used for print output.
pub fn mesh_triangles(mesh: &MeshGL) -> (Vec<&'static Feature>, Vec<u32>) {
    let starts = mesh.run_index();
    let runs = mesh.run_original_id();
    let records = RUNS.lock().unwrap_or_else(|e| e.into_inner());
    let mut catalog = Vec::new();
    let mut names = HashMap::new();
    if records.is_empty() { return (vec![], vec![]); }
    let mut faces = vec![0; mesh.num_tri()];
    for (i, run) in runs.iter().enumerate() {
        let Some(&feature) = records.get(run) else { continue };
        let id = *names.entry(feature.id.as_str()).or_insert_with(|| { catalog.push(feature); catalog.len() as u32 });
        let a = starts[i] as usize / 3;
        let b = starts.get(i + 1).map(|n| *n as usize / 3).unwrap_or(faces.len());
        faces[a..b].fill(id);
    }
    (catalog, faces)
}

/// A retained print solid keeps construction identities beside its unchanged triangle surface.
#[track_caller]
pub fn print_solid(shape: &Manifold) -> Result<Solid> {
    let mesh = shape.to_meshgl();
    let (points, stride, triangles) = (mesh.vert_properties(), mesh.num_prop(), mesh.tri_verts());
    let points: Vec<_> = points.chunks_exact(stride).map(|p| hsm_kernel::v3(p[0] as f64, p[1] as f64, p[2] as f64)).collect();
    let triangles: Vec<_> = triangles.chunks_exact(3).map(|t| [t[0], t[1], t[2]]).collect();
    let (catalog, mut face_of) = mesh_triangles(&mesh);
    if face_of.is_empty() { face_of.resize(triangles.len(), 0); }
    let base = Face::new(Surface::Free { kind: "PRINT" }, "print surface", std::panic::Location::caller());
    let faces: Vec<_> = std::iter::once(base).chain(catalog.into_iter().map(|feature| Face { feature: Some(feature), ..base })).collect();
    Solid::from_mesh(&points, &triangles, &face_of, &faces)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn print_precision_and_retained_models_keep_identity() -> Result<()> {
        let tag = hsm_kernel::feature::intern(Feature { id: "receiver".into(), label: "Receiver".into(),
            parent: None, related: vec!["regulator".into()], source: "print-test".into() });
        let part = Solid::cuboid(hsm_kernel::v3(0.,0.,0.), hsm_kernel::v3(2.,3.,4.)).with_feature(tag);
        let shape = crate::ops::quantized(&manifold(&part)?)?;
        let retained = print_solid(&shape)?;
        assert!(retained.faces().iter().all(|f| f.feature == Some(tag)));
        let bytes = hsm_kernel::model_bytes(&[hsm_kernel::Body { name: "stage", color: None, solid: &retained }]);
        let loaded = hsm_kernel::import::model_bodies(&bytes)?.pop().unwrap().solid;
        let (features, ids) = triangles(&manifold(&loaded)?);
        assert_eq!(features, vec![tag]);
        assert!(ids.iter().all(|&id| id == 1));
        Ok(())
    }
}
