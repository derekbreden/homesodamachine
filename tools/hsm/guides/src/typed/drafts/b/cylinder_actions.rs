//! Guide recipe `cylinder_actions`: the cylinder connection and startup controls, in the
//! regulator's world frame. +Y faces the customer, +Z is up, and the cylinder stands at -X.

use super::*;
use super::{scenes, startup};
use std::path::PathBuf;
use std::rc::Rc;

pub const NAME: &str = "cylinder_actions";

pub const READY_STANDOFF: f64 = 30.0;
pub const STARTUP_EXTRA_HEIGHT: i64 = 300;

/// A render pose: camera direction, target, half-height span and pixel size.
#[derive(Clone, Copy, Debug)]
pub struct Pose {
    pub cam: [Num; 3],
    pub target: [Num; 3],
    pub span: Num,
    pub size: [Num; 2],
}

impl Pose {
    pub fn val(&self) -> Val {
        dict![
            "cam" => self.cam,
            "target" => self.target,
            "span" => self.span,
            "size" => self.size,
        ]
    }
    pub fn from_val(pose: &Val) -> Result<Self> {
        Ok(Pose {
            cam: <[Num; 3]>::from_val(&pose.k("cam")?)?,
            target: <[Num; 3]>::from_val(&pose.k("target")?)?,
            span: Num::from_val(&pose.k("span")?)?,
            size: <[Num; 2]>::from_val(&pose.k("size")?)?,
        })
    }
}

pub const CONNECTION_POSE: Pose = Pose {
    cam: [Num::F(0.12), Num::I(1), Num::F(0.15)],
    target: [Num::I(-34), Num::I(0), Num::I(-50)],
    span: Num::I(150),
    size: [Num::I(1600), Num::I(1500)],
};

pub struct State {
    pub argparse: Val,
    pub cq: Val,
    pub image: Val,
    /// The `scenes` and `startup` namespaces.
    pub scenes: Val,
    pub startup: Val,
    pub out: PathBuf,
    pub art: PathBuf,
    pub reg: Val,
    /// `scenes.install`: the `_install_art` namespace.
    pub install: Val,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let argparse = rt.py("argparse")?;
        let cq = rt.py("cadquery")?;
        let pil = rt.py("PIL")?;
        let image = match pil.a("Image") {
            Ok(image) => image,
            Err(_) => rt.py("PIL.Image")?,
        };
        let scenes_ns = rt.import_module(scenes::NAME)?;
        let startup_ns = rt.import_module(startup::NAME)?;
        let shared = scenes::state(rt)?;
        let out = shared.hardware.join("install-guide/out/cylinder-actions");
        let art = shared.hardware.join("install-guide/art/cylinder-actions");
        Ok(State {
            argparse,
            cq,
            image,
            scenes: scenes_ns,
            startup: startup_ns,
            out,
            art,
            reg: shared.reg.clone(),
            install: shared.install.clone(),
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `unit(vector)`.
pub fn unit(vector: &[Num]) -> Result<Vec<f64>> {
    let squares = fsum(vector.iter().map(|v| v.mul(*v).f()));
    ensure!(squares >= 0.0, "ValueError: math domain error");
    let length = squares.sqrt();
    ensure!(length != 0.0, "ZeroDivisionError: float division by zero");
    Ok(vector.iter().map(|v| v.f() / length).collect())
}

/// `cross(a, b)`.
pub fn cross(a: [Num; 3], b: [Num; 3]) -> [Num; 3] {
    [
        a[1].mul(b[2]).sub(a[2].mul(b[1])),
        a[2].mul(b[0]).sub(a[0].mul(b[2])),
        a[0].mul(b[1]).sub(a[1].mul(b[0])),
    ]
}

fn three(values: &[f64]) -> [f64; 3] {
    [values[0], values[1], values[2]]
}

/// `camera_axes(cam)`: the image plane's right and up directions.
pub fn camera_axes(cam: [Num; 3]) -> Result<([f64; 3], [f64; 3])> {
    let direction = three(&unit(&cam)?);
    let floats = |v: [f64; 3]| v.map(Num::F);
    let right = three(&unit(&cross(
        [Num::I(0), Num::I(0), Num::I(1)],
        floats(direction),
    ))?);
    let up = cross(floats(direction), floats(right)).map(Num::f);
    Ok((right, up))
}

/// `startup_pose()`: the startup camera's pixel registration with extra canvas below it.
pub fn startup_pose() -> Result<Pose> {
    let (_, up) = camera_axes(startup::CAM)?;
    let (width, height) = startup::SIZE;
    let scale = height as f64 / (2.0 * startup::SPAN);
    let shift = STARTUP_EXTRA_HEIGHT as f64 / (2.0 * scale);
    let tall = height + STARTUP_EXTRA_HEIGHT;
    let mut target = [Num::F(0.0); 3];
    for ((slot, value), axis) in target.iter_mut().zip(startup::TARGET).zip(up) {
        *slot = Num::F(value.f() - shift * axis);
    }
    Ok(Pose {
        cam: startup::CAM,
        target,
        span: Num::F(startup::SPAN * tall as f64 / height as f64),
        size: [Num::I(width), Num::I(tall)],
    })
}

/// `pixel(point, pose)`: where a world point lands in the pose's image, from its top left.
pub fn pixel(point: [Num; 3], pose: &Pose) -> Result<(f64, f64)> {
    let (right, up) = camera_axes(pose.cam)?;
    let delta: Vec<Num> = point
        .iter()
        .zip(pose.target)
        .map(|(value, target)| value.sub(target))
        .collect();
    let [width, height] = pose.size;
    let scale = height.f() / Num::I(2).mul(pose.span).f();
    let along = |axes: [f64; 3]| fsum(delta.iter().zip(axes).map(|(v, a)| v.f() * a));
    Ok((
        width.f() / 2.0 + along(right) * scale,
        height.f() / 2.0 - along(up) * scale,
    ))
}

fn station(rt: &Runtime, name: &str) -> Result<[Num; 3]> {
    let st = state(rt)?;
    <[Num; 3]>::from_val(&st.reg.m(name, vec![])?.i(0)?)
}

fn attr(reg: &Val, name: &str) -> Result<Num> {
    Num::from_val(&reg.a(name)?)
}

/// `outlet_stations(stand_off)`: the outlet push-fit and the tube leaving it, and the big
/// nut's face.
pub fn outlet_stations(rt: &Runtime, stand_off: Num) -> Result<OMap<[Num; 3]>> {
    let st = state(rt)?;
    let reg = &st.reg;
    let [x, y, mouth_z] = station(rt, "outlet")?;
    let x = x.add(stand_off);
    let half = |name: &str| -> Result<Num> { Ok(Num::F(attr(reg, name)?.f() / 2.0)) };
    let mut stations = OMap::new();
    stations.set(
        "outlet-connector",
        [
            x,
            y.add(half("PTC_COLLET_D")?),
            Num::F(attr(reg, "OUTLET_HEX_Z")?.add(mouth_z).f() / 2.0),
        ],
    );
    stations.set("red-tube-exit", [x, y, mouth_z]);
    let inlet = Num::from_val(&reg.m("inlet", vec![])?.i(0)?.i(0)?)?;
    stations.set(
        "cga-nut",
        [
            inlet.add(stand_off),
            y.add(half("CGA320_NUT_FLATS")?),
            Num::F(0.0),
        ],
    );
    Ok(stations)
}

/// `assembly(stand_off, pressurised)`: the regulator, its factory-fitted tether and the top of
/// the customer's cylinder.
pub fn assembly(rt: &Runtime, stand_off: Num, pressurised: bool) -> Result<Val> {
    if pressurised {
        startup::assembly(rt)
    } else {
        scenes::cylinder(rt, stand_off)
    }
}

/// `points(stand_off, pressurised)`: the anchors the guide's callouts point at.
pub fn points(rt: &Runtime, stand_off: Num, pressurised: bool) -> Result<OMap<[Num; 3]>> {
    let held = |point: [Num; 3]| [point[0].add(stand_off), point[1], point[2]];
    let mut result = outlet_stations(rt, stand_off)?;
    let fixed = [
        ("upper-gauge", held(station(rt, "outlet_dial")?)),
        ("cylinder-gauge", held(station(rt, "tank_dial")?)),
        ("factory-screw", held(station(rt, "adjustment")?)),
        ("cylinder-handwheel", [Num::I(-115), Num::I(0), Num::I(33)]),
        ("cylinder-valve", [Num::I(-115), Num::I(12), Num::F(-7.5)]),
    ];
    for (name, point) in fixed {
        result.set(name, point);
    }
    if pressurised {
        let tip = startup::points(rt)?.k("upper-needle-tip")?;
        result.set("upper-needle-tip", <[Num; 3]>::from_val(&tip)?);
    }
    Ok(result)
}

fn pixel_val(point: [Num; 3], pose: &Pose) -> Result<Val> {
    Ok(pixel(point, pose)?.to_val())
}

/// `anchor_metadata(stand_off, pressurised, pose)`: the scene's pose, crops and every anchor
/// in world and pixel coordinates.
pub fn anchor_metadata(rt: &Runtime, stand_off: Num, pressurised: bool, pose: &Pose) -> Result<Val> {
    let mut anchors = Dict::new();
    for (name, point) in points(rt, stand_off, pressurised)?.iter() {
        let source = if ["cylinder-handwheel", "cylinder-valve"].contains(&name) {
            "tools/install-guide/scenes.py:cylinder"
        } else if name == "upper-needle-tip" {
            "tools/install-guide/startup.py:points"
        } else {
            "hardware/reference/taprite-3741-regulator/taprite_3741_regulator.py:stations"
        };
        anchors.set(
            name,
            dict![
                "world" => *point,
                "pixel" => pixel_val(*point, pose)?,
                "source" => source,
            ],
        );
    }
    let nut = *outlet_stations(rt, stand_off)?.at("cga-nut")?;
    let seated_nut = *outlet_stations(rt, Num::I(0))?.at("cga-nut")?;
    let crops = if pressurised {
        dict![
            "overview" => (173, 53, 1752, 1360),
            "upper_gauge" => (533, 48, 873, 388),
            "connector_detail" => (485, 950, 905, 1360),
        ]
    } else {
        dict![
            "overview" => (80, 0, 1600, 1500),
            "connector_detail" => (420, 775, 830, 1335),
        ]
    };
    let (outlet_psi, cylinder_psi) = if pressurised {
        let st = startup::state(rt)?;
        (st.outlet_psi.clone(), Val::Int(startup::CYLINDER_PSI))
    } else {
        (Val::Int(0), Val::Int(0))
    };
    Ok(dict![
        "cam" => pose.cam,
        "target" => pose.target,
        "span" => pose.span,
        "size" => pose.size,
        "projection" => "orthographic",
        "up" => (0, 0, 1),
        "trim" => false,
        "pixel_origin" => "top-left",
        "pixels_per_mm" => pose.size[1].f() / Num::I(2).mul(pose.span).f(),
        "crops" => crops,
        "stand_off_mm" => stand_off,
        "outlet_psi" => outlet_psi,
        "cylinder_psi" => cylinder_psi,
        "points" => anchors.val(),
        "approach" => dict![
            "axis" => (-1, 0, 0),
            "distance_mm" => stand_off,
            "from_world" => nut,
            "to_world" => seated_nut,
            "from_pixel" => pixel_val(nut, pose)?,
            "to_pixel" => pixel_val(seated_nut, pose)?,
        ],
        "turn_axes" => dict!["cylinder-handwheel" => (0, 0, 1)],
    ])
}

/// `main()`: export and render the connection and startup scenes, and record their anchors.
pub fn main(rt: &Runtime) -> Result<()> {
    let st = state(rt)?;
    let shared = scenes::state(rt)?;
    let parser = st.argparse.a("ArgumentParser")?.ck(
        vec![],
        kw!["description" => super::table::documentation(NAME).unwrap_or("")],
    )?;
    parser.mk(
        "add_argument",
        args!["scenes"],
        kw![
            "nargs" => "*",
            "choices" => list(&["co2-ready", "co2-connected", "startup-gas"]),
        ],
    )?;
    parser.mk(
        "add_argument",
        args!["--stage-only"],
        kw!["action" => "store_true"],
    )?;
    let args = parser.m("parse_args", vec![])?;
    let wanted: Vec<String> = Vec::from_val(&args.a("scenes")?)?;
    scenes::mkdir(&st.out, true, true)?;
    scenes::mkdir(&st.art, true, true)?;
    let mut jobs = vec![];
    let metadata = dict![
        "geometry_sources" => dict![
            "regulator" => "hardware/reference/taprite-3741-regulator/taprite_3741_regulator.py",
            "cylinder" => "tools/install-guide/scenes.py:cylinder",
            "tether" => "hardware/install-guide/_install_art.py:_co2_tether",
            "startup-dials" => "tools/install-guide/startup.py:assembly",
        ],
        "fittings" => list(&["PI010822S"]),
        "tether_seating" => "Pushed in at the factory; the drawn depth past the mouth is illustrative.",
        "scenes" => Dict::new(),
    ];
    let scenes_meta = metadata.k("scenes")?;
    let states = [
        ("co2-ready", Num::F(READY_STANDOFF), false, CONNECTION_POSE),
        ("co2-connected", Num::I(0), false, CONNECTION_POSE),
        ("startup-gas", Num::I(0), true, startup_pose()?),
    ];
    for (name, stand_off, pressurised, pose) in states {
        if !wanted.is_empty() && !wanted.iter().any(|w| w == name) {
            continue;
        }
        let path = st.out.join(format!("{name}.step"));
        let scene = assembly(rt, stand_off, pressurised)?;
        shared.original.mk(
            "_export_colored",
            vec![scene, Val::Path(path.clone())],
            kw!["mesh" => true],
        )?; // via namespace: _cad_art
        let step = ps(path.strip_prefix(&shared.hardware).with_context(|| {
            format!(
                "ValueError: {} is not in the subpath of {}",
                path.display(),
                shared.hardware.display()
            )
        })?);
        jobs.push(dict![
            "step" => step,
            "out" => ps(&st.art.join(format!("{name}.png"))),
            "cam" => pose.cam,
            "target" => pose.target,
            "span" => pose.span,
            "size" => format!(
                "{}x{}",
                fv(&pose.size[0].to_val(), "")?,
                fv(&pose.size[1].to_val(), "")?
            ),
            "up" => (0, 0, 1),
            "bg" => "#f2eee8",
            "transparent" => true,
            "solid" => true,
            "ortho" => true,
            "trim" => false,
            "ground" => false,
            "fog" => false,
        ]);
        let entry = anchor_metadata(rt, stand_off, pressurised, &pose)?;
        scenes_meta.set(Val::Str(name.into()), entry.clone())?;
        if name == "startup-gas" {
            entry.set(
                Val::Str("registered_source_pose".into()),
                dict![
                    "cam" => startup::CAM,
                    "target" => startup::TARGET,
                    "span" => startup::SPAN,
                    "size" => startup::SIZE,
                    "same_pixel_coordinates" => true,
                    "extra_canvas_below" => STARTUP_EXTRA_HEIGHT,
                ],
            )?;
        }
        rt.pya("builtins", "print")?
            .ck(args![format!("Staged {name}")], kw!["flush" => true])?;
    }
    let jobs = Val::list(jobs);
    write_text(
        &st.out.join("scenes.json"),
        &(json_dumps(&jobs, kw!["indent" => 2])? + "\n"),
    )?;
    if !args.a("stage_only")?.truthy()? {
        shared.hsm_render.m("render", vec![jobs.clone()])?;
        for (name, entry) in scenes_meta.items()? {
            let png = st.art.join(format!("{}.png", fv(&name, "")?));
            let opened = st.image.m("open", vec![Val::Path(png)])?;
            with(&opened, |rendered| {
                let size = Val::Tuple(entry.k("size")?.iter()?);
                ensure!(
                    hsm_documents::interop::compare("eq", rendered.a("size")?, size)?.truthy()?,
                    "assertion failed"
                );
                let bounds = rendered
                    .m("getchannel", args!["A"])?
                    .m("getbbox", vec![])?;
                entry.set(Val::Str("alpha_bounds".into()), bounds)?;
                Ok(())
            })?;
        }
    }
    let anchors = st.out.join("anchors.json");
    write_text(
        &anchors,
        &(json_dumps(&metadata, kw!["indent" => 2])? + "\n"),
    )?;
    rt.pya("builtins", "print")?.c(vec![Val::Path(anchors)])?;
    Ok(())
}

fn points_val(points: &OMap<[Num; 3]>) -> Val {
    points.to_val()
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let st = state(rt)?;
    ns.value("argparse", st.argparse.clone());
    ns.module(rt, "json", "json")?;
    ns.module(rt, "math", "math")?;
    ns.value("cq", st.cq.clone());
    ns.value("Image", st.image.clone());
    ns.value("scenes", st.scenes.clone());
    ns.value("startup", st.startup.clone());
    ns.value("OUT", st.out.clone());
    ns.value("ART", st.art.clone());
    ns.value("READY_STANDOFF", READY_STANDOFF);
    ns.value("CONNECTION_POSE", CONNECTION_POSE.val());
    ns.value("STARTUP_EXTRA_HEIGHT", STARTUP_EXTRA_HEIGHT);
    ns.value("reg", st.reg.clone());
    ns.value("install", st.install.clone());
    ns.func(rt, "unit", |_, c| {
        let vector: Vec<Num> = c.req(0, "vector")?;
        Ok(tuple(&unit(&vector)?))
    });
    ns.func(rt, "cross", |_, c| {
        let a: [Num; 3] = c.req(0, "a")?;
        let b: [Num; 3] = c.req(1, "b")?;
        Ok(cross(a, b).to_val())
    });
    ns.func(rt, "camera_axes", |_, c| {
        let cam: [Num; 3] = c.req(0, "cam")?;
        Ok(camera_axes(cam)?.to_val())
    });
    ns.func(rt, "startup_pose", |_, _| Ok(startup_pose()?.val()));
    ns.func(rt, "pixel", |_, c| {
        let point: [Num; 3] = c.req(0, "point")?;
        let pose: Val = c.req(1, "pose")?;
        pixel_val(point, &Pose::from_val(&pose)?)
    });
    ns.func(rt, "outlet_stations", |rt, c| {
        let stand_off: Num = c.req(0, "stand_off")?;
        Ok(points_val(&outlet_stations(rt, stand_off)?))
    });
    ns.func(rt, "assembly", |rt, c| {
        let stand_off: Num = c.opt(0, "stand_off", Num::I(0))?;
        let pressurised: Val = c.opt(1, "pressurised", Val::Bool(false))?;
        assembly(rt, stand_off, pressurised.truthy()?)
    });
    ns.func(rt, "points", |rt, c| {
        let stand_off: Num = c.req(0, "stand_off")?;
        let pressurised: Val = c.req(1, "pressurised")?;
        Ok(points_val(&points(rt, stand_off, pressurised.truthy()?)?))
    });
    ns.func(rt, "anchor_metadata", |rt, c| {
        let stand_off: Num = c.req(0, "stand_off")?;
        let pressurised: Val = c.req(1, "pressurised")?;
        let pose: Val = c.req(2, "pose")?;
        anchor_metadata(rt, stand_off, pressurised.truthy()?, &Pose::from_val(&pose)?)
    });
    ns.func(rt, "main", |rt, _| {
        main(rt)?;
        Ok(Val::None)
    });
    Ok(())
}
