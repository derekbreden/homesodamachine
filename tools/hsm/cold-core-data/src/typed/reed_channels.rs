//! `_reed_channels`: the reed-and-cable channel system for level sensing, built into the foam
//! shell on the outer face of each bag-pocket far ±X wall.

use super::cad::Cq;
use super::cold_core_interface as core;
use super::*;

pub const NAME: &str = "_reed_channels";

pub const REEDS_PER_RESERVOIR: i64 = 4;
/// The cap conduits a reed cable leaves by, each with the side of the reservoir it serves.
pub const REED_CABLE_CONDUITS: [(&str, i64); 1] = [("reed-cable-a", 1)];

/// One reed-cable conduit's shared mouth with its reservoir's cavity.
struct Mouth {
    side: i64,
    x: f64,
    y: f64,
    cav_x: [f64; 2],
    mouth_x: f64,
    mouth_y: f64,
}

pub struct State {
    pub wall_and_floor_thickness: f64,
    pub wall_thickness: f64,
    pub reed_channel_inner_x: f64,
    pub bag_pocket_far_inner_x: f64,
    pub foam_shell_outer_height: f64,
    pub foam_shell_rim_z: f64,
    pub bag_pocket_outermost_x: f64,
    pub lldpe_tube_od: f64,
    pub port_hole_radius: f64,
    pub reed_x_depth: f64,
    pub reed_y_half_w: f64,
    pub level_rod_y: f64,
    bound: Val,
    pub w: f64,
    pub reed_y_center: f64,
    pub reed_cavity_z_range: [f64; 2],
    /// `(0, foam_shell_rim_z)`: the floor is the int the source writes.
    pub reed_envelope_z_range: (i64, f64),
    pub reed_cavity_y_range: [f64; 2],
    pub reed_envelope_y_range: [f64; 2],
    pub reed_line_clearance: f64,
    reed_clear: Val,
    /// `_name` as the two module-level loops leave it.
    last_name: Option<String>,
    /// `_room`, `_what` of the last conduit the clearance loop measured.
    last_room: Option<(f64, String)>,
    pub reed_cable_mouth_min: f64,
    reed_cable_over: Val,
    last_mouth: Option<Mouth>,
}

/// `sorted((a, b))`.
fn sorted2(a: f64, b: f64) -> [f64; 2] {
    if b < a { [b, a] } else { [a, b] }
}

/// `'AB'[side < 0]`.
fn reservoir_letter(side: f64) -> &'static str {
    if side < 0.0 { "B" } else { "A" }
}

impl State {
    /// `reed_channel_plan_room(x, y)`: how far a plan point stands off the nearer reed channel
    /// envelope, and which channel that is.
    fn plan_room(&self, x: f64, y: f64) -> (f64, String) {
        let mut room: Vec<(f64, String)> = vec![];
        for s in [1i64, -1] {
            let side = s as f64;
            let env_x = sorted2(
                side * self.reed_channel_inner_x,
                side * (self.reed_channel_inner_x + self.reed_x_depth + self.w),
            );
            let dx = pmax(env_x[0] - x, x - env_x[1]);
            let dy = pmax(
                self.reed_envelope_y_range[0] - y,
                y - self.reed_envelope_y_range[1],
            );
            room.push((
                pmax(dx, dy),
                format!("reservoir {}'s reed channel", reservoir_letter(side)),
            ));
        }
        least(room)
    }
}

/// `min(rows)` over `(mm, what)` pairs, as Python compares tuples.
fn least(rows: Vec<(f64, String)>) -> (f64, String) {
    let mut it = rows.into_iter();
    let mut best = it.next().expect("two reed channels");
    for row in it {
        if row.0 < best.0 || (row.0 == best.0 && row.1 < best.1) {
            best = row;
        }
    }
    best
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let core = core::state(rt)?;
        let b = &core.base;
        let bound = rt.pya("_stated_bounds", "bound")?;
        let w = b.wall_thickness;
        let reed_y_center = b.level_rod_y;
        let reed_cavity_y_range = [reed_y_center - b.reed_y_half_w, reed_y_center + b.reed_y_half_w];
        let reed_envelope_y_range = [reed_cavity_y_range[0] - w, reed_cavity_y_range[1] + w];
        let reed_line_clearance = core.lldpe_tube_od / 2.0;
        let mut s = Self {
            wall_and_floor_thickness: b.wall_and_floor_thickness,
            wall_thickness: b.wall_thickness,
            reed_channel_inner_x: b.reed_channel_inner_x,
            bag_pocket_far_inner_x: b.bag_pocket_far_inner_x,
            foam_shell_outer_height: b.foam_shell_outer_height,
            foam_shell_rim_z: b.foam_shell_rim_z,
            bag_pocket_outermost_x: b.bag_pocket_outermost_x,
            lldpe_tube_od: core.lldpe_tube_od,
            port_hole_radius: b.port_hole_radius,
            reed_x_depth: b.reed_x_depth,
            reed_y_half_w: b.reed_y_half_w,
            level_rod_y: b.level_rod_y,
            bound,
            w,
            reed_y_center,
            reed_cavity_z_range: [b.wall_and_floor_thickness, b.foam_shell_rim_z],
            reed_envelope_z_range: (0, b.foam_shell_rim_z),
            reed_cavity_y_range,
            reed_envelope_y_range,
            reed_line_clearance,
            reed_clear: Val::None,
            last_name: None,
            last_room: None,
            reed_cable_mouth_min: b.port_hole_radius,
            reed_cable_over: Val::None,
            last_mouth: None,
        };
        s.reed_clear = s.bound.c(args![
            "reed-channel-clear",
            "Every conduit's line falls clear of both reed channels",
            format!("{} mm off the nearer channel", ff(reed_line_clearance, "g"))
        ])?;
        for name in core.cap_conduits.keys() {
            s.last_name = Some(name.to_owned());
            if REED_CABLE_CONDUITS.iter().any(|(n, _)| *n == name) {
                continue;
            }
            let [fx, fy] = core.cap_conduit_floor_xy(name)?;
            let (room, what) = s.plan_room(-fx, -fy);
            s.reed_clear.c(args![
                room >= reed_line_clearance - 1e-09,
                format!(
                    "cap conduit {name}: the line coming down it stands {} mm off {what}, inside the {} mm a ⌀{} tube's own section takes — a line over a reed cavity is a void meeting a void and collides with nothing",
                    ff(room, ".3f"),
                    ff(reed_line_clearance, "g"),
                    ff(s.lldpe_tube_od, "g")
                )
            ])?;
            s.last_room = Some((room, what));
        }
        let mouth_min = s.reed_cable_mouth_min;
        s.reed_cable_over = s.bound.c(args![
            "reed-cable-conduit-stands-over-its-channel",
            "Every reed-cable conduit opens on the channel its own cable climbs",
            format!("{} mm of shared mouth on each axis", ff(mouth_min, "g"))
        ])?;
        let mut cables = REED_CABLE_CONDUITS.to_vec();
        cables.sort();
        for (name, side) in cables {
            s.last_name = Some(name.to_owned());
            let letter = reservoir_letter(side as f64);
            if core.cap_conduits.get(name).is_none() {
                bail!(
                    "`REED_CABLE_CONDUITS` names {} as the bore reservoir {letter}'s cable leaves by, and the cap carries no conduit by that name — the exemption above is what is still holding it out of `reed-channel-clear`.",
                    Val::Str(name.into()).repr()?
                );
            }
            let [fx, fy] = core.cap_conduit_floor_xy(name)?;
            let (x, y) = (-fx, -fy);
            let sf = side as f64;
            let cav_x = sorted2(
                sf * s.reed_channel_inner_x,
                sf * (s.reed_channel_inner_x + s.reed_x_depth),
            );
            let cav_y = s.reed_cavity_y_range;
            let radius = s.port_hole_radius;
            let mouth_x = pmin(cav_x[1], x + radius) - pmax(cav_x[0], x - radius);
            let mouth_y = pmin(cav_y[1], y + radius) - pmax(cav_y[0], y - radius);
            s.reed_cable_over.c(args![
                pmin(mouth_x, mouth_y) >= mouth_min - 1e-09,
                format!(
                    "reed-cable conduit {name}: its bore at ({}, {}) and reservoir {letter}'s cavity share a mouth {} \u{d7} {} mm — the cable comes up the cavity and leaves by this bore, and what the two do not share is solid shell over the channel",
                    ff(x, ".3f"),
                    ff(y, ".3f"),
                    ff(mouth_x, ".3f"),
                    ff(mouth_y, ".3f")
                )
            ])?;
            s.last_mouth = Some(Mouth {
                side,
                x,
                y,
                cav_x,
                mouth_x,
                mouth_y,
            });
        }
        Ok(s)
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `reed_channel_plan_room(x, y)`: `(mm off the nearer reed channel, which channel)`.
pub fn reed_channel_plan_room(rt: &Runtime, x: f64, y: f64) -> Result<(f64, String)> {
    Ok(state(rt)?.plan_room(x, y))
}

/// `build_reed_channels(side)`: one side's reed channel envelope with its cavity hollowed and
/// the upper back filled to the rim.
pub fn build_reed_channels(rt: &Runtime, side: f64) -> Result<Val> {
    let st = state(rt)?;
    let s = side;
    let bag_x = s * st.reed_channel_inner_x;
    let reed_envelope_x_range = [bag_x, bag_x + s * (st.reed_x_depth + st.w)];
    let reed_cavity_x_range = [bag_x, bag_x + s * st.reed_x_depth];
    let (floor, rim) = st.reed_envelope_z_range;
    let reed_envelope = core::make_box(
        rt,
        &reed_envelope_x_range,
        &st.reed_envelope_y_range,
        &[floor as f64, rim],
    )?;
    let reed_cavity = core::make_box(
        rt,
        &reed_cavity_x_range,
        &st.reed_cavity_y_range,
        &st.reed_cavity_z_range,
    )?;
    let upper_back = core::make_box(
        rt,
        &[s * st.bag_pocket_far_inner_x, s * st.reed_channel_inner_x],
        &st.reed_envelope_y_range,
        &[st.foam_shell_outer_height, st.foam_shell_rim_z],
    )?;
    reed_envelope
        .m("cut", args![reed_cavity])?
        .m("union", args![upper_back])
}

/// `cut_reed_channel_openings(foam_shell)`: both far walls opened onto their reed cavities,
/// each opening gabled over its top.
pub fn cut_reed_channel_openings(rt: &Runtime, foam_shell: &Val) -> Result<Val> {
    let st = state(rt)?;
    let cq = Cq::new(rt)?;
    let mut foam_shell = foam_shell.clone();
    for s in [1.0, -1.0] {
        let wall_x_outer = s * st.bag_pocket_outermost_x;
        let wall_x_inner = s * st.bag_pocket_far_inner_x;
        let reed_opening = core::make_box(
            rt,
            &[wall_x_inner, wall_x_outer],
            &st.reed_cavity_y_range,
            &[st.wall_and_floor_thickness, st.foam_shell_outer_height],
        )?;
        foam_shell = foam_shell.m("cut", args![reed_opening])?;
        let rise = 2.0 * st.reed_y_half_w;
        let z = st.foam_shell_outer_height;
        let [x0, x1] = sorted2(wall_x_inner, wall_x_outer);
        let [y0, y1] = st.reed_cavity_y_range;
        let plane = cq.plane(kw![
            "origin" => (x0, 0.0, 0.0),
            "xDir" => (0.0, 1.0, 0.0),
            "normal" => (1.0, 0.0, 0.0)
        ])?;
        let roof = cq
            .workplane(args![plane], vec![])?
            .m(
                "polyline",
                args![vec![(y0, z), (y1, z), (st.reed_y_center, z + rise)]],
            )?
            .m("close", vec![])?
            .m("extrude", args![x1 - x0])?
            .m("val", vec![])?;
        foam_shell = foam_shell.m("cut", args![roof])?;
    }
    Ok(foam_shell)
}

/// `REED_CABLE_CONDUITS` as the dict Python reads.
fn reed_cable_conduits_val() -> Val {
    let mut d = Dict::new();
    for (name, side) in REED_CABLE_CONDUITS {
        d.set(name, side);
    }
    d.val()
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    let core = core::state(rt)?;
    ns.value("wall_and_floor_thickness", s.wall_and_floor_thickness);
    ns.value("wall_thickness", s.wall_thickness);
    ns.value("reed_channel_inner_x", s.reed_channel_inner_x);
    ns.value("bag_pocket_far_inner_x", s.bag_pocket_far_inner_x);
    ns.value("foam_shell_outer_height", s.foam_shell_outer_height);
    ns.value("foam_shell_rim_z", s.foam_shell_rim_z);
    ns.value("bag_pocket_outermost_x", s.bag_pocket_outermost_x);
    ns.value("cap_conduits", core.cap_conduits.to_val());
    ns.value("cap_conduit_floor_xy", core.cap_conduit_floor_xy.to_val());
    ns.func(rt, "cap_conduit_shell_xy", |rt, c| {
        Ok(core::state(rt)?
            .cap_conduit_shell_xy(&c.req::<String>(0, "name")?)?
            .to_val())
    });
    ns.value("lldpe_tube_od", s.lldpe_tube_od);
    ns.value("port_hole_radius", s.port_hole_radius);
    ns.value("reed_x_depth", s.reed_x_depth);
    ns.value("reed_y_half_w", s.reed_y_half_w);
    ns.value("level_rod_y", s.level_rod_y);
    ns.func(rt, "make_box", |rt, c| {
        let x: Vec<f64> = c.req(0, "x_range")?;
        let y: Vec<f64> = c.req(1, "y_range")?;
        let z: Vec<f64> = c.req(2, "z_range")?;
        core::make_box(rt, &x, &y, &z)
    });
    ns.value("bound", s.bound.clone());
    ns.value("w", s.w);
    ns.value("reeds_per_reservoir", REEDS_PER_RESERVOIR);
    ns.value("reed_y_center", s.reed_y_center);
    ns.value("reed_cavity_z_range", s.reed_cavity_z_range);
    ns.value("reed_envelope_z_range", s.reed_envelope_z_range);
    ns.value("reed_cavity_y_range", s.reed_cavity_y_range);
    ns.value("reed_envelope_y_range", s.reed_envelope_y_range);
    ns.value("reed_line_clearance", s.reed_line_clearance);
    ns.value("REED_CABLE_CONDUITS", reed_cable_conduits_val());
    ns.func(rt, "reed_channel_plan_room", |rt, c| {
        let (x, y) = (c.req(0, "x")?, c.req(1, "y")?);
        Ok(reed_channel_plan_room(rt, x, y)?.to_val())
    });
    ns.value("_reed_clear", s.reed_clear.clone());
    if let Some(name) = &s.last_name {
        ns.value("_name", name.as_str());
    }
    if let Some((room, what)) = &s.last_room {
        ns.value("_room", *room);
        ns.value("_what", what.as_str());
    }
    ns.value("reed_cable_mouth_min", s.reed_cable_mouth_min);
    ns.value("_reed_cable_over", s.reed_cable_over.clone());
    if let Some(m) = &s.last_mouth {
        ns.value("_side", m.side);
        ns.value("_x", m.x);
        ns.value("_y", m.y);
        ns.value("_cav_x", m.cav_x.to_vec());
        ns.value("_cav_y", s.reed_cavity_y_range);
        ns.value("_mouth_x", m.mouth_x);
        ns.value("_mouth_y", m.mouth_y);
    }
    ns.func(rt, "build_reed_channels", |rt, c| {
        build_reed_channels(rt, c.req(0, "side")?)
    });
    ns.func(rt, "cut_reed_channel_openings", |rt, c| {
        cut_reed_channel_openings(rt, &c.req::<Val>(0, "foam_shell")?)
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
