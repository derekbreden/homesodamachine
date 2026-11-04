//! Read the enclosure README's dimensions from canonical appliance facts.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let assigned2 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",
            line!(),
        );
        {
            let fun5 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",
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
    }
    .attr("parent")?;
    e.set("HERE", assigned2.clone())?;
    let assigned9 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",
            line!(),
        );
        {
            let fun12 = e.get("next")?;
            let mut args10 = Vec::new();
            let mut kw11 = Vec::new();
            args10.push({
                let e = e.child();
                let out13 = Val::list(vec![]);
                for item14 in e.get("HERE")?.attr("parents")?.iter()? {
                    e.set("p", item14)?;
                    if {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",
                            line!(),
                        );
                        {
                            let fun17 = binary(
                                "truediv",
                                binary("truediv", e.get("p")?, Val::Str("hardware".into()))?,
                                Val::Str("scripts".into()),
                            )?
                            .attr("is_dir")?;
                            let mut args15 = Vec::new();
                            let mut kw16 = Vec::new();
                            fun17.call(args15, kw16)?
                        }
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
    e.set("ROOT", assigned9.clone())?;
    let assigned18 = binary("truediv", e.get("ROOT")?, Val::Str("hardware".into()))?;
    e.set("HW", assigned18.clone())?;
    for item19 in {
        let mut s = Vec::new();
        s.push(binary("truediv", e.get("ROOT")?, Val::Str("tools".into()))?);
        s.push(binary("truediv", e.get("HW")?, Val::Str("scripts".into()))?);
        s.push(binary(
            "truediv",
            e.get("HW")?,
            Val::Str("manifold-layout".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("HW")?, Val::Str("printed-parts".into()))?,
            Val::Str("cadlib".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("HW")?, Val::Str("printed-parts".into()))?,
            Val::Str("cold-core".into()),
        )?);
        s.push(binary(
            "truediv",
            e.get("HERE")?,
            Val::Str("enclosure".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("HW")?, Val::Str("reference".into()))?,
            Val::Str("condenser-block".into()),
        )?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("path", item19)?;
        {
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",
                line!(),
            );
            {
                let fun22 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args20 = Vec::new();
                let mut kw21 = Vec::new();
                args20.push(Val::Int(0i64));
                args20.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",
                        line!(),
                    );
                    {
                        let fun25 = e.get("str")?;
                        let mut args23 = Vec::new();
                        let mut kw24 = Vec::new();
                        args23.push(e.get("path")?);
                        fun25.call(args23, kw24)?
                    }
                });
                fun22.call(args20, kw21)?
            }
        };
    }
    e.set("_facts", rt.import_module("_facts")?)?;
    let mod26 = rt.import_module("_enclosure_datums")?;
    e.set(
        "_enclosure_numbers",
        rt.member("_enclosure_datums", "load")?,
    )?;
    let assigned27 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",
            line!(),
        );
        {
            let fun30 = e.get("_enclosure_numbers")?;
            let mut args28 = Vec::new();
            let mut kw29 = Vec::new();
            fun30.call(args28, kw29)?
        }
    };
    e.set("enclosure", assigned27.clone())?;
    let mod31 = rt.import_module("_cadq_export")?;
    e.set("note_read", rt.member("_cadq_export", "note_read")?)?;
    let assigned32 = binary(
        "truediv",
        e.get("HW")?,
        Val::Str("reference/condenser-block/condenser_block.py".into()),
    )?;
    e.set("_condenser_source", assigned32.clone())?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",
            line!(),
        );
        {
            let fun35 = e.get("note_read")?;
            let mut args33 = Vec::new();
            let mut kw34 = Vec::new();
            args33.push(e.get("_condenser_source")?);
            fun35.call(args33, kw34)?
        }
    };
    e.set("_condenser", rt.import_module("condenser_block")?)?;
    let assigned36 = {
        let e = e.child();
        let out37 = Val::dict(vec![]);
        for item38 in {
            let mut s = Vec::new();
            s.push(Val::Str("AIRFLOW".into()));
            s.push(Val::Str("FACE_A".into()));
            s.push(Val::Str("FACE_B".into()));
            Val::tuple(s)
        }
        .iter()?
        {
            e.set("name", item38)?;
            out37.set(e.get("name")?, {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",
                    line!(),
                );
                {
                    let fun41 = e.get("getattr")?;
                    let mut args39 = Vec::new();
                    let mut kw40 = Vec::new();
                    args39.push(e.get("_condenser")?);
                    args39.push(e.get("name")?);
                    fun41.call(args39, kw40)?
                }
            })?;
        }
        out37
    };
    e.set("condenser", assigned36.clone())?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",
            line!(),
        );
        {
            let fun44 = e.get("note_read")?;
            let mut args42 = Vec::new();
            let mut kw43 = Vec::new();
            args42.push(binary(
                "truediv",
                e.get("HW")?,
                Val::Str("manifold-layout/enclosure_assembly.py".into()),
            )?);
            fun44.call(args42, kw43)?
        }
    };
    for item45 in {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",
            line!(),
        );
        {
            let fun48 = e.get("_facts")?.attr("sources")?;
            let mut args46 = Vec::new();
            let mut kw47 = Vec::new();
            fun48.call(args46, kw47)?
        }
    }
    .iter()?
    {
        e.set("source", item45)?;
        if {
            let v52 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",
                    line!(),
                );
                {
                    let fun51 = e.get("Path")?;
                    let mut args49 = Vec::new();
                    let mut kw50 = Vec::new();
                    args49.push(e.get("source")?);
                    fun51.call(args49, kw50)?
                }
            }
            .attr("suffix")?;
            let v53 = {
                let mut s = Vec::new();
                s.push(Val::Str(".py".into()));
                s.push(Val::Str(".rs".into()));
                s.push(Val::Str(".json".into()));
                s.push(Val::Str(".toml".into()));
                s.push(Val::Str(".lock".into()));
                s.push(Val::Str(".yaml".into()));
                s.push(Val::Str(".yml".into()));
                Val::tuple(s)
            };
            Val::Bool(compare("in", v52.clone(), v53.clone())?.truthy()?)
        }
        .truthy()?
        {
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",
                    line!(),
                );
                {
                    let fun56 = e.get("note_read")?;
                    let mut args54 = Vec::new();
                    let mut kw55 = Vec::new();
                    args54.push(binary("truediv", e.get("ROOT")?, e.get("source")?)?);
                    fun56.call(args54, kw55)?
                }
            };
        }
    }
    let mod57 = rt.import_module("_cold_core_interface")?;
    e.set(
        "foam_shell_outer_height",
        rt.member("_cold_core_interface", "foam_shell_outer_height")?,
    )?;
    e.set(
        "outer_shell_x_length",
        rt.member("_cold_core_interface", "outer_shell_x_length")?,
    )?;
    e.set(
        "outer_shell_y_length",
        rt.member("_cold_core_interface", "outer_shell_y_length")?,
    )?;
    let mod58 = rt.import_module("docgen")?;
    e.set("substitute_md", rt.member("docgen", "substitute_md")?)?;
    let assigned59 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",
            line!(),
        );
        {
            let fun62 = e.get("_facts")?.attr("read")?;
            let mut args60 = Vec::new();
            let mut kw61 = Vec::new();
            fun62.call(args60, kw61)?
        }
    };
    e.set("facts", assigned59.clone())?;
    let assigned63 = e.get("facts")?.attr("box")?;
    e.set("box", assigned63.clone())?;
    let assigned64 = e.get("box")?.get(Val::Str("outer".into()))?;
    e.set("outer", assigned64.clone())?;
    let assigned65 = {
        let mut s = Vec::new();
        s.push({
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",
                line!(),
            );
            {
                let fun68 = e.get("facts")?.attr("bb")?;
                let mut args66 = Vec::new();
                let mut kw67 = Vec::new();
                args66.push(Val::Str("compressor".into()));
                fun68.call(args66, kw67)?
            }
        });
        s.push({
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",
                line!(),
            );
            {
                let fun71 = e.get("facts")?.attr("bb")?;
                let mut args69 = Vec::new();
                let mut kw70 = Vec::new();
                args69.push(Val::Str("condenser+fan".into()));
                fun71.call(args69, kw70)?
            }
        });
        Val::tuple(s)
    };
    let unpack72 = unpack(assigned65.clone(), 2)?;
    e.set("compressor", unpack72[0].clone())?;
    e.set("block", unpack72[1].clone())?;
    let assigned73 = binary(
        "sub",
        e.get("outer")?.get(Val::Int(1i64))?,
        e.get("outer")?.get(Val::Int(0i64))?,
    )?;
    e.set("APPLIANCE_W", assigned73.clone())?;
    let assigned74 = binary(
        "sub",
        e.get("outer")?.get(Val::Int(3i64))?,
        e.get("outer")?.get(Val::Int(2i64))?,
    )?;
    e.set("APPLIANCE_D", assigned74.clone())?;
    let assigned75 = binary(
        "sub",
        e.get("outer")?.get(Val::Int(5i64))?,
        e.get("outer")?.get(Val::Int(4i64))?,
    )?;
    e.set("APPLIANCE_H", assigned75.clone())?;
    // main
    e.set("main",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned76={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",line!());{let fun79=e.get("min")?;let mut args77=Vec::new();let mut kw78=Vec::new();args77.push({let e=e.child();let out80=Val::list(vec![]);for item81 in e.get("box")?.get(Val::Str("core_stops".into()))?.iter()? {let unpack82=unpack(item81,3)?;e.set("_x",unpack82[0].clone())?;e.set("y",unpack82[1].clone())?;e.set("radius",unpack82[2].clone())?;out80.attr("append")?.call(vec![binary("sub",e.get("y")?,e.get("radius")?)?],vec![])?;}out80});fun79.call(args77,kw78)?}};e.set("core_front",assigned76.clone())?;
let assigned83={let d=Val::dict(vec![]);d.set(Val::Str("FOAM_SHELL_X".into()),{let mut str84=String::new();str84.push_str(&format(&e.get("outer_shell_x_length")?,&val_string({let mut str85=String::new();str85.push_str(".4g");Val::Str(str85)})?)?);Val::Str(str84)})?;d.set(Val::Str("FOAM_SHELL_Y".into()),{let mut str86=String::new();str86.push_str(&format(&e.get("outer_shell_y_length")?,&val_string({let mut str87=String::new();str87.push_str(".4g");Val::Str(str87)})?)?);Val::Str(str86)})?;d.set(Val::Str("FOAM_SHELL_Z".into()),{let mut str88=String::new();str88.push_str(&format(&e.get("foam_shell_outer_height")?,&val_string({let mut str89=String::new();str89.push_str(".4g");Val::Str(str89)})?)?);Val::Str(str88)})?;d.set(Val::Str("APPLIANCE_WIDTH".into()),{let mut str90=String::new();str90.push_str(&format(&e.get("APPLIANCE_W")?,&val_string({let mut str91=String::new();str91.push_str(".4g");Val::Str(str91)})?)?);str90.push_str(" mm");Val::Str(str90)})?;d.set(Val::Str("APPLIANCE_DEPTH".into()),{let mut str92=String::new();str92.push_str(&format(&e.get("APPLIANCE_D")?,&val_string({let mut str93=String::new();str93.push_str(".4g");Val::Str(str93)})?)?);str92.push_str(" mm");Val::Str(str92)})?;d.set(Val::Str("APPLIANCE_HEIGHT".into()),{let mut str94=String::new();str94.push_str(&format(&e.get("APPLIANCE_H")?,&val_string({let mut str95=String::new();str95.push_str(".4g");Val::Str(str95)})?)?);str94.push_str(" mm");Val::Str(str94)})?;d.set(Val::Str("WALL_STANDOFF".into()),{let mut str96=String::new();str96.push_str(&format(&e.get("enclosure")?.attr("side_band_inset")?,&val_string({let mut str97=String::new();str97.push_str(".4g");Val::Str(str97)})?)?);Val::Str(str96)})?;d.set(Val::Str("COMP_BAY_W".into()),{let mut str98=String::new();str98.push_str(&format(&binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",line!());{let fun101=e.get("max")?;let mut args99=Vec::new();let mut kw100=Vec::new();args99.push(e.get("compressor")?.attr("xmax")?);args99.push(e.get("block")?.attr("xmax")?);fun101.call(args99,kw100)?}},{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",line!());{let fun104=e.get("min")?;let mut args102=Vec::new();let mut kw103=Vec::new();args102.push(e.get("compressor")?.attr("xmin")?);args102.push(e.get("block")?.attr("xmin")?);fun104.call(args102,kw103)?}})?,&val_string({let mut str105=String::new();str105.push_str(".4g");Val::Str(str105)})?)?);Val::Str(str98)})?;d.set(Val::Str("COMP_BAY_D".into()),{let mut str106=String::new();str106.push_str(&format(&binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",line!());{let fun109=e.get("max")?;let mut args107=Vec::new();let mut kw108=Vec::new();args107.push(e.get("compressor")?.attr("ymax")?);args107.push(e.get("block")?.attr("ymax")?);fun109.call(args107,kw108)?}},{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",line!());{let fun112=e.get("min")?;let mut args110=Vec::new();let mut kw111=Vec::new();args110.push(e.get("compressor")?.attr("ymin")?);args110.push(e.get("block")?.attr("ymin")?);fun112.call(args110,kw111)?}})?,&val_string({let mut str113=String::new();str113.push_str(".4g");Val::Str(str113)})?)?);Val::Str(str106)})?;d.set(Val::Str("COMP_BAY_TOP".into()),{let mut str114=String::new();str114.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",line!());{let fun117=e.get("max")?;let mut args115=Vec::new();let mut kw116=Vec::new();args115.push(e.get("compressor")?.attr("zmax")?);args115.push(e.get("block")?.attr("zmax")?);fun117.call(args115,kw116)?}},&val_string({let mut str118=String::new();str118.push_str(".4g");Val::Str(str118)})?)?);Val::Str(str114)})?;d.set(Val::Str("COMP_BAY_STEP".into()),{let mut str119=String::new();str119.push_str(&format(&{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",line!());{let fun122=e.get("abs")?;let mut args120=Vec::new();let mut kw121=Vec::new();args120.push(binary("sub",e.get("compressor")?.attr("zmax")?,e.get("block")?.attr("zmax")?)?);fun122.call(args120,kw121)?}},&val_string({let mut str123=String::new();str123.push_str(".4g");Val::Str(str123)})?)?);Val::Str(str119)})?;d.set(Val::Str("COMPRESSOR_ROOF".into()),{let mut str124=String::new();str124.push_str(&format(&e.get("compressor")?.attr("zmax")?,&val_string({let mut str125=String::new();str125.push_str(".4g");Val::Str(str125)})?)?);Val::Str(str124)})?;d.set(Val::Str("MATE_X".into()),{let mut str126=String::new();str126.push_str(&format(&e.get("compressor")?.attr("xmax")?,&val_string({let mut str127=String::new();str127.push_str(".4g");Val::Str(str127)})?)?);Val::Str(str126)})?;d.set(Val::Str("CONDENSER_ACROSS".into()),{let mut str128=String::new();str128.push_str(&format(&e.get("condenser")?.get(Val::Str("AIRFLOW".into()))?,&val_string({let mut str129=String::new();str129.push_str(".4g");Val::Str(str129)})?)?);Val::Str(str128)})?;d.set(Val::Str("CONDENSER_LONG".into()),{let mut str130=String::new();str130.push_str(&format(&e.get("condenser")?.get(Val::Str("FACE_A".into()))?,&val_string({let mut str131=String::new();str131.push_str(".4g");Val::Str(str131)})?)?);Val::Str(str130)})?;d.set(Val::Str("CONDENSER_STANDING".into()),{let mut str132=String::new();str132.push_str(&format(&e.get("condenser")?.get(Val::Str("FACE_B".into()))?,&val_string({let mut str133=String::new();str133.push_str(".4g");Val::Str(str133)})?)?);Val::Str(str132)})?;d.set(Val::Str("CONDENSER_LIFT".into()),{let mut str134=String::new();str134.push_str(&format(&e.get("block")?.attr("zmin")?,&val_string({let mut str135=String::new();str135.push_str(".4g");Val::Str(str135)})?)?);Val::Str(str134)})?;d.set(Val::Str("CORE_FRONT_Y".into()),{let mut str136=String::new();str136.push_str(&format(&e.get("core_front")?,&val_string({let mut str137=String::new();str137.push_str(".4g");Val::Str(str137)})?)?);Val::Str(str136)})?;d.set(Val::Str("CORE_CROWN".into()),{let mut str138=String::new();str138.push_str(&format(&e.get("facts")?.attr("faces")?.get(Val::Str("foam-assembly.cap".into()))?,&val_string({let mut str139=String::new();str139.push_str(".4g");Val::Str(str139)})?)?);Val::Str(str138)})?;d.set(Val::Str("BACK_Z_SEAM".into()),{let mut str140=String::new();str140.push_str(&format(&e.get("box")?.get(Val::Str("splits".into()))?.get(Val::Int(1i64))?,&val_string({let mut str141=String::new();str141.push_str(".4g");Val::Str(str141)})?)?);Val::Str(str140)})?;d.set(Val::Str("BACK_BOTTOM_H".into()),{let mut str142=String::new();str142.push_str(&format(&binary("sub",e.get("facts")?.attr("pieces")?.get(Val::Str("back-bottom".into()))?.get(Val::Str("box".into()))?.get(Val::Int(5i64))?,e.get("facts")?.attr("pieces")?.get(Val::Str("back-bottom".into()))?.get(Val::Str("box".into()))?.get(Val::Int(2i64))?)?,&val_string({let mut str143=String::new();str143.push_str(".4g");Val::Str(str143)})?)?);Val::Str(str142)})?;d.set(Val::Str("BED_Z".into()),{let mut str144=String::new();str144.push_str(&format(&e.get("enclosure")?.attr("H2C_Z")?,&val_string({let mut str145=String::new();str145.push_str(".4g");Val::Str(str145)})?)?);Val::Str(str144)})?;d};e.set("variables",assigned83.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",line!());{let fun148=e.get("substitute_md")?;let mut args146=Vec::new();let mut kw147=Vec::new();args146.push(binary("truediv",e.get("HERE")?,Val::Str("README.md".into()))?);kw147.push(("variables".into(),e.get("variables")?));fun148.call(args146,kw147)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",line!());{let fun151=e.get("print")?;let mut args149=Vec::new();let mut kw150=Vec::new();args149.push(Val::Str("-> README.md".into()));fun151.call(args149,kw150)?}};
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_enclosure_dimensions.rs",
            line!(),
        );
        {
            let fun154 = e.get("main")?;
            let mut args152 = Vec::new();
            let mut kw153 = Vec::new();
            fun154.call(args152, kw153)?
        }
    };
    Ok(Val::None)
}
