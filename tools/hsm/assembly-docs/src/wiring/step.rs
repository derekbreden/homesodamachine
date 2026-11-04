use super::*;
use std::io::{Read, Seek, SeekFrom};
const BEGIN: &str = "/* HSM_INSTALLED_WIRING_BEGIN */\n";
const END: &str = "/* HSM_INSTALLED_WIRING_END */\n";
pub fn base_document(text: &str) -> Result<String> {
    if let Some(start) = text.find(BEGIN) {
        let end = text[start..]
            .find(END)
            .context("unfinished installed wiring block")?
            + start
            + END.len();
        Ok(text[..start].to_owned() + &text[end..])
    } else {
        Ok(text.into())
    }
}
fn records(text: &str) -> Result<Vec<(u64, String)>> {
    let pattern = regex::Regex::new(r"(?ms)^#(\d+)\s*=(.*?);[ \t]*\n")?;
    pattern
        .captures_iter(text)
        .map(|c| Ok((c[1].parse()?, c[2].to_owned())))
        .collect()
}
fn refs(text: &str) -> Result<Vec<u64>> {
    regex::Regex::new(r"#(\d+)")?
        .captures_iter(text)
        .map(|c| Ok(c[1].parse()?))
        .collect()
}
fn root(records: &[(u64, String)], name: Option<&str>) -> Result<[u64; 3]> {
    let product = records
        .iter()
        .find(|(_, body)| {
            if let Some(name) = name {
                body.trim().starts_with(&format!("PRODUCT('{name}',"))
            } else {
                body.trim().starts_with("PRODUCT(")
            }
        })
        .context("STEP root product")?
        .0;
    let parent = |n: u64, kind: &str| -> Result<u64> {
        let parents = records
            .iter()
            .filter(|(_, body)| {
                body.trim().starts_with(&format!("{kind}("))
                    && refs(body).is_ok_and(|rows| rows.contains(&n))
            })
            .map(|r| r.0)
            .collect::<Vec<_>>();
        ensure!(parents.len() == 1, "({n}, {kind:?}, {parents:?})");
        Ok(parents[0])
    };
    let formation = parent(product, "PRODUCT_DEFINITION_FORMATION")?;
    let pd = parent(formation, "PRODUCT_DEFINITION")?;
    let pds = parent(pd, "PRODUCT_DEFINITION_SHAPE")?;
    let sdr = parent(pds, "SHAPE_DEFINITION_REPRESENTATION")?;
    let dictionary = records
        .iter()
        .map(|(n, b)| (*n, b))
        .collect::<BTreeMap<_, _>>();
    let representation = *refs(dictionary[&sdr])?
        .get(1)
        .context("STEP representation reference")?;
    let axis = refs(dictionary[&representation])?
        .into_iter()
        .find(|n| {
            dictionary
                .get(n)
                .is_some_and(|b| b.trim().starts_with("AXIS2_PLACEMENT_3D("))
        })
        .context("STEP identity placement")?;
    Ok([pd, representation, axis])
}
fn wiring(name: &str) -> bool {
    ["wire-", "wiring-", "terminal-"]
        .iter()
        .any(|p| name.starts_with(p))
}
fn header(file: &mut std::fs::File) -> Result<(Value, u64)> {
    let mut size = [0u8; 4];
    file.read_exact(&mut size)?;
    let size = u32::from_le_bytes(size) as usize;
    let mut bytes = vec![0u8; size];
    file.read_exact(&mut bytes)?;
    Ok((serde_json::from_slice(&bytes)?, size as u64 + 4))
}
fn payload_merge(host: &Path, wire: &Path, src: &str) -> Result<[usize; 2]> {
    let mut a = std::fs::File::open(host)?;
    let mut b = std::fs::File::open(wire)?;
    let (before, ab) = header(&mut a)?;
    let (incoming, bb) = header(&mut b)?;
    let mut meshes = Vec::new();
    let mut copies = Vec::new();
    let mut offset = 0u64;
    let retained = rows(&before["meshes"])?
        .iter()
        .filter(|m| !wiring(m["name"].as_str().unwrap_or("")))
        .cloned()
        .collect::<Vec<_>>();
    for (which, start, source) in [(0, ab, &retained), (1, bb, rows(&incoming["meshes"])?)] {
        for original in source {
            let mut row = original.clone();
            for key in ["pos", "nrm", "idx", "fac", "col", "uv"] {
                if let Some(range) = row.get(key) {
                    let at = range[0].as_u64().context("payload span offset")?;
                    let count = range[1].as_u64().context("payload span count")?;
                    row[key] = json!([offset, count]);
                    offset += count * 4;
                    copies.push((which, start + at, count * 4));
                }
            }
            meshes.push(row);
        }
    }
    let mut result = before;
    result["meshes"] = json!(meshes);
    result["src"] = json!(src);
    let mut bytes = serde_json::to_vec(&result)?;
    while bytes.len() % 4 != 0 {
        bytes.push(b' ');
    }
    let temporary = host.with_file_name(format!(
        ".{}.{}.tmp",
        host.file_name().unwrap().to_string_lossy(),
        std::process::id()
    ));
    {
        let mut output = std::fs::File::create(&temporary)?;
        output.write_all(&(bytes.len() as u32).to_le_bytes())?;
        output.write_all(&bytes)?;
        let mut buffer = [0u8; 1 << 16];
        for (which, start, mut size) in copies {
            let input = if which == 0 { &mut a } else { &mut b };
            input.seek(SeekFrom::Start(start))?;
            while size > 0 {
                let count = buffer.len().min(size as usize);
                let read = input.read(&mut buffer[..count])?;
                ensure!(read > 0, "Truncated mesh payload array");
                output.write_all(&buffer[..read])?;
                size -= read as u64;
            }
        }
    }
    std::fs::rename(temporary, host)?;
    Ok([retained.len(), rows(&incoming["meshes"])?.len()])
}
fn fingerprints(path: &Path) -> Result<Value> {
    use sha2::{Digest, Sha256};
    let mut stream = std::fs::File::open(path)?;
    let (data, blob) = header(&mut stream)?;
    let mut out = json!({});
    let mut buffer = [0u8; 1 << 16];
    for row in rows(&data["meshes"])? {
        let name = string(&row["name"])?;
        if wiring(name) {
            continue;
        }
        let mut hash = Sha256::new();
        for key in ["pos", "nrm", "idx", "fac"] {
            let mut size = row[key][1].as_u64().context("payload count")? * 4;
            stream.seek(SeekFrom::Start(
                blob + row[key][0].as_u64().context("payload offset")?,
            ))?;
            while size > 0 {
                let count = buffer.len().min(size as usize);
                let read = stream.read(&mut buffer[..count])?;
                ensure!(read > 0, "truncated retained array");
                hash.update(&buffer[..read]);
                size -= read as u64;
            }
        }
        out[name] = json!(format!("{:x}", hash.finalize()));
    }
    Ok(out)
}
pub fn install(data: &Value) -> Result<Value> {
    let host = string(&data["host"])?;
    let verify = boolean(data, "verify_retained", false);
    let path = PathBuf::from(format!("{host}.mesh"));
    let before = if verify {
        Some(fingerprints(&path)?)
    } else {
        None
    };
    let mut receipt = provider(
        json!({"kind":"append_wiring","host":host,"wire_step":data["wire_step"],"wire_model":data.get("wire_model")}),
    )?;
    receipt
        .as_object_mut()
        .context("wiring integration receipt")?
        .remove("files");
    receipt.as_object_mut().unwrap().remove("bodies");
    if let Some(before) = before {
        let after = fingerprints(&path)?;
        let retained = before
            .as_object()
            .unwrap()
            .keys()
            .map(|k| (k.clone(), after.get(k).cloned().unwrap_or(Value::Null)))
            .collect::<serde_json::Map<_, _>>();
        receipt["all_retained_viewer_arrays_identical"] = json!(before == Value::Object(retained));
    }
    Ok(receipt)
}
pub fn request(request: &Request) -> Result<Value> {
    let d = &request.data;
    match request.op.as_str() {
        "step_base" => Ok(json!(base_document(string(&d["text"])?)?)),
        "step_records" => Ok(json!(records(string(&d["text"])?)?)),
        "step_refs" => Ok(json!(refs(string(&d["text"])?)?)),
        "step_root" => {
            let records = rows(&d["records"])?
                .iter()
                .map(|r| {
                    Ok((
                        r[0].as_u64().context("STEP record number")?,
                        string(&r[1])?.to_owned(),
                    ))
                })
                .collect::<Result<Vec<_>>>()?;
            Ok(json!(root(
                &records,
                d.get("name").and_then(Value::as_str)
            )?))
        }
        "step_payload_merge" => Ok(json!(payload_merge(
            Path::new(string(&d["host"])?),
            Path::new(string(&d["wire"])?),
            string(&d["src"])?
        )?)),
        "step_install" => install(d),
        "step_wiring" => Ok(json!(wiring(string(&d["name"])?))),
        _ => bail!("STEP operation {}", request.op),
    }
}
