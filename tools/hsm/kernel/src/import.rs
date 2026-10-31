//! Parts from other files: the bodies of a `.step.mesh` payload, and of a STEP through a payload
//! cut from it.
//!
//! A payload holds triangles and the face ranges the page picks by, and no surfaces. Every face
//! read from one is a free `MESH` record made by "import", and its source is the file asked for
//! (`face::file_src`): the payload, or the STEP read through it. The solids of one body, which a
//! payload holds as `name/1`, `name/2`, …, come back as one body under its name.
//!
//! A STEP of B-rep faces is read through `.cache/hsm/import/<SHA-256>.step.mesh` at the
//! checkout's root: OCCT's mesh of it at the kernel's rule, which `_rust_part.step` cuts once
//! under the CAD lock. A STEP of triangles, which a mesh kernel writes, is read through the
//! payload its writer cut beside it (`<name>.step.mesh`, whose `src` is the STEP's SHA-256). A
//! relative path is read from the working directory, which `_rust_part.cut` sets to the root.
use crate::face::{Face, Surface, file_src};
use crate::mass;
use crate::math::{V3, v3};
use crate::rule::snap3;
use crate::solid::{Solid, canonical};
use crate::step::MARK;
use anyhow::{Context, Result, bail, ensure};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::path::{Component, Path, PathBuf};

/// A body read from a file.
#[derive(Clone, Debug)]
pub struct Imported {
    pub name: String,
    /// Linear RGB, 0 to 1.
    pub color: Option<[f64; 3]>,
    pub solid: Solid,
}

impl Solid {
    /// The closed mesh `tris` over `verts` as a solid, triangle `t` on the face record
    /// `faces[face_of[t]]`. Corners at one point of the rule's grid are one vertex, a triangle
    /// two of whose corners meet there is dropped, and the solid is wound so its volume is
    /// positive and put in canonical order. A mesh left open or folded is an error.
    pub fn from_mesh(verts: &[V3], tris: &[[u32; 3]], face_of: &[u32], faces: &[Face]) -> Result<Solid> {
        ensure!(tris.len() == face_of.len(), "{} triangles and {} face indices", tris.len(), face_of.len());
        ensure!(
            tris.iter().flatten().all(|&v| (v as usize) < verts.len()),
            "a triangle names a vertex past the mesh's {}",
            verts.len()
        );
        ensure!(
            face_of.iter().all(|&f| (f as usize) < faces.len()),
            "a triangle names a face past the mesh's {}",
            faces.len()
        );
        let mut at: HashMap<[u64; 3], u32> = HashMap::new();
        let mut points = vec![];
        let one: Vec<u32> = verts
            .iter()
            .map(|&p| {
                let p = snap3(p) + V3::ZERO;
                *at.entry([p.x.to_bits(), p.y.to_bits(), p.z.to_bits()]).or_insert_with(|| {
                    points.push(p);
                    points.len() as u32 - 1
                })
            })
            .collect();
        let mut kept = Vec::with_capacity(tris.len());
        let mut kept_face = Vec::with_capacity(tris.len());
        for (t, &f) in tris.iter().zip(face_of) {
            let t = t.map(|v| one[v as usize]);
            if t[0] != t[1] && t[1] != t[2] && t[2] != t[0] {
                kept.push(t);
                kept_face.push(f);
            }
        }
        if mass::signed_volume(&points, &kept) < 0.0 {
            for t in &mut kept {
                t.swap(1, 2);
            }
        }
        let solid = canonical(&points, &kept, &kept_face, faces);
        solid.check()?;
        Ok(solid)
    }
}

/// The bodies of the payload at `path`.
pub fn payload(path: impl AsRef<Path>) -> Result<Vec<Imported>> {
    let path = path.as_ref();
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    bodies(&bytes, &name_of(path))
}

/// The bodies of the STEP at `path`, through a payload cut from it.
pub fn step(path: impl AsRef<Path>) -> Result<Vec<Imported>> {
    let path = path.as_ref();
    let name = name_of(path);
    let data = std::fs::read(path).with_context(|| format!("reading {name}"))?;
    let digest = format!("{:x}", Sha256::digest(&data));
    if data[..data.len().min(200)].windows(MARK.len()).any(|w| w == MARK.as_bytes()) {
        let mut beside = path.as_os_str().to_owned();
        beside.push(".mesh");
        let bytes = std::fs::read(&beside).with_context(|| format!("{name} is triangles, and no payload stands beside it"))?;
        ensure!(
            header(&bytes)?.get("src").and_then(Value::as_str) == Some(&digest),
            "{name} is triangles, and the payload beside it was not cut from it"
        );
        return bodies(&bytes, &name);
    }
    let cut = cache().join(format!("{digest}.step.mesh"));
    let bytes = std::fs::read(&cut)
        .with_context(|| format!("{name} has no payload cut from it; `_rust_part.step` cuts one into {}", cut.display()))?;
    bodies(&bytes, &name)
}


/// The body `name` of `bodies`.
pub fn body<'a>(bodies: &'a [Imported], name: &str) -> Result<&'a Solid> {
    match bodies.iter().find(|b| b.name == name) {
        Some(b) => Ok(&b.solid),
        None => {
            let names: Vec<&str> = bodies.iter().map(|b| b.name.as_str()).collect();
            bail!("no body named {name:?}; the file holds {names:?}")
        }
    }
}

/// The bodies of a payload's bytes, their faces read from the file `name`.
pub fn bodies(bytes: &[u8], name: &str) -> Result<Vec<Imported>> {
    let head = header(bytes)?;
    ensure!(head["v"] == 3, "{name} is payload version {}, not 3", head["v"]);
    let size = u32::from_le_bytes(bytes[..4].try_into()?) as usize;
    let blob = &bytes[4 + size..];
    let src = file_src(name);
    let free = Face::new(Surface::Free { kind: "MESH" }, "import", src);
    let mut out: Vec<Imported> = vec![];
    for e in head["meshes"].as_array().context("a payload header lists its meshes")? {
        let entry = e["name"].as_str().context("a payload mesh has a name")?;
        let pos = words(blob, &e["pos"])?;
        let idx = words(blob, &e["idx"])?;
        let fac = words(blob, &e["fac"])?;
        ensure!(pos.len() % 3 == 0 && idx.len() % 3 == 0 && fac.len() % 2 == 0, "{name}: {entry} has ragged arrays");
        let verts: Vec<V3> = pos
            .chunks_exact(3)
            .map(|p| v3(f32::from_bits(p[0]) as f64, f32::from_bits(p[1]) as f64, f32::from_bits(p[2]) as f64))
            .collect();
        let tris: Vec<[u32; 3]> = idx.chunks_exact(3).map(|t| [t[0], t[1], t[2]]).collect();
        let ranges = fac.len() / 2;
        let mut face_of = vec![ranges as u32; tris.len()];
        for (f, r) in fac.chunks_exact(2).enumerate() {
            ensure!(r[0] <= r[1] && (r[1] as usize) < tris.len(), "{name}: {entry} has a face range past its triangles");
            face_of[r[0] as usize..=r[1] as usize].fill(f as u32);
        }
        let faces = vec![free; ranges + 1];
        let solid = Solid::from_mesh(&verts, &tris, &face_of, &faces).with_context(|| format!("{name}: {entry}"))?;
        let body = without_index(entry);
        let color = e["color"].as_array().map(|c| [0, 1, 2].map(|k| c.get(k).and_then(Value::as_f64).unwrap_or(0.0)));
        match out.iter_mut().find(|b| b.name == body) {
            Some(b) => b.solid = Solid::compose(&[b.solid.clone(), solid]),
            None => out.push(Imported { name: body.to_string(), color, solid }),
        }
    }
    Ok(out)
}

fn header(bytes: &[u8]) -> Result<Value> {
    ensure!(bytes.len() >= 4, "a payload starts with its header's length");
    let size = u32::from_le_bytes(bytes[..4].try_into()?) as usize;
    let head = bytes.get(4..4 + size).context("the payload ends inside its header")?;
    Ok(serde_json::from_slice(head)?)
}

/// The little-endian words of a payload array, `[byte offset, count]` into the blob.
fn words(blob: &[u8], range: &Value) -> Result<Vec<u32>> {
    let at = |k: usize| range.get(k).and_then(Value::as_u64).map(|n| n as usize);
    let (Some(offset), Some(count)) = (at(0), at(1)) else { bail!("a payload array is [offset, count]") };
    let bytes = blob.get(offset..offset + 4 * count).context("a payload array runs past the file")?;
    Ok(bytes.chunks_exact(4).map(|b| u32::from_le_bytes(b.try_into().unwrap())).collect())
}

/// A body's name without the `/<n>` that numbers its solids.
fn without_index(name: &str) -> &str {
    match name.rsplit_once('/') {
        Some((body, n)) if !n.is_empty() && n.bytes().all(|b| b.is_ascii_digit()) => body,
        _ => name,
    }
}

/// The checkout's root, which holds the kernel at `tools/hsm/kernel`.
fn root() -> &'static Path {
    Path::new(env!("CARGO_MANIFEST_DIR")).ancestors().nth(3).unwrap()
}

fn cache() -> PathBuf {
    root().join(".cache/hsm/import")
}

/// `path` as a face record names it: from the checkout's root, or from the working directory
/// when it lies outside the checkout, or whole.
fn name_of(path: &Path) -> String {
    let cwd = std::env::current_dir().unwrap_or_default();
    let mut full = PathBuf::new();
    for c in cwd.join(path).components() {
        match c {
            Component::ParentDir => {
                full.pop();
            }
            Component::CurDir => {}
            c => full.push(c),
        }
    }
    let named = full.strip_prefix(root()).or_else(|_| full.strip_prefix(&cwd)).unwrap_or(&full);
    named.to_string_lossy().into_owned()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::plane::Plane;
    use crate::face::src_line;
    use crate::step::step_bytes;
    use crate::write::{Body, payload_bytes};

    #[test]
    fn a_payload_reads_back_as_written() -> Result<()> {
        let a = Plane::XY.cuboid(10.0, 6.0, 4.0);
        let b = Plane::XY.at(v3(20.0, 0.0, 0.0)).cylinder(3.0, 5.0)?;
        let bytes = payload_bytes(
            &[
                Body { name: "block", color: Some([0.5, 0.25, 0.0]), solid: &a },
                Body { name: "pins/1", color: None, solid: &b },
                Body { name: "pins/2", color: None, solid: &b.translate(v3(10.0, 0.0, 0.0)) },
            ],
            None,
            None,
        );
        let read = bodies(&bytes, "hardware/x/x.step.mesh")?;
        assert_eq!(read.iter().map(|b| b.name.as_str()).collect::<Vec<_>>(), ["block", "pins"]);
        assert_eq!(read[0].color, Some([0.5, 0.25, 0.0]));
        let block = body(&read, "block")?;
        assert!((block.volume() - a.volume()).abs() < 1e-9);
        assert_eq!(block.tris().len(), a.tris().len());
        assert_eq!(block.faces().len(), crate::topo::faces(&a).tris.len());
        let pins = body(&read, "pins")?;
        assert!((pins.volume() - 2.0 * b.volume()).abs() < 1e-3);
        assert_eq!(pins.components().len(), 2);
        let f = block.faces()[0];
        assert_eq!(f.to_string(), "MESH import at hardware/x/x.step.mesh");
        assert!(body(&read, "lever").is_err());
        Ok(())
    }

    #[test]
    fn a_step_reads_through_the_payload_cut_from_it() -> Result<()> {
        let dir = std::env::temp_dir().join(format!("hsm-import-{}", std::process::id()));
        std::fs::create_dir_all(&dir)?;
        let a = Plane::XY.cuboid(1.0, 2.0, 3.0);
        let set = [Body { name: "part", color: None, solid: &a }];
        let ours = dir.join("part.step");
        let written = step_bytes(&set, "part")?;
        std::fs::write(&ours, &written)?;
        let digest = format!("{:x}", Sha256::digest(&written));
        std::fs::write(dir.join("part.step.mesh"), payload_bytes(&set, Some("a STEP since changed"), None))?;
        assert!(step(&ours).is_err());
        std::fs::write(dir.join("part.step.mesh"), payload_bytes(&set, Some(&digest), None))?;
        let read = step(&ours)?;
        assert_eq!(read[0].name, "part");
        assert!((read[0].solid.volume() - 6.0).abs() < 1e-9);
        assert_eq!(src_line(read[0].solid.faces()[0].src), name_of(&ours));
        assert!(name_of(&ours).ends_with("part.step"));

        let theirs = dir.join("vendor.step");
        let vendor = format!("ISO-10303-21;\n/* B-rep faces, from process {} */\n", std::process::id());
        std::fs::write(&theirs, &vendor)?;
        let digest = format!("{:x}", Sha256::digest(vendor.as_bytes()));
        std::fs::write(dir.join("vendor.step.mesh"), payload_bytes(&set, Some(&digest), None))?;
        let missing = format!("{:#}", step(&theirs).unwrap_err());
        assert!(missing.contains("`_rust_part.step` cuts one"), "{missing}");
        let cut = cache().join(format!("{digest}.step.mesh"));
        std::fs::create_dir_all(cache())?;
        std::fs::write(&cut, payload_bytes(&set, Some(&digest), None))?;
        let read = step(&theirs);
        std::fs::remove_file(&cut)?;
        std::fs::remove_dir_all(&dir)?;
        assert!((read?[0].solid.volume() - 6.0).abs() < 1e-9);
        Ok(())
    }

    #[test]
    fn an_open_mesh_is_refused() {
        let face = Face::new(Surface::Free { kind: "MESH" }, "import", file_src("open"));
        let verts = [v3(0.0, 0.0, 0.0), v3(1.0, 0.0, 0.0), v3(0.0, 1.0, 0.0), v3(0.0, 0.0, 1.0)];
        let tris = [[0, 2, 1], [0, 1, 3], [1, 2, 3]];
        assert!(Solid::from_mesh(&verts, &tris, &[0, 0, 0], &[face]).is_err());
        let closed = Solid::from_mesh(&verts, &[[0, 2, 1], [0, 1, 3], [1, 2, 3], [0, 3, 2]], &[0; 4], &[face]).unwrap();
        assert!((closed.volume() - 1.0 / 6.0).abs() < 1e-12);
    }

    #[test]
    fn solid_indices_come_off_the_name() {
        assert_eq!(without_index("collets/2"), "collets");
        assert_eq!(without_index("body"), "body");
        assert_eq!(without_index("a/b"), "a/b");
        assert_eq!(without_index("a/"), "a/");
    }
}
