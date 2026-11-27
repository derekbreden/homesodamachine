//! What the above-core layout puts on the top pieces: the wiring's Wago wells on both, and on
//! back-top the rear wall's openings and identification, its wall hosts, valve seats and fluid
//! supports.
use crate::catalog;
use crate::plan::{Bounds, Graph, Shape};
use crate::quadrant::Y;
use crate::shapes::place;
use crate::faces::back_top_flank_face;
use crate::shell::{back_top_ceiling_face, LIP_LEN, WAGO_WELL_WALL};
use crate::spec::Box;
use crate::junctions::{final_join_id, junctions, Junction, Wago};

/// The piece with every above-core feature it carries, and the wells' pockets, which back-top's
/// wall features keep clear of.
pub fn apply(g: &mut Graph, mut piece: Shape, b: &Box, col: Y) -> (Shape, Option<Shape>) {
    let wells = wells(g, col);
    let mut stocks: Vec<_> = wells.iter().map(|w| w.stock).collect();
    let pockets: Vec<_> = wells.iter().map(|w| w.pocket).collect();
    let row: Vec<_> = wells.iter().filter(|w| final_join_id(&w.junction.name).is_some()).collect();
    if !row.is_empty() {
        let bounds: Vec<_> = row.iter().map(|w| w.stock.bounds()).collect();
        let [_, face, _, aft, bottom, _] = hull(bounds.iter());
        let bank = g.box_([back_top_flank_face()[0], face, b.y_joint + LIP_LEN, aft, bottom, back_top_ceiling_face()]);
        let parts: Vec<_> = row.iter().map(|w| w.junction.name.as_str()).collect();
        stocks.push(g.feature(bank, "west-final-join-bank", "West final connections from seam rib to roof", &parts));
    }
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

struct Well {
    junction: &'static Junction,
    stock: Shape,
    pocket: Shape,
}

/// Each junction's well on this top piece: closed stock round the connector's blank rear half,
/// and the pocket it inserts into butt first. Back-top seats its row against the west wall;
/// front-top carries its wells on the manifold towers.
fn wells(g: &mut Graph, host: Y) -> Vec<Well> {
    let wall = WAGO_WELL_WALL;
    let mut wells = Vec::new();
    for j in junctions().iter().filter(|j| j.host == host) {
        let fit = j.fit;
        let Wago { width: w, depth: d, height: h, .. } = j.wago;
        let rear = -d / 2.0 - fit - wall;
        // Back-top prints ceiling down. Local width runs along installed Z in both rear
        // banks, with opposite signs. Relieve only the supported face and carry its backing.
        let relief = match host {
            Y::Back => -j.rotation[2][0] * catalog::supported(),
            Y::Front => 0.0,
        };
        let left = -w / 2.0 + relief.min(0.0);
        let right = w / 2.0 + relief.max(0.0);
        let stock = g.box_([left - fit - wall, right + fit + wall, rear, j.mouth, -fit - wall, h + fit + wall]);
        let stock = place(g, stock, j.rotation, j.translation);
        let stock = g.feature(stock, format!("{}-well", j.name), format!("{} connector well", j.name), &[&j.name]);
        let width_fit = fit - j.well_width_inset;
        let height_fit = fit - j.well_height_inset;
        let pocket = g.box_([
            left - width_fit, right + width_fit,
            -d / 2.0 - fit, 1.0,
            -height_fit, h + height_fit,
        ]);
        let pocket = place(g, pocket, j.rotation, j.translation);
        let pocket = g.feature(pocket, format!("{}-well", j.name), format!("{} connector well", j.name), &[&j.name]);
        wells.push(Well { junction: j, stock, pocket });
    }
    wells
}

/// Each well's closed stock on this top piece, for the ceiling pocket that runs round it.
pub fn stock_bounds(host: Y) -> Vec<Bounds> {
    let mut graph = Graph::new();
    wells(&mut graph, host).into_iter().map(|w| w.stock.bounds()).collect()
}

/// Each insertion pocket in the enclosure frame, for its host's support and bridge settings.
pub fn pocket_regions(host: Y) -> Vec<(String, Bounds)> {
    let mut graph = Graph::new();
    wells(&mut graph, host).into_iter().map(|w| {
        (format!("{} insertion pocket", w.junction.name), w.pocket.bounds())
    }).collect()
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
