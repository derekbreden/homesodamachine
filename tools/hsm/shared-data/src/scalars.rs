//! Shared fits, profile fields, clipping datums and coordinate-frame scalars.
use anyhow::{Context,Result,bail,ensure};
use hsm_shared_data::common::*;
use serde_json::{Value,json};
use std::f64::consts::PI;

fn constants()->Value{
    let mut v:Value=serde_json::from_str(include_str!("../catalog/scalars.json")).unwrap();
    v["fits"]["running"]=json!(v["fits"]["slip"].as_f64().unwrap()+v["fits"]["sliding_extra"].as_f64().unwrap());
    let grid=v["cable_clip"]["GRID"].as_f64().unwrap();
    for(name,factor)in[("DEPTH",3.),("BACKING",1.),("HEIGHT",13.),("RUN",6.),("RAMP",2.)]{v["cable_clip"][name]=json!(grid*factor);}
    v["snap"]["channel_width"]=json!(v["snap"]["wall_thickness"].as_f64().unwrap()+v["snap"]["ramp_out_outer_growth"].as_f64().unwrap());
    v["reeding"]["_ROOT2"]=json!(2_f64.sqrt());v["boxes"]=json!({"KEEP_BYTES":1<<24});v["clearing"]=json!({"HIT_VOL":1.});v
}
#[derive(Clone)]struct Tensor{shape:Vec<usize>,data:Vec<f64>}
impl Tensor{
    fn read(v:&Value)->Result<Self>{
        if let Some(rows)=v.as_array(){if rows.is_empty(){return Ok(Self{shape:vec![0],data:vec![]})}let values=rows.iter().map(Self::read).collect::<Result<Vec<_>>>()?;ensure!(values.iter().all(|v|v.shape==values[0].shape),"ragged field array");let mut shape=vec![rows.len()];shape.extend_from_slice(&values[0].shape);Ok(Self{shape,data:values.into_iter().flat_map(|v|v.data).collect()})}
        else{Ok(Self{shape:vec![],data:vec![number(v)?]})}
    }
    fn value(&self,index:&[usize],rank:usize)->f64{
        let mut offset=0;for(axis,size)in self.shape.iter().enumerate(){offset=offset*size+if *size==1{0}else{index[rank-self.shape.len()+axis]};}self.data[offset]
    }
}
fn field(a:&Value,b:&Value,f:impl Fn(f64,f64)->Value)->Result<Value>{
    let a=Tensor::read(a)?;let b=Tensor::read(b)?;let rank=a.shape.len().max(b.shape.len());let mut shape=vec![1;rank];
    for t in [&a,&b]{for(i,n)in t.shape.iter().enumerate(){let at=rank-t.shape.len()+i;ensure!(shape[at]==1||*n==1||shape[at]==*n,"field arrays do not broadcast");if shape[at]==1{shape[at]=*n;}}}
    fn nested(a:&Tensor,b:&Tensor,shape:&[usize],index:&mut Vec<usize>,f:&dyn Fn(f64,f64)->Value)->Value{if index.len()==shape.len(){return f(a.value(index,shape.len()),b.value(index,shape.len()))}let axis=index.len();json!((0..shape[axis]).map(|i|{index.push(i);let v=nested(a,b,shape,index,f);index.pop();v}).collect::<Vec<_>>())}
    Ok(nested(&a,&b,&shape,&mut vec![],&f))
}
fn groove(across:f64,pitch:f64,width:f64)->f64{let offset=(across+pitch/2.).rem_euclid(pitch)-pitch/2.;(1.-(offset/(width/2.)).powi(2)).max(0.).sqrt()}
fn rectangle(x:f64,y:f64,r:f64)->Value{
    let(rx,ry,turn)=(x-2.*r,y-2.*r,PI*r/2.);let(x0,x1,y0,y1)=(-x/2.,x/2.,-y/2.,y/2.);
    json!([
        ["line",ry/2.,[[x0,0.],[0.,-1.],[-1.,0.]]],["arc",turn,[[x0+r,y0+r],PI,r]],
        ["line",rx,[[x0+r,y0],[1.,0.],[0.,-1.]]],["arc",turn,[[x1-r,y0+r],-PI/2.,r]],
        ["line",ry,[[x1,y0+r],[0.,1.],[1.,0.]]],["arc",turn,[[x1-r,y1-r],0.,r]],
        ["line",rx,[[x1-r,y1],[-1.,0.],[0.,1.]]],["arc",turn,[[x0+r,y1-r],PI/2.,r]],
        ["line",ry/2.,[[x0,y1-r],[0.,-1.],[-1.,0.]]]
    ])
}
fn walk(segments:&Value,mut s:f64)->Result<Value>{
    let total=array(segments).iter().map(|v|number(&v[1])).collect::<Result<Vec<_>>>()?.iter().sum::<f64>();ensure!(s>=-1e-9&&s<=total+1e-9,"AssertionError: arc length walked off the end of a run");s=s.clamp(0.,total);
    for segment in array(segments){let length=number(&segment[1])?;let data=&segment[2];if s<=length+1e-9{
        if text(&segment[0])=="line"{return Ok(json!([[number(&data[0][0])?+number(&data[1][0])?*s,number(&data[0][1])?+number(&data[1][1])?*s],data[2]]))}
        let angle=number(&data[1])?+s/number(&data[2])?;let(nx,ny)=(angle.cos(),angle.sin());return Ok(json!([[number(&data[0][0])?+number(&data[2])?*nx,number(&data[0][1])?+number(&data[2])?*ny],[nx,ny]]))
    }s-=length;}bail!("AssertionError: arc length walked off the end of a run")
}
pub fn dispatch(op:&str,r:&Value)->Result<Value>{
    let c=constants();let cfg=if r["config"].is_object(){&r["config"]}else{&c["reeding"]};let n=|key:&str,default:f64|r[key].as_f64().unwrap_or(default);
    Ok(match op{
        "constants"=>if let Some(group)=r["group"].as_str(){c[group].clone()}else{c.clone()},
        "clearance"=>{let fits=&c["fits"];json!(number(&fits["slip"])?+if r["sliding"].as_bool().unwrap_or(false){number(&fits["sliding_extra"])?}else{0.}+if r["supported"].as_bool().unwrap_or(false){number(&fits["supported_surface"])?}else{0.}+if r["at_floor"].as_bool().unwrap_or(false){number(&fits["layer_transition"])?}else{0.})},
        "verdict"=>json!(if r["ok"].as_bool().unwrap_or(false){"pass"}else{"fail"}),
        "grade"=>{let ratio=number(&r["ratio"])?;let bands=r.get("bands").unwrap_or(&c["card"]["GRADE_BANDS"]);array(bands).iter().find(|v|number(&v[0]).unwrap_or(f64::INFINITY)<=ratio).map(|v|v[1].clone()).context("StopIteration: ratio has no grade band")?},
        "clip_projection"=>json!(number(&c["cable_clip"]["DEPTH"])?-number(&r["embed"])?),"clip_required_wall"=>json!(number(&r["embed"])?+number(&c["cable_clip"]["BACKING"])?),
        "clip_seat_top"=>json!(number(&c["cable_clip"]["_LOWER"][6][1])?*number(&c["cable_clip"]["GRID"])?),
        "clip_seat_height"=>json!((number(&c["cable_clip"]["_LOWER"][6][1])?-number(&c["cable_clip"]["_LOWER"][7][1])?)*number(&c["cable_clip"]["GRID"])?),
        "clip_channel_mouth"=>json!(number(&c["cable_clip"]["_UPPER"][0][1])?*number(&c["cable_clip"]["GRID"])?),
        "clip_scaled"=>json!(array(&r["points"]).iter().map(|p|Ok(json!([number(&p[0])?*number(&c["cable_clip"]["GRID"])?+n("x_shift",0.),number(&p[1])?*number(&c["cable_clip"]["GRID"])?]))).collect::<Result<Vec<_>>>()?),
        "clip_unit"|"unit"=>{let v=point(&r["vector"])?;let length=v.norm();ensure!(length>if op=="clip_unit"{1e-9}else{1e-12},"direction has no length");row(v/length)},
        "transition"=>{let radius=number(&r["radius"])?;let slope=number(&c["overhang_round"]["OUTWARD_PER_HEIGHT"])?;let height=radius-radius*slope/(1.+slope*slope).sqrt();let inset=radius-radius/(1.+slope*slope).sqrt();json!([height,inset+slope*height])},
        "flip"=>json!([r["point"][0],-number(&r["point"][1])?]),"negate"=>json!(-number(&r["value"])?),
        "snap_frame"=>json!({"extrusion_plane":r["extrusion_plane"],"outward_sign":r["outward_sign"],"up_axis":r["up_axis"],"up_sign":r["up_sign"],"up_first":text(&r["extrusion_plane"]).chars().next()==text(&r["up_axis"]).chars().next()}),
        "cable_origin"=>{let centre=point(&r["centre"])?;let normal=point(&r["outward"])?.unit();let up=point(&r["profile_up"])?.unit();let depth=n("seat_depth",2.20);let height=n("seat_height",7.75);let stock=n("stock",3.);row(centre-normal*(depth/2.)-up*(depth+2.*stock+height/2.))},
        "box_gap"=>{let a=&r["a"];let b=&r["b"];let mut sum=0.;for axis in ["x","y","z"]{let min=format!("{axis}min");let max=format!("{axis}max");let gap=0_f64.max(number(&a[&min])?-number(&b[&max])?).max(number(&b[&min])?-number(&a[&max])?);sum+=gap*gap;}json!(sum.sqrt())},
        "axis_min"=>{let origin=point(&r["origin"])?;let axis=point(&r["axis"])?;ensure!(axis.norm()>=1e-12,"direction has no length");let axis=axis.unit();json!(points(&r["vertices"])?.iter().map(|v|(*v-origin).dot(axis)).reduce(f64::min).context("empty shape")?)},
        "transform"=>{let v=point(&r["vector"])?;let point=text(&r["kind"])=="point";json!((0..3).map(|i|{let row=&r["matrix"][i];Ok(number(&row[0])?*v.x+number(&row[1])?*v.y+number(&row[2])?*v.z+if point{number(&row[3])?}else{0.})}).collect::<Result<Vec<f64>>>()?)},
        "rounded_rect_segments"=>rectangle(number(&r["x_length"])?,number(&r["y_length"])?,number(&r["radius"])?),"walk"=>walk(&r["segments"],number(&r["distance"])?)?,
        "rail_stations"=>{let length=number(&r["length"])?;let start=n("start",0.);let step_count=(length/n("grid",number(&c["flute_skin"]["grid_across"])?)).round_ties_even().max(3.)as usize;let step=length/step_count as f64;let closed=r["closed"].as_bool().unwrap_or(true);json!((0..step_count+usize::from(!closed)).map(|i|start+if !closed&&i==step_count{length}else{i as f64*step}).collect::<Vec<_>>())},
        "limb_angle"|"chevron_limb"|"wave_limb"=>{let sharp=number(&cfg["chevron_sharpness"])?;let factor=if op=="chevron_limb"{sharp/sharp.asin()}else if op=="wave_limb"{1.}else{number(&r["slope_factor"])?};json!((factor*2.*PI*number(&cfg["warp_amplitude"])?/number(&cfg["warp_wavelength"])?).atan().to_degrees())},
        "mullion"=>json!(n("every",1.)*n("pitch",5.)-n("slot",3.1)),"pierce_max"=>json!(n("every",1.)*n("pitch",5.)-n("shell",1.74)),"open_fraction"=>json!(n("slot",3.1)/(n("every",1.)*n("pitch",5.))),
        "groove"|"straight"|"chevron"|"wave"|"cross"|"pierce"|"phase"|"rounded_triangle"=>{
            let pitch=n("pitch",if op=="cross"{6.}else{5.});let width=n("width",if op=="cross"{3.4}else{4.});let wavelength=number(&cfg["warp_wavelength"])?;let amplitude=number(&cfg["warp_amplitude"])?;let sharp=number(&cfg["chevron_sharpness"])?;
            let across=r.get("across").unwrap_or(&Value::Null);let along=r.get("along").unwrap_or(&json!(0.)).clone();let a=if across.is_null(){&along}else{across};
            field(a,&along,|x,y|{let phase=2.*PI*y/wavelength;let triangle=(sharp*phase.sin()).asin()/sharp.asin();match op{
                "phase"=>json!(2.*PI*x/wavelength),"rounded_triangle"=>json!((sharp*(2.*PI*x/wavelength).sin()).asin()/sharp.asin()),
                "chevron"=>json!(groove(x+amplitude*triangle,pitch,width)),"wave"=>json!(groove(x+amplitude*phase.sin(),pitch,width)),
                "cross"=>json!(groove((x+y)/2_f64.sqrt(),pitch,width).max(groove((x-y)/2_f64.sqrt(),pitch,width))),
                "pierce"=>{let offset=(x+pitch/2.).rem_euclid(pitch)-pitch/2.;let index=(x/pitch).round_ties_even()-(n("datum",0.)/pitch).round_ties_even();json!(offset.abs()<=n("slot",3.1)/2.&&index.rem_euclid(n("every",1.))==0.)},
                _=>json!(groove(x,pitch,width))
            }})?
        },
        _=>bail!("unknown shared scalar operation {op}")
    })
}
