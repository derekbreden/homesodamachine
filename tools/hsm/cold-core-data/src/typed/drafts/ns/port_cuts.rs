//! `_port_cuts`: openings through the foam shell (the PRV vent's port and the front wall's two
//! copper feed-throughs) and the two lines that cross the carbonator support ring.

use super::cad::Cq;
use super::cold_core_interface as core;
use super::copper_ports;
use super::support_ring::{self, SLOT_ANGULAR_WIDTH, SLOT_CLOCK, SLOT_COUNT};
use super::*;

pub const NAME: &str = "_port_cuts";

pub const BOTTOM_PORT_DROP: f64 = 11.2;

pub struct State {
    cq: Val,
    fits: Val,
    /// `fits.supported_surface`, as the provider states it.
    supported_surface: Val,
    stated_state: Val,
    pub wall_and_floor_thickness: f64,
    pub carbonator_support_ring_height: f64,
    pub outer_shell_wall: f64,
    pub foam_shell_outer_height: f64,
    pub water_outlet_climb_x: f64,
    pub co2_inlet_y: f64,
    pub co2_lane_x: f64,
    pub lldpe_tube_od: f64,
    pub port_lane_mid_y: f64,
    pub support_ring_radial_width: f64,
    pub carbonator_coil_envelope_radius: f64,
    pub front_face_port_z: f64,
    pub water_outlet_ring_crossing_x: f64,
    pub support_ring_outer_radius: f64,
    pub support_ring_inner_radius: f64,
    pub crossing: Option<[f64; 2]>,
    pub co2_inlet_xyz: [f64; 3],
    pub co2_inlet_lane_xyz: [f64; 3],
    pub co2_bore_to_ring: f64,
    pub co2_crossing: Option<[f64; 2]>,
}

/// `(min(band), max(band)) if band else None`.
fn band_span(band: &[f64]) -> Option<[f64; 2]> {
    if band.is_empty() {
        None
    } else {
        Some([fmin(band.iter().copied()), fmax(band.iter().copied())])
    }
}

/// `ring_crossing_azimuths` against a ring of the given radii.
fn crossing_azimuths(inner: f64, outer: f64, x: f64, tube_radius: f64) -> Option<[f64; 2]> {
    let mut band = vec![];
    for edge in [x - tube_radius, x + tube_radius] {
        for radius in [inner, outer] {
            if edge.abs() >= radius {
                continue;
            }
            let y = -(radius.powf(2.0) - edge.powf(2.0)).sqrt();
            band.push(pymod(degrees(y.atan2(edge)), 360.0));
        }
    }
    band_span(&band)
}

/// `segment_ring_azimuths` against a ring of the given radii.
fn segment_azimuths(
    inner: f64,
    outer: f64,
    a: [f64; 2],
    b: [f64; 2],
    tube_radius: f64,
) -> Option<[f64; 2]> {
    let ([ax, ay], [bx, by]) = (a, b);
    let (dx, dy) = (bx - ax, by - ay);
    let length = hypot(&[dx, dy]);
    if length < 1e-09 {
        return None;
    }
    let (nx, ny) = (-dy / length, dx / length);
    let mut band = vec![];
    for side in [-1.0, 1.0] {
        let (ox, oy) = (ax + nx * side * tube_radius, ay + ny * side * tube_radius);
        for radius in [inner - tube_radius, outer + tube_radius] {
            let qa = dx * dx + dy * dy;
            let qb = 2.0 * (ox * dx + oy * dy);
            let qc = ox * ox + oy * oy - radius * radius;
            let disc = qb * qb - 4.0 * qa * qc;
            if disc < 0.0 {
                continue;
            }
            for t in [
                (-qb - disc.sqrt()) / (2.0 * qa),
                (-qb + disc.sqrt()) / (2.0 * qa),
            ] {
                if 0.0 <= t && t <= 1.0 {
                    band.push(pymod(degrees((oy + t * dy).atan2(ox + t * dx)), 360.0));
                }
            }
        }
    }
    band_span(&band)
}

/// `ring_slot_spans()`: each support-ring slot's azimuth span, in degrees.
pub fn ring_slot_spans() -> Vec<(f64, f64)> {
    let step = 360.0 / SLOT_COUNT as f64;
    (0..SLOT_COUNT)
        .map(|i| {
            let centre = step * (i as f64 + 0.5) + SLOT_CLOCK;
            (centre - SLOT_ANGULAR_WIDTH / 2.0, centre + SLOT_ANGULAR_WIDTH / 2.0)
        })
        .collect()
}

/// Whether one slot holds the whole crossing.
fn held(crossing: Option<[f64; 2]>) -> bool {
    match crossing {
        None => false,
        Some([low, high]) => ring_slot_spans()
            .iter()
            .any(|(lo, hi)| *lo <= low && high <= *hi),
    }
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let cq = rt.py("cadquery")?;
        let fits = rt.py("fits")?;
        let core = core::state(rt)?;
        let b = &core.base;
        let stated_state = rt.pya("_stated_bounds", "state")?;
        support_ring::state(rt)?;
        let supported_surface = fits.a("supported_surface")?;
        let front_face_port_z =
            b.wall_and_floor_thickness + b.carbonator_support_ring_height - BOTTOM_PORT_DROP;
        let water_outlet_ring_crossing_x = core.water_outlet_climb_x;
        let support_ring_outer_radius = b.carbonator_coil_envelope_radius;
        let support_ring_inner_radius = support_ring_outer_radius - b.support_ring_radial_width;
        let (inner, outer) = (support_ring_inner_radius, support_ring_outer_radius);
        let crossing = crossing_azimuths(
            inner,
            outer,
            water_outlet_ring_crossing_x,
            core.lldpe_tube_od / 2.0,
        );
        let spans = || fv(&ring_slot_spans().to_val(), "");
        let x = ff(water_outlet_ring_crossing_x, "g");
        let detail = match crossing {
            None => format!(
                "the carbonated-water outlet at x {x} passes clear outboard of the carbonator \
                 support ring and crosses no azimuth of it — the slot it is struck against is \
                 not the ring this line meets"
            ),
            Some([low, high]) => format!(
                "the carbonated-water outlet crosses the carbonator support ring at x {x} over \
                 azimuths {}°..{}°, which no slot of {} holds — the line would have to be bored \
                 through a bearing segment",
                ff(low, ".1f"),
                ff(high, ".1f"),
                spans()?
            ),
        };
        stated_state.c(args![
            "water-outlet-slot",
            "The carbonated-water outlet crosses the support ring in one slot",
            "one slot holding the whole crossing",
            held(crossing),
            detail
        ])?;
        let co2_inlet_xyz = [0.0, b.co2_inlet_y, front_face_port_z];
        let co2_inlet_lane_xyz = [core.co2_lane_x, b.port_lane_mid_y + 2.5, front_face_port_z];
        let co2_bore_to_ring = b.port_lane_mid_y.abs() - support_ring_outer_radius;
        let co2_crossing = segment_azimuths(
            inner,
            outer,
            [co2_inlet_lane_xyz[0], co2_inlet_lane_xyz[1]],
            [co2_inlet_xyz[0], co2_inlet_xyz[1]],
            core.lldpe_tube_od / 2.0,
        );
        let x = ff(co2_inlet_lane_xyz[0], "g");
        let detail = match co2_crossing {
            None => format!(
                "the CO2 reach in from x {x} passes clear of the ring this is struck against"
            ),
            Some([low, high]) => format!(
                "the CO2 reach in from x {x} crosses the carbonator support ring over azimuths \
                 {}°..{}°, which no slot of {} holds — the line would have to be bored through \
                 a bearing segment that carries the carbonator",
                ff(low, ".1f"),
                ff(high, ".1f"),
                spans()?
            ),
        };
        stated_state.c(args![
            "co2-inlet-slot",
            "The CO2 reach in crosses the support ring in one slot",
            "one slot holding the whole crossing",
            held(co2_crossing),
            detail
        ])?;
        Ok(Self {
            cq,
            fits,
            supported_surface,
            stated_state,
            wall_and_floor_thickness: b.wall_and_floor_thickness,
            carbonator_support_ring_height: b.carbonator_support_ring_height,
            outer_shell_wall: b.outer_shell_wall,
            foam_shell_outer_height: b.foam_shell_outer_height,
            water_outlet_climb_x: core.water_outlet_climb_x,
            co2_inlet_y: b.co2_inlet_y,
            co2_lane_x: core.co2_lane_x,
            lldpe_tube_od: core.lldpe_tube_od,
            port_lane_mid_y: b.port_lane_mid_y,
            support_ring_radial_width: b.support_ring_radial_width,
            carbonator_coil_envelope_radius: b.carbonator_coil_envelope_radius,
            front_face_port_z,
            water_outlet_ring_crossing_x,
            support_ring_outer_radius,
            support_ring_inner_radius,
            crossing,
            co2_inlet_xyz,
            co2_inlet_lane_xyz,
            co2_bore_to_ring,
            co2_crossing,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `ring_crossing_azimuths(x, tube_radius)`: the support-ring azimuths a straight line at
/// `x` covers, or none when it passes clear.
pub fn ring_crossing_azimuths(rt: &Runtime, x: f64, tube_radius: f64) -> Result<Option<[f64; 2]>> {
    let s = state(rt)?;
    Ok(crossing_azimuths(
        s.support_ring_inner_radius,
        s.support_ring_outer_radius,
        x,
        tube_radius,
    ))
}

/// `segment_ring_azimuths(a, b, tube_radius)`: the support-ring azimuths the plan segment
/// a→b sweeps with its tube, or none.
pub fn segment_ring_azimuths(
    rt: &Runtime,
    a: [f64; 2],
    b: [f64; 2],
    tube_radius: f64,
) -> Result<Option<[f64; 2]>> {
    let s = state(rt)?;
    Ok(segment_azimuths(
        s.support_ring_inner_radius,
        s.support_ring_outer_radius,
        a,
        b,
        tube_radius,
    ))
}

/// `cut_prv_vent_port(foam_shell)`: the PRV vent's corridor, and the same lifted by the
/// supported-surface allowance, cut from the shell.
pub fn cut_prv_vent_port(rt: &Runtime, foam_shell: &Val) -> Result<Val> {
    let s = state(rt)?;
    // via namespace: _internal_routes
    let corridor = rt
        .import_module("_internal_routes")?
        .a("route_corridor")?
        .c(args!["prv-vent"])?;
    let once = foam_shell.m("cut", args![corridor])?;
    let lifted = corridor.m(
        "translate",
        args![(0i64, 0i64, s.supported_surface.clone())],
    )?;
    once.m("cut", args![lifted])
}

/// `cut_copper_ports(foam_shell)`: the two copper feed-throughs bored through the front wall.
pub fn cut_copper_ports(rt: &Runtime, foam_shell: &Val) -> Result<Val> {
    let s = state(rt)?;
    let cq = Cq::new(rt)?;
    let mut foam_shell = foam_shell.clone();
    for ([x, y, z], _axis) in copper_ports::stations(rt)?.values() {
        let bore = cq.cylinder(
            copper_ports::HOLE_RADIUS,
            s.outer_shell_wall + 4.0,
            [x - 2.0, *y, *z],
            [1.0, 0.0, 0.0],
        )?;
        foam_shell = foam_shell.m("cut", args![bore])?;
    }
    Ok(foam_shell)
}

/// `a[:2]` of a point Python passes.
fn plan(c: &mut Call, index: usize, name: &str) -> Result<[f64; 2]> {
    let point: Vec<f64> = c.req(index, name)?;
    ensure!(point.len() >= 2, "not enough values to unpack (expected 2, got {})", point.len());
    Ok([point[0], point[1]])
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "math", "math")?;
    ns.value("cq", s.cq.clone());
    ns.value("fits", s.fits.clone());
    ns.value("wall_and_floor_thickness", s.wall_and_floor_thickness);
    ns.value("carbonator_support_ring_height", s.carbonator_support_ring_height);
    ns.value("outer_shell_wall", s.outer_shell_wall);
    ns.value("foam_shell_outer_height", s.foam_shell_outer_height);
    ns.value("water_outlet_climb_x", s.water_outlet_climb_x);
    ns.value("co2_inlet_y", s.co2_inlet_y);
    ns.value("co2_lane_x", s.co2_lane_x);
    ns.value("lldpe_tube_od", s.lldpe_tube_od);
    ns.value("port_lane_mid_y", s.port_lane_mid_y);
    ns.value("support_ring_radial_width", s.support_ring_radial_width);
    ns.value(
        "carbonator_coil_envelope_radius",
        s.carbonator_coil_envelope_radius,
    );
    ns.func(rt, "make_box", |rt, c| {
        let x: Vec<f64> = c.req(0, "x_range")?;
        let y: Vec<f64> = c.req(1, "y_range")?;
        let z: Vec<f64> = c.req(2, "z_range")?;
        core::make_box(rt, &x, &y, &z)
    });
    ns.value("state", s.stated_state.clone());
    ns.value("slot_angular_width", SLOT_ANGULAR_WIDTH);
    ns.value("slot_clock", SLOT_CLOCK);
    ns.value("slot_count", SLOT_COUNT);
    ns.value("bottom_port_drop", BOTTOM_PORT_DROP);
    ns.value("front_face_port_z", s.front_face_port_z);
    ns.value("water_outlet_ring_crossing_x", s.water_outlet_ring_crossing_x);
    ns.value("support_ring_outer_radius", s.support_ring_outer_radius);
    ns.value("support_ring_inner_radius", s.support_ring_inner_radius);
    ns.func(rt, "ring_crossing_azimuths", |rt, c| {
        let x = c.req(0, "x")?;
        let tube_radius = c.req(1, "tube_radius")?;
        Ok(ring_crossing_azimuths(rt, x, tube_radius)?.to_val())
    });
    ns.func(rt, "segment_ring_azimuths", |rt, c| {
        let a = plan(c, 0, "a")?;
        let b = plan(c, 1, "b")?;
        let tube_radius = c.req(2, "tube_radius")?;
        Ok(segment_ring_azimuths(rt, a, b, tube_radius)?.to_val())
    });
    ns.func(rt, "ring_slot_spans", |_, _| Ok(ring_slot_spans().to_val()));
    ns.value("_crossing", s.crossing);
    ns.value("co2_inlet_xyz", s.co2_inlet_xyz);
    ns.value("co2_inlet_lane_xyz", s.co2_inlet_lane_xyz);
    ns.value("co2_bore_to_ring", s.co2_bore_to_ring);
    ns.value("_co2_crossing", s.co2_crossing);
    ns.func(rt, "cut_prv_vent_port", |rt, c| {
        cut_prv_vent_port(rt, &c.req::<Val>(0, "foam_shell")?)
    });
    ns.func(rt, "cut_copper_ports", |rt, c| {
        cut_copper_ports(rt, &c.req::<Val>(0, "foam_shell")?)
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
