#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let mod2 = rt.import_module("reportlab.pdfbase.pdfmetrics")?;
    e.set(
        "stringWidth",
        rt.member("reportlab.pdfbase.pdfmetrics", "stringWidth")?,
    )?;
    let mod3 = rt.import_module("reportlab.pdfgen")?;
    e.set("canvas", rt.member("reportlab.pdfgen", "canvas")?)?;
    let assigned4 = {
        let fun7 = {
            let fun10 = e.get("Path")?;
            let mut args8 = Vec::new();
            let mut kw9 = Vec::new();
            args8.push(e.get("__file__")?);
            fun10.call(args8, kw9)?
        }
        .attr("resolve")?;
        let mut args5 = Vec::new();
        let mut kw6 = Vec::new();
        fun7.call(args5, kw6)?
    }
    .attr("parent")?;
    e.set("HERE", assigned4.clone())?;
    let assigned11 = e.get("HERE")?.attr("parent")?;
    e.set("HW", assigned11.clone())?;
    {
        let fun14 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args12 = Vec::new();
        let mut kw13 = Vec::new();
        args12.push(Val::Int(0i64));
        args12.push({
            let fun17 = e.get("str")?;
            let mut args15 = Vec::new();
            let mut kw16 = Vec::new();
            args15.push(e.get("HERE")?);
            fun17.call(args15, kw16)?
        });
        fun14.call(args12, kw13)?
    };
    {
        let fun20 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args18 = Vec::new();
        let mut kw19 = Vec::new();
        args18.push(Val::Int(0i64));
        args18.push({
            let fun23 = e.get("str")?;
            let mut args21 = Vec::new();
            let mut kw22 = Vec::new();
            args21.push(binary("truediv", e.get("HW")?, Val::Str("scripts".into()))?);
            fun23.call(args21, kw22)?
        });
        fun20.call(args18, kw19)?
    };
    {
        let fun26 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args24 = Vec::new();
        let mut kw25 = Vec::new();
        args24.push(Val::Int(0i64));
        args24.push({
            let fun29 = e.get("str")?;
            let mut args27 = Vec::new();
            let mut kw28 = Vec::new();
            args27.push(binary(
                "truediv",
                e.get("HW")?,
                Val::Str("cut-parts/carbonation/endcaps-circular".into()),
            )?);
            fun29.call(args27, kw28)?
        });
        fun26.call(args24, kw25)?
    };
    let mod30 = rt.import_module("_document_export")?;
    e.set("export_pdf", rt.member("_document_export", "export_pdf")?)?;
    let mod31 = rt.import_module("endcap_circular_drawing")?;
    e.set("line", rt.member("endcap_circular_drawing", "line")?)?;
    e.set("text", rt.member("endcap_circular_drawing", "text")?)?;
    e.set("arrow", rt.member("endcap_circular_drawing", "arrow")?)?;
    e.set("leader", rt.member("endcap_circular_drawing", "leader")?)?;
    e.set(
        "circular_leader",
        rt.member("endcap_circular_drawing", "circular_leader")?,
    )?;
    e.set("center", rt.member("endcap_circular_drawing", "center")?)?;
    e.set(
        "horizontal_dimension",
        rt.member("endcap_circular_drawing", "horizontal_dimension")?,
    )?;
    e.set(
        "path_from_points",
        rt.member("endcap_circular_drawing", "path_from_points")?,
    )?;
    e.set("hatch", rt.member("endcap_circular_drawing", "hatch")?)?;
    e.set(
        "cutting_plane_ends",
        rt.member("endcap_circular_drawing", "cutting_plane_ends")?,
    )?;
    e.set("VISIBLE", rt.member("endcap_circular_drawing", "VISIBLE")?)?;
    e.set(
        "CENTER_DASH",
        rt.member("endcap_circular_drawing", "CENTER_DASH")?,
    )?;
    let mod32 = rt.import_module("_water_inlet_jet")?;
    e.set("JET_CAP_D", rt.member("_water_inlet_jet", "JET_CAP_D")?)?;
    e.set("JET_CAP_T", rt.member("_water_inlet_jet", "JET_CAP_T")?)?;
    e.set(
        "JET_PASSAGE_D",
        rt.member("_water_inlet_jet", "JET_PASSAGE_D")?,
    )?;
    let assigned33 = binary(
        "truediv",
        e.get("HERE")?,
        Val::Str("water-inlet-jet-cap-drawing.pdf".into()),
    )?;
    e.set("PDF_PATH", assigned33.clone())?;
    let assigned34 = {
        let mut s = Vec::new();
        s.push(binary("mul", Val::Int(11i64), Val::Int(72i64))?);
        s.push(binary("mul", Val::Float(8.5f64), Val::Int(72i64))?);
        Val::tuple(s)
    };
    e.set("SHEET", assigned34.clone())?;
    let assigned35 = binary(
        "truediv",
        binary("mul", Val::Int(5i64), Val::Int(72i64))?,
        Val::Float(25.4f64),
    )?;
    e.set("SCALE", assigned35.clone())?;
    let assigned36 = Val::Float(0.05f64);
    e.set("OD_TOL", assigned36.clone())?;
    let assigned37 = Val::Float(0.2f64);
    e.set("THICKNESS_TOL", assigned37.clone())?;
    let assigned38 = Val::Float(0.05f64);
    e.set("BORE_PLUS", assigned38.clone())?;
    let assigned39 = Val::Float(0.01f64);
    e.set("BORE_MINUS", assigned39.clone())?;
    let assigned40 = Val::Float(0.1f64);
    e.set("RADIAL_OFFSET_MAX", assigned40.clone())?;
    let assigned41 = Val::Float(1.0f64);
    e.set("AXIS_ANGLE_MAX", assigned41.clone())?;
    let assigned42 = Val::Float(0.05f64);
    e.set("FACE_GAP_MAX", assigned42.clone())?;
    let assigned43 = Val::Float(0.05f64);
    e.set("THICKNESS_VARIATION_MAX", assigned43.clone())?;
    let assigned44 = Val::Float(0.05f64);
    e.set("HOLE_EDGE_BREAK_MAX", assigned44.clone())?;
    let assigned45 = Val::Str("A".into());
    e.set("REVISION", assigned45.clone())?;
    let assigned46 = {
        let mut s = Vec::new();
        s.push(Val::Int(230i64));
        s.push(Val::Int(420i64));
        Val::tuple(s)
    };
    let unpack47 = unpack(assigned46.clone(), 2)?;
    e.set("CX", unpack47[0].clone())?;
    e.set("CY", unpack47[1].clone())?;
    let assigned48 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("face-and-hole".into()));
            s.push(Val::Int(126i64));
            s.push(Val::Int(337i64));
            s.push(Val::Int(613i64));
            s.push(Val::Int(569i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("od-and-section-markers".into()));
            s.push(Val::Int(126i64));
            s.push(Val::Int(299i64));
            s.push(Val::Int(338i64));
            s.push(Val::Int(469i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("section-and-face-labels".into()));
            s.push(Val::Int(45i64));
            s.push(Val::Int(183i64));
            s.push(Val::Int(455i64));
            s.push(Val::Int(337i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("manufacturing-notes".into()));
            s.push(Val::Int(427i64));
            s.push(Val::Int(175i64));
            s.push(Val::Int(746i64));
            s.push(Val::Int(471i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("units-and-finished-state".into()));
            s.push(Val::Int(35i64));
            s.push(Val::Int(27i64));
            s.push(Val::Int(199i64));
            s.push(Val::Int(146i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("title-block".into()));
            s.push(Val::Int(198i64));
            s.push(Val::Int(27i64));
            s.push(Val::Int(765i64));
            s.push(Val::Int(146i64));
            Val::tuple(s)
        });
        Val::list(s)
    };
    e.set("REVIEW_REGIONS", assigned48.clone())?;
    // face_view
    e.set("face_view", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned49 = binary(
                "truediv",
                binary("mul", e.get("JET_CAP_D")?, e.get("SCALE")?)?,
                Val::Int(2i64),
            )?;
            e.set("r", assigned49.clone())?;
            let assigned50 = binary(
                "truediv",
                binary("mul", e.get("JET_PASSAGE_D")?, e.get("SCALE")?)?,
                Val::Int(2i64),
            )?;
            e.set("bore", assigned50.clone())?;
            {
                let fun53 = e.get("text")?;
                let mut args51 = Vec::new();
                let mut kw52 = Vec::new();
                args51.push(e.get("c")?);
                args51.push(e.get("CX")?);
                args51.push(Val::Int(555i64));
                args51.push(Val::Str("JET EXIT FACE VIEW".into()));
                args51.push(Val::Int(12i64));
                kw52.push(("bold".into(), Val::Bool(true)));
                kw52.push(("align".into(), Val::Str("center".into())));
                fun53.call(args51, kw52)?
            };
            {
                let fun56 = e.get("text")?;
                let mut args54 = Vec::new();
                let mut kw55 = Vec::new();
                args54.push(e.get("c")?);
                args54.push(e.get("CX")?);
                args54.push(Val::Int(538i64));
                args54.push(Val::Str("SCALE 5:1".into()));
                args54.push(Val::Int(9i64));
                kw55.push(("align".into(), Val::Str("center".into())));
                fun56.call(args54, kw55)?
            };
            {
                let fun59 = e.get("c")?.attr("setLineWidth")?;
                let mut args57 = Vec::new();
                let mut kw58 = Vec::new();
                args57.push(e.get("VISIBLE")?);
                fun59.call(args57, kw58)?
            };
            {
                let fun62 = e.get("c")?.attr("circle")?;
                let mut args60 = Vec::new();
                let mut kw61 = Vec::new();
                args60.push(e.get("CX")?);
                args60.push(e.get("CY")?);
                args60.push(e.get("r")?);
                kw61.push(("stroke".into(), Val::Int(1i64)));
                kw61.push(("fill".into(), Val::Int(0i64)));
                fun62.call(args60, kw61)?
            };
            {
                let fun65 = e.get("c")?.attr("circle")?;
                let mut args63 = Vec::new();
                let mut kw64 = Vec::new();
                args63.push(e.get("CX")?);
                args63.push(e.get("CY")?);
                args63.push(e.get("bore")?);
                kw64.push(("stroke".into(), Val::Int(1i64)));
                kw64.push(("fill".into(), Val::Int(0i64)));
                fun65.call(args63, kw64)?
            };
            {
                let fun68 = e.get("center")?;
                let mut args66 = Vec::new();
                let mut kw67 = Vec::new();
                args66.push(e.get("c")?);
                args66.push(e.get("CX")?);
                args66.push(e.get("CY")?);
                args66.push(binary("add", e.get("r")?, Val::Int(14i64))?);
                fun68.call(args66, kw67)?
            };
            {
                let fun71 = e.get("cutting_plane_ends")?;
                let mut args69 = Vec::new();
                let mut kw70 = Vec::new();
                args69.push(e.get("c")?);
                args69.push(binary(
                    "sub",
                    binary("sub", e.get("CX")?, e.get("r")?)?,
                    Val::Int(24i64),
                )?);
                args69.push(binary(
                    "add",
                    binary("add", e.get("CX")?, e.get("r")?)?,
                    Val::Int(24i64),
                )?);
                args69.push(e.get("CY")?);
                args69.push(Val::Str("A".into()));
                fun71.call(args69, kw70)?
            };
            {
                let fun74 = e.get("circular_leader")?;
                let mut args72 = Vec::new();
                let mut kw73 = Vec::new();
                args72.push(e.get("c")?);
                args72.push({
                    let mut s = Vec::new();
                    s.push(e.get("CX")?);
                    s.push(e.get("CY")?);
                    Val::tuple(s)
                });
                args72.push(e.get("bore")?);
                args72.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(350i64));
                    s.push(Val::Int(515i64));
                    Val::tuple(s)
                });
                args72.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(370i64));
                    s.push(Val::Int(515i64));
                    Val::tuple(s)
                });
                args72.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut str75 = String::new();
                        str75.push_str("Ø");
                        str75.push_str(&format(
                            &e.get("JET_PASSAGE_D")?,
                            &val_string({
                                let mut str76 = String::new();
                                str76.push_str(".4f");
                                Val::Str(str76)
                            })?,
                        )?);
                        str75.push_str(" +");
                        str75.push_str(&format(
                            &e.get("BORE_PLUS")?,
                            &val_string({
                                let mut str77 = String::new();
                                str77.push_str(".3f");
                                Val::Str(str77)
                            })?,
                        )?);
                        str75.push_str("/-");
                        str75.push_str(&format(
                            &e.get("BORE_MINUS")?,
                            &val_string({
                                let mut str78 = String::new();
                                str78.push_str(".3f");
                                Val::Str(str78)
                            })?,
                        )?);
                        str75.push_str(" THRU");
                        Val::Str(str75)
                    });
                    s.push(Val::Str("(1/16 IN DRILL)".into()));
                    s.push(Val::Str("POSITION / ALIGNMENT: SEE NOTE 3".into()));
                    Val::list(s)
                });
                args72.push(Val::Float(9.5f64));
                fun74.call(args72, kw73)?
            };
            {
                let fun81 = e.get("horizontal_dimension")?;
                let mut args79 = Vec::new();
                let mut kw80 = Vec::new();
                args79.push(e.get("c")?);
                args79.push(binary("sub", e.get("CX")?, e.get("r")?)?);
                args79.push(binary("add", e.get("CX")?, e.get("r")?)?);
                args79.push(e.get("CY")?);
                args79.push(Val::Int(315i64));
                args79.push({
                    let mut str82 = String::new();
                    str82.push_str("Ø");
                    str82.push_str(&format(
                        &e.get("JET_CAP_D")?,
                        &val_string({
                            let mut str83 = String::new();
                            str83.push_str(".2f");
                            Val::Str(str83)
                        })?,
                    )?);
                    str82.push_str(" ±");
                    str82.push_str(&format(
                        &e.get("OD_TOL")?,
                        &val_string({
                            let mut str84 = String::new();
                            str84.push_str(".2f");
                            Val::Str(str84)
                        })?,
                    )?);
                    Val::Str(str82)
                });
                args79.push(Val::Int(11i64));
                fun81.call(args79, kw80)?
            };
            Ok(Val::None)
        })
    })?;
    // section_view
    e.set("section_view", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned85 = binary(
                "truediv",
                binary("mul", e.get("JET_CAP_D")?, e.get("SCALE")?)?,
                Val::Int(2i64),
            )?;
            e.set("r", assigned85.clone())?;
            let assigned86 = binary(
                "truediv",
                binary("mul", e.get("JET_PASSAGE_D")?, e.get("SCALE")?)?,
                Val::Int(2i64),
            )?;
            e.set("bore", assigned86.clone())?;
            let assigned87 = Val::Int(250i64);
            e.set("bottom", assigned87.clone())?;
            let assigned88 = binary(
                "add",
                e.get("bottom")?,
                binary("mul", e.get("JET_CAP_T")?, e.get("SCALE")?)?,
            )?;
            e.set("top", assigned88.clone())?;
            let assigned89 = {
                let mut s = Vec::new();
                s.push(binary("sub", e.get("CX")?, e.get("r")?)?);
                s.push(binary("add", e.get("CX")?, e.get("r")?)?);
                Val::tuple(s)
            };
            let unpack90 = unpack(assigned89.clone(), 2)?;
            e.set("left", unpack90[0].clone())?;
            e.set("right", unpack90[1].clone())?;
            for item91 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("left")?);
                    s.push(binary("sub", e.get("CX")?, e.get("bore")?)?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("CX")?, e.get("bore")?)?);
                    s.push(e.get("right")?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack105 = unpack(item91, 2)?;
                e.set("a", unpack105[0].clone())?;
                e.set("b", unpack105[1].clone())?;
                let assigned92 = {
                    let fun95 = e.get("path_from_points")?;
                    let mut args93 = Vec::new();
                    let mut kw94 = Vec::new();
                    args93.push(e.get("c")?);
                    args93.push({
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("a")?);
                            s.push(e.get("bottom")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("b")?);
                            s.push(e.get("bottom")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("b")?);
                            s.push(e.get("top")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("a")?);
                            s.push(e.get("top")?);
                            Val::tuple(s)
                        });
                        Val::list(s)
                    });
                    fun95.call(args93, kw94)?
                };
                e.set("p", assigned92.clone())?;
                {
                    let fun98 = e.get("hatch")?;
                    let mut args96 = Vec::new();
                    let mut kw97 = Vec::new();
                    args96.push(e.get("c")?);
                    args96.push(e.get("p")?);
                    args96.push({
                        let mut s = Vec::new();
                        s.push(e.get("a")?);
                        s.push(e.get("bottom")?);
                        s.push(e.get("b")?);
                        s.push(e.get("top")?);
                        Val::tuple(s)
                    });
                    kw97.push(("spacing".into(), Val::Int(6i64)));
                    fun98.call(args96, kw97)?
                };
                {
                    let fun101 = e.get("c")?.attr("setLineWidth")?;
                    let mut args99 = Vec::new();
                    let mut kw100 = Vec::new();
                    args99.push(e.get("VISIBLE")?);
                    fun101.call(args99, kw100)?
                };
                {
                    let fun104 = e.get("c")?.attr("drawPath")?;
                    let mut args102 = Vec::new();
                    let mut kw103 = Vec::new();
                    args102.push(e.get("p")?);
                    kw103.push(("stroke".into(), Val::Int(1i64)));
                    kw103.push(("fill".into(), Val::Int(0i64)));
                    fun104.call(args102, kw103)?
                };
            }
            {
                let fun108 = e.get("line")?;
                let mut args106 = Vec::new();
                let mut kw107 = Vec::new();
                args106.push(e.get("c")?);
                args106.push(e.get("CX")?);
                args106.push(binary("sub", e.get("bottom")?, Val::Int(12i64))?);
                args106.push(e.get("CX")?);
                args106.push(binary("add", e.get("top")?, Val::Int(12i64))?);
                kw107.push(("dash".into(), e.get("CENTER_DASH")?));
                fun108.call(args106, kw107)?
            };
            let assigned109 = Val::Int(348i64);
            e.set("dim_x", assigned109.clone())?;
            for item110 in {
                let mut s = Vec::new();
                s.push(e.get("bottom")?);
                s.push(e.get("top")?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("y", item110)?;
                {
                    let fun113 = e.get("line")?;
                    let mut args111 = Vec::new();
                    let mut kw112 = Vec::new();
                    args111.push(e.get("c")?);
                    args111.push(binary("add", e.get("right")?, Val::Int(4i64))?);
                    args111.push(e.get("y")?);
                    args111.push(binary("add", e.get("dim_x")?, Val::Int(5i64))?);
                    args111.push(e.get("y")?);
                    fun113.call(args111, kw112)?
                };
            }
            {
                let fun116 = e.get("line")?;
                let mut args114 = Vec::new();
                let mut kw115 = Vec::new();
                args114.push(e.get("c")?);
                args114.push(e.get("dim_x")?);
                args114.push(e.get("bottom")?);
                args114.push(e.get("dim_x")?);
                args114.push(e.get("top")?);
                fun116.call(args114, kw115)?
            };
            {
                let fun119 = e.get("arrow")?;
                let mut args117 = Vec::new();
                let mut kw118 = Vec::new();
                args117.push(e.get("c")?);
                args117.push({
                    let mut s = Vec::new();
                    s.push(e.get("dim_x")?);
                    s.push(e.get("bottom")?);
                    Val::tuple(s)
                });
                args117.push({
                    let mut s = Vec::new();
                    s.push(e.get("dim_x")?);
                    s.push(e.get("top")?);
                    Val::tuple(s)
                });
                fun119.call(args117, kw118)?
            };
            {
                let fun122 = e.get("arrow")?;
                let mut args120 = Vec::new();
                let mut kw121 = Vec::new();
                args120.push(e.get("c")?);
                args120.push({
                    let mut s = Vec::new();
                    s.push(e.get("dim_x")?);
                    s.push(e.get("top")?);
                    Val::tuple(s)
                });
                args120.push({
                    let mut s = Vec::new();
                    s.push(e.get("dim_x")?);
                    s.push(e.get("bottom")?);
                    Val::tuple(s)
                });
                fun122.call(args120, kw121)?
            };
            {
                let fun125 = e.get("text")?;
                let mut args123 = Vec::new();
                let mut kw124 = Vec::new();
                args123.push(e.get("c")?);
                args123.push(binary("add", e.get("dim_x")?, Val::Int(9i64))?);
                args123.push(binary(
                    "sub",
                    binary(
                        "truediv",
                        binary("add", e.get("bottom")?, e.get("top")?)?,
                        Val::Int(2i64),
                    )?,
                    Val::Int(3i64),
                )?);
                args123.push({
                    let mut str126 = String::new();
                    str126.push_str(&format(
                        &e.get("JET_CAP_T")?,
                        &val_string({
                            let mut str127 = String::new();
                            str127.push_str(".2f");
                            Val::Str(str127)
                        })?,
                    )?);
                    str126.push_str(" ±");
                    str126.push_str(&format(
                        &e.get("THICKNESS_TOL")?,
                        &val_string({
                            let mut str128 = String::new();
                            str128.push_str(".2f");
                            Val::Str(str128)
                        })?,
                    )?);
                    Val::Str(str126)
                });
                args123.push(Val::Int(10i64));
                fun125.call(args123, kw124)?
            };
            {
                let fun131 = e.get("leader")?;
                let mut args129 = Vec::new();
                let mut kw130 = Vec::new();
                args129.push(e.get("c")?);
                args129.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(190i64));
                    s.push(e.get("top")?);
                    Val::tuple(s)
                });
                args129.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(150i64));
                    s.push(Val::Int(305i64));
                    Val::tuple(s)
                });
                args129.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(130i64));
                    s.push(Val::Int(305i64));
                    Val::tuple(s)
                });
                args129.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("JET EXIT FACE".into()));
                    Val::list(s)
                });
                args129.push(Val::Float(8.5f64));
                fun131.call(args129, kw130)?
            };
            {
                let fun134 = e.get("leader")?;
                let mut args132 = Vec::new();
                let mut kw133 = Vec::new();
                args132.push(e.get("c")?);
                args132.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(270i64));
                    s.push(e.get("bottom")?);
                    Val::tuple(s)
                });
                args132.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(316i64));
                    s.push(Val::Int(215i64));
                    Val::tuple(s)
                });
                args132.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(339i64));
                    s.push(Val::Int(215i64));
                    Val::tuple(s)
                });
                args132.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("ELBOW SEATING FACE".into()));
                    Val::list(s)
                });
                args132.push(Val::Float(8.5f64));
                fun134.call(args132, kw133)?
            };
            {
                let fun137 = e.get("text")?;
                let mut args135 = Vec::new();
                let mut kw136 = Vec::new();
                args135.push(e.get("c")?);
                args135.push(e.get("CX")?);
                args135.push(Val::Int(220i64));
                args135.push(Val::Str("SECTION A-A".into()));
                args135.push(Val::Int(11i64));
                kw136.push(("bold".into(), Val::Bool(true)));
                kw136.push(("align".into(), Val::Str("center".into())));
                fun137.call(args135, kw136)?
            };
            {
                let fun140 = e.get("text")?;
                let mut args138 = Vec::new();
                let mut kw139 = Vec::new();
                args138.push(e.get("c")?);
                args138.push(e.get("CX")?);
                args138.push(Val::Int(204i64));
                args138.push(Val::Str("THROUGH AXIS - SCALE 5:1".into()));
                args138.push(Val::Float(8.5f64));
                kw139.push(("align".into(), Val::Str("center".into())));
                fun140.call(args138, kw139)?
            };
            Ok(Val::None)
        })
    })?;
    // manufacture_notes
    e.set("manufacture_notes",{let params=vec![("c".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned141={let mut s=Vec::new();s.push(Val::Int(435i64));s.push(Val::Int(440i64));s.push(Val::Int(300i64));s.push(Val::Float(8.7f64));s.push(Val::Float(11.5f64));Val::tuple(s)};let unpack142=unpack(assigned141.clone(),5)?;e.set("x",unpack142[0].clone())?;e.set("y",unpack142[1].clone())?;e.set("width",unpack142[2].clone())?;e.set("size",unpack142[3].clone())?;e.set("leading",unpack142[4].clone())?;
{let fun145=e.get("text")?;let mut args143=Vec::new();let mut kw144=Vec::new();args143.push(e.get("c")?);args143.push(e.get("x")?);args143.push(Val::Int(460i64));args143.push(Val::Str("MANUFACTURE AND INSPECTION".into()));args143.push(Val::Int(10i64));kw144.push(("bold".into(),Val::Bool(true)));fun145.call(args143,kw144)?};
let assigned146={let mut s=Vec::new();s.push(Val::Str("1. MATERIAL: 316 STAINLESS ROUND ROD. SELECT STOCK MEETING THE OD LIMITS. DIMENSIONS APPLY AFTER FACE FINISHING AND DEBURRING.".into()));s.push(Val::Str("2. DRILL WHILE ATTACHED TO A 50-60 mm HANDLING BLANK. EXTEND THE FULL-DIAMETER BORE BEYOND THE FINAL CUT FACE; SAW THE SLICE AND FINISH TO THICKNESS.".into()));s.push({let mut str147=String::new();str147.push_str("3. CENTER THE HOLE AT BOTH FACES WITHIN ");str147.push_str(&format(&e.get("RADIAL_OFFSET_MAX")?,&val_string({let mut str148=String::new();str148.push_str(".2f");Val::Str(str148)})?)?);str147.push_str(" RADIAL OF THE OD AXIS. HOLE AXIS NORMAL TO ELBOW SEATING FACE WITHIN ");str147.push_str(&format(&e.get("AXIS_ANGLE_MAX")?,&val_string({let mut str149=String::new();str149.push_str("g");Val::Str(str149)})?)?);str147.push_str("°.");Val::Str(str147)});s.push({let mut str150=String::new();str150.push_str("4. THICKNESS VARIATION ACROSS CAP: ");str150.push_str(&format(&e.get("THICKNESS_VARIATION_MAX")?,&val_string({let mut str151=String::new();str151.push_str(".2f");Val::Str(str151)})?)?);str150.push_str(" MAX. ELBOW SEATING FACE: ");str150.push_str(&format(&e.get("FACE_GAP_MAX")?,&val_string({let mut str152=String::new();str152.push_str(".2f");Val::Str(str152)})?)?);str150.push_str(" MAX GAP ON A FLAT INSPECTION SURFACE, UNDER OWN WEIGHT.");Val::Str(str150)});s.push({let mut str153=String::new();str153.push_str("5. REMOVE BURRS FROM BOTH HOLE ENDS; EDGE BREAK ");str153.push_str(&format(&e.get("HOLE_EDGE_BREAK_MAX")?,&val_string({let mut str154=String::new();str154.push_str(".2f");Val::Str(str154)})?)?);str153.push_str(" MAX. MAINTAIN THE CYLINDRICAL PASSAGE. OD CORNERS: BURR REMOVAL ONLY; PRESERVE THE SQUARE WELD RIM.");Val::Str(str153)});s.push(Val::Str("6. REMOVE ALL CUTTING FLUID AND LOOSE METAL. CAP-TO-ELBOW WELD, INSTALLED FIT AND POST-WELD INSPECTION: ASSEMBLY/WATER-INLET-JET.MD.".into()));Val::list(s)};e.set("paragraphs",assigned146.clone())?;
for item155 in e.get("paragraphs")?.iter()? {
e.set("paragraph",item155)?;let assigned156=Val::Str("".into());e.set("row",assigned156.clone())?;
for item157 in {let fun175=e.get("paragraph")?.attr("split")?;let mut args173=Vec::new();let mut kw174=Vec::new();fun175.call(args173,kw174)?}.iter()? {
e.set("word",item157)?;let assigned158={let fun161=binary("add",binary("add",e.get("row")?,Val::Str(" ".into()))?,e.get("word")?)?.attr("strip")?;let mut args159=Vec::new();let mut kw160=Vec::new();fun161.call(args159,kw160)?};e.set("trial",assigned158.clone())?;
if {let v167=e.get("row")?;if v167.truthy()? {{let v165={let fun164=e.get("stringWidth")?;let mut args162=Vec::new();let mut kw163=Vec::new();args162.push(e.get("trial")?);args162.push(Val::Str("Helvetica".into()));args162.push(e.get("size")?);fun164.call(args162,kw163)?};let v166=e.get("width")?;Val::Bool(compare("gt",v165.clone(),v166.clone())?.truthy()?)}} else {v167}}.truthy()? {
{let fun170=e.get("text")?;let mut args168=Vec::new();let mut kw169=Vec::new();args168.push(e.get("c")?);args168.push(e.get("x")?);args168.push(e.get("y")?);args168.push(e.get("row")?);args168.push(e.get("size")?);fun170.call(args168,kw169)?};
e.set("y",binary("sub",e.get("y")?,e.get("leading")?)?)?;
let assigned171=e.get("word")?;e.set("row",assigned171.clone())?;
}else{
let assigned172=e.get("trial")?;e.set("row",assigned172.clone())?;
}
}
{let fun178=e.get("text")?;let mut args176=Vec::new();let mut kw177=Vec::new();args176.push(e.get("c")?);args176.push(e.get("x")?);args176.push(e.get("y")?);args176.push(e.get("row")?);args176.push(e.get("size")?);fun178.call(args176,kw177)?};
e.set("y",binary("sub",e.get("y")?,binary("add",e.get("leading")?,Val::Int(5i64))?)?)?;
}
return Ok(e.get("y")?);
Ok(Val::None)})})?;
    // title_block
    e.set("title_block", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned179 = {
                let mut s = Vec::new();
                s.push(Val::Int(203i64));
                s.push(Val::Int(765i64));
                s.push(Val::Int(27i64));
                s.push(Val::Int(143i64));
                Val::tuple(s)
            };
            let unpack180 = unpack(assigned179.clone(), 4)?;
            e.set("left", unpack180[0].clone())?;
            e.set("right", unpack180[1].clone())?;
            e.set("bottom", unpack180[2].clone())?;
            e.set("top", unpack180[3].clone())?;
            {
                let fun183 = e.get("c")?.attr("setLineWidth")?;
                let mut args181 = Vec::new();
                let mut kw182 = Vec::new();
                args181.push(Val::Float(0.7f64));
                fun183.call(args181, kw182)?
            };
            {
                let fun186 = e.get("c")?.attr("rect")?;
                let mut args184 = Vec::new();
                let mut kw185 = Vec::new();
                args184.push(e.get("left")?);
                args184.push(e.get("bottom")?);
                args184.push(binary("sub", e.get("right")?, e.get("left")?)?);
                args184.push(binary("sub", e.get("top")?, e.get("bottom")?)?);
                kw185.push(("stroke".into(), Val::Int(1i64)));
                kw185.push(("fill".into(), Val::Int(0i64)));
                fun186.call(args184, kw185)?
            };
            {
                let fun189 = e.get("line")?;
                let mut args187 = Vec::new();
                let mut kw188 = Vec::new();
                args187.push(e.get("c")?);
                args187.push(e.get("left")?);
                args187.push(Val::Int(98i64));
                args187.push(e.get("right")?);
                args187.push(Val::Int(98i64));
                fun189.call(args187, kw188)?
            };
            {
                let fun192 = e.get("line")?;
                let mut args190 = Vec::new();
                let mut kw191 = Vec::new();
                args190.push(e.get("c")?);
                args190.push(e.get("left")?);
                args190.push(Val::Int(65i64));
                args190.push(e.get("right")?);
                args190.push(Val::Int(65i64));
                fun192.call(args190, kw191)?
            };
            {
                let fun195 = e.get("line")?;
                let mut args193 = Vec::new();
                let mut kw194 = Vec::new();
                args193.push(e.get("c")?);
                args193.push(binary("sub", e.get("right")?, Val::Int(135i64))?);
                args193.push(Val::Int(98i64));
                args193.push(binary("sub", e.get("right")?, Val::Int(135i64))?);
                args193.push(e.get("top")?);
                fun195.call(args193, kw194)?
            };
            {
                let fun198 = e.get("text")?;
                let mut args196 = Vec::new();
                let mut kw197 = Vec::new();
                args196.push(e.get("c")?);
                args196.push(binary("add", e.get("left")?, Val::Int(10i64))?);
                args196.push(Val::Int(126i64));
                args196.push(Val::Str("HOME SODA MACHINE".into()));
                args196.push(Val::Int(8i64));
                fun198.call(args196, kw197)?
            };
            {
                let fun201 = e.get("text")?;
                let mut args199 = Vec::new();
                let mut kw200 = Vec::new();
                args199.push(e.get("c")?);
                args199.push(binary("add", e.get("left")?, Val::Int(10i64))?);
                args199.push(Val::Int(108i64));
                args199.push(Val::Str("WATER-INLET JET CAP".into()));
                args199.push(Val::Float(11.5f64));
                kw200.push(("bold".into(), Val::Bool(true)));
                fun201.call(args199, kw200)?
            };
            {
                let fun204 = e.get("text")?;
                let mut args202 = Vec::new();
                let mut kw203 = Vec::new();
                args202.push(e.get("c")?);
                args202.push(binary("sub", e.get("right")?, Val::Float(67.5f64))?);
                args202.push(Val::Int(125i64));
                args202.push(Val::Str("FINISHED PART".into()));
                args202.push(Val::Int(9i64));
                kw203.push(("bold".into(), Val::Bool(true)));
                kw203.push(("align".into(), Val::Str("center".into())));
                fun204.call(args202, kw203)?
            };
            {
                let fun207 = e.get("text")?;
                let mut args205 = Vec::new();
                let mut kw206 = Vec::new();
                args205.push(e.get("c")?);
                args205.push(binary("sub", e.get("right")?, Val::Float(67.5f64))?);
                args205.push(Val::Int(110i64));
                args205.push(Val::Str("CAP BEFORE WELD".into()));
                args205.push(Val::Int(9i64));
                kw206.push(("align".into(), Val::Str("center".into())));
                fun207.call(args205, kw206)?
            };
            for item208 in {
                let mut s = Vec::new();
                s.push(binary("add", e.get("left")?, Val::Int(235i64))?);
                s.push(binary("add", e.get("left")?, Val::Int(370i64))?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("col", item208)?;
                {
                    let fun211 = e.get("line")?;
                    let mut args209 = Vec::new();
                    let mut kw210 = Vec::new();
                    args209.push(e.get("c")?);
                    args209.push(e.get("col")?);
                    args209.push(Val::Int(65i64));
                    args209.push(e.get("col")?);
                    args209.push(Val::Int(98i64));
                    fun211.call(args209, kw210)?
                };
            }
            for item212 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("left")?, Val::Int(10i64))?);
                    s.push(Val::Str("MATERIAL".into()));
                    s.push(Val::Str("316 STAINLESS STEEL".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("left")?, Val::Int(245i64))?);
                    s.push(Val::Str("UNITS".into()));
                    s.push(Val::Str("MILLIMETERS".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("left")?, Val::Int(380i64))?);
                    s.push(Val::Str("QUANTITY".into()));
                    s.push(Val::Str("1 PER CARBONATOR".into()));
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack219 = unpack(item212, 3)?;
                e.set("x", unpack219[0].clone())?;
                e.set("label", unpack219[1].clone())?;
                e.set("value", unpack219[2].clone())?;
                {
                    let fun215 = e.get("text")?;
                    let mut args213 = Vec::new();
                    let mut kw214 = Vec::new();
                    args213.push(e.get("c")?);
                    args213.push(e.get("x")?);
                    args213.push(Val::Int(87i64));
                    args213.push(e.get("label")?);
                    args213.push(Val::Int(7i64));
                    fun215.call(args213, kw214)?
                };
                {
                    let fun218 = e.get("text")?;
                    let mut args216 = Vec::new();
                    let mut kw217 = Vec::new();
                    args216.push(e.get("c")?);
                    args216.push(e.get("x")?);
                    args216.push(Val::Int(73i64));
                    args216.push(e.get("value")?);
                    args216.push(Val::Float(8.5f64));
                    kw217.push(("bold".into(), Val::Bool(true)));
                    fun218.call(args216, kw217)?
                };
            }
            let assigned220 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("left")?);
                    s.push(binary("add", e.get("left")?, Val::Int(175i64))?);
                    s.push(Val::Str("DRAWING".into()));
                    s.push(Val::Str("JET-CAP-01".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("left")?, Val::Int(175i64))?);
                    s.push(binary("add", e.get("left")?, Val::Int(220i64))?);
                    s.push(Val::Str("REV".into()));
                    s.push(e.get("REVISION")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("left")?, Val::Int(220i64))?);
                    s.push(binary("add", e.get("left")?, Val::Int(335i64))?);
                    s.push(Val::Str("DATE".into()));
                    s.push(Val::Str("2026-10-26".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("left")?, Val::Int(335i64))?);
                    s.push(binary("add", e.get("left")?, Val::Int(452i64))?);
                    s.push(Val::Str("SCALE".into()));
                    s.push(Val::Str("AS SHOWN".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("left")?, Val::Int(452i64))?);
                    s.push(e.get("right")?);
                    s.push(Val::Str("SHEET".into()));
                    s.push(Val::Str("1 OF 1".into()));
                    Val::tuple(s)
                });
                Val::tuple(s)
            };
            e.set("fields", assigned220.clone())?;
            for item221 in {
                let fun233 = e.get("enumerate")?;
                let mut args231 = Vec::new();
                let mut kw232 = Vec::new();
                args231.push(e.get("fields")?);
                fun233.call(args231, kw232)?
            }
            .iter()?
            {
                let unpack234 = unpack(item221, 2)?;
                e.set("i", unpack234[0].clone())?;
                let unpack235 = unpack(unpack234[1].clone(), 4)?;
                e.set("a", unpack235[0].clone())?;
                e.set("b", unpack235[1].clone())?;
                e.set("label", unpack235[2].clone())?;
                e.set("value", unpack235[3].clone())?;
                if e.get("i")?.truthy()? {
                    {
                        let fun224 = e.get("line")?;
                        let mut args222 = Vec::new();
                        let mut kw223 = Vec::new();
                        args222.push(e.get("c")?);
                        args222.push(e.get("a")?);
                        args222.push(e.get("bottom")?);
                        args222.push(e.get("a")?);
                        args222.push(Val::Int(65i64));
                        fun224.call(args222, kw223)?
                    };
                }
                {
                    let fun227 = e.get("text")?;
                    let mut args225 = Vec::new();
                    let mut kw226 = Vec::new();
                    args225.push(e.get("c")?);
                    args225.push(binary("add", e.get("a")?, Val::Int(9i64))?);
                    args225.push(Val::Int(53i64));
                    args225.push(e.get("label")?);
                    args225.push(Val::Int(7i64));
                    fun227.call(args225, kw226)?
                };
                {
                    let fun230 = e.get("text")?;
                    let mut args228 = Vec::new();
                    let mut kw229 = Vec::new();
                    args228.push(e.get("c")?);
                    args228.push(binary("add", e.get("a")?, Val::Int(9i64))?);
                    args228.push(Val::Int(37i64));
                    args228.push(e.get("value")?);
                    args228.push(Val::Int(9i64));
                    kw229.push(("bold".into(), Val::Bool(true)));
                    fun230.call(args228, kw229)?
                };
            }
            {
                let fun238 = e.get("text")?;
                let mut args236 = Vec::new();
                let mut kw237 = Vec::new();
                args236.push(e.get("c")?);
                args236.push(Val::Int(47i64));
                args236.push(Val::Int(127i64));
                args236.push(Val::Str("HSM-000011".into()));
                args236.push(Val::Int(9i64));
                kw237.push(("bold".into(), Val::Bool(true)));
                fun238.call(args236, kw237)?
            };
            {
                let fun241 = e.get("text")?;
                let mut args239 = Vec::new();
                let mut kw240 = Vec::new();
                args239.push(e.get("c")?);
                args239.push(Val::Int(47i64));
                args239.push(Val::Int(110i64));
                args239.push(Val::Str("mm DIMENSIONS GOVERN.".into()));
                args239.push(Val::Int(8i64));
                fun241.call(args239, kw240)?
            };
            {
                let fun244 = e.get("text")?;
                let mut args242 = Vec::new();
                let mut kw243 = Vec::new();
                args242.push(e.get("c")?);
                args242.push(Val::Int(47i64));
                args242.push(Val::Int(80i64));
                args242.push(Val::Str("FINISHED, DEBURRED CAP.".into()));
                args242.push(Val::Int(8i64));
                fun244.call(args242, kw243)?
            };
            {
                let fun247 = e.get("text")?;
                let mut args245 = Vec::new();
                let mut kw246 = Vec::new();
                args245.push(e.get("c")?);
                args245.push(Val::Int(47i64));
                args245.push(Val::Int(63i64));
                args245.push(Val::Str("DO NOT SCALE.".into()));
                args245.push(Val::Int(8i64));
                kw246.push(("bold".into(), Val::Bool(true)));
                fun247.call(args245, kw246)?
            };
            {
                let fun250 = e.get("text")?;
                let mut args248 = Vec::new();
                let mut kw249 = Vec::new();
                args248.push(e.get("c")?);
                args248.push(Val::Int(47i64));
                args248.push(Val::Int(49i64));
                args248.push(Val::Str("ANSI A / 11 x 8.5 IN".into()));
                args248.push(Val::Float(7.5f64));
                fun250.call(args248, kw249)?
            };
            {
                let fun253 = e.get("text")?;
                let mut args251 = Vec::new();
                let mut kw252 = Vec::new();
                args251.push(e.get("c")?);
                args251.push(Val::Int(47i64));
                args251.push(Val::Int(36i64));
                args251.push(Val::Str("PRINT AT 100% FOR SCALE.".into()));
                args251.push(Val::Float(7.5f64));
                fun253.call(args251, kw252)?
            };
            Ok(Val::None)
        })
    })?;
    // build_pdf
    e.set("build_pdf",{let params=vec![("path".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned254={let fun257=e.get("canvas")?.attr("Canvas")?;let mut args255=Vec::new();let mut kw256=Vec::new();args255.push({let fun260=e.get("str")?;let mut args258=Vec::new();let mut kw259=Vec::new();args258.push(e.get("path")?);fun260.call(args258,kw259)?});kw256.push(("pagesize".into(),e.get("SHEET")?));kw256.push(("invariant".into(),Val::Int(1i64)));kw256.push(("pageCompression".into(),Val::Int(1i64)));fun257.call(args255,kw256)?};e.set("c",assigned254.clone())?;
{let fun263=e.get("c")?.attr("setTitle")?;let mut args261=Vec::new();let mut kw262=Vec::new();args261.push(Val::Str("Carbonator water-inlet jet cap - engineering drawing".into()));fun263.call(args261,kw262)?};
{let fun266=e.get("c")?.attr("setAuthor")?;let mut args264=Vec::new();let mut kw265=Vec::new();args264.push(Val::Str("Home Soda Machine / Codex".into()));fun266.call(args264,kw265)?};
{let fun269=e.get("c")?.attr("setSubject")?;let mut args267=Vec::new();let mut kw268=Vec::new();args267.push(Val::Str("JET-CAP-01 Rev A: finished 316 cap, 1/16-inch through passage and pre-weld finish".into()));fun269.call(args267,kw268)?};
{let fun272=e.get("c")?.attr("setStrokeColorRGB")?;let mut args270=Vec::new();let mut kw271=Vec::new();args270.push(Val::Int(0i64));args270.push(Val::Int(0i64));args270.push(Val::Int(0i64));fun272.call(args270,kw271)?};
{let fun275=e.get("c")?.attr("setFillColorRGB")?;let mut args273=Vec::new();let mut kw274=Vec::new();args273.push(Val::Int(0i64));args273.push(Val::Int(0i64));args273.push(Val::Int(0i64));fun275.call(args273,kw274)?};
{let fun278=e.get("c")?.attr("setLineWidth")?;let mut args276=Vec::new();let mut kw277=Vec::new();args276.push(Val::Float(0.8f64));fun278.call(args276,kw277)?};
{let fun281=e.get("c")?.attr("rect")?;let mut args279=Vec::new();let mut kw280=Vec::new();args279.push(Val::Int(27i64));args279.push(Val::Int(27i64));args279.push(binary("sub",e.get("SHEET")?.get(Val::Int(0i64))?,Val::Int(54i64))?);args279.push(binary("sub",e.get("SHEET")?.get(Val::Int(1i64))?,Val::Int(54i64))?);kw280.push(("stroke".into(),Val::Int(1i64)));kw280.push(("fill".into(),Val::Int(0i64)));fun281.call(args279,kw280)?};
{let fun284=e.get("face_view")?;let mut args282=Vec::new();let mut kw283=Vec::new();args282.push(e.get("c")?);fun284.call(args282,kw283)?};
{let fun287=e.get("section_view")?;let mut args285=Vec::new();let mut kw286=Vec::new();args285.push(e.get("c")?);fun287.call(args285,kw286)?};
{let fun290=e.get("manufacture_notes")?;let mut args288=Vec::new();let mut kw289=Vec::new();args288.push(e.get("c")?);fun290.call(args288,kw289)?};
{let fun293=e.get("title_block")?;let mut args291=Vec::new();let mut kw292=Vec::new();args291.push(e.get("c")?);fun293.call(args291,kw292)?};
{let fun296=e.get("c")?.attr("showPage")?;let mut args294=Vec::new();let mut kw295=Vec::new();fun296.call(args294,kw295)?};
{let fun299=e.get("c")?.attr("save")?;let mut args297=Vec::new();let mut kw298=Vec::new();fun299.call(args297,kw298)?};
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun302 = e.get("export_pdf")?;
        let mut args300 = Vec::new();
        let mut kw301 = Vec::new();
        args300.push(e.get("build_pdf")?);
        args300.push({
            let fun305 = e.get("str")?;
            let mut args303 = Vec::new();
            let mut kw304 = Vec::new();
            args303.push(e.get("PDF_PATH")?);
            fun305.call(args303, kw304)?
        });
        fun302.call(args300, kw301)?
    };
    {
        let fun308 = e.get("print")?;
        let mut args306 = Vec::new();
        let mut kw307 = Vec::new();
        args306.push({
            let mut str309 = String::new();
            str309.push_str("Exported: ");
            str309.push_str(&format(&e.get("PDF_PATH")?, &String::new())?);
            Val::Str(str309)
        });
        fun308.call(args306, kw307)?
    };
    Ok(Val::None)
}
