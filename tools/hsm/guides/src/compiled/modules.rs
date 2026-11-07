use super::*;
mod common;
mod faucet_book;
mod fill_scene;
mod hold_scene;
mod ice_scene;
mod insertion_actions;
mod preflight;
mod press;
pub fn documentation(name: &str) -> Option<&'static str> {
    match name {
        "fill_scene" => Some(
            "Render concentrate bottles, the closed funnel and a framed Fill screen from the current appliance.",
        ),
        "hold_scene" => Some(
            "Draw the app's phone-at-the-faucet illustration from the faucet's source solids.\n\nThe fixed front camera looks down 15 degrees. The phone lies parallel to the\ndisplay, turned 34 degrees toward the hand. A continuous housing silhouette,\nthe cover's front bezel and aperture, the recessed glass, and the three tube\nmouths carry separate pen weights. The app supplies the template image's color.\n\nRegenerate with tools/cad-venv/bin/python tools/install-guide/hold_scene.py.\nAn optional output path writes a study without replacing the app asset.",
        ),
        "ice_scene" => Some("Model and render ice in the owner guides' frozen first-pour scene."),
        "insertion_actions" => {
            Some("Render the cord and bottle insertion poses from the frozen installation meshes.")
        }
        "preflight" => {
            Some("Check the 9 x 7 inch landscape PDFs, navigation, bleed and print artwork.")
        }
        "press" => Some("Lulu Small Landscape perfect-bound editions and ordering bundle."),
        "faucet_book" => Some(
            "Draw the faucet shop book and its rear-display wiring plate by hand.\n\nThis is a manual document tool. It has no CAD imports or build-system target.\nThe PDF and SVG share one wiring illustration; the source receipt records the\nprocedures and firmware reviewed for this edition.",
        ),
        "common" => Some(
            "Shared vector page furniture for hand-authored Letter shop guides.\n\nManual document tools live outside the hardware generator inventory. Typography,\nprint calibration and drawing primitives are shared; operations and pictures are\nowned by each guide. No geometry or fabrication source is imported here.",
        ),
        _ => None,
    }
}
pub fn source(name: &str) -> Option<&'static str> {
    match name {
        "fill_scene" => Some("tools/install-guide/fill_scene.py"),
        "hold_scene" => Some("tools/install-guide/hold_scene.py"),
        "ice_scene" => Some("tools/install-guide/ice_scene.py"),
        "insertion_actions" => Some("tools/install-guide/insertion_actions.py"),
        "preflight" => Some("tools/install-guide/preflight.py"),
        "press" => Some("tools/install-guide/press.py"),
        "faucet_book" => Some("tools/faucet-assembly-guide/build.py"),
        "common" => Some("tools/assembly-guides/common.py"),
        _ => None,
    }
}
pub fn by_path(path: &str) -> Option<&'static str> {
    if path.ends_with("tools/install-guide/fill_scene.py") {
        return Some("fill_scene");
    }
    if path.ends_with("tools/install-guide/hold_scene.py") {
        return Some("hold_scene");
    }
    if path.ends_with("tools/install-guide/ice_scene.py") {
        return Some("ice_scene");
    }
    if path.ends_with("tools/install-guide/insertion_actions.py") {
        return Some("insertion_actions");
    }
    if path.ends_with("tools/install-guide/preflight.py") {
        return Some("preflight");
    }
    if path.ends_with("tools/install-guide/press.py") {
        return Some("press");
    }
    if path.ends_with("tools/faucet-assembly-guide/build.py") {
        return Some("faucet_book");
    }
    if path.ends_with("tools/assembly-guides/common.py") {
        return Some("common");
    }
    None
}
pub fn initialize(rt: Runtime, e: Env, name: &str) -> Result<()> {
    match name {
        "fill_scene" => fill_scene::initialize(rt, e),
        "hold_scene" => hold_scene::initialize(rt, e),
        "ice_scene" => ice_scene::initialize(rt, e),
        "insertion_actions" => insertion_actions::initialize(rt, e),
        "preflight" => preflight::initialize(rt, e),
        "press" => press::initialize(rt, e),
        "faucet_book" => faucet_book::initialize(rt, e),
        "common" => common::initialize(rt, e),
        _ => bail!("unknown guide module {name}"),
    }
}
pub fn entrypoint(rt: Runtime, e: Env, name: &str) -> Result<Val> {
    match name {
        "fill_scene" => fill_scene::entrypoint(rt, e),
        "hold_scene" => hold_scene::entrypoint(rt, e),
        "ice_scene" => ice_scene::entrypoint(rt, e),
        "insertion_actions" => insertion_actions::entrypoint(rt, e),
        "preflight" => preflight::entrypoint(rt, e),
        "press" => press::entrypoint(rt, e),
        "faucet_book" => faucet_book::entrypoint(rt, e),
        "common" => common::entrypoint(rt, e),
        _ => bail!("unknown guide entrypoint {name}"),
    }
}
