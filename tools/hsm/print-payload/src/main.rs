//! A print's viewer payload at the viewer's existing surface policy, and the graft plans that carry
//! one print's surfaces into another payload.
//!
//!     print-payload <numbers.json> <out directory>
use hsm_print_payload as presentation;
use anyhow::{ensure,Context,Result};
use hsm_geometry::parry::{math::Point,query::PointQuery};
use hsm_geometry::payload;
use hsm_kernel::{v3,V3};
use presentation::Random;
use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{collections::{BTreeSet,HashMap},fs::File,io::Read,path::Path};

fn digest(path:&Path)->Result<String> {
    let mut file=File::open(path)?;let mut hash=Sha256::new();let mut block=[0_u8;65536];
    loop {let n=file.read(&mut block)?;if n==0 {break;}hash.update(&block[..n]);}
    let sha=format!("{:x}",hash.finalize());hsm_kernel::reads::digest(path,&sha);Ok(sha)
}
fn lineage(path:&Path,count:usize,exact:bool)->Option<presentation::Lineage> {
    if path.file_name()?.to_str()?!="enclosure-front-top.stl"||!exact{return None;}
    let sidecar=path.with_file_name(format!("{}.sources.json",path.file_name()?.to_str()?));
    let bytes=std::fs::read(&sidecar).ok()?;hsm_kernel::reads::read(&sidecar,&bytes);
    let d:Value=serde_json::from_slice(&bytes).ok()?;
    if d["v"]!=1||d["sha256"].as_str()!=Some(&digest(path).ok()?){return None;}
    let records=d["records"].as_array()?.iter().map(|g|g.as_array().cloned()).collect::<Option<Vec<_>>>()?;
    let triangles=d["triangles"].as_array()?.iter().map(|i|i.as_u64().map(|i|i as usize)).collect::<Option<Vec<_>>>()?;
    presentation::lineage(&records,&triangles,count,exact)
}
fn identity(path:&Path)->Result<(Value,Value)> {
    let mut archive=zip::ZipArchive::new(File::open(path)?)?;
    let mut read=|name:&str|->Result<Value>{let data=npyz::NpyFile::new(archive.by_name(&format!("{name}.npy"))?)?;
        Ok(serde_json::from_slice(&data.into_vec::<u8>()?)?)};
    let names=read("names")?;let colors=read("colors")?;
    ensure!(names.as_array().is_some_and(|a|a.len()==1)&&colors.as_array().is_some_and(|a|a.len()==1),"one identity per printed piece");
    Ok((names[0].clone(),colors[0].clone()))
}
fn run(n:&Value,out:&Path)->Result<Value> {
    let stl_path=Path::new(n["stl"].as_str().context("print STL")?);
    let bytes=std::fs::read(stl_path)?;hsm_kernel::reads::read(stl_path,&bytes);
    let(mesh,exact)=presentation::weld(&bytes)?;drop(bytes);
    ensure!(!mesh.faces.is_empty(),"printed mesh has triangles");
    let original_sources=lineage(stl_path,mesh.faces.len(),exact);
    let(name,color)=if let Some(row)=n["identity"].as_array(){
        ensure!(row.len()==2 && row[0].is_string(),"explicit print name and colour");
        (row[0].clone(),row[1].clone())
    }else{identity(Path::new(n["model"].as_str().context("fine model")?))?};
    let filename=format!("{}.mesh",n["step_name"].as_str().context("STEP filename")?);
    let output=out.join(&filename);std::fs::create_dir_all(out)?;
    let source=n["source"].as_str().or_else(||n["model"].as_str()).context("print source binding")?;
    let sha=digest(Path::new(source))?;
    let cut=presentation::cut(&mesh,original_sources,presentation::Request{
        name,color,src:&sha,
        crease_deg:n["crease_deg"].as_f64().context("crease angle")?,
        deflection_ratio:n["deflection_ratio"].as_f64().context("deflection ratio")?,
        preserve:n["preserve_print_triangles"].as_bool().unwrap_or(false),
        unknown:stl_path.file_name().and_then(|s|s.to_str())==Some("enclosure-front-top.stl"),
        check:n["check_print"].as_bool().unwrap_or(false),
    }).with_context(||stl_path.display().to_string())?;
    std::fs::write(&output,&cut.payload)?;
    Ok(json!({"files":[filename],"bodies":[],"printed_triangles":cut.printed_triangles,"drawing_triangles":cut.drawing_triangles,"bound":cut.bound,"deviation":cut.deviation,"reduction":cut.reduction,"probe_vertices":cut.probe_vertices,"watertight":cut.watertight,"non_manifold_edges":cut.non_manifold_edges}))
}

fn choice(n:usize,size:usize)->Vec<usize>{
    let size=n.min(size);if size==n{return(0..n).collect();}
    let mut rng=Random::new();let mut selected=BTreeSet::new();
    if n>10000&&size>n/50{let mut ids=(0..n).collect::<Vec<_>>();
        for i in ((n-size).max(1)..n).rev(){let j=rng.bounded(i);ids.swap(i,j);}selected.extend(ids[n-size..].iter().copied());
    }else{for j in n-size..n{let k=rng.bounded(j);if !selected.insert(k){selected.insert(j);}}}
    selected.into_iter().collect()
}
fn mesh_bounds(mesh:&payload::Mesh)->(V3,V3){
    let b=mesh.shape.local_aabb();(v3(b.mins.x,b.mins.y,b.mins.z),v3(b.maxs.x,b.maxs.y,b.maxs.z))
}
fn rotations()->Vec<[[f64;3];3]>{
    let mut out=Vec::new();
    for p in [[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]]{
        let inversions=(0..3).flat_map(|i|(i+1..3).map(move|j|(i,j))).filter(|&(i,j)|p[i]>p[j]).count();
        for a in [1.,-1.]{for b in [1.,-1.]{for c in [1.,-1.]{
            if a*b*c*(if inversions%2==0{1.}else{-1.})<0.{continue;}
            let mut r=[[0.;3];3];for(i,s)in[a,b,c].into_iter().enumerate(){r[i][p[i]]=s;}out.push(r);
        }}}
    }out
}
fn turn(p:V3,r:&[[f64;3];3])->V3{let a=p.to_array();V3::from(std::array::from_fn(|i|r[i][0]*a[0]+r[i][1]*a[1]+r[i][2]*a[2]))}
fn placement(body:&payload::Mesh,skin:&payload::Mesh)->Option<[[f64;4];3]>{
    let(a0,a1)=mesh_bounds(body);let points=skin.shape.vertices();let probes=choice(points.len(),1500);let mut best=None;
    for r in rotations(){
        let mut lo=v3(f64::INFINITY,f64::INFINITY,f64::INFINITY);let mut hi=-lo;
        for p in points{let p=turn(v3(p.x,p.y,p.z),&r);lo=lo.min(p);hi=hi.max(p);}
        let t=((a0+a1)-(lo+hi))/2.;if (lo+t-a0).to_array().map(f64::abs).into_iter().fold(0_f64,f64::max)>0.5{continue;}
        let mut gaps=probes.iter().map(|&i|{let p=points[i];let p=turn(v3(p.x,p.y,p.z),&r)+t;
            let point=Point::new(p.x,p.y,p.z);let q=body.shape.project_local_point(&point,false).point;(point-q).norm()}).collect::<Vec<_>>();
        if gaps.is_empty(){continue;}gaps.sort_by(f64::total_cmp);
        let index=0.99*(gaps.len()-1)as f64;let i=index.floor()as usize;let j=index.ceil()as usize;
        let dev=gaps[i]+(gaps[j]-gaps[i])*(index-i as f64);
        if best.as_ref().is_none_or(|(old,_)|dev<*old){let t=t.to_array();let frame=std::array::from_fn(|k|[r[k][0],r[k][1],r[k][2],t[k]]);best=Some((dev,frame));}
    }
    best.and_then(|(dev,frame)|(dev<=2.).then_some(frame))
}
fn loaded(path:&str)->Result<payload::Payload>{let bytes=std::fs::read(path)?;hsm_kernel::reads::read(Path::new(path),&bytes);payload::decode(&bytes)}
fn graft_plan(n:&Value)->Result<Value>{
    let host=loaded(n["target_payload"].as_str().context("graft target payload")?)?;
    let rows=n["candidates"].as_array().context("graft candidates")?;let mut sources=HashMap::new();let mut skins=Vec::new();let mut moved=Vec::new();
    for candidate in rows{
        let path=candidate["payload"].as_str().context("candidate payload")?;
        if !sources.contains_key(path){sources.insert(path.to_owned(),loaded(path)?);}
        let source=&sources[path];let index=candidate["index"].as_u64().context("source entry index")? as usize;
        let surface=source.meshes.get(index).context("candidate source mesh")?;
        let name=candidate["target"].as_str().context("candidate host name")?;
        let body=host.meshes.iter().find(|mesh|mesh.name==name).context("named graft host mesh")?;
        let(a0,a1)=mesh_bounds(body);let(b0,b1)=mesh_bounds(surface);
        let drift=(a0-b0).to_array().into_iter().chain((a1-b1).to_array()).map(f64::abs).fold(0_f64,f64::max);
        let frame=if drift<=0.5{Some([[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.]])}else{placement(body,surface)};
        if let Some(frame)=frame{
            let mut row=json!({"payload":path,"indices":[index],"targets":[name],"transform":frame});
            if let Some(sha)=&source.source{row["source_sha256"]=json!(sha);}skins.push(row);
        }else{moved.push(json!({"name":name,"drift_mm":drift}));}
    }
    Ok(json!({"files":[],"bodies":[],"skins":skins,"moved":moved}))
}
fn main()->Result<()> {
    let args=std::env::args().collect::<Vec<_>>();ensure!(args.len()==3,"usage: print-payload <numbers.json> <out directory>");
    let bytes=std::fs::read(&args[1])?;hsm_kernel::reads::read(Path::new(&args[1]),&bytes);
    let numbers:Value=serde_json::from_slice(&bytes)?;
    let result=if numbers["op"]=="graft_plan"{graft_plan(&numbers)?}else{run(&numbers,Path::new(&args[2]))?};
    println!("{}",serde_json::to_string(&result)?);Ok(())
}
