//! hsm-manifold preserves mesh precision and construction IDs at the Rust boolean engine boundary.
use anyhow::{Result, ensure};
pub use manifold_rust::types::OpType;
use manifold_rust::{
    csg_tree::CsgNode,
    linalg::{Mat3x4, Vec3},
    manifold::Manifold as Engine,
    types::{Error, MeshGL as FloatMesh, MeshGL64 as DoubleMesh},
};

include!(concat!(env!("OUT_DIR"), "/engine_inputs.rs"));

pub const IMPLEMENTATION: &str = env!("HSM_MANIFOLD_IMPLEMENTATION");

/// Immutable engine results share their retained topology between construction stages.
#[derive(Clone)]
pub struct Manifold(Engine);

pub fn reserve_ids(count: u32) -> u32 {
    Engine::reserve_ids(count)
}

fn checked(shape: Engine) -> Result<Manifold> {
    let shape = Manifold(shape);
    shape.status()?;
    Ok(shape)
}

impl Manifold {
    pub fn status(&self) -> Result<()> {
        let status = self.0.status();
        ensure!(status == Error::NoError, "{status}");
        Ok(())
    }
    pub fn from_meshgl(mesh: &MeshGL) -> Result<Self> {
        checked(Engine::from_mesh_gl(&mesh.0))
    }
    pub fn from_meshgl64(mesh: &MeshGL64) -> Result<Self> {
        checked(Engine::from_mesh_gl64(&mesh.0))
    }
    pub fn from_mesh_f32(vertices: &[f32], stride: usize, indices: &[u32]) -> Result<Self> {
        Self::from_meshgl(&MeshGL::new(vertices, stride, indices)?)
    }
    pub fn from_mesh_f64(vertices: &[f64], stride: usize, indices: &[u64]) -> Result<Self> {
        Self::from_meshgl64(&MeshGL64::new(vertices, stride, indices)?)
    }
    pub fn to_meshgl(&self) -> MeshGL {
        MeshGL(self.0.get_mesh_gl(0))
    }
    pub fn to_meshgl64(&self) -> MeshGL64 {
        MeshGL64(self.0.get_mesh_gl64(0))
    }
    pub fn to_mesh_f32(&self) -> (Vec<f32>, usize, Vec<u32>) {
        let m = self.0.get_mesh_gl(0);
        (m.vert_properties, m.num_prop as usize, m.tri_verts)
    }
    pub fn to_mesh_f64(&self) -> (Vec<f64>, usize, Vec<u64>) {
        let m = self.0.get_mesh_gl64(0);
        (m.vert_properties, m.num_prop as usize, m.tri_verts)
    }
    /// CSG-tree reduction groups independent operands before running the binary boolean engine.
    pub fn batch_boolean(shapes: &[Self], op: OpType) -> Self {
        let nodes = shapes
            .iter()
            .map(|m| CsgNode::from_manifold(&m.0))
            .collect();
        Self(CsgNode::op_n(op, nodes).evaluate_manifold())
    }
    pub fn batch_union(shapes: &[Self]) -> Self {
        Self::batch_boolean(shapes, OpType::Add)
    }
    pub fn union(&self, other: &Self) -> Self {
        Self(self.0.union(&other.0))
    }
    pub fn difference(&self, other: &Self) -> Self {
        Self(self.0.difference(&other.0))
    }
    pub fn intersection(&self, other: &Self) -> Self {
        Self(self.0.intersection(&other.0))
    }
    pub fn split(&self, other: &Self) -> (Self, Self) {
        let (a, b) = self.0.split(&other.0);
        (Self(a), Self(b))
    }
    pub fn split_by_plane(&self, normal: [f64; 3], offset: f64) -> (Self, Self) {
        let (a, b) = self
            .0
            .split_by_plane(Vec3::new(normal[0], normal[1], normal[2]), offset);
        (Self(a), Self(b))
    }
    pub fn simplify(&self, tolerance: f64) -> Self {
        Self(self.0.simplify(tolerance))
    }
    pub fn as_original(&self) -> Self {
        Self(self.0.as_original())
    }
    pub fn decompose(&self) -> Vec<Self> {
        self.0
            .decompose()
            .into_iter()
            .map(Self)
            .collect()
    }
    pub fn volume(&self) -> f64 {
        self.0.volume()
    }
    pub fn surface_area(&self) -> f64 {
        self.0.surface_area()
    }
    pub fn num_tri(&self) -> usize {
        self.0.num_tri()
    }
    pub fn num_vert(&self) -> usize {
        self.0.num_vert()
    }
    pub fn min_gap(&self, other: &Self, limit: f64) -> f64 {
        self.0.min_gap(&other.0, limit)
    }
    pub fn bounds(&self) -> Option<([f64; 3], [f64; 3])> {
        if self.0.is_empty() {
            return None;
        }
        let b = self.0.bounding_box();
        Some(([b.min.x, b.min.y, b.min.z], [b.max.x, b.max.y, b.max.z]))
    }
    /// Affine frames use column-major axes followed by translation.
    pub fn transform(&self, matrix: &[f64; 12]) -> Self {
        let column = |i| Vec3::new(matrix[i], matrix[i + 1], matrix[i + 2]);
        Self(self.0.transform(&Mat3x4::from_cols(
            column(0),
            column(3),
            column(6),
            column(9),
        )))
    }
    pub fn cube(x: f64, y: f64, z: f64, center: bool) -> Self {
        Self(Engine::cube(Vec3::new(x, y, z), center))
    }
    pub fn sphere(radius: f64, segments: usize) -> Self {
        Self(Engine::sphere(radius, segments as i32))
    }
    pub fn translate(&self, x: f64, y: f64, z: f64) -> Self {
        Self(self.0.translate(Vec3::new(x, y, z)))
    }
    pub fn rotate(&self, x: f64, y: f64, z: f64) -> Self {
        Self(self.0.rotate(x, y, z))
    }
}

#[derive(Clone, Default)]
pub struct MeshOptions<'a, I> {
    runs: Option<(&'a [I], &'a [u32])>,
}
impl<'a, I> MeshOptions<'a, I> {
    pub fn new() -> Self {
        Self { runs: None }
    }
    pub fn runs(mut self, starts: &'a [I], ids: &'a [u32]) -> Self {
        self.runs = Some((starts, ids));
        self
    }
}
pub type MeshGLOptions<'a> = MeshOptions<'a, u32>;
pub type MeshGL64Options<'a> = MeshOptions<'a, u64>;

/// Mesh buffers retain the engine's native float and index precision across import and export.
pub struct MeshGL(FloatMesh);
pub struct MeshGL64(DoubleMesh);

macro_rules! mesh {
    ($name:ident,$raw:ident,$value:ty,$index:ty,$options:ident) => {
        impl $name {
            pub fn new(vertices: &[$value], stride: usize, indices: &[$index]) -> Result<Self> {
                Self::new_with_options(vertices, stride, indices, $options::new())
            }
            pub fn new_with_options(
                vertices: &[$value],
                stride: usize,
                indices: &[$index],
                options: $options<'_>,
            ) -> Result<Self> {
                ensure!(
                    stride >= 3 && vertices.len() % stride == 0 && indices.len() % 3 == 0,
                    "mesh buffer lengths and stride agree"
                );
                ensure!(
                    vertices.iter().all(|x| x.is_finite())
                        && indices
                            .iter()
                            .all(|&i| (i as usize) < vertices.len() / stride),
                    "mesh positions and indices are valid"
                );
                let (mut starts, mut ids) = (Vec::new(), Vec::new());
                if let Some((a, b)) = options.runs {
                    starts = a.to_vec();
                    ids = b.to_vec();
                }
                Ok(Self($raw {
                    num_prop: stride as $index,
                    vert_properties: vertices.to_vec(),
                    tri_verts: indices.to_vec(),
                    run_index: starts,
                    run_original_id: ids,
                    ..Default::default()
                }))
            }
            pub fn merge(&self) -> Self {
                let mut m = self.0.clone();
                m.merge();
                Self(m)
            }
            pub fn num_prop(&self) -> usize {
                self.0.num_prop as usize
            }
            pub fn num_tri(&self) -> usize {
                self.0.tri_verts.len() / 3
            }
            pub fn vert_properties(&self) -> Vec<$value> {
                self.0.vert_properties.clone()
            }
            pub fn tri_verts(&self) -> Vec<$index> {
                self.0.tri_verts.clone()
            }
            pub fn run_index(&self) -> Vec<$index> {
                self.0.run_index.clone()
            }
            pub fn run_original_id(&self) -> Vec<u32> {
                self.0.run_original_id.clone()
            }
        }
    };
}
mesh!(MeshGL, FloatMesh, f32, u32, MeshGLOptions);
mesh!(MeshGL64, DoubleMesh, f64, u64, MeshGL64Options);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn batch_identity_shares_mesh_without_mutating_the_input() {
        let input = Manifold::cube(10.0, 12.0, 14.0, true);
        let retained = Manifold::batch_union(std::slice::from_ref(&input));
        assert!(std::ptr::eq(input.0.as_impl(), retained.0.as_impl()));
        let placed = retained.translate(20.0, 0.0, 0.0);
        assert_eq!(input.bounds().unwrap().0[0], -5.0);
        assert_eq!(placed.bounds().unwrap().0[0], 15.0);
    }

    #[test]
    fn split_preserves_both_meshes_and_their_source_runs() {
        let input = Manifold::cube(10.0, 12.0, 14.0, true);
        let cutter = Manifold::cube(7.0, 11.0, 16.0, true);
        for cutter in [
            cutter.translate(2.5, 0.5, 0.0),
            cutter.rotate(5.0, 10.0, 15.0),
            cutter.translate(100.0, 0.0, 0.0),
            Manifold(Engine::empty()),
        ] {
            let (inside, outside) = input.split(&cutter);
            for (actual, expected) in [
                (inside, input.intersection(&cutter)),
                (outside, input.difference(&cutter)),
            ] {
                actual.status().unwrap();
                expected.status().unwrap();
                let a = actual.0.get_mesh_gl64(0);
                let b = expected.0.get_mesh_gl64(0);
                assert_eq!(a.vert_properties, b.vert_properties);
                assert_eq!(a.tri_verts, b.tri_verts);
                assert_eq!(a.run_index, b.run_index);
                assert_eq!(a.run_original_id, b.run_original_id);
                assert_eq!(a.run_transform, b.run_transform);
                assert_eq!(a.face_id, b.face_id);
            }
        }
    }
}
