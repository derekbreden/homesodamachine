//! The request the equipment program cuts from: the installed machine's equipment placed around
//! the pack the placement program set down, and the warm-side tubes run between their ports.
use crate::{color, design, equipment};
use anyhow::{Context, Result};
use hsm_layout_data::{rear, routes, soda};
use serde::Deserialize;
use serde::de::{DeserializeOwned, IgnoredAny, MapAccess, Visitor};
use serde_json::{Map, Value, json};
use std::path::Path;

#[allow(dead_code)]
#[path = "../../../tools/hsm/machine-data/src/archive.rs"]
mod archive;

/// The bodies the soda inlet's foam sleeve is pressed against where it is fitted.
const SOFT_NEIGHBORS: &[&str] = &["vk-solenoid", "g-ganen-pump", "suction-tube", "suction-barb-clamp"];

/// The materials the equipment recipe colours its bodies in, by their catalog names.
const PALETTE: &[&str] = &[
    "C_PCBA",
    "C_PSU",
    "C_RELAY",
    "C_C14",
    "M_BRASS",
    "C_DIGITEN",
    "C_VALVE",
    "M_DONOR_BLACK",
    "M_PETGF_BLACK",
    "M_TPU_BLACK",
    "M_JG_BLACK_PP",
    "M_NEOFIT_WHITE_ACETAL",
    "M_NEOFIT_ACETAL",
    "M_JG_WHITE_PP",
    "M_STAINLESS",
    "M_POM_ORANGE",
    "M_PVC_CLEAR",
    "M_NITRILE_BLACK",
    "M_JG_GREY_ACETAL",
];

/// The purchased parts the recipe sizes its fittings from: the name it reads each by, and its
/// reference directory.
const PARAMETERS: &[(&str, &str)] = &[
    ("stem", "neofit-stem-elbow"),
    ("reducer", "jg-pp061208w"),
    ("check", "neofit-acvus44-check"),
    ("chain", "asse1022-threaded-chain"),
    ("pump", "g-ganen-pump"),
    ("jg", "jg-bulkhead-union"),
    ("drain", "neofit-drain-bulkhead"),
];

/// The keys of a JSON object, in the order its file writes them.
struct Keys(Vec<String>);

impl<'de> Deserialize<'de> for Keys {
    /// Collects an object's keys in file order and skips their values.
    fn deserialize<D: serde::Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        /// Walks one object, keeping its keys.
        struct Walk;
        impl<'de> Visitor<'de> for Walk {
            type Value = Keys;
            /// Says what the walk reads.
            fn expecting(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
                f.write_str("a JSON object")
            }
            /// Keeps each key of the object as it comes.
            fn visit_map<A: MapAccess<'de>>(self, mut map: A) -> Result<Keys, A::Error> {
                let mut keys = vec![];
                while let Some(key) = map.next_key::<String>()? {
                    map.next_value::<IgnoredAny>()?;
                    keys.push(key);
                }
                Ok(Keys(keys))
            }
        }
        deserializer.deserialize_map(Walk)
    }
}

/// The order `above-core.json` authors its fore tubes in.
#[derive(Deserialize)]
struct AboveCoreOrder {
    fore_routes: ForeOrder,
}

/// The fore routes' tubes, in authored order.
#[derive(Deserialize)]
struct ForeOrder {
    tubes: Keys,
}

/// The order `reservoir-a-routes.json` authors Reservoir A's paths in.
#[derive(Deserialize)]
struct ReservoirOrder {
    paths: Keys,
}

/// A design file, read whole, with the order of the objects `T` names in it.
fn read_ordered<T: DeserializeOwned>(path: &Path) -> Result<(Value, T)> {
    let value = design::read(path)?;
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    let order = serde_json::from_slice(&bytes).with_context(|| format!("the key order of {}", path.display()))?;
    Ok((value, order))
}

/// The purchased parts' published dimensions, and where the backflow preventer's ports are on it.
fn parameters(root: &Path) -> Result<Value> {
    let reference = root.join("hardware/reference");
    let mut data = Map::new();
    for &(name, directory) in PARAMETERS {
        data.insert(name.to_owned(), design::read(reference.join(directory).join("reference-parameters.json"))?);
    }
    let check = design::read(reference.join("multiplex-asse1022/scan-model-check.json"))?;
    let ports = &check["interfaces"];
    data.insert(
        "multiplex_ports".to_owned(),
        json!({"inlet": ports["inlet"], "outlet": ports["outlet"], "vent": ports["vent"]}),
    );
    Ok(Value::Object(data))
}

/// The ports of every body the placement program set down, in the world, as `[point, axis, bore]`.
fn pack_ports(prepared: &Value) -> Result<Map<String, Value>> {
    let frames = prepared["metadata"]["frames"].as_object().context("the placed pack's frames")?;
    let mut out = Map::new();
    for (name, frame) in frames {
        let ports = frame["ports"].as_object().with_context(|| format!("{name}'s ports"))?;
        let rows = ports.iter().map(|(port, row)| (port.clone(), json!([row["pos"], row["axis"], row["diam"]])));
        out.insert(name.clone(), Value::Object(rows.collect()));
    }
    Ok(out)
}

/// Whether a fine model carries a drawing of its own beside its geometry.
fn presented(path: &Path) -> Result<bool> {
    let document = archive::metadata(&json!({"path": path, "kind": "document"}))?;
    let declared = document.get("presentation").is_some_and(stated);
    let name = path.to_string_lossy();
    let mesh = name.strip_suffix(".npz").is_some_and(|stem| Path::new(&format!("{stem}.mesh")).is_file());
    Ok(declared || mesh)
}

/// The file each equipment model is read from, and whether a fine one brings its own drawing.
fn sources(root: &Path) -> Result<Value> {
    let mut out = Map::new();
    for relative in equipment::SOURCES {
        let path = design::source(root, relative, design::Use::Equipment)?;
        let mut row = json!({"path": path});
        if path.extension().is_some_and(|e| e == "npz") {
            row["presentation"] = json!(presented(&path)?);
        }
        out.insert((*relative).to_owned(), row);
    }
    Ok(Value::Object(out))
}

/// The palette's colours as the viewer's files carry them.
fn palette() -> Result<Value> {
    let mut out = Map::new();
    for &name in PALETTE {
        out.insert(name.to_owned(), json!(design::material(name)?));
    }
    Ok(Value::Object(out))
}

/// Each tube spool's colour as the viewer's files carry it, from its bytes or its fluid's mark.
fn spool_colors(root: &Path) -> Result<Value> {
    let catalog = design::read(root.join("tools/hsm/shared-data/catalog/routing.json"))?;
    let marks = color::chips()?;
    let mut out = Map::new();
    for (name, spool) in catalog["spools"].as_object().context("the routing catalog's spools")? {
        let own = &spool["color"];
        let rgb = if own["bytes"].is_array() {
            &own["bytes"]
        } else {
            let fluid = own["palette"].as_str().with_context(|| format!("spool {name}'s colour"))?;
            &marks["port_colors"][fluid]
        };
        out.insert(name.clone(), json!(color::rgb8_linear(rgb, false)?));
    }
    Ok(Value::Object(out))
}

/// Every placed port as a route station, keyed `body.port`.
fn stations(world_ports: &Value) -> Result<Value> {
    let mut out = Map::new();
    for (name, ports) in world_ports.as_object().context("the placed ports")? {
        for (port, row) in ports.as_object().with_context(|| format!("{name}'s placed ports"))? {
            out.insert(format!("{name}.{port}"), row.clone());
        }
    }
    Ok(Value::Object(out))
}

/// Routes as `[name, route]` pairs, in their order.
fn pairs(routes: Vec<(String, Value)>) -> Value {
    Value::Array(routes.into_iter().map(|(name, route)| json!([name, route])).collect())
}

/// The warm-side tubes run between the placed ports, in the order they are swept.
fn warm_routes(root: &Path, spec: &Value, data: &Value, world_ports: &Value) -> Result<Vec<(String, Value)>> {
    let stations = stations(world_ports)?;
    let continuations = rear::continuations(spec, &stations, &equipment::route_params(data)?)?;
    let flavors = rear::flavor_routes(&stations)?;
    let (authored, order) =
        read_ordered::<ReservoirOrder>(&root.join("hardware/manifold-layout/reservoir-a-routes.json"))?;
    let reservoir = hsm_layout_data::reservoir_routes(&authored)?;
    let reservoir: Vec<Value> = order.paths.0.iter().map(|name| json!([name, reservoir[name]])).collect();
    let result = routes::specifications(&json!({"spec": spec, "stations": stations,
        "continuations": pairs(continuations), "flavors": pairs(flavors), "reservoir": reservoir}))?;
    let rows = result["routes"].as_array().context("the warm routes")?;
    rows.iter()
        .map(|row| Ok((row[0].as_str().context("a warm route's name")?.to_owned(), row[1].clone())))
        .collect()
}

/// Whether a JSON value states something: present, and neither false, zero nor empty.
fn stated(value: &Value) -> bool {
    match value {
        Value::Null => false,
        Value::Bool(flag) => *flag,
        Value::Number(n) => n.as_f64() != Some(0.),
        Value::String(text) => !text.is_empty(),
        Value::Array(rows) => !rows.is_empty(),
        Value::Object(map) => !map.is_empty(),
    }
}

/// A body's port table cut down to the ports the recipe names for it, in its order.
fn keep_named(ports: &mut Value, names: &Value) -> Result<()> {
    let held = ports.as_object().context("a port table")?;
    let kept: Map<String, Value> = names
        .as_array()
        .context("a body's port names")?
        .iter()
        .filter_map(Value::as_str)
        .filter_map(|port| held.get(port).map(|row| (port.to_owned(), row.clone())))
        .collect();
    *ports = Value::Object(kept);
    Ok(())
}

/// The equipment program's request, around the pack the placement program set down in `prepared`.
pub fn equipment_request(root: &Path, prepared: &Value) -> Result<Value> {
    let (spec, order) = read_ordered::<AboveCoreOrder>(&root.join("hardware/manifold-layout/above-core.json"))?;
    let data = parameters(root)?;
    let pump = design::read(root.join("hardware/printed-parts/cold-core/foam-cap/foam-cap.numbers.json"))?;
    let placed = equipment::numbers(&json!({
        "spec": spec, "data": data, "fore_tube_order": order.fore_routes.tubes.0,
        "external_ports": pack_ports(prepared)?, "sources": sources(root)?, "colors": palette()?,
        "pump_cap": pump["pump"], "insulation_plan": soda::plan(&spec)?, "soft_neighbors": SOFT_NEIGHBORS,
    }))?;
    let warm = warm_routes(root, &spec, &data, &placed["world_ports"])?;
    let names: Vec<&str> = warm.iter().map(|(name, _)| name.as_str()).collect();
    let mut request = equipment::finalize(&json!({
        "equipment": placed, "integrated_order": names,
        "integrated_routes": warm.iter().cloned().collect::<Map<_, _>>(),
        "extra_routes": [], "spool_colors": spool_colors(root)?,
    }))?;
    let named = request
        .as_object_mut()
        .and_then(|fields| fields.remove("_frame_port_order"))
        .context("the frames' port names")?;
    for (name, frame) in request["frames"].as_object_mut().context("the equipment frames")? {
        if let Some(names) = named.get(name) {
            keep_named(&mut frame["ports"], names)?;
        }
    }
    for (name, ports) in request["world_ports"].as_object_mut().context("the placed ports")? {
        if let Some(names) = named.get(name) {
            keep_named(ports, names)?;
        }
    }
    Ok(request)
}
