//! How the core is drawn: each body in its material's colour, a see-through material at its
//! alpha, and each line in the colour of the spool it is cut from; the share of the viewer's
//! deflection budget the drawn surfaces are simplified to; and the printed casing pieces, which
//! the core draws with their own print surfaces.
use hsm_cold_core_catalog::Colour;

/// The drawn surfaces are simplified to this share of the viewer's deflection budget.
pub const SIMPLIFICATION_FRACTION: f64 = 0.5;

/// The pieces drawn at their own part's viewer budget rather than the assembly's: reservoir B's
/// fill holder, small beside the core.
pub const PART_BUDGET: [&str; 1] = ["reservoir-b-fill-guide"];

/// The printed casing pieces the core draws with the surfaces their own print payloads cut, each
/// with that payload's file.
pub const PRINTED_SURFACES: [(&str, &str); 4] = [
    ("foam-shell", "hardware/printed-parts/cold-core/foam-shell/foam-shell.step.mesh"),
    ("foam-cap-lid-top", "hardware/printed-parts/cold-core/foam-cap/foam-cap-lid-top.step.mesh"),
    ("foam-cap-bottom", "hardware/printed-parts/cold-core/foam-cap/foam-cap-bottom.step.mesh"),
    ("reservoir-b-fill-guide", "hardware/printed-parts/cold-core/foam-cap/reservoir-b-fill-guide.step.mesh"),
];

/// The spool each line is cut from, in the routing catalog's names: tap water's white, carbonated
/// water's blue, CO2's red and the flavours' black.
pub fn line_spool(line: &str) -> &'static str {
    match line {
        "water-in" => "white",
        "carb-water-out" => "blue",
        "co2-in" => "red",
        _ => "black",
    }
}

/// The spool the reservoirs' air tubes are cut from.
pub const AIR_TUBE_SPOOL: &str = "drain-white";

/// The alpha a viewer's file records for a colour: at single precision.
pub fn recorded_alpha(colour: Colour) -> f64 {
    colour.alpha as f32 as f64
}
