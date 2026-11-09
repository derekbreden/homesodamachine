use super::*;
mod scene_records;
fn set(value: &Value) -> Result<BTreeSet<String>> {
    Ok(rows(value)?
        .iter()
        .map(|v| string(v).map(str::to_owned))
        .collect::<Result<_>>()?)
}
fn defaults() -> Result<Value> {
    let mut c = hsm_kernel::reads::json("tools/hsm/assembly-docs/src/wiring/scene-constants.json")?;
    for name in ["psu", "relay-1", "relay-2"] {
        for kind in ["screw", "insert"] {
            let numbers = if name == "psu" {
                vec![1, 2, 3, 4]
            } else {
                vec![1, 4]
            };
            for n in numbers {
                c["BACK_TOP_CARRIED_COMPONENTS"]
                    .as_array_mut()
                    .unwrap()
                    .push(json!(format!("{name}-{kind}-{n}")));
            }
        }
    }
    for name in [
        "bulkhead-carb",
        "bulkhead-drain",
        "bulkhead-flavor-a",
        "bulkhead-flavor-b",
    ] {
        for row in [name.to_owned(), format!("{name}-nut")] {
            c["BACK_TOP_CARRIED_COMPONENTS"]
                .as_array_mut()
                .unwrap()
                .push(json!(row));
        }
    }
    for name in [
        "bulkhead-water",
        "bulkhead-carb",
        "bulkhead-drain",
        "bulkhead-flavor-a",
        "bulkhead-flavor-b",
        "co2-inlet",
    ] {
        c["BEARS_ON"][format!("{name}-nut")] = json!(name);
    }
    for tee in ["y-c", "y-d", "y-f", "y-g"] {
        c["BEARS_ON"][format!("tee-{tee}")] = json!("enclosure-front-top");
    }
    c["SCENES"] = scene_records::rows(&c);
    Ok(c)
}
fn core_names(root: &Path) -> Result<Vec<String>> {
    let card = load(
        root,
        "hardware/cold-core-layout/cold-core-assembly.scorecard.json",
    )?;
    let mut names = rows(&card["bodies"])?
        .iter()
        .map(|v| string(v).map(str::to_owned))
        .collect::<Result<Vec<_>>>()?;
    for bend in rows(&card["bends"])? {
        names.push(format!("line-{}", string(&bend["id"])?));
    }
    names.sort();
    Ok(names)
}
fn inner(scene: &Value, names: &[String]) -> Result<BTreeSet<String>> {
    let value = &scene["inner"];
    if value.is_null() || value.as_array().is_some_and(Vec::is_empty) {
        return Ok(BTreeSet::new());
    }
    let list = if value == "*" {
        names.to_vec()
    } else {
        set(value)?.into_iter().collect()
    };
    Ok(list.into_iter().map(|n| format!("cold-core/{n}")).collect())
}
pub fn held(root: &str, holders: &Value, stop: &Value) -> Result<BTreeSet<String>> {
    let stop = set(stop)?;
    let mut out = BTreeSet::new();
    let mut queue = vec![root.to_owned()];
    let map = holders.as_object().context("scene holder map")?;
    while let Some(node) = queue.pop() {
        if out.contains(&node) || stop.contains(&node) {
            continue;
        }
        out.insert(node.clone());
        for (name, by) in map {
            if by.as_str() == Some(&node) && !out.contains(name) {
                queue.push(name.clone());
            }
        }
    }
    Ok(out)
}
fn runs_for(bodies: &BTreeSet<String>, runs: &Value, holders: &Value) -> Result<BTreeSet<String>> {
    let mut out = BTreeSet::new();
    for run in rows(runs)? {
        let id = format!("tube-{}", string(&run["id"])?);
        let from = string(&run["frm"])?.split('.').next().unwrap();
        let to = string(&run["to"])?.split('.').next().unwrap();
        if holders[&id]
            .as_str()
            .is_some_and(|name| bodies.contains(name))
            || (bodies.contains(from) && bodies.contains(to))
        {
            out.insert(id);
        }
    }
    Ok(out)
}
fn crossings(runs: &Value, conduits: &BTreeSet<String>) -> Result<Value> {
    let mut out = json!({});
    for run in rows(runs)? {
        for end in [&run["frm"], &run["to"]] {
            let end = string(end)?;
            if let Some((part, mouth)) = end.split_once('.') {
                if part == "foam-assembly" && conduits.contains(mouth) {
                    out[format!("cold-core/line-{mouth}")] =
                        json!(format!("tube-{}", string(&run["id"])?));
                }
            }
        }
    }
    Ok(out)
}
fn holders(
    c: &Value,
    rows_input: &Value,
    tube_sites: &Value,
    tube_pieces: &Value,
    equipment: &Value,
    rides: &Value,
    present: Option<&BTreeSet<String>>,
    cap_names: &BTreeSet<String>,
) -> Result<Value> {
    let mut out = json!({});
    let rows = rows(rows_input)?;
    let active = |name: &str| present.is_none_or(|p| p.contains(name));
    for row in rows {
        let name = string(&row[0])?;
        if name.starts_with("anchor-cap-") && !cap_names.contains(name) {
            continue;
        }
        let by = row[1]
            .as_str()
            .filter(|v| !v.is_empty())
            .map(|v| json!(v))
            .unwrap_or_else(|| c["BEARS_ON"].get(name).cloned().unwrap_or(Value::Null));
        out[name] = by;
    }
    for row in super::rows(tube_sites)? {
        let id = string(&row[0])?;
        let tube = format!("tube-{id}");
        if active(&tube) {
            out[tube] = tube_pieces[id].clone();
        }
    }
    for name in set(equipment)? {
        if out.get(&name).is_some() {
            out[name] = json!("foam-assembly");
        }
    }
    for name in super::rows(&c["BACK_TOP_CARRIED_COMPONENTS"])?
        .iter()
        .chain(super::rows(&c["BACK_TOP_CARRIED_TUBES"])?)
        .cloned()
        .chain(std::iter::once(json!("tube-soda-core-rise")))
    {
        let name = string(&name)?;
        if active(name) {
            out[name] = json!("enclosure-back-top");
        }
    }
    for (rider, host) in rides.as_object().context("rider map")? {
        let host = string(host)?;
        if out.get(rider).is_some() && out.get(host).is_some() {
            out[rider] = out[host].clone();
        }
    }
    Ok(out)
}
fn legacy_holders(c: &Value, data: &Value) -> Result<Value> {
    let source = provider(json!({"kind":"scene_inputs"}))?;
    let tube_sites = data.get("tube_sites").cloned().unwrap_or_else(|| json!([]));
    let mut cap_names = BTreeSet::new();
    for (name, row) in source["cap_anchors"].as_object().context("cap anchors")? {
        if row["closure"] == "cap" {
            cap_names.insert(format!("anchor-cap-{name}"));
        }
    }
    for row in rows(&tube_sites)? {
        if row[1].get(5).is_some_and(|v| v == "cap") {
            cap_names.insert(format!("anchor-cap-{}", string(&row[0])?));
        }
    }
    let mut pieces = json!({});
    for row in rows(&source["tube_anchor_sites"])? {
        pieces[string(&row[0])?] = row[3].clone();
    }
    let mut out = holders(
        c,
        &source["mounts"],
        &tube_sites,
        &pieces,
        &source["equipment"],
        &json!({}),
        None,
        &cap_names,
    )?;
    let ml = &source["manifold"];
    let mut pump_at = BTreeMap::new();
    for (name, x) in ml["pumps"].as_object().context("manifold pumps")? {
        pump_at.insert(x.to_string(), name.clone());
    }
    for row in rows(&ml["segments"])? {
        let tube = format!("tube-fluid-{}", row[0]);
        let how = string(&row[3])?;
        if let Some(barb) = ml["barb_of"].get(how) {
            let pump = pump_at
                .get(&barb[0].to_string())
                .context("pump station owner")?;
            out[tube] = json!(format!("{pump}-head"));
        } else if ml["fore_stubs"].get(how).is_some() {
            out[tube] = json!("enclosure-front-top");
        }
    }
    for cid in rows(&ml["lower_ids"])? {
        out[format!(
            "tube-fluid-{}",
            cid.as_str()
                .map(str::to_owned)
                .unwrap_or_else(|| cid.to_string())
        )] = json!("enclosure-front-top");
    }
    // Apply riders after the manifold and mounting-parent ownership is complete.
    for (rider, host) in source["rides"].as_object().context("rider map")? {
        if out.get(rider).is_some() && out.get(string(host)?).is_some() {
            out[rider] = out[string(host)?].clone();
        }
    }
    let mut orphans = Vec::new();
    for row in rows(&source["mounts"])? {
        let name = string(&row[0])?;
        if name.starts_with("anchor-cap-") && !cap_names.contains(name) {
            continue;
        }
        if out[name].is_null() && row[2] != "pack" && c["BEARS_ON"].get(name).is_none() {
            orphans.push(format!("{name} ({})", string(&row[2])?));
        }
    }
    if !orphans.is_empty() {
        orphans.sort();
        bail!(
            "these bodies have no parent, so no scene can know whether to show them: {}. `_scorecard.MOUNTS` and `RIDES` leave them unheld; name the piece each bears on in `_scenes.BEARS_ON`, or None for one that comes with the flavour pack.",
            orphans.join(", ")
        );
    }
    Ok(out)
}
fn named(
    scene: &Value,
    c: &Value,
    runs: &Value,
    holders: &Value,
    core_names: &[String],
    promoted: &BTreeSet<String>,
    crossings: &Value,
    strict: bool,
) -> Result<BTreeSet<String>> {
    let roots = set(&scene["roots"])?;
    let later = set(&scene["later"])?;
    let mut bodies = BTreeSet::new();
    for root in &roots {
        bodies.extend(held(root, holders, &scene["later"])?);
    }
    if strict && !later.is_empty() {
        let mut carried = BTreeSet::new();
        for root in &roots {
            carried.extend(held(root, holders, &json!([]))?);
        }
        carried.extend(inner(scene, core_names)?);
        let adrift = later.difference(&carried).cloned().collect::<Vec<_>>();
        if !adrift.is_empty() {
            bail!(
                "scene '{}' holds back {}, which nothing in {} carries. `later` names a body the piece DOES hold and the unit has not got yet; a body that has moved to another piece leaves this row with the piece it moved to.",
                string(&scene["id"])?,
                adrift.join(", "),
                roots.iter().cloned().collect::<Vec<_>>().join(", ")
            );
        }
    }
    let bare = set(&c["BARE"])?;
    let mut derived = if bare.contains(string(&scene["id"])?) {
        roots.clone()
    } else {
        let mut all = bodies.clone();
        all.extend(runs_for(&bodies, runs, holders)?);
        all
    };
    derived.retain(|name| !later.contains(name));
    let inner = inner(scene, core_names)?;
    if !inner.is_empty() {
        derived.remove("foam-assembly");
        derived.extend(inner.difference(&later).cloned());
    }
    fn remove_promoted(derived: &mut BTreeSet<String>, promoted: &BTreeSet<String>) {
        for name in promoted {
            if derived.contains(name) {
                derived.remove(&format!("cold-core/{name}"));
            }
        }
    }
    remove_promoted(&mut derived, promoted);
    derived.extend(set(&scene["also"])?);
    for (line, half) in crossings.as_object().context("conduit crossings")? {
        if derived.contains(line) {
            derived.insert(string(half)?.into());
        }
    }
    derived.retain(|name| !later.contains(name));
    remove_promoted(&mut derived, promoted);
    if let Some(other_id) = scene.get("without").and_then(Value::as_str) {
        let other = rows(&c["SCENES"])?
            .iter()
            .find(|s| s["id"] == other_id)
            .context("subtracted scene")?;
        if strict && other.get("without").is_some_and(|v| !v.is_null()) {
            bail!(
                "scene '{}' is '{}' less its own '{}'. State this scene against a unit that is drawn whole.",
                string(&scene["id"])?,
                other_id,
                string(&other["without"])?
            );
        }
        let mut gone = named(
            other, c, runs, holders, core_names, promoted, crossings, strict,
        )?;
        gone.retain(|name| !roots.contains(name));
        if strict {
            let surplus = gone.difference(&derived).cloned().collect::<Vec<_>>();
            if !surplus.is_empty() {
                bail!(
                    "scene '{}' takes '{}' out of itself and does not carry {} to take. The two are no longer built on the same thing.",
                    string(&scene["id"])?,
                    other_id,
                    surplus.join(", ")
                );
            }
        }
        derived.retain(|name| !gone.contains(name));
    }
    Ok(derived)
}
fn numeric_spec(root: &Path, assembly: &Value, c: &Value) -> Result<Value> {
    let metadata = assembly.get("metadata").unwrap_or(assembly);
    let checks = assembly.get("checks").cloned().unwrap_or_else(|| json!({}));
    let mut colours = metadata
        .get("logical_rgba")
        .or_else(|| metadata.get("colours"))
        .cloned()
        .unwrap_or_else(|| json!({}));
    let core_names = metadata
        .get("core_body_names")
        .map(rows)
        .transpose()?
        .map(|a| {
            a.iter()
                .map(|v| string(v).map(|s| s.strip_prefix("cold-core/").unwrap_or(s).to_owned()))
                .collect::<Result<Vec<_>>>()
        })
        .transpose()?
        .unwrap_or_default();
    let external = metadata
        .get("core_external_names")
        .map(set)
        .transpose()?
        .unwrap_or_default();
    let equipment = metadata
        .get("core_equipment_names")
        .cloned()
        .unwrap_or_else(|| json!([]));
    let mut promoted = set(&equipment)?;
    promoted.extend(external.clone());
    let mut present = colours
        .as_object()
        .context("scene colours")?
        .keys()
        .cloned()
        .collect::<BTreeSet<_>>();
    present.extend(core_names.iter().map(|n| format!("cold-core/{n}")));
    let aliases = present
        .iter()
        .map(|n| n.rsplit('/').next().unwrap())
        .filter(|n| external.contains(*n))
        .map(str::to_owned)
        .collect::<Vec<_>>();
    present.extend(aliases);
    present.insert("foam-assembly".into());
    let tube_sites = metadata
        .get("tube_anchor_sites")
        .cloned()
        .unwrap_or_else(|| json!([]));
    let mut cap_names = metadata
        .get("cap_anchor_names")
        .map(set)
        .transpose()?
        .unwrap_or_default();
    for row in rows(&tube_sites)? {
        if row[1].get(5).is_some_and(|v| v == "cap") {
            cap_names.insert(format!("anchor-cap-{}", string(&row[0])?));
        }
    }
    let empty_rows = json!([]);
    let empty_map = json!({});
    let mount_rows = checks
        .get("mounts")
        .or_else(|| metadata.get("mounts"))
        .unwrap_or(&empty_rows);
    let rides = checks
        .get("rides")
        .or_else(|| metadata.get("rides"))
        .unwrap_or(&empty_map);
    let pieces = metadata.get("tube_anchor_pieces").unwrap_or(&empty_map);
    let mut holders = holders(
        c,
        mount_rows,
        &tube_sites,
        pieces,
        &equipment,
        &json!({}),
        Some(&present),
        &cap_names,
    )?;
    if let Some(tubes) = metadata.get("manifold_tube_holders") {
        holders
            .as_object_mut()
            .unwrap()
            .extend(tubes.as_object().context("manifold tube holders")?.clone());
        for row in rows(&tube_sites)? {
            let id = string(&row[0])?;
            let tube = format!("tube-{id}");
            if present.contains(&tube) {
                holders[tube] = pieces[id].clone();
            }
        }
    }
    // Above-core ownership takes precedence over the manifold tube map.
    for name in set(&equipment)? {
        if holders.get(&name).is_some() {
            holders[name] = json!("foam-assembly");
        }
    }
    for value in rows(&c["BACK_TOP_CARRIED_COMPONENTS"])?
        .iter()
        .chain(rows(&c["BACK_TOP_CARRIED_TUBES"])?)
        .cloned()
        .chain(std::iter::once(json!("tube-soda-core-rise")))
    {
        let name = string(&value)?;
        if present.contains(name) {
            holders[name] = json!("enclosure-back-top");
        }
    }
    for (rider, host) in rides.as_object().context("riders")? {
        if holders.get(rider).is_some() && holders.get(string(host)?).is_some() {
            holders[rider] = holders[string(host)?].clone();
        }
    }
    let runs = metadata.get("runs").unwrap_or(&empty_rows);
    let conduits = metadata
        .get("cap_conduits")
        .map(set)
        .transpose()?
        .unwrap_or_default();
    let crossings = crossings(runs, &conduits)?;
    for name in &external {
        if let Some(value) = colours.get(format!("cold-core/{name}")).cloned() {
            colours[name] = value;
        }
    }
    let mut views = Vec::new();
    for scene in rows(&c["SCENES"])? {
        let names = named(
            scene,
            c,
            runs,
            &holders,
            &core_names,
            &promoted,
            &crossings,
            false,
        )?;
        let missing = names.difference(&present).cloned().collect::<Vec<_>>();
        ensure!(
            missing.is_empty(),
            "scene '{}' names bodies absent from the model: {:?}",
            string(&scene["id"])?,
            missing
        );
        let mut overrides = json!({});
        for (line, half) in crossings.as_object().unwrap() {
            let half = string(half)?;
            if names.contains(line) && names.contains(half) {
                overrides[line] = colours[half].clone();
            }
        }
        views.push(json!({"id":scene["id"],"bodies":names,"inner":inner(scene,&core_names)?,"flip":scene["flip"],"overrides":overrides}));
    }
    let finishes = if let Some(finishes) = metadata.get("finishes") {
        finishes.clone()
    } else {
        call("_finishes", "rows", json!([]))?
    };
    Ok(
        json!({"outer_payload":assembly.get("payload").cloned().unwrap_or_else(||json!(root.join("hardware/manifold-layout/enclosure-assembly.step.mesh"))),"core_payload":assembly.get("core_payload").cloned().unwrap_or_else(||json!(root.join("hardware/cold-core-layout/cold-core-assembly.step.mesh"))),"core_transform":metadata.get("core_carry3x4"),"colours":colours,"core_colours":metadata.get("core_rgba").cloned().unwrap_or_else(||json!({})),"finishes":finishes,"views":views}),
    )
}
pub fn request(request: &Request) -> Result<Value> {
    let d = &request.data;
    let c = defaults()?;
    match request.op.as_str() {
        "scene_definitions" => Ok(c),
        "scene_back_carried" => {
            let mut values = set(&c["BACK_TOP_CARRIED_COMPONENTS"])?;
            values.extend(set(&c["BACK_TOP_CARRIED_TUBES"])?);
            Ok(json!(values))
        }
        "scene_core_names" => Ok(json!(core_names(&request.root)?)),
        "scene_held_by" => Ok(json!(held(string(&d["root"])?, &d["holders"], &d["stop"])?)),
        "scene_inner" => {
            let names = if d["scene"]["inner"] == "*" {
                core_names(&request.root)?
            } else {
                Vec::new()
            };
            Ok(json!(inner(&d["scene"], &names)?))
        }
        "scene_crossings" => {
            let raw = get("_cold_core_interface", "cap_conduits")?;
            let keys = raw
                .as_object()
                .context("cap conduits")?
                .keys()
                .cloned()
                .collect();
            crossings(&d["runs"], &keys)
        }
        "scene_holders" => legacy_holders(&c, d),
        "scene_runs_for" => {
            runs_for(&set(&d["bodies"])?, &d["runs"], &d["holders"]).map(|v| json!(v))
        }
        "scene_named" => {
            let holders = legacy_holders(&c, d)?;
            let mut promoted = set(&call("above_core", "core_equipment_names", json!([]))?)?;
            promoted.extend(
                d.get("core_external_components")
                    .map(set)
                    .transpose()?
                    .unwrap_or_default(),
            );
            let raw = get("_cold_core_interface", "cap_conduits")?;
            let conduits = raw
                .as_object()
                .context("cap conduits")?
                .keys()
                .cloned()
                .collect();
            let cross = crossings(&d["runs"], &conduits)?;
            Ok(json!(named(
                &d["scene"],
                &c,
                &d["runs"],
                &holders,
                &core_names(&request.root)?,
                &promoted,
                &cross,
                true
            )?))
        }
        "scene_numeric_spec" => numeric_spec(&request.root, &d["assembly"], &c),
        _ => bail!("scene operation {}", request.op),
    }
}
