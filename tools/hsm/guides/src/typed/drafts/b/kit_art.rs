//! Guide recipe `kit_art`: the supplied kit drawn as consistent vector hidden-line views.

use super::install_art;
use super::*;
use std::path::{Path, PathBuf};
use std::rc::Rc;

pub const NAME: &str = "kit_art";

pub const CAMERA: [Num; 3] = [Num::F(0.8), Num::I(-1), Num::F(0.7)];
/// Each drawing and the direction it is seen from.
pub const VIEWS: [(&str, [Num; 3]); 9] = [
    ("machine", CAMERA),
    ("faucet-and-plate", [Num::F(0.95), Num::I(-1), Num::F(0.55)]),
    ("filtered-line", CAMERA),
    ("water-tees", [Num::F(0.6), Num::I(-1), Num::F(0.65)]),
    ("regulator-and-tether", [Num::F(0.15), Num::I(1), Num::F(0.3)]),
    ("collet-press", [Num::F(-0.5), Num::F(-0.9), Num::F(0.85)]),
    ("power-cord", CAMERA),
    ("install-guide", CAMERA),
    ("cold-kit", CAMERA),
];

pub struct State {
    pub sys: Val,
    pub root: PathBuf,
    pub hardware: PathBuf,
    pub art: PathBuf,
    pub rust_part: Val,
    pub model_outlines: Val,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let sys = rt.py("sys")?;
        let root = parent_n(&resolve(&rt.file(NAME)), 2);
        let hardware = root.join("hardware");
        let art = hardware.join("install-guide/assets/kit");
        sys.a("path")?.set(
            Val::Slice {
                start: None,
                stop: Some(0),
                step: 1,
            },
            Val::list(vec![
                Val::Str(ps(&hardware.join("scripts"))),
                Val::Str(ps(&hardware.join("install-guide"))),
                Val::Str(ps(&hardware.join("printed-parts/enclosure/enclosure"))),
            ]),
        )?;
        let rust_part = rt.py("_rust_part")?;
        rt.py("_mesh_projection")?;
        let model_outlines = rt.pya("_mesh_projection", "model_outlines")?;
        Ok(State {
            sys,
            root,
            hardware,
            art,
            rust_part,
            model_outlines,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

fn posix(path: &Path, root: &Path) -> Result<String> {
    Ok(ps(path.strip_prefix(root).with_context(|| {
        format!("ValueError: {} is not under {}", path.display(), root.display())
    })?))
}

/// `models(work)`: the kit's meshes cut by `install-art-props` into `work`, one per view.
pub fn models(rt: &Runtime, work: &Path) -> Result<Val> {
    let st = state(rt)?;
    rt.import_module(install_art::NAME)?;
    let shared = install_art::state(rt)?;
    let swept_top = rt.py("_swept_top")?;
    let facts_path = PathBuf::from_val(&shared.machine_facts)?;
    let facts = json_loads(&read_text(&facts_path)?)?;
    let faucet = shared.cad_art.m("_load_faucet_module", vec![])?; // via namespace: _cad_art
    let regulator = install_art::load_regulator(rt)?;
    let inputs: Vec<(&str, PathBuf)> = vec![
        ("faucet", st.hardware.join("faucet-layout/faucet-assembly.step.npz")),
        (
            "collet",
            st.hardware
                .join("printed-parts/collet-press/collet-press.step.npz"),
        ),
        (
            "black_tee",
            st.hardware
                .join("reference/jg-pp0208e-tee/jg-pp0208e-tee.step.mesh"),
        ),
        (
            "regulator",
            shared.regulator_dir.join("taprite-3741-regulator.step.mesh"),
        ),
        (
            "white_tee",
            shared.plumbing_dir.join("out/plumbing-pre-tee.step.npz"),
        ),
    ];
    let mut traced = vec![facts_path.clone()];
    traced.extend(inputs.iter().map(|(_, path)| path.clone()));
    for path in &traced {
        st.rust_part
            .a("_READ_TARGETS")?
            .m("add", args![posix(path, &st.root)?])?;
    }
    let mut relative = Dict::new();
    for (name, path) in &inputs {
        relative.set(*name, posix(path, &st.root)?);
    }
    let outer = facts.k("box")?.k("outer")?;
    let machine = dict![
        "outer" => outer.clone(),
        "profile" => swept_top.m("profile", vec![outer])?,
        "cover" => facts.k("bodies")?.k("funnel-cover")?,
    ];
    let mut lever = vec![];
    for name in [
        "plateau_z",
        "port_center_depth",
        "soda_faucet_tube_r",
        "lever_pivot_y",
        "lever_pivot_z",
        "lever_press_angle_deg",
    ] {
        lever.push(faucet.a(name)?);
    }
    let held = dict![
        "mouth" => regulator.m("outlet", vec![])?.i(0)?,
        "insert" => install_art::TETHER_IN_MOUTH,
    ];
    let kit = dict![
        "inputs" => relative.val(),
        "machine" => machine,
        "lever" => Val::list(lever),
        "regulator" => held,
    ];
    let mut colors = Dict::new();
    for name in ["FILTER_BODY", "FILTER_CAP", "WHITE_TUBE", "RED_TUBE"] {
        colors.set(name, Val::list(vec![Val::Float(0.0); 3]));
    }
    let numbers = dict![
        "kit_art" => kit,
        "filter" => Val::list(vec![
            Val::Float(install_art::FILTER_D),
            Val::Float(install_art::FILTER_L),
        ]),
        "tube_d" => install_art::TUBE_D,
        "colors" => colors.val(),
    ];
    install_art::mkdirs(work)?;
    let path = work.join("kit-art.numbers.json");
    write_text(
        &path,
        &(json_dumps(&numbers, kw!["sort_keys" => true])? + "\n"),
    )?;
    st.rust_part.m(
        "run",
        args!["tooling", "install-art-props", path, work.to_path_buf()],
    )?;
    let mut shown = Dict::new();
    for (name, _) in VIEWS {
        shown.set(name, work.join(format!("{name}.kit.npz")));
    }
    Ok(shown.val())
}

/// `line_svg(model, camera)`: the model's visible outlines from `camera`, fitted to 600 x 450.
pub fn line_svg(rt: &Runtime, model: &Val, camera: &Val) -> Result<String> {
    let st = state(rt)?;
    let view = <[Num; 3]>::from_val(camera)?;
    let right = (view[1].neg(), view[0], 0.0);
    let points = st
        .model_outlines
        .c(vec![model.clone(), camera.clone(), right.to_val()])?;
    let mut edges: Vec<Vec<(f64, f64)>> = vec![];
    for edge in own(&points)?.iter()? {
        let mut line = vec![];
        for p in edge.list()? {
            let xy = p.list()?;
            ensure!(xy.len() == 2, "ValueError: a point unpacks to two values");
            line.push((xy[0].f()?, xy[1].f()?));
        }
        edges.push(line);
    }
    let flat: Vec<(f64, f64)> = edges.iter().flatten().copied().collect();
    ensure!(!flat.is_empty(), "ValueError: min() iterable argument is empty");
    let left = fmin(flat.iter().map(|p| p.0));
    let right = fmax(flat.iter().map(|p| p.0));
    let bottom = fmin(flat.iter().map(|p| p.1));
    let top = fmax(flat.iter().map(|p| p.1));
    let scale = pmin(564.0 / (right - left), 414.0 / (top - bottom));
    let ox = (600.0 - (right - left) * scale) / 2.0;
    let oy = (450.0 - (top - bottom) * scale) / 2.0;
    let mut body = vec![];
    for edge in &edges {
        let path = edge
            .iter()
            .enumerate()
            .map(|(i, (x, y))| {
                format!(
                    "{}{},{}",
                    if i == 0 { "M" } else { "L" },
                    ff(ox + (x - left) * scale, ".4f"),
                    ff(oy + (top - y) * scale, ".4f")
                )
            })
            .collect::<Vec<_>>()
            .join(" ");
        if !path.is_empty() {
            body.push(format!("<path d=\"{path}\"/>"));
        }
    }
    Ok(format!(
        "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"600\" height=\"450\" viewBox=\"0 0 600 450\">\n<g fill=\"none\" stroke=\"#46515b\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">\n{}\n</g>\n</svg>\n",
        body.join("\n")
    ))
}

/// `main()`: every view of the kit, drawn into `assets/kit`.
pub fn draw(rt: &Runtime) -> Result<()> {
    let st = state(rt)?;
    install_art::mkdirs(&st.art)?;
    let shown = models(rt, &st.root.join(".cache/install-guide-kit"))?;
    for (name, camera) in VIEWS {
        rt.pya("builtins", "print")?
            .ck(args!["Drawing", name], kw!["flush" => true])?;
        let svg = line_svg(rt, &shown.get(Val::Str(name.into()))?, &camera.to_val())?;
        write_text(&st.art.join(format!("{name}.svg")), &svg)?;
    }
    rt.print(format!(
        "{} kit drawings written to {}",
        VIEWS.len(),
        posix(&st.art, &st.root)?
    ))?;
    Ok(())
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let st = state(rt)?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.module(rt, "json", "json")?;
    ns.value("sys", st.sys.clone());
    ns.value("ROOT", st.root.clone());
    ns.value("HARDWARE", st.hardware.clone());
    ns.value("ART", st.art.clone());
    ns.value("_rust_part", st.rust_part.clone());
    ns.value("model_outlines", st.model_outlines.clone());
    ns.value("CAMERA", CAMERA);
    ns.value(
        "VIEWS",
        Val::Tuple(
            VIEWS
                .iter()
                .map(|(name, camera)| (*name, *camera).to_val())
                .collect(),
        ),
    );
    ns.func(rt, "models", |rt, c| {
        let work: PathBuf = c.req(0, "work")?;
        models(rt, &work)
    });
    ns.func(rt, "line_svg", |rt, c| {
        let model: Val = c.req(0, "model")?;
        let camera: Val = c.req(1, "camera")?;
        Ok(Val::Str(line_svg(rt, &model, &camera)?))
    });
    ns.func(rt, "main", |rt, _| {
        draw(rt)?;
        Ok(Val::None)
    });
    Ok(())
}

pub fn main(rt: &Runtime) -> Result<()> {
    let st = state(rt)?;
    st.rust_part.m("start", vec![])?;
    draw(rt)
}
