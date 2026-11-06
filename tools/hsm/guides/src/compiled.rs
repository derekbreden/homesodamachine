//! Compiled guide pages and illustrations share scalar/container values and
//! explicit third-party primitive callbacks. Every recipe's control flow is Rust.

use anyhow::{Context, Result, bail, ensure};
pub use hsm_documents::interop::{Val, binary, compare, format, unary};
use hsm_documents::interop::{builtin, builtin_module, callback};
use serde_json::{Value, json};
use std::cell::RefCell;
use std::collections::{BTreeMap, HashMap};
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
    pub fn namespace(&self) -> Val {
        self.root().0.values.clone()
    }
    pub fn child(&self) -> Self {
        Self(Rc::new(Scope {
            values: Val::namespace(vec![]),
            parent: Some(self.clone()),
            module: self.0.module.clone(),
        }))
    }
    pub fn get(&self, name: &str) -> Result<Val> {
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
            let kind = name.to_owned();
            return Ok(Val::function(move |args, _| {
                Ok(Val::Str(format!(
                    "{kind}: {}",
                    args.first().map(Val::str).transpose()?.unwrap_or_default()
                )))
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
    pub fn set_nonlocal(&self, name: &str, value: Val) -> Result<()> {
        let parent = self
            .0
            .parent
            .as_ref()
            .context("nonlocal outside a function")?;
        if parent.0.values.get(name.into()).is_ok() {
            parent.set(name, value)
        } else {
            parent.set_nonlocal(name, value)
        }
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
    Break,
    Next,
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
    builtin(name)
        .with_context(|| format!("missing builtin {name}"))?
        .call(args, kwargs)
}
pub fn delete(e: &Env, name: &str) -> Result<()> {
    e.0.values.delete(name.into())
}
pub fn delete_item(value: Val, key: Val) -> Result<()> {
    value.delete(key)
}
pub fn import_star(e: &Env, module: Val) -> Result<()> {
    let explicit = module.attr("__all__").ok();
    let names = if let Some(names) = &explicit {
        names.iter()?
    } else {
        module
            .attr("__dict__")
            .and_then(|v| v.iter())
            .or_else(|_| module.iter())?
    };
    for name in names {
        let key = name.str()?;
        if explicit.is_some() || !key.starts_with('_') {
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
}
thread_local! {static ACTIVE:RefCell<Option<Runtime>>=const{RefCell::new(None)};}

impl Runtime {
    fn new(root: PathBuf) -> Self {
        Self(Rc::new(State {
            root,
            modules: RefCell::new(HashMap::new()),
            active: RefCell::new(vec![]),
        }))
    }
    pub fn import_module(&self, name: &str) -> Result<Val> {
        if let Some(value) = builtin_module(name) {
            return Ok(value);
        }
        if name == "_guide_native" {
            return hsm_guide_native::module();
        }
        if name == "shutil" {
            return hsm_guide_native::files();
        }
        if name == "docgen" {
            return self.docgen();
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
            e.set("__doc__", modules::documentation(name).unwrap_or("").into())?;
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
    pub fn member(&self, module: &str, name: &str) -> Result<Val> {
        self.import_module(module)?
            .attr(name)
            .or_else(|_| self.import_module(&format!("{module}.{name}")))
    }
    fn module_path(&self, name: &str) -> Option<PathBuf> {
        modules::source(name).map(|p| self.0.root.join(p))
    }
    pub fn python_type(&self, module: &str, name: &str) -> Result<Val> {
        let loader = Val::decode(callback(
            json!({"op":"import","module":"_guides_compiled"}),
        )?)?
        .attr("python_type_module")?;
        let path = self.module_path(module).context("compiled class source")?;
        let imported = loader.call(vec![Val::Str(module.into()), Val::Path(path)], vec![])?;
        imported.attr(name)
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
    fn docgen(&self) -> Result<Val> {
        let mut fields = vec![];
        for (name, kind) in [
            ("substitute_md", hsm_documents::Kind::Markdown),
            ("substitute_mmd", hsm_documents::Kind::Mermaid),
            ("substitute_py_comments", hsm_documents::Kind::Python),
        ] {
            let rt = self.clone();
            let caller = self.caller();
            fields.push((
                name.into(),
                Val::function(move |args, kwargs| {
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
                    let mut values = BTreeMap::new();
                    for key in variables.iter()? {
                        values.insert(key.str()?, variables.get(key)?.str()?);
                    }
                    let source = caller
                        .as_deref()
                        .and_then(|name| modules::source(name))
                        .map(|p| format!("/{p}"));
                    let hardware = source
                        .as_deref()
                        .is_some_and(|s| s.starts_with("/hardware/"));
                    rt.note("_cadq_export", "note_read", &path)?;
                    if hardware && matches!(kind, hsm_documents::Kind::Markdown) {
                        let sidecar = path.with_extension("figures.json");
                        if sidecar.is_file() {
                            rt.note("_cadq_export", "note_read", &sidecar)?;
                        }
                    }
                    let result = hsm_documents::substitute(
                        &path,
                        kind,
                        &values,
                        source.as_deref(),
                        hardware,
                    )?;
                    for maintained in result.maintained {
                        rt.note("docgen", "note_rewritten", &maintained)?;
                    }
                    Ok(Val::None)
                }),
            ));
        }
        fields.push((
            "cells".into(),
            Val::function(|args, _| {
                Ok(Val::list(
                    hsm_documents::cells(&args[0].str()?)
                        .into_iter()
                        .map(Val::Str)
                        .collect(),
                ))
            }),
        ));
        let rt = self.clone();
        fields.push((
            "load_module".into(),
            Val::function(move |args, kwargs| {
                let path = args.get(1).context("load_module path")?.str()?;
                if let Some(name) = modules::by_path(&path) {
                    return rt.import_module(name);
                }
                let module = Val::decode(callback(json!({"op":"import","module":"docgen"}))?)?;
                module.attr("load_module")?.call(args, kwargs)
            }),
        ));
        let raw = Val::decode(callback(json!({"op":"import","module":"docgen"}))?)?;
        fields.push(("note_rewritten".into(), raw.attr("note_rewritten")?));
        Ok(Val::namespace(fields))
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
    fn export(&self, _module: &str, _path: &[String], value: &Val) -> Result<Value> {
        if matches!(value, Val::Func(_) | Val::Namespace(_) | Val::Type(_)) {
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
        "get" => rt.export(name, &path, &value),
        "call" => {
            let args = Val::decode(input["args"].clone())?.iter()?;
            let kwargs = keyword_items(Val::decode(input["kwargs"].clone())?)?;
            rt.0.active.borrow_mut().push(name.into());
            let result = value.call(args, kwargs);
            rt.0.active.borrow_mut().pop();
            rt.export(name, &path, &result?)
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

/// The swept exterior's section at `outer`, the box's X, Y and Z spans: each station a tuple, as
/// the recipes read it.
pub fn swept_profile(outer: Val) -> Result<Val> {
    let bounds = outer.iter()?.iter().map(Val::num).collect::<Result<Vec<_>>>()?;
    let bounds: [f64; 6] = bounds.try_into().map_err(|_| anyhow::anyhow!("an outer box has six bounds"))?;
    let p = hsm_enclosure_interface::swept::profile(&bounds);
    let station = |v: &[f64]| Val::tuple(v.iter().map(|&x| Val::Float(x)).collect());
    Ok(Val::dict(vec![
        (Val::Str("end".into()), station(&p.end)),
        (Val::Str("foot".into()), station(&p.foot)),
        (Val::Str("front_mid".into()), station(&p.front_mid)),
        (Val::Str("normal".into()), station(&p.normal)),
        (Val::Str("origin".into()), station(&p.origin)),
        (Val::Str("roof".into()), station(&p.roof)),
        (Val::Str("start".into()), station(&p.start)),
        (Val::Str("top_mid".into()), station(&p.top_mid)),
    ]))
}
