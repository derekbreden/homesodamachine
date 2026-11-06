//! Back-top: the back half over the seam, the section its flanks, rear wall and ceiling carry
//! beyond `WALL`, then the quadrant's features, and the lands its fluted print keeps plain.
use crate::field::{Rail, perimeter_rail};
use crate::funnel::{cut_plan, funnel_cut, housing_back_y};
use crate::piece::Build;
use crate::plan::{Graph, Shape};
use crate::quadrant::Quadrant;
use crate::rear::{self, BackTopPrint};
use crate::shell::{BACK_TOP_FLANK_T, BACK_TOP_WALL_T, HOOK_FOOT, STATED_BOUND_TOL, WALL, Z_RISE, back_top_ceiling_face, back_top_wall_face};
use crate::spec::Box;
use crate::walls::{back_flank_start, back_top_flank_face, cavity};

/// Back-top as its files are written: the construction and its solid, the nameplate receiver's
/// field the print keeps plain, the print rail, and the print's raised lands.
pub struct BackTop {
    pub graph: Graph,
    pub result: Shape,
    pub receiver_field: Shape,
    pub rails: Vec<Rail>,
    pub print: BackTopPrint,
}

/// Back-top's construction: the shell's back half over the seam, less the funnel's air, then
/// the quadrant's features.
pub fn construction(b: &Box) -> BackTop {
    assert!(housing_back_y(b.pack.funnel[1]) < b.y_joint, "the display housing reaches into back-top");
    let mut g = Graph::new();
    let o = b.outer;
    let silhouette = g.silhouette(o);
    let air = cavity(&mut g, &b.inner, 0.0, None);
    let shell = g.cut(silhouette, &[air]);
    let band = g.box_([o[0], o[1], b.y_joint, o[3], b.splits[1], o[5]]);
    let half = g.intersect(shell, &[band]);
    let funnel = funnel_cut(&mut g, &b.inner, &o, b.pack.funnel);
    let half = g.cut(half, &[funnel]);
    let result = crate::pipeline(&mut g, &Build { b, q: Quadrant::BACK_TOP, silhouette, half });
    let receiver_field = rear::receiver_field(&mut g);
    let rails = vec![perimeter_rail(&o, rear::back_top_plain(&o))];
    BackTop { graph: g, result, receiver_field, rails, print: rear::print() }
}

/// The section the ±X flanks carry beyond `WALL`, from past the Y telescope to the lane. With
/// `up` negative the piece prints on its ceiling and the section stands square from the rail
/// foot's caught face; with `up` positive it starts over the rail's rim and its underside rises
/// across the section.
pub fn flanks(g: &mut Graph, b: &Box, zj: f64, up: f64) -> Shape {
    let [ix0, ix1, _, iy1, _, iz1] = b.inner;
    let [fx0, fx1] = back_top_flank_face();
    let y0 = back_flank_start(b.y_joint);
    let rim = if up > 0.0 { zj + Z_RISE } else { zj + HOOK_FOOT };
    let depth = BACK_TOP_FLANK_T - WALL;
    let sides: Vec<Shape> = [(ix0, fx0), (ix1, fx1)]
        .into_iter()
        .map(|(x_in, x_face)| {
            let side = g.box_([x_in.min(x_face), x_in.max(x_face), y0, iy1, rim, iz1]);
            if up > 0.0 {
                let rise = g.xz_prism(y0 - 1.0, iy1 + 1.0, vec![[x_in, rim], [x_face, rim], [x_face, rim + depth]]);
                g.cut(side, &[rise])
            } else {
                side
            }
        })
        .collect();
    g.union(sides[0], &sides[1..])
}

/// The section the +Y wall carries beyond `WALL`, inboard of the rear plane. Printed on its
/// ceiling it starts square on the seam; printed on its rim it starts over the rail's rim and
/// rises across the section, the way the flanks that turn out of it do.
pub fn wall(g: &mut Graph, b: &Box, zj: f64, up: f64) -> Shape {
    let [ix0, ix1, _, iy1, _, iz1] = b.inner;
    let face = back_top_wall_face();
    let rim = zj + Z_RISE;
    let band = g.box_([ix0, ix1, face, iy1, if up < 0.0 { zj } else { rim }, iz1]);
    if up > 0.0 {
        let rise = g.yz_prism(ix0 - 1.0, ix1 + 1.0, vec![[iy1, rim], [face, rim], [face, rim + (BACK_TOP_WALL_T - WALL)]]);
        g.cut(band, &[rise])
    } else {
        band
    }
}

/// The ceiling slab fused on: the stock between the flank faces from past the Y telescope to the
/// wall face, less the funnel's plan and every body pocket the pack asks of it.
pub fn ceiling(g: &mut Graph, piece: Shape, b: &Box) -> Shape {
    let lane = b.inner[5];
    let face = back_top_ceiling_face();
    let [fx0, fx1] = back_top_flank_face();
    let mut stock = g.box_([fx0, fx1, back_flank_start(b.y_joint), back_top_wall_face(), face, lane + 1.0]);
    let [x0, x1, y0, y1] = cut_plan(b.pack.funnel);
    let funnel = g.box_([x0, x1, y0 - 1.0, y1, face - 1.0, lane + 2.0]);
    stock = g.cut(stock, &[funnel]);
    for [x0, x1, y0, y1, top] in pockets(&b.pack.ceiling_reliefs) {
        let roof = top.min(lane);
        if roof > face + STATED_BOUND_TOL {
            let pocket = g.box_([x0, x1, y0, y1, face - 1.0, roof]);
            stock = g.cut(stock, &[pocket]);
        }
    }
    g.union(piece, &[stock])
}

/// Each body's ceiling pocket, `[x0, x1, y0, y1, top]`. One that runs on out of another body's
/// pocket under the same roof, its two sides standing less than a wall inside that pocket's,
/// takes that pocket's sides, so no sub-wall step stands at either end of it.
fn pockets(reliefs: &[(String, f64, f64, f64, f64, f64)]) -> Vec<[f64; 5]> {
    reliefs
        .iter()
        .map(|(who, x0, x1, y0, y1, top)| {
            assert!(who != "c14-inlet", "the C14 inlet's ceiling pocket has no construction");
            let mut plan = [*x0, *x1, *y0, *y1, *top];
            for (name, x0, x1, y0, y1, top) in reliefs {
                let other = [*x0, *x1, *y0, *y1, *top];
                if name == "c14-inlet"
                    || name == who
                    || (other[4] - plan[4]).abs() > STATED_BOUND_TOL
                    || other[1].min(plan[1]) <= other[0].max(plan[0])
                    || other[3].min(plan[3]) <= other[2].max(plan[2])
                {
                    continue;
                }
                for k in [0, 2] {
                    if other[k] <= plan[k]
                        && plan[k] < other[k] + WALL
                        && other[k + 1] - WALL < plan[k + 1]
                        && plan[k + 1] <= other[k + 1]
                    {
                        plan[k] = other[k];
                        plan[k + 1] = other[k + 1];
                    }
                }
            }
            plan
        })
        .collect()
}
