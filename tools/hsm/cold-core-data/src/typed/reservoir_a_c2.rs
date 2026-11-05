//! `_reservoir_a_c2`: reservoir A's integral C2 snap pair on the cold-core top lid, in
//! appliance millimetres.

use super::cad::Cq;
use super::*;

pub const NAME: &str = "_reservoir_a_c2";

pub const CENTRE: [f64; 3] = [57.25, 209.75, 258.5];
pub const PITCH: f64 = 13.5;
pub const TUBE_OD: f64 = 6.35;
pub const BORE: f64 = 6.35;
pub const WING: f64 = 2.4;
pub const TIP_DEGREES: f64 = 125.42102606277044;
pub const SPAN: f64 = 8.0;
pub const LID_FACE: f64 = 253.4;
pub const FLOOR: f64 = 3.0;

const PRINT_BASIS: &str = "Lid flat underside on bed; C2 mouths grow upward, matching the floor-rooted trial orientation.";
const SPRING_BASIS: &str =
    "Accepted C2 bore6.35, wing2.4 and tip125.421 degrees; no load or lifetime claim.";

/// `specification()`: the pair's datums.
pub struct Specification {
    pub tube_centers_world: [[f64; 3]; 2],
    pub seat_radius: f64,
    pub base_floor_world_z: f64,
    pub base_top_world_z: f64,
    pub base_low: [f64; 3],
    pub base_high: [f64; 3],
    pub body_high: [f64; 3],
    pub outer_radius: f64,
    pub outer_width: f64,
    pub central_land: f64,
    pub static_outer_gap: f64,
    pub nominal_nose_spread_per_jaw: f64,
    pub opposing_jaw_envelope_gap: f64,
}

/// `[a, b, c]` as the list Python builds.
fn list3(p: [f64; 3]) -> Val {
    p.to_vec().to_val()
}

impl Specification {
    /// The dict `specification()` returns. Its base and body bounds share their low corner,
    /// and both `tube_axis_worlds` rows are one list, as the source builds them.
    pub fn val(&self) -> Val {
        let low = list3(self.base_low);
        let axis_row = list3([0.0, 1.0, 0.0]);
        Dict::new()
            .with("closure", "direct-snap")
            .with("centre_world_mm", list3(CENTRE))
            .with(
                "tube_centers_world_mm",
                Val::list(self.tube_centers_world.iter().map(|p| list3(*p)).collect()),
            )
            .with("tube_axis_world", list3([0.0, 1.0, 0.0]))
            .with("tube_axis_worlds", Val::list(vec![axis_row.clone(), axis_row]))
            .with("tube_od_mm", TUBE_OD)
            .with("bore_diameter_mm", BORE)
            .with("seat_radius_mm", self.seat_radius)
            .with("tube_pitch_mm", PITCH)
            .with("station_length_mm", SPAN)
            .with("spring_thickness_mm", WING)
            .with("tip_degrees", TIP_DEGREES)
            .with("lid_face_z_mm", LID_FACE)
            .with("base_floor_world_z_mm", self.base_floor_world_z)
            .with("base_top_world_z_mm", self.base_top_world_z)
            .with(
                "base_bounds_mm",
                Val::list(vec![low.clone(), list3(self.base_high)]),
            )
            .with("body_bounds_mm", Val::list(vec![low, list3(self.body_high)]))
            .with("floor_stock_mm", FLOOR)
            .with("outer_radius_mm", self.outer_radius)
            .with("outer_width_mm", self.outer_width)
            .with("central_land_mm", self.central_land)
            .with("static_outer_gap_mm", self.static_outer_gap)
            .with("nominal_nose_spread_per_jaw_mm", self.nominal_nose_spread_per_jaw)
            .with("clearance_spread_per_jaw_mm", 1.0)
            .with("opposing_jaw_envelope_gap_mm", self.opposing_jaw_envelope_gap)
            .with("insertion_direction_world", list3([0.0, 0.0, -1.0]))
            .with("print_up_world", list3([0.0, 0.0, 1.0]))
            .with("print_basis", PRINT_BASIS)
            .with("spring_basis", SPRING_BASIS)
            .val()
    }
}

/// `specification()`.
pub fn specification() -> Specification {
    let radius = BORE / 2.0;
    let outer = radius + WING;
    let [x, y, z] = CENTRE;
    let centres = [-1.0, 1.0].map(|side: f64| [x + side * PITCH / 2.0, y, z]);
    let low = [centres[0][0] - outer, y - SPAN / 2.0, LID_FACE - FLOOR];
    let high = [centres[1][0] + outer, y + SPAN / 2.0, z];
    let nose = WING / 2.0;
    let middle = radius + nose;
    let spread = TUBE_OD / 2.0 + nose - middle * radians(TIP_DEGREES).sin();
    Specification {
        tube_centers_world: centres,
        seat_radius: radius,
        base_floor_world_z: LID_FACE - FLOOR,
        base_top_world_z: z,
        base_low: low,
        base_high: high,
        body_high: [
            high[0],
            high[1],
            z - middle * radians(TIP_DEGREES).cos() + nose,
        ],
        outer_radius: outer,
        outer_width: PITCH + 2.0 * outer,
        central_land: PITCH - BORE,
        static_outer_gap: PITCH - 2.0 * outer,
        nominal_nose_spread_per_jaw: spread,
        opposing_jaw_envelope_gap: PITCH - 2.0 * outer - 2.0,
    }
}

/// `clips()`: the two C2 clips from `route_snap.tube_clip`, one per tube centre.
pub fn clips(rt: &Runtime) -> Result<(Val, Val)> {
    let cadlib = parent_n(&resolve(&rt.file(NAME)), 1).join("cadlib");
    rt.sys_path_insert(0, &cadlib)?;
    let tube_clip = rt.pya("route_snap", "tube_clip")?;
    let spec = specification();
    let clip = |point: [f64; 3]| {
        tube_clip.ck(
            args![list3(point), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), CENTRE[2] - LID_FACE],
            kw![
                "tube_od" => TUBE_OD,
                "bore_diameter" => BORE,
                "wing" => WING,
                "span" => SPAN,
                "tip_degrees" => TIP_DEGREES,
                "print_up" => (0.0, 0.0, 1.0)
            ],
        )
    };
    let [first, second] = spec.tube_centers_world;
    let first = clip(first)?;
    Ok((first, clip(second)?))
}

/// `base()`: the lid-rooted stock fused with both clips, with the tube bores cut through.
pub fn base(rt: &Runtime) -> Result<Val> {
    let cq = Cq::new(rt)?;
    let s = specification();
    let (lo, hi) = (s.base_low, s.base_high);
    let stock = cq.make_box(std::array::from_fn(|i| hi[i] - lo[i]), lo)?;
    let (first, second) = clips(rt)?;
    let mut body = stock.m("fuse", vec![first, second])?;
    for [x, y, z] in s.tube_centers_world {
        let bore = cq.cylinder(
            BORE / 2.0,
            SPAN + 0.2,
            [x, y - SPAN / 2.0 - 0.1, z],
            [0.0, 1.0, 0.0],
        )?;
        body = body.m("cut", args![bore])?;
    }
    body.m("clean", vec![])
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    ns.module(rt, "math", "math")?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.module(rt, "sys", "sys")?;
    ns.value("CENTRE", CENTRE);
    ns.value("PITCH", PITCH);
    ns.value("TUBE_OD", TUBE_OD);
    ns.value("BORE", BORE);
    ns.value("WING", WING);
    ns.value("TIP_DEGREES", TIP_DEGREES);
    ns.value("SPAN", SPAN);
    ns.value("LID_FACE", LID_FACE);
    ns.value("FLOOR", FLOOR);
    ns.func(rt, "specification", |_, _| Ok(specification().val()));
    ns.func(rt, "clips", |rt, _| Ok(clips(rt)?.to_val()));
    ns.func(rt, "base", |rt, _| base(rt));
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
