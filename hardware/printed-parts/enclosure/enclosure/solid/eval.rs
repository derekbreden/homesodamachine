//! A construction plan evaluated in this process: each reachable operation in graph order, each
//! intermediate released once its last user is built.
use crate::letters;
use crate::ops;
use crate::plan::{Graph, Node, Op, Shape};
use crate::snap_geometry;
use crate::structure::Silhouette;
use anyhow::{Context, Result};
use hsm_kernel::*;

/// The solids of `outputs`, in their order. A plan with a silhouette takes it from `silhouette`.
pub fn evaluate(g: &Graph, outputs: &[Shape], silhouette: Option<&Silhouette>) -> Result<Vec<Solid>> {
    let count = g.nodes.len();
    let mut reachable = vec![false; count];
    let mut stack: Vec<usize> = outputs.iter().map(|s| s.index).collect();
    while let Some(i) = stack.pop() {
        if !reachable[i] {
            reachable[i] = true;
            stack.extend(&g.nodes[i].inputs);
        }
    }
    let mut users = vec![0_usize; count];
    for output in outputs {
        users[output.index] += 1;
    }
    for (node, _) in g.nodes.iter().zip(&reachable).filter(|(_, r)| **r) {
        for &input in &node.inputs {
            users[input] += 1;
        }
    }
    let mut live: Vec<Option<Solid>> = vec![None; count];
    for i in (0..count).filter(|&i| reachable[i]) {
        let node = &g.nodes[i];
        let shape = build(node, &live, silhouette)
            .with_context(|| format!("enclosure node {i} ({})", name(&node.op)))?;
        live[i] = Some(shape);
        for &k in &node.inputs {
            users[k] -= 1;
            if users[k] == 0 {
                live[k] = None;
            }
        }
    }
    outputs
        .iter()
        .map(|output| {
            users[output.index] -= 1;
            let solid = if users[output.index] == 0 { live[output.index].take() } else { live[output.index].clone() };
            solid.context("a finished plan output")
        })
        .collect()
}

/// The first operation reachable from `from` that `pick` takes, in graph order.
pub fn find(g: &Graph, from: Shape, pick: impl Fn(&Op) -> bool) -> Option<Shape> {
    let mut reachable = vec![false; g.nodes.len()];
    let mut stack = vec![from.index];
    while let Some(i) = stack.pop() {
        if !reachable[i] {
            reachable[i] = true;
            stack.extend(&g.nodes[i].inputs);
        }
    }
    (0..g.nodes.len()).find(|&i| reachable[i] && pick(&g.nodes[i].op)).map(|index| Shape { index, bounds: None })
}

fn build(node: &Node, live: &[Option<Solid>], silhouette: Option<&Silhouette>) -> Result<Solid> {
    let inputs = &node.inputs;
    let input = |k: usize| live[inputs[k]].as_ref().expect("a referenced solid is live");
    Ok(match &node.op {
        Op::Empty => Solid::empty(),
        Op::Silhouette => silhouette.context("a silhouette for this plan")?.get()?.clone(),
        Op::Box(b) => {
            let (lo, hi) = ops::corners(b);
            Solid::cuboid(lo, hi)
        }
        Op::RoundedBox { b, radius } => ops::rounded_box(b, *radius)?,
        Op::Cylinder { axis, radius, centre, span, stations: None } => ops::cylinder(*axis, *radius, *centre, *span)?,
        Op::Cylinder { axis, radius, centre, span, stations: Some(stations) } => {
            ops::stationed_cylinder(*axis, *radius, *centre, *span, *stations)?
        }
        Op::Cone { axis, centre, radii, span } => ops::cone(*axis, *centre, *radii, *span)?,
        Op::Prism { axis, span, section } => ops::prism(*axis, *span, section, None, None)?,
        Op::CornerPrism { axis, span, section, corners, radius, offset } => {
            ops::prism(*axis, *span, section, Some((corners.as_slice(), *radius)), *offset)?
        }
        Op::HandholdCutter { b, radius } => ops::handhold_cutter(b, *radius)?,
        Op::HandholdFinishAir(h) => ops::handhold_air(h)?,
        Op::FlankVents(v) => {
            let tools: Vec<&Solid> = (1..inputs.len()).map(input).collect();
            ops::flank_vents(v, input(0), &tools)?
        }
        Op::BezierPrism { axis, span, segments } => ops::bezier_prism(*axis, *span, segments)?,
        Op::ArcPrism { axis, span, start, segments } => ops::arc_prism(*axis, *span, *start, segments)?,
        Op::RuledStack { sections, source } => ops::ruled_stack(sections, *source)?,
        Op::InletFlange(f) => ops::flange(f)?,
        Op::TurnedRuns { centre, profile } => ops::turned(*centre, profile)?,
        Op::RadialProfile { points } => ops::radial_profile(points)?,
        Op::StadiumX { y, z, radius, fore, aft, span } => ops::stadium(*y, *z, *radius, *fore, *aft, *span)?,
        Op::StadiumProfileX { y, z, fore, aft, points } => ops::stadium_profile(*y, *z, *fore, *aft, points)?,
        Op::NameplateStock(s) => snap_geometry::snap_receiver_stock(s)?,
        Op::NameplateCuts(s) => snap_geometry::snap_receiver_cuts(s)?,
        Op::DisposalLetters(l) => letters::disposal(l)?,
        op @ (Op::Union | Op::Cut | Op::Intersect) => {
            let mut s = input(0).clone();
            for k in 1..inputs.len() {
                s = match op {
                    Op::Union => s.union(input(k))?,
                    Op::Cut => s.cut(input(k))?,
                    _ => s.intersect(input(k))?,
                };
            }
            s
        }
        Op::Translate(d) => input(0).translate(v3(d[0], d[1], d[2])),
        Op::Rotate { origin, end, angle } => {
            let origin = v3(origin[0], origin[1], origin[2]);
            input(0).rotate(origin, v3(end[0], end[1], end[2]) - origin, *angle)
        }
        Op::Mirror(axis) => {
            let mut a = [0.; 3];
            a[*axis] = 1.;
            input(0).mirror(V3::ZERO, V3::from(a))
        }
        Op::Placed { rotation: r, translation: t } => {
            let column = |k: usize| v3(r[0][k], r[1][k], r[2][k]);
            input(0).transformed(&Affine::from_columns(column(0), column(1), column(2), v3(t[0], t[1], t[2])))
        }
    })
}

fn name(op: &Op) -> &'static str {
    match op {
        Op::Empty => "empty",
        Op::Silhouette => "silhouette",
        Op::Box(_) => "box",
        Op::RoundedBox { .. } => "rounded-box",
        Op::Cylinder { .. } => "cylinder",
        Op::Cone { .. } => "cone",
        Op::Prism { .. } => "prism",
        Op::CornerPrism { .. } => "corner-prism",
        Op::HandholdCutter { .. } => "handhold-cutter",
        Op::HandholdFinishAir(_) => "handhold-finish-air",
        Op::FlankVents(_) => "flank-vents",
        Op::BezierPrism { .. } => "bezier-prism",
        Op::ArcPrism { .. } => "arc-prism",
        Op::RuledStack { .. } => "ruled-stack",
        Op::InletFlange(_) => "inlet-flange",
        Op::TurnedRuns { .. } => "turned-runs",
        Op::RadialProfile { .. } => "radial-profile",
        Op::StadiumX { .. } => "stadium-x",
        Op::StadiumProfileX { .. } => "stadium-profile-x",
        Op::NameplateStock(_) => "nameplate-stock",
        Op::NameplateCuts(_) => "nameplate-cuts",
        Op::DisposalLetters(_) => "disposal-letters",
        Op::Union => "union",
        Op::Cut => "cut",
        Op::Intersect => "intersect",
        Op::Translate(_) => "translate",
        Op::Rotate { .. } => "rotate",
        Op::Mirror(_) => "mirror",
        Op::Placed { .. } => "placed",
    }
}
