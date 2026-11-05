//! Guide recipe `_install_art`: the shared installation scene builders and presentation props.
//!
//! Each scene is a CadQuery assembly in the appliance's own frame (X across the front, Y from the
//! front face back, Z up from the cabinet floor). `render` stages the scenes through
//! `_install_art_mesh`'s payloads and draws them with `_hsm_render` into `art/`.

use super::*;
use std::path::{Path, PathBuf};
use std::rc::Rc;

pub const NAME: &str = "_install_art";

pub const BOX_X0: f64 = -113.5;
pub const BOX_X1: f64 = 107.5;
pub const BOX_Y0: f64 = 5.0;
pub const BOX_Y1: f64 = 467.0;
pub const BOX_Z0: f64 = -6.0;
pub const BOX_Z1: f64 = 361.0;
pub const PORT_FACE_Y: f64 = 476.5;
pub const PORT_Z_UPPER: f64 = 336.2;
pub const PORT_Z_LOWER: f64 = 273.8;
pub const PORT_X_WEST: f64 = -78.1;
pub const PORT_X_EAST: f64 = -37.8;
/// The clearances page 7 asks the reader to leave, behind and at each side.
pub const CLEAR_BEHIND: f64 = 60.0;
pub const CLEAR_SIDE: f64 = 40.0;
pub const CYLINDER_LANE: f64 = 133.0;
/// Catalogue sizes for the things with no CAD.
pub const CYLINDER_D: f64 = 133.0;
pub const CYLINDER_H: f64 = 457.0;
pub const FILTER_D: f64 = 63.0;
pub const FILTER_L: f64 = 311.0;
pub const BOTTLE_D: f64 = 72.0;
pub const BOTTLE_H: f64 = 190.0;
pub const BOTTLE_NECK_D: f64 = 27.0;
pub const BOTTLE_NECK_H: f64 = 34.0;
pub const TUBE_D: f64 = 6.35;
/// The bottle poured from the front, tipped this far past level, its lowest point this far over
/// the funnel's brim.
pub const BOTTLE_TIP: f64 = 20.0;
pub const BOTTLE_CLEARANCE: f64 = 3.0;
/// The bodies of the machine payload a customer standing behind the machine can see.
pub const REAR_CHILDREN: [&str; 14] = [
    "bulkhead-drain",
    "c14-inlet",
    "keystone-jack",
    "co2-inlet",
    "bulkhead-water",
    "bulkhead-carb",
    "bulkhead-flavor-a",
    "bulkhead-flavor-b",
    "funnel",
    "funnel-cover",
    "nameplate",
    "nameplate-ink",
    "enclosure-back-bottom",
    "enclosure-back-top",
];
pub const REAR_RING_PREFIX: &str = "bulkhead-ring-";
/// The customer's C13 cordset: the inlet's shroud plus a slip, and a moulded 18 AWG cord.
pub const C13_SLIP: f64 = 0.35;
pub const C13_WALL: f64 = 3.5;
pub const C13_BODY_LEN: f64 = 31.0;
pub const C13_NOSE_LEN: f64 = 9.5;
pub const C13_BOOT_LEN: f64 = 30.0;
pub const C13_BOOT_D: (f64, f64) = (14.5, 9.0);
pub const C13_CABLE_D: f64 = 7.8;
/// The plate's stand-off along the slide, from its seat.
pub const PLATE_STANDOFF_X: f64 = -44.0;
/// The washer and nut the faucet ships with.
pub const WASHER_T: f64 = 1.5;
pub const NUT_H: f64 = 5.0;
/// How far past the push-fit's mouth the factory-fitted tether ends.
pub const TETHER_IN_MOUTH: f64 = 4.0;

/// `SCENES` in order: each scene's name and the function that builds it, if any.
pub const SCENES: [(&str, Option<&str>); 17] = [
    ("cabinet-plan", Some("s_cabinet_plan")),
    ("opening", Some("s_opening")),
    ("filter-in-cabinet", Some("s_filter_in_cabinet")),
    ("two-tees", None),
    ("nameplate", Some("s_nameplate")),
    ("plate-sideways", Some("s_plate_sideways")),
    ("stop-open", None),
    ("stop-closed", None),
    ("tee-before", None),
    ("tee-after", None),
    ("bottle-in-funnel", Some("s_bottle_in_funnel")),
    ("kitchen-push", None),
    ("kitchen-hose", None),
    ("regulator", Some("s_regulator")),
    ("collet-press", Some("s_collet_press")),
    ("the-back-face", Some("s_the_back_face")),
    ("the-socket", Some("s_the_socket")),
];

pub struct State {
    pub os: Val,
    pub sys: Val,
    pub tempfile: Val,
    pub here: PathBuf,
    pub hardware: PathBuf,
    pub root: PathBuf,
    pub art: PathBuf,
    pub out: PathBuf,
    pub cq: Val,
    pub import_step: Val,
    pub note_read: Val,
    pub note_write: Val,
    pub xz_plane_y_up: Val,
    pub c14: Val,
    pub cad_art: Val,
    pub hsm_render: Val,
    pub machine_mesh: Val,
    pub machine_facts: Val,
    pub collet_press: PathBuf,
    pub regulator_dir: PathBuf,
    pub plumbing_dir: PathBuf,
    pub modern_dir: PathBuf,
    pub c14_source: PathBuf,
    /// `facts["bodies"]["funnel"]`: the funnel's bounds, to the brim.
    pub funnel_bounds: Val,
    /// `tuple(facts["box"]["funnel"])`: the funnel's mouth in plan.
    pub funnel_mouth: Val,
    pub stone: Val,
    pub cabinet: Val,
    pub coral: Val,
    pub steel: Val,
    pub brass: Val,
    pub white_tube: Val,
    pub red_tube: Val,
    pub blue_tube: Val,
    pub black_part: Val,
    pub concentrate: Val,
    pub bottle_pet: Val,
    pub filter_body: Val,
    pub filter_cap: Val,
    pub printed: Val,
    pub cylinder: Val,
    pub acetal_gray: Val,
    pub rear_children: Val,
    /// `enclosure-assembly.facts.json`.
    pub facts: Val,
    /// The show face: the wall's +Y plane.
    pub rear_face_y: Val,
    pub c14_station: Val,
    pub cordset: Val,
    pub nut_steel: Val,
    pub plate_steel: Val,
    pub black_part_lit: Val,
}

fn color(cq: &Val, r: f64, g: f64, b: f64) -> Result<Val> {
    cq.a("Color")?.c(args![r, g, b, 1.0])
}

impl State {
    fn facts_path(&self) -> Result<PathBuf> {
        PathBuf::from_val(&self.machine_facts)
    }
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let os = rt.py("os")?;
        let sys = rt.py("sys")?;
        let tempfile = rt.py("tempfile")?;
        let here = resolve(&rt.file(NAME))
            .parent()
            .context("module directory")?
            .to_owned();
        let hardware = ancestor(&here, "hardware")?;
        let root = hardware.parent().unwrap_or(&hardware).to_owned();
        let art = here.join("art");
        let out = here.join("out");
        rt.sys_path_insert(0, &hardware.join("scripts"))?;
        rt.sys_path_insert(0, &hardware.join("install-guide"))?;
        rt.sys_path_insert(0, &hardware.join("printed-parts").join("cadlib"))?;
        rt.sys_path_insert(0, &hardware.join("reference").join("iec-c14-inlet"))?;
        let cq = rt.py("cadquery")?;
        rt.py("_cadq_export")?;
        let import_step = rt.pya("_cadq_export", "import_step")?;
        let note_read = rt.pya("_cadq_export", "note_read")?;
        let note_write = rt.pya("_cadq_export", "note_write")?;
        rt.py("world_workplane")?;
        let xz_plane_y_up = rt.pya("world_workplane", "xz_plane_y_up")?;
        let c14 = rt.py("iec_c14_inlet")?;
        let cad_art = rt.import_module("_cad_art")?; // via namespace: _cad_art
        let hsm_render = rt.py("_hsm_render")?;
        let machine_mesh = cad_art.a("MACHINE_MESH")?; // via namespace: _cad_art
        let machine_facts = cad_art.a("MACHINE_FACTS")?; // via namespace: _cad_art
        let collet_press = hardware
            .join("printed-parts")
            .join("collet-press")
            .join("collet-press.step");
        let regulator_dir = hardware.join("reference").join("taprite-3741-regulator");
        let plumbing_dir = hardware.join("install-guide").join("plumbing");
        let modern_dir = plumbing_dir.join("modern");
        let c14_source = resolve(&PathBuf::from(c14.a("__file__")?.s()?));
        let facts_path = PathBuf::from_val(&machine_facts)?;
        let funnel_bounds = json_loads(&read_text(&facts_path)?)?
            .k("bodies")?
            .k("funnel")?;
        let funnel_mouth = Val::Tuple(
            json_loads(&read_text(&facts_path)?)?
                .k("box")?
                .k("funnel")?
                .list()?,
        );
        let stone = color(&cq, 0.55, 0.55, 0.58)?;
        let cabinet = color(&cq, 0.74, 0.7, 0.64)?;
        let coral = color(&cq, 0.84, 0.25, 0.31)?;
        let steel = color(&cq, 0.78, 0.79, 0.82)?;
        let brass = color(&cq, 0.72, 0.58, 0.28)?;
        let white_tube = color(&cq, 0.9, 0.9, 0.93)?;
        let red_tube = color(&cq, 0.78, 0.2, 0.2)?;
        let blue_tube = color(&cq, 0.16, 0.4, 0.75)?;
        let black_part = color(&cq, 0.1, 0.1, 0.12)?;
        let concentrate = color(&cq, 0.3, 0.1, 0.13)?;
        let bottle_pet = color(&cq, 0.86, 0.87, 0.9)?;
        let filter_body = color(&cq, 0.905, 0.915, 0.94)?;
        let filter_cap = color(&cq, 0.42, 0.45, 0.49)?;
        let printed = color(&cq, 0.26, 0.27, 0.3)?;
        let cylinder = color(&cq, 0.4, 0.42, 0.47)?;
        let acetal_gray = color(&cq, 0.43, 0.44, 0.43)?;
        let rear_children = Val::frozen_set(REAR_CHILDREN.iter().map(|c| Val::Str((*c).into())).collect());
        let facts = json_loads(&read_text(&facts_path)?)?;
        let rear_face_y = facts.k("box")?.k("outer")?.i(3)?;
        let c14_station = Val::Tuple(facts.k("constants")?.k("C14_STATION")?.list()?);
        let cordset = color(&cq, 0.035, 0.038, 0.043)?;
        let nut_steel = color(&cq, 0.43, 0.45, 0.48)?;
        let plate_steel = color(&cq, 0.91, 0.92, 0.94)?;
        let black_part_lit = color(&cq, 0.2, 0.205, 0.215)?;
        Ok(State {
            os,
            sys,
            tempfile,
            here,
            hardware,
            root,
            art,
            out,
            cq,
            import_step,
            note_read,
            note_write,
            xz_plane_y_up,
            c14,
            cad_art,
            hsm_render,
            machine_mesh,
            machine_facts,
            collet_press,
            regulator_dir,
            plumbing_dir,
            modern_dir,
            c14_source,
            funnel_bounds,
            funnel_mouth,
            stone,
            cabinet,
            coral,
            steel,
            brass,
            white_tube,
            red_tube,
            blue_tube,
            black_part,
            concentrate,
            bottle_pet,
            filter_body,
            filter_cap,
            printed,
            cylinder,
            acetal_gray,
            rear_children,
            facts,
            rear_face_y,
            c14_station,
            cordset,
            nut_steel,
            plate_steel,
            black_part_lit,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

pub fn box_mid_x() -> f64 {
    (BOX_X0 + BOX_X1) / 2.0
}

/// Python's `abs` on an int or a float.
fn num_abs(n: Num) -> Num {
    match n {
        Num::I(i) => Num::I(i.abs()),
        Num::F(x) => Num::F(x.abs()),
    }
}

/// `Path.mkdir(parents=True, exist_ok=True)`.
pub fn mkdirs(path: &Path) -> Result<()> {
    if let Err(error) = std::fs::create_dir_all(path) {
        if error.kind() != std::io::ErrorKind::AlreadyExists {
            return Err(error).with_context(|| format!("mkdir {}", path.display()));
        }
    }
    Ok(())
}

fn workplane(st: &State, origin: (Num, Num, Num)) -> Result<Val> {
    st.cq.a("Workplane")?.ck(args!["XY"], kw!["origin" => origin])
}

/// `_box`: a box with its low corner at (x0, y0, z0).
pub fn box_(rt: &Runtime, x0: Num, y0: Num, z0: Num, sx: Num, sy: Num, sz: Num) -> Result<Val> {
    let st = state(rt)?;
    workplane(&st, (x0, y0, z0))?.mk(
        "box",
        args![sx, sy, sz],
        kw!["centered" => (false, false, false)],
    )
}

fn turn(base: Val, x: Num, y: Num, z: Num, axis: &str) -> Result<Val> {
    match axis {
        "Z" => Ok(base),
        "Y" => base.m("rotate", args![(x, y, z), (x.add(1.0), y, z), -90.0]),
        _ => base.m("rotate", args![(x, y, z), (x, y.add(1.0), z), 90.0]),
    }
}

/// `_cyl`: a cylinder of `length` from (x, y, z) along `axis`.
pub fn cyl(rt: &Runtime, x: Num, y: Num, z: Num, d: f64, length: Num, axis: &str) -> Result<Val> {
    let st = state(rt)?;
    let base = workplane(&st, (x, y, z))?
        .m("circle", args![d / 2.0])?
        .m("extrude", args![length])?;
    turn(base, x, y, z, axis)
}

/// `_run`: a tube along axis-aligned segments, with a ball at each turn.
pub fn run_tube(rt: &Runtime, points: &[Val], diameter: f64) -> Result<Val> {
    let st = state(rt)?;
    let mut solid: Option<Val> = None;
    for pair in points.windows(2) {
        let a = Vec::<Num>::from_val(&pair[0])?;
        let b = Vec::<Num>::from_val(&pair[1])?;
        ensure!(
            a.len() >= 3 && b.len() >= 3,
            "IndexError: tuple index out of range"
        );
        let deltas: Vec<Num> = (0..3).map(|i| b[i].sub(a[i])).collect();
        let moving: Vec<usize> = (0..deltas.len())
            .filter(|&i| deltas[i].f().abs() > 1e-6)
            .collect();
        if moving.is_empty() {
            continue;
        }
        if moving.len() != 1 {
            bail!(
                "ValueError: {} -> {} is not axis-aligned",
                fv(&pair[0], "")?,
                fv(&pair[1], "")?
            );
        }
        let m = moving[0];
        let axis = ["X", "Y", "Z"][m];
        let length = deltas[m];
        let mut start = a.clone();
        if length.f() < 0.0 {
            start[m] = start[m].add(length);
        }
        let seg = cyl(rt, start[0], start[1], start[2], diameter, num_abs(length), axis)?;
        solid = Some(match solid {
            None => seg,
            Some(s) => s.m("union", vec![seg])?,
        });
    }
    if points.len() > 2 {
        for point in &points[1..points.len() - 1] {
            let ball = st
                .cq
                .a("Workplane")?
                .ck(args!["XY"], kw!["origin" => point.clone()])?
                .m("sphere", args![diameter / 2.0])?;
            solid = Some(match solid {
                None => ball,
                Some(s) => s.m("union", vec![ball])?,
            });
        }
    }
    Ok(solid.unwrap_or(Val::None))
}

/// `_unit`.
pub fn unit(vec: &[f64]) -> Vec<f64> {
    let mag = fsum(vec.iter().map(|c| c * c)).sqrt();
    vec.iter().map(|c| c / mag).collect()
}

fn vector(st: &State, values: &[Num]) -> Result<Val> {
    st.cq
        .a("Vector")?
        .c(values.iter().map(ToVal::to_val).collect())
}

/// `_bend`: a tube along axis-aligned segments whose corners are swept quarter arcs of
/// `radius`, sampled into stubs with a ball at each joint, as one compound.
pub fn bend(rt: &Runtime, points: &[[Num; 3]], diameter: f64, radius: f64, steps: i64) -> Result<Val> {
    let st = state(rt)?;
    let first = points.first().context("IndexError: list index out of range")?;
    let mut samples: Vec<Vec<Num>> = vec![first.to_vec()];
    for i in 1..points.len().saturating_sub(1) {
        let corner = points[i];
        let u = unit(&(0..3).map(|k| corner[k].sub(points[i - 1][k]).f()).collect::<Vec<_>>());
        let v = unit(&(0..3).map(|k| points[i + 1][k].sub(corner[k]).f()).collect::<Vec<_>>());
        if fsum((0..3).map(|k| u[k] * v[k])).abs() > 1e-6 {
            bail!("ValueError: a bend turns a square corner");
        }
        let centre: Vec<f64> = (0..3)
            .map(|k| (corner[k].f() - u[k] * radius) + v[k] * radius)
            .collect();
        for step in 0..steps + 1 {
            let t = ((std::f64::consts::PI / 2.0) * step as f64) / steps as f64;
            samples.push(
                (0..3)
                    .map(|k| Num::F(centre[k] + radius * ((-v[k]) * t.cos() + u[k] * t.sin())))
                    .collect(),
            );
        }
    }
    samples.push(points[points.len() - 1].to_vec());
    let mut pieces = vec![];
    for pair in samples.windows(2) {
        let (a, b) = (&pair[0], &pair[1]);
        let span = st
            .cq
            .a("Vector")?
            .c(args![b[0].sub(a[0]), b[1].sub(a[1]), b[2].sub(a[2])])?;
        if span.a("Length")?.f()? < 1e-9 {
            continue;
        }
        pieces.push(st.cq.a("Solid")?.m(
            "makeCylinder",
            vec![
                Val::Float(diameter / 2.0),
                span.a("Length")?,
                vector(&st, a)?,
                span.m("normalized", vec![])?,
            ],
        )?);
    }
    for point in &samples[1..samples.len() - 1] {
        pieces.push(st.cq.a("Solid")?.mk(
            "makeSphere",
            vec![Val::Float(diameter / 2.0), vector(&st, point)?],
            kw!["angleDegrees1" => -90.0],
        )?);
    }
    st.cq
        .a("Compound")?
        .m("makeCompound", vec![Val::list(pieces)])
}

/// `_add`: `assembly.add(shape, name=name, color=color)` when there is a shape.
pub fn add(assembly: &Val, shape: &Val, name: impl ToVal, color: &Val) -> Result<()> {
    if !matches!(shape, Val::None) {
        assembly.mk(
            "add",
            vec![shape.clone()],
            kw!["name" => name.to_val(), "color" => color.clone()],
        )?;
    }
    Ok(())
}

/// `_cad_art.borrow(assembly, _cad_art.machine_bodies(*keep))`.
fn borrow(st: &State, assembly: &Val, keep: Option<Val>) -> Result<Val> {
    let bodies = st.cad_art.m("machine_bodies", keep.into_iter().collect())?; // via namespace: _cad_art
    st.cad_art.m("borrow", vec![assembly.clone(), bodies]) // via namespace: _cad_art
}

/// `_machine`: the whole appliance with the colours its own payload carries.
pub fn machine(rt: &Runtime, assembly: &Val) -> Result<Val> {
    borrow(&state(rt)?, assembly, None)
}

/// `_hex`: a hexagonal prism of `across_flats`, from (x, y, z) along `axis`.
pub fn hex(
    rt: &Runtime,
    x: Num,
    y: Num,
    z: Num,
    across_flats: f64,
    length: Num,
    axis: &str,
) -> Result<Val> {
    let st = state(rt)?;
    let r = across_flats / 3.0f64.sqrt();
    let pts: Vec<Val> = (0..360)
        .step_by(60)
        .map(|a| (r * radians(a as f64).cos(), r * radians(a as f64).sin()).to_val())
        .collect();
    let base = workplane(&st, (x, y, z))?
        .m("polyline", vec![Val::list(pts)])?
        .m("close", vec![])?
        .m("extrude", args![length])?;
    turn(base, x, y, z, axis)
}

/// `_floor`: a slab of cabinet floor under the cabinet floor's plane.
pub fn floor(rt: &Runtime, x0: Num, y0: Num, sx: Num, sy: Num) -> Result<Val> {
    box_(rt, x0, y0, Num::F(-24.0), sx, sy, Num::F(18.0))
}

/// The `keep` of `_rear_face`: a rear-visible body or one of the bulkhead rings.
fn rear_keep() -> Val {
    Val::function(|args, kwargs| {
        let mut c = Call::new(args, kwargs);
        let name: Val = c.req(0, "name")?;
        c.done()?;
        if REAR_CHILDREN
            .iter()
            .any(|child| matches!(&name, Val::Str(s) if s == child))
        {
            return Ok(Val::Bool(true));
        }
        name.m("startswith", args![REAR_RING_PREFIX])
    })
}

/// `_rear_face`: the machine's rear-visible bodies, colours and all.
pub fn rear_face(rt: &Runtime, assembly: &Val) -> Result<Val> {
    borrow(&state(rt)?, assembly, Some(rear_keep()))
}

/// `_prism`: a rounded rectangular prism on the show face's own plane, running `length` in +Y.
pub fn prism(rt: &Runtime, w: Num, h: Num, r: Num, length: Num) -> Result<Val> {
    let st = state(rt)?;
    st.cq
        .a("Workplane")?
        .c(vec![st.xz_plane_y_up.clone()])?
        .m("rect", args![w, h])?
        .m("extrude", args![length])?
        .m("edges", args!["|Y"])?
        .m("fillet", args![r])
}

/// `_cable`: a round cord swept along a spline through `points`.
pub fn cable(rt: &Runtime, points: &[Vec<Val>], diameter: f64, tangents: &[Vec<Val>]) -> Result<Val> {
    let st = state(rt)?;
    let vectors = points
        .iter()
        .map(|point| st.cq.a("Vector")?.c(point.clone()))
        .collect::<Result<Vec<_>>>()?;
    let directions = tangents
        .iter()
        .map(|t| st.cq.a("Vector")?.c(t.clone()))
        .collect::<Result<Vec<_>>>()?;
    let path = st.cq.a("Edge")?.mk(
        "makeSpline",
        vec![Val::list(vectors.clone())],
        kw!["tangents" => Val::list(directions), "scale" => false],
    )?;
    let first = tangents.first().context("IndexError: tuple index out of range")?;
    let profile = st.cq.a("Wire")?.m(
        "makeCircle",
        vec![
            Val::Float(diameter / 2.0),
            vectors.first().context("IndexError: list index out of range")?.clone(),
            st.cq.a("Vector")?.c(first.clone())?,
        ],
    )?;
    st.cq.a("Solid")?.mk(
        "sweep",
        vec![profile, Val::list(vec![]), path],
        kw!["makeSolid" => true, "isFrenet" => false],
    )
}

fn floats(values: &[f64]) -> Vec<Val> {
    values.iter().map(|v| Val::Float(*v)).collect()
}

/// `_c13_cordset`: the cord end on the inlet's mating axis, `gap` millimetres out from the show
/// face: the nose, the moulding with its three contact slots, the strain relief and the cord.
pub fn c13_cordset(rt: &Runtime, gap: Num) -> Result<Val> {
    let st = state(rt)?;
    let station = st.c14_station.list()?;
    ensure!(station.len() == 2, "ValueError: C14_STATION unpacks to two values");
    let (x, z) = (station[0].clone(), station[1].clone());
    let y0 = Num::from_val(&st.rear_face_y)?.add(gap);
    let nose_w = st.c14.a("MOUTH_W")?.f()? - 2.0 * C13_SLIP;
    let nose_h = st.c14.a("MOUTH_H")?.f()? - 2.0 * C13_SLIP;
    let body = prism(
        rt,
        Num::F(nose_w + 2.0 * C13_WALL),
        Num::F(nose_h + 2.0 * C13_WALL),
        Num::F(3.0),
        Num::F(C13_BODY_LEN),
    )?;
    let body = body.m("faces", args![">Y"])?.m("chamfer", args![1.2])?;
    let nose = prism(
        rt,
        Num::F(nose_w),
        Num::F(nose_h),
        Num::F(st.c14.a("MOUTH_TOP_R")?.f()? - C13_SLIP),
        Num::F(C13_NOSE_LEN),
    )?
    .m("translate", args![(0.0, -C13_NOSE_LEN, 0.0)])?;
    let mut body = body.m("union", vec![nose])?;
    let blades = st
        .c14
        .m("build_blades", vec![])?
        .m("val", vec![])?
        .m("Solids", vec![])?
        .list()?;
    for blade in blades {
        let bb = blade.m("BoundingBox", vec![])?;
        let slot = box_(
            rt,
            Num::F(bb.a("xmin")?.f()? - 0.3),
            Num::F(-C13_NOSE_LEN - 0.5),
            Num::F(bb.a("zmin")?.f()? - 0.3),
            Num::F(bb.a("xlen")?.f()? + 0.6),
            Num::F((C13_NOSE_LEN + 0.5) + 6.0),
            Num::F(bb.a("zlen")?.f()? + 0.6),
        )?;
        body = body.m("cut", vec![slot])?;
    }
    let boot = st
        .cq
        .a("Workplane")?
        .c(vec![st.xz_plane_y_up.clone()])?
        .mk("workplane", vec![], kw!["offset" => C13_BODY_LEN])?
        .m("circle", args![C13_BOOT_D.0 / 2.0])?
        .mk("workplane", vec![], kw!["offset" => C13_BOOT_LEN])?
        .m("circle", args![C13_BOOT_D.1 / 2.0])?
        .m("loft", vec![])?;
    let tail = C13_BODY_LEN + C13_BOOT_LEN;
    let cord = cable(
        rt,
        &[
            floats(&[0.0, tail, 0.0]),
            floats(&[0.0, tail + 26.0, 0.0]),
            floats(&[7.0, tail + 48.0, -58.0]),
            floats(&[11.0, tail + 55.0, -175.0]),
        ],
        C13_CABLE_D,
        &[floats(&[0.0, 1.0, 0.0]), floats(&[0.0, 0.0, -1.0])],
    )?;
    let parts = Val::list(vec![body.m("val", vec![])?, boot.m("val", vec![])?, cord]);
    st.cq
        .a("Compound")?
        .m("makeCompound", vec![parts])?
        .m("translate", vec![Val::Tuple(vec![x, y0.to_val(), z])])
}

fn assembly(st: &State, name: &str) -> Result<Val> {
    st.cq.a("Assembly")?.ck(vec![], kw!["name" => name])
}

/// `s_cabinet_plan`: the slot the appliance stands in, with the clearances on the cabinet floor.
pub fn s_cabinet_plan(rt: &Runtime) -> Result<Val> {
    let st = state(rt)?;
    let a = assembly(&st, "cabinet-plan-scene")?;
    machine(rt, &a)?;
    let x0 = ((BOX_X0 - CLEAR_SIDE) - CYLINDER_LANE) - 30.0;
    let x1 = (BOX_X1 + CLEAR_SIDE) + 30.0;
    let slab = floor(
        rt,
        Num::F(x0),
        Num::F(BOX_Y0 - 40.0),
        Num::F(x1 - x0),
        Num::F(((BOX_Y1 - BOX_Y0) + CLEAR_BEHIND) + 80.0),
    )?;
    add(&a, &slab, "cabinet-floor", &st.cabinet)?;
    let pads = [
        ("behind", BOX_X0, BOX_Y1, BOX_X1 - BOX_X0, CLEAR_BEHIND),
        ("side-west", BOX_X0 - CLEAR_SIDE, BOX_Y0, CLEAR_SIDE, BOX_Y1 - BOX_Y0),
        ("side-east", BOX_X1, BOX_Y0, CLEAR_SIDE, BOX_Y1 - BOX_Y0),
    ];
    for (name, px, py, sx, sy) in pads {
        let pad = box_(
            rt,
            Num::F(px),
            Num::F(py),
            Num::F(-6.0),
            Num::F(sx),
            Num::F(sy),
            Num::F(10.0),
        )?;
        add(&a, &pad, format!("clear-{name}"), &st.coral)?;
    }
    let cx = (BOX_X0 - CLEAR_SIDE) - CYLINDER_LANE / 2.0;
    let bottle = cyl(
        rt,
        Num::F(cx),
        Num::F(BOX_Y0 + 150.0),
        Num::F(-6.0),
        CYLINDER_D,
        Num::F(CYLINDER_H),
        "Z",
    )?;
    add(&a, &bottle, "co2-cylinder", &st.cylinder)?;
    Ok(a)
}

/// The countertop slab with the faucet's hole through it: `centre` shifts the slab in plan.
fn slab(st: &State, fa: &Val, centre: Option<(f64, f64)>, size: (f64, f64)) -> Result<Val> {
    let mut top = st
        .cq
        .a("Workplane")?
        .c(args!["XY"])?
        .mk("workplane", vec![], kw!["offset" => fa.a("countertop_bottom_z")?])?;
    if let Some((cx, cy)) = centre {
        top = top.m("center", args![cx, cy])?;
    }
    let top = top.mk(
        "box",
        args![size.0, size.1, fa.a("countertop_thickness")?],
        kw!["centered" => (true, true, false)],
    )?;
    let hole = st
        .cq
        .a("Workplane")?
        .c(args!["XY"])?
        .mk(
            "workplane",
            vec![],
            kw!["offset" => fa.a("countertop_bottom_z")?.f()? - 1.0],
        )?
        .m("center", args![0.0, fa.a("countertop_hole_center_y")?])?
        .m("circle", args![fa.a("hole_radius")?])?
        .m("extrude", args![fa.a("countertop_thickness")?.f()? + 2.0])?;
    top.m("cut", vec![hole])
}

/// The faucet module and its assembly's children by name.
fn faucet_parts(st: &State) -> Result<(Val, Val)> {
    let fa = st.cad_art.m("_load_faucet_module", vec![])?; // via namespace: _cad_art
    let built = fa.m("build_assembly", vec![])?;
    let parts = st.cad_art.m("_children_by_name", vec![built])?; // via namespace: _cad_art
    Ok((fa, parts))
}

fn clip_z(st: &State, shape: Val, z0: f64, z1: f64) -> Result<Val> {
    st.cad_art.m("_clip_z", args![shape, z0, z1]) // via namespace: _cad_art
}

/// `s_opening`: the one cut, from above, with what it has to accept over it.
pub fn s_opening(rt: &Runtime) -> Result<Val> {
    let st = state(rt)?;
    let (fa, parts) = faucet_parts(&st)?;
    let a = assembly(&st, "opening-scene")?;
    let countertop = slab(&st, &fa, None, (320.0, 210.0))?;
    add(&a, &countertop, "countertop", &st.stone)?;
    let lift = 128.0;
    for (name, colour) in [
        ("flavor_tube_pos_x", &st.black_part),
        ("flavor_tube_neg_x", &st.black_part),
        ("soda_umbilical_tube", &st.blue_tube),
        ("drain_tube", &st.white_tube),
        ("display_signal_ribbon", &st.black_part),
    ] {
        let child = parts.m("get", args![name])?;
        if !matches!(child, Val::None) {
            let shape = clip_z(&st, child.a("obj")?, -70.0, 40.0)?
                .m("translate", args![(0i64, 0i64, lift)])?;
            add(&a, &shape, name, colour)?;
        }
    }
    let shank = parts.m("get", args!["westbrass"])?;
    if !matches!(shank, Val::None) {
        let shape = clip_z(&st, shank.a("obj")?, -70.0, 40.0)?
            .m("translate", args![(0i64, 0i64, lift)])?;
        add(&a, &shape, "shank", &st.steel)?;
    }
    Ok(a)
}

/// `s_filter_in_cabinet`: the cartridge lying flat, the white run easing into both ends.
pub fn s_filter_in_cabinet(rt: &Runtime) -> Result<Val> {
    let st = state(rt)?;
    let a = assembly(&st, "filter-scene")?;
    let z = FILTER_D / 2.0;
    let (half, cap) = (FILTER_L / 2.0, 26.0);
    let cartridge = cyl(
        rt,
        Num::F(-half + cap),
        Num::F(110.0),
        Num::F(z),
        FILTER_D,
        Num::F(FILTER_L - 2.0 * cap),
        "X",
    )?;
    add(&a, &cartridge, "cartridge", &st.filter_body)?;
    for side in [-1.0f64, 1.0] {
        let end = if side > 0.0 { half - cap } else { -half };
        let fitting = cyl(
            rt,
            Num::F(end),
            Num::F(110.0),
            Num::F(z),
            FILTER_D * 0.62,
            Num::F(cap),
            "X",
        )?;
        let name = format!("quick-connect-{}", if side > 0.0 { "out" } else { "in" });
        add(&a, &fitting, name, &st.filter_cap)?;
    }
    let f = Num::F;
    let run_in = bend(
        rt,
        &[
            [f(-half), f(110.0), f(z)],
            [f(-330.0), f(110.0), f(z)],
            [f(-330.0), f(-40.0), f(z)],
        ],
        TUBE_D,
        55.0,
        20,
    )?;
    add(&a, &run_in, "white-run-in", &st.white_tube)?;
    let run_out = bend(
        rt,
        &[
            [f(half), f(110.0), f(z)],
            [f(330.0), f(110.0), f(z)],
            [f(330.0), f(-40.0), f(z)],
        ],
        TUBE_D,
        55.0,
        20,
    )?;
    add(&a, &run_out, "white-run-out", &st.white_tube)?;
    Ok(a)
}

/// `s_collet_press`: the little printed tool that takes any 1/4 inch push fitting apart.
pub fn s_collet_press(rt: &Runtime) -> Result<Val> {
    let st = state(rt)?;
    let a = assembly(&st, "collet-press-scene")?;
    let press = st.import_step.c(args![ps(&st.collet_press)])?;
    a.mk(
        "add",
        vec![press],
        kw!["name" => "collet-press", "color" => st.printed.clone()],
    )?;
    Ok(a)
}

/// `s_the_back_face`: three rows of tube ports, with the power inlet and signal socket.
pub fn s_the_back_face(rt: &Runtime) -> Result<Val> {
    let st = state(rt)?;
    rear_face(rt, &assembly(&st, "the-back-face-scene")?)
}

/// `s_the_socket`: the top row's left-hand end with the cord home in it.
pub fn s_the_socket(rt: &Runtime) -> Result<Val> {
    let st = state(rt)?;
    let a = rear_face(rt, &assembly(&st, "the-socket-scene")?)?;
    let cord = c13_cordset(rt, Num::F(0.5))?;
    a.mk(
        "add",
        vec![cord],
        kw!["name" => "c13-cordset", "color" => st.cordset.clone()],
    )?;
    Ok(a)
}

/// `s_nameplate`: the plate the back cover sends the reader to.
pub fn s_nameplate(rt: &Runtime) -> Result<Val> {
    let st = state(rt)?;
    let a = assembly(&st, "nameplate-scene")?;
    rear_face(rt, &a)?;
    Ok(a)
}

/// `s_plate_sideways`: the under-counter plate coming in from the side.
pub fn s_plate_sideways(rt: &Runtime) -> Result<Val> {
    let st = state(rt)?;
    let (fa, parts) = faucet_parts(&st)?;
    let a = assembly(&st, "plate-scene")?;
    let countertop = slab(&st, &fa, Some((-8.0, 0.0)), (142.0, 68.0))?;
    add(&a, &countertop, "countertop", &st.stone)?;
    for (name, colour) in [
        ("westbrass", &st.steel),
        ("flavor_tube_pos_x", &st.black_part),
        ("flavor_tube_neg_x", &st.black_part_lit),
        ("flavor_umbilical_tube_pos_x", &st.black_part),
        ("flavor_umbilical_tube_neg_x", &st.black_part_lit),
        ("soda_umbilical_tube", &st.blue_tube),
    ] {
        let child = parts.m("get", args![name])?;
        if !matches!(child, Val::None) {
            let clipped = clip_z(&st, child.a("obj")?, -88.0, -30.0)?;
            if clipped.m("solids", vec![])?.m("size", vec![])?.truthy()? {
                add(&a, &clipped, name, colour)?;
            }
        }
    }
    let washer_top = (-fa.a("shank_length")?.f()? + NUT_H) + WASHER_T;
    let washer = st
        .cq
        .a("Workplane")?
        .c(args!["XY"])?
        .mk("workplane", vec![], kw!["offset" => washer_top - WASHER_T])?
        .m("circle", args![12.0])?
        .m("circle", args![6.1])?
        .m("extrude", args![WASHER_T])?;
    add(&a, &washer, "retained-washer", &st.steel)?;
    let nut = st
        .cq
        .a("Workplane")?
        .c(args!["XY"])?
        .mk(
            "workplane",
            vec![],
            kw!["offset" => (washer_top - WASHER_T) - NUT_H],
        )?
        .m("polygon", args![6i64, 22.0])?
        .m("circle", args![6.1])?
        .m("extrude", args![NUT_H])?;
    add(&a, &nut, "retained-nut", &st.nut_steel)?;
    let plate = parts.m("get", args!["under_counter_plate"])?;
    if !matches!(plate, Val::None) {
        let shape = plate
            .a("obj")?
            .m("translate", args![(PLATE_STANDOFF_X, 0.0, 0.0)])?;
        add(&a, &shape, "under-counter-plate", &st.plate_steel)?;
    }
    Ok(a)
}

/// `s_bottle_in_funnel`: a 440 mL bottle tipped past level over the uncovered funnel.
pub fn s_bottle_in_funnel(rt: &Runtime) -> Result<Val> {
    let st = state(rt)?;
    let scene = assembly(&st, "bottle-scene")?;
    let keep = Val::function(|args, kwargs| {
        let mut c = Call::new(args, kwargs);
        let name: Val = c.req(0, "name")?;
        c.done()?;
        Ok(Val::Bool(!hsm_documents::interop::eq(
            &name,
            &Val::Str("funnel-cover".into()),
        )?))
    });
    let a = borrow(&st, &scene, Some(keep))?;
    let shoulder = BOTTLE_NECK_H;
    let body = shoulder + 26.0;
    let f = Num::F;
    let built = vec![
        (
            cyl(rt, f(0.0), f(0.0), f(0.0), BOTTLE_NECK_D, f(BOTTLE_NECK_H), "Z")?,
            "bottle-neck",
            &st.bottle_pet,
        ),
        (
            workplane(&st, (f(0.0), f(0.0), f(shoulder)))?
                .m("circle", args![BOTTLE_NECK_D / 2.0])?
                .mk("workplane", vec![], kw!["offset" => 26.0])?
                .m("circle", args![BOTTLE_D / 2.0])?
                .m("loft", vec![])?,
            "bottle-shoulder",
            &st.bottle_pet,
        ),
        (
            cyl(rt, f(0.0), f(0.0), f(body), BOTTLE_D, f(BOTTLE_H), "Z")?,
            "bottle-body",
            &st.concentrate,
        ),
        (
            cyl(rt, f(0.0), f(0.0), f(body + BOTTLE_H), BOTTLE_D * 0.62, f(4.0), "Z")?,
            "bottle-base",
            &st.bottle_pet,
        ),
    ];
    let mut parts = vec![];
    for (shape, name, colour) in built {
        let tipped = shape.m(
            "rotate",
            args![(0i64, 0i64, 0i64), (1i64, 0i64, 0i64), 90.0 - BOTTLE_TIP],
        )?;
        parts.push((tipped, name, colour));
    }
    let mut lows = vec![];
    for (shape, _, _) in &parts {
        lows.push(
            shape
                .m("val", vec![])?
                .m("BoundingBox", vec![])?
                .a("zmin")?
                .f()?,
        );
    }
    let lowest = fmin(lows);
    let mut mouth = st.funnel_mouth.list()?;
    mouth.push(Val::Float(
        (st.funnel_bounds.i(5)?.f()? + BOTTLE_CLEARANCE) - lowest,
    ));
    let mouth = Val::Tuple(mouth);
    for (shape, name, colour) in &parts {
        let placed = shape.m("translate", vec![mouth.clone()])?;
        add(&a, &placed, *name, colour)?;
    }
    Ok(a)
}

/// `_load_regulator`: the shipped Taprite 3741, its PI010822S in the outlet port.
pub fn load_regulator(rt: &Runtime) -> Result<Val> {
    let st = state(rt)?;
    load(rt, &st.regulator_dir, "taprite_3741_regulator")
}

/// `_co2_tether`: the red tether out of the regulator's push-fit mouth: down `drop`, then `run`
/// along +X.
pub fn co2_tether(rt: &Runtime, mouth: &Val, drop: Num, run: Num, radius: f64) -> Result<Val> {
    let [x, y, z] = <[Num; 3]>::from_val(mouth)?;
    bend(
        rt,
        &[
            [x, y, z.add(TETHER_IN_MOUTH)],
            [x, y, z.sub(drop)],
            [x.add(run), y, z.sub(drop)],
        ],
        TUBE_D,
        radius,
        20,
    )
}

/// `s_regulator`: the two dials, the locked adjusting screw and the red tether.
pub fn s_regulator(rt: &Runtime) -> Result<Val> {
    let st = state(rt)?;
    let reg = load_regulator(rt)?;
    let a = reg.m("build_assembly", vec![])?;
    let outlet = reg.m("outlet", vec![])?.list()?;
    ensure!(outlet.len() == 2, "ValueError: outlet() unpacks to two values");
    let tether = co2_tether(rt, &outlet[0], Num::F(46.0), Num::F(120.0), 22.0)?;
    add(&a, &tether, "red-tether", &st.red_tube)?;
    Ok(a)
}

/// `_load`: `directory/<stem>.py` executed as module `stem`, registered in `sys.modules` first
/// and with its directory on `sys.path` while it runs.
pub fn load(rt: &Runtime, directory: &Path, stem: &str) -> Result<Val> {
    let st = state(rt)?;
    rt.py("importlib.util")?;
    let importlib = rt.py("importlib")?;
    let path = directory.join(format!("{stem}.py"));
    st.note_read.c(args![path])?;
    let spec = importlib
        .a("util")?
        .m("spec_from_file_location", args![stem, path])?;
    let module = importlib.a("util")?.m("module_from_spec", vec![spec.clone()])?;
    st.sys
        .a("modules")?
        .set(Val::Str(stem.into()), module.clone())?;
    st.sys.a("path")?.m("insert", args![0i64, ps(directory)])?;
    let run = spec
        .a("loader")
        .and_then(|loader| loader.m("exec_module", vec![module.clone()]));
    st.sys.a("path")?.m("remove", args![ps(directory)])?;
    run?;
    Ok(module)
}

/// One scene's pose for `_hsm_render`, as `SCENES` keeps it.
pub fn pose(st: &State, name: &str) -> Result<Val> {
    Ok(match name {
        "cabinet-plan" => dict![
            "cam" => (0.0, 0.0, 1.0),
            "up" => (0i64, 1i64, 0i64),
            "size" => "1700x2000",
        ],
        "opening" => dict![
            "cam" => (0.42, -0.8, 0.95),
            "target" => (0.0, 0.0, 24.0),
            "span" => 120.0,
            "size" => "1900x1600",
        ],
        "filter-in-cabinet" => dict!["cam" => (0.32, -1.0, 0.52), "size" => "2200x1200"],
        "two-tees" => dict!["cam" => (0.25, 1.0, 0.32), "size" => "1600x900"],
        "nameplate" => dict![
            "cam" => (-0.14, 1.0, 0.1),
            "target" => (38.16, 467.0, 262.9),
            "span" => 132.0,
            "size" => "1600x1100",
        ],
        "plate-sideways" => dict![
            "cam" => (-0.85, -1.0, -0.85),
            "target" => (-16.0, 0.0, -43.0),
            "span" => 88.0,
            "size" => "1700x950",
        ],
        "stop-open" | "stop-closed" => dict![
            "cam" => (1.05, 1.7, 0.62),
            "target" => (-6.0, 44.0, 96.0),
            "span" => 86.0,
            "size" => "1250x1150",
            "trim" => false,
        ],
        "tee-before" | "tee-after" => dict![
            "cam" => (1.05, 1.7, 0.62),
            "target" => (-6.0, 44.0, 112.0),
            "span" => 132.0,
            "size" => "1250x1150",
            "trim" => false,
        ],
        "bottle-in-funnel" => dict![
            "cam" => (1.0, -0.5, 0.45),
            "target" => (20.0, 215.0, 190.0),
            "span" => 265.0,
            "size" => "1500x1180",
        ],
        "kitchen-push" => dict![
            "cam" => (1.05, -1.72, 0.72),
            "target" => (-46.0, 8.0, 100.0),
            "span" => 88.0,
            "size" => "1500x980",
            "trim" => false,
        ],
        "kitchen-hose" => dict![
            "cam" => (1.05, 1.7, 0.62),
            "target" => (10.0, 53.0, 150.0),
            "span" => 88.0,
            "size" => "1500x980",
            "trim" => false,
        ],
        "regulator" => dict!["cam" => (0.1, 1.0, 0.16), "size" => "1700x1500"],
        "collet-press" => dict!["cam" => (-0.5, -0.9, 0.85), "size" => "1700x1100"],
        "the-back-face" => dict![
            "cam" => (0.0, 1.0, 0.12),
            "target" => (0.0, 467.0, 268.0),
            "span" => 100.0,
            "size" => "3200x2240",
        ],
        "the-socket" => dict![
            "cam" => (-0.26, 1.0, 0.16),
            "target" => Val::Tuple(vec![
                Val::Float(5.0),
                st.rear_face_y.clone(),
                Val::Float(334.1),
            ]),
            "span" => 31.7,
            "size" => "2200x668",
        ],
        _ => bail!("KeyError: {}", Val::Str(name.into()).repr()?),
    })
}

/// `render`: stage the named scenes' payloads, draw them into `art/` and report each picture.
pub fn render(rt: &Runtime, names: &[String]) -> Result<()> {
    let st = state(rt)?;
    mkdirs(&st.art)?;
    mkdirs(&st.out)?;
    st.note_read.c(vec![st.machine_mesh.clone()])?;
    st.note_read.c(vec![st.machine_facts.clone()])?;
    st.note_read.c(args![st.collet_press])?;
    st.note_read.c(args![st.c14_source])?;
    let context = st.tempfile.mk(
        "TemporaryDirectory",
        vec![],
        kw!["prefix" => "install-art-", "dir" => st.out.clone()],
    )?;
    with(&context, |directory| {
        let work = PathBuf::from_val(&directory)?;
        let payloads = rt.import_module("_install_art_mesh")?.a("payloads")?; // via namespace: _install_art_mesh
        let shown = payloads.c(vec![
            rt.import_module(NAME)?,
            Val::list(names.iter().map(|n| Val::Str(n.clone())).collect()),
            Val::Path(work.clone()),
        ])?; // via namespace: _install_art_mesh
        let mut jobs = vec![];
        for name in names {
            let pose = pose(&st, name)?;
            let step = work.join(format!("{name}.step"));
            let relative = step
                .strip_prefix(&st.hardware)
                .with_context(|| format!("ValueError: {} is not under HARDWARE", step.display()))?;
            let mut job = Dict::new()
                .with("step", ps(relative))
                .with("payload", shown.get(Val::Str(name.clone()))?.str()?)
                .with("out", ps(&st.art.join(format!("{name}.png"))))
                .with("up", (0i64, 0i64, 1i64))
                .with("bg", "#ffffff")
                .with("trim", true)
                .with("solid", true)
                .with("ortho", true)
                .with("ground", false)
                .with("fog", false);
            for (key, value) in pose.items()? {
                job.set(key, value);
            }
            jobs.push(job.val());
            rt.print(format!("  staged {name}"))?;
        }
        st.hsm_render.m("render", vec![Val::list(jobs.clone())])?;
        for job in &jobs {
            let out = PathBuf::from(job.ks("out")?);
            st.cad_art
                .m("_clear_connected_background", args![out])?; // via namespace: _cad_art
            st.note_write.c(args![out])?;
            let size = std::fs::metadata(&out)
                .with_context(|| format!("stat {}", out.display()))?
                .len() as i64;
            let file = out
                .file_name()
                .map(|n| n.to_string_lossy().into_owned())
                .unwrap_or_default();
            rt.print(format!("  -> art/{file} ({} KB)", size.div_euclid(1024)))?;
        }
        Ok(())
    })
}

/// `main(argv)`: `--list` prints the scenes; otherwise render the named ones (or all).
pub fn cli(rt: &Runtime, argv: &[String]) -> Result<i64> {
    let st = state(rt)?;
    if argv.iter().any(|a| a == "--list") {
        for (name, _) in SCENES {
            rt.print(name)?;
        }
        return Ok(0);
    }
    let mut wanted: Vec<String> = argv.iter().filter(|a| !a.starts_with('-')).cloned().collect();
    if wanted.is_empty() {
        wanted = SCENES.iter().map(|(name, _)| (*name).to_owned()).collect();
    }
    let unknown: Vec<&str> = wanted
        .iter()
        .map(String::as_str)
        .filter(|n| !SCENES.iter().any(|(name, _)| name == n))
        .collect();
    if !unknown.is_empty() {
        rt.pya("builtins", "print")?.ck(
            args![format!("unknown scene(s): {}", unknown.join(", "))],
            kw!["file" => st.sys.a("stderr")?],
        )?;
        return Ok(1);
    }
    render(rt, &wanted)?;
    Ok(0)
}

/// A function Python sees, its arguments bound like the source signature.
fn exported(rt: &Runtime, f: impl Fn(&Runtime, &mut Call) -> Result<Val> + 'static) -> Val {
    let rt = rt.clone();
    Val::function(move |args, kwargs| {
        let mut call = Call::new(args, kwargs);
        let value = f(&rt, &mut call)?;
        call.done()?;
        Ok(value)
    })
}

fn points3(value: &Val) -> Result<Vec<[Num; 3]>> {
    value.list()?.iter().map(<[Num; 3]>::from_val).collect()
}

fn rows(value: &Val) -> Result<Vec<Vec<Val>>> {
    value.list()?.iter().map(|row| row.list()).collect()
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let st = state(rt)?;
    ns.module(rt, "json", "json")?;
    ns.value("os", st.os.clone());
    ns.value("sys", st.sys.clone());
    ns.value("tempfile", st.tempfile.clone());
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.module(rt, "math", "math")?;
    ns.value("HERE", st.here.clone());
    ns.value("HARDWARE", st.hardware.clone());
    ns.value("ROOT", st.root.clone());
    ns.value("ART", st.art.clone());
    ns.value("OUT", st.out.clone());
    ns.value("cq", st.cq.clone());
    ns.value("import_step", st.import_step.clone());
    ns.value("note_read", st.note_read.clone());
    ns.value("note_write", st.note_write.clone());
    ns.value("xz_plane_y_up", st.xz_plane_y_up.clone());
    ns.value("_c14", st.c14.clone());
    ns.value("_cad_art", st.cad_art.clone());
    ns.value("_hsm_render", st.hsm_render.clone());
    ns.value("MACHINE_MESH", st.machine_mesh.clone());
    ns.value("MACHINE_FACTS", st.machine_facts.clone());
    ns.value("COLLET_PRESS", st.collet_press.clone());
    ns.value("REGULATOR_DIR", st.regulator_dir.clone());
    ns.value("PLUMBING_DIR", st.plumbing_dir.clone());
    ns.value("MODERN_DIR", st.modern_dir.clone());
    ns.value("C14_SOURCE", st.c14_source.clone());
    ns.value("BOX_X0", BOX_X0);
    ns.value("BOX_X1", BOX_X1);
    ns.value("BOX_Y0", BOX_Y0);
    ns.value("BOX_Y1", BOX_Y1);
    ns.value("BOX_Z0", BOX_Z0);
    ns.value("BOX_Z1", BOX_Z1);
    ns.value("BOX_MID_X", box_mid_x());
    ns.value("FUNNEL_BOUNDS", st.funnel_bounds.clone());
    ns.value("FUNNEL_MOUTH", st.funnel_mouth.clone());
    ns.value("PORT_FACE_Y", PORT_FACE_Y);
    ns.value("PORT_Z_UPPER", PORT_Z_UPPER);
    ns.value("PORT_Z_LOWER", PORT_Z_LOWER);
    ns.value("PORT_X_WEST", PORT_X_WEST);
    ns.value("PORT_X_EAST", PORT_X_EAST);
    ns.value("CLEAR_BEHIND", CLEAR_BEHIND);
    ns.value("CLEAR_SIDE", CLEAR_SIDE);
    ns.value("CYLINDER_LANE", CYLINDER_LANE);
    ns.value("CYLINDER_D", CYLINDER_D);
    ns.value("CYLINDER_H", CYLINDER_H);
    ns.value("FILTER_D", FILTER_D);
    ns.value("FILTER_L", FILTER_L);
    ns.value("BOTTLE_D", BOTTLE_D);
    ns.value("BOTTLE_H", BOTTLE_H);
    ns.value("BOTTLE_NECK_D", BOTTLE_NECK_D);
    ns.value("BOTTLE_NECK_H", BOTTLE_NECK_H);
    ns.value("TUBE_D", TUBE_D);
    ns.value("BOTTLE_TIP", BOTTLE_TIP);
    ns.value("BOTTLE_CLEARANCE", BOTTLE_CLEARANCE);
    ns.value("STONE", st.stone.clone());
    ns.value("CABINET", st.cabinet.clone());
    ns.value("CORAL", st.coral.clone());
    ns.value("STEEL", st.steel.clone());
    ns.value("BRASS", st.brass.clone());
    ns.value("WHITE_TUBE", st.white_tube.clone());
    ns.value("RED_TUBE", st.red_tube.clone());
    ns.value("BLUE_TUBE", st.blue_tube.clone());
    ns.value("BLACK_PART", st.black_part.clone());
    ns.value("CONCENTRATE", st.concentrate.clone());
    ns.value("BOTTLE_PET", st.bottle_pet.clone());
    ns.value("FILTER_BODY", st.filter_body.clone());
    ns.value("FILTER_CAP", st.filter_cap.clone());
    ns.value("PRINTED", st.printed.clone());
    ns.value("CYLINDER", st.cylinder.clone());
    ns.value("ACETAL_GRAY", st.acetal_gray.clone());
    ns.func(rt, "_box", |rt, c| {
        box_(
            rt,
            c.req(0, "x0")?,
            c.req(1, "y0")?,
            c.req(2, "z0")?,
            c.req(3, "sx")?,
            c.req(4, "sy")?,
            c.req(5, "sz")?,
        )
    });
    ns.func(rt, "_cyl", |rt, c| {
        let (x, y, z) = (c.req(0, "x")?, c.req(1, "y")?, c.req(2, "z")?);
        let (d, length) = (c.req(3, "d")?, c.req(4, "length")?);
        let axis: String = c.opt(5, "axis", "Z".to_owned())?;
        cyl(rt, x, y, z, d, length, &axis)
    });
    ns.func(rt, "_run", |rt, c| {
        let points: Vec<Val> = c.req(0, "points")?;
        let diameter = c.opt(1, "diameter", TUBE_D)?;
        run_tube(rt, &points, diameter)
    });
    ns.func(rt, "_bend", |rt, c| {
        let points = points3(&c.req::<Val>(0, "points")?)?;
        let diameter = c.opt(1, "diameter", TUBE_D)?;
        let radius = c.opt(2, "radius", 55.0)?;
        let steps = c.opt(3, "steps", 20i64)?;
        bend(rt, &points, diameter, radius, steps)
    });
    ns.func(rt, "_unit", |_, c| {
        let vec: Vec<f64> = c.req(0, "vec")?;
        Ok(unit(&vec).to_val())
    });
    ns.func(rt, "_add", |_, c| {
        let assembly: Val = c.req(0, "assembly")?;
        let shape: Val = c.req(1, "shape")?;
        let name: Val = c.req(2, "name")?;
        let color: Val = c.req(3, "color")?;
        add(&assembly, &shape, name, &color)?;
        Ok(Val::None)
    });
    ns.func(rt, "_machine", |rt, c| machine(rt, &c.req::<Val>(0, "assembly")?));
    ns.func(rt, "_hex", |rt, c| {
        let (x, y, z) = (c.req(0, "x")?, c.req(1, "y")?, c.req(2, "z")?);
        let (across_flats, length) = (c.req(3, "across_flats")?, c.req(4, "length")?);
        let axis: String = c.opt(5, "axis", "Z".to_owned())?;
        hex(rt, x, y, z, across_flats, length, &axis)
    });
    ns.func(rt, "_floor", |rt, c| {
        floor(
            rt,
            c.req(0, "x0")?,
            c.req(1, "y0")?,
            c.req(2, "sx")?,
            c.req(3, "sy")?,
        )
    });
    ns.value("REAR_CHILDREN", st.rear_children.clone());
    ns.value("REAR_RING_PREFIX", REAR_RING_PREFIX);
    ns.value("_FACTS", st.facts.clone());
    ns.value("REAR_FACE_Y", st.rear_face_y.clone());
    ns.value("C14_STATION", st.c14_station.clone());
    ns.value("C13_SLIP", C13_SLIP);
    ns.value("C13_WALL", C13_WALL);
    ns.value("C13_BODY_LEN", C13_BODY_LEN);
    ns.value("C13_NOSE_LEN", C13_NOSE_LEN);
    ns.value("C13_BOOT_LEN", C13_BOOT_LEN);
    ns.value("C13_BOOT_D", C13_BOOT_D);
    ns.value("C13_CABLE_D", C13_CABLE_D);
    ns.value("CORDSET", st.cordset.clone());
    ns.func(rt, "_rear_face", |rt, c| rear_face(rt, &c.req::<Val>(0, "assembly")?));
    ns.func(rt, "_prism", |rt, c| {
        prism(
            rt,
            c.req(0, "w")?,
            c.req(1, "h")?,
            c.req(2, "r")?,
            c.req(3, "length")?,
        )
    });
    ns.func(rt, "_cable", |rt, c| {
        let points = rows(&c.req::<Val>(0, "points")?)?;
        let diameter = c.req(1, "diameter")?;
        let tangents = rows(&c.req::<Val>(2, "tangents")?)?;
        cable(rt, &points, diameter, &tangents)
    });
    ns.func(rt, "_c13_cordset", |rt, c| c13_cordset(rt, c.req(0, "gap")?));
    let builders: Vec<(&str, Val)> = vec![
        ("s_cabinet_plan", exported(rt, |rt, _| s_cabinet_plan(rt))),
        ("s_opening", exported(rt, |rt, _| s_opening(rt))),
        ("s_filter_in_cabinet", exported(rt, |rt, _| s_filter_in_cabinet(rt))),
        ("s_collet_press", exported(rt, |rt, _| s_collet_press(rt))),
        ("s_the_back_face", exported(rt, |rt, _| s_the_back_face(rt))),
        ("s_the_socket", exported(rt, |rt, _| s_the_socket(rt))),
        ("s_nameplate", exported(rt, |rt, _| s_nameplate(rt))),
        ("s_plate_sideways", exported(rt, |rt, _| s_plate_sideways(rt))),
        ("s_bottle_in_funnel", exported(rt, |rt, _| s_bottle_in_funnel(rt))),
        ("s_regulator", exported(rt, |rt, _| s_regulator(rt))),
    ];
    let builder = |name: &str| {
        builders
            .iter()
            .find(|(n, _)| *n == name)
            .map(|(_, f)| f.clone())
            .expect("scene builder")
    };
    for name in [
        "s_cabinet_plan",
        "s_opening",
        "s_filter_in_cabinet",
        "s_collet_press",
        "s_the_back_face",
        "s_the_socket",
        "s_nameplate",
    ] {
        ns.value(name, builder(name));
    }
    ns.value("PLATE_STANDOFF_X", PLATE_STANDOFF_X);
    ns.value("WASHER_T", WASHER_T);
    ns.value("NUT_H", NUT_H);
    ns.value("NUT_STEEL", st.nut_steel.clone());
    ns.value("PLATE_STEEL", st.plate_steel.clone());
    ns.value("BLACK_PART_LIT", st.black_part_lit.clone());
    ns.value("s_plate_sideways", builder("s_plate_sideways"));
    ns.value("s_bottle_in_funnel", builder("s_bottle_in_funnel"));
    ns.value("TETHER_IN_MOUTH", TETHER_IN_MOUTH);
    ns.func(rt, "_load_regulator", |rt, _| load_regulator(rt));
    ns.func(rt, "_co2_tether", |rt, c| {
        let mouth: Val = c.req(0, "mouth")?;
        let (drop, run) = (c.req(1, "drop")?, c.req(2, "run")?);
        let radius = c.req(3, "radius")?;
        co2_tether(rt, &mouth, drop, run, radius)
    });
    ns.value("s_regulator", builder("s_regulator"));
    ns.func(rt, "_load", |rt, c| {
        let directory: PathBuf = c.req(0, "directory")?;
        let stem: String = c.req(1, "stem")?;
        load(rt, &directory, &stem)
    });
    let mut scenes = Dict::new();
    for (name, built_by) in SCENES {
        let function = built_by.map(builder).unwrap_or(Val::None);
        scenes.set(name, Val::Tuple(vec![function, pose(&st, name)?]));
    }
    ns.value("SCENES", scenes.val());
    ns.func(rt, "render", |rt, c| {
        let names: Vec<String> = c.req(0, "names")?;
        render(rt, &names)?;
        Ok(Val::None)
    });
    ns.func(rt, "main", |rt, c| {
        let argv: Vec<String> = c.req(0, "argv")?;
        Ok(Val::Int(cli(rt, &argv)?))
    });
    Ok(())
}

pub fn main(rt: &Runtime) -> Result<()> {
    let rust_part = rt.py("_rust_part")?;
    rt.import_module(NAME)?
        .setattr("_rust_part", rust_part.clone())?;
    rust_part.m("start", vec![])?;
    let st = state(rt)?;
    let argv: Vec<String> = Vec::<String>::from_val(&st.sys.a("argv")?)?;
    let code = cli(rt, argv.get(1..).unwrap_or(&[]))?;
    st.sys.m("exit", args![code])?;
    Ok(())
}
