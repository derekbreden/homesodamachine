//! Pump case — two-piece enclosure for a peristaltic pump.
//!
//! Base: base plate with octagon-to-footprint ramp, octagon pump bore,
//!       and a cylindrical tower below.
//! Cap:  asymmetric flared skirt (wide on +Y, narrow on -Y) with a lower
//!       extension that tapers to uniform width.
//!
//! The two parts mate at a stepped split surface and lock together with
//! snap-fit ramps on four interior walls.
//!
//! Typed API: [`state`] holds the case's stock as a [`Case`] (`pump-case-defaults`, the names the
//! module's `globals().update(_case)` binds) and that reply as JSON (what `case=_case` sends a
//! recipe). The profile recipes ([`offset_polygon`], [`rounded_rect_profile`],
//! [`split_skirt_profile`], [`skirt_profile_set`], [`lower_profile_set`], [`stack_profiles`],
//! [`ring`], [`bore_octagon_profile`]) give [`Profile`]s; [`lower_z_steps`], [`stack_levels`] and
//! [`flank_ramp_bands`] are numbers; the CadQuery builders take and return CadQuery objects as
//! `Val`. No other code replaces this module's names, so typed callers call these directly.
use super::num::{self, Num};
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result, anyhow, bail, ensure};
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "pump_case";

/// A closed outline's points, `(x, y)` about the footprint's centre.
pub type Profile = Vec<[f64; 2]>;

macro_rules! case {
    ($($name:ident),* $(,)?) => {
        /// The case's stock, as `pump-case-defaults` states it: every name the module's
        /// `globals().update(_case)` binds.
        #[derive(Clone, Debug)]
        pub struct Case {
            $(pub $name: f64,)*
            pub arc_segments: i64,
            pub arch_hole_xs: [f64; 2],
            pub skirt_transition_y_mid: [f64; 2],
            pub skirt_transition_y_end: [f64; 2],
            pub skirt_z_steps: [f64; 4],
            pub bore_profile: Profile,
            pub bore_wall_profile: Profile,
            pub skirt_outer_profiles: Vec<Profile>,
            pub skirt_inner_profiles: Vec<Profile>,
        }
        impl Case {
            fn of(v: &Value) -> Result<Case> {
                Ok(Case {
                    $($name: number(v, stringify!($name))?,)*
                    arc_segments: v["arc_segments"].as_i64().context("arc_segments is an integer")?,
                    arch_hole_xs: numbers(&v["arch_hole_xs"])?,
                    skirt_transition_y_mid: numbers(&v["skirt_transition_y_mid"])?,
                    skirt_transition_y_end: numbers(&v["skirt_transition_y_end"])?,
                    skirt_z_steps: numbers(&v["skirt_z_steps"])?,
                    bore_profile: profile(&v["bore_profile"])?,
                    bore_wall_profile: profile(&v["bore_wall_profile"])?,
                    skirt_outer_profiles: profiles(&v["skirt_outer_profiles"])?,
                    skirt_inner_profiles: profiles(&v["skirt_inner_profiles"])?,
                })
            }
        }
    };
}
case!(
    footprint_x,
    footprint_y,
    corner_r,
    wall_thickness,
    center_x,
    center_y,
    footprint_half_extent,
    base_thickness,
    ramp_from_skirt_to_octagon_height,
    skirt_upper_height,
    skirt_wall,
    skirt_wide_flare_per_side,
    skirt_narrow_taper_per_side,
    skirt_wide_straight_height,
    skirt_support_band,
    bore_square_side,
    ledge_depth,
    ledge_shelf_span,
    bore_half_diag,
    bore_half_span,
    vertex_far,
    vertex_near,
    tower_height,
    tower_cap_thickness,
    cylinder_id,
    cylinder_r_inner,
    lower_height,
    lower_cap_thickness,
    lower_footprint_straight,
    step_height,
    step_y_clearance,
    snap_zone_width,
    snap_wall_height,
    snap_deflection,
    arch_radius,
    arch_pitch,
    snap_protrusion_per_side,
    tube_protrusion_length,
    case_outer_x,
    case_outer_y,
    case_outer_z,
    cutter_half_extent,
    overcut,
    octagon_wall_outer_extent,
    bore_depth,
    bore_bottom_z,
    cylinder_cardinal_step,
    cylinder_r_outer,
    cylinder_top_z,
    cylinder_bottom_z,
    skirt_base_half_extent,
    skirt_wide_half_extent,
    skirt_narrow_half_extent,
    skirt_wide_full_width,
    skirt_narrow_full_width,
    skirt_mid_narrow_half_extent,
    skirt_narrow_straight_height,
    skirt_transition_y_end_plus,
    skirt_bottom_z,
    narrow_split_z,
    lower_ramp_height,
    lower_cap_top_z,
    lower_cap_bottom_z,
    pos_y_face_y,
);

/// The module's typed state.
pub struct State {
    pub case: Case,
    /// `_case`: the defaults reply, as a recipe takes it back.
    pub json: Value,
    /// `_here`: this module's directory.
    pub here: PathBuf,
    cq: Val,
    world_workplane: Val,
    xy_plane_z_up: Val,
    xz_plane_y_up: Val,
    frame: Val,
    apply_ramp_out_first: Val,
    apply_ramp_in_first: Val,
}

/// The module's state, initializing the module on first use.
pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

fn number(v: &Value, key: &str) -> Result<f64> {
    v[key].as_f64().with_context(|| format!("{key} is numeric"))
}
fn numbers<const N: usize>(v: &Value) -> Result<[f64; N]> {
    let rows = v.as_array().context("a list of numbers")?;
    ensure!(rows.len() == N, "expected {N} numbers, got {}", rows.len());
    let mut out = [0.; N];
    for (slot, x) in out.iter_mut().zip(rows) {
        *slot = x.as_f64().context("a number")?;
    }
    Ok(out)
}
fn profile(v: &Value) -> Result<Profile> {
    v.as_array().context("a point list")?.iter().map(numbers::<2>).collect()
}
fn profiles(v: &Value) -> Result<Vec<Profile>> {
    v.as_array().context("a list of outlines")?.iter().map(profile).collect()
}
fn nums(values: &[f64]) -> Vec<Num> {
    values.iter().map(|&x| Num::F(x)).collect()
}
fn nth(mut values: Vec<Profile>, index: usize) -> Result<Profile> {
    ensure!(index < values.len(), "list index out of range");
    Ok(values.swap_remove(index))
}

/// `[tuple(p) for p in points]`.
pub fn profile_val(points: &[[f64; 2]]) -> Val {
    Val::list(points.iter().map(|p| py::ftuple(p)).collect())
}
/// A recipe's point list as `[tuple(p) for p in ...]` reads it, each number as the JSON holds it.
fn tuples(v: &Value) -> Result<Val> {
    let rows = v.as_array().context("a point list")?;
    let points = rows.iter().map(|p| {
        let p = p.as_array().context("a point")?;
        Ok(Val::Tuple(p.iter().cloned().map(Val::decode).collect::<Result<_>>()?))
    });
    Ok(Val::list(points.collect::<Result<_>>()?))
}
/// `list(section)` as the JSON a recipe receives.
fn listed(section: &Val) -> Result<Value> {
    let section = py::snapshot(section)?;
    match section {
        Val::List(_) | Val::Tuple(_) => py::plain(&section),
        other => Ok(Value::Array(other.iter()?.iter().map(py::plain).collect::<Result<_>>()?)),
    }
}
fn profile_of(v: &Val) -> Result<Profile> {
    py::snapshot(v)?.iter()?.iter().map(py::v2).collect()
}

/// `_read(op, **values)`: this crate's own recipe, answered in this process. A recipe's error
/// reads as the worker round trip raises it.
fn read(rt: &Rt, request: Value) -> Result<Value> {
    rt.enclosure_data(request).map_err(|error| anyhow!("ValueError: enclosure-data: {error:#}"))
}

/// `next(p for p in path.parents if test(p))`.
fn ancestor(path: &Path, test: impl Fn(&Path) -> bool) -> Result<PathBuf> {
    path.ancestors().skip(1).find(|p| test(p)).map(Path::to_owned).context("StopIteration")
}
fn name_of(path: &Path) -> String {
    path.file_name().map(|v| v.to_string_lossy().to_string()).unwrap_or_default()
}
/// `path.parent`.
fn parent(path: &Path) -> PathBuf {
    path.parent().unwrap_or(path).to_owned()
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("math", rt.import("math")?)?;
    ns.set("sys", rt.import("sys")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let here = parent(&py::resolve(&py::path(&ns.get("__file__")?)?)?);
    ns.set("_here", Val::Path(here.clone()))?;
    let printed = ancestor(&here, |p| name_of(p) == "printed-parts")?;
    py::sys_path_insert(rt, &py::path_str(&printed.join("cadlib")))?;
    let hardware = ancestor(&here, |p| name_of(p) == "hardware")?;
    py::sys_path_insert(rt, &py::path_str(&hardware.join("scripts")))?;
    let tools = ancestor(&here, |p| p.join("tools").join("docgen").is_dir())?;
    py::sys_path_insert(rt, &py::path_str(&tools.join("tools")))?;
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    let world_workplane = rt.member("world_workplane", "WorldWorkplane")?;
    ns.set("WorldWorkplane", world_workplane.clone())?;
    let xy_plane_z_up = rt.member("world_workplane", "xy_plane_z_up")?;
    ns.set("xy_plane_z_up", xy_plane_z_up.clone())?;
    let xz_plane_y_up = rt.member("world_workplane", "xz_plane_y_up")?;
    ns.set("xz_plane_y_up", xz_plane_y_up.clone())?;
    let frame = rt.member("snap", "Frame")?;
    ns.set("Frame", frame.clone())?;
    let apply_ramp_out_first = rt.member("snap", "apply_ramp_out_first")?;
    ns.set("apply_ramp_out_first", apply_ramp_out_first.clone())?;
    let apply_ramp_in_first = rt.member("snap", "apply_ramp_in_first")?;
    ns.set("apply_ramp_in_first", apply_ramp_in_first.clone())?;
    ns.set("substitute_py_comments", rt.member("docgen", "substitute_py_comments")?)?;
    py::sys_path_insert(rt, &py::path_str(&parent(&here).join("enclosure")))?;
    ns.set("_read", rt.member("_enclosure_data", "read")?)?;
    let reply = read(rt, json!({"op": "pump-case-defaults"}))?;
    let case_dict = py::from_json(reply.clone())?;
    ns.set("_case", case_dict.clone())?;
    // globals().update(_case): the dict's own values.
    for key in reply.as_object().context("the pump case stock is a mapping")?.keys() {
        ns.set(key, py::item(&case_dict, py::s(key.clone()))?)?;
    }
    let case = Case::of(&reply)?;
    let arc_segments = case.arc_segments;
    rt.keep(MODULE, State {
        case,
        json: reply,
        here,
        cq,
        world_workplane,
        xy_plane_z_up,
        xz_plane_y_up,
        frame,
        apply_ramp_out_first,
        apply_ramp_in_first,
    });

    ns.def(rt, "bore_octagon_profile", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(profile_val(&bore_octagon_profile(rt)?))
    })?;
    ns.def(rt, "_ring", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["section"], &[])?;
        let points = listed(&b.req("section")?)?;
        tuples(&read(rt, json!({"op": "pump-case-ring", "points": points}))?)
    })?;
    ns.def(rt, "offset_polygon", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["pts", "distance"], &[])?;
        let (points, distance) = (py::plain(&b.req("pts")?)?, py::plain(&b.req("distance")?)?);
        tuples(&read(rt, json!({"op": "pump-case-offset", "points": points, "distance": distance}))?)
    })?;
    ns.def(rt, "rounded_rect_profile", move |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["width", "height", "radius", "n"], &[])?;
        let mut request = serde_json::Map::new();
        request.insert("op".into(), json!("pump-case-rounded"));
        for name in ["width", "height", "radius"] {
            request.insert(name.into(), py::plain(&b.req(name)?)?);
        }
        request.insert("n".into(), py::plain(&b.opt("n").unwrap_or(Val::Int(arc_segments)))?);
        tuples(&read(rt, Value::Object(request))?)
    })?;
    ns.def(rt, "split_skirt_profile", move |rt, args, kwargs| {
        const NAMES: [&str; 9] = [
            "wide_half_extent",
            "wide_radius",
            "narrow_half_extent",
            "narrow_radius",
            "transition_y_plus",
            "transition_y_minus",
            "wide_half_extent_y",
            "narrow_half_extent_y",
            "n",
        ];
        let mut b = py::bind(args, kwargs, &NAMES, &[])?;
        let mut request = serde_json::Map::new();
        request.insert("op".into(), json!("pump-case-split"));
        for (i, name) in NAMES.into_iter().enumerate() {
            let value = match (i, name) {
                (0..4, _) => b.req(name)?,
                (_, "n") => b.opt(name).unwrap_or(Val::Int(arc_segments)),
                _ => b.opt(name).unwrap_or(Val::None),
            };
            request.insert(name.into(), py::plain(&value)?);
        }
        tuples(&read(rt, Value::Object(request))?)
    })?;
    ns.def(rt, "_skirt_profile_set", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["wall_offset"], &[])?;
        let sections = skirt_set(rt, py::plain(&b.req("wall_offset")?)?)?;
        Ok(Val::list(sections.iter().map(|s| profile_val(s)).collect()))
    })?;
    ns.def(rt, "build_base_plate_with_ramp", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        build_base_plate_with_ramp(rt)
    })?;
    ns.def(rt, "add_bore_wall", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["solid"], &[])?;
        add_bore_wall(rt, &b.req("solid")?)
    })?;
    ns.def(rt, "cut_bore_cavity", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["solid"], &[])?;
        cut_bore_cavity(rt, &b.req("solid")?)
    })?;
    ns.def(rt, "loft_profile_stack", |rt, args, kwargs| {
        let mut b =
            py::bind(args, kwargs, &["start_world_z", "z_steps", "profiles", "overcut_last_step"], &[])?;
        let start = Num::of(&b.req("start_world_z")?)?;
        let steps = py::snapshot(&b.req("z_steps")?)?.iter()?.iter().map(Num::of).collect::<Result<Vec<_>>>()?;
        let profiles = py::snapshot(&b.req("profiles")?)?.iter()?.iter().map(profile_of).collect::<Result<Vec<_>>>()?;
        let overcut_last_step = b.bool_or("overcut_last_step", false)?;
        loft_profile_stack(rt, start, &steps, &profiles, overcut_last_step)
    })?;
    ns.def(rt, "build_skirt", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        build_skirt(rt)
    })?;
    ns.def(rt, "build_tower", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        build_tower(rt)
    })?;
    ns.def(rt, "_lower_profile_set", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["wall_offset"], &[])?;
        let (top, narrow) = lower_pair(rt, b.f64("wall_offset")?)?;
        let (top, narrow) = (profile_val(&top), profile_val(&narrow));
        Ok(Val::list(vec![top.clone(), top, narrow.clone(), narrow]))
    })?;
    ns.def(rt, "lower_z_steps", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(py::flist(&lower_z_steps(&state(rt)?.case)))
    })?;
    ns.def(rt, "flank_ramp_bands", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        let [skirt, lower] = flank_ramp_bands(&state(rt)?.case);
        Ok(Val::Tuple(vec![py::ftuple(&skirt), py::ftuple(&lower)]))
    })?;
    ns.def(rt, "_profile_prism", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["profile", "z0", "z1"], &[])?;
        let profile = b.req("profile")?;
        let (z0, z1) = (Num::of(&b.req("z0")?)?, Num::of(&b.req("z1")?)?);
        let ring = tuples(&read(rt, json!({"op": "pump-case-ring", "points": listed(&profile)?}))?)?;
        let st = state(rt)?;
        profile_prism(&st, ring, z0, z1)
    })?;
    ns.def(rt, "_stepped_skirt_y_mask", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["z0", "z1", "body_y_bounds"], &[])?;
        let (z0, z1) = (Num::of(&b.req("z0")?)?, Num::of(&b.req("z1")?)?);
        let st = state(rt)?;
        stepped_skirt_y_mask(&st, z0, z1, &b.req("body_y_bounds")?)
    })?;
    ns.def(rt, "stepped_skirt_cavity", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["air", "support_z", "body_y_bounds", "skirt_y_max"], &[])?;
        let (air, support_z) = (b.f64("air")?, Num::of(&b.req("support_z")?)?);
        let bounds = b.req("body_y_bounds")?;
        stepped_skirt_cavity(rt, air, support_z, &bounds, Num::of(&b.req("skirt_y_max")?)?)
    })?;
    ns.def(rt, "stepped_skirt_drop_well", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["air", "support_z", "body_y_bounds", "skirt_y_max"], &[])?;
        let (air, support_z) = (b.f64("air")?, Num::of(&b.req("support_z")?)?);
        let bounds = b.req("body_y_bounds")?;
        stepped_skirt_drop_well(rt, air, support_z, &bounds, Num::of(&b.req("skirt_y_max")?)?)
    })?;
    ns.def(rt, "cavity", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["air"], &[])?;
        cavity(rt, b.f64_or("air", 0.0)?)
    })?;
    ns.def(rt, "drop_well", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["air"], &[])?;
        drop_well(rt, b.f64_or("air", 0.0)?)
    })?;
    ns.def(rt, "_stack_levels", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(py::flist(&stack_levels(&state(rt)?.case)))
    })?;
    ns.def(rt, "_stack_profiles", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["offset"], &[])?;
        let offset = b.req("offset")?;
        let mut out: Vec<Val> = skirt_set(rt, py::plain(&offset)?)?.iter().map(|s| profile_val(s)).collect();
        let (top, narrow) = lower_pair(rt, offset.num()?)?;
        let narrow = profile_val(&narrow);
        out.extend([profile_val(&top), narrow.clone(), narrow]);
        Ok(Val::list(out))
    })?;
    ns.def(rt, "build_lower_extension", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        build_lower_extension(rt)
    })?;
    ns.def(rt, "cut_arch_notches", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["combined"], &[])?;
        cut_arch_notches(rt, b.req("combined")?)
    })?;
    ns.def(rt, "split_into_base_and_cap", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["combined"], &[])?;
        let (base, cap) = split_into_base_and_cap(rt, &b.req("combined")?)?;
        Ok(Val::Tuple(vec![base, cap]))
    })?;
    ns.def(rt, "add_snap_fits", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["base", "cap"], &[])?;
        let (base, cap) = add_snap_fits(rt, b.req("base")?, b.req("cap")?)?;
        Ok(Val::Tuple(vec![base, cap]))
    })?;
    ns.def(rt, "build_pump_case", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        let (base, cap) = build_pump_case(rt)?;
        Ok(Val::Tuple(vec![base, cap]))
    })?;
    ns.def(rt, "main", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        main(rt)?;
        Ok(Val::None)
    })?;
    Ok(())
}

pub fn main_block(rt: &Rt) -> Result<()> {
    let ns = rt.namespace(MODULE)?;
    let rust_part = rt.import("_rust_part")?;
    ns.set("_rust_part", rust_part.clone())?;
    py::method(&rust_part, "start", vec![])?;
    main(rt)
}

/// Pump bore octagon with ledge indentations, centered at origin.
pub fn bore_octagon_profile(rt: &Rt) -> Result<Profile> {
    let st = state(rt)?;
    profile(&read(rt, json!({"op": "pump-case-bore", "case": st.json}))?)
}

/// A section's points with an explicit closing vertex.
pub fn ring(rt: &Rt, section: &[[f64; 2]]) -> Result<Profile> {
    profile(&read(rt, json!({"op": "pump-case-ring", "points": section}))?)
}
/// `_ring(section)` as the Python value a CadQuery call takes.
fn ring_val(rt: &Rt, section: &[[f64; 2]]) -> Result<Val> {
    tuples(&read(rt, json!({"op": "pump-case-ring", "points": section}))?)
}

/// Offset each edge of a closed polygon outward by distance.
pub fn offset_polygon(rt: &Rt, pts: &[[f64; 2]], distance: f64) -> Result<Profile> {
    profile(&read(rt, json!({"op": "pump-case-offset", "points": pts, "distance": distance}))?)
}

/// Polygon points for a rounded rectangle centered at origin.
pub fn rounded_rect_profile(rt: &Rt, width: f64, height: f64, radius: f64, n: i64) -> Result<Profile> {
    let request = json!({"op": "pump-case-rounded", "width": width, "height": height, "radius": radius, "n": n});
    profile(&read(rt, request)?)
}

/// `split_skirt_profile`'s arguments; `None` leaves one to the recipe, as the Python default does.
#[derive(Clone, Debug)]
pub struct Split {
    pub wide_half_extent: f64,
    pub wide_radius: f64,
    pub narrow_half_extent: f64,
    pub narrow_radius: f64,
    pub transition_y_plus: Option<f64>,
    pub transition_y_minus: Option<f64>,
    pub wide_half_extent_y: Option<f64>,
    pub narrow_half_extent_y: Option<f64>,
    pub n: i64,
}

/// Asymmetric wide/narrow outline with its exact transition vertices.
pub fn split_skirt_profile(rt: &Rt, s: &Split) -> Result<Profile> {
    let request = json!({
        "op": "pump-case-split",
        "wide_half_extent": s.wide_half_extent,
        "wide_radius": s.wide_radius,
        "narrow_half_extent": s.narrow_half_extent,
        "narrow_radius": s.narrow_radius,
        "transition_y_plus": s.transition_y_plus,
        "transition_y_minus": s.transition_y_minus,
        "wide_half_extent_y": s.wide_half_extent_y,
        "narrow_half_extent_y": s.narrow_half_extent_y,
        "n": s.n,
    });
    profile(&read(rt, request)?)
}

fn skirt_set(rt: &Rt, wall_offset: Value) -> Result<Vec<Profile>> {
    let st = state(rt)?;
    profiles(&read(rt, json!({"op": "pump-case-skirt-set", "case": st.json, "wall_offset": wall_offset}))?)
}
/// Five skirt cross-section profiles, top-of-skirt to bottom-of-skirt.
pub fn skirt_profile_set(rt: &Rt, wall_offset: f64) -> Result<Vec<Profile>> {
    skirt_set(rt, json!(wall_offset))
}

/// Base plate (z=0..[+3 mm](BASE_PLATE_FAR_Z)) plus the 45° ramp (z=[+3 mm](BASE_PLATE_FAR_Z)..[+21 mm](BORE_BOTTOM_Z)) shrinking from
/// the [70](FOOTPRINT_X)x[70](FOOTPRINT_X) footprint to a [34](RAMP_BOTTOM_WIDTH)x[34](RAMP_BOTTOM_WIDTH) footprint that meets the octagon bore wall.
pub fn build_base_plate_with_ramp(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let c = &st.case;
    let footprint = rounded_rect_profile(rt, c.footprint_x, c.footprint_y, c.corner_r, c.arc_segments)?;
    let footprint_at_ramp_bottom = rounded_rect_profile(
        rt,
        c.footprint_x - 2. * c.ramp_from_skirt_to_octagon_height,
        c.footprint_y - 2. * c.ramp_from_skirt_to_octagon_height,
        c.corner_r,
        c.arc_segments,
    )?;
    let wp = outline(&centred(&st, Val::Int(0))?, ring_val(rt, &footprint)?)?;
    let wp = py::call_kw(&wp.attr("workplane")?, vec![], vec![("offset", Val::Float(c.base_thickness))])?;
    let wp = outline(&wp, ring_val(rt, &footprint)?)?;
    let wp = py::call_kw(
        &wp.attr("workplane")?,
        vec![],
        vec![("offset", Val::Float(c.ramp_from_skirt_to_octagon_height))],
    )?;
    let wp = outline(&wp, ring_val(rt, &footprint_at_ramp_bottom)?)?;
    py::call_kw(&wp.attr("loft")?, vec![], vec![("ruled", Val::Bool(true))])
}

/// Octagonal bore wall around the pump-flange seat, unioned onto solid.
pub fn add_bore_wall(rt: &Rt, solid: &Val) -> Result<Val> {
    let st = state(rt)?;
    let c = &st.case;
    let wall = outline(&centred(&st, Val::Int(0))?, ring_val(rt, &c.bore_wall_profile)?)?;
    let bore_wall = py::method(&wall, "extrude", vec![Val::Float(c.bore_depth)])?;
    py::method(solid, "union", vec![bore_wall])
}

/// Octagonal pump-flange seat (with ledges) cut through the bore wall
/// and the tower cylinder material overlapping the bore-wall region.
pub fn cut_bore_cavity(rt: &Rt, solid: &Val) -> Result<Val> {
    let st = state(rt)?;
    let c = &st.case;
    let seat = outline(&centred(&st, Val::Int(0))?, ring_val(rt, &c.bore_profile)?)?;
    let bore_cavity = py::method(&seat, "extrude", vec![Val::Float(c.bore_depth + c.overcut)])?;
    py::method(solid, "cut", vec![bore_cavity])
}

/// One stack level's points: world coordinates and the `cq.Vector` made on them.
type Level = Vec<([f64; 3], Val)>;

/// Loft a stack of skirt profiles at successive world-Z levels.
///
/// start_world_z: world Z of the first profile.
/// z_steps: signed world-Z deltas between consecutive profiles.
/// overcut_last_step: extend the last delta by overcut in the same
///     direction as the loft's travel, so a cut profile pierces cleanly
///     through a sibling solid boundary.
///
/// The symmetric outline has one transition vertex on each side; the asymmetric outline has
/// the two ends of its diagonal. That is a real topology change: one vertex opens into one edge.
/// OpenCascade's generic through-sections loft cannot make the ruled solid from unequal wires,
/// so state that correspondence directly. Every ordinary edge makes one ruled face; at each
/// transition the collapsed vertex and the next outline's edge make one triangle. Top, bottom
/// and those side faces are one shell — no epsilon edge and no Boolean seam between half-solids.
pub fn loft_profile_stack(
    rt: &Rt,
    start_world_z: Num,
    z_steps: &[Num],
    profiles: &[Profile],
    overcut_last_step: bool,
) -> Result<Val> {
    let st = state(rt)?;
    let c = &st.case;
    if profiles.len() != z_steps.len() + 1 {
        bail!("a profile stack needs one more outline than Z steps");
    }
    let vector = st.cq.attr("Vector")?;
    let level = |profile: &Profile, z: Num| -> Result<Level> {
        profile
            .iter()
            .map(|&[x, y]| {
                let (wx, wy) = (c.center_x + x, c.center_y + y);
                Ok(([wx, wy, z.f()], py::call(&vector, vec![Val::Float(wx), Val::Float(wy), z.val()])?))
            })
            .collect()
    };
    let mut levels = vec![];
    let mut z = start_world_z;
    levels.push(level(&profiles[0], z)?);
    for (i, (step, profile)) in z_steps.iter().zip(&profiles[1..]).enumerate() {
        let is_last = i == z_steps.len() - 1;
        let extra = if overcut_last_step && is_last { Num::F(c.overcut.copysign(step.f())) } else { Num::I(0) };
        z = z.add(step.add(extra));
        levels.push(level(profile, z)?);
    }

    let make_polygon = st.cq.attr("Wire")?.attr("makePolygon")?;
    let from_wires = st.cq.attr("Face")?.attr("makeFromWires")?;
    let closed_wire = |points: Val| py::call_kw(&make_polygon, vec![points], vec![("close", Val::Bool(true))]);
    let points = |level: &Level| Val::list(level.iter().map(|(_, v)| v.clone()).collect());

    let mut faces = vec![
        py::call(&from_wires, vec![closed_wire(points(&levels[0]))?])?,
        py::call(&from_wires, vec![closed_wire(points(&levels[levels.len() - 1]))?])?,
    ];
    let collapsed_count = 4 * (c.arc_segments + 1) + 2;
    let split_count = collapsed_count + 2;
    let collapse_i = 2 * (c.arc_segments + 1);

    let aligned = |points: &Level| -> Result<Level> {
        let n = points.len() as i64;
        if n == split_count {
            return Ok(points.clone());
        }
        if n != collapsed_count {
            bail!(
                "a skirt outline has {} vertices, expected {} collapsed or {} split",
                num::fmti(n, ""),
                num::fmti(collapsed_count, ""),
                num::fmti(split_count, "")
            );
        }
        // Repeat each collapsed point only in this correspondence list. No edge is made from
        // either repetition: `_side_face` below turns its mate into the one triangular face.
        let at = collapse_i as usize;
        let mut out = points[..at + 1].to_vec();
        out.push(points[at].clone());
        out.extend_from_slice(&points[at + 1..]);
        out.push(points[points.len() - 1].clone());
        Ok(out)
    };

    let make_ruled_surface = st.cq.attr("Face")?.attr("makeRuledSurface")?;
    let make_line = st.cq.attr("Edge")?.attr("makeLine")?;
    // `(b - a).Length`, on the coordinates the two vectors were made on.
    let length = |a: &[f64; 3], b: &[f64; 3]| {
        let (dx, dy, dz) = (b[0] - a[0], b[1] - a[1], b[2] - a[2]);
        (dx * dx + dy * dy + dz * dz).sqrt()
    };
    let side_face = |a0: &([f64; 3], Val), a1: &([f64; 3], Val), b0: &([f64; 3], Val), b1: &([f64; 3], Val)| {
        if length(&a0.0, &a1.0) < 1e-10 {
            return py::call(&from_wires, vec![closed_wire(Val::Tuple(vec![a0.1.clone(), b0.1.clone(), b1.1.clone()]))?]);
        }
        if length(&b0.0, &b1.0) < 1e-10 {
            return py::call(&from_wires, vec![closed_wire(Val::Tuple(vec![a0.1.clone(), a1.1.clone(), b0.1.clone()]))?]);
        }
        py::call(
            &make_ruled_surface,
            vec![
                py::call(&make_line, vec![a0.1.clone(), a1.1.clone()])?,
                py::call(&make_line, vec![b0.1.clone(), b1.1.clone()])?,
            ],
        )
    };

    for pair in levels.windows(2) {
        let (a, b) = (aligned(&pair[0])?, aligned(&pair[1])?);
        let count = split_count as usize;
        for i in 0..count {
            let j = (i + 1) % count;
            faces.push(side_face(&a[i], &a[j], &b[i], &b[j])?);
        }
    }

    let shell = py::call(&st.cq.attr("Shell")?.attr("makeShell")?, vec![Val::list(faces)])?;
    let solid = py::method(&py::call(&st.cq.attr("Solid")?.attr("makeSolid")?, vec![shell])?, "fix", vec![])?;
    if !py::method(&solid, "isValid", vec![])?.truthy()? || py::method(&solid, "Solids", vec![])?.len()? != 1 {
        bail!("the exact skirt loft did not make one valid solid");
    }
    // Keep the project wrapper at the API boundary so later unions/cuts unwrap their operands
    // before CadQuery's strict Workplane type check.
    let workplane = py::call_kw(&st.cq.attr("Workplane")?, vec![], vec![("obj", solid)])?;
    py::call(&st.world_workplane, vec![workplane])
}

/// Asymmetric flared skirt: wide on +Y, narrow on -Y.
pub fn build_skirt(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let c = &st.case;
    let steps = nums(&c.skirt_z_steps);
    let skirt_outer = loft_profile_stack(rt, Num::I(0), &steps, &c.skirt_outer_profiles, false)?;
    let skirt_cavity = loft_profile_stack(rt, Num::I(0), &steps, &c.skirt_inner_profiles, true)?;
    py::method(&skirt_outer, "cut", vec![skirt_cavity])
}

/// Cylindrical tower extending downward from cylinder_top_z. Its outer
/// radius circumscribes the octagonal bore wall, overlapping it on the
/// outside from above the bore wall's far face.
pub fn build_tower(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let c = &st.case;
    let circle = py::method(&centred(&st, Val::Float(c.cylinder_top_z))?, "circle", vec![Val::Float(c.cylinder_r_outer)])?;
    let tower_cylinder = py::method(&circle, "extrude", vec![Val::Float(c.cylinder_bottom_z - c.cylinder_top_z)])?;

    let tower_bore_depth = c.tower_height - c.tower_cap_thickness;
    let bore_top = centred(&st, Val::Float(c.bore_bottom_z - c.overcut))?;
    let circle = py::method(&bore_top, "circle", vec![Val::Float(c.cylinder_r_inner)])?;
    let tower_bore = py::method(&circle, "extrude", vec![Val::Float(tower_bore_depth + c.overcut)])?;
    py::method(&tower_cylinder, "cut", vec![tower_bore])
}

/// `_lower_profile_set(wall_offset)` as its two outlines: the skirt's last (the first two
/// levels) and the narrow symmetric one (the last two).
fn lower_pair(rt: &Rt, wall_offset: f64) -> Result<(Profile, Profile)> {
    let st = state(rt)?;
    let c = &st.case;
    let seam_y_shift = wall_offset * (2f64.sqrt() - 1.);
    let narrow_he = c.skirt_narrow_half_extent - wall_offset;
    let base_he = c.skirt_base_half_extent - wall_offset;
    let radius = c.corner_r - wall_offset;
    let ty_end_minus = c.skirt_transition_y_end[1] + seam_y_shift;
    let narrow_symmetric = split_skirt_profile(rt, &Split {
        wide_half_extent: narrow_he,
        wide_radius: radius,
        narrow_half_extent: narrow_he,
        narrow_radius: radius,
        transition_y_plus: Some(ty_end_minus),
        transition_y_minus: Some(ty_end_minus),
        wide_half_extent_y: Some(base_he),
        narrow_half_extent_y: Some(base_he),
        n: c.arc_segments,
    })?;
    let mut set = skirt_profile_set(rt, wall_offset)?;
    let top = set.pop().context("list index out of range")?;
    Ok((top, narrow_symmetric))
}
/// Four lower-extension cross-section profiles, top to bottom of lower section.
pub fn lower_profile_set(rt: &Rt, wall_offset: f64) -> Result<Vec<Profile>> {
    let (top, narrow_symmetric) = lower_pair(rt, wall_offset)?;
    Ok(vec![top.clone(), top, narrow_symmetric.clone(), narrow_symmetric])
}

/// Signed world-Z deltas between the lower extension's four cross-section levels:
/// straight off the skirt, the wide half's ramp, then uniform to the cap.
pub fn lower_z_steps(c: &Case) -> [f64; 3] {
    let uniform = c.lower_height - c.lower_ramp_height - c.lower_footprint_straight;
    // Lower extension extends in -Z, away from the base plate.
    [-c.lower_footprint_straight, -c.lower_ramp_height, -uniform]
}

/// THE TWO BANDS THE CAVITY CLOSES IN ON A HEAD OVER, each (top_z, bottom_z).
///
/// The skirt tapers its NARROW half (-Y) over the first and the lower extension ramps its
/// WIDE half (+Y) over the second, both at 45 degrees.  Everywhere else the room round a head
/// is plumb, so these two bands are the only levels where the case can bear DOWN on the part
/// — and what stands in them is the surface a case carries a pump on.
pub fn flank_ramp_bands(c: &Case) -> [[f64; 2]; 2] {
    let aft_top = c.skirt_bottom_z - c.lower_footprint_straight;
    [
        [num::sum(c.skirt_z_steps[..1].iter().copied()), num::sum(c.skirt_z_steps[..3].iter().copied())],
        [aft_top, aft_top - c.lower_ramp_height],
    ]
}

/// `WorldWorkplane(plane).workplane(offset=offset).center(x, y)`.
fn world(st: &State, plane: &Val, offset: Val, x: f64, y: f64) -> Result<Val> {
    let wp = py::call(&st.world_workplane, vec![plane.clone()])?;
    let wp = py::call_kw(&wp.attr("workplane")?, vec![], vec![("offset", offset)])?;
    py::method(&wp, "center", vec![Val::Float(x), Val::Float(y)])
}
/// `WorldWorkplane(xy_plane_z_up).workplane(offset=offset).center(center_x, center_y)`.
fn centred(st: &State, offset: Val) -> Result<Val> {
    world(st, &st.xy_plane_z_up, offset, st.case.center_x, st.case.center_y)
}
/// `.polyline(points).wire()`.
fn outline(wp: &Val, points: Val) -> Result<Val> {
    py::method(&py::method(wp, "polyline", vec![points])?, "wire", vec![])
}

/// One stated case profile carried vertically between two exact Z planes.
fn profile_prism(st: &State, ring: Val, z0: Num, z1: Num) -> Result<Val> {
    let wp = outline(&centred(st, z0.val())?, ring)?;
    py::method(&wp, "extrude", vec![z1.sub(z0).val()])
}

/// The one rectangular Y interval occupied by the body below the skirt.
fn stepped_skirt_y_mask(st: &State, z0: Num, z1: Num, body_y_bounds: &Val) -> Result<Val> {
    let c = &st.case;
    let bounds = py::unpack(body_y_bounds, 2)?;
    let (y_min, y_max) = (Num::of(&bounds[0])?, Num::of(&bounds[1])?);
    if !(y_min.f() < y_max.f()) {
        bail!("bad skirt-body Y interval {}", num::fmtv(body_y_bounds, "")?);
    }
    let x0 = c.center_x - c.cutter_half_extent;
    let wp = py::call(&st.cq.attr("Workplane")?, vec![py::s("XY")])?;
    let size = vec![Val::Float(2.0 * c.cutter_half_extent), y_max.sub(y_min).val(), z1.sub(z0).val()];
    let block = py::call_kw(&wp.attr("box")?, size, vec![("centered", Val::Bool(false))])?;
    let at = Val::Tuple(vec![Val::Float(x0), Num::F(c.center_y).add(y_min).val(), z0.val()]);
    py::method(&block, "translate", vec![at])
}

/// The head room with the skirt transition made as one flat three-sided step.
///
/// Above ``support_z`` the room keeps the skirt's symmetric upper outline. Below it the room
/// immediately takes the narrower body outline and retains that outline to the lower extension.
/// Their difference is one continuous land on the X-, X+ and Y- flanks at ``support_z``:
/// 4 mm on X and 5 mm on Y-. Closing the measured ``body_y_bounds`` adds the 3.482 mm Y+ land;
/// the cartridge's separate tube passages later leave only its centre bridge.
pub fn stepped_skirt_cavity(rt: &Rt, air: f64, support_z: Num, body_y_bounds: &Val, skirt_y_max: Num) -> Result<Val> {
    let st = state(rt)?;
    let c = &st.case;
    if !(c.skirt_bottom_z < support_z.f() && support_z.f() < 0.0) {
        bail!(
            "a skirt support at {} must lie between {} and 0 mm",
            support_z.fmt("g"),
            num::fmt(c.skirt_bottom_z, "g")
        );
    }
    let offset = c.skirt_wall - air;
    let upper = nth(skirt_profile_set(rt, offset)?, 1)?;
    let lower = nth(skirt_profile_set(rt, offset)?, 3)?;
    let room = py::method(&cavity(rt, air)?, "val", vec![])?;
    let bottom = Num::F(c.lower_cap_top_z - c.overcut);
    let lower_mask = py::method(&profile_prism(&st, ring_val(rt, &lower)?, bottom, support_z)?, "val", vec![])?;
    let y_mask = py::method(&stepped_skirt_y_mask(&st, bottom, support_z, body_y_bounds)?, "val", vec![])?;
    let lower_room = py::method(&py::method(&room, "intersect", vec![lower_mask])?, "intersect", vec![y_mask])?;
    let upper_prism = py::method(&profile_prism(&st, ring_val(rt, &upper)?, support_z, Num::F(0.0))?, "val", vec![])?;
    let upper_bounds = Val::Tuple(vec![Val::Float(-c.cutter_half_extent), skirt_y_max.val()]);
    let upper_mask = py::method(&stepped_skirt_y_mask(&st, support_z, Num::F(0.0), &upper_bounds)?, "val", vec![])?;
    let upper_room = py::method(&upper_prism, "intersect", vec![upper_mask])?;
    let room = py::method(&upper_room, "fuse", vec![lower_room])?;
    py::call_kw(&st.cq.attr("Workplane")?, vec![], vec![("obj", room)])
}

/// ``stepped_skirt_cavity`` swept toward the bracket plane for Z insertion.
pub fn stepped_skirt_drop_well(
    rt: &Rt,
    air: f64,
    support_z: Num,
    body_y_bounds: &Val,
    skirt_y_max: Num,
) -> Result<Val> {
    let st = state(rt)?;
    let c = &st.case;
    let offset = c.skirt_wall - air;
    let upper = nth(skirt_profile_set(rt, offset)?, 1)?;
    let lower = nth(skirt_profile_set(rt, offset)?, 3)?;
    let swept = py::method(&drop_well(rt, air)?, "val", vec![])?;
    let bottom = Num::F(c.lower_cap_top_z - c.overcut);
    let lower_mask = py::method(&profile_prism(&st, ring_val(rt, &lower)?, bottom, support_z)?, "val", vec![])?;
    let y_mask = py::method(&stepped_skirt_y_mask(&st, bottom, support_z, body_y_bounds)?, "val", vec![])?;
    let lower_room = py::method(&py::method(&swept, "intersect", vec![lower_mask])?, "intersect", vec![y_mask])?;
    // The completed split outline is wider on +Y than the upper outline. Carry that side
    // upward as the physical lower skirt does during insertion; on -Y it is contained and the
    // flat support land remains intact.
    let upper_prism = profile_prism(&st, ring_val(rt, &upper)?, support_z, Num::F(0.0))?;
    let lower_prism = profile_prism(&st, ring_val(rt, &lower)?, support_z, Num::F(0.0))?;
    let carried = py::method(&py::method(&upper_prism, "union", vec![lower_prism])?, "val", vec![])?;
    let upper_bounds = Val::Tuple(vec![Val::Float(-c.cutter_half_extent), skirt_y_max.val()]);
    let upper_mask = py::method(&stepped_skirt_y_mask(&st, support_z, Num::F(0.0), &upper_bounds)?, "val", vec![])?;
    let upper_room = py::method(&carried, "intersect", vec![upper_mask])?;
    let room = py::method(&upper_room, "fuse", vec![lower_room])?;
    py::call_kw(&st.cq.attr("Workplane")?, vec![], vec![("obj", room)])
}

/// THE ROOM THE CASE LEAVES A HEAD — the skirt's interior and the lower extension's, as
/// one solid in the case's own world frame, opened `air` on every face.
///
/// It is not a prism.  `flank_ramp_bands` is where it closes in, and a head shaped to it
/// (`kamoer_kphm400.build_head`) carries a 45 degree face on each side at each band, looking
/// down and outboard. The complete two-piece bench case closes on those fitted faces.
///
/// AND IT IS NOT SQUARE IN PLAN EITHER. The skirt is split in Y and its two halves are
/// different widths: `skirt_narrow_half_extent` on -Y and `skirt_wide_half_extent` on +Y,
/// which is the OUTLET side.  The flare is a HALF-EXTENT and not a Y offset, so the wide half
/// stands further out ACROSS as well — 70.0 mm of room at the outlet face, 64.0 at the centre,
/// 56.0 at the narrow end.  The complete pump stands widest at that same outlet face, across
/// its two tube fittings (`kamoer_kphm400.outlet_span_x`).
///
/// `air` grows every face by walking the profile stack out, so the running fit is struck the
/// way the case's own wall is and every radius opens with it.
pub fn cavity(rt: &Rt, air: f64) -> Result<Val> {
    let st = state(rt)?;
    let c = &st.case;
    let offset = c.skirt_wall - air;
    let skirt = loft_profile_stack(rt, Num::I(0), &nums(&c.skirt_z_steps), &skirt_profile_set(rt, offset)?, false)?;
    let steps = nums(&lower_z_steps(c));
    let lower = loft_profile_stack(rt, Num::F(c.skirt_bottom_z), &steps, &lower_profile_set(rt, offset)?, false)?;
    py::method(&skirt, "union", vec![lower])
}

/// THE ROOM A PUMP NEEDS TO BE LOWERED THROUGH, not just to stand in — `cavity` swept
/// along its own axis toward the crown, in the case's world frame.
///
/// Every station stands at least as open as the widest one under it: 70.0 mm from the flared
/// outlet band up through the crown, and `cavity`'s own figure below that band.
///
/// THE SWEEP IS EACH STATED OUTLINE CARRIED UP TO THE CROWN. `_stack_levels` is every Z the
/// cavity states a section on and `_stack_profiles` the outline standing there. Between them
/// each half changes monotonically and their exact collapse/transition vertices stay on one
/// fixed 45-degree seam plane. The ruled cavity carries that change through its own band; once
/// a half reaches its extremal stated outline, that outline's crown prism carries it through
/// the rest of the insertion path. No sampled staircase stands in the fitting openings.
///
/// `cavity`'s fitted faces stand under their own bands and this leaves them there.
pub fn drop_well(rt: &Rt, air: f64) -> Result<Val> {
    let st = state(rt)?;
    let c = &st.case;
    let mut solid = cavity(rt, air)?;
    let levels = stack_levels(c);
    let profiles = stack_profiles(rt, c.skirt_wall - air)?;
    for (&z, profile) in levels.iter().zip(&profiles) {
        if z >= -1e-9 {
            continue;
        }
        // Struck the way `loft_profile_stack` strikes the same outlines: a profile is stated
        // about the origin and stands on the footprint's own centre.
        let prism = py::method(&outline(&centred(&st, Val::Float(z))?, ring_val(rt, profile)?)?, "extrude", vec![Val::Float(-z)])?;
        solid = py::method(&solid, "union", vec![prism])?;
    }
    Ok(solid)
}

/// Every Z the cavity states a cross-section on, crown first — the skirt's five and the
/// lower extension's four, which share the plane between them.
pub fn stack_levels(c: &Case) -> Vec<f64> {
    let (mut out, mut z) = (vec![0.0], 0.0);
    for dz in c.skirt_z_steps {
        z += dz;
        out.push(z);
    }
    for dz in lower_z_steps(c) {
        z += dz;
        out.push(z);
    }
    out
}

/// The outlines that stand on `_stack_levels`, in the same order. The lower extension's
/// first profile IS the skirt's last, so it is not repeated.
pub fn stack_profiles(rt: &Rt, offset: f64) -> Result<Vec<Profile>> {
    let mut out = skirt_profile_set(rt, offset)?;
    out.extend(lower_profile_set(rt, offset)?.into_iter().skip(1));
    Ok(out)
}

/// Lower portion extending from skirt bottom: taper to uniform, then cap.
pub fn build_lower_extension(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let c = &st.case;
    let lower_outer_profiles = lower_profile_set(rt, 0.0)?;
    let lower_inner_profiles = lower_profile_set(rt, c.skirt_wall)?;

    let steps = nums(&lower_z_steps(c));
    let lower_outer = loft_profile_stack(rt, Num::F(c.skirt_bottom_z), &steps, &lower_outer_profiles, false)?;
    let lower_inner = loft_profile_stack(rt, Num::F(c.skirt_bottom_z), &steps, &lower_inner_profiles, true)?;
    let lower_shell = py::method(&lower_outer, "cut", vec![lower_inner])?;

    let cap_outline = ring_val(rt, &lower_outer_profiles[lower_outer_profiles.len() - 1])?;
    let cap = outline(&centred(&st, Val::Float(c.lower_cap_top_z))?, cap_outline)?;
    let lower_cap = py::method(&cap, "extrude", vec![Val::Float(-c.lower_cap_thickness)])?;
    py::method(&lower_shell, "union", vec![lower_cap])
}

/// Semicircular notches on the +Y face for wire routing.
pub fn cut_arch_notches(rt: &Rt, combined: Val) -> Result<Val> {
    let st = state(rt)?;
    let c = &st.case;
    let arch_cut_depth = c.skirt_wall + c.wall_thickness;
    let mut combined = combined;
    for ax in c.arch_hole_xs {
        let wp = world(&st, &st.xz_plane_y_up, Val::Float(c.pos_y_face_y + c.overcut), ax, c.skirt_bottom_z)?;
        let circle = py::method(&wp, "circle", vec![Val::Float(c.arch_radius)])?;
        let arch_cutter = py::method(&circle, "extrude", vec![Val::Float(-(arch_cut_depth + c.overcut))])?;
        combined = py::method(&combined, "cut", vec![arch_cutter])?;
    }
    Ok(combined)
}

/// Stepped split creating base (with tower) and cap (with lower extension).
///
/// The two parts meet at two different Z levels:
///   Wide half (+Y):   at skirt_bottom_z
///   Narrow half (-Y): step_height higher into the skirt
/// The boundary follows the seam diagonal.
pub fn split_into_base_and_cap(rt: &Rt, combined: &Val) -> Result<(Val, Val)> {
    let st = state(rt)?;
    let c = &st.case;
    let lower_end_z = c.lower_cap_bottom_z - c.overcut;
    let che = c.cutter_half_extent;

    let slab = py::method(&centred(&st, Val::Float(c.skirt_bottom_z))?, "rect", vec![Val::Float(2. * che), Val::Float(2. * che)])?;
    let full_slab = py::method(&slab, "extrude", vec![Val::Float(lower_end_z - c.skirt_bottom_z)])?;

    let step_y = c.skirt_transition_y_end_plus + c.step_y_clearance;
    let narrow_box = [[-che, -che], [che, -che], [che, step_y + c.overcut], [-che, step_y + c.overcut]];
    let step = outline(&centred(&st, Val::Float(c.narrow_split_z))?, ring_val(rt, &narrow_box)?)?;
    let narrow_step = py::method(&step, "extrude", vec![Val::Float(c.skirt_bottom_z - c.narrow_split_z)])?;

    let step_cutter = py::method(&full_slab, "union", vec![narrow_step])?;

    let base = py::method(combined, "cut", vec![step_cutter.clone()])?;
    let cap = py::method(combined, "intersect", vec![step_cutter])?;
    Ok((base, cap))
}

/// Snap-fit ramps on four interior walls where base meets cap.
///
/// The base wall grows a ramp_out_first zigzag; the cap wall grows the
/// complementary ramp_in_first zigzag. The two interleave across the split,
/// their tips reaching past the mating plane to wrap around each other and
/// lock the halves together — the solids slide past without interpenetrating.
///
/// Each snap grows along Z from its split plane. The +Y wide-split snap sits
/// on the flared face; the -Y, +X, -X snaps sit on the narrow-split faces.
pub fn add_snap_fits(rt: &Rt, base: Val, cap: Val) -> Result<(Val, Val)> {
    let st = state(rt)?;
    let c = &st.case;
    let snap_plus_y_inner = c.pos_y_face_y - c.wall_thickness;
    let snap_minus_y_inner = c.center_y - c.footprint_half_extent + c.wall_thickness;
    let snap_plus_x_inner = c.center_x + c.footprint_half_extent - c.wall_thickness;
    let snap_minus_x_inner = c.center_x - c.footprint_half_extent + c.wall_thickness;

    // ±Y snaps extrude along X (plane YZ, +X normal); zone spans X about center.
    let yz_zone_range = py::ftuple(&[c.center_x - c.snap_zone_width / 2., c.center_x + c.snap_zone_width / 2.]);
    // ±X snaps extrude along Y (plane ZX, +Y normal); zone spans Y from just
    // inside the narrow-face corner.
    let zx_zone_start = c.center_y - c.skirt_narrow_half_extent + c.corner_r + 0.5;
    let zx_zone_range = py::ftuple(&[zx_zone_start, zx_zone_start + c.snap_zone_width]);

    let snap_faces = [
        (snap_plus_y_inner, 1, c.skirt_bottom_z, "YZ", &yz_zone_range),
        (snap_minus_y_inner, -1, c.narrow_split_z, "YZ", &yz_zone_range),
        (snap_plus_x_inner, 1, c.narrow_split_z, "ZX", &zx_zone_range),
        (snap_minus_x_inner, -1, c.narrow_split_z, "ZX", &zx_zone_range),
    ];

    let (mut base, mut cap) = (base, cap);
    for (inner_face, sign, split_z, plane, zone_range) in snap_faces {
        let frame = |up_sign: i64| {
            py::call_kw(&st.frame, vec![], vec![
                ("extrusion_plane", py::s(plane)),
                ("outward_sign", Val::Int(sign)),
                ("up_axis", py::s("Z")),
                ("up_sign", Val::Int(up_sign)),
            ])
        };
        let base_frame = frame(-1)?;
        let cap_frame = frame(1)?;
        let ramp = |apply: &Val, solid: Val, frame: Val| {
            py::call_kw(apply, vec![solid], vec![
                ("frame", frame),
                ("inner_wall_at", Val::Float(inner_face)),
                ("wall_top_at", Val::Float(split_z)),
                ("wall_height", Val::Float(c.snap_wall_height)),
                ("zone_range", zone_range.clone()),
                ("deflection_distance", Val::Float(c.snap_deflection)),
            ])
        };
        base = ramp(&st.apply_ramp_out_first, base, base_frame)?;
        cap = ramp(&st.apply_ramp_in_first, cap, cap_frame)?;
    }
    Ok((base, cap))
}

// Assembly

pub fn build_pump_case(rt: &Rt) -> Result<(Val, Val)> {
    let solid = build_base_plate_with_ramp(rt)?;
    let solid = py::method(&solid, "union", vec![build_skirt(rt)?])?;
    let solid = add_bore_wall(rt, &solid)?;
    let solid = py::method(&solid, "union", vec![build_tower(rt)?])?;
    let solid = cut_bore_cavity(rt, &solid)?;
    let combined = py::method(&solid, "union", vec![build_lower_extension(rt)?])?;
    let combined = cut_arch_notches(rt, combined)?;
    let (base, cap) = split_into_base_and_cap(rt, &combined)?;
    add_snap_fits(rt, base, cap)
}

fn main(rt: &Rt) -> Result<()> {
    let st = state(rt)?;
    let variables = read(rt, json!({"op": "pump-case-variables", "case": st.json}))?;
    let mut values = BTreeMap::new();
    for (key, value) in variables.as_object().context("substitute variables")? {
        values.insert(key.clone(), py::from_json(value.clone())?.str()?);
    }
    rt.substitute(hsm_documents::Kind::Python, &st.here.join("pump_case.py"), &values, Some(MODULE))?;
    rt.print("-> updated comments in pump_case.py".into())
}
