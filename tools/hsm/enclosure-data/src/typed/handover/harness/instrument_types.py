"""Patch the private workspace copy to log the types every compiled function receives and returns.

Each worker appends unique lines to $HSM_TRACE_DIR/<step>-<pid>.types.log:
  sig <file>:<line> <param>=<type> ...   the bound parameters of one call
  ret <file>:<line> <type>               what that call returned
A type is a compact shape: F float, I int, B bool, S str, N None, P path, Y bytes,
T(..) tuple, L[..] list, D{k:v} dict, Set[..], NS namespace, Fn callable, Ty:<name> type,
R:<python type> a Python object.
"""
import sys
from pathlib import Path

ws = Path(sys.argv[1])
compiled = ws / 'enclosure-data/src/compiled.rs'
src = compiled.read_text()

INTEROP = r'''
thread_local! {
    static TYPE_OUT: RefCell<Option<(std::fs::File, std::collections::HashSet<String>)>> = RefCell::new(None);
    static PY_TYPES: RefCell<std::collections::HashMap<String, String>> = RefCell::new(std::collections::HashMap::new());
}
pub fn type_log(line: String) {
    TYPE_OUT.with(|t| {
        let mut t = t.borrow_mut();
        if t.is_none() {
            if let Ok(dir) = std::env::var("HSM_TRACE_DIR") {
                let step = std::env::var("HSM_TRACE_STEP").unwrap_or_default();
                let path = format!("{dir}/{step}-{}.types.log", std::process::id());
                if let Ok(f) = std::fs::OpenOptions::new().create(true).append(true).open(path) {
                    *t = Some((f, Default::default()));
                }
            }
        }
        if let Some((f, seen)) = t.as_mut() {
            if seen.insert(line.clone()) {
                use std::io::Write;
                let _ = writeln!(f, "{line}");
            }
        }
    });
}
fn py_type(value: &Value) -> String {
    let key = value.to_string();
    if let Some(found) = PY_TYPES.with(|m| m.borrow().get(&key).cloned()) {
        return found;
    }
    let name = (|| -> Result<String> {
        let builtins = Val::decode(callback(json!({"op":"import","module":"builtins"}))?)?;
        let ty = builtins.attr("type")?.call(vec![Val::Ref(value.clone())], vec![])?;
        Ok(ty.attr("__name__")?.str()?)
    })()
    .unwrap_or_else(|_| "?".into());
    PY_TYPES.with(|m| m.borrow_mut().insert(key, name.clone()));
    name
}
pub fn type_of(v: &Val, depth: usize) -> String {
    fn union(items: &[Val], depth: usize) -> String {
        let mut kinds: Vec<String> = vec![];
        for item in items.iter().take(40) {
            let k = type_of(item, depth + 1);
            if !kinds.contains(&k) {
                kinds.push(k);
            }
        }
        kinds.sort();
        if kinds.len() > 4 {
            kinds.truncate(4);
            kinds.push("..".into());
        }
        kinds.join("|")
    }
    if depth > 3 {
        return "~".into();
    }
    match v {
        Val::None => "N".into(),
        Val::Bool(_) => "B".into(),
        Val::Int(_) => "I".into(),
        Val::Float(_) => "F".into(),
        Val::Str(_) => "S".into(),
        Val::Bytes(_) => "Y".into(),
        Val::Path(_) => "P".into(),
        Val::Tuple(items) => {
            if items.len() <= 8 {
                format!("T({})", items.iter().map(|i| type_of(i, depth + 1)).collect::<Vec<_>>().join(","))
            } else {
                format!("T{}[{}]", items.len(), union(items, depth))
            }
        }
        Val::List(items) => format!("L[{}]", union(&items.borrow(), depth)),
        Val::Set(items) => format!("Set[{}]", union(&items.borrow(), depth)),
        Val::FrozenSet(items) => format!("FSet[{}]", union(items, depth)),
        Val::Dict(entries) => {
            let entries = entries.borrow();
            let keys: Vec<Val> = entries.iter().map(|(k, _)| k.clone()).collect();
            let values: Vec<Val> = entries.iter().map(|(_, v)| v.clone()).collect();
            let named = keys.iter().all(|k| matches!(k, Val::Str(_))) && keys.len() <= 12;
            if named {
                format!("D{{{}}}", entries.iter().map(|(k, v)| format!("{}:{}", k.str().unwrap_or_default(), type_of(v, depth + 1))).collect::<Vec<_>>().join(","))
            } else {
                format!("D{{{}:{}}}", union(&keys, depth), union(&values, depth))
            }
        }
        Val::Namespace(_) => "NS".into(),
        Val::Func(_) => "Fn".into(),
        Val::Type(name) => format!("Ty:{name}"),
        Val::Ref(value) => format!("R:{}", py_type(value)),
        Val::Slice { .. } => "Slice".into(),
    }
}
thread_local! {
    static SITE_STACK: RefCell<Vec<Option<String>>> = RefCell::new(vec![]);
}
pub fn site_mark(site: &str) {
    SITE_STACK.with(|s| {
        if let Some(top) = s.borrow_mut().last_mut() {
            if top.is_none() {
                *top = Some(site.to_owned());
            }
        }
    });
}
pub fn call_enter() {
    SITE_STACK.with(|s| s.borrow_mut().push(None));
}
pub fn call_exit(result: &Result<Val>) {
    let site = SITE_STACK.with(|s| s.borrow_mut().pop()).flatten();
    if let (Some(site), Ok(value)) = (site, result) {
        type_log(format!("ret\t{site}\t{}", type_of(value, 0)));
    }
}
'''
SITE = r'''#[track_caller]
fn type_site(params: &Parameters, e: &Env) {
    let loc = std::panic::Location::caller();
    let site = format!("{}:{}", loc.file(), loc.line());
    hsm_documents::interop::site_mark(&site);
    let mut parts = vec![];
    for (name, _, _) in params.iter() {
        let shown = e.0.values.get(name.clone().into()).map(|v| hsm_documents::interop::type_of(&v, 0)).unwrap_or_else(|_| "?".into());
        parts.push(format!("{name}={shown}"));
    }
    hsm_documents::interop::type_log(format!("sig\t{site}\t{}", parts.join(" ")));
}
'''

src = src.replace('pub type Parameters = Vec<(String, Option<Val>, bool)>;',
                  SITE + '\npub type Parameters = Vec<(String, Option<Val>, bool)>;', 1)
src = src.replace('pub fn bind(\n', '#[track_caller]\npub fn bind(\n', 1)
old_tail = '        ensure!(supplied.is_empty(), "unexpected keyword arguments");\n    }\n    Ok(e)\n}'
assert old_tail in src
src = src.replace(old_tail, '        ensure!(supplied.is_empty(), "unexpected keyword arguments");\n    }\n    type_site(params, &e);\n    Ok(e)\n}', 1)
compiled.write_text(src)

interop = ws / 'documents/src/interop.rs'
text = interop.read_text()
text = text.replace('pub fn callback(query: Value) -> Result<Value> {\n', INTEROP + '\npub fn callback(query: Value) -> Result<Value> {\n', 1)
old_call = '            Self::Func(f) => f(args, kwargs),\n            Self::Ref(_) => remote(\n                "call",'
assert old_call in text
text = text.replace(old_call, '            Self::Func(f) => {\n                call_enter();\n                let result = f(args, kwargs);\n                call_exit(&result);\n                result\n            }\n            Self::Ref(_) => remote(\n                "call",', 1)
interop.write_text(text)
print('instrumented types', compiled, interop)
