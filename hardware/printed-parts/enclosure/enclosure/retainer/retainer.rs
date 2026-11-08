//! Each pump's removable flange retainer is a broad body with local screw seats.
use crate::plan::{Graph, Shape};
use crate::spec::Box;
use hsm_enclosure_retainer_numbers::*;

/// The retainer's head opening leaves a broad bearing strip under the fore flange.
pub fn retainer(g: &mut Graph, b: &Box, centre: f64) -> Shape {
    let d = datums(b);
    let mut body = g.box_([centre-HALF_X,centre+HALF_X,d.y0,d.y1,d.bottom_z,d.retainer_top_z]);
    let notch = g.box_([centre-NOTCH_HALF_X,centre+NOTCH_HALF_X,NOTCH_FORE_Y,d.y1+1.,d.bottom_z-1.,d.retainer_top_z+1.]);
    body = g.cut(body,&[notch]);
    for x in screw_xs(centre) {
        let bore = g.zcyl(CLEARANCE_DIAMETER/2.,x,SCREW_Y,d.bottom_z-1.,d.retainer_top_z+1.);
        let seat = g.zcyl(COUNTERBORE_DIAMETER/2.,x,SCREW_Y,d.bottom_z-1.,d.bottom_z+COUNTERBORE_DEPTH);
        body = g.cut(body,&[bore,seat]);
    }
    body
}
