//! Live numeric construction of the relaxed and installed lower pump retainer.
//!
//! Typed API: [`numbers`] and [`cut`] record the retainer on a native [`Graph`]. [`Leaves`] is
//! `_leaves(shell, graph)`: while it is entered, `shell._pump_lower_well` builds [`lower_well`],
//! `shell._fixed_pump_mount._wing` builds [`wing`] and `shell._ycyl` records the outlet cylinders
//! (over `_record`'s own `_ycyl`); the enclosure and `_fixed_pump_mount` read those three through
//! their namespaces at each call. [`stack`], [`profile_prism`], [`case_drop_well`],
//! [`lower_well`] and [`wing`] record their nodes on any [`AnyGraph`].
use super::_enclosure_panel::{self as panel, AnyGraph, Graph, Leaf, Recording, Solid};
use super::num::Num;
use super::py::{self, Val};
use super::rt::{self, Ns, Rt};
use anyhow::{Context, Result, bail};
use hsm_documents::interop;
use std::cell::RefCell;
use std::path::PathBuf;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_enclosure_pump_retainer";

fn n(value: &Val) -> Result<Num> {
    Num::of(value)
}

/// `min(values)`: the first of equal values.
fn least(values: impl IntoIterator<Item = Num>) -> Result<Num> {
    values.into_iter().reduce(Num::min).context("min() arg is an empty sequence")
}

/// `max(values)`: the first of equal values.
fn most(values: impl IntoIterator<Item = Num>) -> Result<Num> {
    values.into_iter().reduce(Num::max).context("max() arg is an empty sequence")
}

/// `items[index]` as Python indexes a list (negative from the end).
fn item(items: &[Val], index: i64) -> Result<Val> {
    let at = if index < 0 { index + items.len() as i64 } else { index };
    if at < 0 || at as usize >= items.len() {
        bail!("list index out of range");
    }
    Ok(items[at as usize].clone())
}

/// A slice bound as Python clamps it.
fn bound(len: usize, index: i64) -> usize {
    let at = if index < 0 { (index + len as i64).max(0) } else { index };
    (at as usize).min(len)
}

/// `aligned(profile)` of `_stack`: a collapsed skirt profile with its two split points repeated.
fn aligned(profile: &Val, collapsed: Num, split: Num, at: Num) -> Result<Vec<Val>> {
    let profile = profile.iter()?;
    let len = profile.len() as f64;
    if len == split.f() {
        return Ok(profile);
    }
    if len != collapsed.f() {
        bail!("the native pump skirt has an unknown correspondence");
    }
    let Num::I(at) = at else { bail!("list indices must be integers or slices, not float") };
    let cut = bound(profile.len(), at + 1);
    let mut out = profile[..cut].to_vec();
    out.push(item(&profile, at)?);
    out.extend_from_slice(&profile[cut..]);
    out.push(item(&profile, -1)?);
    Ok(out)
}

/// `_stack(graph, case, start, steps, profiles)`: a ruled stack of the case's skirt sections.
pub fn stack(graph: &AnyGraph, case: &Val, start: &Val, steps: &Val, profiles: &Val) -> Result<Solid> {
    let segments = n(&case.attr("arc_segments")?)?;
    let collapsed = Num::I(4).mul(segments.add(Num::I(1))).add(Num::I(2));
    let split = collapsed.add(Num::I(2));
    let at = Num::I(2).mul(segments.add(Num::I(1)));
    let (cx, cy) = (n(&case.attr("center_x")?)?, n(&case.attr("center_y")?)?);
    let mut points: Vec<[Num; 3]> = vec![];
    let mut section = |profile: &Val, z: Num| -> Result<Val> {
        let mut values = vec![];
        for p in aligned(profile, collapsed, split, at)? {
            let xy = py::unpack(&p, 2)?;
            let point = [cx.add(n(&xy[0])?), cy.add(n(&xy[1])?), z];
            values.push(Num::vals(&point));
            points.push(point);
        }
        Ok(Val::list(values))
    };
    let mut z = n(start)?;
    let all = profiles.iter()?;
    let first = all.first().context("list index out of range")?;
    let mut sections = vec![section(first, z)?];
    for (dz, profile) in steps.iter()?.iter().zip(all.iter().skip(1)) {
        z = z.add(n(dz)?);
        sections.push(section(profile, z)?);
    }
    let mut bounds = vec![];
    for axis in 0..3 {
        bounds.push(least(points.iter().map(|p| p[axis]))?);
        bounds.push(most(points.iter().map(|p| p[axis]))?);
    }
    graph.add("ruled-stack", vec![], Num::vals(&bounds), vec![("sections", Val::list(sections))])
}

/// `_profile_prism(graph, case, profile, z0, z1)`: a case-centred profile swept in Z.
pub fn profile_prism(graph: &AnyGraph, case: &Val, profile: &Val, z0: &Val, z1: &Val) -> Result<Solid> {
    let (cx, cy) = (n(&case.attr("center_x")?)?, n(&case.attr("center_y")?)?);
    let mut section = vec![];
    for p in profile.iter()? {
        let xy = py::unpack(&p, 2)?;
        section.push(Val::Tuple(vec![cx.add(n(&xy[0])?).val(), cy.add(n(&xy[1])?).val()]));
    }
    graph.prism(2, z0, z1, &Val::list(section))
}

/// `_case_drop_well(graph, case, air)`: the case's skirt and lower body, offset by `air`.
pub fn case_drop_well(graph: &AnyGraph, case: &Val, air: &Val) -> Result<Solid> {
    let offset = interop::binary("sub", case.attr("skirt_wall")?, air.clone())?;
    let steps = case.attr("skirt_z_steps")?;
    let profiles = py::call(&case.attr("_skirt_profile_set")?, vec![offset.clone()])?;
    let skirt = stack(graph, case, &Val::Float(0.0), &steps, &profiles)?;
    let start = case.attr("skirt_bottom_z")?;
    let steps = py::call(&case.attr("lower_z_steps")?, vec![])?;
    let profiles = py::call(&case.attr("_lower_profile_set")?, vec![offset.clone()])?;
    let lower = stack(graph, case, &start, &steps, &profiles)?;
    let mut solid = skirt.fuse(&[lower])?;
    let levels = py::call(&case.attr("_stack_levels")?, vec![])?;
    let profiles = py::call(&case.attr("_stack_profiles")?, vec![offset])?;
    for (z, profile) in levels.iter()?.iter().zip(profiles.iter()?.iter()) {
        if n(z)?.f() < -1e-9 {
            solid = solid.fuse(&[profile_prism(graph, case, profile, z, &Val::Float(0.0))?])?;
        }
    }
    Ok(solid)
}

/// `_lower_well(shell, graph, pump_trays)`: the retained pump wells, case-centred at the origin.
pub fn lower_well(shell: &Val, graph: &AnyGraph, pump_trays: &Val) -> Result<Solid> {
    let tray = shell.attr("_tray")?;
    let case = shell.attr("_tray")?.attr("_pc")?;
    let air = shell.attr("cap_pump_air")?;
    let seat = n(&py::call(&shell.attr("pump_skirt_support_z")?, vec![pump_trays.clone()])?)?;
    let mut floors = vec![];
    for row in pump_trays.iter()? {
        floors.push(n(&py::unpack(&row, 3)?[2])?);
    }
    let support = seat.sub(least(floors)?);
    let offset = interop::binary("sub", case.attr("skirt_wall")?, air.clone())?;
    let upper = py::call(&case.attr("_skirt_profile_set")?, vec![offset.clone()])?.get(Val::Int(1))?;
    let lower = py::call(&case.attr("_skirt_profile_set")?, vec![offset])?.get(Val::Int(3))?;
    let bottom = n(&case.attr("lower_cap_top_z")?)?.sub(n(&case.attr("overcut")?)?);
    let (cx, cy) = (n(&case.attr("center_x")?)?, n(&case.attr("center_y")?)?);
    let half = n(&case.attr("cutter_half_extent")?)?;
    let mask = |z0: Val, z1: Val, y0: &Val, y1: &Val| -> Result<Solid> {
        graph.box_(vec![cx.sub(half).val(), cx.add(half).val(), cy.add(n(y0)?).val(), cy.add(n(y1)?).val(), z0, z1])
    };
    let lower_room = case_drop_well(graph, &case, &air)?
        .intersect(&[profile_prism(graph, &case, &lower, &bottom.val(), &support.val())?])?;
    let open = tray.attr("skirt_body_open_y_bounds")?.iter()?;
    let [y0, y1] = open.as_slice() else { bail!("mask() takes 4 positional arguments but {} were given", 2 + open.len()) };
    let lower_room = lower_room.intersect(&[mask(bottom.val(), support.val(), y0, y1)?])?;
    let upper_room = profile_prism(graph, &case, &upper, &support.val(), &Val::Float(0.0))?
        .fuse(&[profile_prism(graph, &case, &lower, &support.val(), &Val::Float(0.0))?])?;
    let upper_room = upper_room.intersect(&[mask(support.val(), Val::Float(0.0), &half.neg().val(),
        &tray.attr("skirt_open_y_max")?)?])?;
    let mut room = upper_room.fuse(&[lower_room])?
        .translate(&Val::Tuple(vec![cx.neg().val(), cy.neg().val(), Val::Float(0.0)]))?;
    let miter = py::unpack(&py::call(&tray.attr("outlet_fore_miter")?, vec![air])?, 4)?;
    let (body_half, y0, open_half) = (n(&miter[0])?, miter[1].clone(), n(&miter[2])?);
    if open_half.f() > body_half.add(Num::F(1e-9)).f() {
        let (y1, z0) = (body_half.val(), tray.attr("outlet_axis_z")?);
        let west = graph.box_(vec![open_half.neg().val(), body_half.neg().val(), y0.clone(), y1.clone(), z0.clone(),
            Val::Float(0.0)])?;
        let east = graph.box_(vec![body_half.val(), open_half.val(), y0, y1, z0, Val::Float(0.0)])?;
        room = room.fuse(&[west, east])?;
    }
    Ok(room)
}

/// `_wing(shell, graph, box, side, spread)`: the wing's line/cubic profile, extruded along Y.
pub fn wing(shell: &Val, graph: &AnyGraph, boxv: &Val, side: &Val, spread: &Val) -> Result<Solid> {
    let wing_profile = shell.attr("_fixed_pump_mount")?.attr("wing_profile")?;
    let profile = py::call(&wing_profile, vec![shell.clone(), boxv.clone(), side.clone(), spread.clone()])?;
    let (mut xs, mut zs) = (vec![], vec![]);
    for segment in profile.get(py::s("segments"))?.iter()? {
        for (_, controls) in interop::entries_of(&segment)? {
            for p in controls.iter()? {
                xs.push(n(&p.get(Val::Int(0))?)?);
                zs.push(n(&p.get(Val::Int(1))?)?);
            }
        }
    }
    let mut bounds = vec![least(xs.clone())?.val(), most(xs)?.val()];
    bounds.extend(profile.get(py::s("span"))?.iter()?);
    bounds.push(least(zs.clone())?.val());
    bounds.push(most(zs)?.val());
    let mut numbers = vec![("axis".to_owned(), Val::Int(1))];
    for (key, value) in interop::entries_of(&profile)? {
        numbers.push((key.str()?, value));
    }
    let numbers = numbers.iter().map(|(key, value)| (key.as_str(), value.clone())).collect();
    graph.add("bezier-prism", vec![], Val::Tuple(bounds), numbers)
}

/// `outlet_cylinder(radius, x, z, y0, y1)` of `_leaves`: a Y cylinder carrying the outlet's
/// tangent stations (one list, shared by every cylinder of one `_leaves`).
#[allow(clippy::too_many_arguments)]
fn outlet_cylinder(graph: &AnyGraph, stations: &Val, radius: &Val, x: &Val, z: &Val, y0: &Val, y1: &Val) -> Result<Solid> {
    let (r, xn, zn) = (n(radius)?, n(x)?, n(z)?);
    let bounds = Val::Tuple(vec![xn.sub(r).val(), xn.add(r).val(), y0.clone(), y1.clone(), zn.sub(r).val(), zn.add(r).val()]);
    graph.add("cylinder", vec![], bounds, vec![
        ("axis", Val::Int(1)),
        ("radius", radius.clone()),
        ("centre", Val::Tuple(vec![x.clone(), z.clone()])),
        ("span", Val::Tuple(vec![y0.clone(), y1.clone()])),
        ("stations", stations.clone()),
    ])
}

/// `_leaves(shell, graph)` entered: the enclosure's lower well, the mount's wing and the outlet
/// cylinders record on `graph` until [`Leaves::exit`] puts the originals back.
pub struct Leaves {
    shell: Val,
    fixed: Val,
    /// `shell._pump_lower_well`, `fixed._wing`, `shell._ycyl` as they were.
    originals: [Val; 3],
    leaves: RefCell<Vec<Leaf>>,
}

impl Leaves {
    /// `__enter__`.
    pub fn enter(shell: &Val, graph: &AnyGraph) -> Result<Leaves> {
        let fixed = shell.attr("_fixed_pump_mount")?;
        let originals = [shell.attr("_pump_lower_well")?, fixed.attr("_wing")?, shell.attr("_ycyl")?];
        let tangent = py::call(&shell.attr("_tray")?.attr("outlet_under_tangent")?, vec![shell.attr("cap_pump_air")?])?;
        let tangent = py::unpack(&tangent, 4)?;
        let dz = interop::binary("sub", tangent[3].clone(), shell.attr("_tray")?.attr("outlet_axis_z")?)?.num()?;
        let mut stations = vec![];
        for side in [-1.0, 1.0] {
            let x = interop::binary("mul", Val::Float(side), tangent[2].clone())?.num()?;
            stations.push(Val::Float(dz.atan2(x)));
        }
        let stations = Val::list(stations);
        let well = {
            let (shell, graph) = (shell.clone(), graph.clone());
            panel::leaf(move |args, kwargs| {
                let mut b = py::bind(args, kwargs, &["trays"], &[])?;
                lower_well(&shell, &graph, &b.req("trays")?)
            })
        };
        let wing_leaf = {
            let graph = graph.clone();
            panel::leaf(move |args, kwargs| {
                let mut b = py::bind(args, kwargs, &["e", "box", "side", "spread"], &[])?;
                let [e, boxv, side, spread] = ["e", "box", "side", "spread"].map(|name| b.req(name));
                wing(&e?, &graph, &boxv?, &side?, &spread?)
            })
        };
        let cylinder = {
            let graph = graph.clone();
            panel::leaf(move |args, kwargs| {
                let mut b = py::bind(args, kwargs, &["radius", "x", "z", "y0", "y1"], &[])?;
                let [radius, x, z, y0, y1] = ["radius", "x", "z", "y0", "y1"].map(|name| b.req(name));
                outlet_cylinder(&graph, &stations, &radius?, &x?, &z?, &y0?, &y1?)
            })
        };
        let leaves = Leaves { shell: shell.clone(), fixed: fixed.clone(), originals, leaves: RefCell::new(vec![]) };
        let installed = shell.setattr("_pump_lower_well", well.value.clone())
            .and_then(|_| fixed.setattr("_wing", wing_leaf.value.clone()))
            .and_then(|_| shell.setattr("_ycyl", cylinder.value.clone()));
        leaves.leaves.borrow_mut().extend([well, wing_leaf, cylinder]);
        if let Err(error) = installed {
            // The generated context manager runs its exit after a failed enter, ignoring its error.
            let _ = leaves.exit();
            return Err(error);
        }
        Ok(leaves)
    }
    /// `__exit__`: the originals, in the order Python restores them.
    pub fn exit(&self) -> Result<()> {
        self.shell.setattr("_pump_lower_well", self.originals[0].clone())?;
        self.fixed.setattr("_wing", self.originals[1].clone())?;
        self.shell.setattr("_ycyl", self.originals[2].clone())?;
        self.leaves.borrow_mut().clear();
        Ok(())
    }
}

/// `_leaves(shell, graph)`: the context manager generated callers enter.
pub fn leaves(rt: &Rt, shell: &Val, graph: &Val) -> Val {
    let held: Rc<RefCell<Option<Leaves>>> = Rc::new(RefCell::new(None));
    let enter = {
        let (rt, shell, graph, held) = (rt.clone(), shell.clone(), graph.clone(), held.clone());
        Val::function(move |_, _| {
            let _frame = rt.frame(MODULE);
            *held.borrow_mut() = Some(Leaves::enter(&shell, &AnyGraph::from_val(&graph))?);
            Ok(Val::None)
        })
    };
    let exit = {
        let rt = rt.clone();
        Val::function(move |_, _| {
            let _frame = rt.frame(MODULE);
            match held.borrow().as_ref() {
                Some(leaves) => leaves.exit()?,
                None => bail!("_enclosure_pump_retainer: unknown name original_well"),
            }
            Ok(Val::None)
        })
    };
    rt::context(enter, exit)
}

/// The same retained wells and wing profiles as the native retainer builder.
///
/// `seated` is the caller's value: it reaches `build_pump_retainer` and the result as given.
pub fn numbers(rt: &Rt, shell: &Val, boxv: &Val, seated: &Val) -> Result<Val> {
    let _frame = rt.frame(MODULE);
    rt.import("_enclosure_panel")?;
    rt.import("_materials")?;
    let linear = rt.member("_materials", "linear")?;
    let graph = Graph::new();
    let any = AnyGraph::Native(graph.clone());
    // `with _record(..), _leaves(..)` as the generated code runs it: a failed `_leaves` enter or
    // exit leaves `_record` entered.
    let recording = Recording::enter(rt, shell, &any, Solid::Py(Val::None))?;
    let leaves = Leaves::enter(shell, &any)?;
    let result = (|| {
        py::call_kw(&shell.attr("build_pump_retainer")?, vec![boxv.clone()], vec![("seated", seated.clone())])
    })();
    leaves.exit()?;
    recording.exit()?;
    let result = Solid::from_val(&result?);
    let panel = graph.document(&result, &[])?;
    let color = py::call(&linear, vec![shell.attr("PIECE_COLORS")?.get(py::s("pump-retainer"))?])?;
    let name = if seated.truthy()? { "enclosure-pump-retainer-seated" } else { "enclosure-pump-retainer" };
    Ok(py::dict([("panel", panel), ("color", color), ("name", py::s(name)), ("seated", seated.clone())]))
}

/// Write one retainer pose through the installed part engine.
pub fn cut(rt: &Rt, shell: &Val, boxv: &Val, directory: &Val, seated: &Val) -> Result<Val> {
    let _frame = rt.frame(MODULE);
    let rust_part = rt.import("_rust_part")?;
    let directory = py::call(&rt.member("pathlib", "Path")?, vec![directory.clone()])?;
    let cut = rust_part.attr("cut")?;
    let numbers = numbers(rt, shell, boxv, seated)?;
    let numbers_name = if seated.truthy()? { py::s("enclosure-pump-retainer-seated") } else { Val::None };
    let said = py::call_kw(&cut, vec![py::s("enclosure-shell"), py::s("enclosure-pump-retainer"), numbers, directory.clone()],
        vec![("numbers_name", numbers_name)])?;
    if !seated.truthy()? {
        rt.import("_enclosure_presentation")?;
        let step = interop::binary("truediv", directory, py::s("enclosure-pump-retainer.step"))?;
        super::_enclosure_presentation::print_payload(rt, &PathBuf::from(step.str()?), Val::Bool(false))?;
    }
    Ok(said)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("contextmanager", rt.member("contextlib", "contextmanager")?)?;
    ns.set("math", rt.import("math")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    ns.def(rt, "_stack", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["graph", "case", "start", "steps", "profiles"], &[])?;
        let graph = AnyGraph::from_val(&b.req("graph")?);
        let [case, start, steps, profiles] = ["case", "start", "steps", "profiles"].map(|name| b.req(name));
        Ok(stack(&graph, &case?, &start?, &steps?, &profiles?)?.to_val())
    })?;
    ns.def(rt, "_profile_prism", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["graph", "case", "profile", "z0", "z1"], &[])?;
        let graph = AnyGraph::from_val(&b.req("graph")?);
        let [case, profile, z0, z1] = ["case", "profile", "z0", "z1"].map(|name| b.req(name));
        Ok(profile_prism(&graph, &case?, &profile?, &z0?, &z1?)?.to_val())
    })?;
    ns.def(rt, "_case_drop_well", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["graph", "case", "air"], &[])?;
        let graph = AnyGraph::from_val(&b.req("graph")?);
        Ok(case_drop_well(&graph, &b.req("case")?, &b.req("air")?)?.to_val())
    })?;
    ns.def(rt, "_lower_well", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["shell", "graph", "pump_trays"], &[])?;
        let shell = b.req("shell")?;
        let graph = AnyGraph::from_val(&b.req("graph")?);
        Ok(lower_well(&shell, &graph, &b.req("pump_trays")?)?.to_val())
    })?;
    ns.def(rt, "_wing", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["shell", "graph", "box", "side", "spread"], &[])?;
        let shell = b.req("shell")?;
        let graph = AnyGraph::from_val(&b.req("graph")?);
        let [boxv, side, spread] = ["box", "side", "spread"].map(|name| b.req(name));
        Ok(wing(&shell, &graph, &boxv?, &side?, &spread?)?.to_val())
    })?;
    ns.def(rt, "_leaves", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["shell", "graph"], &[])?;
        Ok(leaves(rt, &b.req("shell")?, &b.req("graph")?))
    })?;
    ns.def(rt, "numbers", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["shell", "box"], &["seated"])?;
        let (shell, boxv) = (b.req("shell")?, b.req("box")?);
        let seated = b.opt("seated").unwrap_or(Val::Bool(false));
        numbers(rt, &shell, &boxv, &seated)
    })?;
    ns.def(rt, "cut", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["shell", "box", "directory"], &["seated"])?;
        let (shell, boxv, directory) = (b.req("shell")?, b.req("box")?, b.req("directory")?);
        let seated = b.opt("seated").unwrap_or(Val::Bool(false));
        cut(rt, &shell, &boxv, &directory, &seated)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}
