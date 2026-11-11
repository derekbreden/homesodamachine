//! experiment.rs maps the frozen faucet article into bounded contact bands and restores its physical print paths.
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::{V3, v3};
use serde_json::{Value, json};
use std::{collections::{BTreeMap, HashMap}, fs, io::{BufRead, BufReader, BufWriter, Write}, path::{Path, PathBuf}};

#[derive(Clone)]
struct Mapping {
    spec: Value,
    normal: V3,
    plane_d: f64,
}
impl Mapping {
    fn value(&self, name: &str) -> f64 { self.spec[name].as_f64().unwrap() }
    fn smooth(t: f64) -> f64 { let t=t.clamp(0.,1.); t*t*(3.-2.*t) }
    fn face_z(&self, p: V3) -> f64 { (self.plane_d-self.normal.x*p.x-self.normal.y*p.y)/self.normal.z }
    fn offset(&self, p: V3) -> f64 {
        let f=self.face_z(p);
        let period=self.value("band_period_mm");
        let r=(f-self.value("band_phase_mm")+period/2.).rem_euclid(period)-period/2.;
        let delta=if r.abs()<=period/4. {r} else {r.signum()*(period/2.-r.abs())};
        let bed=self.spec["bed_blend_mm"].as_array().unwrap();
        let b=Self::smooth((p.z-bed[0].as_f64().unwrap())/(bed[1].as_f64().unwrap()-bed[0].as_f64().unwrap()));
        let full=self.spec["contact_full_weight_mm"].as_array().unwrap();
        let zero=self.spec["contact_zero_weight_mm"].as_array().unwrap();
        let d=p.z-f;
        let weight=if d<full[0].as_f64().unwrap() {
            Self::smooth((d-zero[0].as_f64().unwrap())/(full[0].as_f64().unwrap()-zero[0].as_f64().unwrap()))
        } else if d>full[1].as_f64().unwrap() {
            1.-Self::smooth((d-full[1].as_f64().unwrap())/(zero[1].as_f64().unwrap()-full[1].as_f64().unwrap()))
        } else {1.};
        delta*b*weight
    }
    fn forward(&self, p: V3) -> V3 { v3(p.x,p.y,p.z-self.offset(p)) }
    fn inverse(&self, p: V3) -> V3 {
        let mut q=p;
        for _ in 0..20 { q.z=p.z+self.offset(q); }
        q
    }
    fn stretch(&self, p: V3, height: f64) -> f64 {
        (self.inverse(p).z-self.inverse(p-v3(0.,0.,height)).z)/height
    }
    fn interval_active(&self, a: V3, b: V3) -> bool {
        let da=a.z-self.face_z(a);let db=b.z-self.face_z(b);
        a.z.max(b.z)>self.spec["bed_blend_mm"][0].as_f64().unwrap()
            && da.min(db)<self.spec["contact_zero_weight_mm"][1].as_f64().unwrap()
            && da.max(db)>self.spec["contact_zero_weight_mm"][0].as_f64().unwrap()
    }
}
fn point(value: &Value) -> V3 { v3(value[0].as_f64().unwrap(),value[1].as_f64().unwrap(),value[2].as_f64().unwrap()) }
fn xy(p: V3) -> f64 { p.x.hypot(p.y) }
fn arr(p: V3) -> [f64;3] { [p.x,p.y,p.z] }
fn read(path: &Path) -> Result<Value> { Ok(serde_json::from_slice(&fs::read(path)?)?) }
fn write(path: &Path, value: &Value) -> Result<()> { fs::write(path,serde_json::to_vec_pretty(value)?)?;Ok(()) }

fn geometry(input: &Path, spec_path: &Path, out: &Path) -> Result<()> {
    fs::create_dir_all(out)?;
    let original=read(input)?;
    let mut vertices: Vec<_>=original["vertices"].as_array().context("vertices")?.iter().map(point).collect();
    let mut triangles: Vec<[usize;3]>=original["triangles"].as_array().context("triangles")?.iter().map(|f|std::array::from_fn(|i|f[i].as_u64().unwrap() as usize)).collect();
    let mut groups:BTreeMap<[i64;4],(f64,V3,f64,usize)>=BTreeMap::new();
    for &[a,b,c] in &triangles {
        let cross=(vertices[b]-vertices[a]).cross(vertices[c]-vertices[a]);
        let area=cross.norm()/2.;if area<1e-12 {continue;}
        let n=cross/(2.*area);if n.z>-0.5 {continue;}
        let d=n.dot(vertices[a]);
        let key=[(n.x*1e4).round() as i64,(n.y*1e4).round() as i64,(n.z*1e4).round() as i64,(d*100.).round() as i64];
        let row=groups.entry(key).or_insert((0.,V3::ZERO,0.,0));row.0+=area;row.1+=n*area;row.2+=d*area;row.3+=1;
    }
    let (_,dominant)=groups.iter().max_by(|a,b|a.1.0.total_cmp(&b.1.0)).context("dominant underside plane")?;
    let normal=dominant.1/dominant.0;
    let mapping=Mapping {spec:read(spec_path)?,normal,plane_d:dominant.2/dominant.0};
    let mut definition=json!({"purpose":"Bind the bounded nonplanar map to the dominant inclined contact plane of the complete frozen article.","parameters":mapping.spec,"plane_normal":arr(mapping.normal),"plane_d_mm":mapping.plane_d,"plane_area_mm2":dominant.0,"source_vertices":vertices.len(),"source_triangles":triangles.len()});
    let maximum_y=mapping.value("maximum_mesh_y_step_mm");
    let maximum_z=mapping.value("maximum_mesh_z_step_mm");
    let tolerance=mapping.value("maximum_mesh_mapping_error_mm");
    for round in 0..18 {
        let mut splits=HashMap::new();
        for &[a,b,c] in &triangles {
            for (u,v) in [(a,b),(b,c),(c,a)] {
                let key=if u<v {(u,v)} else {(v,u)};if splits.contains_key(&key){continue;}
                let (p,q)=(vertices[u],vertices[v]);
                if !mapping.interval_active(p,q){continue;}
                let mid=(p+q)/2.;
                let error=(mapping.forward(mid)-(mapping.forward(p)+mapping.forward(q))/2.).norm();
                if (p.y-q.y).abs()>maximum_y || (p.z-q.z).abs()>maximum_z || error>tolerance {
                    let i=vertices.len();vertices.push(mid);splits.insert(key,i);
                }
            }
        }
        if splits.is_empty(){break;}
        let mut refined=Vec::with_capacity(triangles.len()*2);
        for [a,b,c] in triangles {
            let edges=[(a,b),(b,c),(c,a)].map(|(u,v)|splits.get(&if u<v {(u,v)} else {(v,u)}).copied());
            match edges {
                [None,None,None]=>refined.push([a,b,c]),
                [Some(m),None,None]=>refined.extend([[a,m,c],[m,b,c]]),
                [None,Some(m),None]=>refined.extend([[b,m,a],[m,c,a]]),
                [None,None,Some(m)]=>refined.extend([[c,m,b],[m,a,b]]),
                [Some(m),Some(n),None]=>refined.extend([[m,b,n],[a,m,c],[m,n,c]]),
                [None,Some(m),Some(n)]=>refined.extend([[m,c,n],[b,m,a],[m,n,a]]),
                [Some(n),None,Some(m)]=>refined.extend([[m,a,n],[c,m,b],[m,n,b]]),
                [Some(ab),Some(bc),Some(ca)]=>refined.extend([[a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]]),
            }
        }
        triangles=refined;
        println!("mesh refinement {round}: {} triangles",triangles.len());
        ensure!(triangles.len()<3_000_000,"Excessive refinement");
    }
    let mut worst_error=0f64;
    let mut min_jacobian=f64::INFINITY;
    let mut max_roundtrip=0f64;
    let mut max_offset=0f64;
    let mut changed=0;
    for &p in &vertices {
        let mapped=mapping.forward(p);let restored=mapping.inverse(mapped);
        max_roundtrip=max_roundtrip.max((restored-p).norm());
        max_offset=max_offset.max((mapped.z-p.z).abs());
        if (mapped.z-p.z).abs()>0.001 {changed+=1;}
        let jac=(mapping.forward(p+v3(0.,0.,0.001)).z-mapping.forward(p-v3(0.,0.,0.001)).z)/0.002;
        min_jacobian=min_jacobian.min(jac);
    }
    for &[a,b,c] in &triangles {
        let centre=(vertices[a]+vertices[b]+vertices[c])/3.;
        let approximation=(mapping.forward(vertices[a])+mapping.forward(vertices[b])+mapping.forward(vertices[c]))/3.;
        worst_error=worst_error.max((mapping.inverse(approximation)-centre).norm());
    }
    ensure!(max_roundtrip<1e-5 && min_jacobian>0.65 && worst_error<0.012,"Mapping failed geometric review: roundtrip={max_roundtrip}, jac={min_jacobian}, error={worst_error}");
    definition["refined_vertices"]=json!(vertices.len());definition["refined_triangles"]=json!(triangles.len());
    definition["mapped_vertices"]=json!(changed);definition["maximum_vertical_offset_mm"]=json!(max_offset);
    definition["minimum_sampled_vertical_jacobian"]=json!(min_jacobian);definition["maximum_vertex_roundtrip_error_mm"]=json!(max_roundtrip);
    definition["maximum_sampled_facet_restoration_error_mm"]=json!(worst_error);
    write(&out.join("mapping.json"),&definition)?;
    write(&out.join("slicer-mesh.json"),&json!({"vertices":vertices.iter().map(|p|arr(mapping.forward(*p))).collect::<Vec<_>>(),"triangles":triangles}))?;
    println!("geometry map: {}",definition);
    Ok(())
}

fn words(line:&str)->Vec<(char,f64)> {
    let data=line.split(';').next().unwrap().as_bytes();let mut out=Vec::new();let mut i=0;
    while i<data.len() {
        let key=data[i] as char;
        if key.is_ascii_uppercase() {
            let start=i+1;let mut end=start;
            while end<data.len()&&(data[end].is_ascii_digit()||matches!(data[end],b'.'|b'-'|b'+')) {end+=1;}
            if end>start {if let Ok(value)=std::str::from_utf8(&data[start..end]).unwrap().parse::<f64>() {out.push((key,value));}i=end;continue;}
        }
        i+=1;
    }
    out
}
fn get(words:&[(char,f64)], key:char)->Option<f64> {words.iter().rev().find(|w|w.0==key).map(|w|w.1)}

fn paths(input:&Path, definition:&Path, output:&Path)->Result<()> {
    let d=read(definition)?;
    let mapping=Mapping {spec:d["parameters"].clone(),normal:point(&d["plane_normal"]),plane_d:d["plane_d_mm"].as_f64().unwrap()};
    let mut out=BufWriter::new(fs::File::create(output)?);
    let mut rows=BufWriter::new(fs::File::create(output.with_extension("roads.jsonl"))?);
    let mut position=V3::ZERO;let mut actual=V3::ZERO;let mut feed=1800.;let mut relative_e=true;let mut absolute=true;
    let mut body=false;let mut height=0.24;let mut width=0.42;let mut feature=String::new();let mut object=0;
    let mut layer=0;let mut highest=0f64;let mut emitted_feed=0f64;let mut retract_debt=0f64;
    let mut total_roads=0u64;let mut conformal_roads=0u64;let mut total_extra_seconds=0f64;let mut max_slope=0f64;let mut max_motion_offset=0f64;
    let mut extra_travel=0f64;let mut extra_deposition=0f64;let mut deepest_deposition=0f64;let mut max_z_speed=0f64;
    let mut volumes=BTreeMap::<String,f64>::new();let mut minimum_layer_height=f64::INFINITY;let mut maximum_layer_height=0f64;
    for line in BufReader::new(fs::File::open(input)?).lines() {
        let line=line?;
        if line.contains("; CHANGE_LAYER"){body=true;layer+=1;}
        if line.contains("; MACHINE_END_GCODE_START"){body=false;}
        if let Some(v)=line.strip_prefix("; LAYER_HEIGHT: "){height=v.parse()?;}
        if let Some(v)=line.strip_prefix("; LINE_WIDTH: "){width=v.parse()?;}
        if let Some(v)=line.strip_prefix("; FEATURE: "){feature=v.to_string();}
        if let Some(v)=line.strip_prefix("; OBJECT_ID: "){object=v.parse().unwrap_or(0);}
        let w=words(&line);let code=line.split(';').next().unwrap().trim();
        if code=="G90" {absolute=true;}if code=="G91" {absolute=false;}
        if code.starts_with("M83"){relative_e=true;}if code.starts_with("M82"){relative_e=false;}
        let is_motion=matches!(get(&w,'G'),Some(0.)|Some(1.)|Some(2.)|Some(3.));
        if !is_motion {writeln!(out,"{line}")?;continue;}
        let old=position;
        let mut target=position;
        for (axis,key) in [(0,'X'),(1,'Y'),(2,'Z')] {
            if let Some(v)=get(&w,key){let value=if absolute {v}else {target[axis]+v};match axis {0=>target.x=value,1=>target.y=value,_=>target.z=value};}
        }
        let previous_feed=feed;if let Some(f)=get(&w,'F'){feed=f;}
        let e=get(&w,'E');let extrusion=e.unwrap_or(0.);
        if body {retract_debt=(retract_debt-extrusion).max(0.);}
        let arc=matches!(get(&w,'G'),Some(2.)|Some(3.));
        if !body {position=target;actual=target;emitted_feed=feed;writeln!(out,"{line}")?;continue;}
        ensure!(absolute&&relative_e,"The contact experiment requires absolute XYZ and relative E");
        let frozen_bed=layer<=2;
        let lateral=xy(target-old);
        if lateral<1e-9&&!arc {
            if frozen_bed {writeln!(out,"{line}")?;position=target;actual=target;emitted_feed=feed;continue;}
            if get(&w,'Z').is_some(){ensure!(e.is_none(),"Unexpected combined vertical and extruder move");actual=mapping.inverse(target);writeln!(out,"G1 Z{:.5} F{:.0}",actual.z,mapping.value("travel_z_speed_mm_s")*60.)?;emitted_feed=mapping.value("travel_z_speed_mm_s")*60.;}
            else {
                if e.is_some() && (emitted_feed-feed).abs()>0.1 {writeln!(out,"G1 F{feed:.0}")?;emitted_feed=feed;}
                writeln!(out,"{line}")?;if get(&w,'F').is_some(){emitted_feed=feed;}
            }
            position=target;continue;
        }
        let mut points=Vec::new();
        if arc {
            let centre=old+v3(get(&w,'I').unwrap_or(0.),get(&w,'J').unwrap_or(0.),0.);
            ensure!(get(&w,'R').is_none(),"Radius-format arc needs explicit review");
            let start=(old.y-centre.y).atan2(old.x-centre.x);let end=(target.y-centre.y).atan2(target.x-centre.x);
            let ccw=get(&w,'G')==Some(3.);let mut sweep=if ccw {(end-start).rem_euclid(std::f64::consts::TAU)}else {-((start-end).rem_euclid(std::f64::consts::TAU))};
            if sweep.abs()<1e-9 {sweep=if ccw {std::f64::consts::TAU}else {-std::f64::consts::TAU};}
            let radius=xy(old-centre);let count=(sweep.abs()*radius/mapping.value("maximum_gcode_segment_mm")).ceil().max(1.) as usize;
            for i in 1..=count {let f=i as f64/count as f64;let a=start+sweep*f;points.push(v3(centre.x+radius*a.cos(),centre.y+radius*a.sin(),old.z+(target.z-old.z)*f));}
        } else {
            let active=mapping.interval_active(old,target);
            let count=if active {((target-old).norm()/mapping.value("maximum_gcode_segment_mm")).ceil().max(1.) as usize}else{1};
            for i in 1..=count {points.push(old+(target-old)*(i as f64/count as f64));}
        }
        let restored=if frozen_bed {target}else{mapping.inverse(target)};
        if e.is_none()||extrusion==0. {
            if frozen_bed {writeln!(out,"{line}")?;position=target;actual=target;emitted_feed=feed;continue;}
            if (actual.z-old.z).abs()<1e-5 && (restored.z-target.z).abs()<1e-5 && actual.z.min(restored.z)>=highest-1e-5 {
                writeln!(out,"G1 X{:.5} Y{:.5} Z{:.5} F{feed:.0}",restored.x,restored.y,restored.z)?;
                emitted_feed=feed;actual=restored;position=target;continue;
            }
            let safe=actual.z.max(restored.z).max(highest+mapping.value("travel_clearance_mm"));
            let extra=((safe-actual.z).max(0.)+(safe-restored.z).max(0.))/(mapping.value("travel_z_speed_mm_s"));
            total_extra_seconds+=extra;extra_travel+=extra;
            let retract=if extra>0.001 && retract_debt<0.01 {mapping.value("travel_retract_mm")}else{0.};
            if retract>0. {writeln!(out,"G1 E{:.5} F{:.0}",-retract,mapping.value("travel_retract_speed_mm_s")*60.)?;total_extra_seconds+=2.*retract/mapping.value("travel_retract_speed_mm_s");}
            writeln!(out,"G1 Z{safe:.5} F{:.0}",mapping.value("travel_z_speed_mm_s")*60.)?;
            writeln!(out,"G1 X{:.5} Y{:.5} F{feed:.0}",restored.x,restored.y)?;
            writeln!(out,"G1 Z{:.5} F{:.0}",restored.z,mapping.value("travel_z_speed_mm_s")*60.)?;
            emitted_feed=mapping.value("travel_z_speed_mm_s")*60.;
            if retract>0. {writeln!(out,"G1 E{retract:.5} F{:.0}",mapping.value("travel_retract_speed_mm_s")*60.)?;emitted_feed=mapping.value("travel_retract_speed_mm_s")*60.;}
            actual=restored;position=target;continue;
        }
        let steps=points.len();let mut native_from=old;
        if frozen_bed {writeln!(out,"{line}")?;}
        for (index,p) in points.into_iter().enumerate() {
            let q=if frozen_bed {p}else{mapping.inverse(p)};let midpoint=(native_from+p)/2.;let qmid=mapping.inverse(midpoint);
            let shifted=(q.z-p.z).abs()>1e-5||(actual.z-native_from.z).abs()>1e-5;
            let h=if frozen_bed {height}else{height*mapping.stretch(midpoint,height)};
            let amount=extrusion/steps as f64*if extrusion>0. {h/height}else{1.};
            let l=(q-actual).norm();let dz=(q.z-actual.z).abs();
            let selected=if shifted && dz>1e-6 {feed.min(mapping.value("maximum_nonplanar_z_speed_mm_s")*60.*l/dz)}else{feed};
            if !frozen_bed {
                if (selected-emitted_feed).abs()>0.1 {writeln!(out,"G1 F{selected:.0}")?;emitted_feed=selected;}
                writeln!(out,"G1 X{:.5} Y{:.5} Z{:.5} E{amount:.7}",q.x,q.y,q.z)?;
            } else {emitted_feed=feed;}
            let xy=xy(q-actual);
            if extrusion>0.&&xy>1e-8 {
                total_roads+=1;max_motion_offset=max_motion_offset.max((q.z-p.z).abs());
                if shifted {conformal_roads+=1;max_slope=max_slope.max(((q.z-actual.z).abs()/xy).atan().to_degrees());}
                let extra=(l/selected-(p-native_from).norm()/feed)*60.;total_extra_seconds+=extra;extra_deposition+=extra;
                deepest_deposition=deepest_deposition.max(highest-actual.z.min(q.z));
                if shifted {max_z_speed=max_z_speed.max(dz/l*selected/60.);}
                minimum_layer_height=minimum_layer_height.min(h);maximum_layer_height=maximum_layer_height.max(h);
                *volumes.entry(feature.clone()).or_default()+=amount;
                writeln!(rows,"{}",json!({"layer":layer,"object":object,"feature":feature,"from":arr(actual),"to":arr(q),"nominal_from":arr(native_from),"nominal_to":arr(p),"width":width,"height":h,"feed":selected,"native_feed":feed,"extrusion":amount,"mapped":shifted}))?;
                highest=highest.max(actual.z).max(q.z);
            }
            let _=(previous_feed,qmid,index);
            actual=q;native_from=p;
        }
        position=target;
    }
    out.flush()?;rows.flush()?;
    write(&output.with_extension("review.json"),&json!({"purpose":"Read the restored actual movements of the complete faucet test before printer submission.","scope":"Commanded XYZ motion, extrusion volume and bounded displacement; physical finish and release remain unmeasured.","deposited_segments":total_roads,"nonplanar_segments":conformal_roads,"maximum_vertical_motion_offset_mm":max_motion_offset,"maximum_nonplanar_segment_angle_degrees":max_slope,"minimum_vertical_layer_height_mm":minimum_layer_height,"maximum_vertical_layer_height_mm":maximum_layer_height,"maximum_deposited_z_mm":highest,"estimated_added_motion_seconds":total_extra_seconds,"extra_deposition_seconds":extra_deposition,"extra_travel_seconds":extra_travel,"maximum_deposition_depth_below_prior_peak_mm":deepest_deposition,"maximum_nonplanar_z_speed_mm_s":max_z_speed,"filament_length_by_feature_mm":volumes,"travel_clearance_over_deposited_maximum_mm":mapping.value("travel_clearance_mm"),"native_start_end_preserved":true}))?;
    println!("restored {conformal_roads}/{total_roads} deposition segments; max offset {max_motion_offset:.5}; max slope {max_slope:.3}; added motion {total_extra_seconds:.1}s");
    Ok(())
}
fn main()->Result<()> {
    let args:Vec<_>=std::env::args().collect();
    if args.len()!=5 {bail!("Use geometry <mesh.json> <parameters.json> <output>, or paths <native.gcode> <mapping.json> <restored.gcode>");}
    let paths_in:Vec<PathBuf>=args[2..].iter().map(PathBuf::from).collect();
    match args[1].as_str(){"geometry"=>geometry(&paths_in[0],&paths_in[1],&paths_in[2]),"paths"=>paths(&paths_in[0],&paths_in[1],&paths_in[2]),_=>bail!("Unknown experiment operation")}
}
