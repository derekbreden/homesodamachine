//! Manual installation illustrations combine the current appliance meshes with owner-action props.
use anyhow::{Context, Result};
use hsm_kernel::{scene, *, text::{Font, HAlign, VAlign}};
use serde_json::{Value, json};
use std::{fs, path::Path};

const SOURCE: &str = "hardware/manifold-layout/enclosure-assembly.step.mesh";

struct Prop { name: String, solid: Solid, color: [f64; 3] }
fn prop(name: &str, solid: Solid, color: [f64; 3]) -> Prop {
    Prop { name: name.into(), solid, color }
}
fn visible(name: &str) -> bool {
    name.starts_with("enclosure-front-") || name.starts_with("enclosure-back-")
        || ["nameplate", "display", "status-plate", "rear-label", "bulkhead", "funnel"]
            .iter().any(|prefix| name.starts_with(prefix))
        || matches!(name, "co2-inlet" | "keystone-jack" | "c14-inlet")
}
fn select(source: &Value, keep: impl Fn(&str) -> bool) -> Value {
    let mut head = source.clone();
    head["meshes"] = json!(source["meshes"].as_array().unwrap().iter()
        .filter(|node| keep(node["name"].as_str().unwrap())).collect::<Vec<_>>());
    head
}
fn bounds(source: &Value, name: &str) -> Result<[f64; 6]> {
    let head = select(source, |n| n == name);
    let bytes=scene::flatten(&scene::encode(&head,&[])?)?;
    let (head,start)=scene::header(&bytes)?;
    let mut lo = [f64::INFINITY; 3]; let mut hi = [f64::NEG_INFINITY; 3];
    for body in head["meshes"].as_array().unwrap() {
        let at=start+body["pos"][0].as_u64().unwrap() as usize;
        let count=body["pos"][1].as_u64().unwrap() as usize;
        for (i,word) in bytes[at..at+count*4].chunks_exact(4).enumerate() {
            let value=f32::from_le_bytes(word.try_into().unwrap()) as f64;
            let axis=i%3;lo[axis]=lo[axis].min(value);hi[axis]=hi[axis].max(value);
        }
    }
    anyhow::ensure!(lo[0].is_finite(), "the current machine has no {name}");
    Ok([lo[0],lo[1],lo[2],hi[0],hi[1],hi[2]])
}
fn tube(name: &str, points: &[V3], diameter: f64, color: [f64;3]) -> Result<Vec<Prop>> {
    let mut out=vec![];
    for (i,p) in points.windows(2).enumerate() {
        let d=p[1]-p[0];
        out.push(prop(&format!("{name}/{i}"), Solid::cylinder(p[0],d.unit(),diameter/2.,d.norm())?,color));
    }
    for (i,p) in points[1..points.len()-1].iter().enumerate() {
        out.push(prop(&format!("{name}-bend/{i}"),Solid::sphere(*p,diameter/2.)?,color));
    }
    Ok(out)
}
fn props_scene(out: &Path, name: &str, props: &[Prop]) -> Result<Value> {
    let path=out.join(format!("{name}-props.mesh"));
    let bodies=props.iter().map(|p|Body{name:&p.name,solid:&p.solid,color:Some(p.color)}).collect::<Vec<_>>();
    write_payload(&path,&bodies,None,None)?;
    scene::pack(&fs::read(&path)?)
}
fn write_scene(out: &Path, name: &str, head: &Value, props: &[Prop]) -> Result<String> {
    let mut head=head.clone();
    if !props.is_empty() {
        let extra=props_scene(out,name,props)?;
        head["meshes"].as_array_mut().unwrap().extend(extra["meshes"].as_array().unwrap().iter().cloned());
    }
    let path=out.join(format!("{name}.mesh"));
    scene::keep(&path,&scene::encode(&head,&[])?)?;
    Ok(path.to_string_lossy().into_owned())
}
fn bottle(mouth: V3) -> Result<Vec<Prop>> {
    let axis=v3(0.,-20_f64.to_radians().cos(),20_f64.to_radians().sin());
    let plane=Plane::new(mouth,V3::X,axis)?;
    let section=|height,radius|Profile::circle(V2::ZERO,radius).place(&plane.offset(height));
    let outer=Solid::loft(&[section(0.,13.),section(20.,13.),section(47.,35.),section(150.,35.),section(163.,30.)])?;
    let inner=Solid::loft(&[section(-1.,11.),section(20.,11.),section(48.,33.),section(149.,33.),section(160.,28.)])?;
    let shell=prop("Concentrate bottle",outer.cut(&inner)?,[0.07,0.025,0.006]);
    let band=Solid::cylinder(mouth+axis*57.,axis,35.25,77.)?
        .cut(&Solid::cylinder(mouth+axis*56.,axis,34.75,79.)?)?;
    let radial=(v3(1.,-0.5,0.45)-axis*axis.dot(v3(1.,-0.5,0.45))).unit();
    let label=Plane::new(mouth+axis*98.+radial*35.6,radial.cross(axis),radial)?;
    let font=Font::from_bytes(fs::read("hardware/install-guide/fonts/Plex-Bold.ttf")?,0)?;
    let text=label.text(&font,"COLA",13.,0.3,HAlign::Center,VAlign::Center)?;
    let liquid=Solid::cylinder(mouth+axis*49.,axis,32.,104.)?;
    let mut out=vec![shell,prop("Concentrate label",band,[0.93,0.93,0.9]),
        prop("COLA",text,[0.005,0.02,0.08]),prop("Concentrate",liquid,[0.025,0.009,0.003])];
    for k in 0..5 {out.push(prop(&format!("Bottle neck rib {k}"),
        Solid::cylinder(mouth+axis*(2.+k as f64*3.),axis,14.,1.2)?
            .cut(&Solid::cylinder(mouth+axis*(1.+k as f64*3.),axis,11.,3.2)?)?,[0.65,0.7,0.75]));}
    Ok(out)
}
fn main() -> Result<()> {
    let out=std::path::absolute(std::env::args().nth(1).context("install-illustrations <run directory>")?)?;
    fs::create_dir_all(&out)?;
    let source_bytes=fs::read(SOURCE)?;let (source,_)=scene::header(&source_bytes)?;
    let box_record:Value=serde_json::from_slice(&fs::read("hardware/manifold-layout/enclosure-box.json")?)?;
    let rear=box_record["box"]["outer"][3].as_f64().context("rear wall")?;
    let layout:Value=serde_json::from_slice(&fs::read("hardware/manifold-layout/above-core.json")?)?;
    let jack=&layout["rear_wall"]["dry_openings"]["keystone"]["face_center_mm"];
    let exterior=select(&source,visible);
    let mut views=vec![];
    let inlet=bounds(&source,"c14-inlet")?;
    let (px,pz)=((inlet[0]+inlet[3])/2.,(inlet[2]+inlet[5])/2.);
    let opening=json!([px,rear+0.1,pz]);
    let nose_y=inlet[4]+50.;
    let plug=Plane::XZ.at(v3(px,nose_y,pz)).extrude(
        &Profile::new(Loop::rounded_rect(V2::ZERO,26.5,18.,2.)?),-31.)?;
    let mut cord=vec![prop("Power connector",plug,[0.012,0.012,0.014])];
    cord.extend(tube("Power cable",&[v3(px,nose_y+31.,pz),v3(px,nose_y+72.,pz),v3(px-23.,nose_y+103.,pz-15.)],7.,[0.018,0.018,0.02])?);
    let path=write_scene(&out,"power-ready",&exterior,&cord)?;
    views.push(json!({"name":"power-ready","path":path,"cam":[-0.85,1.,0.25],"target":[px-8.,505.3,pz-16.],"span":64.,
        "reference_size":[1800,1300],"scale":2,"anchors":{"cord-approach":[px,nose_y,pz],"power-mouth":opening}}));
    let path=write_scene(&out,"the-back-face",&exterior,&[])?;
    views.push(json!({"name":"the-back-face","path":path,"cam":[0.,1.,0.12],"target":[0.,467.,268.],"span":100.,
        "reference_size":[1600,1120],"scale":2,"anchors":{"jack-port":jack}}));
    for (name,retreat) in [("connect-rear-open",60.),("connect-rear-connected",0.)] {
        let mut props=vec![];let mut anchors=serde_json::Map::new();
        for (part,diameter,color) in [("co2-inlet",6.35,[0.7,0.008,0.008]),("bulkhead-water",6.35,[0.8,0.8,0.8]),
            ("bulkhead-carb",6.35,[0.015,0.2,0.65]),("bulkhead-flavor-a",4.,[0.015,0.015,0.017]),
            ("bulkhead-flavor-b",4.,[0.015,0.015,0.017]),("bulkhead-drain",4.,[0.8,0.8,0.8])] {
            let b=bounds(&source,part)?;let (x,z)=((b[0]+b[3])/2.,(b[2]+b[5])/2.);
            let y=b[4]+retreat;
            let tail=(0..=16).map(|i| {
                let t=i as f64/16.;v3(x+25.*t*t,y+100.*t,z+45.*t*t)
            }).collect::<Vec<_>>();
            props.extend(tube(part,&tail,diameter,color)?);
            if part=="co2-inlet" {anchors.insert("co2-mouth".into(),json!([x,b[4],z]));anchors.insert("co2-tube".into(),json!([x,y,z]));}
        }
        let (jx,jz)=(jack[0].as_f64().unwrap(),jack[2].as_f64().unwrap());
        let y=rear+retreat;
        props.push(prop("Faucet DATA plug",Solid::cuboid(v3(jx-4.75,y,jz-4.),v3(jx+4.75,y+19.,jz+4.)),[0.65,0.7,0.72]));
        let tail=(0..=16).map(|i| {
            let t=i as f64/16.;v3(jx+25.*t*t,y+19.+91.*t,jz+40.*t*t)
        }).collect::<Vec<_>>();
        props.extend(tube("Faucet DATA cable",&tail,3.8,[0.7,0.7,0.7])?);
        let path=write_scene(&out,name,&exterior,&props)?;
        views.push(json!({"name":name,"path":path,"cam":[0.7,1.,0.16],"target":[10.,560.,270.],"span":110.,
            "reference_size":[1600,1050],"scale":2,"anchors":anchors}));
    }
    let funnel=bounds(&source,"funnel")?;
    let mouth=v3((funnel[0]+funnel[3])/2.,(funnel[1]+funnel[4])/2.,funnel[5]+15.);
    for (name,open) in [("fill-ready",true),("fill-closed",false)] {
        let head=select(&exterior,|n| !open || n!="funnel-cover");
        let props=if open {bottle(mouth)?}else{vec![]};
        let path=write_scene(&out,name,&head,&props)?;
        views.push(json!({"name":name,"path":path,"cam":[1.,-0.5,0.45],"target":[0.,150.,380.],"span":230.,
            "reference_size":[1600,1500],"scale":2,"anchors":{}}));
    }
    let path=write_scene(&out,"fill-screen-framed",&select(&exterior,|n|n.starts_with("display")||n.starts_with("status-plate")),&[])?;
    let cover=source["meshes"].as_array().unwrap().iter().find(|n|n["name"]=="display-cover").context("display cover")?;
    let frame=&cover["transform"];let up=v3(frame[0][1].as_f64().unwrap(),frame[1][1].as_f64().unwrap(),frame[2][1].as_f64().unwrap());
    let normal=v3(frame[0][2].as_f64().unwrap(),frame[1][2].as_f64().unwrap(),frame[2][2].as_f64().unwrap());
    let mount:Value=serde_json::from_slice(&fs::read("hardware/printed-parts/enclosure/display-cover/mount-dimensions.json")?)?;
    let inset=mount["cover_mm"][2].as_f64().unwrap()+mount["gasket_thickness_mm"].as_f64().unwrap();
    let centre=v3(frame[0][3].as_f64().unwrap(),frame[1][3].as_f64().unwrap(),frame[2][3].as_f64().unwrap())-normal*inset;
    views.push(json!({"name":"fill-screen-framed","path":path,"cam":[normal.x,normal.y,normal.z],"up":[up.x,up.y,up.z],
        "target":[0.,centre.y,centre.z],"span":75.,"reference_size":[1800,1200],"scale":1,"anchors":{}}));
    fs::write(out.join("scenes.json"),serde_json::to_vec_pretty(&json!({"source":SOURCE,"source_sha256":scene::digest(&source_bytes),
        "screen":{"centre":[centre.x,centre.y,centre.z],"up":[up.x,up.y,up.z],"normal":[normal.x,normal.y,normal.z],"width":99.8,"height":60.},
        "bottle_mouth":[mouth.x,mouth.y,mouth.z],"views":views}))?)?;
    Ok(())
}
