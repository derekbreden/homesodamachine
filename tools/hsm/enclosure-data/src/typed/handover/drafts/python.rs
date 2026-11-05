//! The Python the recipes still call: the build's own bookkeeping (`_rust_part`, `_cadq_export`),
//! dimension modules owned outside this crate, and third-party libraries. Each call goes through
//! the worker's callback; recipes reach it through the typed functions here and in their own
//! modules, never by building calls themselves.
use crate::py::IntoVal;
use anyhow::{Context, Result};
use hsm_documents::interop::{Val, callback};
use serde_json::json;
use std::cell::RefCell;
use std::collections::{BTreeMap, HashMap};
use std::path::{Path, PathBuf};

thread_local! {
    static MODULES: RefCell<HashMap<String, Val>> = RefCell::new(HashMap::new());
}

/// Forget the imported modules: a request for another checkout starts over.
pub fn reset() {
    MODULES.with(|m| m.borrow_mut().clear());
}

/// `import name`, through the callback; one import per name per run.
pub fn import(name: &str) -> Result<Val> {
    if let Some(found) = MODULES.with(|m| m.borrow().get(name).cloned()) {
        return Ok(found);
    }
    let module = Val::decode(callback(json!({"op":"import","module":name}))?)
        .with_context(|| format!("import {name}"))?;
    MODULES.with(|m| m.borrow_mut().insert(name.into(), module.clone()));
    Ok(module)
}

/// `module.name`.
pub fn member(module: &str, name: &str) -> Result<Val> {
    import(module)?.attr(name).with_context(|| format!("{module}.{name}"))
}

/// `module.name` as a float.
pub fn float(module: &str, name: &str) -> Result<f64> {
    member(module, name)?.num().with_context(|| format!("{module}.{name} is a number"))
}

/// `module.name` as an integer.
pub fn int(module: &str, name: &str) -> Result<i64> {
    member(module, name)?.integer().with_context(|| format!("{module}.{name} is an integer"))
}

/// `module.function(*args, **kwargs)`.
pub fn call(module: &str, function: &str, args: Vec<Val>, kwargs: Vec<(&str, Val)>) -> Result<Val> {
    member(module, function)?
        .call(args, kwargs.into_iter().map(|(k, v)| (k.to_owned(), v)).collect())
        .with_context(|| format!("{module}.{function}()"))
}

/// `value.method(*args, **kwargs)` on a Python object.
pub fn method(value: &Val, name: &str, args: Vec<Val>, kwargs: Vec<(&str, Val)>) -> Result<Val> {
    value
        .attr(name)?
        .call(args, kwargs.into_iter().map(|(k, v)| (k.to_owned(), v)).collect())
        .with_context(|| format!(".{name}()"))
}

/// `setattr(module, name, value)` on a Python module.
pub fn set_member(module: &str, name: &str, value: Val) -> Result<()> {
    import(module)?.setattr(name, value)
}

/// `_cadq_export.note_read(path)`: the build records a file the recipe read.
pub fn note_read(path: &Path) -> Result<()> {
    call("_cadq_export", "note_read", vec![Val::Path(path.to_owned())], vec![])?;
    Ok(())
}

/// `_cadq_export.note_write(path)`: the build records a file the recipe wrote.
pub fn note_write(path: &Path) -> Result<()> {
    call("_cadq_export", "note_write", vec![Val::Path(path.to_owned())], vec![])?;
    Ok(())
}

/// `_rust_part.cut(crate, name, numbers, part_dir, numbers_name=...)`: the part's numbers
/// written beside it and its program run.
pub fn rust_part_cut(
    krate: &str,
    name: &str,
    numbers: Val,
    part_dir: &Path,
    numbers_name: Option<&str>,
) -> Result<Val> {
    let mut kwargs = vec![];
    if let Some(n) = numbers_name {
        kwargs.push(("numbers_name", Val::Str(n.into())));
    }
    call(
        "_rust_part",
        "cut",
        vec![krate.into_val(), name.into_val(), numbers, Val::Path(part_dir.to_owned())],
        kwargs,
    )
}

/// `_materials.linear(colour)`.
pub fn linear(colour: Val) -> Result<Val> {
    call("_materials", "linear", vec![colour], vec![])
}

/// The documents a module's numbers are substituted into.
#[derive(Clone, Copy, Debug)]
pub enum Document {
    Markdown,
    Mermaid,
    Python,
}

/// `docgen.substitute_md(path, variables)` and its siblings, as the module named `module`
/// (its repository source path) calls them.
pub fn substitute(
    kind: Document,
    path: &Path,
    variables: &[(String, String)],
    source: &str,
) -> Result<()> {
    let values: BTreeMap<String, String> = variables.iter().cloned().collect();
    let source = format!("/{source}");
    let hardware = source.starts_with("/hardware/");
    note_read(path)?;
    let kind = match kind {
        Document::Markdown => hsm_documents::Kind::Markdown,
        Document::Mermaid => hsm_documents::Kind::Mermaid,
        Document::Python => hsm_documents::Kind::Python,
    };
    if hardware && matches!(kind, hsm_documents::Kind::Markdown) {
        let sidecar = path.with_extension("figures.json");
        if sidecar.is_file() {
            note_read(&sidecar)?;
        }
    }
    let result = hsm_documents::substitute(path, kind, &values, Some(&source), hardware)?;
    for maintained in result.maintained {
        call("docgen", "note_rewritten", vec![Val::Path(maintained)], vec![])?;
    }
    Ok(())
}

/// A repository path under the run's root.
pub fn under(root: &Path, relative: &str) -> PathBuf {
    root.join(relative)
}
