//! Analytic snap profiles and installed frames supplied to compiled machine recipes.
use crate::compiled::{Env, Runtime, Val};
use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};

fn arg<'a>(args: &'a [Val], kwargs: &'a [(String, Val)], index: usize, name: &str) -> Result<&'a Val> {
    args.get(index).or_else(|| kwargs.iter().find(|(key, _)| key == name).map(|(_, value)| value))
        .with_context(|| format!("missing {name}"))
}
fn number(args: &[Val], kwargs: &[(String, Val)], index: usize, name: &str, default: f64) -> Result<f64> {
    args.get(index).or_else(|| kwargs.iter().find(|(key, _)| key == name).map(|(_, value)| value))
        .map(Val::num).transpose().map(|value| value.unwrap_or(default))
}
fn row(value: &Val) -> Result<Vec<f64>> { value.iter()?.iter().map(Val::num).collect() }
fn pairs(value: &Val) -> Result<Vec<[f64; 2]>> {
    value.iter()?.iter().map(|value| { let r = row(value)?; ensure!(r.len() == 2, "an axial profile has two columns"); Ok([r[0], r[1]]) }).collect()
}
fn value(value: Value) -> Result<Val> { Val::decode(value) }
fn field(value: &Val, name: &str) -> Result<Val> { value.get(name.into()) }
fn f(value: &Val, name: &str) -> Result<f64> { field(value, name)?.num() }
fn interpolate(points: &[[f64; 2]], x: f64) -> f64 {
    if x < points[0][0] { return points[0][1]; }
    let last = points.len()-1;
    if x >= points[last][0] { return points[last][1]; }
    let i = points.partition_point(|point| point[0] <= x).saturating_sub(1);
    let [a, ra] = points[i]; let [b, rb] = points[i+1];
    if b == a { rb } else { ra + (rb-ra)*(x-a)/(b-a) }
}
fn clearance(points: &[[f64; 2]], radial: f64, axial: f64, tolerance: f64) -> Result<Vec<[f64; 2]>> {
    ensure!(!points.is_empty(), "an axial profile is empty");
    let mut stations: Vec<_> = points.iter().flat_map(|p| [p[0]-axial, p[0]+axial]).collect();
    stations.sort_by(f64::total_cmp); stations.dedup();
    let points: Vec<[f64; 2]> = stations.iter().map(|&x| {
        let end = interpolate(points,x-axial).max(interpolate(points,x+axial));
        let widest = points.iter().filter(|p| p[0]>=x-axial-1e-8 && p[0]<=x+axial+1e-8).fold(end, |r,p| r.max(p[1]));
        [x,widest+radial]
    }).collect();
    let mut kept=vec![points[0]]; let mut i=0;
    while i+1<points.len() {
        let mut best=i+1;
        for j in i+2..points.len() {
            let line=[points[i],points[j]];
            let mut low=f64::INFINITY;let mut high=f64::NEG_INFINITY;
            for p in &points[i..=j] {let d=interpolate(&line,p[0])-p[1];low=low.min(d);high=high.max(d);}
            if low>=-1e-8 && high<=tolerance {best=j;}
        }
        kept.push(points[best]);i=best;
    }
    Ok(kept)
}
fn solve(a:[f64;2],b:[f64;2],u:f64,v:f64)->Result<[f64;2]>{
    let d=a[0]*b[1]-a[1]*b[0];ensure!(d.abs()>1e-15,"parallel hex planes");
    Ok([(u*b[1]-a[1]*v)/d,(a[0]*v-u*b[0])/d])
}
fn section(points:&[[f64;2]],span:[f64;2])->Value{
    json!({"segments":(0..points.len()).map(|i|json!({"line":[points[i],points[(i+1)%points.len()]]})).collect::<Vec<_>>(),"span":span})
}
fn external(rt:&Runtime,module:&str,path:&[&str])->Result<Val>{let mut value=rt.import_module(module)?;for name in path{value=value.attr(name)?;}Ok(value)}
fn json_value(v:&Val)->Result<Value>{
    Ok(match v {
        Val::Tuple(rows)=>Value::Array(rows.iter().map(json_value).collect::<Result<_>>()?),
        Val::List(rows)=>Value::Array(rows.borrow().iter().map(json_value).collect::<Result<_>>()?),
        Val::Dict(rows)|Val::Namespace(rows)=>Value::Object(rows.borrow().iter().map(|(k,v)|Ok((k.str()?,json_value(v)?))).collect::<Result<_>>()?),
        Val::Ref(_)=>{
            let concrete=Val::decode(hsm_documents::interop::callback(json!({"op":"snapshot","object":v.encode()?}))?)?;
            if matches!(concrete,Val::Ref(_)) {json_value(&v.attr("tolist")?.call(vec![],vec![])?)?}
            else {json_value(&concrete)?}
        },
        _=>v.encode()?,
    })
}

/// The absolute path of a stream opened `rb` from a named file, when `file_digest` is called as
/// these modules call it: the stream and the digest, positionally.
fn named_binary(args: &[Val], kwargs: &[(String, Val)]) -> Option<std::path::PathBuf> {
    let [stream, _digest] = args else { return None };
    if !kwargs.is_empty() || !matches!(stream.attr("mode"), Ok(Val::Str(mode)) if mode == "rb") {
        return None;
    }
    match stream.attr("name") {
        Ok(Val::Str(name)) if std::path::Path::new(&name).is_absolute() => Some(name.into()),
        _ => None,
    }
}

/// A module's `hashlib.file_digest`, reading a named binary file in this process from the
/// stream's position instead of block by block through the Python file object. The stream is
/// left at its end, as `hashlib` leaves it.
fn local_file_digest(hashlib: &Val) {
    use std::io::{Read, Seek, SeekFrom};
    let Val::Namespace(rows) = hashlib else { return };
    let mut rows = rows.borrow_mut();
    let Some(slot) = rows.iter_mut().find(|(key, _)| matches!(key, Val::Str(key) if key == "file_digest")) else {
        return;
    };
    let standard = slot.1.clone();
    slot.1 = Val::function(move |args, kwargs| {
        let Some(path) = named_binary(&args, &kwargs) else { return standard.call(args, kwargs) };
        let mut file = std::fs::File::open(&path)?;
        file.seek(SeekFrom::Start(args[0].attr("tell")?.call(vec![], vec![])?.integer()?.try_into()?))?;
        hsm_documents::interop::note_io(&path, false);
        let file = std::cell::RefCell::new(file);
        let reader = Val::namespace(vec![("read".into(), Val::function(move |args, _| {
            let mut block = Vec::new();
            let mut file = file.borrow_mut();
            match args.first().map(Val::integer).transpose()? {
                Some(size) if size >= 0 => (&mut *file).take(size as u64).read_to_end(&mut block)?,
                _ => file.read_to_end(&mut block)?,
            };
            Ok(Val::Bytes(block))
        }))]);
        let hash = standard.call(vec![reader, args[1].clone()], vec![])?;
        args[0].attr("seek")?.call(vec![Val::Int(0), Val::Int(2)], vec![])?;
        Ok(hash)
    });
}

pub fn install(rt: Runtime, e: &Env, module: &str) -> Result<()> {
    // These digest model files of several hundred MB.
    if matches!(module, "_machine_checks" | "_machine_reporting" | "check_asse_drain") {
        if let Ok(hashlib) = e.get("hashlib") {
            local_file_digest(&hashlib);
        }
    }
    if module=="check_asse_drain" {
        e.set("centerline_radii",Val::function(|args,kw|value(json!(crate::curvature::centerline_radii(&json_value(arg(&args,&kw,0,"segments")?)?)?))))?;
        e.set("_names",Val::function(|args,kw|{
            let path=arg(&args,&kw,0,"path")?.str()?;
            hsm_documents::interop::note_io(std::path::Path::new(&path),false);
            value(crate::archive::metadata(&json!({"path":path,"kind":"names"}))?)
        }))?;
        e.set("_torus_records",Val::function(|args,kw|{
            let path=arg(&args,&kw,0,"path")?.str()?;
            let records=crate::archive::metadata(&json!({"path":path,"kind":"records"}))?;
            hsm_documents::interop::note_io(std::path::Path::new(&path),false);
            let mut out=Vec::new();
            for pair in arg(&args,&kw,1,"entries")?.iter()? {
                let pair=pair.iter()?;let index=pair[0].integer()? as usize;let name=pair[1].str()?;
                for (face,record) in records[index].as_array().context("fine face records")?.iter().enumerate(){
                    if record["kind"]=="TORUS" {out.push(json!({"entry_index":index,"qualified_name":name,"face_index":face,"record":record}));}
                }
            }
            value(json!(out))
        }))?;
    }
    if module == "_machine" {
        let root=rt.root_path().to_string_lossy().into_owned();
        e.set("sources",Val::function(move|_,_|Ok(Val::tuple(value(crate::io::request(&json!({"op":"machine_sources","root":root}))?)?.iter()?))))?;
        let root=rt.root_path().to_string_lossy().into_owned();
        e.set("stamps",Val::function(move|_,_|value(crate::io::request(&json!({"op":"machine_stamps","root":root}))?)))?;
    }
    if module == "rear_plumbing" {
        let rt=rt.clone();
        e.set("regulator_datums",Val::function(move|_,_| {
            let data=external(&rt,"rear_plumbing",&["plan"])?.call(vec![],vec![])?;
            let mount=field(&data,"regulator_mount")?;let fit=field(&mount,"cavity_fit")?;
            let path=rt.root_path().join("hardware/reference/yzmsz-water-regulator/reference-parameters.json");
            hsm_documents::interop::note_io(&path, false);
            let doc:Value=serde_json::from_slice(&std::fs::read(path)?)?;
            let profile=pairs(&value(doc["profile_x_radius_mm"].clone())?)?;
            let pose=external(&rt,"above_core",&["snapshot_pose"])?.call(vec!["reg".into()],vec![])?;
            let rotation=field(&pose,"rotation")?.iter()?.iter().map(row).collect::<Result<Vec<_>>>()?;
            let translation=row(&field(&pose,"translation_mm")?)?;
            let st=field(&mount,"station")?;
            let station=Val::dict(st.iter()?.iter().map(|key|Ok((key.clone(),st.get(key.clone())?))).collect::<Result<_>>()?);
            station.set("tool_angle_degrees".into(),75f64.into())?;
            station.set("tool_sides".into(),Val::tuple(vec![(-1f64).into()]))?;
            station.set("tool_inner_slope".into(),2f64.into())?;
            let half=f(&station,"inner")?-external(&rt,"rear_snaps",&["ROOT_RADIUS"])?.num()?-0.5;
            let out=Val::dict(mount.iter()?.iter().map(|key|Ok((key.clone(),mount.get(key.clone())?))).collect::<Result<_>>()?);
            out.set("station".into(),station.clone())?;
            out.set("profile_frame".into(),value(json!({"rotation":[rotation[1].clone(),rotation[0].iter().map(|v|-v).collect::<Vec<_>>(),rotation[2].clone()],"translation_mm":[translation[1],-translation[0],translation[2]]}))?)?;
            out.set("seat_profile".into(),value(json!(clearance(&profile,f(&fit,"receiver_radial_mm")?,f(&fit,"axial_mm")?,0.06)?))?)?;
            out.set("cap_profile".into(),value(json!(clearance(&profile,f(&fit,"cap_radial_mm")?,f(&fit,"axial_mm")?,0.06)?))?)?;
            out.set("cap_bearing_outlet_setback_mm".into(),1f64.into())?;
            out.set("cap_stock".into(),value(json!([[f(&station,"axis_x")?-half,f(&station,"axis_x")?+half,f(&station,"y0")?,f(&station,"y1")?-1.,f(&mount,"cap_bottom")?,row(&field(&mount,"axis")?)?[1]]]))?)?;
            Ok(out)
        }))?;
    }
    if module != "rear_snaps" {return Ok(());}
    e.set("clearance_profile",Val::function(|args,kw| {
        let points=pairs(arg(&args,&kw,0,"profile")?)?;
        value(json!(clearance(&points,number(&args,&kw,1,"radial",0.)?,number(&args,&kw,2,"axial",0.)?,number(&args,&kw,3,"tolerance",0.06)?)?))
    }))?;
    let depth=e.get("ASSE_BODY_SEATING_DEPTH")?.num()?;
    e.set("asse_cap_room",Val::function(move|args,kw| {
        let axis=row(arg(&args,&kw,0,"axis")?)?;let profile=arg(&args,&kw,1,"profile")?;let span=row(arg(&args,&kw,2,"span")?)?;
        let radius=f(profile,"apothem")?/(std::f64::consts::PI/6.).cos();let clock=f(profile,"clock")?;
        let points:Vec<[f64;2]>=(0..6).map(|i|{let a=(clock+60.*i as f64).to_radians();[axis[0]+radius*a.sin(),axis[1]-radius*a.cos()]}).collect();
        let normals:Vec<[f64;2]>=(0..6).map(|i|{let a=points[i];let b=points[(i+1)%6];let n=[b[1]-a[1],a[0]-b[0]];let d=n[0].hypot(n[1]);[n[0]/d,n[1]/d]}).collect();
        let bounds:Vec<_>=normals.iter().zip(&points).map(|(n,p)|n[0]*p[0]+n[1]*p[1]+depth*(-n[1]).max(0.)).collect();
        let points=(0..6).map(|i|solve(normals[(i+5)%6],normals[i],bounds[(i+5)%6],bounds[i])).collect::<Result<Vec<_>>>()?;
        value(section(&points,[span[0]-0.01,span[1]+0.01]))
    }))?;
    let rt2=rt.clone();let seating=e.get("ASSE_HEX_SEATING_DEPTH")?.num()?;let wall=e.get("WALL")?.num()?;
    e.set("asse_adapter_capture",Val::function(move|args,kw| {
        let chain_frame=arg(&args,&kw,0,"chain_frame")?;let station=arg(&args,&kw,1,"station")?;let axis=row(arg(&args,&kw,2,"axis")?)?;
        let chain=external(&rt2,"rear_plumbing",&["chain"])?.call(vec![],vec![])?;
        let record=chain.attr("parameters")?.call(vec![],vec![])?.get("gagira".into())?;
        let local=Val::dict(vec![("rotation".into(),field(&record,"rotation")?),("translation_mm".into(),field(&record,"origin_mm")?)]);
        let frame=external(&rt2,"above_core_parts",&["_compose"])?.call(vec![chain_frame.clone(),local],vec![])?;
        let rise=external(&rt2,"rear_plumbing",&["plan"])?.call(vec![],vec![])?.get("asse_adapter_rise_mm".into())?.num()?;
        let mut translation=row(&field(&frame,"translation_mm")?)?;translation[2]+=rise;
        let rotation=field(&frame,"rotation")?.iter()?.iter().map(row).collect::<Result<Vec<_>>>()?;
        let profile=pairs(&field(&record,"visible_profile")?)?;let wrench=field(&record,"wrench")?;
        let slip=external(&rt2,"fits",&["slip"])?.num()?;
        let apothem=f(&wrench,"apothem_at_x_zero_mm")?+slip;let clock=f(&wrench,"clock_degrees")?;
        let normals:Vec<[f64;2]>=(0..6).map(|i|{let a=(clock+30.+60.*i as f64).to_radians();[a.cos(),a.sin()]}).collect();
        let bounds:Vec<_>=normals.iter().map(|n|apothem+seating*(-n[0]*rotation[2][1]-n[1]*rotation[2][2]).max(0.)).collect();
        let outline=(0..6).map(|i|solve(normals[(i+5)%6],normals[i],bounds[(i+5)%6],bounds[i])).collect::<Result<Vec<_>>>()?;
        let range=row(&field(&wrench,"range_mm")?)?;
        let cutter=json!({"op":"radial-profile","points":clearance(&profile,slip,slip,0.06)?,"frame":{"rotation":rotation,"translation_mm":translation},"wrench":{"apothem":apothem,"clock":clock,"outline":outline,"relief_span":[range[0]-slip,range[1]+slip],"relief_corner":profile.iter().map(|p|p[1]).fold(f64::NEG_INFINITY,f64::max)+slip+seating}});
        let width=f(station,"outer")?;let low=axis[1]-width*3f64.sqrt()/2.;
        let outline=[[axis[0]-width,axis[1]],[axis[0]+width,axis[1]],[axis[0]+width/2.,low],[axis[0]-width/2.,low]];
        let mut stock=section(&outline,[f(station,"y1")?-wall,translation[1]+13.825+wall]);stock["op"]=json!("section");
        value(json!({"$tuple":[stock,cutter]}))
    }))?;
    let rt2=rt.clone();let fit=e.get("PISCO_CAP_FIT")?.num()?;
    e.set("pisco_cap_fit",Val::function(move|args,kw| {
        let profile=pairs(arg(&args,&kw,0,"profile")?)?;let mouth=arg(&args,&kw,1,"mouth_y")?.num()?;
        let span=row(arg(&args,&kw,2,"cap_y")?)?;let axis=row(arg(&args,&kw,3,"axis")?)?;let neck=arg(&args,&kw,4,"neck_z")?.num()?;
        let slip=external(&rt2,"fits",&["slip"])?.num()?;let axial=external(&rt2,"fits",&["running"])?.num()?;
        let lip=mouth-neck-slip;
        let body=clearance(&profile.iter().copied().filter(|p|p[0]<=neck).collect::<Vec<_>>(),fit,axial,0.06)?;
        let outlet=clearance(&profile.iter().copied().filter(|p|p[0]>=neck).collect::<Vec<_>>(),fit,axial,0.06)?;
        let clipped=|points:&[[f64;2]],a:f64,b:f64|{let mut out=vec![[a,interpolate(points,a)]];out.extend(points.iter().copied().filter(|p|p[0]>a&&p[0]<b));out.push([b,interpolate(points,b)]);out};
        value(json!({"lip_y":lip,"body":clipped(&body,mouth-span[1]-1.,mouth-lip),"neck":clipped(&outlet,mouth-lip,mouth-span[0]+1.),"frame":{"rotation":[[0.,1.,0.],[-1.,0.,0.],[0.,0.,1.]],"translation_mm":[axis[0],mouth,axis[1]]}}))
    }))?;
    Ok(())
}
