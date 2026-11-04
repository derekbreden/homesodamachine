#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    let mod1 = rt.import_module("collections")?;
    e.set("namedtuple", rt.member("collections", "namedtuple")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
    let assigned2 = Val::Float(25.4f64);
    e.set("IN", assigned2.clone())?;
    let assigned3 = {
        let fun6 = e.get("namedtuple")?;
        let mut args4 = Vec::new();
        let mut kw5 = Vec::new();
        args4.push(Val::Str("Mouth".into()));
        args4.push({
            let mut s = Vec::new();
            s.push(Val::Str("pos".into()));
            s.push(Val::Str("axis".into()));
            s.push(Val::Str("diam".into()));
            Val::list(s)
        });
        fun6.call(args4, kw5)?
    };
    e.set("Mouth", assigned3.clone())?;
    // _hex
    e.set("_hex", {
        let params = vec![
            ("across_flats".into(), None, false),
            ("height".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned7 = binary("truediv", e.get("across_flats")?, {
                let fun10 = e.get("math")?.attr("sqrt")?;
                let mut args8 = Vec::new();
                let mut kw9 = Vec::new();
                args8.push(Val::Float(3.0f64));
                fun10.call(args8, kw9)?
            })?;
            e.set("r", assigned7.clone())?;
            let assigned11 = {
                let e = e.child();
                let out12 = Val::list(vec![]);
                for item13 in {
                    let fun16 = e.get("range")?;
                    let mut args14 = Vec::new();
                    let mut kw15 = Vec::new();
                    args14.push(Val::Int(6i64));
                    fun16.call(args14, kw15)?
                }
                .iter()?
                {
                    e.set("i", item13)?;
                    out12.attr("append")?.call(
                        vec![{
                            let mut s = Vec::new();
                            s.push(binary("mul", e.get("r")?, {
                                let fun19 = e.get("math")?.attr("cos")?;
                                let mut args17 = Vec::new();
                                let mut kw18 = Vec::new();
                                args17.push({
                                    let fun22 = e.get("math")?.attr("radians")?;
                                    let mut args20 = Vec::new();
                                    let mut kw21 = Vec::new();
                                    args20.push(binary("mul", Val::Int(60i64), e.get("i")?)?);
                                    fun22.call(args20, kw21)?
                                });
                                fun19.call(args17, kw18)?
                            })?);
                            s.push(binary("mul", e.get("r")?, {
                                let fun25 = e.get("math")?.attr("sin")?;
                                let mut args23 = Vec::new();
                                let mut kw24 = Vec::new();
                                args23.push({
                                    let fun28 = e.get("math")?.attr("radians")?;
                                    let mut args26 = Vec::new();
                                    let mut kw27 = Vec::new();
                                    args26.push(binary("mul", Val::Int(60i64), e.get("i")?)?);
                                    fun28.call(args26, kw27)?
                                });
                                fun25.call(args23, kw24)?
                            })?);
                            Val::tuple(s)
                        }],
                        vec![],
                    )?;
                }
                out12
            };
            e.set("pts", assigned11.clone())?;
            return Ok({
                let fun31 = {
                    let fun34 = {
                        let fun37 = {
                            let fun40 = {
                                let fun43 = e.get("cq")?.attr("Workplane")?;
                                let mut args41 = Vec::new();
                                let mut kw42 = Vec::new();
                                args41.push(Val::Str("XY".into()));
                                fun43.call(args41, kw42)?
                            }
                            .attr("polyline")?;
                            let mut args38 = Vec::new();
                            let mut kw39 = Vec::new();
                            args38.push(binary(
                                "add",
                                e.get("pts")?,
                                e.get("pts")?.get(Val::Slice {
                                    start: None,
                                    stop: Some(Val::Int(1i64).integer()?),
                                    step: 1,
                                })?,
                            )?);
                            fun40.call(args38, kw39)?
                        }
                        .attr("wire")?;
                        let mut args35 = Vec::new();
                        let mut kw36 = Vec::new();
                        fun37.call(args35, kw36)?
                    }
                    .attr("extrude")?;
                    let mut args32 = Vec::new();
                    let mut kw33 = Vec::new();
                    args32.push(e.get("height")?);
                    fun34.call(args32, kw33)?
                }
                .attr("val")?;
                let mut args29 = Vec::new();
                let mut kw30 = Vec::new();
                fun31.call(args29, kw30)?
            });
            Ok(Val::None)
        })
    })?;
    // _cyl
    e.set("_cyl", {
        let params = vec![
            ("radius".into(), None, false),
            ("height".into(), None, false),
            (
                "base".into(),
                Some({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                }),
                false,
            ),
            (
                "axis".into(),
                Some({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(1i64));
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
            return Ok({
                let fun46 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                let mut args44 = Vec::new();
                let mut kw45 = Vec::new();
                args44.push(e.get("radius")?);
                args44.push(e.get("height")?);
                args44.push({
                    let fun49 = e.get("cq")?.attr("Vector")?;
                    let mut args47 = Vec::new();
                    let mut kw48 = Vec::new();
                    args47.extend(e.get("base")?.iter()?);
                    fun49.call(args47, kw48)?
                });
                args44.push({
                    let fun52 = e.get("cq")?.attr("Vector")?;
                    let mut args50 = Vec::new();
                    let mut kw51 = Vec::new();
                    args50.extend(e.get("axis")?.iter()?);
                    fun52.call(args50, kw51)?
                });
                fun46.call(args44, kw45)?
            });
            Ok(Val::None)
        })
    })?;
    // _orient
    e.set("_orient", {
        let params = vec![("solid".into(), None, false), ("axis".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned53 = {
                let fun56 = e.get("cq")?.attr("Vector")?;
                let mut args54 = Vec::new();
                let mut kw55 = Vec::new();
                args54.extend(e.get("axis")?.iter()?);
                fun56.call(args54, kw55)?
            };
            e.set("axis", assigned53.clone())?;
            let assigned57 = {
                let fun60 = e.get("axis")?.attr("normalized")?;
                let mut args58 = Vec::new();
                let mut kw59 = Vec::new();
                fun60.call(args58, kw59)?
            };
            e.set("axis", assigned57.clone())?;
            let assigned61 = {
                let fun64 = e.get("cq")?.attr("Vector")?;
                let mut args62 = Vec::new();
                let mut kw63 = Vec::new();
                args62.push(Val::Int(0i64));
                args62.push(Val::Int(0i64));
                args62.push(Val::Int(1i64));
                fun64.call(args62, kw63)?
            };
            e.set("z", assigned61.clone())?;
            let assigned65 = {
                let fun68 = e.get("max")?;
                let mut args66 = Vec::new();
                let mut kw67 = Vec::new();
                args66.push(unary("neg", Val::Float(1.0f64))?);
                args66.push({
                    let fun71 = e.get("min")?;
                    let mut args69 = Vec::new();
                    let mut kw70 = Vec::new();
                    args69.push(Val::Float(1.0f64));
                    args69.push({
                        let fun74 = e.get("z")?.attr("dot")?;
                        let mut args72 = Vec::new();
                        let mut kw73 = Vec::new();
                        args72.push(e.get("axis")?);
                        fun74.call(args72, kw73)?
                    });
                    fun71.call(args69, kw70)?
                });
                fun68.call(args66, kw67)?
            };
            e.set("dot", assigned65.clone())?;
            if {
                let v75 = e.get("dot")?;
                let v76 = binary("sub", Val::Int(1i64), Val::Float(1e-12f64))?;
                Val::Bool(compare("gt", v75.clone(), v76.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("solid")?);
            }
            if {
                let v77 = e.get("dot")?;
                let v78 = binary("add", unary("neg", Val::Int(1i64))?, Val::Float(1e-12f64))?;
                Val::Bool(compare("lt", v77.clone(), v78.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok({
                    let fun81 = e.get("solid")?.attr("rotate")?;
                    let mut args79 = Vec::new();
                    let mut kw80 = Vec::new();
                    args79.push({
                        let fun84 = e.get("cq")?.attr("Vector")?;
                        let mut args82 = Vec::new();
                        let mut kw83 = Vec::new();
                        args82.push(Val::Int(0i64));
                        args82.push(Val::Int(0i64));
                        args82.push(Val::Int(0i64));
                        fun84.call(args82, kw83)?
                    });
                    args79.push({
                        let fun87 = e.get("cq")?.attr("Vector")?;
                        let mut args85 = Vec::new();
                        let mut kw86 = Vec::new();
                        args85.push(Val::Int(1i64));
                        args85.push(Val::Int(0i64));
                        args85.push(Val::Int(0i64));
                        fun87.call(args85, kw86)?
                    });
                    args79.push(Val::Int(180i64));
                    fun81.call(args79, kw80)?
                });
            }
            return Ok({
                let fun90 = e.get("solid")?.attr("rotate")?;
                let mut args88 = Vec::new();
                let mut kw89 = Vec::new();
                args88.push({
                    let fun93 = e.get("cq")?.attr("Vector")?;
                    let mut args91 = Vec::new();
                    let mut kw92 = Vec::new();
                    args91.push(Val::Int(0i64));
                    args91.push(Val::Int(0i64));
                    args91.push(Val::Int(0i64));
                    fun93.call(args91, kw92)?
                });
                args88.push({
                    let fun96 = e.get("z")?.attr("cross")?;
                    let mut args94 = Vec::new();
                    let mut kw95 = Vec::new();
                    args94.push(e.get("axis")?);
                    fun96.call(args94, kw95)?
                });
                args88.push({
                    let fun99 = e.get("math")?.attr("degrees")?;
                    let mut args97 = Vec::new();
                    let mut kw98 = Vec::new();
                    args97.push({
                        let fun102 = e.get("math")?.attr("acos")?;
                        let mut args100 = Vec::new();
                        let mut kw101 = Vec::new();
                        args100.push(e.get("dot")?);
                        fun102.call(args100, kw101)?
                    });
                    fun99.call(args97, kw98)?
                });
                fun90.call(args88, kw89)?
            });
            Ok(Val::None)
        })
    })?;
    let assigned103 = binary("mul", Val::Float(0.625f64), e.get("IN")?)?;
    e.set("ELBOW_HEX_AF", assigned103.clone())?;
    let assigned104 = binary("mul", Val::Float(0.81f64), e.get("IN")?)?;
    e.set("ELBOW_LEG", assigned104.clone())?;
    let assigned105 = binary("mul", Val::Float(0.25f64), e.get("IN")?)?;
    e.set("ELBOW_BORE", assigned105.clone())?;
    let assigned106 = binary(
        "mul",
        binary("mul", Val::Float(0.5f64), Val::Float(0.4375f64))?,
        e.get("IN")?,
    )?;
    e.set("ELBOW_MALE_R", assigned106.clone())?;
    let assigned107 = binary("mul", Val::Float(0.26f64), e.get("IN")?)?;
    e.set("ELBOW_MALE_LEN", assigned107.clone())?;
    let assigned108 = binary(
        "mul",
        binary("mul", Val::Float(0.5f64), Val::Float(0.54f64))?,
        e.get("IN")?,
    )?;
    e.set("SOCKET_R", assigned108.clone())?;
    let assigned109 = binary("mul", Val::Float(0.5f64), e.get("IN")?)?;
    e.set("SOCKET_DEPTH", assigned109.clone())?;
    // street_elbow
    e.set("street_elbow", {
        let params = vec![
            ("corner".into(), None, true),
            (
                "up".into(),
                Some({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(1i64));
                    Val::tuple(s)
                }),
                true,
            ),
            ("out".into(), None, true),
            ("up_leg".into(), Some(Val::None), true),
            ("out_leg".into(), Some(Val::None), true),
            ("male_len".into(), Some(Val::None), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned110 = {
                let fun113 = {
                    let fun116 = e.get("cq")?.attr("Vector")?;
                    let mut args114 = Vec::new();
                    let mut kw115 = Vec::new();
                    args114.extend(e.get("up")?.iter()?);
                    fun116.call(args114, kw115)?
                }
                .attr("normalized")?;
                let mut args111 = Vec::new();
                let mut kw112 = Vec::new();
                fun113.call(args111, kw112)?
            };
            e.set("up", assigned110.clone())?;
            let assigned117 = {
                let fun120 = {
                    let fun123 = e.get("cq")?.attr("Vector")?;
                    let mut args121 = Vec::new();
                    let mut kw122 = Vec::new();
                    args121.extend(e.get("out")?.iter()?);
                    fun123.call(args121, kw122)?
                }
                .attr("normalized")?;
                let mut args118 = Vec::new();
                let mut kw119 = Vec::new();
                fun120.call(args118, kw119)?
            };
            e.set("out", assigned117.clone())?;
            let assigned124 = {
                let fun127 = e.get("cq")?.attr("Vector")?;
                let mut args125 = Vec::new();
                let mut kw126 = Vec::new();
                args125.extend(e.get("corner")?.iter()?);
                fun127.call(args125, kw126)?
            };
            e.set("c", assigned124.clone())?;
            let assigned128 = if {
                let v129 = e.get("up_leg")?;
                let v130 = Val::None;
                Val::Bool(compare("is", v129.clone(), v130.clone())?.truthy()?)
            }
            .truthy()?
            {
                e.get("ELBOW_LEG")?
            } else {
                e.get("up_leg")?
            };
            e.set("up_leg", assigned128.clone())?;
            let assigned131 = if {
                let v132 = e.get("out_leg")?;
                let v133 = Val::None;
                Val::Bool(compare("is", v132.clone(), v133.clone())?.truthy()?)
            }
            .truthy()?
            {
                e.get("ELBOW_LEG")?
            } else {
                e.get("out_leg")?
            };
            e.set("out_leg", assigned131.clone())?;
            let assigned134 = if {
                let v135 = e.get("male_len")?;
                let v136 = Val::None;
                Val::Bool(compare("is", v135.clone(), v136.clone())?.truthy()?)
            }
            .truthy()?
            {
                e.get("ELBOW_MALE_LEN")?
            } else {
                e.get("male_len")?
            };
            e.set("male_len", assigned134.clone())?;
            let assigned137 = {
                let fun140 = {
                    let fun143 = e.get("_orient")?;
                    let mut args141 = Vec::new();
                    let mut kw142 = Vec::new();
                    args141.push({
                        let fun146 = e.get("_hex")?;
                        let mut args144 = Vec::new();
                        let mut kw145 = Vec::new();
                        args144.push(e.get("ELBOW_HEX_AF")?);
                        args144.push(e.get("up_leg")?);
                        fun146.call(args144, kw145)?
                    });
                    args141.push(e.get("up")?);
                    fun143.call(args141, kw142)?
                }
                .attr("translate")?;
                let mut args138 = Vec::new();
                let mut kw139 = Vec::new();
                args138.push(e.get("c")?);
                fun140.call(args138, kw139)?
            };
            e.set("leg_up", assigned137.clone())?;
            let assigned147 = {
                let fun150 = {
                    let fun153 = e.get("_orient")?;
                    let mut args151 = Vec::new();
                    let mut kw152 = Vec::new();
                    args151.push({
                        let fun156 = e.get("_hex")?;
                        let mut args154 = Vec::new();
                        let mut kw155 = Vec::new();
                        args154.push(e.get("ELBOW_HEX_AF")?);
                        args154.push(e.get("out_leg")?);
                        fun156.call(args154, kw155)?
                    });
                    args151.push(e.get("out")?);
                    fun153.call(args151, kw152)?
                }
                .attr("translate")?;
                let mut args148 = Vec::new();
                let mut kw149 = Vec::new();
                args148.push(e.get("c")?);
                fun150.call(args148, kw149)?
            };
            e.set("leg_out", assigned147.clone())?;
            let assigned157 = {
                let fun160 = {
                    let fun163 = e.get("_orient")?;
                    let mut args161 = Vec::new();
                    let mut kw162 = Vec::new();
                    args161.push({
                        let fun166 = e.get("_cyl")?;
                        let mut args164 = Vec::new();
                        let mut kw165 = Vec::new();
                        args164.push(e.get("ELBOW_MALE_R")?);
                        args164.push(e.get("male_len")?);
                        fun166.call(args164, kw165)?
                    });
                    args161.push(e.get("up")?);
                    fun163.call(args161, kw162)?
                }
                .attr("translate")?;
                let mut args158 = Vec::new();
                let mut kw159 = Vec::new();
                args158.push(binary("add", e.get("c")?, {
                    let fun169 = e.get("up")?.attr("multiply")?;
                    let mut args167 = Vec::new();
                    let mut kw168 = Vec::new();
                    args167.push(e.get("up_leg")?);
                    fun169.call(args167, kw168)?
                })?);
                fun160.call(args158, kw159)?
            };
            e.set("stub", assigned157.clone())?;
            let assigned170 = {
                let fun173 = {
                    let fun176 = e.get("leg_up")?.attr("fuse")?;
                    let mut args174 = Vec::new();
                    let mut kw175 = Vec::new();
                    args174.push(e.get("leg_out")?);
                    fun176.call(args174, kw175)?
                }
                .attr("fuse")?;
                let mut args171 = Vec::new();
                let mut kw172 = Vec::new();
                args171.push(e.get("stub")?);
                fun173.call(args171, kw172)?
            };
            e.set("solid", assigned170.clone())?;
            let assigned177 = {
                let fun180 = {
                    let fun183 = e.get("_orient")?;
                    let mut args181 = Vec::new();
                    let mut kw182 = Vec::new();
                    args181.push({
                        let fun186 = e.get("_cyl")?;
                        let mut args184 = Vec::new();
                        let mut kw185 = Vec::new();
                        args184.push(binary("truediv", e.get("ELBOW_BORE")?, Val::Int(2i64))?);
                        args184.push(binary(
                            "add",
                            binary("add", e.get("up_leg")?, e.get("male_len")?)?,
                            Val::Int(1i64),
                        )?);
                        fun186.call(args184, kw185)?
                    });
                    args181.push(e.get("up")?);
                    fun183.call(args181, kw182)?
                }
                .attr("translate")?;
                let mut args178 = Vec::new();
                let mut kw179 = Vec::new();
                args178.push(e.get("c")?);
                fun180.call(args178, kw179)?
            };
            e.set("bore_up", assigned177.clone())?;
            let assigned187 = {
                let fun190 = {
                    let fun193 = e.get("_orient")?;
                    let mut args191 = Vec::new();
                    let mut kw192 = Vec::new();
                    args191.push({
                        let fun196 = e.get("_cyl")?;
                        let mut args194 = Vec::new();
                        let mut kw195 = Vec::new();
                        args194.push(binary("truediv", e.get("ELBOW_BORE")?, Val::Int(2i64))?);
                        args194.push(binary("add", e.get("out_leg")?, Val::Int(1i64))?);
                        fun196.call(args194, kw195)?
                    });
                    args191.push(e.get("out")?);
                    fun193.call(args191, kw192)?
                }
                .attr("translate")?;
                let mut args188 = Vec::new();
                let mut kw189 = Vec::new();
                args188.push(e.get("c")?);
                fun190.call(args188, kw189)?
            };
            e.set("bore_out", assigned187.clone())?;
            let assigned197 = {
                let fun200 = {
                    let fun203 = e.get("_orient")?;
                    let mut args201 = Vec::new();
                    let mut kw202 = Vec::new();
                    args201.push({
                        let fun206 = e.get("_cyl")?;
                        let mut args204 = Vec::new();
                        let mut kw205 = Vec::new();
                        args204.push(e.get("SOCKET_R")?);
                        args204.push({
                            let fun209 = e.get("min")?;
                            let mut args207 = Vec::new();
                            let mut kw208 = Vec::new();
                            args207.push(e.get("SOCKET_DEPTH")?);
                            args207.push(e.get("out_leg")?);
                            fun209.call(args207, kw208)?
                        });
                        fun206.call(args204, kw205)?
                    });
                    args201.push(e.get("out")?);
                    fun203.call(args201, kw202)?
                }
                .attr("translate")?;
                let mut args198 = Vec::new();
                let mut kw199 = Vec::new();
                args198.push(binary("add", e.get("c")?, {
                    let fun212 = e.get("out")?.attr("multiply")?;
                    let mut args210 = Vec::new();
                    let mut kw211 = Vec::new();
                    args210.push(binary("sub", e.get("out_leg")?, {
                        let fun215 = e.get("min")?;
                        let mut args213 = Vec::new();
                        let mut kw214 = Vec::new();
                        args213.push(e.get("SOCKET_DEPTH")?);
                        args213.push(e.get("out_leg")?);
                        fun215.call(args213, kw214)?
                    })?);
                    fun212.call(args210, kw211)?
                })?);
                fun200.call(args198, kw199)?
            };
            e.set("socket", assigned197.clone())?;
            let assigned216 = {
                let fun219 = {
                    let fun222 = {
                        let fun225 = e.get("solid")?.attr("cut")?;
                        let mut args223 = Vec::new();
                        let mut kw224 = Vec::new();
                        args223.push(e.get("bore_up")?);
                        fun225.call(args223, kw224)?
                    }
                    .attr("cut")?;
                    let mut args220 = Vec::new();
                    let mut kw221 = Vec::new();
                    args220.push(e.get("bore_out")?);
                    fun222.call(args220, kw221)?
                }
                .attr("cut")?;
                let mut args217 = Vec::new();
                let mut kw218 = Vec::new();
                args217.push(e.get("socket")?);
                fun219.call(args217, kw218)?
            };
            e.set("solid", assigned216.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("solid")?);
                s.push({
                    let fun228 = e.get("Mouth")?;
                    let mut args226 = Vec::new();
                    let mut kw227 = Vec::new();
                    args226.push({
                        let fun231 = e.get("tuple")?;
                        let mut args229 = Vec::new();
                        let mut kw230 = Vec::new();
                        args229.push(binary("add", e.get("c")?, {
                            let fun234 = e.get("out")?.attr("multiply")?;
                            let mut args232 = Vec::new();
                            let mut kw233 = Vec::new();
                            args232.push(e.get("out_leg")?);
                            fun234.call(args232, kw233)?
                        })?);
                        fun231.call(args229, kw230)?
                    });
                    args226.push({
                        let fun237 = e.get("tuple")?;
                        let mut args235 = Vec::new();
                        let mut kw236 = Vec::new();
                        args235.push(e.get("out")?);
                        fun237.call(args235, kw236)?
                    });
                    args226.push(e.get("ELBOW_BORE")?);
                    fun228.call(args226, kw227)?
                });
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    let assigned238 = binary("mul", Val::Float(0.52f64), e.get("IN")?)?;
    e.set("MALE_ELBOW_THREAD", assigned238.clone())?;
    let assigned239 = binary("mul", Val::Float(1.256f64), e.get("IN")?)?;
    e.set("MALE_ELBOW_HEIGHT", assigned239.clone())?;
    let assigned240 = binary("mul", Val::Float(0.61f64), e.get("IN")?)?;
    e.set("MALE_ELBOW_BODY_D", assigned240.clone())?;
    let assigned241 = binary("mul", Val::Float(1.063f64), e.get("IN")?)?;
    e.set("MALE_ELBOW_LENGTH", assigned241.clone())?;
    let assigned242 = binary("mul", Val::Float(0.4375f64), e.get("IN")?)?;
    e.set("MALE_ELBOW_POST_W", assigned242.clone())?;
    let assigned243 = binary("mul", Val::Float(0.665f64), e.get("IN")?)?;
    e.set("MALE_ELBOW_INSERTION", assigned243.clone())?;
    let assigned244 = Val::Float(4.3f64);
    e.set("MALE_ELBOW_FLOW_BORE", assigned244.clone())?;
    let assigned245 = binary("mul", Val::Float(0.25f64), e.get("IN")?)?;
    e.set("MALE_ELBOW_TUBE_OD", assigned245.clone())?;
    let assigned246 = binary(
        "sub",
        binary(
            "sub",
            e.get("MALE_ELBOW_HEIGHT")?,
            e.get("MALE_ELBOW_THREAD")?,
        )?,
        binary("truediv", e.get("MALE_ELBOW_BODY_D")?, Val::Int(2i64))?,
    )?;
    e.set("MALE_ELBOW_AXIS_REACH", assigned246.clone())?;
    let assigned247 = binary(
        "sub",
        e.get("MALE_ELBOW_LENGTH")?,
        binary("truediv", e.get("MALE_ELBOW_POST_W")?, Val::Int(2i64))?,
    )?;
    e.set("MALE_ELBOW_MOUTH_REACH", assigned247.clone())?;
    // male_elbow
    e.set("male_elbow", {
        let params = vec![
            ("corner".into(), None, true),
            ("up".into(), None, true),
            ("out".into(), None, true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned248 = {
                let fun251 = {
                    let fun254 = e.get("cq")?.attr("Vector")?;
                    let mut args252 = Vec::new();
                    let mut kw253 = Vec::new();
                    args252.extend(e.get("up")?.iter()?);
                    fun254.call(args252, kw253)?
                }
                .attr("normalized")?;
                let mut args249 = Vec::new();
                let mut kw250 = Vec::new();
                fun251.call(args249, kw250)?
            };
            e.set("up", assigned248.clone())?;
            let assigned255 = {
                let fun258 = {
                    let fun261 = e.get("cq")?.attr("Vector")?;
                    let mut args259 = Vec::new();
                    let mut kw260 = Vec::new();
                    args259.extend(e.get("out")?.iter()?);
                    fun261.call(args259, kw260)?
                }
                .attr("normalized")?;
                let mut args256 = Vec::new();
                let mut kw257 = Vec::new();
                fun258.call(args256, kw257)?
            };
            e.set("out", assigned255.clone())?;
            let assigned262 = {
                let fun265 = e.get("cq")?.attr("Vector")?;
                let mut args263 = Vec::new();
                let mut kw264 = Vec::new();
                args263.extend(e.get("corner")?.iter()?);
                fun265.call(args263, kw264)?
            };
            e.set("c", assigned262.clone())?;
            let assigned266 = binary("truediv", e.get("MALE_ELBOW_BODY_D")?, Val::Int(2i64))?;
            e.set("body_r", assigned266.clone())?;
            let assigned267 = {
                let fun270 = {
                    let fun273 = e.get("_orient")?;
                    let mut args271 = Vec::new();
                    let mut kw272 = Vec::new();
                    args271.push({
                        let fun276 = e.get("_cyl")?;
                        let mut args274 = Vec::new();
                        let mut kw275 = Vec::new();
                        args274.push(e.get("body_r")?);
                        args274.push(e.get("MALE_ELBOW_MOUTH_REACH")?);
                        fun276.call(args274, kw275)?
                    });
                    args271.push(e.get("out")?);
                    fun273.call(args271, kw272)?
                }
                .attr("translate")?;
                let mut args268 = Vec::new();
                let mut kw269 = Vec::new();
                args268.push(e.get("c")?);
                fun270.call(args268, kw269)?
            };
            e.set("socket_body", assigned267.clone())?;
            let assigned277 = {
                let fun280 = {
                    let fun283 = e.get("_orient")?;
                    let mut args281 = Vec::new();
                    let mut kw282 = Vec::new();
                    args281.push({
                        let fun286 = e.get("_cyl")?;
                        let mut args284 = Vec::new();
                        let mut kw285 = Vec::new();
                        args284.push(binary(
                            "truediv",
                            e.get("MALE_ELBOW_POST_W")?,
                            Val::Int(2i64),
                        )?);
                        args284.push(binary(
                            "add",
                            e.get("body_r")?,
                            e.get("MALE_ELBOW_AXIS_REACH")?,
                        )?);
                        fun286.call(args284, kw285)?
                    });
                    args281.push(e.get("up")?);
                    fun283.call(args281, kw282)?
                }
                .attr("translate")?;
                let mut args278 = Vec::new();
                let mut kw279 = Vec::new();
                args278.push(binary("sub", e.get("c")?, {
                    let fun289 = e.get("up")?.attr("multiply")?;
                    let mut args287 = Vec::new();
                    let mut kw288 = Vec::new();
                    args287.push(e.get("body_r")?);
                    fun289.call(args287, kw288)?
                })?);
                fun280.call(args278, kw279)?
            };
            e.set("post", assigned277.clone())?;
            let assigned290 = {
                let fun293 = {
                    let fun296 = e.get("_orient")?;
                    let mut args294 = Vec::new();
                    let mut kw295 = Vec::new();
                    args294.push({
                        let fun299 = e.get("_cyl")?;
                        let mut args297 = Vec::new();
                        let mut kw298 = Vec::new();
                        args297.push(e.get("ELBOW_MALE_R")?);
                        args297.push(e.get("MALE_ELBOW_THREAD")?);
                        fun299.call(args297, kw298)?
                    });
                    args294.push(e.get("up")?);
                    fun296.call(args294, kw295)?
                }
                .attr("translate")?;
                let mut args291 = Vec::new();
                let mut kw292 = Vec::new();
                args291.push(binary("add", e.get("c")?, {
                    let fun302 = e.get("up")?.attr("multiply")?;
                    let mut args300 = Vec::new();
                    let mut kw301 = Vec::new();
                    args300.push(e.get("MALE_ELBOW_AXIS_REACH")?);
                    fun302.call(args300, kw301)?
                })?);
                fun293.call(args291, kw292)?
            };
            e.set("thread", assigned290.clone())?;
            let assigned303 = {
                let fun306 = {
                    let fun309 = e.get("socket_body")?.attr("fuse")?;
                    let mut args307 = Vec::new();
                    let mut kw308 = Vec::new();
                    args307.push(e.get("post")?);
                    fun309.call(args307, kw308)?
                }
                .attr("fuse")?;
                let mut args304 = Vec::new();
                let mut kw305 = Vec::new();
                args304.push(e.get("thread")?);
                fun306.call(args304, kw305)?
            };
            e.set("solid", assigned303.clone())?;
            let assigned310 = binary("add", e.get("c")?, {
                let fun313 = e.get("out")?.attr("multiply")?;
                let mut args311 = Vec::new();
                let mut kw312 = Vec::new();
                args311.push(e.get("MALE_ELBOW_MOUTH_REACH")?);
                fun313.call(args311, kw312)?
            })?;
            e.set("mouth", assigned310.clone())?;
            let assigned314 = {
                let fun317 = {
                    let fun320 = e.get("_orient")?;
                    let mut args318 = Vec::new();
                    let mut kw319 = Vec::new();
                    args318.push({
                        let fun323 = e.get("_cyl")?;
                        let mut args321 = Vec::new();
                        let mut kw322 = Vec::new();
                        args321.push(binary(
                            "truediv",
                            e.get("MALE_ELBOW_TUBE_OD")?,
                            Val::Int(2i64),
                        )?);
                        args321.push(e.get("MALE_ELBOW_INSERTION")?);
                        fun323.call(args321, kw322)?
                    });
                    args318.push(e.get("out")?);
                    fun320.call(args318, kw319)?
                }
                .attr("translate")?;
                let mut args315 = Vec::new();
                let mut kw316 = Vec::new();
                args315.push(binary("sub", e.get("mouth")?, {
                    let fun326 = e.get("out")?.attr("multiply")?;
                    let mut args324 = Vec::new();
                    let mut kw325 = Vec::new();
                    args324.push(e.get("MALE_ELBOW_INSERTION")?);
                    fun326.call(args324, kw325)?
                })?);
                fun317.call(args315, kw316)?
            };
            e.set("socket", assigned314.clone())?;
            let assigned327 = {
                let fun330 = {
                    let fun333 = e.get("_orient")?;
                    let mut args331 = Vec::new();
                    let mut kw332 = Vec::new();
                    args331.push({
                        let fun336 = e.get("_cyl")?;
                        let mut args334 = Vec::new();
                        let mut kw335 = Vec::new();
                        args334.push(binary(
                            "truediv",
                            e.get("MALE_ELBOW_FLOW_BORE")?,
                            Val::Int(2i64),
                        )?);
                        args334.push(e.get("MALE_ELBOW_MOUTH_REACH")?);
                        fun336.call(args334, kw335)?
                    });
                    args331.push(e.get("out")?);
                    fun333.call(args331, kw332)?
                }
                .attr("translate")?;
                let mut args328 = Vec::new();
                let mut kw329 = Vec::new();
                args328.push(e.get("c")?);
                fun330.call(args328, kw329)?
            };
            e.set("bore_out", assigned327.clone())?;
            let assigned337 = {
                let fun340 = {
                    let fun343 = e.get("_orient")?;
                    let mut args341 = Vec::new();
                    let mut kw342 = Vec::new();
                    args341.push({
                        let fun346 = e.get("_cyl")?;
                        let mut args344 = Vec::new();
                        let mut kw345 = Vec::new();
                        args344.push(binary(
                            "truediv",
                            e.get("MALE_ELBOW_FLOW_BORE")?,
                            Val::Int(2i64),
                        )?);
                        args344.push(binary(
                            "add",
                            binary(
                                "add",
                                e.get("MALE_ELBOW_AXIS_REACH")?,
                                e.get("MALE_ELBOW_THREAD")?,
                            )?,
                            Val::Int(1i64),
                        )?);
                        fun346.call(args344, kw345)?
                    });
                    args341.push(e.get("up")?);
                    fun343.call(args341, kw342)?
                }
                .attr("translate")?;
                let mut args338 = Vec::new();
                let mut kw339 = Vec::new();
                args338.push(e.get("c")?);
                fun340.call(args338, kw339)?
            };
            e.set("bore_up", assigned337.clone())?;
            let assigned347 = {
                let fun350 = {
                    let fun353 = {
                        let fun356 = e.get("solid")?.attr("cut")?;
                        let mut args354 = Vec::new();
                        let mut kw355 = Vec::new();
                        args354.push(e.get("socket")?);
                        fun356.call(args354, kw355)?
                    }
                    .attr("cut")?;
                    let mut args351 = Vec::new();
                    let mut kw352 = Vec::new();
                    args351.push(e.get("bore_out")?);
                    fun353.call(args351, kw352)?
                }
                .attr("cut")?;
                let mut args348 = Vec::new();
                let mut kw349 = Vec::new();
                args348.push(e.get("bore_up")?);
                fun350.call(args348, kw349)?
            };
            e.set("solid", assigned347.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("solid")?);
                s.push({
                    let fun359 = e.get("Mouth")?;
                    let mut args357 = Vec::new();
                    let mut kw358 = Vec::new();
                    args357.push({
                        let fun362 = e.get("tuple")?;
                        let mut args360 = Vec::new();
                        let mut kw361 = Vec::new();
                        args360.push(e.get("mouth")?);
                        fun362.call(args360, kw361)?
                    });
                    args357.push({
                        let fun365 = e.get("tuple")?;
                        let mut args363 = Vec::new();
                        let mut kw364 = Vec::new();
                        args363.push(e.get("out")?);
                        fun365.call(args363, kw364)?
                    });
                    args357.push(e.get("MALE_ELBOW_TUBE_OD")?);
                    fun359.call(args357, kw358)?
                });
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    let assigned366 = binary("mul", Val::Float(0.5625f64), e.get("IN")?)?;
    e.set("PRV_HEX_AF", assigned366.clone())?;
    let assigned367 = binary("mul", Val::Float(0.44f64), e.get("IN")?)?;
    e.set("PRV_HEX_H", assigned367.clone())?;
    let assigned368 = binary(
        "mul",
        binary("mul", Val::Float(0.5f64), Val::Float(0.62f64))?,
        e.get("IN")?,
    )?;
    e.set("PRV_CAP_R", assigned368.clone())?;
    let assigned369 = binary("mul", Val::Float(1.06f64), e.get("IN")?)?;
    e.set("PRV_CAP_H", assigned369.clone())?;
    let assigned370 = binary("mul", Val::Float(0.5f64), e.get("IN")?)?;
    e.set("PRV_MALE_LEN", assigned370.clone())?;
    // sv125
    e.set("sv125", {
        let params = vec![("at".into(), None, true), ("axis".into(), None, true)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned371 = {
                let fun374 = {
                    let fun377 = e.get("cq")?.attr("Vector")?;
                    let mut args375 = Vec::new();
                    let mut kw376 = Vec::new();
                    args375.extend(e.get("axis")?.iter()?);
                    fun377.call(args375, kw376)?
                }
                .attr("normalized")?;
                let mut args372 = Vec::new();
                let mut kw373 = Vec::new();
                fun374.call(args372, kw373)?
            };
            e.set("axis", assigned371.clone())?;
            let assigned378 = {
                let fun381 = e.get("cq")?.attr("Vector")?;
                let mut args379 = Vec::new();
                let mut kw380 = Vec::new();
                args379.extend(e.get("at")?.iter()?);
                fun381.call(args379, kw380)?
            };
            e.set("base", assigned378.clone())?;
            let assigned382 = {
                let fun385 = {
                    let fun388 = e.get("_orient")?;
                    let mut args386 = Vec::new();
                    let mut kw387 = Vec::new();
                    args386.push({
                        let fun391 = e.get("_cyl")?;
                        let mut args389 = Vec::new();
                        let mut kw390 = Vec::new();
                        args389.push(e.get("ELBOW_MALE_R")?);
                        args389.push(e.get("PRV_MALE_LEN")?);
                        fun391.call(args389, kw390)?
                    });
                    args386.push(e.get("axis")?);
                    fun388.call(args386, kw387)?
                }
                .attr("translate")?;
                let mut args383 = Vec::new();
                let mut kw384 = Vec::new();
                args383.push(binary("sub", e.get("base")?, {
                    let fun394 = e.get("axis")?.attr("multiply")?;
                    let mut args392 = Vec::new();
                    let mut kw393 = Vec::new();
                    args392.push(e.get("PRV_MALE_LEN")?);
                    fun394.call(args392, kw393)?
                })?);
                fun385.call(args383, kw384)?
            };
            e.set("stub", assigned382.clone())?;
            let assigned395 = {
                let fun398 = {
                    let fun401 = e.get("_orient")?;
                    let mut args399 = Vec::new();
                    let mut kw400 = Vec::new();
                    args399.push({
                        let fun404 = e.get("_hex")?;
                        let mut args402 = Vec::new();
                        let mut kw403 = Vec::new();
                        args402.push(e.get("PRV_HEX_AF")?);
                        args402.push(e.get("PRV_HEX_H")?);
                        fun404.call(args402, kw403)?
                    });
                    args399.push(e.get("axis")?);
                    fun401.call(args399, kw400)?
                }
                .attr("translate")?;
                let mut args396 = Vec::new();
                let mut kw397 = Vec::new();
                args396.push(e.get("base")?);
                fun398.call(args396, kw397)?
            };
            e.set("hexb", assigned395.clone())?;
            let assigned405 = {
                let fun408 = {
                    let fun411 = e.get("_orient")?;
                    let mut args409 = Vec::new();
                    let mut kw410 = Vec::new();
                    args409.push({
                        let fun414 = e.get("_cyl")?;
                        let mut args412 = Vec::new();
                        let mut kw413 = Vec::new();
                        args412.push(e.get("PRV_CAP_R")?);
                        args412.push(e.get("PRV_CAP_H")?);
                        fun414.call(args412, kw413)?
                    });
                    args409.push(e.get("axis")?);
                    fun411.call(args409, kw410)?
                }
                .attr("translate")?;
                let mut args406 = Vec::new();
                let mut kw407 = Vec::new();
                args406.push(binary("add", e.get("base")?, {
                    let fun417 = e.get("axis")?.attr("multiply")?;
                    let mut args415 = Vec::new();
                    let mut kw416 = Vec::new();
                    args415.push(e.get("PRV_HEX_H")?);
                    fun417.call(args415, kw416)?
                })?);
                fun408.call(args406, kw407)?
            };
            e.set("cap", assigned405.clone())?;
            return Ok({
                let fun420 = {
                    let fun423 = e.get("stub")?.attr("fuse")?;
                    let mut args421 = Vec::new();
                    let mut kw422 = Vec::new();
                    args421.push(e.get("hexb")?);
                    fun423.call(args421, kw422)?
                }
                .attr("fuse")?;
                let mut args418 = Vec::new();
                let mut kw419 = Vec::new();
                args418.push(e.get("cap")?);
                fun420.call(args418, kw419)?
            });
            Ok(Val::None)
        })
    })?;
    // sv125_reach
    e.set("sv125_reach", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary("add", e.get("PRV_HEX_H")?, e.get("PRV_CAP_H")?)?);
            Ok(Val::None)
        })
    })?;
    e.set("_float", rt.import_module("_float_interface")?)?;
    let assigned424 = e.get("_float")?.attr("diameter")?;
    e.set("FLOAT_OD", assigned424.clone())?;
    let assigned425 = e.get("_float")?.attr("height")?;
    e.set("FLOAT_H", assigned425.clone())?;
    let assigned426 = e.get("_float")?.attr("bore_diameter")?;
    e.set("FLOAT_BORE", assigned426.clone())?;
    // float_capsule
    e.set("float_capsule", {
        let params = vec![
            ("centre".into(), None, true),
            (
                "axis".into(),
                Some({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(1i64));
                    Val::tuple(s)
                }),
                true,
            ),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned427 = {
                let fun430 = {
                    let fun433 = e.get("cq")?.attr("Vector")?;
                    let mut args431 = Vec::new();
                    let mut kw432 = Vec::new();
                    args431.extend(e.get("axis")?.iter()?);
                    fun433.call(args431, kw432)?
                }
                .attr("normalized")?;
                let mut args428 = Vec::new();
                let mut kw429 = Vec::new();
                fun430.call(args428, kw429)?
            };
            e.set("axis", assigned427.clone())?;
            let assigned434 = {
                let fun437 = e.get("cq")?.attr("Vector")?;
                let mut args435 = Vec::new();
                let mut kw436 = Vec::new();
                args435.extend(e.get("centre")?.iter()?);
                fun437.call(args435, kw436)?
            };
            e.set("c", assigned434.clone())?;
            let assigned438 = {
                let fun441 = {
                    let fun444 = e.get("_orient")?;
                    let mut args442 = Vec::new();
                    let mut kw443 = Vec::new();
                    args442.push({
                        let fun447 = e.get("_cyl")?;
                        let mut args445 = Vec::new();
                        let mut kw446 = Vec::new();
                        args445.push(binary("truediv", e.get("FLOAT_OD")?, Val::Int(2i64))?);
                        args445.push(e.get("FLOAT_H")?);
                        fun447.call(args445, kw446)?
                    });
                    args442.push(e.get("axis")?);
                    fun444.call(args442, kw443)?
                }
                .attr("translate")?;
                let mut args439 = Vec::new();
                let mut kw440 = Vec::new();
                args439.push(binary("sub", e.get("c")?, {
                    let fun450 = e.get("axis")?.attr("multiply")?;
                    let mut args448 = Vec::new();
                    let mut kw449 = Vec::new();
                    args448.push(binary("truediv", e.get("FLOAT_H")?, Val::Int(2i64))?);
                    fun450.call(args448, kw449)?
                })?);
                fun441.call(args439, kw440)?
            };
            e.set("body", assigned438.clone())?;
            let assigned451 = {
                let fun454 = {
                    let fun457 = e.get("_orient")?;
                    let mut args455 = Vec::new();
                    let mut kw456 = Vec::new();
                    args455.push({
                        let fun460 = e.get("_cyl")?;
                        let mut args458 = Vec::new();
                        let mut kw459 = Vec::new();
                        args458.push(binary("truediv", e.get("FLOAT_BORE")?, Val::Int(2i64))?);
                        args458.push(binary("add", e.get("FLOAT_H")?, Val::Int(2i64))?);
                        fun460.call(args458, kw459)?
                    });
                    args455.push(e.get("axis")?);
                    fun457.call(args455, kw456)?
                }
                .attr("translate")?;
                let mut args452 = Vec::new();
                let mut kw453 = Vec::new();
                args452.push(binary("sub", e.get("c")?, {
                    let fun463 = e.get("axis")?.attr("multiply")?;
                    let mut args461 = Vec::new();
                    let mut kw462 = Vec::new();
                    args461.push(binary(
                        "add",
                        binary("truediv", e.get("FLOAT_H")?, Val::Int(2i64))?,
                        Val::Int(1i64),
                    )?);
                    fun463.call(args461, kw462)?
                })?);
                fun454.call(args452, kw453)?
            };
            e.set("bore", assigned451.clone())?;
            let assigned464 = {
                let fun467 = {
                    let fun470 = e.get("_cyl")?;
                    let mut args468 = Vec::new();
                    let mut kw469 = Vec::new();
                    args468.push(binary(
                        "truediv",
                        e.get("_float")?.attr("pocket_od")?,
                        Val::Int(2i64),
                    )?);
                    args468.push(e.get("_float")?.attr("pocket_depth")?);
                    fun470.call(args468, kw469)?
                }
                .attr("cut")?;
                let mut args465 = Vec::new();
                let mut kw466 = Vec::new();
                args465.push({
                    let fun473 = e.get("_cyl")?;
                    let mut args471 = Vec::new();
                    let mut kw472 = Vec::new();
                    args471.push(binary(
                        "truediv",
                        e.get("_float")?.attr("pocket_id")?,
                        Val::Int(2i64),
                    )?);
                    args471.push(e.get("_float")?.attr("pocket_depth")?);
                    fun473.call(args471, kw472)?
                });
                fun467.call(args465, kw466)?
            };
            e.set("pocket", assigned464.clone())?;
            let assigned474 = {
                let fun477 = {
                    let fun480 = e.get("_orient")?;
                    let mut args478 = Vec::new();
                    let mut kw479 = Vec::new();
                    args478.push(e.get("pocket")?);
                    args478.push(e.get("axis")?);
                    fun480.call(args478, kw479)?
                }
                .attr("translate")?;
                let mut args475 = Vec::new();
                let mut kw476 = Vec::new();
                args475.push(binary("add", e.get("c")?, {
                    let fun483 = e.get("axis")?.attr("multiply")?;
                    let mut args481 = Vec::new();
                    let mut kw482 = Vec::new();
                    args481.push(binary(
                        "sub",
                        e.get("_float")?.attr("magnet_seat")?,
                        binary("truediv", e.get("FLOAT_H")?, Val::Int(2i64))?,
                    )?);
                    fun483.call(args481, kw482)?
                })?);
                fun477.call(args475, kw476)?
            };
            e.set("pocket", assigned474.clone())?;
            let assigned484 = {
                let fun487 = {
                    let fun490 = e.get("_cyl")?;
                    let mut args488 = Vec::new();
                    let mut kw489 = Vec::new();
                    args488.push(binary(
                        "truediv",
                        e.get("_float")?.attr("magnet_od")?,
                        Val::Int(2i64),
                    )?);
                    args488.push(e.get("_float")?.attr("magnet_thickness")?);
                    fun490.call(args488, kw489)?
                }
                .attr("cut")?;
                let mut args485 = Vec::new();
                let mut kw486 = Vec::new();
                args485.push({
                    let fun493 = e.get("_cyl")?;
                    let mut args491 = Vec::new();
                    let mut kw492 = Vec::new();
                    args491.push(binary(
                        "truediv",
                        e.get("_float")?.attr("magnet_id")?,
                        Val::Int(2i64),
                    )?);
                    args491.push(e.get("_float")?.attr("magnet_thickness")?);
                    fun493.call(args491, kw492)?
                });
                fun487.call(args485, kw486)?
            };
            e.set("magnet", assigned484.clone())?;
            let assigned494 = {
                let fun497 = {
                    let fun500 = e.get("_orient")?;
                    let mut args498 = Vec::new();
                    let mut kw499 = Vec::new();
                    args498.push(e.get("magnet")?);
                    args498.push(e.get("axis")?);
                    fun500.call(args498, kw499)?
                }
                .attr("translate")?;
                let mut args495 = Vec::new();
                let mut kw496 = Vec::new();
                args495.push(binary("add", e.get("c")?, {
                    let fun503 = e.get("axis")?.attr("multiply")?;
                    let mut args501 = Vec::new();
                    let mut kw502 = Vec::new();
                    args501.push(binary(
                        "sub",
                        e.get("_float")?.attr("magnet_seat")?,
                        binary("truediv", e.get("FLOAT_H")?, Val::Int(2i64))?,
                    )?);
                    fun503.call(args501, kw502)?
                })?);
                fun497.call(args495, kw496)?
            };
            e.set("magnet", assigned494.clone())?;
            return Ok({
                let fun506 = e.get("cq")?.attr("Compound")?.attr("makeCompound")?;
                let mut args504 = Vec::new();
                let mut kw505 = Vec::new();
                args504.push({
                    let mut s = Vec::new();
                    s.push({
                        let fun509 = {
                            let fun512 = e.get("body")?.attr("cut")?;
                            let mut args510 = Vec::new();
                            let mut kw511 = Vec::new();
                            args510.push(e.get("bore")?);
                            fun512.call(args510, kw511)?
                        }
                        .attr("cut")?;
                        let mut args507 = Vec::new();
                        let mut kw508 = Vec::new();
                        args507.push(e.get("pocket")?);
                        fun509.call(args507, kw508)?
                    });
                    s.push(e.get("magnet")?);
                    Val::list(s)
                });
                fun506.call(args504, kw505)?
            });
            Ok(Val::None)
        })
    })?;
    let assigned513 = Val::Float(14.0f64);
    e.set("REED_GLASS_LEN", assigned513.clone())?;
    let assigned514 = Val::Float(1.25f64);
    e.set("REED_GLASS_R", assigned514.clone())?;
    // reed
    e.set("reed", {
        let params = vec![
            ("centre".into(), None, true),
            (
                "axis".into(),
                Some({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(1i64));
                    Val::tuple(s)
                }),
                true,
            ),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned515 = {
                let fun518 = {
                    let fun521 = e.get("cq")?.attr("Vector")?;
                    let mut args519 = Vec::new();
                    let mut kw520 = Vec::new();
                    args519.extend(e.get("axis")?.iter()?);
                    fun521.call(args519, kw520)?
                }
                .attr("normalized")?;
                let mut args516 = Vec::new();
                let mut kw517 = Vec::new();
                fun518.call(args516, kw517)?
            };
            e.set("axis", assigned515.clone())?;
            let assigned522 = {
                let fun525 = e.get("cq")?.attr("Vector")?;
                let mut args523 = Vec::new();
                let mut kw524 = Vec::new();
                args523.extend(e.get("centre")?.iter()?);
                fun525.call(args523, kw524)?
            };
            e.set("c", assigned522.clone())?;
            return Ok({
                let fun528 = {
                    let fun531 = e.get("_orient")?;
                    let mut args529 = Vec::new();
                    let mut kw530 = Vec::new();
                    args529.push({
                        let fun534 = e.get("_cyl")?;
                        let mut args532 = Vec::new();
                        let mut kw533 = Vec::new();
                        args532.push(e.get("REED_GLASS_R")?);
                        args532.push(e.get("REED_GLASS_LEN")?);
                        fun534.call(args532, kw533)?
                    });
                    args529.push(e.get("axis")?);
                    fun531.call(args529, kw530)?
                }
                .attr("translate")?;
                let mut args526 = Vec::new();
                let mut kw527 = Vec::new();
                args526.push(binary("sub", e.get("c")?, {
                    let fun537 = e.get("axis")?.attr("multiply")?;
                    let mut args535 = Vec::new();
                    let mut kw536 = Vec::new();
                    args535.push(binary("truediv", e.get("REED_GLASS_LEN")?, Val::Int(2i64))?);
                    fun537.call(args535, kw536)?
                })?);
                fun528.call(args526, kw527)?
            });
            Ok(Val::None)
        })
    })?;
    let assigned538 = Val::Float(4.3f64);
    e.set("TO92_W", assigned538.clone())?;
    let assigned539 = Val::Float(5.2f64);
    e.set("TO92_H", assigned539.clone())?;
    let assigned540 = Val::Float(1.2f64);
    e.set("TO92_CORNER_R", assigned540.clone())?;
    // to92
    e.set("to92", {
        let params = vec![
            ("centre".into(), None, true),
            (
                "axis".into(),
                Some({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(1i64));
                    Val::tuple(s)
                }),
                true,
            ),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned541 = {
                let fun544 = {
                    let fun547 = e.get("cq")?.attr("Vector")?;
                    let mut args545 = Vec::new();
                    let mut kw546 = Vec::new();
                    args545.extend(e.get("axis")?.iter()?);
                    fun547.call(args545, kw546)?
                }
                .attr("normalized")?;
                let mut args542 = Vec::new();
                let mut kw543 = Vec::new();
                fun544.call(args542, kw543)?
            };
            e.set("axis", assigned541.clone())?;
            let assigned548 = {
                let fun551 = e.get("cq")?.attr("Vector")?;
                let mut args549 = Vec::new();
                let mut kw550 = Vec::new();
                args549.extend(e.get("centre")?.iter()?);
                fun551.call(args549, kw550)?
            };
            e.set("c", assigned548.clone())?;
            let assigned552 = {
                let fun555 = {
                    let fun558 = {
                        let fun561 = {
                            let fun564 = {
                                let fun567 = {
                                    let fun570 = e.get("cq")?.attr("Workplane")?;
                                    let mut args568 = Vec::new();
                                    let mut kw569 = Vec::new();
                                    args568.push(Val::Str("XY".into()));
                                    fun570.call(args568, kw569)?
                                }
                                .attr("rect")?;
                                let mut args565 = Vec::new();
                                let mut kw566 = Vec::new();
                                args565.push(e.get("TO92_W")?);
                                args565.push(e.get("TO92_W")?);
                                fun567.call(args565, kw566)?
                            }
                            .attr("extrude")?;
                            let mut args562 = Vec::new();
                            let mut kw563 = Vec::new();
                            args562.push(e.get("TO92_H")?);
                            fun564.call(args562, kw563)?
                        }
                        .attr("edges")?;
                        let mut args559 = Vec::new();
                        let mut kw560 = Vec::new();
                        args559.push(Val::Str("|Z".into()));
                        fun561.call(args559, kw560)?
                    }
                    .attr("fillet")?;
                    let mut args556 = Vec::new();
                    let mut kw557 = Vec::new();
                    args556.push(e.get("TO92_CORNER_R")?);
                    fun558.call(args556, kw557)?
                }
                .attr("val")?;
                let mut args553 = Vec::new();
                let mut kw554 = Vec::new();
                fun555.call(args553, kw554)?
            };
            e.set("body", assigned552.clone())?;
            return Ok({
                let fun573 = {
                    let fun576 = e.get("_orient")?;
                    let mut args574 = Vec::new();
                    let mut kw575 = Vec::new();
                    args574.push(e.get("body")?);
                    args574.push(e.get("axis")?);
                    fun576.call(args574, kw575)?
                }
                .attr("translate")?;
                let mut args571 = Vec::new();
                let mut kw572 = Vec::new();
                args571.push(binary("sub", e.get("c")?, {
                    let fun579 = e.get("axis")?.attr("multiply")?;
                    let mut args577 = Vec::new();
                    let mut kw578 = Vec::new();
                    args577.push(binary("truediv", e.get("TO92_H")?, Val::Int(2i64))?);
                    fun579.call(args577, kw578)?
                })?);
                fun573.call(args571, kw572)?
            });
            Ok(Val::None)
        })
    })?;
    // stand_x_along
    e.set("stand_x_along", {
        let params = vec![
            ("solid".into(), None, false),
            ("at".into(), None, true),
            ("axis".into(), None, true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned580 = {
                let fun583 = {
                    let fun586 = e.get("cq")?.attr("Vector")?;
                    let mut args584 = Vec::new();
                    let mut kw585 = Vec::new();
                    args584.extend(e.get("axis")?.iter()?);
                    fun586.call(args584, kw585)?
                }
                .attr("normalized")?;
                let mut args581 = Vec::new();
                let mut kw582 = Vec::new();
                fun583.call(args581, kw582)?
            };
            e.set("a", assigned580.clone())?;
            let assigned587 = {
                let fun590 = e.get("cq")?.attr("Vector")?;
                let mut args588 = Vec::new();
                let mut kw589 = Vec::new();
                args588.push(Val::Int(1i64));
                args588.push(Val::Int(0i64));
                args588.push(Val::Int(0i64));
                fun590.call(args588, kw589)?
            };
            e.set("x", assigned587.clone())?;
            let assigned591 = {
                let fun594 = e.get("max")?;
                let mut args592 = Vec::new();
                let mut kw593 = Vec::new();
                args592.push(unary("neg", Val::Float(1.0f64))?);
                args592.push({
                    let fun597 = e.get("min")?;
                    let mut args595 = Vec::new();
                    let mut kw596 = Vec::new();
                    args595.push(Val::Float(1.0f64));
                    args595.push({
                        let fun600 = e.get("x")?.attr("dot")?;
                        let mut args598 = Vec::new();
                        let mut kw599 = Vec::new();
                        args598.push(e.get("a")?);
                        fun600.call(args598, kw599)?
                    });
                    fun597.call(args595, kw596)?
                });
                fun594.call(args592, kw593)?
            };
            e.set("dot", assigned591.clone())?;
            if {
                let v601 = e.get("dot")?;
                let v602 = binary("sub", Val::Int(1i64), Val::Float(1e-12f64))?;
                Val::Bool(compare("gt", v601.clone(), v602.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned603 = e.get("solid")?;
                e.set("turned", assigned603.clone())?;
            } else {
                if {
                    let v604 = e.get("dot")?;
                    let v605 = binary("add", unary("neg", Val::Int(1i64))?, Val::Float(1e-12f64))?;
                    Val::Bool(compare("lt", v604.clone(), v605.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned606 = {
                        let fun609 = e.get("solid")?.attr("rotate")?;
                        let mut args607 = Vec::new();
                        let mut kw608 = Vec::new();
                        args607.push({
                            let fun612 = e.get("cq")?.attr("Vector")?;
                            let mut args610 = Vec::new();
                            let mut kw611 = Vec::new();
                            args610.push(Val::Int(0i64));
                            args610.push(Val::Int(0i64));
                            args610.push(Val::Int(0i64));
                            fun612.call(args610, kw611)?
                        });
                        args607.push({
                            let fun615 = e.get("cq")?.attr("Vector")?;
                            let mut args613 = Vec::new();
                            let mut kw614 = Vec::new();
                            args613.push(Val::Int(0i64));
                            args613.push(Val::Int(0i64));
                            args613.push(Val::Int(1i64));
                            fun615.call(args613, kw614)?
                        });
                        args607.push(Val::Int(180i64));
                        fun609.call(args607, kw608)?
                    };
                    e.set("turned", assigned606.clone())?;
                } else {
                    let assigned616 = {
                        let fun619 = e.get("solid")?.attr("rotate")?;
                        let mut args617 = Vec::new();
                        let mut kw618 = Vec::new();
                        args617.push({
                            let fun622 = e.get("cq")?.attr("Vector")?;
                            let mut args620 = Vec::new();
                            let mut kw621 = Vec::new();
                            args620.push(Val::Int(0i64));
                            args620.push(Val::Int(0i64));
                            args620.push(Val::Int(0i64));
                            fun622.call(args620, kw621)?
                        });
                        args617.push({
                            let fun625 = e.get("x")?.attr("cross")?;
                            let mut args623 = Vec::new();
                            let mut kw624 = Vec::new();
                            args623.push(e.get("a")?);
                            fun625.call(args623, kw624)?
                        });
                        args617.push({
                            let fun628 = e.get("math")?.attr("degrees")?;
                            let mut args626 = Vec::new();
                            let mut kw627 = Vec::new();
                            args626.push({
                                let fun631 = e.get("math")?.attr("acos")?;
                                let mut args629 = Vec::new();
                                let mut kw630 = Vec::new();
                                args629.push(e.get("dot")?);
                                fun631.call(args629, kw630)?
                            });
                            fun628.call(args626, kw627)?
                        });
                        fun619.call(args617, kw618)?
                    };
                    e.set("turned", assigned616.clone())?;
                }
            }
            return Ok({
                let fun634 = e.get("turned")?.attr("translate")?;
                let mut args632 = Vec::new();
                let mut kw633 = Vec::new();
                args632.push({
                    let fun637 = e.get("cq")?.attr("Vector")?;
                    let mut args635 = Vec::new();
                    let mut kw636 = Vec::new();
                    args635.extend(e.get("at")?.iter()?);
                    fun637.call(args635, kw636)?
                });
                fun634.call(args632, kw633)?
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
