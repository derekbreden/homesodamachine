//! The compiled build plan uses native values and explicit library primitive callbacks.

use anyhow::{Context, Result, bail, ensure};
pub use hsm_documents::interop::{Val, binary, unary, compare, format};
use hsm_documents::interop::{builtin, builtin_module, callback};
use serde_json::{Value, json};
use std::cell::RefCell;
use std::collections::HashMap;
use std::path::PathBuf;
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
        Self(Rc::new(Scope { values: Val::namespace(vec![]), parent: None, module: module.into() }))
    }
    pub fn child(&self) -> Self {
        Self(Rc::new(Scope { values: Val::namespace(vec![]), parent: Some(self.clone()), module: self.0.module.clone() }))
    }
    pub fn get(&self, name: &str) -> Result<Val> {
        if name == "globals" || name == "locals" {
            let scope = if name == "globals" { self.root() } else { self.clone() };
            return Ok(Val::function(move |_, _| Ok(scope.dictionary())));
        }
        if let Ok(value) = self.0.values.get(name.into()) { return Ok(value); }
        if let Some(parent) = &self.0.parent { return parent.get(name); }
        if let Some(value) = builtin(name) { return Ok(value); }
        if name.ends_with("Error") || matches!(name,"Exception"|"SystemExit"|"StopIteration") {
            let kind=name.to_owned();
            return Ok(Val::function(move |args,_| Ok(Val::Str(format!("{kind}: {}",args.first().map(Val::str).transpose()?.unwrap_or_default())))));
        }
        bail!("{}: unknown name {name}",self.0.module)
    }
    pub fn set(&self, name: &str, value: Val) -> Result<()> { self.0.values.set(name.into(),value) }
    fn root(&self)->Self { self.0.parent.as_ref().map_or_else(||self.clone(),Env::root) }
    fn dictionary(&self)->Val { match &self.0.values {Val::Namespace(rows)=>Val::Dict(rows.clone()),_=>unreachable!()} }
}

pub type Parameters=Vec<(String,Option<Val>,bool)>;
pub enum Flow {Continue,LoopContinue}
pub fn bind(outer:&Env,params:&Parameters,args:Vec<Val>,kwargs:Vec<(String,Val)>,varargs:Option<&str>,varkw:Option<&str>)->Result<Env> {
    let e=outer.child();let mut positional=args.into_iter();let mut supplied=kwargs;
    for (name,default,keyword_only) in params {
        let keyword=supplied.iter().position(|(key,_)|key==name);
        let value=if !keyword_only {positional.next()}else{None};
        let value=match(value,keyword){
            (Some(_),Some(_))=>bail!("multiple arguments for {name}"),
            (Some(value),None)=>value,
            (None,Some(index))=>supplied.remove(index).1,
            (None,None)=>default.clone().with_context(||format!("missing argument {name}"))?,
        };e.set(name,value)?;
    }
    let excess:Vec<_>=positional.collect();
    if let Some(name)=varargs {e.set(name,Val::tuple(excess))?;} else {ensure!(excess.is_empty(),"too many positional arguments");}
    if let Some(name)=varkw {e.set(name,Val::dict(supplied.into_iter().map(|(k,v)|(k.into(),v)).collect()))?;}else{ensure!(supplied.is_empty(),"unexpected keyword arguments");}
    Ok(e)
}

pub fn unpack(value:Val,count:usize)->Result<Vec<Val>> {let values=value.iter()?;ensure!(values.len()==count,"unpack: expected {count}, got {}",values.len());Ok(values)}
pub fn keyword_items(value:Val)->Result<Vec<(String,Val)>> {value.iter()?.into_iter().map(|key|Ok((key.str()?,value.get(key)?))).collect()}
pub fn val_string(value:Val)->Result<String>{value.str()}
#[derive(Clone)]
pub struct Runtime(Rc<State>);
struct State {
    root:PathBuf,
    modules:RefCell<HashMap<String,Env>>,
    active:RefCell<Vec<String>>,
}
thread_local! {static ACTIVE:RefCell<Option<Runtime>>=const{RefCell::new(None)};}

impl Runtime {
    fn new(root:PathBuf)->Self {Self(Rc::new(State{root,modules:RefCell::new(HashMap::new()),active:RefCell::new(vec![])}))}
    pub fn import_module(&self,name:&str)->Result<Val> {
        if let Some(value)=builtin_module(name){return Ok(value)}
        if let Some(path)=modules::source(name){
            if let Some(e)=self.0.modules.borrow().get(name){return Ok(e.0.values.clone())}
            let e=Env::module(name);
            e.set("__name__",name.into())?;
            e.set("__file__",Val::Path(self.0.root.join(path)))?;
            self.0.modules.borrow_mut().insert(name.into(),e.clone());
            self.0.active.borrow_mut().push(name.into());
            let result=modules::initialize(self.clone(),e.clone(),name);
            self.0.active.borrow_mut().pop();
            if result.is_err(){self.0.modules.borrow_mut().remove(name);}
            result.with_context(||format!("initialize {name}"))?;
            return Ok(e.0.values.clone());
        }
        Val::decode(callback(json!({"op":"import","module":name}))?)
    }
    pub fn member(&self,module:&str,name:&str)->Result<Val>{
        let imported=self.import_module(module)?;
        match imported.attr(name){Ok(value)=>Ok(value),Err(_)=>self.import_module(&format!("{module}.{name}"))}
    }
    pub fn frame(&self,e:&Env)->Frame {self.0.active.borrow_mut().push(e.0.module.clone());Frame(self.clone())}
    fn export(&self,_module:&str,_path:&[String],value:&Val)->Result<Value>{
        match value {
            Val::Func(_)|Val::Namespace(_)|Val::Type(_)=>value.encode_ref(),
            Val::Path(path)=>Ok(json!({"$path":path.to_string_lossy()})),
            Val::Tuple(items)=>Ok(json!({"$tuple":items.iter().map(|v|self.export(_module,_path,v)).collect::<Result<Vec<_>>>()?})),
            Val::List(items)=>Ok(Value::Array(items.borrow().iter().map(|v|self.export(_module,_path,v)).collect::<Result<_>>()?)),
            Val::Dict(items)=>Ok(json!({"$dict":items.borrow().iter().map(|(k,v)|Ok(json!([self.export(_module,_path,k)?,self.export(_module,_path,v)?]))).collect::<Result<Vec<Value>>>()?})),
            _=>value.encode(),
        }
    }
}

pub struct Frame(Runtime);
impl Drop for Frame {fn drop(&mut self){self.0.0.active.borrow_mut().pop();}}

pub fn request(input:&Value)->Result<Value>{
    let root=PathBuf::from(input["root"].as_str().context("compiled recipe root")?);
    let rt=ACTIVE.with(|held|{let mut held=held.borrow_mut();if held.as_ref().is_none_or(|rt|rt.0.root!=root){*held=Some(Runtime::new(root));}held.as_ref().unwrap().clone()});
    let name=input["module"].as_str().context("compiled recipe module")?;
    let module=rt.import_module(name)?;
    let path:Vec<String>=input["path"].as_array().map(|a|a.iter().filter_map(Value::as_str).map(str::to_owned).collect()).unwrap_or_default();
    let mut value=module.clone();for field in &path {value=value.attr(field)?;}
    match input["action"].as_str().unwrap_or("call"){
        "invoke"=>{
            let function=Val::decode(input["function"].clone())?;
            let args=Val::decode(input["args"].clone())?.iter()?;
            let kwargs=keyword_items(Val::decode(input["kwargs"].clone())?)?;
            rt.0.active.borrow_mut().push(name.into());
            let result=function.call(args,kwargs);rt.0.active.borrow_mut().pop();
            rt.export(name,&path,&result?)
        },
        "names"=>Ok(json!(module.iter()?.iter().map(Val::str).collect::<Result<Vec<_>>>()?)),
        "public-names"=>Ok(json!(module.iter()?.iter().map(Val::str).collect::<Result<Vec<_>>>()?.into_iter().filter(|s|!s.starts_with('_')&&!s.contains('.')).collect::<Vec<_>>())),
        "get"=>rt.export(name,&path,&value),
        "call"=>{
            let args=Val::decode(input["args"].clone())?.iter()?;
            let kwargs=keyword_items(Val::decode(input["kwargs"].clone())?)?;
            rt.0.active.borrow_mut().push(name.into());
            let result=value.call(args,kwargs);rt.0.active.borrow_mut().pop();
            rt.export(name,&path,&result?)
        },
        "main"=>{let e=rt.0.modules.borrow().get(name).cloned().context("main module")?;modules::entrypoint(rt.clone(),e,name)?;Ok(Value::Null)},
        action=>bail!("unknown compiled recipe action {action}"),
    }
}
