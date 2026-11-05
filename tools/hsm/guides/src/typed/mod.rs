//! Typed owner-guide pages and illustrations.
//!
//! Every module keeps its Python name, source path and members. Its state is a Rust struct,
//! initialized once per runtime in its source's own statement order, and its functions take and
//! return Rust values. `Val` carries values across the adapter boundary and through the explicit
//! callbacks into ReportLab, Pillow, pypdf, CadQuery and the other library primitives.

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

mod cad_art;
mod cad_art_mesh;
mod common;
mod contours;
mod cylinder_actions;
mod faucet_book;
mod fill_scene;
mod hold_scene;
mod ice_scene;
mod insertion_actions;
mod install_art;
mod install_art_mesh;
mod kit_art;
mod landscape;
mod opening_scene;
mod plumbing_art_mesh;
mod plumbing_scenes;
mod preflight;
mod press;
mod render_modern_tee;
mod scenes;
mod startup;

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
    natives: RefCell<HashMap<&'static str, Val>>,
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
            natives: RefCell::new(HashMap::new()),
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
    /// A class a guide's Python source keeps for library callbacks (ReportLab flowables and
    /// drawing helpers), loaded from that source file once.
    pub fn python_type(&self, module: &str, name: &str) -> Result<Val> {
        let loader = self.pya("_guides_compiled", "python_type_module")?;
        let path = self.file(module);
        let imported = loader.call(vec![Val::Str(module.into()), Val::Path(path)], vec![])?;
        imported.attr(name)
    }
    /// A function of the Rust guide primitives (`_guide_native`).
    pub fn native(&self, name: &'static str) -> Result<Val> {
        if let Some(function) = self.0.natives.borrow().get(name) {
            return Ok(function.clone());
        }
        let function = super::native::module()?.attr(name)?;
        self.0.natives.borrow_mut().insert(name, function.clone());
        Ok(function)
    }
    /// `shutil.copyfile`, `shutil.copy2` or `shutil.which`, as the guides run them.
    pub fn shutil(&self, name: &str) -> Result<Val> {
        super::native::files()?.attr(name)
    }
    /// `sys.path.insert(index, str(path))`, as the source module runs it.
    pub fn sys_path_insert(&self, index: i64, path: &Path) -> Result<()> {
        self.pya("sys", "path")?.attr("insert")?.call(
            vec![Val::Int(index), Val::Str(path.to_string_lossy().into_owned())],
            vec![],
        )?;
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
        let source = caller.and_then(table::source).map(|p| format!("/{p}"));
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
    pub fn substitute_md(
        &self,
        path: &Path,
        variables: &[(String, String)],
        caller: Option<&str>,
    ) -> Result<()> {
        self.substitute(hsm_documents::Kind::Markdown, path, variables, caller)
    }
    /// The function a `from docgen import <name>` binds in a module namespace, with that
    /// module as the Sources caller.
    pub fn docgen_member(&self, name: &str, caller: Option<&'static str>) -> Result<Val> {
        let kind = match name {
            "substitute_md" => hsm_documents::Kind::Markdown,
            "substitute_mmd" => hsm_documents::Kind::Mermaid,
            "substitute_py_comments" => hsm_documents::Kind::Python,
            "cells" => {
                return Ok(Val::function(|args, _| {
                    Ok(Val::list(
                        hsm_documents::cells(&args[0].str()?)
                            .into_iter()
                            .map(Val::Str)
                            .collect(),
                    ))
                }));
            }
            "load_module" => {
                let rt = self.clone();
                return Ok(Val::function(move |args, kwargs| {
                    let path = args.get(1).context("load_module path")?.str()?;
                    if let Some(name) = table::by_path(&path) {
                        return rt.import_module(name);
                    }
                    rt.pya("docgen", "load_module")?.call(args, kwargs)
                }));
            }
            _ => return self.pya("docgen", name),
        };
        let rt = self.clone();
        Ok(Val::function(move |args, kwargs| {
            let path = PathBuf::from(args.first().context("substitute path")?.str()?);
            let variables = args
                .get(1)
                .cloned()
                .or_else(|| {
                    kwargs
                        .iter()
                        .find(|(k, _)| k == "variables")
                        .map(|(_, v)| v.clone())
                })
                .context("substitute variables")?;
            let mut values = vec![];
            for key in variables.iter()? {
                values.push((key.str()?, variables.get(key)?.str()?));
            }
            rt.substitute(kind, &path, &values, caller)?;
            Ok(Val::None)
        }))
    }
    /// `docgen.load_module(name, path)`: a compiled guide module's namespace when `path` is
    /// one of their sources, else Python's docgen loads it (with the values the caller gave).
    pub fn load_module(&self, name: Val, path: Val) -> Result<Val> {
        if let Some(module) = table::by_path(&path.str()?) {
            return self.import_module(module);
        }
        self.pya("docgen", "load_module")?.call(vec![name, path], vec![])
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
        ns.value("__doc__", table::documentation(name).unwrap_or(""));
        members(self, name, &mut ns).with_context(|| format!("initialize {name}"))?;
        let value = ns.into_val();
        self.0
            .namespaces
            .borrow_mut()
            .insert(name.into(), value.clone());
        Ok(Some(value))
    }
    /// A compiled module's namespace, a Rust primitive set, or a Python module.
    pub fn import_module(&self, name: &str) -> Result<Val> {
        if let Some(module) = hsm_documents::interop::builtin_module(name) {
            return Ok(module);
        }
        match name {
            "_guide_native" => return super::native::module(),
            "shutil" => return super::native::files(),
            _ => {}
        }
        if let Some(module) = self.namespace(name)? {
            return Ok(module);
        }
        self.py(name)
    }
    fn export(&self, value: &Val) -> Result<Value> {
        if matches!(value, Val::Func(_) | Val::Namespace(_) | Val::Type(_)) {
            value.encode_ref()
        } else {
            hsm_documents::interop::native_snapshot(value)
        }
    }
}

/// The members a module shows Python, in its source's order.
fn members(rt: &Runtime, name: &str, ns: &mut Namespace) -> Result<()> {
    match name {
        "_cad_art" => cad_art::members(rt, ns),
        "_cad_art_mesh" => cad_art_mesh::members(rt, ns),
        "_install_art" => install_art::members(rt, ns),
        "_install_art_mesh" => install_art_mesh::members(rt, ns),
        "_plumbing_art_mesh" => plumbing_art_mesh::members(rt, ns),
        "render_modern_tee" => render_modern_tee::members(rt, ns),
        "plumbing_scenes" => plumbing_scenes::members(rt, ns),
        "contours" => contours::members(rt, ns),
        "cylinder_actions" => cylinder_actions::members(rt, ns),
        "fill_scene" => fill_scene::members(rt, ns),
        "hold_scene" => hold_scene::members(rt, ns),
        "ice_scene" => ice_scene::members(rt, ns),
        "insertion_actions" => insertion_actions::members(rt, ns),
        "kit_art" => kit_art::members(rt, ns),
        "landscape" => landscape::members(rt, ns),
        "opening_scene" => opening_scene::members(rt, ns),
        "preflight" => preflight::members(rt, ns),
        "press" => press::members(rt, ns),
        "scenes" => scenes::members(rt, ns),
        "startup" => startup::members(rt, ns),
        "faucet_book" => faucet_book::members(rt, ns),
        "common" => common::members(rt, ns),
        _ => bail!("unknown guide module {name}"),
    }
}

/// A module's `if __name__ == "__main__":` block.
fn entrypoint(rt: &Runtime, name: &str) -> Result<()> {
    match name {
        "_cad_art" => cad_art::main(rt),
        "_cad_art_mesh" => cad_art_mesh::main(rt),
        "_install_art" => install_art::main(rt),
        "_install_art_mesh" => install_art_mesh::main(rt),
        "_plumbing_art_mesh" => plumbing_art_mesh::main(rt),
        "render_modern_tee" => render_modern_tee::main(rt),
        "plumbing_scenes" => plumbing_scenes::main(rt),
        "contours" => contours::main(rt),
        "cylinder_actions" => cylinder_actions::main(rt),
        "fill_scene" => fill_scene::main(rt),
        "hold_scene" => hold_scene::main(rt),
        "ice_scene" => ice_scene::main(rt),
        "insertion_actions" => insertion_actions::main(rt),
        "kit_art" => kit_art::main(rt),
        "landscape" => landscape::main(rt),
        "opening_scene" => opening_scene::main(rt),
        "preflight" => preflight::main(rt),
        "press" => press::main(rt),
        "scenes" => scenes::main(rt),
        "startup" => startup::main(rt),
        "faucet_book" => faucet_book::main(rt),
        "common" => common::main(rt),
        _ => bail!("unknown guide entrypoint {name}"),
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
