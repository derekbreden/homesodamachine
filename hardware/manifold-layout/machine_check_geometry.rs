//! Exact pairwise questions and their finite nominal receiving interfaces.
use super::*;
pub struct Readings {
    pub clashes: Vec<Value>,
    pub unanswered: Vec<Value>,
    pub contacts: Value,
    pub clearances: Vec<Value>,
    pub lanes: Vec<String>,
}
fn elbow_host(name: &str) -> String {
    let n = name.trim_start_matches("stem-elbow-");
    format!(
        "{}{n}",
        if n.starts_with("y-") {
            "tee-"
        } else {
            "valve-"
        }
    )
}
fn profile() -> Value {
    serde_json::from_str(include_str!(
        "../reference/neofit-stem-elbow/reference-parameters.json"
    ))
    .unwrap()
}
fn frame(m: &Value, name: &str) -> Result<Option<Affine>> {
    fine::transform(
        m["installed_frames"]
            .get(name)
            .or_else(|| m["frames"][name].get("transform")),
    )
}
fn port(m: &Value, host: &str, port: &str) -> Result<(V3, V3, f64)> {
    let row = m["frames"][host]
        .get("ports")
        .unwrap_or(&m["frames"][host])
        .get(port)
        .with_context(|| format!("missing port {host}.{port}"))?;
    if row.is_object() {
        Ok((
            vector(&row["pos"])?,
            vector(row.get("axis").unwrap_or(&row["normal"]))?,
            num(&row["diam"]),
        ))
    } else {
        Ok((vector(&row[0])?, vector(&row[1])?, num(&row[2])))
    }
}
fn plans(v: &Value) -> Vec<(String, Value)> {
    if v.is_object() {
        obj(v).into_iter().collect()
    } else {
        array(v)
            .iter()
            .enumerate()
            .map(|(i, v)| {
                (
                    v.get("name").map(string).unwrap_or_else(|| i.to_string()),
                    v.clone(),
                )
            })
            .collect()
    }
}
fn mate_regions(
    w: &World,
    m: &Value,
    pending: &BTreeSet<(String, String)>,
) -> Result<Vec<(String, String, Solid, String)>> {
    let mut out = Vec::new();
    let p = profile();
    let check: Value = serde_json::from_str(include_str!(
        "../reference/neofit-achv44-check/model-dimensions.json"
    ))?;
    let reducer: Value = serde_json::from_str(include_str!(
        "../reference/jg-pp061208w/reference-parameters.json"
    ))?;
    let reducer_depth = num(&reducer["length_mm"]) - num(&reducer["body_face_x_mm"])
        + num(&reducer["body_face_to_stop_display_mm"]);
    let mut stems = vec![
        ("tee-fold", "vk-solenoid", 12.7),
        ("reg-va-elbow", "valve-v-a", 12.7),
        ("va-outlet-elbow", "valve-v-a", 12.7),
        ("vb-inlet-turn", "valve-v-b", 12.7),
        ("vb-outlet-stem", "valve-v-b", 12.7),
        ("lower-valve-elbow", "vk-solenoid", 12.7),
        (
            "carbonator-fold",
            "discharge-chain",
            m["check_socket_outlet_depth"]
                .as_f64()
                .unwrap_or(num(&check["socket_insertion"]["outlet_mm"])),
        ),
        ("soda-stem-elbow", "bulkhead-carb", 12.7),
        ("ya-stem-elbow", "tee-y-a", 15.7),
        ("yb-stem-elbow", "tee-y-b", 15.7),
        (
            "va-south-elbow",
            "va-outlet-elbow",
            num(&p["published_socket_insertion_mm"]),
        ),
    ];
    stems.extend([
        ("reservoir-a-fill-turn", "valve-v-f", 12.7),
        ("reservoir-a-draw-turn", "valve-v-e", 12.7),
        ("reservoir-b-fill-turn", "valve-v-i", 12.7),
    ]);
    for (stem, host, depth) in stems {
        if !pending.contains(&pair(stem, host)) {
            continue;
        }
        let mut region = stem_region(&w.solid(stem)?, &p, false)?;
        if host.starts_with("valve-v-") || host == "vk-solenoid" {
            if let Some(frame) = frame(m, host)? {
                let inv = inverse_rigid(frame);
                for &i in &w.g(host)?.indices {
                    for s in w.parts[i].solid.components() {
                        let b = bounds(&s.transformed(&inv));
                        if (b[1] > 25.75 || b[4] < -25.75)
                            && b[0] >= -7.
                            && b[3] <= 7.
                            && b[2] >= 4.
                            && b[5] <= 18.1
                        {
                            region = region.union(&s)?;
                        }
                    }
                }
            }
        }
        out.push((stem.to_owned(),host.to_owned(),region,format!("Finite NeoFit male profile and own release-collet interface; selected {} mm engagement",pretty(depth))));
    }
    let tubes = [
        ("tube-fluid-16", "reservoir-a-draw-turn", "socket", 16.891),
        ("tube-fluid-14", "reservoir-a-fill-turn", "socket", 16.891),
        ("tube-fluid-26", "valve-v-h", "inlet", 12.7),
        ("tube-fluid-24", "reservoir-b-fill-turn", "socket", 16.891),
        (
            "tube-above-core-water-in",
            "bulkhead-water",
            "inboard",
            12.7,
        ),
        ("tube-soda-meter-bulkhead", "digiten-flow", "outlet", 15.7),
        ("tube-soda-meter-bulkhead", "bulkhead-carb", "tube-in", 15.7),
        ("tube-above-core-tee-vk-link", "water-split", "to-vk", 15.7),
        ("tube-above-core-tee-vk-link", "tee-fold", "socket", 16.891),
        (
            "tube-above-core-tee-regulator",
            "water-split",
            "to-flavor",
            15.7,
        ),
        (
            "tube-above-core-tee-regulator",
            "flow-regulator",
            "inlet",
            15.,
        ),
        ("tube-soda-core-rise", "digiten-flow", "inlet", 15.7),
        (
            "tube-above-core-pump-check-link",
            "discharge-chain",
            "inlet",
            m["check_socket_inlet_depth"]
                .as_f64()
                .unwrap_or(num(&check["socket_insertion"]["inlet_mm"])),
        ),
        (
            "tube-above-core-pump-inlet-link",
            "suction-reducer",
            "tube",
            m["reducer_tube_insertion_depth"]
                .as_f64()
                .unwrap_or(reducer_depth),
        ),
        (
            "tube-above-core-pump-inlet-link",
            "lower-pump-elbow",
            "socket",
            16.891,
        ),
    ];
    for (tube, host, port_name, depth) in tubes {
        if !pending.contains(&pair(tube, host)) {
            continue;
        }
        let (mouth, axis, diam) = port(m, host, port_name)?;
        let mut radius = diam / 2.;
        let mut basis = format!(
            "{host}.{port_name}: Ø{} × {} mm nominal insertion",
            pretty(diam),
            pretty(depth)
        );
        if [
            "tube-above-core-tee-vk-link",
            "tube-above-core-tee-regulator",
            "tube-above-core-pump-inlet-link",
        ]
        .contains(&tube)
        {
            let bend =
                m["native_route_specs"][tube.trim_start_matches("tube-")]["minimum_radius_mm"]
                    .as_f64();
            if let Some(bend) = bend.filter(|v| *v > depth) {
                let sag = depth * depth / (bend + (bend * bend - depth * depth).sqrt());
                radius += sag;
                basis +=
                    &format!("; selected R{bend:.3} curved stub, {sag:.6} mm maximum radial sag");
            }
        }
        out.push((
            tube.to_owned(),
            host.to_owned(),
            cylinder(radius, mouth, -axis, depth, true)?,
            basis,
        ));
    }
    for side in ["suction", "discharge"] {
        let a = format!("{side}-reducer");
        let b = format!("{side}-tube");
        if !pending.contains(&pair(&a, &b)) {
            continue;
        }
        let r = &m["reducer_sleeves"][side];
        let radius = r["radius"]
            .as_f64()
            .context("reducer sleeve needs its current opened radius")?;
        let transform = fine::transform(r.get("transform"))?
            .or(frame(m, &a)?)
            .context("reducer sleeve needs its installed frame")?;
        out.push((
            a,
            b,
            cylinder(
                radius + 0.02,
                V3::ZERO,
                V3::from([1., 0., 0.]),
                num(&r["trim"]),
                true,
            )?
            .transformed(&transform),
            "Own trimmed reducer stem and rounded shoulder inside its PVC sleeve".to_owned(),
        ));
    }
    for (name, r) in plans(&m["funnel_fasteners"]) {
        let base = if name.starts_with("funnel-frame-") {
            name
        } else {
            format!("funnel-frame-{name}")
        };
        let host = r["host"]
            .as_str()
            .map(str::to_owned)
            .unwrap_or_else(|| format!("enclosure-{}-top", r["col"].as_str().unwrap_or("front")));
        let start = V3::from([num(&r["x"]), num(&r["y"]), num(&r["insert_top_z"]) - 5.7]);
        let axis = V3::from([0., 0., 1.]);
        for (a, b, inner, outer, basis) in [
            (
                format!("{base}-screw"),
                format!("{base}-insert"),
                1.25 - 2e-6,
                1.5,
                "M3 shaft in RX-M3×5.7 nominal threaded annulus",
            ),
            (
                format!("{base}-insert"),
                host,
                2. - 2e-6,
                2.3,
                "Ø4.0..4.6 × 5.7 mm RX heat-set interference annulus",
            ),
        ] {
            if pending.contains(&pair(&a, &b)) {
                out.push((
                    a,
                    b,
                    annulus(inner, outer, start, axis, 5.7, true)?,
                    basis.to_owned(),
                ));
            }
        }
    }
    for (component, plan) in plans(&m["wall_mount_datums"]) {
        for (i, s) in array(&plan["stations"]).iter().enumerate() {
            if s["threaded"] != true {
                continue;
            }
            let screw = format!("{component}-screw-{}", i + 1);
            let insert = format!("{component}-insert-{}", i + 1);
            let host = string(&plan["parent"]);
            if !pending.contains(&pair(&screw, &insert))
                && !pending.contains(&pair(&insert, &host))
            {
                continue;
            }
            let dimension = |key: &str| {
                plan[key].as_f64().with_context(|| format!("wall mount {component} needs {key}"))
            };
            let start = vector(&s["insert_face_world_mm"])?;
            let axis = -vector(&s["axis_world"])?;
            for (a, b, inner, outer, basis) in [
                (
                    screw,
                    insert.clone(),
                    dimension("insert_bore_radius_mm")?,
                    dimension("screw_radius_mm")?,
                    "Own shaft in the selected insert's nominal thread annulus",
                ),
                (
                    insert,
                    host,
                    dimension("pilot_radius_mm")?,
                    dimension("insert_radius_mm")?,
                    "Selected insert knurl in its own finite wall pilot annulus",
                ),
            ] {
                if outer <= inner {
                    continue;
                }
                if pending.contains(&pair(&a, &b)) {
                    out.push((
                        a,
                        b,
                        annulus(
                            inner - 2e-6,
                            outer,
                            start,
                            axis,
                            dimension("insert_length_mm")?,
                            true,
                        )?,
                        basis.to_owned(),
                    ));
                }
            }
        }
    }
    for (_, r) in plans(&m["y_seam_insert_datums"]) {
        let name = string(&r["name"]);
        let host = string(&r["host"]);
        if pending.contains(&pair(&name, &host)) {
            out.push((
                name,
                host,
                annulus(
                    3.2 - 2e-6,
                    3.55,
                    V3::from([num(&r["x"]), num(&r["y"]), num(&r["z0"])]),
                    V3::from([0., 0., 1.]),
                    num(&r["z1"]) - num(&r["z0"]),
                    true,
                )?,
                "RX-M5×9.5: Ø6.4..7.1 mm nominal heat-set interference annulus".to_owned(),
            ));
        }
    }
    Ok(out)
}
pub fn selected_mounts(m: &Value, rules: &Value) -> Vec<Value> {
    let mut fittings = obj(&rules["selected_fittings"]);
    for (name, r) in plans(&m["union_supports"]) {
        if r["support_implemented"] == true {
            fittings.insert(name, json!([r["parent"], "cradle"]));
        }
    }
    let selected = if m["selected_fitting_names"].is_array() {
        strings(&m["selected_fitting_names"])
    } else {
        fittings.keys().cloned().collect()
    };
    let mut rows = selected
        .iter()
        .filter_map(|n| fittings.get(n).map(|v| json!([n, v[0], v[1]])))
        .collect::<Vec<_>>();
    rows.extend(array(&rules["selected_fixed_mounts"]).iter().cloned());
    for side in ["suction", "discharge"] {
        for part in [
            "reducer",
            "barb-clamp",
            "barb-key",
            "stem-clamp",
            "stem-key",
        ] {
            rows.push(json!([
                format!("{side}-{part}"),
                format!("{side}-tube"),
                "clamped-joint"
            ]));
        }
        rows.push(json!([format!("{side}-tube"), "g-ganen-pump", "barb"]));
    }
    for (name, plan) in plans(&m["wall_mount_datums"]) {
        for (i, s) in array(&plan["stations"]).iter().enumerate() {
            if s["threaded"] == true {
                for (kind, joint) in [("screw", "thread"), ("insert", "heat-set")] {
                    rows.push(json!([
                        format!("{name}-{kind}-{}", i + 1),
                        "enclosure-back-top",
                        joint
                    ]));
                }
            }
        }
    }
    for ns in array(&m["fluid_grid_assignment"]) {
        for name in strings(ns) {
            if !["bulkhead-water", "co2-inlet"].contains(&name.as_str()) {
                rows.push(json!([format!("{name}-nut"), name, "thread"]));
            }
        }
    }
    for (name, r) in plans(&m["funnel_fasteners"]) {
        let host = r["host"]
            .as_str()
            .map(str::to_owned)
            .unwrap_or_else(|| format!("enclosure-{}-top", r["col"].as_str().unwrap_or("front")));
        let base = if name.starts_with("funnel-frame-") {
            name
        } else {
            format!("funnel-frame-{name}")
        };
        for (kind, joint) in [("screw", "thread"), ("insert", "heat-set")] {
            rows.push(json!([format!("{base}-{kind}"), host, joint]));
        }
    }
    for side in ["west", "east"] {
        for (station, host) in [("lower", "back-bottom"), ("upper", "front-top")] {
            for (kind, joint) in [("screw", "thread"), ("insert", "heat-set")] {
                rows.push(json!([
                    format!("y-seam-{side}-{station}-{kind}"),
                    format!("enclosure-{host}"),
                    joint
                ]));
            }
        }
    }
    rows.extend(array(&m["selected_mounts"]).iter().cloned());
    rows
}
pub fn anchored(m: &Value) -> Result<BTreeSet<(String, String)>> {
    let runs = array(&m["runs"]);
    let present = m.get("tube_anchor_sites");
    let site_ids = array(present.unwrap_or(&m["anchor_sites"]))
        .iter()
        .map(|r| string(&r[0]))
        .collect::<BTreeSet<_>>();
    let mut pairs = BTreeSet::new();
    for r in array(&m["anchor_sites"]) {
        let id = string(&r[0]);
        if site_ids.contains(&id) {
            pairs.insert(pair(&id, &string(&r[3])));
        }
    }
    for (id, closure) in obj(&m["tube_anchor_closures"]) {
        if site_ids.contains(&id) && closure == "cap" {
            pairs.insert(pair(&id, &format!("anchor-cap-{id}")));
        }
    }
    let mut cap_ids = BTreeSet::new();
    for r in runs {
        let pts = routes::points(r)?;
        for station in array(&m["cap_tube_anchors"]) {
            let p = vector(station.get("point").unwrap_or(&station[0]))?;
            if pts.windows(2).any(|w| routes::on_leg(p, w[0], w[1], 1e-3)) {
                cap_ids.insert(string(&r["id"]));
            }
        }
    }
    for id in &cap_ids {
        pairs.insert(pair(id, "foam-assembly"));
        if m["core_cap_anchors"][id]["closure"] == "cap" {
            pairs.insert(pair(id, &format!("anchor-cap-{id}")));
        }
    }
    for (_, r) in plans(&m["reservoir_anchor_datums"]) {
        if r["closure"] == "snap" {
            for id in strings(&r["routes_west_to_east"]) {
                pairs.insert(pair(&id, &string(&r["cap_name"])));
            }
        }
    }
    pairs.extend(
        array(&m["anchored_pairs"])
            .iter()
            .map(|r| pair(&string(&r[0]), &string(&r[1]))),
    );
    Ok(pairs)
}
fn touching(w: &World, m: &Value, rules: &Value) -> BTreeSet<(String, String)> {
    let mut pairs = array(&rules["touching_ok"])
        .iter()
        .map(|r| pair(&string(&r[0]), &string(&r[1])))
        .collect::<BTreeSet<_>>();
    for r in selected_mounts(m, rules) {
        if r[1].is_string() && r[2] != "tube-carried" {
            pairs.insert(pair(&string(&r[0]), &string(&r[1])));
        }
    }
    for (a, b) in [
        ("pcba", "foam-assembly"),
        ("digiten-flow", "enclosure-back-top"),
        ("digiten-flow", "soda-outlet-return-stem"),
        ("soda-bend-holder", "tube-soda-core-rise"),
        ("soda-continuous-insulation", "tube-soda-core-rise"),
        ("soda-continuous-insulation", "soda-bend-holder"),
        ("water-split", "asse-outlet-tpu"),
        ("water-split", "tee-fold"),
        ("flow-regulator", "reg-va-elbow"),
        ("gas-check", "gas-lower-b"),
        ("lower-pump-elbow", "pump-inlet-tpu"),
        ("discharge-chain", "pump-outlet-tpu"),
        ("discharge-chain", "pump-outlet-tube-band"),
    ] {
        pairs.insert(pair(a, b));
    }
    for n in strings(&m["soft_neighbors"]) {
        pairs.insert(pair("soda-continuous-insulation", &n));
    }
    for (n, r) in plans(&m["wiring_placements"]) {
        let host = if r["parent"] == "cold-core" {
            "foam-assembly".to_owned()
        } else {
            format!("enclosure-{}", string(&r["parent"]))
        };
        pairs.insert(pair(&n, &host));
    }
    for (side, _) in [("inlet", 0), ("outlet", 0)] {
        let cuff = format!("pump-{side}-tpu");
        pairs.insert(pair(&cuff, "g-ganen-pump"));
        for band in ["barb", "tube"] {
            pairs.insert(pair(&format!("pump-{side}-{band}-band"), &cuff));
        }
        pairs.insert(pair(&format!("asse-{side}-tpu"), "asse1022-assembly"));
    }
    for (component, plan) in plans(&m["wall_mount_datums"]) {
        for (i, s) in array(&plan["stations"]).iter().enumerate() {
            if s["threaded"] != true {
                continue;
            }
            let screw = format!("{component}-screw-{}", i + 1);
            let insert = format!("{component}-insert-{}", i + 1);
            pairs.insert(pair(&screw, &component));
            pairs.insert(pair(&insert, &component));
            pairs.insert(pair(&screw, &insert));
        }
    }
    for col in ["front", "back"] {
        for side in ["west", "east"] {
            let base = format!("funnel-frame-{col}-{side}");
            pairs.insert(pair(&format!("{base}-screw"), &format!("{base}-insert")));
            for kind in ["screw", "insert"] {
                pairs.insert(pair("funnel-frame", &format!("{base}-{kind}")));
            }
        }
    }
    for side in ["west", "east"] {
        for station in ["lower", "upper"] {
            let b = format!("y-seam-{side}-{station}");
            pairs.insert(pair(&format!("{b}-screw"), &format!("{b}-insert")));
        }
    }
    pairs.retain(|(a, b)| w.index.contains_key(a) && w.index.contains_key(b));
    pairs
}
pub fn read(w: &mut World, m: &Value, rules: &Value, with_clearance: bool) -> Result<Readings> {
    let logical = w.populations.iter().flatten().cloned().collect::<Vec<_>>();
    let mut census = Vec::new();
    let mut owners = Vec::new();
    for (i, a) in logical.iter().enumerate() {
        for b in &logical[i + 1..] {
            let aa = w.g(a)?.bounds;
            let bb = w.g(b)?.bounds;
            if (0..3).any(|k| aa[k + 3] <= bb[k] + 1e-6 || bb[k + 3] <= aa[k] + 1e-6) {
                continue;
            }
            census.push(w.q("shared_volume", a, b)?);
            owners.push((a.clone(), b.clone()));
        }
    }
    let mut bad = Vec::new();
    let mut unanswered = Vec::new();
    for ((a, b), r) in owners.into_iter().zip(w.measure(census)?) {
        if r.get("error").is_some() {
            unanswered.push(json!([a, b, r["error"]]));
        } else if num(&r["value"]) > 1. {
            bad.push(json!({"a":a,"b":b,"volume":r["value"]}));
        }
    }
    let pending = bad
        .iter()
        .map(|r| pair(&string(&r["a"]), &string(&r["b"])))
        .collect::<BTreeSet<_>>();
    let mut contacts = json!({"mates":{"pairs":[],"scope":"Finite nominal mating regions only; physical insertion, sealing and retention remain unqualified."}});
    let mut masks = Vec::new();
    let mut families = Vec::new();
    match mate_regions(w, m, &pending) {
        Ok(regions) => {
            for (a, b, tool, basis) in regions {
                let (a, b) = pair(&a, &b);
                masks.push((a, b, tool));
                families.push(("mates".to_owned(), basis));
            }
        }
        Err(e) => unanswered.push(json!([
            "selected nominal mates",
            "engagement regions",
            format!("{e:#}")
        ])),
    }
    if ["g", "j"].iter().any(|v| {
        pending.contains(&pair(
            &format!("valve-v-{v}"),
            &format!("flavor-reducer-v-{v}"),
        ))
    }) {
        for v in ["g", "j"] {
            let a = format!("flavor-reducer-v-{v}");
            let b = format!("valve-v-{v}");
            match w.solid(&a).and_then(|s| stem_region(&s, &profile(), true)) {
                Ok(mask) => {
                    masks.push((a, b, mask));
                    families.push(("reducers".to_owned(), v.to_owned()));
                }
                Err(e) => unanswered.push(json!([
                    "valve-v-g",
                    "flavor-reducer-v-g",
                    format!("reducer stems in their ports: {e:#}")
                ])),
            }
        }
    }
    let mut elbow_names = w.populations[0]
        .iter()
        .filter(|n| n.starts_with("stem-elbow-"))
        .cloned()
        .collect::<Vec<_>>();
    elbow_names.sort();
    if elbow_names
        .iter()
        .any(|n| pending.contains(&pair(n, &elbow_host(n))))
    {
        for a in elbow_names {
            let b = elbow_host(&a);
            match w.solid(&a).and_then(|s| stem_region(&s, &profile(), false)) {
                Ok(mask) => {
                    masks.push((a.clone(), b, mask));
                    families.push((
                        "elbows".to_owned(),
                        a.trim_start_matches("stem-elbow-").to_owned(),
                    ));
                }
                Err(e) => unanswered.push(json!([
                    "stem-elbow",
                    "its collet",
                    format!("elbow stems in their collets: {e:#}")
                ])),
            }
        }
    }
    if pending.contains(&pair("funnel-drain-union", "funnel")) {
        let r = &m["funnel_seal"];
        let make = || -> Result<Solid> {
            annulus(
                num(&r["inner_radius"]) - 0.01,
                num(&r["outer_radius"]) + 0.01,
                vector(&r["base"])?,
                V3::from([0., 0., 1.]),
                num(&r["length"]),
                false,
            )
        };
        match make() {
            Ok(mask) => {
                masks.push(("funnel-drain-union".to_owned(), "funnel".to_owned(), mask));
                families.push(("seal".to_owned(), String::new()));
            }
            Err(e) => unanswered.push(json!([
                "funnel-drain-union",
                "funnel",
                format!("sealing land contact: {e:#}")
            ])),
        }
    }
    let mut queries = Vec::new();
    let temporary_start = w.parts.len();
    let mut mask_pairs = Vec::with_capacity(masks.len());
    for (a, b, mask) in masks {
        let i = w.parts.len();
        w.parts.push(Imported {
            name: format!("mask-{i}"),
            color: None,
            solid: mask,
        });
        let mut q = w.q("common", &a, &b)?;
        q["distribute_a"] = json!(true);
        q["fine_mask_stages"] = json!([{"name":"receiving-interface","indices":[i]}]);
        queries.push(q);
        mask_pairs.push((a, b));
    }
    let readings = w.measure(queries);
    // The receiving tools have no role in later clearances, slopes or drain
    // questions. No source entry or externally visible index is changed.
    w.parts.truncate(temporary_start);
    let readings = readings?;
    let mut admitted = BTreeSet::new();
    let mut family_pairs: BTreeMap<String, Vec<(String, String)>> = BTreeMap::new();
    let mut family_pass: BTreeMap<String, bool> = BTreeMap::new();
    for (((a, b), (family, basis)), r) in mask_pairs.iter().zip(&families).zip(readings) {
        if r.get("error").is_some() {
            unanswered.push(json!([a, b, r["error"]]));
            continue;
        }
        let total = num(&r["common"]["raw"]["volume_mm3"]);
        let outside = num(&r["common"]["residual"]["volume_mm3"]);
        let pass = outside <= 1.;
        if family == "mates" {
            let parts = pair(a, b);
            contacts["mates"]["pairs"].as_array_mut().unwrap().push(json!({"parts":[parts.0,parts.1],"basis":basis,"common_mm3":total,"outside_mate_region_mm3":outside,"pass":pass}));
            if pass {
                admitted.insert(parts);
            }
        } else if family == "seal" {
            contacts["seal"] =
                json!({"land_contact_mm3":total,"outside_land_mm3":outside,"pass":pass});
            if pass {
                admitted.insert(pair(a, b));
            }
        } else {
            if !contacts[family].is_object() {
                contacts[family] = json!({"stems":{},"pass":true});
            }
            contacts[family]["stems"][basis] = json!([total, outside]);
            family_pairs
                .entry(family.clone())
                .or_default()
                .push(pair(a, b));
            *family_pass.entry(family.clone()).or_insert(true) &= pass;
        }
    }
    for (family, pass) in family_pass {
        contacts[&family]["pass"] = json!(pass);
        if pass {
            admitted.extend(family_pairs.remove(&family).unwrap_or_default());
        }
    }
    bad.retain(|r| !admitted.contains(&pair(&string(&r["a"]), &string(&r["b"]))));
    if let Some(pump) = bad
        .iter()
        .find(|r| pair(&string(&r["a"]), &string(&r["b"])) == pair("g-ganen-pump", "foam-assembly"))
    {
        let total = num(&pump["volume"]);
        contacts["pump"] = json!({"rigid_overlap_mm3":total,"free_foot_contact_mm3":0.,"outside_contact_masks_mm3":total,"feet":[],"pass":total<=1.});
    }
    let qs = bad
        .iter()
        .map(|r| w.q("common", &string(&r["a"]), &string(&r["b"])))
        .collect::<Result<Vec<_>>>()?;
    let readings = w.measure(qs)?;
    let mut clashes = Vec::new();
    for (mut hit, r) in bad.into_iter().zip(readings) {
        if r.get("error").is_some() || r["common"]["raw"]["min"].is_null() {
            unanswered.push(json!([
                hit["a"],
                hit["b"],
                r.get("error")
                    .cloned()
                    .unwrap_or(json!("Common material has no measurable bounds"))
            ]));
        } else {
            hit["where"] = r["common"]["raw"].clone();
            clashes.push(hit);
        }
    }
    let (clearances, lanes) = if with_clearance {
        clearance(w, m, rules)?
    } else {
        (Vec::new(), Vec::new())
    };
    Ok(Readings {
        clashes,
        unanswered,
        contacts,
        clearances,
        lanes,
    })
}

pub fn clearance(w: &mut World, m: &Value, rules: &Value) -> Result<(Vec<Value>, Vec<String>)> {
    let touching = touching(w, m, rules);
    let pack = names(&m["pack_body_names"]);
    let mut pairs = Vec::new();
    let bodies = w.populations[0].clone();
    for (i, a) in bodies.iter().enumerate() {
        for b in &bodies[i + 1..] {
            if pack.contains(a) && pack.contains(b) {
                continue;
            }
            if box_gap(&w.g(a)?.bounds, &w.g(b)?.bounds) >= 2. {
                continue;
            }
            pairs.push((
                a.clone(),
                b.clone(),
                a.clone(),
                b.clone(),
                touching.contains(&pair(a, b)),
            ));
        }
    }
    let runs = array(&m["runs"]);
    let drawn = names(&json!(w.populations[1]));
    let tubes = runs
        .iter()
        .filter(|r| drawn.contains(&format!("tube-{}", string(&r["id"]))))
        .map(|r| (string(&r["id"]), format!("tube-{}", string(&r["id"]))))
        .collect::<Vec<_>>();
    let mut rest = bodies.clone();
    rest.extend(w.populations[2].iter().cloned());
    rest.extend(
        w.populations[1]
            .iter()
            .filter(|n| !tubes.iter().any(|(_, t)| t == *n))
            .cloned(),
    );
    let touching = touching
        .iter()
        .map(|(a, b)| pair(a.trim_start_matches("tube-"), b.trim_start_matches("tube-")))
        .collect::<BTreeSet<_>>();
    let anchored = anchored(m)?;
    for (i, (a, aa)) in tubes.iter().enumerate() {
        for (b, bb) in &tubes[i + 1..] {
            if box_gap(&w.g(aa)?.bounds, &w.g(bb)?.bounds) < 2. {
                pairs.push((a.clone(), b.clone(), aa.clone(), bb.clone(), false));
            }
        }
    }
    let mut adapters = obj(&rules["port_adapters"]);
    adapters.extend(obj(&m["port_adapters"]));
    for (a, aa) in &tubes {
        let run = runs.iter().find(|r| r["id"] == *a).unwrap();
        let mut ends = BTreeSet::new();
        for key in ["frm", "to"] {
            let port = string(&run[key]);
            ends.insert(port.split('.').next().unwrap_or("").to_owned());
            if let Some(adapter) = adapters.get(&port) {
                ends.insert(string(adapter));
            }
        }
        for b in &rest {
            if ends.contains(b) || box_gap(&w.g(aa)?.bounds, &w.g(b)?.bounds) >= 2. {
                continue;
            }
            pairs.push((
                a.clone(),
                b.clone(),
                aa.clone(),
                b.clone(),
                touching.contains(&pair(a, b)) || anchored.contains(&pair(a, b)),
            ));
        }
    }
    let qs = pairs
        .iter()
        .map(|(_, _, a, b, _)| {
            let mut q = w.q("gap", a, b)?;
            q["within_mm"] = json!(2.);
            Ok(q)
        })
        .collect::<Result<Vec<_>>>()?;
    let mut clearances = Vec::new();
    for ((x, y, _, _, ok), r) in pairs.into_iter().zip(w.measure(qs)?) {
        if let Some(e) = r.get("error") {
            bail!("clearance query: {e}");
        }
        let gap = num(&r["value"]).min(2.);
        if gap < 2. {
            clearances.push(json!([x, y, gap, ok]));
        }
    }
    clearances.sort_by(|a, b| num(&a[2]).total_cmp(&num(&b[2])));
    let mut tight: BTreeMap<String, Vec<(f64, String)>> = BTreeMap::new();
    for r in &clearances {
        if r[3] == true || num(&r[2]) >= 1. {
            continue;
        }
        for (rid, other) in [
            (string(&r[0]), string(&r[1])),
            (string(&r[1]), string(&r[0])),
        ] {
            if runs.iter().any(|r| r["id"] == rid) && bodies.contains(&other) {
                tight.entry(rid).or_default().push((num(&r[2]), other));
            }
        }
    }
    let mut lanes = Vec::new();
    for (rid, mut hits) in tight {
        if hits.len() < 2 {
            continue;
        }
        hits.sort_by(|a, b| a.0.total_cmp(&b.0).then(a.1.cmp(&b.1)));
        let (ga, p) = &hits[0];
        let (gb, q) = &hits[1];
        let run = runs.iter().find(|r| r["id"] == rid).unwrap();
        let od = num(&run["diam"]);
        let horizon = ga + od + gb;
        let mut query = w.q("gap", p, q)?;
        query["within_mm"] = json!(horizon);
        let reading = w.measure(vec![query])?;
        let lane = num(&reading[0]["value"]);
        let side = (lane - od) / 2.;
        let note = format!(
            "{rid} threads {p} — {q}: they leave {lane:.3} mm and the tube is Ø{}, so {side:.3} mm a side",
            pretty(od)
        );
        lanes.push(if(side-ga).abs()<5e-3&&(side-gb).abs()<5e-3{format!("{note} is that lane's own best — nothing moves inside it, so the fix is a body or the route itself{}",routes::need_clause(&routes::need(run)?))}else{format!("{note} if it were centred, and it is not")});
    }
    Ok((clearances, lanes))
}
