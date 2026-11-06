//! What the above-core layout puts on the top pieces: the wiring's Wago wells on both, and on
//! back-top the rear wall's openings and identification, its wall hosts, valve seats and fluid
//! supports.
use crate::plan::{Bounds, Graph, P3, Shape};
use crate::quadrant::Y;
use crate::shapes::place;
use crate::shell::back_top_wall_face;
use crate::spec::Box;

/// A Wago 221 lever connector, by its body: across its poles, along its wire axis, and its height.
#[derive(Clone, Copy)]
struct Wago {
    width: f64,
    depth: f64,
    height: f64,
}

const WAGO_413: Wago = Wago { width: 18.8, depth: 18.6, height: 8.4 };
const WAGO_415: Wago = Wago { width: 30.0, depth: 18.6, height: 8.4 };
const WAGO_420: Wago = Wago { width: 29.8, depth: 18.3, height: 15.8 };

/// A well's stock round its pocket, and the connector's fit in that pocket.
const WELL_WALL: f64 = 3.0;
const WELL_FIT: f64 = 0.15;

/// The plane back-top's wells reach back to inside the rear wall.
const REAR_WELL_BACK_Y: f64 = 466.95;

/// The wiring model's frames, by rotation rows: lever ports fore, the same stood on end, and
/// lying on the east flank.
const PORTS_FORE: [P3; 3] = [[-1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]];
const UPRIGHT_PORTS_FORE: [P3; 3] = [[0.0, 0.0, 1.0], [0.0, -1.0, 0.0], [1.0, 0.0, 0.0]];
const EAST_FLANK: [P3; 3] = [[0.0, -1.0, 0.0], [0.0, 0.0, -1.0], [1.0, 0.0, 0.0]];

/// One junction the wiring model mounts on a top piece: its connector, where it stands, and how
/// far its well's mouth stands back of the lever face.
struct Junction {
    name: &'static str,
    wago: Wago,
    host: Y,
    rotation: [P3; 3],
    translation: P3,
    mouth: f64,
}

/// The wiring model's junctions on the two top pieces, in its placement order: the mains live,
/// earth and neutral buses under the ceiling PSU, and the two valve-manifold commons.
const JUNCTIONS: [Junction; 5] = [
    Junction { name: "wago-h", wago: WAGO_413, host: Y::Back, rotation: PORTS_FORE,
               translation: [-85.0, 456.5, 264.0], mouth: 0.0 },
    Junction { name: "wago-g", wago: WAGO_413, host: Y::Back, rotation: PORTS_FORE,
               translation: [-85.0, 457.5, 296.5], mouth: 0.0 },
    Junction { name: "wago-n", wago: WAGO_413, host: Y::Back, rotation: UPRIGHT_PORTS_FORE,
               translation: [-69.4, 456.5, 267.5], mouth: 0.0 },
    Junction { name: "wago-mana", wago: WAGO_420, host: Y::Front, rotation: EAST_FLANK,
               translation: [95.20, 185.05, 277.0], mouth: -0.75 },
    Junction { name: "wago-manb", wago: WAGO_415, host: Y::Front, rotation: EAST_FLANK,
               translation: [95.05, 177.65, 243.0], mouth: -0.75 },
];

fn junction(name: &str) -> &'static Junction {
    JUNCTIONS.iter().find(|j| j.name == name).expect("the wiring model places this junction")
}

/// The piece with every above-core feature it carries, and the wells' pockets, which back-top's
/// rear wall keeps clear of.
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
/// and the pocket it inserts into butt first. Back-top's wells reach back into the rear wall,
/// and each connected cluster of them roofs over to the wall.
fn wells(g: &mut Graph, host: Y) -> (Vec<Shape>, Vec<Shape>) {
    let (wall, fit) = (WELL_WALL, WELL_FIT);
    let mut stocks = Vec::new();
    let mut pockets = Vec::new();
    for j in JUNCTIONS.iter().filter(|j| j.host == host) {
        let Wago { width: w, depth: d, height: h } = j.wago;
        let mut rear = -d / 2.0 - fit - wall;
        if host == Y::Back {
            rear = rear.min(j.translation[1] - REAR_WELL_BACK_Y);
        }
        let stock = g.box_([-w / 2.0 - fit - wall, w / 2.0 + fit + wall, rear, j.mouth, -fit - wall, h + fit + wall]);
        stocks.push(place(g, stock, j.rotation, j.translation));
        let pocket = g.box_([-w / 2.0 - fit, w / 2.0 + fit, -d / 2.0 - fit, 1.0, -fit, h + fit]);
        pockets.push(place(g, pocket, j.rotation, j.translation));
    }
    if host == Y::Back {
        let roofs = rear_roofs(&stocks);
        let wall_y = back_top_wall_face() + 0.5;
        let neutral = junction("wago-n").translation;
        let live = stocks[JUNCTIONS.iter().filter(|j| j.host == Y::Back).position(|j| j.name == "wago-h")
            .expect("the live bus stands on back-top")].bounds();
        for (stock, roof) in stocks.iter_mut().zip(roofs) {
            let Some([x0, x1, y0, _, z0, z1]) = roof else { continue };
            let run = (wall_y - y0).max(0.0);
            if run == 0.0 {
                continue;
            }
            let cluster = x0 <= neutral[0] && neutral[0] <= x1 && z0 <= neutral[2] && neutral[2] <= z1;
            let top = if cluster { z1 } else { z1 + run };
            let bottom = if cluster { (z1 - wall).min(live[5]) } else { z1 - wall };
            let roof = g.prism(0, x0, x1, vec![[y0, bottom], [y0, z1], [wall_y, top], [wall_y, bottom]]);
            *stock = g.union(*stock, &[roof]);
        }
    }
    (stocks, pockets)
}

/// The roof each rear well carries to the wall: a lone well its own bounds, the first well of
/// a cluster of overlapping wells the cluster's, the rest of the cluster none.
fn rear_roofs(stocks: &[Shape]) -> Vec<Option<Bounds>> {
    let boxes: Vec<Bounds> = stocks.iter().map(|s| s.bounds()).collect();
    for (i, a) in boxes.iter().enumerate() {
        for b in &boxes[i + 1..] {
            let overlap: Vec<f64> = (0..3).map(|k| a[2 * k + 1].min(b[2 * k + 1]) - a[2 * k].max(b[2 * k])).collect();
            assert!(!(overlap.iter().all(|&v| v >= 0.0) && overlap.iter().any(|&v| v == 0.0)),
                    "touching rear well stocks need a joint of their own");
        }
    }
    let overlaps = |a: &Bounds, b: &Bounds| (0..3).all(|k| a[2 * k + 1].min(b[2 * k + 1]) - a[2 * k].max(b[2 * k]) > 0.0);
    let mut roofs: Vec<Option<Option<Bounds>>> = vec![None; boxes.len()];
    for start in 0..boxes.len() {
        if roofs[start].is_some() {
            continue;
        }
        let mut group = vec![start];
        let mut pending = vec![start];
        while let Some(current) = pending.pop() {
            for other in 0..boxes.len() {
                if other != current && !group.contains(&other) && overlaps(&boxes[current], &boxes[other]) {
                    group.push(other);
                    pending.push(other);
                }
            }
        }
        if group.len() == 1 {
            roofs[start] = Some(Some(boxes[start]));
            continue;
        }
        let hull = hull(group.iter().map(|&m| &boxes[m]));
        for &member in &group {
            roofs[member] = Some(if member == start { Some(hull) } else { None });
        }
    }
    roofs.into_iter().map(|r| r.expect("every well has its roof decided")).collect()
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
