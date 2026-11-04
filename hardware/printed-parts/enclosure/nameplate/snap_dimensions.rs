//! Nameplate-local coordinates: plate back Y=0, face +Y, height +Z.
//! The leaves bend in X, within each face-up printed layer.
use serde_json::{Value, json};

pub fn dimensions(width: f64, height: f64, thick: f64, slip: f64, supported: f64) -> Value {
    let half = width / 2.;
    let leaf_outer = half - 2.;
    let mouth_w = width + 2. * slip;
    let mouth_h = height + 2. * slip;
    let bottom = -mouth_h / 2. - 3. - supported;
    let top = mouth_h / 2. + 6.;
    json!({
        "width":width,"height":height,"thick":thick,"corner":5.,
        "slip":slip,"supported":supported,
        "frame_width":mouth_w+6.,"frame_bottom":bottom,"frame_top":top,
        "frame_corner":7.,"floor_rear":-3.6-slip,"floor_stock":3.6,
        "crown_y":thick-3.,"mouth_width":mouth_w,"mouth_height":mouth_h,
        "leaf_inner":leaf_outer-2.,"leaf_outer":leaf_outer,"leaf_thick":2.,
        "leaf_y":[-4.,-2.],"leaf_root_z":-31.5,"leaf_top_z":5.,"root_radius":1.5,
        "root_x":[leaf_outer-3.5,leaf_outer+1.5],"root_z":[-35.5,-31.5],
        "hook_z":[-5.,5.],"hook_projection":1.2,
        "catch_inner":leaf_outer+slip,"catch_front":-slip,"catch_rear":-1.75,
        "pocket_rear":-4.-supported,"pocket_outer":leaf_outer+1.2+supported,
        "root_pocket_outer":leaf_outer+1.5+supported,
        "pocket_inner":leaf_outer-3.5-supported,
        "pocket_bottom":-35.5-supported,"pocket_top":5.+slip+supported,
        "pocket_stock":3.,"release_width_z":6.,
        "release_inner_x":leaf_outer-0.2,"release_outer_x":mouth_w/2.+3.5
    })
}
