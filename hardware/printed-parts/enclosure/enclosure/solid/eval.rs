//! A construction plan reuses valid retained stages and evaluates the remaining operations in
//! graph order, releasing each intermediate after its last user.
use crate::letters;
use crate::ops;
use crate::plan::{Graph, Node, Op, Shape};
use crate::snap_geometry;
use crate::structure::Silhouette;
use anyhow::{Context, Result};
use hsm_kernel::*;

/// The solids of `outputs`, in their order. A plan with a silhouette takes it from `silhouette`.
pub fn evaluate(
    g: &Graph,
    outputs: &[Shape],
    silhouette: Option<&Silhouette>,
) -> Result<Vec<Solid>> {
    let started = std::time::Instant::now();
    let count = g.nodes.len();
    let mut potential = vec![false; count];
    let mut pending: Vec<usize> = outputs.iter().map(|output| output.index).collect();
    while let Some(i) = pending.pop() {
        if !potential[i] {
            potential[i] = true;
            pending.extend(&g.nodes[i].inputs);
        }
    }
    let mut cache = crate::cache::Cache::new();
    let mut keys = Vec::<String>::with_capacity(count);
    let mut candidates = vec![false; count];
    for (i, node) in g.nodes.iter().enumerate() {
        if !potential[i] {
            keys.push(String::new());
            continue;
        }
        let mut operation = serde_json::Value::Object(crate::plan::op_json(&node.op));
        if matches!(node.op, Op::Silhouette) {
            operation["structure"] =
                serde_json::to_value(silhouette.context("a silhouette for this plan")?.structure)?;
        }
        let inputs: Vec<&str> = node
            .inputs
            .iter()
            .map(|&input| keys[input].as_str())
            .collect();
        keys.push(crate::cache::Cache::key(
            &serde_json::to_vec(&operation)?,
            &inputs,
        ));
        candidates[i] = matches!(
            node.op,
            Op::Checkpoint(_) | Op::Silhouette | Op::SeamBand { .. } | Op::FlankVentCuts(_)
        );
    }
    for output in outputs {
        candidates[output.index] = true;
        if let Some((core, _)) = g.additive_parts(*output) {
            candidates[core.index] = true;
        }
    }
    let mut reachable = vec![false; count];
    let mut live: Vec<Option<Solid>> = vec![None; count];
    let mut stack: Vec<usize> = outputs.iter().map(|s| s.index).collect();
    while let Some(i) = stack.pop() {
        if !reachable[i] {
            reachable[i] = true;
            if candidates[i] {
                live[i] = cache.load(&keys[i]);
            }
            if live[i].is_none() {
                stack.extend(&g.nodes[i].inputs);
            }
        }
    }
    let mut users = vec![0_usize; count];
    for output in outputs {
        users[output.index] += 1;
    }
    for (_, node) in g
        .nodes
        .iter()
        .enumerate()
        .filter(|(i, _)| reachable[*i] && live[*i].is_none())
    {
        for &input in &node.inputs {
            users[input] += 1;
        }
    }
    let mut built = 0;
    let mut identities = 0;
    let mut timings = Vec::new();
    for i in (0..count).filter(|&i| reachable[i]) {
        if live[i].is_some() {
            continue;
        }
        let node = &g.nodes[i];
        let stage = std::time::Instant::now();
        let shape = if let Op::Feature(feature) = &node.op {
            identities += 1;
            let source = node.inputs[0];
            if users[source] == 1 {
                Ok(live[source].take().expect("live feature input").with_feature(feature))
            } else { build(node, &live, silhouette) }
        } else { build(node, &live, silhouette) }
            .with_context(|| format!("enclosure node {i} ({})", name(&node.op)))?;
        let seconds = stage.elapsed().as_secs_f64();
        built += 1;
        if seconds >= 0.01 {
            timings
                .push(serde_json::json!({"node":i,"operation":name(&node.op),"seconds":seconds}));
        }
        if candidates[i] {
            cache.save(&keys[i], &shape);
        }
        live[i] = Some(shape);
        for &k in &node.inputs {
            users[k] -= 1;
            if users[k] == 0 {
                live[k] = None;
            }
        }
    }
    let result = outputs
        .iter()
        .map(|output| {
            users[output.index] -= 1;
            let solid = if users[output.index] == 0 {
                live[output.index].take()
            } else {
                live[output.index].clone()
            };
            solid.context("a finished plan output")
        })
        .collect();
    if let Some(path) = std::env::var_os("HSM_STAGE_PROFILE") {
        let report = serde_json::json!({"seconds":started.elapsed().as_secs_f64(),"nodes":count,"built":built,
            "identity_nodes":identities,"geometry_built":built-identities,
            "implementation":env!("HSM_STAGE_IMPLEMENTATION"),
            "reused":cache.hits,"stored":cache.stored,"bytes_read":cache.bytes_read,"bytes_written":cache.bytes_written,
            "cache_io_seconds":cache.io_seconds,"stages":timings});
        std::fs::write(path, serde_json::to_vec_pretty(&report)?)?;
    }
    result
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
    (0..g.nodes.len())
        .find(|&i| reachable[i] && pick(&g.nodes[i].op))
        .map(|index| Shape {
            index,
            bounds: None,
        })
}

fn build(node: &Node, live: &[Option<Solid>], silhouette: Option<&Silhouette>) -> Result<Solid> {
    let inputs = &node.inputs;
    let input = |k: usize| {
        live[inputs[k]]
            .as_ref()
            .expect("a referenced solid is live")
    };
    Ok(match &node.op {
        Op::Empty => Solid::empty(),
        Op::Silhouette => silhouette
            .context("a silhouette for this plan")?
            .get()?
            .clone(),
        Op::SeamBand {
            outer,
            centre,
            exterior,
        } => crate::exterior::band(*outer, *centre, *exterior)?,
        Op::Checkpoint(_) => input(0).clone(),
        Op::Feature(feature) => input(0).clone().with_feature(feature),
        Op::Box(b) => {
            let (lo, hi) = ops::corners(b);
            Solid::cuboid(lo, hi)
        }
        Op::RoundedBox { b, radius } => ops::rounded_box(b, *radius)?,
        Op::Cylinder {
            axis,
            radius,
            centre,
            span,
            stations: None,
        } => ops::cylinder(*axis, *radius, *centre, *span)?,
        Op::Cylinder {
            axis,
            radius,
            centre,
            span,
            stations: Some(stations),
        } => ops::stationed_cylinder(*axis, *radius, *centre, *span, *stations)?,
        Op::Cone {
            axis,
            centre,
            radii,
            span,
        } => ops::cone(*axis, *centre, *radii, *span)?,
        Op::Prism {
            axis,
            span,
            section,
        } => ops::prism(*axis, *span, section, None, None)?,
        Op::CornerPrism {
            axis,
            span,
            section,
            corners,
            radius,
            offset,
        } => ops::prism(
            *axis,
            *span,
            section,
            Some((corners.as_slice(), *radius)),
            *offset,
        )?,
        Op::HandholdCutter { b, radius } => ops::handhold_cutter(b, *radius)?,
        Op::HandholdFinishAir(h) => ops::handhold_air(h)?,
        Op::FlankVentCuts(v) => {
            let tools: Vec<&Solid> = (1..inputs.len()).map(input).collect();
            ops::flank_vent_cuts(v, input(0), &tools)?
        }
        Op::BezierPrism {
            axis,
            span,
            segments,
        } => ops::bezier_prism(*axis, *span, segments)?,
        Op::ArcPrism {
            axis,
            span,
            start,
            segments,
        } => ops::arc_prism(*axis, *span, *start, segments)?,
        Op::RuledStack { sections, source } => ops::ruled_stack(sections, *source)?,
        Op::InletFlange(f) => ops::flange(f)?,
        Op::TurnedRuns { centre, profile } => ops::turned(*centre, profile)?,
        Op::RadialProfile { points } => ops::radial_profile(points)?,
        Op::StadiumX {
            y,
            z,
            radius,
            fore,
            aft,
            span,
        } => ops::stadium(*y, *z, *radius, *fore, *aft, *span)?,
        Op::StadiumProfileX {
            y,
            z,
            fore,
            aft,
            points,
        } => ops::stadium_profile(*y, *z, *fore, *aft, points)?,
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
        Op::Placed {
            rotation: r,
            translation: t,
        } => {
            let column = |k: usize| v3(r[0][k], r[1][k], r[2][k]);
            input(0).transformed(&Affine::from_columns(
                column(0),
                column(1),
                column(2),
                v3(t[0], t[1], t[2]),
            ))
        }
    })
}

fn name(op: &Op) -> &'static str {
    match op {
        Op::Empty => "empty",
        Op::Silhouette => "silhouette",
        Op::SeamBand { .. } => "seam band",
        Op::Checkpoint(_) => "checkpoint",
        Op::Feature(_) => "feature identity",
        Op::Box(_) => "box",
        Op::RoundedBox { .. } => "rounded-box",
        Op::Cylinder { .. } => "cylinder",
        Op::Cone { .. } => "cone",
        Op::Prism { .. } => "prism",
        Op::CornerPrism { .. } => "corner-prism",
        Op::HandholdCutter { .. } => "handhold-cutter",
        Op::HandholdFinishAir(_) => "handhold-finish-air",
        Op::FlankVentCuts(_) => "flank-vents",
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn edited_geometry_reuses_a_prefix_and_recovers_from_a_damaged_entry() -> Result<()> {
        let directory = std::env::temp_dir().join(format!("hsm-stage-edit-{}", std::process::id()));
        std::fs::create_dir_all(&directory)?;
        let profile = directory.join("profile.json");
        unsafe {
            std::env::set_var("HSM_STAGE_CACHE_DIR", &directory);
            std::env::set_var("HSM_STAGE_PROFILE", &profile);
        }
        let draw = |radius| -> Result<Solid> {
            let mut graph = Graph::new();
            let a = graph.box_([0.0, 30.0, 0.0, 20.0, 0.0, 10.0]);
            let b = graph.zcyl(6.0, 15.0, 10.0, 5.0, 18.0);
            let stock = graph.union(a, &[b]);
            let stock = graph.checkpoint("mount stock", stock);
            let tool = graph.zcyl(radius, 15.0, 10.0, -1.0, 20.0);
            let result = graph.cut(stock, &[tool]);
            Ok(evaluate(&graph, &[result], None)?.remove(0))
        };
        let bytes = |solid: &Solid| {
            hsm_kernel::model_bytes(&[Body {
                name: "part",
                color: None,
                solid,
            }])
        };
        let first = draw(2.0)?;
        let edited = draw(3.0)?;
        let report: serde_json::Value = serde_json::from_slice(&std::fs::read(&profile)?)?;
        assert!(report["reused"].as_u64().unwrap() > 0);
        assert!(edited.volume() < first.volume());
        unsafe {
            std::env::set_var("HSM_STAGE_CACHE_OFF", "1");
        }
        let fresh = draw(3.0)?;
        assert_eq!(bytes(&edited), bytes(&fresh));
        unsafe {
            std::env::remove_var("HSM_STAGE_CACHE_OFF");
        }
        for entry in std::fs::read_dir(&directory)? {
            let path = entry?.path();
            if path.extension().is_some_and(|extension| extension == "npz") {
                std::fs::write(path, b"interrupted entry")?;
            }
        }
        let recovered = draw(3.0)?;
        assert_eq!(bytes(&fresh), bytes(&recovered));
        unsafe {
            std::env::remove_var("HSM_STAGE_CACHE_DIR");
            std::env::remove_var("HSM_STAGE_PROFILE");
        }
        std::fs::remove_dir_all(directory)?;
        Ok(())
    }

    #[test]
    fn an_addition_takes_the_same_openings_and_joint_limits() -> Result<()> {
        let draw = |factored| -> Result<Solid> {
            let mut graph = Graph::new();
            let wall = graph.box_([0.0, 20.0, 0.0, 3.0, 0.0, 20.0]);
            let band = graph.box_([0.0, 20.0, 2.0, 6.0, 8.0, 12.0]);
            let stock = if factored {
                graph.additive(wall, band)
            } else {
                graph.union(wall, &[band])
            };
            let opening = graph.ycyl(2.0, 10.0, 10.0, -1.0, 8.0);
            let stock = graph.cut(stock, &[opening]);
            let limit = graph.box_([0.25, 19.75, -1.0, 8.0, 0.0, 20.0]);
            let result = graph.intersect(stock, &[limit]);
            Ok(evaluate(&graph, &[result], None)?.remove(0))
        };
        let direct = draw(false)?;
        let factored = draw(true)?;
        assert!((direct.volume() - factored.volume()).abs() < 1e-7);
        assert!(direct.cut(&factored)?.volume() < 1e-7);
        assert!(factored.cut(&direct)?.volume() < 1e-7);
        Ok(())
    }
}
