//! Guide recipe: `tools/install-guide/startup.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("json", rt.import_module("json")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
    e.set("scenes", rt.import_module("scenes")?)?;
    let assigned1 = binary(
        "truediv",
        e.get("scenes")?.attr("HARDWARE")?,
        Val::Str("install-guide/out/startup".into()),
    )?;
    e.set("OUT", assigned1.clone())?;
    let assigned2 = binary(
        "truediv",
        e.get("scenes")?.attr("HARDWARE")?,
        Val::Str("install-guide/art".into()),
    )?;
    e.set("ART", assigned2.clone())?;
    let assigned3 = {
        let mut s = Vec::new();
        s.push(Val::Float(0.08f64));
        s.push(Val::Int(1i64));
        s.push(Val::Float(0.12f64));
        Val::tuple(s)
    };
    e.set("CAM", assigned3.clone())?;
    let assigned4 = {
        let mut s = Vec::new();
        s.push(unary("neg", Val::Int(35i64))?);
        s.push(Val::Int(0i64));
        s.push(unary("neg", Val::Float(4.5f64))?);
        Val::tuple(s)
    };
    e.set("TARGET", assigned4.clone())?;
    let assigned5 = Val::Float(103.5f64);
    e.set("SPAN", assigned5.clone())?;
    let assigned6 = {
        let mut s = Vec::new();
        s.push(Val::Int(1800i64));
        s.push(Val::Int(1200i64));
        Val::tuple(s)
    };
    e.set("SIZE", assigned6.clone())?;
    let assigned7 = e.get("scenes")?.attr("reg")?;
    e.set("reg", assigned7.clone())?;
    let assigned8 = e.get("reg")?.attr("FACTORY_SET_PSI")?;
    e.set("OUTLET_PSI", assigned8.clone())?;
    let assigned9 = Val::Int(800i64);
    e.set("CYLINDER_PSI", assigned9.clone())?;
    // dial_print
    e.set("dial_print", {
        let params = vec![
            ("child".into(), None, false),
            ("centre".into(), None, false),
            ("pressure".into(), None, false),
            ("full".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned10 = binary(
                "add",
                e.get("reg")?.attr("GAUGE_FACE_Y")?,
                e.get("reg")?.attr("PRINT_T")?,
            )?;
            e.set("face_y", assigned10.clone())?;
            let assigned11 = {
                let e = e.child();
                let out12 = Val::list(vec![]);
                for item13 in {
                    let fun16 = e.get("child")?.attr("obj")?.attr("Solids")?;
                    let mut args14 = Vec::new();
                    let mut kw15 = Vec::new();
                    fun16.call(args14, kw15)?
                }
                .iter()?
                {
                    e.set("solid", item13)?;
                    if {
                        let v20 = {
                            let fun19 = e.get("solid")?.attr("BoundingBox")?;
                            let mut args17 = Vec::new();
                            let mut kw18 = Vec::new();
                            fun19.call(args17, kw18)?
                        }
                        .attr("ymin")?;
                        let v21 = binary("sub", e.get("face_y")?, Val::Float(1e-05f64))?;
                        Val::Bool(compare("lt", v20.clone(), v21.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        out12.attr("append")?.call(vec![e.get("solid")?], vec![])?;
                    }
                }
                out12
            };
            e.set("marks", assigned11.clone())?;
            let assigned22 = {
                let fun25 = {
                    let fun28 = {
                        let fun31 = e.get("cq")?.attr("Workplane")?;
                        let mut args29 = Vec::new();
                        let mut kw30 = Vec::new();
                        args29.push(e.get("reg")?.attr("_dial_plane")?);
                        fun31.call(args29, kw30)?
                    }
                    .attr("workplane")?;
                    let mut args26 = Vec::new();
                    let mut kw27 = Vec::new();
                    kw27.push(("offset".into(), e.get("face_y")?));
                    fun28.call(args26, kw27)?
                }
                .attr("center")?;
                let mut args23 = Vec::new();
                let mut kw24 = Vec::new();
                args23.push(unary("neg", e.get("centre")?.get(Val::Int(0i64))?)?);
                args23.push(e.get("centre")?.get(Val::Int(2i64))?);
                fun25.call(args23, kw24)?
            };
            e.set("plane", assigned22.clone())?;
            {
                let fun34 = e.get("marks")?.attr("append")?;
                let mut args32 = Vec::new();
                let mut kw33 = Vec::new();
                args32.push({
                    let fun37 = e.get("reg")?.attr("_needle")?;
                    let mut args35 = Vec::new();
                    let mut kw36 = Vec::new();
                    args35.push({
                        let fun40 = e.get("reg")?.attr("_scale_deg")?;
                        let mut args38 = Vec::new();
                        let mut kw39 = Vec::new();
                        args38.push(e.get("pressure")?);
                        args38.push(e.get("full")?);
                        fun40.call(args38, kw39)?
                    });
                    args35.push(e.get("plane")?);
                    fun37.call(args35, kw36)?
                });
                fun34.call(args32, kw33)?
            };
            return Ok({
                let fun43 = e.get("cq")?.attr("Compound")?.attr("makeCompound")?;
                let mut args41 = Vec::new();
                let mut kw42 = Vec::new();
                args41.push(e.get("marks")?);
                fun43.call(args41, kw42)?
            });
            Ok(Val::None)
        })
    })?;
    // assembly
    e.set("assembly", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned44 = {
                let fun47 = e.get("cq")?.attr("Assembly")?;
                let mut args45 = Vec::new();
                let mut kw46 = Vec::new();
                kw46.push(("name".into(), Val::Str("startup-gas".into())));
                fun47.call(args45, kw46)?
            };
            e.set("result", assigned44.clone())?;
            for item48 in {
                let fun78 = e.get("scenes")?.attr("cylinder")?;
                let mut args76 = Vec::new();
                let mut kw77 = Vec::new();
                fun78.call(args76, kw77)?
            }
            .attr("children")?
            .iter()?
            {
                e.set("child", item48)?;
                if {
                    let v49 = e.get("child")?.attr("name")?;
                    let v50 = Val::Str("outlet-black-print".into());
                    Val::Bool(compare("eq", v49.clone(), v50.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned51 = {
                        let fun54 = e.get("dial_print")?;
                        let mut args52 = Vec::new();
                        let mut kw53 = Vec::new();
                        args52.push(e.get("child")?);
                        args52.push(
                            {
                                let fun57 = e.get("reg")?.attr("outlet_dial")?;
                                let mut args55 = Vec::new();
                                let mut kw56 = Vec::new();
                                fun57.call(args55, kw56)?
                            }
                            .get(Val::Int(0i64))?,
                        );
                        args52.push(e.get("OUTLET_PSI")?);
                        args52.push(e.get("reg")?.attr("OUTLET_FULL_PSI")?);
                        fun54.call(args52, kw53)?
                    };
                    e.set("obj", assigned51.clone())?;
                    {
                        let fun60 = e.get("result")?.attr("add")?;
                        let mut args58 = Vec::new();
                        let mut kw59 = Vec::new();
                        args58.push(e.get("obj")?);
                        kw59.push(("name".into(), e.get("child")?.attr("name")?));
                        kw59.push(("color".into(), e.get("child")?.attr("color")?));
                        fun60.call(args58, kw59)?
                    };
                } else {
                    if {
                        let v61 = e.get("child")?.attr("name")?;
                        let v62 = Val::Str("tank-black-print".into());
                        Val::Bool(compare("eq", v61.clone(), v62.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        let assigned63 = {
                            let fun66 = e.get("dial_print")?;
                            let mut args64 = Vec::new();
                            let mut kw65 = Vec::new();
                            args64.push(e.get("child")?);
                            args64.push(
                                {
                                    let fun69 = e.get("reg")?.attr("tank_dial")?;
                                    let mut args67 = Vec::new();
                                    let mut kw68 = Vec::new();
                                    fun69.call(args67, kw68)?
                                }
                                .get(Val::Int(0i64))?,
                            );
                            args64.push(e.get("CYLINDER_PSI")?);
                            args64.push(e.get("reg")?.attr("TANK_FULL_PSI")?);
                            fun66.call(args64, kw65)?
                        };
                        e.set("obj", assigned63.clone())?;
                        {
                            let fun72 = e.get("result")?.attr("add")?;
                            let mut args70 = Vec::new();
                            let mut kw71 = Vec::new();
                            args70.push(e.get("obj")?);
                            kw71.push(("name".into(), e.get("child")?.attr("name")?));
                            kw71.push(("color".into(), e.get("child")?.attr("color")?));
                            fun72.call(args70, kw71)?
                        };
                    } else {
                        {
                            let fun75 = e.get("result")?.attr("add")?;
                            let mut args73 = Vec::new();
                            let mut kw74 = Vec::new();
                            args73.push(e.get("child")?);
                            fun75.call(args73, kw74)?
                        };
                    }
                }
            }
            return Ok(e.get("result")?);
            Ok(Val::None)
        })
    })?;
    // points
    e.set("points", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned79 = {
                let fun82 = e.get("math")?.attr("radians")?;
                let mut args80 = Vec::new();
                let mut kw81 = Vec::new();
                args80.push({
                    let fun85 = e.get("reg")?.attr("_scale_deg")?;
                    let mut args83 = Vec::new();
                    let mut kw84 = Vec::new();
                    args83.push(e.get("OUTLET_PSI")?);
                    args83.push(e.get("reg")?.attr("OUTLET_FULL_PSI")?);
                    fun85.call(args83, kw84)?
                });
                fun82.call(args80, kw81)?
            };
            e.set("angle", assigned79.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(
                    Val::Str("upper-gauge".into()),
                    {
                        let fun88 = e.get("reg")?.attr("outlet_dial")?;
                        let mut args86 = Vec::new();
                        let mut kw87 = Vec::new();
                        fun88.call(args86, kw87)?
                    }
                    .get(Val::Int(0i64))?,
                )?;
                d.set(Val::Str("upper-needle-tip".into()), {
                    let mut s = Vec::new();
                    s.push(binary(
                        "mul",
                        unary("neg", e.get("reg")?.attr("NEEDLE_R")?)?,
                        {
                            let fun91 = e.get("math")?.attr("cos")?;
                            let mut args89 = Vec::new();
                            let mut kw90 = Vec::new();
                            args89.push(e.get("angle")?);
                            fun91.call(args89, kw90)?
                        },
                    )?);
                    s.push(binary(
                        "add",
                        binary(
                            "add",
                            e.get("reg")?.attr("GAUGE_FACE_Y")?,
                            e.get("reg")?.attr("PRINT_T")?,
                        )?,
                        Val::Float(0.8f64),
                    )?);
                    s.push(binary(
                        "add",
                        e.get("reg")?.attr("OUTLET_REACH")?,
                        binary("mul", e.get("reg")?.attr("NEEDLE_R")?, {
                            let fun94 = e.get("math")?.attr("sin")?;
                            let mut args92 = Vec::new();
                            let mut kw93 = Vec::new();
                            args92.push(e.get("angle")?);
                            fun94.call(args92, kw93)?
                        })?,
                    )?);
                    Val::tuple(s)
                })?;
                d.set(
                    Val::Str("cylinder-gauge".into()),
                    {
                        let fun97 = e.get("reg")?.attr("tank_dial")?;
                        let mut args95 = Vec::new();
                        let mut kw96 = Vec::new();
                        fun97.call(args95, kw96)?
                    }
                    .get(Val::Int(0i64))?,
                )?;
                d.set(
                    Val::Str("factory-screw".into()),
                    {
                        let fun100 = e.get("reg")?.attr("adjustment")?;
                        let mut args98 = Vec::new();
                        let mut kw99 = Vec::new();
                        fun100.call(args98, kw99)?
                    }
                    .get(Val::Int(0i64))?,
                )?;
                d.set(Val::Str("cylinder-handwheel".into()), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Int(115i64))?);
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(33i64));
                    Val::tuple(s)
                })?;
                d
            });
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
                let fun103 = e.get("OUT")?.attr("mkdir")?;
                let mut args101 = Vec::new();
                let mut kw102 = Vec::new();
                kw102.push(("parents".into(), Val::Bool(true)));
                kw102.push(("exist_ok".into(), Val::Bool(true)));
                fun103.call(args101, kw102)?
            };
            {
                let fun106 = e.get("ART")?.attr("mkdir")?;
                let mut args104 = Vec::new();
                let mut kw105 = Vec::new();
                kw105.push(("exist_ok".into(), Val::Bool(true)));
                fun106.call(args104, kw105)?
            };
            let assigned107 = {
                let mut s = Vec::new();
                s.push(e.get("OUT")?);
                s.push(e.get("ART")?);
                s.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                Val::tuple(s)
            };
            let unpack108 = unpack(assigned107.clone(), 3)?;
            e.get("scenes")?.setattr("OUT", unpack108[0].clone())?;
            e.get("scenes")?.setattr("ART", unpack108[1].clone())?;
            e.get("scenes")?.setattr("jobs", unpack108[2].clone())?;
            {
                let fun111 = e.get("scenes")?.attr("stage")?;
                let mut args109 = Vec::new();
                let mut kw110 = Vec::new();
                args109.push(Val::Str("startup-gas".into()));
                args109.push({
                    let fun114 = e.get("assembly")?;
                    let mut args112 = Vec::new();
                    let mut kw113 = Vec::new();
                    fun114.call(args112, kw113)?
                });
                args109.push(e.get("CAM")?);
                args109.push(e.get("TARGET")?);
                args109.push(e.get("SPAN")?);
                kw110.push(("size".into(), {
                    let mut str115 = String::new();
                    str115.push_str(&format(
                        &e.get("SIZE")?.get(Val::Int(0i64))?,
                        &String::new(),
                    )?);
                    str115.push_str("x");
                    str115.push_str(&format(
                        &e.get("SIZE")?.get(Val::Int(1i64))?,
                        &String::new(),
                    )?);
                    Val::Str(str115)
                }));
                fun111.call(args109, kw110)?
            };
            {
                let fun118 = e.get("scenes")?.attr("render")?;
                let mut args116 = Vec::new();
                let mut kw117 = Vec::new();
                fun118.call(args116, kw117)?
            };
            let assigned119 = {
                let fun122 = e.get("dict")?;
                let mut args120 = Vec::new();
                let mut kw121 = Vec::new();
                kw121.push(("cam".into(), e.get("CAM")?));
                kw121.push(("target".into(), e.get("TARGET")?));
                kw121.push(("span".into(), e.get("SPAN")?));
                kw121.push(("size".into(), e.get("SIZE")?));
                kw121.push(("outlet_psi".into(), e.get("OUTLET_PSI")?));
                kw121.push(("cylinder_psi".into(), e.get("CYLINDER_PSI")?));
                kw121.push(("points".into(), {
                    let fun125 = e.get("points")?;
                    let mut args123 = Vec::new();
                    let mut kw124 = Vec::new();
                    fun125.call(args123, kw124)?
                }));
                fun122.call(args120, kw121)?
            };
            e.set("metadata", assigned119.clone())?;
            {
                let fun128 = binary("truediv", e.get("OUT")?, Val::Str("points.json".into()))?
                    .attr("write_text")?;
                let mut args126 = Vec::new();
                let mut kw127 = Vec::new();
                args126.push(binary(
                    "add",
                    {
                        let fun131 = e.get("json")?.attr("dumps")?;
                        let mut args129 = Vec::new();
                        let mut kw130 = Vec::new();
                        args129.push(e.get("metadata")?);
                        kw130.push(("indent".into(), Val::Int(2i64)));
                        fun131.call(args129, kw130)?
                    },
                    Val::Str("\n".into()),
                )?);
                fun128.call(args126, kw127)?
            };
            {
                let fun134 = e.get("print")?;
                let mut args132 = Vec::new();
                let mut kw133 = Vec::new();
                args132.push({
                    let fun137 = e.get("json")?.attr("dumps")?;
                    let mut args135 = Vec::new();
                    let mut kw136 = Vec::new();
                    args135.push(e.get("metadata")?);
                    kw136.push(("indent".into(), Val::Int(2i64)));
                    fun137.call(args135, kw136)?
                });
                fun134.call(args132, kw133)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun140 = e.get("main")?;
        let mut args138 = Vec::new();
        let mut kw139 = Vec::new();
        fun140.call(args138, kw139)?
    };
    Ok(Val::None)
}
