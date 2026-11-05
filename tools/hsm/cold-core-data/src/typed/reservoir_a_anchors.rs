//! `_reservoir_a_anchors`: reservoir A's fore snap receiver and aft tied seats, in appliance
//! millimetres.

use super::reservoir_a_c2 as snap;
use super::*;
use std::f64::consts::PI;

pub const NAME: &str = "_reservoir_a_anchors";

/// One anchor station as `_SPECIFICATION` states it.
pub struct StationSpec {
    pub id: &'static str,
    pub label: &'static str,
    pub world_y: Option<f64>,
    pub station_length: Option<f64>,
    pub curved_seats: Option<bool>,
    pub seat_lip_below_axis: Option<f64>,
    pub routes_west_to_east: [&'static str; 2],
}

/// `_SPECIFICATION`.
pub struct Spec {
    pub units: &'static str,
    pub assembly_owner: &'static str,
    pub mounting_parent: &'static str,
    pub tube_od: f64,
    pub tube_axis_world: [f64; 3],
    pub lid_face_z: f64,
    pub root_z: f64,
    pub seat_top_z: f64,
    pub seat_radius: f64,
    pub seat_floor_stock: f64,
    pub station_length: f64,
    pub stock_west_of_first_tube: f64,
    pub stock_east_of_last_tube: f64,
    pub tie_slot_width_y: f64,
    pub tie_slot_bottom_z: f64,
    pub tie_slot_floor_stock: f64,
    pub tie_access_inner_offset: f64,
    pub tie_witness_width: f64,
    pub tie_witness_thickness: f64,
    pub tie_witness_outer_bend_radius: f64,
    pub tie_witness_bottom_center_z: f64,
    pub stations: [StationSpec; 2],
}

pub const SPECIFICATION: Spec = Spec {
    units: "mm",
    assembly_owner: "back-bottom",
    mounting_parent: "cold-core top lid",
    tube_od: 6.35,
    tube_axis_world: [0.0, 1.0, 0.0],
    lid_face_z: 253.4,
    root_z: 248.0,
    seat_top_z: 257.0,
    seat_radius: 3.325,
    seat_floor_stock: 3.0,
    station_length: 10.0,
    stock_west_of_first_tube: 6.325,
    stock_east_of_last_tube: 6.325,
    tie_slot_width_y: 3.2,
    tie_slot_bottom_z: 251.6,
    tie_slot_floor_stock: 3.0,
    tie_access_inner_offset: 0.0,
    tie_witness_width: 2.5,
    tie_witness_thickness: 0.8,
    tie_witness_outer_bend_radius: 3.75,
    tie_witness_bottom_center_z: 252.4,
    stations: [
        StationSpec {
            id: "a-pair-fore-anchor",
            label: "Reservoir A fore paired anchor",
            world_y: None,
            station_length: None,
            curved_seats: None,
            seat_lip_below_axis: None,
            routes_west_to_east: ["fluid-16", "fluid-14"],
        },
        StationSpec {
            id: "a-pair-aft-anchor",
            label: "Reservoir A aft paired anchor",
            world_y: Some(390.5),
            station_length: Some(9.2),
            curved_seats: Some(true),
            seat_lip_below_axis: Some(1.2),
            routes_west_to_east: ["fluid-16", "fluid-14"],
        },
    ],
};

fn list3(p: [f64; 3]) -> Val {
    p.to_vec().to_val()
}
/// Nested bounds as the lists of lists Python builds.
fn rows(b: &[[f64; 3]]) -> Val {
    Val::list(b.iter().map(|r| list3(*r)).collect())
}

impl StationSpec {
    fn entries(&self) -> Dict {
        let mut d = Dict::new().with("id", self.id).with("label", self.label);
        if let Some(y) = self.world_y {
            d.set("world_y_mm", y);
        }
        if let Some(length) = self.station_length {
            d.set("station_length_mm", length);
        }
        if let Some(curved) = self.curved_seats {
            d.set("curved_seats", curved);
        }
        if let Some(lip) = self.seat_lip_below_axis {
            d.set("seat_lip_below_axis_mm", lip);
        }
        d.set(
            "routes_west_to_east",
            self.routes_west_to_east.map(String::from).to_vec(),
        );
        d
    }
}

impl Spec {
    /// The dict Python holds, with `stations` as given.
    fn entries(&self, stations: Val) -> Dict {
        Dict::new()
            .with("units", self.units)
            .with("assembly_owner", self.assembly_owner)
            .with("mounting_parent", self.mounting_parent)
            .with("tube_od_mm", self.tube_od)
            .with("tube_axis_world", list3(self.tube_axis_world))
            .with("lid_face_z_mm", self.lid_face_z)
            .with("root_z_mm", self.root_z)
            .with("seat_top_z_mm", self.seat_top_z)
            .with("seat_radius_mm", self.seat_radius)
            .with("seat_floor_stock_mm", self.seat_floor_stock)
            .with("station_length_mm", self.station_length)
            .with("stock_west_of_first_tube_mm", self.stock_west_of_first_tube)
            .with("stock_east_of_last_tube_mm", self.stock_east_of_last_tube)
            .with("tie_slot_width_y_mm", self.tie_slot_width_y)
            .with("tie_slot_bottom_z_mm", self.tie_slot_bottom_z)
            .with("tie_slot_floor_stock_mm", self.tie_slot_floor_stock)
            .with("tie_access_inner_offset_mm", self.tie_access_inner_offset)
            .with("tie_witness_width_mm", self.tie_witness_width)
            .with("tie_witness_thickness_mm", self.tie_witness_thickness)
            .with(
                "tie_witness_outer_bend_radius_mm",
                self.tie_witness_outer_bend_radius,
            )
            .with(
                "tie_witness_bottom_center_z_mm",
                self.tie_witness_bottom_center_z,
            )
            .with("stations", stations)
    }
    /// `_SPECIFICATION`.
    pub fn val(&self) -> Val {
        let stations = self.stations.iter().map(|s| s.entries().val()).collect();
        self.entries(Val::list(stations)).val()
    }
}

/// How a station holds its tubes.
pub enum Closure {
    /// The fore pair: `_reservoir_a_c2`'s integral snap.
    DirectSnap(snap::Specification),
    /// A tied pair, its tube centres where the routes cross the station.
    Tie { tube_centers_world: Vec<[f64; 3]> },
}

pub struct Station {
    pub spec: &'static StationSpec,
    pub closure: Closure,
}

impl Station {
    /// The station's row in `specification()['stations']`.
    pub fn val(&self) -> Result<Val> {
        let mut d = self.spec.entries();
        match &self.closure {
            Closure::DirectSnap(snap) => {
                for (k, v) in snap.val().items()? {
                    d.set(k, v);
                }
            }
            Closure::Tie { tube_centers_world } => {
                d.set("closure", "tie");
                d.set("tube_centers_world_mm", tube_centers_world.clone());
            }
        }
        Ok(d.val())
    }
}

/// `specification()`.
pub struct Specification {
    pub stations: Vec<Station>,
    pub tie_slot_top_z: f64,
    pub tie_access_outer_offset: f64,
}

impl Specification {
    pub fn val(&self) -> Result<Val> {
        let stations = self.stations.iter().map(Station::val).collect::<Result<_>>()?;
        Ok(SPECIFICATION
            .entries(Val::list(stations))
            .with("tie_slot_top_z_mm", self.tie_slot_top_z)
            .with("tie_access_outer_offset_mm", self.tie_access_outer_offset)
            .val())
    }
}

/// `specification()`: the fore station takes the C2 snap's datums, the aft one is tied at
/// the routes' crossings.
pub fn specification(rt: &Runtime) -> Result<Specification> {
    let s = &SPECIFICATION;
    let [fore, aft] = &s.stations;
    let world_y = aft.world_y.context("KeyError: 'world_y_mm'")?;
    let mut centres = vec![];
    for route in aft.routes_west_to_east {
        centres.push(route_station(rt, route, world_y)?.0);
    }
    let stations = vec![
        Station {
            spec: fore,
            closure: Closure::DirectSnap(snap::specification()),
        },
        Station {
            spec: aft,
            closure: Closure::Tie {
                tube_centers_world: centres,
            },
        },
    ];
    let tied: Vec<f64> = stations
        .iter()
        .filter_map(|row| match &row.closure {
            Closure::Tie { tube_centers_world } => Some(tube_centers_world),
            Closure::DirectSnap(_) => None,
        })
        .flatten()
        .map(|point| point[2])
        .collect();
    ensure!(!tied.is_empty(), "min() arg is an empty sequence");
    Ok(Specification {
        stations,
        tie_slot_top_z: fmin(tied) - s.seat_radius - s.seat_floor_stock,
        tie_access_outer_offset: pmax(s.stock_west_of_first_tube, s.stock_east_of_last_tube),
    })
}

/// `{**station}`.
fn spread(station: &Val) -> Result<Dict> {
    let mut d = Dict::new();
    for (k, v) in station.items()? {
        d.set(k, v);
    }
    Ok(d)
}

/// `datums()`: each station's stock, tie slot and access bounds, by station id.
pub fn datums(rt: &Runtime) -> Result<Val> {
    let spec = specification(rt)?;
    let s = &SPECIFICATION;
    let mut result = Dict::new();
    for station in &spec.stations {
        let row_val = station.val()?;
        let mut row = spread(&row_val)?;
        let centres = match &station.closure {
            Closure::DirectSnap(_) => {
                row.set("stock_bounds_mm", row_val.k("body_bounds_mm")?);
                let axis = row_val.k("tube_axis_world")?;
                row.set("tube_axes_world", Val::list(vec![axis.clone(), axis]));
                result.set(station.spec.id, row.val());
                continue;
            }
            Closure::Tie { tube_centers_world } => tube_centers_world,
        };
        ensure!(
            centres.len() == 2,
            "expected 2 values to unpack, got {}",
            centres.len()
        );
        let (first, last) = (centres[0], centres[1]);
        let (x0, x1) = (first[0], last[0]);
        let y = first[1];
        let half = station.spec.station_length.unwrap_or(s.station_length) / 2.0;
        let top = s.seat_top_z;
        let slot_half = s.tie_slot_width_y / 2.0;
        let inner = s.tie_access_inner_offset;
        let east = s.stock_east_of_last_tube;
        let mut west_edge = x0 - s.stock_west_of_first_tube;
        let mut east_edge = x1 + east;
        let bottom = s.tie_slot_bottom_z;
        let mut stock_bounds = [[west_edge, y - half, s.root_z], [east_edge, y + half, top]];
        let mut tie_slot_bounds = [
            [west_edge, y - slot_half, bottom],
            [east_edge, y + slot_half, spec.tie_slot_top_z],
        ];
        let mut access_bounds = [
            [[west_edge, y - slot_half, bottom], [x0 - inner, y + slot_half, top + 0.1]],
            [[x1 + inner, y - slot_half, bottom], [east_edge, y + slot_half, top + 0.1]],
        ];
        let mut curved = None;
        if station.spec.curved_seats == Some(true) {
            let routes = station.spec.routes_west_to_east;
            let mut held = vec![];
            for route in routes {
                held.push(route_station(rt, route, y)?);
            }
            let mut lanes = vec![];
            for route in routes {
                let mut lane = vec![];
                for i in 0..65i64 {
                    lane.push(route_station(
                        rt,
                        route,
                        y - half + (i * 2) as f64 * half / 64.0,
                    )?);
                }
                lanes.push(lane);
            }
            let r = s.seat_radius;
            let edges: Vec<(f64, f64)> = lanes
                .iter()
                .map(|lane| {
                    (
                        fmin(lane.iter().map(|(p, u)| p[0] - r / u[1].abs())),
                        fmax(lane.iter().map(|(p, u)| p[0] + r / u[1].abs())),
                    )
                })
                .collect();
            let lip = station
                .spec
                .seat_lip_below_axis
                .context("KeyError: 'seat_lip_below_axis_mm'")?;
            let tops: Vec<f64> = lanes
                .iter()
                .map(|lane| fmin(lane.iter().map(|(p, _)| p[2])) - lip)
                .collect();
            let (west, east) = (&edges[0], &edges[edges.len() - 1]);
            west_edge = west.0 - 3.0;
            east_edge = east.1 + 3.0;
            let highest = fmax(tops.iter().copied());
            stock_bounds = [[west_edge, y - half, s.root_z], [east_edge, y + half, highest]];
            let reach = s.seat_floor_stock;
            let (top_west, top_east) = (tops[0], tops[tops.len() - 1]);
            let seat_roof = vec![
                (west_edge, top_west),
                (west.1 - reach, top_west),
                (east.0 + reach, top_east),
                (east_edge, top_east),
            ];
            tie_slot_bounds[0][0] = west_edge;
            tie_slot_bounds[1][0] = east_edge;
            for (mouth, xa, xb) in [(0, west_edge, x0), (1, x1, east_edge)] {
                access_bounds[mouth][0][0] = xa;
                access_bounds[mouth][1][0] = xb;
                access_bounds[mouth][1][2] = highest + 0.1;
            }
            curved = Some((held, seat_roof));
        }
        row.set("stock_bounds_mm", rows(&stock_bounds));
        row.set("tie_slot_bounds_mm", rows(&tie_slot_bounds));
        row.set(
            "access_bounds_mm",
            Val::list(access_bounds.iter().map(|m| rows(m)).collect()),
        );
        if let Some((held, seat_roof)) = curved {
            row.set("nominal_tube_centers_world_mm", row_val.k("tube_centers_world_mm")?);
            row.set(
                "tube_centers_world_mm",
                held.iter().map(|(p, _)| *p).collect::<Vec<_>>(),
            );
            row.set(
                "tube_axes_world",
                held.iter().map(|(_, axis)| *axis).collect::<Vec<_>>(),
            );
            row.set("seat_roof_xz_mm", seat_roof);
        }
        result.set(station.spec.id, row.val());
    }
    Ok(result.val())
}

/// `_route_station(identifier, y)`: where reservoir-A route `identifier` crosses world Y `y`,
/// and its direction there. The route specification and its vector arithmetic stay with the
/// `above_core_routes` provider.
pub fn route_station(rt: &Runtime, identifier: &str, y: f64) -> Result<([f64; 3], [f64; 3])> {
    let routes = rt.py("above_core_routes")?;
    let specs = routes.m("reservoir_a_route_specs", vec![])?;
    for segment in specs.k(identifier)?.k("segments")?.list()? {
        let points = segment.k("points_mm")?;
        let (first, last) = (points.i(0)?, points.i(-1)?);
        let (f1, l1) = (first.i(1)?.f()?, last.i(1)?.f()?);
        if !(pmin(f1, l1) - 1e-08 <= y && y <= pmax(f1, l1) + 1e-08) {
            continue;
        }
        if segment.ks("kind")? == "line" {
            if (l1 - f1).abs() < 1e-09 {
                continue;
            }
            let t = (y - f1) / (l1 - f1);
            let along = routes.m("_sub", vec![last.clone(), first.clone()])?;
            let scaled = routes.m("_mul", args![along, t])?;
            let point = routes.m("_add", vec![first.clone(), scaled])?;
            let direction = routes.m("_sub", vec![last, first])?;
            let unit = routes.m("_unit", vec![direction])?;
            return Ok((point.v3()?, unit.v3()?));
        }
        let (center, axis) = (segment.k("center_mm")?, segment.k("axis")?);
        let radial = routes.m("_sub", vec![first.clone(), center.clone()])?;
        let sideways = routes.m("_cross", vec![axis.clone(), radial.clone()])?;
        let point = |angle: f64| -> Result<Val> {
            let along = routes.m("_mul", args![radial, angle.cos()])?;
            let across = routes.m("_mul", args![sideways, angle.sin()])?;
            let offset = routes.m("_add", vec![along, across])?;
            routes.m("_add", vec![center.clone(), offset])
        };
        let (mut lo, mut hi) = (0.0, segment.kf("angle_rad")?);
        let increasing = l1 > f1;
        for _ in 0..48 {
            let mid = (lo + hi) / 2.0;
            if (point(mid)?.i(1)?.f()? < y) == increasing {
                lo = mid;
            } else {
                hi = mid;
            }
        }
        let station = point((lo + hi) / 2.0)?;
        let radius = routes.m("_sub", vec![station.clone(), center.clone()])?;
        let tangent = routes.m("_cross", vec![axis.clone(), radius])?;
        let unit = routes.m("_unit", vec![tangent])?;
        return Ok((station.v3()?, unit.v3()?));
    }
    bail!("{identifier} has no restraint crossing at Y{}", ff(y, "g"))
}

/// `tie_profile(row)`: the tie witness's outline in the station's XZ plane, round the two
/// tubes and back under them.
pub fn tie_profile(rt: &Runtime, first: [f64; 3], last: [f64; 3]) -> Result<Vec<(f64, f64)>> {
    specification(rt)?;
    let s = &SPECIFICATION;
    let (x0, x1, z) = (first[0], last[0], first[2]);
    let radius = s.tie_witness_outer_bend_radius;
    let bottom = s.tie_witness_bottom_center_z;
    let turn = 1.5;
    let mut points = vec![];
    let mut arc = |x: f64, zz: f64, r: f64, start: f64, end: f64| {
        for i in 0..13 {
            let angle = start + (end - start) * i as f64 / 12.0;
            points.push((x + r * angle.cos(), zz + r * angle.sin()));
        }
    };
    let tangent = (last[2] - first[2]).atan2(x1 - x0) + PI / 2.0;
    arc(x0, z, radius, PI, tangent);
    arc(x1, last[2], radius, tangent, 0.0);
    arc(x1 + radius - turn, bottom + turn, turn, 0.0, -PI / 2.0);
    arc(x0 - radius + turn, bottom + turn, turn, -PI / 2.0, -PI);
    Ok(points)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    ns.python(rt, "deepcopy", "copy", "deepcopy")?;
    ns.module(rt, "math", "math")?;
    ns.module(rt, "snap", snap::NAME)?;
    ns.value("_SPECIFICATION", SPECIFICATION.val());
    ns.func(rt, "specification", |rt, _| specification(rt)?.val());
    ns.func(rt, "datums", |rt, _| datums(rt));
    ns.func(rt, "_route_station", |rt, c| {
        let identifier = c.req::<String>(0, "identifier")?;
        let y = c.req(1, "y")?;
        Ok(route_station(rt, &identifier, y)?.to_val())
    });
    ns.func(rt, "tie_profile", |rt, c| {
        let row = c.req::<Val>(0, "row")?;
        let centres = row.k("tube_centers_world_mm")?.list()?;
        ensure!(
            centres.len() == 2,
            "expected 2 values to unpack, got {}",
            centres.len()
        );
        Ok(tie_profile(rt, centres[0].v3()?, centres[1].v3()?)?.to_val())
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
