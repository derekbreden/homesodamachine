//! Shared mesh objects let assemblies retain geometry while their references and placements change.
use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{collections::BTreeMap, fs, path::{Path, PathBuf}, sync::atomic::{AtomicU64, Ordering}};

const ARRAYS: [&str; 6] = ["pos", "nrm", "idx", "fac", "col", "uv"];
static NEXT: AtomicU64 = AtomicU64::new(0);

pub fn digest(bytes: &[u8]) -> String { format!("{:x}", Sha256::digest(bytes)) }

pub fn cache_dir() -> PathBuf {
    std::env::var_os("HSM_WORKSPACE").map(PathBuf::from).unwrap_or_else(||
        Path::new(env!("CARGO_MANIFEST_DIR")).ancestors().nth(3).unwrap().to_path_buf())
        .join(".cache/meshes/scene-assets")
}

pub fn asset_path(hash: &str) -> Result<PathBuf> {
    ensure!(hash.len() == 64 && hash.bytes().all(|c| c.is_ascii_hexdigit()), "invalid mesh object digest");
    Ok(cache_dir().join(format!("{hash}.mesh")))
}

pub fn keep(path: &Path, bytes: &[u8]) -> Result<()> {
    if fs::read(path).is_ok_and(|old| old == bytes) { return Ok(()); }
    fs::create_dir_all(path.parent().context("mesh parent")?)?;
    let temp = path.with_extension(format!("{}-{}.tmp", std::process::id(), NEXT.fetch_add(1, Ordering::Relaxed)));
    fs::write(&temp, bytes)?;
    fs::rename(temp, path)?;
    Ok(())
}

pub fn store(bytes: &[u8]) -> Result<String> {
    let hash = digest(bytes);
    let path = asset_path(&hash)?;
    keep(&path, bytes)?;
    Ok(hash)
}

pub fn header(bytes: &[u8]) -> Result<(Value, usize)> {
    ensure!(bytes.len() >= 4, "truncated surface header");
    let end = 4usize.checked_add(u32::from_le_bytes(bytes[..4].try_into()?) as usize).context("surface header overflow")?;
    ensure!(end % 4 == 0, "unaligned surface header");
    Ok((serde_json::from_slice(bytes.get(4..end).context("truncated surface header")?)?, end))
}

pub fn encode(head: &Value, blob: &[u8]) -> Result<Vec<u8>> {
    let mut head = serde_json::to_vec(head)?;
    while head.len() % 4 != 0 { head.push(b' '); }
    let mut out = Vec::with_capacity(4 + head.len() + blob.len());
    out.extend_from_slice(&(head.len() as u32).to_le_bytes()); out.extend(head); out.extend(blob);
    Ok(out)
}

pub fn is_scene(bytes: &[u8]) -> bool { header(bytes).is_ok_and(|(h,_)| h["v"] == 4) }

pub fn body(name: &str) -> &str {
    name.rsplit_once('/').filter(|(_,n)| !n.is_empty() && n.bytes().all(|c|c.is_ascii_digit()))
        .map(|(b,_)|b).unwrap_or(name)
}

fn span<'a>(blob: &'a [u8], row: &Value, key: &str) -> Result<&'a [u8]> {
    let at = row[key][0].as_u64().context("surface offset")? as usize;
    let len = row[key][1].as_u64().context("surface count")? as usize;
    let end = len.checked_mul(4).and_then(|n|at.checked_add(n)).context("surface span overflow")?;
    ensure!(at % 4 == 0, "unaligned surface span");
    blob.get(at..end).context("truncated surface span")
}

/// Split a packed surface into immutable body objects without changing any drawing array.
pub fn pack(bytes: &[u8]) -> Result<Value> {
    let (mut head, start) = header(bytes)?;
    if head["v"] == 4 { return Ok(head); }
    ensure!(matches!(head["v"].as_u64(), Some(2 | 3)), "unsupported surface version");
    let rows = head["meshes"].as_array().context("surface meshes")?;
    let mut groups: Vec<(String,Vec<&Value>)> = Vec::new();
    for row in rows {
        let name = row["name"].as_str().context("surface name")?;
        let name = body(name);
        let i = groups.iter().position(|(n,_)|n == name).unwrap_or_else(|| {groups.push((name.into(),Vec::new()));groups.len()-1});
        groups[i].1.push(row);
    }
    let mut instances = Vec::new();
    for (name, rows) in groups {
        if let Some(origin)=rows[0].get("_scene").filter(|v|v["asset"].is_string()) {
            if rows.iter().all(|row|row["_scene"]["asset"]==origin["asset"] && row["_scene"]["transform"]==origin["transform"])
                && origin["entries"].as_array().is_some_and(|entries|entries.len()==rows.len()) {
                let mut node=origin.clone();node["name"]=json!(name);
                node["entries"]=json!(rows.iter().map(|row|json!({"name":row["name"],"color":row["color"]})).collect::<Vec<_>>());
                instances.push(node);continue;
            }
        }
        let mut data = Vec::new(); let mut geometry = Vec::new(); let mut entries = Vec::new();
        for (index,row) in rows.iter().enumerate() {
            let mut item = (*row).clone();
            entries.push(json!({"name":row["name"],"color":row["color"]}));
            item["name"] = json!(index.to_string()); item["color"] = Value::Null;
            item.as_object_mut().unwrap().remove("_scene");
            for key in ARRAYS { if row.get(key).is_some() {
                let array = span(&bytes[start..], row, key)?;
                item[key] = json!([data.len(),array.len()/4]); data.extend_from_slice(array);
            }}
            geometry.push(item);
        }
        let object = encode(&json!({"v":3,"meshes":geometry}), &data)?;
        let asset = store(&object)?;
        instances.push(json!({"name":name,"asset":asset,"bytes":object.len(),"entries":entries}));
    }
    head["v"] = json!(4); head["meshes"] = json!(instances);
    Ok(head)
}

pub fn assets(head: &Value) -> Vec<String> {
    let mut hashes = head["meshes"].as_array().into_iter().flatten()
        .filter_map(|r|r["asset"].as_str().map(str::to_owned)).collect::<Vec<_>>();
    hashes.sort(); hashes.dedup(); hashes
}

fn carry(bytes: &mut [u8], key: &str, frame: &Value) -> Result<()> {
    let m = frame.as_array().context("placement rows")?;
    ensure!(m.len() >= 3 && m[..3].iter().all(|r|r.as_array().is_some_and(|r|r.len()==4)), "placement shape");
    let mut a=[[0.;3];3];
    for r in 0..3 {for c in 0..3 {a[r][c]=m[r][c].as_f64().context("placement number")?;}}
    let det=a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]);
    ensure!(det.abs()>1e-15,"singular placement");
    let co=[
        [a[1][1]*a[2][2]-a[1][2]*a[2][1],a[1][2]*a[2][0]-a[1][0]*a[2][2],a[1][0]*a[2][1]-a[1][1]*a[2][0]],
        [a[0][2]*a[2][1]-a[0][1]*a[2][2],a[0][0]*a[2][2]-a[0][2]*a[2][0],a[0][1]*a[2][0]-a[0][0]*a[2][1]],
        [a[0][1]*a[1][2]-a[0][2]*a[1][1],a[0][2]*a[1][0]-a[0][0]*a[1][2],a[0][0]*a[1][1]-a[0][1]*a[1][0]]];
    if key=="idx" {
        if det<0. {for tri in bytes.chunks_exact_mut(12) {for c in 0..4 {tri.swap(4+c,8+c);}}}
        return Ok(());
    }
    for xyz in bytes.chunks_exact_mut(12) {
        let p: [f64;3] = std::array::from_fn(|i|f32::from_le_bytes(xyz[i*4..i*4+4].try_into().unwrap()) as f64);
        let mut values=[0.;3];
        for r in 0..3 {
            let mut n = if key == "pos" {m[r][3].as_f64().context("placement number")?} else {0.};
            for c in 0..3 { n += if key=="pos" {a[r][c]*p[c]} else {co[r][c]*p[c]/det}; }
            values[r]=n;
        }
        let norm=if key=="nrm" {values.iter().map(|v|v*v).sum::<f64>().sqrt().max(f64::MIN_POSITIVE)} else {1.};
        for r in 0..3 {xyz[r*4..r*4+4].copy_from_slice(&((values[r]/norm) as f32).to_le_bytes());}
    }
    Ok(())
}

/// Resolve the shared representation for native readers that consume contiguous arrays.
pub fn flatten_with(bytes: &[u8], mut load: impl FnMut(&str)->Result<Vec<u8>>) -> Result<Vec<u8>> {
    let (mut head,_) = header(bytes)?;
    if head["v"] != 4 { return Ok(bytes.to_vec()); }
    let mut output = Vec::new(); let mut rows = Vec::new();
    let mut held: BTreeMap<String,Vec<u8>> = BTreeMap::new();
    for node in head["meshes"].as_array().context("scene instances")? {
        let hash = node["asset"].as_str().context("mesh object")?;
        if !held.contains_key(hash) { let data=load(hash)?;ensure!(digest(&data)==hash,"mesh object digest mismatch");held.insert(hash.into(),data); }
        let data = &held[hash]; let (object,start) = header(data)?;
        let object_rows=object["meshes"].as_array().context("object meshes")?;
        for (index,original) in object_rows.iter().enumerate() {
            let mut row = original.clone();
            let instance=&node["entries"][index];
            row["name"] = instance["name"].clone();
            row["color"] = if instance["color"].as_array().is_some_and(|c|c.len()>3) {json!(&instance["color"].as_array().unwrap()[..3])} else {instance["color"].clone()};
            row["_scene"] = node.clone();
            for key in ARRAYS { if original.get(key).is_some() {
                let mut array=span(&data[start..],original,key)?.to_vec();
                if matches!(key,"pos"|"nrm"|"idx") && !node["transform"].is_null() {carry(&mut array,key,&node["transform"])?;}
                row[key]=json!([output.len(),array.len()/4]);output.extend(array);
            }}
            rows.push(row);
        }
    }
    head["v"]=json!(3);head["meshes"]=json!(rows);
    encode(&head,&output)
}

pub fn flatten(bytes: &[u8]) -> Result<Vec<u8>> {
    flatten_with(bytes, load_asset)
}

/// Missing shared objects are restored by content address without starting a CAD build.
pub fn load_asset(hash: &str) -> Result<Vec<u8>> {
    let path=asset_path(hash)?;
    if let Ok(bytes)=fs::read(&path) {return Ok(bytes);}
    use std::process::{Command,Stdio};
    fs::create_dir_all(cache_dir())?;
    let mut fetch=Command::new("curl").args(["-fsSL","--connect-timeout","10","--max-time","90",&format!("https://homesodamachine.com/objects/s-{hash}.gz")])
        .stdout(Stdio::piped()).stderr(Stdio::piped()).spawn()?;
    let decoded=Command::new("gzip").arg("-dc").stdin(fetch.stdout.take().context("mesh download pipe")?).output()?;
    let fetched=fetch.wait_with_output()?;
    ensure!(fetched.status.success() && decoded.status.success(),"mesh object {hash} is unavailable");
    ensure!(digest(&decoded.stdout)==hash,"mesh object digest mismatch");
    keep(&path,&decoded.stdout)?;Ok(decoded.stdout)
}

pub fn read(path: &Path) -> Result<Vec<u8>> { flatten(&fs::read(path)?) }

pub fn write(path: &Path, bytes: &[u8]) -> Result<()> { keep(path, &encode(&pack(bytes)?, &[])?) }

pub fn persist(path: &Path, head: &Value) -> Result<()> {
    keep(path,&encode(head,&[])?)?;
    if (head["step_export"]==false && path.to_string_lossy().ends_with(".step.mesh")) || path.to_string_lossy().ends_with(".glb.mesh") {
        let old=PathBuf::from(path.to_string_lossy().trim_end_matches(".mesh"));
        if old.is_file() {fs::remove_file(old)?;}
    }
    Ok(())
}

/// Each completed part replaces its own references while other instances keep their last surfaces.
pub fn replace(head: &mut Value, source: &str, bytes: &[u8]) -> Result<usize> {
    let sha=digest(bytes);
    if head["sources"][source] == sha {return Ok(0);}
    let part=pack(bytes)?;let parts=part["meshes"].as_array().context("part meshes")?;
    let mut changed=0;
    for host in head["meshes"].as_array_mut().context("scene meshes")? {
        let normalize=|s:&str|s.replace('_',"-");
        let name=normalize(host["name"].as_str().context("instance name")?);
        let found=parts.iter().find(|p| {
            let own=normalize(p["name"].as_str().unwrap_or(""));
            if let Some(bound)=host["source"].as_str() {bound==source && (name==own || name.ends_with(&format!("/{own}")) || parts.len()==1)}
            else {name==own || name.ends_with(&format!("/{own}"))}
        });
        if let Some(part)=found {
            let stem=host["name"].as_str().unwrap().to_owned();
            host["asset"]=part["asset"].clone();host["bytes"]=part["bytes"].clone();
            let mut entries=part["entries"].as_array().context("part entries")?.clone();
            let count=entries.len();
            for (i,entry) in entries.iter_mut().enumerate() {
                entry["name"]=json!(if count==1 {stem.clone()} else {format!("{stem}/{i}")});
                if !host["color_override"].is_null() {entry["color"]=host["color_override"].clone();}
            }
                host["entries"]=json!(entries);host["source"]=json!(source);host["source_sha256"]=json!(sha);changed+=1;
        }
    }
    if changed>0 {
        if !head["sources"].is_object(){head["sources"]=json!({});}
        head["sources"][source]=json!(sha);
        head["src"]=json!(digest(&serde_json::to_vec(&head["meshes"])?));
        head["source_kind"]=json!("scene");
    }
    Ok(changed)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn triangle(names:&[&str], shift:f32)->Vec<u8> {
        let mut blob=Vec::new();let mut rows=Vec::new();
        for name in names {
            let mut row=json!({"name":name,"color":[0.2,0.3,0.4],"face_sources":[[{"op":"test","src":"source.rs"}]]});
            for (key,values) in [("pos",vec![shift,0.,0.,shift+1.,0.,0.,shift,1.,0.]),("nrm",vec![0.,0.,1.,0.,0.,1.,0.,0.,1.])] {
                row[key]=json!([blob.len(),values.len()]);for v in values {blob.extend_from_slice(&v.to_le_bytes());}
            }
            for (key,values) in [("idx",vec![0u32,1,2]),("fac",vec![0u32,0])] {
                row[key]=json!([blob.len(),values.len()]);for v in values {blob.extend_from_slice(&v.to_le_bytes());}
            }
            rows.push(row);
        }
        encode(&json!({"v":3,"meshes":rows,"src":"native-model"}),&blob).unwrap()
    }
    #[test]
    fn shared_instances_preserve_arrays_and_part_replacement_keeps_other_parts()->Result<()> {
        let raw=triangle(&["left","right"],0.);let mut scene=pack(&raw)?;
        assert_eq!(assets(&scene).len(),1);
        let expanded=flatten(&encode(&scene,&[])?)?;
        let (old,start)=header(&raw)?;let (new,end)=header(&expanded)?;
        assert_eq!(&raw[start..],&expanded[end..]);
        for (a,b) in old["meshes"].as_array().unwrap().iter().zip(new["meshes"].as_array().unwrap()) {
            for key in ["name","color","face_sources"] {assert_eq!(a[key],b[key]);}
        }
        let unchanged=scene["meshes"][1].clone();
        assert_eq!(replace(&mut scene,"part.mesh",&triangle(&["left"],2.))?,1);
        assert_eq!(scene["meshes"][1],unchanged);
        assert_eq!(replace(&mut scene,"part.mesh",&triangle(&["left"],2.))?,0);
        let broken=flatten_with(&encode(&scene,&[])?,|_|Ok(vec![0]));assert!(broken.is_err());
        Ok(())
    }
    #[test]
    fn placements_reuse_mesh_objects_and_reflections_preserve_winding()->Result<()> {
        let mut scene=pack(&triangle(&["part"],0.))?;let asset=scene["meshes"][0]["asset"].clone();
        scene["meshes"][0]["transform"]=json!([[-1.,0.,0.,5.],[0.,1.,0.,3.],[0.,0.,1.,2.]]);
        let flat=flatten(&encode(&scene,&[])?)?;let (head,start)=header(&flat)?;
        let row=&head["meshes"][0];let pos=span(&flat[start..],row,"pos")?;
        assert_eq!(f32::from_le_bytes(pos[..4].try_into()?),5.);
        let idx=span(&flat[start..],row,"idx")?;
        assert_eq!(u32::from_le_bytes(idx[4..8].try_into()?),2);
        assert_eq!(scene["meshes"][0]["asset"],asset);
        assert_eq!(pack(&flat)?["meshes"][0]["asset"],asset);
        Ok(())
    }
}
