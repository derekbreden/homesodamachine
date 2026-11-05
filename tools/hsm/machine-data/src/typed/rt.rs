//! The resident module registry: typed module state, provider imports and the request protocol.
use super::py;
use anyhow::{Context, Result, bail, ensure};
use hsm_documents::interop::{Val, builtin_module, callback, native_snapshot};
use serde_json::{Value, json};
use std::any::Any;
use std::cell::RefCell;
use std::collections::{BTreeMap, HashMap};
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
        let rt = rt.clone();
        let module = self.module();
        self.set(name, Val::function(move |args, kwargs| {
            let _frame = rt.frame(module);
            f(&rt, args, kwargs)
        }))
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
        }))
    }
    pub fn root(&self) -> &Path {
        &self.0.root
    }
    pub fn root_path(&self) -> &Path {
        &self.0.root
    }
    pub fn import_module(&self, name: &str) -> Result<Val> {
        self.import(name)
    }
    pub fn frame(&self, module: &'static str) -> Frame {
        self.0.active.borrow_mut().push(module);
        Frame(self.clone())
    }
    fn caller(&self) -> Option<&'static str> {
        self.0.active.borrow().last().copied()
    }

    /// A module of this crate, initialized on first import; a provider module otherwise.
    pub fn import(&self, name: &str) -> Result<Val> {
        if let Some(module) = super::static_name(name) {
            #[cfg(feature = "hybrid")]
            if !super::converted(module) {
                return crate::compiled::import_generated(&self.0.root, module);
            }
            return self.namespace(module).map(|ns| ns.0);
        }
        self.provider(name)
    }
    /// A provider or standard module. Python keeps one module object per name, so the handle
    /// is kept after its first import.
    pub fn provider(&self, name: &str) -> Result<Val> {
        if let Some(value) = self.0.providers.borrow().get(name) {
            return Ok(value.clone());
        }
        // The document shims read which module imported them, so each import makes its own.
        if name == "docgen" {
            return self.docgen();
        }
        if name == "_document_export" {
            return self.document_export();
        }
        let value = if let Some(value) = builtin_module(name) {
            value
        } else {
            Val::decode(callback(json!({"op": "import", "module": name}))?)?
        };
        self.0.providers.borrow_mut().insert(name.to_owned(), value.clone());
        Ok(value)
    }
    /// `from module import name`.
    pub fn member(&self, module: &str, name: &str) -> Result<Val> {
        let imported = self.import(module)?;
        if let Ok(value) = imported.attr(name) {
            return Ok(value);
        }
        if builtin_module(module).is_some() {
            let primitive = Val::decode(callback(json!({"op": "import", "module": module}))?)?;
            if let Ok(value) = primitive.attr(name) {
                return Ok(value);
            }
        }
        self.import(&format!("{module}.{name}"))
    }
    /// A class the module's Python surface declares.
    pub fn python_type(&self, module: &str, name: &str) -> Result<Val> {
        let imported = Val::decode(callback(json!({"op": "import", "module": module}))?)?;
        imported.attr(name)
    }
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
        Ok(ns)
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
    pub fn keep<T: 'static>(&self, module: &'static str, state: T) -> Rc<T> {
        let state = Rc::new(state);
        self.0.typed.borrow_mut().insert(module, state.clone());
        state
    }

    /// `_layout_data.data(op, **values)`: the layout data recipes, answered in this process.
    pub fn layout_data(&self, payload: Value) -> Result<Value> {
        hsm_layout_data::request(payload)
    }
    /// `print(text)`, through the interpreter's own stdout.
    pub fn print(&self, text: String) -> Result<()> {
        let print = hsm_documents::interop::builtin("print").context("print")?;
        print.call(vec![Val::Str(text)], vec![])?;
        Ok(())
    }
    pub fn note_read(&self, path: &Path) -> Result<()> {
        self.note("_cadq_export", "note_read", path)
    }
    fn note(&self, module: &str, function: &str, path: &Path) -> Result<()> {
        let primitive = Val::decode(callback(json!({"op": "import", "module": module}))?)?.attr(function)?;
        primitive.call(vec![Val::Path(path.to_owned())], vec![])?;
        Ok(())
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
                let source = caller.and_then(super::source).map(|p| format!("/{p}"));
                let hardware = source.as_deref().is_some_and(|s| s.starts_with("/hardware/"));
                rt.note("_cadq_export", "note_read", &path)?;
                if hardware && matches!(kind, hsm_documents::Kind::Markdown) {
                    let sidecar = path.with_extension("figures.json");
                    if sidecar.is_file() {
                        rt.note("_cadq_export", "note_read", &sidecar)?;
                    }
                }
                let result = hsm_documents::substitute(&path, kind, &values, source.as_deref(), hardware)?;
                for maintained in result.maintained {
                    rt.note("docgen", "note_rewritten", &maintained)?;
                }
                Ok(Val::None)
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
/// A typed module, reached from a generated namespace.
#[cfg(feature = "hybrid")]
pub fn import_typed(root: &Path, name: &str) -> Result<Val> {
    active(root).import(name)
}

pub fn request(input: &Value) -> Result<Value> {
    let root = PathBuf::from(input["root"].as_str().context("compiled recipe root")?);
    let rt = active(&root);
    let name = input["module"].as_str().context("compiled recipe module")?;
    let module = rt.import(name)?;
    let path: Vec<String> = input["path"].as_array()
        .map(|a| a.iter().filter_map(Value::as_str).map(str::to_owned).collect())
        .unwrap_or_default();
    if input["action"] == "set" {
        ensure!(path.len() == 1, "a module binding has one name");
        let args = Val::decode(input["args"].clone())?.iter()?;
        module.set(path[0].clone().into(), args.first().context("module binding value")?.clone())?;
        return Ok(Value::Null);
    }
    let mut value = module.clone();
    for field in &path {
        value = value.attr(field)?;
    }
    match input["action"].as_str().unwrap_or("call") {
        "names" => Ok(json!(module.iter()?.iter().map(Val::str).collect::<Result<Vec<_>>>()?)),
        "get" => native_snapshot(&value),
        "call" => {
            let args = Val::decode(input["args"].clone())?.iter()?;
            let kwargs = keyword_items(Val::decode(input["kwargs"].clone())?)?;
            let module = super::static_name(name).unwrap_or("");
            let result = {
                let _frame = rt.frame(module);
                value.call(args, kwargs)
            };
            native_snapshot(&result?)
        }
        "main" => {
            let module = super::static_name(name).context("main module")?;
            super::entrypoint(&rt, module)?;
            Ok(Value::Null)
        }
        action => bail!("unknown compiled recipe action {action}"),
    }
}

/// Invoke a retained function identity and return its public containers by value.
pub fn invoke(input: &Value) -> Result<Value> {
    let callable = Val::decode(input["target"].clone())?;
    let args = Val::decode(input["args"].clone())?.iter()?;
    let kwargs = keyword_items(Val::decode(input["kwargs"].clone())?)?;
    native_snapshot(&callable.call(args, kwargs)?)
}

pub fn keyword_items(value: Val) -> Result<Vec<(String, Val)>> {
    value.iter()?.into_iter().map(|key| Ok((key.str()?, value.get(key)?))).collect()
}
