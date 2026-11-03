//! Fine archives are reference streams: unchanged numeric members retain their bytes.
use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{
    collections::BTreeMap,
    fs::File,
    io::{Cursor, Read, Seek, Write},
    path::{Component, Path, PathBuf},
};
use zip::{ZipArchive, ZipWriter, write::SimpleFileOptions};

#[derive(Clone, Copy)]
pub struct Frame(pub [[f64; 4]; 3]);
impl Frame {
    pub fn read(value: Option<&Value>) -> Result<Self> {
        let mut out = Self([[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.]]);
        if let Some(value) = value.filter(|v| !v.is_null()) {
            let rows = value.as_array().context("frame must be 3x4 or 4x4")?;
            ensure!(rows.len() == 3 || rows.len() == 4, "frame rows");
            for r in 0..3 {
                let row = rows[r].as_array().context("frame row")?;
                ensure!(row.len() == 4, "frame columns");
                for c in 0..4 {
                    out.0[r][c] = row[c].as_f64().context("frame number")?;
                    ensure!(out.0[r][c].is_finite(), "nonfinite frame");
                }
            }
        }
        ensure!(out.det().abs() > 1e-15, "singular frame");
        Ok(out)
    }
    pub fn rigid(&self) -> bool {
        (0..3).all(|r| {
            (0..3).all(|c| {
                let dot: f64 = (0..3).map(|k| self.0[r][k] * self.0[c][k]).sum();
                (dot - if r == c { 1. } else { 0. }).abs() < 1e-12
            })
        })
    }
    pub fn identity(&self) -> bool {
        self.0 == [[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.]]
    }
    pub fn det(&self) -> f64 {
        let a = &self.0;
        a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
            - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
            + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
    }
    pub fn direction(&self, p: [f64; 3]) -> [f64; 3] {
        std::array::from_fn(|r| (0..3).map(|c| self.0[r][c] * p[c]).sum())
    }
    pub fn point(&self, p: [f64; 3]) -> [f64; 3] {
        let p = self.direction(p);
        std::array::from_fn(|r| p[r] + self.0[r][3])
    }
    pub fn normal(&self, p: [f64; 3]) -> [f64; 3] {
        let a = &self.0;
        let d = self.det();
        let co = [
            [
                (a[1][1] * a[2][2] - a[1][2] * a[2][1]) / d,
                (a[1][2] * a[2][0] - a[1][0] * a[2][2]) / d,
                (a[1][0] * a[2][1] - a[1][1] * a[2][0]) / d,
            ],
            [
                (a[0][2] * a[2][1] - a[0][1] * a[2][2]) / d,
                (a[0][0] * a[2][2] - a[0][2] * a[2][0]) / d,
                (a[0][1] * a[2][0] - a[0][0] * a[2][1]) / d,
            ],
            [
                (a[0][1] * a[1][2] - a[0][2] * a[1][1]) / d,
                (a[0][2] * a[1][0] - a[0][0] * a[1][2]) / d,
                (a[0][0] * a[1][1] - a[0][1] * a[1][0]) / d,
            ],
        ];
        unit(std::array::from_fn(|r| {
            (0..3).map(|c| co[r][c] * p[c]).sum()
        }))
    }
}
fn unit(p: [f64; 3]) -> [f64; 3] {
    let n = p.into_iter().map(|v| v * v).sum::<f64>().sqrt();
    p.map(|v| v / n)
}
fn rounded(v: f64) -> f64 {
    (v * 1e9).round_ties_even() / 1e9
}

pub struct Model {
    pub names: Vec<String>,
    pub colors: Vec<Value>,
    pub document: Value,
    records: Vec<String>,
    archive: ZipArchive<File>,
}
impl Model {
    pub fn open(path: &Path) -> Result<Self> {
        let mut file = File::open(path).with_context(|| format!("model {}", path.display()))?;
        let mut hash = Sha256::new();
        let mut block = [0u8; 65536];
        loop {
            let n = file.read(&mut block)?;
            if n == 0 {
                break;
            }
            hash.update(&block[..n]);
        }
        hsm_kernel::reads::digest(path, &format!("{:x}", hash.finalize()));
        let mut archive = ZipArchive::new(File::open(path)?)?;
        let names = serde_json::from_slice(npy_data(&member(&mut archive, "names.npy")?)?)?;
        let colors = serde_json::from_slice(npy_data(&member(&mut archive, "colors.npy")?)?)?;
        let records = spans(npy_data(&member(&mut archive, "records.npy")?)?)?;
        let document = if archive
            .file_names()
            .any(|n| n.is_ok_and(|n| n == "document.npy"))
        {
            serde_json::from_slice(npy_data(&member(&mut archive, "document.npy")?)?)?
        } else {
            json!({})
        };
        Ok(Self {
            names,
            colors,
            document,
            records,
            archive,
        })
    }
    pub fn selected(&self, instance: &Value) -> Result<Vec<usize>> {
        let selection = instance.get("indices").and_then(Value::as_array);
        if let Some(rows) = selection {
            for index in rows {
                ensure!(
                    index
                        .as_u64()
                        .is_some_and(|i| (i as usize) < self.names.len()),
                    "model selection out of range"
                );
            }
        }
        Ok((0..self.names.len())
            .filter(|i| {
                selection.is_none_or(|rows| rows.iter().any(|v| v.as_u64() == Some(*i as u64)))
            })
            .collect())
    }
}
fn member<R: Read + Seek>(zip: &mut ZipArchive<R>, name: &str) -> Result<Vec<u8>> {
    let mut bytes = Vec::new();
    zip.by_name(name)?.read_to_end(&mut bytes)?;
    Ok(bytes)
}
fn npy_offset(raw: &[u8]) -> Result<usize> {
    ensure!(raw.starts_with(b"\x93NUMPY") && raw.len() > 10, "bad npy");
    let start = if raw[6] == 1 { 10 } else { 12 };
    let size = if start == 10 {
        u16::from_le_bytes(raw[8..10].try_into()?) as usize
    } else {
        u32::from_le_bytes(raw[8..12].try_into()?) as usize
    };
    ensure!(start + size <= raw.len(), "truncated npy");
    Ok(start + size)
}
fn npy_data(raw: &[u8]) -> Result<&[u8]> {
    Ok(&raw[npy_offset(raw)?..])
}
fn npy_text(raw: &[u8]) -> Vec<u8> {
    let mut head = format!(
        "{{'descr': '|u1', 'fortran_order': False, 'shape': ({},), }}",
        raw.len()
    )
    .into_bytes();
    while (10 + head.len() + 1) % 64 != 0 {
        head.push(b' ')
    }
    head.push(b'\n');
    let mut out = b"\x93NUMPY\x01\x00".to_vec();
    out.extend_from_slice(&(head.len() as u16).to_le_bytes());
    out.extend(head);
    out.extend(raw);
    out
}
fn spans(raw: &[u8]) -> Result<Vec<String>> {
    let text = std::str::from_utf8(raw)?;
    let mut out = Vec::new();
    let mut cursor = 1;
    let bytes = text.as_bytes();
    while cursor < bytes.len() {
        while cursor < bytes.len() && (bytes[cursor].is_ascii_whitespace() || bytes[cursor] == b',')
        {
            cursor += 1
        }
        if cursor == bytes.len() || bytes[cursor] == b']' {
            break;
        }
        let start = cursor;
        let mut depth = 0i64;
        let mut string = false;
        let mut escaped = false;
        loop {
            let c = bytes[cursor];
            cursor += 1;
            if string {
                if escaped {
                    escaped = false
                } else if c == b'\\' {
                    escaped = true
                } else if c == b'"' {
                    string = false
                }
            } else {
                match c {
                    b'"' => string = true,
                    b'[' | b'{' => depth += 1,
                    b']' | b'}' => depth -= 1,
                    _ => {}
                }
            }
            if depth == 0 && !string {
                break;
            }
            ensure!(cursor < bytes.len(), "records json");
        }
        out.push(text[start..cursor].to_owned());
    }
    Ok(out)
}
fn moved_records(raw: &str, frame: &Frame) -> Result<String> {
    let mut rows: Value = serde_json::from_str(raw)?;
    for row in rows.as_array_mut().context("entry records")? {
        if row.is_null() {
            continue;
        }
        for key in ["p", "c", "d", "n"] {
            if let Some(values) = row.get(key).and_then(Value::as_array) {
                let p = [
                    values[0].as_f64().context("record vector")?,
                    values[1].as_f64().context("record vector")?,
                    values[2].as_f64().context("record vector")?,
                ];
                let p = match key {
                    "p" | "c" => frame.point(p),
                    "n" => frame.normal(p),
                    _ => unit(frame.direction(p)),
                };
                row[key] = json!(p.map(rounded));
            }
        }
        for key in ["r", "R"] {
            if let Some(v) = row.get(key).and_then(Value::as_f64) {
                row[key] = json!(rounded(v * frame.det().abs().cbrt()));
            }
        }
        for value in row.as_object_mut().context("record")?.values_mut() {
            if value.is_f64() {
                *value = json!(rounded(value.as_f64().unwrap()));
            }
        }
    }
    Ok(serde_json::to_string(&rows)?)
}
struct NumericPart {
    v: Vec<u8>,
    t: Vec<u8>,
    f: Vec<u8>,
    records: String,
}
fn split_parts(path: &Path, index: usize, frame: &Frame) -> Result<Vec<NumericPart>> {
    let source = hsm_kernel::import::model(path)?;
    let source = source.get(index).context("component source index")?;
    let parts = super::component_order::in_frame(&source.solid, &frame.0)?;
    let bodies: Vec<_> = parts
        .iter()
        .map(|solid| hsm_kernel::write::Body {
            name: &source.name,
            color: source.color,
            solid,
        })
        .collect();
    let bytes = hsm_kernel::step::model_bytes(&bodies);
    let mut archive = ZipArchive::new(Cursor::new(bytes))?;
    let records = spans(npy_data(&member(&mut archive, "records.npy")?)?)?;
    (0..parts.len())
        .map(|index| {
            Ok(NumericPart {
                v: member(&mut archive, &format!("V{index}.npy"))?,
                t: member(&mut archive, &format!("T{index}.npy"))?,
                f: member(&mut archive, &format!("F{index}.npy"))?,
                records: records[index].clone(),
            })
        })
        .collect()
}
pub fn component_count(path: &Path, index: usize) -> Result<usize> {
    let source = hsm_kernel::import::model(path)?;
    Ok(source
        .get(index)
        .context("component source index")?
        .solid
        .components()
        .len())
}
#[derive(Clone)]
struct Ref {
    path: PathBuf,
    index: usize,
    name: String,
    color: Value,
    frame: Frame,
    owned: Option<std::sync::Arc<NumericPart>>,
}
fn references(instances: &Value) -> Result<Vec<Ref>> {
    let mut rows = Vec::new();
    let mut sources = BTreeMap::new();
    for instance in instances.as_array().context("instances")? {
        let path = PathBuf::from(super::text(instance, "model")?);
        if !sources.contains_key(&path) {
            sources.insert(path.clone(), Model::open(&path)?);
        }
        let source = &sources[&path];
        let frame = Frame::read(instance.get("transform"))?;
        for index in source.selected(instance)? {
            let name = instance
                .get("name")
                .and_then(Value::as_str)
                .map(str::to_owned)
                .unwrap_or_else(|| {
                    format!(
                        "{}{}",
                        instance["prefix"].as_str().unwrap_or(""),
                        source.names[index]
                    )
                });
            let color = instance
                .get("color")
                .unwrap_or(&source.colors[index])
                .clone();
            if instance["split_components"].as_bool().unwrap_or(false) {
                let parts = split_parts(&path, index, &frame)?;
                let count = parts.len();
                for (ordinal, part) in parts.into_iter().enumerate() {
                    rows.push(Ref {
                        path: path.clone(),
                        index,
                        name: if count > 1 {
                            format!("{name}/{}", ordinal + 1)
                        } else {
                            name.clone()
                        },
                        color: color.clone(),
                        frame,
                        owned: Some(std::sync::Arc::new(part)),
                    });
                }
            } else {
                rows.push(Ref {
                    path: path.clone(),
                    index,
                    name,
                    color,
                    frame,
                    owned: None,
                });
            }
        }
    }
    Ok(rows)
}
fn write_refs(rows: &[Ref], document: Option<&Value>, path: &Path) -> Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let temp = path.with_file_name(format!(
        ".{}.{}.tmp",
        path.file_name().unwrap().to_string_lossy(),
        std::process::id()
    ));
    let mut writer = ZipWriter::new(File::create(&temp)?);
    let options = SimpleFileOptions::default().compression_method(zip::CompressionMethod::Stored);
    let mut sources = BTreeMap::new();
    for row in rows {
        if !sources.contains_key(&row.path) {
            sources.insert(row.path.clone(), Model::open(&row.path)?);
        }
    }
    let mut records = Vec::new();
    for (ordinal, row) in rows.iter().enumerate() {
        let source = sources.get_mut(&row.path).unwrap();
        for kind in ["V", "T", "F"] {
            let mut bytes = if let Some(part) = &row.owned {
                match kind {
                    "V" => part.v.clone(),
                    "T" => part.t.clone(),
                    _ => part.f.clone(),
                }
            } else {
                member(&mut source.archive, &format!("{kind}{}.npy", row.index))?
            };
            if !row.frame.identity() && (kind == "V" || (kind == "T" && row.frame.det() < 0.)) {
                let offset = npy_offset(&bytes)?;
                if kind == "V" {
                    ensure!(
                        (bytes.len() - offset) % 24 == 0,
                        "vertex dtype must be f64 xyz"
                    );
                    for xyz in bytes[offset..].chunks_exact_mut(24) {
                        let p = std::array::from_fn(|c| {
                            f64::from_le_bytes(xyz[c * 8..c * 8 + 8].try_into().unwrap())
                        });
                        let p = row.frame.point(p);
                        for c in 0..3 {
                            xyz[c * 8..c * 8 + 8].copy_from_slice(&p[c].to_le_bytes());
                        }
                    }
                } else {
                    let head = std::str::from_utf8(&bytes[10..offset])?;
                    let width = if head.contains("i8") || head.contains("u8") {
                        8
                    } else {
                        4
                    };
                    for tri in bytes[offset..].chunks_exact_mut(width * 3) {
                        for c in 0..width {
                            tri.swap(width + c, 2 * width + c);
                        }
                    }
                }
            }
            writer.start_file(format!("{kind}{ordinal}.npy"), options)?;
            writer.write_all(&bytes)?;
        }
        let record = row
            .owned
            .as_ref()
            .map(|part| part.records.as_str())
            .unwrap_or(&source.records[row.index]);
        records.push(if row.frame.identity() {
            record.to_owned()
        } else {
            moved_records(record, &row.frame)?
        });
    }
    let names: Vec<_> = rows.iter().map(|r| &r.name).collect();
    let colors: Vec<_> = rows
        .iter()
        .map(|r| match r.color.as_array() {
            Some(c) => json!(
                c.iter()
                    .map(|x| rounded(x.as_f64().unwrap()))
                    .collect::<Vec<_>>()
            ),
            None => Value::Null,
        })
        .collect();
    for (name, raw) in [
        ("names", serde_json::to_vec(&names)?),
        ("colors", serde_json::to_vec(&colors)?),
        ("records", format!("[{}]", records.join(",")).into_bytes()),
    ] {
        writer.start_file(format!("{name}.npy"), options)?;
        writer.write_all(&npy_text(&raw))?;
    }
    if let Some(document) = document {
        writer.start_file("document.npy", options)?;
        writer.write_all(&npy_text(&serde_json::to_vec(document)?))?;
    }
    writer.finish()?;
    std::fs::rename(temp, path)?;
    Ok(())
}
pub fn physical(spec: &Value, output: &Path) -> Result<Value> {
    let name = spec["name"].as_str().unwrap_or("enclosure-assembly");
    let model = output.join(format!("{name}.step.npz"));
    let step = output.join(format!("{name}.step"));
    let mesh = output.join(format!("{name}.step.mesh"));
    let instances = spec.get("instances").context("physical instances")?;
    let rows = references(instances)?;
    write_refs(&rows, spec.get("document"), &model)?;
    let fine = hsm_kernel::import::model(&model)?;
    let bodies: Vec<_> = fine
        .iter()
        .map(|p| hsm_kernel::write::Body {
            name: &p.name,
            color: p.color,
            solid: &p.solid,
        })
        .collect();
    let bytes = hsm_kernel::step::step_bytes(&bodies, name)?;
    let src = super::digest(&bytes);
    super::put(&step, &bytes)?;
    let mut shown = super::payload::placed_surfaces(instances, &fine)?;
    shown.header["src"] = json!(src);
    if let Some(skins) = spec.get("presentation") {
        shown.graft(skins)?;
    }
    shown.write(&mesh)?;
    bind(&model, &mesh)?;
    Ok(
        json!({"files":[super::output_name(&step,output),super::output_name(&model,output),super::output_name(&mesh,output)],"bodies":fine.iter().map(|p|json!({"name":p.name})).collect::<Vec<_>>(),"model":model,"payload":mesh,"physical_step_sha256":src}),
    )
}
pub fn scene(spec: &Value, output: &Path) -> Result<Value> {
    let path = PathBuf::from(super::text(spec, "model")?);
    let model = Model::open(&path)?;
    let aliases = &spec["aliases"];
    let mut groups: Vec<(String, Vec<Ref>)> = Vec::new();
    for (index, name) in model.names.iter().enumerate() {
        let base = super::payload::body(name);
        let name = aliases[base].as_str().unwrap_or(base).to_owned();
        let at = groups.iter().position(|g| g.0 == name).unwrap_or_else(|| {
            groups.push((name.clone(), Vec::new()));
            groups.len() - 1
        });
        groups[at].1.push(Ref {
            path: path.clone(),
            index,
            name,
            color: model.colors[index].clone(),
            frame: Frame::read(None)?,
            owned: None,
        });
    }
    let mut rows = Vec::new();
    let outer: Vec<_> = groups
        .iter()
        .filter(|g| !g.0.starts_with("cold-core/"))
        .map(|g| g.0.clone())
        .collect();
    let inner: Vec<_> = groups
        .iter()
        .filter(|g| g.0.starts_with("cold-core/"))
        .map(|g| g.0.clone())
        .collect();
    for group in groups.iter().filter(|g| !g.0.starts_with("cold-core/")) {
        rows.extend(group.1.clone());
    }
    let env = &spec["envelope"];
    let ep = PathBuf::from(super::text(env, "path")?);
    let envelope = Model::open(&ep)?;
    let frame = Frame::read(env.get("transform"))?;
    for index in 0..envelope.names.len() {
        rows.push(Ref {
            path: ep.clone(),
            index,
            name: "foam-assembly".into(),
            color: env["color"].clone(),
            frame,
            owned: None,
        });
    }
    for group in groups.iter().filter(|g| g.0.starts_with("cold-core/")) {
        rows.extend(group.1.clone());
    }
    let mut doc = spec["document"].clone();
    if !doc.is_object() {
        doc = json!({})
    }
    let mut solids = outer;
    solids.push("foam-assembly".into());
    doc["solids"] = json!(solids);
    doc["core"] = json!(inner);
    let target = spec
        .get("file")
        .and_then(Value::as_str)
        .map(PathBuf::from)
        .unwrap_or_else(|| output.join("enclosure-assembly.npz"));
    write_refs(&rows, Some(&doc), &target)?;
    Ok(json!({"files":[super::output_name(&target,output)],"bodies":[],"model":target}))
}
fn relative(path: &Path, base: &Path) -> String {
    let a: Vec<_> = path.components().collect();
    let b: Vec<_> = base.components().collect();
    let common = a.iter().zip(&b).take_while(|(x, y)| x == y).count();
    let mut out = PathBuf::new();
    for c in &b[common..] {
        if matches!(c, Component::Normal(_)) {
            out.push("..");
        }
    }
    for c in &a[common..] {
        out.push(c.as_os_str());
    }
    out.to_string_lossy().into_owned()
}
pub fn bind(path: &Path, payload: &Path) -> Result<()> {
    let mut source = ZipArchive::new(File::open(path)?)?;
    let mut document = if source
        .file_names()
        .any(|n| n.is_ok_and(|n| n == "document.npy"))
    {
        serde_json::from_slice(npy_data(&member(&mut source, "document.npy")?)?)?
    } else {
        json!({})
    };
    document["presentation"] = json!({"path":relative(payload,path.parent().unwrap()),"sha256":super::digest(&super::read(payload)?)});
    let temp = path.with_file_name(format!(
        ".{}.{}.bind",
        path.file_name().unwrap().to_string_lossy(),
        std::process::id()
    ));
    let mut target = ZipWriter::new(File::create(&temp)?);
    let options = SimpleFileOptions::default().compression_method(zip::CompressionMethod::Stored);
    for index in 0..source.len() {
        let mut file = source.by_index(index)?;
        if file.name()? == "document.npy" {
            continue;
        }
        target.start_file(file.name()?, options)?;
        std::io::copy(&mut file, &mut target)?;
    }
    target.start_file("document.npy", options)?;
    target.write_all(&npy_text(&serde_json::to_vec(&document)?))?;
    target.finish()?;
    drop(source);
    std::fs::rename(temp, path)?;
    Ok(())
}
