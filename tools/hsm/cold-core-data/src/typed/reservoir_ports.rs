//! `_reservoir_ports`: matched flush TPU seats and independent reservoir air-tube datums, in
//! mm. Port XY belongs to the cold-core shell frame.

use super::cad::Cq;
use super::*;

pub const NAME: &str = "_reservoir_ports";

pub const PLATE_THICKNESS: f64 = 4.0;
pub const AIR_TUBE_OD: f64 = 4.0;
pub const AIR_TUBE_ID: f64 = 2.5;
pub const AIR_TUBE_ABOVE_CASING: f64 = 6.0;
pub const AIR_TUBE_BELOW_LID: f64 = 1.0;
pub const AIR_PASSAGE_DIAMETER: f64 = 5.2;
pub const AIR_PASSAGE_WALL: f64 = 3.0;

/// A spool grommet's specification.
#[derive(Clone, Copy, Debug)]
pub struct Grip {
    pub waist_d: f64,
    pub flare_d: f64,
    pub bore_d: f64,
    pub lead_d: f64,
    pub lead_h: f64,
}

impl Grip {
    /// The dict Python holds.
    pub fn val(&self) -> Val {
        Dict::new()
            .with("waist_d", self.waist_d)
            .with("flare_d", self.flare_d)
            .with("bore_d", self.bore_d)
            .with("lead_d", self.lead_d)
            .with("lead_h", self.lead_h)
            .val()
    }
    /// A specification dict as Python passes it.
    pub fn of(v: &Val) -> Result<Self> {
        Ok(Self {
            waist_d: v.kf("waist_d")?,
            flare_d: v.kf("flare_d")?,
            bore_d: v.kf("bore_d")?,
            lead_d: v.kf("lead_d")?,
            lead_h: v.kf("lead_h")?,
        })
    }
}

pub const LIQUID_GRIP: Grip = Grip {
    waist_d: 9.0,
    flare_d: 11.0,
    bore_d: 6.2,
    lead_d: 7.0,
    lead_h: 0.4,
};
pub const AIR_GRIP: Grip = Grip {
    waist_d: 6.0,
    flare_d: 8.0,
    bore_d: 3.9,
    lead_d: 4.5,
    lead_h: 0.3,
};

/// `air_position`, keyed by reservoir side.
pub const AIR_POSITION: [(i64, [f64; 2]); 2] = [(1, [120.0, -26.0]), (-1, [-109.0, -32.5])];

/// `air_position[side]`.
pub fn air_position(side: i64) -> Result<[f64; 2]> {
    AIR_POSITION
        .iter()
        .find(|(s, _)| *s == side)
        .map(|(_, xy)| *xy)
        .with_context(|| format!("KeyError: {side}"))
}

/// `air_position` as the dict Python reads.
pub fn air_position_val() -> Val {
    let mut d = Dict::new();
    for (side, xy) in AIR_POSITION {
        d.set(side, xy);
    }
    d.val()
}

/// `cylinder(xy, z0, z1, diameter)`.
pub fn cylinder(rt: &Runtime, xy: [f64; 2], z0: f64, z1: f64, diameter: f64) -> Result<Val> {
    let cq = Cq::new(rt)?;
    cq.solid(
        "makeCylinder",
        args![diameter / 2.0, z1 - z0, cq.vector([xy[0], xy[1], z0])?],
    )
}

/// `spool_envelope(xy, z0, specification)`: the waisted spool the plate captures.
pub fn spool_envelope(rt: &Runtime, xy: [f64; 2], z0: f64, specification: &Grip) -> Result<Val> {
    let cq = Cq::new(rt)?;
    let z1 = z0 + PLATE_THICKNESS;
    let waist = specification.waist_d / 2.0;
    let flare = specification.flare_d / 2.0;
    let depth = flare - waist;
    let body = cylinder(rt, xy, z0, z1, 2.0 * waist)?;
    let lower = cq.solid("makeCone", args![flare, waist, depth, cq.vector([xy[0], xy[1], z0])?])?;
    let upper = cq.solid(
        "makeCone",
        args![waist, flare, depth, cq.vector([xy[0], xy[1], z1 - depth])?],
    )?;
    body.m("fuse", vec![lower, upper])?.m("clean", vec![])
}

/// `seat_tool(xy, z0, specification)`: the spool's seat with a skim over its top face.
pub fn seat_tool(rt: &Runtime, xy: [f64; 2], z0: f64, specification: &Grip) -> Result<Val> {
    let z1 = z0 + PLATE_THICKNESS;
    spool_envelope(rt, xy, z0, specification)?.m(
        "fuse",
        args![cylinder(rt, xy, z1, z1 + 0.1, specification.flare_d)?],
    )
}

/// `build_grommet(specification, xy=(0.0, 0.0), z0=0.0)`.
pub fn build_grommet(rt: &Runtime, specification: &Grip, xy: [f64; 2], z0: f64) -> Result<Val> {
    let cq = Cq::new(rt)?;
    let z1 = z0 + PLATE_THICKNESS;
    let radius = specification.bore_d / 2.0;
    let lead_radius = specification.lead_d / 2.0;
    let lead_height = specification.lead_h;
    let bore = cylinder(rt, xy, z0 - 0.1, z1 + 0.1, 2.0 * radius)?;
    let lower = cq.solid(
        "makeCone",
        args![lead_radius, radius, lead_height, cq.vector([xy[0], xy[1], z0])?],
    )?;
    let upper = cq.solid(
        "makeCone",
        args![radius, lead_radius, lead_height, cq.vector([xy[0], xy[1], z1 - lead_height])?],
    )?;
    let opening = bore.m("fuse", vec![lower, upper])?;
    spool_envelope(rt, xy, z0, specification)?
        .m("cut", args![opening])?
        .m("clean", vec![])
}

/// `build_air_tube(side, lid_underside_z, casing_face_z)`.
pub fn build_air_tube(rt: &Runtime, side: i64, lid_underside_z: f64, casing_face_z: f64) -> Result<Val> {
    let xy = air_position(side)?;
    let z0 = lid_underside_z - AIR_TUBE_BELOW_LID;
    let z1 = casing_face_z + AIR_TUBE_ABOVE_CASING;
    cylinder(rt, xy, z0, z1, AIR_TUBE_OD)?
        .m("cut", args![cylinder(rt, xy, z0 - 0.1, z1 + 0.1, AIR_TUBE_ID)?])?
        .m("clean", vec![])
}

fn grip_arg(c: &mut Call, index: usize) -> Result<Grip> {
    Grip::of(&c.req::<Val>(index, "specification")?)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    ns.value("plate_thickness", PLATE_THICKNESS);
    ns.value("liquid_grip", LIQUID_GRIP.val());
    ns.value("air_grip", AIR_GRIP.val());
    ns.value("air_position", air_position_val());
    ns.value("air_tube_od", AIR_TUBE_OD);
    ns.value("air_tube_id", AIR_TUBE_ID);
    ns.value("air_tube_above_casing", AIR_TUBE_ABOVE_CASING);
    ns.value("air_tube_below_lid", AIR_TUBE_BELOW_LID);
    ns.value("air_passage_diameter", AIR_PASSAGE_DIAMETER);
    ns.value("air_passage_wall", AIR_PASSAGE_WALL);
    ns.func(rt, "__getattr__", |rt, c| {
        let name = c.req::<String>(0, "name")?;
        if name == "cq" {
            return rt.py("cadquery");
        }
        bail!("{name}")
    });
    ns.func(rt, "cylinder", |rt, c| {
        let xy = c.req(0, "xy")?;
        let (z0, z1) = (c.req(1, "z0")?, c.req(2, "z1")?);
        cylinder(rt, xy, z0, z1, c.req(3, "diameter")?)
    });
    ns.func(rt, "spool_envelope", |rt, c| {
        let (xy, z0) = (c.req(0, "xy")?, c.req(1, "z0")?);
        spool_envelope(rt, xy, z0, &grip_arg(c, 2)?)
    });
    ns.func(rt, "seat_tool", |rt, c| {
        let (xy, z0) = (c.req(0, "xy")?, c.req(1, "z0")?);
        seat_tool(rt, xy, z0, &grip_arg(c, 2)?)
    });
    ns.func(rt, "build_grommet", |rt, c| {
        let specification = grip_arg(c, 0)?;
        let xy = c.opt(1, "xy", [0.0, 0.0])?;
        let z0 = c.opt(2, "z0", 0.0)?;
        build_grommet(rt, &specification, xy, z0)
    });
    ns.func(rt, "build_air_tube", |rt, c| {
        let side = c.req(0, "side")?;
        let lid = c.req(1, "lid_underside_z")?;
        build_air_tube(rt, side, lid, c.req(2, "casing_face_z")?)
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
