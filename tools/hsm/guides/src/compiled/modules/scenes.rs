//! Guide recipe: `tools/install-guide/scenes.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    rt.import_module("importlib.util")?;
    e.set("importlib", rt.import_module("importlib")?)?;
    e.set("json", rt.import_module("json")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
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
    }
    .attr("parents")?
    .get(Val::Int(2i64))?;
    e.set("ROOT", assigned2.clone())?;
    let assigned9 = binary("truediv", e.get("ROOT")?, Val::Str("hardware".into()))?;
    e.set("HARDWARE", assigned9.clone())?;
    let assigned10 = binary(
        "truediv",
        e.get("HARDWARE")?,
        Val::Str("install-guide/out".into()),
    )?;
    e.set("OUT", assigned10.clone())?;
    let assigned11 = binary(
        "truediv",
        e.get("HARDWARE")?,
        Val::Str("install-guide/art".into()),
    )?;
    e.set("ART", assigned11.clone())?;
    let assigned12 = {
        let mut s = Vec::new();
        s.push({
            let fun15 = e.get("str")?;
            let mut args13 = Vec::new();
            let mut kw14 = Vec::new();
            args13.push(binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("install-guide".into()),
            )?);
            fun15.call(args13, kw14)?
        });
        s.push({
            let fun18 = e.get("str")?;
            let mut args16 = Vec::new();
            let mut kw17 = Vec::new();
            args16.push(binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("scripts".into()),
            )?);
            fun18.call(args16, kw17)?
        });
        Val::list(s)
    };
    e.get("sys")?.attr("path")?.set(
        Val::Slice {
            start: None,
            stop: Some(Val::Int(0i64).integer()?),
            step: 1,
        },
        assigned12.clone(),
    )?;
    e.set("cq", rt.import_module("cadquery")?)?;
    e.set("install", rt.import_module("_install_art")?)?;
    e.set("original", rt.import_module("_cad_art")?)?;
    e.set("_hsm_render", rt.import_module("_hsm_render")?)?;
    // load
    e.set("load", {
        let params = vec![("path".into(), None, false), ("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned19 = {
                let fun22 = e
                    .get("importlib")?
                    .attr("util")?
                    .attr("spec_from_file_location")?;
                let mut args20 = Vec::new();
                let mut kw21 = Vec::new();
                args20.push(e.get("name")?);
                args20.push(e.get("path")?);
                fun22.call(args20, kw21)?
            };
            e.set("spec", assigned19.clone())?;
            let assigned23 = {
                let fun26 = e.get("importlib")?.attr("util")?.attr("module_from_spec")?;
                let mut args24 = Vec::new();
                let mut kw25 = Vec::new();
                args24.push(e.get("spec")?);
                fun26.call(args24, kw25)?
            };
            e.set("module", assigned23.clone())?;
            {
                let fun29 = e.get("spec")?.attr("loader")?.attr("exec_module")?;
                let mut args27 = Vec::new();
                let mut kw28 = Vec::new();
                args27.push(e.get("module")?);
                fun29.call(args27, kw28)?
            };
            return Ok(e.get("module")?);
            Ok(Val::None)
        })
    })?;
    let assigned30 = {
        let fun33 = e.get("load")?;
        let mut args31 = Vec::new();
        let mut kw32 = Vec::new();
        args31.push(binary(
            "truediv",
            e.get("HARDWARE")?,
            Val::Str("reference/taprite-3741-regulator/taprite_3741_regulator.py".into()),
        )?);
        args31.push(Val::Str("installation_regulator".into()));
        fun33.call(args31, kw32)?
    };
    e.set("reg", assigned30.clone())?;
    let assigned34 = {
        let fun37 = e.get("cq")?.attr("Color")?;
        let mut args35 = Vec::new();
        let mut kw36 = Vec::new();
        args35.push(Val::Float(0.63f64));
        args35.push(Val::Float(0.66f64));
        args35.push(Val::Float(0.7f64));
        fun37.call(args35, kw36)?
    };
    e.set("SILVER", assigned34.clone())?;
    let assigned38 = {
        let fun41 = e.get("cq")?.attr("Color")?;
        let mut args39 = Vec::new();
        let mut kw40 = Vec::new();
        args39.push(Val::Float(0.07f64));
        args39.push(Val::Float(0.075f64));
        args39.push(Val::Float(0.085f64));
        fun41.call(args39, kw40)?
    };
    e.set("BLACK", assigned38.clone())?;
    let assigned42 = {
        let fun45 = e.get("cq")?.attr("Color")?;
        let mut args43 = Vec::new();
        let mut kw44 = Vec::new();
        args43.push(Val::Float(0.58f64));
        args43.push(Val::Float(0.7f64));
        args43.push(Val::Float(0.74f64));
        args43.push(Val::Float(0.3f64));
        fun45.call(args43, kw44)?
    };
    e.set("GLASS", assigned42.clone())?;
    let assigned46 = {
        let fun49 = e.get("cq")?.attr("Color")?;
        let mut args47 = Vec::new();
        let mut kw48 = Vec::new();
        args47.push(Val::Float(0.2f64));
        args47.push(Val::Float(0.07f64));
        args47.push(Val::Float(0.025f64));
        args47.push(Val::Float(1.0f64));
        fun49.call(args47, kw48)?
    };
    e.set("DRINK", assigned46.clone())?;
    let assigned50 = {
        let mut s = Vec::new();
        Val::list(s)
    };
    e.set("jobs", assigned50.clone())?;
    // stage
    e.set("stage", {
        let params = vec![
            ("name".into(), None, false),
            ("assembly".into(), None, false),
            ("cam".into(), None, false),
            ("target".into(), None, false),
            ("span".into(), None, false),
            ("size".into(), Some(Val::Str("1600x1500".into())), false),
            ("flutes".into(), Some(Val::Bool(false)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned51 = binary("truediv", e.get("OUT")?, {
                let mut str52 = String::new();
                str52.push_str(&format(&e.get("name")?, &String::new())?);
                str52.push_str(".step");
                Val::Str(str52)
            })?;
            e.set("path", assigned51.clone())?;
            {
                let fun55 = e.get("original")?.attr("_export_colored")?;
                let mut args53 = Vec::new();
                let mut kw54 = Vec::new();
                args53.push(e.get("assembly")?);
                args53.push(e.get("path")?);
                kw54.push(("mesh".into(), Val::Bool(true)));
                fun55.call(args53, kw54)?
            };
            if e.get("flutes")?.truthy()? {
                {
                    let fun58 = e.get("install")?.attr("_graft_flutes")?;
                    let mut args56 = Vec::new();
                    let mut kw57 = Vec::new();
                    args56.push(e.get("path")?);
                    fun58.call(args56, kw57)?
                };
            }
            {
                let fun61 = e.get("jobs")?.attr("append")?;
                let mut args59 = Vec::new();
                let mut kw60 = Vec::new();
                args59.push({
                    let fun64 = e.get("dict")?;
                    let mut args62 = Vec::new();
                    let mut kw63 = Vec::new();
                    kw63.push(("step".into(), {
                        let fun67 = e.get("str")?;
                        let mut args65 = Vec::new();
                        let mut kw66 = Vec::new();
                        args65.push({
                            let fun70 = e.get("path")?.attr("relative_to")?;
                            let mut args68 = Vec::new();
                            let mut kw69 = Vec::new();
                            args68.push(e.get("HARDWARE")?);
                            fun70.call(args68, kw69)?
                        });
                        fun67.call(args65, kw66)?
                    }));
                    kw63.push(("out".into(), {
                        let fun73 = e.get("str")?;
                        let mut args71 = Vec::new();
                        let mut kw72 = Vec::new();
                        args71.push(binary("truediv", e.get("ART")?, {
                            let mut str74 = String::new();
                            str74.push_str(&format(&e.get("name")?, &String::new())?);
                            str74.push_str(".png");
                            Val::Str(str74)
                        })?);
                        fun73.call(args71, kw72)?
                    }));
                    kw63.push(("cam".into(), e.get("cam")?));
                    kw63.push(("target".into(), e.get("target")?));
                    kw63.push(("span".into(), e.get("span")?));
                    kw63.push(("size".into(), e.get("size")?));
                    kw63.push(("up".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        Val::tuple(s)
                    }));
                    kw63.push(("bg".into(), Val::Str("#f2eee8".into())));
                    kw63.push(("transparent".into(), Val::Bool(true)));
                    kw63.push(("solid".into(), Val::Bool(true)));
                    kw63.push(("ortho".into(), Val::Bool(true)));
                    kw63.push(("trim".into(), Val::Bool(false)));
                    kw63.push(("ground".into(), Val::Bool(false)));
                    kw63.push(("fog".into(), Val::Bool(false)));
                    fun64.call(args62, kw63)?
                });
                fun61.call(args59, kw60)?
            };
            {
                let fun77 = e.get("print")?;
                let mut args75 = Vec::new();
                let mut kw76 = Vec::new();
                args75.push(Val::Str("Staged".into()));
                args75.push(e.get("name")?);
                kw76.push(("flush".into(), Val::Bool(true)));
                fun77.call(args75, kw76)?
            };
            Ok(Val::None)
        })
    })?;
    // cylinder
    e.set("cylinder", {
        let params = vec![("stand_off".into(), Some(Val::Int(0i64)), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned78 = {
                let fun81 = e.get("cq")?.attr("Assembly")?;
                let mut args79 = Vec::new();
                let mut kw80 = Vec::new();
                kw80.push(("name".into(), Val::Str("cylinder-connection".into())));
                fun81.call(args79, kw80)?
            };
            e.set("a", assigned78.clone())?;
            let assigned82 = {
                let fun85 = e.get("cq")?.attr("Location")?;
                let mut args83 = Vec::new();
                let mut kw84 = Vec::new();
                args83.push({
                    let fun88 = e.get("cq")?.attr("Vector")?;
                    let mut args86 = Vec::new();
                    let mut kw87 = Vec::new();
                    args86.push(e.get("stand_off")?);
                    args86.push(Val::Int(0i64));
                    args86.push(Val::Int(0i64));
                    fun88.call(args86, kw87)?
                });
                fun85.call(args83, kw84)?
            };
            e.set("move", assigned82.clone())?;
            for item89 in {
                let fun98 = e.get("reg")?.attr("build_assembly")?;
                let mut args96 = Vec::new();
                let mut kw97 = Vec::new();
                fun98.call(args96, kw97)?
            }
            .attr("children")?
            .iter()?
            {
                e.set("child", item89)?;
                {
                    let fun92 = e.get("a")?.attr("add")?;
                    let mut args90 = Vec::new();
                    let mut kw91 = Vec::new();
                    args90.push(if e.get("stand_off")?.truthy()? {
                        {
                            let fun95 = e.get("child")?.attr("obj")?.attr("moved")?;
                            let mut args93 = Vec::new();
                            let mut kw94 = Vec::new();
                            args93.push(e.get("move")?);
                            fun95.call(args93, kw94)?
                        }
                    } else {
                        e.get("child")?.attr("obj")?
                    });
                    kw91.push(("name".into(), e.get("child")?.attr("name")?));
                    kw91.push(("color".into(), e.get("child")?.attr("color")?));
                    fun92.call(args90, kw91)?
                };
            }
            let assigned99 = unary("neg", Val::Float(115.0f64))?;
            e.set("cx", assigned99.clone())?;
            let assigned100 = {
                let fun103 = {
                    let fun106 = {
                        let fun109 = {
                            let fun112 = {
                                let fun115 = {
                                    let fun118 = {
                                        let fun121 = {
                                            let fun124 = {
                                                let fun127 = {
                                                    let fun130 = {
                                                        let fun133 =
                                                            e.get("cq")?.attr("Workplane")?;
                                                        let mut args131 = Vec::new();
                                                        let mut kw132 = Vec::new();
                                                        args131.push(Val::Str("XZ".into()));
                                                        kw132.push(("origin".into(), {
                                                            let mut s = Vec::new();
                                                            s.push(e.get("cx")?);
                                                            s.push(Val::Int(0i64));
                                                            s.push(unary("neg", Val::Int(468i64))?);
                                                            Val::tuple(s)
                                                        }));
                                                        fun133.call(args131, kw132)?
                                                    }
                                                    .attr("moveTo")?;
                                                    let mut args128 = Vec::new();
                                                    let mut kw129 = Vec::new();
                                                    args128.push(Val::Int(0i64));
                                                    args128.push(Val::Int(0i64));
                                                    fun130.call(args128, kw129)?
                                                }
                                                .attr("lineTo")?;
                                                let mut args125 = Vec::new();
                                                let mut kw126 = Vec::new();
                                                args125.push(Val::Int(54i64));
                                                args125.push(Val::Int(0i64));
                                                fun127.call(args125, kw126)?
                                            }
                                            .attr("threePointArc")?;
                                            let mut args122 = Vec::new();
                                            let mut kw123 = Vec::new();
                                            args122.push({
                                                let mut s = Vec::new();
                                                s.push(Val::Int(64i64));
                                                s.push(Val::Int(6i64));
                                                Val::tuple(s)
                                            });
                                            args122.push({
                                                let mut s = Vec::new();
                                                s.push(Val::Float(66.5f64));
                                                s.push(Val::Int(17i64));
                                                Val::tuple(s)
                                            });
                                            fun124.call(args122, kw123)?
                                        }
                                        .attr("lineTo")?;
                                        let mut args119 = Vec::new();
                                        let mut kw120 = Vec::new();
                                        args119.push(Val::Float(66.5f64));
                                        args119.push(Val::Int(366i64));
                                        fun121.call(args119, kw120)?
                                    }
                                    .attr("threePointArc")?;
                                    let mut args116 = Vec::new();
                                    let mut kw117 = Vec::new();
                                    args116.push({
                                        let mut s = Vec::new();
                                        s.push(Val::Int(60i64));
                                        s.push(Val::Int(400i64));
                                        Val::tuple(s)
                                    });
                                    args116.push({
                                        let mut s = Vec::new();
                                        s.push(Val::Int(19i64));
                                        s.push(Val::Int(424i64));
                                        Val::tuple(s)
                                    });
                                    fun118.call(args116, kw117)?
                                }
                                .attr("lineTo")?;
                                let mut args113 = Vec::new();
                                let mut kw114 = Vec::new();
                                args113.push(Val::Int(16i64));
                                args113.push(Val::Int(424i64));
                                fun115.call(args113, kw114)?
                            }
                            .attr("lineTo")?;
                            let mut args110 = Vec::new();
                            let mut kw111 = Vec::new();
                            args110.push(Val::Int(16i64));
                            args110.push(Val::Int(441i64));
                            fun112.call(args110, kw111)?
                        }
                        .attr("lineTo")?;
                        let mut args107 = Vec::new();
                        let mut kw108 = Vec::new();
                        args107.push(Val::Int(0i64));
                        args107.push(Val::Int(441i64));
                        fun109.call(args107, kw108)?
                    }
                    .attr("close")?;
                    let mut args104 = Vec::new();
                    let mut kw105 = Vec::new();
                    fun106.call(args104, kw105)?
                }
                .attr("revolve")?;
                let mut args101 = Vec::new();
                let mut kw102 = Vec::new();
                fun103.call(args101, kw102)?
            };
            e.set("body", assigned100.clone())?;
            {
                let fun136 = e.get("a")?.attr("add")?;
                let mut args134 = Vec::new();
                let mut kw135 = Vec::new();
                args134.push(e.get("body")?);
                kw135.push(("name".into(), Val::Str("cylinder-body".into())));
                kw135.push(("color".into(), e.get("SILVER")?));
                fun136.call(args134, kw135)?
            };
            {
                let fun139 = e.get("a")?.attr("add")?;
                let mut args137 = Vec::new();
                let mut kw138 = Vec::new();
                args137.push({
                    let fun142 = e.get("install")?.attr("_cyl")?;
                    let mut args140 = Vec::new();
                    let mut kw141 = Vec::new();
                    args140.push(e.get("cx")?);
                    args140.push(Val::Int(0i64));
                    args140.push(unary("neg", Val::Int(29i64))?);
                    args140.push(Val::Int(24i64));
                    args140.push(Val::Int(43i64));
                    fun142.call(args140, kw141)?
                });
                kw138.push(("name".into(), Val::Str("cylinder-valve".into())));
                kw138.push(("color".into(), e.get("install")?.attr("BRASS")?));
                fun139.call(args137, kw138)?
            };
            {
                let fun145 = e.get("a")?.attr("add")?;
                let mut args143 = Vec::new();
                let mut kw144 = Vec::new();
                args143.push({
                    let fun148 = e.get("install")?.attr("_cyl")?;
                    let mut args146 = Vec::new();
                    let mut kw147 = Vec::new();
                    args146.push(e.get("cx")?);
                    args146.push(Val::Int(0i64));
                    args146.push(Val::Int(14i64));
                    args146.push(Val::Int(8i64));
                    args146.push(Val::Int(12i64));
                    fun148.call(args146, kw147)?
                });
                kw144.push(("name".into(), Val::Str("cylinder-valve-stem".into())));
                kw144.push(("color".into(), e.get("install")?.attr("BRASS")?));
                fun145.call(args143, kw144)?
            };
            {
                let fun151 = e.get("a")?.attr("add")?;
                let mut args149 = Vec::new();
                let mut kw150 = Vec::new();
                args149.push({
                    let fun154 = e.get("install")?.attr("_cyl")?;
                    let mut args152 = Vec::new();
                    let mut kw153 = Vec::new();
                    args152.push(e.get("cx")?);
                    args152.push(Val::Int(0i64));
                    args152.push(Val::Int(25i64));
                    args152.push(Val::Int(48i64));
                    args152.push(Val::Int(8i64));
                    fun154.call(args152, kw153)?
                });
                kw150.push(("name".into(), Val::Str("cylinder-handwheel".into())));
                kw150.push(("color".into(), e.get("BLACK")?));
                fun151.call(args149, kw150)?
            };
            {
                let fun157 = e.get("a")?.attr("add")?;
                let mut args155 = Vec::new();
                let mut kw156 = Vec::new();
                args155.push({
                    let fun160 = e.get("install")?.attr("_cyl")?;
                    let mut args158 = Vec::new();
                    let mut kw159 = Vec::new();
                    args158.push(e.get("cx")?);
                    args158.push(Val::Int(0i64));
                    args158.push(unary("neg", Val::Int(1i64))?);
                    args158.push(Val::Int(18i64));
                    args158.push(binary(
                        "sub",
                        Val::Int(115i64),
                        e.get("reg")?.attr("INLET_NUT_FACE")?,
                    )?);
                    kw159.push(("axis".into(), Val::Str("X".into())));
                    fun160.call(args158, kw159)?
                });
                kw156.push(("name".into(), Val::Str("valve-outlet".into())));
                kw156.push(("color".into(), e.get("install")?.attr("BRASS")?));
                fun157.call(args155, kw156)?
            };
            let assigned161 = {
                let fun164 = e.get("reg")?.attr("outlet")?;
                let mut args162 = Vec::new();
                let mut kw163 = Vec::new();
                fun164.call(args162, kw163)?
            };
            let unpack165 = unpack(assigned161.clone(), 2)?;
            e.set("mouth", unpack165[0].clone())?;
            e.set("_", unpack165[1].clone())?;
            {
                let fun168 = e.get("a")?.attr("add")?;
                let mut args166 = Vec::new();
                let mut kw167 = Vec::new();
                args166.push({
                    let fun171 = e.get("install")?.attr("_co2_tether")?;
                    let mut args169 = Vec::new();
                    let mut kw170 = Vec::new();
                    args169.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            e.get("mouth")?.get(Val::Int(0i64))?,
                            e.get("stand_off")?,
                        )?);
                        s.push(e.get("mouth")?.get(Val::Int(1i64))?);
                        s.push(e.get("mouth")?.get(Val::Int(2i64))?);
                        Val::tuple(s)
                    });
                    args169.push(Val::Int(69i64));
                    args169.push(Val::Int(160i64));
                    args169.push(Val::Int(28i64));
                    fun171.call(args169, kw170)?
                });
                kw167.push(("name".into(), Val::Str("red-tether".into())));
                kw167.push(("color".into(), e.get("install")?.attr("RED_TUBE")?));
                fun168.call(args166, kw167)?
            };
            return Ok(e.get("a")?);
            Ok(Val::None)
        })
    })?;
    // fill
    e.set("fill", {
        let params = vec![("gap".into(), Some(Val::Int(0i64)), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned172 = {
                let fun175 = e.get("install")?.attr("s_bottle_in_funnel")?;
                let mut args173 = Vec::new();
                let mut kw174 = Vec::new();
                fun175.call(args173, kw174)?
            };
            e.set("source", assigned172.clone())?;
            let assigned176 = {
                let fun179 = e.get("cq")?.attr("Assembly")?;
                let mut args177 = Vec::new();
                let mut kw178 = Vec::new();
                kw178.push(("name".into(), Val::Str("fill".into())));
                fun179.call(args177, kw178)?
            };
            e.set("a", assigned176.clone())?;
            let assigned180 = {
                let mut s = Vec::new();
                s.push(Val::Str("funnel".into()));
                s.push(Val::Str("nameplate".into()));
                s.push(Val::Str("nameplate-ink".into()));
                s.push(Val::Str("enclosure-front-top".into()));
                s.push(Val::Str("enclosure-front-bottom".into()));
                s.push(Val::Str("enclosure-back-top".into()));
                s.push(Val::Str("enclosure-back-bottom".into()));
                s.push(Val::Str("front-display".into()));
                s.push(Val::Str("front-display-screen".into()));
                s.push(Val::Str("display-cover".into()));
                s.push(Val::Str("enclosure-display".into()));
                s.push(Val::Str("enclosure-display-screen".into()));
                Val::set_values(s)
            };
            e.set("exterior", assigned180.clone())?;
            for item181 in e.get("source")?.attr("children")?.iter()? {
                e.set("child", item181)?;
                if {
                    let fun184 = e.get("child")?.attr("name")?.attr("startswith")?;
                    let mut args182 = Vec::new();
                    let mut kw183 = Vec::new();
                    args182.push(Val::Str("bottle-".into()));
                    fun184.call(args182, kw183)?
                }
                .truthy()?
                {
                    {
                        let fun187 = e.get("a")?.attr("add")?;
                        let mut args185 = Vec::new();
                        let mut kw186 = Vec::new();
                        args185.push({
                            let fun190 = e.get("child")?.attr("obj")?.attr("translate")?;
                            let mut args188 = Vec::new();
                            let mut kw189 = Vec::new();
                            args188.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(0i64));
                                s.push(Val::Int(0i64));
                                s.push(e.get("gap")?);
                                Val::tuple(s)
                            });
                            fun190.call(args188, kw189)?
                        });
                        kw186.push(("name".into(), e.get("child")?.attr("name")?));
                        kw186.push(("color".into(), e.get("child")?.attr("color")?));
                        fun187.call(args185, kw186)?
                    };
                } else {
                    if {
                        let v193 = {
                            let v194 = e.get("child")?.attr("name")?;
                            let v195 = e.get("exterior")?;
                            Val::Bool(compare("in", v194.clone(), v195.clone())?.truthy()?)
                        };
                        if v193.truthy()? {
                            v193
                        } else {
                            {
                                let v191 = Val::Str("display".into());
                                let v192 = e.get("child")?.attr("name")?;
                                Val::Bool(compare("in", v191.clone(), v192.clone())?.truthy()?)
                            }
                        }
                    }
                    .truthy()?
                    {
                        {
                            let fun198 = e.get("a")?.attr("add")?;
                            let mut args196 = Vec::new();
                            let mut kw197 = Vec::new();
                            args196.push(e.get("child")?);
                            fun198.call(args196, kw197)?
                        };
                    }
                }
            }
            return Ok(e.get("a")?);
            Ok(Val::None)
        })
    })?;
    // pour
    e.set("pour", {
        let params = vec![("pressed".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned199 = {
                let fun202 = e.get("original")?.attr("_load_faucet_module")?;
                let mut args200 = Vec::new();
                let mut kw201 = Vec::new();
                fun202.call(args200, kw201)?
            };
            e.set("fa", assigned199.clone())?;
            let assigned203 = {
                let fun206 = e.get("original")?.attr("_children_by_name")?;
                let mut args204 = Vec::new();
                let mut kw205 = Vec::new();
                args204.push({
                    let fun209 = e.get("fa")?.attr("build_assembly")?;
                    let mut args207 = Vec::new();
                    let mut kw208 = Vec::new();
                    fun209.call(args207, kw208)?
                });
                fun206.call(args204, kw205)?
            };
            e.set("parts", assigned203.clone())?;
            let assigned210 = {
                let fun213 = e.get("original")?.attr("_physical_levers")?;
                let mut args211 = Vec::new();
                let mut kw212 = Vec::new();
                args211.push(e.get("fa")?);
                fun213.call(args211, kw212)?
            };
            let unpack214 = unpack(assigned210.clone(), 2)?;
            e.set("rest", unpack214[0].clone())?;
            e.set("held", unpack214[1].clone())?;
            let assigned215 = {
                let fun218 = e.get("cq")?.attr("Assembly")?;
                let mut args216 = Vec::new();
                let mut kw217 = Vec::new();
                kw217.push(("name".into(), Val::Str("first-pour".into())));
                fun218.call(args216, kw217)?
            };
            e.set("a", assigned215.clone())?;
            let assigned219 = {
                let mut s = Vec::new();
                s.push(Val::Str("westbrass".into()));
                s.push(Val::Str("drain_tube".into()));
                s.push(Val::Str("soda_faucet_tube".into()));
                s.push(Val::Str("tpu_o_ring".into()));
                s.push(Val::Str("flavor_tube_pos_x".into()));
                s.push(Val::Str("flavor_tube_neg_x".into()));
                s.push(Val::Str("lever".into()));
                s.push(Val::Str("above_counter_plate".into()));
                s.push(Val::Str("above_counter_gasket".into()));
                s.push(Val::Str("shell_base".into()));
                s.push(Val::Str("shell_tip".into()));
                s.push(Val::Str("faucet-display-cover-seated".into()));
                s.push(Val::Str("faucet_display".into()));
                s.push(Val::Str("faucet_display_screen".into()));
                Val::list(s)
            };
            e.set("names", assigned219.clone())?;
            for item220 in e.get("names")?.iter()? {
                e.set("name", item220)?;
                let assigned221 = e.get("parts")?.get(e.get("name")?)?;
                e.set("child", assigned221.clone())?;
                let assigned222 = if {
                    let v223 = e.get("name")?;
                    let v224 = Val::Str("lever".into());
                    Val::Bool(compare("eq", v223.clone(), v224.clone())?.truthy()?)
                }
                .truthy()?
                {
                    if e.get("pressed")?.truthy()? {
                        e.get("held")?
                    } else {
                        e.get("rest")?
                    }
                } else {
                    e.get("child")?.attr("obj")?
                };
                e.set("obj", assigned222.clone())?;
                if {
                    let v225 = e.get("name")?;
                    let v226 = {
                        let mut s = Vec::new();
                        s.push(Val::Str("westbrass".into()));
                        s.push(Val::Str("drain_tube".into()));
                        s.push(Val::Str("flavor_tube_pos_x".into()));
                        s.push(Val::Str("flavor_tube_neg_x".into()));
                        Val::set_values(s)
                    };
                    Val::Bool(compare("in", v225.clone(), v226.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned227 = {
                        let fun230 = e.get("original")?.attr("_clip_z")?;
                        let mut args228 = Vec::new();
                        let mut kw229 = Vec::new();
                        args228.push(e.get("obj")?);
                        args228.push(e.get("fa")?.attr("countertop_top_z")?);
                        args228.push(Val::Int(260i64));
                        fun230.call(args228, kw229)?
                    };
                    e.set("obj", assigned227.clone())?;
                }
                {
                    let fun233 = e.get("a")?.attr("add")?;
                    let mut args231 = Vec::new();
                    let mut kw232 = Vec::new();
                    args231.push(e.get("obj")?);
                    kw232.push(("name".into(), e.get("name")?));
                    kw232.push(("color".into(), e.get("child")?.attr("color")?));
                    fun233.call(args231, kw232)?
                };
            }
            {
                let fun236 = e.get("a")?.attr("add")?;
                let mut args234 = Vec::new();
                let mut kw235 = Vec::new();
                args234.push({
                    let fun239 = e.get("install")?.attr("_box")?;
                    let mut args237 = Vec::new();
                    let mut kw238 = Vec::new();
                    args237.push(unary("neg", Val::Int(120i64))?);
                    args237.push(unary("neg", Val::Int(280i64))?);
                    args237.push(unary("neg", Val::Int(14i64))?);
                    args237.push(Val::Int(240i64));
                    args237.push(Val::Int(340i64));
                    args237.push(Val::Int(14i64));
                    fun239.call(args237, kw238)?
                });
                kw235.push(("name".into(), Val::Str("countertop".into())));
                kw235.push(("color".into(), e.get("install")?.attr("STONE")?));
                fun236.call(args234, kw235)?
            };
            let assigned240 = {
                let fun243 = e.get("fa")?.attr("_tip_centerline_world")?;
                let mut args241 = Vec::new();
                let mut kw242 = Vec::new();
                fun243.call(args241, kw242)?
            };
            let unpack244 = unpack(assigned240.clone(), 2)?;
            e.set("_", unpack244[0].clone())?;
            e.set("tip_vector", unpack244[1].clone())?;
            let assigned245 = {
                let fun248 = e.get("tip_vector")?.attr("toTuple")?;
                let mut args246 = Vec::new();
                let mut kw247 = Vec::new();
                fun248.call(args246, kw247)?
            };
            e.set("tip", assigned245.clone())?;
            let assigned249 = {
                let mut s = Vec::new();
                s.push(e.get("tip")?.get(Val::Int(0i64))?);
                s.push(e.get("tip")?.get(Val::Int(1i64))?);
                Val::tuple(s)
            };
            let unpack250 = unpack(assigned249.clone(), 2)?;
            e.set("gx", unpack250[0].clone())?;
            e.set("gy", unpack250[1].clone())?;
            let assigned251 = {
                let fun254 = {
                    let fun257 = {
                        let fun260 = {
                            let fun263 = {
                                let fun266 = {
                                    let fun269 = e.get("cq")?.attr("Workplane")?;
                                    let mut args267 = Vec::new();
                                    let mut kw268 = Vec::new();
                                    args267.push(Val::Str("XY".into()));
                                    fun269.call(args267, kw268)?
                                }
                                .attr("circle")?;
                                let mut args264 = Vec::new();
                                let mut kw265 = Vec::new();
                                args264.push(Val::Int(31i64));
                                fun266.call(args264, kw265)?
                            }
                            .attr("workplane")?;
                            let mut args261 = Vec::new();
                            let mut kw262 = Vec::new();
                            kw262.push(("offset".into(), Val::Int(104i64)));
                            fun263.call(args261, kw262)?
                        }
                        .attr("circle")?;
                        let mut args258 = Vec::new();
                        let mut kw259 = Vec::new();
                        args258.push(Val::Int(37i64));
                        fun260.call(args258, kw259)?
                    }
                    .attr("loft")?;
                    let mut args255 = Vec::new();
                    let mut kw256 = Vec::new();
                    fun257.call(args255, kw256)?
                }
                .attr("cut")?;
                let mut args252 = Vec::new();
                let mut kw253 = Vec::new();
                args252.push({
                    let fun272 = {
                        let fun275 = {
                            let fun278 = {
                                let fun281 = {
                                    let fun284 = {
                                        let fun287 = e.get("cq")?.attr("Workplane")?;
                                        let mut args285 = Vec::new();
                                        let mut kw286 = Vec::new();
                                        args285.push(Val::Str("XY".into()));
                                        fun287.call(args285, kw286)?
                                    }
                                    .attr("workplane")?;
                                    let mut args282 = Vec::new();
                                    let mut kw283 = Vec::new();
                                    kw283.push(("offset".into(), Val::Int(4i64)));
                                    fun284.call(args282, kw283)?
                                }
                                .attr("circle")?;
                                let mut args279 = Vec::new();
                                let mut kw280 = Vec::new();
                                args279.push(Val::Int(28i64));
                                fun281.call(args279, kw280)?
                            }
                            .attr("workplane")?;
                            let mut args276 = Vec::new();
                            let mut kw277 = Vec::new();
                            kw277.push(("offset".into(), Val::Int(101i64)));
                            fun278.call(args276, kw277)?
                        }
                        .attr("circle")?;
                        let mut args273 = Vec::new();
                        let mut kw274 = Vec::new();
                        args273.push(Val::Float(34.2f64));
                        fun275.call(args273, kw274)?
                    }
                    .attr("loft")?;
                    let mut args270 = Vec::new();
                    let mut kw271 = Vec::new();
                    fun272.call(args270, kw271)?
                });
                fun254.call(args252, kw253)?
            };
            e.set("glass", assigned251.clone())?;
            {
                let fun290 = e.get("a")?.attr("add")?;
                let mut args288 = Vec::new();
                let mut kw289 = Vec::new();
                args288.push({
                    let fun293 = e.get("glass")?.attr("translate")?;
                    let mut args291 = Vec::new();
                    let mut kw292 = Vec::new();
                    args291.push({
                        let mut s = Vec::new();
                        s.push(e.get("gx")?);
                        s.push(e.get("gy")?);
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    fun293.call(args291, kw292)?
                });
                kw289.push(("name".into(), Val::Str("glass".into())));
                kw289.push(("color".into(), e.get("GLASS")?));
                fun290.call(args288, kw289)?
            };
            let assigned294 = {
                let fun297 = {
                    let fun300 = {
                        let fun303 = {
                            let fun306 = {
                                let fun309 = e.get("cq")?.attr("Workplane")?;
                                let mut args307 = Vec::new();
                                let mut kw308 = Vec::new();
                                args307.push(Val::Str("XY".into()));
                                fun309.call(args307, kw308)?
                            }
                            .attr("workplane")?;
                            let mut args304 = Vec::new();
                            let mut kw305 = Vec::new();
                            kw305.push(("offset".into(), Val::Float(103.4f64)));
                            fun306.call(args304, kw305)?
                        }
                        .attr("circle")?;
                        let mut args301 = Vec::new();
                        let mut kw302 = Vec::new();
                        args301.push(Val::Int(37i64));
                        fun303.call(args301, kw302)?
                    }
                    .attr("circle")?;
                    let mut args298 = Vec::new();
                    let mut kw299 = Vec::new();
                    args298.push(Val::Float(34.1f64));
                    fun300.call(args298, kw299)?
                }
                .attr("extrude")?;
                let mut args295 = Vec::new();
                let mut kw296 = Vec::new();
                args295.push(Val::Float(0.7f64));
                fun297.call(args295, kw296)?
            };
            e.set("rim", assigned294.clone())?;
            {
                let fun312 = e.get("a")?.attr("add")?;
                let mut args310 = Vec::new();
                let mut kw311 = Vec::new();
                args310.push({
                    let fun315 = e.get("rim")?.attr("translate")?;
                    let mut args313 = Vec::new();
                    let mut kw314 = Vec::new();
                    args313.push({
                        let mut s = Vec::new();
                        s.push(e.get("gx")?);
                        s.push(e.get("gy")?);
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    fun315.call(args313, kw314)?
                });
                kw311.push(("name".into(), Val::Str("glass-rim".into())));
                kw311.push(("color".into(), {
                    let fun318 = e.get("cq")?.attr("Color")?;
                    let mut args316 = Vec::new();
                    let mut kw317 = Vec::new();
                    args316.push(Val::Float(0.8f64));
                    args316.push(Val::Float(0.87f64));
                    args316.push(Val::Float(0.9f64));
                    fun318.call(args316, kw317)?
                }));
                fun312.call(args310, kw311)?
            };
            let assigned319 = {
                let fun322 = {
                    let fun325 = {
                        let fun328 = {
                            let fun331 = {
                                let fun334 = e.get("cq")?.attr("Workplane")?;
                                let mut args332 = Vec::new();
                                let mut kw333 = Vec::new();
                                args332.push(Val::Str("XY".into()));
                                fun334.call(args332, kw333)?
                            }
                            .attr("workplane")?;
                            let mut args329 = Vec::new();
                            let mut kw330 = Vec::new();
                            kw330.push(("offset".into(), Val::Float(103.35f64)));
                            fun331.call(args329, kw330)?
                        }
                        .attr("circle")?;
                        let mut args326 = Vec::new();
                        let mut kw327 = Vec::new();
                        args326.push(Val::Float(37.5f64));
                        fun328.call(args326, kw327)?
                    }
                    .attr("circle")?;
                    let mut args323 = Vec::new();
                    let mut kw324 = Vec::new();
                    args323.push(Val::Float(36.65f64));
                    fun325.call(args323, kw324)?
                }
                .attr("extrude")?;
                let mut args320 = Vec::new();
                let mut kw321 = Vec::new();
                args320.push(Val::Float(0.8f64));
                fun322.call(args320, kw321)?
            };
            e.set("rim_edge", assigned319.clone())?;
            {
                let fun337 = e.get("a")?.attr("add")?;
                let mut args335 = Vec::new();
                let mut kw336 = Vec::new();
                args335.push({
                    let fun340 = e.get("rim_edge")?.attr("translate")?;
                    let mut args338 = Vec::new();
                    let mut kw339 = Vec::new();
                    args338.push({
                        let mut s = Vec::new();
                        s.push(e.get("gx")?);
                        s.push(e.get("gy")?);
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    fun340.call(args338, kw339)?
                });
                kw336.push(("name".into(), Val::Str("glass-rim-edge".into())));
                kw336.push(("color".into(), {
                    let fun343 = e.get("cq")?.attr("Color")?;
                    let mut args341 = Vec::new();
                    let mut kw342 = Vec::new();
                    args341.push(Val::Float(0.46f64));
                    args341.push(Val::Float(0.57f64));
                    args341.push(Val::Float(0.62f64));
                    fun343.call(args341, kw342)?
                }));
                fun337.call(args335, kw336)?
            };
            let assigned344 = {
                let fun347 = {
                    let fun350 = {
                        let fun353 = {
                            let fun356 = {
                                let fun359 = e.get("cq")?.attr("Workplane")?;
                                let mut args357 = Vec::new();
                                let mut kw358 = Vec::new();
                                args357.push(Val::Str("XY".into()));
                                fun359.call(args357, kw358)?
                            }
                            .attr("workplane")?;
                            let mut args354 = Vec::new();
                            let mut kw355 = Vec::new();
                            kw355.push(("offset".into(), Val::Float(0.8f64)));
                            fun356.call(args354, kw355)?
                        }
                        .attr("circle")?;
                        let mut args351 = Vec::new();
                        let mut kw352 = Vec::new();
                        args351.push(Val::Float(31.15f64));
                        fun353.call(args351, kw352)?
                    }
                    .attr("circle")?;
                    let mut args348 = Vec::new();
                    let mut kw349 = Vec::new();
                    args348.push(Val::Float(28.2f64));
                    fun350.call(args348, kw349)?
                }
                .attr("extrude")?;
                let mut args345 = Vec::new();
                let mut kw346 = Vec::new();
                args345.push(Val::Float(2.0f64));
                fun347.call(args345, kw346)?
            };
            e.set("base", assigned344.clone())?;
            {
                let fun362 = e.get("a")?.attr("add")?;
                let mut args360 = Vec::new();
                let mut kw361 = Vec::new();
                args360.push({
                    let fun365 = e.get("base")?.attr("translate")?;
                    let mut args363 = Vec::new();
                    let mut kw364 = Vec::new();
                    args363.push({
                        let mut s = Vec::new();
                        s.push(e.get("gx")?);
                        s.push(e.get("gy")?);
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    fun365.call(args363, kw364)?
                });
                kw361.push(("name".into(), Val::Str("glass-base".into())));
                kw361.push(("color".into(), {
                    let fun368 = e.get("cq")?.attr("Color")?;
                    let mut args366 = Vec::new();
                    let mut kw367 = Vec::new();
                    args366.push(Val::Float(0.74f64));
                    args366.push(Val::Float(0.83f64));
                    args366.push(Val::Float(0.86f64));
                    fun368.call(args366, kw367)?
                }));
                fun362.call(args360, kw361)?
            };
            let assigned369 = {
                let fun372 = {
                    let fun375 = {
                        let fun378 = {
                            let fun381 = {
                                let fun384 = e.get("cq")?.attr("Workplane")?;
                                let mut args382 = Vec::new();
                                let mut kw383 = Vec::new();
                                args382.push(Val::Str("XY".into()));
                                fun384.call(args382, kw383)?
                            }
                            .attr("workplane")?;
                            let mut args379 = Vec::new();
                            let mut kw380 = Vec::new();
                            kw380.push(("offset".into(), Val::Float(0.6f64)));
                            fun381.call(args379, kw380)?
                        }
                        .attr("circle")?;
                        let mut args376 = Vec::new();
                        let mut kw377 = Vec::new();
                        args376.push(Val::Float(31.3f64));
                        fun378.call(args376, kw377)?
                    }
                    .attr("circle")?;
                    let mut args373 = Vec::new();
                    let mut kw374 = Vec::new();
                    args373.push(Val::Float(30.55f64));
                    fun375.call(args373, kw374)?
                }
                .attr("extrude")?;
                let mut args370 = Vec::new();
                let mut kw371 = Vec::new();
                args370.push(Val::Float(0.8f64));
                fun372.call(args370, kw371)?
            };
            e.set("base_edge", assigned369.clone())?;
            {
                let fun387 = e.get("a")?.attr("add")?;
                let mut args385 = Vec::new();
                let mut kw386 = Vec::new();
                args385.push({
                    let fun390 = e.get("base_edge")?.attr("translate")?;
                    let mut args388 = Vec::new();
                    let mut kw389 = Vec::new();
                    args388.push({
                        let mut s = Vec::new();
                        s.push(e.get("gx")?);
                        s.push(e.get("gy")?);
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    fun390.call(args388, kw389)?
                });
                kw386.push(("name".into(), Val::Str("glass-base-edge".into())));
                kw386.push(("color".into(), {
                    let fun393 = e.get("cq")?.attr("Color")?;
                    let mut args391 = Vec::new();
                    let mut kw392 = Vec::new();
                    args391.push(Val::Float(0.46f64));
                    args391.push(Val::Float(0.57f64));
                    args391.push(Val::Float(0.62f64));
                    fun393.call(args391, kw392)?
                }));
                fun387.call(args385, kw386)?
            };
            let assigned394 = {
                let fun397 = e.get("math")?.attr("atan2")?;
                let mut args395 = Vec::new();
                let mut kw396 = Vec::new();
                args395.push(unary("neg", Val::Float(1.8f64))?);
                args395.push(Val::Int(1i64));
                fun397.call(args395, kw396)?
            };
            e.set("face_angle", assigned394.clone())?;
            // glass_stroke
            e.set("glass_stroke", {
                let params = vec![
                    ("name".into(), None, false),
                    ("angle".into(), None, false),
                    ("z0".into(), None, false),
                    ("z1".into(), None, false),
                    ("radius".into(), None, false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned398 = {
                        let mut s = Vec::new();
                        Val::list(s)
                    };
                    e.set("points", assigned398.clone())?;
                    for item399 in {
                        let mut s = Vec::new();
                        s.push(e.get("z0")?);
                        s.push(e.get("z1")?);
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("z", item399)?;
                        let assigned400 = binary(
                            "add",
                            Val::Int(31i64),
                            binary(
                                "truediv",
                                binary("mul", Val::Int(6i64), e.get("z")?)?,
                                Val::Int(104i64),
                            )?,
                        )?;
                        e.set("r", assigned400.clone())?;
                        {
                            let fun403 = e.get("points")?.attr("append")?;
                            let mut args401 = Vec::new();
                            let mut kw402 = Vec::new();
                            args401.push({
                                let fun406 = e.get("cq")?.attr("Vector")?;
                                let mut args404 = Vec::new();
                                let mut kw405 = Vec::new();
                                args404.push(binary(
                                    "add",
                                    e.get("gx")?,
                                    binary("mul", e.get("r")?, {
                                        let fun409 = e.get("math")?.attr("cos")?;
                                        let mut args407 = Vec::new();
                                        let mut kw408 = Vec::new();
                                        args407.push(e.get("angle")?);
                                        fun409.call(args407, kw408)?
                                    })?,
                                )?);
                                args404.push(binary(
                                    "add",
                                    e.get("gy")?,
                                    binary("mul", e.get("r")?, {
                                        let fun412 = e.get("math")?.attr("sin")?;
                                        let mut args410 = Vec::new();
                                        let mut kw411 = Vec::new();
                                        args410.push(e.get("angle")?);
                                        fun412.call(args410, kw411)?
                                    })?,
                                )?);
                                args404.push(e.get("z")?);
                                fun406.call(args404, kw405)?
                            });
                            fun403.call(args401, kw402)?
                        };
                    }
                    let assigned413 = binary(
                        "sub",
                        e.get("points")?.get(Val::Int(1i64))?,
                        e.get("points")?.get(Val::Int(0i64))?,
                    )?;
                    e.set("span", assigned413.clone())?;
                    let assigned414 = {
                        let fun417 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                        let mut args415 = Vec::new();
                        let mut kw416 = Vec::new();
                        args415.push(e.get("radius")?);
                        args415.push(e.get("span")?.attr("Length")?);
                        args415.push(e.get("points")?.get(Val::Int(0i64))?);
                        args415.push({
                            let fun420 = e.get("span")?.attr("normalized")?;
                            let mut args418 = Vec::new();
                            let mut kw419 = Vec::new();
                            fun420.call(args418, kw419)?
                        });
                        fun417.call(args415, kw416)?
                    };
                    e.set("body", assigned414.clone())?;
                    let assigned421 = {
                        let e = e.child();
                        let out422 = Val::list(vec![]);
                        for item423 in e.get("points")?.iter()? {
                            e.set("p", item423)?;
                            out422.attr("append")?.call(
                                vec![{
                                    let fun426 = e.get("cq")?.attr("Solid")?.attr("makeSphere")?;
                                    let mut args424 = Vec::new();
                                    let mut kw425 = Vec::new();
                                    args424.push(e.get("radius")?);
                                    args424.push(e.get("p")?);
                                    kw425.push((
                                        "angleDegrees1".into(),
                                        unary("neg", Val::Int(90i64))?,
                                    ));
                                    fun426.call(args424, kw425)?
                                }],
                                vec![],
                            )?;
                        }
                        out422
                    };
                    e.set("caps", assigned421.clone())?;
                    {
                        let fun429 = e.get("a")?.attr("add")?;
                        let mut args427 = Vec::new();
                        let mut kw428 = Vec::new();
                        args427.push({
                            let fun432 = e.get("cq")?.attr("Compound")?.attr("makeCompound")?;
                            let mut args430 = Vec::new();
                            let mut kw431 = Vec::new();
                            args430.push({
                                let mut s = Vec::new();
                                s.push(e.get("body")?);
                                s.extend(e.get("caps")?.iter()?);
                                Val::list(s)
                            });
                            fun432.call(args430, kw431)?
                        });
                        kw428.push(("name".into(), e.get("name")?));
                        kw428.push(("color".into(), {
                            let fun435 = e.get("cq")?.attr("Color")?;
                            let mut args433 = Vec::new();
                            let mut kw434 = Vec::new();
                            args433.push(Val::Float(0.7f64));
                            args433.push(Val::Float(0.8f64));
                            args433.push(Val::Float(0.85f64));
                            fun435.call(args433, kw434)?
                        }));
                        fun429.call(args427, kw428)?
                    };
                    Ok(Val::None)
                })
            })?;
            let assigned436 = {
                let fun439 = e.get("math")?.attr("acos")?;
                let mut args437 = Vec::new();
                let mut kw438 = Vec::new();
                args437.push(binary(
                    "truediv",
                    binary(
                        "truediv",
                        binary("mul", Val::Float(0.67f64), Val::Int(6i64))?,
                        Val::Int(104i64),
                    )?,
                    {
                        let fun442 = e.get("math")?.attr("hypot")?;
                        let mut args440 = Vec::new();
                        let mut kw441 = Vec::new();
                        args440.push(Val::Int(1i64));
                        args440.push(Val::Float(1.8f64));
                        fun442.call(args440, kw441)?
                    },
                )?);
                fun439.call(args437, kw438)?
            };
            e.set("side_angle", assigned436.clone())?;
            for item443 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Int(1i64))?);
                    s.push(Val::Str("left".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(1i64));
                    s.push(Val::Str("right".into()));
                    Val::tuple(s)
                });
                Val::list(s)
            }
            .iter()?
            {
                let unpack448 = unpack(item443, 2)?;
                e.set("sign", unpack448[0].clone())?;
                e.set("side", unpack448[1].clone())?;
                {
                    let fun446 = e.get("glass_stroke")?;
                    let mut args444 = Vec::new();
                    let mut kw445 = Vec::new();
                    args444.push({
                        let mut str447 = String::new();
                        str447.push_str("glass-edge-");
                        str447.push_str(&format(&e.get("side")?, &String::new())?);
                        Val::Str(str447)
                    });
                    args444.push(binary(
                        "add",
                        e.get("face_angle")?,
                        binary("mul", e.get("sign")?, e.get("side_angle")?)?,
                    )?);
                    args444.push(Val::Float(2.5f64));
                    args444.push(Val::Float(102.8f64));
                    args444.push(Val::Float(0.7f64));
                    fun446.call(args444, kw445)?
                };
            }
            {
                let fun451 = e.get("glass_stroke")?;
                let mut args449 = Vec::new();
                let mut kw450 = Vec::new();
                args449.push(Val::Str("glass-highlight-wide".into()));
                args449.push(binary(
                    "add",
                    binary("sub", e.get("face_angle")?, e.get("side_angle")?)?,
                    Val::Float(0.16f64),
                )?);
                args449.push(Val::Int(12i64));
                args449.push(Val::Int(96i64));
                args449.push(Val::Float(1.15f64));
                fun451.call(args449, kw450)?
            };
            {
                let fun454 = e.get("glass_stroke")?;
                let mut args452 = Vec::new();
                let mut kw453 = Vec::new();
                args452.push(Val::Str("glass-highlight-short".into()));
                args452.push(binary(
                    "sub",
                    binary("add", e.get("face_angle")?, e.get("side_angle")?)?,
                    Val::Float(0.13f64),
                )?);
                args452.push(Val::Int(51i64));
                args452.push(Val::Int(95i64));
                args452.push(Val::Float(0.65f64));
                fun454.call(args452, kw453)?
            };
            if e.get("pressed")?.truthy()? {
                let assigned455 = {
                    let fun458 = {
                        let fun461 = {
                            let fun464 = {
                                let fun467 = {
                                    let fun470 = {
                                        let fun473 = e.get("cq")?.attr("Workplane")?;
                                        let mut args471 = Vec::new();
                                        let mut kw472 = Vec::new();
                                        args471.push(Val::Str("XY".into()));
                                        fun473.call(args471, kw472)?
                                    }
                                    .attr("workplane")?;
                                    let mut args468 = Vec::new();
                                    let mut kw469 = Vec::new();
                                    kw469.push(("offset".into(), Val::Int(5i64)));
                                    fun470.call(args468, kw469)?
                                }
                                .attr("circle")?;
                                let mut args465 = Vec::new();
                                let mut kw466 = Vec::new();
                                args465.push(Val::Float(27.7f64));
                                fun467.call(args465, kw466)?
                            }
                            .attr("workplane")?;
                            let mut args462 = Vec::new();
                            let mut kw463 = Vec::new();
                            kw463.push(("offset".into(), Val::Int(75i64)));
                            fun464.call(args462, kw463)?
                        }
                        .attr("circle")?;
                        let mut args459 = Vec::new();
                        let mut kw460 = Vec::new();
                        args459.push(Val::Float(32.1f64));
                        fun461.call(args459, kw460)?
                    }
                    .attr("loft")?;
                    let mut args456 = Vec::new();
                    let mut kw457 = Vec::new();
                    fun458.call(args456, kw457)?
                };
                e.set("drink", assigned455.clone())?;
                {
                    let fun476 = e.get("a")?.attr("add")?;
                    let mut args474 = Vec::new();
                    let mut kw475 = Vec::new();
                    args474.push({
                        let fun479 = e.get("drink")?.attr("translate")?;
                        let mut args477 = Vec::new();
                        let mut kw478 = Vec::new();
                        args477.push({
                            let mut s = Vec::new();
                            s.push(e.get("gx")?);
                            s.push(e.get("gy")?);
                            s.push(Val::Int(0i64));
                            Val::tuple(s)
                        });
                        fun479.call(args477, kw478)?
                    });
                    kw475.push(("name".into(), Val::Str("drink".into())));
                    kw475.push(("color".into(), e.get("DRINK")?));
                    fun476.call(args474, kw475)?
                };
                let assigned480 = {
                    let fun483 = {
                        let fun486 = {
                            let fun489 = {
                                let fun492 = e.get("cq")?.attr("Workplane")?;
                                let mut args490 = Vec::new();
                                let mut kw491 = Vec::new();
                                args490.push(Val::Str("XY".into()));
                                fun492.call(args490, kw491)?
                            }
                            .attr("workplane")?;
                            let mut args487 = Vec::new();
                            let mut kw488 = Vec::new();
                            kw488.push(("offset".into(), Val::Int(80i64)));
                            fun489.call(args487, kw488)?
                        }
                        .attr("circle")?;
                        let mut args484 = Vec::new();
                        let mut kw485 = Vec::new();
                        args484.push(Val::Float(32.1f64));
                        fun486.call(args484, kw485)?
                    }
                    .attr("extrude")?;
                    let mut args481 = Vec::new();
                    let mut kw482 = Vec::new();
                    args481.push(Val::Float(0.15f64));
                    fun483.call(args481, kw482)?
                };
                e.set("top", assigned480.clone())?;
                {
                    let fun495 = e.get("a")?.attr("add")?;
                    let mut args493 = Vec::new();
                    let mut kw494 = Vec::new();
                    args493.push({
                        let fun498 = e.get("top")?.attr("translate")?;
                        let mut args496 = Vec::new();
                        let mut kw497 = Vec::new();
                        args496.push({
                            let mut s = Vec::new();
                            s.push(e.get("gx")?);
                            s.push(e.get("gy")?);
                            s.push(Val::Int(0i64));
                            Val::tuple(s)
                        });
                        fun498.call(args496, kw497)?
                    });
                    kw494.push(("name".into(), Val::Str("drink-top".into())));
                    kw494.push(("color".into(), {
                        let fun501 = e.get("cq")?.attr("Color")?;
                        let mut args499 = Vec::new();
                        let mut kw500 = Vec::new();
                        args499.push(Val::Float(0.53f64));
                        args499.push(Val::Float(0.31f64));
                        args499.push(Val::Float(0.18f64));
                        fun501.call(args499, kw500)?
                    }));
                    fun495.call(args493, kw494)?
                };
            }
            {
                let fun504 = binary(
                    "truediv",
                    e.get("OUT")?,
                    Val::Str("pour-points.json".into()),
                )?
                .attr("write_text")?;
                let mut args502 = Vec::new();
                let mut kw503 = Vec::new();
                args502.push({
                    let fun507 = e.get("json")?.attr("dumps")?;
                    let mut args505 = Vec::new();
                    let mut kw506 = Vec::new();
                    args505.push({
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("tip".into()), {
                            let fun510 = e.get("list")?;
                            let mut args508 = Vec::new();
                            let mut kw509 = Vec::new();
                            args508.push(e.get("tip")?);
                            fun510.call(args508, kw509)?
                        })?;
                        d.set(Val::Str("lever".into()), {
                            let mut s = Vec::new();
                            s.push(Val::Int(0i64));
                            s.push(e.get("fa")?.attr("lever_pivot_y")?);
                            s.push(e.get("fa")?.attr("lever_pivot_z")?);
                            Val::list(s)
                        })?;
                        d
                    });
                    fun507.call(args505, kw506)?
                });
                fun504.call(args502, kw503)?
            };
            return Ok(e.get("a")?);
            Ok(Val::None)
        })
    })?;
    // materials
    e.set("materials", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let fun513 = e.get("dict")?;
                    let mut args511 = Vec::new();
                    let mut kw512 = Vec::new();
                    kw512.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("glass".into()));
                        Val::list(s)
                    }));
                    kw512.push(("color".into(), Val::Str("#d6e8ec".into())));
                    kw512.push(("opacity".into(), Val::Float(0.06f64)));
                    kw512.push(("roughness".into(), Val::Float(0.15f64)));
                    kw512.push(("metalness".into(), Val::Float(0.05f64)));
                    kw512.push(("depth_write".into(), Val::Bool(false)));
                    kw512.push(("side".into(), Val::Str("double".into())));
                    kw512.push(("order".into(), Val::Int(10i64)));
                    fun513.call(args511, kw512)?
                });
                s.push({
                    let fun516 = e.get("dict")?;
                    let mut args514 = Vec::new();
                    let mut kw515 = Vec::new();
                    kw515.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("glass-rim".into()));
                        s.push(Val::Str("glass-base".into()));
                        Val::list(s)
                    }));
                    kw515.push(("color".into(), Val::Str("#d3e1e5".into())));
                    kw515.push(("unlit".into(), Val::Bool(true)));
                    kw515.push(("side".into(), Val::Str("front".into())));
                    fun516.call(args514, kw515)?
                });
                s.push({
                    let fun519 = e.get("dict")?;
                    let mut args517 = Vec::new();
                    let mut kw518 = Vec::new();
                    kw518.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("glass-edge-*".into()));
                        s.push(Val::Str("glass-rim-edge".into()));
                        s.push(Val::Str("glass-base-edge".into()));
                        Val::list(s)
                    }));
                    kw518.push(("color".into(), Val::Str("#8099a4".into())));
                    kw518.push(("unlit".into(), Val::Bool(true)));
                    kw518.push(("side".into(), Val::Str("front".into())));
                    fun519.call(args517, kw518)?
                });
                s.push({
                    let fun522 = e.get("dict")?;
                    let mut args520 = Vec::new();
                    let mut kw521 = Vec::new();
                    kw521.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("glass-highlight-*".into()));
                        Val::list(s)
                    }));
                    kw521.push(("color".into(), Val::Str("#ffffff".into())));
                    kw521.push(("opacity".into(), Val::Float(0.74f64)));
                    kw521.push(("unlit".into(), Val::Bool(true)));
                    kw521.push(("depth_write".into(), Val::Bool(false)));
                    kw521.push(("side".into(), Val::Str("front".into())));
                    kw521.push(("order".into(), Val::Int(11i64)));
                    fun522.call(args520, kw521)?
                });
                s.push({
                    let fun525 = e.get("dict")?;
                    let mut args523 = Vec::new();
                    let mut kw524 = Vec::new();
                    kw524.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("drink".into()));
                        Val::list(s)
                    }));
                    kw524.push(("color".into(), Val::Str("#351a0f".into())));
                    kw524.push(("unlit".into(), Val::Bool(true)));
                    kw524.push(("side".into(), Val::Str("front".into())));
                    fun525.call(args523, kw524)?
                });
                s.push({
                    let fun528 = e.get("dict")?;
                    let mut args526 = Vec::new();
                    let mut kw527 = Vec::new();
                    kw527.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("drink-top".into()));
                        Val::list(s)
                    }));
                    kw527.push(("color".into(), Val::Str("#6f422b".into())));
                    kw527.push(("unlit".into(), Val::Bool(true)));
                    kw527.push(("side".into(), Val::Str("front".into())));
                    fun528.call(args526, kw527)?
                });
                Val::list(s)
            });
            Ok(Val::None)
        })
    })?;
    // render
    e.set("render", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned529 = {
                let e = e.child();
                let out530 = Val::list(vec![]);
                for item531 in e.get("jobs")?.iter()? {
                    e.set("job", item531)?;
                    out530.attr("append")?.call(
                        vec![{
                            let fun534 = e.get("dict")?;
                            let mut args532 = Vec::new();
                            let mut kw533 = Vec::new();
                            args532.push(e.get("job")?);
                            kw533.push(("materials".into(), {
                                let fun537 = e.get("materials")?;
                                let mut args535 = Vec::new();
                                let mut kw536 = Vec::new();
                                fun537.call(args535, kw536)?
                            }));
                            fun534.call(args532, kw533)?
                        }],
                        vec![],
                    )?;
                }
                out530
            };
            e.set("entries", assigned529.clone())?;
            {
                let fun540 = binary("truediv", e.get("OUT")?, Val::Str("scenes.json".into()))?
                    .attr("write_text")?;
                let mut args538 = Vec::new();
                let mut kw539 = Vec::new();
                args538.push(binary(
                    "add",
                    {
                        let fun543 = e.get("json")?.attr("dumps")?;
                        let mut args541 = Vec::new();
                        let mut kw542 = Vec::new();
                        args541.push(e.get("entries")?);
                        kw542.push(("indent".into(), Val::Int(2i64)));
                        fun543.call(args541, kw542)?
                    },
                    Val::Str("\n".into()),
                )?);
                fun540.call(args538, kw539)?
            };
            {
                let fun546 = e.get("_hsm_render")?.attr("render")?;
                let mut args544 = Vec::new();
                let mut kw545 = Vec::new();
                args544.push(e.get("entries")?);
                fun546.call(args544, kw545)?
            };
            Ok(Val::None)
        })
    })?;
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
                let fun549 = e.get("OUT")?.attr("mkdir")?;
                let mut args547 = Vec::new();
                let mut kw548 = Vec::new();
                kw548.push(("parents".into(), Val::Bool(true)));
                kw548.push(("exist_ok".into(), Val::Bool(true)));
                fun549.call(args547, kw548)?
            };
            {
                let fun552 = e.get("ART")?.attr("mkdir")?;
                let mut args550 = Vec::new();
                let mut kw551 = Vec::new();
                kw551.push(("exist_ok".into(), Val::Bool(true)));
                fun552.call(args550, kw551)?
            };
            let assigned553 = {
                let fun556 = e.get("set")?;
                let mut args554 = Vec::new();
                let mut kw555 = Vec::new();
                args554.push(e.get("sys")?.attr("argv")?.get(Val::Slice {
                    start: Some(Val::Int(1i64).integer()?),
                    stop: None,
                    step: 1,
                })?);
                fun556.call(args554, kw555)?
            };
            e.set("wanted", assigned553.clone())?;
            if {
                let v559 = unary("not", e.get("wanted")?)?;
                if v559.truthy()? {
                    v559
                } else {
                    {
                        let v557 = Val::Str("gas".into());
                        let v558 = e.get("wanted")?;
                        Val::Bool(compare("in", v557.clone(), v558.clone())?.truthy()?)
                    }
                }
            }
            .truthy()?
            {
                {
                    let fun562 = e.get("stage")?;
                    let mut args560 = Vec::new();
                    let mut kw561 = Vec::new();
                    args560.push(Val::Str("co2-ready".into()));
                    args560.push({
                        let fun565 = e.get("cylinder")?;
                        let mut args563 = Vec::new();
                        let mut kw564 = Vec::new();
                        args563.push(Val::Int(30i64));
                        fun565.call(args563, kw564)?
                    });
                    args560.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.12f64));
                        s.push(Val::Int(1i64));
                        s.push(Val::Float(0.15f64));
                        Val::tuple(s)
                    });
                    args560.push({
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Int(34i64))?);
                        s.push(Val::Int(0i64));
                        s.push(unary("neg", Val::Int(58i64))?);
                        Val::tuple(s)
                    });
                    args560.push(Val::Int(150i64));
                    fun562.call(args560, kw561)?
                };
                {
                    let fun568 = e.get("stage")?;
                    let mut args566 = Vec::new();
                    let mut kw567 = Vec::new();
                    args566.push(Val::Str("co2-connected".into()));
                    args566.push({
                        let fun571 = e.get("cylinder")?;
                        let mut args569 = Vec::new();
                        let mut kw570 = Vec::new();
                        fun571.call(args569, kw570)?
                    });
                    args566.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.12f64));
                        s.push(Val::Int(1i64));
                        s.push(Val::Float(0.15f64));
                        Val::tuple(s)
                    });
                    args566.push({
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Int(34i64))?);
                        s.push(Val::Int(0i64));
                        s.push(unary("neg", Val::Int(58i64))?);
                        Val::tuple(s)
                    });
                    args566.push(Val::Int(150i64));
                    fun568.call(args566, kw567)?
                };
            }
            if {
                let v574 = unary("not", e.get("wanted")?)?;
                if v574.truthy()? {
                    v574
                } else {
                    {
                        let v572 = Val::Str("power".into());
                        let v573 = e.get("wanted")?;
                        Val::Bool(compare("in", v572.clone(), v573.clone())?.truthy()?)
                    }
                }
            }
            .truthy()?
            {
                let assigned575 = {
                    let fun578 = e.get("original")?.attr("_build_connection_steps")?;
                    let mut args576 = Vec::new();
                    let mut kw577 = Vec::new();
                    args576.push(e.get("OUT")?);
                    fun578.call(args576, kw577)?
                };
                e.set("paths", assigned575.clone())?;
                let assigned579 = {
                    let fun582 = e.get("cq")?.attr("Assembly")?.attr("load")?;
                    let mut args580 = Vec::new();
                    let mut kw581 = Vec::new();
                    args580.push({
                        let fun585 = e.get("str")?;
                        let mut args583 = Vec::new();
                        let mut kw584 = Vec::new();
                        args583.push(
                            e.get("paths")?
                                .get(Val::Str("connect-rear-connected".into()))?,
                        );
                        fun585.call(args583, kw584)?
                    });
                    fun582.call(args580, kw581)?
                };
                e.set("connected", assigned579.clone())?;
                for item586 in {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("power-ready".into()));
                        s.push(Val::Int(65i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("power-connected".into()));
                        s.push(Val::Float(0.5f64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                }
                .iter()?
                {
                    let unpack606 = unpack(item586, 2)?;
                    e.set("label", unpack606[0].clone())?;
                    e.set("gap", unpack606[1].clone())?;
                    let assigned587 = {
                        let fun590 = e.get("cq")?.attr("Assembly")?;
                        let mut args588 = Vec::new();
                        let mut kw589 = Vec::new();
                        kw589.push(("name".into(), e.get("label")?));
                        fun590.call(args588, kw589)?
                    };
                    e.set("a", assigned587.clone())?;
                    for item591 in e.get("connected")?.attr("children")?.iter()? {
                        e.set("child", item591)?;
                        {
                            let fun594 = e.get("a")?.attr("add")?;
                            let mut args592 = Vec::new();
                            let mut kw593 = Vec::new();
                            args592.push(e.get("child")?);
                            fun594.call(args592, kw593)?
                        };
                    }
                    {
                        let fun597 = e.get("a")?.attr("add")?;
                        let mut args595 = Vec::new();
                        let mut kw596 = Vec::new();
                        args595.push({
                            let fun600 = e.get("install")?.attr("_c13_cordset")?;
                            let mut args598 = Vec::new();
                            let mut kw599 = Vec::new();
                            args598.push(e.get("gap")?);
                            fun600.call(args598, kw599)?
                        });
                        kw596.push(("name".into(), Val::Str("cordset".into())));
                        kw596.push(("color".into(), e.get("install")?.attr("CORDSET")?));
                        fun597.call(args595, kw596)?
                    };
                    let assigned601 = e.get("install")?.attr("C14_STATION")?;
                    let unpack602 = unpack(assigned601.clone(), 2)?;
                    e.set("x", unpack602[0].clone())?;
                    e.set("z", unpack602[1].clone())?;
                    {
                        let fun605 = e.get("stage")?;
                        let mut args603 = Vec::new();
                        let mut kw604 = Vec::new();
                        args603.push(e.get("label")?);
                        args603.push(e.get("a")?);
                        args603.push({
                            let mut s = Vec::new();
                            s.push(unary("neg", Val::Float(0.85f64))?);
                            s.push(Val::Int(1i64));
                            s.push(Val::Float(0.25f64));
                            Val::tuple(s)
                        });
                        args603.push({
                            let mut s = Vec::new();
                            s.push(binary("sub", e.get("x")?, Val::Int(8i64))?);
                            s.push(binary(
                                "add",
                                e.get("install")?.attr("REAR_FACE_Y")?,
                                Val::Int(34i64),
                            )?);
                            s.push(binary("sub", e.get("z")?, Val::Int(16i64))?);
                            Val::tuple(s)
                        });
                        args603.push(Val::Int(64i64));
                        kw604.push(("size".into(), Val::Str("1800x1300".into())));
                        kw604.push(("flutes".into(), Val::Bool(true)));
                        fun605.call(args603, kw604)?
                    };
                }
            }
            if {
                let v609 = unary("not", e.get("wanted")?)?;
                if v609.truthy()? {
                    v609
                } else {
                    {
                        let v607 = Val::Str("fill".into());
                        let v608 = e.get("wanted")?;
                        Val::Bool(compare("in", v607.clone(), v608.clone())?.truthy()?)
                    }
                }
            }
            .truthy()?
            {
                for item610 in {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("fill-ready".into()));
                        s.push(Val::Int(85i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("fill-seated".into()));
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                }
                .iter()?
                {
                    let unpack617 = unpack(item610, 2)?;
                    e.set("name", unpack617[0].clone())?;
                    e.set("gap", unpack617[1].clone())?;
                    {
                        let fun613 = e.get("stage")?;
                        let mut args611 = Vec::new();
                        let mut kw612 = Vec::new();
                        args611.push(e.get("name")?);
                        args611.push({
                            let fun616 = e.get("fill")?;
                            let mut args614 = Vec::new();
                            let mut kw615 = Vec::new();
                            args614.push(e.get("gap")?);
                            fun616.call(args614, kw615)?
                        });
                        args611.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(0.65f64));
                            s.push(unary("neg", Val::Int(1i64))?);
                            s.push(Val::Float(0.5f64));
                            Val::tuple(s)
                        });
                        args611.push({
                            let mut s = Vec::new();
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(140i64));
                            s.push(Val::Int(465i64));
                            Val::tuple(s)
                        });
                        args611.push(Val::Int(265i64));
                        kw612.push(("flutes".into(), Val::Bool(true)));
                        fun613.call(args611, kw612)?
                    };
                }
            }
            if {
                let v620 = unary("not", e.get("wanted")?)?;
                if v620.truthy()? {
                    v620
                } else {
                    {
                        let v618 = Val::Str("pour".into());
                        let v619 = e.get("wanted")?;
                        Val::Bool(compare("in", v618.clone(), v619.clone())?.truthy()?)
                    }
                }
            }
            .truthy()?
            {
                for item621 in {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("pour-ready".into()));
                        s.push(Val::Bool(false));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("pour-running".into()));
                        s.push(Val::Bool(true));
                        Val::tuple(s)
                    });
                    Val::list(s)
                }
                .iter()?
                {
                    let unpack628 = unpack(item621, 2)?;
                    e.set("name", unpack628[0].clone())?;
                    e.set("pressed", unpack628[1].clone())?;
                    {
                        let fun624 = e.get("stage")?;
                        let mut args622 = Vec::new();
                        let mut kw623 = Vec::new();
                        args622.push(e.get("name")?);
                        args622.push({
                            let fun627 = e.get("pour")?;
                            let mut args625 = Vec::new();
                            let mut kw626 = Vec::new();
                            args625.push(e.get("pressed")?);
                            fun627.call(args625, kw626)?
                        });
                        args622.push({
                            let mut s = Vec::new();
                            s.push(Val::Int(1i64));
                            s.push(unary("neg", Val::Float(1.8f64))?);
                            s.push(Val::Float(0.67f64));
                            Val::tuple(s)
                        });
                        args622.push({
                            let mut s = Vec::new();
                            s.push(Val::Int(0i64));
                            s.push(unary("neg", Val::Int(78i64))?);
                            s.push(Val::Int(119i64));
                            Val::tuple(s)
                        });
                        args622.push(Val::Int(140i64));
                        fun624.call(args622, kw623)?
                    };
                }
            }
            {
                let fun631 = e.get("render")?;
                let mut args629 = Vec::new();
                let mut kw630 = Vec::new();
                fun631.call(args629, kw630)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun634 = e.get("main")?;
        let mut args632 = Vec::new();
        let mut kw633 = Vec::new();
        fun634.call(args632, kw633)?
    };
    Ok(Val::None)
}
