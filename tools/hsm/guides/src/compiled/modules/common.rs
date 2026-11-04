//! Guide recipe: `tools/assembly-guides/common.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("hashlib", rt.import_module("hashlib")?)?;
    e.set("json", rt.import_module("json")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("shutil", rt.import_module("shutil")?)?;
    e.set("subprocess", rt.import_module("subprocess")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let mod2 = rt.import_module("reportlab.lib.colors")?;
    e.set("HexColor", rt.member("reportlab.lib.colors", "HexColor")?)?;
    let mod3 = rt.import_module("reportlab.lib.styles")?;
    e.set(
        "ParagraphStyle",
        rt.member("reportlab.lib.styles", "ParagraphStyle")?,
    )?;
    let mod4 = rt.import_module("reportlab.pdfbase")?;
    e.set("pdfmetrics", rt.member("reportlab.pdfbase", "pdfmetrics")?)?;
    let mod5 = rt.import_module("reportlab.pdfbase.ttfonts")?;
    e.set("TTFont", rt.member("reportlab.pdfbase.ttfonts", "TTFont")?)?;
    let mod6 = rt.import_module("reportlab.pdfgen")?;
    e.set("canvas", rt.member("reportlab.pdfgen", "canvas")?)?;
    let mod7 = rt.import_module("reportlab.platypus")?;
    e.set("Paragraph", rt.member("reportlab.platypus", "Paragraph")?)?;
    let assigned8 = {
        let fun11 = {
            let fun14 = e.get("Path")?;
            let mut args12 = Vec::new();
            let mut kw13 = Vec::new();
            args12.push(e.get("__file__")?);
            fun14.call(args12, kw13)?
        }
        .attr("resolve")?;
        let mut args9 = Vec::new();
        let mut kw10 = Vec::new();
        fun11.call(args9, kw10)?
    }
    .attr("parents")?
    .get(Val::Int(2i64))?;
    e.set("ROOT", assigned8.clone())?;
    let assigned15 = {
        let mut s = Vec::new();
        s.push(Val::Int(612i64));
        s.push(Val::Int(792i64));
        Val::tuple(s)
    };
    let unpack16 = unpack(assigned15.clone(), 2)?;
    e.set("W", unpack16[0].clone())?;
    e.set("H", unpack16[1].clone())?;
    let assigned17 = Val::Float(0.98f64);
    e.set("CONTENT_SCALE", assigned17.clone())?;
    let assigned18 = Val::Int(18i64);
    e.set("BLEED_OVERHANG", assigned18.clone())?;
    let assigned19 = Val::Int(24i64);
    e.set("BAND_INSET", assigned19.clone())?;
    let assigned20 = {
        let mut s = Vec::new();
        s.push(Val::Str("#202337".into()));
        s.push(Val::Str("#1749D1".into()));
        s.push(Val::Str("#E95A2C".into()));
        Val::tuple(s)
    };
    let unpack21 = unpack(assigned20.clone(), 3)?;
    e.set("INK", unpack21[0].clone())?;
    e.set("BLUE", unpack21[1].clone())?;
    e.set("ORANGE", unpack21[2].clone())?;
    let assigned22 = {
        let mut s = Vec::new();
        s.push(Val::Str("#FCFCFA".into()));
        s.push(Val::Str("#EAF0FC".into()));
        s.push(Val::Str("#E4E8EE".into()));
        Val::tuple(s)
    };
    let unpack23 = unpack(assigned22.clone(), 3)?;
    e.set("PAPER", unpack23[0].clone())?;
    e.set("ICE", unpack23[1].clone())?;
    e.set("STEEL", unpack23[2].clone())?;
    let assigned24 = {
        let mut s = Vec::new();
        s.push(Val::Str("#606A78".into()));
        s.push(Val::Str("#DCE2EB".into()));
        s.push(Val::Str("#B8722C".into()));
        s.push(Val::Str("#ECD5AA".into()));
        Val::tuple(s)
    };
    let unpack25 = unpack(assigned24.clone(), 4)?;
    e.set("MUTED", unpack25[0].clone())?;
    e.set("RULE", unpack25[1].clone())?;
    e.set("COPPER", unpack25[2].clone())?;
    e.set("GLOVE", unpack25[3].clone())?;
    let assigned26 = binary(
        "truediv",
        e.get("ROOT")?,
        Val::Str("hardware/install-guide/fonts".into()),
    )?;
    e.set("FONT_DIR", assigned26.clone())?;
    for item27 in {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("Plex".into()));
            s.push(Val::Str("Plex-Regular.ttf".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("PlexSemi".into()));
            s.push(Val::Str("Plex-Semibold.ttf".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("PlexBold".into()));
            s.push(Val::Str("Plex-Bold.ttf".into()));
            Val::tuple(s)
        });
        Val::list(s)
    }
    .iter()?
    {
        let unpack37 = unpack(item27, 2)?;
        e.set("face_name", unpack37[0].clone())?;
        e.set("filename", unpack37[1].clone())?;
        {
            let fun30 = e.get("pdfmetrics")?.attr("registerFont")?;
            let mut args28 = Vec::new();
            let mut kw29 = Vec::new();
            args28.push({
                let fun33 = e.get("TTFont")?;
                let mut args31 = Vec::new();
                let mut kw32 = Vec::new();
                args31.push(e.get("face_name")?);
                args31.push({
                    let fun36 = e.get("str")?;
                    let mut args34 = Vec::new();
                    let mut kw35 = Vec::new();
                    args34.push(binary("truediv", e.get("FONT_DIR")?, e.get("filename")?)?);
                    fun36.call(args34, kw35)?
                });
                fun33.call(args31, kw32)?
            });
            fun30.call(args28, kw29)?
        };
    }
    {
        let fun40 = e.get("pdfmetrics")?.attr("registerFontFamily")?;
        let mut args38 = Vec::new();
        let mut kw39 = Vec::new();
        args38.push(Val::Str("Plex".into()));
        kw39.push(("normal".into(), Val::Str("Plex".into())));
        kw39.push(("bold".into(), Val::Str("PlexBold".into())));
        kw39.push(("italic".into(), Val::Str("Plex".into())));
        kw39.push(("boldItalic".into(), Val::Str("PlexBold".into())));
        fun40.call(args38, kw39)?
    };
    // color
    e.set("color", {
        let params = vec![("value".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun43 = e.get("HexColor")?;
                let mut args41 = Vec::new();
                let mut kw42 = Vec::new();
                args41.push(e.get("value")?);
                fun43.call(args41, kw42)?
            });
            Ok(Val::None)
        })
    })?;
    // box
    e.set("box", {
        let params = vec![
            ("c".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("width".into(), None, false),
            ("height".into(), None, false),
            ("fill".into(), Some(e.get("PAPER")?), false),
            ("stroke".into(), Some(Val::None), false),
            ("radius".into(), Some(Val::Int(0i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun46 = e.get("c")?.attr("setFillColor")?;
                let mut args44 = Vec::new();
                let mut kw45 = Vec::new();
                args44.push({
                    let fun49 = e.get("color")?;
                    let mut args47 = Vec::new();
                    let mut kw48 = Vec::new();
                    args47.push(e.get("fill")?);
                    fun49.call(args47, kw48)?
                });
                fun46.call(args44, kw45)?
            };
            {
                let fun52 = e.get("c")?.attr("setStrokeColor")?;
                let mut args50 = Vec::new();
                let mut kw51 = Vec::new();
                args50.push({
                    let fun55 = e.get("color")?;
                    let mut args53 = Vec::new();
                    let mut kw54 = Vec::new();
                    args53.push({
                        let v56 = e.get("stroke")?;
                        if v56.truthy()? { v56 } else { e.get("fill")? }
                    });
                    fun55.call(args53, kw54)?
                });
                fun52.call(args50, kw51)?
            };
            {
                let fun59 = e.get("c")?.attr("setLineWidth")?;
                let mut args57 = Vec::new();
                let mut kw58 = Vec::new();
                args57.push(Val::Float(0.7f64));
                fun59.call(args57, kw58)?
            };
            if e.get("radius")?.truthy()? {
                {
                    let fun62 = e.get("c")?.attr("roundRect")?;
                    let mut args60 = Vec::new();
                    let mut kw61 = Vec::new();
                    args60.push(e.get("x")?);
                    args60.push(binary(
                        "sub",
                        binary("sub", e.get("H")?, e.get("y")?)?,
                        e.get("height")?,
                    )?);
                    args60.push(e.get("width")?);
                    args60.push(e.get("height")?);
                    args60.push(e.get("radius")?);
                    kw61.push(("fill".into(), Val::Int(1i64)));
                    kw61.push(("stroke".into(), {
                        let fun65 = e.get("bool")?;
                        let mut args63 = Vec::new();
                        let mut kw64 = Vec::new();
                        args63.push(e.get("stroke")?);
                        fun65.call(args63, kw64)?
                    }));
                    fun62.call(args60, kw61)?
                };
            } else {
                {
                    let fun68 = e.get("c")?.attr("rect")?;
                    let mut args66 = Vec::new();
                    let mut kw67 = Vec::new();
                    args66.push(e.get("x")?);
                    args66.push(binary(
                        "sub",
                        binary("sub", e.get("H")?, e.get("y")?)?,
                        e.get("height")?,
                    )?);
                    args66.push(e.get("width")?);
                    args66.push(e.get("height")?);
                    kw67.push(("fill".into(), Val::Int(1i64)));
                    kw67.push(("stroke".into(), {
                        let fun71 = e.get("bool")?;
                        let mut args69 = Vec::new();
                        let mut kw70 = Vec::new();
                        args69.push(e.get("stroke")?);
                        fun71.call(args69, kw70)?
                    }));
                    fun68.call(args66, kw67)?
                };
            }
            Ok(Val::None)
        })
    })?;
    // text
    e.set("text", {
        let params = vec![
            ("c".into(), None, false),
            ("value".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("size".into(), Some(Val::Int(12i64)), false),
            ("font".into(), Some(Val::Str("Plex".into())), false),
            ("fill".into(), Some(e.get("INK")?), false),
            ("align".into(), Some(Val::Str("left".into())), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun74 = e.get("c")?.attr("setFont")?;
                let mut args72 = Vec::new();
                let mut kw73 = Vec::new();
                args72.push(e.get("font")?);
                args72.push(e.get("size")?);
                fun74.call(args72, kw73)?
            };
            {
                let fun77 = e.get("c")?.attr("setFillColor")?;
                let mut args75 = Vec::new();
                let mut kw76 = Vec::new();
                args75.push({
                    let fun80 = e.get("color")?;
                    let mut args78 = Vec::new();
                    let mut kw79 = Vec::new();
                    args78.push(e.get("fill")?);
                    fun80.call(args78, kw79)?
                });
                fun77.call(args75, kw76)?
            };
            {
                let fun83 = {
                    let fun86 = e.get("getattr")?;
                    let mut args84 = Vec::new();
                    let mut kw85 = Vec::new();
                    args84.push(e.get("c")?);
                    args84.push(
                        {
                            let d = Val::dict(vec![]);
                            d.set(Val::Str("left".into()), Val::Str("drawString".into()))?;
                            d.set(
                                Val::Str("center".into()),
                                Val::Str("drawCentredString".into()),
                            )?;
                            d.set(Val::Str("right".into()), Val::Str("drawRightString".into()))?;
                            d
                        }
                        .get(e.get("align")?)?,
                    );
                    fun86.call(args84, kw85)?
                };
                let mut args81 = Vec::new();
                let mut kw82 = Vec::new();
                args81.push(e.get("x")?);
                args81.push(binary("sub", e.get("H")?, e.get("y")?)?);
                args81.push(e.get("value")?);
                fun83.call(args81, kw82)?
            };
            Ok(Val::None)
        })
    })?;
    // paragraph
    e.set("paragraph", {
        let params = vec![
            ("c".into(), None, false),
            ("value".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("width".into(), None, false),
            ("size".into(), Some(Val::Float(11.4f64)), false),
            ("leading".into(), Some(Val::None), false),
            ("fill".into(), Some(e.get("INK")?), false),
            ("max_height".into(), Some(Val::None), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned87 = {
                let fun90 = e.get("ParagraphStyle")?;
                let mut args88 = Vec::new();
                let mut kw89 = Vec::new();
                args88.push(Val::Str("copy".into()));
                kw89.push(("fontName".into(), Val::Str("Plex".into())));
                kw89.push(("fontSize".into(), e.get("size")?));
                kw89.push(("leading".into(), {
                    let v91 = e.get("leading")?;
                    if v91.truthy()? {
                        v91
                    } else {
                        binary("mul", e.get("size")?, Val::Float(1.22f64))?
                    }
                }));
                kw89.push(("textColor".into(), {
                    let fun94 = e.get("color")?;
                    let mut args92 = Vec::new();
                    let mut kw93 = Vec::new();
                    args92.push(e.get("fill")?);
                    fun94.call(args92, kw93)?
                }));
                fun90.call(args88, kw89)?
            };
            e.set("style", assigned87.clone())?;
            let assigned95 = {
                let fun98 = e.get("Paragraph")?;
                let mut args96 = Vec::new();
                let mut kw97 = Vec::new();
                args96.push(e.get("value")?);
                args96.push(e.get("style")?);
                fun98.call(args96, kw97)?
            };
            e.set("p", assigned95.clone())?;
            let assigned99 = {
                let fun102 = e.get("p")?.attr("wrap")?;
                let mut args100 = Vec::new();
                let mut kw101 = Vec::new();
                args100.push(e.get("width")?);
                args100.push(e.get("H")?);
                fun102.call(args100, kw101)?
            };
            let unpack103 = unpack(assigned99.clone(), 2)?;
            e.set("_", unpack103[0].clone())?;
            e.set("height", unpack103[1].clone())?;
            if {
                let v106 = e.get("max_height")?;
                if v106.truthy()? {
                    {
                        let v104 = e.get("height")?;
                        let v105 = e.get("max_height")?;
                        Val::Bool(compare("gt", v104.clone(), v105.clone())?.truthy()?)
                    }
                } else {
                    v106
                }
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun109 = e.get("ValueError")?;
                        let mut args107 = Vec::new();
                        let mut kw108 = Vec::new();
                        args107.push({
                            let mut str110 = String::new();
                            str110.push_str("Text exceeds its box: ");
                            str110.push_str(&format(&e.get("value")?, &String::new())?);
                            Val::Str(str110)
                        });
                        fun109.call(args107, kw108)?
                    })?
                );
            }
            {
                let fun113 = e.get("p")?.attr("drawOn")?;
                let mut args111 = Vec::new();
                let mut kw112 = Vec::new();
                args111.push(e.get("c")?);
                args111.push(e.get("x")?);
                args111.push(binary(
                    "sub",
                    binary("sub", e.get("H")?, e.get("y")?)?,
                    e.get("height")?,
                )?);
                fun113.call(args111, kw112)?
            };
            return Ok(e.get("height")?);
            Ok(Val::None)
        })
    })?;
    e.set("Art.__init__", {
        let params = vec![
            ("self".into(), None, false),
            ("c".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("scale".into(), Some(Val::Int(1i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned114 = {
                let mut s = Vec::new();
                s.push(e.get("c")?);
                s.push(e.get("x")?);
                s.push(e.get("y")?);
                s.push(e.get("scale")?);
                Val::tuple(s)
            };
            let unpack115 = unpack(assigned114.clone(), 4)?;
            e.get("self")?.setattr("c", unpack115[0].clone())?;
            e.get("self")?.setattr("x", unpack115[1].clone())?;
            e.get("self")?.setattr("y", unpack115[2].clone())?;
            e.get("self")?.setattr("scale", unpack115[3].clone())?;
            Ok(Val::None)
        })
    })?;
    e.set("Art.__enter__", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun118 = e.get("self")?.attr("c")?.attr("saveState")?;
                let mut args116 = Vec::new();
                let mut kw117 = Vec::new();
                fun118.call(args116, kw117)?
            };
            {
                let fun121 = e.get("self")?.attr("c")?.attr("translate")?;
                let mut args119 = Vec::new();
                let mut kw120 = Vec::new();
                args119.push(e.get("self")?.attr("x")?);
                args119.push(binary("sub", e.get("H")?, e.get("self")?.attr("y")?)?);
                fun121.call(args119, kw120)?
            };
            {
                let fun124 = e.get("self")?.attr("c")?.attr("scale")?;
                let mut args122 = Vec::new();
                let mut kw123 = Vec::new();
                args122.push(e.get("self")?.attr("scale")?);
                args122.push(unary("neg", e.get("self")?.attr("scale")?)?);
                fun124.call(args122, kw123)?
            };
            {
                let fun127 = e.get("self")?.attr("c")?.attr("setLineCap")?;
                let mut args125 = Vec::new();
                let mut kw126 = Vec::new();
                args125.push(Val::Int(1i64));
                fun127.call(args125, kw126)?
            };
            {
                let fun130 = e.get("self")?.attr("c")?.attr("setLineJoin")?;
                let mut args128 = Vec::new();
                let mut kw129 = Vec::new();
                args128.push(Val::Int(1i64));
                fun130.call(args128, kw129)?
            };
            return Ok(e.get("self")?);
            Ok(Val::None)
        })
    })?;
    e.set("Art.__exit__", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, Some("exc"), None)?;
            let _frame = rt.frame(&outer);
            {
                let fun133 = e.get("self")?.attr("c")?.attr("restoreState")?;
                let mut args131 = Vec::new();
                let mut kw132 = Vec::new();
                fun133.call(args131, kw132)?
            };
            Ok(Val::None)
        })
    })?;
    e.set("Art.shape", {
        let params = vec![
            ("self".into(), None, false),
            ("points".into(), None, false),
            ("fill".into(), Some(Val::None), false),
            ("stroke".into(), Some(e.get("INK")?), false),
            ("width".into(), Some(Val::Float(1.5f64)), false),
            ("close".into(), Some(Val::Bool(true)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned134 = e.get("self")?.attr("c")?;
            e.set("c", assigned134.clone())?;
            let assigned135 = {
                let fun138 = e.get("c")?.attr("beginPath")?;
                let mut args136 = Vec::new();
                let mut kw137 = Vec::new();
                fun138.call(args136, kw137)?
            };
            e.set("p", assigned135.clone())?;
            {
                let fun141 = e.get("p")?.attr("moveTo")?;
                let mut args139 = Vec::new();
                let mut kw140 = Vec::new();
                args139.extend(e.get("points")?.get(Val::Int(0i64))?.iter()?);
                fun141.call(args139, kw140)?
            };
            for item142 in e
                .get("points")?
                .get(Val::Slice {
                    start: Some(Val::Int(1i64).integer()?),
                    stop: None,
                    step: 1,
                })?
                .iter()?
            {
                e.set("point", item142)?;
                if {
                    let v146 = {
                        let fun145 = e.get("len")?;
                        let mut args143 = Vec::new();
                        let mut kw144 = Vec::new();
                        args143.push(e.get("point")?);
                        fun145.call(args143, kw144)?
                    };
                    let v147 = Val::Int(2i64);
                    Val::Bool(compare("eq", v146.clone(), v147.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun150 = e.get("p")?.attr("lineTo")?;
                        let mut args148 = Vec::new();
                        let mut kw149 = Vec::new();
                        args148.extend(e.get("point")?.iter()?);
                        fun150.call(args148, kw149)?
                    };
                } else {
                    {
                        let fun153 = e.get("p")?.attr("curveTo")?;
                        let mut args151 = Vec::new();
                        let mut kw152 = Vec::new();
                        args151.extend(e.get("point")?.iter()?);
                        fun153.call(args151, kw152)?
                    };
                }
            }
            if e.get("close")?.truthy()? {
                {
                    let fun156 = e.get("p")?.attr("close")?;
                    let mut args154 = Vec::new();
                    let mut kw155 = Vec::new();
                    fun156.call(args154, kw155)?
                };
            }
            {
                let fun159 = e.get("c")?.attr("setStrokeColor")?;
                let mut args157 = Vec::new();
                let mut kw158 = Vec::new();
                args157.push({
                    let fun162 = e.get("color")?;
                    let mut args160 = Vec::new();
                    let mut kw161 = Vec::new();
                    args160.push({
                        let v163 = e.get("stroke")?;
                        if v163.truthy()? { v163 } else { e.get("fill")? }
                    });
                    fun162.call(args160, kw161)?
                });
                fun159.call(args157, kw158)?
            };
            {
                let fun166 = e.get("c")?.attr("setFillColor")?;
                let mut args164 = Vec::new();
                let mut kw165 = Vec::new();
                args164.push({
                    let fun169 = e.get("color")?;
                    let mut args167 = Vec::new();
                    let mut kw168 = Vec::new();
                    args167.push({
                        let v170 = e.get("fill")?;
                        if v170.truthy()? {
                            v170
                        } else {
                            e.get("PAPER")?
                        }
                    });
                    fun169.call(args167, kw168)?
                });
                fun166.call(args164, kw165)?
            };
            {
                let fun173 = e.get("c")?.attr("setLineWidth")?;
                let mut args171 = Vec::new();
                let mut kw172 = Vec::new();
                args171.push(e.get("width")?);
                fun173.call(args171, kw172)?
            };
            {
                let fun176 = e.get("c")?.attr("drawPath")?;
                let mut args174 = Vec::new();
                let mut kw175 = Vec::new();
                args174.push(e.get("p")?);
                kw175.push(("fill".into(), {
                    let fun179 = e.get("bool")?;
                    let mut args177 = Vec::new();
                    let mut kw178 = Vec::new();
                    args177.push(e.get("fill")?);
                    fun179.call(args177, kw178)?
                }));
                kw175.push(("stroke".into(), {
                    let fun182 = e.get("bool")?;
                    let mut args180 = Vec::new();
                    let mut kw181 = Vec::new();
                    args180.push(e.get("stroke")?);
                    fun182.call(args180, kw181)?
                }));
                fun176.call(args174, kw175)?
            };
            Ok(Val::None)
        })
    })?;
    e.set("Art.line", {
        let params = vec![
            ("self".into(), None, false),
            ("x1".into(), None, false),
            ("y1".into(), None, false),
            ("x2".into(), None, false),
            ("y2".into(), None, false),
            ("fill".into(), Some(e.get("INK")?), false),
            ("width".into(), Some(Val::Float(1.4f64)), false),
            ("dash".into(), Some(Val::None), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned183 = e.get("self")?.attr("c")?;
            e.set("c", assigned183.clone())?;
            {
                let fun186 = e.get("c")?.attr("setStrokeColor")?;
                let mut args184 = Vec::new();
                let mut kw185 = Vec::new();
                args184.push({
                    let fun189 = e.get("color")?;
                    let mut args187 = Vec::new();
                    let mut kw188 = Vec::new();
                    args187.push(e.get("fill")?);
                    fun189.call(args187, kw188)?
                });
                fun186.call(args184, kw185)?
            };
            {
                let fun192 = e.get("c")?.attr("setLineWidth")?;
                let mut args190 = Vec::new();
                let mut kw191 = Vec::new();
                args190.push(e.get("width")?);
                fun192.call(args190, kw191)?
            };
            {
                let fun195 = e.get("c")?.attr("setDash")?;
                let mut args193 = Vec::new();
                let mut kw194 = Vec::new();
                args193.push({
                    let v196 = e.get("dash")?;
                    if v196.truthy()? {
                        v196
                    } else {
                        {
                            let mut s = Vec::new();
                            Val::list(s)
                        }
                    }
                });
                fun195.call(args193, kw194)?
            };
            {
                let fun199 = e.get("c")?.attr("line")?;
                let mut args197 = Vec::new();
                let mut kw198 = Vec::new();
                args197.push(e.get("x1")?);
                args197.push(e.get("y1")?);
                args197.push(e.get("x2")?);
                args197.push(e.get("y2")?);
                fun199.call(args197, kw198)?
            };
            {
                let fun202 = e.get("c")?.attr("setDash")?;
                let mut args200 = Vec::new();
                let mut kw201 = Vec::new();
                args200.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                fun202.call(args200, kw201)?
            };
            Ok(Val::None)
        })
    })?;
    e.set("Art.rect", {
        let params = vec![
            ("self".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("width".into(), None, false),
            ("height".into(), None, false),
            ("fill".into(), Some(e.get("STEEL")?), false),
            ("stroke".into(), Some(e.get("INK")?), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun205 = e.get("self")?.attr("shape")?;
                let mut args203 = Vec::new();
                let mut kw204 = Vec::new();
                args203.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("add", e.get("x")?, e.get("width")?)?);
                        s.push(e.get("y")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("add", e.get("x")?, e.get("width")?)?);
                        s.push(binary("add", e.get("y")?, e.get("height")?)?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(binary("add", e.get("y")?, e.get("height")?)?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args203.push(e.get("fill")?);
                args203.push(e.get("stroke")?);
                fun205.call(args203, kw204)?
            };
            Ok(Val::None)
        })
    })?;
    e.set("Art.ellipse", {
        let params = vec![
            ("self".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("width".into(), None, false),
            ("height".into(), None, false),
            ("fill".into(), Some(e.get("STEEL")?), false),
            ("stroke".into(), Some(e.get("INK")?), false),
            ("lw".into(), Some(Val::Float(1.5f64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned206 = e.get("self")?.attr("c")?;
            e.set("c", assigned206.clone())?;
            {
                let fun209 = e.get("c")?.attr("setFillColor")?;
                let mut args207 = Vec::new();
                let mut kw208 = Vec::new();
                args207.push({
                    let fun212 = e.get("color")?;
                    let mut args210 = Vec::new();
                    let mut kw211 = Vec::new();
                    args210.push({
                        let v213 = e.get("fill")?;
                        if v213.truthy()? {
                            v213
                        } else {
                            e.get("PAPER")?
                        }
                    });
                    fun212.call(args210, kw211)?
                });
                fun209.call(args207, kw208)?
            };
            {
                let fun216 = e.get("c")?.attr("setStrokeColor")?;
                let mut args214 = Vec::new();
                let mut kw215 = Vec::new();
                args214.push({
                    let fun219 = e.get("color")?;
                    let mut args217 = Vec::new();
                    let mut kw218 = Vec::new();
                    args217.push({
                        let v220 = e.get("stroke")?;
                        if v220.truthy()? { v220 } else { e.get("fill")? }
                    });
                    fun219.call(args217, kw218)?
                });
                fun216.call(args214, kw215)?
            };
            {
                let fun223 = e.get("c")?.attr("setLineWidth")?;
                let mut args221 = Vec::new();
                let mut kw222 = Vec::new();
                args221.push(e.get("lw")?);
                fun223.call(args221, kw222)?
            };
            {
                let fun226 = e.get("c")?.attr("ellipse")?;
                let mut args224 = Vec::new();
                let mut kw225 = Vec::new();
                args224.push(e.get("x")?);
                args224.push(e.get("y")?);
                args224.push(binary("add", e.get("x")?, e.get("width")?)?);
                args224.push(binary("add", e.get("y")?, e.get("height")?)?);
                kw225.push(("fill".into(), {
                    let fun229 = e.get("bool")?;
                    let mut args227 = Vec::new();
                    let mut kw228 = Vec::new();
                    args227.push(e.get("fill")?);
                    fun229.call(args227, kw228)?
                }));
                kw225.push(("stroke".into(), {
                    let fun232 = e.get("bool")?;
                    let mut args230 = Vec::new();
                    let mut kw231 = Vec::new();
                    args230.push(e.get("stroke")?);
                    fun232.call(args230, kw231)?
                }));
                fun226.call(args224, kw225)?
            };
            Ok(Val::None)
        })
    })?;
    e.set("Art.label", {
        let params = vec![
            ("self".into(), None, false),
            ("value".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("size".into(), Some(Val::Int(10i64)), false),
            ("fill".into(), Some(e.get("INK")?), false),
            ("font".into(), Some(Val::Str("PlexSemi".into())), false),
            ("align".into(), Some(Val::Str("left".into())), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned233 = e.get("self")?.attr("c")?;
            e.set("c", assigned233.clone())?;
            {
                let fun236 = e.get("c")?.attr("saveState")?;
                let mut args234 = Vec::new();
                let mut kw235 = Vec::new();
                fun236.call(args234, kw235)?
            };
            {
                let fun239 = e.get("c")?.attr("scale")?;
                let mut args237 = Vec::new();
                let mut kw238 = Vec::new();
                args237.push(Val::Int(1i64));
                args237.push(unary("neg", Val::Int(1i64))?);
                fun239.call(args237, kw238)?
            };
            {
                let fun242 = e.get("c")?.attr("setFont")?;
                let mut args240 = Vec::new();
                let mut kw241 = Vec::new();
                args240.push(e.get("font")?);
                args240.push(e.get("size")?);
                fun242.call(args240, kw241)?
            };
            {
                let fun245 = e.get("c")?.attr("setFillColor")?;
                let mut args243 = Vec::new();
                let mut kw244 = Vec::new();
                args243.push({
                    let fun248 = e.get("color")?;
                    let mut args246 = Vec::new();
                    let mut kw247 = Vec::new();
                    args246.push(e.get("fill")?);
                    fun248.call(args246, kw247)?
                });
                fun245.call(args243, kw244)?
            };
            {
                let fun251 = {
                    let fun254 = e.get("getattr")?;
                    let mut args252 = Vec::new();
                    let mut kw253 = Vec::new();
                    args252.push(e.get("c")?);
                    args252.push(
                        {
                            let d = Val::dict(vec![]);
                            d.set(Val::Str("left".into()), Val::Str("drawString".into()))?;
                            d.set(
                                Val::Str("center".into()),
                                Val::Str("drawCentredString".into()),
                            )?;
                            d.set(Val::Str("right".into()), Val::Str("drawRightString".into()))?;
                            d
                        }
                        .get(e.get("align")?)?,
                    );
                    fun254.call(args252, kw253)?
                };
                let mut args249 = Vec::new();
                let mut kw250 = Vec::new();
                args249.push(e.get("x")?);
                args249.push(unary("neg", e.get("y")?)?);
                args249.push(e.get("value")?);
                fun251.call(args249, kw250)?
            };
            {
                let fun257 = e.get("c")?.attr("restoreState")?;
                let mut args255 = Vec::new();
                let mut kw256 = Vec::new();
                fun257.call(args255, kw256)?
            };
            Ok(Val::None)
        })
    })?;
    e.set("Art.arrow", {
        let params = vec![
            ("self".into(), None, false),
            ("x1".into(), None, false),
            ("y1".into(), None, false),
            ("x2".into(), None, false),
            ("y2".into(), None, false),
            ("fill".into(), Some(e.get("BLUE")?), false),
            ("width".into(), Some(Val::Int(2i64)), false),
            ("head".into(), Some(Val::Int(6i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun260 = e.get("self")?.attr("line")?;
                let mut args258 = Vec::new();
                let mut kw259 = Vec::new();
                args258.push(e.get("x1")?);
                args258.push(e.get("y1")?);
                args258.push(e.get("x2")?);
                args258.push(e.get("y2")?);
                args258.push(e.get("fill")?);
                args258.push(e.get("width")?);
                fun260.call(args258, kw259)?
            };
            let assigned261 = {
                let fun264 = e.get("math")?.attr("atan2")?;
                let mut args262 = Vec::new();
                let mut kw263 = Vec::new();
                args262.push(binary("sub", e.get("y2")?, e.get("y1")?)?);
                args262.push(binary("sub", e.get("x2")?, e.get("x1")?)?);
                fun264.call(args262, kw263)?
            };
            e.set("angle", assigned261.clone())?;
            {
                let fun267 = e.get("self")?.attr("shape")?;
                let mut args265 = Vec::new();
                let mut kw266 = Vec::new();
                args265.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("x2")?);
                        s.push(e.get("y2")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "sub",
                            e.get("x2")?,
                            binary("mul", e.get("head")?, {
                                let fun270 = e.get("math")?.attr("cos")?;
                                let mut args268 = Vec::new();
                                let mut kw269 = Vec::new();
                                args268.push(binary("sub", e.get("angle")?, Val::Float(0.5f64))?);
                                fun270.call(args268, kw269)?
                            })?,
                        )?);
                        s.push(binary(
                            "sub",
                            e.get("y2")?,
                            binary("mul", e.get("head")?, {
                                let fun273 = e.get("math")?.attr("sin")?;
                                let mut args271 = Vec::new();
                                let mut kw272 = Vec::new();
                                args271.push(binary("sub", e.get("angle")?, Val::Float(0.5f64))?);
                                fun273.call(args271, kw272)?
                            })?,
                        )?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "sub",
                            e.get("x2")?,
                            binary("mul", e.get("head")?, {
                                let fun276 = e.get("math")?.attr("cos")?;
                                let mut args274 = Vec::new();
                                let mut kw275 = Vec::new();
                                args274.push(binary("add", e.get("angle")?, Val::Float(0.5f64))?);
                                fun276.call(args274, kw275)?
                            })?,
                        )?);
                        s.push(binary(
                            "sub",
                            e.get("y2")?,
                            binary("mul", e.get("head")?, {
                                let fun279 = e.get("math")?.attr("sin")?;
                                let mut args277 = Vec::new();
                                let mut kw278 = Vec::new();
                                args277.push(binary("add", e.get("angle")?, Val::Float(0.5f64))?);
                                fun279.call(args277, kw278)?
                            })?,
                        )?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args265.push(e.get("fill")?);
                args265.push(Val::None);
                fun267.call(args265, kw266)?
            };
            Ok(Val::None)
        })
    })?;
    e.set("Art.dim", {
        let params = vec![
            ("self".into(), None, false),
            ("x1".into(), None, false),
            ("y1".into(), None, false),
            ("x2".into(), None, false),
            ("y2".into(), None, false),
            ("fill".into(), Some(e.get("BLUE")?), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun282 = e.get("self")?.attr("line")?;
                let mut args280 = Vec::new();
                let mut kw281 = Vec::new();
                args280.push(e.get("x1")?);
                args280.push(e.get("y1")?);
                args280.push(e.get("x2")?);
                args280.push(e.get("y2")?);
                args280.push(e.get("fill")?);
                args280.push(Val::Float(0.8f64));
                fun282.call(args280, kw281)?
            };
            if {
                let v283 = e.get("x1")?;
                let v284 = e.get("x2")?;
                Val::Bool(compare("eq", v283.clone(), v284.clone())?.truthy()?)
            }
            .truthy()?
            {
                for item285 in {
                    let mut s = Vec::new();
                    s.push(e.get("y1")?);
                    s.push(e.get("y2")?);
                    Val::list(s)
                }
                .iter()?
                {
                    e.set("y", item285)?;
                    {
                        let fun288 = e.get("self")?.attr("line")?;
                        let mut args286 = Vec::new();
                        let mut kw287 = Vec::new();
                        args286.push(binary("sub", e.get("x1")?, Val::Int(4i64))?);
                        args286.push(e.get("y")?);
                        args286.push(binary("add", e.get("x1")?, Val::Int(4i64))?);
                        args286.push(e.get("y")?);
                        args286.push(e.get("fill")?);
                        args286.push(Val::Int(1i64));
                        fun288.call(args286, kw287)?
                    };
                }
            } else {
                for item289 in {
                    let mut s = Vec::new();
                    s.push(e.get("x1")?);
                    s.push(e.get("x2")?);
                    Val::list(s)
                }
                .iter()?
                {
                    e.set("x", item289)?;
                    {
                        let fun292 = e.get("self")?.attr("line")?;
                        let mut args290 = Vec::new();
                        let mut kw291 = Vec::new();
                        args290.push(e.get("x")?);
                        args290.push(binary("sub", e.get("y1")?, Val::Int(4i64))?);
                        args290.push(e.get("x")?);
                        args290.push(binary("add", e.get("y1")?, Val::Int(4i64))?);
                        args290.push(e.get("fill")?);
                        args290.push(Val::Int(1i64));
                        fun292.call(args290, kw291)?
                    };
                }
            }
            Ok(Val::None)
        })
    })?;
    e.set("Art", rt.python_type("common", "Art")?)?;
    // badge
    e.set("badge", {
        let params = vec![
            ("c".into(), None, false),
            ("n".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("label".into(), None, false),
            ("fill".into(), Some(e.get("BLUE")?), false),
            ("size".into(), Some(Val::Int(14i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun295 = e.get("box")?;
                let mut args293 = Vec::new();
                let mut kw294 = Vec::new();
                args293.push(e.get("c")?);
                args293.push(e.get("x")?);
                args293.push(e.get("y")?);
                args293.push(Val::Int(22i64));
                args293.push(Val::Int(22i64));
                args293.push(e.get("fill")?);
                kw294.push(("radius".into(), Val::Int(5i64)));
                fun295.call(args293, kw294)?
            };
            {
                let fun298 = e.get("text")?;
                let mut args296 = Vec::new();
                let mut kw297 = Vec::new();
                args296.push(e.get("c")?);
                args296.push({
                    let fun301 = e.get("str")?;
                    let mut args299 = Vec::new();
                    let mut kw300 = Vec::new();
                    args299.push(e.get("n")?);
                    fun301.call(args299, kw300)?
                });
                args296.push(binary("add", e.get("x")?, Val::Int(11i64))?);
                args296.push(binary("add", e.get("y")?, Val::Float(15.5f64))?);
                args296.push(Val::Int(12i64));
                args296.push(Val::Str("PlexBold".into()));
                args296.push(e.get("PAPER")?);
                args296.push(Val::Str("center".into()));
                fun298.call(args296, kw297)?
            };
            {
                let fun304 = e.get("text")?;
                let mut args302 = Vec::new();
                let mut kw303 = Vec::new();
                args302.push(e.get("c")?);
                args302.push(e.get("label")?);
                args302.push(binary("add", e.get("x")?, Val::Int(31i64))?);
                args302.push(binary("add", e.get("y")?, Val::Int(16i64))?);
                args302.push(e.get("size")?);
                args302.push(Val::Str("PlexSemi".into()));
                fun304.call(args302, kw303)?
            };
            Ok(Val::None)
        })
    })?;
    // page_backdrop
    e.set("page_backdrop", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned305 = e.get("BLEED_OVERHANG")?;
            e.set("bleed", assigned305.clone())?;
            {
                let fun308 = e.get("box")?;
                let mut args306 = Vec::new();
                let mut kw307 = Vec::new();
                args306.push(e.get("c")?);
                args306.push(unary("neg", e.get("bleed")?)?);
                args306.push(unary("neg", e.get("bleed")?)?);
                args306.push(binary(
                    "add",
                    e.get("W")?,
                    binary("mul", Val::Int(2i64), e.get("bleed")?)?,
                )?);
                args306.push(binary(
                    "add",
                    e.get("H")?,
                    binary("mul", Val::Int(2i64), e.get("bleed")?)?,
                )?);
                args306.push(e.get("PAPER")?);
                fun308.call(args306, kw307)?
            };
            {
                let fun311 = e.get("box")?;
                let mut args309 = Vec::new();
                let mut kw310 = Vec::new();
                args309.push(e.get("c")?);
                args309.push(unary("neg", e.get("bleed")?)?);
                args309.push(unary("neg", e.get("bleed")?)?);
                args309.push(binary(
                    "add",
                    e.get("W")?,
                    binary("mul", Val::Int(2i64), e.get("bleed")?)?,
                )?);
                args309.push(binary("add", e.get("BAND_INSET")?, e.get("bleed")?)?);
                args309.push(e.get("BLUE")?);
                fun311.call(args309, kw310)?
            };
            {
                let fun314 = e.get("box")?;
                let mut args312 = Vec::new();
                let mut kw313 = Vec::new();
                args312.push(e.get("c")?);
                args312.push(binary("sub", e.get("W")?, e.get("BAND_INSET")?)?);
                args312.push(e.get("BAND_INSET")?);
                args312.push(binary("add", e.get("BAND_INSET")?, e.get("bleed")?)?);
                args312.push(binary(
                    "add",
                    binary("sub", e.get("H")?, e.get("BAND_INSET")?)?,
                    e.get("bleed")?,
                )?);
                args312.push(e.get("ORANGE")?);
                fun314.call(args312, kw313)?
            };
            Ok(Val::None)
        })
    })?;
    // header
    e.set("header", {
        let params = vec![
            ("c".into(), None, false),
            ("n".into(), None, false),
            ("title".into(), None, false),
            ("subtitle".into(), None, false),
            ("total".into(), None, false),
            (
                "category".into(),
                Some(Val::Str("BENCH INSTRUCTIONS".into())),
                false,
            ),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun317 = e.get("text")?;
                let mut args315 = Vec::new();
                let mut kw316 = Vec::new();
                args315.push(e.get("c")?);
                args315.push({
                    let mut str318 = String::new();
                    str318.push_str("HOME SODA MACHINE / ");
                    str318.push_str(&format(&e.get("category")?, &String::new())?);
                    Val::Str(str318)
                });
                args315.push(Val::Int(32i64));
                args315.push(Val::Int(35i64));
                args315.push(Val::Float(9.5f64));
                args315.push(Val::Str("PlexSemi".into()));
                args315.push(e.get("BLUE")?);
                fun317.call(args315, kw316)?
            };
            {
                let fun321 = e.get("text")?;
                let mut args319 = Vec::new();
                let mut kw320 = Vec::new();
                args319.push(e.get("c")?);
                args319.push({
                    let mut str322 = String::new();
                    str322.push_str(&format(
                        &e.get("n")?,
                        &val_string({
                            let mut str323 = String::new();
                            str323.push_str("02d");
                            Val::Str(str323)
                        })?,
                    )?);
                    str322.push_str(" / ");
                    str322.push_str(&format(
                        &e.get("total")?,
                        &val_string({
                            let mut str324 = String::new();
                            str324.push_str("02d");
                            Val::Str(str324)
                        })?,
                    )?);
                    Val::Str(str322)
                });
                args319.push(Val::Int(577i64));
                args319.push(Val::Int(35i64));
                args319.push(Val::Int(10i64));
                args319.push(Val::Str("PlexSemi".into()));
                args319.push(e.get("MUTED")?);
                args319.push(Val::Str("right".into()));
                fun321.call(args319, kw320)?
            };
            for item325 in {
                let fun331 = e.get("enumerate")?;
                let mut args329 = Vec::new();
                let mut kw330 = Vec::new();
                args329.push({
                    let fun334 = e.get("title")?.attr("split")?;
                    let mut args332 = Vec::new();
                    let mut kw333 = Vec::new();
                    args332.push(Val::Str("\n".into()));
                    fun334.call(args332, kw333)?
                });
                fun331.call(args329, kw330)?
            }
            .iter()?
            {
                let unpack335 = unpack(item325, 2)?;
                e.set("i", unpack335[0].clone())?;
                e.set("line", unpack335[1].clone())?;
                {
                    let fun328 = e.get("text")?;
                    let mut args326 = Vec::new();
                    let mut kw327 = Vec::new();
                    args326.push(e.get("c")?);
                    args326.push(e.get("line")?);
                    args326.push(Val::Int(32i64));
                    args326.push(binary(
                        "add",
                        Val::Int(75i64),
                        binary("mul", e.get("i")?, Val::Int(31i64))?,
                    )?);
                    args326.push(Val::Int(30i64));
                    args326.push(Val::Str("PlexBold".into()));
                    fun328.call(args326, kw327)?
                };
            }
            let assigned336 = binary(
                "add",
                Val::Int(75i64),
                binary(
                    "mul",
                    binary(
                        "sub",
                        {
                            let fun339 = e.get("len")?;
                            let mut args337 = Vec::new();
                            let mut kw338 = Vec::new();
                            args337.push({
                                let fun342 = e.get("title")?.attr("split")?;
                                let mut args340 = Vec::new();
                                let mut kw341 = Vec::new();
                                args340.push(Val::Str("\n".into()));
                                fun342.call(args340, kw341)?
                            });
                            fun339.call(args337, kw338)?
                        },
                        Val::Int(1i64),
                    )?,
                    Val::Int(31i64),
                )?,
            )?;
            e.set("last", assigned336.clone())?;
            return Ok({
                let fun345 = e.get("paragraph")?;
                let mut args343 = Vec::new();
                let mut kw344 = Vec::new();
                args343.push(e.get("c")?);
                args343.push(e.get("subtitle")?);
                args343.push(Val::Int(33i64));
                args343.push(binary("add", e.get("last")?, Val::Int(14i64))?);
                args343.push(Val::Int(540i64));
                args343.push(Val::Int(13i64));
                args343.push(Val::Int(16i64));
                args343.push(e.get("MUTED")?);
                args343.push(Val::Int(48i64));
                fun345.call(args343, kw344)?
            });
            Ok(Val::None)
        })
    })?;
    // footer
    e.set("footer", {
        let params = vec![
            ("c".into(), None, false),
            ("n".into(), None, false),
            ("source".into(), None, false),
            ("link".into(), Some(Val::None), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun348 = e.get("box")?;
                let mut args346 = Vec::new();
                let mut kw347 = Vec::new();
                args346.push(e.get("c")?);
                args346.push(Val::Int(32i64));
                args346.push(Val::Int(752i64));
                args346.push(Val::Int(548i64));
                args346.push(Val::Float(0.8f64));
                args346.push(e.get("RULE")?);
                fun348.call(args346, kw347)?
            };
            {
                let fun351 = e.get("paragraph")?;
                let mut args349 = Vec::new();
                let mut kw350 = Vec::new();
                args349.push(e.get("c")?);
                args349.push(e.get("source")?);
                args349.push(Val::Int(32i64));
                args349.push(Val::Int(759i64));
                args349.push(Val::Int(425i64));
                args349.push(Val::Float(8.1f64));
                args349.push(Val::Float(9.5f64));
                args349.push(e.get("MUTED")?);
                args349.push(Val::Int(20i64));
                fun351.call(args349, kw350)?
            };
            {
                let fun354 = e.get("text")?;
                let mut args352 = Vec::new();
                let mut kw353 = Vec::new();
                args352.push(e.get("c")?);
                args352.push({
                    let mut str355 = String::new();
                    str355.push_str("LETTER / ");
                    str355.push_str(&format(&e.get("n")?, &String::new())?);
                    Val::Str(str355)
                });
                args352.push(Val::Int(580i64));
                args352.push(Val::Int(768i64));
                args352.push(Val::Int(8i64));
                args352.push(Val::Str("PlexSemi".into()));
                args352.push(e.get("MUTED")?);
                args352.push(Val::Str("right".into()));
                fun354.call(args352, kw353)?
            };
            if e.get("link")?.truthy()? {
                {
                    let fun358 = e.get("c")?.attr("linkURL")?;
                    let mut args356 = Vec::new();
                    let mut kw357 = Vec::new();
                    args356.push(e.get("link")?);
                    args356.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(32i64));
                        s.push(Val::Int(15i64));
                        s.push(Val::Int(580i64));
                        s.push(Val::Int(38i64));
                        Val::tuple(s)
                    });
                    kw357.push(("relative".into(), Val::Int(1i64)));
                    fun358.call(args356, kw357)?
                };
            }
            Ok(Val::None)
        })
    })?;
    // panel
    e.set("panel", {
        let params = vec![
            ("c".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("width".into(), None, false),
            ("height".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun361 = e.get("box")?;
                let mut args359 = Vec::new();
                let mut kw360 = Vec::new();
                args359.push(e.get("c")?);
                args359.push(e.get("x")?);
                args359.push(e.get("y")?);
                args359.push(e.get("width")?);
                args359.push(e.get("height")?);
                args359.push(Val::Str("#FFFFFF".into()));
                args359.push(e.get("RULE")?);
                args359.push(Val::Int(8i64));
                fun361.call(args359, kw360)?
            };
            Ok(Val::None)
        })
    })?;
    // begin_page
    e.set("begin_page", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun364 = e.get("page_backdrop")?;
                let mut args362 = Vec::new();
                let mut kw363 = Vec::new();
                args362.push(e.get("c")?);
                fun364.call(args362, kw363)?
            };
            {
                let fun367 = e.get("c")?.attr("saveState")?;
                let mut args365 = Vec::new();
                let mut kw366 = Vec::new();
                fun367.call(args365, kw366)?
            };
            {
                let fun370 = e.get("c")?.attr("translate")?;
                let mut args368 = Vec::new();
                let mut kw369 = Vec::new();
                args368.push(binary(
                    "truediv",
                    binary(
                        "mul",
                        e.get("W")?,
                        binary("sub", Val::Int(1i64), e.get("CONTENT_SCALE")?)?,
                    )?,
                    Val::Int(2i64),
                )?);
                args368.push(binary(
                    "truediv",
                    binary(
                        "mul",
                        e.get("H")?,
                        binary("sub", Val::Int(1i64), e.get("CONTENT_SCALE")?)?,
                    )?,
                    Val::Int(2i64),
                )?);
                fun370.call(args368, kw369)?
            };
            {
                let fun373 = e.get("c")?.attr("scale")?;
                let mut args371 = Vec::new();
                let mut kw372 = Vec::new();
                args371.push(e.get("CONTENT_SCALE")?);
                args371.push(e.get("CONTENT_SCALE")?);
                fun373.call(args371, kw372)?
            };
            Ok(Val::None)
        })
    })?;
    // end_page
    e.set("end_page", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun376 = e.get("c")?.attr("restoreState")?;
                let mut args374 = Vec::new();
                let mut kw375 = Vec::new();
                fun376.call(args374, kw375)?
            };
            {
                let fun379 = e.get("c")?.attr("showPage")?;
                let mut args377 = Vec::new();
                let mut kw378 = Vec::new();
                fun379.call(args377, kw378)?
            };
            Ok(Val::None)
        })
    })?;
    // publish
    e.set("publish", {
        let params = vec![
            ("pdf".into(), None, false),
            ("guide_dir".into(), None, false),
            ("title".into(), None, false),
            ("subtitle".into(), None, false),
            ("pages".into(), None, false),
            ("sources".into(), None, false),
            ("extra".into(), Some(Val::None), false),
            ("write_manifest".into(), Some(Val::Bool(true)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod380 = rt.import_module("PIL")?;
            e.set("Image", rt.member("PIL", "Image")?)?;
            let assigned381 = {
                let mut s = Vec::new();
                s.push({
                    let fun384 = e.get("Path")?;
                    let mut args382 = Vec::new();
                    let mut kw383 = Vec::new();
                    args382.push(e.get("pdf")?);
                    fun384.call(args382, kw383)?
                });
                s.push({
                    let fun387 = e.get("Path")?;
                    let mut args385 = Vec::new();
                    let mut kw386 = Vec::new();
                    args385.push(e.get("guide_dir")?);
                    fun387.call(args385, kw386)?
                });
                Val::tuple(s)
            };
            let unpack388 = unpack(assigned381.clone(), 2)?;
            e.set("pdf", unpack388[0].clone())?;
            e.set("guide_dir", unpack388[1].clone())?;
            {
                let fun391 = e.get("guide_dir")?.attr("mkdir")?;
                let mut args389 = Vec::new();
                let mut kw390 = Vec::new();
                kw390.push(("parents".into(), Val::Bool(true)));
                kw390.push(("exist_ok".into(), Val::Bool(true)));
                fun391.call(args389, kw390)?
            };
            let assigned392 = e.get("pdf")?.attr("stem")?;
            e.set("name", assigned392.clone())?;
            let assigned393 = binary("truediv", e.get("guide_dir")?, e.get("pdf")?.attr("name")?)?;
            e.set("canonical", assigned393.clone())?;
            {
                let fun396 = e.get("shutil")?.attr("copyfile")?;
                let mut args394 = Vec::new();
                let mut kw395 = Vec::new();
                args394.push(e.get("pdf")?);
                args394.push(e.get("canonical")?);
                fun396.call(args394, kw395)?
            };
            let assigned397 = binary("truediv", e.get("guide_dir")?, {
                let mut str398 = String::new();
                str398.push_str(&format(&e.get("name")?, &String::new())?);
                str398.push_str(".cover.png");
                Val::Str(str398)
            })?;
            e.set("cover", assigned397.clone())?;
            e.set("tempfile", rt.import_module("tempfile")?)?;
            let context399 = {
                let fun402 = e.get("tempfile")?.attr("TemporaryDirectory")?;
                let mut args400 = Vec::new();
                let mut kw401 = Vec::new();
                kw401.push(("prefix".into(), Val::Str("hsm-guide-cover-".into())));
                fun402.call(args400, kw401)?
            };
            e.set(
                "scratch",
                context399.attr("__enter__")?.call(vec![], vec![])?,
            )?;
            let context_result434 = (|| -> Result<Flow> {
                let assigned403 = binary(
                    "truediv",
                    {
                        let fun406 = e.get("Path")?;
                        let mut args404 = Vec::new();
                        let mut kw405 = Vec::new();
                        args404.push(e.get("scratch")?);
                        fun406.call(args404, kw405)?
                    },
                    Val::Str("cover".into()),
                )?;
                e.set("prefix", assigned403.clone())?;
                {
                    let fun409 = e.get("subprocess")?.attr("run")?;
                    let mut args407 = Vec::new();
                    let mut kw408 = Vec::new();
                    args407.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("pdftoppm".into()));
                        s.push(Val::Str("-f".into()));
                        s.push(Val::Str("1".into()));
                        s.push(Val::Str("-singlefile".into()));
                        s.push(Val::Str("-scale-to-x".into()));
                        s.push(Val::Str("800".into()));
                        s.push(Val::Str("-scale-to-y".into()));
                        s.push(Val::Str("-1".into()));
                        s.push(Val::Str("-png".into()));
                        s.push({
                            let fun412 = e.get("str")?;
                            let mut args410 = Vec::new();
                            let mut kw411 = Vec::new();
                            args410.push(e.get("pdf")?);
                            fun412.call(args410, kw411)?
                        });
                        s.push({
                            let fun415 = e.get("str")?;
                            let mut args413 = Vec::new();
                            let mut kw414 = Vec::new();
                            args413.push(e.get("prefix")?);
                            fun415.call(args413, kw414)?
                        });
                        Val::list(s)
                    });
                    kw408.push(("check".into(), Val::Bool(true)));
                    kw408.push(("capture_output".into(), Val::Bool(true)));
                    fun409.call(args407, kw408)?
                };
                let context416 = {
                    let fun419 = e.get("Image")?.attr("open")?;
                    let mut args417 = Vec::new();
                    let mut kw418 = Vec::new();
                    args417.push({
                        let fun422 = e.get("prefix")?.attr("with_suffix")?;
                        let mut args420 = Vec::new();
                        let mut kw421 = Vec::new();
                        args420.push(Val::Str(".png".into()));
                        fun422.call(args420, kw421)?
                    });
                    fun419.call(args417, kw418)?
                };
                e.set("im", context416.attr("__enter__")?.call(vec![], vec![])?)?;
                let context_result433 = (|| -> Result<Flow> {
                    {
                        let fun425 = {
                            let fun428 = e.get("im")?.attr("convert")?;
                            let mut args426 = Vec::new();
                            let mut kw427 = Vec::new();
                            args426.push(Val::Str("RGB".into()));
                            fun428.call(args426, kw427)?
                        }
                        .attr("save")?;
                        let mut args423 = Vec::new();
                        let mut kw424 = Vec::new();
                        args423.push(e.get("cover")?);
                        kw424.push(("optimize".into(), Val::Bool(true)));
                        fun425.call(args423, kw424)?
                    };
                    let assigned429 = {
                        let fun432 = e.get("list")?;
                        let mut args430 = Vec::new();
                        let mut kw431 = Vec::new();
                        args430.push(e.get("im")?.attr("size")?);
                        fun432.call(args430, kw431)?
                    };
                    e.set("cover_size", assigned429.clone())?;
                    Ok(Flow::Continue)
                })();
                context416
                    .attr("__exit__")?
                    .call(vec![Val::None, Val::None, Val::None], vec![])?;
                match context_result433? {
                    Flow::Continue => {}
                    Flow::Return(value) => return Ok(Flow::Return(value)),
                    Flow::Break => anyhow::bail!("break outside a loop"),
                    Flow::Next => anyhow::bail!("continue outside a loop"),
                }
                Ok(Flow::Continue)
            })();
            context399
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            match context_result434? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
                Flow::Break => anyhow::bail!("break outside a loop"),
                Flow::Next => anyhow::bail!("continue outside a loop"),
            }
            {
                let fun437 = binary("truediv", e.get("guide_dir")?, {
                    let mut str438 = String::new();
                    str438.push_str(&format(&e.get("pdf")?.attr("name")?, &String::new())?);
                    str438.push_str(".json");
                    Val::Str(str438)
                })?
                .attr("write_text")?;
                let mut args435 = Vec::new();
                let mut kw436 = Vec::new();
                args435.push(binary(
                    "add",
                    {
                        let fun441 = e.get("json")?.attr("dumps")?;
                        let mut args439 = Vec::new();
                        let mut kw440 = Vec::new();
                        args439.push({
                            let d = Val::dict(vec![]);
                            d.set(Val::Str("title".into()), e.get("title")?)?;
                            d.set(Val::Str("subtitle".into()), e.get("subtitle")?)?;
                            d.set(Val::Str("pages".into()), e.get("pages")?)?;
                            d.set(Val::Str("cover".into()), e.get("cover")?.attr("name")?)?;
                            d.set(Val::Str("cover_size".into()), e.get("cover_size")?)?;
                            d
                        });
                        kw440.push(("indent".into(), Val::Int(2i64)));
                        fun441.call(args439, kw440)?
                    },
                    Val::Str("\n".into()),
                )?);
                fun437.call(args435, kw436)?
            };
            let assigned442 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("pdf".into()), e.get("pdf")?.attr("name")?)?;
                d.set(Val::Str("pages".into()), e.get("pages")?)?;
                d.set(Val::Str("page_inches".into()), {
                    let mut s = Vec::new();
                    s.push(Val::Float(8.5f64));
                    s.push(Val::Int(11i64));
                    Val::list(s)
                })?;
                d.set(Val::Str("print_layout".into()), {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("content_scale".into()), e.get("CONTENT_SCALE")?)?;
                    d.set(
                        Val::Str("bleed_overhang_inches".into()),
                        Val::Float(0.25f64),
                    )?;
                    d.set(
                        Val::Str("colored_band_inset_inches".into()),
                        binary("truediv", Val::Int(1i64), Val::Int(3i64))?,
                    )?;
                    d.set(Val::Str("bleed_layer_scale".into()), Val::Int(1i64))?;
                    d.set(Val::Str("media_source".into()), Val::Str("rear".into()))?;
                    d.set(
                        Val::Str("print_scaling".into()),
                        Val::Str("100% / none".into()),
                    )?;
                    d
                })?;
                d.set(
                    Val::Str("artwork".into()),
                    Val::Str(
                        "vector schematic; dimensions govern; not a full-size template".into(),
                    ),
                )?;
                d.set(Val::Str("source_sha256".into()), {
                    let e = e.child();
                    let out443 = Val::dict(vec![]);
                    for item444 in e.get("sources")?.iter()? {
                        e.set("p", item444)?;
                        out443.set(
                            {
                                let fun447 = e.get("str")?;
                                let mut args445 = Vec::new();
                                let mut kw446 = Vec::new();
                                args445.push(e.get("p")?);
                                fun447.call(args445, kw446)?
                            },
                            {
                                let fun450 = {
                                    let fun453 = e.get("hashlib")?.attr("sha256")?;
                                    let mut args451 = Vec::new();
                                    let mut kw452 = Vec::new();
                                    args451.push({
                                        let fun456 =
                                            binary("truediv", e.get("ROOT")?, e.get("p")?)?
                                                .attr("read_bytes")?;
                                        let mut args454 = Vec::new();
                                        let mut kw455 = Vec::new();
                                        fun456.call(args454, kw455)?
                                    });
                                    fun453.call(args451, kw452)?
                                }
                                .attr("hexdigest")?;
                                let mut args448 = Vec::new();
                                let mut kw449 = Vec::new();
                                fun450.call(args448, kw449)?
                            },
                        )?;
                    }
                    out443
                })?;
                d.set(Val::Str("pdf_sha256".into()), {
                    let fun459 = {
                        let fun462 = e.get("hashlib")?.attr("sha256")?;
                        let mut args460 = Vec::new();
                        let mut kw461 = Vec::new();
                        args460.push({
                            let fun465 = e.get("pdf")?.attr("read_bytes")?;
                            let mut args463 = Vec::new();
                            let mut kw464 = Vec::new();
                            fun465.call(args463, kw464)?
                        });
                        fun462.call(args460, kw461)?
                    }
                    .attr("hexdigest")?;
                    let mut args457 = Vec::new();
                    let mut kw458 = Vec::new();
                    fun459.call(args457, kw458)?
                })?;
                d
            };
            e.set("manifest", assigned442.clone())?;
            if e.get("extra")?.truthy()? {
                {
                    let fun468 = e.get("manifest")?.attr("update")?;
                    let mut args466 = Vec::new();
                    let mut kw467 = Vec::new();
                    args466.push(e.get("extra")?);
                    fun468.call(args466, kw467)?
                };
            }
            if e.get("write_manifest")?.truthy()? {
                {
                    let fun471 = {
                        let fun474 = e.get("pdf")?.attr("with_suffix")?;
                        let mut args472 = Vec::new();
                        let mut kw473 = Vec::new();
                        args472.push(Val::Str(".sources.json".into()));
                        fun474.call(args472, kw473)?
                    }
                    .attr("write_text")?;
                    let mut args469 = Vec::new();
                    let mut kw470 = Vec::new();
                    args469.push(binary(
                        "add",
                        {
                            let fun477 = e.get("json")?.attr("dumps")?;
                            let mut args475 = Vec::new();
                            let mut kw476 = Vec::new();
                            args475.push(e.get("manifest")?);
                            kw476.push(("indent".into(), Val::Int(2i64)));
                            fun477.call(args475, kw476)?
                        },
                        Val::Str("\n".into()),
                    )?);
                    fun471.call(args469, kw470)?
                };
            }
            return Ok(e.get("canonical")?);
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
