//! The production cradle and the cropped web/socket receiver.
#[path="../cradle_geometry.rs"]
mod cradle_geometry;
use anyhow::Result;
use hsm_kernel::part::{args,write_part};
use hsm_kernel::{Body,v3};

fn main() -> Result<()> {
    let (n,out) = args()?;
    let cradle = cradle_geometry::cradle(&n)?;
    let receiver = cradle_geometry::receiver(&n)?;
    let facts = cradle_geometry::trial_facts(&n,&receiver,&cradle)?;
    let file = "geometry-check.json";
    let bytes = format!("{}\n",serde_json::to_string_pretty(&facts)?);
    let path = out.join(file);
    if std::fs::read(&path).ok().as_deref()!=Some(bytes.as_bytes()) {
        std::fs::write(&path,bytes)?;
    }
    let printed = cradle.translate(v3(0.0,0.0,-n.list("block")?[3]));
    for (name,solid) in [("test-receiver",&receiver),("test-cradle",&printed)] {
        let mut said = write_part(&out,name,&[Body {
            name,color:Some(n.color("color")?),solid,
        }])?;
        if name=="test-receiver" { said["files"].as_array_mut().unwrap().push(file.into()); }
        println!("{said}");
    }
    Ok(())
}
