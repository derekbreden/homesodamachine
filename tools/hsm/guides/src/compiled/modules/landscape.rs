//! Guide recipe: `tools/install-guide/landscape.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("hashlib", rt.import_module("hashlib")?)?;
    e.set("io", rt.import_module("io")?)?;
    e.set("json", rt.import_module("json")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("re", rt.import_module("re")?)?;
    e.set("subprocess", rt.import_module("subprocess")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    e.set("ET", rt.import_module("xml.etree.ElementTree")?)?;
    let mod2 = rt.import_module("PIL")?;
    e.set("Image", rt.member("PIL", "Image")?)?;
    e.set("ezdxf", rt.import_module("ezdxf")?)?;
    let mod3 = rt.import_module("reportlab.pdfgen")?;
    e.set("canvas", rt.member("reportlab.pdfgen", "canvas")?)?;
    let mod4 = rt.import_module("reportlab.pdfbase")?;
    e.set("pdfmetrics", rt.member("reportlab.pdfbase", "pdfmetrics")?)?;
    let mod5 = rt.import_module("reportlab.pdfbase.ttfonts")?;
    e.set("TTFont", rt.member("reportlab.pdfbase.ttfonts", "TTFont")?)?;
    let mod6 = rt.import_module("reportlab.lib.colors")?;
    e.set("HexColor", rt.member("reportlab.lib.colors", "HexColor")?)?;
    e.set("white", rt.member("reportlab.lib.colors", "white")?)?;
    let mod7 = rt.import_module("reportlab.lib.styles")?;
    e.set(
        "ParagraphStyle",
        rt.member("reportlab.lib.styles", "ParagraphStyle")?,
    )?;
    let mod8 = rt.import_module("reportlab.platypus")?;
    e.set("Paragraph", rt.member("reportlab.platypus", "Paragraph")?)?;
    let mod9 = rt.import_module("reportlab.lib.utils")?;
    e.set(
        "ImageReader",
        rt.member("reportlab.lib.utils", "ImageReader")?,
    )?;
    let mod10 = rt.import_module("contours")?;
    e.set("Contours", rt.member("contours", "Contours")?)?;
    e.set("PAD", rt.member("contours", "PAD")?)?;
    let mod11 = rt.import_module("press")?;
    e.set("BLEED", rt.member("press", "BLEED")?)?;
    e.set("TRIM_W", rt.member("press", "TRIM_W")?)?;
    e.set("TRIM_H", rt.member("press", "TRIM_H")?)?;
    e.set("write_editions", rt.member("press", "write_editions")?)?;
    e.set(
        "make_order_bundle",
        rt.member("press", "make_order_bundle")?,
    )?;
    let assigned12 = {
        let fun15 = {
            let fun18 = e.get("Path")?;
            let mut args16 = Vec::new();
            let mut kw17 = Vec::new();
            args16.push(e.get("__file__")?);
            fun18.call(args16, kw17)?
        }
        .attr("resolve")?;
        let mut args13 = Vec::new();
        let mut kw14 = Vec::new();
        fun15.call(args13, kw14)?
    }
    .attr("parents")?
    .get(Val::Int(2i64))?;
    e.set("ROOT", assigned12.clone())?;
    let assigned19 = binary(
        "truediv",
        e.get("ROOT")?,
        Val::Str("hardware/install-guide".into()),
    )?;
    e.set("DIR", assigned19.clone())?;
    let assigned20 = binary("truediv", e.get("DIR")?, Val::Str("assets".into()))?;
    e.set("ART", assigned20.clone())?;
    let assigned21 = binary("truediv", e.get("DIR")?, Val::Str("out/landscape".into()))?;
    e.set("OUT", assigned21.clone())?;
    let assigned22 = binary(
        "truediv",
        e.get("DIR")?,
        Val::Str("install-guide.pdf".into()),
    )?;
    e.set("PDF", assigned22.clone())?;
    let assigned23 = binary("truediv", e.get("DIR")?, Val::Str("press".into()))?;
    e.set("PRESS_DIR", assigned23.clone())?;
    let assigned24 = binary("truediv", e.get("ROOT")?, Val::Str("output/pdf".into()))?;
    e.set("OUTPUT", assigned24.clone())?;
    let assigned25 = e.get("DIR")?;
    e.set("DOC_OUTPUT", assigned25.clone())?;
    let assigned26 = {
        let mut s = Vec::new();
        s.push(e.get("TRIM_W")?);
        s.push(e.get("TRIM_H")?);
        Val::tuple(s)
    };
    let unpack27 = unpack(assigned26.clone(), 2)?;
    e.set("W", unpack27[0].clone())?;
    e.set("H", unpack27[1].clone())?;
    let assigned28 = {
        let mut s = Vec::new();
        s.push(Val::Int(44i64));
        s.push(binary("sub", e.get("W")?, Val::Int(88i64))?);
        Val::tuple(s)
    };
    let unpack29 = unpack(assigned28.clone(), 2)?;
    e.set("M", unpack29[0].clone())?;
    e.set("CW", unpack29[1].clone())?;
    let assigned30 = {
        let mut s = Vec::new();
        s.push(Val::Int(350i64));
        s.push(binary(
            "sub",
            binary("sub", e.get("W")?, e.get("M")?)?,
            Val::Int(350i64),
        )?);
        Val::tuple(s)
    };
    let unpack31 = unpack(assigned30.clone(), 2)?;
    e.set("RIGHT", unpack31[0].clone())?;
    e.set("RW", unpack31[1].clone())?;
    let assigned32 = {
        let mut s = Vec::new();
        s.push(Val::Str("#1749D1".into()));
        s.push(Val::Str("#10319C".into()));
        s.push(Val::Str("#DCE6FF".into()));
        s.push(Val::Str("#FF9152".into()));
        Val::tuple(s)
    };
    let unpack33 = unpack(assigned32.clone(), 4)?;
    e.set("BLUE", unpack33[0].clone())?;
    e.set("NAVY", unpack33[1].clone())?;
    e.set("ICE", unpack33[2].clone())?;
    e.set("ORANGE", unpack33[3].clone())?;
    let assigned34 = {
        let mut s = Vec::new();
        s.push(Val::Str("#202337".into()));
        s.push(Val::Str("#606A78".into()));
        s.push(Val::Str("#DCE2EB".into()));
        s.push(Val::Str("#D64050".into()));
        Val::tuple(s)
    };
    let unpack35 = unpack(assigned34.clone(), 4)?;
    e.set("INK", unpack35[0].clone())?;
    e.set("MUTED", unpack35[1].clone())?;
    e.set("RULE", unpack35[2].clone())?;
    e.set("CORAL", unpack35[3].clone())?;
    for item36 in {
        let mut s = Vec::new();
        s.push(Val::Str("Regular".into()));
        s.push(Val::Str("Semibold".into()));
        s.push(Val::Str("Bold".into()));
        Val::list(s)
    }
    .iter()?
    {
        e.set("name", item36)?;
        {
            let fun39 = e.get("pdfmetrics")?.attr("registerFont")?;
            let mut args37 = Vec::new();
            let mut kw38 = Vec::new();
            args37.push({
                let fun42 = e.get("TTFont")?;
                let mut args40 = Vec::new();
                let mut kw41 = Vec::new();
                args40.push(e.get("name")?);
                args40.push({
                    let fun45 = e.get("str")?;
                    let mut args43 = Vec::new();
                    let mut kw44 = Vec::new();
                    args43.push(binary(
                        "truediv",
                        binary("truediv", e.get("DIR")?, Val::Str("fonts".into()))?,
                        {
                            let mut str46 = String::new();
                            str46.push_str("Plex-");
                            str46.push_str(&format(&e.get("name")?, &String::new())?);
                            str46.push_str(".ttf");
                            Val::Str(str46)
                        },
                    )?);
                    fun45.call(args43, kw44)?
                });
                fun42.call(args40, kw41)?
            });
            fun39.call(args37, kw38)?
        };
    }
    {
        let fun49 = e.get("pdfmetrics")?.attr("registerFontFamily")?;
        let mut args47 = Vec::new();
        let mut kw48 = Vec::new();
        args47.push(Val::Str("Regular".into()));
        kw48.push(("normal".into(), Val::Str("Regular".into())));
        kw48.push(("bold".into(), Val::Str("Bold".into())));
        kw48.push(("italic".into(), Val::Str("Regular".into())));
        kw48.push(("boldItalic".into(), Val::Str("Bold".into())));
        fun49.call(args47, kw48)?
    };
    let assigned50 = {
        let fun53 = e.get("Contours")?;
        let mut args51 = Vec::new();
        let mut kw52 = Vec::new();
        args51.push(Val::Str("#46515b".into()));
        kw52.push(("width".into(), Val::Float(0.72f64)));
        fun53.call(args51, kw52)?
    };
    e.set("contours", assigned50.clone())?;
    let assigned54 = {
        let fun57 = e.get("io")?.attr("BytesIO")?;
        let mut args55 = Vec::new();
        let mut kw56 = Vec::new();
        fun57.call(args55, kw56)?
    };
    e.set("buffer", assigned54.clone())?;
    let assigned58 = {
        let fun61 = e.get("canvas")?.attr("Canvas")?;
        let mut args59 = Vec::new();
        let mut kw60 = Vec::new();
        args59.push(e.get("buffer")?);
        kw60.push(("pagesize".into(), {
            let mut s = Vec::new();
            s.push(binary(
                "add",
                e.get("W")?,
                binary("mul", Val::Int(2i64), e.get("BLEED")?)?,
            )?);
            s.push(binary(
                "add",
                e.get("H")?,
                binary("mul", Val::Int(2i64), e.get("BLEED")?)?,
            )?);
            Val::tuple(s)
        }));
        kw60.push(("pageCompression".into(), Val::Int(1i64)));
        kw60.push(("invariant".into(), Val::Int(1i64)));
        kw60.push(("initialFontName".into(), Val::Str("Regular".into())));
        fun61.call(args59, kw60)?
    };
    e.set("c", assigned58.clone())?;
    {
        let fun64 = e.get("c")?.attr("setTitle")?;
        let mut args62 = Vec::new();
        let mut kw63 = Vec::new();
        args62.push(Val::Str("Home Soda Machine - Install guide".into()));
        fun64.call(args62, kw63)?
    };
    {
        let fun67 = e.get("c")?.attr("setAuthor")?;
        let mut args65 = Vec::new();
        let mut kw66 = Vec::new();
        args65.push(Val::Str("Derek Bredensteiner".into()));
        fun67.call(args65, kw66)?
    };
    {
        let fun70 = e.get("c")?.attr("setSubject")?;
        let mut args68 = Vec::new();
        let mut kw69 = Vec::new();
        args68.push(Val::Str(
            "Seven steps to the first glass. 32 interior pages. 9 x 7 inch landscape.".into(),
        ));
        fun70.call(args68, kw69)?
    };
    let assigned71 = Val::Int(0i64);
    e.set("page_no", assigned71.clone())?;
    let assigned72 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            Val::list(s)
        });
        s.push({
            let mut s = Vec::new();
            Val::list(s)
        });
        s.push({
            let mut s = Vec::new();
            Val::list(s)
        });
        s.push({
            let mut s = Vec::new();
            Val::list(s)
        });
        Val::tuple(s)
    };
    let unpack73 = unpack(assigned72.clone(), 4)?;
    e.set("checks", unpack73[0].clone())?;
    e.set("image_checks", unpack73[1].clone())?;
    e.set("titles", unpack73[2].clone())?;
    e.set("mount_slot_checks", unpack73[3].clone())?;
    let assigned74 = {
        let fun77 = e.get("json")?.attr("loads")?;
        let mut args75 = Vec::new();
        let mut kw76 = Vec::new();
        args75.push({
            let fun80 = binary(
                "truediv",
                e.get("ART")?,
                Val::Str("print-resolution.json".into()),
            )?
            .attr("read_text")?;
            let mut args78 = Vec::new();
            let mut kw79 = Vec::new();
            fun80.call(args78, kw79)?
        });
        fun77.call(args75, kw76)?
    }
    .get(Val::Str("assets".into()))?;
    e.set("resolutions", assigned74.clone())?;
    let assigned81 = {
        let fun84 = e.get("json")?.attr("loads")?;
        let mut args82 = Vec::new();
        let mut kw83 = Vec::new();
        args82.push({
            let fun87 = binary(
                "truediv",
                e.get("ART")?,
                Val::Str("fill-scene-inputs.json".into()),
            )?
            .attr("read_text")?;
            let mut args85 = Vec::new();
            let mut kw86 = Vec::new();
            fun87.call(args85, kw86)?
        });
        fun84.call(args82, kw83)?
    };
    e.set("FILL", assigned81.clone())?;
    let assigned88 = {
        let fun91 = e.get("tuple")?;
        let mut args89 = Vec::new();
        let mut kw90 = Vec::new();
        args89.push({
            let e = e.child();
            let out92 = Val::list(vec![]);
            for item93 in {
                let mut s = Vec::new();
                s.push(Val::Str("cam".into()));
                s.push(Val::Str("target".into()));
                s.push(Val::Str("span".into()));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("key", item93)?;
                out92.attr("append")?.call(
                    vec![
                        e.get("FILL")?
                            .get(Val::Str("pose".into()))?
                            .get(e.get("key")?)?,
                    ],
                    vec![],
                )?;
            }
            out92
        });
        fun91.call(args89, kw90)?
    };
    e.set("FILL_POSE", assigned88.clone())?;
    // begin_page
    e.set("begin_page", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun96 = e.get("c")?.attr("translate")?;
                let mut args94 = Vec::new();
                let mut kw95 = Vec::new();
                args94.push(e.get("BLEED")?);
                args94.push(e.get("BLEED")?);
                fun96.call(args94, kw95)?
            };
            Ok(Val::None)
        })
    })?;
    // rect
    e.set("rect", {
        let params = vec![
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("w".into(), None, false),
            ("h".into(), None, false),
            ("fill".into(), None, false),
            ("stroke".into(), Some(Val::None), false),
            ("r".into(), Some(Val::Int(0i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun99 = e.get("c")?.attr("setFillColor")?;
                let mut args97 = Vec::new();
                let mut kw98 = Vec::new();
                args97.push({
                    let fun102 = e.get("HexColor")?;
                    let mut args100 = Vec::new();
                    let mut kw101 = Vec::new();
                    args100.push(e.get("fill")?);
                    fun102.call(args100, kw101)?
                });
                fun99.call(args97, kw98)?
            };
            {
                let fun105 = e.get("c")?.attr("setStrokeColor")?;
                let mut args103 = Vec::new();
                let mut kw104 = Vec::new();
                args103.push({
                    let fun108 = e.get("HexColor")?;
                    let mut args106 = Vec::new();
                    let mut kw107 = Vec::new();
                    args106.push({
                        let v109 = e.get("stroke")?;
                        if v109.truthy()? { v109 } else { e.get("fill")? }
                    });
                    fun108.call(args106, kw107)?
                });
                fun105.call(args103, kw104)?
            };
            {
                let fun112 = e.get("c")?.attr("setLineWidth")?;
                let mut args110 = Vec::new();
                let mut kw111 = Vec::new();
                args110.push(Val::Float(0.7f64));
                fun112.call(args110, kw111)?
            };
            if e.get("r")?.truthy()? {
                {
                    let fun115 = e.get("c")?.attr("roundRect")?;
                    let mut args113 = Vec::new();
                    let mut kw114 = Vec::new();
                    args113.push(e.get("x")?);
                    args113.push(binary(
                        "sub",
                        binary("sub", e.get("H")?, e.get("y")?)?,
                        e.get("h")?,
                    )?);
                    args113.push(e.get("w")?);
                    args113.push(e.get("h")?);
                    args113.push(e.get("r")?);
                    kw114.push(("fill".into(), Val::Int(1i64)));
                    kw114.push(("stroke".into(), {
                        let fun118 = e.get("bool")?;
                        let mut args116 = Vec::new();
                        let mut kw117 = Vec::new();
                        args116.push(e.get("stroke")?);
                        fun118.call(args116, kw117)?
                    }));
                    fun115.call(args113, kw114)?
                };
            } else {
                {
                    let fun121 = e.get("c")?.attr("rect")?;
                    let mut args119 = Vec::new();
                    let mut kw120 = Vec::new();
                    args119.push(e.get("x")?);
                    args119.push(binary(
                        "sub",
                        binary("sub", e.get("H")?, e.get("y")?)?,
                        e.get("h")?,
                    )?);
                    args119.push(e.get("w")?);
                    args119.push(e.get("h")?);
                    kw120.push(("fill".into(), Val::Int(1i64)));
                    kw120.push(("stroke".into(), {
                        let fun124 = e.get("bool")?;
                        let mut args122 = Vec::new();
                        let mut kw123 = Vec::new();
                        args122.push(e.get("stroke")?);
                        fun124.call(args122, kw123)?
                    }));
                    fun121.call(args119, kw120)?
                };
            }
            Ok(Val::None)
        })
    })?;
    // ground
    e.set("ground", {
        let params = vec![("color".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun127 = e.get("rect")?;
                let mut args125 = Vec::new();
                let mut kw126 = Vec::new();
                args125.push(unary("neg", e.get("BLEED")?)?);
                args125.push(unary("neg", e.get("BLEED")?)?);
                args125.push(binary(
                    "add",
                    e.get("W")?,
                    binary("mul", Val::Int(2i64), e.get("BLEED")?)?,
                )?);
                args125.push(binary(
                    "add",
                    e.get("H")?,
                    binary("mul", Val::Int(2i64), e.get("BLEED")?)?,
                )?);
                args125.push(e.get("color")?);
                fun127.call(args125, kw126)?
            };
            Ok(Val::None)
        })
    })?;
    // line
    e.set("line", {
        let params = vec![
            ("x1".into(), None, false),
            ("y1".into(), None, false),
            ("x2".into(), None, false),
            ("y2".into(), None, false),
            ("color".into(), Some(e.get("RULE")?), false),
            ("width".into(), Some(Val::Float(0.8f64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun130 = e.get("c")?.attr("setStrokeColor")?;
                let mut args128 = Vec::new();
                let mut kw129 = Vec::new();
                args128.push({
                    let fun133 = e.get("HexColor")?;
                    let mut args131 = Vec::new();
                    let mut kw132 = Vec::new();
                    args131.push(e.get("color")?);
                    fun133.call(args131, kw132)?
                });
                fun130.call(args128, kw129)?
            };
            {
                let fun136 = e.get("c")?.attr("setLineWidth")?;
                let mut args134 = Vec::new();
                let mut kw135 = Vec::new();
                args134.push(e.get("width")?);
                fun136.call(args134, kw135)?
            };
            {
                let fun139 = e.get("c")?.attr("line")?;
                let mut args137 = Vec::new();
                let mut kw138 = Vec::new();
                args137.push(e.get("x1")?);
                args137.push(binary("sub", e.get("H")?, e.get("y1")?)?);
                args137.push(e.get("x2")?);
                args137.push(binary("sub", e.get("H")?, e.get("y2")?)?);
                fun139.call(args137, kw138)?
            };
            Ok(Val::None)
        })
    })?;
    // text
    e.set("text", {
        let params = vec![
            ("s".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("size".into(), Some(Val::Int(13i64)), false),
            ("font".into(), Some(Val::Str("Regular".into())), false),
            ("color".into(), Some(e.get("INK")?), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned140 = {
                let fun143 = e.get("pdfmetrics")?.attr("stringWidth")?;
                let mut args141 = Vec::new();
                let mut kw142 = Vec::new();
                args141.push(e.get("s")?);
                args141.push(e.get("font")?);
                args141.push(e.get("size")?);
                fun143.call(args141, kw142)?
            };
            e.set("width", assigned140.clone())?;
            if {
                let v152 = {
                    let v153 = e.get("x")?;
                    let v154 = Val::Int(36i64);
                    Val::Bool(compare("lt", v153.clone(), v154.clone())?.truthy()?)
                };
                if v152.truthy()? {
                    v152
                } else {
                    {
                        let v149 = {
                            let v150 = binary("add", e.get("x")?, e.get("width")?)?;
                            let v151 = binary("sub", e.get("W")?, Val::Int(36i64))?;
                            Val::Bool(compare("gt", v150.clone(), v151.clone())?.truthy()?)
                        };
                        if v149.truthy()? {
                            v149
                        } else {
                            {
                                let v146 = {
                                    let v147 = e.get("y")?;
                                    let v148 = Val::Int(36i64);
                                    Val::Bool(compare("lt", v147.clone(), v148.clone())?.truthy()?)
                                };
                                if v146.truthy()? {
                                    v146
                                } else {
                                    {
                                        let v144 = binary("add", e.get("y")?, e.get("size")?)?;
                                        let v145 = binary("sub", e.get("H")?, Val::Int(36i64))?;
                                        Val::Bool(
                                            compare("gt", v144.clone(), v145.clone())?.truthy()?,
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun157 = e.get("ValueError")?;
                        let mut args155 = Vec::new();
                        let mut kw156 = Vec::new();
                        args155.push({
                            let mut str158 = String::new();
                            str158.push_str("Page ");
                            str158.push_str(&format(&e.get("page_no")?, &String::new())?);
                            str158.push_str(": text outside safety margin: ");
                            str158.push_str(&format(
                                &builtin_call("repr", vec![e.get("s")?], vec![])?,
                                &String::new(),
                            )?);
                            Val::Str(str158)
                        });
                        fun157.call(args155, kw156)?
                    })?
                );
            }
            {
                let fun161 = e.get("c")?.attr("setFillColor")?;
                let mut args159 = Vec::new();
                let mut kw160 = Vec::new();
                args159.push({
                    let fun164 = e.get("HexColor")?;
                    let mut args162 = Vec::new();
                    let mut kw163 = Vec::new();
                    args162.push(e.get("color")?);
                    fun164.call(args162, kw163)?
                });
                fun161.call(args159, kw160)?
            };
            {
                let fun167 = e.get("c")?.attr("setFont")?;
                let mut args165 = Vec::new();
                let mut kw166 = Vec::new();
                args165.push(e.get("font")?);
                args165.push(e.get("size")?);
                fun167.call(args165, kw166)?
            };
            {
                let fun170 = e.get("c")?.attr("drawString")?;
                let mut args168 = Vec::new();
                let mut kw169 = Vec::new();
                args168.push(e.get("x")?);
                args168.push(binary(
                    "sub",
                    binary("sub", e.get("H")?, e.get("y")?)?,
                    binary("mul", e.get("size")?, Val::Float(0.8f64))?,
                )?);
                args168.push(e.get("s")?);
                fun170.call(args168, kw169)?
            };
            Ok(Val::None)
        })
    })?;
    // para
    e.set("para", {
        let params = vec![
            ("s".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("w".into(), Some(e.get("CW")?), false),
            ("size".into(), Some(Val::Int(13i64)), false),
            ("leading".into(), Some(Val::Int(18i64)), false),
            ("color".into(), Some(e.get("INK")?), false),
            ("font".into(), Some(Val::Str("Regular".into())), false),
            ("limit".into(), Some(Val::None), false),
            ("alignment".into(), Some(Val::Int(0i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned171 = {
                let fun174 = e.get("Paragraph")?;
                let mut args172 = Vec::new();
                let mut kw173 = Vec::new();
                args172.push(e.get("s")?);
                args172.push({
                    let fun177 = e.get("ParagraphStyle")?;
                    let mut args175 = Vec::new();
                    let mut kw176 = Vec::new();
                    args175.push(Val::Str("body".into()));
                    kw176.push(("fontName".into(), e.get("font")?));
                    kw176.push(("fontSize".into(), e.get("size")?));
                    kw176.push(("leading".into(), e.get("leading")?));
                    kw176.push(("textColor".into(), {
                        let fun180 = e.get("HexColor")?;
                        let mut args178 = Vec::new();
                        let mut kw179 = Vec::new();
                        args178.push(e.get("color")?);
                        fun180.call(args178, kw179)?
                    }));
                    kw176.push(("alignment".into(), e.get("alignment")?));
                    fun177.call(args175, kw176)?
                });
                fun174.call(args172, kw173)?
            };
            e.set("p", assigned171.clone())?;
            let assigned181 = {
                let fun184 = e.get("p")?.attr("wrap")?;
                let mut args182 = Vec::new();
                let mut kw183 = Vec::new();
                args182.push(e.get("w")?);
                args182.push(Val::Int(1000i64));
                fun184.call(args182, kw183)?
            };
            let unpack185 = unpack(assigned181.clone(), 2)?;
            e.set("_", unpack185[0].clone())?;
            e.set("h", unpack185[1].clone())?;
            if {
                let v188 = {
                    let v189 = e.get("limit")?;
                    let v190 = Val::None;
                    Val::Bool(compare("is_not", v189.clone(), v190.clone())?.truthy()?)
                };
                if v188.truthy()? {
                    {
                        let v186 = e.get("h")?;
                        let v187 = binary("add", e.get("limit")?, Val::Float(0.1f64))?;
                        Val::Bool(compare("gt", v186.clone(), v187.clone())?.truthy()?)
                    }
                } else {
                    v188
                }
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun193 = e.get("ValueError")?;
                        let mut args191 = Vec::new();
                        let mut kw192 = Vec::new();
                        args191.push({
                            let mut str194 = String::new();
                            str194.push_str("Page ");
                            str194.push_str(&format(&e.get("page_no")?, &String::new())?);
                            str194.push_str(": paragraph ");
                            str194.push_str(&format(&e.get("h")?, &String::new())?);
                            str194.push_str(">");
                            str194.push_str(&format(&e.get("limit")?, &String::new())?);
                            str194.push_str(": ");
                            str194.push_str(&format(
                                &e.get("s")?.get(Val::Slice {
                                    start: None,
                                    stop: Some(Val::Int(80i64).integer()?),
                                    step: 1,
                                })?,
                                &String::new(),
                            )?);
                            Val::Str(str194)
                        });
                        fun193.call(args191, kw192)?
                    })?
                );
            }
            if {
                let v203 = {
                    let v204 = e.get("x")?;
                    let v205 = Val::Int(36i64);
                    Val::Bool(compare("lt", v204.clone(), v205.clone())?.truthy()?)
                };
                if v203.truthy()? {
                    v203
                } else {
                    {
                        let v200 = {
                            let v201 = binary("add", e.get("x")?, e.get("w")?)?;
                            let v202 = binary("sub", e.get("W")?, Val::Int(36i64))?;
                            Val::Bool(compare("gt", v201.clone(), v202.clone())?.truthy()?)
                        };
                        if v200.truthy()? {
                            v200
                        } else {
                            {
                                let v197 = {
                                    let v198 = e.get("y")?;
                                    let v199 = Val::Int(36i64);
                                    Val::Bool(compare("lt", v198.clone(), v199.clone())?.truthy()?)
                                };
                                if v197.truthy()? {
                                    v197
                                } else {
                                    {
                                        let v195 = binary("add", e.get("y")?, e.get("h")?)?;
                                        let v196 = Val::Int(441i64);
                                        Val::Bool(
                                            compare("gt", v195.clone(), v196.clone())?.truthy()?,
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun208 = e.get("ValueError")?;
                        let mut args206 = Vec::new();
                        let mut kw207 = Vec::new();
                        args206.push({
                            let mut str209 = String::new();
                            str209.push_str("Page ");
                            str209.push_str(&format(&e.get("page_no")?, &String::new())?);
                            str209.push_str(": paragraph overflow ");
                            str209.push_str(&format(
                                &binary("add", e.get("y")?, e.get("h")?)?,
                                &String::new(),
                            )?);
                            str209.push_str(": ");
                            str209.push_str(&format(
                                &e.get("s")?.get(Val::Slice {
                                    start: None,
                                    stop: Some(Val::Int(80i64).integer()?),
                                    step: 1,
                                })?,
                                &String::new(),
                            )?);
                            Val::Str(str209)
                        });
                        fun208.call(args206, kw207)?
                    })?
                );
            }
            {
                let fun212 = e.get("p")?.attr("drawOn")?;
                let mut args210 = Vec::new();
                let mut kw211 = Vec::new();
                args210.push(e.get("c")?);
                args210.push(e.get("x")?);
                args210.push(binary(
                    "sub",
                    binary("sub", e.get("H")?, e.get("y")?)?,
                    e.get("h")?,
                )?);
                fun212.call(args210, kw211)?
            };
            {
                let fun215 = e.get("checks")?.attr("append")?;
                let mut args213 = Vec::new();
                let mut kw214 = Vec::new();
                args213.push({
                    let fun218 = e.get("dict")?;
                    let mut args216 = Vec::new();
                    let mut kw217 = Vec::new();
                    kw217.push(("page".into(), e.get("page_no")?));
                    kw217.push(("text".into(), e.get("s")?));
                    kw217.push(("box".into(), {
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y")?);
                        s.push(e.get("w")?);
                        s.push(e.get("h")?);
                        Val::list(s)
                    }));
                    fun218.call(args216, kw217)?
                });
                fun215.call(args213, kw214)?
            };
            return Ok(e.get("h")?);
            Ok(Val::None)
        })
    })?;
    // label
    e.set("label", {
        let params = vec![
            ("s".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("color".into(), Some(e.get("BLUE")?), false),
            ("size".into(), Some(Val::Int(9i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun221 = e.get("c")?.attr("saveState")?;
                let mut args219 = Vec::new();
                let mut kw220 = Vec::new();
                fun221.call(args219, kw220)?
            };
            let assigned222 = {
                let fun225 = e.get("c")?.attr("beginText")?;
                let mut args223 = Vec::new();
                let mut kw224 = Vec::new();
                args223.push(e.get("x")?);
                args223.push(binary(
                    "sub",
                    binary("sub", e.get("H")?, e.get("y")?)?,
                    binary("mul", e.get("size")?, Val::Float(0.8f64))?,
                )?);
                fun225.call(args223, kw224)?
            };
            e.set("t", assigned222.clone())?;
            {
                let fun228 = e.get("t")?.attr("setFont")?;
                let mut args226 = Vec::new();
                let mut kw227 = Vec::new();
                args226.push(Val::Str("Bold".into()));
                args226.push(e.get("size")?);
                fun228.call(args226, kw227)?
            };
            {
                let fun231 = e.get("t")?.attr("setFillColor")?;
                let mut args229 = Vec::new();
                let mut kw230 = Vec::new();
                args229.push({
                    let fun234 = e.get("HexColor")?;
                    let mut args232 = Vec::new();
                    let mut kw233 = Vec::new();
                    args232.push(e.get("color")?);
                    fun234.call(args232, kw233)?
                });
                fun231.call(args229, kw230)?
            };
            {
                let fun237 = e.get("t")?.attr("setCharSpace")?;
                let mut args235 = Vec::new();
                let mut kw236 = Vec::new();
                args235.push(Val::Int(1i64));
                fun237.call(args235, kw236)?
            };
            {
                let fun240 = e.get("t")?.attr("textOut")?;
                let mut args238 = Vec::new();
                let mut kw239 = Vec::new();
                args238.push({
                    let fun243 = e.get("s")?.attr("upper")?;
                    let mut args241 = Vec::new();
                    let mut kw242 = Vec::new();
                    fun243.call(args241, kw242)?
                });
                fun240.call(args238, kw239)?
            };
            {
                let fun246 = e.get("c")?.attr("drawText")?;
                let mut args244 = Vec::new();
                let mut kw245 = Vec::new();
                args244.push(e.get("t")?);
                fun246.call(args244, kw245)?
            };
            {
                let fun249 = e.get("c")?.attr("restoreState")?;
                let mut args247 = Vec::new();
                let mut kw248 = Vec::new();
                fun249.call(args247, kw248)?
            };
            Ok(Val::None)
        })
    })?;
    // badge
    e.set("badge", {
        let params = vec![
            ("n".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("r".into(), Some(Val::Int(14i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun252 = e.get("c")?.attr("setFillColor")?;
                let mut args250 = Vec::new();
                let mut kw251 = Vec::new();
                args250.push({
                    let fun255 = e.get("HexColor")?;
                    let mut args253 = Vec::new();
                    let mut kw254 = Vec::new();
                    args253.push(e.get("BLUE")?);
                    fun255.call(args253, kw254)?
                });
                fun252.call(args250, kw251)?
            };
            {
                let fun258 = e.get("c")?.attr("circle")?;
                let mut args256 = Vec::new();
                let mut kw257 = Vec::new();
                args256.push(binary("add", e.get("x")?, e.get("r")?)?);
                args256.push(binary(
                    "sub",
                    binary("sub", e.get("H")?, e.get("y")?)?,
                    e.get("r")?,
                )?);
                args256.push(e.get("r")?);
                kw257.push(("stroke".into(), Val::Int(0i64)));
                kw257.push(("fill".into(), Val::Int(1i64)));
                fun258.call(args256, kw257)?
            };
            {
                let fun261 = e.get("text")?;
                let mut args259 = Vec::new();
                let mut kw260 = Vec::new();
                args259.push({
                    let fun264 = e.get("str")?;
                    let mut args262 = Vec::new();
                    let mut kw263 = Vec::new();
                    args262.push(e.get("n")?);
                    fun264.call(args262, kw263)?
                });
                args259.push(binary(
                    "sub",
                    binary("add", e.get("x")?, e.get("r")?)?,
                    binary(
                        "truediv",
                        {
                            let fun267 = e.get("pdfmetrics")?.attr("stringWidth")?;
                            let mut args265 = Vec::new();
                            let mut kw266 = Vec::new();
                            args265.push({
                                let fun270 = e.get("str")?;
                                let mut args268 = Vec::new();
                                let mut kw269 = Vec::new();
                                args268.push(e.get("n")?);
                                fun270.call(args268, kw269)?
                            });
                            args265.push(Val::Str("Bold".into()));
                            args265.push(Val::Int(16i64));
                            fun267.call(args265, kw266)?
                        },
                        Val::Int(2i64),
                    )?,
                )?);
                args259.push(binary("add", e.get("y")?, Val::Int(6i64))?);
                args259.push(Val::Int(16i64));
                args259.push(Val::Str("Bold".into()));
                args259.push(Val::Str("#FFFFFF".into()));
                fun261.call(args259, kw260)?
            };
            Ok(Val::None)
        })
    })?;
    // header
    e.set("header", {
        let params = vec![
            ("title".into(), None, false),
            (
                "phase".into(),
                Some(Val::Str("BEFORE YOU START".into())),
                false,
            ),
            ("step".into(), Some(Val::None), false),
            ("sub".into(), Some(Val::None), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set_global("page_no", binary("add", e.get("page_no")?, Val::Int(1i64))?)?;
            {
                let fun273 = e.get("begin_page")?;
                let mut args271 = Vec::new();
                let mut kw272 = Vec::new();
                fun273.call(args271, kw272)?
            };
            {
                let fun276 = e.get("ground")?;
                let mut args274 = Vec::new();
                let mut kw275 = Vec::new();
                args274.push(Val::Str("#FFFFFF".into()));
                fun276.call(args274, kw275)?
            };
            {
                let fun279 = e.get("rect")?;
                let mut args277 = Vec::new();
                let mut kw278 = Vec::new();
                args277.push(unary("neg", e.get("BLEED")?)?);
                args277.push(unary("neg", e.get("BLEED")?)?);
                args277.push(binary(
                    "add",
                    e.get("W")?,
                    binary("mul", Val::Int(2i64), e.get("BLEED")?)?,
                )?);
                args277.push(binary("add", Val::Int(7i64), e.get("BLEED")?)?);
                args277.push(e.get("BLUE")?);
                fun279.call(args277, kw278)?
            };
            {
                let fun282 = e.get("label")?;
                let mut args280 = Vec::new();
                let mut kw281 = Vec::new();
                args280.push(e.get("phase")?);
                args280.push(e.get("M")?);
                args280.push(Val::Int(40i64));
                fun282.call(args280, kw281)?
            };
            let assigned283 = if e.get("step")?.truthy()? {
                binary("sub", e.get("CW")?, Val::Int(44i64))?
            } else {
                e.get("CW")?
            };
            e.set("width", assigned283.clone())?;
            let assigned284 = {
                let fun287 = e.get("min")?;
                let mut args285 = Vec::new();
                let mut kw286 = Vec::new();
                args285.push(Val::Int(28i64));
                args285.push(binary(
                    "truediv",
                    binary("mul", Val::Int(28i64), e.get("width")?)?,
                    {
                        let fun290 = e.get("pdfmetrics")?.attr("stringWidth")?;
                        let mut args288 = Vec::new();
                        let mut kw289 = Vec::new();
                        args288.push(e.get("title")?);
                        args288.push(Val::Str("Bold".into()));
                        args288.push(Val::Int(28i64));
                        fun290.call(args288, kw289)?
                    },
                )?);
                fun287.call(args285, kw286)?
            };
            e.set("size", assigned284.clone())?;
            {
                let fun293 = e.get("text")?;
                let mut args291 = Vec::new();
                let mut kw292 = Vec::new();
                args291.push(e.get("title")?);
                args291.push(e.get("M")?);
                args291.push(Val::Int(64i64));
                args291.push(e.get("size")?);
                args291.push(Val::Str("Bold".into()));
                args291.push(e.get("NAVY")?);
                fun293.call(args291, kw292)?
            };
            if {
                let v294 = e.get("step")?;
                let v295 = Val::None;
                Val::Bool(compare("is_not", v294.clone(), v295.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun298 = e.get("badge")?;
                    let mut args296 = Vec::new();
                    let mut kw297 = Vec::new();
                    args296.push(e.get("step")?);
                    args296.push(binary(
                        "sub",
                        binary("sub", e.get("W")?, e.get("M")?)?,
                        Val::Int(28i64),
                    )?);
                    args296.push(Val::Int(61i64));
                    fun298.call(args296, kw297)?
                };
            }
            if e.get("sub")?.truthy()? {
                {
                    let fun301 = e.get("para")?;
                    let mut args299 = Vec::new();
                    let mut kw300 = Vec::new();
                    args299.push(e.get("sub")?);
                    args299.push(e.get("M")?);
                    args299.push(Val::Int(103i64));
                    args299.push(e.get("CW")?);
                    args299.push(Val::Int(12i64));
                    args299.push(Val::Int(16i64));
                    args299.push(e.get("MUTED")?);
                    kw300.push(("limit".into(), Val::Int(32i64)));
                    fun301.call(args299, kw300)?
                };
            }
            {
                let fun304 = e.get("c")?.attr("bookmarkPage")?;
                let mut args302 = Vec::new();
                let mut kw303 = Vec::new();
                args302.push({
                    let mut str305 = String::new();
                    str305.push_str("page-");
                    str305.push_str(&format(&e.get("page_no")?, &String::new())?);
                    Val::Str(str305)
                });
                fun304.call(args302, kw303)?
            };
            {
                let fun308 = e.get("c")?.attr("addOutlineEntry")?;
                let mut args306 = Vec::new();
                let mut kw307 = Vec::new();
                args306.push({
                    let mut str309 = String::new();
                    str309.push_str(&format(
                        &binary("sub", e.get("page_no")?, Val::Int(1i64))?,
                        &String::new(),
                    )?);
                    str309.push_str(". ");
                    str309.push_str(&format(&e.get("title")?, &String::new())?);
                    Val::Str(str309)
                });
                args306.push({
                    let mut str310 = String::new();
                    str310.push_str("page-");
                    str310.push_str(&format(&e.get("page_no")?, &String::new())?);
                    Val::Str(str310)
                });
                args306.push(Val::Int(0i64));
                args306.push(Val::Bool(false));
                fun308.call(args306, kw307)?
            };
            {
                let fun313 = e.get("titles")?.attr("append")?;
                let mut args311 = Vec::new();
                let mut kw312 = Vec::new();
                args311.push(e.get("title")?);
                fun313.call(args311, kw312)?
            };
            Ok(Val::None)
        })
    })?;
    // end
    e.set("end", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun316 = e.get("line")?;
                let mut args314 = Vec::new();
                let mut kw315 = Vec::new();
                args314.push(e.get("M")?);
                args314.push(Val::Int(449i64));
                args314.push(binary("sub", e.get("W")?, e.get("M")?)?);
                args314.push(Val::Int(449i64));
                fun316.call(args314, kw315)?
            };
            {
                let fun319 = e.get("text")?;
                let mut args317 = Vec::new();
                let mut kw318 = Vec::new();
                args317.push(Val::Str("HOME SODA MACHINE".into()));
                args317.push(e.get("M")?);
                args317.push(Val::Int(459i64));
                args317.push(Val::Int(8i64));
                args317.push(Val::Str("Bold".into()));
                args317.push(e.get("NAVY")?);
                fun319.call(args317, kw318)?
            };
            {
                let fun322 = e.get("text")?;
                let mut args320 = Vec::new();
                let mut kw321 = Vec::new();
                args320.push(Val::Str("Install guide".into()));
                args320.push(Val::Int(275i64));
                args320.push(Val::Int(459i64));
                args320.push(Val::Int(8i64));
                args320.push(Val::Str("Regular".into()));
                args320.push(e.get("MUTED")?);
                fun322.call(args320, kw321)?
            };
            let assigned323 = {
                let fun326 = e.get("str")?;
                let mut args324 = Vec::new();
                let mut kw325 = Vec::new();
                args324.push(binary("sub", e.get("page_no")?, Val::Int(1i64))?);
                fun326.call(args324, kw325)?
            };
            e.set("number", assigned323.clone())?;
            {
                let fun329 = e.get("text")?;
                let mut args327 = Vec::new();
                let mut kw328 = Vec::new();
                args327.push(e.get("number")?);
                args327.push(binary("sub", binary("sub", e.get("W")?, e.get("M")?)?, {
                    let fun332 = e.get("pdfmetrics")?.attr("stringWidth")?;
                    let mut args330 = Vec::new();
                    let mut kw331 = Vec::new();
                    args330.push(e.get("number")?);
                    args330.push(Val::Str("Semibold".into()));
                    args330.push(Val::Int(9i64));
                    fun332.call(args330, kw331)?
                })?);
                args327.push(Val::Int(458i64));
                args327.push(Val::Int(9i64));
                args327.push(Val::Str("Semibold".into()));
                args327.push(e.get("NAVY")?);
                fun329.call(args327, kw328)?
            };
            {
                let fun335 = e.get("c")?.attr("showPage")?;
                let mut args333 = Vec::new();
                let mut kw334 = Vec::new();
                fun335.call(args333, kw334)?
            };
            Ok(Val::None)
        })
    })?;
    // image_reader
    e.set("image_reader", {
        let params = vec![
            ("source".into(), None, false),
            ("background".into(), Some(Val::Str("#FFFFFF".into())), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned336 = if {
                let fun339 = e.get("isinstance")?;
                let mut args337 = Vec::new();
                let mut kw338 = Vec::new();
                args337.push(e.get("source")?);
                args337.push({
                    let mut s = Vec::new();
                    s.push(e.get("str")?);
                    s.push(e.get("Path")?);
                    Val::tuple(s)
                });
                fun339.call(args337, kw338)?
            }
            .truthy()?
            {
                {
                    let fun342 = {
                        let fun345 = e.get("Image")?.attr("open")?;
                        let mut args343 = Vec::new();
                        let mut kw344 = Vec::new();
                        args343.push(e.get("source")?);
                        fun345.call(args343, kw344)?
                    }
                    .attr("convert")?;
                    let mut args340 = Vec::new();
                    let mut kw341 = Vec::new();
                    args340.push(Val::Str("RGBA".into()));
                    fun342.call(args340, kw341)?
                }
            } else {
                {
                    let fun348 = e.get("source")?.attr("convert")?;
                    let mut args346 = Vec::new();
                    let mut kw347 = Vec::new();
                    args346.push(Val::Str("RGBA".into()));
                    fun348.call(args346, kw347)?
                }
            };
            e.set("im", assigned336.clone())?;
            let assigned349 = {
                let fun352 = e.get("Image")?.attr("new")?;
                let mut args350 = Vec::new();
                let mut kw351 = Vec::new();
                args350.push(Val::Str("RGB".into()));
                args350.push(e.get("im")?.attr("size")?);
                args350.push(e.get("background")?);
                fun352.call(args350, kw351)?
            };
            e.set("flat", assigned349.clone())?;
            {
                let fun355 = e.get("flat")?.attr("paste")?;
                let mut args353 = Vec::new();
                let mut kw354 = Vec::new();
                args353.push(e.get("im")?);
                kw354.push(("mask".into(), {
                    let fun358 = e.get("im")?.attr("getchannel")?;
                    let mut args356 = Vec::new();
                    let mut kw357 = Vec::new();
                    args356.push(Val::Str("A".into()));
                    fun358.call(args356, kw357)?
                }));
                fun355.call(args353, kw354)?
            };
            return Ok({
                let fun361 = e.get("ImageReader")?;
                let mut args359 = Vec::new();
                let mut kw360 = Vec::new();
                args359.push(e.get("flat")?);
                fun361.call(args359, kw360)?
            });
            Ok(Val::None)
        })
    })?;
    // pic
    e.set("pic", {
        let params = vec![
            ("name".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("w".into(), None, false),
            ("h".into(), None, false),
            ("crop".into(), Some(Val::None), false),
            ("outline".into(), Some(Val::Bool(true)), false),
            ("fade_crops".into(), Some(Val::Bool(true)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned362 = binary("truediv", e.get("ART")?, e.get("name")?)?;
            e.set("source", assigned362.clone())?;
            let assigned363 = {
                let fun366 = e.get("Image")?.attr("open")?;
                let mut args364 = Vec::new();
                let mut kw365 = Vec::new();
                args364.push(e.get("source")?);
                fun366.call(args364, kw365)?
            };
            e.set("im", assigned363.clone())?;
            let assigned367 = {
                let fun370 = e.get("resolutions")?.attr("get")?;
                let mut args368 = Vec::new();
                let mut kw369 = Vec::new();
                args368.push(e.get("name")?);
                args368.push({
                    let d = Val::dict(vec![]);
                    d
                });
                fun370.call(args368, kw369)?
            };
            e.set("resolution", assigned367.clone())?;
            if {
                let v376 = e.get("resolution")?;
                if v376.truthy()? {
                    {
                        let v374 = {
                            let fun373 = e.get("list")?;
                            let mut args371 = Vec::new();
                            let mut kw372 = Vec::new();
                            args371.push(e.get("im")?.attr("size")?);
                            fun373.call(args371, kw372)?
                        };
                        let v375 = e.get("resolution")?.get(Val::Str("render_size".into()))?;
                        Val::Bool(compare("ne", v374.clone(), v375.clone())?.truthy()?)
                    }
                } else {
                    v376
                }
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun379 = e.get("ValueError")?;
                        let mut args377 = Vec::new();
                        let mut kw378 = Vec::new();
                        args377.push({
                            let mut str380 = String::new();
                            str380.push_str(&format(&e.get("name")?, &String::new())?);
                            str380.push_str(": dimensions disagree with print-resolution.json");
                            Val::Str(str380)
                        });
                        fun379.call(args377, kw378)?
                    })?
                );
            }
            let assigned381 = {
                let fun384 = e.get("resolution")?.attr("get")?;
                let mut args382 = Vec::new();
                let mut kw383 = Vec::new();
                args382.push(Val::Str("scale".into()));
                args382.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(1i64));
                    s.push(Val::Int(1i64));
                    Val::list(s)
                });
                fun384.call(args382, kw383)?
            };
            let unpack385 = unpack(assigned381.clone(), 2)?;
            e.set("rx", unpack385[0].clone())?;
            e.set("ry", unpack385[1].clone())?;
            if e.get("crop")?.truthy()? {
                let assigned386 = {
                    let fun389 = e.get("tuple")?;
                    let mut args387 = Vec::new();
                    let mut kw388 = Vec::new();
                    args387.push({
                        let e = e.child();
                        let out390 = Val::list(vec![]);
                        for item391 in {
                            let fun394 = e.get("zip")?;
                            let mut args392 = Vec::new();
                            let mut kw393 = Vec::new();
                            args392.push(e.get("crop")?);
                            args392.push({
                                let mut s = Vec::new();
                                s.push(e.get("rx")?);
                                s.push(e.get("ry")?);
                                s.push(e.get("rx")?);
                                s.push(e.get("ry")?);
                                Val::tuple(s)
                            });
                            fun394.call(args392, kw393)?
                        }
                        .iter()?
                        {
                            let unpack395 = unpack(item391, 2)?;
                            e.set("value", unpack395[0].clone())?;
                            e.set("factor", unpack395[1].clone())?;
                            out390.attr("append")?.call(
                                vec![binary("mul", e.get("value")?, e.get("factor")?)?],
                                vec![],
                            )?;
                        }
                        out390
                    });
                    fun389.call(args387, kw388)?
                };
                e.set("crop", assigned386.clone())?;
            }
            let assigned396 = {
                let v406 = e.get("crop")?;
                if v406.truthy()? {
                    v406
                } else {
                    {
                        let v397 = if {
                            let v398 = e.get("im")?.attr("mode")?;
                            let v399 = Val::Str("RGBA".into());
                            Val::Bool(compare("eq", v398.clone(), v399.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            {
                                let fun402 = {
                                    let fun405 = e.get("im")?.attr("getchannel")?;
                                    let mut args403 = Vec::new();
                                    let mut kw404 = Vec::new();
                                    args403.push(Val::Str("A".into()));
                                    fun405.call(args403, kw404)?
                                }
                                .attr("getbbox")?;
                                let mut args400 = Vec::new();
                                let mut kw401 = Vec::new();
                                fun402.call(args400, kw401)?
                            }
                        } else {
                            Val::None
                        };
                        if v397.truthy()? {
                            v397
                        } else {
                            {
                                let mut s = Vec::new();
                                s.push(Val::Int(0i64));
                                s.push(Val::Int(0i64));
                                s.push(e.get("im")?.attr("width")?);
                                s.push(e.get("im")?.attr("height")?);
                                Val::tuple(s)
                            }
                        }
                    }
                }
            };
            e.set("bounds", assigned396.clone())?;
            let assigned407 = e.get("bounds")?;
            let unpack408 = unpack(assigned407.clone(), 4)?;
            e.set("a", unpack408[0].clone())?;
            e.set("b", unpack408[1].clone())?;
            e.set("cc", unpack408[2].clone())?;
            e.set("d", unpack408[3].clone())?;
            let assigned409 = {
                let fun412 = e.get("min")?;
                let mut args410 = Vec::new();
                let mut kw411 = Vec::new();
                args410.push(binary(
                    "truediv",
                    e.get("w")?,
                    binary("sub", e.get("cc")?, e.get("a")?)?,
                )?);
                args410.push(binary(
                    "truediv",
                    e.get("h")?,
                    binary("sub", e.get("d")?, e.get("b")?)?,
                )?);
                args410.push(binary("truediv", Val::Int(72i64), Val::Int(300i64))?);
                fun412.call(args410, kw411)?
            };
            e.set("scale", assigned409.clone())?;
            let assigned413 = {
                let mut s = Vec::new();
                s.push(binary(
                    "mul",
                    binary("sub", e.get("cc")?, e.get("a")?)?,
                    e.get("scale")?,
                )?);
                s.push(binary(
                    "mul",
                    binary("sub", e.get("d")?, e.get("b")?)?,
                    e.get("scale")?,
                )?);
                Val::tuple(s)
            };
            let unpack414 = unpack(assigned413.clone(), 2)?;
            e.set("iw", unpack414[0].clone())?;
            e.set("ih", unpack414[1].clone())?;
            let assigned415 = {
                let mut s = Vec::new();
                s.push(binary(
                    "add",
                    e.get("x")?,
                    binary(
                        "truediv",
                        binary("sub", e.get("w")?, e.get("iw")?)?,
                        Val::Int(2i64),
                    )?,
                )?);
                s.push(binary(
                    "add",
                    e.get("y")?,
                    binary(
                        "truediv",
                        binary("sub", e.get("h")?, e.get("ih")?)?,
                        Val::Int(2i64),
                    )?,
                )?);
                Val::tuple(s)
            };
            let unpack416 = unpack(assigned415.clone(), 2)?;
            e.set("ox", unpack416[0].clone())?;
            e.set("oy", unpack416[1].clone())?;
            let assigned417 = binary("truediv", Val::Int(72i64), e.get("scale")?)?;
            e.set("ppi", assigned417.clone())?;
            {
                let fun420 = e.get("image_checks")?.attr("append")?;
                let mut args418 = Vec::new();
                let mut kw419 = Vec::new();
                args418.push({
                    let fun423 = e.get("dict")?;
                    let mut args421 = Vec::new();
                    let mut kw422 = Vec::new();
                    kw422.push(("page".into(), e.get("page_no")?));
                    kw422.push(("source".into(), e.get("name")?));
                    kw422.push(("native_pixels".into(), {
                        let fun426 = e.get("list")?;
                        let mut args424 = Vec::new();
                        let mut kw425 = Vec::new();
                        args424.push(e.get("im")?.attr("size")?);
                        fun426.call(args424, kw425)?
                    }));
                    kw422.push(("ppi".into(), e.get("ppi")?));
                    kw422.push(("box".into(), {
                        let mut s = Vec::new();
                        s.push(e.get("ox")?);
                        s.push(e.get("oy")?);
                        s.push(e.get("iw")?);
                        s.push(e.get("ih")?);
                        Val::list(s)
                    }));
                    fun423.call(args421, kw422)?
                });
                fun420.call(args418, kw419)?
            };
            if e.get("outline")?.truthy()? {
                let assigned427 = {
                    let fun430 = e.get("contours")?.attr("picture")?;
                    let mut args428 = Vec::new();
                    let mut kw429 = Vec::new();
                    args428.push(e.get("source")?);
                    args428.push(e.get("bounds")?);
                    args428.push(e.get("iw")?);
                    args428.push(e.get("ih")?);
                    kw429.push(("fade_crops".into(), e.get("fade_crops")?));
                    fun430.call(args428, kw429)?
                };
                let unpack431 = unpack(assigned427.clone(), 2)?;
                e.set("target", unpack431[0].clone())?;
                let unpack432 = unpack(unpack431[1].clone(), 2)?;
                e.set("pw", unpack432[0].clone())?;
                e.set("ph", unpack432[1].clone())?;
                if {
                    let fun435 = e.get("target")?.attr("exists")?;
                    let mut args433 = Vec::new();
                    let mut kw434 = Vec::new();
                    fun435.call(args433, kw434)?
                }
                .truthy()?
                {
                    {
                        let fun438 = e.get("c")?.attr("drawImage")?;
                        let mut args436 = Vec::new();
                        let mut kw437 = Vec::new();
                        args436.push({
                            let fun441 = e.get("image_reader")?;
                            let mut args439 = Vec::new();
                            let mut kw440 = Vec::new();
                            args439.push(e.get("target")?);
                            fun441.call(args439, kw440)?
                        });
                        args436.push(binary("sub", e.get("ox")?, e.get("PAD")?)?);
                        args436.push(binary(
                            "sub",
                            binary(
                                "sub",
                                binary("sub", e.get("H")?, e.get("oy")?)?,
                                e.get("ih")?,
                            )?,
                            e.get("PAD")?,
                        )?);
                        kw437.push(("width".into(), e.get("pw")?));
                        kw437.push(("height".into(), e.get("ph")?));
                        fun438.call(args436, kw437)?
                    };
                }
            } else {
                {
                    let fun444 = e.get("c")?.attr("drawImage")?;
                    let mut args442 = Vec::new();
                    let mut kw443 = Vec::new();
                    args442.push({
                        let fun447 = e.get("image_reader")?;
                        let mut args445 = Vec::new();
                        let mut kw446 = Vec::new();
                        args445.push({
                            let fun450 = e.get("im")?.attr("crop")?;
                            let mut args448 = Vec::new();
                            let mut kw449 = Vec::new();
                            args448.push(e.get("bounds")?);
                            fun450.call(args448, kw449)?
                        });
                        fun447.call(args445, kw446)?
                    });
                    args442.push(e.get("ox")?);
                    args442.push(binary(
                        "sub",
                        binary("sub", e.get("H")?, e.get("oy")?)?,
                        e.get("ih")?,
                    )?);
                    kw443.push(("width".into(), e.get("iw")?));
                    kw443.push(("height".into(), e.get("ih")?));
                    fun444.call(args442, kw443)?
                };
            }
            return Ok({
                let params = vec![("px".into(), None, false), ("py".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    return Ok({
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            e.get("ox")?,
                            binary(
                                "mul",
                                binary(
                                    "sub",
                                    binary("mul", e.get("px")?, e.get("rx")?)?,
                                    e.get("a")?,
                                )?,
                                e.get("scale")?,
                            )?,
                        )?);
                        s.push(binary(
                            "add",
                            e.get("oy")?,
                            binary(
                                "mul",
                                binary(
                                    "sub",
                                    binary("mul", e.get("py")?, e.get("ry")?)?,
                                    e.get("b")?,
                                )?,
                                e.get("scale")?,
                            )?,
                        )?);
                        Val::tuple(s)
                    });
                    Ok(Val::None)
                })
            });
            Ok(Val::None)
        })
    })?;
    // caption
    e.set("caption", {
        let params = vec![
            ("s".into(), None, false),
            ("y".into(), None, false),
            ("x".into(), Some(e.get("M")?), false),
            ("w".into(), Some(Val::Int(264i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun453 = e.get("para")?;
                let mut args451 = Vec::new();
                let mut kw452 = Vec::new();
                args451.push(e.get("s")?);
                args451.push(e.get("x")?);
                args451.push(e.get("y")?);
                args451.push(e.get("w")?);
                args451.push(Val::Int(10i64));
                args451.push(Val::Int(14i64));
                args451.push(e.get("MUTED")?);
                kw452.push(("limit".into(), Val::Int(42i64)));
                fun453.call(args451, kw452)?
            });
            Ok(Val::None)
        })
    })?;
    // kit_picture
    e.set("kit_picture", {
        let params = vec![
            ("name".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("w".into(), None, false),
            ("h".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned454 = {
                let fun457 = {
                    let fun460 = e.get("ET")?.attr("parse")?;
                    let mut args458 = Vec::new();
                    let mut kw459 = Vec::new();
                    args458.push(binary(
                        "truediv",
                        binary("truediv", e.get("ART")?, Val::Str("kit".into()))?,
                        {
                            let mut str461 = String::new();
                            str461.push_str(&format(&e.get("name")?, &String::new())?);
                            str461.push_str(".svg");
                            Val::Str(str461)
                        },
                    )?);
                    fun460.call(args458, kw459)?
                }
                .attr("getroot")?;
                let mut args455 = Vec::new();
                let mut kw456 = Vec::new();
                fun457.call(args455, kw456)?
            };
            e.set("svg", assigned454.clone())?;
            let assigned462 = {
                let e = e.child();
                let out463 = Val::list(vec![]);
                for item464 in {
                    let fun467 = e.get("svg")?.attr("iter")?;
                    let mut args465 = Vec::new();
                    let mut kw466 = Vec::new();
                    args465.push(Val::Str("{http://www.w3.org/2000/svg}path".into()));
                    fun467.call(args465, kw466)?
                }
                .iter()?
                {
                    e.set("node", item464)?;
                    out463.attr("append")?.call(
                        vec![{
                            let e = e.child();
                            let out468 = Val::list(vec![]);
                            for item469 in {
                                let fun472 = e.get("re")?.attr("findall")?;
                                let mut args470 = Vec::new();
                                let mut kw471 = Vec::new();
                                args470.push(Val::Str("([ML])([-+\\d.eE]+),([-+\\d.eE]+)".into()));
                                args470.push(
                                    e.get("node")?.attr("attrib")?.get(Val::Str("d".into()))?,
                                );
                                fun472.call(args470, kw471)?
                            }
                            .iter()?
                            {
                                let unpack473 = unpack(item469, 3)?;
                                e.set("command", unpack473[0].clone())?;
                                e.set("px", unpack473[1].clone())?;
                                e.set("py", unpack473[2].clone())?;
                                out468.attr("append")?.call(
                                    vec![{
                                        let mut s = Vec::new();
                                        s.push(e.get("command")?);
                                        s.push({
                                            let fun476 = e.get("float")?;
                                            let mut args474 = Vec::new();
                                            let mut kw475 = Vec::new();
                                            args474.push(e.get("px")?);
                                            fun476.call(args474, kw475)?
                                        });
                                        s.push({
                                            let fun479 = e.get("float")?;
                                            let mut args477 = Vec::new();
                                            let mut kw478 = Vec::new();
                                            args477.push(e.get("py")?);
                                            fun479.call(args477, kw478)?
                                        });
                                        Val::tuple(s)
                                    }],
                                    vec![],
                                )?;
                            }
                            out468
                        }],
                        vec![],
                    )?;
                }
                out463
            };
            e.set("paths", assigned462.clone())?;
            let assigned480 = {
                let e = e.child();
                let out481 = Val::list(vec![]);
                for item482 in e.get("paths")?.iter()? {
                    e.set("path", item482)?;
                    for item483 in e.get("path")?.iter()? {
                        e.set("point", item483)?;
                        out481.attr("append")?.call(vec![e.get("point")?], vec![])?;
                    }
                }
                out481
            };
            e.set("points", assigned480.clone())?;
            let assigned484 = {
                let mut s = Vec::new();
                s.push({
                    let fun487 = e.get("min")?;
                    let mut args485 = Vec::new();
                    let mut kw486 = Vec::new();
                    args485.push({
                        let e = e.child();
                        let out488 = Val::list(vec![]);
                        for item489 in e.get("points")?.iter()? {
                            e.set("p", item489)?;
                            out488
                                .attr("append")?
                                .call(vec![e.get("p")?.get(Val::Int(1i64))?], vec![])?;
                        }
                        out488
                    });
                    fun487.call(args485, kw486)?
                });
                s.push({
                    let fun492 = e.get("max")?;
                    let mut args490 = Vec::new();
                    let mut kw491 = Vec::new();
                    args490.push({
                        let e = e.child();
                        let out493 = Val::list(vec![]);
                        for item494 in e.get("points")?.iter()? {
                            e.set("p", item494)?;
                            out493
                                .attr("append")?
                                .call(vec![e.get("p")?.get(Val::Int(1i64))?], vec![])?;
                        }
                        out493
                    });
                    fun492.call(args490, kw491)?
                });
                Val::tuple(s)
            };
            let unpack495 = unpack(assigned484.clone(), 2)?;
            e.set("left", unpack495[0].clone())?;
            e.set("right", unpack495[1].clone())?;
            let assigned496 = {
                let mut s = Vec::new();
                s.push({
                    let fun499 = e.get("min")?;
                    let mut args497 = Vec::new();
                    let mut kw498 = Vec::new();
                    args497.push({
                        let e = e.child();
                        let out500 = Val::list(vec![]);
                        for item501 in e.get("points")?.iter()? {
                            e.set("p", item501)?;
                            out500
                                .attr("append")?
                                .call(vec![e.get("p")?.get(Val::Int(2i64))?], vec![])?;
                        }
                        out500
                    });
                    fun499.call(args497, kw498)?
                });
                s.push({
                    let fun504 = e.get("max")?;
                    let mut args502 = Vec::new();
                    let mut kw503 = Vec::new();
                    args502.push({
                        let e = e.child();
                        let out505 = Val::list(vec![]);
                        for item506 in e.get("points")?.iter()? {
                            e.set("p", item506)?;
                            out505
                                .attr("append")?
                                .call(vec![e.get("p")?.get(Val::Int(2i64))?], vec![])?;
                        }
                        out505
                    });
                    fun504.call(args502, kw503)?
                });
                Val::tuple(s)
            };
            let unpack507 = unpack(assigned496.clone(), 2)?;
            e.set("top", unpack507[0].clone())?;
            e.set("bottom", unpack507[1].clone())?;
            let assigned508 = {
                let fun511 = e.get("min")?;
                let mut args509 = Vec::new();
                let mut kw510 = Vec::new();
                args509.push(binary(
                    "truediv",
                    e.get("w")?,
                    binary("sub", e.get("right")?, e.get("left")?)?,
                )?);
                args509.push(binary(
                    "truediv",
                    e.get("h")?,
                    binary("sub", e.get("bottom")?, e.get("top")?)?,
                )?);
                fun511.call(args509, kw510)?
            };
            e.set("scale", assigned508.clone())?;
            let assigned512 = {
                let mut s = Vec::new();
                s.push(binary(
                    "add",
                    e.get("x")?,
                    binary(
                        "truediv",
                        binary(
                            "sub",
                            e.get("w")?,
                            binary(
                                "mul",
                                binary("sub", e.get("right")?, e.get("left")?)?,
                                e.get("scale")?,
                            )?,
                        )?,
                        Val::Int(2i64),
                    )?,
                )?);
                s.push(binary(
                    "sub",
                    binary("add", e.get("y")?, e.get("h")?)?,
                    binary(
                        "mul",
                        binary("sub", e.get("bottom")?, e.get("top")?)?,
                        e.get("scale")?,
                    )?,
                )?);
                Val::tuple(s)
            };
            let unpack513 = unpack(assigned512.clone(), 2)?;
            e.set("ox", unpack513[0].clone())?;
            e.set("oy", unpack513[1].clone())?;
            {
                let fun516 = e.get("c")?.attr("saveState")?;
                let mut args514 = Vec::new();
                let mut kw515 = Vec::new();
                fun516.call(args514, kw515)?
            };
            {
                let fun519 = e.get("c")?.attr("setLineWidth")?;
                let mut args517 = Vec::new();
                let mut kw518 = Vec::new();
                args517.push(Val::Float(0.68f64));
                fun519.call(args517, kw518)?
            };
            {
                let fun522 = e.get("c")?.attr("setStrokeColor")?;
                let mut args520 = Vec::new();
                let mut kw521 = Vec::new();
                args520.push({
                    let fun525 = e.get("HexColor")?;
                    let mut args523 = Vec::new();
                    let mut kw524 = Vec::new();
                    args523.push(Val::Str("#46515b".into()));
                    fun525.call(args523, kw524)?
                });
                fun522.call(args520, kw521)?
            };
            {
                let fun528 = e.get("c")?.attr("setLineCap")?;
                let mut args526 = Vec::new();
                let mut kw527 = Vec::new();
                args526.push(Val::Int(1i64));
                fun528.call(args526, kw527)?
            };
            {
                let fun531 = e.get("c")?.attr("setLineJoin")?;
                let mut args529 = Vec::new();
                let mut kw530 = Vec::new();
                args529.push(Val::Int(1i64));
                fun531.call(args529, kw530)?
            };
            for item532 in e.get("paths")?.iter()? {
                e.set("points", item532)?;
                let assigned533 = {
                    let fun536 = e.get("c")?.attr("beginPath")?;
                    let mut args534 = Vec::new();
                    let mut kw535 = Vec::new();
                    fun536.call(args534, kw535)?
                };
                e.set("path", assigned533.clone())?;
                for item537 in e.get("points")?.iter()? {
                    let unpack544 = unpack(item537, 3)?;
                    e.set("command", unpack544[0].clone())?;
                    e.set("px", unpack544[1].clone())?;
                    e.set("py", unpack544[2].clone())?;
                    let assigned538 = {
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            e.get("ox")?,
                            binary(
                                "mul",
                                binary("sub", e.get("px")?, e.get("left")?)?,
                                e.get("scale")?,
                            )?,
                        )?);
                        s.push(binary(
                            "sub",
                            binary("sub", e.get("H")?, e.get("oy")?)?,
                            binary(
                                "mul",
                                binary("sub", e.get("py")?, e.get("top")?)?,
                                e.get("scale")?,
                            )?,
                        )?);
                        Val::tuple(s)
                    };
                    e.set("point", assigned538.clone())?;
                    {
                        let fun541 = if {
                            let v542 = e.get("command")?;
                            let v543 = Val::Str("M".into());
                            Val::Bool(compare("eq", v542.clone(), v543.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            e.get("path")?.attr("moveTo")?
                        } else {
                            e.get("path")?.attr("lineTo")?
                        };
                        let mut args539 = Vec::new();
                        let mut kw540 = Vec::new();
                        args539.extend(e.get("point")?.iter()?);
                        fun541.call(args539, kw540)?
                    };
                }
                {
                    let fun547 = e.get("c")?.attr("drawPath")?;
                    let mut args545 = Vec::new();
                    let mut kw546 = Vec::new();
                    args545.push(e.get("path")?);
                    kw546.push(("stroke".into(), Val::Int(1i64)));
                    kw546.push(("fill".into(), Val::Int(0i64)));
                    fun547.call(args545, kw546)?
                };
            }
            {
                let fun550 = e.get("c")?.attr("restoreState")?;
                let mut args548 = Vec::new();
                let mut kw549 = Vec::new();
                fun550.call(args548, kw549)?
            };
            Ok(Val::None)
        })
    })?;
    // note
    e.set("note", {
        let params = vec![
            ("title".into(), None, false),
            ("s".into(), None, false),
            ("y".into(), None, false),
            ("x".into(), Some(e.get("M")?), false),
            ("w".into(), Some(e.get("CW")?), false),
            ("kind".into(), Some(Val::Str("blue".into())), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned551 = binary(
                "add",
                {
                    let fun554 = {
                        let fun557 = e.get("Paragraph")?;
                        let mut args555 = Vec::new();
                        let mut kw556 = Vec::new();
                        args555.push(e.get("s")?);
                        args555.push({
                            let fun560 = e.get("ParagraphStyle")?;
                            let mut args558 = Vec::new();
                            let mut kw559 = Vec::new();
                            args558.push(Val::Str("measure".into()));
                            kw559.push(("fontName".into(), Val::Str("Regular".into())));
                            kw559.push(("fontSize".into(), Val::Int(12i64)));
                            kw559.push(("leading".into(), Val::Int(17i64)));
                            fun560.call(args558, kw559)?
                        });
                        fun557.call(args555, kw556)?
                    }
                    .attr("wrap")?;
                    let mut args552 = Vec::new();
                    let mut kw553 = Vec::new();
                    args552.push(binary("sub", e.get("w")?, Val::Int(28i64))?);
                    args552.push(Val::Int(1000i64));
                    fun554.call(args552, kw553)?
                }
                .get(Val::Int(1i64))?,
                Val::Int(44i64),
            )?;
            e.set("h", assigned551.clone())?;
            if {
                let v561 = binary("add", e.get("y")?, e.get("h")?)?;
                let v562 = Val::Int(439i64);
                Val::Bool(compare("gt", v561.clone(), v562.clone())?.truthy()?)
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun565 = e.get("ValueError")?;
                        let mut args563 = Vec::new();
                        let mut kw564 = Vec::new();
                        args563.push({
                            let mut str566 = String::new();
                            str566.push_str("Page ");
                            str566.push_str(&format(&e.get("page_no")?, &String::new())?);
                            str566.push_str(": note overflow ");
                            str566.push_str(&format(&e.get("title")?, &String::new())?);
                            str566.push_str(": ");
                            str566.push_str(&format(
                                &binary("add", e.get("y")?, e.get("h")?)?,
                                &String::new(),
                            )?);
                            Val::Str(str566)
                        });
                        fun565.call(args563, kw564)?
                    })?
                );
            }
            {
                let fun569 = e.get("rect")?;
                let mut args567 = Vec::new();
                let mut kw568 = Vec::new();
                args567.push(e.get("x")?);
                args567.push(e.get("y")?);
                args567.push(e.get("w")?);
                args567.push(e.get("h")?);
                args567.push(
                    if {
                        let v570 = e.get("kind")?;
                        let v571 = Val::Str("blue".into());
                        Val::Bool(compare("eq", v570.clone(), v571.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        e.get("ICE")?
                    } else {
                        Val::Str("#FFF0E6".into())
                    },
                );
                kw568.push(("r".into(), Val::Int(6i64)));
                fun569.call(args567, kw568)?
            };
            {
                let fun574 = e.get("label")?;
                let mut args572 = Vec::new();
                let mut kw573 = Vec::new();
                args572.push(e.get("title")?);
                args572.push(binary("add", e.get("x")?, Val::Int(14i64))?);
                args572.push(binary("add", e.get("y")?, Val::Int(13i64))?);
                args572.push(
                    if {
                        let v575 = e.get("kind")?;
                        let v576 = Val::Str("blue".into());
                        Val::Bool(compare("eq", v575.clone(), v576.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        e.get("NAVY")?
                    } else {
                        Val::Str("#8B381B".into())
                    },
                );
                args572.push(Val::Int(8i64));
                fun574.call(args572, kw573)?
            };
            {
                let fun579 = e.get("para")?;
                let mut args577 = Vec::new();
                let mut kw578 = Vec::new();
                args577.push(e.get("s")?);
                args577.push(binary("add", e.get("x")?, Val::Int(14i64))?);
                args577.push(binary("add", e.get("y")?, Val::Int(32i64))?);
                args577.push(binary("sub", e.get("w")?, Val::Int(28i64))?);
                args577.push(Val::Int(12i64));
                args577.push(Val::Int(17i64));
                kw578.push(("limit".into(), binary("sub", e.get("h")?, Val::Int(32i64))?));
                fun579.call(args577, kw578)?
            };
            return Ok(e.get("h")?);
            Ok(Val::None)
        })
    })?;
    // item
    e.set("item", {
        let params = vec![
            ("n".into(), None, false),
            ("title".into(), None, false),
            ("s".into(), None, false),
            ("y".into(), None, false),
            ("x".into(), Some(e.get("RIGHT")?), false),
            ("w".into(), Some(e.get("RW")?), false),
            ("size".into(), Some(Val::Int(13i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun582 = e.get("label")?;
                let mut args580 = Vec::new();
                let mut kw581 = Vec::new();
                args580.push(e.get("n")?);
                args580.push(e.get("x")?);
                args580.push(e.get("y")?);
                fun582.call(args580, kw581)?
            };
            {
                let fun585 = e.get("text")?;
                let mut args583 = Vec::new();
                let mut kw584 = Vec::new();
                args583.push(e.get("title")?);
                args583.push(e.get("x")?);
                args583.push(binary("add", e.get("y")?, Val::Int(22i64))?);
                args583.push(Val::Int(16i64));
                args583.push(Val::Str("Bold".into()));
                args583.push(e.get("NAVY")?);
                fun585.call(args583, kw584)?
            };
            return Ok(binary("add", Val::Int(51i64), {
                let fun588 = e.get("para")?;
                let mut args586 = Vec::new();
                let mut kw587 = Vec::new();
                args586.push(e.get("s")?);
                args586.push(e.get("x")?);
                args586.push(binary("add", e.get("y")?, Val::Int(51i64))?);
                args586.push(e.get("w")?);
                args586.push(e.get("size")?);
                args586.push(Val::Int(18i64));
                fun588.call(args586, kw587)?
            })?);
            Ok(Val::None)
        })
    })?;
    // arrow
    e.set("arrow", {
        let params = vec![("head".into(), Some(Val::Int(9i64)), true)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, Some("points"), None)?;
            let _frame = rt.frame(&outer);
            let assigned589 = {
                let fun592 = e.get("list")?;
                let mut args590 = Vec::new();
                let mut kw591 = Vec::new();
                args590.push({
                    let fun595 = e.get("zip")?;
                    let mut args593 = Vec::new();
                    let mut kw594 = Vec::new();
                    args593.push(e.get("points")?.get(Val::Slice {
                        start: None,
                        stop: None,
                        step: Val::Int(2i64).integer()?,
                    })?);
                    args593.push(e.get("points")?.get(Val::Slice {
                        start: Some(Val::Int(1i64).integer()?),
                        stop: None,
                        step: Val::Int(2i64).integer()?,
                    })?);
                    fun595.call(args593, kw594)?
                });
                fun592.call(args590, kw591)?
            };
            e.set("path", assigned589.clone())?;
            let assigned596 = {
                let fun599 = e.get("path")?.attr("pop")?;
                let mut args597 = Vec::new();
                let mut kw598 = Vec::new();
                fun599.call(args597, kw598)?
            };
            let unpack600 = unpack(assigned596.clone(), 2)?;
            e.set("x2", unpack600[0].clone())?;
            e.set("y2", unpack600[1].clone())?;
            while {
                let v609 = {
                    let v613 = {
                        let fun612 = e.get("len")?;
                        let mut args610 = Vec::new();
                        let mut kw611 = Vec::new();
                        args610.push(e.get("path")?);
                        fun612.call(args610, kw611)?
                    };
                    let v614 = Val::Int(1i64);
                    Val::Bool(compare("gt", v613.clone(), v614.clone())?.truthy()?)
                };
                if v609.truthy()? {
                    {
                        let v607 = {
                            let fun606 = e.get("math")?.attr("hypot")?;
                            let mut args604 = Vec::new();
                            let mut kw605 = Vec::new();
                            args604.push(binary(
                                "sub",
                                e.get("x2")?,
                                e.get("path")?
                                    .get(unary("neg", Val::Int(1i64))?)?
                                    .get(Val::Int(0i64))?,
                            )?);
                            args604.push(binary(
                                "sub",
                                e.get("y2")?,
                                e.get("path")?
                                    .get(unary("neg", Val::Int(1i64))?)?
                                    .get(Val::Int(1i64))?,
                            )?);
                            fun606.call(args604, kw605)?
                        };
                        let v608 = e.get("head")?;
                        Val::Bool(compare("lt", v607.clone(), v608.clone())?.truthy()?)
                    }
                } else {
                    v609
                }
            }
            .truthy()?
            {
                {
                    let fun603 = e.get("path")?.attr("pop")?;
                    let mut args601 = Vec::new();
                    let mut kw602 = Vec::new();
                    fun603.call(args601, kw602)?
                };
            }
            let assigned615 = e.get("path")?.get(unary("neg", Val::Int(1i64))?)?;
            let unpack616 = unpack(assigned615.clone(), 2)?;
            e.set("x1", unpack616[0].clone())?;
            e.set("y1", unpack616[1].clone())?;
            let assigned617 = {
                let fun620 = e.get("math")?.attr("hypot")?;
                let mut args618 = Vec::new();
                let mut kw619 = Vec::new();
                args618.push(binary("sub", e.get("x2")?, e.get("x1")?)?);
                args618.push(binary("sub", e.get("y2")?, e.get("y1")?)?);
                fun620.call(args618, kw619)?
            };
            e.set("length", assigned617.clone())?;
            let assigned621 = {
                let mut s = Vec::new();
                s.push(binary(
                    "truediv",
                    binary("sub", e.get("x2")?, e.get("x1")?)?,
                    e.get("length")?,
                )?);
                s.push(binary(
                    "truediv",
                    binary("sub", e.get("y2")?, e.get("y1")?)?,
                    e.get("length")?,
                )?);
                Val::tuple(s)
            };
            let unpack622 = unpack(assigned621.clone(), 2)?;
            e.set("ux", unpack622[0].clone())?;
            e.set("uy", unpack622[1].clone())?;
            let assigned623 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("x2")?,
                    binary("mul", e.get("head")?, e.get("ux")?)?,
                )?);
                s.push(binary(
                    "sub",
                    e.get("y2")?,
                    binary("mul", e.get("head")?, e.get("uy")?)?,
                )?);
                Val::tuple(s)
            };
            let unpack624 = unpack(assigned623.clone(), 2)?;
            e.set("bx", unpack624[0].clone())?;
            e.set("by", unpack624[1].clone())?;
            let assigned625 = {
                let fun628 = e.get("c")?.attr("beginPath")?;
                let mut args626 = Vec::new();
                let mut kw627 = Vec::new();
                fun628.call(args626, kw627)?
            };
            e.set("shaft", assigned625.clone())?;
            {
                let fun631 = e.get("shaft")?.attr("moveTo")?;
                let mut args629 = Vec::new();
                let mut kw630 = Vec::new();
                args629.push(e.get("path")?.get(Val::Int(0i64))?.get(Val::Int(0i64))?);
                args629.push(binary(
                    "sub",
                    e.get("H")?,
                    e.get("path")?.get(Val::Int(0i64))?.get(Val::Int(1i64))?,
                )?);
                fun631.call(args629, kw630)?
            };
            for item632 in e
                .get("path")?
                .get(Val::Slice {
                    start: Some(Val::Int(1i64).integer()?),
                    stop: None,
                    step: 1,
                })?
                .iter()?
            {
                let unpack636 = unpack(item632, 2)?;
                e.set("x", unpack636[0].clone())?;
                e.set("y", unpack636[1].clone())?;
                {
                    let fun635 = e.get("shaft")?.attr("lineTo")?;
                    let mut args633 = Vec::new();
                    let mut kw634 = Vec::new();
                    args633.push(e.get("x")?);
                    args633.push(binary("sub", e.get("H")?, e.get("y")?)?);
                    fun635.call(args633, kw634)?
                };
            }
            {
                let fun639 = e.get("shaft")?.attr("lineTo")?;
                let mut args637 = Vec::new();
                let mut kw638 = Vec::new();
                args637.push(e.get("bx")?);
                args637.push(binary("sub", e.get("H")?, e.get("by")?)?);
                fun639.call(args637, kw638)?
            };
            let assigned640 = {
                let fun643 = e.get("c")?.attr("beginPath")?;
                let mut args641 = Vec::new();
                let mut kw642 = Vec::new();
                fun643.call(args641, kw642)?
            };
            e.set("tip", assigned640.clone())?;
            {
                let fun646 = e.get("tip")?.attr("moveTo")?;
                let mut args644 = Vec::new();
                let mut kw645 = Vec::new();
                args644.push(e.get("x2")?);
                args644.push(binary("sub", e.get("H")?, e.get("y2")?)?);
                fun646.call(args644, kw645)?
            };
            {
                let fun649 = e.get("tip")?.attr("lineTo")?;
                let mut args647 = Vec::new();
                let mut kw648 = Vec::new();
                args647.push(binary(
                    "sub",
                    e.get("bx")?,
                    binary(
                        "mul",
                        binary("mul", e.get("head")?, Val::Float(0.45f64))?,
                        e.get("uy")?,
                    )?,
                )?);
                args647.push(binary(
                    "sub",
                    binary("sub", e.get("H")?, e.get("by")?)?,
                    binary(
                        "mul",
                        binary("mul", e.get("head")?, Val::Float(0.45f64))?,
                        e.get("ux")?,
                    )?,
                )?);
                fun649.call(args647, kw648)?
            };
            {
                let fun652 = e.get("tip")?.attr("lineTo")?;
                let mut args650 = Vec::new();
                let mut kw651 = Vec::new();
                args650.push(binary(
                    "add",
                    e.get("bx")?,
                    binary(
                        "mul",
                        binary("mul", e.get("head")?, Val::Float(0.45f64))?,
                        e.get("uy")?,
                    )?,
                )?);
                args650.push(binary(
                    "add",
                    binary("sub", e.get("H")?, e.get("by")?)?,
                    binary(
                        "mul",
                        binary("mul", e.get("head")?, Val::Float(0.45f64))?,
                        e.get("ux")?,
                    )?,
                )?);
                fun652.call(args650, kw651)?
            };
            {
                let fun655 = e.get("tip")?.attr("close")?;
                let mut args653 = Vec::new();
                let mut kw654 = Vec::new();
                fun655.call(args653, kw654)?
            };
            {
                let fun658 = e.get("c")?.attr("saveState")?;
                let mut args656 = Vec::new();
                let mut kw657 = Vec::new();
                fun658.call(args656, kw657)?
            };
            {
                let fun661 = e.get("c")?.attr("setLineCap")?;
                let mut args659 = Vec::new();
                let mut kw660 = Vec::new();
                args659.push(Val::Int(1i64));
                fun661.call(args659, kw660)?
            };
            for item662 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("white")?);
                    s.push(Val::Float(4.8f64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push({
                        let fun682 = e.get("HexColor")?;
                        let mut args680 = Vec::new();
                        let mut kw681 = Vec::new();
                        args680.push(e.get("CORAL")?);
                        fun682.call(args680, kw681)?
                    });
                    s.push(Val::Float(2.7f64));
                    Val::tuple(s)
                });
                Val::list(s)
            }
            .iter()?
            {
                let unpack683 = unpack(item662, 2)?;
                e.set("color", unpack683[0].clone())?;
                e.set("width", unpack683[1].clone())?;
                {
                    let fun665 = e.get("c")?.attr("setStrokeColor")?;
                    let mut args663 = Vec::new();
                    let mut kw664 = Vec::new();
                    args663.push(e.get("color")?);
                    fun665.call(args663, kw664)?
                };
                {
                    let fun668 = e.get("c")?.attr("setFillColor")?;
                    let mut args666 = Vec::new();
                    let mut kw667 = Vec::new();
                    args666.push(e.get("color")?);
                    fun668.call(args666, kw667)?
                };
                {
                    let fun671 = e.get("c")?.attr("setLineWidth")?;
                    let mut args669 = Vec::new();
                    let mut kw670 = Vec::new();
                    args669.push(e.get("width")?);
                    fun671.call(args669, kw670)?
                };
                {
                    let fun674 = e.get("c")?.attr("drawPath")?;
                    let mut args672 = Vec::new();
                    let mut kw673 = Vec::new();
                    args672.push(e.get("shaft")?);
                    kw673.push(("stroke".into(), Val::Int(1i64)));
                    fun674.call(args672, kw673)?
                };
                {
                    let fun677 = e.get("c")?.attr("drawPath")?;
                    let mut args675 = Vec::new();
                    let mut kw676 = Vec::new();
                    args675.push(e.get("tip")?);
                    kw676.push(("fill".into(), Val::Int(1i64)));
                    kw676.push((
                        "stroke".into(),
                        if {
                            let v678 = e.get("color")?;
                            let v679 = e.get("white")?;
                            Val::Bool(compare("eq", v678.clone(), v679.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            Val::Int(1i64)
                        } else {
                            Val::Int(0i64)
                        },
                    ));
                    fun677.call(args675, kw676)?
                };
            }
            {
                let fun686 = e.get("c")?.attr("restoreState")?;
                let mut args684 = Vec::new();
                let mut kw685 = Vec::new();
                fun686.call(args684, kw685)?
            };
            Ok(Val::None)
        })
    })?;
    // leader
    e.set("leader", {
        let params = vec![
            ("s".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("point".into(), None, false),
            ("side".into(), Some(Val::Str("right".into())), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun689 = e.get("text")?;
                let mut args687 = Vec::new();
                let mut kw688 = Vec::new();
                args687.push(e.get("s")?);
                args687.push(e.get("x")?);
                args687.push(e.get("y")?);
                args687.push(Val::Int(10i64));
                args687.push(Val::Str("Semibold".into()));
                args687.push(e.get("INK")?);
                fun689.call(args687, kw688)?
            };
            let assigned690 = {
                let fun693 = e.get("pdfmetrics")?.attr("stringWidth")?;
                let mut args691 = Vec::new();
                let mut kw692 = Vec::new();
                args691.push(e.get("s")?);
                args691.push(Val::Str("Semibold".into()));
                args691.push(Val::Int(10i64));
                fun693.call(args691, kw692)?
            };
            e.set("width", assigned690.clone())?;
            let assigned694 = if {
                let v695 = e.get("side")?;
                let v696 = Val::Str("right".into());
                Val::Bool(compare("eq", v695.clone(), v696.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        binary("add", e.get("x")?, e.get("width")?)?,
                        Val::Int(6i64),
                    )?);
                    s.push(binary("add", e.get("y")?, Val::Int(4i64))?);
                    Val::tuple(s)
                }
            } else {
                {
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("x")?, Val::Int(6i64))?);
                    s.push(binary("add", e.get("y")?, Val::Int(4i64))?);
                    Val::tuple(s)
                }
            };
            e.set("start", assigned694.clone())?;
            for item697 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("#FFFFFF".into()));
                    s.push(Val::Int(3i64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("INK")?);
                    s.push(Val::Float(0.8f64));
                    Val::tuple(s)
                });
                Val::list(s)
            }
            .iter()?
            {
                let unpack701 = unpack(item697, 2)?;
                e.set("color", unpack701[0].clone())?;
                e.set("stroke", unpack701[1].clone())?;
                {
                    let fun700 = e.get("line")?;
                    let mut args698 = Vec::new();
                    let mut kw699 = Vec::new();
                    args698.extend(e.get("start")?.iter()?);
                    args698.extend(e.get("point")?.iter()?);
                    args698.push(e.get("color")?);
                    args698.push(e.get("stroke")?);
                    fun700.call(args698, kw699)?
                };
            }
            {
                let fun704 = e.get("c")?.attr("setFillColor")?;
                let mut args702 = Vec::new();
                let mut kw703 = Vec::new();
                args702.push({
                    let fun707 = e.get("HexColor")?;
                    let mut args705 = Vec::new();
                    let mut kw706 = Vec::new();
                    args705.push(e.get("CORAL")?);
                    fun707.call(args705, kw706)?
                });
                fun704.call(args702, kw703)?
            };
            {
                let fun710 = e.get("c")?.attr("setStrokeColor")?;
                let mut args708 = Vec::new();
                let mut kw709 = Vec::new();
                args708.push(e.get("white")?);
                fun710.call(args708, kw709)?
            };
            {
                let fun713 = e.get("c")?.attr("setLineWidth")?;
                let mut args711 = Vec::new();
                let mut kw712 = Vec::new();
                args711.push(Val::Float(0.8f64));
                fun713.call(args711, kw712)?
            };
            {
                let fun716 = e.get("c")?.attr("circle")?;
                let mut args714 = Vec::new();
                let mut kw715 = Vec::new();
                args714.push(e.get("point")?.get(Val::Int(0i64))?);
                args714.push(binary(
                    "sub",
                    e.get("H")?,
                    e.get("point")?.get(Val::Int(1i64))?,
                )?);
                args714.push(Val::Float(2.5f64));
                kw715.push(("fill".into(), Val::Int(1i64)));
                kw715.push(("stroke".into(), Val::Int(1i64)));
                fun716.call(args714, kw715)?
            };
            Ok(Val::None)
        })
    })?;
    // projected
    e.set("projected", {
        let params = vec![
            ("mapper".into(), None, false),
            ("point".into(), None, false),
            ("cam".into(), None, false),
            ("target".into(), None, false),
            ("span".into(), None, false),
            (
                "size".into(),
                Some({
                    let mut s = Vec::new();
                    s.push(Val::Int(1600i64));
                    s.push(Val::Int(1500i64));
                    Val::tuple(s)
                }),
                false,
            ),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer); // unit
            e.set("unit", {
                let params = vec![("v".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned717 = {
                        let fun720 = e.get("math")?.attr("sqrt")?;
                        let mut args718 = Vec::new();
                        let mut kw719 = Vec::new();
                        args718.push({
                            let fun723 = e.get("sum")?;
                            let mut args721 = Vec::new();
                            let mut kw722 = Vec::new();
                            args721.push({
                                let e = e.child();
                                let out724 = Val::list(vec![]);
                                for item725 in e.get("v")?.iter()? {
                                    e.set("t", item725)?;
                                    out724.attr("append")?.call(
                                        vec![binary("mul", e.get("t")?, e.get("t")?)?],
                                        vec![],
                                    )?;
                                }
                                out724
                            });
                            fun723.call(args721, kw722)?
                        });
                        fun720.call(args718, kw719)?
                    };
                    e.set("length", assigned717.clone())?;
                    return Ok({
                        let fun728 = e.get("tuple")?;
                        let mut args726 = Vec::new();
                        let mut kw727 = Vec::new();
                        args726.push({
                            let e = e.child();
                            let out729 = Val::list(vec![]);
                            for item730 in e.get("v")?.iter()? {
                                e.set("t", item730)?;
                                out729.attr("append")?.call(
                                    vec![binary("truediv", e.get("t")?, e.get("length")?)?],
                                    vec![],
                                )?;
                            }
                            out729
                        });
                        fun728.call(args726, kw727)?
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
                        Val::tuple(s)
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned731 = {
                let fun734 = e.get("unit")?;
                let mut args732 = Vec::new();
                let mut kw733 = Vec::new();
                args732.push(e.get("cam")?);
                fun734.call(args732, kw733)?
            };
            e.set("direction", assigned731.clone())?;
            let assigned735 = {
                let fun738 = e.get("unit")?;
                let mut args736 = Vec::new();
                let mut kw737 = Vec::new();
                args736.push({
                    let fun741 = e.get("cross")?;
                    let mut args739 = Vec::new();
                    let mut kw740 = Vec::new();
                    args739.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        Val::tuple(s)
                    });
                    args739.push(e.get("direction")?);
                    fun741.call(args739, kw740)?
                });
                fun738.call(args736, kw737)?
            };
            e.set("right", assigned735.clone())?;
            let assigned742 = {
                let fun745 = e.get("cross")?;
                let mut args743 = Vec::new();
                let mut kw744 = Vec::new();
                args743.push(e.get("direction")?);
                args743.push(e.get("right")?);
                fun745.call(args743, kw744)?
            };
            e.set("up", assigned742.clone())?;
            let assigned746 = {
                let fun749 = e.get("tuple")?;
                let mut args747 = Vec::new();
                let mut kw748 = Vec::new();
                args747.push({
                    let e = e.child();
                    let out750 = Val::list(vec![]);
                    for item751 in {
                        let fun754 = e.get("zip")?;
                        let mut args752 = Vec::new();
                        let mut kw753 = Vec::new();
                        args752.push(e.get("point")?);
                        args752.push(e.get("target")?);
                        fun754.call(args752, kw753)?
                    }
                    .iter()?
                    {
                        let unpack755 = unpack(item751, 2)?;
                        e.set("p", unpack755[0].clone())?;
                        e.set("t", unpack755[1].clone())?;
                        out750
                            .attr("append")?
                            .call(vec![binary("sub", e.get("p")?, e.get("t")?)?], vec![])?;
                    }
                    out750
                });
                fun749.call(args747, kw748)?
            };
            e.set("delta", assigned746.clone())?;
            let assigned756 = binary(
                "truediv",
                e.get("size")?.get(Val::Int(1i64))?,
                binary("mul", Val::Int(2i64), e.get("span")?)?,
            )?;
            e.set("scale", assigned756.clone())?;
            return Ok({
                let fun759 = e.get("mapper")?;
                let mut args757 = Vec::new();
                let mut kw758 = Vec::new();
                args757.push(binary(
                    "add",
                    binary(
                        "truediv",
                        e.get("size")?.get(Val::Int(0i64))?,
                        Val::Int(2i64),
                    )?,
                    binary(
                        "mul",
                        {
                            let fun762 = e.get("sum")?;
                            let mut args760 = Vec::new();
                            let mut kw761 = Vec::new();
                            args760.push({
                                let e = e.child();
                                let out763 = Val::list(vec![]);
                                for item764 in {
                                    let fun767 = e.get("zip")?;
                                    let mut args765 = Vec::new();
                                    let mut kw766 = Vec::new();
                                    args765.push(e.get("delta")?);
                                    args765.push(e.get("right")?);
                                    fun767.call(args765, kw766)?
                                }
                                .iter()?
                                {
                                    let unpack768 = unpack(item764, 2)?;
                                    e.set("a", unpack768[0].clone())?;
                                    e.set("b", unpack768[1].clone())?;
                                    out763.attr("append")?.call(
                                        vec![binary("mul", e.get("a")?, e.get("b")?)?],
                                        vec![],
                                    )?;
                                }
                                out763
                            });
                            fun762.call(args760, kw761)?
                        },
                        e.get("scale")?,
                    )?,
                )?);
                args757.push(binary(
                    "sub",
                    binary(
                        "truediv",
                        e.get("size")?.get(Val::Int(1i64))?,
                        Val::Int(2i64),
                    )?,
                    binary(
                        "mul",
                        {
                            let fun771 = e.get("sum")?;
                            let mut args769 = Vec::new();
                            let mut kw770 = Vec::new();
                            args769.push({
                                let e = e.child();
                                let out772 = Val::list(vec![]);
                                for item773 in {
                                    let fun776 = e.get("zip")?;
                                    let mut args774 = Vec::new();
                                    let mut kw775 = Vec::new();
                                    args774.push(e.get("delta")?);
                                    args774.push(e.get("up")?);
                                    fun776.call(args774, kw775)?
                                }
                                .iter()?
                                {
                                    let unpack777 = unpack(item773, 2)?;
                                    e.set("a", unpack777[0].clone())?;
                                    e.set("b", unpack777[1].clone())?;
                                    out772.attr("append")?.call(
                                        vec![binary("mul", e.get("a")?, e.get("b")?)?],
                                        vec![],
                                    )?;
                                }
                                out772
                            });
                            fun771.call(args769, kw770)?
                        },
                        e.get("scale")?,
                    )?,
                )?);
                fun759.call(args757, kw758)?
            });
            Ok(Val::None)
        })
    })?;
    // mounting_slots
    e.set("mounting_slots", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned778 = binary(
                "truediv",
                e.get("ROOT")?,
                Val::Str("hardware/cut-parts/faucet/under-counter-plate".into()),
            )?;
            e.set("plate_dir", assigned778.clone())?;
            let assigned779 = {
                let mut s = Vec::new();
                s.push(binary(
                    "truediv",
                    e.get("plate_dir")?,
                    Val::Str("under-counter-plate.dxf".into()),
                )?);
                s.push(binary(
                    "truediv",
                    e.get("plate_dir")?,
                    Val::Str("under_counter_plate.py".into()),
                )?);
                s.push(binary(
                    "truediv",
                    e.get("ROOT")?,
                    Val::Str("hardware/printed-parts/faucet/faucet_paths.py".into()),
                )?);
                s.push(binary(
                    "truediv",
                    e.get("ROOT")?,
                    Val::Str("hardware/faucet-layout/faucet_assembly.py".into()),
                )?);
                s.push(binary(
                    "truediv",
                    e.get("ROOT")?,
                    Val::Str("hardware/printed-parts/faucet/faucet-shell/faucet_shell.py".into()),
                )?);
                s.push(binary(
                    "truediv",
                    e.get("ROOT")?,
                    Val::Str("tools/hsm/faucet-data/src/lib.rs".into()),
                )?);
                Val::list(s)
            };
            e.set("sources", assigned779.clone())?;
            // literals
            e.set("literals", {
                let params = vec![("path".into(), None, false), ("names".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let mod780 = rt.import_module("docgen")?;
                    e.set("load_module", rt.member("docgen", "load_module")?)?;
                    let assigned781 = {
                        let fun784 = e.get("load_module")?;
                        let mut args782 = Vec::new();
                        let mut kw783 = Vec::new();
                        args782.push(Val::Str("guide_faucet_dimensions".into()));
                        args782.push(e.get("path")?);
                        fun784.call(args782, kw783)?
                    };
                    e.set("provider", assigned781.clone())?;
                    return Ok({
                        let e = e.child();
                        let out785 = Val::dict(vec![]);
                        for item786 in e.get("names")?.iter()? {
                            e.set("name", item786)?;
                            out785.set(e.get("name")?, {
                                let fun789 = e.get("float")?;
                                let mut args787 = Vec::new();
                                let mut kw788 = Vec::new();
                                args787.push({
                                    let fun792 = e.get("getattr")?;
                                    let mut args790 = Vec::new();
                                    let mut kw791 = Vec::new();
                                    args790.push(e.get("provider")?);
                                    args790.push(e.get("name")?);
                                    fun792.call(args790, kw791)?
                                });
                                fun789.call(args787, kw788)?
                            })?;
                        }
                        out785
                    });
                    Ok(Val::None)
                })
            })?;
            {
                let fun795 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args793 = Vec::new();
                let mut kw794 = Vec::new();
                args793.push(Val::Int(0i64));
                args793.push({
                    let fun798 = e.get("str")?;
                    let mut args796 = Vec::new();
                    let mut kw797 = Vec::new();
                    args796.push(binary(
                        "truediv",
                        e.get("ROOT")?,
                        Val::Str("hardware/printed-parts/faucet".into()),
                    )?);
                    fun798.call(args796, kw797)?
                });
                fun795.call(args793, kw794)?
            };
            e.set("faucet_paths", rt.import_module("faucet_paths")?)?;
            let assigned799 = {
                let e = e.child();
                let out800 = Val::dict(vec![]);
                for item801 in {
                    let mut s = Vec::new();
                    s.push(Val::Str("FLAVOR_OD".into()));
                    s.push(Val::Str("DRAIN_OD".into()));
                    s.push(Val::Str("LOWER_FLAVOR_X".into()));
                    s.push(Val::Str("LOWER_BUNDLE_X".into()));
                    s.push(Val::Str("LOWER_Y".into()));
                    s.push(Val::Str("LOWER_DRAIN_Y".into()));
                    s.push(Val::Str("LOWER_RIBBON_Y".into()));
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("name", item801)?;
                    out800.set(e.get("name")?, {
                        let fun804 = e.get("float")?;
                        let mut args802 = Vec::new();
                        let mut kw803 = Vec::new();
                        args802.push({
                            let fun807 = e.get("getattr")?;
                            let mut args805 = Vec::new();
                            let mut kw806 = Vec::new();
                            args805.push(e.get("faucet_paths")?);
                            args805.push(e.get("name")?);
                            fun807.call(args805, kw806)?
                        });
                        fun804.call(args802, kw803)?
                    })?;
                }
                out800
            };
            e.set("coords", assigned799.clone())?;
            let assigned808 = {
                let fun811 = e.get("literals")?;
                let mut args809 = Vec::new();
                let mut kw810 = Vec::new();
                args809.push(e.get("sources")?.get(Val::Int(3i64))?);
                args809.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("shank_od".into()));
                    Val::tuple(s)
                });
                fun811.call(args809, kw810)?
            }
            .get(Val::Str("shank_od".into()))?;
            e.set("shank", assigned808.clone())?;
            let assigned812 = {
                let e = e.child();
                let out813 = Val::dict(vec![]);
                for item814 in {
                    let mut s = Vec::new();
                    s.push(Val::Str("RIBBON_WIDTH".into()));
                    s.push(Val::Str("RIBBON_DEPTH".into()));
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("name", item814)?;
                    out813.set(e.get("name")?, {
                        let fun817 = e.get("float")?;
                        let mut args815 = Vec::new();
                        let mut kw816 = Vec::new();
                        args815.push({
                            let fun820 = e.get("getattr")?;
                            let mut args818 = Vec::new();
                            let mut kw819 = Vec::new();
                            args818.push(e.get("faucet_paths")?);
                            args818.push(e.get("name")?);
                            fun820.call(args818, kw819)?
                        });
                        fun817.call(args815, kw816)?
                    })?;
                }
                out813
            };
            e.set("cable", assigned812.clone())?;
            let assigned821 = {
                let fun824 = e.get("ezdxf")?.attr("readfile")?;
                let mut args822 = Vec::new();
                let mut kw823 = Vec::new();
                args822.push(e.get("sources")?.get(Val::Int(0i64))?);
                fun824.call(args822, kw823)?
            };
            e.set("drawing", assigned821.clone())?;
            if {
                let v828 = {
                    let fun827 = e.get("drawing")?.attr("header")?.attr("get")?;
                    let mut args825 = Vec::new();
                    let mut kw826 = Vec::new();
                    args825.push(Val::Str("$INSUNITS".into()));
                    fun827.call(args825, kw826)?
                };
                let v829 = Val::Int(4i64);
                Val::Bool(compare("ne", v828.clone(), v829.clone())?.truthy()?)
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun832 = e.get("ValueError")?;
                        let mut args830 = Vec::new();
                        let mut kw831 = Vec::new();
                        args830.push(Val::Str(
                            "The mounting-slot diagram requires a millimetre DXF".into(),
                        ));
                        fun832.call(args830, kw831)?
                    })?
                );
            }
            let assigned833 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("segments", assigned833.clone())?;
            for item834 in {
                let fun891 = e.get("drawing")?.attr("modelspace")?;
                let mut args889 = Vec::new();
                let mut kw890 = Vec::new();
                fun891.call(args889, kw890)?
            }
            .iter()?
            {
                e.set("entity", item834)?;
                if {
                    let v838 = {
                        let fun837 = e.get("entity")?.attr("dxftype")?;
                        let mut args835 = Vec::new();
                        let mut kw836 = Vec::new();
                        fun837.call(args835, kw836)?
                    };
                    let v839 = Val::Str("LINE".into());
                    Val::Bool(compare("eq", v838.clone(), v839.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned840 = {
                        let mut s = Vec::new();
                        s.push(e.get("entity")?.attr("dxf")?.attr("start")?);
                        s.push(e.get("entity")?.attr("dxf")?.attr("end")?);
                        Val::tuple(s)
                    };
                    let unpack841 = unpack(assigned840.clone(), 2)?;
                    e.set("start", unpack841[0].clone())?;
                    e.set("finish", unpack841[1].clone())?;
                    {
                        let fun844 = e.get("segments")?.attr("append")?;
                        let mut args842 = Vec::new();
                        let mut kw843 = Vec::new();
                        args842.push({
                            let mut s = Vec::new();
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("start")?.attr("x")?);
                                s.push(e.get("start")?.attr("y")?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("finish")?.attr("x")?);
                                s.push(e.get("finish")?.attr("y")?);
                                Val::tuple(s)
                            });
                            Val::list(s)
                        });
                        fun844.call(args842, kw843)?
                    };
                } else {
                    if {
                        let v848 = {
                            let fun847 = e.get("entity")?.attr("dxftype")?;
                            let mut args845 = Vec::new();
                            let mut kw846 = Vec::new();
                            fun847.call(args845, kw846)?
                        };
                        let v849 = Val::Str("ARC".into());
                        Val::Bool(compare("eq", v848.clone(), v849.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        let assigned850 = {
                            let mut s = Vec::new();
                            s.push(e.get("entity")?.attr("dxf")?.attr("center")?);
                            s.push(e.get("entity")?.attr("dxf")?.attr("radius")?);
                            Val::tuple(s)
                        };
                        let unpack851 = unpack(assigned850.clone(), 2)?;
                        e.set("center", unpack851[0].clone())?;
                        e.set("radius", unpack851[1].clone())?;
                        let assigned852 = {
                            let mut s = Vec::new();
                            s.push(e.get("entity")?.attr("dxf")?.attr("start_angle")?);
                            s.push(e.get("entity")?.attr("dxf")?.attr("end_angle")?);
                            Val::tuple(s)
                        };
                        let unpack853 = unpack(assigned852.clone(), 2)?;
                        e.set("start", unpack853[0].clone())?;
                        e.set("finish", unpack853[1].clone())?;
                        let assigned854 = binary(
                            "mod",
                            binary("sub", e.get("finish")?, e.get("start")?)?,
                            Val::Int(360i64),
                        )?;
                        e.set("sweep", assigned854.clone())?;
                        let assigned855 = {
                            let fun858 = e.get("max")?;
                            let mut args856 = Vec::new();
                            let mut kw857 = Vec::new();
                            args856.push(Val::Int(1i64));
                            args856.push({
                                let fun861 = e.get("math")?.attr("ceil")?;
                                let mut args859 = Vec::new();
                                let mut kw860 = Vec::new();
                                args859.push(e.get("sweep")?);
                                fun861.call(args859, kw860)?
                            });
                            fun858.call(args856, kw857)?
                        };
                        e.set("count", assigned855.clone())?;
                        {
                            let fun864 = e.get("segments")?.attr("append")?;
                            let mut args862 = Vec::new();
                            let mut kw863 = Vec::new();
                            args862.push({
                                let e = e.child();
                                let out865 = Val::list(vec![]);
                                for item866 in {
                                    let fun869 = e.get("range")?;
                                    let mut args867 = Vec::new();
                                    let mut kw868 = Vec::new();
                                    args867.push(binary("add", e.get("count")?, Val::Int(1i64))?);
                                    fun869.call(args867, kw868)?
                                }
                                .iter()?
                                {
                                    e.set("i", item866)?;
                                    out865.attr("append")?.call(
                                        vec![{
                                            let mut s = Vec::new();
                                            s.push(binary(
                                                "add",
                                                e.get("center")?.attr("x")?,
                                                binary("mul", e.get("radius")?, {
                                                    let fun872 = e.get("math")?.attr("cos")?;
                                                    let mut args870 = Vec::new();
                                                    let mut kw871 = Vec::new();
                                                    args870.push({
                                                        let fun875 =
                                                            e.get("math")?.attr("radians")?;
                                                        let mut args873 = Vec::new();
                                                        let mut kw874 = Vec::new();
                                                        args873.push(binary(
                                                            "add",
                                                            e.get("start")?,
                                                            binary(
                                                                "truediv",
                                                                binary(
                                                                    "mul",
                                                                    e.get("sweep")?,
                                                                    e.get("i")?,
                                                                )?,
                                                                e.get("count")?,
                                                            )?,
                                                        )?);
                                                        fun875.call(args873, kw874)?
                                                    });
                                                    fun872.call(args870, kw871)?
                                                })?,
                                            )?);
                                            s.push(binary(
                                                "add",
                                                e.get("center")?.attr("y")?,
                                                binary("mul", e.get("radius")?, {
                                                    let fun878 = e.get("math")?.attr("sin")?;
                                                    let mut args876 = Vec::new();
                                                    let mut kw877 = Vec::new();
                                                    args876.push({
                                                        let fun881 =
                                                            e.get("math")?.attr("radians")?;
                                                        let mut args879 = Vec::new();
                                                        let mut kw880 = Vec::new();
                                                        args879.push(binary(
                                                            "add",
                                                            e.get("start")?,
                                                            binary(
                                                                "truediv",
                                                                binary(
                                                                    "mul",
                                                                    e.get("sweep")?,
                                                                    e.get("i")?,
                                                                )?,
                                                                e.get("count")?,
                                                            )?,
                                                        )?);
                                                        fun881.call(args879, kw880)?
                                                    });
                                                    fun878.call(args876, kw877)?
                                                })?,
                                            )?);
                                            Val::tuple(s)
                                        }],
                                        vec![],
                                    )?;
                                }
                                out865
                            });
                            fun864.call(args862, kw863)?
                        };
                    } else {
                        anyhow::bail!(
                            "{}",
                            val_string({
                                let fun884 = e.get("ValueError")?;
                                let mut args882 = Vec::new();
                                let mut kw883 = Vec::new();
                                args882.push({
                                    let mut str885 = String::new();
                                    str885.push_str("Unsupported steel-outline entity: ");
                                    str885.push_str(&format(
                                        &{
                                            let fun888 = e.get("entity")?.attr("dxftype")?;
                                            let mut args886 = Vec::new();
                                            let mut kw887 = Vec::new();
                                            fun888.call(args886, kw887)?
                                        },
                                        &String::new(),
                                    )?);
                                    Val::Str(str885)
                                });
                                fun884.call(args882, kw883)?
                            })?
                        );
                    }
                }
            }
            let assigned892 = {
                let fun895 = e.get("segments")?.attr("pop")?;
                let mut args893 = Vec::new();
                let mut kw894 = Vec::new();
                args893.push(Val::Int(0i64));
                fun895.call(args893, kw894)?
            };
            e.set("outline", assigned892.clone())?;
            while e.get("segments")?.truthy()? {
                let assigned896 = {
                    let fun899 = e.get("next")?;
                    let mut args897 = Vec::new();
                    let mut kw898 = Vec::new();
                    args897.push({
                        let e = e.child();
                        let out900 = Val::list(vec![]);
                        for item901 in {
                            let fun904 = e.get("enumerate")?;
                            let mut args902 = Vec::new();
                            let mut kw903 = Vec::new();
                            args902.push(e.get("segments")?);
                            fun904.call(args902, kw903)?
                        }
                        .iter()?
                        {
                            let unpack905 = unpack(item901, 2)?;
                            e.set("i", unpack905[0].clone())?;
                            e.set("points", unpack905[1].clone())?;
                            for item906 in {
                                let mut s = Vec::new();
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(Val::Bool(false));
                                    s.push(e.get("points")?.get(Val::Int(0i64))?);
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(Val::Bool(true));
                                    s.push(e.get("points")?.get(unary("neg", Val::Int(1i64))?)?);
                                    Val::tuple(s)
                                });
                                Val::tuple(s)
                            }
                            .iter()?
                            {
                                let unpack907 = unpack(item906, 2)?;
                                e.set("reverse", unpack907[0].clone())?;
                                e.set("endpoint", unpack907[1].clone())?;
                                if {
                                    let v911 = {
                                        let fun910 = e.get("math")?.attr("dist")?;
                                        let mut args908 = Vec::new();
                                        let mut kw909 = Vec::new();
                                        args908.push(
                                            e.get("outline")?.get(unary("neg", Val::Int(1i64))?)?,
                                        );
                                        args908.push(e.get("endpoint")?);
                                        fun910.call(args908, kw909)?
                                    };
                                    let v912 = Val::Float(1e-06f64);
                                    Val::Bool(compare("lt", v911.clone(), v912.clone())?.truthy()?)
                                }
                                .truthy()?
                                {
                                    out900.attr("append")?.call(
                                        vec![{
                                            let mut s = Vec::new();
                                            s.push(e.get("i")?);
                                            s.push(e.get("reverse")?);
                                            Val::tuple(s)
                                        }],
                                        vec![],
                                    )?;
                                }
                            }
                        }
                        out900
                    });
                    args897.push(Val::None);
                    fun899.call(args897, kw898)?
                };
                e.set("match", assigned896.clone())?;
                if {
                    let v913 = e.get("match")?;
                    let v914 = Val::None;
                    Val::Bool(compare("is", v913.clone(), v914.clone())?.truthy()?)
                }
                .truthy()?
                {
                    anyhow::bail!(
                        "{}",
                        val_string({
                            let fun917 = e.get("ValueError")?;
                            let mut args915 = Vec::new();
                            let mut kw916 = Vec::new();
                            args915.push(Val::Str(
                                "The mounting steel outline is not one continuous boundary".into(),
                            ));
                            fun917.call(args915, kw916)?
                        })?
                    );
                }
                let assigned918 = e.get("match")?;
                let unpack919 = unpack(assigned918.clone(), 2)?;
                e.set("i", unpack919[0].clone())?;
                e.set("reverse", unpack919[1].clone())?;
                let assigned920 = {
                    let fun923 = e.get("segments")?.attr("pop")?;
                    let mut args921 = Vec::new();
                    let mut kw922 = Vec::new();
                    args921.push(e.get("i")?);
                    fun923.call(args921, kw922)?
                };
                e.set("points", assigned920.clone())?;
                {
                    let fun926 = e.get("outline")?.attr("extend")?;
                    let mut args924 = Vec::new();
                    let mut kw925 = Vec::new();
                    args924.push(
                        if e.get("reverse")?.truthy()? {
                            e.get("points")?.get(Val::Slice {
                                start: None,
                                stop: None,
                                step: unary("neg", Val::Int(1i64))?.integer()?,
                            })?
                        } else {
                            e.get("points")?
                        }
                        .get(Val::Slice {
                            start: Some(Val::Int(1i64).integer()?),
                            stop: None,
                            step: 1,
                        })?,
                    );
                    fun926.call(args924, kw925)?
                };
            }
            if {
                let v930 = {
                    let fun929 = e.get("math")?.attr("dist")?;
                    let mut args927 = Vec::new();
                    let mut kw928 = Vec::new();
                    args927.push(e.get("outline")?.get(Val::Int(0i64))?);
                    args927.push(e.get("outline")?.get(unary("neg", Val::Int(1i64))?)?);
                    fun929.call(args927, kw928)?
                };
                let v931 = Val::Float(1e-06f64);
                Val::Bool(compare("gt", v930.clone(), v931.clone())?.truthy()?)
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun934 = e.get("ValueError")?;
                        let mut args932 = Vec::new();
                        let mut kw933 = Vec::new();
                        args932.push(Val::Str("The mounting steel outline is open".into()));
                        fun934.call(args932, kw933)?
                    })?
                );
            }
            {
                let fun937 = e.get("rect")?;
                let mut args935 = Vec::new();
                let mut kw936 = Vec::new();
                args935.push(e.get("M")?);
                args935.push(Val::Int(282i64));
                args935.push(e.get("CW")?);
                args935.push(Val::Int(158i64));
                args935.push(Val::Str("#F5F7FC".into()));
                kw936.push(("r".into(), Val::Int(6i64)));
                fun937.call(args935, kw936)?
            };
            {
                let fun940 = e.get("text")?;
                let mut args938 = Vec::new();
                let mut kw939 = Vec::new();
                args938.push(Val::Str("Back / toward wall".into()));
                args938.push(binary("add", e.get("M")?, Val::Int(12i64))?);
                args938.push(Val::Int(286i64));
                args938.push(Val::Int(8i64));
                args938.push(Val::Str("Semibold".into()));
                args938.push(e.get("MUTED")?);
                fun940.call(args938, kw939)?
            };
            {
                let fun943 = e.get("text")?;
                let mut args941 = Vec::new();
                let mut kw942 = Vec::new();
                args941.push(Val::Str(
                    "Plate seen from below; washer and nut omitted.".into(),
                ));
                args941.push(Val::Int(350i64));
                args941.push(Val::Int(286i64));
                args941.push(Val::Int(8i64));
                args941.push(Val::Str("Regular".into()));
                args941.push(e.get("MUTED")?);
                fun943.call(args941, kw942)?
            };
            let assigned944 = {
                let mut s = Vec::new();
                s.push(Val::Float(2.5f64));
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(144i64));
                    s.push(Val::Int(371i64));
                    Val::tuple(s)
                });
                Val::tuple(s)
            };
            let unpack945 = unpack(assigned944.clone(), 2)?;
            e.set("scale", unpack945[0].clone())?;
            e.set("center", unpack945[1].clone())?;
            // at
            e.set("at", {
                let params = vec![("x".into(), None, false), ("y".into(), None, false)];
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
                            e.get("center")?.get(Val::Int(0i64))?,
                            binary("mul", e.get("x")?, e.get("scale")?)?,
                        )?);
                        s.push(binary(
                            "sub",
                            e.get("center")?.get(Val::Int(1i64))?,
                            binary("mul", e.get("y")?, e.get("scale")?)?,
                        )?);
                        Val::tuple(s)
                    });
                    Ok(Val::None)
                })
            })?;
            {
                let fun948 = e.get("c")?.attr("saveState")?;
                let mut args946 = Vec::new();
                let mut kw947 = Vec::new();
                fun948.call(args946, kw947)?
            };
            {
                let fun951 = e.get("c")?.attr("setLineWidth")?;
                let mut args949 = Vec::new();
                let mut kw950 = Vec::new();
                args949.push(Val::Float(0.8f64));
                fun951.call(args949, kw950)?
            };
            {
                let fun954 = e.get("c")?.attr("setStrokeColor")?;
                let mut args952 = Vec::new();
                let mut kw953 = Vec::new();
                args952.push({
                    let fun957 = e.get("HexColor")?;
                    let mut args955 = Vec::new();
                    let mut kw956 = Vec::new();
                    args955.push(Val::Str("#46515b".into()));
                    fun957.call(args955, kw956)?
                });
                fun954.call(args952, kw953)?
            };
            {
                let fun960 = e.get("c")?.attr("setFillColor")?;
                let mut args958 = Vec::new();
                let mut kw959 = Vec::new();
                args958.push({
                    let fun963 = e.get("HexColor")?;
                    let mut args961 = Vec::new();
                    let mut kw962 = Vec::new();
                    args961.push(Val::Str("#E7E9EE".into()));
                    fun963.call(args961, kw962)?
                });
                fun960.call(args958, kw959)?
            };
            let assigned964 = {
                let fun967 = e.get("c")?.attr("beginPath")?;
                let mut args965 = Vec::new();
                let mut kw966 = Vec::new();
                fun967.call(args965, kw966)?
            };
            e.set("path", assigned964.clone())?;
            for item968 in {
                let fun981 = e.get("enumerate")?;
                let mut args979 = Vec::new();
                let mut kw980 = Vec::new();
                args979.push(e.get("outline")?);
                fun981.call(args979, kw980)?
            }
            .iter()?
            {
                let unpack982 = unpack(item968, 2)?;
                e.set("i", unpack982[0].clone())?;
                let unpack983 = unpack(unpack982[1].clone(), 2)?;
                e.set("dx", unpack983[0].clone())?;
                e.set("dy", unpack983[1].clone())?;
                let assigned969 = {
                    let fun972 = e.get("at")?;
                    let mut args970 = Vec::new();
                    let mut kw971 = Vec::new();
                    args970.push(unary("neg", e.get("dy")?)?);
                    args970.push(e.get("dx")?);
                    fun972.call(args970, kw971)?
                };
                let unpack973 = unpack(assigned969.clone(), 2)?;
                e.set("px", unpack973[0].clone())?;
                e.set("py", unpack973[1].clone())?;
                {
                    let fun976 = if {
                        let v977 = e.get("i")?;
                        let v978 = Val::Int(0i64);
                        Val::Bool(compare("eq", v977.clone(), v978.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        e.get("path")?.attr("moveTo")?
                    } else {
                        e.get("path")?.attr("lineTo")?
                    };
                    let mut args974 = Vec::new();
                    let mut kw975 = Vec::new();
                    args974.push(e.get("px")?);
                    args974.push(binary("sub", e.get("H")?, e.get("py")?)?);
                    fun976.call(args974, kw975)?
                };
            }
            {
                let fun986 = e.get("path")?.attr("close")?;
                let mut args984 = Vec::new();
                let mut kw985 = Vec::new();
                fun986.call(args984, kw985)?
            };
            {
                let fun989 = e.get("c")?.attr("drawPath")?;
                let mut args987 = Vec::new();
                let mut kw988 = Vec::new();
                args987.push(e.get("path")?);
                kw988.push(("stroke".into(), Val::Int(1i64)));
                kw988.push(("fill".into(), Val::Int(1i64)));
                fun989.call(args987, kw988)?
            };
            // disc
            e.set("disc", {
                let params = vec![
                    ("point".into(), None, false),
                    ("diameter".into(), None, false),
                    ("fill".into(), None, false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned990 = {
                        let fun993 = e.get("at")?;
                        let mut args991 = Vec::new();
                        let mut kw992 = Vec::new();
                        args991.extend(e.get("point")?.iter()?);
                        fun993.call(args991, kw992)?
                    };
                    let unpack994 = unpack(assigned990.clone(), 2)?;
                    e.set("px", unpack994[0].clone())?;
                    e.set("py", unpack994[1].clone())?;
                    {
                        let fun997 = e.get("c")?.attr("setFillColor")?;
                        let mut args995 = Vec::new();
                        let mut kw996 = Vec::new();
                        args995.push({
                            let fun1000 = e.get("HexColor")?;
                            let mut args998 = Vec::new();
                            let mut kw999 = Vec::new();
                            args998.push(e.get("fill")?);
                            fun1000.call(args998, kw999)?
                        });
                        fun997.call(args995, kw996)?
                    };
                    {
                        let fun1003 = e.get("c")?.attr("setStrokeColor")?;
                        let mut args1001 = Vec::new();
                        let mut kw1002 = Vec::new();
                        args1001.push({
                            let fun1006 = e.get("HexColor")?;
                            let mut args1004 = Vec::new();
                            let mut kw1005 = Vec::new();
                            args1004.push(e.get("INK")?);
                            fun1006.call(args1004, kw1005)?
                        });
                        fun1003.call(args1001, kw1002)?
                    };
                    {
                        let fun1009 = e.get("c")?.attr("circle")?;
                        let mut args1007 = Vec::new();
                        let mut kw1008 = Vec::new();
                        args1007.push(e.get("px")?);
                        args1007.push(binary("sub", e.get("H")?, e.get("py")?)?);
                        args1007.push(binary(
                            "truediv",
                            binary("mul", e.get("diameter")?, e.get("scale")?)?,
                            Val::Int(2i64),
                        )?);
                        kw1008.push(("stroke".into(), Val::Int(1i64)));
                        kw1008.push(("fill".into(), Val::Int(1i64)));
                        fun1009.call(args1007, kw1008)?
                    };
                    Ok(Val::None)
                })
            })?;
            let assigned1010 = {
                let e = e.child();
                let out1011 = Val::list(vec![]);
                for item1012 in {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Int(1i64))?);
                    s.push(Val::Int(1i64));
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("sign", item1012)?;
                    out1011.attr("append")?.call(
                        vec![{
                            let mut s = Vec::new();
                            s.push(binary(
                                "add",
                                e.get("coords")?.get(Val::Str("LOWER_BUNDLE_X".into()))?,
                                binary(
                                    "mul",
                                    e.get("sign")?,
                                    e.get("coords")?.get(Val::Str("LOWER_FLAVOR_X".into()))?,
                                )?,
                            )?);
                            s.push(e.get("coords")?.get(Val::Str("LOWER_Y".into()))?);
                            Val::tuple(s)
                        }],
                        vec![],
                    )?;
                }
                out1011
            };
            e.set("flavors", assigned1010.clone())?;
            let assigned1013 = {
                let mut s = Vec::new();
                s.push(e.get("coords")?.get(Val::Str("LOWER_BUNDLE_X".into()))?);
                s.push(e.get("coords")?.get(Val::Str("LOWER_DRAIN_Y".into()))?);
                Val::tuple(s)
            };
            e.set("drain", assigned1013.clone())?;
            let assigned1014 = {
                let mut s = Vec::new();
                s.push(e.get("coords")?.get(Val::Str("LOWER_BUNDLE_X".into()))?);
                s.push(e.get("coords")?.get(Val::Str("LOWER_RIBBON_Y".into()))?);
                Val::tuple(s)
            };
            e.set("ribbon", assigned1014.clone())?;
            {
                let fun1017 = e.get("disc")?;
                let mut args1015 = Vec::new();
                let mut kw1016 = Vec::new();
                args1015.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                });
                args1015.push(e.get("shank")?);
                args1015.push(Val::Str("#202337".into()));
                fun1017.call(args1015, kw1016)?
            };
            for item1018 in e.get("flavors")?.iter()? {
                e.set("point", item1018)?;
                {
                    let fun1021 = e.get("disc")?;
                    let mut args1019 = Vec::new();
                    let mut kw1020 = Vec::new();
                    args1019.push(e.get("point")?);
                    args1019.push(e.get("coords")?.get(Val::Str("FLAVOR_OD".into()))?);
                    args1019.push(Val::Str("#202337".into()));
                    fun1021.call(args1019, kw1020)?
                };
            }
            {
                let fun1024 = e.get("disc")?;
                let mut args1022 = Vec::new();
                let mut kw1023 = Vec::new();
                args1022.push(e.get("drain")?);
                args1022.push(e.get("coords")?.get(Val::Str("DRAIN_OD".into()))?);
                args1022.push(Val::Str("#FFFFFF".into()));
                fun1024.call(args1022, kw1023)?
            };
            let assigned1025 = {
                let fun1028 = e.get("at")?;
                let mut args1026 = Vec::new();
                let mut kw1027 = Vec::new();
                args1026.extend(e.get("ribbon")?.iter()?);
                fun1028.call(args1026, kw1027)?
            };
            let unpack1029 = unpack(assigned1025.clone(), 2)?;
            e.set("px", unpack1029[0].clone())?;
            e.set("py", unpack1029[1].clone())?;
            let assigned1030 = binary(
                "mul",
                e.get("cable")?.get(Val::Str("RIBBON_WIDTH".into()))?,
                e.get("scale")?,
            )?;
            e.set("cable_w", assigned1030.clone())?;
            let assigned1031 = binary(
                "mul",
                e.get("cable")?.get(Val::Str("RIBBON_DEPTH".into()))?,
                e.get("scale")?,
            )?;
            e.set("cable_h", assigned1031.clone())?;
            {
                let fun1034 = e.get("rect")?;
                let mut args1032 = Vec::new();
                let mut kw1033 = Vec::new();
                args1032.push(binary(
                    "sub",
                    e.get("px")?,
                    binary("truediv", e.get("cable_w")?, Val::Int(2i64))?,
                )?);
                args1032.push(binary(
                    "sub",
                    e.get("py")?,
                    binary("truediv", e.get("cable_h")?, Val::Int(2i64))?,
                )?);
                args1032.push(e.get("cable_w")?);
                args1032.push(e.get("cable_h")?);
                args1032.push(Val::Str("#202337".into()));
                fun1034.call(args1032, kw1033)?
            };
            let assigned1035 = {
                let e = e.child();
                let out1036 = Val::list(vec![]);
                for item1037 in e.get("flavors")?.iter()? {
                    let unpack1038 = unpack(item1037, 2)?;
                    e.set("x", unpack1038[0].clone())?;
                    e.set("y", unpack1038[1].clone())?;
                    for item1039 in {
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Int(1i64))?);
                        s.push(Val::Int(1i64));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("sx", item1039)?;
                        for item1040 in {
                            let mut s = Vec::new();
                            s.push(unary("neg", Val::Int(1i64))?);
                            s.push(Val::Int(1i64));
                            Val::tuple(s)
                        }
                        .iter()?
                        {
                            e.set("sy", item1040)?;
                            out1036.attr("append")?.call(
                                vec![{
                                    let mut s = Vec::new();
                                    s.push(binary(
                                        "add",
                                        e.get("x")?,
                                        binary(
                                            "truediv",
                                            binary(
                                                "mul",
                                                e.get("sx")?,
                                                e.get("coords")?
                                                    .get(Val::Str("FLAVOR_OD".into()))?,
                                            )?,
                                            Val::Int(2i64),
                                        )?,
                                    )?);
                                    s.push(binary(
                                        "add",
                                        e.get("y")?,
                                        binary(
                                            "truediv",
                                            binary(
                                                "mul",
                                                e.get("sy")?,
                                                e.get("coords")?
                                                    .get(Val::Str("FLAVOR_OD".into()))?,
                                            )?,
                                            Val::Int(2i64),
                                        )?,
                                    )?);
                                    Val::tuple(s)
                                }],
                                vec![],
                            )?;
                        }
                    }
                }
                out1036
            };
            e.set("ends", assigned1035.clone())?;
            e.set(
                "ends",
                binary("add", e.get("ends")?, {
                    let e = e.child();
                    let out1041 = Val::list(vec![]);
                    for item1042 in {
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Int(1i64))?);
                        s.push(Val::Int(1i64));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("sx", item1042)?;
                        for item1043 in {
                            let mut s = Vec::new();
                            s.push(unary("neg", Val::Int(1i64))?);
                            s.push(Val::Int(1i64));
                            Val::tuple(s)
                        }
                        .iter()?
                        {
                            e.set("sy", item1043)?;
                            out1041.attr("append")?.call(
                                vec![{
                                    let mut s = Vec::new();
                                    s.push(binary(
                                        "add",
                                        e.get("drain")?.get(Val::Int(0i64))?,
                                        binary(
                                            "truediv",
                                            binary(
                                                "mul",
                                                e.get("sx")?,
                                                e.get("coords")?
                                                    .get(Val::Str("DRAIN_OD".into()))?,
                                            )?,
                                            Val::Int(2i64),
                                        )?,
                                    )?);
                                    s.push(binary(
                                        "add",
                                        e.get("drain")?.get(Val::Int(1i64))?,
                                        binary(
                                            "truediv",
                                            binary(
                                                "mul",
                                                e.get("sy")?,
                                                e.get("coords")?
                                                    .get(Val::Str("DRAIN_OD".into()))?,
                                            )?,
                                            Val::Int(2i64),
                                        )?,
                                    )?);
                                    Val::tuple(s)
                                }],
                                vec![],
                            )?;
                        }
                    }
                    out1041
                })?,
            )?;
            e.set(
                "ends",
                binary("add", e.get("ends")?, {
                    let e = e.child();
                    let out1044 = Val::list(vec![]);
                    for item1045 in {
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Int(1i64))?);
                        s.push(Val::Int(1i64));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("sx", item1045)?;
                        for item1046 in {
                            let mut s = Vec::new();
                            s.push(unary("neg", Val::Int(1i64))?);
                            s.push(Val::Int(1i64));
                            Val::tuple(s)
                        }
                        .iter()?
                        {
                            e.set("sy", item1046)?;
                            out1044.attr("append")?.call(
                                vec![{
                                    let mut s = Vec::new();
                                    s.push(binary(
                                        "add",
                                        e.get("ribbon")?.get(Val::Int(0i64))?,
                                        binary(
                                            "truediv",
                                            binary(
                                                "mul",
                                                e.get("sx")?,
                                                e.get("cable")?
                                                    .get(Val::Str("RIBBON_WIDTH".into()))?,
                                            )?,
                                            Val::Int(2i64),
                                        )?,
                                    )?);
                                    s.push(binary(
                                        "add",
                                        e.get("ribbon")?.get(Val::Int(1i64))?,
                                        binary(
                                            "truediv",
                                            binary(
                                                "mul",
                                                e.get("sy")?,
                                                e.get("cable")?
                                                    .get(Val::Str("RIBBON_DEPTH".into()))?,
                                            )?,
                                            Val::Int(2i64),
                                        )?,
                                    )?);
                                    Val::tuple(s)
                                }],
                                vec![],
                            )?;
                        }
                    }
                    out1044
                })?,
            )?;
            let assigned1047 = {
                let e = e.child();
                let out1048 = Val::list(vec![]);
                for item1049 in e.get("ends")?.iter()? {
                    e.set("point", item1049)?;
                    out1048.attr("append")?.call(
                        vec![{
                            let fun1052 = e.get("at")?;
                            let mut args1050 = Vec::new();
                            let mut kw1051 = Vec::new();
                            args1050.extend(e.get("point")?.iter()?);
                            fun1052.call(args1050, kw1051)?
                        }],
                        vec![],
                    )?;
                }
                out1048
            };
            e.set("points", assigned1047.clone())?;
            let assigned1053 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    {
                        let fun1056 = e.get("min")?;
                        let mut args1054 = Vec::new();
                        let mut kw1055 = Vec::new();
                        args1054.push({
                            let e = e.child();
                            let out1057 = Val::list(vec![]);
                            for item1058 in e.get("points")?.iter()? {
                                e.set("p", item1058)?;
                                out1057
                                    .attr("append")?
                                    .call(vec![e.get("p")?.get(Val::Int(0i64))?], vec![])?;
                            }
                            out1057
                        });
                        fun1056.call(args1054, kw1055)?
                    },
                    Val::Int(3i64),
                )?);
                s.push(binary(
                    "sub",
                    {
                        let fun1061 = e.get("min")?;
                        let mut args1059 = Vec::new();
                        let mut kw1060 = Vec::new();
                        args1059.push({
                            let e = e.child();
                            let out1062 = Val::list(vec![]);
                            for item1063 in e.get("points")?.iter()? {
                                e.set("p", item1063)?;
                                out1062
                                    .attr("append")?
                                    .call(vec![e.get("p")?.get(Val::Int(1i64))?], vec![])?;
                            }
                            out1062
                        });
                        fun1061.call(args1059, kw1060)?
                    },
                    Val::Int(3i64),
                )?);
                Val::tuple(s)
            };
            let unpack1064 = unpack(assigned1053.clone(), 2)?;
            e.set("left", unpack1064[0].clone())?;
            e.set("top", unpack1064[1].clone())?;
            let assigned1065 = {
                let mut s = Vec::new();
                s.push(binary(
                    "add",
                    {
                        let fun1068 = e.get("max")?;
                        let mut args1066 = Vec::new();
                        let mut kw1067 = Vec::new();
                        args1066.push({
                            let e = e.child();
                            let out1069 = Val::list(vec![]);
                            for item1070 in e.get("points")?.iter()? {
                                e.set("p", item1070)?;
                                out1069
                                    .attr("append")?
                                    .call(vec![e.get("p")?.get(Val::Int(0i64))?], vec![])?;
                            }
                            out1069
                        });
                        fun1068.call(args1066, kw1067)?
                    },
                    Val::Int(3i64),
                )?);
                s.push(binary(
                    "add",
                    {
                        let fun1073 = e.get("max")?;
                        let mut args1071 = Vec::new();
                        let mut kw1072 = Vec::new();
                        args1071.push({
                            let e = e.child();
                            let out1074 = Val::list(vec![]);
                            for item1075 in e.get("points")?.iter()? {
                                e.set("p", item1075)?;
                                out1074
                                    .attr("append")?
                                    .call(vec![e.get("p")?.get(Val::Int(1i64))?], vec![])?;
                            }
                            out1074
                        });
                        fun1073.call(args1071, kw1072)?
                    },
                    Val::Int(3i64),
                )?);
                Val::tuple(s)
            };
            let unpack1076 = unpack(assigned1065.clone(), 2)?;
            e.set("right", unpack1076[0].clone())?;
            e.set("bottom", unpack1076[1].clone())?;
            {
                let fun1079 = e.get("c")?.attr("setStrokeColor")?;
                let mut args1077 = Vec::new();
                let mut kw1078 = Vec::new();
                args1077.push({
                    let fun1082 = e.get("HexColor")?;
                    let mut args1080 = Vec::new();
                    let mut kw1081 = Vec::new();
                    args1080.push(e.get("BLUE")?);
                    fun1082.call(args1080, kw1081)?
                });
                fun1079.call(args1077, kw1078)?
            };
            {
                let fun1085 = e.get("c")?.attr("setLineWidth")?;
                let mut args1083 = Vec::new();
                let mut kw1084 = Vec::new();
                args1083.push(Val::Float(1.1f64));
                fun1085.call(args1083, kw1084)?
            };
            {
                let fun1088 = e.get("c")?.attr("roundRect")?;
                let mut args1086 = Vec::new();
                let mut kw1087 = Vec::new();
                args1086.push(e.get("left")?);
                args1086.push(binary("sub", e.get("H")?, e.get("bottom")?)?);
                args1086.push(binary("sub", e.get("right")?, e.get("left")?)?);
                args1086.push(binary("sub", e.get("bottom")?, e.get("top")?)?);
                args1086.push(Val::Int(4i64));
                kw1087.push(("fill".into(), Val::Int(0i64)));
                kw1087.push(("stroke".into(), Val::Int(1i64)));
                fun1088.call(args1086, kw1087)?
            };
            {
                let fun1091 = e.get("c")?.attr("restoreState")?;
                let mut args1089 = Vec::new();
                let mut kw1090 = Vec::new();
                fun1091.call(args1089, kw1090)?
            };
            // pointer
            e.set("pointer", {
                let params = vec![("start".into(), None, false), ("point".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    for item1092 in {
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Str("#FFFFFF".into()));
                            s.push(Val::Int(3i64));
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("INK")?);
                            s.push(Val::Float(0.8f64));
                            Val::tuple(s)
                        });
                        Val::list(s)
                    }
                    .iter()?
                    {
                        let unpack1096 = unpack(item1092, 2)?;
                        e.set("color", unpack1096[0].clone())?;
                        e.set("width", unpack1096[1].clone())?;
                        {
                            let fun1095 = e.get("line")?;
                            let mut args1093 = Vec::new();
                            let mut kw1094 = Vec::new();
                            args1093.extend(e.get("start")?.iter()?);
                            args1093.extend(e.get("point")?.iter()?);
                            args1093.push(e.get("color")?);
                            args1093.push(e.get("width")?);
                            fun1095.call(args1093, kw1094)?
                        };
                    }
                    {
                        let fun1099 = e.get("c")?.attr("setFillColor")?;
                        let mut args1097 = Vec::new();
                        let mut kw1098 = Vec::new();
                        args1097.push({
                            let fun1102 = e.get("HexColor")?;
                            let mut args1100 = Vec::new();
                            let mut kw1101 = Vec::new();
                            args1100.push(e.get("CORAL")?);
                            fun1102.call(args1100, kw1101)?
                        });
                        fun1099.call(args1097, kw1098)?
                    };
                    {
                        let fun1105 = e.get("c")?.attr("setStrokeColor")?;
                        let mut args1103 = Vec::new();
                        let mut kw1104 = Vec::new();
                        args1103.push(e.get("white")?);
                        fun1105.call(args1103, kw1104)?
                    };
                    {
                        let fun1108 = e.get("c")?.attr("circle")?;
                        let mut args1106 = Vec::new();
                        let mut kw1107 = Vec::new();
                        args1106.push(e.get("point")?.get(Val::Int(0i64))?);
                        args1106.push(binary(
                            "sub",
                            e.get("H")?,
                            e.get("point")?.get(Val::Int(1i64))?,
                        )?);
                        args1106.push(Val::Float(2.2f64));
                        kw1107.push(("fill".into(), Val::Int(1i64)));
                        kw1107.push(("stroke".into(), Val::Int(1i64)));
                        fun1108.call(args1106, kw1107)?
                    };
                    Ok(Val::None)
                })
            })?;
            {
                let fun1111 = e.get("label")?;
                let mut args1109 = Vec::new();
                let mut kw1110 = Vec::new();
                args1109.push(Val::Str("BACK / NARROW SLOT".into()));
                args1109.push(Val::Int(250i64));
                args1109.push(Val::Int(302i64));
                fun1111.call(args1109, kw1110)?
            };
            {
                let fun1114 = e.get("pointer")?;
                let mut args1112 = Vec::new();
                let mut kw1113 = Vec::new();
                args1112.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(244i64));
                    s.push(Val::Int(310i64));
                    Val::tuple(s)
                });
                args1112.push({
                    let mut s = Vec::new();
                    s.push(e.get("right")?);
                    s.push(binary(
                        "truediv",
                        binary("add", e.get("top")?, e.get("bottom")?)?,
                        Val::Int(2i64),
                    )?);
                    Val::tuple(s)
                });
                fun1114.call(args1112, kw1113)?
            };
            for item1115 in {
                let mut s = Vec::new();
                s.push(Val::Int(261i64));
                s.push(Val::Int(272i64));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("x", item1115)?;
                {
                    let fun1118 = e.get("c")?.attr("setFillColor")?;
                    let mut args1116 = Vec::new();
                    let mut kw1117 = Vec::new();
                    args1116.push({
                        let fun1121 = e.get("HexColor")?;
                        let mut args1119 = Vec::new();
                        let mut kw1120 = Vec::new();
                        args1119.push(e.get("INK")?);
                        fun1121.call(args1119, kw1120)?
                    });
                    fun1118.call(args1116, kw1117)?
                };
                {
                    let fun1124 = e.get("c")?.attr("circle")?;
                    let mut args1122 = Vec::new();
                    let mut kw1123 = Vec::new();
                    args1122.push(e.get("x")?);
                    args1122.push(binary("sub", e.get("H")?, Val::Int(328i64))?);
                    args1122.push(Val::Float(4.5f64));
                    kw1123.push(("fill".into(), Val::Int(1i64)));
                    kw1123.push(("stroke".into(), Val::Int(0i64)));
                    fun1124.call(args1122, kw1123)?
                };
            }
            {
                let fun1127 = e.get("text")?;
                let mut args1125 = Vec::new();
                let mut kw1126 = Vec::new();
                args1125.push(Val::Str("Both black flavor tubes".into()));
                args1125.push(Val::Int(288i64));
                args1125.push(Val::Int(323i64));
                args1125.push(Val::Int(11i64));
                args1125.push(Val::Str("Semibold".into()));
                fun1127.call(args1125, kw1126)?
            };
            {
                let fun1130 = e.get("c")?.attr("setFillColor")?;
                let mut args1128 = Vec::new();
                let mut kw1129 = Vec::new();
                args1128.push(e.get("white")?);
                fun1130.call(args1128, kw1129)?
            };
            {
                let fun1133 = e.get("c")?.attr("setStrokeColor")?;
                let mut args1131 = Vec::new();
                let mut kw1132 = Vec::new();
                args1131.push({
                    let fun1136 = e.get("HexColor")?;
                    let mut args1134 = Vec::new();
                    let mut kw1135 = Vec::new();
                    args1134.push(e.get("INK")?);
                    fun1136.call(args1134, kw1135)?
                });
                fun1133.call(args1131, kw1132)?
            };
            {
                let fun1139 = e.get("c")?.attr("setLineWidth")?;
                let mut args1137 = Vec::new();
                let mut kw1138 = Vec::new();
                args1137.push(Val::Float(0.8f64));
                fun1139.call(args1137, kw1138)?
            };
            {
                let fun1142 = e.get("c")?.attr("circle")?;
                let mut args1140 = Vec::new();
                let mut kw1141 = Vec::new();
                args1140.push(Val::Float(266.5f64));
                args1140.push(binary("sub", e.get("H")?, Val::Int(350i64))?);
                args1140.push(Val::Float(4.5f64));
                kw1141.push(("fill".into(), Val::Int(1i64)));
                kw1141.push(("stroke".into(), Val::Int(1i64)));
                fun1142.call(args1140, kw1141)?
            };
            {
                let fun1145 = e.get("text")?;
                let mut args1143 = Vec::new();
                let mut kw1144 = Vec::new();
                args1143.push(Val::Str("White DRAIN tube".into()));
                args1143.push(Val::Int(288i64));
                args1143.push(Val::Int(345i64));
                args1143.push(Val::Int(11i64));
                args1143.push(Val::Str("Semibold".into()));
                fun1145.call(args1143, kw1144)?
            };
            {
                let fun1148 = e.get("rect")?;
                let mut args1146 = Vec::new();
                let mut kw1147 = Vec::new();
                args1146.push(Val::Int(257i64));
                args1146.push(Val::Int(370i64));
                args1146.push(Val::Int(19i64));
                args1146.push(Val::Float(4.5f64));
                args1146.push(e.get("INK")?);
                fun1148.call(args1146, kw1147)?
            };
            {
                let fun1151 = e.get("text")?;
                let mut args1149 = Vec::new();
                let mut kw1150 = Vec::new();
                args1149.push(Val::Str("Flat display ribbon".into()));
                args1149.push(Val::Int(288i64));
                args1149.push(Val::Int(367i64));
                args1149.push(Val::Int(11i64));
                args1149.push(Val::Str("Semibold".into()));
                fun1151.call(args1149, kw1150)?
            };
            {
                let fun1154 = e.get("label")?;
                let mut args1152 = Vec::new();
                let mut kw1153 = Vec::new();
                args1152.push(Val::Str("FRONT / WIDE SLOT".into()));
                args1152.push(Val::Int(250i64));
                args1152.push(Val::Int(397i64));
                fun1154.call(args1152, kw1153)?
            };
            {
                let fun1157 = e.get("pointer")?;
                let mut args1155 = Vec::new();
                let mut kw1156 = Vec::new();
                args1155.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(244i64));
                    s.push(Val::Int(405i64));
                    Val::tuple(s)
                });
                args1155.push({
                    let fun1160 = e.get("at")?;
                    let mut args1158 = Vec::new();
                    let mut kw1159 = Vec::new();
                    args1158.push(binary("truediv", e.get("shank")?, Val::Int(3i64))?);
                    args1158.push(binary(
                        "truediv",
                        unary("neg", e.get("shank")?)?,
                        Val::Int(3i64),
                    )?);
                    fun1160.call(args1158, kw1159)?
                });
                fun1157.call(args1155, kw1156)?
            };
            {
                let fun1163 = e.get("text")?;
                let mut args1161 = Vec::new();
                let mut kw1162 = Vec::new();
                args1161.push(Val::Str("Shank; blue SODA connects below.".into()));
                args1161.push(Val::Int(250i64));
                args1161.push(Val::Int(417i64));
                args1161.push(Val::Int(10i64));
                fun1163.call(args1161, kw1162)?
            };
            {
                let fun1166 = e.get("mount_slot_checks")?.attr("append")?;
                let mut args1164 = Vec::new();
                let mut kw1165 = Vec::new();
                args1164.push({
                    let fun1169 = e.get("dict")?;
                    let mut args1167 = Vec::new();
                    let mut kw1168 = Vec::new();
                    kw1168.push(("reading_pdf_page".into(), e.get("page_no")?));
                    kw1168.push((
                        "numbered_interior".into(),
                        binary("sub", e.get("page_no")?, Val::Int(1i64))?,
                    ));
                    kw1168.push(("source_sha256".into(), {
                        let e = e.child();
                        let out1170 = Val::dict(vec![]);
                        for item1171 in e.get("sources")?.iter()? {
                            e.set("path", item1171)?;
                            out1170.set(
                                {
                                    let fun1174 = e.get("str")?;
                                    let mut args1172 = Vec::new();
                                    let mut kw1173 = Vec::new();
                                    args1172.push({
                                        let fun1177 = e.get("path")?.attr("relative_to")?;
                                        let mut args1175 = Vec::new();
                                        let mut kw1176 = Vec::new();
                                        args1175.push(e.get("ROOT")?);
                                        fun1177.call(args1175, kw1176)?
                                    });
                                    fun1174.call(args1172, kw1173)?
                                },
                                {
                                    let fun1180 = {
                                        let fun1183 = e.get("hashlib")?.attr("sha256")?;
                                        let mut args1181 = Vec::new();
                                        let mut kw1182 = Vec::new();
                                        args1181.push({
                                            let fun1186 = e.get("path")?.attr("read_bytes")?;
                                            let mut args1184 = Vec::new();
                                            let mut kw1185 = Vec::new();
                                            fun1186.call(args1184, kw1185)?
                                        });
                                        fun1183.call(args1181, kw1182)?
                                    }
                                    .attr("hexdigest")?;
                                    let mut args1178 = Vec::new();
                                    let mut kw1179 = Vec::new();
                                    fun1180.call(args1178, kw1179)?
                                },
                            )?;
                        }
                        out1170
                    }));
                    kw1168.push((
                        "profile".into(),
                        Val::Str("Centered production under-counter plate".into()),
                    ));
                    kw1168.push((
                        "view".into(),
                        Val::Str("Looking up; world +Y at page top, world +X at page left".into()),
                    ));
                    kw1168.push(("rear_slot".into(), {
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("flavor_centers_mm".into()), e.get("flavors")?)?;
                        d.set(
                            Val::Str("flavor_od_mm".into()),
                            e.get("coords")?.get(Val::Str("FLAVOR_OD".into()))?,
                        )?;
                        d.set(Val::Str("drain_center_mm".into()), e.get("drain")?)?;
                        d.set(
                            Val::Str("drain_od_mm".into()),
                            e.get("coords")?.get(Val::Str("DRAIN_OD".into()))?,
                        )?;
                        d.set(Val::Str("ribbon_center_mm".into()), e.get("ribbon")?)?;
                        d.set(Val::Str("ribbon_envelope_mm".into()), {
                            let mut s = Vec::new();
                            s.push(e.get("cable")?.get(Val::Str("RIBBON_WIDTH".into()))?);
                            s.push(e.get("cable")?.get(Val::Str("RIBBON_DEPTH".into()))?);
                            Val::list(s)
                        })?;
                        d
                    }));
                    kw1168.push(("front_slot".into(), {
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("shank_center_mm".into()), {
                            let mut s = Vec::new();
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(0i64));
                            Val::list(s)
                        })?;
                        d.set(Val::Str("shank_od_mm".into()), e.get("shank")?)?;
                        d.set(
                            Val::Str("blue_soda_attachment".into()),
                            Val::Str("Below the plate at the shank bottom".into()),
                        )?;
                        d
                    }));
                    kw1168.push(("omitted_for_visibility".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("retained washer".into()));
                        s.push(Val::Str("retained nut".into()));
                        Val::list(s)
                    }));
                    fun1169.call(args1167, kw1168)?
                });
                fun1166.call(args1164, kw1165)?
            };
            Ok(Val::None)
        })
    })?;
    // front_cover
    e.set("front_cover", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1187 = Val::Int(1i64);
            e.set_global("page_no", assigned1187.clone())?;
            {
                let fun1190 = e.get("begin_page")?;
                let mut args1188 = Vec::new();
                let mut kw1189 = Vec::new();
                fun1190.call(args1188, kw1189)?
            };
            {
                let fun1193 = e.get("ground")?;
                let mut args1191 = Vec::new();
                let mut kw1192 = Vec::new();
                args1191.push(e.get("BLUE")?);
                fun1193.call(args1191, kw1192)?
            };
            {
                let fun1196 = e.get("label")?;
                let mut args1194 = Vec::new();
                let mut kw1195 = Vec::new();
                args1194.push(Val::Str("HOME SODA MACHINE".into()));
                args1194.push(Val::Int(52i64));
                args1194.push(Val::Int(51i64));
                args1194.push(Val::Str("#FFFFFF".into()));
                args1194.push(Val::Int(11i64));
                fun1196.call(args1194, kw1195)?
            };
            {
                let fun1199 = e.get("text")?;
                let mut args1197 = Vec::new();
                let mut kw1198 = Vec::new();
                args1197.push(Val::Str("Install".into()));
                args1197.push(Val::Int(52i64));
                args1197.push(Val::Int(145i64));
                args1197.push(Val::Int(60i64));
                args1197.push(Val::Str("Bold".into()));
                args1197.push(Val::Str("#FFFFFF".into()));
                fun1199.call(args1197, kw1198)?
            };
            {
                let fun1202 = e.get("text")?;
                let mut args1200 = Vec::new();
                let mut kw1201 = Vec::new();
                args1200.push(Val::Str("guide".into()));
                args1200.push(Val::Int(52i64));
                args1200.push(Val::Int(211i64));
                args1200.push(Val::Int(60i64));
                args1200.push(Val::Str("Bold".into()));
                args1200.push(Val::Str("#FFFFFF".into()));
                fun1202.call(args1200, kw1201)?
            };
            {
                let fun1205 = e.get("c")?.attr("drawImage")?;
                let mut args1203 = Vec::new();
                let mut kw1204 = Vec::new();
                args1203.push({
                    let fun1208 = e.get("image_reader")?;
                    let mut args1206 = Vec::new();
                    let mut kw1207 = Vec::new();
                    args1206.push(binary(
                        "truediv",
                        e.get("ART")?,
                        Val::Str("brand/mark-1024.png".into()),
                    )?);
                    args1206.push(e.get("BLUE")?);
                    fun1208.call(args1206, kw1207)?
                });
                args1203.push(Val::Int(373i64));
                args1203.push(binary("sub", e.get("H")?, Val::Int(295i64))?);
                kw1204.push(("width".into(), Val::Int(222i64)));
                kw1204.push(("height".into(), Val::Int(222i64)));
                fun1205.call(args1203, kw1204)?
            };
            {
                let fun1211 = e.get("rect")?;
                let mut args1209 = Vec::new();
                let mut kw1210 = Vec::new();
                args1209.push(Val::Int(52i64));
                args1209.push(Val::Int(311i64));
                args1209.push(Val::Int(64i64));
                args1209.push(Val::Int(5i64));
                args1209.push(e.get("ORANGE")?);
                fun1211.call(args1209, kw1210)?
            };
            {
                let fun1214 = e.get("para")?;
                let mut args1212 = Vec::new();
                let mut kw1213 = Vec::new();
                args1212.push(Val::Str("From the box<br/>to your first glass.".into()));
                args1212.push(Val::Int(52i64));
                args1212.push(Val::Int(345i64));
                args1212.push(Val::Int(328i64));
                args1212.push(Val::Int(23i64));
                args1212.push(Val::Int(30i64));
                args1212.push(Val::Str("#FFFFFF".into()));
                kw1213.push(("limit".into(), Val::Int(60i64)));
                fun1214.call(args1212, kw1213)?
            };
            {
                let fun1217 = e.get("text")?;
                let mut args1215 = Vec::new();
                let mut kw1216 = Vec::new();
                args1215.push(Val::Str("SEVEN STEPS. EVERY CONNECTION.".into()));
                args1215.push(Val::Int(52i64));
                args1215.push(Val::Int(445i64));
                args1215.push(Val::Int(9i64));
                args1215.push(Val::Str("Semibold".into()));
                args1215.push(e.get("ICE")?);
                fun1217.call(args1215, kw1216)?
            };
            {
                let fun1220 = e.get("text")?;
                let mut args1218 = Vec::new();
                let mut kw1219 = Vec::new();
                args1218.push(Val::Str("homesodamachine.com".into()));
                args1218.push(Val::Int(425i64));
                args1218.push(Val::Int(445i64));
                args1218.push(Val::Int(10i64));
                args1218.push(Val::Str("Regular".into()));
                args1218.push(Val::Str("#FFFFFF".into()));
                fun1220.call(args1218, kw1219)?
            };
            {
                let fun1223 = e.get("c")?.attr("bookmarkPage")?;
                let mut args1221 = Vec::new();
                let mut kw1222 = Vec::new();
                args1221.push(Val::Str("page-1".into()));
                fun1223.call(args1221, kw1222)?
            };
            {
                let fun1226 = e.get("c")?.attr("addOutlineEntry")?;
                let mut args1224 = Vec::new();
                let mut kw1225 = Vec::new();
                args1224.push(Val::Str("Cover".into()));
                args1224.push(Val::Str("page-1".into()));
                args1224.push(Val::Int(0i64));
                args1224.push(Val::Bool(false));
                fun1226.call(args1224, kw1225)?
            };
            {
                let fun1229 = e.get("c")?.attr("showPage")?;
                let mut args1227 = Vec::new();
                let mut kw1228 = Vec::new();
                fun1229.call(args1227, kw1228)?
            };
            Ok(Val::None)
        })
    })?;
    // back_cover
    e.set("back_cover",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set_global("page_no",binary("add",e.get("page_no")?,Val::Int(1i64))?)?;
{let fun1232=e.get("begin_page")?;let mut args1230=Vec::new();let mut kw1231=Vec::new();fun1232.call(args1230,kw1231)?};
{let fun1235=e.get("ground")?;let mut args1233=Vec::new();let mut kw1234=Vec::new();args1233.push(e.get("BLUE")?);fun1235.call(args1233,kw1234)?};
{let fun1238=e.get("label")?;let mut args1236=Vec::new();let mut kw1237=Vec::new();args1236.push(Val::Str("HOME SODA MACHINE".into()));args1236.push(Val::Int(52i64));args1236.push(Val::Int(51i64));args1236.push(Val::Str("#FFFFFF".into()));args1236.push(Val::Int(11i64));fun1238.call(args1236,kw1237)?};
{let fun1241=e.get("c")?.attr("drawImage")?;let mut args1239=Vec::new();let mut kw1240=Vec::new();args1239.push({let fun1244=e.get("image_reader")?;let mut args1242=Vec::new();let mut kw1243=Vec::new();args1242.push(binary("truediv",e.get("ART")?,Val::Str("brand/mark-1024.png".into()))?);args1242.push(e.get("BLUE")?);fun1244.call(args1242,kw1243)?});args1239.push(Val::Int(44i64));args1239.push(binary("sub",e.get("H")?,Val::Int(280i64))?);kw1240.push(("width".into(),Val::Int(216i64)));kw1240.push(("height".into(),Val::Int(216i64)));fun1241.call(args1239,kw1240)?};
{let fun1247=e.get("text")?;let mut args1245=Vec::new();let mut kw1246=Vec::new();args1245.push(Val::Str("On tap.".into()));args1245.push(Val::Int(313i64));args1245.push(Val::Int(136i64));args1245.push(Val::Int(51i64));args1245.push(Val::Str("Bold".into()));args1245.push(Val::Str("#FFFFFF".into()));fun1247.call(args1245,kw1246)?};
{let fun1250=e.get("rect")?;let mut args1248=Vec::new();let mut kw1249=Vec::new();args1248.push(Val::Int(315i64));args1248.push(Val::Int(212i64));args1248.push(Val::Int(57i64));args1248.push(Val::Int(5i64));args1248.push(e.get("ORANGE")?);fun1250.call(args1248,kw1249)?};
{let fun1253=e.get("para")?;let mut args1251=Vec::new();let mut kw1252=Vec::new();args1251.push(Val::Str("Keep this guide<br/>with your install kit.".into()));args1251.push(Val::Int(315i64));args1251.push(Val::Int(251i64));args1251.push(Val::Int(277i64));args1251.push(Val::Int(23i64));args1251.push(Val::Int(30i64));args1251.push(Val::Str("#FFFFFF".into()));kw1252.push(("limit".into(),Val::Int(60i64)));fun1253.call(args1251,kw1252)?};
{let fun1256=e.get("para")?;let mut args1254=Vec::new();let mut kw1255=Vec::new();args1254.push(Val::Str("<b>Sealed cooling circuit</b><br/>R-600a (isobutane), flammable refrigerant.<br/>Under 1.5 oz (40 g). Do not open, puncture or heat.".into()));args1254.push(Val::Int(52i64));args1254.push(Val::Int(357i64));args1254.push(Val::Int(540i64));args1254.push(Val::Float(10.5f64));args1254.push(Val::Int(15i64));args1254.push(e.get("ICE")?);kw1255.push(("limit".into(),Val::Int(60i64)));fun1256.call(args1254,kw1255)?};
{let fun1259=e.get("text")?;let mut args1257=Vec::new();let mut kw1258=Vec::new();args1257.push(Val::Str("homesodamachine.com".into()));args1257.push(Val::Int(52i64));args1257.push(Val::Int(438i64));args1257.push(Val::Int(15i64));args1257.push(Val::Str("Semibold".into()));args1257.push(Val::Str("#FFFFFF".into()));fun1259.call(args1257,kw1258)?};
{let fun1262=e.get("text")?;let mut args1260=Vec::new();let mut kw1261=Vec::new();args1260.push(Val::Str("Guides: /drawings".into()));args1260.push(Val::Int(455i64));args1260.push(Val::Int(442i64));args1260.push(Val::Int(10i64));args1260.push(Val::Str("Regular".into()));args1260.push(e.get("ICE")?);fun1262.call(args1260,kw1261)?};
{let fun1265=e.get("c")?.attr("linkURL")?;let mut args1263=Vec::new();let mut kw1264=Vec::new();args1263.push(Val::Str("https://homesodamachine.com".into()));args1263.push({let mut s=Vec::new();s.push(Val::Int(52i64));s.push(binary("sub",e.get("H")?,Val::Int(459i64))?);s.push(Val::Int(301i64));s.push(binary("sub",e.get("H")?,Val::Int(435i64))?);Val::tuple(s)});kw1264.push(("relative".into(),Val::Int(1i64)));fun1265.call(args1263,kw1264)?};
{let fun1268=e.get("c")?.attr("linkURL")?;let mut args1266=Vec::new();let mut kw1267=Vec::new();args1266.push(Val::Str("https://homesodamachine.com/drawings".into()));args1266.push({let mut s=Vec::new();s.push(Val::Int(450i64));s.push(binary("sub",e.get("H")?,Val::Int(458i64))?);s.push(Val::Int(600i64));s.push(binary("sub",e.get("H")?,Val::Int(435i64))?);Val::tuple(s)});kw1267.push(("relative".into(),Val::Int(1i64)));fun1268.call(args1266,kw1267)?};
{let fun1271=e.get("c")?.attr("bookmarkPage")?;let mut args1269=Vec::new();let mut kw1270=Vec::new();args1269.push({let mut str1272=String::new();str1272.push_str("page-");str1272.push_str(&format(&e.get("page_no")?,&String::new())?);Val::Str(str1272)});fun1271.call(args1269,kw1270)?};
{let fun1275=e.get("c")?.attr("addOutlineEntry")?;let mut args1273=Vec::new();let mut kw1274=Vec::new();args1273.push(Val::Str("Back cover".into()));args1273.push({let mut str1276=String::new();str1276.push_str("page-");str1276.push_str(&format(&e.get("page_no")?,&String::new())?);Val::Str(str1276)});args1273.push(Val::Int(0i64));args1273.push(Val::Bool(false));fun1275.call(args1273,kw1274)?};
{let fun1279=e.get("c")?.attr("showPage")?;let mut args1277=Vec::new();let mut kw1278=Vec::new();fun1279.call(args1277,kw1278)?};
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun1282 = e.get("front_cover")?;
        let mut args1280 = Vec::new();
        let mut kw1281 = Vec::new();
        fun1282.call(args1280, kw1281)?
    };
    {
        let fun1285 = e.get("header")?;
        let mut args1283 = Vec::new();
        let mut kw1284 = Vec::new();
        args1283.push(Val::Str("Your first glass starts here".into()));
        kw1284.push((
            "sub".into(),
            Val::Str(
                "Keep this booklet beside you while you install. Follow the seven steps in order."
                    .into(),
            ),
        ));
        fun1285.call(args1283, kw1284)?
    };
    {
        let fun1288 = e.get("pic")?;
        let mut args1286 = Vec::new();
        let mut kw1287 = Vec::new();
        args1286.push(Val::Str("steps/pour-base.png".into()));
        args1286.push(e.get("M")?);
        args1286.push(Val::Int(145i64));
        args1286.push(Val::Int(260i64));
        args1286.push(Val::Int(271i64));
        kw1287.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(150i64));
            s.push(Val::Int(40i64));
            s.push(Val::Int(1475i64));
            s.push(Val::Int(1500i64));
            Val::tuple(s)
        }));
        fun1288.call(args1286, kw1287)?
    };
    {
        let fun1291 = e.get("text")?;
        let mut args1289 = Vec::new();
        let mut kw1290 = Vec::new();
        args1289.push(Val::Str("Make the connections.".into()));
        args1289.push(e.get("RIGHT")?);
        args1289.push(Val::Int(158i64));
        args1289.push(Val::Int(18i64));
        args1289.push(Val::Str("Bold".into()));
        args1289.push(e.get("NAVY")?);
        fun1291.call(args1289, kw1290)?
    };
    {
        let fun1294 = e.get("para")?;
        let mut args1292 = Vec::new();
        let mut kw1293 = Vec::new();
        args1292.push(Val::Str("Start with the faucet and cold-water supply. Match each tube to its color on the back of the machine.".into()));
        args1292.push(e.get("RIGHT")?);
        args1292.push(Val::Int(190i64));
        args1292.push(e.get("RW")?);
        fun1294.call(args1292, kw1293)?
    };
    {
        let fun1297 = e.get("text")?;
        let mut args1295 = Vec::new();
        let mut kw1296 = Vec::new();
        args1295.push(Val::Str("Fill both flavors.".into()));
        args1295.push(e.get("RIGHT")?);
        args1295.push(Val::Int(271i64));
        args1295.push(Val::Int(18i64));
        args1295.push(Val::Str("Bold".into()));
        args1295.push(e.get("NAVY")?);
        fun1297.call(args1295, kw1296)?
    };
    {
        let fun1300 = e.get("para")?;
        let mut args1298 = Vec::new();
        let mut kw1299 = Vec::new();
        args1298.push(Val::Str(
            "Use one concentrate bottle for each reservoir. The display walks you through Fill."
                .into(),
        ));
        args1298.push(e.get("RIGHT")?);
        args1298.push(Val::Int(304i64));
        args1298.push(e.get("RW")?);
        fun1300.call(args1298, kw1299)?
    };
    {
        let fun1303 = e.get("para")?;
        let mut args1301 = Vec::new();
        let mut kw1302 = Vec::new();
        args1301.push(Val::Str("<b>Then chill, choose and pour.</b><br/>The first chill takes about an hour. Fill your glass with ice before pouring.".into()));
        args1301.push(e.get("RIGHT")?);
        args1301.push(Val::Int(373i64));
        args1301.push(e.get("RW")?);
        args1301.push(Val::Int(12i64));
        args1301.push(Val::Int(17i64));
        kw1302.push(("limit".into(), Val::Int(68i64)));
        fun1303.call(args1301, kw1302)?
    };
    {
        let fun1306 = e.get("end")?;
        let mut args1304 = Vec::new();
        let mut kw1305 = Vec::new();
        fun1306.call(args1304, kw1305)?
    };
    {
        let fun1309 = e.get("header")?;
        let mut args1307 = Vec::new();
        let mut kw1308 = Vec::new();
        args1307.push(Val::Str("Your route to soda".into()));
        kw1308.push((
            "sub".into(),
            Val::Str(
                "Follow the seven steps in order. Page numbers below refer to this booklet.".into(),
            ),
        ));
        fun1309.call(args1307, kw1308)?
    };
    let assigned1310 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(1i64));
            s.push(Val::Str("Mount the faucet".into()));
            s.push(Val::Str("5-8".into()));
            s.push(Val::Int(5i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(2i64));
            s.push(Val::Str("Add the cold-water tee".into()));
            s.push(Val::Str("9-16".into()));
            s.push(Val::Int(9i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(3i64));
            s.push(Val::Str("Match the rear connections".into()));
            s.push(Val::Str("17-18".into()));
            s.push(Val::Int(17i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(4i64));
            s.push(Val::Str("Prepare the cylinder".into()));
            s.push(Val::Str("19-21".into()));
            s.push(Val::Int(19i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(5i64));
            s.push(Val::Str("Water, then gas, then power".into()));
            s.push(Val::Str("22-24".into()));
            s.push(Val::Int(22i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(6i64));
            s.push(Val::Str("Fill both flavors".into()));
            s.push(Val::Str("25-27".into()));
            s.push(Val::Int(25i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(7i64));
            s.push(Val::Str("Chill. Choose. Pour.".into()));
            s.push(Val::Str("28-29".into()));
            s.push(Val::Int(28i64));
            Val::tuple(s)
        });
        Val::list(s)
    };
    e.set("route", assigned1310.clone())?;
    for item1311 in {
        let fun1331 = e.get("enumerate")?;
        let mut args1329 = Vec::new();
        let mut kw1330 = Vec::new();
        args1329.push(e.get("route")?);
        fun1331.call(args1329, kw1330)?
    }
    .iter()?
    {
        let unpack1332 = unpack(item1311, 2)?;
        e.set("i", unpack1332[0].clone())?;
        let unpack1333 = unpack(unpack1332[1].clone(), 4)?;
        e.set("number", unpack1333[0].clone())?;
        e.set("title", unpack1333[1].clone())?;
        e.set("pages", unpack1333[2].clone())?;
        e.set("target", unpack1333[3].clone())?;
        let assigned1312 = binary(
            "add",
            Val::Int(145i64),
            binary("mul", e.get("i")?, Val::Int(36i64))?,
        )?;
        e.set("y", assigned1312.clone())?;
        {
            let fun1315 = e.get("badge")?;
            let mut args1313 = Vec::new();
            let mut kw1314 = Vec::new();
            args1313.push(e.get("number")?);
            args1313.push(e.get("M")?);
            args1313.push(e.get("y")?);
            args1313.push(Val::Int(11i64));
            fun1315.call(args1313, kw1314)?
        };
        {
            let fun1318 = e.get("text")?;
            let mut args1316 = Vec::new();
            let mut kw1317 = Vec::new();
            args1316.push(e.get("title")?);
            args1316.push(binary("add", e.get("M")?, Val::Int(35i64))?);
            args1316.push(binary("add", e.get("y")?, Val::Int(3i64))?);
            args1316.push(Val::Int(13i64));
            args1316.push(Val::Str("Semibold".into()));
            args1316.push(e.get("NAVY")?);
            fun1318.call(args1316, kw1317)?
        };
        {
            let fun1321 = e.get("text")?;
            let mut args1319 = Vec::new();
            let mut kw1320 = Vec::new();
            args1319.push(e.get("pages")?);
            args1319.push(binary("sub", Val::Int(327i64), {
                let fun1324 = e.get("pdfmetrics")?.attr("stringWidth")?;
                let mut args1322 = Vec::new();
                let mut kw1323 = Vec::new();
                args1322.push(e.get("pages")?);
                args1322.push(Val::Str("Regular".into()));
                args1322.push(Val::Int(11i64));
                fun1324.call(args1322, kw1323)?
            })?);
            args1319.push(binary("add", e.get("y")?, Val::Int(4i64))?);
            args1319.push(Val::Int(11i64));
            args1319.push(Val::Str("Regular".into()));
            args1319.push(e.get("MUTED")?);
            fun1321.call(args1319, kw1320)?
        };
        {
            let fun1327 = e.get("c")?.attr("linkRect")?;
            let mut args1325 = Vec::new();
            let mut kw1326 = Vec::new();
            args1325.push(Val::Str("".into()));
            args1325.push({
                let mut str1328 = String::new();
                str1328.push_str("page-");
                str1328.push_str(&format(
                    &binary("add", e.get("target")?, Val::Int(1i64))?,
                    &String::new(),
                )?);
                Val::Str(str1328)
            });
            args1325.push({
                let mut s = Vec::new();
                s.push(e.get("M")?);
                s.push(binary(
                    "sub",
                    binary("sub", e.get("H")?, e.get("y")?)?,
                    Val::Int(25i64),
                )?);
                s.push(Val::Int(333i64));
                s.push(binary(
                    "add",
                    binary("sub", e.get("H")?, e.get("y")?)?,
                    Val::Int(2i64),
                )?);
                Val::tuple(s)
            });
            kw1326.push(("relative".into(), Val::Int(1i64)));
            kw1326.push(("thickness".into(), Val::Int(0i64)));
            fun1327.call(args1325, kw1326)?
        };
    }
    {
        let fun1336 = e.get("note")?;
        let mut args1334 = Vec::new();
        let mut kw1335 = Vec::new();
        args1334.push(Val::Str("BEFORE THE FIRST CONNECTION".into()));
        args1334.push(Val::Str("Check the kit and space on pages 3-4. Keep the cylinder closed and the power cord unplugged while you install.".into()));
        args1334.push(Val::Int(149i64));
        args1334.push(e.get("RIGHT")?);
        args1334.push(e.get("RW")?);
        fun1336.call(args1334, kw1335)?
    };
    {
        let fun1339 = e.get("note")?;
        let mut args1337 = Vec::new();
        let mut kw1338 = Vec::new();
        args1337.push(Val::Str("KEEP THIS GUIDE".into()));
        args1337.push(Val::Str(
            "Care is on page 30. Connection checks are on pages 31-32.".into(),
        ));
        args1337.push(Val::Int(334i64));
        args1337.push(e.get("RIGHT")?);
        args1337.push(e.get("RW")?);
        fun1339.call(args1337, kw1338)?
    };
    {
        let fun1342 = e.get("end")?;
        let mut args1340 = Vec::new();
        let mut kw1341 = Vec::new();
        fun1342.call(args1340, kw1341)?
    };
    {
        let fun1345 = e.get("header")?;
        let mut args1343 = Vec::new();
        let mut kw1344 = Vec::new();
        args1343.push(Val::Str("Have everything ready".into()));
        kw1344.push((
            "sub".into(),
            Val::Str(
                "Unpack the kit. Have your own supplies ready before opening a water connection."
                    .into(),
            ),
        ));
        fun1345.call(args1343, kw1344)?
    };
    {
        let fun1348 = e.get("label")?;
        let mut args1346 = Vec::new();
        let mut kw1347 = Vec::new();
        args1346.push(Val::Str("IN THE BOX".into()));
        args1346.push(e.get("M")?);
        args1346.push(Val::Int(134i64));
        fun1348.call(args1346, kw1347)?
    };
    let assigned1349 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("machine".into()));
            s.push(Val::Str("Soda machine".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("faucet-and-plate".into()));
            s.push(Val::Str("Faucet +<br/>mounting plate".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("filtered-line".into()));
            s.push(Val::Str("Filtered water line".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("water-tees".into()));
            s.push(Val::Str("Both water tees".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("regulator-and-tether".into()));
            s.push(Val::Str("Regulator + CO2 tether<br/>+ nylon washer".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("collet-press".into()));
            s.push(Val::Str("Collet press".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("power-cord".into()));
            s.push(Val::Str("Power cord".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("install-guide".into()));
            s.push(Val::Str("Install guide".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("cold-kit".into()));
            s.push(Val::Str("Cold kit".into()));
            Val::tuple(s)
        });
        Val::list(s)
    };
    e.set("kit", assigned1349.clone())?;
    for item1350 in {
        let fun1376 = e.get("enumerate")?;
        let mut args1374 = Vec::new();
        let mut kw1375 = Vec::new();
        args1374.push(e.get("kit")?);
        fun1376.call(args1374, kw1375)?
    }
    .iter()?
    {
        let unpack1377 = unpack(item1350, 2)?;
        e.set("i", unpack1377[0].clone())?;
        let unpack1378 = unpack(unpack1377[1].clone(), 2)?;
        e.set("art", unpack1378[0].clone())?;
        e.set("title", unpack1378[1].clone())?;
        let assigned1351 = {
            let mut s = Vec::new();
            s.push(binary(
                "add",
                e.get("M")?,
                binary(
                    "mul",
                    binary("mod", e.get("i")?, Val::Int(3i64))?,
                    Val::Int(136i64),
                )?,
            )?);
            s.push(binary(
                "add",
                Val::Int(149i64),
                binary(
                    "mul",
                    binary("floordiv", e.get("i")?, Val::Int(3i64))?,
                    Val::Int(99i64),
                )?,
            )?);
            Val::tuple(s)
        };
        let unpack1352 = unpack(assigned1351.clone(), 2)?;
        e.set("x", unpack1352[0].clone())?;
        e.set("y", unpack1352[1].clone())?;
        let assigned1353 = if {
            let v1354 = Val::Str("<br/>".into());
            let v1355 = e.get("title")?;
            Val::Bool(compare("in", v1354.clone(), v1355.clone())?.truthy()?)
        }
        .truthy()?
        {
            Val::Int(25i64)
        } else {
            Val::Float(12.5f64)
        };
        e.set("title_height", assigned1353.clone())?;
        let assigned1356 = binary(
            "add",
            e.get("title_height")?,
            if {
                let v1357 = e.get("art")?;
                let v1358 = Val::Str("cold-kit".into());
                Val::Bool(compare("eq", v1357.clone(), v1358.clone())?.truthy()?)
            }
            .truthy()?
            {
                Val::Int(13i64)
            } else {
                Val::Int(0i64)
            },
        )?;
        e.set("caption_height", assigned1356.clone())?;
        let assigned1359 = binary(
            "sub",
            binary(
                "sub",
                binary("add", e.get("y")?, Val::Int(90i64))?,
                Val::Int(7i64),
            )?,
            e.get("caption_height")?,
        )?;
        e.set("caption_y", assigned1359.clone())?;
        {
            let fun1362 = e.get("rect")?;
            let mut args1360 = Vec::new();
            let mut kw1361 = Vec::new();
            args1360.push(e.get("x")?);
            args1360.push(e.get("y")?);
            args1360.push(Val::Int(128i64));
            args1360.push(Val::Int(90i64));
            args1360.push(Val::Str("#FFFFFF".into()));
            args1360.push(e.get("RULE")?);
            kw1361.push(("r".into(), Val::Int(4i64)));
            fun1362.call(args1360, kw1361)?
        };
        {
            let fun1365 = e.get("kit_picture")?;
            let mut args1363 = Vec::new();
            let mut kw1364 = Vec::new();
            args1363.push(e.get("art")?);
            args1363.push(binary("add", e.get("x")?, Val::Int(8i64))?);
            args1363.push(binary("add", e.get("y")?, Val::Int(5i64))?);
            args1363.push(Val::Int(112i64));
            args1363.push(binary(
                "sub",
                binary("sub", e.get("caption_y")?, e.get("y")?)?,
                Val::Int(10i64),
            )?);
            fun1365.call(args1363, kw1364)?
        };
        {
            let fun1368 = e.get("para")?;
            let mut args1366 = Vec::new();
            let mut kw1367 = Vec::new();
            args1366.push(e.get("title")?);
            args1366.push(binary("add", e.get("x")?, Val::Int(8i64))?);
            args1366.push(e.get("caption_y")?);
            args1366.push(Val::Int(112i64));
            args1366.push(Val::Float(10.5f64));
            args1366.push(Val::Float(12.5f64));
            args1366.push(e.get("INK")?);
            args1366.push(Val::Str("Semibold".into()));
            kw1367.push(("limit".into(), e.get("title_height")?));
            kw1367.push(("alignment".into(), Val::Int(1i64)));
            fun1368.call(args1366, kw1367)?
        };
        if {
            let v1369 = e.get("art")?;
            let v1370 = Val::Str("cold-kit".into());
            Val::Bool(compare("eq", v1369.clone(), v1370.clone())?.truthy()?)
        }
        .truthy()?
        {
            {
                let fun1373 = e.get("para")?;
                let mut args1371 = Vec::new();
                let mut kw1372 = Vec::new();
                args1371.push(Val::Str("Keep bagged for later.".into()));
                args1371.push(binary("add", e.get("x")?, Val::Int(8i64))?);
                args1371.push(binary(
                    "add",
                    binary("add", e.get("caption_y")?, e.get("title_height")?)?,
                    Val::Int(1i64),
                )?);
                args1371.push(Val::Int(112i64));
                args1371.push(Val::Int(9i64));
                args1371.push(Val::Int(12i64));
                args1371.push(e.get("MUTED")?);
                kw1372.push(("alignment".into(), Val::Int(1i64)));
                fun1373.call(args1371, kw1372)?
            };
        }
    }
    {
        let fun1381 = e.get("rect")?;
        let mut args1379 = Vec::new();
        let mut kw1380 = Vec::new();
        args1379.push(Val::Int(459i64));
        args1379.push(Val::Int(144i64));
        args1379.push(Val::Int(145i64));
        args1379.push(Val::Int(295i64));
        args1379.push(Val::Str("#F2F5FB".into()));
        kw1380.push(("r".into(), Val::Int(6i64)));
        fun1381.call(args1379, kw1380)?
    };
    {
        let fun1384 = e.get("label")?;
        let mut args1382 = Vec::new();
        let mut kw1383 = Vec::new();
        args1382.push(Val::Str("YOU SUPPLY".into()));
        args1382.push(Val::Int(473i64));
        args1382.push(Val::Int(159i64));
        args1382.push(e.get("NAVY")?);
        args1382.push(Val::Int(8i64));
        fun1384.call(args1382, kw1383)?
    };
    let assigned1385 = {
        let mut s = Vec::new();
        s.push(Val::Str("Filled 5 lb CO2 cylinder<br/>(CGA-320)".into()));
        s.push(Val::Str(
            "Concentrate for both flavors<br/>(SodaStream compatible)".into(),
        ));
        s.push(Val::Str("Adjustable wrench".into()));
        s.push(Val::Str("Second wrench for a braided hose".into()));
        s.push(Val::Str("Towel".into()));
        s.push(Val::Str("Prepared counter opening".into()));
        s.push(Val::Str("Grounded 120 V outlet".into()));
        Val::list(s)
    };
    e.set("supplies", assigned1385.clone())?;
    let assigned1386 = Val::Int(181i64);
    e.set("y", assigned1386.clone())?;
    for item1387 in e.get("supplies")?.iter()? {
        e.set("entry", item1387)?;
        {
            let fun1390 = e.get("rect")?;
            let mut args1388 = Vec::new();
            let mut kw1389 = Vec::new();
            args1388.push(Val::Int(473i64));
            args1388.push(binary("add", e.get("y")?, Val::Int(2i64))?);
            args1388.push(Val::Int(8i64));
            args1388.push(Val::Int(8i64));
            args1388.push(Val::Str("#FFFFFF".into()));
            args1388.push(e.get("MUTED")?);
            args1388.push(Val::Int(1i64));
            fun1390.call(args1388, kw1389)?
        };
        let assigned1391 = {
            let fun1394 = e.get("para")?;
            let mut args1392 = Vec::new();
            let mut kw1393 = Vec::new();
            args1392.push(e.get("entry")?);
            args1392.push(Val::Int(488i64));
            args1392.push(e.get("y")?);
            args1392.push(Val::Int(103i64));
            args1392.push(Val::Int(10i64));
            args1392.push(Val::Int(13i64));
            kw1393.push(("limit".into(), Val::Int(52i64)));
            fun1394.call(args1392, kw1393)?
        };
        e.set("h", assigned1391.clone())?;
        e.set(
            "y",
            binary(
                "add",
                e.get("y")?,
                binary("add", e.get("h")?, Val::Int(11i64))?,
            )?,
        )?;
    }
    {
        let fun1397 = e.get("end")?;
        let mut args1395 = Vec::new();
        let mut kw1396 = Vec::new();
        fun1397.call(args1395, kw1396)?
    };
    {
        let fun1400 = e.get("header")?;
        let mut args1398 = Vec::new();
        let mut kw1399 = Vec::new();
        args1398.push(Val::Str("Make room under the counter".into()));
        kw1399.push((
            "sub".into(),
            Val::Str(
                "Leave the cylinder valve, water shutoff and power plug easy to reach.".into(),
            ),
        ));
        fun1400.call(args1398, kw1399)?
    };
    {
        let fun1403 = e.get("rect")?;
        let mut args1401 = Vec::new();
        let mut kw1402 = Vec::new();
        args1401.push(Val::Int(65i64));
        args1401.push(Val::Int(152i64));
        args1401.push(Val::Int(237i64));
        args1401.push(Val::Int(224i64));
        args1401.push(e.get("ICE")?);
        kw1402.push(("r".into(), Val::Int(6i64)));
        fun1403.call(args1401, kw1402)?
    };
    {
        let fun1406 = e.get("rect")?;
        let mut args1404 = Vec::new();
        let mut kw1405 = Vec::new();
        args1404.push(Val::Int(97i64));
        args1404.push(Val::Int(179i64));
        args1404.push(Val::Int(172i64));
        args1404.push(Val::Int(194i64));
        args1404.push(Val::Str("#E8EBF0".into()));
        args1404.push(e.get("INK")?);
        args1404.push(Val::Int(4i64));
        fun1406.call(args1404, kw1405)?
    };
    {
        let fun1409 = e.get("rect")?;
        let mut args1407 = Vec::new();
        let mut kw1408 = Vec::new();
        args1407.push(Val::Int(110i64));
        args1407.push(Val::Int(292i64));
        args1407.push(Val::Int(146i64));
        args1407.push(Val::Int(68i64));
        args1407.push(Val::Str("#D8DCE3".into()));
        args1407.push(e.get("MUTED")?);
        args1407.push(Val::Int(3i64));
        fun1409.call(args1407, kw1408)?
    };
    {
        let fun1412 = e.get("text")?;
        let mut args1410 = Vec::new();
        let mut kw1411 = Vec::new();
        args1410.push(Val::Str("TOP VIEW".into()));
        args1410.push(Val::Int(150i64));
        args1410.push(Val::Int(229i64));
        args1410.push(Val::Int(11i64));
        args1410.push(Val::Str("Semibold".into()));
        args1410.push(e.get("MUTED")?);
        fun1412.call(args1410, kw1411)?
    };
    {
        let fun1415 = e.get("text")?;
        let mut args1413 = Vec::new();
        let mut kw1414 = Vec::new();
        args1413.push(Val::Str("Front".into()));
        args1413.push(Val::Int(165i64));
        args1413.push(Val::Int(391i64));
        args1413.push(Val::Int(11i64));
        args1413.push(Val::Str("Regular".into()));
        args1413.push(e.get("MUTED")?);
        fun1415.call(args1413, kw1414)?
    };
    {
        let fun1418 = e.get("text")?;
        let mut args1416 = Vec::new();
        let mut kw1417 = Vec::new();
        args1416.push(Val::Str("Machine envelope".into()));
        args1416.push(e.get("RIGHT")?);
        args1416.push(Val::Int(152i64));
        args1416.push(Val::Int(17i64));
        args1416.push(Val::Str("Bold".into()));
        args1416.push(e.get("NAVY")?);
        fun1418.call(args1416, kw1417)?
    };
    {
        let fun1421 = e.get("para")?;
        let mut args1419 = Vec::new();
        let mut kw1420 = Vec::new();
        args1419.push(Val::Str(
            "<b>8-1/2 in wide</b><br/><b>18-3/8 in deep</b><br/><b>14-3/8 in tall, with cover</b>"
                .into(),
        ));
        args1419.push(e.get("RIGHT")?);
        args1419.push(Val::Int(187i64));
        args1419.push(e.get("RW")?);
        args1419.push(Val::Int(13i64));
        args1419.push(Val::Int(20i64));
        fun1421.call(args1419, kw1420)?
    };
    {
        let fun1424 = e.get("para")?;
        let mut args1422 = Vec::new();
        let mut kw1423 = Vec::new();
        args1422.push(Val::Str("Leave <b>2-3/8 in behind</b> and <b>1-5/8 in on each side.</b> Keep the side air paths open.".into()));
        args1422.push(e.get("RIGHT")?);
        args1422.push(Val::Int(268i64));
        args1422.push(e.get("RW")?);
        fun1424.call(args1422, kw1423)?
    };
    {
        let fun1427 = e.get("para")?;
        let mut args1425 = Vec::new();
        let mut kw1426 = Vec::new();
        args1425.push(Val::Str("Above: room to tip a bottle just past level over the funnel.<br/><br/>Beside it: space for the cylinder, about 5-1/4 in across and 18 in tall, plus its regulator.".into()));
        args1425.push(e.get("RIGHT")?);
        args1425.push(Val::Int(338i64));
        args1425.push(e.get("RW")?);
        args1425.push(Val::Int(12i64));
        args1425.push(Val::Int(17i64));
        kw1426.push(("limit".into(), Val::Int(102i64)));
        fun1427.call(args1425, kw1426)?
    };
    {
        let fun1430 = e.get("end")?;
        let mut args1428 = Vec::new();
        let mut kw1429 = Vec::new();
        fun1430.call(args1428, kw1429)?
    };
    {
        let fun1433 = e.get("header")?;
        let mut args1431 = Vec::new();
        let mut kw1432 = Vec::new();
        args1431.push(Val::Str("Prepare the counter opening".into()));
        args1431.push(Val::Str("INSTALL / MOUNT THE FAUCET".into()));
        args1431.push(Val::Int(1i64));
        fun1433.call(args1431, kw1432)?
    };
    {
        let fun1436 = e.get("pic")?;
        let mut args1434 = Vec::new();
        let mut kw1435 = Vec::new();
        args1434.push(Val::Str("opening.png".into()));
        args1434.push(e.get("M")?);
        args1434.push(Val::Int(151i64));
        args1434.push(Val::Int(264i64));
        args1434.push(Val::Int(220i64));
        fun1436.call(args1434, kw1435)?
    };
    {
        let fun1439 = e.get("text")?;
        let mut args1437 = Vec::new();
        let mut kw1438 = Vec::new();
        args1437.push(Val::Str("One 1-3/8 in opening".into()));
        args1437.push(e.get("RIGHT")?);
        args1437.push(Val::Int(158i64));
        args1437.push(Val::Int(18i64));
        args1437.push(Val::Str("Bold".into()));
        args1437.push(e.get("NAVY")?);
        fun1439.call(args1437, kw1438)?
    };
    {
        let fun1442 = e.get("para")?;
        let mut args1440 = Vec::new();
        let mut kw1441 = Vec::new();
        args1440.push(Val::Str("Place the hole center <b>at most 2 in behind the bowl edge.</b> Aim the faucet into the bowl, within 10 degrees of straight ahead.".into()));
        args1440.push(e.get("RIGHT")?);
        args1440.push(Val::Int(194i64));
        args1440.push(e.get("RW")?);
        args1440.push(Val::Int(12i64));
        args1440.push(Val::Int(17i64));
        kw1441.push(("limit".into(), Val::Int(133i64)));
        fun1442.call(args1440, kw1441)?
    };
    {
        let fun1445 = e.get("note")?;
        let mut args1443 = Vec::new();
        let mut kw1444 = Vec::new();
        args1443.push(Val::Str("STONE COUNTER".into()));
        args1443.push(Val::Str(
            "Use a spare 1-3/8 in sink or counter hole, or a 1-3/8 in diamond core bit kept wet."
                .into(),
        ));
        args1443.push(Val::Int(351i64));
        args1443.push(e.get("RIGHT")?);
        args1443.push(e.get("RW")?);
        fun1445.call(args1443, kw1444)?
    };
    {
        let fun1448 = e.get("caption")?;
        let mut args1446 = Vec::new();
        let mut kw1447 = Vec::new();
        args1446.push(Val::Str(
            "Prepare the opening before lowering the faucet.".into(),
        ));
        args1446.push(Val::Int(390i64));
        fun1448.call(args1446, kw1447)?
    };
    {
        let fun1451 = e.get("end")?;
        let mut args1449 = Vec::new();
        let mut kw1450 = Vec::new();
        fun1451.call(args1449, kw1450)?
    };
    {
        let fun1454 = e.get("header")?;
        let mut args1452 = Vec::new();
        let mut kw1453 = Vec::new();
        args1452.push(Val::Str("Lower. Then push back.".into()));
        args1452.push(Val::Str("INSTALL / MOUNT THE FAUCET".into()));
        args1452.push(Val::Int(1i64));
        fun1454.call(args1452, kw1453)?
    };
    let assigned1455 = {
        let fun1458 = e.get("pic")?;
        let mut args1456 = Vec::new();
        let mut kw1457 = Vec::new();
        args1456.push(Val::Str("steps/mount-drop.png".into()));
        args1456.push(e.get("M")?);
        args1456.push(Val::Int(125i64));
        args1456.push(Val::Int(274i64));
        args1456.push(Val::Int(294i64));
        kw1457.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(9i64));
            s.push(Val::Int(33i64));
            s.push(Val::Int(763i64));
            s.push(Val::Int(1331i64));
            Val::tuple(s)
        }));
        fun1458.call(args1456, kw1457)?
    };
    e.set("p", assigned1455.clone())?;
    {
        let fun1461 = e.get("arrow")?;
        let mut args1459 = Vec::new();
        let mut kw1460 = Vec::new();
        args1459.extend(
            {
                let fun1464 = e.get("p")?;
                let mut args1462 = Vec::new();
                let mut kw1463 = Vec::new();
                args1462.push(Val::Int(190i64));
                args1462.push(Val::Int(660i64));
                fun1464.call(args1462, kw1463)?
            }
            .iter()?,
        );
        args1459.extend(
            {
                let fun1467 = e.get("p")?;
                let mut args1465 = Vec::new();
                let mut kw1466 = Vec::new();
                args1465.push(Val::Int(190i64));
                args1465.push(Val::Int(963i64));
                fun1467.call(args1465, kw1466)?
            }
            .iter()?,
        );
        kw1460.push(("head".into(), Val::Int(11i64)));
        fun1461.call(args1459, kw1460)?
    };
    {
        let fun1470 = e.get("arrow")?;
        let mut args1468 = Vec::new();
        let mut kw1469 = Vec::new();
        args1468.extend(
            {
                let fun1473 = e.get("p")?;
                let mut args1471 = Vec::new();
                let mut kw1472 = Vec::new();
                args1471.push(Val::Int(382i64));
                args1471.push(Val::Int(866i64));
                fun1473.call(args1471, kw1472)?
            }
            .iter()?,
        );
        args1468.extend(
            {
                let fun1476 = e.get("p")?;
                let mut args1474 = Vec::new();
                let mut kw1475 = Vec::new();
                args1474.push(Val::Int(585i64));
                args1474.push(Val::Int(928i64));
                fun1476.call(args1474, kw1475)?
            }
            .iter()?,
        );
        kw1469.push(("head".into(), Val::Int(10i64)));
        fun1470.call(args1468, kw1469)?
    };
    {
        let fun1479 = e.get("item")?;
        let mut args1477 = Vec::new();
        let mut kw1478 = Vec::new();
        args1477.push(Val::Str("1 / LOWER".into()));
        args1477.push(Val::Str("Feed the tails through".into()));
        args1477.push(Val::Str("Pass all four attached tubes and the display cable through the opening. The small white tube is DRAIN. Lower the faucet onto the counter.".into()));
        args1477.push(Val::Int(151i64));
        fun1479.call(args1477, kw1478)?
    };
    {
        let fun1482 = e.get("item")?;
        let mut args1480 = Vec::new();
        let mut kw1481 = Vec::new();
        args1480.push(Val::Str("2 / POSITION".into()));
        args1480.push(Val::Str("Push the faucet back".into()));
        args1480.push(Val::Str("Push it away from you until the rear tube bundle meets the back edge of the hole. Hold that position for the plate.".into()));
        args1480.push(Val::Int(299i64));
        fun1482.call(args1480, kw1481)?
    };
    {
        let fun1485 = e.get("end")?;
        let mut args1483 = Vec::new();
        let mut kw1484 = Vec::new();
        fun1485.call(args1483, kw1484)?
    };
    {
        let fun1488 = e.get("header")?;
        let mut args1486 = Vec::new();
        let mut kw1487 = Vec::new();
        args1486.push(Val::Str("Slide the plate into place".into()));
        args1486.push(Val::Str("INSTALL / MOUNT THE FAUCET".into()));
        args1486.push(Val::Int(1i64));
        fun1488.call(args1486, kw1487)?
    };
    let assigned1489 = {
        let fun1492 = e.get("pic")?;
        let mut args1490 = Vec::new();
        let mut kw1491 = Vec::new();
        args1490.push(Val::Str("steps/mount-under-slide-clean.png".into()));
        args1490.push(e.get("M")?);
        args1490.push(Val::Int(132i64));
        args1490.push(Val::Int(278i64));
        args1490.push(Val::Int(126i64));
        kw1491.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(205i64));
            s.push(Val::Int(280i64));
            s.push(Val::Int(1090i64));
            s.push(Val::Int(650i64));
            Val::tuple(s)
        }));
        fun1492.call(args1490, kw1491)?
    };
    e.set("p", assigned1489.clone())?;
    {
        let fun1495 = e.get("arrow")?;
        let mut args1493 = Vec::new();
        let mut kw1494 = Vec::new();
        args1493.extend(
            {
                let fun1498 = e.get("p")?;
                let mut args1496 = Vec::new();
                let mut kw1497 = Vec::new();
                args1496.push(Val::Int(430i64));
                args1496.push(Val::Int(540i64));
                fun1498.call(args1496, kw1497)?
            }
            .iter()?,
        );
        args1493.extend(
            {
                let fun1501 = e.get("p")?;
                let mut args1499 = Vec::new();
                let mut kw1500 = Vec::new();
                args1499.push(Val::Int(870i64));
                args1499.push(Val::Int(455i64));
                fun1501.call(args1499, kw1500)?
            }
            .iter()?,
        );
        kw1494.push(("head".into(), Val::Int(10i64)));
        fun1495.call(args1493, kw1494)?
    };
    {
        let fun1504 = e.get("caption")?;
        let mut args1502 = Vec::new();
        let mut kw1503 = Vec::new();
        args1502.push(Val::Str("The plate sits above the washer and nut.".into()));
        args1502.push(Val::Int(261i64));
        fun1504.call(args1502, kw1503)?
    };
    {
        let fun1507 = e.get("item")?;
        let mut args1505 = Vec::new();
        let mut kw1506 = Vec::new();
        args1505.push(Val::Str("3 / FROM BELOW".into()));
        args1505.push(Val::Str("Hold the plate flat".into()));
        args1505.push(Val::Str("Hold the steel plate flat against the counter, above the washer and nut. Slide it onto the shank and rear bundle.".into()));
        args1505.push(Val::Int(132i64));
        fun1507.call(args1505, kw1506)?
    };
    {
        let fun1510 = e.get("para")?;
        let mut args1508 = Vec::new();
        let mut kw1509 = Vec::new();
        args1508.push(Val::Str("Match the slots as shown below.".into()));
        args1508.push(e.get("RIGHT")?);
        args1508.push(Val::Int(250i64));
        args1508.push(e.get("RW")?);
        args1508.push(Val::Int(12i64));
        args1508.push(Val::Int(17i64));
        kw1509.push(("limit".into(), Val::Int(17i64)));
        fun1510.call(args1508, kw1509)?
    };
    {
        let fun1513 = e.get("mounting_slots")?;
        let mut args1511 = Vec::new();
        let mut kw1512 = Vec::new();
        fun1513.call(args1511, kw1512)?
    };
    {
        let fun1516 = e.get("end")?;
        let mut args1514 = Vec::new();
        let mut kw1515 = Vec::new();
        fun1516.call(args1514, kw1515)?
    };
    {
        let fun1519 = e.get("header")?;
        let mut args1517 = Vec::new();
        let mut kw1518 = Vec::new();
        args1517.push(Val::Str("Tighten the faucet nut".into()));
        args1517.push(Val::Str("INSTALL / MOUNT THE FAUCET".into()));
        args1517.push(Val::Int(1i64));
        fun1519.call(args1517, kw1518)?
    };
    {
        let fun1522 = e.get("pic")?;
        let mut args1520 = Vec::new();
        let mut kw1521 = Vec::new();
        args1520.push(Val::Str("steps/mount-under-tighten-clean.png".into()));
        args1520.push(e.get("M")?);
        args1520.push(Val::Int(132i64));
        args1520.push(Val::Int(278i64));
        args1520.push(Val::Int(126i64));
        kw1521.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(740i64));
            s.push(Val::Int(310i64));
            s.push(Val::Int(1180i64));
            s.push(Val::Int(610i64));
            Val::tuple(s)
        }));
        fun1522.call(args1520, kw1521)?
    };
    {
        let fun1525 = e.get("caption")?;
        let mut args1523 = Vec::new();
        let mut kw1524 = Vec::new();
        args1523.push(Val::Str("The plate stays above the washer and nut.".into()));
        args1523.push(Val::Int(261i64));
        fun1525.call(args1523, kw1524)?
    };
    {
        let fun1528 = e.get("item")?;
        let mut args1526 = Vec::new();
        let mut kw1527 = Vec::new();
        args1526.push(Val::Str("4 / SECURE".into()));
        args1526.push(Val::Str("Hand-tighten the nut".into()));
        args1526.push(Val::Str("Keep the plate flat against the counter and the faucet pushed back. Hand-tighten the nut against the washer.".into()));
        args1526.push(Val::Int(132i64));
        fun1528.call(args1526, kw1527)?
    };
    {
        let fun1531 = e.get("para")?;
        let mut args1529 = Vec::new();
        let mut kw1530 = Vec::new();
        args1529.push(Val::Str(
            "Keep the neck-joint drain opening entirely over the bowl and uncovered.".into(),
        ));
        args1529.push(e.get("RIGHT")?);
        args1529.push(Val::Int(244i64));
        args1529.push(e.get("RW")?);
        args1529.push(Val::Int(11i64));
        args1529.push(Val::Int(14i64));
        kw1530.push(("limit".into(), Val::Int(28i64)));
        fun1531.call(args1529, kw1530)?
    };
    {
        let fun1534 = e.get("mounting_slots")?;
        let mut args1532 = Vec::new();
        let mut kw1533 = Vec::new();
        fun1534.call(args1532, kw1533)?
    };
    {
        let fun1537 = e.get("end")?;
        let mut args1535 = Vec::new();
        let mut kw1536 = Vec::new();
        fun1537.call(args1535, kw1536)?
    };
    {
        let fun1540 = e.get("header")?;
        let mut args1538 = Vec::new();
        let mut kw1539 = Vec::new();
        args1538.push(Val::Str("Which water connection?".into()));
        args1538.push(Val::Str("INSTALL / ADD THE COLD-WATER TEE".into()));
        args1538.push(Val::Int(2i64));
        args1538.push(Val::Str(
            "Look at the cold supply under your sink. Use the tee that matches it.".into(),
        ));
        fun1540.call(args1538, kw1539)?
    };
    {
        let fun1543 = e.get("pic")?;
        let mut args1541 = Vec::new();
        let mut kw1542 = Vec::new();
        args1541.push(Val::Str("kitchen-push.png".into()));
        args1541.push(e.get("M")?);
        args1541.push(Val::Int(145i64));
        args1541.push(Val::Int(225i64));
        args1541.push(Val::Int(121i64));
        fun1543.call(args1541, kw1542)?
    };
    {
        let fun1546 = e.get("text")?;
        let mut args1544 = Vec::new();
        let mut kw1545 = Vec::new();
        args1544.push(Val::Str("1/4 in plastic tube".into()));
        args1544.push(e.get("M")?);
        args1544.push(Val::Int(286i64));
        args1544.push(Val::Int(18i64));
        args1544.push(Val::Str("Bold".into()));
        args1544.push(e.get("NAVY")?);
        fun1546.call(args1544, kw1545)?
    };
    {
        let fun1549 = e.get("para")?;
        let mut args1547 = Vec::new();
        let mut kw1548 = Vec::new();
        args1547.push(Val::Str("A small tube in a push fitting, like a filter or refrigerator line. Use the <b>black tee</b>.".into()));
        args1547.push(e.get("M")?);
        args1547.push(Val::Int(321i64));
        args1547.push(Val::Int(258i64));
        fun1549.call(args1547, kw1548)?
    };
    {
        let fun1552 = e.get("text")?;
        let mut args1550 = Vec::new();
        let mut kw1551 = Vec::new();
        args1550.push(Val::Str("Continue on pages 10-12".into()));
        args1550.push(e.get("M")?);
        args1550.push(Val::Int(403i64));
        args1550.push(Val::Int(12i64));
        args1550.push(Val::Str("Bold".into()));
        args1550.push(e.get("BLUE")?);
        fun1552.call(args1550, kw1551)?
    };
    {
        let fun1555 = e.get("pic")?;
        let mut args1553 = Vec::new();
        let mut kw1554 = Vec::new();
        args1553.push(Val::Str("kitchen-hose.png".into()));
        args1553.push(e.get("RIGHT")?);
        args1553.push(Val::Int(145i64));
        args1553.push(e.get("RW")?);
        args1553.push(Val::Int(121i64));
        fun1555.call(args1553, kw1554)?
    };
    {
        let fun1558 = e.get("text")?;
        let mut args1556 = Vec::new();
        let mut kw1557 = Vec::new();
        args1556.push(Val::Str("Braided hose".into()));
        args1556.push(e.get("RIGHT")?);
        args1556.push(Val::Int(286i64));
        args1556.push(Val::Int(18i64));
        args1556.push(Val::Str("Bold".into()));
        args1556.push(e.get("NAVY")?);
        fun1558.call(args1556, kw1557)?
    };
    {
        let fun1561 = e.get("para")?;
        let mut args1559 = Vec::new();
        let mut kw1560 = Vec::new();
        args1559.push(Val::Str("A braided supply hose threaded onto a <b>3/8 in shutoff</b>. Use the <b>white tee</b>.".into()));
        args1559.push(e.get("RIGHT")?);
        args1559.push(Val::Int(321i64));
        args1559.push(e.get("RW")?);
        fun1561.call(args1559, kw1560)?
    };
    {
        let fun1564 = e.get("text")?;
        let mut args1562 = Vec::new();
        let mut kw1563 = Vec::new();
        args1562.push(Val::Str("Continue on pages 13-16".into()));
        args1562.push(e.get("RIGHT")?);
        args1562.push(Val::Int(403i64));
        args1562.push(Val::Int(12i64));
        args1562.push(Val::Str("Bold".into()));
        args1562.push(e.get("BLUE")?);
        fun1564.call(args1562, kw1563)?
    };
    {
        let fun1567 = e.get("end")?;
        let mut args1565 = Vec::new();
        let mut kw1566 = Vec::new();
        fun1567.call(args1565, kw1566)?
    };
    {
        let fun1570 = e.get("header")?;
        let mut args1568 = Vec::new();
        let mut kw1569 = Vec::new();
        args1568.push(Val::Str("Close the cold-water shutoff".into()));
        args1568.push(Val::Str("INSTALL / PLASTIC-TUBE CONNECTION".into()));
        args1568.push(Val::Int(2i64));
        fun1570.call(args1568, kw1569)?
    };
    {
        let fun1573 = e.get("pic")?;
        let mut args1571 = Vec::new();
        let mut kw1572 = Vec::new();
        args1571.push(Val::Str("steps/modern-water-off.png".into()));
        args1571.push(e.get("M")?);
        args1571.push(Val::Int(167i64));
        args1571.push(Val::Int(278i64));
        args1571.push(Val::Int(169i64));
        kw1572.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(170i64));
            s.push(Val::Int(190i64));
            s.push(Val::Int(1100i64));
            s.push(Val::Int(635i64));
            Val::tuple(s)
        }));
        fun1573.call(args1571, kw1572)?
    };
    {
        let fun1576 = e.get("caption")?;
        let mut args1574 = Vec::new();
        let mut kw1575 = Vec::new();
        args1574.push(Val::Str(
            "Keep the shutoff closed while making connections.".into(),
        ));
        args1574.push(Val::Int(368i64));
        fun1576.call(args1574, kw1575)?
    };
    {
        let fun1579 = e.get("item")?;
        let mut args1577 = Vec::new();
        let mut kw1578 = Vec::new();
        args1577.push(Val::Str("1 / WATER OFF".into()));
        args1577.push(Val::Str("Wait for flow to stop".into()));
        args1577.push(Val::Str(
            "Close the cold-water shutoff. Run the tap or dispenser on that line until flow stops."
                .into(),
        ));
        args1577.push(Val::Int(156i64));
        fun1579.call(args1577, kw1578)?
    };
    {
        let fun1582 = e.get("para")?;
        let mut args1580 = Vec::new();
        let mut kw1581 = Vec::new();
        args1580.push(Val::Str(
            "Put a towel beneath the fitting to catch the water left in the tube.".into(),
        ));
        args1580.push(e.get("RIGHT")?);
        args1580.push(Val::Int(318i64));
        args1580.push(e.get("RW")?);
        fun1582.call(args1580, kw1581)?
    };
    {
        let fun1585 = e.get("end")?;
        let mut args1583 = Vec::new();
        let mut kw1584 = Vec::new();
        fun1585.call(args1583, kw1584)?
    };
    {
        let fun1588 = e.get("header")?;
        let mut args1586 = Vec::new();
        let mut kw1587 = Vec::new();
        args1586.push(Val::Str("Release the original tube".into()));
        args1586.push(Val::Str("INSTALL / PLASTIC-TUBE CONNECTION".into()));
        args1586.push(Val::Int(2i64));
        fun1588.call(args1586, kw1587)?
    };
    let assigned1589 = {
        let fun1592 = e.get("pic")?;
        let mut args1590 = Vec::new();
        let mut kw1591 = Vec::new();
        args1590.push(Val::Str("steps/release-with-press.png".into()));
        args1590.push(e.get("M")?);
        args1590.push(Val::Int(173i64));
        args1590.push(Val::Int(278i64));
        args1590.push(Val::Int(173i64));
        kw1591.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(0i64));
            s.push(Val::Int(0i64));
            s.push(Val::Int(1840i64));
            s.push(Val::Int(1040i64));
            Val::tuple(s)
        }));
        fun1592.call(args1590, kw1591)?
    };
    e.set("p", assigned1589.clone())?;
    {
        let fun1595 = e.get("arrow")?;
        let mut args1593 = Vec::new();
        let mut kw1594 = Vec::new();
        args1593.extend(
            {
                let fun1598 = e.get("p")?;
                let mut args1596 = Vec::new();
                let mut kw1597 = Vec::new();
                args1596.push(Val::Float(1316.97f64));
                args1596.push(Val::Float(779.94f64));
                fun1598.call(args1596, kw1597)?
            }
            .iter()?,
        );
        args1593.extend(
            {
                let fun1601 = e.get("p")?;
                let mut args1599 = Vec::new();
                let mut kw1600 = Vec::new();
                args1599.push(Val::Float(1042.29f64));
                args1599.push(Val::Float(700.52f64));
                fun1601.call(args1599, kw1600)?
            }
            .iter()?,
        );
        kw1594.push(("head".into(), Val::Int(8i64)));
        fun1595.call(args1593, kw1594)?
    };
    {
        let fun1604 = e.get("arrow")?;
        let mut args1602 = Vec::new();
        let mut kw1603 = Vec::new();
        args1602.extend(
            {
                let fun1607 = e.get("p")?;
                let mut args1605 = Vec::new();
                let mut kw1606 = Vec::new();
                args1605.push(Val::Int(1510i64));
                args1605.push(Val::Int(554i64));
                fun1607.call(args1605, kw1606)?
            }
            .iter()?,
        );
        args1602.extend(
            {
                let fun1610 = e.get("p")?;
                let mut args1608 = Vec::new();
                let mut kw1609 = Vec::new();
                args1608.push(Val::Int(1780i64));
                args1608.push(Val::Int(632i64));
                fun1610.call(args1608, kw1609)?
            }
            .iter()?,
        );
        kw1603.push(("head".into(), Val::Int(8i64)));
        fun1604.call(args1602, kw1603)?
    };
    {
        let fun1613 = e.get("item")?;
        let mut args1611 = Vec::new();
        let mut kw1612 = Vec::new();
        args1611.push(Val::Str("2 / RELEASE".into()));
        args1611.push(Val::Str("Hold the ring in".into()));
        args1611.push(Val::Str("Use the collet press to hold the fitting's release ring in. With your other hand, pull the original white tube out.".into()));
        args1611.push(Val::Int(153i64));
        fun1613.call(args1611, kw1612)?
    };
    {
        let fun1616 = e.get("note")?;
        let mut args1614 = Vec::new();
        let mut kw1615 = Vec::new();
        args1614.push(Val::Str("KEEP THE TOOL".into()));
        args1614.push(Val::Str("The collet press also releases the machine's push-connect tubes when their pressure has been relieved.".into()));
        args1614.push(Val::Int(321i64));
        args1614.push(e.get("RIGHT")?);
        args1614.push(e.get("RW")?);
        fun1616.call(args1614, kw1615)?
    };
    {
        let fun1619 = e.get("end")?;
        let mut args1617 = Vec::new();
        let mut kw1618 = Vec::new();
        fun1619.call(args1617, kw1618)?
    };
    {
        let fun1622 = e.get("header")?;
        let mut args1620 = Vec::new();
        let mut kw1621 = Vec::new();
        args1620.push(Val::Str("Fit the black tee".into()));
        args1620.push(Val::Str("INSTALL / PLASTIC-TUBE CONNECTION".into()));
        args1620.push(Val::Int(2i64));
        fun1622.call(args1620, kw1621)?
    };
    let assigned1623 = {
        let fun1626 = e.get("pic")?;
        let mut args1624 = Vec::new();
        let mut kw1625 = Vec::new();
        args1624.push(Val::Str("steps/modern-tee-assembly-ready.png".into()));
        args1624.push(e.get("M")?);
        args1624.push(Val::Int(145i64));
        args1624.push(Val::Int(278i64));
        args1624.push(Val::Int(90i64));
        kw1625.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(200i64));
            s.push(Val::Int(130i64));
            s.push(Val::Int(1860i64));
            s.push(Val::Int(670i64));
            Val::tuple(s)
        }));
        fun1626.call(args1624, kw1625)?
    };
    e.set("p", assigned1623.clone())?;
    {
        let fun1629 = e.get("arrow")?;
        let mut args1627 = Vec::new();
        let mut kw1628 = Vec::new();
        args1627.extend(
            {
                let fun1632 = e.get("p")?;
                let mut args1630 = Vec::new();
                let mut kw1631 = Vec::new();
                args1630.push(Val::Int(1110i64));
                args1630.push(Val::Int(170i64));
                fun1632.call(args1630, kw1631)?
            }
            .iter()?,
        );
        args1627.extend(
            {
                let fun1635 = e.get("p")?;
                let mut args1633 = Vec::new();
                let mut kw1634 = Vec::new();
                args1633.push(Val::Int(810i64));
                args1633.push(Val::Int(170i64));
                fun1635.call(args1633, kw1634)?
            }
            .iter()?,
        );
        kw1628.push(("head".into(), Val::Int(9i64)));
        fun1629.call(args1627, kw1628)?
    };
    {
        let fun1638 = e.get("pic")?;
        let mut args1636 = Vec::new();
        let mut kw1637 = Vec::new();
        args1636.push(Val::Str("steps/modern-tee-complete.png".into()));
        args1636.push(e.get("M")?);
        args1636.push(Val::Int(286i64));
        args1636.push(Val::Int(278i64));
        args1636.push(Val::Int(90i64));
        kw1637.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(200i64));
            s.push(Val::Int(130i64));
            s.push(Val::Int(1860i64));
            s.push(Val::Int(670i64));
            Val::tuple(s)
        }));
        fun1638.call(args1636, kw1637)?
    };
    {
        let fun1641 = e.get("item")?;
        let mut args1639 = Vec::new();
        let mut kw1640 = Vec::new();
        args1639.push(Val::Str("3 / JUMPER".into()));
        args1639.push(Val::Str("Push it fully home".into()));
        args1639.push(Val::Str(
            "Push the short jumper on the supplied black tee into the fitting you opened.".into(),
        ));
        args1639.push(Val::Int(137i64));
        fun1641.call(args1639, kw1640)?
    };
    {
        let fun1644 = e.get("item")?;
        let mut args1642 = Vec::new();
        let mut kw1643 = Vec::new();
        args1642.push(Val::Str("4 / ORIGINAL TUBE".into()));
        args1642.push(Val::Str("Reconnect. Then tug.".into()));
        args1642.push(Val::Str("Push the original tube into the tee's open end. Tug both joints gently to check they hold.".into()));
        args1642.push(Val::Int(281i64));
        fun1644.call(args1642, kw1643)?
    };
    {
        let fun1647 = e.get("caption")?;
        let mut args1645 = Vec::new();
        let mut kw1646 = Vec::new();
        args1645.push(Val::Str(
            "Keep the filtered white run attached. Go to page 17.".into(),
        ));
        args1645.push(Val::Int(403i64));
        kw1646.push(("w".into(), e.get("CW")?));
        fun1647.call(args1645, kw1646)?
    };
    {
        let fun1650 = e.get("end")?;
        let mut args1648 = Vec::new();
        let mut kw1649 = Vec::new();
        fun1650.call(args1648, kw1649)?
    };
    {
        let fun1653 = e.get("header")?;
        let mut args1651 = Vec::new();
        let mut kw1652 = Vec::new();
        args1651.push(Val::Str("Prepare the braided-hose connection".into()));
        args1651.push(Val::Str("INSTALL / BRAIDED-HOSE CONNECTION".into()));
        args1651.push(Val::Int(2i64));
        fun1653.call(args1651, kw1652)?
    };
    {
        let fun1656 = e.get("pic")?;
        let mut args1654 = Vec::new();
        let mut kw1655 = Vec::new();
        args1654.push(Val::Str("two-tees.png".into()));
        args1654.push(e.get("M")?);
        args1654.push(Val::Int(162i64));
        args1654.push(Val::Int(274i64));
        args1654.push(Val::Int(121i64));
        fun1656.call(args1654, kw1655)?
    };
    {
        let fun1659 = e.get("caption")?;
        let mut args1657 = Vec::new();
        let mut kw1658 = Vec::new();
        args1657.push(Val::Str("The white tee has a side-port lever.".into()));
        args1657.push(Val::Int(315i64));
        fun1659.call(args1657, kw1658)?
    };
    {
        let fun1662 = e.get("item")?;
        let mut args1660 = Vec::new();
        let mut kw1661 = Vec::new();
        args1660.push(Val::Str("1 / FIND COLD".into()));
        args1660.push(Val::Str("Trace the hose to its valve".into()));
        args1660.push(Val::Str("The white tee fits a 3/8 in outlet. Close that valve, then open the kitchen faucet on cold. Wait for flow to stop.".into()));
        args1660.push(Val::Int(145i64));
        fun1662.call(args1660, kw1661)?
    };
    {
        let fun1665 = e.get("note")?;
        let mut args1663 = Vec::new();
        let mut kw1664 = Vec::new();
        args1663.push(Val::Str("BEFORE LOOSENING".into()));
        args1663.push(Val::Str("If water keeps flowing, leave the hose connected; the shutoff needs repair. Put a towel below the connection.".into()));
        args1663.push(Val::Int(321i64));
        args1663.push(e.get("RIGHT")?);
        args1663.push(e.get("RW")?);
        args1663.push(Val::Str("orange".into()));
        fun1665.call(args1663, kw1664)?
    };
    {
        let fun1668 = e.get("end")?;
        let mut args1666 = Vec::new();
        let mut kw1667 = Vec::new();
        fun1668.call(args1666, kw1667)?
    };
    {
        let fun1671 = e.get("header")?;
        let mut args1669 = Vec::new();
        let mut kw1670 = Vec::new();
        args1669.push(Val::Str("Lift the braided hose clear".into()));
        args1669.push(Val::Str("INSTALL / BRAIDED-HOSE CONNECTION".into()));
        args1669.push(Val::Int(2i64));
        fun1671.call(args1669, kw1670)?
    };
    {
        let fun1674 = e.get("pic")?;
        let mut args1672 = Vec::new();
        let mut kw1673 = Vec::new();
        args1672.push(Val::Str("hose-attached.png".into()));
        args1672.push(e.get("M")?);
        args1672.push(Val::Int(135i64));
        args1672.push(Val::Int(130i64));
        args1672.push(Val::Int(215i64));
        kw1673.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(270i64));
            s.push(Val::Int(0i64));
            s.push(Val::Int(820i64));
            s.push(Val::Int(940i64));
            Val::tuple(s)
        }));
        fun1674.call(args1672, kw1673)?
    };
    {
        let fun1677 = e.get("pic")?;
        let mut args1675 = Vec::new();
        let mut kw1676 = Vec::new();
        args1675.push(Val::Str("hose-removed.png".into()));
        args1675.push(Val::Int(192i64));
        args1675.push(Val::Int(135i64));
        args1675.push(Val::Int(130i64));
        args1675.push(Val::Int(215i64));
        kw1676.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(270i64));
            s.push(Val::Int(0i64));
            s.push(Val::Int(820i64));
            s.push(Val::Int(940i64));
            Val::tuple(s)
        }));
        fun1677.call(args1675, kw1676)?
    };
    {
        let fun1680 = e.get("caption")?;
        let mut args1678 = Vec::new();
        let mut kw1679 = Vec::new();
        args1678.push(Val::Str("Valve closed".into()));
        args1678.push(Val::Int(369i64));
        kw1679.push(("w".into(), Val::Int(130i64)));
        fun1680.call(args1678, kw1679)?
    };
    {
        let fun1683 = e.get("caption")?;
        let mut args1681 = Vec::new();
        let mut kw1682 = Vec::new();
        args1681.push(Val::Str("Hose lifted clear".into()));
        args1681.push(Val::Int(369i64));
        kw1682.push(("x".into(), Val::Int(192i64)));
        kw1682.push(("w".into(), Val::Int(130i64)));
        fun1683.call(args1681, kw1682)?
    };
    {
        let fun1686 = e.get("item")?;
        let mut args1684 = Vec::new();
        let mut kw1685 = Vec::new();
        args1684.push(Val::Str("2 / TWO WRENCHES".into()));
        args1684.push(Val::Str("Hold the valve steady".into()));
        args1684.push(Val::Str("Use one wrench on the valve body while the other loosens the hose nut. Keep the valve from twisting on its pipe.".into()));
        args1684.push(Val::Int(153i64));
        fun1686.call(args1684, kw1685)?
    };
    {
        let fun1689 = e.get("para")?;
        let mut args1687 = Vec::new();
        let mut kw1688 = Vec::new();
        args1687.push(Val::Str(
            "Finish unscrewing the nut by hand. Lift the hose away and catch the water left in it."
                .into(),
        ));
        args1687.push(e.get("RIGHT")?);
        args1687.push(Val::Int(319i64));
        args1687.push(e.get("RW")?);
        fun1689.call(args1687, kw1688)?
    };
    {
        let fun1692 = e.get("end")?;
        let mut args1690 = Vec::new();
        let mut kw1691 = Vec::new();
        fun1692.call(args1690, kw1691)?
    };
    {
        let fun1695 = e.get("header")?;
        let mut args1693 = Vec::new();
        let mut kw1694 = Vec::new();
        args1693.push(Val::Str("Fit the white tee".into()));
        args1693.push(Val::Str("INSTALL / BRAIDED-HOSE CONNECTION".into()));
        args1693.push(Val::Int(2i64));
        fun1695.call(args1693, kw1694)?
    };
    {
        let fun1698 = e.get("pic")?;
        let mut args1696 = Vec::new();
        let mut kw1697 = Vec::new();
        args1696.push(Val::Str("tee-after.png".into()));
        args1696.push(e.get("M")?);
        args1696.push(Val::Int(137i64));
        args1696.push(Val::Int(264i64));
        args1696.push(Val::Int(269i64));
        fun1698.call(args1696, kw1697)?
    };
    {
        let fun1701 = e.get("item")?;
        let mut args1699 = Vec::new();
        let mut kw1700 = Vec::new();
        args1699.push(Val::Str("3 / TEE ONTO VALVE".into()));
        args1699.push(Val::Str("Start the lower nut by hand".into()));
        args1699.push(Val::Str(
            "Thread the tee's lower nut onto the shutoff outlet. Keep the valve body steady."
                .into(),
        ));
        args1699.push(Val::Int(144i64));
        fun1701.call(args1699, kw1700)?
    };
    {
        let fun1704 = e.get("item")?;
        let mut args1702 = Vec::new();
        let mut kw1703 = Vec::new();
        args1702.push(Val::Str("4 / HOSE ONTO TEE".into()));
        args1702.push(Val::Str("Reconnect the braided hose".into()));
        args1702.push(Val::Str("Start the hose nut on the tee's top by hand. Hold the tee steady and nip both joints up: snug, then a little more.".into()));
        args1702.push(Val::Int(291i64));
        fun1704.call(args1702, kw1703)?
    };
    {
        let fun1707 = e.get("end")?;
        let mut args1705 = Vec::new();
        let mut kw1706 = Vec::new();
        fun1707.call(args1705, kw1706)?
    };
    {
        let fun1710 = e.get("header")?;
        let mut args1708 = Vec::new();
        let mut kw1709 = Vec::new();
        args1708.push(Val::Str("Move the white filtered run".into()));
        args1708.push(Val::Str("INSTALL / BRAIDED-HOSE CONNECTION".into()));
        args1708.push(Val::Int(2i64));
        fun1710.call(args1708, kw1709)?
    };
    {
        let fun1713 = e.get("pic")?;
        let mut args1711 = Vec::new();
        let mut kw1712 = Vec::new();
        args1711.push(Val::Str("filter-in-cabinet.png".into()));
        args1711.push(e.get("M")?);
        args1711.push(Val::Int(164i64));
        args1711.push(Val::Int(274i64));
        args1711.push(Val::Int(179i64));
        fun1713.call(args1711, kw1712)?
    };
    {
        let fun1716 = e.get("caption")?;
        let mut args1714 = Vec::new();
        let mut kw1715 = Vec::new();
        args1714.push(Val::Str(
            "Keep the filter and its tube collar on the run.".into(),
        ));
        args1714.push(Val::Int(371i64));
        fun1716.call(args1714, kw1715)?
    };
    {
        let fun1719 = e.get("item")?;
        let mut args1717 = Vec::new();
        let mut kw1718 = Vec::new();
        args1717.push(Val::Str("5 / MOVE THE RUN".into()));
        args1717.push(Val::Str("Release it from the black tee".into()));
        args1717.push(Val::Str("Use the collet press on the black tee's branch. Its short jumper and the black tee are not used on this path.".into()));
        args1717.push(Val::Int(146i64));
        fun1719.call(args1717, kw1718)?
    };
    {
        let fun1722 = e.get("para")?;
        let mut args1720 = Vec::new();
        let mut kw1721 = Vec::new();
        args1720.push(Val::Str("Push the filtered white run fully into the white tee's side port, then tug gently. Leave the small side-port lever open.".into()));
        args1720.push(e.get("RIGHT")?);
        args1720.push(Val::Int(294i64));
        args1720.push(e.get("RW")?);
        fun1722.call(args1720, kw1721)?
    };
    {
        let fun1725 = e.get("text")?;
        let mut args1723 = Vec::new();
        let mut kw1724 = Vec::new();
        args1723.push(Val::Str("Keep the main shutoff closed.".into()));
        args1723.push(e.get("RIGHT")?);
        args1723.push(Val::Int(396i64));
        args1723.push(Val::Int(12i64));
        args1723.push(Val::Str("Bold".into()));
        args1723.push(e.get("BLUE")?);
        fun1725.call(args1723, kw1724)?
    };
    {
        let fun1728 = e.get("end")?;
        let mut args1726 = Vec::new();
        let mut kw1727 = Vec::new();
        fun1728.call(args1726, kw1727)?
    };
    {
        let fun1731 = e.get("header")?;
        let mut args1729 = Vec::new();
        let mut kw1730 = Vec::new();
        args1729.push(Val::Str("Match the rear connections".into()));
        args1729.push(Val::Str("INSTALL / MATCH THE REAR CONNECTIONS".into()));
        args1729.push(Val::Int(3i64));
        fun1731.call(args1729, kw1730)?
    };
    let assigned1732 = {
        let fun1735 = e.get("pic")?;
        let mut args1733 = Vec::new();
        let mut kw1734 = Vec::new();
        args1733.push(Val::Str("steps/the-back-face.png".into()));
        args1733.push(e.get("M")?);
        args1733.push(Val::Int(148i64));
        args1733.push(Val::Int(282i64));
        args1733.push(Val::Int(253i64));
        kw1734.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(160i64));
            s.push(Val::Int(20i64));
            s.push(Val::Int(1440i64));
            s.push(Val::Int(1120i64));
            Val::tuple(s)
        }));
        fun1735.call(args1733, kw1734)?
    };
    e.set("p", assigned1732.clone())?;
    {
        let fun1738 = e.get("leader")?;
        let mut args1736 = Vec::new();
        let mut kw1737 = Vec::new();
        args1736.push(Val::Str("DATA / Faucet cable".into()));
        args1736.push(e.get("M")?);
        args1736.push(Val::Int(136i64));
        args1736.push({
            let fun1741 = e.get("p")?;
            let mut args1739 = Vec::new();
            let mut kw1740 = Vec::new();
            args1739.extend(
                e.get("resolutions")?
                    .get(Val::Str("steps/the-back-face.png".into()))?
                    .get(Val::Str("anchors_reference_pixels".into()))?
                    .get(Val::Str("jack-port".into()))?
                    .iter()?,
            );
            fun1741.call(args1739, kw1740)?
        });
        fun1738.call(args1736, kw1737)?
    };
    {
        let fun1744 = e.get("para")?;
        let mut args1742 = Vec::new();
        let mut kw1743 = Vec::new();
        args1742.push(Val::Str("Pull off the <b>CO2 and TAP shipping caps.</b> They cover the fittings; leave the fittings mounted.".into()));
        args1742.push(e.get("RIGHT")?);
        args1742.push(Val::Int(136i64));
        args1742.push(e.get("RW")?);
        args1742.push(Val::Int(12i64));
        args1742.push(Val::Int(17i64));
        kw1743.push(("limit".into(), Val::Int(68i64)));
        fun1744.call(args1742, kw1743)?
    };
    let assigned1745 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("CO2".into()));
            s.push(Val::Str("Top left / red tube from the cylinder".into()));
            s.push(Val::Str("#D7333C".into()));
            s.push(Val::Str("#FFFFFF".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("TAP".into()));
            s.push(Val::Str("Top right / larger white filter tube".into()));
            s.push(Val::Str("#FFFFFF".into()));
            s.push(e.get("INK")?);
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("SODA".into()));
            s.push(Val::Str("Middle left / blue faucet tube".into()));
            s.push(Val::Str("#1670DB".into()));
            s.push(Val::Str("#FFFFFF".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("DRAIN".into()));
            s.push(Val::Str("Bottom left / small white 4 mm tube".into()));
            s.push(Val::Str("#FFFFFF".into()));
            s.push(e.get("INK")?);
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("FLAVOR".into()));
            s.push(Val::Str("Right column / black tubes; either port".into()));
            s.push(e.get("INK")?);
            s.push(Val::Str("#FFFFFF".into()));
            Val::tuple(s)
        });
        Val::list(s)
    };
    e.set("rows", assigned1745.clone())?;
    for item1746 in {
        let fun1761 = e.get("enumerate")?;
        let mut args1759 = Vec::new();
        let mut kw1760 = Vec::new();
        args1759.push(e.get("rows")?);
        fun1761.call(args1759, kw1760)?
    }
    .iter()?
    {
        let unpack1762 = unpack(item1746, 2)?;
        e.set("i", unpack1762[0].clone())?;
        let unpack1763 = unpack(unpack1762[1].clone(), 4)?;
        e.set("name", unpack1763[0].clone())?;
        e.set("desc", unpack1763[1].clone())?;
        e.set("bg", unpack1763[2].clone())?;
        e.set("fg", unpack1763[3].clone())?;
        let assigned1747 = binary(
            "add",
            Val::Int(215i64),
            binary("mul", e.get("i")?, Val::Int(43i64))?,
        )?;
        e.set("y", assigned1747.clone())?;
        {
            let fun1750 = e.get("rect")?;
            let mut args1748 = Vec::new();
            let mut kw1749 = Vec::new();
            args1748.push(e.get("RIGHT")?);
            args1748.push(e.get("y")?);
            args1748.push(Val::Int(71i64));
            args1748.push(Val::Int(23i64));
            args1748.push(e.get("bg")?);
            args1748.push(
                if {
                    let v1751 = e.get("bg")?;
                    let v1752 = Val::Str("#FFFFFF".into());
                    Val::Bool(compare("eq", v1751.clone(), v1752.clone())?.truthy()?)
                }
                .truthy()?
                {
                    e.get("RULE")?
                } else {
                    Val::None
                },
            );
            args1748.push(Val::Int(3i64));
            fun1750.call(args1748, kw1749)?
        };
        {
            let fun1755 = e.get("text")?;
            let mut args1753 = Vec::new();
            let mut kw1754 = Vec::new();
            args1753.push(e.get("name")?);
            args1753.push(binary("add", e.get("RIGHT")?, Val::Int(8i64))?);
            args1753.push(binary("add", e.get("y")?, Val::Int(6i64))?);
            args1753.push(Val::Int(10i64));
            args1753.push(Val::Str("Bold".into()));
            args1753.push(e.get("fg")?);
            fun1755.call(args1753, kw1754)?
        };
        {
            let fun1758 = e.get("text")?;
            let mut args1756 = Vec::new();
            let mut kw1757 = Vec::new();
            args1756.push(e.get("desc")?);
            args1756.push(e.get("RIGHT")?);
            args1756.push(binary("add", e.get("y")?, Val::Int(29i64))?);
            args1756.push(Val::Int(11i64));
            args1756.push(Val::Str("Regular".into()));
            args1756.push(e.get("INK")?);
            fun1758.call(args1756, kw1757)?
        };
    }
    {
        let fun1766 = e.get("end")?;
        let mut args1764 = Vec::new();
        let mut kw1765 = Vec::new();
        fun1766.call(args1764, kw1765)?
    };
    {
        let fun1769 = e.get("header")?;
        let mut args1767 = Vec::new();
        let mut kw1768 = Vec::new();
        args1767.push(Val::Str("Push home. Then tug.".into()));
        args1767.push(Val::Str("INSTALL / MATCH THE REAR CONNECTIONS".into()));
        args1767.push(Val::Int(3i64));
        fun1769.call(args1767, kw1768)?
    };
    {
        let fun1772 = e.get("pic")?;
        let mut args1770 = Vec::new();
        let mut kw1771 = Vec::new();
        args1770.push(Val::Str("steps/connect-rear-open.png".into()));
        args1770.push(e.get("M")?);
        args1770.push(Val::Int(155i64));
        args1770.push(Val::Int(283i64));
        args1770.push(Val::Int(183i64));
        kw1771.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(60i64));
            s.push(Val::Int(160i64));
            s.push(Val::Int(1350i64));
            s.push(Val::Int(880i64));
            Val::tuple(s)
        }));
        fun1772.call(args1770, kw1771)?
    };
    {
        let fun1775 = e.get("caption")?;
        let mut args1773 = Vec::new();
        let mut kw1774 = Vec::new();
        args1773.push(Val::Str(
            "Push straight into the fitting, all the way to its stop.".into(),
        ));
        args1773.push(Val::Int(362i64));
        fun1775.call(args1773, kw1774)?
    };
    {
        let fun1778 = e.get("item")?;
        let mut args1776 = Vec::new();
        let mut kw1777 = Vec::new();
        args1776.push(Val::Str("CHECK EVERY TUBE".into()));
        args1776.push(Val::Str("Push to its stop".into()));
        args1776.push(Val::Str("Match each tube label to its port. A fitting can grip before the tube reaches the seal. Push fully home, then tug gently.".into()));
        args1776.push(Val::Int(144i64));
        fun1778.call(args1776, kw1777)?
    };
    {
        let fun1781 = e.get("para")?;
        let mut args1779 = Vec::new();
        let mut kw1780 = Vec::new();
        args1779.push(Val::Str("<b>Click the faucet cable into DATA.</b><br/><br/>Leave the DRAIN tube at its factory length. Lay the filter flat and route all tails in loose curves, clear of things that slide in and out.".into()));
        args1779.push(e.get("RIGHT")?);
        args1779.push(Val::Int(303i64));
        args1779.push(e.get("RW")?);
        args1779.push(Val::Int(12i64));
        args1779.push(Val::Int(17i64));
        kw1780.push(("limit".into(), Val::Int(136i64)));
        fun1781.call(args1779, kw1780)?
    };
    {
        let fun1784 = e.get("end")?;
        let mut args1782 = Vec::new();
        let mut kw1783 = Vec::new();
        fun1784.call(args1782, kw1783)?
    };
    {
        let fun1787 = e.get("header")?;
        let mut args1785 = Vec::new();
        let mut kw1786 = Vec::new();
        args1785.push(Val::Str("Prepare the CO2 cylinder".into()));
        args1785.push(Val::Str("TURN IT ON / PREPARE THE CYLINDER".into()));
        args1785.push(Val::Int(4i64));
        fun1787.call(args1785, kw1786)?
    };
    {
        let fun1790 = e.get("pic")?;
        let mut args1788 = Vec::new();
        let mut kw1789 = Vec::new();
        args1788.push(Val::Str("steps/co2-ready.png".into()));
        args1788.push(e.get("M")?);
        args1788.push(Val::Int(135i64));
        args1788.push(Val::Int(278i64));
        args1788.push(Val::Int(279i64));
        kw1789.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(0i64));
            s.push(Val::Int(0i64));
            s.push(Val::Int(1560i64));
            s.push(Val::Int(1500i64));
            Val::tuple(s)
        }));
        fun1790.call(args1788, kw1789)?
    };
    {
        let fun1793 = e.get("item")?;
        let mut args1791 = Vec::new();
        let mut kw1792 = Vec::new();
        args1791.push(Val::Str("1 / CYLINDER".into()));
        args1791.push(Val::Str("Stand it upright".into()));
        args1791.push(Val::Str("Use a filled 5 lb cylinder with a CGA-320 connection. Stand it beside the machine with its valve closed.".into()));
        args1791.push(Val::Int(146i64));
        fun1793.call(args1791, kw1792)?
    };
    {
        let fun1796 = e.get("note")?;
        let mut args1794 = Vec::new();
        let mut kw1795 = Vec::new();
        args1794.push(Val::Str("PRESSURE IS ALREADY SET".into()));
        args1794.push(Val::Str("The supplied regulator is set at the factory. Leave its adjusting screw and locknut alone.".into()));
        args1794.push(Val::Int(315i64));
        args1794.push(e.get("RIGHT")?);
        args1794.push(e.get("RW")?);
        fun1796.call(args1794, kw1795)?
    };
    {
        let fun1799 = e.get("end")?;
        let mut args1797 = Vec::new();
        let mut kw1798 = Vec::new();
        fun1799.call(args1797, kw1798)?
    };
    {
        let fun1802 = e.get("header")?;
        let mut args1800 = Vec::new();
        let mut kw1801 = Vec::new();
        args1800.push(Val::Str("Attach the supplied regulator".into()));
        args1800.push(Val::Str("TURN IT ON / PREPARE THE CYLINDER".into()));
        args1800.push(Val::Int(4i64));
        fun1802.call(args1800, kw1801)?
    };
    {
        let fun1805 = e.get("pic")?;
        let mut args1803 = Vec::new();
        let mut kw1804 = Vec::new();
        args1803.push(Val::Str("steps/co2-ready.png".into()));
        args1803.push(e.get("M")?);
        args1803.push(Val::Int(137i64));
        args1803.push(Val::Int(278i64));
        args1803.push(Val::Int(266i64));
        kw1804.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(0i64));
            s.push(Val::Int(0i64));
            s.push(Val::Int(1560i64));
            s.push(Val::Int(1500i64));
            Val::tuple(s)
        }));
        fun1805.call(args1803, kw1804)?
    };
    {
        let fun1808 = e.get("item")?;
        let mut args1806 = Vec::new();
        let mut kw1807 = Vec::new();
        args1806.push(Val::Str("2 / CGA-320 NUT".into()));
        args1806.push(Val::Str("One washer, lying flat".into()));
        args1806.push(Val::Str("Place one supplied nylon washer flat inside the large nut. Start the nut squarely on the closed cylinder outlet by hand.".into()));
        args1806.push(Val::Int(146i64));
        fun1808.call(args1806, kw1807)?
    };
    {
        let fun1811 = e.get("para")?;
        let mut args1809 = Vec::new();
        let mut kw1810 = Vec::new();
        args1809.push(Val::Str(
            "Snug it with the wrench. Extra force can damage the washer.".into(),
        ));
        args1809.push(e.get("RIGHT")?);
        args1809.push(Val::Int(282i64));
        args1809.push(e.get("RW")?);
        args1809.push(Val::Int(12i64));
        args1809.push(Val::Int(17i64));
        kw1810.push(("limit".into(), Val::Int(51i64)));
        fun1811.call(args1809, kw1810)?
    };
    {
        let fun1814 = e.get("note")?;
        let mut args1812 = Vec::new();
        let mut kw1813 = Vec::new();
        args1812.push(Val::Str("REGULATOR + TETHER".into()));
        args1812.push(Val::Str("The outlet adapter and red tether arrive fitted to the regulator. Keep them assembled.".into()));
        args1812.push(Val::Int(341i64));
        args1812.push(e.get("RIGHT")?);
        args1812.push(e.get("RW")?);
        fun1814.call(args1812, kw1813)?
    };
    {
        let fun1817 = e.get("end")?;
        let mut args1815 = Vec::new();
        let mut kw1816 = Vec::new();
        fun1817.call(args1815, kw1816)?
    };
    {
        let fun1820 = e.get("header")?;
        let mut args1818 = Vec::new();
        let mut kw1819 = Vec::new();
        args1818.push(Val::Str("Connect the red tether".into()));
        args1818.push(Val::Str("TURN IT ON / PREPARE THE CYLINDER".into()));
        args1818.push(Val::Int(4i64));
        fun1820.call(args1818, kw1819)?
    };
    let assigned1821 = {
        let fun1824 = e.get("pic")?;
        let mut args1822 = Vec::new();
        let mut kw1823 = Vec::new();
        args1822.push(Val::Str("steps/connect-rear-open.png".into()));
        args1822.push(e.get("M")?);
        args1822.push(Val::Int(156i64));
        args1822.push(Val::Int(278i64));
        args1822.push(Val::Int(230i64));
        kw1823.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(60i64));
            s.push(Val::Int(160i64));
            s.push(Val::Int(1350i64));
            s.push(Val::Int(880i64));
            Val::tuple(s)
        }));
        fun1824.call(args1822, kw1823)?
    };
    e.set("p", assigned1821.clone())?;
    let assigned1825 = e
        .get("resolutions")?
        .get(Val::Str("steps/connect-rear-open.png".into()))?
        .get(Val::Str("anchors_reference_pixels".into()))?;
    e.set("co2_anchors", assigned1825.clone())?;
    {
        let fun1828 = e.get("arrow")?;
        let mut args1826 = Vec::new();
        let mut kw1827 = Vec::new();
        args1826.extend(
            {
                let fun1831 = e.get("p")?;
                let mut args1829 = Vec::new();
                let mut kw1830 = Vec::new();
                args1829.extend(
                    e.get("co2_anchors")?
                        .get(Val::Str("co2-tube".into()))?
                        .iter()?,
                );
                fun1831.call(args1829, kw1830)?
            }
            .iter()?,
        );
        args1826.extend(
            {
                let fun1834 = e.get("p")?;
                let mut args1832 = Vec::new();
                let mut kw1833 = Vec::new();
                args1832.extend(
                    e.get("co2_anchors")?
                        .get(Val::Str("co2-mouth".into()))?
                        .iter()?,
                );
                fun1834.call(args1832, kw1833)?
            }
            .iter()?,
        );
        kw1827.push(("head".into(), Val::Int(10i64)));
        fun1828.call(args1826, kw1827)?
    };
    {
        let fun1837 = e.get("caption")?;
        let mut args1835 = Vec::new();
        let mut kw1836 = Vec::new();
        args1835.push(Val::Str(
            "Keep the regulator end of the tether assembled.".into(),
        ));
        args1835.push(Val::Int(402i64));
        fun1837.call(args1835, kw1836)?
    };
    {
        let fun1840 = e.get("item")?;
        let mut args1838 = Vec::new();
        let mut kw1839 = Vec::new();
        args1838.push(Val::Str("3 / CO2 PORT".into()));
        args1838.push(Val::Str("Red tube to red fitting".into()));
        args1838.push(Val::Str("Push the free end of the red tether into the machine's red CO2 port. Push fully home, then tug gently.".into()));
        args1838.push(Val::Int(153i64));
        fun1840.call(args1838, kw1839)?
    };
    {
        let fun1843 = e.get("note")?;
        let mut args1841 = Vec::new();
        let mut kw1842 = Vec::new();
        args1841.push(Val::Str("KEEP THE CYLINDER CLOSED".into()));
        args1841.push(Val::Str("Finish all connections before opening water or gas. The next pages take you through water, gas and power in that order.".into()));
        args1841.push(Val::Int(319i64));
        args1841.push(e.get("RIGHT")?);
        args1841.push(e.get("RW")?);
        fun1843.call(args1841, kw1842)?
    };
    {
        let fun1846 = e.get("end")?;
        let mut args1844 = Vec::new();
        let mut kw1845 = Vec::new();
        fun1846.call(args1844, kw1845)?
    };
    {
        let fun1849 = e.get("header")?;
        let mut args1847 = Vec::new();
        let mut kw1848 = Vec::new();
        args1847.push(Val::Str("First, open the water".into()));
        args1847.push(Val::Str("TURN IT ON / WATER, GAS, POWER".into()));
        args1847.push(Val::Int(5i64));
        fun1849.call(args1847, kw1848)?
    };
    {
        let fun1852 = e.get("pic")?;
        let mut args1850 = Vec::new();
        let mut kw1851 = Vec::new();
        args1850.push(Val::Str("steps/modern-water-on.png".into()));
        args1850.push(e.get("M")?);
        args1850.push(Val::Int(158i64));
        args1850.push(Val::Int(278i64));
        args1850.push(Val::Int(176i64));
        kw1851.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(170i64));
            s.push(Val::Int(190i64));
            s.push(Val::Int(1100i64));
            s.push(Val::Int(635i64));
            Val::tuple(s)
        }));
        fun1852.call(args1850, kw1851)?
    };
    {
        let fun1855 = e.get("caption")?;
        let mut args1853 = Vec::new();
        let mut kw1854 = Vec::new();
        args1853.push(Val::Str(
            "Plastic-tube valve: its open handle follows the tube.".into(),
        ));
        args1853.push(Val::Int(365i64));
        fun1855.call(args1853, kw1854)?
    };
    {
        let fun1858 = e.get("item")?;
        let mut args1856 = Vec::new();
        let mut kw1857 = Vec::new();
        args1856.push(Val::Str("1 / WATER".into()));
        args1856.push(Val::Str("Open the shutoff slowly".into()));
        args1856.push(Val::Str("On the braided-hose path, check that the white tee's small side-port lever is open too.".into()));
        args1856.push(Val::Int(141i64));
        fun1858.call(args1856, kw1857)?
    };
    {
        let fun1861 = e.get("para")?;
        let mut args1859 = Vec::new();
        let mut kw1860 = Vec::new();
        args1859.push(Val::Str("<b>Watch for a full minute.</b><br/>Inspect the tee, filter ends and TAP connection. Keep power unplugged.".into()));
        args1859.push(e.get("RIGHT")?);
        args1859.push(Val::Int(267i64));
        args1859.push(e.get("RW")?);
        args1859.push(Val::Int(12i64));
        args1859.push(Val::Int(17i64));
        fun1861.call(args1859, kw1860)?
    };
    {
        let fun1864 = e.get("note")?;
        let mut args1862 = Vec::new();
        let mut kw1863 = Vec::new();
        args1862.push(Val::Str("IF YOU SEE WATER".into()));
        args1862.push(Val::Str("Close the shutoff. Resolve the leak before opening gas or connecting power. See page 31.".into()));
        args1862.push(Val::Int(342i64));
        args1862.push(e.get("RIGHT")?);
        args1862.push(e.get("RW")?);
        args1862.push(Val::Str("orange".into()));
        fun1864.call(args1862, kw1863)?
    };
    {
        let fun1867 = e.get("end")?;
        let mut args1865 = Vec::new();
        let mut kw1866 = Vec::new();
        fun1867.call(args1865, kw1866)?
    };
    {
        let fun1870 = e.get("header")?;
        let mut args1868 = Vec::new();
        let mut kw1869 = Vec::new();
        args1868.push(Val::Str("Then, open the gas".into()));
        args1868.push(Val::Str("TURN IT ON / WATER, GAS, POWER".into()));
        args1868.push(Val::Int(5i64));
        fun1870.call(args1868, kw1869)?
    };
    {
        let fun1873 = e.get("pic")?;
        let mut args1871 = Vec::new();
        let mut kw1872 = Vec::new();
        args1871.push(Val::Str("steps/startup-gas.png".into()));
        args1871.push(e.get("M")?);
        args1871.push(Val::Int(138i64));
        args1871.push(Val::Int(278i64));
        args1871.push(Val::Int(269i64));
        fun1873.call(args1871, kw1872)?
    };
    {
        let fun1876 = e.get("item")?;
        let mut args1874 = Vec::new();
        let mut kw1875 = Vec::new();
        args1874.push(Val::Str("2 / GAS".into()));
        args1874.push(Val::Str("Open the valve slowly".into()));
        args1874.push(Val::Str(
            "Pressure is factory set. Leave the screw alone; the upper gauge settles near 75 PSI."
                .into(),
        ));
        args1874.push(Val::Int(144i64));
        kw1875.push(("size".into(), Val::Int(12i64)));
        fun1876.call(args1874, kw1875)?
    };
    {
        let fun1879 = e.get("para")?;
        let mut args1877 = Vec::new();
        let mut kw1878 = Vec::new();
        args1877.push(Val::Str("Listen at the cylinder nut, outlet and red CO2 port. A continuing hiss means a leak. Soapy water shows it as growing bubbles.".into()));
        args1877.push(e.get("RIGHT")?);
        args1877.push(Val::Int(251i64));
        args1877.push(e.get("RW")?);
        args1877.push(Val::Int(12i64));
        args1877.push(Val::Int(17i64));
        kw1878.push(("limit".into(), Val::Int(102i64)));
        fun1879.call(args1877, kw1878)?
    };
    {
        let fun1882 = e.get("note")?;
        let mut args1880 = Vec::new();
        let mut kw1881 = Vec::new();
        args1880.push(Val::Str("BEFORE POWER".into()));
        args1880.push(Val::Str(
            "If gas continues to escape, close the cylinder. Check page 32 and retest.".into(),
        ));
        args1880.push(Val::Int(342i64));
        args1880.push(e.get("RIGHT")?);
        args1880.push(e.get("RW")?);
        args1880.push(Val::Str("orange".into()));
        fun1882.call(args1880, kw1881)?
    };
    {
        let fun1885 = e.get("end")?;
        let mut args1883 = Vec::new();
        let mut kw1884 = Vec::new();
        fun1885.call(args1883, kw1884)?
    };
    {
        let fun1888 = e.get("header")?;
        let mut args1886 = Vec::new();
        let mut kw1887 = Vec::new();
        args1886.push(Val::Str("Finally, connect power".into()));
        args1886.push(Val::Str("TURN IT ON / WATER, GAS, POWER".into()));
        args1886.push(Val::Int(5i64));
        fun1888.call(args1886, kw1887)?
    };
    let assigned1889 = {
        let fun1892 = e.get("pic")?;
        let mut args1890 = Vec::new();
        let mut kw1891 = Vec::new();
        args1890.push(Val::Str("steps/power-ready.png".into()));
        args1890.push(e.get("M")?);
        args1890.push(Val::Int(164i64));
        args1890.push(Val::Int(278i64));
        args1890.push(Val::Int(194i64));
        kw1891.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(0i64));
            s.push(Val::Int(160i64));
            s.push(Val::Int(1800i64));
            s.push(Val::Int(1140i64));
            Val::tuple(s)
        }));
        fun1892.call(args1890, kw1891)?
    };
    e.set("p", assigned1889.clone())?;
    let assigned1893 = e
        .get("resolutions")?
        .get(Val::Str("steps/power-ready.png".into()))?
        .get(Val::Str("anchors_reference_pixels".into()))?;
    e.set("power_anchors", assigned1893.clone())?;
    {
        let fun1896 = e.get("arrow")?;
        let mut args1894 = Vec::new();
        let mut kw1895 = Vec::new();
        args1894.extend(
            {
                let fun1899 = e.get("p")?;
                let mut args1897 = Vec::new();
                let mut kw1898 = Vec::new();
                args1897.extend(
                    e.get("power_anchors")?
                        .get(Val::Str("cord-approach".into()))?
                        .iter()?,
                );
                fun1899.call(args1897, kw1898)?
            }
            .iter()?,
        );
        args1894.extend(
            {
                let fun1902 = e.get("p")?;
                let mut args1900 = Vec::new();
                let mut kw1901 = Vec::new();
                args1900.extend(
                    e.get("power_anchors")?
                        .get(Val::Str("power-mouth".into()))?
                        .iter()?,
                );
                fun1902.call(args1900, kw1901)?
            }
            .iter()?,
        );
        kw1895.push(("head".into(), Val::Int(10i64)));
        fun1896.call(args1894, kw1895)?
    };
    {
        let fun1905 = e.get("item")?;
        let mut args1903 = Vec::new();
        let mut kw1904 = Vec::new();
        args1903.push(Val::Str("3 / POWER".into()));
        args1903.push(Val::Str("Connect the supplied cord".into()));
        args1903.push(Val::Str("Push it straight into the power socket at the upper right of the rear panel. Plug into a grounded 120 V outlet.".into()));
        args1903.push(Val::Int(144i64));
        fun1905.call(args1903, kw1904)?
    };
    {
        let fun1908 = e.get("para")?;
        let mut args1906 = Vec::new();
        let mut kw1907 = Vec::new();
        args1906.push(Val::Str(
            "The machine chimes and its display starts. Follow the display if it reports an issue."
                .into(),
        ));
        args1906.push(e.get("RIGHT")?);
        args1906.push(Val::Int(296i64));
        args1906.push(e.get("RW")?);
        fun1908.call(args1906, kw1907)?
    };
    {
        let fun1911 = e.get("caption")?;
        let mut args1909 = Vec::new();
        let mut kw1910 = Vec::new();
        args1909.push(Val::Str(
            "120 V, 60 Hz; 5 A, 600 W. The inlet's 250 V marking describes the connector.".into(),
        ));
        args1909.push(Val::Int(396i64));
        kw1910.push(("w".into(), e.get("CW")?));
        fun1911.call(args1909, kw1910)?
    };
    {
        let fun1914 = e.get("end")?;
        let mut args1912 = Vec::new();
        let mut kw1913 = Vec::new();
        fun1914.call(args1912, kw1913)?
    };
    {
        let fun1917 = e.get("header")?;
        let mut args1915 = Vec::new();
        let mut kw1916 = Vec::new();
        args1915.push(Val::Str("Choose the flavor to fill".into()));
        args1915.push(Val::Str("YOUR FIRST GLASS / FILL BOTH FLAVORS".into()));
        args1915.push(Val::Int(6i64));
        fun1917.call(args1915, kw1916)?
    };
    {
        let fun1920 = e.get("pic")?;
        let mut args1918 = Vec::new();
        let mut kw1919 = Vec::new();
        args1918.push(Val::Str("fill-screen-framed.png".into()));
        args1918.push(e.get("M")?);
        args1918.push(Val::Int(160i64));
        args1918.push(Val::Int(278i64));
        args1918.push(Val::Int(207i64));
        kw1919.push(("fade_crops".into(), Val::Bool(false)));
        fun1920.call(args1918, kw1919)?
    };
    {
        let fun1923 = e.get("caption")?;
        let mut args1921 = Vec::new();
        let mut kw1922 = Vec::new();
        args1921.push(Val::Str(
            "Flavor 1 is selected. Fill and Start filling are separate controls.".into(),
        ));
        args1921.push(Val::Int(389i64));
        fun1923.call(args1921, kw1922)?
    };
    {
        let fun1926 = e.get("item")?;
        let mut args1924 = Vec::new();
        let mut kw1925 = Vec::new();
        args1924.push(Val::Str("1 / CHOOSE".into()));
        args1924.push(Val::Str("Tap a flavor on the left".into()));
        args1924.push(Val::Str(
            "The large portrait shows the reservoir you selected.".into(),
        ));
        args1924.push(Val::Int(149i64));
        fun1926.call(args1924, kw1925)?
    };
    {
        let fun1929 = e.get("item")?;
        let mut args1927 = Vec::new();
        let mut kw1928 = Vec::new();
        args1927.push(Val::Str("2 / OPEN FILL".into()));
        args1927.push(Val::Str("Tap Fill across the top".into()));
        args1927.push(Val::Str(
            "Leave Start filling alone until the concentrate is in place on the next page.".into(),
        ));
        args1927.push(Val::Int(283i64));
        fun1929.call(args1927, kw1928)?
    };
    {
        let fun1932 = e.get("end")?;
        let mut args1930 = Vec::new();
        let mut kw1931 = Vec::new();
        fun1932.call(args1930, kw1931)?
    };
    {
        let fun1935 = e.get("header")?;
        let mut args1933 = Vec::new();
        let mut kw1934 = Vec::new();
        args1933.push(Val::Str("Bottle first. Then start.".into()));
        args1933.push(Val::Str("YOUR FIRST GLASS / FILL BOTH FLAVORS".into()));
        args1933.push(Val::Int(6i64));
        fun1935.call(args1933, kw1934)?
    };
    let assigned1936 = {
        let fun1939 = e.get("pic")?;
        let mut args1937 = Vec::new();
        let mut kw1938 = Vec::new();
        args1937.push(Val::Str("steps/fill-ready.png".into()));
        args1937.push(e.get("M")?);
        args1937.push(Val::Int(133i64));
        args1937.push(Val::Int(278i64));
        args1937.push(Val::Int(279i64));
        kw1938.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(180i64));
            s.push(Val::Int(480i64));
            s.push(Val::Int(1360i64));
            s.push(Val::Int(1500i64));
            Val::tuple(s)
        }));
        fun1939.call(args1937, kw1938)?
    };
    e.set("p", assigned1936.clone())?;
    {
        let fun1942 = e.get("arrow")?;
        let mut args1940 = Vec::new();
        let mut kw1941 = Vec::new();
        args1940.extend(
            {
                let e = e.child();
                let out1943 = Val::list(vec![]);
                for item1944 in e.get("FILL")?.get(Val::Str("arrow".into()))?.iter()? {
                    e.set("point", item1944)?;
                    for item1945 in {
                        let fun1948 = e.get("projected")?;
                        let mut args1946 = Vec::new();
                        let mut kw1947 = Vec::new();
                        args1946.push(e.get("p")?);
                        args1946.push(e.get("point")?);
                        args1946.extend(e.get("FILL_POSE")?.iter()?);
                        fun1948.call(args1946, kw1947)?
                    }
                    .iter()?
                    {
                        e.set("v", item1945)?;
                        out1943.attr("append")?.call(vec![e.get("v")?], vec![])?;
                    }
                }
                out1943
            }
            .iter()?,
        );
        kw1941.push(("head".into(), Val::Int(10i64)));
        fun1942.call(args1940, kw1941)?
    };
    {
        let fun1951 = e.get("item")?;
        let mut args1949 = Vec::new();
        let mut kw1950 = Vec::new();
        args1949.push(Val::Str("3 / ADD CONCENTRATE".into()));
        args1949.push(Val::Str("Lift off the funnel cover".into()));
        args1949.push(Val::Str("Wipe off water and debris. Lift by the front edge, then tip one whole 14.8&nbsp;fl&nbsp;oz (440&nbsp;mL) bottle just past level over the funnel until it empties.".into()));
        args1949.push(Val::Int(146i64));
        fun1951.call(args1949, kw1950)?
    };
    {
        let fun1954 = e.get("item")?;
        let mut args1952 = Vec::new();
        let mut kw1953 = Vec::new();
        args1952.push(Val::Str("4 / START".into()));
        args1952.push(Val::Str("Tap Start filling".into()));
        args1952.push(Val::Str(
            "Let the machine draw the concentrate into the selected reservoir.".into(),
        ));
        args1952.push(Val::Int(309i64));
        fun1954.call(args1952, kw1953)?
    };
    {
        let fun1957 = e.get("end")?;
        let mut args1955 = Vec::new();
        let mut kw1956 = Vec::new();
        fun1957.call(args1955, kw1956)?
    };
    {
        let fun1960 = e.get("header")?;
        let mut args1958 = Vec::new();
        let mut kw1959 = Vec::new();
        args1958.push(Val::Str("Wait for Filled. Then repeat.".into()));
        args1958.push(Val::Str("YOUR FIRST GLASS / FILL BOTH FLAVORS".into()));
        args1958.push(Val::Int(6i64));
        fun1960.call(args1958, kw1959)?
    };
    {
        let fun1963 = e.get("pic")?;
        let mut args1961 = Vec::new();
        let mut kw1962 = Vec::new();
        args1961.push(Val::Str("steps/fill-closed.png".into()));
        args1961.push(e.get("M")?);
        args1961.push(Val::Int(130i64));
        args1961.push(Val::Int(278i64));
        args1961.push(Val::Int(282i64));
        kw1962.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(180i64));
            s.push(Val::Int(480i64));
            s.push(Val::Int(1360i64));
            s.push(Val::Int(1500i64));
            Val::tuple(s)
        }));
        fun1963.call(args1961, kw1962)?
    };
    {
        let fun1966 = e.get("item")?;
        let mut args1964 = Vec::new();
        let mut kw1965 = Vec::new();
        args1964.push(Val::Str("5 / FILLED".into()));
        args1964.push(Val::Str("Replace the funnel cover".into()));
        args1964.push(Val::Str("When the display says Filled, the concentrate is in the reservoir. Press the cover down until it rests evenly on the brim.".into()));
        args1964.push(Val::Int(145i64));
        fun1966.call(args1964, kw1965)?
    };
    {
        let fun1969 = e.get("item")?;
        let mut args1967 = Vec::new();
        let mut kw1968 = Vec::new();
        args1967.push(Val::Str("6 / OTHER FLAVOR".into()));
        args1967.push(Val::Str("Repeat the same sequence".into()));
        args1967.push(Val::Str("Select the other image, open Fill, lift off the cover, pour in its bottle, then tap Start filling.".into()));
        args1967.push(Val::Int(295i64));
        fun1969.call(args1967, kw1968)?
    };
    {
        let fun1972 = e.get("end")?;
        let mut args1970 = Vec::new();
        let mut kw1971 = Vec::new();
        fun1972.call(args1970, kw1971)?
    };
    {
        let fun1975 = e.get("header")?;
        let mut args1973 = Vec::new();
        let mut kw1974 = Vec::new();
        args1973.push(Val::Str("Allow the first chill".into()));
        args1973.push(Val::Str("YOUR FIRST GLASS".into()));
        args1973.push(Val::Int(7i64));
        fun1975.call(args1973, kw1974)?
    };
    {
        let fun1978 = e.get("pic")?;
        let mut args1976 = Vec::new();
        let mut kw1977 = Vec::new();
        args1976.push(Val::Str("steps/pour-base.png".into()));
        args1976.push(e.get("M")?);
        args1976.push(Val::Int(132i64));
        args1976.push(Val::Int(278i64));
        args1976.push(Val::Int(286i64));
        kw1977.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(150i64));
            s.push(Val::Int(40i64));
            s.push(Val::Int(1475i64));
            s.push(Val::Int(1500i64));
            Val::tuple(s)
        }));
        fun1978.call(args1976, kw1977)?
    };
    {
        let fun1981 = e.get("label")?;
        let mut args1979 = Vec::new();
        let mut kw1980 = Vec::new();
        args1979.push(Val::Str("FIRST CHILL".into()));
        args1979.push(e.get("RIGHT")?);
        args1979.push(Val::Int(152i64));
        fun1981.call(args1979, kw1980)?
    };
    {
        let fun1984 = e.get("text")?;
        let mut args1982 = Vec::new();
        let mut kw1983 = Vec::new();
        args1982.push(Val::Str("About 1 hour".into()));
        args1982.push(e.get("RIGHT")?);
        args1982.push(Val::Int(185i64));
        args1982.push(Val::Int(28i64));
        args1982.push(Val::Str("Bold".into()));
        args1982.push(e.get("NAVY")?);
        fun1984.call(args1982, kw1983)?
    };
    {
        let fun1987 = e.get("para")?;
        let mut args1985 = Vec::new();
        let mut kw1986 = Vec::new();
        args1985.push(Val::Str(
            "Let the machine chill before your first pour.".into(),
        ));
        args1985.push(e.get("RIGHT")?);
        args1985.push(Val::Int(242i64));
        args1985.push(e.get("RW")?);
        args1985.push(Val::Int(15i64));
        args1985.push(Val::Int(21i64));
        fun1987.call(args1985, kw1986)?
    };
    {
        let fun1990 = e.get("note")?;
        let mut args1988 = Vec::new();
        let mut kw1989 = Vec::new();
        args1988.push(Val::Str("READY FOR YOUR GLASS".into()));
        args1988.push(Val::Str("Keep the water and cylinder supplies open. Choose your flavor at the faucet when you are ready to pour.".into()));
        args1988.push(Val::Int(330i64));
        args1988.push(e.get("RIGHT")?);
        args1988.push(e.get("RW")?);
        fun1990.call(args1988, kw1989)?
    };
    {
        let fun1993 = e.get("end")?;
        let mut args1991 = Vec::new();
        let mut kw1992 = Vec::new();
        fun1993.call(args1991, kw1992)?
    };
    {
        let fun1996 = e.get("header")?;
        let mut args1994 = Vec::new();
        let mut kw1995 = Vec::new();
        args1994.push(Val::Str("Choose. Ice. Pour.".into()));
        args1994.push(Val::Str("YOUR FIRST GLASS".into()));
        args1994.push(Val::Int(7i64));
        fun1996.call(args1994, kw1995)?
    };
    let assigned1997 = {
        let fun2000 = e.get("pic")?;
        let mut args1998 = Vec::new();
        let mut kw1999 = Vec::new();
        args1998.push(Val::Str("steps/pour-base.png".into()));
        args1998.push(e.get("M")?);
        args1998.push(Val::Int(131i64));
        args1998.push(Val::Int(278i64));
        args1998.push(Val::Int(283i64));
        kw1999.push(("crop".into(), {
            let mut s = Vec::new();
            s.push(Val::Int(150i64));
            s.push(Val::Int(40i64));
            s.push(Val::Int(1475i64));
            s.push(Val::Int(1500i64));
            Val::tuple(s)
        }));
        fun2000.call(args1998, kw1999)?
    };
    e.set("p", assigned1997.clone())?;
    let assigned2001 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(1i64));
            s.push(unary("neg", Val::Float(1.8f64))?);
            s.push(Val::Float(0.67f64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(0i64));
            s.push(unary("neg", Val::Int(78i64))?);
            s.push(Val::Int(119i64));
            Val::tuple(s)
        });
        s.push(Val::Int(140i64));
        Val::tuple(s)
    };
    e.set("pose", assigned2001.clone())?;
    let assigned2002 = {
        let fun2005 = e.get("projected")?;
        let mut args2003 = Vec::new();
        let mut kw2004 = Vec::new();
        args2003.push(e.get("p")?);
        args2003.push({
            let mut s = Vec::new();
            s.push(Val::Int(0i64));
            s.push(unary("neg", Val::Float(134.243f64))?);
            s.push(Val::Float(211.599f64));
            Val::tuple(s)
        });
        args2003.extend(e.get("pose")?.iter()?);
        fun2005.call(args2003, kw2004)?
    };
    e.set("tap", assigned2002.clone())?;
    {
        let fun2008 = e.get("leader")?;
        let mut args2006 = Vec::new();
        let mut kw2007 = Vec::new();
        args2006.push(Val::Str("Tap screen".into()));
        args2006.push(e.get("M")?);
        args2006.push(Val::Int(157i64));
        args2006.push(e.get("tap")?);
        fun2008.call(args2006, kw2007)?
    };
    let assigned2009 = {
        let fun2012 = e.get("projected")?;
        let mut args2010 = Vec::new();
        let mut kw2011 = Vec::new();
        args2010.push(e.get("p")?);
        args2010.push({
            let mut s = Vec::new();
            s.push(Val::Int(0i64));
            s.push(unary("neg", Val::Int(38i64))?);
            s.push(Val::Int(39i64));
            Val::tuple(s)
        });
        args2010.extend(e.get("pose")?.iter()?);
        fun2012.call(args2010, kw2011)?
    };
    e.set("press", assigned2009.clone())?;
    {
        let fun2015 = e.get("arrow")?;
        let mut args2013 = Vec::new();
        let mut kw2014 = Vec::new();
        args2013.push(e.get("press")?.get(Val::Int(0i64))?);
        args2013.push(binary(
            "sub",
            e.get("press")?.get(Val::Int(1i64))?,
            Val::Int(26i64),
        )?);
        args2013.push(e.get("press")?.get(Val::Int(0i64))?);
        args2013.push(binary(
            "sub",
            e.get("press")?.get(Val::Int(1i64))?,
            Val::Int(2i64),
        )?);
        kw2014.push(("head".into(), Val::Int(9i64)));
        fun2015.call(args2013, kw2014)?
    };
    {
        let fun2018 = e.get("item")?;
        let mut args2016 = Vec::new();
        let mut kw2017 = Vec::new();
        args2016.push(Val::Str("1 / CHOOSE".into()));
        args2016.push(Val::Str("Tap the faucet display".into()));
        args2016.push(Val::Str(
            "Select a flavor. If the display is dim, the first tap wakes it.".into(),
        ));
        args2016.push(Val::Int(143i64));
        fun2018.call(args2016, kw2017)?
    };
    {
        let fun2021 = e.get("item")?;
        let mut args2019 = Vec::new();
        let mut kw2020 = Vec::new();
        args2019.push(Val::Str("2 / POUR".into()));
        args2019.push(Val::Str("Fill your glass with ice".into()));
        args2019.push(Val::Str(
            "Put it under the faucet and press the lever down. Release the lever to stop.".into(),
        ));
        args2019.push(Val::Int(284i64));
        fun2021.call(args2019, kw2020)?
    };
    {
        let fun2024 = e.get("end")?;
        let mut args2022 = Vec::new();
        let mut kw2023 = Vec::new();
        fun2024.call(args2022, kw2023)?
    };
    {
        let fun2027 = e.get("header")?;
        let mut args2025 = Vec::new();
        let mut kw2026 = Vec::new();
        args2025.push(Val::Str("Keep it ready".into()));
        args2025.push(Val::Str("AFTER INSTALLATION".into()));
        fun2027.call(args2025, kw2026)?
    };
    {
        let fun2030 = e.get("text")?;
        let mut args2028 = Vec::new();
        let mut kw2029 = Vec::new();
        args2028.push(Val::Str("Top up a flavor".into()));
        args2028.push(e.get("M")?);
        args2028.push(Val::Int(148i64));
        args2028.push(Val::Int(17i64));
        args2028.push(Val::Str("Bold".into()));
        args2028.push(e.get("NAVY")?);
        fun2030.call(args2028, kw2029)?
    };
    {
        let fun2033 = e.get("para")?;
        let mut args2031 = Vec::new();
        let mut kw2032 = Vec::new();
        args2031.push(Val::Str("Use the Fill sequence on pages 25-27. If the display says <b>Full</b>, concentrate remains in the funnel. Add no more and replace the cover.".into()));
        args2031.push(e.get("M")?);
        args2031.push(Val::Int(180i64));
        args2031.push(Val::Int(263i64));
        args2031.push(Val::Int(12i64));
        args2031.push(Val::Int(17i64));
        kw2032.push(("limit".into(), Val::Int(102i64)));
        fun2033.call(args2031, kw2032)?
    };
    {
        let fun2036 = e.get("text")?;
        let mut args2034 = Vec::new();
        let mut kw2035 = Vec::new();
        args2034.push(Val::Str("Change a flavor".into()));
        args2034.push(e.get("M")?);
        args2034.push(Val::Int(280i64));
        args2034.push(Val::Int(17i64));
        args2034.push(Val::Str("Bold".into()));
        args2034.push(e.get("NAVY")?);
        fun2036.call(args2034, kw2035)?
    };
    {
        let fun2039 = e.get("para")?;
        let mut args2037 = Vec::new();
        let mut kw2038 = Vec::new();
        args2037.push(Val::Str("Fill the funnel with water first. Then select the old flavor, open Clean and tap Start cleaning; the water rinses the line below the funnel. When it finishes, fill the new flavor.".into()));
        args2037.push(e.get("M")?);
        args2037.push(Val::Int(312i64));
        args2037.push(Val::Int(263i64));
        args2037.push(Val::Int(12i64));
        args2037.push(Val::Int(17i64));
        kw2038.push(("limit".into(), Val::Int(68i64)));
        fun2039.call(args2037, kw2038)?
    };
    {
        let fun2042 = e.get("text")?;
        let mut args2040 = Vec::new();
        let mut kw2041 = Vec::new();
        args2040.push(Val::Str("Rinse the funnel".into()));
        args2040.push(e.get("RIGHT")?);
        args2040.push(Val::Int(148i64));
        args2040.push(Val::Int(17i64));
        args2040.push(Val::Str("Bold".into()));
        args2040.push(e.get("NAVY")?);
        fun2042.call(args2040, kw2041)?
    };
    {
        let fun2045 = e.get("para")?;
        let mut args2043 = Vec::new();
        let mut kw2044 = Vec::new();
        args2043.push(Val::Str("Rinse weekly and after changing flavors. Wash the removable silicone funnel and both faces of its cover by hand.".into()));
        args2043.push(e.get("RIGHT")?);
        args2043.push(Val::Int(180i64));
        args2043.push(e.get("RW")?);
        args2043.push(Val::Int(12i64));
        args2043.push(Val::Int(17i64));
        kw2044.push(("limit".into(), Val::Int(51i64)));
        fun2045.call(args2043, kw2044)?
    };
    {
        let fun2048 = e.get("para")?;
        let mut args2046 = Vec::new();
        let mut kw2047 = Vec::new();
        args2046.push(Val::Str("Wipe the cover and lift it by its front edge. When the funnel is empty, lift it straight out. Its plug slides off the drain tube; the tube stays in the machine.".into()));
        args2046.push(e.get("RIGHT")?);
        args2046.push(Val::Int(246i64));
        args2046.push(e.get("RW")?);
        args2046.push(Val::Int(12i64));
        args2046.push(Val::Int(17i64));
        kw2047.push(("limit".into(), Val::Int(68i64)));
        fun2048.call(args2046, kw2047)?
    };
    {
        let fun2051 = e.get("para")?;
        let mut args2049 = Vec::new();
        let mut kw2050 = Vec::new();
        args2049.push(Val::Str("To refit, align the plug in its socket and press down until the brim seats. Press the cover evenly onto the brim.".into()));
        args2049.push(e.get("RIGHT")?);
        args2049.push(Val::Int(329i64));
        args2049.push(e.get("RW")?);
        args2049.push(Val::Int(12i64));
        args2049.push(Val::Int(17i64));
        kw2050.push(("limit".into(), Val::Int(51i64)));
        fun2051.call(args2049, kw2050)?
    };
    {
        let fun2054 = e.get("caption")?;
        let mut args2052 = Vec::new();
        let mut kw2053 = Vec::new();
        args2052.push(Val::Str("Filter: replace yearly; relieve the white line's pressure as on page 31 first. Cylinder: refill when its left gauge reaches the red band. Keep the spare nylon washer for the refill.".into()));
        args2052.push(Val::Int(402i64));
        kw2053.push(("w".into(), e.get("CW")?));
        fun2054.call(args2052, kw2053)?
    };
    {
        let fun2057 = e.get("end")?;
        let mut args2055 = Vec::new();
        let mut kw2056 = Vec::new();
        fun2057.call(args2055, kw2056)?
    };
    {
        let fun2060 = e.get("header")?;
        let mut args2058 = Vec::new();
        let mut kw2059 = Vec::new();
        args2058.push(Val::Str("Check a leaking water connection".into()));
        args2058.push(Val::Str("FIRST CHECKS".into()));
        fun2060.call(args2058, kw2059)?
    };
    {
        let fun2063 = e.get("note")?;
        let mut args2061 = Vec::new();
        let mut kw2062 = Vec::new();
        args2061.push(Val::Str("FIRST, CLOSE THE SUPPLIES".into()));
        args2061.push(Val::Str("Close the water shutoff and cylinder valve. Unplug the machine. Leave pressurized connections assembled.".into()));
        args2061.push(Val::Int(139i64));
        fun2063.call(args2061, kw2062)?
    };
    {
        let fun2066 = e.get("text")?;
        let mut args2064 = Vec::new();
        let mut kw2065 = Vec::new();
        args2064.push(Val::Str("White TAP line".into()));
        args2064.push(e.get("M")?);
        args2064.push(Val::Int(260i64));
        args2064.push(Val::Int(17i64));
        args2064.push(Val::Str("Bold".into()));
        args2064.push(e.get("NAVY")?);
        fun2066.call(args2064, kw2065)?
    };
    {
        let fun2069 = e.get("para")?;
        let mut args2067 = Vec::new();
        let mut kw2068 = Vec::new();
        args2067.push(Val::Str("Run the tap or dispenser on that same cold-water line until flow stops. Keep the white tee's side lever open, if used.".into()));
        args2067.push(e.get("M")?);
        args2067.push(Val::Int(292i64));
        args2067.push(Val::Int(263i64));
        args2067.push(Val::Int(12i64));
        args2067.push(Val::Int(17i64));
        kw2068.push(("limit".into(), Val::Int(85i64)));
        fun2069.call(args2067, kw2068)?
    };
    {
        let fun2072 = e.get("text")?;
        let mut args2070 = Vec::new();
        let mut kw2071 = Vec::new();
        args2070.push(Val::Str("Blue SODA line".into()));
        args2070.push(e.get("M")?);
        args2070.push(Val::Int(365i64));
        args2070.push(Val::Int(17i64));
        args2070.push(Val::Str("Bold".into()));
        args2070.push(e.get("NAVY")?);
        fun2072.call(args2070, kw2071)?
    };
    {
        let fun2075 = e.get("para")?;
        let mut args2073 = Vec::new();
        let mut kw2074 = Vec::new();
        args2073.push(Val::Str(
            "Press the soda lever over a jug until water and hissing stop.".into(),
        ));
        args2073.push(e.get("M")?);
        args2073.push(Val::Int(397i64));
        args2073.push(Val::Int(263i64));
        args2073.push(Val::Int(12i64));
        args2073.push(Val::Int(17i64));
        kw2074.push(("limit".into(), Val::Int(34i64)));
        fun2075.call(args2073, kw2074)?
    };
    {
        let fun2078 = e.get("text")?;
        let mut args2076 = Vec::new();
        let mut kw2077 = Vec::new();
        args2076.push(Val::Str("After pressure is released".into()));
        args2076.push(e.get("RIGHT")?);
        args2076.push(Val::Int(260i64));
        args2076.push(Val::Int(17i64));
        args2076.push(Val::Str("Bold".into()));
        args2076.push(e.get("NAVY")?);
        fun2078.call(args2076, kw2077)?
    };
    {
        let fun2081 = e.get("para")?;
        let mut args2079 = Vec::new();
        let mut kw2080 = Vec::new();
        args2079.push(Val::Str("Hold the release ring in with the collet press. Pull out the tube and check for dirt or damage. Push an undamaged tube fully to its internal stop, then tug gently.".into()));
        args2079.push(e.get("RIGHT")?);
        args2079.push(Val::Int(292i64));
        args2079.push(e.get("RW")?);
        args2079.push(Val::Int(12i64));
        args2079.push(Val::Int(17i64));
        kw2080.push(("limit".into(), Val::Int(119i64)));
        fun2081.call(args2079, kw2080)?
    };
    {
        let fun2084 = e.get("end")?;
        let mut args2082 = Vec::new();
        let mut kw2083 = Vec::new();
        fun2084.call(args2082, kw2083)?
    };
    {
        let fun2087 = e.get("header")?;
        let mut args2085 = Vec::new();
        let mut kw2086 = Vec::new();
        args2085.push(Val::Str("Gas and first-pour checks".into()));
        args2085.push(Val::Str("FIRST CHECKS".into()));
        fun2087.call(args2085, kw2086)?
    };
    {
        let fun2090 = e.get("text")?;
        let mut args2088 = Vec::new();
        let mut kw2089 = Vec::new();
        args2088.push(Val::Str("Gas at a connection".into()));
        args2088.push(e.get("M")?);
        args2088.push(Val::Int(145i64));
        args2088.push(Val::Int(17i64));
        args2088.push(Val::Str("Bold".into()));
        args2088.push(e.get("NAVY")?);
        fun2090.call(args2088, kw2089)?
    };
    {
        let fun2093 = e.get("para")?;
        let mut args2091 = Vec::new();
        let mut kw2092 = Vec::new();
        args2091.push(Val::Str(
            "Close the cylinder valve. Growing bubbles in soapy water locate a leaking joint."
                .into(),
        ));
        args2091.push(e.get("M")?);
        args2091.push(Val::Int(180i64));
        args2091.push(Val::Int(263i64));
        args2091.push(Val::Int(12i64));
        args2091.push(Val::Int(16i64));
        kw2092.push(("limit".into(), Val::Int(48i64)));
        fun2093.call(args2091, kw2092)?
    };
    {
        let fun2096 = e.get("para")?;
        let mut args2094 = Vec::new();
        let mut kw2095 = Vec::new();
        args2094.push(Val::Str("<b>Leave the regulator and red tether assembled until depressurized.</b> Do not loosen a fitting to let pressure out.".into()));
        args2094.push(e.get("M")?);
        args2094.push(Val::Int(244i64));
        args2094.push(Val::Int(263i64));
        args2094.push(Val::Int(12i64));
        args2094.push(Val::Int(16i64));
        kw2095.push(("limit".into(), Val::Int(64i64)));
        fun2096.call(args2094, kw2095)?
    };
    {
        let fun2099 = e.get("para")?;
        let mut args2097 = Vec::new();
        let mut kw2098 = Vec::new();
        args2097.push(Val::Str("Then check the nut's flat nylon washer and fully seat both red-tube ends. See pages 20-21.".into()));
        args2097.push(e.get("M")?);
        args2097.push(Val::Int(322i64));
        args2097.push(Val::Int(263i64));
        args2097.push(Val::Int(12i64));
        args2097.push(Val::Int(16i64));
        kw2098.push(("limit".into(), Val::Int(64i64)));
        fun2099.call(args2097, kw2098)?
    };
    {
        let fun2102 = e.get("para")?;
        let mut args2100 = Vec::new();
        let mut kw2101 = Vec::new();
        args2100.push(Val::Str(
            "After repair, repeat the water and gas checks on pages 22-23 before connecting power."
                .into(),
        ));
        args2100.push(e.get("M")?);
        args2100.push(Val::Int(393i64));
        args2100.push(Val::Int(263i64));
        args2100.push(Val::Int(12i64));
        args2100.push(Val::Int(16i64));
        kw2101.push(("limit".into(), Val::Int(48i64)));
        fun2102.call(args2100, kw2101)?
    };
    for item2103 in {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(145i64));
            s.push(Val::Str("No pour".into()));
            s.push(Val::Str(
                "Check the water shutoff and the white tee's side-port lever.".into(),
            ));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(242i64));
            s.push(Val::Str("No power".into()));
            s.push(Val::Str(
                "Check the cord and outlet, then read any display message.".into(),
            ));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(339i64));
            s.push(Val::Str("Warm pour".into()));
            s.push(Val::Str("Allow about an hour for the first chill.".into()));
            Val::tuple(s)
        });
        Val::list(s)
    }
    .iter()?
    {
        let unpack2110 = unpack(item2103, 3)?;
        e.set("y", unpack2110[0].clone())?;
        e.set("title", unpack2110[1].clone())?;
        e.set("s", unpack2110[2].clone())?;
        {
            let fun2106 = e.get("text")?;
            let mut args2104 = Vec::new();
            let mut kw2105 = Vec::new();
            args2104.push(e.get("title")?);
            args2104.push(e.get("RIGHT")?);
            args2104.push(e.get("y")?);
            args2104.push(Val::Int(17i64));
            args2104.push(Val::Str("Bold".into()));
            args2104.push(e.get("NAVY")?);
            fun2106.call(args2104, kw2105)?
        };
        {
            let fun2109 = e.get("para")?;
            let mut args2107 = Vec::new();
            let mut kw2108 = Vec::new();
            args2107.push(e.get("s")?);
            args2107.push(e.get("RIGHT")?);
            args2107.push(binary("add", e.get("y")?, Val::Int(32i64))?);
            args2107.push(e.get("RW")?);
            args2107.push(Val::Int(12i64));
            args2107.push(Val::Int(17i64));
            kw2108.push(("limit".into(), Val::Int(51i64)));
            fun2109.call(args2107, kw2108)?
        };
    }
    {
        let fun2113 = e.get("end")?;
        let mut args2111 = Vec::new();
        let mut kw2112 = Vec::new();
        fun2113.call(args2111, kw2112)?
    };
    {
        let fun2116 = e.get("back_cover")?;
        let mut args2114 = Vec::new();
        let mut kw2115 = Vec::new();
        fun2116.call(args2114, kw2115)?
    };
    {
        let fun2119 = e.get("c")?.attr("save")?;
        let mut args2117 = Vec::new();
        let mut kw2118 = Vec::new();
        fun2119.call(args2117, kw2118)?
    };
    if !{
        let v2120 = e.get("page_no")?;
        let v2121 = Val::Int(34i64);
        Val::Bool(compare("eq", v2120.clone(), v2121.clone())?.truthy()?)
    }
    .truthy()?
    {
        anyhow::bail!("{}", val_string(Val::Str("assertion failed".into()))?);
    }
    if e.get("contours")?.attr("pending")?.truthy()? {
        {
            let fun2124 = e.get("contours")?.attr("render")?;
            let mut args2122 = Vec::new();
            let mut kw2123 = Vec::new();
            fun2124.call(args2122, kw2123)?
        };
        {
            let fun2127 = e.get("subprocess")?.attr("run")?;
            let mut args2125 = Vec::new();
            let mut kw2126 = Vec::new();
            args2125.push({
                let mut s = Vec::new();
                s.push(e.get("sys")?.attr("executable")?);
                s.push({
                    let fun2130 = e.get("str")?;
                    let mut args2128 = Vec::new();
                    let mut kw2129 = Vec::new();
                    args2128.push({
                        let fun2133 = {
                            let fun2136 = e.get("Path")?;
                            let mut args2134 = Vec::new();
                            let mut kw2135 = Vec::new();
                            args2134.push(e.get("__file__")?);
                            fun2136.call(args2134, kw2135)?
                        }
                        .attr("resolve")?;
                        let mut args2131 = Vec::new();
                        let mut kw2132 = Vec::new();
                        fun2133.call(args2131, kw2132)?
                    });
                    fun2130.call(args2128, kw2129)?
                });
                Val::list(s)
            });
            kw2126.push(("cwd".into(), e.get("ROOT")?));
            kw2126.push(("check".into(), Val::Bool(true)));
            fun2127.call(args2125, kw2126)?
        };
        {
            let fun2139 = e.get("sys")?.attr("exit")?;
            let mut args2137 = Vec::new();
            let mut kw2138 = Vec::new();
            args2137.push(Val::Int(0i64));
            fun2139.call(args2137, kw2138)?
        };
    }
    {
        let fun2142 = e.get("OUT")?.attr("mkdir")?;
        let mut args2140 = Vec::new();
        let mut kw2141 = Vec::new();
        kw2141.push(("parents".into(), Val::Bool(true)));
        kw2141.push(("exist_ok".into(), Val::Bool(true)));
        fun2142.call(args2140, kw2141)?
    };
    {
        let fun2145 = e.get("write_editions")?;
        let mut args2143 = Vec::new();
        let mut kw2144 = Vec::new();
        args2143.push({
            let fun2148 = e.get("buffer")?.attr("getvalue")?;
            let mut args2146 = Vec::new();
            let mut kw2147 = Vec::new();
            fun2148.call(args2146, kw2147)?
        });
        args2143.push(e.get("PDF")?);
        args2143.push(e.get("PRESS_DIR")?);
        args2143.push(e.get("OUTPUT")?);
        args2143.push(e.get("OUT")?);
        fun2145.call(args2143, kw2144)?
    };
    {
        let fun2151 = e.get("subprocess")?.attr("run")?;
        let mut args2149 = Vec::new();
        let mut kw2150 = Vec::new();
        args2149.push({
            let mut s = Vec::new();
            s.push(Val::Str("pdftoppm".into()));
            s.push(Val::Str("-f".into()));
            s.push(Val::Str("1".into()));
            s.push(Val::Str("-l".into()));
            s.push(Val::Str("1".into()));
            s.push(Val::Str("-scale-to".into()));
            s.push(Val::Str("1200".into()));
            s.push(Val::Str("-singlefile".into()));
            s.push(Val::Str("-png".into()));
            s.push({
                let fun2154 = e.get("str")?;
                let mut args2152 = Vec::new();
                let mut kw2153 = Vec::new();
                args2152.push(e.get("PDF")?);
                fun2154.call(args2152, kw2153)?
            });
            s.push({
                let fun2157 = e.get("str")?;
                let mut args2155 = Vec::new();
                let mut kw2156 = Vec::new();
                args2155.push(binary("truediv", e.get("OUT")?, Val::Str("cover".into()))?);
                fun2157.call(args2155, kw2156)?
            });
            Val::list(s)
        });
        kw2150.push(("check".into(), Val::Bool(true)));
        fun2151.call(args2149, kw2150)?
    };
    let assigned2158 = {
        let fun2161 = e.get("Image")?.attr("open")?;
        let mut args2159 = Vec::new();
        let mut kw2160 = Vec::new();
        args2159.push(binary(
            "truediv",
            e.get("OUT")?,
            Val::Str("cover.png".into()),
        )?);
        fun2161.call(args2159, kw2160)?
    };
    e.set("im", assigned2158.clone())?;
    {
        let fun2164 = e.get("im")?.attr("thumbnail")?;
        let mut args2162 = Vec::new();
        let mut kw2163 = Vec::new();
        args2162.push({
            let mut s = Vec::new();
            s.push(Val::Int(1200i64));
            s.push(Val::Int(1200i64));
            Val::tuple(s)
        });
        fun2164.call(args2162, kw2163)?
    };
    {
        let fun2167 = e.get("im")?.attr("save")?;
        let mut args2165 = Vec::new();
        let mut kw2166 = Vec::new();
        args2165.push(binary(
            "truediv",
            e.get("DOC_OUTPUT")?,
            Val::Str("install-guide.cover.png".into()),
        )?);
        fun2167.call(args2165, kw2166)?
    };
    {
        let fun2170 = binary(
            "truediv",
            e.get("DOC_OUTPUT")?,
            Val::Str("install-guide.pdf.json".into()),
        )?
        .attr("write_text")?;
        let mut args2168 = Vec::new();
        let mut kw2169 = Vec::new();
        args2168.push(binary("add",{let fun2173=e.get("json")?.attr("dumps")?;let mut args2171=Vec::new();let mut kw2172=Vec::new();args2171.push({let fun2176=e.get("dict")?;let mut args2174=Vec::new();let mut kw2175=Vec::new();kw2175.push(("title".into(),Val::Str("Home Soda Machine install guide".into())));kw2175.push(("subtitle".into(),Val::Str("Owner install guide - seven steps in detail - 32 interior pages, 9 x 7 in landscape".into())));kw2175.push(("pages".into(),Val::Int(34i64)));kw2175.push(("interior_pages".into(),Val::Int(32i64)));kw2175.push(("cover".into(),Val::Str("install-guide.cover.png".into())));kw2175.push(("cover_size".into(),{let fun2179=e.get("list")?;let mut args2177=Vec::new();let mut kw2178=Vec::new();args2177.push(e.get("im")?.attr("size")?);fun2179.call(args2177,kw2178)?}));fun2176.call(args2174,kw2175)?});kw2172.push(("indent".into(),Val::Int(2i64)));fun2173.call(args2171,kw2172)?},Val::Str("\n".into()))?);
        fun2170.call(args2168, kw2169)?
    };
    {
        let fun2182 = binary(
            "truediv",
            e.get("OUT")?,
            Val::Str("layout-checks.json".into()),
        )?
        .attr("write_text")?;
        let mut args2180 = Vec::new();
        let mut kw2181 = Vec::new();
        args2180.push(binary(
            "add",
            {
                let fun2185 = e.get("json")?.attr("dumps")?;
                let mut args2183 = Vec::new();
                let mut kw2184 = Vec::new();
                args2183.push(e.get("checks")?);
                kw2184.push(("indent".into(), Val::Int(2i64)));
                fun2185.call(args2183, kw2184)?
            },
            Val::Str("\n".into()),
        )?);
        fun2182.call(args2180, kw2181)?
    };
    {
        let fun2188 = binary(
            "truediv",
            e.get("OUT")?,
            Val::Str("image-checks.json".into()),
        )?
        .attr("write_text")?;
        let mut args2186 = Vec::new();
        let mut kw2187 = Vec::new();
        args2186.push(binary(
            "add",
            {
                let fun2191 = e.get("json")?.attr("dumps")?;
                let mut args2189 = Vec::new();
                let mut kw2190 = Vec::new();
                args2189.push(e.get("image_checks")?);
                kw2190.push(("indent".into(), Val::Int(2i64)));
                fun2191.call(args2189, kw2190)?
            },
            Val::Str("\n".into()),
        )?);
        fun2188.call(args2186, kw2187)?
    };
    {
        let fun2194 = binary(
            "truediv",
            e.get("OUT")?,
            Val::Str("mount-slot-checks.json".into()),
        )?
        .attr("write_text")?;
        let mut args2192 = Vec::new();
        let mut kw2193 = Vec::new();
        args2192.push(binary(
            "add",
            {
                let fun2197 = e.get("json")?.attr("dumps")?;
                let mut args2195 = Vec::new();
                let mut kw2196 = Vec::new();
                args2195.push(e.get("mount_slot_checks")?);
                kw2196.push(("indent".into(), Val::Int(2i64)));
                fun2197.call(args2195, kw2196)?
            },
            Val::Str("\n".into()),
        )?);
        fun2194.call(args2192, kw2193)?
    };
    {
        let fun2200 = binary("truediv", e.get("OUT")?, Val::Str("page-plan.json".into()))?
            .attr("write_text")?;
        let mut args2198 = Vec::new();
        let mut kw2199 = Vec::new();
        args2198.push(binary(
            "add",
            {
                let fun2203 = e.get("json")?.attr("dumps")?;
                let mut args2201 = Vec::new();
                let mut kw2202 = Vec::new();
                args2201.push({
                    let fun2206 = e.get("dict")?;
                    let mut args2204 = Vec::new();
                    let mut kw2205 = Vec::new();
                    kw2205.push(("interior_pages".into(), Val::Int(32i64)));
                    kw2205.push(("titles".into(), e.get("titles")?));
                    fun2206.call(args2204, kw2205)?
                });
                kw2202.push(("indent".into(), Val::Int(2i64)));
                fun2203.call(args2201, kw2202)?
            },
            Val::Str("\n".into()),
        )?);
        fun2200.call(args2198, kw2199)?
    };
    {
        let fun2209 = e.get("print")?;
        let mut args2207 = Vec::new();
        let mut kw2208 = Vec::new();
        args2207.push({
            let mut str2210 = String::new();
            str2210.push_str(&format(&e.get("PDF")?, &String::new())?);
            str2210.push_str(": 32 interior pages + covers, ");
            str2210.push_str(&format(
                &binary(
                    "floordiv",
                    {
                        let fun2213 = e.get("PDF")?.attr("stat")?;
                        let mut args2211 = Vec::new();
                        let mut kw2212 = Vec::new();
                        fun2213.call(args2211, kw2212)?
                    }
                    .attr("st_size")?,
                    Val::Int(1024i64),
                )?,
                &String::new(),
            )?);
            str2210.push_str(" KB");
            Val::Str(str2210)
        });
        fun2209.call(args2207, kw2208)?
    };
    {
        let fun2216 = e.get("make_order_bundle")?;
        let mut args2214 = Vec::new();
        let mut kw2215 = Vec::new();
        args2214.push(e.get("PRESS_DIR")?);
        args2214.push(e.get("OUTPUT")?);
        fun2216.call(args2214, kw2215)?
    };
    Ok(Val::None)
}
