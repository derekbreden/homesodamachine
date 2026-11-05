"""Add a reachability trace to the private workspace copy of enclosure-data and hsm-documents.

Each worker appends unique lines to $HSM_TRACE_DIR/<step>-<pid>.log:
  fn <file>:<line>          a compiled function body ran (the bind() call site)
  req <action> <module> <path>   a request from Python reached a module
  ext <module>              a module imported through the Python callback
  member <module>.<name>    rt.member lookups
  cb <op> <module> <name>   a primitive callback query
"""
import re
import sys
from pathlib import Path

ws = Path(sys.argv[1])
compiled = ws / 'enclosure-data/src/compiled.rs'
src = compiled.read_text()

TRACE = r'''
thread_local! {
    static TRACE_OUT: RefCell<Option<(std::fs::File, std::collections::HashSet<String>)>> = RefCell::new(None);
    static TRACE_SITES: RefCell<std::collections::HashSet<(usize, u32)>> = RefCell::new(Default::default());
}
pub fn trace(kind: &str, detail: &str) {
    TRACE_OUT.with(|t| {
        let mut t = t.borrow_mut();
        if t.is_none() {
            if let Ok(dir) = std::env::var("HSM_TRACE_DIR") {
                let step = std::env::var("HSM_TRACE_STEP").unwrap_or_default();
                let path = format!("{dir}/{step}-{}.log", std::process::id());
                if let Ok(f) = std::fs::OpenOptions::new().create(true).append(true).open(path) {
                    *t = Some((f, Default::default()));
                }
            }
        }
        if let Some((f, seen)) = t.as_mut() {
            let key = format!("{kind}\t{detail}");
            if seen.insert(key.clone()) {
                use std::io::Write;
                let _ = writeln!(f, "{key}");
            }
        }
    });
}
#[track_caller]
fn trace_site() {
    let loc = std::panic::Location::caller();
    let key = (loc.file().as_ptr() as usize, loc.line());
    if TRACE_SITES.with(|s| s.borrow_mut().insert(key)) {
        trace("fn", &format!("{}:{}", loc.file(), loc.line()));
    }
}
'''

# bind(): record its caller (the compiled function body).
src = src.replace('pub type Parameters = Vec<(String, Option<Val>, bool)>;',
                  TRACE + '\npub type Parameters = Vec<(String, Option<Val>, bool)>;', 1)
src = src.replace('pub fn bind(\n', '#[track_caller]\npub fn bind(\n', 1)
src = src.replace(') -> Result<Env> {\n    let e = outer.child();',
                  ') -> Result<Env> {\n    trace_site();\n    let e = outer.child();', 1)
# imports through the callback, and member lookups
src = src.replace('        Val::decode(callback(json!({"op":"import","module":name}))?)\n    }\n    pub fn python_type',
                  '        trace("ext", name);\n        Val::decode(callback(json!({"op":"import","module":name}))?)\n    }\n    pub fn python_type', 1)
src = src.replace('    pub fn member(&self, module: &str, name: &str) -> Result<Val> {\n',
                  '    pub fn member(&self, module: &str, name: &str) -> Result<Val> {\n        trace("member", &format!("{module}.{name}"));\n', 1)
# requests from Python
src = src.replace('    let name = input["module"].as_str().context("compiled recipe module")?;\n',
                  '    let name = input["module"].as_str().context("compiled recipe module")?;\n'
                  '    trace("req", &format!("{} {} {}", input["action"].as_str().unwrap_or("call"), name, input["path"]));\n', 1)
assert src.count('trace(') >= 5, 'patch points moved'
compiled.write_text(src)

interop = ws / 'documents/src/interop.rs'
text = interop.read_text()
HOOK = r'''
thread_local! {
    static CB_TRACE: RefCell<Option<(std::fs::File, std::collections::HashSet<String>)>> = RefCell::new(None);
}
fn cb_trace(query: &Value) {
    CB_TRACE.with(|t| {
        let mut t = t.borrow_mut();
        if t.is_none() {
            if let Ok(dir) = std::env::var("HSM_TRACE_DIR") {
                let step = std::env::var("HSM_TRACE_STEP").unwrap_or_default();
                let path = format!("{dir}/{step}-{}.cb.log", std::process::id());
                if let Ok(f) = std::fs::OpenOptions::new().create(true).append(true).open(path) {
                    *t = Some((f, Default::default()));
                }
            }
        }
        if let Some((f, seen)) = t.as_mut() {
            let key = format!("cb\t{}\t{}\t{}", query["op"].as_str().unwrap_or(""),
                              query["module"].as_str().unwrap_or(""), query["name"].as_str().unwrap_or(""));
            if seen.insert(key.clone()) {
                use std::io::Write;
                let _ = writeln!(f, "{key}");
            }
        }
    });
}
'''
text = text.replace('pub fn callback(query: Value) -> Result<Value> {\n',
                    HOOK + 'pub fn callback(query: Value) -> Result<Value> {\n    cb_trace(&query);\n', 1)
assert 'cb_trace(&query)' in text
interop.write_text(text)
print('instrumented', compiled, interop)
