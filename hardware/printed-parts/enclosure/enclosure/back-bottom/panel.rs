//! The back-bottom panel: the lower rear quadrant, cut from the back half under the seam.
use crate::piece::Build;
use crate::plan::{Graph, Shape};
use crate::quadrant::Quadrant;
use crate::spec::Box;
use crate::walls::{cavity, floor_tongue};

/// The back-bottom's construction: the back half under the seam, its floor relieved for the
/// front floor's tongue, then the quadrant's features.
pub fn construction(b: &Box) -> (Graph, Shape) {
    let mut g = Graph::new();
    let silhouette = g.silhouette(b.outer);
    let top = b.splits[1];
    let o = b.outer;
    let air = cavity(&mut g, &b.inner, 0.0, None);
    let shell = g.cut(silhouette, &[air]);
    let band = g.box_([o[0], o[1], b.y_joint, o[3], o[4], top]);
    let half = g.intersect(shell, &[band]);
    let (_, relief) = floor_tongue(&mut g, &b.inner, b.y_joint);
    let half = g.cut(half, &[relief]);
    let piece = crate::pipeline(&mut g, &Build { b, q: Quadrant::BACK_BOTTOM, silhouette, half });
    (g, piece)
}
