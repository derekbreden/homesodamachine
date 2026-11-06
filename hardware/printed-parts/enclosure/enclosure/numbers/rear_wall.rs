//! The rear wall's numbers the pieces' prints take: the keystone jack, the identification tiles
//! and their rails, the nameplate's plate and the wing nameplate's lips, and the plain lands they
//! leave on the rear face for the front pieces' flutes.
use crate::catalog::{slip, supported};
use crate::layout::layout;
use crate::quadrant::sorted;
use crate::shell::WALL;
use crate::disposal::disposal_field;
use crate::{Bounds, P2};

/// The IEC C14 inlet: its flange across its noses and its long flats, the chord from a nose to a
/// flat's end, its ears' centres off its axis, the knuckle round between flat and taper, and its
/// thickness; its body behind the flange, the chamfers on its lower edges and the rounds on its
/// upper ones. Two washer-backed screws carry the flange on short inserts.
pub mod c14 {
    pub const FLANGE_W: f64 = 49.77;
    pub const FLANGE_H: f64 = 21.9;
    pub const FLANGE_END_CHORD: f64 = 17.98;
    pub const EAR_CX: f64 = 20.0;
    pub const KNUCKLE_R: f64 = 1.2;
    pub const FLANGE_T: f64 = 3.25;
    pub const BODY_W: f64 = 26.10;
    pub const BODY_H: f64 = 18.00;
    pub const BODY_CHAMFER_LEG: f64 = 4.85;
    pub const BODY_TOP_R: f64 = 1.0;
    pub const BOSS_DEPTH: f64 = 10.25;
    pub const PILOT_DEPTH: f64 = 7.25;
}

/// The keystone jack: its face, the lip it latches behind, the pocket its body swings into and
/// that pocket's rise off the face's centre, its depth to the catches, the ease over the
/// aperture and the face it leaves over the aperture's top edge, each catch's height and how
/// proud it stands, and the receptacle's wall and the jack's own slip in it.
pub mod keystone {
    pub const FACE_W: f64 = 14.5;
    pub const FACE_H: f64 = 16.0;
    pub const LIP_D: f64 = 3.0;
    pub const POCKET_W: f64 = 14.9;
    pub const POCKET_H: f64 = 24.4;
    pub const POCKET_RISE: f64 = 1.67;
    pub const DEPTH: f64 = 9.7;
    pub const EASE_DEG: f64 = 50.0;
    pub const EASE_SHOULDER: f64 = 1.0;
    pub const CATCH_UPPER: (f64, f64) = (2.0, 1.4);
    pub const CATCH_LOWER: (f64, f64) = (2.6, 1.3);
    pub const RECEPTACLE_WALL: f64 = 3.0;
    pub const FIT_SLIP: f64 = 0.25;
}

/// The identification tiles: their slip across their channels, the stock each rail keeps outside
/// a channel, how far a rail's bound stands inside a tile's edge, the headroom a channel runs
/// past the roof, and the planes a channel, a rail's root and a rail's bound run between.
pub const TILE_SLIP: f64 = 0.3;
pub const RAIL_STOCK: f64 = 3.0;
pub const RAIL_INSET: f64 = 2.0;
pub const CHANNEL_HEADROOM: f64 = 2.0;
pub const CHANNEL_Y: P2 = [469.299, 472.799];
pub const ROOT_Y: P2 = [469.299, 471.31];
pub const BOUND_Y: P2 = [471.3, 474.3];

/// The rear nameplate: its plate, and how proud of the wall its raised field stands.
pub const PLATE_WIDTH: f64 = 88.0;
pub const PLATE_HEIGHT: f64 = 100.0;
pub const PLATE_THICK: f64 = 3.36;
pub const FIELD_PROUD: f64 = 2.0;

/// The wing nameplate's retaining lips the front pieces' rail lands keep: each wing's projection
/// past the plate's edge and its span, the air at the plate's edge, and the margin round a lip.
pub const WING_PROJECTION: f64 = 2.40;
pub const WING_SPAN: f64 = 30.0;
pub const WING_FACE_AIR: f64 = 0.15;
pub const LIP_MARGIN: f64 = 0.4;

/// The flat land round the jack's aperture on the rear face: the flutes stay off its lip and the
/// ease over the aperture, one wall past each edge.
pub fn keystone_land() -> Bounds {
    use keystone::*;
    let [x, y, z] = layout().rear_wall.dry_openings.keystone.face_center_mm;
    let half_w = FACE_W / 2.0 + slip() + WALL;
    let half_h = FACE_H / 2.0 + slip() + WALL;
    [x - half_w, x + half_w, y - 3.0, y + 1.0, z - half_h, z + half_h + EASE_SHOULDER]
}

/// The two tile channels, one per fluid column, from the channel floor through the roof.
pub fn label_channels() -> Vec<Bounds> {
    let l = layout();
    let id = &l.rear_identification;
    let half = (id.width_mm + TILE_SLIP) / 2.0;
    let (floor, roof) = (id.channel_floor_z_mm, l.enclosure.roof_z_mm + CHANNEL_HEADROOM);
    l.fluid_grid.columns_x_mm.iter().map(|&x| [x - half, x + half, CHANNEL_Y[0], CHANNEL_Y[1], floor, roof]).collect()
}

/// The three rails beside and between the two channels: each `half` off its column's axis on
/// its channel side, one rail's stock past the outer channel edges.
fn rails(half: f64, [y0, y1]: P2) -> [Bounds; 3] {
    let l = layout();
    let id = &l.rear_identification;
    let [west, east] = <[f64; 2]>::try_from(l.fluid_grid.columns_x_mm.as_slice()).expect("the tile rails span two columns");
    let edge = (id.width_mm + TILE_SLIP) / 2.0 + RAIL_STOCK;
    let (floor, roof) = (id.channel_floor_z_mm, l.enclosure.roof_z_mm);
    [[west - edge, west - half, y0, y1, floor, roof], [west + half, east - half, y0, y1, floor, roof],
     [east + half, east + edge, y0, y1, floor, roof]]
}

/// The rails' full roots outside the sliding tile channels, into the rear corner stock.
pub fn rail_roots() -> [Bounds; 3] {
    rails((layout().rear_identification.width_mm + TILE_SLIP) / 2.0, ROOT_Y)
}

/// The rails' bounds proud of the rear face, over the tiles' edges.
pub fn rail_bounds() -> [Bounds; 3] {
    rails(layout().rear_identification.width_mm / 2.0 - RAIL_INSET, BOUND_Y)
}

/// The wing nameplate's two retaining lips, each round one wing from the plate's edge to past its
/// tip, through the plate's thickness to past its face.
pub fn wing_lips() -> [Bounds; 2] {
    let p = &layout().rear_identification.nameplate;
    let (x, z, face) = (p.center_x_mm, p.center_z_mm, p.face_y_mm);
    let tip_air = WING_FACE_AIR + slip();
    [-1.0, 1.0].map(|side| {
        let (x0, x1) = sorted(side * (PLATE_WIDTH / 2.0 + WING_FACE_AIR), side * (PLATE_WIDTH / 2.0 + WING_PROJECTION + tip_air));
        [x + x0 - LIP_MARGIN, x + x1 + LIP_MARGIN, face - PLATE_THICK - slip(), face + 1.0,
         z - WING_SPAN / 2.0 - slip() - supported() - LIP_MARGIN, z + WING_SPAN / 2.0 + slip() + LIP_MARGIN]
    })
}

/// The front pieces' plain lands on the rear face: the warning's field, the wing nameplate's
/// lips, the tile rails' bounds and the keystone's land.
pub fn front_plain(outer: &Bounds) -> Vec<Bounds> {
    let mut plain = vec![disposal_field(outer)];
    plain.extend(wing_lips());
    plain.extend(rail_bounds());
    plain.push(keystone_land());
    plain
}
