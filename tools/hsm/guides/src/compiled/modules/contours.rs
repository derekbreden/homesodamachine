//! Guide recipe: `tools/install-guide/contours.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("hashlib", rt.import_module("hashlib")?)?;
    e.set("json", rt.import_module("json")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("subprocess", rt.import_module("subprocess")?)?;
    e.set("ET", rt.import_module("xml.etree.ElementTree")?)?;
    let mod2 = rt.import_module("PIL")?;
    e.set("Image", rt.member("PIL", "Image")?)?;
    // glass_lip
    e.set("glass_lip", {
        let params = vec![("box".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned3 = {
                let mut s = Vec::new();
                s.push(Val::Int(1i64));
                s.push(unary("neg", Val::Float(1.8f64))?);
                s.push(Val::Float(0.67f64));
                Val::tuple(s)
            };
            e.set("direction", assigned3.clone())?;
            // unit
            e.set("unit", {
                let params = vec![("v".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned4 = {
                        let fun7 = e.get("math")?.attr("sqrt")?;
                        let mut args5 = Vec::new();
                        let mut kw6 = Vec::new();
                        args5.push({
                            let fun10 = e.get("sum")?;
                            let mut args8 = Vec::new();
                            let mut kw9 = Vec::new();
                            args8.push({
                                let e = e.child();
                                let out11 = Val::list(vec![]);
                                for item12 in e.get("v")?.iter()? {
                                    e.set("a", item12)?;
                                    out11.attr("append")?.call(
                                        vec![binary("mul", e.get("a")?, e.get("a")?)?],
                                        vec![],
                                    )?;
                                }
                                out11
                            });
                            fun10.call(args8, kw9)?
                        });
                        fun7.call(args5, kw6)?
                    };
                    e.set("length", assigned4.clone())?;
                    return Ok({
                        let e = e.child();
                        let out13 = Val::list(vec![]);
                        for item14 in e.get("v")?.iter()? {
                            e.set("a", item14)?;
                            out13.attr("append")?.call(
                                vec![binary("truediv", e.get("a")?, e.get("length")?)?],
                                vec![],
                            )?;
                        }
                        out13
                    });
                    Ok(Val::None)
                })
            })?;
            // cross
            e.set("cross", {
                let params = vec![("a".into(), None, false), ("b".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    return Ok({
                        let mut s = Vec::new();
                        s.push(binary(
                            "sub",
                            binary(
                                "mul",
                                e.get("a")?.get(Val::Int(1i64))?,
                                e.get("b")?.get(Val::Int(2i64))?,
                            )?,
                            binary(
                                "mul",
                                e.get("a")?.get(Val::Int(2i64))?,
                                e.get("b")?.get(Val::Int(1i64))?,
                            )?,
                        )?);
                        s.push(binary(
                            "sub",
                            binary(
                                "mul",
                                e.get("a")?.get(Val::Int(2i64))?,
                                e.get("b")?.get(Val::Int(0i64))?,
                            )?,
                            binary(
                                "mul",
                                e.get("a")?.get(Val::Int(0i64))?,
                                e.get("b")?.get(Val::Int(2i64))?,
                            )?,
                        )?);
                        s.push(binary(
                            "sub",
                            binary(
                                "mul",
                                e.get("a")?.get(Val::Int(0i64))?,
                                e.get("b")?.get(Val::Int(1i64))?,
                            )?,
                            binary(
                                "mul",
                                e.get("a")?.get(Val::Int(1i64))?,
                                e.get("b")?.get(Val::Int(0i64))?,
                            )?,
                        )?);
                        Val::list(s)
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned15 = {
                let fun18 = e.get("unit")?;
                let mut args16 = Vec::new();
                let mut kw17 = Vec::new();
                args16.push(e.get("direction")?);
                fun18.call(args16, kw17)?
            };
            e.set("direction", assigned15.clone())?;
            let assigned19 = {
                let fun22 = e.get("unit")?;
                let mut args20 = Vec::new();
                let mut kw21 = Vec::new();
                args20.push({
                    let fun25 = e.get("cross")?;
                    let mut args23 = Vec::new();
                    let mut kw24 = Vec::new();
                    args23.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        Val::tuple(s)
                    });
                    args23.push(e.get("direction")?);
                    fun25.call(args23, kw24)?
                });
                fun22.call(args20, kw21)?
            };
            e.set("right", assigned19.clone())?;
            let assigned26 = {
                let fun29 = e.get("cross")?;
                let mut args27 = Vec::new();
                let mut kw28 = Vec::new();
                args27.push(e.get("direction")?);
                args27.push(e.get("right")?);
                fun29.call(args27, kw28)?
            };
            e.set("up", assigned26.clone())?;
            let assigned30 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("points", assigned30.clone())?;
            let assigned31 = e.get("box")?;
            let unpack32 = unpack(assigned31.clone(), 4)?;
            e.set("x", unpack32[0].clone())?;
            e.set("y", unpack32[1].clone())?;
            e.set("w", unpack32[2].clone())?;
            e.set("h", unpack32[3].clone())?;
            for item33 in {
                let fun67 = e.get("range")?;
                let mut args65 = Vec::new();
                let mut kw66 = Vec::new();
                args65.push(Val::Int(129i64));
                fun67.call(args65, kw66)?
            }
            .iter()?
            {
                e.set("i", item33)?;
                let assigned34 = binary(
                    "truediv",
                    binary(
                        "mul",
                        binary("mul", e.get("i")?, Val::Int(2i64))?,
                        e.get("math")?.attr("pi")?,
                    )?,
                    Val::Int(128i64),
                )?;
                e.set("angle", assigned34.clone())?;
                let assigned35 = {
                    let mut s = Vec::new();
                    s.push(binary("mul", Val::Int(37i64), {
                        let fun38 = e.get("math")?.attr("cos")?;
                        let mut args36 = Vec::new();
                        let mut kw37 = Vec::new();
                        args36.push(e.get("angle")?);
                        fun38.call(args36, kw37)?
                    })?);
                    s.push(binary(
                        "add",
                        binary(
                            "add",
                            unary("neg", Val::Float(133.99672200476698f64))?,
                            binary("mul", Val::Int(37i64), {
                                let fun41 = e.get("math")?.attr("sin")?;
                                let mut args39 = Vec::new();
                                let mut kw40 = Vec::new();
                                args39.push(e.get("angle")?);
                                fun41.call(args39, kw40)?
                            })?,
                        )?,
                        Val::Int(78i64),
                    )?);
                    s.push(binary("sub", Val::Int(104i64), Val::Int(119i64))?);
                    Val::tuple(s)
                };
                e.set("delta", assigned35.clone())?;
                let assigned42 = binary(
                    "add",
                    Val::Int(800i64),
                    binary(
                        "truediv",
                        binary(
                            "mul",
                            {
                                let fun45 = e.get("sum")?;
                                let mut args43 = Vec::new();
                                let mut kw44 = Vec::new();
                                args43.push({
                                    let e = e.child();
                                    let out46 = Val::list(vec![]);
                                    for item47 in {
                                        let fun50 = e.get("zip")?;
                                        let mut args48 = Vec::new();
                                        let mut kw49 = Vec::new();
                                        args48.push(e.get("delta")?);
                                        args48.push(e.get("right")?);
                                        fun50.call(args48, kw49)?
                                    }
                                    .iter()?
                                    {
                                        let unpack51 = unpack(item47, 2)?;
                                        e.set("a", unpack51[0].clone())?;
                                        e.set("b", unpack51[1].clone())?;
                                        out46.attr("append")?.call(
                                            vec![binary("mul", e.get("a")?, e.get("b")?)?],
                                            vec![],
                                        )?;
                                    }
                                    out46
                                });
                                fun45.call(args43, kw44)?
                            },
                            Val::Int(1500i64),
                        )?,
                        Val::Int(280i64),
                    )?,
                )?;
                e.set("px", assigned42.clone())?;
                let assigned52 = binary(
                    "sub",
                    Val::Int(750i64),
                    binary(
                        "truediv",
                        binary(
                            "mul",
                            {
                                let fun55 = e.get("sum")?;
                                let mut args53 = Vec::new();
                                let mut kw54 = Vec::new();
                                args53.push({
                                    let e = e.child();
                                    let out56 = Val::list(vec![]);
                                    for item57 in {
                                        let fun60 = e.get("zip")?;
                                        let mut args58 = Vec::new();
                                        let mut kw59 = Vec::new();
                                        args58.push(e.get("delta")?);
                                        args58.push(e.get("up")?);
                                        fun60.call(args58, kw59)?
                                    }
                                    .iter()?
                                    {
                                        let unpack61 = unpack(item57, 2)?;
                                        e.set("a", unpack61[0].clone())?;
                                        e.set("b", unpack61[1].clone())?;
                                        out56.attr("append")?.call(
                                            vec![binary("mul", e.get("a")?, e.get("b")?)?],
                                            vec![],
                                        )?;
                                    }
                                    out56
                                });
                                fun55.call(args53, kw54)?
                            },
                            Val::Int(1500i64),
                        )?,
                        Val::Int(280i64),
                    )?,
                )?;
                e.set("py", assigned52.clone())?;
                {
                    let fun64 = e.get("points")?.attr("append")?;
                    let mut args62 = Vec::new();
                    let mut kw63 = Vec::new();
                    args62.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            e.get("x")?,
                            binary(
                                "truediv",
                                binary("mul", e.get("px")?, e.get("w")?)?,
                                Val::Int(1600i64),
                            )?,
                        )?);
                        s.push(binary(
                            "add",
                            e.get("y")?,
                            binary(
                                "truediv",
                                binary("mul", e.get("py")?, e.get("h")?)?,
                                Val::Int(1500i64),
                            )?,
                        )?);
                        Val::tuple(s)
                    });
                    fun64.call(args62, kw63)?
                };
            }
            return Ok(binary(
                "add",
                binary("add", Val::Str("M".into()), {
                    let fun70 = Val::Str("L".into()).attr("join")?;
                    let mut args68 = Vec::new();
                    let mut kw69 = Vec::new();
                    args68.push({
                        let e = e.child();
                        let out71 = Val::list(vec![]);
                        for item72 in e.get("points")?.iter()? {
                            let unpack73 = unpack(item72, 2)?;
                            e.set("px", unpack73[0].clone())?;
                            e.set("py", unpack73[1].clone())?;
                            out71.attr("append")?.call(
                                vec![{
                                    let mut str74 = String::new();
                                    str74.push_str(&format(
                                        &e.get("px")?,
                                        &val_string({
                                            let mut str75 = String::new();
                                            str75.push_str(".3f");
                                            Val::Str(str75)
                                        })?,
                                    )?);
                                    str74.push_str(" ");
                                    str74.push_str(&format(
                                        &e.get("py")?,
                                        &val_string({
                                            let mut str76 = String::new();
                                            str76.push_str(".3f");
                                            Val::Str(str76)
                                        })?,
                                    )?);
                                    Val::Str(str74)
                                }],
                                vec![],
                            )?;
                        }
                        out71
                    });
                    fun70.call(args68, kw69)?
                })?,
                Val::Str("Z".into()),
            )?);
            Ok(Val::None)
        })
    })?;
    let assigned77 = {
        let fun80 = {
            let fun83 = e.get("Path")?;
            let mut args81 = Vec::new();
            let mut kw82 = Vec::new();
            args81.push(e.get("__file__")?);
            fun83.call(args81, kw82)?
        }
        .attr("resolve")?;
        let mut args78 = Vec::new();
        let mut kw79 = Vec::new();
        fun80.call(args78, kw79)?
    }
    .attr("parents")?
    .get(Val::Int(2i64))?;
    e.set("ROOT", assigned77.clone())?;
    let assigned84 = binary(
        "truediv",
        e.get("ROOT")?,
        Val::Str("hardware/install-guide/assets".into()),
    )?;
    e.set("ART", assigned84.clone())?;
    let assigned85 = binary(
        "truediv",
        e.get("ROOT")?,
        Val::Str("hardware/install-guide/out/contours".into()),
    )?;
    e.set("OUT", assigned85.clone())?;
    let assigned86 = Val::Int(3i64);
    e.set("PAD", assigned86.clone())?;
    let assigned87 = Val::Int(432i64);
    e.set("PPI", assigned87.clone())?;
    // _filter_region
    e.set("_filter_region", {
        let params = vec![
            ("width".into(), None, false),
            ("height".into(), None, false),
            ("stroke".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned88 = {
                let fun91 = e.get("max")?;
                let mut args89 = Vec::new();
                let mut kw90 = Vec::new();
                args89.push(e.get("PAD")?);
                args89.push(binary(
                    "add",
                    e.get("stroke")?,
                    binary("truediv", Val::Int(72i64), e.get("PPI")?)?,
                )?);
                fun91.call(args89, kw90)?
            };
            e.set("margin", assigned88.clone())?;
            return Ok({
                let mut str92 = String::new();
                str92.push_str("filterUnits=\"userSpaceOnUse\" x=\"");
                str92.push_str(&format(&unary("neg", e.get("margin")?)?, &String::new())?);
                str92.push_str("\" y=\"");
                str92.push_str(&format(&unary("neg", e.get("margin")?)?, &String::new())?);
                str92.push_str("\" width=\"");
                str92.push_str(&format(
                    &binary(
                        "add",
                        e.get("width")?,
                        binary("mul", Val::Int(2i64), e.get("margin")?)?,
                    )?,
                    &String::new(),
                )?);
                str92.push_str("\" height=\"");
                str92.push_str(&format(
                    &binary(
                        "add",
                        e.get("height")?,
                        binary("mul", Val::Int(2i64), e.get("margin")?)?,
                    )?,
                    &String::new(),
                )?);
                str92.push_str("\"");
                Val::Str(str92)
            });
            Ok(Val::None)
        })
    })?;
    e.set("Contours.__init__", {
        let params = vec![
            ("self".into(), None, false),
            ("color".into(), None, false),
            ("width".into(), Some(Val::Float(0.6f64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned93 = e.get("color")?;
            e.get("self")?.setattr("color", assigned93.clone())?;
            let assigned94 = e.get("width")?;
            e.get("self")?.setattr("width", assigned94.clone())?;
            let assigned95 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.get("self")?.setattr("pending", assigned95.clone())?;
            let assigned96 = {
                let fun99 = {
                    let fun102 = e.get("hashlib")?.attr("sha256")?;
                    let mut args100 = Vec::new();
                    let mut kw101 = Vec::new();
                    args100.push({
                        let fun105 = {
                            let fun108 = {
                                let fun111 = e.get("Path")?;
                                let mut args109 = Vec::new();
                                let mut kw110 = Vec::new();
                                args109.push(e.get("__file__")?);
                                fun111.call(args109, kw110)?
                            }
                            .attr("with_name")?;
                            let mut args106 = Vec::new();
                            let mut kw107 = Vec::new();
                            args106.push(Val::Str("render-contours.mjs".into()));
                            fun108.call(args106, kw107)?
                        }
                        .attr("read_bytes")?;
                        let mut args103 = Vec::new();
                        let mut kw104 = Vec::new();
                        fun105.call(args103, kw104)?
                    });
                    fun102.call(args100, kw101)?
                }
                .attr("hexdigest")?;
                let mut args97 = Vec::new();
                let mut kw98 = Vec::new();
                fun99.call(args97, kw98)?
            };
            e.get("self")?
                .setattr("renderer_digest", assigned96.clone())?;
            {
                let fun114 = e.get("OUT")?.attr("mkdir")?;
                let mut args112 = Vec::new();
                let mut kw113 = Vec::new();
                kw113.push(("parents".into(), Val::Bool(true)));
                kw113.push(("exist_ok".into(), Val::Bool(true)));
                fun114.call(args112, kw113)?
            };
            Ok(Val::None)
        })
    })?;
    e.set("Contours.picture",{let params=vec![("self".into(),None,false),("source".into(),None,false),("bounds".into(),None,false),("iw".into(),None,false),("ih".into(),None,false),("fade_crops".into(),Some(Val::Bool(true)),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned115=e.get("bounds")?;let unpack116=unpack(assigned115.clone(),4)?;e.set("a",unpack116[0].clone())?;e.set("b",unpack116[1].clone())?;e.set("c",unpack116[2].clone())?;e.set("d",unpack116[3].clone())?;
let assigned117=binary("truediv",e.get("iw")?,binary("sub",e.get("c")?,e.get("a")?)?)?;e.set("scale",assigned117.clone())?;
let assigned118={let fun121=e.get("Image")?.attr("open")?;let mut args119=Vec::new();let mut kw120=Vec::new();args119.push(e.get("source")?);fun121.call(args119,kw120)?}.attr("size")?;e.set("source_size",assigned118.clone())?;
let assigned122={let mut s=Vec::new();s.push(binary("sub",e.get("PAD")?,binary("mul",e.get("a")?,e.get("scale")?)?)?);s.push(binary("sub",e.get("PAD")?,binary("mul",e.get("b")?,e.get("scale")?)?)?);Val::tuple(s)};let unpack123=unpack(assigned122.clone(),2)?;e.set("x",unpack123[0].clone())?;e.set("y",unpack123[1].clone())?;
let assigned124={let mut s=Vec::new();s.push(binary("mul",e.get("source_size")?.get(Val::Int(0i64))?,e.get("scale")?)?);s.push(binary("mul",e.get("source_size")?.get(Val::Int(1i64))?,e.get("scale")?)?);Val::tuple(s)};let unpack125=unpack(assigned124.clone(),2)?;e.set("w",unpack125[0].clone())?;e.set("h",unpack125[1].clone())?;
let assigned126={let mut s=Vec::new();s.push(binary("add",e.get("iw")?,binary("mul",Val::Int(2i64),e.get("PAD")?)?)?);s.push(binary("add",e.get("ih")?,binary("mul",Val::Int(2i64),e.get("PAD")?)?)?);Val::tuple(s)};let unpack127=unpack(assigned126.clone(),2)?;e.set("pw",unpack127[0].clone())?;e.set("ph",unpack127[1].clone())?;
let assigned128={let mut s=Vec::new();s.push({let fun131=e.get("math")?.attr("ceil")?;let mut args129=Vec::new();let mut kw130=Vec::new();args129.push(binary("truediv",binary("mul",e.get("pw")?,e.get("PPI")?)?,Val::Int(72i64))?);fun131.call(args129,kw130)?});s.push({let fun134=e.get("math")?.attr("ceil")?;let mut args132=Vec::new();let mut kw133=Vec::new();args132.push(binary("truediv",binary("mul",e.get("ph")?,e.get("PPI")?)?,Val::Int(72i64))?);fun134.call(args132,kw133)?});Val::tuple(s)};e.set("pixels",assigned128.clone())?;
let assigned135={let fun138=e.get("_filter_region")?;let mut args136=Vec::new();let mut kw137=Vec::new();args136.push(e.get("pw")?);args136.push(e.get("ph")?);args136.push(e.get("self")?.attr("width")?);fun138.call(args136,kw137)?};e.set("region",assigned135.clone())?;
let assigned139={let mut str140=String::new();str140.push_str("<image x=\"");str140.push_str(&format(&e.get("x")?,&String::new())?);str140.push_str("\" y=\"");str140.push_str(&format(&e.get("y")?,&String::new())?);str140.push_str("\" width=\"");str140.push_str(&format(&e.get("w")?,&String::new())?);str140.push_str("\" height=\"");str140.push_str(&format(&e.get("h")?,&String::new())?);str140.push_str("\" href=\"");str140.push_str(&format(&{let fun143=e.get("source")?.attr("as_uri")?;let mut args141=Vec::new();let mut kw142=Vec::new();fun143.call(args141,kw142)?},&String::new())?);str140.push_str("\"/>");Val::Str(str140)};e.set("raw",assigned139.clone())?;
let assigned144=e.get("raw")?;e.set("silhouette",assigned144.clone())?;
let assigned145=Val::Str("".into());e.set("lip",assigned145.clone())?;
let assigned146={let fun149={let fun152=e.get("hashlib")?.attr("sha256")?;let mut args150=Vec::new();let mut kw151=Vec::new();args150.push({let fun155=e.get("source")?.attr("read_bytes")?;let mut args153=Vec::new();let mut kw154=Vec::new();fun155.call(args153,kw154)?});fun152.call(args150,kw151)?}.attr("hexdigest")?;let mut args147=Vec::new();let mut kw148=Vec::new();fun149.call(args147,kw148)?};e.set("source_digest",assigned146.clone())?;
let assigned156={let mut s=Vec::new();s.push(e.get("source_digest")?);Val::list(s)};e.set("source_digests",assigned156.clone())?;
let assigned157=Val::Str("".into());e.set("component_outline",assigned157.clone())?;
let assigned158=Val::Str("".into());e.set("component_defs",assigned158.clone())?;
if {let v159=e.get("source")?.attr("name")?;let v160=Val::Str("opening.png".into());Val::Bool(compare("eq",v159.clone(),v160.clone())?.truthy()?)}.truthy()? {
let assigned161={let fun164={let fun167=e.get("ET")?.attr("parse")?;let mut args165=Vec::new();let mut kw166=Vec::new();args165.push({let fun170=e.get("source")?.attr("with_name")?;let mut args168=Vec::new();let mut kw169=Vec::new();args168.push(Val::Str("opening-faucet-outline.svg".into()));fun170.call(args168,kw169)?});fun167.call(args165,kw166)?}.attr("getroot")?;let mut args162=Vec::new();let mut kw163=Vec::new();fun164.call(args162,kw163)?};e.set("overlay",assigned161.clone())?;
if {let v171=e.get("overlay")?.attr("attrib")?.get(Val::Str("data-source-sha256".into()))?;let v172=e.get("source_digest")?;Val::Bool(compare("ne",v171.clone(),v172.clone())?.truthy()?)}.truthy()? {
anyhow::bail!("{}",val_string({let fun175=e.get("ValueError")?;let mut args173=Vec::new();let mut kw174=Vec::new();args173.push(Val::Str("Opening artwork no longer matches its component outline".into()));fun175.call(args173,kw174)?})?);
}
if {let v185={let fun178=e.get("tuple")?;let mut args176=Vec::new();let mut kw177=Vec::new();args176.push({let fun181=e.get("map")?;let mut args179=Vec::new();let mut kw180=Vec::new();args179.push(e.get("float")?);args179.push({let fun184=e.get("overlay")?.attr("attrib")?.get(Val::Str("viewBox".into()))?.attr("split")?;let mut args182=Vec::new();let mut kw183=Vec::new();fun184.call(args182,kw183)?});fun181.call(args179,kw180)?});fun178.call(args176,kw177)?};let v186={let mut s=Vec::new();s.push(Val::Int(0i64));s.push(Val::Int(0i64));s.extend(e.get("source_size")?.iter()?);Val::tuple(s)};Val::Bool(compare("ne",v185.clone(),v186.clone())?.truthy()?)}.truthy()? {
anyhow::bail!("{}",val_string({let fun189=e.get("ValueError")?;let mut args187=Vec::new();let mut kw188=Vec::new();args187.push(Val::Str("Opening component outline uses a different coordinate frame".into()));fun189.call(args187,kw188)?})?);
}
let assigned190={let fun193=Val::Str("".into()).attr("join")?;let mut args191=Vec::new();let mut kw192=Vec::new();args191.push({let e=e.child();let out194=Val::list(vec![]);for item195 in {let fun198=e.get("overlay")?.attr("iter")?;let mut args196=Vec::new();let mut kw197=Vec::new();args196.push(Val::Str("{http://www.w3.org/2000/svg}path".into()));fun198.call(args196,kw197)?}.iter()? {e.set("node",item195)?;out194.attr("append")?.call(vec![{let mut str199=String::new();str199.push_str("<path d=\"");str199.push_str(&format(&e.get("node")?.attr("attrib")?.get(Val::Str("d".into()))?,&String::new())?);str199.push_str("\"/>");Val::Str(str199)}],vec![])?;}out194});fun193.call(args191,kw192)?};e.set("paths",assigned190.clone())?;
let assigned200={let mut str201=String::new();str201.push_str("<filter id=\"component-interior\" ");str201.push_str(&format(&e.get("region")?,&String::new())?);str201.push_str(" color-interpolation-filters=\"sRGB\">\n              <feComponentTransfer in=\"SourceAlpha\" result=\"solid\"><feFuncA type=\"linear\" slope=\"40\"/></feComponentTransfer>\n              <feMorphology in=\"solid\" operator=\"erode\" radius=\"");str201.push_str(&format(&e.get("self")?.attr("width")?,&String::new())?);str201.push_str("\" result=\"inside\"/>\n              <feFlood flood-color=\"white\"/><feComposite in2=\"inside\" operator=\"in\"/>\n            </filter>\n            <mask id=\"component-mask\" maskUnits=\"userSpaceOnUse\" x=\"0\" y=\"0\" width=\"");str201.push_str(&format(&e.get("pw")?,&String::new())?);str201.push_str("\" height=\"");str201.push_str(&format(&e.get("ph")?,&String::new())?);str201.push_str("\">\n              <g filter=\"url(#component-interior)\">");str201.push_str(&format(&e.get("raw")?,&String::new())?);str201.push_str("</g>\n            </mask>");Val::Str(str201)};e.set("component_defs",assigned200.clone())?;
let assigned202={let mut str203=String::new();str203.push_str("<g mask=\"url(#component-mask)\"><svg x=\"");str203.push_str(&format(&e.get("x")?,&String::new())?);str203.push_str("\" y=\"");str203.push_str(&format(&e.get("y")?,&String::new())?);str203.push_str("\" width=\"");str203.push_str(&format(&e.get("w")?,&String::new())?);str203.push_str("\" height=\"");str203.push_str(&format(&e.get("h")?,&String::new())?);str203.push_str("\" viewBox=\"");str203.push_str(&format(&e.get("overlay")?.attr("attrib")?.get(Val::Str("viewBox".into()))?,&String::new())?);str203.push_str("\"><g fill=\"none\" stroke=\"");str203.push_str(&format(&e.get("self")?.attr("color")?,&String::new())?);str203.push_str("\" stroke-width=\"");str203.push_str(&format(&binary("truediv",e.get("self")?.attr("width")?,e.get("scale")?)?,&String::new())?);str203.push_str("\" stroke-linejoin=\"round\" stroke-linecap=\"round\">");str203.push_str(&format(&e.get("paths")?,&String::new())?);str203.push_str("</g></svg></g>");Val::Str(str203)};e.set("component_outline",assigned202.clone())?;
}
if {let v204=e.get("source")?.attr("name")?;let v205=Val::Str("pour-base.png".into());Val::Bool(compare("eq",v204.clone(),v205.clone())?.truthy()?)}.truthy()? {
let assigned206=binary("truediv",e.get("source")?.attr("parent")?,Val::Str("pour-glass-mask.png".into()))?;e.set("mask",assigned206.clone())?;
{let fun209=e.get("source_digests")?.attr("append")?;let mut args207=Vec::new();let mut kw208=Vec::new();args207.push({let fun212={let fun215=e.get("hashlib")?.attr("sha256")?;let mut args213=Vec::new();let mut kw214=Vec::new();args213.push({let fun218=e.get("mask")?.attr("read_bytes")?;let mut args216=Vec::new();let mut kw217=Vec::new();fun218.call(args216,kw217)?});fun215.call(args213,kw214)?}.attr("hexdigest")?;let mut args210=Vec::new();let mut kw211=Vec::new();fun212.call(args210,kw211)?});fun209.call(args207,kw208)?};
e.set("silhouette",binary("add",e.get("silhouette")?,{let mut str219=String::new();str219.push_str("<image x=\"");str219.push_str(&format(&e.get("x")?,&String::new())?);str219.push_str("\" y=\"");str219.push_str(&format(&e.get("y")?,&String::new())?);str219.push_str("\" width=\"");str219.push_str(&format(&e.get("w")?,&String::new())?);str219.push_str("\" height=\"");str219.push_str(&format(&e.get("h")?,&String::new())?);str219.push_str("\" href=\"");str219.push_str(&format(&{let fun222=e.get("mask")?.attr("as_uri")?;let mut args220=Vec::new();let mut kw221=Vec::new();fun222.call(args220,kw221)?},&String::new())?);str219.push_str("\"/>");Val::Str(str219)})?)?;
let assigned223={let mut str224=String::new();str224.push_str("<path d=\"");str224.push_str(&format(&{let fun227=e.get("glass_lip")?;let mut args225=Vec::new();let mut kw226=Vec::new();args225.push({let mut s=Vec::new();s.push(e.get("x")?);s.push(e.get("y")?);s.push(e.get("w")?);s.push(e.get("h")?);Val::tuple(s)});fun227.call(args225,kw226)?},&String::new())?);str224.push_str("\" fill=\"none\" stroke=\"");str224.push_str(&format(&e.get("self")?.attr("color")?,&String::new())?);str224.push_str("\" stroke-width=\"");str224.push_str(&format(&e.get("self")?.attr("width")?,&String::new())?);str224.push_str("\"/>");Val::Str(str224)};e.set("lip",assigned223.clone())?;
}
let assigned228={let fun231={let fun234=e.get("Image")?.attr("open")?;let mut args232=Vec::new();let mut kw233=Vec::new();args232.push(e.get("source")?);fun234.call(args232,kw233)?}.attr("convert")?;let mut args229=Vec::new();let mut kw230=Vec::new();args229.push(Val::Str("RGBA".into()));fun231.call(args229,kw230)?};e.set("im",assigned228.clone())?;
let assigned235={let fun238=e.get("im")?.attr("getchannel")?;let mut args236=Vec::new();let mut kw237=Vec::new();args236.push(Val::Str("A".into()));fun238.call(args236,kw237)?};e.set("alpha",assigned235.clone())?;
let assigned239={let mut s=Vec::new();s.push({let fun242=e.get("max")?;let mut args240=Vec::new();let mut kw241=Vec::new();args240.push(Val::Int(0i64));args240.push(e.get("a")?);fun242.call(args240,kw241)?});s.push({let fun245=e.get("max")?;let mut args243=Vec::new();let mut kw244=Vec::new();args243.push(Val::Int(0i64));args243.push(e.get("b")?);fun245.call(args243,kw244)?});s.push({let fun248=e.get("min")?;let mut args246=Vec::new();let mut kw247=Vec::new();args246.push(e.get("im")?.attr("width")?);args246.push(e.get("c")?);fun248.call(args246,kw247)?});s.push({let fun251=e.get("min")?;let mut args249=Vec::new();let mut kw250=Vec::new();args249.push(e.get("im")?.attr("height")?);args249.push(e.get("d")?);fun251.call(args249,kw250)?});Val::tuple(s)};e.set("actual",assigned239.clone())?;
let assigned252=e.get("actual")?;let unpack253=unpack(assigned252.clone(),4)?;e.set("aa",unpack253[0].clone())?;e.set("bb",unpack253[1].clone())?;e.set("cc",unpack253[2].clone())?;e.set("dd",unpack253[3].clone())?;
let assigned254={let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(e.get("aa")?);s.push(e.get("bb")?);s.push(binary("add",e.get("aa")?,Val::Int(1i64))?);s.push(e.get("dd")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("sub",e.get("cc")?,Val::Int(1i64))?);s.push(e.get("bb")?);s.push(e.get("cc")?);s.push(e.get("dd")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("aa")?);s.push(e.get("bb")?);s.push(e.get("cc")?);s.push(binary("add",e.get("bb")?,Val::Int(1i64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("aa")?);s.push(binary("sub",e.get("dd")?,Val::Int(1i64))?);s.push(e.get("cc")?);s.push(e.get("dd")?);Val::tuple(s)});Val::list(s)};e.set("edge_bands",assigned254.clone())?;
let assigned255={let e=e.child();let out256=Val::list(vec![]);for item257 in e.get("edge_bands")?.iter()? {e.set("band",item257)?;out256.attr("append")?.call(vec![{let v269=e.get("fade_crops")?;if v269.truthy()? {{let v267={let fun260=e.get("max")?;let mut args258=Vec::new();let mut kw259=Vec::new();args258.push({let fun263={let fun266=e.get("alpha")?.attr("crop")?;let mut args264=Vec::new();let mut kw265=Vec::new();args264.push(e.get("band")?);fun266.call(args264,kw265)?}.attr("getdata")?;let mut args261=Vec::new();let mut kw262=Vec::new();fun263.call(args261,kw262)?});kw259.push(("default".into(),Val::Int(0i64)));fun260.call(args258,kw259)?};let v268=Val::Int(100i64);Val::Bool(compare("gt",v267.clone(),v268.clone())?.truthy()?)}} else {v269}}],vec![])?;}out256};e.set("cut",assigned255.clone())?;
let assigned270={let mut s=Vec::new();s.push(binary("truediv",{let fun273=e.get("min")?;let mut args271=Vec::new();let mut kw272=Vec::new();args271.push(Val::Float(3.2f64));args271.push(binary("mul",e.get("iw")?,Val::Float(0.035f64))?);fun273.call(args271,kw272)?},e.get("iw")?)?);s.push(binary("truediv",{let fun276=e.get("min")?;let mut args274=Vec::new();let mut kw275=Vec::new();args274.push(Val::Float(3.2f64));args274.push(binary("mul",e.get("ih")?,Val::Float(0.05f64))?);fun276.call(args274,kw275)?},e.get("ih")?)?);Val::tuple(s)};let unpack277=unpack(assigned270.clone(),2)?;e.set("fx",unpack277[0].clone())?;e.set("fy",unpack277[1].clone())?;
let assigned278={let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Int(0i64));s.push(if e.get("cut")?.get(Val::Int(0i64))?.truthy()? {Val::Str("black".into())} else {Val::Str("white".into())});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("fx")?);s.push(Val::Str("white".into()));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("sub",Val::Int(1i64),e.get("fx")?)?);s.push(Val::Str("white".into()));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Int(1i64));s.push(if e.get("cut")?.get(Val::Int(1i64))?.truthy()? {Val::Str("black".into())} else {Val::Str("white".into())});Val::tuple(s)});Val::list(s)};e.set("stops_x",assigned278.clone())?;
let assigned279={let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Int(0i64));s.push(if e.get("cut")?.get(Val::Int(2i64))?.truthy()? {Val::Str("black".into())} else {Val::Str("white".into())});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("fy")?);s.push(Val::Str("white".into()));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("sub",Val::Int(1i64),e.get("fy")?)?);s.push(Val::Str("white".into()));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Int(1i64));s.push(if e.get("cut")?.get(Val::Int(3i64))?.truthy()? {Val::Str("black".into())} else {Val::Str("white".into())});Val::tuple(s)});Val::list(s)};e.set("stops_y",assigned279.clone())?;
let assigned280={let mut s=Vec::new();s.push(if e.get("cut")?.get(Val::Int(0i64))?.truthy()? {e.get("PAD")?} else {Val::Int(0i64)});s.push(if e.get("cut")?.get(Val::Int(1i64))?.truthy()? {binary("add",e.get("PAD")?,e.get("iw")?)?} else {e.get("pw")?});Val::tuple(s)};let unpack281=unpack(assigned280.clone(),2)?;e.set("mx0",unpack281[0].clone())?;e.set("mx1",unpack281[1].clone())?;
let assigned282={let mut s=Vec::new();s.push(if e.get("cut")?.get(Val::Int(2i64))?.truthy()? {e.get("PAD")?} else {Val::Int(0i64)});s.push(if e.get("cut")?.get(Val::Int(3i64))?.truthy()? {binary("add",e.get("PAD")?,e.get("ih")?)?} else {e.get("ph")?});Val::tuple(s)};let unpack283=unpack(assigned282.clone(),2)?;e.set("my0",unpack283[0].clone())?;e.set("my1",unpack283[1].clone())?;
// stops
e.set("stops",{let params=vec![("values".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let fun286=Val::Str("".into()).attr("join")?;let mut args284=Vec::new();let mut kw285=Vec::new();args284.push({let e=e.child();let out287=Val::list(vec![]);for item288 in e.get("values")?.iter()? {let unpack289=unpack(item288,2)?;e.set("offset",unpack289[0].clone())?;e.set("color",unpack289[1].clone())?;out287.attr("append")?.call(vec![{let mut str290=String::new();str290.push_str("<stop offset=\"");str290.push_str(&format(&e.get("offset")?,&String::new())?);str290.push_str("\" stop-color=\"");str290.push_str(&format(&e.get("color")?,&String::new())?);str290.push_str("\"/>");Val::Str(str290)}],vec![])?;}out287});fun286.call(args284,kw285)?});
Ok(Val::None)})})?;
let assigned291={let mut str292=String::new();str292.push_str("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"");str292.push_str(&format(&e.get("pixels")?.get(Val::Int(0i64))?,&String::new())?);str292.push_str("\" height=\"");str292.push_str(&format(&e.get("pixels")?.get(Val::Int(1i64))?,&String::new())?);str292.push_str("\" viewBox=\"0 0 ");str292.push_str(&format(&e.get("pw")?,&String::new())?);str292.push_str(" ");str292.push_str(&format(&e.get("ph")?,&String::new())?);str292.push_str("\"><defs>");str292.push_str(&format(&e.get("component_defs")?,&String::new())?);str292.push_str("\n        <filter id=\"contour\" ");str292.push_str(&format(&e.get("region")?,&String::new())?);str292.push_str(" color-interpolation-filters=\"sRGB\">\n          <feComponentTransfer in=\"SourceAlpha\" result=\"solid\"><feFuncA type=\"linear\" slope=\"40\"/></feComponentTransfer>\n          <feMorphology operator=\"dilate\" radius=\"");str292.push_str(&format(&e.get("self")?.attr("width")?,&String::new())?);str292.push_str("\" result=\"outside\"/>\n          <feComposite in=\"outside\" in2=\"solid\" operator=\"out\" result=\"edge\"/>\n          <feFlood flood-color=\"");str292.push_str(&format(&e.get("self")?.attr("color")?,&String::new())?);str292.push_str("\"/><feComposite in2=\"edge\" operator=\"in\"/>\n        </filter>\n        <linearGradient id=\"fade-x\">");str292.push_str(&format(&{let fun295=e.get("stops")?;let mut args293=Vec::new();let mut kw294=Vec::new();args293.push(e.get("stops_x")?);fun295.call(args293,kw294)?},&String::new())?);str292.push_str("</linearGradient>\n        <linearGradient id=\"fade-y\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\">");str292.push_str(&format(&{let fun298=e.get("stops")?;let mut args296=Vec::new();let mut kw297=Vec::new();args296.push(e.get("stops_y")?);fun298.call(args296,kw297)?},&String::new())?);str292.push_str("</linearGradient>\n        <mask id=\"mx\" maskUnits=\"userSpaceOnUse\" x=\"0\" y=\"0\" width=\"");str292.push_str(&format(&e.get("pw")?,&String::new())?);str292.push_str("\" height=\"");str292.push_str(&format(&e.get("ph")?,&String::new())?);str292.push_str("\">\n          <rect x=\"");str292.push_str(&format(&e.get("mx0")?,&String::new())?);str292.push_str("\" y=\"0\" width=\"");str292.push_str(&format(&binary("sub",e.get("mx1")?,e.get("mx0")?)?,&String::new())?);str292.push_str("\" height=\"");str292.push_str(&format(&e.get("ph")?,&String::new())?);str292.push_str("\" fill=\"url(#fade-x)\"/>\n        </mask>\n        <mask id=\"my\" maskUnits=\"userSpaceOnUse\" x=\"0\" y=\"0\" width=\"");str292.push_str(&format(&e.get("pw")?,&String::new())?);str292.push_str("\" height=\"");str292.push_str(&format(&e.get("ph")?,&String::new())?);str292.push_str("\">\n          <rect x=\"0\" y=\"");str292.push_str(&format(&e.get("my0")?,&String::new())?);str292.push_str("\" width=\"");str292.push_str(&format(&e.get("pw")?,&String::new())?);str292.push_str("\" height=\"");str292.push_str(&format(&binary("sub",e.get("my1")?,e.get("my0")?)?,&String::new())?);str292.push_str("\" fill=\"url(#fade-y)\"/>\n        </mask>\n        </defs><g mask=\"url(#mx)\"><g mask=\"url(#my)\"><g filter=\"url(#contour)\">");str292.push_str(&format(&e.get("silhouette")?,&String::new())?);str292.push_str("</g>");str292.push_str(&format(&e.get("raw")?,&String::new())?);str292.push_str(&format(&e.get("lip")?,&String::new())?);str292.push_str(&format(&e.get("component_outline")?,&String::new())?);str292.push_str("</g></g>\n        </svg>");Val::Str(str292)};e.set("body",assigned291.clone())?;
let assigned299={let fun302={let fun305=e.get("hashlib")?.attr("sha256")?;let mut args303=Vec::new();let mut kw304=Vec::new();args303.push({let fun308=binary("add",binary("add",e.get("body")?,{let fun311=Val::Str("".into()).attr("join")?;let mut args309=Vec::new();let mut kw310=Vec::new();args309.push(e.get("source_digests")?);fun311.call(args309,kw310)?})?,e.get("self")?.attr("renderer_digest")?)?.attr("encode")?;let mut args306=Vec::new();let mut kw307=Vec::new();fun308.call(args306,kw307)?});fun305.call(args303,kw304)?}.attr("hexdigest")?;let mut args300=Vec::new();let mut kw301=Vec::new();fun302.call(args300,kw301)?}.get(Val::Slice{start:None,stop:Some(Val::Int(20i64).integer()?),step:1})?;e.set("digest",assigned299.clone())?;
let assigned312=binary("truediv",e.get("OUT")?,{let mut str313=String::new();str313.push_str(&format(&e.get("digest")?,&String::new())?);str313.push_str(".png");Val::Str(str313)})?;e.set("target",assigned312.clone())?;
if unary("not",{let fun316=e.get("target")?.attr("exists")?;let mut args314=Vec::new();let mut kw315=Vec::new();fun316.call(args314,kw315)?})?.truthy()? {
let assigned317=binary("truediv",e.get("OUT")?,{let mut str318=String::new();str318.push_str(&format(&e.get("digest")?,&String::new())?);str318.push_str(".svg");Val::Str(str318)})?;e.set("page",assigned317.clone())?;
{let fun321=e.get("page")?.attr("write_text")?;let mut args319=Vec::new();let mut kw320=Vec::new();args319.push(binary("add",{let fun324=Val::Str("\n".into()).attr("join")?;let mut args322=Vec::new();let mut kw323=Vec::new();args322.push({let e=e.child();let out325=Val::list(vec![]);for item326 in {let fun329=e.get("body")?.attr("splitlines")?;let mut args327=Vec::new();let mut kw328=Vec::new();fun329.call(args327,kw328)?}.iter()? {e.set("line",item326)?;out325.attr("append")?.call(vec![{let fun332=e.get("line")?.attr("rstrip")?;let mut args330=Vec::new();let mut kw331=Vec::new();fun332.call(args330,kw331)?}],vec![])?;}out325});fun324.call(args322,kw323)?},Val::Str("\n".into()))?);fun321.call(args319,kw320)?};
{let fun335=e.get("self")?.attr("pending")?.attr("append")?;let mut args333=Vec::new();let mut kw334=Vec::new();args333.push({let d=Val::dict(vec![]);d.set(Val::Str("svg".into()),{let fun338=e.get("str")?;let mut args336=Vec::new();let mut kw337=Vec::new();args336.push(e.get("page")?);fun338.call(args336,kw337)?})?;d.set(Val::Str("out".into()),{let fun341=e.get("str")?;let mut args339=Vec::new();let mut kw340=Vec::new();args339.push(e.get("target")?);fun341.call(args339,kw340)?})?;d.set(Val::Str("size".into()),e.get("pixels")?)?;d});fun335.call(args333,kw334)?};
}
return Ok({let mut s=Vec::new();s.push(e.get("target")?);s.push({let mut s=Vec::new();s.push(e.get("pw")?);s.push(e.get("ph")?);Val::tuple(s)});Val::tuple(s)});
Ok(Val::None)})})?;
    e.set("Contours.render", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned342 = binary("truediv", e.get("OUT")?, {
                let mut str343 = String::new();
                str343.push_str("jobs-");
                str343.push_str(&format(
                    &e.get("self")?.attr("color")?.get(Val::Slice {
                        start: Some(Val::Int(1i64).integer()?),
                        stop: None,
                        step: 1,
                    })?,
                    &String::new(),
                )?);
                str343.push_str(".json");
                Val::Str(str343)
            })?;
            e.set("manifest", assigned342.clone())?;
            {
                let fun346 = e.get("manifest")?.attr("write_text")?;
                let mut args344 = Vec::new();
                let mut kw345 = Vec::new();
                args344.push(binary(
                    "add",
                    {
                        let fun349 = e.get("json")?.attr("dumps")?;
                        let mut args347 = Vec::new();
                        let mut kw348 = Vec::new();
                        args347.push(e.get("self")?.attr("pending")?);
                        kw348.push(("indent".into(), Val::Int(2i64)));
                        fun349.call(args347, kw348)?
                    },
                    Val::Str("\n".into()),
                )?);
                fun346.call(args344, kw345)?
            };
            {
                let fun352 = e.get("subprocess")?.attr("run")?;
                let mut args350 = Vec::new();
                let mut kw351 = Vec::new();
                args350.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("node".into()));
                    s.push({
                        let fun355 = e.get("str")?;
                        let mut args353 = Vec::new();
                        let mut kw354 = Vec::new();
                        args353.push({
                            let fun358 = {
                                let fun361 = e.get("Path")?;
                                let mut args359 = Vec::new();
                                let mut kw360 = Vec::new();
                                args359.push(e.get("__file__")?);
                                fun361.call(args359, kw360)?
                            }
                            .attr("with_name")?;
                            let mut args356 = Vec::new();
                            let mut kw357 = Vec::new();
                            args356.push(Val::Str("render-contours.mjs".into()));
                            fun358.call(args356, kw357)?
                        });
                        fun355.call(args353, kw354)?
                    });
                    s.push({
                        let fun364 = e.get("str")?;
                        let mut args362 = Vec::new();
                        let mut kw363 = Vec::new();
                        args362.push(e.get("manifest")?);
                        fun364.call(args362, kw363)?
                    });
                    Val::list(s)
                });
                kw351.push(("cwd".into(), e.get("ROOT")?));
                kw351.push(("check".into(), Val::Bool(true)));
                fun352.call(args350, kw351)?
            };
            Ok(Val::None)
        })
    })?;
    e.set("Contours", rt.python_type("contours", "Contours")?)?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
