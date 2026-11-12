//! The pump retainer prints as one solid; the installed model places one at each pump with its fasteners.
#[path = "retainer/retainer.rs"]
mod retainer;

use anyhow::{Context, Result};
use hsm_enclosure_numbers::{catalog, spec};
use hsm_enclosure_retainer_numbers as dimensions;
use hsm_enclosure_solid::pieces::{digest, keep, payload, solids};
use hsm_enclosure_solid::plan::{self, Graph};
use hsm_kernel::{Body, Plane, Profile, Solid, V3, v2, v3};
use hsm_kernel::write::{PrintOutput, payload_bytes_with_sources};
use std::path::Path;

fn main() -> Result<()> {
    let (b,out)=hsm_enclosure_solid::run::arguments("enclosure-pump-retainer")?;
    let mut g=Graph::new();
    let shape=retainer::retainer(&mut g,&b,0.);
    let part=as_saved(solids(&g,[shape],None)?)?;
    write_print(&out,&part)?;
    let mut placed=Vec::new();
    for (i,p) in b.pack.pump_trays.iter().enumerate() {
        placed.push((format!("enclosure-pump-retainer-{}",if i==0 {"a"} else {"b"}),catalog::wall_color(),part.translate(v3(p[0],0.,0.))));
    }
    placed.extend(hardware(&b)?);
    let bodies:Vec<_>=placed.iter().map(|(name,color,solid)|Body{name,color:Some(*color),solid}).collect();
    write_installed(&out,"enclosure-pump-retainer-seated",&bodies)
}

fn write_print(dir:&Path,solid:&Solid)->Result<()> {
    let name="enclosure-pump-retainer";
    let bodies=[Body{name,color:Some(catalog::wall_color()),solid}];
    let simple=solid.simplified()?;
    let print=PrintOutput::new(&[Body{name,color:Some(catalog::wall_color()),solid:&simple}]);
    let model=print.model_bytes(&bodies,&format!("{name}.stl"),None)?;
    let stl=print.into_stl_bytes();
    keep(&dir.join(format!("{name}.step.npz")),&model)?;
    keep(&dir.join(format!("{name}.stl")),&stl)?;
    payload(dir,name,catalog::wall_color(),&stl,&model,None)
}

fn write_installed(dir:&Path,name:&str,bodies:&[Body])->Result<()> {
    let model=hsm_kernel::model_bytes(bodies);
    keep(&dir.join(format!("{name}.step.npz")),&model)?;
    let bytes=payload_bytes_with_sources(bodies,Some(&digest(&model)),None);
    let mut head=hsm_kernel::scene::pack(&bytes)?;
    head["step_export"]=false.into();
    hsm_kernel::scene::persist(&dir.join(format!("{name}.step.mesh")),&head)
}

/// Purchased socket screws and short heat-set inserts stand on the printed seats.
fn hardware(b:&spec::Box)->Result<Vec<(String,[f64;3],Solid)>> {
    use dimensions::*;
    let d=datums(b);
    let seat=d.bottom_z+COUNTERBORE_DEPTH;
    let mut out=Vec::new();
    for (i,p) in b.pack.pump_trays.iter().enumerate() {
        for (side,x) in ["west","east"].into_iter().zip(screw_xs(p[0])) {
            let base=seat-HEAD_HEIGHT;
            let head=Solid::cylinder(v3(x,SCREW_Y,base),V3::Z,HEAD_DIAMETER/2.,HEAD_HEIGHT)?;
            let shaft=Solid::cylinder(v3(x,SCREW_Y,seat),V3::Z,SCREW_DIAMETER/2.,SCREW_LENGTH)?;
            let r=HEX_KEY/(2.*(std::f64::consts::PI/6.).cos());
            let hex:Vec<_>=(0..6).map(|i|{let a=std::f64::consts::TAU*i as f64/6.;v2(x+r*a.cos(),SCREW_Y+r*a.sin())}).collect();
            let socket=Plane::XY.at(v3(0.,0.,base-0.1)).extrude(&Profile::polygon(&hex),1.7)?;
            let screw=head.union(&shaft)?.cut(&socket)?;
            let z=insert_start(b);
            let insert=Solid::cylinder(v3(x,SCREW_Y,z),V3::Z,INSERT_DIAMETER/2.,INSERT_LENGTH)?
                .cut(&Solid::cylinder(v3(x,SCREW_Y,z-0.1),V3::Z,1.3,INSERT_LENGTH+0.2)?)?;
            let pump=if i==0 {"a"} else {"b"};
            out.push((format!("pump-retainer-{pump}-{side}-screw"),[0.025;3],screw));
            out.push((format!("pump-retainer-{pump}-{side}-insert"),[0.65,0.38,0.09],insert));
        }
    }
    Ok(out)
}

/// The clamp as a saved model holds it, so one built in this run draws the same installed
/// payload as one restored from a saved stage.
fn as_saved([solid]:[Solid;1])->Result<Solid> {
    let model=hsm_kernel::model_bytes(&[Body{name:"clamp",color:None,solid:&solid}]);
    Ok(hsm_kernel::import::model_bodies(&model)?.pop().context("the saved clamp")?.solid)
}
