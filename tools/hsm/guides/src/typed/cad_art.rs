//! `_cad_art`: the install guide's focused, customer-facing CAD pictures. The production
//! models carry more geometry than an instruction frame needs; these scenes keep the touched
//! parts, render them through `_hsm_render` and trim each picture to its frame.

use super::cad_art_mesh;
use super::*;
use std::cell::RefCell;

pub const NAME: &str = "_cad_art";

pub const MOUNT_CAM: [f64; 3] = [1.0, -1.45, -0.38];
pub const MOUNT_TARGET: [f64; 3] = [0.0, 0.0, 110.0];
pub const MOUNT_FRAME_SHAVE: i64 = 18;
pub const MOUNT_FRAME_TRIM_TOP: i64 = 200;
pub const MOUNT_DROP_TRIM_TOP: i64 = 120;
pub const MOUNT_FRAME_TRIM_BOTTOM: i64 = 40;
pub const UNDER_MOUNT_CAM: [f64; 3] = [0.58, -1.6, -0.72];
pub const UNDER_MOUNT_TARGET: [f64; 3] = [0.0, 0.0, -34.0];
pub const UNDER_MOUNT_FRAME_SHAVE: i64 = 18;
pub const PLATE_APPROACH_X: f64 = -72.0;
pub const UNDER_COUNTERTOP_X: f64 = 220.0;
pub const UNDER_COUNTERTOP_Y: f64 = 72.0;
pub const CONNECT_CAM: [f64; 3] = [0.7, 1.0, 0.16];
pub const CONNECT_TARGET: [f64; 3] = [44.0, 630.0, 370.0];
pub const CONNECT_ORTHO_SPAN: f64 = 180.0;
pub const CONNECT_RENDER_SIZE: &str = "1600x1800";
pub const CONNECT_OPEN_GAP: f64 = 160.0;
pub const CONNECT_CROP: [i64; 4] = [0, 650, 1350, 1800];

pub struct State {
    pub importlib: Val,
    pub json: Val,
    pub os: Val,
    pub shutil: Val,
    pub subprocess: Val,
    pub sys: Val,
    pub tempfile: Val,
    /// `pathlib.Path`, as the runtime constructs it.
    pub path: Val,
    pub cq: Val,
    /// `PIL.Image`.
    pub image: Val,
    pub here: PathBuf,
    pub hardware: PathBuf,
    pub root: PathBuf,
    pub art: PathBuf,
    pub out: PathBuf,
    pub faucet_source: PathBuf,
    pub machine_step: PathBuf,
    pub machine_mesh: PathBuf,
    pub machine_facts: PathBuf,
    pub tube_collar_dir: PathBuf,
    pub per_solid_color: Val,
    pub write_mesh_payload: Val,
    /// `_cadq_export.note_read` / `note_write`, called with the values the source passes.
    pub note_read: Val,
    pub note_write: Val,
    pub hsm_render: Val,
    /// `_y_wall_dimensions`.
    pub rear: Val,
}
impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        rt.import_module("importlib.util")?;
        let importlib = rt.import_module("importlib")?;
        let json = rt.import_module("json")?;
        let os = rt.import_module("os")?;
        let shutil = rt.import_module("shutil")?;
        let subprocess = rt.import_module("subprocess")?;
        let sys = rt.import_module("sys")?;
        let tempfile = rt.import_module("tempfile")?;
        rt.import_module("pathlib")?;
        let path = member(rt, "pathlib", "Path")?;
        let cq = rt.import_module("cadquery")?;
        rt.import_module("PIL")?;
        let image = member(rt, "PIL", "Image")?;
        let resolved = resolve(&rt.file(NAME));
        let here = resolved.parent().unwrap_or(&resolved).to_owned();
        let hardware = ancestor(&here, "hardware")?;
        let root = hardware.parent().unwrap_or(&hardware).to_owned();
        let art = here.join("art");
        let out = here.join("out");
        let faucet_source = hardware.join("faucet-layout").join("faucet_assembly.py");
        let layout = hardware.join("manifold-layout");
        let machine_step = layout.join("enclosure-assembly.step");
        let machine_mesh = layout.join("enclosure-assembly.step.mesh");
        let machine_facts = layout.join("enclosure-assembly.facts.json");
        let tube_collar_dir = hardware
            .join("printed-parts")
            .join("faucet")
            .join("tube-collar");
        rt.sys_path_insert(0, &hardware.join("scripts"))?;
        rt.sys_path_insert(
            0,
            &hardware
                .join("printed-parts")
                .join("enclosure")
                .join("y-wall-of-back-top"),
        )?;
        rt.import_module("_cadq_export")?;
        let per_solid_color = member(rt, "_cadq_export", "_per_solid_color")?;
        let write_mesh_payload = member(rt, "_cadq_export", "_write_mesh_payload")?;
        let note_read = member(rt, "_cadq_export", "note_read")?;
        let note_write = member(rt, "_cadq_export", "note_write")?;
        let hsm_render = rt.import_module("_hsm_render")?;
        let rear = rt.import_module("_y_wall_dimensions")?;
        Ok(Self {
            importlib,
            json,
            os,
            shutil,
            subprocess,
            sys,
            tempfile,
            path,
            cq,
            image,
            here,
            hardware,
            root,
            art,
            out,
            faucet_source,
            machine_step,
            machine_mesh,
            machine_facts,
            tube_collar_dir,
            per_solid_color,
            write_mesh_payload,
            note_read,
            note_write,
            hsm_render,
            rear,
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

fn assembly(cq: &Val, name: &str) -> Result<Val> {
    cq.a("Assembly")?.ck(vec![], kw!["name" => name])
}
fn workplane(cq: &Val, plane: &str) -> Result<Val> {
    cq.a("Workplane")?.c(args![plane])
}
fn rgba(cq: &Val, r: f64, g: f64, b: f64) -> Result<Val> {
    cq.a("Color")?.c(args![r, g, b, 1.0])
}
/// `out.add(obj, name=name, color=color)`.
fn add(out: &Val, obj: Val, name: impl ToVal, color: &Val) -> Result<()> {
    out.mk("add", vec![obj], kw!["name" => name, "color" => color])?;
    Ok(())
}
/// `obj.solids().size()`, as `if not ...` reads it.
fn has_solids(obj: &Val) -> Result<bool> {
    obj.m("solids", vec![])?.m("size", vec![])?.truthy()
}
fn save_png(image: &Val, path: &Val) -> Result<()> {
    image.mk(
        "save",
        vec![path.clone()],
        kw!["format" => "PNG", "compress_level" => 9i64, "optimize" => false],
    )?;
    Ok(())
}
fn tuple3(a: impl ToVal, b: impl ToVal, c: impl ToVal) -> Val {
    Val::Tuple(vec![a.to_val(), b.to_val(), c.to_val()])
}

/// `_load_faucet_module()`: the faucet layout's assembly source, executed as a fresh module.
pub fn load_faucet_module(rt: &Runtime) -> Result<Val> {
    let st = state(rt)?;
    st.note_read.c(vec![Val::Path(st.faucet_source.clone())])?;
    let spec = st.importlib.a("util")?.m(
        "spec_from_file_location",
        vec![
            Val::Str("installation_faucet".into()),
            Val::Path(st.faucet_source.clone()),
        ],
    )?;
    if matches!(spec, Val::None) || matches!(spec.a("loader")?, Val::None) {
        bail!("RuntimeError: cannot import {}", ps(&st.faucet_source));
    }
    let module = st
        .importlib
        .a("util")?
        .m("module_from_spec", vec![spec.clone()])?;
    spec.a("loader")?.m("exec_module", vec![module.clone()])?;
    Ok(module)
}

/// `machine_bodies(keep)`: the machine payload's entries whose body name `keep` takes.
pub fn machine_bodies(rt: &Runtime, keep: impl Fn(&str) -> Result<bool>) -> Result<Vec<Val>> {
    let st = state(rt)?;
    let flute_payload = rt.import_module("flute_payload")?;
    let payload = flute_payload.m("read_payload", vec![Val::Path(st.machine_mesh.clone())])?;
    let entries = if payload.truthy()? {
        payload
    } else {
        Val::list(vec![])
    };
    let mut out = vec![];
    for entry in entries.iter()? {
        let name = entry.k("name")?.str()?;
        if keep(name.split('/').next().unwrap_or(""))? {
            out.push(entry);
        }
    }
    Ok(out)
}

/// `borrow(assembly, bodies)`: the assembly with `bodies` added to its borrowed machine meshes.
pub fn borrow(assembly: &Val, bodies: &Val) -> Result<Val> {
    let mut machine = assembly
        .a("machine")
        .unwrap_or_else(|_| Val::tuple(vec![]))
        .iter()?;
    machine.extend(bodies.iter()?);
    assembly.setattr("machine", Val::list(machine))?;
    Ok(assembly.clone())
}

/// `_export_colored(assembly, target, *, mesh=False)`: the colored STEP (and its payload);
/// borrowed machine meshes go out beside the assembly's own solids as one mesh STEP.
pub fn export_colored(rt: &Runtime, assembly: &Val, target: &Val, mesh: bool) -> Result<Val> {
    let st = state(rt)?;
    let machine = assembly
        .a("machine")
        .unwrap_or_else(|_| Val::tuple(vec![]));
    let colored = if assembly.a("children")?.truthy()? {
        st.per_solid_color.c(vec![assembly.clone()])?
    } else {
        Val::None
    };
    if !machine.truthy()? {
        colored.m("export", vec![Val::Str(target.str()?)])?;
        if mesh {
            st.write_mesh_payload
                .c(vec![target.clone(), colored.clone()])?;
        }
        return Ok(target.clone());
    }
    let mesh_payload = rt.import_module("_mesh_payload")?;
    let np = rt.import_module("numpy")?;
    rt.import_module("meshcad")?;
    let mesh_write = member(rt, "meshcad", "write")?;
    let mut meshes = vec![];
    if !matches!(colored, Val::None) {
        meshes.extend(mesh_payload.m("from_assembly", vec![colored.clone()])?.iter()?);
    }
    meshes.extend(machine.iter()?);
    let mut rows = vec![];
    for m in &meshes {
        let name = m.k("name")?;
        let pos = np
            .m("asarray", vec![m.k("pos")?, Val::Type("float".into())])?
            .m("reshape", args![-1i64, 3i64])?;
        let idx = np
            .m("asarray", vec![m.k("idx")?, np.a("int64")?])?
            .m("reshape", args![-1i64, 3i64])?;
        rows.push(Val::tuple(vec![
            name,
            Val::tuple(vec![pos, idx]),
            m.k("color")?,
        ]));
    }
    mesh_write.mk(
        "write_step",
        vec![Val::list(rows), target.clone()],
        kw!["root_name" => assembly.a("name")?],
    )?;
    let digest = mesh_payload.m("source_digest", vec![target.clone()])?;
    mesh_payload.mk(
        "write",
        vec![
            Val::list(meshes),
            Val::Str(format!("{}.mesh", target.str()?)),
        ],
        kw!["src" => digest],
    )?;
    Ok(target.clone())
}

/// `_clip_z(obj, z_min, z_max)`: `obj` cut to the slab between two heights.
pub fn clip_z(rt: &Runtime, obj: &Val, z_min: Num, z_max: Num) -> Result<Val> {
    let st = state(rt)?;
    let clip = workplane(&st.cq, "XY")?
        .mk("workplane", vec![], kw!["offset" => z_min])?
        .mk(
            "box",
            args![600.0, 600.0, z_max.sub(z_min)],
            kw!["centered" => (true, true, false)],
        )?;
    let obj = if obj.a("intersect").is_ok() {
        obj.clone()
    } else {
        workplane(&st.cq, "XY")?.m("newObject", vec![Val::list(vec![obj.clone()])])?
    };
    obj.m("intersect", vec![clip])
}

/// `_moved(obj, xyz)`: `obj` translated by `xyz`.
pub fn moved(rt: &Runtime, obj: &Val, xyz: &Val) -> Result<Val> {
    if obj.a("translate").is_ok() {
        return obj.m("translate", vec![xyz.clone()]);
    }
    let st = state(rt)?;
    let vector = st.cq.a("Vector")?.c(xyz.iter()?)?;
    let location = st.cq.a("Location")?.c(vec![vector])?;
    obj.m("moved", vec![location])
}

/// `_children_by_name(assembly)`.
pub fn children_by_name(assembly: &Val) -> Result<OMap<Val>> {
    let mut out = OMap::new();
    for child in assembly.a("children")?.iter()? {
        out.set(&child.a("name")?.str()?, child);
    }
    Ok(out)
}

/// `_add_child(out, child, *, name=None, obj=None, color=None)`: the child, or the given
/// replacement shape, name and color, added to `out`.
pub fn add_child(out: &Val, child: &Val, name: &Val, obj: &Val, color: &Val) -> Result<()> {
    let shape = if matches!(obj, Val::None) {
        child.a("obj")?
    } else {
        obj.clone()
    };
    let name = if name.truthy()? {
        name.clone()
    } else {
        child.a("name")?
    };
    let color = if matches!(color, Val::None) {
        child.a("color")?
    } else {
        color.clone()
    };
    out.mk("add", vec![shape], kw!["name" => name, "color" => color])?;
    Ok(())
}

/// `_physical_levers(fa)`: the lever at rest and pressed, each cut clear of the soda tube.
pub fn physical_levers(rt: &Runtime, fa: &Val) -> Result<(Val, Val)> {
    let st = state(rt)?;
    let cq = &st.cq;
    let plateau = || Num::from_val(&fa.a("plateau_z")?);
    let cut_cylinder = fa
        .a("WorldWorkplane")?
        .c(vec![fa.a("xy_plane_z_up")?])?
        .mk("workplane", vec![], kw!["offset" => plateau()?.add(1i64)])?
        .m(
            "moveTo",
            vec![Val::tuple(vec![
                Val::Int(0),
                Val::Float(fa.a("port_center_depth")?.f()? + 0.125),
            ])],
        )?
        .m(
            "circle",
            vec![Num::from_val(&fa.a("soda_faucet_tube_r")?)?.add(1i64).to_val()],
        )?
        .m("extrude", args![50i64])?
        .m("unwrap", vec![])?;
    let taper_plane = cq.a("Plane")?.ck(
        vec![],
        kw![
            "origin" => (0i64, 0i64, 0i64),
            "xDir" => (1i64, 0i64, 0i64),
            "normal" => (0i64, -1i64, 0i64),
        ],
    )?;
    let taper = cq
        .a("Workplane")?
        .c(vec![taper_plane])?
        .mk("workplane", vec![], kw!["offset" => 6i64])?
        .m("moveTo", args![0i64, plateau()?.f() + 4.5])?
        .mk("rect", args![13i64, 8.5], kw!["centered" => (true, false)])?
        .mk("workplane", vec![], kw!["offset" => 36i64])?
        .m("moveTo", args![0i64, plateau()?.add(10i64)])?
        .mk("rect", args![13i64, 3i64], kw!["centered" => (true, false)])?
        .mk("loft", vec![], kw!["combine" => true])?;
    let rest = fa
        .a("WorldWorkplane")?
        .c(vec![fa.a("xy_plane_z_up")?])?
        .mk("workplane", vec![], kw!["offset" => plateau()?.add(1i64)])?
        .m("moveTo", vec![Val::tuple(vec![Val::Int(0), Val::Float(1.5)])])?
        .m("rect", args![13i64, 15i64])?
        .m("extrude", args![12i64])?
        .m("unwrap", vec![])?
        .m("union", vec![taper])?
        .m("cut", vec![cut_cylinder.clone()])?;
    let pivot_a = tuple3(0i64, fa.a("lever_pivot_y")?, fa.a("lever_pivot_z")?);
    let pivot_b = tuple3(1i64, fa.a("lever_pivot_y")?, fa.a("lever_pivot_z")?);
    let angle = Num::from_val(&fa.a("lever_press_angle_deg")?)?;
    let pressed = rest
        .m("rotate", vec![pivot_a, pivot_b, angle.to_val()])?
        .m("cut", vec![cut_cylinder])?;
    Ok((rest, pressed))
}

const ABOVE_COUNTER_NAMES: [&str; 14] = [
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
const ABOVE_COUNTER_CLIPPED: [&str; 4] = [
    "westbrass",
    "drain_tube",
    "flavor_tube_pos_x",
    "flavor_tube_neg_x",
];
const MOUNT_NAMES: [&str; 17] = [
    "westbrass",
    "drain_tube",
    "soda_faucet_tube",
    "tpu_o_ring",
    "flavor_tube_pos_x",
    "flavor_tube_neg_x",
    "flavor_umbilical_tube_pos_x",
    "flavor_umbilical_tube_neg_x",
    "soda_umbilical_tube",
    "lever",
    "above_counter_plate",
    "above_counter_gasket",
    "shell_base",
    "shell_tip",
    "faucet-display-cover-seated",
    "faucet_display",
    "faucet_display_screen",
];
/// `enumerate(..., start=1)` as the runtime calls it: its `enumerate` takes `start` only
/// positionally, so the keyword leaves the first index at 0.
const ENUMERATE_START: usize = 0;

/// `_build_steps(work)`: the faucet and mount scenes as CadQuery assemblies, exported as
/// colored STEPs with their payloads.
pub fn build_steps(rt: &Runtime, work: &Path) -> Result<OMap<Val>> {
    let st = state(rt)?;
    let cq = &st.cq;
    let fa = load_faucet_module(rt)?;
    let faucet = fa.m("build_assembly", vec![])?;
    let parts = children_by_name(&faucet)?;
    let (lever_rest, lever_pressed) = physical_levers(rt, &fa)?;
    let step = |name: &str| Val::Path(work.join(name));

    let above_counter_with = |lever: &Val, name: &str| -> Result<Val> {
        let above = assembly(cq, name)?;
        for part_name in ABOVE_COUNTER_NAMES {
            let child = parts.at(part_name)?;
            let mut obj = if part_name == "lever" {
                lever.clone()
            } else {
                child.a("obj")?
            };
            if ABOVE_COUNTER_CLIPPED.contains(&part_name) {
                obj = clip_z(
                    rt,
                    &obj,
                    Num::from_val(&fa.a("countertop_top_z")?)?,
                    Num::F(260.0),
                )?;
            }
            add_child(&above, child, &Val::None, &obj, &Val::None)?;
        }
        Ok(above)
    };
    let user_step = export_colored(
        rt,
        &above_counter_with(&lever_rest, "faucet-user")?,
        &step("faucet-user.step"),
        true,
    )?;
    let pressed_step = export_colored(
        rt,
        &above_counter_with(&lever_pressed, "faucet-user-pressed")?,
        &step("faucet-user-pressed.step"),
        true,
    )?;
    let faucet_full_step = export_colored(rt, &faucet, &step("faucet-full.step"), true)?;
    let slab = workplane(cq, "XY")?
        .mk("workplane", vec![], kw!["offset" => fa.a("countertop_bottom_z")?])?
        .mk(
            "box",
            args![
                UNDER_COUNTERTOP_X,
                UNDER_COUNTERTOP_Y,
                fa.a("countertop_thickness")?
            ],
            kw!["centered" => (true, true, false)],
        )?;
    let hole = workplane(cq, "XY")?
        .mk(
            "workplane",
            vec![],
            kw!["offset" => fa.a("countertop_bottom_z")?.f()? - 1.0],
        )?
        .m("center", args![0.0, fa.a("countertop_hole_center_y")?])?
        .m("circle", vec![fa.a("hole_radius")?])?
        .m("extrude", args![fa.a("countertop_thickness")?.f()? + 2.0])?;
    let countertop_window = slab.m("cut", vec![hole])?;

    let mut flavor_lengths: Vec<(String, &str)> = vec![];
    for body in ["flavor_tube", "flavor_umbilical_tube"] {
        for side in ["pos_x", "neg_x"] {
            flavor_lengths.push((format!("{body}_{side}"), side));
        }
    }
    let mut mount_tails: Vec<String> = flavor_lengths.iter().map(|(n, _)| n.clone()).collect();
    mount_tails.push("soda_umbilical_tube".into());
    mount_tails.push("drain_tube".into());
    let mount_clip = (Num::F(-88.0), Num::F(380.0));
    let washer_thickness = 1.5;
    let nut_height = 5.0;
    let captive_washer_top_z = (-fa.a("shank_length")?.f()? + nut_height) + washer_thickness;
    let final_washer_top_z = Num::from_val(&fa.a("countertop_bottom_z")?)?
        .sub(Num::from_val(&fa.a("under_counter_plate_thickness")?)?)
        .f();
    let plate_steel = rgba(cq, 0.91, 0.92, 0.94)?;
    let washer_steel = rgba(cq, 0.82, 0.83, 0.84)?;
    let nut_steel = rgba(cq, 0.43, 0.45, 0.48)?;
    let countertop_stone = rgba(cq, 0.55, 0.55, 0.58)?;
    let flavor_black_a = rgba(cq, 0.025, 0.027, 0.031)?;
    let flavor_black_b = rgba(cq, 0.2, 0.205, 0.215)?;
    let mut flavor_colors = OMap::new();
    for (name, side) in &flavor_lengths {
        let color = if *side == "pos_x" {
            &flavor_black_a
        } else {
            &flavor_black_b
        };
        flavor_colors.set(name, color.clone());
    }
    let flavor_color = |name: &str| flavor_colors.get(name).cloned().unwrap_or(Val::None);
    let signal_black = rgba(cq, 0.035, 0.038, 0.043)?;
    let signal_stripe_black = rgba(cq, 0.16, 0.17, 0.19)?;
    let frame_anchor_color = rgba(cq, 0.95, 0.04, 0.82)?;

    let donor_hardware = |washer_top_z: f64| -> Result<(Val, Val)> {
        let washer_bottom_z = washer_top_z - washer_thickness;
        let washer = workplane(cq, "XY")?
            .mk("workplane", vec![], kw!["offset" => washer_bottom_z])?
            .m("circle", args![12.0])?
            .m("circle", args![6.1])?
            .m("extrude", args![washer_thickness])?;
        let nut = workplane(cq, "XY")?
            .mk("workplane", vec![], kw!["offset" => washer_bottom_z - nut_height])?
            .m("polygon", args![6i64, 22.0])?
            .m("circle", args![6.1])?
            .m("extrude", args![nut_height])?;
        Ok((washer, nut))
    };
    let signal_geometry: RefCell<Option<(Val, Val)>> = RefCell::new(None);
    let signal_ribbon = |lift_z: f64| -> Result<(Val, Val)> {
        if signal_geometry.borrow().is_none() {
            let shell = fa.a("faucet_shell")?;
            let path = fa.m("_step_path", args![1i64, -123.0])?;
            let origin = vec![
                shell.a("signal_lower_exit_x")?,
                shell.a("signal_lower_exit_y")?,
                fa.a("under_counter_plate_bottom_z")?,
            ];
            let tail = workplane(cq, "XY")?
                .m(
                    "rect",
                    vec![
                        shell.a("signal_ribbon_max_width")?,
                        shell.a("signal_ribbon_max_depth")?,
                    ],
                )?
                .mk("sweep", vec![path.clone()], kw!["transition" => "round"])?
                .m("translate", vec![Val::tuple(origin.clone())])?;
            let ribbon = parts
                .at("display_signal_ribbon")?
                .a("obj")?
                .m("union", vec![tail])?;
            let stripes = workplane(cq, "XY")?
                .m(
                    "pushPoints",
                    vec![Val::list(vec![
                        (-1.05, 0.0).to_val(),
                        (0.0, 0.0).to_val(),
                        (1.05, 0.0).to_val(),
                    ])],
                )?
                .m("rect", args![0.24, 0.08])?
                .mk("sweep", vec![path], kw!["transition" => "round"])?
                .m(
                    "translate",
                    vec![tuple3(
                        origin[0].clone(),
                        (origin[1].f()? - shell.a("signal_ribbon_max_depth")?.f()? / 2.0)
                            - 0.04,
                        origin[2].clone(),
                    )],
                )?;
            *signal_geometry.borrow_mut() = Some((ribbon, stripes));
        }
        let (ribbon, stripes) = signal_geometry.borrow().clone().context("signal geometry")?;
        let ribbon = moved(rt, &ribbon, &tuple3(0.0, 0.0, lift_z))?;
        let stripes = moved(rt, &stripes, &tuple3(0.0, 0.0, lift_z))?;
        Ok((
            clip_z(rt, &ribbon, mount_clip.0, mount_clip.1)?,
            clip_z(rt, &stripes, mount_clip.0, mount_clip.1)?,
        ))
    };
    let render_frame = |out: &Val,
                        cam: [f64; 3],
                        target: [f64; 3],
                        across_size: f64,
                        rise_size: f64,
                        prefix: &str|
     -> Result<()> {
        let view = cq.a("Vector")?.c(args![cam[0], cam[1], cam[2]])?;
        let view = view.m("multiply", args![1.0 / view.a("Length")?.f()?])?;
        let world_up = cq.a("Vector")?.c(args![0.0, 0.0, 1.0])?;
        let right = view.m("cross", vec![world_up])?;
        let right = right.m("multiply", args![1.0 / right.a("Length")?.f()?])?;
        let screen_up = right.m("cross", vec![view.clone()])?;
        let screen_up = screen_up.m("multiply", args![1.0 / screen_up.a("Length")?.f()?])?;
        let target = cq.a("Vector")?.c(args![target[0], target[1], target[2]])?;
        for (i, (across, rise)) in [(-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0)]
            .into_iter()
            .enumerate()
        {
            let index = ENUMERATE_START + i;
            let point = target
                .m("add", vec![right.m("multiply", args![across * across_size])?])?
                .m("add", vec![screen_up.m("multiply", args![rise * rise_size])?])?;
            let anchor = workplane(cq, "XY")?
                .mk("workplane", vec![], kw!["offset" => point.a("z")?.f()? - 0.75])?
                .m("center", vec![point.a("x")?, point.a("y")?])?
                .mk("box", args![1.5, 1.5, 1.5], kw!["centered" => (true, true, false)])?;
            add(out, anchor, format!("{prefix}-{index}"), &frame_anchor_color)?;
        }
        Ok(())
    };
    let add_render_frame =
        |out: &Val| render_frame(out, MOUNT_CAM, MOUNT_TARGET, 118.0, 235.0, "render-frame-anchor");
    let add_under_render_frame = |out: &Val| {
        render_frame(
            out,
            UNDER_MOUNT_CAM,
            UNDER_MOUNT_TARGET,
            137.0,
            58.0,
            "under-render-frame-anchor",
        )
    };
    let add_mount_product = |out: &Val, lift_z: f64, washer_top_z: Option<f64>| -> Result<()> {
        let mv = tuple3(0.0, 0.0, lift_z);
        for part_name in MOUNT_NAMES {
            let child = parts.at(part_name)?;
            let obj = if part_name == "lever" {
                lever_rest.clone()
            } else {
                child.a("obj")?
            };
            let mut obj = moved(rt, &obj, &mv)?;
            if mount_tails.iter().any(|t| t == part_name) {
                obj = clip_z(rt, &obj, mount_clip.0, mount_clip.1)?;
                if !has_solids(&obj)? {
                    continue;
                }
            }
            add_child(out, child, &Val::None, &obj, &flavor_color(part_name))?;
        }
        let (ribbon, ribbon_stripes) = signal_ribbon(lift_z)?;
        add(out, ribbon, "sig6-flat-ribbon", &signal_black)?;
        add(out, ribbon_stripes, "sig6-ribbon-face-stripes", &signal_stripe_black)?;
        let washer_top_z = washer_top_z.unwrap_or(captive_washer_top_z + lift_z);
        let (washer, nut) = donor_hardware(washer_top_z)?;
        add(out, washer, "retained-donor-washer", &washer_steel)?;
        add(out, nut, "retained-donor-nut", &nut_steel)?;
        Ok(())
    };
    let add_countertop_section =
        |out: &Val| add(out, countertop_window.clone(), "countertop-window", &countertop_stone);
    let add_under_countertop = |out: &Val| {
        add(
            out,
            countertop_window.clone(),
            "under-countertop-window",
            &countertop_stone,
        )
    };
    let add_under_mount_product = |out: &Val, washer_top_z: f64| -> Result<()> {
        let under_clip = (Num::F(-86.0), Num::F(-2.0));
        let mut names = vec!["westbrass".to_owned()];
        names.extend(flavor_lengths.iter().map(|(n, _)| n.clone()));
        names.push("soda_umbilical_tube".into());
        names.push("drain_tube".into());
        for part_name in &names {
            let child = parts.at(part_name)?;
            let obj = clip_z(rt, &child.a("obj")?, under_clip.0, under_clip.1)?;
            if !has_solids(&obj)? {
                continue;
            }
            add_child(
                out,
                child,
                &Val::Str(format!("under-{part_name}")),
                &obj,
                &flavor_color(part_name),
            )?;
        }
        let (ribbon, ribbon_stripes) = signal_ribbon(0.0)?;
        add(
            out,
            clip_z(rt, &ribbon, under_clip.0, under_clip.1)?,
            "under-sig6-flat-ribbon",
            &signal_black,
        )?;
        add(
            out,
            clip_z(rt, &ribbon_stripes, under_clip.0, under_clip.1)?,
            "under-sig6-ribbon-face-stripes",
            &signal_stripe_black,
        )?;
        let (washer, nut) = donor_hardware(washer_top_z)?;
        add(out, washer, "under-retained-donor-washer", &washer_steel)?;
        add(out, nut, "under-retained-donor-nut", &nut_steel)?;
        Ok(())
    };
    let plate = parts.at("under_counter_plate")?;
    let plate_moved = || -> Result<Val> {
        moved(rt, &plate.a("obj")?, &tuple3(PLATE_APPROACH_X, 0.0, 0.0))
    };

    let factory = assembly(cq, "faucet-mount-factory-captive")?;
    add_countertop_section(&factory)?;
    add_mount_product(&factory, 35.0, None)?;
    add_render_frame(&factory)?;
    let drop_step = export_colored(rt, &factory, &step("mount-drop.step"), true)?;

    let lowered = assembly(cq, "faucet-mount-lowered")?;
    add_countertop_section(&lowered)?;
    add_mount_product(&lowered, 0.0, None)?;
    add_render_frame(&lowered)?;
    let lowered_clean_step = export_colored(rt, &lowered, &step("mount-lowered-clean.step"), true)?;
    let seated_step = export_colored(rt, &lowered, &step("mount-seated.step"), true)?;

    let slide = assembly(cq, "faucet-mount-slide-plate")?;
    add_countertop_section(&slide)?;
    add_mount_product(&slide, 0.0, None)?;
    add_child(&slide, plate, &Val::None, &plate_moved()?, &plate_steel)?;
    add_render_frame(&slide)?;
    let slide_clean_step = export_colored(rt, &slide, &step("mount-slide-clean.step"), true)?;
    let slide_step = export_colored(rt, &slide, &step("mount-slide.step"), true)?;

    let tight = assembly(cq, "faucet-mount-tighten")?;
    add_countertop_section(&tight)?;
    add_mount_product(&tight, 0.0, Some(final_washer_top_z))?;
    add_child(&tight, plate, &Val::None, &Val::None, &plate_steel)?;
    add_render_frame(&tight)?;
    let final_clean_step = export_colored(rt, &tight, &step("mount-final-clean.step"), true)?;
    let tight_step = export_colored(rt, &tight, &step("mount-tighten.step"), true)?;

    let under_slide = assembly(cq, "faucet-mount-under-slide")?;
    add_under_countertop(&under_slide)?;
    add_under_mount_product(&under_slide, captive_washer_top_z)?;
    add_child(
        &under_slide,
        plate,
        &Val::Str("under-open-plate".into()),
        &plate_moved()?,
        &plate_steel,
    )?;
    add_under_render_frame(&under_slide)?;
    let under_slide_step =
        export_colored(rt, &under_slide, &step("mount-under-slide-clean.step"), true)?;

    let under_tight = assembly(cq, "faucet-mount-under-tighten")?;
    add_under_countertop(&under_tight)?;
    add_under_mount_product(&under_tight, final_washer_top_z)?;
    add_child(
        &under_tight,
        plate,
        &Val::Str("under-seated-plate".into()),
        &Val::None,
        &plate_steel,
    )?;
    add_under_render_frame(&under_tight)?;
    let under_tight_step =
        export_colored(rt, &under_tight, &step("mount-under-tighten-clean.step"), true)?;

    let mut out = OMap::new();
    out.set("faucet-user", user_step);
    out.set("faucet-user-pressed", pressed_step);
    out.set("faucet-full", faucet_full_step);
    out.set("mount-drop", drop_step);
    out.set("mount-seated", seated_step);
    out.set("mount-slide", slide_step);
    out.set("mount-tighten", tight_step);
    out.set("mount-lowered-clean", lowered_clean_step);
    out.set("mount-slide-clean", slide_clean_step);
    out.set("mount-final-clean", final_clean_step);
    out.set("mount-under-slide-clean", under_slide_step);
    out.set("mount-under-tighten-clean", under_tight_step);
    Ok(out)
}

const EXACT_NAMES: [&str; 13] = [
    "c14-inlet",
    "keystone-jack",
    "co2-inlet",
    "bulkhead-water",
    "bulkhead-flavor-a",
    "bulkhead-flavor-b",
    "bulkhead-carb",
    "bulkhead-drain",
    "funnel",
    "nameplate",
    "nameplate-ink",
    "enclosure-back-bottom",
    "enclosure-back-top",
];
const COLLAR_STEPS: [(&str, &str); 6] = [
    ("tap", "water"),
    ("co2", "co2"),
    ("carb", "carb"),
    ("flavor-a", "flavor-a"),
    ("flavor-b", "flavor-b"),
    ("drain", "drain"),
];
const COLLAR_FLUIDS: [(&str, &str); 6] = [
    ("tap", "water"),
    ("carb", "carb"),
    ("co2", "co2"),
    ("flavor-a", "flavor"),
    ("flavor-b", "flavor"),
    ("drain", "drain"),
];
const PACK_STATIONS: [(&str, (f64, f64)); 6] = [
    ("tap", (-60.0, 322.0)),
    ("co2", (-40.0, 322.0)),
    ("carb", (-50.0, 312.0)),
    ("flavor-a", (-40.0, 302.0)),
    ("flavor-b", (-60.0, 302.0)),
    ("drain", (-50.0, 292.0)),
];
fn lookup<'a, T>(rows: &'a [(&str, T)], key: &str) -> Result<&'a T> {
    rows.iter()
        .find(|(k, _)| *k == key)
        .map(|(_, v)| v)
        .with_context(|| format!("KeyError: {key:?}"))
}

/// `_build_connection_steps(work)`: the rear face, then the field leads open and connected.
pub fn build_connection_steps(rt: &Runtime, work: &Path) -> Result<OMap<Val>> {
    let st = state(rt)?;
    let cq = &st.cq;
    st.note_read.c(vec![Val::Path(st.machine_facts.clone())])?;
    let facts = json_loads(&read_text(&st.machine_facts)?)?;
    st.note_read
        .c(vec![Val::Path(st.tube_collar_dir.join("tube_collar.py"))])?;
    let rear_bodies = machine_bodies(rt, |name| {
        Ok(EXACT_NAMES.contains(&name) || name.starts_with("bulkhead-ring-"))
    })?;
    let mut found = vec![];
    for entry in &rear_bodies {
        let name = entry.k("name")?.str()?;
        found.push(name.split('/').next().unwrap_or("").to_owned());
    }
    let mut missing: Vec<&str> = EXACT_NAMES
        .into_iter()
        .filter(|name| !found.iter().any(|f| f == name))
        .collect();
    if !missing.is_empty() {
        missing.sort();
        let file = st
            .machine_mesh
            .file_name()
            .map(|n| n.to_string_lossy().into_owned())
            .unwrap_or_default();
        bail!(
            "RuntimeError: {file} has no {} for the rear scene",
            repr_strs(missing)
        );
    }
    let rear_bodies = Val::list(rear_bodies);
    let tube_blue = rgba(cq, 0.035, 0.31, 0.82)?;
    let tube_red = rgba(cq, 0.67, 0.042, 0.042)?;
    let tube_white = rgba(cq, 0.82, 0.84, 0.87)?;
    let tube_black_a = rgba(cq, 0.025, 0.027, 0.031)?;
    let tube_black_b = rgba(cq, 0.115, 0.12, 0.13)?;
    let ribbon_black = rgba(cq, 0.035, 0.038, 0.043)?;
    let ribbon_edge = rgba(cq, 0.16, 0.17, 0.19)?;
    let plug_body = rgba(cq, 0.72, 0.74, 0.78)?;
    let plug_latch = rgba(cq, 0.86, 0.87, 0.89)?;
    let contact_gold = rgba(cq, 0.73, 0.49, 0.14)?;

    let vectors = |points: &[Vec<Val>]| -> Result<Vec<Val>> {
        points
            .iter()
            .map(|point| cq.a("Vector")?.c(point.clone()))
            .collect()
    };
    let round_sweep = |points: &[Vec<Val>], radius: f64| -> Result<Val> {
        let vectors = vectors(points)?;
        let tangent = cq.a("Vector")?.c(args![0.0, 1.0, 0.0])?;
        let path = cq.a("Edge")?.mk(
            "makeSpline",
            vec![Val::list(vectors.clone())],
            kw!["tangents" => (tangent.clone(), tangent.clone()), "scale" => false],
        )?;
        let profile = cq
            .a("Wire")?
            .m("makeCircle", vec![Val::Float(radius), vectors[0].clone(), tangent])?;
        cq.a("Solid")?.mk(
            "sweep",
            vec![profile, Val::list(vec![]), path],
            kw!["makeSolid" => true, "isFrenet" => false],
        )
    };
    let ribbon_sweep = |points: &[Vec<Val>], width: f64, thickness: f64| -> Result<Val> {
        let vectors = vectors(points)?;
        let tangent = cq.a("Vector")?.c(args![0.0, 1.0, 0.0])?;
        let path = cq.a("Edge")?.mk(
            "makeSpline",
            vec![Val::list(vectors.clone())],
            kw!["tangents" => (tangent.clone(), tangent.clone()), "scale" => false],
        )?;
        let p = &vectors[0];
        // `cq.Vector(p.x ± width / 2.0, p.y, p.z ± thickness / 2.0)`, in the source's order.
        let corner = |right: bool, up: bool| -> Result<Val> {
            let x = p.a("x")?.f()?;
            let z = p.a("z")?.f()?;
            cq.a("Vector")?.c(vec![
                Val::Float(if right { x + width / 2.0 } else { x - width / 2.0 }),
                p.a("y")?,
                Val::Float(if up { z + thickness / 2.0 } else { z - thickness / 2.0 }),
            ])
        };
        let corners = vec![
            corner(false, false)?,
            corner(true, false)?,
            corner(true, true)?,
            corner(false, true)?,
        ];
        let profile = cq
            .a("Wire")?
            .mk("makePolygon", vec![Val::list(corners)], kw!["close" => true])?;
        cq.a("Solid")?.mk(
            "sweep",
            vec![profile, Val::list(vec![]), path],
            kw!["makeSolid" => true, "isFrenet" => true],
        )
    };
    let split_collar = |which: &str| -> Result<(Val, Val)> {
        rt.sys_path_insert(0, &st.tube_collar_dir)?;
        let tube_collar = rt.import_module("tube_collar")?;
        let collar_step = *lookup(&COLLAR_STEPS, which)?;
        Ok((
            tube_collar.m("build_collar", args![collar_step])?,
            tube_collar.m("build_word", args![collar_step])?,
        ))
    };
    let card_ports = facts.k("card_ports")?;
    let ports = [
        ("tap", card_ports.k("bulkhead-water")?.k("outboard")?),
        ("carb", card_ports.k("bulkhead-carb")?.k("tube-out")?),
        ("co2", card_ports.k("gas-regulator")?.k("outboard")?),
        ("flavor-a", card_ports.k("bulkhead-flavor-a")?.k("tube-out")?),
        ("flavor-b", card_ports.k("bulkhead-flavor-b")?.k("tube-out")?),
        ("drain", card_ports.k("bulkhead-drain")?.k("outboard")?),
    ];
    let tube_colors = [
        ("tap", &tube_white),
        ("carb", &tube_blue),
        ("co2", &tube_red),
        ("flavor-a", &tube_black_a),
        ("flavor-b", &tube_black_b),
        ("drain", &tube_white),
    ];
    let fluid_colors = |function: &str| -> Result<Vec<(&str, Val)>> {
        let mut out = vec![];
        for (which, fluid) in COLLAR_FLUIDS {
            let mut channels = vec![];
            for c in st.rear.m(function, args![fluid])?.iter()? {
                channels.push(Val::Float(c.f()? / 255.0));
            }
            channels.push(Val::Float(1.0));
            out.push((which, cq.a("Color")?.c(channels)?));
        }
        Ok(out)
    };
    let collar_colors = fluid_colors("chip_color")?;
    let collar_word_colors = fluid_colors("word_color")?;
    let umbilical = assembly(cq, "customer-field-leads-wall-end")?;
    let straight_end_y = 560.0;
    let pack_y = 626.0;
    let tail_y = 940.0;
    let collar_tip_setback = 47.5;
    for which in ["tap", "co2", "carb", "flavor-a", "flavor-b", "drain"] {
        let port = lookup(&ports, which)?;
        let pos = port.k("pos")?.iter()?;
        ensure!(pos.len() == 3, "unpack: expected 3, got {}", pos.len());
        let (x, tube_start_y, z) = (&pos[0], &pos[1], &pos[2]);
        let (pack_x, pack_z) = *lookup(&PACK_STATIONS, which)?;
        let points = vec![
            vec![x.clone(), tube_start_y.clone(), z.clone()],
            vec![x.clone(), Val::Float(straight_end_y), z.clone()],
            vec![x.clone(), Val::Float(578.0), z.clone()],
            vec![
                Val::Float(((2.0 * x.f()?) + pack_x) / 3.0),
                Val::Float(598.0),
                Val::Float(((2.0 * z.f()?) + pack_z) / 3.0),
            ],
            vec![Val::Float(pack_x), Val::Float(pack_y), Val::Float(pack_z)],
            vec![Val::Float(pack_x), Val::Float(tail_y), Val::Float(pack_z)],
        ];
        let tube = round_sweep(&points, lookup(&ports, which)?.k("diam")?.f()? / 2.0)?;
        add(
            &umbilical,
            tube,
            format!("wall-end-tube-{which}"),
            lookup(&tube_colors, which)?,
        )?;
        let (collar, words) = split_collar(which)?;
        let mv = tuple3(
            x.clone(),
            tube_start_y.f()? + collar_tip_setback,
            z.clone(),
        );
        add(
            &umbilical,
            collar.m("translate", vec![mv.clone()])?,
            format!("wall-end-collar-{which}"),
            lookup(&collar_colors, which)?,
        )?;
        add(
            &umbilical,
            words.m("translate", vec![mv])?,
            format!("wall-end-collar-{which}-word"),
            lookup(&collar_word_colors, which)?,
        )?;
    }
    let station = facts.k("constants")?.k("KEYSTONE_STATION")?.iter()?;
    ensure!(station.len() == 2, "unpack: expected 2, got {}", station.len());
    let (jack_x, jack_station_z) = (station[0].clone(), station[1].f()?);
    let jx = jack_x.f()?;
    let jack_face_y = facts.k("bodies")?.k("keystone-jack")?.i(4)?.f()?;
    let jack_port_z = jack_station_z - 1.0;
    let plug_w = 9.0;
    let plug_h = 6.45;
    let plug_y0 = jack_face_y - 6.2;
    let plug_depth = 21.0;
    let make_box = |x: f64, y: f64, z: f64, at: (f64, f64, f64)| -> Result<Val> {
        let corner = cq.a("Vector")?.c(args![at.0, at.1, at.2])?;
        cq.a("Solid")?.m("makeBox", vec![x.to_val(), y.to_val(), z.to_val(), corner])
    };
    let compound = |shapes: Vec<Val>| -> Result<Val> {
        cq.a("Compound")?.m("makeCompound", vec![Val::list(shapes)])
    };
    let plug = make_box(
        plug_w,
        plug_depth,
        plug_h,
        (jx - plug_w / 2.0, plug_y0, jack_port_z - plug_h / 2.0),
    )?;
    let boot = make_box(
        7.8,
        5.5,
        5.5,
        (jx - 3.9, plug_y0 + plug_depth, jack_port_z - 2.75),
    )?;
    add(
        &umbilical,
        compound(vec![plug, boot])?,
        "wall-end-rj11-plug-body",
        &plug_body,
    )?;
    let latch_z = jack_port_z - plug_h / 2.0;
    let latch_tongue = make_box(
        3.4,
        12.0,
        0.75,
        (jx - 1.7, plug_y0 + 4.0, latch_z - 0.75),
    )?;
    let latch_ramp = workplane(cq, "YZ")?
        .m(
            "polyline",
            vec![Val::list(vec![
                (plug_y0 + 10.0, latch_z - 0.75).to_val(),
                (plug_y0 + 16.0, latch_z - 0.75).to_val(),
                (plug_y0 + 16.0, latch_z - 2.35).to_val(),
                (plug_y0 + 10.0, latch_z - 0.75).to_val(),
            ])],
        )?
        .m("wire", vec![])?
        .m("extrude", args![3.4])?
        .m("translate", vec![tuple3(jx - 1.7, 0.0, 0.0)])?
        .m("val", vec![])?;
    add(
        &umbilical,
        compound(vec![latch_tongue, latch_ramp])?,
        "wall-end-rj11-latch",
        &plug_latch,
    )?;
    for (i, contact_x) in [-2.7, -0.9, 0.9, 2.7].into_iter().enumerate() {
        let index = ENUMERATE_START + i;
        let contact = make_box(
            0.48,
            7.0,
            0.18,
            (
                (jx + contact_x) - 0.24,
                plug_y0 + 0.4,
                (jack_port_z + plug_h / 2.0) - 0.18,
            ),
        )?;
        add(
            &umbilical,
            contact,
            format!("wall-end-rj11-contact-{index}"),
            &contact_gold,
        )?;
    }
    let ribbon_start_y = (plug_y0 + plug_depth) + 5.5;
    let ribbon_points = vec![
        vec![jack_x.clone(), Val::Float(ribbon_start_y), Val::Float(jack_port_z)],
        vec![jack_x.clone(), Val::Float(548.0), Val::Float(jack_port_z)],
        vec![Val::Float(-42.0), Val::Float(590.0), Val::Float(298.0)],
        vec![Val::Float(-48.5), Val::Float(pack_y), Val::Float(294.0)],
        vec![Val::Float(-48.5), Val::Float(tail_y), Val::Float(294.0)],
    ];
    let ribbon = ribbon_sweep(&ribbon_points, 4.0, 1.2)?;
    let mut mark_points = vec![];
    for point in &ribbon_points {
        mark_points.push(vec![
            Val::Float(point[0].f()? + 1.55),
            point[1].clone(),
            Val::Float(point[2].f()? + 0.63),
        ]);
    }
    let ribbon_mark = ribbon_sweep(&mark_points, 0.28, 0.08)?;
    add(&umbilical, ribbon, "wall-end-sig6-ribbon", &ribbon_black)?;
    add(&umbilical, ribbon_mark, "wall-end-sig6-ribbon-mark", &ribbon_edge)?;
    let scene_state = |name: &str, shift_y: f64| -> Result<Val> {
        let scene = borrow(&assembly(cq, name)?, &rear_bodies)?;
        let location = cq
            .a("Location")?
            .c(vec![cq.a("Vector")?.c(args![0.0, shift_y, 0.0])?])?;
        scene.mk(
            "add",
            vec![umbilical.clone()],
            kw!["name" => format!("{name}-umbilical"), "loc" => location],
        )?;
        export_colored(rt, &scene, &Val::Path(work.join(format!("{name}.step"))), true)
    };
    let rear = borrow(&assembly(cq, "the-back-face")?, &rear_bodies)?;
    let rear_step = export_colored(rt, &rear, &Val::Path(work.join("the-back-face.step")), true)?;
    let open_step = scene_state("connect-rear-open", CONNECT_OPEN_GAP)?;
    let connected_step = scene_state("connect-rear-connected", 0.0)?;
    let mut out = OMap::new();
    out.set("the-back-face", rear_step);
    out.set("connect-rear-open", open_step);
    out.set("connect-rear-connected", connected_step);
    Ok(out)
}

/// `_job(step, out, cam, *, target=None)`: one `_hsm_render` job for a STEP and its payload.
pub fn job(rt: &Runtime, step: &Path, out: &Val, cam: &Val, target: &Val) -> Result<Val> {
    let st = state(rt)?;
    let mut output = PathBuf::from(out.str()?);
    if !output.is_absolute() {
        output = st.art.join(&output);
    }
    let relative = step.strip_prefix(&st.hardware).with_context(|| {
        format!(
            "ValueError: {} is not in the subpath of {}",
            ps(step),
            ps(&st.hardware)
        )
    })?;
    let mut job = Dict::new();
    job.set("step", ps(relative))
        .set("payload", ps(&PathBuf::from(format!("{}.mesh", ps(step)))))
        .set("out", ps(&output))
        .set("cam", cam.clone())
        .set("up", (0i64, 0i64, 1i64))
        .set("size", "2400x2400")
        .set("bg", "#ffffff")
        .set("trim", true)
        .set("solid", true)
        .set("ortho", true);
    if !matches!(target, Val::None) {
        job.set("target", target.clone());
    }
    Ok(job.val())
}

/// `_canonicalize_png(path)`: the picture rewritten as RGBA PNG at a fixed compression.
pub fn canonicalize_png(rt: &Runtime, path: &Val) -> Result<()> {
    let st = state(rt)?;
    let context = st.image.m("open", vec![path.clone()])?;
    with(&context, |image| {
        let pixels = image.m("convert", args!["RGBA"])?;
        save_png(&pixels, path)
    })
}

/// `shutil.which("magick") or shutil.which("convert")`.
fn magick(st: &State) -> Result<Val> {
    let found = st.shutil.a("which")?.c(args!["magick"])?;
    if found.truthy()? {
        return Ok(found);
    }
    st.shutil.a("which")?.c(args!["convert"])
}

/// `_crop(source, geometry, target)`: an ImageMagick crop between pictures under `ART`.
pub fn crop(rt: &Runtime, source: &Val, geometry: &Val, target: &Val) -> Result<()> {
    let st = state(rt)?;
    let magick = magick(&st)?;
    if !magick.truthy()? {
        return Ok(());
    }
    let mut source_path = PathBuf::from(source.str()?);
    let mut target_path = PathBuf::from(target.str()?);
    if !source_path.is_absolute() {
        source_path = st.art.join(&source_path);
    }
    if !target_path.is_absolute() {
        target_path = st.art.join(&target_path);
    }
    st.subprocess.mk(
        "run",
        vec![Val::list(vec![
            magick,
            Val::Str(ps(&source_path)),
            Val::Str("-crop".into()),
            geometry.clone(),
            Val::Str("+repage".into()),
            Val::Str("-strip".into()),
            Val::Str(ps(&target_path)),
        ])],
        kw!["check" => true],
    )?;
    canonicalize_png(rt, &Val::Path(target_path.clone()))?;
    st.note_write.c(vec![Val::Path(target_path)])?;
    Ok(())
}

/// `_clear_connected_background(path)`: the white background connected to the picture's
/// border made transparent.
pub fn clear_connected_background(rt: &Runtime, path: &Val) -> Result<()> {
    let st = state(rt)?;
    let magick = magick(&st)?;
    if !magick.truthy()? {
        bail!("RuntimeError: ImageMagick is required to clear CAD picture backgrounds");
    }
    let tool = PathBuf::from(magick.str()?);
    let primitive = if tool.file_name().is_some_and(|n| n == "magick") {
        "alpha"
    } else {
        "matte"
    };
    let text = |s: &str| Val::Str(s.into());
    st.subprocess.mk(
        "run",
        vec![Val::list(vec![
            magick.clone(),
            Val::Str(path.str()?),
            text("-bordercolor"),
            text("white"),
            text("-border"),
            text("1"),
            text("-alpha"),
            text("set"),
            text("-channel"),
            text("RGBA"),
            text("-fuzz"),
            text("3%"),
            text("-fill"),
            text("none"),
            text("-draw"),
            Val::Str(format!("{primitive} 0,0 floodfill")),
            text("-shave"),
            text("1x1"),
            text("-strip"),
            Val::Str(path.str()?),
        ])],
        kw!["check" => true],
    )?;
    canonicalize_png(rt, path)?;
    st.note_write.c(vec![path.clone()])?;
    Ok(())
}

/// `_shave_render_frame(path, margin)`: a mount picture trimmed to its render frame.
pub fn shave_render_frame(rt: &Runtime, path: &Val, margin: Num) -> Result<()> {
    let st = state(rt)?;
    let context = st.image.m("open", vec![path.clone()])?;
    with(&context, |image| {
        let trim_top = if path.a("name")?.str()? == "mount-drop.png" {
            MOUNT_DROP_TRIM_TOP
        } else {
            MOUNT_FRAME_TRIM_TOP
        };
        let top = margin.add(trim_top);
        let bottom = Num::from_val(&image.a("height")?)?
            .sub(margin)
            .sub(MOUNT_FRAME_TRIM_BOTTOM);
        let width = Num::from_val(&image.a("width")?)?;
        if width.f() <= Num::I(2).mul(margin).f() || bottom.f() <= top.f() {
            bail!(
                "ValueError: cannot shave {}px from {}x{}: {}",
                fv(&margin.to_val(), "")?,
                fv(&image.a("width")?, "")?,
                fv(&image.a("height")?, "")?,
                fv(path, "")?
            );
        }
        let width = Num::from_val(&image.a("width")?)?;
        let cropped = image.m(
            "crop",
            vec![Val::tuple(vec![
                margin.to_val(),
                top.to_val(),
                width.sub(margin).to_val(),
                bottom.to_val(),
            ])],
        )?;
        save_png(&cropped, path)
    })?;
    canonicalize_png(rt, path)?;
    st.note_write.c(vec![path.clone()])?;
    Ok(())
}

/// `_shave_under_render_frame(path, margin)`: an under-counter picture trimmed by `margin`.
pub fn shave_under_render_frame(rt: &Runtime, path: &Val, margin: Num) -> Result<()> {
    let st = state(rt)?;
    let context = st.image.m("open", vec![path.clone()])?;
    with(&context, |image| {
        let width = Num::from_val(&image.a("width")?)?;
        let twice = Num::I(2).mul(margin);
        if width.f() <= twice.f() || Num::from_val(&image.a("height")?)?.f() <= twice.f() {
            bail!(
                "ValueError: cannot shave {}px from {}x{}: {}",
                fv(&margin.to_val(), "")?,
                fv(&image.a("width")?, "")?,
                fv(&image.a("height")?, "")?,
                fv(path, "")?
            );
        }
        let width = Num::from_val(&image.a("width")?)?;
        let height = Num::from_val(&image.a("height")?)?;
        let cropped = image.m(
            "crop",
            vec![Val::tuple(vec![
                margin.to_val(),
                margin.to_val(),
                width.sub(margin).to_val(),
                height.sub(margin).to_val(),
            ])],
        )?;
        save_png(&cropped, path)
    })?;
    canonicalize_png(rt, path)?;
    st.note_write.c(vec![path.clone()])?;
    Ok(())
}

/// `_crop_registered_connection(path)`: a rear render cut to the registered connection frame.
pub fn crop_registered_connection(rt: &Runtime, path: &Val) -> Result<()> {
    let st = state(rt)?;
    let context = st.image.m("open", vec![path.clone()])?;
    with(&context, |image| {
        let mut expected = vec![];
        for part in CONNECT_RENDER_SIZE.split('x') {
            expected.push(Val::Int(part.parse()?));
        }
        if !hsm_documents::interop::eq(&image.a("size")?, &Val::tuple(expected))? {
            bail!(
                "ValueError: expected {CONNECT_RENDER_SIZE} rear render, found {}x{}: {}",
                fv(&image.a("width")?, "")?,
                fv(&image.a("height")?, "")?,
                fv(path, "")?
            );
        }
        let cropped = image.m("crop", vec![CONNECT_CROP.to_val()])?;
        save_png(&cropped, path)
    })?;
    canonicalize_png(rt, path)?;
    st.note_write.c(vec![path.clone()])?;
    Ok(())
}

/// `main(*, mount_studies=False)`: build the scenes in a temporary directory, render every
/// picture, then trim, clear and crop each one.
pub fn run(rt: &Runtime, mount_studies: bool) -> Result<()> {
    let st = state(rt)?;
    std::fs::create_dir_all(&st.art)?;
    std::fs::create_dir_all(&st.out)?;
    if !mount_studies {
        st.note_read.c(vec![Val::Path(st.machine_mesh.clone())])?;
    }
    let context = st.tempfile.mk(
        "TemporaryDirectory",
        vec![],
        kw!["prefix" => "installation-cad-", "dir" => st.out.clone()],
    )?;
    with(&context, |directory| {
        let work = PathBuf::from(directory.str()?);
        cad_art_mesh::state(rt)?;
        let this = rt.import_module(NAME)?;
        let mut steps = cad_art_mesh::build_steps(rt, &this, &work)?;
        if !mount_studies {
            for (name, step) in cad_art_mesh::build_connection_steps(rt, &this, &work)?.0 {
                steps.set(&name, step);
            }
        }
        let step_job = |name: &str, out: &str, cam: [f64; 3], target: [f64; 3]| -> Result<Val> {
            job(
                rt,
                steps.at(name)?,
                &Val::Str(out.into()),
                &cam.to_val(),
                &target.to_val(),
            )
        };
        let mount = |name: &str| step_job(name, &format!("{name}.png"), MOUNT_CAM, MOUNT_TARGET);
        let mount_jobs = vec![
            mount("mount-drop")?,
            mount("mount-seated")?,
            mount("mount-slide")?,
            mount("mount-tighten")?,
        ];
        let mount_clean_jobs = vec![
            mount("mount-lowered-clean")?,
            mount("mount-slide-clean")?,
            mount("mount-final-clean")?,
        ];
        let under = |name: &str| {
            step_job(
                name,
                &format!("{name}.png"),
                UNDER_MOUNT_CAM,
                UNDER_MOUNT_TARGET,
            )
        };
        let under_mount_jobs = vec![
            under("mount-under-slide-clean")?,
            under("mount-under-tighten-clean")?,
        ];
        let mount_frame_jobs = [mount_jobs, mount_clean_jobs].concat();
        let mount_render_jobs = [mount_frame_jobs.clone(), under_mount_jobs.clone()].concat();
        let connect_jobs = if mount_studies {
            vec![]
        } else {
            let connect = |name: &str| {
                step_job(name, &format!("{name}.png"), CONNECT_CAM, CONNECT_TARGET)
            };
            vec![
                connect("connect-rear-open")?,
                connect("connect-rear-connected")?,
            ]
        };
        for job in &connect_jobs {
            job.set("size".into(), CONNECT_RENDER_SIZE.into())?;
            job.set("span".into(), Val::Float(CONNECT_ORTHO_SPAN))?;
            job.set("trim".into(), Val::Bool(false))?;
            job.set("ground".into(), Val::Bool(false))?;
            job.set("fog".into(), Val::Bool(false))?;
            job.set("transparent".into(), Val::Bool(true))?;
        }
        let jobs = if mount_studies {
            let study_dir = st.out.join("mount-studies");
            std::fs::create_dir_all(&study_dir)?;
            for job in &mount_render_jobs {
                let out = PathBuf::from(job.k("out")?.str()?);
                let name = out
                    .file_name()
                    .map(|n| n.to_string_lossy().into_owned())
                    .unwrap_or_default();
                job.set("out".into(), Val::Str(ps(&study_dir.join(name))))?;
            }
            mount_render_jobs.clone()
        } else {
            let view = |name: &str, out: Val, cam: (f64, f64, f64)| -> Result<Val> {
                job(rt, steps.at(name)?, &out, &cam.to_val(), &Val::None)
            };
            let machine = |out: Val, cam: (f64, f64, f64)| -> Result<Val> {
                job(rt, &st.machine_step, &out, &cam.to_val(), &Val::None)
            };
            let mut jobs = vec![
                view("faucet-user", "faucet-front.png".into(), (0.18, -1.0, 0.18))?,
                view("faucet-user", "faucet-side.png".into(), (1.0, -1.4, 0.75))?,
                view(
                    "faucet-user-pressed",
                    "faucet-side-pressed.png".into(),
                    (1.0, -1.4, 0.75),
                )?,
                view(
                    "faucet-full",
                    Val::Path(work.join("faucet-full-front.png")),
                    (0.0, -1.0, 0.28),
                )?,
            ];
            jobs.extend(mount_render_jobs.iter().cloned());
            jobs.extend(connect_jobs.iter().cloned());
            jobs.push(machine("machine-front.png".into(), (1.0, -1.25, 0.72))?);
            jobs.push(machine(
                Val::Path(work.join("machine-back.png")),
                (0.12, 1.0, 0.32),
            )?);
            jobs.push(machine("machine-back-iso.png".into(), (1.0, 1.0, 1.0))?);
            jobs
        };
        st.hsm_render.m("render", vec![Val::list(jobs.clone())])?;
        let connect = Val::list(connect_jobs.clone());
        let frames = Val::list(mount_frame_jobs.clone());
        let unders = Val::list(under_mount_jobs.clone());
        for job in &jobs {
            let output = Val::Path(PathBuf::from(job.k("out")?.str()?));
            if !connect.contains(job)? {
                clear_connected_background(rt, &output)?;
            }
            if frames.contains(job)? {
                shave_render_frame(rt, &output, Num::I(MOUNT_FRAME_SHAVE))?;
            } else if unders.contains(job)? {
                shave_under_render_frame(rt, &output, Num::I(UNDER_MOUNT_FRAME_SHAVE))?;
            } else if connect.contains(job)? {
                crop_registered_connection(rt, &output)?;
            }
            st.note_write.c(vec![output])?;
        }
        if !mount_studies {
            let s = |text: &str| Val::Str(text.into());
            let w = |name: &str| Val::Path(work.join(name));
            crop(rt, &s("machine-front.png"), &s("960x660+0+100"), &s("machine-funnel-close.png"))?;
            crop(rt, &w("machine-back.png"), &s("720x560+180+300"), &s("machine-back-close.png"))?;
            crop(rt, &s("machine-back-iso.png"), &s("617x720+850+220"), &s("machine-ports-iso.png"))?;
            crop(rt, &s("machine-ports-iso.png"), &s("617x612+0+72"), &s("machine-ports-action.png"))?;
            crop(rt, &s("machine-ports-iso.png"), &s("594x393+23+293"), &s("machine-signal-iso.png"))?;
            crop(rt, &w("faucet-full-front.png"), &s("410x540+0+1060"), &s("faucet-tails-front.png"))?;
            crop(rt, &s("mount-tighten.png"), &s("772x560+0+700"), &s("mount-tighten-close.png"))?;
        }
        Ok(())
    })
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let st = state(rt)?;
    ns.value("importlib", st.importlib.clone());
    ns.value("json", st.json.clone());
    ns.value("os", st.os.clone());
    ns.value("shutil", st.shutil.clone());
    ns.value("subprocess", st.subprocess.clone());
    ns.value("sys", st.sys.clone());
    ns.value("tempfile", st.tempfile.clone());
    ns.value("Path", st.path.clone());
    ns.value("cq", st.cq.clone());
    ns.value("Image", st.image.clone());
    ns.value("HERE", st.here.clone());
    ns.value("HARDWARE", st.hardware.clone());
    ns.value("ROOT", st.root.clone());
    ns.value("ART", st.art.clone());
    ns.value("OUT", st.out.clone());
    ns.value("FAUCET_SOURCE", st.faucet_source.clone());
    ns.value("MACHINE_STEP", st.machine_step.clone());
    ns.value("MACHINE_MESH", st.machine_mesh.clone());
    ns.value("MACHINE_FACTS", st.machine_facts.clone());
    ns.value("TUBE_COLLAR_DIR", st.tube_collar_dir.clone());
    ns.value("MOUNT_CAM", MOUNT_CAM);
    ns.value("MOUNT_TARGET", MOUNT_TARGET);
    ns.value("MOUNT_FRAME_SHAVE", MOUNT_FRAME_SHAVE);
    ns.value("MOUNT_FRAME_TRIM_TOP", MOUNT_FRAME_TRIM_TOP);
    ns.value("MOUNT_DROP_TRIM_TOP", MOUNT_DROP_TRIM_TOP);
    ns.value("MOUNT_FRAME_TRIM_BOTTOM", MOUNT_FRAME_TRIM_BOTTOM);
    ns.value("UNDER_MOUNT_CAM", UNDER_MOUNT_CAM);
    ns.value("UNDER_MOUNT_TARGET", UNDER_MOUNT_TARGET);
    ns.value("UNDER_MOUNT_FRAME_SHAVE", UNDER_MOUNT_FRAME_SHAVE);
    ns.value("PLATE_APPROACH_X", PLATE_APPROACH_X);
    ns.value("UNDER_COUNTERTOP_X", UNDER_COUNTERTOP_X);
    ns.value("UNDER_COUNTERTOP_Y", UNDER_COUNTERTOP_Y);
    ns.value("CONNECT_CAM", CONNECT_CAM);
    ns.value("CONNECT_TARGET", CONNECT_TARGET);
    ns.value("CONNECT_ORTHO_SPAN", CONNECT_ORTHO_SPAN);
    ns.value("CONNECT_RENDER_SIZE", CONNECT_RENDER_SIZE);
    ns.value("CONNECT_OPEN_GAP", CONNECT_OPEN_GAP);
    ns.value("CONNECT_CROP", CONNECT_CROP);
    ns.value("_per_solid_color", st.per_solid_color.clone());
    ns.value("_write_mesh_payload", st.write_mesh_payload.clone());
    ns.value("note_read", st.note_read.clone());
    ns.value("note_write", st.note_write.clone());
    ns.value("_hsm_render", st.hsm_render.clone());
    ns.value("_rear", st.rear.clone());
    ns.func(rt, "_load_faucet_module", |rt, _| load_faucet_module(rt));
    ns.func(rt, "machine_bodies", |rt, c| {
        let keep = c.maybe::<Val>(0, "keep")?;
        let bodies = match keep {
            Some(keep) => machine_bodies(rt, |name| {
                keep.c(vec![Val::Str(name.into())])?.truthy()
            })?,
            None => machine_bodies(rt, |_| Ok(true))?,
        };
        Ok(Val::list(bodies))
    });
    ns.func(rt, "borrow", |_, c| {
        let assembly: Val = c.req(0, "assembly")?;
        let bodies: Val = c.req(1, "bodies")?;
        borrow(&assembly, &bodies)
    });
    ns.func(rt, "_export_colored", |rt, c| {
        let assembly: Val = c.req(0, "assembly")?;
        let target: Val = c.req(1, "target")?;
        let mesh: bool = c.kw("mesh", false)?;
        export_colored(rt, &assembly, &target, mesh)
    });
    ns.func(rt, "_clip_z", |rt, c| {
        let obj: Val = c.req(0, "obj")?;
        let z_min: Num = c.req(1, "z_min")?;
        let z_max: Num = c.req(2, "z_max")?;
        clip_z(rt, &obj, z_min, z_max)
    });
    ns.func(rt, "_moved", |rt, c| {
        let obj: Val = c.req(0, "obj")?;
        let xyz: Val = c.req(1, "xyz")?;
        moved(rt, &obj, &xyz)
    });
    ns.func(rt, "_children_by_name", |_, c| {
        let assembly: Val = c.req(0, "assembly")?;
        Ok(children_by_name(&assembly)?.to_val())
    });
    ns.func(rt, "_add_child", |_, c| {
        let out: Val = c.req(0, "out")?;
        let child: Val = c.req(1, "child")?;
        let name: Val = c.kw("name", Val::None)?;
        let obj: Val = c.kw("obj", Val::None)?;
        let color: Val = c.kw("color", Val::None)?;
        add_child(&out, &child, &name, &obj, &color)?;
        Ok(Val::None)
    });
    ns.func(rt, "_physical_levers", |rt, c| {
        let fa: Val = c.req(0, "fa")?;
        Ok(physical_levers(rt, &fa)?.to_val())
    });
    ns.func(rt, "_build_steps", |rt, c| {
        let work: PathBuf = c.req(0, "work")?;
        Ok(build_steps(rt, &work)?.to_val())
    });
    ns.func(rt, "_build_connection_steps", |rt, c| {
        let work: PathBuf = c.req(0, "work")?;
        Ok(build_connection_steps(rt, &work)?.to_val())
    });
    ns.func(rt, "_job", |rt, c| {
        let step: PathBuf = c.req(0, "step")?;
        let out: Val = c.req(1, "out")?;
        let cam: Val = c.req(2, "cam")?;
        let target: Val = c.kw("target", Val::None)?;
        job(rt, &step, &out, &cam, &target)
    });
    ns.func(rt, "_canonicalize_png", |rt, c| {
        let path: Val = c.req(0, "path")?;
        canonicalize_png(rt, &path)?;
        Ok(Val::None)
    });
    ns.func(rt, "_crop", |rt, c| {
        let source: Val = c.req(0, "source")?;
        let geometry: Val = c.req(1, "geometry")?;
        let target: Val = c.req(2, "target")?;
        crop(rt, &source, &geometry, &target)?;
        Ok(Val::None)
    });
    ns.func(rt, "_clear_connected_background", |rt, c| {
        let path: Val = c.req(0, "path")?;
        clear_connected_background(rt, &path)?;
        Ok(Val::None)
    });
    ns.func(rt, "_shave_render_frame", |rt, c| {
        let path: Val = c.req(0, "path")?;
        let margin: Num = c.req(1, "margin")?;
        shave_render_frame(rt, &path, margin)?;
        Ok(Val::None)
    });
    ns.func(rt, "_shave_under_render_frame", |rt, c| {
        let path: Val = c.req(0, "path")?;
        let margin: Num = c.req(1, "margin")?;
        shave_under_render_frame(rt, &path, margin)?;
        Ok(Val::None)
    });
    ns.func(rt, "_crop_registered_connection", |rt, c| {
        let path: Val = c.req(0, "path")?;
        crop_registered_connection(rt, &path)?;
        Ok(Val::None)
    });
    ns.func(rt, "main", |rt, c| {
        let mount_studies: bool = c.kw("mount_studies", false)?;
        run(rt, mount_studies)?;
        Ok(Val::None)
    });
    Ok(())
}

/// The `__main__` block.
pub fn main(rt: &Runtime) -> Result<()> {
    rt.sys_path_insert(0, &parent_n(&resolve(&rt.file(NAME)), 1).join("scripts"))?;
    rt.import_module("_rust_part")?.m("start", vec![])?;
    let argv = rt.pya("sys", "argv")?.iter()?;
    let mount_studies = argv
        .iter()
        .skip(1)
        .any(|arg| matches!(arg, Val::Str(s) if s == "--mount-studies"));
    run(rt, mount_studies)
}
