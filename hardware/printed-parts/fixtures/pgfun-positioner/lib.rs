//! The positioner's received-fit parameters, frames and pinned reference meshes.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Affine, Face, Solid, Surface, V3, v3};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{
    collections::BTreeMap,
    io::Write,
    path::{Path, PathBuf},
};

pub const DIRECTORY: &str = "hardware/printed-parts/fixtures/pgfun-positioner";
pub const SCAN: &str = "hardware/reference/xlaserlab-sup29f-xh/source/reconstructed-surfaces.npz";
pub const GUN_PARTS: &str =
    "hardware/reference/xlaserlab-sup29f-xh/source/positioner-reference-parts.npz";
pub const ROTATOR: &str =
    "hardware/printed-parts/fixtures/weld-rotator/weld-rotator-assembly.step.npz";

/// Parameters shared by the solid construction, motion binding and shop guide.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Design {
    pub revision: String,
    pub units: String,
    pub yaw_xy: [f64; 2],
    pub pivot_z: f64,
    pub working_lever_mm: f64,
    pub aim: [f64; 3],
    pub barrel_down_deg: f64,
    pub nozzle_gap: f64,
    pub pose_source: String,
    pub yaw_input_z: f64,
    pub pitch_output_x: f64,
    pub reducer_length: f64,
    pub case_flange_thickness: f64,
    pub case_flange_size: f64,
    pub case_pcd: f64,
    pub output_pcd: f64,
    pub output_phase_deg: f64,
    pub reduction: u32,
    pub motor_full_steps: u32,
    pub external_microsteps: u32,
    pub soft_limit_deg: f64,
    pub hard_stop_deg: f64,
    pub bearing_bore: f64,
    pub journal_diameter: f64,
    pub shaft_bore: f64,
    pub opposite_bearing_bore: f64,
    pub adapter_thickness: f64,
    pub bearing_width: f64,
    pub bearing_spacer: f64,
    pub journal_length: f64,
    pub neck_length: f64,
    pub output_flange_thickness: f64,
    pub cradle_bands_x: Vec<f64>,
    pub cradle_band_width: f64,
    pub liner_thickness: f64,
    pub contact_clearance: f64,
    pub cheek_thickness: f64,
    pub gun_supported_mass_kg: f64,
    #[serde(rename = "design_cable_force_N")]
    pub design_cable_force_n: f64,
    #[serde(rename = "design_joint_torque_Nm")]
    pub design_joint_torque_nm: f64,
    #[serde(rename = "structural_fault_torque_Nm")]
    pub structural_fault_torque_nm: f64,
    pub print_density_g_cm3: f64,
    #[serde(rename = "analysis_modulus_MPa")]
    pub analysis_modulus_mpa: f64,
    #[serde(rename = "analysis_allowable_MPa")]
    pub analysis_allowable_mpa: f64,
    pub gun_lateral_mm: f64,
    pub barrel_azimuth_deg: f64,
    pub gun_roll_deg: f64,
    pub stop_radius: f64,
    pub cheek_inner_x: f64,
    pub camera_view_down_deg: f64,
    pub camera_lens_distance_mm: f64,
    pub camera_stage_source: String,
}

impl Design {
    pub fn read(path: impl AsRef<Path>) -> Result<Self> {
        let path = path.as_ref();
        let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
        hsm_kernel::reads::read(path, &bytes);
        Ok(serde_json::from_slice(&bytes)?)
    }

    pub fn pivot(&self) -> V3 {
        v3(self.yaw_xy[0], self.yaw_xy[1], self.pivot_z)
    }

    pub fn gun_rotation(&self) -> Affine {
        Affine::rotation(V3::ZERO, V3::X, self.gun_roll_deg)
            .then(&Affine::rotation(V3::ZERO, V3::Z, 90.))
            .then(&Affine::rotation(V3::ZERO, V3::X, -self.barrel_down_deg))
            .then(&Affine::rotation(V3::ZERO, V3::Z, self.barrel_azimuth_deg))
    }

    pub fn gun_origin_relative(&self) -> V3 {
        let (a, az) = (
            self.barrel_down_deg.to_radians(),
            self.barrel_azimuth_deg.to_radians(),
        );
        let direction = v3(-a.cos() * az.sin(), a.cos() * az.cos(), -a.sin());
        let lateral = v3(-az.cos(), -az.sin(), 0.);
        v3(0., self.working_lever_mm, 0.) - direction * (121. + self.nozzle_gap)
            + lateral * self.gun_lateral_mm
    }

    pub fn gun_transform(&self) -> Affine {
        self.gun_rotation().then(&Affine::translation(
            self.pivot() + self.gun_origin_relative(),
        ))
    }
}

/// A reference surface keeps its original coordinates and triangle ordering.
#[derive(Clone, Debug)]
pub struct Mesh {
    pub vertices: Vec<[f64; 3]>,
    pub faces: Vec<[u32; 3]>,
}

impl Mesh {
    pub fn from_solid(solid: &Solid) -> Self {
        Self {
            vertices: solid.verts().iter().map(|p| p.to_array()).collect(),
            faces: solid.tris().to_vec(),
        }
    }

    pub fn transformed(&self, frame: &Affine) -> Self {
        Self {
            vertices: self
                .vertices
                .iter()
                .map(|&p| frame.point(p.into()).to_array())
                .collect(),
            faces: self.faces.clone(),
        }
    }

    pub fn solid(&self, name: &str) -> Result<Solid> {
        let points: Vec<_> = self.vertices.iter().copied().map(V3::from).collect();
        let record = Face::new(
            Surface::Free { kind: "MESH" },
            "import",
            hsm_kernel::face::file_src(name),
        );
        Solid::from_mesh(&points, &self.faces, &vec![0; self.faces.len()], &[record])
    }

    pub fn joined(&mut self, other: &Self) {
        let offset = self.vertices.len() as u32;
        self.vertices.extend_from_slice(&other.vertices);
        self.faces
            .extend(other.faces.iter().map(|t| t.map(|i| i + offset)));
    }
}

pub fn sha256(path: impl AsRef<Path>) -> Result<String> {
    let path = path.as_ref();
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    let sha = format!("{:x}", Sha256::digest(&bytes));
    hsm_kernel::reads::digest(path, &sha);
    Ok(sha)
}

pub fn root() -> PathBuf {
    let mut path = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    while !path.join("tools/hsm/Cargo.toml").is_file() {
        if !path.pop() {
            return PathBuf::from(".");
        }
    }
    path
}

/// Named vertex/triangle arrays written by the reference producer and the fixture.
pub fn load_meshes(path: impl AsRef<Path>) -> Result<BTreeMap<String, Mesh>> {
    let path = path.as_ref();
    let file = std::fs::File::open(path).with_context(|| format!("opening {}", path.display()))?;
    let mut archive = zip::ZipArchive::new(file)?;
    let names: Vec<String> = archive
        .file_names()
        .map(|name| name.map(|name| name.into_owned()))
        .collect::<Result<Vec<_>, _>>()?
        .into_iter()
        .filter_map(|name| name.strip_suffix("__v.npy").map(str::to_owned))
        .collect();
    let mut meshes = BTreeMap::new();
    for name in names {
        let vertices = npyz::NpyFile::new(archive.by_name(&format!("{name}__v.npy"))?)?;
        ensure!(
            vertices.shape().len() == 2 && vertices.shape()[1] == 3,
            "{name}: vertex rows"
        );
        let values = match vertices.dtype().descr().as_str() {
            "'<f4'" => vertices
                .into_vec::<f32>()?
                .into_iter()
                .map(f64::from)
                .collect(),
            _ => vertices.into_vec::<f64>()?,
        };
        let vertices = values.chunks_exact(3).map(|p| [p[0], p[1], p[2]]).collect();
        let triangles = npyz::NpyFile::new(archive.by_name(&format!("{name}__f.npy"))?)?;
        ensure!(
            triangles.shape().len() == 2 && triangles.shape()[1] == 3,
            "{name}: triangle rows"
        );
        let values: Vec<u32> = match triangles.dtype().descr().as_str() {
            "'<i8'" => triangles
                .into_vec::<i64>()?
                .into_iter()
                .map(u32::try_from)
                .collect::<Result<_, _>>()?,
            "'<i4'" => triangles
                .into_vec::<i32>()?
                .into_iter()
                .map(u32::try_from)
                .collect::<Result<_, _>>()?,
            _ => triangles.into_vec::<u32>()?,
        };
        let faces = values.chunks_exact(3).map(|t| [t[0], t[1], t[2]]).collect();
        meshes.insert(name, Mesh { vertices, faces });
    }
    Ok(meshes)
}

pub fn archive_options() -> zip::write::SimpleFileOptions {
    zip::write::SimpleFileOptions::default()
        .compression_method(zip::CompressionMethod::Deflated)
        .last_modified_time(zip::DateTime::default())
}

/// The fixture's meshes as NumPy arrays, readable by the guide and external analysis.
pub fn write_meshes(path: &Path, meshes: &BTreeMap<String, Mesh>) -> Result<()> {
    let mut archive = zip::ZipWriter::new(std::fs::File::create(path)?);
    for (name, mesh) in meshes {
        archive.start_file(format!("{name}__v.npy"), archive_options())?;
        write_npy(
            &mut archive,
            "<f8",
            &[mesh.vertices.len(), 3],
            mesh.vertices.iter().flatten().flat_map(|v| v.to_le_bytes()),
        )?;
        archive.start_file(format!("{name}__f.npy"), archive_options())?;
        write_npy(
            &mut archive,
            "<u4",
            &[mesh.faces.len(), 3],
            mesh.faces.iter().flatten().flat_map(|v| v.to_le_bytes()),
        )?;
    }
    archive.finish()?;
    Ok(())
}

fn write_npy(
    out: &mut impl Write,
    dtype: &str,
    shape: &[usize],
    bytes: impl Iterator<Item = u8>,
) -> Result<()> {
    let dimensions = shape
        .iter()
        .map(|v| format!("{v},"))
        .collect::<Vec<_>>()
        .join(" ");
    let mut header =
        format!("{{'descr': '{dtype}', 'fortran_order': False, 'shape': ({dimensions}), }}");
    while (10 + header.len() + 1) % 64 != 0 {
        header.push(' ');
    }
    header.push('\n');
    out.write_all(b"\x93NUMPY\x01\x00")?;
    out.write_all(&(header.len() as u16).to_le_bytes())?;
    out.write_all(header.as_bytes())?;
    let data: Vec<_> = bytes.collect();
    out.write_all(&data)?;
    Ok(())
}

/// Pinned exterior gun meshes and the rotator's current fine placed bodies.
pub fn references(root: &Path, out: &Path, design: &Design) -> Result<BTreeMap<String, Mesh>> {
    let receipt_path = Path::new(GUN_PARTS).with_extension("json");
    let pinned: serde_json::Value =
        serde_json::from_slice(&std::fs::read(root.join(&receipt_path))?)?;
    ensure!(
        sha256(root.join(GUN_PARTS))?
            == pinned["asset"]["sha256"]
                .as_str()
                .context("pinned gun hash")?,
        "gun reference parts differ from their receipt"
    );
    let mut sources = BTreeMap::new();
    for file in [GUN_PARTS, SCAN, ROTATOR] {
        sources.insert(file.to_owned(), sha256(root.join(file))?);
    }
    sources.insert(
        receipt_path.to_string_lossy().into_owned(),
        sha256(root.join(&receipt_path))?,
    );
    ensure!(
        sources[SCAN]
            == pinned["sources"][SCAN]
                .as_str()
                .context("pinned scan hash")?,
        "gun reference scan differs from its receipt"
    );
    let cache = out.join("reference-meshes.npz");
    let receipt = out.join("reference-source.json");
    if cache.is_file() && receipt.is_file() {
        let held: serde_json::Value = serde_json::from_slice(&std::fs::read(&receipt)?)?;
        if held["sources"] == serde_json::to_value(&sources)?
            && held["recessed_cap_plane_z"].as_f64() == Some(design.aim[2])
            && held["mesh_sha256"].as_str() == Some(&sha256(&cache)?)
        {
            return load_meshes(&cache);
        }
    }
    let mut meshes: BTreeMap<String, Mesh> = load_meshes(root.join(GUN_PARTS))?
        .into_iter()
        .filter(|(name, _)| {
            name != "housing"
                && (!name.starts_with("wire-feed-")
                    || ["wire-feed-front-nut", "wire-feed-thread-envelope"]
                        .contains(&name.as_str()))
        })
        .map(|(name, mesh)| (format!("gun:{name}"), mesh))
        .collect();
    for (name, mesh) in load_meshes(root.join(SCAN))? {
        meshes.insert(format!("gun:{name}"), mesh);
    }
    hsm_kernel::import::visit_model(root.join(ROTATOR), |_, body| {
        let name = body
            .name
            .rsplit_once('/')
            .filter(|(_, suffix)| suffix.parse::<usize>().is_ok())
            .map_or(body.name.as_str(), |(head, _)| head);
        let name = format!("rotator:weld-rotator/{name}");
        let mesh = Mesh::from_solid(&body.solid);
        meshes
            .entry(name)
            .and_modify(|held| held.joined(&mesh))
            .or_insert(mesh);
        Ok(())
    })?;
    let cap = Solid::cylinder(
        v3(0., 0., design.aim[2] - 3.175),
        V3::Z,
        123.698 / 2.,
        3.175,
    )?;
    meshes.insert("rotator:recessed-cap".into(), Mesh::from_solid(&cap));
    std::fs::create_dir_all(out)?;
    write_meshes(&cache, &meshes)?;
    std::fs::write(
        receipt,
        serde_json::to_vec_pretty(
            &serde_json::json!({"sources":sources,"mesh_sha256":sha256(&cache)?,"recessed_cap_plane_z":design.aim[2],
        "scope":"Pinned exterior gun reconstruction, rotator CAD and nominal recessed cap; received fit is unmeasured."}),
        )?,
    )?;
    Ok(meshes)
}
