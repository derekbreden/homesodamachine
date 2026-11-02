//! Upright drilling jaws for the authored inlet-jet cap stock.
use anyhow::{ensure, Result};
use hsm_kernel::part::{self, Numbers};
use hsm_kernel::{v3, Body, Solid, V3};
use serde_json::json;

fn build(n: &Numbers) -> Result<(Solid, Solid)> {
    let base = n.list("base")?;
    let jaw = n.list("jaw")?;
    let (width, depth, height) = (jaw[0], jaw[1], jaw[2]);
    let gap = n.f("gap")?;
    let radius = n.f("groove_radius")?;
    let groove = Solid::cylinder(v3(0.0, 0.0, base[2] - 1.0), V3::Z,
                                radius, height + 2.0)?;
    let fixed = Solid::cuboid(v3(-base[0]/2.0, -base[1]/2.0, 0.0),
                              v3(base[0]/2.0, base[1]/2.0, base[2]))
        .union(&Solid::cuboid(v3(-width/2.0, gap/2.0, base[2]),
                              v3(width/2.0, gap/2.0+depth, base[2]+height))
               .cut(&groove)?)?;
    let loose = Solid::cuboid(v3(-width/2.0, -gap/2.0-depth, base[2]),
                              v3(width/2.0, -gap/2.0, base[2]+height)).cut(&groove)?;
    for (name, part) in [("fixed jaw and base", &fixed), ("loose jaw", &loose)] {
        part.check()?;
        ensure!(part.components().len() == 1 && part.volume() > 0.0,
                "{name}: expected one valid positive-volume solid");
    }
    for diameter in [n.f("stock_diameter")?-0.1,n.f("stock_diameter")?,n.f("stock_diameter")?+0.1] {
        let closure = 2.0*radius-diameter;
        ensure!(closure > 0.0 && gap-closure > 0.0,
                "candidate stock range exhausts jaw travel");
    }
    let drill = Solid::cylinder(v3(0.0,n.f("radial_slip")?,base[2]+n.f("minimum_blank")?-4.0),
                                V3::Z,n.f("drill_diameter")?/2.0,15.0)?;
    ensure!(fixed.shared_volume(&drill)? + loose.shared_volume(&drill)? <= 1e-6,
            "drilling path reaches a printed jaw");
    let loose_print = loose.translate(v3(0.0,0.0,-base[2]));
    for (name,part,size) in [("fixed",&fixed,[base[0],base[1],base[2]+height]),
                           ("loose",&loose_print,[width,depth,height])] {
        ensure!(part.bounds().size().to_array().iter().zip(size).all(|(a,b)| (a-b).abs() <= 1e-6),
                "{name}: unexpected print envelope");
    }
    Ok((fixed,loose_print))
}

fn main() -> Result<()> {
    let (n,out) = part::args()?;
    let (fixed,loose) = build(&n)?;
    let mut files=vec![];let mut bodies=vec![];
    for (name,solid) in [("water-inlet-jet-fixture-fixed",&fixed),
                         ("water-inlet-jet-fixture-loose",&loose)] {
        let said=part::write_part(&out,name,&[Body{name,color:Some(n.color("color")?),solid}])?;
        files.extend(said["files"].as_array().unwrap().iter().cloned());
        bodies.extend(said["bodies"].as_array().unwrap().iter().cloned());
    }
    println!("{}",json!({"files":files,"bodies":bodies}));
    Ok(())
}
