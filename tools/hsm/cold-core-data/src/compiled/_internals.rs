#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
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
    let assigned17 = binary(
        "truediv",
        binary("truediv", e.get("_hw")?, Val::Str("printed-parts".into()))?,
        Val::Str("cold-core".into()),
    )?;
    e.set("_cold", assigned17.clone())?;
    for item18 in {
        let mut s = Vec::new();
        s.push(binary(
            "truediv",
            e.get("_hw")?,
            Val::Str("scripts".into()),
        )?);
        s.push(e.get("_cold")?);
        s.push(binary(
            "truediv",
            e.get("_cold")?,
            Val::Str("reservoir".into()),
        )?);
        s.push(binary(
            "truediv",
            e.get("_cold")?,
            Val::Str("reed-bridge".into()),
        )?);
        s.push(e.get("_here")?.attr("parent")?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("_p", item18)?;
        if {
            let v22 = {
                let fun21 = e.get("str")?;
                let mut args19 = Vec::new();
                let mut kw20 = Vec::new();
                args19.push(e.get("_p")?);
                fun21.call(args19, kw20)?
            };
            let v23 = e.get("sys")?.attr("path")?;
            Val::Bool(compare("not_in", v22.clone(), v23.clone())?.truthy()?)
        }
        .truthy()?
        {
            {
                let fun26 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args24 = Vec::new();
                let mut kw25 = Vec::new();
                args24.push(Val::Int(0i64));
                args24.push({
                    let fun29 = e.get("str")?;
                    let mut args27 = Vec::new();
                    let mut kw28 = Vec::new();
                    args27.push(e.get("_p")?);
                    fun29.call(args27, kw28)?
                });
                fun26.call(args24, kw25)?
            };
        }
    }
    e.set("F", rt.import_module("_fittings")?)?;
    e.set("_V", rt.import_module("_carbonator")?)?;
    e.set("_C", rt.import_module("_coil")?)?;
    e.set("_res", rt.import_module("reservoir")?)?;
    e.set("_bridge", rt.import_module("reed_bridge")?)?;
    e.set("_R", rt.import_module("_internal_routes")?)?;
    let mod30 = rt.import_module("_water_inlet_jet")?;
    e.set("JET_CAP_D", rt.member("_water_inlet_jet", "JET_CAP_D")?)?;
    e.set("JET_CAP_T", rt.member("_water_inlet_jet", "JET_CAP_T")?)?;
    e.set(
        "JET_PASSAGE_D",
        rt.member("_water_inlet_jet", "JET_PASSAGE_D")?,
    )?;
    let mod31 = rt.import_module("_cold_core_interface")?;
    e.set(
        "reed_column_axis_x",
        rt.member("_cold_core_interface", "reed_column_axis_x")?,
    )?;
    e.set(
        "reed_x_depth",
        rt.member("_cold_core_interface", "reed_x_depth")?,
    )?;
    e.set(
        "carbonator_outer_radius",
        rt.member("_cold_core_interface", "carbonator_outer_radius")?,
    )?;
    e.set(
        "carbonator_sensor_axis",
        rt.member("_cold_core_interface", "carbonator_sensor_axis")?,
    )?;
    let mod32 = rt.import_module("_reed_channels")?;
    e.set(
        "reed_y_center",
        rt.member("_reed_channels", "reed_y_center")?,
    )?;
    e.set(
        "reeds_per_reservoir",
        rt.member("_reed_channels", "reeds_per_reservoir")?,
    )?;
    e.set("_float", rt.import_module("_float_interface")?)?;
    let assigned33 = binary(
        "truediv",
        binary("truediv", e.get("_hw")?, Val::Str("reference".into()))?,
        Val::Str("jg-pp010822e".into()),
    )?;
    e.set("_ref", assigned33.clone())?;
    {
        let fun36 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args34 = Vec::new();
        let mut kw35 = Vec::new();
        args34.push(Val::Int(0i64));
        args34.push({
            let fun39 = e.get("str")?;
            let mut args37 = Vec::new();
            let mut kw38 = Vec::new();
            args37.push(e.get("_ref")?);
            fun39.call(args37, kw38)?
        });
        fun36.call(args34, kw35)?
    };
    e.set("_ptc", rt.import_module("jg_pp010822e")?)?;
    let mod40 = rt.import_module("_cadq_export")?;
    e.set("import_step", rt.member("_cadq_export", "import_step")?)?;
    let assigned41 = binary(
        "add",
        e.get("_ptc")?.attr("COLLET_LENGTH")?,
        e.get("_ptc")?.attr("HEX_LENGTH")?,
    )?;
    e.set("PTC_STANDOFF", assigned41.clone())?;
    let assigned42 = {
        let mut s = Vec::new();
        s.push(Val::Str("water-in".into()));
        Val::tuple(s)
    };
    e.set("PTC_PORTS", assigned42.clone())?;
    // collet_on
    e.set("collet_on", {
        let params = vec![("mouth".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned43 = {
                let fun46 = {
                    let fun49 = e.get("cq")?.attr("Vector")?;
                    let mut args47 = Vec::new();
                    let mut kw48 = Vec::new();
                    args47.extend(e.get("mouth")?.attr("axis")?.iter()?);
                    fun49.call(args47, kw48)?
                }
                .attr("normalized")?;
                let mut args44 = Vec::new();
                let mut kw45 = Vec::new();
                fun46.call(args44, kw45)?
            };
            e.set("out", assigned43.clone())?;
            let assigned50 = binary(
                "add",
                {
                    let fun53 = e.get("cq")?.attr("Vector")?;
                    let mut args51 = Vec::new();
                    let mut kw52 = Vec::new();
                    args51.extend(e.get("mouth")?.attr("pos")?.iter()?);
                    fun53.call(args51, kw52)?
                },
                {
                    let fun56 = e.get("out")?.attr("multiply")?;
                    let mut args54 = Vec::new();
                    let mut kw55 = Vec::new();
                    args54.push(e.get("PTC_STANDOFF")?);
                    fun56.call(args54, kw55)?
                },
            )?;
            e.set("origin", assigned50.clone())?;
            let assigned57 = {
                let fun60 = e.get("F")?.attr("stand_x_along")?;
                let mut args58 = Vec::new();
                let mut kw59 = Vec::new();
                args58.push({
                    let fun63 = {
                        let fun66 = e.get("import_step")?;
                        let mut args64 = Vec::new();
                        let mut kw65 = Vec::new();
                        args64.push({
                            let fun69 = e.get("str")?;
                            let mut args67 = Vec::new();
                            let mut kw68 = Vec::new();
                            args67.push(binary(
                                "truediv",
                                e.get("_ref")?,
                                Val::Str("jg-pp010822e.step".into()),
                            )?);
                            fun69.call(args67, kw68)?
                        });
                        fun66.call(args64, kw65)?
                    }
                    .attr("val")?;
                    let mut args61 = Vec::new();
                    let mut kw62 = Vec::new();
                    fun63.call(args61, kw62)?
                });
                kw59.push(("at".into(), e.get("origin")?));
                kw59.push(("axis".into(), unary("neg", e.get("out")?)?));
                fun60.call(args58, kw59)?
            };
            e.set("solid", assigned57.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("solid")?);
                s.push({
                    let fun72 = e.get("F")?.attr("Mouth")?;
                    let mut args70 = Vec::new();
                    let mut kw71 = Vec::new();
                    args70.push({
                        let fun75 = e.get("tuple")?;
                        let mut args73 = Vec::new();
                        let mut kw74 = Vec::new();
                        args73.push(e.get("origin")?);
                        fun75.call(args73, kw74)?
                    });
                    args70.push({
                        let fun78 = e.get("tuple")?;
                        let mut args76 = Vec::new();
                        let mut kw77 = Vec::new();
                        args76.push(e.get("out")?);
                        fun78.call(args76, kw77)?
                    });
                    args70.push(e.get("_ptc")?.attr("TUBE_D")?);
                    fun72.call(args70, kw71)?
                });
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // carbonator_collets
    e.set("carbonator_collets", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned79 = {
                let fun82 = e.get("_V")?.attr("mouths")?;
                let mut args80 = Vec::new();
                let mut kw81 = Vec::new();
                fun82.call(args80, kw81)?
            };
            e.set("vm", assigned79.clone())?;
            return Ok({
                let e = e.child();
                let out83 = Val::dict(vec![]);
                for item84 in e.get("PTC_PORTS")?.iter()? {
                    e.set("name", item84)?;
                    out83.set(e.get("name")?, {
                        let fun87 = e.get("collet_on")?;
                        let mut args85 = Vec::new();
                        let mut kw86 = Vec::new();
                        args85.push(e.get("vm")?.get(e.get("name")?)?);
                        fun87.call(args85, kw86)?
                    })?;
                }
                out83
            });
            Ok(Val::None)
        })
    })?;
    // water_inlet_jet
    e.set("water_inlet_jet", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned88 = {
                let fun91 = e.get("cq")?.attr("Vector")?;
                let mut args89 = Vec::new();
                let mut kw90 = Vec::new();
                args89.extend(
                    {
                        let fun94 = e.get("_V")?.attr("port_male_tip")?;
                        let mut args92 = Vec::new();
                        let mut kw93 = Vec::new();
                        args92.push(Val::Str("water-in".into()));
                        fun94.call(args92, kw93)?
                    }
                    .iter()?,
                );
                fun91.call(args89, kw90)?
            };
            e.set("tip", assigned88.clone())?;
            let assigned95 = {
                let fun98 = e.get("cq")?.attr("Vector")?;
                let mut args96 = Vec::new();
                let mut kw97 = Vec::new();
                args96.extend(
                    {
                        let fun101 = e.get("_V")?.attr("port_up")?;
                        let mut args99 = Vec::new();
                        let mut kw100 = Vec::new();
                        args99.push(Val::Str("water-in".into()));
                        fun101.call(args99, kw100)?
                    }
                    .iter()?,
                );
                fun98.call(args96, kw97)?
            };
            e.set("axis", assigned95.clone())?;
            let assigned102 = {
                let fun105 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                let mut args103 = Vec::new();
                let mut kw104 = Vec::new();
                args103.push(binary("truediv", e.get("JET_CAP_D")?, Val::Float(2.0f64))?);
                args103.push(e.get("JET_CAP_T")?);
                args103.push(e.get("tip")?);
                args103.push(e.get("axis")?);
                fun105.call(args103, kw104)?
            };
            e.set("cap", assigned102.clone())?;
            let assigned106 = {
                let fun109 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                let mut args107 = Vec::new();
                let mut kw108 = Vec::new();
                args107.push(binary(
                    "truediv",
                    e.get("JET_PASSAGE_D")?,
                    Val::Float(2.0f64),
                )?);
                args107.push(e.get("JET_CAP_T")?);
                args107.push(e.get("tip")?);
                args107.push(e.get("axis")?);
                fun109.call(args107, kw108)?
            };
            e.set("passage", assigned106.clone())?;
            return Ok({
                let fun112 = e.get("cap")?.attr("cut")?;
                let mut args110 = Vec::new();
                let mut kw111 = Vec::new();
                args110.push(e.get("passage")?);
                fun112.call(args110, kw111)?
            });
            Ok(Val::None)
        })
    })?;
    let assigned113 = e.get("_res")?.attr("rod_position_x")?;
    e.set("RES_ROD_X", assigned113.clone())?;
    let assigned114 = e.get("_res")?.attr("rod_position_y")?;
    e.set("RES_ROD_Y", assigned114.clone())?;
    let assigned115 = e.get("_res")?.attr("reservoir_rod_len")?;
    e.set("RES_ROD_LEN", assigned115.clone())?;
    // rod_seat_z
    e.set("rod_seat_z", {
        let params = vec![
            ("reservoir_solid".into(), None, false),
            ("x".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned116 = {
                let fun119 = e.get("reservoir_solid")?.attr("BoundingBox")?;
                let mut args117 = Vec::new();
                let mut kw118 = Vec::new();
                fun119.call(args117, kw118)?
            };
            e.set("bb", assigned116.clone())?;
            let assigned120 = {
                let fun123 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                let mut args121 = Vec::new();
                let mut kw122 = Vec::new();
                args121.push(binary(
                    "truediv",
                    e.get("_V")?.attr("ROD_D")?,
                    Val::Int(2i64),
                )?);
                args121.push(binary(
                    "add",
                    binary(
                        "sub",
                        binary(
                            "truediv",
                            binary(
                                "add",
                                e.get("bb")?.attr("zmin")?,
                                e.get("bb")?.attr("zmax")?,
                            )?,
                            Val::Float(2.0f64),
                        )?,
                        e.get("bb")?.attr("zmin")?,
                    )?,
                    Val::Int(1i64),
                )?);
                args121.push({
                    let fun126 = e.get("cq")?.attr("Vector")?;
                    let mut args124 = Vec::new();
                    let mut kw125 = Vec::new();
                    args124.push(e.get("x")?);
                    args124.push(e.get("RES_ROD_Y")?);
                    args124.push(binary("sub", e.get("bb")?.attr("zmin")?, Val::Int(1i64))?);
                    fun126.call(args124, kw125)?
                });
                args121.push({
                    let fun129 = e.get("cq")?.attr("Vector")?;
                    let mut args127 = Vec::new();
                    let mut kw128 = Vec::new();
                    args127.push(Val::Int(0i64));
                    args127.push(Val::Int(0i64));
                    args127.push(Val::Int(1i64));
                    fun129.call(args127, kw128)?
                });
                fun123.call(args121, kw122)?
            };
            e.set("probe", assigned120.clone())?;
            let assigned130 = {
                let fun133 = e.get("reservoir_solid")?.attr("intersect")?;
                let mut args131 = Vec::new();
                let mut kw132 = Vec::new();
                args131.push(e.get("probe")?);
                fun133.call(args131, kw132)?
            };
            e.set("hit", assigned130.clone())?;
            return Ok(
                if {
                    let v137 = {
                        let fun136 = e.get("hit")?.attr("Volume")?;
                        let mut args134 = Vec::new();
                        let mut kw135 = Vec::new();
                        fun136.call(args134, kw135)?
                    };
                    let v138 = Val::Float(1e-09f64);
                    Val::Bool(compare("gt", v137.clone(), v138.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun141 = e.get("hit")?.attr("BoundingBox")?;
                        let mut args139 = Vec::new();
                        let mut kw140 = Vec::new();
                        fun141.call(args139, kw140)?
                    }
                    .attr("zmax")?
                } else {
                    e.get("bb")?.attr("zmin")?
                },
            );
            Ok(Val::None)
        })
    })?;
    let assigned142 = e.get("reed_column_axis_x")?;
    e.set("REED_COLUMN_X", assigned142.clone())?;
    let assigned143 = e.get("_res")?.attr("float_magnet_travel_z")?;
    e.set("FLOAT_TRAVEL_Z", assigned143.clone())?;
    let assigned144 = e.get("_res")?.attr("reservoir_reed_pitch")?;
    e.set("RESERVOIR_REED_PITCH", assigned144.clone())?;
    // reservoir_reed_z
    e.set("reservoir_reed_z", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("_res")?.attr("reservoir_reed_centres_z")?);
            Ok(Val::None)
        })
    })?;
    // carbonator_reed_z
    e.set("carbonator_reed_z", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let mut s = Vec::new();
                s.push(binary(
                    "add",
                    e.get("_bridge")?.attr("reed_low_z")?,
                    e.get("_V")?.attr("carbonator_bottom_z")?,
                )?);
                s.push(binary(
                    "add",
                    e.get("_bridge")?.attr("reed_high_z")?,
                    e.get("_V")?.attr("carbonator_bottom_z")?,
                )?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // carbonator_reed_radius
    e.set("carbonator_reed_radius", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary(
                "add",
                e.get("carbonator_outer_radius")?,
                e.get("F")?.attr("REED_GLASS_R")?,
            )?);
            Ok(Val::None)
        })
    })?;
    // carbonator_reed_xy
    e.set("carbonator_reed_xy", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun147 = e.get("tuple")?;
                let mut args145 = Vec::new();
                let mut kw146 = Vec::new();
                args145.push({
                    let e = e.child();
                    let out148 = Val::list(vec![]);
                    for item149 in e.get("carbonator_sensor_axis")?.iter()? {
                        e.set("v", item149)?;
                        out148.attr("append")?.call(
                            vec![binary(
                                "mul",
                                {
                                    let fun152 = e.get("carbonator_reed_radius")?;
                                    let mut args150 = Vec::new();
                                    let mut kw151 = Vec::new();
                                    fun152.call(args150, kw151)?
                                },
                                e.get("v")?,
                            )?],
                            vec![],
                        )?;
                    }
                    out148
                });
                fun147.call(args145, kw146)?
            });
            Ok(Val::None)
        })
    })?;
    let assigned153 = e.get("_float")?.attr("guide_radial_clearance")?;
    e.set("FLOAT_SLOP", assigned153.clone())?;
    let assigned154 = e.get("_float")?.attr("float_edge_design_maximum")?;
    e.set("FLOAT_EDGE_DESIGN_MAXIMUM", assigned154.clone())?;
    // float_ride
    e.set("float_ride", {
        let params = vec![("park".into(), None, false), ("wall".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("park")?);
                s.push(binary(
                    "sub",
                    binary(
                        "sub",
                        e.get("wall")?,
                        binary("truediv", e.get("F")?.attr("FLOAT_OD")?, Val::Float(2.0f64))?,
                    )?,
                    binary("sub", e.get("park")?, e.get("FLOAT_SLOP")?)?,
                )?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // reservoir_wall_x
    e.set("reservoir_wall_x", {
        let params = vec![
            ("reservoir_solid".into(), None, false),
            ("side".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned155 = Val::Float(0.05f64);
            e.set("step", assigned155.clone())?;
            let assigned156 = {
                let fun159 = e.get("reservoir_solid")?.attr("BoundingBox")?;
                let mut args157 = Vec::new();
                let mut kw158 = Vec::new();
                fun159.call(args157, kw158)?
            };
            e.set("bb", assigned156.clone())?;
            let assigned160 = if {
                let v161 = e.get("side")?;
                let v162 = Val::Int(0i64);
                Val::Bool(compare("gt", v161.clone(), v162.clone())?.truthy()?)
            }
            .truthy()?
            {
                e.get("bb")?.attr("xmax")?
            } else {
                e.get("bb")?.attr("xmin")?
            };
            e.set("far", assigned160.clone())?;
            let assigned163 = e.get("RES_ROD_X")?;
            e.set("reach", assigned163.clone())?;
            while {
                let v189 = e.get("reach")?;
                let v190 = binary(
                    "add",
                    {
                        let fun188 = e.get("abs")?;
                        let mut args186 = Vec::new();
                        let mut kw187 = Vec::new();
                        args186.push(e.get("far")?);
                        fun188.call(args186, kw187)?
                    },
                    e.get("step")?,
                )?;
                Val::Bool(compare("lt", v189.clone(), v190.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned164 = binary("mul", e.get("side")?, e.get("reach")?)?;
                e.set("x", assigned164.clone())?;
                let assigned165 = {
                    let fun168 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                    let mut args166 = Vec::new();
                    let mut kw167 = Vec::new();
                    args166.push(e.get("step")?);
                    args166.push(Val::Float(1.0f64));
                    args166.push(Val::Float(1.0f64));
                    args166.push({
                        let fun171 = e.get("cq")?.attr("Vector")?;
                        let mut args169 = Vec::new();
                        let mut kw170 = Vec::new();
                        args169.push({
                            let fun174 = e.get("min")?;
                            let mut args172 = Vec::new();
                            let mut kw173 = Vec::new();
                            args172.push(e.get("x")?);
                            args172.push(binary(
                                "add",
                                e.get("x")?,
                                binary("mul", e.get("side")?, e.get("step")?)?,
                            )?);
                            fun174.call(args172, kw173)?
                        });
                        args169.push(binary("sub", e.get("RES_ROD_Y")?, Val::Float(0.5f64))?);
                        args169.push(binary(
                            "sub",
                            binary(
                                "truediv",
                                {
                                    let fun177 = e.get("sum")?;
                                    let mut args175 = Vec::new();
                                    let mut kw176 = Vec::new();
                                    args175.push(e.get("FLOAT_TRAVEL_Z")?);
                                    fun177.call(args175, kw176)?
                                },
                                Val::Float(2.0f64),
                            )?,
                            Val::Float(0.5f64),
                        )?);
                        fun171.call(args169, kw170)?
                    });
                    fun168.call(args166, kw167)?
                };
                e.set("bar", assigned165.clone())?;
                if {
                    let v184 = {
                        let fun180 = {
                            let fun183 = e.get("reservoir_solid")?.attr("intersect")?;
                            let mut args181 = Vec::new();
                            let mut kw182 = Vec::new();
                            args181.push(e.get("bar")?);
                            fun183.call(args181, kw182)?
                        }
                        .attr("Volume")?;
                        let mut args178 = Vec::new();
                        let mut kw179 = Vec::new();
                        fun180.call(args178, kw179)?
                    };
                    let v185 = Val::Float(1e-09f64);
                    Val::Bool(compare("gt", v184.clone(), v185.clone())?.truthy()?)
                }
                .truthy()?
                {
                    return Ok(e.get("reach")?);
                }
                e.set("reach", binary("add", e.get("reach")?, e.get("step")?)?)?;
            }
            return Ok({
                let fun193 = e.get("abs")?;
                let mut args191 = Vec::new();
                let mut kw192 = Vec::new();
                args191.push(e.get("far")?);
                fun193.call(args191, kw192)?
            });
            Ok(Val::None)
        })
    })?;
    // float_seats
    e.set("float_seats", {
        let params = vec![("reservoirs".into(), Some(Val::None), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned194 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("out", assigned194.clone())?;
            let assigned195 = {
                let mut s = Vec::new();
                s.push(e.get("_V")?.attr("ROD_RADIUS")?);
                s.push(binary(
                    "truediv",
                    e.get("_V")?.attr("TUBE_ID")?,
                    Val::Float(2.0f64),
                )?);
                Val::tuple(s)
            };
            let unpack196 = unpack(assigned195.clone(), 2)?;
            e.set("park", unpack196[0].clone())?;
            e.set("wall", unpack196[1].clone())?;
            let assigned197 = {
                let fun200 = e.get("float_ride")?;
                let mut args198 = Vec::new();
                let mut kw199 = Vec::new();
                args198.push(e.get("park")?);
                args198.push(e.get("wall")?);
                fun200.call(args198, kw199)?
            };
            let unpack201 = unpack(assigned197.clone(), 2)?;
            e.set("centre", unpack201[0].clone())?;
            e.set("standoff", unpack201[1].clone())?;
            let assigned202 = {
                let mut s = Vec::new();
                s.push(e.get("park")?);
                s.push(e.get("wall")?);
                s.push(e.get("centre")?);
                s.push(e.get("standoff")?);
                Val::tuple(s)
            };
            e.get("out")?
                .set(Val::Str("float-carb".into()), assigned202.clone())?;
            for item203 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("a".into()));
                    s.push(unary("pos", Val::Int(1i64))?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("b".into()));
                    s.push(unary("neg", Val::Int(1i64))?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack223 = unpack(item203, 2)?;
                e.set("name", unpack223[0].clone())?;
                e.set("side", unpack223[1].clone())?;
                let assigned204 = {
                    let fun207 = {
                        let v208 = e.get("reservoirs")?;
                        if v208.truthy()? {
                            v208
                        } else {
                            {
                                let d = Val::dict(vec![]);
                                d
                            }
                        }
                    }
                    .attr("get")?;
                    let mut args205 = Vec::new();
                    let mut kw206 = Vec::new();
                    args205.push({
                        let mut str209 = String::new();
                        str209.push_str("reservoir-");
                        str209.push_str(&format(&e.get("name")?, &String::new())?);
                        Val::Str(str209)
                    });
                    fun207.call(args205, kw206)?
                };
                e.set("body", assigned204.clone())?;
                if {
                    let v210 = e.get("body")?;
                    let v211 = Val::None;
                    Val::Bool(compare("is", v210.clone(), v211.clone())?.truthy()?)
                }
                .truthy()?
                {
                    continue;
                }
                let assigned212 = {
                    let fun215 = e.get("reservoir_wall_x")?;
                    let mut args213 = Vec::new();
                    let mut kw214 = Vec::new();
                    args213.push(e.get("body")?);
                    args213.push(e.get("side")?);
                    fun215.call(args213, kw214)?
                };
                e.set("wall", assigned212.clone())?;
                let assigned216 = {
                    let fun219 = e.get("float_ride")?;
                    let mut args217 = Vec::new();
                    let mut kw218 = Vec::new();
                    args217.push(e.get("RES_ROD_X")?);
                    args217.push(e.get("wall")?);
                    fun219.call(args217, kw218)?
                };
                let unpack220 = unpack(assigned216.clone(), 2)?;
                e.set("centre", unpack220[0].clone())?;
                e.set("standoff", unpack220[1].clone())?;
                let assigned221 = {
                    let mut s = Vec::new();
                    s.push(e.get("RES_ROD_X")?);
                    s.push(e.get("wall")?);
                    s.push(e.get("centre")?);
                    s.push(e.get("standoff")?);
                    Val::tuple(s)
                };
                e.get("out")?.set(
                    {
                        let mut str222 = String::new();
                        str222.push_str("float-");
                        str222.push_str(&format(&e.get("name")?, &String::new())?);
                        Val::Str(str222)
                    },
                    assigned221.clone(),
                )?;
            }
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    // level_bodies
    e.set("level_bodies", {
        let params = vec![("reservoirs".into(), Some(Val::None), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned224 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("out", assigned224.clone())?;
            let assigned225 = {
                let fun228 = e.get("float_seats")?;
                let mut args226 = Vec::new();
                let mut kw227 = Vec::new();
                args226.push(e.get("reservoirs")?);
                fun228.call(args226, kw227)?
            };
            e.set("seats", assigned225.clone())?;
            let assigned229 = {
                let fun232 = e.get("F")?.attr("float_capsule")?;
                let mut args230 = Vec::new();
                let mut kw231 = Vec::new();
                kw231.push(("centre".into(), {
                    let mut s = Vec::new();
                    s.extend(
                        {
                            let e = e.child();
                            let out233 = Val::list(vec![]);
                            for item234 in e.get("carbonator_sensor_axis")?.iter()? {
                                e.set("v", item234)?;
                                out233.attr("append")?.call(
                                    vec![binary(
                                        "mul",
                                        e.get("seats")?
                                            .get(Val::Str("float-carb".into()))?
                                            .get(Val::Int(2i64))?,
                                        e.get("v")?,
                                    )?],
                                    vec![],
                                )?;
                            }
                            out233
                        }
                        .iter()?,
                    );
                    s.push(binary(
                        "add",
                        e.get("_bridge")?.attr("reed_high_z")?,
                        e.get("_V")?.attr("carbonator_bottom_z")?,
                    )?);
                    Val::tuple(s)
                }));
                fun232.call(args230, kw231)?
            };
            e.get("out")?
                .set(Val::Str("float-carb".into()), assigned229.clone())?;
            for item235 in {
                let fun246 = e.get("enumerate")?;
                let mut args244 = Vec::new();
                let mut kw245 = Vec::new();
                args244.push({
                    let fun249 = e.get("carbonator_reed_z")?;
                    let mut args247 = Vec::new();
                    let mut kw248 = Vec::new();
                    fun249.call(args247, kw248)?
                });
                kw245.push(("start".into(), Val::Int(1i64)));
                fun246.call(args244, kw245)?
            }
            .iter()?
            {
                let unpack250 = unpack(item235, 2)?;
                e.set("i", unpack250[0].clone())?;
                e.set("z", unpack250[1].clone())?;
                let assigned236 = {
                    let fun239 = e.get("F")?.attr("reed")?;
                    let mut args237 = Vec::new();
                    let mut kw238 = Vec::new();
                    kw238.push(("centre".into(), {
                        let mut s = Vec::new();
                        s.extend(
                            {
                                let fun242 = e.get("carbonator_reed_xy")?;
                                let mut args240 = Vec::new();
                                let mut kw241 = Vec::new();
                                fun242.call(args240, kw241)?
                            }
                            .iter()?,
                        );
                        s.push(e.get("z")?);
                        Val::tuple(s)
                    }));
                    fun239.call(args237, kw238)?
                };
                e.get("out")?.set(
                    {
                        let mut str243 = String::new();
                        str243.push_str("reed-carb-");
                        str243.push_str(&format(&e.get("i")?, &String::new())?);
                        Val::Str(str243)
                    },
                    assigned236.clone(),
                )?;
            }
            for item251 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("a".into()));
                    s.push(unary("pos", Val::Int(1i64))?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("b".into()));
                    s.push(unary("neg", Val::Int(1i64))?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack301 = unpack(item251, 2)?;
                e.set("name", unpack301[0].clone())?;
                e.set("side", unpack301[1].clone())?;
                let assigned252 = {
                    let fun255 = {
                        let v256 = e.get("reservoirs")?;
                        if v256.truthy()? {
                            v256
                        } else {
                            {
                                let d = Val::dict(vec![]);
                                d
                            }
                        }
                    }
                    .attr("get")?;
                    let mut args253 = Vec::new();
                    let mut kw254 = Vec::new();
                    args253.push({
                        let mut str257 = String::new();
                        str257.push_str("reservoir-");
                        str257.push_str(&format(&e.get("name")?, &String::new())?);
                        Val::Str(str257)
                    });
                    fun255.call(args253, kw254)?
                };
                e.set("body", assigned252.clone())?;
                let assigned258 = if {
                    let v259 = e.get("body")?;
                    let v260 = Val::None;
                    Val::Bool(compare("is_not", v259.clone(), v260.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun263 = e.get("rod_seat_z")?;
                        let mut args261 = Vec::new();
                        let mut kw262 = Vec::new();
                        args261.push(e.get("body")?);
                        args261.push(binary("mul", e.get("side")?, e.get("RES_ROD_X")?)?);
                        fun263.call(args261, kw262)?
                    }
                } else {
                    Val::Float(0.0f64)
                };
                e.set("z0", assigned258.clone())?;
                let assigned264 = {
                    let fun267 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                    let mut args265 = Vec::new();
                    let mut kw266 = Vec::new();
                    args265.push(binary(
                        "truediv",
                        e.get("_V")?.attr("ROD_D")?,
                        Val::Int(2i64),
                    )?);
                    args265.push(e.get("RES_ROD_LEN")?);
                    args265.push({
                        let fun270 = e.get("cq")?.attr("Vector")?;
                        let mut args268 = Vec::new();
                        let mut kw269 = Vec::new();
                        args268.push(binary("mul", e.get("side")?, e.get("RES_ROD_X")?)?);
                        args268.push(e.get("RES_ROD_Y")?);
                        args268.push(e.get("z0")?);
                        fun270.call(args268, kw269)?
                    });
                    args265.push({
                        let fun273 = e.get("cq")?.attr("Vector")?;
                        let mut args271 = Vec::new();
                        let mut kw272 = Vec::new();
                        args271.push(Val::Int(0i64));
                        args271.push(Val::Int(0i64));
                        args271.push(Val::Int(1i64));
                        fun273.call(args271, kw272)?
                    });
                    fun267.call(args265, kw266)?
                };
                e.get("out")?.set(
                    {
                        let mut str274 = String::new();
                        str274.push_str("float-rod-");
                        str274.push_str(&format(&e.get("name")?, &String::new())?);
                        Val::Str(str274)
                    },
                    assigned264.clone(),
                )?;
                let assigned275 = {
                    let fun278 = e.get("seats")?.attr("get")?;
                    let mut args276 = Vec::new();
                    let mut kw277 = Vec::new();
                    args276.push({
                        let mut str279 = String::new();
                        str279.push_str("float-");
                        str279.push_str(&format(&e.get("name")?, &String::new())?);
                        Val::Str(str279)
                    });
                    fun278.call(args276, kw277)?
                };
                e.set("seat", assigned275.clone())?;
                let assigned280 = {
                    let fun283 = e.get("F")?.attr("float_capsule")?;
                    let mut args281 = Vec::new();
                    let mut kw282 = Vec::new();
                    kw282.push(("centre".into(), {
                        let mut s = Vec::new();
                        s.push(binary(
                            "mul",
                            e.get("side")?,
                            if e.get("seat")?.truthy()? {
                                e.get("seat")?.get(Val::Int(2i64))?
                            } else {
                                e.get("RES_ROD_X")?
                            },
                        )?);
                        s.push(e.get("RES_ROD_Y")?);
                        s.push(binary(
                            "truediv",
                            {
                                let fun286 = e.get("sum")?;
                                let mut args284 = Vec::new();
                                let mut kw285 = Vec::new();
                                args284.push(e.get("FLOAT_TRAVEL_Z")?);
                                fun286.call(args284, kw285)?
                            },
                            Val::Float(2.0f64),
                        )?);
                        Val::tuple(s)
                    }));
                    fun283.call(args281, kw282)?
                };
                e.get("out")?.set(
                    {
                        let mut str287 = String::new();
                        str287.push_str("float-");
                        str287.push_str(&format(&e.get("name")?, &String::new())?);
                        Val::Str(str287)
                    },
                    assigned280.clone(),
                )?;
                for item288 in {
                    let fun296 = e.get("enumerate")?;
                    let mut args294 = Vec::new();
                    let mut kw295 = Vec::new();
                    args294.push({
                        let fun299 = e.get("reservoir_reed_z")?;
                        let mut args297 = Vec::new();
                        let mut kw298 = Vec::new();
                        fun299.call(args297, kw298)?
                    });
                    kw295.push(("start".into(), Val::Int(1i64)));
                    fun296.call(args294, kw295)?
                }
                .iter()?
                {
                    let unpack300 = unpack(item288, 2)?;
                    e.set("i", unpack300[0].clone())?;
                    e.set("z", unpack300[1].clone())?;
                    let assigned289 = {
                        let fun292 = e.get("F")?.attr("reed")?;
                        let mut args290 = Vec::new();
                        let mut kw291 = Vec::new();
                        kw291.push(("centre".into(), {
                            let mut s = Vec::new();
                            s.push(binary("mul", e.get("side")?, e.get("REED_COLUMN_X")?)?);
                            s.push(e.get("reed_y_center")?);
                            s.push(e.get("z")?);
                            Val::tuple(s)
                        }));
                        fun292.call(args290, kw291)?
                    };
                    e.get("out")?.set(
                        {
                            let mut str293 = String::new();
                            str293.push_str("reed-");
                            str293.push_str(&format(&e.get("name")?, &String::new())?);
                            str293.push_str("-");
                            str293.push_str(&format(&e.get("i")?, &String::new())?);
                            Val::Str(str293)
                        },
                        assigned289.clone(),
                    )?;
                }
            }
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    // _cap_z
    e.set("_cap_z", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary(
                "sub",
                e.get("_R")?.attr("reservoir_cap_top_z")?,
                e.get("_res")?.attr("cap_total_height")?,
            )?);
            Ok(Val::None)
        })
    })?;
    let assigned302 = binary("mul", e.get("F")?.attr("TO92_W")?, Val::Float(0.71f64))?;
    e.set("PROBE_STANDOFF", assigned302.clone())?;
    // probes
    e.set("probes", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned303 = {
                let fun306 = e.get("_C")?.attr("gap_z_near")?;
                let mut args304 = Vec::new();
                let mut kw305 = Vec::new();
                args304.push(Val::Float(180.0f64));
                args304.push(binary(
                    "truediv",
                    binary(
                        "add",
                        e.get("_V")?.attr("interior_z")?.get(Val::Int(0i64))?,
                        e.get("_V")?.attr("interior_z")?.get(Val::Int(1i64))?,
                    )?,
                    Val::Float(2.0f64),
                )?);
                fun306.call(args304, kw305)?
            };
            e.set("carbonator_z", assigned303.clone())?;
            let assigned307 = {
                let mut s = Vec::new();
                s.push(unary(
                    "neg",
                    binary(
                        "add",
                        e.get("carbonator_outer_radius")?,
                        e.get("PROBE_STANDOFF")?,
                    )?,
                )?);
                s.push(Val::Float(0.0f64));
                s.push(e.get("carbonator_z")?);
                Val::tuple(s)
            };
            e.set("carbonator_at", assigned307.clone())?;
            let assigned308 = {
                let fun311 = {
                    let fun314 = e.get("_C")?.attr("_at")?;
                    let mut args312 = Vec::new();
                    let mut kw313 = Vec::new();
                    args312.push(e.get("_C")?.attr("AZ_OUT")?);
                    args312.push(e.get("_C")?.attr("evap_tail_high_z")?);
                    args312.push(binary(
                        "add",
                        binary(
                            "add",
                            e.get("_C")?.attr("WIND_R")?,
                            e.get("_C")?.attr("TUBE_R")?,
                        )?,
                        binary("truediv", e.get("F")?.attr("TO92_W")?, Val::Float(2.0f64))?,
                    )?);
                    fun314.call(args312, kw313)?
                }
                .attr("toTuple")?;
                let mut args309 = Vec::new();
                let mut kw310 = Vec::new();
                fun311.call(args309, kw310)?
            };
            e.set("coil_at", assigned308.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("probe-carbonator-ds18b20".into()), {
                    let fun317 = e.get("F")?.attr("to92")?;
                    let mut args315 = Vec::new();
                    let mut kw316 = Vec::new();
                    kw316.push(("centre".into(), e.get("carbonator_at")?));
                    kw316.push(("axis".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        Val::tuple(s)
                    }));
                    fun317.call(args315, kw316)?
                })?;
                d.set(Val::Str("probe-coil-ds18s20".into()), {
                    let fun320 = e.get("F")?.attr("to92")?;
                    let mut args318 = Vec::new();
                    let mut kw319 = Vec::new();
                    kw319.push(("centre".into(), e.get("coil_at")?));
                    kw319.push(("axis".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        Val::tuple(s)
                    }));
                    fun320.call(args318, kw319)?
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // bodies
    e.set("bodies", {
        let params = vec![("reservoirs".into(), Some(Val::None), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned321 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("water-inlet-jet-cap-nominal".into()), {
                    let fun324 = e.get("water_inlet_jet")?;
                    let mut args322 = Vec::new();
                    let mut kw323 = Vec::new();
                    fun324.call(args322, kw323)?
                })?;
                d
            };
            e.set("out", assigned321.clone())?;
            for item325 in {
                let fun330 = {
                    let fun333 = e.get("carbonator_collets")?;
                    let mut args331 = Vec::new();
                    let mut kw332 = Vec::new();
                    fun333.call(args331, kw332)?
                }
                .attr("items")?;
                let mut args328 = Vec::new();
                let mut kw329 = Vec::new();
                fun330.call(args328, kw329)?
            }
            .iter()?
            {
                let unpack334 = unpack(item325, 2)?;
                e.set("name", unpack334[0].clone())?;
                let unpack335 = unpack(unpack334[1].clone(), 2)?;
                e.set("solid", unpack335[0].clone())?;
                e.set("_m", unpack335[1].clone())?;
                let assigned326 = e.get("solid")?;
                e.get("out")?.set(
                    {
                        let mut str327 = String::new();
                        str327.push_str("collet-");
                        str327.push_str(&format(&e.get("name")?, &String::new())?);
                        Val::Str(str327)
                    },
                    assigned326.clone(),
                )?;
            }
            {
                let fun338 = e.get("out")?.attr("update")?;
                let mut args336 = Vec::new();
                let mut kw337 = Vec::new();
                args336.push({
                    let fun341 = e.get("level_bodies")?;
                    let mut args339 = Vec::new();
                    let mut kw340 = Vec::new();
                    args339.push(e.get("reservoirs")?);
                    fun341.call(args339, kw340)?
                });
                fun338.call(args336, kw337)?
            };
            {
                let fun344 = e.get("out")?.attr("update")?;
                let mut args342 = Vec::new();
                let mut kw343 = Vec::new();
                args342.push({
                    let fun347 = e.get("probes")?;
                    let mut args345 = Vec::new();
                    let mut kw346 = Vec::new();
                    fun347.call(args345, kw346)?
                });
                fun344.call(args342, kw343)?
            };
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    // report
    e.set("report", {
        let params = vec![
            ("reservoirs".into(), Some(Val::None), false),
            ("rod_seats".into(), Some(Val::None), true),
            ("seats".into(), Some(Val::None), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun350 = e.get("print")?;
                let mut args348 = Vec::new();
                let mut kw349 = Vec::new();
                args348.push(Val::Str("  internals".into()));
                fun350.call(args348, kw349)?
            };
            {
                let fun353 = e.get("print")?;
                let mut args351 = Vec::new();
                let mut kw352 = Vec::new();
                args351.push({
                    let mut str354 = String::new();
                    str354.push_str("    inlet jet       nominal ⌀");
                    str354.push_str(&format(
                        &e.get("JET_CAP_D")?,
                        &val_string({
                            let mut str355 = String::new();
                            str355.push_str("g");
                            Val::Str(str355)
                        })?,
                    )?);
                    str354.push_str(" × ");
                    str354.push_str(&format(
                        &e.get("JET_CAP_T")?,
                        &val_string({
                            let mut str356 = String::new();
                            str356.push_str("g");
                            Val::Str(str356)
                        })?,
                    )?);
                    str354.push_str(" cap, ⌀");
                    str354.push_str(&format(
                        &e.get("JET_PASSAGE_D")?,
                        &val_string({
                            let mut str357 = String::new();
                            str357.push_str("g");
                            Val::Str(str357)
                        })?,
                    )?);
                    str354.push_str(" passage; fit, weld and installed projection unqualified");
                    Val::Str(str354)
                });
                fun353.call(args351, kw352)?
            };
            {
                let fun360 = e.get("print")?;
                let mut args358 = Vec::new();
                let mut kw359 = Vec::new();
                args358.push({
                    let mut str361 = String::new();
                    str361.push_str("    carb reeds      z ");
                    str361.push_str(&format(
                        &{
                            let fun364 = Val::Str(", ".into()).attr("join")?;
                            let mut args362 = Vec::new();
                            let mut kw363 = Vec::new();
                            args362.push({
                                let e = e.child();
                                let out365 = Val::list(vec![]);
                                for item366 in {
                                    let fun369 = e.get("carbonator_reed_z")?;
                                    let mut args367 = Vec::new();
                                    let mut kw368 = Vec::new();
                                    fun369.call(args367, kw368)?
                                }
                                .iter()?
                                {
                                    e.set("z", item366)?;
                                    out365.attr("append")?.call(
                                        vec![{
                                            let mut str370 = String::new();
                                            str370.push_str(&format(
                                                &e.get("z")?,
                                                &val_string({
                                                    let mut str371 = String::new();
                                                    str371.push_str(".1f");
                                                    Val::Str(str371)
                                                })?,
                                            )?);
                                            Val::Str(str370)
                                        }],
                                        vec![],
                                    )?;
                                }
                                out365
                            });
                            fun364.call(args362, kw363)?
                        },
                        &String::new(),
                    )?);
                    str361.push_str(" at XY ");
                    str361.push_str(&format(
                        &{
                            let fun374 = e.get("carbonator_reed_xy")?;
                            let mut args372 = Vec::new();
                            let mut kw373 = Vec::new();
                            fun374.call(args372, kw373)?
                        },
                        &String::new(),
                    )?);
                    Val::Str(str361)
                });
                fun360.call(args358, kw359)?
            };
            {
                let fun377 = e.get("print")?;
                let mut args375 = Vec::new();
                let mut kw376 = Vec::new();
                args375.push({
                    let mut str378 = String::new();
                    str378.push_str("    res reeds       z ");
                    str378.push_str(&format(
                        &{
                            let fun381 = Val::Str(", ".into()).attr("join")?;
                            let mut args379 = Vec::new();
                            let mut kw380 = Vec::new();
                            args379.push({
                                let e = e.child();
                                let out382 = Val::list(vec![]);
                                for item383 in {
                                    let fun386 = e.get("reservoir_reed_z")?;
                                    let mut args384 = Vec::new();
                                    let mut kw385 = Vec::new();
                                    fun386.call(args384, kw385)?
                                }
                                .iter()?
                                {
                                    e.set("z", item383)?;
                                    out382.attr("append")?.call(
                                        vec![{
                                            let mut str387 = String::new();
                                            str387.push_str(&format(
                                                &e.get("z")?,
                                                &val_string({
                                                    let mut str388 = String::new();
                                                    str388.push_str(".1f");
                                                    Val::Str(str388)
                                                })?,
                                            )?);
                                            Val::Str(str387)
                                        }],
                                        vec![],
                                    )?;
                                }
                                out382
                            });
                            fun381.call(args379, kw380)?
                        },
                        &String::new(),
                    )?);
                    str378.push_str(" at x ±");
                    str378.push_str(&format(
                        &e.get("REED_COLUMN_X")?,
                        &val_string({
                            let mut str389 = String::new();
                            str389.push_str(".1f");
                            Val::Str(str389)
                        })?,
                    )?);
                    str378.push_str(", y ");
                    str378.push_str(&format(
                        &e.get("reed_y_center")?,
                        &val_string({
                            let mut str390 = String::new();
                            str390.push_str(".1f");
                            Val::Str(str390)
                        })?,
                    )?);
                    str378.push_str(", ");
                    str378.push_str(&format(
                        &e.get("RESERVOIR_REED_PITCH")?,
                        &val_string({
                            let mut str391 = String::new();
                            str391.push_str(".0f");
                            Val::Str(str391)
                        })?,
                    )?);
                    str378.push_str(" mm pitch in a ");
                    str378.push_str(&format(
                        &e.get("FLOAT_TRAVEL_Z")?.get(Val::Int(0i64))?,
                        &val_string({
                            let mut str392 = String::new();
                            str392.push_str(".0f");
                            Val::Str(str392)
                        })?,
                    )?);
                    str378.push_str("..");
                    str378.push_str(&format(
                        &e.get("FLOAT_TRAVEL_Z")?.get(Val::Int(1i64))?,
                        &val_string({
                            let mut str393 = String::new();
                            str393.push_str(".0f");
                            Val::Str(str393)
                        })?,
                    )?);
                    str378.push_str(" travel");
                    Val::Str(str378)
                });
                fun377.call(args375, kw376)?
            };
            let assigned394 = Val::Str("".into());
            e.set("seat_text", assigned394.clone())?;
            if {
                let v395 = e.get("rod_seats")?;
                let v396 = Val::None;
                Val::Bool(compare("is_not", v395.clone(), v396.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned397 = binary("add", Val::Str(", seated at z ".into()), {
                    let fun400 = Val::Str(", ".into()).attr("join")?;
                    let mut args398 = Vec::new();
                    let mut kw399 = Vec::new();
                    args398.push({
                        let e = e.child();
                        let out401 = Val::list(vec![]);
                        for item402 in {
                            let mut s = Vec::new();
                            s.push(Val::Str("a".into()));
                            s.push(Val::Str("b".into()));
                            Val::tuple(s)
                        }
                        .iter()?
                        {
                            e.set("n", item402)?;
                            out401.attr("append")?.call(
                                vec![{
                                    let mut str403 = String::new();
                                    str403.push_str(&format(
                                        &e.get("rod_seats")?.get(e.get("n")?)?,
                                        &val_string({
                                            let mut str404 = String::new();
                                            str404.push_str(".1f");
                                            Val::Str(str404)
                                        })?,
                                    )?);
                                    Val::Str(str403)
                                }],
                                vec![],
                            )?;
                        }
                        out401
                    });
                    fun400.call(args398, kw399)?
                })?;
                e.set("seat_text", assigned397.clone())?;
            } else {
                if e.get("reservoirs")?.truthy()? {
                    let assigned405 = binary("add", Val::Str(", seated at z ".into()), {
                        let fun408 = Val::Str(", ".into()).attr("join")?;
                        let mut args406 = Vec::new();
                        let mut kw407 = Vec::new();
                        args406.push({
                            let e = e.child();
                            let out409 = Val::list(vec![]);
                            for item410 in {
                                let mut s = Vec::new();
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(Val::Str("a".into()));
                                    s.push(Val::Int(1i64));
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(Val::Str("b".into()));
                                    s.push(unary("neg", Val::Int(1i64))?);
                                    Val::tuple(s)
                                });
                                Val::tuple(s)
                            }
                            .iter()?
                            {
                                let unpack411 = unpack(item410, 2)?;
                                e.set("n", unpack411[0].clone())?;
                                e.set("s", unpack411[1].clone())?;
                                if {
                                    let v413 = {
                                        let mut str412 = String::new();
                                        str412.push_str("reservoir-");
                                        str412.push_str(&format(&e.get("n")?, &String::new())?);
                                        Val::Str(str412)
                                    };
                                    let v414 = e.get("reservoirs")?;
                                    Val::Bool(compare("in", v413.clone(), v414.clone())?.truthy()?)
                                }
                                .truthy()?
                                {
                                    out409.attr("append")?.call(
                                        vec![{
                                            let mut str415 = String::new();
                                            str415.push_str(&format(
                                                &{
                                                    let fun418 = e.get("rod_seat_z")?;
                                                    let mut args416 = Vec::new();
                                                    let mut kw417 = Vec::new();
                                                    args416.push(e.get("reservoirs")?.get({
                                                        let mut str419 = String::new();
                                                        str419.push_str("reservoir-");
                                                        str419.push_str(&format(
                                                            &e.get("n")?,
                                                            &String::new(),
                                                        )?);
                                                        Val::Str(str419)
                                                    })?);
                                                    args416.push(binary(
                                                        "mul",
                                                        e.get("s")?,
                                                        e.get("RES_ROD_X")?,
                                                    )?);
                                                    fun418.call(args416, kw417)?
                                                },
                                                &val_string({
                                                    let mut str420 = String::new();
                                                    str420.push_str(".1f");
                                                    Val::Str(str420)
                                                })?,
                                            )?);
                                            Val::Str(str415)
                                        }],
                                        vec![],
                                    )?;
                                }
                            }
                            out409
                        });
                        fun408.call(args406, kw407)?
                    })?;
                    e.set("seat_text", assigned405.clone())?;
                }
            }
            {
                let fun423 = e.get("print")?;
                let mut args421 = Vec::new();
                let mut kw422 = Vec::new();
                args421.push({
                    let mut str424 = String::new();
                    str424.push_str("    res rods        ⌀");
                    str424.push_str(&format(
                        &e.get("_V")?.attr("ROD_D")?,
                        &val_string({
                            let mut str425 = String::new();
                            str425.push_str(".3f");
                            Val::Str(str425)
                        })?,
                    )?);
                    str424.push_str(" × ");
                    str424.push_str(&format(
                        &e.get("RES_ROD_LEN")?,
                        &val_string({
                            let mut str426 = String::new();
                            str426.push_str(".1f");
                            Val::Str(str426)
                        })?,
                    )?);
                    str424.push_str(" at x ±");
                    str424.push_str(&format(
                        &e.get("RES_ROD_X")?,
                        &val_string({
                            let mut str427 = String::new();
                            str427.push_str(".0f");
                            Val::Str(str427)
                        })?,
                    )?);
                    str424.push_str(", y ");
                    str424.push_str(&format(
                        &e.get("RES_ROD_Y")?,
                        &val_string({
                            let mut str428 = String::new();
                            str428.push_str(".1f");
                            Val::Str(str428)
                        })?,
                    )?);
                    str424.push_str(&format(&e.get("seat_text")?, &String::new())?);
                    Val::Str(str424)
                });
                fun423.call(args421, kw422)?
            };
            {
                let fun431 = e.get("print")?;
                let mut args429 = Vec::new();
                let mut kw430 = Vec::new();
                args429.push({
                    let mut str432 = String::new();
                    str432.push_str("    float slop      ⌀");
                    str432.push_str(&format(
                        &e.get("F")?.attr("FLOAT_BORE")?,
                        &val_string({
                            let mut str433 = String::new();
                            str433.push_str(".2f");
                            Val::Str(str433)
                        })?,
                    )?);
                    str432.push_str(" bore on a ⌀");
                    str432.push_str(&format(
                        &e.get("_V")?.attr("ROD_D")?,
                        &val_string({
                            let mut str434 = String::new();
                            str434.push_str(".3f");
                            Val::Str(str434)
                        })?,
                    )?);
                    str432.push_str(" rod — ");
                    str432.push_str(&format(
                        &e.get("FLOAT_SLOP")?,
                        &val_string({
                            let mut str435 = String::new();
                            str435.push_str(".3f");
                            Val::Str(str435)
                        })?,
                    )?);
                    str432.push_str(" mm radial freedom; printed-float bench edge limit ");
                    str432.push_str(&format(
                        &e.get("_float")?.attr("float_edge_reported_usable_limit")?,
                        &val_string({
                            let mut str436 = String::new();
                            str436.push_str("g");
                            Val::Str(str436)
                        })?,
                    )?);
                    str432.push_str(" mm");
                    Val::Str(str432)
                });
                fun431.call(args429, kw430)?
            };
            for item437 in {
                let fun449 = e.get("sorted")?;
                let mut args447 = Vec::new();
                let mut kw448 = Vec::new();
                args447.push({
                    let fun452 = if {
                        let v453 = e.get("seats")?;
                        let v454 = Val::None;
                        Val::Bool(compare("is", v453.clone(), v454.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun457 = e.get("float_seats")?;
                            let mut args455 = Vec::new();
                            let mut kw456 = Vec::new();
                            args455.push(e.get("reservoirs")?);
                            fun457.call(args455, kw456)?
                        }
                    } else {
                        e.get("seats")?
                    }
                    .attr("items")?;
                    let mut args450 = Vec::new();
                    let mut kw451 = Vec::new();
                    fun452.call(args450, kw451)?
                });
                fun449.call(args447, kw448)?
            }
            .iter()?
            {
                let unpack458 = unpack(item437, 2)?;
                e.set("name", unpack458[0].clone())?;
                let unpack459 = unpack(unpack458[1].clone(), 4)?;
                e.set("park", unpack459[0].clone())?;
                e.set("wall", unpack459[1].clone())?;
                e.set("centre", unpack459[2].clone())?;
                e.set("standoff", unpack459[3].clone())?;
                {
                    let fun440 = e.get("print")?;
                    let mut args438 = Vec::new();
                    let mut kw439 = Vec::new();
                    args438.push({
                        let mut str441 = String::new();
                        str441.push_str("    ");
                        str441.push_str(&format(
                            &e.get("name")?,
                            &val_string({
                                let mut str442 = String::new();
                                str442.push_str("15");
                                Val::Str(str442)
                            })?,
                        )?);
                        str441.push_str(" rod axis ");
                        str441.push_str(&format(
                            &e.get("park")?,
                            &val_string({
                                let mut str443 = String::new();
                                str443.push_str(".3f");
                                Val::Str(str443)
                            })?,
                        )?);
                        str441.push_str(", wet wall ");
                        str441.push_str(&format(
                            &e.get("wall")?,
                            &val_string({
                                let mut str444 = String::new();
                                str444.push_str(".3f");
                                Val::Str(str444)
                            })?,
                        )?);
                        str441.push_str(", float axis ");
                        str441.push_str(&format(
                            &e.get("centre")?,
                            &val_string({
                                let mut str445 = String::new();
                                str445.push_str(".3f");
                                Val::Str(str445)
                            })?,
                        )?);
                        str441.push_str(" — maximum body/wall gap ");
                        str441.push_str(&format(
                            &e.get("standoff")?,
                            &val_string({
                                let mut str446 = String::new();
                                str446.push_str(".3f");
                                Val::Str(str446)
                            })?,
                        )?);
                        str441.push_str(" mm");
                        Val::Str(str441)
                    });
                    fun440.call(args438, kw439)?
                };
            }
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun462 = e.get("report")?;
        let mut args460 = Vec::new();
        let mut kw461 = Vec::new();
        fun462.call(args460, kw461)?
    };
    Ok(Val::None)
}
