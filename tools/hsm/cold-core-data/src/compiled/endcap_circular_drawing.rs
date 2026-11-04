#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let mod2 = rt.import_module("reportlab.lib.units")?;
    e.set("inch", rt.member("reportlab.lib.units", "inch")?)?;
    let mod3 = rt.import_module("reportlab.pdfbase")?;
    e.set("pdfmetrics", rt.member("reportlab.pdfbase", "pdfmetrics")?)?;
    let mod4 = rt.import_module("reportlab.pdfgen")?;
    e.set("canvas", rt.member("reportlab.pdfgen", "canvas")?)?;
    let assigned5 = {
        let fun8 = {
            let fun11 = e.get("Path")?;
            let mut args9 = Vec::new();
            let mut kw10 = Vec::new();
            args9.push(e.get("__file__")?);
            fun11.call(args9, kw10)?
        }
        .attr("resolve")?;
        let mut args6 = Vec::new();
        let mut kw7 = Vec::new();
        fun8.call(args6, kw7)?
    }
    .attr("parent")?;
    e.set("HERE", assigned5.clone())?;
    let assigned12 = {
        let fun15 = e.get("next")?;
        let mut args13 = Vec::new();
        let mut kw14 = Vec::new();
        args13.push({
            let e = e.child();
            let out16 = Val::list(vec![]);
            for item17 in e.get("HERE")?.attr("parents")?.iter()? {
                e.set("p", item17)?;
                if {
                    let fun20 = binary(
                        "truediv",
                        binary("truediv", e.get("p")?, Val::Str("tools".into()))?,
                        Val::Str("docgen".into()),
                    )?
                    .attr("is_dir")?;
                    let mut args18 = Vec::new();
                    let mut kw19 = Vec::new();
                    fun20.call(args18, kw19)?
                }
                .truthy()?
                {
                    out16.attr("append")?.call(vec![e.get("p")?], vec![])?;
                }
            }
            out16
        });
        fun15.call(args13, kw14)?
    };
    e.set("ROOT", assigned12.clone())?;
    {
        let fun23 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args21 = Vec::new();
        let mut kw22 = Vec::new();
        args21.push(Val::Int(0i64));
        args21.push({
            let fun26 = e.get("str")?;
            let mut args24 = Vec::new();
            let mut kw25 = Vec::new();
            args24.push(binary(
                "truediv",
                binary("truediv", e.get("ROOT")?, Val::Str("hardware".into()))?,
                Val::Str("scripts".into()),
            )?);
            fun26.call(args24, kw25)?
        });
        fun23.call(args21, kw22)?
    };
    let mod27 = rt.import_module("_document_export")?;
    e.set("export_pdf", rt.member("_document_export", "export_pdf")?)?;
    let mod28 = rt.import_module("endcap_circular_dxf")?;
    e.set(
        "disc_diameter",
        rt.member("endcap_circular_dxf", "disc_diameter")?,
    )?;
    e.set(
        "disc_thickness",
        rt.member("endcap_circular_dxf", "disc_thickness")?,
    )?;
    e.set(
        "hole_positions",
        rt.member("endcap_circular_dxf", "hole_positions")?,
    )?;
    e.set(
        "hole_radius",
        rt.member("endcap_circular_dxf", "hole_radius")?,
    )?;
    e.set(
        "register_position",
        rt.member("endcap_circular_dxf", "register_position")?,
    )?;
    e.set(
        "register_drill_diameter",
        rt.member("endcap_circular_dxf", "register_drill_diameter")?,
    )?;
    e.set(
        "register_depth",
        rt.member("endcap_circular_dxf", "register_depth")?,
    )?;
    let assigned29 = binary(
        "truediv",
        e.get("HERE")?,
        Val::Str("endcap-circular-2hole-drawing.pdf".into()),
    )?;
    e.set("PDF_PATH", assigned29.clone())?;
    let assigned30 = Val::Str("E".into());
    e.set("REVISION", assigned30.clone())?;
    let assigned31 = Val::Str("2026-10-28".into());
    e.set("REVISION_DATE", assigned31.clone())?;
    let assigned32 = {
        let mut s = Vec::new();
        s.push(binary("mul", Val::Int(17i64), e.get("inch")?)?);
        s.push(binary("mul", Val::Int(11i64), e.get("inch")?)?);
        Val::tuple(s)
    };
    e.set("SHEET", assigned32.clone())?;
    let assigned33 = Val::Int(27i64);
    e.set("MARGIN", assigned33.clone())?;
    let assigned34 = Val::Float(0.85f64);
    e.set("VISIBLE", assigned34.clone())?;
    let assigned35 = Val::Float(0.35f64);
    e.set("THIN", assigned35.clone())?;
    let assigned36 = {
        let mut s = Vec::new();
        s.push(Val::Int(12i64));
        s.push(Val::Int(3i64));
        s.push(Val::Int(2i64));
        s.push(Val::Int(3i64));
        Val::tuple(s)
    };
    e.set("CENTER_DASH", assigned36.clone())?;
    let assigned37 = {
        let mut s = Vec::new();
        s.push(Val::Int(294i64));
        s.push(Val::Int(490i64));
        Val::tuple(s)
    };
    let unpack38 = unpack(assigned37.clone(), 2)?;
    e.set("CX", unpack38[0].clone())?;
    e.set("CY", unpack38[1].clone())?;
    let assigned39 = binary(
        "truediv",
        binary("mul", e.get("disc_diameter")?, e.get("inch")?)?,
        Val::Int(2i64),
    )?;
    e.set("RADIUS", assigned39.clone())?;
    // line
    e.set("line", {
        let params = vec![
            ("c".into(), None, false),
            ("x1".into(), None, false),
            ("y1".into(), None, false),
            ("x2".into(), None, false),
            ("y2".into(), None, false),
            ("weight".into(), Some(e.get("THIN")?), false),
            (
                "dash".into(),
                Some({
                    let mut s = Vec::new();
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
            let _frame = rt.frame(&outer);
            {
                let fun42 = e.get("c")?.attr("setLineWidth")?;
                let mut args40 = Vec::new();
                let mut kw41 = Vec::new();
                args40.push(e.get("weight")?);
                fun42.call(args40, kw41)?
            };
            {
                let fun45 = e.get("c")?.attr("setDash")?;
                let mut args43 = Vec::new();
                let mut kw44 = Vec::new();
                args43.push(e.get("dash")?);
                fun45.call(args43, kw44)?
            };
            {
                let fun48 = e.get("c")?.attr("line")?;
                let mut args46 = Vec::new();
                let mut kw47 = Vec::new();
                args46.push(e.get("x1")?);
                args46.push(e.get("y1")?);
                args46.push(e.get("x2")?);
                args46.push(e.get("y2")?);
                fun48.call(args46, kw47)?
            };
            {
                let fun51 = e.get("c")?.attr("setDash")?;
                let mut args49 = Vec::new();
                let mut kw50 = Vec::new();
                fun51.call(args49, kw50)?
            };
            Ok(Val::None)
        })
    })?;
    // text
    e.set("text", {
        let params = vec![
            ("c".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("value".into(), None, false),
            ("size".into(), Some(Val::Int(9i64)), false),
            ("bold".into(), Some(Val::Bool(false)), false),
            ("align".into(), Some(Val::Str("left".into())), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun54 = e.get("c")?.attr("setFont")?;
                let mut args52 = Vec::new();
                let mut kw53 = Vec::new();
                args52.push(if e.get("bold")?.truthy()? {
                    Val::Str("Helvetica-Bold".into())
                } else {
                    Val::Str("Helvetica".into())
                });
                args52.push(e.get("size")?);
                fun54.call(args52, kw53)?
            };
            if {
                let v55 = e.get("align")?;
                let v56 = Val::Str("center".into());
                Val::Bool(compare("eq", v55.clone(), v56.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun59 = e.get("c")?.attr("drawCentredString")?;
                    let mut args57 = Vec::new();
                    let mut kw58 = Vec::new();
                    args57.push(e.get("x")?);
                    args57.push(e.get("y")?);
                    args57.push(e.get("value")?);
                    fun59.call(args57, kw58)?
                };
            } else {
                if {
                    let v60 = e.get("align")?;
                    let v61 = Val::Str("right".into());
                    Val::Bool(compare("eq", v60.clone(), v61.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun64 = e.get("c")?.attr("drawRightString")?;
                        let mut args62 = Vec::new();
                        let mut kw63 = Vec::new();
                        args62.push(e.get("x")?);
                        args62.push(e.get("y")?);
                        args62.push(e.get("value")?);
                        fun64.call(args62, kw63)?
                    };
                } else {
                    {
                        let fun67 = e.get("c")?.attr("drawString")?;
                        let mut args65 = Vec::new();
                        let mut kw66 = Vec::new();
                        args65.push(e.get("x")?);
                        args65.push(e.get("y")?);
                        args65.push(e.get("value")?);
                        fun67.call(args65, kw66)?
                    };
                }
            }
            Ok(Val::None)
        })
    })?;
    // arrow
    e.set("arrow", {
        let params = vec![
            ("c".into(), None, false),
            ("tip".into(), None, false),
            ("tail".into(), None, false),
            ("length".into(), Some(Val::Int(6i64)), false),
            ("width".into(), Some(Val::Int(2i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned68 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("tip")?.get(Val::Int(0i64))?,
                    e.get("tail")?.get(Val::Int(0i64))?,
                )?);
                s.push(binary(
                    "sub",
                    e.get("tip")?.get(Val::Int(1i64))?,
                    e.get("tail")?.get(Val::Int(1i64))?,
                )?);
                Val::tuple(s)
            };
            let unpack69 = unpack(assigned68.clone(), 2)?;
            e.set("dx", unpack69[0].clone())?;
            e.set("dy", unpack69[1].clone())?;
            let assigned70 = {
                let fun73 = e.get("math")?.attr("hypot")?;
                let mut args71 = Vec::new();
                let mut kw72 = Vec::new();
                args71.push(e.get("dx")?);
                args71.push(e.get("dy")?);
                fun73.call(args71, kw72)?
            };
            e.set("norm", assigned70.clone())?;
            let assigned74 = {
                let mut s = Vec::new();
                s.push(binary("truediv", e.get("dx")?, e.get("norm")?)?);
                s.push(binary("truediv", e.get("dy")?, e.get("norm")?)?);
                Val::tuple(s)
            };
            let unpack75 = unpack(assigned74.clone(), 2)?;
            e.set("ux", unpack75[0].clone())?;
            e.set("uy", unpack75[1].clone())?;
            let assigned76 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("tip")?.get(Val::Int(0i64))?,
                    binary("mul", e.get("length")?, e.get("ux")?)?,
                )?);
                s.push(binary(
                    "sub",
                    e.get("tip")?.get(Val::Int(1i64))?,
                    binary("mul", e.get("length")?, e.get("uy")?)?,
                )?);
                Val::tuple(s)
            };
            let unpack77 = unpack(assigned76.clone(), 2)?;
            e.set("bx", unpack77[0].clone())?;
            e.set("by", unpack77[1].clone())?;
            let assigned78 = {
                let fun81 = e.get("c")?.attr("beginPath")?;
                let mut args79 = Vec::new();
                let mut kw80 = Vec::new();
                fun81.call(args79, kw80)?
            };
            e.set("p", assigned78.clone())?;
            {
                let fun84 = e.get("p")?.attr("moveTo")?;
                let mut args82 = Vec::new();
                let mut kw83 = Vec::new();
                args82.extend(e.get("tip")?.iter()?);
                fun84.call(args82, kw83)?
            };
            {
                let fun87 = e.get("p")?.attr("lineTo")?;
                let mut args85 = Vec::new();
                let mut kw86 = Vec::new();
                args85.push(binary(
                    "sub",
                    e.get("bx")?,
                    binary("mul", e.get("width")?, e.get("uy")?)?,
                )?);
                args85.push(binary(
                    "add",
                    e.get("by")?,
                    binary("mul", e.get("width")?, e.get("ux")?)?,
                )?);
                fun87.call(args85, kw86)?
            };
            {
                let fun90 = e.get("p")?.attr("lineTo")?;
                let mut args88 = Vec::new();
                let mut kw89 = Vec::new();
                args88.push(binary(
                    "add",
                    e.get("bx")?,
                    binary("mul", e.get("width")?, e.get("uy")?)?,
                )?);
                args88.push(binary(
                    "sub",
                    e.get("by")?,
                    binary("mul", e.get("width")?, e.get("ux")?)?,
                )?);
                fun90.call(args88, kw89)?
            };
            {
                let fun93 = e.get("p")?.attr("close")?;
                let mut args91 = Vec::new();
                let mut kw92 = Vec::new();
                fun93.call(args91, kw92)?
            };
            {
                let fun96 = e.get("c")?.attr("drawPath")?;
                let mut args94 = Vec::new();
                let mut kw95 = Vec::new();
                args94.push(e.get("p")?);
                kw95.push(("stroke".into(), Val::Int(0i64)));
                kw95.push(("fill".into(), Val::Int(1i64)));
                fun96.call(args94, kw95)?
            };
            Ok(Val::None)
        })
    })?;
    // leader
    e.set("leader", {
        let params = vec![
            ("c".into(), None, false),
            ("tip".into(), None, false),
            ("knee".into(), None, false),
            ("end".into(), None, false),
            ("lines".into(), None, false),
            ("size".into(), Some(Val::Int(9i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun99 = e.get("line")?;
                let mut args97 = Vec::new();
                let mut kw98 = Vec::new();
                args97.push(e.get("c")?);
                args97.extend(e.get("tip")?.iter()?);
                args97.extend(e.get("knee")?.iter()?);
                fun99.call(args97, kw98)?
            };
            {
                let fun102 = e.get("line")?;
                let mut args100 = Vec::new();
                let mut kw101 = Vec::new();
                args100.push(e.get("c")?);
                args100.extend(e.get("knee")?.iter()?);
                args100.extend(e.get("end")?.iter()?);
                fun102.call(args100, kw101)?
            };
            {
                let fun105 = e.get("arrow")?;
                let mut args103 = Vec::new();
                let mut kw104 = Vec::new();
                args103.push(e.get("c")?);
                args103.push(e.get("tip")?);
                args103.push(e.get("knee")?);
                fun105.call(args103, kw104)?
            };
            let assigned106 = {
                let v107 = e.get("end")?.get(Val::Int(0i64))?;
                let v108 = e.get("knee")?.get(Val::Int(0i64))?;
                Val::Bool(compare("gt", v107.clone(), v108.clone())?.truthy()?)
            };
            e.set("text_on_right", assigned106.clone())?;
            let assigned109 = binary(
                "add",
                e.get("end")?.get(Val::Int(0i64))?,
                if e.get("text_on_right")?.truthy()? {
                    Val::Int(4i64)
                } else {
                    unary("neg", Val::Int(4i64))?
                },
            )?;
            e.set("text_x", assigned109.clone())?;
            let assigned110 = if e.get("text_on_right")?.truthy()? {
                Val::Str("left".into())
            } else {
                Val::Str("right".into())
            };
            e.set("align", assigned110.clone())?;
            let assigned111 = {
                let fun114 = e.get("pdfmetrics")?.attr("getAscent")?;
                let mut args112 = Vec::new();
                let mut kw113 = Vec::new();
                args112.push(Val::Str("Helvetica".into()));
                args112.push(e.get("size")?);
                fun114.call(args112, kw113)?
            };
            e.set("cap_height", assigned111.clone())?;
            for item115 in {
                let fun121 = e.get("enumerate")?;
                let mut args119 = Vec::new();
                let mut kw120 = Vec::new();
                args119.push(e.get("lines")?);
                fun121.call(args119, kw120)?
            }
            .iter()?
            {
                let unpack122 = unpack(item115, 2)?;
                e.set("i", unpack122[0].clone())?;
                e.set("value", unpack122[1].clone())?;
                {
                    let fun118 = e.get("text")?;
                    let mut args116 = Vec::new();
                    let mut kw117 = Vec::new();
                    args116.push(e.get("c")?);
                    args116.push(e.get("text_x")?);
                    args116.push(binary(
                        "sub",
                        binary(
                            "sub",
                            e.get("end")?.get(Val::Int(1i64))?,
                            binary("truediv", e.get("cap_height")?, Val::Int(2i64))?,
                        )?,
                        binary("mul", e.get("i")?, Val::Int(12i64))?,
                    )?);
                    args116.push(e.get("value")?);
                    args116.push(e.get("size")?);
                    kw117.push(("align".into(), e.get("align")?));
                    fun118.call(args116, kw117)?
                };
            }
            Ok(Val::None)
        })
    })?;
    // circular_leader
    e.set("circular_leader", {
        let params = vec![
            ("c".into(), None, false),
            ("center_xy".into(), None, false),
            ("radius".into(), None, false),
            ("knee".into(), None, false),
            ("end".into(), None, false),
            ("lines".into(), None, false),
            ("size".into(), Some(Val::Int(9i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned123 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("knee")?.get(Val::Int(0i64))?,
                    e.get("center_xy")?.get(Val::Int(0i64))?,
                )?);
                s.push(binary(
                    "sub",
                    e.get("knee")?.get(Val::Int(1i64))?,
                    e.get("center_xy")?.get(Val::Int(1i64))?,
                )?);
                Val::tuple(s)
            };
            let unpack124 = unpack(assigned123.clone(), 2)?;
            e.set("dx", unpack124[0].clone())?;
            e.set("dy", unpack124[1].clone())?;
            let assigned125 = {
                let fun128 = e.get("math")?.attr("hypot")?;
                let mut args126 = Vec::new();
                let mut kw127 = Vec::new();
                args126.push(e.get("dx")?);
                args126.push(e.get("dy")?);
                fun128.call(args126, kw127)?
            };
            e.set("distance", assigned125.clone())?;
            let assigned129 = {
                let mut s = Vec::new();
                s.push(binary(
                    "add",
                    e.get("center_xy")?.get(Val::Int(0i64))?,
                    binary(
                        "truediv",
                        binary("mul", e.get("radius")?, e.get("dx")?)?,
                        e.get("distance")?,
                    )?,
                )?);
                s.push(binary(
                    "add",
                    e.get("center_xy")?.get(Val::Int(1i64))?,
                    binary(
                        "truediv",
                        binary("mul", e.get("radius")?, e.get("dy")?)?,
                        e.get("distance")?,
                    )?,
                )?);
                Val::tuple(s)
            };
            e.set("tip", assigned129.clone())?;
            {
                let fun132 = e.get("leader")?;
                let mut args130 = Vec::new();
                let mut kw131 = Vec::new();
                args130.push(e.get("c")?);
                args130.push(e.get("tip")?);
                args130.push(e.get("knee")?);
                args130.push(e.get("end")?);
                args130.push(e.get("lines")?);
                args130.push(e.get("size")?);
                fun132.call(args130, kw131)?
            };
            Ok(Val::None)
        })
    })?;
    // horizontal_dimension
    e.set("horizontal_dimension", {
        let params = vec![
            ("c".into(), None, false),
            ("x1".into(), None, false),
            ("x2".into(), None, false),
            ("witness_y".into(), None, false),
            ("dim_y".into(), None, false),
            ("label".into(), None, false),
            ("size".into(), Some(Val::Int(10i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned133 = if {
                let v134 = e.get("dim_y")?;
                let v135 = e.get("witness_y")?;
                Val::Bool(compare("gt", v134.clone(), v135.clone())?.truthy()?)
            }
            .truthy()?
            {
                Val::Int(1i64)
            } else {
                unary("neg", Val::Int(1i64))?
            };
            e.set("sign", assigned133.clone())?;
            for item136 in {
                let mut s = Vec::new();
                s.push(e.get("x1")?);
                s.push(e.get("x2")?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("x", item136)?;
                {
                    let fun139 = e.get("line")?;
                    let mut args137 = Vec::new();
                    let mut kw138 = Vec::new();
                    args137.push(e.get("c")?);
                    args137.push(e.get("x")?);
                    args137.push(binary(
                        "add",
                        e.get("witness_y")?,
                        binary("mul", e.get("sign")?, Val::Int(4i64))?,
                    )?);
                    args137.push(e.get("x")?);
                    args137.push(binary(
                        "add",
                        e.get("dim_y")?,
                        binary("mul", e.get("sign")?, Val::Int(5i64))?,
                    )?);
                    fun139.call(args137, kw138)?
                };
            }
            {
                let fun142 = e.get("line")?;
                let mut args140 = Vec::new();
                let mut kw141 = Vec::new();
                args140.push(e.get("c")?);
                args140.push(e.get("x1")?);
                args140.push(e.get("dim_y")?);
                args140.push(e.get("x2")?);
                args140.push(e.get("dim_y")?);
                fun142.call(args140, kw141)?
            };
            {
                let fun145 = e.get("arrow")?;
                let mut args143 = Vec::new();
                let mut kw144 = Vec::new();
                args143.push(e.get("c")?);
                args143.push({
                    let mut s = Vec::new();
                    s.push(e.get("x1")?);
                    s.push(e.get("dim_y")?);
                    Val::tuple(s)
                });
                args143.push({
                    let mut s = Vec::new();
                    s.push(e.get("x2")?);
                    s.push(e.get("dim_y")?);
                    Val::tuple(s)
                });
                fun145.call(args143, kw144)?
            };
            {
                let fun148 = e.get("arrow")?;
                let mut args146 = Vec::new();
                let mut kw147 = Vec::new();
                args146.push(e.get("c")?);
                args146.push({
                    let mut s = Vec::new();
                    s.push(e.get("x2")?);
                    s.push(e.get("dim_y")?);
                    Val::tuple(s)
                });
                args146.push({
                    let mut s = Vec::new();
                    s.push(e.get("x1")?);
                    s.push(e.get("dim_y")?);
                    Val::tuple(s)
                });
                fun148.call(args146, kw147)?
            };
            {
                let fun151 = e.get("text")?;
                let mut args149 = Vec::new();
                let mut kw150 = Vec::new();
                args149.push(e.get("c")?);
                args149.push(binary(
                    "truediv",
                    binary("add", e.get("x1")?, e.get("x2")?)?,
                    Val::Int(2i64),
                )?);
                args149.push(binary("add", e.get("dim_y")?, Val::Int(5i64))?);
                args149.push(e.get("label")?);
                args149.push(e.get("size")?);
                kw150.push(("align".into(), Val::Str("center".into())));
                fun151.call(args149, kw150)?
            };
            Ok(Val::None)
        })
    })?;
    // vertical_dimension
    e.set("vertical_dimension", {
        let params = vec![
            ("c".into(), None, false),
            ("x".into(), None, false),
            ("y1".into(), None, false),
            ("y2".into(), None, false),
            ("witness_x".into(), None, false),
            ("lines".into(), None, false),
            ("outside".into(), Some(Val::Bool(false)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            for item152 in {
                let mut s = Vec::new();
                s.push(e.get("y1")?);
                s.push(e.get("y2")?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("y", item152)?;
                {
                    let fun155 = e.get("line")?;
                    let mut args153 = Vec::new();
                    let mut kw154 = Vec::new();
                    args153.push(e.get("c")?);
                    args153.push(binary("add", e.get("witness_x")?, Val::Int(4i64))?);
                    args153.push(e.get("y")?);
                    args153.push(binary("add", e.get("x")?, Val::Int(5i64))?);
                    args153.push(e.get("y")?);
                    fun155.call(args153, kw154)?
                };
            }
            if e.get("outside")?.truthy()? {
                {
                    let fun158 = e.get("line")?;
                    let mut args156 = Vec::new();
                    let mut kw157 = Vec::new();
                    args156.push(e.get("c")?);
                    args156.push(e.get("x")?);
                    args156.push(binary("sub", e.get("y1")?, Val::Int(13i64))?);
                    args156.push(e.get("x")?);
                    args156.push(binary("add", e.get("y2")?, Val::Int(13i64))?);
                    fun158.call(args156, kw157)?
                };
                {
                    let fun161 = e.get("arrow")?;
                    let mut args159 = Vec::new();
                    let mut kw160 = Vec::new();
                    args159.push(e.get("c")?);
                    args159.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y1")?);
                        Val::tuple(s)
                    });
                    args159.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(binary("sub", e.get("y1")?, Val::Int(13i64))?);
                        Val::tuple(s)
                    });
                    fun161.call(args159, kw160)?
                };
                {
                    let fun164 = e.get("arrow")?;
                    let mut args162 = Vec::new();
                    let mut kw163 = Vec::new();
                    args162.push(e.get("c")?);
                    args162.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y2")?);
                        Val::tuple(s)
                    });
                    args162.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(binary("add", e.get("y2")?, Val::Int(13i64))?);
                        Val::tuple(s)
                    });
                    fun164.call(args162, kw163)?
                };
            } else {
                {
                    let fun167 = e.get("line")?;
                    let mut args165 = Vec::new();
                    let mut kw166 = Vec::new();
                    args165.push(e.get("c")?);
                    args165.push(e.get("x")?);
                    args165.push(e.get("y1")?);
                    args165.push(e.get("x")?);
                    args165.push(e.get("y2")?);
                    fun167.call(args165, kw166)?
                };
                {
                    let fun170 = e.get("arrow")?;
                    let mut args168 = Vec::new();
                    let mut kw169 = Vec::new();
                    args168.push(e.get("c")?);
                    args168.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y1")?);
                        Val::tuple(s)
                    });
                    args168.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y2")?);
                        Val::tuple(s)
                    });
                    fun170.call(args168, kw169)?
                };
                {
                    let fun173 = e.get("arrow")?;
                    let mut args171 = Vec::new();
                    let mut kw172 = Vec::new();
                    args171.push(e.get("c")?);
                    args171.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y2")?);
                        Val::tuple(s)
                    });
                    args171.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y1")?);
                        Val::tuple(s)
                    });
                    fun173.call(args171, kw172)?
                };
            }
            let assigned174 = binary(
                "sub",
                binary(
                    "add",
                    binary(
                        "truediv",
                        binary("add", e.get("y1")?, e.get("y2")?)?,
                        Val::Int(2i64),
                    )?,
                    binary(
                        "mul",
                        binary(
                            "sub",
                            {
                                let fun177 = e.get("len")?;
                                let mut args175 = Vec::new();
                                let mut kw176 = Vec::new();
                                args175.push(e.get("lines")?);
                                fun177.call(args175, kw176)?
                            },
                            Val::Int(1i64),
                        )?,
                        Val::Int(5i64),
                    )?,
                )?,
                Val::Int(3i64),
            )?;
            e.set("y", assigned174.clone())?;
            for item178 in {
                let fun184 = e.get("enumerate")?;
                let mut args182 = Vec::new();
                let mut kw183 = Vec::new();
                args182.push(e.get("lines")?);
                fun184.call(args182, kw183)?
            }
            .iter()?
            {
                let unpack185 = unpack(item178, 2)?;
                e.set("i", unpack185[0].clone())?;
                e.set("value", unpack185[1].clone())?;
                {
                    let fun181 = e.get("text")?;
                    let mut args179 = Vec::new();
                    let mut kw180 = Vec::new();
                    args179.push(e.get("c")?);
                    args179.push(binary("add", e.get("x")?, Val::Int(9i64))?);
                    args179.push(binary(
                        "sub",
                        e.get("y")?,
                        binary("mul", e.get("i")?, Val::Int(11i64))?,
                    )?);
                    args179.push(e.get("value")?);
                    args179.push(Val::Int(9i64));
                    fun181.call(args179, kw180)?
                };
            }
            Ok(Val::None)
        })
    })?;
    // center
    e.set("center", {
        let params = vec![
            ("c".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("half".into(), Some(Val::Int(13i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun188 = e.get("line")?;
                let mut args186 = Vec::new();
                let mut kw187 = Vec::new();
                args186.push(e.get("c")?);
                args186.push(binary("sub", e.get("x")?, e.get("half")?)?);
                args186.push(e.get("y")?);
                args186.push(binary("add", e.get("x")?, e.get("half")?)?);
                args186.push(e.get("y")?);
                kw187.push(("dash".into(), e.get("CENTER_DASH")?));
                fun188.call(args186, kw187)?
            };
            {
                let fun191 = e.get("line")?;
                let mut args189 = Vec::new();
                let mut kw190 = Vec::new();
                args189.push(e.get("c")?);
                args189.push(e.get("x")?);
                args189.push(binary("sub", e.get("y")?, e.get("half")?)?);
                args189.push(e.get("x")?);
                args189.push(binary("add", e.get("y")?, e.get("half")?)?);
                kw190.push(("dash".into(), e.get("CENTER_DASH")?));
                fun191.call(args189, kw190)?
            };
            Ok(Val::None)
        })
    })?;
    // hatch
    e.set("hatch", {
        let params = vec![
            ("c".into(), None, false),
            ("path".into(), None, false),
            ("bounds".into(), None, false),
            ("spacing".into(), Some(Val::Int(7i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun194 = e.get("c")?.attr("saveState")?;
                let mut args192 = Vec::new();
                let mut kw193 = Vec::new();
                fun194.call(args192, kw193)?
            };
            {
                let fun197 = e.get("c")?.attr("clipPath")?;
                let mut args195 = Vec::new();
                let mut kw196 = Vec::new();
                args195.push(e.get("path")?);
                kw196.push(("stroke".into(), Val::Int(0i64)));
                kw196.push(("fill".into(), Val::Int(0i64)));
                fun197.call(args195, kw196)?
            };
            let assigned198 = e.get("bounds")?;
            let unpack199 = unpack(assigned198.clone(), 4)?;
            e.set("x0", unpack199[0].clone())?;
            e.set("y0", unpack199[1].clone())?;
            e.set("x1", unpack199[2].clone())?;
            e.set("y1", unpack199[3].clone())?;
            for item200 in {
                let fun206 = e.get("range")?;
                let mut args204 = Vec::new();
                let mut kw205 = Vec::new();
                args204.push({
                    let fun209 = e.get("math")?.attr("floor")?;
                    let mut args207 = Vec::new();
                    let mut kw208 = Vec::new();
                    args207.push(binary(
                        "sub",
                        e.get("x0")?,
                        binary("sub", e.get("y1")?, e.get("y0")?)?,
                    )?);
                    fun209.call(args207, kw208)?
                });
                args204.push(binary(
                    "add",
                    {
                        let fun212 = e.get("math")?.attr("ceil")?;
                        let mut args210 = Vec::new();
                        let mut kw211 = Vec::new();
                        args210.push(e.get("x1")?);
                        fun212.call(args210, kw211)?
                    },
                    Val::Int(1i64),
                )?);
                args204.push(e.get("spacing")?);
                fun206.call(args204, kw205)?
            }
            .iter()?
            {
                e.set("offset", item200)?;
                {
                    let fun203 = e.get("line")?;
                    let mut args201 = Vec::new();
                    let mut kw202 = Vec::new();
                    args201.push(e.get("c")?);
                    args201.push(e.get("offset")?);
                    args201.push(e.get("y0")?);
                    args201.push(binary(
                        "add",
                        e.get("offset")?,
                        binary("sub", e.get("y1")?, e.get("y0")?)?,
                    )?);
                    args201.push(e.get("y1")?);
                    args201.push(Val::Float(0.25f64));
                    fun203.call(args201, kw202)?
                };
            }
            {
                let fun215 = e.get("c")?.attr("restoreState")?;
                let mut args213 = Vec::new();
                let mut kw214 = Vec::new();
                fun215.call(args213, kw214)?
            };
            Ok(Val::None)
        })
    })?;
    // path_from_points
    e.set("path_from_points", {
        let params = vec![("c".into(), None, false), ("points".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned216 = {
                let fun219 = e.get("c")?.attr("beginPath")?;
                let mut args217 = Vec::new();
                let mut kw218 = Vec::new();
                fun219.call(args217, kw218)?
            };
            e.set("p", assigned216.clone())?;
            {
                let fun222 = e.get("p")?.attr("moveTo")?;
                let mut args220 = Vec::new();
                let mut kw221 = Vec::new();
                args220.extend(e.get("points")?.get(Val::Int(0i64))?.iter()?);
                fun222.call(args220, kw221)?
            };
            for item223 in e
                .get("points")?
                .get(Val::Slice {
                    start: Some(Val::Int(1i64).integer()?),
                    stop: None,
                    step: 1,
                })?
                .iter()?
            {
                e.set("point", item223)?;
                {
                    let fun226 = e.get("p")?.attr("lineTo")?;
                    let mut args224 = Vec::new();
                    let mut kw225 = Vec::new();
                    args224.extend(e.get("point")?.iter()?);
                    fun226.call(args224, kw225)?
                };
            }
            {
                let fun229 = e.get("p")?.attr("close")?;
                let mut args227 = Vec::new();
                let mut kw228 = Vec::new();
                fun229.call(args227, kw228)?
            };
            return Ok(e.get("p")?);
            Ok(Val::None)
        })
    })?;
    // cutting_plane_ends
    e.set("cutting_plane_ends", {
        let params = vec![
            ("c".into(), None, false),
            ("left".into(), None, false),
            ("right".into(), None, false),
            ("y".into(), None, false),
            ("label".into(), None, false),
            ("rise".into(), Some(Val::Int(21i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun232 = e.get("line")?;
                let mut args230 = Vec::new();
                let mut kw231 = Vec::new();
                args230.push(e.get("c")?);
                args230.push(e.get("left")?);
                args230.push(e.get("y")?);
                args230.push(binary("add", e.get("left")?, Val::Int(16i64))?);
                args230.push(e.get("y")?);
                args230.push(Val::Float(1.0f64));
                fun232.call(args230, kw231)?
            };
            {
                let fun235 = e.get("line")?;
                let mut args233 = Vec::new();
                let mut kw234 = Vec::new();
                args233.push(e.get("c")?);
                args233.push(binary("sub", e.get("right")?, Val::Int(16i64))?);
                args233.push(e.get("y")?);
                args233.push(e.get("right")?);
                args233.push(e.get("y")?);
                args233.push(Val::Float(1.0f64));
                fun235.call(args233, kw234)?
            };
            for item236 in {
                let mut s = Vec::new();
                s.push(e.get("left")?);
                s.push(e.get("right")?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("x", item236)?;
                {
                    let fun239 = e.get("line")?;
                    let mut args237 = Vec::new();
                    let mut kw238 = Vec::new();
                    args237.push(e.get("c")?);
                    args237.push(e.get("x")?);
                    args237.push(e.get("y")?);
                    args237.push(e.get("x")?);
                    args237.push(binary("add", e.get("y")?, e.get("rise")?)?);
                    args237.push(Val::Float(1.0f64));
                    fun239.call(args237, kw238)?
                };
                {
                    let fun242 = e.get("arrow")?;
                    let mut args240 = Vec::new();
                    let mut kw241 = Vec::new();
                    args240.push(e.get("c")?);
                    args240.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(binary("add", e.get("y")?, e.get("rise")?)?);
                        Val::tuple(s)
                    });
                    args240.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y")?);
                        Val::tuple(s)
                    });
                    kw241.push(("length".into(), Val::Int(8i64)));
                    kw241.push(("width".into(), Val::Float(2.5f64)));
                    fun242.call(args240, kw241)?
                };
                {
                    let fun245 = e.get("text")?;
                    let mut args243 = Vec::new();
                    let mut kw244 = Vec::new();
                    args243.push(e.get("c")?);
                    args243.push(e.get("x")?);
                    args243.push(binary(
                        "add",
                        binary("add", e.get("y")?, e.get("rise")?)?,
                        Val::Int(7i64),
                    )?);
                    args243.push(e.get("label")?);
                    args243.push(Val::Int(11i64));
                    kw244.push(("bold".into(), Val::Bool(true)));
                    kw244.push(("align".into(), Val::Str("center".into())));
                    fun245.call(args243, kw244)?
                };
            }
            Ok(Val::None)
        })
    })?;
    // face_view
    e.set("face_view", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun248 = e.get("text")?;
                let mut args246 = Vec::new();
                let mut kw247 = Vec::new();
                args246.push(e.get("c")?);
                args246.push(e.get("CX")?);
                args246.push(Val::Int(734i64));
                args246.push(Val::Str("INSIDE FACE VIEW".into()));
                args246.push(Val::Int(12i64));
                kw247.push(("bold".into(), Val::Bool(true)));
                kw247.push(("align".into(), Val::Str("center".into())));
                fun248.call(args246, kw247)?
            };
            {
                let fun251 = e.get("text")?;
                let mut args249 = Vec::new();
                let mut kw250 = Vec::new();
                args249.push(e.get("c")?);
                args249.push(e.get("CX")?);
                args249.push(Val::Int(718i64));
                args249.push(Val::Str("SCALE 1:1".into()));
                args249.push(Val::Int(9i64));
                kw250.push(("align".into(), Val::Str("center".into())));
                fun251.call(args249, kw250)?
            };
            {
                let fun254 = e.get("c")?.attr("setLineWidth")?;
                let mut args252 = Vec::new();
                let mut kw253 = Vec::new();
                args252.push(e.get("VISIBLE")?);
                fun254.call(args252, kw253)?
            };
            {
                let fun257 = e.get("c")?.attr("circle")?;
                let mut args255 = Vec::new();
                let mut kw256 = Vec::new();
                args255.push(e.get("CX")?);
                args255.push(e.get("CY")?);
                args255.push(e.get("RADIUS")?);
                kw256.push(("stroke".into(), Val::Int(1i64)));
                kw256.push(("fill".into(), Val::Int(0i64)));
                fun257.call(args255, kw256)?
            };
            {
                let fun260 = e.get("line")?;
                let mut args258 = Vec::new();
                let mut kw259 = Vec::new();
                args258.push(e.get("c")?);
                args258.push(binary(
                    "sub",
                    binary("sub", e.get("CX")?, e.get("RADIUS")?)?,
                    Val::Int(13i64),
                )?);
                args258.push(e.get("CY")?);
                args258.push(binary(
                    "add",
                    binary("add", e.get("CX")?, e.get("RADIUS")?)?,
                    Val::Int(13i64),
                )?);
                args258.push(e.get("CY")?);
                kw259.push(("dash".into(), e.get("CENTER_DASH")?));
                fun260.call(args258, kw259)?
            };
            {
                let fun263 = e.get("line")?;
                let mut args261 = Vec::new();
                let mut kw262 = Vec::new();
                args261.push(e.get("c")?);
                args261.push(e.get("CX")?);
                args261.push(binary(
                    "sub",
                    binary("sub", e.get("CY")?, e.get("RADIUS")?)?,
                    Val::Int(13i64),
                )?);
                args261.push(e.get("CX")?);
                args261.push(binary(
                    "add",
                    binary("add", e.get("CY")?, e.get("RADIUS")?)?,
                    Val::Int(13i64),
                )?);
                kw262.push(("dash".into(), e.get("CENTER_DASH")?));
                fun263.call(args261, kw262)?
            };
            for item264 in {
                let fun290 = e.get("enumerate")?;
                let mut args288 = Vec::new();
                let mut kw289 = Vec::new();
                args288.push(e.get("hole_positions")?);
                args288.push(Val::Int(1i64));
                fun290.call(args288, kw289)?
            }
            .iter()?
            {
                let unpack291 = unpack(item264, 2)?;
                e.set("i", unpack291[0].clone())?;
                let unpack292 = unpack(unpack291[1].clone(), 2)?;
                e.set("px", unpack292[0].clone())?;
                e.set("py", unpack292[1].clone())?;
                let assigned265 = {
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("CX")?,
                        binary("mul", e.get("px")?, e.get("inch")?)?,
                    )?);
                    s.push(binary(
                        "add",
                        e.get("CY")?,
                        binary("mul", e.get("py")?, e.get("inch")?)?,
                    )?);
                    Val::tuple(s)
                };
                let unpack266 = unpack(assigned265.clone(), 2)?;
                e.set("x", unpack266[0].clone())?;
                e.set("y", unpack266[1].clone())?;
                let assigned267 = binary("mul", e.get("hole_radius")?, e.get("inch")?)?;
                e.set("minor", assigned267.clone())?;
                {
                    let fun270 = e.get("c")?.attr("setLineWidth")?;
                    let mut args268 = Vec::new();
                    let mut kw269 = Vec::new();
                    args268.push(e.get("VISIBLE")?);
                    fun270.call(args268, kw269)?
                };
                {
                    let fun273 = e.get("c")?.attr("circle")?;
                    let mut args271 = Vec::new();
                    let mut kw272 = Vec::new();
                    args271.push(e.get("x")?);
                    args271.push(e.get("y")?);
                    args271.push(e.get("minor")?);
                    kw272.push(("stroke".into(), Val::Int(1i64)));
                    kw272.push(("fill".into(), Val::Int(0i64)));
                    fun273.call(args271, kw272)?
                };
                {
                    let fun276 = e.get("c")?.attr("setLineWidth")?;
                    let mut args274 = Vec::new();
                    let mut kw275 = Vec::new();
                    args274.push(e.get("THIN")?);
                    fun276.call(args274, kw275)?
                };
                let assigned277 = binary(
                    "add",
                    e.get("minor")?,
                    binary("mul", Val::Float(0.04f64), e.get("inch")?)?,
                )?;
                e.set("root", assigned277.clone())?;
                {
                    let fun280 = e.get("c")?.attr("arc")?;
                    let mut args278 = Vec::new();
                    let mut kw279 = Vec::new();
                    args278.push(binary("sub", e.get("x")?, e.get("root")?)?);
                    args278.push(binary("sub", e.get("y")?, e.get("root")?)?);
                    args278.push(binary("add", e.get("x")?, e.get("root")?)?);
                    args278.push(binary("add", e.get("y")?, e.get("root")?)?);
                    args278.push(Val::Int(35i64));
                    args278.push(Val::Int(270i64));
                    fun280.call(args278, kw279)?
                };
                {
                    let fun283 = e.get("center")?;
                    let mut args281 = Vec::new();
                    let mut kw282 = Vec::new();
                    args281.push(e.get("c")?);
                    args281.push(e.get("x")?);
                    args281.push(e.get("y")?);
                    args281.push(Val::Int(24i64));
                    fun283.call(args281, kw282)?
                };
                {
                    let fun286 = e.get("text")?;
                    let mut args284 = Vec::new();
                    let mut kw285 = Vec::new();
                    args284.push(e.get("c")?);
                    args284.push(e.get("x")?);
                    args284.push(binary("add", e.get("y")?, Val::Int(31i64))?);
                    args284.push({
                        let mut str287 = String::new();
                        str287.push_str("P");
                        str287.push_str(&format(&e.get("i")?, &String::new())?);
                        Val::Str(str287)
                    });
                    args284.push(Val::Int(10i64));
                    kw285.push(("bold".into(), Val::Bool(true)));
                    kw285.push(("align".into(), Val::Str("center".into())));
                    fun286.call(args284, kw285)?
                };
            }
            let assigned293 = {
                let mut s = Vec::new();
                s.push(binary(
                    "add",
                    e.get("CX")?,
                    binary(
                        "mul",
                        e.get("register_position")?.get(Val::Int(0i64))?,
                        e.get("inch")?,
                    )?,
                )?);
                s.push(binary(
                    "add",
                    e.get("CY")?,
                    binary(
                        "mul",
                        e.get("register_position")?.get(Val::Int(1i64))?,
                        e.get("inch")?,
                    )?,
                )?);
                Val::tuple(s)
            };
            let unpack294 = unpack(assigned293.clone(), 2)?;
            e.set("rx", unpack294[0].clone())?;
            e.set("ry", unpack294[1].clone())?;
            {
                let fun297 = e.get("c")?.attr("setLineWidth")?;
                let mut args295 = Vec::new();
                let mut kw296 = Vec::new();
                args295.push(e.get("VISIBLE")?);
                fun297.call(args295, kw296)?
            };
            {
                let fun300 = e.get("c")?.attr("circle")?;
                let mut args298 = Vec::new();
                let mut kw299 = Vec::new();
                args298.push(e.get("rx")?);
                args298.push(e.get("ry")?);
                args298.push(binary(
                    "truediv",
                    binary("mul", e.get("register_drill_diameter")?, e.get("inch")?)?,
                    Val::Int(2i64),
                )?);
                kw299.push(("stroke".into(), Val::Int(1i64)));
                kw299.push(("fill".into(), Val::Int(0i64)));
                fun300.call(args298, kw299)?
            };
            {
                let fun303 = e.get("center")?;
                let mut args301 = Vec::new();
                let mut kw302 = Vec::new();
                args301.push(e.get("c")?);
                args301.push(e.get("rx")?);
                args301.push(e.get("ry")?);
                args301.push(Val::Int(10i64));
                fun303.call(args301, kw302)?
            };
            {
                let fun306 = e.get("cutting_plane_ends")?;
                let mut args304 = Vec::new();
                let mut kw305 = Vec::new();
                args304.push(e.get("c")?);
                args304.push(binary(
                    "sub",
                    binary("sub", e.get("CX")?, e.get("RADIUS")?)?,
                    Val::Int(24i64),
                )?);
                args304.push(binary(
                    "add",
                    binary("add", e.get("CX")?, e.get("RADIUS")?)?,
                    Val::Int(24i64),
                )?);
                args304.push(e.get("CY")?);
                args304.push(Val::Str("A".into()));
                fun306.call(args304, kw305)?
            };
            {
                let fun309 = e.get("circular_leader")?;
                let mut args307 = Vec::new();
                let mut kw308 = Vec::new();
                args307.push(e.get("c")?);
                args307.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("CX")?,
                        binary(
                            "mul",
                            e.get("hole_positions")?
                                .get(Val::Int(1i64))?
                                .get(Val::Int(0i64))?,
                            e.get("inch")?,
                        )?,
                    )?);
                    s.push(e.get("CY")?);
                    Val::tuple(s)
                });
                args307.push(binary("mul", e.get("hole_radius")?, e.get("inch")?)?);
                args307.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(484i64));
                    s.push(Val::Int(600i64));
                    Val::tuple(s)
                });
                args307.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(510i64));
                    s.push(Val::Int(600i64));
                    Val::tuple(s)
                });
                args307.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("2X 1/4-18 NPT THRU".into()));
                    s.push(Val::Str("TAP FROM OUTSIDE FACE".into()));
                    s.push(Val::Str("P1, P2 - SEE NOTE 2".into()));
                    Val::list(s)
                });
                args307.push(Val::Int(10i64));
                fun309.call(args307, kw308)?
            };
            {
                let fun312 = e.get("circular_leader")?;
                let mut args310 = Vec::new();
                let mut kw311 = Vec::new();
                args310.push(e.get("c")?);
                args310.push({
                    let mut s = Vec::new();
                    s.push(e.get("rx")?);
                    s.push(e.get("ry")?);
                    Val::tuple(s)
                });
                args310.push(binary(
                    "truediv",
                    binary("mul", e.get("register_drill_diameter")?, e.get("inch")?)?,
                    Val::Int(2i64),
                )?);
                args310.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(322i64));
                    s.push(Val::Int(415i64));
                    Val::tuple(s)
                });
                args310.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(342i64));
                    s.push(Val::Int(415i64));
                    Val::tuple(s)
                });
                args310.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("R1 - BLIND REGISTER".into()));
                    s.push(Val::Str("SEE DETAIL B".into()));
                    Val::list(s)
                });
                args310.push(Val::Int(9i64));
                fun312.call(args310, kw311)?
            };
            {
                let fun315 = e.get("horizontal_dimension")?;
                let mut args313 = Vec::new();
                let mut kw314 = Vec::new();
                args313.push(e.get("c")?);
                args313.push(binary("sub", e.get("CX")?, e.get("RADIUS")?)?);
                args313.push(binary("add", e.get("CX")?, e.get("RADIUS")?)?);
                args313.push(e.get("CY")?);
                args313.push(Val::Int(286i64));
                args313.push({
                    let mut str316 = String::new();
                    str316.push_str("Ø");
                    str316.push_str(&format(
                        &e.get("disc_diameter")?,
                        &val_string({
                            let mut str317 = String::new();
                            str317.push_str(".3f");
                            Val::Str(str317)
                        })?,
                    )?);
                    Val::Str(str316)
                });
                args313.push(Val::Int(11i64));
                fun315.call(args313, kw314)?
            };
            Ok(Val::None)
        })
    })?;
    // port_section
    e.set("port_section", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned318 = Val::Int(226i64);
            e.set("bottom", assigned318.clone())?;
            let assigned319 = binary(
                "add",
                e.get("bottom")?,
                binary("mul", e.get("disc_thickness")?, e.get("inch")?)?,
            )?;
            e.set("top", assigned319.clone())?;
            let assigned320 = {
                let mut s = Vec::new();
                s.push(binary("sub", e.get("CX")?, e.get("RADIUS")?)?);
                s.push(binary("add", e.get("CX")?, e.get("RADIUS")?)?);
                Val::tuple(s)
            };
            let unpack321 = unpack(assigned320.clone(), 2)?;
            e.set("left", unpack321[0].clone())?;
            e.set("right", unpack321[1].clone())?;
            let assigned322 = {
                let fun325 = e.get("path_from_points")?;
                let mut args323 = Vec::new();
                let mut kw324 = Vec::new();
                args323.push(e.get("c")?);
                args323.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("left")?);
                        s.push(e.get("bottom")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("right")?);
                        s.push(e.get("bottom")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("right")?);
                        s.push(e.get("top")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("left")?);
                        s.push(e.get("top")?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                fun325.call(args323, kw324)?
            };
            e.set("outer", assigned322.clone())?;
            {
                let fun328 = e.get("hatch")?;
                let mut args326 = Vec::new();
                let mut kw327 = Vec::new();
                args326.push(e.get("c")?);
                args326.push(e.get("outer")?);
                args326.push({
                    let mut s = Vec::new();
                    s.push(e.get("left")?);
                    s.push(e.get("bottom")?);
                    s.push(e.get("right")?);
                    s.push(e.get("top")?);
                    Val::tuple(s)
                });
                kw327.push(("spacing".into(), Val::Int(6i64)));
                fun328.call(args326, kw327)?
            };
            {
                let fun331 = e.get("c")?.attr("setLineWidth")?;
                let mut args329 = Vec::new();
                let mut kw330 = Vec::new();
                args329.push(e.get("VISIBLE")?);
                fun331.call(args329, kw330)?
            };
            {
                let fun334 = e.get("c")?.attr("drawPath")?;
                let mut args332 = Vec::new();
                let mut kw333 = Vec::new();
                args332.push(e.get("outer")?);
                kw333.push(("stroke".into(), Val::Int(1i64)));
                kw333.push(("fill".into(), Val::Int(0i64)));
                fun334.call(args332, kw333)?
            };
            for item335 in e.get("hole_positions")?.iter()? {
                let unpack365 = unpack(item335, 2)?;
                e.set("px", unpack365[0].clone())?;
                e.set("_", unpack365[1].clone())?;
                let assigned336 = binary(
                    "add",
                    e.get("CX")?,
                    binary("mul", e.get("px")?, e.get("inch")?)?,
                )?;
                e.set("x", assigned336.clone())?;
                let assigned337 = binary("mul", e.get("hole_radius")?, e.get("inch")?)?;
                e.set("r_inside", assigned337.clone())?;
                let assigned338 = binary(
                    "add",
                    e.get("r_inside")?,
                    binary(
                        "truediv",
                        binary("mul", e.get("disc_thickness")?, e.get("inch")?)?,
                        Val::Int(32i64),
                    )?,
                )?;
                e.set("r_outside", assigned338.clone())?;
                let assigned339 = {
                    let fun342 = e.get("path_from_points")?;
                    let mut args340 = Vec::new();
                    let mut kw341 = Vec::new();
                    args340.push(e.get("c")?);
                    args340.push({
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary("sub", e.get("x")?, e.get("r_outside")?)?);
                            s.push(e.get("bottom")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary("add", e.get("x")?, e.get("r_outside")?)?);
                            s.push(e.get("bottom")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary("add", e.get("x")?, e.get("r_inside")?)?);
                            s.push(e.get("top")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary("sub", e.get("x")?, e.get("r_inside")?)?);
                            s.push(e.get("top")?);
                            Val::tuple(s)
                        });
                        Val::list(s)
                    });
                    fun342.call(args340, kw341)?
                };
                e.set("opening", assigned339.clone())?;
                {
                    let fun345 = e.get("c")?.attr("setFillColorRGB")?;
                    let mut args343 = Vec::new();
                    let mut kw344 = Vec::new();
                    args343.push(Val::Int(1i64));
                    args343.push(Val::Int(1i64));
                    args343.push(Val::Int(1i64));
                    fun345.call(args343, kw344)?
                };
                {
                    let fun348 = e.get("c")?.attr("drawPath")?;
                    let mut args346 = Vec::new();
                    let mut kw347 = Vec::new();
                    args346.push(e.get("opening")?);
                    kw347.push(("stroke".into(), Val::Int(0i64)));
                    kw347.push(("fill".into(), Val::Int(1i64)));
                    fun348.call(args346, kw347)?
                };
                {
                    let fun351 = e.get("c")?.attr("setFillColorRGB")?;
                    let mut args349 = Vec::new();
                    let mut kw350 = Vec::new();
                    args349.push(Val::Int(0i64));
                    args349.push(Val::Int(0i64));
                    args349.push(Val::Int(0i64));
                    fun351.call(args349, kw350)?
                };
                {
                    let fun354 = e.get("line")?;
                    let mut args352 = Vec::new();
                    let mut kw353 = Vec::new();
                    args352.push(e.get("c")?);
                    args352.push(binary("sub", e.get("x")?, e.get("r_outside")?)?);
                    args352.push(e.get("bottom")?);
                    args352.push(binary("sub", e.get("x")?, e.get("r_inside")?)?);
                    args352.push(e.get("top")?);
                    args352.push(e.get("VISIBLE")?);
                    fun354.call(args352, kw353)?
                };
                {
                    let fun357 = e.get("line")?;
                    let mut args355 = Vec::new();
                    let mut kw356 = Vec::new();
                    args355.push(e.get("c")?);
                    args355.push(binary("add", e.get("x")?, e.get("r_outside")?)?);
                    args355.push(e.get("bottom")?);
                    args355.push(binary("add", e.get("x")?, e.get("r_inside")?)?);
                    args355.push(e.get("top")?);
                    args355.push(e.get("VISIBLE")?);
                    fun357.call(args355, kw356)?
                };
                for item358 in {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Int(1i64))?);
                    s.push(Val::Int(1i64));
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("sign", item358)?;
                    {
                        let fun361 = e.get("line")?;
                        let mut args359 = Vec::new();
                        let mut kw360 = Vec::new();
                        args359.push(e.get("c")?);
                        args359.push(binary(
                            "add",
                            e.get("x")?,
                            binary(
                                "mul",
                                e.get("sign")?,
                                binary(
                                    "add",
                                    e.get("r_outside")?,
                                    binary("mul", Val::Float(0.04f64), e.get("inch")?)?,
                                )?,
                            )?,
                        )?);
                        args359.push(e.get("bottom")?);
                        args359.push(binary(
                            "add",
                            e.get("x")?,
                            binary(
                                "mul",
                                e.get("sign")?,
                                binary(
                                    "add",
                                    e.get("r_inside")?,
                                    binary("mul", Val::Float(0.04f64), e.get("inch")?)?,
                                )?,
                            )?,
                        )?);
                        args359.push(e.get("top")?);
                        fun361.call(args359, kw360)?
                    };
                }
                {
                    let fun364 = e.get("line")?;
                    let mut args362 = Vec::new();
                    let mut kw363 = Vec::new();
                    args362.push(e.get("c")?);
                    args362.push(e.get("x")?);
                    args362.push(binary("sub", e.get("bottom")?, Val::Int(9i64))?);
                    args362.push(e.get("x")?);
                    args362.push(binary("add", e.get("top")?, Val::Int(9i64))?);
                    kw363.push(("dash".into(), e.get("CENTER_DASH")?));
                    fun364.call(args362, kw363)?
                };
            }
            let assigned366 = binary(
                "add",
                e.get("CX")?,
                binary(
                    "mul",
                    e.get("register_position")?.get(Val::Int(0i64))?,
                    e.get("inch")?,
                )?,
            )?;
            e.set("rx", assigned366.clone())?;
            let assigned367 = binary(
                "truediv",
                binary("mul", e.get("register_drill_diameter")?, e.get("inch")?)?,
                Val::Int(2i64),
            )?;
            e.set("rr", assigned367.clone())?;
            let assigned368 = binary(
                "sub",
                e.get("top")?,
                binary("mul", e.get("register_depth")?, e.get("inch")?)?,
            )?;
            e.set("tip", assigned368.clone())?;
            let assigned369 = binary(
                "add",
                e.get("tip")?,
                binary("truediv", e.get("rr")?, {
                    let fun372 = e.get("math")?.attr("tan")?;
                    let mut args370 = Vec::new();
                    let mut kw371 = Vec::new();
                    args370.push({
                        let fun375 = e.get("math")?.attr("radians")?;
                        let mut args373 = Vec::new();
                        let mut kw374 = Vec::new();
                        args373.push(binary("truediv", Val::Int(135i64), Val::Int(2i64))?);
                        fun375.call(args373, kw374)?
                    });
                    fun372.call(args370, kw371)?
                })?,
            )?;
            e.set("shoulder", assigned369.clone())?;
            let assigned376 = {
                let fun379 = e.get("path_from_points")?;
                let mut args377 = Vec::new();
                let mut kw378 = Vec::new();
                args377.push(e.get("c")?);
                args377.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("sub", e.get("rx")?, e.get("rr")?)?);
                        s.push(e.get("top")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("sub", e.get("rx")?, e.get("rr")?)?);
                        s.push(e.get("shoulder")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("rx")?);
                        s.push(e.get("tip")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("add", e.get("rx")?, e.get("rr")?)?);
                        s.push(e.get("shoulder")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("add", e.get("rx")?, e.get("rr")?)?);
                        s.push(e.get("top")?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                fun379.call(args377, kw378)?
            };
            e.set("opening", assigned376.clone())?;
            {
                let fun382 = e.get("c")?.attr("setFillColorRGB")?;
                let mut args380 = Vec::new();
                let mut kw381 = Vec::new();
                args380.push(Val::Int(1i64));
                args380.push(Val::Int(1i64));
                args380.push(Val::Int(1i64));
                fun382.call(args380, kw381)?
            };
            {
                let fun385 = e.get("c")?.attr("drawPath")?;
                let mut args383 = Vec::new();
                let mut kw384 = Vec::new();
                args383.push(e.get("opening")?);
                kw384.push(("stroke".into(), Val::Int(0i64)));
                kw384.push(("fill".into(), Val::Int(1i64)));
                fun385.call(args383, kw384)?
            };
            {
                let fun388 = e.get("c")?.attr("setFillColorRGB")?;
                let mut args386 = Vec::new();
                let mut kw387 = Vec::new();
                args386.push(Val::Int(0i64));
                args386.push(Val::Int(0i64));
                args386.push(Val::Int(0i64));
                fun388.call(args386, kw387)?
            };
            for item389 in {
                let fun395 = e.get("zip")?;
                let mut args393 = Vec::new();
                let mut kw394 = Vec::new();
                args393.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("sub", e.get("rx")?, e.get("rr")?)?);
                        s.push(e.get("top")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("sub", e.get("rx")?, e.get("rr")?)?);
                        s.push(e.get("shoulder")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("rx")?);
                        s.push(e.get("tip")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("add", e.get("rx")?, e.get("rr")?)?);
                        s.push(e.get("shoulder")?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args393.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("sub", e.get("rx")?, e.get("rr")?)?);
                        s.push(e.get("shoulder")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("rx")?);
                        s.push(e.get("tip")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("add", e.get("rx")?, e.get("rr")?)?);
                        s.push(e.get("shoulder")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("add", e.get("rx")?, e.get("rr")?)?);
                        s.push(e.get("top")?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                fun395.call(args393, kw394)?
            }
            .iter()?
            {
                let unpack396 = unpack(item389, 2)?;
                e.set("a", unpack396[0].clone())?;
                e.set("b", unpack396[1].clone())?;
                {
                    let fun392 = e.get("line")?;
                    let mut args390 = Vec::new();
                    let mut kw391 = Vec::new();
                    args390.push(e.get("c")?);
                    args390.extend(e.get("a")?.iter()?);
                    args390.extend(e.get("b")?.iter()?);
                    args390.push(e.get("VISIBLE")?);
                    fun392.call(args390, kw391)?
                };
            }
            {
                let fun399 = e.get("line")?;
                let mut args397 = Vec::new();
                let mut kw398 = Vec::new();
                args397.push(e.get("c")?);
                args397.push(e.get("rx")?);
                args397.push(binary("sub", e.get("bottom")?, Val::Int(9i64))?);
                args397.push(e.get("rx")?);
                args397.push(binary("add", e.get("top")?, Val::Int(9i64))?);
                kw398.push(("dash".into(), e.get("CENTER_DASH")?));
                fun399.call(args397, kw398)?
            };
            {
                let fun402 = e.get("vertical_dimension")?;
                let mut args400 = Vec::new();
                let mut kw401 = Vec::new();
                args400.push(e.get("c")?);
                args400.push(Val::Int(493i64));
                args400.push(e.get("bottom")?);
                args400.push(e.get("top")?);
                args400.push(e.get("right")?);
                args400.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut str403 = String::new();
                        str403.push_str(&format(
                            &e.get("disc_thickness")?,
                            &val_string({
                                let mut str404 = String::new();
                                str404.push_str(".3f");
                                Val::Str(str404)
                            })?,
                        )?);
                        Val::Str(str403)
                    });
                    Val::list(s)
                });
                kw401.push(("outside".into(), Val::Bool(true)));
                fun402.call(args400, kw401)?
            };
            {
                let fun407 = e.get("text")?;
                let mut args405 = Vec::new();
                let mut kw406 = Vec::new();
                args405.push(e.get("c")?);
                args405.push(e.get("CX")?);
                args405.push(Val::Int(194i64));
                args405.push(Val::Str("SECTION A-A".into()));
                args405.push(Val::Int(11i64));
                kw406.push(("bold".into(), Val::Bool(true)));
                kw406.push(("align".into(), Val::Str("center".into())));
                fun407.call(args405, kw406)?
            };
            {
                let fun410 = e.get("text")?;
                let mut args408 = Vec::new();
                let mut kw409 = Vec::new();
                args408.push(e.get("c")?);
                args408.push(e.get("CX")?);
                args408.push(Val::Int(180i64));
                args408.push(Val::Str("SCALE 1:1 - THREADS SHOWN CONVENTIONALLY".into()));
                args408.push(Val::Int(8i64));
                kw409.push(("align".into(), Val::Str("center".into())));
                fun410.call(args408, kw409)?
            };
            {
                let fun413 = e.get("leader")?;
                let mut args411 = Vec::new();
                let mut kw412 = Vec::new();
                args411.push(e.get("c")?);
                args411.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(205i64));
                    s.push(e.get("top")?);
                    Val::tuple(s)
                });
                args411.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(140i64));
                    s.push(Val::Int(273i64));
                    Val::tuple(s)
                });
                args411.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(110i64));
                    s.push(Val::Int(273i64));
                    Val::tuple(s)
                });
                args411.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("INSIDE FACE".into()));
                    Val::list(s)
                });
                args411.push(Val::Float(8.5f64));
                fun413.call(args411, kw412)?
            };
            {
                let fun416 = e.get("leader")?;
                let mut args414 = Vec::new();
                let mut kw415 = Vec::new();
                args414.push(e.get("c")?);
                args414.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(405i64));
                    s.push(e.get("bottom")?);
                    Val::tuple(s)
                });
                args414.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(425i64));
                    s.push(Val::Int(190i64));
                    Val::tuple(s)
                });
                args414.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(445i64));
                    s.push(Val::Int(190i64));
                    Val::tuple(s)
                });
                args414.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("OUTSIDE FACE".into()));
                    s.push(Val::Str("NPT ENTRY / WELD FACE".into()));
                    Val::list(s)
                });
                args414.push(Val::Float(8.5f64));
                fun416.call(args414, kw415)?
            };
            Ok(Val::None)
        })
    })?;
    // register_section
    e.set("register_section", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned417 = binary("mul", Val::Int(4i64), e.get("inch")?)?;
            e.set("scale", assigned417.clone())?;
            let assigned418 = {
                let mut s = Vec::new();
                s.push(Val::Int(900i64));
                s.push(Val::Int(630i64));
                s.push(Val::Int(122i64));
                Val::tuple(s)
            };
            let unpack419 = unpack(assigned418.clone(), 3)?;
            e.set("x", unpack419[0].clone())?;
            e.set("top", unpack419[1].clone())?;
            e.set("half_width", unpack419[2].clone())?;
            let assigned420 = binary(
                "sub",
                e.get("top")?,
                binary("mul", e.get("disc_thickness")?, e.get("scale")?)?,
            )?;
            e.set("bottom", assigned420.clone())?;
            let assigned421 = binary(
                "truediv",
                binary("mul", e.get("register_drill_diameter")?, e.get("scale")?)?,
                Val::Int(2i64),
            )?;
            e.set("radius", assigned421.clone())?;
            let assigned422 = binary(
                "sub",
                e.get("top")?,
                binary("mul", e.get("register_depth")?, e.get("scale")?)?,
            )?;
            e.set("tip", assigned422.clone())?;
            let assigned423 = Val::Int(135i64);
            e.set("point_angle", assigned423.clone())?;
            let assigned424 = binary("truediv", e.get("radius")?, {
                let fun427 = e.get("math")?.attr("tan")?;
                let mut args425 = Vec::new();
                let mut kw426 = Vec::new();
                args425.push({
                    let fun430 = e.get("math")?.attr("radians")?;
                    let mut args428 = Vec::new();
                    let mut kw429 = Vec::new();
                    args428.push(binary("truediv", e.get("point_angle")?, Val::Int(2i64))?);
                    fun430.call(args428, kw429)?
                });
                fun427.call(args425, kw426)?
            })?;
            e.set("point_height", assigned424.clone())?;
            let assigned431 = binary("add", e.get("tip")?, e.get("point_height")?)?;
            e.set("shoulder", assigned431.clone())?;
            {
                let fun434 = e.get("text")?;
                let mut args432 = Vec::new();
                let mut kw433 = Vec::new();
                args432.push(e.get("c")?);
                args432.push(e.get("x")?);
                args432.push(Val::Int(734i64));
                args432.push(Val::Str("DETAIL B - SECTION AT R1".into()));
                args432.push(Val::Int(12i64));
                kw433.push(("bold".into(), Val::Bool(true)));
                kw433.push(("align".into(), Val::Str("center".into())));
                fun434.call(args432, kw433)?
            };
            {
                let fun437 = e.get("text")?;
                let mut args435 = Vec::new();
                let mut kw436 = Vec::new();
                args435.push(e.get("c")?);
                args435.push(e.get("x")?);
                args435.push(Val::Int(718i64));
                args435.push(Val::Str("LOCAL VIEW AT R1 - SCALE 4:1".into()));
                args435.push(Val::Int(9i64));
                kw436.push(("align".into(), Val::Str("center".into())));
                fun437.call(args435, kw436)?
            };
            let assigned438 = {
                let mut s = Vec::new();
                s.push(binary("sub", e.get("x")?, e.get("half_width")?)?);
                s.push(binary("add", e.get("x")?, e.get("half_width")?)?);
                Val::tuple(s)
            };
            let unpack439 = unpack(assigned438.clone(), 2)?;
            e.set("left", unpack439[0].clone())?;
            e.set("right", unpack439[1].clone())?;
            let assigned440 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("left")?);
                    s.push(e.get("top")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("x")?, e.get("radius")?)?);
                    s.push(e.get("top")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("x")?, e.get("radius")?)?);
                    s.push(e.get("shoulder")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("tip")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("x")?, e.get("radius")?)?);
                    s.push(e.get("shoulder")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("x")?, e.get("radius")?)?);
                    s.push(e.get("top")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("right")?);
                    s.push(e.get("top")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("right")?);
                    s.push(binary("sub", e.get("top")?, Val::Int(23i64))?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("right")?, Val::Int(4i64))?);
                    s.push(binary("sub", e.get("top")?, Val::Int(30i64))?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("right")?, Val::Int(4i64))?);
                    s.push(binary("sub", e.get("top")?, Val::Int(40i64))?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("right")?);
                    s.push(binary("sub", e.get("top")?, Val::Int(47i64))?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("right")?);
                    s.push(e.get("bottom")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("left")?);
                    s.push(e.get("bottom")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("left")?);
                    s.push(binary("add", e.get("bottom")?, Val::Int(23i64))?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("left")?, Val::Int(4i64))?);
                    s.push(binary("add", e.get("bottom")?, Val::Int(30i64))?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("left")?, Val::Int(4i64))?);
                    s.push(binary("add", e.get("bottom")?, Val::Int(40i64))?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("left")?);
                    s.push(binary("add", e.get("bottom")?, Val::Int(47i64))?);
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("points", assigned440.clone())?;
            let assigned441 = {
                let fun444 = e.get("path_from_points")?;
                let mut args442 = Vec::new();
                let mut kw443 = Vec::new();
                args442.push(e.get("c")?);
                args442.push(e.get("points")?);
                fun444.call(args442, kw443)?
            };
            e.set("material", assigned441.clone())?;
            {
                let fun447 = e.get("hatch")?;
                let mut args445 = Vec::new();
                let mut kw446 = Vec::new();
                args445.push(e.get("c")?);
                args445.push(e.get("material")?);
                args445.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("left")?, Val::Int(5i64))?);
                    s.push(e.get("bottom")?);
                    s.push(binary("add", e.get("right")?, Val::Int(5i64))?);
                    s.push(e.get("top")?);
                    Val::tuple(s)
                });
                kw446.push(("spacing".into(), Val::Int(8i64)));
                fun447.call(args445, kw446)?
            };
            {
                let fun450 = e.get("c")?.attr("setLineWidth")?;
                let mut args448 = Vec::new();
                let mut kw449 = Vec::new();
                args448.push(e.get("VISIBLE")?);
                fun450.call(args448, kw449)?
            };
            {
                let fun453 = e.get("c")?.attr("drawPath")?;
                let mut args451 = Vec::new();
                let mut kw452 = Vec::new();
                args451.push(e.get("material")?);
                kw452.push(("stroke".into(), Val::Int(1i64)));
                kw452.push(("fill".into(), Val::Int(0i64)));
                fun453.call(args451, kw452)?
            };
            {
                let fun456 = e.get("line")?;
                let mut args454 = Vec::new();
                let mut kw455 = Vec::new();
                args454.push(e.get("c")?);
                args454.push(e.get("x")?);
                args454.push(binary("sub", e.get("bottom")?, Val::Int(9i64))?);
                args454.push(e.get("x")?);
                args454.push(binary("add", e.get("top")?, Val::Int(18i64))?);
                kw455.push(("dash".into(), e.get("CENTER_DASH")?));
                fun456.call(args454, kw455)?
            };
            {
                let fun459 = e.get("horizontal_dimension")?;
                let mut args457 = Vec::new();
                let mut kw458 = Vec::new();
                args457.push(e.get("c")?);
                args457.push(binary("sub", e.get("x")?, e.get("radius")?)?);
                args457.push(binary("add", e.get("x")?, e.get("radius")?)?);
                args457.push(e.get("top")?);
                args457.push(Val::Int(674i64));
                args457.push(Val::Str("Ø9/64".into()));
                args457.push(Val::Int(10i64));
                fun459.call(args457, kw458)?
            };
            {
                let fun462 = e.get("vertical_dimension")?;
                let mut args460 = Vec::new();
                let mut kw461 = Vec::new();
                args460.push(e.get("c")?);
                args460.push(Val::Int(1050i64));
                args460.push(e.get("tip")?);
                args460.push(e.get("top")?);
                args460.push(e.get("right")?);
                args460.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut str463 = String::new();
                        str463.push_str(&format(
                            &e.get("register_depth")?,
                            &val_string({
                                let mut str464 = String::new();
                                str464.push_str(".3f");
                                Val::Str(str464)
                            })?,
                        )?);
                        Val::Str(str463)
                    });
                    s.push(Val::Str("TO TIP".into()));
                    Val::list(s)
                });
                fun462.call(args460, kw461)?
            };
            {
                let fun467 = e.get("line")?;
                let mut args465 = Vec::new();
                let mut kw466 = Vec::new();
                args465.push(e.get("c")?);
                args465.push(binary("add", e.get("x")?, Val::Int(4i64))?);
                args465.push(e.get("tip")?);
                args465.push(binary("add", e.get("right")?, Val::Int(4i64))?);
                args465.push(e.get("tip")?);
                fun467.call(args465, kw466)?
            };
            let assigned468 = binary("sub", e.get("disc_thickness")?, e.get("register_depth")?)?;
            e.set("remaining", assigned468.clone())?;
            {
                let fun471 = e.get("vertical_dimension")?;
                let mut args469 = Vec::new();
                let mut kw470 = Vec::new();
                args469.push(e.get("c")?);
                args469.push(Val::Int(1125i64));
                args469.push(e.get("bottom")?);
                args469.push(e.get("tip")?);
                args469.push(e.get("right")?);
                args469.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut str472 = String::new();
                        str472.push_str(&format(
                            &e.get("remaining")?,
                            &val_string({
                                let mut str473 = String::new();
                                str473.push_str(".3f");
                                Val::Str(str473)
                            })?,
                        )?);
                        str472.push_str(" REF");
                        Val::Str(str472)
                    });
                    s.push(Val::Str("WEB".into()));
                    Val::list(s)
                });
                fun471.call(args469, kw470)?
            };
            {
                let fun476 = e.get("text")?;
                let mut args474 = Vec::new();
                let mut kw475 = Vec::new();
                args474.push(e.get("c")?);
                args474.push(e.get("left")?);
                args474.push(binary("add", e.get("top")?, Val::Int(13i64))?);
                args474.push(Val::Str("INSIDE FACE".into()));
                args474.push(Val::Float(8.5f64));
                fun476.call(args474, kw475)?
            };
            {
                let fun479 = e.get("text")?;
                let mut args477 = Vec::new();
                let mut kw478 = Vec::new();
                args477.push(e.get("c")?);
                args477.push(e.get("left")?);
                args477.push(binary("sub", e.get("bottom")?, Val::Int(16i64))?);
                args477.push(Val::Str("OUTSIDE FACE".into()));
                args477.push(Val::Float(8.5f64));
                fun479.call(args477, kw478)?
            };
            {
                let fun482 = e.get("text")?;
                let mut args480 = Vec::new();
                let mut kw481 = Vec::new();
                args480.push(e.get("c")?);
                args480.push(e.get("x")?);
                args480.push(Val::Int(526i64));
                args480.push(Val::Str("135° DRILL POINT".into()));
                args480.push(Val::Int(9i64));
                kw481.push(("align".into(), Val::Str("center".into())));
                fun482.call(args480, kw481)?
            };
            {
                let fun485 = e.get("text")?;
                let mut args483 = Vec::new();
                let mut kw484 = Vec::new();
                args483.push(e.get("c")?);
                args483.push(e.get("x")?);
                args483.push(Val::Int(511i64));
                args483.push(Val::Str("DO NOT BREAK THROUGH".into()));
                args483.push(Val::Int(10i64));
                kw484.push(("bold".into(), Val::Bool(true)));
                kw484.push(("align".into(), Val::Str("center".into())));
                fun485.call(args483, kw484)?
            };
            Ok(Val::None)
        })
    })?;
    // location_table
    e.set("location_table", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned486 = {
                let mut s = Vec::new();
                s.push(Val::Int(705i64));
                s.push(Val::Int(1168i64));
                s.push(Val::Int(455i64));
                Val::tuple(s)
            };
            let unpack487 = unpack(assigned486.clone(), 3)?;
            e.set("left", unpack487[0].clone())?;
            e.set("right", unpack487[1].clone())?;
            e.set("top", unpack487[2].clone())?;
            let assigned488 = {
                let mut s = Vec::new();
                s.push(e.get("left")?);
                s.push(binary("add", e.get("left")?, Val::Int(65i64))?);
                s.push(binary("add", e.get("left")?, Val::Int(154i64))?);
                s.push(binary("add", e.get("left")?, Val::Int(243i64))?);
                s.push(e.get("right")?);
                Val::tuple(s)
            };
            e.set("columns", assigned488.clone())?;
            let assigned489 = Val::Int(24i64);
            e.set("row_height", assigned489.clone())?;
            let assigned490 = binary(
                "sub",
                e.get("top")?,
                binary("mul", Val::Int(4i64), e.get("row_height")?)?,
            )?;
            e.set("bottom", assigned490.clone())?;
            {
                let fun493 = e.get("text")?;
                let mut args491 = Vec::new();
                let mut kw492 = Vec::new();
                args491.push(e.get("c")?);
                args491.push(e.get("left")?);
                args491.push(binary("add", e.get("top")?, Val::Int(14i64))?);
                args491.push(Val::Str("FEATURE LOCATIONS".into()));
                args491.push(Val::Int(10i64));
                kw492.push(("bold".into(), Val::Bool(true)));
                fun493.call(args491, kw492)?
            };
            {
                let fun496 = e.get("c")?.attr("setLineWidth")?;
                let mut args494 = Vec::new();
                let mut kw495 = Vec::new();
                args494.push(e.get("THIN")?);
                fun496.call(args494, kw495)?
            };
            {
                let fun499 = e.get("c")?.attr("rect")?;
                let mut args497 = Vec::new();
                let mut kw498 = Vec::new();
                args497.push(e.get("left")?);
                args497.push(e.get("bottom")?);
                args497.push(binary("sub", e.get("right")?, e.get("left")?)?);
                args497.push(binary("sub", e.get("top")?, e.get("bottom")?)?);
                kw498.push(("stroke".into(), Val::Int(1i64)));
                kw498.push(("fill".into(), Val::Int(0i64)));
                fun499.call(args497, kw498)?
            };
            for item500 in e
                .get("columns")?
                .get(Val::Slice {
                    start: Some(Val::Int(1i64).integer()?),
                    stop: Some(unary("neg", Val::Int(1i64))?.integer()?),
                    step: 1,
                })?
                .iter()?
            {
                e.set("x", item500)?;
                {
                    let fun503 = e.get("line")?;
                    let mut args501 = Vec::new();
                    let mut kw502 = Vec::new();
                    args501.push(e.get("c")?);
                    args501.push(e.get("x")?);
                    args501.push(e.get("bottom")?);
                    args501.push(e.get("x")?);
                    args501.push(e.get("top")?);
                    fun503.call(args501, kw502)?
                };
            }
            for item504 in {
                let fun510 = e.get("range")?;
                let mut args508 = Vec::new();
                let mut kw509 = Vec::new();
                args508.push(Val::Int(1i64));
                args508.push(Val::Int(4i64));
                fun510.call(args508, kw509)?
            }
            .iter()?
            {
                e.set("i", item504)?;
                {
                    let fun507 = e.get("line")?;
                    let mut args505 = Vec::new();
                    let mut kw506 = Vec::new();
                    args505.push(e.get("c")?);
                    args505.push(e.get("left")?);
                    args505.push(binary(
                        "sub",
                        e.get("top")?,
                        binary("mul", e.get("i")?, e.get("row_height")?)?,
                    )?);
                    args505.push(e.get("right")?);
                    args505.push(binary(
                        "sub",
                        e.get("top")?,
                        binary("mul", e.get("i")?, e.get("row_height")?)?,
                    )?);
                    fun507.call(args505, kw506)?
                };
            }
            let assigned511 = {
                let mut s = Vec::new();
                s.push(Val::Str("FEATURE".into()));
                s.push(Val::Str("X".into()));
                s.push(Val::Str("Y".into()));
                s.push(Val::Str("DESCRIPTION".into()));
                Val::tuple(s)
            };
            e.set("headers", assigned511.clone())?;
            for item512 in {
                let fun518 = e.get("enumerate")?;
                let mut args516 = Vec::new();
                let mut kw517 = Vec::new();
                args516.push(e.get("headers")?);
                fun518.call(args516, kw517)?
            }
            .iter()?
            {
                let unpack519 = unpack(item512, 2)?;
                e.set("i", unpack519[0].clone())?;
                e.set("value", unpack519[1].clone())?;
                {
                    let fun515 = e.get("text")?;
                    let mut args513 = Vec::new();
                    let mut kw514 = Vec::new();
                    args513.push(e.get("c")?);
                    args513.push(binary(
                        "truediv",
                        binary(
                            "add",
                            e.get("columns")?.get(e.get("i")?)?,
                            e.get("columns")?
                                .get(binary("add", e.get("i")?, Val::Int(1i64))?)?,
                        )?,
                        Val::Int(2i64),
                    )?);
                    args513.push(binary("sub", e.get("top")?, Val::Int(16i64))?);
                    args513.push(e.get("value")?);
                    args513.push(Val::Float(8.5f64));
                    kw514.push(("bold".into(), Val::Bool(true)));
                    kw514.push(("align".into(), Val::Str("center".into())));
                    fun515.call(args513, kw514)?
                };
            }
            let assigned520 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("P1".into()));
                    s.extend(e.get("hole_positions")?.get(Val::Int(0i64))?.iter()?);
                    s.push(Val::Str("THREADED PORT".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("P2".into()));
                    s.extend(e.get("hole_positions")?.get(Val::Int(1i64))?.iter()?);
                    s.push(Val::Str("THREADED PORT".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("R1".into()));
                    s.extend(e.get("register_position")?.iter()?);
                    s.push(Val::Str("BLIND ROD REGISTER".into()));
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("features", assigned520.clone())?;
            for item521 in {
                let fun540 = e.get("enumerate")?;
                let mut args538 = Vec::new();
                let mut kw539 = Vec::new();
                args538.push(e.get("features")?);
                args538.push(Val::Int(1i64));
                fun540.call(args538, kw539)?
            }
            .iter()?
            {
                let unpack541 = unpack(item521, 2)?;
                e.set("row", unpack541[0].clone())?;
                let unpack542 = unpack(unpack541[1].clone(), 4)?;
                e.set("feature", unpack542[0].clone())?;
                e.set("x", unpack542[1].clone())?;
                e.set("y", unpack542[2].clone())?;
                e.set("description", unpack542[3].clone())?;
                let assigned522 = binary(
                    "sub",
                    binary(
                        "sub",
                        e.get("top")?,
                        binary("mul", e.get("row_height")?, e.get("row")?)?,
                    )?,
                    Val::Int(16i64),
                )?;
                e.set("baseline", assigned522.clone())?;
                let assigned523 = {
                    let mut s = Vec::new();
                    s.push(e.get("feature")?);
                    s.push({
                        let mut str524 = String::new();
                        str524.push_str(&format(
                            &e.get("x")?,
                            &val_string({
                                let mut str525 = String::new();
                                str525.push_str(".3f");
                                Val::Str(str525)
                            })?,
                        )?);
                        Val::Str(str524)
                    });
                    s.push({
                        let mut str526 = String::new();
                        str526.push_str(&format(
                            &e.get("y")?,
                            &val_string({
                                let mut str527 = String::new();
                                str527.push_str(".3f");
                                Val::Str(str527)
                            })?,
                        )?);
                        Val::Str(str526)
                    });
                    s.push(e.get("description")?);
                    Val::tuple(s)
                };
                e.set("values", assigned523.clone())?;
                for item528 in {
                    let fun536 = e.get("enumerate")?;
                    let mut args534 = Vec::new();
                    let mut kw535 = Vec::new();
                    args534.push(e.get("values")?);
                    fun536.call(args534, kw535)?
                }
                .iter()?
                {
                    let unpack537 = unpack(item528, 2)?;
                    e.set("i", unpack537[0].clone())?;
                    e.set("value", unpack537[1].clone())?;
                    {
                        let fun531 = e.get("text")?;
                        let mut args529 = Vec::new();
                        let mut kw530 = Vec::new();
                        args529.push(e.get("c")?);
                        args529.push(binary(
                            "truediv",
                            binary(
                                "add",
                                e.get("columns")?.get(e.get("i")?)?,
                                e.get("columns")?.get(binary(
                                    "add",
                                    e.get("i")?,
                                    Val::Int(1i64),
                                )?)?,
                            )?,
                            Val::Int(2i64),
                        )?);
                        args529.push(e.get("baseline")?);
                        args529.push(e.get("value")?);
                        args529.push(Val::Int(9i64));
                        kw530.push(("bold".into(), {
                            let v532 = e.get("i")?;
                            let v533 = Val::Int(0i64);
                            Val::Bool(compare("eq", v532.clone(), v533.clone())?.truthy()?)
                        }));
                        kw530.push(("align".into(), Val::Str("center".into())));
                        fun531.call(args529, kw530)?
                    };
                }
            }
            {
                let fun545 = e.get("text")?;
                let mut args543 = Vec::new();
                let mut kw544 = Vec::new();
                args543.push(e.get("c")?);
                args543.push(e.get("left")?);
                args543.push(binary("sub", e.get("bottom")?, Val::Int(16i64))?);
                args543.push(Val::Str(
                    "ORIGIN: DISC OD CENTER. +X RIGHT; +Y UP IN INSIDE FACE VIEW.".into(),
                ));
                args543.push(Val::Int(8i64));
                fun545.call(args543, kw544)?
            };
            {
                let fun548 = e.get("text")?;
                let mut args546 = Vec::new();
                let mut kw547 = Vec::new();
                args546.push(e.get("c")?);
                args546.push(e.get("left")?);
                args546.push(binary("sub", e.get("bottom")?, Val::Int(29i64))?);
                args546.push(Val::Str(
                    "COORDINATES LOCATE FEATURE AXES. HOLE AXES NORMAL TO FACES.".into(),
                ));
                args546.push(Val::Int(8i64));
                fun548.call(args546, kw547)?
            };
            Ok(Val::None)
        })
    })?;
    // notes
    e.set("notes", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned549 = {
                let mut s = Vec::new();
                s.push(Val::Int(661i64));
                s.push(Val::Int(306i64));
                Val::tuple(s)
            };
            let unpack550 = unpack(assigned549.clone(), 2)?;
            e.set("x", unpack550[0].clone())?;
            e.set("y", unpack550[1].clone())?;
            {
                let fun553 = e.get("text")?;
                let mut args551 = Vec::new();
                let mut kw552 = Vec::new();
                args551.push(e.get("c")?);
                args551.push(e.get("x")?);
                args551.push(e.get("y")?);
                args551.push(Val::Str("FABRICATION NOTES".into()));
                args551.push(Val::Int(10i64));
                kw552.push(("bold".into(), Val::Bool(true)));
                fun553.call(args551, kw552)?
            };
            let assigned554 = {
                let mut s = Vec::new();
                s.push(Val::Str(
                    "1. BLANK: ENDCAP-CIRCULAR-2HOLE.DXF; TWO Ø0.438 LASER-CUT PILOTS.".into(),
                ));
                s.push(Val::Str(
                    "2. CLEAR THE CUT LIP ON BOTH PORT FACES WITH AN 82° COUNTERSINK".into(),
                ));
                s.push(Val::Str(
                    "    BEFORE TAPPING. NPT FORM: ASME B1.20.1. TARGET 4.5 TURNS".into(),
                ));
                s.push(Val::Str(
                    "    ENGAGEMENT; VERIFY ELBOW FIT AND FINAL CLOCKING ON A TRIAL".into(),
                ));
                s.push(Val::Str(
                    "    PART PER PRESSURE-VESSEL PROCEDURE, STEP 1.".into(),
                ));
                s.push(Val::Str(
                    "3. R1 IS BLIND. TOP CAP ONLY: Ø5/32 AT THE SAME TIP DEPTH IS".into(),
                ));
                s.push(Val::Str(
                    "    PERMITTED IF NEEDED FOR ROD-TIP FIT. BOTH CAPS START AT Ø9/64.".into(),
                ));
                s.push(Val::Str(
                    "4. OD: CHAMFER THE INSIDE EDGE FOR INSERTION. OUTSIDE EDGE:".into(),
                ));
                s.push(Val::Str(
                    "    REMOVE BURR ONLY; PRESERVE THE SQUARE CLOSURE-WELD CORNER.".into(),
                ));
                s.push(Val::Str(
                    "5. REMOVE BURRS, CHIPS AND CUTTING FLUID. ROD TACK AND VESSEL".into(),
                ));
                s.push(Val::Str(
                    "    WELDS: PRESSURE-VESSEL ASSEMBLY PROCEDURE.".into(),
                ));
                Val::list(s)
            };
            e.set("rows", assigned554.clone())?;
            for item555 in {
                let fun561 = e.get("enumerate")?;
                let mut args559 = Vec::new();
                let mut kw560 = Vec::new();
                args559.push(e.get("rows")?);
                fun561.call(args559, kw560)?
            }
            .iter()?
            {
                let unpack562 = unpack(item555, 2)?;
                e.set("i", unpack562[0].clone())?;
                e.set("value", unpack562[1].clone())?;
                {
                    let fun558 = e.get("text")?;
                    let mut args556 = Vec::new();
                    let mut kw557 = Vec::new();
                    args556.push(e.get("c")?);
                    args556.push(e.get("x")?);
                    args556.push(binary(
                        "sub",
                        binary("sub", e.get("y")?, Val::Int(19i64))?,
                        binary("mul", e.get("i")?, Val::Int(12i64))?,
                    )?);
                    args556.push(e.get("value")?);
                    args556.push(Val::Float(8.6f64));
                    fun558.call(args556, kw557)?
                };
            }
            Ok(Val::None)
        })
    })?;
    // title_block
    e.set("title_block", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned563 = {
                let mut s = Vec::new();
                s.push(Val::Int(635i64));
                s.push(e.get("MARGIN")?);
                s.push(binary(
                    "sub",
                    e.get("SHEET")?.get(Val::Int(0i64))?,
                    e.get("MARGIN")?,
                )?);
                s.push(Val::Int(143i64));
                Val::tuple(s)
            };
            let unpack564 = unpack(assigned563.clone(), 4)?;
            e.set("left", unpack564[0].clone())?;
            e.set("bottom", unpack564[1].clone())?;
            e.set("right", unpack564[2].clone())?;
            e.set("top", unpack564[3].clone())?;
            {
                let fun567 = e.get("c")?.attr("setLineWidth")?;
                let mut args565 = Vec::new();
                let mut kw566 = Vec::new();
                args565.push(Val::Float(0.7f64));
                fun567.call(args565, kw566)?
            };
            {
                let fun570 = e.get("c")?.attr("rect")?;
                let mut args568 = Vec::new();
                let mut kw569 = Vec::new();
                args568.push(e.get("left")?);
                args568.push(e.get("bottom")?);
                args568.push(binary("sub", e.get("right")?, e.get("left")?)?);
                args568.push(binary("sub", e.get("top")?, e.get("bottom")?)?);
                kw569.push(("stroke".into(), Val::Int(1i64)));
                kw569.push(("fill".into(), Val::Int(0i64)));
                fun570.call(args568, kw569)?
            };
            {
                let fun573 = e.get("line")?;
                let mut args571 = Vec::new();
                let mut kw572 = Vec::new();
                args571.push(e.get("c")?);
                args571.push(e.get("left")?);
                args571.push(Val::Int(98i64));
                args571.push(e.get("right")?);
                args571.push(Val::Int(98i64));
                fun573.call(args571, kw572)?
            };
            {
                let fun576 = e.get("line")?;
                let mut args574 = Vec::new();
                let mut kw575 = Vec::new();
                args574.push(e.get("c")?);
                args574.push(e.get("left")?);
                args574.push(Val::Int(65i64));
                args574.push(e.get("right")?);
                args574.push(Val::Int(65i64));
                fun576.call(args574, kw575)?
            };
            {
                let fun579 = e.get("line")?;
                let mut args577 = Vec::new();
                let mut kw578 = Vec::new();
                args577.push(e.get("c")?);
                args577.push(Val::Int(1010i64));
                args577.push(Val::Int(98i64));
                args577.push(Val::Int(1010i64));
                args577.push(e.get("top")?);
                fun579.call(args577, kw578)?
            };
            {
                let fun582 = e.get("text")?;
                let mut args580 = Vec::new();
                let mut kw581 = Vec::new();
                args580.push(e.get("c")?);
                args580.push(binary("add", e.get("left")?, Val::Int(10i64))?);
                args580.push(Val::Int(125i64));
                args580.push(Val::Str("HOME SODA MACHINE".into()));
                args580.push(Val::Int(8i64));
                fun582.call(args580, kw581)?
            };
            {
                let fun585 = e.get("text")?;
                let mut args583 = Vec::new();
                let mut kw584 = Vec::new();
                args583.push(e.get("c")?);
                args583.push(binary("add", e.get("left")?, Val::Int(10i64))?);
                args583.push(Val::Int(108i64));
                args583.push(Val::Str("CARBONATOR END CAP - FINISHED".into()));
                args583.push(Val::Int(13i64));
                kw584.push(("bold".into(), Val::Bool(true)));
                fun585.call(args583, kw584)?
            };
            {
                let fun588 = e.get("text")?;
                let mut args586 = Vec::new();
                let mut kw587 = Vec::new();
                args586.push(e.get("c")?);
                args586.push(Val::Int(1104i64));
                args586.push(Val::Int(124i64));
                args586.push(Val::Str("PROTOTYPE".into()));
                args586.push(Val::Int(10i64));
                kw587.push(("bold".into(), Val::Bool(true)));
                kw587.push(("align".into(), Val::Str("center".into())));
                fun588.call(args586, kw587)?
            };
            {
                let fun591 = e.get("text")?;
                let mut args589 = Vec::new();
                let mut kw590 = Vec::new();
                args589.push(e.get("c")?);
                args589.push(Val::Int(1104i64));
                args589.push(Val::Int(109i64));
                args589.push(Val::Str("FOR REVIEW".into()));
                args589.push(Val::Int(9i64));
                kw590.push(("align".into(), Val::Str("center".into())));
                fun591.call(args589, kw590)?
            };
            for item592 in {
                let mut s = Vec::new();
                s.push(Val::Int(866i64));
                s.push(Val::Int(1030i64));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("x", item592)?;
                {
                    let fun595 = e.get("line")?;
                    let mut args593 = Vec::new();
                    let mut kw594 = Vec::new();
                    args593.push(e.get("c")?);
                    args593.push(e.get("x")?);
                    args593.push(Val::Int(65i64));
                    args593.push(e.get("x")?);
                    args593.push(Val::Int(98i64));
                    fun595.call(args593, kw594)?
                };
            }
            for item596 in {
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
                    s.push(Val::Int(876i64));
                    s.push(Val::Str("UNITS".into()));
                    s.push(Val::Str("INCHES".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(1040i64));
                    s.push(Val::Str("QUANTITY".into()));
                    s.push(Val::Str("2 PER CARBONATOR".into()));
                    Val::tuple(s)
                });
                Val::list(s)
            }
            .iter()?
            {
                let unpack603 = unpack(item596, 3)?;
                e.set("x", unpack603[0].clone())?;
                e.set("label", unpack603[1].clone())?;
                e.set("value", unpack603[2].clone())?;
                {
                    let fun599 = e.get("text")?;
                    let mut args597 = Vec::new();
                    let mut kw598 = Vec::new();
                    args597.push(e.get("c")?);
                    args597.push(e.get("x")?);
                    args597.push(Val::Int(87i64));
                    args597.push(e.get("label")?);
                    args597.push(Val::Int(7i64));
                    fun599.call(args597, kw598)?
                };
                {
                    let fun602 = e.get("text")?;
                    let mut args600 = Vec::new();
                    let mut kw601 = Vec::new();
                    args600.push(e.get("c")?);
                    args600.push(e.get("x")?);
                    args600.push(Val::Int(73i64));
                    args600.push(e.get("value")?);
                    args600.push(Val::Int(9i64));
                    kw601.push(("bold".into(), Val::Bool(true)));
                    fun602.call(args600, kw601)?
                };
            }
            let assigned604 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(635i64));
                    s.push(Val::Int(815i64));
                    s.push(Val::Str("DRAWING".into()));
                    s.push(Val::Str("END-CAP-01".into()));
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
                    s.push(e.get("REVISION_DATE")?);
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
                Val::list(s)
            };
            e.set("fields", assigned604.clone())?;
            for item605 in {
                let fun617 = e.get("enumerate")?;
                let mut args615 = Vec::new();
                let mut kw616 = Vec::new();
                args615.push(e.get("fields")?);
                fun617.call(args615, kw616)?
            }
            .iter()?
            {
                let unpack618 = unpack(item605, 2)?;
                e.set("i", unpack618[0].clone())?;
                let unpack619 = unpack(unpack618[1].clone(), 4)?;
                e.set("a", unpack619[0].clone())?;
                e.set("b", unpack619[1].clone())?;
                e.set("label", unpack619[2].clone())?;
                e.set("value", unpack619[3].clone())?;
                if e.get("i")?.truthy()? {
                    {
                        let fun608 = e.get("line")?;
                        let mut args606 = Vec::new();
                        let mut kw607 = Vec::new();
                        args606.push(e.get("c")?);
                        args606.push(e.get("a")?);
                        args606.push(e.get("bottom")?);
                        args606.push(e.get("a")?);
                        args606.push(Val::Int(65i64));
                        fun608.call(args606, kw607)?
                    };
                }
                {
                    let fun611 = e.get("text")?;
                    let mut args609 = Vec::new();
                    let mut kw610 = Vec::new();
                    args609.push(e.get("c")?);
                    args609.push(binary("add", e.get("a")?, Val::Int(9i64))?);
                    args609.push(Val::Int(53i64));
                    args609.push(e.get("label")?);
                    args609.push(Val::Int(7i64));
                    fun611.call(args609, kw610)?
                };
                {
                    let fun614 = e.get("text")?;
                    let mut args612 = Vec::new();
                    let mut kw613 = Vec::new();
                    args612.push(e.get("c")?);
                    args612.push(binary("add", e.get("a")?, Val::Int(9i64))?);
                    args612.push(Val::Int(37i64));
                    args612.push(e.get("value")?);
                    args612.push(Val::Int(9i64));
                    kw613.push(("bold".into(), Val::Bool(true)));
                    fun614.call(args612, kw613)?
                };
            }
            {
                let fun622 = e.get("text")?;
                let mut args620 = Vec::new();
                let mut kw621 = Vec::new();
                args620.push(e.get("c")?);
                args620.push(Val::Int(47i64));
                args620.push(Val::Int(125i64));
                args620.push(Val::Str("UNLESS OTHERWISE SPECIFIED".into()));
                args620.push(Val::Int(9i64));
                kw621.push(("bold".into(), Val::Bool(true)));
                fun622.call(args620, kw621)?
            };
            {
                let fun625 = e.get("text")?;
                let mut args623 = Vec::new();
                let mut kw624 = Vec::new();
                args623.push(e.get("c")?);
                args623.push(Val::Int(47i64));
                args623.push(Val::Int(108i64));
                args623.push(Val::Str("LINEAR ±0.005 IN     ANGULAR ±0.5°".into()));
                args623.push(Val::Int(10i64));
                fun625.call(args623, kw624)?
            };
            {
                let fun628 = e.get("text")?;
                let mut args626 = Vec::new();
                let mut kw627 = Vec::new();
                args626.push(e.get("c")?);
                args626.push(Val::Int(47i64));
                args626.push(Val::Int(91i64));
                args626.push(Val::Str(
                    "REFERENCE DIMENSIONS ARE IDENTIFIED BY REF.".into(),
                ));
                args626.push(Val::Float(8.5f64));
                fun628.call(args626, kw627)?
            };
            {
                let fun631 = e.get("text")?;
                let mut args629 = Vec::new();
                let mut kw630 = Vec::new();
                args629.push(e.get("c")?);
                args629.push(Val::Int(47i64));
                args629.push(Val::Int(65i64));
                args629.push(Val::Str(
                    "DIMENSIONS GOVERN. DO NOT SCALE THE DRAWING.".into(),
                ));
                args629.push(Val::Int(9i64));
                kw630.push(("bold".into(), Val::Bool(true)));
                fun631.call(args629, kw630)?
            };
            {
                let fun634 = e.get("text")?;
                let mut args632 = Vec::new();
                let mut kw633 = Vec::new();
                args632.push(e.get("c")?);
                args632.push(Val::Int(47i64));
                args632.push(Val::Int(49i64));
                args632.push(Val::Str(
                    "ANSI B / 17 x 11 IN. PRINT AT 100% FOR THE STATED VIEW SCALES.".into(),
                ));
                args632.push(Val::Int(8i64));
                fun634.call(args632, kw633)?
            };
            {
                let fun637 = e.get("text")?;
                let mut args635 = Vec::new();
                let mut kw636 = Vec::new();
                args635.push(e.get("c")?);
                args635.push(Val::Int(47i64));
                args635.push(Val::Int(36i64));
                args635.push(Val::Str(
                    "MACHINED CAP COMMON TO TOP AND BOTTOM; ROD TACK IS AN ASSEMBLY OPERATION."
                        .into(),
                ));
                args635.push(Val::Int(8i64));
                fun637.call(args635, kw636)?
            };
            Ok(Val::None)
        })
    })?;
    // build_pdf
    e.set("build_pdf",{let params=vec![("path".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned638={let fun641=e.get("canvas")?.attr("Canvas")?;let mut args639=Vec::new();let mut kw640=Vec::new();args639.push({let fun644=e.get("str")?;let mut args642=Vec::new();let mut kw643=Vec::new();args642.push(e.get("path")?);fun644.call(args642,kw643)?});kw640.push(("pagesize".into(),e.get("SHEET")?));kw640.push(("invariant".into(),Val::Int(1i64)));kw640.push(("pageCompression".into(),Val::Int(1i64)));fun641.call(args639,kw640)?};e.set("c",assigned638.clone())?;
{let fun647=e.get("c")?.attr("setTitle")?;let mut args645=Vec::new();let mut kw646=Vec::new();args645.push(Val::Str("Carbonator end cap - finished machined part".into()));fun647.call(args645,kw646)?};
{let fun650=e.get("c")?.attr("setAuthor")?;let mut args648=Vec::new();let mut kw649=Vec::new();args648.push(Val::Str("Home Soda Machine / Codex".into()));fun650.call(args648,kw649)?};
{let fun653=e.get("c")?.attr("setSubject")?;let mut args651=Vec::new();let mut kw652=Vec::new();args651.push({let mut str654=String::new();str654.push_str("END-CAP-01 Rev ");str654.push_str(&format(&e.get("REVISION")?,&String::new())?);str654.push_str(": tapped ports, blind float-rod register and face-specific edge preparation");Val::Str(str654)});fun653.call(args651,kw652)?};
{let fun657=e.get("c")?.attr("setStrokeColorRGB")?;let mut args655=Vec::new();let mut kw656=Vec::new();args655.push(Val::Int(0i64));args655.push(Val::Int(0i64));args655.push(Val::Int(0i64));fun657.call(args655,kw656)?};
{let fun660=e.get("c")?.attr("setFillColorRGB")?;let mut args658=Vec::new();let mut kw659=Vec::new();args658.push(Val::Int(0i64));args658.push(Val::Int(0i64));args658.push(Val::Int(0i64));fun660.call(args658,kw659)?};
{let fun663=e.get("c")?.attr("setLineWidth")?;let mut args661=Vec::new();let mut kw662=Vec::new();args661.push(Val::Int(1i64));fun663.call(args661,kw662)?};
{let fun666=e.get("c")?.attr("rect")?;let mut args664=Vec::new();let mut kw665=Vec::new();args664.push(e.get("MARGIN")?);args664.push(e.get("MARGIN")?);args664.push(binary("sub",e.get("SHEET")?.get(Val::Int(0i64))?,binary("mul",Val::Int(2i64),e.get("MARGIN")?)?)?);args664.push(binary("sub",e.get("SHEET")?.get(Val::Int(1i64))?,binary("mul",Val::Int(2i64),e.get("MARGIN")?)?)?);kw665.push(("stroke".into(),Val::Int(1i64)));kw665.push(("fill".into(),Val::Int(0i64)));fun666.call(args664,kw665)?};
{let fun669=e.get("face_view")?;let mut args667=Vec::new();let mut kw668=Vec::new();args667.push(e.get("c")?);fun669.call(args667,kw668)?};
{let fun672=e.get("port_section")?;let mut args670=Vec::new();let mut kw671=Vec::new();args670.push(e.get("c")?);fun672.call(args670,kw671)?};
{let fun675=e.get("register_section")?;let mut args673=Vec::new();let mut kw674=Vec::new();args673.push(e.get("c")?);fun675.call(args673,kw674)?};
{let fun678=e.get("location_table")?;let mut args676=Vec::new();let mut kw677=Vec::new();args676.push(e.get("c")?);fun678.call(args676,kw677)?};
{let fun681=e.get("notes")?;let mut args679=Vec::new();let mut kw680=Vec::new();args679.push(e.get("c")?);fun681.call(args679,kw680)?};
{let fun684=e.get("title_block")?;let mut args682=Vec::new();let mut kw683=Vec::new();args682.push(e.get("c")?);fun684.call(args682,kw683)?};
{let fun687=e.get("c")?.attr("showPage")?;let mut args685=Vec::new();let mut kw686=Vec::new();fun687.call(args685,kw686)?};
{let fun690=e.get("c")?.attr("save")?;let mut args688=Vec::new();let mut kw689=Vec::new();fun690.call(args688,kw689)?};
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
                let fun693 = e.get("export_pdf")?;
                let mut args691 = Vec::new();
                let mut kw692 = Vec::new();
                args691.push(e.get("build_pdf")?);
                args691.push({
                    let fun696 = e.get("str")?;
                    let mut args694 = Vec::new();
                    let mut kw695 = Vec::new();
                    args694.push(e.get("PDF_PATH")?);
                    fun696.call(args694, kw695)?
                });
                fun693.call(args691, kw692)?
            };
            {
                let fun699 = e.get("print")?;
                let mut args697 = Vec::new();
                let mut kw698 = Vec::new();
                args697.push({
                    let mut str700 = String::new();
                    str700.push_str("Exported: ");
                    str700.push_str(&format(&e.get("PDF_PATH")?, &String::new())?);
                    Val::Str(str700)
                });
                fun699.call(args697, kw698)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun703 = e.get("main")?;
        let mut args701 = Vec::new();
        let mut kw702 = Vec::new();
        fun703.call(args701, kw702)?
    };
    Ok(Val::None)
}
