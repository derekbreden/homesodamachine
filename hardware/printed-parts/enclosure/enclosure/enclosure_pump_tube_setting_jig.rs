//! The factory tube-setting jig's files from the declared Box: four open channels on the pump
//! cartridge's cradle back, their blind ends at each pump tube's seated tip.
//!
//!     enclosure-pump-tube-setting-jig [--box <declared Box>] [<output directory>]
use anyhow::Result;
use hsm_enclosure_dock_numbers::plumbing;
use hsm_enclosure_numbers::Color;
use hsm_enclosure_numbers::catalog::{digits, wall_color};
use hsm_enclosure_numbers::shell::shell;
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
    let jig = tube_setting_jig(&mut g, plate, shell().pump_cartridge_aft_y(&b.pack.pump_trays, plate));
    write(&out, &g, jig, digits(wall_color()))
}

/// Factory gauge that seats on the cradle's flat back and catches the four tube tips: four open
/// channels admit the tubes, and their blind ends are the seated tip datum.
pub fn tube_setting_jig(g: &mut Graph, plate: &ColletPlate, cradle_back_y: f64) -> Shape {
    let row = plate.holes[0][1];
    let tip = plumbing::tip_y(plate.fore_y);
    let first = plate.holes[0][0];
    let last = plate.holes[plate.holes.len() - 1][0];
    let mut body = g.box_([first - 8.0, last + 8.0, cradle_back_y, tip + 3.0, row - 8.0, row + 8.0]);
    for &[x, z] in &plate.holes {
        let bore = g.ycyl(3.5, x, z, cradle_back_y - 0.1, tip);
        let opening = g.box_([x - 3.5, x + 3.5, cradle_back_y - 0.1, tip, z, row + 8.1]);
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
