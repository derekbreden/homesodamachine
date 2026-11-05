//! The ledger of bounds a module states about its own constants.
//!
//! A bound is an instance of the `StatedBound` class its Python surface declares, so a module
//! that imports the ledger holds and calls the same object the Rust recipes record into. The
//! ledger keeps each open bound with its id, in the order the bounds were stated.
use super::rt::{Ns, Rt};
use super::{docs, py};
use anyhow::Result;
use hsm_documents::interop::{self, Val};
use py::s;
use std::cell::RefCell;

/// Converted: the hybrid development build runs this module, not its generated namespace.
pub const TYPED: bool = true;

const MODULE: &str = "_stated_bounds";

pub struct State {
    /// `BOUNDS`: every open bound, in stated order.
    bounds: Val,
    ids: RefCell<Vec<Val>>,
    bound_type: Val,
    stated_type: Val,
}

fn state(rt: &Rt) -> Result<std::rc::Rc<State>> {
    rt.state::<State>(MODULE)
}

/// Open one stated bound and hand back the recorder its readings are taken with.
pub fn bound(rt: &Rt, id: Val, label: Val, target: Val) -> Result<Val> {
    let st = state(rt)?;
    let b = py::call(&st.stated_type, vec![id.clone(), label, target])?;
    let mut ids = st.ids.borrow_mut();
    let Val::List(rows) = &st.bounds else { unreachable!() };
    let mut rows = rows.borrow_mut();
    let mut kept_ids = Vec::with_capacity(ids.len() + 1);
    let mut kept = Vec::with_capacity(ids.len() + 1);
    for (x, row) in ids.iter().zip(rows.iter()) {
        if !interop::eq(x, &id)? {
            kept_ids.push(x.clone());
            kept.push(row.clone());
        }
    }
    kept_ids.push(id);
    kept.push(b.clone());
    *ids = kept_ids;
    *rows = kept;
    Ok(b)
}

/// One bound with a single reading, stated and read in one line.
pub fn state_bound(rt: &Rt, id: Val, label: Val, target: Val, ok: &Val, note: &Val) -> Result<bool> {
    let b = bound(rt, id, label, target)?;
    take(&b, ok, note)
}

/// `StatedBound.__call__`: take one reading and hand back the reading itself.
pub fn take(b: &Val, ok: &Val, note: &Val) -> Result<bool> {
    let ok = ok.truthy()?;
    let total = b.attr("total")?;
    b.setattr("total", interop::binary("add", total, Val::Int(1))?)?;
    if ok {
        let held = b.attr("held")?;
        b.setattr("held", interop::binary("add", held, Val::Int(1))?)?;
    } else if note.truthy()? {
        py::method(&b.attr("detail")?, "append", vec![note.clone()])?;
    }
    Ok(ok)
}

/// A bound with no readings holds: its population is empty.
fn holds(b: &Val) -> Result<bool> {
    interop::eq(&b.attr("held")?, &b.attr("total")?)
}

fn value(b: &Val) -> Result<String> {
    let total = b.attr("total")?;
    if interop::eq(&total, &Val::Int(1))? {
        return Ok(if holds(b)? { "holds" } else { "open" }.into());
    }
    Ok(format!("{}/{} hold", interop::format(&b.attr("held")?, "")?, interop::format(&total, "")?))
}

fn record(st: &State, b: &Val) -> Result<Val> {
    let detail = Val::list(b.attr("detail")?.iter()?);
    py::call(&st.bound_type, vec![b.attr("id")?, b.attr("label")?, holds(b)?.into(), s(value(b)?), b.attr("target")?, detail])
}

/// Every stated bound as a plain `Bound` tuple, for a ledger that renders them.
pub fn records(rt: &Rt) -> Result<Vec<Val>> {
    let st = state(rt)?;
    let rows = st.bounds.iter()?;
    rows.iter().map(|b| record(&st, b)).collect()
}

/// The stated bounds, printed: 0 when every one holds, 1 when any is open.
fn report(rt: &Rt) -> Result<i64> {
    let st = state(rt)?;
    let rows = st.bounds.iter()?;
    let mut open = 0;
    for b in &rows {
        if !b.attr("ok")?.truthy()? {
            open += 1;
        }
    }
    for b in &rows {
        let flag = if b.attr("ok")?.truthy()? { "OK  " } else { "OPEN" };
        rt.print(format!(
            "  {flag} {} {} {}",
            interop::format(&b.attr("id")?, "28")?,
            interop::format(&b.attr("value")?, "12")?,
            interop::format(&b.attr("label")?, "")?
        ))?;
        for line in b.attr("detail")?.iter()? {
            rt.print(format!("         {}", interop::format(&line, "")?))?;
        }
    }
    rt.print(format!("\n{}/{} stated bounds hold", rows.len() - open, rows.len()))?;
    Ok(if open > 0 { 1 } else { 0 })
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::STATED_BOUNDS))?;
    let namedtuple = rt.member("collections", "namedtuple")?;
    ns.set("namedtuple", namedtuple.clone())?;
    let bound_type = py::call_kw(&namedtuple, vec![s("Bound"), s("id label ok value target detail")], vec![("module", ns.get("__name__")?)])?;
    ns.set("Bound", bound_type.clone())?;
    let bounds = Val::list(vec![]);
    ns.set("BOUNDS", bounds.clone())?;
    ns.def(rt, "StatedBound.__init__", |_, args, kw| {
        let mut a = py::bind(args, kw, &["self", "id", "label", "target"], &[])?;
        let b = a.req("self")?;
        b.setattr("id", a.req("id")?)?;
        b.setattr("label", a.req("label")?)?;
        b.setattr("target", a.req("target")?)?;
        b.setattr("held", Val::Int(0))?;
        b.setattr("total", Val::Int(0))?;
        b.setattr("detail", Val::list(vec![]))?;
        Ok(Val::None)
    })?;
    ns.def(rt, "StatedBound.__call__", |_, args, kw| {
        let mut a = py::bind(args, kw, &["self", "ok", "note"], &[])?;
        let b = a.req("self")?;
        let ok = a.req("ok")?;
        let note = a.opt("note").unwrap_or_else(|| s(""));
        Ok(take(&b, &ok, &note)?.into())
    })?;
    ns.def(rt, "StatedBound.ok", |_, args, kw| {
        let mut a = py::bind(args, kw, &["self"], &[])?;
        Ok(holds(&a.req("self")?)?.into())
    })?;
    ns.def(rt, "StatedBound.value", |_, args, kw| {
        let mut a = py::bind(args, kw, &["self"], &[])?;
        Ok(s(value(&a.req("self")?)?))
    })?;
    ns.def(rt, "StatedBound.record", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["self"], &[])?;
        let st = state(rt)?;
        record(&st, &a.req("self")?)
    })?;
    let stated_type = rt.python_type(MODULE, "StatedBound")?;
    ns.set("StatedBound", stated_type.clone())?;
    rt.keep(MODULE, State { bounds, ids: RefCell::new(vec![]), bound_type, stated_type });
    ns.def(rt, "bound", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["id", "label", "target"], &[])?;
        bound(rt, a.req("id")?, a.req("label")?, a.req("target")?)
    })?;
    ns.def(rt, "state", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["id", "label", "target", "ok", "note"], &[])?;
        let (id, label, target, ok) = (a.req("id")?, a.req("label")?, a.req("target")?, a.req("ok")?);
        let note = a.opt("note").unwrap_or_else(|| s(""));
        Ok(state_bound(rt, id, label, target, &ok, &note)?.into())
    })?;
    ns.def(rt, "records", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(Val::list(records(rt)?))
    })?;
    ns.def(rt, "report", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(Val::Int(report(rt)?))
    })?;
    Ok(())
}
