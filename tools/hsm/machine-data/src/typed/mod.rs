//! The machine's layout, assembly and report recipes as typed Rust modules.
//!
//! Each module keeps the namespace its Python surface reads: the same names, holding the same
//! values, with its functions taking and returning Python values at that boundary.
pub mod num;
pub mod py;
pub mod rt;
pub mod docs;

pub mod _assembly_questions;
pub mod _facts;
pub mod _gas_chain;
pub mod _lines;
pub mod _machine;
pub mod _machine_checks;
pub mod _machine_equipment;
pub mod _machine_export;
pub mod _machine_layout;
pub mod _machine_reporting;
pub mod _machine_routes;
pub mod _scorecard;
pub mod _stated_bounds;
pub mod _tube_export;
pub mod above_core_bom;
pub mod above_core_parts;
pub mod above_core_wiring;
pub mod check_asse_drain;
pub mod enclosure_assembly;
pub mod manifold_layout;
pub mod rear_plumbing;
pub mod rear_snaps;

use anyhow::{Result, bail};
use rt::{Ns, Rt};

/// Every module and the source path its namespace reports as `__file__`, in lookup order.
const MODULES: &[(&str, &str)] = &[
    ("enclosure_assembly", "hardware/manifold-layout/enclosure_assembly.py"),
    ("manifold_layout", "hardware/manifold-layout/manifold_layout.py"),
    ("_scorecard", "hardware/manifold-layout/_scorecard.py"),
    ("_lines", "hardware/manifold-layout/_lines.py"),
    ("rear_snaps", "hardware/manifold-layout/rear_snaps.py"),
    ("above_core_wiring", "hardware/manifold-layout/above_core_wiring.py"),
    ("above_core_parts", "hardware/manifold-layout/above_core_parts.py"),
    ("above_core_bom", "hardware/manifold-layout/above_core_bom.py"),
    ("_machine_reporting", "hardware/manifold-layout/_machine_reporting.py"),
    ("_gas_chain", "hardware/manifold-layout/_gas_chain.py"),
    ("rear_plumbing", "hardware/manifold-layout/rear_plumbing.py"),
    ("_machine_checks", "hardware/scripts/_machine_checks.py"),
    ("_machine_layout", "hardware/scripts/_machine_layout.py"),
    ("_machine_equipment", "hardware/scripts/_machine_equipment.py"),
    ("_facts", "hardware/scripts/_facts.py"),
    ("_machine", "hardware/scripts/_machine.py"),
    ("_stated_bounds", "hardware/scripts/_stated_bounds.py"),
    ("_tube_export", "hardware/scripts/_tube_export.py"),
    ("check_asse_drain", "hardware/scripts/check_asse_drain.py"),
    ("_machine_export", "hardware/scripts/_machine_export.py"),
    ("_machine_routes", "hardware/scripts/_machine_routes.py"),
    ("_assembly_questions", "hardware/manifold-layout/enclosure_assembly.py"),
];

/// Whether a module runs typed in the hybrid development build; the rest run their generated
/// namespaces.
#[cfg(feature = "hybrid")]
pub fn converted(name: &str) -> bool {
    match name {
        "enclosure_assembly" => enclosure_assembly::TYPED,
        "manifold_layout" => manifold_layout::TYPED,
        "_scorecard" => _scorecard::TYPED,
        "_lines" => _lines::TYPED,
        "rear_snaps" => rear_snaps::TYPED,
        "above_core_wiring" => above_core_wiring::TYPED,
        "above_core_parts" => above_core_parts::TYPED,
        "above_core_bom" => above_core_bom::TYPED,
        "_machine_reporting" => _machine_reporting::TYPED,
        "_gas_chain" => _gas_chain::TYPED,
        "rear_plumbing" => rear_plumbing::TYPED,
        "_machine_checks" => _machine_checks::TYPED,
        "_machine_layout" => _machine_layout::TYPED,
        "_machine_equipment" => _machine_equipment::TYPED,
        "_facts" => _facts::TYPED,
        "_machine" => _machine::TYPED,
        "_stated_bounds" => _stated_bounds::TYPED,
        "_tube_export" => _tube_export::TYPED,
        "check_asse_drain" => check_asse_drain::TYPED,
        "_machine_export" => _machine_export::TYPED,
        "_machine_routes" => _machine_routes::TYPED,
        "_assembly_questions" => _assembly_questions::TYPED,
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
        "enclosure_assembly" => enclosure_assembly::install(rt, ns)?,
        "manifold_layout" => manifold_layout::install(rt, ns)?,
        "_scorecard" => _scorecard::install(rt, ns)?,
        "_lines" => _lines::install(rt, ns)?,
        "rear_snaps" => rear_snaps::install(rt, ns)?,
        "above_core_wiring" => above_core_wiring::install(rt, ns)?,
        "above_core_parts" => above_core_parts::install(rt, ns)?,
        "above_core_bom" => above_core_bom::install(rt, ns)?,
        "_machine_reporting" => _machine_reporting::install(rt, ns)?,
        "_gas_chain" => _gas_chain::install(rt, ns)?,
        "rear_plumbing" => rear_plumbing::install(rt, ns)?,
        "_machine_checks" => _machine_checks::install(rt, ns)?,
        "_machine_layout" => _machine_layout::install(rt, ns)?,
        "_machine_equipment" => _machine_equipment::install(rt, ns)?,
        "_facts" => _facts::install(rt, ns)?,
        "_machine" => _machine::install(rt, ns)?,
        "_stated_bounds" => _stated_bounds::install(rt, ns)?,
        "_tube_export" => _tube_export::install(rt, ns)?,
        "check_asse_drain" => check_asse_drain::install(rt, ns)?,
        "_machine_export" => _machine_export::install(rt, ns)?,
        "_machine_routes" => _machine_routes::install(rt, ns)?,
        "_assembly_questions" => _assembly_questions::install(rt, ns)?,
        _ => bail!("unknown machine module {name}"),
    }
    crate::native_profiles::install(rt.clone(), ns, name)
}

/// A module run as a script: its `if __name__ == "__main__"` block.
pub fn entrypoint(rt: &Rt, name: &'static str) -> Result<()> {
    #[cfg(feature = "hybrid")]
    if !converted(name) {
        return crate::compiled::entrypoint_generated(rt.root(), name);
    }
    let _frame = rt.frame(name);
    match name {
        "enclosure_assembly" => enclosure_assembly::main_block(rt),
        "manifold_layout" => manifold_layout::main_block(rt),
        "_scorecard" => _scorecard::main_block(rt),
        "_facts" => _facts::main_block(rt),
        "check_asse_drain" => check_asse_drain::main_block(rt),
        _ => Ok(()),
    }
}
