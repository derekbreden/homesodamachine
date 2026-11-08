//! The side-loading pump cartridge captures both faces of the skirts in continuous channels.
//! It prints on its closed end; the pumps enter through the opposite end before installation.
use crate::catalog::wall_color;
use crate::plan::{Graph, Shape};
use crate::spec::Box;
use hsm_enclosure_retainer_numbers::channels;

/// The front and rear bearing channels join at the closed end, with the head and motor open.
pub fn retainer(g: &mut Graph, b: &Box) -> Shape {
    let d = channels(b);
    let fore = g.yz_prism(d.x0, d.x1, vec![
        [d.fore_y, d.bottom_z], [d.lower_fore_y, d.bottom_z],
        [d.lower_fore_y, d.support_z], [d.fore_groove_y, d.support_z],
        [d.fore_groove_y, d.bearing_z], [d.upper_fore_y, d.bearing_z],
        [d.upper_fore_y, d.top_z], [d.fore_y, d.top_z],
    ]);
    let aft = g.yz_prism(d.x0, d.x1, vec![
        [d.lower_aft_y, d.bottom_z], [d.aft_y, d.bottom_z],
        [d.aft_y, d.top_z], [d.upper_aft_y, d.top_z],
        [d.upper_aft_y, d.bearing_z], [d.aft_groove_y, d.bearing_z],
        [d.aft_groove_y, d.support_z], [d.lower_aft_y, d.support_z],
    ]);
    let end = g.box_([d.end_x, d.x1, d.fore_y, d.aft_y, d.bottom_z, d.top_z]);
    g.union(end, &[fore, aft])
}

/// The cartridge has the same geometry on the plate and in the machine.
pub struct Piece {
    pub name: &'static str,
    pub color: [f64; 3],
    pub graph: Graph,
    pub result: Shape,
    pub seated: bool,
}

pub fn piece(b: &Box, seated: bool) -> Piece {
    let mut graph = Graph::new();
    let result = retainer(&mut graph, b);
    Piece {
        name: if seated { "enclosure-pump-retainer-seated" } else { "enclosure-pump-retainer" },
        color: wall_color(), graph, result, seated,
    }
}
