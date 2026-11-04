//! Shared enclosure dimensions that do not require building the enclosure model.
//!
//! Parts that mate with the shell import this module. The enclosure module re-exports the same
//! names so its public geometry API stays intact without making a small mating part load the whole
//! machine.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_enclosure_interface.rs",
            line!(),
        );
        {
            let fun4 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args2 = Vec::new();
            let mut kw3 = Vec::new();
            args2.push(Val::Int(0i64));
            args2.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_interface.rs",line!());{let fun7=e.get("str")?;let mut args5=Vec::new();let mut kw6=Vec::new();args5.push(binary("truediv",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_interface.rs",line!());{let fun10=e.get("next")?;let mut args8=Vec::new();let mut kw9=Vec::new();args8.push({let e=e.child();let out11=Val::list(vec![]);for item12 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_interface.rs",line!());{let fun15={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_interface.rs",line!());{let fun18=e.get("Path")?;let mut args16=Vec::new();let mut kw17=Vec::new();args16.push(e.get("__file__")?);fun18.call(args16,kw17)?}}.attr("resolve")?;let mut args13=Vec::new();let mut kw14=Vec::new();fun15.call(args13,kw14)?}}.attr("parents")?.iter()? {e.set("p",item12)?;if {let v19=e.get("p")?.attr("name")?;let v20=Val::Str("printed-parts".into());Val::Bool(compare("eq",v19.clone(),v20.clone())?.truthy()?)}.truthy()? {out11.attr("append")?.call(vec![e.get("p")?],vec![])?;}}out11});fun10.call(args8,kw9)?}},Val::Str("cadlib".into()))?);fun7.call(args5,kw6)?}});
            fun4.call(args2, kw3)?
        }
    };
    e.set("fits", rt.import_module("fits")?)?;
    let mod21 = rt.import_module("_enclosure_data")?;
    e.set("_read", rt.member("_enclosure_data", "read")?)?;
    let assigned22 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_enclosure_interface.rs",
            line!(),
        );
        {
            let fun25 = e.get("_read")?;
            let mut args23 = Vec::new();
            let mut kw24 = Vec::new();
            args23.push(Val::Str("core-interface".into()));
            kw24.push(("fits".into(), {
                let e = e.child();
                let out26 = Val::dict(vec![]);
                for item27 in {
                    let mut s = Vec::new();
                    s.push(Val::Str("slip".into()));
                    s.push(Val::Str("running".into()));
                    s.push(Val::Str("supported_surface".into()));
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("name", item27)?;
                    out26.set(e.get("name")?, {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_interface.rs",
                            line!(),
                        );
                        {
                            let fun30 = e.get("getattr")?;
                            let mut args28 = Vec::new();
                            let mut kw29 = Vec::new();
                            args28.push(e.get("fits")?);
                            args28.push(e.get("name")?);
                            fun30.call(args28, kw29)?
                        }
                    })?;
                }
                out26
            }));
            fun25.call(args23, kw24)?
        }
    };
    e.set("_values", assigned22.clone())?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_enclosure_interface.rs",
            line!(),
        );
        {
            let fun33 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_interface.rs",
                    line!(),
                );
                {
                    let fun36 = e.get("globals")?;
                    let mut args34 = Vec::new();
                    let mut kw35 = Vec::new();
                    fun36.call(args34, kw35)?
                }
            }
            .attr("update")?;
            let mut args31 = Vec::new();
            let mut kw32 = Vec::new();
            args31.push(e.get("_values")?);
            fun33.call(args31, kw32)?
        }
    };
    // flute_reach
    e.set("flute_reach", {
        let params = vec![("band_height".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_interface.rs",
                    line!(),
                );
                {
                    let fun39 = e.get("_read")?;
                    let mut args37 = Vec::new();
                    let mut kw38 = Vec::new();
                    args37.push(Val::Str("core-flute-reach".into()));
                    kw38.push(("band_height".into(), e.get("band_height")?));
                    kw38.push(("values".into(), {
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("flute_rise".into()), e.get("flute_rise")?)?;
                        d.set(Val::Str("flute_depth".into()), e.get("flute_depth")?)?;
                        d
                    }));
                    fun39.call(args37, kw38)?
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
