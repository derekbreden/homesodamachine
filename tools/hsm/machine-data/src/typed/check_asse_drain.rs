//! Read the dedicated ASSE drain against the actual installed appliance bodies.
//!
//! The drain question itself is `_machine_checks.drain`; this module binds the fine models it
//! reads, checks they agree with the saved placement facts, and writes the result. `_names`,
//! `centerline_radii` and `_torus_records` are native functions installed after this module's
//! top level, so they are reached through the namespace.
use super::rt::{Ns, Rt};
use super::{docs, py};
use anyhow::{Result, bail};
use hsm_documents::interop::{self, Val};
use py::s;
use std::path::PathBuf;
use std::rc::Rc;

/// Not yet verified, so the build runs the generated namespace: `write`, and `main` past its
/// input checks, have not been compared with the generated build.
pub const TYPED: bool = false;

const MODULE: &str = "check_asse_drain";
const OUTPUT: &str = "hardware/manifold-layout/drain-clearance-check.json";
const NAMES: [&str; 4] = ["asse-drain-adapter", "tube-drain-vent", "tube-fluid-18", "tube-fluid-28"];
/// Pairs that share material by design.
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

pub struct State {
    ns: Ns,
    root: PathBuf,
    path_type: Val,
    hashlib: Val,
    json: Val,
    output: Val,
    names: Val,
}
fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// `raise ValueError(text)` as the runtime reports it.
fn value_error(text: &str) -> anyhow::Error {
    anyhow::anyhow!("ValueError: {text}")
}
fn ne(a: Val, b: Val) -> Result<bool> {
    interop::compare("ne", a, b)?.truthy()
}

/// The file's SHA-256, read through the interpreter's file object.
pub fn sha(rt: &Rt, path: &Val) -> Result<Val> {
    let st = state(rt)?;
    let file = py::method(&py::call(&st.path_type, vec![path.clone()])?, "open", vec![s("rb")])?;
    let stream = py::method(&file, "__enter__", vec![])?;
    let digest = py::call(&st.hashlib.attr("file_digest")?, vec![stream, s("sha256")])
        .and_then(|digest| py::method(&digest, "hexdigest", vec![]));
    py::method(&file, "__exit__", vec![Val::None, Val::None, Val::None])?;
    digest
}

/// A path under the checkout root, or an absolute path, resolved.
pub fn resolve_path(rt: &Rt, path: &Val) -> Result<PathBuf> {
    let st = state(rt)?;
    let path = PathBuf::from(path.str()?);
    if path.is_absolute() { py::resolve(&path) } else { py::resolve(&st.root.join(path)) }
}

/// `{'path': ..., 'sha256': ...}`: the path relative to the root where it lies under it.
pub fn binding(rt: &Rt, path: &Val) -> Result<Val> {
    let st = state(rt)?;
    let path = resolve_path(rt, path)?;
    let shown = match path.strip_prefix(&st.root) {
        Ok(relative) => py::path_str(relative),
        Err(_) => py::path_str(&path),
    };
    let digest = sha(rt, &Val::Path(path))?;
    Ok(py::dict([("path", s(shown)), ("sha256", digest)]))
}

/// A body's name without its trailing instance number.
pub fn base(rt: &Rt, name: &Val) -> Result<Val> {
    py::call(&rt.import("re")?.attr("sub")?, vec![s(r"/\d+$"), s(""), name.clone()])
}

/// Whether two `(min..., max...)` boxes overlap within 1 mm.
pub fn overlap(a: &Val, b: &Val) -> Result<bool> {
    let less = |x: Val, y: Val| -> Result<bool> { interop::compare("lt", x, y)?.truthy() };
    let plus_one = |v: Val| -> Result<Val> {
        match v {
            Val::Int(_) | Val::Float(_) | Val::Bool(_) => Ok(super::num::Num::of(&v)?.add(super::num::Num::I(1)).val()),
            other => interop::binary("add", other, Val::Int(1)),
        }
    };
    let mut apart = vec![];
    for i in 0..3i64 {
        let separated = less(plus_one(a.get(Val::Int(i + 3))?)?, b.get(Val::Int(i))?)?
            || less(plus_one(b.get(Val::Int(i + 3))?)?, a.get(Val::Int(i))?)?;
        apart.push(separated);
    }
    Ok(!apart.into_iter().any(|x| x))
}

/// The fine summary rows of a model and its binding, checked against the model's entry names.
pub fn rows(rt: &Rt, model: &Val, component_names: &Val, reading: &Val) -> Result<Val> {
    let st = state(rt)?;
    let assembly = rt.import("_assembly_model")?;
    let model = Val::Path(resolve_path(rt, model)?);
    let bound = binding(rt, &model)?;
    let rows = if matches!(reading, Val::None) {
        let instance = py::call(&assembly.attr("instance")?, vec![model.clone()])?;
        let measured = py::call_kw(
            &assembly.attr("measure")?,
            vec![Val::list(vec![instance]), Val::Tuple(vec![])],
            vec![("component_names", component_names.clone())],
        )?;
        measured.get(s("bodies"))?
    } else {
        let read = Val::Path(resolve_path(rt, &reading.get(s("path"))?)?);
        if ne(read, model.clone())? || ne(reading.get(s("sha256"))?, bound.get(s("sha256"))?)? {
            return Err(value_error("Physical fine summaries belong to another model"));
        }
        reading.get(s("bodies"))?
    };
    let local = py::snapshot(&rows)?;
    let names = local.iter()?.iter().map(|row| row.get(s("name"))).collect::<Result<Vec<_>>>()?;
    let native = py::call(&st.ns.get("_names")?, vec![model])?;
    if ne(Val::list(names), native)? {
        return Err(value_error("Fine summary entry names differ from the bound model"));
    }
    Ok(Val::Tuple(vec![rows, bound]))
}

/// The keyword arguments of `write`, in its signature's order.
pub struct Drain {
    pub envelope: Val,
    pub names: Val,
    pub route_specs: Val,
    pub physical_reading: Val,
    pub aliases: Val,
    pub wiring_model: Val,
    pub obstacles: Val,
    pub expected_envelope_bounds: Val,
}

/// Read the existing drain question in Rust over explicit immutable models.
pub fn write(rt: &Rt, model: &Val, output: &Val, drain: Drain) -> Result<Val> {
    let st = state(rt)?;
    let checks = rt.import("_machine_checks")?;
    let result = py::call_kw(&checks.attr("drain")?, vec![model.clone()], vec![
        ("envelope", drain.envelope),
        ("names", drain.names),
        ("route_specs", drain.route_specs),
        ("physical_reading", drain.physical_reading),
        ("aliases", drain.aliases),
        ("wiring_model", drain.wiring_model),
        ("obstacles", drain.obstacles),
        ("expected_envelope_bounds", drain.expected_envelope_bounds),
    ])?;
    if !matches!(output, Val::None) {
        let text = dumps(&st, &result, vec![("indent", Val::Int(2))])? + "\n";
        py::method(&py::call(&st.path_type, vec![output.clone()])?, "write_text", vec![s(text)])?;
    }
    let print = interop::builtin("print").ok_or_else(|| anyhow::anyhow!("missing builtin print"))?;
    print.call(vec![s("ASSE drain clearance"), result.get(s("passed"))?], vec![("flush".into(), Val::Bool(true))])?;
    Ok(result)
}

fn dumps(st: &State, value: &Val, kwargs: Vec<(&str, Val)>) -> Result<String> {
    py::call_kw(&st.json.attr("dumps")?, vec![value.clone()], kwargs)?.str()
}
fn loads(st: &State, text: Val) -> Result<Val> {
    py::call(&st.json.attr("loads")?, vec![text])
}
/// `Path(str(path) + suffix)`.
fn suffixed(st: &State, path: &Val, suffix: &str) -> Result<Val> {
    py::call(&st.path_type, vec![s(path.str()? + suffix)])
}

/// Read the installed fine models and their exact saved casing placement.
pub fn main(rt: &Rt, argv: &Val) -> Result<Val> {
    let st = state(rt)?;
    let argparse = rt.import("argparse")?;
    rt.import("numpy")?;
    let realized = rt.import("_realized")?;
    let parser = py::call_kw(&argparse.attr("ArgumentParser")?, vec![], vec![("description", st.ns.get("__doc__")?)])?;
    let root = Val::Path(st.root.clone());
    let at = |relative: &str| interop::binary("truediv", root.clone(), s(relative));
    let add = |flag: &str, kwargs: Vec<(&str, Val)>| -> Result<()> {
        py::call_kw(&parser.attr("add_argument")?, vec![s(flag)], kwargs)?;
        Ok(())
    };
    let path_type = st.path_type.clone();
    add("--aggregate", vec![("type", path_type.clone()), ("default", at("hardware/manifold-layout/enclosure-assembly.step")?)])?;
    add("--facts", vec![("type", path_type.clone()), ("default", at("hardware/manifold-layout/enclosure-assembly.facts.json")?)])?;
    add("--scorecard", vec![("type", path_type.clone()), ("default", at("hardware/manifold-layout/enclosure-assembly.scorecard.json")?)])?;
    add("--scene", vec![("type", path_type.clone()), ("default", at("hardware/manifold-layout/enclosure-assembly.scene.npz")?)])?;
    add("--manifest", vec![("type", path_type.clone()), ("default", at("hardware/wiring/enclosure-wiring.json")?)])?;
    add("--envelope-frame", vec![
        ("type", path_type.clone()),
        ("help", s("Explicit casing path/SHA/transform JSON when the scene has no fine drain binding")),
    ])?;
    add("--only", vec![("nargs", s("+"))])?;
    add("--neighbors", vec![("nargs", s("+"))])?;
    add("--output", vec![("type", path_type), ("default", st.output.clone())])?;
    let args = py::method(&parser, "parse_args", vec![argv.clone()])?;
    let saved = loads(&st, py::method(&args.attr("facts")?, "read_text", vec![])?)?;
    let digest = |path: Val| py::call(&realized.attr("code_digest")?, vec![path]);
    let card = py::method(&saved, "get", vec![s("card")])?;
    let disagree = ne(card, digest(args.attr("scorecard")?)?)? || {
        let step = py::method(&saved, "get", vec![s("step")])?;
        ne(step, digest(args.attr("aggregate")?)?)?
    };
    if disagree {
        return Err(value_error("The saved assembly, scorecard and placement facts disagree"));
    }
    let model = suffixed(&st, &args.attr("aggregate")?, ".npz")?;
    let mut cold_core = vec![];
    for name in py::call(&st.ns.get("_names")?, vec![model.clone()])?.iter()? {
        cold_core.push(py::method(&name, "startswith", vec![s("cold-core/")])?.truthy()?);
    }
    if !cold_core.into_iter().any(|x| x) {
        return Err(value_error("The exported fine assembly contains no cold-core bodies"));
    }
    let frame = args.attr("envelope_frame")?;
    let envelope = if frame.truthy()? {
        loads(&st, py::method(&frame, "read_text", vec![])?)?
    } else {
        let assembly = rt.import("_assembly_model")?;
        let document = py::call(&assembly.attr("document")?, vec![args.attr("scene")?])?;
        let drain = py::method(&document, "get", vec![s("drain")])?;
        let drain = if drain.truthy()? { drain } else { Val::dict(vec![]) };
        let inputs = py::method(&drain, "get", vec![s("fine_inputs"), Val::dict(vec![])])?;
        let physical = py::method(&inputs, "get", vec![s("physical"), Val::dict(vec![])])?;
        if ne(py::method(&physical, "get", vec![s("sha256")])?, sha(rt, &model)?)? {
            return Err(value_error("The scene lacks this physical model casing binding; supply --envelope-frame"));
        }
        inputs.get(s("envelope"))?
    };
    let manifest_path = args.attr("manifest")?;
    let manifest = loads(&st, py::method(&manifest_path, "read_text", vec![])?)?;
    let wiring = suffixed(&st, &py::method(&manifest_path, "with_suffix", vec![s(".step")])?, ".npz")?;
    let foreign = ne(py::method(&manifest, "get", vec![s("physical_fine_model_sha256")])?, sha(rt, &model)?)? || {
        ne(py::method(&manifest, "get", vec![s("wiring_fine_model_sha256")])?, sha(rt, &wiring)?)?
    };
    if foreign {
        return Err(value_error("The installed wiring fine manifest belongs to another model"));
    }
    let expected = saved.get(s("bodies"))?.get(s("foam-assembly"))?;
    let only = args.attr("only")?;
    let names = if only.truthy()? { only } else { st.names.clone() };
    let route_specs = Val::dict(vec![]);
    for row in saved.get(s("native_runs"))?.iter()? {
        route_specs.set(row.get(s("id"))?, row)?;
    }
    let result = write(rt, &model, &args.attr("output")?, Drain {
        envelope: envelope.clone(),
        names,
        route_specs,
        physical_reading: Val::None,
        aliases: Val::None,
        wiring_model: wiring.clone(),
        obstacles: args.attr("neighbors")?,
        expected_envelope_bounds: expected.clone(),
    })?;
    let inputs = [
        args.attr("aggregate")?,
        model,
        wiring,
        args.attr("facts")?,
        args.attr("scorecard")?,
        manifest_path,
        Val::Path(resolve_path(rt, &envelope.get(s("path"))?)?),
    ];
    let digests = Val::dict(vec![]);
    for path in inputs {
        let key = s(path.str()?);
        digests.set(key, sha(rt, &path)?)?;
    }
    result.set(s("serialized_input_sha256"), digests)?;
    result.set(s("placement_fact_bounds_mm"), expected.clone())?;
    let compact = dumps(&st, &expected, vec![("separators", Val::Tuple(vec![s(","), s(":")]))])?;
    let encoded = py::method(&s(compact), "encode", vec![])?;
    let hashed = py::call(&st.hashlib.attr("sha256")?, vec![encoded])?;
    result.set(s("placement_fact_bounds_sha256"), py::method(&hashed, "hexdigest", vec![])?)?;
    result.set(s("foam_envelope_matches_saved_placement"), Val::Bool(true))?;
    let text = dumps(&st, &result, vec![("indent", Val::Int(2))])? + "\n";
    py::method(&args.attr("output")?, "write_text", vec![s(text)])?;
    Ok(Val::Int(if result.get(s("passed"))?.truthy()? { 0 } else { 1 }))
}

/// `sys.exit(main())`.
pub fn main_block(rt: &Rt) -> Result<()> {
    let st = state(rt)?;
    let code = main(rt, &Val::None)?;
    py::call(&st.ns.get("sys")?.attr("exit")?, vec![code])?;
    Ok(())
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::CHECK_ASSE_DRAIN))?;
    let path_type = rt.member("pathlib", "Path")?;
    ns.set("Path", path_type.clone())?;
    let hashlib = rt.import("hashlib")?;
    ns.set("hashlib", hashlib.clone())?;
    let json = rt.import("json")?;
    ns.set("json", json.clone())?;
    ns.set("sys", rt.import("sys")?)?;
    let file = py::call(&path_type, vec![ns.get("__file__")?])?;
    let root = py::method(&file, "resolve", vec![])?.attr("parents")?.get(Val::Int(2))?;
    ns.set("ROOT", root.clone())?;
    let root = py::path(&root)?;
    let output = Val::Path(root.join(OUTPUT));
    ns.set("OUTPUT", output.clone())?;
    let names = py::tuple(NAMES.map(s));
    ns.set("NAMES", names.clone())?;
    ns.set("CONNECTED", Val::set_values(CONNECTED.iter().map(|(a, b)| Val::frozen_set(vec![s(*a), s(*b)])).collect()))?;
    rt.keep(MODULE, State { ns: ns.clone(), root, path_type, hashlib, json, output: output.clone(), names: names.clone() });

    ns.def(rt, "sha", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["path"], &[])?;
        sha(rt, &a.req("path")?)
    })?;
    ns.def(rt, "_path", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["path"], &[])?;
        Ok(Val::Path(resolve_path(rt, &a.req("path")?)?))
    })?;
    ns.def(rt, "_binding", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["path"], &[])?;
        binding(rt, &a.req("path")?)
    })?;
    ns.def(rt, "_base", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        base(rt, &a.req("name")?)
    })?;
    ns.def(rt, "_overlap", |_, args, kw| {
        let mut a = py::bind(args, kw, &["a", "b"], &[])?;
        let (first, second) = (a.req("a")?, a.req("b")?);
        Ok(Val::Bool(overlap(&first, &second)?))
    })?;
    ns.def(rt, "_rows", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["model", "component_names", "reading"], &[])?;
        let model = a.req("model")?;
        let component_names = a.opt("component_names").unwrap_or_else(|| Val::Tuple(vec![]));
        let reading = a.opt("reading").unwrap_or(Val::None);
        rows(rt, &model, &component_names, &reading)
    })?;
    ns.def(rt, "write", move |rt, args, kw| {
        let keywords = ["envelope", "names", "route_specs", "physical_reading", "aliases", "wiring_model", "obstacles", "expected_envelope_bounds"];
        let mut a = py::bind(args, kw, &["model", "output"], &keywords)?;
        let model = a.req("model")?;
        let target = a.opt("output").unwrap_or_else(|| output.clone());
        let drain = Drain {
            envelope: a.req("envelope")?,
            names: a.opt("names").unwrap_or_else(|| names.clone()),
            route_specs: a.opt("route_specs").unwrap_or(Val::None),
            physical_reading: a.opt("physical_reading").unwrap_or(Val::None),
            aliases: a.opt("aliases").unwrap_or(Val::None),
            wiring_model: a.opt("wiring_model").unwrap_or(Val::None),
            obstacles: a.opt("obstacles").unwrap_or(Val::None),
            expected_envelope_bounds: a.opt("expected_envelope_bounds").unwrap_or(Val::None),
        };
        write(rt, &model, &target, drain)
    })?;
    ns.def(rt, "main", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["argv"], &[])?;
        main(rt, &a.opt("argv").unwrap_or(Val::None))
    })?;
    Ok(())
}
