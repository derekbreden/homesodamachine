//! `_reed_b_outlet`: reservoir B cable's fore side outlet below the shell rim.

use super::cad::Cq;
use super::cold_core_interface as core;
use super::*;

pub const NAME: &str = "_reed_b_outlet";

pub const DEPTH: f64 = 6.0;

/// `datums()`.
pub struct Datums {
    pub axis_xy: [f64; 2],
    pub front_x: f64,
    pub width: f64,
    pub depth: f64,
    pub top_z: f64,
    pub bottom_z: f64,
    pub roof_shoulder_z: f64,
    pub roof_peak_z: f64,
    pub notch_min: [f64; 3],
    pub notch_max: [f64; 3],
}

impl Datums {
    /// The dict `datums()` returns.
    pub fn val(&self) -> Val {
        Dict::new()
            .with("axis_xy_mm", self.axis_xy)
            .with("front_x_mm", self.front_x)
            .with("width_mm", self.width)
            .with("depth_mm", self.depth)
            .with("top_z_mm", self.top_z)
            .with("bottom_z_mm", self.bottom_z)
            .with("roof_shoulder_z_mm", self.roof_shoulder_z)
            .with("roof_peak_z_mm", self.roof_peak_z)
            .with("notch_min_mm", self.notch_min)
            .with("notch_max_mm", self.notch_max)
            .val()
    }
}

/// `datums()`: the notch through the fore wall over reservoir B's reed column.
pub fn datums(rt: &Runtime) -> Result<Datums> {
    let core = core::state(rt)?;
    let b = &core.base;
    let front = -b.outer_shell_x_length / 2.0;
    let axis = -b.reed_column_axis_x;
    let y = b.level_rod_y;
    let half = b.reed_y_half_w;
    let top = b.foam_shell_outer_height;
    let bottom = top - DEPTH;
    let shoulder = top + 0.25;
    let peak = shoulder + 2.0 * half;
    Ok(Datums {
        axis_xy: [axis, y],
        front_x: front,
        width: 2.0 * half,
        depth: DEPTH,
        top_z: top,
        bottom_z: bottom,
        roof_shoulder_z: shoulder,
        roof_peak_z: peak,
        notch_min: [front - 1.0, y - half, bottom],
        notch_max: [axis, y + half, peak],
    })
}

/// `apply(shell)`: the shell with the outlet's gabled opening cut through its fore wall.
pub fn apply(rt: &Runtime, shell: &Val) -> Result<Val> {
    let cq = Cq::new(rt)?;
    let d = datums(rt)?;
    let (lo, hi) = (d.notch_min, d.notch_max);
    let plane = cq.plane(kw![
        "origin" => (lo[0], 0.0, 0.0),
        "xDir" => (0.0, 1.0, 0.0),
        "normal" => (1.0, 0.0, 0.0)
    ])?;
    let shoulder = d.roof_shoulder_z;
    let profile = vec![
        (lo[1], lo[2]),
        (hi[1], lo[2]),
        (hi[1], shoulder),
        (d.axis_xy[1], d.roof_peak_z),
        (lo[1], shoulder),
    ];
    let opening = cq
        .workplane(args![plane], vec![])?
        .m("polyline", args![profile])?
        .m("close", vec![])?
        .m("extrude", args![hi[0] - lo[0]])?
        .m("val", vec![])?;
    shell.m("cut", args![opening])
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    ns.module(rt, "importlib", "importlib")?;
    ns.value("depth", DEPTH);
    ns.func(rt, "datums", |rt, _| Ok(datums(rt)?.val()));
    ns.func(rt, "apply", |rt, c| apply(rt, &c.req::<Val>(0, "shell")?));
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
