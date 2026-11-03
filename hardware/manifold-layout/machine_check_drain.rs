//! Dedicated nominal ASSE drain reading over the complete installed population.
use super::*;
const NAMES: [&str; 4] = [
    "asse-drain-adapter",
    "tube-drain-vent",
    "tube-fluid-18",
    "tube-fluid-28",
];
const CONNECTED: [(&str, &str); 9] = [
    ("asse-drain-adapter", "asse1022-assembly"),
    ("asse-drain-adapter", "tube-drain-vent"),
    ("tube-drain-vent", "bulkhead-drain"),
    ("tube-fluid-18", "valve-v-g"),
    ("tube-fluid-18", "flavor-reducer-v-g"),
    ("tube-fluid-18", "bulkhead-flavor-a"),
    ("tube-fluid-28", "valve-v-j"),
    ("tube-fluid-28", "flavor-reducer-v-j"),
    ("tube-fluid-28", "bulkhead-flavor-b"),
];
const SCOPE: &str = "Nominal authoritative fine model clearance of the direct TPU ASSE sleeve and dedicated drain against the complete installed assembly population, including cold-core bodies and retained flavor returns. Connected interfaces are excluded. Tubes exclude flexible conductors and jackets as obstacles; connector housings remain. The white 4 mm return requires at least 1 mm to every other unconnected body. Pump occupied envelopes are read per component. The sleeve expanded shape is an occupancy approximation. Hardware tolerances, zip-tie heads, actual bending, seals and vent performance are unmeasured.";
pub fn read(world: &mut World, spec: &Value) -> Result<Value> {
    let checked = spec
        .get("checked_members")
        .map(strings)
        .unwrap_or_else(|| NAMES.iter().map(|s| s.to_string()).collect());
    ensure!(!checked.is_empty(), "drain reading needs a checked member");
    let selected = spec
        .get("obstacles")
        .filter(|v| !v.is_null())
        .map(names)
        .unwrap_or_else(|| world.groups.iter().map(|g| g.name.clone()).collect());
    for n in &selected {
        world.g(n)?;
    }
    if let Some(expected) = spec
        .get("expected_envelope_bounds")
        .filter(|v| v.is_array())
    {
        ensure!(array(expected).len() == 6, "casing bounds need six values");
        let actual = world.g("foam-assembly")?.bounds;
        ensure!(
            (0..6).all(|i| (actual[i] - num(&expected[i])).abs() <= 1e-5),
            "exact casing model/frame differs from saved placement"
        );
    }
    let connected = CONNECTED
        .iter()
        .map(|(a, b)| pair(a, b))
        .collect::<BTreeSet<_>>();
    let mut checks = BTreeMap::new();
    let mut candidates = Vec::new();
    let mut queries = Vec::new();
    let mut owners = Vec::new();
    for n in &checked {
        let g = world.g(n)?;
        let mut components = 0;
        let mut valid = true;
        for &i in &g.indices {
            let s = fine::summary(&world.parts[i], true);
            components += array(&s["components"]).len();
            valid &= num(&s["volume"]) > 0.
                && num(&s["triangles"]) > 0.
                && array(&s["min"])
                    .iter()
                    .chain(array(&s["max"]))
                    .chain(std::iter::once(&s["volume"]))
                    .all(|v| v.as_f64().is_some_and(f64::is_finite));
        }
        checks.insert(n.clone(),json!({"valid":valid,"solids":components,"minimum_unconnected_gap_mm":if n=="tube-drain-vent"{1.}else{0.},"neighbors":[]}));
        for other in &world.groups {
            if !selected.contains(&other.name)
                || other.name == *n
                || connected.contains(&pair(n, &other.name))
            {
                continue;
            }
            let leaf = other.name.rsplit('/').next().unwrap();
            let wire = ["wire-", "wiring-", "terminal-"]
                .iter()
                .any(|p| leaf.starts_with(p))
                && !["wiring-junction-", "terminal-J"]
                    .iter()
                    .any(|p| leaf.starts_with(p));
            if n.starts_with("tube-") && wire {
                continue;
            }
            if !overlap(&g.bounds, &other.bounds, 1.) {
                continue;
            }
            candidates.push((n.clone(), other.name.clone()));
            for &a in &g.indices {
                for &b in &other.indices {
                    queries.push(json!({"kind":"gap","a":a,"b":b}));
                    queries.push(json!({"kind":"common","a":a,"b":b}));
                    owners.push((n.clone(), other.name.clone()));
                }
            }
        }
    }
    let count = queries.len();
    let readings = world.measure(queries)?;
    ensure!(readings.len() == count, "drain fine query coverage differs");
    let mut values = candidates
        .iter()
        .cloned()
        .map(|p| (p, (Vec::<f64>::new(), Vec::<f64>::new())))
        .collect::<BTreeMap<_, _>>();
    let mut errors = Vec::new();
    for (owner, row) in owners.iter().zip(readings.chunks_exact(2)) {
        ensure!(
            row[0]["kind"] == "gap" && row[1]["kind"] == "common",
            "drain query order differs"
        );
        if row[0].get("error").is_some() || row[1].get("error").is_some() {
            errors.push(json!({"member":owner.0,"obstacle":owner.1,"error":row[0].get("error").or_else(||row[1].get("error"))}));
            continue;
        }
        let found = values.get_mut(owner).unwrap();
        found.0.push(num(&row[0]["value"]));
        found.1.push(num(&row[1]["common"]["raw"]["volume_mm3"]));
    }
    // Neighbor order is the original complete-population order, independent of
    // the native map used to aggregate separate occupied entries.
    for (n, other) in &candidates {
        let (gap, volume) = &values[&(n.clone(), other.clone())];
        if gap.is_empty() {
            continue;
        }
        checks.get_mut(n).unwrap()["neighbors"].as_array_mut().unwrap().push(json!({"name":other,"gap_mm":round(gap.iter().copied().fold(f64::INFINITY,f64::min),7),"overlap_mm3":round(volume.iter().sum(),7)}));
    }
    for (n, row) in &mut checks {
        row["passed"] = json!(
            row["valid"] == true
                && row["solids"] == 1
                && !errors.iter().any(|e| e["member"] == *n)
                && array(&row["neighbors"])
                    .iter()
                    .all(|r| num(&r["overlap_mm3"]) <= 1e-5
                        && num(&r["gap_mm"]) >= num(&row["minimum_unconnected_gap_mm"]) - 1e-6)
        );
    }
    let specs = spec
        .get("route_specs")
        .unwrap_or(&spec["metadata"]["native_route_specs"]);
    let mut radii = BTreeMap::new();
    let mut surfaces = BTreeMap::new();
    for n in &checked {
        if !["tube-drain-vent", "tube-fluid-18", "tube-fluid-28"].contains(&n.as_str()) {
            continue;
        }
        let route = if n == "tube-drain-vent" {
            &specs["drain-vent"]
        } else {
            &Value::Null
        };
        let values = if route.is_object() {
            routes::centerline_radii(&route["segments"])?
        } else {
            let mut found = Vec::new();
            let mut values = Vec::new();
            for &i in &world.g(n)?.indices {
                for (fi, f) in world.parts[i].solid.faces().iter().enumerate() {
                    if let Surface::Torus { major, .. } = f.surface {
                        values.push(round(major, 7));
                        found.push(json!({"entry_index":world.role[i].1,"qualified_name":world.role[i].2,"face_index":fi,"record":hsm_kernel::write::face_json(f)}));
                    }
                }
            }
            surfaces.insert(n.clone(), json!(found));
            values.sort_by(f64::total_cmp);
            values.dedup();
            values
        };
        let passed = (!values.is_empty()
            || (n == "tube-drain-vent" && !array(&route["segments"]).is_empty()))
            && values.iter().all(|v| *v >= 25. - 1e-6);
        let mut row = json!({"centerline_radii_mm":values,"passed":passed});
        if n == "tube-drain-vent" {
            row["method"] = json!(if route.is_object() {
                "Producer centerline; circular arcs and cubic curvature extrema"
            } else {
                "Authoritative fine toroidal face records"
            });
        } else {
            row["stock_minimum_mm"] = json!(25.);
        }
        radii.insert(n.clone(), row);
    }
    let population=world.groups.iter().map(|g|(g.name.clone(),json!(g.indices.iter().map(|&i|json!({"model":world.role[i].0,"entry_index":world.role[i].1,"qualified_name":world.role[i].2})).collect::<Vec<_>>()))).collect::<BTreeMap<_,_>>();
    let passed = errors.is_empty()
        && checks
            .values()
            .chain(radii.values())
            .all(|r| r["passed"] == true);
    let mut inputs = spec["input_bindings"].clone();
    if !inputs.is_object() {
        inputs = json!({});
    }
    inputs["population"] = json!(population);
    inputs["aliases"] = spec["aliases"]
        .as_object()
        .map(|_| spec["aliases"].clone())
        .unwrap_or(json!({}));
    inputs["bend_surface_records"] = json!(surfaces);
    Ok(
        json!({"scope":if spec.get("obstacles").is_some_and(|v|!v.is_null()){format!("Selected named obstacles only. {SCOPE}")}else{SCOPE.to_owned()},"conservative_cold_core_envelope_included":true,"installed_body_count":world.groups.len(),"checked_members":checked,"checks":checks,"bend_radii":radii,"source_sha256":spec["source_sha256"],"fine_inputs":inputs,"fine_query_count":count,"candidate_pairs":candidates,"selected_obstacles":if spec.get("obstacles").is_some_and(|v|!v.is_null()){json!(selected)}else{Value::Null},"errors":errors,"passed":passed}),
    )
}
