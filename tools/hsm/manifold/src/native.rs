//! The native boundary uses Manifold for production mesh booleans.
use anyhow::Result;
use manifold_csg::Manifold as Engine;
pub use manifold_csg::{MeshGL, MeshGL64, MeshGL64Options, MeshGLOptions, OpType, reserve_ids};
use std::sync::Arc;

/// Shared ownership keeps retained construction solids cheap to clone.
#[derive(Clone)]
pub struct Manifold(Arc<Engine>);

impl Manifold {
    pub fn status(&self) -> Result<()> {
        self.0.status()?;
        Ok(())
    }
    pub fn from_meshgl(mesh: &MeshGL) -> Result<Self> {
        Ok(Self(Arc::new(Engine::from_meshgl(mesh)?)))
    }
    pub fn from_meshgl64(mesh: &MeshGL64) -> Result<Self> {
        Ok(Self(Arc::new(Engine::from_meshgl64(mesh)?)))
    }
    pub fn from_mesh_f32(vertices: &[f32], stride: usize, indices: &[u32]) -> Result<Self> {
        Ok(Self(Arc::new(Engine::from_mesh_f32(
            vertices, stride, indices,
        )?)))
    }
    pub fn from_mesh_f64(vertices: &[f64], stride: usize, indices: &[u64]) -> Result<Self> {
        Ok(Self(Arc::new(Engine::from_mesh_f64(
            vertices, stride, indices,
        )?)))
    }
    pub fn to_meshgl(&self) -> MeshGL {
        self.0.to_meshgl()
    }
    pub fn to_meshgl64(&self) -> MeshGL64 {
        self.0.to_meshgl64()
    }
    pub fn to_mesh_f32(&self) -> (Vec<f32>, usize, Vec<u32>) {
        self.0.to_mesh_f32()
    }
    pub fn to_mesh_f64(&self) -> (Vec<f64>, usize, Vec<u64>) {
        self.0.to_mesh_f64()
    }
    pub fn batch_boolean(shapes: &[Self], op: OpType) -> Self {
        let operands = shapes
            .iter()
            .map(|shape| (*shape.0).clone())
            .collect::<Vec<_>>();
        Self(Arc::new(Engine::batch_boolean(&operands, op)))
    }
    pub fn batch_union(shapes: &[Self]) -> Self {
        Self::batch_boolean(shapes, OpType::Add)
    }
    pub fn union(&self, other: &Self) -> Self {
        Self(Arc::new(self.0.union(&other.0)))
    }
    pub fn difference(&self, other: &Self) -> Self {
        Self(Arc::new(self.0.difference(&other.0)))
    }
    pub fn intersection(&self, other: &Self) -> Self {
        Self(Arc::new(self.0.intersection(&other.0)))
    }
    pub fn split(&self, cutter: &Self) -> (Self, Self) {
        let (inside, outside) = self.0.split(&cutter.0);
        (Self(Arc::new(inside)), Self(Arc::new(outside)))
    }
    pub fn split_by_plane(&self, normal: [f64; 3], offset: f64) -> (Self, Self) {
        let (positive, negative) = self.0.split_by_plane(normal, offset);
        (Self(Arc::new(positive)), Self(Arc::new(negative)))
    }
    pub fn simplify(&self, tolerance: f64) -> Self {
        Self(Arc::new(self.0.simplify(tolerance)))
    }
    pub fn as_original(&self) -> Self {
        Self(Arc::new(self.0.as_original()))
    }
    pub fn decompose(&self) -> Vec<Self> {
        self.0
            .decompose()
            .into_iter()
            .map(|shape| Self(Arc::new(shape)))
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
        self.0
            .bounding_box()
            .map(|bounds| (bounds.min(), bounds.max()))
    }
    /// Affine frames use column-major axes followed by translation.
    pub fn transform(&self, matrix: &[f64; 12]) -> Self {
        Self(Arc::new(self.0.transform(matrix)))
    }
    pub fn cube(x: f64, y: f64, z: f64, center: bool) -> Self {
        Self(Arc::new(Engine::cube(x, y, z, center)))
    }
    pub fn sphere(radius: f64, segments: usize) -> Self {
        Self(Arc::new(Engine::sphere(radius, segments as i32)))
    }
    pub fn translate(&self, x: f64, y: f64, z: f64) -> Self {
        Self(Arc::new(self.0.translate(x, y, z)))
    }
    pub fn rotate(&self, x: f64, y: f64, z: f64) -> Self {
        Self(Arc::new(self.0.rotate(x, y, z)))
    }
}
