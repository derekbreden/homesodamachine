//! The construction questions `_machine_checks` reads out of the enclosure assembly: the port
//! pocket and clamp-stack bounds stated at import, the wedge clearances and the anchor corbels
//! an authored tube anchor keeps.
use super::_stated_bounds;
use super::num::Num;
use super::py::{self, s};
use super::rt::{Ns, Rt};
use anyhow::{Result, bail};
use hsm_documents::interop::{self, Val};

/// Not yet compared with the generated build: the hybrid development build runs the generated namespace.
pub const TYPED: bool = false;

const MODULE: &str = "_assembly_questions";

struct State {
    /// `_enc`: the enclosure datums the corbel question asks about.
    enc: Val,
    /// `_enc.wall + PORT_BOSS_PROUD + fits.slip`, the floor of every clamp stack.
    floor: Num,
}

/// `port_clamp_stack(t)`: the wall at the fitting's station, floored on the plain wall, the ring's
/// boss and the slip fit.
fn port_clamp_stack(st: &State, t: Num) -> Num {
    t.max(st.floor)
}

/// `authored_anchor_corbels(stations)`: each corbel end an authored tube anchor specifies, as the
/// wedge question's kept room.
fn authored_anchor_corbels(st: &State, stations: &Val) -> Result<Val> {
    let frames = py::unpack(&py::method(&st.enc, "back_top_frames", vec![])?, 2)?;
    let (roots, lane) = (frames[0].clone(), frames[1].clone());
    let up = py::method(&st.enc, "print_up", vec![s("back"), s("top")])?;
    let mut rooms = vec![];
    for station in stations.iter()? {
        if station.len()? < 5 {
            continue;
        }
        let forms = station.get(Val::Int(4))?.iter()?;
        let bounds = py::method(&st.enc, "tube_anchor_end_corbel_bounds", vec![station.clone(), roots.clone(), lane.clone(), up.clone()])?
            .iter()?;
        for (i, (form, bound)) in forms.iter().zip(bounds).enumerate() {
            if !interop::eq(form, &s("corbel"))? || matches!(bound, Val::None) {
                continue;
            }
            let mid = station.get(Val::Int(0))?;
            let at = |k: i64| -> Result<String> { interop::format(&mid.get(Val::Int(k))?, ".2f") };
            let label = format!("tube anchor at ({}, {}, {}), end {}", at(0)?, at(1)?, at(2)?, i + 1);
            rooms.push(Val::Tuple(vec![
                s(label),
                bound,
                s("the anchor site specifies its ordinary full-width 45-degree corbel"),
            ]));
        }
    }
    Ok(Val::Tuple(rooms))
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", Val::None)?;
    let datums = rt.import("_enclosure_datums")?;
    ns.set("_enclosure_datums", datums.clone())?;
    let enc = py::method(&datums, "load", vec![])?;
    ns.set("_enc", enc.clone())?;
    ns.set("_stated", rt.import("_stated_bounds")?)?;
    let above = rt.import("above_core")?;
    ns.set("_above", above.clone())?;
    let fits = rt.import("fits")?;
    ns.set("fits", fits.clone())?;
    let jg = rt.import("jg_bulkhead_union")?;
    ns.set("_jg", jg.clone())?;
    let ring = rt.import("bulkhead_ring")?;
    ns.set("_ring", ring.clone())?;
    let drain = rt.import("neofit_drain_bulkhead")?;
    ns.set("_drain_bulkhead", drain.clone())?;
    let neofit = rt.import("neofit_bulkhead")?;
    ns.set("_neofit", neofit.clone())?;

    let fittings: [(&str, &Val, &str, &str, &str); 6] = [
        ("bulkhead-water", &jg, "union", "water", "water"),
        ("bulkhead-carb", &jg, "union", "carb", "carb"),
        ("bulkhead-flavor-a", &drain, "drain", "flavor-a", "flavor"),
        ("bulkhead-flavor-b", &drain, "drain", "flavor-b", "flavor"),
        ("co2-inlet", &neofit, "neofit", "co2", "co2"),
        ("bulkhead-drain", &drain, "drain", "drain", "drain"),
    ];
    ns.set("Y_WALL_FITTINGS", py::dict(fittings.iter().map(|(n, fit, r, w, f)| {
        (*n, Val::Tuple(vec![(*fit).clone(), s(*r), s(*w), s(*f)]))
    })))?;
    let thick = ring.attr("THICK")?;
    ns.set("PORT_BOSS_PROUD", thick.clone())?;
    let (thick, wall) = (Num::of(&thick)?, Num::of(&enc.attr("wall")?)?);
    let floor = wall.add(thick).add(Num::of(&fits.attr("slip")?)?);
    let st = rt.keep(MODULE, State { enc: enc.clone(), floor });
    ns.def(rt, "port_clamp_stack", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["t"], &[])?;
        let t = Num::of(&a.req("t")?)?;
        Ok(port_clamp_stack(&*rt.state::<State>(MODULE)?, t).val())
    })?;

    _stated_bounds::state_bound(
        rt,
        s("port-pocket-floor"),
        s("Every pocket leaves wall under the chip it holds"),
        s(format!("a chip under `enclosure.wall` {} mm", wall.fmt("g"))),
        &Val::Bool(thick.f() < wall.f() - 1e-09),
        &s(format!(
            "the pocket is cut {} mm into a wall {} mm thick and leaves {} mm of floor under the chip.",
            thick.fmt("g"),
            wall.fmt("g"),
            wall.sub(thick).fmt(".2f")
        )),
    )?;
    let port_stack = _stated_bounds::bound(
        rt,
        s("port-clamp-stack"),
        s("Every fitting's bare barrel takes the wall and the ring lying in it"),
        s(format!("a stack of the wall at its own station, floored on `enclosure.wall` and {} mm of boss", thick.fmt("g"))),
    )?;
    ns.set("_port_stack", port_stack.clone())?;
    let ports = py::snapshot(&py::at(&py::at(&py::method(&above, "specification", vec![])?, "rear_wall")?, "wet_ports")?)?.iter()?;
    for (n, fit, r, w, f) in fittings {
        ns.set("_n", s(n))?;
        ns.set("_fit", fit.clone())?;
        ns.set("_r", s(r))?;
        ns.set("_w", s(w))?;
        ns.set("_f", s(f))?;
        let panel = fit.attr("PANEL_THREAD").unwrap_or(Val::None);
        let bare = if panel.truthy()? { panel } else { fit.attr("THREAD_LEN")? };
        ns.set("_bare", bare.clone())?;
        let mut port = None;
        for row in &ports {
            if interop::eq(&py::at(row, "name")?, &s(n))? {
                port = Some(row.clone());
                break;
            }
        }
        let Some(port) = port else { bail!("StopIteration") };
        ns.set("_port", port.clone())?;
        let t = py::method(&enc, "back_wall_t_at", vec![py::at(&port, "center_x_mm")?, py::at(&port, "center_z_mm")?])?;
        ns.set("_t", t.clone())?;
        let t = Num::of(&t)?;
        let stack = port_clamp_stack(&st, t);
        ns.set("_stack", stack.val())?;
        let bare = Num::of(&bare)?;
        let note = format!(
            "{n} offers {} mm of bare barrel and the joint it makes up through {} mm of wall stacks {} mm, leaving the nut none of it",
            bare.fmt(".2f"),
            t.fmt("g"),
            stack.fmt("g")
        );
        _stated_bounds::take(&port_stack, &Val::Bool(stack.f() <= bare.f() + 1e-09), &s(note))?;
    }
    ns.set("WEDGE_CLEAR", Val::Float(1.0))?;
    ns.set("KEPT_WEDGES", Val::Tuple(vec![]))?;
    ns.set("_PLAN_INSET", Val::Float(0.02))?;
    ns.def(rt, "authored_anchor_corbels", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["stations"], &[])?;
        let stations = a.req("stations")?;
        authored_anchor_corbels(&*rt.state::<State>(MODULE)?, &stations)
    })?;
    Ok(())
}
