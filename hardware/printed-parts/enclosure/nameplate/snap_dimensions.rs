//! Nameplate mount coordinates: plate back Y=0, face +Y, height +Z.
use serde_json::{Value, json};

pub fn dimensions(width: f64, height: f64, thick: f64, slip: f64, supported: f64, proud: f64) -> Value {
    let mouth_w = width + 2. * slip;
    let mouth_h = height + 2. * slip;
    json!({
        "width":width,"height":height,"thick":thick,"corner":5.,
        "slip":slip,"supported":supported,
        "frame_width":mouth_w+6.,"frame_bottom":-mouth_h/2.-3.-supported,
        "frame_top":mouth_h/2.+proud+3.,"frame_corner":7.,
        "floor_rear":-3.,"floor_stock":3.,"insert_stock_rear":-4.64,"insert_stock_radius":6.,
        "field_proud":proud,"crown_y":thick-proud,"mouth_width":mouth_w,"mouth_height":mouth_h,
        "stations":[[-33.,-39.],[33.,-39.],[-33.,39.],[33.,39.]],
        "clearance_diameter":3.4,"counterbore_diameter":6.2,"counterbore_depth":1.,
        "screw_length":6.,"screw_diameter":3.,"head_diameter":5.5,"head_height":3.,
        "hex_key":2.5,"insert_diameter":4.6,"insert_length":4.,
        "pilot_diameter":4.,"pilot_rear":-4.64
    })
}
