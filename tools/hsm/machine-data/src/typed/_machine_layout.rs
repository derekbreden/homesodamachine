//! Numeric installation inputs for the machine's Rust placement program.
//!
//! A plan is cut by the machine program in stages: the referenced part models first, then (for the
//! installed stage) the enclosure pieces and the pump dock, then the complete machine with the
//! equipment, routes and copper runs laid in. The datums come from the enclosure, cold-core and
//! reference-part providers; the arithmetic on them is done here.
use super::num::{self, Num};
use super::rt::{Ns, Rt, keyword_items};
use super::{docs, py};
use anyhow::{Context, Result, bail, ensure};
use hsm_documents::interop::{self, Val, entries_of};
use py::s;
use std::path::{Path, PathBuf};
use std::rc::Rc;

/// Not yet compared with the generated build: the hybrid development build runs the generated namespace.
pub const TYPED: bool = false;

const MODULE: &str = "_machine_layout";

struct State {
    /// `ROOT`: the checkout the module's own file sits in.
    root: PathBuf,
    /// `HW`.
    hw: PathBuf,
    /// `LAYOUT`: `hardware/manifold-layout`.
    layout: PathBuf,
}

fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// The materials `numbers` reads, in the order it imports them.
const MATERIALS: [&str; 14] = [
    "C_COMP",
    "C_COND",
    "C_MQ6",
    "C_DISPLAY_GLASS",
    "C_AC_HUB",
    "M_TINNED_STEEL",
    "M_PETG_BLACK",
    "M_PETGF_BLACK",
    "M_SILICONE_BLACK",
    "M_TPU_BLACK",
    "M_STAINLESS",
    "M_BRASS",
    "M_NEOFIT_WHITE_ACETAL",
    "M_DONOR_BLACK",
];

/// Each colored part and the material it is drawn in.
const COLORS: [(&str, &str); 15] = [
    ("compressor", "C_COMP"),
    ("condenser", "C_COND"),
    ("mq6", "C_MQ6"),
    ("fuse", "M_TINNED_STEEL"),
    ("fuse_clamp", "M_PETG_BLACK"),
    ("funnel", "M_SILICONE_BLACK"),
    ("funnel_cover", "M_PETG_BLACK"),
    ("display", "C_DISPLAY_GLASS"),
    ("display_cover", "M_PETGF_BLACK"),
    ("display_gasket", "M_TPU_BLACK"),
    ("wago", "C_AC_HUB"),
    ("screw", "M_STAINLESS"),
    ("insert", "M_BRASS"),
    ("seam_screw", "M_DONOR_BLACK"),
    ("elbow", "M_NEOFIT_WHITE_ACETAL"),
];

/// The through-wall fittings, west to east.
const THROUGH_WALL: [&str; 8] = [
    "bulkhead-water",
    "c14-inlet",
    "keystone-jack",
    "co2-inlet",
    "bulkhead-flavor-a",
    "bulkhead-flavor-b",
    "bulkhead-carb",
    "bulkhead-drain",
];

/// The four pump barbs in sorted order: name, east of the pump centre, the barb's side of its
/// pump, and the valves its tee feeds (front, back).
const BARBS: [(&str, bool, i64, &str, &str); 4] = [
    ("Y-C", false, 1, "V-E", "V-C"),
    ("Y-D", false, -1, "V-F", "V-G"),
    ("Y-F", true, -1, "V-H", "V-D"),
    ("Y-G", true, 1, "V-I", "V-J"),
];

/// Runs whose manifold stubs the machine program draws itself.
const AUTHORED: [&str; 22] = [
    "water-7", "water-6", "water-5", "water-2", "fluid-1", "water-3", "co2-0", "co2-1", "co2-2", "fluid-2",
    "fluid-4", "fluid-28", "carb-1", "carb-2", "fluid-18", "fluid-24", "fluid-26", "fluid-14", "fluid-16",
    "refrig-3", "refrig-2", "refrig-1",
];

/// Manifold bodies the machine leaves out of its own model.
const OMITTED: [&str; 10] = [
    "valve-v-a",
    "coil-v-a",
    "valve-v-b",
    "coil-v-b",
    "step-fluid-3",
    "step-fluid-5",
    "turn-fluid-3",
    "turn-fluid-5",
    "stub-fluid-2",
    "stub-fluid-4",
];

/// The copper runs: id, from port, to port and the bend arguments each takes.
const REFRIGERANT: [(&str, &str, &str, &[(&str, f64)]); 3] = [
    ("refrig-1", "compressor.refrig-discharge", "condenser+fan.refrig-inlet", &[]),
    ("refrig-2", "condenser+fan.refrig-outlet", "foam-assembly.evap-inlet", &[("lead", 2.0), ("min_bend", 8.0)]),
    ("refrig-3", "compressor.refrig-suction", "foam-assembly.evap-outlet", &[("bend", 12.7), ("lead", 20.0)]),
];

/// The installed parts' models, under `hardware/`.
const INSTALLED_PATHS: [(&str, &str); 7] = [
    ("funnel", "printed-parts/zone-c/funnel/funnel.step"),
    ("funnel_cover", "printed-parts/zone-c/funnel-cover/funnel-cover.step"),
    ("cradle", "printed-parts/zone-c/funnel/elbow-cradle.step"),
    ("stem_elbow", "reference/neofit-stem-elbow/neofit-stem-elbow.step"),
    ("display", "reference/waveshare-43b-display/waveshare-43b-display.step"),
    ("display_cover", "printed-parts/enclosure/display-cover/display-cover.step"),
    ("display_gasket", "printed-parts/enclosure/display-gasket/display-gasket.step"),
];

const PIECES: [&str; 5] = ["front-bottom", "front-top", "back-bottom", "back-top", "pump-retainer"];
const PANELS: [&str; 4] = ["front-bottom", "front-top", "back-bottom", "back-top"];
const BOX_FIELDS: [&str; 6] = ["xmin", "xmax", "ymin", "ymax", "zmin", "zmax"];

// The runtime's arithmetic where it can fail.

fn sqrt(x: f64) -> Result<f64> {
    ensure!(x >= 0., "math domain error");
    Ok(x.sqrt())
}
fn div(a: f64, b: f64) -> Result<f64> {
    ensure!(b != 0., "division by zero");
    Ok(a / b)
}
/// `math.dist(a, b)`.
fn dist(a: &[f64], b: &[f64]) -> Result<f64> {
    ensure!(a.len() == b.len(), "distance dimensions");
    Ok(num::dist(a, b))
}
/// `a > b` between two floats.
fn gt(a: f64, b: f64) -> Result<bool> {
    Ok(a.partial_cmp(&b).context("unordered numeric comparison")?.is_gt())
}
/// `str.isdigit()` as the runtime answers it.
fn digits(text: &str) -> bool {
    !text.is_empty() && text.chars().all(|c| c.is_ascii_digit())
}
/// The first three coordinates of a point read off a sequence.
fn xyz(values: &[f64]) -> Result<[f64; 3]> {
    ensure!(values.len() >= 3, "index out of range");
    Ok([values[0], values[1], values[2]])
}
fn call0(object: &Val, name: &str) -> Result<Val> {
    py::method(object, name, vec![])
}
/// `sorted(values)`.
fn sorted(values: &Val) -> Result<Val> {
    interop::builtin("sorted").context("sorted")?.call(vec![values.clone()], vec![])
}
/// Sorted, distinct names.
fn names(mut rows: Vec<String>) -> Val {
    rows.sort();
    rows.dedup();
    Val::list(rows.into_iter().map(Val::Str).collect())
}
fn text_of(value: &Val) -> Result<&str> {
    match value {
        Val::Str(text) => Ok(text),
        other => bail!("expected a name, got {}", other.repr()?),
    }
}
/// `path.write_text(text)`, recorded as a write.
fn write_text(path: &Path, text: String) -> Result<()> {
    Val::Path(path.to_owned()).attr("write_text")?.call(vec![Val::Str(text)], vec![])?;
    Ok(())
}
fn parent(path: &Path) -> PathBuf {
    path.parent().unwrap_or(path).to_owned()
}
fn num_attr(object: &Val, name: &str) -> Result<Num> {
    Num::of(&object.attr(name)?)
}
/// `{**source}` into `target`: each key of `source`, read back through it.
fn dict_extend(target: &Val, source: &Val) -> Result<()> {
    for key in source.iter()? {
        target.set(key.clone(), source.get(key)?)?;
    }
    Ok(())
}

/// `_source(root, path)`: the machine program's reference to one part model, noting the frozen
/// asset manifests beside the staged and authored copies.
fn source(rt: &Rt, st: &State, root: &Val, relative: &Path) -> Result<Val> {
    let request = rt.member("_rust_data", "request")?;
    let note_read = rt.member("_cadq_export", "note_read")?;
    let staged = py::path(root)?.join(relative);
    let authored = st.root.join(relative);
    for manifest in [parent(&staged).join("frozen-asset.json"), parent(&authored).join("frozen-asset.json")] {
        if manifest.is_file() {
            py::call(&note_read, vec![Val::Path(manifest)])?;
        }
    }
    let payload = py::dict([
        ("op", s("model_source")),
        ("mode", s("layout")),
        ("relative", s(py::path_str(relative))),
        ("input_root", s(root.str()?)),
        ("authored_root", s(py::path_str(&st.root))),
    ]);
    py::call(&request, vec![s("machine-data"), s("machine-data"), payload])
}

fn source_at(rt: &Rt, st: &State, root: &Val, relative: &str) -> Result<Val> {
    source(rt, st, root, Path::new(relative))
}

/// `_linear(color)`: a material's linear RGBA.
fn linear(rt: &Rt, color: &Val) -> Result<Val> {
    py::call(&rt.member("_materials", "linear")?, vec![color.clone()])
}

/// `_point(frame, point)` and `_axis(frame, axis)`: a 3x4 frame applied to a point or direction,
/// each row summed from the integer 0 as `sum` adds.
fn apply(frame: &Val, point: &Val, translate: bool) -> Result<Val> {
    let mut out = Vec::with_capacity(3);
    for i in 0..3 {
        let row = frame.get(Val::Int(i))?;
        let mut total = Val::Int(0);
        for j in 0..3 {
            let term = interop::binary("mul", row.get(Val::Int(j))?, point.get(Val::Int(j))?)?;
            total = interop::binary("add", total, term)?;
        }
        if translate {
            total = interop::binary("add", total, row.get(Val::Int(3))?)?;
        }
        out.push(total);
    }
    Ok(Val::Tuple(out))
}

/// `_installed(point)`: a manifold-frame point in the machine's world frame.
fn installed([x, y, z]: [Num; 3]) -> [Num; 3] {
    [x.neg(), z.add(Num::F(14.48)), y.add(Num::F(201.425))]
}

/// `{name: (*mouth, 6.35) for name, mouth in rows.items()}`.
fn mouths(rows: &Val) -> Result<Val> {
    let out = Val::dict(vec![]);
    for item in call0(rows, "items")?.iter()? {
        let pair = py::unpack(&item, 2)?;
        let mut port = pair[1].iter()?;
        port.push(Val::Float(6.35));
        out.set(pair[0].clone(), Val::Tuple(port))?;
    }
    Ok(out)
}

/// One port: centre, axis and bore.
fn port(point: [f64; 3], axis: [f64; 3], bore: f64) -> Val {
    Val::Tuple(vec![py::ftuple(&point), py::ftuple(&axis), Val::Float(bore)])
}

/// `_manifold_datums(enc, construction)`: the pump trays, collet plate and manifold ports the
/// machine program places the manifold with.
fn manifold_datums(rt: &Rt, enc: &Val, construction: &Val) -> Result<Val> {
    let kp = enc.attr("_tray")?.attr("_kp")?;
    let dock = enc.attr("_dock")?;
    let tee = dock.attr("tee")?;
    let plumbing = dock.attr("plumbing")?;
    let interface = enc.attr("_interface")?;
    let manifold = rt.import("manifold_layout")?;
    let barb_pitch = num_attr(&kp, "barb_pitch")?;
    let branch_reach = num_attr(&tee, "BRANCH_REACH")?;
    let pump_pitch = branch_reach.add(barb_pitch.div(Num::F(2.0)));
    let barb_z = num_attr(&kp, "head_w")?.sub(num_attr(&interface, "pump_station_lead")?);
    let seated_drop = num_attr(&interface, "pump_seated_drop")?;
    let pump_y = num_attr(&kp, "outlet_above_skirt_bottom")?
        .sub(num_attr(&interface, "pump_station_drop")?)
        .sub(seated_drop)
        .sub(num_attr(&interface, "manifold_rise")?);
    let head_front = num_attr(&kp, "head_front_z")?;
    let inset = num_attr(&kp, "arch_plane_z")?.sub(head_front);
    let head_y = inset.neg().add(pump_y).sub(head_front).add(num_attr(&kp, "base_plane_z")?);
    let head_z = barb_z.sub(num_attr(&kp, "body_y_face")?).add(num_attr(&kp, "cy")?);
    let mut trays = vec![];
    for px in [pump_pitch.neg(), pump_pitch] {
        let mut center = installed([px, head_y, head_z]);
        center[2] = center[2].add(seated_drop);
        trays.push(Val::Tuple(center.iter().map(|c| Val::Float(num::round_to(c.f(), 6))).collect()));
    }
    let pump_trays = Val::list(trays);

    // The reference bodies of the manifold model, keyed by name in first-seen order.
    let mut references: Vec<String> = vec![];
    for row in py::at(construction, "bodies")?.iter()? {
        if interop::eq(&py::at(&row, "kind")?, &s("reference"))? {
            let name = text_of(&py::at(&row, "name")?)?.to_owned();
            if !references.contains(&name) {
                references.push(name);
            }
        }
    }
    let valve_ports = py::dict([
        ("inlet", port([0.0, -29.75, 11.05], [0.0, -1.0, 0.0], 6.35)),
        ("outlet", port([0.0, 29.75, 11.05], [0.0, 1.0, 0.0], 6.35)),
    ]);
    let manifold_ports = Val::dict(vec![]);
    for name in references.iter().filter(|n| n.starts_with("valve-v-")) {
        manifold_ports.set(s(name.as_str()), valve_ports.clone())?;
    }
    for name in ["valve-v-g", "valve-v-j"] {
        let outlet = port([0.0, 29.75 + ((1.445 - 0.827) * 25.4), 11.05], [0.0, 1.0, 0.0], 4.0);
        manifold_ports.set(s(name), py::merged(&valve_ports, [("outlet", outlet)])?)?;
    }
    let run_half = num_attr(&tee, "RUN_HALF")?;
    let tee_ports = py::dict([
        ("lower", Val::Tuple(vec![Num::vals(&[Num::F(0.0), Num::F(0.0), run_half.neg()]), py::ftuple(&[0.0, 0.0, -1.0]), Val::Float(6.35)])),
        ("upper", Val::Tuple(vec![Num::vals(&[Num::F(0.0), Num::F(0.0), run_half]), py::ftuple(&[0.0, 0.0, 1.0]), Val::Float(6.35)])),
        ("branch", Val::Tuple(vec![Num::vals(&[Num::F(0.0), branch_reach, Num::F(0.0)]), py::ftuple(&[0.0, 1.0, 0.0]), Val::Float(6.35)])),
    ]);
    for name in references.iter().filter(|n| n.starts_with("tee-y-")) {
        manifold_ports.set(s(name.as_str()), tee_ports.clone())?;
    }

    let mut holes: Vec<(f64, f64)> = vec![];
    let upper = Val::dict(vec![]);
    let returns = Val::dict(vec![]);
    let fore = num::round_to(installed([Num::F(0.0), pump_y, barb_z])[1].add(Num::F(5.351)).f(), 6);
    let port_axis = manifold.attr("port_axis")?;
    let port_at = manifold.attr("port")?;
    for (_, east, side, front, back) in BARBS {
        let px = if east { pump_pitch } else { pump_pitch.neg() };
        let at = installed([px.add(Num::I(side).mul(barb_pitch).div(Num::F(2.0))), pump_y, barb_z]);
        let (x, z) = (num::round_to(at[0].f(), 6), num::round_to(at[2].f(), 6));
        holes.push((x, z));
        for (destination, valve, end) in [(&upper, front, "front"), (&returns, back, "back")] {
            let direction = py::call(&port_axis, vec![s(valve), s(end)])?;
            let point = installed(Num::three(&py::call(&port_at, vec![s(valve), s(end)])?)?);
            let axis = Val::Tuple(vec![
                interop::unary("neg", direction.get(Val::Int(0))?)?,
                direction.get(Val::Int(2))?,
                direction.get(Val::Int(1))?,
            ]);
            destination.set(s(num::fstr(x)), py::dict([("point", Num::vals(&point)), ("axis", axis), ("valve", s(valve))]))?;
        }
    }
    let rounded = |value: Val| -> Result<Val> { Ok(Val::Float(num::round_to(value.num()?, 6))) };
    let holes = sorted(&Val::list(holes.iter().map(|(x, z)| py::ftuple(&[*x, *z])).collect()))?;
    let collet = py::dict([
        ("holes", holes),
        ("fore_y", Val::Float(fore)),
        ("aft_y", rounded(py::method(&plumbing, "plate_aft_y", vec![Val::Float(fore)])?)?),
        ("wall_aft_y", rounded(py::method(&dock, "wall_aft_y", vec![Val::Float(fore)])?)?),
        ("x0", call0(enc, "interior_x")?.get(Val::Int(0))?),
        ("x1", call0(enc, "interior_x")?.get(Val::Int(1))?),
        ("z0", enc.attr("z_seam")?),
        ("z1", Val::Float(218.85)),
        ("hole_d", Num::I(2).mul(num_attr(&dock, "HOLE_R")?).val()),
        ("seat_z", rounded(py::method(enc, "bay_floor_z", vec![pump_trays.clone()])?.get(Val::Int(1))?)?),
        ("upper_ports", upper),
        ("return_ports", returns),
        ("valve_trays", Val::list(vec![])),
        ("fixture_print_bed_z", num_attr(enc, "z_seam")?.add(num_attr(enc, "slide_slip")?).val()),
        ("tee_axis_y", rounded(py::method(&plumbing, "tee_axis_y", vec![Val::Float(fore)])?)?),
        ("seated_tube_bottom_y", rounded(py::method(&plumbing, "tip_y", vec![Val::Float(fore)])?)?),
        ("tube_bottom_y", rounded(py::method(&plumbing, "tip_y", vec![Val::Float(fore)])?)?),
        ("pump_tube_cut", Num::F(13.149 + 5.351).add(num_attr(&plumbing, "TIP_FROM_FORE")?).val()),
        ("assembly_state", s("seated")),
    ]);

    let mut omitted: Vec<String> = OMITTED.iter().map(|n| n.to_string()).collect();
    omitted.extend(AUTHORED.iter().map(|n| format!("stub-{n}")));
    for (name, _, _, _, back) in BARBS {
        omitted.push(format!("tee-{}", name.to_lowercase()));
        for host in [name, back] {
            omitted.push(format!("stem-elbow-{}", host.to_lowercase()));
        }
    }
    Ok(py::dict([
        ("manifold_exclude", names(omitted)),
        ("manifold_ports", manifold_ports),
        ("pump_trays", pump_trays),
        ("collet_plate", collet),
        ("pump_face_z", pump_y.sub(inset).val()),
    ]))
}

/// `numbers(*, stage='pack', box_document=None, input_root=ROOT)`: the reference request the
/// machine program cuts a plan from.
fn numbers(rt: &Rt, st: &State, stage: Val, box_document: Val, input_root: &Val) -> Result<Val> {
    call0(&rt.import("_rust_part")?, "start")?;
    let enc = call0(&rt.import("_enclosure_datums")?, "load")?;
    let core_reference = rt.import("core_reference")?;
    let compressor = rt.import("compressor")?;
    let mq6 = rt.import("mq6_gas_sensor")?;
    let fuse = rt.import("sf76e_thermal_fuse")?;
    let mut materials = vec![];
    for name in MATERIALS {
        materials.push((name, rt.member("_materials", name)?));
    }
    let root = py::path(input_root)?;
    let root_val = Val::Path(root.clone());
    let construction = py::json_loads(&py::read_text(&root.join("hardware/manifold-layout/manifold-layout.numbers.json"))?)?;
    let core = call0(&core_reference, "datums")?;
    let cci = rt.import("_cold_core_interface")?;
    core.set(s("source_seat"), core.get(s("seat"))?)?;
    core.set(s("corner_round_radius"), cci.attr("corner_round_radius")?)?;
    core.set(s("ports"), mouths(&core.get(s("conduit_mouths"))?)?)?;
    py::method(&core.get(s("ports"))?, "update", vec![mouths(&core.get(s("copper_mouths"))?)?])?;

    let first = |object: &Val, name: &str, i: i64| -> Result<Val> { call0(object, name)?.get(Val::Int(i)) };
    let datums = py::dict([
        ("compressor_front", Val::Float(11.0)),
        ("world_lift", Val::Float(201.425)),
        ("pack_y", Val::Float(14.48)),
        ("suction_lane_x", Num::of(&first(&enc, "lip_face_x", 0)?)?.add(Num::F(25.4)).val()),
        ("cond_bore_depth", enc.attr("cond_bore_depth")?),
        ("cond_mount_clear", enc.attr("cond_mount_clear")?),
        ("cond_slot_press", enc.attr("cond_slot_press")?),
        ("cond_slot_grip", enc.attr("cond_slot_grip")?),
        ("cond_rail_wall", enc.attr("cond_rail_wall")?),
        ("front_bottom_west", first(&enc, "front_bottom_flank_face", 0)?),
        ("front_bottom_east", first(&enc, "front_bottom_flank_face", 1)?),
        ("front_top_west", first(&enc, "front_top_flank_face", 0)?),
        ("front_top_east", first(&enc, "front_top_flank_face", 1)?),
        ("clearance_floor", Val::Float(1.0)),
        ("mq6_y0", Val::Float(38.3)),
        ("mq6_rail_wall", enc.attr("mq6_rail_wall")?),
        ("mq6_card_plane", first(&mq6, "card_plane", 0)?),
        ("floor_grommet_squeeze", Val::Float(0.4)),
        ("floor_boss_slip", Val::Float(1.0)),
        ("rear_plane_y", enc.attr("rear_plane_y")?),
        ("rear_seam_clear", enc.attr("rear_seam_clear")?),
        ("core_stop_rise", enc.attr("core_stop_rise")?),
        ("through_wall", Val::list(THROUGH_WALL.iter().map(|n| s(*n)).collect())),
        (
            "compressor",
            py::dict([
                ("ports", mouths(&call0(&compressor, "stations")?)?),
                ("power_face", first(&compressor, "power_face", 0)?),
                ("mount_xy", call0(&compressor, "mount_pattern")?),
                ("base_z", compressor.attr("BASE_Z")?),
                ("mount_d", compressor.attr("MOUNT_D")?),
                ("power_y", compressor.attr("POWER_Y")?),
                ("power_z", compressor.attr("POWER_Z")?),
            ]),
        ),
        ("fuse", py::dict([("length", fuse.attr("LENGTH")?), ("diameter", fuse.attr("BODY_D")?)])),
        (
            "condenser",
            py::dict([
                ("airflow", Val::Float(56.0)),
                ("face_a", Val::Float(154.0)),
                ("face_b", Val::Float(137.0)),
                ("plate_t", Val::Float(0.4)),
                ("recess_y", Val::Float(20.0)),
                ("mount_x", Val::Float(29.0)),
                ("mount_y", Val::Float(139.0)),
                ("mount_d", Val::Float(5.0)),
                (
                    "ports",
                    py::dict([
                        ("refrig-inlet", port([0.0, 87.0, 66.0], [-1.0, 0.0, 0.0], 6.35)),
                        ("refrig-outlet", port([33.0, 154.0, 38.75], [0.0, 1.0, 0.0], 6.35)),
                    ]),
                ),
            ]),
        ),
    ]);
    for (key, value) in entries_of(&manifold_datums(rt, &enc, &construction)?)? {
        datums.set(key, value)?;
    }
    let material = |name: &str| materials.iter().find(|(n, _)| *n == name).map(|(_, v)| v.clone()).context("material");
    let sources = py::dict([
        ("compressor", source_at(rt, st, &root_val, "hardware/reference/compressor/compressor.step")?),
        ("mq6", source_at(rt, st, &root_val, "hardware/reference/mq6-gas-sensor/mq6-gas-sensor.step")?),
        ("fuse", source_at(rt, st, &root_val, "hardware/reference/sf76e-thermal-fuse/sf76e-thermal-fuse.step")?),
        ("fuse_clamp", source_at(rt, st, &root_val, "hardware/printed-parts/refrigeration/fuse-clamp/fuse-clamp.step")?),
        ("manifold", s(py::path_str(&root.join("hardware/manifold-layout/manifold-layout.step.npz")))),
        ("core", s(py::path_str(&root.join("hardware/cold-core-layout/cold-core-assembly.scene.npz")))),
        ("casing", s(py::path_str(&root.join("hardware/printed-parts/cold-core/foam-assembly/foam-assembly.step.npz")))),
    ]);
    let colors = Val::dict(vec![]);
    for (name, key) in COLORS {
        colors.set(s(name), linear(rt, &material(key)?)?)?;
    }
    let above_core = py::json_loads(&py::read_text(&root.join("hardware/manifold-layout/above-core.json"))?)?;
    Ok(py::dict([
        ("stage", stage),
        ("sources", sources),
        ("datums", datums),
        ("input_root", s(py::path_str(&root))),
        ("core_datums", core),
        ("colors", colors),
        ("above_core", above_core),
        ("manifold_numbers", construction),
        ("box", box_document),
        ("equipment", Val::dict(vec![])),
        ("installed", Val::dict(vec![])),
    ]))
}

/// `_box_tuple(document, enc)`: the enclosure's `Box` from a box document.
fn box_tuple(rt: &Rt, document: &Val, enc: &Val) -> Result<Val> {
    let box_spec = rt.import("_box_spec")?;
    let records = Val::dict(vec![]);
    for kind in [enc.attr("Pack")?, enc.attr("PortField")?, enc.attr("Nameplate")?] {
        records.set(kind.attr("__name__")?, kind)?;
    }
    let box_type = enc.attr("Box")?;
    let tupled = box_spec.attr("_tupled")?;
    let body = document.get(s("box"))?;
    let mut fields = vec![];
    for field in box_type.attr("_fields")?.iter()? {
        fields.push(py::call(&tupled, vec![body.get(field)?, records.clone()])?);
    }
    py::call(&box_type, fields)
}

/// `installed_numbers(request, document, *, input_root=ROOT)`: the installed parts' datums and
/// models, added to `request`; the enclosure's box comes back.
fn installed_numbers(rt: &Rt, st: &State, request: &Val, document: &Val, input_root: &Val) -> Result<Val> {
    let enc = call0(&rt.import("_enclosure_datums")?, "load")?;
    let boxed = box_tuple(rt, document, &enc)?;
    let cradle = rt.import("elbow_cradle")?;
    let elbow = rt.import("neofit_stem_elbow")?;
    let frame = enc.attr("_funnel_frame_part")?;
    let funnel = enc.attr("_funnel")?;
    let inner = boxed.attr("inner")?;
    let outer = boxed.attr("outer")?;
    let y_joint = boxed.attr("y_joint")?;
    let cx = Num::of(&inner.get(Val::Int(0))?)?.add(Num::of(&inner.get(Val::Int(1))?)?).div(Num::F(2.0));
    let cy = frame.attr("center_y")?;
    let centre = || Val::Tuple(vec![cx.val(), cy.clone()]);
    let seat = py::method(&enc, "funnel_seat_z", vec![outer.clone()])?;
    let floor = py::method(&frame, "datums", vec![seat.clone()])?.get(Val::Int(0))?;
    let facet = py::unpack(&py::method(&enc, "_facet_geom", vec![outer.clone()])?, 5)?;
    let fasteners = py::method(&frame, "fastener_datums", vec![inner.clone(), y_joint.clone(), centre(), seat.clone()])?;
    let mut seam = vec![];
    for (side, xi, sx) in [("west", inner.get(Val::Int(0))?, 1.0), ("east", inner.get(Val::Int(1))?, -1.0)] {
        for rod in py::method(&enc, "y_stack_rods", vec![inner.clone()])?.iter()? {
            let rod = py::unpack(&rod, 7)?;
            let (station, head, tip, length, owner, insert0, insert1) =
                (&rod[0], &rod[1], &rod[2], &rod[3], &rod[4], &rod[5], &rod[6]);
            let axis = py::method(&enc, "y_stack_axis", vec![xi.clone(), Val::Float(sx), y_joint.clone(), station.clone()])?;
            let axis = py::unpack(&axis, 2)?;
            seam.push(py::dict([
                ("name", s(format!("y-seam-{side}-{}", num::fmtv(station, "")?))),
                ("x", axis[0].clone()),
                ("y", axis[1].clone()),
                ("seat", head.clone()),
                ("tip", tip.clone()),
                ("upward", Val::Bool(interop::eq(station, &s("lower"))?)),
                ("insert0", insert0.clone()),
                ("insert1", insert1.clone()),
                ("owner", owner.clone()),
                ("length", length.clone()),
            ]));
        }
    }
    // `(*point, bore)`.
    let bored = |point: Val, bore: Val| -> Result<Val> {
        let mut row = point.iter()?;
        row.push(bore);
        Ok(Val::Tuple(row))
    };
    let seat_n = Num::of(&seat)?;
    let data = py::dict([
        ("cx", cx.val()),
        ("cy", cy.clone()),
        ("funnel_seat_z", seat.clone()),
        ("cover_z", Num::of(&outer.get(Val::Int(5))?)?.add(num_attr(&funnel, "apron_rise")?).val()),
        ("frame_floor", floor),
        (
            "frame_front",
            py::method(&frame, "roof_datums", vec![inner.clone(), centre(), seat.clone(), y_joint.clone()])?.get(s("front"))?,
        ),
        ("neck_dx", funnel.attr("neck_dx")?),
        ("neck_dy", funnel.attr("neck_dy")?),
        ("cradle_catch_gap", cradle.attr("CATCH_GAP")?),
        ("cradle_source_z0", call0(&cradle, "block")?.get(Val::Int(3))?),
        ("drain_stem_tip", call0(&elbow, "stem_tip")?.get(Val::Int(0))?),
        (
            "drain_ports",
            py::dict([
                ("stub", bored(call0(&elbow, "stem_tip")?, elbow.attr("STEM_OD")?)?),
                ("outlet", bored(call0(&elbow, "socket")?, elbow.attr("TUBE_OD")?)?),
            ]),
        ),
        (
            "funnel_ports",
            py::dict([(
                "drain",
                Val::Tuple(vec![funnel.attr("drain_local")?, py::ftuple(&[0.0, 0.0, -1.0]), funnel.attr("spout_id")?]),
            )]),
        ),
        ("spout_land_z", funnel.attr("spout_land_z")?),
        ("display_angle_deg", enc.attr("display_facet_angle_deg")?),
        ("display_origin", facet[2].clone()),
        ("display_normal", facet[1].clone()),
        ("display_centre_x", py::method(&enc, "display_centre_x", vec![outer.clone()])?),
        ("display_bezel_depth", enc.attr("display_bezel_depth")?),
        ("display_native_bezel_depth", Val::Float(1.0)),
        ("display_body_offset_x", enc.attr("display_body_offset_x")?),
        ("display_body_offset_slope", enc.attr("display_body_offset_slope")?),
        (
            "display_cover_origin",
            call0(&py::method(&enc, "display_plane", vec![outer.clone()])?.attr("origin")?, "toTuple")?,
        ),
        ("funnel_fasteners", fasteners),
        ("y_seam", Val::list(seam)),
        (
            "funnel_seal",
            py::dict([
                (
                    "base",
                    Num::vals(&[
                        cx.add(num_attr(&funnel, "neck_dx")?),
                        Num::of(&cy)?.add(num_attr(&funnel, "neck_dy")?),
                        seat_n.add(num_attr(&funnel, "spout_land_z")?).sub(num_attr(&funnel, "sealing_land")?),
                    ]),
                ),
                ("outer_radius", num_attr(&elbow, "STEM_OD")?.div(Num::F(2.0)).val()),
                ("inner_radius", num_attr(&funnel, "sealing_id")?.div(Num::F(2.0)).val()),
                ("length", funnel.attr("sealing_land")?),
            ]),
        ),
    ]);
    let mut models = vec![];
    for (name, path) in INSTALLED_PATHS {
        models.push((name, source_at(rt, st, input_root, &format!("hardware/{path}"))?));
    }
    py::method(&request.get(s("sources"))?, "update", vec![py::dict(models)])?;
    let pieces = Val::dict(vec![]);
    for name in PIECES {
        let path = format!("hardware/printed-parts/enclosure/enclosure/enclosure-{name}.step");
        pieces.set(s(name), source_at(rt, st, input_root, &path)?)?;
    }
    request.set(s("piece_models"), pieces)?;
    request.set(s("installed_datums"), data)?;
    Ok(boxed)
}

/// `_run_records(frames)`: the three copper runs bent between their frames, as route records and
/// as the swept segments the machine program draws.
fn run_records(rt: &Rt, frames: &Val) -> Result<(Val, Val)> {
    call0(&rt.import("_rust_part")?, "start")?;
    let routing = rt.import("_routing")?;
    let namespace = rt.member("types", "SimpleNamespace")?;
    for item in call0(frames, "items")?.iter()? {
        let pair = py::unpack(&item, 2)?;
        let (name, row) = (&pair[0], &pair[1]);
        if !py::dget(row, "ports", Val::None)?.truthy()? {
            continue;
        }
        let bounds = py::dget(row, "bb", py::ftuple(&[0.0; 6]))?;
        let ports = Val::dict(vec![]);
        for entry in call0(&py::at(row, "ports")?, "items")?.iter()? {
            let entry = py::unpack(&entry, 2)?;
            let at = &entry[1];
            ports.set(
                entry[0].clone(),
                Val::Tuple(vec![Val::Tuple(py::at(at, "pos")?.iter()?), Val::Tuple(py::at(at, "axis")?.iter()?), py::at(at, "diam")?]),
            )?;
        }
        let fields = BOX_FIELDS.iter().zip(bounds.iter()?).map(|(k, v)| (k.to_string(), v)).collect();
        let bb = namespace.call(vec![], fields)?;
        py::call_kw(&routing.attr("frame")?, vec![name.clone(), Val::None, ports], vec![("bb", bb)])?;
    }
    let vars = interop::builtin("vars").context("vars")?;
    let mut records = vec![];
    let mut sweeps = vec![];
    for (identifier, from, to, extra) in REFRIGERANT {
        let mut kwargs = vec![("kind", s("refrigerant"))];
        kwargs.extend(extra.iter().map(|(k, v)| (*k, Val::Float(*v))));
        let run = py::call_kw(&routing.attr("bent")?, vec![s(identifier), s(from), s(to)], kwargs)?;
        let fields = vars.call(vec![run.clone()], vec![])?;
        let record = Val::dict(vec![]);
        for key in fields.iter()? {
            record.set(key.clone(), fields.get(key)?)?;
        }
        record.set(s("length"), run.attr("length")?)?;
        records.push(record);

        // Each corner's tangent set-back, `need[i]`, keyed by corner index as a dict keeps it.
        let radii = run.attr("radii")?;
        let mut corners: Vec<(Val, f64)> = vec![];
        let mut need: Vec<(Val, f64, f64)> = vec![];
        for bend in run.attr("bends")?.iter()? {
            let bend = py::unpack(&bend, 4)?;
            let turn = bend[1].num()?;
            let radius = radii.get(bend[0].clone())?.num()?;
            let back = radius * (num::radians(turn) / 2.0).tan();
            corners.push((bend[0].clone(), turn));
            let mut found = false;
            for row in need.iter_mut() {
                if interop::eq(&row.0, &bend[0])? {
                    (row.1, row.2) = (back, radius);
                    found = true;
                    break;
                }
            }
            if !found {
                need.push((bend[0].clone(), back, radius));
            }
        }
        let pts = py::snapshot(&run.attr("pts")?)?;
        let unit = routing.attr("_unit")?;
        let mut segments = vec![];
        let line = |a: Val, b: Val| py::dict([("kind", s("line")), ("points_mm", Val::list(vec![a, b]))]);
        let mut cursor = pts.get(Val::Int(0))?;
        let mut at = py::f64s(&cursor)?;
        for (i, turn) in &corners {
            let mut corner = None;
            for row in &need {
                if interop::eq(&row.0, i)? {
                    corner = Some((row.1, row.2));
                    break;
                }
            }
            let (back, radius) = corner.context("corner set-back")?;
            if back == 0. {
                continue;
            }
            let index = i.integer()?;
            let vertex = pts.get(i.clone())?;
            let incoming = xyz(&py::f64s(&py::call(&unit, vec![pts.get(Val::Int(index - 1))?, vertex.clone()])?)?)?;
            let outgoing = xyz(&py::f64s(&py::call(&unit, vec![vertex.clone(), pts.get(Val::Int(index + 1))?])?)?)?;
            let v = xyz(&py::f64s(&vertex)?)?;
            let p1: Vec<f64> = (0..3).map(|k| v[k] - incoming[k] * back).collect();
            let p2: Vec<f64> = (0..3).map(|k| v[k] + outgoing[k] * back).collect();
            let bisector: Vec<f64> = (0..3).map(|k| outgoing[k] - incoming[k]).collect();
            let span = sqrt(num::sum(bisector.iter().map(|c| c * c)))?;
            let distance = div(radius, num::cos(num::radians(*turn) / 2.0))?;
            let mut center = vec![];
            for k in 0..3 {
                center.push(v[k] + div(bisector[k], span)? * distance);
            }
            let radial: Vec<f64> = (0..3).map(|k| v[k] - center[k]).collect();
            let span = sqrt(num::sum(radial.iter().map(|c| c * c)))?;
            let mut middle = vec![];
            for k in 0..3 {
                middle.push(center[k] + div(radial[k], span)? * radius);
            }
            let (p1_val, p2_val) = (py::flist(&p1), py::flist(&p2));
            if gt(dist(&at, &p1)?, 1e-09)? {
                segments.push(line(cursor.clone(), p1_val.clone()));
            }
            segments.push(py::dict([("kind", s("arc")), ("points_mm", Val::list(vec![p1_val, py::flist(&middle), p2_val.clone()]))]));
            cursor = p2_val;
            at = p2;
        }
        let last = pts.get(Val::Int(-1))?;
        if gt(dist(&at, &py::f64s(&last)?)?, 1e-09)? {
            segments.push(line(cursor, last));
        }
        let linear = rt.member("_materials", "linear")?;
        let copper = rt.member("_materials", "M_COPPER")?;
        sweeps.push(py::dict([
            ("name", s(format!("tube-{identifier}"))),
            ("segments", Val::list(segments)),
            ("od_mm", run.attr("diam")?),
            ("id_mm", Val::Float(0.0)),
            ("color", py::call(&linear, vec![copper])?),
        ]));
    }
    Ok((Val::list(records), Val::list(sweeps)))
}

/// `_result_plan(receipt, directory, name)`: the model-reference plan a cut wrote.
fn result_plan(receipt: &Val, directory: &Path, name: &str) -> Result<Val> {
    if receipt.contains(&s("instances"))? {
        return Ok(receipt.clone());
    }
    let path = directory.join(format!("{name}.json"));
    if path.is_file() {
        return py::json_loads(&py::read_text(&path)?);
    }
    let mut results = py::dget(receipt, "results", Val::Tuple(vec![]))?.iter()?;
    results.reverse();
    for result in results {
        if result.contains(&s("instances"))? {
            return Ok(result);
        }
    }
    bail!("ValueError: {name} did not emit its model-reference plan")
}

/// `_route_records(routes)`: the equipment's fluid routes as run records.
fn route_records(routes: &Val) -> Result<Vec<Val>> {
    let mut result = vec![];
    for item in call0(routes, "items")?.iter()? {
        let pair = py::unpack(&item, 2)?;
        let (name, row) = (&pair[0], &pair[1]);
        let owners = py::dget(row, "owners", Val::Tuple(vec![s(""), s("")]))?;
        let points = py::dget(row, "points_mm", py::dget(row, "centerline_mm", Val::None)?)?;
        if matches!(points, Val::None) {
            continue;
        }
        let from = py::dget(row, "frm", py::dget(row, "from", owners.get(Val::Int(0))?)?)?;
        let to = py::dget(row, "to", owners.get(Val::Int(-1))?)?;
        let diam = py::at(row, "od_mm")?;
        let bend = py::dget(row, "minimum_radius_mm", Val::None)?;
        let bend = if bend.truthy()? { bend } else { Val::Float(0.0) };
        let note = py::dget(row, "basis", s(""))?;
        let pts = points.iter()?;
        let mut legs = vec![];
        for (a, b) in pts.iter().zip(pts.iter().skip(1)) {
            legs.push(dist(&py::f64s(a)?, &py::f64s(b)?)?);
        }
        result.push(py::dict([
            ("id", name.clone()),
            ("kind", s("fluid")),
            ("frm", from),
            ("to", to),
            ("pts", points),
            ("diam", diam),
            ("bend", bend),
            ("note", note),
            ("min_bend", Val::None),
            ("bends", Val::list(vec![])),
            ("radii", Val::dict(vec![])),
            ("caps", Val::dict(vec![])),
            ("length", num::sum_val(&legs)),
        ]));
    }
    Ok(result)
}

/// `_placement_metadata(request, equipment_request, runs)`: what the complete cut checks and
/// reports the machine against.
fn placement_metadata(rt: &Rt, request: &Val, er: &Val, runs: &Val) -> Result<Val> {
    let enc = call0(&rt.import("_enclosure_datums")?, "load")?;
    let above_core = rt.import("above_core")?;
    let wiring = rt.import("above_core_wiring")?;
    let ml = rt.import("manifold_layout")?;
    rt.import("_stated_bounds")?;
    let core = rt.import("_cold_core_interface")?;
    let anchors_module = rt.import("_reservoir_a_anchors")?;
    let barb_of = ml.attr("BARB_OF")?;
    let fore_stubs = ml.attr("FORE_STUBS")?;
    // `made(how)`: how the manifold makes one fluid connection.
    let made = |how: &Val| -> Result<Val> {
        if interop::eq(how, &s("spine"))? {
            return Ok(s("elbows"));
        }
        if barb_of.contains(how)? {
            return Ok(s("pump-dock"));
        }
        if fore_stubs.contains(how)? {
            return Ok(s("straight"));
        }
        if Val::Tuple(vec![s("turn"), s("butt")]).contains(how)? {
            return Ok(how.clone());
        }
        let ends = ml.attr("RUNS")?.get(how.clone())?.iter()?;
        ensure!(ends.len() >= 2, "missing argument 1");
        let length = dist(&py::f64s(&ends[0])?, &py::f64s(&ends[1])?)?;
        Ok(s(if gt(length, 1e-09)? { "straight" } else { "butt" }))
    };
    let holders = Val::dict(vec![]);
    let pump_at = Val::dict(vec![]);
    for item in call0(&ml.attr("PUMPS")?, "items")?.iter()? {
        let pair = py::unpack(&item, 2)?;
        pump_at.set(pair[1].clone(), pair[0].clone())?;
    }
    let segments = ml.attr("SEGMENTS")?.iter()?;
    let tube = |cid: &Val| -> Result<Val> { Ok(s(format!("tube-fluid-{}", num::fmtv(cid, "")?))) };
    for segment in &segments {
        let row = py::unpack(segment, 4)?;
        let (cid, how) = (&row[0], &row[3]);
        if barb_of.contains(how)? {
            let pump = pump_at.get(barb_of.get(how.clone())?.get(Val::Int(0))?)?;
            holders.set(tube(cid)?, interop::binary("add", pump, s("-head"))?)?;
        } else if fore_stubs.contains(how)? {
            holders.set(tube(cid)?, s("enclosure-front-top"))?;
        }
    }
    for cid in call0(&ml, "lower_links")?.iter()? {
        holders.set(tube(&cid)?, s("enclosure-front-top"))?;
    }

    let mut active = vec![];
    for run in runs.iter()? {
        active.push(run.get(s("id"))?);
    }
    let anchor_spec = call0(&anchors_module, "specification")?;
    let mut anchors = vec![];
    for row in call0(&py::snapshot(&call0(&anchors_module, "datums")?)?, "values")?.iter()? {
        let names = row.get(s("routes_west_to_east"))?.iter()?;
        let centers = row.get(s("tube_centers_world_mm"))?.iter()?;
        let axes = row.get(s("tube_axes_world"))?.iter()?;
        for ((name, point), axis) in names.iter().zip(&centers).zip(&axes) {
            let mut taken = false;
            for id in &active {
                if interop::eq(id, name)? {
                    taken = true;
                    break;
                }
            }
            if taken {
                let seat = py::dget(&row, "seat_radius_mm", anchor_spec.get(s("seat_radius_mm"))?)?;
                anchors.push(Val::Tuple(vec![point.clone(), axis.clone(), py::ftuple(&[0.0, 0.0, -1.0]), seat]));
            }
        }
    }

    let mut bounds = vec![];
    for bound in super::_stated_bounds::records(rt)? {
        let row = Val::dict(vec![]);
        dict_extend(&row, &call0(&bound, "_asdict")?)?;
        row.set(s("kind"), s("gate"))?;
        bounds.push(row);
    }
    if py::dget(request, "box", Val::None)?.truthy()? {
        let tupled = rt.import("_box_spec")?.attr("_tupled")?;
        for stated in request.get(s("box"))?.get(s("bounds"))?.iter()? {
            let row = Val::dict(vec![]);
            for item in call0(&stated, "items")?.iter()? {
                let pair = py::unpack(&item, 2)?;
                row.set(pair[0].clone(), py::call(&tupled, vec![pair[1].clone(), Val::dict(vec![])])?)?;
            }
            bounds.push(row);
        }
    }

    let routes = er.get(s("routes"))?;
    let lengths = Val::dict(vec![]);
    for item in call0(&routes, "items")?.iter()? {
        let pair = py::unpack(&item, 2)?;
        if pair[1].contains(&s("length_mm"))? {
            lengths.set(pair[0].clone(), pair[1].get(s("length_mm"))?)?;
        }
    }
    let connections = Val::dict(vec![]);
    for segment in &segments {
        let row = py::unpack(segment, 4)?;
        connections.set(s(format!("fluid-{}", row[0].str()?)), made(&row[3])?)?;
    }
    let mut cap_anchors = vec![];
    for item in call0(&core.attr("cap_anchors")?, "items")?.iter()? {
        let pair = py::unpack(&item, 2)?;
        if interop::eq(&pair[1].attr("closure")?, &s("cap"))? {
            cap_anchors.push(pair[0].clone());
        }
    }
    let keystone = || -> Result<Val> {
        request.get(s("above_core"))?.get(s("rear_wall"))?.get(s("dry_openings"))?.get(s("keystone"))?.get(s("face_center_mm"))
    };
    let metadata = py::dict([
        ("runs", runs.clone()),
        ("native_route_specs", routes.clone()),
        ("native_route_order", Val::list(routes.iter()?)),
        ("route_lengths", lengths),
        ("world_ports", er.get(s("world_ports"))?),
        ("native_connections", call0(&above_core, "logical_connections")?),
        ("manifold_connection_made", connections),
        ("refrigerant_mates", Val::list(vec![])),
        ("blocked_runs", Val::dict(vec![])),
        ("bounds", Val::list(bounds)),
        ("tube_anchor_sites", Val::list(vec![])),
        ("tube_anchor_pieces", Val::dict(vec![])),
        ("tube_anchors", Val::list(vec![])),
        ("body_anchors", Val::list(vec![])),
        ("cap_tube_anchors", Val::list(anchors)),
        ("tube_anchor_span", Val::Float(200.0)),
        ("manifold_tube_holders", holders),
        ("core_equipment_names", sorted(&call0(&above_core, "core_equipment_names")?)?),
        ("cap_anchor_names", Val::list(cap_anchors)),
        ("cap_conduits", Val::list(core.attr("cap_conduits")?.iter()?)),
        ("selected_fitting_names", er.get(s("component_order"))?),
        ("fluid_grid_assignment", request.get(s("above_core"))?.get(s("fluid_grid"))?.get(s("assignment"))?),
        ("wiring_placements", call0(&wiring, "placements")?),
        ("soft_neighbors", py::dget(&py::dget(er, "insulation", Val::dict(vec![]))?, "neighbors", Val::Tuple(vec![]))?),
        ("wall_mount_datums", call0(&enc.attr("_above_core_shell")?, "wall_mount_datums")?),
        ("keystone_station", Val::Tuple(vec![keystone()?.get(Val::Int(0))?, keystone()?.get(Val::Int(2))?])),
        ("keystone_clearances", Val::list(vec![])),
        ("core_alpha_by_name", Val::dict(vec![])),
        ("bed", py::flist(&[325.0, 320.0, 320.0])),
    ]);
    let document = rt.member("_assembly_model", "document")?;
    let alpha = py::call(&document, vec![request.get(s("sources"))?.get(s("core"))?])?;
    metadata.set(s("core_alpha_by_name"), py::dget(&alpha, "alpha_by_name", Val::dict(vec![]))?)?;
    let installed = py::dget(request, "installed_datums", Val::dict(vec![]))?;
    metadata.set(s("funnel_fasteners"), py::dget(&installed, "funnel_fasteners", Val::list(vec![]))?)?;
    metadata.set(s("funnel_seal"), py::dget(&installed, "funnel_seal", Val::None)?)?;
    metadata.set(s("y_seam_insert_datums"), py::dget(&installed, "y_seam", Val::list(vec![]))?)?;
    Ok(metadata)
}

/// `_equipment(request, prepared, directory)`: the equipment and its routes cut against the
/// referenced frames, with the copper runs and wiring junctions added.
fn equipment(rt: &Rt, st: &State, request: &Val, prepared: &Val, directory: &Path) -> Result<Val> {
    rt.import("_machine_equipment")?;
    let routes_module = rt.import("_machine_routes")?;
    let frames = prepared.get(s("metadata"))?.get(s("frames"))?;
    let ports = Val::dict(vec![]);
    for item in call0(&frames, "items")?.iter()? {
        let pair = py::unpack(&item, 2)?;
        let rows = Val::dict(vec![]);
        for entry in call0(&pair[1].get(s("ports"))?, "items")?.iter()? {
            let entry = py::unpack(&entry, 2)?;
            let row = &entry[1];
            rows.set(entry[0].clone(), Val::Tuple(vec![row.get(s("pos"))?, row.get(s("axis"))?, row.get(s("diam"))?]))?;
        }
        ports.set(pair[0].clone(), rows)?;
    }
    let none = Val::Tuple(vec![]);
    let er = super::_machine_equipment::numbers(rt, &ports, &none, &request.get(s("input_root"))?)?;
    let equipment_dir = directory.join("equipment");
    let built = super::_machine_equipment::build(rt, &Val::Path(equipment_dir.clone()), &ports, &none, &request.get(s("input_root"))?)?;
    let equipment = result_plan(&built, &equipment_dir, "machine-equipment")?;
    let model = s(py::path_str(&directory.join("equipment/machine-equipment.step.npz")));
    let route_inputs = super::_machine_routes::equipment_inputs(&er, &model, &equipment.get(s("groups"))?)?;
    let (copper_records, copper_sweeps) = run_records(rt, &frames)?;
    let copper = Val::dict(vec![]);
    for row in copper_sweeps.iter()? {
        let name = text_of(&row.get(s("name"))?)?.to_owned();
        let body = Val::dict(vec![]);
        for (key, value) in entries_of(&row)? {
            if !interop::eq(&key, &s("name"))? {
                body.set(key, value)?;
            }
        }
        body.set(s("spool"), s("copper"))?;
        copper.set(s(name.strip_prefix("tube-").unwrap_or(&name)), body)?;
    }
    route_inputs.set(s("routes"), interop::binary("or", copper, route_inputs.get(s("routes"))?)?)?;
    let routes_dir = directory.join("routes");
    let receipt = routes_module.attr("build")?.call(vec![Val::Path(routes_dir.clone())], keyword_items(route_inputs)?)?;
    let routes = result_plan(&receipt, &routes_dir, "machine-routes")?;
    let lengths = py::dget(&routes, "lengths", py::dget(&routes, "route_lengths", Val::dict(vec![]))?)?;
    let specs = er.get(s("routes"))?;
    for item in call0(&lengths, "items")?.iter()? {
        let pair = py::unpack(&item, 2)?;
        if specs.contains(&pair[0])? {
            specs.get(pair[0].clone())?.set(s("length_mm"), pair[1].clone())?;
        }
    }
    py::method(&equipment.get(s("instances"))?, "extend", vec![routes.get(s("instances"))?])?;
    equipment.set(s("route_specs"), specs.clone())?;
    let mut runs = copper_records.iter()?;
    runs.extend(route_records(&specs)?);
    equipment.set(s("metadata"), placement_metadata(rt, request, &er, &Val::list(runs))?)?;
    equipment.set(s("core_equipment"), er.get(s("core_equipment"))?)?;
    equipment.set(s("component_order"), er.get(s("component_order"))?)?;
    let world_ports = er.get(s("world_ports"))?;
    let placed = Val::dict(vec![]);
    for item in call0(&er.get(s("frames"))?, "items")?.iter()? {
        let pair = py::unpack(&item, 2)?;
        let transform = pair[1].get(s("transform"))?;
        let rows = Val::dict(vec![]);
        for entry in call0(&py::method(&world_ports, "get", vec![pair[0].clone(), Val::dict(vec![])])?, "items")?.iter()? {
            let entry = py::unpack(&entry, 2)?;
            let at = py::unpack(&entry[1], 3)?;
            rows.set(entry[0].clone(), py::dict([("pos", at[0].clone()), ("axis", at[1].clone()), ("diam", at[2].clone())]))?;
        }
        placed.set(pair[0].clone(), py::dict([("transform", transform), ("ports", rows)]))?;
    }
    equipment.set(s("frames"), placed)?;
    let wiring = rt.import("above_core_wiring")?;
    for item in call0(&call0(&wiring, "placements")?, "items")?.iter()? {
        let pair = py::unpack(&item, 2)?;
        let (name, row) = (&pair[0], &pair[1]);
        let core = py::path(&request.get(s("sources"))?.get(s("core"))?)?;
        let root = core.ancestors().nth(3).context("index out of range")?.to_owned();
        let path = format!("hardware/reference/wago-221/wago-221-{}.step", num::fmtv(&row.get(s("size"))?, "")?);
        let model = source_at(rt, st, &Val::Path(root), &path)?;
        let rotation = row.get(s("rotation"))?.iter()?;
        let translation = row.get(s("translation_mm"))?.iter()?;
        let mut transform = vec![];
        for (r, t) in rotation.iter().zip(&translation) {
            let mut line = r.iter()?;
            line.push(t.clone());
            transform.push(Val::list(line));
        }
        let instance = py::dict([
            ("model", model),
            ("name", name.clone()),
            ("transform", Val::list(transform)),
            ("color", request.get(s("colors"))?.get(s("wago"))?),
            ("owner", row.get(s("parent"))?),
        ]);
        py::method(&py::method(&equipment, "setdefault", vec![s("junctions"), Val::list(vec![])])?, "append", vec![instance])?;
    }
    Ok(equipment)
}

/// `_normal_metadata(plan, request)`: the complete plan's metadata in its reported form.
fn normal_metadata(rt: &Rt, plan: &Val, request: &Val) -> Result<Val> {
    let mounts = rt.import("_above_core_mounts")?;
    rt.import("_machine_equipment")?;
    let metadata = plan.get(s("metadata"))?;
    if interop::eq(&request.get(s("stage"))?, &s("installed"))? {
        rt.import("_machine_reporting")?;
        let canonical = super::_machine_reporting::plain(&request.get(s("box"))?.get(s("box"))?.get(s("pack"))?)?;
        let pack = metadata.get(s("pack"))?;
        for (field, value) in entries_of(&canonical)? {
            if interop::eq(&field, &s("placed"))? {
                continue;
            }
            if !pack.contains(&field)? || !interop::eq(&pack.get(field.clone())?, &value)? {
                pack.set(field, value)?;
            }
        }
    }
    metadata.set(s("enclosure_pack_body_names"), sorted(&metadata.get(s("pack"))?.get(s("placed"))?)?)?;
    let mut bodies = vec![];
    for row in request.get(s("manifold_numbers"))?.get(s("bodies"))?.iter()? {
        let name = text_of(&row.get(s("name"))?)?.to_owned();
        if !["tube-", "turn-", "step-", "stub-"].iter().any(|p| name.starts_with(p)) {
            bodies.push(name);
        }
    }
    metadata.set(s("pack_body_names"), names(bodies))?;
    let frames = metadata.get(s("frames"))?;
    py::method(&frames, "pop", vec![s("__pack_base"), Val::None])?;
    let sleeves = Val::dict(vec![]);
    for side in ["suction", "discharge"] {
        let reducer = s(format!("{side}-reducer"));
        if !frames.contains(&reducer)? {
            continue;
        }
        let joint = py::snapshot(&super::_machine_equipment::joint_numbers(rt, s(side))?)?;
        let bore = py::unpack(&joint.get(s("bore"))?.get(Val::Int(-1))?, 2)?;
        // The runtime's `**`, `+`, `-` and `/`, so the squares are its `powf` calls.
        let square = |value: Val| interop::binary("pow", value, Val::Int(2));
        let wall = interop::binary("sub", square(joint.get(s("tube_od_mm"))?)?, square(joint.get(s("tube_id_mm"))?)?)?;
        let area = interop::binary("add", square(bore[1].clone())?, interop::binary("truediv", wall, Val::Float(4.0))?)?;
        let radius = sqrt(area.num()?)?;
        sleeves.set(
            s(side),
            py::dict([("radius", Val::Float(radius)), ("trim", bore[0].clone()), ("transform", frames.get(reducer)?.get(s("transform"))?)]),
        )?;
    }
    metadata.set(s("reducer_sleeves"), sleeves)?;
    metadata.set(s("union_supports"), call0(&mounts, "union_support_datums")?)?;
    let installed = py::dget(request, "installed_datums", Val::dict(vec![]))?;
    metadata.set(s("funnel_fasteners"), py::dget(&installed, "funnel_fasteners", Val::list(vec![]))?)?;
    metadata.set(s("funnel_seal"), py::dget(&installed, "funnel_seal", Val::None)?)?;
    let mut inserts = vec![];
    for row in py::dget(&installed, "y_seam", Val::list(vec![]))?.iter()? {
        inserts.push(py::dict([
            ("name", interop::binary("add", row.get(s("name"))?, s("-insert"))?),
            ("host", interop::binary("add", s("enclosure-"), row.get(s("owner"))?)?),
            ("x", row.get(s("x"))?),
            ("y", row.get(s("y"))?),
            ("z0", row.get(s("insert0"))?),
            ("z1", row.get(s("insert1"))?),
        ]));
    }
    metadata.set(s("y_seam_insert_datums"), Val::list(inserts))?;
    Ok(plan.clone())
}

/// `_bind_presentations(plan, input_root=ROOT)`: each instance whose model has a fine payload
/// beside it is drawn with that payload.
fn bind_presentations(st: &State, plan: &Val, input_root: &Val) -> Result<Val> {
    let mut manifests: Vec<(PathBuf, Val)> = vec![];
    let skins = py::method(plan, "setdefault", vec![s("presentation"), Val::list(vec![])])?;
    let sort_keys = || vec![("sort_keys", Val::Bool(true))];
    let mut existing = vec![];
    for row in skins.iter()? {
        existing.push(py::json_dumps(&row, sort_keys())?);
    }
    for row in plan.get(s("instances"))?.iter()? {
        let model = py::path(&row.get(s("model"))?)?;
        let folder = parent(&model);
        let manifest = match manifests.iter().find(|(path, _)| *path == folder) {
            Some((_, manifest)) => manifest.clone(),
            None => {
                let path = folder.join("frozen-asset.json");
                let manifest = if path.is_file() { py::json_loads(&py::read_text(&path)?)? } else { Val::dict(vec![]) };
                manifests.push((folder.clone(), manifest.clone()));
                manifest
            }
        };
        let fine = py::dget(&manifest, "fine_model", Val::dict(vec![]))?;
        let name = model.file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_default();
        if !interop::eq(&py::dget(&fine, "path", Val::None)?, &s(name))? {
            continue;
        }
        let mut payload = folder.join(manifest.get(s("fine_payload"))?.get(s("path"))?.str()?);
        if !payload.is_file() && payload.starts_with(&st.root) {
            payload = py::path(input_root)?.join(payload.strip_prefix(&st.root)?);
        }
        let skin = py::dict([
            ("payload", s(py::path_str(&payload))),
            ("indices", py::dget(&row, "indices", Val::None)?),
            ("transform", row.get(s("transform"))?),
            ("targets", Val::list(vec![row.get(s("name"))?])),
        ]);
        let key = py::json_dumps(&skin, sort_keys())?;
        if !existing.contains(&key) {
            py::method(&skins, "append", vec![skin])?;
            existing.push(key);
        }
    }
    Ok(plan.clone())
}

/// `_work_directory(*parts)`: a scratch directory under the part runner's root.
fn work_directory(rt: &Rt, parts: &[Val]) -> Result<Val> {
    let root = rt.import("_rust_part")?.attr("ROOT")?;
    let base = interop::binary("truediv", root, s("tmp/machine-layout"))?;
    let mut tail = PathBuf::new();
    for part in parts {
        tail.push(part.str()?);
    }
    interop::binary("truediv", base, Val::Path(tail))
}

/// `local(value)`: the plan with the staged model's path replaced by the installed one.
fn local(value: &Val, staged: &Val, installed: &str) -> Result<Val> {
    Ok(match value {
        Val::Dict(_) => {
            let out = Val::dict(vec![]);
            for (key, row) in entries_of(value)? {
                out.set(key, local(&row, staged, installed)?)?;
            }
            out
        }
        Val::List(rows) => {
            let rows = rows.borrow().clone();
            Val::list(rows.iter().map(|row| local(row, staged, installed)).collect::<Result<_>>()?)
        }
        _ if interop::eq(value, staged)? => s(installed),
        _ => value.clone(),
    })
}

/// `_run(request, directory)`: one cut of the machine program, its plan read back with local
/// model paths and fine presentations bound.
fn run(rt: &Rt, st: &State, request: &Val, directory: &Path) -> Result<Val> {
    let rust_part = rt.import("_rust_part")?;
    py::mkdirs(directory)?;
    let output = directory.join("machine-layout.json");
    let payload = py::dict([("request", request.clone())]);
    py::call(&rust_part.attr("cut")?, vec![s("machine"), s("machine-layout"), payload, Val::Path(directory.to_owned())])?;
    let plan = py::json_loads(&py::read_text(&output)?)?;
    let staged = plan.get(s("generated_model"))?;
    let installed = py::path_str(&py::resolve(&directory.join("machine-layout.parts.npz"))?);
    let input_root = py::dget(request, "input_root", Val::Path(st.root.clone()))?;
    let plan = bind_presentations(st, &local(&plan, &staged, &installed)?, &input_root)?;
    let separators = Val::Tuple(vec![s(","), s(":")]);
    write_text(&output, py::json_dumps(&plan, vec![("separators", separators)])? + "\n")?;
    Ok(plan)
}

/// `plan(*, stage='pack', box_document=None, directory=None, input_root=ROOT)`: the machine's
/// placed plan, cut whole for the pack or installed stage.
fn plan(rt: &Rt, st: &State, stage: &Val, box_document: &Val, directory: Val, input_root: &Val) -> Result<Val> {
    let directory = if matches!(directory, Val::None) { work_directory(rt, &[stage.clone()])? } else { directory };
    let directory = py::path(&directory)?;
    let request = numbers(rt, st, s("pack"), box_document.clone(), input_root)?;
    let prepared = run(rt, st, &request, &directory.join("references"))?;
    if interop::eq(stage, &s("installed"))? {
        let boxed = installed_numbers(rt, st, &request, box_document, input_root)?;
        let driver = rt.import("_enclosure_rust_driver")?;
        let installed = py::call(&driver.attr("installed_instances")?, vec![box_document.clone(), Val::Path(directory.join("enclosure"))])?;
        request.set(s("installed"), installed)?;
        let mut panels = vec![];
        for name in PANELS {
            let path = format!("hardware/printed-parts/enclosure/enclosure/enclosure-{name}.step");
            panels.push(py::dict([
                ("model", source_at(rt, st, input_root, &path)?),
                ("name", s(format!("enclosure-{name}"))),
                ("color", request.get(s("colors"))?.get(s("display_cover"))?),
            ]));
        }
        let ordinary = py::method(&request.get(s("installed"))?, "setdefault", vec![s("instances"), Val::list(vec![])])?;
        for row in ordinary.iter()? {
            let word = py::method(&py::dget(&row, "name", s(""))?, "endswith", vec![s("-word")])?;
            if word.truthy()? || interop::eq(&py::dget(&row, "name", Val::None)?, &s("nameplate-ink"))? {
                row.set(s("split_components"), Val::Bool(true))?;
            }
        }
        let mut retainer = vec![];
        for row in ordinary.iter()? {
            if interop::eq(&py::dget(&row, "name", Val::None)?, &s("enclosure-pump-retainer"))? {
                retainer.push(row);
            }
        }
        let retainer = Val::list(retainer);
        let mut rows = vec![];
        for row in ordinary.iter()? {
            if !retainer.contains(&row)? {
                rows.push(row);
            }
        }
        rows.extend(panels);
        rows.extend(retainer.iter()?);
        request.get(s("installed"))?.set(s("instances"), Val::list(rows))?;
        let plate = boxed.attr("pack")?.attr("collet_plate")?;
        let dock = dock_instances(rt, st, &plate, Val::Path(directory.join("dock")), input_root)?;
        request.set(s("dock"), dock)?;
    }
    let equipment = equipment(rt, st, &request, &prepared, &directory)?;
    request.set(s("prepared"), prepared)?;
    request.set(s("equipment"), equipment)?;
    request.set(s("stage"), stage.clone())?;
    let result = normal_metadata(rt, &run(rt, st, &request, &directory.join("complete"))?, &request)?;
    write_text(&directory.join("complete/machine-layout.json"), py::json_dumps(&result, vec![])? + "\n")?;
    Ok(result)
}

/// `dock_instances(plate, directory=None, *, input_root=ROOT)`: the pump dock's tees and stem
/// elbows placed on the collet plate.
fn dock_instances(rt: &Rt, st: &State, plate: &Val, directory: Val, input_root: &Val) -> Result<Val> {
    let enc = call0(&rt.import("_enclosure_datums")?, "load")?;
    let acetal = rt.member("_materials", "M_NEOFIT_WHITE_ACETAL")?;
    let black = rt.member("_materials", "M_JG_BLACK_PP")?;
    let dock = enc.attr("_dock")?;
    let plumbing = dock.attr("plumbing")?;
    let layouts = py::snapshot(&py::method(&plumbing, "layouts", vec![plate.clone()])?)?;
    let mut rows = vec![];
    for station in py::method(&dock, "stations", vec![plate.clone()])?.iter()? {
        let station = py::unpack(&station, 4)?;
        let (tee, x, z) = (&station[1], &station[2], &station[3]);
        let key = s(x.str()?);
        let target = plate.get(s("return_ports"))?.get(key.clone())?;
        let tee_y = py::method(&plumbing, "tee_axis_y", vec![plate.get(s("fore_y"))?])?;
        let hosts = [tee.clone(), target.get(s("valve"))?];
        let placed = layouts.get(key)?.get(s("return"))?.get(s("elbows"))?.iter()?;
        let mut elbows = vec![];
        for (host, row) in hosts.iter().zip(&placed) {
            let elbow = py::dict([("name", interop::binary("add", s("stem-elbow-"), call0(host, "lower")?)?)]);
            for key in row.iter()? {
                elbow.set(key.clone(), row.get(key)?)?;
            }
            elbows.push(elbow);
        }
        rows.push(py::dict([
            ("tee", interop::binary("add", s("tee-"), call0(tee, "lower")?)?),
            ("x", x.clone()),
            ("z", z.clone()),
            ("tee_y", tee_y),
            ("elbows", Val::list(elbows)),
        ]));
    }
    let request = py::dict([
        ("stage", s("dock")),
        (
            "sources",
            py::dict([
                ("tee", source_at(rt, st, input_root, "hardware/reference/tee-connector/tee-connector.step")?),
                ("stem_elbow", source_at(rt, st, input_root, "hardware/reference/neofit-stem-elbow/neofit-stem-elbow.step")?),
            ]),
        ),
        ("dock_rows", Val::list(rows)),
        ("hub_back_reach", dock.attr("stem_elbow")?.attr("HUB_BACK_REACH")?),
        ("colors", py::dict([("tee", linear(rt, &black)?), ("elbow", linear(rt, &acetal)?)])),
    ]);
    let directory = if matches!(directory, Val::None) { work_directory(rt, &[s("dock")])? } else { directory };
    run(rt, st, &request, &py::path(&directory)?)
}

/// `name.rsplit('/', 1)`: a numbered body's logical name.
fn logical_name(name: &str) -> String {
    match name.rsplit_once('/') {
        Some((head, tail)) if digits(tail) => head.to_owned(),
        _ => name.to_owned(),
    }
}

/// `main()`: the installed machine's plan, physical STEP, wiring, checks, scene and reports.
fn main(rt: &Rt, st: &State) -> Result<Val> {
    let box_spec = rt.import("_box_spec")?;
    rt.import("_machine_export")?;
    let checks = rt.import("_machine_checks")?;
    rt.import("_machine_reporting")?;
    let box_document = py::json_loads(&call0(&box_spec.attr("ARTIFACT")?, "read_text")?.str()?)?;
    let spec = plan(rt, st, &s("installed"), &box_document, Val::None, &Val::Path(st.root.clone()))?;
    let output = st.layout.join("enclosure-assembly.step");
    let physical = py::merged(&spec, [("physical_presentation", s("enclosure-assembly.physical.step.mesh"))])?;
    let produced = super::_machine_export::export(rt, &physical, &Val::Path(parent(&output)))?;
    let model = s(py::path_str(&output) + ".npz");
    let metadata = spec.get(s("metadata"))?;
    let export_from_fine = rt.member("hardware.wiring.installed.build", "export_from_fine")?;
    let scalars = super::_machine_reporting::scalar_namespace(rt, &spec)?;
    py::call(&export_from_fine, vec![model.clone(), Val::Path(output.clone()), scalars])?;
    let identity = rt.member("_assembly_model", "identity")?;
    let mut wiring = vec![];
    for item in py::call(&identity, vec![Val::Path(st.hw.join("wiring/enclosure-wiring.step.npz"))])?.iter()? {
        let pair = py::unpack(&item, 2)?;
        wiring.push(logical_name(text_of(&pair[0])?));
    }
    metadata.set(s("wiring_names"), names(wiring))?;
    let aliases = || py::dget(&spec, "aliases", Val::dict(vec![]));
    let checked = py::call_kw(
        &checks.attr("check")?,
        vec![model.clone()],
        vec![("envelope", spec.get(s("envelope"))?), ("aliases", aliases()?), ("metadata", metadata.clone())],
    )?;
    metadata.set(s("mounts"), py::dget(&checked, "mounts", Val::list(vec![]))?)?;
    metadata.set(s("rides"), py::dget(&checked, "rides", Val::dict(vec![]))?)?;
    let document = super::_machine_reporting::scene_document(rt, &spec, &checked, &Val::None)?;
    let scene = st.layout.join("enclosure-assembly.scene.npz");
    super::_machine_export::scene(rt, &model, &Val::Path(scene.clone()), aliases()?, &spec.get(s("envelope"))?, document)?;
    let reports = [("enclosure-assembly.scorecard.json", checked.get(s("scorecard"))?), ("drain-clearance-check.json", checked.get(s("drain"))?)];
    for (name, value) in reports {
        write_text(&st.layout.join(name), py::json_dumps(&value, vec![("indent", Val::Int(2))])? + "\n")?;
    }
    let paths = py::dict([
        ("scene_path", Val::Path(scene)),
        ("step_path", Val::Path(output)),
        ("scorecard_path", Val::Path(st.layout.join("enclosure-assembly.scorecard.json"))),
    ]);
    super::_machine_reporting::write(rt, &spec, &checked, &model, paths)?;
    spec.set(s("checks"), checked.clone())?;
    view_metadata(rt, st, &spec, &model)?;
    py::sys_path_insert(rt, &py::path_str(&st.hw.join("assembly/scenes")))?;
    let render = rt.import("render_scenes")?;
    py::call_kw(&render.attr("write_glbs")?, vec![spec.clone()], vec![("require_core_payload", Val::Bool(true))])?;
    Ok(Val::Tuple(vec![produced, checked]))
}

/// `struct.unpack('f', struct.pack('f', value))[0]`: a channel at single precision.
fn single(value: &Val) -> Result<Val> {
    Ok(Val::Float(value.num()? as f32 as f64))
}

/// `_view_metadata(spec, model)`: the viewer's colours and payloads, added to the spec.
fn view_metadata(rt: &Rt, st: &State, spec: &Val, model: &Val) -> Result<()> {
    let assembly_model = rt.import("_assembly_model")?;
    let glass = rt.member("_materials", "C_DISPLAY_GLASS")?;
    let pvc = rt.member("_materials", "M_PVC_CLEAR")?;
    let metadata = spec.get(s("metadata"))?;
    metadata.set(s("core_carry3x4"), metadata.get(s("core_carry"))?)?;
    let colours = Val::dict(vec![]);
    let alpha = py::dget(&metadata, "core_alpha_by_name", Val::dict(vec![]))?;
    let opacity = |material: &Val| -> Result<Val> { call0(material, "toTuple")?.get(Val::Int(-1)) };
    let direct = py::dict([("suction-tube", opacity(&pvc)?), ("discharge-tube", opacity(&pvc)?), ("display", opacity(&glass)?)]);
    for item in py::call(&assembly_model.attr("identity")?, vec![model.clone()])?.iter()? {
        let pair = py::unpack(&item, 2)?;
        let full = text_of(&pair[0])?;
        let (stem, tail) = full.rsplit_once('/').unwrap_or(("", full));
        let name = if digits(tail) { stem.to_owned() } else { full.to_owned() };
        let color = &pair[1];
        if matches!(color, Val::None) {
            continue;
        }
        let logical = name.strip_prefix("cold-core/").unwrap_or(&name);
        let fallback = py::method(&alpha, "get", vec![s(logical), Val::Float(1.0)])?;
        let mut channels = color.iter()?;
        channels.push(py::method(&direct, "get", vec![s(logical), fallback])?);
        let rgba = channels.iter().map(single).collect::<Result<Vec<_>>>()?;
        colours.set(s(name.as_str()), Val::list(rgba))?;
    }
    metadata.set(s("rgba"), colours.clone())?;
    metadata.set(s("colours"), colours.clone())?;
    let core = Val::dict(vec![]);
    for (name, color) in entries_of(&colours)? {
        if let Some(logical) = text_of(&name)?.strip_prefix("cold-core/") {
            core.set(s(logical), color)?;
        }
    }
    metadata.set(s("core_rgba"), core)?;
    spec.set(s("payload"), s(py::path_str(&st.layout.join("enclosure-assembly.step.mesh"))))?;
    spec.set(s("core_payload"), s(py::path_str(&st.hw.join("cold-core-layout/cold-core-assembly.step.mesh"))))?;
    Ok(())
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::MACHINE_LAYOUT))?;
    ns.set("json", rt.import("json")?)?;
    ns.set("math", rt.import("math")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    ns.set("sys", rt.import("sys")?)?;
    let here = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    let root = here.ancestors().nth(3).context("index out of range")?.to_owned();
    ns.set("ROOT", Val::Path(root.clone()))?;
    let hw = root.join("hardware");
    ns.set("HW", Val::Path(hw.clone()))?;
    let layout = hw.join("manifold-layout");
    ns.set("LAYOUT", Val::Path(layout.clone()))?;
    let enclosure = hw.join("printed-parts/enclosure/enclosure");
    ns.set("ENCLOSURE", Val::Path(enclosure.clone()))?;
    let search = [
        root.clone(),
        layout.clone(),
        enclosure,
        hw.join("cold-core-layout"),
        hw.join("reference/compressor"),
        hw.join("reference/mq6-gas-sensor"),
        hw.join("reference/sf76e-thermal-fuse"),
    ];
    for path in search {
        ns.set("_path", Val::Path(path.clone()))?;
        let text = py::path_str(&path);
        if !py::sys_path_has(rt, &text)? {
            py::sys_path_insert(rt, &text)?;
        }
    }
    let default_root = Val::Path(root.clone());
    rt.keep(MODULE, State { root, hw, layout });

    ns.def(rt, "_source", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["root", "path"], &[])?;
        let (root, path) = (a.req("root")?, a.req("path")?);
        source(rt, &*state(rt)?, &root, &py::path(&path)?)
    })?;
    ns.def(rt, "_linear", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["color"], &[])?;
        linear(rt, &a.req("color")?)
    })?;
    ns.def(rt, "_point", |_, args, kw| {
        let mut a = py::bind(args, kw, &["frame", "point"], &[])?;
        let (frame, point) = (a.req("frame")?, a.req("point")?);
        apply(&frame, &point, true)
    })?;
    ns.def(rt, "_axis", |_, args, kw| {
        let mut a = py::bind(args, kw, &["frame", "axis"], &[])?;
        let (frame, axis) = (a.req("frame")?, a.req("axis")?);
        apply(&frame, &axis, false)
    })?;
    ns.def(rt, "_installed", |_, args, kw| {
        let mut a = py::bind(args, kw, &["point"], &[])?;
        Ok(Num::vals(&installed(Num::three(&a.req("point")?)?)))
    })?;
    ns.def(rt, "_manifold_datums", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["enc", "construction"], &[])?;
        let (enc, construction) = (a.req("enc")?, a.req("construction")?);
        manifold_datums(rt, &enc, &construction)
    })?;
    let root = default_root.clone();
    ns.def(rt, "numbers", move |rt, args, kw| {
        let mut a = py::bind(args, kw, &[], &["stage", "box_document", "input_root"])?;
        let stage = a.opt("stage").unwrap_or_else(|| s("pack"));
        let box_document = a.opt("box_document").unwrap_or(Val::None);
        let input_root = a.opt("input_root").unwrap_or_else(|| root.clone());
        numbers(rt, &*state(rt)?, stage, box_document, &input_root)
    })?;
    ns.def(rt, "_box_tuple", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["document", "enc"], &[])?;
        let (document, enc) = (a.req("document")?, a.req("enc")?);
        box_tuple(rt, &document, &enc)
    })?;
    let root = default_root.clone();
    ns.def(rt, "installed_numbers", move |rt, args, kw| {
        let mut a = py::bind(args, kw, &["request", "document"], &["input_root"])?;
        let (request, document) = (a.req("request")?, a.req("document")?);
        let input_root = a.opt("input_root").unwrap_or_else(|| root.clone());
        installed_numbers(rt, &*state(rt)?, &request, &document, &input_root)
    })?;
    ns.def(rt, "_run_records", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["frames"], &[])?;
        let (records, sweeps) = run_records(rt, &a.req("frames")?)?;
        Ok(Val::Tuple(vec![records, sweeps]))
    })?;
    ns.def(rt, "_result_plan", |_, args, kw| {
        let mut a = py::bind(args, kw, &["receipt", "directory", "name"], &[])?;
        let (receipt, directory, name) = (a.req("receipt")?, a.req("directory")?, a.req("name")?);
        result_plan(&receipt, &py::path(&directory)?, &name.str()?)
    })?;
    ns.def(rt, "_route_records", |_, args, kw| {
        let mut a = py::bind(args, kw, &["routes"], &[])?;
        Ok(Val::list(route_records(&a.req("routes")?)?))
    })?;
    ns.def(rt, "_placement_metadata", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["request", "equipment_request", "runs"], &[])?;
        let (request, er, runs) = (a.req("request")?, a.req("equipment_request")?, a.req("runs")?);
        placement_metadata(rt, &request, &er, &runs)
    })?;
    ns.def(rt, "_equipment", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["request", "prepared", "directory"], &[])?;
        let (request, prepared, directory) = (a.req("request")?, a.req("prepared")?, a.req("directory")?);
        equipment(rt, &*state(rt)?, &request, &prepared, &py::path(&directory)?)
    })?;
    ns.def(rt, "_normal_metadata", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["plan", "request"], &[])?;
        let (plan, request) = (a.req("plan")?, a.req("request")?);
        normal_metadata(rt, &plan, &request)
    })?;
    let root = default_root.clone();
    ns.def(rt, "_bind_presentations", move |rt, args, kw| {
        let mut a = py::bind(args, kw, &["plan", "input_root"], &[])?;
        let plan = a.req("plan")?;
        let input_root = a.opt("input_root").unwrap_or_else(|| root.clone());
        bind_presentations(&*state(rt)?, &plan, &input_root)
    })?;
    ns.def(rt, "_work_directory", |rt, args, kw| {
        ensure!(kw.is_empty(), "unexpected keyword arguments {:?}", kw.iter().map(|(k, _)| k).collect::<Vec<_>>());
        work_directory(rt, &args)
    })?;
    ns.def(rt, "_run", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["request", "directory"], &[])?;
        let (request, directory) = (a.req("request")?, a.req("directory")?);
        run(rt, &*state(rt)?, &request, &py::path(&directory)?)
    })?;
    let root = default_root.clone();
    ns.def(rt, "plan", move |rt, args, kw| {
        let mut a = py::bind(args, kw, &[], &["stage", "box_document", "directory", "input_root"])?;
        let stage = a.opt("stage").unwrap_or_else(|| s("pack"));
        let box_document = a.opt("box_document").unwrap_or(Val::None);
        let directory = a.opt("directory").unwrap_or(Val::None);
        let input_root = a.opt("input_root").unwrap_or_else(|| root.clone());
        plan(rt, &*state(rt)?, &stage, &box_document, directory, &input_root)
    })?;
    let root = default_root;
    ns.def(rt, "dock_instances", move |rt, args, kw| {
        let mut a = py::bind(args, kw, &["plate", "directory"], &["input_root"])?;
        let plate = a.req("plate")?;
        let directory = a.opt("directory").unwrap_or(Val::None);
        let input_root = a.opt("input_root").unwrap_or_else(|| root.clone());
        dock_instances(rt, &*state(rt)?, &plate, directory, &input_root)
    })?;
    ns.def(rt, "main", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        main(rt, &*state(rt)?)
    })?;
    ns.def(rt, "_view_metadata", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["spec", "model"], &[])?;
        let (spec, model) = (a.req("spec")?, a.req("model")?);
        view_metadata(rt, &*state(rt)?, &spec, &model)?;
        Ok(Val::None)
    })?;
    Ok(())
}
