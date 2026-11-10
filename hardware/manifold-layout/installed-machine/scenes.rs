//! The machine's scene views for the /3d viewer: which bodies each named scene draws and in what
//! colour and finish, from the plan, the physical model's bodies and the fastening rules the
//! machine checks hold, as the GLB writer takes them.
use anyhow::{Context, Result, bail, ensure};
use serde_json::{Map, Value, json};
use std::collections::{BTreeMap, BTreeSet};
use std::io::Read;
use std::path::Path;

/// The named scenes as the assembly docs write them down.
#[allow(dead_code)]
#[path = "../../../tools/hsm/assembly-docs/src/wiring/scenes/scene_records.rs"]
mod scene_records;

/// The cold core's casing, which a scene that opens the core draws as its inner bodies instead.
const INNER_ROOT: &str = "foam-assembly";
/// The prefix the cold core's own bodies carry in the machine's model.
const CORE: &str = "cold-core/";
/// The fastening table and the riders the machine checks hold.
const RULES: &str = "hardware/manifold-layout/machine_check_rules.json";
/// The scenes' constants: the carried bodies, the bodies each piece bears on.
const SCENE_CONSTANTS: &str = "tools/hsm/assembly-docs/src/wiring/scene-constants.json";
/// The cold core's published viewer payload, which the scenes that open the core draw from.
const CORE_PAYLOAD: &str = "hardware/cold-core-layout/cold-core-assembly.step.mesh";

/// The views spec the GLB writer cuts every scene from: the plan `spec` placed the bodies whose
/// fine model is `physical_model` and whose viewer payload is `payload`.
pub fn views_spec(root: &Path, spec: &Value, physical_model: &Path, payload: &Path) -> Result<Value> {
    let metadata = &spec["metadata"];
    let constants = constants(root)?;
    let scenes = scenes(&constants)?;
    let rules = crate::design::read(root.join(RULES))?;
    let identity = identity(physical_model)?;
    let mut colours = colours(&identity, metadata)?;
    let core_colours: Map<String, Value> = colours
        .iter()
        .filter_map(|(name, rgba)| name.strip_prefix(CORE).map(|n| (n.to_owned(), rgba.clone())))
        .collect();
    let core_names: Vec<String> = strings(&metadata["core_body_names"])
        .into_iter()
        .map(|n| n.strip_prefix(CORE).map(str::to_owned).unwrap_or(n))
        .collect();
    let external: BTreeSet<String> = strings(&metadata["core_external_names"]).into_iter().collect();
    let equipment = strings(&metadata["core_equipment_names"]);
    let promoted: BTreeSet<String> = equipment.iter().cloned().chain(external.iter().cloned()).collect();

    let mut present: BTreeSet<String> = colours.keys().cloned().collect();
    present.extend(core_names.iter().map(|n| format!("{CORE}{n}")));
    let aliases: Vec<String> = present.iter().map(|n| last(n).to_owned()).filter(|n| external.contains(n)).collect();
    present.extend(aliases);
    present.insert(INNER_ROOT.to_owned());

    let holders = holders(&constants, &mounts(spec, &identity, &rules)?, &rules["rides"], metadata, &present, &equipment)?;
    let runs = metadata["runs"].as_array().cloned().unwrap_or_default();
    let conduits: BTreeSet<String> = strings(&metadata["cap_conduits"]).into_iter().collect();
    let crossings = crossings(&runs, &conduits)?;
    for name in &external {
        if let Some(rgba) = colours.get(&format!("{CORE}{name}")).cloned() {
            colours.insert(name.clone(), rgba);
        }
    }
    let world = World { scenes: &scenes, holders: &holders, runs: &runs, core_names: &core_names,
                        promoted: &promoted, crossings: &crossings, bare: &strings(&constants["BARE"]) };
    let mut views = Vec::new();
    for scene in &scenes {
        let names = world.named(scene)?;
        let missing: Vec<&String> = names.difference(&present).collect();
        ensure!(missing.is_empty(), "scene '{}' names bodies absent from the model: {missing:?}", scene.id);
        let mut overrides = Map::new();
        for (line, half) in &crossings {
            if names.contains(line) && names.contains(half) {
                overrides.insert(line.clone(), colours.get(half).cloned().unwrap_or(Value::Null));
            }
        }
        views.push(json!({"id": scene.id, "bodies": names, "inner": world.inner(scene), "flip": scene.flip,
                          "overrides": overrides}));
    }
    Ok(json!({
        "op": "views",
        "outer_payload": payload,
        "core_payload": root.join(CORE_PAYLOAD),
        "core_transform": metadata["core_carry"],
        "colours": colours,
        "core_colours": core_colours,
        "finishes": finishes(root)?,
        "views": views,
    }))
}

/// One named scene: the pieces it starts from, the core bodies it opens, the bodies it adds,
/// holds back or takes away with another scene, and how it is turned to be looked at.
struct Scene {
    id: String,
    roots: BTreeSet<String>,
    inner: Inner,
    flip: Value,
    also: BTreeSet<String>,
    later: BTreeSet<String>,
    without: Option<String>,
}

/// The cold core bodies a scene opens: none, every one, or the ones it names.
enum Inner {
    None,
    All,
    Named(Vec<String>),
}

/// The scene constants as written down, with the fastener and nut names they spell out.
fn constants(root: &Path) -> Result<Value> {
    let mut c = crate::design::read(root.join(SCENE_CONSTANTS))?;
    let carried = c["BACK_TOP_CARRIED_COMPONENTS"].as_array_mut().context("the back top's carried bodies")?;
    for name in ["psu", "relay-1", "relay-2"] {
        for kind in ["screw", "insert"] {
            let numbers: &[u32] = if name == "psu" { &[1, 2, 3, 4] } else { &[1, 4] };
            carried.extend(numbers.iter().map(|n| json!(format!("{name}-{kind}-{n}"))));
        }
    }
    for fitting in ["bulkhead-carb", "bulkhead-drain", "bulkhead-flavor-a", "bulkhead-flavor-b"] {
        carried.push(json!(fitting));
        carried.push(json!(format!("{fitting}-nut")));
    }
    for fitting in ["bulkhead-water", "bulkhead-carb", "bulkhead-drain", "bulkhead-flavor-a", "bulkhead-flavor-b", "co2-inlet"] {
        c["BEARS_ON"][format!("{fitting}-nut")] = json!(fitting);
    }
    for tee in ["y-c", "y-d", "y-f", "y-g"] {
        c["BEARS_ON"][format!("tee-{tee}")] = json!("enclosure-front-top");
    }
    Ok(c)
}

/// The named scenes, in the order the viewer lists them.
fn scenes(constants: &Value) -> Result<Vec<Scene>> {
    let rows = scene_records::rows(constants);
    rows.as_array().context("the scene records")?.iter().map(|row| {
        let inner = match &row["inner"] {
            Value::String(all) if all == "*" => Inner::All,
            Value::Array(names) if !names.is_empty() => Inner::Named(strings(&Value::Array(names.clone()))),
            Value::Array(_) | Value::Null => Inner::None,
            other => bail!("a scene's inner bodies are {other}"),
        };
        Ok(Scene {
            id: row["id"].as_str().context("a scene's id")?.to_owned(),
            roots: strings(&row["roots"]).into_iter().collect(),
            inner,
            flip: row["flip"].clone(),
            also: strings(&row["also"]).into_iter().collect(),
            later: strings(&row["later"]).into_iter().collect(),
            without: row["without"].as_str().map(str::to_owned),
        })
    }).collect()
}

/// A row of the fastening table: the body, and the piece it bears on where it names one.
struct Mount {
    body: String,
    holder: Option<String>,
}

/// The fastening table the machine checks hold, kept to the bodies the model places: the
/// table's own rows, the rows its selected fittings and stated fasteners spell out, and every
/// placed body the table does not name as one that comes with the pack.
fn mounts(spec: &Value, identity: &[(String, Option<[f64; 3]>)], rules: &Value) -> Result<Vec<Mount>> {
    let placed = placed_bodies(spec, identity);
    let mut rows: Vec<Mount> = rules["mounts"].as_array().into_iter().flatten().cloned()
        .chain(selected_mounts(&spec["metadata"], rules))
        .map(|row| Mount { body: row[0].as_str().unwrap_or_default().to_owned(),
                           holder: row[1].as_str().filter(|s| !s.is_empty()).map(str::to_owned) })
        .filter(|m| placed.contains(&m.body))
        .collect();
    let named: BTreeSet<String> = rows.iter().map(|m| m.body.clone()).collect();
    rows.extend(placed.difference(&named).map(|body| Mount { body: body.clone(), holder: None }));
    Ok(rows)
}

/// The bodies the machine checks question: every body of the physical model under its machine
/// name, and the cold core's casing, less the core's own inside bodies, the wiring, the
/// enclosure's pieces and the drawn tubes.
fn placed_bodies(spec: &Value, identity: &[(String, Option<[f64; 3]>)]) -> BTreeSet<String> {
    let metadata = &spec["metadata"];
    let core: BTreeSet<String> = strings(&metadata["core_body_names"]).into_iter().collect();
    let external: BTreeSet<String> = strings(&metadata["core_external_names"]).into_iter().collect();
    let wiring: BTreeSet<String> = strings(&metadata["wiring_names"]).into_iter().collect();
    let mut out = BTreeSet::new();
    for name in identity.iter().map(|(name, _)| base(name)).chain(std::iter::once(INNER_ROOT)) {
        let name = spec["aliases"].get(name).and_then(Value::as_str).unwrap_or(name);
        let tail = last(name);
        let inside = (core.contains(name) || name.starts_with(CORE)) && !external.contains(tail);
        let drawn = ["tube-", "turn-", "step-", "stub-"].iter().any(|p| name.starts_with(p));
        if wiring.contains(name) || tail.starts_with("wire-") || inside || name.starts_with("enclosure-") || drawn {
            continue;
        }
        out.insert(name.to_owned());
    }
    out
}

/// The fastening rows the plan's selected fittings and stated fasteners spell out, in the
/// order the machine checks spell them.
fn selected_mounts(m: &Value, rules: &Value) -> Vec<Value> {
    let mut fittings: BTreeMap<String, Value> = object(&rules["selected_fittings"]);
    for (name, r) in plans(&m["union_supports"]) {
        if r["support_implemented"] == true {
            fittings.insert(name, json!([r["parent"], "cradle"]));
        }
    }
    let selected: Vec<String> = if m["selected_fitting_names"].is_array() {
        strings(&m["selected_fitting_names"])
    } else {
        fittings.keys().cloned().collect()
    };
    let mut rows: Vec<Value> = selected.iter()
        .filter_map(|n| fittings.get(n).map(|v| json!([n, v[0], v[1]])))
        .collect();
    rows.extend(rules["selected_fixed_mounts"].as_array().into_iter().flatten().cloned());
    for side in ["suction", "discharge"] {
        for part in ["reducer", "barb-clamp", "barb-key", "stem-clamp", "stem-key"] {
            rows.push(json!([format!("{side}-{part}"), format!("{side}-tube"), "clamped-joint"]));
        }
        rows.push(json!([format!("{side}-tube"), "g-ganen-pump", "barb"]));
    }
    for (name, plan) in plans(&m["wall_mount_datums"]) {
        for (i, s) in plan["stations"].as_array().into_iter().flatten().enumerate() {
            if s["threaded"] == true {
                for (kind, joint) in [("screw", "thread"), ("insert", "heat-set")] {
                    rows.push(json!([format!("{name}-{kind}-{}", i + 1), "enclosure-back-top", joint]));
                }
            }
        }
    }
    for column in m["fluid_grid_assignment"].as_array().into_iter().flatten() {
        for name in strings(column) {
            if !["bulkhead-water", "co2-inlet"].contains(&name.as_str()) {
                rows.push(json!([format!("{name}-nut"), name, "thread"]));
            }
        }
    }
    for (name, r) in plans(&m["funnel_fasteners"]) {
        let host = r["host"].as_str().map(str::to_owned)
            .unwrap_or_else(|| format!("enclosure-{}-top", r["col"].as_str().unwrap_or("front")));
        let base = if name.starts_with("funnel-frame-") { name } else { format!("funnel-frame-{name}") };
        for (kind, joint) in [("screw", "thread"), ("insert", "heat-set")] {
            rows.push(json!([format!("{base}-{kind}"), host, joint]));
        }
    }
    for side in ["west", "east"] {
        for (station, host) in [("lower", "back-bottom"), ("upper", "front-top")] {
            for (kind, joint) in [("screw", "thread"), ("insert", "heat-set")] {
                rows.push(json!([format!("y-seam-{side}-{station}-{kind}"), format!("enclosure-{host}"), joint]));
            }
        }
    }
    rows.extend(m["selected_mounts"].as_array().into_iter().flatten().cloned());
    rows
}

/// Which piece holds each body, so a scene knows what comes with the pieces it draws: the
/// fastening table, the manifold's tubes, the core equipment on the casing, the back top's
/// carried bodies, and riders taking their host's holder.
fn holders(
    constants: &Value,
    mounts: &[Mount],
    rides: &Value,
    metadata: &Value,
    present: &BTreeSet<String>,
    equipment: &[String],
) -> Result<BTreeMap<String, Option<String>>> {
    let bears_on = &constants["BEARS_ON"];
    let mut caps: BTreeSet<String> = strings(&metadata["cap_anchor_names"]).into_iter().collect();
    let sites = metadata["tube_anchor_sites"].as_array().cloned().unwrap_or_default();
    for row in &sites {
        if row[1].get(5).is_some_and(|v| v == "cap") {
            caps.insert(format!("anchor-cap-{}", row[0].as_str().context("a tube anchor's run")?));
        }
    }
    let mut out: BTreeMap<String, Option<String>> = BTreeMap::new();
    for mount in mounts {
        if mount.body.starts_with("anchor-cap-") && !caps.contains(&mount.body) {
            continue;
        }
        let by = mount.holder.clone().or_else(|| bears_on[&mount.body].as_str().map(str::to_owned));
        out.insert(mount.body.clone(), by);
    }
    for (tube, by) in metadata["manifold_tube_holders"].as_object().into_iter().flatten() {
        out.insert(tube.clone(), by.as_str().map(str::to_owned));
    }
    for row in &sites {
        let run = row[0].as_str().context("a tube anchor's run")?;
        let tube = format!("tube-{run}");
        if present.contains(&tube) {
            out.insert(tube, metadata["tube_anchor_pieces"][run].as_str().map(str::to_owned));
        }
    }
    for name in equipment {
        if let Some(by) = out.get_mut(name) {
            *by = Some(INNER_ROOT.to_owned());
        }
    }
    let carried = constants["BACK_TOP_CARRIED_COMPONENTS"].as_array().into_iter().flatten()
        .chain(constants["BACK_TOP_CARRIED_TUBES"].as_array().into_iter().flatten())
        .filter_map(Value::as_str)
        .chain(std::iter::once("tube-soda-core-rise"));
    for name in carried {
        if present.contains(name) {
            out.insert(name.to_owned(), Some("enclosure-back-top".to_owned()));
        }
    }
    for (rider, host) in rides.as_object().into_iter().flatten() {
        let host = host.as_str().context("a rider's host")?;
        if out.contains_key(rider) && out.contains_key(host) {
            let by = out[host].clone();
            out.insert(rider.clone(), by);
        }
    }
    Ok(out)
}

/// The core conduit lines whose tube continues outside the core, each to that tube's name.
fn crossings(runs: &[Value], conduits: &BTreeSet<String>) -> Result<BTreeMap<String, String>> {
    let mut out = BTreeMap::new();
    for run in runs {
        for end in [&run["frm"], &run["to"]] {
            if let Some((part, mouth)) = end.as_str().context("a run's end")?.split_once('.')
                && part == INNER_ROOT && conduits.contains(mouth)
            {
                out.insert(format!("{CORE}line-{mouth}"), format!("tube-{}", run["id"].as_str().context("a run's id")?));
            }
        }
    }
    Ok(out)
}

/// What the scenes are composed over: the holders, the runs and the core's bodies.
struct World<'a> {
    scenes: &'a [Scene],
    holders: &'a BTreeMap<String, Option<String>>,
    runs: &'a [Value],
    core_names: &'a [String],
    promoted: &'a BTreeSet<String>,
    crossings: &'a BTreeMap<String, String>,
    bare: &'a [String],
}

impl World<'_> {
    /// The bodies `root` holds, directly or through what it holds, stopping at `stop`.
    fn held(&self, root: &str, stop: &BTreeSet<String>) -> BTreeSet<String> {
        let mut out = BTreeSet::new();
        let mut queue = vec![root.to_owned()];
        while let Some(node) = queue.pop() {
            if out.contains(&node) || stop.contains(&node) {
                continue;
            }
            out.insert(node.clone());
            for (name, by) in self.holders {
                if by.as_deref() == Some(node.as_str()) && !out.contains(name) {
                    queue.push(name.clone());
                }
            }
        }
        out
    }

    /// The cold core bodies `scene` opens, under their machine names.
    fn inner(&self, scene: &Scene) -> BTreeSet<String> {
        let names: &[String] = match &scene.inner {
            Inner::None => &[],
            Inner::All => self.core_names,
            Inner::Named(names) => names,
        };
        names.iter().map(|n| format!("{CORE}{n}")).collect()
    }

    /// The bodies `scene` draws.
    fn named(&self, scene: &Scene) -> Result<BTreeSet<String>> {
        let mut bodies = BTreeSet::new();
        for root in &scene.roots {
            bodies.extend(self.held(root, &scene.later));
        }
        let mut derived = if self.bare.contains(&scene.id) {
            scene.roots.clone()
        } else {
            let mut all = bodies.clone();
            for run in self.runs {
                let id = format!("tube-{}", run["id"].as_str().context("a run's id")?);
                let end = |key: &str| run[key].as_str().unwrap_or_default().split('.').next().unwrap_or_default().to_owned();
                let held = self.holders.get(&id).and_then(|by| by.as_deref()).is_some_and(|by| bodies.contains(by));
                if held || (bodies.contains(&end("frm")) && bodies.contains(&end("to"))) {
                    all.insert(id);
                }
            }
            all
        };
        derived.retain(|name| !scene.later.contains(name));
        let inner = self.inner(scene);
        if !inner.is_empty() {
            derived.remove(INNER_ROOT);
            derived.extend(inner.difference(&scene.later).cloned());
        }
        self.unpromote(&mut derived);
        derived.extend(scene.also.iter().cloned());
        for (line, half) in self.crossings {
            if derived.contains(line) {
                derived.insert(half.clone());
            }
        }
        derived.retain(|name| !scene.later.contains(name));
        self.unpromote(&mut derived);
        if let Some(other) = &scene.without {
            let other = self.scenes.iter().find(|s| &s.id == other).with_context(|| format!("no scene {other}"))?;
            let gone = self.named(other)?;
            derived.retain(|name| !gone.contains(name) || scene.roots.contains(name));
        }
        Ok(derived)
    }

    /// Takes out the core's copy of each body the machine draws in its own right.
    fn unpromote(&self, derived: &mut BTreeSet<String>) {
        for name in self.promoted {
            if derived.contains(name) {
                derived.remove(&format!("{CORE}{name}"));
            }
        }
    }
}

/// Each body's linear RGBA as the viewer draws it: the physical model's colour, and the
/// opacity the cold core states for its own bodies or else the catalog's for the material of
/// that colour.
fn colours(identity: &[(String, Option<[f64; 3]>)], metadata: &Value) -> Result<Map<String, Value>> {
    let stated = &metadata["core_alpha_by_name"];
    let translucent = translucent_materials()?;
    let mut out = Map::new();
    for (name, color) in identity {
        let name = base(name);
        let Some(rgb) = color else { continue };
        let logical = name.strip_prefix(CORE).unwrap_or(name);
        let rgb = rgb.map(|c| c as f32 as f64);
        let alpha = match stated[logical].as_f64() {
            Some(alpha) => alpha,
            None => translucent.iter().find(|(colour, _)| *colour == rgb).map_or(1., |(_, alpha)| *alpha),
        };
        out.insert(name.to_owned(), json!([rgb[0], rgb[1], rgb[2], alpha as f32 as f64]));
    }
    Ok(out)
}

/// The catalog's see-through materials, each as the linear RGB its bodies carry and its opacity.
fn translucent_materials() -> Result<Vec<([f64; 3], f64)>> {
    let catalog = crate::color::dispatch("catalog", &json!({}))?;
    let mut out = Vec::new();
    for (name, args) in catalog["colors"].as_object().context("the materials catalog's colours")? {
        if let Some(alpha) = args.as_array().filter(|a| a.len() >= 4).and_then(|a| a[3].as_f64()) {
            if alpha < 1. {
                out.push((crate::design::material(name)?, alpha));
            }
        }
    }
    Ok(out)
}

/// How each material colour takes the light: the materials catalog's finishes, the port chips'
/// filaments at the finish of the PET-GF they print in, and the tube stock's spools, merged by
/// the shared colour code as the website's finish table is.
fn finishes(root: &Path) -> Result<Value> {
    let catalog = crate::color::dispatch("catalog", &json!({}))?;
    let routing = crate::design::read(root.join("tools/hsm/shared-data/catalog/routing.json"))?;
    Ok(json!(crate::color::catalog_finishes(&catalog, &routing)?))
}

/// The bodies of the fine model at `path`, each with its colour where it has one, read from the
/// model's names and colours alone.
fn identity(path: &Path) -> Result<Vec<(String, Option<[f64; 3]>)>> {
    crate::design::record(path);
    let file = std::fs::File::open(path).with_context(|| format!("reading {}", path.display()))?;
    let mut archive = zip::ZipArchive::new(std::io::BufReader::new(file))
        .with_context(|| format!("reading model {}", path.display()))?;
    let mut member = |name: &str| -> Result<Value> {
        let mut bytes = Vec::new();
        archive.by_name(name)?.read_to_end(&mut bytes)?;
        ensure!(bytes.len() > 10 && bytes.starts_with(b"\x93NUMPY"), "{name} is not an array");
        let (start, size) = if bytes[6] == 1 {
            (10, u16::from_le_bytes([bytes[8], bytes[9]]) as usize)
        } else {
            (12, u32::from_le_bytes([bytes[8], bytes[9], bytes[10], bytes[11]]) as usize)
        };
        Ok(serde_json::from_slice(&bytes[start + size..])?)
    };
    let names: Vec<String> = serde_json::from_value(member("names.npy")?)?;
    let colors: Vec<Option<[f64; 3]>> = serde_json::from_value(member("colors.npy")?)?;
    ensure!(names.len() == colors.len(), "{} names {} bodies and colours {}", path.display(), names.len(), colors.len());
    Ok(names.into_iter().zip(colors).collect())
}

/// `name` without the solid number a body of several solids carries.
fn base(name: &str) -> &str {
    match name.rsplit_once('/') {
        Some((head, tail)) if !tail.is_empty() && tail.chars().all(|c| c.is_ascii_digit()) => head,
        _ => name,
    }
}

/// The last path segment of a body name.
fn last(name: &str) -> &str {
    name.rsplit('/').next().unwrap_or(name)
}

/// The texts of a list, or none.
fn strings(value: &Value) -> Vec<String> {
    value.as_array().into_iter().flatten().filter_map(Value::as_str).map(str::to_owned).collect()
}

/// An object's entries, or none.
fn object(value: &Value) -> BTreeMap<String, Value> {
    value.as_object().map(|o| o.iter().map(|(k, v)| (k.clone(), v.clone())).collect()).unwrap_or_default()
}

/// A plan's records by name: an object's entries, or a list's rows by their `name` or position.
fn plans(value: &Value) -> Vec<(String, Value)> {
    if value.is_object() {
        object(value).into_iter().collect()
    } else {
        value.as_array().into_iter().flatten().enumerate()
            .map(|(i, v)| (v.get("name").and_then(Value::as_str).map(str::to_owned).unwrap_or_else(|| i.to_string()), v.clone()))
            .collect()
    }
}
