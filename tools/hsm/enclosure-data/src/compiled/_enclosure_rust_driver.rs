//! Normal enclosure construction from scalar recipes and ordered fine-model references.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("contextlib")?;
    e.set("contextmanager", rt.member("contextlib", "contextmanager")?)?;
    e.set("json", rt.import_module("json")?)?;
    let mod2 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let assigned3 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",
            line!(),
        );
        {
            let fun6 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",
                    line!(),
                );
                {
                    let fun9 = e.get("Path")?;
                    let mut args7 = Vec::new();
                    let mut kw8 = Vec::new();
                    args7.push(e.get("__file__")?);
                    fun9.call(args7, kw8)?
                }
            }
            .attr("resolve")?;
            let mut args4 = Vec::new();
            let mut kw5 = Vec::new();
            fun6.call(args4, kw5)?
        }
    }
    .attr("parent")?;
    e.set("HERE", assigned3.clone())?;
    let assigned10 = e.get("HERE")?.attr("parents")?.get(Val::Int(3i64))?;
    e.set("ROOT", assigned10.clone())?;
    // load
    e.set("load", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod11 = rt.import_module("_enclosure_datums")?;
            e.set("scalar_source", rt.member("_enclosure_datums", "load")?)?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",
                    line!(),
                );
                {
                    let fun14 = e.get("scalar_source")?;
                    let mut args12 = Vec::new();
                    let mut kw13 = Vec::new();
                    fun14.call(args12, kw13)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // box_from_document
    e.set("box_from_document",{let params=vec![("document".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned15={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun18=e.get("load")?;let mut args16=Vec::new();let mut kw17=Vec::new();fun18.call(args16,kw17)?}};e.set("shell",assigned15.clone())?;
e.set("_box_spec",rt.import_module("_box_spec")?)?;
let assigned19={let e=e.child();let out20=Val::dict(vec![]);for item21 in {let mut s=Vec::new();s.push(e.get("shell")?.attr("Pack")?);s.push(e.get("shell")?.attr("PortField")?);s.push(e.get("shell")?.attr("Nameplate")?);Val::tuple(s)}.iter()? {e.set("kind",item21)?;out20.set(e.get("kind")?.attr("__name__")?,e.get("kind")?)?;}out20};e.set("types",assigned19.clone())?;
let assigned22={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun25=e.get("shell")?.attr("Box")?;let mut args23=Vec::new();let mut kw24=Vec::new();args23.extend({let e=e.child();let out26=Val::list(vec![]);for item27 in e.get("shell")?.attr("Box")?.attr("_fields")?.iter()? {e.set("name",item27)?;out26.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun30=e.get("_box_spec")?.attr("_tupled")?;let mut args28=Vec::new();let mut kw29=Vec::new();args28.push(e.get("document")?.get(Val::Str("box".into()))?.get(e.get("name")?)?);args28.push(e.get("types")?);fun30.call(args28,kw29)?}}],vec![])?;}out26}.iter()?);fun25.call(args23,kw24)?}};e.set("box",assigned22.clone())?;
let assigned31={let e=e.child();let out32=Val::list(vec![]);for item33 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun36=e.get("document")?.attr("get")?;let mut args34=Vec::new();let mut kw35=Vec::new();args34.push(Val::Str("bounds".into()));args34.push({let mut s=Vec::new();Val::tuple(s)});fun36.call(args34,kw35)?}}.iter()? {e.set("row",item33)?;out32.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun39=e.get("shell")?.attr("Bound")?;let mut args37=Vec::new();let mut kw38=Vec::new();args37.extend({let e=e.child();let out40=Val::list(vec![]);for item41 in e.get("shell")?.attr("Bound")?.attr("_fields")?.iter()? {e.set("name",item41)?;out40.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun44=e.get("_box_spec")?.attr("_tupled")?;let mut args42=Vec::new();let mut kw43=Vec::new();args42.push(e.get("row")?.get(e.get("name")?)?);args42.push(e.get("types")?);fun44.call(args42,kw43)?}}],vec![])?;}out40}.iter()?);fun39.call(args37,kw38)?}}],vec![])?;}out32};e.set("bounds",assigned31.clone())?;
return Ok({let mut s=Vec::new();s.push(e.get("shell")?);s.push(e.get("box")?);s.push(e.get("bounds")?);Val::tuple(s)});
Ok(Val::None)})})?;
    // _model_instance
    e.set("_model_instance",{let params=vec![("model".into(),None,false),("name".into(),Some(Val::None),false),("transform".into(),Some(Val::None),true),("indices".into(),Some(Val::None),true),("color".into(),Some(Val::None),true),("split_components".into(),Some(Val::Bool(false)),true)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned45={let d=Val::dict(vec![]);d.set(Val::Str("model".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun48=e.get("str")?;let mut args46=Vec::new();let mut kw47=Vec::new();args46.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun51={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun54=e.get("Path")?;let mut args52=Vec::new();let mut kw53=Vec::new();args52.push(e.get("model")?);fun54.call(args52,kw53)?}}.attr("resolve")?;let mut args49=Vec::new();let mut kw50=Vec::new();fun51.call(args49,kw50)?}});fun48.call(args46,kw47)?}})?;d};e.set("row",assigned45.clone())?;
if {let v55=e.get("name")?;let v56=Val::None;Val::Bool(compare("is_not",v55.clone(),v56.clone())?.truthy()?)}.truthy()? {
let assigned57=e.get("name")?;e.get("row")?.set(Val::Str("name".into()),assigned57.clone())?;
}
if {let v58=e.get("transform")?;let v59=Val::None;Val::Bool(compare("is_not",v58.clone(),v59.clone())?.truthy()?)}.truthy()? {
let assigned60=e.get("transform")?;e.get("row")?.set(Val::Str("transform".into()),assigned60.clone())?;
}
if {let v61=e.get("indices")?;let v62=Val::None;Val::Bool(compare("is_not",v61.clone(),v62.clone())?.truthy()?)}.truthy()? {
let assigned63=e.get("indices")?;e.get("row")?.set(Val::Str("indices".into()),assigned63.clone())?;
}
if {let v64=e.get("color")?;let v65=Val::None;Val::Bool(compare("is_not",v64.clone(),v65.clone())?.truthy()?)}.truthy()? {
let assigned66={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun69=e.get("list")?;let mut args67=Vec::new();let mut kw68=Vec::new();args67.push(e.get("color")?);fun69.call(args67,kw68)?}};e.get("row")?.set(Val::Str("color".into()),assigned66.clone())?;
}
if e.get("split_components")?.truthy()? {
let assigned70=Val::Bool(true);e.get("row")?.set(Val::Str("split_components".into()),assigned70.clone())?;
}
return Ok(e.get("row")?);
Ok(Val::None)})})?;
    // _translation
    e.set("_translation", {
        let params = vec![("point".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned71 = e.get("point")?;
            let unpack72 = unpack(assigned71.clone(), 3)?;
            e.set("x", unpack72[0].clone())?;
            e.set("y", unpack72[1].clone())?;
            e.set("z", unpack72[2].clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(e.get("x")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(e.get("y")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(1.0f64));
                    s.push(e.get("z")?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // cut_pieces
    e.set("cut_pieces", {
        let params = vec![
            ("shell".into(), None, false),
            ("box".into(), None, false),
            ("directory".into(), Some(e.get("HERE")?), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_enclosure_panel", rt.import_module("_enclosure_panel")?)?;
            e.set(
                "_enclosure_back_top",
                rt.import_module("_enclosure_back_top")?,
            )?;
            e.set(
                "_enclosure_front_top",
                rt.import_module("_enclosure_front_top")?,
            )?;
            e.set(
                "_enclosure_front_bottom",
                rt.import_module("_enclosure_front_bottom")?,
            )?;
            e.set(
                "_enclosure_pump_retainer",
                rt.import_module("_enclosure_pump_retainer")?,
            )?;
            let assigned73 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",
                    line!(),
                );
                {
                    let fun76 = e.get("Path")?;
                    let mut args74 = Vec::new();
                    let mut kw75 = Vec::new();
                    args74.push(e.get("directory")?);
                    fun76.call(args74, kw75)?
                }
            };
            e.set("directory", assigned73.clone())?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",
                    line!(),
                );
                {
                    let fun79 = e.get("directory")?.attr("mkdir")?;
                    let mut args77 = Vec::new();
                    let mut kw78 = Vec::new();
                    kw78.push(("parents".into(), Val::Bool(true)));
                    kw78.push(("exist_ok".into(), Val::Bool(true)));
                    fun79.call(args77, kw78)?
                }
            };
            for item80 in {
                let mut s = Vec::new();
                s.push(e.get("_enclosure_panel")?);
                s.push(e.get("_enclosure_back_top")?);
                s.push(e.get("_enclosure_front_top")?);
                s.push(e.get("_enclosure_front_bottom")?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("module", item80)?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",
                        line!(),
                    );
                    {
                        let fun83 = e.get("module")?.attr("cut")?;
                        let mut args81 = Vec::new();
                        let mut kw82 = Vec::new();
                        args81.push(e.get("shell")?);
                        args81.push(e.get("box")?);
                        args81.push(e.get("directory")?);
                        fun83.call(args81, kw82)?
                    }
                };
            }
            let assigned84 = {
                let e = e.child();
                let out85 = Val::list(vec![]);
                for item86 in e.get("shell")?.attr("PIECE_COLORS")?.iter()? {
                    e.set("name", item86)?;
                    if {
                        let v87 = e.get("name")?;
                        let v88 = Val::Str("pump-retainer".into());
                        Val::Bool(compare("ne", v87.clone(), v88.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        out85.attr("append")?.call(vec![e.get("name")?], vec![])?;
                    }
                }
                out85
            };
            e.set("names", assigned84.clone())?;
            let assigned89 = Val::None;
            e.set("installed", assigned89.clone())?;
            if {
                let v90 = e.get("box")?.attr("pump_bay")?;
                if v90.truthy()? {
                    e.get("box")?.attr("pack")?.attr("collet_plate")?
                } else {
                    v90
                }
            }
            .truthy()?
            {
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",
                        line!(),
                    );
                    {
                        let fun93 = e.get("_enclosure_pump_retainer")?.attr("cut")?;
                        let mut args91 = Vec::new();
                        let mut kw92 = Vec::new();
                        args91.push(e.get("shell")?);
                        args91.push(e.get("box")?);
                        args91.push(e.get("directory")?);
                        fun93.call(args91, kw92)?
                    }
                };
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",
                        line!(),
                    );
                    {
                        let fun96 = e.get("_enclosure_pump_retainer")?.attr("cut")?;
                        let mut args94 = Vec::new();
                        let mut kw95 = Vec::new();
                        args94.push(e.get("shell")?);
                        args94.push(e.get("box")?);
                        args94.push(e.get("directory")?);
                        kw95.push(("seated".into(), Val::Bool(true)));
                        fun96.call(args94, kw95)?
                    }
                };
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",
                        line!(),
                    );
                    {
                        let fun99 = e.get("names")?.attr("append")?;
                        let mut args97 = Vec::new();
                        let mut kw98 = Vec::new();
                        args97.push(Val::Str("pump-retainer".into()));
                        fun99.call(args97, kw98)?
                    }
                };
                let assigned100 = binary(
                    "truediv",
                    e.get("directory")?,
                    Val::Str("enclosure-pump-retainer-seated.step.npz".into()),
                )?;
                e.set("installed", assigned100.clone())?;
            }
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let e = e.child();
                    let out101 = Val::dict(vec![]);
                    for item102 in e.get("names")?.iter()? {
                        e.set("name", item102)?;
                        out101.set(
                            e.get("name")?,
                            binary("truediv", e.get("directory")?, {
                                let mut str103 = String::new();
                                str103.push_str("enclosure-");
                                str103.push_str(&format(&e.get("name")?, &String::new())?);
                                str103.push_str(".step.npz");
                                Val::Str(str103)
                            })?,
                        )?;
                    }
                    out101
                });
                s.push(e.get("installed")?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    e.set("_dock_recipe", {
        let params = vec![("shell".into(), None, false), ("graph".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let enter_e = e.clone();
            let enter_rt = rt.clone();
            let enter = Val::function(move |_, _| {
                let e = enter_e.clone();
                let rt = enter_rt.clone();
                let _frame = rt.frame(&e);
                let assigned104 = e.get("shell")?.attr("_dock")?;
                e.set("dock", assigned104.clone())?;
                let assigned105 = {
                    let mut s = Vec::new();
                    s.push(e.get("dock")?.attr("box")?);
                    s.push(e.get("dock")?.attr("ycyl")?);
                    Val::tuple(s)
                };
                e.set("originals", assigned105.clone())?;
                let assigned106 = e.get("graph")?.attr("box")?;
                e.get("dock")?.setattr("box", assigned106.clone())?;
                let assigned107 = {
                    let params = vec![
                        ("r".into(), None, false),
                        ("x".into(), None, false),
                        ("z".into(), None, false),
                        ("y0".into(), None, false),
                        ("y1".into(), None, false),
                    ];
                    let outer = e.clone();
                    let runtime = rt.clone();
                    Val::function(move |args, kwargs| {
                        let rt = runtime.clone();
                        let e = bind(&outer, &params, args, kwargs, None, None)?;
                        let _frame = rt.frame(&outer);
                        return Ok({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",
                                line!(),
                            );
                            {
                                let fun110 = e.get("graph")?.attr("cylinder")?;
                                let mut args108 = Vec::new();
                                let mut kw109 = Vec::new();
                                args108.push(Val::Int(1i64));
                                args108.push(e.get("r")?);
                                args108.push(e.get("x")?);
                                args108.push(e.get("z")?);
                                args108.push(e.get("y0")?);
                                args108.push(e.get("y1")?);
                                fun110.call(args108, kw109)?
                            }
                        });
                        Ok(Val::None)
                    })
                };
                e.get("dock")?.setattr("ycyl", assigned107.clone())?;
                Ok(Val::None)
            });
            let exit_e = e.clone();
            let exit_rt = rt.clone();
            let exit = Val::function(move |_, _| {
                let e = exit_e.clone();
                let rt = exit_rt.clone();
                let _frame = rt.frame(&e);
                let assigned111 = e.get("originals")?;
                let unpack112 = unpack(assigned111.clone(), 2)?;
                e.get("dock")?.setattr("box", unpack112[0].clone())?;
                e.get("dock")?.setattr("ycyl", unpack112[1].clone())?;
                Ok(Val::None)
            });
            Ok(context(enter, exit))
        })
    })?; // cut_tube_setting_jig
    e.set("cut_tube_setting_jig",{let params=vec![("shell".into(),None,false),("box".into(),None,false),("directory".into(),Some(e.get("HERE")?),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("_rust_part",rt.import_module("_rust_part")?)?;
let mod113=rt.import_module("_materials")?;e.set("linear",rt.member("_materials","linear")?)?;e.set("M_PETGF_BLACK",rt.member("_materials","M_PETGF_BLACK")?)?;
let mod114=rt.import_module("_enclosure_panel")?;e.set("_Graph",rt.member("_enclosure_panel","_Graph")?)?;
let mod115=rt.import_module("_enclosure_presentation")?;e.set("print_payload",rt.member("_enclosure_presentation","print_payload")?)?;
let assigned116={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun119=e.get("_Graph")?;let mut args117=Vec::new();let mut kw118=Vec::new();fun119.call(args117,kw118)?}};e.set("graph",assigned116.clone())?;
let context120={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun123=e.get("_dock_recipe")?;let mut args121=Vec::new();let mut kw122=Vec::new();args121.push(e.get("shell")?);args121.push(e.get("graph")?);fun123.call(args121,kw122)?}};context120.attr("__enter__")?.call(vec![],vec![])?;let context_result131=(||->Result<Flow>{let assigned124={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun127=e.get("shell")?.attr("_dock")?.attr("tube_setting_jig")?;let mut args125=Vec::new();let mut kw126=Vec::new();args125.push(e.get("box")?.attr("pack")?.attr("collet_plate")?);args125.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun130=e.get("shell")?.attr("pump_cartridge_aft_y")?;let mut args128=Vec::new();let mut kw129=Vec::new();args128.push(e.get("box")?.attr("pack")?.attr("pump_trays")?);args128.push(e.get("box")?.attr("pack")?.attr("collet_plate")?);fun130.call(args128,kw129)?}});fun127.call(args125,kw126)?}};e.set("solid",assigned124.clone())?;
Ok(Flow::Continue)})();context120.attr("__exit__")?.call(vec![Val::None,Val::None,Val::None],vec![])?;match context_result131? {Flow::Continue=>{},Flow::Return(value)=>return Ok(value)}
let assigned132={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun135=e.get("Path")?;let mut args133=Vec::new();let mut kw134=Vec::new();args133.push(e.get("directory")?);fun135.call(args133,kw134)?}};e.set("directory",assigned132.clone())?;
let assigned136={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun139=e.get("dict")?;let mut args137=Vec::new();let mut kw138=Vec::new();kw138.push(("panel".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun142=e.get("graph")?.attr("document")?;let mut args140=Vec::new();let mut kw141=Vec::new();args140.push(e.get("solid")?);fun142.call(args140,kw141)?}}));kw138.push(("color".into(),{let e=e.child();let out143=Val::list(vec![]);for item144 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun147=e.get("linear")?;let mut args145=Vec::new();let mut kw146=Vec::new();args145.push(e.get("M_PETGF_BLACK")?);fun147.call(args145,kw146)?}}.iter()? {e.set("c",item144)?;out143.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun150=e.get("round")?;let mut args148=Vec::new();let mut kw149=Vec::new();args148.push(e.get("c")?);args148.push(Val::Int(9i64));fun150.call(args148,kw149)?}}],vec![])?;}out143}));fun139.call(args137,kw138)?}};e.set("numbers",assigned136.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun153=e.get("_rust_part")?.attr("cut")?;let mut args151=Vec::new();let mut kw152=Vec::new();args151.push(Val::Str("enclosure-shell".into()));args151.push(Val::Str("enclosure-dock".into()));args151.push(e.get("numbers")?);args151.push(e.get("directory")?);fun153.call(args151,kw152)?}};
let assigned154=binary("truediv",e.get("directory")?,Val::Str("enclosure-pump-tube-setting-jig.step".into()))?;e.set("step",assigned154.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun157=e.get("print_payload")?;let mut args155=Vec::new();let mut kw156=Vec::new();args155.push(e.get("step")?);kw156.push(("check_print".into(),Val::Bool(false)));fun157.call(args155,kw156)?}};
Ok(Val::None)})})?;
    // installed_instances
    e.set("installed_instances",{let params=vec![("box_document".into(),None,false),("directory".into(),Some(Val::None),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned158={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun161=e.get("box_from_document")?;let mut args159=Vec::new();let mut kw160=Vec::new();args159.push(e.get("box_document")?);fun161.call(args159,kw160)?}};let unpack162=unpack(assigned158.clone(),3)?;e.set("shell",unpack162[0].clone())?;e.set("box",unpack162[1].clone())?;e.set("_bounds",unpack162[2].clone())?;
e.set("_rust_part",rt.import_module("_rust_part")?)?;
let mod163=rt.import_module("_materials")?;e.set("linear",rt.member("_materials","linear")?)?;e.set("M_PETGF_BLACK",rt.member("_materials","M_PETGF_BLACK")?)?;
let assigned164=if {let v165=e.get("directory")?;let v166=Val::None;Val::Bool(compare("is_not",v165.clone(),v166.clone())?.truthy()?)}.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun169=e.get("Path")?;let mut args167=Vec::new();let mut kw168=Vec::new();args167.push(e.get("directory")?);fun169.call(args167,kw168)?}}} else {binary("truediv",e.get("HERE")?,Val::Str("installed".into()))?};e.set("directory",assigned164.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun172=e.get("directory")?.attr("mkdir")?;let mut args170=Vec::new();let mut kw171=Vec::new();kw171.push(("parents".into(),Val::Bool(true)));kw171.push(("exist_ok".into(),Val::Bool(true)));fun172.call(args170,kw171)?}};
let assigned173={let mut s=Vec::new();Val::list(s)};e.set("instances",assigned173.clone())?;
if {let v174=e.get("box")?.attr("pump_bay")?;if v174.truthy()? {e.get("box")?.attr("pack")?.attr("collet_plate")?} else {v174}}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun177=e.get("instances")?.attr("append")?;let mut args175=Vec::new();let mut kw176=Vec::new();args175.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun180=e.get("_model_instance")?;let mut args178=Vec::new();let mut kw179=Vec::new();args178.push(binary("truediv",e.get("HERE")?,Val::Str("enclosure-pump-retainer-seated.step.npz".into()))?);args178.push(Val::Str("enclosure-pump-retainer".into()));fun180.call(args178,kw179)?}});fun177.call(args175,kw176)?}};
}
let assigned181=e.get("shell")?.attr("_funnel_frame_part")?;e.set("frame",assigned181.clone())?;
let assigned182={let mut s=Vec::new();s.push(binary("truediv",binary("add",e.get("box")?.attr("inner")?.get(Val::Int(0i64))?,e.get("box")?.attr("inner")?.get(Val::Int(1i64))?)?,Val::Float(2.0f64))?);s.push(e.get("frame")?.attr("center_y")?);Val::tuple(s)};e.set("centre",assigned182.clone())?;
let assigned183={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun186=e.get("shell")?.attr("funnel_seat_z")?;let mut args184=Vec::new();let mut kw185=Vec::new();args184.push(e.get("box")?.attr("outer")?);fun186.call(args184,kw185)?}};e.set("seat",assigned183.clone())?;
let assigned187={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun190=e.get("frame")?.attr("datums")?;let mut args188=Vec::new();let mut kw189=Vec::new();args188.push(e.get("seat")?);fun190.call(args188,kw189)?}}.get(Val::Int(0i64))?;e.set("floor",assigned187.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun193=e.get("_rust_part")?.attr("cut")?;let mut args191=Vec::new();let mut kw192=Vec::new();args191.push(Val::Str("funnel".into()));args191.push(Val::Str("funnel-frame".into()));args191.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun196=e.get("frame")?.attr("numbers")?;let mut args194=Vec::new();let mut kw195=Vec::new();args194.push(e.get("box")?.attr("inner")?);args194.push(e.get("box")?.attr("y_joint")?);args194.push(e.get("centre")?);args194.push(e.get("seat")?);fun196.call(args194,kw195)?}});args191.push(e.get("directory")?);kw192.push(("numbers_name".into(),Val::Str("enclosure-funnel-frame".into())));fun193.call(args191,kw192)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun199=e.get("instances")?.attr("append")?;let mut args197=Vec::new();let mut kw198=Vec::new();args197.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun202=e.get("_model_instance")?;let mut args200=Vec::new();let mut kw201=Vec::new();args200.push(binary("truediv",e.get("directory")?,Val::Str("funnel-frame.step.npz".into()))?);args200.push(Val::Str("funnel-frame".into()));kw201.push(("transform".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun205=e.get("_translation")?;let mut args203=Vec::new();let mut kw204=Vec::new();args203.push({let mut s=Vec::new();s.extend(e.get("centre")?.iter()?);s.push(e.get("floor")?);Val::tuple(s)});fun205.call(args203,kw204)?}}));kw201.push(("color".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun208=e.get("linear")?;let mut args206=Vec::new();let mut kw207=Vec::new();args206.push(e.get("M_PETGF_BLACK")?);fun208.call(args206,kw207)?}}));fun202.call(args200,kw201)?}});fun199.call(args197,kw198)?}};
let assigned209={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun212=e.get("shell")?.attr("_above_core_shell")?.attr("rear_identification")?;let mut args210=Vec::new();let mut kw211=Vec::new();fun212.call(args210,kw211)?}};e.set("identification",assigned209.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun215=e.get("_rust_part")?.attr("cut")?;let mut args213=Vec::new();let mut kw214=Vec::new();args213.push(Val::Str("enclosure-components".into()));args213.push(Val::Str("rear-identification".into()));args213.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun218=e.get("identification")?.attr("numbers")?;let mut args216=Vec::new();let mut kw217=Vec::new();fun218.call(args216,kw217)?}});args213.push(e.get("directory")?);fun215.call(args213,kw214)?}};
for item219 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun222=e.get("identification")?.attr("stations")?;let mut args220=Vec::new();let mut kw221=Vec::new();fun222.call(args220,kw221)?}}.iter()? {
e.set("station",item219)?;let assigned223=e.get("station")?.get(Val::Str("which".into()))?;e.set("which",assigned223.clone())?;
let assigned224=binary("truediv",e.get("directory")?,{let mut str225=String::new();str225.push_str("rear-label-");str225.push_str(&format(&e.get("which")?,&String::new())?);str225.push_str(".step.npz");Val::Str(str225)})?;e.set("model",assigned224.clone())?;
let assigned226={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun229=e.get("_translation")?;let mut args227=Vec::new();let mut kw228=Vec::new();args227.push({let mut s=Vec::new();s.push(e.get("station")?.get(Val::Str("center_x_mm".into()))?);s.push(e.get("station")?.get(Val::Str("floor_y_mm".into()))?);s.push(e.get("station")?.get(Val::Str("center_z_mm".into()))?);Val::tuple(s)});fun229.call(args227,kw228)?}};e.set("transform",assigned226.clone())?;
for item230 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun233=e.get("enumerate")?;let mut args231=Vec::new();let mut kw232=Vec::new();args231.push({let mut s=Vec::new();s.push(Val::Str("".into()));s.push(Val::Str("-word".into()));Val::tuple(s)});fun233.call(args231,kw232)?}}.iter()? {
let unpack234=unpack(item230,2)?;e.set("index",unpack234[0].clone())?;e.set("suffix",unpack234[1].clone())?;{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun237=e.get("instances")?.attr("append")?;let mut args235=Vec::new();let mut kw236=Vec::new();args235.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun240=e.get("_model_instance")?;let mut args238=Vec::new();let mut kw239=Vec::new();args238.push(e.get("model")?);args238.push({let mut str241=String::new();str241.push_str("bulkhead-ring-");str241.push_str(&format(&e.get("which")?,&String::new())?);str241.push_str(&format(&e.get("suffix")?,&String::new())?);Val::Str(str241)});kw239.push(("indices".into(),{let mut s=Vec::new();s.push(e.get("index")?);Val::list(s)}));kw239.push(("transform".into(),e.get("transform")?));kw239.push(("split_components".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun244=e.get("bool")?;let mut args242=Vec::new();let mut kw243=Vec::new();args242.push(e.get("index")?);fun244.call(args242,kw243)?}}));fun240.call(args238,kw239)?}});fun237.call(args235,kw236)?}};
}
}
let assigned245=e.get("identification")?.attr("nameplate")?;e.set("plate",assigned245.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun248=e.get("_rust_part")?.attr("cut")?;let mut args246=Vec::new();let mut kw247=Vec::new();args246.push(Val::Str("enclosure-components".into()));args246.push(Val::Str("nameplate".into()));args246.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun251=e.get("plate")?.attr("numbers")?;let mut args249=Vec::new();let mut kw250=Vec::new();args249.push(Val::Int(1i64));fun251.call(args249,kw250)?}});args246.push(e.get("directory")?);kw247.push(("numbers_name".into(),Val::Str("enclosure-nameplate".into())));fun248.call(args246,kw247)?}};
let assigned252={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun255=e.get("identification")?.attr("nameplate_plan")?;let mut args253=Vec::new();let mut kw254=Vec::new();fun255.call(args253,kw254)?}};e.set("plan",assigned252.clone())?;
let assigned256={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun259=e.get("_translation")?;let mut args257=Vec::new();let mut kw258=Vec::new();args257.push({let mut s=Vec::new();s.push(e.get("plan")?.get(Val::Str("center_x_mm".into()))?);s.push(binary("sub",e.get("plan")?.get(Val::Str("face_y_mm".into()))?,e.get("plate")?.attr("THICK")?)?);s.push(e.get("plan")?.get(Val::Str("center_z_mm".into()))?);Val::tuple(s)});fun259.call(args257,kw258)?}};e.set("transform",assigned256.clone())?;
for item260 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun263=e.get("enumerate")?;let mut args261=Vec::new();let mut kw262=Vec::new();args261.push({let mut s=Vec::new();s.push(Val::Str("nameplate".into()));s.push(Val::Str("nameplate-ink".into()));Val::tuple(s)});fun263.call(args261,kw262)?}}.iter()? {
let unpack264=unpack(item260,2)?;e.set("index",unpack264[0].clone())?;e.set("name",unpack264[1].clone())?;let assigned265=if e.get("index")?.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun268=e.get("identification")?.attr("colours")?.attr("word_color")?;let mut args266=Vec::new();let mut kw267=Vec::new();args266.push(Val::Str("flavor".into()));fun268.call(args266,kw267)?}}} else {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun271=e.get("identification")?.attr("colours")?.attr("chip_color")?;let mut args269=Vec::new();let mut kw270=Vec::new();args269.push(Val::Str("flavor".into()));fun271.call(args269,kw270)?}}};e.set("colour",assigned265.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun274=e.get("instances")?.attr("append")?;let mut args272=Vec::new();let mut kw273=Vec::new();args272.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun277=e.get("_model_instance")?;let mut args275=Vec::new();let mut kw276=Vec::new();args275.push(binary("truediv",e.get("directory")?,Val::Str("nameplate-001.step.npz".into()))?);args275.push(e.get("name")?);kw276.push(("indices".into(),{let mut s=Vec::new();s.push(e.get("index")?);Val::list(s)}));kw276.push(("transform".into(),e.get("transform")?));kw276.push(("color".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun280=e.get("linear")?;let mut args278=Vec::new();let mut kw279=Vec::new();args278.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun283=e.get("identification")?.attr("_colour")?;let mut args281=Vec::new();let mut kw282=Vec::new();args281.push(e.get("colour")?);fun283.call(args281,kw282)?}});fun280.call(args278,kw279)?}}));kw276.push(("split_components".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun286=e.get("bool")?;let mut args284=Vec::new();let mut kw285=Vec::new();args284.push(e.get("index")?);fun286.call(args284,kw285)?}}));fun277.call(args275,kw276)?}});fun274.call(args272,kw273)?}};
}
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun289=e.get("dict")?;let mut args287=Vec::new();let mut kw288=Vec::new();kw288.push(("instances".into(),e.get("instances")?));kw288.push(("datums".into(),{let d=Val::dict(vec![]);d.set(Val::Str("funnel_frame_fasteners".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun292=e.get("frame")?.attr("fastener_datums")?;let mut args290=Vec::new();let mut kw291=Vec::new();args290.push(e.get("box")?.attr("inner")?);args290.push(e.get("box")?.attr("y_joint")?);args290.push(e.get("centre")?);args290.push(e.get("seat")?);fun292.call(args290,kw291)?}})?;d.set(Val::Str("funnel_centre".into()),e.get("centre")?)?;d.set(Val::Str("funnel_seat".into()),e.get("seat")?)?;d.set(Val::Str("funnel_frame_floor".into()),e.get("floor")?)?;d.set(Val::Str("y_stack_rods".into()),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun295=e.get("shell")?.attr("y_stack_rods")?;let mut args293=Vec::new();let mut kw294=Vec::new();args293.push(e.get("box")?.attr("inner")?);fun295.call(args293,kw294)?}})?;d}));fun289.call(args287,kw288)?}});
Ok(Val::None)})})?;
    // box_from_plan
    e.set("box_from_plan",{let params=vec![("plan".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned296={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun299=e.get("load")?;let mut args297=Vec::new();let mut kw298=Vec::new();fun299.call(args297,kw298)?}};e.set("shell",assigned296.clone())?;
e.set("_box_spec",rt.import_module("_box_spec")?)?;
let mod300=rt.import_module("_rust_enclosure_checks")?;e.set("box_readings",rt.member("_rust_enclosure_checks","box_readings")?)?;
let assigned301=e.get("plan")?.get(Val::Str("metadata".into()))?;e.set("metadata",assigned301.clone())?;
let assigned302=e.get("metadata")?.get(Val::Str("pack".into()))?;e.set("raw",assigned302.clone())?;
let assigned303={let e=e.child();let out304=Val::dict(vec![]);for item305 in {let mut s=Vec::new();s.push(e.get("shell")?.attr("Pack")?);s.push(e.get("shell")?.attr("PortField")?);s.push(e.get("shell")?.attr("Nameplate")?);Val::tuple(s)}.iter()? {e.set("kind",item305)?;out304.set(e.get("kind")?.attr("__name__")?,e.get("kind")?)?;}out304};e.set("types",assigned303.clone())?;
if {let v306=Val::Str("__hsm_namedtuple__".into());let v307=e.get("raw")?;Val::Bool(compare("in",v306.clone(),v307.clone())?.truthy()?)}.truthy()? {
let assigned308={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun311=e.get("_box_spec")?.attr("_tupled")?;let mut args309=Vec::new();let mut kw310=Vec::new();args309.push(e.get("raw")?);args309.push(e.get("types")?);fun311.call(args309,kw310)?}};e.set("pack",assigned308.clone())?;
let assigned312=e.get("pack")?.attr("placed")?;e.set("placed",assigned312.clone())?;
}else{
// stations
e.set("stations",{let params=vec![("value".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun315=e.get("isinstance")?;let mut args313=Vec::new();let mut kw314=Vec::new();args313.push(e.get("value")?);args313.push(e.get("list")?);fun315.call(args313,kw314)?}}.truthy()? {
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun318=e.get("tuple")?;let mut args316=Vec::new();let mut kw317=Vec::new();args316.push({let e=e.child();let out319=Val::list(vec![]);for item320 in e.get("value")?.iter()? {e.set("item",item320)?;out319.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun323=e.get("stations")?;let mut args321=Vec::new();let mut kw322=Vec::new();args321.push(e.get("item")?);fun323.call(args321,kw322)?}}],vec![])?;}out319});fun318.call(args316,kw317)?}});
}
if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun326=e.get("isinstance")?;let mut args324=Vec::new();let mut kw325=Vec::new();args324.push(e.get("value")?);args324.push(e.get("dict")?);fun326.call(args324,kw325)?}}.truthy()? {
if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun329=e.get("any")?;let mut args327=Vec::new();let mut kw328=Vec::new();args327.push({let e=e.child();let out330=Val::list(vec![]);for item331 in e.get("value")?.iter()? {e.set("name",item331)?;out330.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun334=e.get("name")?.attr("startswith")?;let mut args332=Vec::new();let mut kw333=Vec::new();args332.push(Val::Str("__hsm_".into()));fun334.call(args332,kw333)?}}],vec![])?;}out330});fun329.call(args327,kw328)?}}.truthy()? {
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun337=e.get("_box_spec")?.attr("_tupled")?;let mut args335=Vec::new();let mut kw336=Vec::new();args335.push(e.get("value")?);args335.push(e.get("types")?);fun337.call(args335,kw336)?}});
}
return Ok({let e=e.child();let out338=Val::dict(vec![]);for item339 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun342=e.get("value")?.attr("items")?;let mut args340=Vec::new();let mut kw341=Vec::new();fun342.call(args340,kw341)?}}.iter()? {let unpack343=unpack(item339,2)?;e.set("name",unpack343[0].clone())?;e.set("item",unpack343[1].clone())?;out338.set(e.get("name")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun346=e.get("stations")?;let mut args344=Vec::new();let mut kw345=Vec::new();args344.push(e.get("item")?);fun346.call(args344,kw345)?}})?;}out338});
}
return Ok(e.get("value")?);
Ok(Val::None)})})?;
let assigned347={let e=e.child();let out348=Val::dict(vec![]);for item349 in e.get("shell")?.attr("Pack")?.attr("_fields")?.iter()? {e.set("name",item349)?;if {let v350=e.get("name")?;let v351=e.get("raw")?;Val::Bool(compare("in",v350.clone(),v351.clone())?.truthy()?)}.truthy()? {out348.set(e.get("name")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun354=e.get("stations")?;let mut args352=Vec::new();let mut kw353=Vec::new();args352.push(e.get("raw")?.get(e.get("name")?)?);fun354.call(args352,kw353)?}})?;}}out348};e.set("values",assigned347.clone())?;
for item355 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Str("port_field".into()));s.push(e.get("shell")?.attr("PortField")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("nameplate".into()));s.push(e.get("shell")?.attr("Nameplate")?);Val::tuple(s)});Val::tuple(s)}.iter()? {
let unpack356=unpack(item355,2)?;e.set("name",unpack356[0].clone())?;e.set("record",unpack356[1].clone())?;if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun359=e.get("isinstance")?;let mut args357=Vec::new();let mut kw358=Vec::new();args357.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun362=e.get("values")?.attr("get")?;let mut args360=Vec::new();let mut kw361=Vec::new();args360.push(e.get("name")?);fun362.call(args360,kw361)?}});args357.push(e.get("dict")?);fun359.call(args357,kw358)?}}.truthy()? {
let assigned363={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun366=e.get("record")?;let mut args364=Vec::new();let mut kw365=Vec::new();kw365.extend(keyword_items(e.get("values")?.get(e.get("name")?)?)?);fun366.call(args364,kw365)?}};e.get("values")?.set(e.get("name")?,assigned363.clone())?;
}
}
let assigned367={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun370=e.get("values")?.attr("pop")?;let mut args368=Vec::new();let mut kw369=Vec::new();args368.push(Val::Str("placed".into()));fun370.call(args368,kw369)?}};e.set("placed",assigned367.clone())?;
let assigned371={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun374=e.get("shell")?.attr("Pack")?;let mut args372=Vec::new();let mut kw373=Vec::new();kw373.push(("placed".into(),{let d=Val::dict(vec![]);d}));kw373.extend(keyword_items(e.get("values")?)?);fun374.call(args372,kw373)?}};e.set("pack",assigned371.clone())?;
}
let assigned375={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun378=e.get("metadata")?.attr("get")?;let mut args376=Vec::new();let mut kw377=Vec::new();args376.push(Val::Str("raw_bounds".into()));args376.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun381=e.get("metadata")?.attr("get")?;let mut args379=Vec::new();let mut kw380=Vec::new();args379.push(Val::Str("bounds".into()));fun381.call(args379,kw380)?}});fun378.call(args376,kw377)?}};e.set("raw_bounds",assigned375.clone())?;
let assigned382={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun385=e.get("metadata")?.attr("get")?;let mut args383=Vec::new();let mut kw384=Vec::new();args383.push(Val::Str("pack_order".into()));args383.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun388=e.get("tuple")?;let mut args386=Vec::new();let mut kw387=Vec::new();args386.push(e.get("placed")?);fun388.call(args386,kw387)?}});fun385.call(args383,kw384)?}};e.set("order",assigned382.clone())?;
let assigned389={let e=e.child();let out390=Val::dict(vec![]);for item391 in e.get("order")?.iter()? {e.set("name",item391)?;if {let v392=e.get("name")?;let v393=e.get("placed")?;Val::Bool(compare("in",v392.clone(),v393.clone())?.truthy()?)}.truthy()? {out390.set(e.get("name")?,e.get("raw_bounds")?.get(e.get("name")?)?)?;}}out390};e.set("bounds",assigned389.clone())?;
let assigned394={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun397=e.get("metadata")?.attr("get")?;let mut args395=Vec::new();let mut kw396=Vec::new();args395.push(Val::Str("pack_references".into()));args395.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun400=e.get("metadata")?.attr("get")?;let mut args398=Vec::new();let mut kw399=Vec::new();args398.push(Val::Str("references".into()));fun400.call(args398,kw399)?}});fun397.call(args395,kw396)?}};e.set("references",assigned394.clone())?;
if {let v401=e.get("references")?;let v402=Val::None;Val::Bool(compare("is",v401.clone(),v402.clone())?.truthy()?)}.truthy()? {
let assigned403={let e=e.child();let out404=Val::dict(vec![]);for item405 in e.get("plan")?.get(Val::Str("instances".into()))?.iter()? {e.set("row",item405)?;if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun408=e.get("row")?.attr("get")?;let mut args406=Vec::new();let mut kw407=Vec::new();args406.push(Val::Str("name".into()));fun408.call(args406,kw407)?}}.truthy()? {out404.set(e.get("row")?.get(Val::Str("name".into()))?,e.get("row")?)?;}}out404};e.set("references",assigned403.clone())?;
}
let assigned409={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun412=e.get("pack")?.attr("_replace")?;let mut args410=Vec::new();let mut kw411=Vec::new();kw411.push(("placed".into(),{let e=e.child();let out413=Val::dict(vec![]);for item414 in e.get("bounds")?.iter()? {e.set("name",item414)?;out413.set(e.get("name")?,{let mut s=Vec::new();s.push(Val::None);s.push(Val::None);Val::tuple(s)})?;}out413}));fun412.call(args410,kw411)?}};e.set("pack",assigned409.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun417=e.get("shell")?.attr("BOUNDS")?.attr("clear")?;let mut args415=Vec::new();let mut kw416=Vec::new();fun417.call(args415,kw416)?}};
let assigned418={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun421=e.get("box_readings")?;let mut args419=Vec::new();let mut kw420=Vec::new();args419.push(e.get("shell")?);args419.push(e.get("pack")?);args419.push(e.get("bounds")?);args419.push(e.get("references")?);fun421.call(args419,kw420)?}};e.set("readings",assigned418.clone())?;
let assigned422={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun425=e.get("shell")?.attr("stated_box")?;let mut args423=Vec::new();let mut kw424=Vec::new();args423.push(e.get("pack")?);kw424.push(("readings".into(),e.get("readings")?));fun425.call(args423,kw424)?}};e.set("box",assigned422.clone())?;
let assigned426={let mut s=Vec::new();s.push(binary("truediv",binary("add",e.get("box")?.attr("inner")?.get(Val::Int(0i64))?,e.get("box")?.attr("inner")?.get(Val::Int(1i64))?)?,Val::Float(2.0f64))?);s.push(e.get("shell")?.attr("_funnel_frame_part")?.attr("center_y")?);Val::tuple(s)};e.set("centre",assigned426.clone())?;
let assigned427={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun430=e.get("shell")?.attr("with_funnel")?;let mut args428=Vec::new();let mut kw429=Vec::new();args428.push(e.get("box")?);args428.push(e.get("centre")?);fun430.call(args428,kw429)?}};e.set("box",assigned427.clone())?;
return Ok({let mut s=Vec::new();s.push(e.get("shell")?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun433=e.get("shell")?.attr("documented")?;let mut args431=Vec::new();let mut kw432=Vec::new();args431.push(e.get("box")?);fun433.call(args431,kw432)?}});Val::tuple(s)});
Ok(Val::None)})})?;
    // main
    e.set("main",{let params=vec![("box_path".into(),Some(Val::None),false),("directory".into(),Some(Val::None),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned434={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun437=e.get("load")?;let mut args435=Vec::new();let mut kw436=Vec::new();fun437.call(args435,kw436)?}};e.set("shell",assigned434.clone())?;
e.set("_box_spec",rt.import_module("_box_spec")?)?;
let mod438=rt.import_module("_machine_export")?;e.set("export",rt.member("_machine_export","export")?)?;
let mod439=rt.import_module("_machine_layout")?;e.set("dock_instances",rt.member("_machine_layout","dock_instances")?)?;
let mod440=rt.import_module("_rust_enclosure_checks")?;e.set("check_pieces",rt.member("_rust_enclosure_checks","check_pieces")?)?;
let assigned441=if {let v442=e.get("box_path")?;let v443=Val::None;Val::Bool(compare("is_not",v442.clone(),v443.clone())?.truthy()?)}.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun446=e.get("Path")?;let mut args444=Vec::new();let mut kw445=Vec::new();args444.push(e.get("box_path")?);fun446.call(args444,kw445)?}}} else {e.get("_box_spec")?.attr("ARTIFACT")?};e.set("box_path",assigned441.clone())?;
let assigned447={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun450=e.get("json")?.attr("loads")?;let mut args448=Vec::new();let mut kw449=Vec::new();args448.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun453=e.get("box_path")?.attr("read_text")?;let mut args451=Vec::new();let mut kw452=Vec::new();fun453.call(args451,kw452)?}});fun450.call(args448,kw449)?}};e.set("document",assigned447.clone())?;
let assigned454={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun457=e.get("box_from_document")?;let mut args455=Vec::new();let mut kw456=Vec::new();args455.push(e.get("document")?);fun457.call(args455,kw456)?}};let unpack458=unpack(assigned454.clone(),3)?;e.set("shell",unpack458[0].clone())?;e.set("box",unpack458[1].clone())?;e.set("bounds",unpack458[2].clone())?;
let assigned459=e.get("bounds")?;e.get("shell")?.attr("BOUNDS")?.set(Val::Slice{start:None,stop:None,step:1},assigned459.clone())?;
let assigned460=if {let v461=e.get("directory")?;let v462=Val::None;Val::Bool(compare("is_not",v461.clone(),v462.clone())?.truthy()?)}.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun465=e.get("Path")?;let mut args463=Vec::new();let mut kw464=Vec::new();args463.push(e.get("directory")?);fun465.call(args463,kw464)?}}} else {e.get("HERE")?};e.set("directory",assigned460.clone())?;
let assigned466={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun469=e.get("cut_pieces")?;let mut args467=Vec::new();let mut kw468=Vec::new();args467.push(e.get("shell")?);args467.push(e.get("box")?);args467.push(e.get("directory")?);fun469.call(args467,kw468)?}};let unpack470=unpack(assigned466.clone(),2)?;e.set("models",unpack470[0].clone())?;e.set("seated",unpack470[1].clone())?;
let assigned471={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun474=e.get("check_pieces")?;let mut args472=Vec::new();let mut kw473=Vec::new();args472.push(e.get("shell")?);args472.push(e.get("box")?);args472.push(e.get("models")?);kw473.push(("installed_retainer".into(),e.get("seated")?));fun474.call(args472,kw473)?}};e.set("readings",assigned471.clone())?;
let mod475=rt.import_module("_materials")?;e.set("linear",rt.member("_materials","linear")?)?;
let assigned476={let e=e.child();let out477=Val::list(vec![]);for item478 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun481=e.get("models")?.attr("items")?;let mut args479=Vec::new();let mut kw480=Vec::new();fun481.call(args479,kw480)?}}.iter()? {let unpack482=unpack(item478,2)?;e.set("name",unpack482[0].clone())?;e.set("model",unpack482[1].clone())?;out477.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun485=e.get("_model_instance")?;let mut args483=Vec::new();let mut kw484=Vec::new();args483.push(if {let v486=e.get("name")?;let v487=Val::Str("pump-retainer".into());Val::Bool(compare("eq",v486.clone(),v487.clone())?.truthy()?)}.truthy()? {e.get("seated")?} else {e.get("model")?});args483.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun490={let mut str491=String::new();str491.push_str("enclosure-");str491.push_str(&format(&e.get("name")?,&String::new())?);Val::Str(str491)}.attr("replace")?;let mut args488=Vec::new();let mut kw489=Vec::new();args488.push(Val::Str("-".into()));args488.push(Val::Str("_".into()));fun490.call(args488,kw489)?}});kw484.push(("color".into(),{let e=e.child();let out492=Val::list(vec![]);for item493 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun496=e.get("linear")?;let mut args494=Vec::new();let mut kw495=Vec::new();args494.push(e.get("shell")?.attr("PIECE_COLORS")?.get(e.get("name")?)?);fun496.call(args494,kw495)?}}.iter()? {e.set("c",item493)?;out492.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun499=e.get("round")?;let mut args497=Vec::new();let mut kw498=Vec::new();args497.push(e.get("c")?);args497.push(Val::Int(9i64));fun499.call(args497,kw498)?}}],vec![])?;}out492}));fun485.call(args483,kw484)?}}],vec![])?;}out477};e.set("instances",assigned476.clone())?;
if e.get("box")?.attr("pack")?.attr("collet_plate")?.truthy()? {
let assigned500={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun503=e.get("dock_instances")?;let mut args501=Vec::new();let mut kw502=Vec::new();args501.push(e.get("box")?.attr("pack")?.attr("collet_plate")?);kw502.push(("directory".into(),binary("truediv",e.get("directory")?,Val::Str("installed".into()))?));fun503.call(args501,kw502)?}};e.set("dock",assigned500.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun506=e.get("instances")?.attr("extend")?;let mut args504=Vec::new();let mut kw505=Vec::new();args504.push(e.get("dock")?.get(Val::Str("instances".into()))?);fun506.call(args504,kw505)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun509=e.get("cut_tube_setting_jig")?;let mut args507=Vec::new();let mut kw508=Vec::new();args507.push(e.get("shell")?);args507.push(e.get("box")?);args507.push(e.get("directory")?);fun509.call(args507,kw508)?}};
}
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun512=e.get("export")?;let mut args510=Vec::new();let mut kw511=Vec::new();args510.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun515=e.get("dict")?;let mut args513=Vec::new();let mut kw514=Vec::new();kw514.push(("name".into(),Val::Str("enclosure".into())));kw514.push(("instances".into(),e.get("instances")?));fun515.call(args513,kw514)?}});args510.push(e.get("directory")?);fun512.call(args510,kw511)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun518=e.get("shell")?.attr("_report_columns")?;let mut args516=Vec::new();let mut kw517=Vec::new();args516.push(e.get("box")?);fun518.call(args516,kw517)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun521=e.get("shell")?.attr("_report_seams")?;let mut args519=Vec::new();let mut kw520=Vec::new();args519.push(e.get("box")?);fun521.call(args519,kw520)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun524=e.get("shell")?.attr("_report_stacks")?;let mut args522=Vec::new();let mut kw523=Vec::new();args522.push(e.get("box")?);fun524.call(args522,kw523)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun527=e.get("shell")?.attr("_report_bounds")?;let mut args525=Vec::new();let mut kw526=Vec::new();fun527.call(args525,kw526)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun530=e.get("shell")?.attr("_write_docs")?;let mut args528=Vec::new();let mut kw529=Vec::new();args528.push(e.get("box")?);args528.push(e.get("readings")?.get(Val::Str("vents".into()))?);fun530.call(args528,kw529)?}};
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_rust_driver.rs",line!());{let fun533=e.get("dict")?;let mut args531=Vec::new();let mut kw532=Vec::new();kw532.push(("models".into(),e.get("models")?));kw532.push(("installed_retainer".into(),e.get("seated")?));kw532.push(("checks".into(),e.get("readings")?));fun533.call(args531,kw532)?}});
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
