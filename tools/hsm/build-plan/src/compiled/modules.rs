use super::*;
#[path="modules/gen_build.rs"] mod gen_build;
pub fn source(name:&str)->Option<&'static str> {match name {"gen_build"=>Some("tools/bazel/gen_build.py"),_=>None}}
pub fn initialize(rt:Runtime,e:Env,name:&str)->Result<()> {match name {"gen_build"=>gen_build::initialize(rt,e),_=>bail!("unknown build module {name}")}}
pub fn entrypoint(rt:Runtime,e:Env,name:&str)->Result<Val> {match name {"gen_build"=>gen_build::entrypoint(rt,e),_=>bail!("unknown build module {name}")}}
