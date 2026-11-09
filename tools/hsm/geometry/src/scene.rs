//! Shared mesh objects let assemblies retain geometry while their references and placements change.
use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{collections::BTreeMap, fs, path::{Path, PathBuf}, sync::atomic::{AtomicU64, Ordering}};

const ARRAYS: [&str; 6] = ["pos", "nrm", "idx", "fac", "col", "uv"];
static NEXT: AtomicU64 = AtomicU64::new(0);
mod imports {
    //! Source inventories reconcile added and removed bodies without rebuilding unrelated geometry.
    use super::{body, digest, header, load_asset, pack};
    use anyhow::{Context, Result, ensure};
    use serde_json::{Value, json};

    type Frame = [[f64; 4]; 3];
    const ID: Frame = [[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.]];

    fn frame(value: &Value) -> Result<Frame> {
        if value.is_null() { return Ok(ID); }
        let mut out = ID;
        for r in 0..3 { for c in 0..4 {
            out[r][c] = value[r][c].as_f64().context("source placement number")?;
        }}
        Ok(out)
    }

    fn multiply(a: Frame, b: Frame) -> Frame {
        std::array::from_fn(|r| std::array::from_fn(|c|
            (0..3).map(|k| a[r][k]*b[k][c]).sum::<f64>() + if c == 3 {a[r][3]} else {0.}))
    }

    fn inverse(a: Frame) -> Result<Frame> {
        let det = a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
            -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
            +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]);
        ensure!(det.abs()>1e-15, "singular source placement");
        let mut out = ID;
        for r in 0..3 { for c in 0..3 {
            let (r1,r2,c1,c2)=((c+1)%3,(c+2)%3,(r+1)%3,(r+2)%3);
            out[r][c]=(a[r1][c1]*a[r2][c2]-a[r1][c2]*a[r2][c1])/det;
        }}
        for r in 0..3 {out[r][3]=-(0..3).map(|c|out[r][c]*a[c][3]).sum::<f64>();}
        Ok(out)
    }

    fn normalized(name: &str) -> String {name.replace('_', "-")}

    fn prefix<'a>(host: &'a str, own: &str) -> Option<&'a str> {
        let (host_key,own_key)=(normalized(host),normalized(own));
        if host_key == own_key {Some("")}
        else if host_key.ends_with(&format!("/{own_key}")) {Some(&host[..host.len()-own.len()])}
        else {None}
    }

    fn inventory(head: &Value) -> Result<Vec<Value>> {
        let mut rows = Vec::new();
        for node in head["meshes"].as_array().context("source meshes")? {
            let name=body(node["name"].as_str().context("source body name")?);
            if !rows.iter().any(|row: &Value| row["name"] == name) {
                rows.push(json!({"name":name,"transform":if head["v"] == 4 {node["transform"].clone()} else {Value::Null}}));
            }
        }
        Ok(rows)
    }

    fn own<'a>(host: &Value, rows: &'a [Value]) -> Option<&'a Value> {
        if let Some(name)=host["source_name"].as_str() {
            return rows.iter().find(|row| row["name"].as_str().is_some_and(|n| normalized(n)==normalized(name)));
        }
        rows.iter().find(|row| prefix(host["name"].as_str().unwrap_or(""),row["name"].as_str().unwrap_or("")).is_some())
    }

    fn placed(part: &Value, previous: Option<&Value>, name: &str, source: &str, sha: &str, outer: Option<Frame>) -> Result<Value> {
        let mut node=previous.cloned().unwrap_or_else(||part.clone());
        node["name"]=json!(name);
        node["asset"]=part["asset"].clone();node["bytes"]=part["bytes"].clone();
        if let Some(outer)=outer {node["transform"]=json!(multiply(outer,frame(&part["transform"])?));}
        let mut entries=part["entries"].as_array().context("source entries")?.clone();
        let count=entries.len();
        for (i,entry) in entries.iter_mut().enumerate() {
            entry["name"]=json!(if count==1 {name.to_owned()} else {format!("{name}/{i}")});
            if !node["color_override"].is_null() {entry["color"]=node["color_override"].clone();}
        }
        node["entries"]=json!(entries);node["source"]=json!(source);
        if let Some(count) = part.get("feature_count") { node["feature_count"] = count.clone(); }
        else { node.as_object_mut().unwrap().remove("feature_count"); }
        node["source_name"]=part["name"].clone();node["source_sha256"]=json!(sha);
        Ok(node)
    }

    #[derive(Clone)]
    struct Group {prefix: String, transform: Frame, members: Vec<usize>}

    fn member(host: &Value, old: &[Value]) -> Result<Option<(String,Frame)>> {
        let Some(part)=own(host,old) else {return Ok(None)};
        let Some(prefix)=prefix(host["name"].as_str().context("instance name")?,part["name"].as_str().unwrap()) else {return Ok(None)};
        Ok(Some((prefix.into(),multiply(frame(&host["transform"])?,inverse(frame(&part["transform"])?)?))))
    }

    fn same(a: Frame, b: Frame) -> bool {
        a.iter().flatten().zip(b.iter().flatten()).all(|(a,b)|(a-b).abs()<1e-9)
    }

    /// Whole imports adopt source membership; named selections keep their authored scope.
    pub(super) fn replace(head: &mut Value, source: &str, bytes: &[u8], complete: bool) -> Result<usize> {
        let sha=digest(bytes);
        if head["sources"][source]==sha && head["source_inventory"][source].is_array() {return Ok(0);}
        let part=pack(bytes)?;
        let parts=part["meshes"].as_array().context("part meshes")?;
        let hosts=head["meshes"].as_array().context("scene meshes")?.clone();
        let bound=hosts.iter().any(|node|node["source"]==source);
        let saved=head["source_groups"][source].as_array().cloned().unwrap_or_default();
        if !bound && saved.is_empty() && !hosts.iter().any(|node|node["source"].is_null() && own(node,parts).is_some()) {return Ok(0);}
        let current=inventory(&part)?;
        let previous=hosts.iter().filter(|node|node["source"]==source)
            .filter_map(|node|node["source_sha256"].as_str()).find(|hash|*hash!=sha)
            .or_else(||head["sources"][source].as_str().filter(|hash|*hash!=sha));
        let old=if let Some(rows)=head["source_inventory"][source].as_array() {rows.clone()}
            else if let Some(previous)=previous.filter(|_|bound) {
                inventory(&header(&load_asset(previous).with_context(||format!("previous source inventory for {source}"))?)?.0)?
            } else {current.clone()};
        let mut groups=Vec::<Group>::new();
        if complete {
            for group in saved {
                groups.push(Group {prefix:group["prefix"].as_str().context("source prefix")?.into(),transform:frame(&group["transform"])?,members:Vec::new()});
            }
            let mut candidates=Vec::<Group>::new();
            for (index,node) in hosts.iter().enumerate().filter(|(_,node)|node["source"]==source) {
                let Some((prefix,transform))=member(node,&old)? else {continue};
                let i=candidates.iter().position(|group|group.prefix==prefix && same(group.transform,transform)).unwrap_or_else(||{
                    candidates.push(Group {prefix,transform,members:Vec::new()});candidates.len()-1
                });
                candidates[i].members.push(index);
            }
            for group in candidates {
                let full=!old.is_empty() && old.iter().all(|part|group.members.iter().any(|&i|own(&hosts[i],std::slice::from_ref(part)).is_some()));
                if full && !groups.iter().any(|g|g.prefix==group.prefix && same(g.transform,group.transform)) {groups.push(group);}
            }
            for group in &mut groups {
                group.members=(0..hosts.len()).filter(|&i|hosts[i]["source"]==source && member(&hosts[i],&old).ok().flatten().is_some_and(|(prefix,transform)|prefix==group.prefix && same(transform,group.transform))).collect();
            }
        }
        let mut output=Vec::new();let mut emitted=vec![false;groups.len()];
        let emit=|group: &Group, output: &mut Vec<Value>| -> Result<()> {
            let uniform=group.members.first().map(|&i|hosts[i]["color_override"].clone()).filter(|color|!color.is_null() && group.members.iter().all(|&i|hosts[i]["color_override"]==*color));
            for part in parts {
                let previous=group.members.iter().map(|&i|&hosts[i]).find(|node|own(node,std::slice::from_ref(part)).is_some());
                let name=previous.and_then(|node|node["name"].as_str()).map(str::to_owned).unwrap_or_else(||format!("{}{}",group.prefix,part["name"].as_str().unwrap()));
                let mut node=placed(part,previous,&name,source,&sha,Some(group.transform))?;
                if previous.is_none() {if let Some(color)=&uniform {node["color_override"]=color.clone();for entry in node["entries"].as_array_mut().unwrap(){entry["color"]=color.clone();}}}
                output.push(node);
            }
            Ok(())
        };
        for (index,host) in hosts.iter().enumerate() {
            if let Some(i)=groups.iter().position(|group|group.members.contains(&index)) {
                if !emitted[i] {emit(&groups[i],&mut output)?;emitted[i]=true;}
                continue;
            }
            if host["source"]==source {
                if let Some(old_part)=own(host,&old) {
                    if let Some(part)=parts.iter().find(|part|normalized(part["name"].as_str().unwrap())==normalized(old_part["name"].as_str().unwrap())) {
                        let outer=multiply(frame(&host["transform"])?,inverse(frame(&old_part["transform"])?)?);
                        output.push(placed(part,Some(host),host["name"].as_str().unwrap(),source,&sha,Some(outer))?);
                    }
                    continue;
                }
            }
            let found=if host["source"].is_null() || host["source"]==source {own(host,parts).or_else(||(host["source"]==source && parts.len()==1).then(||&parts[0]))} else {None};
            output.push(if let Some(part)=found {placed(part,Some(host),host["name"].as_str().context("instance name")?,source,&sha,None)?} else {host.clone()});
        }
        for (i,group) in groups.iter().enumerate() {if !emitted[i] {emit(group,&mut output)?;}}
        let changed=hosts.iter().zip(&output).filter(|(a,b)|a!=b).count()+hosts.len().abs_diff(output.len());
        if !bound && changed==0 && groups.is_empty() {return Ok(0);}
        head["meshes"]=json!(output);
        if !head["sources"].is_object(){head["sources"]=json!({});}
        if !head["source_inventory"].is_object(){head["source_inventory"]=json!({});}
        head["sources"][source]=json!(sha);head["source_inventory"][source]=json!(current);
        if complete && !groups.is_empty() {
            if !head["source_groups"].is_object(){head["source_groups"]=json!({});}
            head["source_groups"][source]=json!(groups.iter().map(|group|json!({"prefix":group.prefix,"transform":group.transform})).collect::<Vec<_>>());
        }
        head["src"]=json!(digest(&serde_json::to_vec(&head["meshes"])?));head["source_kind"]=json!("scene");
        Ok(changed.max(1))
    }
}

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
        let mut node = json!({"name":name,"asset":asset,"bytes":object.len(),"entries":entries});
        let features = rows.iter().map(|r| r["features"].as_array().map_or(0, Vec::len)).sum::<usize>();
        if features > 0 { node["feature_count"] = json!(features); }
        instances.push(node);
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
    flatten_selection_with(bytes, None, &mut load)
}

/// Selected viewer entries retain their source arrays, placements and original scene order.
pub fn flatten_selected_with(bytes: &[u8], selected: &[usize], mut load: impl FnMut(&str)->Result<Vec<u8>>) -> Result<Vec<u8>> {
    flatten_selection_with(bytes, Some(selected), &mut load)
}

fn flatten_selection_with(bytes: &[u8], selected: Option<&[usize]>, load: &mut impl FnMut(&str)->Result<Vec<u8>>) -> Result<Vec<u8>> {
    let (mut head,_) = header(bytes)?;
    if head["v"] != 4 {
        if let Some(selected) = selected {
            let (_,start) = header(bytes)?;
            head["meshes"] = json!(head["meshes"].as_array().context("surface meshes")?.iter().enumerate()
                .filter(|(i,_)|selected.contains(i)).map(|(_,row)|row.clone()).collect::<Vec<_>>());
            return encode(&head, &bytes[start..]);
        }
        return Ok(bytes.to_vec());
    }
    let mut output = Vec::new(); let mut rows = Vec::new();
    let mut held: BTreeMap<String,Vec<u8>> = BTreeMap::new();
    let mut first = 0;
    for node in head["meshes"].as_array().context("scene instances")? {
        let count = node["entries"].as_array().context("instance entries")?.len();
        let base = first; first += count;
        if selected.is_some_and(|selected|!(base..first).any(|i|selected.contains(&i))) {continue;}
        let hash = node["asset"].as_str().context("mesh object")?;
        if !held.contains_key(hash) { let data=load(hash)?;ensure!(digest(&data)==hash,"mesh object digest mismatch");held.insert(hash.into(),data); }
        let data = &held[hash]; let (object,start) = header(data)?;
        let object_rows=object["meshes"].as_array().context("object meshes")?;
        ensure!(object_rows.len()==count,"instance entry count differs from mesh object");
        for (index,original) in object_rows.iter().enumerate() {
            if selected.is_some_and(|selected|!selected.contains(&(base+index))) {continue;}
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

/// Bounds scan the displayed positions without building a triangle acceleration structure.
pub fn entry_bounds(bytes: &[u8], row: &Value, transform: &Value) -> Result<[[f64; 3]; 2]> {
    ensure!(bytes.len()>=4,"truncated surface header");
    let start=4usize.checked_add(u32::from_le_bytes(bytes[..4].try_into()?) as usize).context("surface header overflow")?;
    ensure!(start%4==0,"unaligned surface header");
    let positions = span(bytes.get(start..).context("truncated surface header")?, row, "pos")?;
    ensure!(!positions.is_empty() && positions.len()%12==0,"invalid position count");
    let mut frame = [[0.;4];3];
    if !transform.is_null() {
        for r in 0..3 {for c in 0..4 {frame[r][c]=transform[r][c].as_f64().context("placement number")?;}}
    }
    let mut bounds = [[f64::INFINITY;3],[f64::NEG_INFINITY;3]];
    for xyz in positions.chunks_exact(12) {
        let p: [f64;3] = std::array::from_fn(|i|f32::from_le_bytes(xyz[i*4..i*4+4].try_into().unwrap()) as f64);
        ensure!(p.iter().all(|n|n.is_finite()),"non-finite position");
        for r in 0..3 {
            let n = if transform.is_null() {p[r]} else {
                let mut n = frame[r][3];
                for c in 0..3 {n += frame[r][c]*p[c];}
                (n as f32) as f64
            };
            ensure!(n.is_finite(),"non-finite placed position");
            bounds[0][r]=bounds[0][r].min(n);bounds[1][r]=bounds[1][r].max(n);
        }
    }
    Ok(bounds)
}

/// Bounds of authored surface ranges read existing indices without allocating query geometry.
pub fn feature_bounds(bytes: &[u8], row: &Value, feature: &Value, transform: &Value) -> Result<[[f64; 3]; 2]> {
    let (_, start) = header(bytes)?;
    let blob = &bytes[start..];
    let positions = span(blob, row, "pos")?;
    let indices = span(blob, row, "idx")?;
    let mut bounds = [[f64::INFINITY; 3], [f64::NEG_INFINITY; 3]];
    for range in feature["triangles"].as_array().context("feature triangle ranges")? {
        let a = range[0].as_u64().context("feature range start")? as usize;
        let b = range[1].as_u64().context("feature range end")? as usize;
        ensure!(a <= b && (b + 1) * 12 <= indices.len(), "feature range outside mesh");
        for index in indices[a * 12..(b + 1) * 12].chunks_exact(4) {
            let i = u32::from_le_bytes(index.try_into()?) as usize * 12;
            let xyz = positions.get(i..i + 12).context("feature vertex outside mesh")?;
            let p: [f64; 3] = std::array::from_fn(|k| f32::from_le_bytes(xyz[k*4..k*4+4].try_into().unwrap()) as f64);
            for r in 0..3 {
                let q = if transform.is_null() { p[r] } else {
                    let mut q = transform[r][3].as_f64().context("placement translation")?;
                    for c in 0..3 { q += transform[r][c].as_f64().context("placement rotation")? * p[c]; }
                    q as f32 as f64
                };
                bounds[0][r] = bounds[0][r].min(q); bounds[1][r] = bounds[1][r].max(q);
            }
        }
    }
    ensure!(bounds.iter().flatten().all(|n| n.is_finite()), "feature has no finite surface");
    Ok(bounds)
}

/// Selected exported triangles retain their original viewer identifiers.
pub struct FeatureSurface {
    pub vertices: Vec<[f64;3]>,
    pub triangles: Vec<[u32;3]>,
    pub triangle_ids: Vec<u32>,
    pub faces: Vec<[u32;2]>,
    pub face_sources: Option<Vec<Vec<Value>>>,
}

/// Query-time feature geometry references the selected exported triangles and compacts their vertices.
pub fn feature_surface(bytes: &[u8], row: &Value, feature: &Value, transform: &Value) -> Result<FeatureSurface> {
    let (_, start) = header(bytes)?;
    let blob = &bytes[start..];
    let positions = span(blob, row, "pos")?;
    let indices = span(blob, row, "idx")?;
    let mut vertices = Vec::new();
    let mut triangles = Vec::new();
    let mut original = Vec::new();
    let mut vertex_ids = BTreeMap::new();
    for range in feature["triangles"].as_array().context("feature triangle ranges")? {
        let a = range[0].as_u64().context("feature range start")? as usize;
        let b = range[1].as_u64().context("feature range end")? as usize;
        ensure!(a <= b && (b + 1) * 12 <= indices.len(), "feature range outside mesh");
        for (offset, triangle) in indices[a*12..(b+1)*12].chunks_exact(12).enumerate() {
            let mut selected = [0;3];
            for k in 0..3 {
                let i = u32::from_le_bytes(triangle[k*4..k*4+4].try_into()?);
                selected[k] = if let Some(&id) = vertex_ids.get(&i) { id } else {
                    let offset = i as usize * 12;
                    let xyz = positions.get(offset..offset+12).context("feature vertex outside mesh")?;
                    let p: [f64;3] = std::array::from_fn(|j| f32::from_le_bytes(xyz[j*4..j*4+4].try_into().unwrap()) as f64);
                    let mut q = p;
                    if !transform.is_null() {
                        for r in 0..3 {
                            q[r] = transform[r][3].as_f64().context("placement translation")?;
                            for c in 0..3 { q[r] += transform[r][c].as_f64().context("placement rotation")? * p[c]; }
                            q[r] = q[r] as f32 as f64;
                        }
                    }
                    let id = vertices.len() as u32; vertices.push(q); vertex_ids.insert(i,id); id
                };
            }
            triangles.push(selected); original.push((a+offset) as u32);
        }
    }
    let ranges = span(blob, row, "fac")?;
    let faces = ranges.chunks_exact(8).map(|r| [u32::from_le_bytes(r[..4].try_into().unwrap()),u32::from_le_bytes(r[4..].try_into().unwrap())]).collect();
    let face_sources = row["face_sources"].as_array().and_then(|a| a.iter().map(|r| r.as_array().cloned()).collect());
    Ok(FeatureSurface { vertices, triangles, triangle_ids: original, faces, face_sources })
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

/// Completed sources reconcile their imported bodies while unrelated instances retain their surfaces.
pub fn replace(head: &mut Value, source: &str, bytes: &[u8]) -> Result<usize> {
    imports::replace(head,source,bytes,true)
}

/// A named view updates only its selected bodies when their source membership changes.
pub fn replace_selected(head: &mut Value, source: &str, bytes: &[u8]) -> Result<usize> {
    imports::replace(head,source,bytes,false)
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

    #[test]
    fn selected_entries_skip_unrelated_assets_and_bounds_match_displayed_rounding()->Result<()> {
        let mut scene=pack(&triangle(&["first","second"],0.1234567))?;
        scene["meshes"][0]["transform"]=json!([[-0.6,-0.8,0.,5.123456789],[0.8,-0.6,0.,3.987654321],[0.,0.,1.,2.]]);
        let all=encode(&scene,&[])?;
        let full=crate::payload::decode(&flatten(&all)?)?;
        let data=load_asset(scene["meshes"][0]["asset"].as_str().unwrap())?;
        let (object,_)=header(&data)?;
        let bounds=entry_bounds(&data,&object["meshes"][0],&scene["meshes"][0]["transform"])?;
        assert_eq!(bounds,[full.meshes[0].bounds([0.;3]).0,full.meshes[0].bounds([0.;3]).1]);
        let expected=scene["meshes"][0]["asset"].as_str().unwrap().to_owned();
        scene["meshes"][1]["asset"]=json!("unavailable");
        let selected=flatten_selected_with(&encode(&scene,&[])?,&[0],|hash| {
            assert_eq!(hash,expected);Ok(data.clone())
        })?;
        let payload=crate::payload::decode(&selected)?;
        assert_eq!(payload.meshes.len(),1);
        assert_eq!(payload.meshes[0].name,"first");
        assert_eq!(payload.meshes[0].bounds([0.;3]),full.meshes[0].bounds([0.;3]));
        Ok(())
    }

    fn imported(names: &[&str]) -> Result<Value> {
        let bytes=triangle(names,0.);let sha=store(&bytes)?;
        let mut scene=pack(&bytes)?;
        for node in scene["meshes"].as_array_mut().unwrap() {
            node["source"]=json!("part.mesh");node["source_sha256"]=json!(sha);
        }
        scene["sources"]=json!({"part.mesh":sha});
        Ok(scene)
    }

    #[test]
    fn legacy_imports_adopt_new_retainer_bodies_and_keep_unrelated_assets()->Result<()> {
        let mut scene=imported(&["retainer"])?;
        let unrelated=pack(&triangle(&["wall"],0.))?["meshes"][0].clone();
        scene["meshes"].as_array_mut().unwrap().push(unrelated.clone());
        let source=triangle(&["retainer-a","retainer-b","screw"],2.);
        assert!(replace(&mut scene,"part.mesh",&source)?>0);
        let rows=scene["meshes"].as_array().unwrap();
        assert_eq!(rows.iter().map(|row|row["name"].as_str().unwrap()).collect::<Vec<_>>(),["retainer-a","retainer-b","screw","wall"]);
        assert_eq!(rows.last(),Some(&unrelated));
        assert_eq!(replace(&mut scene,"part.mesh",&source)?,0);
        let flat=flatten(&encode(&scene,&[])?)?;
        assert_eq!(header(&flat)?.0["meshes"].as_array().unwrap().len(),4);
        Ok(())
    }

    #[test]
    fn imported_membership_survives_removals_empty_sources_and_reintroduction()->Result<()> {
        let mut scene=imported(&["left","right"])?;
        replace(&mut scene,"part.mesh",&triangle(&["left","right"],0.))?;
        replace(&mut scene,"part.mesh",&triangle(&["left","cap"],1.))?;
        assert_eq!(scene["meshes"][1]["name"],"cap");
        let empty=triangle(&[],0.);
        replace(&mut scene,"part.mesh",&empty)?;
        assert!(scene["meshes"].as_array().unwrap().is_empty());
        assert_eq!(replace(&mut scene,"part.mesh",&empty)?,0);
        replace(&mut scene,"part.mesh",&triangle(&["replacement"],3.))?;
        assert_eq!(scene["meshes"].as_array().unwrap().len(),1);
        assert_eq!(scene["meshes"][0]["name"],"replacement");
        Ok(())
    }

    #[test]
    fn legacy_partial_refresh_recovers_membership_from_the_retained_body_revision()->Result<()> {
        let mut scene=imported(&["retainer","screw"])?;
        let next=triangle(&["retainer-a","retainer-b","screw"],2.);
        let sha=digest(&next);
        scene["sources"]["part.mesh"]=json!(sha);
        scene["meshes"][1]["source_sha256"]=json!(sha);
        replace(&mut scene,"part.mesh",&next)?;
        let names:Vec<_>=scene["meshes"].as_array().unwrap().iter().map(|node|node["name"].as_str().unwrap()).collect();
        assert_eq!(names,["retainer-a","retainer-b","screw"]);
        Ok(())
    }

    #[test]
    fn repeated_imports_place_new_bodies_in_each_assembly_frame()->Result<()> {
        let old=pack(&triangle(&["cap"],0.))?;
        let mut source=old.clone();source["meshes"][0]["transform"]=json!([[1.,0.,0.,2.],[0.,1.,0.,0.],[0.,0.,1.,0.]]);
        let bytes=encode(&source,&[])?;let sha=store(&bytes)?;
        let mut a=source["meshes"][0].clone();a["name"]=json!("left/cap");a["entries"][0]["name"]=json!("left/cap");
        a["source"]=json!("part.mesh");a["source_sha256"]=json!(sha);
        a["transform"]=json!([[-1.,0.,0.,8.],[0.,1.,0.,20.],[0.,0.,1.,30.]]);
        a["color_override"]=json!([1.,0.,0.]);
        let mut b=a.clone();b["name"]=json!("right/cap");b["entries"][0]["name"]=json!("right/cap");
        b["transform"]=json!([[1.,0.,0.,102.],[0.,1.,0.,0.],[0.,0.,1.,0.]]);
        let mut scene=json!({"v":4,"meshes":[a,b],"sources":{"part.mesh":sha}});
        let mut next=pack(&triangle(&["cap","nut"],5.))?;
        for node in next["meshes"].as_array_mut().unwrap(){node["transform"]=source["meshes"][0]["transform"].clone();}
        replace(&mut scene,"part.mesh",&encode(&next,&[])?)?;
        let flat=flatten(&encode(&scene,&[])?)?;let (head,start)=header(&flat)?;
        let node=head["meshes"].as_array().unwrap().iter().find(|row|row["name"]=="left/nut").unwrap();
        let pos=span(&flat[start..],node,"pos")?;
        let first:Vec<_>=pos[..12].chunks_exact(4).map(|v|f32::from_le_bytes(v.try_into().unwrap())).collect();
        assert_eq!(first,[3.,20.,30.]);assert_eq!(node["color"],json!([1.,0.,0.]));
        let node=head["meshes"].as_array().unwrap().iter().find(|row|row["name"]=="right/nut").unwrap();
        assert_eq!(f32::from_le_bytes(span(&flat[start..],node,"pos")?[..4].try_into()?),107.);
        Ok(())
    }

    #[test]
    fn named_views_and_partial_imports_keep_their_selection()->Result<()> {
        let mut selected=imported(&["cap"])?;
        replace_selected(&mut selected,"part.mesh",&triangle(&["cap","screw"],1.))?;
        assert_eq!(selected["meshes"].as_array().unwrap().len(),1);
        replace_selected(&mut selected,"part.mesh",&triangle(&["screw"],2.))?;
        assert!(selected["meshes"].as_array().unwrap().is_empty());
        let mut partial=imported(&["cap","omitted"])?;
        partial["meshes"].as_array_mut().unwrap().pop();
        partial["meshes"][0]["source_name"]=json!("cap");partial["meshes"][0]["name"]=json!("chosen");
        replace(&mut partial,"part.mesh",&triangle(&["cap","omitted","screw"],2.))?;
        assert_eq!(partial["meshes"].as_array().unwrap().len(),1);
        assert_eq!(partial["meshes"][0]["name"],"chosen");
        Ok(())
    }

    #[test]
    fn unplaced_sources_do_not_invent_assembly_membership()->Result<()> {
        let mut scene=imported(&["cap"])?;let old=scene.clone();
        assert_eq!(replace(&mut scene,"unrelated.mesh",&triangle(&["cap","screw"],1.))?,0);
        assert_eq!(scene,old);
        Ok(())
    }
}
