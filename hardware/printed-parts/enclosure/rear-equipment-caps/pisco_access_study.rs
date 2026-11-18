//! This study compares an L shaped Pisco cover with a common cover for the Pisco and meter.
#[allow(dead_code)]
mod stations;

use anyhow::Result;
use hsm_enclosure_numbers::{P2, Bounds};
use hsm_enclosure_numbers::catalog::{running, slip};
use hsm_enclosure_numbers::layout::{Pose, layout};
use hsm_kernel::{Affine, Body, Plane, Profile, Solid, V3, v2, v3};
use hsm_kernel::import::{self, Imported};
use hsm_kernel::part::{write_part, write_shown};
use std::path::{Path, PathBuf};

const WALL: f64 = 3.0;
const ROOT: f64 = 1.5;
const OVERRUN: f64 = 1.0;
const RELEASE: f64 = 3.6;
const DROP: f64 = 40.0;
const BEARING_LENGTH: f64 = 3.0;
const BODY_FIT: f64 = 0.15;
const HARDWARE_ENTRY: f64 = 64.0;

type Item = (String, [f64; 3], Solid);
const FIXED: [f64; 3] = [0.12, 0.24, 0.34];
const COVER: [f64; 3] = [0.95, 0.48, 0.08];
const METER: [f64; 3] = [0.22, 0.46, 0.52];

fn box_([x0,x1,y0,y1,z0,z1]: Bounds) -> Solid {
    Solid::cuboid(v3(x0,y0,z0),v3(x1,y1,z1))
}

fn frame(p: &Pose) -> Affine {
    Affine::from_columns(
        v3(p.rotation[0][0],p.rotation[1][0],p.rotation[2][0]),
        v3(p.rotation[0][1],p.rotation[1][1],p.rotation[2][1]),
        v3(p.rotation[0][2],p.rotation[1][2],p.rotation[2][2]), V3::from(p.translation_mm))
}

fn turned(points: &[P2]) -> Result<Solid> {
    let mut outline = vec![v2(points[0][0],0.0)];
    outline.extend(points.iter().copied().map(hsm_kernel::V2::from));
    outline.push(v2(points[points.len()-1][0],0.0));
    Plane::XY.revolve(&Profile::polygon(&outline),360.0,hsm_kernel::V2::ZERO,v2(1.0,0.0))
}

struct Access {
    cover: Solid,
    receiver: Solid,
    leaf: Solid,
    rigid: Solid,
    leaf_root: f64,
    whole_receiver: Solid,
}

/// The open lower west quarter is the cover; a fixed east cheek holds the opposite quarter.
fn pisco(old: &Solid, original: &Solid) -> Result<Access> {
    let st = stations::pisco_station();
    let m = stations::Meter::placed();
    let mouth = layout().rear_plumbing.gas_frame.point([0.0;3]);
    let x = mouth[0];
    let b = original.bounds();
    let cap = original.intersect(&box_([b.min.x-OVERRUN,x-slip()/2.0,
        st.y0-OVERRUN,st.y1+OVERRUN,b.min.z-OVERRUN,b.max.z+OVERRUN]))?;
    let region = box_([b.min.x-OVERRUN,x-st.inner+ROOT+0.5,
        st.y0-OVERRUN,st.y1+OVERRUN,st.root,b.max.z+OVERRUN])
        .union(&box_([b.min.x-OVERRUN,x,st.y0-OVERRUN,st.y1+OVERRUN,
            st.bearing-ROOT,b.max.z+OVERRUN]))?;
    let leaf = cap.intersect(&region)?;
    let rigid = cap.cut(&region)?;
    let pose = Pose { rotation: [[0.0,1.0,0.0],[-1.0,0.0,0.0],[0.0,0.0,1.0]], translation_mm: mouth };
    let bore = turned(&stations::clearance_profile(&stations::pisco_exterior().profile_z_radius_mm,
        running()+slip(),running()))?.transformed(&frame(&pose));
    let cheek = box_([x+slip()/2.0,x+st.outer,
        st.y0-running()-WALL,st.y1+running()+WALL,b.min.z,352.0]).cut(&bore)?;
    let release_room = box_([b.min.x-RELEASE-ROOT,x-st.ledge,
        st.y0-running(),st.y1+running(),st.split-OVERRUN,352.0]);
    let exterior = &stations::pisco_exterior().profile_z_radius_mm;
    let widest = exterior.iter().copied().reduce(|best,p|if p[1]>best[1]{p}else{best}).unwrap();
    let ring = mouth[1]-widest[0];
    let low = ring-BEARING_LENGTH/2.0;
    let high = ring+BEARING_LENGTH/2.0;
    let mut receiver = old.union(&cheek)?.cut(&release_room)?;
    for (a,b,air) in [(st.y0-running()-WALL-OVERRUN,low,running()+slip()),
        (low,high,BODY_FIT),(high,st.y1+running(),running()+slip())] {
        let passage = Solid::cylinder(v3(x,a,mouth[2]),V3::Y,widest[1]+air,b-a)?;
        receiver=receiver.cut(&passage)?;
        // The lower bore follows the shell's corbel slope in the ceiling-down print.
        let slope=stations::corbel_slope();
        let r=widest[1]+air;
        let norm=(1.0+slope*slope).sqrt();
        let tangent=[x+r*slope/norm,mouth[2]-r/norm];
        let apex=[x,mouth[2]-r*norm];
        let relief=Plane::XZ.at(v3(0.0,a,0.0)).extrude(
            &Profile::polygon(&[v2(apex[0],apex[1]),v2(tangent[0],tangent[1]),v2(x,mouth[2])]),-(b-a))?;
        receiver=receiver.cut(&relief)?;
    }
    let crop = box_([b.min.x-7.0,107.5,m.seat[0]-WALL,st.y1+running()+2.0*WALL,
        m.z-m.station().outer-WALL,355.0]);
    Ok(Access {cover:cap,receiver:receiver.intersect(&crop)?,leaf,rigid,leaf_root:st.root,
        whole_receiver:receiver})
}

/// The shared cover keeps the meter's lower spring and joins its rigid back to the Pisco's back.
fn common(a: &Access, old_meter: &Solid) -> Result<Solid> {
    let m = stations::Meter::placed();
    let st = m.station();
    let b = old_meter.bounds();
    let remove = box_([b.min.x+9.0,b.max.x+OVERRUN,m.cap[0]-OVERRUN,m.cap[1]+OVERRUN,
        m.z+st.inner-OVERRUN,b.max.z+OVERRUN]);
    let lower = old_meter.cut(&remove)?;
    let ab = a.cover.bounds();
    let join = box_([ab.min.x,b.min.x+9.0,ab.min.y,m.cap[1],m.z+st.inner-ROOT,
        stations::pisco_station().root]);
    lower.union(&join)?.union(&a.cover)
}

fn save(out: &Path,name: &str,items: &[Item]) -> Result<()> {
    let bodies:Vec<_> = items.iter().map(|(name,color,solid)|Body{name:name.as_str(),color:Some(*color),solid}).collect();
    println!("{}",write_shown(out,name,&bodies)?);
    Ok(())
}

fn add_context(items: &mut Vec<Item>,machine: &[Imported]) {
    for b in machine.iter().filter(|b| b.name.starts_with("gas-regulator") || b.name=="gas-check"
        || b.name.starts_with("digiten-flow") || b.name=="tube-soda-meter-bulkhead") {
        items.push((b.name.clone(),b.color.unwrap_or([0.5;3]),b.solid.clone()));
    }
}

fn main() -> Result<()> {
    let out = std::env::args_os().nth(1).map(PathBuf::from)
        .unwrap_or_else(||PathBuf::from("hardware/printed-parts/enclosure/rear-equipment-caps/pisco-access"));
    std::fs::create_dir_all(&out)?;
    hsm_kernel::reads::begin();
    let installed = import::model("hardware/printed-parts/enclosure/rear-equipment-caps/rear-equipment-caps-installed.step.npz")?;
    let meter = import::body(&installed,"meter-snap-cap")?.clone();
    let shell = import::model("hardware/printed-parts/enclosure/enclosure/enclosure-back-top.step.npz")?;
    let old = import::body(&shell,"enclosure-back-top")?;
    let original = import::body(&installed,"pisco-snap-cap")?;
    let a = pisco(old,original)?;
    let combined = common(&a,&meter)?;
    let bytes=std::fs::read("hardware/manifold-layout/enclosure-assembly.step.mesh")?;
    let size=u32::from_le_bytes(bytes[..4].try_into()?) as usize;
    let header:serde_json::Value=serde_json::from_slice(&bytes[4..size+4])?;
    let mut at=0;
    let mut selected=Vec::new();
    for b in header["meshes"].as_array().unwrap() {
        for e in b["entries"].as_array().unwrap() {
            let n=e["name"].as_str().unwrap_or("");
            if n.starts_with("gas-regulator")||n=="gas-check"||n.starts_with("digiten-flow")
                ||n=="tube-soda-meter-bulkhead" {selected.push(at);}
            at+=1;
        }
    }
    let bytes=hsm_kernel::scene::flatten_selected_with(&bytes,&selected,hsm_kernel::scene::load_asset)?;
    let machine=import::bodies(&bytes,"installed plumbing")?;
    for (name,cap,independent) in [("separate-l-cover",&a.cover,true),("combined-cover",&combined,false)] {
        for (state,move_by) in [("seated",V3::ZERO),("exploded",v3(-35.0,-15.0,-8.0))] {
            let mut items = vec![("receiver".into(),FIXED,a.receiver.clone()),
                (name.into(),COVER,cap.translate(move_by))];
            if independent {items.push(("meter-snap-cap".into(),METER,meter.clone()));}
            add_context(&mut items,&machine);
            save(&out,&format!("{name}-{state}"),&items)?;
        }
        let turned = cap.rotate(V3::ZERO,V3::X,90.0);
        let b = turned.bounds();
        let printed = turned.translate(v3(-(b.min.x+b.max.x)/2.0,-(b.min.y+b.max.y)/2.0,-b.min.z));
        println!("{}",write_part(&out,name,&[Body{name,color:Some(COVER),solid:&printed}])?);
    }
    let report = serde_json::json!({"purpose":"These sampled moves compare access through the retained receiver geometry. Exploded views separate the parts for inspection and do not describe an installation move.",
        "separate":sample_path(&released(&a,&a.cover,false)?,&a.whole_receiver,&machine,false)?,
        "combined":sample_path(&released(&a,&combined,true)?,&a.whole_receiver,&machine,true)?,
        "hardware_entry":hardware_entry(&a.whole_receiver,&machine)?});
    std::fs::write(out.join("access.numbers.json"),serde_json::to_vec_pretty(&report)?)?;
    println!("saved access.numbers.json");
    Ok(())
}

/// The Pisco enters axially through the open fore end of its receiver with its check disconnected.
fn hardware_entry(receiver:&Solid,machine:&[Imported])->Result<serde_json::Value> {
    let regulator=import::body(machine,"gas-regulator")?;
    let mut rows=Vec::new();
    for i in 0..=HARDWARE_ENTRY as usize {
        let by=v3(0.0,-(i as f64),0.0);
        rows.push(serde_json::json!({"fore_mm":i,"receiver_intersection_mm3":
            regulator.translate(by).intersect(receiver)?.volume()}));
    }
    Ok(serde_json::json!(rows))
}

/// A held leaf bends into its free space, with its root fixed to the rigid back.
fn released(a:&Access,cap:&Solid,combined:bool)->Result<Solid> {
    let rate = RELEASE/(stations::pisco_station().bearing+stations::catch_air()-a.leaf_root);
    let shear = Affine::from_columns(V3::X,V3::Y,v3(-rate,0.0,1.0),v3(rate*a.leaf_root,0.0,0.0));
    let rigid=if combined {cap.cut(&a.leaf)?} else {a.rigid.clone()};
    let mut held = Solid::compose(&[rigid,a.leaf.transformed(&shear)]);
    if combined {
        let m=stations::Meter::placed();
        let st=m.station();
        let root=m.split+st.root;
        let region=box_([root,110.0,m.cap[0]-OVERRUN,m.cap[1]+OVERRUN,
            m.z-st.outer-OVERRUN,m.z-st.inner+stations::REACH+OVERRUN]);
        let leaf=held.intersect(&region)?;
        let rate=RELEASE/(st.bearing+stations::catch_air()-st.root);
        let shear=Affine::from_columns(v3(1.0,0.0,-rate),V3::Y,V3::Z,v3(0.0,0.0,rate*root));
        held=Solid::compose(&[held.cut(&region)?,leaf.transformed(&shear)]);
    }
    Ok(held)
}

/// The separate cover drops after the meter is removed; the common cover retains the meter.
fn sample_path(cap: &Solid,receiver: &Solid,machine:&[Imported],combined:bool) -> Result<serde_json::Value> {
    let mut rows=Vec::new();
    let waypoints=if combined {vec![v3(0.0,0.0,0.0),v3(-4.0,0.0,0.0),v3(-4.0,0.0,-12.0)]}
        else {vec![V3::ZERO,v3(0.0,0.0,-DROP)]};
    for leg in waypoints.windows(2) {
        let steps=(leg[1]-leg[0]).norm().ceil() as usize;
        for i in 0..=steps {
            let by=leg[0]+(leg[1]-leg[0])*(i as f64/steps as f64);
            let moving=cap.translate(by);
            let shell=moving.intersect(receiver)?.volume();
            let mut hardware=Vec::new();
            for b in machine.iter().filter(|b|b.name.starts_with("gas-regulator")||b.name=="gas-check"
                ||(combined&&b.name.starts_with("digiten-flow"))) {
                let v=moving.intersect(&b.solid)?.volume();
                if v>0.01 {hardware.push(serde_json::json!({"part":b.name,"volume_mm3":v}));}
            }
            rows.push(serde_json::json!({"translation_mm":[by.x,by.y,by.z],"receiver_intersection_mm3":shell,"hardware":hardware}));
        }
    }
    Ok(serde_json::json!(rows))
}
