//! Printed surfaces carried into the bodies that own them.
use anyhow::{Result,ensure};
use hsm_geometry::{parry::{math::Point,query::PointQuery},payload::Mesh as QueryMesh};
use hsm_kernel::{V3,v3};
use serde_json::{Value,json};
use std::{collections::{BTreeMap,BTreeSet},fs,path::Path};
use crate::payload::{self,Mesh};

struct Random {state:u128,high:Option<u32>}
impl Random {
    fn new()->Self {Self{state:35399562948360463058890781895381311971,high:None}}
    fn next(&mut self)->u64 {
        self.state=self.state.wrapping_mul(0x2360ed051fc65da44385df649fccf645).wrapping_add(87136372517582989555478159403783844777);
        (((self.state>>64)as u64)^(self.state as u64)).rotate_right((self.state>>122)as u32)
    }
    fn next32(&mut self)->u32 {if let Some(high)=self.high.take(){high}else{let n=self.next();self.high=Some((n>>32)as u32);n as u32}}
    fn bounded(&mut self,max:usize)->usize {
        if max==0{return 0;}let range=max as u64+1;
        if max<u32::MAX as usize {let threshold=((u32::MAX as u64-max as u64)%range)as u32;
            loop {let m=self.next32()as u64*range;if m as u32>=threshold{return(m>>32)as usize;}}
        }else{let threshold=(u64::MAX-max as u64)%range;
            loop{let m=self.next()as u128*range as u128;if m as u64>=threshold{return(m>>64)as usize;}}}
    }
}
fn choice(n:usize,size:usize)->Vec<usize> {
    let size=n.min(size);if size==n{return(0..n).collect();}
    let mut rng=Random::new();let mut selected=BTreeSet::new();
    if n>10000&&size>n/50 {let mut ids=(0..n).collect::<Vec<_>>();for i in ((n-size).max(1)..n).rev(){let j=rng.bounded(i);ids.swap(i,j);}selected.extend(ids[n-size..].iter().copied());}
    else {for j in n-size..n {let k=rng.bounded(j);if !selected.insert(k){selected.insert(j);}}}
    selected.into_iter().collect()
}
pub fn rotations()->Vec<[[f64;3];3]> {
    let mut out=Vec::new();
    for p in [[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]] {
        let inversions=(0..3).flat_map(|i|(i+1..3).map(move|j|(i,j))).filter(|&(i,j)|p[i]>p[j]).count();
        for a in [1.,-1.] {for b in [1.,-1.] {for c in [1.,-1.] {
            if a*b*c*(if inversions%2==0{1.}else{-1.})<0. {continue;}
            let mut r=[[0.;3];3];for(i,s)in[a,b,c].into_iter().enumerate(){r[i][p[i]]=s;}out.push(r);
        }}}
    }out
}
fn turn(p:V3,r:&[[f64;3];3])->V3 {let a=p.to_array();V3::from(std::array::from_fn(|i|r[i][0]*a[0]+r[i][1]*a[1]+r[i][2]*a[2]))}
fn points(mesh:&Mesh)->Vec<V3>{mesh.pos.chunks_exact(3).map(|p|v3(p[0],p[1],p[2])).collect()}
fn bounds(points:&[V3])->(V3,V3) {
    let mut low=v3(f64::INFINITY,f64::INFINITY,f64::INFINITY);let mut high=-low;
    for &point in points {low=low.min(point);high=high.max(point);} (low,high)
}
pub fn drift(a:&Mesh,b:&Mesh)->f64 {
    let(a0,a1)=bounds(&points(a));let(b0,b1)=bounds(&points(b));
    (a0-b0).to_array().into_iter().chain((a1-b1).to_array()).map(f64::abs).fold(0.,f64::max)
}
pub fn placement(body:&Mesh,skin:&Mesh,tolerance:f64)->Result<Option<[[f64;4];3]>> {
    let a=points(body);let b=points(skin);let(a0,a1)=bounds(&a);
    let query=QueryMesh::from_arrays("graft body",a.iter().map(|p|p.to_array()).collect(),body.idx.chunks_exact(3).map(|t|[t[0],t[1],t[2]]).collect())?;
    let probes=choice(b.len(),1500);let mut best=None;
    for rotation in rotations() {
        let turned:Vec<_>=b.iter().map(|&p|turn(p,&rotation)).collect();let(low,high)=bounds(&turned);
        let shift=((a0+a1)-(low+high))/2.;
        if (low+shift-a0).to_array().into_iter().map(f64::abs).fold(0.,f64::max)>tolerance {continue;}
        let mut gaps=probes.iter().map(|&i|{
            let p=turn(b[i],&rotation)+shift;let p=Point::new(p.x,p.y,p.z);
            let q=query.shape.project_local_point(&p,false).point;(p-q).norm()
        }).collect::<Vec<_>>();
        if gaps.is_empty(){continue;}gaps.sort_by(f64::total_cmp);
        let index=0.99*(gaps.len()-1)as f64;let i=index.floor()as usize;let j=index.ceil()as usize;
        let deviation=gaps[i]+(gaps[j]-gaps[i])*(index-i as f64);
        if best.as_ref().is_none_or(|(old,_)|deviation<*old) {
            let shift=shift.to_array();let frame=std::array::from_fn(|k|[rotation[k][0],rotation[k][1],rotation[k][2],shift[k]]);best=Some((deviation,frame));
        }
    }
    Ok(best.and_then(|(deviation,frame)|(deviation<=2.).then_some(frame)))
}
pub fn carry(mesh:&Mesh,frame:[[f64;4];3])->Mesh {
    let mut out=mesh.clone();
    for (array,translate) in [(&mut out.pos,true),(&mut out.nrm,false)] {
        for p in array.chunks_exact_mut(3) {
            let a=[p[0],p[1],p[2]];
            for k in 0..3 {p[k]=a[0]*frame[k][0]+a[1]*frame[k][1]+a[2]*frame[k][2]+if translate{frame[k][3]}else{0.};}
        }
    }out
}

pub fn catalog(pieces:&[std::path::PathBuf])->Result<Value> {
    let mut meshes=serde_json::Map::new();let mut reads=Vec::new();
    for step in pieces {
        if step.file_stem().is_some_and(|name|name=="enclosure-pump-retainer") {continue;}
        let path=step.with_file_name(format!("{}.mesh",step.file_name().unwrap().to_string_lossy()));
        let Ok(payload)=payload::read(&path) else {continue;};
        if payload.meshes.len()!=1 {continue;}
        let current=payload::digest(step)?;
        ensure!(payload.src.as_deref()==Some(current.as_str()),
            "{} was cut from a {} that is not the one beside it ({} against {}) — it draws that solid's surface wherever it is grafted. Recut it:\n    tools/cad-venv/bin/python hardware/scripts/flute_payload.py",
            path.file_name().unwrap().to_string_lossy(),step.file_name().unwrap().to_string_lossy(),
            payload.src.as_deref().unwrap_or("None").chars().take(12).collect::<String>(),&current[..12]);
        reads.push(step.clone());reads.push(path);
        let mesh=payload.meshes.into_iter().next().unwrap();meshes.insert(mesh.name.clone(),serde_json::to_value(mesh)?);
    }
    Ok(json!({"meshes":meshes,"reads":reads}))
}

pub fn graft(path:&Path,skins:&BTreeMap<String,Mesh>,same_frame:bool,mut select:impl FnMut(&str,Option<&str>)->Result<Option<String>>,owner:Option<&str>)->Result<Value> {
    let Ok(mut host)=payload::read(path) else {return Ok(json!({"landed":0,"moved":[]}));};
    host.version=3;
    if host.src.is_none() {
        let source=path.with_file_name(path.file_name().unwrap().to_string_lossy().trim_end_matches(".mesh"));
        if source.is_file(){host.src=Some(payload::digest(source)?);}
    }
    let mut moved=Vec::new();let mut landed=0;
    for entry in &mut host.meshes {
        // The list-form compatibility reader exposes the four geometry arrays.
        entry.col=None;entry.uv=None;
        let Some(key)=select(&entry.name,owner)? else {continue;};
        let Some(value)=skins.get(&key) else {continue;};
        let mut surface=value.clone();
        let drift=drift(entry,&surface);
        if drift>0.5 && !same_frame {
            if let Some(frame)=placement(entry,&surface,0.5)? {surface=carry(&surface,frame);}
            else {moved.push(json!({"name":entry.name,"drift_mm":drift}));continue;}
        }
        entry.pos=surface.pos;entry.nrm=surface.nrm;entry.idx=surface.idx;entry.fac=surface.fac;
        entry.face_sources=surface.face_sources;landed+=1;
    }
    if landed>0 {
        let data=payload::encode(&host)?;
        if fs::read(path).ok().as_deref()!=Some(&data) {
            let temporary=path.with_file_name(format!("{}.tmp",path.file_name().unwrap().to_string_lossy()));
            fs::write(&temporary,data)?;fs::rename(temporary,path)?;
        }
    }
    Ok(json!({"landed":landed,"moved":moved}))
}
