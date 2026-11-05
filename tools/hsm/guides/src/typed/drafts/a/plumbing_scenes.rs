//! `plumbing_scenes`: the registered under-sink cold-water hookup scenes for the Install
//! guide. The plumbing data program supplies the scene dimensions, palette and render frame;
//! `_plumbing_art_mesh` exports the four scenes and `_hsm_render` draws them.

use super::plumbing_art_mesh;
use super::*;

pub const NAME: &str = "plumbing_scenes";

pub struct State {
    pub argparse: Val,
    pub sys: Val,
    /// `pathlib.Path`, as the runtime constructs it.
    pub path: Val,
    pub here: PathBuf,
    pub hardware: PathBuf,
    pub root: PathBuf,
    pub out: PathBuf,
    pub art: PathBuf,
    pub hsm_render: Val,
    /// `_rust_data.request`.
    pub data_request: Val,
    /// The plumbing datums the module binds at its top level, in the data program's order,
    /// with `SCENE_NAMES` as a tuple.
    pub datums: OMap<Val>,
    pub scene_names: Vec<String>,
}
impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let argparse = rt.import_module("argparse")?;
        let sys = rt.import_module("sys")?;
        let path = rt.import_module("pathlib")?.a("Path")?;
        let resolved = resolve(&rt.file(NAME));
        let here = resolved.parent().unwrap_or(&resolved).to_owned();
        let hardware = ancestor(&here, "hardware")?;
        let root = hardware.parent().unwrap_or(&hardware).to_owned();
        let out = here.join("out");
        let art = here.join("art");
        rt.sys_path_insert(0, &hardware.join("scripts"))?;
        rt.sys_path_insert(0, &hardware.join("install-guide"))?;
        let hsm_render = rt.import_module("_hsm_render")?;
        rt.import_module("_rust_data")?;
        let data_request = rt
            .import_module("_rust_data")?
            .attr("request")
            .or_else(|_| rt.import_module("_rust_data.request"))?;
        let found = request(&data_request, &root, "datums", vec![])?;
        let mut datums = OMap::new();
        for (name, value) in found.items()? {
            datums.set(&name.str()?, value);
        }
        let names = datums.at("SCENE_NAMES")?.iter()?;
        datums.set("SCENE_NAMES", Val::Tuple(names.clone()));
        let scene_names = names.iter().map(Val::str).collect::<Result<_>>()?;
        Ok(Self {
            argparse,
            sys,
            path,
            here,
            hardware,
            root,
            out,
            art,
            hsm_render,
            data_request,
            datums,
            scene_names,
        })
    }
}
pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `_data_request("faucet-data", "faucet-data", {"op": "plumbing", "fn": fn, "root": ...,
/// "modern": False, **values})`.
fn request(data_request: &Val, root: &Path, function: &str, values: Vec<(String, Val)>) -> Result<Val> {
    let spec = Val::dict(vec![]);
    spec.set("op".into(), "plumbing".into())?;
    spec.set("fn".into(), function.into())?;
    spec.set("root".into(), Val::Str(ps(root)))?;
    spec.set("modern".into(), Val::Bool(false))?;
    for (key, value) in values {
        spec.set(Val::Str(key), value)?;
    }
    data_request.c(vec!["faucet-data".into(), "faucet-data".into(), spec])
}

/// `_plumbing_data(fn="datums", **values)`: one legacy plumbing request.
pub fn plumbing_data(rt: &Runtime, function: &str, values: Vec<(String, Val)>) -> Result<Val> {
    let st = state(rt)?;
    request(&st.data_request, &st.root, function, values)
}

/// `_render(step_paths, art_dir)`: the scenes' render jobs, rendered, then each picture
/// canonicalized.
pub fn render(rt: &Runtime, step_paths: &OMap<PathBuf>, art_dir: &Path) -> Result<()> {
    let st = state(rt)?;
    let mut steps = Dict::new();
    for (name, path) in step_paths.iter() {
        steps.set(name, ps(path));
    }
    let jobs = plumbing_data(
        rt,
        "legacy-jobs",
        vec![
            ("steps".into(), steps.val()),
            ("directory".into(), Val::Str(ps(art_dir))),
        ],
    )?;
    st.hsm_render.m("render", vec![jobs.clone()])?;
    for row in jobs.iter()? {
        plumbing_data(rt, "canonicalize-png", vec![("path".into(), row.k("out")?)])?;
    }
    Ok(())
}

/// `main()`: export the four scenes, then (by default) render them.
pub fn run(rt: &Runtime) -> Result<()> {
    let st = state(rt)?;
    let module = rt.import_module(NAME)?;
    let parser = st
        .argparse
        .a("ArgumentParser")?
        .ck(vec![], kw!["description" => module.a("__doc__")?])?;
    let relative = |path: &Path| -> Result<String> {
        Ok(ps(path.strip_prefix(&st.root).with_context(|| {
            format!("ValueError: {} is not in the subpath of {}", ps(path), ps(&st.root))
        })?))
    };
    parser.mk(
        "add_argument",
        args!["--out-dir"],
        kw![
            "type" => st.path.clone(),
            "default" => st.out.clone(),
            "help" => format!("STEP/PNG output directory (default: {})", relative(&st.out)?),
        ],
    )?;
    parser.mk(
        "add_argument",
        args!["--render"],
        kw![
            "dest" => "render",
            "action" => "store_true",
            "help" => "render the four registered 2000x1100 instruction PNGs (the default)",
        ],
    )?;
    parser.mk(
        "add_argument",
        args!["--steps-only"],
        kw![
            "dest" => "render",
            "action" => "store_false",
            "help" => "export only the STEP and mesh intermediates",
        ],
    )?;
    parser.mk(
        "add_argument",
        args!["--art-dir"],
        kw![
            "type" => st.path.clone(),
            "default" => st.art.clone(),
            "help" => format!("PNG output directory (default: {})", relative(&st.art)?),
        ],
    )?;
    parser.mk("set_defaults", vec![], kw!["render" => true])?;
    let args = parser.m("parse_args", vec![])?;
    let output_dir = args.a("out_dir")?.m("resolve", vec![])?;
    output_dir.mk("mkdir", vec![], kw!["parents" => true, "exist_ok" => true])?;
    plumbing_art_mesh::state(rt)?;
    let step_paths = plumbing_art_mesh::export(
        rt,
        &module,
        &st.scene_names,
        &PathBuf::from_val(&output_dir)?,
        false,
    )?;
    if args.a("render")?.truthy()? {
        let art_dir = args.a("art_dir")?.m("resolve", vec![])?;
        art_dir.mk("mkdir", vec![], kw!["parents" => true, "exist_ok" => true])?;
        let art_dir = PathBuf::from_val(&art_dir)?;
        render(rt, &step_paths, &art_dir)?;
        for name in &st.scene_names {
            rt.print(format!(
                "rendered -> {}",
                ps(&art_dir.join(format!("{name}.png")))
            ))?;
        }
    }
    Ok(())
}

/// `_plumbing_data`'s signature, `(fn="datums", **values)`.
fn bind_data(args: Vec<Val>, mut kwargs: Vec<(String, Val)>) -> Result<(String, Vec<(String, Val)>)> {
    let keyword = kwargs
        .iter()
        .position(|(k, _)| k == "fn")
        .map(|i| kwargs.remove(i).1);
    let mut args = args.into_iter();
    let function = match (args.next(), keyword) {
        (Some(_), Some(_)) => bail!("multiple arguments for fn"),
        (Some(v), None) | (None, Some(v)) => v,
        (None, None) => Val::Str("datums".into()),
    };
    ensure!(args.next().is_none(), "too many positional arguments");
    Ok((String::from_val(&function)?, kwargs))
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let st = state(rt)?;
    ns.value("argparse", st.argparse.clone());
    ns.value("sys", st.sys.clone());
    ns.value("Path", st.path.clone());
    ns.value("HERE", st.here.clone());
    ns.value("HARDWARE", st.hardware.clone());
    ns.value("ROOT", st.root.clone());
    ns.value("OUT", st.out.clone());
    ns.value("ART", st.art.clone());
    ns.value("_hsm_render", st.hsm_render.clone());
    ns.value("_data_request", st.data_request.clone());
    let runtime = rt.clone();
    ns.value(
        "_plumbing_data",
        Val::function(move |args, kwargs| {
            let (function, values) = bind_data(args, kwargs)?;
            plumbing_data(&runtime, &function, values)
        }),
    );
    for (name, value) in st.datums.iter() {
        ns.value(name, value.clone());
    }
    ns.func(rt, "_render", |rt, c| {
        let step_paths: Val = c.req(0, "step_paths")?;
        let art_dir: PathBuf = c.req(1, "art_dir")?;
        let mut paths = OMap::new();
        for (name, path) in step_paths.items()? {
            paths.set(&name.str()?, PathBuf::from_val(&path)?);
        }
        render(rt, &paths, &art_dir)?;
        Ok(Val::None)
    });
    ns.func(rt, "main", |rt, _| {
        run(rt)?;
        Ok(Val::None)
    });
    Ok(())
}

/// The `__main__` block.
pub fn main(rt: &Runtime) -> Result<()> {
    rt.sys_path_insert(0, &parent_n(&resolve(&rt.file(NAME)), 2).join("scripts"))?;
    rt.import_module("_rust_part")?.m("start", vec![])?;
    run(rt)
}
