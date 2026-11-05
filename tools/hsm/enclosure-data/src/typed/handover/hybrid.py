"""Write the hybrid crate root: the shared tree's main.rs and compiled.rs with the typed registry
wired in. Re-run after either file changes upstream.

usage: python3 hybrid.py
"""
import os
from pathlib import Path

REPO = Path('/Users/derekbredensteiner/Developer/homesodamachine')
R = Path(__file__).resolve().parent
SRC = REPO / 'tools/hsm/enclosure-data/src'
OUT = R / 'typed/enclosure-data/src'


def replace(text, old, new, count=1):
    assert text.count(old) == count, (old, text.count(old))
    return text.replace(old, new)


main = (SRC / 'main.rs').read_text()
main = replace(main, 'mod compiled;\n', 'mod compiled;\nmod typed;\n')
main = replace(main, 'let result = compiled::request(v);\n        compiled::register_io()?;',
               'let result = typed::rt::request(v);\n        typed::rt::register_io()?;')

compiled = (SRC / 'compiled.rs').read_text()
old = '''        if let Some(path) = modules::source(name) {
            if let Some(e) = self.0.modules.borrow().get(name) {
                return Ok(e.0.values.clone());
            }'''
new = '''        if let Some(path) = modules::source(name) {
            if crate::typed::converted(name) {
                return crate::typed::rt::import_typed(&self.0.root, name);
            }
            return self.generated(name, path);
        }
        Val::decode(callback(json!({"op":"import","module":name}))?)
    }
    /// A module's generated namespace, run on first use.
    fn generated(&self, name: &str, path: &str) -> Result<Val> {
        {
            if let Some(e) = self.0.modules.borrow().get(name) {
                return Ok(e.0.values.clone());
            }'''
compiled = replace(compiled, old, new)
old = '''            result.with_context(|| format!("initialize {name}"))?;
            return Ok(e.0.values.clone());
        }
        Val::decode(callback(json!({"op":"import","module":name}))?)
    }'''
new = '''            result.with_context(|| format!("initialize {name}"))?;
            Ok(e.0.values.clone())
        }
    }'''
compiled = replace(compiled, old, new)
compiled = replace(compiled, '            self.0.modules.borrow_mut().insert(name.into(), e.clone());\n            self.0.active.borrow_mut().push(name.into());\n            let result = modules::initialize(self.clone(), e.clone(), name);', '            self.0.modules.borrow_mut().insert(name.into(), e.clone());\n            crate::typed::rt::generated_started(&self.0.root, name, &e.0.values);\n            self.0.active.borrow_mut().push(name.into());\n            let result = modules::initialize(self.clone(), e.clone(), name);')
compiled += '''
fn generated_runtime(root: &Path) -> Runtime {
    ACTIVE.with(|held| {
        let mut held = held.borrow_mut();
        if held.as_ref().is_none_or(|rt| rt.0.root != root) {
            *held = Some(Runtime::new(root.to_owned()));
        }
        held.as_ref().unwrap().clone()
    })
}
/// The namespace of a module the typed registry has not converted.
pub fn import_generated(root: &Path, name: &str) -> Result<Val> {
    generated_runtime(root).import_module(name)
}
/// A module's generated namespace even where the typed registry converts the module: a module
/// converted function by function starts from it and replaces what it has converted.
pub fn generated_namespace(root: &Path, name: &str) -> Result<Val> {
    let rt = generated_runtime(root);
    rt.generated(name, modules::source(name).context("generated module source")?)
}
/// A generated module run as a script.
pub fn entrypoint_generated(root: &Path, name: &str) -> Result<()> {
    let rt = generated_runtime(root);
    rt.import_module(name)?;
    let e = rt.0.modules.borrow().get(name).cloned().context("main module")?;
    rt.0.active.borrow_mut().push(name.into());
    let result = modules::entrypoint(rt.clone(), e, name);
    rt.0.active.borrow_mut().pop();
    result.map(|_| ())
}
'''
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'main.rs').write_text(main)
(OUT / 'compiled.rs').write_text(compiled)
for entry in sorted(SRC.iterdir()):
    if entry.name in ('main.rs', 'compiled.rs', 'typed'):
        continue
    link = OUT / entry.name
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(entry)
print('hybrid root', OUT)
