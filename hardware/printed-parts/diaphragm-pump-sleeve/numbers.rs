//! The diaphragm pump sleeve's numbers, in millimetres: the TPU elbow that takes a G Ganen pump
//! port's barb in one round socket and 1/4" LLDPE tube in the other, turned a quarter turn, with a
//! flat foot across its outer corner so it stands as a V with both mouths up. Local frame: the
//! barb's tip at the origin, +X out along the barb, +Y the way the tube leaves.

/// The barb socket: its relaxed bore, sized against the scanned G Ganen barbs, and how deep the
/// barb enters.
pub const BARB_BORE: f64 = 9.0;
pub const BARB_DEPTH: f64 = 11.0;
/// The tube the sleeve takes, and the tube socket's relaxed bore and depth.
pub const TUBE_D: f64 = 6.35;
pub const TUBE_BORE: f64 = 6.10;
pub const TUBE_DEPTH: f64 = 15.0;
/// The passage between the sockets.
pub const PASSAGE: f64 = 4.40;
/// The least wall round either socket.
pub const MIN_WALL: f64 = 2.80;
/// The tube's stop below the tube socket, where the passage turns up into it.
pub const TUBE_STOP: f64 = 3.50;
/// The neck that blends the barb socket's round into the tube socket's: its length past the stop.
pub const NECK_PAST_STOP: f64 = 3.0;
/// The clamp band each socket takes on its plain outside, and the air left beside it.
pub const CLAMP_BAND: f64 = 9.0;
pub const BAND_AIR: f64 = 1.0;
/// Each mouth's lead-in: how far it opens, at the angle it opens on.
pub const ENTRY: f64 = 0.40;
pub const ENTRY_ANGLE_DEG: f64 = 60.;
/// The sleeve's colour: Siraya Tech Flex TPU 85A Clear, as sRGB.
pub const COLOUR_SRGB: [f64; 3] = [0.92, 0.92, 0.90];

/// The barb socket's outside.
pub fn barb_od() -> f64 {
    BARB_BORE + 2.0 * MIN_WALL
}

/// The tube socket's outside.
pub fn tube_od() -> f64 {
    TUBE_BORE + 2.0 * MIN_WALL
}

/// The tube socket's mouth along +Y.
pub fn tube_mouth() -> f64 {
    TUBE_STOP + TUBE_DEPTH
}

/// The neck's length along +Y.
pub fn neck_length() -> f64 {
    TUBE_STOP + NECK_PAST_STOP
}

/// How tall each mouth's lead-in is.
pub fn entry_height() -> f64 {
    ENTRY * ENTRY_ANGLE_DEG.to_radians().tan()
}

/// The tube socket's outside once the tube opens its bore.
fn tube_installed_od() -> f64 {
    (tube_od().powi(2) + TUBE_D.powi(2) - TUBE_BORE.powi(2)).sqrt()
}

/// Where the tube's axis stands along +X past the barb's tip: the barb's band, its air, and the
/// installed tube socket's half width beyond it.
pub fn tube_axis() -> f64 {
    -(BARB_DEPTH - CLAMP_BAND) + BAND_AIR + tube_installed_od() / 2.0
}

/// How far the foot's cut stands from the elbow's corner, along each axis.
pub fn foot() -> f64 {
    tube_axis() / 2_f64.sqrt() + PASSAGE / 2.0 + MIN_WALL
}

/// The foot's cutter, square, across.
pub fn foot_span() -> f64 {
    4.0 * (BARB_DEPTH + tube_mouth())
}

/// The print pose's turn: the sine and cosine of a half right angle.
pub fn print_s() -> f64 {
    1.0 / 2_f64.sqrt()
}

/// The posed body's move onto the bed, centred along X.
pub fn print_shift() -> [f64; 3] {
    let q = print_s();
    let xmin = (-BARB_DEPTH - barb_od() / 2.0) * q;
    let xmax = (tube_axis() + tube_od() / 2.0 + tube_mouth()) * q;
    [-(xmin + xmax) / 2.0, 0.0, foot()]
}
