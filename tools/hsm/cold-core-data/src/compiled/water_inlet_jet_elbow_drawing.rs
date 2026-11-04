#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let mod2 = rt.import_module("reportlab.pdfgen")?;
    e.set("canvas", rt.member("reportlab.pdfgen", "canvas")?)?;
    let mod3 = rt.import_module("reportlab.pdfbase.pdfmetrics")?;
    e.set(
        "stringWidth",
        rt.member("reportlab.pdfbase.pdfmetrics", "stringWidth")?,
    )?;
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
    for item12 in {
        let mut s = Vec::new();
        s.push(e.get("HERE")?);
        s.push(binary("truediv", e.get("HW")?, Val::Str("scripts".into()))?);
        s.push(binary(
            "truediv",
            e.get("HW")?,
            Val::Str("printed-parts/cold-core".into()),
        )?);
        s.push(binary(
            "truediv",
            e.get("HW")?,
            Val::Str("cut-parts/carbonation/endcaps-circular".into()),
        )?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("folder", item12)?;
        {
            let fun15 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args13 = Vec::new();
            let mut kw14 = Vec::new();
            args13.push(Val::Int(0i64));
            args13.push({
                let fun18 = e.get("str")?;
                let mut args16 = Vec::new();
                let mut kw17 = Vec::new();
                args16.push(e.get("folder")?);
                fun18.call(args16, kw17)?
            });
            fun15.call(args13, kw14)?
        };
    }
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun21 = e.get("_rust_part")?.attr("start")?;
        let mut args19 = Vec::new();
        let mut kw20 = Vec::new();
        fun21.call(args19, kw20)?
    };
    let mod22 = rt.import_module("_document_export")?;
    e.set("export_pdf", rt.member("_document_export", "export_pdf")?)?;
    let mod23 = rt.import_module("endcap_circular_drawing")?;
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
    e.set("THIN", rt.member("endcap_circular_drawing", "THIN")?)?;
    e.set(
        "CENTER_DASH",
        rt.member("endcap_circular_drawing", "CENTER_DASH")?,
    )?;
    e.set("carbonator", rt.import_module("_carbonator")?)?;
    e.set("fitting", rt.import_module("_fittings")?)?;
    e.set("cap", rt.import_module("water_inlet_jet_cap_drawing")?)?;
    let mod24 = rt.import_module("_water_inlet_jet")?;
    e.set("JET_CAP_D", rt.member("_water_inlet_jet", "JET_CAP_D")?)?;
    e.set("JET_CAP_T", rt.member("_water_inlet_jet", "JET_CAP_T")?)?;
    e.set(
        "JET_PASSAGE_D",
        rt.member("_water_inlet_jet", "JET_PASSAGE_D")?,
    )?;
    let assigned25 = binary(
        "truediv",
        e.get("HERE")?,
        Val::Str("water-inlet-jet-elbow-drawing.pdf".into()),
    )?;
    e.set("PDF_PATH", assigned25.clone())?;
    let assigned26 = {
        let mut s = Vec::new();
        s.push(binary("mul", Val::Int(17i64), Val::Int(72i64))?);
        s.push(binary("mul", Val::Int(11i64), Val::Int(72i64))?);
        Val::tuple(s)
    };
    e.set("SHEET", assigned26.clone())?;
    let assigned27 = binary("truediv", Val::Int(72i64), Val::Float(25.4f64))?;
    e.set("PT_PER_MM", assigned27.clone())?;
    let assigned28 = binary("mul", Val::Int(2i64), e.get("PT_PER_MM")?)?;
    e.set("SCALE", assigned28.clone())?;
    let assigned29 = {
        let mut s = Vec::new();
        s.push(Val::Int(300i64));
        s.push(Val::Int(650i64));
        Val::tuple(s)
    };
    let unpack30 = unpack(assigned29.clone(), 2)?;
    e.set("CX", unpack30[0].clone())?;
    e.set("SEAT", unpack30[1].clone())?;
    let assigned31 = Val::Float(0.1f64);
    e.set("CAP_OFFSET_MAX", assigned31.clone())?;
    let assigned32 = Val::Float(0.2f64);
    e.set("JET_OFFSET_MAX", assigned32.clone())?;
    let assigned33 = Val::Str("A".into());
    e.set("REVISION", assigned33.clone())?;
    let assigned34 = Val::Str("HSM-000338".into());
    e.set("MATERIAL_ID", assigned34.clone())?;
    let assigned35 = binary(
        "sub",
        unary("neg", e.get("carbonator")?.attr("ELBOW_AXIS_OFFSET")?)?,
        e.get("fitting")?.attr("ELBOW_MALE_LEN")?,
    )?;
    e.set("CORNER_Z", assigned35.clone())?;
    let assigned36 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("assembly-upper".into()));
            s.push(Val::Int(35i64));
            s.push(Val::Int(565i64));
            s.push(Val::Int(665i64));
            s.push(Val::Int(756i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("assembly-lower".into()));
            s.push(Val::Int(155i64));
            s.push(Val::Int(407i64));
            s.push(Val::Int(687i64));
            s.push(Val::Int(575i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("exit-view".into()));
            s.push(Val::Int(175i64));
            s.push(Val::Int(195i64));
            s.push(Val::Int(673i64));
            s.push(Val::Int(377i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("joint-detail".into()));
            s.push(Val::Int(681i64));
            s.push(Val::Int(519i64));
            s.push(Val::Int(1191i64));
            s.push(Val::Int(756i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("assembly-parts".into()));
            s.push(Val::Int(700i64));
            s.push(Val::Int(390i64));
            s.push(Val::Int(1190i64));
            s.push(Val::Int(520i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("requirements".into()));
            s.push(Val::Int(700i64));
            s.push(Val::Int(166i64));
            s.push(Val::Int(1190i64));
            s.push(Val::Int(390i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("release-and-footer".into()));
            s.push(Val::Int(35i64));
            s.push(Val::Int(27i64));
            s.push(Val::Int(629i64));
            s.push(Val::Int(178i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("title-block".into()));
            s.push(Val::Int(630i64));
            s.push(Val::Int(27i64));
            s.push(Val::Int(1197i64));
            s.push(Val::Int(146i64));
            Val::tuple(s)
        });
        Val::list(s)
    };
    e.set("REVIEW_REGIONS", assigned36.clone())?;
    // section_material
    e.set("section_material", {
        let params = vec![
            ("c".into(), None, false),
            ("points".into(), None, false),
            ("reverse".into(), Some(Val::Bool(false)), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned37 = {
                let fun40 = e.get("path_from_points")?;
                let mut args38 = Vec::new();
                let mut kw39 = Vec::new();
                args38.push(e.get("c")?);
                args38.push(e.get("points")?);
                fun40.call(args38, kw39)?
            };
            e.set("p", assigned37.clone())?;
            let assigned41 = {
                let fun44 = e.get("zip")?;
                let mut args42 = Vec::new();
                let mut kw43 = Vec::new();
                args42.extend(e.get("points")?.iter()?);
                fun44.call(args42, kw43)?
            };
            let unpack45 = unpack(assigned41.clone(), 2)?;
            e.set("xs", unpack45[0].clone())?;
            e.set("ys", unpack45[1].clone())?;
            if e.get("reverse")?.truthy()? {
                let assigned46 = {
                    let mut s = Vec::new();
                    s.push({
                        let fun49 = e.get("min")?;
                        let mut args47 = Vec::new();
                        let mut kw48 = Vec::new();
                        args47.push(e.get("ys")?);
                        fun49.call(args47, kw48)?
                    });
                    s.push({
                        let fun52 = e.get("max")?;
                        let mut args50 = Vec::new();
                        let mut kw51 = Vec::new();
                        args50.push(e.get("ys")?);
                        fun52.call(args50, kw51)?
                    });
                    Val::tuple(s)
                };
                let unpack53 = unpack(assigned46.clone(), 2)?;
                e.set("low", unpack53[0].clone())?;
                e.set("high", unpack53[1].clone())?;
                {
                    let fun56 = e.get("c")?.attr("saveState")?;
                    let mut args54 = Vec::new();
                    let mut kw55 = Vec::new();
                    fun56.call(args54, kw55)?
                };
                {
                    let fun59 = e.get("c")?.attr("translate")?;
                    let mut args57 = Vec::new();
                    let mut kw58 = Vec::new();
                    args57.push(Val::Int(0i64));
                    args57.push(binary("add", e.get("low")?, e.get("high")?)?);
                    fun59.call(args57, kw58)?
                };
                {
                    let fun62 = e.get("c")?.attr("scale")?;
                    let mut args60 = Vec::new();
                    let mut kw61 = Vec::new();
                    args60.push(Val::Int(1i64));
                    args60.push(unary("neg", Val::Int(1i64))?);
                    fun62.call(args60, kw61)?
                };
                let assigned63 = {
                    let fun66 = e.get("path_from_points")?;
                    let mut args64 = Vec::new();
                    let mut kw65 = Vec::new();
                    args64.push(e.get("c")?);
                    args64.push({
                        let e = e.child();
                        let out67 = Val::list(vec![]);
                        for item68 in e.get("points")?.iter()? {
                            let unpack69 = unpack(item68, 2)?;
                            e.set("x", unpack69[0].clone())?;
                            e.set("y", unpack69[1].clone())?;
                            out67.attr("append")?.call(
                                vec![{
                                    let mut s = Vec::new();
                                    s.push(e.get("x")?);
                                    s.push(binary(
                                        "sub",
                                        binary("add", e.get("low")?, e.get("high")?)?,
                                        e.get("y")?,
                                    )?);
                                    Val::tuple(s)
                                }],
                                vec![],
                            )?;
                        }
                        out67
                    });
                    fun66.call(args64, kw65)?
                };
                e.set("mirrored", assigned63.clone())?;
                {
                    let fun72 = e.get("hatch")?;
                    let mut args70 = Vec::new();
                    let mut kw71 = Vec::new();
                    args70.push(e.get("c")?);
                    args70.push(e.get("mirrored")?);
                    args70.push({
                        let mut s = Vec::new();
                        s.push({
                            let fun75 = e.get("min")?;
                            let mut args73 = Vec::new();
                            let mut kw74 = Vec::new();
                            args73.push(e.get("xs")?);
                            fun75.call(args73, kw74)?
                        });
                        s.push(e.get("low")?);
                        s.push({
                            let fun78 = e.get("max")?;
                            let mut args76 = Vec::new();
                            let mut kw77 = Vec::new();
                            args76.push(e.get("xs")?);
                            fun78.call(args76, kw77)?
                        });
                        s.push(e.get("high")?);
                        Val::tuple(s)
                    });
                    kw71.push(("spacing".into(), Val::Int(6i64)));
                    fun72.call(args70, kw71)?
                };
                {
                    let fun81 = e.get("c")?.attr("restoreState")?;
                    let mut args79 = Vec::new();
                    let mut kw80 = Vec::new();
                    fun81.call(args79, kw80)?
                };
            } else {
                {
                    let fun84 = e.get("hatch")?;
                    let mut args82 = Vec::new();
                    let mut kw83 = Vec::new();
                    args82.push(e.get("c")?);
                    args82.push(e.get("p")?);
                    args82.push({
                        let mut s = Vec::new();
                        s.push({
                            let fun87 = e.get("min")?;
                            let mut args85 = Vec::new();
                            let mut kw86 = Vec::new();
                            args85.push(e.get("xs")?);
                            fun87.call(args85, kw86)?
                        });
                        s.push({
                            let fun90 = e.get("min")?;
                            let mut args88 = Vec::new();
                            let mut kw89 = Vec::new();
                            args88.push(e.get("ys")?);
                            fun90.call(args88, kw89)?
                        });
                        s.push({
                            let fun93 = e.get("max")?;
                            let mut args91 = Vec::new();
                            let mut kw92 = Vec::new();
                            args91.push(e.get("xs")?);
                            fun93.call(args91, kw92)?
                        });
                        s.push({
                            let fun96 = e.get("max")?;
                            let mut args94 = Vec::new();
                            let mut kw95 = Vec::new();
                            args94.push(e.get("ys")?);
                            fun96.call(args94, kw95)?
                        });
                        Val::tuple(s)
                    });
                    kw83.push(("spacing".into(), Val::Int(6i64)));
                    fun84.call(args82, kw83)?
                };
            }
            {
                let fun99 = e.get("c")?.attr("setLineWidth")?;
                let mut args97 = Vec::new();
                let mut kw98 = Vec::new();
                args97.push(e.get("VISIBLE")?);
                fun99.call(args97, kw98)?
            };
            {
                let fun102 = e.get("c")?.attr("drawPath")?;
                let mut args100 = Vec::new();
                let mut kw101 = Vec::new();
                args100.push(e.get("p")?);
                kw101.push(("stroke".into(), Val::Int(1i64)));
                kw101.push(("fill".into(), Val::Int(0i64)));
                fun102.call(args100, kw101)?
            };
            Ok(Val::None)
        })
    })?;
    // fusion_bands
    e.set("fusion_bands", {
        let params = vec![
            ("c".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("scale".into(), None, false),
            ("half_height".into(), None, true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned103 = {
                let mut s = Vec::new();
                s.push(binary(
                    "truediv",
                    e.get("fitting")?.attr("ELBOW_BORE")?,
                    Val::Int(2i64),
                )?);
                s.push(binary("truediv", e.get("JET_CAP_D")?, Val::Int(2i64))?);
                Val::tuple(s)
            };
            let unpack104 = unpack(assigned103.clone(), 2)?;
            e.set("inside", unpack104[0].clone())?;
            e.set("outside", unpack104[1].clone())?;
            {
                let fun107 = e.get("c")?.attr("setFillColorRGB")?;
                let mut args105 = Vec::new();
                let mut kw106 = Vec::new();
                args105.push(Val::Float(0.78f64));
                args105.push(Val::Float(0.78f64));
                args105.push(Val::Float(0.78f64));
                fun107.call(args105, kw106)?
            };
            for item108 in {
                let mut s = Vec::new();
                s.push(unary("neg", Val::Int(1i64))?);
                s.push(Val::Int(1i64));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("sign", item108)?;
                let assigned109 = {
                    let fun112 = e.get("sorted")?;
                    let mut args110 = Vec::new();
                    let mut kw111 = Vec::new();
                    args110.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            e.get("x")?,
                            binary(
                                "mul",
                                binary("mul", e.get("sign")?, e.get("inside")?)?,
                                e.get("scale")?,
                            )?,
                        )?);
                        s.push(binary(
                            "add",
                            e.get("x")?,
                            binary(
                                "mul",
                                binary("mul", e.get("sign")?, e.get("outside")?)?,
                                e.get("scale")?,
                            )?,
                        )?);
                        Val::tuple(s)
                    });
                    fun112.call(args110, kw111)?
                };
                let unpack113 = unpack(assigned109.clone(), 2)?;
                e.set("a", unpack113[0].clone())?;
                e.set("b", unpack113[1].clone())?;
                {
                    let fun116 = e.get("c")?.attr("rect")?;
                    let mut args114 = Vec::new();
                    let mut kw115 = Vec::new();
                    args114.push(e.get("a")?);
                    args114.push(binary("sub", e.get("y")?, e.get("half_height")?)?);
                    args114.push(binary("sub", e.get("b")?, e.get("a")?)?);
                    args114.push(binary("mul", Val::Int(2i64), e.get("half_height")?)?);
                    kw115.push(("stroke".into(), Val::Int(0i64)));
                    kw115.push(("fill".into(), Val::Int(1i64)));
                    fun116.call(args114, kw115)?
                };
            }
            {
                let fun119 = e.get("c")?.attr("setFillColorRGB")?;
                let mut args117 = Vec::new();
                let mut kw118 = Vec::new();
                args117.push(Val::Int(0i64));
                args117.push(Val::Int(0i64));
                args117.push(Val::Int(0i64));
                fun119.call(args117, kw118)?
            };
            Ok(Val::None)
        })
    })?;
    // balloon
    e.set("balloon", {
        let params = vec![
            ("c".into(), None, false),
            ("value".into(), None, false),
            ("at".into(), None, false),
            ("target".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned120 = Val::Int(10i64);
            e.set("radius", assigned120.clone())?;
            let assigned121 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("target")?.get(Val::Int(0i64))?,
                    e.get("at")?.get(Val::Int(0i64))?,
                )?);
                s.push(binary(
                    "sub",
                    e.get("target")?.get(Val::Int(1i64))?,
                    e.get("at")?.get(Val::Int(1i64))?,
                )?);
                Val::tuple(s)
            };
            let unpack122 = unpack(assigned121.clone(), 2)?;
            e.set("dx", unpack122[0].clone())?;
            e.set("dy", unpack122[1].clone())?;
            let assigned123 = {
                let fun126 = e.get("math")?.attr("hypot")?;
                let mut args124 = Vec::new();
                let mut kw125 = Vec::new();
                args124.push(e.get("dx")?);
                args124.push(e.get("dy")?);
                fun126.call(args124, kw125)?
            };
            e.set("distance", assigned123.clone())?;
            let assigned127 = {
                let mut s = Vec::new();
                s.push(binary(
                    "add",
                    e.get("at")?.get(Val::Int(0i64))?,
                    binary(
                        "truediv",
                        binary("mul", e.get("radius")?, e.get("dx")?)?,
                        e.get("distance")?,
                    )?,
                )?);
                s.push(binary(
                    "add",
                    e.get("at")?.get(Val::Int(1i64))?,
                    binary(
                        "truediv",
                        binary("mul", e.get("radius")?, e.get("dy")?)?,
                        e.get("distance")?,
                    )?,
                )?);
                Val::tuple(s)
            };
            e.set("start", assigned127.clone())?;
            {
                let fun130 = e.get("line")?;
                let mut args128 = Vec::new();
                let mut kw129 = Vec::new();
                args128.push(e.get("c")?);
                args128.extend(e.get("start")?.iter()?);
                args128.extend(e.get("target")?.iter()?);
                fun130.call(args128, kw129)?
            };
            {
                let fun133 = e.get("arrow")?;
                let mut args131 = Vec::new();
                let mut kw132 = Vec::new();
                args131.push(e.get("c")?);
                args131.push(e.get("target")?);
                args131.push(e.get("start")?);
                fun133.call(args131, kw132)?
            };
            {
                let fun136 = e.get("c")?.attr("setLineWidth")?;
                let mut args134 = Vec::new();
                let mut kw135 = Vec::new();
                args134.push(Val::Float(0.6f64));
                fun136.call(args134, kw135)?
            };
            {
                let fun139 = e.get("c")?.attr("circle")?;
                let mut args137 = Vec::new();
                let mut kw138 = Vec::new();
                args137.extend(e.get("at")?.iter()?);
                args137.push(e.get("radius")?);
                kw138.push(("stroke".into(), Val::Int(1i64)));
                kw138.push(("fill".into(), Val::Int(0i64)));
                fun139.call(args137, kw138)?
            };
            {
                let fun142 = e.get("text")?;
                let mut args140 = Vec::new();
                let mut kw141 = Vec::new();
                args140.push(e.get("c")?);
                args140.push(e.get("at")?.get(Val::Int(0i64))?);
                args140.push(binary(
                    "sub",
                    e.get("at")?.get(Val::Int(1i64))?,
                    Val::Int(3i64),
                )?);
                args140.push({
                    let fun145 = e.get("str")?;
                    let mut args143 = Vec::new();
                    let mut kw144 = Vec::new();
                    args143.push(e.get("value")?);
                    fun145.call(args143, kw144)?
                });
                args140.push(Val::Int(9i64));
                kw141.push(("bold".into(), Val::Bool(true)));
                kw141.push(("align".into(), Val::Str("center".into())));
                fun142.call(args140, kw141)?
            };
            Ok(Val::None)
        })
    })?;
    // assembly_view
    e.set("assembly_view", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun148 = e.get("text")?;
                let mut args146 = Vec::new();
                let mut kw147 = Vec::new();
                args146.push(e.get("c")?);
                args146.push(e.get("CX")?);
                args146.push(Val::Int(735i64));
                args146.push(Val::Str("WATER-INLET JET ELBOW".into()));
                args146.push(Val::Int(12i64));
                kw147.push(("bold".into(), Val::Bool(true)));
                kw147.push(("align".into(), Val::Str("center".into())));
                fun148.call(args146, kw147)?
            };
            {
                let fun151 = e.get("text")?;
                let mut args149 = Vec::new();
                let mut kw150 = Vec::new();
                args149.push(e.get("c")?);
                args149.push(e.get("CX")?);
                args149.push(Val::Int(718i64));
                args149.push(Val::Str(
                    "SIDE VIEW - SCALE 2:1 - HIDDEN DETAIL OMITTED".into(),
                ));
                args149.push(Val::Int(9i64));
                kw150.push(("align".into(), Val::Str("center".into())));
                fun151.call(args149, kw150)?
            };
            let assigned152 = binary("truediv", e.get("fitting")?.attr("ELBOW_HEX_AF")?, {
                let fun155 = e.get("math")?.attr("sqrt")?;
                let mut args153 = Vec::new();
                let mut kw154 = Vec::new();
                args153.push(Val::Int(3i64));
                fun155.call(args153, kw154)?
            })?;
            e.set("r", assigned152.clone())?;
            let assigned156 = {
                let mut s = Vec::new();
                s.push(e.get("fitting")?.attr("ELBOW_MALE_R")?);
                s.push(unary("neg", e.get("fitting")?.attr("ELBOW_MALE_LEN")?)?);
                s.push(e.get("fitting")?.attr("ELBOW_LEG")?);
                Val::tuple(s)
            };
            let unpack157 = unpack(assigned156.clone(), 3)?;
            e.set("male_r", unpack157[0].clone())?;
            e.set("male_base", unpack157[1].clone())?;
            e.set("out", unpack157[2].clone())?;
            let assigned158 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", e.get("r")?)?);
                    s.push(e.get("male_base")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", e.get("r")?)?);
                    s.push(e.get("CORNER_Z")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(e.get("CORNER_Z")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(binary("sub", e.get("CORNER_Z")?, e.get("r")?)?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("out")?);
                    s.push(binary("sub", e.get("CORNER_Z")?, e.get("r")?)?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("out")?);
                    s.push(binary("add", e.get("CORNER_Z")?, e.get("r")?)?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("r")?);
                    s.push(binary("add", e.get("CORNER_Z")?, e.get("r")?)?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("r")?);
                    s.push(e.get("male_base")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("male_r")?);
                    s.push(e.get("male_base")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("male_r")?);
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", e.get("male_r")?)?);
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", e.get("male_r")?)?);
                    s.push(e.get("male_base")?);
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("outline", assigned158.clone())?;
            let assigned159 = {
                let fun162 = e.get("path_from_points")?;
                let mut args160 = Vec::new();
                let mut kw161 = Vec::new();
                args160.push(e.get("c")?);
                args160.push({
                    let e = e.child();
                    let out163 = Val::list(vec![]);
                    for item164 in e.get("outline")?.iter()? {
                        let unpack165 = unpack(item164, 2)?;
                        e.set("x", unpack165[0].clone())?;
                        e.set("z", unpack165[1].clone())?;
                        out163.attr("append")?.call(
                            vec![{
                                let mut s = Vec::new();
                                s.push(binary(
                                    "add",
                                    e.get("CX")?,
                                    binary("mul", e.get("x")?, e.get("SCALE")?)?,
                                )?);
                                s.push(binary(
                                    "add",
                                    e.get("SEAT")?,
                                    binary("mul", e.get("z")?, e.get("SCALE")?)?,
                                )?);
                                Val::tuple(s)
                            }],
                            vec![],
                        )?;
                    }
                    out163
                });
                fun162.call(args160, kw161)?
            };
            e.set("p", assigned159.clone())?;
            {
                let fun168 = e.get("c")?.attr("setLineWidth")?;
                let mut args166 = Vec::new();
                let mut kw167 = Vec::new();
                args166.push(e.get("VISIBLE")?);
                fun168.call(args166, kw167)?
            };
            {
                let fun171 = e.get("c")?.attr("drawPath")?;
                let mut args169 = Vec::new();
                let mut kw170 = Vec::new();
                args169.push(e.get("p")?);
                kw170.push(("stroke".into(), Val::Int(1i64)));
                kw170.push(("fill".into(), Val::Int(0i64)));
                fun171.call(args169, kw170)?
            };
            for item172 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "truediv",
                        unary("neg", e.get("r")?)?,
                        Val::Int(2i64),
                    )?);
                    s.push(e.get("CORNER_Z")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("truediv", e.get("r")?, Val::Int(2i64))?);
                    s.push(binary("add", e.get("CORNER_Z")?, e.get("r")?)?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack176 = unpack(item172, 2)?;
                e.set("x", unpack176[0].clone())?;
                e.set("end_z", unpack176[1].clone())?;
                {
                    let fun175 = e.get("line")?;
                    let mut args173 = Vec::new();
                    let mut kw174 = Vec::new();
                    args173.push(e.get("c")?);
                    args173.push(binary(
                        "add",
                        e.get("CX")?,
                        binary("mul", e.get("x")?, e.get("SCALE")?)?,
                    )?);
                    args173.push(binary(
                        "add",
                        e.get("SEAT")?,
                        binary("mul", e.get("male_base")?, e.get("SCALE")?)?,
                    )?);
                    args173.push(binary(
                        "add",
                        e.get("CX")?,
                        binary("mul", e.get("x")?, e.get("SCALE")?)?,
                    )?);
                    args173.push(binary(
                        "add",
                        e.get("SEAT")?,
                        binary("mul", e.get("end_z")?, e.get("SCALE")?)?,
                    )?);
                    args173.push(e.get("THIN")?);
                    fun175.call(args173, kw174)?
                };
            }
            {
                let fun179 = e.get("line")?;
                let mut args177 = Vec::new();
                let mut kw178 = Vec::new();
                args177.push(e.get("c")?);
                args177.push(binary(
                    "add",
                    e.get("CX")?,
                    binary("mul", e.get("r")?, e.get("SCALE")?)?,
                )?);
                args177.push(binary(
                    "add",
                    e.get("SEAT")?,
                    binary(
                        "mul",
                        binary(
                            "add",
                            e.get("CORNER_Z")?,
                            binary("truediv", e.get("r")?, Val::Int(2i64))?,
                        )?,
                        e.get("SCALE")?,
                    )?,
                )?);
                args177.push(binary(
                    "add",
                    e.get("CX")?,
                    binary("mul", e.get("out")?, e.get("SCALE")?)?,
                )?);
                args177.push(binary(
                    "add",
                    e.get("SEAT")?,
                    binary(
                        "mul",
                        binary(
                            "add",
                            e.get("CORNER_Z")?,
                            binary("truediv", e.get("r")?, Val::Int(2i64))?,
                        )?,
                        e.get("SCALE")?,
                    )?,
                )?);
                args177.push(e.get("THIN")?);
                fun179.call(args177, kw178)?
            };
            let assigned180 = binary(
                "truediv",
                binary("mul", e.get("JET_CAP_D")?, e.get("SCALE")?)?,
                Val::Int(2i64),
            )?;
            e.set("cap_r", assigned180.clone())?;
            {
                let fun183 = e.get("c")?.attr("setLineWidth")?;
                let mut args181 = Vec::new();
                let mut kw182 = Vec::new();
                args181.push(e.get("VISIBLE")?);
                fun183.call(args181, kw182)?
            };
            {
                let fun186 = e.get("c")?.attr("rect")?;
                let mut args184 = Vec::new();
                let mut kw185 = Vec::new();
                args184.push(binary("sub", e.get("CX")?, e.get("cap_r")?)?);
                args184.push(e.get("SEAT")?);
                args184.push(binary("mul", Val::Int(2i64), e.get("cap_r")?)?);
                args184.push(binary("mul", e.get("JET_CAP_T")?, e.get("SCALE")?)?);
                kw185.push(("stroke".into(), Val::Int(1i64)));
                kw185.push(("fill".into(), Val::Int(0i64)));
                fun186.call(args184, kw185)?
            };
            let assigned187 = e.get("r")?;
            e.set("left", assigned187.clone())?;
            let assigned188 = binary("sub", e.get("CORNER_Z")?, e.get("r")?)?;
            e.set("bottom", assigned188.clone())?;
            {
                let fun191 = e.get("line")?;
                let mut args189 = Vec::new();
                let mut kw190 = Vec::new();
                args189.push(e.get("c")?);
                args189.push(e.get("CX")?);
                args189.push(binary(
                    "sub",
                    binary(
                        "add",
                        e.get("SEAT")?,
                        binary("mul", e.get("bottom")?, e.get("SCALE")?)?,
                    )?,
                    Val::Int(12i64),
                )?);
                args189.push(e.get("CX")?);
                args189.push(binary(
                    "add",
                    binary(
                        "add",
                        e.get("SEAT")?,
                        binary("mul", e.get("JET_CAP_T")?, e.get("SCALE")?)?,
                    )?,
                    Val::Int(14i64),
                )?);
                kw190.push(("dash".into(), e.get("CENTER_DASH")?));
                fun191.call(args189, kw190)?
            };
            let assigned192 = binary(
                "add",
                e.get("SEAT")?,
                binary("mul", e.get("CORNER_Z")?, e.get("SCALE")?)?,
            )?;
            e.set("axis_y", assigned192.clone())?;
            {
                let fun195 = e.get("line")?;
                let mut args193 = Vec::new();
                let mut kw194 = Vec::new();
                args193.push(e.get("c")?);
                args193.push(binary("sub", e.get("CX")?, Val::Int(12i64))?);
                args193.push(e.get("axis_y")?);
                args193.push(binary(
                    "add",
                    binary(
                        "add",
                        e.get("CX")?,
                        binary("mul", e.get("fitting")?.attr("ELBOW_LEG")?, e.get("SCALE")?)?,
                    )?,
                    Val::Int(15i64),
                )?);
                args193.push(e.get("axis_y")?);
                kw194.push(("dash".into(), e.get("CENTER_DASH")?));
                fun195.call(args193, kw194)?
            };
            {
                let fun198 = e.get("leader")?;
                let mut args196 = Vec::new();
                let mut kw197 = Vec::new();
                args196.push(e.get("c")?);
                args196.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        e.get("CX")?,
                        binary(
                            "truediv",
                            binary("mul", e.get("JET_CAP_D")?, e.get("SCALE")?)?,
                            Val::Int(2i64),
                        )?,
                    )?);
                    s.push(e.get("SEAT")?);
                    Val::tuple(s)
                });
                args196.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(207i64));
                    s.push(Val::Int(692i64));
                    Val::tuple(s)
                });
                args196.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(184i64));
                    s.push(Val::Int(692i64));
                    Val::tuple(s)
                });
                args196.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("W1 - CONTINUOUS 360° WELD".into()));
                    s.push(Val::Str("FULL WETTED-ROOT FUSION".into()));
                    Val::list(s)
                });
                args196.push(Val::Float(9.5f64));
                fun198.call(args196, kw197)?
            };
            {
                let fun201 = e.get("leader")?;
                let mut args199 = Vec::new();
                let mut kw200 = Vec::new();
                args199.push(e.get("c")?);
                args199.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("CX")?,
                        binary(
                            "mul",
                            e.get("fitting")?.attr("ELBOW_MALE_R")?,
                            e.get("SCALE")?,
                        )?,
                    )?);
                    s.push(binary(
                        "sub",
                        e.get("SEAT")?,
                        binary("mul", Val::Int(3i64), e.get("SCALE")?)?,
                    )?);
                    Val::tuple(s)
                });
                args199.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(452i64));
                    s.push(Val::Int(674i64));
                    Val::tuple(s)
                });
                args199.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(473i64));
                    s.push(Val::Int(674i64));
                    Val::tuple(s)
                });
                args199.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("1/4-18 NPT MALE".into()));
                    s.push(Val::Str("AS RECEIVED".into()));
                    Val::list(s)
                });
                args199.push(Val::Float(9.5f64));
                fun201.call(args199, kw200)?
            };
            {
                let fun204 = e.get("leader")?;
                let mut args202 = Vec::new();
                let mut kw203 = Vec::new();
                args202.push(e.get("c")?);
                args202.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("CX")?,
                        binary("mul", e.get("fitting")?.attr("ELBOW_LEG")?, e.get("SCALE")?)?,
                    )?);
                    s.push(binary(
                        "add",
                        e.get("axis_y")?,
                        binary("mul", e.get("fitting")?.attr("SOCKET_R")?, e.get("SCALE")?)?,
                    )?);
                    Val::tuple(s)
                });
                args202.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(500i64));
                    s.push(Val::Int(555i64));
                    Val::tuple(s)
                });
                args202.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(522i64));
                    s.push(Val::Int(555i64));
                    Val::tuple(s)
                });
                args202.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("1/4-18 NPT FEMALE".into()));
                    s.push(Val::Str("AS RECEIVED".into()));
                    Val::list(s)
                });
                args202.push(Val::Float(9.5f64));
                fun204.call(args202, kw203)?
            };
            {
                let fun207 = e.get("balloon")?;
                let mut args205 = Vec::new();
                let mut kw206 = Vec::new();
                args205.push(e.get("c")?);
                args205.push(Val::Int(1i64));
                args205.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(177i64));
                    s.push(Val::Int(513i64));
                    Val::tuple(s)
                });
                args205.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        e.get("CX")?,
                        binary("mul", e.get("left")?, e.get("SCALE")?)?,
                    )?);
                    s.push(binary(
                        "sub",
                        e.get("SEAT")?,
                        binary("mul", Val::Int(18i64), e.get("SCALE")?)?,
                    )?);
                    Val::tuple(s)
                });
                fun207.call(args205, kw206)?
            };
            {
                let fun210 = e.get("balloon")?;
                let mut args208 = Vec::new();
                let mut kw209 = Vec::new();
                args208.push(e.get("c")?);
                args208.push(Val::Int(2i64));
                args208.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(370i64));
                    s.push(Val::Int(697i64));
                    Val::tuple(s)
                });
                args208.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("CX")?, Val::Int(10i64))?);
                    s.push(binary(
                        "add",
                        e.get("SEAT")?,
                        binary("mul", e.get("JET_CAP_T")?, e.get("SCALE")?)?,
                    )?);
                    Val::tuple(s)
                });
                fun210.call(args208, kw209)?
            };
            Ok(Val::None)
        })
    })?;
    // exit_view
    e.set("exit_view", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned211 = {
                let mut s = Vec::new();
                s.push(e.get("CX")?);
                s.push(Val::Int(270i64));
                Val::tuple(s)
            };
            let unpack212 = unpack(assigned211.clone(), 2)?;
            e.set("x", unpack212[0].clone())?;
            e.set("y", unpack212[1].clone())?;
            let assigned213 = binary("truediv", e.get("fitting")?.attr("ELBOW_HEX_AF")?, {
                let fun216 = e.get("math")?.attr("sqrt")?;
                let mut args214 = Vec::new();
                let mut kw215 = Vec::new();
                args214.push(Val::Int(3i64));
                fun216.call(args214, kw215)?
            })?;
            e.set("r", assigned213.clone())?;
            let assigned217 = {
                let e = e.child();
                let out218 = Val::list(vec![]);
                for item219 in {
                    let fun222 = e.get("range")?;
                    let mut args220 = Vec::new();
                    let mut kw221 = Vec::new();
                    args220.push(Val::Int(6i64));
                    fun222.call(args220, kw221)?
                }
                .iter()?
                {
                    e.set("i", item219)?;
                    out218.attr("append")?.call(
                        vec![{
                            let mut s = Vec::new();
                            s.push(binary(
                                "add",
                                e.get("x")?,
                                binary("mul", binary("mul", e.get("r")?, e.get("SCALE")?)?, {
                                    let fun225 = e.get("math")?.attr("cos")?;
                                    let mut args223 = Vec::new();
                                    let mut kw224 = Vec::new();
                                    args223.push({
                                        let fun228 = e.get("math")?.attr("radians")?;
                                        let mut args226 = Vec::new();
                                        let mut kw227 = Vec::new();
                                        args226.push(binary("mul", Val::Int(60i64), e.get("i")?)?);
                                        fun228.call(args226, kw227)?
                                    });
                                    fun225.call(args223, kw224)?
                                })?,
                            )?);
                            s.push(binary(
                                "add",
                                e.get("y")?,
                                binary("mul", binary("mul", e.get("r")?, e.get("SCALE")?)?, {
                                    let fun231 = e.get("math")?.attr("sin")?;
                                    let mut args229 = Vec::new();
                                    let mut kw230 = Vec::new();
                                    args229.push({
                                        let fun234 = e.get("math")?.attr("radians")?;
                                        let mut args232 = Vec::new();
                                        let mut kw233 = Vec::new();
                                        args232.push(binary("mul", Val::Int(60i64), e.get("i")?)?);
                                        fun234.call(args232, kw233)?
                                    });
                                    fun231.call(args229, kw230)?
                                })?,
                            )?);
                            Val::tuple(s)
                        }],
                        vec![],
                    )?;
                }
                out218
            };
            e.set("pts", assigned217.clone())?;
            {
                let fun237 = e.get("text")?;
                let mut args235 = Vec::new();
                let mut kw236 = Vec::new();
                args235.push(e.get("c")?);
                args235.push(e.get("x")?);
                args235.push(Val::Int(360i64));
                args235.push(Val::Str("JET EXIT END VIEW".into()));
                args235.push(Val::Int(12i64));
                kw236.push(("bold".into(), Val::Bool(true)));
                kw236.push(("align".into(), Val::Str("center".into())));
                fun237.call(args235, kw236)?
            };
            {
                let fun240 = e.get("text")?;
                let mut args238 = Vec::new();
                let mut kw239 = Vec::new();
                args238.push(e.get("c")?);
                args238.push(e.get("x")?);
                args238.push(Val::Int(344i64));
                args238.push(Val::Str("LOOKING ALONG MALE PORT AXIS - SCALE 2:1".into()));
                args238.push(Val::Float(8.5f64));
                kw239.push(("align".into(), Val::Str("center".into())));
                fun240.call(args238, kw239)?
            };
            {
                let fun243 = e.get("c")?.attr("setLineWidth")?;
                let mut args241 = Vec::new();
                let mut kw242 = Vec::new();
                args241.push(e.get("VISIBLE")?);
                fun243.call(args241, kw242)?
            };
            {
                let fun246 = e.get("c")?.attr("drawPath")?;
                let mut args244 = Vec::new();
                let mut kw245 = Vec::new();
                args244.push({
                    let fun249 = e.get("path_from_points")?;
                    let mut args247 = Vec::new();
                    let mut kw248 = Vec::new();
                    args247.push(e.get("c")?);
                    args247.push(e.get("pts")?);
                    fun249.call(args247, kw248)?
                });
                kw245.push(("stroke".into(), Val::Int(1i64)));
                kw245.push(("fill".into(), Val::Int(0i64)));
                fun246.call(args244, kw245)?
            };
            let assigned250 = binary(
                "truediv",
                binary(
                    "mul",
                    e.get("fitting")?.attr("ELBOW_HEX_AF")?,
                    e.get("SCALE")?,
                )?,
                Val::Int(2i64),
            )?;
            e.set("half_w", assigned250.clone())?;
            let assigned251 = binary(
                "add",
                e.get("x")?,
                binary(
                    "truediv",
                    binary("mul", e.get("r")?, e.get("SCALE")?)?,
                    Val::Int(2i64),
                )?,
            )?;
            e.set("upper_x", assigned251.clone())?;
            let assigned252 = binary(
                "add",
                e.get("x")?,
                binary("mul", e.get("fitting")?.attr("ELBOW_LEG")?, e.get("SCALE")?)?,
            )?;
            e.set("end_x", assigned252.clone())?;
            {
                let fun255 = e.get("line")?;
                let mut args253 = Vec::new();
                let mut kw254 = Vec::new();
                args253.push(e.get("c")?);
                args253.push(e.get("upper_x")?);
                args253.push(binary("add", e.get("y")?, e.get("half_w")?)?);
                args253.push(e.get("end_x")?);
                args253.push(binary("add", e.get("y")?, e.get("half_w")?)?);
                args253.push(e.get("VISIBLE")?);
                fun255.call(args253, kw254)?
            };
            {
                let fun258 = e.get("line")?;
                let mut args256 = Vec::new();
                let mut kw257 = Vec::new();
                args256.push(e.get("c")?);
                args256.push(e.get("end_x")?);
                args256.push(binary("add", e.get("y")?, e.get("half_w")?)?);
                args256.push(e.get("end_x")?);
                args256.push(binary("sub", e.get("y")?, e.get("half_w")?)?);
                args256.push(e.get("VISIBLE")?);
                fun258.call(args256, kw257)?
            };
            {
                let fun261 = e.get("line")?;
                let mut args259 = Vec::new();
                let mut kw260 = Vec::new();
                args259.push(e.get("c")?);
                args259.push(e.get("end_x")?);
                args259.push(binary("sub", e.get("y")?, e.get("half_w")?)?);
                args259.push(e.get("upper_x")?);
                args259.push(binary("sub", e.get("y")?, e.get("half_w")?)?);
                args259.push(e.get("VISIBLE")?);
                fun261.call(args259, kw260)?
            };
            {
                let fun264 = e.get("line")?;
                let mut args262 = Vec::new();
                let mut kw263 = Vec::new();
                args262.push(e.get("c")?);
                args262.push(binary(
                    "add",
                    e.get("x")?,
                    binary("mul", e.get("r")?, e.get("SCALE")?)?,
                )?);
                args262.push(e.get("y")?);
                args262.push(e.get("end_x")?);
                args262.push(e.get("y")?);
                args262.push(e.get("VISIBLE")?);
                fun264.call(args262, kw263)?
            };
            for item265 in {
                let mut s = Vec::new();
                s.push(e.get("fitting")?.attr("ELBOW_MALE_R")?);
                s.push(binary("truediv", e.get("JET_CAP_D")?, Val::Int(2i64))?);
                s.push(binary("truediv", e.get("JET_PASSAGE_D")?, Val::Int(2i64))?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("radius", item265)?;
                {
                    let fun268 = e.get("c")?.attr("setLineWidth")?;
                    let mut args266 = Vec::new();
                    let mut kw267 = Vec::new();
                    args266.push(e.get("VISIBLE")?);
                    fun268.call(args266, kw267)?
                };
                {
                    let fun271 = e.get("c")?.attr("circle")?;
                    let mut args269 = Vec::new();
                    let mut kw270 = Vec::new();
                    args269.push(e.get("x")?);
                    args269.push(e.get("y")?);
                    args269.push(binary("mul", e.get("radius")?, e.get("SCALE")?)?);
                    kw270.push(("stroke".into(), Val::Int(1i64)));
                    kw270.push(("fill".into(), Val::Int(0i64)));
                    fun271.call(args269, kw270)?
                };
            }
            {
                let fun274 = e.get("center")?;
                let mut args272 = Vec::new();
                let mut kw273 = Vec::new();
                args272.push(e.get("c")?);
                args272.push(e.get("x")?);
                args272.push(e.get("y")?);
                args272.push(Val::Int(14i64));
                fun274.call(args272, kw273)?
            };
            let assigned275 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    binary(
                        "sub",
                        e.get("x")?,
                        binary("mul", e.get("r")?, e.get("SCALE")?)?,
                    )?,
                    Val::Int(20i64),
                )?);
                s.push(binary("add", e.get("end_x")?, Val::Int(20i64))?);
                Val::tuple(s)
            };
            let unpack276 = unpack(assigned275.clone(), 2)?;
            e.set("left", unpack276[0].clone())?;
            e.set("right", unpack276[1].clone())?;
            {
                let fun279 = e.get("line")?;
                let mut args277 = Vec::new();
                let mut kw278 = Vec::new();
                args277.push(e.get("c")?);
                args277.push(binary("add", e.get("left")?, Val::Int(14i64))?);
                args277.push(e.get("y")?);
                args277.push(binary("sub", e.get("right")?, Val::Int(14i64))?);
                args277.push(e.get("y")?);
                kw278.push(("dash".into(), e.get("CENTER_DASH")?));
                fun279.call(args277, kw278)?
            };
            {
                let fun282 = e.get("cutting_plane_ends")?;
                let mut args280 = Vec::new();
                let mut kw281 = Vec::new();
                args280.push(e.get("c")?);
                args280.push(e.get("left")?);
                args280.push(e.get("right")?);
                args280.push(e.get("y")?);
                args280.push(Val::Str("A".into()));
                kw281.push(("rise".into(), Val::Int(20i64)));
                fun282.call(args280, kw281)?
            };
            {
                let fun285 = e.get("circular_leader")?;
                let mut args283 = Vec::new();
                let mut kw284 = Vec::new();
                args283.push(e.get("c")?);
                args283.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y")?);
                    Val::tuple(s)
                });
                args283.push(binary(
                    "truediv",
                    binary("mul", e.get("JET_PASSAGE_D")?, e.get("SCALE")?)?,
                    Val::Int(2i64),
                )?);
                args283.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(485i64));
                    s.push(Val::Int(355i64));
                    Val::tuple(s)
                });
                args283.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(505i64));
                    s.push(Val::Int(355i64));
                    Val::tuple(s)
                });
                args283.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("JET BORE: JET-CAP-01".into()));
                    s.push(Val::Str("RETAIN LIMITS AFTER WELD".into()));
                    Val::list(s)
                });
                args283.push(Val::Float(9.5f64));
                fun285.call(args283, kw284)?
            };
            {
                let fun288 = e.get("text")?;
                let mut args286 = Vec::new();
                let mut kw287 = Vec::new();
                args286.push(e.get("c")?);
                args286.push(binary("add", e.get("x")?, Val::Int(45i64))?);
                args286.push(Val::Int(207i64));
                args286.push(Val::Str(
                    "FITTING BODY AND THREAD PROFILES ARE SCHEMATIC.".into(),
                ));
                args286.push(Val::Int(8i64));
                kw287.push(("align".into(), Val::Str("center".into())));
                fun288.call(args286, kw287)?
            };
            Ok(Val::None)
        })
    })?;
    // joint_detail
    e.set("joint_detail", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned289 = {
                let mut s = Vec::new();
                s.push(Val::Int(945i64));
                s.push(Val::Int(600i64));
                s.push(binary("mul", Val::Int(5i64), e.get("PT_PER_MM")?)?);
                Val::tuple(s)
            };
            let unpack290 = unpack(assigned289.clone(), 3)?;
            e.set("x", unpack290[0].clone())?;
            e.set("seat", unpack290[1].clone())?;
            e.set("s", unpack290[2].clone())?;
            let assigned291 = {
                let mut s = Vec::new();
                s.push(binary(
                    "truediv",
                    binary("mul", e.get("JET_CAP_D")?, e.get("s")?)?,
                    Val::Int(2i64),
                )?);
                s.push(binary(
                    "truediv",
                    binary("mul", e.get("JET_PASSAGE_D")?, e.get("s")?)?,
                    Val::Int(2i64),
                )?);
                Val::tuple(s)
            };
            let unpack292 = unpack(assigned291.clone(), 2)?;
            e.set("cr", unpack292[0].clone())?;
            e.set("hole", unpack292[1].clone())?;
            let assigned293 = {
                let mut s = Vec::new();
                s.push(binary(
                    "truediv",
                    binary("mul", e.get("fitting")?.attr("ELBOW_BORE")?, e.get("s")?)?,
                    Val::Int(2i64),
                )?);
                s.push(binary(
                    "mul",
                    e.get("fitting")?.attr("ELBOW_MALE_R")?,
                    e.get("s")?,
                )?);
                Val::tuple(s)
            };
            let unpack294 = unpack(assigned293.clone(), 2)?;
            e.set("inner", unpack294[0].clone())?;
            e.set("outer", unpack294[1].clone())?;
            let assigned295 = {
                let mut s = Vec::new();
                s.push(binary(
                    "add",
                    e.get("seat")?,
                    binary("mul", e.get("JET_CAP_T")?, e.get("s")?)?,
                )?);
                s.push(Val::Int(550i64));
                Val::tuple(s)
            };
            let unpack296 = unpack(assigned295.clone(), 2)?;
            e.set("top", unpack296[0].clone())?;
            e.set("bottom", unpack296[1].clone())?;
            {
                let fun299 = e.get("text")?;
                let mut args297 = Vec::new();
                let mut kw298 = Vec::new();
                args297.push(e.get("c")?);
                args297.push(e.get("x")?);
                args297.push(Val::Int(735i64));
                args297.push(Val::Str("SECTION A-A - CAP-TO-ELBOW JOINT".into()));
                args297.push(Val::Int(11i64));
                kw298.push(("bold".into(), Val::Bool(true)));
                kw298.push(("align".into(), Val::Str("center".into())));
                fun299.call(args297, kw298)?
            };
            {
                let fun302 = e.get("text")?;
                let mut args300 = Vec::new();
                let mut kw301 = Vec::new();
                args300.push(e.get("c")?);
                args300.push(e.get("x")?);
                args300.push(Val::Int(718i64));
                args300.push(Val::Str("LOCAL AT MALE TIP - SCALE 5:1".into()));
                args300.push(Val::Int(9i64));
                kw301.push(("align".into(), Val::Str("center".into())));
                fun302.call(args300, kw301)?
            };
            for item303 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("x")?, e.get("outer")?)?);
                    s.push(binary("sub", e.get("x")?, e.get("inner")?)?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("x")?, e.get("inner")?)?);
                    s.push(binary("add", e.get("x")?, e.get("outer")?)?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack308 = unpack(item303, 2)?;
                e.set("a", unpack308[0].clone())?;
                e.set("b", unpack308[1].clone())?;
                let assigned304 = {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("a")?);
                        s.push(e.get("seat")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("b")?);
                        s.push(e.get("seat")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("b")?);
                        s.push(binary("add", e.get("bottom")?, Val::Int(5i64))?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "sub",
                            e.get("b")?,
                            binary(
                                "truediv",
                                binary("sub", e.get("b")?, e.get("a")?)?,
                                Val::Int(3i64),
                            )?,
                        )?);
                        s.push(binary("add", e.get("bottom")?, Val::Int(8i64))?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            e.get("a")?,
                            binary(
                                "truediv",
                                binary("sub", e.get("b")?, e.get("a")?)?,
                                Val::Int(3i64),
                            )?,
                        )?);
                        s.push(binary("add", e.get("bottom")?, Val::Int(2i64))?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("a")?);
                        s.push(binary("add", e.get("bottom")?, Val::Int(5i64))?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                };
                e.set("points", assigned304.clone())?;
                {
                    let fun307 = e.get("section_material")?;
                    let mut args305 = Vec::new();
                    let mut kw306 = Vec::new();
                    args305.push(e.get("c")?);
                    args305.push(e.get("points")?);
                    fun307.call(args305, kw306)?
                };
            }
            for item309 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("x")?, e.get("cr")?)?);
                    s.push(binary("sub", e.get("x")?, e.get("hole")?)?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("x")?, e.get("hole")?)?);
                    s.push(binary("add", e.get("x")?, e.get("cr")?)?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack313 = unpack(item309, 2)?;
                e.set("a", unpack313[0].clone())?;
                e.set("b", unpack313[1].clone())?;
                {
                    let fun312 = e.get("section_material")?;
                    let mut args310 = Vec::new();
                    let mut kw311 = Vec::new();
                    args310.push(e.get("c")?);
                    args310.push({
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("a")?);
                            s.push(e.get("seat")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("b")?);
                            s.push(e.get("seat")?);
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
                    kw311.push(("reverse".into(), Val::Bool(true)));
                    fun312.call(args310, kw311)?
                };
            }
            {
                let fun316 = e.get("fusion_bands")?;
                let mut args314 = Vec::new();
                let mut kw315 = Vec::new();
                args314.push(e.get("c")?);
                args314.push(e.get("x")?);
                args314.push(e.get("seat")?);
                args314.push(e.get("s")?);
                kw315.push(("half_height".into(), Val::Int(3i64)));
                fun316.call(args314, kw315)?
            };
            {
                let fun319 = e.get("line")?;
                let mut args317 = Vec::new();
                let mut kw318 = Vec::new();
                args317.push(e.get("c")?);
                args317.push(e.get("x")?);
                args317.push(binary("sub", e.get("bottom")?, Val::Int(3i64))?);
                args317.push(e.get("x")?);
                args317.push(binary("add", e.get("top")?, Val::Int(13i64))?);
                kw318.push(("dash".into(), e.get("CENTER_DASH")?));
                fun319.call(args317, kw318)?
            };
            {
                let fun322 = e.get("horizontal_dimension")?;
                let mut args320 = Vec::new();
                let mut kw321 = Vec::new();
                args320.push(e.get("c")?);
                args320.push(binary("sub", e.get("x")?, e.get("hole")?)?);
                args320.push(binary("add", e.get("x")?, e.get("hole")?)?);
                args320.push(e.get("top")?);
                args320.push(Val::Int(670i64));
                args320.push({
                    let mut str323 = String::new();
                    str323.push_str("Ø");
                    str323.push_str(&format(
                        &e.get("JET_PASSAGE_D")?,
                        &val_string({
                            let mut str324 = String::new();
                            str324.push_str(".4f");
                            Val::Str(str324)
                        })?,
                    )?);
                    str323.push_str(" REF");
                    Val::Str(str323)
                });
                args320.push(Val::Float(9.5f64));
                fun322.call(args320, kw321)?
            };
            let assigned325 = Val::Int(1065i64);
            e.set("dim_x", assigned325.clone())?;
            for item326 in {
                let mut s = Vec::new();
                s.push(e.get("seat")?);
                s.push(e.get("top")?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("y", item326)?;
                {
                    let fun329 = e.get("line")?;
                    let mut args327 = Vec::new();
                    let mut kw328 = Vec::new();
                    args327.push(e.get("c")?);
                    args327.push(binary(
                        "add",
                        binary("add", e.get("x")?, e.get("cr")?)?,
                        Val::Int(4i64),
                    )?);
                    args327.push(e.get("y")?);
                    args327.push(binary("add", e.get("dim_x")?, Val::Int(5i64))?);
                    args327.push(e.get("y")?);
                    fun329.call(args327, kw328)?
                };
            }
            {
                let fun332 = e.get("line")?;
                let mut args330 = Vec::new();
                let mut kw331 = Vec::new();
                args330.push(e.get("c")?);
                args330.push(e.get("dim_x")?);
                args330.push(e.get("seat")?);
                args330.push(e.get("dim_x")?);
                args330.push(e.get("top")?);
                fun332.call(args330, kw331)?
            };
            {
                let fun335 = e.get("arrow")?;
                let mut args333 = Vec::new();
                let mut kw334 = Vec::new();
                args333.push(e.get("c")?);
                args333.push({
                    let mut s = Vec::new();
                    s.push(e.get("dim_x")?);
                    s.push(e.get("seat")?);
                    Val::tuple(s)
                });
                args333.push({
                    let mut s = Vec::new();
                    s.push(e.get("dim_x")?);
                    s.push(e.get("top")?);
                    Val::tuple(s)
                });
                fun335.call(args333, kw334)?
            };
            {
                let fun338 = e.get("arrow")?;
                let mut args336 = Vec::new();
                let mut kw337 = Vec::new();
                args336.push(e.get("c")?);
                args336.push({
                    let mut s = Vec::new();
                    s.push(e.get("dim_x")?);
                    s.push(e.get("top")?);
                    Val::tuple(s)
                });
                args336.push({
                    let mut s = Vec::new();
                    s.push(e.get("dim_x")?);
                    s.push(e.get("seat")?);
                    Val::tuple(s)
                });
                fun338.call(args336, kw337)?
            };
            {
                let fun341 = e.get("text")?;
                let mut args339 = Vec::new();
                let mut kw340 = Vec::new();
                args339.push(e.get("c")?);
                args339.push(binary("add", e.get("dim_x")?, Val::Int(9i64))?);
                args339.push(binary(
                    "sub",
                    binary(
                        "truediv",
                        binary("add", e.get("seat")?, e.get("top")?)?,
                        Val::Int(2i64),
                    )?,
                    Val::Int(3i64),
                )?);
                args339.push({
                    let mut str342 = String::new();
                    str342.push_str(&format(
                        &e.get("JET_CAP_T")?,
                        &val_string({
                            let mut str343 = String::new();
                            str343.push_str(".2f");
                            Val::Str(str343)
                        })?,
                    )?);
                    str342.push_str(" REF");
                    Val::Str(str342)
                });
                args339.push(Val::Float(9.5f64));
                fun341.call(args339, kw340)?
            };
            {
                let fun346 = e.get("leader")?;
                let mut args344 = Vec::new();
                let mut kw345 = Vec::new();
                args344.push(e.get("c")?);
                args344.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("x")?, e.get("inner")?)?);
                    s.push(e.get("seat")?);
                    Val::tuple(s)
                });
                args344.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(807i64));
                    s.push(Val::Int(650i64));
                    Val::tuple(s)
                });
                args344.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(780i64));
                    s.push(Val::Int(650i64));
                    Val::tuple(s)
                });
                args344.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("WETTED ROOT".into()));
                    s.push(Val::Str("FULLY FUSED".into()));
                    Val::list(s)
                });
                args344.push(Val::Float(9.5f64));
                fun346.call(args344, kw345)?
            };
            {
                let fun349 = e.get("leader")?;
                let mut args347 = Vec::new();
                let mut kw348 = Vec::new();
                args347.push(e.get("c")?);
                args347.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("x")?,
                        binary(
                            "truediv",
                            binary("add", e.get("inner")?, e.get("cr")?)?,
                            Val::Int(2i64),
                        )?,
                    )?);
                    s.push(e.get("seat")?);
                    Val::tuple(s)
                });
                args347.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(1070i64));
                    s.push(Val::Int(555i64));
                    Val::tuple(s)
                });
                args347.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(1100i64));
                    s.push(Val::Int(555i64));
                    Val::tuple(s)
                });
                args347.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("W1 / 360°".into()));
                    s.push(Val::Str("SEE NOTE 2".into()));
                    Val::list(s)
                });
                args347.push(Val::Float(9.5f64));
                fun349.call(args347, kw348)?
            };
            {
                let fun352 = e.get("text")?;
                let mut args350 = Vec::new();
                let mut kw351 = Vec::new();
                args350.push(e.get("c")?);
                args350.push(e.get("x")?);
                args350.push(Val::Int(529i64));
                args350.push(Val::Str(
                    "GREY BAND: REQUIRED FUSION PATH; WELD PROFILE DIAGRAMMATIC.".into(),
                ));
                args350.push(Val::Float(7.7f64));
                kw351.push(("align".into(), Val::Str("center".into())));
                fun352.call(args350, kw351)?
            };
            Ok(Val::None)
        })
    })?;
    // parts_list
    e.set("parts_list", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned353 = {
                let mut s = Vec::new();
                s.push(Val::Int(710i64));
                s.push(Val::Int(1178i64));
                s.push(Val::Int(485i64));
                Val::tuple(s)
            };
            let unpack354 = unpack(assigned353.clone(), 3)?;
            e.set("left", unpack354[0].clone())?;
            e.set("right", unpack354[1].clone())?;
            e.set("top", unpack354[2].clone())?;
            let assigned355 = {
                let mut s = Vec::new();
                s.push(e.get("left")?);
                s.push(Val::Int(744i64));
                s.push(Val::Int(779i64));
                s.push(Val::Int(876i64));
                s.push(e.get("right")?);
                Val::tuple(s)
            };
            e.set("cols", assigned355.clone())?;
            {
                let fun358 = e.get("text")?;
                let mut args356 = Vec::new();
                let mut kw357 = Vec::new();
                args356.push(e.get("c")?);
                args356.push(e.get("left")?);
                args356.push(Val::Int(503i64));
                args356.push(Val::Str("PARTS AT THIS WELD".into()));
                args356.push(Val::Int(10i64));
                kw357.push(("bold".into(), Val::Bool(true)));
                fun358.call(args356, kw357)?
            };
            {
                let fun361 = e.get("c")?.attr("setLineWidth")?;
                let mut args359 = Vec::new();
                let mut kw360 = Vec::new();
                args359.push(e.get("THIN")?);
                fun361.call(args359, kw360)?
            };
            {
                let fun364 = e.get("c")?.attr("rect")?;
                let mut args362 = Vec::new();
                let mut kw363 = Vec::new();
                args362.push(e.get("left")?);
                args362.push(Val::Int(399i64));
                args362.push(binary("sub", e.get("right")?, e.get("left")?)?);
                args362.push(binary("sub", e.get("top")?, Val::Int(399i64))?);
                kw363.push(("stroke".into(), Val::Int(1i64)));
                kw363.push(("fill".into(), Val::Int(0i64)));
                fun364.call(args362, kw363)?
            };
            for item365 in e
                .get("cols")?
                .get(Val::Slice {
                    start: Some(Val::Int(1i64).integer()?),
                    stop: Some(unary("neg", Val::Int(1i64))?.integer()?),
                    step: 1,
                })?
                .iter()?
            {
                e.set("col", item365)?;
                {
                    let fun368 = e.get("line")?;
                    let mut args366 = Vec::new();
                    let mut kw367 = Vec::new();
                    args366.push(e.get("c")?);
                    args366.push(e.get("col")?);
                    args366.push(Val::Int(399i64));
                    args366.push(e.get("col")?);
                    args366.push(e.get("top")?);
                    fun368.call(args366, kw367)?
                };
            }
            {
                let fun371 = e.get("line")?;
                let mut args369 = Vec::new();
                let mut kw370 = Vec::new();
                args369.push(e.get("c")?);
                args369.push(e.get("left")?);
                args369.push(Val::Int(463i64));
                args369.push(e.get("right")?);
                args369.push(Val::Int(463i64));
                fun371.call(args369, kw370)?
            };
            {
                let fun374 = e.get("line")?;
                let mut args372 = Vec::new();
                let mut kw373 = Vec::new();
                args372.push(e.get("c")?);
                args372.push(e.get("left")?);
                args372.push(Val::Int(431i64));
                args372.push(e.get("right")?);
                args372.push(Val::Int(431i64));
                fun374.call(args372, kw373)?
            };
            for item375 in {
                let fun381 = e.get("enumerate")?;
                let mut args379 = Vec::new();
                let mut kw380 = Vec::new();
                args379.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("ITEM".into()));
                    s.push(Val::Str("QTY".into()));
                    s.push(Val::Str("MATERIAL".into()));
                    s.push(Val::Str("DESCRIPTION / DEFINITION".into()));
                    Val::tuple(s)
                });
                fun381.call(args379, kw380)?
            }
            .iter()?
            {
                let unpack382 = unpack(item375, 2)?;
                e.set("j", unpack382[0].clone())?;
                e.set("label", unpack382[1].clone())?;
                {
                    let fun378 = e.get("text")?;
                    let mut args376 = Vec::new();
                    let mut kw377 = Vec::new();
                    args376.push(e.get("c")?);
                    args376.push(binary(
                        "truediv",
                        binary(
                            "add",
                            e.get("cols")?.get(e.get("j")?)?,
                            e.get("cols")?
                                .get(binary("add", e.get("j")?, Val::Int(1i64))?)?,
                        )?,
                        Val::Int(2i64),
                    )?);
                    args376.push(Val::Int(471i64));
                    args376.push(e.get("label")?);
                    args376.push(Val::Float(7.8f64));
                    kw377.push(("bold".into(), Val::Bool(true)));
                    kw377.push(("align".into(), Val::Str("center".into())));
                    fun378.call(args376, kw377)?
                };
            }
            for item383 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(450i64));
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("1".into()));
                        s.push(Val::Str("1".into()));
                        s.push(Val::Str("HSM-000010".into()));
                        s.push(Val::Str("TAISHER 316L STREET ELBOW, 1/4 NPT M X F".into()));
                        Val::tuple(s)
                    });
                    s.push(Val::Str("ORDER ID B0CZ38MYL1; AS RECEIVED".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(418i64));
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("2".into()));
                        s.push(Val::Str("1".into()));
                        s.push(Val::Str("HSM-000011".into()));
                        s.push(Val::Str("316 STAINLESS DRILLED CAP; JET-CAP-01".into()));
                        Val::tuple(s)
                    });
                    s.push(Val::Str("FINISHED COMPONENT BEFORE WELDING".into()));
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack397 = unpack(item383, 3)?;
                e.set("y", unpack397[0].clone())?;
                e.set("values", unpack397[1].clone())?;
                e.set("more", unpack397[2].clone())?;
                for item384 in {
                    let fun392 = e.get("enumerate")?;
                    let mut args390 = Vec::new();
                    let mut kw391 = Vec::new();
                    args390.push(e.get("values")?);
                    fun392.call(args390, kw391)?
                }
                .iter()?
                {
                    let unpack393 = unpack(item384, 2)?;
                    e.set("j", unpack393[0].clone())?;
                    e.set("value", unpack393[1].clone())?;
                    {
                        let fun387 = e.get("text")?;
                        let mut args385 = Vec::new();
                        let mut kw386 = Vec::new();
                        args385.push(e.get("c")?);
                        args385.push(binary(
                            "add",
                            e.get("cols")?.get(e.get("j")?)?,
                            Val::Int(5i64),
                        )?);
                        args385.push(e.get("y")?);
                        args385.push(e.get("value")?);
                        args385.push(Val::Float(7.9f64));
                        kw386.push(("bold".into(), {
                            let v388 = e.get("j")?;
                            let v389 = Val::Int(0i64);
                            Val::Bool(compare("eq", v388.clone(), v389.clone())?.truthy()?)
                        }));
                        fun387.call(args385, kw386)?
                    };
                }
                {
                    let fun396 = e.get("text")?;
                    let mut args394 = Vec::new();
                    let mut kw395 = Vec::new();
                    args394.push(e.get("c")?);
                    args394.push(binary(
                        "add",
                        e.get("cols")?.get(Val::Int(3i64))?,
                        Val::Int(5i64),
                    )?);
                    args394.push(binary("sub", e.get("y")?, Val::Int(12i64))?);
                    args394.push(e.get("more")?);
                    args394.push(Val::Float(7.7f64));
                    fun396.call(args394, kw395)?
                };
            }
            Ok(Val::None)
        })
    })?;
    // requirements
    e.set("requirements",{let params=vec![("c".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned398={let mut s=Vec::new();s.push(Val::Int(710i64));s.push(Val::Int(355i64));s.push(Val::Int(468i64));s.push(Val::Float(8.7f64));Val::tuple(s)};let unpack399=unpack(assigned398.clone(),4)?;e.set("x",unpack399[0].clone())?;e.set("y",unpack399[1].clone())?;e.set("width",unpack399[2].clone())?;e.set("size",unpack399[3].clone())?;
{let fun402=e.get("text")?;let mut args400=Vec::new();let mut kw401=Vec::new();args400.push(e.get("c")?);args400.push(e.get("x")?);args400.push(Val::Int(375i64));args400.push(Val::Str("ASSEMBLY AND ACCEPTANCE".into()));args400.push(Val::Int(10i64));kw401.push(("bold".into(),Val::Bool(true)));fun402.call(args400,kw401)?};
let assigned403={let mut s=Vec::new();s.push(Val::Str("1. Assemble items 1 and 2. The purchased elbow controls fitting geometry. Body, bores and thread profiles are reference representations. Cap dimensions: JET-CAP-01.".into()));s.push(Val::Str("2. W1: continuous 360° weld. Fuse the complete cap-to-tip interface through to the wetted bore-side root. Preserve the open jet. The grey band shows the required fusion path, not a weld size. Use the accepted small-joint coupon procedure; filler, if used: ER316L.".into()));s.push({let mut str404=String::new();str404.push_str("3. Cap OD axis within ");str404.push_str(&format(&e.get("CAP_OFFSET_MAX")?,&val_string({let mut str405=String::new();str405.push_str(".2f");Val::Str(str405)})?)?);str404.push_str(" radial of male-port bore axis; pre-weld seating gap ");str404.push_str(&format(&e.get("cap")?.attr("FACE_GAP_MAX")?,&val_string({let mut str406=String::new();str406.push_str(".2f");Val::Str(str406)})?)?);str404.push_str(" MAX. Completed jet axis within ");str404.push_str(&format(&e.get("JET_OFFSET_MAX")?,&val_string({let mut str407=String::new();str407.push_str(".2f");Val::Str(str407)})?)?);str404.push_str(" radial of that bore axis and normal to the elbow tip within ");str404.push_str(&format(&e.get("cap")?.attr("AXIS_ANGLE_MAX")?,&val_string({let mut str408=String::new();str408.push_str("g");Val::Str(str408)})?)?);str404.push_str("°. Retain JET-CAP-01 passage limits after welding.");Val::Str(str404)});s.push(Val::Str("4. Verify both threads after welding. Trial-fit through the loose END-CAP-01 plate at Port 2; the welded envelope must clear the actual tapped port and the jet exit must project into headspace. Record make-up depth, clocking and projection.".into()));s.push(Val::Str("5. Inspect the cap and open passage; remove loose metal and cutting fluid. Flush, clean, passivate and flow-check the completed elbow per assembly/water-inlet-jet.md. Flow must emerge through the jet passage only.".into()));s.push(Val::Str("6. Record actual bore/tip/land, cap overlap, maximum welded OD and port clearance. Qualify the same-material joint by sectioned-root inspection; retain settings and coupon identity. Numerical weld settings and flow acceptance require that qualification.".into()));Val::list(s)};e.set("paragraphs",assigned403.clone())?;
for item409 in e.get("paragraphs")?.iter()? {
e.set("paragraph",item409)?;let assigned410=Val::Str("".into());e.set("row",assigned410.clone())?;
for item411 in {let fun429=e.get("paragraph")?.attr("split")?;let mut args427=Vec::new();let mut kw428=Vec::new();fun429.call(args427,kw428)?}.iter()? {
e.set("word",item411)?;let assigned412={let fun415=binary("add",binary("add",e.get("row")?,Val::Str(" ".into()))?,e.get("word")?)?.attr("strip")?;let mut args413=Vec::new();let mut kw414=Vec::new();fun415.call(args413,kw414)?};e.set("trial",assigned412.clone())?;
if {let v421=e.get("row")?;if v421.truthy()? {{let v419={let fun418=e.get("stringWidth")?;let mut args416=Vec::new();let mut kw417=Vec::new();args416.push(e.get("trial")?);args416.push(Val::Str("Helvetica".into()));args416.push(e.get("size")?);fun418.call(args416,kw417)?};let v420=e.get("width")?;Val::Bool(compare("gt",v419.clone(),v420.clone())?.truthy()?)}} else {v421}}.truthy()? {
{let fun424=e.get("text")?;let mut args422=Vec::new();let mut kw423=Vec::new();args422.push(e.get("c")?);args422.push(e.get("x")?);args422.push(e.get("y")?);args422.push(e.get("row")?);args422.push(e.get("size")?);fun424.call(args422,kw423)?};
e.set("y",binary("sub",e.get("y")?,Val::Int(11i64))?)?;
let assigned425=e.get("word")?;e.set("row",assigned425.clone())?;
}else{
let assigned426=e.get("trial")?;e.set("row",assigned426.clone())?;
}
}
{let fun432=e.get("text")?;let mut args430=Vec::new();let mut kw431=Vec::new();args430.push(e.get("c")?);args430.push(e.get("x")?);args430.push(e.get("y")?);args430.push(e.get("row")?);args430.push(e.get("size")?);fun432.call(args430,kw431)?};
e.set("y",binary("sub",e.get("y")?,Val::Int(16i64))?)?;
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
            let assigned433 = {
                let mut s = Vec::new();
                s.push(Val::Int(635i64));
                s.push(Val::Int(1197i64));
                Val::tuple(s)
            };
            let unpack434 = unpack(assigned433.clone(), 2)?;
            e.set("left", unpack434[0].clone())?;
            e.set("right", unpack434[1].clone())?;
            {
                let fun437 = e.get("c")?.attr("setLineWidth")?;
                let mut args435 = Vec::new();
                let mut kw436 = Vec::new();
                args435.push(Val::Float(0.7f64));
                fun437.call(args435, kw436)?
            };
            {
                let fun440 = e.get("c")?.attr("rect")?;
                let mut args438 = Vec::new();
                let mut kw439 = Vec::new();
                args438.push(e.get("left")?);
                args438.push(Val::Int(27i64));
                args438.push(binary("sub", e.get("right")?, e.get("left")?)?);
                args438.push(Val::Int(116i64));
                kw439.push(("stroke".into(), Val::Int(1i64)));
                kw439.push(("fill".into(), Val::Int(0i64)));
                fun440.call(args438, kw439)?
            };
            for item441 in {
                let mut s = Vec::new();
                s.push(Val::Int(98i64));
                s.push(Val::Int(65i64));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("y", item441)?;
                {
                    let fun444 = e.get("line")?;
                    let mut args442 = Vec::new();
                    let mut kw443 = Vec::new();
                    args442.push(e.get("c")?);
                    args442.push(e.get("left")?);
                    args442.push(e.get("y")?);
                    args442.push(e.get("right")?);
                    args442.push(e.get("y")?);
                    fun444.call(args442, kw443)?
                };
            }
            {
                let fun447 = e.get("line")?;
                let mut args445 = Vec::new();
                let mut kw446 = Vec::new();
                args445.push(e.get("c")?);
                args445.push(Val::Int(1010i64));
                args445.push(Val::Int(98i64));
                args445.push(Val::Int(1010i64));
                args445.push(Val::Int(143i64));
                fun447.call(args445, kw446)?
            };
            {
                let fun450 = e.get("text")?;
                let mut args448 = Vec::new();
                let mut kw449 = Vec::new();
                args448.push(e.get("c")?);
                args448.push(Val::Int(645i64));
                args448.push(Val::Int(126i64));
                args448.push(Val::Str("HOME SODA MACHINE".into()));
                args448.push(Val::Int(8i64));
                fun450.call(args448, kw449)?
            };
            {
                let fun453 = e.get("text")?;
                let mut args451 = Vec::new();
                let mut kw452 = Vec::new();
                args451.push(e.get("c")?);
                args451.push(Val::Int(645i64));
                args451.push(Val::Int(108i64));
                args451.push(Val::Str("CARBONATOR WATER-INLET JET ELBOW".into()));
                args451.push(Val::Float(11.5f64));
                kw452.push(("bold".into(), Val::Bool(true)));
                fun453.call(args451, kw452)?
            };
            {
                let fun456 = e.get("text")?;
                let mut args454 = Vec::new();
                let mut kw455 = Vec::new();
                args454.push(e.get("c")?);
                args454.push(Val::Int(1104i64));
                args454.push(Val::Int(125i64));
                args454.push(Val::Str("ASSEMBLY DEFINITION".into()));
                args454.push(Val::Float(8.5f64));
                kw455.push(("bold".into(), Val::Bool(true)));
                kw455.push(("align".into(), Val::Str("center".into())));
                fun456.call(args454, kw455)?
            };
            {
                let fun459 = e.get("text")?;
                let mut args457 = Vec::new();
                let mut kw458 = Vec::new();
                args457.push(e.get("c")?);
                args457.push(Val::Int(1104i64));
                args457.push(Val::Int(110i64));
                args457.push(Val::Str("QUALIFICATION PENDING".into()));
                args457.push(Val::Float(8.5f64));
                kw458.push(("align".into(), Val::Str("center".into())));
                fun459.call(args457, kw458)?
            };
            for item460 in {
                let mut s = Vec::new();
                s.push(Val::Int(866i64));
                s.push(Val::Int(1030i64));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("col", item460)?;
                {
                    let fun463 = e.get("line")?;
                    let mut args461 = Vec::new();
                    let mut kw462 = Vec::new();
                    args461.push(e.get("c")?);
                    args461.push(e.get("col")?);
                    args461.push(Val::Int(65i64));
                    args461.push(e.get("col")?);
                    args461.push(Val::Int(98i64));
                    fun463.call(args461, kw462)?
                };
            }
            for item464 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(645i64));
                    s.push(Val::Str("MATERIAL".into()));
                    s.push(Val::Str("SEE PARTS LIST".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(876i64));
                    s.push(Val::Str("UNITS".into()));
                    s.push(Val::Str("MILLIMETERS".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(1040i64));
                    s.push(Val::Str("QUANTITY".into()));
                    s.push(Val::Str("1 PER CARBONATOR".into()));
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack471 = unpack(item464, 3)?;
                e.set("x", unpack471[0].clone())?;
                e.set("label", unpack471[1].clone())?;
                e.set("value", unpack471[2].clone())?;
                {
                    let fun467 = e.get("text")?;
                    let mut args465 = Vec::new();
                    let mut kw466 = Vec::new();
                    args465.push(e.get("c")?);
                    args465.push(e.get("x")?);
                    args465.push(Val::Int(87i64));
                    args465.push(e.get("label")?);
                    args465.push(Val::Int(7i64));
                    fun467.call(args465, kw466)?
                };
                {
                    let fun470 = e.get("text")?;
                    let mut args468 = Vec::new();
                    let mut kw469 = Vec::new();
                    args468.push(e.get("c")?);
                    args468.push(e.get("x")?);
                    args468.push(Val::Int(73i64));
                    args468.push(e.get("value")?);
                    args468.push(Val::Float(8.5f64));
                    kw469.push(("bold".into(), Val::Bool(true)));
                    fun470.call(args468, kw469)?
                };
            }
            let assigned472 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(635i64));
                    s.push(Val::Int(815i64));
                    s.push(Val::Str("DRAWING".into()));
                    s.push(Val::Str("JET-ELB-01".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(815i64));
                    s.push(Val::Int(867i64));
                    s.push(Val::Str("REV".into()));
                    s.push(e.get("REVISION")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(867i64));
                    s.push(Val::Int(990i64));
                    s.push(Val::Str("DATE".into()));
                    s.push(Val::Str("2026-10-26".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(990i64));
                    s.push(Val::Int(1113i64));
                    s.push(Val::Str("SCALE".into()));
                    s.push(Val::Str("AS SHOWN".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(1113i64));
                    s.push(Val::Int(1197i64));
                    s.push(Val::Str("SHEET".into()));
                    s.push(Val::Str("1 OF 1".into()));
                    Val::tuple(s)
                });
                Val::tuple(s)
            };
            e.set("fields", assigned472.clone())?;
            for item473 in {
                let fun485 = e.get("enumerate")?;
                let mut args483 = Vec::new();
                let mut kw484 = Vec::new();
                args483.push(e.get("fields")?);
                fun485.call(args483, kw484)?
            }
            .iter()?
            {
                let unpack486 = unpack(item473, 2)?;
                e.set("i", unpack486[0].clone())?;
                let unpack487 = unpack(unpack486[1].clone(), 4)?;
                e.set("a", unpack487[0].clone())?;
                e.set("b", unpack487[1].clone())?;
                e.set("label", unpack487[2].clone())?;
                e.set("value", unpack487[3].clone())?;
                if e.get("i")?.truthy()? {
                    {
                        let fun476 = e.get("line")?;
                        let mut args474 = Vec::new();
                        let mut kw475 = Vec::new();
                        args474.push(e.get("c")?);
                        args474.push(e.get("a")?);
                        args474.push(Val::Int(27i64));
                        args474.push(e.get("a")?);
                        args474.push(Val::Int(65i64));
                        fun476.call(args474, kw475)?
                    };
                }
                {
                    let fun479 = e.get("text")?;
                    let mut args477 = Vec::new();
                    let mut kw478 = Vec::new();
                    args477.push(e.get("c")?);
                    args477.push(binary("add", e.get("a")?, Val::Int(9i64))?);
                    args477.push(Val::Int(53i64));
                    args477.push(e.get("label")?);
                    args477.push(Val::Int(7i64));
                    fun479.call(args477, kw478)?
                };
                {
                    let fun482 = e.get("text")?;
                    let mut args480 = Vec::new();
                    let mut kw481 = Vec::new();
                    args480.push(e.get("c")?);
                    args480.push(binary("add", e.get("a")?, Val::Int(9i64))?);
                    args480.push(Val::Int(37i64));
                    args480.push(e.get("value")?);
                    args480.push(Val::Int(9i64));
                    kw481.push(("bold".into(), Val::Bool(true)));
                    fun482.call(args480, kw481)?
                };
            }
            {
                let fun490 = e.get("text")?;
                let mut args488 = Vec::new();
                let mut kw489 = Vec::new();
                args488.push(e.get("c")?);
                args488.push(Val::Int(47i64));
                args488.push(Val::Int(127i64));
                args488.push(e.get("MATERIAL_ID")?);
                args488.push(Val::Int(9i64));
                kw489.push(("bold".into(), Val::Bool(true)));
                fun490.call(args488, kw489)?
            };
            {
                let fun493 = e.get("text")?;
                let mut args491 = Vec::new();
                let mut kw492 = Vec::new();
                args491.push(e.get("c")?);
                args491.push(Val::Int(47i64));
                args491.push(Val::Int(110i64));
                args491.push(Val::Str("mm DIMENSIONS GOVERN. REF = REFERENCE.".into()));
                args491.push(Val::Float(8.5f64));
                fun493.call(args491, kw492)?
            };
            {
                let fun496 = e.get("text")?;
                let mut args494 = Vec::new();
                let mut kw495 = Vec::new();
                args494.push(e.get("c")?);
                args494.push(Val::Int(47i64));
                args494.push(Val::Int(94i64));
                args494.push(Val::Str(
                    "PURCHASED FITTING CONTROLS ITS OWN GEOMETRY.".into(),
                ));
                args494.push(Val::Float(8.5f64));
                fun496.call(args494, kw495)?
            };
            {
                let fun499 = e.get("text")?;
                let mut args497 = Vec::new();
                let mut kw498 = Vec::new();
                args497.push(e.get("c")?);
                args497.push(Val::Int(47i64));
                args497.push(Val::Int(74i64));
                args497.push(Val::Str(
                    "DO NOT SCALE. ANSI B / 17 x 11 IN. PRINT AT 100% FOR SCALE.".into(),
                ));
                args497.push(Val::Float(8.5f64));
                fun499.call(args497, kw498)?
            };
            {
                let fun502 = e.get("text")?;
                let mut args500 = Vec::new();
                let mut kw501 = Vec::new();
                args500.push(e.get("c")?);
                args500.push(Val::Int(47i64));
                args500.push(Val::Int(48i64));
                args500.push(Val::Str(
                    "CAP COMPONENT: JET-CAP-01. ASSEMBLY: WATER-INLET-JET.MD.".into(),
                ));
                args500.push(Val::Int(8i64));
                fun502.call(args500, kw501)?
            };
            Ok(Val::None)
        })
    })?;
    // build_pdf
    e.set("build_pdf",{let params=vec![("path".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned503={let fun506=e.get("canvas")?.attr("Canvas")?;let mut args504=Vec::new();let mut kw505=Vec::new();args504.push({let fun509=e.get("str")?;let mut args507=Vec::new();let mut kw508=Vec::new();args507.push(e.get("path")?);fun509.call(args507,kw508)?});kw505.push(("pagesize".into(),e.get("SHEET")?));kw505.push(("invariant".into(),Val::Int(1i64)));kw505.push(("pageCompression".into(),Val::Int(1i64)));fun506.call(args504,kw505)?};e.set("c",assigned503.clone())?;
{let fun512=e.get("c")?.attr("setTitle")?;let mut args510=Vec::new();let mut kw511=Vec::new();args510.push(Val::Str("Carbonator water-inlet jet elbow - assembly engineering drawing".into()));fun512.call(args510,kw511)?};
{let fun515=e.get("c")?.attr("setAuthor")?;let mut args513=Vec::new();let mut kw514=Vec::new();args513.push(Val::Str("Home Soda Machine / Codex".into()));fun515.call(args513,kw514)?};
{let fun518=e.get("c")?.attr("setSubject")?;let mut args516=Vec::new();let mut kw517=Vec::new();args516.push(Val::Str("JET-ELB-01 Rev A: welded cap and TAISHER street elbow, full-root fusion and finished assembly acceptance".into()));fun518.call(args516,kw517)?};
{let fun521=e.get("c")?.attr("setStrokeColorRGB")?;let mut args519=Vec::new();let mut kw520=Vec::new();args519.push(Val::Int(0i64));args519.push(Val::Int(0i64));args519.push(Val::Int(0i64));fun521.call(args519,kw520)?};
{let fun524=e.get("c")?.attr("setFillColorRGB")?;let mut args522=Vec::new();let mut kw523=Vec::new();args522.push(Val::Int(0i64));args522.push(Val::Int(0i64));args522.push(Val::Int(0i64));fun524.call(args522,kw523)?};
{let fun527=e.get("c")?.attr("setLineWidth")?;let mut args525=Vec::new();let mut kw526=Vec::new();args525.push(Val::Float(0.8f64));fun527.call(args525,kw526)?};
{let fun530=e.get("c")?.attr("rect")?;let mut args528=Vec::new();let mut kw529=Vec::new();args528.push(Val::Int(27i64));args528.push(Val::Int(27i64));args528.push(binary("sub",e.get("SHEET")?.get(Val::Int(0i64))?,Val::Int(54i64))?);args528.push(binary("sub",e.get("SHEET")?.get(Val::Int(1i64))?,Val::Int(54i64))?);kw529.push(("stroke".into(),Val::Int(1i64)));kw529.push(("fill".into(),Val::Int(0i64)));fun530.call(args528,kw529)?};
{let fun533=e.get("assembly_view")?;let mut args531=Vec::new();let mut kw532=Vec::new();args531.push(e.get("c")?);fun533.call(args531,kw532)?};
{let fun536=e.get("exit_view")?;let mut args534=Vec::new();let mut kw535=Vec::new();args534.push(e.get("c")?);fun536.call(args534,kw535)?};
{let fun539=e.get("joint_detail")?;let mut args537=Vec::new();let mut kw538=Vec::new();args537.push(e.get("c")?);fun539.call(args537,kw538)?};
{let fun542=e.get("parts_list")?;let mut args540=Vec::new();let mut kw541=Vec::new();args540.push(e.get("c")?);fun542.call(args540,kw541)?};
{let fun545=e.get("requirements")?;let mut args543=Vec::new();let mut kw544=Vec::new();args543.push(e.get("c")?);fun545.call(args543,kw544)?};
{let fun548=e.get("text")?;let mut args546=Vec::new();let mut kw547=Vec::new();args546.push(e.get("c")?);args546.push(Val::Int(47i64));args546.push(Val::Int(164i64));args546.push(Val::Str("RELEASE ITEMS: MEASURED FIT / LAND AND PORT CLEARANCE; QUALIFIED SMALL-JOINT WELD; FLOW ACCEPTANCE.".into()));args546.push(Val::Float(8.5f64));kw547.push(("bold".into(),Val::Bool(true)));fun548.call(args546,kw547)?};
{let fun551=e.get("title_block")?;let mut args549=Vec::new();let mut kw550=Vec::new();args549.push(e.get("c")?);fun551.call(args549,kw550)?};
{let fun554=e.get("c")?.attr("showPage")?;let mut args552=Vec::new();let mut kw553=Vec::new();fun554.call(args552,kw553)?};
{let fun557=e.get("c")?.attr("save")?;let mut args555=Vec::new();let mut kw556=Vec::new();fun557.call(args555,kw556)?};
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun560 = e.get("export_pdf")?;
        let mut args558 = Vec::new();
        let mut kw559 = Vec::new();
        args558.push(e.get("build_pdf")?);
        args558.push({
            let fun563 = e.get("str")?;
            let mut args561 = Vec::new();
            let mut kw562 = Vec::new();
            args561.push(e.get("PDF_PATH")?);
            fun563.call(args561, kw562)?
        });
        fun560.call(args558, kw559)?
    };
    {
        let fun566 = e.get("print")?;
        let mut args564 = Vec::new();
        let mut kw565 = Vec::new();
        args564.push({
            let mut str567 = String::new();
            str567.push_str("Exported: ");
            str567.push_str(&format(&e.get("PDF_PATH")?, &String::new())?);
            Val::Str(str567)
        });
        fun566.call(args564, kw565)?
    };
    Ok(Val::None)
}
