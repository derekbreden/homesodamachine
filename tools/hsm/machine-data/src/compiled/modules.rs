use super::*;
#[path="enclosure_assembly.rs"] mod m_enclosure_assembly;
#[path="manifold_layout.rs"] mod m_manifold_layout;
#[path="_scorecard.rs"] mod m__scorecard;
#[path="_lines.rs"] mod m__lines;
#[path="rear_snaps.rs"] mod m_rear_snaps;
#[path="above_core_wiring.rs"] mod m_above_core_wiring;
#[path="above_core_parts.rs"] mod m_above_core_parts;
#[path="above_core_bom.rs"] mod m_above_core_bom;
#[path="_machine_reporting.rs"] mod m__machine_reporting;
#[path="_gas_chain.rs"] mod m__gas_chain;
#[path="rear_plumbing.rs"] mod m_rear_plumbing;
#[path="_machine_checks.rs"] mod m__machine_checks;
#[path="_machine_layout.rs"] mod m__machine_layout;
#[path="_machine_equipment.rs"] mod m__machine_equipment;
#[path="_facts.rs"] mod m__facts;
#[path="_machine.rs"] mod m__machine;
#[path="_stated_bounds.rs"] mod m__stated_bounds;
#[path="_machine_export.rs"] mod m__machine_export;
#[path="_machine_routes.rs"] mod m__machine_routes;
#[path="_assembly_questions.rs"] mod m__assembly_questions;
pub fn source(name:&str)->Option<&'static str>{match name {
"enclosure_assembly"=>Some("hardware/manifold-layout/enclosure_assembly.py"),
"manifold_layout"=>Some("hardware/manifold-layout/manifold_layout.py"),
"_scorecard"=>Some("hardware/manifold-layout/_scorecard.py"),
"_lines"=>Some("hardware/manifold-layout/_lines.py"),
"rear_snaps"=>Some("hardware/manifold-layout/rear_snaps.py"),
"above_core_wiring"=>Some("hardware/manifold-layout/above_core_wiring.py"),
"above_core_parts"=>Some("hardware/manifold-layout/above_core_parts.py"),
"above_core_bom"=>Some("hardware/manifold-layout/above_core_bom.py"),
"_machine_reporting"=>Some("hardware/manifold-layout/_machine_reporting.py"),
"_gas_chain"=>Some("hardware/manifold-layout/_gas_chain.py"),
"rear_plumbing"=>Some("hardware/manifold-layout/rear_plumbing.py"),
"_machine_checks"=>Some("hardware/scripts/_machine_checks.py"),
"_machine_layout"=>Some("hardware/scripts/_machine_layout.py"),
"_machine_equipment"=>Some("hardware/scripts/_machine_equipment.py"),
"_facts"=>Some("hardware/scripts/_facts.py"),
"_machine"=>Some("hardware/scripts/_machine.py"),
"_stated_bounds"=>Some("hardware/scripts/_stated_bounds.py"),
"_machine_export"=>Some("hardware/scripts/_machine_export.py"),
"_machine_routes"=>Some("hardware/scripts/_machine_routes.py"),
"_assembly_questions"=>Some("hardware/manifold-layout/enclosure_assembly.py"),
_=>None}}
pub fn initialize(rt:Runtime,e:Env,name:&str)->Result<()>{match name {
"enclosure_assembly"=>m_enclosure_assembly::initialize(rt,e),
"manifold_layout"=>m_manifold_layout::initialize(rt,e),
"_scorecard"=>m__scorecard::initialize(rt,e),
"_lines"=>m__lines::initialize(rt,e),
"rear_snaps"=>m_rear_snaps::initialize(rt,e),
"above_core_wiring"=>m_above_core_wiring::initialize(rt,e),
"above_core_parts"=>m_above_core_parts::initialize(rt,e),
"above_core_bom"=>m_above_core_bom::initialize(rt,e),
"_machine_reporting"=>m__machine_reporting::initialize(rt,e),
"_gas_chain"=>m__gas_chain::initialize(rt,e),
"rear_plumbing"=>m_rear_plumbing::initialize(rt,e),
"_machine_checks"=>m__machine_checks::initialize(rt,e),
"_machine_layout"=>m__machine_layout::initialize(rt,e),
"_machine_equipment"=>m__machine_equipment::initialize(rt,e),
"_facts"=>m__facts::initialize(rt,e),
"_machine"=>m__machine::initialize(rt,e),
"_stated_bounds"=>m__stated_bounds::initialize(rt,e),
"_machine_export"=>m__machine_export::initialize(rt,e),
"_machine_routes"=>m__machine_routes::initialize(rt,e),
"_assembly_questions"=>m__assembly_questions::initialize(rt,e),
_=>bail!("unknown machine module {name}")}}
pub fn entrypoint(rt:Runtime,e:Env,name:&str)->Result<Val>{match name {
"enclosure_assembly"=>m_enclosure_assembly::entrypoint(rt,e),
"manifold_layout"=>m_manifold_layout::entrypoint(rt,e),
"_scorecard"=>m__scorecard::entrypoint(rt,e),
"_lines"=>m__lines::entrypoint(rt,e),
"rear_snaps"=>m_rear_snaps::entrypoint(rt,e),
"above_core_wiring"=>m_above_core_wiring::entrypoint(rt,e),
"above_core_parts"=>m_above_core_parts::entrypoint(rt,e),
"above_core_bom"=>m_above_core_bom::entrypoint(rt,e),
"_machine_reporting"=>m__machine_reporting::entrypoint(rt,e),
"_gas_chain"=>m__gas_chain::entrypoint(rt,e),
"rear_plumbing"=>m_rear_plumbing::entrypoint(rt,e),
"_machine_checks"=>m__machine_checks::entrypoint(rt,e),
"_machine_layout"=>m__machine_layout::entrypoint(rt,e),
"_machine_equipment"=>m__machine_equipment::entrypoint(rt,e),
"_facts"=>m__facts::entrypoint(rt,e),
"_machine"=>m__machine::entrypoint(rt,e),
"_stated_bounds"=>m__stated_bounds::entrypoint(rt,e),
"_machine_export"=>m__machine_export::entrypoint(rt,e),
"_machine_routes"=>m__machine_routes::entrypoint(rt,e),
"_assembly_questions"=>m__assembly_questions::entrypoint(rt,e),
_=>bail!("unknown machine module {name}")}}
pub fn by_path(path:&str)->Option<&'static str>{
if path.ends_with("hardware/manifold-layout/enclosure_assembly.py") {return Some("enclosure_assembly");}
if path.ends_with("hardware/manifold-layout/manifold_layout.py") {return Some("manifold_layout");}
if path.ends_with("hardware/manifold-layout/_scorecard.py") {return Some("_scorecard");}
if path.ends_with("hardware/manifold-layout/_lines.py") {return Some("_lines");}
if path.ends_with("hardware/manifold-layout/rear_snaps.py") {return Some("rear_snaps");}
if path.ends_with("hardware/manifold-layout/above_core_wiring.py") {return Some("above_core_wiring");}
if path.ends_with("hardware/manifold-layout/above_core_parts.py") {return Some("above_core_parts");}
if path.ends_with("hardware/manifold-layout/above_core_bom.py") {return Some("above_core_bom");}
if path.ends_with("hardware/manifold-layout/_machine_reporting.py") {return Some("_machine_reporting");}
if path.ends_with("hardware/manifold-layout/_gas_chain.py") {return Some("_gas_chain");}
if path.ends_with("hardware/manifold-layout/rear_plumbing.py") {return Some("rear_plumbing");}
if path.ends_with("hardware/scripts/_machine_checks.py") {return Some("_machine_checks");}
if path.ends_with("hardware/scripts/_machine_layout.py") {return Some("_machine_layout");}
if path.ends_with("hardware/scripts/_machine_equipment.py") {return Some("_machine_equipment");}
if path.ends_with("hardware/scripts/_facts.py") {return Some("_facts");}
if path.ends_with("hardware/scripts/_machine.py") {return Some("_machine");}
if path.ends_with("hardware/scripts/_stated_bounds.py") {return Some("_stated_bounds");}
if path.ends_with("hardware/scripts/_machine_export.py") {return Some("_machine_export");}
if path.ends_with("hardware/scripts/_machine_routes.py") {return Some("_machine_routes");}
if path.ends_with("hardware/manifold-layout/enclosure_assembly.py") {return Some("_assembly_questions");}
None}
