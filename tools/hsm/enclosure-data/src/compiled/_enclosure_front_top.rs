//! Private front-top numeric records; native builders retain their existing readers.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("contextlib")?;
    e.set("contextmanager", rt.member("contextlib", "contextmanager")?)?;
    e.set("ExitStack", rt.member("contextlib", "ExitStack")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set(
        "_enclosure_structure",
        rt.import_module("_enclosure_structure")?,
    )?;
    let mod2 = rt.import_module("_enclosure_panel")?;
    e.set("_Graph", rt.member("_enclosure_panel", "_Graph")?)?;
    e.set("_record", rt.member("_enclosure_panel", "_record")?)?;
    let mod3 = rt.import_module("_enclosure_back_top")?;
    e.set(
        "_shared_leaves",
        rt.member("_enclosure_back_top", "_leaves")?,
    )?;
    e.set("_replace", rt.member("_enclosure_back_top", "_replace")?)?;
    e.set("_rounded", rt.member("_enclosure_back_top", "_rounded")?)?;
    e.set("_placed", rt.member("_enclosure_back_top", "_placed")?)?;
    e.set(
        "_funnel_containment",
        rt.member("_enclosure_back_top", "_funnel_containment")?,
    )?;
    // _corner_numbers
    e.set("_corner_numbers",{let params=vec![("shell".into(),None,false),("outer".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("json",rt.import_module("json")?)?;
let mod4=rt.import_module("pathlib")?;e.set("Path",rt.member("pathlib","Path")?)?;
let assigned5={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun8=e.get("json")?.attr("loads")?;let mut args6=Vec::new();let mut kw7=Vec::new();args6.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun11={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun14={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun17=e.get("Path")?;let mut args15=Vec::new();let mut kw16=Vec::new();args15.push(e.get("__file__")?);fun17.call(args15,kw16)?}}.attr("with_name")?;let mut args12=Vec::new();let mut kw13=Vec::new();args12.push(Val::Str("front-corner-controls.json".into()));fun14.call(args12,kw13)?}}.attr("read_text")?;let mut args9=Vec::new();let mut kw10=Vec::new();fun11.call(args9,kw10)?}});fun8.call(args6,kw7)?}};e.set("asset",assigned5.clone())?;
let assigned18=e.get("shell")?.attr("_swept_top")?;e.set("swept",assigned18.clone())?;
let assigned19={let d=Val::dict(vec![]);d.set(Val::Str("front_radius_mm".into()),e.get("swept")?.attr("FRONT_RADIUS")?)?;d.set(Val::Str("side_radius_mm".into()),e.get("swept")?.attr("SIDE_RADIUS")?)?;d.set(Val::Str("top_radius_mm".into()),e.get("swept")?.attr("TOP_RADIUS")?)?;d.set(Val::Str("angle_deg".into()),e.get("swept")?.attr("ANGLE")?)?;d.set(Val::Str("display_flat_mm".into()),e.get("swept")?.attr("FLAT")?)?;d};e.set("current",assigned19.clone())?;
if {let v22={let v23=e.get("current")?;let v24=e.get("asset")?.get(Val::Str("domain".into()))?;Val::Bool(compare("ne",v23.clone(),v24.clone())?.truthy()?)};if v22.truthy()? {v22} else {{let v20=binary("sub",e.get("outer")?.get(Val::Int(1i64))?,e.get("outer")?.get(Val::Int(0i64))?)?;let v21=binary("mul",Val::Int(4i64),e.get("swept")?.attr("FRONT_RADIUS")?)?;Val::Bool(compare("le",v20.clone(),v21.clone())?.truthy()?)}}}.truthy()? {
anyhow::bail!("{}",val_string({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun27=e.get("ValueError")?;let mut args25=Vec::new();let mut kw26=Vec::new();args25.push(Val::Str("the front corner is outside its retained analytic parameter domain".into()));fun27.call(args25,kw26)?}})?);
}
let assigned28={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun31=e.get("swept")?.attr("profile")?;let mut args29=Vec::new();let mut kw30=Vec::new();args29.push(e.get("outer")?);fun31.call(args29,kw30)?}}.get(Val::Str("foot".into()))?.get(Val::Int(1i64))?;e.set("foot",assigned28.clone())?;
return Ok({let d=Val::dict(vec![]);d.set(Val::Str("surfaces".into()),e.get("asset")?.get(Val::Str("surfaces".into()))?)?;d.set(Val::Str("scale_mm".into()),e.get("swept")?.attr("SIDE_RADIUS")?)?;d.set(Val::Str("frames".into()),{let mut s=Vec::new();s.push({let d=Val::dict(vec![]);d.set(Val::Str("origin".into()),{let mut s=Vec::new();s.push(binary("add",e.get("outer")?.get(Val::Int(0i64))?,e.get("swept")?.attr("FRONT_RADIUS")?)?);s.push(binary("add",e.get("outer")?.get(Val::Int(2i64))?,e.get("swept")?.attr("FRONT_RADIUS")?)?);s.push(e.get("foot")?);Val::tuple(s)})?;d.set(Val::Str("x_sign".into()),unary("neg",Val::Float(1.0f64))?)?;d});s.push({let d=Val::dict(vec![]);d.set(Val::Str("origin".into()),{let mut s=Vec::new();s.push(binary("sub",e.get("outer")?.get(Val::Int(1i64))?,e.get("swept")?.attr("FRONT_RADIUS")?)?);s.push(binary("add",e.get("outer")?.get(Val::Int(2i64))?,e.get("swept")?.attr("FRONT_RADIUS")?)?);s.push(e.get("foot")?);Val::tuple(s)})?;d.set(Val::Str("x_sign".into()),Val::Float(1.0f64))?;d});Val::list(s)})?;d});
Ok(Val::None)})})?;
    // can_cut
    e.set("can_cut", {
        let params = vec![("shell".into(), None, false), ("box".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let attempt32 = (|| -> Result<Flow> {
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                        line!(),
                    );
                    {
                        let fun36 = e.get("_corner_numbers")?;
                        let mut args34 = Vec::new();
                        let mut kw35 = Vec::new();
                        args34.push(e.get("shell")?);
                        args34.push(e.get("box")?.attr("outer")?);
                        fun36.call(args34, kw35)?
                    }
                };
                Ok(Flow::Continue)
            })();
            let outcome33 = (|| -> Result<Flow> {
                match attempt32 {
                    Ok(Flow::Return(value)) => Ok(Flow::Return(value)),
                    Ok(Flow::Continue) => Ok(Flow::Continue),
                    Err(error) => {
                        return Ok(Flow::Return(Val::Bool(false)));
                        Ok(Flow::Continue)
                    }
                }
            })();
            match outcome33? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
            }
            return Ok(Val::Bool(true));
            Ok(Val::None)
        })
    })?;
    // _halfspace
    e.set("_halfspace", {
        let params = vec![
            ("graph".into(), None, false),
            ("origin".into(), None, false),
            ("normal".into(), None, false),
            ("extent".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v40 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                        line!(),
                    );
                    {
                        let fun39 = e.get("abs")?;
                        let mut args37 = Vec::new();
                        let mut kw38 = Vec::new();
                        args37.push(e.get("normal")?.get(Val::Int(0i64))?);
                        fun39.call(args37, kw38)?
                    }
                };
                let v41 = Val::Float(1e-10f64);
                Val::Bool(compare("gt", v40.clone(), v41.clone())?.truthy()?)
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun44 = e.get("ValueError")?;
                            let mut args42 = Vec::new();
                            let mut kw43 = Vec::new();
                            args42.push(Val::Str(
                                "the front display plane no longer has its declared X direction"
                                    .into(),
                            ));
                            fun44.call(args42, kw43)?
                        }
                    })?
                );
            }
            let assigned45 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun48 = e.get("math")?.attr("sqrt")?;
                    let mut args46 = Vec::new();
                    let mut kw47 = Vec::new();
                    args46.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun51 = e.get("sum")?;
                            let mut args49 = Vec::new();
                            let mut kw50 = Vec::new();
                            args49.push({
                                let e = e.child();
                                let out52 = Val::list(vec![]);
                                for item53 in e.get("normal")?.iter()? {
                                    e.set("v", item53)?;
                                    out52.attr("append")?.call(
                                        vec![binary("mul", e.get("v")?, e.get("v")?)?],
                                        vec![],
                                    )?;
                                }
                                out52
                            });
                            fun51.call(args49, kw50)?
                        }
                    });
                    fun48.call(args46, kw47)?
                }
            };
            e.set("length", assigned45.clone())?;
            let assigned54 = {
                let mut s = Vec::new();
                s.push(binary(
                    "truediv",
                    e.get("normal")?.get(Val::Int(1i64))?,
                    e.get("length")?,
                )?);
                s.push(binary(
                    "truediv",
                    e.get("normal")?.get(Val::Int(2i64))?,
                    e.get("length")?,
                )?);
                Val::tuple(s)
            };
            let unpack55 = unpack(assigned54.clone(), 2)?;
            e.set("ny", unpack55[0].clone())?;
            e.set("nz", unpack55[1].clone())?;
            let assigned56 = {
                let e = e.child();
                let out57 = Val::list(vec![]);
                for item58 in {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "mul",
                            unary("neg", Val::Int(2i64))?,
                            e.get("extent")?,
                        )?);
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("mul", Val::Int(2i64), e.get("extent")?)?);
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("mul", Val::Int(2i64), e.get("extent")?)?);
                        s.push(e.get("extent")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "mul",
                            unary("neg", Val::Int(2i64))?,
                            e.get("extent")?,
                        )?);
                        s.push(e.get("extent")?);
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                }
                .iter()?
                {
                    let unpack59 = unpack(item58, 2)?;
                    e.set("s", unpack59[0].clone())?;
                    e.set("d", unpack59[1].clone())?;
                    out57.attr("append")?.call(
                        vec![{
                            let mut s = Vec::new();
                            s.push(binary(
                                "add",
                                binary(
                                    "add",
                                    e.get("origin")?.get(Val::Int(1i64))?,
                                    binary("mul", e.get("s")?, e.get("nz")?)?,
                                )?,
                                binary("mul", e.get("d")?, e.get("ny")?)?,
                            )?);
                            s.push(binary(
                                "add",
                                binary(
                                    "sub",
                                    e.get("origin")?.get(Val::Int(2i64))?,
                                    binary("mul", e.get("s")?, e.get("ny")?)?,
                                )?,
                                binary("mul", e.get("d")?, e.get("nz")?)?,
                            )?);
                            Val::tuple(s)
                        }],
                        vec![],
                    )?;
                }
                out57
            };
            e.set("section", assigned56.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun62 = e.get("graph")?.attr("prism")?;
                    let mut args60 = Vec::new();
                    let mut kw61 = Vec::new();
                    args60.push(Val::Int(0i64));
                    args60.push(binary(
                        "sub",
                        e.get("origin")?.get(Val::Int(0i64))?,
                        binary("mul", Val::Int(2i64), e.get("extent")?)?,
                    )?);
                    args60.push(binary(
                        "add",
                        e.get("origin")?.get(Val::Int(0i64))?,
                        binary("mul", Val::Int(2i64), e.get("extent")?)?,
                    )?);
                    args60.push(e.get("section")?);
                    fun62.call(args60, kw61)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // _display_frame
    e.set("_display_frame", {
        let params = vec![("shell".into(), None, false), ("outer".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned63 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun66 = e.get("shell")?.attr("_facet_geom")?;
                    let mut args64 = Vec::new();
                    let mut kw65 = Vec::new();
                    args64.push(e.get("outer")?);
                    fun66.call(args64, kw65)?
                }
            };
            let unpack67 = unpack(assigned63.clone(), 5)?;
            e.set("_", unpack67[0].clone())?;
            e.set("normal", unpack67[1].clone())?;
            e.set("origin", unpack67[2].clone())?;
            e.set("_", unpack67[3].clone())?;
            e.set("_", unpack67[4].clone())?;
            if {
                let v71 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                        line!(),
                    );
                    {
                        let fun70 = e.get("abs")?;
                        let mut args68 = Vec::new();
                        let mut kw69 = Vec::new();
                        args68.push(e.get("normal")?.get(Val::Int(0i64))?);
                        fun70.call(args68, kw69)?
                    }
                };
                let v72 = Val::Float(1e-10f64);
                Val::Bool(compare("gt", v71.clone(), v72.clone())?.truthy()?)
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun75 = e.get("ValueError")?;
                            let mut args73 = Vec::new();
                            let mut kw74 = Vec::new();
                            args73.push(Val::Str(
                                "the front display plane no longer has its declared X direction"
                                    .into(),
                            ));
                            fun75.call(args73, kw74)?
                        }
                    })?
                );
            }
            let assigned76 = e.get("normal")?;
            let unpack77 = unpack(assigned76.clone(), 3)?;
            e.set("_", unpack77[0].clone())?;
            e.set("ny", unpack77[1].clone())?;
            e.set("nz", unpack77[2].clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("rotation".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(1.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(e.get("nz")?);
                        s.push(e.get("ny")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(unary("neg", e.get("ny")?)?);
                        s.push(e.get("nz")?);
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                })?;
                d.set(Val::Str("translation_mm".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun80 = e.get("shell")?.attr("display_centre_x")?;
                            let mut args78 = Vec::new();
                            let mut kw79 = Vec::new();
                            args78.push(e.get("outer")?);
                            fun80.call(args78, kw79)?
                        }
                    });
                    s.push(e.get("origin")?.get(Val::Int(1i64))?);
                    s.push(e.get("origin")?.get(Val::Int(2i64))?);
                    Val::tuple(s)
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // _display_exits
    e.set("_display_exits", {
        let params = vec![
            ("graph".into(), None, false),
            ("wing".into(), None, false),
            ("depth".into(), None, false),
            ("inset".into(), Some(Val::Float(0.0f64)), false),
            ("roof_drop".into(), Some(Val::Float(0.0f64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned81 = binary(
                "sub",
                binary(
                    "add",
                    binary(
                        "add",
                        e.get("wing")?.attr("BACK")?,
                        e.get("wing")?.attr("WING_THICK")?,
                    )?,
                    e.get("wing")?.attr("BEARING_AIR")?,
                )?,
                e.get("roof_drop")?,
            )?;
            e.set("roof", assigned81.clone())?;
            let assigned82 = binary("mul", unary("neg", e.get("depth")?)?, {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun85 = e.get("math")?.attr("tan")?;
                    let mut args83 = Vec::new();
                    let mut kw84 = Vec::new();
                    args83.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun88 = e.get("math")?.attr("radians")?;
                            let mut args86 = Vec::new();
                            let mut kw87 = Vec::new();
                            args86.push(e.get("wing")?.attr("ANGLE")?);
                            fun88.call(args86, kw87)?
                        }
                    });
                    fun85.call(args83, kw84)?
                }
            })?;
            e.set("shift", assigned82.clone())?;
            let assigned89 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("out", assigned89.clone())?;
            for item90 in {
                let mut s = Vec::new();
                s.push(unary("neg", Val::Int(1i64))?);
                s.push(Val::Int(1i64));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("side", item90)?;
                let assigned91 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                        line!(),
                    );
                    {
                        let fun94 = e.get("sorted")?;
                        let mut args92 = Vec::new();
                        let mut kw93 = Vec::new();
                        args92.push({
                            let mut s = Vec::new();
                            s.push(binary(
                                "mul",
                                e.get("side")?,
                                binary(
                                    "sub",
                                    binary(
                                        "truediv",
                                        e.get("wing")?.attr("COVER_X")?,
                                        Val::Int(2i64),
                                    )?,
                                    Val::Float(0.1f64),
                                )?,
                            )?);
                            s.push(binary(
                                "mul",
                                e.get("side")?,
                                binary(
                                    "add",
                                    binary(
                                        "add",
                                        binary(
                                            "truediv",
                                            e.get("wing")?.attr("COVER_X")?,
                                            Val::Int(2i64),
                                        )?,
                                        e.get("wing")?.attr("WING_REACH")?,
                                    )?,
                                    e.get("wing")?.attr("TIP_AIR")?,
                                )?,
                            )?);
                            Val::tuple(s)
                        });
                        fun94.call(args92, kw93)?
                    }
                };
                let unpack95 = unpack(assigned91.clone(), 2)?;
                e.set("xa", unpack95[0].clone())?;
                e.set("xb", unpack95[1].clone())?;
                let assigned96 = {
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        binary(
                            "sub",
                            binary(
                                "truediv",
                                unary("neg", e.get("wing")?.attr("WING_SPAN")?)?,
                                Val::Int(2i64),
                            )?,
                            e.get("wing")?.attr("END_AIR")?,
                        )?,
                        e.get("inset")?,
                    )?);
                    s.push(binary(
                        "sub",
                        binary(
                            "add",
                            binary("truediv", e.get("wing")?.attr("WING_SPAN")?, Val::Int(2i64))?,
                            e.get("wing")?.attr("END_AIR")?,
                        )?,
                        e.get("inset")?,
                    )?);
                    Val::tuple(s)
                };
                let unpack97 = unpack(assigned96.clone(), 2)?;
                e.set("y0", unpack97[0].clone())?;
                e.set("y1", unpack97[1].clone())?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                        line!(),
                    );
                    {
                        let fun100 = e.get("out")?.attr("append")?;
                        let mut args98 = Vec::new();
                        let mut kw99 = Vec::new();
                        args98.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                                line!(),
                            );
                            {
                                let fun103 = e.get("graph")?.attr("prism")?;
                                let mut args101 = Vec::new();
                                let mut kw102 = Vec::new();
                                args101.push(Val::Int(0i64));
                                args101.push(binary("add", e.get("xa")?, e.get("inset")?)?);
                                args101.push(binary("sub", e.get("xb")?, e.get("inset")?)?);
                                args101.push({
                                    let mut s = Vec::new();
                                    s.push({
                                        let mut s = Vec::new();
                                        s.push(e.get("y0")?);
                                        s.push(e.get("roof")?);
                                        Val::tuple(s)
                                    });
                                    s.push({
                                        let mut s = Vec::new();
                                        s.push(binary("add", e.get("y0")?, e.get("shift")?)?);
                                        s.push(binary("sub", e.get("roof")?, e.get("depth")?)?);
                                        Val::tuple(s)
                                    });
                                    s.push({
                                        let mut s = Vec::new();
                                        s.push(binary("add", e.get("y1")?, e.get("shift")?)?);
                                        s.push(binary("sub", e.get("roof")?, e.get("depth")?)?);
                                        Val::tuple(s)
                                    });
                                    s.push({
                                        let mut s = Vec::new();
                                        s.push(e.get("y1")?);
                                        s.push(e.get("roof")?);
                                        Val::tuple(s)
                                    });
                                    Val::tuple(s)
                                });
                                fun103.call(args101, kw102)?
                            }
                        });
                        fun100.call(args98, kw99)?
                    }
                };
            }
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    // _display_cut
    e.set("_display_cut",{let params=vec![("shell".into(),None,false),("graph".into(),None,false),("outer".into(),None,false),("support_floor".into(),Some(Val::None),false),("support_fore".into(),Some(Val::None),false),("extend_wing_exits".into(),Some(Val::Bool(true)),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("layout",rt.import_module("above_core")?)?;
let assigned104=e.get("shell")?.attr("_display_wings")?;e.set("wing",assigned104.clone())?;
let assigned105={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun108=e.get("_display_frame")?;let mut args106=Vec::new();let mut kw107=Vec::new();args106.push(e.get("shell")?);args106.push(e.get("outer")?);fun108.call(args106,kw107)?}};e.set("frame",assigned105.clone())?;
let assigned109={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun112=e.get("shell")?.attr("_display_cut_exit_depth")?;let mut args110=Vec::new();let mut kw111=Vec::new();fun112.call(args110,kw111)?}};e.set("canonical",assigned109.clone())?;
let assigned113={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun116=e.get("wing")?.attr("cuts")?;let mut args114=Vec::new();let mut kw115=Vec::new();args114.push(binary("add",e.get("shell")?.attr("display_facet_thickness")?,e.get("shell")?.attr("display_pcb_cut_through")?)?);args114.push(e.get("canonical")?);fun116.call(args114,kw115)?}};e.set("local",assigned113.clone())?;
let assigned117=e.get("shell")?.attr("_interface")?.attr("display_inset_corner_r")?;e.set("radius",assigned117.clone())?;
let assigned118={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun121=e.get("_rounded")?;let mut args119=Vec::new();let mut kw120=Vec::new();args119.push(e.get("graph")?);args119.push(Val::Int(2i64));args119.push({let mut s=Vec::new();s.push(binary("truediv",unary("neg",e.get("shell")?.attr("display_inset_x")?)?,Val::Int(2i64))?);s.push(binary("truediv",e.get("shell")?.attr("display_inset_x")?,Val::Int(2i64))?);s.push(binary("truediv",unary("neg",e.get("shell")?.attr("display_inset_slope")?)?,Val::Int(2i64))?);s.push(binary("truediv",e.get("shell")?.attr("display_inset_slope")?,Val::Int(2i64))?);s.push(unary("neg",e.get("shell")?.attr("display_facet_thickness")?)?);s.push(unary("neg",e.get("shell")?.attr("display_inset_depth")?)?);Val::tuple(s)});args119.push(e.get("radius")?);fun121.call(args119,kw120)?}};e.set("below",assigned118.clone())?;
for item122 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun125=e.get("wing")?.attr("support_exits")?;let mut args123=Vec::new();let mut kw124=Vec::new();args123.push(e.get("canonical")?);fun125.call(args123,kw124)?}}.iter()? {
e.set("exit",item122)?;let assigned126={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun129=e.get("local")?.attr("fuse")?;let mut args127=Vec::new();let mut kw128=Vec::new();args127.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun132=e.get("below")?.attr("intersect")?;let mut args130=Vec::new();let mut kw131=Vec::new();args130.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun135=e.get("exit")?.attr("translate")?;let mut args133=Vec::new();let mut kw134=Vec::new();args133.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(unary("neg",e.get("radius")?)?);s.push(Val::Float(0.0f64));Val::tuple(s)});fun135.call(args133,kw134)?}});fun132.call(args130,kw131)?}});fun129.call(args127,kw128)?}};e.set("local",assigned126.clone())?;
}
let assigned136={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun139=e.get("_placed")?;let mut args137=Vec::new();let mut kw138=Vec::new();args137.push(e.get("graph")?);args137.push(e.get("local")?);args137.push(e.get("frame")?);fun139.call(args137,kw138)?}};e.set("result",assigned136.clone())?;
if {let v140={let v141=e.get("support_floor")?;let v142=Val::None;Val::Bool(compare("is_not",v141.clone(),v142.clone())?.truthy()?)};if v140.truthy()? {e.get("extend_wing_exits")?} else {v140}}.truthy()? {
let assigned143={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun146=e.get("graph")?.attr("box")?;let mut args144=Vec::new();let mut kw145=Vec::new();args144.push(binary("sub",e.get("outer")?.get(Val::Int(0i64))?,Val::Int(1i64))?);args144.push(binary("add",e.get("outer")?.get(Val::Int(1i64))?,Val::Int(1i64))?);args144.push(binary("sub",e.get("outer")?.get(Val::Int(2i64))?,Val::Int(1i64))?);args144.push(binary("add",e.get("outer")?.get(Val::Int(3i64))?,Val::Int(1i64))?);args144.push(e.get("support_floor")?);args144.push(binary("add",e.get("outer")?.get(Val::Int(5i64))?,Val::Int(1i64))?);fun146.call(args144,kw145)?}};e.set("room",assigned143.clone())?;
if {let v147=e.get("support_fore")?;let v148=Val::None;Val::Bool(compare("is_not",v147.clone(),v148.clone())?.truthy()?)}.truthy()? {
let assigned149=binary("add",binary("add",e.get("wing")?.attr("BACK")?,e.get("wing")?.attr("WING_THICK")?)?,e.get("wing")?.attr("BEARING_AIR")?)?;e.set("roof",assigned149.clone())?;
let assigned150={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun153=e.get("layout")?.attr("point")?;let mut args151=Vec::new();let mut kw152=Vec::new();args151.push(e.get("frame")?);args151.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(binary("sub",binary("add",binary("truediv",e.get("wing")?.attr("WING_SPAN")?,Val::Int(2i64))?,e.get("wing")?.attr("END_AIR")?)?,binary("mul",e.get("canonical")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun156=e.get("math")?.attr("tan")?;let mut args154=Vec::new();let mut kw155=Vec::new();args154.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun159=e.get("math")?.attr("radians")?;let mut args157=Vec::new();let mut kw158=Vec::new();args157.push(e.get("wing")?.attr("ANGLE")?);fun159.call(args157,kw158)?}});fun156.call(args154,kw155)?}})?)?);s.push(binary("sub",e.get("roof")?,e.get("canonical")?)?);Val::tuple(s)});fun153.call(args151,kw152)?}};e.set("aft",assigned150.clone())?;
let assigned160={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun163=e.get("max")?;let mut args161=Vec::new();let mut kw162=Vec::new();args161.push(Val::Float(0.0f64));args161.push(binary("sub",e.get("aft")?.get(Val::Int(1i64))?,e.get("support_fore")?)?);fun163.call(args161,kw162)?}};e.set("run",assigned160.clone())?;
let assigned164={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun167=e.get("room")?.attr("intersect")?;let mut args165=Vec::new();let mut kw166=Vec::new();args165.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun170=e.get("graph")?.attr("prism")?;let mut args168=Vec::new();let mut kw169=Vec::new();args168.push(Val::Int(0i64));args168.push(binary("sub",e.get("outer")?.get(Val::Int(0i64))?,Val::Int(1i64))?);args168.push(binary("add",e.get("outer")?.get(Val::Int(1i64))?,Val::Int(1i64))?);args168.push({let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(binary("sub",e.get("outer")?.get(Val::Int(2i64))?,Val::Int(1i64))?);s.push(e.get("support_floor")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("support_fore")?);s.push(e.get("support_floor")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("support_fore")?);s.push(binary("sub",e.get("aft")?.get(Val::Int(2i64))?,e.get("run")?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("aft")?.get(Val::Int(1i64))?);s.push(e.get("aft")?.get(Val::Int(2i64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("add",e.get("outer")?.get(Val::Int(3i64))?,Val::Int(1i64))?);s.push(e.get("aft")?.get(Val::Int(2i64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("add",e.get("outer")?.get(Val::Int(3i64))?,Val::Int(1i64))?);s.push(binary("add",e.get("outer")?.get(Val::Int(5i64))?,Val::Int(1i64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("sub",e.get("outer")?.get(Val::Int(2i64))?,Val::Int(1i64))?);s.push(binary("add",e.get("outer")?.get(Val::Int(5i64))?,Val::Int(1i64))?);Val::tuple(s)});Val::tuple(s)});fun170.call(args168,kw169)?}});fun167.call(args165,kw166)?}};e.set("room",assigned164.clone())?;
}
for item171 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun174=e.get("wing")?.attr("support_exits")?;let mut args172=Vec::new();let mut kw173=Vec::new();args172.push(Val::Int(250i64));fun174.call(args172,kw173)?}}.iter()? {
e.set("exit",item171)?;let assigned175={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun178=e.get("result")?.attr("fuse")?;let mut args176=Vec::new();let mut kw177=Vec::new();args176.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun181={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun184=e.get("_placed")?;let mut args182=Vec::new();let mut kw183=Vec::new();args182.push(e.get("graph")?);args182.push(e.get("exit")?);args182.push(e.get("frame")?);fun184.call(args182,kw183)?}}.attr("intersect")?;let mut args179=Vec::new();let mut kw180=Vec::new();args179.push(e.get("room")?);fun181.call(args179,kw180)?}});fun178.call(args176,kw177)?}};e.set("result",assigned175.clone())?;
}
}
return Ok(e.get("result")?);
Ok(Val::None)})})?;
    // _valve_body
    e.set("_valve_body", {
        let params = vec![("shell".into(), None, false), ("graph".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned185 = e.get("shell")?.attr("_valve_tray")?;
            e.set("tray", assigned185.clone())?;
            let assigned186 = {
                let mut s = Vec::new();
                s.push(e.get("tray")?.attr("_valve")?);
                s.push(e.get("tray")?.attr("_seat")?);
                s.push(e.get("tray")?.attr("PORT_SLIP")?);
                Val::tuple(s)
            };
            let unpack187 = unpack(assigned186.clone(), 3)?;
            e.set("valve", unpack187[0].clone())?;
            e.set("seat", unpack187[1].clone())?;
            e.set("slip", unpack187[2].clone())?;
            // cylinder
            e.set("cylinder", {
                let params = vec![
                    ("radius".into(), None, false),
                    ("z0".into(), None, false),
                    ("z1".into(), None, false),
                    ("x".into(), Some(Val::Float(0.0f64)), false),
                    ("y".into(), Some(Val::Float(0.0f64)), false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    return Ok({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun190 = e.get("graph")?.attr("cylinder")?;
                            let mut args188 = Vec::new();
                            let mut kw189 = Vec::new();
                            args188.push(Val::Int(2i64));
                            args188.push(e.get("radius")?);
                            args188.push(e.get("x")?);
                            args188.push(e.get("y")?);
                            args188.push(e.get("z0")?);
                            args188.push(e.get("z1")?);
                            fun190.call(args188, kw189)?
                        }
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned191 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun194 = e.get("cylinder")?;
                    let mut args192 = Vec::new();
                    let mut kw193 = Vec::new();
                    args192.push(binary(
                        "add",
                        e.get("valve")?.attr("bearing_radius")?,
                        e.get("slip")?,
                    )?);
                    args192.push(e.get("seat")?.attr("seat_top_z")?);
                    args192.push(binary(
                        "add",
                        e.get("valve")?
                            .attr("bearing_z_range")?
                            .get(Val::Int(1i64))?,
                        e.get("slip")?,
                    )?);
                    fun194.call(args192, kw193)?
                }
            };
            e.set("body", assigned191.clone())?;
            let assigned195 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun198 = e.get("body")?.attr("fuse")?;
                    let mut args196 = Vec::new();
                    let mut kw197 = Vec::new();
                    args196.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun201 = e.get("cylinder")?;
                            let mut args199 = Vec::new();
                            let mut kw200 = Vec::new();
                            args199.push(binary(
                                "add",
                                e.get("valve")?.attr("body_radius")?,
                                e.get("slip")?,
                            )?);
                            args199.push(binary(
                                "sub",
                                e.get("valve")?
                                    .attr("body_main_z_range")?
                                    .get(Val::Int(0i64))?,
                                e.get("slip")?,
                            )?);
                            args199.push(binary(
                                "add",
                                e.get("valve")?
                                    .attr("body_main_z_range")?
                                    .get(Val::Int(1i64))?,
                                e.get("slip")?,
                            )?);
                            fun201.call(args199, kw200)?
                        }
                    });
                    fun198.call(args196, kw197)?
                }
            };
            e.set("body", assigned195.clone())?;
            for item202 in {
                let mut s = Vec::new();
                s.push(unary("neg", Val::Float(1.0f64))?);
                s.push(Val::Float(1.0f64));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("sx", item202)?;
                for item203 in {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(1.0f64))?);
                    s.push(Val::Float(1.0f64));
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("sy", item203)?;
                    let assigned204 = {
                        let mut s = Vec::new();
                        s.push(binary(
                            "mul",
                            e.get("sx")?,
                            e.get("seat")?.attr("corner_inset_x")?,
                        )?);
                        s.push(binary(
                            "mul",
                            e.get("sy")?,
                            e.get("seat")?.attr("corner_inset_y")?,
                        )?);
                        Val::tuple(s)
                    };
                    let unpack205 = unpack(assigned204.clone(), 2)?;
                    e.set("x", unpack205[0].clone())?;
                    e.set("y", unpack205[1].clone())?;
                    let assigned206 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun209 = e.get("body")?.attr("fuse")?;
                            let mut args207 = Vec::new();
                            let mut kw208 = Vec::new();
                            args207.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                                    line!(),
                                );
                                {
                                    let fun212 = e.get("cylinder")?;
                                    let mut args210 = Vec::new();
                                    let mut kw211 = Vec::new();
                                    args210.push(binary(
                                        "add",
                                        e.get("valve")?.attr("corner_boss_radius")?,
                                        e.get("slip")?,
                                    )?);
                                    args210.push(e.get("seat")?.attr("seat_top_z")?);
                                    args210.push(binary(
                                        "add",
                                        e.get("valve")?.attr("post_shoulder_z")?,
                                        e.get("slip")?,
                                    )?);
                                    args210.push(e.get("x")?);
                                    args210.push(e.get("y")?);
                                    fun212.call(args210, kw211)?
                                }
                            });
                            fun209.call(args207, kw208)?
                        }
                    };
                    e.set("body", assigned206.clone())?;
                    let assigned213 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun216 = e.get("body")?.attr("fuse")?;
                            let mut args214 = Vec::new();
                            let mut kw215 = Vec::new();
                            args214.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                                    line!(),
                                );
                                {
                                    let fun219 = e.get("cylinder")?;
                                    let mut args217 = Vec::new();
                                    let mut kw218 = Vec::new();
                                    args217.push(binary(
                                        "add",
                                        e.get("valve")?.attr("upper_corner_radius")?,
                                        e.get("slip")?,
                                    )?);
                                    args217.push(binary(
                                        "sub",
                                        e.get("valve")?.attr("post_shoulder_z")?,
                                        e.get("slip")?,
                                    )?);
                                    args217.push(binary(
                                        "add",
                                        e.get("valve")?.attr("body_top_z")?,
                                        e.get("slip")?,
                                    )?);
                                    args217.push(e.get("x")?);
                                    args217.push(e.get("y")?);
                                    fun219.call(args217, kw218)?
                                }
                            });
                            fun216.call(args214, kw215)?
                        }
                    };
                    e.set("body", assigned213.clone())?;
                }
            }
            let assigned220 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun223 = e.get("_rounded")?;
                    let mut args221 = Vec::new();
                    let mut kw222 = Vec::new();
                    args221.push(e.get("graph")?);
                    args221.push(Val::Int(2i64));
                    args221.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "sub",
                            binary(
                                "truediv",
                                unary("neg", e.get("valve")?.attr("cap_width_x")?)?,
                                Val::Int(2i64),
                            )?,
                            e.get("slip")?,
                        )?);
                        s.push(binary(
                            "add",
                            binary(
                                "truediv",
                                e.get("valve")?.attr("cap_width_x")?,
                                Val::Int(2i64),
                            )?,
                            e.get("slip")?,
                        )?);
                        s.push(binary(
                            "sub",
                            binary(
                                "truediv",
                                unary("neg", e.get("valve")?.attr("cap_depth_y")?)?,
                                Val::Int(2i64),
                            )?,
                            e.get("slip")?,
                        )?);
                        s.push(binary(
                            "add",
                            binary(
                                "truediv",
                                e.get("valve")?.attr("cap_depth_y")?,
                                Val::Int(2i64),
                            )?,
                            e.get("slip")?,
                        )?);
                        s.push(binary(
                            "sub",
                            e.get("valve")?
                                .attr("top_box_z_range")?
                                .get(Val::Int(0i64))?,
                            e.get("slip")?,
                        )?);
                        s.push(binary(
                            "add",
                            binary(
                                "add",
                                e.get("valve")?
                                    .attr("top_box_z_range")?
                                    .get(Val::Int(0i64))?,
                                e.get("valve")?.attr("top_box_height")?,
                            )?,
                            e.get("slip")?,
                        )?);
                        Val::tuple(s)
                    });
                    args221.push(binary(
                        "add",
                        e.get("valve")?.attr("cap_corner_radius")?,
                        e.get("slip")?,
                    )?);
                    fun223.call(args221, kw222)?
                }
            };
            e.set("cap", assigned220.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun226 = e.get("body")?.attr("fuse")?;
                    let mut args224 = Vec::new();
                    let mut kw225 = Vec::new();
                    args224.push(e.get("cap")?);
                    fun226.call(args224, kw225)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // _teardrop
    e.set("_teardrop", {
        let params = vec![
            ("graph".into(), None, false),
            ("radius".into(), None, false),
            ("x".into(), None, false),
            ("z".into(), None, false),
            ("y0".into(), None, false),
            ("y1".into(), None, false),
            ("angle".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned227 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun230 = e.get("math")?.attr("radians")?;
                    let mut args228 = Vec::new();
                    let mut kw229 = Vec::new();
                    args228.push(e.get("angle")?);
                    fun230.call(args228, kw229)?
                }
            };
            e.set("a", assigned227.clone())?;
            let assigned231 = binary("mul", e.get("radius")?, {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun234 = e.get("math")?.attr("sin")?;
                    let mut args232 = Vec::new();
                    let mut kw233 = Vec::new();
                    args232.push(e.get("a")?);
                    fun234.call(args232, kw233)?
                }
            })?;
            e.set("half", assigned231.clone())?;
            let assigned235 = {
                let mut s = Vec::new();
                s.push(binary(
                    "add",
                    e.get("z")?,
                    binary("mul", e.get("radius")?, {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun238 = e.get("math")?.attr("cos")?;
                            let mut args236 = Vec::new();
                            let mut kw237 = Vec::new();
                            args236.push(e.get("a")?);
                            fun238.call(args236, kw237)?
                        }
                    })?,
                )?);
                s.push(binary(
                    "add",
                    e.get("z")?,
                    binary("truediv", e.get("radius")?, {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun241 = e.get("math")?.attr("cos")?;
                            let mut args239 = Vec::new();
                            let mut kw240 = Vec::new();
                            args239.push(e.get("a")?);
                            fun241.call(args239, kw240)?
                        }
                    })?,
                )?);
                Val::tuple(s)
            };
            let unpack242 = unpack(assigned235.clone(), 2)?;
            e.set("tangent", unpack242[0].clone())?;
            e.set("apex", unpack242[1].clone())?;
            let assigned243 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun246 = e.get("graph")?.attr("add")?;
                    let mut args244 = Vec::new();
                    let mut kw245 = Vec::new();
                    args244.push(Val::Str("cylinder".into()));
                    kw245.push(("axis".into(), Val::Int(1i64)));
                    kw245.push(("radius".into(), e.get("radius")?));
                    kw245.push(("centre".into(), {
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("z")?);
                        Val::tuple(s)
                    }));
                    kw245.push(("span".into(), {
                        let mut s = Vec::new();
                        s.push(e.get("y0")?);
                        s.push(e.get("y1")?);
                        Val::tuple(s)
                    }));
                    kw245.push(("stations".into(), {
                        let mut s = Vec::new();
                        s.push(binary(
                            "sub",
                            binary("truediv", e.get("math")?.attr("pi")?, Val::Int(2i64))?,
                            e.get("a")?,
                        )?);
                        s.push(binary(
                            "add",
                            binary("truediv", e.get("math")?.attr("pi")?, Val::Int(2i64))?,
                            e.get("a")?,
                        )?);
                        Val::tuple(s)
                    }));
                    kw245.push(("bounds".into(), {
                        let mut s = Vec::new();
                        s.push(binary("sub", e.get("x")?, e.get("radius")?)?);
                        s.push(binary("add", e.get("x")?, e.get("radius")?)?);
                        s.push(e.get("y0")?);
                        s.push(e.get("y1")?);
                        s.push(binary("sub", e.get("z")?, e.get("radius")?)?);
                        s.push(binary("add", e.get("z")?, e.get("radius")?)?);
                        Val::tuple(s)
                    }));
                    fun246.call(args244, kw245)?
                }
            };
            e.set("circle", assigned243.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun249 = e.get("circle")?.attr("fuse")?;
                    let mut args247 = Vec::new();
                    let mut kw248 = Vec::new();
                    args247.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun252 = e.get("graph")?.attr("prism")?;
                            let mut args250 = Vec::new();
                            let mut kw251 = Vec::new();
                            args250.push(Val::Int(1i64));
                            args250.push(e.get("y0")?);
                            args250.push(e.get("y1")?);
                            args250.push({
                                let mut s = Vec::new();
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(binary("sub", e.get("x")?, e.get("half")?)?);
                                    s.push(e.get("tangent")?);
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(binary("add", e.get("x")?, e.get("half")?)?);
                                    s.push(e.get("tangent")?);
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(e.get("x")?);
                                    s.push(e.get("apex")?);
                                    Val::tuple(s)
                                });
                                Val::tuple(s)
                            });
                            fun252.call(args250, kw251)?
                        }
                    });
                    fun249.call(args247, kw248)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // _stacked_towers
    e.set("_stacked_towers",{let params=vec![("graph".into(),None,false),("stock".into(),None,false),("inner".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);e.set("layout",rt.import_module("above_core")?)?;
let mod253=rt.import_module("itertools")?;e.set("product",rt.member("itertools","product")?)?;
let assigned254={let mut s=Vec::new();Val::list(s)};e.set("boxes",assigned254.clone())?;
// visit
e.set("visit",{let params=vec![("index".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned255=e.get("graph")?.attr("nodes")?.get(e.get("index")?)?;e.set("node",assigned255.clone())?;
if {let v256=e.get("node")?.get(Val::Str("op".into()))?;let v257=Val::Str("union".into());Val::Bool(compare("eq",v256.clone(),v257.clone())?.truthy()?)}.truthy()? {
for item258 in e.get("node")?.get(Val::Str("inputs".into()))?.iter()? {
e.set("child",item258)?;{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun261=e.get("visit")?;let mut args259=Vec::new();let mut kw260=Vec::new();args259.push(e.get("child")?);fun261.call(args259,kw260)?}};
}
return Ok(Val::None);
}
if {let v262=e.get("node")?.get(Val::Str("op".into()))?;let v263=Val::Str("placed".into());Val::Bool(compare("ne",v262.clone(),v263.clone())?.truthy()?)}.truthy()? {
anyhow::bail!("{}",val_string({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun266=e.get("ValueError")?;let mut args264=Vec::new();let mut kw265=Vec::new();args264.push(Val::Str("the front well tower requires its declared placed rectangular stock".into()));fun266.call(args264,kw265)?}})?);
}
let assigned267=e.get("graph")?.attr("nodes")?.get(e.get("node")?.get(Val::Str("inputs".into()))?.get(Val::Int(0i64))?)?;e.set("source",assigned267.clone())?;
if {let v268=e.get("source")?.get(Val::Str("op".into()))?;let v269=Val::Str("box".into());Val::Bool(compare("ne",v268.clone(),v269.clone())?.truthy()?)}.truthy()? {
anyhow::bail!("{}",val_string({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun272=e.get("ValueError")?;let mut args270=Vec::new();let mut kw271=Vec::new();args270.push(Val::Str("the front well tower requires its declared rectangular stock".into()));fun272.call(args270,kw271)?}})?);
}
let assigned273=e.get("node")?.get(Val::Str("frame".into()))?;e.set("frame",assigned273.clone())?;
if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun276=e.get("any")?;let mut args274=Vec::new();let mut kw275=Vec::new();args274.push({let e=e.child();let out277=Val::list(vec![]);for item278 in e.get("frame")?.get(Val::Str("rotation".into()))?.iter()? {e.set("row",item278)?;out277.attr("append")?.call(vec![{let v289={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun281=e.get("sum")?;let mut args279=Vec::new();let mut kw280=Vec::new();args279.push({let e=e.child();let out282=Val::list(vec![]);for item283 in e.get("row")?.iter()? {e.set("v",item283)?;out282.attr("append")?.call(vec![{let v287={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun286=e.get("abs")?;let mut args284=Vec::new();let mut kw285=Vec::new();args284.push(e.get("v")?);fun286.call(args284,kw285)?}};let v288=Val::Float(1e-08f64);Val::Bool(compare("gt",v287.clone(),v288.clone())?.truthy()?)}],vec![])?;}out282});fun281.call(args279,kw280)?}};let v290=Val::Int(1i64);Val::Bool(compare("ne",v289.clone(),v290.clone())?.truthy()?)}],vec![])?;}out277});fun276.call(args274,kw275)?}}.truthy()? {
anyhow::bail!("{}",val_string({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun293=e.get("ValueError")?;let mut args291=Vec::new();let mut kw292=Vec::new();args291.push(Val::Str("a front well is no longer aligned to the principal wall planes".into()));fun293.call(args291,kw292)?}})?);
}
let assigned294={let e=e.child();let out295=Val::list(vec![]);for item296 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun299=e.get("product")?;let mut args297=Vec::new();let mut kw298=Vec::new();args297.extend({let e=e.child();let out300=Val::list(vec![]);for item301 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun304=e.get("range")?;let mut args302=Vec::new();let mut kw303=Vec::new();args302.push(Val::Int(3i64));fun304.call(args302,kw303)?}}.iter()? {e.set("k",item301)?;out300.attr("append")?.call(vec![e.get("source")?.get(Val::Str("box".into()))?.get(Val::Slice{start:Some(binary("mul",Val::Int(2i64),e.get("k")?)?.integer()?),stop:Some(binary("add",binary("mul",Val::Int(2i64),e.get("k")?)?,Val::Int(2i64))?.integer()?),step:1})?],vec![])?;}out300}.iter()?);fun299.call(args297,kw298)?}}.iter()? {e.set("p",item296)?;out295.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun307=e.get("layout")?.attr("point")?;let mut args305=Vec::new();let mut kw306=Vec::new();args305.push(e.get("frame")?);args305.push(e.get("p")?);fun307.call(args305,kw306)?}}],vec![])?;}out295};e.set("points",assigned294.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun310=e.get("boxes")?.attr("append")?;let mut args308=Vec::new();let mut kw309=Vec::new();args308.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun313=e.get("tuple")?;let mut args311=Vec::new();let mut kw312=Vec::new();args311.push({let e=e.child();let out314=Val::list(vec![]);for item315 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun318=e.get("range")?;let mut args316=Vec::new();let mut kw317=Vec::new();args316.push(Val::Int(3i64));fun318.call(args316,kw317)?}}.iter()? {e.set("k",item315)?;for item319 in {let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun322=e.get("min")?;let mut args320=Vec::new();let mut kw321=Vec::new();args320.push({let e=e.child();let out323=Val::list(vec![]);for item324 in e.get("points")?.iter()? {e.set("p",item324)?;out323.attr("append")?.call(vec![e.get("p")?.get(e.get("k")?)?],vec![])?;}out323});fun322.call(args320,kw321)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun327=e.get("max")?;let mut args325=Vec::new();let mut kw326=Vec::new();args325.push({let e=e.child();let out328=Val::list(vec![]);for item329 in e.get("points")?.iter()? {e.set("p",item329)?;out328.attr("append")?.call(vec![e.get("p")?.get(e.get("k")?)?],vec![])?;}out328});fun327.call(args325,kw326)?}});Val::tuple(s)}.iter()? {e.set("v",item319)?;out314.attr("append")?.call(vec![e.get("v")?],vec![])?;}}out314});fun313.call(args311,kw312)?}});fun310.call(args308,kw309)?}};
Ok(Val::None)})})?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun332=e.get("visit")?;let mut args330=Vec::new();let mut kw331=Vec::new();args330.push(e.get("stock")?.attr("index")?);fun332.call(args330,kw331)?}};
let assigned333={let mut s=Vec::new();Val::list(s)};e.set("groups",assigned333.clone())?;
while e.get("boxes")?.truthy()? {
let assigned334={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun337=e.get("boxes")?.attr("pop")?;let mut args335=Vec::new();let mut kw336=Vec::new();fun337.call(args335,kw336)?}});Val::list(s)};e.set("group",assigned334.clone())?;
let assigned338=Val::Bool(true);e.set("changed",assigned338.clone())?;
while e.get("changed")?.truthy()? {
let assigned339=Val::Bool(false);e.set("changed",assigned339.clone())?;
for item340 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun343=e.get("range")?;let mut args341=Vec::new();let mut kw342=Vec::new();args341.push(binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun346=e.get("len")?;let mut args344=Vec::new();let mut kw345=Vec::new();args344.push(e.get("boxes")?);fun346.call(args344,kw345)?}},Val::Int(1i64))?);args341.push(unary("neg",Val::Int(1i64))?);args341.push(unary("neg",Val::Int(1i64))?);fun343.call(args341,kw342)?}}.iter()? {
e.set("i",item340)?;let assigned347=e.get("boxes")?.get(e.get("i")?)?;e.set("b",assigned347.clone())?;
if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun350=e.get("any")?;let mut args348=Vec::new();let mut kw349=Vec::new();args348.push({let e=e.child();let out351=Val::list(vec![]);for item352 in e.get("group")?.iter()? {e.set("a",item352)?;out351.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun355=e.get("all")?;let mut args353=Vec::new();let mut kw354=Vec::new();args353.push({let e=e.child();let out356=Val::list(vec![]);for item357 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun360=e.get("range")?;let mut args358=Vec::new();let mut kw359=Vec::new();args358.push(Val::Int(3i64));fun360.call(args358,kw359)?}}.iter()? {e.set("k",item357)?;out356.attr("append")?.call(vec![{let v367=binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun363=e.get("min")?;let mut args361=Vec::new();let mut kw362=Vec::new();args361.push(e.get("a")?.get(binary("add",binary("mul",Val::Int(2i64),e.get("k")?)?,Val::Int(1i64))?)?);args361.push(e.get("b")?.get(binary("add",binary("mul",Val::Int(2i64),e.get("k")?)?,Val::Int(1i64))?)?);fun363.call(args361,kw362)?}},{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun366=e.get("max")?;let mut args364=Vec::new();let mut kw365=Vec::new();args364.push(e.get("a")?.get(binary("mul",Val::Int(2i64),e.get("k")?)?)?);args364.push(e.get("b")?.get(binary("mul",Val::Int(2i64),e.get("k")?)?)?);fun366.call(args364,kw365)?}})?;let v368=Val::Float(1e-08f64);Val::Bool(compare("gt",v367.clone(),v368.clone())?.truthy()?)}],vec![])?;}out356});fun355.call(args353,kw354)?}}],vec![])?;}out351});fun350.call(args348,kw349)?}}.truthy()? {
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun371=e.get("group")?.attr("append")?;let mut args369=Vec::new();let mut kw370=Vec::new();args369.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun374=e.get("boxes")?.attr("pop")?;let mut args372=Vec::new();let mut kw373=Vec::new();args372.push(e.get("i")?);fun374.call(args372,kw373)?}});fun371.call(args369,kw370)?}};
let assigned375=Val::Bool(true);e.set("changed",assigned375.clone())?;
}
}
}
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun378=e.get("groups")?.attr("append")?;let mut args376=Vec::new();let mut kw377=Vec::new();args376.push(e.get("group")?);fun378.call(args376,kw377)?}};
}
let assigned379={let mut s=Vec::new();Val::list(s)};e.set("towers",assigned379.clone())?;
for item380 in e.get("groups")?.iter()? {
e.set("group",item380)?;let assigned381={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun384=e.get("tuple")?;let mut args382=Vec::new();let mut kw383=Vec::new();args382.push({let e=e.child();let out385=Val::list(vec![]);for item386 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun389=e.get("range")?;let mut args387=Vec::new();let mut kw388=Vec::new();args387.push(Val::Int(3i64));fun389.call(args387,kw388)?}}.iter()? {e.set("k",item386)?;for item390 in {let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun393=e.get("min")?;let mut args391=Vec::new();let mut kw392=Vec::new();args391.push({let e=e.child();let out394=Val::list(vec![]);for item395 in e.get("group")?.iter()? {e.set("p",item395)?;out394.attr("append")?.call(vec![e.get("p")?.get(binary("mul",Val::Int(2i64),e.get("k")?)?)?],vec![])?;}out394});fun393.call(args391,kw392)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun398=e.get("max")?;let mut args396=Vec::new();let mut kw397=Vec::new();args396.push({let e=e.child();let out399=Val::list(vec![]);for item400 in e.get("group")?.iter()? {e.set("p",item400)?;out399.attr("append")?.call(vec![e.get("p")?.get(binary("add",binary("mul",Val::Int(2i64),e.get("k")?)?,Val::Int(1i64))?)?],vec![])?;}out399});fun398.call(args396,kw397)?}});Val::tuple(s)}.iter()? {e.set("v",item390)?;out385.attr("append")?.call(vec![e.get("v")?],vec![])?;}}out385});fun384.call(args382,kw383)?}};e.set("b",assigned381.clone())?;
let assigned401=if {let v402=e.get("b")?.get(Val::Int(1i64))?;let v403=Val::Int(0i64);Val::Bool(compare("gt",v402.clone(),v403.clone())?.truthy()?)}.truthy()? {e.get("inner")?.get(Val::Int(1i64))?} else {e.get("inner")?.get(Val::Int(0i64))?};e.set("wall",assigned401.clone())?;
let assigned404=if {let v405=e.get("b")?.get(Val::Int(1i64))?;let v406=Val::Int(0i64);Val::Bool(compare("gt",v405.clone(),v406.clone())?.truthy()?)}.truthy()? {e.get("b")?.get(Val::Int(0i64))?} else {e.get("b")?.get(Val::Int(1i64))?};e.set("face",assigned404.clone())?;
let assigned407={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun410=e.get("abs")?;let mut args408=Vec::new();let mut kw409=Vec::new();args408.push(binary("sub",e.get("wall")?,e.get("face")?)?);fun410.call(args408,kw409)?}};e.set("run",assigned407.clone())?;
let assigned411={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun414=e.get("graph")?.attr("prism")?;let mut args412=Vec::new();let mut kw413=Vec::new();args412.push(Val::Int(1i64));args412.push(e.get("b")?.get(Val::Int(2i64))?);args412.push(e.get("b")?.get(Val::Int(3i64))?);args412.push({let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(e.get("face")?);s.push(e.get("b")?.get(Val::Int(4i64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("wall")?);s.push(e.get("b")?.get(Val::Int(4i64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("wall")?);s.push(binary("sub",e.get("b")?.get(Val::Int(4i64))?,e.get("run")?)?);Val::tuple(s)});Val::tuple(s)});fun414.call(args412,kw413)?}};e.set("wedge",assigned411.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun417=e.get("towers")?.attr("append")?;let mut args415=Vec::new();let mut kw416=Vec::new();args415.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun420={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun423=e.get("graph")?.attr("box")?;let mut args421=Vec::new();let mut kw422=Vec::new();args421.extend(e.get("b")?.iter()?);fun423.call(args421,kw422)?}}.attr("fuse")?;let mut args418=Vec::new();let mut kw419=Vec::new();args418.push(e.get("wedge")?);fun420.call(args418,kw419)?}});fun417.call(args415,kw416)?}};
}
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun426=e.get("towers")?.get(Val::Int(0i64))?.attr("fuse")?;let mut args424=Vec::new();let mut kw425=Vec::new();args424.extend(e.get("towers")?.get(Val::Slice{start:Some(Val::Int(1i64).integer()?),stop:None,step:1})?.iter()?);fun426.call(args424,kw425)?}});
Ok(Val::None)})})?;
    // _pump_inverse
    e.set("_pump_inverse",{let params=vec![("shell".into(),None,false),("graph".into(),None,false),("box".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned427={let mut s=Vec::new();Val::list(s)};e.set("out",assigned427.clone())?;
for item428 in e.get("box")?.attr("pack")?.attr("pump_trays")?.iter()? {
let unpack429=unpack(item428,3)?;e.set("x",unpack429[0].clone())?;e.set("y0",unpack429[1].clone())?;e.set("z",unpack429[2].clone())?;let assigned430=binary("sub",e.get("z")?,e.get("shell")?.attr("_interface")?.attr("pump_seated_drop")?)?;e.set("flange",assigned430.clone())?;
let assigned431=binary("add",e.get("y0")?,e.get("shell")?.attr("_tray")?.attr("rear_axis_y_shift")?)?;e.set("y",assigned431.clone())?;
let assigned432={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun435=e.get("shell")?.attr("fits")?.attr("clearance")?;let mut args433=Vec::new();let mut kw434=Vec::new();kw434.push(("supported".into(),Val::Bool(true)));fun435.call(args433,kw434)?}};e.set("finish",assigned432.clone())?;
let assigned436={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun439=e.get("shell")?.attr("_tray")?.attr("boss_room")?;let mut args437=Vec::new();let mut kw438=Vec::new();args437.push(e.get("shell")?.attr("cap_boss_air")?);fun439.call(args437,kw438)?}};e.set("room",assigned436.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun442=e.get("out")?.attr("append")?;let mut args440=Vec::new();let mut kw441=Vec::new();args440.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun445={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun448=e.get("room")?.attr("fuse")?;let mut args446=Vec::new();let mut kw447=Vec::new();args446.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun451=e.get("room")?.attr("translate")?;let mut args449=Vec::new();let mut kw450=Vec::new();args449.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(e.get("finish")?);Val::tuple(s)});fun451.call(args449,kw450)?}});fun448.call(args446,kw447)?}}.attr("translate")?;let mut args443=Vec::new();let mut kw444=Vec::new();args443.push({let mut s=Vec::new();s.push(e.get("x")?);s.push(e.get("y")?);s.push(e.get("flange")?);Val::tuple(s)});fun445.call(args443,kw444)?}});fun442.call(args440,kw441)?}};
let assigned452=binary("add",e.get("flange")?,e.get("shell")?.attr("_tray")?.attr("motor_crown")?)?;e.set("motor_end",assigned452.clone())?;
let assigned453={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun456=e.get("shell")?.attr("cap_terminal_crown_r")?;let mut args454=Vec::new();let mut kw455=Vec::new();args454.push(e.get("box")?);fun456.call(args454,kw455)?}};e.set("radius",assigned453.clone())?;
let assigned457=binary("sub",e.get("motor_end")?,e.get("shell")?.attr("wall")?)?;e.set("start",assigned457.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun460=e.get("out")?.attr("append")?;let mut args458=Vec::new();let mut kw459=Vec::new();args458.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun463=e.get("graph")?.attr("cylinder")?;let mut args461=Vec::new();let mut kw462=Vec::new();args461.push(Val::Int(2i64));args461.push(e.get("shell")?.attr("_tray")?.attr("can_half")?);args461.push(e.get("x")?);args461.push(e.get("y")?);args461.push(binary("sub",binary("add",binary("add",e.get("flange")?,e.get("shell")?.attr("_tray")?.attr("boss_depth")?)?,e.get("finish")?)?,Val::Float(0.01f64))?);args461.push(binary("add",e.get("start")?,Val::Float(0.01f64))?);fun463.call(args461,kw462)?}});fun460.call(args458,kw459)?}};
// cone
e.set("cone",{let params=vec![("r0".into(),None,false),("r1".into(),None,false),("z0".into(),None,false),("height".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned464={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun467=e.get("max")?;let mut args465=Vec::new();let mut kw466=Vec::new();args465.push(e.get("r0")?);args465.push(e.get("r1")?);fun467.call(args465,kw466)?}};e.set("r",assigned464.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun470=e.get("graph")?.attr("add")?;let mut args468=Vec::new();let mut kw469=Vec::new();args468.push(Val::Str("cone".into()));kw469.push(("axis".into(),Val::Int(2i64)));kw469.push(("centre".into(),{let mut s=Vec::new();s.push(e.get("x")?);s.push(e.get("y")?);Val::tuple(s)}));kw469.push(("radii".into(),{let mut s=Vec::new();s.push(e.get("r0")?);s.push(e.get("r1")?);Val::tuple(s)}));kw469.push(("span".into(),{let mut s=Vec::new();s.push(e.get("z0")?);s.push(binary("add",e.get("z0")?,e.get("height")?)?);Val::tuple(s)}));kw469.push(("bounds".into(),{let mut s=Vec::new();s.push(binary("sub",e.get("x")?,e.get("r")?)?);s.push(binary("add",e.get("x")?,e.get("r")?)?);s.push(binary("sub",e.get("y")?,e.get("r")?)?);s.push(binary("add",e.get("y")?,e.get("r")?)?);s.push(e.get("z0")?);s.push(binary("add",e.get("z0")?,e.get("height")?)?);Val::tuple(s)}));fun470.call(args468,kw469)?}});
Ok(Val::None)})})?;
let assigned471=binary("sub",e.get("radius")?,e.get("shell")?.attr("_tray")?.attr("can_half")?)?;e.set("rise",assigned471.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun474=e.get("out")?.attr("append")?;let mut args472=Vec::new();let mut kw473=Vec::new();args472.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun477=e.get("cone")?;let mut args475=Vec::new();let mut kw476=Vec::new();args475.push(e.get("shell")?.attr("_tray")?.attr("can_half")?);args475.push(e.get("radius")?);args475.push(e.get("start")?);args475.push(e.get("rise")?);fun477.call(args475,kw476)?}});fun474.call(args472,kw473)?}};
let assigned478=binary("mul",e.get("radius")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun481=e.get("math")?.attr("tan")?;let mut args479=Vec::new();let mut kw480=Vec::new();args479.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun484=e.get("math")?.attr("radians")?;let mut args482=Vec::new();let mut kw483=Vec::new();args482.push(e.get("shell")?.attr("teardrop_roof_angle")?);fun484.call(args482,kw483)?}});fun481.call(args479,kw480)?}})?;e.set("roof",assigned478.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun487=e.get("out")?.attr("append")?;let mut args485=Vec::new();let mut kw486=Vec::new();args485.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun490=e.get("cone")?;let mut args488=Vec::new();let mut kw489=Vec::new();args488.push(e.get("radius")?);args488.push(Val::Float(0.0f64));args488.push(binary("add",e.get("start")?,e.get("rise")?)?);args488.push(e.get("roof")?);fun490.call(args488,kw489)?}});fun487.call(args485,kw486)?}};
}
return Ok(e.get("out")?);
Ok(Val::None)})})?;
    // _box_points
    e.set("_box_points",{let params=vec![("bounds".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let mod491=rt.import_module("itertools")?;e.set("product",rt.member("itertools","product")?)?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun494=e.get("list")?;let mut args492=Vec::new();let mut kw493=Vec::new();args492.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun497=e.get("product")?;let mut args495=Vec::new();let mut kw496=Vec::new();args495.extend({let e=e.child();let out498=Val::list(vec![]);for item499 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun502=e.get("range")?;let mut args500=Vec::new();let mut kw501=Vec::new();args500.push(Val::Int(3i64));fun502.call(args500,kw501)?}}.iter()? {e.set("k",item499)?;out498.attr("append")?.call(vec![e.get("bounds")?.get(Val::Slice{start:Some(binary("mul",Val::Int(2i64),e.get("k")?)?.integer()?),stop:Some(binary("add",binary("mul",Val::Int(2i64),e.get("k")?)?,Val::Int(2i64))?.integer()?),step:1})?],vec![])?;}out498}.iter()?);fun497.call(args495,kw496)?}});fun494.call(args492,kw493)?}});
Ok(Val::None)})})?;
    // _diamond
    e.set("_diamond", {
        let params = vec![
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("z".into(), None, false),
            ("radius".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("x")?, e.get("radius")?)?);
                    s.push(e.get("y")?);
                    s.push(e.get("z")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y")?);
                    s.push(binary("add", e.get("z")?, e.get("radius")?)?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("x")?, e.get("radius")?)?);
                    s.push(e.get("y")?);
                    s.push(e.get("z")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y")?);
                    s.push(binary("sub", e.get("z")?, e.get("radius")?)?);
                    Val::tuple(s)
                });
                Val::list(s)
            });
            Ok(Val::None)
        })
    })?;
    // _corridor
    e.set("_corridor", {
        let params = vec![
            ("shell".into(), None, false),
            ("graph".into(), None, false),
            ("clouds".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned503 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun506 = e
                        .get("shell")?
                        .attr("_fixed_pump_mount")?
                        .attr("_corridor_profile")?;
                    let mut args504 = Vec::new();
                    let mut kw505 = Vec::new();
                    args504.push({
                        let e = e.child();
                        let out507 = Val::list(vec![]);
                        for item508 in e.get("clouds")?.iter()? {
                            e.set("cloud", item508)?;
                            for item509 in e.get("cloud")?.iter()? {
                                e.set("p", item509)?;
                                out507.attr("append")?.call(vec![e.get("p")?], vec![])?;
                            }
                        }
                        out507
                    });
                    fun506.call(args504, kw505)?
                }
            };
            let unpack510 = unpack(assigned503.clone(), 2)?;
            e.set("span", unpack510[0].clone())?;
            e.set("profile", unpack510[1].clone())?;
            let assigned511 = {
                let e = e.child();
                let out512 = Val::list(vec![]);
                for item513 in e.get("span")?.iter()? {
                    e.set("x", item513)?;
                    for item514 in e.get("profile")?.iter()? {
                        let unpack515 = unpack(item514, 2)?;
                        e.set("y", unpack515[0].clone())?;
                        e.set("z", unpack515[1].clone())?;
                        out512.attr("append")?.call(
                            vec![{
                                let mut s = Vec::new();
                                s.push(e.get("x")?);
                                s.push(e.get("y")?);
                                s.push(e.get("z")?);
                                Val::tuple(s)
                            }],
                            vec![],
                        )?;
                    }
                }
                out512
            };
            e.set("points", assigned511.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                        line!(),
                    );
                    {
                        let fun518 = e.get("graph")?.attr("prism")?;
                        let mut args516 = Vec::new();
                        let mut kw517 = Vec::new();
                        args516.push(Val::Int(0i64));
                        args516.extend(e.get("span")?.iter()?);
                        args516.push(e.get("profile")?);
                        fun518.call(args516, kw517)?
                    }
                });
                s.push(e.get("points")?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // _pump_wires
    e.set("_pump_wires",{let params=vec![("shell".into(),None,false),("graph".into(),None,false),("box".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned519=e.get("shell")?.attr("_fixed_pump_mount")?;e.set("mount",assigned519.clone())?;
let assigned520={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun523=e.get("mount")?.attr("wiring_passages")?;let mut args521=Vec::new();let mut kw522=Vec::new();args521.push(e.get("shell")?);args521.push(e.get("box")?);fun523.call(args521,kw522)?}};e.set("plan",assigned520.clone())?;
let assigned524=e.get("plan")?.get(Val::Str("front-top-electrical".into()))?.get(Val::Str("points_mm".into()))?;let unpack525=unpack(assigned524.clone(),2)?;e.set("rear",unpack525[0].clone())?;e.set("fore",unpack525[1].clone())?;
let assigned526=e.get("plan")?.get(Val::Str("front-top-electrical".into()))?.get(Val::Str("diamond_half_span_mm".into()))?;e.set("radius",assigned526.clone())?;
let assigned527={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun530=e.get("graph")?.attr("prism")?;let mut args528=Vec::new();let mut kw529=Vec::new();args528.push(Val::Int(1i64));args528.push(e.get("fore")?.get(Val::Int(1i64))?);args528.push(e.get("rear")?.get(Val::Int(1i64))?);args528.push({let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(unary("neg",e.get("radius")?)?);s.push(e.get("rear")?.get(Val::Int(2i64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(binary("add",e.get("rear")?.get(Val::Int(2i64))?,e.get("radius")?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("radius")?);s.push(e.get("rear")?.get(Val::Int(2i64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(binary("sub",e.get("rear")?.get(Val::Int(2i64))?,e.get("radius")?)?);Val::tuple(s)});Val::tuple(s)});fun530.call(args528,kw529)?}};e.set("shared",assigned527.clone())?;
let assigned531=binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun534=e.get("_diamond")?;let mut args532=Vec::new();let mut kw533=Vec::new();args532.push(Val::Float(0.0f64));args532.push(e.get("fore")?.get(Val::Int(1i64))?);args532.push(e.get("rear")?.get(Val::Int(2i64))?);args532.push(e.get("radius")?);fun534.call(args532,kw533)?}},{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun537=e.get("_diamond")?;let mut args535=Vec::new();let mut kw536=Vec::new();args535.push(Val::Float(0.0f64));args535.push(e.get("rear")?.get(Val::Int(1i64))?);args535.push(e.get("rear")?.get(Val::Int(2i64))?);args535.push(e.get("radius")?);fun537.call(args535,kw536)?}})?;e.set("shared_points",assigned531.clone())?;
let assigned538={let mut s=Vec::new();s.push(unary("neg",e.get("radius")?)?);s.push(e.get("radius")?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun541=e.get("shell")?.attr("housing_back_y")?;let mut args539=Vec::new();let mut kw540=Vec::new();args539.push(e.get("box")?.attr("outer")?);fun541.call(args539,kw540)?}});s.push(e.get("rear")?.get(Val::Int(1i64))?);s.push(e.get("rear")?.get(Val::Int(2i64))?);s.push(binary("add",e.get("box")?.attr("pump_bay")?.get(Val::Int(2i64))?,Val::Float(0.01f64))?);Val::tuple(s)};e.set("opening",assigned538.clone())?;
let assigned542=e.get("plan")?.get(Val::Str("front-top-pump-cross".into()))?;e.set("cross",assigned542.clone())?;
let assigned543=e.get("cross")?.get(Val::Str("points_mm".into()))?;let unpack544=unpack(assigned543.clone(),3)?;e.set("a",unpack544[0].clone())?;e.set("_",unpack544[1].clone())?;e.set("b",unpack544[2].clone())?;
let assigned545=e.get("cross")?.get(Val::Str("roof_half_span_mm".into()))?;e.set("radius",assigned545.clone())?;
let assigned546=e.get("cross")?.get(Val::Str("floor_z_mm".into()))?;e.set("floor",assigned546.clone())?;
let assigned547={let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(binary("sub",e.get("a")?.get(Val::Int(1i64))?,e.get("radius")?)?);s.push(e.get("floor")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("add",e.get("a")?.get(Val::Int(1i64))?,e.get("radius")?)?);s.push(e.get("floor")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("add",e.get("a")?.get(Val::Int(1i64))?,e.get("radius")?)?);s.push(e.get("a")?.get(Val::Int(2i64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("a")?.get(Val::Int(1i64))?);s.push(binary("add",e.get("a")?.get(Val::Int(2i64))?,e.get("radius")?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("sub",e.get("a")?.get(Val::Int(1i64))?,e.get("radius")?)?);s.push(e.get("a")?.get(Val::Int(2i64))?);Val::tuple(s)});Val::tuple(s)};e.set("section",assigned547.clone())?;
let assigned548={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun551=e.get("graph")?.attr("prism")?;let mut args549=Vec::new();let mut kw550=Vec::new();args549.push(Val::Int(0i64));args549.push(e.get("a")?.get(Val::Int(0i64))?);args549.push(e.get("b")?.get(Val::Int(0i64))?);args549.push(e.get("section")?);fun551.call(args549,kw550)?}};e.set("cross_body",assigned548.clone())?;
let assigned552={let e=e.child();let out553=Val::list(vec![]);for item554 in {let mut s=Vec::new();s.push(e.get("a")?.get(Val::Int(0i64))?);s.push(e.get("b")?.get(Val::Int(0i64))?);Val::tuple(s)}.iter()? {e.set("x",item554)?;for item555 in e.get("section")?.iter()? {let unpack556=unpack(item555,2)?;e.set("y",unpack556[0].clone())?;e.set("z",unpack556[1].clone())?;out553.attr("append")?.call(vec![{let mut s=Vec::new();s.push(e.get("x")?);s.push(e.get("y")?);s.push(e.get("z")?);Val::tuple(s)}],vec![])?;}}out553};e.set("cross_points",assigned552.clone())?;
let assigned557=e.get("plan")?.get(Val::Str("front-top-display-chimney".into()))?.get(Val::Str("bounds_mm".into()))?;e.set("chimney",assigned557.clone())?;
let assigned558=e.get("plan")?.get(Val::Str("front-top-display-link".into()))?;e.set("link",assigned558.clone())?;
let assigned559=e.get("link")?.get(Val::Str("points_mm".into()))?;let unpack560=unpack(assigned559.clone(),2)?;e.set("a",unpack560[0].clone())?;e.set("b",unpack560[1].clone())?;
let assigned561=e.get("link")?.get(Val::Str("diamond_half_span_mm".into()))?;e.set("radius",assigned561.clone())?;
let assigned562={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun565=e.get("_display_frame")?;let mut args563=Vec::new();let mut kw564=Vec::new();args563.push(e.get("shell")?);args563.push(e.get("box")?.attr("outer")?);fun565.call(args563,kw564)?}};e.set("frame",assigned562.clone())?;
let assigned566={let mut s=Vec::new();Val::list(s)};e.set("local",assigned566.clone())?;
for item567 in binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun570=e.get("_diamond")?;let mut args568=Vec::new();let mut kw569=Vec::new();args568.extend(e.get("link")?.get(Val::Str("terminal_entry_mm".into()))?.iter()?);args568.push(e.get("radius")?);fun570.call(args568,kw569)?}},{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun573=e.get("_diamond")?;let mut args571=Vec::new();let mut kw572=Vec::new();args571.extend(e.get("a")?.iter()?);args571.push(e.get("radius")?);fun573.call(args571,kw572)?}})?.iter()? {
e.set("point",item567)?;let assigned574={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun577=e.get("tuple")?;let mut args575=Vec::new();let mut kw576=Vec::new();args575.push({let e=e.child();let out578=Val::list(vec![]);for item579 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun582=e.get("zip")?;let mut args580=Vec::new();let mut kw581=Vec::new();args580.push(e.get("point")?);args580.push(e.get("frame")?.get(Val::Str("translation_mm".into()))?);fun582.call(args580,kw581)?}}.iter()? {let unpack583=unpack(item579,2)?;e.set("v",unpack583[0].clone())?;e.set("o",unpack583[1].clone())?;out578.attr("append")?.call(vec![binary("sub",e.get("v")?,e.get("o")?)?],vec![])?;}out578});fun577.call(args575,kw576)?}};e.set("delta",assigned574.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun586=e.get("local")?.attr("append")?;let mut args584=Vec::new();let mut kw585=Vec::new();args584.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun589=e.get("tuple")?;let mut args587=Vec::new();let mut kw588=Vec::new();args587.push({let e=e.child();let out590=Val::list(vec![]);for item591 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun594=e.get("range")?;let mut args592=Vec::new();let mut kw593=Vec::new();args592.push(Val::Int(3i64));fun594.call(args592,kw593)?}}.iter()? {e.set("k",item591)?;out590.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun597=e.get("sum")?;let mut args595=Vec::new();let mut kw596=Vec::new();args595.push({let e=e.child();let out598=Val::list(vec![]);for item599 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun602=e.get("range")?;let mut args600=Vec::new();let mut kw601=Vec::new();args600.push(Val::Int(3i64));fun602.call(args600,kw601)?}}.iter()? {e.set("j",item599)?;out598.attr("append")?.call(vec![binary("mul",e.get("frame")?.get(Val::Str("rotation".into()))?.get(e.get("j")?)?.get(e.get("k")?)?,e.get("delta")?.get(e.get("j")?)?)?],vec![])?;}out598});fun597.call(args595,kw596)?}}],vec![])?;}out590});fun589.call(args587,kw588)?}});fun586.call(args584,kw585)?}};
}
let assigned603={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun606=e.get("tuple")?;let mut args604=Vec::new();let mut kw605=Vec::new();args604.push({let e=e.child();let out607=Val::list(vec![]);for item608 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun611=e.get("range")?;let mut args609=Vec::new();let mut kw610=Vec::new();args609.push(Val::Int(3i64));fun611.call(args609,kw610)?}}.iter()? {e.set("k",item608)?;for item612 in {let mut s=Vec::new();s.push(binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun615=e.get("min")?;let mut args613=Vec::new();let mut kw614=Vec::new();args613.push({let e=e.child();let out616=Val::list(vec![]);for item617 in e.get("local")?.iter()? {e.set("p",item617)?;out616.attr("append")?.call(vec![e.get("p")?.get(e.get("k")?)?],vec![])?;}out616});fun615.call(args613,kw614)?}},Val::Float(1.0f64))?);s.push(binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun620=e.get("max")?;let mut args618=Vec::new();let mut kw619=Vec::new();args618.push({let e=e.child();let out621=Val::list(vec![]);for item622 in e.get("local")?.iter()? {e.set("p",item622)?;out621.attr("append")?.call(vec![e.get("p")?.get(e.get("k")?)?],vec![])?;}out621});fun620.call(args618,kw619)?}},Val::Float(1.0f64))?);Val::tuple(s)}.iter()? {e.set("v",item612)?;out607.attr("append")?.call(vec![e.get("v")?],vec![])?;}}out607});fun606.call(args604,kw605)?}};e.set("bounds",assigned603.clone())?;
e.set("layout",rt.import_module("above_core")?)?;
let assigned623={let e=e.child();let out624=Val::list(vec![]);for item625 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun628=e.get("_box_points")?;let mut args626=Vec::new();let mut kw627=Vec::new();args626.push(e.get("bounds")?);fun628.call(args626,kw627)?}}.iter()? {e.set("p",item625)?;out624.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun631=e.get("layout")?.attr("point")?;let mut args629=Vec::new();let mut kw630=Vec::new();args629.push(e.get("frame")?);args629.push(e.get("p")?);fun631.call(args629,kw630)?}}],vec![])?;}out624};e.set("entry",assigned623.clone())?;
let assigned632={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun635=e.get("_corridor")?;let mut args633=Vec::new();let mut kw634=Vec::new();args633.push(e.get("shell")?);args633.push(e.get("graph")?);args633.push({let mut s=Vec::new();s.push(e.get("entry")?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun638=e.get("_diamond")?;let mut args636=Vec::new();let mut kw637=Vec::new();args636.extend(e.get("a")?.iter()?);args636.push(e.get("radius")?);fun638.call(args636,kw637)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun641=e.get("_diamond")?;let mut args639=Vec::new();let mut kw640=Vec::new();args639.extend(e.get("b")?.iter()?);args639.push(e.get("radius")?);fun641.call(args639,kw640)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun644=e.get("_box_points")?;let mut args642=Vec::new();let mut kw643=Vec::new();args642.push(e.get("chimney")?);fun644.call(args642,kw643)?}});Val::list(s)});fun635.call(args633,kw634)?}};let unpack645=unpack(assigned632.clone(),2)?;e.set("corridor",unpack645[0].clone())?;e.set("corridor_points",unpack645[1].clone())?;
return Ok({let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(e.get("shared")?);s.push(e.get("shared_points")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun648=e.get("graph")?.attr("box")?;let mut args646=Vec::new();let mut kw647=Vec::new();args646.extend(e.get("opening")?.iter()?);fun648.call(args646,kw647)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun651=e.get("_box_points")?;let mut args649=Vec::new();let mut kw650=Vec::new();args649.push(e.get("opening")?);fun651.call(args649,kw650)?}});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("cross_body")?);s.push(e.get("cross_points")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("corridor")?);s.push(e.get("corridor_points")?);Val::tuple(s)});Val::list(s)});
Ok(Val::None)})})?;
    // _upper_wire_room
    e.set("_upper_wire_room", {
        let params = vec![
            ("shell".into(), None, false),
            ("graph".into(), None, false),
            ("box".into(), None, false),
            ("wire_rooms".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned652 = e.get("shell")?.attr("_fixed_pump_mount")?;
            e.set("mount", assigned652.clone())?;
            let assigned653 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun656 = e.get("mount")?.attr("datums")?;
                    let mut args654 = Vec::new();
                    let mut kw655 = Vec::new();
                    args654.push(e.get("shell")?);
                    args654.push(e.get("box")?);
                    fun656.call(args654, kw655)?
                }
            };
            e.set("d", assigned653.clone())?;
            let assigned657 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun660 = e.get("shell")?.attr("cap_terminal_crown_r")?;
                    let mut args658 = Vec::new();
                    let mut kw659 = Vec::new();
                    args658.push(e.get("box")?);
                    fun660.call(args658, kw659)?
                }
            };
            e.set("radius", assigned657.clone())?;
            let assigned661 = binary(
                "sub",
                binary(
                    "add",
                    binary(
                        "sub",
                        binary(
                            "add",
                            e.get("d")?.get(Val::Str("flange_z".into()))?,
                            e.get("shell")?.attr("_tray")?.attr("motor_crown")?,
                        )?,
                        e.get("shell")?.attr("wall")?,
                    )?,
                    e.get("radius")?,
                )?,
                e.get("shell")?.attr("_tray")?.attr("can_half")?,
            )?;
            e.set("base", assigned661.clone())?;
            let assigned662 = binary(
                "add",
                e.get("base")?,
                binary("mul", e.get("radius")?, {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                        line!(),
                    );
                    {
                        let fun665 = e.get("math")?.attr("tan")?;
                        let mut args663 = Vec::new();
                        let mut kw664 = Vec::new();
                        args663.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                                line!(),
                            );
                            {
                                let fun668 = e.get("math")?.attr("radians")?;
                                let mut args666 = Vec::new();
                                let mut kw667 = Vec::new();
                                args666.push(e.get("shell")?.attr("teardrop_roof_angle")?);
                                fun668.call(args666, kw667)?
                            }
                        });
                        fun665.call(args663, kw664)?
                    }
                })?,
            )?;
            e.set("peak", assigned662.clone())?;
            let assigned669 = binary(
                "sub",
                e.get("shell")?.attr("display_body_offset_x")?,
                binary(
                    "truediv",
                    e.get("shell")?.attr("display_pcb_x")?,
                    Val::Int(2i64),
                )?,
            )?;
            e.set("x0", assigned669.clone())?;
            let assigned670 = binary(
                "add",
                e.get("shell")?.attr("display_body_offset_x")?,
                binary(
                    "truediv",
                    e.get("shell")?.attr("display_pcb_x")?,
                    Val::Int(2i64),
                )?,
            )?;
            e.set("x1", assigned670.clone())?;
            let assigned671 = {
                let e = e.child();
                let out672 = Val::list(vec![]);
                for item673 in {
                    let mut s = Vec::new();
                    s.push(e.get("x0")?);
                    s.push(e.get("x1")?);
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("x", item673)?;
                    for item674 in {
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary(
                                "sub",
                                e.get("d")?.get(Val::Str("motor_y".into()))?,
                                e.get("radius")?,
                            )?);
                            s.push(e.get("base")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary(
                                "add",
                                e.get("d")?.get(Val::Str("motor_y".into()))?,
                                e.get("radius")?,
                            )?);
                            s.push(e.get("base")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("d")?.get(Val::Str("motor_y".into()))?);
                            s.push(e.get("peak")?);
                            Val::tuple(s)
                        });
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        let unpack675 = unpack(item674, 2)?;
                        e.set("y", unpack675[0].clone())?;
                        e.set("z", unpack675[1].clone())?;
                        out672.attr("append")?.call(
                            vec![{
                                let mut s = Vec::new();
                                s.push(e.get("x")?);
                                s.push(e.get("y")?);
                                s.push(e.get("z")?);
                                Val::tuple(s)
                            }],
                            vec![],
                        )?;
                    }
                }
                out672
            };
            e.set("motor", assigned671.clone())?;
            let assigned676 = {
                let mut s = Vec::new();
                s.push(e.get("x0")?);
                s.push(e.get("x1")?);
                s.push(binary(
                    "sub",
                    e.get("shell")?.attr("display_body_offset_slope")?,
                    binary(
                        "truediv",
                        e.get("shell")?.attr("display_pcb_slope")?,
                        Val::Int(2i64),
                    )?,
                )?);
                s.push(binary(
                    "add",
                    e.get("shell")?.attr("display_body_offset_slope")?,
                    binary(
                        "truediv",
                        e.get("shell")?.attr("display_pcb_slope")?,
                        Val::Int(2i64),
                    )?,
                )?);
                s.push(binary(
                    "sub",
                    unary("neg", e.get("shell")?.attr("display_facet_thickness")?)?,
                    e.get("shell")?.attr("display_pcb_cut_through")?,
                )?);
                s.push(e.get("shell")?.attr("_display_wings")?.attr("GLASS_SEAT")?);
                Val::tuple(s)
            };
            e.set("bounds", assigned676.clone())?;
            e.set("layout", rt.import_module("above_core")?)?;
            let assigned677 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun680 = e.get("_display_frame")?;
                    let mut args678 = Vec::new();
                    let mut kw679 = Vec::new();
                    args678.push(e.get("shell")?);
                    args678.push(e.get("box")?.attr("outer")?);
                    fun680.call(args678, kw679)?
                }
            };
            e.set("frame", assigned677.clone())?;
            let assigned681 = {
                let e = e.child();
                let out682 = Val::list(vec![]);
                for item683 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                        line!(),
                    );
                    {
                        let fun686 = e.get("_box_points")?;
                        let mut args684 = Vec::new();
                        let mut kw685 = Vec::new();
                        args684.push(e.get("bounds")?);
                        fun686.call(args684, kw685)?
                    }
                }
                .iter()?
                {
                    e.set("p", item683)?;
                    out682.attr("append")?.call(
                        vec![{
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                                line!(),
                            );
                            {
                                let fun689 = e.get("layout")?.attr("point")?;
                                let mut args687 = Vec::new();
                                let mut kw688 = Vec::new();
                                args687.push(e.get("frame")?);
                                args687.push(e.get("p")?);
                                fun689.call(args687, kw688)?
                            }
                        }],
                        vec![],
                    )?;
                }
                out682
            };
            e.set("pcb", assigned681.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun692 = e.get("_corridor")?;
                    let mut args690 = Vec::new();
                    let mut kw691 = Vec::new();
                    args690.push(e.get("shell")?);
                    args690.push(e.get("graph")?);
                    args690.push({
                        let mut s = Vec::new();
                        s.push(e.get("motor")?);
                        s.push(e.get("pcb")?);
                        s.extend(
                            {
                                let e = e.child();
                                let out693 = Val::list(vec![]);
                                for item694 in e
                                    .get("wire_rooms")?
                                    .get(Val::Slice {
                                        start: Some(Val::Int(2i64).integer()?),
                                        stop: None,
                                        step: 1,
                                    })?
                                    .iter()?
                                {
                                    let unpack695 = unpack(item694, 2)?;
                                    e.set("_", unpack695[0].clone())?;
                                    e.set("points", unpack695[1].clone())?;
                                    out693
                                        .attr("append")?
                                        .call(vec![e.get("points")?], vec![])?;
                                }
                                out693
                            }
                            .iter()?,
                        );
                        Val::list(s)
                    });
                    fun692.call(args690, kw691)?
                }
            }
            .get(Val::Int(0i64))?);
            Ok(Val::None)
        })
    })?;
    // _display_cleanouts
    e.set("_display_cleanouts",{let params=vec![("shell".into(),None,false),("graph".into(),None,false),("box".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned696=e.get("shell")?.attr("_display_wings")?;e.set("wing",assigned696.clone())?;
let assigned697=binary("add",binary("add",binary("truediv",e.get("wing")?.attr("COVER_X")?,Val::Int(2i64))?,e.get("wing")?.attr("WING_REACH")?)?,e.get("wing")?.attr("TIP_AIR")?)?;e.set("reach",assigned697.clone())?;
let assigned698={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun701=e.get("shell")?.attr("_display_cut_exit_depth")?;let mut args699=Vec::new();let mut kw700=Vec::new();fun701.call(args699,kw700)?}};e.set("depth",assigned698.clone())?;
let assigned702=binary("sub",e.get("wing")?.attr("GLASS_SEAT")?,e.get("shell")?.attr("wall")?)?;e.set("roof",assigned702.clone())?;
let assigned703=binary("sub",binary("add",binary("add",e.get("wing")?.attr("BACK")?,e.get("wing")?.attr("WING_THICK")?)?,e.get("wing")?.attr("BEARING_AIR")?)?,e.get("depth")?)?;e.set("floor",assigned703.clone())?;
let assigned704=binary("sub",binary("sub",binary("truediv",unary("neg",e.get("wing")?.attr("WING_SPAN")?)?,Val::Int(2i64))?,e.get("wing")?.attr("END_AIR")?)?,binary("mul",e.get("depth")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun707=e.get("math")?.attr("tan")?;let mut args705=Vec::new();let mut kw706=Vec::new();args705.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun710=e.get("math")?.attr("radians")?;let mut args708=Vec::new();let mut kw709=Vec::new();args708.push(e.get("wing")?.attr("ANGLE")?);fun710.call(args708,kw709)?}});fun707.call(args705,kw706)?}})?)?;e.set("y0",assigned704.clone())?;
let assigned711=binary("add",binary("truediv",e.get("wing")?.attr("WING_SPAN")?,Val::Int(2i64))?,e.get("wing")?.attr("END_AIR")?)?;e.set("y1",assigned711.clone())?;
let assigned712=binary("sub",e.get("shell")?.attr("display_body_offset_x")?,binary("truediv",e.get("shell")?.attr("display_pcb_x")?,Val::Int(2i64))?)?;e.set("pcb0",assigned712.clone())?;
let assigned713=binary("add",e.get("shell")?.attr("display_body_offset_x")?,binary("truediv",e.get("shell")?.attr("display_pcb_x")?,Val::Int(2i64))?)?;e.set("pcb1",assigned713.clone())?;
let assigned714={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun717=e.get("_display_frame")?;let mut args715=Vec::new();let mut kw716=Vec::new();args715.push(e.get("shell")?);args715.push(e.get("box")?.attr("outer")?);fun717.call(args715,kw716)?}};e.set("frame",assigned714.clone())?;
return Ok({let e=e.child();let out718=Val::list(vec![]);for item719 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(unary("neg",e.get("reach")?)?);s.push(binary("add",e.get("pcb0")?,Val::Float(0.01f64))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("sub",e.get("pcb1")?,Val::Float(0.01f64))?);s.push(e.get("reach")?);Val::tuple(s)});Val::tuple(s)}.iter()? {let unpack720=unpack(item719,2)?;e.set("x0",unpack720[0].clone())?;e.set("x1",unpack720[1].clone())?;out718.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun723=e.get("_placed")?;let mut args721=Vec::new();let mut kw722=Vec::new();args721.push(e.get("graph")?);args721.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun726=e.get("graph")?.attr("box")?;let mut args724=Vec::new();let mut kw725=Vec::new();args724.push(e.get("x0")?);args724.push(e.get("x1")?);args724.push(e.get("y0")?);args724.push(e.get("y1")?);args724.push(e.get("floor")?);args724.push(e.get("roof")?);fun726.call(args724,kw725)?}});args721.push(e.get("frame")?);fun723.call(args721,kw722)?}}],vec![])?;}out718});
Ok(Val::None)})})?;
    e.set("_leaves",{let params=vec![("shell".into(),None,false),("graph".into(),None,false),("box".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;
            let enter_e=e.clone();let enter_rt=rt.clone();
            let enter=Val::function(move|_,_|{let e=enter_e.clone();let rt=enter_rt.clone();let _frame=rt.frame(&e);
        let assigned727=e.get("shell")?.attr("_display_wings")?;e.set("wing",assigned727.clone())?;
// rounded
e.set("rounded",{let params=vec![("w".into(),None,false),("d".into(),None,false),("r".into(),None,false),("z0".into(),None,false),("z1".into(),None,false),("cx".into(),Some(Val::Float(0.0f64)),false),("cy".into(),Some(Val::Float(0.0f64)),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun730=e.get("_rounded")?;let mut args728=Vec::new();let mut kw729=Vec::new();args728.push(e.get("graph")?);args728.push(Val::Int(2i64));args728.push({let mut s=Vec::new();s.push(binary("sub",e.get("cx")?,binary("truediv",e.get("w")?,Val::Int(2i64))?)?);s.push(binary("add",e.get("cx")?,binary("truediv",e.get("w")?,Val::Int(2i64))?)?);s.push(binary("sub",e.get("cy")?,binary("truediv",e.get("d")?,Val::Int(2i64))?)?);s.push(binary("add",e.get("cy")?,binary("truediv",e.get("d")?,Val::Int(2i64))?)?);s.push(e.get("z0")?);s.push(e.get("z1")?);Val::tuple(s)});args728.push(e.get("r")?);fun730.call(args728,kw729)?}});
Ok(Val::None)})})?;
e.set("context731",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun734=e.get("ExitStack")?;let mut args732=Vec::new();let mut kw733=Vec::new();fun734.call(args732,kw733)?}})?;e.set("stack",e.get("context731")?.attr("__enter__")?.call(vec![],vec![])?)?;{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun737=e.get("stack")?.attr("enter_context")?;let mut args735=Vec::new();let mut kw736=Vec::new();args735.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun740=e.get("_shared_leaves")?;let mut args738=Vec::new();let mut kw739=Vec::new();args738.push(e.get("shell")?);args738.push(e.get("graph")?);args738.push(e.get("box")?);fun740.call(args738,kw739)?}});fun737.call(args735,kw736)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun743=e.get("stack")?.attr("enter_context")?;let mut args741=Vec::new();let mut kw742=Vec::new();args741.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun746=e.get("_replace")?;let mut args744=Vec::new();let mut kw745=Vec::new();args744.push(e.get("wing")?);args744.push({let d=Val::dict(vec![]);d.set(Val::Str("box".into()),e.get("graph")?.attr("box")?)?;d.set(Val::Str("rounded_prism".into()),e.get("rounded")?)?;d.set(Val::Str("support_exits".into()),{let params=vec![("depth".into(),None,false),("inset".into(),Some(Val::Float(0.0f64)),false),("roof_drop".into(),Some(Val::Float(0.0f64)),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun749=e.get("_display_exits")?;let mut args747=Vec::new();let mut kw748=Vec::new();args747.push(e.get("graph")?);args747.push(e.get("wing")?);args747.push(e.get("depth")?);args747.push(e.get("inset")?);args747.push(e.get("roof_drop")?);fun749.call(args747,kw748)?}});
Ok(Val::None)})})?;d});fun746.call(args744,kw745)?}});fun743.call(args741,kw742)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun752=e.get("stack")?.attr("enter_context")?;let mut args750=Vec::new();let mut kw751=Vec::new();args750.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun755=e.get("_replace")?;let mut args753=Vec::new();let mut kw754=Vec::new();args753.push(e.get("shell")?.attr("_valve_tray")?);args753.push({let d=Val::dict(vec![]);d.set(Val::Str("build_body_clearance".into()),{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun758=e.get("_valve_body")?;let mut args756=Vec::new();let mut kw757=Vec::new();args756.push(e.get("shell")?);args756.push(e.get("graph")?);fun758.call(args756,kw757)?}});
Ok(Val::None)})})?;d.set(Val::Str("build_port_channel".into()),{let params=vec![("length".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun761=e.get("graph")?.attr("cylinder")?;let mut args759=Vec::new();let mut kw760=Vec::new();args759.push(Val::Int(1i64));args759.push(binary("add",e.get("shell")?.attr("_valve_tray")?.attr("_valve")?.attr("port_radius")?,e.get("shell")?.attr("_valve_tray")?.attr("PORT_SLIP")?)?);args759.push(Val::Float(0.0f64));args759.push(e.get("shell")?.attr("_valve_tray")?.attr("_valve")?.attr("port_center_z")?);args759.push(binary("truediv",unary("neg",e.get("length")?)?,Val::Int(2i64))?);args759.push(binary("truediv",e.get("length")?,Val::Int(2i64))?);fun761.call(args759,kw760)?}});
Ok(Val::None)})})?;d});fun755.call(args753,kw754)?}});fun752.call(args750,kw751)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun764=e.get("stack")?.attr("enter_context")?;let mut args762=Vec::new();let mut kw763=Vec::new();args762.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun767=e.get("_replace")?;let mut args765=Vec::new();let mut kw766=Vec::new();args765.push(e.get("shell")?.attr("_dock")?);args765.push({let d=Val::dict(vec![]);d.set(Val::Str("return_clearances".into()),{let params=vec![("plate".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let e=e.child();let out768=Val::list(vec![]);for item769 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun772=e.get("plate")?.get(Val::Str("return_ports".into()))?.attr("values")?;let mut args770=Vec::new();let mut kw771=Vec::new();fun772.call(args770,kw771)?}}.iter()? {e.set("port",item769)?;out768.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun775=e.get("graph")?.attr("cylinder")?;let mut args773=Vec::new();let mut kw774=Vec::new();args773.push(Val::Int(2i64));args773.push(e.get("shell")?.attr("_dock")?.attr("RETURN_CHANNEL_R")?);args773.extend(e.get("port")?.get(Val::Str("point".into()))?.get(Val::Slice{start:None,stop:Some(Val::Int(2i64).integer()?),step:1})?.iter()?);args773.push(binary("sub",e.get("plate")?.get(Val::Str("z0".into()))?,Val::Float(1.0f64))?);args773.push(binary("add",e.get("port")?.get(Val::Str("point".into()))?.get(Val::Int(2i64))?,Val::Float(20.0f64))?);fun775.call(args773,kw774)?}}],vec![])?;}out768});
Ok(Val::None)})})?;d.set(Val::Str("box".into()),e.get("graph")?.attr("box")?)?;d.set(Val::Str("ycyl".into()),{let params=vec![("radius".into(),None,false),("x".into(),None,false),("z".into(),None,false),("y0".into(),None,false),("y1".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun778=e.get("graph")?.attr("cylinder")?;let mut args776=Vec::new();let mut kw777=Vec::new();args776.push(Val::Int(1i64));args776.push(e.get("radius")?);args776.push(e.get("x")?);args776.push(e.get("z")?);args776.push(e.get("y0")?);args776.push(e.get("y1")?);fun778.call(args776,kw777)?}});
Ok(Val::None)})})?;d.set(Val::Str("teardrop_y".into()),{let params=vec![("r".into(),None,false),("x".into(),None,false),("z".into(),None,false),("y0".into(),None,false),("y1".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun781=e.get("_teardrop")?;let mut args779=Vec::new();let mut kw780=Vec::new();args779.push(e.get("graph")?);args779.push(e.get("r")?);args779.push(e.get("x")?);args779.push(e.get("z")?);args779.push(e.get("y0")?);args779.push(e.get("y1")?);args779.push(e.get("shell")?.attr("_dock")?.attr("TEARDROP_DEG")?);fun781.call(args779,kw780)?}});
Ok(Val::None)})})?;d});fun767.call(args765,kw766)?}});fun764.call(args762,kw763)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun784=e.get("stack")?.attr("enter_context")?;let mut args782=Vec::new();let mut kw783=Vec::new();args782.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun787=e.get("_replace")?;let mut args785=Vec::new();let mut kw786=Vec::new();args785.push(e.get("shell")?.attr("_above_core_shell")?);args785.push({let d=Val::dict(vec![]);d.set(Val::Str("stacked_well_towers".into()),{let params=vec![("stock".into(),None,false),("inner".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun790=e.get("_stacked_towers")?;let mut args788=Vec::new();let mut kw789=Vec::new();args788.push(e.get("graph")?);args788.push(e.get("stock")?);args788.push(e.get("inner")?);fun790.call(args788,kw789)?}});
Ok(Val::None)})})?;d});fun787.call(args785,kw786)?}});fun784.call(args782,kw783)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun793=e.get("stack")?.attr("enter_context")?;let mut args791=Vec::new();let mut kw792=Vec::new();args791.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun796=e.get("_replace")?;let mut args794=Vec::new();let mut kw795=Vec::new();args794.push(e.get("shell")?.attr("_tray")?);args794.push({let d=Val::dict(vec![]);d.set(Val::Str("boss_room".into()),{let params=vec![("air".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun799=e.get("graph")?.attr("prism")?;let mut args797=Vec::new();let mut kw798=Vec::new();args797.push(Val::Int(2i64));args797.push(Val::Float(0.0f64));args797.push(e.get("shell")?.attr("_tray")?.attr("boss_depth")?);args797.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun802=e.get("shell")?.attr("_tray")?.attr("_pc")?.attr("offset_polygon")?;let mut args800=Vec::new();let mut kw801=Vec::new();args800.push(e.get("shell")?.attr("_tray")?.attr("_pc")?.attr("bore_profile")?);args800.push(e.get("air")?);fun802.call(args800,kw801)?}});fun799.call(args797,kw798)?}});
Ok(Val::None)})})?;d});fun796.call(args794,kw795)?}});fun793.call(args791,kw792)?}};
let assigned803=Val::None;e.set("wire_rooms",assigned803.clone())?;
// wires
e.set("wires",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);if {let v804=e.get("wire_rooms")?;let v805=Val::None;Val::Bool(compare("is",v804.clone(),v805.clone())?.truthy()?)}.truthy()? {
let assigned806={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun809=e.get("_pump_wires")?;let mut args807=Vec::new();let mut kw808=Vec::new();args807.push(e.get("shell")?);args807.push(e.get("graph")?);args807.push(e.get("box")?);fun809.call(args807,kw808)?}};e.set_nonlocal("wire_rooms",assigned806.clone())?;
}
return Ok(e.get("wire_rooms")?);
Ok(Val::None)})})?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun812=e.get("stack")?.attr("enter_context")?;let mut args810=Vec::new();let mut kw811=Vec::new();args810.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun815=e.get("_replace")?;let mut args813=Vec::new();let mut kw814=Vec::new();args813.push(e.get("shell")?.attr("_fixed_pump_mount")?);args813.push({let d=Val::dict(vec![]);d.set(Val::Str("inverse_cuts".into()),{let params=vec![("e".into(),None,false),("box".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun818=e.get("_pump_inverse")?;let mut args816=Vec::new();let mut kw817=Vec::new();args816.push(e.get("e")?);args816.push(e.get("graph")?);args816.push(e.get("box")?);fun818.call(args816,kw817)?}});
Ok(Val::None)})})?;d.set(Val::Str("wire_cuts".into()),{let params=vec![("e".into(),None,false),("box".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let e=e.child();let out819=Val::list(vec![]);for item820 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun823=e.get("wires")?;let mut args821=Vec::new();let mut kw822=Vec::new();fun823.call(args821,kw822)?}}.iter()? {let unpack824=unpack(item820,2)?;e.set("shape",unpack824[0].clone())?;e.set("_",unpack824[1].clone())?;out819.attr("append")?.call(vec![e.get("shape")?],vec![])?;}out819});
Ok(Val::None)})})?;d.set(Val::Str("upper_wire_room".into()),{let params=vec![("e".into(),None,false),("box".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun827=e.get("_upper_wire_room")?;let mut args825=Vec::new();let mut kw826=Vec::new();args825.push(e.get("e")?);args825.push(e.get("graph")?);args825.push(e.get("box")?);args825.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun830=e.get("wires")?;let mut args828=Vec::new();let mut kw829=Vec::new();fun830.call(args828,kw829)?}});fun827.call(args825,kw826)?}});
Ok(Val::None)})})?;d.set(Val::Str("display_cleanouts".into()),{let params=vec![("e".into(),None,false),("box".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun833=e.get("_display_cleanouts")?;let mut args831=Vec::new();let mut kw832=Vec::new();args831.push(e.get("e")?);args831.push(e.get("graph")?);args831.push(e.get("box")?);fun833.call(args831,kw832)?}});
Ok(Val::None)})})?;d});fun815.call(args813,kw814)?}});fun812.call(args810,kw811)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun836=e.get("stack")?.attr("enter_context")?;let mut args834=Vec::new();let mut kw835=Vec::new();args834.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun839=e.get("_replace")?;let mut args837=Vec::new();let mut kw838=Vec::new();args837.push(e.get("shell")?);args837.push({let d=Val::dict(vec![]);d.set(Val::Str("_halfspace".into()),{let params=vec![("origin".into(),None,false),("normal".into(),None,false),("extent".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun842=e.get("_halfspace")?;let mut args840=Vec::new();let mut kw841=Vec::new();args840.push(e.get("graph")?);args840.push(e.get("origin")?);args840.push(e.get("normal")?);args840.push(e.get("extent")?);fun842.call(args840,kw841)?}});
Ok(Val::None)})})?;d.set(Val::Str("_display_cuts".into()),{let params=vec![("outer".into(),None,false),("support_floor".into(),Some(Val::None),false),("support_fore".into(),Some(Val::None),false),("extend_wing_exits".into(),Some(Val::Bool(true)),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun845=e.get("_display_cut")?;let mut args843=Vec::new();let mut kw844=Vec::new();args843.push(e.get("shell")?);args843.push(e.get("graph")?);args843.push(e.get("outer")?);args843.push(e.get("support_floor")?);args843.push(e.get("support_fore")?);args843.push(e.get("extend_wing_exits")?);fun845.call(args843,kw844)?}});
Ok(Val::None)})})?;d.set(Val::Str("_valve_tray_placed".into()),{let params=vec![("shape".into(),None,false),("plane".into(),None,false),("sign".into(),None,false),("x".into(),None,false),("z".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun848={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun851=e.get("shape")?.attr("rotate")?;let mut args849=Vec::new();let mut kw850=Vec::new();args849.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));Val::tuple(s)});args849.push({let mut s=Vec::new();s.push(Val::Float(1.0f64));s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));Val::tuple(s)});args849.push(if {let v852=e.get("sign")?;let v853=Val::Int(0i64);Val::Bool(compare("gt",v852.clone(),v853.clone())?.truthy()?)}.truthy()? {unary("neg",Val::Float(90.0f64))?} else {Val::Float(90.0f64)});fun851.call(args849,kw850)?}}.attr("translate")?;let mut args846=Vec::new();let mut kw847=Vec::new();args846.push({let mut s=Vec::new();s.push(e.get("x")?);s.push(e.get("plane")?);s.push(e.get("z")?);Val::tuple(s)});fun848.call(args846,kw847)?}});
Ok(Val::None)})})?;d.set(Val::Str("_z_rail_crossing".into()),{let params=vec![("face".into(),None,false),("inside".into(),None,false),("joint".into(),None,false),("aft".into(),None,false),("floor".into(),None,false),("peak".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun856=e.get("graph")?.attr("prism")?;let mut args854=Vec::new();let mut kw855=Vec::new();args854.push(Val::Int(0i64));args854.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun859=e.get("min")?;let mut args857=Vec::new();let mut kw858=Vec::new();args857.push(e.get("face")?);args857.push(e.get("inside")?);fun859.call(args857,kw858)?}});args854.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun862=e.get("max")?;let mut args860=Vec::new();let mut kw861=Vec::new();args860.push(e.get("face")?);args860.push(e.get("inside")?);fun862.call(args860,kw861)?}});args854.push({let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(e.get("joint")?);s.push(e.get("floor")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("aft")?);s.push(binary("sub",binary("add",e.get("floor")?,e.get("aft")?)?,e.get("joint")?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("aft")?);s.push(binary("sub",binary("add",e.get("peak")?,e.get("aft")?)?,e.get("joint")?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("joint")?);s.push(e.get("peak")?);Val::tuple(s)});Val::tuple(s)});fun856.call(args854,kw855)?}});
Ok(Val::None)})})?;d});fun839.call(args837,kw838)?}});fun836.call(args834,kw835)?}};
Ok(Val::None)});
            let exit_e=e.clone();let exit_rt=rt.clone();
            let exit=Val::function(move|_,_|{let e=exit_e.clone();let rt=exit_rt.clone();let _frame=rt.frame(&e);
        e.get("context731")?.attr("__exit__")?.call(vec![Val::None,Val::None,Val::None],vec![])?;Ok(Val::None)});Ok(context(enter,exit))})})?; // _front_half
    e.set("_front_half",{let params=vec![("shell".into(),None,false),("graph".into(),None,false),("box".into(),None,false),("structure".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned863={let mut s=Vec::new();s.push(e.get("box")?.attr("inner")?);s.push(e.get("box")?.attr("outer")?);Val::tuple(s)};let unpack864=unpack(assigned863.clone(),2)?;e.set("inner",unpack864[0].clone())?;e.set("outer",unpack864[1].clone())?;
let assigned865=Val::None;e.set("housing_back",assigned865.clone())?;
if {let v867=e.get("box")?.attr("pump_bay")?;if v867.truthy()? {{let v866=e.get("box")?.attr("pack")?.attr("collet_plate")?;if v866.truthy()? {e.get("box")?.attr("pack")?.attr("funnel")?} else {v866}}} else {v867}}.truthy()? {
let assigned868=binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun871=e.get("shell")?.attr("_funnel_frame_part")?.attr("roof_datums")?;let mut args869=Vec::new();let mut kw870=Vec::new();args869.push(e.get("inner")?);args869.push(e.get("box")?.attr("pack")?.attr("funnel")?);args869.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun874=e.get("shell")?.attr("funnel_seat_z")?;let mut args872=Vec::new();let mut kw873=Vec::new();args872.push(e.get("outer")?);fun874.call(args872,kw873)?}});args869.push(e.get("box")?.attr("y_joint")?);fun871.call(args869,kw870)?}}.get(Val::Str("front".into()))?,e.get("shell")?.attr("slide_slip")?)?;e.set("housing_back",assigned868.clone())?;
}
let assigned875={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun878=e.get("shell")?.attr("_facet_geom")?;let mut args876=Vec::new();let mut kw877=Vec::new();args876.push(e.get("outer")?);fun878.call(args876,kw877)?}};let unpack879=unpack(assigned875.clone(),5)?;e.set("_",unpack879[0].clone())?;e.set("normal",unpack879[1].clone())?;e.set("origin",unpack879[2].clone())?;e.set("_",unpack879[3].clone())?;e.set("_",unpack879[4].clone())?;
let assigned880=binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun883=e.get("max")?;let mut args881=Vec::new();let mut kw882=Vec::new();args881.push(binary("sub",e.get("outer")?.get(Val::Int(1i64))?,e.get("outer")?.get(Val::Int(0i64))?)?);args881.push(binary("sub",e.get("outer")?.get(Val::Int(3i64))?,e.get("outer")?.get(Val::Int(2i64))?)?);args881.push(binary("sub",e.get("outer")?.get(Val::Int(5i64))?,e.get("outer")?.get(Val::Int(4i64))?)?);fun883.call(args881,kw882)?}},Val::Float(100.0f64))?;e.set("extent",assigned880.clone())?;
let assigned884={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun887=e.get("tuple")?;let mut args885=Vec::new();let mut kw886=Vec::new();args885.push({let e=e.child();let out888=Val::list(vec![]);for item889 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun892=e.get("zip")?;let mut args890=Vec::new();let mut kw891=Vec::new();args890.push(e.get("origin")?);args890.push(e.get("normal")?);fun892.call(args890,kw891)?}}.iter()? {let unpack893=unpack(item889,2)?;e.set("p",unpack893[0].clone())?;e.set("n",unpack893[1].clone())?;out888.attr("append")?.call(vec![binary("sub",e.get("p")?,binary("mul",e.get("shell")?.attr("display_facet_thickness")?,e.get("n")?)?)?],vec![])?;}out888});fun887.call(args885,kw886)?}};e.set("back",assigned884.clone())?;
let assigned894={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun897={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun900=e.get("shell")?.attr("_halfspace")?;let mut args898=Vec::new();let mut kw899=Vec::new();args898.push(e.get("back")?);args898.push(e.get("normal")?);args898.push(e.get("extent")?);fun900.call(args898,kw899)?}}.attr("intersect")?;let mut args895=Vec::new();let mut kw896=Vec::new();args895.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun903=e.get("graph")?.attr("box")?;let mut args901=Vec::new();let mut kw902=Vec::new();args901.push(binary("sub",e.get("outer")?.get(Val::Int(0i64))?,e.get("extent")?)?);args901.push(binary("add",e.get("outer")?.get(Val::Int(1i64))?,e.get("extent")?)?);args901.push(binary("sub",e.get("outer")?.get(Val::Int(2i64))?,e.get("extent")?)?);args901.push(if {let v904=e.get("housing_back")?;let v905=Val::None;Val::Bool(compare("is",v904.clone(),v905.clone())?.truthy()?)}.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun908=e.get("shell")?.attr("housing_back_y")?;let mut args906=Vec::new();let mut kw907=Vec::new();args906.push(e.get("outer")?);fun908.call(args906,kw907)?}}} else {e.get("housing_back")?});args901.push(binary("sub",e.get("outer")?.get(Val::Int(4i64))?,e.get("extent")?)?);args901.push(binary("add",e.get("outer")?.get(Val::Int(5i64))?,e.get("extent")?)?);fun903.call(args901,kw902)?}});fun897.call(args895,kw896)?}};e.set("keepout",assigned894.clone())?;
let assigned909={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun912={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun915=e.get("shell")?.attr("_cavity")?;let mut args913=Vec::new();let mut kw914=Vec::new();args913.push(e.get("inner")?);fun915.call(args913,kw914)?}}.attr("cut")?;let mut args910=Vec::new();let mut kw911=Vec::new();args910.push(e.get("keepout")?);fun912.call(args910,kw911)?}};e.set("cavity",assigned909.clone())?;
let assigned916={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun919=e.get("shell")?.attr("housing_fill")?;let mut args917=Vec::new();let mut kw918=Vec::new();args917.push(e.get("box")?);fun919.call(args917,kw918)?}};e.set("fill",assigned916.clone())?;
if {let v920=e.get("fill")?;let v921=Val::None;Val::Bool(compare("is_not",v920.clone(),v921.clone())?.truthy()?)}.truthy()? {
let assigned922={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun925=e.get("cavity")?.attr("cut")?;let mut args923=Vec::new();let mut kw924=Vec::new();args923.push(e.get("fill")?);fun925.call(args923,kw924)?}};e.set("cavity",assigned922.clone())?;
}
let assigned926={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun929={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun932=e.get("structure")?.attr("cut")?;let mut args930=Vec::new();let mut kw931=Vec::new();args930.push(e.get("cavity")?);fun932.call(args930,kw931)?}}.attr("intersect")?;let mut args927=Vec::new();let mut kw928=Vec::new();args927.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun935=e.get("graph")?.attr("box")?;let mut args933=Vec::new();let mut kw934=Vec::new();args933.push(e.get("outer")?.get(Val::Int(0i64))?);args933.push(e.get("outer")?.get(Val::Int(1i64))?);args933.push(e.get("outer")?.get(Val::Int(2i64))?);args933.push(e.get("box")?.attr("y_joint")?);args933.push(e.get("outer")?.get(Val::Int(4i64))?);args933.push(e.get("outer")?.get(Val::Int(5i64))?);fun935.call(args933,kw934)?}});fun929.call(args927,kw928)?}};e.set("front",assigned926.clone())?;
for item936 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun939=e.get("shell")?.attr("_front_relief_cuts")?;let mut args937=Vec::new();let mut kw938=Vec::new();args937.push(e.get("inner")?);args937.push(e.get("shell")?.attr("fridge_reliefs")?);fun939.call(args937,kw938)?}}.iter()? {
e.set("cut",item936)?;let assigned940={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun943=e.get("front")?.attr("cut")?;let mut args941=Vec::new();let mut kw942=Vec::new();args941.push(e.get("cut")?);fun943.call(args941,kw942)?}};e.set("front",assigned940.clone())?;
}
let assigned944={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun947=e.get("front")?.attr("fuse")?;let mut args945=Vec::new();let mut kw946=Vec::new();args945.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun950=e.get("shell")?.attr("_front_lip")?;let mut args948=Vec::new();let mut kw949=Vec::new();args948.push(e.get("inner")?);args948.push(e.get("box")?.attr("y_joint")?);fun950.call(args948,kw949)?}});args945.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun953=e.get("shell")?.attr("_floor_tongue")?;let mut args951=Vec::new();let mut kw952=Vec::new();args951.push(e.get("inner")?);args951.push(e.get("box")?.attr("y_joint")?);fun953.call(args951,kw952)?}}.get(Val::Int(0i64))?);fun947.call(args945,kw946)?}};e.set("front",assigned944.clone())?;
let assigned954={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun957=e.get("front")?.attr("cut")?;let mut args955=Vec::new();let mut kw956=Vec::new();args955.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun960=e.get("shell")?.attr("_facet_wedge")?;let mut args958=Vec::new();let mut kw959=Vec::new();args958.push(e.get("outer")?);fun960.call(args958,kw959)?}});fun957.call(args955,kw956)?}};e.set("front",assigned954.clone())?;
let assigned961={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun964=e.get("front")?.attr("cut")?;let mut args962=Vec::new();let mut kw963=Vec::new();args962.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun967=e.get("shell")?.attr("_display_cuts")?;let mut args965=Vec::new();let mut kw966=Vec::new();args965.push(e.get("outer")?);args965.push(if e.get("box")?.attr("pump_bay")?.truthy()? {e.get("box")?.attr("pump_bay")?.get(Val::Int(2i64))?} else {Val::None});args965.push(if e.get("box")?.attr("pack")?.attr("collet_plate")?.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun970=e.get("shell")?.attr("bay_back_y")?;let mut args968=Vec::new();let mut kw969=Vec::new();args968.push(e.get("box")?.attr("pack")?.attr("collet_plate")?);fun970.call(args968,kw969)?}}} else {Val::None});kw966.push(("extend_wing_exits".into(),unary("not",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun973=e.get("bool")?;let mut args971=Vec::new();let mut kw972=Vec::new();args971.push({let v975=e.get("box")?.attr("pump_bay")?;if v975.truthy()? {{let v974=e.get("box")?.attr("pack")?.attr("collet_plate")?;if v974.truthy()? {e.get("box")?.attr("pack")?.attr("pump_trays")?} else {v974}}} else {v975}});fun973.call(args971,kw972)?}})?));fun967.call(args965,kw966)?}});fun964.call(args962,kw963)?}};e.set("front",assigned961.clone())?;
if e.get("box")?.attr("pack")?.attr("funnel")?.truthy()? {
let assigned976={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun979=e.get("front")?.attr("cut")?;let mut args977=Vec::new();let mut kw978=Vec::new();args977.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun982=e.get("shell")?.attr("_funnel_cut")?;let mut args980=Vec::new();let mut kw981=Vec::new();args980.push(e.get("inner")?);args980.push(e.get("outer")?);args980.push(e.get("box")?.attr("pack")?.attr("funnel")?);fun982.call(args980,kw981)?}});fun979.call(args977,kw978)?}};e.set("front",assigned976.clone())?;
}
for item983 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun986=e.get("shell")?.attr("_port_cuts")?;let mut args984=Vec::new();let mut kw985=Vec::new();args984.push(e.get("box")?.attr("pack")?.attr("front_ports")?);args984.push(binary("sub",e.get("outer")?.get(Val::Int(2i64))?,Val::Float(5.0f64))?);args984.push(binary("add",e.get("inner")?.get(Val::Int(2i64))?,Val::Float(5.0f64))?);fun986.call(args984,kw985)?}}.iter()? {
e.set("cut",item983)?;let assigned987={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun990=e.get("front")?.attr("cut")?;let mut args988=Vec::new();let mut kw989=Vec::new();args988.push(e.get("cut")?);fun990.call(args988,kw989)?}};e.set("front",assigned987.clone())?;
}
for item991 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun994=e.get("shell")?.attr("_x_port_cuts")?;let mut args992=Vec::new();let mut kw993=Vec::new();args992.push(e.get("box")?.attr("pack")?.attr("east_ports")?);args992.push(binary("sub",e.get("inner")?.get(Val::Int(1i64))?,Val::Float(5.0f64))?);args992.push(binary("add",e.get("outer")?.get(Val::Int(1i64))?,Val::Float(5.0f64))?);fun994.call(args992,kw993)?}}.iter()? {
e.set("cut",item991)?;let assigned995={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun998=e.get("front")?.attr("cut")?;let mut args996=Vec::new();let mut kw997=Vec::new();args996.push(e.get("cut")?);fun998.call(args996,kw997)?}};e.set("front",assigned995.clone())?;
}
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",line!());{let fun1001=e.get("front")?.attr("intersect")?;let mut args999=Vec::new();let mut kw1000=Vec::new();args999.push(e.get("structure")?);fun1001.call(args999,kw1000)?}});
Ok(Val::None)})})?;
    // numbers
    e.set("numbers", {
        let params = vec![
            ("shell".into(), None, false),
            ("box".into(), None, false),
            ("graph".into(), Some(Val::None), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1002 = {
                let v1006 = e.get("graph")?;
                if v1006.truthy()? {
                    v1006
                } else {
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun1005 = e.get("_Graph")?;
                            let mut args1003 = Vec::new();
                            let mut kw1004 = Vec::new();
                            fun1005.call(args1003, kw1004)?
                        }
                    }
                }
            };
            e.set("graph", assigned1002.clone())?;
            let assigned1007 = {
                let d = Val::dict(vec![]);
                d
            };
            e.get("graph")?.setattr("extras", assigned1007.clone())?;
            if e.get("box")?.attr("pack")?.attr("funnel")?.truthy()? {
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                        line!(),
                    );
                    {
                        let fun1010 = e.get("_funnel_containment")?;
                        let mut args1008 = Vec::new();
                        let mut kw1009 = Vec::new();
                        args1008.push(e.get("shell")?);
                        args1008.push(e.get("box")?);
                        fun1010.call(args1008, kw1009)?
                    }
                };
            }
            let assigned1011 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun1014 = e.get("graph")?.attr("add")?;
                    let mut args1012 = Vec::new();
                    let mut kw1013 = Vec::new();
                    args1012.push(Val::Str("silhouette".into()));
                    kw1013.push(("bounds".into(), e.get("box")?.attr("outer")?));
                    fun1014.call(args1012, kw1013)?
                }
            };
            e.set("structure", assigned1011.clone())?;
            let context1015 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun1018 = e.get("_record")?;
                    let mut args1016 = Vec::new();
                    let mut kw1017 = Vec::new();
                    args1016.push(e.get("shell")?);
                    args1016.push(e.get("graph")?);
                    args1016.push(e.get("structure")?);
                    fun1018.call(args1016, kw1017)?
                }
            };
            context1015.attr("__enter__")?.call(vec![], vec![])?;
            let context1019 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun1022 = e.get("_leaves")?;
                    let mut args1020 = Vec::new();
                    let mut kw1021 = Vec::new();
                    args1020.push(e.get("shell")?);
                    args1020.push(e.get("graph")?);
                    args1020.push(e.get("box")?);
                    fun1022.call(args1020, kw1021)?
                }
            };
            context1019.attr("__enter__")?.call(vec![], vec![])?;
            let context_result1031 = (|| -> Result<Flow> {
                let assigned1023 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                        line!(),
                    );
                    {
                        let fun1026 = e.get("_front_half")?;
                        let mut args1024 = Vec::new();
                        let mut kw1025 = Vec::new();
                        args1024.push(e.get("shell")?);
                        args1024.push(e.get("graph")?);
                        args1024.push(e.get("box")?);
                        args1024.push(e.get("structure")?);
                        fun1026.call(args1024, kw1025)?
                    }
                };
                e.set("half", assigned1023.clone())?;
                let assigned1027 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                        line!(),
                    );
                    {
                        let fun1030 = e.get("shell")?.attr("build_piece")?;
                        let mut args1028 = Vec::new();
                        let mut kw1029 = Vec::new();
                        args1028.push(e.get("box")?);
                        args1028.push(Val::Str("front".into()));
                        args1028.push(Val::Str("top".into()));
                        kw1029.push(("halves_cache".into(), {
                            let d = Val::dict(vec![]);
                            d.set(Val::Str("front".into()), e.get("half")?)?;
                            d
                        }));
                        fun1030.call(args1028, kw1029)?
                    }
                };
                e.set("result", assigned1027.clone())?;
                Ok(Flow::Continue)
            })();
            context1019
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            context1015
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            match context_result1031? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
            }
            let mod1032 = rt.import_module("_materials")?;
            e.set("linear", rt.member("_materials", "linear")?)?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun1035 = e.get("dict")?;
                    let mut args1033 = Vec::new();
                    let mut kw1034 = Vec::new();
                    args1033.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun1038 = e.get("_enclosure_structure")?.attr("numbers")?;
                            let mut args1036 = Vec::new();
                            let mut kw1037 = Vec::new();
                            args1036.push(e.get("box")?.attr("outer")?);
                            fun1038.call(args1036, kw1037)?
                        }
                    });
                    kw1034.push(("color".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun1041 = e.get("linear")?;
                            let mut args1039 = Vec::new();
                            let mut kw1040 = Vec::new();
                            args1039.push(
                                e.get("shell")?
                                    .attr("PIECE_COLORS")?
                                    .get(Val::Str("front-top".into()))?,
                            );
                            fun1041.call(args1039, kw1040)?
                        }
                    }));
                    kw1034.push(("panel".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun1044 = e.get("graph")?.attr("document")?;
                            let mut args1042 = Vec::new();
                            let mut kw1043 = Vec::new();
                            args1042.push(e.get("result")?);
                            args1042.push(e.get("graph")?.attr("extras")?);
                            fun1044.call(args1042, kw1043)?
                        }
                    }));
                    kw1034.push(("panel_bounds".into(), e.get("result")?.attr("bounds")?));
                    kw1034.push(("front_corners".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun1047 = e.get("_corner_numbers")?;
                            let mut args1045 = Vec::new();
                            let mut kw1046 = Vec::new();
                            args1045.push(e.get("shell")?);
                            args1045.push(e.get("box")?.attr("outer")?);
                            fun1047.call(args1045, kw1046)?
                        }
                    }));
                    fun1035.call(args1033, kw1034)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // print_numbers
    e.set("print_numbers", {
        let params = vec![("shell".into(), None, false), ("box".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_enclosure_skin", rt.import_module("_enclosure_skin")?)?;
            let assigned1048 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun1051 = e
                        .get("shell")?
                        .attr("_above_core_shell")?
                        .attr("rear_identification")?;
                    let mut args1049 = Vec::new();
                    let mut kw1050 = Vec::new();
                    fun1051.call(args1049, kw1050)?
                }
            };
            e.set("identification", assigned1048.clone())?;
            let assigned1052 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun1055 = e.get("identification")?.attr("nameplate_station")?;
                    let mut args1053 = Vec::new();
                    let mut kw1054 = Vec::new();
                    fun1055.call(args1053, kw1054)?
                }
            };
            e.set("station", assigned1052.clone())?;
            let assigned1056 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun1059 = e.get("identification")?.attr("nameplate_plan")?;
                    let mut args1057 = Vec::new();
                    let mut kw1058 = Vec::new();
                    fun1059.call(args1057, kw1058)?
                }
            };
            e.set("plan", assigned1056.clone())?;
            let assigned1060 = e
                .get("identification")?
                .attr("nameplate")?
                .attr("wing_interface")?;
            e.set("wing", assigned1060.clone())?;
            let assigned1061 = {
                let mut s = Vec::new();
                s.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                        line!(),
                    );
                    {
                        let fun1064 = e.get("shell")?.attr("disposal_field")?;
                        let mut args1062 = Vec::new();
                        let mut kw1063 = Vec::new();
                        args1062.push(e.get("box")?.attr("outer")?);
                        fun1064.call(args1062, kw1063)?
                    }
                });
                s.extend(
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun1067 = e.get("wing")?.attr("plain_lips")?;
                            let mut args1065 = Vec::new();
                            let mut kw1066 = Vec::new();
                            args1065.push(e.get("station")?);
                            args1065.push(e.get("plan")?.get(Val::Str("face_y_mm".into()))?);
                            fun1067.call(args1065, kw1066)?
                        }
                    }
                    .iter()?,
                );
                s.extend(
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun1070 = e.get("identification")?.attr("rail_bounds")?;
                            let mut args1068 = Vec::new();
                            let mut kw1069 = Vec::new();
                            fun1070.call(args1068, kw1069)?
                        }
                    }
                    .iter()?,
                );
                s.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                        line!(),
                    );
                    {
                        let fun1073 = e
                            .get("shell")?
                            .attr("_above_core_shell")?
                            .attr("keystone_land")?;
                        let mut args1071 = Vec::new();
                        let mut kw1072 = Vec::new();
                        fun1073.call(args1071, kw1072)?
                    }
                });
                Val::tuple(s)
            };
            e.set("plain", assigned1061.clone())?;
            if e.get("box")?.attr("pack")?.attr("nameplate")?.truthy()? {
                e.set(
                    "plain",
                    binary("add", e.get("plain")?, {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun1076 =
                                e.get("shell")?.attr("_nameplate_fit")?.attr("plain_lips")?;
                            let mut args1074 = Vec::new();
                            let mut kw1075 = Vec::new();
                            args1074.push(e.get("box")?.attr("pack")?.attr("nameplate")?);
                            args1074.push(e.get("box")?.attr("outer")?.get(Val::Int(3i64))?);
                            fun1076.call(args1074, kw1075)?
                        }
                    })?,
                )?;
            }
            if e.get("box")?.attr("pack")?.attr("keystone")?.truthy()? {
                e.set(
                    "plain",
                    binary("add", e.get("plain")?, {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun1079 = e.get("shell")?.attr("_data_fit")?.attr("plain_lips")?;
                            let mut args1077 = Vec::new();
                            let mut kw1078 = Vec::new();
                            args1077.push(e.get("box")?.attr("pack")?.attr("keystone")?);
                            args1077.push(e.get("box")?.attr("outer")?.get(Val::Int(3i64))?);
                            fun1079.call(args1077, kw1078)?
                        }
                    })?,
                )?;
            }
            let assigned1080 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun1083 = e.get("numbers")?;
                    let mut args1081 = Vec::new();
                    let mut kw1082 = Vec::new();
                    args1081.push(e.get("shell")?);
                    args1081.push(e.get("box")?);
                    fun1083.call(args1081, kw1082)?
                }
            };
            e.set("out", assigned1080.clone())?;
            e.set("layout", rt.import_module("above_core")?)?;
            let assigned1084 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun1087 = e.get("layout")?.attr("specification")?;
                    let mut args1085 = Vec::new();
                    let mut kw1086 = Vec::new();
                    fun1087.call(args1085, kw1086)?
                }
            }
            .get(Val::Str("rear_wall".into()))?
            .get(Val::Str("rear_wall".into()))?
            .get(Val::Str("ymax".into()))?;
            e.set("face", assigned1084.clone())?;
            let assigned1088 = binary(
                "add",
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                        line!(),
                    );
                    {
                        let fun1091 = e.get("max")?;
                        let mut args1089 = Vec::new();
                        let mut kw1090 = Vec::new();
                        args1089.push(e.get("shell")?.attr("flute_rise")?);
                        args1089.push(
                            e.get("_enclosure_skin")?
                                .attr("reeding")?
                                .attr("flute_width")?,
                        );
                        fun1091.call(args1089, kw1090)?
                    }
                },
                e.get("shell")?.attr("_flute_skin")?.attr("face_tol")?,
            )?;
            e.set("reach", assigned1088.clone())?;
            let assigned1092 = e.get("out")?.get(Val::Str("panel_bounds".into()))?;
            e.set("bounds", assigned1092.clone())?;
            if {
                let v1095 = {
                    let v1096 = e.get("bounds")?;
                    let v1097 = Val::None;
                    Val::Bool(compare("is", v1096.clone(), v1097.clone())?.truthy()?)
                };
                if v1095.truthy()? {
                    v1095
                } else {
                    {
                        let v1093 = binary(
                            "add",
                            e.get("bounds")?.get(Val::Int(3i64))?,
                            e.get("reach")?,
                        )?;
                        let v1094 = binary("sub", e.get("face")?, Val::Float(3.0f64))?;
                        Val::Bool(compare("ge", v1093.clone(), v1094.clone())?.truthy()?)
                    }
                }
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun1100 = e.get("ValueError")?;
                            let mut args1098 = Vec::new();
                            let mut kw1099 = Vec::new();
                            args1098.push(Val::Str(
                                "the rear receiver land reaches the front-top print boundary"
                                    .into(),
                            ));
                            fun1100.call(args1098, kw1099)?
                        }
                    })?
                );
            }
            let assigned1101 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun1104 = e.get("shell")?.attr("_flute_skin")?.attr("Rail")?;
                    let mut args1102 = Vec::new();
                    let mut kw1103 = Vec::new();
                    kw1103.push(("at".into(), {
                        let params = vec![("s".into(), None, false)];
                        let outer = e.clone();
                        let runtime = rt.clone();
                        Val::function(move |args, kwargs| {
                            let rt = runtime.clone();
                            let e = bind(&outer, &params, args, kwargs, None, None)?;
                            let _frame = rt.frame(&outer);
                            return Ok({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                                    line!(),
                                );
                                {
                                    let fun1107 = e.get("shell")?.attr("plan_at")?;
                                    let mut args1105 = Vec::new();
                                    let mut kw1106 = Vec::new();
                                    args1105.push(e.get("s")?);
                                    args1105.push(e.get("box")?.attr("outer")?);
                                    fun1107.call(args1105, kw1106)?
                                }
                            });
                            Ok(Val::None)
                        })
                    }));
                    kw1103.push(("length".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun1110 = e.get("shell")?.attr("plan_perimeter")?;
                            let mut args1108 = Vec::new();
                            let mut kw1109 = Vec::new();
                            args1108.push(e.get("box")?.attr("outer")?);
                            fun1110.call(args1108, kw1109)?
                        }
                    }));
                    kw1103.push(("plain".into(), e.get("plain")?));
                    fun1104.call(args1102, kw1103)?
                }
            };
            e.set("rail", assigned1101.clone())?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun1113 = e.get("out")?.attr("update")?;
                    let mut args1111 = Vec::new();
                    let mut kw1112 = Vec::new();
                    args1111.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun1116 = e.get("_enclosure_skin")?.attr("field_numbers")?;
                            let mut args1114 = Vec::new();
                            let mut kw1115 = Vec::new();
                            args1114.push({
                                let mut s = Vec::new();
                                s.push(e.get("rail")?);
                                Val::list(s)
                            });
                            args1114.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                                    line!(),
                                );
                                {
                                    let fun1119 = e.get("shell")?.attr("flute_pitch")?;
                                    let mut args1117 = Vec::new();
                                    let mut kw1118 = Vec::new();
                                    args1117.push(e.get("box")?.attr("outer")?);
                                    fun1119.call(args1117, kw1118)?
                                }
                            });
                            args1114.push(e.get("shell")?.attr("flute_depth")?);
                            args1114.push(e.get("shell")?.attr("flute_rise")?);
                            fun1116.call(args1114, kw1115)?
                        }
                    });
                    fun1113.call(args1111, kw1112)?
                }
            };
            let assigned1120 = {
                let d = Val::dict(vec![]);
                d.set(
                    Val::Str("front_panel_ymax_mm".into()),
                    e.get("bounds")?.get(Val::Int(3i64))?,
                )?;
                d.set(Val::Str("field_reach_mm".into()), e.get("reach")?)?;
                d.set(
                    Val::Str("rear_land_ymin_mm".into()),
                    binary("sub", e.get("face")?, Val::Float(3.0f64))?,
                )?;
                d
            };
            e.get("out")?.set(
                Val::Str("disjoint_receiver_land".into()),
                assigned1120.clone(),
            )?;
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    // cut
    e.set("cut", {
        let params = vec![
            ("shell".into(), None, false),
            ("box".into(), None, false),
            ("directory".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod1121 = rt.import_module("pathlib")?;
            e.set("Path", rt.member("pathlib", "Path")?)?;
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            let mod1122 = rt.import_module("_enclosure_presentation")?;
            e.set(
                "print_payload",
                rt.member("_enclosure_presentation", "print_payload")?,
            )?;
            let assigned1123 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun1126 = e.get("_rust_part")?.attr("cut")?;
                    let mut args1124 = Vec::new();
                    let mut kw1125 = Vec::new();
                    args1124.push(Val::Str("enclosure-shell".into()));
                    args1124.push(Val::Str("enclosure-front-top".into()));
                    args1124.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                            line!(),
                        );
                        {
                            let fun1129 = e.get("print_numbers")?;
                            let mut args1127 = Vec::new();
                            let mut kw1128 = Vec::new();
                            args1127.push(e.get("shell")?);
                            args1127.push(e.get("box")?);
                            fun1129.call(args1127, kw1128)?
                        }
                    });
                    args1124.push(e.get("directory")?);
                    fun1126.call(args1124, kw1125)?
                }
            };
            e.set("said", assigned1123.clone())?;
            let assigned1130 = binary(
                "truediv",
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                        line!(),
                    );
                    {
                        let fun1133 = e.get("Path")?;
                        let mut args1131 = Vec::new();
                        let mut kw1132 = Vec::new();
                        args1131.push(e.get("directory")?);
                        fun1133.call(args1131, kw1132)?
                    }
                },
                Val::Str("enclosure-front-top.step".into()),
            )?;
            e.set("step", assigned1130.clone())?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_front_top.rs",
                    line!(),
                );
                {
                    let fun1136 = e.get("print_payload")?;
                    let mut args1134 = Vec::new();
                    let mut kw1135 = Vec::new();
                    args1134.push(e.get("step")?);
                    kw1135.push(("check_print".into(), Val::Bool(true)));
                    fun1136.call(args1134, kw1135)?
                }
            };
            return Ok(e.get("said")?);
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
