#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("print_mesh")?;
    e.set("piece_mesh", rt.member("print_mesh", "print_mesh")?)?;
    e.set(
        "write_print_stl",
        rt.member("print_mesh", "write_print_stl")?,
    )?;
    // write_bed_file
    e.set("write_bed_file", {
        let params = vec![("solid".into(), None, false), ("path".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned2 = {
                let fun5 = e.get("write_print_stl")?;
                let mut args3 = Vec::new();
                let mut kw4 = Vec::new();
                args3.push(e.get("solid")?);
                args3.push(e.get("path")?);
                fun5.call(args3, kw4)?
            };
            e.set("mesh", assigned2.clone())?;
            {
                let fun8 = e.get("print")?;
                let mut args6 = Vec::new();
                let mut kw7 = Vec::new();
                args6.push({
                    let mut str9 = String::new();
                    str9.push_str("-> ");
                    str9.push_str(&format(&e.get("path")?.attr("name")?, &String::new())?);
                    str9.push_str(" (");
                    str9.push_str(&format(
                        &{
                            let fun12 = e.get("len")?;
                            let mut args10 = Vec::new();
                            let mut kw11 = Vec::new();
                            args10.push(e.get("mesh")?.attr("faces")?);
                            fun12.call(args10, kw11)?
                        },
                        &String::new(),
                    )?);
                    str9.push_str(" facets, watertight)");
                    Val::Str(str9)
                });
                fun8.call(args6, kw7)?
            };
            return Ok(e.get("mesh")?);
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
