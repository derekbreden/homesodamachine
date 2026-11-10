//! Publish numerical interfaces for native SolidCraft designs without building the machine.
use hsm_aero_float_numbers as f;
use hsm_carbonator_numbers::{self as c, bond as b};
use hsm_carbonator_tube_numbers as tube;
use hsm_coil_numbers::{self as coil, Segment, Tail};
use hsm_cold_core_assembly_numbers as a;
use hsm_endcap_circular_numbers as cap;
use hsm_reed_bridge_numbers as bridge;
use serde_json::{Value, json};
use std::{error::Error, fs, path::Path};
mod build;
mod display;

fn local(mut point: [f64; 3]) -> [f64; 3] {
    point[2] -= c::BOTTOM_Z;
    point
}
fn swatch(colour: hsm_cold_core_catalog::Colour) -> Value {
    json!(colour.linear.map(|v| {
        ((if v <= 0.0031308 {
            12.92 * v
        } else {
            1.055 * v.powf(1. / 2.4) - 0.055
        }) * 255.)
            .round() as u8
    }))
}
fn tail(t: Tail) -> Value {
    let form = coil::tail_form(t, false);
    json!({"name":t.name(),"segments":form.segments.iter().map(|s|match s{
  Segment::Bend{id,start,end,mid,radius,degrees,..}=>json!({"type":"arc","id":id,"start":local(*start),"end":local(*end),"mid":local(*mid),"radius":radius,"degrees":degrees}),
  Segment::Straight{id,start,end,length}=>json!({"type":"line","id":id,"start":local(*start),"end":local(*end),"length":length})
 }).collect::<Vec<_>>()})
}
fn main() -> Result<(), Box<dyn Error>> {
    if std::env::args().nth(1).as_deref() == Some("display") {
        return display::run();
    }
    let rod = hsm_cold_core_data::rod();
    let length = rod["finished_length"].as_f64().ok_or("rod length")? * cap::INCH;
    let point_angle = rod["register_point_degrees"]
        .as_f64()
        .ok_or("register point angle")?;
    let seat = c::REGISTER_DEPTH - (c::ROD_DIAMETER / 2.) / (point_angle / 2.).to_radians().tan();
    let rod_bottom = c::BOTTOM_PLATE_Z[1] - c::BOTTOM_Z - seat;
    let float_at = local(a::carbonator_float());
    let register = c::rod_xy();
    let bond = b::datums(c::TOP_PLATE_Z[1] - c::BOTTOM_Z);
    let segments = (coil::WRAPS * f64::from(coil::SAMPLES_PER_TURN)).ceil() as usize;
    let points = (0..=segments)
        .map(|i| {
            let turn = coil::WRAPS * i as f64 / segments as f64;
            let angle = coil::INLET_AZIMUTH + 360. * turn;
            let z = coil::LOW_Z + coil::PITCH * turn;
            local(coil::at(angle, z, coil::ride_radius(angle, z)))
        })
        .collect::<Vec<_>>();
    let plan = (0..=bridge::PLAN_SEGMENTS)
        .map(|i| {
            let angle = -bridge::bridge_half_angle()
                + 2. * bridge::bridge_half_angle() * f64::from(i)
                    / f64::from(bridge::PLAN_SEGMENTS);
            let r = bridge::plan_radius(angle);
            [r * angle.cos(), r * angle.sin()]
        })
        .collect::<Vec<_>>();
    let body = json!({
     "frame":{"origin":"bottom tube rim","axis":"Z","sensor_azimuth":-90.},
     "tube":{"outer_diameter":tube::OD,"bore_diameter":tube::ID,"length":tube::LENGTH,"wall":tube::WALL},
     "cap":{"diameter":c::PLATE_DIAMETER,"thickness":c::PLATE_THICKNESS,"recess":c::PLATE_RECESS,
      "port_diameter":c::PORT_TAP_DIAMETER,"port_spacing":cap::HOLE_SPACING_IN*cap::INCH,
      "register_xy":register,"register_diameter":c::REGISTER_DIAMETER,"register_depth":c::REGISTER_DEPTH,
      "register_point_angle":point_angle,"register_cone_height":c::REGISTER_DIAMETER/2./(point_angle/2.).to_radians().tan()},
     "rod":{"diameter":c::ROD_DIAMETER,"length":length,"bottom":rod_bottom,"top":rod_bottom+length,
      "register_seat_depth":seat,"upper_engagement":rod_bottom+length-(c::INTERIOR_Z[1]-c::BOTTOM_Z),
      "seat_clearance":(c::INTERIOR_Z[1]-c::BOTTOM_Z+seat)-(rod_bottom+length)},
     "stop":{"diameter":c::UPPER_STOP_DIAMETER,"bore":c::UPPER_STOP_BORE,"height":c::UPPER_STOP_HEIGHT},
     "float":{"diameter":f::DIAMETER,"height":f::height(),"bore":f::BORE_DIAMETER,"at":float_at,
      "pocket_od":f::POCKET_OD,"pocket_id":f::POCKET_ID,"pocket_depth":f::POCKET_DEPTH,
      "magnet_seat":f::magnet_seat(),"magnet_od":f::MAGNET_OD,"magnet_id":f::MAGNET_ID,"magnet_thickness":f::MAGNET_THICKNESS,
      "travel":[c::BOTTOM_PLATE_Z[1]-c::BOTTOM_Z+f::height()/2.,c::INTERIOR_Z[1]-c::BOTTOM_Z-c::UPPER_STOP_HEIGHT-f::height()/2.]},
     "ports":c::ports().iter().map(|p|json!({"name":p.name,"top":p.plate==c::Plate::Top,"corner":local(p.corner),"up":p.up,"out":p.out,"mouth":local(p.mouth),"male_tip":local(p.male_tip()),"axis_offset":p.axis_offset(),"male_length":p.male_length()})).collect::<Vec<_>>(),
     "street_elbow":{"hex":c::street_elbow::HEX_AF,"leg":c::street_elbow::LEG,"bore":c::street_elbow::BORE,"male_radius":c::street_elbow::MALE_RADIUS,"male_length":c::street_elbow::MALE_LENGTH,"socket_radius":c::street_elbow::SOCKET_RADIUS,"socket_depth":c::street_elbow::SOCKET_DEPTH},
     "male_elbow":{"thread":c::male_elbow::THREAD,"height":c::male_elbow::HEIGHT,"diameter":c::male_elbow::BODY_DIAMETER,"length":c::male_elbow::LENGTH,"post":c::male_elbow::POST_WIDTH,"insertion":c::male_elbow::INSERTION,"bore":c::male_elbow::FLOW_BORE,"tube":c::male_elbow::TUBE_OD,"axis_reach":c::male_elbow::AXIS_REACH,"mouth_reach":c::male_elbow::MOUTH_REACH},
     "prv":{"hex":c::prv::HEX_AF,"hex_height":c::prv::HEX_HEIGHT,"cap_radius":c::prv::CAP_RADIUS,"cap_height":c::prv::CAP_HEIGHT,"male_length":c::prv::MALE_LENGTH},
     "shroud":{"outer_diameter":hsm_prv_shroud_numbers::outer_diameter(),"inner_diameter":hsm_prv_shroud_numbers::inner_diameter(),"length":hsm_prv_shroud_numbers::TOTAL_LENGTH,"cavity":hsm_prv_shroud_numbers::CAVITY_LENGTH,"vent_diameter":hsm_prv_shroud_numbers::vent_hole_diameter(),"vent_z":hsm_prv_shroud_numbers::VENT_STATION_Z,"supported_surface":hsm_cold_core_catalog::fits().supported_surface},
     "adapter":{"collet_diameter":c::collet::COLLET_DIAMETER,"collet_length":c::collet::COLLET_LENGTH,"hex_corners":c::collet::HEX_ACROSS_CORNERS,"hex_length":c::collet::HEX_LENGTH,"shank_diameter":c::collet::SHANK_DIAMETER,"shank_length":c::collet::SHANK_LENGTH,"standoff":c::collet::STANDOFF},
     "jet":{"diameter":c::jet::CAP_DIAMETER,"height":c::jet::CAP_THICKNESS,"bore":c::jet::PASSAGE_DIAMETER},
     "bond":{"contact":bond.contact_point,"out":bond.contact_outward,"screw_axis":bond.screw_axis,"screw_underhead":bond.screw_underhead,"wire_exit":bond.wire_exit,
      "tap":b::TAP_DRILL_DIAMETER,"thread":b::THREAD_DIAMETER,"screw_length":b::SCREW_LENGTH,"head_diameter":b::SCREW_HEAD_DIAMETER,"head_height":b::SCREW_HEAD_HEIGHT,
      "ring_eye":b::RING_EYE_DIAMETER,"ring_thickness":b::RING_TONGUE_THICKNESS,"ring_barrel":b::RING_BARREL_DIAMETER,"ring_barrel_length":b::RING_BARREL_LENGTH,
      "washer_od":b::WASHER_DIAMETER,"washer_bore":b::WASHER_BORE,"washer_thickness":b::WASHER_THICKNESS},
     "colours":{"stainless":swatch(c::street_elbow_colour()),"pushfit":swatch(c::male_elbow_colour()),"brass":swatch(c::prv_colour()),"copper":swatch(hsm_cold_core_catalog::copper())},
     "coil":{"tube_diameter":coil::TUBE_OD,"wall":0.031*cap::INCH,"wall_source":"hardware/assembly/handwork.md","radius":coil::WIND_RADIUS,"turns":coil::WRAPS,"pitch":coil::PITCH,
      "bottom":coil::LOW_Z-c::BOTTOM_Z,"top":coil::HIGH_Z-c::BOTTOM_Z,"points":points,"tails":[tail(Tail::Inlet),tail(Tail::Outlet)],
      "bridge_lift":coil::bridge_lift()},
     "reeds":{"length":a::REED_LENGTH,"diameter":a::REED_RADIUS*2.,"positions":a::carbonator_reeds().map(local)},
     "probes":{"width":a::to92::WIDTH,"height":a::to92::HEIGHT,"corner":a::to92::CORNER_RADIUS,"carbonator":local(a::carbonator_probe()),"coil":local(a::coil_probe())},
     "bridge":{"inner":bridge::inner_radius(),"skirt":bridge::skirt_radius(),"plateau":bridge::plateau_radius(),
      "bottom":bridge::bridge_z_bottom(),"top":bridge::bridge_z_top(),"plateau_bottom":bridge::plateau_z_bottom(),"plateau_top":bridge::plateau_z_top(),
      "pocket_length":bridge::pocket_length(),"pocket_width":bridge::pocket_width(),"reed_z":[bridge::reed_low_z(),bridge::reed_high_z()],
      "groove_width":bridge::LEAD_GROOVE_WIDTH,"groove_y":bridge::LEAD_GROOVE_Y,"notch_length":bridge::LEAD_NOTCH_LENGTH,"plan":plan}
    });
    let output = Path::new("hardware/reference/carbonator-core/solidcraft/contracts.json");
    fs::write(output, serde_json::to_string_pretty(&body)? + "\n")?;
    println!("{}", output.display());
    if std::env::args().nth(1).as_deref() == Some("build") {
        build::run()?;
    }
    Ok(())
}
