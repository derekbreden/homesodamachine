//! `_support_ring`: the annular ring at the bottom of the foam shell's central zone that
//! holds the carbonator up by its outer rim, with its angular slots.

use super::cold_core_interface as core;
use super::*;

pub const NAME: &str = "_support_ring";

pub const SLOT_COUNT: i64 = 4;
pub const SLOT_ANGULAR_WIDTH: f64 = 30.0;
/// The slots stand between the diagonals and are clocked off them.
pub const SLOT_CLOCK: f64 = -8.0;
/// Slot overruns each ring face radially.
pub const SLOT_RADIAL_MARGIN: f64 = 1.0;

pub struct State {
    cq: Val,
    xz_plane_y_down: Val,
    pub wall_and_floor_thickness: f64,
    pub carbonator_coil_envelope_radius: f64,
    pub carbonator_support_ring_height: f64,
    pub support_ring_radial_width: f64,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let cq = rt.py("cadquery")?;
        let core = core::state(rt)?;
        let b = &core.base;
        let xz_plane_y_down = rt.pya("world_workplane", "xz_plane_y_down")?;
        Ok(Self {
            cq,
            xz_plane_y_down,
            wall_and_floor_thickness: b.wall_and_floor_thickness,
            carbonator_coil_envelope_radius: b.carbonator_coil_envelope_radius,
            carbonator_support_ring_height: b.carbonator_support_ring_height,
            support_ring_radial_width: b.support_ring_radial_width,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `revolve_rect(r_range, z_range, angle=360)`: a rectangular (r, z) profile on the XZ plane,
/// revolved `angle` degrees about +Z from the +X axis.
pub fn revolve_rect(rt: &Runtime, r_range: &[f64], z_range: &[f64], angle: Num) -> Result<Val> {
    let s = state(rt)?;
    let (r_min, r_max) = (fmin(r_range.iter().copied()), fmax(r_range.iter().copied()));
    let (z_min, z_max) = (fmin(z_range.iter().copied()), fmax(z_range.iter().copied()));
    s.cq.a("Workplane")?
        .c(args![s.xz_plane_y_down])?
        .m("moveTo", args![r_min, z_min])?
        .m("lineTo", args![r_max, z_min])?
        .m("lineTo", args![r_max, z_max])?
        .m("lineTo", args![r_min, z_max])?
        .m("lineTo", args![r_min, z_min])?
        .m("wire", vec![])?
        .m("revolve", args![angle])
}

/// `build_carbonator_support_ring()`: the ring with its equal-spaced slots cut through.
pub fn build_carbonator_support_ring(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let r_outer = s.carbonator_coil_envelope_radius;
    let r_inner = r_outer - s.support_ring_radial_width;
    let z_bottom = s.wall_and_floor_thickness;
    let z_top = z_bottom + s.carbonator_support_ring_height;
    let ring_r_range = [r_inner, r_outer];
    let ring_z_range = [z_bottom, z_top];
    let slot_r_range = [r_inner - SLOT_RADIAL_MARGIN, r_outer + SLOT_RADIAL_MARGIN];
    let mut ring = revolve_rect(rt, &ring_r_range, &ring_z_range, Num::I(360))?;
    let slot_spacing_angle = 360.0 / SLOT_COUNT as f64;
    let slot_template = revolve_rect(rt, &slot_r_range, &ring_z_range, Num::F(SLOT_ANGULAR_WIDTH))?;
    for i in 0..SLOT_COUNT {
        let slot_center_angle = slot_spacing_angle * (i as f64 + 0.5) + SLOT_CLOCK;
        let slot_start_angle = slot_center_angle - SLOT_ANGULAR_WIDTH / 2.0;
        let slot = slot_template.m(
            "rotate",
            args![(0i64, 0i64, 0i64), (0i64, 0i64, 1i64), slot_start_angle],
        )?;
        ring = ring.m("cut", args![slot])?;
    }
    Ok(ring)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("cq", s.cq.clone());
    ns.value("xz_plane_y_down", s.xz_plane_y_down.clone());
    ns.value("wall_and_floor_thickness", s.wall_and_floor_thickness);
    ns.value("carbonator_coil_envelope_radius", s.carbonator_coil_envelope_radius);
    ns.value("carbonator_support_ring_height", s.carbonator_support_ring_height);
    ns.value("support_ring_radial_width", s.support_ring_radial_width);
    ns.value("slot_count", SLOT_COUNT);
    ns.value("slot_angular_width", SLOT_ANGULAR_WIDTH);
    ns.value("slot_clock", SLOT_CLOCK);
    ns.value("slot_radial_margin", SLOT_RADIAL_MARGIN);
    ns.func(rt, "revolve_rect", |rt, c| {
        let r_range: Vec<f64> = c.req(0, "r_range")?;
        let z_range: Vec<f64> = c.req(1, "z_range")?;
        let angle = c.opt(2, "angle", Num::I(360))?;
        revolve_rect(rt, &r_range, &z_range, angle)
    });
    ns.func(rt, "build_carbonator_support_ring", |rt, _| {
        build_carbonator_support_ring(rt)
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
