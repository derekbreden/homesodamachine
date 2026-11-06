//! Guide recipe: `tools/install-guide/kit_art.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("json", rt.import_module("json")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let assigned2 = {
        let fun5 = {
            let fun8 = e.get("Path")?;
            let mut args6 = Vec::new();
            let mut kw7 = Vec::new();
            args6.push(e.get("__file__")?);
            fun8.call(args6, kw7)?
        }
        .attr("resolve")?;
        let mut args3 = Vec::new();
        let mut kw4 = Vec::new();
        fun5.call(args3, kw4)?
    }
    .attr("parents")?
    .get(Val::Int(2i64))?;
    e.set("ROOT", assigned2.clone())?;
    let assigned9 = binary("truediv", e.get("ROOT")?, Val::Str("hardware".into()))?;
    e.set("HARDWARE", assigned9.clone())?;
    let assigned10 = binary(
        "truediv",
        e.get("HARDWARE")?,
        Val::Str("install-guide/assets/kit".into()),
    )?;
    e.set("ART", assigned10.clone())?;
    let assigned11 = {
        let mut s = Vec::new();
        s.push({
            let fun14 = e.get("str")?;
            let mut args12 = Vec::new();
            let mut kw13 = Vec::new();
            args12.push(binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("scripts".into()),
            )?);
            fun14.call(args12, kw13)?
        });
        s.push({
            let fun17 = e.get("str")?;
            let mut args15 = Vec::new();
            let mut kw16 = Vec::new();
            args15.push(binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("install-guide".into()),
            )?);
            fun17.call(args15, kw16)?
        });
        s.push({
            let fun20 = e.get("str")?;
            let mut args18 = Vec::new();
            let mut kw19 = Vec::new();
            args18.push(binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("printed-parts/enclosure/enclosure".into()),
            )?);
            fun20.call(args18, kw19)?
        });
        Val::list(s)
    };
    e.get("sys")?.attr("path")?.set(
        Val::Slice {
            start: None,
            stop: Some(Val::Int(0i64).integer()?),
            step: 1,
        },
        assigned11.clone(),
    )?;
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    let mod21 = rt.import_module("_mesh_projection")?;
    e.set(
        "model_outlines",
        rt.member("_mesh_projection", "model_outlines")?,
    )?;
    let assigned22 = {
        let mut s = Vec::new();
        s.push(Val::Float(0.8f64));
        s.push(unary("neg", Val::Int(1i64))?);
        s.push(Val::Float(0.7f64));
        Val::tuple(s)
    };
    e.set("CAMERA", assigned22.clone())?;
    let assigned23 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("machine".into()));
            s.push(e.get("CAMERA")?);
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("faucet-and-plate".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Float(0.95f64));
                s.push(unary("neg", Val::Int(1i64))?);
                s.push(Val::Float(0.55f64));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("filtered-line".into()));
            s.push(e.get("CAMERA")?);
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("water-tees".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Float(0.6f64));
                s.push(unary("neg", Val::Int(1i64))?);
                s.push(Val::Float(0.65f64));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("regulator-and-tether".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Float(0.15f64));
                s.push(Val::Int(1i64));
                s.push(Val::Float(0.3f64));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("collet-press".into()));
            s.push({
                let mut s = Vec::new();
                s.push(unary("neg", Val::Float(0.5f64))?);
                s.push(unary("neg", Val::Float(0.9f64))?);
                s.push(Val::Float(0.85f64));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("power-cord".into()));
            s.push(e.get("CAMERA")?);
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("install-guide".into()));
            s.push(e.get("CAMERA")?);
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("cold-kit".into()));
            s.push(e.get("CAMERA")?);
            Val::tuple(s)
        });
        Val::tuple(s)
    };
    e.set("VIEWS", assigned23.clone())?;
    // models
    e.set("models", {
        let params = vec![("work".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("shared", rt.import_module("_install_art")?)?;
            let assigned24 = {
                let fun27 = e.get("json")?.attr("loads")?;
                let mut args25 = Vec::new();
                let mut kw26 = Vec::new();
                args25.push({
                    let fun30 = e.get("shared")?.attr("MACHINE_FACTS")?.attr("read_text")?;
                    let mut args28 = Vec::new();
                    let mut kw29 = Vec::new();
                    fun30.call(args28, kw29)?
                });
                fun27.call(args25, kw26)?
            };
            e.set("facts", assigned24.clone())?;
            let assigned31 = {
                let fun34 = e
                    .get("shared")?
                    .attr("_cad_art")?
                    .attr("_load_faucet_module")?;
                let mut args32 = Vec::new();
                let mut kw33 = Vec::new();
                fun34.call(args32, kw33)?
            };
            e.set("faucet", assigned31.clone())?;
            let assigned35 = {
                let fun38 = e.get("shared")?.attr("_load_regulator")?;
                let mut args36 = Vec::new();
                let mut kw37 = Vec::new();
                fun38.call(args36, kw37)?
            };
            e.set("regulator", assigned35.clone())?;
            let assigned39 = {
                let d = Val::dict(vec![]);
                d.set(
                    Val::Str("faucet".into()),
                    binary(
                        "truediv",
                        e.get("HARDWARE")?,
                        Val::Str("faucet-layout/faucet-assembly.step.npz".into()),
                    )?,
                )?;
                d.set(
                    Val::Str("collet".into()),
                    binary(
                        "truediv",
                        e.get("HARDWARE")?,
                        Val::Str("printed-parts/collet-press/collet-press.step.npz".into()),
                    )?,
                )?;
                d.set(
                    Val::Str("black_tee".into()),
                    binary(
                        "truediv",
                        e.get("HARDWARE")?,
                        Val::Str("reference/jg-pp0208e-tee/jg-pp0208e-tee.step.mesh".into()),
                    )?,
                )?;
                d.set(
                    Val::Str("regulator".into()),
                    binary(
                        "truediv",
                        e.get("shared")?.attr("REGULATOR_DIR")?,
                        Val::Str("taprite-3741-regulator.step.mesh".into()),
                    )?,
                )?;
                d.set(
                    Val::Str("white_tee".into()),
                    binary(
                        "truediv",
                        e.get("shared")?.attr("PLUMBING_DIR")?,
                        Val::Str("out/plumbing-pre-tee.step.npz".into()),
                    )?,
                )?;
                d
            };
            e.set("inputs", assigned39.clone())?;
            for item40 in {
                let mut s = Vec::new();
                s.push(e.get("shared")?.attr("MACHINE_FACTS")?);
                s.extend(
                    {
                        let fun52 = e.get("inputs")?.attr("values")?;
                        let mut args50 = Vec::new();
                        let mut kw51 = Vec::new();
                        fun52.call(args50, kw51)?
                    }
                    .iter()?,
                );
                Val::list(s)
            }
            .iter()?
            {
                e.set("path", item40)?;
                {
                    let fun43 = e.get("_rust_part")?.attr("_READ_TARGETS")?.attr("add")?;
                    let mut args41 = Vec::new();
                    let mut kw42 = Vec::new();
                    args41.push({
                        let fun46 = {
                            let fun49 = e.get("path")?.attr("relative_to")?;
                            let mut args47 = Vec::new();
                            let mut kw48 = Vec::new();
                            args47.push(e.get("ROOT")?);
                            fun49.call(args47, kw48)?
                        }
                        .attr("as_posix")?;
                        let mut args44 = Vec::new();
                        let mut kw45 = Vec::new();
                        fun46.call(args44, kw45)?
                    });
                    fun43.call(args41, kw42)?
                };
            }
            let assigned53 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("kit_art".into()), {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("inputs".into()), {
                        let e = e.child();
                        let out54 = Val::dict(vec![]);
                        for item55 in {
                            let fun58 = e.get("inputs")?.attr("items")?;
                            let mut args56 = Vec::new();
                            let mut kw57 = Vec::new();
                            fun58.call(args56, kw57)?
                        }
                        .iter()?
                        {
                            let unpack59 = unpack(item55, 2)?;
                            e.set("name", unpack59[0].clone())?;
                            e.set("path", unpack59[1].clone())?;
                            out54.set(e.get("name")?, {
                                let fun62 = {
                                    let fun65 = e.get("path")?.attr("relative_to")?;
                                    let mut args63 = Vec::new();
                                    let mut kw64 = Vec::new();
                                    args63.push(e.get("ROOT")?);
                                    fun65.call(args63, kw64)?
                                }
                                .attr("as_posix")?;
                                let mut args60 = Vec::new();
                                let mut kw61 = Vec::new();
                                fun62.call(args60, kw61)?
                            })?;
                        }
                        out54
                    })?;
                    d.set(Val::Str("machine".into()), {
                        let d = Val::dict(vec![]);
                        d.set(
                            Val::Str("outer".into()),
                            e.get("facts")?
                                .get(Val::Str("box".into()))?
                                .get(Val::Str("outer".into()))?,
                        )?;
                        d.set(
                            Val::Str("profile".into()),
                            swept_profile(
                                e.get("facts")?
                                    .get(Val::Str("box".into()))?
                                    .get(Val::Str("outer".into()))?,
                            )?,
                        )?;
                        d.set(
                            Val::Str("cover".into()),
                            e.get("facts")?
                                .get(Val::Str("bodies".into()))?
                                .get(Val::Str("funnel-cover".into()))?,
                        )?;
                        d
                    })?;
                    d.set(Val::Str("lever".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("faucet")?.attr("plateau_z")?);
                        s.push(e.get("faucet")?.attr("port_center_depth")?);
                        s.push(e.get("faucet")?.attr("soda_faucet_tube_r")?);
                        s.push(e.get("faucet")?.attr("lever_pivot_y")?);
                        s.push(e.get("faucet")?.attr("lever_pivot_z")?);
                        s.push(e.get("faucet")?.attr("lever_press_angle_deg")?);
                        Val::list(s)
                    })?;
                    d.set(Val::Str("regulator".into()), {
                        let d = Val::dict(vec![]);
                        d.set(
                            Val::Str("mouth".into()),
                            {
                                let fun71 = e.get("regulator")?.attr("outlet")?;
                                let mut args69 = Vec::new();
                                let mut kw70 = Vec::new();
                                fun71.call(args69, kw70)?
                            }
                            .get(Val::Int(0i64))?,
                        )?;
                        d.set(
                            Val::Str("insert".into()),
                            e.get("shared")?.attr("TETHER_IN_MOUTH")?,
                        )?;
                        d
                    })?;
                    d
                })?;
                d.set(Val::Str("filter".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("shared")?.attr("FILTER_D")?);
                    s.push(e.get("shared")?.attr("FILTER_L")?);
                    Val::list(s)
                })?;
                d.set(Val::Str("tube_d".into()), e.get("shared")?.attr("TUBE_D")?)?;
                d.set(Val::Str("colors".into()), {
                    let e = e.child();
                    let out72 = Val::dict(vec![]);
                    for item73 in {
                        let mut s = Vec::new();
                        s.push(Val::Str("FILTER_BODY".into()));
                        s.push(Val::Str("FILTER_CAP".into()));
                        s.push(Val::Str("WHITE_TUBE".into()));
                        s.push(Val::Str("RED_TUBE".into()));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("name", item73)?;
                        out72.set(e.get("name")?, {
                            let mut s = Vec::new();
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(0.0f64));
                            Val::list(s)
                        })?;
                    }
                    out72
                })?;
                d
            };
            e.set("numbers", assigned53.clone())?;
            {
                let fun76 = e.get("work")?.attr("mkdir")?;
                let mut args74 = Vec::new();
                let mut kw75 = Vec::new();
                kw75.push(("parents".into(), Val::Bool(true)));
                kw75.push(("exist_ok".into(), Val::Bool(true)));
                fun76.call(args74, kw75)?
            };
            let assigned77 = binary(
                "truediv",
                e.get("work")?,
                Val::Str("kit-art.numbers.json".into()),
            )?;
            e.set("path", assigned77.clone())?;
            {
                let fun80 = e.get("path")?.attr("write_text")?;
                let mut args78 = Vec::new();
                let mut kw79 = Vec::new();
                args78.push(binary(
                    "add",
                    {
                        let fun83 = e.get("json")?.attr("dumps")?;
                        let mut args81 = Vec::new();
                        let mut kw82 = Vec::new();
                        args81.push(e.get("numbers")?);
                        kw82.push(("sort_keys".into(), Val::Bool(true)));
                        fun83.call(args81, kw82)?
                    },
                    Val::Str("\n".into()),
                )?);
                fun80.call(args78, kw79)?
            };
            {
                let fun86 = e.get("_rust_part")?.attr("run")?;
                let mut args84 = Vec::new();
                let mut kw85 = Vec::new();
                args84.push(Val::Str("tooling".into()));
                args84.push(Val::Str("install-art-props".into()));
                args84.push(e.get("path")?);
                args84.push(e.get("work")?);
                fun86.call(args84, kw85)?
            };
            return Ok({
                let e = e.child();
                let out87 = Val::dict(vec![]);
                for item88 in e.get("VIEWS")?.iter()? {
                    let unpack89 = unpack(item88, 2)?;
                    e.set("name", unpack89[0].clone())?;
                    e.set("_", unpack89[1].clone())?;
                    out87.set(
                        e.get("name")?,
                        binary("truediv", e.get("work")?, {
                            let mut str90 = String::new();
                            str90.push_str(&format(&e.get("name")?, &String::new())?);
                            str90.push_str(".kit.npz");
                            Val::Str(str90)
                        })?,
                    )?;
                }
                out87
            });
            Ok(Val::None)
        })
    })?;
    // line_svg
    e.set("line_svg",{let params=vec![("model".into(),None,false),("camera".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned91={let mut s=Vec::new();s.push(unary("neg",e.get("camera")?.get(Val::Int(1i64))?)?);s.push(e.get("camera")?.get(Val::Int(0i64))?);s.push(Val::Float(0.0f64));Val::tuple(s)};e.set("right",assigned91.clone())?;
let assigned92={let fun95=e.get("model_outlines")?;let mut args93=Vec::new();let mut kw94=Vec::new();args93.push(e.get("model")?);args93.push(e.get("camera")?);args93.push(e.get("right")?);fun95.call(args93,kw94)?};e.set("points",assigned92.clone())?;
let assigned96={let e=e.child();let out97=Val::list(vec![]);for item98 in e.get("points")?.iter()? {e.set("edge",item98)?;for item99 in e.get("edge")?.iter()? {e.set("p",item99)?;out97.attr("append")?.call(vec![e.get("p")?],vec![])?;}}out97};e.set("flat",assigned96.clone())?;
let assigned100={let mut s=Vec::new();s.push({let fun103=e.get("min")?;let mut args101=Vec::new();let mut kw102=Vec::new();args101.push({let e=e.child();let out104=Val::list(vec![]);for item105 in e.get("flat")?.iter()? {e.set("p",item105)?;out104.attr("append")?.call(vec![e.get("p")?.get(Val::Int(0i64))?],vec![])?;}out104});fun103.call(args101,kw102)?});s.push({let fun108=e.get("max")?;let mut args106=Vec::new();let mut kw107=Vec::new();args106.push({let e=e.child();let out109=Val::list(vec![]);for item110 in e.get("flat")?.iter()? {e.set("p",item110)?;out109.attr("append")?.call(vec![e.get("p")?.get(Val::Int(0i64))?],vec![])?;}out109});fun108.call(args106,kw107)?});Val::tuple(s)};let unpack111=unpack(assigned100.clone(),2)?;e.set("left",unpack111[0].clone())?;e.set("right",unpack111[1].clone())?;
let assigned112={let mut s=Vec::new();s.push({let fun115=e.get("min")?;let mut args113=Vec::new();let mut kw114=Vec::new();args113.push({let e=e.child();let out116=Val::list(vec![]);for item117 in e.get("flat")?.iter()? {e.set("p",item117)?;out116.attr("append")?.call(vec![e.get("p")?.get(Val::Int(1i64))?],vec![])?;}out116});fun115.call(args113,kw114)?});s.push({let fun120=e.get("max")?;let mut args118=Vec::new();let mut kw119=Vec::new();args118.push({let e=e.child();let out121=Val::list(vec![]);for item122 in e.get("flat")?.iter()? {e.set("p",item122)?;out121.attr("append")?.call(vec![e.get("p")?.get(Val::Int(1i64))?],vec![])?;}out121});fun120.call(args118,kw119)?});Val::tuple(s)};let unpack123=unpack(assigned112.clone(),2)?;e.set("bottom",unpack123[0].clone())?;e.set("top",unpack123[1].clone())?;
let assigned124={let fun127=e.get("min")?;let mut args125=Vec::new();let mut kw126=Vec::new();args125.push(binary("truediv",Val::Int(564i64),binary("sub",e.get("right")?,e.get("left")?)?)?);args125.push(binary("truediv",Val::Int(414i64),binary("sub",e.get("top")?,e.get("bottom")?)?)?);fun127.call(args125,kw126)?};e.set("scale",assigned124.clone())?;
let assigned128={let mut s=Vec::new();s.push(binary("truediv",binary("sub",Val::Int(600i64),binary("mul",binary("sub",e.get("right")?,e.get("left")?)?,e.get("scale")?)?)?,Val::Int(2i64))?);s.push(binary("truediv",binary("sub",Val::Int(450i64),binary("mul",binary("sub",e.get("top")?,e.get("bottom")?)?,e.get("scale")?)?)?,Val::Int(2i64))?);Val::tuple(s)};let unpack129=unpack(assigned128.clone(),2)?;e.set("ox",unpack129[0].clone())?;e.set("oy",unpack129[1].clone())?;
let assigned130={let mut s=Vec::new();Val::list(s)};e.set("body",assigned130.clone())?;
for item131 in e.get("points")?.iter()? {
e.set("edge",item131)?;let assigned132={let fun135=Val::Str(" ".into()).attr("join")?;let mut args133=Vec::new();let mut kw134=Vec::new();args133.push({let e=e.child();let out136=Val::list(vec![]);for item137 in {let fun140=e.get("enumerate")?;let mut args138=Vec::new();let mut kw139=Vec::new();args138.push(e.get("edge")?);fun140.call(args138,kw139)?}.iter()? {let unpack141=unpack(item137,2)?;e.set("i",unpack141[0].clone())?;let unpack142=unpack(unpack141[1].clone(),2)?;e.set("x",unpack142[0].clone())?;e.set("y",unpack142[1].clone())?;out136.attr("append")?.call(vec![{let mut str143=String::new();str143.push_str(&format(&if {let v144=e.get("i")?;let v145=Val::Int(0i64);Val::Bool(compare("eq",v144.clone(),v145.clone())?.truthy()?)}.truthy()? {Val::Str("M".into())} else {Val::Str("L".into())},&String::new())?);str143.push_str(&format(&binary("add",e.get("ox")?,binary("mul",binary("sub",e.get("x")?,e.get("left")?)?,e.get("scale")?)?)?,&val_string({let mut str146=String::new();str146.push_str(".4f");Val::Str(str146)})?)?);str143.push_str(",");str143.push_str(&format(&binary("add",e.get("oy")?,binary("mul",binary("sub",e.get("top")?,e.get("y")?)?,e.get("scale")?)?)?,&val_string({let mut str147=String::new();str147.push_str(".4f");Val::Str(str147)})?)?);Val::Str(str143)}],vec![])?;}out136});fun135.call(args133,kw134)?};e.set("path",assigned132.clone())?;
if e.get("path")?.truthy()? {
{let fun150=e.get("body")?.attr("append")?;let mut args148=Vec::new();let mut kw149=Vec::new();args148.push({let mut str151=String::new();str151.push_str("<path d=\"");str151.push_str(&format(&e.get("path")?,&String::new())?);str151.push_str("\"/>");Val::Str(str151)});fun150.call(args148,kw149)?};
}
}
return Ok(binary("add",binary("add",Val::Str("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"600\" height=\"450\" viewBox=\"0 0 600 450\">\n<g fill=\"none\" stroke=\"#46515b\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">\n".into()),{let fun154=Val::Str("\n".into()).attr("join")?;let mut args152=Vec::new();let mut kw153=Vec::new();args152.push(e.get("body")?);fun154.call(args152,kw153)?})?,Val::Str("\n</g>\n</svg>\n".into()))?);
Ok(Val::None)})})?;
    // main
    e.set("main", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun157 = e.get("ART")?.attr("mkdir")?;
                let mut args155 = Vec::new();
                let mut kw156 = Vec::new();
                kw156.push(("parents".into(), Val::Bool(true)));
                kw156.push(("exist_ok".into(), Val::Bool(true)));
                fun157.call(args155, kw156)?
            };
            let assigned158 = {
                let fun161 = e.get("models")?;
                let mut args159 = Vec::new();
                let mut kw160 = Vec::new();
                args159.push(binary(
                    "truediv",
                    e.get("ROOT")?,
                    Val::Str(".cache/install-guide-kit".into()),
                )?);
                fun161.call(args159, kw160)?
            };
            e.set("shown", assigned158.clone())?;
            for item162 in e.get("VIEWS")?.iter()? {
                let unpack173 = unpack(item162, 2)?;
                e.set("name", unpack173[0].clone())?;
                e.set("camera", unpack173[1].clone())?;
                {
                    let fun165 = e.get("print")?;
                    let mut args163 = Vec::new();
                    let mut kw164 = Vec::new();
                    args163.push(Val::Str("Drawing".into()));
                    args163.push(e.get("name")?);
                    kw164.push(("flush".into(), Val::Bool(true)));
                    fun165.call(args163, kw164)?
                };
                {
                    let fun168 = binary("truediv", e.get("ART")?, {
                        let mut str169 = String::new();
                        str169.push_str(&format(&e.get("name")?, &String::new())?);
                        str169.push_str(".svg");
                        Val::Str(str169)
                    })?
                    .attr("write_text")?;
                    let mut args166 = Vec::new();
                    let mut kw167 = Vec::new();
                    args166.push({
                        let fun172 = e.get("line_svg")?;
                        let mut args170 = Vec::new();
                        let mut kw171 = Vec::new();
                        args170.push(e.get("shown")?.get(e.get("name")?)?);
                        args170.push(e.get("camera")?);
                        fun172.call(args170, kw171)?
                    });
                    fun168.call(args166, kw167)?
                };
            }
            {
                let fun176 = e.get("print")?;
                let mut args174 = Vec::new();
                let mut kw175 = Vec::new();
                args174.push({
                    let mut str177 = String::new();
                    str177.push_str(&format(
                        &{
                            let fun180 = e.get("len")?;
                            let mut args178 = Vec::new();
                            let mut kw179 = Vec::new();
                            args178.push(e.get("VIEWS")?);
                            fun180.call(args178, kw179)?
                        },
                        &String::new(),
                    )?);
                    str177.push_str(" kit drawings written to ");
                    str177.push_str(&format(
                        &{
                            let fun183 = e.get("ART")?.attr("relative_to")?;
                            let mut args181 = Vec::new();
                            let mut kw182 = Vec::new();
                            args181.push(e.get("ROOT")?);
                            fun183.call(args181, kw182)?
                        },
                        &String::new(),
                    )?);
                    Val::Str(str177)
                });
                fun176.call(args174, kw175)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun186 = e.get("_rust_part")?.attr("start")?;
        let mut args184 = Vec::new();
        let mut kw185 = Vec::new();
        fun186.call(args184, kw185)?
    };
    {
        let fun189 = e.get("main")?;
        let mut args187 = Vec::new();
        let mut kw188 = Vec::new();
        fun189.call(args187, kw188)?
    };
    Ok(Val::None)
}
