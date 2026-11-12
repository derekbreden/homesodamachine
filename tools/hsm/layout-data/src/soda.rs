use crate::*;

const HOLDER_ACCEPTANCE: &str = "future/tube-bend-holder-exploration/prints/2026-10-23-legs-123-w2-petgf-left04-z018-mark1/physical-result.json";
const FOAM_EVIDENCE: &str =
    "hardware/reference/cargen-pipe-insulation/elbow-fit-2026-10-24/physical-observation.json";

pub fn tail(control: &[V3], t: f64) -> Vec<V3> {
    let mut row = control.to_vec();
    let mut tails = vec![*row.last().unwrap()];
    while row.len() > 1 {
        row = row
            .windows(2)
            .map(|w| std::array::from_fn(|i| (1. - t) * w[0][i] + t * w[1][i]))
            .collect();
        tails.push(*row.last().unwrap());
    }
    tails.reverse();
    tails
}
fn transition(a: V3, b: V3) -> Value {
    let third = (b[2] - a[2]) / 3.;
    bezier(&[a, add(a, [0., 0., third]), add(b, [0., 0., -third]), b])
}
pub fn plan(spec: &Value) -> Result<Value> {
    let selected = &spec["soda_inlet"];
    let holder = &selected["holder"];
    let foam = &selected["foam"];
    let meter = &spec["parts"]["digiten-flow"];
    let mouth = point(meter, [-30.5, 0., 0.])?;
    let forward = vector(&meter["rotation"], [1., 0., 0.])?;
    let up = [0., 0., 1.];
    let radius = number(&holder["centreline_bend_r_mm"])?;
    let leg = number(&holder["leg_mm"])?;
    let gap = number(&selected["holder_to_meter_mm"])?;
    let end = add(mouth, mul(forward, -leg - gap));
    let centre = add(end, mul(up, -radius));
    let start = add(centre, mul(forward, -radius));
    let middle = add(
        centre,
        add(
            mul(forward, -radius / 2f64.sqrt()),
            mul(up, radius / 2f64.sqrt()),
        ),
    );
    let guide = xyz(&spec["cap_guides_world_mm"]["carb-water-out"])?;
    let xaxis = mul(forward, -1.);
    let zaxis = [xaxis[1], -xaxis[0], 0.];
    let rotation: Vec<_> = (0..3).map(|i| [xaxis[i], up[i], zaxis[i]]).collect();
    let zc = number(&holder["wall_mm"])? + number(&holder["channel_d_mm"])? / 2.;
    let translation = add(centre, mul(zaxis, -zc));
    let insertion = number(&selected["meter_insertion_estimate_mm"])?;
    let inserted = add(mouth, mul(forward, insertion));
    let transition = transition(guide, start);
    let controls = points3(&transition["control_points_mm"])?;
    let foam_t = number(&foam["start_above_guide_mm"])? / (start[2] - guide[2]);
    let foam_controls = tail(&controls, foam_t);
    let foam_end = add(mouth, mul(forward, -number(&foam["end_before_meter_mm"])?));
    let arc = json!({"kind":"arc","points_mm":[start,middle,end],"radius_mm":radius,"center_mm":centre,
        "axis":[-forward[1],forward[0],0.],"angle_rad":PI/2.});
    let tube_segments = vec![transition, arc.clone(), line(end, inserted)];
    let foam_segments = vec![bezier(&foam_controls), arc, line(end, foam_end)];
    let samples: Vec<_> = (0..129)
        .map(|i| tail(&foam_controls, i as f64 / 128.)[0])
        .collect();
    let curve_length: f64 = samples.windows(2).map(|w| norm(sub(w[0], w[1]))).sum();
    let foam_length = curve_length + radius * PI / 2. + norm(sub(end, foam_end));
    let offset = (start[0] - guide[0]).hypot(start[1] - guide[1]);
    let transition_radius = if offset != 0. {
        json!((start[2] - guide[2]).powi(2) / (6. * offset))
    } else {
        Value::Null
    };
    Ok(
        json!({"selection":selected["selection"],"holder":holder,"physical_acceptance":HOLDER_ACCEPTANCE,
        "foam_fit_evidence":FOAM_EVIDENCE,"core_guide_mm":guide,"guide_outward":up,
        "meter_mouth_mm":mouth,"meter_insertion_mm":insertion,
        "meter_insertion_basis":"Nominal DIGITEN layout estimate; actual receiving depth is unmeasured.",
        "flow_axis":forward,"arc_start_mm":start,"bend_center_mm":centre,"arc_mid_mm":middle,"arc_end_mm":end,
        "holder_rotation":rotation,"holder_translation_mm":translation,"holder_to_meter_mm":gap,
        "tube_segments":tube_segments,"foam_segments":foam_segments,"tube_od_mm":selected["tube_od_mm"],
        "tube_id_mm":selected["tube_id_mm"],"nominal_foam_id_mm":foam["stock_id_mm"],
        "nominal_foam_od_mm":foam["stock_od_mm"],"nominal_foam_cut_length_mm":foam_length,
        "guide_transition_minimum_radius_lower_bound_mm":transition_radius,"foam_cut_mm":foam["square_cut_mm"],
        "accepted_soft_neighbors":["vk-solenoid","g-ganen-pump","suction-tube","suction-barb-clamp"],
        "foam_model_scope":foam["occupied_model_scope"],"assembly":selected["assembly"]}),
    )
}
pub fn tube(spec: &Value) -> Result<Value> {
    let p = plan(spec)?;
    let centre = xyz(&p["bend_center_mm"])?;
    let forward = xyz(&p["flow_axis"])?;
    let control = points3(&p["tube_segments"][0]["control_points_mm"])?;
    let mut points: Vec<_> = (0..33).map(|i| tail(&control, i as f64 / 32.)[0]).collect();
    let radius = number(&p["holder"]["centreline_bend_r_mm"])?;
    for i in 1..33 {
        let angle = i as f64 * PI / 64.;
        points.push(add(
            centre,
            add(
                mul(forward, -radius * angle.cos()),
                [0., 0., radius * angle.sin()],
            ),
        ));
    }
    points.push(xyz(&p["tube_segments"][2]["points_mm"][1])?);
    Ok(
        json!({"points_mm":points,"centerline_mm":points,"segments":p["tube_segments"],"od_mm":p["tube_od_mm"],
        "id_mm":p["tube_id_mm"],"radius_mm":radius,"minimum_radius_mm":radius,"spool":"blue",
        "from":"foam-assembly.carb-water-out","frm":"foam-assembly.carb-water-out","to":"digiten-flow.inlet",
        "owners":["foam-assembly","digiten-flow"],"status":"selected_native_layout",
        "note":"Continuous soda tube through the plain guide and accepted R14 holder into the meter; the guide adds no insertion, joint or cut."}),
    )
}
