//! BVH distance, ray and section queries, and Manifold volume intersections.
use crate::payload::Mesh;
use anyhow::{Result, anyhow, ensure};
use manifold_csg::{Manifold, MeshGL64};
use parry3d_f64::{
    bounding_volume::BoundingVolume,
    math::{Isometry, Point, Vector},
    query::{self, ClosestPoints, Ray, RayCast},
};
use serde::Serialize;
use std::sync::{Mutex, MutexGuard};

pub fn xyz(p: Point<f64>) -> [f64; 3] {
    [p.x, p.y, p.z]
}

fn pose(by: [f64; 3]) -> Isometry<f64> {
    Isometry::translation(by[0], by[1], by[2])
}

impl Mesh {
    pub fn face(&self, triangle: u32) -> Option<usize> {
        let i = self.faces.partition_point(|r| r[1] < triangle);
        self.faces.get(i).filter(|r| r[0] <= triangle).map(|_| i)
    }

    pub fn bounds(&self, by: [f64; 3]) -> ([f64; 3], [f64; 3]) {
        let b = self.shape.local_aabb().transform_by(&pose(by));
        (xyz(b.mins), xyz(b.maxs))
    }

    pub fn solid(&self) -> Result<MutexGuard<'_, Manifold>> {
        let held = self.solid.get_or_init(|| {
            let vertices: Vec<_> = self
                .shape
                .vertices()
                .iter()
                .flat_map(|p| [p.x, p.y, p.z])
                .collect();
            let indices: Vec<_> = self
                .shape
                .indices()
                .iter()
                .flatten()
                .map(|&i| i as u64)
                .collect();
            // Viewer vertices are split at face boundaries. Manifold joins
            // coincident seam vertices before checking that the surface closes.
            let gl = MeshGL64::new(&vertices, 3, &indices).map_err(|e| e.to_string())?;
            Manifold::from_meshgl64(&gl.merge())
                .map(Mutex::new)
                .map_err(|e| e.to_string())
        });
        match held {
            Ok(solid) => solid.lock().map_err(|_| anyhow!("solid lock poisoned")),
            Err(e) => Err(anyhow!(
                "{} cannot form a closed Manifold solid: {e}",
                self.name
            )),
        }
    }
}

/// Intersection volume includes containment. A zero-volume contact is not penetration.
pub fn overlap(a: &Mesh, b: &Mesh, by: [f64; 3]) -> Result<f64> {
    if !a
        .shape
        .local_aabb()
        .transform_by(&pose(by))
        .intersects(&b.shape.local_aabb())
    {
        return Ok(0.0);
    }
    // Take independent clones so even the same mesh may be queried against itself.
    let left = a.solid()?.translate(by[0], by[1], by[2]);
    let right = b.solid()?.translate(0.0, 0.0, 0.0);
    let result = left.intersection(&right);
    result
        .status()
        .map_err(|e| anyhow!("intersection failed: {e}"))?;
    let volume = result.volume();
    ensure!(
        volume.is_finite() && volume >= 0.0,
        "invalid intersection volume {volume}"
    );
    Ok(volume)
}

#[derive(Serialize)]
pub struct Gap {
    /// Minimum distance between triangle surfaces; positive for a contained body.
    pub surface_distance_mm: f64,
    pub point_a: Option<[f64; 3]>,
    pub point_b: Option<[f64; 3]>,
    pub intersection_volume_mm3: Option<f64>,
    /// Zero for solid penetration, otherwise the surface distance. None when
    /// containment cannot be established on an invalid solid.
    pub clearance_mm: Option<f64>,
    pub volume_error: Option<String>,
}

pub fn gap(a: &Mesh, b: &Mesh, by: [f64; 3]) -> Result<Gap> {
    let (distance, pa, pb) = match query::closest_points(
        &pose(by),
        &a.shape,
        &Isometry::identity(),
        &b.shape,
        f64::MAX,
    )
    .map_err(|_| anyhow!("unsupported triangle distance query"))?
    {
        ClosestPoints::WithinMargin(pa, pb) => ((pa - pb).norm(), Some(xyz(pa)), Some(xyz(pb))),
        ClosestPoints::Intersecting => (0.0, None, None),
        ClosestPoints::Disjoint => return Err(anyhow!("no closest triangle pair")),
    };
    // Disjoint AABBs establish separation without needing closed solids.
    let intersects = a
        .shape
        .local_aabb()
        .transform_by(&pose(by))
        .intersects(&b.shape.local_aabb());
    let volume = if intersects {
        overlap(a, b, by)
    } else {
        Ok(0.0)
    };
    let (volume, error) = match volume {
        Ok(v) => (Some(v), None),
        Err(e) => (None, Some(e.to_string())),
    };
    let clearance = if distance == 0.0 || volume.is_some_and(|v| v > 0.0) {
        Some(0.0)
    } else if volume.is_some() {
        Some(distance)
    } else {
        None
    };
    Ok(Gap {
        surface_distance_mm: distance,
        point_a: pa,
        point_b: pb,
        intersection_volume_mm3: volume,
        clearance_mm: clearance,
        volume_error: error,
    })
}

#[derive(Serialize)]
pub struct Hit {
    pub distance_mm: f64,
    pub point: [f64; 3],
    pub normal: [f64; 3],
    pub triangle: Option<u32>,
    pub face: Option<usize>,
}

pub fn ray(mesh: &Mesh, origin: [f64; 3], direction: [f64; 3], max: f64) -> Result<Option<Hit>> {
    let direction = Vector::from(direction);
    ensure!(
        direction.norm() > 0.0 && direction.norm().is_finite() && max > 0.0,
        "ray needs a direction and positive maximum distance"
    );
    let ray = Ray::new(Point::from(origin), direction.normalize());
    Ok(mesh
        .shape
        .cast_local_ray_and_get_normal(&ray, max, false)
        .map(|hit| {
            let triangle = match hit.feature {
                parry3d_f64::shape::FeatureId::Face(i) => {
                    Some(i % mesh.shape.indices().len() as u32)
                }
                _ => None,
            };
            Hit {
                distance_mm: hit.time_of_impact,
                point: xyz(ray.point_at(hit.time_of_impact)),
                normal: hit.normal.into(),
                triangle,
                face: triangle.and_then(|i| mesh.face(i)),
            }
        }))
}

#[derive(Serialize)]
pub struct Segment {
    pub points: [[f64; 3]; 2],
    pub triangle: u32,
    pub face: Option<usize>,
}

#[derive(Serialize)]
pub struct Section {
    pub normal: [f64; 3],
    pub offset_mm: f64,
    pub segments: Vec<Segment>,
    pub coplanar_triangles: Vec<u32>,
}

/// Intersect n.dot(point) = offset. Raw triangle segments retain face provenance.
pub fn section(mesh: &Mesh, normal: [f64; 3], offset: f64) -> Result<Section> {
    let n = Vector::from(normal);
    let length = n.norm();
    ensure!(
        length > 0.0 && length.is_finite(),
        "section normal must have a finite nonzero length"
    );
    let n = n / length;
    let offset = offset / length;
    let mut result = Section {
        normal: n.into(),
        offset_mm: offset,
        segments: vec![],
        coplanar_triangles: vec![],
    };
    let tolerance = 1e-9;
    let candidates = mesh
        .shape
        .bvh()
        .leaves(|node: &parry3d_f64::partitioning::BvhNode| {
            let bounds = node.aabb();
            let c = bounds.center();
            let h = bounds.half_extents();
            (n.dot(&c.coords) - offset).abs() <= n.abs().dot(&h) + tolerance
        });
    for i in candidates {
        let t = mesh.shape.triangle(i);
        let p = [t.a, t.b, t.c];
        let d = p.map(|v| n.dot(&v.coords) - offset);
        if d.iter().all(|v| v.abs() <= tolerance) {
            result.coplanar_triangles.push(i);
            continue;
        }
        let mut points = Vec::new();
        for e in 0..3 {
            let j = (e + 1) % 3;
            if d[e].abs() <= tolerance {
                points.push(p[e]);
            }
            if (d[e] < -tolerance && d[j] > tolerance) || (d[e] > tolerance && d[j] < -tolerance) {
                points.push(p[e] + (p[j] - p[e]) * (d[e] / (d[e] - d[j])));
            }
        }
        points.dedup_by(|a, b| (*a - *b).norm() <= tolerance);
        if points.len() >= 2 && (points[0] - points[1]).norm() > tolerance {
            result.segments.push(Segment {
                points: [xyz(points[0]), xyz(points[1])],
                triangle: i,
                face: mesh.face(i),
            });
        }
    }
    result.segments.sort_by_key(|s| s.triangle);
    result.coplanar_triangles.sort_unstable();
    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;
    use parry3d_f64::shape::TriMesh;
    use std::sync::OnceLock;

    fn cube(size: f64, at: [f64; 3]) -> Mesh {
        let solid = Manifold::cube(size, size, size, true).translate(at[0], at[1], at[2]);
        let (pos, stride, idx) = solid.to_mesh_f64();
        let points = pos
            .chunks_exact(stride)
            .map(|p| Point::new(p[0], p[1], p[2]))
            .collect();
        let indices: Vec<_> = idx
            .chunks_exact(3)
            .map(|t| [t[0] as u32, t[1] as u32, t[2] as u32])
            .collect();
        let faces = (0..indices.len() as u32).map(|i| [i, i]).collect();
        Mesh {
            name: "cube".into(),
            color: None,
            shape: TriMesh::new(points, indices).unwrap(),
            faces,
            solid: OnceLock::new(),
        }
    }

    fn near(a: f64, b: f64) {
        assert!((a - b).abs() < 1e-8, "{a} != {b}");
    }

    #[test]
    fn separation_and_witnesses() {
        let (a, b) = (cube(2.0, [0.0; 3]), cube(2.0, [5.0, 0.0, 0.0]));
        let g = gap(&a, &b, [0.0; 3]).unwrap();
        near(g.surface_distance_mm, 3.0);
        near(g.clearance_mm.unwrap(), 3.0);
        near(g.intersection_volume_mm3.unwrap(), 0.0);
        near(g.point_b.unwrap()[0] - g.point_a.unwrap()[0], 3.0);
    }

    #[test]
    fn containment_is_not_clearance() {
        let (outer, inner) = (cube(10.0, [0.0; 3]), cube(2.0, [0.0; 3]));
        let g = gap(&outer, &inner, [0.0; 3]).unwrap();
        near(g.surface_distance_mm, 4.0);
        near(g.clearance_mm.unwrap(), 0.0);
        near(g.intersection_volume_mm3.unwrap(), 8.0);
    }

    #[test]
    fn touching_and_translated_intersection() {
        let (a, b) = (cube(2.0, [0.0; 3]), cube(2.0, [2.0, 0.0, 0.0]));
        near(overlap(&a, &b, [0.0; 3]).unwrap(), 0.0);
        near(overlap(&a, &b, [1.0, 0.0, 0.0]).unwrap(), 4.0);
        near(overlap(&a, &a, [0.0; 3]).unwrap(), 8.0);
        near(overlap(&a, &b, [0.0; 3]).unwrap(), 0.0);
    }

    #[test]
    fn open_surfaces_cannot_report_a_solid_clearance() {
        let shape = TriMesh::new(
            vec![
                Point::new(-1.0, -1.0, 0.0),
                Point::new(1.0, -1.0, 0.0),
                Point::new(0.0, 1.0, 0.0),
            ],
            vec![[0, 1, 2]],
        )
        .unwrap();
        let open = Mesh {
            name: "open".into(),
            color: None,
            shape,
            faces: vec![[0, 0]],
            solid: OnceLock::new(),
        };
        let enclosed = cube(0.2, [0.0, 0.0, 0.3]);
        let g = gap(&open, &enclosed, [0.0; 3]).unwrap();
        // AABBs disjoint: surface separation is established even for open meshes.
        near(g.clearance_mm.unwrap(), 0.2);
        assert!(overlap(&open, &cube(2.0, [0.0; 3]), [0.0; 3]).is_err());
    }

    #[test]
    fn rays_keep_triangle_ids_on_both_sides() {
        let mesh = cube(2.0, [0.0; 3]);
        let front = ray(&mesh, [0.0, 0.0, 3.0], [0.0, 0.0, -5.0], 10.0)
            .unwrap()
            .unwrap();
        near(front.distance_mm, 2.0);
        let back = ray(&mesh, [0.0; 3], [0.0, 0.0, 1.0], 10.0)
            .unwrap()
            .unwrap();
        near(back.distance_mm, 1.0);
        for hit in [front, back] {
            assert!((hit.triangle.unwrap() as usize) < mesh.shape.indices().len());
            assert!(hit.face.is_some());
        }
    }

    #[test]
    fn sections_handle_crossings_coplanar_faces_and_scaled_planes() {
        let mesh = cube(2.0, [0.0; 3]);
        let section = section(&mesh, [0.0, 0.0, 2.0], 0.0).unwrap();
        near(
            section
                .segments
                .iter()
                .map(|s| (Point::from(s.points[1]) - Point::from(s.points[0])).norm())
                .sum(),
            8.0,
        );
        assert!(
            section
                .segments
                .iter()
                .all(|s| s.points.iter().all(|p| p[2].abs() < 1e-9))
        );
        assert_eq!(
            super::section(&mesh, [0.0, 0.0, 1.0], 1.0)
                .unwrap()
                .coplanar_triangles
                .len(),
            2
        );
        assert!(super::section(&mesh, [0.0; 3], 0.0).is_err());
    }
}
