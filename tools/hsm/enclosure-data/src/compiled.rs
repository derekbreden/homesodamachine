//! Compiled enclosure recipes and drawings share scalar/container values and
//! explicit third-party primitive callbacks. Every recipe's control flow is Rust.

use anyhow::{Context, Result, bail, ensure};
pub use hsm_documents::interop::{Val, binary, compare, format, unary};
use hsm_documents::interop::{builtin, builtin_module, callback};
use serde_json::{Value, json};
use std::cell::RefCell;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::rc::Rc;

mod modules;

#[derive(Clone)]
pub struct Env(Rc<Scope>);
struct Scope {
    values: Val,
    parent: Option<Env>,
    module: String,
}

impl Env {
    pub fn module(module: &str) -> Self {
        Self(Rc::new(Scope {
            values: Val::namespace(vec![]),
            parent: None,
            module: module.into(),
        }))
    }
    pub fn child(&self) -> Self {
        Self(Rc::new(Scope {
            values: Val::namespace(vec![]),
            parent: Some(self.clone()),
            module: self.0.module.clone(),
        }))
    }
    pub fn get(&self, name: &str) -> Result<Val> {
        if name == "_read_input" {
            return Ok(Val::function(|args, _| {
                let value = args.first().context("input path")?.clone();
                let rt = ACTIVE
                    .with(|held| held.borrow().clone())
                    .context("input read outside a compiled call")?;
                rt.note("_cadq_export", "note_read", Path::new(&value.str()?))?;
                Ok(value)
            }));
        }
        if name == "_source_info" {
            return Ok(Val::function(|_, _| source_info()));
        }
        if name == "globals" || name == "locals" {
            let scope = if name == "globals" {
                self.root()
            } else {
                self.clone()
            };
            return Ok(Val::function(move |_, _| Ok(scope.dictionary())));
        }
        if let Ok(value) = self.0.values.get(name.into()) {
            return Ok(value);
        }
        if let Some(parent) = &self.0.parent {
            return parent.get(name);
        }
        if let Some(value) = builtin(name) {
            return Ok(value);
        }
        if name.ends_with("Error") || matches!(name, "Exception" | "SystemExit" | "StopIteration") {
            return Ok(Val::function(move |args, _| {
                Ok(Val::Str(
                    args.first().map(Val::str).transpose()?.unwrap_or_default(),
                ))
            }));
        }
        bail!("{}: unknown name {name}", self.0.module)
    }
    pub fn set(&self, name: &str, value: Val) -> Result<()> {
        self.0.values.set(name.into(), value)
    }
    pub fn set_global(&self, name: &str, value: Val) -> Result<()> {
        self.root().set(name, value)
    }
    fn root(&self) -> Self {
        self.0
            .parent
            .as_ref()
            .map_or_else(|| self.clone(), Env::root)
    }
    fn dictionary(&self) -> Val {
        match &self.0.values {
            Val::Namespace(rows) => Val::Dict(rows.clone()),
            _ => unreachable!(),
        }
    }
}

pub type Parameters = Vec<(String, Option<Val>, bool)>;
pub enum Flow {
    Continue,
    Return(Val),
}
pub fn bind(
    outer: &Env,
    params: &Parameters,
    args: Vec<Val>,
    kwargs: Vec<(String, Val)>,
    varargs: Option<&str>,
    varkw: Option<&str>,
) -> Result<Env> {
    let e = outer.child();
    let mut positional = args.into_iter();
    let mut supplied = kwargs;
    for (name, default, keyword_only) in params {
        let keyword = supplied.iter().position(|(key, _)| key == name);
        let value = if !keyword_only {
            positional.next()
        } else {
            None
        };
        let value = match (value, keyword) {
            (Some(_), Some(_)) => bail!("multiple arguments for {name}"),
            (Some(value), None) => value,
            (None, Some(index)) => supplied.remove(index).1,
            (None, None) => default
                .clone()
                .with_context(|| format!("missing argument {name}"))?,
        };
        e.set(name, value)?;
    }
    let excess: Vec<_> = positional.collect();
    if let Some(name) = varargs {
        e.set(name, Val::tuple(excess))?;
    } else {
        ensure!(excess.is_empty(), "too many positional arguments");
    }
    if let Some(name) = varkw {
        e.set(
            name,
            Val::dict(supplied.into_iter().map(|(k, v)| (k.into(), v)).collect()),
        )?;
    } else {
        ensure!(supplied.is_empty(), "unexpected keyword arguments");
    }
    Ok(e)
}

pub fn unpack(value: Val, count: usize) -> Result<Vec<Val>> {
    let values = value.iter()?;
    ensure!(
        values.len() == count,
        "unpack: expected {count}, got {}",
        values.len()
    );
    Ok(values)
}
pub fn keyword_items(value: Val) -> Result<Vec<(String, Val)>> {
    value
        .iter()?
        .into_iter()
        .map(|key| Ok((key.str()?, value.get(key)?)))
        .collect()
}
pub fn dict_extend(target: &Val, source: Val) -> Result<()> {
    for key in source.iter()? {
        target.set(key.clone(), source.get(key)?)?;
    }
    Ok(())
}
pub fn val_string(value: Val) -> Result<String> {
    value.str()
}
pub fn builtin_call(name: &str, args: Vec<Val>, kwargs: Vec<(String, Val)>) -> Result<Val> {
    if let Some(function) = builtin(name) {
        return function.call(args, kwargs);
    }
    Val::decode(callback(json!({"op":"import","module":"builtins"}))?)?
        .attr(name)?
        .call(args, kwargs)
}
pub fn delete(e: &Env, name: &str) -> Result<()> {
    e.0.values.delete(name.into())
}
pub fn delete_item(value: Val, key: Val) -> Result<()> {
    value.delete(key)
}
pub fn import_star(e: &Env, module: Val) -> Result<()> {
    let names = module
        .attr("__all__")
        .and_then(|v| v.iter())
        .unwrap_or_else(|_| module.iter().unwrap_or_default());
    for name in names {
        let key = name.str()?;
        if !key.starts_with('_') {
            e.set(&key, module.attr(&key)?)?;
        }
    }
    Ok(())
}

#[derive(Clone)]
pub struct Runtime(Rc<State>);
struct State {
    root: PathBuf,
    modules: RefCell<HashMap<String, Env>>,
    active: RefCell<Vec<String>>,
    /// Each site entered, and whether a compiled function or module body was running then.
    /// A module's own `__main__` statements run in neither.
    locations: RefCell<Vec<(String, u32, bool)>>,
}
thread_local! {static ACTIVE:RefCell<Option<Runtime>>=const{RefCell::new(None)};}

impl Runtime {
    pub fn source_at(&self, path: &str, line: u32) -> SourceSite {
        let inside = !self.0.active.borrow().is_empty();
        self.0.locations.borrow_mut().push((path.into(), line, inside));
        SourceSite(self.clone())
    }
    fn new(root: PathBuf) -> Self {
        Self(Rc::new(State {
            root,
            modules: RefCell::new(HashMap::new()),
            active: RefCell::new(vec![]),
            locations: RefCell::new(vec![]),
        }))
    }
    pub fn import_module(&self, name: &str) -> Result<Val> {
        if let Some(value) = builtin_module(name) {
            return Ok(value);
        }
        if name == "importlib" {
            let raw = Val::decode(callback(json!({"op":"import","module":"importlib"}))?)?;
            let raw_import = raw.attr("import_module")?;
            let rt = self.clone();
            let import = Val::function(move |args, kwargs| {
                let name = args.first().context("import module name")?.str()?;
                if modules::source(&name).is_some() {
                    rt.import_module(&name)
                } else {
                    raw_import.call(args, kwargs)
                }
            });
            let fallback = Val::function(move |args, _| raw.attr(&args[0].str()?));
            return Ok(Val::namespace(vec![
                ("import_module".into(), import),
                ("__getattr__".into(), fallback),
            ]));
        }
        if name == "_document_export" {
            return self.document_export();
        }
        if let Some(path) = modules::source(name) {
            if let Some(e) = self.0.modules.borrow().get(name) {
                return Ok(e.0.values.clone());
            }
            let e = Env::module(name);
            e.set("__name__", name.into())?;
            e.set("__file__", Val::Path(self.0.root.join(path)))?;
            self.0.modules.borrow_mut().insert(name.into(), e.clone());
            self.0.active.borrow_mut().push(name.into());
            let result = modules::initialize(self.clone(), e.clone(), name);
            self.0.active.borrow_mut().pop();
            if result.is_err() {
                self.0.modules.borrow_mut().remove(name);
            }
            result.with_context(|| format!("initialize {name}"))?;
            return Ok(e.0.values.clone());
        }
        Val::decode(callback(json!({"op":"import","module":name}))?)
    }
    pub fn python_type(&self, module: &str, name: &str) -> Result<Val> {
        let imported = Val::decode(callback(json!({"op":"import","module":module}))?)?;
        imported.attr(name)
    }
    pub fn member(&self, module: &str, name: &str) -> Result<Val> {
        let imported = self.import_module(module)?;
        match imported.attr(name) {
            Ok(value) => Ok(value),
            Err(_) => self.import_module(&format!("{module}.{name}")),
        }
    }
    fn caller(&self) -> Option<String> {
        self.0.active.borrow().last().cloned()
    }
    pub fn frame(&self, e: &Env) -> Frame {
        self.0.active.borrow_mut().push(e.0.module.clone());
        Frame(self.clone())
    }
    fn note(&self, module: &str, function: &str, path: &Path) -> Result<()> {
        let primitive =
            Val::decode(callback(json!({"op":"import","module":module}))?)?.attr(function)?;
        primitive.call(vec![Val::Path(path.to_owned())], vec![])?;
        Ok(())
    }
    fn document_export(&self) -> Result<Val> {
        let mut fields = vec![];
        for name in ["export_pdf", "export_dxf"] {
            let rt = self.clone();
            let pdf = name == "export_pdf";
            fields.push((
                name.into(),
                Val::function(move |args, _| {
                    let source = args.first().context("export source")?.clone();
                    let target = PathBuf::from(args.get(1).context("export path")?.str()?);
                    hsm_documents::atomic_write(
                        &target,
                        |temporary| {
                            if pdf {
                                source.call(vec![Val::Path(temporary.to_owned())], vec![])?;
                                hsm_documents::canonicalize_file(temporary, "pdf")?;
                            } else {
                                source
                                    .attr("saveas")?
                                    .call(vec![Val::Path(temporary.to_owned())], vec![])?;
                                hsm_documents::canonicalize_file(temporary, "dxf")?;
                            }
                            Ok(())
                        },
                        false,
                    )?;
                    rt.note("_cadq_export", "note_write", &target)?;
                    Ok(Val::None)
                }),
            ));
        }
        Ok(Val::namespace(fields))
    }
    fn export(&self, _module: &str, path: &[String], value: &Val, identity: bool) -> Result<Value> {
        if matches!(value, Val::Func(_) | Val::Namespace(_) | Val::Type(_))
            || (identity
                && path
                    .first()
                    .is_some_and(|name| matches!(name.as_str(), "BOUNDS" | "_z_seam_passes")))
        {
            value.encode_ref()
        } else {
            hsm_documents::interop::native_snapshot(value)
        }
    }
}

pub struct Frame(Runtime);
impl Drop for Frame {
    fn drop(&mut self) {
        self.0.0.active.borrow_mut().pop();
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

pub fn request(input: &Value) -> Result<Value> {
    let root = PathBuf::from(input["root"].as_str().context("compiled recipe root")?);
    let rt = ACTIVE.with(|held| {
        let mut held = held.borrow_mut();
        if held.as_ref().is_none_or(|rt| rt.0.root != root) {
            *held = Some(Runtime::new(root));
        }
        held.as_ref().unwrap().clone()
    });
    if input["action"].as_str() == Some("invoke") {
        let callable = Val::decode(input["callable"].clone())?;
        let args = Val::decode(input["args"].clone())?.iter()?;
        let kwargs = keyword_items(Val::decode(input["kwargs"].clone())?)?;
        return rt.export("", &[], &callable.call(args, kwargs)?, false);
    }
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
    if input["action"].as_str() == Some("set") {
        let (name, parents) = path.split_last().context("set module field")?;
        let mut target = module.clone();
        for field in parents {
            target = target.attr(field)?;
        }
        let value = Val::decode(input["args"].clone())?
            .iter()?
            .first()
            .context("set value")?
            .clone();
        target.setattr(name, value)?;
        return Ok(Value::Null);
    }
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
                .filter(|name| !name.starts_with('_'))
                .collect::<Vec<_>>()
        )),
        "get" => rt.export(name, &path, &value, true),
        "call" => {
            let args = Val::decode(input["args"].clone())?.iter()?;
            let kwargs = keyword_items(Val::decode(input["kwargs"].clone())?)?;
            rt.0.active.borrow_mut().push(name.into());
            let result = value.call(args, kwargs);
            rt.0.active.borrow_mut().pop();
            rt.export(name, &path, &result?, false)
        }
        "main" => {
            let e =
                rt.0.modules
                    .borrow()
                    .get(name)
                    .cloned()
                    .context("main module")?;
            modules::entrypoint(rt.clone(), e, name)?;
            Ok(Value::Null)
        }
        action => bail!("unknown compiled recipe action {action}"),
    }
}

pub struct SourceSite(Runtime);
impl Drop for SourceSite {
    fn drop(&mut self) {
        self.0.0.locations.borrow_mut().pop();
    }
}

fn source_info() -> Result<Val> {
    let rt = ACTIVE
        .with(|held| held.borrow().clone())
        .context("source location outside a compiled call")?;
    let sites = rt.0.locations.borrow();
    // A `__main__` statement is where a program starts, not where anything is constructed:
    // a construction it leads to names the site it would name from any other entry, so the
    // same recipe makes the same numbers whichever program asked for it.
    let source = sites
        .iter()
        .rev()
        .find(|(path, _, inside)| *inside && path.ends_with("/enclosure.rs"))
        .or_else(|| sites.iter().rev().nth(1))
        .or_else(|| sites.last())
        .context("construction source location")?;
    Ok(Val::dict(vec![
        ("path".into(), source.0.clone().into()),
        ("line".into(), Val::Int(source.1 as i64)),
    ]))
}

pub fn context(enter: Val, exit: Val) -> Val {
    let cleanup = exit.clone();
    let entered = Val::function(move |args, kwargs| match enter.call(args, kwargs) {
        Ok(value) => Ok(value),
        Err(error) => {
            let _ = cleanup.call(vec![Val::None, Val::None, Val::None], vec![]);
            Err(error)
        }
    });
    Val::namespace(vec![
        ("__enter__".into(), entered),
        ("__exit__".into(), exit),
    ])
}

/// Cache an authored pure recipe without leaving the compiled worker.
pub fn memoize(function: Val, limit: Option<usize>) -> Val {
    let cache = Rc::new(RefCell::new(
        std::collections::VecDeque::<(String, Val)>::new(),
    ));
    Val::function(move |args, kwargs| {
        let key = serde_json::to_string(&(
            Val::tuple(args.clone()).encode()?,
            Val::dict(
                kwargs
                    .iter()
                    .map(|(key, value)| (key.clone().into(), value.clone()))
                    .collect(),
            )
            .encode()?,
        ))?;
        let hit = {
            let mut entries = cache.borrow_mut();
            entries
                .iter()
                .position(|(held, _)| held == &key)
                .and_then(|index| entries.remove(index))
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
