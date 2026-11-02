//! Two-body tooling for the authored silicone funnel, in the existing mold frame.
#[path="../funnel/funnel_geometry.rs"]
mod funnel_geometry;
use anyhow::{Context,Result,ensure};
use hsm_kernel::{Body,Solid,V3,v3};
use hsm_kernel::part::{Numbers,args,AssemblyBody,write_assembly};
use hsm_kernel::write::PrintOutput;
use sha2::{Digest,Sha256};
use serde_json::{json,Value};
use std::path::Path;

fn block(w:f64,d:f64,z0:f64,z1:f64,x:f64,y:f64)->Solid {
    Solid::cuboid(v3(x-w/2.0,y-d/2.0,z0),v3(x+w/2.0,y+d/2.0,z1))
}
fn cylinder(r:f64,z0:f64,z1:f64,x:f64,y:f64)->Result<Solid> {
    Solid::cylinder(v3(x,y,z0),V3::Z,r,z1-z0)
}
fn round(w:f64,d:f64,r:f64,z0:f64,z1:f64)->Result<Solid> {
    funnel_geometry::prism(w,d,r,r,z0,z1,0.0,0.0)
}
fn rows(n:&Numbers,key:&str)->Result<Vec<(f64,f64)>> {
    n.get(key)?.as_array().context("XY positions are a list")?.iter().map(|v|
        Ok((v[0].as_f64().context("X is numeric")?,v[1].as_f64().context("Y is numeric")?))).collect()
}
struct Parts {cavity:Solid,core:Solid,funnel:Solid,rod:Solid}
fn build(n:&Numbers)->Result<Parts> {
    let funnel=funnel_geometry::Dimensions::from_numbers(n)?;
    let(exterior,bore)=funnel_geometry::build_solids(&funnel,0.0,true,true)?;
    let finish=n.f("finish_allowance")?;
    let(forming,_)=funnel_geometry::build_solids(&funnel,finish,true,true)?;
    let(x,y)=funnel.drain_xy;
    let top=n.f("top_z")?;let end=n.f("end_z")?;let(_,neck)=n.pair("ramp_z")?;
    let floor=n.f("floor_z")?;let back=n.f("back_z")?;let(w,d)=n.pair("flange_size")?;
    let base=n.list("base_size")?;let(z0,z1)=n.pair("corbel_z")?;let r=n.f("flange_radius")?;
    let blank=round(base[0],base[1],n.f("base_radius")?,floor,z0)?
        .union(&funnel_geometry::corbel(base[0],base[1],n.f("base_radius")?,z0,w,d,r,z1)?)?
        .union(&round(w,d,r,top-n.f("flange_thickness")?,top)?)?;
    let cavity=blank.cut(&forming)?.cut(&cylinder(n.f("rod_socket_diameter")?/2.0,end-n.f("rod_socket_depth")?,end,x,y)?)?;

    let plug=funnel_geometry::wet(&funnel,back+1.0,-finish)?;
    let guide=n.f("rod_diameter")?/2.0+n.f("rod_clearance")?/2.0;
    let guide_top=neck+n.f("rod_guide_length")?;
    let slope=n.f("corbel_run_per_rise")?;let dry=guide+(back-guide_top)*slope;
    let dry_void=Solid::cone(v3(x,y,guide_top),V3::Z,guide,dry+slope,back+1.0-guide_top)?;
    let(aw,ad)=n.pair("apron_size")?;let ar=n.f("apron_radius")?+finish;
    let apron=funnel_geometry::prism(aw+2.0*finish,ad+2.0*finish,ar,ar,top-1.0,top+finish,0.0,n.f("apron_y")?)?;
    let plate=round(w,d,r,top,back)?.cut(&apron)?;
    let rod_bottom=end-n.f("rod_end_depth")?;let rod_top=rod_bottom+n.f("rod_length")?;
    let rod=cylinder(n.f("rod_diameter")?/2.0,rod_bottom,rod_top,x,y)?;
    let seat=cylinder(guide,neck-1.0,back+1.0,x,y)?;
    let core=plug.union(&plate)?.cut_all(&[dry_void,seat])?.intersect(&block(w+2.0,d+2.0,neck,back,0.0,0.0))?;

    let mut pegs=vec![];let mut holes=vec![];
    let lead=n.f("locator_leadin")?;let height=n.f("locator_height")?;let radius=n.f("locator_diameter")?/2.0;
    for(index,(x,y))in rows(n,"locator_xy")?.into_iter().enumerate() {
        pegs.push(cylinder(radius,top-1.0,top+height-lead,x,y)?.union(
            &Solid::cone(v3(x,y,top+height-lead),V3::Z,radius,radius-lead,lead)?)?);
        let radius=radius+n.f("locator_clearance")?;
        let hole=cylinder(radius,top-1.0,back+1.0,x,y)?;
        let entry=Solid::cone(v3(x,y,top),V3::Z,radius+lead,radius,lead)?;
        holes.push(if index==0 {hole.union(&entry)?} else {
            let travel=n.f("locator_slot_travel")?;
            Solid::union_all(&[hole.clone(),hole.translate(v3(travel,0.0,0.0)),hole.translate(v3(-travel,0.0,0.0)),
                block(2.0*travel,2.0*radius,top-1.0,back+1.0,x,y),entry.clone(),entry.translate(v3(travel,0.0,0.0)),entry.translate(v3(-travel,0.0,0.0))])?
        });
    }
    let cavity=cavity.union(&Solid::union_all(&pegs)?)?;let core=core.cut_all(&holes)?;
    let bolts=rows(n,"bolt_xy")?;let(bx,by)=n.pair("bolt_limits")?;
    let mut pockets=vec![];let mut passages=vec![];
    for(x,y)in bolts {
        passages.push(cylinder(n.f("bolt_diameter")?/2.0,floor-1.0,back+1.0,x,y)?);
        let side=if x.abs()==bx {x.signum()} else {y.signum()};
        if x.abs()==bx {
            let(inner,outer)=(bx-4.6,w/2.0+1.0);
            pockets.push(block(outer-inner,n.f("bolt_pocket_width")?,floor-1.0,z1,side*(inner+outer)/2.0,y));
        } else {
            let(inner,outer)=(by-4.6,d/2.0+1.0);
            pockets.push(block(n.f("bolt_pocket_width")?,outer-inner,floor-1.0,z1,x,side*(inner+outer)/2.0));
        }
    }
    let cavity=cavity.cut_all(&pockets)?.cut_all(&passages)?;
    let mut ports=vec![];let(pourx,poury)=n.pair("pour_xy")?;
    ports.push(cylinder(n.f("pour_diameter")?/2.0,top-1.0,back+1.0,pourx,poury)?);
    for(x,y)in rows(n,"vent_xy")? {ports.push(cylinder(n.f("vent_diameter")?/2.0,top-1.0,back+1.0,x,y)?);}
    let core=core.cut_all(&passages)?.cut_all(&ports)?;
    let mut notches=vec![];
    for(angle,reach)in[(0.0,w/2.0),(90.0,d/2.0),(180.0,w/2.0),(270.0,d/2.0)] {
        notches.push(block(n.f("pry_depth")?+1.0,n.f("pry_width")?,top-n.f("pry_height")?,top+1.0,reach-n.f("pry_depth")?/2.0+0.5,0.0)
            .rotate(V3::ZERO,V3::Z,angle));
    }
    let cavity=cavity.cut_all(&notches)?;let cast=exterior.cut(&bore)?;
    let shift=v3(0.0,0.0,-floor);
    Ok(Parts{cavity:cavity.translate(shift),core:core.translate(shift),funnel:cast.translate(shift),rod:rod.translate(shift)})
}
fn body<'a>(n:&Numbers,name:&'a str,solid:&'a Solid)->Result<Body<'a>> {
    Ok(Body{name,color:Some(n.color(&format!("{name}_color"))?),solid})
}
fn shown(n:&Numbers,out:&Path,name:&str,bodies:&[Body])->Result<Value> {
    let views=bodies.iter().map(|b|{let size=b.solid.bounds().size();
        b.solid.simplified_to((size.x+size.y+size.z)/3.0*n.f("viewer_deflection_ratio")?)
    }).collect::<Result<Vec<_>>>()?;
    let parts=bodies.iter().zip(&views).map(|(b,p)|AssemblyBody{name:b.name,color:b.color,fine:b.solid,presentation:p}).collect::<Vec<_>>();
    write_assembly(out,name,&parts,Some(&json!({})))
}
fn keep(path:&Path,bytes:&[u8])->Result<()> {
    if std::fs::read(path).ok().as_deref()==Some(bytes) {return Ok(());}
    let temporary=path.with_extension(format!("{}.tmp",std::process::id()));
    std::fs::write(&temporary,bytes)?;std::fs::rename(temporary,path)?;Ok(())
}

fn printed(n:&Numbers,out:&Path,name:&str,fine:&Solid,print:&Solid)->Result<Value> {
    let color=Some(n.color(&format!("{name}_color"))?);let size=fine.bounds().size();
    let tolerance=(size.x+size.y+size.z)/3.0*n.f("viewer_deflection_ratio")?;
    let view=fine.simplified_to(tolerance)?;let shown=[Body{name,color,solid:&view}];
    let step=hsm_kernel::step::step_bytes(&shown,name)?;let digest=format!("{:x}",Sha256::digest(&step));
    let payload=hsm_kernel::write::payload_bytes_with_sources(&shown,Some(&digest),None);
    let payload_name=format!("{name}.step.mesh");let stl_name=format!("{name}.stl");
    let document=json!({"presentation":{"path":payload_name,"sha256":format!("{:x}",Sha256::digest(&payload)),"tolerance_mm":tolerance}});
    let output=PrintOutput::new(&[Body{name,color,solid:print}]);
    let model=output.model_bytes(&[Body{name,color,solid:fine}],&stl_name,Some(&document))?;
    for(file,bytes)in[(format!("{name}.step"),step.as_slice()),(format!("{name}.step.npz"),model.as_slice()),(payload_name,payload.as_slice()),(stl_name,output.stl_bytes())] {keep(&out.join(file),bytes)?;}
    Ok(json!({"files":[format!("{name}.step"),format!("{name}.step.npz"),format!("{name}.step.mesh"),format!("{name}.stl")],
        "bodies":[{"name":name,"volume":fine.volume(),"area":fine.area(),"min":fine.bounds().min.to_array(),"max":fine.bounds().max.to_array(),"triangles":fine.tris().len(),"presentation_triangles":view.tris().len(),"print_triangles":(output.stl_bytes().len()-84)/50}]}))
}
fn emit(n:&Numbers,p:&Parts,out:&Path,checks:&Value)->Result<()> {
    for(name,s)in[("cavity",&p.cavity),("core",&p.core),("funnel",&p.funnel),("rod",&p.rod)] {
        let b=body(n,name,s)?;
        let mut said=match name {"cavity"=>printed(n,out,name,s,&funnel_geometry::fabrication_copy(s,"FUNNEL cavity fabrication copy")?)?,"core"=>printed(n,out,name,s,&s.simplified()?)?,_=>shown(n,out,name,&[b])?};
        if name=="cavity" {said["bodies"][0]["checks"]=checks.clone();}
        println!("{said}");
    }
    let bodies=[body(n,"cavity",&p.cavity)?,body(n,"core",&p.core)?,body(n,"funnel",&p.funnel)?,body(n,"rod",&p.rod)?];
    println!("{}",shown(n,out,"assembly",&bodies)?);
    let spacing=(p.cavity.bounds().size().x+p.core.bounds().size().x)/4.0+22.0;
    let left=p.cavity.translate(v3(-spacing,0.0,0.0));
    let right=p.core.rotate(V3::ZERO,V3::X,180.0);let right=right.translate(v3(spacing,0.0,-right.bounds().min.z));
    println!("{}",shown(n,out,"overview",&[body(n,"cavity",&left)?,body(n,"core",&right)?])?);
    let cavity=p.cavity.rotate(V3::ZERO,V3::X,180.0);let cavity=cavity.translate(v3(-spacing,0.0,-cavity.bounds().min.z));
    let core=p.core.translate(v3(spacing,0.0,-p.core.bounds().min.z));
    println!("{}",shown(n,out,"backs",&[body(n,"cavity",&cavity)?,body(n,"core",&core)?])?);
    let slab=block(240.0,2.0,-1.0,120.0,0.0,n.pair("drain_xy")?.1);
    let sections=[p.cavity.intersect(&slab)?,p.core.intersect(&slab)?,p.funnel.intersect(&slab)?,p.rod.intersect(&slab)?];
    println!("{}",shown(n,out,"section",&[body(n,"cavity",&sections[0])?,body(n,"core",&sections[1])?,body(n,"funnel",&sections[2])?,body(n,"rod",&sections[3])?])?);
    Ok(())
}
fn measured(name:&str,s:&Solid)->Result<hsm_geometry::payload::Mesh> {
    hsm_geometry::payload::Mesh::from_arrays(name,s.verts().iter().map(|p|p.to_array()).collect(),s.tris().to_vec())
}
fn containment(n:&Numbers,p:&Parts)->Result<Value> {
    let(drain_x,drain_y)=n.pair("drain_xy")?;
    let shift=-n.f("floor_z")?;let top=n.f("top_z")?+shift;let back=n.f("back_z")?+shift;
    let(w,_)=n.pair("flange_size")?;let(_,neck)=n.pair("ramp_z")?;let guide=neck+n.f("rod_guide_length")?+shift;
    let marker=|x:f64,y:f64,z:f64|block(0.001,0.001,z-0.0005,z+0.0005,x,y);
    let witness=marker(drain_x+n.f("rod_diameter")?,drain_y,p.rod.bounds().min.z+n.f("rod_socket_depth")?);
    let outside=marker(-(w+26.0)/2.0+1.0,0.0,0.0);
    let surrounding=block(w+26.0,w+26.0,-2.0,back+8.0,0.0,0.0);
    let mouth=block(w+2.0,w+2.0,top-0.02,back+2.0,0.0,0.0);
    let mut caps=vec![];let(x,y)=n.pair("pour_xy")?;
    caps.push(cylinder(n.f("pour_diameter")?/2.0+0.02,back-0.02,back+1.0,x,y)?);
    for(x,y)in rows(n,"vent_xy")? {caps.push(cylinder(n.f("vent_diameter")?/2.0+0.02,back-0.02,back+1.0,x,y)?);}
    caps.push(cylinder((n.f("rod_diameter")?+n.f("rod_clearance")?)/2.0+0.02,guide-0.02,guide+1.0,drain_x,drain_y)?);
    let sets=[("cavity",vec![p.cavity.clone(),mouth]),("assembled",{
        let mut tools=vec![p.cavity.clone(),p.core.clone(),p.rod.clone()];tools.extend(caps);tools})];
    let mut result=json!({});
    for(name,tools)in sets {
        let complement=surrounding.cut_all(&tools)?;
        let mut retained=vec![];
        for component in complement.components() {
            if component.shared_volume(&witness)?>1e-12 && component.shared_volume(&outside)?<1e-12 {retained.push(component);}
        }
        ensure!(retained.len()==1,"{name}: the liquid space reaches the outside");
        let missing=p.funnel.cut_all(&tools)?.cut(&retained[0])?.volume();
        ensure!(missing<n.f("tolerance")?,"{name}: casting outside retained liquid {missing}");
        result[name]=json!({"retained_volume_ml":retained[0].volume()/1000.0,"casting_outside_retained_mm3":missing});
    }
    Ok(result)
}
fn checks(n:&Numbers,p:&Parts)->Result<Value> {
    let funnel=funnel_geometry::Dimensions::from_numbers(n)?;
    let(x,y)=funnel.drain_xy;
    let tolerance=n.f("tolerance")?;let(_,neck)=n.pair("ramp_z")?;let end=n.f("end_z")?;
    let rod_engagement=end-n.f("rod_end_depth")?+n.f("rod_length")?-neck;
    let mut overlap:f64=0.0;
    for(a,b)in[(&p.cavity,&p.core),(&p.cavity,&p.funnel),(&p.core,&p.funnel),(&p.cavity,&p.rod),(&p.core,&p.rod)] {
        overlap=overlap.max(a.shared_volume(b)?);
    }
    for lift in [0.5,1.5,3.0,6.0,12.0,rod_engagement,52.0] {overlap=overlap.max(p.cavity.shared_volume(&p.core.translate(v3(0.0,0.0,lift)))?);}
    for withdrawal in [0.0,0.5,1.0,2.0,4.0,8.0,n.f("rod_length")?] {overlap=overlap.max(p.core.shared_volume(&p.rod.translate(v3(0.0,0.0,-withdrawal)))?);}
    let shift=-n.f("floor_z")?;let top=n.f("top_z")?;let back=n.f("back_z")?;
    for(x,y)in rows(n,"bolt_xy")? {
        let washer=cylinder(4.5,top-n.f("flange_thickness")?-1.0+shift,top-n.f("flange_thickness")?+shift,x,y)?;
        overlap=overlap.max(p.cavity.shared_volume(&washer)?);
    }
    ensure!(overlap<tolerance,"tooling, release path or washer overlap {overlap}");
    let cavity_backing=n.f("shell_thickness")?+n.f("forming_join_allowance")?;
    let guide=(n.f("rod_diameter")?+n.f("rod_clearance")?)/2.0;let guide_top=neck+n.f("rod_guide_length")?;
    let slope=n.f("corbel_run_per_rise")?;let dry=guide+(back-guide_top)*slope;
    let dry_void=Solid::cone(v3(x,y,guide_top+shift),V3::Z,guide,dry+slope,back+1.0-guide_top)?;
    let core_backing=hsm_geometry::queries::gap(&measured("dry access",&dry_void)?,&measured("cast",&p.funnel)?,[0.0;3])?.surface_distance_mm-n.f("finish_allowance")?;
    Ok(json!({"maximum_overlap_mm3":overlap,"minimum_cavity_backing_mm":cavity_backing,"cavity_backing_scope":"Analytic continuous-envelope design minimum: shell thickness plus forming-join allowance","minimum_core_backing_mm":core_backing,"liquid_containment":containment(n,p)?}))
}
fn main()->Result<()> {
    let(n,out)=args()?;std::fs::create_dir_all(&out)?;let p=build(&n)?;
    for s in [&p.cavity,&p.core,&p.funnel,&p.rod] {s.check()?;ensure!(s.components().len()==1,"each tooling child is one closed body");}
    let facts=checks(&n,&p)?;emit(&n,&p,&out,&facts)
}
