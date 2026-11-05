//! Integral tube and cable restraints on their owning enclosure quadrant.
//!
//! Typed API: [`features`] gives one quadrant's restraint bodies with their site records, and
//! [`apply`] fuses them onto a piece. The bodies are `route_snap`'s CadQuery solids (Python
//! objects, reached by callback); the tube sites come from [`super::_tube_snap_sites::tube_sites`].
//!
//! The back-top recipe replaces this module's `apply` while it records (`_replace` in
//! `_enclosure_back_top._leaves`); nothing here calls `apply`, so the replacement reaches every
//! caller that reads it from this module.
use super::_tube_snap_sites::{self as tube_snap_sites, SharedRoot};
use super::num;
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result};
use hsm_documents::interop::eq;
use std::path::Path;

pub const TYPED: bool = true;

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    rt.import("pathlib")?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    ns.set("sys", rt.import("sys")?)?;
    ns.set("cq", rt.import("cadquery")?)?;
    let file = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    let root = file
        .ancestors()
        .skip(1)
        .find(|p| p.join("hardware").join("wiring").is_dir())
        .map(Path::to_owned)
        .context("StopIteration")?;
    ns.set("_ROOT", Val::Path(root.clone()))?;
    for directory in [root.clone(), root.join("hardware").join("printed-parts").join("cadlib")] {
        ns.set("directory", Val::Path(directory.clone()))?;
        let text = py::path_str(&directory);
        if !py::sys_path_has(rt, &text)? {
            py::sys_path_insert(rt, &text)?;
        }
    }
    ns.set("route_snap", rt.import("route_snap")?)?;
    ns.def(rt, "features", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["host"], &[])?;
        features(rt, &b.req("host")?)
    })?;
    ns.def(rt, "apply", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["piece", "y_side", "z_side"], &[])?;
        let (piece, y_side, z_side) = (b.req("piece")?, b.req("y_side")?, b.req("z_side")?);
        apply(rt, &piece, &y_side, &z_side)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}

/// One flavor station's paired seats, gathered under their shared root.
struct Group {
    root: SharedRoot,
    members: Vec<Val>,
    bodies: Vec<Val>,
}

/// Native additions; paired seats share one broad filled root per station.
///
/// Each entry is `(record, body)`: a cable or tube site's record with its `kind`, or a
/// `tube-group` record holding a station's members and shared root.
pub fn features(rt: &Rt, host: &Val) -> Result<Val> {
    let cable_sites = rt.member("hardware.wiring.installed.retainers", "cable_sites")?;
    rt.import("_tube_snap_sites")?;
    let route_snap = rt.import("route_snap")?;
    let mut result = vec![];
    for site in py::snapshot(&py::call(&cable_sites, vec![])?)?.iter()? {
        if !eq(&py::at(&site, "host")?, host)? {
            continue;
        }
        let field = |key: &str| py::at(&site, key);
        let body = py::call_kw(
            &route_snap.attr("cable_hook")?,
            vec![field("origin")?, field("outward")?, field("profile_up")?],
            vec![
                ("seat_depth", field("seat_depth")?),
                ("seat_height", field("seat_height")?),
                ("span", field("span")?),
                ("stock", field("stock")?),
                ("beak", field("beak")?),
            ],
        )?;
        result.push(py::tuple([py::merged(&site, [("kind", py::s("cable"))])?, body]));
    }
    let mut groups: Vec<Group> = vec![];
    for site in tube_snap_sites::tube_sites() {
        if !eq(&py::s(site.host.clone()), host)? {
            continue;
        }
        let body = py::call_kw(
            &route_snap.attr("tube_clip")?,
            vec![
                py::ftuple(&site.centre),
                py::ftuple(&site.along),
                py::ftuple(&site.outward),
                Val::Float(site.root_distance),
            ],
            vec![
                ("tube_od", Val::Float(site.tube_od)),
                ("bore_diameter", Val::Float(site.bore_diameter)),
                ("span", Val::Float(site.span)),
                ("wing", Val::Float(site.wing)),
                ("print_up", py::ftuple(&site.print_up)),
            ],
        )?;
        match &site.group {
            None => result.push(py::tuple([py::merged(&site.val(), [("kind", py::s("tube"))])?, body])),
            Some(root) => {
                let at = match groups.iter().position(|group| group.root.id == root.id) {
                    Some(at) => at,
                    None => {
                        groups.push(Group { root: root.clone(), members: vec![], bodies: vec![] });
                        groups.len() - 1
                    }
                };
                groups[at].members.push(site.val());
                groups[at].bodies.push(body);
            }
        }
    }
    let cq = rt.import("cadquery")?;
    for group in groups {
        let root = &group.root;
        let make_box = cq.attr("Solid")?.attr("makeBox")?;
        let mut size: Vec<Val> = root.bridge_size.iter().map(|&v| Val::Float(v)).collect();
        size.push(py::call(&cq.attr("Vector")?, root.bridge_origin.iter().map(|&v| Val::Float(v)).collect())?);
        let bridge = py::call(&make_box, size)?;
        let (first, others) = group.bodies.split_first().context("not enough values to unpack")?;
        let mut fused = vec![bridge];
        fused.extend(others.iter().cloned());
        let body = py::method(&py::method(first, "fuse", fused)?, "clean", vec![])?;
        result.push(py::tuple([
            py::dict([
                ("id", py::s(root.id.clone())),
                ("kind", py::s("tube-group")),
                ("host", host.clone()),
                ("members", Val::Tuple(group.members)),
                ("shared_root", root.val()),
            ]),
            body,
        ]));
    }
    Ok(Val::Tuple(result))
}

/// `piece` with the restraints its quadrant owns fused on; `piece` itself when it owns none.
pub fn apply(rt: &Rt, piece: &Val, y_side: &Val, z_side: &Val) -> Result<Val> {
    let host = format!("enclosure-{}-{}", num::fmtv(y_side, "")?, num::fmtv(z_side, "")?);
    let mut additions = vec![];
    for entry in features(rt, &py::s(host))?.iter()? {
        additions.push(py::unpack(&entry, 2)?.swap_remove(1));
    }
    if additions.is_empty() {
        return Ok(piece.clone());
    }
    py::method(piece, "fuse", additions)
}
