//! `_copper_ports`: the evaporator copper feed-throughs in the shell's native frame.

use super::cold_core_interface as core;
use super::*;

pub const NAME: &str = "_copper_ports";

pub const COPPER_OUTER_DIAMETER: f64 = 6.35;
pub const HOLE_RADIUS: f64 = 3.75;
/// The refrigeration base's two entries set these axes independently of wall stock.
pub const EVAP_CROSS_Z: f64 = 28.425;

/// One feed-through: its axis point and outward direction.
pub type Station = ([f64; 3], [f64; 3]);

pub struct State {
    pub front_wall_x: f64,
    pub port_lane_mid_y: f64,
    pub west_lane_mid_y: f64,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let core = core::state(rt)?;
        let b = &core.base;
        Ok(Self {
            front_wall_x: b.front_wall_x,
            port_lane_mid_y: b.port_lane_mid_y,
            west_lane_mid_y: b.west_lane_mid_y,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `stations()`: name -> (axis point, outward direction), at the retained copper datum.
pub fn stations(rt: &Runtime) -> Result<OMap<Station>> {
    let s = state(rt)?;
    let mut out = OMap::new();
    out.set(
        "evap-inlet",
        ([s.front_wall_x, s.port_lane_mid_y, EVAP_CROSS_Z], [-1.0, 0.0, 0.0]),
    );
    out.set(
        "evap-outlet",
        ([s.front_wall_x, s.west_lane_mid_y, EVAP_CROSS_Z], [-1.0, 0.0, 0.0]),
    );
    Ok(out)
}

/// `station(name)`.
pub fn station(rt: &Runtime, name: &str) -> Result<Station> {
    Ok(*stations(rt)?.at(name)?)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("front_wall_x", s.front_wall_x);
    ns.value("port_lane_mid_y", s.port_lane_mid_y);
    ns.value("west_lane_mid_y", s.west_lane_mid_y);
    ns.value("copper_outer_diameter", COPPER_OUTER_DIAMETER);
    ns.value("hole_radius", HOLE_RADIUS);
    ns.value("evap_cross_z", EVAP_CROSS_Z);
    ns.func(rt, "stations", |rt, _| Ok(stations(rt)?.to_val()));
    ns.func(rt, "station", |rt, c| {
        Ok(station(rt, &c.req::<String>(0, "name")?)?.to_val())
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
