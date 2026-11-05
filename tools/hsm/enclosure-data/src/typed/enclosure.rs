//! Thin Edition enclosure — a tall, narrow PETG box, split into four printable
//! pieces (front/back × bottom/top) that telescope and pin together at two corner stacks.
//!
//! WIDTH, HEIGHT and DEPTH are all BOUNDS, not consequences — `appliance_width` struck
//! symmetric about x = 0, `appliance_height` from the floor slab's underside to the top
//! wall's outer face, and `rear_plane_y` fixing the back while the front wall reaches the
//! pump cradle's plane from its interior datum. The contents do
//! not set them; they have to fit inside, and `_dims` measures every one of them against
//! the pack and enters the reading in `BOUNDS`. The box comes out at its stated size
//! either way, so a pack that overran it gets a wall drawn through it.
//!
//! Three bodies stand on the floor slab — the compressor and the condenser side by side
//! across the front, and the cold core behind them. The Y seam's corner stacks occupy its
//! overlap in Y, the lower from the handhold ceiling to the Z seam and
//! the upper from over the tap-water line to the roof. A body is held one `side_band_inset`
//! off the wall where it meets their footprint in Y and Z; outside that footprint the band is
//! the wall's own air. The cold core meets the lower stack and is held off it; the compressor
//! stands under the front column and the condenser is not on the slab at all. The core is the widest of the three
//! even yawed a quarter turn (`enclosure_assembly.FOAM_YAW`), which is what puts its 181 mm
//! short face across the machine instead of its 283 mm long one. The pack is placed by
//! `../../../manifold-layout/enclosure_assembly.py`. Features:
//!
//!   * A 30° machine-display plane between tangent front and roof curves. Rounded
//!     side edges meet the fluted walls; the rear top edge remains square. The
//!     rounded bezel snaps into the recessed plane, ahead of the inset funnel.
//!   * A front↔back split at the stated `y_seam`, so its machinery is aft of the
//!     front pack and a front-quadrant tray never has to be notched around it:
//!     the front pieces' aft walls telescope (a full-wall lip,
//!     nothing shaved) into the back pieces — a proud tongue on the side walls and
//!     ceiling, and on the floor, where the cold core rides the cavity side and a
//!     proud tongue cannot, a full-thickness tongue that ends square inside the slab
//!     (`_floor_tongue`). Each ±X corner of the seam is a STACK of knuckles that
//!     alternate between the front and back pieces, sliding past one another as
//!     the halves telescope, held by two vertical M5 rods: the lower driven up
//!     from the handhold ceiling through front-bottom's knuckle into an insert in
//!     back-bottom's knuckle under the Z seam, the upper down from back-top's
//!     roof into an insert in front-top's knuckle under the funnel frame. Each
//!     ordinary screw seats its head on a printed floor and runs in an as-printed
//!     clearance passage (`_y_stacks`).
//!   * A bottom↔top split per column that SLIDES HOME and takes no screw, at ONE
//!     stated height both sides of the Y seam (`z_seam`, one level line round the
//!     box). The BOTTOM pieces carry the lip — a 3-sided band, their outer ±Y
//!     wall + both side walls, stopping short of the Y-seam overlap — with a
//!     HOOKED RAIL on each flank's straight run: an ARM standing on the mouth
//!     whose HEAD steps outboard over the groove (`_z_rail_heads`). The TOP
//!     pieces run their wall to the mouth at full section — the FOOT — with a
//!     notch above it that swallows that head (`_z_rail_feet`,
//!     `_z_rail_channels`). THE TWO COLUMNS ARE MIRRORED: front-top enters fore of
//!     home and slides AFT over the front wall's own plane, back-top enters aft of
//!     home and slides FORE over the rear wall's — each to the stop block closing
//!     its own far end; the end walls and corner turns close head-on behind it, the
//!     same telescoping mate the Y seam makes, arrived at along Y. Lifting a seated
//!     top lands each foot's flat top on its head's flat underside down both whole
//!     runs. A top comes off the way it went on, toward the end of the box it
//!     stands at — front-top forward into open air, back-top aft — so neither is
//!     lifted over the other and neither asks the box to come out from under
//!     whatever it is built under. Front-top is held by the two upper rods
//!     alone, so with those two out it draws off the front. A WALL THAT
//!     LIP STANDS ON IS `2 * wall` THICK, floor slab to lip rim
//!     (`_lip_underwall`): the lip is a skin standing proud of the interior
//!     face, and a skin that began at the seam would land its underside in air —
//!     a soffit round three sides of a piece that prints floor-down. Carried to
//!     the slab it is a wall instead, and there is nothing in a bottom piece for
//!     the bed to bridge.
//!
//! The walls stand off the bodies rather than on them — one side band at the ±X
//! walls, one wall at the back — because a body on the floor spans the interior wall
//! to wall, so a wall on its face would leave the seam machinery nowhere to stand.
//! The cold core seats flush against the seams instead, and stands flat on the floor slab — its bottom cap's lid is a plane and
//! every cap screw is down in a counterbore, so nothing goes under it. The ±X bands'
//! own seam furniture fences it sideways, the back Z seam's lip behind, and the floor's
//! two core lugs (`_core_fence`) ahead. The floor that core stands on is flat: the
//! Y seam's floor tongue stays within the slab and ends square, rather than standing
//! proud of its cavity-side face.
//!
//! Three pieces print on their Z− FACE — the bottom pieces floor-down on the slab,
//! front-top mouth-down on its seam rim — and back-top prints on its Z+ face, its
//! ceiling on the bed. The build axis is the box's own Z on every piece and the sign
//! is the piece's (`print_up`): where it is +Z the face that hangs is the one looking
//! DOWN, where it is −Z the one looking UP, and every 45° relief in this file is
//! struck on the side that hangs for its piece. The anti-warp corner relief goes on
//! the arrises that run along the build axis: the box's four standing verticals. Each quadrant owns only two of them —
//! its other two "corners" are the Y-seam, a telescoping mating face with no
//! exterior arris to relieve — so the front pieces round the front-left/right
//! verticals, the back pieces the back-left/right, and every seam stays square.
//! The display plane meets rounded side edges, which continue into the fluted
//! walls. The rear top edge remains square.
//!
//! Inside those same verticals stand the COLUMNS, and each is that relief MIRRORED —
//! congruent with it, a QUARTER TURN of the same radius, swung from the interior
//! corner because that is the only place such a turn fits with its ends on the two
//! inner faces. Two sharp corners and one arc between them, the corner behind it
//! solid, floor slab to ceiling. They are the cavity's own shape (`_cavity`), so everything held inside
//! it meets a column the way it meets a wall: a mount inside the footprint is the
//! column's material with only its bore left. At a front corner the rail channel's
//! deep lane passes through the pillar's flank side on its way to the stop, the one
//! mark the slide leaves on one.
//!
//! A knuckle is a block of one piece standing in the other's overlap: a front knuckle
//! roots fore of the seam in its own flank and runs aft inside the back piece's skin, a
//! back knuckle grows out of that skin and its flank. Every face between knuckles keeps a
//! running fit, so the halves telescope. Back-bottom holds the lower screw at both ends,
//! capturing front-bottom between them. Front-top holds the upper screw's head and insert,
//! capturing back-top's middle knuckle. All four screws are fully threaded M5 × 100.
//!
//! A Z seam is held shut along its whole run rather than pinned at its ends: the
//! rails' hooks bear over every millimetre both flanks carry, and the stop
//! blocks and end walls close the travel. At each Y-seam corner the upper screw pins
//! front-top to back-top, retaining front-top on its slide.
//!
//! main() exports the four printable pieces (enclosure-front-bottom.step,
//! enclosure-front-top.step, enclosure-back-bottom.step, enclosure-back-top.step)
//! plus enclosure.step — the four as separate solids in assembled position,
//! seams intact (mirrors `faucet_shell.py`). All five come through the same
//! code from a `Box`.
//!
//! The root: the module's typed constants (`State`), what every function receives (`Cx`), and the
//! install. The functions are in five parts by Python line: `p1` 118–2116, `p2` 2117–3500, `p3` 3501–4993,
//! `p4` 4994–6595, `p5` 6596–8543.
#![allow(non_snake_case, non_upper_case_globals, dead_code, unused_imports)]
use super::num::Num;
use super::py::{self, Args, Kwargs, Py, Tup, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result};
use std::rc::Rc;

pub mod p1;
pub mod p2;
pub mod p3;
pub mod p4;
pub mod p5;

pub const TYPED: bool = true;
const MODULE: &str = "enclosure";

/// What every typed function of the module receives: the registry, the module namespace (the
/// names the recorders replace are read there at every use) and the module's constants.
pub struct Cx {
    pub rt: Rt,
    pub ns: Ns,
    pub s: State,
    /// What the root and part 1 keep between calls.
    pub memo: Memo,
}

/// Values kept between calls: provider constants read once (a side-effect-free provider read may
/// be), and the id of every Python `Bound` instance `BOUNDS` has held (a namedtuple's fields never
/// change, and `_rust_objects` keeps every object it hands out, so a reference names one bound).
#[derive(Default)]
pub struct Memo {
    /// `{'SIZES': _wago.SIZES, 'lever_swing': _wago.lever_swing}` as `_core_wago` sends it.
    pub wago: std::cell::OnceCell<serde_json::Value>,
    /// `fits.supported_surface`.
    pub supported_surface: std::cell::OnceCell<f64>,
    /// A Python `Bound`'s `id`, by its reference handle.
    pub bound_ids: std::cell::RefCell<std::collections::HashMap<i64, Val>>,
}

/// Every module constant, one field per Python name, as the top level leaves it.
pub struct State {
    pub math: Val,
    pub sys: Val,
    pub _here: Val,
    pub _repo: Val,
    pub _tools: Val,
    pub PIECE_COLORS: Val,
    pub _fixed_pump_mount: Val,
    pub fits: Val,
    pub port_chip: Val,
    pub reeding: Val,
    pub _flute_skin: Val,
    pub _funnel: Val,
    pub _funnel_frame_part: Val,
    pub _above_core_shell: Val,
    pub _wago: Val,
    pub _mq6: Val,
    pub _keystone: Val,
    pub _c14: Val,
    pub _jg: Val,
    pub _seat: Val,
    pub _valve_tray: Val,
    pub _tray: Val,
    pub _dock: Val,
    pub _interface: Val,
    pub _swept_top: Val,
    pub _display_wings: Val,
    pub _grip_interface: Val,
    pub _anchor_cap: Val,
    pub BACK_TOP_UP: f64,
    pub H2C_X: f64,
    pub H2C_Y: f64,
    pub H2C_Z: f64,
    pub PIECE_PRINT_UP: Val,
    pub appliance_height: f64,
    pub appliance_width: f64,
    pub back_bottom_flank_t: f64,
    pub back_hook_lap: f64,
    pub back_top_ceiling_growth: f64,
    pub back_top_ceiling_t: f64,
    pub back_top_flank_t: f64,
    pub back_top_port_row_z: f64,
    pub back_top_wall_reliefs: Tup<Val>,
    pub back_top_wall_t: f64,
    pub bay_crown_air: f64,
    pub boss_ligament: f64,
    pub c14_bore_h: f64,
    pub c14_bore_r: f64,
    pub c14_bore_w: f64,
    pub c14_cord_extra_x: f64,
    pub c14_fit_extra: f64,
    pub c14_insertion_relief: f64,
    pub c14_pocket_depth: f64,
    pub c14_pocket_end_chord: f64,
    pub c14_pocket_h: f64,
    pub c14_pocket_knuckle_r: f64,
    pub c14_pocket_overcut: f64,
    pub c14_pocket_slip: f64,
    pub c14_pocket_w: f64,
    pub c14_pocket_wall: f64,
    pub c14_screw_pitch: f64,
    pub c14_station_x: f64,
    pub c14_tunnel_len: f64,
    pub c14_tunnel_wall: f64,
    pub c14_wall_relief_h: f64,
    pub c14_wall_relief_w: f64,
    pub cable_bore_air: f64,
    pub cable_bore_dia: f64,
    pub cable_sleeve_nom: f64,
    pub cap_boss_air: f64,
    pub cap_fitting_half: f64,
    pub cap_kiss: f64,
    pub cap_kiss_station_allowance: f64,
    pub cap_pump_air: f64,
    pub ceiling_lip_drop: f64,
    pub ceiling_skin: f64,
    pub co2_axis_drop: f64,
    pub column_corners: [[i64; 2]; 4],
    pub column_round: f64,
    pub cond_bore_depth: f64,
    pub cond_boss_t: f64,
    pub cond_fan_drop: f64,
    pub cond_fan_rise: f64,
    pub cond_mount_clear: f64,
    pub cond_rail_wall: f64,
    pub cond_screw_len: f64,
    pub cond_slot_grip: f64,
    pub cond_slot_press: f64,
    pub cond_vent_clear: f64,
    pub cond_vent_island_min: i64,
    pub cond_vent_probe: f64,
    pub cond_vent_transom_h: f64,
    pub cond_vent_transoms: i64,
    pub core_hold_land: f64,
    pub core_hold_reach: f64,
    pub core_hold_rise: f64,
    pub core_stop_rise: f64,
    pub core_stop_slip: f64,
    pub core_stop_web: f64,
    pub corner_round: f64,
    pub display_bezel_cut_slope: f64,
    pub display_bezel_cut_x: f64,
    pub display_bezel_depth: f64,
    pub display_bezel_slope: f64,
    pub display_bezel_x: f64,
    pub display_body_offset_slope: f64,
    pub display_body_offset_x: f64,
    pub display_corner_r: f64,
    pub display_cover_slip: f64,
    pub display_cover_thickness: f64,
    pub display_facet_angle_deg: f64,
    pub display_facet_buffer: f64,
    pub display_facet_slope: f64,
    pub display_facet_thickness: f64,
    pub display_facet_x: f64,
    pub display_inset_depth: f64,
    pub display_inset_lap: f64,
    pub display_inset_reach: f64,
    pub display_inset_slope: f64,
    pub display_inset_x: f64,
    pub display_loom_x_offset: f64,
    pub display_pcb_cut_through: f64,
    pub display_pcb_slope: f64,
    pub display_pcb_x: f64,
    pub disposal_bottom: f64,
    pub disposal_cap_height: f64,
    pub disposal_embed: f64,
    pub disposal_font: String,
    pub disposal_kind: String,
    pub disposal_line_gap: f64,
    pub disposal_lines: [String; 6],
    pub disposal_margin: f64,
    pub disposal_raise: f64,
    pub east_boss_corbel_clear: f64,
    pub east_boss_joint_air: f64,
    pub east_boss_min_stand: f64,
    pub east_knurl_entry_r: f64,
    pub floor_drop: f64,
    pub floor_heatset_depth: f64,
    pub floor_heatset_dia: f64,
    pub floor_heatset_min_wall: f64,
    pub floor_t: f64,
    pub flute_backing: f64,
    pub flute_count: i64,
    pub flute_depth: f64,
    pub flute_fade_steps: i64,
    pub flute_full_depth_height: f64,
    pub flute_pitch_drift: f64,
    pub flute_rise: f64,
    pub flute_samples: i64,
    pub fridge_reliefs: [[f64; 5]; 2],
    pub front_bottom_flank_t: f64,
    pub front_hook_lap: f64,
    pub front_plane_y: f64,
    pub front_seam_clear: f64,
    pub front_top_flank_t: f64,
    pub front_wall: f64,
    pub funnel_band_gap: f64,
    pub funnel_collar_air: f64,
    pub funnel_front_y: f64,
    pub funnel_seat_thickness: f64,
    pub handhold_corner_r: f64,
    pub handhold_edge_r: f64,
    pub handhold_height: f64,
    pub handhold_length: f64,
    pub handhold_roof: f64,
    pub handhold_wall: f64,
    pub handhold_y: f64,
    pub head_cbore_dia: f64,
    pub heatset_depth: f64,
    pub heatset_dia: f64,
    pub heatset_len: f64,
    pub heatset_long_len: f64,
    pub hook_arm: f64,
    pub hook_foot: f64,
    pub hook_lap: f64,
    pub lip_len: f64,
    pub lower_rod_len: f64,
    pub mount_bar_reach: f64,
    pub mount_bore_relief: f64,
    pub mount_boss_dia: f64,
    pub mount_boss_out: f64,
    pub mq6_can_yz: f64,
    pub mq6_card_x: f64,
    pub mq6_card_y: f64,
    pub mq6_card_z: f64,
    pub mq6_grip: f64,
    pub mq6_header_relief: f64,
    pub mq6_rail_wall: f64,
    pub mq6_slot_press: f64,
    pub plate_foot_corbel_angle: f64,
    pub plate_foot_reach: f64,
    pub plate_foot_t: f64,
    pub plate_foot_y: f64,
    pub pump_bay_floor_air: f64,
    pub pump_bay_floor_relief: f64,
    pub pump_bay_roof_relief: f64,
    pub pump_bay_side_air: f64,
    pub pump_cartridge_front_y: f64,
    pub pump_cartridge_top_clearance: f64,
    pub pump_cartridge_z_clearance: f64,
    pub pump_relief_floor: f64,
    pub pump_relief_skin: f64,
    pub pump_relief_z_air: f64,
    pub pump_show_growth: f64,
    pub pump_station_drop: f64,
    pub pump_station_front_y: f64,
    pub pump_station_lead: f64,
    pub rail_entry: f64,
    pub rail_flare_drop: f64,
    pub rail_lead: f64,
    pub rail_reach_in: f64,
    pub rail_stop_len: f64,
    pub rear_plane_y: f64,
    pub rear_seam_clear: f64,
    pub relief_chamfer: f64,
    pub ridge_wall_t: f64,
    pub screw_clear_dia: f64,
    pub side_band_inset: f64,
    pub slab_t: f64,
    pub slide_slip: f64,
    pub socket_cap: f64,
    pub stated_bound_tol: f64,
    pub station_land_draft: f64,
    pub upper_rod_len: f64,
    pub wago_lever_clear: f64,
    pub wago_pitch: f64,
    pub wago_roof_tab: f64,
    pub wago_well_press: f64,
    pub wago_well_wall: f64,
    pub wall: f64,
    pub y_seam: f64,
    pub y_stack_axis_in: f64,
    pub y_stack_cbore_depth: f64,
    pub y_stack_cbore_dia: f64,
    pub y_stack_clearance_dia: f64,
    pub y_stack_front_root: f64,
    pub y_stack_head_h: f64,
    pub y_stack_head_recess: f64,
    pub y_stack_high_depth: f64,
    pub y_stack_low_depth: f64,
    pub y_stack_lower_anchor_face_drop: f64,
    pub y_stack_lower_axis_in: f64,
    pub y_stack_lower_plane_over_seat: f64,
    pub y_stack_screw_length_tolerance: f64,
    pub y_stack_tip_clearance: f64,
    pub y_stack_upper_chamfer: f64,
    pub y_stack_upper_datum: f64,
    pub y_stack_upper_head_datum: f64,
    pub z_joint_clear: f64,
    pub z_lip_y_margin: f64,
    pub z_rise: f64,
    pub z_seam: f64,
    pub _nameplate_fit: Val,
    pub _data_fit: Val,
    pub BOUNDS: Val,
    pub column_relief_slip: f64,
    pub _z_seam_passes: Val,
    pub teardrop_roof_angle: f64,
    pub vent_channel_w: f64,
    pub vent_rib_wall: f64,
    pub vent_duct_drop: f64,
    pub vent_groove_drop: f64,
    pub vent_ramp_angle: f64,
    pub asse_cradle_up: f64,
    pub asse_v_half: f64,
    pub asse_cradle_lip: f64,
    pub tie_w: f64,
    pub tie_wide_w: f64,
    pub tie_t: f64,
    pub tie_cav_buffer: f64,
    pub tie_cav_w: f64,
    pub tie_cav_wide_w: f64,
    pub tie_cav_wall: f64,
    pub flow_meter_anchor_wall: f64,
    pub flow_meter_anchor_end_wall: f64,
    pub flow_meter_anchor_len: f64,
    pub tube_anchor_len: f64,
    pub tube_anchor_cavity_depth: f64,
    pub tube_anchor_backing_min: f64,
    pub tube_anchor_corbel_reach: f64,
    pub _ROOT_FACE: Val,
    pub keystone_nut_clear: f64,
    pub keystone_ease_shoulder: f64,
    pub piece_mesh_tol: f64,
    pub piece_mesh_angle: f64,
    pub _last_box: Val,
}

impl State {
    /// The constants as the generated top level left them.
    #[cfg(feature = "hybrid")]
    pub fn from_ns(ns: &Ns) -> Result<State> {
        fn read<T: Py>(ns: &Ns, name: &str) -> Result<T> {
            T::from_py(&ns.get(name)?).with_context(|| format!("enclosure.{name}"))
        }
        Ok(State {
            math: read(ns, "math")?,
            sys: read(ns, "sys")?,
            _here: read(ns, "_here")?,
            _repo: read(ns, "_repo")?,
            _tools: read(ns, "_tools")?,
            PIECE_COLORS: read(ns, "PIECE_COLORS")?,
            _fixed_pump_mount: read(ns, "_fixed_pump_mount")?,
            fits: read(ns, "fits")?,
            port_chip: read(ns, "port_chip")?,
            reeding: read(ns, "reeding")?,
            _flute_skin: read(ns, "_flute_skin")?,
            _funnel: read(ns, "_funnel")?,
            _funnel_frame_part: read(ns, "_funnel_frame_part")?,
            _above_core_shell: read(ns, "_above_core_shell")?,
            _wago: read(ns, "_wago")?,
            _mq6: read(ns, "_mq6")?,
            _keystone: read(ns, "_keystone")?,
            _c14: read(ns, "_c14")?,
            _jg: read(ns, "_jg")?,
            _seat: read(ns, "_seat")?,
            _valve_tray: read(ns, "_valve_tray")?,
            _tray: read(ns, "_tray")?,
            _dock: read(ns, "_dock")?,
            _interface: read(ns, "_interface")?,
            _swept_top: read(ns, "_swept_top")?,
            _display_wings: read(ns, "_display_wings")?,
            _grip_interface: read(ns, "_grip_interface")?,
            _anchor_cap: read(ns, "_anchor_cap")?,
            BACK_TOP_UP: read(ns, "BACK_TOP_UP")?,
            H2C_X: read(ns, "H2C_X")?,
            H2C_Y: read(ns, "H2C_Y")?,
            H2C_Z: read(ns, "H2C_Z")?,
            PIECE_PRINT_UP: read(ns, "PIECE_PRINT_UP")?,
            appliance_height: read(ns, "appliance_height")?,
            appliance_width: read(ns, "appliance_width")?,
            back_bottom_flank_t: read(ns, "back_bottom_flank_t")?,
            back_hook_lap: read(ns, "back_hook_lap")?,
            back_top_ceiling_growth: read(ns, "back_top_ceiling_growth")?,
            back_top_ceiling_t: read(ns, "back_top_ceiling_t")?,
            back_top_flank_t: read(ns, "back_top_flank_t")?,
            back_top_port_row_z: read(ns, "back_top_port_row_z")?,
            back_top_wall_reliefs: read(ns, "back_top_wall_reliefs")?,
            back_top_wall_t: read(ns, "back_top_wall_t")?,
            bay_crown_air: read(ns, "bay_crown_air")?,
            boss_ligament: read(ns, "boss_ligament")?,
            c14_bore_h: read(ns, "c14_bore_h")?,
            c14_bore_r: read(ns, "c14_bore_r")?,
            c14_bore_w: read(ns, "c14_bore_w")?,
            c14_cord_extra_x: read(ns, "c14_cord_extra_x")?,
            c14_fit_extra: read(ns, "c14_fit_extra")?,
            c14_insertion_relief: read(ns, "c14_insertion_relief")?,
            c14_pocket_depth: read(ns, "c14_pocket_depth")?,
            c14_pocket_end_chord: read(ns, "c14_pocket_end_chord")?,
            c14_pocket_h: read(ns, "c14_pocket_h")?,
            c14_pocket_knuckle_r: read(ns, "c14_pocket_knuckle_r")?,
            c14_pocket_overcut: read(ns, "c14_pocket_overcut")?,
            c14_pocket_slip: read(ns, "c14_pocket_slip")?,
            c14_pocket_w: read(ns, "c14_pocket_w")?,
            c14_pocket_wall: read(ns, "c14_pocket_wall")?,
            c14_screw_pitch: read(ns, "c14_screw_pitch")?,
            c14_station_x: read(ns, "c14_station_x")?,
            c14_tunnel_len: read(ns, "c14_tunnel_len")?,
            c14_tunnel_wall: read(ns, "c14_tunnel_wall")?,
            c14_wall_relief_h: read(ns, "c14_wall_relief_h")?,
            c14_wall_relief_w: read(ns, "c14_wall_relief_w")?,
            cable_bore_air: read(ns, "cable_bore_air")?,
            cable_bore_dia: read(ns, "cable_bore_dia")?,
            cable_sleeve_nom: read(ns, "cable_sleeve_nom")?,
            cap_boss_air: read(ns, "cap_boss_air")?,
            cap_fitting_half: read(ns, "cap_fitting_half")?,
            cap_kiss: read(ns, "cap_kiss")?,
            cap_kiss_station_allowance: read(ns, "cap_kiss_station_allowance")?,
            cap_pump_air: read(ns, "cap_pump_air")?,
            ceiling_lip_drop: read(ns, "ceiling_lip_drop")?,
            ceiling_skin: read(ns, "ceiling_skin")?,
            co2_axis_drop: read(ns, "co2_axis_drop")?,
            column_corners: read(ns, "column_corners")?,
            column_round: read(ns, "column_round")?,
            cond_bore_depth: read(ns, "cond_bore_depth")?,
            cond_boss_t: read(ns, "cond_boss_t")?,
            cond_fan_drop: read(ns, "cond_fan_drop")?,
            cond_fan_rise: read(ns, "cond_fan_rise")?,
            cond_mount_clear: read(ns, "cond_mount_clear")?,
            cond_rail_wall: read(ns, "cond_rail_wall")?,
            cond_screw_len: read(ns, "cond_screw_len")?,
            cond_slot_grip: read(ns, "cond_slot_grip")?,
            cond_slot_press: read(ns, "cond_slot_press")?,
            cond_vent_clear: read(ns, "cond_vent_clear")?,
            cond_vent_island_min: read(ns, "cond_vent_island_min")?,
            cond_vent_probe: read(ns, "cond_vent_probe")?,
            cond_vent_transom_h: read(ns, "cond_vent_transom_h")?,
            cond_vent_transoms: read(ns, "cond_vent_transoms")?,
            core_hold_land: read(ns, "core_hold_land")?,
            core_hold_reach: read(ns, "core_hold_reach")?,
            core_hold_rise: read(ns, "core_hold_rise")?,
            core_stop_rise: read(ns, "core_stop_rise")?,
            core_stop_slip: read(ns, "core_stop_slip")?,
            core_stop_web: read(ns, "core_stop_web")?,
            corner_round: read(ns, "corner_round")?,
            display_bezel_cut_slope: read(ns, "display_bezel_cut_slope")?,
            display_bezel_cut_x: read(ns, "display_bezel_cut_x")?,
            display_bezel_depth: read(ns, "display_bezel_depth")?,
            display_bezel_slope: read(ns, "display_bezel_slope")?,
            display_bezel_x: read(ns, "display_bezel_x")?,
            display_body_offset_slope: read(ns, "display_body_offset_slope")?,
            display_body_offset_x: read(ns, "display_body_offset_x")?,
            display_corner_r: read(ns, "display_corner_r")?,
            display_cover_slip: read(ns, "display_cover_slip")?,
            display_cover_thickness: read(ns, "display_cover_thickness")?,
            display_facet_angle_deg: read(ns, "display_facet_angle_deg")?,
            display_facet_buffer: read(ns, "display_facet_buffer")?,
            display_facet_slope: read(ns, "display_facet_slope")?,
            display_facet_thickness: read(ns, "display_facet_thickness")?,
            display_facet_x: read(ns, "display_facet_x")?,
            display_inset_depth: read(ns, "display_inset_depth")?,
            display_inset_lap: read(ns, "display_inset_lap")?,
            display_inset_reach: read(ns, "display_inset_reach")?,
            display_inset_slope: read(ns, "display_inset_slope")?,
            display_inset_x: read(ns, "display_inset_x")?,
            display_loom_x_offset: read(ns, "display_loom_x_offset")?,
            display_pcb_cut_through: read(ns, "display_pcb_cut_through")?,
            display_pcb_slope: read(ns, "display_pcb_slope")?,
            display_pcb_x: read(ns, "display_pcb_x")?,
            disposal_bottom: read(ns, "disposal_bottom")?,
            disposal_cap_height: read(ns, "disposal_cap_height")?,
            disposal_embed: read(ns, "disposal_embed")?,
            disposal_font: read(ns, "disposal_font")?,
            disposal_kind: read(ns, "disposal_kind")?,
            disposal_line_gap: read(ns, "disposal_line_gap")?,
            disposal_lines: read(ns, "disposal_lines")?,
            disposal_margin: read(ns, "disposal_margin")?,
            disposal_raise: read(ns, "disposal_raise")?,
            east_boss_corbel_clear: read(ns, "east_boss_corbel_clear")?,
            east_boss_joint_air: read(ns, "east_boss_joint_air")?,
            east_boss_min_stand: read(ns, "east_boss_min_stand")?,
            east_knurl_entry_r: read(ns, "east_knurl_entry_r")?,
            floor_drop: read(ns, "floor_drop")?,
            floor_heatset_depth: read(ns, "floor_heatset_depth")?,
            floor_heatset_dia: read(ns, "floor_heatset_dia")?,
            floor_heatset_min_wall: read(ns, "floor_heatset_min_wall")?,
            floor_t: read(ns, "floor_t")?,
            flute_backing: read(ns, "flute_backing")?,
            flute_count: read(ns, "flute_count")?,
            flute_depth: read(ns, "flute_depth")?,
            flute_fade_steps: read(ns, "flute_fade_steps")?,
            flute_full_depth_height: read(ns, "flute_full_depth_height")?,
            flute_pitch_drift: read(ns, "flute_pitch_drift")?,
            flute_rise: read(ns, "flute_rise")?,
            flute_samples: read(ns, "flute_samples")?,
            fridge_reliefs: read(ns, "fridge_reliefs")?,
            front_bottom_flank_t: read(ns, "front_bottom_flank_t")?,
            front_hook_lap: read(ns, "front_hook_lap")?,
            front_plane_y: read(ns, "front_plane_y")?,
            front_seam_clear: read(ns, "front_seam_clear")?,
            front_top_flank_t: read(ns, "front_top_flank_t")?,
            front_wall: read(ns, "front_wall")?,
            funnel_band_gap: read(ns, "funnel_band_gap")?,
            funnel_collar_air: read(ns, "funnel_collar_air")?,
            funnel_front_y: read(ns, "funnel_front_y")?,
            funnel_seat_thickness: read(ns, "funnel_seat_thickness")?,
            handhold_corner_r: read(ns, "handhold_corner_r")?,
            handhold_edge_r: read(ns, "handhold_edge_r")?,
            handhold_height: read(ns, "handhold_height")?,
            handhold_length: read(ns, "handhold_length")?,
            handhold_roof: read(ns, "handhold_roof")?,
            handhold_wall: read(ns, "handhold_wall")?,
            handhold_y: read(ns, "handhold_y")?,
            head_cbore_dia: read(ns, "head_cbore_dia")?,
            heatset_depth: read(ns, "heatset_depth")?,
            heatset_dia: read(ns, "heatset_dia")?,
            heatset_len: read(ns, "heatset_len")?,
            heatset_long_len: read(ns, "heatset_long_len")?,
            hook_arm: read(ns, "hook_arm")?,
            hook_foot: read(ns, "hook_foot")?,
            hook_lap: read(ns, "hook_lap")?,
            lip_len: read(ns, "lip_len")?,
            lower_rod_len: read(ns, "lower_rod_len")?,
            mount_bar_reach: read(ns, "mount_bar_reach")?,
            mount_bore_relief: read(ns, "mount_bore_relief")?,
            mount_boss_dia: read(ns, "mount_boss_dia")?,
            mount_boss_out: read(ns, "mount_boss_out")?,
            mq6_can_yz: read(ns, "mq6_can_yz")?,
            mq6_card_x: read(ns, "mq6_card_x")?,
            mq6_card_y: read(ns, "mq6_card_y")?,
            mq6_card_z: read(ns, "mq6_card_z")?,
            mq6_grip: read(ns, "mq6_grip")?,
            mq6_header_relief: read(ns, "mq6_header_relief")?,
            mq6_rail_wall: read(ns, "mq6_rail_wall")?,
            mq6_slot_press: read(ns, "mq6_slot_press")?,
            plate_foot_corbel_angle: read(ns, "plate_foot_corbel_angle")?,
            plate_foot_reach: read(ns, "plate_foot_reach")?,
            plate_foot_t: read(ns, "plate_foot_t")?,
            plate_foot_y: read(ns, "plate_foot_y")?,
            pump_bay_floor_air: read(ns, "pump_bay_floor_air")?,
            pump_bay_floor_relief: read(ns, "pump_bay_floor_relief")?,
            pump_bay_roof_relief: read(ns, "pump_bay_roof_relief")?,
            pump_bay_side_air: read(ns, "pump_bay_side_air")?,
            pump_cartridge_front_y: read(ns, "pump_cartridge_front_y")?,
            pump_cartridge_top_clearance: read(ns, "pump_cartridge_top_clearance")?,
            pump_cartridge_z_clearance: read(ns, "pump_cartridge_z_clearance")?,
            pump_relief_floor: read(ns, "pump_relief_floor")?,
            pump_relief_skin: read(ns, "pump_relief_skin")?,
            pump_relief_z_air: read(ns, "pump_relief_z_air")?,
            pump_show_growth: read(ns, "pump_show_growth")?,
            pump_station_drop: read(ns, "pump_station_drop")?,
            pump_station_front_y: read(ns, "pump_station_front_y")?,
            pump_station_lead: read(ns, "pump_station_lead")?,
            rail_entry: read(ns, "rail_entry")?,
            rail_flare_drop: read(ns, "rail_flare_drop")?,
            rail_lead: read(ns, "rail_lead")?,
            rail_reach_in: read(ns, "rail_reach_in")?,
            rail_stop_len: read(ns, "rail_stop_len")?,
            rear_plane_y: read(ns, "rear_plane_y")?,
            rear_seam_clear: read(ns, "rear_seam_clear")?,
            relief_chamfer: read(ns, "relief_chamfer")?,
            ridge_wall_t: read(ns, "ridge_wall_t")?,
            screw_clear_dia: read(ns, "screw_clear_dia")?,
            side_band_inset: read(ns, "side_band_inset")?,
            slab_t: read(ns, "slab_t")?,
            slide_slip: read(ns, "slide_slip")?,
            socket_cap: read(ns, "socket_cap")?,
            stated_bound_tol: read(ns, "stated_bound_tol")?,
            station_land_draft: read(ns, "station_land_draft")?,
            upper_rod_len: read(ns, "upper_rod_len")?,
            wago_lever_clear: read(ns, "wago_lever_clear")?,
            wago_pitch: read(ns, "wago_pitch")?,
            wago_roof_tab: read(ns, "wago_roof_tab")?,
            wago_well_press: read(ns, "wago_well_press")?,
            wago_well_wall: read(ns, "wago_well_wall")?,
            wall: read(ns, "wall")?,
            y_seam: read(ns, "y_seam")?,
            y_stack_axis_in: read(ns, "y_stack_axis_in")?,
            y_stack_cbore_depth: read(ns, "y_stack_cbore_depth")?,
            y_stack_cbore_dia: read(ns, "y_stack_cbore_dia")?,
            y_stack_clearance_dia: read(ns, "y_stack_clearance_dia")?,
            y_stack_front_root: read(ns, "y_stack_front_root")?,
            y_stack_head_h: read(ns, "y_stack_head_h")?,
            y_stack_head_recess: read(ns, "y_stack_head_recess")?,
            y_stack_high_depth: read(ns, "y_stack_high_depth")?,
            y_stack_low_depth: read(ns, "y_stack_low_depth")?,
            y_stack_lower_anchor_face_drop: read(ns, "y_stack_lower_anchor_face_drop")?,
            y_stack_lower_axis_in: read(ns, "y_stack_lower_axis_in")?,
            y_stack_lower_plane_over_seat: read(ns, "y_stack_lower_plane_over_seat")?,
            y_stack_screw_length_tolerance: read(ns, "y_stack_screw_length_tolerance")?,
            y_stack_tip_clearance: read(ns, "y_stack_tip_clearance")?,
            y_stack_upper_chamfer: read(ns, "y_stack_upper_chamfer")?,
            y_stack_upper_datum: read(ns, "y_stack_upper_datum")?,
            y_stack_upper_head_datum: read(ns, "y_stack_upper_head_datum")?,
            z_joint_clear: read(ns, "z_joint_clear")?,
            z_lip_y_margin: read(ns, "z_lip_y_margin")?,
            z_rise: read(ns, "z_rise")?,
            z_seam: read(ns, "z_seam")?,
            _nameplate_fit: read(ns, "_nameplate_fit")?,
            _data_fit: read(ns, "_data_fit")?,
            BOUNDS: read(ns, "BOUNDS")?,
            column_relief_slip: read(ns, "column_relief_slip")?,
            _z_seam_passes: read(ns, "_z_seam_passes")?,
            teardrop_roof_angle: read(ns, "teardrop_roof_angle")?,
            vent_channel_w: read(ns, "vent_channel_w")?,
            vent_rib_wall: read(ns, "vent_rib_wall")?,
            vent_duct_drop: read(ns, "vent_duct_drop")?,
            vent_groove_drop: read(ns, "vent_groove_drop")?,
            vent_ramp_angle: read(ns, "vent_ramp_angle")?,
            asse_cradle_up: read(ns, "asse_cradle_up")?,
            asse_v_half: read(ns, "asse_v_half")?,
            asse_cradle_lip: read(ns, "asse_cradle_lip")?,
            tie_w: read(ns, "tie_w")?,
            tie_wide_w: read(ns, "tie_wide_w")?,
            tie_t: read(ns, "tie_t")?,
            tie_cav_buffer: read(ns, "tie_cav_buffer")?,
            tie_cav_w: read(ns, "tie_cav_w")?,
            tie_cav_wide_w: read(ns, "tie_cav_wide_w")?,
            tie_cav_wall: read(ns, "tie_cav_wall")?,
            flow_meter_anchor_wall: read(ns, "flow_meter_anchor_wall")?,
            flow_meter_anchor_end_wall: read(ns, "flow_meter_anchor_end_wall")?,
            flow_meter_anchor_len: read(ns, "flow_meter_anchor_len")?,
            tube_anchor_len: read(ns, "tube_anchor_len")?,
            tube_anchor_cavity_depth: read(ns, "tube_anchor_cavity_depth")?,
            tube_anchor_backing_min: read(ns, "tube_anchor_backing_min")?,
            tube_anchor_corbel_reach: read(ns, "tube_anchor_corbel_reach")?,
            _ROOT_FACE: read(ns, "_ROOT_FACE")?,
            keystone_nut_clear: read(ns, "keystone_nut_clear")?,
            keystone_ease_shoulder: read(ns, "keystone_ease_shoulder")?,
            piece_mesh_tol: read(ns, "piece_mesh_tol")?,
            piece_mesh_angle: read(ns, "piece_mesh_angle")?,
            _last_box: read(ns, "_last_box")?,
        })
    }
}

// --- the module's namedtuples ---------------------------------------------------------------------
//
// The namespace keeps the classes the top level makes (`namedtuple(..., module="enclosure")`, Python
// classes), and every instance a caller holds is one of them. A struct's `from_py` reads an instance
// in one snapshot (a namedtuple arrives as the tuple of its fields); its `to_py` calls the namespace's
// class, so Python receives a new instance of that class holding the same values.

/// The namespace's namedtuple class `name`.
fn class(name: &str) -> Result<Val> {
    super::rt::current()?.state::<Cx>(MODULE)?.ns.get(name)
}

/// A record's fields in order, read in one snapshot.
fn fields_of(value: &Val, n: usize, what: &str) -> Result<Vec<Val>> {
    let items = py::snapshot(value)?.iter().with_context(|| format!("{what}: not a record"))?;
    anyhow::ensure!(items.len() == n, "{what}: expected {n} fields, got {}", items.len());
    Ok(items)
}

/// A field holding a record of its own (`PortField`, `Nameplate`), which the snapshot flattened to
/// a tuple: the instance itself, read from the object that holds it, so that it reaches Python again
/// as that class. Anything else stays as the snapshot gave it.
fn record_field(owner: &Val, path: &[&str], flat: Val) -> Result<Val> {
    match (&flat, owner) {
        (Val::Tuple(items), Val::Ref(_)) if !items.is_empty() => {
            let mut value = owner.clone();
            for name in path {
                value = value.attr(name)?;
            }
            Ok(value)
        }
        _ => Ok(flat),
    }
}

/// The whole description of one box — what `build_pieces` cuts the four pieces from: the pack it
/// stands around, and the figures the shell measures for itself once it knows what is inside.
///   pack          the placed bodies and every station they put on a wall, as `Pack` states them
///   inner/outer   the cavity and the shell, (x0, x1, y0, y1, z0, z1)
///   y_joint       the front↔back seam plane
///   splits        the bottom↔top seam height per Y column, (front, back)
///   z_seam_passes whether each (front, back) Z seam crosses its column rather than an open band
///   column_reliefs what the standing corners' PILLARS give up to the pack standing in them, one
///                 (sx, sy, name, room) per body: the corner's own signs, whose body it is, and the
///                 world box the column is cut back to, `(x0, x1, y0, y1, z0, z1)`
///   pump_bay      the pump cradle's opening in the flat front span, (x0, x1, z_top); None when
///                 the pack stands no pumps
#[derive(Clone, Debug)]
pub struct Box {
    pub pack: Pack,
    pub inner: [f64; 6],
    pub outer: [f64; 6],
    pub y_joint: f64,
    pub splits: [f64; 2],
    pub z_seam_passes: [bool; 2],
    pub column_reliefs: Tup<(i64, i64, String, [f64; 6])>,
    pub pump_bay: Option<[f64; 3]>,
}
impl Py for Box {
    fn to_py(&self) -> Result<Val> {
        py::call(&class("Box")?, vec![
            self.pack.to_py()?,
            self.inner.to_py()?,
            self.outer.to_py()?,
            self.y_joint.to_py()?,
            self.splits.to_py()?,
            self.z_seam_passes.to_py()?,
            self.column_reliefs.to_py()?,
            self.pump_bay.to_py()?,
        ])
    }
    fn from_py(value: &Val) -> Result<Box> {
        let items: [Val; 8] = fields_of(value, 8, "Box")?.try_into().map_err(|_| anyhow::anyhow!("Box"))?;
        let [pack, inner, outer, y_joint, splits, z_seam_passes, column_reliefs, pump_bay] = items;
        let pack = match &pack {
            Val::Tuple(rows) => Pack::read(value, &["pack"], rows.clone())?,
            _ => Pack::from_py(&pack)?,
        };
        Ok(Box {
            pack,
            inner: Py::from_py(&inner).context("Box.inner")?,
            outer: Py::from_py(&outer).context("Box.outer")?,
            y_joint: Py::from_py(&y_joint).context("Box.y_joint")?,
            splits: Py::from_py(&splits).context("Box.splits")?,
            z_seam_passes: Py::from_py(&z_seam_passes).context("Box.z_seam_passes")?,
            column_reliefs: Py::from_py(&column_reliefs).context("Box.column_reliefs")?,
            pump_bay: Py::from_py(&pump_bay).context("Box.pump_bay")?,
        })
    }
}

/// What a box is built AROUND: the placed bodies, and every station they put on a wall (the
/// Python's comment above `Pack` describes each field). Every field is the value Python holds, as
/// one snapshot copies it: a tuple stays a tuple, a list a list, a dict a local dict (`placed`'s
/// solids stay references), None None; a `PortField` or `Nameplate` is the instance itself. Read a
/// field typed with `Py::from_py` (`Tup::<[f64; 4]>::from_py(&pack.floor_bosses)?`); a changed
/// field is a `Val` again (`_replace` is `Pack { placed: .., ..pack.clone() }`).
#[derive(Clone, Debug)]
pub struct Pack {
    pub placed: Val,
    pub front_ports: Val,
    pub back_ports: Val,
    pub east_ports: Val,
    pub west_ports: Val,
    pub funnel: Val,
    pub c14: Val,
    pub east_bosses: Val,
    pub east_mount_fills: Val,
    pub side_wells: Val,
    pub floor_bosses: Val,
    pub west_cradle: Val,
    pub cond_cradle: Val,
    pub cond_mount: Val,
    pub cond_airway: Val,
    pub asse_cradle: Val,
    pub flow_meter_anchors: Val,
    pub tube_anchors: Val,
    pub ceiling_reliefs: Val,
    pub flank_reliefs: Val,
    pub port_field: Val,
    pub nameplate: Val,
    pub keystone: Val,
    pub valve_trays: Val,
    pub pump_trays: Val,
    pub core_stops: Val,
    pub core_holds: Val,
    pub vent_chase: Val,
    pub collet_plate: Val,
    pub front_flank_reliefs: Val,
}
impl Pack {
    /// The fields of a Pack the snapshot of `owner` (a Box or a Pack, reached by `path`) gave.
    fn read(owner: &Val, path: &[&str], rows: Vec<Val>) -> Result<Pack> {
        let items: [Val; 30] = rows.try_into().map_err(|rows: Vec<Val>| anyhow::anyhow!("Pack: expected 30 fields, got {}", rows.len()))?;
        let [placed, front_ports, back_ports, east_ports, west_ports, funnel, c14, east_bosses,
            east_mount_fills, side_wells, floor_bosses, west_cradle, cond_cradle, cond_mount,
            cond_airway, asse_cradle, flow_meter_anchors, tube_anchors, ceiling_reliefs,
            flank_reliefs, port_field, nameplate, keystone, valve_trays, pump_trays, core_stops,
            core_holds, vent_chase, collet_plate, front_flank_reliefs] = items;
        let at = |name: &'static str| -> Vec<&str> {
            let mut at = path.to_vec();
            at.push(name);
            at
        };
        Ok(Pack {
            placed, front_ports, back_ports, east_ports, west_ports, funnel, c14, east_bosses,
            east_mount_fills, side_wells, floor_bosses, west_cradle, cond_cradle, cond_mount,
            cond_airway, asse_cradle, flow_meter_anchors, tube_anchors, ceiling_reliefs,
            flank_reliefs,
            port_field: record_field(owner, &at("port_field"), port_field)?,
            nameplate: record_field(owner, &at("nameplate"), nameplate)?,
            keystone, valve_trays, pump_trays, core_stops, core_holds, vent_chase, collet_plate,
            front_flank_reliefs,
        })
    }
    fn fields(&self) -> Vec<Val> {
        vec![
            self.placed.clone(), self.front_ports.clone(), self.back_ports.clone(),
            self.east_ports.clone(), self.west_ports.clone(), self.funnel.clone(), self.c14.clone(),
            self.east_bosses.clone(), self.east_mount_fills.clone(), self.side_wells.clone(),
            self.floor_bosses.clone(), self.west_cradle.clone(), self.cond_cradle.clone(),
            self.cond_mount.clone(), self.cond_airway.clone(), self.asse_cradle.clone(),
            self.flow_meter_anchors.clone(), self.tube_anchors.clone(), self.ceiling_reliefs.clone(),
            self.flank_reliefs.clone(), self.port_field.clone(), self.nameplate.clone(),
            self.keystone.clone(), self.valve_trays.clone(), self.pump_trays.clone(),
            self.core_stops.clone(), self.core_holds.clone(), self.vent_chase.clone(),
            self.collet_plate.clone(), self.front_flank_reliefs.clone(),
        ]
    }
}
impl Py for Pack {
    fn to_py(&self) -> Result<Val> {
        py::call(&class("Pack")?, self.fields())
    }
    fn from_py(value: &Val) -> Result<Pack> {
        Pack::read(value, &[], fields_of(value, 30, "Pack")?)
    }
}

/// The pockets the +Y wall of back-top's outer face carries and the nut lands behind them,
/// `PortField(proud, rim, pockets)`: how deep a pocket is cut, the wall the field keeps around
/// each chip, and one `(x, z, width, rise, bottom)` per pocket (as Python holds them).
#[derive(Clone, Debug)]
pub struct PortField {
    pub proud: Num,
    pub rim: Num,
    pub pockets: Val,
}
impl Py for PortField {
    fn to_py(&self) -> Result<Val> {
        py::call(&class("PortField")?, vec![self.proud.val(), self.rim.val(), self.pockets.clone()])
    }
    fn from_py(value: &Val) -> Result<PortField> {
        let [proud, rim, pockets]: [Val; 3] = fields_of(value, 3, "PortField")?.try_into().map_err(|_| anyhow::anyhow!("PortField"))?;
        Ok(PortField { proud: Num::of(&proud)?, rim: Num::of(&rim)?, pockets })
    }
}

/// One bound's reading, `Bound(id, label, ok, value, target, detail)`: what `record_bound` enters
/// in `BOUNDS`. This module's own bounds state `value` and `target` as text and `detail` as a list
/// of lines (`Bound::stated`); a bound from elsewhere keeps whatever it holds.
#[derive(Clone, Debug)]
pub struct Bound {
    pub id: String,
    pub label: String,
    pub ok: bool,
    pub value: Val,
    pub target: Val,
    pub detail: Val,
}
impl Bound {
    /// A bound as this module states one: reading and target as text, detail a list of lines.
    pub fn stated(id: impl Into<String>, label: impl Into<String>, ok: bool, value: String, target: String,
                  detail: Vec<String>) -> Bound {
        Bound {
            id: id.into(),
            label: label.into(),
            ok,
            value: Val::Str(value),
            target: Val::Str(target),
            detail: Val::list(detail.into_iter().map(Val::Str).collect()),
        }
    }
}
impl Py for Bound {
    fn to_py(&self) -> Result<Val> {
        py::call(&class("Bound")?, vec![
            Val::Str(self.id.clone()),
            Val::Str(self.label.clone()),
            Val::Bool(self.ok),
            self.value.clone(),
            self.target.clone(),
            self.detail.clone(),
        ])
    }
    fn from_py(value: &Val) -> Result<Bound> {
        let [id, label, ok, reading, target, detail]: [Val; 6] =
            fields_of(value, 6, "Bound")?.try_into().map_err(|_| anyhow::anyhow!("Bound"))?;
        Ok(Bound {
            id: Py::from_py(&id).context("Bound.id")?,
            label: Py::from_py(&label).context("Bound.label")?,
            ok: Py::from_py(&ok).context("Bound.ok")?,
            value: reading,
            target,
            detail,
        })
    }
}

/// The fine-model readings a box is sized on, `BoxReadings(bounds, lip, floor, under, pillars)`
/// (`_rust_enclosure_checks.box_readings`): `bounds` is `{name: (lower, upper)}`, `lip`
/// `{"front"|"back": {key: row}}`, and `floor` / `under` / `pillars` dicts keyed by tuples, each row a
/// `{'volume_mm3', 'min', 'max'[, 'components']}` dict. Each field is the snapshot's local dict.
#[derive(Clone, Debug)]
pub struct BoxReadings {
    pub bounds: Val,
    pub lip: Val,
    pub floor: Val,
    pub under: Val,
    pub pillars: Val,
}
impl Py for BoxReadings {
    fn to_py(&self) -> Result<Val> {
        py::call(&class("BoxReadings")?, vec![
            self.bounds.clone(),
            self.lip.clone(),
            self.floor.clone(),
            self.under.clone(),
            self.pillars.clone(),
        ])
    }
    fn from_py(value: &Val) -> Result<BoxReadings> {
        let [bounds, lip, floor, under, pillars]: [Val; 5] =
            fields_of(value, 5, "BoxReadings")?.try_into().map_err(|_| anyhow::anyhow!("BoxReadings"))?;
        Ok(BoxReadings { bounds, lip, floor, under, pillars })
    }
}

/// Six scalar extrema, `_ReadingBounds(xmin, xmax, ymin, ymax, zmin, zmax)`. `from_py` also reads
/// any object with those six attributes (a CadQuery `BoundBox`, as `_boxes.boxed` gives); `to_py`
/// makes a `_ReadingBounds`.
#[allow(non_camel_case_types)]
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct _ReadingBounds {
    pub xmin: f64,
    pub xmax: f64,
    pub ymin: f64,
    pub ymax: f64,
    pub zmin: f64,
    pub zmax: f64,
}
impl Py for _ReadingBounds {
    fn to_py(&self) -> Result<Val> {
        py::call(&class("_ReadingBounds")?, vec![
            Val::Float(self.xmin),
            Val::Float(self.xmax),
            Val::Float(self.ymin),
            Val::Float(self.ymax),
            Val::Float(self.zmin),
            Val::Float(self.zmax),
        ])
    }
    fn from_py(value: &Val) -> Result<_ReadingBounds> {
        let flat = py::snapshot(value)?;
        let six: [f64; 6] = match &flat {
            Val::Tuple(items) if items.len() == 6 => Py::from_py(&flat)?,
            _ => {
                let f = |name: &str| -> Result<f64> { value.attr(name)?.num() };
                [f("xmin")?, f("xmax")?, f("ymin")?, f("ymax")?, f("zmin")?, f("zmax")?]
            }
        };
        let [xmin, xmax, ymin, ymax, zmin, zmax] = six;
        Ok(_ReadingBounds { xmin, xmax, ymin, ymax, zmin, zmax })
    }
}

/// Every function of the module in source order, with its part.
pub const FUNCTIONS: &[(&str, u8)] = &[
    ("print_up", 1),
    ("flute_backed_sections", 1),
    ("wago_stand", 1),
    ("wago_engage", 1),
    ("wago_half", 1),
    ("wago_swing", 1),
    ("cond_slot_half", 1),
    ("cond_slot_mouth", 1),
    ("interior_x", 1),
    ("back_top_wall_face", 1),
    ("back_wall_t_at", 1),
    ("back_top_flank_face", 1),
    ("back_bottom_flank_face", 1),
    ("front_bottom_flank_face", 1),
    ("vent_flank_face", 1),
    ("front_top_flank_face", 1),
    ("front_top_flank_root_z", 1),
    ("tray_corbel_roots", 1),
    ("lip_face_x", 1),
    ("piece_root_faces", 1),
    ("_c14_pocket_landmarks", 1),
    ("c14_mount_half", 1),
    ("back_top_ceiling_face", 1),
    ("back_top_ceiling_stock", 1),
    ("back_flank_start", 1),
    ("documented", 1),
    ("record_bound", 1),
    ("_supported_cut", 1),
    ("_ring", 1),
    ("_column_arc", 1),
    ("_corner_column", 1),
    ("_column_pillar", 1),
    ("_column_along", 1),
    ("wall_flat_from_corner", 1),
    ("_column_depth", 1),
    ("_cavity", 1),
    ("_cradle_relief", 1),
    ("_column_relief", 1),
    ("_column_relief_rise", 1),
    ("wall_band_corner_y", 1),
    ("wall_boss_aft_limit", 1),
    ("east_band_free_y", 1),
    ("front_band_free_y", 1),
    ("seam_bosses", 1),
    ("_in_a_boss", 1),
    ("_open_bands", 1),
    ("_clipped", 1),
    ("_bed_band", 1),
    ("_lip_band", 1),
    ("_lip_denied", 1),
    ("_z_joints", 1),
    ("back_top_flank_bound", 1),
    ("_dims", 2),
    ("_facet_geom", 2),
    ("housing_back_y", 2),
    ("pcb_ridge", 2),
    ("_ridge_join", 2),
    ("_seat_back", 2),
    ("display_centre_x", 2),
    ("_facet_wedge", 2),
    ("flank_x_at", 2),
    ("_plan_segments", 2),
    ("seam_cap_z", 2),
    ("plate_outline", 2),
    ("plan_perimeter", 2),
    ("flute_pitch", 2),
    ("plan_at", 2),
    ("flute_rails", 2),
    ("flute_centres", 2),
    ("housing_fill", 2),
    ("_display_point", 2),
    ("display_plane", 2),
    ("_display_cut_exit_depth", 2),
    ("_port_cuts", 2),
    ("disposal_field", 2),
    ("disposal_figures", 2),
    ("_nameplate", 2),
    ("_port_chip", 2),
    ("_port_field", 2),
    ("_x_port_cuts", 2),
    ("_funnel_frame", 2),
    ("_funnel_hole", 2),
    ("_funnel_cut_plan", 2),
    ("funnel_seat_z", 2),
    ("with_funnel", 2),
    ("_funnel_cut", 2),
    ("_seat_ledge_corbels", 2),
    ("_ceiling_tongue_air", 2),
    ("_handhold_levels", 2),
    ("_band_x", 2),
    ("y_stack_y", 2),
    ("_y_stack_gap", 2),
    ("_y_knuckle_faces", 2),
    ("y_stack", 2),
    ("y_stack_axis", 2),
    ("y_stack_rods", 2),
    ("_y_face_z", 2),
    ("_y_under_face", 2),
    ("_y_between_faces", 2),
    ("_y_top_cap", 2),
    ("_y_knuckle", 2),
    ("_y_knuckle_air", 2),
    ("_y_stack_bores", 2),
    ("_y_bore_reliefs", 2),
    ("_y_stacks", 2),
    ("_front_lip", 2),
    ("_y_lip_channel", 2),
    ("_floor_tongue", 2),
    ("_handhold_y", 2),
    ("grip_interface", 2),
    ("_handhold_backing_end", 2),
    ("_handhold_backing_joint", 2),
    ("_handhold_frame", 2),
    ("_handholds", 2),
    ("_finish_handholds", 2),
    ("_z_rail_runs", 3),
    ("_z_rail_travel", 3),
    ("_rail_nominal_foot_face", 3),
    ("_rail_foot_face", 3),
    ("_rail_hook_lap", 3),
    ("_rail_x", 3),
    ("_rail_channel_span", 3),
    ("rail_catch_air", 3),
    ("_z_rail_heads", 3),
    ("_z_rail_feet", 3),
    ("_rail_keep", 3),
    ("_z_rail_channels", 3),
    ("_lip_ring", 3),
    ("_lip_underwall", 3),
    ("_front_bottom_flank_skin", 3),
    ("_plate_foot", 3),
    ("_plate_foot_clearance", 3),
    ("plate_foot_envelope_clearance", 3),
    ("plate_foot_condenser_clearance", 3),
    ("_back_bottom_flank_skin", 3),
    ("bay_x_span", 3),
    ("_pump_relief_regions", 3),
    ("_front_relief_regions", 3),
    ("_front_relief_cuts", 3),
    ("_front_floor", 3),
    ("_front_flat_lip_drop", 3),
    ("bay_back_y", 3),
    ("_front_top_flank_bedding_cut", 3),
    ("_front_top_flanks", 3),
    ("_back_top_wall", 3),
    ("_back_top_wall_relief_cut", 3),
    ("_back_top_flank_tie_cut", 3),
    ("_flank_body_pockets", 3),
    ("_front_top_flank_pockets", 3),
    ("_back_top_flanks", 3),
    ("_ceiling_tie_reliefs", 3),
    ("_ceiling_cap_reliefs", 3),
    ("_ceiling_tie_channel_relief", 3),
    ("_back_top_ceiling", 3),
    ("cap_split_z", 3),
    ("cap_terminal_opening_z", 3),
    ("cap_crown_z", 3),
    ("cap_terminal_crown_r", 3),
    ("pump_skirt_support_z", 3),
    ("pump_skirt_band_aft_y", 3),
    ("pump_cartridge_aft_y", 3),
    ("_outlet_fore_miter_wedges", 3),
    ("_outlet_under_tangent_wedges", 3),
    ("pump_cartridge_figures", 3),
    ("bay_floor_z", 3),
    ("_flank_lip_drop", 3),
    ("_flank_lip_run", 3),
    ("_bay_floor", 3),
    ("_bulkhead", 3),
    ("_ridge_wall", 3),
    ("_teardrop_y", 3),
    ("build_pump_retainer", 3),
    ("pump_dock_figures", 3),
    ("_floor_bosses", 3),
    ("_east_boss_stem", 3),
    ("_east_wedge", 3),
    ("_east_boss_corbel", 3),
    ("east_boss_wings", 3),
    ("east_boss_pairs", 3),
    ("_east_bar", 3),
    ("_east_bar_support", 3),
    ("_east_boss_support", 3),
    ("east_boss_insert_setback", 3),
    ("east_boss_sleeve_r", 3),
    ("east_sleeve_r", 3),
    ("_east_bosses", 4),
    ("east_boss_bore_end", 4),
    ("_wago_pocket", 4),
    ("_side_wells", 4),
    ("_vent_chase", 4),
    ("_west_cradle", 4),
    ("_cond_cradle_corbel", 4),
    ("_cond_cradle", 4),
    ("_cond_mount_corbel", 4),
    ("_cond_mount", 4),
    ("vent_band", 4),
    ("vent_transoms", 4),
    ("vent_segment", 4),
    ("vent_segments", 4),
    ("vent_grooves", 4),
    ("_vent_runs", 4),
    ("_vent_cutter", 4),
    ("vent_measure", 4),
    ("_flank_vents", 4),
    ("vent_readings", 4),
    ("_core_stop_handhold_air", 4),
    ("_core_stops", 4),
    ("_core_holds", 4),
    ("_core_fit_pocket", 4),
    ("_asse_tie_channel_span", 4),
    ("_asse_square_end", 4),
    ("_asse_cradle", 4),
    ("_digiten_bore", 4),
    ("_valve_socket_cutters", 4),
    ("_valve_trays", 4),
    ("_flow_meter_anchors", 4),
    ("tube_anchor_tie_loop", 5),
    ("_anchor_plane", 5),
    ("tube_anchor_end_columns", 5),
    ("tube_anchor_corbel_depth", 5),
    ("tube_anchor_end_corbel_bounds", 5),
    ("back_top_frames", 5),
    ("back_top_owns", 5),
    ("_tube_anchors", 5),
    ("anchor_capped", 5),
    ("_capped_anchor", 5),
    ("_c14_aperture", 5),
    ("_c14_tunnel_geometry", 5),
    ("keystone_pocket_width", 5),
    ("_keystone_pocket_cut", 5),
    ("_keystone_catches", 5),
    ("_keystone_receptacle_geometry", 5),
    ("_keystone_receptacle", 5),
    ("_c14_tunnel", 5),
    ("_piece_bands", 5),
    ("_seam_fit_reliefs", 5),
    ("build_piece", 5),
    ("_report_facet", 5),
    ("_report_split", 5),
    ("_report_seams", 5),
    ("y_stack_figures", 5),
    ("_report_stacks", 5),
    ("_report_slide", 5),
    ("_handhold_bound", 5),
    ("_ceiling_show_cap_bound", 5),
    ("_silhouette_bound", 5),
    ("stated_box", 5),
    ("_report_columns", 5),
    ("_report_bounds", 5),
    ("_write_docs", 5),
    ("_reading_bounds", 5),
    ("_box_bound_rows", 5),
    ("_box_question_frame", 5),
    ("_lip_lane_boxes", 5),
    ("_lip_lane_tool", 5),
    ("_floor_section_tool", 5),
    ("_under_lip_tool", 5),
    ("box_question_tools", 5),
    ("main", 5),
];

impl Cx {
    /// A function no part has converted yet: its generated definition, called through the namespace,
    /// with its result converted.
    #[cfg(feature = "hybrid")]
    pub fn generated<T: Py>(&self, name: &str, args: Vec<Val>, kwargs: Vec<(&str, Val)>) -> Result<T> {
        let function = self.ns.get(name)?;
        T::from_py(&py::call_kw(&function, args, kwargs)?).with_context(|| format!("enclosure.{name} result"))
    }
}

fn part_function(cx: &Rc<Cx>, part: u8, name: &str) -> Option<Result<Val>> {
    match part {
        1 => p1::function(cx, name),
        2 => p2::function(cx, name),
        3 => p3::function(cx, name),
        4 => p4::function(cx, name),
        5 => p5::function(cx, name),
        _ => None,
    }
}
fn part_converted(part: u8, name: &str) -> bool {
    match part {
        1 => p1::CONVERTED.contains(&name),
        2 => p2::CONVERTED.contains(&name),
        3 => p3::CONVERTED.contains(&name),
        4 => p4::CONVERTED.contains(&name),
        5 => p5::CONVERTED.contains(&name),
        _ => false,
    }
}

/// The hybrid build: the generated module runs and its namespace becomes the module's; every
/// function a part lists in `CONVERTED` is then replaced there by that part's typed wrapper.
#[cfg(feature = "hybrid")]
pub fn install(rt: &Rt, _ns: &Ns) -> Result<()> {
    let base = rt.generated_base(MODULE)?;
    let state = State::from_ns(&base)?;
    let cx = rt.keep(MODULE, Cx { rt: rt.clone(), ns: base.clone(), s: state, memo: Memo::default() });
    for &(name, part) in FUNCTIONS {
        if part_converted(part, name) {
            let function = part_function(&cx, part, name)
                .with_context(|| format!("enclosure.{name} is converted but has no wrapper"))??;
            base.set(name, function)?;
        }
    }
    Ok(())
}

/// The final build: the whole top level, typed, in source order.
#[cfg(not(feature = "hybrid"))]
pub fn install(_rt: &Rt, _ns: &Ns) -> Result<()> {
    anyhow::bail!("enclosure: the typed top level is not written")
}

/// `if __name__ == "__main__"`: the enclosure step.
pub fn main_block(rt: &Rt) -> Result<()> {
    let generate = rt.member("_enclosure_rust_driver", "main")?;
    py::call(&generate, vec![])?;
    Ok(())
}
