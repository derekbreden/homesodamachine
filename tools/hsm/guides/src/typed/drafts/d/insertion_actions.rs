//! Guide recipe `insertion_actions` (`tools/install-guide/insertion_actions.py`): the cord and
//! bottle insertion poses, staged from the frozen installation meshes and rendered on the GPU.
use super::Num::{F, I};
use super::*;
use std::path::Path;

pub const NAME: &str = "insertion_actions";

/// The cordset's retreat from the inlet, in mm along +Y.
pub const POWER_RETREAT: f64 = 25.0;
/// The bottle's lift above the funnel, in mm along +Z.
pub const BOTTLE_LIFT: f64 = 50.0;

/// One registered orthographic camera.
#[derive(Clone, Copy, Debug)]
pub struct Pose {
    pub cam: [Num; 3],
    pub target: [Num; 3],
    pub span: Num,
    pub size: [Num; 2],
}
impl ToVal for Pose {
    fn to_val(&self) -> Val {
        dict![
            "cam" => self.cam,
            "target" => self.target,
            "span" => self.span,
            "size" => self.size,
        ]
    }
}
impl FromVal for Pose {
    fn from_val(v: &Val) -> Result<Self> {
        Ok(Pose {
            cam: FromVal::from_val(&v.k("cam")?)?,
            target: FromVal::from_val(&v.k("target")?)?,
            span: FromVal::from_val(&v.k("span")?)?,
            size: FromVal::from_val(&v.k("size")?)?,
        })
    }
}

/// A world point and the pixel it lands on.
#[derive(Clone, Copy, Debug)]
pub struct Anchor {
    pub world: [f64; 3],
    pub pixel: [f64; 2],
}
impl ToVal for Anchor {
    fn to_val(&self) -> Val {
        dict!["world" => self.world, "pixel" => self.pixel]
    }
}

/// The meshes a scene moves and by how much.
#[derive(Clone, Copy, Debug)]
pub struct Action {
    pub prefix: &'static str,
    pub translation: [Num; 3],
    pub expected: i64,
}
impl ToVal for Action {
    fn to_val(&self) -> Val {
        dict![
            "prefix" => self.prefix,
            "translation" => self.translation,
            "expected" => self.expected,
        ]
    }
}

/// One scene's registration record, as `metadata` returns it.
#[derive(Clone, Debug)]
pub struct Metadata {
    pub pose: Pose,
    pub source_step: String,
    pub source_mesh: String,
    pub source_mesh_sha256: String,
    pub pixels_per_mm: f64,
    pub crop: [i64; 4],
    pub action: Action,
    pub visible_axis_gap_mm: f64,
    pub insertion_axis: [i64; 3],
    pub points: Vec<(String, Anchor)>,
}
impl ToVal for Metadata {
    fn to_val(&self) -> Val {
        let mut points = Dict::new();
        for (key, anchor) in &self.points {
            points.set(key.as_str(), anchor);
        }
        dict![
            "cam" => self.pose.cam,
            "target" => self.pose.target,
            "span" => self.pose.span,
            "size" => self.pose.size,
            "source_step" => self.source_step.as_str(),
            "source_mesh" => self.source_mesh.as_str(),
            "source_mesh_sha256" => self.source_mesh_sha256.as_str(),
            "projection" => "orthographic",
            "up" => [0i64, 0, 1],
            "trim" => false,
            "pixel_origin" => "top-left",
            "pixels_per_mm" => self.pixels_per_mm,
            "crop" => self.crop,
            "action" => self.action,
            "visible_axis_gap_mm" => self.visible_axis_gap_mm,
            "insertion_axis" => self.insertion_axis,
            "points" => points,
        ]
    }
}

pub struct State {
    pub argparse: Val,
    pub hashlib: Val,
    pub json: Val,
    pub math: Val,
    /// `pathlib.Path`, as the runtime constructs it.
    pub path: Val,
    pub r#struct: Val,
    pub sys: Val,
    /// `PIL.Image`.
    pub image: Val,
    pub root: PathBuf,
    pub hardware: PathBuf,
    pub snapshots: PathBuf,
    pub out: PathBuf,
    pub art: PathBuf,
    pub hsm_render: Val,
    pub machine_facts: Val,
    pub power_x: Num,
    pub power_z: Num,
    pub rear_y: Num,
    pub poses: OMap<Pose>,
}
impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let argparse = rt.import_module("argparse")?;
        let hashlib = rt.import_module("hashlib")?;
        let json = rt.import_module("json")?;
        let math = rt.import_module("math")?;
        rt.import_module("pathlib")?;
        let path = member(rt, "pathlib", "Path")?;
        let r#struct = rt.import_module("struct")?;
        let sys = rt.import_module("sys")?;
        rt.import_module("PIL")?;
        let image = member(rt, "PIL", "Image")?;
        let root = parent_n(&resolve(&rt.file(NAME)), 2);
        let hardware = root.join("hardware");
        let snapshots = hardware.join("install-guide/out");
        let out = snapshots.join("insertion-actions");
        let art = hardware.join("install-guide/art/insertion-actions");
        rt.sys_path_insert(0, &hardware.join("scripts"))?;
        let hsm_render = rt.import_module("_hsm_render")?;
        let machine_facts = json_loads(&read_text(
            &hardware.join("manifold-layout/enclosure-assembly.facts.json"),
        )?)?;
        let (power_x, power_z): (Num, Num) =
            FromVal::from_val(&machine_facts.k("constants")?.k("C14_STATION")?)?;
        let rear_y = Num::from_val(&machine_facts.k("box")?.k("outer")?.i(3)?)?;
        let mut poses = OMap::new();
        poses.set(
            "power-ready",
            Pose {
                cam: [F(0.85).neg(), I(1), F(0.25)],
                target: [power_x.sub(8), rear_y.add(34), power_z.sub(16)],
                span: I(64),
                size: [I(1800), I(1300)],
            },
        );
        poses.set(
            "fill-ready",
            Pose {
                cam: [F(0.65), I(1).neg(), F(0.5)],
                target: [I(0), I(140), I(465)],
                span: I(265),
                size: [I(1600), I(1500)],
            },
        );
        Ok(Self {
            argparse,
            hashlib,
            json,
            math,
            path,
            r#struct,
            sys,
            image,
            root,
            hardware,
            snapshots,
            out,
            art,
            hsm_render,
            machine_facts,
            power_x,
            power_z,
            rear_y,
            poses,
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

/// `str(n)` of a Python number.
fn num_str(n: Num) -> String {
    match n {
        I(i) => i.to_string(),
        F(x) => pystr(x),
    }
}

/// `path.mkdir(parents=True, exist_ok=True)`, as the runtime runs it.
fn mkdir(path: &Path) -> Result<()> {
    match std::fs::create_dir_all(path) {
        Err(e) if e.kind() != std::io::ErrorKind::AlreadyExists => Err(e.into()),
        _ => Ok(()),
    }
}

/// `tuple(value / length for value in vector)` with `length` the vector's Euclidean norm.
pub fn unit(vector: &[f64]) -> Result<Vec<f64>> {
    let length = fsum(vector.iter().map(|value| value * value)).sqrt();
    ensure!(length != 0., "division by zero");
    Ok(vector.iter().map(|value| value / length).collect())
}

/// The top-left-origin pixel a world point lands on in the pose's orthographic picture.
pub fn pixel(point: &[f64], pose: &Pose) -> Result<[f64; 2]> {
    let direction = unit(&pose.cam.map(Num::f))?;
    let right = unit(&[-direction[1], direction[0], 0.])?;
    let up = [
        direction[1] * right[2] - direction[2] * right[1],
        direction[2] * right[0] - direction[0] * right[2],
        direction[0] * right[1] - direction[1] * right[0],
    ];
    let delta: Vec<f64> = point
        .iter()
        .zip(pose.target)
        .map(|(value, target)| value - target.f())
        .collect();
    let [width, height] = pose.size.map(Num::f);
    let twice = I(2).mul(pose.span).f();
    ensure!(twice != 0., "division by zero");
    let scale = height / twice;
    Ok([
        width / 2. + fsum(delta.iter().zip(&right).map(|(value, axis)| value * axis)) * scale,
        height / 2. - fsum(delta.iter().zip(&up).map(|(value, axis)| value * axis)) * scale,
    ])
}

/// `_guide_native.mesh_bounds(path)`: each mesh's name and its `(min, max)` corners.
pub fn mesh_bounds(rt: &Runtime, path: &Path) -> Result<Val> {
    rt.native("mesh_bounds")?.c(args![path.to_path_buf()])
}

/// One mesh's `(min, max)` corners from a `mesh_bounds` result.
fn corners(bounds: &Val, name: &str) -> Result<([f64; 3], [f64; 3])> {
    let (lo, hi): (Val, Val) = FromVal::from_val(&bounds.k(name)?)?;
    Ok((lo.v3()?, hi.v3()?))
}

pub fn anchor(point: [f64; 3], pose: &Pose) -> Result<Anchor> {
    Ok(Anchor {
        world: point,
        pixel: pixel(&point, pose)?,
    })
}

pub fn metadata(rt: &Runtime, name: &str) -> Result<Metadata> {
    let st = state(rt)?;
    let pose = *st.poses.at(name)?;
    let source = if name == "power-ready" {
        "power-ready"
    } else {
        "fill-seated"
    };
    let step = st.snapshots.join(format!("{source}.step"));
    let mesh = step.with_extension("step.mesh");
    let bounds = mesh_bounds(rt, &mesh)?;
    let points: Vec<(&str, [f64; 3])>;
    let action;
    let crop;
    let gap;
    let axis;
    if name == "power-ready" {
        let (plug_min, plug_max) = corners(&bounds, "cordset/1")?;
        let x = (plug_min[0] + plug_max[0]) / 2.;
        let z = (plug_min[2] + plug_max[2]) / 2.;
        let front_y = plug_min[1] + POWER_RETREAT;
        let body_y = (plug_min[1] + plug_max[1]) / 2. + POWER_RETREAT;
        let socket_y = corners(&bounds, "c14-inlet")?.1[1];
        points = vec![
            ("connector-mouth", [x, front_y, z]),
            ("connector-body", [x, body_y, z]),
            ("connector-body-top", [x, body_y, plug_max[2]]),
            ("connector-body-side", [plug_min[0], body_y, z]),
            ("socket-mouth", [x, socket_y, z]),
            ("arrow-start", [plug_min[0], body_y, z]),
            ("arrow-end", [plug_min[0], socket_y + 18., z]),
        ];
        action = Action {
            prefix: "cordset",
            translation: [I(0), F(POWER_RETREAT), I(0)],
            expected: 3,
        };
        crop = [0, 160, 1800, 1140];
        gap = front_y - socket_y;
        axis = [0, -1, 0];
    } else {
        let (neck_min, neck_max) = corners(&bounds, "bottle-neck")?;
        let (body_min, body_max) = corners(&bounds, "bottle-body")?;
        let x = (neck_min[0] + neck_max[0]) / 2.;
        let y = (neck_min[1] + neck_max[1]) / 2.;
        let radius = (body_max[0] - body_min[0]) / 2.;
        let facing = unit(&[pose.cam[0].f(), pose.cam[1].f(), 0.])?;
        let (surface_x, surface_y) = (x + radius * facing[0], y + radius * facing[1]);
        let mouth_z = neck_min[2] + BOTTLE_LIFT;
        let rim_z = corners(&bounds, "funnel")?.1[2];
        points = vec![
            ("bottle-mouth", [x, y, mouth_z]),
            (
                "bottle-body",
                [
                    surface_x,
                    surface_y,
                    (body_min[2] + body_max[2]) / 2. + BOTTLE_LIFT,
                ],
            ),
            (
                "bottle-top",
                [x, y, corners(&bounds, "bottle-base")?.1[2] + BOTTLE_LIFT],
            ),
            ("funnel-mouth", [x, y, rim_z]),
            (
                "arrow-start",
                [surface_x, surface_y, body_max[2] + BOTTLE_LIFT - 35.],
            ),
            (
                "arrow-end",
                [surface_x, surface_y, body_min[2] + BOTTLE_LIFT + 24.],
            ),
        ];
        action = Action {
            prefix: "bottle-",
            translation: [I(0), I(0), F(BOTTLE_LIFT)],
            expected: 4,
        };
        crop = [290, 190, 1550, 1500];
        gap = mouth_z - rim_z;
        axis = [0, 0, -1];
    }
    let source_step = ps(step.strip_prefix(&st.root)?);
    let source_mesh = ps(mesh.strip_prefix(&st.root)?);
    hsm_documents::interop::note_io(&mesh, false);
    let bytes = std::fs::read(&mesh).with_context(|| format!("read {}", mesh.display()))?;
    let source_mesh_sha256 = st
        .hashlib
        .a("sha256")?
        .c(vec![Val::Bytes(bytes)])?
        .m("hexdigest", vec![])?
        .s()?;
    let twice = I(2).mul(pose.span).f();
    ensure!(twice != 0., "division by zero");
    let pixels_per_mm = pose.size[1].f() / twice;
    let anchors = points
        .into_iter()
        .map(|(key, value)| Ok((key.to_owned(), anchor(value, &pose)?)))
        .collect::<Result<Vec<_>>>()?;
    Ok(Metadata {
        pose,
        source_step,
        source_mesh,
        source_mesh_sha256,
        pixels_per_mm,
        crop,
        action,
        visible_axis_gap_mm: gap,
        insertion_axis: axis,
        points: anchors,
    })
}

/// `_guide_native.moved_payload(name, entry, ROOT, OUT)`: a render-only copy of the frozen payload
/// with the moving meshes translated. It records `render_mesh`, `render_mesh_sha256` and
/// `moved_meshes` in `entry` and returns the copy's path.
pub fn moved_payload(rt: &Runtime, name: &str, entry: &Val) -> Result<Val> {
    let st = state(rt)?;
    rt.native("moved_payload")?.c(args![
        name,
        entry.clone(),
        st.root.clone(),
        st.out.clone()
    ])
}

/// `_guide_native.registration(entry, report)`: the anchor pixels from the matrix the GPU picture
/// was drawn with.
pub fn registration(rt: &Runtime, entry: &Val, report: &Val) -> Result<Val> {
    rt.native("registration")?
        .c(args![entry.clone(), report.clone()])
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let st = state(rt)?;
    ns.value("argparse", st.argparse.clone());
    ns.value("hashlib", st.hashlib.clone());
    ns.value("json", st.json.clone());
    ns.value("math", st.math.clone());
    ns.value("Path", st.path.clone());
    ns.value("struct", st.r#struct.clone());
    ns.value("sys", st.sys.clone());
    ns.value("Image", st.image.clone());
    ns.value("ROOT", st.root.clone());
    ns.value("HARDWARE", st.hardware.clone());
    ns.value("SNAPSHOTS", st.snapshots.clone());
    ns.value("OUT", st.out.clone());
    ns.value("ART", st.art.clone());
    ns.value("_hsm_render", st.hsm_render.clone());
    ns.value("POWER_RETREAT", POWER_RETREAT);
    ns.value("BOTTLE_LIFT", BOTTLE_LIFT);
    ns.value("_machine_facts", st.machine_facts.clone());
    ns.value("_power_x", st.power_x);
    ns.value("_power_z", st.power_z);
    ns.value("_rear_y", st.rear_y);
    ns.value("POSES", &st.poses);
    ns.func(rt, "unit", |_rt, c| {
        let vector: Vec<f64> = c.req(0, "vector")?;
        Ok(tuple(&unit(&vector)?))
    });
    ns.func(rt, "pixel", |_rt, c| {
        let point: Vec<f64> = c.req(0, "point")?;
        let pose: Pose = c.req(1, "pose")?;
        Ok(pixel(&point, &pose)?.to_val())
    });
    ns.func(rt, "mesh_bounds", |rt, c| {
        let path: PathBuf = c.req(0, "path")?;
        mesh_bounds(rt, &path)
    });
    ns.func(rt, "anchor", |_rt, c| {
        let point: Val = c.req(0, "point")?;
        let pose: Pose = c.req(1, "pose")?;
        let pixel = pixel(&point.floats()?, &pose)?;
        Ok(dict!["world" => point, "pixel" => pixel])
    });
    ns.func(rt, "metadata", |rt, c| {
        let name: String = c.req(0, "name")?;
        Ok(metadata(rt, &name)?.to_val())
    });
    ns.func(rt, "moved_payload", |rt, c| {
        let name: String = c.req(0, "name")?;
        let entry: Val = c.req(1, "entry")?;
        moved_payload(rt, &name, &entry)
    });
    ns.func(rt, "registration", |rt, c| {
        let entry: Val = c.req(0, "entry")?;
        let report: Val = c.req(1, "report")?;
        registration(rt, &entry, &report)
    });
    ns.func(rt, "main", |rt, _c| {
        main(rt)?;
        Ok(Val::None)
    });
    Ok(())
}

/// One requested scene: its typed record and the dict `moved_payload` and the render fill in.
#[derive(Clone)]
struct Scene {
    meta: Metadata,
    entry: Val,
}

pub fn main(rt: &Runtime) -> Result<()> {
    let st = state(rt)?;
    let doc = super::table::documentation(NAME).unwrap_or("");
    let parser = st
        .argparse
        .a("ArgumentParser")?
        .ck(vec![], kw!["description" => doc])?;
    let choices: Vec<&str> = st.poses.keys().collect();
    parser.mk(
        "add_argument",
        args!["scenes"],
        kw!["nargs" => "*", "choices" => choices],
    )?;
    parser.mk(
        "add_argument",
        args!["--stage-only"],
        kw!["action" => "store_true"],
    )?;
    let args = parser.m("parse_args", vec![])?;
    mkdir(&st.out)?;
    mkdir(&st.art)?;
    let requested = args.a("scenes")?;
    let names: Vec<String> = if requested.truthy()? {
        FromVal::from_val(&requested)?
    } else {
        st.poses.keys().map(str::to_owned).collect()
    };
    let mut entries: OMap<Scene> = OMap::new();
    for name in &names {
        let meta = metadata(rt, name)?;
        let entry = meta.to_val();
        entries.set(name, Scene { meta, entry });
    }
    let mut jobs = vec![];
    for (name, scene) in entries.iter() {
        let payload = moved_payload(rt, name, &scene.entry)?;
        let pose = scene.meta.pose;
        let size: Vec<String> = pose.size.iter().map(|&n| num_str(n)).collect();
        jobs.push(dict![
            "step" => ps(Path::new(&scene.meta.source_step).strip_prefix("hardware")?),
            "payload" => payload.str()?,
            "out" => ps(&st.art.join(format!("{name}.png"))),
            "cam" => pose.cam,
            "target" => pose.target,
            "span" => pose.span,
            "size" => size.join("x"),
            "up" => [0i64, 0, 1],
            "bg" => "#f2eee8",
            "transparent" => true,
            "solid" => true,
            "ortho" => true,
            "trim" => false,
            "ground" => false,
            "fog" => false,
        ]);
    }
    let jobs = Val::list(jobs);
    let manifest = st.out.join("scenes.json");
    write_text(
        &manifest,
        &(json_dumps(&jobs, kw!["indent" => 2i64])? + "\n"),
    )?;
    if !args.a("stage_only")?.truthy()? {
        let reports = st
            .hsm_render
            .mk("render", vec![jobs.clone()], kw!["reports" => true])?
            .list()?;
        ensure!(
            reports.len() == entries.len(),
            "zip argument lengths differ"
        );
        for ((name, scene), report) in entries.iter().zip(&reports) {
            let opened = st
                .image
                .m("open", args![st.art.join(format!("{name}.png"))])?;
            with(&opened, |rendered| {
                let mode = rendered.a("mode")?;
                ensure!(
                    matches!(&mode, Val::Str(m) if m == "RGBA"),
                    "assertion failed"
                );
                let size = rendered.a("size")?.floats()?;
                ensure!(
                    size == scene.meta.pose.size.map(Num::f),
                    "assertion failed"
                );
                let bounds = rendered
                    .m("getchannel", args!["A"])?
                    .m("getbbox", vec![])?;
                scene.entry.set("alpha_bounds".into(), bounds)?;
                Ok(())
            })?;
            let measured_registration = registration(rt, &scene.entry, report)?;
            write_text(
                &st.out.join(format!("{name}.render.json")),
                &(json_dumps(&measured_registration, kw!["indent" => 2i64])? + "\n"),
            )?;
            for (point, anchor_entry) in &scene.meta.points {
                let measured = measured_registration.k("points")?.k(point)?.floats()?;
                let errors: Vec<f64> = measured
                    .iter()
                    .zip(anchor_entry.pixel)
                    .map(|(a, b)| (a - b).abs())
                    .collect();
                ensure!(!errors.is_empty(), "max() arg is an empty sequence");
                ensure!(fmax(errors) < 1e-05, "assertion failed");
            }
        }
    }
    let scenes: OMap<Val> = OMap(
        entries
            .iter()
            .map(|(name, scene)| (name.to_owned(), scene.entry.clone()))
            .collect(),
    );
    let anchors = st.out.join("anchors.json");
    write_text(
        &anchors,
        &(json_dumps(&dict!["scenes" => scenes], kw!["indent" => 2i64])? + "\n"),
    )?;
    rt.print(ps(&anchors))?;
    Ok(())
}
