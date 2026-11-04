//! Rust construction datums for the enclosure's swept exterior.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("_swept_top", rt.import_module("_swept_top")?)?;
    let mod1 = rt.import_module("overhang_round")?;
    e.set(
        "OUTWARD_PER_HEIGHT",
        rt.member("overhang_round", "OUTWARD_PER_HEIGHT")?,
    )?;
    let mod2 = rt.import_module("_enclosure_data")?;
    e.set("read", rt.member("_enclosure_data", "read")?)?;
    let mod3 = rt.import_module("_enclosure_core_data")?;
    e.set("tupled", rt.member("_enclosure_core_data", "tupled")?)?;
    // numbers
    e.set("numbers", {
        let params = vec![("outer".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_structure.rs",
                    line!(),
                );
                {
                    let fun6 = e.get("tupled")?;
                    let mut args4 = Vec::new();
                    let mut kw5 = Vec::new();
                    args4.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_structure.rs",
                            line!(),
                        );
                        {
                            let fun9 = e.get("read")?;
                            let mut args7 = Vec::new();
                            let mut kw8 = Vec::new();
                            args7.push(Val::Str("swept-structure".into()));
                            kw8.push(("outer".into(), e.get("outer")?));
                            kw8.push(("parameters".into(), {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_enclosure_structure.rs",
                                    line!(),
                                );
                                {
                                    let fun12 = e.get("_swept_top")?.attr("_parameters")?;
                                    let mut args10 = Vec::new();
                                    let mut kw11 = Vec::new();
                                    fun12.call(args10, kw11)?
                                }
                            }));
                            kw8.push(("outward_per_height".into(), e.get("OUTWARD_PER_HEIGHT")?));
                            fun9.call(args7, kw8)?
                        }
                    });
                    fun6.call(args4, kw5)?
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
