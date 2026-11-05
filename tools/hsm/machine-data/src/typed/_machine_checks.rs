//! The machine checks' request: plain inputs, their file bindings, and the construction ledgers
//! the fit, clearance and drain reader takes from the placed enclosure.
use super::num::Num;
use super::rt::{Ns, Rt};
use super::{docs, py};
use anyhow::{Context, Result, bail};
use hsm_documents::interop::{self, Val};
use py::s;
use std::io::Read;
use std::path::{Path, PathBuf};

/// Not yet compared with the generated build: the hybrid development build runs the generated namespace.
pub const TYPED: bool = false;

const MODULE: &str = "_machine_checks";

struct State {
    root: PathBuf,
    hashlib: Val,
    importlib: Val,
    io: Val,
    json: Val,
    redirect_stdout: Val,
}

fn state(rt: &Rt) -> Result<std::rc::Rc<State>> {
    rt.state::<State>(MODULE)
}

/// The sources whose digests the check request carries.
const SOURCES: [&str; 19] = [
    "hardware/scripts/check_asse_drain.py",
    "hardware/manifold-layout/_drain.py",
    "hardware/manifold-layout/enclosure_assembly.py",
    "hardware/manifold-layout/_lines.py",
    "hardware/manifold-layout/rear_plumbing.py",
    "hardware/manifold-layout/above-core.json",
    "hardware/reference/neofit-drain-bulkhead/neofit_drain_bulkhead.py",
    "hardware/reference/asse1022-assembly/asse1022_assembly.py",
    "hardware/printed-parts/asse-drain-adapter/asse_drain_adapter.py",
    "hardware/scripts/_assembly_model.py",
    "hardware/manifold-layout/enclosure_assembly.rs",
    "hardware/manifold-layout/machine_checks.rs",
    "hardware/manifold-layout/machine_check_drain.rs",
    "hardware/manifold-layout/machine_check_geometry.rs",
    "hardware/manifold-layout/machine_check_report.rs",
    "hardware/manifold-layout/machine_check_routes.rs",
    "hardware/manifold-layout/machine_check_rules.json",
    "hardware/manifold-layout/machine_check_bounds.rs",
    "hardware/scripts/_machine_checks.py",
];

/// The provider directories `_construction_metadata` imports from.
const PROVIDERS: [&str; 8] = [
    "manifold-layout",
    "cold-core-layout",
    "printed-parts/enclosure/enclosure",
    "printed-parts/refrigeration/fuse-clamp",
    "printed-parts/enclosure/bulkhead-ring",
    "reference/jg-bulkhead-union",
    "reference/neofit-drain-bulkhead",
    "reference/neofit-bulkhead",
];

const WANTED: [&str; 4] = ["fuse-clamp-donor", "stub-tails-billed", "port-pocket-floor", "port-clamp-stack"];

/// `_path(path)`: a path against the checkout root, resolved.
fn path_of(st: &State, path: &Val) -> Result<PathBuf> {
    let path = py::path(path)?;
    py::resolve(&if path.is_absolute() { path } else { st.root.join(path) })
}

/// `_sha(path)`: the file opened by the interpreter as the recipe opens it, its bytes hashed here.
fn sha(st: &State, path: &Val) -> Result<String> {
    let path = path_of(st, path)?;
    let opened = Val::Path(path.clone()).attr("open")?.call(vec![s("rb")], vec![])?;
    opened.attr("__enter__")?.call(vec![], vec![])?;
    let digest = (|| -> Result<String> {
        let hasher = py::call(&st.hashlib.attr("sha256")?, vec![])?;
        let update = hasher.attr("update")?;
        let mut file = std::fs::File::open(&path)?;
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

/// `_binding(path)`: the file's path under the root and its digest.
fn binding(st: &State, path: &Val) -> Result<Val> {
    let path = path_of(st, path)?;
    let named = match path.strip_prefix(&st.root) {
        Ok(rel) if path.starts_with(&st.root) => py::path_str(rel),
        _ => py::path_str(&path),
    };
    Ok(py::dict([("path", s(named)), ("sha256", s(sha(st, &Val::Path(path))?))]))
}

/// `isinstance(value, kinds)` as the runtime answers it.
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
        "str" => matches!(value, Val::Str(_)),
        "int" => matches!(value, Val::Int(_) | Val::Bool(_)),
        "float" => matches!(value, Val::Float(_)),
        "bool" => matches!(value, Val::Bool(_)),
        _ => false,
    }))
}

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

/// `_plain(value)`: check inputs as plain scalar data.
fn plain(value: &Val) -> Result<Val> {
    if is_kind(value, &["Path"])? {
        return Ok(s(value.str()?));
    }
    if is_kind(value, &["dict"])? {
        let out = Val::dict(vec![]);
        for (k, v) in items(value)? {
            out.set(s(k.str()?), plain(&v)?)?;
        }
        return Ok(out);
    }
    if is_kind(value, &["tuple", "list", "set", "frozenset"])? {
        return Ok(Val::list(value.iter()?.iter().map(plain).collect::<Result<_>>()?));
    }
    if matches!(value, Val::None) || is_kind(value, &["str", "int", "float", "bool"])? {
        return Ok(value.clone());
    }
    // The recipe names the type in its message; `type` is no runtime builtin.
    bail!("{MODULE}: unknown name type")
}

/// A `{**record._asdict(), 'kind': 'gate'}` row.
fn gate_row(record: &Val) -> Result<Val> {
    let fields = py::snapshot(&py::method(record, "_asdict", vec![])?)?;
    let row = Val::dict(vec![]);
    for (k, v) in items(&fields)? {
        row.set(k, v)?;
    }
    row.set(s("kind"), s("gate"))?;
    Ok(row)
}

/// The body name a solid index belongs to: `display/2` is a solid of `display`.
fn logical(name: &str) -> &str {
    let (head, tail) = name.rsplit_once('/').unwrap_or((name, name));
    if !tail.is_empty() && tail.chars().all(|c| c.is_ascii_digit()) { head } else { name }
}

/// The handhold bound, read once on a question graph with the shell's bound ledger held off.
struct Handhold<'a> {
    request: &'a Val,
    indices: &'a Val,
    shell: &'a Val,
    checks: &'a Val,
    boxed: &'a Val,
}
impl Handhold<'_> {
    fn bound(&self, graph: &Val) -> Result<Val> {
        let pieces = Val::dict(vec![]);
        for name in ["front-bottom", "back-bottom"] {
            let spec = py::dict([
                ("model", py::at(self.request, "physical_model")?),
                ("indices", py::at(self.indices, &format!("enclosure-{name}"))?),
            ]);
            pieces.set(s(name), py::method(graph, "model", vec![spec])?)?;
        }
        let original = self.shell.attr("record_bound")?;
        let held = Val::function(|args, kwargs| {
            let mut a = py::bind(args, kwargs, &["row"], &[])?;
            a.req("row")
        });
        self.shell.setattr("record_bound", held)?;
        let attempt = (|| -> Result<Val> {
            let context = py::call(&self.checks.attr("_numeric")?, vec![self.shell.clone(), graph.clone()])?;
            context.attr("__enter__")?.call(vec![], vec![])?;
            let result = py::call(&self.shell.attr("_handhold_bound")?, vec![pieces.clone(), self.boxed.clone()]);
            context.attr("__exit__")?.call(vec![Val::None, Val::None, Val::None], vec![])?;
            result
        })();
        self.shell.setattr("record_bound", original)?;
        attempt
    }
}

/// `_construction_metadata(request)`: the stated bounds, the funnel attachment, the handhold and
/// the wedge question the construction ledger carries, written into the request's metadata.
fn construction_metadata(rt: &Rt, st: &State, request: &Val) -> Result<Val> {
    let metadata = py::at(request, "metadata")?;
    if !py::method(&metadata, "get", vec![s("box")])?.truthy()? {
        return Ok(Val::None);
    }
    let hardware = st.root.join("hardware");
    for path in PROVIDERS.iter().map(|p| hardware.join(p)) {
        let text = py::path_str(&path);
        if !py::sys_path_has(rt, &text)? {
            py::sys_path_insert(rt, &text)?;
        }
    }
    let shell = py::method(&rt.import("_enclosure_datums")?, "load", vec![])?;
    rt.import("_coil")?;
    rt.import("fuse_clamp")?;
    rt.import("_stated_bounds")?;
    let box_spec = rt.import("_box_spec")?;
    rt.import("above_core")?;
    rt.import("fits")?;
    let checks = rt.import("_rust_enclosure_checks")?;
    let model = rt.import("_assembly_model")?;
    let types = Val::dict(vec![]);
    for kind in ["Pack", "PortField", "Nameplate"] {
        let kind = shell.attr(kind)?;
        types.set(kind.attr("__name__")?, kind)?;
    }
    let document = py::at(&metadata, "box")?;
    let box_type = shell.attr("Box")?;
    let tupled = box_spec.attr("_tupled")?;
    let body = py::at(&document, "box")?;
    let mut fields = vec![];
    for field in box_type.attr("_fields")?.iter()? {
        fields.push(py::call(&tupled, vec![body.get(field)?, types.clone()])?);
    }
    let boxed = py::call(&box_type, fields)?;
    let scope = rt.import("_assembly_questions")?;

    let mut rows = vec![];
    for record in super::_stated_bounds::records(rt)? {
        let id = record.attr("id")?;
        if WANTED.iter().any(|w| matches!(&id, Val::Str(t) if t == w)) {
            rows.push(gate_row(&record)?);
        }
    }
    let frame = py::at(&py::at(&metadata, "frames")?, "funnel-drain-union")?;
    let stem_top = Num::of(&py::at(&py::at(&py::at(&frame, "ports")?, "stub")?, "pos")?.get(Val::Int(2))?)?;
    let funnel = shell.attr("_funnel")?;
    let elbow = py::call(&st.importlib.attr("import_module")?, vec![s("neofit_stem_elbow")])?;
    let seat = |rt_shell: &Val| -> Result<Val> { py::call(&rt_shell.attr("funnel_seat_z")?, vec![boxed.attr("outer")?]) };
    let land_top = Num::of(&seat(&shell)?)?.add(Num::of(&funnel.attr("spout_land_z")?)?);
    let floor = py::call(&shell.attr("_funnel_frame_part")?.attr("datums")?, vec![seat(&shell)?])?.get(Val::Int(0))?;
    let bend_z = py::at(&frame, "transform")?.get(Val::Int(2))?.get(Val::Int(3))?;
    let collar = Num::of(&elbow.attr("COLLAR_OD")?)?.div(Num::F(2.0));
    let body_air = Num::of(&floor)?.sub(Num::of(&bend_z)?).sub(collar);
    // `next([...], None)`: every run's id is read, the first match kept.
    let mut matched = vec![];
    for row in py::at(&metadata, "runs")?.iter()? {
        if interop::eq(&py::at(&row, "id")?, &s("above-core-drain-vb-east-link"))? {
            matched.push(row);
        }
    }
    let drain = matched.into_iter().next().unwrap_or(Val::None);
    let gap = stem_top.sub(land_top);
    let gap = match gap {
        Num::I(i) => i.abs() as f64,
        Num::F(x) => x.abs(),
    };
    let ok = gap < 0.001 && body_air.f() > 0.0 && !matches!(drain, Val::None);
    let reach = if matches!(drain, Val::None) {
        "not drawn".to_owned()
    } else {
        format!("{} mm to V-B", interop::format(&py::at(&drain, "length")?, ".1f")?)
    };
    let value = format!(
        "Uncut ATEU44W tip Z{}; {} mm engagement; socket body {} mm below the frame; fluid-4 {reach}",
        stem_top.fmt(".3f"),
        interop::format(&funnel.attr("sealing_land")?, ".3f")?,
        body_air.fmt(".3f"),
    );
    rows.push(py::dict([
        ("id", s("funnel-drain-attachment")),
        ("label", s("The removable funnel seals on the retained elbow stem")),
        ("kind", s("goal")),
        ("ok", Val::Bool(ok)),
        ("value", s(value)),
        ("target", s("a fixed elbow stem through the frame connected to V-B")),
        ("detail", Val::list(vec![s(
            "The cradle's snap and the plug's push-on seal on the stem are not physically qualified; `zone-c/funnel/cradle-trial` tests the snap.",
        )])),
    ]));

    let indices = Val::dict(vec![]);
    let identity = py::call(&model.attr("identity")?, vec![py::at(request, "physical_model")?])?;
    for (i, item) in identity.iter()?.into_iter().enumerate() {
        let pair = py::unpack(&item, 2)?;
        let name = pair[0].str()?;
        let key = s(logical(&name));
        let held = py::method(&indices, "setdefault", vec![key, Val::list(vec![])])?;
        py::method(&held, "append", vec![Val::Int(i as i64)])?;
    }
    let handhold = Handhold { request, indices: &indices, shell: &shell, checks: &checks, boxed: &boxed };
    let graph = py::call(&checks.attr("_Questions")?, vec![])?;
    let quiet = py::call(&st.redirect_stdout, vec![py::call(&st.io.attr("StringIO")?, vec![])?])?;
    quiet.attr("__enter__")?.call(vec![], vec![])?;
    let first = handhold.bound(&graph);
    quiet.attr("__exit__")?.call(vec![Val::None, Val::None, Val::None], vec![])?;
    first?;
    let measured = py::call(&checks.attr("_measure")?, vec![graph])?;
    let row = handhold.bound(&py::call(&checks.attr("_Questions")?, vec![measured])?)?;
    rows.push(gate_row(&row)?);

    let replace = rows.iter().map(|row| py::at(row, "id")).collect::<Result<Vec<_>>>()?;
    let mut bounds = vec![];
    for row in py::dget(&metadata, "bounds", Val::Tuple(vec![]))?.iter()? {
        let id = py::at(&row, "id")?;
        let mut kept = true;
        for r in &replace {
            if interop::eq(r, &id)? {
                kept = false;
                break;
            }
        }
        if kept {
            bounds.push(row);
        }
    }
    bounds.extend(rows);
    metadata.set(s("bounds"), Val::list(bounds))?;

    let print_up = shell.attr("PIECE_PRINT_UP")?;
    let mut kept = scope.attr("KEPT_WEDGES")?.iter()?;
    let anchors = py::dget(&metadata, "tube_anchors", Val::Tuple(vec![]))?;
    kept.extend(py::call(&scope.attr("authored_anchor_corbels")?, vec![anchors])?.iter()?);
    let piece_paths = Val::dict(vec![]);
    for name in print_up.iter()? {
        let path = format!("hardware/printed-parts/enclosure/enclosure/enclosure-{}.step", name.str()?);
        piece_paths.set(name, s(path))?;
    }
    metadata.set(s("wedge_question"), py::dict([
        ("clearance", scope.attr("WEDGE_CLEAR")?),
        ("inset", scope.attr("_PLAN_INSET")?),
        ("print_up", print_up),
        ("kept", Val::list(kept)),
        ("piece_paths", piece_paths),
    ]))?;
    Ok(Val::None)
}

/// `read(request)`: the machine checks of one plain request, its file bindings verified unchanged
/// after the reader returns.
fn read(rt: &Rt, st: &State, request: &Val) -> Result<Val> {
    let rust_part = rt.import("_rust_part")?;
    let model_module = rt.import("_assembly_model")?;
    let request = plain(request)?;
    let given = py::method(&request, "get", vec![s("model")])?;
    let model = path_of(st, &py::method(&request, "get", vec![s("physical_model"), given])?)?;
    request.set(s("physical_model"), s(py::path_str(&model)))?;
    let envelope = py::dict_of(&py::at(&request, "envelope")?)?;
    let given = py::method(&envelope, "get", vec![s("model")])?;
    let envelope_path = path_of(st, &py::method(&envelope, "get", vec![s("path"), given])?)?;
    let envelope_binding = binding(st, &Val::Path(envelope_path.clone()))?;
    let declared = py::method(&envelope, "get", vec![s("sha256")])?;
    if !matches!(declared, Val::None) && !interop::eq(&declared, &py::at(&envelope_binding, "sha256")?)? {
        bail!("ValueError: The exact casing model differs from its declared binding");
    }
    envelope.set(s("path"), s(py::path_str(&envelope_path)))?;
    request.set(s("envelope"), envelope.clone())?;
    let physical = binding(st, &Val::Path(model.clone()))?;
    let envelope_row = py::dict_of(&envelope_binding)?;
    envelope_row.set(s("transform"), py::at(&envelope, "transform")?)?;
    let mut names = vec![];
    for item in py::call(&model_module.attr("identity")?, vec![Val::Path(envelope_path)])?.iter()? {
        names.push(py::unpack(&item, 2)?[0].clone());
    }
    envelope_row.set(s("qualified_names"), Val::list(names))?;
    let bindings = py::dict([("physical", physical), ("envelope", envelope_row)]);
    if !matches!(py::method(&request, "get", vec![s("wiring_model")])?, Val::None) {
        let wiring = s(py::path_str(&path_of(st, &py::at(&request, "wiring_model")?)?));
        request.set(s("wiring_model"), wiring)?;
        bindings.set(s("wiring"), binding(st, &py::at(&request, "wiring_model")?)?)?;
    }
    let metadata = py::method(&request, "setdefault", vec![s("metadata"), Val::dict(vec![])])?;
    let mode = py::dget(&request, "mode", s("all"))?;
    if !["drain", "geometry", "clearance"].iter().any(|m| matches!(&mode, Val::Str(t) if t == m)) {
        construction_metadata(rt, st, &request)?;
    }
    let connections = py::json_loads(&py::read_text(&st.root.join("hardware/manifold-layout/above-core.json"))?)?;
    let order = Val::list(py::dget(&connections, "logical_connections", Val::dict(vec![]))?.iter()?);
    let mut more = vec![];
    for k in py::dget(&metadata, "native_connections", Val::dict(vec![]))?.iter()? {
        if !order.contains(&k)? {
            more.push(k);
        }
    }
    py::method(&order, "extend", vec![Val::list(more)])?;
    py::method(&metadata, "setdefault", vec![s("native_connection_order"), order])?;
    py::method(&metadata, "setdefault", vec![s("bed"), py::flist(&[325.0, 320.0, 320.0])])?;
    py::method(&metadata, "setdefault", vec![s("seat_tolerance"), Val::Float(1e-06)])?;
    py::method(&metadata, "setdefault", vec![s("tube_anchor_span"), Val::Float(200.0)])?;
    let topology = s(py::path_str(&st.root.join("hardware/topology/fluid-topology.md")));
    py::method(&metadata, "setdefault", vec![s("topology_path"), topology])?;
    py::method(&request, "setdefault", vec![s("aliases"), Val::dict(vec![])])?;
    let native = py::dget(&metadata, "native_route_specs", Val::dict(vec![]))?;
    let specs = py::method(&request, "get", vec![s("route_specs"), native])?;
    let text = py::json_dumps(&specs, vec![("sort_keys", Val::Bool(true))])?;
    let hasher = py::call(&st.hashlib.attr("sha256")?, vec![Val::Bytes(text.into_bytes())])?;
    bindings.set(s("route_specs_sha256"), py::method(&hasher, "hexdigest", vec![])?)?;
    request.set(s("input_bindings"), bindings.clone())?;
    let digests = Val::dict(vec![]);
    for p in SOURCES {
        digests.set(s(p), s(sha(st, &Val::Path(st.root.join(p)))?))?;
    }
    request.set(s("source_sha256"), digests)?;
    let said = py::call(&rust_part.attr("check")?, vec![s("machine"), s("machine-checks"), py::dict([("request", request)])])?;
    for (role, binding) in items(&bindings)? {
        if is_kind(&binding, &["dict"])? && !interop::eq(&s(sha(st, &py::at(&binding, "path")?)?), &py::at(&binding, "sha256")?)? {
            bail!("ValueError: Fine {} input changed during machine checks", interop::format(&role, "")?);
        }
    }
    Ok(said)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::MACHINE_CHECKS))?;
    let redirect_stdout = rt.member("contextlib", "redirect_stdout")?;
    ns.set("redirect_stdout", redirect_stdout.clone())?;
    let hashlib = rt.import("hashlib")?;
    ns.set("hashlib", hashlib.clone())?;
    let importlib = rt.import("importlib")?;
    ns.set("importlib", importlib.clone())?;
    let io = rt.import("io")?;
    ns.set("io", io.clone())?;
    let json = rt.import("json")?;
    ns.set("json", json.clone())?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    ns.set("sys", rt.import("sys")?)?;
    let here = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    let root = here.ancestors().nth(3).unwrap_or(&here).to_owned();
    ns.set("ROOT", Val::Path(root.clone()))?;
    rt.keep(MODULE, State { root, hashlib, importlib, io, json, redirect_stdout });
    ns.def(rt, "_path", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["path"], &[])?;
        Ok(Val::Path(path_of(&*state(rt)?, &a.req("path")?)?))
    })?;
    ns.def(rt, "_sha", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["path"], &[])?;
        Ok(s(sha(&*state(rt)?, &a.req("path")?)?))
    })?;
    ns.def(rt, "_binding", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["path"], &[])?;
        binding(&*state(rt)?, &a.req("path")?)
    })?;
    ns.def(rt, "_plain", |_, args, kw| {
        let mut a = py::bind(args, kw, &["value"], &[])?;
        plain(&a.req("value")?)
    })?;
    ns.def(rt, "_construction_metadata", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["request"], &[])?;
        construction_metadata(rt, &*state(rt)?, &a.req("request")?)
    })?;
    ns.def(rt, "read", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["request"], &[])?;
        read(rt, &*state(rt)?, &a.req("request")?)
    })?;
    ns.def(rt, "check", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["model"], &["envelope", "aliases", "metadata", "drain"])?;
        let model = a.req("model")?;
        let envelope = a.req("envelope")?;
        let aliases = a.opt("aliases").unwrap_or(Val::None);
        let metadata = a.req("metadata")?;
        let drain = a.opt("drain").unwrap_or(Val::Bool(true));
        let aliases = if aliases.truthy()? { aliases } else { Val::dict(vec![]) };
        let request = py::dict([
            ("physical_model", model),
            ("envelope", envelope),
            ("aliases", aliases),
            ("metadata", metadata),
            ("drain", drain),
        ]);
        read(rt, &*state(rt)?, &request)
    })?;
    ns.def(rt, "drain", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["model"], &[
            "envelope",
            "names",
            "route_specs",
            "aliases",
            "wiring_model",
            "obstacles",
            "expected_envelope_bounds",
            "physical_reading",
        ])?;
        let st = state(rt)?;
        let model = a.req("model")?;
        let envelope = a.req("envelope")?;
        let none = |v: Option<Val>| v.unwrap_or(Val::None);
        let (names, route_specs, aliases) = (none(a.opt("names")), none(a.opt("route_specs")), none(a.opt("aliases")));
        let (wiring_model, obstacles) = (none(a.opt("wiring_model")), none(a.opt("obstacles")));
        let (expected, reading) = (none(a.opt("expected_envelope_bounds")), none(a.opt("physical_reading")));
        if !matches!(reading, Val::None)
            && (path_of(&st, &py::at(&reading, "path")?)? != path_of(&st, &model)?
                || !interop::eq(&py::at(&reading, "sha256")?, &s(sha(&st, &model)?))?)
        {
            bail!("ValueError: Physical fine summaries belong to another model");
        }
        let request = py::dict([
            ("mode", s("drain")),
            ("physical_model", model),
            ("envelope", envelope),
            ("aliases", if aliases.truthy()? { aliases } else { Val::dict(vec![]) }),
            ("route_specs", if route_specs.truthy()? { route_specs } else { Val::dict(vec![]) }),
            ("expected_envelope_bounds", expected),
        ]);
        if !matches!(names, Val::None) {
            request.set(s("checked_members"), Val::list(names.iter()?))?;
        }
        if !matches!(wiring_model, Val::None) {
            request.set(s("wiring_model"), wiring_model)?;
        }
        if !matches!(obstacles, Val::None) {
            request.set(s("obstacles"), Val::list(obstacles.iter()?))?;
        }
        py::at(&read(rt, &st, &request)?, "drain")
    })?;
    Ok(())
}
