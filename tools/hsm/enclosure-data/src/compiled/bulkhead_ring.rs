//! Rear-port identification figures: the word each of the +Y wall of back-top's six stations
//! carries, the lettering those words are set in, and the label envelope the wall's port pockets
//! are read from.
//!
//! Nothing here builds a part. `rear_identification` cuts the six installed tiles and `tube_collar`
//! the collars that name the same lines, and both take each station's word, the key its two filaments
//! are read under and the lettering from here, so a word changed for a port is changed on the wall
//! and on the tube by one edit. `data_ring` letters in the same face.
//!
//!     STATIONS, FLUIDS    each station's word, and the key `_y_wall_dimensions` reads its chip and
//!                         word filaments under
//!     WORD_*              the face, em, recess depth, raise and measured widths of the lettering
//!     RING_W, THICK, RISE, od, bottom, rise
//!                         the label envelope `enclosure_assembly` reads for the wall's port
//!                         pockets, the bosses behind them and the clamp stack
//!     split               a two-colour label STEP back apart, as `(tile, word)`
//!
//! Coordinate frame — THE FITTING'S:
//!   Y = the fitting's flow axis. +Y = outboard, toward the customer's tube.
//!   Origin = the label's INBOARD face, the one that lands on the wall. A label spans y = 0 to its
//!       own thickness, and its word fills a recess in the outboard face and stands proud of it.
//!   +Z = up. X completes the right-handed frame, so from outside the machine — looking down −Y —
//!       +X runs to the LEFT and a word reads along −X.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("collections", rt.import_module("collections")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let assigned2 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",
            line!(),
        );
        {
            let fun5 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",
                    line!(),
                );
                {
                    let fun8 = e.get("Path")?;
                    let mut args6 = Vec::new();
                    let mut kw7 = Vec::new();
                    args6.push(e.get("__file__")?);
                    fun8.call(args6, kw7)?
                }
            }
            .attr("resolve")?;
            let mut args3 = Vec::new();
            let mut kw4 = Vec::new();
            fun5.call(args3, kw4)?
        }
    };
    e.set("_here", assigned2.clone())?;
    let assigned9 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",
            line!(),
        );
        {
            let fun12 = e.get("next")?;
            let mut args10 = Vec::new();
            let mut kw11 = Vec::new();
            args10.push({
                let e = e.child();
                let out13 = Val::list(vec![]);
                for item14 in e.get("_here")?.attr("parents")?.iter()? {
                    e.set("p", item14)?;
                    if {
                        let v15 = e.get("p")?.attr("name")?;
                        let v16 = Val::Str("hardware".into());
                        Val::Bool(compare("eq", v15.clone(), v16.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        out13.attr("append")?.call(vec![e.get("p")?], vec![])?;
                    }
                }
                out13
            });
            fun12.call(args10, kw11)?
        }
    };
    e.set("_hw", assigned9.clone())?;
    for item17 in {
        let mut s = Vec::new();
        s.push(binary(
            "truediv",
            e.get("_hw")?,
            Val::Str("scripts".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("_hw")?, Val::Str("printed-parts".into()))?,
            Val::Str("cadlib".into()),
        )?);
        s.push(binary(
            "truediv",
            binary(
                "truediv",
                binary("truediv", e.get("_hw")?, Val::Str("printed-parts".into()))?,
                Val::Str("enclosure".into()),
            )?,
            Val::Str("enclosure".into()),
        )?);
        s.push(binary(
            "truediv",
            binary(
                "truediv",
                binary("truediv", e.get("_hw")?, Val::Str("printed-parts".into()))?,
                Val::Str("enclosure".into()),
            )?,
            Val::Str("y-wall-of-back-top".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("_hw")?, Val::Str("reference".into()))?,
            Val::Str("jg-bulkhead-union".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("_hw")?, Val::Str("reference".into()))?,
            Val::Str("neofit-bulkhead".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("_hw")?, Val::Str("reference".into()))?,
            Val::Str("neofit-drain-bulkhead".into()),
        )?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("_p", item17)?;
        {
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",
                line!(),
            );
            {
                let fun20 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args18 = Vec::new();
                let mut kw19 = Vec::new();
                args18.push(Val::Int(0i64));
                args18.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",
                        line!(),
                    );
                    {
                        let fun23 = e.get("str")?;
                        let mut args21 = Vec::new();
                        let mut kw22 = Vec::new();
                        args21.push(e.get("_p")?);
                        fun23.call(args21, kw22)?
                    }
                });
                fun20.call(args18, kw19)?
            }
        };
    }
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",
            line!(),
        );
        {
            let fun26 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args24 = Vec::new();
            let mut kw25 = Vec::new();
            args24.push(Val::Int(0i64));
            args24.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",line!());{let fun29=e.get("str")?;let mut args27=Vec::new();let mut kw28=Vec::new();args27.push(binary("truediv",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",line!());{let fun32=e.get("next")?;let mut args30=Vec::new();let mut kw31=Vec::new();args30.push({let e=e.child();let out33=Val::list(vec![]);for item34 in e.get("_here")?.attr("parents")?.iter()? {e.set("p",item34)?;if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",line!());{let fun37=binary("truediv",binary("truediv",e.get("p")?,Val::Str("tools".into()))?,Val::Str("docgen".into()))?.attr("is_dir")?;let mut args35=Vec::new();let mut kw36=Vec::new();fun37.call(args35,kw36)?}}.truthy()? {out33.attr("append")?.call(vec![e.get("p")?],vec![])?;}}out33});fun32.call(args30,kw31)?}},Val::Str("tools".into()))?);fun29.call(args27,kw28)?}});
            fun26.call(args24, kw25)?
        }
    };
    e.set("cq", rt.import_module("cadquery")?)?;
    e.set("_jg", rt.import_module("jg_bulkhead_union")?)?;
    e.set("_drain", rt.import_module("neofit_drain_bulkhead")?)?;
    e.set("_neo", rt.import_module("neofit_bulkhead")?)?;
    e.set("port_chip", rt.import_module("port_chip")?)?;
    e.set("_enc_interface", rt.import_module("_enclosure_interface")?)?;
    let assigned38 = {
        let d = Val::dict(vec![]);
        d.set(Val::Str("union".into()), e.get("_jg")?)?;
        d.set(Val::Str("neofit".into()), e.get("_neo")?)?;
        d.set(Val::Str("drain".into()), e.get("_drain")?)?;
        d
    };
    e.set("FAMILIES", assigned38.clone())?;
    let mod39 = rt.import_module("_enclosure_data")?;
    e.set("_dimensions", rt.member("_enclosure_data", "dimensions")?)?;
    e.set("_read", rt.member("_enclosure_data", "read")?)?;
    let assigned40 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",
            line!(),
        );
        {
            let fun43 = e.get("_dimensions")?;
            let mut args41 = Vec::new();
            let mut kw42 = Vec::new();
            fun43.call(args41, kw42)?
        }
    }
    .get(Val::Str("bulkhead".into()))?;
    e.set("_values", assigned40.clone())?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",
            line!(),
        );
        {
            let fun46 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",
                    line!(),
                );
                {
                    let fun49 = e.get("globals")?;
                    let mut args47 = Vec::new();
                    let mut kw48 = Vec::new();
                    fun49.call(args47, kw48)?
                }
            }
            .attr("update")?;
            let mut args44 = Vec::new();
            let mut kw45 = Vec::new();
            args44.push({
                let e = e.child();
                let out50 = Val::dict(vec![]);
                for item51 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",
                        line!(),
                    );
                    {
                        let fun54 = e.get("_values")?.attr("items")?;
                        let mut args52 = Vec::new();
                        let mut kw53 = Vec::new();
                        fun54.call(args52, kw53)?
                    }
                }
                .iter()?
                {
                    let unpack55 = unpack(item51, 2)?;
                    e.set("name", unpack55[0].clone())?;
                    e.set("value", unpack55[1].clone())?;
                    if {
                        let v58 = {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",
                                line!(),
                            );
                            {
                                let fun61 = e.get("name")?.attr("isupper")?;
                                let mut args59 = Vec::new();
                                let mut kw60 = Vec::new();
                                fun61.call(args59, kw60)?
                            }
                        };
                        if v58.truthy()? {
                            {
                                let v56 = e.get("name")?;
                                let v57 = Val::Str("STATIONS".into());
                                Val::Bool(compare("ne", v56.clone(), v57.clone())?.truthy()?)
                            }
                        } else {
                            v58
                        }
                    }
                    .truthy()?
                    {
                        out50.set(e.get("name")?, e.get("value")?)?;
                    }
                }
                out50
            });
            fun46.call(args44, kw45)?
        }
    };
    let assigned62 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",
            line!(),
        );
        {
            let fun65 = e.get("collections")?.attr("namedtuple")?;
            let mut args63 = Vec::new();
            let mut kw64 = Vec::new();
            args63.push(Val::Str("Chip".into()));
            args63.push(Val::Str("word".into()));
            fun65.call(args63, kw64)?
        }
    };
    e.set("Chip", assigned62.clone())?;
    let assigned66 = {
        let e = e.child();
        let out67 = Val::dict(vec![]);
        for item68 in e
            .get("_values")?
            .get(Val::Str("station_order".into()))?
            .iter()?
        {
            e.set("name", item68)?;
            out67.set(e.get("name")?, {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",
                    line!(),
                );
                {
                    let fun71 = e.get("Chip")?;
                    let mut args69 = Vec::new();
                    let mut kw70 = Vec::new();
                    args69.push(
                        e.get("_values")?
                            .get(Val::Str("STATIONS".into()))?
                            .get(e.get("name")?)?,
                    );
                    fun71.call(args69, kw70)?
                }
            })?;
        }
        out67
    };
    e.set("STATIONS", assigned66.clone())?;
    let assigned72 = {
        let e = e.child();
        let out73 = Val::dict(vec![]);
        for item74 in e
            .get("_values")?
            .get(Val::Str("station_order".into()))?
            .iter()?
        {
            e.set("name", item74)?;
            out73.set(
                e.get("name")?,
                e.get("_values")?
                    .get(Val::Str("FLUIDS".into()))?
                    .get(e.get("name")?)?,
            )?;
        }
        out73
    };
    e.set("FLUIDS", assigned72.clone())?;
    // od
    e.set("od", {
        let params = vec![("fam".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("_values")?.get(Val::Str("width".into()))?);
            Ok(Val::None)
        })
    })?;
    // bottom
    e.set("bottom", {
        let params = vec![("fam".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",
                    line!(),
                );
                {
                    let fun77 = e.get("_read")?;
                    let mut args75 = Vec::new();
                    let mut kw76 = Vec::new();
                    args75.push(Val::Str("bulkhead-bottom".into()));
                    kw76.push(("flange_footprint".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",
                            line!(),
                        );
                        {
                            let fun80 = e
                                .get("FAMILIES")?
                                .get(e.get("fam")?)?
                                .attr("flange_footprint")?;
                            let mut args78 = Vec::new();
                            let mut kw79 = Vec::new();
                            fun80.call(args78, kw79)?
                        }
                    }));
                    fun77.call(args75, kw76)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // rise
    e.set("rise", {
        let params = vec![("which".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",
                    line!(),
                );
                {
                    let fun83 = e.get("_read")?;
                    let mut args81 = Vec::new();
                    let mut kw82 = Vec::new();
                    args81.push(Val::Str("bulkhead-rise".into()));
                    kw82.push(("bulkhead".into(), e.get("_values")?));
                    kw82.push(("which".into(), e.get("which")?));
                    kw82.push((
                        "co2_axis_drop".into(),
                        e.get("_enc_interface")?.attr("co2_axis_drop")?,
                    ));
                    fun83.call(args81, kw82)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // split
    e.set("split",{let params=vec![("shape".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned84=if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",line!());{let fun87=e.get("hasattr")?;let mut args85=Vec::new();let mut kw86=Vec::new();args85.push(e.get("shape")?);args85.push(Val::Str("Solids".into()));fun87.call(args85,kw86)?}}.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",line!());{let fun90=e.get("shape")?.attr("Solids")?;let mut args88=Vec::new();let mut kw89=Vec::new();fun90.call(args88,kw89)?}}} else {e.get("shape")?};e.set("solids",assigned84.clone())?;
let assigned91={let e=e.child();let out92=Val::list(vec![]);for item93 in e.get("solids")?.iter()? {e.set("s",item93)?;if {let v100={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",line!());{let fun96=e.get("abs")?;let mut args94=Vec::new();let mut kw95=Vec::new();args94.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",line!());{let fun99=e.get("s")?.attr("BoundingBox")?;let mut args97=Vec::new();let mut kw98=Vec::new();fun99.call(args97,kw98)?}}.attr("ymin")?);fun96.call(args94,kw95)?}};let v101=Val::Float(1e-06f64);Val::Bool(compare("lt",v100.clone(),v101.clone())?.truthy()?)}.truthy()? {out92.attr("append")?.call(vec![e.get("s")?],vec![])?;}}out92};e.set("floor",assigned91.clone())?;
if {let v107={let v111={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",line!());{let fun110=e.get("len")?;let mut args108=Vec::new();let mut kw109=Vec::new();args108.push(e.get("floor")?);fun110.call(args108,kw109)?}};let v112=Val::Int(1i64);Val::Bool(compare("ne",v111.clone(),v112.clone())?.truthy()?)};if v107.truthy()? {v107} else {{let v105={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",line!());{let fun104=e.get("len")?;let mut args102=Vec::new();let mut kw103=Vec::new();args102.push(e.get("solids")?);fun104.call(args102,kw103)?}};let v106=Val::Int(2i64);Val::Bool(compare("lt",v105.clone(),v106.clone())?.truthy()?)}}}.truthy()? {
anyhow::bail!("{}",val_string({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",line!());{let fun115=e.get("ValueError")?;let mut args113=Vec::new();let mut kw114=Vec::new();args113.push({let mut str116=String::new();str116.push_str("a label's STEP is a tile and the letters lying in it, and this one carries ");str116.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",line!());{let fun119=e.get("len")?;let mut args117=Vec::new();let mut kw118=Vec::new();args117.push(e.get("solids")?);fun119.call(args117,kw118)?}},&String::new())?);str116.push_str(" ");str116.push_str(&format(&if {let v123={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",line!());{let fun122=e.get("len")?;let mut args120=Vec::new();let mut kw121=Vec::new();args120.push(e.get("solids")?);fun122.call(args120,kw121)?}};let v124=Val::Int(1i64);Val::Bool(compare("eq",v123.clone(),v124.clone())?.truthy()?)}.truthy()? {Val::Str("body".into())} else {Val::Str("bodies".into())},&String::new())?);str116.push_str(", ");str116.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",line!());{let fun127=e.get("len")?;let mut args125=Vec::new();let mut kw126=Vec::new();args125.push(e.get("floor")?);fun127.call(args125,kw126)?}},&String::new())?);str116.push_str(" of them on the inboard face");Val::Str(str116)});fun115.call(args113,kw114)?}})?);
}
return Ok({let mut s=Vec::new();s.push(e.get("floor")?.get(Val::Int(0i64))?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/bulkhead_ring.rs",line!());{let fun130=e.get("cq")?.attr("Compound")?.attr("makeCompound")?;let mut args128=Vec::new();let mut kw129=Vec::new();args128.push({let e=e.child();let out131=Val::list(vec![]);for item132 in e.get("solids")?.iter()? {e.set("s",item132)?;if {let v133=e.get("s")?;let v134=e.get("floor")?.get(Val::Int(0i64))?;Val::Bool(compare("is_not",v133.clone(),v134.clone())?.truthy()?)}.truthy()? {out131.attr("append")?.call(vec![e.get("s")?],vec![])?;}}out131});fun130.call(args128,kw129)?}});Val::tuple(s)});
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
