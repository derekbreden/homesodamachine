//! Printed enclosure presentation at the viewer's existing surface policy.
#[path="enclosure_presentation/quadric.rs"]
mod quadric;
use anyhow::{ensure,Context,Result};
use hsm_geometry::parry::{math::Point,query::PointQuery,shape::TriMesh};
use hsm_kernel::{v3,V3};
use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{collections::{BTreeMap,BTreeSet,HashMap},fs::File,io::{Read,Write},path::Path};

struct Mesh { points:Vec<V3>,faces:Vec<[u32;3]> }
struct Edge { a:u32,b:u32,face:usize }
fn digest(path:&Path)->Result<String> {
    let mut file=File::open(path)?;let mut hash=Sha256::new();let mut block=[0_u8;65536];
    loop {let n=file.read(&mut block)?;if n==0 {break;}hash.update(&block[..n]);}
    let sha=format!("{:x}",hash.finalize());hsm_kernel::reads::digest(path,&sha);Ok(sha)
}
fn stl(path:&Path)->Result<(Mesh,bool)> {
    let bytes=std::fs::read(path)?;hsm_kernel::reads::read(path,&bytes);
    ensure!(bytes.len()>=84,"binary print STL header");
    let count=u32::from_le_bytes(bytes[80..84].try_into()?) as usize;
    ensure!(bytes.len()==84+count*50,"binary print STL triangle count");
    let mut weld=HashMap::<[i64;3],u32>::new();let mut points=Vec::new();let mut faces=Vec::new();let mut exact=true;
    for i in 0..count {
        let mut triangle=[0;3];
        for j in 0..3 {
            let p: [f64;3]=std::array::from_fn(|k| {
                let start=84+i*50+12+j*12+k*4;
                f32::from_le_bytes(bytes[start..start+4].try_into().unwrap()) as f64
            });
            ensure!(p.iter().all(|x| x.is_finite()),"finite print vertices");
            let key=p.map(|x| (x*1.0e8).round_ties_even() as i64);
            let id=*weld.entry(key).or_insert_with(|| {points.push(V3::from(p));(points.len()-1) as u32});
            exact &= points[id as usize].to_array().map(|x| (x as f32).to_bits())==p.map(|x| (x as f32).to_bits());
            triangle[j]=id;
        }
        faces.push(triangle);
    }
    Ok((Mesh{points,faces},exact))
}
fn geometry(mesh:&Mesh)->(Vec<V3>,Vec<f64>,Vec<Edge>) {
    let mut normals=Vec::with_capacity(mesh.faces.len());let mut areas=Vec::with_capacity(mesh.faces.len());let mut edges=Vec::with_capacity(mesh.faces.len()*3);
    for (i,t) in mesh.faces.iter().enumerate() {
        let [a,b,c]=t.map(|k|mesh.points[k as usize]);let cross=(b-a).cross(c-a);let len=cross.norm();
        normals.push(if len>1.0e-15 {cross/len}else{V3::ZERO});areas.push(len/2.);
        for k in 0..3 {edges.push(Edge{a:t[k].min(t[(k+1)%3]),b:t[k].max(t[(k+1)%3]),face:i});}
    }
    edges.sort_by_key(|e|(e.a,e.b,e.face));(normals,areas,edges)
}
struct Random {state:u128,high:Option<u32>}
impl Random {
    // NumPy PCG64's SeedSequence(0), with its uint32 buffering and Lemire bounds.
    fn new()->Self {Self{state:35399562948360463058890781895381311971,high:None}}
    fn next(&mut self)->u64 {
        self.state=self.state.wrapping_mul(0x2360ed051fc65da44385df649fccf645).wrapping_add(87136372517582989555478159403783844777);
        (((self.state>>64) as u64)^(self.state as u64)).rotate_right((self.state>>122) as u32)
    }
    fn next32(&mut self)->u32 {if let Some(high)=self.high.take(){high}else{let n=self.next();self.high=Some((n>>32)as u32);n as u32}}
    fn bounded(&mut self,max:usize)->usize {
        if max==0{return 0;}let range=max as u64+1;
        if max<u32::MAX as usize {
            let threshold=((u32::MAX as u64-max as u64)%range)as u32;
            loop{let m=self.next32()as u64*range;if m as u32>=threshold{return(m>>32)as usize;}}
        }else{
            let threshold=(u64::MAX-max as u64)%range;
            loop{let m=self.next()as u128*range as u128;if m as u64>=threshold{return(m>>64)as usize;}}
        }
    }
}
fn probes(mesh:&Mesh,normals:&[V3],edges:&[Edge],angle:f64)->Vec<usize> {
    let n=mesh.points.len();let size=n.min(40000);let mut rng=Random::new();let mut selected=BTreeSet::new();
    if n<=size {selected.extend(0..n);}
    else if n>10000 && size>n/50 {
        let mut ids=(0..n).collect::<Vec<_>>();for i in ((n-size).max(1)..n).rev(){let j=rng.bounded(i);ids.swap(i,j);}
        selected.extend(ids[n-size..].iter().copied());
    }else{
        for j in n-size..n {let v=rng.bounded(j);if !selected.insert(v){selected.insert(j);}}
    }
    let mut i=0;
    while i<edges.len(){let mut j=i+1;while j<edges.len() && edges[j].a==edges[i].a && edges[j].b==edges[i].b {j+=1;}
        if j-i==2 {let dot=normals[edges[i].face].dot(normals[edges[i+1].face]).clamp(-1.,1.);
            if dot.acos()>=angle {selected.insert(edges[i].a as usize);selected.insert(edges[i].b as usize);}}
        i=j;
    }
    selected.into_iter().collect()
}
fn deviation(original:&Mesh,reduced:&Mesh,probes:&[usize])->Result<f64> {
    let shape=TriMesh::new(reduced.points.iter().map(|p|Point::new(p.x,p.y,p.z)).collect(),reduced.faces.clone()).map_err(|e|anyhow::anyhow!("reduced print mesh: {e}"))?;
    let mut worst:f64=0.;
    for &i in probes {let p=original.points[i];let point=Point::new(p.x,p.y,p.z);
        let q=shape.project_local_point(&point,false).point;worst=worst.max((v3(q.x,q.y,q.z)-p).norm());}
    Ok(worst)
}
fn valid_contributor(v:&Value)->bool {
    if v.is_null(){return true;}
    let Some(m)=v.as_object()else{return false;};
    if !m.get("op").is_some_and(Value::is_string)||!m.get("src").is_some_and(|v|v.is_null()||v.is_string()){return false;}
    m.get("via").is_none_or(|v|v.is_null()||v.as_object().is_some_and(|m|m.get("op").is_some_and(Value::is_string)&&m.get("src").is_some_and(|v|v.is_null()||v.is_string())))
}
fn lineage(path:&Path,count:usize,exact:bool)->Option<Vec<Vec<Value>>> {
    if path.file_name()?.to_str()?!="enclosure-front-top.stl"||!exact{return None;}
    let sidecar=path.with_file_name(format!("{}.sources.json",path.file_name()?.to_str()?));
    let bytes=std::fs::read(&sidecar).ok()?;hsm_kernel::reads::read(&sidecar,&bytes);
    let d:Value=serde_json::from_slice(&bytes).ok()?;
    if d["v"]!=1||d["sha256"].as_str()!=Some(&digest(path).ok()?){return None;}
    let records=d["records"].as_array()?;let indices=d["triangles"].as_array()?;
    if indices.len()!=count||!records.iter().all(|g|g.as_array().is_some_and(|r|r.iter().all(valid_contributor))){return None;}
    indices.iter().map(|i|{let group=records.get(i.as_u64()?as usize)?.as_array()?.clone();Some(if group.is_empty(){vec![Value::Null]}else{group})}).collect()
}
fn source_union<'a>(groups:impl Iterator<Item=&'a Vec<Value>>)->Vec<Value> {
    let mut unique=BTreeMap::new();for group in groups {for record in group {unique.insert(serde_json::to_string(record).unwrap(),record.clone());}}
    if unique.is_empty(){vec![Value::Null]}else{unique.into_values().collect()}
}
fn collapsed_sources(original:&Mesh,reduced:&Mesh,collapses:&[[u32;2]],sources:&[Vec<Value>])->Vec<Vec<Value>> {
    let mut parent=(0..original.points.len()as u32).collect::<Vec<_>>();for &[a,b]in collapses{parent[b as usize]=a;}
    for i in 0..parent.len(){let mut root=parent[i];while parent[root as usize]!=root{root=parent[root as usize];}parent[i]=root;}
    let mapped=original.faces.iter().map(|t|t.map(|i|parent[i as usize])).collect::<Vec<_>>();
    let good=|t:&[u32;3]|t[0]!=t[1]&&t[1]!=t[2]&&t[2]!=t[0];
    let used=mapped.iter().filter(|t|good(t)).flatten().copied().collect::<BTreeSet<_>>();
    let remap=used.into_iter().enumerate().map(|(i,k)|(k,i as u32)).collect::<HashMap<_,_>>();
    let mut groups=HashMap::<[u32;3],Vec<Value>>::new();
    for (t,source)in mapped.iter().zip(sources){if !good(t){continue;}let mut key=t.map(|i|remap[&i]);key.sort_unstable();
        let mut merged=source.clone();if let Some(old)=groups.get(&key){merged=source_union([old,source].into_iter());}groups.insert(key,merged);}
    reduced.faces.iter().map(|t|{let mut key=*t;key.sort_unstable();groups.get(&key).cloned().unwrap_or_else(||vec![Value::Null])}).collect()
}
fn root(parent:&mut[usize],mut i:usize)->usize{while parent[i]!=i{parent[i]=parent[parent[i]];i=parent[i];}i}
fn creased(mesh:&Mesh,angle:f64,sources:Option<&[Vec<Value>]>)->(Vec<f32>,Vec<f32>,Vec<u32>,Vec<u32>,Option<Vec<Vec<Value>>>) {
    let(normals,areas,edges)=geometry(mesh);let mut parent=(0..mesh.faces.len()).collect::<Vec<_>>();let mut i=0;
    while i<edges.len(){let mut j=i+1;while j<edges.len()&&edges[j].a==edges[i].a&&edges[j].b==edges[i].b{j+=1;}
        if j-i==2&&normals[edges[i].face].dot(normals[edges[i+1].face]).clamp(-1.,1.).acos()<=angle {
            let a=root(&mut parent,edges[i].face);let b=root(&mut parent,edges[i+1].face);parent[a.max(b)]=a.min(b);}
        i=j;
    }
    let mut regions=HashMap::new();let mut labels=Vec::with_capacity(parent.len());
    for i in 0..parent.len(){let r=root(&mut parent,i);let next=regions.len();labels.push(*regions.entry(r).or_insert(next));}
    let mut order=(0..mesh.faces.len()).collect::<Vec<_>>();order.sort_by_key(|&i|labels[i]);
    let corners=order.iter().flat_map(|&i|mesh.faces[i].map(|v|(v,labels[i]))).collect::<BTreeSet<_>>();
    let mapping=corners.iter().enumerate().map(|(i,&k)|(k,i)).collect::<HashMap<_,_>>();
    let positions=corners.iter().flat_map(|&(v,_)|mesh.points[v as usize].to_array().map(|x|x as f32)).collect();
    let mut sums=vec![V3::ZERO;corners.len()];let mut first_normal=vec![None;corners.len()];let mut indices=Vec::with_capacity(mesh.faces.len()*3);
    let mut ranges=Vec::new();let mut groups=Vec::new();let mut begin=0;
    for (position,&face)in order.iter().enumerate(){
        let weighted=normals[face]*areas[face];for &v in &mesh.faces[face]{let k=mapping[&(v,labels[face])];indices.push(k as u32);sums[k]+=weighted;if first_normal[k].is_none(){first_normal[k]=Some(normals[face]);}}
        if position+1==order.len()||labels[order[position+1]]!=labels[face]{ranges.extend([begin as u32,position as u32]);
            if let Some(s)=sources{groups.push(source_union(order[begin..=position].iter().map(|&i|&s[i])));}begin=position+1;}
    }
    let blanks=sums.iter().filter(|n|n.norm()<1.0e-12).count();
    let shade=sums.iter().enumerate().flat_map(|(k,n)|{let p=if n.norm()<1.0e-12 {
        if blanks==1 {first_normal[k].unwrap_or(V3::Z).unit()} else {V3::Z}
    }else{n.unit()};p.to_array().map(|x|x as f32)}).collect();
    (positions,shade,indices,ranges,sources.map(|_|groups))
}
fn identity(path:&Path)->Result<(Value,Value)> {
    let mut archive=zip::ZipArchive::new(File::open(path)?)?;
    let mut read=|name:&str|->Result<Value>{let data=npyz::NpyFile::new(archive.by_name(&format!("{name}.npy"))?)?;
        Ok(serde_json::from_slice(&data.into_vec::<u8>()?)?)};
    let names=read("names")?;let colors=read("colors")?;
    ensure!(names.as_array().is_some_and(|a|a.len()==1)&&colors.as_array().is_some_and(|a|a.len()==1),"one identity per printed piece");
    Ok((names[0].clone(),colors[0].clone()))
}
fn write_payload(path:&Path,name:Value,color:Value,src:&str,bound:f64,dev:f64,
    arrays:(Vec<f32>,Vec<f32>,Vec<u32>,Vec<u32>,Option<Vec<Vec<Value>>>),unknown:bool)->Result<()> {
    let(pos,nrm,idx,fac,sources)=arrays;let mut blob=Vec::new();let mut entry=json!({"name":name,"color":color});
    for(key,data)in[("pos",pos.into_iter().flat_map(f32::to_le_bytes).collect::<Vec<_>>()),("nrm",nrm.into_iter().flat_map(f32::to_le_bytes).collect())]{entry[key]=json!([blob.len(),data.len()/4]);blob.extend(data);}
    let faces=fac.len()/2;
    for(key,data)in[("idx",idx.into_iter().flat_map(u32::to_le_bytes).collect::<Vec<_>>()),("fac",fac.into_iter().flat_map(u32::to_le_bytes).collect())]{entry[key]=json!([blob.len(),data.len()/4]);blob.extend(data);}
    if let Some(s)=sources{entry["face_sources"]=json!(s);}else if unknown{entry["face_sources"]=json!(vec![vec![Value::Null];faces]);}
    let round=|x:f64|format!("{x:.4}").parse::<f64>().unwrap();
    let header=json!({"v":3,"meshes":[entry],"src":src,"cut":{"dev":round(dev),"bound":round(bound)}});
    let mut text=serde_json::to_vec(&header)?;while(text.len()+4)%4!=0{text.push(b' ');}
    let mut file=File::create(path)?;file.write_all(&(text.len()as u32).to_le_bytes())?;file.write_all(&text)?;file.write_all(&blob)?;Ok(())
}
fn run(n:&Value,out:&Path)->Result<Value> {
    let stl_path=Path::new(n["stl"].as_str().context("print STL")?);let model=Path::new(n["model"].as_str().context("fine model")?);
    let(mesh,exact)=stl(stl_path)?;ensure!(!mesh.faces.is_empty(),"printed mesh has triangles");
    let(normals,_,edges)=geometry(&mesh);let mut non_manifold=0;let mut watertight=true;let mut i=0;
    while i<edges.len(){let mut j=i+1;while j<edges.len()&&edges[j].a==edges[i].a&&edges[j].b==edges[i].b{j+=1;}
        if j-i>2{non_manifold+=1;}if j-i!=2{watertight=false;}i=j;}
    if n["check_print"].as_bool().unwrap_or(false){ensure!(non_manifold==0&&watertight,"{}: {non_manifold} non-manifold edge(s), watertight={watertight}",stl_path.display());}
    let angle=n["crease_deg"].as_f64().context("crease angle")?.to_radians();let probe=probes(&mesh,&normals,&edges,angle);
    let mut lo=v3(f64::INFINITY,f64::INFINITY,f64::INFINITY);let mut hi=-lo;for &p in &mesh.points{lo=lo.min(p);hi=hi.max(p);}
    let size=hi-lo;let bound=(size.x+size.y+size.z)/3.*n["deflection_ratio"].as_f64().context("deflection ratio")?;
    let original_sources=lineage(stl_path,mesh.faces.len(),exact);let mut accepted=None;
    for reduction in [0.97,0.95,0.90,0.80,0.75,0.60]{
        let(points,faces,collapses)=quadric::simplify(&mesh.points,&mesh.faces,reduction,4.);
        let reduced=Mesh{points,faces};let dev=deviation(&mesh,&reduced,&probe)?;
        if dev<=bound{let sources=original_sources.as_ref().map(|s|collapsed_sources(&mesh,&reduced,&collapses,s));accepted=Some((reduced,dev,sources,reduction));break;}
    }
    let(reduced,dev,sources,reduction)=accepted.unwrap_or_else(||(Mesh{points:mesh.points.clone(),faces:mesh.faces.clone()},0.,original_sources,0.));
    let(name,color)=identity(model)?;let filename=format!("{}.mesh",n["step_name"].as_str().context("STEP filename")?);
    let output=out.join(&filename);std::fs::create_dir_all(out)?;let sha=digest(model)?;
    let arrays=creased(&reduced,angle,sources.as_deref());
    write_payload(&output,name,color,&sha,bound,dev,arrays,stl_path.file_name().and_then(|s|s.to_str())==Some("enclosure-front-top.stl"))?;
    Ok(json!({"files":[filename],"bodies":[],"printed_triangles":mesh.faces.len(),"drawing_triangles":reduced.faces.len(),"bound":bound,"deviation":dev,"reduction":reduction,"probe_vertices":probe.len(),"watertight":watertight,"non_manifold_edges":non_manifold}))
}
fn main()->Result<()> {
    let args=std::env::args().collect::<Vec<_>>();ensure!(args.len()==3,"usage: enclosure-presentation <numbers.json> <out directory>");
    let bytes=std::fs::read(&args[1])?;hsm_kernel::reads::read(Path::new(&args[1]),&bytes);
    let numbers:Value=serde_json::from_slice(&bytes)?;println!("{}",serde_json::to_string(&run(&numbers,Path::new(&args[2]))?)?);Ok(())
}
