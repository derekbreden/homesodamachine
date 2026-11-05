//! `_cold_core_interface`: shared cold-core datums and construction interfaces.
//!
//! The Rust recipe (`interface::base`) owns the casing stock, cavity envelope, clamp stack and
//! port lanes; this module carries those as typed fields beside the cap mount and passage
//! recipes the sibling parts read, and records its stated bounds in source order.

use super::above_core_mounts as mounts;
use super::cad::Cq;
use super::*;
use serde_json::Value;

pub const NAME: &str = "_cold_core_interface";

/// The reservoirs' fill and draw bores, keyed by side.
#[derive(Clone, Copy, Debug)]
pub struct Ports {
    pub minus: [f64; 2],
    pub plus: [f64; 2],
}
impl Ports {
    pub fn side(&self, side: i64) -> Result<[f64; 2]> {
        match side {
            -1 => Ok(self.minus),
            1 => Ok(self.plus),
            _ => bail!("unknown reservoir side"),
        }
    }
}
impl ToVal for Ports {
    fn to_val(&self) -> Val {
        dict! {-1i64 => self.minus, 1i64 => self.plus}
    }
}

/// `interface::base`, the Rust recipe's casing stock, cavity envelope, clamp stack and port
/// datums, as typed fields.
pub struct Base {
    pub wall_thickness: f64,
    pub floor_thickness: f64,
    pub wall_and_floor_thickness: f64,
    pub hole_shift_from_edge: f64,
    pub outer_shell_wall: f64,
    pub coil_radial_clearance: f64,
    pub carbonator_coil_envelope_radius: f64,
    pub pocket_centerward_arc_outer_radius: f64,
    pub foam_thickness_around_cylinder: f64,
    pub below_carbonator_elbows_height: f64,
    pub above_carbonator_elbows_height: f64,
    pub foam_shell_outer_height: f64,
    pub carbonator_support_ring_height: f64,
    pub support_ring_radial_width: f64,
    pub passage_tube_od: f64,
    pub port_hole_radius: f64,
    pub reed_x_depth: f64,
    pub reed_y_half_w: f64,
    pub level_rod_y: f64,
    pub bag_pocket_far_inner_x: f64,
    pub bag_pocket_y_inner_max: f64,
    pub bag_pocket_width: f64,
    pub bag_pocket_depth: f64,
    pub bag_pocket_floor_top_z: f64,
    pub bag_pocket_walls_top_z: f64,
    pub reed_channel_inner_x: f64,
    pub reed_column_axis_x: f64,
    pub reservoir_clearance: f64,
    pub bag_pocket_corner_inner_radius: f64,
    pub reservoir_floor_thickness: f64,
    pub reservoir_fill_port: Ports,
    pub reservoir_fill_sides: [i64; 2],
    pub reservoir_draw_port: Ports,
    pub casing_foil_allowance: f64,
    pub casing_foil_land: f64,
    pub outer_shell_x_length: f64,
    pub outer_shell_y_length: f64,
    pub seam_channel_land: f64,
    pub seam_channel_width: f64,
    pub seam_channel_depth: f64,
    pub bag_pocket_outermost_x: f64,
    pub outer_shell_foam_gap: f64,
    pub forward_band_width: f64,
    pub forward_band_mid_x: f64,
    pub pour_band_pocket_side_y: f64,
    pub pour_band_shell_side_y: f64,
    pub foam_cap_interior_height: f64,
    pub foam_cap_height: f64,
    pub foam_cap_lid_pour_radius: f64,
    pub foam_cap_lid_vent_radius: f64,
    pub foam_cap_lid_hole_inset: f64,
    pub top_lid_pour_xy: [f64; 2],
    pub top_lid_vent_setback: f64,
    pub carbonator_port_offset: f64,
    pub carbonator_sensor_azimuth: f64,
    pub carbonator_sensor_axis: [f64; 2],
    pub carbonator_float_top_stop_height: f64,
    pub carbonator_float_top_stop_diameter: f64,
    pub co2_inlet_y: f64,
    pub co2_inlet_tube_radius: f64,
    pub water_inlet_port_y: f64,
    pub prv_port_y: f64,
    pub cap_shell_clearance: f64,
    pub cap_lid_clearance: f64,
    pub screw_clearance_radius: f64,
    pub insert_pocket_radius: f64,
    pub insert_pocket_depth: f64,
    pub screw_boss_size: f64,
    pub screw_guard_diameter: f64,
    pub screw_head_height: f64,
    pub head_seat_recess: f64,
    pub head_cbore_radius: f64,
    pub head_cbore_depth: f64,
    pub head_pad_height: f64,
    pub head_pad_slip: f64,
    pub foam_cap_lid_height: f64,
    pub top_lid_bottom_z: f64,
    pub foam_shell_rim_z: f64,
    pub bottom_cap_height: f64,
    pub bottom_pour_radius: f64,
    pub bottom_pour_positions: Vec<[f64; 2]>,
    pub front_wall_x: f64,
    pub port_lane_outer_y: f64,
    pub port_lane_inner_y: f64,
    pub port_lane_mid_y: f64,
    pub west_lane_mid_y: f64,
    pub evap_tail_low_z: f64,
    pub evap_tail_high_z: f64,
    pub corner_round_radius: f64,
    pub boss_wall_y: f64,
    pub boss_wall_x: f64,
    pub mid_screw_x_offset: f64,
    pub attachment_stations: Vec<([f64; 2], String)>,
    pub attachment_xy_positions: Vec<[f64; 2]>,
    pub lid_attachment_stations: Vec<([f64; 2], String)>,
    pub lid_attachment_xy_positions: Vec<[f64; 2]>,
    pub cap_screw_length: f64,
    pub insert_length: f64,
    pub cap_screw_beyond_face: f64,
    pub top_lid_screw_beyond_face: f64,
    pub cap_screw_tip_air: f64,
    pub bottom_screw_bore_depth: f64,
    pub top_screw_bore_depth: f64,
    pub deck_mount_boss_radius: f64,
    pub deck_mount_bore_radius: f64,
    pub deck_mount_lid_slip: f64,
    pub deck_mount_insert_length: f64,
    pub deck_mount_bore_relief: f64,
    pub deck_mount_cap_gap: f64,
    pub states: Vec<(String, String, String, bool, String)>,
}

impl Module for Base {
    const NAME: &'static str = "_cold_core_interface (base)";
    fn init(rt: &Runtime) -> Result<Self> {
        state(rt)?;
        bail!("the interface base is settled by {NAME}")
    }
}

impl Base {
    pub fn from_json(v: &Value) -> Result<Self> {
        let f = |k: &str| v[k].as_f64().with_context(|| format!("base {k}"));
        let xy = |w: &Value| -> Result<[f64; 2]> { Ok([w[0].as_f64().context("x")?, w[1].as_f64().context("y")?]) };
        let xys = |k: &str| -> Result<Vec<[f64; 2]>> { v[k].as_array().context("pairs")?.iter().map(xy).collect() };
        let stations = |k: &str| -> Result<Vec<([f64; 2], String)>> { v[k].as_array().context("stations")?.iter().map(|r| Ok((xy(&r[0])?, r[1].as_str().context("wall")?.to_owned()))).collect() };
        let ports = |k: &str| -> Result<Ports> { Ok(Ports { minus: xy(&v[k]["-1"])?, plus: xy(&v[k]["1"])? }) };
        Ok(Self {
            wall_thickness: f("wall_thickness")?,
            floor_thickness: f("floor_thickness")?,
            wall_and_floor_thickness: f("wall_and_floor_thickness")?,
            hole_shift_from_edge: f("hole_shift_from_edge")?,
            outer_shell_wall: f("outer_shell_wall")?,
            coil_radial_clearance: f("coil_radial_clearance")?,
            carbonator_coil_envelope_radius: f("carbonator_coil_envelope_radius")?,
            pocket_centerward_arc_outer_radius: f("pocket_centerward_arc_outer_radius")?,
            foam_thickness_around_cylinder: f("foam_thickness_around_cylinder")?,
            below_carbonator_elbows_height: f("below_carbonator_elbows_height")?,
            above_carbonator_elbows_height: f("above_carbonator_elbows_height")?,
            foam_shell_outer_height: f("foam_shell_outer_height")?,
            carbonator_support_ring_height: f("carbonator_support_ring_height")?,
            support_ring_radial_width: f("support_ring_radial_width")?,
            passage_tube_od: f("passage_tube_od")?,
            port_hole_radius: f("port_hole_radius")?,
            reed_x_depth: f("reed_x_depth")?,
            reed_y_half_w: f("reed_y_half_w")?,
            level_rod_y: f("level_rod_y")?,
            bag_pocket_far_inner_x: f("bag_pocket_far_inner_x")?,
            bag_pocket_y_inner_max: f("bag_pocket_y_inner_max")?,
            bag_pocket_width: f("bag_pocket_width")?,
            bag_pocket_depth: f("bag_pocket_depth")?,
            bag_pocket_floor_top_z: f("bag_pocket_floor_top_z")?,
            bag_pocket_walls_top_z: f("bag_pocket_walls_top_z")?,
            reed_channel_inner_x: f("reed_channel_inner_x")?,
            reed_column_axis_x: f("reed_column_axis_x")?,
            reservoir_clearance: f("reservoir_clearance")?,
            bag_pocket_corner_inner_radius: f("bag_pocket_corner_inner_radius")?,
            reservoir_floor_thickness: f("reservoir_floor_thickness")?,
            reservoir_fill_port: ports("reservoir_fill_port")?,
            reservoir_fill_sides: [v["reservoir_fill_sides"][0].as_i64().context("side")?, v["reservoir_fill_sides"][1].as_i64().context("side")?],
            reservoir_draw_port: ports("reservoir_draw_port")?,
            casing_foil_allowance: f("casing_foil_allowance")?,
            casing_foil_land: f("casing_foil_land")?,
            outer_shell_x_length: f("outer_shell_x_length")?,
            outer_shell_y_length: f("outer_shell_y_length")?,
            seam_channel_land: f("seam_channel_land")?,
            seam_channel_width: f("seam_channel_width")?,
            seam_channel_depth: f("seam_channel_depth")?,
            bag_pocket_outermost_x: f("bag_pocket_outermost_x")?,
            outer_shell_foam_gap: f("outer_shell_foam_gap")?,
            forward_band_width: f("forward_band_width")?,
            forward_band_mid_x: f("forward_band_mid_x")?,
            pour_band_pocket_side_y: f("pour_band_pocket_side_y")?,
            pour_band_shell_side_y: f("pour_band_shell_side_y")?,
            foam_cap_interior_height: f("foam_cap_interior_height")?,
            foam_cap_height: f("foam_cap_height")?,
            foam_cap_lid_pour_radius: f("foam_cap_lid_pour_radius")?,
            foam_cap_lid_vent_radius: f("foam_cap_lid_vent_radius")?,
            foam_cap_lid_hole_inset: f("foam_cap_lid_hole_inset")?,
            top_lid_pour_xy: xy(&v["top_lid_pour_xy"])?,
            top_lid_vent_setback: f("top_lid_vent_setback")?,
            carbonator_port_offset: f("carbonator_port_offset")?,
            carbonator_sensor_azimuth: f("carbonator_sensor_azimuth")?,
            carbonator_sensor_axis: xy(&v["carbonator_sensor_axis"])?,
            carbonator_float_top_stop_height: f("carbonator_float_top_stop_height")?,
            carbonator_float_top_stop_diameter: f("carbonator_float_top_stop_diameter")?,
            co2_inlet_y: f("co2_inlet_y")?,
            co2_inlet_tube_radius: f("co2_inlet_tube_radius")?,
            water_inlet_port_y: f("water_inlet_port_y")?,
            prv_port_y: f("prv_port_y")?,
            cap_shell_clearance: f("cap_shell_clearance")?,
            cap_lid_clearance: f("cap_lid_clearance")?,
            screw_clearance_radius: f("screw_clearance_radius")?,
            insert_pocket_radius: f("insert_pocket_radius")?,
            insert_pocket_depth: f("insert_pocket_depth")?,
            screw_boss_size: f("screw_boss_size")?,
            screw_guard_diameter: f("screw_guard_diameter")?,
            screw_head_height: f("screw_head_height")?,
            head_seat_recess: f("head_seat_recess")?,
            head_cbore_radius: f("head_cbore_radius")?,
            head_cbore_depth: f("head_cbore_depth")?,
            head_pad_height: f("head_pad_height")?,
            head_pad_slip: f("head_pad_slip")?,
            foam_cap_lid_height: f("foam_cap_lid_height")?,
            top_lid_bottom_z: f("top_lid_bottom_z")?,
            foam_shell_rim_z: f("foam_shell_rim_z")?,
            bottom_cap_height: f("bottom_cap_height")?,
            bottom_pour_radius: f("bottom_pour_radius")?,
            bottom_pour_positions: xys("bottom_pour_positions")?,
            front_wall_x: f("front_wall_x")?,
            port_lane_outer_y: f("port_lane_outer_y")?,
            port_lane_inner_y: f("port_lane_inner_y")?,
            port_lane_mid_y: f("port_lane_mid_y")?,
            west_lane_mid_y: f("west_lane_mid_y")?,
            evap_tail_low_z: f("evap_tail_low_z")?,
            evap_tail_high_z: f("evap_tail_high_z")?,
            corner_round_radius: f("corner_round_radius")?,
            boss_wall_y: f("_boss_wall_y")?,
            boss_wall_x: f("_boss_wall_x")?,
            mid_screw_x_offset: f("mid_screw_x_offset")?,
            attachment_stations: stations("attachment_stations")?,
            attachment_xy_positions: xys("attachment_xy_positions")?,
            lid_attachment_stations: stations("lid_attachment_stations")?,
            lid_attachment_xy_positions: xys("lid_attachment_xy_positions")?,
            cap_screw_length: f("cap_screw_length")?,
            insert_length: f("insert_length")?,
            cap_screw_beyond_face: f("cap_screw_beyond_face")?,
            top_lid_screw_beyond_face: f("top_lid_screw_beyond_face")?,
            cap_screw_tip_air: f("cap_screw_tip_air")?,
            bottom_screw_bore_depth: f("bottom_screw_bore_depth")?,
            top_screw_bore_depth: f("top_screw_bore_depth")?,
            deck_mount_boss_radius: f("deck_mount_boss_radius")?,
            deck_mount_bore_radius: f("deck_mount_bore_radius")?,
            deck_mount_lid_slip: f("deck_mount_lid_slip")?,
            deck_mount_insert_length: f("deck_mount_insert_length")?,
            deck_mount_bore_relief: f("deck_mount_bore_relief")?,
            deck_mount_cap_gap: f("deck_mount_cap_gap")?,
            states: v["_states"].as_array().context("states")?.iter().map(|r| Ok((r[0].as_str().context("id")?.to_owned(), r[1].as_str().context("label")?.to_owned(), r[2].as_str().context("target")?.to_owned(), r[3].as_bool().context("ok")?, r[4].as_str().context("message")?.to_owned()))).collect::<Result<_>>()?,
        })
    }
    /// The module globals the recipe defines, in its JSON's key order, as `globals().update`
    /// leaves them once the source has made tuples and int keys of them.
    pub fn globals(&self) -> Vec<(&'static str, Val)> {
        let pair = |p: &[f64; 2]| Val::Tuple(vec![Val::Float(p[0]), Val::Float(p[1])]);
        let stations = |rows: &[([f64; 2], String)]| Val::Tuple(rows.iter().map(|(p, w)| Val::Tuple(vec![pair(p), Val::Str(w.clone())])).collect());
        vec![
            ("_boss_wall_x", Val::Float(self.boss_wall_x)),
            ("_boss_wall_y", Val::Float(self.boss_wall_y)),
            ("above_carbonator_elbows_height", Val::Float(self.above_carbonator_elbows_height)),
            ("attachment_stations", stations(&self.attachment_stations)),
            ("attachment_xy_positions", Val::list(self.attachment_xy_positions.iter().map(pair).collect())),
            ("bag_pocket_corner_inner_radius", Val::Float(self.bag_pocket_corner_inner_radius)),
            ("bag_pocket_depth", Val::Float(self.bag_pocket_depth)),
            ("bag_pocket_far_inner_x", Val::Float(self.bag_pocket_far_inner_x)),
            ("bag_pocket_floor_top_z", Val::Float(self.bag_pocket_floor_top_z)),
            ("bag_pocket_outermost_x", Val::Float(self.bag_pocket_outermost_x)),
            ("bag_pocket_walls_top_z", Val::Float(self.bag_pocket_walls_top_z)),
            ("bag_pocket_width", Val::Float(self.bag_pocket_width)),
            ("bag_pocket_y_inner_max", Val::Float(self.bag_pocket_y_inner_max)),
            ("below_carbonator_elbows_height", Val::Float(self.below_carbonator_elbows_height)),
            ("bottom_cap_height", Val::Float(self.bottom_cap_height)),
            ("bottom_pour_positions", Val::Tuple(self.bottom_pour_positions.iter().map(pair).collect())),
            ("bottom_pour_radius", Val::Float(self.bottom_pour_radius)),
            ("bottom_screw_bore_depth", Val::Float(self.bottom_screw_bore_depth)),
            ("cap_lid_clearance", Val::Float(self.cap_lid_clearance)),
            ("cap_screw_beyond_face", Val::Float(self.cap_screw_beyond_face)),
            ("cap_screw_length", Val::Float(self.cap_screw_length)),
            ("cap_screw_tip_air", Val::Float(self.cap_screw_tip_air)),
            ("cap_shell_clearance", Val::Float(self.cap_shell_clearance)),
            ("carbonator_coil_envelope_radius", Val::Float(self.carbonator_coil_envelope_radius)),
            ("carbonator_float_top_stop_diameter", Val::Float(self.carbonator_float_top_stop_diameter)),
            ("carbonator_float_top_stop_height", Val::Float(self.carbonator_float_top_stop_height)),
            ("carbonator_port_offset", Val::Float(self.carbonator_port_offset)),
            ("carbonator_sensor_axis", pair(&self.carbonator_sensor_axis)),
            ("carbonator_sensor_azimuth", Val::Float(self.carbonator_sensor_azimuth)),
            ("carbonator_support_ring_height", Val::Float(self.carbonator_support_ring_height)),
            ("casing_foil_allowance", Val::Float(self.casing_foil_allowance)),
            ("casing_foil_land", Val::Float(self.casing_foil_land)),
            ("co2_inlet_tube_radius", Val::Float(self.co2_inlet_tube_radius)),
            ("co2_inlet_y", Val::Float(self.co2_inlet_y)),
            ("coil_radial_clearance", Val::Float(self.coil_radial_clearance)),
            ("corner_round_radius", Val::Float(self.corner_round_radius)),
            ("deck_mount_bore_radius", Val::Float(self.deck_mount_bore_radius)),
            ("deck_mount_bore_relief", Val::Float(self.deck_mount_bore_relief)),
            ("deck_mount_boss_radius", Val::Float(self.deck_mount_boss_radius)),
            ("deck_mount_cap_gap", Val::Float(self.deck_mount_cap_gap)),
            ("deck_mount_insert_length", Val::Float(self.deck_mount_insert_length)),
            ("deck_mount_lid_slip", Val::Float(self.deck_mount_lid_slip)),
            ("evap_tail_high_z", Val::Float(self.evap_tail_high_z)),
            ("evap_tail_low_z", Val::Float(self.evap_tail_low_z)),
            ("floor_thickness", Val::Float(self.floor_thickness)),
            ("foam_cap_height", Val::Float(self.foam_cap_height)),
            ("foam_cap_interior_height", Val::Float(self.foam_cap_interior_height)),
            ("foam_cap_lid_height", Val::Float(self.foam_cap_lid_height)),
            ("foam_cap_lid_hole_inset", Val::Float(self.foam_cap_lid_hole_inset)),
            ("foam_cap_lid_pour_radius", Val::Float(self.foam_cap_lid_pour_radius)),
            ("foam_cap_lid_vent_radius", Val::Float(self.foam_cap_lid_vent_radius)),
            ("foam_shell_outer_height", Val::Float(self.foam_shell_outer_height)),
            ("foam_shell_rim_z", Val::Float(self.foam_shell_rim_z)),
            ("foam_thickness_around_cylinder", Val::Float(self.foam_thickness_around_cylinder)),
            ("forward_band_mid_x", Val::Float(self.forward_band_mid_x)),
            ("forward_band_width", Val::Float(self.forward_band_width)),
            ("front_wall_x", Val::Float(self.front_wall_x)),
            ("head_cbore_depth", Val::Float(self.head_cbore_depth)),
            ("head_cbore_radius", Val::Float(self.head_cbore_radius)),
            ("head_pad_height", Val::Float(self.head_pad_height)),
            ("head_pad_slip", Val::Float(self.head_pad_slip)),
            ("head_seat_recess", Val::Float(self.head_seat_recess)),
            ("hole_shift_from_edge", Val::Float(self.hole_shift_from_edge)),
            ("insert_length", Val::Float(self.insert_length)),
            ("insert_pocket_depth", Val::Float(self.insert_pocket_depth)),
            ("insert_pocket_radius", Val::Float(self.insert_pocket_radius)),
            ("level_rod_y", Val::Float(self.level_rod_y)),
            ("lid_attachment_stations", stations(&self.lid_attachment_stations)),
            ("lid_attachment_xy_positions", Val::list(self.lid_attachment_xy_positions.iter().map(pair).collect())),
            ("mid_screw_x_offset", Val::Float(self.mid_screw_x_offset)),
            ("outer_shell_foam_gap", Val::Float(self.outer_shell_foam_gap)),
            ("outer_shell_wall", Val::Float(self.outer_shell_wall)),
            ("outer_shell_x_length", Val::Float(self.outer_shell_x_length)),
            ("outer_shell_y_length", Val::Float(self.outer_shell_y_length)),
            ("passage_tube_od", Val::Float(self.passage_tube_od)),
            ("pocket_centerward_arc_outer_radius", Val::Float(self.pocket_centerward_arc_outer_radius)),
            ("port_hole_radius", Val::Float(self.port_hole_radius)),
            ("port_lane_inner_y", Val::Float(self.port_lane_inner_y)),
            ("port_lane_mid_y", Val::Float(self.port_lane_mid_y)),
            ("port_lane_outer_y", Val::Float(self.port_lane_outer_y)),
            ("pour_band_pocket_side_y", Val::Float(self.pour_band_pocket_side_y)),
            ("pour_band_shell_side_y", Val::Float(self.pour_band_shell_side_y)),
            ("prv_port_y", Val::Float(self.prv_port_y)),
            ("reed_channel_inner_x", Val::Float(self.reed_channel_inner_x)),
            ("reed_column_axis_x", Val::Float(self.reed_column_axis_x)),
            ("reed_x_depth", Val::Float(self.reed_x_depth)),
            ("reed_y_half_w", Val::Float(self.reed_y_half_w)),
            ("reservoir_clearance", Val::Float(self.reservoir_clearance)),
            ("reservoir_draw_port", self.reservoir_draw_port.to_val()),
            ("reservoir_fill_port", self.reservoir_fill_port.to_val()),
            ("reservoir_fill_sides", Val::Tuple(self.reservoir_fill_sides.iter().map(|s| Val::Int(*s)).collect())),
            ("reservoir_floor_thickness", Val::Float(self.reservoir_floor_thickness)),
            ("screw_boss_size", Val::Float(self.screw_boss_size)),
            ("screw_clearance_radius", Val::Float(self.screw_clearance_radius)),
            ("screw_guard_diameter", Val::Float(self.screw_guard_diameter)),
            ("screw_head_height", Val::Float(self.screw_head_height)),
            ("seam_channel_depth", Val::Float(self.seam_channel_depth)),
            ("seam_channel_land", Val::Float(self.seam_channel_land)),
            ("seam_channel_width", Val::Float(self.seam_channel_width)),
            ("support_ring_radial_width", Val::Float(self.support_ring_radial_width)),
            ("top_lid_bottom_z", Val::Float(self.top_lid_bottom_z)),
            ("top_lid_pour_xy", pair(&self.top_lid_pour_xy)),
            ("top_lid_screw_beyond_face", Val::Float(self.top_lid_screw_beyond_face)),
            ("top_lid_vent_setback", Val::Float(self.top_lid_vent_setback)),
            ("top_screw_bore_depth", Val::Float(self.top_screw_bore_depth)),
            ("wall_and_floor_thickness", Val::Float(self.wall_and_floor_thickness)),
            ("wall_thickness", Val::Float(self.wall_thickness)),
            ("water_inlet_port_y", Val::Float(self.water_inlet_port_y)),
            ("west_lane_mid_y", Val::Float(self.west_lane_mid_y)),
        ]
    }
}

/// The base, as soon as `_cold_core_interface` has read it: its own initialization and the
/// recipes it calls partway through read it here.
pub fn base(rt: &Runtime) -> Result<Rc<Base>> {
    if let Some(held) = rt.held::<Base>() {
        return Ok(held);
    }
    state(rt)?;
    rt.held::<Base>().context("interface base")
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// A horizontal valve cradle station.
#[derive(Clone)]
pub struct Cradle {
    pub centre: [f64; 2],
    pub yaw: f64,
    pub seat: Val,
}

/// A chain anchor rib on the lid's outer face.
#[derive(Clone)]
pub struct CapAnchor {
    pub centre: [f64; 2],
    pub seat_r: f64,
    pub over_face: Option<f64>,
    pub along: String,
    pub closure: String,
}

/// A side post standing on the cap.
#[derive(Clone)]
pub struct SideAnchor {
    pub centre: [f64; 2],
    pub over_face: f64,
    pub seat_r: f64,
    pub axis_off: f64,
    pub depth: f64,
}

pub struct State {
    pub base: Rc<Base>,
    here: PathBuf,
    fits: Val,
    valve_seat: Val,
    stated: Val,
    enclosure: [Val; 4],
    anchor_cap: Val,
    carbonator_outer_radius: Val,
    carbonator_height: Val,
    read: Val,
    interface_fits: Val,
    base_recipe: Val,
    base_states: Val,
    last_row: Val,
    deck_mount_type: Val,
    pub deck_mounts: OMap<mounts::DeckMount>,
    deck_mount_vals: Val,
    pub deck_mount_bore_depth: f64,
    mount_reach: Val,
    cradle_type: Val,
    pub cap_cradles: OMap<Cradle>,
    pub cap_cradle_corner_inset_x: f64,
    pub cap_cradle_corner_inset_y: f64,
    pub cap_cradle_socket_radius: f64,
    pub cap_cradle_wall: f64,
    pub cap_cradle_boss_radius: f64,
    pub cap_cradle_half_x: f64,
    pub cap_cradle_half_y: f64,
    pub cap_cradle_corner_radius: f64,
    cradle_vals: [Val; 8],
    pub cap_cradle_room_gap: f64,
    pub lldpe_tube_od: f64,
    pub cap_conduit_bore_radius: f64,
    pub cap_conduit_bore_radii: OMap<f64>,
    pub cap_conduit_wall: f64,
    pub cap_conduit_boss_radius: f64,
    pub cap_conduit_lid_slip: f64,
    pub cap_conduit_entry_skew: f64,
    pub cap_conduit_entry_relief_radius: f64,
    pub cap_conduit_entry_skew_ceiling: f64,
    pub co2_lane_x: f64,
    pub co2_cap_x: f64,
    pub water_outlet_climb_x: f64,
    pub water_outlet_upper_climb_x: f64,
    pub water_outlet_drift_z: (f64, f64),
    pub reed_cable_conduit_x: f64,
    pub reed_cable_conduit_y: f64,
    pub cap_fluid_conduits: OMap<[f64; 2]>,
    pub cap_cable_floor_conduits: OMap<[f64; 2]>,
    pub cap_cable_conduits: OMap<[f64; 2]>,
    pub cap_conduits: OMap<[f64; 2]>,
    pub cap_conduit_floor_xy: OMap<[f64; 2]>,
    pub cap_passive_guides: Vec<String>,
    pub cap_cable_guides: Vec<String>,
    pub cap_conduit_links: Vec<(String, String)>,
    pub cap_conduit_link_width: f64,
    fill_conduits: Vec<String>,
    fill_wanted: Vec<String>,
    pub carbonator_top_plate_z: f64,
    pub top_band_to_cap: f64,
    pub lldpe_bend_radius: f64,
    conduit_wall: Val,
    cradle_room: Val,
    anchor_type: Val,
    pub cap_anchors: OMap<CapAnchor>,
    pub cap_anchor_tie_w: f64,
    pub cap_anchor_cav_buffer: f64,
    pub cap_anchor_cav_w: f64,
    pub cap_anchor_cav_wall: f64,
    pub cap_anchor_len: f64,
    pub cap_anchor_wall: f64,
    pub cap_anchor_channel_height: f64,
    anchor_room: Val,
    side_anchor_type: Val,
    pub cap_side_wall: f64,
    pub cap_side_len: f64,
    pub cap_side_cav_w: f64,
    pub cap_side_flank: f64,
    pub cap_side_tie_t: f64,
    pub cap_side_cav_h: f64,
    pub cap_side_cav_backing_min: f64,
    pub cap_side_back_relief: f64,
    pub cap_side_web: f64,
    pub cap_side_anchors: OMap<SideAnchor>,
    side_anchor_room: Val,
    pair_neck: Val,
    last_name: String,
    last_pair: Option<(String, String, f64, &'static str, f64)>,
}

fn wall_neck(b: &Base, boss: f64, bore: f64, x: f64, y: f64) -> (f64, &'static str) {
    let to_outer = pmin(
        b.outer_shell_x_length / 2.0 - x.abs(),
        b.outer_shell_y_length / 2.0 - y.abs(),
    );
    if to_outer - b.outer_shell_wall >= boss {
        return (
            to_outer - b.outer_shell_wall - boss,
            "the pour gap behind a standing column",
        );
    }
    (to_outer - bore, "the wall left outboard of a merged bore")
}

/// Two-member frozensets compared as Python compares them.
fn same_pair(a: [[f64; 2]; 2], b: [[f64; 2]; 2]) -> bool {
    let eq = |p: [f64; 2], q: [f64; 2]| p[0] == q[0] && p[1] == q[1];
    a.iter().all(|p| b.iter().any(|q| eq(*p, *q))) && b.iter().all(|q| a.iter().any(|p| eq(*p, *q)))
}

fn pair_neck(
    boss: f64,
    links: &[(String, String)],
    conduits: &OMap<[f64; 2]>,
    link_width: f64,
    a: [f64; 2],
    b: [f64; 2],
) -> Result<(f64, &'static str)> {
    for (first, second) in links {
        if same_pair([a, b], [*conduits.at(first)?, *conduits.at(second)?]) {
            return Ok((link_width, "the connecting web"));
        }
    }
    Ok(bare_pair_neck(boss, a, b))
}

fn bare_pair_neck(boss: f64, a: [f64; 2], b: [f64; 2]) -> (f64, &'static str) {
    let r = boss;
    let d = hypot(&[a[0] - b[0], a[1] - b[1]]);
    if d >= 2.0 * r {
        return (d - 2.0 * r, "the pour gap between two standing columns");
    }
    (
        2.0 * pmax(r * r - (d / 2.0).powf(2.0), 0.0).sqrt(),
        "the neck their lens leaves",
    )
}

fn call_state(stated: &Val, row: Vec<Val>) -> Result<()> {
    stated.a("state")?.c(row)?;
    Ok(())
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let file = rt.file(NAME);
        let here = resolve(&file)
            .parent()
            .context("module directory")?
            .to_owned();
        rt.sys_path_insert(0, &ancestor(&here, "printed-parts")?.join("cadlib"))?;
        rt.sys_path_insert(0, &ancestor(&here, "hardware")?.join("scripts"))?;
        let parent = here.parent().context("cold-core parent")?.to_owned();
        rt.sys_path_insert(0, &parent.join("enclosure").join("enclosure"))?;
        rt.sys_path_insert(0, &parent.join("valve-seat"))?;
        let hardware = parent_n(&here, 1);
        rt.sys_path_insert(
            0,
            &hardware
                .join("reference")
                .join("g-ganen-pump")
                .join("installation"),
        )?;
        rt.sys_path_insert(0, &hardware.join("cold-core-layout"))?;
        let fits = rt.py("fits")?;
        let valve_seat = rt.py("valve_seat")?;
        mounts::state(rt)?;
        let stated = rt.py("_stated_bounds")?;
        let bound = stated.a("bound")?;
        stated.a("state")?;
        let enclosure = ["manifold_rise", "inner_limb_drop", "rear_plane_y", "rear_seam_clear"]
            .map(|name| rt.pya("_enclosure_interface", name));
        let [e0, e1, e2, e3] = enclosure;
        let enclosure = [e0?, e1?, e2?, e3?];
        let anchor_cap = rt.py("_anchor_cap_interface")?;
        let carbonator_outer_radius = rt.pya("_carbonator_stock", "carbonator_outer_radius")?;
        let carbonator_height = rt.pya("_carbonator_stock", "carbonator_height")?;
        let read = rt.pya("_cold_core_data", "read")?;
        let names = ["running", "slip", "m5_thread_pass_dia", "supported_surface"];
        let mut interface_fits = Dict::new();
        let mut fits_json = serde_json::Map::new();
        for name in names {
            let value = fits.a(name)?;
            fits_json.insert(name.into(), value.encode()?);
            interface_fits.set(name, value);
        }
        let interface_fits = interface_fits.val();
        let mut recipe = crate::interface::base(&Value::Object(fits_json))?;
        let base_states = recipe
            .as_object_mut()
            .context("interface base")?
            .remove("_states")
            .context("interface base states")?;
        let base = Base::from_json(&{
            let mut with = recipe.clone();
            with["_states"] = base_states.clone();
            with
        })?;
        let base_recipe = Val::decode(recipe)?;
        let base_states = Val::decode(base_states)?;
        let b = rt.put(base);
        let mut last_row = Val::None;
        for row in &b.states {
            let values = vec![
                Val::Str(row.0.clone()),
                Val::Str(row.1.clone()),
                Val::Str(row.2.clone()),
                Val::Bool(row.3),
                Val::Str(row.4.clone()),
            ];
            last_row = Val::list(values.clone());
            call_state(&stated, values)?;
        }

        // Deck mounts pass through the equipment lid and carry the above-core PCB.
        let deck_mount_type =
            rt.namedtuple("DeckMount", "points standoff seat screw seat_min", NAME)?;
        let mut deck_mounts = OMap::new();
        let mut deck_mount_vals = Dict::new();
        for (name, row) in mounts::deck_mounts(rt)?.iter() {
            deck_mount_vals.set(name.as_str(), deck_mount_type.c(row.fields.clone())?);
            deck_mounts.set(name, row.clone());
        }
        let lid_stack = b.foam_cap_lid_height + b.cap_lid_clearance;
        let reach = |m: &mounts::DeckMount| {
            let mut over = m.seat;
            if m.standoff == 0.0 {
                over += lid_stack;
            }
            m.screw - over
        };
        let deepest = deck_mounts
            .values()
            .map(|m| m.screw - m.seat_min - if m.standoff == 0.0 { lid_stack } else { 0.0 })
            .reduce(pmax)
            .unwrap_or(0.0);
        let deck_mount_bore_depth = pmax(
            b.deck_mount_insert_length + b.deck_mount_bore_relief,
            deepest + b.deck_mount_bore_relief,
        );
        let mount_reach = bound.c(args![
            "deck-mount-reach",
            "Every deck mount's screw reaches the whole of its insert",
            format!("{} mm into the column", ff(b.deck_mount_insert_length, "g"))
        ])?;
        let mut last_name = "lid_attachment_xy_positions".to_owned();
        for (name, m) in deck_mounts.iter() {
            let fields = &m.fields;
            mount_reach.c(args![
                reach(m) >= b.deck_mount_insert_length,
                format!(
                    "deck mount {name}: an M3 × {} through {} mm of seat reaches {} mm into the column, short of its {} mm insert",
                    fv(&fields[3], "g")?,
                    fv(&fields[2], "g")?,
                    ff(reach(m), "g"),
                    ff(b.deck_mount_insert_length, "g")
                )
            ])?;
            last_name = name.to_owned();
        }

        // Horizontal valve cradles: the current cap has none.
        let cradle_type = rt.namedtuple("Cradle", "centre yaw seat", NAME)?;
        let cradle_vals = [
            "corner_inset_x",
            "corner_inset_y",
            "socket_radius",
            "wall",
            "boss_radius",
            "seat_half_x",
            "seat_half_y",
            "seat_corner_radius",
        ]
        .map(|name| valve_seat.a(name));
        let [c0, c1, c2, c3, c4, c5, c6, c7] = cradle_vals;
        let cradle_vals = [c0?, c1?, c2?, c3?, c4?, c5?, c6?, c7?];
        let cv = |i: usize| cradle_vals[i].f();

        // Cap conduits.
        let lldpe_tube_od = 6.35;
        let cap_conduit_bore_radius = b.port_hole_radius;
        let mut cap_conduit_bore_radii = OMap::new();
        cap_conduit_bore_radii.set("reservoir-a-fill", 5.5);
        let cap_conduit_wall = b.wall_thickness;
        let cap_conduit_boss_radius = cap_conduit_bore_radius + cap_conduit_wall;
        let cap_conduit_lid_slip = b.deck_mount_lid_slip;
        let cap_conduit_entry_skew = 38.0;
        let cap_conduit_entry_relief_radius = cap_conduit_bore_radius
            + b.wall_and_floor_thickness * radians(cap_conduit_entry_skew).tan();
        let cap_conduit_entry_skew_ceiling =
            degrees(cap_conduit_wall.atan2(b.wall_and_floor_thickness));
        let across = lldpe_tube_od / radians(cap_conduit_entry_skew).cos();
        call_state(
            &stated,
            args![
                "entry-passes-section",
                "The countersink's mouth passes the leaning tube's whole section",
                format!("⌀{} across the face", ff(across, ".2f")),
                cap_conduit_entry_relief_radius
                    >= (0.5 * lldpe_tube_od / radians(cap_conduit_entry_skew).cos() - 1e-9),
                format!(
                    "cap conduit entry: a ⌀{} line leaning {}° reads {} mm across the lid's face, over the ⌀{} the relief opens to",
                    ff(lldpe_tube_od, "g"),
                    ff(cap_conduit_entry_skew, "g"),
                    ff(across, ".2f"),
                    ff(2.0 * cap_conduit_entry_relief_radius, ".2f")
                )
            ],
        )?;
        let co2_lane_x = 48.0;
        let co2_cap_x = mounts::gas_guide_xy(rt)?[0];
        let water_outlet_climb_x = -48.5;
        let water_outlet_upper_climb_x = -35.0;
        let water_outlet_drift_z = (b.evap_tail_low_z + lldpe_tube_od + 2.0, 140.0);
        let reed_cable_conduit_x = b.reed_column_axis_x;
        let reed_cable_conduit_y = b.level_rod_y;
        let reed_xy = |side: f64| [-side * reed_cable_conduit_x, -reed_cable_conduit_y];
        let fill = |side: i64| -> Result<[f64; 2]> {
            let xy = b.reservoir_fill_port.side(side)?;
            Ok([-xy[0], -xy[1]])
        };
        let draw = |side: i64| -> Result<[f64; 2]> {
            let xy = b.reservoir_draw_port.side(side)?;
            Ok([-xy[0], -xy[1]])
        };
        let mut cap_fluid_conduits = OMap::new();
        cap_fluid_conduits.set(
            "water-in",
            mounts::cap_guide_xy(rt, "water-in", [86.2532889963965, 32.80179966121266])?,
        );
        cap_fluid_conduits.set("reservoir-a", draw(1)?);
        cap_fluid_conduits.set("reservoir-b", mounts::cap_guide_xy(rt, "B-draw", draw(-1)?)?);
        cap_fluid_conduits.set(
            "reservoir-a-fill",
            mounts::cap_guide_xy(rt, "A-fill", fill(1)?)?,
        );
        cap_fluid_conduits.set("reservoir-b-fill", fill(-1)?);
        cap_fluid_conduits.set(
            "carb-water-out",
            mounts::cap_guide_xy(rt, "carb-water-out", [52.2, -b.port_lane_mid_y])?,
        );
        cap_fluid_conduits.set("co2-in", mounts::gas_guide_xy(rt)?);
        let mut cap_cable_floor_conduits = OMap::new();
        cap_cable_floor_conduits.set("reed-cable-a", reed_xy(1.0));
        cap_cable_floor_conduits.set("sensor-cable", [-23.2, -48.0]);
        let mut cap_cable_conduits = OMap::new();
        for (name, xy) in cap_cable_floor_conduits.iter() {
            cap_cable_conduits.set(name, mounts::cap_guide_xy(rt, name, *xy)?);
        }
        let mut cap_conduits = cap_fluid_conduits.clone();
        for (name, xy) in cap_cable_conduits.iter() {
            cap_conduits.set(name, *xy);
        }
        let mut cap_conduit_floor_xy = cap_conduits.clone();
        for (name, xy) in cap_cable_floor_conduits.iter() {
            cap_conduit_floor_xy.set(name, *xy);
        }
        cap_conduit_floor_xy.set("water-in", mounts::water_in_floor_xy(rt)?);
        cap_conduit_floor_xy.set("reservoir-b", draw(-1)?);
        cap_conduit_floor_xy.set("reservoir-a-fill", fill(1)?);
        cap_conduit_floor_xy.set("reservoir-b-fill", fill(-1)?);
        cap_conduit_floor_xy.set("carb-water-out", *cap_conduits.at("carb-water-out")?);
        let cap_passive_guides = vec!["reservoir-a-fill".to_owned()];
        let cap_cable_guides: Vec<String> = cap_cable_conduits.keys().map(str::to_owned).collect();
        let cap_conduit_links: Vec<(String, String)> = vec![];
        let cap_conduit_link_width = 5.0;
        let fill_conduits: Vec<String> = cap_conduits
            .keys()
            .filter(|n| n.ends_with("-fill"))
            .map(str::to_owned)
            .collect();
        let mut fill_wanted: Vec<String> = vec![];
        for s in b.reservoir_fill_sides {
            let name = format!("reservoir-{}-fill", if s < 0 { 'b' } else { 'a' });
            if !fill_wanted.contains(&name) {
                fill_wanted.push(name);
            }
        }
        fn sorted(items: &[String]) -> Vec<&str> {
            let mut v: Vec<&str> = items.iter().map(String::as_str).collect();
            v.sort();
            v
        }
        let same = fill_conduits.len() == fill_wanted.len()
            && fill_conduits.iter().all(|n| fill_wanted.contains(n));
        call_state(
            &stated,
            args![
                "fill-conduits-paired",
                "Every fill bore has a conduit over it and every conduit a bore",
                format!("the cap's fills naming {}", repr_strs(sorted(&fill_wanted))),
                same,
                format!(
                    "reservoir fills: {} stand on the cap, but `reservoir_fill_sides` cuts ({}, {}) — a conduit with no bore under it is a hole into a sealed pocket, and a bore with no conduit over it is a blind one",
                    repr_strs(sorted(&fill_conduits)),
                    b.reservoir_fill_sides[0],
                    b.reservoir_fill_sides[1]
                )
            ],
        )?;
        let carbonator_top_plate_z = b.wall_and_floor_thickness
            + b.carbonator_support_ring_height
            + carbonator_height.f()?;
        let top_band_to_cap =
            b.foam_shell_outer_height - (carbonator_top_plate_z + b.hole_shift_from_edge);
        let lldpe_bend_radius = 4.0 * lldpe_tube_od;
        let conduit_wall = bound.c(args![
            "cap-conduit-wall",
            "Every conduit column stands the pour gap off the wall or merges in",
            format!("the pour gap apart or a {} mm neck", ff(cap_conduit_wall, "g"))
        ])?;
        for (name, xy) in cap_conduits.iter() {
            let (neck, what) = wall_neck(&b, cap_conduit_boss_radius, cap_conduit_bore_radius, xy[0], xy[1]);
            let want = if what.starts_with("the pour") {
                b.deck_mount_cap_gap
            } else {
                cap_conduit_wall
            };
            conduit_wall.c(args![
                neck >= want - 1e-9,
                format!(
                    "cap conduit {name}: {what} is {} mm, under the {} mm it takes — a column either stands the pour gap off the wall or merges into it",
                    ff(neck, ".3f"),
                    ff(want, "g")
                )
            ])?;
            last_name = name.to_owned();
        }
        let cap_cradle_room_gap = 1.0;
        let cradle_room = bound.c(args![
            "cradle-room",
            "Every plinth clears the other openings on the lid",
            format!("{} mm off the nearest", ff(cap_cradle_room_gap, "g"))
        ])?;
        let anchor_type =
            rt.namedtuple("CapAnchor", "centre seat_r over_face along closure", NAME)?;
        anchor_type
            .a("__new__")?
            .setattr("__defaults__", (Val::None, "x", "tie").to_val())?;
        let cap_anchor_tie_w = 2.5;
        let cap_anchor_cav_buffer = 2.0 * fits.a("slip")?.f()?;
        let cap_anchor_cav_w = cap_anchor_tie_w + cap_anchor_cav_buffer;
        let cap_anchor_cav_wall = 3.0;
        let cap_anchor_len = cap_anchor_cav_w + 2.0 * cap_anchor_cav_wall;
        let cap_anchor_wall = cv(3)?;
        let cap_anchor_channel_height = cap_anchor_wall + fits.a("supported_surface")?.f()?;
        let anchor_room = bound.c(args![
            "anchor-room",
            "Every chain anchor stands its room off everything else the face opens",
            format!("{} mm off the nearest", ff(cap_cradle_room_gap, "g"))
        ])?;
        let side_anchor_type =
            rt.namedtuple("SideAnchor", "centre over_face seat_r axis_off depth", NAME)?;
        let cap_side_wall = cap_anchor_wall;
        let cap_side_len = cap_anchor_len;
        let cap_side_cav_w = cap_anchor_cav_w;
        let cap_side_flank = (cap_side_len - cap_side_cav_w) / 2.0;
        let side_anchor_room = bound.c(args![
            "cap-side-anchor-room",
            "Every side post stands clear of what the lid's face opens",
            format!("{} mm off the nearest", ff(cap_cradle_room_gap, "g"))
        ])?;
        let pair_neck_bound = bound.c(args![
            "cap-conduit-pair",
            "Every pair of conduits stands apart or merges on a neck, never tangent",
            format!("the pour gap apart or a {} mm neck", ff(cap_conduit_wall, "g"))
        ])?;
        let mut names: Vec<&str> = cap_conduits.keys().collect();
        names.sort();
        let mut last_pair = None;
        for i in 0..names.len() {
            for j in i + 1..names.len() {
                let (a, bn) = (names[i], names[j]);
                let (neck, what) = pair_neck(
                    cap_conduit_boss_radius,
                    &cap_conduit_links,
                    &cap_conduits,
                    cap_conduit_link_width,
                    *cap_conduits.at(a)?,
                    *cap_conduits.at(bn)?,
                )?;
                let want = if what.starts_with("the pour") {
                    b.deck_mount_cap_gap
                } else {
                    cap_conduit_wall
                };
                pair_neck_bound.c(args![
                    neck >= want - 1e-9,
                    format!(
                        "cap conduits {a} and {bn}: {what} is {} mm, under the {} mm it takes — a pair either stands the pour gap apart or merges on a neck a wall thick",
                        ff(neck, ".3f"),
                        ff(want, "g")
                    )
                ])?;
                last_pair = Some((a.to_owned(), bn.to_owned(), neck, what, want));
            }
        }
        Ok(Self {
            base: b.clone(),
            here,
            fits,
            valve_seat,
            stated,
            enclosure,
            anchor_cap,
            carbonator_outer_radius,
            carbonator_height,
            read,
            interface_fits,
            base_recipe,
            base_states,
            last_row,
            deck_mount_type,
            deck_mounts,
            deck_mount_vals: deck_mount_vals.val(),
            deck_mount_bore_depth,
            mount_reach,
            cradle_type,
            cap_cradles: OMap::new(),
            cap_cradle_corner_inset_x: cv(0)?,
            cap_cradle_corner_inset_y: cv(1)?,
            cap_cradle_socket_radius: cv(2)?,
            cap_cradle_wall: cv(3)?,
            cap_cradle_boss_radius: cv(4)?,
            cap_cradle_half_x: cv(5)?,
            cap_cradle_half_y: cv(6)?,
            cap_cradle_corner_radius: cv(7)?,
            cradle_vals: cradle_vals.clone(),
            cap_cradle_room_gap,
            lldpe_tube_od,
            cap_conduit_bore_radius,
            cap_conduit_bore_radii,
            cap_conduit_wall,
            cap_conduit_boss_radius,
            cap_conduit_lid_slip,
            cap_conduit_entry_skew,
            cap_conduit_entry_relief_radius,
            cap_conduit_entry_skew_ceiling,
            co2_lane_x,
            co2_cap_x,
            water_outlet_climb_x,
            water_outlet_upper_climb_x,
            water_outlet_drift_z,
            reed_cable_conduit_x,
            reed_cable_conduit_y,
            cap_fluid_conduits,
            cap_cable_floor_conduits,
            cap_cable_conduits,
            cap_conduits,
            cap_conduit_floor_xy,
            cap_passive_guides,
            cap_cable_guides,
            cap_conduit_links,
            cap_conduit_link_width,
            fill_conduits,
            fill_wanted,
            carbonator_top_plate_z,
            top_band_to_cap,
            lldpe_bend_radius,
            conduit_wall,
            cradle_room,
            anchor_type,
            cap_anchors: OMap::new(),
            cap_anchor_tie_w,
            cap_anchor_cav_buffer,
            cap_anchor_cav_w,
            cap_anchor_cav_wall,
            cap_anchor_len,
            cap_anchor_wall,
            cap_anchor_channel_height,
            anchor_room,
            side_anchor_type,
            cap_side_wall,
            cap_side_len,
            cap_side_cav_w,
            cap_side_flank,
            cap_side_tie_t: 1.0,
            cap_side_cav_h: cap_side_wall,
            cap_side_cav_backing_min: 1.0,
            cap_side_back_relief: 1.2,
            cap_side_web: cap_side_wall,
            cap_side_anchors: OMap::new(),
            side_anchor_room,
            pair_neck: pair_neck_bound,
            last_name,
            last_pair,
        })
    }
}

impl State {
    /// `reservoir_fill_conduit_xy(side)`: the fill conduit in the cap frame.
    pub fn reservoir_fill_conduit_xy(&self, side: i64) -> Result<[f64; 2]> {
        let xy = self.base.reservoir_fill_port.side(side)?;
        Ok([-xy[0], -xy[1]])
    }
    /// `reservoir_draw_conduit_xy(side)`.
    pub fn reservoir_draw_conduit_xy(&self, side: i64) -> Result<[f64; 2]> {
        let xy = self.base.reservoir_draw_port.side(side)?;
        Ok([-xy[0], -xy[1]])
    }
    fn mount(&self, name: &str) -> Result<&mounts::DeckMount> {
        self.deck_mounts.at(name)
    }
    /// `deck_mount_xy(name)`: the selected boss centres, sorted and without repeats.
    pub fn deck_mount_xy(&self, name: &str) -> Result<Vec<[f64; 2]>> {
        let mut unique: Vec<[f64; 2]> = vec![];
        for p in &self.mount(name)?.points {
            if !unique.iter().any(|q| q[0] == p[0] && q[1] == p[1]) {
                unique.push(*p);
            }
        }
        unique.sort_by(|a, b| {
            a[0].partial_cmp(&b[0])
                .unwrap_or(std::cmp::Ordering::Equal)
                .then(a[1].partial_cmp(&b[1]).unwrap_or(std::cmp::Ordering::Equal))
        });
        Ok(unique)
    }
    pub fn deck_mount_standoff(&self, name: &str) -> Result<f64> {
        Ok(self.mount(name)?.standoff)
    }
    pub fn deck_mount_proud(&self) -> Result<f64> {
        Ok(self
            .deck_mounts
            .values()
            .map(|m| m.standoff)
            .reduce(pmax)
            .unwrap_or(0.0))
    }
    /// `deck_mount_reach(name)`: how far a seated screw runs past this mount's column top.
    pub fn deck_mount_reach(&self, name: &str) -> Result<f64> {
        let m = self.mount(name)?;
        let mut over = m.seat;
        if m.standoff == 0.0 {
            over += self.base.foam_cap_lid_height + self.base.cap_lid_clearance;
        }
        Ok(m.screw - over)
    }
    /// `deck_lid_hole_radius(name)`.
    pub fn deck_lid_hole_radius(&self, name: &str) -> Result<f64> {
        if self.deck_mount_standoff(name)? == 0.0 {
            return Ok(self.base.screw_clearance_radius);
        }
        Ok(self.base.deck_mount_boss_radius + self.base.deck_mount_lid_slip)
    }
    fn cradle(&self, name: &str) -> Result<&Cradle> {
        self.cap_cradles.at(name)
    }
    pub fn cap_cradle_xy(&self, name: &str) -> Result<Vec<[f64; 2]>> {
        let station = self.cradle(name)?;
        let [cx, cy] = station.centre;
        let th = radians(station.yaw + 90.0);
        let (c, s) = (th.cos(), th.sin());
        let mut out = vec![];
        for sx in [-1.0, 1.0] {
            for sy in [-1.0, 1.0] {
                out.push([
                    cx + c * sx * self.cap_cradle_corner_inset_x
                        - s * sy * self.cap_cradle_corner_inset_y,
                    cy + s * sx * self.cap_cradle_corner_inset_x
                        + c * sy * self.cap_cradle_corner_inset_y,
                ]);
            }
        }
        Ok(out)
    }
    pub fn cap_cradle_half_extents(&self, name: &str) -> Result<[f64; 2]> {
        let th = radians(self.cradle(name)?.yaw + 90.0);
        let (c, s) = (th.cos().abs(), th.sin().abs());
        Ok([
            c * self.cap_cradle_half_x + s * self.cap_cradle_half_y,
            s * self.cap_cradle_half_x + c * self.cap_cradle_half_y,
        ])
    }
    pub fn cap_cradle_circle_gap(&self, name: &str, x: f64, y: f64, radius: f64) -> Result<f64> {
        let station = self.cradle(name)?;
        let [cx, cy] = station.centre;
        let th = radians(station.yaw + 90.0);
        let (dx, dy) = (x - cx, y - cy);
        let px = (th.cos() * dx + th.sin() * dy).abs();
        let py = (-th.sin() * dx + th.cos() * dy).abs();
        let qx = px - (self.cap_cradle_half_x - self.cap_cradle_corner_radius);
        let qy = py - (self.cap_cradle_half_y - self.cap_cradle_corner_radius);
        Ok(hypot(&[pmax(qx, 0.0), pmax(qy, 0.0)]) + pmin(pmax(qx, qy), 0.0)
            - self.cap_cradle_corner_radius
            - radius)
    }
    pub fn cap_cradle_rectangle_gap(&self, name: &str, x0: f64, x1: f64, y0: f64, y1: f64) -> Result<f64> {
        let station = self.cradle(name)?;
        let [cx, cy] = station.centre;
        ensure!(
            isclose(pymod(station.yaw, 90.0), 0.0),
            "plinth rectangle reading needs an axial station"
        );
        let [hx, hy] = self.cap_cradle_half_extents(name)?;
        let (core_x, core_y) = (
            hx - self.cap_cradle_corner_radius,
            hy - self.cap_cradle_corner_radius,
        );
        let dx = fmax([x0 - (cx + core_x), (cx - core_x) - x1, 0.0]);
        let dy = fmax([y0 - (cy + core_y), (cy - core_y) - y1, 0.0]);
        Ok(hypot(&[dx, dy]) - self.cap_cradle_corner_radius)
    }
    /// `cap_cradle_room(name)`: `(mm, what)`.
    pub fn cap_cradle_room(&self, name: &str) -> Result<(f64, String)> {
        let b = &self.base;
        let mut room: Vec<(f64, String)> = vec![];
        for (cname, xy) in self.cap_conduits.iter() {
            let gap = self.cap_cradle_circle_gap(name, xy[0], xy[1], self.cap_conduit_entry_relief_radius)?;
            room.push((pmax(gap, self.cap_cradle_room_gap), format!("the {cname} conduit passage")));
        }
        for xy in &b.attachment_xy_positions {
            room.push((
                self.cap_cradle_circle_gap(name, xy[0], xy[1], b.head_cbore_radius)?,
                "a clamp screw's counterbore".into(),
            ));
        }
        for dname in self.deck_mounts.keys() {
            for xy in self.deck_mount_xy(dname)? {
                room.push((
                    self.cap_cradle_circle_gap(name, xy[0], xy[1], self.deck_lid_hole_radius(dname)?)?,
                    format!("the {dname} mount's lid hole"),
                ));
            }
        }
        let [cx, cy] = self.cradle(name)?.centre;
        let [hx, hy] = self.cap_cradle_half_extents(name)?;
        room.push((
            pmin(
                b.outer_shell_x_length / 2.0 - cx.abs() - hx,
                b.outer_shell_y_length / 2.0 - cy.abs() - hy,
            ),
            "the lid's own edge".into(),
        ));
        for (other, station) in self.cap_cradles.iter() {
            if other == name {
                continue;
            }
            let [ox, oy] = station.centre;
            let [ohx, ohy] = self.cap_cradle_half_extents(other)?;
            room.push((
                self.cap_cradle_rectangle_gap(name, ox - ohx, ox + ohx, oy - ohy, oy + ohy)?,
                format!("the {other} plinth"),
            ));
        }
        least(room)
    }
    /// `reed_cable_conduit_xy(side)`.
    pub fn reed_cable_conduit_xy(&self, side: f64) -> [f64; 2] {
        [-side * self.reed_cable_conduit_x, -self.reed_cable_conduit_y]
    }
    /// `cap_conduit_wall_neck(x, y)`: `(mm, what)`.
    pub fn cap_conduit_wall_neck(&self, x: f64, y: f64) -> (f64, &'static str) {
        wall_neck(&self.base, self.cap_conduit_boss_radius, self.cap_conduit_bore_radius, x, y)
    }
    /// `foam_cap_lid_pour_xy(top)`: the top lid's fore-west pour station, or the bottom lid's.
    pub fn foam_cap_lid_pour_xy(&self, top: bool) -> Result<[f64; 2]> {
        let b = &self.base;
        if top {
            return Ok(b.top_lid_pour_xy);
        }
        let x = b.outer_shell_x_length / 2.0 - b.foam_cap_lid_hole_inset;
        let mut bands: Vec<[f64; 2]> = vec![];
        let mut fence = |sx: f64, sy: f64, need: f64| {
            let reach = need.powf(2.0) - (x - sx).powf(2.0);
            if reach > 0.0 {
                let half = reach.sqrt();
                bands.push([sy - half, sy + half]);
            }
        };
        for name in self.deck_mounts.keys() {
            for [sx, sy] in self.deck_mount_xy(name)? {
                fence(
                    sx,
                    sy,
                    b.foam_cap_lid_pour_radius + b.screw_clearance_radius + b.deck_mount_cap_gap,
                );
            }
        }
        for (name, station) in self.cap_cradles.iter() {
            ensure!(isclose(pymod(station.yaw, 90.0), 0.0), "AssertionError");
            let [cx, cy] = station.centre;
            let [hx, hy] = self.cap_cradle_half_extents(name)?;
            let (core_x, core_y) = (
                hx - self.cap_cradle_corner_radius,
                hy - self.cap_cradle_corner_radius,
            );
            let reach = b.foam_cap_lid_pour_radius + b.deck_mount_cap_gap + self.cap_cradle_corner_radius;
            let dx = pmax((x - cx).abs() - core_x, 0.0);
            if dx < reach {
                let half = core_y + (reach * reach - dx * dx).sqrt();
                bands.push([cy - half, cy + half]);
            }
        }
        bands.sort_by(|a, b| {
            a[0].partial_cmp(&b[0])
                .unwrap_or(std::cmp::Ordering::Equal)
                .then(a[1].partial_cmp(&b[1]).unwrap_or(std::cmp::Ordering::Equal))
        });
        let mut merged: Vec<[f64; 2]> = vec![];
        for [lo, hi] in bands {
            if let Some(last) = merged.last_mut().filter(|last| lo <= last[1]) {
                last[1] = pmax(last[1], hi);
            } else {
                merged.push([lo, hi]);
            }
        }
        let mut y = 0.0;
        for [lo, hi] in merged {
            if lo < y && y < hi {
                y = if (y - lo) <= (hi - y) { lo } else { hi };
                break;
            }
        }
        Ok([x, y])
    }
    /// `foam_cap_lid_vent_xy(top)`: both vent holes' centres in the lid.
    pub fn foam_cap_lid_vent_xy(&self, top: bool) -> [[f64; 2]; 2] {
        let b = &self.base;
        let x = -(b.outer_shell_x_length / 2.0 - b.foam_cap_lid_hole_inset
            + if top { b.top_lid_vent_setback } else { 0.0 });
        let y = b.outer_shell_y_length / 2.0 - b.foam_cap_lid_hole_inset;
        [[x, y], [x, -y]]
    }
    fn anchor(&self, name: &str) -> Result<&CapAnchor> {
        self.cap_anchors.at(name)
    }
    /// `cap_anchor_axis_over_face(name)`.
    pub fn cap_anchor_axis_over_face(&self, name: &str) -> Result<f64> {
        let row = self.anchor(name)?;
        let least = row.seat_r
            + self.cap_anchor_wall
            + if row.closure == "cap" {
                0.0
            } else {
                self.cap_anchor_channel_height
            };
        match row.over_face {
            None => Ok(least),
            Some(stated) if stated < least - 1e-9 => bail!(
                "cap_anchor_axis_over_face: {name} states {} mm over the lid's face and the rib's own layers come to {}. A seat lower than that stands the body on the lid or on its own zip tie.",
                ff(stated, ".3f"),
                ff(least, ".3f")
            ),
            Some(stated) => Ok(stated),
        }
    }
    /// `cap_anchor_tie_loop(name)`: the shortest zip tie closing round body and rib.
    pub fn cap_anchor_tie_loop(&self, rt: &Runtime, name: &str) -> Result<f64> {
        let r = self.anchor(name)?.seat_r;
        let (w, h);
        if name == "discharge-chain" {
            let data = mounts::check_support_datums(rt)?;
            let w = data.half_width;
            let h = data.centre[2] - data.tie_route_z;
            return Ok(w + h + (w * w - r * r).sqrt() + (h * h - r * r).sqrt()
                + r * (1.5 * std::f64::consts::PI - (r / w).acos() - (r / h).acos()));
        } else {
            w = r + self.cap_anchor_wall;
            h = self.cap_anchor_axis_over_face(name)? - self.cap_anchor_channel_height;
        }
        Ok(2.0 * w + 2.0 * h + 2.0 * (w * w - r * r).sqrt()
            + r * (std::f64::consts::PI - 2.0 * (r / w).acos()))
    }
    /// `cap_anchor_slotted(name)`.
    pub fn cap_anchor_slotted(&self, name: &str) -> Result<bool> {
        if self.anchor(name)?.closure != "cap" {
            return Ok(false);
        }
        Ok(self.cap_anchor_axis_over_face(name)?
            < self.anchor_cap.a("SLOT_TOP")?.f()? - self.anchor_cap.a("HEADROOM")?.f()? / 2.0)
    }
    /// `cap_anchor_room(name)`: `(mm, what)`.
    pub fn cap_anchor_room(&self, name: &str) -> Result<(f64, String)> {
        let b = &self.base;
        let row = self.anchor(name)?;
        let [cx, cy] = row.centre;
        let (length, reach) = if row.closure == "cap" {
            let slot = if self.cap_anchor_slotted(name)? {
                self.anchor_cap.a("SLOT_W")?.f()?
            } else {
                0.0
            };
            (
                self.anchor_cap.a("RIB_LEN")?.f()?,
                self.anchor_cap.a("RIB_R")?.f()? + slot,
            )
        } else {
            (self.cap_anchor_len, row.seat_r + self.cap_anchor_wall)
        };
        let (along, across) = if row.along == "x" {
            (length / 2.0, reach)
        } else {
            (reach, length / 2.0)
        };
        let (x0, x1) = (cx - along, cx + along);
        let (y0, y1) = (cy - across, cy + across);
        let off = |px: f64, py: f64, r: f64| {
            let dx = fmax([x0 - px, 0.0, px - x1]);
            let dy = fmax([y0 - py, 0.0, py - y1]);
            hypot(&[dx, dy]) - r
        };
        let mut room: Vec<(f64, String)> = vec![];
        for (cname, [bx, by]) in self.cap_conduits.iter() {
            room.push((
                off(*bx, *by, self.cap_conduit_entry_relief_radius),
                format!("the {cname} conduit's entry"),
            ));
        }
        for [bx, by] in &b.lid_attachment_xy_positions {
            room.push((off(*bx, *by, b.head_cbore_radius), "a clamp screw's counterbore".into()));
        }
        for dname in self.deck_mounts.keys() {
            for [dx, dy] in self.deck_mount_xy(dname)? {
                room.push((
                    off(dx, dy, self.deck_lid_hole_radius(dname)?),
                    format!("the {dname} mount's lid hole"),
                ));
            }
        }
        for vname in self.cap_cradles.keys() {
            room.push((
                self.cap_cradle_rectangle_gap(vname, x0, x1, y0, y1)?,
                format!("the {vname} plinth"),
            ));
        }
        room.push((
            fmin([
                b.outer_shell_x_length / 2.0 - x0.abs(),
                b.outer_shell_x_length / 2.0 - x1.abs(),
                b.outer_shell_y_length / 2.0 - y0.abs(),
                b.outer_shell_y_length / 2.0 - y1.abs(),
            ]),
            "the lid's own edge".into(),
        ));
        least(room)
    }
    fn side(&self, name: &str) -> Result<&SideAnchor> {
        self.cap_side_anchors.at(name)
    }
    pub fn cap_side_axis_y(&self, name: &str) -> Result<f64> {
        let a = self.side(name)?;
        Ok(a.centre[0] + a.axis_off)
    }
    pub fn cap_side_wrap_deg(&self, name: &str) -> Result<f64> {
        let a = self.side(name)?;
        Ok(2.0 * degrees((a.axis_off / a.seat_r).acos()))
    }
    pub fn cap_side_tunnel_roof(&self, name: &str) -> Result<f64> {
        let a = self.side(name)?;
        Ok(a.over_face - a.seat_r - self.cap_side_wall)
    }
    pub fn cap_side_tunnel_h(&self, name: &str) -> Result<f64> {
        let roof = self.cap_side_tunnel_roof(name)?;
        if roof - self.cap_side_cav_h >= self.cap_side_cav_backing_min - 1e-9 {
            return Ok(self.cap_side_cav_h);
        }
        Ok(roof)
    }
    pub fn cap_side_anchor_height(&self, name: &str) -> Result<f64> {
        let a = self.side(name)?;
        Ok(a.over_face + a.seat_r + self.fits.a("supported_surface")?.f()? + self.cap_side_wall)
    }
    pub fn cap_side_anchor_holds(&self, name: &str) -> Result<()> {
        let a = self.side(name)?;
        let roof = self.cap_side_tunnel_roof(name)?;
        if roof < self.cap_side_tie_t - 1e-9 {
            bail!(
                "cap_side_anchor_holds: {name} runs {} mm over the lid's face; the pipe takes {} of that and one wall {} more, leaving {} mm under it where the zip tie is {} thick. What gives way here is the run's own lane, not the lid: route it further off that face.",
                ff(a.over_face, ".3f"),
                ff(a.seat_r, ".3f"),
                ff(self.cap_side_wall, ".3f"),
                ff(roof, ".3f"),
                ff(self.cap_side_tie_t, "g")
            );
        }
        let web = a.depth + a.axis_off - a.seat_r - self.cap_side_back_relief;
        if web < self.cap_side_web - 1e-9 {
            bail!(
                "cap_side_anchor_holds: the post runs {} mm back from its face; the pipe takes {} of that and the tie's channel {} more, leaving a web of {} where this face wants {}. What caps the depth is the body behind the post, so what gives is the pipe or the lane — not the web.",
                ff(a.depth, ".3f"),
                ff(a.seat_r - a.axis_off, ".3f"),
                ff(self.cap_side_back_relief, "g"),
                ff(web, ".3f"),
                ff(self.cap_side_web, "g")
            );
        }
        Ok(())
    }
    pub fn cap_side_anchor_tie_loop(&self, name: &str) -> Result<f64> {
        let a = self.side(name)?;
        let w = a.seat_r + self.cap_side_wall;
        let tun_h = self.cap_side_tunnel_h(name)?;
        let axis = tun_h + w;
        let crown = tun_h + 2.0 * w;
        let d_lo = hypot(&[a.axis_off, axis]);
        let d_hi = hypot(&[a.axis_off, crown - axis]);
        let sweep = pymod(
            (crown - axis).atan2(-a.axis_off) - (-axis).atan2(-a.axis_off),
            2.0 * std::f64::consts::PI,
        );
        Ok(2.0 * a.depth
            + crown
            + (d_lo * d_lo - a.seat_r * a.seat_r).sqrt()
            + (d_hi * d_hi - a.seat_r * a.seat_r).sqrt()
            + a.seat_r * (sweep - (a.seat_r / d_lo).acos() - (a.seat_r / d_hi).acos()))
    }
    pub fn cap_side_anchor_room(&self, name: &str) -> Result<(f64, String)> {
        let b = &self.base;
        let a = self.side(name)?;
        let [cx, cy] = a.centre;
        let (x0, x1) = (cx - a.depth, cx);
        let (y0, y1) = (cy - self.cap_side_len / 2.0, cy + self.cap_side_len / 2.0);
        let off = |px: f64, py: f64, r: f64| {
            let dx = fmax([x0 - px, 0.0, px - x1]);
            let dy = fmax([y0 - py, 0.0, py - y1]);
            hypot(&[dx, dy]) - r
        };
        let mut room: Vec<(f64, String)> = vec![];
        for [bx, by] in &b.lid_attachment_xy_positions {
            room.push((off(*bx, *by, b.head_cbore_radius), "a clamp screw's counterbore".into()));
        }
        for (cname, [bx, by]) in self.cap_conduits.iter() {
            room.push((
                off(*bx, *by, self.cap_conduit_entry_relief_radius),
                format!("the {cname} conduit's entry"),
            ));
        }
        for dname in self.deck_mounts.keys() {
            for [dx, dy] in self.deck_mount_xy(dname)? {
                room.push((
                    off(dx, dy, self.deck_lid_hole_radius(dname)?),
                    format!("the {dname} mount's lid hole"),
                ));
            }
        }
        for vname in self.cap_cradles.keys() {
            room.push((
                self.cap_cradle_rectangle_gap(vname, x0, x1, y0, y1)?,
                format!("the {vname} plinth"),
            ));
        }
        for (aname, anchor) in self.cap_anchors.iter() {
            room.push((
                off(anchor.centre[0], anchor.centre[1], anchor.seat_r + self.cap_anchor_wall),
                format!("the {aname} rib"),
            ));
        }
        least(room)
    }
    /// `cap_conduit_pair_neck(a, b)`: `(mm, what)`.
    pub fn cap_conduit_pair_neck(&self, a: [f64; 2], b: [f64; 2]) -> Result<(f64, &'static str)> {
        pair_neck(
            self.cap_conduit_boss_radius,
            &self.cap_conduit_links,
            &self.cap_conduits,
            self.cap_conduit_link_width,
            a,
            b,
        )
    }
    /// `cap_conduits[name]`.
    pub fn cap_conduit(&self, name: &str) -> Result<[f64; 2]> {
        self.cap_conduits.at(name).copied()
    }
    /// `cap_conduit_floor_xy[name]`.
    pub fn cap_conduit_floor_xy(&self, name: &str) -> Result<[f64; 2]> {
        self.cap_conduit_floor_xy.at(name).copied()
    }
    /// `cap_conduit_shell_xy(name)`: the station in the shell's own frame.
    pub fn cap_conduit_shell_xy(&self, name: &str) -> Result<[f64; 2]> {
        let [x, y] = self.cap_conduit(name)?;
        Ok([-x, -y])
    }
    /// `cap_conduit_station(name)`.
    pub fn cap_conduit_station(&self, name: &str) -> Result<([f64; 3], [f64; 3])> {
        let [x, y] = self.cap_conduit(name)?;
        Ok(([x, y, 0.0], [0.0, 0.0, 1.0]))
    }
}

/// `min(rows)` over `(mm, what)` pairs, as Python compares tuples.
fn least(rows: Vec<(f64, String)>) -> Result<(f64, String)> {
    let mut it = rows.into_iter();
    let mut best = it.next().context("ValueError: min() arg is an empty sequence")?;
    for row in it {
        if row.0 < best.0 || (row.0 == best.0 && row.1 < best.1) {
            best = row;
        }
    }
    Ok(best)
}

/// `make_box(x_range, y_range, z_range)`: an axis-aligned box from world ranges.
pub fn make_box(rt: &Runtime, x: &[f64], y: &[f64], z: &[f64]) -> Result<Val> {
    let ww = rt.py("world_workplane")?;
    let (x_min, x_max) = (fmin(x.iter().copied()), fmax(x.iter().copied()));
    let (y_min, y_max) = (fmin(y.iter().copied()), fmax(y.iter().copied()));
    let (z_min, z_max) = (fmin(z.iter().copied()), fmax(z.iter().copied()));
    ww.a("WorldWorkplane")?
        .c(args![ww.a("xy_plane_z_up")?])?
        .mk("workplane", vec![], kw!["offset" => z_min])?
        .m("moveTo", args![((x_min + x_max) / 2.0, (y_min + y_max) / 2.0)])?
        .m("rect", args![x_max - x_min, y_max - y_min])?
        .m("extrude", args![z_max - z_min])?
        .m("unwrap", vec![])
}

/// `build_z_axis_hole_punch(*, origin, hole_punch_radius, hole_punch_height)`.
pub fn build_z_axis_hole_punch(rt: &Runtime, origin: &Val, radius: &Val, height: &Val) -> Result<Val> {
    let cq = Cq::new(rt)?;
    let plane = rt.pya("world_workplane", "xy_plane_z_up")?;
    let (x, y, z): (Val, Val, Val) = FromVal::from_val(origin)?;
    cq.workplane(args![plane], vec![])?
        .mk(
            "workplane",
            vec![],
            kw!["origin" => (x, y, 0i64), "offset" => z],
        )?
        .m("circle", args![radius])?
        .m("extrude", args![height])
}

/// The `if __name__ == "__main__":` block: the source's own doc comments.
pub fn main(rt: &Runtime) -> Result<()> {
    let s = state(rt)?;
    let b = &s.base;
    let tools = ancestor_where(&s.here, |p| p.join("tools").join("docgen").is_dir())?.join("tools");
    rt.sys_path_insert(0, &tools)?;
    let g = |x: f64| ff(x, ".4g");
    let variables: Vec<(String, String)> = [
        ("WALL_AND_FLOOR_THICKNESS", format!("{} mm", g(b.wall_and_floor_thickness))),
        ("COIL_RADIAL_CLEARANCE", format!("{} mm", g(b.coil_radial_clearance))),
        ("ABOVE_TANK_ELBOWS_HEIGHT", format!("{} mm", g(b.above_carbonator_elbows_height))),
        ("BELOW_TANK_ELBOWS_HEIGHT", format!("{} mm", g(b.below_carbonator_elbows_height))),
        ("PORT_HOLE_DIAMETER", g(b.port_hole_radius * 2.0)),
        ("SCREW_CLEARANCE_DIAMETER", g(b.screw_clearance_radius * 2.0)),
        ("INSERT_POCKET_DIAMETER", g(b.insert_pocket_radius * 2.0)),
        ("SCREW_BOSS_SIZE", format!("{} × {} mm", g(b.screw_boss_size), g(b.screw_boss_size))),
        ("SCREW_HEAD_H", format!("{} mm", g(b.screw_head_height))),
        ("HEAD_PAD_H", format!("{} mm", g(b.head_pad_height))),
        ("FOAM_CAP_LID_H", format!("{} mm", g(b.foam_cap_lid_height))),
        ("HEAD_CBORE_D", format!("{} mm", g(b.head_cbore_radius * 2.0))),
        ("CAP_SCREW_L", g(b.cap_screw_length)),
        ("DECK_MOUNT_CAP_GAP", format!("{} mm", g(b.deck_mount_cap_gap))),
        ("CARBONATOR_PORT_PITCH", format!("{}\"", g(2.0 * b.carbonator_port_offset / 25.4))),
        ("CARBONATOR_PORT_OFFSET", format!("{} mm", g(b.carbonator_port_offset))),
        ("LLDPE_BEND_R", format!("{} mm", g(s.lldpe_bend_radius))),
        ("FORWARD_BAND", format!("{} mm", g(b.forward_band_width))),
        ("LLDPE_TUBE_OD", g(s.lldpe_tube_od)),
        ("ENTRY_RELIEF_D", g(2.0 * s.cap_conduit_entry_relief_radius)),
        ("ENTRY_SKEW_CEILING", format!("{}°", g(s.cap_conduit_entry_skew_ceiling))),
        ("ANCHOR_LOOP", "none".to_owned()),
    ]
    .into_iter()
    .map(|(k, v)| (k.to_owned(), v))
    .collect();
    rt.substitute_py_comments(&rt.file(NAME), &variables, None)?;
    rt.print("-> _cold_core_interface.py (self)")
}


fn xy_tuple(points: &[[f64; 2]]) -> Val {
    Val::Tuple(points.iter().map(ToVal::to_val).collect())
}

fn room_val(room: (f64, String)) -> Val {
    (room.0, room.1).to_val()
}

/// The module's `__getattr__`: CadQuery and the world workplanes on first touch.
fn module_getattr(rt: &Runtime, name: &str) -> Result<Val> {
    if name == "cq" {
        return rt.py("cadquery");
    }
    if ["xy_plane_z_up", "xz_plane_y_up", "xz_plane_y_down", "WorldWorkplane"].contains(&name) {
        return rt.pya("world_workplane", name);
    }
    bail!("AttributeError: module '{NAME}' has no attribute '{name}'")
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    let b = s.base.clone();
    ns.module(rt, "itertools", "itertools")?;
    ns.module(rt, "math", "math")?;
    ns.module(rt, "sys", "sys")?;
    ns.value("namedtuple", rt.import_module("collections")?.a("namedtuple")?);
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("_here", Val::Path(s.here.clone()));
    ns.value("fits", s.fits.clone());
    ns.value("_valve_seat", s.valve_seat.clone());
    ns.module(rt, "_above_mounts", "_above_core_mounts")?;
    ns.value("bound", s.stated.a("bound")?);
    ns.value("state", s.stated.a("state")?);
    for (name, value) in ["manifold_rise", "inner_limb_drop", "rear_plane_y", "rear_seam_clear"]
        .iter()
        .zip(&s.enclosure)
    {
        ns.value(name, value.clone());
    }
    ns.value("_anchor_cap", s.anchor_cap.clone());
    ns.value("carbonator_outer_radius", s.carbonator_outer_radius.clone());
    ns.value("carbonator_height", s.carbonator_height.clone());
    ns.value("_read", s.read.clone());
    ns.value("_interface_fits", s.interface_fits.clone());
    ns.value("_base_recipe", s.base_recipe.clone());
    ns.value("_base_states", s.base_states.clone());
    for (name, value) in b.globals() {
        ns.value(name, value);
    }
    ns.value("_name", s.last_name.as_str());
    ns.value("_row", s.last_row.clone());
    ns.func(rt, "reservoir_fill_conduit_xy", |rt, c| {
        Ok(state(rt)?.reservoir_fill_conduit_xy(c.req(0, "side")?)?.to_val())
    });
    ns.func(rt, "reservoir_draw_conduit_xy", |rt, c| {
        Ok(state(rt)?.reservoir_draw_conduit_xy(c.req(0, "side")?)?.to_val())
    });
    ns.value("DeckMount", s.deck_mount_type.clone());
    ns.value("deck_mounts", s.deck_mount_vals.clone());
    ns.func(rt, "deck_mount_xy", |rt, c| {
        Ok(xy_tuple(&state(rt)?.deck_mount_xy(&c.req::<String>(0, "name")?)?))
    });
    ns.func(rt, "deck_mount_standoff", |rt, c| {
        let s = state(rt)?;
        Ok(s.mount(&c.req::<String>(0, "name")?)?.fields[1].clone())
    });
    ns.func(rt, "deck_mount_proud", |rt, _| Ok(state(rt)?.deck_mount_proud()?.to_val()));
    ns.func(rt, "deck_mount_reach", |rt, c| {
        Ok(state(rt)?.deck_mount_reach(&c.req::<String>(0, "name")?)?.to_val())
    });
    ns.value("deck_mount_bore_depth", s.deck_mount_bore_depth);
    ns.value("_mount_reach", s.mount_reach.clone());
    ns.func(rt, "deck_lid_hole_radius", |rt, c| {
        Ok(state(rt)?.deck_lid_hole_radius(&c.req::<String>(0, "name")?)?.to_val())
    });
    ns.value("Cradle", s.cradle_type.clone());
    ns.value("cap_cradles", Val::dict(vec![]));
    for (name, value) in [
        "cap_cradle_corner_inset_x",
        "cap_cradle_corner_inset_y",
        "cap_cradle_socket_radius",
        "cap_cradle_wall",
        "cap_cradle_boss_radius",
        "cap_cradle_half_x",
        "cap_cradle_half_y",
        "cap_cradle_corner_radius",
    ]
    .iter()
    .zip(&s.cradle_vals)
    {
        ns.value(name, value.clone());
    }
    ns.value("cap_cradle_room_gap", s.cap_cradle_room_gap);
    ns.func(rt, "cap_cradle_xy", |rt, c| {
        Ok(xy_tuple(&state(rt)?.cap_cradle_xy(&c.req::<String>(0, "name")?)?))
    });
    ns.func(rt, "cap_cradle_half_extents", |rt, c| {
        Ok(state(rt)?.cap_cradle_half_extents(&c.req::<String>(0, "name")?)?.to_val())
    });
    ns.func(rt, "cap_cradle_circle_gap", |rt, c| {
        let name = c.req::<String>(0, "name")?;
        let (x, y, r) = (c.req(1, "x")?, c.req(2, "y")?, c.req(3, "radius")?);
        Ok(state(rt)?.cap_cradle_circle_gap(&name, x, y, r)?.to_val())
    });
    ns.func(rt, "cap_cradle_rectangle_gap", |rt, c| {
        let name = c.req::<String>(0, "name")?;
        let (x0, x1) = (c.req(1, "x0")?, c.req(2, "x1")?);
        let (y0, y1) = (c.req(3, "y0")?, c.req(4, "y1")?);
        Ok(state(rt)?.cap_cradle_rectangle_gap(&name, x0, x1, y0, y1)?.to_val())
    });
    ns.func(rt, "cap_cradle_room", |rt, c| {
        Ok(room_val(state(rt)?.cap_cradle_room(&c.req::<String>(0, "name")?)?))
    });
    ns.value("lldpe_tube_od", s.lldpe_tube_od);
    ns.value("cap_conduit_bore_radius", s.cap_conduit_bore_radius);
    ns.value("cap_conduit_bore_radii", s.cap_conduit_bore_radii.to_val());
    ns.value("cap_conduit_wall", s.cap_conduit_wall);
    ns.value("cap_conduit_boss_radius", s.cap_conduit_boss_radius);
    ns.value("cap_conduit_lid_slip", s.cap_conduit_lid_slip);
    ns.value("cap_conduit_entry_skew", s.cap_conduit_entry_skew);
    ns.value("cap_conduit_entry_relief_radius", s.cap_conduit_entry_relief_radius);
    ns.value("cap_conduit_entry_skew_ceiling", s.cap_conduit_entry_skew_ceiling);
    ns.value("co2_lane_x", s.co2_lane_x);
    ns.value("co2_cap_x", s.co2_cap_x);
    ns.value("water_outlet_climb_x", s.water_outlet_climb_x);
    ns.value("water_outlet_upper_climb_x", s.water_outlet_upper_climb_x);
    ns.value("water_outlet_drift_z", s.water_outlet_drift_z);
    ns.value("reed_cable_conduit_x", s.reed_cable_conduit_x);
    ns.value("reed_cable_conduit_y", s.reed_cable_conduit_y);
    ns.func(rt, "reed_cable_conduit_xy", |rt, c| {
        Ok(state(rt)?.reed_cable_conduit_xy(c.req(0, "side")?).to_val())
    });
    ns.value("cap_fluid_conduits", s.cap_fluid_conduits.to_val());
    ns.value("cap_cable_floor_conduits", s.cap_cable_floor_conduits.to_val());
    ns.value("cap_cable_conduits", s.cap_cable_conduits.to_val());
    ns.value("cap_conduits", s.cap_conduits.to_val());
    ns.value("cap_conduit_floor_xy", s.cap_conduit_floor_xy.to_val());
    ns.value("cap_passive_guides", Val::Tuple(s.cap_passive_guides.iter().map(|n| n.to_val()).collect()));
    ns.value("cap_cable_guides", Val::Tuple(s.cap_cable_guides.iter().map(|n| n.to_val()).collect()));
    ns.value("cap_conduit_links", Val::Tuple(vec![]));
    ns.value("cap_conduit_link_width", s.cap_conduit_link_width);
    let set = |names: &[String]| Val::set_values(names.iter().map(|n| n.to_val()).collect());
    ns.value("_fill_conduits", set(&s.fill_conduits));
    ns.value("_fill_wanted", set(&s.fill_wanted));
    ns.value("carbonator_top_plate_z", s.carbonator_top_plate_z);
    ns.value("top_band_to_cap", s.top_band_to_cap);
    ns.value("lldpe_bend_radius", s.lldpe_bend_radius);
    ns.func(rt, "cap_conduit_wall_neck", |rt, c| {
        let (x, y) = (c.req(0, "x")?, c.req(1, "y")?);
        Ok(state(rt)?.cap_conduit_wall_neck(x, y).to_val())
    });
    ns.value("_conduit_wall", s.conduit_wall.clone());
    if let Some((_, _, neck, what, want)) = &s.last_pair {
        ns.value("_neck", *neck);
        ns.value("_what", *what);
        ns.value("_want", *want);
    }
    ns.func(rt, "foam_cap_lid_pour_xy", |rt, c| {
        let top = c.opt::<Val>(0, "top", Val::Bool(false))?.truthy()?;
        Ok(state(rt)?.foam_cap_lid_pour_xy(top)?.to_val())
    });
    ns.func(rt, "foam_cap_lid_vent_xy", |rt, c| {
        let top = c.opt::<Val>(0, "top", Val::Bool(false))?.truthy()?;
        Ok(state(rt)?.foam_cap_lid_vent_xy(top).to_val())
    });
    ns.value("_cradle_room", s.cradle_room.clone());
    ns.value("CapAnchor", s.anchor_type.clone());
    ns.value("cap_anchors", Val::dict(vec![]));
    ns.value("cap_anchor_tie_w", s.cap_anchor_tie_w);
    ns.value("cap_anchor_cav_buffer", s.cap_anchor_cav_buffer);
    ns.value("cap_anchor_cav_w", s.cap_anchor_cav_w);
    ns.value("cap_anchor_cav_wall", s.cap_anchor_cav_wall);
    ns.value("cap_anchor_len", s.cap_anchor_len);
    ns.value("cap_anchor_wall", s.cradle_vals[3].clone());
    ns.value("cap_anchor_channel_height", s.cap_anchor_channel_height);
    ns.func(rt, "cap_anchor_axis_over_face", |rt, c| {
        Ok(state(rt)?.cap_anchor_axis_over_face(&c.req::<String>(0, "name")?)?.to_val())
    });
    ns.func(rt, "cap_anchor_tie_loop", |rt, c| {
        Ok(state(rt)?.cap_anchor_tie_loop(rt, &c.req::<String>(0, "name")?)?.to_val())
    });
    ns.func(rt, "cap_anchor_slotted", |rt, c| {
        Ok(state(rt)?.cap_anchor_slotted(&c.req::<String>(0, "name")?)?.to_val())
    });
    ns.func(rt, "cap_anchor_room", |rt, c| {
        Ok(room_val(state(rt)?.cap_anchor_room(&c.req::<String>(0, "name")?)?))
    });
    ns.value("_anchor_room", s.anchor_room.clone());
    ns.value("SideAnchor", s.side_anchor_type.clone());
    ns.value("cap_side_wall", s.cradle_vals[3].clone());
    ns.value("cap_side_len", s.cap_side_len);
    ns.value("cap_side_cav_w", s.cap_side_cav_w);
    ns.value("cap_side_flank", s.cap_side_flank);
    ns.value("cap_side_tie_t", s.cap_side_tie_t);
    ns.value("cap_side_cav_h", s.cradle_vals[3].clone());
    ns.value("cap_side_cav_backing_min", s.cap_side_cav_backing_min);
    ns.value("cap_side_back_relief", s.cap_side_back_relief);
    ns.value("cap_side_web", s.cradle_vals[3].clone());
    ns.value("cap_side_anchors", Val::dict(vec![]));
    ns.func(rt, "cap_side_axis_y", |rt, c| {
        Ok(state(rt)?.cap_side_axis_y(&c.req::<String>(0, "name")?)?.to_val())
    });
    ns.func(rt, "cap_side_wrap_deg", |rt, c| {
        Ok(state(rt)?.cap_side_wrap_deg(&c.req::<String>(0, "name")?)?.to_val())
    });
    ns.func(rt, "cap_side_tunnel_roof", |rt, c| {
        Ok(state(rt)?.cap_side_tunnel_roof(&c.req::<String>(0, "name")?)?.to_val())
    });
    ns.func(rt, "cap_side_tunnel_h", |rt, c| {
        Ok(state(rt)?.cap_side_tunnel_h(&c.req::<String>(0, "name")?)?.to_val())
    });
    ns.func(rt, "cap_side_anchor_height", |rt, c| {
        Ok(state(rt)?.cap_side_anchor_height(&c.req::<String>(0, "name")?)?.to_val())
    });
    ns.func(rt, "cap_side_anchor_holds", |rt, c| {
        state(rt)?.cap_side_anchor_holds(&c.req::<String>(0, "name")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "cap_side_anchor_tie_loop", |rt, c| {
        Ok(state(rt)?.cap_side_anchor_tie_loop(&c.req::<String>(0, "name")?)?.to_val())
    });
    ns.func(rt, "cap_side_anchor_room", |rt, c| {
        Ok(room_val(state(rt)?.cap_side_anchor_room(&c.req::<String>(0, "name")?)?))
    });
    ns.value("_side_anchor_room", s.side_anchor_room.clone());
    ns.func(rt, "cap_conduit_pair_neck", |rt, c| {
        let (a, b) = (c.req(0, "a")?, c.req(1, "b")?);
        Ok(state(rt)?.cap_conduit_pair_neck(a, b)?.to_val())
    });
    ns.value("_pair_neck", s.pair_neck.clone());
    if let Some((a, b, _, _, _)) = &s.last_pair {
        ns.value("_a", a.as_str());
        ns.value("_b", b.as_str());
    }
    ns.func(rt, "cap_conduit_shell_xy", |rt, c| {
        Ok(state(rt)?.cap_conduit_shell_xy(&c.req::<String>(0, "name")?)?.to_val())
    });
    ns.value("cap_conduit_axis", (0.0, 0.0, 1.0));
    ns.func(rt, "cap_conduit_station", |rt, c| {
        Ok(state(rt)?.cap_conduit_station(&c.req::<String>(0, "name")?)?.to_val())
    });
    ns.func(rt, "make_box", |rt, c| {
        let x: Vec<f64> = c.req(0, "x_range")?;
        let y: Vec<f64> = c.req(1, "y_range")?;
        let z: Vec<f64> = c.req(2, "z_range")?;
        make_box(rt, &x, &y, &z)
    });
    ns.func(rt, "build_z_axis_hole_punch", |rt, c| {
        let origin = c.kw::<Val>("origin", (0i64, 0i64, 0i64).to_val())?;
        let radius = c.req::<Val>(usize::MAX, "hole_punch_radius")?;
        let height = c.kw::<Val>("hole_punch_height", Val::Int(40))?;
        build_z_axis_hole_punch(rt, &origin, &radius, &height)
    });
    ns.func(rt, "__getattr__", |rt, c| module_getattr(rt, &c.req::<String>(0, "name")?));
    Ok(())
}
