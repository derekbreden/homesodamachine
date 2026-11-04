#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
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
    };
    e.set("_here", assigned2.clone())?;
    let assigned9 = {
        let fun12 = e.get("next")?;
        let mut args10 = Vec::new();
        let mut kw11 = Vec::new();
        args10.push({
            let e = e.child();
            let out13 = Val::list(vec![]);
            for item14 in e.get("_here")?.attr("parents")?.iter()? {
                e.set("p", item14)?;
                if {
                    let v15 = e.get("p")?.attr("name")?;
                    let v16 = Val::Str("hardware".into());
                    Val::Bool(compare("eq", v15.clone(), v16.clone())?.truthy()?)
                }
                .truthy()?
                {
                    out13.attr("append")?.call(vec![e.get("p")?], vec![])?;
                }
            }
            out13
        });
        fun12.call(args10, kw11)?
    };
    e.set("_hw", assigned9.clone())?;
    if {
        let v20 = {
            let fun19 = e.get("str")?;
            let mut args17 = Vec::new();
            let mut kw18 = Vec::new();
            args17.push(e.get("_here")?.attr("parent")?);
            fun19.call(args17, kw18)?
        };
        let v21 = e.get("sys")?.attr("path")?;
        Val::Bool(compare("not_in", v20.clone(), v21.clone())?.truthy()?)
    }
    .truthy()?
    {
        {
            let fun24 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args22 = Vec::new();
            let mut kw23 = Vec::new();
            args22.push(Val::Int(0i64));
            args22.push({
                let fun27 = e.get("str")?;
                let mut args25 = Vec::new();
                let mut kw26 = Vec::new();
                args25.push(e.get("_here")?.attr("parent")?);
                fun27.call(args25, kw26)?
            });
            fun24.call(args22, kw23)?
        };
    }
    let mod28 = rt.import_module("_cold_scorecard")?;
    e.set("Check", rt.member("_cold_scorecard", "Check")?)?;
    e.set("verdict", rt.member("_cold_scorecard", "verdict")?)?;
    let assigned29 = binary(
        "truediv",
        binary("truediv", e.get("_hw")?, Val::Str("ledger".into()))?,
        Val::Str("bom.md".into()),
    )?;
    e.set("BOM", assigned29.clone())?;
    let assigned30 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("316 tube".into()));
            s.push(Val::Str("OnlineMetals #12498".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("carbonator-tube".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("endcap plates".into()));
            s.push(Val::Str(
                "SendCutSend 1/4\"-thick 316 SS circular endcap plate".into(),
            ));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("endcap-bottom".into()));
                s.push(Val::Str("endcap-top".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("earth clamp screw".into()));
            s.push(Val::Str("Carbonator earth-clamp screw".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("carbonator-earth-screw".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("earth clamp lockwasher".into()));
            s.push(Val::Str("DIN 6797".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("carbonator-earth-lockwasher".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("top-plate elbows".into()));
            s.push(Val::Str(
                "TAISHER 2PCS 316L SS 90° Barstock Street Elbow".into(),
            ));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("carbonator-elbow-water-in".into()));
                s.push(Val::Str("carbonator-elbow-prv".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("bottom-plate elbows".into()));
            s.push(Val::Str("neoFit AME4-N2-E".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("carbonator-elbow-co2-in".into()));
                s.push(Val::Str("carbonator-elbow-carb-water-out".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("water inlet jet".into()));
            s.push(Val::Str("Water-inlet jet cap".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("water-inlet-jet-cap-nominal".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("upper float stop".into()));
            s.push(Val::Str("Carbonator upper float stop".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("float-stop-carb-top".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("PRV".into()));
            s.push(Val::Str("Control Devices SV-125".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("prv-sv125".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("PTFE thread tape".into()));
            s.push(Val::Str("Millrose 70894 Nickel Guard".into()));
            s.push({
                let mut s = Vec::new();
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("water PTC collet".into()));
            s.push(Val::Str("John Guest PP010822E".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("collet-water-in".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("evaporator coil".into()));
            s.push(Val::Str("GOORY 1/4\" OD × 50 ft ACR copper coil".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("evap-coil".into()));
                s.push(Val::Str("evap-tail-inlet".into()));
                s.push(Val::Str("evap-tail-outlet".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("carbonator probe".into()));
            s.push(Val::Str("TIEXYE DS18B20".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("probe-carbonator-ds18b20".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("coil probe".into()));
            s.push(Val::Str("DS18S20+ TO-92".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("probe-coil-ds18s20".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("pour-in-place foam".into()));
            s.push(Val::Str("closed-cell pour-in-place PU foam".into()));
            s.push({
                let mut s = Vec::new();
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("foil tape".into()));
            s.push(Val::Str("3M 425 aluminum foil tape".into()));
            s.push({
                let mut s = Vec::new();
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("foam shell".into()));
            s.push(Val::Str("Cold-core inner shell (foam-shell)".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("foam-shell".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("foam cap lid top".into()));
            s.push(Val::Str("Cold-core foam cap lid — top".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("foam-cap-lid-top".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("foam cap bottom".into()));
            s.push(Val::Str("Cold-core foam cap — bottom".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("foam-cap-bottom".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("B-fill bend holder".into()));
            s.push(Val::Str("Reservoir B fill bend holder".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("reservoir-b-fill-guide".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("PRV shroud".into()));
            s.push(Val::Str("PRV shroud".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("prv-shroud".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("reservoir body L".into()));
            s.push(Val::Str("Flavor reservoir body — left".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("reservoir-b".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("reservoir body R".into()));
            s.push(Val::Str("Flavor reservoir body — right".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("reservoir-a".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("reservoir cap L".into()));
            s.push(Val::Str("Flavor reservoir cap — left".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("reservoir-b-cap".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("reservoir cap R".into()));
            s.push(Val::Str("Flavor reservoir cap — right".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("reservoir-a-cap".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("reservoir gaskets".into()));
            s.push(Val::Str("2× reservoir gasket".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("reservoir-a-gasket".into()));
                s.push(Val::Str("reservoir-b-gasket".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("reed bridge".into()));
            s.push(Val::Str("Carbonator reed bridge".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("reed-bridge".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("floats".into()));
            s.push(Val::Str("ASA Aero magnetic float".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("float-carb".into()));
                s.push(Val::Str("float-a".into()));
                s.push(Val::Str("float-b".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("float magnets".into()));
            s.push(Val::Str("K&J Magnetics RC62 N42 ring magnet".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("float-carb".into()));
                s.push(Val::Str("float-a".into()));
                s.push(Val::Str("float-b".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("reed columns".into()));
            s.push(Val::Str("Pre-soldered reed-and-wire column".into()));
            s.push({
                let mut s = Vec::new();
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("float rods".into()));
            s.push(Val::Str("Tandefio 1/8\" × 12\" 316 SS round rod".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("float-rod-carb".into()));
                s.push(Val::Str("float-rod-a".into()));
                s.push(Val::Str("float-rod-b".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("reeds".into()));
            s.push(Val::Str("Littelfuse MDSR-7-10-15 reed switches".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("reed-carb-1".into()));
                s.push(Val::Str("reed-carb-2".into()));
                s.push(Val::Str("reed-a-1".into()));
                s.push(Val::Str("reed-a-2".into()));
                s.push(Val::Str("reed-a-3".into()));
                s.push(Val::Str("reed-a-4".into()));
                s.push(Val::Str("reed-b-1".into()));
                s.push(Val::Str("reed-b-2".into()));
                s.push(Val::Str("reed-b-3".into()));
                s.push(Val::Str("reed-b-4".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("M3 heat-set inserts".into()));
            s.push(Val::Str(
                "ruthex RX-M3 × 5.7 full-length heat-set inserts".into(),
            ));
            s.push({
                let mut s = Vec::new();
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("M5 closure inserts".into()));
            s.push(Val::Str("ruthex M5 Threaded Inserts".into()));
            s.push({
                let mut s = Vec::new();
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("cap clamp screws".into()));
            s.push(Val::Str("SVLING M5 × 0.8 × 100 mm".into()));
            s.push({
                let fun33 = e.get("tuple")?;
                let mut args31 = Vec::new();
                let mut kw32 = Vec::new();
                args31.push({
                    let e = e.child();
                    let out34 = Val::list(vec![]);
                    for item35 in {
                        let mut s = Vec::new();
                        s.push(Val::Str("top".into()));
                        s.push(Val::Str("bottom".into()));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("side", item35)?;
                        for item36 in {
                            let fun39 = e.get("range")?;
                            let mut args37 = Vec::new();
                            let mut kw38 = Vec::new();
                            args37.push(Val::Int(1i64));
                            args37.push(Val::Int(11i64));
                            fun39.call(args37, kw38)?
                        }
                        .iter()?
                        {
                            e.set("i", item36)?;
                            out34.attr("append")?.call(
                                vec![{
                                    let mut str40 = String::new();
                                    str40.push_str("cap-clamp-");
                                    str40.push_str(&format(&e.get("side")?, &String::new())?);
                                    str40.push_str("-");
                                    str40.push_str(&format(&e.get("i")?, &String::new())?);
                                    Val::Str(str40)
                                }],
                                vec![],
                            )?;
                        }
                    }
                    out34
                });
                fun33.call(args31, kw32)?
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("reservoir cap screws".into()));
            s.push(Val::Str(
                "BNUOK M3 × 12 mm socket head cap, 304 stainless".into(),
            ));
            s.push({
                let mut s = Vec::new();
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("reservoir tube grips".into()));
            s.push(Val::Str("4× reservoir tube grip".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("reservoir-grip-a-fill".into()));
                s.push(Val::Str("reservoir-grip-a-draw".into()));
                s.push(Val::Str("reservoir-grip-b-fill".into()));
                s.push(Val::Str("reservoir-grip-b-draw".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("reservoir air grips".into()));
            s.push(Val::Str("2× reservoir air grip".into()));
            s.push({
                let mut s = Vec::new();
                s.push(Val::Str("reservoir-grip-a-air".into()));
                s.push(Val::Str("reservoir-grip-b-air".into()));
                Val::tuple(s)
            });
            Val::tuple(s)
        });
        Val::tuple(s)
    };
    e.set("PARTS", assigned30.clone())?;
    let assigned41 = {
        let mut s = Vec::new();
        s.push(Val::Str("line-".into()));
        s.push(Val::Str("tube-".into()));
        Val::tuple(s)
    };
    e.set("UNBILLED_PREFIXES", assigned41.clone())?;
    // _bill_text
    e.set("_bill_text", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun44 = e.get("BOM")?.attr("read_text")?;
                let mut args42 = Vec::new();
                let mut kw43 = Vec::new();
                kw43.push(("encoding".into(), Val::Str("utf-8".into())));
                fun44.call(args42, kw43)?
            });
            Ok(Val::None)
        })
    })?;
    // check
    e.set("check", {
        let params = vec![("placed".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned45 = {
                let fun48 = e.get("_bill_text")?;
                let mut args46 = Vec::new();
                let mut kw47 = Vec::new();
                fun48.call(args46, kw47)?
            };
            e.set("bill", assigned45.clone())?;
            let assigned49 = {
                let fun52 = e.get("set")?;
                let mut args50 = Vec::new();
                let mut kw51 = Vec::new();
                fun52.call(args50, kw51)?
            };
            e.set("claimed", assigned49.clone())?;
            let assigned53 = {
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
                Val::tuple(s)
            };
            let unpack54 = unpack(assigned53.clone(), 3)?;
            e.set("missing_row", unpack54[0].clone())?;
            e.set("no_body", unpack54[1].clone())?;
            e.set("absent", unpack54[2].clone())?;
            for item55 in e.get("PARTS")?.iter()? {
                let unpack81 = unpack(item55, 3)?;
                e.set("label", unpack81[0].clone())?;
                e.set("bills", unpack81[1].clone())?;
                e.set("bodies", unpack81[2].clone())?;
                if {
                    let v56 = e.get("bills")?;
                    let v57 = e.get("bill")?;
                    Val::Bool(compare("not_in", v56.clone(), v57.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun60 = e.get("missing_row")?.attr("append")?;
                        let mut args58 = Vec::new();
                        let mut kw59 = Vec::new();
                        args58.push({
                            let mut str61 = String::new();
                            str61.push_str(&format(&e.get("label")?, &String::new())?);
                            str61.push_str(": no row in bom.md matching \"");
                            str61.push_str(&format(&e.get("bills")?, &String::new())?);
                            str61.push_str("\"");
                            Val::Str(str61)
                        });
                        fun60.call(args58, kw59)?
                    };
                }
                if unary("not", e.get("bodies")?)?.truthy()? {
                    {
                        let fun64 = e.get("no_body")?.attr("append")?;
                        let mut args62 = Vec::new();
                        let mut kw63 = Vec::new();
                        args62.push({
                            let mut str65 = String::new();
                            str65.push_str(&format(&e.get("label")?, &String::new())?);
                            str65.push_str(" — billed, no solid here (\"");
                            str65.push_str(&format(&e.get("bills")?, &String::new())?);
                            str65.push_str("\")");
                            Val::Str(str65)
                        });
                        fun64.call(args62, kw63)?
                    };
                    continue;
                }
                let assigned66 = {
                    let e = e.child();
                    let out67 = Val::list(vec![]);
                    for item68 in e.get("bodies")?.iter()? {
                        e.set("b", item68)?;
                        if {
                            let v69 = e.get("b")?;
                            let v70 = e.get("placed")?;
                            Val::Bool(compare("not_in", v69.clone(), v70.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            out67.attr("append")?.call(vec![e.get("b")?], vec![])?;
                        }
                    }
                    out67
                };
                e.set("gone", assigned66.clone())?;
                {
                    let fun73 = e.get("claimed")?.attr("update")?;
                    let mut args71 = Vec::new();
                    let mut kw72 = Vec::new();
                    args71.push(e.get("bodies")?);
                    fun73.call(args71, kw72)?
                };
                if e.get("gone")?.truthy()? {
                    {
                        let fun76 = e.get("absent")?.attr("append")?;
                        let mut args74 = Vec::new();
                        let mut kw75 = Vec::new();
                        args74.push({
                            let mut str77 = String::new();
                            str77.push_str(&format(&e.get("label")?, &String::new())?);
                            str77.push_str(": ");
                            str77.push_str(&format(
                                &{
                                    let fun80 = Val::Str(", ".into()).attr("join")?;
                                    let mut args78 = Vec::new();
                                    let mut kw79 = Vec::new();
                                    args78.push(e.get("gone")?);
                                    fun80.call(args78, kw79)?
                                },
                                &String::new(),
                            )?);
                            str77.push_str(" not placed");
                            Val::Str(str77)
                        });
                        fun76.call(args74, kw75)?
                    };
                }
            }
            let assigned82 = {
                let fun85 = e.get("sorted")?;
                let mut args83 = Vec::new();
                let mut kw84 = Vec::new();
                args83.push({
                    let e = e.child();
                    let out86 = Val::list(vec![]);
                    for item87 in e.get("placed")?.iter()? {
                        e.set("n", item87)?;
                        if {
                            let v91 = {
                                let v92 = e.get("n")?;
                                let v93 = e.get("claimed")?;
                                Val::Bool(compare("not_in", v92.clone(), v93.clone())?.truthy()?)
                            };
                            if v91.truthy()? {
                                unary("not", {
                                    let fun90 = e.get("n")?.attr("startswith")?;
                                    let mut args88 = Vec::new();
                                    let mut kw89 = Vec::new();
                                    args88.push(e.get("UNBILLED_PREFIXES")?);
                                    fun90.call(args88, kw89)?
                                })?
                            } else {
                                v91
                            }
                        }
                        .truthy()?
                        {
                            out86.attr("append")?.call(vec![e.get("n")?], vec![])?;
                        }
                    }
                    out86
                });
                fun85.call(args83, kw84)?
            };
            e.set("unclaimed", assigned82.clone())?;
            let assigned94 = {
                let fun97 = e.get("sum")?;
                let mut args95 = Vec::new();
                let mut kw96 = Vec::new();
                args95.push({
                    let e = e.child();
                    let out98 = Val::list(vec![]);
                    for item99 in e.get("PARTS")?.iter()? {
                        let unpack100 = unpack(item99, 3)?;
                        e.set("_l", unpack100[0].clone())?;
                        e.set("_b", unpack100[1].clone())?;
                        e.set("bodies", unpack100[2].clone())?;
                        if {
                            let v108 = e.get("bodies")?;
                            if v108.truthy()? {
                                {
                                    let fun103 = e.get("all")?;
                                    let mut args101 = Vec::new();
                                    let mut kw102 = Vec::new();
                                    args101.push({
                                        let e = e.child();
                                        let out104 = Val::list(vec![]);
                                        for item105 in e.get("bodies")?.iter()? {
                                            e.set("b", item105)?;
                                            out104.attr("append")?.call(
                                                vec![{
                                                    let v106 = e.get("b")?;
                                                    let v107 = e.get("placed")?;
                                                    Val::Bool(
                                                        compare("in", v106.clone(), v107.clone())?
                                                            .truthy()?,
                                                    )
                                                }],
                                                vec![],
                                            )?;
                                        }
                                        out104
                                    });
                                    fun103.call(args101, kw102)?
                                }
                            } else {
                                v108
                            }
                        }
                        .truthy()?
                        {
                            out98.attr("append")?.call(vec![Val::Int(1i64)], vec![])?;
                        }
                    }
                    out98
                });
                fun97.call(args95, kw96)?
            };
            e.set("covered", assigned94.clone())?;
            let assigned109 = binary(
                "add",
                binary("add", e.get("missing_row")?, e.get("absent")?)?,
                e.get("no_body")?,
            )?;
            e.set("detail", assigned109.clone())?;
            e.set(
                "detail",
                binary("add", e.get("detail")?, {
                    let e = e.child();
                    let out110 = Val::list(vec![]);
                    for item111 in e.get("unclaimed")?.iter()? {
                        e.set("n", item111)?;
                        out110.attr("append")?.call(
                            vec![{
                                let mut str112 = String::new();
                                str112.push_str("placed, unbilled: ");
                                str112.push_str(&format(&e.get("n")?, &String::new())?);
                                Val::Str(str112)
                            }],
                            vec![],
                        )?;
                    }
                    out110
                })?,
            )?;
            return Ok({
                let fun115 = e.get("Check")?;
                let mut args113 = Vec::new();
                let mut kw114 = Vec::new();
                args113.push(Val::Str("bom-covered".into()));
                args113.push(Val::Str(
                    "Every billed cold-core part has a body here".into(),
                ));
                args113.push(Val::Str("goal".into()));
                args113.push({
                    let fun118 = e.get("verdict")?;
                    let mut args116 = Vec::new();
                    let mut kw117 = Vec::new();
                    args116.push(unary("not", e.get("detail")?)?);
                    fun118.call(args116, kw117)?
                });
                args113.push({
                    let mut str119 = String::new();
                    str119.push_str(&format(&e.get("covered")?, &String::new())?);
                    str119.push_str("/");
                    str119.push_str(&format(
                        &{
                            let fun122 = e.get("len")?;
                            let mut args120 = Vec::new();
                            let mut kw121 = Vec::new();
                            args120.push(e.get("PARTS")?);
                            fun122.call(args120, kw121)?
                        },
                        &String::new(),
                    )?);
                    Val::Str(str119)
                });
                args113.push(Val::Str("a body per billed part".into()));
                args113.push(e.get("detail")?);
                fun115.call(args113, kw114)?
            });
            Ok(Val::None)
        })
    })?;
    // report
    e.set("report", {
        let params = vec![("placed".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned123 = {
                let fun126 = e.get("check")?;
                let mut args124 = Vec::new();
                let mut kw125 = Vec::new();
                args124.push(e.get("placed")?);
                fun126.call(args124, kw125)?
            };
            e.set("c", assigned123.clone())?;
            {
                let fun129 = e.get("print")?;
                let mut args127 = Vec::new();
                let mut kw128 = Vec::new();
                args127.push({
                    let mut str130 = String::new();
                    str130.push_str("  bom coverage    ");
                    str130.push_str(&format(&e.get("c")?.attr("value")?, &String::new())?);
                    str130.push_str(" billed parts carry a body");
                    Val::Str(str130)
                });
                fun129.call(args127, kw128)?
            };
            for item131 in e.get("c")?.attr("detail")?.iter()? {
                e.set("line", item131)?;
                {
                    let fun134 = e.get("print")?;
                    let mut args132 = Vec::new();
                    let mut kw133 = Vec::new();
                    args132.push({
                        let mut str135 = String::new();
                        str135.push_str("    ");
                        str135.push_str(&format(&e.get("line")?, &String::new())?);
                        Val::Str(str135)
                    });
                    fun134.call(args132, kw133)?
                };
            }
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
