//! Front-top's tee wall, the pump tees that stand in it and the stem elbows of their returns.
//!
//! Each pump port feeds a purchased PP0208E tee (`fixed_returns`). Its branch stands in the TEE
//! WALL: front-top's bay bulkhead, one flat slab the bay's whole width and height
//! (`enclosure._bulkhead`). Each tee has one collar-clear bore through the wall from its bore
//! face; ahead of the bore a smaller hole through the wall's fore band passes the pump tube and
//! leaves room for the branch collet to stand extended and grip it. The bore holds the tee in X
//! and Z. Its fixed branch barrel stops it fore on the bore face, clear of the collet, and its
//! lower return, anchored in the rear valve, stops it aft.
//!
//! Each lower return carries a NeoFit stem elbow in the tee's lower collet and another in the rear
//! valve's bottom collet, their stems cut to stand where `fixed_returns.elbow_return` puts them.
//!
//! Every wall cut is a horizontal bore in a piece printed on Z, so each is teardropped.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("functools")?;
    e.set("lru_cache", rt.member("functools", "lru_cache")?)?;
    let mod2 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
    let assigned3 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
            line!(),
        );
        {
            let fun6 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun9 = e.get("Path")?;
                    let mut args7 = Vec::new();
                    let mut kw8 = Vec::new();
                    args7.push(e.get("__file__")?);
                    fun9.call(args7, kw8)?
                }
            }
            .attr("resolve")?;
            let mut args4 = Vec::new();
            let mut kw5 = Vec::new();
            fun6.call(args4, kw5)?
        }
    }
    .attr("parent")?;
    e.set("HERE", assigned3.clone())?;
    let assigned10 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
            line!(),
        );
        {
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
        }
    };
    e.set("HW", assigned10.clone())?;
    for item18 in {
        let mut s = Vec::new();
        s.push(binary(
            "truediv",
            binary("truediv", e.get("HW")?, Val::Str("printed-parts".into()))?,
            Val::Str("cadlib".into()),
        )?);
        s.push(binary(
            "truediv",
            binary(
                "truediv",
                binary("truediv", e.get("HW")?, Val::Str("printed-parts".into()))?,
                Val::Str("enclosure".into()),
            )?,
            Val::Str("enclosure".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("HW")?, Val::Str("reference".into()))?,
            Val::Str("tee-connector".into()),
        )?);
        s.push(binary(
            "truediv",
            binary("truediv", e.get("HW")?, Val::Str("reference".into()))?,
            Val::Str("neofit-stem-elbow".into()),
        )?);
        s.push(binary("truediv", e.get("HW")?, Val::Str("scripts".into()))?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("_p", item18)?;
        if {
            let v22 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun21 = e.get("str")?;
                    let mut args19 = Vec::new();
                    let mut kw20 = Vec::new();
                    args19.push(e.get("_p")?);
                    fun21.call(args19, kw20)?
                }
            };
            let v23 = e.get("sys")?.attr("path")?;
            Val::Bool(compare("not_in", v22.clone(), v23.clone())?.truthy()?)
        }
        .truthy()?
        {
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun26 = e.get("sys")?.attr("path")?.attr("insert")?;
                    let mut args24 = Vec::new();
                    let mut kw25 = Vec::new();
                    args24.push(Val::Int(0i64));
                    args24.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                            line!(),
                        );
                        {
                            let fun29 = e.get("str")?;
                            let mut args27 = Vec::new();
                            let mut kw28 = Vec::new();
                            args27.push(e.get("_p")?);
                            fun29.call(args27, kw28)?
                        }
                    });
                    fun26.call(args24, kw25)?
                }
            };
        }
    }
    e.set("fits", rt.import_module("fits")?)?;
    e.set("tee", rt.import_module("tee_connector")?)?;
    e.set("plumbing", rt.import_module("fixed_returns")?)?;
    e.set("stem_elbow", rt.import_module("neofit_stem_elbow")?)?;
    let assigned30 = {
        let mut s = Vec::new();
        s.push(Val::Str("west-outer".into()));
        s.push(Val::Str("west-inner".into()));
        s.push(Val::Str("east-inner".into()));
        s.push(Val::Str("east-outer".into()));
        Val::tuple(s)
    };
    e.set("STATIONS", assigned30.clone())?;
    let assigned31 = {
        let d = Val::dict(vec![]);
        d.set(Val::Str("west-outer".into()), Val::Str("Y-G".into()))?;
        d.set(Val::Str("west-inner".into()), Val::Str("Y-F".into()))?;
        d.set(Val::Str("east-inner".into()), Val::Str("Y-C".into()))?;
        d.set(Val::Str("east-outer".into()), Val::Str("Y-D".into()))?;
        d
    };
    e.set("TEES", assigned31.clone())?;
    let assigned32 = binary(
        "add",
        binary(
            "truediv",
            e.get("tee")?.attr("COLLAR_ENVELOPE_D")?,
            Val::Float(2.0f64),
        )?,
        e.get("fits")?.attr("running")?,
    )?;
    e.set("BORE_R", assigned32.clone())?;
    let assigned33 = Val::Float(1.454f64);
    e.set("BODY_AIR", assigned33.clone())?;
    let assigned34 = binary(
        "add",
        e.get("tee")?.attr("COLLET_NOSE_R")?,
        e.get("fits")?.attr("running")?,
    )?;
    e.set("HOLE_R", assigned34.clone())?;
    let assigned35 = Val::Float(8.1f64);
    e.set("RETURN_CHANNEL_R", assigned35.clone())?;
    let assigned36 = Val::Float(36.0f64);
    e.set("TEARDROP_DEG", assigned36.clone())?;
    // box
    e.set("box", {
        let params = vec![
            ("x0".into(), None, false),
            ("x1".into(), None, false),
            ("y0".into(), None, false),
            ("y1".into(), None, false),
            ("z0".into(), None, false),
            ("z1".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun39 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                    let mut args37 = Vec::new();
                    let mut kw38 = Vec::new();
                    args37.push(binary("sub", e.get("x1")?, e.get("x0")?)?);
                    args37.push(binary("sub", e.get("y1")?, e.get("y0")?)?);
                    args37.push(binary("sub", e.get("z1")?, e.get("z0")?)?);
                    args37.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                            line!(),
                        );
                        {
                            let fun42 = e.get("cq")?.attr("Vector")?;
                            let mut args40 = Vec::new();
                            let mut kw41 = Vec::new();
                            args40.push(e.get("x0")?);
                            args40.push(e.get("y0")?);
                            args40.push(e.get("z0")?);
                            fun42.call(args40, kw41)?
                        }
                    });
                    fun39.call(args37, kw38)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // ycyl
    e.set("ycyl", {
        let params = vec![
            ("radius".into(), None, false),
            ("x".into(), None, false),
            ("z".into(), None, false),
            ("y0".into(), None, false),
            ("y1".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun45 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                    let mut args43 = Vec::new();
                    let mut kw44 = Vec::new();
                    args43.push(e.get("radius")?);
                    args43.push(binary("sub", e.get("y1")?, e.get("y0")?)?);
                    args43.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                            line!(),
                        );
                        {
                            let fun48 = e.get("cq")?.attr("Vector")?;
                            let mut args46 = Vec::new();
                            let mut kw47 = Vec::new();
                            args46.push(e.get("x")?);
                            args46.push(e.get("y0")?);
                            args46.push(e.get("z")?);
                            fun48.call(args46, kw47)?
                        }
                    });
                    args43.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                            line!(),
                        );
                        {
                            let fun51 = e.get("cq")?.attr("Vector")?;
                            let mut args49 = Vec::new();
                            let mut kw50 = Vec::new();
                            args49.push(Val::Int(0i64));
                            args49.push(Val::Int(1i64));
                            args49.push(Val::Int(0i64));
                            fun51.call(args49, kw50)?
                        }
                    });
                    fun45.call(args43, kw44)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // fused
    e.set("fused", {
        let params = vec![("parts".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned52 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun55 = e.get("tuple")?;
                    let mut args53 = Vec::new();
                    let mut kw54 = Vec::new();
                    args53.push(e.get("parts")?);
                    fun55.call(args53, kw54)?
                }
            };
            e.set("parts", assigned52.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun58 = if {
                        let v62 = {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                                line!(),
                            );
                            {
                                let fun61 = e.get("len")?;
                                let mut args59 = Vec::new();
                                let mut kw60 = Vec::new();
                                args59.push(e.get("parts")?);
                                fun61.call(args59, kw60)?
                            }
                        };
                        let v63 = Val::Int(1i64);
                        Val::Bool(compare("gt", v62.clone(), v63.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                                line!(),
                            );
                            {
                                let fun66 = e.get("parts")?.get(Val::Int(0i64))?.attr("fuse")?;
                                let mut args64 = Vec::new();
                                let mut kw65 = Vec::new();
                                args64.extend(
                                    e.get("parts")?
                                        .get(Val::Slice {
                                            start: Some(Val::Int(1i64).integer()?),
                                            stop: None,
                                            step: 1,
                                        })?
                                        .iter()?,
                                );
                                fun66.call(args64, kw65)?
                            }
                        }
                    } else {
                        e.get("parts")?.get(Val::Int(0i64))?
                    }
                    .attr("clean")?;
                    let mut args56 = Vec::new();
                    let mut kw57 = Vec::new();
                    fun58.call(args56, kw57)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // teardrop_y
    e.set("teardrop_y",{let params=vec![("r".into(),None,false),("x".into(),None,false),("z".into(),None,false),("y0".into(),None,false),("y1".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned67={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun70=e.get("math")?.attr("radians")?;let mut args68=Vec::new();let mut kw69=Vec::new();args68.push(e.get("TEARDROP_DEG")?);fun70.call(args68,kw69)?}};e.set("a",assigned67.clone())?;
let assigned71={let mut s=Vec::new();s.push(binary("mul",e.get("r")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun74=e.get("math")?.attr("sin")?;let mut args72=Vec::new();let mut kw73=Vec::new();args72.push(e.get("a")?);fun74.call(args72,kw73)?}})?);s.push(binary("add",e.get("z")?,binary("mul",e.get("r")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun77=e.get("math")?.attr("cos")?;let mut args75=Vec::new();let mut kw76=Vec::new();args75.push(e.get("a")?);fun77.call(args75,kw76)?}})?)?);s.push(binary("add",e.get("z")?,binary("truediv",e.get("r")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun80=e.get("math")?.attr("cos")?;let mut args78=Vec::new();let mut kw79=Vec::new();args78.push(e.get("a")?);fun80.call(args78,kw79)?}})?)?);Val::tuple(s)};let unpack81=unpack(assigned71.clone(),3)?;e.set("half",unpack81[0].clone())?;e.set("tangent",unpack81[1].clone())?;e.set("apex",unpack81[2].clone())?;
let assigned82={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun85={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun88={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun91={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun94={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun97=e.get("cq")?.attr("Workplane")?;let mut args95=Vec::new();let mut kw96=Vec::new();args95.push(Val::Str("XZ".into()));kw96.push(("origin".into(),{let mut s=Vec::new();s.push(Val::Int(0i64));s.push(e.get("y0")?);s.push(Val::Int(0i64));Val::tuple(s)}));fun97.call(args95,kw96)?}}.attr("polyline")?;let mut args92=Vec::new();let mut kw93=Vec::new();args92.push({let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(binary("sub",e.get("x")?,e.get("half")?)?);s.push(e.get("tangent")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("add",e.get("x")?,e.get("half")?)?);s.push(e.get("tangent")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(e.get("x")?);s.push(e.get("apex")?);Val::tuple(s)});Val::list(s)});fun94.call(args92,kw93)?}}.attr("close")?;let mut args89=Vec::new();let mut kw90=Vec::new();fun91.call(args89,kw90)?}}.attr("extrude")?;let mut args86=Vec::new();let mut kw87=Vec::new();args86.push(unary("neg",binary("sub",e.get("y1")?,e.get("y0")?)?)?);fun88.call(args86,kw87)?}}.attr("val")?;let mut args83=Vec::new();let mut kw84=Vec::new();fun85.call(args83,kw84)?}};e.set("roof",assigned82.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun100={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun103=e.get("ycyl")?;let mut args101=Vec::new();let mut kw102=Vec::new();args101.push(e.get("r")?);args101.push(e.get("x")?);args101.push(e.get("z")?);args101.push(e.get("y0")?);args101.push(e.get("y1")?);fun103.call(args101,kw102)?}}.attr("fuse")?;let mut args98=Vec::new();let mut kw99=Vec::new();args98.push(e.get("roof")?);fun100.call(args98,kw99)?}});
Ok(Val::None)})})?;
    // stations
    e.set("stations", {
        let params = vec![("plate".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let e = e.child();
                let out104 = Val::list(vec![]);
                for item105 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun108 = e.get("zip")?;
                        let mut args106 = Vec::new();
                        let mut kw107 = Vec::new();
                        args106.push(e.get("STATIONS")?);
                        args106.push(e.get("plate")?.get(Val::Str("holes".into()))?);
                        fun108.call(args106, kw107)?
                    }
                }
                .iter()?
                {
                    let unpack109 = unpack(item105, 2)?;
                    e.set("name", unpack109[0].clone())?;
                    let unpack110 = unpack(unpack109[1].clone(), 2)?;
                    e.set("x", unpack110[0].clone())?;
                    e.set("z", unpack110[1].clone())?;
                    out104.attr("append")?.call(
                        vec![{
                            let mut s = Vec::new();
                            s.push(e.get("name")?);
                            s.push(e.get("TEES")?.get(e.get("name")?)?);
                            s.push(e.get("x")?);
                            s.push(e.get("z")?);
                            Val::tuple(s)
                        }],
                        vec![],
                    )?;
                }
                out104
            });
            Ok(Val::None)
        })
    })?;
    // wall_aft_y
    e.set("wall_aft_y", {
        let params = vec![("fore_y".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary(
                "sub",
                binary(
                    "sub",
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                            line!(),
                        );
                        {
                            let fun113 = e.get("plumbing")?.attr("tee_axis_y")?;
                            let mut args111 = Vec::new();
                            let mut kw112 = Vec::new();
                            args111.push(e.get("fore_y")?);
                            fun113.call(args111, kw112)?
                        }
                    },
                    e.get("tee")?.attr("BARREL_R")?,
                )?,
                e.get("BODY_AIR")?,
            )?);
            Ok(Val::None)
        })
    })?;
    // bore_depth
    e.set("bore_depth", {
        let params = vec![("plate".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary(
                "sub",
                e.get("plate")?.get(Val::Str("wall_aft_y".into()))?,
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun116 = e.get("plumbing")?.attr("plate_aft_y")?;
                        let mut args114 = Vec::new();
                        let mut kw115 = Vec::new();
                        args114.push(e.get("plate")?.get(Val::Str("fore_y".into()))?);
                        fun116.call(args114, kw115)?
                    }
                },
            )?);
            Ok(Val::None)
        })
    })?;
    // return_clearances
    e.set("return_clearances", {
        let params = vec![("plate".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned117 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("out", assigned117.clone())?;
            for item118 in {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun121 = e
                        .get("plate")?
                        .get(Val::Str("return_ports".into()))?
                        .attr("values")?;
                    let mut args119 = Vec::new();
                    let mut kw120 = Vec::new();
                    fun121.call(args119, kw120)?
                }
            }
            .iter()?
            {
                e.set("port", item118)?;
                let assigned122 = e.get("port")?.get(Val::Str("point".into()))?;
                let unpack123 = unpack(assigned122.clone(), 3)?;
                e.set("x", unpack123[0].clone())?;
                e.set("y", unpack123[1].clone())?;
                e.set("z", unpack123[2].clone())?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun126 = e.get("out")?.attr("append")?;
                        let mut args124 = Vec::new();
                        let mut kw125 = Vec::new();
                        args124.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                                line!(),
                            );
                            {
                                let fun129 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                                let mut args127 = Vec::new();
                                let mut kw128 = Vec::new();
                                args127.push(e.get("RETURN_CHANNEL_R")?);
                                args127.push(binary(
                                    "sub",
                                    binary("add", e.get("z")?, Val::Float(20.0f64))?,
                                    binary(
                                        "sub",
                                        e.get("plate")?.get(Val::Str("z0".into()))?,
                                        Val::Float(1.0f64),
                                    )?,
                                )?);
                                args127.push({
                                    let _site = rt.source_at(
                                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                                        line!(),
                                    );
                                    {
                                        let fun132 = e.get("cq")?.attr("Vector")?;
                                        let mut args130 = Vec::new();
                                        let mut kw131 = Vec::new();
                                        args130.push(e.get("x")?);
                                        args130.push(e.get("y")?);
                                        args130.push(binary(
                                            "sub",
                                            e.get("plate")?.get(Val::Str("z0".into()))?,
                                            Val::Float(1.0f64),
                                        )?);
                                        fun132.call(args130, kw131)?
                                    }
                                });
                                args127.push({
                                    let _site = rt.source_at(
                                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                                        line!(),
                                    );
                                    {
                                        let fun135 = e.get("cq")?.attr("Vector")?;
                                        let mut args133 = Vec::new();
                                        let mut kw134 = Vec::new();
                                        args133.push(Val::Int(0i64));
                                        args133.push(Val::Int(0i64));
                                        args133.push(Val::Int(1i64));
                                        fun135.call(args133, kw134)?
                                    }
                                });
                                fun129.call(args127, kw128)?
                            }
                        });
                        fun126.call(args124, kw125)?
                    }
                };
            }
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    // plate_holes
    e.set("plate_holes", {
        let params = vec![("plate".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned136 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("plate")?.get(Val::Str("fore_y".into()))?,
                    Val::Float(1.0f64),
                )?);
                s.push(binary(
                    "add",
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                            line!(),
                        );
                        {
                            let fun139 = e.get("plumbing")?.attr("plate_aft_y")?;
                            let mut args137 = Vec::new();
                            let mut kw138 = Vec::new();
                            args137.push(e.get("plate")?.get(Val::Str("fore_y".into()))?);
                            fun139.call(args137, kw138)?
                        }
                    },
                    Val::Float(1.0f64),
                )?);
                Val::tuple(s)
            };
            let unpack140 = unpack(assigned136.clone(), 2)?;
            e.set("y0", unpack140[0].clone())?;
            e.set("y1", unpack140[1].clone())?;
            return Ok({
                let e = e.child();
                let out141 = Val::list(vec![]);
                for item142 in e.get("plate")?.get(Val::Str("holes".into()))?.iter()? {
                    let unpack143 = unpack(item142, 2)?;
                    e.set("x", unpack143[0].clone())?;
                    e.set("z", unpack143[1].clone())?;
                    out141.attr("append")?.call(
                        vec![{
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                                line!(),
                            );
                            {
                                let fun146 = e.get("teardrop_y")?;
                                let mut args144 = Vec::new();
                                let mut kw145 = Vec::new();
                                args144.push(e.get("HOLE_R")?);
                                args144.push(e.get("x")?);
                                args144.push(e.get("z")?);
                                args144.push(e.get("y0")?);
                                args144.push(e.get("y1")?);
                                fun146.call(args144, kw145)?
                            }
                        }],
                        vec![],
                    )?;
                }
                out141
            });
            Ok(Val::None)
        })
    })?;
    // tee_bores
    e.set("tee_bores", {
        let params = vec![("plate".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned147 = {
                let mut s = Vec::new();
                s.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun150 = e.get("plumbing")?.attr("plate_aft_y")?;
                        let mut args148 = Vec::new();
                        let mut kw149 = Vec::new();
                        args148.push(e.get("plate")?.get(Val::Str("fore_y".into()))?);
                        fun150.call(args148, kw149)?
                    }
                });
                s.push(binary(
                    "add",
                    e.get("plate")?.get(Val::Str("wall_aft_y".into()))?,
                    Val::Float(1.0f64),
                )?);
                Val::tuple(s)
            };
            let unpack151 = unpack(assigned147.clone(), 2)?;
            e.set("y0", unpack151[0].clone())?;
            e.set("y1", unpack151[1].clone())?;
            return Ok({
                let e = e.child();
                let out152 = Val::list(vec![]);
                for item153 in e.get("plate")?.get(Val::Str("holes".into()))?.iter()? {
                    let unpack154 = unpack(item153, 2)?;
                    e.set("x", unpack154[0].clone())?;
                    e.set("z", unpack154[1].clone())?;
                    out152.attr("append")?.call(
                        vec![{
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                                line!(),
                            );
                            {
                                let fun157 = e.get("teardrop_y")?;
                                let mut args155 = Vec::new();
                                let mut kw156 = Vec::new();
                                args155.push(e.get("BORE_R")?);
                                args155.push(e.get("x")?);
                                args155.push(e.get("z")?);
                                args155.push(e.get("y0")?);
                                args155.push(e.get("y1")?);
                                fun157.call(args155, kw156)?
                            }
                        }],
                        vec![],
                    )?;
                }
                out152
            });
            Ok(Val::None)
        })
    })?;
    // wall_cuts
    e.set("wall_cuts", {
        let params = vec![("plate".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary(
                "add",
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun160 = e.get("plate_holes")?;
                        let mut args158 = Vec::new();
                        let mut kw159 = Vec::new();
                        args158.push(e.get("plate")?);
                        fun160.call(args158, kw159)?
                    }
                },
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun163 = e.get("tee_bores")?;
                        let mut args161 = Vec::new();
                        let mut kw162 = Vec::new();
                        args161.push(e.get("plate")?);
                        fun163.call(args161, kw162)?
                    }
                },
            )?);
            Ok(Val::None)
        })
    })?;
    e.set("_tee_native",memoize({let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let mod164=rt.import_module("_cadq_export")?;e.set("import_step",rt.member("_cadq_export","import_step")?)?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun167={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun170=e.get("import_step")?;let mut args168=Vec::new();let mut kw169=Vec::new();args168.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun173=e.get("str")?;let mut args171=Vec::new();let mut kw172=Vec::new();args171.push(binary("truediv",binary("truediv",binary("truediv",e.get("HW")?,Val::Str("reference".into()))?,Val::Str("tee-connector".into()))?,Val::Str("tee-connector.step".into()))?);fun173.call(args171,kw172)?}});fun170.call(args168,kw169)?}}.attr("val")?;let mut args165=Vec::new();let mut kw166=Vec::new();fun167.call(args165,kw166)?}});
Ok(Val::None)})},Some(1usize)))?; // tee_body
    e.set("tee_body", {
        let params = vec![
            ("plate".into(), None, false),
            ("x".into(), None, false),
            ("z".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned174 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun177 = e.get("plumbing")?.attr("tee_axis_y")?;
                    let mut args175 = Vec::new();
                    let mut kw176 = Vec::new();
                    args175.push(e.get("plate")?.get(Val::Str("fore_y".into()))?);
                    fun177.call(args175, kw176)?
                }
            };
            e.set("y", assigned174.clone())?;
            let assigned178 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun181 = e.get("cq")?.attr("Location")?;
                    let mut args179 = Vec::new();
                    let mut kw180 = Vec::new();
                    args179.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                            line!(),
                        );
                        {
                            let fun184 = e.get("cq")?.attr("Plane")?;
                            let mut args182 = Vec::new();
                            let mut kw183 = Vec::new();
                            kw183.push(("origin".into(), {
                                let mut s = Vec::new();
                                s.push(e.get("x")?);
                                s.push(e.get("y")?);
                                s.push(e.get("z")?);
                                Val::tuple(s)
                            }));
                            kw183.push(("xDir".into(), {
                                let mut s = Vec::new();
                                s.push(unary("neg", Val::Int(1i64))?);
                                s.push(Val::Int(0i64));
                                s.push(Val::Int(0i64));
                                Val::tuple(s)
                            }));
                            kw183.push(("normal".into(), {
                                let mut s = Vec::new();
                                s.push(Val::Int(0i64));
                                s.push(Val::Int(0i64));
                                s.push(Val::Int(1i64));
                                Val::tuple(s)
                            }));
                            fun184.call(args182, kw183)?
                        }
                    });
                    fun181.call(args179, kw180)?
                }
            };
            e.set("pose", assigned178.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun187 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                            line!(),
                        );
                        {
                            let fun190 = e.get("_tee_native")?;
                            let mut args188 = Vec::new();
                            let mut kw189 = Vec::new();
                            fun190.call(args188, kw189)?
                        }
                    }
                    .attr("moved")?;
                    let mut args185 = Vec::new();
                    let mut kw186 = Vec::new();
                    args185.push(e.get("pose")?);
                    fun187.call(args185, kw186)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("_elbow_native",memoize({let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun193=e.get("tuple")?;let mut args191=Vec::new();let mut kw192=Vec::new();args191.push({let e=e.child();let out194=Val::list(vec![]);for item195 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun198=e.get("stem_elbow")?.attr("build")?;let mut args196=Vec::new();let mut kw197=Vec::new();fun198.call(args196,kw197)?}}.iter()? {let unpack199=unpack(item195,2)?;e.set("_name",unpack199[0].clone())?;e.set("piece",unpack199[1].clone())?;out194.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun202=e.get("piece")?.attr("val")?;let mut args200=Vec::new();let mut kw201=Vec::new();fun202.call(args200,kw201)?}}],vec![])?;}out194});fun193.call(args191,kw192)?}});
Ok(Val::None)})},Some(1usize)))?; // elbow_body
    e.set("elbow_body", {
        let params = vec![("row".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned203 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun206 = e.get("_elbow_native")?;
                    let mut args204 = Vec::new();
                    let mut kw205 = Vec::new();
                    fun206.call(args204, kw205)?
                }
            };
            let unpack207 = unpack(assigned203.clone(), 2)?;
            e.set("body", unpack207[0].clone())?;
            e.set("collet", unpack207[1].clone())?;
            let assigned208 = binary(
                "add",
                e.get("stem_elbow")?.attr("HUB_BACK_REACH")?,
                e.get("row")?.get(Val::Str("stem".into()))?,
            )?;
            e.set("keep", assigned208.clone())?;
            let assigned209 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun212 = e.get("body")?.attr("cut")?;
                    let mut args210 = Vec::new();
                    let mut kw211 = Vec::new();
                    args210.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                            line!(),
                        );
                        {
                            let fun215 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                            let mut args213 = Vec::new();
                            let mut kw214 = Vec::new();
                            args213.push(Val::Float(40.0f64));
                            args213.push(Val::Float(40.0f64));
                            args213.push(Val::Float(40.0f64));
                            args213.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                                    line!(),
                                );
                                {
                                    let fun218 = e.get("cq")?.attr("Vector")?;
                                    let mut args216 = Vec::new();
                                    let mut kw217 = Vec::new();
                                    args216.push(binary(
                                        "sub",
                                        unary("neg", e.get("keep")?)?,
                                        Val::Float(40.0f64),
                                    )?);
                                    args216.push(unary("neg", Val::Float(20.0f64))?);
                                    args216.push(unary("neg", Val::Float(20.0f64))?);
                                    fun218.call(args216, kw217)?
                                }
                            });
                            fun215.call(args213, kw214)?
                        }
                    });
                    fun212.call(args210, kw211)?
                }
            };
            e.set("body", assigned209.clone())?;
            let assigned219 = e.get("row")?.get(Val::Str("socket".into()))?;
            let unpack220 = unpack(assigned219.clone(), 3)?;
            e.set("ux", unpack220[0].clone())?;
            e.set("uy", unpack220[1].clone())?;
            e.set("_uz", unpack220[2].clone())?;
            let assigned221 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun224 = e.get("cq")?.attr("Location")?;
                    let mut args222 = Vec::new();
                    let mut kw223 = Vec::new();
                    args222.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                            line!(),
                        );
                        {
                            let fun227 = e.get("cq")?.attr("Plane")?;
                            let mut args225 = Vec::new();
                            let mut kw226 = Vec::new();
                            kw226.push((
                                "origin".into(),
                                e.get("row")?.get(Val::Str("crossing".into()))?,
                            ));
                            kw226.push(("xDir".into(), {
                                let mut s = Vec::new();
                                s.push(Val::Int(0i64));
                                s.push(Val::Int(0i64));
                                s.push(unary("neg", Val::Int(1i64))?);
                                Val::tuple(s)
                            }));
                            kw226.push(("normal".into(), {
                                let mut s = Vec::new();
                                s.push(e.get("uy")?);
                                s.push(unary("neg", e.get("ux")?)?);
                                s.push(Val::Int(0i64));
                                Val::tuple(s)
                            }));
                            fun227.call(args225, kw226)?
                        }
                    });
                    fun224.call(args222, kw223)?
                }
            };
            e.set("pose", assigned221.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun230 = e.get("cq")?.attr("Compound")?.attr("makeCompound")?;
                    let mut args228 = Vec::new();
                    let mut kw229 = Vec::new();
                    args228.push({
                        let mut s = Vec::new();
                        s.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                                line!(),
                            );
                            {
                                let fun233 = e.get("body")?.attr("moved")?;
                                let mut args231 = Vec::new();
                                let mut kw232 = Vec::new();
                                args231.push(e.get("pose")?);
                                fun233.call(args231, kw232)?
                            }
                        });
                        s.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                                line!(),
                            );
                            {
                                let fun236 = e.get("collet")?.attr("moved")?;
                                let mut args234 = Vec::new();
                                let mut kw235 = Vec::new();
                                args234.push(e.get("pose")?);
                                fun236.call(args234, kw235)?
                            }
                        });
                        Val::list(s)
                    });
                    fun230.call(args228, kw229)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // elbow_host
    e.set("elbow_host", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned237 = e.get("name")?.get(Val::Slice {
                start: Some(
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                            line!(),
                        );
                        {
                            let fun240 = e.get("len")?;
                            let mut args238 = Vec::new();
                            let mut kw239 = Vec::new();
                            args238.push(Val::Str("stem-elbow-".into()));
                            fun240.call(args238, kw239)?
                        }
                    }
                    .integer()?,
                ),
                stop: None,
                step: 1,
            })?;
            e.set("host", assigned237.clone())?;
            return Ok(binary(
                "add",
                if {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun243 = e.get("host")?.attr("startswith")?;
                        let mut args241 = Vec::new();
                        let mut kw242 = Vec::new();
                        args241.push(Val::Str("y-".into()));
                        fun243.call(args241, kw242)?
                    }
                }
                .truthy()?
                {
                    Val::Str("tee-".into())
                } else {
                    Val::Str("valve-".into())
                },
                e.get("host")?,
            )?);
            Ok(Val::None)
        })
    })?;
    // _surface
    e.set("_surface", {
        let params = vec![("face".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned244 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun247 = e.get("sys")?.attr("modules")?.attr("get")?;
                    let mut args245 = Vec::new();
                    let mut kw246 = Vec::new();
                    args245.push(Val::Str("meshcad".into()));
                    fun247.call(args245, kw246)?
                }
            };
            e.set("meshcad", assigned244.clone())?;
            if {
                let v251 = {
                    let v252 = e.get("meshcad")?;
                    let v253 = Val::None;
                    Val::Bool(compare("is_not", v252.clone(), v253.clone())?.truthy()?)
                };
                if v251.truthy()? {
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                            line!(),
                        );
                        {
                            let fun250 = e.get("meshcad")?.attr("is_mesh")?;
                            let mut args248 = Vec::new();
                            let mut kw249 = Vec::new();
                            args248.push(e.get("face")?);
                            fun250.call(args248, kw249)?
                        }
                    }
                } else {
                    v251
                }
            }
            .truthy()?
            {
                return Ok({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun256 = e.get("face")?.attr("_geomAdaptor")?;
                        let mut args254 = Vec::new();
                        let mut kw255 = Vec::new();
                        fun256.call(args254, kw255)?
                    }
                });
            }
            let mod257 = rt.import_module("OCP.BRepAdaptor")?;
            e.set(
                "BRepAdaptor_Surface",
                rt.member("OCP.BRepAdaptor", "BRepAdaptor_Surface")?,
            )?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun260 = e.get("BRepAdaptor_Surface")?;
                    let mut args258 = Vec::new();
                    let mut kw259 = Vec::new();
                    args258.push(e.get("face")?.attr("wrapped")?);
                    fun260.call(args258, kw259)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // _on
    e.set("_on", {
        let params = vec![("face".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned261 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun264 = e.get("sys")?.attr("modules")?.attr("get")?;
                    let mut args262 = Vec::new();
                    let mut kw263 = Vec::new();
                    args262.push(Val::Str("meshcad".into()));
                    fun264.call(args262, kw263)?
                }
            };
            e.set("meshcad", assigned261.clone())?;
            if {
                let v268 = {
                    let v269 = e.get("meshcad")?;
                    let v270 = Val::None;
                    Val::Bool(compare("is_not", v269.clone(), v270.clone())?.truthy()?)
                };
                if v268.truthy()? {
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                            line!(),
                        );
                        {
                            let fun267 = e.get("meshcad")?.attr("is_mesh")?;
                            let mut args265 = Vec::new();
                            let mut kw266 = Vec::new();
                            args265.push(e.get("face")?);
                            fun267.call(args265, kw266)?
                        }
                    }
                } else {
                    v268
                }
            }
            .truthy()?
            {
                return Ok({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun273 = {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                                line!(),
                            );
                            {
                                let fun276 = e.get("face")?.attr("Vertices")?;
                                let mut args274 = Vec::new();
                                let mut kw275 = Vec::new();
                                fun276.call(args274, kw275)?
                            }
                        }
                        .get(Val::Int(0i64))?
                        .attr("Center")?;
                        let mut args271 = Vec::new();
                        let mut kw272 = Vec::new();
                        fun273.call(args271, kw272)?
                    }
                });
            }
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun279 = e.get("face")?.attr("positionAt")?;
                    let mut args277 = Vec::new();
                    let mut kw278 = Vec::new();
                    args277.push(Val::Float(0.5f64));
                    args277.push(Val::Float(0.5f64));
                    fun279.call(args277, kw278)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // stem_mate_region
    e.set("stem_mate_region",{let params=vec![("elbow".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned280=binary("truediv",e.get("stem_elbow")?.attr("STEM_OD")?,Val::Float(2.0f64))?;e.set("r",assigned280.clone())?;
// outer
e.set("outer",{let params=vec![("face".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned281={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun284={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun287={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun290=e.get("_surface")?;let mut args288=Vec::new();let mut kw289=Vec::new();args288.push(e.get("face")?);fun290.call(args288,kw289)?}}.attr("Cylinder")?;let mut args285=Vec::new();let mut kw286=Vec::new();fun287.call(args285,kw286)?}}.attr("Axis")?;let mut args282=Vec::new();let mut kw283=Vec::new();fun284.call(args282,kw283)?}};e.set("axis",assigned281.clone())?;
let assigned291={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun294=e.get("cq")?.attr("Vector")?;let mut args292=Vec::new();let mut kw293=Vec::new();args292.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun297={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun300=e.get("axis")?.attr("Location")?;let mut args298=Vec::new();let mut kw299=Vec::new();fun300.call(args298,kw299)?}}.attr("X")?;let mut args295=Vec::new();let mut kw296=Vec::new();fun297.call(args295,kw296)?}});args292.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun303={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun306=e.get("axis")?.attr("Location")?;let mut args304=Vec::new();let mut kw305=Vec::new();fun306.call(args304,kw305)?}}.attr("Y")?;let mut args301=Vec::new();let mut kw302=Vec::new();fun303.call(args301,kw302)?}});args292.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun309={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun312=e.get("axis")?.attr("Location")?;let mut args310=Vec::new();let mut kw311=Vec::new();fun312.call(args310,kw311)?}}.attr("Z")?;let mut args307=Vec::new();let mut kw308=Vec::new();fun309.call(args307,kw308)?}});fun294.call(args292,kw293)?}};e.set("o",assigned291.clone())?;
let assigned313={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun316=e.get("cq")?.attr("Vector")?;let mut args314=Vec::new();let mut kw315=Vec::new();args314.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun319={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun322=e.get("axis")?.attr("Direction")?;let mut args320=Vec::new();let mut kw321=Vec::new();fun322.call(args320,kw321)?}}.attr("X")?;let mut args317=Vec::new();let mut kw318=Vec::new();fun319.call(args317,kw318)?}});args314.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun325={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun328=e.get("axis")?.attr("Direction")?;let mut args326=Vec::new();let mut kw327=Vec::new();fun328.call(args326,kw327)?}}.attr("Y")?;let mut args323=Vec::new();let mut kw324=Vec::new();fun325.call(args323,kw324)?}});args314.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun331={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun334=e.get("axis")?.attr("Direction")?;let mut args332=Vec::new();let mut kw333=Vec::new();fun334.call(args332,kw333)?}}.attr("Z")?;let mut args329=Vec::new();let mut kw330=Vec::new();fun331.call(args329,kw330)?}});fun316.call(args314,kw315)?}};e.set("d",assigned313.clone())?;
let assigned335={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun338=e.get("_on")?;let mut args336=Vec::new();let mut kw337=Vec::new();args336.push(e.get("face")?);fun338.call(args336,kw337)?}};e.set("p",assigned335.clone())?;
let assigned339=binary("sub",e.get("p")?,binary("add",e.get("o")?,binary("mul",e.get("d")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun342=binary("sub",e.get("p")?,e.get("o")?)?.attr("dot")?;let mut args340=Vec::new();let mut kw341=Vec::new();args340.push(e.get("d")?);fun342.call(args340,kw341)?}})?)?)?;e.set("off",assigned339.clone())?;
return Ok({let v349={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun345={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun348=e.get("face")?.attr("normalAt")?;let mut args346=Vec::new();let mut kw347=Vec::new();args346.push(e.get("p")?);fun348.call(args346,kw347)?}}.attr("dot")?;let mut args343=Vec::new();let mut kw344=Vec::new();args343.push(e.get("off")?);fun345.call(args343,kw344)?}};let v350=Val::Float(0.0f64);Val::Bool(compare("gt",v349.clone(),v350.clone())?.truthy()?)});
Ok(Val::None)})})?;
let assigned351={let e=e.child();let out352=Val::list(vec![]);for item353 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun356=e.get("elbow")?.attr("Faces")?;let mut args354=Vec::new();let mut kw355=Vec::new();fun356.call(args354,kw355)?}}.iter()? {e.set("face",item353)?;if {let v375={let v379={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun378=e.get("face")?.attr("geomType")?;let mut args376=Vec::new();let mut kw377=Vec::new();fun378.call(args376,kw377)?}};let v380=Val::Str("CYLINDER".into());Val::Bool(compare("eq",v379.clone(),v380.clone())?.truthy()?)};if v375.truthy()? {{let v360={let v373={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun363=e.get("abs")?;let mut args361=Vec::new();let mut kw362=Vec::new();args361.push(binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun366={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun369={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun372=e.get("_surface")?;let mut args370=Vec::new();let mut kw371=Vec::new();args370.push(e.get("face")?);fun372.call(args370,kw371)?}}.attr("Cylinder")?;let mut args367=Vec::new();let mut kw368=Vec::new();fun369.call(args367,kw368)?}}.attr("Radius")?;let mut args364=Vec::new();let mut kw365=Vec::new();fun366.call(args364,kw365)?}},e.get("r")?)?);fun363.call(args361,kw362)?}};let v374=Val::Float(0.001f64);Val::Bool(compare("lt",v373.clone(),v374.clone())?.truthy()?)};if v360.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun359=e.get("outer")?;let mut args357=Vec::new();let mut kw358=Vec::new();args357.push(e.get("face")?);fun359.call(args357,kw358)?}}} else {v360}}} else {v375}}.truthy()? {out352.attr("append")?.call(vec![e.get("face")?],vec![])?;}}out352};e.set("faces",assigned351.clone())?;
let assigned381={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun384={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun387={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun390=e.get("_surface")?;let mut args388=Vec::new();let mut kw389=Vec::new();args388.push(e.get("faces")?.get(Val::Int(0i64))?);fun390.call(args388,kw389)?}}.attr("Cylinder")?;let mut args385=Vec::new();let mut kw386=Vec::new();fun387.call(args385,kw386)?}}.attr("Axis")?;let mut args382=Vec::new();let mut kw383=Vec::new();fun384.call(args382,kw383)?}};e.set("axis",assigned381.clone())?;
let assigned391={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun394=e.get("cq")?.attr("Vector")?;let mut args392=Vec::new();let mut kw393=Vec::new();args392.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun397={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun400=e.get("axis")?.attr("Location")?;let mut args398=Vec::new();let mut kw399=Vec::new();fun400.call(args398,kw399)?}}.attr("X")?;let mut args395=Vec::new();let mut kw396=Vec::new();fun397.call(args395,kw396)?}});args392.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun403={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun406=e.get("axis")?.attr("Location")?;let mut args404=Vec::new();let mut kw405=Vec::new();fun406.call(args404,kw405)?}}.attr("Y")?;let mut args401=Vec::new();let mut kw402=Vec::new();fun403.call(args401,kw402)?}});args392.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun409={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun412=e.get("axis")?.attr("Location")?;let mut args410=Vec::new();let mut kw411=Vec::new();fun412.call(args410,kw411)?}}.attr("Z")?;let mut args407=Vec::new();let mut kw408=Vec::new();fun409.call(args407,kw408)?}});fun394.call(args392,kw393)?}};e.set("o",assigned391.clone())?;
let assigned413={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun416=e.get("cq")?.attr("Vector")?;let mut args414=Vec::new();let mut kw415=Vec::new();args414.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun419={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun422=e.get("axis")?.attr("Direction")?;let mut args420=Vec::new();let mut kw421=Vec::new();fun422.call(args420,kw421)?}}.attr("X")?;let mut args417=Vec::new();let mut kw418=Vec::new();fun419.call(args417,kw418)?}});args414.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun425={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun428=e.get("axis")?.attr("Direction")?;let mut args426=Vec::new();let mut kw427=Vec::new();fun428.call(args426,kw427)?}}.attr("Y")?;let mut args423=Vec::new();let mut kw424=Vec::new();fun425.call(args423,kw424)?}});args414.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun431={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun434=e.get("axis")?.attr("Direction")?;let mut args432=Vec::new();let mut kw433=Vec::new();fun434.call(args432,kw433)?}}.attr("Z")?;let mut args429=Vec::new();let mut kw430=Vec::new();fun431.call(args429,kw430)?}});fun416.call(args414,kw415)?}};e.set("d",assigned413.clone())?;
let assigned435={let e=e.child();let out436=Val::list(vec![]);for item437 in e.get("faces")?.iter()? {e.set("face",item437)?;for item438 in {let e=e.child();let out439=Val::list(vec![]);for item440 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun443=e.get("face")?.attr("Vertices")?;let mut args441=Vec::new();let mut kw442=Vec::new();fun443.call(args441,kw442)?}}.iter()? {e.set("v",item440)?;out439.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun446=e.get("v")?.attr("Center")?;let mut args444=Vec::new();let mut kw445=Vec::new();fun446.call(args444,kw445)?}}],vec![])?;}out439}.iter()? {e.set("p",item438)?;out436.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun449=binary("sub",e.get("p")?,e.get("o")?)?.attr("dot")?;let mut args447=Vec::new();let mut kw448=Vec::new();args447.push(e.get("d")?);fun449.call(args447,kw448)?}}],vec![])?;}}out436};e.set("t",assigned435.clone())?;
let assigned450=e.get("stem_elbow")?.attr("PARAMETERS")?.get(Val::Str("profiles".into()))?.get(Val::Str("stem_x".into()))?;e.set("profile",assigned450.clone())?;
let assigned451={let e=e.child();let out452=Val::list(vec![]);for item453 in e.get("profile")?.iter()? {let unpack454=unpack(item453,2)?;e.set("x",unpack454[0].clone())?;e.set("radius",unpack454[1].clone())?;if {let v458={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun457=e.get("abs")?;let mut args455=Vec::new();let mut kw456=Vec::new();args455.push(binary("sub",e.get("radius")?,e.get("r")?)?);fun457.call(args455,kw456)?}};let v459=Val::Float(1e-06f64);Val::Bool(compare("lt",v458.clone(),v459.clone())?.truthy()?)}.truthy()? {out452.attr("append")?.call(vec![e.get("x")?],vec![])?;}}out452};e.set("straight",assigned451.clone())?;
let assigned460=binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun463=e.get("min")?;let mut args461=Vec::new();let mut kw462=Vec::new();args461.push(e.get("straight")?);fun463.call(args461,kw462)?}},e.get("profile")?.get(Val::Int(0i64))?.get(Val::Int(0i64))?)?;e.set("tip_allowance",assigned460.clone())?;
let assigned464={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun467=e.get("max")?;let mut args465=Vec::new();let mut kw466=Vec::new();args465.push({let e=e.child();let out468=Val::list(vec![]);for item469 in e.get("profile")?.iter()? {let unpack470=unpack(item469,2)?;e.set("x",unpack470[0].clone())?;e.set("radius",unpack470[1].clone())?;if {let v473={let v474=e.get("x")?;let v475=Val::Int(0i64);Val::Bool(compare("lt",v474.clone(),v475.clone())?.truthy()?)};if v473.truthy()? {{let v471=e.get("radius")?;let v472=e.get("r")?;Val::Bool(compare("gt",v471.clone(),v472.clone())?.truthy()?)}} else {v473}}.truthy()? {out468.attr("append")?.call(vec![e.get("x")?],vec![])?;}}out468});fun467.call(args465,kw466)?}};e.set("root_end",assigned464.clone())?;
let assigned476=binary("sub",e.get("root_end")?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun479=e.get("max")?;let mut args477=Vec::new();let mut kw478=Vec::new();args477.push(e.get("straight")?);fun479.call(args477,kw478)?}})?;e.set("root_allowance",assigned476.clone())?;
let assigned480={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun483=e.get("max")?;let mut args481=Vec::new();let mut kw482=Vec::new();args481.push({let e=e.child();let out484=Val::list(vec![]);for item485 in e.get("profile")?.iter()? {let unpack486=unpack(item485,2)?;e.set("x",unpack486[0].clone())?;e.set("radius",unpack486[1].clone())?;if {let v487=e.get("x")?;let v488=e.get("root_end")?;Val::Bool(compare("le",v487.clone(),v488.clone())?.truthy()?)}.truthy()? {out484.attr("append")?.call(vec![e.get("radius")?],vec![])?;}}out484});fun483.call(args481,kw482)?}};e.set("root_radius",assigned480.clone())?;
let assigned489={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun492=e.get("min")?;let mut args490=Vec::new();let mut kw491=Vec::new();args490.push(e.get("t")?);fun492.call(args490,kw491)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun495=e.get("max")?;let mut args493=Vec::new();let mut kw494=Vec::new();args493.push(e.get("t")?);fun495.call(args493,kw494)?}});Val::tuple(s)};let unpack496=unpack(assigned489.clone(),2)?;e.set("lo",unpack496[0].clone())?;e.set("hi",unpack496[1].clone())?;
let assigned497={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun500=e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;let mut args498=Vec::new();let mut kw499=Vec::new();args498.push(binary("add",e.get("r")?,Val::Float(0.01f64))?);args498.push(binary("add",binary("add",binary("sub",e.get("hi")?,e.get("lo")?)?,binary("mul",Val::Int(2i64),e.get("tip_allowance")?)?)?,Val::Float(0.02f64))?);args498.push(binary("add",e.get("o")?,binary("mul",e.get("d")?,binary("sub",binary("sub",e.get("lo")?,e.get("tip_allowance")?)?,Val::Float(0.01f64))?)?)?);args498.push(e.get("d")?);fun500.call(args498,kw499)?}};e.set("stem",assigned497.clone())?;
let assigned501={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun504=binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun507=e.get("elbow")?.attr("Center")?;let mut args505=Vec::new();let mut kw506=Vec::new();fun507.call(args505,kw506)?}},e.get("o")?)?.attr("dot")?;let mut args502=Vec::new();let mut kw503=Vec::new();args502.push(e.get("d")?);fun504.call(args502,kw503)?}};e.set("centre",assigned501.clone())?;
let assigned508=if {let v515={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun511=e.get("abs")?;let mut args509=Vec::new();let mut kw510=Vec::new();args509.push(binary("sub",e.get("centre")?,e.get("hi")?)?);fun511.call(args509,kw510)?}};let v516={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun514=e.get("abs")?;let mut args512=Vec::new();let mut kw513=Vec::new();args512.push(binary("sub",e.get("centre")?,e.get("lo")?)?);fun514.call(args512,kw513)?}};Val::Bool(compare("lt",v515.clone(),v516.clone())?.truthy()?)}.truthy()? {Val::Float(1.0f64)} else {unary("neg",Val::Float(1.0f64))?};e.set("outward",assigned508.clone())?;
let assigned517=if {let v518=e.get("outward")?;let v519=Val::Int(0i64);Val::Bool(compare("gt",v518.clone(),v519.clone())?.truthy()?)}.truthy()? {e.get("hi")?} else {e.get("lo")?};e.set("end",assigned517.clone())?;
let assigned520={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun523=e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;let mut args521=Vec::new();let mut kw522=Vec::new();args521.push(binary("add",e.get("root_radius")?,Val::Float(0.01f64))?);args521.push(binary("add",e.get("root_allowance")?,Val::Float(0.02f64))?);args521.push(binary("add",e.get("o")?,binary("mul",e.get("d")?,binary("sub",e.get("end")?,binary("mul",e.get("outward")?,Val::Float(0.01f64))?)?)?)?);args521.push(binary("mul",e.get("d")?,e.get("outward")?)?);fun523.call(args521,kw522)?}};e.set("root",assigned520.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/dock_structure.rs",line!());{let fun526=e.get("stem")?.attr("fuse")?;let mut args524=Vec::new();let mut kw525=Vec::new();args524.push(e.get("root")?);fun526.call(args524,kw525)?}});
Ok(Val::None)})})?;
    // stem_overlap
    e.set("stem_overlap", {
        let params = vec![("elbow".into(), None, false), ("host".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned527 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun530 = e.get("stem_mate_region")?;
                    let mut args528 = Vec::new();
                    let mut kw529 = Vec::new();
                    args528.push(e.get("elbow")?);
                    fun530.call(args528, kw529)?
                }
            };
            e.set("stem", assigned527.clone())?;
            let assigned531 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun534 = e.get("elbow")?.attr("intersect")?;
                    let mut args532 = Vec::new();
                    let mut kw533 = Vec::new();
                    args532.push(e.get("host")?);
                    fun534.call(args532, kw533)?
                }
            };
            e.set("common", assigned531.clone())?;
            let assigned535 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun538 = e.get("common")?.attr("Volume")?;
                    let mut args536 = Vec::new();
                    let mut kw537 = Vec::new();
                    fun538.call(args536, kw537)?
                }
            };
            e.set("inside", assigned535.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("inside")?);
                s.push(
                    if {
                        let v539 = e.get("inside")?;
                        let v540 = Val::Int(0i64);
                        Val::Bool(compare("gt", v539.clone(), v540.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                                line!(),
                            );
                            {
                                let fun543 = {
                                    let _site = rt.source_at(
                                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                                        line!(),
                                    );
                                    {
                                        let fun546 = e.get("common")?.attr("cut")?;
                                        let mut args544 = Vec::new();
                                        let mut kw545 = Vec::new();
                                        args544.push(e.get("stem")?);
                                        fun546.call(args544, kw545)?
                                    }
                                }
                                .attr("Volume")?;
                                let mut args541 = Vec::new();
                                let mut kw542 = Vec::new();
                                fun543.call(args541, kw542)?
                            }
                        }
                    } else {
                        Val::Float(0.0f64)
                    },
                );
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // parts
    e.set("parts", {
        let params = vec![("plate".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned547 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("out", assigned547.clone())?;
            for item548 in {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun551 = e.get("stations")?;
                    let mut args549 = Vec::new();
                    let mut kw550 = Vec::new();
                    args549.push(e.get("plate")?);
                    fun551.call(args549, kw550)?
                }
            }
            .iter()?
            {
                let unpack552 = unpack(item548, 4)?;
                e.set("_station", unpack552[0].clone())?;
                e.set("name", unpack552[1].clone())?;
                e.set("x", unpack552[2].clone())?;
                e.set("z", unpack552[3].clone())?;
                let assigned553 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun556 = e.get("tee_body")?;
                        let mut args554 = Vec::new();
                        let mut kw555 = Vec::new();
                        args554.push(e.get("plate")?);
                        args554.push(e.get("x")?);
                        args554.push(e.get("z")?);
                        fun556.call(args554, kw555)?
                    }
                };
                e.get("out")?.set(
                    binary("add", Val::Str("tee-".into()), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                            line!(),
                        );
                        {
                            let fun559 = e.get("name")?.attr("lower")?;
                            let mut args557 = Vec::new();
                            let mut kw558 = Vec::new();
                            fun559.call(args557, kw558)?
                        }
                    })?,
                    assigned553.clone(),
                )?;
                let assigned560 = e.get("plate")?.get(Val::Str("return_ports".into()))?.get({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun563 = e.get("str")?;
                        let mut args561 = Vec::new();
                        let mut kw562 = Vec::new();
                        args561.push(e.get("x")?);
                        fun563.call(args561, kw562)?
                    }
                })?;
                e.set("target", assigned560.clone())?;
                let assigned564 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun567 = e.get("plumbing")?.attr("tee_ports")?;
                        let mut args565 = Vec::new();
                        let mut kw566 = Vec::new();
                        args565.push(e.get("plate")?.get(Val::Str("fore_y".into()))?);
                        args565.push(e.get("x")?);
                        args565.push(e.get("z")?);
                        fun567.call(args565, kw566)?
                    }
                }
                .get(Val::Str("lower".into()))?
                .get(Val::Str("point".into()))?;
                e.set("lower", assigned564.clone())?;
                let assigned568 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun571 = e.get("plumbing")?.attr("elbow_return")?;
                        let mut args569 = Vec::new();
                        let mut kw570 = Vec::new();
                        args569.push(e.get("lower")?);
                        args569.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                                line!(),
                            );
                            {
                                let fun574 = e.get("tuple")?;
                                let mut args572 = Vec::new();
                                let mut kw573 = Vec::new();
                                args572.push(e.get("target")?.get(Val::Str("point".into()))?);
                                fun574.call(args572, kw573)?
                            }
                        });
                        fun571.call(args569, kw570)?
                    }
                }
                .get(Val::Str("elbows".into()))?;
                let unpack575 = unpack(assigned568.clone(), 2)?;
                e.set("at_tee", unpack575[0].clone())?;
                e.set("at_valve", unpack575[1].clone())?;
                let assigned576 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun579 = e.get("elbow_body")?;
                        let mut args577 = Vec::new();
                        let mut kw578 = Vec::new();
                        args577.push(e.get("at_tee")?);
                        fun579.call(args577, kw578)?
                    }
                };
                e.get("out")?.set(
                    binary("add", Val::Str("stem-elbow-".into()), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                            line!(),
                        );
                        {
                            let fun582 = e.get("name")?.attr("lower")?;
                            let mut args580 = Vec::new();
                            let mut kw581 = Vec::new();
                            fun582.call(args580, kw581)?
                        }
                    })?,
                    assigned576.clone(),
                )?;
                let assigned583 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun586 = e.get("elbow_body")?;
                        let mut args584 = Vec::new();
                        let mut kw585 = Vec::new();
                        args584.push(e.get("at_valve")?);
                        fun586.call(args584, kw585)?
                    }
                };
                e.get("out")?.set(
                    binary("add", Val::Str("stem-elbow-".into()), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                            line!(),
                        );
                        {
                            let fun589 = e
                                .get("target")?
                                .get(Val::Str("valve".into()))?
                                .attr("lower")?;
                            let mut args587 = Vec::new();
                            let mut kw588 = Vec::new();
                            fun589.call(args587, kw588)?
                        }
                    })?,
                    assigned583.clone(),
                )?;
            }
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    // part_color
    e.set("part_color", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod590 = rt.import_module("_materials")?;
            e.set("M_JG_BLACK_PP", rt.member("_materials", "M_JG_BLACK_PP")?)?;
            e.set(
                "M_NEOFIT_WHITE_ACETAL",
                rt.member("_materials", "M_NEOFIT_WHITE_ACETAL")?,
            )?;
            return Ok(
                if {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun593 = e.get("name")?.attr("startswith")?;
                        let mut args591 = Vec::new();
                        let mut kw592 = Vec::new();
                        args591.push(Val::Str("stem-elbow-".into()));
                        fun593.call(args591, kw592)?
                    }
                }
                .truthy()?
                {
                    e.get("M_NEOFIT_WHITE_ACETAL")?
                } else {
                    e.get("M_JG_BLACK_PP")?
                },
            );
            Ok(Val::None)
        })
    })?;
    // tube_setting_jig
    e.set("tube_setting_jig", {
        let params = vec![
            ("plate".into(), None, false),
            ("cradle_back_y".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned594 = e
                .get("plate")?
                .get(Val::Str("holes".into()))?
                .get(Val::Int(0i64))?
                .get(Val::Int(1i64))?;
            e.set("row", assigned594.clone())?;
            let assigned595 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun598 = e.get("plumbing")?.attr("tip_y")?;
                    let mut args596 = Vec::new();
                    let mut kw597 = Vec::new();
                    args596.push(e.get("plate")?.get(Val::Str("fore_y".into()))?);
                    fun598.call(args596, kw597)?
                }
            };
            e.set("tip", assigned595.clone())?;
            let assigned599 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun602 = e.get("box")?;
                    let mut args600 = Vec::new();
                    let mut kw601 = Vec::new();
                    args600.push(binary(
                        "sub",
                        e.get("plate")?
                            .get(Val::Str("holes".into()))?
                            .get(Val::Int(0i64))?
                            .get(Val::Int(0i64))?,
                        Val::Int(8i64),
                    )?);
                    args600.push(binary(
                        "add",
                        e.get("plate")?
                            .get(Val::Str("holes".into()))?
                            .get(unary("neg", Val::Int(1i64))?)?
                            .get(Val::Int(0i64))?,
                        Val::Int(8i64),
                    )?);
                    args600.push(e.get("cradle_back_y")?);
                    args600.push(binary("add", e.get("tip")?, Val::Int(3i64))?);
                    args600.push(binary("sub", e.get("row")?, Val::Int(8i64))?);
                    args600.push(binary("add", e.get("row")?, Val::Int(8i64))?);
                    fun602.call(args600, kw601)?
                }
            };
            e.set("body", assigned599.clone())?;
            for item603 in e.get("plate")?.get(Val::Str("holes".into()))?.iter()? {
                let unpack604 = unpack(item603, 2)?;
                e.set("x", unpack604[0].clone())?;
                e.set("z", unpack604[1].clone())?;
                let assigned605 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun608 = e.get("ycyl")?;
                        let mut args606 = Vec::new();
                        let mut kw607 = Vec::new();
                        args606.push(Val::Float(3.5f64));
                        args606.push(e.get("x")?);
                        args606.push(e.get("z")?);
                        args606.push(binary("sub", e.get("cradle_back_y")?, Val::Float(0.1f64))?);
                        args606.push(e.get("tip")?);
                        fun608.call(args606, kw607)?
                    }
                };
                e.set("bore", assigned605.clone())?;
                let assigned609 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun612 = e.get("box")?;
                        let mut args610 = Vec::new();
                        let mut kw611 = Vec::new();
                        args610.push(binary("sub", e.get("x")?, Val::Float(3.5f64))?);
                        args610.push(binary("add", e.get("x")?, Val::Float(3.5f64))?);
                        args610.push(binary("sub", e.get("cradle_back_y")?, Val::Float(0.1f64))?);
                        args610.push(e.get("tip")?);
                        args610.push(e.get("z")?);
                        args610.push(binary("add", e.get("row")?, Val::Float(8.1f64))?);
                        fun612.call(args610, kw611)?
                    }
                };
                e.set("opening", assigned609.clone())?;
                let assigned613 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                        line!(),
                    );
                    {
                        let fun616 = e.get("body")?.attr("cut")?;
                        let mut args614 = Vec::new();
                        let mut kw615 = Vec::new();
                        args614.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                                line!(),
                            );
                            {
                                let fun619 = e.get("bore")?.attr("fuse")?;
                                let mut args617 = Vec::new();
                                let mut kw618 = Vec::new();
                                args617.push(e.get("opening")?);
                                fun619.call(args617, kw618)?
                            }
                        });
                        fun616.call(args614, kw615)?
                    }
                };
                e.set("body", assigned613.clone())?;
            }
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/dock_structure.rs",
                    line!(),
                );
                {
                    let fun622 = e.get("body")?.attr("clean")?;
                    let mut args620 = Vec::new();
                    let mut kw621 = Vec::new();
                    fun622.call(args620, kw621)?
                }
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
