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
    for item18 in {
        let mut s = Vec::new();
        s.push(binary("truediv", e.get("HW")?, Val::Str("scripts".into()))?);
        s.push(binary(
            "truediv",
            e.get("HW")?,
            Val::Str("printed-parts/cold-core/reservoir".into()),
        )?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("p", item18)?;
        {
            let fun21 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args19 = Vec::new();
            let mut kw20 = Vec::new();
            args19.push(Val::Int(0i64));
            args19.push({
                let fun24 = e.get("str")?;
                let mut args22 = Vec::new();
                let mut kw23 = Vec::new();
                args22.push(e.get("p")?);
                fun24.call(args22, kw23)?
            });
            fun21.call(args19, kw20)?
        };
    }
    e.set("source", rt.import_module("reservoir")?)?;
    let mod25 = rt.import_module("_fabrication_drawing")?;
    import_star(&e, mod25.clone())?;
    let assigned26 = binary(
        "truediv",
        e.get("HERE")?,
        Val::Str("reservoir-float-rod-drawing.pdf".into()),
    )?;
    e.set("PDF_PATH", assigned26.clone())?;
    let assigned27 = {
        let mut s = Vec::new();
        s.push(Val::Int(792i64));
        s.push(Val::Int(612i64));
        Val::tuple(s)
    };
    e.set("SHEET", assigned27.clone())?;
    let assigned28 = e.get("source")?.attr("reservoir_rod_len")?;
    e.set("LENGTH", assigned28.clone())?;
    let assigned29 = e.get("source")?.attr("rod_diameter")?;
    e.set("DIAMETER", assigned29.clone())?;
    let assigned30 = Val::Float(0.1f64);
    e.set("LENGTH_MINUS", assigned30.clone())?;
    let assigned31 = Val::Float(0.05f64);
    e.set("DIAMETER_TOL", assigned31.clone())?;
    let assigned32 = Val::Float(0.1f64);
    e.set("STRAIGHTNESS", assigned32.clone())?;
    let assigned33 = Val::Float(0.08f64);
    e.set("EDGE_BREAK", assigned33.clone())?;
    let assigned34 = Val::Float(0.5f64);
    e.set("END_ANGLE", assigned34.clone())?;
    let assigned35 = {
        let mut s = Vec::new();
        s.push(Val::Float(0.05f64));
        s.push(Val::Float(0.5f64));
        Val::tuple(s)
    };
    let unpack36 = unpack(assigned35.clone(), 2)?;
    e.set("ENDPLAY_MIN", unpack36[0].clone())?;
    e.set("ENDPLAY_MAX", unpack36[1].clone())?;
    let assigned37 = Val::Str("HSM-000339".into());
    e.set("MATERIAL_ID", assigned37.clone())?;
    let assigned38 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("side-view".into()));
            s.push(Val::Int(40i64));
            s.push(Val::Int(375i64));
            s.push(Val::Int(750i64));
            s.push(Val::Int(565i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("end-view".into()));
            s.push(Val::Int(545i64));
            s.push(Val::Int(230i64));
            s.push(Val::Int(752i64));
            s.push(Val::Int(370i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("requirements".into()));
            s.push(Val::Int(40i64));
            s.push(Val::Int(155i64));
            s.push(Val::Int(548i64));
            s.push(Val::Int(370i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("title-block".into()));
            s.push(Val::Int(35i64));
            s.push(Val::Int(27i64));
            s.push(Val::Int(765i64));
            s.push(Val::Int(146i64));
            Val::tuple(s)
        });
        Val::list(s)
    };
    e.set("REVIEW_REGIONS", assigned38.clone())?;
    // views
    e.set("views", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned39 = {
                let mut s = Vec::new();
                s.push(Val::Int(72i64));
                s.push(Val::Int(447i64));
                s.push(e.get("MM")?);
                Val::tuple(s)
            };
            let unpack40 = unpack(assigned39.clone(), 3)?;
            e.set("x", unpack40[0].clone())?;
            e.set("y", unpack40[1].clone())?;
            e.set("s", unpack40[2].clone())?;
            let assigned41 = {
                let mut s = Vec::new();
                s.push(binary("mul", e.get("LENGTH")?, e.get("s")?)?);
                s.push(binary("mul", e.get("DIAMETER")?, e.get("s")?)?);
                Val::tuple(s)
            };
            let unpack42 = unpack(assigned41.clone(), 2)?;
            e.set("length", unpack42[0].clone())?;
            e.set("diameter", unpack42[1].clone())?;
            {
                let fun45 = e.get("text")?;
                let mut args43 = Vec::new();
                let mut kw44 = Vec::new();
                args43.push(e.get("c")?);
                args43.push(binary(
                    "add",
                    e.get("x")?,
                    binary("truediv", e.get("length")?, Val::Int(2i64))?,
                )?);
                args43.push(Val::Int(552i64));
                args43.push(Val::Str("FINISHED ROD - SIDE VIEW".into()));
                args43.push(Val::Int(12i64));
                kw44.push(("bold".into(), Val::Bool(true)));
                kw44.push(("align".into(), Val::Str("center".into())));
                fun45.call(args43, kw44)?
            };
            {
                let fun48 = e.get("text")?;
                let mut args46 = Vec::new();
                let mut kw47 = Vec::new();
                args46.push(e.get("c")?);
                args46.push(binary(
                    "add",
                    e.get("x")?,
                    binary("truediv", e.get("length")?, Val::Int(2i64))?,
                )?);
                args46.push(Val::Int(535i64));
                args46.push(Val::Str("SCALE 1:1".into()));
                args46.push(Val::Int(9i64));
                kw47.push(("align".into(), Val::Str("center".into())));
                fun48.call(args46, kw47)?
            };
            {
                let fun51 = e.get("c")?.attr("setLineWidth")?;
                let mut args49 = Vec::new();
                let mut kw50 = Vec::new();
                args49.push(e.get("VISIBLE")?);
                fun51.call(args49, kw50)?
            };
            {
                let fun54 = e.get("c")?.attr("rect")?;
                let mut args52 = Vec::new();
                let mut kw53 = Vec::new();
                args52.push(e.get("x")?);
                args52.push(e.get("y")?);
                args52.push(e.get("length")?);
                args52.push(e.get("diameter")?);
                kw53.push(("stroke".into(), Val::Int(1i64)));
                kw53.push(("fill".into(), Val::Int(0i64)));
                fun54.call(args52, kw53)?
            };
            {
                let fun57 = e.get("line")?;
                let mut args55 = Vec::new();
                let mut kw56 = Vec::new();
                args55.push(e.get("c")?);
                args55.push(binary("sub", e.get("x")?, Val::Int(14i64))?);
                args55.push(binary(
                    "add",
                    e.get("y")?,
                    binary("truediv", e.get("diameter")?, Val::Int(2i64))?,
                )?);
                args55.push(binary(
                    "add",
                    binary("add", e.get("x")?, e.get("length")?)?,
                    Val::Int(14i64),
                )?);
                args55.push(binary(
                    "add",
                    e.get("y")?,
                    binary("truediv", e.get("diameter")?, Val::Int(2i64))?,
                )?);
                kw56.push(("dash".into(), e.get("CENTER_DASH")?));
                fun57.call(args55, kw56)?
            };
            {
                let fun60 = e.get("horizontal_dimension")?;
                let mut args58 = Vec::new();
                let mut kw59 = Vec::new();
                args58.push(e.get("c")?);
                args58.push(e.get("x")?);
                args58.push(binary("add", e.get("x")?, e.get("length")?)?);
                args58.push(binary("add", e.get("y")?, e.get("diameter")?)?);
                args58.push(Val::Int(500i64));
                args58.push({
                    let mut str61 = String::new();
                    str61.push_str(&format(
                        &e.get("LENGTH")?,
                        &val_string({
                            let mut str62 = String::new();
                            str62.push_str(".2f");
                            Val::Str(str62)
                        })?,
                    )?);
                    str61.push_str(" +0.00 / -");
                    str61.push_str(&format(
                        &e.get("LENGTH_MINUS")?,
                        &val_string({
                            let mut str63 = String::new();
                            str63.push_str(".2f");
                            Val::Str(str63)
                        })?,
                    )?);
                    Val::Str(str61)
                });
                args58.push(Val::Int(12i64));
                fun60.call(args58, kw59)?
            };
            {
                let fun66 = e.get("leader")?;
                let mut args64 = Vec::new();
                let mut kw65 = Vec::new();
                args64.push(e.get("c")?);
                args64.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("x")?, e.get("length")?)?);
                    s.push(binary(
                        "add",
                        e.get("y")?,
                        binary("truediv", e.get("diameter")?, Val::Int(2i64))?,
                    )?);
                    Val::tuple(s)
                });
                args64.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(605i64));
                    s.push(Val::Int(403i64));
                    Val::tuple(s)
                });
                args64.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(581i64));
                    s.push(Val::Int(403i64));
                    Val::tuple(s)
                });
                args64.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("BOTH ENDS FLAT AND SQUARE".into()));
                    s.push(Val::Str("DEBURR; 0.08 MAX EDGE BREAK".into()));
                    Val::list(s)
                });
                args64.push(Val::Int(9i64));
                fun66.call(args64, kw65)?
            };
            let assigned67 = {
                let mut s = Vec::new();
                s.push(Val::Int(635i64));
                s.push(Val::Int(290i64));
                s.push(binary("mul", Val::Int(4i64), e.get("MM")?)?);
                Val::tuple(s)
            };
            let unpack68 = unpack(assigned67.clone(), 3)?;
            e.set("x", unpack68[0].clone())?;
            e.set("y", unpack68[1].clone())?;
            e.set("s", unpack68[2].clone())?;
            let assigned69 = binary(
                "truediv",
                binary("mul", e.get("DIAMETER")?, e.get("s")?)?,
                Val::Int(2i64),
            )?;
            e.set("radius", assigned69.clone())?;
            {
                let fun72 = e.get("text")?;
                let mut args70 = Vec::new();
                let mut kw71 = Vec::new();
                args70.push(e.get("c")?);
                args70.push(e.get("x")?);
                args70.push(Val::Int(353i64));
                args70.push(Val::Str("END VIEW".into()));
                args70.push(Val::Int(11i64));
                kw71.push(("bold".into(), Val::Bool(true)));
                kw71.push(("align".into(), Val::Str("center".into())));
                fun72.call(args70, kw71)?
            };
            {
                let fun75 = e.get("text")?;
                let mut args73 = Vec::new();
                let mut kw74 = Vec::new();
                args73.push(e.get("c")?);
                args73.push(e.get("x")?);
                args73.push(Val::Int(337i64));
                args73.push(Val::Str("SCALE 4:1".into()));
                args73.push(Val::Int(9i64));
                kw74.push(("align".into(), Val::Str("center".into())));
                fun75.call(args73, kw74)?
            };
            {
                let fun78 = e.get("c")?.attr("setLineWidth")?;
                let mut args76 = Vec::new();
                let mut kw77 = Vec::new();
                args76.push(e.get("VISIBLE")?);
                fun78.call(args76, kw77)?
            };
            {
                let fun81 = e.get("c")?.attr("circle")?;
                let mut args79 = Vec::new();
                let mut kw80 = Vec::new();
                args79.push(e.get("x")?);
                args79.push(e.get("y")?);
                args79.push(e.get("radius")?);
                kw80.push(("stroke".into(), Val::Int(1i64)));
                kw80.push(("fill".into(), Val::Int(0i64)));
                fun81.call(args79, kw80)?
            };
            {
                let fun84 = e.get("center")?;
                let mut args82 = Vec::new();
                let mut kw83 = Vec::new();
                args82.push(e.get("c")?);
                args82.push(e.get("x")?);
                args82.push(e.get("y")?);
                args82.push(binary("add", e.get("radius")?, Val::Int(9i64))?);
                fun84.call(args82, kw83)?
            };
            {
                let fun87 = e.get("circular_leader")?;
                let mut args85 = Vec::new();
                let mut kw86 = Vec::new();
                args85.push(e.get("c")?);
                args85.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y")?);
                    Val::tuple(s)
                });
                args85.push(e.get("radius")?);
                args85.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(674i64));
                    s.push(Val::Int(319i64));
                    Val::tuple(s)
                });
                args85.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(690i64));
                    s.push(Val::Int(319i64));
                    Val::tuple(s)
                });
                args85.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut str88 = String::new();
                        str88.push_str("Ø");
                        str88.push_str(&format(
                            &e.get("DIAMETER")?,
                            &val_string({
                                let mut str89 = String::new();
                                str89.push_str(".3f");
                                Val::Str(str89)
                            })?,
                        )?);
                        Val::Str(str88)
                    });
                    s.push({
                        let mut str90 = String::new();
                        str90.push_str("±");
                        str90.push_str(&format(
                            &e.get("DIAMETER_TOL")?,
                            &val_string({
                                let mut str91 = String::new();
                                str91.push_str(".2f");
                                Val::Str(str91)
                            })?,
                        )?);
                        Val::Str(str90)
                    });
                    Val::list(s)
                });
                args85.push(Val::Int(10i64));
                fun87.call(args85, kw86)?
            };
            {
                let fun94 = e.get("text")?;
                let mut args92 = Vec::new();
                let mut kw93 = Vec::new();
                args92.push(e.get("c")?);
                args92.push(e.get("x")?);
                args92.push(Val::Int(244i64));
                args92.push(Val::Str("SAME PART FOR A AND B".into()));
                args92.push(Val::Float(8.5f64));
                kw93.push(("bold".into(), Val::Bool(true)));
                kw93.push(("align".into(), Val::Str("center".into())));
                fun94.call(args92, kw93)?
            };
            Ok(Val::None)
        })
    })?;
    // requirements
    e.set("requirements",{let params=vec![("c".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);{let fun97=e.get("text")?;let mut args95=Vec::new();let mut kw96=Vec::new();args95.push(e.get("c")?);args95.push(Val::Int(48i64));args95.push(Val::Int(353i64));args95.push(Val::Str("FINISHED PART AND ASSEMBLY REQUIREMENTS".into()));args95.push(Val::Int(10i64));kw96.push(("bold".into(),Val::Bool(true)));fun97.call(args95,kw96)?};
let assigned98=binary("add",e.get("LENGTH")?,e.get("source")?.attr("reservoir_rod_clearance")?)?;e.set("seat_span",assigned98.clone())?;
let assigned99={let mut s=Vec::new();s.push(Val::Str("1. Material: 316 stainless round rod. Use stock meeting the diameter limits; stock must be longer than the finished cut. Quantity: two identical rods per cold core, one per flavor reservoir.".into()));s.push({let mut str100=String::new();str100.push_str("2. Length applies after cutting and deburring. Ends flat; each square to the axis within ");str100.push_str(&format(&e.get("END_ANGLE")?,&val_string({let mut str101=String::new();str101.push_str("g");Val::Str(str101)})?)?);str100.push_str("°. Edge break ");str100.push_str(&format(&e.get("EDGE_BREAK")?,&val_string({let mut str102=String::new();str102.push_str(".2f");Val::Str(str102)})?)?);str100.push_str(" MAX. Sliding surface free of raised burrs, sharp ridges and embedded debris; remove cutting fluid.");Val::Str(str100)});s.push({let mut str103=String::new();str103.push_str("3. Centerline departure from a straight line joining the end centers: ");str103.push_str(&format(&e.get("STRAIGHTNESS")?,&val_string({let mut str104=String::new();str104.push_str(".2f");Val::Str(str104)})?)?);str103.push_str(" MAX over the full length. Verify free travel through the actual float's complete stroke.");Val::Str(str103)});s.push({let mut str105=String::new();str105.push_str("4. Reservoir interface: Ø");str105.push_str(&format(&e.get("source")?.attr("rod_bore")?,&val_string({let mut str106=String::new();str106.push_str(".3f");Val::Str(str106)})?)?);str105.push_str(" nominal seat bores; lower seat to upper seat ");str105.push_str(&format(&e.get("seat_span")?,&val_string({let mut str107=String::new();str107.push_str(".2f");Val::Str(str107)})?)?);str105.push_str(" REF. At nominal seats, this rod's length limits leave 0.15-0.25 REF axial clearance.");Val::Str(str105)});s.push({let mut str108=String::new();str108.push_str("5. Seat lower end in the body boss and capture upper end in the cap boss; no weld. With the gasket and cap fully seated, verify ");str108.push_str(&format(&e.get("ENDPLAY_MIN")?,&val_string({let mut str109=String::new();str109.push_str(".2f");Val::Str(str109)})?)?);str108.push_str("-");str108.push_str(&format(&e.get("ENDPLAY_MAX")?,&val_string({let mut str110=String::new();str110.push_str(".2f");Val::Str(str110)})?)?);str108.push_str(" total axial endplay. Correct out-of-limit seats; retain the specified rod length. The rod must not hold the cap off its gasket.");Val::Str(str108)});Val::list(s)};e.set("items",assigned99.clone())?;
return Ok({let fun113=e.get("paragraphs")?;let mut args111=Vec::new();let mut kw112=Vec::new();args111.push(e.get("c")?);args111.push(Val::Int(48i64));args111.push(Val::Int(333i64));args111.push(e.get("items")?);args111.push(Val::Int(475i64));kw112.push(("size".into(),Val::Float(8.7f64)));kw112.push(("leading".into(),Val::Float(11.5f64)));kw112.push(("gap".into(),Val::Int(6i64)));fun113.call(args111,kw112)?});
Ok(Val::None)})})?;
    // build_pdf
    e.set("build_pdf",{let params=vec![("path".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned114={let fun117=e.get("canvas")?.attr("Canvas")?;let mut args115=Vec::new();let mut kw116=Vec::new();args115.push({let fun120=e.get("str")?;let mut args118=Vec::new();let mut kw119=Vec::new();args118.push(e.get("path")?);fun120.call(args118,kw119)?});kw116.push(("pagesize".into(),e.get("SHEET")?));kw116.push(("invariant".into(),Val::Int(1i64)));kw116.push(("pageCompression".into(),Val::Int(1i64)));fun117.call(args115,kw116)?};e.set("c",assigned114.clone())?;
{let fun123=e.get("c")?.attr("setTitle")?;let mut args121=Vec::new();let mut kw122=Vec::new();args121.push(Val::Str("Reservoir float guide rod - engineering drawing".into()));fun123.call(args121,kw122)?};
{let fun126=e.get("c")?.attr("setAuthor")?;let mut args124=Vec::new();let mut kw125=Vec::new();args124.push(Val::Str("Home Soda Machine / Codex".into()));fun126.call(args124,kw125)?};
{let fun129=e.get("c")?.attr("setSubject")?;let mut args127=Vec::new();let mut kw128=Vec::new();args127.push(Val::Str("FR-RES-01 Rev A: fixed finished length, end finish and reservoir-seat acceptance".into()));fun129.call(args127,kw128)?};
{let fun132=e.get("frame")?;let mut args130=Vec::new();let mut kw131=Vec::new();args130.push(e.get("c")?);args130.push(e.get("SHEET")?);fun132.call(args130,kw131)?};
{let fun135=e.get("views")?;let mut args133=Vec::new();let mut kw134=Vec::new();args133.push(e.get("c")?);fun135.call(args133,kw134)?};
{let fun138=e.get("requirements")?;let mut args136=Vec::new();let mut kw137=Vec::new();args136.push(e.get("c")?);fun138.call(args136,kw137)?};
{let fun141=e.get("title_block")?;let mut args139=Vec::new();let mut kw140=Vec::new();args139.push(e.get("c")?);args139.push(e.get("SHEET")?);args139.push(Val::Str("RESERVOIR FLOAT GUIDE ROD".into()));args139.push(Val::Str("FR-RES-01".into()));args139.push(Val::Str("316 STAINLESS STEEL".into()));args139.push(Val::Str("2 PER COLD CORE".into()));args139.push(e.get("MATERIAL_ID")?);args139.push({let mut s=Vec::new();s.push(Val::Str("FINISHED PART".into()));s.push(Val::Str("DESIGN DEFINITION".into()));Val::tuple(s)});fun141.call(args139,kw140)?};
{let fun144=e.get("c")?.attr("showPage")?;let mut args142=Vec::new();let mut kw143=Vec::new();fun144.call(args142,kw143)?};
{let fun147=e.get("c")?.attr("save")?;let mut args145=Vec::new();let mut kw146=Vec::new();fun147.call(args145,kw146)?};
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun150 = e.get("export_pdf")?;
        let mut args148 = Vec::new();
        let mut kw149 = Vec::new();
        args148.push(e.get("build_pdf")?);
        args148.push({
            let fun153 = e.get("str")?;
            let mut args151 = Vec::new();
            let mut kw152 = Vec::new();
            args151.push(e.get("PDF_PATH")?);
            fun153.call(args151, kw152)?
        });
        fun150.call(args148, kw149)?
    };
    {
        let fun156 = e.get("print")?;
        let mut args154 = Vec::new();
        let mut kw155 = Vec::new();
        args154.push({
            let mut str157 = String::new();
            str157.push_str("Exported: ");
            str157.push_str(&format(&e.get("PDF_PATH")?, &String::new())?);
            Val::Str(str157)
        });
        fun156.call(args154, kw155)?
    };
    Ok(Val::None)
}
