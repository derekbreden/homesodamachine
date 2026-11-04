//! Fine archives are reference streams: unchanged numeric members retain their bytes.
use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{
    collections::{BTreeMap, BTreeSet},
    fs::File,
    io::{BufReader, BufWriter, Cursor, Read, Seek, SeekFrom, Write},
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
    path: PathBuf,
    records: Vec<String>,
    archive: ZipArchive<File>,
}
pub type Models = BTreeMap<PathBuf, Model>;
impl Model {
    pub fn open(path: &Path) -> Result<Self> {
        Self::open_headers(path, true, true)
    }
    fn for_visiting(path: &Path) -> Result<Self> {
        Self::open_headers(path, false, false)
    }
    fn open_headers(path: &Path, input: bool, records: bool) -> Result<Self> {
        if input {
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
        }
        let mut archive = ZipArchive::new(File::open(path)?)?;
        let names = serde_json::from_slice(npy_data(&member(&mut archive, "names.npy")?)?)?;
        let colors = serde_json::from_slice(npy_data(&member(&mut archive, "colors.npy")?)?)?;
        let records = if records {
            spans(npy_data(&member(&mut archive, "records.npy")?)?)?
        } else {
            Vec::new()
        };
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
            path: path.to_owned(),
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

    /// Decode selected bodies in stored order in one archive pass, releasing each after use.
    pub(super) fn visit_selected(
        &self,
        indices: &BTreeSet<usize>,
        visit: impl FnMut(usize, hsm_kernel::Imported) -> Result<()>,
    ) -> Result<()> {
        if indices.is_empty() {
            return Ok(());
        }
        hsm_kernel::import::visit_model_indices(&self.path, indices, visit)?;
        Ok(())
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
fn references(instances: &Value, sources: &mut Models) -> Result<Vec<Ref>> {
    let mut rows = Vec::new();
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
    write_refs_using(rows, document, path, &mut Models::new())
}
fn write_refs_using(
    rows: &[Ref], document: Option<&Value>, path: &Path, sources: &mut Models,
) -> Result<()> {
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
/// Write buffers directly to an atomic output, retaining the old file when bytes match.
pub(super) fn put_stream(
    path: &Path,
    write: impl FnOnce(&mut BufWriter<File>) -> Result<()>,
) -> Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let temp = path.with_file_name(format!(
        ".{}.{}.stream",
        path.file_name().unwrap().to_string_lossy(),
        std::process::id()
    ));
    let mut writer = BufWriter::new(File::create(&temp)?);
    write(&mut writer)?;
    writer.flush()?;
    drop(writer);
    let equal = if path.is_file()
        && std::fs::metadata(path)?.len() == std::fs::metadata(&temp)?.len()
    {
        let mut old = BufReader::new(File::open(path)?);
        let mut new = BufReader::new(File::open(&temp)?);
        let mut a = [0u8; 65536];
        let mut b = [0u8; 65536];
        loop {
            let n = old.read(&mut a)?;
            if n == 0 {
                break true;
            }
            new.read_exact(&mut b[..n])?;
            if a[..n] != b[..n] {
                break false;
            }
        }
    } else {
        false
    };
    if equal {
        std::fs::remove_file(temp)?;
    } else {
        std::fs::rename(temp, path)?;
    }
    Ok(())
}

fn stream_digest(path: &Path, input: bool) -> Result<String> {
    let mut file = File::open(path)?;
    let mut hash = Sha256::new();
    let mut buffer = [0u8; 65536];
    loop {
        let count = file.read(&mut buffer)?;
        if count == 0 {
            break;
        }
        hash.update(&buffer[..count]);
    }
    let digest = format!("{:x}", hash.finalize());
    if input {
        hsm_kernel::reads::digest(path, &digest);
    }
    Ok(digest)
}

fn step_string(text: &str) -> String {
    use std::fmt::Write;
    let mut out = String::from("'");
    for c in text.chars() {
        match c {
            '\'' => out.push_str("''"),
            '\\' => out.push_str("\\\\"),
            ' '..='~' => out.push(c),
            _ => {
                out.push_str("\\X2\\");
                for value in c.encode_utf16(&mut [0; 2]) {
                    write!(out, "{value:04X}").unwrap();
                }
                out.push_str("\\X0\\");
            }
        }
    }
    out.push('\'');
    out
}

struct StepEntities<'a> {
    writer: &'a mut BufWriter<File>,
    next: usize,
}
impl StepEntities<'_> {
    fn add(&mut self, body: impl AsRef<str>) -> Result<String> {
        self.parts(&[body.as_ref()])
    }
    fn parts(&mut self, pieces: &[&str]) -> Result<String> {
        let id = self.next;
        self.next += 1;
        write!(self.writer, "#{id} = ")?;
        for piece in pieces {
            self.writer.write_all(piece.as_bytes())?;
        }
        self.writer.write_all(b";\n")?;
        Ok(format!("#{id}"))
    }
    fn product(&mut self, context: &str, name: &str, shape: &str) -> Result<(String, String)> {
        let at = self.next;
        self.add(format!("SHAPE_DEFINITION_REPRESENTATION(#{},{shape})", at + 1))?;
        self.add(format!("PRODUCT_DEFINITION_SHAPE('','',#{})", at + 2))?;
        self.add(format!("PRODUCT_DEFINITION('design','',#{},#{})", at + 3, at + 6))?;
        self.add(format!("PRODUCT_DEFINITION_FORMATION('','',#{})", at + 4))?;
        let name = step_string(name);
        self.add(format!("PRODUCT({name},{name},'',(#{}))", at + 5))?;
        self.add(format!("PRODUCT_CONTEXT('',{context},'mechanical')"))?;
        self.add(format!("PRODUCT_DEFINITION_CONTEXT('part definition',{context},'design')"))?;
        Ok((format!("#{}", at + 2), format!("#{}", at + 4)))
    }
    fn placement(&mut self) -> Result<String> {
        let at = self.next;
        self.add(format!("AXIS2_PLACEMENT_3D('',#{},#{},#{})", at + 1, at + 2, at + 3))?;
        self.add("CARTESIAN_POINT('',(0.,0.,0.))")?;
        self.add("DIRECTION('',(0.,0.,1.))")?;
        self.add("DIRECTION('',(1.,0.,0.))")?;
        Ok(format!("#{at}"))
    }
    fn units(&mut self) -> Result<String> {
        let at = self.next;
        self.add(format!(
            "( GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{})) \
             GLOBAL_UNIT_ASSIGNED_CONTEXT((#{},#{},#{})) REPRESENTATION_CONTEXT('Context #1',\
             '3D Context with UNIT and UNCERTAINTY') )",
            at + 4, at + 1, at + 2, at + 3
        ))?;
        self.add("( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) )")?;
        self.add("( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) )")?;
        self.add("( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() )")?;
        self.add(format!(
            "UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),#{},'distance_accuracy_value','confusion accuracy')",
            at + 1
        ))?;
        Ok(format!("#{at}"))
    }
}

/// Keep the kernel's exact one-body tessellation and AP242 entity order while
/// releasing its simplification backend before importing the next stored body.
fn write_step_stream(model: &mut Model, path: &Path, root: &str) -> Result<String> {
    let count = model.names.len();
    put_stream(path, |writer| {
        if count == 1 {
            model.visit_selected(&BTreeSet::from([0]), |_, part| {
                let body = hsm_kernel::write::Body { name: &part.name, color: part.color, solid: &part.solid };
                writer.write_all(&hsm_kernel::step::step_bytes(&[body], root)?)?;
                Ok(())
            })?;
            return Ok(());
        }
        writer.write_all(b"ISO-10303-21;\nHEADER;\n")?;
        writeln!(writer, "FILE_DESCRIPTION(({}),'2;1');", step_string(hsm_kernel::step::MARK))?;
        writeln!(writer, "FILE_NAME({},'1970-01-01T00:00:00',(''),(''),'hsm-kernel','hsm-kernel','');", step_string(root))?;
        writer.write_all(b"FILE_SCHEMA(('AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF { 1 0 10303 442 1 1 4 }'));\nENDSEC;\nDATA;\n")?;
        let mut e = StepEntities { writer, next: 1 };
        e.add("APPLICATION_PROTOCOL_DEFINITION('international standard','ap242_managed_model_based_3d_engineering',2013,#2)")?;
        let app = e.add("APPLICATION_CONTEXT('Managed model based 3d engineering')")?;
        let shape = format!("#{}", e.next + 7);
        let (assembly, product) = e.product(&app, root, &shape)?;
        let at = e.next;
        let places: Vec<_> = (0..=count).map(|i| format!("#{}", at + 1 + 4 * i)).collect();
        let context = format!("#{}", at + 1 + 4 * (count + 1));
        let rep = e.add(format!("SHAPE_REPRESENTATION('',({}),{context})", places.join(",")))?;
        for expected in &places {
            ensure!(e.placement()? == *expected, "STEP placement order");
        }
        ensure!(e.units()? == context, "STEP unit order");
        e.add(format!("PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,({product}))"))?;
        let mut styled = Vec::new();
        model.visit_selected(&(0..count).collect(), |index, part| {
            let body = hsm_kernel::write::Body { name: &part.name, color: part.color, solid: &part.solid };
            let single = hsm_kernel::step::step_bytes(&[body], root)?;
            let text = std::str::from_utf8(&single)?;
            let entity = |kind: &str| -> Result<&str> {
                let start = text.find(kind).context("kernel STEP entity")?;
                let tail = &text[start..];
                Ok(&tail[..tail.find(";\n").context("kernel STEP entity end")?])
            };
            let triangles = entity("TRIANGULATED_SURFACE_SET('")?;
            let coordinates = entity("COORDINATES_LIST('")?;
            let (_, triangles) = triangles.strip_prefix("TRIANGULATED_SURFACE_SET('',#")
                .context("kernel surface set reference")?.split_once(',').context("kernel surface set")?;
            let shape = format!("#{}", e.next + 7);
            let (definition, product) = e.product(&app, &part.name, &shape)?;
            let own = format!("#{}", e.next);
            let set = format!("#{}", e.next + 1);
            let points = format!("TRIANGULATED_SURFACE_SET('',#{},", e.next + 2);
            e.add(format!("MANIFOLD_SURFACE_SHAPE_REPRESENTATION('',({},{set}),{context})", places[0]))?;
            e.parts(&[&points, triangles])?;
            e.add(coordinates)?;
            let at = e.next;
            e.add(format!("CONTEXT_DEPENDENT_SHAPE_REPRESENTATION(#{},#{})", at + 1, at + 3))?;
            e.add(format!(
                "( REPRESENTATION_RELATIONSHIP('','',{own},{rep}) REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION(#{}) \
                 SHAPE_REPRESENTATION_RELATIONSHIP() )", at + 2
            ))?;
            e.add(format!("ITEM_DEFINED_TRANSFORMATION('','',{},{})", places[0], places[index + 1]))?;
            e.add(format!("PRODUCT_DEFINITION_SHAPE('Placement','Placement of an item',#{})", at + 4))?;
            e.add(format!("NEXT_ASSEMBLY_USAGE_OCCURRENCE('{}',{},'',{assembly},{definition},$)", index + 1, step_string(&part.name)))?;
            e.add(format!("PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,({product}))"))?;
            if let Some(color) = part.color {
                styled.push((set, color));
            }
            Ok(())
        })?;
        if !styled.is_empty() {
            let at = e.next;
            let items: Vec<_> = (0..styled.len()).map(|i| format!("#{}", at + 1 + 8 * i)).collect();
            e.add(format!("MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',({}),{context})", items.join(",")))?;
            for (set, color) in styled {
                let at = e.next;
                e.add(format!("STYLED_ITEM('color',(#{}),{set})", at + 1))?;
                e.add(format!("PRESENTATION_STYLE_ASSIGNMENT((#{}))", at + 2))?;
                e.add(format!("SURFACE_STYLE_USAGE(.BOTH.,#{})", at + 3))?;
                e.add(format!("SURFACE_SIDE_STYLE('',(#{}))", at + 4))?;
                e.add(format!("SURFACE_STYLE_FILL_AREA(#{})", at + 5))?;
                e.add(format!("FILL_AREA_STYLE('',(#{}))", at + 6))?;
                e.add(format!("FILL_AREA_STYLE_COLOUR('',#{})", at + 7))?;
                let color = color.map(|c| {
                    let c = c as f32 as f64;
                    let c = if c <= 0.0031308 { c * 12.92 } else { c.powf(1.0 / 2.4) * 1.055 - 0.055 };
                    let mut text = format!("{c:.12}");
                    while text.ends_with('0') { text.pop(); }
                    text
                });
                e.add(format!("COLOUR_RGB('',{},{},{})", color[0], color[1], color[2]))?;
            }
        }
        e.writer.write_all(b"ENDSEC;\nEND-ISO-10303-21;\n")?;
        Ok(())
    })?;
    stream_digest(path, false)
}

fn copy_payload(from: &Path, to: &Path) -> Result<()> {
    let temp = to.with_file_name(format!(
        ".{}.{}.copy",
        to.file_name().unwrap().to_string_lossy(),
        std::process::id()
    ));
    #[cfg(target_os = "macos")]
    let cloned = {
        use std::{ffi::CString, os::unix::ffi::OsStrExt};
        unsafe extern "C" {
            fn clonefile(
                from: *const std::ffi::c_char,
                to: *const std::ffi::c_char,
                flags: u32,
            ) -> i32;
        }
        let from = CString::new(from.as_os_str().as_bytes())?;
        let to = CString::new(temp.as_os_str().as_bytes())?;
        // The two owned C strings remain alive for this clonefile call.
        unsafe { clonefile(from.as_ptr(), to.as_ptr(), 0) == 0 }
    };
    #[cfg(not(target_os = "macos"))]
    let cloned = false;
    if !cloned {
        std::fs::copy(from, &temp)?;
    }
    std::fs::rename(temp, to)?;
    Ok(())
}

pub fn physical(spec: &Value, output: &Path) -> Result<Value> {
    let name = spec["name"].as_str().unwrap_or("enclosure-assembly");
    let model = output.join(format!("{name}.step.npz"));
    let step = output.join(format!("{name}.step"));
    let mesh = output.join(format!("{name}.step.mesh"));
    let presentation = spec["physical_presentation"]
        .as_str()
        .map(|file| output.join(file))
        .unwrap_or_else(|| mesh.clone());
    let instances = spec.get("instances").context("physical instances")?;
    let mut sources = Models::new();
    let rows = references(instances, &mut sources)?;
    // The physical model's document is attached after its presentation is complete.
    // Reuse each immutable input archive across reference, copy and presentation phases.
    write_refs_using(&rows, None, &model, &mut sources)?;
    drop(rows);
    let mut fine = Model::for_visiting(&model)?;
    let src = write_step_stream(&mut fine, &step, name)?;
    let mut shown = super::payload::placed_surfaces(instances, &mut fine, &mut sources)?;
    drop(sources);
    let names: Vec<_> = fine.names.iter().map(|name| json!({"name":name})).collect();
    drop(fine);
    shown.header["src"] = json!(src);
    if let Some(skins) = spec.get("presentation") {
        shown.graft(skins)?;
    }
    shown.write(&presentation)?;
    drop(shown);
    if presentation != mesh {
        copy_payload(&presentation, &mesh)?;
    }
    bind_fresh(&model, &presentation, spec.get("document"))?;
    let mut files = vec![
        super::output_name(&step, output),
        super::output_name(&model, output),
        super::output_name(&mesh, output),
    ];
    if presentation != mesh {
        files.push(super::output_name(&presentation, output));
    }
    Ok(
        json!({"files":files,"bodies":names,"model":model,"payload":mesh,"physical_step_sha256":src}),
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
/// Finalize a newly written physical archive without copying its numeric members again.
pub(super) fn bind_fresh(path: &Path, payload: &Path, document: Option<&Value>) -> Result<()> {
    let mut document = document.cloned().unwrap_or_else(|| json!({}));
    document["presentation"] = json!({"path":relative(payload,path.parent().unwrap()),"sha256":stream_digest(payload, false)?});
    let file = std::fs::OpenOptions::new().read(true).write(true).open(path)?;
    let start = ZipArchive::new(file.try_clone()?)?.central_directory_start();
    let mut position = file.try_clone()?;
    let mut target = ZipWriter::new_append(file)?;
    // Cloned File handles share their cursor. Replace the old directory rather than
    // leaving it between the numeric members and the final document.
    position.seek(SeekFrom::Start(start))?;
    let options = SimpleFileOptions::default().compression_method(zip::CompressionMethod::Stored);
    target.start_file("document.npy", options)?;
    target.write_all(&npy_text(&serde_json::to_vec(&document)?))?;
    target.finish()?;
    Ok(())
}
pub fn bind(path: &Path, payload: &Path) -> Result<()> {
    bind_document(path, payload, true)
}
fn bind_document(path: &Path, payload: &Path, input: bool) -> Result<()> {
    let mut source = ZipArchive::new(File::open(path)?)?;
    let mut document = if source
        .file_names()
        .any(|n| n.is_ok_and(|n| n == "document.npy"))
    {
        serde_json::from_slice(npy_data(&member(&mut source, "document.npy")?)?)?
    } else {
        json!({})
    };
    document["presentation"] = json!({"path":relative(payload,path.parent().unwrap()),"sha256":stream_digest(payload, input)?});
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
