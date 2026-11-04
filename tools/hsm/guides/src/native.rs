//! Surface and pixel calculations used by the guide artwork.
use anyhow::{Context, Result, ensure};
use hsm_build_data::payload::{self, Mesh};
use hsm_documents::interop::{self, Val, callback, note_io};
use serde_json::json;
use std::{
    collections::{HashMap, VecDeque},
    path::{Path, PathBuf},
};

fn arg(args: &[Val], n: usize) -> Result<Val> {
    args.get(n).cloned().context("guide primitive argument")
}
fn concrete(value: &Val) -> Result<Val> {
    if matches!(value, Val::Ref(_)) {
        Val::decode(callback(json!({"op":"snapshot","object":value.encode()?}))?)
    } else {
        Ok(value.clone())
    }
}
fn items(value: &Val) -> Result<Vec<Val>> {
    concrete(value)?.iter()
}
fn numbers(value: &Val) -> Result<Vec<f64>> {
    items(value)?.iter().map(Val::num).collect()
}
fn values(values: impl IntoIterator<Item = f64>) -> Val {
    Val::list(values.into_iter().map(Val::Float).collect())
}
fn mesh_value(mesh: Mesh) -> Result<Val> {
    let mut fields = vec![
        ("name".into(), Val::Str(mesh.name)),
        ("color".into(), Val::decode(mesh.color)?),
    ];
    if let Some(sources) = mesh.face_sources {
        fields.push((
            "face_sources".into(),
            Val::decode(serde_json::from_str(sources.get())?)?,
        ));
    }
    fields.extend([
        ("pos".into(), values(mesh.pos)),
        ("nrm".into(), values(mesh.nrm)),
        (
            "idx".into(),
            Val::list(mesh.idx.into_iter().map(|v| Val::Int(v as i64)).collect()),
        ),
        (
            "fac".into(),
            Val::list(mesh.fac.into_iter().map(|v| Val::Int(v as i64)).collect()),
        ),
    ]);
    if let Some(uv) = mesh.uv {
        fields.push(("uv".into(), values(uv)));
    }
    if let Some(col) = mesh.col {
        fields.push(("col".into(), values(col)));
    }
    Ok(Val::dict(fields))
}
fn json_text(value: Val) -> Result<String> {
    interop::builtin_module("json")
        .unwrap()
        .attr("dumps")?
        .call(
            vec![value],
            vec![(
                "separators".into(),
                Val::tuple(vec![",".into(), ":".into()]),
            )],
        )?
        .str()
}
fn read_meshes(path: &Path) -> Result<Val> {
    note_io(path, false);
    Ok(Val::list(
        payload::read(path)?
            .meshes
            .into_iter()
            .map(mesh_value)
            .collect::<Result<_>>()?,
    ))
}
fn mesh_bounds(path: &Path) -> Result<Val> {
    note_io(path, false);
    let data = payload::read(path)?;
    let mut result = vec![];
    for mesh in data.meshes {
        let mut lo = [f64::INFINITY; 3];
        let mut hi = [f64::NEG_INFINITY; 3];
        for p in mesh.pos.chunks_exact(3) {
            for axis in 0..3 {
                lo[axis] = lo[axis].min(p[axis]);
                hi[axis] = hi[axis].max(p[axis]);
            }
        }
        result.push((mesh.name.into(), Val::tuple(vec![values(lo), values(hi)])));
    }
    Ok(Val::dict(result))
}
fn moved_payload(name: &str, entry: &Val, root: &Path, out: &Path) -> Result<Val> {
    let source = root.join(entry.get("source_mesh".into())?.str()?);
    note_io(&source, false);
    let mut data = payload::read(&source)?;
    let action = entry.get("action".into())?;
    let prefix = action.get("prefix".into())?.str()?;
    let delta = numbers(&action.get("translation".into())?)?;
    ensure!(delta.len() == 3, "translation has three axes");
    let mut moved = vec![];
    for mesh in &mut data.meshes {
        if mesh.name.starts_with(&prefix) {
            for p in mesh.pos.chunks_exact_mut(3) {
                for axis in 0..3 {
                    p[axis] = ((p[axis] + delta[axis]) as f32) as f64;
                }
            }
            moved.push(Val::Str(mesh.name.clone()));
        }
    }
    ensure!(
        moved.len() == action.get("expected".into())?.integer()? as usize,
        "unexpected number of moving meshes"
    );
    data.src = None;
    data.cut = Some(serde_json::value::RawValue::from_string(json_text(
        Val::dict(vec![
            (
                "source_payload_sha256".into(),
                entry.get("source_mesh_sha256".into())?,
            ),
            ("action".into(), action),
        ]),
    )?)?);
    let target = out.join(format!("{name}.step.mesh"));
    payload::write(&target, &data)?;
    note_io(&target, true);
    entry.set(
        "render_mesh".into(),
        target
            .strip_prefix(root)?
            .to_string_lossy()
            .to_string()
            .into(),
    )?;
    entry.set(
        "render_mesh_sha256".into(),
        payload::digest(&target)?.into(),
    )?;
    entry.set("moved_meshes".into(), Val::list(moved))?;
    Ok(Val::Path(target))
}
fn registration(entry: &Val, report: &Val) -> Result<Val> {
    let matrix = numbers(&report.get("camera".into())?.get("view_proj".into())?)?;
    ensure!(matrix.len() == 16, "camera projection matrix");
    let size = numbers(&entry.get("size".into())?)?;
    let points = concrete(&entry.get("points".into())?)?;
    let mut result = vec![];
    for key in points.iter()? {
        let world = numbers(&points.get(key.clone())?.get("world".into())?)?;
        let p = [world[0], world[1], world[2], 1.];
        let mut clip = [0.; 4];
        for row in 0..4 {
            clip[row] = (0..4).map(|col| matrix[col * 4 + row] * p[col]).sum();
        }
        result.push((
            key,
            values([
                (clip[0] / clip[3] + 1.) * size[0] / 2.,
                (1. - clip[1] / clip[3]) * size[1] / 2.,
            ]),
        ));
    }
    Ok(Val::dict(vec![
        ("moved".into(), entry.get("moved_meshes".into())?),
        ("points".into(), Val::dict(result)),
    ]))
}
fn ice_colors(ice: &Val) -> Result<Val> {
    let mut light = [-0.25, -0.65, 1.];
    let length: f64 = light.iter().map(|v| v * v).sum::<f64>().sqrt();
    for v in &mut light {
        *v /= length;
    }
    fn linear(rgb: [u8; 3]) -> [f64; 3] {
        rgb.map(|v| {
            let c = v as f64 / 255.;
            if c <= 0.04045 {
                c / 12.92
            } else {
                ((c + 0.055) / 1.055).powf(2.4)
            }
        })
    }
    let dark = linear([0x75, 0x94, 0xa8]);
    let pale = linear([0xf0, 0xf9, 0xff]);
    for mesh in ice.iter()? {
        let normals = numbers(&mesh.get("nrm".into())?)?;
        let mut colors = vec![];
        for n in normals.chunks_exact(3) {
            let t =
                (0.25 + 0.8 * (n[0] * light[0] + n[1] * light[1] + n[2] * light[2])).clamp(0., 1.);
            for axis in 0..3 {
                colors.push((1. - t) * dark[axis] + t * pale[axis]);
            }
        }
        mesh.set("col".into(), values(colors))?;
    }
    Ok(Val::None)
}
fn drink_front(drink: &Val) -> Result<Val> {
    let normals = numbers(&drink.get("nrm".into())?)?;
    let indices = items(&drink.get("idx".into())?)?
        .iter()
        .map(|v| Ok(v.integer()? as usize))
        .collect::<Result<Vec<_>>>()?;
    let keep = indices
        .chunks_exact(3)
        .map(|t| normals[t[0] * 3 + 2] + normals[t[1] * 3 + 2] + normals[t[2] * 3 + 2] < 1.5)
        .collect::<Vec<_>>();
    let mut chosen = vec![];
    for (triangle, &yes) in indices.chunks_exact(3).zip(&keep) {
        if yes {
            chosen.extend(triangle.iter().map(|&v| Val::Int(v as i64)));
        }
    }
    drink.set("idx".into(), Val::list(chosen))?;
    let ranges = items(&drink.get("fac".into())?)?;
    let mut faces = vec![];
    let mut offset = 0i64;
    for range in ranges.chunks_exact(2) {
        let lo = range[0].integer()? as usize;
        let hi = range[1].integer()? as usize;
        let n = keep[lo..=hi].iter().filter(|&&v| v).count() as i64;
        if n > 0 {
            faces.extend([Val::Int(offset), Val::Int(offset + n - 1)]);
            offset += n;
        }
    }
    drink.set("fac".into(), Val::list(faces))?;
    Ok(Val::None)
}
fn exterior(mut mask: Vec<bool>, width: usize, height: usize) -> Result<Val> {
    ensure!(mask.len() == width * height, "silhouette raster size");
    if width == 0 || height == 0 {
        return Ok(Val::list(vec![]));
    }
    let mut outside = vec![false; mask.len()];
    let mut queue = VecDeque::new();
    for y in 0..height {
        for x in 0..width {
            let i = y * width + x;
            if (x == 0 || y == 0 || x == width - 1 || y == height - 1) && !mask[i] && !outside[i] {
                outside[i] = true;
                queue.push_back((x, y));
            }
        }
    }
    while let Some((x, y)) = queue.pop_front() {
        for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)] {
            let a = x as isize + dx;
            let b = y as isize + dy;
            if a >= 0 && b >= 0 && (a as usize) < width && (b as usize) < height {
                let i = b as usize * width + a as usize;
                if !mask[i] && !outside[i] {
                    outside[i] = true;
                    queue.push_back((a as usize, b as usize));
                }
            }
        }
    }
    for (v, external) in mask.iter_mut().zip(outside) {
        *v = !external;
    }
    type Point = (usize, usize);
    let mut edges: HashMap<Point, Vec<Point>> = HashMap::new();
    let mut order = vec![];
    for side in 0..4 {
        for y in 0..height {
            for x in 0..width {
                if !mask[y * width + x] {
                    continue;
                }
                let neighbour = match side {
                    0 => y > 0 && mask[(y - 1) * width + x],
                    1 => x + 1 < width && mask[y * width + x + 1],
                    2 => y + 1 < height && mask[(y + 1) * width + x],
                    _ => x > 0 && mask[y * width + x - 1],
                };
                if !neighbour {
                    let (a, b) = [
                        ((x, y), (x + 1, y)),
                        ((x + 1, y), (x + 1, y + 1)),
                        ((x + 1, y + 1), (x, y + 1)),
                        ((x, y + 1), (x, y)),
                    ][side];
                    if !edges.contains_key(&a) {
                        order.push(a);
                    }
                    edges.entry(a).or_default().push(b);
                }
            }
        }
    }
    let mut loops = vec![];
    let mut first = 0;
    while !edges.is_empty() {
        while !edges.contains_key(&order[first]) {
            first += 1;
        }
        let start = order[first];
        let mut point = start;
        let mut line = vec![point];
        loop {
            let options = edges
                .get_mut(&point)
                .context("silhouette edge continuation")?;
            let following = options.pop().unwrap();
            if options.is_empty() {
                edges.remove(&point);
            }
            line.push(following);
            point = following;
            if point == start {
                break;
            }
        }
        let mut keep = vec![line[0]];
        for i in 1..line.len() - 1 {
            let (a, b, c) = (line[i - 1], line[i], line[i + 1]);
            if (b.0 as i64 - a.0 as i64) * (c.1 as i64 - b.1 as i64)
                != (b.1 as i64 - a.1 as i64) * (c.0 as i64 - b.0 as i64)
            {
                keep.push(b);
            }
        }
        if keep.len() >= 3 {
            loops.push(Val::list(
                keep.into_iter()
                    .map(|(x, y)| Val::tuple(vec![Val::Int(x as i64), Val::Int(y as i64)]))
                    .collect(),
            ));
        }
    }
    Ok(Val::list(loops))
}
fn outlines(input: Val) -> Result<Val> {
    let rows = if matches!(input, Val::Ref(_)) {
        concrete(&input.attr("tolist")?.call(vec![], vec![])?)?
    } else {
        input
    };
    let rows = rows.iter()?;
    let height = rows.len();
    let width = rows.first().map(Val::len).transpose()?.unwrap_or(0);
    let mut pixels = vec![];
    for row in rows {
        ensure!(row.len()? == width, "ragged mask");
        pixels.extend(
            row.iter()?
                .iter()
                .map(Val::truthy)
                .collect::<Result<Vec<_>>>()?,
        );
    }
    exterior(pixels, width, height)
}
pub fn module() -> Result<Val> {
    let mut fields = vec![];
    fields.push((
        "read_meshes".into(),
        Val::function(|a, _| read_meshes(&PathBuf::from(arg(&a, 0)?.str()?))),
    ));
    fields.push((
        "mesh_bounds".into(),
        Val::function(|a, _| mesh_bounds(&PathBuf::from(arg(&a, 0)?.str()?))),
    ));
    fields.push((
        "moved_payload".into(),
        Val::function(|a, _| {
            moved_payload(
                &arg(&a, 0)?.str()?,
                &arg(&a, 1)?,
                &PathBuf::from(arg(&a, 2)?.str()?),
                &PathBuf::from(arg(&a, 3)?.str()?),
            )
        }),
    ));
    fields.push((
        "registration".into(),
        Val::function(|a, _| registration(&arg(&a, 0)?, &arg(&a, 1)?)),
    ));
    fields.push((
        "ice_colors".into(),
        Val::function(|a, _| ice_colors(&arg(&a, 0)?)),
    ));
    fields.push((
        "drink_front".into(),
        Val::function(|a, _| drink_front(&arg(&a, 0)?)),
    ));
    fields.push((
        "outlines".into(),
        Val::function(|a, _| outlines(arg(&a, 0)?)),
    ));
    fields.push((
        "alpha_outlines".into(),
        Val::function(|a, _| {
            let image = arg(&a, 0)?;
            let size = image.attr("size")?.iter()?;
            let width = size[0].integer()? as usize;
            let height = size[1].integer()? as usize;
            let threshold = arg(&a, 1)?.integer()? as u8;
            let data = image.attr("tobytes")?.call(vec![], vec![])?;
            let Val::Bytes(bytes) = data else {
                anyhow::bail!("alpha image bytes")
            };
            exterior(
                bytes.into_iter().map(|v| v >= threshold).collect(),
                width,
                height,
            )
        }),
    ));
    Ok(Val::namespace(fields))
}

pub fn files() -> Result<Val> {
    let mut fields = vec![];
    for name in ["copyfile", "copy2"] {
        fields.push((
            name.into(),
            Val::function(move |args, _| {
                let source = PathBuf::from(arg(&args, 0)?.str()?);
                let target = PathBuf::from(arg(&args, 1)?.str()?);
                note_io(&source, false);
                note_io(&target, true);
                std::fs::copy(&source, &target)?;
                if name == "copy2" {
                    let metadata = std::fs::metadata(&source)?;
                    let times = std::fs::FileTimes::new()
                        .set_modified(metadata.modified()?)
                        .set_accessed(metadata.accessed()?);
                    std::fs::File::options()
                        .write(true)
                        .open(&target)?
                        .set_times(times)?;
                }
                Ok(Val::Path(target))
            }),
        ));
    }
    fields.push((
        "which".into(),
        Val::function(|args, _| {
            let command = arg(&args, 0)?.str()?;
            let candidates = if command.contains('/') {
                vec![PathBuf::from(command)]
            } else {
                std::env::split_paths(&std::env::var_os("PATH").unwrap_or_default())
                    .map(|p| p.join(&command))
                    .collect()
            };
            use std::os::unix::fs::PermissionsExt;
            Ok(candidates
                .into_iter()
                .find(|p| {
                    std::fs::metadata(p)
                        .is_ok_and(|m| m.is_file() && m.permissions().mode() & 0o111 != 0)
                })
                .map(|p| Val::Str(p.to_string_lossy().to_string()))
                .unwrap_or(Val::None))
        }),
    ));
    Ok(Val::namespace(fields))
}
