//! Typed cold-core recipes and drawings.
//!
//! Every module keeps its Python name, source path and members. Its state is a Rust struct,
//! initialized once per runtime in its source's own statement order, and its functions take and
//! return Rust values. `Val` carries values across the adapter boundary and through the explicit
//! callbacks into Python providers and library primitives.

#[allow(unused_imports)]
pub(crate) use anyhow::{Context, Result, bail, ensure};
#[allow(unused_imports)]
pub(crate) use crate::{args, dict, kw};
pub use hsm_documents::interop::Val;
use hsm_documents::interop::callback;
use serde_json::{Value, json};
use std::any::Any;
use std::cell::RefCell;
use std::collections::{BTreeMap, HashMap};
use std::path::{Path, PathBuf};
use std::rc::Rc;

mod py;
pub use py::*;
mod table;

mod above_core;
mod cad;

mod above_core_mounts;
mod all_aero_float;
mod bom;
mod carbonator;
mod carbonator_tube_step;
mod carbonator_vessel_drawing;
mod coil_mandrel;
mod cold_core_assembly;
mod cold_core_interface;
mod cold_core_style;
mod cold_scorecard;
mod copper_ports;
mod core_numbers;
mod core_points;
mod core_presentation;
mod core_reference;
mod endcap_circular_drawing;
mod endcap_circular_dxf;
mod endcap_circular_step;
mod evaporator_coil_drawing;
mod fittings;
mod float_rod_drawing;
mod foam_assembly;
mod foam_cap;
mod foam_cap_parts;
mod foam_numbers;
mod foam_shell;
mod foam_shell_parts;
mod integration;
mod internal_routes;
mod internals;
mod magnetic_float;
mod outer_shell;
mod port_cuts;
mod prv_shroud;
mod reed_b_outlet;
mod reed_bridge;
mod reed_channels;
mod reservoir;
mod reservoir_a_anchors;
mod reservoir_a_c2;
mod reservoir_b_fill;
mod reservoir_float_rod_drawing;
mod reservoir_pocket_walls;
mod reservoir_ports;
mod show_skin;
mod support_ring;
mod water_inlet_jet;
mod water_inlet_jet_cap_drawing;
mod water_inlet_jet_elbow_drawing;
mod water_pressure_regulator;

/// A module's typed state, built by its own top-level statements.
pub trait Module: Any + Sized {
    const NAME: &'static str;
    fn init(rt: &Runtime) -> Result<Self>;
}

#[derive(Clone)]
pub struct Runtime(Rc<State>);
struct State {
    root: PathBuf,
    python: RefCell<HashMap<String, Val>>,
    states: RefCell<HashMap<&'static str, Rc<dyn Any>>>,
    loading: RefCell<Vec<&'static str>>,
    namespaces: RefCell<HashMap<String, Val>>,
}
thread_local! {static ACTIVE:RefCell<Option<Runtime>>=const{RefCell::new(None)};}

impl Runtime {
    fn new(root: PathBuf) -> Self {
        Self(Rc::new(State {
            root,
            python: RefCell::new(HashMap::new()),
            states: RefCell::new(HashMap::new()),
            loading: RefCell::new(vec![]),
            namespaces: RefCell::new(HashMap::new()),
        }))
    }
    pub fn root(&self) -> &Path {
        &self.0.root
    }
    /// One module's state; the first request runs its initialization.
    pub fn state<T: Module>(&self) -> Result<Rc<T>> {
        if let Some(held) = self.0.states.borrow().get(T::NAME) {
            return Ok(held.clone().downcast::<T>().expect("module state type"));
        }
        if self.0.loading.borrow().contains(&T::NAME) {
            bail!("{} is read during its own initialization", T::NAME);
        }
        self.0.loading.borrow_mut().push(T::NAME);
        let result = T::init(self);
        self.0.loading.borrow_mut().retain(|name| *name != T::NAME);
        let value = result.with_context(|| format!("initialize {}", T::NAME))?;
        if let Some(held) = self.held::<T>() {
            return Ok(held);
        }
        let state = Rc::new(value);
        self.0.states.borrow_mut().insert(T::NAME, state.clone());
        Ok(state)
    }
    /// A state another module's initialization put here before it finished.
    pub fn held<T: Module>(&self) -> Option<Rc<T>> {
        self.0
            .states
            .borrow()
            .get(T::NAME)
            .map(|held| held.clone().downcast::<T>().expect("module state type"))
    }
    /// Keep a state that a module's initialization settles partway through.
    pub fn put<T: Module>(&self, value: T) -> Rc<T> {
        let state = Rc::new(value);
        self.0.states.borrow_mut().insert(T::NAME, state.clone());
        state
    }
    /// The source file of a compiled module, under this runtime's root.
    pub fn file(&self, module: &str) -> PathBuf {
        self.0.root.join(table::source(module).unwrap_or_default())
    }
    /// A Python module, imported once through the adapter callback.
    pub fn py(&self, name: &str) -> Result<Val> {
        if let Some(module) = self.0.python.borrow().get(name) {
            return Ok(module.clone());
        }
        let module = Val::decode(callback(json!({"op":"import","module":name}))?)?;
        self.0
            .python
            .borrow_mut()
            .insert(name.into(), module.clone());
        Ok(module)
    }
    /// A member of a Python module.
    pub fn pya(&self, module: &str, name: &str) -> Result<Val> {
        self.py(module)?.attr(name)
    }
    /// `sys.path.insert(index, str(path))`, as the source module runs it.
    pub fn sys_path_insert(&self, index: i64, path: &Path) -> Result<()> {
        self.pya("sys", "path")?.attr("insert")?.call(
            vec![Val::Int(index), Val::Str(path.to_string_lossy().into_owned())],
            vec![],
        )?;
        Ok(())
    }
    /// `sys.path[:0] = paths`.
    pub fn sys_path_prepend(&self, paths: &[PathBuf]) -> Result<()> {
        let list = self.pya("sys", "path")?;
        for (index, path) in paths.iter().enumerate() {
            list.attr("insert")?.call(
                vec![
                    Val::Int(index as i64),
                    Val::Str(path.to_string_lossy().into_owned()),
                ],
                vec![],
            )?;
        }
        Ok(())
    }
    /// `print(*values)` on the Python process's stdout.
    pub fn print(&self, text: impl Into<String>) -> Result<()> {
        self.pya("builtins", "print")?
            .call(vec![Val::Str(text.into())], vec![])?;
        Ok(())
    }
    /// `collections.namedtuple(name, fields)` declared by `module`.
    pub fn namedtuple(&self, name: &str, fields: &str, module: &str) -> Result<Val> {
        self.pya("collections", "namedtuple")?.call(
            vec![name.into(), fields.into()],
            vec![("module".into(), module.into())],
        )
    }
    fn note(&self, module: &str, function: &str, path: &Path) -> Result<()> {
        self.pya(module, function)?
            .call(vec![Val::Path(path.to_owned())], vec![])?;
        Ok(())
    }
    pub fn note_read(&self, path: &Path) -> Result<()> {
        self.note("_cadq_export", "note_read", path)
    }
    pub fn note_write(&self, path: &Path) -> Result<()> {
        self.note("_cadq_export", "note_write", path)
    }
    /// docgen's substitution into one maintained document. `caller` is the compiled module
    /// whose import of docgen supplies the Sources entry, or none.
    pub fn substitute(
        &self,
        kind: hsm_documents::Kind,
        path: &Path,
        variables: &[(String, String)],
        caller: Option<&str>,
    ) -> Result<()> {
        let values: BTreeMap<String, String> = variables.iter().cloned().collect();
        let source = caller
            .and_then(table::source)
            .map(|p| format!("/{p}"));
        let hardware = source
            .as_deref()
            .is_some_and(|s| s.starts_with("/hardware/"));
        self.note_read(path)?;
        if hardware && matches!(kind, hsm_documents::Kind::Markdown) {
            let sidecar = path.with_extension("figures.json");
            if sidecar.is_file() {
                self.note_read(&sidecar)?;
            }
        }
        let result = hsm_documents::substitute(path, kind, &values, source.as_deref(), hardware)?;
        for maintained in result.maintained {
            self.note("docgen", "note_rewritten", &maintained)?;
        }
        Ok(())
    }
    pub fn substitute_py_comments(
        &self,
        path: &Path,
        variables: &[(String, String)],
        caller: Option<&str>,
    ) -> Result<()> {
        self.substitute(hsm_documents::Kind::Python, path, variables, caller)
    }
    pub fn substitute_md(
        &self,
        path: &Path,
        variables: &[(String, String)],
        caller: Option<&str>,
    ) -> Result<()> {
        self.substitute(hsm_documents::Kind::Markdown, path, variables, caller)
    }
    /// `_document_export.export_pdf(draw, target)`: the drawing callback writes a temporary
    /// file, which is normalized and moved over the target.
    pub fn export_pdf(&self, target: &Path, draw: impl Fn(&Path) -> Result<()>) -> Result<()> {
        hsm_documents::atomic_write(
            target,
            |temporary| {
                draw(temporary)?;
                hsm_documents::canonicalize_file(temporary, "pdf")
            },
            false,
        )?;
        self.note_write(target)
    }
    /// `_document_export.export_dxf(document, target)`.
    pub fn export_dxf(&self, document: &Val, target: &Path) -> Result<()> {
        hsm_documents::atomic_write(
            target,
            |temporary| {
                document
                    .attr("saveas")?
                    .call(vec![Val::Path(temporary.to_owned())], vec![])?;
                hsm_documents::canonicalize_file(temporary, "dxf")
            },
            false,
        )?;
        self.note_write(target)
    }
    /// The Python-visible namespace of a compiled module, built once.
    fn namespace(&self, name: &str) -> Result<Option<Val>> {
        if let Some(held) = self.0.namespaces.borrow().get(name) {
            return Ok(Some(held.clone()));
        }
        let Some(path) = table::source(name) else {
            return Ok(None);
        };
        let mut ns = Namespace::default();
        ns.value("__name__", name);
        ns.value("__file__", Val::Path(self.0.root.join(path)));
        ns.value(
            "__doc__",
            table::documentation(name).map_or(Val::None, Val::from),
        );
        members(self, name, &mut ns).with_context(|| format!("initialize {name}"))?;
        let value = ns.into_val();
        self.0
            .namespaces
            .borrow_mut()
            .insert(name.into(), value.clone());
        Ok(Some(value))
    }
    /// A compiled module's namespace, or a Python module through the adapter.
    pub fn import_module(&self, name: &str) -> Result<Val> {
        if let Some(module) = hsm_documents::interop::builtin_module(name) {
            return Ok(module);
        }
        if let Some(module) = self.namespace(name)? {
            return Ok(module);
        }
        self.py(name)
    }
    fn export(&self, value: &Val) -> Result<Value> {
        match value {
            Val::Func(_) | Val::Namespace(_) | Val::Type(_) => value.encode_ref(),
            Val::Path(path) => Ok(json!({"$path":path.to_string_lossy()})),
            Val::Tuple(items) => Ok(
                json!({"$tuple":items.iter().map(|v|self.export(v)).collect::<Result<Vec<_>>>()?}),
            ),
            Val::List(items) => Ok(Value::Array(
                items
                    .borrow()
                    .iter()
                    .map(|v| self.export(v))
                    .collect::<Result<_>>()?,
            )),
            Val::Set(items) => Ok(
                json!({"$set":items.borrow().iter().map(|v|self.export(v)).collect::<Result<Vec<_>>>()?}),
            ),
            Val::Dict(items) => Ok(
                json!({"$dict":items.borrow().iter().map(|(k,v)|Ok(json!([self.export(k)?,self.export(v)?]))).collect::<Result<Vec<Value>>>()?}),
            ),
            _ => value.encode(),
        }
    }
}

/// The members a module shows Python, in its source's order.
fn members(rt: &Runtime, name: &str, ns: &mut Namespace) -> Result<()> {
    match name {
        "_above_core_mounts" => above_core_mounts::members(rt, ns),
        "_bom" => bom::members(rt, ns),
        "_carbonator" => carbonator::members(rt, ns),
        "_cold_core_interface" => cold_core_interface::members(rt, ns),
        "_cold_core_style" => cold_core_style::members(rt, ns),
        "_cold_scorecard" => cold_scorecard::members(rt, ns),
        "_copper_ports" => copper_ports::members(rt, ns),
        "_core_points" => core_points::members(rt, ns),
        "_core_presentation" => core_presentation::members(rt, ns),
        "_fittings" => fittings::members(rt, ns),
        "_foam_cap" => foam_cap_parts::members(rt, ns),
        "_foam_shell" => foam_shell_parts::members(rt, ns),
        "_internal_routes" => internal_routes::members(rt, ns),
        "_internals" => internals::members(rt, ns),
        "_outer_shell" => outer_shell::members(rt, ns),
        "_port_cuts" => port_cuts::members(rt, ns),
        "_reed_b_outlet" => reed_b_outlet::members(rt, ns),
        "_reed_channels" => reed_channels::members(rt, ns),
        "_reservoir_a_anchors" => reservoir_a_anchors::members(rt, ns),
        "_reservoir_a_c2" => reservoir_a_c2::members(rt, ns),
        "_reservoir_b_fill" => reservoir_b_fill::members(rt, ns),
        "_reservoir_pocket_walls" => reservoir_pocket_walls::members(rt, ns),
        "_reservoir_ports" => reservoir_ports::members(rt, ns),
        "_show_skin" => show_skin::members(rt, ns),
        "_support_ring" => support_ring::members(rt, ns),
        "_water_inlet_jet" => water_inlet_jet::members(rt, ns),
        "_water_pressure_regulator" => water_pressure_regulator::members(rt, ns),
        "all_aero_float" => all_aero_float::members(rt, ns),
        "carbonator_tube_step" => carbonator_tube_step::members(rt, ns),
        "carbonator_vessel_drawing" => carbonator_vessel_drawing::members(rt, ns),
        "coil_mandrel" => coil_mandrel::members(rt, ns),
        "cold_core_assembly" => cold_core_assembly::members(rt, ns),
        "core_numbers" => core_numbers::members(rt, ns),
        "core_reference" => core_reference::members(rt, ns),
        "endcap_circular_drawing" => endcap_circular_drawing::members(rt, ns),
        "endcap_circular_dxf" => endcap_circular_dxf::members(rt, ns),
        "endcap_circular_step" => endcap_circular_step::members(rt, ns),
        "evaporator_coil_drawing" => evaporator_coil_drawing::members(rt, ns),
        "float_rod_drawing" => float_rod_drawing::members(rt, ns),
        "foam_assembly" => foam_assembly::members(rt, ns),
        "foam_cap" => foam_cap::members(rt, ns),
        "foam_numbers" => foam_numbers::members(rt, ns),
        "foam_shell" => foam_shell::members(rt, ns),
        "integration" => integration::members(rt, ns),
        "magnetic_float" => magnetic_float::members(rt, ns),
        "prv_shroud" => prv_shroud::members(rt, ns),
        "reed_bridge" => reed_bridge::members(rt, ns),
        "reservoir" => reservoir::members(rt, ns),
        "reservoir_float_rod_drawing" => reservoir_float_rod_drawing::members(rt, ns),
        "water_inlet_jet_cap_drawing" => water_inlet_jet_cap_drawing::members(rt, ns),
        "water_inlet_jet_elbow_drawing" => water_inlet_jet_elbow_drawing::members(rt, ns),
        _ => bail!("unknown cold-core module {name}"),
    }
}

/// A module's `if __name__ == "__main__":` block.
fn entrypoint(rt: &Runtime, name: &str) -> Result<()> {
    match name {
        "_carbonator" => carbonator::main(rt),
        "_cold_core_interface" => cold_core_interface::main(rt),
        "_internals" => internals::main(rt),
        "all_aero_float" => all_aero_float::main(rt),
        "carbonator_tube_step" => carbonator_tube_step::main(rt),
        "carbonator_vessel_drawing" => carbonator_vessel_drawing::main(rt),
        "coil_mandrel" => coil_mandrel::main(rt),
        "cold_core_assembly" => cold_core_assembly::main(rt),
        "endcap_circular_drawing" => endcap_circular_drawing::main(rt),
        "endcap_circular_dxf" => endcap_circular_dxf::main(rt),
        "endcap_circular_step" => endcap_circular_step::main(rt),
        "evaporator_coil_drawing" => evaporator_coil_drawing::main(rt),
        "float_rod_drawing" => float_rod_drawing::main(rt),
        "foam_assembly" => foam_assembly::main(rt),
        "foam_cap" => foam_cap::main(rt),
        "foam_shell" => foam_shell::main(rt),
        "integration" => integration::main(rt),
        "magnetic_float" => magnetic_float::main(rt),
        "prv_shroud" => prv_shroud::main(rt),
        "reed_bridge" => reed_bridge::main(rt),
        "reservoir" => reservoir::main(rt),
        "reservoir_float_rod_drawing" => reservoir_float_rod_drawing::main(rt),
        "water_inlet_jet_cap_drawing" => water_inlet_jet_cap_drawing::main(rt),
        "water_inlet_jet_elbow_drawing" => water_inlet_jet_elbow_drawing::main(rt),
        _ => Ok(()),
    }
}

pub fn register_io() -> Result<()> {
    let runtime = ACTIVE.with(|v| v.borrow().clone());
    if let Some(rt) = runtime {
        let (reads, writes) = hsm_documents::interop::io_paths();
        hsm_documents::interop::clear_io();
        for path in reads {
            rt.note_read(&path)?;
        }
        for path in writes {
            rt.note_write(&path)?;
        }
    }
    Ok(())
}

pub fn invoke(input: &Value) -> Result<Value> {
    let rt = ACTIVE
        .with(|held| held.borrow().clone())
        .context("compiled recipe runtime")?;
    let function = Val::decode(input["target"].clone())?;
    let args = Val::decode(input["args"].clone())?.iter()?;
    let kwargs = keyword_items(Val::decode(input["kwargs"].clone())?)?;
    let value = function.call(args, kwargs)?;
    rt.export(&value)
}

fn keyword_items(value: Val) -> Result<Vec<(String, Val)>> {
    value
        .iter()?
        .into_iter()
        .map(|key| Ok((key.str()?, value.get(key)?)))
        .collect()
}

pub fn request(input: &Value) -> Result<Value> {
    let root = PathBuf::from(input["root"].as_str().context("compiled recipe root")?);
    let rt = ACTIVE.with(|held| {
        let mut held = held.borrow_mut();
        if held.as_ref().is_none_or(|rt| rt.0.root != root) {
            *held = Some(Runtime::new(root));
        }
        held.as_ref().unwrap().clone()
    });
    let name = input["module"].as_str().context("compiled recipe module")?;
    let module = rt.import_module(name)?;
    let path: Vec<String> = input["path"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(Value::as_str)
                .map(str::to_owned)
                .collect()
        })
        .unwrap_or_default();
    let mut value = module.clone();
    for field in &path {
        value = value.attr(field)?;
    }
    match input["action"].as_str().unwrap_or("call") {
        "names" => Ok(json!(
            module
                .iter()?
                .iter()
                .map(Val::str)
                .collect::<Result<Vec<_>>>()?
        )),
        "public-names" => Ok(json!(
            module
                .iter()?
                .iter()
                .map(Val::str)
                .collect::<Result<Vec<_>>>()?
                .into_iter()
                .filter(|s| !s.starts_with('_') && !s.contains('.'))
                .collect::<Vec<_>>()
        )),
        "get" => rt.export(&value),
        "call" => {
            let args = Val::decode(input["args"].clone())?.iter()?;
            let kwargs = keyword_items(Val::decode(input["kwargs"].clone())?)?;
            rt.export(&value.call(args, kwargs)?)
        }
        "main" => {
            entrypoint(&rt, name)?;
            Ok(Value::Null)
        }
        action => bail!("unknown compiled recipe action {action}"),
    }
}
