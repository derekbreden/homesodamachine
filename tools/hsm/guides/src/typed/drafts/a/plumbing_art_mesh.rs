//! `_plumbing_art_mesh`: the under-sink instruction scenes as Rust-kernel illustration
//! geometry. The caller's plain module values (its named states and palette) go to the
//! plumbing spec, and the props job writes each scene's STEP payload into the directory.

use super::*;

pub const NAME: &str = "_plumbing_art_mesh";

pub struct State {
    pub json: Val,
    /// `pathlib.Path`, as the runtime constructs it.
    pub path: Val,
    pub tempfile: Val,
    pub rust_part: Val,
}
impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let json = rt.import_module("json")?;
        let path = rt.import_module("pathlib")?.a("Path")?;
        let tempfile = rt.import_module("tempfile")?;
        let rust_part = rt.import_module("_rust_part")?;
        Ok(Self {
            json,
            path,
            tempfile,
            rust_part,
        })
    }
}
pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `_rust_part.<targets>.add(_rust_part._relative(Path(path)))`.
fn note(st: &State, targets: &str, path: &Val) -> Result<()> {
    let add = st.rust_part.a(targets)?.a("add")?;
    let relative = st
        .rust_part
        .a("_relative")?
        .c(vec![Val::Path(PathBuf::from(path.str()?))])?;
    add.c(vec![relative])?;
    Ok(())
}

/// `note_read(path)`: an input supplied to the Rust geometry program, recorded when it lies
/// under the build root (every failure is passed over).
pub fn note_read(rt: &Runtime, path: &Val) -> Result<()> {
    let st = state(rt)?;
    let _ = note(&st, "_READ_TARGETS", path);
    Ok(())
}

/// `note_write(path)`: an output a child geometry or rendering program emitted, recorded the
/// same way.
pub fn note_write(rt: &Runtime, path: &Val) -> Result<()> {
    let st = state(rt)?;
    let _ = note(&st, "_WRITE_TARGETS", path);
    Ok(())
}

/// `_plain(value)`: a string, number, bool or None, or a tuple or list of plain values.
pub fn plain(value: &Val) -> bool {
    match value {
        Val::Str(_) | Val::Int(_) | Val::Float(_) | Val::Bool(_) | Val::None => true,
        Val::Tuple(items) => items.iter().all(plain),
        Val::List(items) => items.borrow().iter().all(plain),
        _ => false,
    }
}

/// `vars(module).items()`.
fn module_items(module: &Val) -> Result<Vec<(Val, Val)>> {
    let vars = hsm_documents::interop::builtin("vars").context("vars builtin")?;
    let mut out = vec![];
    for item in vars.c(vec![module.clone()])?.m("items", vec![])?.iter()? {
        let pair = item.iter()?;
        ensure!(pair.len() == 2, "unpack: expected 2, got {}", pair.len());
        out.push((pair[0].clone(), pair[1].clone()));
    }
    Ok(out)
}

/// `export(module, names, directory, *, modern=False)`: the caller's named scenes as STEP
/// payloads in `directory`, keyed by scene name.
pub fn export(
    rt: &Runtime,
    module: &Val,
    names: &[String],
    directory: &Path,
    modern: bool,
) -> Result<OMap<PathBuf>> {
    let st = state(rt)?;
    rt.import_module("_rust_data")?;
    let request = rt
        .import_module("_rust_data")?
        .attr("request")
        .or_else(|_| rt.import_module("_rust_data.request"))?;
    let values = Val::dict(vec![]);
    for (name, value) in module_items(module)? {
        if plain(&value) {
            values.set(name, value)?;
        }
    }
    let source = Val::dict(vec![]);
    source.set("op".into(), "plumbing".into())?;
    source.set("fn".into(), "spec".into())?;
    source.set("modern".into(), Val::Bool(modern))?;
    source.set(
        "names".into(),
        Val::list(names.iter().map(|n| Val::Str(n.clone())).collect()),
    )?;
    source.set("facts".into(), values)?;
    if modern {
        let union = module.a("union_ref")?;
        note_read(rt, &union.a("PAYLOAD_PATH")?)?;
        let payload = union
            .a("PAYLOAD_PATH")?
            .m("relative_to", vec![module.a("ROOT")?])?
            .str()?;
        let spec = Dict::new()
            .with("payload", payload)
            .with("ring_start", union.a("ring_face_z")?)
            .with("ring_end", union.a("port_face_z")?)
            .with("collet_d", union.a("COLLET_D")?)
            .with("collet_bore", union.a("COLLET_BORE")?);
        source.set("union".into(), spec.val())?;
    }
    std::fs::create_dir_all(directory)?;
    let context = st.tempfile.mk(
        "TemporaryDirectory",
        vec![],
        kw!["prefix" => ".plumbing-props-", "dir" => module.a("HERE")?],
    )?;
    with(&context, |temporary| {
        let path = PathBuf::from(temporary.str()?).join("numbers.json");
        let spec = Val::dict(vec![]);
        for (key, value) in source.items()? {
            spec.set(key, value)?;
        }
        spec.set("output".into(), Val::Str(ps(&path)))?;
        request.c(vec!["faucet-data".into(), "faucet-data".into(), spec])?;
        let printed = st.rust_part.m(
            "run",
            args!["tooling", "install-art-props", path, directory.to_path_buf()],
        )?;
        for line in printed.m("splitlines", vec![])?.iter()? {
            if line.m("strip", vec![])?.truthy()? {
                for name in json_loads(&line.str()?)?.k("files")?.iter()? {
                    note_write(rt, &Val::Path(directory.join(name.str()?)))?;
                }
            }
        }
        Ok(())
    })?;
    let mut out = OMap::new();
    for name in names {
        out.set(name, directory.join(format!("{name}.step")));
    }
    Ok(out)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let st = state(rt)?;
    ns.value("json", st.json.clone());
    ns.value("Path", st.path.clone());
    ns.value("tempfile", st.tempfile.clone());
    ns.value("_rust_part", st.rust_part.clone());
    ns.func(rt, "note_read", |rt, c| {
        note_read(rt, &c.req::<Val>(0, "path")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "note_write", |rt, c| {
        note_write(rt, &c.req::<Val>(0, "path")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "_plain", |_, c| Ok(Val::Bool(plain(&c.req::<Val>(0, "value")?))));
    ns.func(rt, "export", |rt, c| {
        let module: Val = c.req(0, "module")?;
        let names: Vec<String> = c.req(1, "names")?;
        let directory: PathBuf = c.req(2, "directory")?;
        let modern: bool = c.kw("modern", false)?;
        Ok(export(rt, &module, &names, &directory, modern)?.to_val())
    });
    Ok(())
}

pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
