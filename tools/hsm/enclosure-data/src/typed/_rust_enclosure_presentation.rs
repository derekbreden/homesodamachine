//! The enclosure's existing print-surface presentation, authored by Rust.
//!
//! Typed API: [`print_payload`] draws one printed STL's presentation payload beside its STEP
//! and returns the `enclosure-presentation` program's reading (a JSON document, as Python's
//! `json.loads` gives it).
use super::num;
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::Result;
use std::cell::OnceCell;
use std::path::{Path, PathBuf};

pub const TYPED: bool = true;
const MODULE: &str = "_rust_enclosure_presentation";

/// The module's provider handles and the print-surface rules, read on first use.
struct State {
    /// `_payload_rules.CREASE_DEG` and `_payload_rules.LINEAR_DEFLECTION_RATIO`.
    rules: OnceCell<(Val, Val)>,
}

/// `print_payload`'s keyword-only options, with the Python defaults.
#[derive(Clone)]
pub struct Options {
    /// Retains the quadrant writers' existing slicer refusal. This flag and the next reach the
    /// program's numbers as the caller gave them.
    pub check_print: Val,
    pub preserve_print_triangles: Val,
    /// The solid identity recorded in the payload (a Python value, passed through as it is).
    pub identity: Option<Val>,
    /// The STEP the payload names as its source.
    pub source: Option<PathBuf>,
    /// The printed STL; `step` with the `.stl` suffix when absent.
    pub stl: Option<PathBuf>,
    pub verbose: bool,
}
impl Default for Options {
    fn default() -> Self {
        Self {
            check_print: Val::Bool(false),
            preserve_print_triangles: Val::Bool(false),
            identity: None,
            source: None,
            stl: None,
            verbose: true,
        }
    }
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    rt.keep(MODULE, State { rules: OnceCell::new() });
    ns.set("json", rt.import("json")?)?;
    rt.import("pathlib")?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    ns.set("tempfile", rt.import("tempfile")?)?;
    ns.def(rt, "print_payload", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["step"], &[
            "check_print", "preserve_print_triangles", "identity", "source", "stl", "verbose",
        ])?;
        let step = PathBuf::from(b.req("step")?.str()?);
        let options = Options {
            check_print: b.opt("check_print").unwrap_or(Val::Bool(false)),
            preserve_print_triangles: b.opt("preserve_print_triangles").unwrap_or(Val::Bool(false)),
            identity: b.some("identity"),
            source: b.some("source").map(|v| v.str().map(PathBuf::from)).transpose()?,
            stl: b.some("stl").map(|v| v.str().map(PathBuf::from)).transpose()?,
            verbose: b.bool_or("verbose", true)?,
        };
        print_payload(rt, &step, &options)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}

/// `_payload_rules.CREASE_DEG` and `LINEAR_DEFLECTION_RATIO`: provider constants, read once.
fn rules(rt: &Rt, state: &State) -> Result<(Val, Val)> {
    if let Some(rules) = state.rules.get() {
        return Ok(rules.clone());
    }
    let crease = rt.member("_payload_rules", "CREASE_DEG")?;
    let deflection = rt.member("_payload_rules", "LINEAR_DEFLECTION_RATIO")?;
    Ok(state.rules.get_or_init(|| (crease, deflection)).clone())
}

/// `path.write_text(text)` as the runtime's `Path` does it: the build records the write.
fn write_text(path: &Path, text: &str) -> Result<()> {
    std::fs::write(path, text)?;
    hsm_documents::interop::note_io(path, true);
    Ok(())
}

/// `path.with_suffix(suffix)` as the runtime's `Path` computes it.
fn with_suffix(path: &Path, suffix: &str) -> PathBuf {
    let mut p = path.to_owned();
    p.set_extension(suffix.trim_start_matches('.'));
    p
}

/// `path.name`.
fn name(path: &Path) -> String {
    path.file_name().map(|v| v.to_string_lossy().to_string()).unwrap_or_default()
}

/// Draw the printed STL without changing it or its fine physical model.
///
/// ``check_print`` retains the quadrant writers' existing slicer refusal. The
/// relaxed retainer and setting jig use their existing unchecked path.
pub fn print_payload(rt: &Rt, step: &Path, options: &Options) -> Result<Val> {
    let state = rt.state::<State>(MODULE)?;
    let rust_part = rt.import("_rust_part")?;
    let (crease_deg, deflection_ratio) = rules(rt, &state)?;

    let step = py::resolve(step)?;
    let step_name = name(&step);
    let stl = match &options.stl {
        Some(stl) => py::resolve(stl)?,
        None => with_suffix(&step, ".stl"),
    };
    let numbers = py::dict([
        ("step_name", py::s(step_name.clone())),
        ("model", py::s(py::path_str(&step.with_file_name(step_name.clone() + ".npz")))),
        ("stl", py::s(py::path_str(&stl))),
        ("check_print", options.check_print.clone()),
        ("preserve_print_triangles", options.preserve_print_triangles.clone()),
        ("crease_deg", crease_deg),
        ("deflection_ratio", deflection_ratio),
    ]);
    if let Some(identity) = &options.identity {
        numbers.set(py::s("identity"), identity.clone())?;
    }
    if let Some(source) = &options.source {
        numbers.set(py::s("source"), py::s(py::path_str(&py::resolve(source)?)))?;
    }
    let temporary = py::call_kw(
        &rt.import("tempfile")?.attr("TemporaryDirectory")?,
        vec![],
        vec![("prefix", py::s("hsm-enclosure-presentation-"))],
    )?;
    let directory = py::method(&temporary, "__enter__", vec![])?;
    let body = (|| -> Result<Val> {
        let source = PathBuf::from(directory.str()?).join("enclosure-presentation.numbers.json");
        write_text(&source, &(py::json_dumps(&numbers, vec![("sort_keys", Val::Bool(true))])? + "\n"))?;
        let reply = py::method(&rust_part, "run", vec![
            py::s("enclosure-shell"),
            py::s("enclosure-presentation"),
            Val::Path(source),
            Val::Path(step.parent().unwrap_or(&step).to_owned()),
        ])?;
        py::json_loads(&reply.str()?)
    })();
    py::method(&temporary, "__exit__", vec![Val::None, Val::None, Val::None])?;
    let result = body?;

    let target = step.with_file_name(step_name + ".mesh");
    let add = rust_part.attr("_WRITE_TARGETS")?.attr("add")?;
    let relative = py::method(&rust_part, "_relative", vec![Val::Path(target.clone())])?;
    py::call(&add, vec![relative])?;
    if options.verbose {
        let field = |key: &str, spec: &str| -> Result<String> { num::fmtv(&py::at(&result, key)?, spec) };
        rt.print(format!(
            "-> {}  {} -> {} facets, {} mm inside a {} mm budget",
            name(&target),
            field("printed_triangles", "")?,
            field("drawing_triangles", "")?,
            field("deviation", ".3f")?,
            field("bound", ".3f")?,
        ))?;
    }
    Ok(result)
}
