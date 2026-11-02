//! The cast silicone funnel, with its original brim-bearing frame.
mod funnel_geometry;
use anyhow::{Result,ensure};
use hsm_kernel::{Solid,v3};
use hsm_kernel::part::{args,AssemblyBody,write_assembly};
use serde_json::json;
fn main()->Result<()> {
    let(n,out)=args()?;let dims=funnel_geometry::Dimensions::from_numbers(&n)?;
    let(outside,cavity)=funnel_geometry::build_solids(&dims,0.0,true,true)?;
    let funnel=outside.cut(&cavity)?;funnel.check()?;
    ensure!(funnel.components().len()==1,"the funnel is one closed body");
    let fill=cavity.intersect(&Solid::cuboid(v3(-300.0,-300.0,dims.end_z),v3(300.0,300.0,dims.top_z)))?.volume();
    let size=funnel.bounds().size();let tolerance=(size.x+size.y+size.z)/3.0*n.f("viewer_deflection_ratio")?;
    let presentation=funnel.simplified_to(tolerance)?;
    let mut said=write_assembly(&out,"funnel",&[AssemblyBody{name:"funnel",color:Some(n.color("color")?),fine:&funnel,presentation:&presentation}],Some(&json!({})))?;
    said["bodies"][0]["fill_mm3"]=json!(fill);println!("{said}");Ok(())
}
