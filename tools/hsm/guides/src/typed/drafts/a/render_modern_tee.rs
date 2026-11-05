//! `render_modern_tee`: the modern-home, all-push-connect cold-water installation sequence.
//! The plumbing data program supplies the dimensions, palette, registered views and scene
//! list; `_plumbing_art_mesh` exports the scenes, `_hsm_render` draws them.

use super::plumbing_art_mesh;
use super::*;

pub const NAME: &str = "render_modern_tee";

pub struct State {
    pub sys: Val,
    pub tempfile: Val,
    pub shutil: Val,
    /// `dataclasses.dataclass`.
    pub dataclass: Val,
    /// `pathlib.Path`, as the runtime constructs it.
    pub path: Val,
    pub here: PathBuf,
    pub hardware: PathBuf,
    pub root: PathBuf,
    pub art: PathBuf,
    pub hsm_render: Val,
    /// `jg_pp0408w`, the household union's reference model.
    pub union_ref: Val,
    /// The stub's `View` dataclass.
    pub view: Val,
    /// `_rust_data.request`.
    pub data_request: Val,
    /// `_plumbing_values`: the datums as the data program returned them.
    pub plumbing_values: Val,
    /// The last `(_name, _value)` the binding loop left at module level.
    pub last: Option<(Val, Val)>,
    /// The names the datums bind at module level, each `*_VIEW` as a `View`.
    pub bound: OMap<Val>,
    /// `SCENES`: each scene name with its `View`.
    pub scenes: Vec<(String, Val)>,
}
impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let sys = rt.import_module("sys")?;
        let tempfile = rt.import_module("tempfile")?;
        let shutil = rt.import_module("shutil")?;
        rt.import_module("dataclasses")?;
        let dataclass = member(rt, "dataclasses", "dataclass")?;
        let path = rt.import_module("pathlib")?.a("Path")?;
        let resolved = resolve(&rt.file(NAME));
        let here = resolved.parent().unwrap_or(&resolved).to_owned();
        let hardware = ancestor(&here, "hardware")?;
        let root = hardware.parent().unwrap_or(&hardware).to_owned();
        let art = here.join("art");
        rt.sys_path_insert(0, &hardware.join("scripts"))?;
        rt.sys_path_insert(0, &hardware.join("install-guide"))?;
        rt.sys_path_insert(0, &hardware.join("reference").join("jg-pp0408w"))?;
        plumbing_art_mesh::state(rt)?;
        let hsm_render = rt.import_module("_hsm_render")?;
        let union_ref = rt.import_module("jg_pp0408w")?;
        let view = rt.python_type(NAME, "View")?;
        rt.import_module("_rust_data")?;
        let data_request = member(rt, "_rust_data", "request")?;
        let plumbing_values = request(&data_request, &union_ref, &root, "datums", vec![])?;
        let make_view = |value: &Val| -> Result<Val> {
            view.c(vec![
                Val::Tuple(value.k("camera")?.iter()?),
                Val::Tuple(value.k("target")?.iter()?),
                value.k("span")?,
            ])
        };
        let mut last = None;
        let mut bound = OMap::new();
        for (name, value) in plumbing_values.items()? {
            last = Some((name.clone(), value.clone()));
            let key = name.str()?;
            if key.ends_with("_VIEW") {
                bound.set(&key, make_view(&value)?);
            } else if key != "SCENES" {
                bound.set(&key, value);
            }
        }
        let mut scenes = vec![];
        for row in plumbing_values.k("SCENES")?.iter()? {
            let pair = row.iter()?;
            ensure!(pair.len() == 2, "unpack: expected 2, got {}", pair.len());
            scenes.push((pair[0].str()?, make_view(&pair[1])?));
        }
        Ok(Self {
            sys,
            tempfile,
            shutil,
            dataclass,
            path,
            here,
            hardware,
            root,
            art,
            hsm_render,
            union_ref,
            view,
            data_request,
            plumbing_values,
            last,
            bound,
            scenes,
        })
    }
}
pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `from module import name`: the module's attribute, else the submodule `module.name`.
fn member(rt: &Runtime, module: &str, name: &str) -> Result<Val> {
    rt.import_module(module)?
        .attr(name)
        .or_else(|_| rt.import_module(&format!("{module}.{name}")))
}

/// `_data_request("faucet-data", "faucet-data", {"op": "plumbing", "fn": fn, "root": ...,
/// "modern": True, **values})`; the datums request also carries the union's reach and
/// insertion depth.
fn request(
    data_request: &Val,
    union_ref: &Val,
    root: &Path,
    function: &str,
    mut values: Vec<(String, Val)>,
) -> Result<Val> {
    if function == "datums" {
        let reach = union_ref.m("reach", vec![])?;
        let insertion = union_ref.a("INSERTION")?;
        for (key, value) in [("union_reach", reach), ("union_insertion", insertion)] {
            match values.iter_mut().find(|(k, _)| k == key) {
                Some(row) => row.1 = value,
                None => values.push((key.into(), value)),
            }
        }
    }
    let spec = Val::dict(vec![]);
    spec.set("op".into(), "plumbing".into())?;
    spec.set("fn".into(), function.into())?;
    spec.set("root".into(), Val::Str(ps(root)))?;
    spec.set("modern".into(), Val::Bool(true))?;
    for (key, value) in values {
        spec.set(Val::Str(key), value)?;
    }
    data_request.c(vec!["faucet-data".into(), "faucet-data".into(), spec])
}

/// `_plumbing_data(fn="datums", **values)`: one modern plumbing request.
pub fn plumbing_data(rt: &Runtime, function: &str, values: Vec<(String, Val)>) -> Result<Val> {
    let st = state(rt)?;
    request(&st.data_request, &st.union_ref, &st.root, function, values)
}

/// `_canonicalize_png(path)`.
pub fn canonicalize_png(rt: &Runtime, path: &Val) -> Result<()> {
    plumbing_data(rt, "canonicalize-png", vec![("path".into(), Val::Str(path.str()?))])?;
    Ok(())
}

/// `_job(step, output, view)`: the `_hsm_render` job for one scene.
pub fn job(rt: &Runtime, step: &Val, output: &Val, view: &Val) -> Result<Val> {
    let vars = hsm_documents::interop::builtin("vars").context("vars builtin")?;
    let step = Val::Str(step.str()?);
    let output = Val::Str(output.str()?);
    let view = vars.c(vec![view.clone()])?;
    plumbing_data(
        rt,
        "job",
        vec![
            ("step".into(), step),
            ("output".into(), output),
            ("view".into(), view),
        ],
    )
}

/// `main()`: export the scenes into a temporary directory (the opening scene's STEP into the
/// shared `out/`), render every picture and canonicalize it.
pub fn run(rt: &Runtime) -> Result<()> {
    let st = state(rt)?;
    std::fs::create_dir_all(&st.art)?;
    let shared = st.here.join("out");
    std::fs::create_dir_all(&shared)?;
    let mut outputs = vec![];
    let context = st.tempfile.mk(
        "TemporaryDirectory",
        vec![],
        kw!["prefix" => ".modern-pushfit-", "dir" => st.here.clone()],
    )?;
    with(&context, |directory| {
        let work = PathBuf::from(directory.str()?);
        plumbing_art_mesh::state(rt)?;
        let names: Vec<String> = st.scenes.iter().map(|(name, _)| name.clone()).collect();
        let module = rt.import_module(NAME)?;
        let steps = plumbing_art_mesh::export(rt, &module, &names, &work, true)?;
        let mut jobs = vec![];
        for (name, view) in &st.scenes {
            let base = if name == "modern-water-on" {
                &shared
            } else {
                &work
            };
            let step = base.join(format!("{name}.step"));
            let output = st.art.join(format!("{name}.png"));
            if name == "modern-water-on" {
                let copied = plumbing_data(
                    rt,
                    "copy-step",
                    vec![
                        ("source".into(), Val::Str(ps(steps.at(name)?))),
                        ("target".into(), Val::Str(ps(&step))),
                    ],
                )?;
                for target in copied.iter()? {
                    plumbing_art_mesh::note_write(
                        rt,
                        &Val::Path(PathBuf::from(target.str()?)),
                    )?;
                }
            }
            jobs.push(job(rt, &Val::Path(step), &Val::Path(output.clone()), view)?);
            outputs.push(output);
        }
        st.hsm_render.m("render", vec![Val::list(jobs)])?;
        for output in &outputs {
            let output = Val::Path(output.clone());
            canonicalize_png(rt, &output)?;
            plumbing_art_mesh::note_write(rt, &output)?;
        }
        Ok(())
    })?;
    rt.print("modern push-connect installation art:")?;
    for output in &outputs {
        rt.print(format!("  {}", ps(output)))?;
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
    ns.value("sys", st.sys.clone());
    ns.value("tempfile", st.tempfile.clone());
    ns.value("shutil", st.shutil.clone());
    ns.value("dataclass", st.dataclass.clone());
    ns.value("Path", st.path.clone());
    ns.value("HERE", st.here.clone());
    ns.value("HARDWARE", st.hardware.clone());
    ns.value("ROOT", st.root.clone());
    ns.value("ART", st.art.clone());
    ns.value(
        "note_write",
        rt.import_module(plumbing_art_mesh::NAME)?.a("note_write")?,
    );
    ns.value("_hsm_render", st.hsm_render.clone());
    ns.value("union_ref", st.union_ref.clone());
    ns.value("View", st.view.clone());
    ns.value("_data_request", st.data_request.clone());
    let runtime = rt.clone();
    ns.value(
        "_plumbing_data",
        Val::function(move |args, kwargs| {
            let (function, values) = bind_data(args, kwargs)?;
            plumbing_data(&runtime, &function, values)
        }),
    );
    ns.value("_plumbing_values", st.plumbing_values.clone());
    if let Some((name, value)) = &st.last {
        ns.value("_name", name.clone());
        ns.value("_value", value.clone());
    }
    for (name, value) in st.bound.iter() {
        ns.value(name, value.clone());
    }
    ns.value(
        "SCENES",
        Val::Tuple(
            st.scenes
                .iter()
                .map(|(name, view)| Val::Tuple(vec![Val::Str(name.clone()), view.clone()]))
                .collect(),
        ),
    );
    ns.func(rt, "_canonicalize_png", |rt, c| {
        canonicalize_png(rt, &c.req::<Val>(0, "path")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "_job", |rt, c| {
        let step: Val = c.req(0, "step")?;
        let output: Val = c.req(1, "output")?;
        let view: Val = c.req(2, "view")?;
        job(rt, &step, &output, &view)
    });
    ns.func(rt, "main", |rt, _| {
        run(rt)?;
        Ok(Val::None)
    });
    Ok(())
}

/// The `__main__` block.
pub fn main(rt: &Runtime) -> Result<()> {
    rt.sys_path_insert(0, &parent_n(&resolve(&rt.file(NAME)), 3).join("scripts"))?;
    rt.import_module("_rust_part")?.m("start", vec![])?;
    run(rt)
}
