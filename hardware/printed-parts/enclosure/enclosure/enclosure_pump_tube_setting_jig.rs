//! The factory tube-length gauge cuts the pump tube blanks against open channels with blind stops.
//!
//!     enclosure-pump-tube-setting-jig [--box <declared Box>] [<output directory>]
use anyhow::Result;
use hsm_enclosure_numbers::Color;
use hsm_enclosure_numbers::catalog::{digits, wall_color};
use hsm_enclosure_numbers::spec::ColletPlate;
use hsm_enclosure_solid::pieces::{keep, payload, solids};
use hsm_enclosure_solid::plan::{Graph, Shape};
use hsm_kernel::Body;
use hsm_kernel::write::PrintOutput;
use std::path::Path;

fn main() -> Result<()> {
    let (b, out) = hsm_enclosure_solid::run::arguments("enclosure-pump-tube-setting-jig")?;
    let mut g = Graph::new();
    let plate = &b.pack.collet_plate;
    let jig = tube_setting_jig(&mut g, plate);
    write(&out, &g, jig, digits(wall_color()))
}

/// The tube blank sits against a blind stop and is cut at the gauge's open fore face.
pub fn tube_setting_jig(g: &mut Graph, plate: &ColletPlate) -> Shape {
    let row = plate.holes[0][1];
    let tip = plate.pump_tube_cut;
    let front = 0.;
    let first = plate.holes[0][0];
    let last = plate.holes[plate.holes.len() - 1][0];
    let mut body = g.box_([first - 8.0, last + 8.0, front, tip + 3.0, row - 8.0, row + 8.0]);
    for &[x, z] in &plate.holes {
        let bore = g.ycyl(3.5, x, z, front - 0.1, tip);
        let opening = g.box_([x - 3.5, x + 3.5, front - 0.1, tip, z, row + 8.1]);
        let channel = g.union(bore, &[opening]);
        body = g.cut(body, &[channel]);
    }
    body
}

fn write(dir: &Path, g: &Graph, result: Shape, color: Color) -> Result<()> {
    let name = "enclosure-pump-tube-setting-jig";
    let [solid] = solids(g, [result], None)?;
    let bodies=[Body{name,color:Some(color),solid:&solid}];
    let simple=solid.simplified()?;
    let print=PrintOutput::new(&[Body{name,color:Some(color),solid:&simple}]);
    let model=print.model_bytes(&bodies,&format!("{name}.stl"),None)?;
    let stl=print.into_stl_bytes();
    keep(&dir.join(format!("{name}.step.npz")),&model)?;
    keep(&dir.join(format!("{name}.stl")),&stl)?;
    payload(dir, name, color, &stl, &model, None)
}
