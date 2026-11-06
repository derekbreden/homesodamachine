use super::*;
#[path = "_above_core_shell.rs"]
mod _above_core_shell;
#[path = "_anchor_cap_interface.rs"]
mod _anchor_cap_interface;
#[path = "_back_top_meter.rs"]
mod _back_top_meter;
#[path = "_data_wing_interface.rs"]
mod _data_wing_interface;
#[path = "_display_retention.rs"]
mod _display_retention;
#[path = "_display_wing_interface.rs"]
mod _display_wing_interface;
#[path = "_disposal_artwork.rs"]
mod _disposal_artwork;
#[path = "_enclosure_datums.rs"]
mod _enclosure_datums;
#[path = "_enclosure_dimensions.rs"]
mod _enclosure_dimensions;
#[path = "_enclosure_interface.rs"]
mod _enclosure_interface;
#[path = "_enclosure_panel.rs"]
mod _enclosure_panel;
#[path = "_enclosure_rust_driver.rs"]
mod _enclosure_rust_driver;
#[path = "_enclosure_structure.rs"]
mod _enclosure_structure;
#[path = "_fixed_pump_mount.rs"]
mod _fixed_pump_mount;
#[path = "_grip_interface.rs"]
mod _grip_interface;
#[path = "_nameplate_dimensions.rs"]
mod _nameplate_dimensions;
#[path = "_nameplate_interface.rs"]
mod _nameplate_interface;
#[path = "_nameplate_wing_interface.rs"]
mod _nameplate_wing_interface;
#[path = "_rust_enclosure_checks.rs"]
mod _rust_enclosure_checks;
#[path = "_swept_top.rs"]
mod _swept_top;
#[path = "_y_wall_dimensions.rs"]
mod _y_wall_dimensions;
#[path = "bulkhead_ring.rs"]
mod bulkhead_ring;
#[path = "data_ring.rs"]
mod data_ring;
#[path = "display_cover.rs"]
mod display_cover;
#[path = "display_gasket.rs"]
mod display_gasket;
#[path = "dock_structure.rs"]
mod dock_structure;
#[path = "enclosure.rs"]
mod enclosure;
#[path = "fixed_returns.rs"]
mod fixed_returns;
#[path = "nameplate.rs"]
mod nameplate;
#[path = "pump_case.rs"]
mod pump_case;
#[path = "pump_tray.rs"]
mod pump_tray;
#[path = "rear_equipment_caps.rs"]
mod rear_equipment_caps;
#[path = "rear_identification.rs"]
mod rear_identification;
#[path = "valve_tray.rs"]
mod valve_tray;
pub fn source(name: &str) -> Option<&'static str> {
    match name {
        "_above_core_shell" => {
            Some("hardware/printed-parts/enclosure/enclosure/_above_core_shell.py")
        }
        "_anchor_cap_interface" => {
            Some("hardware/printed-parts/enclosure/enclosure/_anchor_cap_interface.py")
        }
        "_back_top_meter" => Some("hardware/printed-parts/enclosure/enclosure/_back_top_meter.py"),
        "_data_wing_interface" => {
            Some("hardware/printed-parts/enclosure/enclosure/_data_wing_interface.py")
        }
        "_display_retention" => {
            Some("hardware/printed-parts/enclosure/enclosure/_display_retention.py")
        }
        "_display_wing_interface" => {
            Some("hardware/printed-parts/enclosure/enclosure/_display_wing_interface.py")
        }
        "_disposal_artwork" => {
            Some("hardware/printed-parts/enclosure/enclosure/_disposal_artwork.py")
        }
        "_enclosure_datums" => {
            Some("hardware/printed-parts/enclosure/enclosure/_enclosure_datums.py")
        }
        "_enclosure_dimensions" => {
            Some("hardware/printed-parts/enclosure/_enclosure_dimensions.py")
        }
        "_enclosure_interface" => {
            Some("hardware/printed-parts/enclosure/enclosure/_enclosure_interface.py")
        }
        "_enclosure_panel" => {
            Some("hardware/printed-parts/enclosure/enclosure/_enclosure_panel.py")
        }
        "_enclosure_rust_driver" => {
            Some("hardware/printed-parts/enclosure/enclosure/_enclosure_rust_driver.py")
        }
        "_enclosure_structure" => {
            Some("hardware/printed-parts/enclosure/enclosure/_enclosure_structure.py")
        }
        "_fixed_pump_mount" => {
            Some("hardware/printed-parts/enclosure/enclosure/_fixed_pump_mount.py")
        }
        "_grip_interface" => Some("hardware/printed-parts/enclosure/enclosure/_grip_interface.py"),
        "_nameplate_dimensions" => {
            Some("hardware/printed-parts/enclosure/nameplate/_nameplate_dimensions.py")
        }
        "_nameplate_interface" => {
            Some("hardware/printed-parts/enclosure/enclosure/_nameplate_interface.py")
        }
        "_nameplate_wing_interface" => {
            Some("hardware/printed-parts/enclosure/enclosure/_nameplate_wing_interface.py")
        }
        "_rust_enclosure_checks" => {
            Some("hardware/printed-parts/enclosure/enclosure/_rust_enclosure_checks.py")
        }
        "_swept_top" => Some("hardware/printed-parts/enclosure/enclosure/_swept_top.py"),
        "_y_wall_dimensions" => {
            Some("hardware/printed-parts/enclosure/y-wall-of-back-top/_y_wall_dimensions.py")
        }
        "bulkhead_ring" => Some("hardware/printed-parts/enclosure/bulkhead-ring/bulkhead_ring.py"),
        "data_ring" => Some("hardware/printed-parts/enclosure/data-ring/data_ring.py"),
        "display_cover" => Some("hardware/printed-parts/enclosure/display-cover/display_cover.py"),
        "display_gasket" => {
            Some("hardware/printed-parts/enclosure/display-gasket/display_gasket.py")
        }
        "dock_structure" => Some("hardware/printed-parts/enclosure/pump-dock/dock_structure.py"),
        "enclosure" => Some("hardware/printed-parts/enclosure/enclosure/enclosure.py"),
        "fixed_returns" => Some("hardware/printed-parts/enclosure/pump-dock/fixed_returns.py"),
        "nameplate" => Some("hardware/printed-parts/enclosure/nameplate/nameplate.py"),
        "pump_case" => Some("hardware/printed-parts/enclosure/pump-tray/pump_case.py"),
        "pump_tray" => Some("hardware/printed-parts/enclosure/pump-tray/pump_tray.py"),
        "rear_equipment_caps" => {
            Some("hardware/printed-parts/enclosure/rear-equipment-caps/rear_equipment_caps.py")
        }
        "rear_identification" => {
            Some("hardware/printed-parts/enclosure/rear-identification/rear_identification.py")
        }
        "valve_tray" => Some("hardware/printed-parts/enclosure/valve-tray/valve_tray.py"),
        _ => None,
    }
}
pub fn initialize(rt: Runtime, e: Env, name: &str) -> Result<()> {
    match name {
        "_above_core_shell" => _above_core_shell::initialize(rt, e),
        "_anchor_cap_interface" => _anchor_cap_interface::initialize(rt, e),
        "_back_top_meter" => _back_top_meter::initialize(rt, e),
        "_data_wing_interface" => _data_wing_interface::initialize(rt, e),
        "_display_retention" => _display_retention::initialize(rt, e),
        "_display_wing_interface" => _display_wing_interface::initialize(rt, e),
        "_disposal_artwork" => _disposal_artwork::initialize(rt, e),
        "_enclosure_datums" => _enclosure_datums::initialize(rt, e),
        "_enclosure_dimensions" => _enclosure_dimensions::initialize(rt, e),
        "_enclosure_interface" => _enclosure_interface::initialize(rt, e),
        "_enclosure_panel" => _enclosure_panel::initialize(rt, e),
        "_enclosure_rust_driver" => _enclosure_rust_driver::initialize(rt, e),
        "_enclosure_structure" => _enclosure_structure::initialize(rt, e),
        "_fixed_pump_mount" => _fixed_pump_mount::initialize(rt, e),
        "_grip_interface" => _grip_interface::initialize(rt, e),
        "_nameplate_dimensions" => _nameplate_dimensions::initialize(rt, e),
        "_nameplate_interface" => _nameplate_interface::initialize(rt, e),
        "_nameplate_wing_interface" => _nameplate_wing_interface::initialize(rt, e),
        "_rust_enclosure_checks" => _rust_enclosure_checks::initialize(rt, e),
        "_swept_top" => _swept_top::initialize(rt, e),
        "_y_wall_dimensions" => _y_wall_dimensions::initialize(rt, e),
        "bulkhead_ring" => bulkhead_ring::initialize(rt, e),
        "data_ring" => data_ring::initialize(rt, e),
        "display_cover" => display_cover::initialize(rt, e),
        "display_gasket" => display_gasket::initialize(rt, e),
        "dock_structure" => dock_structure::initialize(rt, e),
        "enclosure" => enclosure::initialize(rt, e),
        "fixed_returns" => fixed_returns::initialize(rt, e),
        "nameplate" => nameplate::initialize(rt, e),
        "pump_case" => pump_case::initialize(rt, e),
        "pump_tray" => pump_tray::initialize(rt, e),
        "rear_equipment_caps" => rear_equipment_caps::initialize(rt, e),
        "rear_identification" => rear_identification::initialize(rt, e),
        "valve_tray" => valve_tray::initialize(rt, e),
        _ => anyhow::bail!("unknown enclosure module {name}"),
    }
}
pub fn entrypoint(rt: Runtime, e: Env, name: &str) -> Result<Val> {
    match name {
        "_above_core_shell" => _above_core_shell::entrypoint(rt, e),
        "_anchor_cap_interface" => _anchor_cap_interface::entrypoint(rt, e),
        "_back_top_meter" => _back_top_meter::entrypoint(rt, e),
        "_data_wing_interface" => _data_wing_interface::entrypoint(rt, e),
        "_display_retention" => _display_retention::entrypoint(rt, e),
        "_display_wing_interface" => _display_wing_interface::entrypoint(rt, e),
        "_disposal_artwork" => _disposal_artwork::entrypoint(rt, e),
        "_enclosure_datums" => _enclosure_datums::entrypoint(rt, e),
        "_enclosure_dimensions" => _enclosure_dimensions::entrypoint(rt, e),
        "_enclosure_interface" => _enclosure_interface::entrypoint(rt, e),
        "_enclosure_panel" => _enclosure_panel::entrypoint(rt, e),
        "_enclosure_rust_driver" => _enclosure_rust_driver::entrypoint(rt, e),
        "_enclosure_structure" => _enclosure_structure::entrypoint(rt, e),
        "_fixed_pump_mount" => _fixed_pump_mount::entrypoint(rt, e),
        "_grip_interface" => _grip_interface::entrypoint(rt, e),
        "_nameplate_dimensions" => _nameplate_dimensions::entrypoint(rt, e),
        "_nameplate_interface" => _nameplate_interface::entrypoint(rt, e),
        "_nameplate_wing_interface" => _nameplate_wing_interface::entrypoint(rt, e),
        "_rust_enclosure_checks" => _rust_enclosure_checks::entrypoint(rt, e),
        "_swept_top" => _swept_top::entrypoint(rt, e),
        "_y_wall_dimensions" => _y_wall_dimensions::entrypoint(rt, e),
        "bulkhead_ring" => bulkhead_ring::entrypoint(rt, e),
        "data_ring" => data_ring::entrypoint(rt, e),
        "display_cover" => display_cover::entrypoint(rt, e),
        "display_gasket" => display_gasket::entrypoint(rt, e),
        "dock_structure" => dock_structure::entrypoint(rt, e),
        "enclosure" => enclosure::entrypoint(rt, e),
        "fixed_returns" => fixed_returns::entrypoint(rt, e),
        "nameplate" => nameplate::entrypoint(rt, e),
        "pump_case" => pump_case::entrypoint(rt, e),
        "pump_tray" => pump_tray::entrypoint(rt, e),
        "rear_equipment_caps" => rear_equipment_caps::entrypoint(rt, e),
        "rear_identification" => rear_identification::entrypoint(rt, e),
        "valve_tray" => valve_tray::entrypoint(rt, e),
        _ => anyhow::bail!("unknown enclosure entrypoint {name}"),
    }
}
pub fn by_path(path: &str) -> Option<&'static str> {
    match path {
        p if p.ends_with("hardware/printed-parts/enclosure/enclosure/_above_core_shell.py") => {
            Some("_above_core_shell")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/enclosure/_anchor_cap_interface.py") => {
            Some("_anchor_cap_interface")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/enclosure/_back_top_meter.py") => {
            Some("_back_top_meter")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/enclosure/_data_wing_interface.py") => {
            Some("_data_wing_interface")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/enclosure/_display_retention.py") => {
            Some("_display_retention")
        }
        p if p
            .ends_with("hardware/printed-parts/enclosure/enclosure/_display_wing_interface.py") =>
        {
            Some("_display_wing_interface")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/enclosure/_disposal_artwork.py") => {
            Some("_disposal_artwork")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/enclosure/_enclosure_datums.py") => {
            Some("_enclosure_datums")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/_enclosure_dimensions.py") => {
            Some("_enclosure_dimensions")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/enclosure/_enclosure_interface.py") => {
            Some("_enclosure_interface")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/enclosure/_enclosure_panel.py") => {
            Some("_enclosure_panel")
        }
        p if p
            .ends_with("hardware/printed-parts/enclosure/enclosure/_enclosure_rust_driver.py") =>
        {
            Some("_enclosure_rust_driver")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/enclosure/_enclosure_structure.py") => {
            Some("_enclosure_structure")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/enclosure/_fixed_pump_mount.py") => {
            Some("_fixed_pump_mount")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/enclosure/_grip_interface.py") => {
            Some("_grip_interface")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/nameplate/_nameplate_dimensions.py") => {
            Some("_nameplate_dimensions")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/enclosure/_nameplate_interface.py") => {
            Some("_nameplate_interface")
        }
        p if p.ends_with(
            "hardware/printed-parts/enclosure/enclosure/_nameplate_wing_interface.py",
        ) =>
        {
            Some("_nameplate_wing_interface")
        }
        p if p
            .ends_with("hardware/printed-parts/enclosure/enclosure/_rust_enclosure_checks.py") =>
        {
            Some("_rust_enclosure_checks")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/enclosure/_swept_top.py") => {
            Some("_swept_top")
        }
        p if p.ends_with(
            "hardware/printed-parts/enclosure/y-wall-of-back-top/_y_wall_dimensions.py",
        ) =>
        {
            Some("_y_wall_dimensions")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/bulkhead-ring/bulkhead_ring.py") => {
            Some("bulkhead_ring")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/data-ring/data_ring.py") => {
            Some("data_ring")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/display-cover/display_cover.py") => {
            Some("display_cover")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/display-gasket/display_gasket.py") => {
            Some("display_gasket")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/pump-dock/dock_structure.py") => {
            Some("dock_structure")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/enclosure/enclosure.py") => {
            Some("enclosure")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/pump-dock/fixed_returns.py") => {
            Some("fixed_returns")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/nameplate/nameplate.py") => {
            Some("nameplate")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/pump-tray/pump_case.py") => {
            Some("pump_case")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/pump-tray/pump_tray.py") => {
            Some("pump_tray")
        }
        p if p.ends_with(
            "hardware/printed-parts/enclosure/rear-equipment-caps/rear_equipment_caps.py",
        ) =>
        {
            Some("rear_equipment_caps")
        }
        p if p.ends_with(
            "hardware/printed-parts/enclosure/rear-identification/rear_identification.py",
        ) =>
        {
            Some("rear_identification")
        }
        p if p.ends_with("hardware/printed-parts/enclosure/valve-tray/valve_tray.py") => {
            Some("valve_tray")
        }
        _ => None,
    }
}
