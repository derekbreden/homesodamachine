#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let mod2 = rt.import_module("reportlab.pdfgen")?;
    e.set("canvas", rt.member("reportlab.pdfgen", "canvas")?)?;
    let assigned3 = {
        let fun6 = {
            let fun9 = e.get("Path")?;
            let mut args7 = Vec::new();
            let mut kw8 = Vec::new();
            args7.push(e.get("__file__")?);
            fun9.call(args7, kw8)?
        }
        .attr("resolve")?;
        let mut args4 = Vec::new();
        let mut kw5 = Vec::new();
        fun6.call(args4, kw5)?
    }
    .attr("parent")?;
    e.set("HERE", assigned3.clone())?;
    let assigned10 = {
        let fun13 = e.get("next")?;
        let mut args11 = Vec::new();
        let mut kw12 = Vec::new();
        args11.push({
            let e = e.child();
            let out14 = Val::list(vec![]);
            for item15 in e.get("HERE")?.attr("parents")?.iter()? {
                e.set("p", item15)?;
                if {
                    let v16 = e.get("p")?.attr("name")?;
                    let v17 = Val::Str("hardware".into());
                    Val::Bool(compare("eq", v16.clone(), v17.clone())?.truthy()?)
                }
                .truthy()?
                {
                    out14.attr("append")?.call(vec![e.get("p")?], vec![])?;
                }
            }
            out14
        });
        fun13.call(args11, kw12)?
    };
    e.set("HW", assigned10.clone())?;
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
    let mod24 = rt.import_module("_carbonator_drawing")?;
    import_star(&e, mod24.clone())?;
    let assigned25 = binary(
        "truediv",
        e.get("HERE")?,
        Val::Str("carbonator-float-rod-drawing.pdf".into()),
    )?;
    e.set("PDF_PATH", assigned25.clone())?;
    let assigned26 = {
        let mut s = Vec::new();
        s.push(binary("mul", Val::Int(11i64), e.get("IN")?)?);
        s.push(binary("mul", Val::Float(8.5f64), e.get("IN")?)?);
        Val::tuple(s)
    };
    e.set("SHEET", assigned26.clone())?;
    let assigned27 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("side-view".into()));
            s.push(Val::Int(40i64));
            s.push(Val::Int(365i64));
            s.push(Val::Int(493i64));
            s.push(Val::Int(555i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("end-view".into()));
            s.push(Val::Int(508i64));
            s.push(Val::Int(365i64));
            s.push(Val::Int(751i64));
            s.push(Val::Int(555i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("notes-fit".into()));
            s.push(Val::Int(40i64));
            s.push(Val::Int(169i64));
            s.push(Val::Int(752i64));
            s.push(Val::Int(360i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("title-status".into()));
            s.push(Val::Int(35i64));
            s.push(Val::Int(27i64));
            s.push(Val::Int(765i64));
            s.push(Val::Int(179i64));
            Val::tuple(s)
        });
        Val::list(s)
    };
    e.set("REVIEW_REGIONS", assigned27.clone())?;
    // views
    e.set("views", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned28 = {
                let mut s = Vec::new();
                s.push(Val::Int(72i64));
                s.push(Val::Int(430i64));
                Val::tuple(s)
            };
            let unpack29 = unpack(assigned28.clone(), 2)?;
            e.set("x", unpack29[0].clone())?;
            e.set("y", unpack29[1].clone())?;
            let assigned30 = binary("mul", e.get("ROD_LENGTH")?, e.get("IN")?)?;
            e.set("length", assigned30.clone())?;
            let assigned31 = binary("mul", e.get("ROD_D")?, e.get("IN")?)?;
            e.set("diameter", assigned31.clone())?;
            {
                let fun34 = e.get("text")?;
                let mut args32 = Vec::new();
                let mut kw33 = Vec::new();
                args32.push(e.get("c")?);
                args32.push(binary(
                    "add",
                    e.get("x")?,
                    binary("truediv", e.get("length")?, Val::Int(2i64))?,
                )?);
                args32.push(Val::Int(544i64));
                args32.push(Val::Str("SIDE VIEW".into()));
                args32.push(Val::Int(12i64));
                kw33.push(("bold".into(), Val::Bool(true)));
                kw33.push(("align".into(), Val::Str("center".into())));
                fun34.call(args32, kw33)?
            };
            {
                let fun37 = e.get("text")?;
                let mut args35 = Vec::new();
                let mut kw36 = Vec::new();
                args35.push(e.get("c")?);
                args35.push(binary(
                    "add",
                    e.get("x")?,
                    binary("truediv", e.get("length")?, Val::Int(2i64))?,
                )?);
                args35.push(Val::Int(527i64));
                args35.push(Val::Str("SCALE 1:1".into()));
                args35.push(Val::Float(8.5f64));
                kw36.push(("align".into(), Val::Str("center".into())));
                fun37.call(args35, kw36)?
            };
            {
                let fun40 = e.get("c")?.attr("setLineWidth")?;
                let mut args38 = Vec::new();
                let mut kw39 = Vec::new();
                args38.push(e.get("VISIBLE")?);
                fun40.call(args38, kw39)?
            };
            {
                let fun43 = e.get("c")?.attr("rect")?;
                let mut args41 = Vec::new();
                let mut kw42 = Vec::new();
                args41.push(e.get("x")?);
                args41.push(e.get("y")?);
                args41.push(e.get("length")?);
                args41.push(e.get("diameter")?);
                kw42.push(("stroke".into(), Val::Int(1i64)));
                kw42.push(("fill".into(), Val::Int(0i64)));
                fun43.call(args41, kw42)?
            };
            {
                let fun46 = e.get("line")?;
                let mut args44 = Vec::new();
                let mut kw45 = Vec::new();
                args44.push(e.get("c")?);
                args44.push(binary("sub", e.get("x")?, Val::Int(14i64))?);
                args44.push(binary(
                    "add",
                    e.get("y")?,
                    binary("truediv", e.get("diameter")?, Val::Int(2i64))?,
                )?);
                args44.push(binary(
                    "add",
                    binary("add", e.get("x")?, e.get("length")?)?,
                    Val::Int(14i64),
                )?);
                args44.push(binary(
                    "add",
                    e.get("y")?,
                    binary("truediv", e.get("diameter")?, Val::Int(2i64))?,
                )?);
                kw45.push(("dash".into(), e.get("CENTER_DASH")?));
                fun46.call(args44, kw45)?
            };
            {
                let fun49 = e.get("horizontal_dimension")?;
                let mut args47 = Vec::new();
                let mut kw48 = Vec::new();
                args47.push(e.get("c")?);
                args47.push(e.get("x")?);
                args47.push(binary("add", e.get("x")?, e.get("length")?)?);
                args47.push(binary("add", e.get("y")?, e.get("diameter")?)?);
                args47.push(Val::Int(485i64));
                args47.push({
                    let mut str50 = String::new();
                    str50.push_str(&format(
                        &e.get("ROD_LENGTH")?,
                        &val_string({
                            let mut str51 = String::new();
                            str51.push_str(".3f");
                            Val::Str(str51)
                        })?,
                    )?);
                    str50.push_str(" ±");
                    str50.push_str(&format(
                        &e.get("ROD_LENGTH_TOL")?,
                        &val_string({
                            let mut str52 = String::new();
                            str52.push_str(".3f");
                            Val::Str(str52)
                        })?,
                    )?);
                    Val::Str(str50)
                });
                args47.push(Val::Int(12i64));
                fun49.call(args47, kw48)?
            };
            {
                let fun55 = e.get("text")?;
                let mut args53 = Vec::new();
                let mut kw54 = Vec::new();
                args53.push(e.get("c")?);
                args53.push(binary(
                    "add",
                    e.get("x")?,
                    binary("truediv", e.get("length")?, Val::Int(2i64))?,
                )?);
                args53.push(Val::Int(468i64));
                args53.push({
                    let mut str56 = String::new();
                    str56.push_str(&format(
                        &binary("mul", e.get("ROD_LENGTH")?, e.get("MM")?)?,
                        &val_string({
                            let mut str57 = String::new();
                            str57.push_str(".2f");
                            Val::Str(str57)
                        })?,
                    )?);
                    str56.push_str(" ±");
                    str56.push_str(&format(
                        &binary("mul", e.get("ROD_LENGTH_TOL")?, e.get("MM")?)?,
                        &val_string({
                            let mut str58 = String::new();
                            str58.push_str(".2f");
                            Val::Str(str58)
                        })?,
                    )?);
                    str56.push_str(" mm REF");
                    Val::Str(str56)
                });
                args53.push(Val::Int(9i64));
                kw54.push(("align".into(), Val::Str("center".into())));
                fun55.call(args53, kw54)?
            };
            {
                let fun61 = e.get("leader")?;
                let mut args59 = Vec::new();
                let mut kw60 = Vec::new();
                args59.push(e.get("c")?);
                args59.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(binary(
                        "add",
                        e.get("y")?,
                        binary("truediv", e.get("diameter")?, Val::Int(2i64))?,
                    )?);
                    Val::tuple(s)
                });
                args59.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("x")?, Val::Int(36i64))?);
                    s.push(Val::Int(390i64));
                    Val::tuple(s)
                });
                args59.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("x")?, Val::Int(60i64))?);
                    s.push(Val::Int(390i64));
                    Val::tuple(s)
                });
                args59.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("SQUARE CUT; DEBURR BOTH ENDS".into()));
                    s.push(Val::Str("KEEP GUIDE SURFACE FREE OF BURRS".into()));
                    Val::list(s)
                });
                args59.push(Val::Int(9i64));
                fun61.call(args59, kw60)?
            };
            let assigned62 = {
                let mut s = Vec::new();
                s.push(Val::Int(620i64));
                s.push(binary(
                    "add",
                    e.get("y")?,
                    binary("truediv", e.get("diameter")?, Val::Int(2i64))?,
                )?);
                s.push(binary("mul", Val::Int(4i64), e.get("IN")?)?);
                Val::tuple(s)
            };
            let unpack63 = unpack(assigned62.clone(), 3)?;
            e.set("center_x", unpack63[0].clone())?;
            e.set("center_y", unpack63[1].clone())?;
            e.set("end_scale", unpack63[2].clone())?;
            let assigned64 = binary(
                "truediv",
                binary("mul", e.get("ROD_D")?, e.get("end_scale")?)?,
                Val::Int(2i64),
            )?;
            e.set("radius", assigned64.clone())?;
            {
                let fun67 = e.get("text")?;
                let mut args65 = Vec::new();
                let mut kw66 = Vec::new();
                args65.push(e.get("c")?);
                args65.push(e.get("center_x")?);
                args65.push(Val::Int(544i64));
                args65.push(Val::Str("END VIEW".into()));
                args65.push(Val::Int(12i64));
                kw66.push(("bold".into(), Val::Bool(true)));
                kw66.push(("align".into(), Val::Str("center".into())));
                fun67.call(args65, kw66)?
            };
            {
                let fun70 = e.get("text")?;
                let mut args68 = Vec::new();
                let mut kw69 = Vec::new();
                args68.push(e.get("c")?);
                args68.push(e.get("center_x")?);
                args68.push(Val::Int(527i64));
                args68.push(Val::Str("SCALE 4:1".into()));
                args68.push(Val::Float(8.5f64));
                kw69.push(("align".into(), Val::Str("center".into())));
                fun70.call(args68, kw69)?
            };
            {
                let fun73 = e.get("c")?.attr("setLineWidth")?;
                let mut args71 = Vec::new();
                let mut kw72 = Vec::new();
                args71.push(e.get("VISIBLE")?);
                fun73.call(args71, kw72)?
            };
            {
                let fun76 = e.get("c")?.attr("circle")?;
                let mut args74 = Vec::new();
                let mut kw75 = Vec::new();
                args74.push(e.get("center_x")?);
                args74.push(e.get("center_y")?);
                args74.push(e.get("radius")?);
                kw75.push(("stroke".into(), Val::Int(1i64)));
                kw75.push(("fill".into(), Val::Int(0i64)));
                fun76.call(args74, kw75)?
            };
            {
                let fun79 = e.get("center")?;
                let mut args77 = Vec::new();
                let mut kw78 = Vec::new();
                args77.push(e.get("c")?);
                args77.push(e.get("center_x")?);
                args77.push(e.get("center_y")?);
                args77.push(binary("add", e.get("radius")?, Val::Int(10i64))?);
                fun79.call(args77, kw78)?
            };
            {
                let fun82 = e.get("circular_leader")?;
                let mut args80 = Vec::new();
                let mut kw81 = Vec::new();
                args80.push(e.get("c")?);
                args80.push({
                    let mut s = Vec::new();
                    s.push(e.get("center_x")?);
                    s.push(e.get("center_y")?);
                    Val::tuple(s)
                });
                args80.push(e.get("radius")?);
                args80.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(646i64));
                    s.push(Val::Int(490i64));
                    Val::tuple(s)
                });
                args80.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(662i64));
                    s.push(Val::Int(490i64));
                    Val::tuple(s)
                });
                args80.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut str83 = String::new();
                        str83.push_str("Ø");
                        str83.push_str(&format(
                            &e.get("ROD_D")?,
                            &val_string({
                                let mut str84 = String::new();
                                str84.push_str(".3f");
                                Val::Str(str84)
                            })?,
                        )?);
                        Val::Str(str83)
                    });
                    s.push({
                        let mut str85 = String::new();
                        str85.push_str("±");
                        str85.push_str(&format(
                            &e.get("ROD_D_TOL")?,
                            &val_string({
                                let mut str86 = String::new();
                                str86.push_str(".3f");
                                Val::Str(str86)
                            })?,
                        )?);
                        Val::Str(str85)
                    });
                    Val::list(s)
                });
                args80.push(Val::Int(10i64));
                fun82.call(args80, kw81)?
            };
            Ok(Val::None)
        })
    })?;
    // requirements
    e.set("requirements",{let params=vec![("c".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);{let fun89=e.get("text")?;let mut args87=Vec::new();let mut kw88=Vec::new();args87.push(e.get("c")?);args87.push(Val::Int(48i64));args87.push(Val::Int(343i64));args87.push(Val::Str("FINISHED PART REQUIREMENTS".into()));args87.push(Val::Int(10i64));kw88.push(("bold".into(),Val::Bool(true)));fun89.call(args87,kw88)?};
let assigned90={let mut s=Vec::new();s.push(Val::Str("1. Material: 316 stainless round rod. Stock: Tandefio B0CY4DWJFQ, nominal 1/8-inch x 12-inch sticks. Select stock meeting the stated diameter tolerance.".into()));s.push({let mut str91=String::new();str91.push_str("2. Length is the FINISHED overall length after cutting and deburring. Cut both ends flat and square to the rod axis within ");str91.push_str(&format(&e.get("rod_spec")?.attr("end_squareness_degrees")?,&val_string({let mut str92=String::new();str92.push_str("g");Val::Str(str92)})?)?);str91.push_str("°. Remove burrs; edge break ");str91.push_str(&format(&e.get("rod_spec")?.attr("edge_break_maximum")?,&val_string({let mut str93=String::new();str93.push_str(".3f");Val::Str(str93)})?)?);str91.push_str(" MAX. Keep the sliding surface free of burrs, chips and cutting fluid.");Val::Str(str91)});s.push({let mut str94=String::new();str94.push_str("3. Assembly interface: cap inside faces ");str94.push_str(&format(&e.get("INSIDE_SPAN")?,&val_string({let mut str95=String::new();str95.push_str(".3f");Val::Str(str95)})?)?);str94.push_str(" ±");str94.push_str(&format(&e.get("INSIDE_SPAN_TOL")?,&val_string({let mut str96=String::new();str96.push_str(".3f");Val::Str(str96)})?)?);str94.push_str(" apart AT THE ROD AXIS; registers coaxial, per CV-WLD-01. Registers per END-CAP-01: Ø9/64, ");str94.push_str(&format(&e.get("REG_DEPTH")?,&val_string({let mut str97=String::new();str97.push_str(".3f");Val::Str(str97)})?)?);str94.push_str(" ±");str94.push_str(&format(&e.get("rod_spec")?.attr("register_depth_tolerance")?,&val_string({let mut str98=String::new();str98.push_str(".3f");Val::Str(str98)})?)?);str94.push_str(" TO DRILL TIP; point ");str94.push_str(&format(&e.get("rod_spec")?.attr("register_point_degrees")?,&val_string({let mut str99=String::new();str99.push_str("g");Val::Str(str99)})?)?);str94.push_str("° ±");str94.push_str(&format(&e.get("rod_spec")?.attr("register_point_tolerance_degrees")?,&val_string({let mut str100=String::new();str100.push_str("g");Val::Str(str100)})?)?);str94.push_str("°. Flat rod ends seat above the drill tip.");Val::Str(str94)});s.push(Val::Str("4. Seat the rod in the bottom register and tack to the bottom cap. Before top closure, verify top-register engagement and full cap seating; verify free float travel. Maintain the specified cap spacing; rod length is controlled by this drawing.".into()));s.push(Val::Str("5. Quantity: one per carbonator. Reservoir rods are separate parts. Rod tack and vessel assembly follow the pressure-vessel procedure, steps 2-5.".into()));Val::list(s)};e.set("paragraphs",assigned90.clone())?;
return Ok({let fun103=e.get("wrap_lines")?;let mut args101=Vec::new();let mut kw102=Vec::new();args101.push(e.get("c")?);args101.push(Val::Int(48i64));args101.push(Val::Int(324i64));args101.push(e.get("paragraphs")?);args101.push(Val::Int(691i64));kw102.push(("size".into(),Val::Int(9i64)));kw102.push(("leading".into(),Val::Int(12i64)));kw102.push(("gap".into(),Val::Int(6i64)));fun103.call(args101,kw102)?});
Ok(Val::None)})})?;
    // build_pdf
    e.set("build_pdf",{let params=vec![("path".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned104={let fun107=e.get("canvas")?.attr("Canvas")?;let mut args105=Vec::new();let mut kw106=Vec::new();args105.push({let fun110=e.get("str")?;let mut args108=Vec::new();let mut kw109=Vec::new();args108.push(e.get("path")?);fun110.call(args108,kw109)?});kw106.push(("pagesize".into(),e.get("SHEET")?));kw106.push(("invariant".into(),Val::Int(1i64)));kw106.push(("pageCompression".into(),Val::Int(1i64)));fun107.call(args105,kw106)?};e.set("c",assigned104.clone())?;
{let fun113=e.get("c")?.attr("setTitle")?;let mut args111=Vec::new();let mut kw112=Vec::new();args111.push(Val::Str("Carbonator float guide rod - engineering drawing".into()));fun113.call(args111,kw112)?};
{let fun116=e.get("c")?.attr("setAuthor")?;let mut args114=Vec::new();let mut kw115=Vec::new();args114.push(Val::Str("Home Soda Machine / Codex".into()));fun116.call(args114,kw115)?};
{let fun119=e.get("c")?.attr("setSubject")?;let mut args117=Vec::new();let mut kw118=Vec::new();args117.push(Val::Str("FR-CARB-01 Rev B: finished 316 rod, fixed cut length and toleranced assembly interface".into()));fun119.call(args117,kw118)?};
{let fun122=e.get("frame")?;let mut args120=Vec::new();let mut kw121=Vec::new();args120.push(e.get("c")?);args120.push(e.get("SHEET")?);fun122.call(args120,kw121)?};
{let fun125=e.get("views")?;let mut args123=Vec::new();let mut kw124=Vec::new();args123.push(e.get("c")?);fun125.call(args123,kw124)?};
{let fun128=e.get("requirements")?;let mut args126=Vec::new();let mut kw127=Vec::new();args126.push(e.get("c")?);fun128.call(args126,kw127)?};
{let fun131=e.get("text")?;let mut args129=Vec::new();let mut kw130=Vec::new();args129.push(e.get("c")?);args129.push(Val::Int(48i64));args129.push(Val::Int(160i64));args129.push(Val::Str("ALL DIMENSIONS APPLY TO THE FINISHED, DEBURRED PART. INCH DIMENSIONS GOVERN.".into()));args129.push(Val::Float(8.5f64));kw130.push(("bold".into(),Val::Bool(true)));fun131.call(args129,kw130)?};
{let fun134=e.get("title_block")?;let mut args132=Vec::new();let mut kw133=Vec::new();args132.push(e.get("c")?);args132.push(e.get("SHEET")?);args132.push(Val::Str("CARBONATOR FLOAT GUIDE ROD".into()));args132.push(Val::Str("FR-CARB-01".into()));args132.push(Val::Str("316 STAINLESS STEEL".into()));args132.push(Val::Str("1 PER CARBONATOR".into()));args132.push(Val::Str("HSM-000336".into()));kw133.push(("revision".into(),Val::Str("B".into())));kw133.push(("status".into(),{let mut s=Vec::new();s.push(Val::Str("FINISHED PART".into()));s.push(Val::Str("DESIGN DEFINITION".into()));Val::tuple(s)}));fun134.call(args132,kw133)?};
{let fun137=e.get("c")?.attr("showPage")?;let mut args135=Vec::new();let mut kw136=Vec::new();fun137.call(args135,kw136)?};
{let fun140=e.get("c")?.attr("save")?;let mut args138=Vec::new();let mut kw139=Vec::new();fun140.call(args138,kw139)?};
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun143 = e.get("export_pdf")?;
        let mut args141 = Vec::new();
        let mut kw142 = Vec::new();
        args141.push(e.get("build_pdf")?);
        args141.push({
            let fun146 = e.get("str")?;
            let mut args144 = Vec::new();
            let mut kw145 = Vec::new();
            args144.push(e.get("PDF_PATH")?);
            fun146.call(args144, kw145)?
        });
        fun143.call(args141, kw142)?
    };
    {
        let fun149 = e.get("print")?;
        let mut args147 = Vec::new();
        let mut kw148 = Vec::new();
        args147.push({
            let mut str150 = String::new();
            str150.push_str("Exported: ");
            str150.push_str(&format(&e.get("PDF_PATH")?, &String::new())?);
            Val::Str(str150)
        });
        fun149.call(args147, kw148)?
    };
    Ok(Val::None)
}
