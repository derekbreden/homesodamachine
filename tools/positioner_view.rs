//! `/positioner` receives every installed fixture and pinned-reference triangle in its motion frame.
use anyhow::{Context, Result, bail, ensure};
use base64::{Engine, engine::general_purpose::STANDARD};
use flate2::{Compression, GzBuilder};
use hsm_kernel::{Affine, V3};
use hsm_pgfun_positioner::{DIRECTORY, Design, Mesh, load_meshes, root, sha256};
use serde::Deserialize;
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, HashMap},
    io::Write,
    path::{Path, PathBuf},
};

#[derive(Deserialize)]
struct Info {
    name: String,
    group: String,
    category: String,
}

/// Creased normal regions duplicate corners while preserving each source triangle and winding.
fn display(mesh: &Mesh) -> Result<Value> {
    let points: Vec<_> = mesh.vertices.iter().copied().map(V3::from).collect();
    let mut normals = vec![];
    let mut areas = vec![];
    let mut edges: BTreeMap<(u32, u32), Vec<usize>> = BTreeMap::new();
    for (i, t) in mesh.faces.iter().enumerate() {
        let [a, b, c] = t.map(|v| points[v as usize]);
        let cross = (b - a).cross(c - a);
        let length = cross.norm();
        normals.push(if length > 1e-15 {
            cross / length
        } else {
            V3::ZERO
        });
        areas.push(length / 2.);
        for j in 0..3 {
            edges
                .entry((t[j].min(t[(j + 1) % 3]), t[j].max(t[(j + 1) % 3])))
                .or_default()
                .push(i);
        }
    }
    let mut parent: Vec<_> = (0..mesh.faces.len()).collect();
    fn find(parent: &mut [usize], mut i: usize) -> usize {
        while parent[i] != i {
            parent[i] = parent[parent[i]];
            i = parent[i];
        }
        i
    }
    let crease = hsm_print_payload::CREASE_DEG.to_radians().cos();
    for adjacent in edges.values() {
        if let [a, b] = adjacent.as_slice() {
            if normals[*a].dot(normals[*b]) > crease {
                let (a, b) = (find(&mut parent, *a), find(&mut parent, *b));
                parent[b] = a;
            }
        }
    }
    let mut ids: HashMap<(u32, usize), u32> = HashMap::new();
    let mut vertices = vec![];
    let mut vertex_normals: Vec<V3> = vec![];
    let mut faces = vec![];
    for (i, t) in mesh.faces.iter().enumerate() {
        let group = find(&mut parent, i);
        let mut face = [0_u32; 3];
        for (corner, &original) in t.iter().enumerate() {
            let id = *ids.entry((original, group)).or_insert_with(|| {
                vertices.push(points[original as usize]);
                vertex_normals.push(V3::ZERO);
                (vertices.len() - 1) as u32
            });
            vertex_normals[id as usize] = vertex_normals[id as usize] + normals[i] * areas[i];
            face[corner] = id;
        }
        faces.push(face);
    }
    let mut position_bytes = vec![];
    let mut normal_bytes = vec![];
    for (p, n) in vertices.iter().zip(vertex_normals) {
        for x in p.to_array() {
            let f = x as f32;
            ensure!((f as f64 - x).abs() < 0.0001, "viewer position precision");
            position_bytes.extend_from_slice(&f.to_le_bytes());
        }
        let length = n.norm();
        let n = if length > 1e-15 { n / length } else { V3::ZERO };
        for x in n.to_array() {
            normal_bytes.extend_from_slice(&((x * 32767.).round_ties_even() as i16).to_le_bytes());
        }
    }
    let wide = vertices.len() > 65536;
    let mut index_bytes = vec![];
    for t in &faces {
        for &i in t {
            if wide {
                index_bytes.extend_from_slice(&i.to_le_bytes());
            } else {
                index_bytes.extend_from_slice(&(i as u16).to_le_bytes());
            }
        }
    }
    let mut edge_counts: HashMap<(u32, u32), i32> = HashMap::new();
    for t in &mesh.faces {
        for j in 0..3 {
            *edge_counts.entry((t[j], t[(j + 1) % 3])).or_default() += 1;
        }
    }
    let closed = edge_counts
        .iter()
        .all(|(&(a, b), &count)| count == 1 && edge_counts.get(&(b, a)) == Some(&1));
    let volume = hsm_kernel::mass::signed_volume(&points, &mesh.faces);
    Ok(
        json!({"v":STANDARD.encode(position_bytes),"n":STANDARD.encode(normal_bytes),"f":STANDARD.encode(index_bytes),
        "indexType":if wide {"uint32"}else{"uint16"},"sourceFaceCount":mesh.faces.len(),"sourceVolumeMm3":volume,"sourceClosed":closed}),
    )
}

fn build(root: &Path, cad: &Path, output: &Path) -> Result<()> {
    let items: Vec<Info> =
        serde_json::from_slice(&std::fs::read(cad.join("display-meshes.json"))?)?;
    let info: BTreeMap<_, _> = items.into_iter().map(|p| (p.name.clone(), p)).collect();
    let binding: Value = serde_json::from_slice(&std::fs::read(cad.join("motion-geometry.json"))?)?;
    let references: Value =
        serde_json::from_slice(&std::fs::read(cad.join("reference-source.json"))?)?;
    for (path, expected) in binding["motion"]["mechanical_sources"]
        .as_object()
        .context("mechanical sources")?
    {
        ensure!(
            Some(sha256(root.join(path))?.as_str()) == expected.as_str(),
            "mechanical source differs: {path}"
        );
    }
    ensure!(
        Some(sha256(cad.join("reference-meshes.npz"))?.as_str())
            == references["mesh_sha256"].as_str(),
        "pinned reference meshes differ"
    );
    let d = Design::read(cad.join("design.json"))?;
    let design = serde_json::to_value(&d)?;
    for (key, value) in design.as_object().unwrap() {
        ensure!(
            &binding["motion"][key] == value,
            "rebuild the CAD after changing design.json"
        );
    }
    let pivot = d.pivot();
    let mut parts = vec![];
    for filename in ["assembly-meshes.npz", "reference-meshes.npz"] {
        for (name, mut mesh) in load_meshes(cad.join(filename))? {
            let (group, category) = info
                .get(&name)
                .map(|p| (p.group.as_str(), p.category.as_str()))
                .unwrap_or((
                    if name.starts_with("gun:") {
                        "pitch"
                    } else {
                        "fixed"
                    },
                    "reference",
                ));
            if name.starts_with("gun:") {
                mesh = mesh.transformed(&d.gun_transform());
            }
            if ["pitch", "yaw"].contains(&group) {
                mesh = mesh.transformed(&Affine::translation(-pivot));
            }
            let mut row = display(&mesh).with_context(|| format!("viewer body {name}"))?;
            if ["print", "liner"].contains(&category) {
                ensure!(
                    row["sourceClosed"] == true
                        && row["sourceVolumeMm3"].as_f64().is_some_and(|v| v > 0.),
                    "{name}: closed positive printable volume"
                );
            }
            row["name"] = json!(name);
            row["group"] = json!(group);
            row["category"] = json!(category);
            parts.push(row);
        }
    }
    let payload = json!({"revision":d.revision,"geometrySha256":binding["sha256"],"meshFormat":"creased-f32-v1","pivot":pivot.to_array(),"softLimitDeg":d.soft_limit_deg,"parts":parts});
    std::fs::create_dir_all(output.parent().context("viewer output directory")?)?;
    let mut gzip = GzBuilder::new()
        .mtime(0)
        .write(std::fs::File::create(output)?, Compression::default());
    gzip.write_all(&serde_json::to_vec(&payload)?)?;
    gzip.finish()?;
    println!(
        "{}",
        json!({"path":output,"bytes":std::fs::metadata(output)?.len(),"parts":parts.len()})
    );
    Ok(())
}

fn main() -> Result<()> {
    let root = root();
    let mut args = std::env::args_os().skip(1);
    let cad = args
        .next()
        .map(PathBuf::from)
        .unwrap_or_else(|| root.join(DIRECTORY));
    let output = args
        .next()
        .map(PathBuf::from)
        .unwrap_or_else(|| root.join("web/public/assemblies/pgfun-positioner.json.gz"));
    if args.next().is_some() {
        bail!("usage: positioner-view [<fixture directory> [<viewer output>]]");
    }
    hsm_kernel::reads::begin();
    build(&root, &cad, &output)
}
