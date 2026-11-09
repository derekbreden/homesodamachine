//! What the above-core layout puts on the top pieces: the wiring's Wago wells on both, and on
//! back-top the rear wall's openings and identification, its wall hosts, valve seats and fluid
//! supports.
use crate::plan::{Bounds, Graph, Shape};
use crate::quadrant::Y;
use crate::shapes::place;
use crate::shell::WAGO_WELL_WALL;
use crate::spec::Box;
use crate::junctions::{JUNCTIONS, Wago};

/// The connector's fit in its well's pocket; the well's stock round it is the shell's.
const WELL_FIT: f64 = 0.15;

/// The piece with every above-core feature it carries, and the wells' pockets, which back-top's
/// wall features keep clear of.
pub fn apply(g: &mut Graph, mut piece: Shape, b: &Box, col: Y) -> (Shape, Option<Shape>) {
    let (stocks, pockets) = wells(g, col);
    let cut = union_all(g, &pockets);
    if !stocks.is_empty() {
        let stock = match col {
            Y::Front => stacked_towers(g, &stocks, &b.inner),
            Y::Back => union_all(g, &stocks).expect("back-top carries wells"),
        };
        piece = g.union(piece, &[stock]);
    }
    if let Some(cut) = cut {
        piece = g.cut(piece, &[cut]);
    }
    (piece, cut)
}

/// The first shape fused with the rest, or nothing when there are none.
fn union_all(g: &mut Graph, shapes: &[Shape]) -> Option<Shape> {
    let (first, rest) = shapes.split_first()?;
    Some(g.union(*first, rest))
}

/// Each junction's well on this top piece: closed stock round the connector's blank rear half,
/// and the pocket it inserts into butt first. Back-top seats its row against the west wall;
/// front-top carries its wells on the manifold towers.
fn wells(g: &mut Graph, host: Y) -> (Vec<Shape>, Vec<Shape>) {
    let (wall, fit) = (WAGO_WELL_WALL, WELL_FIT);
    let mut stocks = Vec::new();
    let mut pockets = Vec::new();
    for j in JUNCTIONS.iter().filter(|j| j.host == host) {
        let Wago { width: w, depth: d, height: h, .. } = j.wago;
        let rear = -d / 2.0 - fit - wall;
        let stock = g.box_([-w / 2.0 - fit - wall, w / 2.0 + fit + wall, rear, j.mouth, -fit - wall, h + fit + wall]);
        stocks.push(place(g, stock, j.rotation, j.translation));
        let pocket = g.box_([-w / 2.0 - fit, w / 2.0 + fit, -d / 2.0 - fit, 1.0, -fit, h + fit]);
        pockets.push(place(g, pocket, j.rotation, j.translation));
    }
    (stocks, pockets)
}

/// Front-top's wells as towers: each overlapping group of well stocks one box, standing on a
/// wedge that runs it out to its flank.
fn stacked_towers(g: &mut Graph, stocks: &[Shape], inner: &Bounds) -> Shape {
    let mut boxes: Vec<Bounds> = stocks.iter().map(|s| s.bounds()).collect();
    let overlaps = |a: &Bounds, b: &Bounds| (0..3).all(|k| a[2 * k + 1].min(b[2 * k + 1]) - a[2 * k].max(b[2 * k]) > 1e-8);
    let mut groups: Vec<Vec<Bounds>> = Vec::new();
    while let Some(first) = boxes.pop() {
        let mut group = vec![first];
        let mut changed = true;
        while changed {
            changed = false;
            for i in (0..boxes.len()).rev() {
                if group.iter().any(|a| overlaps(a, &boxes[i])) {
                    group.push(boxes.remove(i));
                    changed = true;
                }
            }
        }
        groups.push(group);
    }
    let towers: Vec<Shape> = groups
        .iter()
        .map(|group| {
            let b = hull(group.iter());
            let east = b[1] > 0.0;
            let wall = if east { inner[1] } else { inner[0] };
            let face = if east { b[0] } else { b[1] };
            let run = (wall - face).abs();
            let wedge = g.prism(1, b[2], b[3], vec![[face, b[4]], [wall, b[4]], [wall, b[4] - run]]);
            let stock = g.box_(b);
            g.union(stock, &[wedge])
        })
        .collect();
    g.union(towers[0], &towers[1..])
}

/// The bounds that hold every one of these bounds.
fn hull<'a>(members: impl Iterator<Item = &'a Bounds> + Clone) -> Bounds {
    std::array::from_fn(|i| {
        let values = members.clone().map(|m| m[i]);
        if i % 2 == 0 { values.fold(f64::INFINITY, f64::min) } else { values.fold(f64::NEG_INFINITY, f64::max) }
    })
}
