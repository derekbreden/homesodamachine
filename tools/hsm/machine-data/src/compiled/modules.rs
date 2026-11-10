use super::*;
#[path="_machine_export.rs"] mod m__machine_export;
pub fn source(name:&str)->Option<&'static str>{match name {
"_machine_export"=>Some("hardware/scripts/_machine_export.py"),
_=>None}}
pub fn initialize(rt:Runtime,e:Env,name:&str)->Result<()>{match name {
"_machine_export"=>m__machine_export::initialize(rt,e),
_=>bail!("unknown machine module {name}")}}
pub fn entrypoint(rt:Runtime,e:Env,name:&str)->Result<Val>{match name {
"_machine_export"=>m__machine_export::entrypoint(rt,e),
_=>bail!("unknown machine module {name}")}}
pub fn by_path(path:&str)->Option<&'static str>{
if path.ends_with("hardware/scripts/_machine_export.py") {return Some("_machine_export");}
None}
