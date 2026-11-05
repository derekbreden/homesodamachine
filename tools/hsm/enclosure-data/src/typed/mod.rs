//! The enclosure's interfaces, recipes, drawings and reports as typed Rust modules.
//!
//! Each module keeps the namespace its Python surface reads: the same names, holding the same
//! values, with its functions taking and returning Python values at that boundary.
pub mod num;
pub mod py;
pub mod rt;

pub mod _above_core_shell;
pub mod _anchor_cap_interface;
pub mod _back_top_meter;
pub mod _data_wing_interface;
pub mod _display_retention;
pub mod _display_wing_interface;
pub mod _disposal_artwork;
pub mod _enclosure_back_top;
pub mod _enclosure_datums;
pub mod _enclosure_dimensions;
pub mod _enclosure_front_bottom;
pub mod _enclosure_front_top;
pub mod _enclosure_interface;
pub mod _enclosure_panel;
pub mod _enclosure_presentation;
pub mod _enclosure_pump_retainer;
pub mod _enclosure_rust_driver;
pub mod _enclosure_skin;
pub mod _enclosure_structure;
pub mod _fixed_pump_mount;
pub mod _grip_interface;
pub mod _nameplate_dimensions;
pub mod _nameplate_interface;
pub mod _nameplate_wing_interface;
pub mod _route_snaps;
pub mod _rust_enclosure_checks;
pub mod _rust_enclosure_presentation;
pub mod _swept_top;
pub mod _tube_snap_sites;
pub mod _y_wall_dimensions;
pub mod bulkhead_ring;
pub mod data_ring;
pub mod display_cover;
pub mod display_gasket;
pub mod dock_structure;
pub mod enclosure;
pub mod fixed_returns;
pub mod nameplate;
pub mod pump_case;
pub mod pump_tray;
pub mod rear_equipment_caps;
pub mod rear_identification;
pub mod valve_tray;

use anyhow::{Result, bail};
use rt::{Ns, Rt};

/// Every module and the source path its namespace reports as `__file__`, in lookup order.
const MODULES: &[(&str, &str)] = &[
    ("_above_core_shell", "hardware/printed-parts/enclosure/enclosure/_above_core_shell.py"),
    ("_anchor_cap_interface", "hardware/printed-parts/enclosure/enclosure/_anchor_cap_interface.py"),
    ("_back_top_meter", "hardware/printed-parts/enclosure/enclosure/_back_top_meter.py"),
    ("_data_wing_interface", "hardware/printed-parts/enclosure/enclosure/_data_wing_interface.py"),
    ("_display_retention", "hardware/printed-parts/enclosure/enclosure/_display_retention.py"),
    ("_display_wing_interface", "hardware/printed-parts/enclosure/enclosure/_display_wing_interface.py"),
    ("_disposal_artwork", "hardware/printed-parts/enclosure/enclosure/_disposal_artwork.py"),
    ("_enclosure_back_top", "hardware/printed-parts/enclosure/enclosure/_enclosure_back_top.py"),
    ("_enclosure_datums", "hardware/printed-parts/enclosure/enclosure/_enclosure_datums.py"),
    ("_enclosure_dimensions", "hardware/printed-parts/enclosure/_enclosure_dimensions.py"),
    ("_enclosure_front_bottom", "hardware/printed-parts/enclosure/enclosure/_enclosure_front_bottom.py"),
    ("_enclosure_front_top", "hardware/printed-parts/enclosure/enclosure/_enclosure_front_top.py"),
    ("_enclosure_interface", "hardware/printed-parts/enclosure/enclosure/_enclosure_interface.py"),
    ("_enclosure_panel", "hardware/printed-parts/enclosure/enclosure/_enclosure_panel.py"),
    ("_enclosure_presentation", "hardware/printed-parts/enclosure/enclosure/_enclosure_presentation.py"),
    ("_enclosure_pump_retainer", "hardware/printed-parts/enclosure/enclosure/_enclosure_pump_retainer.py"),
    ("_enclosure_rust_driver", "hardware/printed-parts/enclosure/enclosure/_enclosure_rust_driver.py"),
    ("_enclosure_skin", "hardware/printed-parts/enclosure/enclosure/_enclosure_skin.py"),
    ("_enclosure_structure", "hardware/printed-parts/enclosure/enclosure/_enclosure_structure.py"),
    ("_fixed_pump_mount", "hardware/printed-parts/enclosure/enclosure/_fixed_pump_mount.py"),
    ("_grip_interface", "hardware/printed-parts/enclosure/enclosure/_grip_interface.py"),
    ("_nameplate_dimensions", "hardware/printed-parts/enclosure/nameplate/_nameplate_dimensions.py"),
    ("_nameplate_interface", "hardware/printed-parts/enclosure/enclosure/_nameplate_interface.py"),
    ("_nameplate_wing_interface", "hardware/printed-parts/enclosure/enclosure/_nameplate_wing_interface.py"),
    ("_route_snaps", "hardware/printed-parts/enclosure/enclosure/_route_snaps.py"),
    ("_rust_enclosure_checks", "hardware/printed-parts/enclosure/enclosure/_rust_enclosure_checks.py"),
    ("_rust_enclosure_presentation", "hardware/printed-parts/enclosure/enclosure/_rust_enclosure_presentation.py"),
    ("_swept_top", "hardware/printed-parts/enclosure/enclosure/_swept_top.py"),
    ("_tube_snap_sites", "hardware/printed-parts/enclosure/enclosure/_tube_snap_sites.py"),
    ("_y_wall_dimensions", "hardware/printed-parts/enclosure/y-wall-of-back-top/_y_wall_dimensions.py"),
    ("bulkhead_ring", "hardware/printed-parts/enclosure/bulkhead-ring/bulkhead_ring.py"),
    ("data_ring", "hardware/printed-parts/enclosure/data-ring/data_ring.py"),
    ("display_cover", "hardware/printed-parts/enclosure/display-cover/display_cover.py"),
    ("display_gasket", "hardware/printed-parts/enclosure/display-gasket/display_gasket.py"),
    ("dock_structure", "hardware/printed-parts/enclosure/pump-dock/dock_structure.py"),
    ("enclosure", "hardware/printed-parts/enclosure/enclosure/enclosure.py"),
    ("fixed_returns", "hardware/printed-parts/enclosure/pump-dock/fixed_returns.py"),
    ("nameplate", "hardware/printed-parts/enclosure/nameplate/nameplate.py"),
    ("pump_case", "hardware/printed-parts/enclosure/pump-tray/pump_case.py"),
    ("pump_tray", "hardware/printed-parts/enclosure/pump-tray/pump_tray.py"),
    ("rear_equipment_caps", "hardware/printed-parts/enclosure/rear-equipment-caps/rear_equipment_caps.py"),
    ("rear_identification", "hardware/printed-parts/enclosure/rear-identification/rear_identification.py"),
    ("valve_tray", "hardware/printed-parts/enclosure/valve-tray/valve_tray.py"),
];

/// Whether a module runs typed in the hybrid development build; the rest run their generated
/// namespaces.
#[cfg(feature = "hybrid")]
pub fn converted(name: &str) -> bool {
    match name {
        "_above_core_shell" => _above_core_shell::TYPED,
        "_anchor_cap_interface" => _anchor_cap_interface::TYPED,
        "_back_top_meter" => _back_top_meter::TYPED,
        "_data_wing_interface" => _data_wing_interface::TYPED,
        "_display_retention" => _display_retention::TYPED,
        "_display_wing_interface" => _display_wing_interface::TYPED,
        "_disposal_artwork" => _disposal_artwork::TYPED,
        "_enclosure_back_top" => _enclosure_back_top::TYPED,
        "_enclosure_datums" => _enclosure_datums::TYPED,
        "_enclosure_dimensions" => _enclosure_dimensions::TYPED,
        "_enclosure_front_bottom" => _enclosure_front_bottom::TYPED,
        "_enclosure_front_top" => _enclosure_front_top::TYPED,
        "_enclosure_interface" => _enclosure_interface::TYPED,
        "_enclosure_panel" => _enclosure_panel::TYPED,
        "_enclosure_presentation" => _enclosure_presentation::TYPED,
        "_enclosure_pump_retainer" => _enclosure_pump_retainer::TYPED,
        "_enclosure_rust_driver" => _enclosure_rust_driver::TYPED,
        "_enclosure_skin" => _enclosure_skin::TYPED,
        "_enclosure_structure" => _enclosure_structure::TYPED,
        "_fixed_pump_mount" => _fixed_pump_mount::TYPED,
        "_grip_interface" => _grip_interface::TYPED,
        "_nameplate_dimensions" => _nameplate_dimensions::TYPED,
        "_nameplate_interface" => _nameplate_interface::TYPED,
        "_nameplate_wing_interface" => _nameplate_wing_interface::TYPED,
        "_route_snaps" => _route_snaps::TYPED,
        "_rust_enclosure_checks" => _rust_enclosure_checks::TYPED,
        "_rust_enclosure_presentation" => _rust_enclosure_presentation::TYPED,
        "_swept_top" => _swept_top::TYPED,
        "_tube_snap_sites" => _tube_snap_sites::TYPED,
        "_y_wall_dimensions" => _y_wall_dimensions::TYPED,
        "bulkhead_ring" => bulkhead_ring::TYPED,
        "data_ring" => data_ring::TYPED,
        "display_cover" => display_cover::TYPED,
        "display_gasket" => display_gasket::TYPED,
        "dock_structure" => dock_structure::TYPED,
        "enclosure" => enclosure::TYPED,
        "fixed_returns" => fixed_returns::TYPED,
        "nameplate" => nameplate::TYPED,
        "pump_case" => pump_case::TYPED,
        "pump_tray" => pump_tray::TYPED,
        "rear_equipment_caps" => rear_equipment_caps::TYPED,
        "rear_identification" => rear_identification::TYPED,
        "valve_tray" => valve_tray::TYPED,
        _ => false,
    }
}

pub fn static_name(name: &str) -> Option<&'static str> {
    MODULES.iter().find(|(module, _)| *module == name).map(|(module, _)| *module)
}
pub fn source(name: &str) -> Option<&'static str> {
    MODULES.iter().find(|(module, _)| *module == name).map(|(_, path)| *path)
}
pub fn by_path(path: &str) -> Option<&'static str> {
    MODULES.iter().find(|(_, source)| path.ends_with(source)).map(|(module, _)| *module)
}

/// Run a module's top level into its namespace.
pub fn install(rt: &Rt, ns: &Ns, name: &'static str) -> Result<()> {
    match name {
        "_above_core_shell" => _above_core_shell::install(rt, ns),
        "_anchor_cap_interface" => _anchor_cap_interface::install(rt, ns),
        "_back_top_meter" => _back_top_meter::install(rt, ns),
        "_data_wing_interface" => _data_wing_interface::install(rt, ns),
        "_display_retention" => _display_retention::install(rt, ns),
        "_display_wing_interface" => _display_wing_interface::install(rt, ns),
        "_disposal_artwork" => _disposal_artwork::install(rt, ns),
        "_enclosure_back_top" => _enclosure_back_top::install(rt, ns),
        "_enclosure_datums" => _enclosure_datums::install(rt, ns),
        "_enclosure_dimensions" => _enclosure_dimensions::install(rt, ns),
        "_enclosure_front_bottom" => _enclosure_front_bottom::install(rt, ns),
        "_enclosure_front_top" => _enclosure_front_top::install(rt, ns),
        "_enclosure_interface" => _enclosure_interface::install(rt, ns),
        "_enclosure_panel" => _enclosure_panel::install(rt, ns),
        "_enclosure_presentation" => _enclosure_presentation::install(rt, ns),
        "_enclosure_pump_retainer" => _enclosure_pump_retainer::install(rt, ns),
        "_enclosure_rust_driver" => _enclosure_rust_driver::install(rt, ns),
        "_enclosure_skin" => _enclosure_skin::install(rt, ns),
        "_enclosure_structure" => _enclosure_structure::install(rt, ns),
        "_fixed_pump_mount" => _fixed_pump_mount::install(rt, ns),
        "_grip_interface" => _grip_interface::install(rt, ns),
        "_nameplate_dimensions" => _nameplate_dimensions::install(rt, ns),
        "_nameplate_interface" => _nameplate_interface::install(rt, ns),
        "_nameplate_wing_interface" => _nameplate_wing_interface::install(rt, ns),
        "_route_snaps" => _route_snaps::install(rt, ns),
        "_rust_enclosure_checks" => _rust_enclosure_checks::install(rt, ns),
        "_rust_enclosure_presentation" => _rust_enclosure_presentation::install(rt, ns),
        "_swept_top" => _swept_top::install(rt, ns),
        "_tube_snap_sites" => _tube_snap_sites::install(rt, ns),
        "_y_wall_dimensions" => _y_wall_dimensions::install(rt, ns),
        "bulkhead_ring" => bulkhead_ring::install(rt, ns),
        "data_ring" => data_ring::install(rt, ns),
        "display_cover" => display_cover::install(rt, ns),
        "display_gasket" => display_gasket::install(rt, ns),
        "dock_structure" => dock_structure::install(rt, ns),
        "enclosure" => enclosure::install(rt, ns),
        "fixed_returns" => fixed_returns::install(rt, ns),
        "nameplate" => nameplate::install(rt, ns),
        "pump_case" => pump_case::install(rt, ns),
        "pump_tray" => pump_tray::install(rt, ns),
        "rear_equipment_caps" => rear_equipment_caps::install(rt, ns),
        "rear_identification" => rear_identification::install(rt, ns),
        "valve_tray" => valve_tray::install(rt, ns),
        _ => bail!("unknown enclosure module {name}"),
    }
}

/// A module run as a script: its `if __name__ == "__main__"` block.
pub fn entrypoint(rt: &Rt, name: &'static str) -> Result<()> {
    #[cfg(feature = "hybrid")]
    if !converted(name) {
        return crate::compiled::entrypoint_generated(rt.root(), name);
    }
    let _frame = rt.frame(name);
    match name {
        "_enclosure_dimensions" => _enclosure_dimensions::main_block(rt),
        "_nameplate_dimensions" => _nameplate_dimensions::main_block(rt),
        "_y_wall_dimensions" => _y_wall_dimensions::main_block(rt),
        "data_ring" => data_ring::main_block(rt),
        "display_cover" => display_cover::main_block(rt),
        "display_gasket" => display_gasket::main_block(rt),
        "enclosure" => enclosure::main_block(rt),
        "nameplate" => nameplate::main_block(rt),
        "pump_case" => pump_case::main_block(rt),
        "pump_tray" => pump_tray::main_block(rt),
        "rear_equipment_caps" => rear_equipment_caps::main_block(rt),
        "rear_identification" => rear_identification::main_block(rt),
        "valve_tray" => valve_tray::main_block(rt),
        _ => Ok(()),
    }
}
