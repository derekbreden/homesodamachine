//! Guide recipe `ice_scene` (`tools/install-guide/ice_scene.py`): ice modelled into the owner
//! guides' frozen first-pour scene and rendered at one or two cola opacities.
use super::Num::{F, I};
use super::*;
use std::path::Path;

pub const NAME: &str = "ice_scene";

/// The glass axis in the frozen scene, in world XY.
pub const GLASS_CENTER: [Num; 2] = [I(0), F(-133.99672200476698)];
pub const CAMERA: [Num; 3] = [I(1), F(-1.8), F(0.67)];

pub struct State {
    /// `pathlib.Path`, as the runtime constructs it.
    pub path: Val,
    pub argparse: Val,
    pub json: Val,
    pub math: Val,
    pub sys: Val,
    pub cq: Val,
    pub root: PathBuf,
    pub hardware: PathBuf,
    pub out: PathBuf,
    pub source: PathBuf,
    pub per_solid_color: Val,
    pub hsm_render: Val,
    pub mesh_payload: Val,
    pub read_payload: Val,
}
impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        rt.import_module("pathlib")?;
        let path = member(rt, "pathlib", "Path")?;
        let argparse = rt.import_module("argparse")?;
        let json = rt.import_module("json")?;
        let math = rt.import_module("math")?;
        let sys = rt.import_module("sys")?;
        let cq = rt.import_module("cadquery")?;
        let root = parent_n(&resolve(&rt.file(NAME)), 2);
        let hardware = root.join("hardware");
        let out = hardware.join("install-guide/out/ice");
        let source = hardware.join("install-guide/out/pour-legibility/pour-running.step");
        rt.sys_path_insert(0, &hardware.join("scripts"))?;
        rt.import_module("_cadq_export")?;
        let per_solid_color = member(rt, "_cadq_export", "_per_solid_color")?;
        let hsm_render = rt.import_module("_hsm_render")?;
        let mesh_payload = rt.import_module("_mesh_payload")?;
        rt.import_module("flute_payload")?;
        let read_payload = member(rt, "flute_payload", "read_payload")?;
        Ok(Self {
            path,
            argparse,
            json,
            math,
            sys,
            cq,
            root,
            hardware,
            out,
            source,
            per_solid_color,
            hsm_render,
            mesh_payload,
            read_payload,
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

/// `path.mkdir(parents=parents, exist_ok=True)`, as the runtime runs it.
fn mkdir(path: &Path, parents: bool) -> Result<()> {
    let made = if parents {
        std::fs::create_dir_all(path)
    } else {
        std::fs::create_dir(path)
    };
    match made {
        Err(e) if e.kind() != std::io::ErrorKind::AlreadyExists => Err(e.into()),
        _ => Ok(()),
    }
}

/// One ice cube: its offset across and along the view, its height, its box and its X, Y, Z turns
/// in degrees.
#[derive(Clone, Copy)]
struct Cube {
    u: Num,
    v: Num,
    z: Num,
    size: [Num; 3],
    angles: [Num; 3],
}

/// Write the first-pour payload with ice cubes added and the cola split into a front and a
/// depth layer; returns the payload's path.
pub fn scene(rt: &Runtime) -> Result<PathBuf> {
    let st = state(rt)?;
    let cq = &st.cq;
    let meshes = st
        .read_payload
        .c(args![st.source.with_extension("step.mesh")])?;
    if !meshes.truthy()? {
        bail!(
            "ValueError: No frozen first-pour payload at {}",
            ps(&st.source)
        );
    }
    let result = cq
        .a("Assembly")?
        .ck(vec![], kw!["name" => "first-pour-with-ice"])?;
    let length = hypot(&[CAMERA[0].f(), CAMERA[1].f()]);
    ensure!(length != 0., "division by zero");
    let front = [CAMERA[0].f() / length, CAMERA[1].f() / length];
    let right = [-front[1], front[0]];
    let mut cubes = vec![
        Cube {
            u: I(-14),
            v: I(-8),
            z: I(78),
            size: [I(21), I(21), I(23)],
            angles: [I(11), I(-8), I(18)],
        },
        Cube {
            u: I(15),
            v: I(-10),
            z: I(79),
            size: [I(21), I(21), I(22)],
            angles: [I(-9), I(12), I(-19)],
        },
        Cube {
            u: I(0),
            v: I(15),
            z: I(76),
            size: [I(22), I(21), I(24)],
            angles: [I(8), I(-9), I(34)],
        },
    ];
    let layers: [(f64, f64, i64, [f64; 3]); 3] = [
        (14.8, 10.3, -12, [18.8, 19.0, 16.8]),
        (33.4, 10.8, 14, [20.0, 19.7, 17.2]),
        (51.9, 11.1, -5, [20.4, 20.1, 17.0]),
    ];
    let turns: [[i64; 3]; 4] = [[-2, 2, -2], [2, -1, 2], [-1, -2, -3], [1, 2, 3]];
    let alignment = degrees(right[1].atan2(right[0]));
    for (z, spread, yaw, size) in layers {
        let angle = radians(yaw as f64);
        let corners = [
            (-spread, -spread),
            (spread, -spread),
            (spread, spread),
            (-spread, spread),
        ];
        for ((u, v), [rx, ry, rz]) in corners.into_iter().zip(turns) {
            let (u, v) = (
                u * angle.cos() - v * angle.sin(),
                u * angle.sin() + v * angle.cos(),
            );
            cubes.push(Cube {
                u: F(u),
                v: F(v),
                z: F(z),
                size: size.map(F),
                angles: [I(rx), I(ry), F(alignment - yaw as f64 + rz as f64)],
            });
        }
    }
    for (index, ice) in cubes.iter().enumerate() {
        let mut cube = cq
            .a("Workplane")?
            .c(args!["XY"])?
            .m("box", ice.size.iter().map(ToVal::to_val).collect())?
            .m("edges", vec![])?
            .m("fillet", args![2.1])?;
        for (axis, angle) in [[1i64, 0, 0], [0, 1, 0], [0, 0, 1]]
            .into_iter()
            .zip(ice.angles)
        {
            cube = cube.m("rotate", args![[0i64, 0, 0], axis, angle])?;
        }
        let x = GLASS_CENTER[0].f() + right[0] * ice.u.f() + front[0] * ice.v.f();
        let y = GLASS_CENTER[1].f() + right[1] * ice.u.f() + front[1] * ice.v.f();
        cube = cube.m("translate", args![(x, y, ice.z)])?;
        let color = cq.a("Color")?.c(args![0.83, 0.92, 0.97])?;
        result.mk(
            "add",
            vec![cube],
            kw!["name" => format!("ice-{}", index + 1), "color" => color],
        )?;
    }
    let ice = st
        .mesh_payload
        .m("from_assembly", args![st.per_solid_color.c(args![result])?])?;
    rt.native("ice_colors")?.c(args![ice.clone()])?;
    let mut drinks = vec![];
    for mesh in meshes.iter()? {
        if matches!(mesh.k("name")?, Val::Str(ref name) if name == "drink") {
            drinks.push(mesh);
        }
    }
    let Some(drink) = drinks.into_iter().next() else {
        bail!("ValueError: The frozen first-pour scene has no cola");
    };
    let back = Val::dict(hsm_documents::interop::entries_of(&drink)?);
    back.set("name".into(), "cola-depth".into())?;
    rt.native("drink_front")?.c(args![drink])?;
    let target = st.out.join("pour-with-ice.step.mesh");
    let mut written = meshes.iter()?;
    written.extend(ice.iter()?);
    written.push(back);
    st.mesh_payload
        .m("write", args![Val::list(written), target.clone()])?;
    Ok(target)
}

/// The renderer's material rules for one ice style and cola opacity.
pub fn materials(style: &str, opacity: Num) -> Val {
    let opaque = opacity.f() == 1.;
    Val::list(vec![
        dict![
            "names" => vec!["cola-depth"],
            "color" => "#351a0f",
            "unlit" => true,
            "side" => "back",
        ],
        dict![
            "names" => vec!["glass"],
            "color" => "#d6e8ec",
            "opacity" => 0.045,
            "roughness" => 0.15,
            "metalness" => 0.05,
            "depth_write" => false,
            "side" => "double",
            "order" => 10i64,
        ],
        dict![
            "names" => vec!["glass-rim", "glass-base"],
            "color" => "#edf2f3",
            "unlit" => true,
            "side" => "front",
        ],
        dict![
            "names" => vec!["drink"],
            "color" => "#351a0f",
            "unlit" => true,
            "opacity" => opacity,
            "depth_write" => opaque,
            "side" => "front",
            "order" => 2i64,
        ],
        dict![
            "names" => vec!["drink-top"],
            "color" => "#6f422b",
            "unlit" => true,
            "opacity" => opacity,
            "depth_write" => opaque,
            "side" => "front",
            "order" => 3i64,
        ],
        dict![
            "names" => vec!["ice-*"],
            "color" => "#ffffff",
            "unlit" => true,
            "tone_mapped" => false,
            "vertex_colors" => true,
            "opacity" => if style == "clear" { F(0.78) } else { I(1) },
            "depth_write" => true,
            "side" => "front",
            "order" => 1i64,
        ],
    ])
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let st = state(rt)?;
    ns.value("Path", st.path.clone());
    ns.value("argparse", st.argparse.clone());
    ns.value("json", st.json.clone());
    ns.value("math", st.math.clone());
    ns.value("sys", st.sys.clone());
    ns.value("cq", st.cq.clone());
    ns.value("ROOT", st.root.clone());
    ns.value("HARDWARE", st.hardware.clone());
    ns.value("OUT", st.out.clone());
    ns.value("SOURCE", st.source.clone());
    ns.value("_per_solid_color", st.per_solid_color.clone());
    ns.value("_hsm_render", st.hsm_render.clone());
    ns.value("_mesh_payload", st.mesh_payload.clone());
    ns.value("read_payload", st.read_payload.clone());
    ns.value("GLASS_CENTER", GLASS_CENTER);
    ns.value("CAMERA", CAMERA);
    ns.func(rt, "scene", |rt, _c| Ok(Val::Path(scene(rt)?)));
    ns.func(rt, "materials", |_rt, c| {
        let style: String = c.req(0, "style")?;
        let opacity: Num = c.req(1, "opacity")?;
        Ok(materials(&style, opacity))
    });
    ns.func(rt, "main", |rt, _c| {
        main(rt)?;
        Ok(Val::None)
    });
    Ok(())
}

pub fn main(rt: &Runtime) -> Result<()> {
    let st = state(rt)?;
    let doc = super::table::documentation(NAME).unwrap_or("");
    let parser = st
        .argparse
        .a("ArgumentParser")?
        .ck(vec![], kw!["description" => doc])?;
    parser.mk(
        "add_argument",
        args!["--style"],
        kw!["choices" => vec!["frosted", "clear"], "default" => "clear"],
    )?;
    let float = hsm_documents::interop::builtin("float").context("builtin float")?;
    parser.mk(
        "add_argument",
        args!["--cola-opacity"],
        kw!["type" => float, "default" => 0.82],
    )?;
    parser.mk(
        "add_argument",
        args!["--compare"],
        kw!["action" => "store_true"],
    )?;
    let args = parser.m("parse_args", vec![])?;
    let cola_opacity = Num::from_val(&args.a("cola_opacity")?)?.f();
    if !(0. < cola_opacity && cola_opacity <= 1.) {
        parser.m("error", args!["--cola-opacity must be between 0 and 1"])?;
    }
    mkdir(&st.out, true)?;
    let payload = scene(rt)?;
    let opacities = if args.a("compare")?.truthy()? {
        vec![F(0.7), F(0.82)]
    } else {
        vec![Num::from_val(&args.a("cola_opacity")?)?]
    };
    let mut entries = vec![];
    for opacity in opacities {
        let directory = st
            .out
            .join(format!("cola-{}", round_int(opacity.mul(I(100)).f())));
        mkdir(&directory, false)?;
        let style = args.a("style")?.s()?;
        entries.push(dict![
            "payload" => ps(&payload),
            "out" => ps(&directory.join("pour-base.png")),
            "materials" => materials(&style, opacity),
            "hide" => vec![
                "countertop",
                "glass-edge-*",
                "glass-highlight-*",
                "glass-rim-edge",
                "glass-base-edge",
            ],
            "cam" => CAMERA,
            "target" => [0i64, -78, 119],
            "span" => 140i64,
            "size" => "1600x1500",
            "up" => [0i64, 0, 1],
            "bg" => "#ffffff",
            "transparent" => true,
            "solid" => true,
            "ortho" => true,
            "trim" => false,
            "ground" => false,
            "fog" => false,
        ]);
    }
    let entries = Val::list(entries);
    write_text(
        &st.out.join("jobs.json"),
        &(json_dumps(&entries, kw!["indent" => 2i64])? + "\n"),
    )?;
    st.hsm_render.m("render", vec![entries.clone()])?;
    for job in entries.iter()? {
        rt.print(job.k("out")?.str()?)?;
    }
    Ok(())
}
