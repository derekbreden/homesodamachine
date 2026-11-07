//! The ASSE drain adapter's numbers, in millimetres. The TPU vent cup takes the Multiplex ASSE's
//! vent barb from above, and a quarter turn inside it carries the drain to a horizontal tube
//! socket on −X. Native frame: +Z points up into the vent mouth, Z = 0 at the mouth.

/// The cup's relaxed bore round the vent barb.
pub const BARB_BORE: f64 = 6.10;
/// The tube socket's relaxed bore round the white drain tube.
pub const TUBE_BORE: f64 = 3.80;
/// How far the vent barb reaches into the cup.
pub const INSTALLED_REACH: f64 = 8.6;
/// The conical reducer from the barb bore down to the turn's passage, below the mouth.
pub const REDUCER_LENGTH: f64 = 5.50;
/// The least wall under a tie land's recess.
pub const MIN_WALL: f64 = 3.45;
/// Each tie land: its recess, flat width and the ramp either side.
pub const GROOVE_DEPTH: f64 = 0.50;
pub const GROOVE_FLAT: f64 = 2.80;
pub const GROOVE_RAMP: f64 = 1.0;
/// The cup's tie land, measured down from the barb's tip.
pub const BARB_TIE_FROM_TIP: f64 = 5.5;
/// The tube socket's reach from the vent axis, and its tie land back from the socket's mouth.
pub const ELBOW_REACH: f64 = 25.4;
pub const TUBE_TIE_FROM_MOUTH: f64 = 6.0;
/// The turn's centreline radius.
pub const ELBOW_RADIUS: f64 = 4.05;
/// How far the print flat stands off the outside corner it is cut across.
pub const FLAT_STANDOFF: f64 = 0.6;

/// The cup's outside: the bore with the least wall and a land's recess each side.
pub fn barb_od() -> f64 {
    BARB_BORE + 2. * (MIN_WALL + GROOVE_DEPTH)
}

/// The tube socket's outside.
pub fn tube_od() -> f64 {
    TUBE_BORE + 2. * (MIN_WALL + GROOVE_DEPTH)
}

/// Where the turn starts below the mouth: the reducer's foot.
pub fn turn_start_z() -> f64 {
    -REDUCER_LENGTH
}

/// The tube socket's axis below the mouth: past the reducer and round the turn.
pub fn socket_drop() -> f64 {
    REDUCER_LENGTH + ELBOW_RADIUS
}

/// The two tie lands' centres: the cup's along +Z from the mouth, the socket's along its axis
/// from the vent axis.
pub fn groove_centres() -> [f64; 2] {
    [INSTALLED_REACH - BARB_TIE_FROM_TIP, ELBOW_REACH - TUBE_TIE_FROM_MOUTH]
}

/// The print flat's height in the frame tipped for printing: across the corner between the cup's
/// foot and the socket's underside.
pub fn flat_z() -> f64 {
    -(barb_od() / 2. + socket_drop() + tube_od() / 2.) / 2_f64.sqrt() + FLAT_STANDOFF
}

/// The tipped body's move onto the bed, centred on its footprint in X.
pub fn print_shift() -> [f64; 3] {
    let (rb, rt) = (barb_od() / 2., tube_od() / 2.);
    [(ELBOW_REACH + socket_drop() + rt - rb - INSTALLED_REACH) / (2. * 2_f64.sqrt()), 0., -flat_z()]
}
