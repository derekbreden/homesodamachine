//! Selected integral tube snaps on back-top's roof and east wall.
//!
//! The listed world-space line endpoints and parameters are explicit routing
//! datums; this registry does not infer clearance or follow an unrelated route
//! edit. Back-top builds in machine -Z. Each flavor station shares one filled
//! root bridge while its two seats remain individual routing records.
//!
//! Quarter-inch tube retains the selected C2 section: diameter 6.35, wing 2.40.
//! The 4 mm tube uses diameter 4.10 and a 1.52 mm functional spring section scaled
//! from C2's proportions. That smaller section is a modeled fit estimate.
//!
//! Typed API: [`tube_sites`] gives the placed [`TubeSite`] records; [`TubeSite::val`] is the
//! record as the namespace's `tube_sites()` returns it.
use super::num;
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::Result;

pub const TYPED: bool = true;

/// One `_SITES` row: a straight route segment and the snap section that holds it.
struct Site {
    id: &'static str,
    route_id: &'static str,
    endpoints: [[f64; 3]; 2],
    face_axis: usize,
    face: f64,
    outward: [f64; 3],
    tube_od: f64,
    bore_diameter: f64,
    wing: f64,
    source: &'static str,
    source_function: &'static str,
    source_segment: i64,
    install_before: &'static [&'static str],
    basis: &'static str,
    /// `line_parameter`, where the row names one (the snap's place along its line).
    line_parameter: Option<f64>,
    /// `group`, where the row shares a root bridge with its station's other seat.
    group: Option<&'static str>,
}

const SITES: &[Site] = &[Site {
    id: "tube-snap-reservoir-a-fill-east",
    route_id: "fluid-14",
    endpoints: [[94.31, 244., 258.5], [94.31, 286., 258.5]],
    face_axis: 0,
    face: 98.5,
    outward: [-1., 0., 0.],
    tube_od: 6.35,
    bore_diameter: 6.35,
    wing: 2.40,
    source: "hardware/manifold-layout/reservoir-a-routes.json",
    source_function: "fluid-14.segments",
    source_segment: 12,
    install_before: &["fluid-16"],
    basis: "East-wall fill straight; seat fill before draw and use the integral fore C2 seats on the cold-core lid.",
    line_parameter: None,
    group: None,
}];

/// The flavor stations' shared roof bridges, by their Y.
const SHARED_ROOT_YS: [i64; 2] = [354, 390];

/// One flavor station's filled root bridge, shared by its two seats.
#[derive(Clone, Debug)]
pub struct SharedRoot {
    pub id: String,
    pub bridge_origin: [f64; 3],
    pub bridge_size: [f64; 3],
}
impl SharedRoot {
    pub fn val(&self) -> Val {
        py::dict([
            ("id", py::s(self.id.clone())),
            ("bridge_origin", py::ftuple(&self.bridge_origin)),
            ("bridge_size", py::ftuple(&self.bridge_size)),
        ])
    }
}

/// `_SHARED_ROOTS`, in definition order.
fn shared_roots() -> Vec<SharedRoot> {
    SHARED_ROOT_YS
        .iter()
        .map(|&y| SharedRoot {
            id: format!("tube-snap-flavor-roof-{}", num::fmti(y, "")),
            bridge_origin: [-51.53, y as f64 - 4., 343.],
            bridge_size: [3.06, 8., 3.1],
        })
        .collect()
}

/// Where a site's parameters came from, as its record reports them.
#[derive(Clone, Debug)]
pub struct SourceParameter {
    pub file: String,
    pub function: String,
    pub native_segment_index: i64,
    pub line_endpoints_world_mm: [[f64; 3]; 2],
    pub line_parameter: f64,
    pub straight_end_clearance_mm: f64,
    pub straight_end_clearances_mm: [f64; 2],
    pub host_face_axis: String,
    pub host_face_coordinate_mm: f64,
}

/// One placed tube snap: its line, section and host face.
#[derive(Clone, Debug)]
pub struct TubeSite {
    pub id: String,
    pub route_id: String,
    pub host: String,
    pub centre: [f64; 3],
    pub along: [f64; 3],
    pub outward: [f64; 3],
    pub root_distance: f64,
    pub tube_od: f64,
    pub bore_diameter: f64,
    pub wing: f64,
    pub span: f64,
    pub print_up: [f64; 3],
    pub basis: String,
    pub install_before: Vec<String>,
    pub group: Option<SharedRoot>,
    pub source_parameter: SourceParameter,
}
impl TubeSite {
    /// The record as `tube_sites()` returns it to Python.
    pub fn val(&self) -> Val {
        let p = &self.source_parameter;
        let mut rows = vec![
            ("id", py::s(self.id.clone())),
            ("route_id", py::s(self.route_id.clone())),
            ("host", py::s(self.host.clone())),
            ("centre", py::ftuple(&self.centre)),
            ("along", py::ftuple(&self.along)),
            ("outward", py::ftuple(&self.outward)),
            ("root_distance", Val::Float(self.root_distance)),
            ("tube_od", Val::Float(self.tube_od)),
            ("bore_diameter", Val::Float(self.bore_diameter)),
            ("wing", Val::Float(self.wing)),
            ("span", Val::Float(self.span)),
            ("print_up", py::ftuple(&self.print_up)),
            ("basis", py::s(self.basis.clone())),
            ("install_before", py::tuple(self.install_before.iter().map(|s| py::s(s.clone())))),
        ];
        if let Some(group) = &self.group {
            rows.push(("group", group.val()));
        }
        rows.push(("source_parameter", py::dict([
            ("file", py::s(p.file.clone())),
            ("function", py::s(p.function.clone())),
            ("native_segment_index", Val::Int(p.native_segment_index)),
            ("line_endpoints_world_mm", py::tuple(p.line_endpoints_world_mm.iter().map(|e| py::ftuple(e)))),
            ("line_parameter", Val::Float(p.line_parameter)),
            ("straight_end_clearance_mm", Val::Float(p.straight_end_clearance_mm)),
            ("straight_end_clearances_mm", py::ftuple(&p.straight_end_clearances_mm)),
            ("host_face_axis", py::s(p.host_face_axis.clone())),
            ("host_face_coordinate_mm", Val::Float(p.host_face_coordinate_mm)),
        ])));
        py::dict(rows)
    }
}

/// A `_SITES` row as the namespace holds it.
fn site_val(row: &Site) -> Val {
    let mut rows = vec![
        ("id", py::s(row.id)),
        ("route_id", py::s(row.route_id)),
        ("endpoints", py::tuple(row.endpoints.iter().map(|e| py::ftuple(e)))),
        ("face_axis", Val::Int(row.face_axis as i64)),
        ("face", Val::Float(row.face)),
        ("outward", py::ftuple(&row.outward)),
        ("tube_od", Val::Float(row.tube_od)),
        ("bore_diameter", Val::Float(row.bore_diameter)),
        ("wing", Val::Float(row.wing)),
        ("source", py::s(row.source)),
        ("source_function", py::s(row.source_function)),
        ("source_segment", Val::Int(row.source_segment)),
        ("install_before", py::tuple(row.install_before.iter().map(|s| py::s(*s)))),
        ("basis", py::s(row.basis)),
    ];
    if let Some(parameter) = row.line_parameter {
        rows.push(("line_parameter", Val::Float(parameter)));
    }
    if let Some(group) = row.group {
        rows.push(("group", py::s(group)));
    }
    py::dict(rows)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("math", rt.import("math")?)?;
    ns.set("_SITES", py::tuple(SITES.iter().map(site_val)))?;
    ns.set("_SHARED_ROOTS", Val::dict(shared_roots().iter().map(|root| (py::s(root.id.clone()), root.val())).collect()))?;
    ns.def(rt, "tube_sites", |_rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(py::tuple(tube_sites().iter().map(TubeSite::val)))
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}

/// Pure coordinates and section parameters; no CAD or assembly imports.
pub fn tube_sites() -> Vec<TubeSite> {
    let roots = shared_roots();
    SITES
        .iter()
        .map(|row| {
            let [first, last] = row.endpoints;
            let parameter = row.line_parameter.unwrap_or(0.5);
            let centre: [f64; 3] = std::array::from_fn(|k| first[k] + (last[k] - first[k]) * parameter);
            let length = num::dist(&first, &last);
            let along: [f64; 3] = std::array::from_fn(|k| (last[k] - first[k]) / length);
            let root_distance = (row.face - centre[row.face_axis]).abs();
            let end_clearances = [length * parameter - 4., length * (1. - parameter) - 4.];
            TubeSite {
                id: row.id.into(),
                route_id: row.route_id.into(),
                host: "enclosure-back-top".into(),
                centre,
                along,
                outward: row.outward,
                root_distance,
                tube_od: row.tube_od,
                bore_diameter: row.bore_diameter,
                wing: row.wing,
                span: 8.,
                print_up: [0., 0., -1.],
                basis: row.basis.into(),
                install_before: row.install_before.iter().map(|s| (*s).to_owned()).collect(),
                group: row.group.map(|id| roots.iter().find(|root| root.id == id).cloned().expect("a shared root")),
                source_parameter: SourceParameter {
                    file: row.source.into(),
                    function: row.source_function.into(),
                    native_segment_index: row.source_segment,
                    line_endpoints_world_mm: row.endpoints,
                    line_parameter: parameter,
                    straight_end_clearance_mm: num::min2(end_clearances[0], end_clearances[1]),
                    straight_end_clearances_mm: end_clearances,
                    host_face_axis: ["X", "Y", "Z"][row.face_axis].into(),
                    host_face_coordinate_mm: row.face,
                },
            }
        })
        .collect()
}
