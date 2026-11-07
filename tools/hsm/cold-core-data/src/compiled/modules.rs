use super::*;
#[path = "carbonator_tube_step.rs"]
mod m_carbonator_tube_step;
#[path = "carbonator_vessel_drawing.rs"]
mod m_carbonator_vessel_drawing;
#[path = "coil_mandrel.rs"]
mod m_coil_mandrel;
#[path = "endcap_circular_drawing.rs"]
mod m_endcap_circular_drawing;
#[path = "endcap_circular_dxf.rs"]
mod m_endcap_circular_dxf;
#[path = "evaporator_coil_drawing.rs"]
mod m_evaporator_coil_drawing;
#[path = "float_rod_drawing.rs"]
mod m_float_rod_drawing;
#[path = "integration.rs"]
mod m_integration;
#[path = "magnetic_float.rs"]
mod m_magnetic_float;
#[path = "_above_core_mounts.rs"]
mod m_private_above_core_mounts;
#[path = "_carbonator.rs"]
mod m_private_carbonator;
#[path = "_cold_core_interface.rs"]
mod m_private_cold_core_interface;
#[path = "_cold_scorecard.rs"]
mod m_private_cold_scorecard;
#[path = "_copper_ports.rs"]
mod m_private_copper_ports;
#[path = "_fittings.rs"]
mod m_private_fittings;
#[path = "_foam_cap.rs"]
mod m_private_foam_cap;
#[path = "_foam_shell.rs"]
mod m_private_foam_shell;
#[path = "_internal_routes.rs"]
mod m_private_internal_routes;
#[path = "_outer_shell.rs"]
mod m_private_outer_shell;
#[path = "_port_cuts.rs"]
mod m_private_port_cuts;
#[path = "_reed_b_outlet.rs"]
mod m_private_reed_b_outlet;
#[path = "_reed_channels.rs"]
mod m_private_reed_channels;
#[path = "_reservoir_a_anchors.rs"]
mod m_private_reservoir_a_anchors;
#[path = "_reservoir_a_c2.rs"]
mod m_private_reservoir_a_c2;
#[path = "_reservoir_b_fill.rs"]
mod m_private_reservoir_b_fill;
#[path = "_reservoir_pocket_walls.rs"]
mod m_private_reservoir_pocket_walls;
#[path = "_reservoir_ports.rs"]
mod m_private_reservoir_ports;
#[path = "_show_skin.rs"]
mod m_private_show_skin;
#[path = "_support_ring.rs"]
mod m_private_support_ring;
#[path = "_water_inlet_jet.rs"]
mod m_private_water_inlet_jet;
#[path = "prv_shroud.rs"]
mod m_prv_shroud;
#[path = "reed_bridge.rs"]
mod m_reed_bridge;
#[path = "reservoir.rs"]
mod m_reservoir;
#[path = "reservoir_float_rod_drawing.rs"]
mod m_reservoir_float_rod_drawing;
#[path = "water_inlet_jet_cap_drawing.rs"]
mod m_water_inlet_jet_cap_drawing;
#[path = "water_inlet_jet_elbow_drawing.rs"]
mod m_water_inlet_jet_elbow_drawing;
pub fn source(name: &str) -> Option<&'static str> {
    match name {
        "coil_mandrel" => Some("hardware/printed-parts/cold-core/coil-mandrel/coil_mandrel.py"),
        "_carbonator" => Some("hardware/cold-core-layout/_carbonator.py"),
        "_cold_scorecard" => Some("hardware/cold-core-layout/_cold_scorecard.py"),
        "_fittings" => Some("hardware/cold-core-layout/_fittings.py"),
        "_water_inlet_jet" => Some("hardware/cold-core-layout/_water_inlet_jet.py"),
        "carbonator_vessel_drawing" => {
            Some("hardware/cold-core-layout/carbonator_vessel_drawing.py")
        }
        "evaporator_coil_drawing" => Some("hardware/cold-core-layout/evaporator_coil_drawing.py"),
        "water_inlet_jet_cap_drawing" => {
            Some("hardware/cold-core-layout/water_inlet_jet_cap_drawing.py")
        }
        "water_inlet_jet_elbow_drawing" => {
            Some("hardware/cold-core-layout/water_inlet_jet_elbow_drawing.py")
        }
        "carbonator_tube_step" => {
            Some("hardware/cut-parts/carbonation/carbonator-tube/carbonator_tube_step.py")
        }
        "endcap_circular_drawing" => {
            Some("hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_drawing.py")
        }
        "endcap_circular_dxf" => {
            Some("hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.py")
        }
        "float_rod_drawing" => {
            Some("hardware/cut-parts/carbonation/float-rod/float_rod_drawing.py")
        }
        "reservoir_float_rod_drawing" => Some(
            "hardware/cut-parts/carbonation/reservoir-float-rod/reservoir_float_rod_drawing.py",
        ),
        "_above_core_mounts" => Some("hardware/printed-parts/cold-core/_above_core_mounts.py"),
        "_cold_core_interface" => Some("hardware/printed-parts/cold-core/_cold_core_interface.py"),
        "_copper_ports" => Some("hardware/printed-parts/cold-core/_copper_ports.py"),
        "_foam_cap" => Some("hardware/printed-parts/cold-core/_foam_cap.py"),
        "_foam_shell" => Some("hardware/printed-parts/cold-core/_foam_shell.py"),
        "_internal_routes" => Some("hardware/printed-parts/cold-core/_internal_routes.py"),
        "_outer_shell" => Some("hardware/printed-parts/cold-core/_outer_shell.py"),
        "_port_cuts" => Some("hardware/printed-parts/cold-core/_port_cuts.py"),
        "_reed_b_outlet" => Some("hardware/printed-parts/cold-core/_reed_b_outlet.py"),
        "_reed_channels" => Some("hardware/printed-parts/cold-core/_reed_channels.py"),
        "_reservoir_a_anchors" => Some("hardware/printed-parts/cold-core/_reservoir_a_anchors.py"),
        "_reservoir_a_c2" => Some("hardware/printed-parts/cold-core/_reservoir_a_c2.py"),
        "_reservoir_b_fill" => Some("hardware/printed-parts/cold-core/_reservoir_b_fill.py"),
        "_reservoir_pocket_walls" => {
            Some("hardware/printed-parts/cold-core/_reservoir_pocket_walls.py")
        }
        "_reservoir_ports" => Some("hardware/printed-parts/cold-core/_reservoir_ports.py"),
        "_show_skin" => Some("hardware/printed-parts/cold-core/_show_skin.py"),
        "_support_ring" => Some("hardware/printed-parts/cold-core/_support_ring.py"),
        "integration" => {
            Some("hardware/printed-parts/cold-core/magnetic-float/all-aero/integration.py")
        }
        "magnetic_float" => {
            Some("hardware/printed-parts/cold-core/magnetic-float/magnetic_float.py")
        }
        "prv_shroud" => Some("hardware/printed-parts/cold-core/prv-shroud/prv_shroud.py"),
        "reed_bridge" => Some("hardware/printed-parts/cold-core/reed-bridge/reed_bridge.py"),
        "reservoir" => Some("hardware/printed-parts/cold-core/reservoir/reservoir.py"),
        _ => None,
    }
}
pub fn by_path(path: &str) -> Option<&'static str> {
    if path.ends_with("hardware/printed-parts/cold-core/coil-mandrel/coil_mandrel.py") {
        return Some("coil_mandrel");
    }
    if path.ends_with("hardware/cold-core-layout/_carbonator.py") {
        return Some("_carbonator");
    }
    if path.ends_with("hardware/cold-core-layout/_cold_scorecard.py") {
        return Some("_cold_scorecard");
    }
    if path.ends_with("hardware/cold-core-layout/_fittings.py") {
        return Some("_fittings");
    }
    if path.ends_with("hardware/cold-core-layout/_water_inlet_jet.py") {
        return Some("_water_inlet_jet");
    }
    if path.ends_with("hardware/cold-core-layout/carbonator_vessel_drawing.py") {
        return Some("carbonator_vessel_drawing");
    }
    if path.ends_with("hardware/cold-core-layout/evaporator_coil_drawing.py") {
        return Some("evaporator_coil_drawing");
    }
    if path.ends_with("hardware/cold-core-layout/water_inlet_jet_cap_drawing.py") {
        return Some("water_inlet_jet_cap_drawing");
    }
    if path.ends_with("hardware/cold-core-layout/water_inlet_jet_elbow_drawing.py") {
        return Some("water_inlet_jet_elbow_drawing");
    }
    if path.ends_with("hardware/cut-parts/carbonation/carbonator-tube/carbonator_tube_step.py") {
        return Some("carbonator_tube_step");
    }
    if path.ends_with("hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_drawing.py")
    {
        return Some("endcap_circular_drawing");
    }
    if path.ends_with("hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.py") {
        return Some("endcap_circular_dxf");
    }
    if path.ends_with("hardware/cut-parts/carbonation/float-rod/float_rod_drawing.py") {
        return Some("float_rod_drawing");
    }
    if path.ends_with(
        "hardware/cut-parts/carbonation/reservoir-float-rod/reservoir_float_rod_drawing.py",
    ) {
        return Some("reservoir_float_rod_drawing");
    }
    if path.ends_with("hardware/printed-parts/cold-core/_above_core_mounts.py") {
        return Some("_above_core_mounts");
    }
    if path.ends_with("hardware/printed-parts/cold-core/_cold_core_interface.py") {
        return Some("_cold_core_interface");
    }
    if path.ends_with("hardware/printed-parts/cold-core/_copper_ports.py") {
        return Some("_copper_ports");
    }
    if path.ends_with("hardware/printed-parts/cold-core/_foam_cap.py") {
        return Some("_foam_cap");
    }
    if path.ends_with("hardware/printed-parts/cold-core/_foam_shell.py") {
        return Some("_foam_shell");
    }
    if path.ends_with("hardware/printed-parts/cold-core/_internal_routes.py") {
        return Some("_internal_routes");
    }
    if path.ends_with("hardware/printed-parts/cold-core/_outer_shell.py") {
        return Some("_outer_shell");
    }
    if path.ends_with("hardware/printed-parts/cold-core/_port_cuts.py") {
        return Some("_port_cuts");
    }
    if path.ends_with("hardware/printed-parts/cold-core/_reed_b_outlet.py") {
        return Some("_reed_b_outlet");
    }
    if path.ends_with("hardware/printed-parts/cold-core/_reed_channels.py") {
        return Some("_reed_channels");
    }
    if path.ends_with("hardware/printed-parts/cold-core/_reservoir_a_anchors.py") {
        return Some("_reservoir_a_anchors");
    }
    if path.ends_with("hardware/printed-parts/cold-core/_reservoir_a_c2.py") {
        return Some("_reservoir_a_c2");
    }
    if path.ends_with("hardware/printed-parts/cold-core/_reservoir_b_fill.py") {
        return Some("_reservoir_b_fill");
    }
    if path.ends_with("hardware/printed-parts/cold-core/_reservoir_pocket_walls.py") {
        return Some("_reservoir_pocket_walls");
    }
    if path.ends_with("hardware/printed-parts/cold-core/_reservoir_ports.py") {
        return Some("_reservoir_ports");
    }
    if path.ends_with("hardware/printed-parts/cold-core/_show_skin.py") {
        return Some("_show_skin");
    }
    if path.ends_with("hardware/printed-parts/cold-core/_support_ring.py") {
        return Some("_support_ring");
    }
    if path.ends_with("hardware/printed-parts/cold-core/magnetic-float/all-aero/integration.py") {
        return Some("integration");
    }
    if path.ends_with("hardware/printed-parts/cold-core/magnetic-float/magnetic_float.py") {
        return Some("magnetic_float");
    }
    if path.ends_with("hardware/printed-parts/cold-core/prv-shroud/prv_shroud.py") {
        return Some("prv_shroud");
    }
    if path.ends_with("hardware/printed-parts/cold-core/reed-bridge/reed_bridge.py") {
        return Some("reed_bridge");
    }
    if path.ends_with("hardware/printed-parts/cold-core/reservoir/reservoir.py") {
        return Some("reservoir");
    }
    None
}
pub fn initialize(rt: Runtime, e: Env, name: &str) -> Result<()> {
    match name {
        "coil_mandrel" => m_coil_mandrel::initialize(rt, e),
        "_carbonator" => m_private_carbonator::initialize(rt, e),
        "_cold_scorecard" => m_private_cold_scorecard::initialize(rt, e),
        "_fittings" => m_private_fittings::initialize(rt, e),
        "_water_inlet_jet" => m_private_water_inlet_jet::initialize(rt, e),
        "carbonator_vessel_drawing" => m_carbonator_vessel_drawing::initialize(rt, e),
        "evaporator_coil_drawing" => m_evaporator_coil_drawing::initialize(rt, e),
        "water_inlet_jet_cap_drawing" => m_water_inlet_jet_cap_drawing::initialize(rt, e),
        "water_inlet_jet_elbow_drawing" => m_water_inlet_jet_elbow_drawing::initialize(rt, e),
        "carbonator_tube_step" => m_carbonator_tube_step::initialize(rt, e),
        "endcap_circular_drawing" => m_endcap_circular_drawing::initialize(rt, e),
        "endcap_circular_dxf" => m_endcap_circular_dxf::initialize(rt, e),
        "float_rod_drawing" => m_float_rod_drawing::initialize(rt, e),
        "reservoir_float_rod_drawing" => m_reservoir_float_rod_drawing::initialize(rt, e),
        "_above_core_mounts" => m_private_above_core_mounts::initialize(rt, e),
        "_cold_core_interface" => m_private_cold_core_interface::initialize(rt, e),
        "_copper_ports" => m_private_copper_ports::initialize(rt, e),
        "_foam_cap" => m_private_foam_cap::initialize(rt, e),
        "_foam_shell" => m_private_foam_shell::initialize(rt, e),
        "_internal_routes" => m_private_internal_routes::initialize(rt, e),
        "_outer_shell" => m_private_outer_shell::initialize(rt, e),
        "_port_cuts" => m_private_port_cuts::initialize(rt, e),
        "_reed_b_outlet" => m_private_reed_b_outlet::initialize(rt, e),
        "_reed_channels" => m_private_reed_channels::initialize(rt, e),
        "_reservoir_a_anchors" => m_private_reservoir_a_anchors::initialize(rt, e),
        "_reservoir_a_c2" => m_private_reservoir_a_c2::initialize(rt, e),
        "_reservoir_b_fill" => m_private_reservoir_b_fill::initialize(rt, e),
        "_reservoir_pocket_walls" => m_private_reservoir_pocket_walls::initialize(rt, e),
        "_reservoir_ports" => m_private_reservoir_ports::initialize(rt, e),
        "_show_skin" => m_private_show_skin::initialize(rt, e),
        "_support_ring" => m_private_support_ring::initialize(rt, e),
        "integration" => m_integration::initialize(rt, e),
        "magnetic_float" => m_magnetic_float::initialize(rt, e),
        "prv_shroud" => m_prv_shroud::initialize(rt, e),
        "reed_bridge" => m_reed_bridge::initialize(rt, e),
        "reservoir" => m_reservoir::initialize(rt, e),
        _ => bail!("unknown cold-core module {name}"),
    }
}
pub fn entrypoint(rt: Runtime, e: Env, name: &str) -> Result<()> {
    match name {
        "coil_mandrel" => m_coil_mandrel::entrypoint(rt, e).map(|_| ()),
        "_carbonator" => m_private_carbonator::entrypoint(rt, e).map(|_| ()),
        "_cold_scorecard" => m_private_cold_scorecard::entrypoint(rt, e).map(|_| ()),
        "_fittings" => m_private_fittings::entrypoint(rt, e).map(|_| ()),
        "_water_inlet_jet" => m_private_water_inlet_jet::entrypoint(rt, e).map(|_| ()),
        "carbonator_vessel_drawing" => m_carbonator_vessel_drawing::entrypoint(rt, e).map(|_| ()),
        "evaporator_coil_drawing" => m_evaporator_coil_drawing::entrypoint(rt, e).map(|_| ()),
        "water_inlet_jet_cap_drawing" => {
            m_water_inlet_jet_cap_drawing::entrypoint(rt, e).map(|_| ())
        }
        "water_inlet_jet_elbow_drawing" => {
            m_water_inlet_jet_elbow_drawing::entrypoint(rt, e).map(|_| ())
        }
        "carbonator_tube_step" => m_carbonator_tube_step::entrypoint(rt, e).map(|_| ()),
        "endcap_circular_drawing" => m_endcap_circular_drawing::entrypoint(rt, e).map(|_| ()),
        "endcap_circular_dxf" => m_endcap_circular_dxf::entrypoint(rt, e).map(|_| ()),
        "float_rod_drawing" => m_float_rod_drawing::entrypoint(rt, e).map(|_| ()),
        "reservoir_float_rod_drawing" => {
            m_reservoir_float_rod_drawing::entrypoint(rt, e).map(|_| ())
        }
        "_above_core_mounts" => m_private_above_core_mounts::entrypoint(rt, e).map(|_| ()),
        "_cold_core_interface" => m_private_cold_core_interface::entrypoint(rt, e).map(|_| ()),
        "_copper_ports" => m_private_copper_ports::entrypoint(rt, e).map(|_| ()),
        "_foam_cap" => m_private_foam_cap::entrypoint(rt, e).map(|_| ()),
        "_foam_shell" => m_private_foam_shell::entrypoint(rt, e).map(|_| ()),
        "_internal_routes" => m_private_internal_routes::entrypoint(rt, e).map(|_| ()),
        "_outer_shell" => m_private_outer_shell::entrypoint(rt, e).map(|_| ()),
        "_port_cuts" => m_private_port_cuts::entrypoint(rt, e).map(|_| ()),
        "_reed_b_outlet" => m_private_reed_b_outlet::entrypoint(rt, e).map(|_| ()),
        "_reed_channels" => m_private_reed_channels::entrypoint(rt, e).map(|_| ()),
        "_reservoir_a_anchors" => m_private_reservoir_a_anchors::entrypoint(rt, e).map(|_| ()),
        "_reservoir_a_c2" => m_private_reservoir_a_c2::entrypoint(rt, e).map(|_| ()),
        "_reservoir_b_fill" => m_private_reservoir_b_fill::entrypoint(rt, e).map(|_| ()),
        "_reservoir_pocket_walls" => {
            m_private_reservoir_pocket_walls::entrypoint(rt, e).map(|_| ())
        }
        "_reservoir_ports" => m_private_reservoir_ports::entrypoint(rt, e).map(|_| ()),
        "_show_skin" => m_private_show_skin::entrypoint(rt, e).map(|_| ()),
        "_support_ring" => m_private_support_ring::entrypoint(rt, e).map(|_| ()),
        "integration" => m_integration::entrypoint(rt, e).map(|_| ()),
        "magnetic_float" => m_magnetic_float::entrypoint(rt, e).map(|_| ()),
        "prv_shroud" => m_prv_shroud::entrypoint(rt, e).map(|_| ()),
        "reed_bridge" => m_reed_bridge::entrypoint(rt, e).map(|_| ()),
        "reservoir" => m_reservoir::entrypoint(rt, e).map(|_| ()),
        _ => bail!("unknown cold-core module {name}"),
    }
}

pub fn documentation(name: &str) -> Option<&'static str> {
    match name {
        "_carbonator" => Some(
            "The carbonator, in the foam shell's own frame.\n\nA 5\" OD × 0.065\" wall 316 tube with a 1/4\"-thick circular plate recessed into each end and\nfillet-welded there, the 1/8\" 316L float rod welded between the plates' blind registers, a\nTAISHER street elbow made up on each of the top plate's two tapped 1/4\" NPT ports, and a neoFit\nAME4-N2-E push-fit male elbow on each of the bottom plate's two.\n\n  Z         the shell's own. The tube's bottom sits one floor slab and one support ring up\n            (`carbonator_bottom_z`); every figure below is struck off that.\n  ±Y        the port axis. All four ports stand `carbonator_port_offset` off the carbonator's axis\n            on it, two under the carbonator and two over it.\n  −Y        the register azimuth — the rod, and the reed bridge on the outside of the wall.\n\nEach plate is set one plate thickness in from its tube end, and that recess is where the\nclosure fillet is laid (`assembly/pressure-vessel.md`). So the interior runs\n`interior_floor_z` to `interior_ceiling_z` in the tube's own frame and the carbonator's outside is\nthe tube, end to end.\n\nTHE ELBOWS ARE PLACED BY THE STOREYS, NOT BY THEIR OWN REACH. `front_face_port_z` and\n`top_band_z` are where the shell's lines cross those bands, and an elbow's corner is what has\nto arrive there. `BOTTOM_AXIS_OFFSET` and `ELBOW_AXIS_OFFSET` are those standoffs struck off\nthe shell, and `report` holds each against the same distance read off its catalog part.\n",
        ),
        "_cold_scorecard" => Some(
            "The cold core's arrangement as a scorecard, written beside its STEP.\n\nSame sidecar the enclosure's card writes ([`web/contracts/scorecard-sidecar.js`]\n(/web/contracts/scorecard-sidecar.js)), so the 3D viewer draws this card with the machinery it\nalready has. The checks are this assembly's own — a carbonator, a wound coil, two reservoirs, and\nthe lines potted among them.\n\nREPORTING, NOT GATING. `main` never exits nonzero on a finding — every row lands in the card\nand on the terminal, and the build still writes its STEP. A reading that stops the build is a\nreading nobody sees at `/3d`.\n\n  bom-covered    every billed cold-core part against the body that realizes it\n  bodies-clear   no two solids share volume\n  routes-fit     no line meets a solid\n  lines-apart    no line meets another line\n  arcs-hold      every corner turns at the stock arc\n  floats-couple  every Aero float clears its wall and rides within the reed distance limit\n",
        ),
        "_fittings" => Some(
            "The purchased hardware inside the cold core, as solids.\n\nEvery body here is a PARAMETRIC STAND-IN built to its catalog envelope. What each one owes the\narrangement is where its mouths are and how much room it takes; what it does not owe is a\nthread form or a casting radius. Each is built from the two or three figures the layout reads\noff it — the mating dimension, the reach, the envelope — and each of those figures carries its\nsource in its own comment.\n\nWHAT A FITTING IS FOR, in this file: the mouth. Each builder hands back the point and axis a\nline lands on, and the assembly routes to that. A fitting that moves carries its line with it.\n",
        ),
        "_water_inlet_jet" => Some(
            "Candidate inlet-jet dimensions, shared by the nominal model and fabrication procedure.\n\nThese are fabrication targets for the purchased 316 rod. They do not establish the\nelbow's measured bore, available weld land, installed projection or qualified joint.\n",
        ),
        "carbonator_vessel_drawing" => Some(
            "Carbonator closure assembly: source-defined sections and an exterior end view.\n\nFabrication state of HSM-0004, before permanent fittings. Registers show their\nactual drill points; the rod has its fixed finished length and the cap spacing\nis controlled to its specified interface tolerance. Weld profiles are\ndiagrammatic because a qualified weld size is not established by the procedure.\n",
        ),
        "evaporator_coil_drawing" => Some(
            "EVAP-01: production coil, complete tube outlines and tangent tail forms.\n\nThe installed coil and both tails share _coil's geometry. Views project the\nqualified kernel's fine tube meshes with hidden edges clipped in model space.\nThe local bridge relief is defined separately by a radial section and its dimensions.\nSheet two defines all circular bends and their tangent stations. Dimensions\nand tolerances define the manufactured article rather than a prototype state.\n",
        ),
        "water_inlet_jet_cap_drawing" => Some(
            "Finished drilled water-inlet jet cap, on one ANSI A landscape sheet.\n\nThe nominal disc and through passage come from _water_inlet_jet, the same\nparameters used by the installed model. This drawing owns finished-component\ntolerances, centering, face condition and burr limits. The cap-to-elbow joint,\ninstalled port fit and post-weld acceptance belong to assembly/water-inlet-jet.md.\n\nRun with tools/cad-venv/bin/python. No CAD geometry or welding settings change.\n",
        ),
        "water_inlet_jet_elbow_drawing" => Some(
            "Water-inlet jet elbow assembly: purchased fitting plus welded drilled cap.\n\nThe exterior envelope and local tip section use the same parametric reference\nfitting as the cold core. It is a layout stand-in, not measured vendor detail. The drawing\nidentifies the purchased item and controls assembly alignment and acceptance;\ncap dimensions belong to JET-CAP-01. Grey bands show the required fusion path,\nnot a predicted or dimensioned weld profile. Measured fit and weld qualification\nremain explicit release items under assembly/water-inlet-jet.md.\n\nRun with tools/cad-venv/bin/python. No machine geometry or weld recipe changes.\n",
        ),
        "carbonator_tube_step" => Some(
            "\nCarbonator tube — the 3D solid of the cut stock, for the welding fixture and for quotes.\n\nThe pressure vessel's barrel: 5\" OD × 0.065\" wall 316 stainless, cut square to\nlength. This is purchased tube (OnlineMetals #12498) cut to size and deburred,\nnot a fabricated part — there is no cut file and no drawing, because a saw and a\nlength are the whole of it. The solid exists so the tube is a model the viewer\ncan open on its own, the same as the end caps that close it.\n\nEvery dimension is read off `_carbonator_stock`, which the assembly also reads.\nNothing here is a second copy of a number.\n\nThe tube stands on the origin, ends square, as it lies on the saw — not at the\nz it occupies inside the shell. Its assembly placement is the cold core's to\nstate.\n\nUnits: millimetres.\n",
        ),
        "endcap_circular_drawing" => Some(
            "Finished carbonator end cap, on one ANSI B landscape engineering sheet.\n\nThe face view and location table describe the two tapped ports and the blind\nrod register. Section A-A identifies the plate faces and NPT entry direction;\nlocal section B-B shows the actual 135-degree drill point and tip-depth datum.\nAll part dimensions come from the laser-blank/register source module. Thread\nlines are a conventional representation, not a model of the helical surfaces.\n\nRun with tools/cad-venv/bin/python. No CAD or cut-file geometry is changed.\n",
        ),
        "endcap_circular_dxf" => Some(
            "\nCarbonator end-cap disc — circular carbonator, 2 ports per cap.\n\nTwo identical discs per carbonator, each with 2x tap-drill holes for 1/4\"-18 NPT.\n4 ports/carbonator split 2+2 across both caps.\n\n── Dimensions ──\n\n  Disc diameter:          (= tube ID 4.870\" − 0.010\" slip-fit)\n  Disc thickness:         (1/4\" 316 SS, laser-cut)\n  Hole diameter:          (7/16\" — tap drill for 1/4\"-18 NPT)\n  Hole spacing:           (center-to-center along one axis)\n  Hole positions:      (-, 0) and (+, 0)\n\n── Rod register (in-house DRILLED secondary op — deliberately NOT in the cut) ──\n\n  The level-sensing float rod (1/8\" 316L) is welded to the bottom plate and\n  its top end seats in a shallow blind register in the top plate's inside\n  face. That register is a BLIND hole — it must not pierce the plate, because\n  the plate is the 90 PSI pressure boundary (hydro 180 PSI). A laser DXF cuts\n  THROUGH, so the register cannot live in this cut file without breaching the\n  carbonator. It is drilled in-house on the WEN 4208T after the discs arrive; the\n  laser geometry below is unchanged, so existing discs need no re-cut.\n\n  Both discs are drilled identically (kept interchangeable): top plate captures\n  the rod tip, bottom plate seats/locates the rod base for its tack weld.\n\n  Register center:     (−, 0) on the −X axis, beyond P1.\n                       Radius = tube-ID radius \n                       minus, the shared Aero float guide datum.\n                       A 36 mm float has 2 mm nominal clearance from the wet wall;\n                       its 4.8 mm bore allows 0.8125 mm radial motion on the 1/8\" rod.\n                       The external reed lies on this same azimuth. Exact metric\n                       radius is 41.849 mm. Liquid switching height needs calibration.\n  Register drill:      9/64\"  — slip-fit on the 1/8\" rod; snug, which\n                       self-locates the rod base in the bottom plate for its tack\n                       weld. Open the TOP plate's pocket to 5/32\" (0.156\") only if\n                       the cap fights to seat over the rod tip at closure (step 5).\n  Register depth:       blind, to the drill-point tip, from the inside face\n                       — leaves of the plate as intact pressure\n                       boundary. 135° split-point bit ⇒ ~0.07\" of full-diameter\n                       pocket gripping the rod tip: ample, non-load-bearing capture.\n\n── Material ──\n\n  316 stainless steel, thick, laser-cut.\n\nUnits: inches.  DXF $INSUNITS = 1 (inches).\n",
        ),
        "float_rod_drawing" => Some(
            "Finished carbonator guide rod: fixed cut length, tolerances and end finish.\n\nThe controlled cap spacing and conical-register tolerance basis are stated on\nthe sheet. All rod dimensions and fit assumptions come from float_rod_dimensions.\n",
        ),
        "reservoir_float_rod_drawing" => Some(
            "Finished reservoir guide rod; common part for channels A and B.\n\nNominal dimensions are imported from the reservoir's seats. The limits below\nare chosen finished-part requirements, not measured stock/print capability.\n",
        ),
        "_above_core_mounts" => Some(
            "Cold-core equipment mounts carried by the production above-core datums.\n\nCoordinates returned here belong to the top cap and lid before their installed\nhalf turn. Component mounting holes come from their native references; the\nappliance placement belongs to ``manifold-layout/above_core.py``.\n",
        ),
        "_cold_core_interface" => Some(
            "Shared cold-core datums and construction interfaces.\n\nRust owns the casing stock, cavity envelope, clamp stack and port-lane\ndimensions. The remaining cap mount and passage recipes expose their\nsource-frame values to the sibling parts.\n\nThe constants carry claims about each other — a screw long enough for its insert, a band wide\nenough for its bore, two columns far enough apart for foam to reach between them — and those are\nsettled here, as this file is read, with no solid yet to measure. `_stated_bounds` is the ledger\nthey record into; `enclosure_assembly.carry_stated_bounds` drains it onto the machine's card, where\nan open one is a red row a reader can see beside the geometry it describes. The siblings that\nimport this module take `bound` and `state` from here rather than reaching for the ledger\nthemselves, because this is already the path they read every other shared name off.",
        ),
        "_copper_ports" => Some("Evaporator copper feed-throughs in the shell's native frame."),
        "_foam_cap" => Some(
            "Uniform equipment lid and open-topped bottom closure for the cold core.\n\nThe lid's underside is its bed face. The bottom closure prints on its outside\nfloor and carries its M5 head pads inside. Exterior foil closes the dry seams.\n",
        ),
        "_foam_shell" => Some(
            "Top-level foam-shell assembly: union the wall builders, then cut\nall the port holes and channel openings.",
        ),
        "_internal_routes" => Some(
            "The lines INSIDE the cold core, drawn.\n\nSeven fluid conduits, four cable passages and two reservoir air bores stand on\nthe top cap. This module draws each fluid run from its fitting\nto the mouth it leaves by, as a swept ⌀ solid on the tube's own\ncentreline. The shell is a set of voids and a line is a void's occupant, so nothing\nabout a route shows up in a bounding box and nothing about it collides with anything:\nthe only way to know a line fits is to draw it and measure it, which is what\n`report_routes` does at every foam-assembly build.\n\nWHERE EACH LINE GOES, and what it does at the end of it:\n\n  water-in         from the aft plain guide through the cup, east of the sensor loom\n                   and clear of the equipment columns, to the fixed TOP-plate elbow.\n                   Filtered tap water enters above the liquid against CO2 back-pressure.\n  carb-water-out   the carbonator's BOTTOM plate, under the liquid: the carbonator's own\n                   drain. Out flat on its own storey and through a slot in the support\n                   ring, up beside the coil, and onto the port lane only once the carbonator's\n                   top plate is under it, then across the cap to the upper soda guide.\n  co2-in           down the port lane, a shallow shift onto the lower column,\n                   and straight in along the leaning reach that crosses the support ring at a slot — then the plain\n                   bottom gas opening. Gas bubbles through the water to the headspace;\n                   the top water-inlet jet mixes during refill.\n  reservoir-a      each reservoir's dip tube: the draw line itself, straight down from its\n  reservoir-b      conduit through the bore in that reservoir's own cap to the floor, its\n                   mouth the lowest point a line reaches in the cavity.\n  reservoir-a-fill through its aligned guide into the reservoir's headspace.\n  reservoir-b-fill from the cap's Y− side entry, through the independent R14 holder\n                   and vertically into the original reservoir fill seat.\n\nThe carbonator and both reservoirs are filled high and drawn low. Nothing that enters\none can leave without crossing it, which is what the air-purge and clean-flush service modes run on.\n\nTHE BANDS ARE STACKED IN Z, not in Y — AND A RISER IS ON NO BAND. A lane is one bore\nwide, so two runs that want it at the same height cannot pass: what separates them is the\nstorey each takes. On the port lane, the CO2 has the lane's own floor where it turns in to\nthe carbonator; the evaporator's inlet copper takes a storey above it; the carbonated water\ndoes not join the lane until it is over the carbonator. On the west lane, the PRV vent and the\nevaporator's outlet copper take two storeys and water-in runs high over the carbonator.\nA RISER answers to none of that — it stands in every storey at once, so what keeps it\nclear is its X, and one bore of lane holds exactly one riser. EACH LANE CARRIES ONE. The\nCO2's fall is the port lane's (`_cold_core_interface.co2_cap_x`), and the evaporator's\noutlet copper is the west lane’s. The short PRV vent falls from its shroud and\nleaves through the +Y flank. `report_routes` reads the clearance of every run.\n\nWHAT A CORNER TURNS AT IS NOT CHOSEN HERE — it is what the corridor leaves, and\n`fit_route` is how the corridor states it: each line is drawn at the stock arc and\nstepped down until it stops meeting anything. The reading that comes back is the\nmeasurement, and the whole reason to draw these at all.\n\nWHERE A LINE HAS TO REACH AND RISE AT ONCE, IT LEANS: one diagonal in place of two square\ncorners on a step's own width, which is what the carbonated water does under the carbonator to\ncross the CO2 and again at the top to put itself on its conduit's column.\n\nThe water inlet retains the carbonator elbow's clocking line. Its R14\nturn finishes below the cup floor. The soda tube turns above the carbonator\nwhile the body is open for potting. Both pass straight through the cap.\n",
        ),
        "_outer_shell" => Some(
            "Outer rectangular cup (floor + four perimeter walls) with a cylindrical boss at\nevery `attachment_stations` station and their heat-set insert pockets. Exterior\ncorners rounded; each corner boss seated in the corner with its ⌀ tangent to the\nexterior wall arc, two short webs filling to the flanking flat walls — the\ncylinder + corner-fill teardrop idiom of the reservoir pocket-corner supports.",
        ),
        "_port_cuts" => Some(
            "Openings through the foam shell — the PRV vent's port through the +Y flank and the front\nwall's two copper feed-throughs — and the two lines that cross the carbonator support ring.\n\nEVERY FLUID LINE LEAVES BY THE TOP, and no line crosses a bag pocket's wall: both reservoirs\nare filled and drawn through their own caps. The two lines that run under the carbonator —\nthe CO2 in and the carbonated water out — cross the support ring at its own slots, on the\ncolumns `co2_lane_x` and `water_outlet_climb_x`, and the assertions here are what hold each\ncrossing inside one slot.\n\nOnly the two copper feed-throughs open on the shell's −X FACE. The two reed cables take the\nreed channels' own cavities, open to the cap (`_reed_channels`), and they are the whole\nof what crosses that wall besides the copper: it is mated face to face with the refrigeration\nbase, and the copper meets that base's own entries.\n",
        ),
        "_reed_b_outlet" => Some("Reservoir B cable's fore side outlet below the shell rim."),
        "_reed_channels" => Some(
            "Reed-and-cable channel system for level sensing — built into the\nfoam shell on the outer face of each bag-pocket far ±X wall.",
        ),
        "_reservoir_a_anchors" => Some(
            "Reservoir A's fore snap receiver and aft tied seats, in appliance millimetres.\n\nThe fore integral C2 pair shares `_reservoir_a_c2`. The aft open seats\nshare one filled stepped-height saddle within the casing footprint. Its tie witnesses\ndescribe routing, not purchased dimensions or physical acceptance.\n",
        ),
        "_reservoir_a_c2" => Some(
            "Integral fore Reservoir A C2 pair, in appliance millimetres.\n\nThe broad filled base joins both seats to the lid. Its equator is the root\nof the two independent C2 spring pairs; the air above that plane stays open.\n",
        ),
        "_reservoir_b_fill" => Some(
            "B-fill tube passage and independent R14 bend holder, in appliance XYZ.\n\nThe R14 bend and 6.8 mm bore use the accepted holder's tube envelope.\nThe cap passage is circular, with 0.5 mm insertion lead-ins and a supported\nroof allowance toward print-up. The inlet extends to the front cap face;\nthe outlet turns directly into the reservoir seat.\n",
        ),
        "_reservoir_pocket_walls" => Some(
            "Two reservoir pockets, one on each ±X side, as four-walled\nenclosures whose centerward wall is curved to clear the carbonator+coil\nenvelope. The −X pocket mirrors the +X pocket across YZ.",
        ),
        "_reservoir_ports" => Some(
            "Matched flush TPU seats and independent reservoir air-tube datums, in mm.\n\nPort XY belongs to the cold-core shell frame. Each lid captures a spool through\nits flat plate; the casing cup and lid carry the air tube beyond the insulation.\n",
        ),
        "_show_skin" => Some("Smooth cold-core casing surfaces, shared by shell, cups and lids."),
        "_support_ring" => Some(
            "Annular ring sitting at the bottom of the foam-shell's central\nzone, holding the carbonator up by its outer rim. The ring's outer face sits\non the carbonator+coil envelope — inboard of the reservoir pockets' centerward\nwall, which stands off from it by the cylinder's foam blanket.",
        ),
        "integration" => Some(
            "Verify the shared float datums against emitted vessel CAD.\n\nUpright geometry is checked over the whole translation range with bore play.\nPhysical sliding, expansion, immersion and directional reed switching are not\naccepted by this check. Run after the float/reservoir/end-cap generators.\n",
        ),
        "magnetic_float" => Some(
            "RC62 magnetic float: PETG Translucent Clear envelope and fitted ASA Aero core.\n\nFrame: guide bore on Z, finished bottom at Z=0, roof at positive Z.\nThe separate Aero insert seats from Z=47 to the roof underside at Z=57.\n\nThis module holds the float's numbers and the figures derived from them, and writes the numbers\nthe geometry takes (`numbers()`) to `magnetic-float.numbers.json`; `magnetic_float.rs`, beside\nit, cuts each piece's STEP and payload, the printed pieces' STLs, and the assembly, section and\nexploded views from them on the kernel (`hardware/scripts/_rust_part.py`).\n",
        ),
        "prv_shroud" => Some(
            "PRV shroud — printed PETG cup that surrounds the Control Devices\nSV-125 pressure-relief valve during the cold-core body foam pour.\n\nThe SV-125 is an open-port pop-off valve: gas exits through a single\nradial discharge port on the smooth cylinder between the NPT threads\nand the hex, and the spring chamber above the hex is open to\natmosphere through bonnet windows above. Both features need to see\nair, not cured polyurethane foam, for the valve to function as a\nrelief device.\n\nThe shroud slips over the entire valve from the pull-ring end and\nseats on the smooth ⌀18.8 mm cylindrical section of the TAISHER 316L\nSS 90° street elbow (B0CZ38MYL1) that threads into Port 4. The\nopen shroud end-to-elbow joint is sealed with a bead of 100% RTV\nsilicone caulk, tooled to a fillet — foam-tight, not airtight.\n\nA ⌀ hole through the BARREL accepts a length of 1/4\" OD\nLLDPE tubing — the unpressurized vent line. The LLDPE runs down the\nfoam shell's WEST LANE and out its slot in the −X wall, one station\nbelow the evaporator outlet copper that shares it, into the appliance\ninterior, where it terminates open.\n\nThe hole is radial and not in the cap because THE CAP HAS NOWHERE TO\nSEND A TUBE. Installed, the shroud lies horizontally on the +Y port's\nlateral axis and its cap face stands ~3 mm off the foam shell's own\ninner wall — less than a tube's radius, so a line leaving axially has\nno room to turn. Leaving radially through the barrel's underside, the\nline is already pointing down the lane it has to fall, and needs no\ncorner at all. The hole's station along the barrel\n( from the open end) is what lands it on that\nlane's centreline once the shroud is made up on the elbow.\n\nGeometry\n--------\n\n    Z =  ┌──────────────────────┐  ← cap outside surface\n               │ ░░░░ cap ░░░░░░ │  ← closed, no hole\n    Z =  ├──────────────────────┤  ← cap inside surface\n               │                      │\n               │   (cavity around     │\n               │    PRV body, hex,    │  ← ID\n               │    upper smooth cyl, │     OD ( wall)\n               │    bonnet windows,   │\n               │    pull-ring)        │\n               │                      │\n    Z = 0      └ open ────────────────┘  ← seats on elbow ⌀18.8 mm cyl\n\n               ⌀ vent bored radially through the −Y wall at\n               Z =; the cup is rolled about its own axis at\n               install so that wall faces the shell's −Z, and the tube leaves\n               DOWNWARD onto the west lane (`cold_core_assembly._prv_roll`).\n\nThe cavity length spans from the bottom of the elbow's smooth\ncylinder to the tip of the PRV pull-ring with the valve hand-tight\nin the elbow's lateral F outlet.\n\nCoordinate convention: cylinder axis along Z, open end at Z=0, cap\ntop at Z=. Installed orientation is horizontal — the shroud's Z\naxis aligns with the lateral run of the TAISHER elbow off Port 4.\n",
        ),
        "reed_bridge" => Some(
            "Carbonator reed bridge — printed PETG interposer holding the two\nexternal level reeds against the carbonator wall on the register azimuth,\nstanding the evaporator coil off the glass where a wrap crosses it.\n\nThe RC62 is an axially-magnetised neodymium ring: radially outside it, on\nits mid-plane, the field is purely axial, so both reeds stand with their\nglass vertical. reed_glass_length of vertical glass spans one wrap or two\nat the wind's inter_wrap_clear.\n\nThe plateau stands pocket_depth off the steel; each reed lies in a pocket\ncut clear through to the wall, so its glass rests on bare 316L. Ramps on\nall four sides are what each wrap rides over as the coil is dragged down\nthe carbonator. Copper hoop tension clamps the bridge to the wall; the foam\npour sets it.\n\nThe setting gauge hangs on the tube's bottom rim and its top face is\nbridge_z_bottom.\n\nFrame: +Z is the carbonator axis, Z=0 at the tube's bottom rim — the face\nthat seats on the carbonator support ring. +X is the register azimuth, the line\nthe wall-preloaded donut rides. The part is symmetric about the XZ plane\napart from the lead groove.\n",
        ),
        "reservoir" => Some(
            "Reservoir — open-top `[`-shaped PETG cup that stands on the floor of each\nbag pocket of the foam shell, closed by a separately-printed cap clamped\nthrough a TPU gasket. Mirrored ±X. Carries the level-sensing rod, and its\ncap carries flush TPU tube grips and a separate bidirectional air tube.\n\nSame coordinate convention as ../foam-shell/: +Z vertical, +X is\nthe bag-pocket axis (two cavities sit on opposite sides), +Y is\nperpendicular to it.",
        ),
        "coil_mandrel" => Some(
            "\nCoil winding mandrel.\n\nHollow PETG cylinder for hand-winding 1/4\" OD copper around the 5\"\nround 316L carbonator. solid PETG wall, with a shallow\nhelical guide groove deep that cradles the copper.\n\nThe undersized groove is a rough-forming aid. Feed material from the long\nends while setting the finished diameter, pitch and turn count on the vessel\nfixture. EVAP-01 and cold-core-layout/_coil.py define the production coil,\nincluding its opposite tangent exits and complete R15 tail forms.\n\nThe Rust cold-core scalar recipe derives the winding dimensions and stub\nallowances. This interface supplies them to the part program and Python readers;\n`coil_mandrel.rs` cuts the STEP, payload and STL on the kernel.\n",
        ),
        _ => None,
    }
}
