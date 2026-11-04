#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let assigned2 = {
        let fun5 = e.get("next")?;
        let mut args3 = Vec::new();
        let mut kw4 = Vec::new();
        args3.push({
            let e = e.child();
            let out6 = Val::list(vec![]);
            for item7 in {
                let fun10 = {
                    let fun13 = e.get("Path")?;
                    let mut args11 = Vec::new();
                    let mut kw12 = Vec::new();
                    args11.push(e.get("__file__")?);
                    fun13.call(args11, kw12)?
                }
                .attr("resolve")?;
                let mut args8 = Vec::new();
                let mut kw9 = Vec::new();
                fun10.call(args8, kw9)?
            }
            .attr("parents")?
            .iter()?
            {
                e.set("p", item7)?;
                if {
                    let fun16 = binary(
                        "truediv",
                        e.get("p")?,
                        Val::Str("hardware/scripts/_rust_part.py".into()),
                    )?
                    .attr("is_file")?;
                    let mut args14 = Vec::new();
                    let mut kw15 = Vec::new();
                    fun16.call(args14, kw15)?
                }
                .truthy()?
                {
                    out6.attr("append")?.call(vec![e.get("p")?], vec![])?;
                }
            }
            out6
        });
        fun5.call(args3, kw4)?
    };
    e.set("ROOT", assigned2.clone())?;
    {
        let fun19 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args17 = Vec::new();
        let mut kw18 = Vec::new();
        args17.push(Val::Int(0i64));
        args17.push({
            let fun22 = e.get("str")?;
            let mut args20 = Vec::new();
            let mut kw21 = Vec::new();
            args20.push(binary(
                "truediv",
                e.get("ROOT")?,
                Val::Str("hardware/scripts".into()),
            )?);
            fun22.call(args20, kw21)?
        });
        fun19.call(args17, kw18)?
    };
    e.set("source", rt.import_module("cold_core_assembly")?)?;
    e.set("points", rt.import_module("_core_points")?)?;
    let mod23 = rt.import_module("_materials")?;
    e.set("linear", rt.member("_materials", "linear")?)?;
    // _constants
    e.set("_constants", {
        let params = vec![
            ("module".into(), None, false),
            ("names".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let e = e.child();
                let out24 = Val::dict(vec![]);
                for item25 in {
                    let fun28 = e.get("names")?.attr("split")?;
                    let mut args26 = Vec::new();
                    let mut kw27 = Vec::new();
                    fun28.call(args26, kw27)?
                }
                .iter()?
                {
                    e.set("name", item25)?;
                    out24.set(e.get("name")?, {
                        let fun31 = e.get("getattr")?;
                        let mut args29 = Vec::new();
                        let mut kw30 = Vec::new();
                        args29.push(e.get("module")?);
                        args29.push(e.get("name")?);
                        fun31.call(args29, kw30)?
                    })?;
                }
                out24
            });
            Ok(Val::None)
        })
    })?;
    // _rotation_to_z
    e.set("_rotation_to_z", {
        let params = vec![("axis".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned32 = {
                let fun35 = e.get("points")?.attr("unit")?;
                let mut args33 = Vec::new();
                let mut kw34 = Vec::new();
                args33.push(e.get("axis")?);
                fun35.call(args33, kw34)?
            };
            e.set("axis", assigned32.clone())?;
            let assigned36 = {
                let fun39 = e.get("max")?;
                let mut args37 = Vec::new();
                let mut kw38 = Vec::new();
                args37.push(unary("neg", Val::Float(1.0f64))?);
                args37.push({
                    let fun42 = e.get("min")?;
                    let mut args40 = Vec::new();
                    let mut kw41 = Vec::new();
                    args40.push(Val::Float(1.0f64));
                    args40.push(e.get("axis")?.get(Val::Int(2i64))?);
                    fun42.call(args40, kw41)?
                });
                fun39.call(args37, kw38)?
            };
            e.set("dot", assigned36.clone())?;
            if {
                let v43 = e.get("dot")?;
                let v44 = binary("sub", Val::Float(1.0f64), Val::Float(1e-12f64))?;
                Val::Bool(compare("gt", v43.clone(), v44.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok({
                    let mut s = Vec::new();
                    Val::list(s)
                });
            }
            if {
                let v45 = e.get("dot")?;
                let v46 = binary(
                    "add",
                    unary("neg", Val::Float(1.0f64))?,
                    Val::Float(1e-12f64),
                )?;
                Val::Bool(compare("lt", v45.clone(), v46.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok({
                    let mut s = Vec::new();
                    s.push({
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("axis".into()), {
                            let mut s = Vec::new();
                            s.push(Val::Float(1.0f64));
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(0.0f64));
                            Val::tuple(s)
                        })?;
                        d.set(Val::Str("degrees".into()), Val::Float(180.0f64))?;
                        d
                    });
                    Val::list(s)
                });
            }
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("axis".into()), {
                        let fun49 = e.get("points")?.attr("cross")?;
                        let mut args47 = Vec::new();
                        let mut kw48 = Vec::new();
                        args47.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(1.0f64));
                            Val::tuple(s)
                        });
                        args47.push(e.get("axis")?);
                        fun49.call(args47, kw48)?
                    })?;
                    d.set(Val::Str("degrees".into()), {
                        let fun52 = e.get("math")?.attr("degrees")?;
                        let mut args50 = Vec::new();
                        let mut kw51 = Vec::new();
                        args50.push({
                            let fun55 = e.get("math")?.attr("acos")?;
                            let mut args53 = Vec::new();
                            let mut kw54 = Vec::new();
                            args53.push(e.get("dot")?);
                            fun55.call(args53, kw54)?
                        });
                        fun52.call(args50, kw51)?
                    })?;
                    d
                });
                Val::list(s)
            });
            Ok(Val::None)
        })
    })?;
    // _rotate
    e.set("_rotate", {
        let params = vec![
            ("vector".into(), None, false),
            ("rotations".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            for item56 in e.get("rotations")?.iter()? {
                e.set("rotation", item56)?;
                let assigned57 = {
                    let fun60 = e.get("points")?.attr("turned")?;
                    let mut args58 = Vec::new();
                    let mut kw59 = Vec::new();
                    args58.push(e.get("vector")?);
                    args58.push({
                        let fun63 = e.get("points")?.attr("unit")?;
                        let mut args61 = Vec::new();
                        let mut kw62 = Vec::new();
                        args61.push(e.get("rotation")?.get(Val::Str("axis".into()))?);
                        fun63.call(args61, kw62)?
                    });
                    args58.push({
                        let fun66 = e.get("math")?.attr("radians")?;
                        let mut args64 = Vec::new();
                        let mut kw65 = Vec::new();
                        args64.push(e.get("rotation")?.get(Val::Str("degrees".into()))?);
                        fun66.call(args64, kw65)?
                    });
                    fun60.call(args58, kw59)?
                };
                e.set("vector", assigned57.clone())?;
            }
            return Ok(e.get("vector")?);
            Ok(Val::None)
        })
    })?;
    // _world_to_cap
    e.set("_world_to_cap", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned67 = e.get("source")?.attr("_above_mounts")?.attr("above_core")?;
            e.set("layout", assigned67.clone())?;
            let assigned68 = {
                let fun71 = e.get("layout")?.attr("cap_lid_pose")?;
                let mut args69 = Vec::new();
                let mut kw70 = Vec::new();
                fun71.call(args69, kw70)?
            };
            e.set("pose", assigned68.clone())?;
            let assigned72 = {
                let fun75 = e.get("tuple")?;
                let mut args73 = Vec::new();
                let mut kw74 = Vec::new();
                args73.push({
                    let fun78 = e.get("zip")?;
                    let mut args76 = Vec::new();
                    let mut kw77 = Vec::new();
                    args76.extend(e.get("pose")?.get(Val::Str("rotation".into()))?.iter()?);
                    fun78.call(args76, kw77)?
                });
                fun75.call(args73, kw74)?
            };
            e.set("rows", assigned72.clone())?;
            let assigned79 = {
                let e = e.child();
                let out80 = Val::list(vec![]);
                for item81 in e.get("rows")?.iter()? {
                    e.set("row", item81)?;
                    out80.attr("append")?.call(
                        vec![unary("neg", {
                            let fun84 = e.get("points")?.attr("dot")?;
                            let mut args82 = Vec::new();
                            let mut kw83 = Vec::new();
                            args82.push(e.get("row")?);
                            args82.push(e.get("pose")?.get(Val::Str("translation_mm".into()))?);
                            fun84.call(args82, kw83)?
                        })?],
                        vec![],
                    )?;
                }
                out80
            };
            e.set("translation", assigned79.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("columns".into()), {
                    let fun87 = e.get("list")?;
                    let mut args85 = Vec::new();
                    let mut kw86 = Vec::new();
                    args85.push({
                        let fun90 = e.get("zip")?;
                        let mut args88 = Vec::new();
                        let mut kw89 = Vec::new();
                        args88.extend(e.get("rows")?.iter()?);
                        fun90.call(args88, kw89)?
                    });
                    fun87.call(args85, kw86)?
                })?;
                d.set(Val::Str("translation".into()), e.get("translation")?)?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // numbers
    e.set("numbers",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned91={let mut s=Vec::new();s.push(e.get("source")?.attr("_V")?);s.push(e.get("source")?.attr("_C")?);s.push(e.get("source")?.attr("_I")?);s.push(e.get("source")?.attr("_F")?);s.push(e.get("source")?.attr("_routes")?);Val::tuple(s)};let unpack92=unpack(assigned91.clone(),5)?;e.set("V",unpack92[0].clone())?;e.set("C",unpack92[1].clone())?;e.set("I",unpack92[2].clone())?;e.set("F",unpack92[3].clone())?;e.set("R",unpack92[4].clone())?;
let assigned93=rt.import_module("_cold_core_interface")?;e.set("core",assigned93.clone())?;
let assigned94=rt.import_module("reservoir")?;e.set("reservoir",assigned94.clone())?;
let assigned95=rt.import_module("_float_interface")?;e.set("floating",assigned95.clone())?;
let assigned96=rt.import_module("reed_bridge")?;e.set("bridge",assigned96.clone())?;
let assigned97=e.get("source")?.attr("_tube_ports")?;e.set("ports",assigned97.clone())?;
let assigned98={let mut s=Vec::new();Val::list(s)};e.set("rows",assigned98.clone())?;
// body
e.set("body",{let params=vec![("kind".into(),None,false),("name".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,Some("data"))?;let _frame=rt.frame(&outer);let assigned99={let fun102=e.get("source")?.attr("_style")?.attr("colour_for")?;let mut args100=Vec::new();let mut kw101=Vec::new();args100.push(e.get("name")?);fun102.call(args100,kw101)?};e.set("color",assigned99.clone())?;
let assigned103={let d=Val::dict(vec![]);d.set(Val::Str("kind".into()),e.get("kind")?)?;d.set(Val::Str("name".into()),e.get("name")?)?;d.set(Val::Str("color".into()),{let fun106=e.get("linear")?;let mut args104=Vec::new();let mut kw105=Vec::new();args104.push(e.get("color")?);fun106.call(args104,kw105)?})?;d.set(Val::Str("alpha".into()),{let fun109=e.get("color")?.attr("toTuple")?;let mut args107=Vec::new();let mut kw108=Vec::new();fun109.call(args107,kw108)?}.get(Val::Int(3i64))?)?;dict_extend(&d,e.get("data")?)?;d};e.set("row",assigned103.clone())?;
{let fun112=e.get("rows")?.attr("append")?;let mut args110=Vec::new();let mut kw111=Vec::new();args110.push(e.get("row")?);fun112.call(args110,kw111)?};
return Ok(e.get("row")?);
Ok(Val::None)})})?;
// model
e.set("model",{let params=vec![("name".into(),None,false),("folder".into(),None,false),("stem".into(),Some(Val::None),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,Some("placement"))?;let _frame=rt.frame(&outer);return Ok({let fun115=e.get("body")?;let mut args113=Vec::new();let mut kw114=Vec::new();args113.push(Val::Str("model".into()));args113.push(e.get("name")?);kw114.push(("model".into(),{let mut str116=String::new();str116.push_str("hardware/printed-parts/cold-core/");str116.push_str(&format(&e.get("folder")?,&String::new())?);str116.push_str("/");str116.push_str(&format(&{let v117=e.get("stem")?;if v117.truthy()? {v117} else {e.get("name")?}},&String::new())?);str116.push_str(".step.npz");Val::Str(str116)}));kw114.push(("printed_presentation".into(),{let v118=e.get("folder")?;let v119={let mut s=Vec::new();s.push(Val::Str("foam-shell".into()));s.push(Val::Str("foam-cap".into()));Val::tuple(s)};Val::Bool(compare("in",v118.clone(),v119.clone())?.truthy()?)}));kw114.extend(keyword_items(e.get("placement")?)?);fun115.call(args113,kw114)?});
Ok(Val::None)})})?;
for item120 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Str("top".into()));s.push(binary("sub",e.get("source")?.attr("_foam")?.attr("cap_face_z")?,e.get("core")?.attr("head_cbore_depth")?)?);s.push(unary("neg",Val::Float(1.0f64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("bottom".into()));s.push(binary("add",e.get("source")?.attr("_foam")?.attr("stack_floor_z")?,e.get("core")?.attr("head_pad_height")?)?);s.push(Val::Float(1.0f64));Val::tuple(s)});Val::tuple(s)}.iter()? {
let unpack130=unpack(item120,3)?;e.set("side",unpack130[0].clone())?;e.set("seat",unpack130[1].clone())?;e.set("direction",unpack130[2].clone())?;for item121 in {let fun128=e.get("enumerate")?;let mut args126=Vec::new();let mut kw127=Vec::new();args126.push(e.get("core")?.attr("attachment_xy_positions")?);args126.push(Val::Int(1i64));fun128.call(args126,kw127)?}.iter()? {
let unpack129=unpack(item121,2)?;e.set("i",unpack129[0].clone())?;e.set("xy",unpack129[1].clone())?;{let fun124=e.get("body")?;let mut args122=Vec::new();let mut kw123=Vec::new();args122.push(Val::Str("cap-clamp".into()));args122.push({let mut str125=String::new();str125.push_str("cap-clamp-");str125.push_str(&format(&e.get("side")?,&String::new())?);str125.push_str("-");str125.push_str(&format(&e.get("i")?,&String::new())?);Val::Str(str125)});kw123.push(("xy".into(),e.get("xy")?));kw123.push(("seat".into(),e.get("seat")?));kw123.push(("direction".into(),e.get("direction")?));fun124.call(args122,kw123)?};
}
}
e.set("b_fill",rt.import_module("_reservoir_b_fill")?)?;
let assigned131={let fun134=e.get("b_fill")?.attr("passage")?;let mut args132=Vec::new();let mut kw133=Vec::new();fun134.call(args132,kw133)?}.get(Val::Str("bend_end_world_mm".into()))?;let unpack135=unpack(assigned131.clone(),3)?;e.set("x",unpack135[0].clone())?;e.set("y",unpack135[1].clone())?;e.set("z",unpack135[2].clone())?;
{let fun138=e.get("model")?;let mut args136=Vec::new();let mut kw137=Vec::new();args136.push(Val::Str("reservoir-b-fill-guide".into()));args136.push(Val::Str("foam-cap".into()));kw137.push(("rotations".into(),{let mut s=Vec::new();s.push({let d=Val::dict(vec![]);d.set(Val::Str("axis".into()),{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(1.0f64));s.push(Val::Float(0.0f64));Val::tuple(s)})?;d.set(Val::Str("degrees".into()),unary("neg",Val::Float(90.0f64))?)?;d});Val::list(s)}));kw137.push(("translation".into(),{let mut s=Vec::new();s.push(binary("add",e.get("x")?,e.get("b_fill")?.attr("CHANNEL_CENTRE")?)?);s.push(binary("sub",e.get("y")?,e.get("b_fill")?.attr("BEND_RADIUS")?)?);s.push(e.get("z")?);Val::tuple(s)}));kw137.push(("transform".into(),{let fun141=e.get("_world_to_cap")?;let mut args139=Vec::new();let mut kw140=Vec::new();fun141.call(args139,kw140)?}));kw137.push(("after_rotations".into(),{let mut s=Vec::new();s.push({let d=Val::dict(vec![]);d.set(Val::Str("axis".into()),{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(Val::Float(1.0f64));Val::tuple(s)})?;d.set(Val::Str("degrees".into()),Val::Float(180.0f64))?;d});Val::list(s)}));kw137.push(("after_translation".into(),{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(binary("add",e.get("source")?.attr("foam_shell_outer_height")?,e.get("source")?.attr("_foam")?.attr("top_cap_height")?)?);Val::tuple(s)}));fun138.call(args136,kw137)?};
let mod142=rt.import_module("foam_numbers")?;e.set("stack_numbers",rt.member("foam_numbers","stack_numbers")?)?;
for item143 in {let fun149=e.get("stack_numbers")?;let mut args147=Vec::new();let mut kw148=Vec::new();fun149.call(args147,kw148)?}.get(Val::Str("models".into()))?.iter()? {
e.set("piece",item143)?;{let fun146=e.get("body")?;let mut args144=Vec::new();let mut kw145=Vec::new();args144.push(Val::Str("model".into()));args144.push(e.get("piece")?.get(Val::Str("name".into()))?);kw145.push(("model".into(),e.get("piece")?.get(Val::Str("model".into()))?));kw145.push(("rotations".into(),{let mut s=Vec::new();s.push({let d=Val::dict(vec![]);d.set(Val::Str("axis".into()),{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(Val::Float(1.0f64));Val::tuple(s)})?;d.set(Val::Str("degrees".into()),e.get("piece")?.get(Val::Str("rotation_z_degrees".into()))?)?;d});Val::list(s)}));kw145.push(("translation".into(),e.get("piece")?.get(Val::Str("translation".into()))?));fun146.call(args144,kw145)?};
}
{let fun152=e.get("body")?;let mut args150=Vec::new();let mut kw151=Vec::new();args150.push(Val::Str("carbonator-tube".into()));args150.push(Val::Str("carbonator-tube".into()));fun152.call(args150,kw151)?};
for item153 in {let mut s=Vec::new();s.push(Val::Str("bottom".into()));s.push(Val::Str("top".into()));Val::tuple(s)}.iter()? {
e.set("which",item153)?;{let fun156=e.get("body")?;let mut args154=Vec::new();let mut kw155=Vec::new();args154.push(Val::Str("endcap".into()));args154.push({let mut str157=String::new();str157.push_str("endcap-");str157.push_str(&format(&e.get("which")?,&String::new())?);Val::Str(str157)});kw155.push(("side".into(),e.get("which")?));fun156.call(args154,kw155)?};
}
{let fun160=e.get("body")?;let mut args158=Vec::new();let mut kw159=Vec::new();args158.push(Val::Str("carbonator-rod".into()));args158.push(Val::Str("float-rod-carb".into()));fun160.call(args158,kw159)?};
{let fun163=e.get("body")?;let mut args161=Vec::new();let mut kw162=Vec::new();args161.push(Val::Str("carbonator-stop".into()));args161.push(Val::Str("float-stop-carb-top".into()));fun163.call(args161,kw162)?};
for item164 in {let mut s=Vec::new();s.push(Val::Str("carbonator-earth-screw".into()));s.push(Val::Str("carbonator-earth-lockwasher".into()));Val::tuple(s)}.iter()? {
e.set("name",item164)?;{let fun167=e.get("body")?;let mut args165=Vec::new();let mut kw166=Vec::new();args165.push(e.get("name")?);args165.push(e.get("name")?);fun167.call(args165,kw166)?};
}
let assigned168={let d=Val::dict(vec![]);d};e.set("mouths",assigned168.clone())?;
for item169 in {let fun229=e.get("V")?.attr("PORTS")?.attr("items")?;let mut args227=Vec::new();let mut kw228=Vec::new();fun229.call(args227,kw228)?}.iter()? {
let unpack230=unpack(item169,2)?;e.set("name",unpack230[0].clone())?;e.set("port",unpack230[1].clone())?;if {let v170=e.get("name")?;let v171=e.get("V")?.attr("PORT_LINES")?;Val::Bool(compare("in",v170.clone(),v171.clone())?.truthy()?)}.truthy()? {
let assigned172=e.get("V")?.attr("PORT_LINES")?.get(e.get("name")?)?;let unpack173=unpack(assigned172.clone(),2)?;e.set("line",unpack173[0].clone())?;e.set("which",unpack173[1].clone())?;
let assigned174=e.get("R")?.attr("routes")?.get(e.get("line")?)?;e.set("route",assigned174.clone())?;
let assigned175=if {let v176=e.get("which")?;let v177=Val::Str("start".into());Val::Bool(compare("eq",v176.clone(),v177.clone())?.truthy()?)}.truthy()? {{let mut s=Vec::new();s.push(e.get("route")?.get(Val::Int(0i64))?);s.push(e.get("route")?.get(Val::Int(1i64))?);Val::tuple(s)}} else {{let mut s=Vec::new();s.push(e.get("route")?.get(unary("neg",Val::Int(1i64))?)?);s.push(e.get("route")?.get(unary("neg",Val::Int(2i64))?)?);Val::tuple(s)}};let unpack178=unpack(assigned175.clone(),2)?;e.set("a",unpack178[0].clone())?;e.set("b",unpack178[1].clone())?;
let assigned179={let fun182=e.get("points")?.attr("unit")?;let mut args180=Vec::new();let mut kw181=Vec::new();args180.push({let fun185=e.get("points")?.attr("sub")?;let mut args183=Vec::new();let mut kw184=Vec::new();args183.push(e.get("b")?);args183.push(e.get("a")?);fun185.call(args183,kw184)?});fun182.call(args180,kw181)?};e.set("out",assigned179.clone())?;
}else{
let assigned186=e.get("V")?.attr("PRV_OUT")?;e.set("out",assigned186.clone())?;
}
let assigned187={let mut s=Vec::new();s.push({let fun190=e.get("V")?.attr("port_corner")?;let mut args188=Vec::new();let mut kw189=Vec::new();args188.push(e.get("name")?);fun190.call(args188,kw189)?});s.push({let fun193=e.get("V")?.attr("port_up")?;let mut args191=Vec::new();let mut kw192=Vec::new();args191.push(e.get("name")?);fun193.call(args191,kw192)?});Val::tuple(s)};let unpack194=unpack(assigned187.clone(),2)?;e.set("corner",unpack194[0].clone())?;e.set("up",unpack194[1].clone())?;
let assigned195=if {let v196=e.get("port")?.get(Val::Str("plate".into()))?;let v197=Val::Str("bottom".into());Val::Bool(compare("eq",v196.clone(),v197.clone())?.truthy()?)}.truthy()? {Val::Str("male-elbow".into())} else {Val::Str("street-elbow".into())};e.set("kind",assigned195.clone())?;
let assigned198={let d=Val::dict(vec![]);d.set(Val::Str("corner".into()),e.get("corner")?)?;d.set(Val::Str("up".into()),e.get("up")?)?;d.set(Val::Str("out".into()),e.get("out")?)?;d};e.set("data",assigned198.clone())?;
if {let v199=e.get("kind")?;let v200=Val::Str("street-elbow".into());Val::Bool(compare("eq",v199.clone(),v200.clone())?.truthy()?)}.truthy()? {
{let fun203=e.get("data")?.attr("update")?;let mut args201=Vec::new();let mut kw202=Vec::new();kw202.push(("up_leg".into(),e.get("V")?.attr("ELBOW_AXIS_OFFSET")?));kw202.push(("out_leg".into(),e.get("F")?.attr("ELBOW_LEG")?));kw202.push(("male_len".into(),{let fun206=e.get("V")?.attr("male_len")?;let mut args204=Vec::new();let mut kw205=Vec::new();args204.push(e.get("name")?);fun206.call(args204,kw205)?}));fun203.call(args201,kw202)?};
}
{let fun209=e.get("body")?;let mut args207=Vec::new();let mut kw208=Vec::new();args207.push(e.get("kind")?);args207.push({let mut str210=String::new();str210.push_str("carbonator-elbow-");str210.push_str(&format(&e.get("name")?,&String::new())?);Val::Str(str210)});kw208.extend(keyword_items(e.get("data")?)?);fun209.call(args207,kw208)?};
let assigned211=if {let v212=e.get("kind")?;let v213=Val::Str("male-elbow".into());Val::Bool(compare("eq",v212.clone(),v213.clone())?.truthy()?)}.truthy()? {e.get("F")?.attr("MALE_ELBOW_MOUTH_REACH")?} else {e.get("F")?.attr("ELBOW_LEG")?};e.set("reach",assigned211.clone())?;
let assigned214={let d=Val::dict(vec![]);d.set(Val::Str("position".into()),{let fun217=e.get("points")?.attr("add")?;let mut args215=Vec::new();let mut kw216=Vec::new();args215.push(e.get("corner")?);args215.push({let fun220=e.get("points")?.attr("scale")?;let mut args218=Vec::new();let mut kw219=Vec::new();args218.push({let fun223=e.get("points")?.attr("unit")?;let mut args221=Vec::new();let mut kw222=Vec::new();args221.push(e.get("out")?);fun223.call(args221,kw222)?});args218.push(e.get("reach")?);fun220.call(args218,kw219)?});fun217.call(args215,kw216)?})?;d.set(Val::Str("axis".into()),{let fun226=e.get("points")?.attr("unit")?;let mut args224=Vec::new();let mut kw225=Vec::new();args224.push(e.get("out")?);fun226.call(args224,kw225)?})?;d};e.get("mouths")?.set(e.get("name")?,assigned214.clone())?;
}
for item231 in {let fun251=e.get("source")?.attr("RESERVOIRS")?.attr("items")?;let mut args249=Vec::new();let mut kw250=Vec::new();fun251.call(args249,kw250)?}.iter()? {
let unpack252=unpack(item231,2)?;e.set("name",unpack252[0].clone())?;e.set("stem",unpack252[1].clone())?;{let fun234=e.get("model")?;let mut args232=Vec::new();let mut kw233=Vec::new();args232.push(e.get("name")?);args232.push(Val::Str("reservoir".into()));args232.push(e.get("stem")?);fun234.call(args232,kw233)?};
{let fun237=e.get("model")?;let mut args235=Vec::new();let mut kw236=Vec::new();args235.push({let mut str238=String::new();str238.push_str(&format(&e.get("name")?,&String::new())?);str238.push_str("-cap");Val::Str(str238)});args235.push(Val::Str("reservoir".into()));args235.push({let fun241=e.get("stem")?.attr("replace")?;let mut args239=Vec::new();let mut kw240=Vec::new();args239.push(Val::Str("reservoir".into()));args239.push(Val::Str("reservoir-cap".into()));fun241.call(args239,kw240)?});kw236.push(("translation".into(),{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(e.get("reservoir")?.attr("cap_assembly_lift")?);Val::tuple(s)}));fun237.call(args235,kw236)?};
{let fun244=e.get("model")?;let mut args242=Vec::new();let mut kw243=Vec::new();args242.push({let mut str245=String::new();str245.push_str(&format(&e.get("name")?,&String::new())?);str245.push_str("-gasket");Val::Str(str245)});args242.push(Val::Str("reservoir".into()));args242.push(Val::Str("reservoir-gasket".into()));kw243.push(("mirror_x".into(),{let fun248=e.get("stem")?.attr("endswith")?;let mut args246=Vec::new();let mut kw247=Vec::new();args246.push(Val::Str("-left".into()));fun248.call(args246,kw247)?}));kw243.push(("seat_top".into(),e.get("reservoir")?.attr("cap_assembly_lift")?));fun244.call(args242,kw243)?};
}
let assigned253=binary("add",e.get("reservoir")?.attr("cap_assembly_lift")?,e.get("reservoir")?.attr("cap_wall_height")?)?;e.set("grip_z",assigned253.clone())?;
for item254 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Str("a".into()));s.push(Val::Int(1i64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("b".into()));s.push(unary("neg",Val::Int(1i64))?);Val::tuple(s)});Val::tuple(s)}.iter()? {
let unpack269=unpack(item254,2)?;e.set("letter",unpack269[0].clone())?;e.set("side",unpack269[1].clone())?;for item255 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Str("fill".into()));s.push(e.get("reservoir")?.attr("fill_position")?.get(e.get("side")?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("draw".into()));s.push(e.get("reservoir")?.attr("draw_position")?.get(e.get("side")?)?);Val::tuple(s)});Val::tuple(s)}.iter()? {
let unpack260=unpack(item255,2)?;e.set("port",unpack260[0].clone())?;e.set("xy",unpack260[1].clone())?;{let fun258=e.get("body")?;let mut args256=Vec::new();let mut kw257=Vec::new();args256.push(Val::Str("grommet".into()));args256.push({let mut str259=String::new();str259.push_str("reservoir-grip-");str259.push_str(&format(&e.get("letter")?,&String::new())?);str259.push_str("-");str259.push_str(&format(&e.get("port")?,&String::new())?);Val::Str(str259)});kw257.push(("xy".into(),e.get("xy")?));kw257.push(("z".into(),e.get("grip_z")?));kw257.push(("specification".into(),e.get("ports")?.attr("liquid_grip")?));fun258.call(args256,kw257)?};
}
{let fun263=e.get("body")?;let mut args261=Vec::new();let mut kw262=Vec::new();args261.push(Val::Str("grommet".into()));args261.push({let mut str264=String::new();str264.push_str("reservoir-grip-");str264.push_str(&format(&e.get("letter")?,&String::new())?);str264.push_str("-air");Val::Str(str264)});kw262.push(("xy".into(),e.get("ports")?.attr("air_position")?.get(e.get("side")?)?));kw262.push(("z".into(),e.get("grip_z")?));kw262.push(("specification".into(),e.get("ports")?.attr("air_grip")?));fun263.call(args261,kw262)?};
{let fun267=e.get("body")?;let mut args265=Vec::new();let mut kw266=Vec::new();args265.push(Val::Str("air-tube".into()));args265.push({let mut str268=String::new();str268.push_str("tube-reservoir-air-");str268.push_str(&format(&e.get("letter")?,&String::new())?);Val::Str(str268)});kw266.push(("xy".into(),e.get("ports")?.attr("air_position")?.get(e.get("side")?)?));kw266.push(("z0".into(),binary("sub",e.get("grip_z")?,e.get("ports")?.attr("air_tube_below_lid")?)?));kw266.push(("z1".into(),binary("add",e.get("source")?.attr("_foam")?.attr("cap_face_z")?,e.get("ports")?.attr("air_tube_above_casing")?)?));fun267.call(args265,kw266)?};
}
{let fun272=e.get("body")?;let mut args270=Vec::new();let mut kw271=Vec::new();args270.push(Val::Str("coil".into()));args270.push(Val::Str("evap-coil".into()));fun272.call(args270,kw271)?};
for item273 in {let mut s=Vec::new();s.push(Val::Str("inlet".into()));s.push(Val::Str("outlet".into()));Val::tuple(s)}.iter()? {
e.set("which",item273)?;{let fun276=e.get("body")?;let mut args274=Vec::new();let mut kw275=Vec::new();args274.push(Val::Str("coil-tail".into()));args274.push({let mut str277=String::new();str277.push_str("evap-tail-");str277.push_str(&format(&e.get("which")?,&String::new())?);Val::Str(str277)});kw275.push(("segments".into(),{let fun280=e.get("C")?.attr("tail_layout")?;let mut args278=Vec::new();let mut kw279=Vec::new();args278.push(e.get("which")?);fun280.call(args278,kw279)?}));fun276.call(args274,kw275)?};
}
let assigned281={let mut s=Vec::new();s.push({let fun284=e.get("V")?.attr("port_corner")?;let mut args282=Vec::new();let mut kw283=Vec::new();args282.push(Val::Str("water-in".into()));fun284.call(args282,kw283)?});s.push({let fun287=e.get("V")?.attr("port_up")?;let mut args285=Vec::new();let mut kw286=Vec::new();args285.push(Val::Str("water-in".into()));fun287.call(args285,kw286)?});Val::tuple(s)};let unpack288=unpack(assigned281.clone(),2)?;e.set("water_corner",unpack288[0].clone())?;e.set("water_up",unpack288[1].clone())?;
let assigned289={let fun292=e.get("points")?.attr("add")?;let mut args290=Vec::new();let mut kw291=Vec::new();args290.push(e.get("water_corner")?);args290.push({let fun295=e.get("points")?.attr("scale")?;let mut args293=Vec::new();let mut kw294=Vec::new();args293.push(e.get("water_up")?);args293.push(binary("add",{let fun298=e.get("V")?.attr("axis_offset")?;let mut args296=Vec::new();let mut kw297=Vec::new();args296.push(Val::Str("water-in".into()));fun298.call(args296,kw297)?},{let fun301=e.get("V")?.attr("male_len")?;let mut args299=Vec::new();let mut kw300=Vec::new();args299.push(Val::Str("water-in".into()));fun301.call(args299,kw300)?})?);fun295.call(args293,kw294)?});fun292.call(args290,kw291)?};e.set("tip",assigned289.clone())?;
{let fun304=e.get("body")?;let mut args302=Vec::new();let mut kw303=Vec::new();args302.push(Val::Str("jet".into()));args302.push(Val::Str("water-inlet-jet-cap-nominal".into()));kw303.push(("at".into(),e.get("tip")?));kw303.push(("axis".into(),e.get("water_up")?));fun304.call(args302,kw303)?};
for item305 in e.get("I")?.attr("PTC_PORTS")?.iter()? {
e.set("name",item305)?;let assigned306=e.get("mouths")?.get(e.get("name")?)?;e.set("mouth",assigned306.clone())?;
let assigned307={let fun310=e.get("points")?.attr("add")?;let mut args308=Vec::new();let mut kw309=Vec::new();args308.push(e.get("mouth")?.get(Val::Str("position".into()))?);args308.push({let fun313=e.get("points")?.attr("scale")?;let mut args311=Vec::new();let mut kw312=Vec::new();args311.push(e.get("mouth")?.get(Val::Str("axis".into()))?);args311.push(e.get("I")?.attr("PTC_STANDOFF")?);fun313.call(args311,kw312)?});fun310.call(args308,kw309)?};e.set("origin",assigned307.clone())?;
{let fun316=e.get("body")?;let mut args314=Vec::new();let mut kw315=Vec::new();args314.push(Val::Str("collet".into()));args314.push({let mut str317=String::new();str317.push_str("collet-");str317.push_str(&format(&e.get("name")?,&String::new())?);Val::Str(str317)});kw315.push(("at".into(),e.get("origin")?));kw315.push(("axis".into(),{let fun320=e.get("points")?.attr("scale")?;let mut args318=Vec::new();let mut kw319=Vec::new();args318.push(e.get("mouth")?.get(Val::Str("axis".into()))?);args318.push(unary("neg",Val::Float(1.0f64))?);fun320.call(args318,kw319)?}));fun316.call(args314,kw315)?};
}
{let fun323=e.get("body")?;let mut args321=Vec::new();let mut kw322=Vec::new();args321.push(Val::Str("float".into()));args321.push(Val::Str("float-carb".into()));kw322.push(("at".into(),{let mut s=Vec::new();s.extend({let e=e.child();let out324=Val::list(vec![]);for item325 in e.get("core")?.attr("carbonator_sensor_axis")?.iter()? {e.set("v",item325)?;out324.attr("append")?.call(vec![binary("mul",e.get("V")?.attr("ROD_RADIUS")?,e.get("v")?)?],vec![])?;}out324}.iter()?);s.push(binary("add",e.get("bridge")?.attr("reed_high_z")?,e.get("V")?.attr("carbonator_bottom_z")?)?);Val::tuple(s)}));fun323.call(args321,kw322)?};
for item326 in {let fun336=e.get("enumerate")?;let mut args334=Vec::new();let mut kw335=Vec::new();args334.push({let fun339=e.get("I")?.attr("carbonator_reed_z")?;let mut args337=Vec::new();let mut kw338=Vec::new();fun339.call(args337,kw338)?});args334.push(Val::Int(1i64));fun336.call(args334,kw335)?}.iter()? {
let unpack340=unpack(item326,2)?;e.set("i",unpack340[0].clone())?;e.set("z",unpack340[1].clone())?;{let fun329=e.get("body")?;let mut args327=Vec::new();let mut kw328=Vec::new();args327.push(Val::Str("reed".into()));args327.push({let mut str330=String::new();str330.push_str("reed-carb-");str330.push_str(&format(&e.get("i")?,&String::new())?);Val::Str(str330)});kw328.push(("at".into(),{let mut s=Vec::new();s.extend({let fun333=e.get("I")?.attr("carbonator_reed_xy")?;let mut args331=Vec::new();let mut kw332=Vec::new();fun333.call(args331,kw332)?}.iter()?);s.push(e.get("z")?);Val::tuple(s)}));fun329.call(args327,kw328)?};
}
for item341 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Str("a".into()));s.push(Val::Int(1i64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("b".into()));s.push(unary("neg",Val::Int(1i64))?);Val::tuple(s)});Val::tuple(s)}.iter()? {
let unpack366=unpack(item341,2)?;e.set("name",unpack366[0].clone())?;e.set("side",unpack366[1].clone())?;{let fun344=e.get("body")?;let mut args342=Vec::new();let mut kw343=Vec::new();args342.push(Val::Str("reservoir-rod".into()));args342.push({let mut str345=String::new();str345.push_str("float-rod-");str345.push_str(&format(&e.get("name")?,&String::new())?);Val::Str(str345)});kw343.push(("reservoir".into(),{let mut str346=String::new();str346.push_str("reservoir-");str346.push_str(&format(&e.get("name")?,&String::new())?);Val::Str(str346)}));kw343.push(("x".into(),binary("mul",e.get("side")?,e.get("I")?.attr("RES_ROD_X")?)?));kw343.push(("y".into(),e.get("I")?.attr("RES_ROD_Y")?));fun344.call(args342,kw343)?};
{let fun349=e.get("body")?;let mut args347=Vec::new();let mut kw348=Vec::new();args347.push(Val::Str("float".into()));args347.push({let mut str350=String::new();str350.push_str("float-");str350.push_str(&format(&e.get("name")?,&String::new())?);Val::Str(str350)});kw348.push(("at".into(),{let mut s=Vec::new();s.push(binary("mul",e.get("side")?,e.get("I")?.attr("RES_ROD_X")?)?);s.push(e.get("I")?.attr("RES_ROD_Y")?);s.push(binary("truediv",{let fun353=e.get("sum")?;let mut args351=Vec::new();let mut kw352=Vec::new();args351.push(e.get("I")?.attr("FLOAT_TRAVEL_Z")?);fun353.call(args351,kw352)?},Val::Float(2.0f64))?);Val::tuple(s)}));fun349.call(args347,kw348)?};
for item354 in {let fun361=e.get("enumerate")?;let mut args359=Vec::new();let mut kw360=Vec::new();args359.push({let fun364=e.get("I")?.attr("reservoir_reed_z")?;let mut args362=Vec::new();let mut kw363=Vec::new();fun364.call(args362,kw363)?});args359.push(Val::Int(1i64));fun361.call(args359,kw360)?}.iter()? {
let unpack365=unpack(item354,2)?;e.set("i",unpack365[0].clone())?;e.set("z",unpack365[1].clone())?;{let fun357=e.get("body")?;let mut args355=Vec::new();let mut kw356=Vec::new();args355.push(Val::Str("reed".into()));args355.push({let mut str358=String::new();str358.push_str("reed-");str358.push_str(&format(&e.get("name")?,&String::new())?);str358.push_str("-");str358.push_str(&format(&e.get("i")?,&String::new())?);Val::Str(str358)});kw356.push(("at".into(),{let mut s=Vec::new();s.push(binary("mul",e.get("side")?,e.get("I")?.attr("REED_COLUMN_X")?)?);s.push(e.get("I")?.attr("reed_y_center")?);s.push(e.get("z")?);Val::tuple(s)}));fun357.call(args355,kw356)?};
}
}
let assigned367={let fun370=e.get("C")?.attr("gap_z_near")?;let mut args368=Vec::new();let mut kw369=Vec::new();args368.push(Val::Float(180.0f64));args368.push(binary("truediv",{let fun373=e.get("sum")?;let mut args371=Vec::new();let mut kw372=Vec::new();args371.push(e.get("V")?.attr("interior_z")?);fun373.call(args371,kw372)?},Val::Float(2.0f64))?);fun370.call(args368,kw369)?};e.set("probe_z",assigned367.clone())?;
{let fun376=e.get("body")?;let mut args374=Vec::new();let mut kw375=Vec::new();args374.push(Val::Str("probe".into()));args374.push(Val::Str("probe-carbonator-ds18b20".into()));kw375.push(("at".into(),{let mut s=Vec::new();s.push(unary("neg",binary("add",e.get("core")?.attr("carbonator_outer_radius")?,e.get("I")?.attr("PROBE_STANDOFF")?)?)?);s.push(Val::Float(0.0f64));s.push(e.get("probe_z")?);Val::tuple(s)}));fun376.call(args374,kw375)?};
{let fun379=e.get("body")?;let mut args377=Vec::new();let mut kw378=Vec::new();args377.push(Val::Str("probe".into()));args377.push(Val::Str("probe-coil-ds18s20".into()));kw378.push(("at".into(),{let fun382=e.get("C")?.attr("_at_xyz")?;let mut args380=Vec::new();let mut kw381=Vec::new();args380.push(e.get("C")?.attr("AZ_OUT")?);args380.push(e.get("C")?.attr("evap_tail_high_z")?);args380.push(binary("add",binary("add",e.get("C")?.attr("WIND_R")?,e.get("C")?.attr("TUBE_R")?)?,binary("truediv",e.get("F")?.attr("TO92_W")?,Val::Float(2.0f64))?)?);fun382.call(args380,kw381)?}));fun379.call(args377,kw378)?};
let assigned383=e.get("mouths")?.get(Val::Str("prv".into()))?;e.set("prv",assigned383.clone())?;
let assigned384=e.get("prv")?.get(Val::Str("axis".into()))?;e.set("axis",assigned384.clone())?;
let assigned385={let fun388=e.get("_rotation_to_z")?;let mut args386=Vec::new();let mut kw387=Vec::new();args386.push(e.get("axis")?);fun388.call(args386,kw387)?};e.set("rotations",assigned385.clone())?;
let assigned389={let fun392=e.get("_rotate")?;let mut args390=Vec::new();let mut kw391=Vec::new();args390.push(e.get("source")?.attr("VENT_LOCAL")?);args390.push(e.get("rotations")?);fun392.call(args390,kw391)?};e.set("vent",assigned389.clone())?;
let assigned393=e.get("source")?.attr("VENT_WORLD")?;e.set("down",assigned393.clone())?;
let assigned394={let fun397=e.get("math")?.attr("degrees")?;let mut args395=Vec::new();let mut kw396=Vec::new();args395.push({let fun400=e.get("math")?.attr("atan2")?;let mut args398=Vec::new();let mut kw399=Vec::new();args398.push({let fun403=e.get("points")?.attr("dot")?;let mut args401=Vec::new();let mut kw402=Vec::new();args401.push(e.get("axis")?);args401.push({let fun406=e.get("points")?.attr("cross")?;let mut args404=Vec::new();let mut kw405=Vec::new();args404.push(e.get("vent")?);args404.push(e.get("down")?);fun406.call(args404,kw405)?});fun403.call(args401,kw402)?});args398.push({let fun409=e.get("points")?.attr("dot")?;let mut args407=Vec::new();let mut kw408=Vec::new();args407.push(e.get("vent")?);args407.push(e.get("down")?);fun409.call(args407,kw408)?});fun400.call(args398,kw399)?});fun397.call(args395,kw396)?};e.set("roll",assigned394.clone())?;
{let fun412=e.get("rotations")?.attr("append")?;let mut args410=Vec::new();let mut kw411=Vec::new();args410.push({let d=Val::dict(vec![]);d.set(Val::Str("axis".into()),e.get("axis")?)?;d.set(Val::Str("degrees".into()),e.get("roll")?)?;d});fun412.call(args410,kw411)?};
{let fun415=e.get("body")?;let mut args413=Vec::new();let mut kw414=Vec::new();args413.push(Val::Str("prv".into()));args413.push(Val::Str("prv-sv125".into()));kw414.push(("at".into(),e.get("prv")?.get(Val::Str("position".into()))?));kw414.push(("axis".into(),e.get("axis")?));fun415.call(args413,kw414)?};
{let fun418=e.get("model")?;let mut args416=Vec::new();let mut kw417=Vec::new();args416.push(Val::Str("prv-shroud".into()));args416.push(Val::Str("prv-shroud".into()));kw417.push(("rotations".into(),e.get("rotations")?));kw417.push(("translation".into(),e.get("prv")?.get(Val::Str("position".into()))?));fun418.call(args416,kw417)?};
{let fun421=e.get("model")?;let mut args419=Vec::new();let mut kw420=Vec::new();args419.push(Val::Str("reed-bridge".into()));args419.push(Val::Str("reed-bridge".into()));kw420.push(("rotations".into(),{let mut s=Vec::new();s.push({let d=Val::dict(vec![]);d.set(Val::Str("axis".into()),{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(Val::Float(1.0f64));Val::tuple(s)})?;d.set(Val::Str("degrees".into()),e.get("core")?.attr("carbonator_sensor_azimuth")?)?;d});Val::list(s)}));kw420.push(("translation".into(),{let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(e.get("V")?.attr("carbonator_bottom_z")?);Val::tuple(s)}));fun421.call(args419,kw420)?};
let assigned422={let e=e.child();let out423=Val::dict(vec![]);for item424 in {let fun427=e.get("R")?.attr("routes")?.attr("items")?;let mut args425=Vec::new();let mut kw426=Vec::new();fun427.call(args425,kw426)?}.iter()? {let unpack428=unpack(item424,2)?;e.set("name",unpack428[0].clone())?;e.set("route",unpack428[1].clone())?;out423.set(e.get("name")?,{let fun431=e.get("list")?;let mut args429=Vec::new();let mut kw430=Vec::new();args429.push(e.get("route")?);fun431.call(args429,kw430)?})?;}out423};e.set("trimmed",assigned422.clone())?;
for item432 in {let fun438=e.get("V")?.attr("PORT_LINES")?.attr("items")?;let mut args436=Vec::new();let mut kw437=Vec::new();fun438.call(args436,kw437)?}.iter()? {
let unpack439=unpack(item432,2)?;e.set("port",unpack439[0].clone())?;let unpack440=unpack(unpack439[1].clone(),2)?;e.set("line",unpack440[0].clone())?;e.set("which",unpack440[1].clone())?;let assigned433=e.get("mouths")?.get(e.get("port")?)?.get(Val::Str("position".into()))?;e.get("trimmed")?.get(e.get("line")?)?.set(if {let v434=e.get("which")?;let v435=Val::Str("start".into());Val::Bool(compare("eq",v434.clone(),v435.clone())?.truthy()?)}.truthy()? {Val::Int(0i64)} else {unary("neg",Val::Int(1i64))?},assigned433.clone())?;
}
let assigned441=e.get("source")?.attr("_shroud")?;e.set("shroud",assigned441.clone())?;
let assigned442={let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(binary("truediv",unary("neg",e.get("shroud")?.attr("outer_diameter")?)?,Val::Float(2.0f64))?);s.push(e.get("shroud")?.attr("vent_station_z")?);Val::tuple(s)};e.set("local",assigned442.clone())?;
let assigned443={let fun446=e.get("points")?.attr("add")?;let mut args444=Vec::new();let mut kw445=Vec::new();args444.push({let fun449=e.get("_rotate")?;let mut args447=Vec::new();let mut kw448=Vec::new();args447.push(e.get("local")?);args447.push(e.get("rotations")?);fun449.call(args447,kw448)?});args444.push(e.get("prv")?.get(Val::Str("position".into()))?);fun446.call(args444,kw445)?};e.set("vent_mouth",assigned443.clone())?;
let assigned450={let fun453=e.get("tuple")?;let mut args451=Vec::new();let mut kw452=Vec::new();args451.push({let e=e.child();let out454=Val::list(vec![]);for item455 in e.get("vent_mouth")?.iter()? {e.set("v",item455)?;out454.attr("append")?.call(vec![{let fun458=e.get("round")?;let mut args456=Vec::new();let mut kw457=Vec::new();args456.push(e.get("v")?);args456.push(Val::Int(6i64));fun458.call(args456,kw457)?}],vec![])?;}out454});fun453.call(args451,kw452)?};e.get("trimmed")?.get(Val::Str("prv-vent".into()))?.set(Val::Int(0i64),assigned450.clone())?;
let assigned459={let e=e.child();let out460=Val::list(vec![]);for item461 in {let fun464=e.get("sorted")?;let mut args462=Vec::new();let mut kw463=Vec::new();args462.push(e.get("trimmed")?);fun464.call(args462,kw463)?}.iter()? {e.set("name",item461)?;out460.attr("append")?.call(vec![{let d=Val::dict(vec![]);d.set(Val::Str("name".into()),e.get("name")?)?;d.set(Val::Str("points".into()),e.get("trimmed")?.get(e.get("name")?)?)?;d.set(Val::Str("exempt".into()),{let fun467=e.get("source")?.attr("MADE_UP_ON")?.attr("get")?;let mut args465=Vec::new();let mut kw466=Vec::new();args465.push(e.get("name")?);args465.push({let mut s=Vec::new();Val::tuple(s)});fun467.call(args465,kw466)?})?;d}],vec![])?;}out460};e.set("route_rows",assigned459.clone())?;
let assigned468={let e=e.child();let out469=Val::dict(vec![]);for item470 in e.get("rows")?.iter()? {e.set("row",item470)?;out469.set(e.get("row")?.get(Val::Str("name".into()))?,e.get("row")?.get(Val::Str("alpha".into()))?)?;}out469};e.set("alpha",assigned468.clone())?;
for item471 in e.get("route_rows")?.iter()? {
e.set("route",item471)?;let assigned472=binary("add",Val::Str("line-".into()),e.get("route")?.get(Val::Str("name".into()))?)?;e.set("name",assigned472.clone())?;
let assigned473={let fun476=e.get("source")?.attr("_style")?.attr("colour_for")?;let mut args474=Vec::new();let mut kw475=Vec::new();args474.push(e.get("name")?);fun476.call(args474,kw475)?};e.set("color",assigned473.clone())?;
{let fun479=e.get("route")?.attr("update")?;let mut args477=Vec::new();let mut kw478=Vec::new();kw478.push(("color".into(),{let fun482=e.get("linear")?;let mut args480=Vec::new();let mut kw481=Vec::new();args480.push(e.get("color")?);fun482.call(args480,kw481)?}));kw478.push(("alpha".into(),{let fun485=e.get("color")?.attr("toTuple")?;let mut args483=Vec::new();let mut kw484=Vec::new();fun485.call(args483,kw484)?}.get(Val::Int(3i64))?));fun479.call(args477,kw478)?};
let assigned486=e.get("route")?.get(Val::Str("alpha".into()))?;e.get("alpha")?.set(e.get("name")?,assigned486.clone())?;
}
e.set("bond",rt.import_module("_carbonator_bond")?)?;
let mod487=rt.import_module("_cadq_export")?;e.set("note_read",rt.member("_cadq_export","note_read")?)?;
let mod488=rt.import_module("_payload_rules")?;e.set("LINEAR_DEFLECTION_RATIO",rt.member("_payload_rules","LINEAR_DEFLECTION_RATIO")?)?;
for item489 in e.get("rows")?.iter()? {
e.set("row",item489)?;if {let v490=e.get("row")?.get(Val::Str("kind".into()))?;let v491=Val::Str("model".into());Val::Bool(compare("eq",v490.clone(),v491.clone())?.truthy()?)}.truthy()? {
{let fun494=e.get("note_read")?;let mut args492=Vec::new();let mut kw493=Vec::new();args492.push(binary("truediv",e.get("ROOT")?,e.get("row")?.get(Val::Str("model".into()))?)?);fun494.call(args492,kw493)?};
}
}
return Ok({let d=Val::dict(vec![]);d.set(Val::Str("bodies".into()),e.get("rows")?)?;d.set(Val::Str("routes".into()),e.get("route_rows")?)?;d.set(Val::Str("mouths".into()),e.get("mouths")?)?;d.set(Val::Str("fittings".into()),{let fun497=e.get("_constants")?;let mut args495=Vec::new();let mut kw496=Vec::new();args495.push(e.get("F")?);args495.push(Val::Str("ELBOW_HEX_AF ELBOW_BORE ELBOW_MALE_R SOCKET_R SOCKET_DEPTH\n            MALE_ELBOW_BODY_D MALE_ELBOW_MOUTH_REACH MALE_ELBOW_AXIS_REACH MALE_ELBOW_THREAD\n            MALE_ELBOW_POST_W MALE_ELBOW_INSERTION MALE_ELBOW_TUBE_OD MALE_ELBOW_FLOW_BORE\n            PRV_MALE_LEN PRV_HEX_H PRV_HEX_AF PRV_CAP_R PRV_CAP_H\n            REED_GLASS_LEN REED_GLASS_R TO92_W TO92_H TO92_CORNER_R".into()));fun497.call(args495,kw496)?})?;d.set(Val::Str("float".into()),{let fun500=e.get("_constants")?;let mut args498=Vec::new();let mut kw499=Vec::new();args498.push(e.get("floating")?);args498.push(Val::Str("height diameter bore_diameter magnet_seat pocket_od\n            pocket_id pocket_depth magnet_od magnet_id magnet_thickness".into()));fun500.call(args498,kw499)?})?;d.set(Val::Str("collet".into()),{let fun503=e.get("_constants")?;let mut args501=Vec::new();let mut kw502=Vec::new();args501.push(e.get("I")?.attr("_ptc")?);args501.push(Val::Str("COLLET_D COLLET_LENGTH HEX_ACROSS_CORNERS HEX_LENGTH SHANK_D SHANK_LENGTH".into()));fun503.call(args501,kw502)?})?;d.set(Val::Str("carbonator".into()),{let d=Val::dict(vec![]);dict_extend(&d,{let fun506=e.get("_constants")?;let mut args504=Vec::new();let mut kw505=Vec::new();args504.push(e.get("V")?);args504.push(Val::Str("TUBE_OD TUBE_ID carbonator_height carbonator_bottom_z\n            PLATE_D PLATE_T PORT_TAP_D ROD_D ROD_XY REGISTER_DEPTH UPPER_STOP_H\n            UPPER_STOP_D UPPER_STOP_BORE bottom_plate_z top_plate_z interior_z".into()));fun506.call(args504,kw505)?})?;d.set(Val::Str("register_diameter".into()),binary("mul",e.get("V")?.attr("_endcap")?.attr("register_drill_diameter")?,e.get("V")?.attr("IN")?)?)?;d.set(Val::Str("ports".into()),{let e=e.child();let out507=Val::list(vec![]);for item508 in {let fun511=e.get("V")?.attr("PORTS")?.attr("items")?;let mut args509=Vec::new();let mut kw510=Vec::new();fun511.call(args509,kw510)?}.iter()? {let unpack512=unpack(item508,2)?;e.set("name",unpack512[0].clone())?;e.set("port",unpack512[1].clone())?;out507.attr("append")?.call(vec![{let d=Val::dict(vec![]);d.set(Val::Str("name".into()),e.get("name")?)?;dict_extend(&d,e.get("port")?)?;d}],vec![])?;}out507})?;d})?;d.set(Val::Str("cap_clamp".into()),e.get("source")?.attr("CAP_CLAMP")?)?;d.set(Val::Str("bond".into()),{let d=Val::dict(vec![]);dict_extend(&d,{let fun515=e.get("bond")?.attr("datums")?;let mut args513=Vec::new();let mut kw514=Vec::new();args513.push(e.get("V")?.attr("top_plate_z")?.get(Val::Int(1i64))?);fun515.call(args513,kw514)?})?;dict_extend(&d,{let fun518=e.get("_constants")?;let mut args516=Vec::new();let mut kw517=Vec::new();args516.push(e.get("bond")?);args516.push(Val::Str("TUBE_WALL THREAD_DIAMETER\n            SCREW_DIAMETER SCREW_LENGTH SCREW_HEAD_DIAMETER SCREW_HEAD_HEIGHT\n            WASHER_DIAMETER WASHER_BORE WASHER_THICKNESS".into()));fun518.call(args516,kw517)?})?;d})?;d.set(Val::Str("coil".into()),{let d=Val::dict(vec![]);dict_extend(&d,{let fun521=e.get("_constants")?;let mut args519=Vec::new();let mut kw520=Vec::new();args519.push(e.get("C")?);args519.push(Val::Str("TUBE_R WIND_R TOTAL_WRAPS PITCH WIND_HEIGHT evap_tail_low_z AZ_IN".into()));fun521.call(args519,kw520)?})?;d.set(Val::Str("stock".into()),{let fun524=e.get("vars")?;let mut args522=Vec::new();let mut kw523=Vec::new();args522.push(e.get("C")?.attr("COPPER_STOCK")?);fun524.call(args522,kw523)?})?;d.set(Val::Str("bend_floor".into()),e.get("C")?.attr("COPPER_BEND")?)?;d.set(Val::Str("path_chord_mm".into()),Val::Float(0.0035f64))?;d})?;d.set(Val::Str("ports".into()),{let fun527=e.get("_constants")?;let mut args525=Vec::new();let mut kw526=Vec::new();args525.push(e.get("ports")?);args525.push(Val::Str("plate_thickness air_tube_od air_tube_id".into()));fun527.call(args525,kw526)?})?;d.set(Val::Str("internals".into()),{let fun530=e.get("_constants")?;let mut args528=Vec::new();let mut kw529=Vec::new();args528.push(e.get("I")?);args528.push(Val::Str("RES_ROD_LEN RES_ROD_X RES_ROD_Y FLOAT_TRAVEL_Z".into()));fun530.call(args528,kw529)?})?;d.set(Val::Str("jet".into()),{let fun533=e.get("_constants")?;let mut args531=Vec::new();let mut kw532=Vec::new();args531.push(e.get("I")?);args531.push(Val::Str("JET_CAP_D JET_CAP_T JET_PASSAGE_D".into()));fun533.call(args531,kw532)?})?;d.set(Val::Str("routing".into()),{let d=Val::dict(vec![]);d.set(Val::Str("radius".into()),e.get("R")?.attr("line_radius")?)?;d.set(Val::Str("stock_bend".into()),e.get("R")?.attr("route_bend_radius")?)?;d.set(Val::Str("floor".into()),e.get("R")?.attr("bend_floor")?)?;d.set(Val::Str("ladder".into()),e.get("R")?.attr("bend_ladder")?)?;d.set(Val::Str("touch_volume".into()),e.get("R")?.attr("touch_volume")?)?;d.set(Val::Str("tail_names".into()),e.get("source")?.attr("TAIL_LINES")?)?;d.set(Val::Str("prv_flank_y".into()),e.get("R")?.attr("prv_vent_flank_y")?)?;d})?;d.set(Val::Str("presentation".into()),{let d=Val::dict(vec![]);d.set(Val::Str("deflection_ratio".into()),e.get("LINEAR_DEFLECTION_RATIO")?)?;d.set(Val::Str("simplification_fraction".into()),Val::Float(0.5f64))?;d})?;d.set(Val::Str("card".into()),{let d=Val::dict(vec![]);d.set(Val::Str("touch_volume".into()),e.get("source")?.attr("_card")?.attr("TOUCH_VOLUME")?)?;d.set(Val::Str("joined".into()),{let fun536=e.get("sorted")?;let mut args534=Vec::new();let mut kw535=Vec::new();args534.push({let e=e.child();let out537=Val::list(vec![]);for item538 in e.get("source")?.attr("JOINED")?.iter()? {e.set("pair",item538)?;out537.attr("append")?.call(vec![{let fun541=e.get("sorted")?;let mut args539=Vec::new();let mut kw540=Vec::new();args539.push(e.get("pair")?);fun541.call(args539,kw540)?}],vec![])?;}out537});fun536.call(args534,kw535)?})?;d.set(Val::Str("rides_on".into()),{let fun544=e.get("sorted")?;let mut args542=Vec::new();let mut kw543=Vec::new();args542.push({let e=e.child();let out545=Val::list(vec![]);for item546 in e.get("source")?.attr("RIDES_ON")?.iter()? {e.set("pair",item546)?;out545.attr("append")?.call(vec![{let fun549=e.get("sorted")?;let mut args547=Vec::new();let mut kw548=Vec::new();args547.push(e.get("pair")?);fun549.call(args547,kw548)?}],vec![])?;}out545});fun544.call(args542,kw543)?})?;d})?;d.set(Val::Str("document".into()),{let d=Val::dict(vec![]);d.set(Val::Str("frame".into()),Val::Str("foam assembly source".into()))?;d.set(Val::Str("schema".into()),Val::Str("hsm-cold-core-model-1".into()))?;d.set(Val::Str("alpha_by_name".into()),e.get("alpha")?)?;d})?;d});
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
