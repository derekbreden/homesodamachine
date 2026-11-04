//! Dispatch the enclosure's printed viewer surfaces to its Rust writer.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    // print_payload
    e.set("print_payload", {
        let params = vec![
            ("step".into(), None, false),
            ("check_print".into(), Some(Val::Bool(false)), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod1 = rt.import_module("_rust_enclosure_presentation")?;
            e.set(
                "write",
                rt.member("_rust_enclosure_presentation", "print_payload")?,
            )?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_presentation.rs",
                    line!(),
                );
                {
                    let fun4 = e.get("write")?;
                    let mut args2 = Vec::new();
                    let mut kw3 = Vec::new();
                    args2.push(e.get("step")?);
                    kw3.push(("check_print".into(), e.get("check_print")?));
                    fun4.call(args2, kw3)?
                }
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
