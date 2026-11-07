use super::*;
mod _cad_art;
mod _cad_art_mesh;
mod _install_art;
mod _install_art_mesh;
mod common;
mod cylinder_actions;
mod faucet_book;
mod fill_scene;
mod hold_scene;
mod ice_scene;
mod insertion_actions;
mod preflight;
mod press;
mod scenes;
mod startup;
pub fn documentation(name: &str) -> Option<&'static str> {
    match name {
        "_cad_art" => Some(
            "Render the install guide's focused, customer-facing CAD pictures.\n\nThe production models carry more geometry than an instruction frame needs. This module keeps the\nexact touched parts and makes four deliberate presentation cuts:\n\n- the faucet's source lever is a union of rest + pressed states for collision checking, so the\n  customer views reconstruct one physical state at a time from the same dimensions;\n- invisible tube tails are clipped at the countertop for the user-side faucet views;\n- the mount sequence keeps the recognizable full faucet for the lowering event, then changes once\n  to a fixed, literal below-counter camera for the plate and retained-nut actions;\n- the retained donor washer and nut are plain visual stand-ins because the purchased hardware has\n  no source CAD. Their family installation geometry is shown without using them as dimensional\n  authority.\n\nThe scene payload intermediates live in a temporary directory under ``hardware/``.\nOnly the final PNGs land in ``art/``.\n\n``--mount-studies`` renders only the registered mount frames into ``out/mount-studies/`` for fast\nvisual review without touching the checked-in artwork.",
        ),
        "_cad_art_mesh" => {
            Some("Producer surfaces and authored illustration props for the customer pictures.")
        }
        "_install_art" => Some(
            "Shared installation scene builders and presentation props.\n\nThe cabinet, countertop, CO2 cylinder, filter and power cord are illustration geometry.\nRendered scenes are written to art/; owner documents keep their own print snapshots.\n\n    tools/cad-venv/bin/python hardware/install-guide/_install_art.py\n    tools/cad-venv/bin/python hardware/install-guide/_install_art.py --list\n    tools/cad-venv/bin/python hardware/install-guide/_install_art.py opening cabinet-plan",
        ),
        "_install_art_mesh" => Some(
            "The installation pictures' producer surfaces and illustration props.\n\nProducer meshes keep their normals, face ranges and material colours. Only the\ntwo faucet detail crops pass through the solid kernel, to close their cut ends.\nThese scene payloads serve pictures; they are not measurement models.",
        ),
        "cylinder_actions" => Some(
            "The cylinder connection and startup controls, in the regulator's world frame.\n\n+Y faces the customer, +Z is up, and the cylinder stands at -X. The red tether is\npushed into the regulator's PI010822S at the factory, so the customer's one joint here is\nthe big nut onto the cylinder valve.",
        ),
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
        "scenes" => {
            Some("Compose the cylinder, power, fill and pour pictures for the install guide.")
        }
        "startup" => Some(
            "Draw the cylinder handwheel and the factory-set regulator with both gauges pressurised.",
        ),
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
        "_cad_art" => Some("hardware/install-guide/_cad_art.py"),
        "_cad_art_mesh" => Some("hardware/install-guide/_cad_art_mesh.py"),
        "_install_art" => Some("hardware/install-guide/_install_art.py"),
        "_install_art_mesh" => Some("hardware/install-guide/_install_art_mesh.py"),
        "cylinder_actions" => Some("tools/install-guide/cylinder_actions.py"),
        "fill_scene" => Some("tools/install-guide/fill_scene.py"),
        "hold_scene" => Some("tools/install-guide/hold_scene.py"),
        "ice_scene" => Some("tools/install-guide/ice_scene.py"),
        "insertion_actions" => Some("tools/install-guide/insertion_actions.py"),
        "preflight" => Some("tools/install-guide/preflight.py"),
        "press" => Some("tools/install-guide/press.py"),
        "scenes" => Some("tools/install-guide/scenes.py"),
        "startup" => Some("tools/install-guide/startup.py"),
        "faucet_book" => Some("tools/faucet-assembly-guide/build.py"),
        "common" => Some("tools/assembly-guides/common.py"),
        _ => None,
    }
}
pub fn by_path(path: &str) -> Option<&'static str> {
    if path.ends_with("hardware/install-guide/_cad_art.py") {
        return Some("_cad_art");
    }
    if path.ends_with("hardware/install-guide/_cad_art_mesh.py") {
        return Some("_cad_art_mesh");
    }
    if path.ends_with("hardware/install-guide/_install_art.py") {
        return Some("_install_art");
    }
    if path.ends_with("hardware/install-guide/_install_art_mesh.py") {
        return Some("_install_art_mesh");
    }
    if path.ends_with("tools/install-guide/cylinder_actions.py") {
        return Some("cylinder_actions");
    }
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
    if path.ends_with("tools/install-guide/scenes.py") {
        return Some("scenes");
    }
    if path.ends_with("tools/install-guide/startup.py") {
        return Some("startup");
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
        "_cad_art" => _cad_art::initialize(rt, e),
        "_cad_art_mesh" => _cad_art_mesh::initialize(rt, e),
        "_install_art" => _install_art::initialize(rt, e),
        "_install_art_mesh" => _install_art_mesh::initialize(rt, e),
        "cylinder_actions" => cylinder_actions::initialize(rt, e),
        "fill_scene" => fill_scene::initialize(rt, e),
        "hold_scene" => hold_scene::initialize(rt, e),
        "ice_scene" => ice_scene::initialize(rt, e),
        "insertion_actions" => insertion_actions::initialize(rt, e),
        "preflight" => preflight::initialize(rt, e),
        "press" => press::initialize(rt, e),
        "scenes" => scenes::initialize(rt, e),
        "startup" => startup::initialize(rt, e),
        "faucet_book" => faucet_book::initialize(rt, e),
        "common" => common::initialize(rt, e),
        _ => bail!("unknown guide module {name}"),
    }
}
pub fn entrypoint(rt: Runtime, e: Env, name: &str) -> Result<Val> {
    match name {
        "_cad_art" => _cad_art::entrypoint(rt, e),
        "_cad_art_mesh" => _cad_art_mesh::entrypoint(rt, e),
        "_install_art" => _install_art::entrypoint(rt, e),
        "_install_art_mesh" => _install_art_mesh::entrypoint(rt, e),
        "cylinder_actions" => cylinder_actions::entrypoint(rt, e),
        "fill_scene" => fill_scene::entrypoint(rt, e),
        "hold_scene" => hold_scene::entrypoint(rt, e),
        "ice_scene" => ice_scene::entrypoint(rt, e),
        "insertion_actions" => insertion_actions::entrypoint(rt, e),
        "preflight" => preflight::entrypoint(rt, e),
        "press" => press::entrypoint(rt, e),
        "scenes" => scenes::entrypoint(rt, e),
        "startup" => startup::entrypoint(rt, e),
        "faucet_book" => faucet_book::entrypoint(rt, e),
        "common" => common::entrypoint(rt, e),
        _ => bail!("unknown guide entrypoint {name}"),
    }
}
