//! The tube collars' numbers, in millimetres. A collar rides a tail of 1/4" LLDPE and carries its
//! station's word on three faces, in the bulkhead ring's lettering, so a word changed on the wall
//! is changed on the tube by the same edit. It prints flat face down, its bore's axis along the bed.
//! The canonical frame has the bore on Y, the flag's flat top at Z = `RISE` and the rounded
//! underside below the axis.
use hsm_bulkhead_ring_numbers as ring;

/// The 1/4" LLDPE the collars ride, nominal, and what a spool holds it to.
pub const TUBE_OD: f64 = 6.35;
pub const LLDPE_TOL: f64 = 0.13;
/// What the printer takes off the bore's diameter, calipered on a finished collar: the crown of a
/// bore printed along the bed sags into it.
pub const BORE_SHRINK: f64 = 0.10;
/// What the bore clears the biggest tube by, once the sag has had it.
pub const SLIP: f64 = 0.10;
/// The bore, as the slicer is handed it: the top of the tube's band, the sag and the slip.
pub const BORE: f64 = TUBE_OD + LLDPE_TOL + BORE_SHRINK + SLIP;
/// The 4 mm tails' bore: the drain's and the flavor pair's.
pub const SMALL_BORE: f64 = 4.0 + 0.0762 + BORE_SHRINK + SLIP;
/// The collar's width, and the diameter of the half round below the axis.
pub const OD: f64 = 12.0;
/// How far the flag stands above the axis: the band a port's word is lettered in.
pub const RISE: f64 = ring::RING_W;
/// The run along the tube.
pub const LENGTH: f64 = 30.0;
/// How deep a word's recess is cut, what the flat keeps clear round it, and the lettering's size.
pub const WORD_DEPTH: f64 = ring::WORD_DEPTH;
pub const WORD_MARGIN: f64 = ring::WORD_MARGIN;
pub const WORD_SIZE: f64 = ring::WORD_SIZE;
/// The faces a word is lettered on.
pub const FACES: [&str; 3] = ["top", "+x", "-x"];
/// The words' outlines, as the rear labels draw them.
pub const ARTWORK: &str = "hardware/printed-parts/enclosure/rear-identification/label-words.json";

/// Each collar: its station, the tube it rides and the bench that threads it on. Its word and its
/// filaments are the ring's for that station.
pub const COLLARS: [(&str, &str, &str); 6] = [
    ("water", "the customer's tap-water run, up to their angle stop", "pack bench"),
    ("carb", "the umbilical's blue carbonated-water tail", "faucet bench"),
    ("co2", "the customer's red tether, +Y wall of back-top to regulator", "pack bench"),
    ("flavor-a", "the umbilical's first black flavour tail", "faucet bench"),
    ("flavor-b", "the umbilical's second black flavour tail", "faucet bench"),
    ("drain", "the umbilical's white 4 mm vent tail", "faucet bench"),
];

/// The collar for `station`'s bore.
pub fn bore(station: &str) -> f64 {
    if ["drain", "flavor-a", "flavor-b"].contains(&station) { SMALL_BORE } else { BORE }
}

/// `station`'s word and the key its filaments are read under, from the ring.
pub fn word_and_fluid(station: &str) -> (&'static str, &'static str) {
    let (_, word, fluid) = ring::STATIONS.iter().find(|(s, _, _)| *s == station).expect("a ring station");
    (word, fluid)
}

/// The bore the tube meets, once the printer's sag has had it.
pub const BORE_PRINTED: f64 = BORE - BORE_SHRINK;
/// The colour between the bore and each flat, and what is left behind a word.
pub const WALL: f64 = (OD - BORE) / 2.0;
pub const BACKING: f64 = WALL - WORD_DEPTH;
/// The play on the loosest tube.
pub const CLEARANCE: f64 = BORE_PRINTED - (TUBE_OD - LLDPE_TOL);
