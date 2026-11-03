//! Install an already-generated wiring assembly without touching physical records.
use super::payload::Payload;
use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};
use std::{
    collections::BTreeMap,
    path::{Path, PathBuf},
};
const BEGIN: &str = "/* HSM_INSTALLED_WIRING_BEGIN */\n";
const END: &str = "/* HSM_INSTALLED_WIRING_END */\n";
fn base(text: &str) -> Result<String> {
    if let Some(start) = text.find(BEGIN) {
        let end = text[start..].find(END).context("unfinished wiring block")? + start + END.len();
        Ok(format!("{}{}", &text[..start], &text[end..]))
    } else {
        Ok(text.into())
    }
}
fn records(text: &str) -> Result<Vec<(u64, String)>> {
    let mut out = Vec::new();
    let mut at = 0;
    let bytes = text.as_bytes();
    while at < bytes.len() {
        let Some(rel) = text[at..].find('#') else {
            break;
        };
        at += rel;
        if at > 0 && bytes[at - 1] != b'\n' {
            at += 1;
            continue;
        }
        let start = at + 1;
        let mut end = start;
        while end < bytes.len() && bytes[end].is_ascii_digit() {
            end += 1
        }
        if end == start {
            at += 1;
            continue;
        }
        let id = text[start..end].parse()?;
        while end < bytes.len() && bytes[end].is_ascii_whitespace() {
            end += 1
        }
        if bytes.get(end) != Some(&b'=') {
            at = end;
            continue;
        }
        let first = end + 1;
        let last = text[first..]
            .find(";\n")
            .map(|v| first + v)
            .context("STEP record ending")?;
        out.push((id, text[first..last].into()));
        at = last + 2;
    }
    Ok(out)
}
fn refs(text: &str) -> Vec<u64> {
    let mut out = Vec::new();
    let b = text.as_bytes();
    let mut at = 0;
    while at < b.len() {
        if b[at] != b'#' {
            at += 1;
            continue;
        }
        at += 1;
        let start = at;
        while at < b.len() && b[at].is_ascii_digit() {
            at += 1
        }
        if start < at {
            out.push(text[start..at].parse().unwrap());
        }
    }
    out
}
fn remap(text: &str, offset: u64) -> String {
    let mut out = String::with_capacity(text.len());
    let bytes = text.as_bytes();
    let mut at = 0;
    let mut last = 0;
    while at < bytes.len() {
        if bytes[at] != b'#' {
            at += 1;
            continue;
        }
        let first = at;
        at += 1;
        let start = at;
        while at < bytes.len() && bytes[at].is_ascii_digit() {
            at += 1
        }
        if at > start {
            out.push_str(&text[last..first]);
            out.push('#');
            out.push_str(&(text[start..at].parse::<u64>().unwrap() + offset).to_string());
            last = at;
        }
    }
    out.push_str(&text[last..]);
    out
}
fn root(rows: &[(u64, String)], name: &str) -> Result<(u64, u64, u64)> {
    let dict: BTreeMap<_, _> = rows.iter().map(|(id, b)| (*id, b.as_str())).collect();
    let product = rows
        .iter()
        .find(|(_, b)| b.trim_start().starts_with(&format!("PRODUCT('{name}',")))
        .map(|r| r.0)
        .context("STEP assembly product")?;
    let parent = |id: u64, kind: &str| -> Result<u64> {
        let found: Vec<_> = rows
            .iter()
            .filter(|(_, b)| {
                b.trim_start().starts_with(&format!("{kind}(")) && refs(b).contains(&id)
            })
            .map(|r| r.0)
            .collect();
        ensure!(found.len() == 1, "STEP {kind} parent count {}", found.len());
        Ok(found[0])
    };
    let formation = parent(product, "PRODUCT_DEFINITION_FORMATION")?;
    let pd = parent(formation, "PRODUCT_DEFINITION")?;
    let pds = parent(pd, "PRODUCT_DEFINITION_SHAPE")?;
    let sdr = parent(pds, "SHAPE_DEFINITION_REPRESENTATION")?;
    let representation = *refs(dict[&sdr]).get(1).context("STEP representation")?;
    let axis = refs(dict[&representation])
        .into_iter()
        .find(|n| dict[n].trim_start().starts_with("AXIS2_PLACEMENT_3D("))
        .context("STEP datum")?;
    Ok((pd, representation, axis))
}
fn wiring(name: &str) -> bool {
    ["wire-", "wiring-", "terminal-"]
        .iter()
        .any(|p| name.starts_with(p))
}
pub fn append(spec: &Value, output: &Path) -> Result<Value> {
    let host = PathBuf::from(super::text(spec, "host_step")?);
    let wire = PathBuf::from(super::text(spec, "wire_step")?);
    let host_bytes = super::read(&host)?;
    let base = base(std::str::from_utf8(&host_bytes)?)?;
    let original = records(&base)?;
    let wire_bytes = super::read(&wire)?;
    let incoming = records(std::str::from_utf8(&wire_bytes)?)?;
    let (hp, hr, ha) = root(
        &original,
        spec["host_name"].as_str().unwrap_or("enclosure-assembly"),
    )?;
    let (wp, wr, wa) = root(
        &incoming,
        spec["wire_name"].as_str().unwrap_or("installed-wiring"),
    )?;
    let offset = original.iter().map(|v| v.0).max().context("empty STEP")?;
    let mut added = String::new();
    for (id, body) in &incoming {
        added.push_str(&format!("#{} ={};\n", id + offset, remap(body, offset)));
    }
    let n = incoming
        .iter()
        .map(|v| v.0 + offset)
        .max()
        .context("empty wiring STEP")?
        + 1;
    added.push_str(&format!("#{n} = CONTEXT_DEPENDENT_SHAPE_REPRESENTATION(#{},#{});\n#{} = ( REPRESENTATION_RELATIONSHIP('','',#{},#{hr}) REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION(#{}) SHAPE_REPRESENTATION_RELATIONSHIP() );\n#{} = ITEM_DEFINED_TRANSFORMATION('','',#{},#{ha});\n#{} = PRODUCT_DEFINITION_SHAPE('Placement','Installed wiring',#{});\n#{} = NEXT_ASSEMBLY_USAGE_OCCURRENCE('installed-wiring','installed-wiring','',#{hp},#{},$);\n",n+1,n+3,n+1,wr+offset,n+2,n+2,wa+offset,n+3,n+4,n+4,wp+offset));
    let end = base.rfind("ENDSEC;").context("STEP end")?;
    let result = format!("{}{BEGIN}{added}{END}{}", &base[..end], &base[end..]);
    let physical_sha = super::digest(base.as_bytes());
    let installed_sha = super::digest(result.as_bytes());
    super::put(&host, result.as_bytes())?;
    let host_mesh = PathBuf::from(format!("{}.mesh", host.display()));
    let wire_mesh = PathBuf::from(format!("{}.mesh", wire.display()));
    let mut physical = Payload::read(&host_mesh)?;
    physical.meshes.retain(|m| !wiring(m.name()));
    let retained = physical.meshes.len();
    let incoming_payload = Payload::read(&wire_mesh)?;
    let wire_count = incoming_payload.meshes.len();
    physical.meshes.extend(incoming_payload.meshes);
    physical.header["src"] = json!(installed_sha);
    physical.write(&host_mesh)?;
    let mut receipt = json!({"schema":1,"scope":"Wiring-only integration; existing physical parts retained","physical_step_sha256":physical_sha,"installed_step_sha256":installed_sha,"physical_records_retained":original.len(),"physical_meshes_retained":retained,"wiring_meshes":wire_count,"all_retained_viewer_arrays_identical":Value::Null,"wiring_step_sha256":super::digest(&wire_bytes),"files":[super::output_name(&host,output),super::output_name(&host_mesh,output)],"bodies":[]});
    if let Some(model) = spec["wire_model"].as_str() {
        receipt["wiring_fine_model"] =
            json!({"path":model,"sha256":super::digest(&super::read(Path::new(model))?)});
    }
    Ok(receipt)
}
