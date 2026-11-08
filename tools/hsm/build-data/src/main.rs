use anyhow::{Context, Result, bail, ensure};
use hsm_build_data::{artifact_cache, artifacts, assets, inventory, payload, projection, publication, sources, surfaces, support};
use regex::Regex;
use serde_json::{Value, json};
use std::{collections::BTreeSet, fs, io::{self,BufRead,Write}, path::{Path,PathBuf}};

fn text<'a>(v:&'a Value,key:&str)->Result<&'a str> {v[key].as_str().with_context(||format!("{key} is text"))}
fn path(v:&Value)->Result<&Path> {Ok(Path::new(text(v,"path")?))}
fn directories(v:&Value,suffix:&str)->Result<Vec<PathBuf>> {
    let mut output=Vec::new();
    for directory in v["directories"].as_array().context("directories is an array")? {
        let directory=Path::new(directory.as_str().context("directory is text")?);
        let mut found=fs::read_dir(directory).into_iter().flatten().filter_map(Result::ok)
            .map(|e|e.path()).filter(|p|p.file_name().is_some_and(|n|n.to_string_lossy().ends_with(suffix)))
            .collect::<Vec<_>>();
        found.sort();output.extend(found);
    }
    Ok(output)
}

fn product(text:&str)->Result<Vec<String>> {
    let pattern=Regex::new(r"PRODUCT\('([^']*)'")?;
    Ok(pattern.captures_iter(text).filter_map(|m|(!m[1].starts_with("Open CASCADE")).then(||m[1].into())).collect())
}

fn identity(path:&Path)->Result<Value> {
    let text=String::from_utf8_lossy(&fs::read(path)?).into_owned();
    let names=product(&text)?;
    let colors=Regex::new(r"COLOUR_RGB\('',([\d.eE+-]+),([\d.eE+-]+),([\d.eE+-]+)\)")?
        .captures_iter(&text).map(|m|[m[1].to_string(),m[2].to_string(),m[3].to_string()]).collect::<BTreeSet<_>>();
    let name=path.file_name().unwrap_or_default().to_string_lossy();
    ensure!(names.len()==1,"{name}: {} named products, expected the piece's own",names.len());
    ensure!(colors.len()==1,"{name}: {} colours, expected the piece's own",colors.len());
    let rgb=colors.into_iter().next().unwrap().map(|c|c.parse::<f64>()).into_iter().collect::<std::result::Result<Vec<_>,_>>()?;
    ensure!(rgb.iter().all(|&c|(0. ..=1.).contains(&c)),"{name}: RGB channels outside 0 to 1");
    let linear:Vec<_>=rgb.iter().map(|&c|if c<=0.04045 {c/12.92} else {((c+0.055)/1.055).powf(2.4)})
        .map(|c|(c as f32) as f64).collect();
    Ok(json!([names[0],linear]))
}

fn fluted_key(v:&Value)->Result<Value> {
    let name=text(v,"name")?.replace('_',"-");
    let (parent,own)=name.rsplit_once('/').unwrap_or(("",&name));
    if !own.is_empty() && own.chars().all(char::is_numeric) {return Ok(Value::Null);}
    let keys: BTreeSet<&str>=v["names"].as_array().context("names is an array")?.iter().filter_map(Value::as_str).collect();
    if keys.contains(name.as_str()) {return Ok(json!(name));}
    if !parent.is_empty() && keys.contains(own) {return Ok(json!(own));}
    let owner=v["owner"].as_str().unwrap_or("").replace('_',"-");
    let scopes=parent.split('/').chain(std::iter::once(owner.as_str()));
    let mut matches=BTreeSet::new();
    for scope in scopes {
        if matches!(scope,"faucet-shell"|"faucet-assembly") {
            let alias=match own {"shell-base"=>Some("faucet-shell-base"),"shell-tip"=>Some("faucet-shell-tip"),_=>None};
            if let Some(alias)=alias.filter(|a|keys.contains(a)) {matches.insert(alias);}
        }
    }
    Ok(if matches.len()==1 {json!(matches.into_iter().next().unwrap())} else {Value::Null})
}

fn callback(query:Value)->Result<Value> {
    println!("{}",json!({"_hsm_callback":query,"_hsm_reentrant":true}));io::stdout().flush()?;
    loop {
        let mut line=String::new();io::stdin().read_line(&mut line)?;
        let result:Value=serde_json::from_str(&line)?;
        if let Some(request)=result.get("_hsm_request") {
            let nested=match dispatch(request) {Ok(value)=>value,Err(error)=>json!({"error":format!("{error:#}")})};
            println!("{}",json!({"_hsm_nested_result":nested}));io::stdout().flush()?;continue;
        }
        if let Some(error)=result.get("_hsm_callback_error") {bail!("provider: {error}");}
        return result.get("_hsm_callback_result").cloned().context("provider callback result");
    }
}

fn dispatch(v:&Value)->Result<Value> {
    if let Some(value)=inventory::dispatch(v)? {return Ok(value);}
    if let Some(value)=publication::dispatch(v)? {return Ok(value);}
    if let Some(value)=artifact_cache::dispatch(v)? {return Ok(value);}
    if let Some(value)=artifacts::dispatch(v,&mut callback)? {return Ok(value);}
    match text(v,"op")? {
        "project-graph"=>Ok(support::project_graph(&v["graph"],text(v,"generator")?)),
        "project-graph-file"=>{support::write_projection(Path::new(text(v,"source")?),Path::new(text(v,"output")?),text(v,"generator")?)?;Ok(Value::Null)},
        "blake2b16"=>Ok(json!(sources::blake2b16(&serde_json::from_value::<Vec<u8>>(v["bytes"].clone())?))),
        "code-digest"=>Ok(json!(sources::code_digest(path(v)?,&mut callback)?)),
        "digest"=>Ok(json!(sources::digest(&serde_json::from_value::<Vec<PathBuf>>(v["paths"].clone())?,&mut callback)?)),
        "source-files"=>Ok(json!(sources::source_files(Path::new(text(v,"root")?),path(v)?,&mut callback)?)),
        "compiled"=>Ok(json!(sources::compiled(path(v)?,Path::new(text(v,"workspace")?))?)),
        "manifests"=>Ok(json!(sources::manifests(&serde_json::from_value::<Vec<String>>(v["sources"].clone())?,text(v,"crate")?,Path::new(text(v,"workspace")?)))),
        "program-inputs"=>{
            let workspace=Path::new(text(v,"workspace")?);
            let sources=sources::compiled(path(v)?,workspace)?;
            let mut inputs:BTreeSet<_>=sources.iter().cloned().collect();
            inputs.extend(sources::manifests(&sources,text(v,"crate")?,workspace));
            Ok(json!(inputs))
        },
        "adopt-fine-payload"=>assets::adopt(path(v)?,Path::new(text(v,"out")?),text(v,"digest")?,
            v["linear"].as_f64().context("linear")?,v["angular"].as_f64().context("angular")?),
        "step-input"=>assets::step_input(path(v)?,Path::new(text(v,"root")?),Path::new(text(v,"workspace")?),
            v["linear"].as_f64().context("linear")?,v["angular"].as_f64().context("angular")?),
        "print-inputs"=>{
            let faucet:Vec<PathBuf>=serde_json::from_value(v["faucet_directories"].clone())?;
            let items=directories(v,".step")?.into_iter().filter(|p|p.with_extension("stl").is_file()).map(|step| {
                let preserve=v["preserve"].as_bool().unwrap_or_else(||
                    step.parent().and_then(|p|p.canonicalize().ok()).is_some_and(|p|faucet.contains(&p)));
                json!({"step":step,"stl":step.with_extension("stl"),"preserve":preserve})
            }).collect::<Vec<_>>();Ok(json!(items))
        },
        "preserve-print-triangles"=>{
            let directories:Vec<PathBuf>=serde_json::from_value(v["faucet_directories"].clone())?;
            Ok(json!(v["requested"].as_bool().unwrap_or_else(||path(v).ok().and_then(Path::parent)
                .and_then(|p|p.canonicalize().ok()).is_some_and(|parent|directories.contains(&parent)))))
        },
        "graft-inputs"=>{
            let mut skins=serde_json::Map::new();let mut own=BTreeSet::new();let mut reads=Vec::new();
            for step in directories(v,".step")?.into_iter().filter(|p|p.with_extension("stl").is_file()) {
                let payload=step.with_file_name(format!("{}.mesh",step.file_name().unwrap().to_string_lossy()));
                let payload=payload.canonicalize()?;
                let head=payload::header(&payload)?;reads.push(payload.clone());
                for (index,mesh) in head["meshes"].as_array().context("payload meshes")?.iter().enumerate() {
                    skins.insert(mesh["name"].as_str().context("mesh name")?.into(),json!({"payload":payload,"index":index}));
                }
                own.insert(payload.file_name().unwrap().to_owned());
            }
            let names=skins.keys().cloned().collect::<Vec<_>>();let mut requests=Vec::new();
            for target in directories(v,".step.mesh")? {
                if own.contains(target.file_name().unwrap()) {continue;}
                let target=target.canonicalize()?;
                let owner=dispatch(&json!({"op":"owner","path":target}))?;
                let head=payload::header(&target)?;reads.push(target.clone());
                let mut candidates=Vec::new();
                for entry in head["meshes"].as_array().context("payload meshes")? {
                    let name=fluted_key(&json!({"name":entry["name"],"names":names,"owner":owner}))?;
                    if let Some(name)=name.as_str() {
                        let mut row=skins[name].clone();row["target"]=entry["name"].clone();candidates.push(row);
                    }
                }
                if !candidates.is_empty() {requests.push(json!({"path":target,"numbers":{"op":"graft_plan","target_payload":target,"candidates":candidates}}));}
            }
            Ok(json!({"requests":requests,"reads":reads}))
        },
        "surface-catalog"=>surfaces::catalog(&directories(v,".step")?.into_iter().filter(|p|p.with_extension("stl").is_file()).collect::<Vec<_>>()),
        "axis-rotations"=>Ok(json!(surfaces::rotations())),
        "placement"=>Ok(json!(surfaces::placement(&serde_json::from_value(v["body"].clone())?,
            &serde_json::from_value(v["surface"].clone())?,v["tolerance"].as_f64().unwrap_or(0.5))?)),
        "carry"=>Ok(serde_json::to_value(surfaces::carry(&serde_json::from_value(v["surface"].clone())?,
            serde_json::from_value(v["frame"].clone())?))?),
        "drift"=>Ok(json!(surfaces::drift(&serde_json::from_value(v["body"].clone())?,&serde_json::from_value(v["surface"].clone())?))),
        "graft-surfaces"=>{
            let skins:std::collections::BTreeMap<String,payload::Mesh>=serde_json::from_str(text(v,"surfaces_json")?)?;
            let names=skins.keys().cloned().collect::<Vec<_>>();
            let owner=dispatch(&json!({"op":"owner","path":path(v)?}))?;
            surfaces::graft(path(v)?,&skins,v["same_frame"].as_bool().unwrap_or(false),|name,owner| {
                Ok(fluted_key(&json!({"name":name,"names":names,"owner":owner}))?.as_str().map(str::to_owned))
            },owner.as_str())
        },
        "header"=>payload::header(path(v)?),
        "scene-pack"=>{
            let input=path(v)?;let bytes=fs::read(input)?;
            let file=v["output"].as_str().map(Path::new).unwrap_or(input);
            hsm_geometry::scene::write(file,&bytes)?;
            Ok(hsm_geometry::scene::header(&fs::read(file)?)?.0)
        },
        "scene-flatten"=>{
            let bytes=hsm_geometry::scene::read(path(v)?)?;
            hsm_geometry::scene::keep(Path::new(text(v,"output")?),&bytes)?;
            Ok(Value::Null)
        },
        "scene-replace"=>{
            let source=Path::new(text(v,"source")?);
            let bytes=fs::read(source)?;
            let mut replies=Vec::new();
            for host in v["hosts"].as_array().context("scene hosts")? {
                let file=Path::new(host.as_str().context("host path")?);
                if !file.is_file(){continue;}
                let mut head=hsm_geometry::scene::pack(&fs::read(file)?)?;
                let count=if file.to_string_lossy().ends_with(".glb.mesh") {
                    hsm_geometry::scene::replace_selected(&mut head,text(v,"relative")?,&bytes)?
                } else {hsm_geometry::scene::replace(&mut head,text(v,"relative")?,&bytes)?};
                if count>0 {hsm_geometry::scene::keep(file,&hsm_geometry::scene::encode(&head,&[])?)?;}
                replies.push(json!({"path":file,"replaced":count}));
            }
            Ok(json!(replies))
        },
        "scene-assets"=>{
            let mut assets=std::collections::BTreeSet::new();
            for file in v["paths"].as_array().context("scene paths")? {
                let name=file.as_str().context("scene path")?;
                let Ok(mut head)=payload::header(Path::new(name)) else {continue;};
                if head["v"]==4 {
                    if let Some(expected)=v["expected"][name].as_str() {
                        if hsm_geometry::scene::digest(&fs::read(name)?)!=expected {
                            head=hsm_geometry::scene::header(&hsm_geometry::scene::load_asset(expected)?)?.0;
                        }
                    }
                }
                if head["v"] == 4 {
                    assets.extend(hsm_geometry::scene::assets(&head));
                }
            }
            let rows=assets.into_iter().map(|hash| {
                Ok(json!({"path":hsm_geometry::scene::asset_path(&hash)?,"sha256":hash}))
            }).collect::<Result<Vec<_>>>()?;
            Ok(json!(rows))
        },
        "scene-obsolete"=>{
            let root=Path::new(text(v,"root")?);let mut retired=Vec::new();
            for row in v["paths"].as_array().context("candidate exports")? {
                let relative=row.as_str().context("export path")?;
                if !relative.ends_with(".step") && !relative.ends_with(".glb"){continue;}
                let file=root.join(format!("{relative}.mesh"));
                if let Ok(head)=payload::header(&file) {
                    if head["v"]==4 && (head["step_export"]==false || relative.ends_with(".glb")) {retired.push(relative);}
                }
            }
            Ok(json!(retired))
        },
        "sha256"=>Ok(json!(payload::digest(path(v)?)?)),
        "read-payload"=>Ok(serde_json::to_value(payload::read(path(v)?)?)?),
        "payload-names"=>{
            let names=payload::header(path(v)?).ok().filter(|header|matches!(header["v"].as_u64(),Some(2|3|4)))
                .and_then(|header|header["meshes"].as_array().map(|rows|rows.iter().map(|m|m["name"].clone()).collect::<Vec<_>>()));
            Ok(json!(names.unwrap_or_default()))
        },
        "write-payload"=>{
            let payload:payload::Payload=serde_json::from_str(text(v,"payload_json")?)?;
            payload::write(path(v)?,&payload)?;Ok(Value::Null)
        },
        "aligned-sources"=>Ok(payload::aligned_sources(v.get("sources"),v["ranges"].as_u64().context("ranges is an integer")? as usize).unwrap_or(Value::Null)),
        "record-sources"=>Ok(payload::record_sources(&v["record"])),
        "pieces"=>Ok(json!(directories(v,".step")?.into_iter().filter(|p|p.with_extension("stl").is_file())
            .map(|p|[p.to_string_lossy().into_owned(),p.with_extension("stl").to_string_lossy().into_owned()]).collect::<Vec<_>>())),
        "payloads"=>Ok(json!(directories(v,".step.mesh")?)),
        "identity"=>identity(path(v)?),
        "owner"=>{
            let path=path(v)?;
            let step=if path.extension().is_some_and(|e|e=="mesh") {path.with_extension("")} else {path.with_extension("step")};
            if step.is_file() {
                let mut owner=None;
                let reader=io::BufReader::new(fs::File::open(&step)?);
                for line in reader.lines() {if let Some(name)=product(&line?)?.first() {owner=Some(name.replace('_',"-"));break;}}
                Ok(json!(owner))
            } else {Ok(json!(step.file_stem().unwrap_or_default().to_string_lossy().replace('_',"-")))}
        },
        "fluted-key"=>fluted_key(v),
        "visible-edges"=>Ok(json!(projection::visible_edges(
            &serde_json::from_value::<Vec<[f64;3]>>(v["vertices"].clone())?,
            &serde_json::from_value::<Vec<[u32;3]>>(v["triangles"].clone())?,
            serde_json::from_value(v["normal"].clone())?,serde_json::from_value(v["right"].clone())?,
            v["sharp_degrees"].as_f64().unwrap_or(30.),
            &serde_json::from_value::<Vec<([f64;3],[f64;3])>>(v["join_planes"].clone())?)?)),
        "paths"=>Ok(json!(projection::paths(&serde_json::from_value::<Vec<[[f64;2];2]>>(v["edges"].clone())?,v["simplify"].as_f64().unwrap_or(0.)))),
        "model-outlines"=>Ok(json!(projection::model_outlines(path(v)?,
            serde_json::from_value(v["normal"].clone())?,serde_json::from_value(v["right"].clone())?,
            v["simplify"].as_f64().unwrap_or(0.0025),
            &serde_json::from_value::<Vec<([f64;3],[f64;3])>>(v["join_planes"].clone())?)?)),
        op=>bail!("unknown build data operation {op}"),
    }
}

fn main()->Result<()> {
    let serve=std::env::args().any(|arg|arg=="--serve");
    loop {
        let mut line=String::new();
        if io::stdin().read_line(&mut line)?==0 {break;}
        let result=serde_json::from_str::<Value>(&line).map_err(Into::into).and_then(|v|dispatch(&v));
        let result=match result {Ok(value)=>value,Err(error)=>json!({"error":format!("{error:#}")})};
        println!("{}",serde_json::to_string(&result)?);io::stdout().flush()?;
        if !serve {break;}
    }
    Ok(())
}
