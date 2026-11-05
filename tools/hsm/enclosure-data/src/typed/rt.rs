//! The resident module registry: typed module state, provider imports and the request protocol.
use super::py;
use anyhow::{Context, Result, bail};
use hsm_documents::interop::{Val, builtin_module, callback, native_snapshot};
use serde_json::{Value, json};
use std::any::Any;
use std::cell::RefCell;
use std::collections::{BTreeMap, HashMap, VecDeque};
use std::path::{Path, PathBuf};
use std::rc::Rc;

#[derive(Clone)]
pub struct Rt(Rc<State>);
struct State {
    root: PathBuf,
    namespaces: RefCell<HashMap<&'static str, Val>>,
    typed: RefCell<HashMap<&'static str, Rc<dyn Any>>>,
    providers: RefCell<HashMap<String, Val>>,
    active: RefCell<Vec<&'static str>>,
    #[cfg(feature = "hybrid")]
    adopting: RefCell<Vec<&'static str>>,
}
thread_local! {static ACTIVE: RefCell<Option<Rt>> = const { RefCell::new(None) };}

/// One module's namespace as Python sees it: names in definition order.
#[derive(Clone)]
pub struct Ns(pub Val);
impl Ns {
    pub fn set(&self, name: &str, value: Val) -> Result<()> {
        self.0.set(name.into(), value)
    }
    pub fn get(&self, name: &str) -> Result<Val> {
        self.0.get(name.into())
    }
    /// A module function: Python arguments in, Python values out.
    pub fn def(&self, rt: &Rt, name: &str, f: impl Fn(&Rt, py::Args, py::Kwargs) -> Result<Val> + 'static) -> Result<()> {
        let function = self.function(rt, f);
        self.set(name, function)
    }
    /// A Python-callable function of this module that is not (yet) bound to a name: a closure, a
    /// default argument or a value another module installs.
    pub fn function(&self, rt: &Rt, f: impl Fn(&Rt, py::Args, py::Kwargs) -> Result<Val> + 'static) -> Val {
        let rt = rt.clone();
        let module = self.module();
        Val::function(move |args, kwargs| {
            let _frame = rt.frame(module);
            f(&rt, args, kwargs)
        })
    }
    /// `globals()`: a dict that shares this namespace's rows, so writes through it rebind names.
    pub fn globals(&self) -> Val {
        match &self.0 {
            Val::Namespace(rows) => Val::Dict(rows.clone()),
            other => other.clone(),
        }
    }
    /// The module's names in order.
    pub fn names(&self) -> Result<Vec<String>> {
        self.0.iter()?.iter().map(Val::str).collect()
    }
    fn module(&self) -> &'static str {
        let name = self.0.get("__name__".into()).and_then(|v| v.str()).unwrap_or_default();
        super::static_name(&name).unwrap_or("")
    }
}

pub struct Frame(Rt);
impl Drop for Frame {
    fn drop(&mut self) {
        self.0.0.active.borrow_mut().pop();
    }
}

impl Rt {
    fn new(root: PathBuf) -> Self {
        Self(Rc::new(State {
            root,
            namespaces: RefCell::new(HashMap::new()),
            typed: RefCell::new(HashMap::new()),
            providers: RefCell::new(HashMap::new()),
            active: RefCell::new(vec![]),
            #[cfg(feature = "hybrid")]
            adopting: RefCell::new(vec![]),
        }))
    }
    /// The checkout the request named: every repository path is under it.
    pub fn root(&self) -> &Path {
        &self.0.root
    }
    pub fn frame(&self, module: &'static str) -> Frame {
        self.0.active.borrow_mut().push(module);
        Frame(self.clone())
    }
    fn caller(&self) -> Option<&'static str> {
        self.0.active.borrow().last().copied()
    }

    /// `import name`: a module of this crate, initialized on first import; the runtime's own
    /// modules (`math`, `json`, ...), the import shims, or a Python module otherwise.
    pub fn import(&self, name: &str) -> Result<Val> {
        if let Some(value) = builtin_module(name) {
            return Ok(value);
        }
        if let Some(module) = super::static_name(name) {
            #[cfg(feature = "hybrid")]
            if !super::converted(module) {
                return crate::compiled::import_generated(&self.0.root, module);
            }
            return self.namespace(module).map(|ns| ns.0);
        }
        self.provider(name)
    }
    /// A Python module, or one of the shims this runtime puts in front of one. Python keeps one
    /// module object per name, so the handle is kept after its first import.
    pub fn provider(&self, name: &str) -> Result<Val> {
        // The document shims read which module imported them, so each import makes its own.
        match name {
            "importlib" => return self.importlib(),
            "docgen" => return self.docgen(),
            "_document_export" => return self.document_export(),
            _ => {}
        }
        if let Some(value) = self.0.providers.borrow().get(name) {
            return Ok(value.clone());
        }
        let value = Val::decode(callback(json!({"op": "import", "module": name}))?)?;
        self.0.providers.borrow_mut().insert(name.to_owned(), value.clone());
        Ok(value)
    }
    /// `from module import name`.
    pub fn member(&self, module: &str, name: &str) -> Result<Val> {
        let imported = self.import(module)?;
        match imported.attr(name) {
            Ok(value) => Ok(value),
            Err(_) => self.import(&format!("{module}.{name}")),
        }
    }
    /// A class the module's Python surface declares.
    pub fn python_type(&self, module: &str, name: &str) -> Result<Val> {
        let imported = Val::decode(callback(json!({"op": "import", "module": module}))?)?;
        imported.attr(name)
    }
    /// A typed module's namespace, running its top level on first use.
    pub fn namespace(&self, module: &'static str) -> Result<Ns> {
        if let Some(ns) = self.0.namespaces.borrow().get(module) {
            return Ok(Ns(ns.clone()));
        }
        let ns = Ns(Val::namespace(vec![]));
        ns.set("__name__", module.into())?;
        ns.set("__file__", Val::Path(self.0.root.join(super::source(module).context("module source")?)))?;
        self.0.namespaces.borrow_mut().insert(module, ns.0.clone());
        let _frame = self.frame(module);
        let result = super::install(self, &ns, module);
        if result.is_err() {
            self.0.namespaces.borrow_mut().remove(module);
            self.0.typed.borrow_mut().remove(module);
        }
        result.with_context(|| format!("initialize {module}"))?;
        // A module that adopts its generated namespace (a module converted function by function)
        // registers that namespace in place of the one made here.
        Ok(Ns(self.0.namespaces.borrow().get(module).cloned().unwrap_or(ns.0)))
    }
    /// Use `value` as `module`'s namespace from now on (a module converted function by function
    /// keeps its generated namespace and replaces the functions it has converted).
    #[cfg(feature = "hybrid")]
    pub fn adopt(&self, module: &'static str, value: Val) {
        self.0.namespaces.borrow_mut().insert(module, value);
    }
    /// A module converted function by function: its generated namespace, run now and adopted as
    /// the module's namespace before its top level runs, so a module it imports that imports it
    /// back sees that namespace, as in Python.
    #[cfg(feature = "hybrid")]
    pub fn generated_base(&self, module: &'static str) -> Result<Ns> {
        self.0.adopting.borrow_mut().push(module);
        let result = crate::compiled::generated_namespace(&self.0.root, module);
        self.0.adopting.borrow_mut().pop();
        let value = result?;
        self.adopt(module, value.clone());
        Ok(Ns(value))
    }
    /// A module's typed state, initializing the module on first use.
    pub fn state<T: 'static>(&self, module: &'static str) -> Result<Rc<T>> {
        if let Some(state) = self.0.typed.borrow().get(module) {
            return state.clone().downcast::<T>().map_err(|_| anyhow::anyhow!("{module} state type"));
        }
        self.namespace(module)?;
        let state = self.0.typed.borrow().get(module).cloned().with_context(|| format!("{module} has no typed state"))?;
        state.downcast::<T>().map_err(|_| anyhow::anyhow!("{module} state type"))
    }
    /// Keep a module's typed state; call it from the module's `install` before anything that can
    /// import a module which reads this one's state.
    pub fn keep<T: 'static>(&self, module: &'static str, state: T) -> Rc<T> {
        let state = Rc::new(state);
        self.0.typed.borrow_mut().insert(module, state.clone());
        state
    }

    /// One of this crate's own scalar recipes (`_enclosure_data.read(op, **values)`), answered in
    /// this process: the same JSON in and out as the worker round trip.
    pub fn enclosure_data(&self, payload: Value) -> Result<Value> {
        crate::dispatch(&payload)
    }
    /// `print(text)`, through the interpreter's own stdout.
    pub fn print(&self, text: String) -> Result<()> {
        let print = hsm_documents::interop::builtin("print").context("print")?;
        print.call(vec![Val::Str(text)], vec![])?;
        Ok(())
    }
    /// `_cadq_export.note_read(path)`: the build records a file the recipe read.
    pub fn note_read(&self, path: &Path) -> Result<()> {
        self.note("_cadq_export", "note_read", path)
    }
    /// `_cadq_export.note_write(path)`: the build records a file the recipe wrote.
    pub fn note_write(&self, path: &Path) -> Result<()> {
        self.note("_cadq_export", "note_write", path)
    }
    /// `_read_input(path)`: the path, recorded as a read.
    pub fn read_input(&self, path: Val) -> Result<Val> {
        self.note_read(Path::new(&path.str()?))?;
        Ok(path)
    }
    fn note(&self, module: &str, function: &str, path: &Path) -> Result<()> {
        let primitive = Val::decode(callback(json!({"op": "import", "module": module}))?)?.attr(function)?;
        primitive.call(vec![Val::Path(path.to_owned())], vec![])?;
        Ok(())
    }
    fn importlib(&self) -> Result<Val> {
        let raw = Val::decode(callback(json!({"op": "import", "module": "importlib"}))?)?;
        let raw_import = raw.attr("import_module")?;
        let rt = self.clone();
        let import = Val::function(move |args, kwargs| {
            let name = args.first().context("import module name")?.str()?;
            if super::source(&name).is_some() { rt.import(&name) } else { raw_import.call(args, kwargs) }
        });
        let fallback = Val::function(move |args, _| raw.attr(&args[0].str()?));
        Ok(Val::namespace(vec![("import_module".into(), import), ("__getattr__".into(), fallback)]))
    }
    fn docgen(&self) -> Result<Val> {
        let mut fields = vec![];
        for (name, kind) in [
            ("substitute_md", hsm_documents::Kind::Markdown),
            ("substitute_mmd", hsm_documents::Kind::Mermaid),
            ("substitute_py_comments", hsm_documents::Kind::Python),
        ] {
            let rt = self.clone();
            let caller = self.caller();
            fields.push((name.into(), Val::function(move |args, kwargs| {
                let path = PathBuf::from(args.first().context("substitute path")?.str()?);
                let variables = args.get(1).cloned()
                    .or_else(|| kwargs.iter().find(|(k, _)| k == "variables").map(|(_, v)| v.clone()))
                    .context("substitute variables")?;
                let mut values = BTreeMap::new();
                for key in variables.iter()? {
                    values.insert(key.str()?, variables.get(key)?.str()?);
                }
                rt.substitute(kind, &path, &values, caller)
            })));
        }
        fields.push(("cells".into(), Val::function(|args, _| {
            Ok(Val::list(hsm_documents::cells(&args[0].str()?).into_iter().map(Val::Str).collect()))
        })));
        let rt = self.clone();
        fields.push(("load_module".into(), Val::function(move |args, kwargs| {
            let path = args.get(1).context("load_module path")?.str()?;
            if let Some(name) = super::by_path(&path) {
                return rt.import(name);
            }
            let module = Val::decode(callback(json!({"op": "import", "module": "docgen"}))?)?;
            module.attr("load_module")?.call(args, kwargs)
        })));
        let raw = Val::decode(callback(json!({"op": "import", "module": "docgen"}))?)?;
        fields.push(("note_rewritten".into(), raw.attr("note_rewritten")?));
        Ok(Val::namespace(fields))
    }
    /// `docgen.substitute_md(path, variables)` (and `_mmd`, `_py_comments`) as `module` calls it.
    pub fn substitute(
        &self,
        kind: hsm_documents::Kind,
        path: &Path,
        values: &BTreeMap<String, String>,
        module: Option<&'static str>,
    ) -> Result<Val> {
        let source = module.and_then(super::source).map(|p| format!("/{p}"));
        let hardware = source.as_deref().is_some_and(|s| s.starts_with("/hardware/"));
        self.note("_cadq_export", "note_read", path)?;
        if hardware && matches!(kind, hsm_documents::Kind::Markdown) {
            let sidecar = path.with_extension("figures.json");
            if sidecar.is_file() {
                self.note("_cadq_export", "note_read", &sidecar)?;
            }
        }
        let result = hsm_documents::substitute(path, kind, values, source.as_deref(), hardware)?;
        for maintained in result.maintained {
            self.note("docgen", "note_rewritten", &maintained)?;
        }
        Ok(Val::None)
    }
    fn document_export(&self) -> Result<Val> {
        let mut fields = vec![];
        for name in ["export_pdf", "export_dxf"] {
            let rt = self.clone();
            let pdf = name == "export_pdf";
            fields.push((name.into(), Val::function(move |args, _| {
                let source = args.first().context("export source")?.clone();
                let target = PathBuf::from(args.get(1).context("export path")?.str()?);
                hsm_documents::atomic_write(&target, |temporary| {
                    if pdf {
                        source.call(vec![Val::Path(temporary.to_owned())], vec![])?;
                        hsm_documents::canonicalize_file(temporary, "pdf")?;
                    } else {
                        source.attr("saveas")?.call(vec![Val::Path(temporary.to_owned())], vec![])?;
                        hsm_documents::canonicalize_file(temporary, "dxf")?;
                    }
                    Ok(())
                }, false)?;
                rt.note("_cadq_export", "note_write", &target)?;
                Ok(Val::None)
            })));
        }
        Ok(Val::namespace(fields))
    }
}

/// Where a construction was made, as a graph node records it: this crate's source file and the
/// line that called the function marked `#[track_caller]`.
#[track_caller]
pub fn site() -> Val {
    let caller = std::panic::Location::caller();
    Val::dict(vec![
        ("path".into(), Val::Str(format!("tools/hsm/{}", caller.file()))),
        ("line".into(), Val::Int(caller.line() as i64)),
    ])
}

/// A value returned to Python: functions, namespaces and classes by reference; `BOUNDS` and
/// `_z_seam_passes` read as module members by reference too, so callers append to the module's
/// own containers; everything else by value.
fn export(path: &[String], value: &Val, identity: bool) -> Result<Value> {
    if matches!(value, Val::Func(_) | Val::Namespace(_) | Val::Type(_))
        || (identity && path.first().is_some_and(|name| matches!(name.as_str(), "BOUNDS" | "_z_seam_passes")))
    {
        value.encode_ref()
    } else {
        native_snapshot(value)
    }
}

pub fn register_io() -> Result<()> {
    let runtime = ACTIVE.with(|v| v.borrow().clone());
    if let Some(rt) = runtime {
        let (reads, writes) = hsm_documents::interop::io_paths();
        hsm_documents::interop::clear_io();
        for path in reads {
            rt.note("_cadq_export", "note_read", &path)?;
        }
        for path in writes {
            rt.note("_cadq_export", "note_write", &path)?;
        }
    }
    Ok(())
}

fn active(root: &Path) -> Rt {
    ACTIVE.with(|held| {
        let mut held = held.borrow_mut();
        if held.as_ref().is_none_or(|rt| rt.0.root != root) {
            *held = Some(Rt::new(root.to_owned()));
        }
        held.as_ref().unwrap().clone()
    })
}
/// The registry serving the current request.
pub fn current() -> Result<Rt> {
    ACTIVE.with(|held| held.borrow().clone()).context("typed recipe call outside a request")
}
/// A typed module, reached from a generated namespace.
#[cfg(feature = "hybrid")]
pub fn import_typed(root: &Path, name: &str) -> Result<Val> {
    active(root).import(name)
}
/// The generated runtime is about to run `name`'s top level into `values`: a module converted
/// function by function adopts that namespace now.
#[cfg(feature = "hybrid")]
pub fn generated_started(root: &Path, name: &str, values: &Val) {
    let rt = active(root);
    let adopting = rt.0.adopting.borrow().last().copied();
    if let Some(module) = adopting.filter(|module| *module == name) {
        rt.adopt(module, values.clone());
    }
}

pub fn request(input: &Value) -> Result<Value> {
    let root = PathBuf::from(input["root"].as_str().context("compiled recipe root")?);
    let rt = active(&root);
    if input["action"].as_str() == Some("invoke") {
        let callable = Val::decode(input["callable"].clone())?;
        let args = Val::decode(input["args"].clone())?.iter()?;
        let kwargs = keyword_items(Val::decode(input["kwargs"].clone())?)?;
        return export(&[], &callable.call(args, kwargs)?, false);
    }
    let name = input["module"].as_str().context("compiled recipe module")?;
    let module = rt.import(name)?;
    let path: Vec<String> = input["path"].as_array()
        .map(|a| a.iter().filter_map(Value::as_str).map(str::to_owned).collect())
        .unwrap_or_default();
    if input["action"].as_str() == Some("set") {
        let (field, parents) = path.split_last().context("set module field")?;
        let mut target = module.clone();
        for parent in parents {
            target = target.attr(parent)?;
        }
        let value = Val::decode(input["args"].clone())?.iter()?.first().context("set value")?.clone();
        target.setattr(field, value)?;
        return Ok(Value::Null);
    }
    let mut value = module.clone();
    for field in &path {
        value = value.attr(field)?;
    }
    match input["action"].as_str().unwrap_or("call") {
        "names" => Ok(json!(module.iter()?.iter().map(Val::str).collect::<Result<Vec<_>>>()?)),
        "public-names" => Ok(json!(module.iter()?.iter().map(Val::str).collect::<Result<Vec<_>>>()?
            .into_iter().filter(|name| !name.starts_with('_')).collect::<Vec<_>>())),
        "get" => export(&path, &value, true),
        "call" => {
            let args = Val::decode(input["args"].clone())?.iter()?;
            let kwargs = keyword_items(Val::decode(input["kwargs"].clone())?)?;
            let caller = super::static_name(name).unwrap_or("");
            let result = {
                let _frame = rt.frame(caller);
                value.call(args, kwargs)
            };
            export(&path, &result?, false)
        }
        "main" => {
            let module = super::static_name(name).context("main module")?;
            super::entrypoint(&rt, module)?;
            Ok(Value::Null)
        }
        action => bail!("unknown compiled recipe action {action}"),
    }
}

pub fn keyword_items(value: Val) -> Result<Vec<(String, Val)>> {
    value.iter()?.into_iter().map(|key| Ok((key.str()?, value.get(key)?))).collect()
}

/// A context manager Python can `with`: `enter` runs on entry (and `exit` with three `None`s if
/// it raises), `exit` on the way out.
pub fn context(enter: Val, exit: Val) -> Val {
    let cleanup = exit.clone();
    let entered = Val::function(move |args, kwargs| match enter.call(args, kwargs) {
        Ok(value) => Ok(value),
        Err(error) => {
            let _ = cleanup.call(vec![Val::None, Val::None, Val::None], vec![]);
            Err(error)
        }
    });
    Val::namespace(vec![("__enter__".into(), entered), ("__exit__".into(), exit)])
}

/// `functools.cache` / `lru_cache(maxsize=limit)` of a Python-callable function: results kept by
/// the encoded arguments, least recently used first out.
pub fn memoize(function: Val, limit: Option<usize>) -> Val {
    let cache = Rc::new(RefCell::new(VecDeque::<(String, Val)>::new()));
    Val::function(move |args, kwargs| {
        let key = serde_json::to_string(&(
            Val::tuple(args.clone()).encode()?,
            Val::dict(kwargs.iter().map(|(key, value)| (key.clone().into(), value.clone())).collect()).encode()?,
        ))?;
        let hit = {
            let mut entries = cache.borrow_mut();
            entries.iter().position(|(held, _)| held == &key).and_then(|index| entries.remove(index))
        };
        if let Some((key, value)) = hit {
            cache.borrow_mut().push_back((key, value.clone()));
            return Ok(value);
        }
        let value = function.call(args, kwargs)?;
        if limit != Some(0) {
            let mut entries = cache.borrow_mut();
            entries.push_back((key, value.clone()));
            if let Some(maximum) = limit {
                while entries.len() > maximum {
                    entries.pop_front();
                }
            }
        }
        Ok(value)
    })
}
