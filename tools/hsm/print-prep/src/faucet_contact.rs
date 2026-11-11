//! Map the inclined contact region for slicing and restore its paths in the physical build frame.

use anyhow::{ensure, Context, Result};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::fs;
use std::io::{Read, Write};
use std::path::Path;

use crate::faucet::{cross, members, paint_of, set_paint, sub};
use crate::gcode::{arc, words};
use crate::ids::md5_hex;
use crate::mesh::{bounds, Mesh};
use crate::project::{Object, Paint, Plate};
use crate::refresh::Refreshed;
use crate::{apply, sha256_hex};
use hsm_faucet_numbers::{paths::TOTAL_ANGLE, shell::DISPENSE_FACE_THICKNESS};

type Point = [f64; 3];
type Face = [usize; 3];
const GCODE: &str = "Metadata/plate_1.gcode";
const REVIEW: &str = "Metadata/hsm_nonplanar_contact.json";

pub struct ContactBand {
    surface: Surface,
    bounds: [[f64; 2]; 2],
    edge: f64,
    period: f64,
    phase: f64,
    bed: [f64; 2],
    full: [f64; 2],
    zero: [f64; 2],
    mesh_y: f64,
    mesh_z: f64,
    mesh_error: f64,
    refine_interiors: bool,
    support_paint: Option<SupportPaint>,
    segment: f64,
    z_print_feed: f64,
    z_travel_feed: f64,
    clearance: f64,
    retract: f64,
    retract_feed: f64,
}

enum Surface {
    Plane { normal: Point, seat: Point },
    HeightField(HeightField),
}

struct SupportPaint {
    faces: BTreeSet<usize>,
    shadows: Vec<Vec<Point>>,
}

impl SupportPaint {
    fn new(spec: &Value) -> Result<Self> {
        Ok(Self {
            faces: serde_json::from_value(spec["faces"].clone())?,
            shadows: serde_json::from_value(spec["outlet_shadows"].clone())?,
        })
    }

    fn clear(&self, face: [Point; 3]) -> bool {
        self.shadows.iter().all(|shadow| shadow.iter().any(|edge| {
            face.iter().all(|p| edge[0] * p[0] + edge[1] * p[1] >= edge[2])
        }))
    }
}

struct HeightField {
    bounds: [[f64; 2]; 2],
    samples: [usize; 2],
    heights: Vec<f64>,
    range: [f64; 2],
    release: Option<SupportRelease>,
}

struct SupportRelease {
    depth: f64,
    blend: [f64; 4],
}

impl SupportRelease {
    fn new(spec: &Value) -> Result<Self> {
        let depth = spec["depth_mm"].as_f64().context("support release depth")?;
        let blend: [f64; 4] = serde_json::from_value(spec["blend_below_roof_mm"].clone())?;
        ensure!(depth > 0. && blend[0] < blend[1] && blend[1] <= blend[2] && blend[2] < blend[3]
            && blend[3] <= 0., "invalid support release blend below the roof");
        Ok(Self { depth, blend })
    }

    fn shift(&self, distance: f64) -> f64 {
        let [lo, full_lo, full_hi, hi] = self.blend;
        self.depth * smooth((distance - lo) / (full_lo - lo)) * smooth((hi - distance) / (hi - full_hi))
    }
}

impl HeightField {
    fn new(spec: &Value, release: Option<&Value>) -> Result<Self> {
        let bounds: [[f64; 2]; 2] = serde_json::from_value(spec["bounds_mm"].clone())?;
        let samples: [usize; 2] = serde_json::from_value(spec["samples"].clone())?;
        let heights: Vec<f64> = serde_json::from_value(spec["z_mm"].clone())?;
        ensure!(samples.into_iter().all(|count| count >= 2)
            && samples[0].checked_mul(samples[1]) == Some(heights.len())
            && (0..2).all(|axis| bounds[0][axis] < bounds[1][axis])
            && heights.iter().all(|height| height.is_finite()),
            "invalid contact height field");
        let range = heights.iter().fold([f64::INFINITY, f64::NEG_INFINITY], |[lo, hi], &z| {
            [lo.min(z), hi.max(z)]
        });
        let release = release.map(SupportRelease::new).transpose()?;
        Ok(Self { bounds, samples, heights, range, release })
    }

    fn height(&self, p: Point) -> f64 {
        let [(x, u), (y, v)] = [0, 1].map(|axis| {
            let last = self.samples[axis] - 1;
            let fraction = (p[axis] - self.bounds[0][axis]) / (self.bounds[1][axis] - self.bounds[0][axis]);
            let position = fraction.clamp(0., 1.) * last as f64;
            let index = (position as usize).min(last - 1);
            (index, position - index as f64)
        });
        let lower = y * self.samples[0] + x;
        let upper = lower + self.samples[0];
        let a = self.heights[lower] * (1. - u) + self.heights[lower + 1] * u;
        let b = self.heights[upper] * (1. - u) + self.heights[upper + 1] * u;
        a * (1. - v) + b * v
    }
}

impl ContactBand {
    pub fn new(spec: &Value) -> Result<Self> {
        let parameters = &spec["parameters"];
        let number = |key: &str| parameters[key].as_f64().with_context(|| format!("contact band {key}"));
        let surface = if let Some(field) = spec.get("height_field") {
            Surface::HeightField(HeightField::new(field, parameters.get("support_release"))?)
        } else {
            let normal: Point = serde_json::from_value(spec["plane_normal"].clone())?;
            ensure!(normal[2].abs() > 0.5, "contact plane needs a vertical component");
            Surface::Plane { normal, seat: serde_json::from_value(spec["seat_plate_mm"].clone())? }
        };
        let band = Self {
            surface,
            bounds: serde_json::from_value(spec["bounds_mm"].clone())?,
            edge: spec["edge_blend_mm"].as_f64().context("contact band edge blend")?,
            period: number("band_period_mm")?,
            phase: number("band_phase_mm")?,
            bed: serde_json::from_value(parameters["bed_blend_mm"].clone())?,
            full: serde_json::from_value(parameters["contact_full_weight_mm"].clone())?,
            zero: serde_json::from_value(parameters["contact_zero_weight_mm"].clone())?,
            mesh_y: number("maximum_mesh_y_step_mm")?,
            mesh_z: number("maximum_mesh_z_step_mm")?,
            mesh_error: number("maximum_mesh_mapping_error_mm")?,
            refine_interiors: spec["refine_mesh_interiors"].as_bool().unwrap_or(false),
            support_paint: spec.get("support_paint").map(SupportPaint::new).transpose()?,
            segment: number("maximum_gcode_segment_mm")?,
            z_print_feed: number("maximum_nonplanar_z_speed_mm_s")? * 60.,
            z_travel_feed: number("travel_z_speed_mm_s")? * 60.,
            clearance: number("travel_clearance_mm")?,
            retract: number("travel_retract_mm")?,
            retract_feed: number("travel_retract_speed_mm_s")? * 60.,
        };
        ensure!(
            band.bed[0] >= 0. && band.bed[0] < band.bed[1]
                && band.zero[0] < band.full[0] && band.full[0] <= band.full[1] && band.full[1] < band.zero[1]
                && (0..2).all(|axis| band.bounds[1][axis] - band.bounds[0][axis] > 2. * band.edge)
                && [band.edge, band.period, band.mesh_y, band.mesh_z, band.mesh_error, band.segment,
                    band.z_print_feed, band.z_travel_feed, band.clearance, band.retract_feed]
                    .into_iter().all(|value| value > 0.)
                && band.retract >= 0.,
            "invalid contact band geometry or motion limits"
        );
        if let Surface::HeightField(HeightField { release: Some(release), .. }) = &band.surface {
            ensure!(band.zero[0] <= release.blend[0] && release.blend[3] <= band.zero[1],
                "support release must stay within the contact band");
        }
        Ok(band)
    }

    fn face_z(&self, p: Point) -> f64 {
        match &self.surface {
            Surface::Plane { normal, seat } => {
                seat[2] - (normal[0] * (p[0] - seat[0]) + normal[1] * (p[1] - seat[1])) / normal[2]
            }
            Surface::HeightField(field) => field.height(p),
        }
    }

    fn edge_weight(&self, p: Point) -> f64 {
        (0..2).map(|axis| smooth((p[axis] - self.bounds[0][axis]).min(self.bounds[1][axis] - p[axis]) / self.edge))
            .product()
    }

    fn offset(&self, p: Point) -> f64 {
        if p[2] <= self.bed[0] {
            return 0.;
        }
        let edge = self.edge_weight(p);
        if edge == 0. {
            return 0.;
        }
        let face = self.face_z(p);
        let d = p[2] - face;
        let contact = if d < self.full[0] {
            smooth((d - self.zero[0]) / (self.full[0] - self.zero[0]))
        } else {
            smooth((self.zero[1] - d) / (self.zero[1] - self.full[1]))
        };
        let r = (face - self.phase + self.period / 2.).rem_euclid(self.period) - self.period / 2.;
        let delta = r.signum() * r.abs().min(self.period / 2. - r.abs());
        let offset = delta * edge * contact;
        let offset = if let Surface::HeightField(HeightField { release: Some(release), .. }) = &self.surface {
            offset - release.shift(d) * edge
        } else {
            offset
        };
        offset * smooth((p[2] - self.bed[0]) / (self.bed[1] - self.bed[0]))
    }

    fn mapped(&self, mut p: Point) -> Point {
        p[2] -= self.offset(p);
        p
    }

    fn mesh_knot(&self, p: Point, q: Point) -> Option<Point> {
        if !self.refine_interiors || !matches!(self.surface, Surface::Plane { .. }) {
            return None;
        }
        let (start, end) = (self.face_z(p), self.face_z(q));
        let step = self.period / 2.;
        let first = self.phase + self.period / 4.;
        let knot = first + step * (((start + end) / 2. - first) / step).round();
        if (knot - start).abs() < 1e-6 || (knot - end).abs() < 1e-6 {
            return None;
        }
        let t = (knot - start) / (end - start);
        (1e-5..1. - 1e-5).contains(&t).then(|| mix(p, q, t))
    }

    fn restored(&self, p: Point) -> Point {
        let mut q = p;
        for _ in 0..20 {
            let z = p[2] + self.offset(q);
            if (z - q[2]).abs() < 1e-10 {
                break;
            }
            q[2] = z;
        }
        q
    }

    fn interval(&self, a: Point, b: Point, padding: f64) -> bool {
        if a[2].max(b[2]) <= self.bed[0]
            || (0..2).any(|axis| a[axis].max(b[axis]) <= self.bounds[0][axis]
                || a[axis].min(b[axis]) >= self.bounds[1][axis])
        {
            return false;
        }
        if let Surface::HeightField(field) = &self.surface {
            return a[2].min(b[2]) - field.range[1] < self.zero[1] + padding
                && a[2].max(b[2]) - field.range[0] > self.zero[0] - padding;
        }
        let da = a[2] - self.face_z(a);
        let db = b[2] - self.face_z(b);
        da.min(db) < self.zero[1] + padding && da.max(db) > self.zero[0] - padding
    }

    /// Carry model, support geometry, modifiers and facet paint into the common slicing frame.
    pub fn warp_object(&self, object: &mut Object) -> Result<Value> {
        let r = object.rotation;
        let t = object.translation;
        let mut review = BTreeMap::new();
        review.insert(object.name.clone(), self.warp_mesh(&mut object.vertices, &mut object.faces, &mut object.paint, r, t, self.support_paint.as_ref())
            .with_context(|| format!("mapping {}", object.name))?);
        for part in &mut object.parts {
            review.insert(part.name.clone(), self.warp_mesh(&mut part.vertices, &mut part.faces, &mut part.paint, r, t, None)
                .with_context(|| format!("mapping {}", part.name))?);
        }
        Ok(json!(review))
    }

    /// Slice and cool in the mapped frame, then keep the actual model and paths in the final archive.
    pub fn slice_project(&self, plate: &mut Plate, object: usize, project: &Path, directory: &Path, slicer: &Path) -> Result<Value> {
        Self::slice_bands(plate, &[(object, self)], project, directory, slicer)
    }

    /// Slice a plate with contact regions on distinct objects in the same native run.
    pub fn slice_bands(plate: &mut Plate, scopes: &[(usize, &Self)], project: &Path, directory: &Path,
                       slicer: &Path) -> Result<Value> {
        ensure!(!directory.exists() || fs::read_dir(directory)?.next().is_none(),
            "the contact slice directory must be empty");
        ensure!(!scopes.is_empty(), "the contact slice needs a contact region");
        for (i, (object, band)) in scopes.iter().enumerate() {
            ensure!(scopes[..i].iter().all(|(other, their_band)| {
                other != object && (0..2).any(|axis| band.bounds[0][axis] >= their_band.bounds[1][axis]
                    || band.bounds[1][axis] <= their_band.bounds[0][axis])
            }), "contact regions on one plate must have distinct objects and XY footprints");
        }
        let native = directory.join("mapped-slice");
        fs::create_dir_all(&native)?;
        let source = native.join(project.file_name().context("contact project filename")?);
        let archive_name = format!("{}.gcode.3mf", project.file_stem().context("contact project stem")?.to_string_lossy());
        let mut geometry = BTreeMap::new();
        for &(object, band) in scopes {
            let object = &mut plate.objects[object];
            geometry.insert(object.name.clone(), band.warp_object(object)?);
        }
        fs::write(directory.join("contact-geometry.json"), serde_json::to_vec_pretty(&geometry)?)?;
        plate.write(&source)?;
        crate::slice::run(slicer, &source, &native)?;
        crate::slice::apply_directory(&native, &source)?;
        let archive = directory.join(&archive_name);
        let bands: Vec<_> = scopes.iter().map(|&(_, band)| band).collect();
        let mut report = Self::restore_bands(&bands, project, &native.join(archive_name), &archive)?;
        fs::write(directory.join("plate_1.gcode"), crate::gcode::plate_gcode(&archive)?)?;
        write_motion_result(&native.join("result.json"), &directory.join("result.json"),
            report["added_commanded_motion_seconds"].as_f64().context("contact motion time")?)?;
        report["geometry"] = json!(geometry);
        report["archive"] = json!(archive);
        fs::write(directory.join("contact-motion.json"), serde_json::to_vec_pretty(&report)?)?;
        Ok(report)
    }

    fn warp_mesh(&self, vertices: &mut Vec<Point>, faces: &mut Vec<Face>, paint: &mut Option<Vec<Paint>>,
                 rotation: [[f64; 3]; 3], translation: Point, support_paint: Option<&SupportPaint>) -> Result<Value> {
        let mut world: Vec<Point> = vertices.iter().map(|p| add(apply(&rotation, *p), translation)).collect();
        let original_count = faces.len();
        let mut parents: Vec<usize> = (0..original_count).collect();
        let rounds = if self.refine_interiors { 28 } else { 18 };
        for _ in 0..rounds {
            let mut splits = HashMap::new();
            for (&[a, b, c], parent) in faces.iter().zip(&parents) {
                let refine_paint = support_paint.is_some_and(|selection| selection.faces.contains(parent));
                let refine_interior = self.refine_interiors && {
                    let [pa, pb, pc] = [world[a], world[b], world[c]];
                    let center = mix(mix(pa, pb, 0.5), pc, 1. / 3.);
                    let estimated_center = (self.mapped(pa)[2] + self.mapped(pb)[2] + self.mapped(pc)[2]) / 3.;
                    (self.mapped(center)[2] - estimated_center).abs() > self.mesh_error * 2.
                };
                for (u, v) in [edge(a, b), edge(b, c), edge(c, a)] {
                    if splits.contains_key(&(u, v)) {
                        continue;
                    }
                    let (p, q) = (world[u], world[v]);
                    if !refine_interior && !self.interval(p, q, 0.) {
                        continue;
                    }
                    if let Some(knot) = self.mesh_knot(p, q) {
                        splits.insert((u, v), world.len());
                        world.push(knot);
                        continue;
                    }
                    let mid = mix(p, q, 0.5);
                    let error = (self.mapped(mid)[2] - (self.mapped(p)[2] + self.mapped(q)[2]) / 2.).abs();
                    let x_edge = p[0].min(q[0]) < self.bounds[0][0] + self.edge
                        || p[0].max(q[0]) > self.bounds[1][0] - self.edge;
                    let curved_x = matches!(self.surface, Surface::HeightField(_)) && (p[0] - q[0]).abs() > self.mesh_y;
                    if refine_interior || error > self.mesh_error || (p[1] - q[1]).abs() > self.mesh_y
                        || (p[2] - q[2]).abs() > self.mesh_z || (x_edge && (p[0] - q[0]).abs() > self.edge) || curved_x
                        || (refine_paint && (p[0] - q[0]).abs() > self.mesh_y)
                    {
                        splits.insert((u, v), world.len());
                        world.push(mid);
                    }
                }
            }
            if splits.is_empty() {
                break;
            }
            let mut refined = Vec::with_capacity(faces.len() * 2);
            let mut refined_parents = Vec::with_capacity(faces.len() * 2);
            for (&[a, b, c], &parent) in faces.iter().zip(&parents) {
                let from = refined.len();
                match [edge(a, b), edge(b, c), edge(c, a)].map(|key| splits.get(&key).copied()) {
                    [None, None, None] => refined.push([a, b, c]),
                    [Some(m), None, None] => refined.extend([[a, m, c], [m, b, c]]),
                    [None, Some(m), None] => refined.extend([[b, m, a], [m, c, a]]),
                    [None, None, Some(m)] => refined.extend([[c, m, b], [m, a, b]]),
                    [Some(m), Some(n), None] => refined.extend([[m, b, n], [a, m, c], [m, n, c]]),
                    [None, Some(m), Some(n)] => refined.extend([[m, c, n], [b, m, a], [m, n, a]]),
                    [Some(n), None, Some(m)] => refined.extend([[m, a, n], [c, m, b], [m, n, b]]),
                    [Some(ab), Some(bc), Some(ca)] => refined.extend([[a, ab, ca], [ab, b, bc], [ca, bc, c], [ab, bc, ca]]),
                }
                refined_parents.resize(refined_parents.len() + refined.len() - from, parent);
            }
            ensure!(refined.len() < 3_000_000, "contact band mesh refinement did not converge");
            *faces = refined;
            parents = refined_parents;
        }
        let mapped: Vec<Point> = world.iter().map(|p| self.mapped(*p)).collect();
        let mut max_shift = 0.0_f64;
        let mut max_roundtrip = 0.0_f64;
        let mut min_jacobian = 1.0_f64;
        for (&original, &warped) in world.iter().zip(&mapped) {
            let shift = (original[2] - warped[2]).abs();
            max_shift = max_shift.max(shift);
            if shift > 1e-9 {
                max_roundtrip = max_roundtrip.max((self.restored(warped)[2] - original[2]).abs());
                let hi = self.mapped(add(original, [0., 0., 0.001]))[2];
                let lo = self.mapped(add(original, [0., 0., -0.001]))[2];
                min_jacobian = min_jacobian.min((hi - lo) / 0.002);
            }
        }
        let mut max_error = 0.0_f64;
        for &[a, b, c] in faces.iter() {
            let center = mix(mix(world[a], world[b], 0.5), world[c], 1. / 3.);
            let approximation = mix(mix(mapped[a], mapped[b], 0.5), mapped[c], 1. / 3.);
            max_error = max_error.max((self.restored(approximation)[2] - center[2]).abs());
        }
        ensure!(max_roundtrip < 1e-5 && min_jacobian > 0.65 && max_error < 0.012,
            "contact geometry mapping error {max_error:.5}, roundtrip {max_roundtrip:.5}, Jacobian {min_jacobian:.5}");
        let inverse = [0, 1, 2].map(|axis| [0, 1, 2].map(|other| rotation[other][axis]));
        *vertices = mapped.into_iter().map(|p| apply(&inverse, sub(p, translation))).collect();
        let mut marked_area = 0.;
        if let Some(original) = paint.as_mut() {
            *original = faces.iter().zip(&parents).map(|(face, &parent)| {
                let mut next = original[parent].clone();
                if let Some(selection) = support_paint.filter(|s| s.faces.contains(&parent)) {
                    let [a, b, c] = face.map(|i| world[i]);
                    let clear = selection.clear([a, b, c]);
                    if clear {
                        marked_area += distance(cross(sub(b, a), sub(c, a)), [0.; 3]) / 2.;
                    }
                    set_paint(&mut next, "paint_supports", if clear { "4" } else { "8" });
                }
                next
            }).collect();
        }
        Ok(json!({"source_triangles": original_count, "slice_triangles": faces.len(),
            "maximum_shift_mm": max_shift, "maximum_roundtrip_error_mm": max_roundtrip,
            "minimum_sampled_jacobian": min_jacobian, "maximum_facet_restoration_error_mm": max_error,
            "scoped_support_paint_area_mm2": marked_area}))
    }

    /// Restore the cooled plate in an archive that contains the actual, unwarped product meshes.
    pub fn restore_archive(&self, physical: &Path, native: &Path, output: &Path) -> Result<Value> {
        Self::restore_bands(&[self], physical, native, output)
    }

    fn restore_bands(bands: &[&Self], physical: &Path, native: &Path, output: &Path) -> Result<Value> {
        ensure!(output != physical && output != native, "restored archive needs its own path");
        let physical = members(physical)?;
        let mut archive = zip::ZipArchive::new(fs::File::open(native)?)?;
        let native_gcode = read_member(&mut archive, GCODE)?;
        let (gcode, mut review) = Self::restore_paths(bands, &native_gcode)?;
        review["gcode_input_sha256"] = json!(sha256_hex(&native_gcode));
        review["gcode_sha256"] = json!(sha256_hex(&gcode));
        let mut replaced = physical.into_iter().filter(|(name, _)| {
            name.starts_with("3D/") || name == "Metadata/model_settings.config"
        }).collect::<BTreeMap<_, _>>();
        replaced.insert(format!("{GCODE}.md5"), md5_hex(&gcode).into_bytes());
        replaced.insert(GCODE.to_string(), gcode);
        replace_prediction(&mut archive, &mut replaced, review["added_commanded_motion_seconds"].as_f64().context("contact motion time")?)?;
        replaced.insert(REVIEW.to_string(), serde_json::to_vec_pretty(&review)?);
        write_archive(archive, replaced, output, true)?;
        review["archive_sha256"] = json!(sha256_hex(&fs::read(output)?));
        Ok(review)
    }

    fn restore_paths(bands: &[&Self], input: &[u8]) -> Result<(Vec<u8>, Value)> {
        let mut motion = Motion::new(input.len());
        let mut deposited = vec![0; bands.len()];
        for line in std::str::from_utf8(input)?.lines() {
            motion.line(bands, &mut deposited, line)?;
        }
        ensure!(deposited.iter().all(|count| *count > 0), "a contact band contains no restored extrusion");
        Ok((motion.out, json!({"purpose": "Read the bounded restored movements of the full print.",
            "mapped_deposition_segments": motion.shifted_roads, "lifted_travels": motion.lifted_travels,
            "mapped_deposition_segments_by_region": deposited,
            "maximum_vertical_motion_offset_mm": motion.max_shift,
            "maximum_mapped_z_speed_mm_s": motion.max_z_speed,
            "maximum_mapped_path_slope_degrees": motion.max_slope,
            "added_commanded_motion_seconds": motion.added_seconds,
            "restored_extrusion_delta_mm": motion.extrusion_delta})))
    }
}

/// Find the supported back of the dispense face and keep the beverage aperture clear.
pub fn add_tip_dispense_contact(project: &mut Refreshed, spec: &Value, parameters: &Value) -> Result<Value> {
    let part = spec["part"].as_str().context("dispense contact part")?;
    let row = project.row(part)?;
    let index = row.index;
    let object = &project.plate.objects[index];
    let (sin, cos) = TOTAL_ANGLE.sin_cos();
    let normal = apply(&object.rotation, [0., sin, -cos]);
    ensure!(normal[2] < -std::f64::consts::FRAC_1_SQRT_2, "the dispense contact must face down on a shallow incline");
    let world: Vec<_> = row.mesh.vertices.iter().map(|point| {
        add(apply(&object.rotation, sub(*point, row.center)), object.translation)
    }).collect();
    let planes = parallel_faces(&world, &row.mesh.faces, normal);
    let inside = planes.iter().filter(|face| face.downward)
        .max_by(|a, b| a.area.total_cmp(&b.area)).context("supported inside face")?;
    let outside = planes.iter().filter(|face| !face.downward && (inside.offset - face.offset - DISPENSE_FACE_THICKNESS).abs() < 0.01)
        .max_by(|a, b| a.area.total_cmp(&b.area)).context("outlet plane")?;
    let patch: Vec<_> = inside.faces.iter().flat_map(|face| face.map(|i| world[i])).collect();
    let inside_faces: BTreeSet<_> = inside.faces.iter().copied().collect();
    let contact_marks: BTreeMap<_, _> = row.mesh.faces.iter().enumerate()
        .filter_map(|(i, face)| inside_faces.contains(face).then(|| (i, face.map(|v| world[v])))).collect();
    let (low, high) = bounds(&patch);
    let mut seat = mix(low, high, 0.5);
    seat[2] += (inside.offset - dot(normal, seat)) / normal[2];
    let margin = spec["mapping_margin_mm"].as_f64().context("dispense mapping margin")?;
    let window = [[low[0] - margin, low[1] - margin], [high[0] + margin, high[1] + margin]];
    let mut parameters = parameters.clone();
    parameters["contact_full_weight_mm"][1] = spec["interior_full_mm"].clone();
    parameters["contact_zero_weight_mm"][1] = spec["interior_end_mm"].clone();
    for key in ["maximum_mesh_y_step_mm", "maximum_mesh_z_step_mm"] {
        parameters[key] = json!(parameters[key].as_f64().context("dispense mesh step")? / 2.);
    }
    let mut band = json!({"parameters": parameters, "plane_normal": normal, "seat_plate_mm": seat,
        "bounds_mm": window, "edge_blend_mm": spec["mapping_edge_blend_mm"], "refine_mesh_interiors": true});
    ContactBand::new(&band)?;
    ensure!(band["parameters"]["contact_zero_weight_mm"][1].as_f64().unwrap_or(f64::INFINITY)
        < DISPENSE_FACE_THICKNESS / normal[2].abs(), "the dispense mapping reaches the exterior face");

    let mut loops = boundary_loops(&outside.faces, &world)?;
    loops.sort_by(|a, b| polygon_area(b, normal).abs().total_cmp(&polygon_area(a, normal).abs()));
    let exterior_winding = polygon_area(loops.first().context("the exterior outlet boundary")?, normal).signum();
    let apertures: Vec<_> = loops.into_iter().skip(1)
        .filter(|aperture| polygon_area(aperture, normal).signum() != exterior_winding)
        .collect();
    ensure!(!apertures.is_empty(), "the selected exterior face has no beverage aperture");
    let clearance = spec["outlet_clearance_mm"].as_f64().context("outlet radial clearance")?;
    let shadow_clearance = spec["outlet_shadow_clearance_mm"].as_f64().unwrap_or(clearance);
    let depth: [f64; 2] = serde_json::from_value(spec["outlet_depth_mm"].clone())?;
    ensure!(clearance >= 0. && depth[0] < 0. && depth[1] > DISPENSE_FACE_THICKNESS,
        "the outlet blocker must span the full face");
    let r = object.rotation;
    let t = object.translation;
    let inverse = [0, 1, 2].map(|axis| [0, 1, 2].map(|other| r[other][axis]));
    let mut blockers = Vec::new();
    let mut shadows = Vec::new();
    for (number, mut aperture) in apertures.into_iter().enumerate() {
        shadows.push(outlet_shadow(&aperture, normal, depth, shadow_clearance));
        let (vertices, faces) = outlet_blocker(&mut aperture, normal, clearance, depth);
        let vertices = vertices.into_iter().map(|point| apply(&inverse, sub(point, t))).collect();
        let mesh = Mesh { vertices, faces };
        let name = format!("Keep support clear of beverage outlet {}", number + 1);
        mesh.check_closed_single_body(&name)?;
        let id = project.plate.add_part(index, &name, mesh.vertices, mesh.faces, "support_blocker", Vec::new(), None);
        blockers.push(json!({"part_id": id, "aperture_plate_mm": aperture, "depth_mm": depth, "clearance_mm": clearance}));
    }
    let object = &mut project.plate.objects[index];
    object.settings.retain(|(key, _)| key != "support_style");
    object.settings.push(("support_style".into(), "tree_slim".into()));
    let selection = SupportPaint { faces: contact_marks.keys().copied().collect(), shadows };
    let paint = paint_of(project, index);
    for (i, face) in contact_marks {
        set_paint(&mut paint[i], "paint_supports", if selection.clear(face) { "4" } else { "8" });
    }
    band["support_paint"] = json!({"faces": selection.faces, "outlet_shadows": selection.shadows});
    Ok(json!({"part": part, "support_style": "tree_slim", "plate_bounds_mm": [low, high],
        "inclination_degrees": normal[2].abs().acos().to_degrees(),
        "contact_area_mm2": inside.area, "face_count": inside.faces.len(),
        "outlet_blockers": blockers, "band": band}))
}

fn outlet_shadow(aperture: &[Point], normal: Point, depth: [f64; 2], clearance: f64) -> Vec<Point> {
    let mut points: Vec<_> = aperture.iter().flat_map(|p| depth.map(|d| [p[0] + normal[0] * d, p[1] + normal[1] * d])).collect();
    points.sort_by(|a, b| a[0].total_cmp(&b[0]).then(a[1].total_cmp(&b[1])));
    points.dedup();
    let orient = |a: [f64; 2], b: [f64; 2], c: [f64; 2]| {
        (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    };
    let mut polygon = Vec::new();
    for reverse in [false, true] {
        let start = polygon.len();
        for i in 0..points.len() {
            let point = points[if reverse { points.len() - 1 - i } else { i }];
            while polygon.len() >= start + 2
                && orient(polygon[polygon.len() - 2], polygon[polygon.len() - 1], point) <= 0.
            {
                polygon.pop();
            }
            polygon.push(point);
        }
        polygon.pop();
    }
    polygon.iter().zip(polygon.iter().cycle().skip(1)).map(|(a, b)| {
        let [dx, dy] = [b[0] - a[0], b[1] - a[1]];
        let length = dx.hypot(dy);
        let [nx, ny] = [dy / length, -dx / length];
        [nx, ny, nx * a[0] + ny * a[1] + clearance]
    }).collect()
}

struct ParallelFace {
    offset: f64,
    downward: bool,
    faces: Vec<Face>,
    area: f64,
}

fn parallel_faces(points: &[Point], faces: &[Face], axis: Point) -> Vec<ParallelFace> {
    let mut groups = Vec::<ParallelFace>::new();
    for &face in faces {
        let [a, b, c] = face.map(|i| points[i]);
        let n = cross(sub(b, a), sub(c, a));
        let size = distance(n, [0.; 3]);
        let projection = dot(n, axis);
        if size <= 1e-8 || projection.abs() < size * 0.999999 {
            continue;
        }
        let offset = (dot(a, axis) + dot(b, axis) + dot(c, axis)) / 3.;
        let downward = projection > 0.;
        let area = size / 2.;
        if let Some(group) = groups.iter_mut().find(|g| g.downward == downward && (g.offset - offset).abs() < 0.001) {
            group.faces.push(face);
            group.area += area;
        } else {
            groups.push(ParallelFace { offset, downward, faces: vec![face], area });
        }
    }
    groups
}

fn boundary_loops(faces: &[Face], points: &[Point]) -> Result<Vec<Vec<Point>>> {
    let mut opposite = BTreeMap::new();
    for &[a, b, c] in faces {
        for (side, corner) in [((a, b), c), ((b, c), a), ((c, a), b)] {
            ensure!(opposite.insert(side, corner).is_none(), "the outlet face has inconsistent triangle winding");
        }
    }
    let mut remaining: BTreeSet<_> = opposite.keys().copied()
        .filter(|&(a, b)| !opposite.contains_key(&(b, a))).collect();
    let mut loops = Vec::new();
    while let Some(&start) = remaining.first() {
        let mut walk = Vec::new();
        let mut side = start;
        loop {
            ensure!(remaining.remove(&side), "the outlet face has an open boundary path");
            walk.push(side.0);
            let mut next = (side.1, opposite[&side]);
            // Cross each interior edge of the fan at this vertex until the boundary resumes.
            while let Some(&corner) = opposite.get(&(next.1, next.0)) {
                next.1 = corner;
            }
            if next == start {
                break;
            }
            side = next;
        }
        let mut path = Vec::new();
        let mut indices = BTreeMap::new();
        for vertex in walk.into_iter().chain(std::iter::once(start.0)) {
            // An aperture can meet the exterior at a vertex. Split the walk at that contact.
            if let Some(&at) = indices.get(&vertex) {
                let cycle = path.split_off(at);
                ensure!(cycle.len() >= 3, "the outlet face has a degenerate boundary loop");
                for corner in &cycle {
                    indices.remove(corner);
                }
                loops.push(cycle.into_iter().map(|corner| points[corner]).collect());
            }
            indices.insert(vertex, path.len());
            path.push(vertex);
        }
    }
    Ok(loops)
}

fn polygon_area(loop_points: &[Point], normal: Point) -> f64 {
    loop_points.iter().zip(loop_points.iter().cycle().skip(1))
        .map(|(&a, &b)| dot(cross(a, b), normal) / 2.).sum()
}

fn outlet_blocker(aperture: &mut [Point], normal: Point, clearance: f64, depth: [f64; 2]) -> (Vec<Point>, Vec<Face>) {
    if polygon_area(aperture, normal) < 0. {
        aperture.reverse();
    }
    let count = aperture.len();
    let center = scale(aperture.iter().copied().fold([0.; 3], add), 1. / count as f64);
    let mut vertices = Vec::with_capacity(count * 2 + 2);
    for shift in depth {
        for &point in aperture.iter() {
            let ray = sub(point, center);
            vertices.push(add(add(point, scale(ray, clearance / distance(point, center))), scale(normal, shift)));
        }
    }
    vertices.extend(depth.map(|shift| add(center, scale(normal, shift))));
    let mut faces = Vec::with_capacity(count * 4);
    for i in 0..count {
        let j = (i + 1) % count;
        faces.extend([[i, j, j + count], [i, j + count, i + count],
                      [2 * count, j, i], [2 * count + 1, i + count, j + count]]);
    }
    (vertices, faces)
}

fn dot(a: Point, b: Point) -> f64 {
    a.into_iter().zip(b).map(|(a, b)| a * b).sum()
}

fn scale(point: Point, factor: f64) -> Point {
    point.map(|component| component * factor)
}

/// Apply the supported first perimeter to the restored slice, retaining the input for review.
pub fn apply_rim_contour(project: &Path, directory: &Path, spec: crate::rim_contour::RimSpec) -> Result<Value> {
    let archive_name = format!("{}.gcode.3mf", project.file_stem().context("rim project stem")?.to_string_lossy());
    let archive = directory.join(archive_name);
    let raw = directory.join("plate_1.gcode");
    let prior = directory.join("mapped-slice");
    let source = prior.join("restored-before-contour.gcode");
    fs::copy(&raw, &source)?;
    fs::copy(&archive, prior.join("restored-before-contour.gcode.3mf"))?;
    let output = prior.join("rim-contour.gcode");
    let reading = crate::rim_contour::apply(&source, &output, spec)?;
    ensure!(reading.emitted_contact_segments > 0 && reading.modified_native_paths > 0,
        "the selected full faucet has no supported first perimeter replacement");
    let gcode = fs::read(&output)?;
    let mut report = json!({"purpose": "Bind the continuous first outer rim course to the complete product.",
        "identify_id": spec.identify_id, "seat_plate_mm": spec.center_mm,
        "seat_fall_angle_degrees": spec.seat_fall_angle_degrees, "rim_semi_axes_mm": spec.semi_axes_mm,
        "supported_angles_degrees": spec.supported_angles_degrees,
        "gcode_input_sha256": sha256_hex(&fs::read(&source)?), "gcode_sha256": sha256_hex(&gcode),
        "arc_count": reading.arc_count, "emitted_contact_segments": reading.emitted_contact_segments,
        "modified_native_paths": reading.modified_native_paths, "extrusion_added_mm": reading.extrusion_added_mm,
        "extrusion_removed_mm": reading.extrusion_removed_mm,
        "added_commanded_motion_seconds": reading.estimated_motion_delta_seconds,
        "maximum_contact_depth_below_prior_peak_mm": reading.maximum_contact_depth_below_prior_peak_mm,
        "minimum_contact_z_mm": reading.minimum_contact_z_mm});
    let mut zip = zip::ZipArchive::new(fs::File::open(&archive)?)?;
    let mut replaced = BTreeMap::from([
        (format!("{GCODE}.md5"), md5_hex(&gcode).into_bytes()),
        (GCODE.into(), gcode),
        ("Metadata/hsm_rim_contour.json".into(), serde_json::to_vec_pretty(&report)?),
    ]);
    replace_prediction(&mut zip, &mut replaced, reading.estimated_motion_delta_seconds)?;
    write_archive(zip, replaced, &archive, false)?;
    fs::rename(output, raw)?;
    let result = directory.join("result.json");
    write_motion_result(&result, &result, reading.estimated_motion_delta_seconds)?;
    report["archive_sha256"] = json!(sha256_hex(&fs::read(&archive)?));
    fs::write(directory.join("rim-contour.json"), serde_json::to_vec_pretty(&report)?)?;
    Ok(report)
}

fn replace_prediction(archive: &mut zip::ZipArchive<fs::File>, replaced: &mut BTreeMap<String, Vec<u8>>,
                      seconds: f64) -> Result<()> {
    let name = "Metadata/slice_info.config";
    let info = read_member(archive, name)?;
    let prediction = json!([{"member": GCODE, "added_commanded_motion_seconds": seconds}]);
    replaced.insert(name.into(), crate::slice::add_predictions(std::str::from_utf8(&info)?, &prediction)?.into_bytes());
    Ok(())
}

fn write_motion_result(source: &Path, output: &Path, added: f64) -> Result<()> {
    let mut result: Value = serde_json::from_slice(&fs::read(source)?)?;
    for plate in result["sliced_plates"].as_array_mut().into_iter().flatten() {
        if let Some(seconds) = plate["total_predication"].as_f64() {
            plate["total_predication"] = json!((seconds + added).ceil() as i64);
        }
    }
    fs::write(output, serde_json::to_vec_pretty(&result)?)?;
    Ok(())
}

fn write_archive(mut archive: zip::ZipArchive<fs::File>, replaced: BTreeMap<String, Vec<u8>>,
                 output: &Path, replace_model: bool) -> Result<()> {
    let options = zip::write::SimpleFileOptions::default().compression_method(zip::CompressionMethod::Deflated);
    let temporary = output.with_extension(format!("restoring-{}", std::process::id()));
    let mut writer = zip::ZipWriter::new(fs::File::create(&temporary)?);
    for i in 0..archive.len() {
        let entry = archive.by_index_raw(i)?;
        let name = entry.name()?;
        if !(replaced.contains_key::<str>(name.as_ref()) || replace_model && name.starts_with("3D/")) {
            writer.raw_copy_file(entry)?;
        }
    }
    for (name, data) in replaced {
        writer.start_file(name, options)?;
        writer.write_all(&data)?;
    }
    writer.finish()?;
    fs::rename(&temporary, output)?;
    Ok(())
}

fn add(a: Point, b: Point) -> Point {
    [0, 1, 2].map(|axis| a[axis] + b[axis])
}

fn mix(a: Point, b: Point, t: f64) -> Point {
    [0, 1, 2].map(|axis| a[axis] + (b[axis] - a[axis]) * t)
}

fn distance(a: Point, b: Point) -> f64 {
    (a[0] - b[0]).hypot(a[1] - b[1]).hypot(a[2] - b[2])
}

fn smooth(t: f64) -> f64 {
    let t = t.clamp(0., 1.);
    t * t * (3. - 2. * t)
}

fn edge(a: usize, b: usize) -> (usize, usize) {
    (a.min(b), a.max(b))
}

fn read_member<R: Read + std::io::Seek>(archive: &mut zip::ZipArchive<R>, name: &str) -> Result<Vec<u8>> {
    let mut data = Vec::new();
    archive.by_name(name)?.read_to_end(&mut data)?;
    Ok(data)
}

struct Motion {
    out: Vec<u8>,
    native: Point,
    actual: Point,
    feed: f64,
    emitted_feed: f64,
    height: f64,
    layer: usize,
    in_print: bool,
    absolute: bool,
    relative_e: bool,
    retract_debt: f64,
    highest: f64,
    shifted_roads: usize,
    lifted_travels: usize,
    max_shift: f64,
    max_z_speed: f64,
    max_slope: f64,
    added_seconds: f64,
    extrusion_delta: f64,
}

impl Motion {
    fn new(capacity: usize) -> Self {
        Self { out: Vec::with_capacity(capacity), native: [0.; 3], actual: [0.; 3], feed: 1800.,
            emitted_feed: 1800., height: 0.24, layer: 0, in_print: false, absolute: true,
            relative_e: false, retract_debt: 0., highest: 0., shifted_roads: 0, lifted_travels: 0,
            max_shift: 0., max_z_speed: 0., max_slope: 0., added_seconds: 0., extrusion_delta: 0. }
    }

    fn line(&mut self, bands: &[&ContactBand], deposited: &mut [usize], line: &str) -> Result<()> {
        if line.starts_with("; CHANGE_LAYER") {
            self.in_print = true;
            self.layer += 1;
        }
        if line.starts_with("; MACHINE_END_GCODE_START") {
            self.in_print = false;
        }
        if let Some(height) = line.strip_prefix("; LAYER_HEIGHT: ") {
            self.height = height.parse()?;
        }
        let (command, comment) = line.split_once(';').unwrap_or((line, ""));
        let w = words(command.trim());
        let get = |key| w.iter().find(|(word, _)| *word == key).map(|(_, value)| *value);
        match (get(b'G'), get(b'M')) {
            (Some(90.), _) => self.absolute = true,
            (Some(91.), _) => self.absolute = false,
            (_, Some(82.)) => self.relative_e = false,
            (_, Some(83.)) => self.relative_e = true,
            _ => {}
        }
        let axes = [b'X', b'Y', b'Z'];
        if get(b'G') == Some(92.) {
            for (axis, key) in axes.into_iter().enumerate() {
                if let Some(value) = get(key) {
                    ensure!(!self.in_print, "unsupported coordinate reset in mapped print body");
                    self.native[axis] = value;
                    self.actual[axis] = value;
                }
            }
        }
        let Some(code @ (0. | 1. | 2. | 3.)) = get(b'G') else {
            writeln!(self.out, "{line}")?;
            return Ok(());
        };
        let from = self.native;
        let target = [0, 1, 2].map(|axis| get(axes[axis]).map_or(from[axis], |value| {
            if self.absolute { value } else { from[axis] + value }
        }));
        self.native = target;
        if let Some(feed) = get(b'F') {
            self.feed = feed;
        }
        let e = get(b'E').unwrap_or(0.);
        let arc_move = code == 2. || code == 3.;
        let lateral = arc_move || (target[0] - from[0]).hypot(target[1] - from[1]) > 1e-9;
        if self.in_print && e != 0. {
            self.retract_debt = (self.retract_debt - e).max(0.);
        }
        let mut chords = Vec::new();
        let mut active = None;
        if self.in_print && self.layer > 2 && (lateral || get(b'Z').is_some()) {
            if arc_move {
                ensure!(get(b'R').is_none(), "unsupported radius-format arc in mapped print body");
                let chord = bands.iter().map(|band| band.segment).fold(f64::INFINITY, f64::min);
                chords = arc(from[0], from[1], target[0], target[1], &w, code == 2., chord);
                let last = chords.len() - 1;
                active = bands.iter().position(|band| chords.windows(2).enumerate().any(|(i, xy)| {
                    let a = [xy[0].0, xy[0].1, mix(from, target, i as f64 / last as f64)[2]];
                    let b = [xy[1].0, xy[1].1, mix(from, target, (i + 1) as f64 / last as f64)[2]];
                    band.interval(a, b, band.period / 4.)
                }));
            } else {
                active = bands.iter().position(|band| band.interval(from, target, band.period / 4.));
            }
        }
        let Some(active) = active else {
            if self.in_print && get(b'F').is_none() && (self.emitted_feed - self.feed).abs() > 0.1 {
                self.set_feed(self.feed)?;
            }
            writeln!(self.out, "{line}")?;
            if get(b'F').is_some() {
                self.emitted_feed = self.feed;
            }
            if lateral || (target[2] - from[2]).abs() > 1e-9 || !self.in_print {
                self.actual = target;
            }
            if self.in_print && lateral && e > 0. {
                self.highest = self.highest.max(from[2]).max(target[2]);
            }
            return Ok(());
        };
        let band = bands[active];
        ensure!(self.absolute && self.relative_e && self.feed > 0.,
            "the contact band requires absolute XYZ, relative extrusion and positive feed");
        let restored = bands.iter().fold(target, |point, band| band.restored(point));
        let only_z = (target[0] - from[0]).hypot(target[1] - from[1]) < 1e-9;
        if only_z && e == 0. {
            self.move_z(band, from, target, restored, comment)?;
        } else if !lateral {
            ensure!((restored[2] - self.actual[2]).abs() < 1e-5, "combined Z and extruder move in contact band");
            self.set_feed(self.feed)?;
            writeln!(self.out, "G1 E{e:.7} ;{comment}")?;
        } else if e == 0. {
            self.travel(band, from, target, restored, comment)?;
        } else {
            let start = self.shifted_roads;
            self.extruding(band, from, target, e, &chords, comment)?;
            deposited[active] += self.shifted_roads - start;
        }
        Ok(())
    }

    fn move_z(&mut self, band: &ContactBand, from: Point, target: Point, restored: Point, comment: &str) -> Result<()> {
        let dz = (restored[2] - self.actual[2]).abs();
        if dz > 1e-5 {
            writeln!(self.out, "G1 Z{:.5} F{:.0} ;{comment}", restored[2], band.z_travel_feed)?;
            self.added_seconds += (dz / band.z_travel_feed - (target[2] - from[2]).abs() / self.feed) * 60.;
            self.actual = restored;
            self.emitted_feed = band.z_travel_feed;
        } else {
            self.set_feed(self.feed)?;
            if !comment.is_empty() {
                writeln!(self.out, ";{comment}")?;
            }
        }
        Ok(())
    }

    fn set_feed(&mut self, feed: f64) -> Result<()> {
        if (self.emitted_feed - feed).abs() > 0.1 {
            writeln!(self.out, "G1 F{feed:.0}")?;
            self.emitted_feed = feed;
        }
        Ok(())
    }

    fn travel(&mut self, band: &ContactBand, from: Point, target: Point, restored: Point, comment: &str) -> Result<()> {
        let safe = self.actual[2].max(restored[2]).max(self.highest + band.clearance);
        let dz = (safe - self.actual[2]) + (safe - restored[2]);
        let z_time = dz * 60. / band.z_travel_feed;
        if dz > 1e-5 {
            self.lifted_travels += 1;
            let retract = if self.retract_debt < 0.01 { band.retract } else { 0. };
            if retract > 0. {
                writeln!(self.out, "G1 E{:.5} F{:.0}", -retract, band.retract_feed)?;
                self.added_seconds += 120. * retract / band.retract_feed;
            }
            writeln!(self.out, "G1 Z{safe:.5} F{:.0}", band.z_travel_feed)?;
            writeln!(self.out, "G1 X{:.5} Y{:.5} F{:.0} ;{comment}", restored[0], restored[1], self.feed)?;
            writeln!(self.out, "G1 Z{:.5} F{:.0}", restored[2], band.z_travel_feed)?;
            self.emitted_feed = band.z_travel_feed;
            if retract > 0. {
                writeln!(self.out, "G1 E{retract:.5} F{:.0}", band.retract_feed)?;
                self.emitted_feed = band.retract_feed;
            }
        } else {
            writeln!(self.out, "G1 X{:.5} Y{:.5} Z{:.5} F{:.0} ;{comment}", restored[0], restored[1], restored[2], self.feed)?;
            self.emitted_feed = self.feed;
        }
        self.added_seconds += z_time + ((target[0] - from[0]).hypot(target[1] - from[1]) - distance(from, target)) * 60. / self.feed;
        self.actual = restored;
        Ok(())
    }

    fn extruding(&mut self, band: &ContactBand, from: Point, target: Point, e: f64, chords: &[(f64, f64)], comment: &str) -> Result<()> {
        let count = if chords.is_empty() {
            (distance(from, target) / band.segment).ceil().max(1.) as usize
        } else {
            chords.len() - 1
        };
        let mut native_from = from;
        for i in 1..=count {
            let t = i as f64 / count as f64;
            let mut p = mix(from, target, t);
            if !chords.is_empty() {
                [p[0], p[1]] = [chords[i].0, chords[i].1];
            }
            let q = band.restored(p);
            let mid = mix(native_from, p, 0.5);
            let shift = (q[2] - p[2]).abs().max((self.actual[2] - native_from[2]).abs());
            let length = distance(self.actual, q);
            let dz = (self.actual[2] - q[2]).abs();
            let feed = if dz > 1e-6 && length > 1e-6 {
                self.feed.min(band.z_print_feed * length / dz).floor().max(1.)
            } else {
                self.feed
            };
            let native_amount = e / count as f64;
            let amount = if e > 0. {
                let lower = add(mid, [0., 0., -self.height]);
                native_amount * ((band.restored(mid)[2] - band.restored(lower)[2]) / self.height)
            } else {
                native_amount
            };
            self.set_feed(feed)?;
            write!(self.out, "G1 X{:.5} Y{:.5} Z{:.5}", q[0], q[1], q[2])?;
            if e != 0. {
                write!(self.out, " E{amount:.7}")?;
            }
            if i == count && !comment.is_empty() {
                write!(self.out, " ;{comment}")?;
            }
            writeln!(self.out)?;
            self.added_seconds += (length / feed - distance(native_from, p) / self.feed) * 60.;
            self.extrusion_delta += amount - native_amount;
            if e > 0. {
                self.highest = self.highest.max(self.actual[2]).max(q[2]);
                if shift > 1e-5 {
                    self.shifted_roads += 1;
                    self.max_shift = self.max_shift.max(shift);
                    self.max_z_speed = self.max_z_speed.max(dz / length.max(1e-9) * feed / 60.);
                    let xy = (q[0] - self.actual[0]).hypot(q[1] - self.actual[1]);
                    self.max_slope = self.max_slope.max(dz.atan2(xy).to_degrees());
                }
            }
            self.actual = q;
            native_from = p;
        }
        Ok(())
    }
}
