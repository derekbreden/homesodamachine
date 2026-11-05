//! Guide recipe `scenes`: the cylinder, power, fill and pour pictures for the install guide.
//!
//! `OUT`, `ART` and `jobs` are module globals that `startup.main` rebinds before it stages its
//! scene, so `stage`, `pour`, `render` and `main` read them from this module's namespace when
//! they run, as the source's functions read their globals.

use super::install_art;
use super::*;
use std::path::{Path, PathBuf};
use std::rc::Rc;

pub const NAME: &str = "scenes";

pub struct State {
    pub importlib: Val,
    pub sys: Val,
    pub root: PathBuf,
    pub hardware: PathBuf,
    pub out: PathBuf,
    pub art: PathBuf,
    pub cq: Val,
    /// The `_install_art` namespace.
    pub install: Val,
    /// The `_cad_art` namespace.
    pub original: Val,
    pub hsm_render: Val,
    pub reg: Val,
    pub silver: Val,
    pub black: Val,
    pub glass: Val,
    pub drink: Val,
    /// The `jobs` list the module starts with.
    pub jobs: Val,
}

/// `load(path, name)` with the module's `importlib`.
fn load_with(importlib: &Val, path: Val, name: Val) -> Result<Val> {
    let spec = importlib
        .a("util")?
        .m("spec_from_file_location", vec![name, path])?;
    let module = importlib
        .a("util")?
        .m("module_from_spec", vec![spec.clone()])?;
    spec.a("loader")?.m("exec_module", vec![module.clone()])?;
    Ok(module)
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        rt.py("importlib.util")?;
        let importlib = rt.py("importlib")?;
        let sys = rt.py("sys")?;
        let root = parent_n(&resolve(&rt.file(NAME)), 2);
        let hardware = root.join("hardware");
        let out = hardware.join("install-guide/out");
        let art = hardware.join("install-guide/art");
        sys.a("path")?.set(
            Val::Slice {
                start: None,
                stop: Some(0),
                step: 1,
            },
            Val::list(vec![
                Val::Str(ps(&hardware.join("install-guide"))),
                Val::Str(ps(&hardware.join("scripts"))),
            ]),
        )?;
        let cq = rt.py("cadquery")?;
        let install = rt.import_module(install_art::NAME)?;
        let original = rt.import_module("_cad_art")?; // via namespace: _cad_art
        let hsm_render = rt.py("_hsm_render")?;
        let reg = load_with(
            &importlib,
            Val::Path(hardware.join("reference/taprite-3741-regulator/taprite_3741_regulator.py")),
            Val::Str("installation_regulator".into()),
        )?;
        let silver = cq.a("Color")?.c(args![0.63, 0.66, 0.7])?;
        let black = cq.a("Color")?.c(args![0.07, 0.075, 0.085])?;
        let glass = cq.a("Color")?.c(args![0.58, 0.7, 0.74, 0.3])?;
        let drink = cq.a("Color")?.c(args![0.2, 0.07, 0.025, 1.0])?;
        Ok(State {
            importlib,
            sys,
            root,
            hardware,
            out,
            art,
            cq,
            install,
            original,
            hsm_render,
            reg,
            silver,
            black,
            glass,
            drink,
            jobs: Val::list(vec![]),
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// A module global as it is bound now (`OUT`, `ART`, `jobs`).
fn global(rt: &Runtime, name: &str) -> Result<Val> {
    rt.import_module(NAME)?.a(name)
}

fn global_path(rt: &Runtime, name: &str) -> Result<PathBuf> {
    PathBuf::from_val(&global(rt, name)?)
}

/// `path.mkdir(parents=..., exist_ok=...)`.
pub fn mkdir(path: &Path, parents: bool, exist_ok: bool) -> Result<()> {
    let result = if parents {
        std::fs::create_dir_all(path)
    } else {
        std::fs::create_dir(path)
    };
    if let Err(error) = result {
        if !exist_ok || error.kind() != std::io::ErrorKind::AlreadyExists {
            return Err(error).with_context(|| format!("mkdir {}", path.display()));
        }
    }
    Ok(())
}

fn truthy(n: Num) -> bool {
    n.f() != 0.0
}

/// `load(path, name)`: a Python source file executed as module `name`.
pub fn load(rt: &Runtime, path: Val, name: Val) -> Result<Val> {
    let st = state(rt)?;
    load_with(&st.importlib, path, name)
}

/// `stage(name, assembly, cam, target, span, size, flutes)`: export the scene's colored STEP and
/// queue its render job.
#[allow(clippy::too_many_arguments)]
pub fn stage(
    rt: &Runtime,
    name: &str,
    assembly: &Val,
    cam: Val,
    target: Val,
    span: Val,
    size: Val,
    flutes: bool,
) -> Result<()> {
    let st = state(rt)?;
    let path = global_path(rt, "OUT")?.join(format!("{name}.step"));
    st.original.mk(
        "_export_colored",
        vec![assembly.clone(), Val::Path(path.clone())],
        kw!["mesh" => true],
    )?; // via namespace: _cad_art
    if flutes {
        // `_install_art` has no `_graft_flutes`: the lookup fails as the source's does.
        st.install
            .a("_graft_flutes")?
            .c(vec![Val::Path(path.clone())])?;
    }
    let step = ps(path.strip_prefix(&st.hardware).with_context(|| {
        format!(
            "ValueError: {} is not in the subpath of {}",
            path.display(),
            st.hardware.display()
        )
    })?);
    let out = ps(&global_path(rt, "ART")?.join(format!("{name}.png")));
    let job = dict![
        "step" => step,
        "out" => out,
        "cam" => cam,
        "target" => target,
        "span" => span,
        "size" => size,
        "up" => (0, 0, 1),
        "bg" => "#f2eee8",
        "transparent" => true,
        "solid" => true,
        "ortho" => true,
        "trim" => false,
        "ground" => false,
        "fog" => false,
    ];
    global(rt, "jobs")?.m("append", vec![job])?;
    rt.pya("builtins", "print")?
        .ck(args!["Staged", name], kw!["flush" => true])?;
    Ok(())
}

/// `cylinder(stand_off)`: the regulator on the customer's cylinder, its red tether in the outlet
/// from the factory; `stand_off` holds the regulator out along its inlet axis.
pub fn cylinder(rt: &Runtime, stand_off: Num) -> Result<Val> {
    let st = state(rt)?;
    let install = install_art::state(rt)?;
    let cq = &st.cq;
    let a = cq
        .a("Assembly")?
        .ck(vec![], kw!["name" => "cylinder-connection"])?;
    let shift = cq
        .a("Location")?
        .c(vec![cq.a("Vector")?.c(args![stand_off, 0, 0])?])?;
    let built = st.reg.m("build_assembly", vec![])?;
    for child in built.a("children")?.iter()? {
        let obj = if truthy(stand_off) {
            child.a("obj")?.m("moved", vec![shift.clone()])?
        } else {
            child.a("obj")?
        };
        a.mk(
            "add",
            vec![obj],
            kw!["name" => child.a("name")?, "color" => child.a("color")?],
        )?;
    }
    let cx = -115.0;
    let body = cq
        .a("Workplane")?
        .ck(args!["XZ"], kw!["origin" => (cx, 0, -468)])?
        .m("moveTo", args![0, 0])?
        .m("lineTo", args![54, 0])?
        .m("threePointArc", args![(64, 6), (66.5, 17)])?
        .m("lineTo", args![66.5, 366])?
        .m("threePointArc", args![(60, 400), (19, 424)])?
        .m("lineTo", args![16, 424])?
        .m("lineTo", args![16, 441])?
        .m("lineTo", args![0, 441])?
        .m("close", vec![])?
        .m("revolve", vec![])?;
    a.mk(
        "add",
        vec![body],
        kw!["name" => "cylinder-body", "color" => st.silver.clone()],
    )?;
    let x = Num::F(cx);
    let valve = install_art::cyl(rt, x, Num::I(0), Num::I(-29), 24.0, Num::I(43), "Z")?;
    a.mk(
        "add",
        vec![valve],
        kw!["name" => "cylinder-valve", "color" => install.brass.clone()],
    )?;
    let stem = install_art::cyl(rt, x, Num::I(0), Num::I(14), 8.0, Num::I(12), "Z")?;
    a.mk(
        "add",
        vec![stem],
        kw!["name" => "cylinder-valve-stem", "color" => install.brass.clone()],
    )?;
    let handwheel = install_art::cyl(rt, x, Num::I(0), Num::I(25), 48.0, Num::I(8), "Z")?;
    a.mk(
        "add",
        vec![handwheel],
        kw!["name" => "cylinder-handwheel", "color" => st.black.clone()],
    )?;
    let nut_face = Num::from_val(&st.reg.a("INLET_NUT_FACE")?)?;
    let outlet = install_art::cyl(
        rt,
        x,
        Num::I(0),
        Num::I(-1),
        18.0,
        Num::I(115).sub(nut_face),
        "X",
    )?;
    a.mk(
        "add",
        vec![outlet],
        kw!["name" => "valve-outlet", "color" => install.brass.clone()],
    )?;
    let ports = st.reg.m("outlet", vec![])?.iter()?;
    ensure!(
        ports.len() == 2,
        "ValueError: too many values to unpack (expected 2)"
    );
    let mouth = &ports[0];
    let held = Val::Tuple(vec![
        Num::from_val(&mouth.i(0)?)?.add(stand_off).to_val(),
        mouth.i(1)?,
        mouth.i(2)?,
    ]);
    let tether = install_art::co2_tether(rt, &held, Num::I(69), Num::I(160), 28.0)?;
    a.mk(
        "add",
        vec![tether],
        kw!["name" => "red-tether", "color" => install.red_tube.clone()],
    )?;
    Ok(a)
}

/// `fill(gap)`: the bottle `gap` above its seat in the funnel, with the exterior around it.
pub fn fill(rt: &Runtime, gap: Num) -> Result<Val> {
    let st = state(rt)?;
    let source = install_art::s_bottle_in_funnel(rt)?;
    let a = st.cq.a("Assembly")?.ck(vec![], kw!["name" => "fill"])?;
    let exterior = [
        "funnel",
        "nameplate",
        "nameplate-ink",
        "enclosure-front-top",
        "enclosure-front-bottom",
        "enclosure-back-top",
        "enclosure-back-bottom",
        "front-display",
        "front-display-screen",
        "display-cover",
        "enclosure-display",
        "enclosure-display-screen",
    ];
    for child in source.a("children")?.iter()? {
        let name = child.a("name")?.s()?;
        if name.starts_with("bottle-") {
            let moved = child.a("obj")?.m("translate", args![(0, 0, gap)])?;
            a.mk(
                "add",
                vec![moved],
                kw!["name" => name, "color" => child.a("color")?],
            )?;
        } else if exterior.contains(&name.as_str()) || name.contains("display") {
            a.m("add", vec![child])?;
        }
    }
    Ok(a)
}

/// `glass_stroke`: one drawn edge of the glass, a capped rod from `z0` to `z1` on its wall.
#[allow(clippy::too_many_arguments)]
fn glass_stroke(
    st: &State,
    a: &Val,
    (gx, gy): (f64, f64),
    name: &str,
    angle: f64,
    z0: Num,
    z1: Num,
    radius: f64,
) -> Result<()> {
    let cq = &st.cq;
    let mut points = vec![];
    for z in [z0, z1] {
        let r = 31.0 + Num::I(6).mul(z).f() / 104.0;
        points.push(cq.a("Vector")?.c(args![
            gx + r * angle.cos(),
            gy + r * angle.sin(),
            z
        ])?);
    }
    let span = hsm_documents::interop::binary("sub", points[1].clone(), points[0].clone())?;
    let body = cq.a("Solid")?.a("makeCylinder")?.c(vec![
        Val::Float(radius),
        span.a("Length")?,
        points[0].clone(),
        span.m("normalized", vec![])?,
    ])?;
    let mut parts = vec![body];
    for p in &points {
        parts.push(cq.a("Solid")?.a("makeSphere")?.ck(
            vec![Val::Float(radius), p.clone()],
            kw!["angleDegrees1" => -90],
        )?);
    }
    let compound = cq
        .a("Compound")?
        .a("makeCompound")?
        .c(vec![Val::list(parts)])?;
    let color = cq.a("Color")?.c(args![0.7, 0.8, 0.85])?;
    a.mk(
        "add",
        vec![compound],
        kw!["name" => name, "color" => color],
    )?;
    Ok(())
}

/// `pour(pressed)`: the faucet over a glass, the lever at rest or pressed with cola running.
pub fn pour(rt: &Runtime, pressed: bool) -> Result<Val> {
    let st = state(rt)?;
    let install = install_art::state(rt)?;
    let cq = &st.cq;
    let fa = st.original.m("_load_faucet_module", vec![])?; // via namespace: _cad_art
    let built = fa.m("build_assembly", vec![])?;
    let parts = st.original.m("_children_by_name", vec![built])?; // via namespace: _cad_art
    let levers = st.original.m("_physical_levers", vec![fa.clone()])?.iter()?; // via namespace: _cad_art
    ensure!(
        levers.len() == 2,
        "ValueError: too many values to unpack (expected 2)"
    );
    let (rest, held) = (levers[0].clone(), levers[1].clone());
    let a = st.cq.a("Assembly")?.ck(vec![], kw!["name" => "first-pour"])?;
    let names = [
        "westbrass",
        "drain_tube",
        "soda_faucet_tube",
        "tpu_o_ring",
        "flavor_tube_pos_x",
        "flavor_tube_neg_x",
        "lever",
        "above_counter_plate",
        "above_counter_gasket",
        "shell_base",
        "shell_tip",
        "faucet-display-cover-seated",
        "faucet_display",
        "faucet_display_screen",
    ];
    for name in names {
        let child = parts.get(Val::Str(name.into()))?;
        let mut obj = if name == "lever" {
            if pressed { held.clone() } else { rest.clone() }
        } else {
            child.a("obj")?
        };
        if ["westbrass", "drain_tube", "flavor_tube_pos_x", "flavor_tube_neg_x"].contains(&name) {
            obj = st.original.m(
                "_clip_z",
                vec![obj, fa.a("countertop_top_z")?, Val::Int(260)],
            )?; // via namespace: _cad_art
        }
        a.mk(
            "add",
            vec![obj],
            kw!["name" => name, "color" => child.a("color")?],
        )?;
    }
    let counter = install_art::box_(
        rt,
        Num::I(-120),
        Num::I(-280),
        Num::I(-14),
        Num::I(240),
        Num::I(340),
        Num::I(14),
    )?;
    a.mk(
        "add",
        vec![counter],
        kw!["name" => "countertop", "color" => install.stone.clone()],
    )?;
    let centerline = fa.m("_tip_centerline_world", vec![])?.iter()?;
    ensure!(
        centerline.len() == 2,
        "ValueError: too many values to unpack (expected 2)"
    );
    let tip = centerline[1].m("toTuple", vec![])?;
    let (gx, gy) = (tip.i(0)?, tip.i(1)?);
    let at = (gx.clone(), gy.clone(), 0);
    let wp = || cq.a("Workplane")?.c(args!["XY"]);
    let outer = wp()?
        .m("circle", args![31])?
        .mk("workplane", vec![], kw!["offset" => 104])?
        .m("circle", args![37])?
        .m("loft", vec![])?;
    let inner = wp()?
        .mk("workplane", vec![], kw!["offset" => 4])?
        .m("circle", args![28])?
        .mk("workplane", vec![], kw!["offset" => 101])?
        .m("circle", args![34.2])?
        .m("loft", vec![])?;
    let glass = outer.m("cut", vec![inner])?;
    a.mk(
        "add",
        vec![glass.m("translate", args![at.clone()])?],
        kw!["name" => "glass", "color" => st.glass.clone()],
    )?;
    let rings: [(&str, f64, f64, f64, f64, [f64; 3]); 4] = [
        ("glass-rim", 103.4, 37.0, 34.1, 0.7, [0.8, 0.87, 0.9]),
        ("glass-rim-edge", 103.35, 37.5, 36.65, 0.8, [0.46, 0.57, 0.62]),
        ("glass-base", 0.8, 31.15, 28.2, 2.0, [0.74, 0.83, 0.86]),
        ("glass-base-edge", 0.6, 31.3, 30.55, 0.8, [0.46, 0.57, 0.62]),
    ];
    for (name, offset, outside, inside, height, [r, g, b]) in rings {
        let outside = if name == "glass-rim" {
            Val::Int(37)
        } else {
            Val::Float(outside)
        };
        let ring = wp()?
            .mk("workplane", vec![], kw!["offset" => offset])?
            .m("circle", vec![outside])?
            .m("circle", args![inside])?
            .m("extrude", args![height])?;
        let moved = ring.m("translate", args![at.clone()])?;
        let color = cq.a("Color")?.c(args![r, g, b])?;
        a.mk("add", vec![moved], kw!["name" => name, "color" => color])?;
    }
    let face_angle = (-1.8f64).atan2(1.0);
    let centre = (gx.f()?, gy.f()?);
    let side_angle = ((0.67 * 6.0) / 104.0 / hypot(&[1.0, 1.8])).acos();
    ensure!(side_angle.is_finite(), "ValueError: math domain error");
    for (sign, side) in [(-1.0, "left"), (1.0, "right")] {
        glass_stroke(
            &st,
            &a,
            centre,
            &format!("glass-edge-{side}"),
            face_angle + sign * side_angle,
            Num::F(2.5),
            Num::F(102.8),
            0.7,
        )?;
    }
    glass_stroke(
        &st,
        &a,
        centre,
        "glass-highlight-wide",
        face_angle - side_angle + 0.16,
        Num::I(12),
        Num::I(96),
        1.15,
    )?;
    glass_stroke(
        &st,
        &a,
        centre,
        "glass-highlight-short",
        face_angle + side_angle - 0.13,
        Num::I(51),
        Num::I(95),
        0.65,
    )?;
    if pressed {
        let drink = wp()?
            .mk("workplane", vec![], kw!["offset" => 5])?
            .m("circle", args![27.7])?
            .mk("workplane", vec![], kw!["offset" => 75])?
            .m("circle", args![32.1])?
            .m("loft", vec![])?;
        a.mk(
            "add",
            vec![drink.m("translate", args![at.clone()])?],
            kw!["name" => "drink", "color" => st.drink.clone()],
        )?;
        let top = wp()?
            .mk("workplane", vec![], kw!["offset" => 80])?
            .m("circle", args![32.1])?
            .m("extrude", args![0.15])?;
        let moved = top.m("translate", args![at.clone()])?;
        let color = cq.a("Color")?.c(args![0.53, 0.31, 0.18])?;
        a.mk(
            "add",
            vec![moved],
            kw!["name" => "drink-top", "color" => color],
        )?;
    }
    let points = dict![
        "tip" => Val::list(tip.iter()?),
        "lever" => Val::list(vec![
            Val::Int(0),
            fa.a("lever_pivot_y")?,
            fa.a("lever_pivot_z")?,
        ]),
    ];
    write_text(
        &global_path(rt, "OUT")?.join("pour-points.json"),
        &json_dumps(&points, vec![])?,
    )?;
    Ok(a)
}

/// `materials()`: the glass and cola's authored presentation, addressed by solid name.
pub fn materials() -> Val {
    Val::list(vec![
        dict![
            "names" => list(&["glass"]),
            "color" => "#d6e8ec",
            "opacity" => 0.06,
            "roughness" => 0.15,
            "metalness" => 0.05,
            "depth_write" => false,
            "side" => "double",
            "order" => 10,
        ],
        dict![
            "names" => list(&["glass-rim", "glass-base"]),
            "color" => "#d3e1e5",
            "unlit" => true,
            "side" => "front",
        ],
        dict![
            "names" => list(&["glass-edge-*", "glass-rim-edge", "glass-base-edge"]),
            "color" => "#8099a4",
            "unlit" => true,
            "side" => "front",
        ],
        dict![
            "names" => list(&["glass-highlight-*"]),
            "color" => "#ffffff",
            "opacity" => 0.74,
            "unlit" => true,
            "depth_write" => false,
            "side" => "front",
            "order" => 11,
        ],
        dict![
            "names" => list(&["drink"]),
            "color" => "#351a0f",
            "unlit" => true,
            "side" => "front",
        ],
        dict![
            "names" => list(&["drink-top"]),
            "color" => "#6f422b",
            "unlit" => true,
            "side" => "front",
        ],
    ])
}

/// `render()`: draw the staged payloads with the clear glass and cola materials.
pub fn render(rt: &Runtime) -> Result<()> {
    let st = state(rt)?;
    let mut entries = vec![];
    for job in global(rt, "jobs")?.iter()? {
        let mut entry = Dict(job.items()?);
        entry.set("materials", materials());
        entries.push(entry.val());
    }
    let entries = Val::list(entries);
    write_text(
        &global_path(rt, "OUT")?.join("scenes.json"),
        &(json_dumps(&entries, kw!["indent" => 2])? + "\n"),
    )?;
    st.hsm_render.m("render", vec![entries])?;
    Ok(())
}

/// `main()`: stage the scenes the arguments name (all when none), then render them.
pub fn main(rt: &Runtime) -> Result<()> {
    let st = state(rt)?;
    mkdir(&global_path(rt, "OUT")?, true, true)?;
    mkdir(&global_path(rt, "ART")?, false, true)?;
    let argv: Vec<String> = Vec::from_val(&st.sys.a("argv")?)?;
    let wanted: Vec<String> = argv.into_iter().skip(1).collect();
    let want = |scene: &str| wanted.is_empty() || wanted.iter().any(|w| w == scene);
    let default_size = || Val::Str("1600x1500".into());
    if want("gas") {
        for (name, stand_off) in [("co2-ready", Num::I(30)), ("co2-connected", Num::I(0))] {
            let assembly = cylinder(rt, stand_off)?;
            stage(
                rt,
                name,
                &assembly,
                (0.12, 1, 0.15).to_val(),
                (-34, 0, -58).to_val(),
                Val::Int(150),
                default_size(),
                false,
            )?;
        }
    }
    if want("power") {
        let install = install_art::state(rt)?;
        let paths = st
            .original
            .m("_build_connection_steps", vec![global(rt, "OUT")?])?; // via namespace: _cad_art
        let connected = st
            .cq
            .a("Assembly")?
            .a("load")?
            .c(vec![Val::Str(paths.k("connect-rear-connected")?.str()?)])?;
        for (label, gap) in [("power-ready", Num::I(65)), ("power-connected", Num::F(0.5))] {
            let a = st.cq.a("Assembly")?.ck(vec![], kw!["name" => label])?;
            for child in connected.a("children")?.iter()? {
                a.m("add", vec![child])?;
            }
            let cordset = install_art::c13_cordset(rt, gap)?;
            a.mk(
                "add",
                vec![cordset],
                kw!["name" => "cordset", "color" => install.cordset.clone()],
            )?;
            let station = install.c14_station.iter()?;
            ensure!(
                station.len() == 2,
                "ValueError: too many values to unpack (expected 2)"
            );
            let (x, z) = (Num::from_val(&station[0])?, Num::from_val(&station[1])?);
            let face = Num::from_val(&install.rear_face_y)?;
            stage(
                rt,
                label,
                &a,
                (-0.85, 1, 0.25).to_val(),
                (x.sub(Num::I(8)), face.add(Num::I(34)), z.sub(Num::I(16))).to_val(),
                Val::Int(64),
                Val::Str("1800x1300".into()),
                true,
            )?;
        }
    }
    if want("fill") {
        for (name, gap) in [("fill-ready", 85), ("fill-seated", 0)] {
            let assembly = fill(rt, Num::I(gap))?;
            stage(
                rt,
                name,
                &assembly,
                (0.65, -1, 0.5).to_val(),
                (0, 140, 465).to_val(),
                Val::Int(265),
                default_size(),
                true,
            )?;
        }
    }
    if want("pour") {
        for (name, pressed) in [("pour-ready", false), ("pour-running", true)] {
            let assembly = pour(rt, pressed)?;
            stage(
                rt,
                name,
                &assembly,
                (1, -1.8, 0.67).to_val(),
                (0, -78, 119).to_val(),
                Val::Int(140),
                default_size(),
                false,
            )?;
        }
    }
    render(rt)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let st = state(rt)?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("importlib", st.importlib.clone());
    ns.module(rt, "json", "json")?;
    ns.module(rt, "math", "math")?;
    ns.value("sys", st.sys.clone());
    ns.value("ROOT", st.root.clone());
    ns.value("HARDWARE", st.hardware.clone());
    ns.value("OUT", st.out.clone());
    ns.value("ART", st.art.clone());
    ns.value("cq", st.cq.clone());
    ns.value("install", st.install.clone());
    ns.value("original", st.original.clone());
    ns.value("_hsm_render", st.hsm_render.clone());
    ns.func(rt, "load", |rt, c| {
        let path: Val = c.req(0, "path")?;
        let name: Val = c.req(1, "name")?;
        load(rt, path, name)
    });
    ns.value("reg", st.reg.clone());
    ns.value("SILVER", st.silver.clone());
    ns.value("BLACK", st.black.clone());
    ns.value("GLASS", st.glass.clone());
    ns.value("DRINK", st.drink.clone());
    ns.value("jobs", st.jobs.clone());
    ns.func(rt, "stage", |rt, c| {
        let name: Val = c.req(0, "name")?;
        let assembly: Val = c.req(1, "assembly")?;
        let cam: Val = c.req(2, "cam")?;
        let target: Val = c.req(3, "target")?;
        let span: Val = c.req(4, "span")?;
        let size: Val = c.opt(5, "size", Val::Str("1600x1500".into()))?;
        let flutes: Val = c.opt(6, "flutes", Val::Bool(false))?;
        stage(
            rt,
            &fv(&name, "")?,
            &assembly,
            cam,
            target,
            span,
            size,
            flutes.truthy()?,
        )?;
        Ok(Val::None)
    });
    ns.func(rt, "cylinder", |rt, c| {
        let stand_off: Num = c.opt(0, "stand_off", Num::I(0))?;
        cylinder(rt, stand_off)
    });
    ns.func(rt, "fill", |rt, c| {
        let gap: Num = c.opt(0, "gap", Num::I(0))?;
        fill(rt, gap)
    });
    ns.func(rt, "pour", |rt, c| {
        let pressed: Val = c.req(0, "pressed")?;
        pour(rt, pressed.truthy()?)
    });
    ns.func(rt, "materials", |_, _| Ok(materials()));
    ns.func(rt, "render", |rt, _| {
        render(rt)?;
        Ok(Val::None)
    });
    ns.func(rt, "main", |rt, _| {
        main(rt)?;
        Ok(Val::None)
    });
    Ok(())
}
