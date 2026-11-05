//! Guide recipe `opening_scene`: the current counter opening and its registered component
//! silhouette.

use super::install_art;
use super::*;
use std::path::{Path, PathBuf};
use std::rc::Rc;

pub const NAME: &str = "opening_scene";

pub struct State {
    pub os: Val,
    pub sys: Val,
    pub image: Val,
    pub root: PathBuf,
    pub hardware: PathBuf,
    pub out: PathBuf,
    pub assets: PathBuf,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let os = rt.py("os")?;
        let sys = rt.py("sys")?;
        let pil = rt.py("PIL")?;
        let image = match pil.a("Image") {
            Ok(image) => image,
            Err(_) => rt.py("PIL.Image")?,
        };
        let root = parent_n(&resolve(&rt.file(NAME)), 2);
        let hardware = root.join("hardware");
        let out = hardware.join("install-guide/out/opening");
        let assets = hardware.join("install-guide/assets");
        sys.a("path")?.set(
            Val::Slice {
                start: None,
                stop: Some(0),
                step: 1,
            },
            Val::list(vec![
                Val::Str(ps(&hardware.join("install-guide"))),
                Val::Str(ps(&hardware.join("scripts"))),
                Val::Str(ps(&root.join("tools"))),
            ]),
        )?;
        Ok(State {
            os,
            sys,
            image,
            root,
            hardware,
            out,
            assets,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `outlines(mask)`: the outer contours of a mask, as `_guide_native.outlines` traces them.
pub fn outlines(rt: &Runtime, mask: &Val) -> Result<Val> {
    rt.native("outlines")?.c(vec![mask.clone()])
}

/// `str(path.relative_to(base))`.
fn relative(path: &Path, base: &Path) -> Result<String> {
    Ok(ps(path.strip_prefix(base).with_context(|| {
        format!(
            "ValueError: {} is not in the subpath of {}",
            path.display(),
            base.display()
        )
    })?))
}

/// `hashlib.sha256(path.read_bytes()).hexdigest()`.
fn sha256(path: &Path) -> Result<Val> {
    hsm_documents::interop::note_io(path, false);
    let bytes = std::fs::read(path).with_context(|| format!("read {}", path.display()))?;
    hsm_documents::interop::builtin_module("hashlib")
        .context("hashlib module")?
        .m("sha256", vec![Val::Bytes(bytes)])?
        .m("hexdigest", vec![])
}

/// `main()`: render the opening scene and its components, crop both to the scene's alpha,
/// trace the component silhouette and register the artwork.
pub fn main(rt: &Runtime) -> Result<()> {
    let st = state(rt)?;
    let rust_part = rt.py("_rust_part")?;
    rust_part.m("start", vec![])?;
    let note_rewritten = rt.docgen_member("note_rewritten", Some(NAME))?;
    let hsm_render = rt.py("_hsm_render")?;
    let install = rt.import_module(install_art::NAME)?;
    let mesh_payload = rt.py("_mesh_payload")?;
    let art_mesh = rt.import_module("_install_art_mesh")?; // via namespace: _install_art_mesh
    let payloads = art_mesh.a("payloads")?; // via namespace: _install_art_mesh
    let read = art_mesh.a("_read")?; // via namespace: _install_art_mesh
    install_art::mkdirs(&st.out)?;
    install_art::mkdirs(&st.assets)?;
    let staged = payloads.c(vec![
        install,
        Val::list(vec![Val::Str("opening".into())]),
        Val::Path(st.out.clone()),
    ])?; // via namespace: _install_art_mesh
    let scene = read.c(vec![staged.k("opening")?])?; // via namespace: _install_art_mesh
    let mut component = vec![];
    for mesh in scene.iter()? {
        let name = mesh.k("name")?.s()?;
        if name.split('/').next() != Some("countertop") {
            component.push(mesh);
        }
    }
    let component = Val::list(component);
    let paths = [
        ("scene", st.out.join("opening.step")),
        ("components", st.out.join("components.step")),
    ];
    let mut scenes = vec![];
    for (name, meshes) in [("scene", &scene), ("components", &component)] {
        let source = st.out.join(format!("opening-{name}.mesh"));
        mesh_payload.m("write", vec![meshes.clone(), Val::Path(source.clone())])?;
        let path = &paths.iter().find(|(key, _)| *key == name).expect("path").1;
        let stem = path
            .file_stem()
            .map(|s| s.to_string_lossy().into_owned())
            .unwrap_or_default();
        scenes.push(dict!["name" => stem, "payload" => ps(&source)]);
    }
    let numbers = st.out.join("opening-export.numbers.json");
    write_text(
        &numbers,
        &(json_dumps(
            &dict!["surface_scenes" => Val::list(scenes)],
            kw!["sort_keys" => true],
        )? + "\n"),
    )?;
    rust_part.m(
        "run",
        args!["tooling", "install-art-props", numbers, st.out.clone()],
    )?;
    let mut jobs = vec![];
    for (name, path) in &paths {
        let job = Dict::new()
            .with("cam", (0.42, -0.8, 0.95))
            .with("target", (0.0, 0.0, 24.0))
            .with("span", 120.0)
            .with("size", "3800x3200")
            .with("up", (0, 0, 1))
            .with("bg", "#f2eee8")
            .with("transparent", true)
            .with("solid", true)
            .with("ortho", true)
            .with("trim", false)
            .with("ground", false)
            .with("fog", false)
            .with("step", relative(path, &st.hardware)?)
            .with("out", ps(&st.out.join(format!("{name}.png"))))
            .with("zoom", 10.0);
        jobs.push(job.val());
    }
    hsm_render.m("render", vec![Val::list(jobs)])?;
    let image = st
        .image
        .m("open", vec![Val::Path(st.out.join("scene.png"))])?
        .m("convert", args!["RGBA"])?;
    let threshold = Val::function(|args, _| {
        let a = args.first().context("missing argument a")?;
        Ok(Val::Int(if a.num()? >= 12.0 { 255 } else { 0 }))
    });
    let crop = image
        .m("getchannel", args!["A"])?
        .a("point")?
        .c(vec![threshold])?
        .m("getbbox", vec![])?;
    ensure!(!matches!(crop, Val::None), "assertion failed");
    let image = image.m("crop", vec![crop.clone()])?;
    let target = st.assets.join("opening.png");
    image.m("save", vec![Val::Path(target.clone())])?;
    let alpha_outlines = rt.native("alpha_outlines")?;
    let alpha = st
        .image
        .m("open", vec![Val::Path(st.out.join("components.png"))])?
        .m("convert", args!["RGBA"])?
        .m("crop", vec![crop.clone()])?
        .m("getchannel", args!["A"])?;
    let loops = alpha_outlines.c(vec![alpha, Val::Int(128)])?;
    ensure!(loops.truthy()?, "assertion failed");
    let size = image.a("size")?.iter()?;
    ensure!(
        size.len() == 2,
        "ValueError: not enough values to unpack (expected 2, got {})",
        size.len()
    );
    let (width, height) = (size[0].clone(), size[1].clone());
    let digest = sha256(&target)?;
    let (w, h) = (fv(&width, "")?, fv(&height, "")?);
    let mut lines = vec![
        format!(
            "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{w}\" height=\"{h}\" viewBox=\"0 0 {w} {h}\" data-source-sha256=\"{}\">",
            fv(&digest, "")?
        ),
        "<title>Current faucet shank, four tubes and display cable</title>".to_string(),
    ];
    for outline in loops.iter()? {
        let mut points = vec![];
        for point in outline.iter()? {
            let xy = point.iter()?;
            ensure!(
                xy.len() == 2,
                "ValueError: not enough values to unpack (expected 2, got {})",
                xy.len()
            );
            points.push(format!("{} {}", fv(&xy[0], "")?, fv(&xy[1], "")?));
        }
        let data = format!("M{} Z", points.join(" L"));
        lines.push(format!(
            "<path fill=\"none\" stroke=\"#46515b\" stroke-width=\"8.72\" d=\"{data}\"/>"
        ));
    }
    lines.push("</svg>".to_string());
    write_text(
        &st.assets.join("opening-faucet-outline.svg"),
        &(lines.join("\n") + "\n"),
    )?;
    let (scene_step, component_step) = (&paths[0].1, &paths[1].1);
    let scene_sha = sha256(scene_step)?;
    let component_sha = sha256(component_step)?;
    let mut sources = Dict::new();
    for path in [
        rt.file(NAME),
        st.hardware.join("install-guide/_install_art.py"),
        st.hardware.join("install-guide/_install_art_mesh.py"),
        st.hardware.join("install-guide/install_art_props.rs"),
        st.hardware.join("faucet-layout/faucet-assembly.step.mesh"),
        st.hardware.join("faucet-layout/faucet_assembly.py"),
    ] {
        let key = relative(&path, &st.root)?;
        sources.set(key, sha256(&path)?);
    }
    let registration = dict![
        "render_sha256" => digest.clone(),
        "render_size" => Val::list(vec![width.clone(), height.clone()]),
        "native_crop" => crop.clone(),
        "scene_step_sha256" => scene_sha,
        "component_step_sha256" => component_sha,
        "source_sha256" => sources.val(),
        "silhouette_scope" => "Same orthographic pose and native viewport; outer component-alpha contours.",
    ];
    write_text(
        &st.out.join("registration.json"),
        &(json_dumps(&registration, kw!["indent" => 2])? + "\n"),
    )?;
    let resolution_path = st.assets.join("print-resolution.json");
    let resolution = json_loads(&read_text(&resolution_path)?)?;
    let source_sha = sha256(&rt.file(NAME))?;
    let scene_sha = sha256(scene_step)?;
    let entry = dict![
        "reference_size" => Val::list(vec![width.clone(), height.clone()]),
        "render_size" => Val::list(vec![width.clone(), height.clone()]),
        "scale" => Val::list(vec![Val::Float(1.0), Val::Float(1.0)]),
        "render_sha256" => digest.clone(),
        "source_sha256" => source_sha,
        "scene_step_sha256" => scene_sha,
        "fixed_native_crop" => crop.clone(),
        "silhouette" => "opening-faucet-outline.svg",
    ];
    resolution
        .k("assets")?
        .set(Val::Str("opening.png".into()), entry)?;
    write_text(
        &resolution_path,
        &(json_dumps(&resolution, kw!["indent" => 2])? + "\n"),
    )?;
    note_rewritten.c(vec![Val::Path(resolution_path)])?;
    rt.pya("builtins", "print")?.ck(
        args!["Current opening artwork and component outline registered"],
        kw!["flush" => true],
    )?;
    Ok(())
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let st = state(rt)?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.module(rt, "hashlib", "hashlib")?;
    ns.module(rt, "json", "json")?;
    ns.value("os", st.os.clone());
    ns.value("sys", st.sys.clone());
    ns.value("Image", st.image.clone());
    ns.value("ROOT", st.root.clone());
    ns.value("HARDWARE", st.hardware.clone());
    ns.value("OUT", st.out.clone());
    ns.value("ASSETS", st.assets.clone());
    ns.func(rt, "outlines", |rt, c| {
        let mask: Val = c.req(0, "mask")?;
        outlines(rt, &mask)
    });
    ns.func(rt, "main", |rt, _| {
        main(rt)?;
        Ok(Val::None)
    });
    Ok(())
}
