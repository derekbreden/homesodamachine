//! Pasted picks locate nearby surfaces in existing fine, print and viewer exports.
use crate::{
    math::*,
    pick_format::{self, Source, Via},
};
use anyhow::{Context, Result, ensure};
use hsm_geometry::{payload, scene};
use hsm_kernel::{
    face::{Face, Surface as NativeSurface},
    import,
};
use regex::Regex;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{
    fs,
    io::Read,
    path::{Path, PathBuf},
    sync::OnceLock,
};

pub const SURFACES: [&str; 3] = ["authored", "printed", "drawn"];
#[derive(Clone, Debug, Serialize)]
pub struct Probe {
    pub label: String,
    pub point: V3,
}
#[derive(Clone, Debug)]
pub struct Options {
    pub radius: f64,
    pub surfaces: Vec<String>,
    pub rows: usize,
}
impl Default for Options {
    fn default() -> Self {
        Self {
            radius: 1.,
            surfaces: SURFACES.map(str::to_owned).to_vec(),
            rows: 6,
        }
    }
}
#[derive(Clone, Debug, Serialize)]
#[serde(tag = "kind", rename_all = "kebab-case")]
pub enum Description {
    Plane {
        normal: V3,
    },
    Cylinder {
        radius: f64,
        axis: V3,
        direction: V3,
    },
    Curved {
        surface: String,
    },
}
#[derive(Clone, Debug, Serialize)]
pub struct Reading {
    pub body: String,
    pub description: Description,
    pub on: V3,
    pub distance: f64,
    pub facets: usize,
    pub span: V3,
    pub sources: Vec<Option<Source>>,
}
#[derive(Clone, Debug, Serialize)]
pub struct SurfaceReading {
    pub surface: String,
    pub file: Option<PathBuf>,
    pub digest: Option<String>,
    pub representation: Option<String>,
    pub requested: bool,
    pub error: Option<String>,
    pub source: Option<String>,
    pub decimation: Option<Decimation>,
    pub probes: Vec<Vec<Reading>>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Decimation {
    pub dev: f64,
    pub bound: f64,
}
#[derive(Clone, Debug, Serialize)]
pub struct Report {
    pub file: PathBuf,
    pub radius: f64,
    pub probes: Vec<Probe>,
    pub surfaces: Vec<SurfaceReading>,
}
fn point_regex() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        let n = r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)";
        Regex::new(&format!(r"x={n}\s+y={n}\s+z={n}")).unwrap()
    })
}

/// Directions introduce no location; labels cannot add accidental probe coordinates.
pub fn points(text: &str) -> Result<Vec<Probe>> {
    let mut found = Vec::new();
    for raw in text.lines() {
        let line = raw.trim();
        if line.is_empty() || line.starts_with("file:") || line.starts_with("solid:") {
            continue;
        }
        let line = line.split(['"', '“']).next().unwrap_or(line);
        let tag = line.split_once(':').map_or("?", |(tag, _)| tag);
        let mut seen = 0;
        for captures in point_regex().captures_iter(line) {
            let full = captures.get(0).unwrap();
            let lead = line[..full.start()]
                .trim_end()
                .split_whitespace()
                .last()
                .unwrap_or("")
                .trim_matches('·');
            if ["n", "dir", "axis"].contains(&lead) {
                continue;
            }
            let point = [
                captures[1].parse::<f64>()?,
                captures[2].parse()?,
                captures[3].parse()?,
            ];
            ensure!(
                point.iter().all(|v| v.is_finite()),
                "pick coordinates must be finite"
            );
            seen += 1;
            let label = if seen == 1 {
                tag.into()
            } else if tag == "edge" {
                format!("{tag} →")
            } else {
                format!("{tag} {seen}")
            };
            found.push(Probe { label, point });
        }
    }
    Ok(found)
}
pub fn source(root: &Path, text: &str) -> Result<PathBuf> {
    let named = text
        .lines()
        .find_map(|line| {
            line.trim()
                .strip_prefix("file:")
                .map(|path| path.split('·').next().unwrap().trim())
        })
        .context("no file: line in the pick")?;
    let named = named.strip_suffix(".mesh").unwrap_or(named);
    let path = PathBuf::from(named);
    Ok(if path.is_absolute() {
        path
    } else {
        root.join(path)
    })
}
fn named_bodies(text: &str) -> Vec<String> {
    text.lines()
        .filter_map(|line| {
            line.trim()
                .strip_prefix("solid:")
                .map(str::trim)
                .filter(|v| !v.is_empty())
                .map(str::to_owned)
        })
        .collect()
}
fn wanted(name: &str, names: &[String]) -> bool {
    names.is_empty()
        || names.iter().any(|selected| {
            name == selected
                || name.strip_suffix("/0") == Some(selected.as_str())
                || name
                    .rsplit_once('/')
                    .is_some_and(|(body, index)| body == selected && index.parse::<u32>().is_ok())
        })
}
fn near_triangle(p: V3, radius: f64, triangle: [V3; 3]) -> bool {
    (0..3).all(|axis| {
        triangle.iter().any(|v| v[axis] <= p[axis] + radius)
            && triangle.iter().any(|v| v[axis] >= p[axis] - radius)
    })
}
struct Group {
    normal: V3,
    offset: f64,
    reading: Reading,
    low: V3,
    high: V3,
    key: Option<usize>,
}
struct FaceData {
    key: Option<usize>,
    description: Option<Description>,
    sources: Vec<Option<Source>>,
}
fn records(face: &Face) -> Vec<Option<Source>> {
    if let Some(records) = face.src.contributors() {
        return records
            .iter()
            .map(|record| serde_json::from_value(record.clone()).unwrap_or(None))
            .collect();
    }
    if face.record_null {
        return vec![None];
    }
    vec![Some(Source {
        src: face
            .src
            .recorded()
            .then(|| hsm_kernel::face::src_line(face.src)),
        op: (!face.op.is_empty()).then(|| face.op.into()),
        via: face.via.map(|via| Via {
            src: via
                .src
                .recorded()
                .then(|| hsm_kernel::face::src_line(via.src)),
            op: (!via.op.is_empty()).then(|| via.op.into()),
        }),
    })]
}
fn description(face: &Face) -> Description {
    match face.surface {
        NativeSurface::Plane { n, .. } => Description::Plane {
            normal: n.to_array(),
        },
        NativeSurface::Cylinder { p, d, r } => Description::Cylinder {
            radius: r,
            axis: p.to_array(),
            direction: d.to_array(),
        },
        NativeSurface::Cone { .. } => Description::Curved {
            surface: "cone".into(),
        },
        NativeSurface::Sphere { .. } => Description::Curved {
            surface: "sphere".into(),
        },
        NativeSurface::Torus { .. } => Description::Curved {
            surface: "torus".into(),
        },
        NativeSurface::Free { kind } => Description::Curved {
            surface: kind.into(),
        },
    }
}
fn extend_sources(target: &mut Vec<Option<Source>>, sources: Vec<Option<Source>>) {
    for source in sources {
        if !target.contains(&source) {
            target.push(source);
        }
    }
}
fn measure(
    vertices: &[V3],
    triangles: &[[usize; 3]],
    body: &str,
    probes: &[Probe],
    options: &Options,
    face_data: impl Fn(usize) -> Option<FaceData>,
    into: &mut [Vec<Reading>],
) {
    let cosine = 5f64.to_radians().cos();
    for (probe, rows) in probes.iter().zip(into) {
        let mut groups = Vec::<Group>::new();
        for (index, face) in triangles.iter().enumerate() {
            let triangle = face.map(|i| vertices[i]);
            if !near_triangle(probe.point, options.radius, triangle) {
                continue;
            }
            let normal = unit(cross(
                sub(triangle[1], triangle[0]),
                sub(triangle[2], triangle[0]),
            ));
            if normal == [0.; 3] {
                continue;
            }
            let on = closest(probe.point, triangle[0], triangle[1], triangle[2]);
            let distance = length(sub(probe.point, on));
            if distance > options.radius {
                continue;
            }
            let offset = dot(normal, triangle[0]);
            let native = face_data(index);
            let key = native.as_ref().and_then(|data| data.key);
            let group = groups.iter_mut().find(|g| {
                if let Some(key) = key {
                    g.key == Some(key)
                } else {
                    g.key.is_none()
                        && dot(g.normal, normal) >= cosine
                        && (g.offset - offset).abs() <= 0.02
                }
            });
            let low = std::array::from_fn(|axis| {
                triangle
                    .iter()
                    .map(|v| v[axis])
                    .fold(f64::INFINITY, f64::min)
            });
            let high = std::array::from_fn(|axis| {
                triangle
                    .iter()
                    .map(|v| v[axis])
                    .fold(f64::NEG_INFINITY, f64::max)
            });
            if let Some(group) = group {
                group.reading.facets += 1;
                for axis in 0..3 {
                    group.low[axis] = group.low[axis].min(low[axis]);
                    group.high[axis] = group.high[axis].max(high[axis]);
                }
                if distance < group.reading.distance {
                    group.reading.on = on;
                    group.reading.distance = distance;
                }
                if let Some(data) = native {
                    extend_sources(&mut group.reading.sources, data.sources);
                }
            } else {
                let (description, sources) = native
                    .map(|data| {
                        (
                            data.description.unwrap_or(Description::Plane { normal }),
                            data.sources,
                        )
                    })
                    .unwrap_or((Description::Plane { normal }, vec![]));
                groups.push(Group {
                    normal,
                    offset,
                    key,
                    low,
                    high,
                    reading: Reading {
                        body: body.into(),
                        description,
                        on,
                        distance,
                        facets: 1,
                        span: [0.; 3],
                        sources,
                    },
                });
            }
        }
        rows.extend(groups.into_iter().map(|mut group| {
            group.reading.span = sub(group.high, group.low);
            group.reading
        }));
    }
}
fn imported(
    body: import::Imported,
    names: &[String],
    probes: &[Probe],
    options: &Options,
    into: &mut [Vec<Reading>],
) {
    if !wanted(&body.name, names) {
        return;
    }
    let vertices = body
        .solid
        .verts()
        .iter()
        .map(|v| v.to_array())
        .collect::<Vec<_>>();
    let triangles = body
        .solid
        .tris()
        .iter()
        .map(|t| t.map(|v| v as usize))
        .collect::<Vec<_>>();
    measure(
        &vertices,
        &triangles,
        &body.name,
        probes,
        options,
        |triangle| {
            let key = body.solid.face_of()[triangle] as usize;
            let face = &body.solid.faces()[key];
            Some(FaceData {
                key: Some(key),
                description: Some(description(face)),
                sources: records(face),
            })
        },
        into,
    );
}
fn file_digest(path: &Path) -> Result<String> {
    let mut file = fs::File::open(path)?;
    let mut hash = Sha256::new();
    let mut block = [0u8; 64 * 1024];
    loop {
        let count = file.read(&mut block)?;
        if count == 0 {
            break;
        }
        hash.update(&block[..count]);
    }
    Ok(format!("{:x}", hash.finalize()))
}
fn flat(root: &Path, bytes: &[u8]) -> Result<Vec<u8>> {
    if scene::is_scene(bytes) {
        scene::flatten_with(bytes, |sha| {
            Ok(fs::read(
                root.join(format!(".cache/meshes/scene-assets/{sha}.mesh")),
            )?)
        })
    } else {
        Ok(bytes.to_vec())
    }
}
fn measured_path(root: &Path, step: &Path, kind: &str) -> Option<PathBuf> {
    match kind {
        "authored" => {
            let model = PathBuf::from(format!("{}.npz", step.display()));
            if model.is_file() {
                Some(model)
            } else {
                step.is_file().then(|| step.to_owned())
            }
        }
        "printed" => {
            let path = step.with_extension("stl");
            path.is_file().then_some(path)
        }
        "drawn" => {
            let path = PathBuf::from(format!("{}.mesh", step.display()));
            path.is_file().then_some(path)
        }
        _ => {
            let _ = root;
            None
        }
    }
}
fn load(
    root: &Path,
    step: &Path,
    kind: &str,
    text: &str,
    probes: &[Probe],
    options: &Options,
) -> SurfaceReading {
    let requested = options.surfaces.iter().any(|surface| surface == kind);
    let path = measured_path(root, step, kind);
    let mut output = SurfaceReading {
        surface: kind.into(),
        file: path.clone(),
        digest: None,
        representation: None,
        requested,
        error: None,
        source: None,
        decimation: None,
        probes: probes.iter().map(|_| vec![]).collect(),
    };
    if !requested {
        return output;
    }
    let Some(path) = path else {
        output.error = Some("export is absent".into());
        return output;
    };
    let names = named_bodies(text);
    let result = (|| -> Result<()> {
        if kind == "authored" {
            if path.extension().is_some_and(|ext| ext == "npz") {
                output.representation = Some("native fine model".into());
                import::visit_model(&path, |_, body| {
                    imported(body, &names, probes, options, &mut output.probes);
                    Ok(())
                })?;
            } else {
                let bytes = fs::read(&path)?;
                let sha = scene::digest(&bytes);
                let native = bytes[..bytes.len().min(200)]
                    .windows(hsm_kernel::step::MARK.len())
                    .any(|window| window == hsm_kernel::step::MARK.as_bytes());
                let payload = if native {
                    PathBuf::from(format!("{}.mesh", path.display()))
                } else {
                    root.join(format!(".cache/hsm/import/{sha}.step.mesh"))
                };
                let data = fs::read(&payload).with_context(|| {
                    format!("no existing STEP import payload at {}", payload.display())
                })?;
                let header = scene::header(&data)?.0;
                ensure!(
                    !native || header["src"] == sha,
                    "STEP payload source does not match the STEP"
                );
                output.representation = Some("existing STEP import payload".into());
                output.source = Some(sha);
                output.file = Some(payload.clone());
                for body in import::bodies(&flat(root, &data)?, &step.to_string_lossy())? {
                    imported(body, &names, probes, options, &mut output.probes);
                }
            }
        } else if kind == "printed" {
            output.representation = Some("printed STL".into());
            let mesh = hsm_print_prep::mesh::Mesh::read_stl_exact(&path)?;
            measure(
                &mesh.vertices,
                &mesh.faces,
                "printed",
                probes,
                options,
                |_| None,
                &mut output.probes,
            );
        } else {
            output.representation = Some("viewer payload".into());
            let bytes = fs::read(&path)?;
            let header = scene::header(&bytes)?.0;
            output.source = header["src"].as_str().map(str::to_owned);
            output.decimation = serde_json::from_value(header["cut"].clone()).ok();
            let payload = payload::decode(&flat(root, &bytes)?)?;
            for mesh in payload.meshes {
                if !wanted(&mesh.name, &names) {
                    continue;
                }
                let vertices = mesh
                    .shape
                    .vertices()
                    .iter()
                    .map(|p| [p.x, p.y, p.z])
                    .collect::<Vec<_>>();
                let triangles = mesh
                    .shape
                    .indices()
                    .iter()
                    .map(|t| t.map(|v| v as usize))
                    .collect::<Vec<_>>();
                measure(
                    &vertices,
                    &triangles,
                    &mesh.name,
                    probes,
                    options,
                    |triangle| {
                        let group = mesh.faces.iter().position(|range| {
                            range[0] as usize <= triangle && triangle <= range[1] as usize
                        })?;
                        let records = mesh.face_sources.as_ref()?.get(group)?;
                        Some(FaceData {
                            key: None,
                            description: None,
                            sources: records
                                .iter()
                                .map(|record| {
                                    serde_json::from_value(record.clone()).unwrap_or(None)
                                })
                                .collect(),
                        })
                    },
                    &mut output.probes,
                );
            }
        }
        if let Some(path) = &output.file {
            output.digest = Some(file_digest(path)?);
        }
        for rows in &mut output.probes {
            rows.sort_by(|a, b| {
                a.distance
                    .total_cmp(&b.distance)
                    .then_with(|| a.body.cmp(&b.body))
            });
        }
        Ok(())
    })();
    if let Err(error) = result {
        output.error = Some(format!("{error:#}"));
    }
    output
}
pub fn read(root: &Path, text: &str, options: &Options) -> Result<Report> {
    ensure!(
        options.radius.is_finite() && options.radius > 0.,
        "radius must be positive and finite"
    );
    ensure!(
        options
            .surfaces
            .iter()
            .all(|name| SURFACES.contains(&name.as_str())),
        "surfaces are authored,printed,drawn"
    );
    let file = source(root, text)?;
    let probes = points(text)?;
    ensure!(!probes.is_empty(), "no coordinates in the pick");
    let surfaces = SURFACES
        .iter()
        .map(|kind| load(root, &file, kind, text, &probes, options))
        .collect();
    Ok(Report {
        file,
        radius: options.radius,
        probes,
        surfaces,
    })
}
pub fn print(report: &Report, options: &Options) {
    println!("{} · window {} mm", report.file.display(), report.radius);
    for surface in &report.surfaces {
        let note = if !surface.requested {
            "not requested".into()
        } else if let Some(error) = &surface.error {
            error.clone()
        } else {
            format!(
                "{} · {}",
                surface
                    .file
                    .as_ref()
                    .map_or_else(|| "absent".into(), |path| path.display().to_string()),
                surface.representation.as_deref().unwrap_or("export")
            )
        };
        println!("  {:<9} {note}", surface.surface);
    }
    for (index, probe) in report.probes.iter().enumerate() {
        println!("\n  {} {}", probe.label, pick_format::fpt(probe.point));
        let mut located = Vec::new();
        for surface in report
            .surfaces
            .iter()
            .filter(|s| s.requested && s.error.is_none())
        {
            let rows = &surface.probes[index];
            if let Some(first) = rows.first() {
                located.push(format!("{} {:.3}", surface.surface, first.distance));
            }
            for row in rows.iter().take(if options.rows == 0 {
                usize::MAX
            } else {
                options.rows
            }) {
                let kind = match &row.description {
                    Description::Plane { normal } => {
                        format!("plane · n {}", pick_format::fpt(*normal))
                    }
                    Description::Cylinder {
                        radius, direction, ..
                    } => format!(
                        "cylinder · r={radius:.3} · dir {}",
                        pick_format::fpt(*direction)
                    ),
                    Description::Curved { surface } => surface.clone(),
                };
                println!(
                    "    {:<9} {} · {kind} · thru {} · d {:.3} · {} facets · span {:.3} × {:.3} × {:.3}",
                    surface.surface,
                    row.body,
                    pick_format::fpt(row.on),
                    row.distance,
                    row.facets,
                    row.span[0],
                    row.span[1],
                    row.span[2]
                );
                if !row.sources.is_empty() {
                    println!("              {}", pick_format::source_line(&row.sources));
                }
            }
            if rows.is_empty() {
                println!("    {:<9} nothing in the window", surface.surface);
            } else if options.rows > 0 && rows.len() > options.rows {
                println!("              … {} more", rows.len() - options.rows);
            }
        }
        println!(
            "    where     {}",
            if located.is_empty() {
                "no measured surface in the window".into()
            } else {
                located.join(" · ")
            }
        );
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn points_ignore_directions_and_label_coordinates() {
        let text = "file: hardware/part.step.mesh · decimated .2\nsolid: part\nedge: x=0 y=0 z=0 → x=1 y=2 z=3 · dir x=1 y=0 z=0\nface: plane · n x=0 y=0 z=1 · thru x=4 y=5 z=6\nclick: x=7 y=8 z=9 \"x=100 y=200 z=300\"";
        let probes = points(text).unwrap();
        assert_eq!(probes.len(), 4);
        assert_eq!(probes[1].label, "edge →");
        assert_eq!(probes[3].point, [7., 8., 9.]);
        assert_eq!(
            source(Path::new("/repo"), text).unwrap(),
            PathBuf::from("/repo/hardware/part.step")
        );
    }
    #[test]
    fn nearest_planes_lead_and_keep_points_on_the_surface() {
        let vertices = vec![
            [0., -20., -20.],
            [0., 20., -20.],
            [0., 20., 20.],
            [0., -20., 20.],
            [0.25, -3.5, -3.5],
            [0.25, 3.5, -3.5],
            [0.25, 3.5, 3.5],
            [0.25, -3.5, 3.5],
        ];
        let faces = vec![[0, 1, 2], [0, 2, 3], [4, 5, 6], [4, 6, 7]];
        let probes = [Probe {
            label: "click".into(),
            point: [0.30, 0., 0.],
        }];
        let mut into = vec![vec![]];
        measure(
            &vertices,
            &faces,
            "fixture",
            &probes,
            &Options::default(),
            |_| None,
            &mut into,
        );
        into[0].sort_by(|a, b| a.distance.total_cmp(&b.distance));
        assert!((into[0][0].distance - 0.05).abs() < 1e-10);
        assert_eq!(into[0][0].on[0], 0.25);
        assert!((into[0][1].distance - 0.30).abs() < 1e-10);
    }
    #[test]
    fn whole_facets_intersect_the_window_even_when_centers_are_far() {
        let vertices = vec![[0., -100., -100.], [0., 100., -100.], [0., 0., 100.]];
        let mut into = vec![vec![]];
        measure(
            &vertices,
            &[[0, 1, 2]],
            "wide",
            &[Probe {
                label: "click".into(),
                point: [0.1, 0., 0.],
            }],
            &Options::default(),
            |_| None,
            &mut into,
        );
        assert_eq!(into[0].len(), 1);
        assert!((into[0][0].distance - 0.1).abs() < 1e-10);
    }
}
