//! The wiring context and reports the machine program answers from its reference plan.
//!
//! Each report is one request to the machine program (`_rust_data.request`), its arguments
//! flattened to plain data first; the scalar namespace is a `SimpleNamespace` of provider
//! modules and authored turns that the wiring recipes read.
use super::num::Num;
use super::rt::{Ns, Rt, keyword_items};
use super::{docs, py};
use anyhow::{Context, Result, ensure};
use hsm_documents::interop::{self, Val};
use py::s;
use std::io::Read;
use std::path::{Path, PathBuf};

/// Not yet compared with the generated build: the hybrid development build runs the generated namespace.
pub const TYPED: bool = false;

const MODULE: &str = "_machine_reporting";

struct State {
    root: PathBuf,
    hw: PathBuf,
    layout: PathBuf,
    hashlib: Val,
    importlib: Val,
    json: Val,
    time: Val,
    simple_namespace: Val,
    anchor_sites: Val,
}

fn state(rt: &Rt) -> Result<std::rc::Rc<State>> {
    rt.state::<State>(MODULE)
}

/// The directories the reports import their providers from, put on `sys.path` once.
const PATHS: [&str; 12] = [
    "scripts",
    "manifold-layout",
    "cold-core-layout",
    "printed-parts/cold-core",
    "printed-parts/cold-core/foam-assembly",
    "printed-parts/enclosure/enclosure",
    "printed-parts/enclosure/bulkhead-ring",
    "printed-parts/enclosure/pump-tray",
    "printed-parts/electronics/pcba-tray",
    "reference/digiten-flow-sensor",
    "reference/sf76e-thermal-fuse",
    "reference/jg-bulkhead-union",
];

fn paths(rt: &Rt, st: &State) -> Result<()> {
    let mut all = vec![st.root.clone()];
    all.extend(PATHS.iter().map(|p| st.hw.join(p)));
    for path in all {
        let text = py::path_str(&path);
        if !py::sys_path_has(rt, &text)? {
            py::sys_path_insert(rt, &text)?;
        }
    }
    Ok(())
}

/// `isinstance(value, kinds)` as the runtime answers it: by variant for local values, by the
/// interpreter for provider objects.
fn is_kind(value: &Val, kinds: &[&str]) -> Result<bool> {
    if matches!(value, Val::Ref(_)) {
        let kind = if kinds.len() == 1 {
            Val::Type(kinds[0].into())
        } else {
            Val::Tuple(kinds.iter().map(|k| Val::Type((*k).into())).collect())
        };
        return interop::builtin("isinstance").context("isinstance")?.call(vec![value.clone(), kind], vec![])?.truthy();
    }
    Ok(kinds.iter().any(|kind| match *kind {
        "dict" => matches!(value, Val::Dict(_)),
        "tuple" => matches!(value, Val::Tuple(_)),
        "list" => matches!(value, Val::List(_)),
        "set" => matches!(value, Val::Set(_)),
        "frozenset" => matches!(value, Val::FrozenSet(_)),
        "Path" => matches!(value, Val::Path(_)),
        _ => false,
    }))
}

/// `mapping.items()`, as key and value pairs.
fn items(value: &Val) -> Result<Vec<(Val, Val)>> {
    if let Val::Dict(rows) = value {
        return Ok(rows.borrow().clone());
    }
    py::method(value, "items", vec![])?
        .iter()?
        .into_iter()
        .map(|item| {
            let pair = py::unpack(&item, 2)?;
            Ok((pair[0].clone(), pair[1].clone()))
        })
        .collect()
}

/// `str(value)`.
fn text(value: &Val) -> Result<Val> {
    Ok(s(value.str()?))
}

/// `plain(value)`: records, wrapped containers and paths as JSON data.
pub fn plain(value: &Val) -> Result<Val> {
    if let Ok(asdict) = value.attr("_asdict") {
        let out = Val::dict(vec![]);
        for (key, row) in items(&asdict.call(vec![], vec![])?)? {
            out.set(key, plain(&row)?)?;
        }
        return Ok(out);
    }
    if is_kind(value, &["dict"])? {
        if value.contains(&s("__hsm_namedtuple__"))? {
            let zipped = interop::builtin("zip").context("zip")?.call(
                vec![py::at(value, "fields")?, py::at(value, "values")?],
                vec![("strict".into(), Val::Bool(true))],
            )?;
            let out = Val::dict(vec![]);
            for item in zipped.iter()? {
                let pair = py::unpack(&item, 2)?;
                out.set(pair[0].clone(), plain(&pair[1])?)?;
            }
            return Ok(out);
        }
        if value.contains(&s("__hsm_dict__"))? {
            let out = Val::dict(vec![]);
            for item in py::at(value, "__hsm_dict__")?.iter()? {
                let pair = py::unpack(&item, 2)?;
                out.set(text(&pair[0])?, plain(&pair[1])?)?;
            }
            return Ok(out);
        }
        if value.contains(&s("__hsm_list__"))? {
            let rows = py::at(value, "__hsm_list__")?.iter()?;
            return Ok(Val::list(rows.iter().map(plain).collect::<Result<_>>()?));
        }
        let out = Val::dict(vec![]);
        for (key, row) in items(value)? {
            out.set(text(&key)?, plain(&row)?)?;
        }
        return Ok(out);
    }
    if is_kind(value, &["tuple", "list", "set", "frozenset"])? {
        return Ok(Val::list(value.iter()?.iter().map(plain).collect::<Result<_>>()?));
    }
    if is_kind(value, &["Path"])? {
        return text(value);
    }
    Ok(value.clone())
}

/// `wire(value)`: an argument of a report request as plain data.
fn wire(value: &Val) -> Result<Val> {
    if let Ok(asdict) = value.attr("_asdict") {
        let out = Val::dict(vec![]);
        for (key, row) in items(&asdict.call(vec![], vec![])?)? {
            out.set(key, wire(&row)?)?;
        }
        return Ok(out);
    }
    if is_kind(value, &["dict"])? {
        let out = Val::dict(vec![]);
        for (key, row) in items(value)? {
            out.set(text(&key)?, wire(&row)?)?;
        }
        return Ok(out);
    }
    if is_kind(value, &["tuple", "list", "set", "frozenset"])? {
        return Ok(Val::list(value.iter()?.iter().map(wire).collect::<Result<_>>()?));
    }
    if is_kind(value, &["Path"])? {
        return text(value);
    }
    Ok(value.clone())
}

/// `_request(op, **values)`: one report from the machine program.
pub fn request(rt: &Rt, op: &str, values: Vec<(&str, Val)>) -> Result<Val> {
    let st = state(rt)?;
    request_values(rt, &st, s(op), Val::dict(values.into_iter().map(|(k, v)| (s(k), v)).collect()))
}

fn request_values(rt: &Rt, st: &State, op: Val, values: Val) -> Result<Val> {
    paths(rt, st)?;
    let call = rt.member("_rust_data", "request")?;
    let values = wire(&values)?;
    let mut metadata = py::method(&values, "get", vec![s("metadata")])?;
    if values.contains(&s("spec"))? {
        metadata = py::method(&py::at(&values, "spec")?, "get", vec![s("metadata")])?;
    }
    if !matches!(metadata, Val::None) {
        let routes = py::dget(&metadata, "routes", Val::dict(vec![]))?;
        let specs = py::method(&metadata, "get", vec![s("native_route_specs"), routes])?;
        py::method(&metadata, "setdefault", vec![s("native_route_order"), Val::list(specs.iter()?)])?;
        let groups = py::dget(&metadata, "native_connections", Val::dict(vec![]))?;
        let order = py::method(&metadata, "get", vec![s("native_connection_order"), Val::list(groups.iter()?)])?;
        py::method(&metadata, "setdefault", vec![s("connection_order"), order])?;
    }
    let payload = Val::dict(vec![(s("op"), op)]);
    for (key, value) in items(&values)? {
        payload.set(key, value)?;
    }
    py::call(&call, vec![s("machine-data"), s("machine-data"), payload])
}

/// `scalar_namespace(spec=None)`: the providers and authored turns the wiring recipes read,
/// with the spec's wiring context laid over them.
pub fn scalar_namespace(rt: &Rt, spec: &Val) -> Result<Val> {
    let st = state(rt)?;
    paths(rt, &st)?;
    let enc = py::method(&rt.import("_enclosure_datums")?, "load", vec![])?;
    let cci = rt.import("_cold_core_interface")?;
    let foam = rt.import("foam_assembly")?;
    let carbonator = rt.import("_carbonator")?;
    let pcba = rt.import("pcba_tray")?;
    let fuse = rt.import("sf76e_thermal_fuse")?;
    let digiten = rt.import("digiten_flow_sensor")?;
    let axis = |v: [f64; 3]| py::ftuple(&v);
    let (x, y, z) = (axis([1.0, 0.0, 0.0]), axis([0.0, 1.0, 0.0]), axis([0.0, 0.0, 1.0]));
    let turn = |a: &Val, deg: f64| Val::Tuple(vec![a.clone(), Val::Float(deg)]);
    let relay = Val::Tuple(vec![turn(&z, 270.0), turn(&y, 270.0)]);
    let wagos = Val::dict(vec![]);
    for size in ["413", "415", "420"] {
        wagos.set(s(size), Val::Path(st.hw.join(format!("reference/wago-221/wago-221-{size}.step"))))?;
    }
    let namespace = |rows: Vec<(&str, Val)>| -> Result<Val> {
        st.simple_namespace.call(vec![], rows.into_iter().map(|(k, v)| (k.to_owned(), v)).collect())
    };
    let bond = carbonator.attr("_bond")?;
    let top_plate_z = carbonator.attr("top_plate_z")?;
    let cca = namespace(vec![("_V", namespace(vec![("_bond", bond), ("top_plate_z", top_plate_z)])?)])?;
    let ml = namespace(vec![("VALVE_STEP", Val::Path(st.hw.join("reference/beduan-solenoid/beduan-solenoid.step")))])?;
    let relay2 = Val::Tuple(relay.iter()?.into_iter().chain([turn(&x, 90.0)]).collect());
    let tilt = Num::of(&enc.attr("display_facet_angle_deg")?)?.sub(Num::F(90.0));
    let collet = Num::of(&digiten.attr("port_face")?)?.sub(Num::of(&digiten.attr("port_collar_end")?)?);
    let values = py::dict([
        ("_enc", enc.clone()),
        ("_cci", cci),
        ("_foam", foam),
        ("_pcba", pcba),
        ("_fuse", fuse),
        ("_digiten", digiten),
        ("_cca", cca),
        ("ml", ml),
        ("PCBA_STEP", Val::Path(st.hw.join("printed-parts/electronics/pcba-tray/pcba-board.step"))),
        ("PSU_STEP", Val::Path(st.hw.join("reference/meanwell-irm90/meanwell-irm90.step"))),
        ("RELAY_STEP", Val::Path(st.hw.join("reference/teyleten-relay/teyleten-relay.step"))),
        ("MQ6_STEP", Val::Path(st.hw.join("reference/mq6-gas-sensor/mq6-gas-sensor.step"))),
        ("DIGITEN_STEP", Val::Path(st.hw.join("reference/digiten-flow-sensor/digiten-flow-sensor.step"))),
        ("C14_STEP", Val::Path(st.hw.join("reference/iec-c14-inlet/iec-c14-inlet.step"))),
        ("PCBA_TURN", Val::Tuple(vec![turn(&y, -90.0), turn(&x, -90.0)])),
        ("PSU_TURN", Val::Tuple(vec![turn(&y, -90.0)])),
        ("RELAY_TURN", relay),
        ("RELAY2_TURN", relay2),
        ("WAGO_TURN", Val::Tuple(vec![turn(&x, 90.0), turn(&y, -90.0)])),
        ("WAGO_TURN_WEST", Val::Tuple(vec![turn(&x, 90.0), turn(&y, 90.0)])),
        ("FUSE_TURN", Val::Tuple(vec![turn(&x, 90.0), turn(&z, 90.0)])),
        ("MQ6_TURN", Val::Tuple(vec![turn(&x, -90.0), turn(&z, 90.0)])),
        ("DIGITEN_TURN", Val::Tuple(vec![turn(&z, 90.0), turn(&y, 90.0)])),
        ("DISPLAY_TILT", Val::Tuple(vec![x.clone(), tilt.val()])),
        ("wago_step", wagos.attr("__getitem__")?),
        ("WAGO_POLES", Val::Tuple(["wago-v12", "wago-gnd", "wago-g", "wago-h", "wago-n"].into_iter().map(s).collect())),
        ("CRADLE_TOL", Val::Float(0.01)),
        ("PORT_NUT_GAP", Val::Float(7.0)),
        ("FLOOR_GROMMET_SQUEEZE", Val::Float(0.4)),
        ("DIGITEN_COLLET_FREE", collet.val()),
    ]);
    let base = if spec.truthy()? { spec.clone() } else { Val::dict(vec![]) };
    let context = py::dget(&py::dget(&base, "metadata", Val::dict(vec![]))?, "wiring_context", Val::dict(vec![]))?;
    py::method(&values, "update", vec![context])?;
    st.simple_namespace.call(vec![], keyword_items(values)?)
}

/// `route_metadata(spec, checked)`: the routing report, with the spools, cap anchors and port
/// order the plan's runs are drawn with.
pub fn route_metadata(rt: &Rt, spec: &Val, checked: &Val) -> Result<Val> {
    let st = state(rt)?;
    let metadata = py::at(spec, "metadata")?;
    if metadata.contains(&s("route_metadata"))? {
        return request(rt, "report_route_metadata", vec![("spec", spec.clone()), ("checked", checked.clone())]);
    }
    let ea = scalar_namespace(rt, spec)?;
    let routing = rt.import("_routing")?;
    let routes = py::dget(&metadata, "routes", Val::dict(vec![]))?;
    let specs = py::snapshot(&py::method(&metadata, "get", vec![s("native_route_specs"), routes])?)?;
    let spools = Val::dict(vec![]);
    for run in py::snapshot(&py::at(&metadata, "runs")?)?.iter()? {
        let name = py::at(&run, "id")?;
        let named = specs.contains(&name)? && py::method(&specs.get(name.clone())?, "get", vec![s("spool")])?.truthy()?;
        let spool = if named {
            routing.attr("SPOOLS")?.get(py::at(&specs.get(name.clone())?, "spool")?)?
        } else {
            py::call(&routing.attr("spool_of")?, vec![name.clone()])?
        };
        let row = Val::dict(vec![]);
        for key in ["name", "rgb", "alpha", "roughness", "metalness", "names"] {
            row.set(s(key), plain(&spool.attr(key)?)?)?;
        }
        spools.set(name, row)?;
    }
    let (cci, foam) = (ea.attr("_cci")?, ea.attr("_foam")?);
    let face = Num::of(&foam.attr("cap_face_z")?)?;
    let cap = Val::dict(vec![]);
    for name in cci.attr("cap_anchors")?.iter()? {
        let mut row = py::call(&foam.attr("cap_anchor_station")?, vec![name.clone()])?.iter()?;
        let over = Num::of(&py::call(&cci.attr("cap_anchor_axis_over_face")?, vec![name.clone()])?)?;
        row.push(face.add(over).val());
        cap.set(name, Val::list(row))?;
    }
    let side = Val::dict(vec![]);
    for (name, anchor) in items(&cci.attr("cap_side_anchors")?)? {
        let mut row = py::call(&foam.attr("cap_side_anchor_station")?, vec![name.clone()])?.iter()?;
        row.push(face.add(Num::of(&anchor.attr("over_face")?)?).val());
        side.set(name, Val::list(row))?;
    }
    let port_order = Val::dict(vec![]);
    for (name, ports) in items(&py::dget(&metadata, "world_ports", Val::dict(vec![]))?)? {
        port_order.set(name, Val::list(ports.iter()?))?;
    }
    let frames = Val::dict(vec![]);
    for (name, frame) in items(&py::at(&metadata, "frames")?)? {
        frames.set(name, Val::list(py::dget(&frame, "ports", Val::dict(vec![]))?.iter()?))?;
    }
    py::method(&port_order, "update", vec![frames])?;
    request(rt, "report_route_metadata", vec![
        ("spec", spec.clone()),
        ("checked", checked.clone()),
        ("cap_local_points", cap),
        ("cap_side_local_points", side),
        ("spools", spools),
        ("anchor_sites", st.anchor_sites.clone()),
        ("port_order", port_order),
    ])
}

/// `scene_document(spec, checked, *, taken=None)`: the scene's scalar document.
pub fn scene_document(rt: &Rt, spec: &Val, checked: &Val, taken: &Val) -> Result<Val> {
    let st = state(rt)?;
    paths(rt, &st)?;
    let machine = rt.import("_machine")?;
    let routing = rt.import("_routing")?;
    let taken = if matches!(taken, Val::None) { py::call(&st.time.attr("time")?, vec![])? } else { taken.clone() };
    let sources = py::call(&machine.attr("stamps")?, vec![])?;
    let fields = Val::list(routing.attr("Run")?.attr("__dataclass_fields__")?.iter()?);
    request(rt, "report_scene", vec![
        ("spec", spec.clone()),
        ("checked", checked.clone()),
        ("taken", taken),
        ("sources", sources),
        ("run_fields", fields),
    ])
}

/// `_tray_inputs(ea)`: the scalars the tray report reads off the enclosure.
fn tray_inputs(rt: &Rt, ea: &Val) -> Result<Vec<(&'static str, Val)>> {
    let above = rt.import("above_core")?;
    let mut valves = py::call(&above.attr("valve_names")?, vec![])?.iter()?;
    valves.extend(ea.attr("_cci")?.attr("cap_cradles")?.iter()?);
    valves.extend(py::call(&above.attr("core_equipment_names")?, vec![])?.iter()?);
    let enc = ea.attr("_enc")?;
    Ok(vec![
        ("excluded_valves", Val::list(valves)),
        ("interior_x", py::call(&enc.attr("interior_x")?, vec![])?),
        ("rear_axis_y_shift", enc.attr("_tray")?.attr("rear_axis_y_shift")?),
        ("pump_seated_drop", enc.attr("_interface")?.attr("pump_seated_drop")?),
        ("pump_relief_floor", enc.attr("pump_relief_floor")?),
    ])
}

enum Hash {
    Sha256,
    Blake2b16,
}

/// `hashlib.file_digest(path.open('rb'), ...)`: the file opened by the interpreter as the
/// recipe opens it, its bytes hashed here.
fn file_digest(st: &State, path: &Path, hash: Hash) -> Result<String> {
    let opened = Val::Path(path.to_owned()).attr("open")?.call(vec![s("rb")], vec![])?;
    opened.attr("__enter__")?.call(vec![], vec![])?;
    let digest = (|| -> Result<String> {
        let hasher = match hash {
            Hash::Sha256 => py::call(&st.hashlib.attr("sha256")?, vec![])?,
            Hash::Blake2b16 => py::call_kw(&st.hashlib.attr("blake2b")?, vec![], vec![("digest_size", Val::Int(16))])?,
        };
        let update = hasher.attr("update")?;
        let mut file = std::fs::File::open(path)?;
        let mut block = vec![0u8; 1 << 22];
        loop {
            let n = file.read(&mut block)?;
            if n == 0 {
                break;
            }
            update.call(vec![Val::Bytes(block[..n].to_vec())], vec![])?;
        }
        py::method(&hasher, "hexdigest", vec![])?.str()
    })();
    opened.attr("__exit__")?.call(vec![Val::None, Val::None, Val::None], vec![])?;
    digest
}

/// `gather(...)`'s `artifact(path)`: a file the facts name, read and hashed.
fn artifact(rt: &Rt, st: &State, path: &Path) -> Result<Val> {
    rt.note_read(path)?;
    let digest = file_digest(st, path, Hash::Sha256)?;
    Ok(py::dict([("path", s(py::path_str(path.strip_prefix(&st.root)?))), ("sha256", s(digest))]))
}

/// `Path.with_suffix(suffix)` as the runtime computes it.
fn with_suffix(path: &Path, suffix: &str) -> Result<PathBuf> {
    ensure!(suffix.is_empty() || suffix.starts_with('.'), "invalid suffix");
    let mut out = path.to_owned();
    out.set_extension(suffix.trim_start_matches('.'));
    Ok(out)
}

const STANDALONE_HEAD: [&str; 19] = [
    "compressor",
    "condenser+fan",
    "foam-assembly",
    "g-ganen-pump",
    "funnel",
    "discharge-chain",
    "display",
    "display-cover",
    "display-gasket",
    "psu",
    "pcba",
    "relay-1",
    "relay-2",
    "asse1022-assembly",
    "bulkhead-drain",
    "asse-drain-adapter",
    "mq6-sensor",
    "thermal-fuse",
    "fuse-clamp",
];
const STANDALONE_TAIL: [&str; 18] = [
    "wago-mana",
    "wago-manb",
    "wago-reeds-b",
    "wago-sensors",
    "water-split",
    "flow-regulator",
    "vk-solenoid",
    "bulkhead-water",
    "c14-inlet",
    "co2-inlet",
    "gasher-co2",
    "wr1110",
    "nameplate",
    "nameplate-ink",
    "bulkhead-flavor-a",
    "bulkhead-flavor-b",
    "bulkhead-carb",
    "digiten-flow",
];

/// `gather(spec, checked, physical_model, *, scene_path=None, step_path=None,
/// scorecard_path=None)`: the build's facts, answered by the machine program.
pub fn gather(rt: &Rt, spec: &Val, checked: &Val, physical_model: &Val, scene_path: &Val, step_path: &Val, scorecard_path: &Val) -> Result<Val> {
    let st = state(rt)?;
    paths(rt, &st)?;
    let facts = rt.import("_facts")?;
    let realized = rt.import("_realized")?;
    let above = rt.import("above_core")?;
    let ring = rt.import("bulkhead_ring")?;
    let union = rt.import("jg_bulkhead_union")?;
    let ea = scalar_namespace(rt, spec)?;
    let metadata = py::at(spec, "metadata")?;
    let physical_model = py::path(physical_model)?;
    let step_path = if matches!(step_path, Val::None) {
        let model = py::path_str(&physical_model);
        PathBuf::from(model.strip_suffix(".npz").unwrap_or(&model))
    } else {
        py::path(step_path)?
    };
    let scene_path = if matches!(scene_path, Val::None) { with_suffix(&step_path, ".scene.npz")? } else { py::path(scene_path)? };
    let scorecard_path = if matches!(scorecard_path, Val::None) { with_suffix(&step_path, ".scorecard.json")? } else { py::path(scorecard_path)? };
    let step_digest = file_digest(&st, &step_path, Hash::Blake2b16)?;

    let station = py::snapshot(&py::at(&py::call(&above.attr("pose")?, vec![s("c14-inlet")])?, "translation_mm")?)?;
    let constants = py::dict([
        ("C14_STATION", Val::list(vec![station.get(Val::Int(0))?, station.get(Val::Int(2))?])),
        ("DIGITEN_COLLET_FREE", ea.attr("DIGITEN_COLLET_FREE")?),
        ("FLOOR_GROMMET_SQUEEZE", ea.attr("FLOOR_GROMMET_SQUEEZE")?),
        ("KEYSTONE_CLEARANCES", py::dget(&metadata, "keystone_clearances", Val::Tuple(vec![]))?),
        ("KEYSTONE_STATION", py::at(&metadata, "keystone_station")?),
        ("CRADLE_TOL", ea.attr("CRADLE_TOL")?),
        ("PORT_NUT_GAP", ea.attr("PORT_NUT_GAP")?),
        ("WAGO_POLES", ea.attr("WAGO_POLES")?),
    ]);
    let enc = ea.attr("_enc")?;
    for name in ["appliance_width", "side_band_inset", "wall"] {
        constants.set(s(name), enc.attr(name)?)?;
    }
    let mut names: Vec<Val> = STANDALONE_HEAD.iter().map(|n| s(*n)).collect();
    names.extend(ea.attr("WAGO_POLES")?.iter()?);
    names.extend(STANDALONE_TAIL.iter().map(|n| s(*n)));
    let standalone = py::dget(&metadata, "standalone_names", Val::Tuple(names))?;

    let tray = py::dict(tray_inputs(rt, &ea)?);
    let box_fact_order = facts.attr("_BOX_FACT_ORDER")?;
    let card_port_bodies = facts.attr("CARD_PORT_BODIES")?;
    let wet_ports = py::at(&py::at(&py::call(&above.attr("specification")?, vec![])?, "rear_wall")?, "wet_ports")?;
    let footprint = py::call(&union.attr("panel_footprint")?, vec![])?.get(Val::Int(0))?;
    let ring_od = py::call(&ring.attr("od")?, vec![s("union")])?;
    let fit_slip = py::call(&st.importlib.attr("import_module")?, vec![s("fits")])?.attr("slip")?;
    let body_d = union.attr("BODY_D")?;
    let wire_exit = py::call(&ea.attr("_digiten")?.attr("wire_exit")?, vec![])?;
    let funnel = enc.attr("_funnel")?;
    let collar = Val::list(vec![funnel.attr("collar_w")?, funnel.attr("collar_d")?]);
    let cap_face_z = ea.attr("_foam")?.attr("cap_face_z")?;
    let card_digest = py::call(&realized.attr("code_digest")?, vec![Val::Path(scorecard_path)])?;
    let source_digest = py::call(&facts.attr("source_digest")?, vec![])?;
    let routing = route_metadata(rt, spec, checked)?;
    let artifacts = py::dict([
        ("step", artifact(rt, &st, &step_path)?),
        ("fine_model", artifact(rt, &st, &physical_model)?),
        ("scene", artifact(rt, &st, &scene_path)?),
    ]);
    request(rt, "report_facts", vec![
        ("spec", spec.clone()),
        ("checked", checked.clone()),
        ("tray_inputs", tray),
        ("box_fact_order", box_fact_order),
        ("card_port_bodies", card_port_bodies),
        ("wet_ports", wet_ports),
        ("constants", constants),
        ("union_panel_footprint", footprint),
        ("bulkhead_ring_union_od", ring_od),
        ("fit_slip", fit_slip),
        ("union_body_d", body_d),
        ("digiten_wire_exit", wire_exit),
        ("standalone_names", standalone),
        ("funnel_collar", collar),
        ("foam_cap_face_z", cap_face_z),
        ("card_digest", card_digest),
        ("step_digest", s(step_digest)),
        ("source_digest", source_digest),
        ("routing", routing),
        ("artifacts", artifacts),
    ])
}

/// `write(spec, checked, physical_model, **paths)`: the facts written beside the assembly.
pub fn write(rt: &Rt, spec: &Val, checked: &Val, physical_model: &Val, paths: Val) -> Result<Val> {
    let st = state(rt)?;
    let target = py::path(&py::method(&paths, "pop", vec![s("facts_path"), Val::Path(st.layout.join("enclosure-assembly.facts.json"))])?)?;
    let mut a = py::bind(vec![], keyword_items(paths)?, &[], &["scene_path", "step_path", "scorecard_path"])?;
    let scene_path = a.opt("scene_path").unwrap_or(Val::None);
    let step_path = a.opt("step_path").unwrap_or(Val::None);
    let scorecard_path = a.opt("scorecard_path").unwrap_or(Val::None);
    let value = gather(rt, spec, checked, physical_model, &scene_path, &step_path, &scorecard_path)?;
    let atomic_write = rt.member("_cadq_export", "_atomic_write")?;
    let json = st.json.clone();
    let writer = Val::function(move |args, kwargs| {
        let mut a = py::bind(args, kwargs, &["path"], &[])?;
        let path = py::path(&a.req("path")?)?;
        let text = py::call_kw(&json.attr("dumps")?, vec![value.clone()], vec![("indent", Val::Int(1)), ("sort_keys", Val::Bool(true))])?.str()?;
        Val::Path(path).attr("write_text")?.call(vec![s(text + "\n")], vec![])
    });
    py::call(&atomic_write, vec![Val::Path(target.clone()), writer])?;
    Ok(Val::Path(target))
}

/// Binds `(name, *, **rest)`: the named positional parameters, then the rest of the keywords
/// in the order given.
pub fn bind_rest(args: py::Args, mut kwargs: py::Kwargs, names: &[&str]) -> Result<(Vec<Val>, Val)> {
    ensure!(args.len() <= names.len(), "too many positional arguments");
    let mut args = args.into_iter();
    let mut bound = vec![];
    for name in names {
        let given = args.next();
        let named = kwargs.iter().position(|(k, _)| k == name).map(|i| kwargs.remove(i).1);
        ensure!(!(given.is_some() && named.is_some()), "multiple arguments for {name}");
        bound.push(given.or(named).with_context(|| format!("missing argument {name}"))?);
    }
    Ok((bound, Val::dict(kwargs.into_iter().map(|(k, v)| (s(k), v)).collect())))
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::MACHINE_REPORTING))?;
    let hashlib = rt.import("hashlib")?;
    ns.set("hashlib", hashlib.clone())?;
    let importlib = rt.import("importlib")?;
    ns.set("importlib", importlib.clone())?;
    let json = rt.import("json")?;
    ns.set("json", json.clone())?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    ns.set("sys", rt.import("sys")?)?;
    let time = rt.import("time")?;
    ns.set("time", time.clone())?;
    let simple_namespace = rt.member("types", "SimpleNamespace")?;
    ns.set("SimpleNamespace", simple_namespace.clone())?;
    let here = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    let root = here.ancestors().nth(3).unwrap_or(&here).to_owned();
    ns.set("ROOT", Val::Path(root.clone()))?;
    let hw = root.join("hardware");
    ns.set("HW", Val::Path(hw.clone()))?;
    let layout = hw.join("manifold-layout");
    ns.set("LAYOUT", Val::Path(layout.clone()))?;
    let site = |name: &str, end: i64, axis: [f64; 3]| {
        Val::Tuple(vec![s(name), Val::Int(end), py::ftuple(&axis), s("enclosure-back-top")])
    };
    let anchor_sites = Val::Tuple(vec![
        site("carb-1", 1, [0.0, 0.0, 1.0]),
        site("co2-2", 1, [0.0, 0.0, 1.0]),
        site("fluid-28", 2, [-1.0, 0.0, 0.0]),
    ]);
    ns.set("_ANCHOR_SITES", anchor_sites.clone())?;
    rt.keep(MODULE, State { root, hw, layout, hashlib, importlib, json, time, simple_namespace, anchor_sites });

    ns.def(rt, "_paths", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        paths(rt, &*state(rt)?)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "plain", |_, args, kw| {
        let mut a = py::bind(args, kw, &["value"], &[])?;
        plain(&a.req("value")?)
    })?;
    ns.def(rt, "scalar_namespace", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["spec"], &[])?;
        scalar_namespace(rt, &a.opt("spec").unwrap_or(Val::None))
    })?;
    ns.def(rt, "_request", |rt, args, kw| {
        let (bound, values) = bind_rest(args, kw, &["op"])?;
        request_values(rt, &*state(rt)?, bound[0].clone(), values)
    })?;
    ns.def(rt, "_bounds", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["spec"], &[])?;
        request(rt, "report_bounds", vec![("spec", a.req("spec")?)])
    })?;
    ns.def(rt, "_ports", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["frame"], &[])?;
        request(rt, "report_ports", vec![("frame", a.req("frame")?)])
    })?;
    ns.def(rt, "_route_rows", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["metadata"], &[])?;
        Ok(Val::Tuple(request(rt, "report_routes", vec![("metadata", a.req("metadata")?)])?.iter()?))
    })?;
    ns.def(rt, "_run_length", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["row"], &[])?;
        request(rt, "report_run_length", vec![("row", a.req("row")?)])
    })?;
    ns.def(rt, "route_metadata", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["spec", "checked"], &[])?;
        route_metadata(rt, &a.req("spec")?, &a.req("checked")?)
    })?;
    ns.def(rt, "scene_document", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["spec", "checked"], &["taken"])?;
        let (spec, checked) = (a.req("spec")?, a.req("checked")?);
        scene_document(rt, &spec, &checked, &a.opt("taken").unwrap_or(Val::None))
    })?;
    ns.def(rt, "_tray_inputs", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["ea"], &[])?;
        Ok(py::dict(tray_inputs(rt, &a.req("ea")?)?))
    })?;
    ns.def(rt, "_tray_reports", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["bounds", "ea"], &[])?;
        let (bounds, ea) = (a.req("bounds")?, a.req("ea")?);
        let mut values = vec![("bounds", bounds)];
        values.extend(tray_inputs(rt, &ea)?);
        Ok(Val::Tuple(request(rt, "report_trays", values)?.iter()?))
    })?;
    ns.def(rt, "gather", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["spec", "checked", "physical_model"], &["scene_path", "step_path", "scorecard_path"])?;
        let (spec, checked, model) = (a.req("spec")?, a.req("checked")?, a.req("physical_model")?);
        let scene = a.opt("scene_path").unwrap_or(Val::None);
        let step = a.opt("step_path").unwrap_or(Val::None);
        let card = a.opt("scorecard_path").unwrap_or(Val::None);
        gather(rt, &spec, &checked, &model, &scene, &step, &card)
    })?;
    ns.def(rt, "write", |rt, args, kw| {
        let (bound, paths) = bind_rest(args, kw, &["spec", "checked", "physical_model"])?;
        write(rt, &bound[0], &bound[1], &bound[2], paths)
    })?;
    Ok(())
}
