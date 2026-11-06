#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("itertools", rt.import_module("itertools")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("collections")?;
    e.set("namedtuple", rt.member("collections", "namedtuple")?)?;
    let mod2 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
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
    e.set("_here", assigned3.clone())?;
    {
        let fun12 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args10 = Vec::new();
        let mut kw11 = Vec::new();
        args10.push(Val::Int(0i64));
        args10.push({
            let fun15 = e.get("str")?;
            let mut args13 = Vec::new();
            let mut kw14 = Vec::new();
            args13.push(binary(
                "truediv",
                {
                    let fun18 = e.get("next")?;
                    let mut args16 = Vec::new();
                    let mut kw17 = Vec::new();
                    args16.push({
                        let e = e.child();
                        let out19 = Val::list(vec![]);
                        for item20 in e.get("_here")?.attr("parents")?.iter()? {
                            e.set("p", item20)?;
                            if {
                                let v21 = e.get("p")?.attr("name")?;
                                let v22 = Val::Str("printed-parts".into());
                                Val::Bool(compare("eq", v21.clone(), v22.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                out19.attr("append")?.call(vec![e.get("p")?], vec![])?;
                            }
                        }
                        out19
                    });
                    fun18.call(args16, kw17)?
                },
                Val::Str("cadlib".into()),
            )?);
            fun15.call(args13, kw14)?
        });
        fun12.call(args10, kw11)?
    };
    {
        let fun25 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args23 = Vec::new();
        let mut kw24 = Vec::new();
        args23.push(Val::Int(0i64));
        args23.push({
            let fun28 = e.get("str")?;
            let mut args26 = Vec::new();
            let mut kw27 = Vec::new();
            args26.push(binary(
                "truediv",
                {
                    let fun31 = e.get("next")?;
                    let mut args29 = Vec::new();
                    let mut kw30 = Vec::new();
                    args29.push({
                        let e = e.child();
                        let out32 = Val::list(vec![]);
                        for item33 in e.get("_here")?.attr("parents")?.iter()? {
                            e.set("p", item33)?;
                            if {
                                let v34 = e.get("p")?.attr("name")?;
                                let v35 = Val::Str("hardware".into());
                                Val::Bool(compare("eq", v34.clone(), v35.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                out32.attr("append")?.call(vec![e.get("p")?], vec![])?;
                            }
                        }
                        out32
                    });
                    fun31.call(args29, kw30)?
                },
                Val::Str("scripts".into()),
            )?);
            fun28.call(args26, kw27)?
        });
        fun25.call(args23, kw24)?
    };
    {
        let fun38 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args36 = Vec::new();
        let mut kw37 = Vec::new();
        args36.push(Val::Int(0i64));
        args36.push({
            let fun41 = e.get("str")?;
            let mut args39 = Vec::new();
            let mut kw40 = Vec::new();
            args39.push(binary(
                "truediv",
                binary(
                    "truediv",
                    e.get("_here")?.attr("parent")?,
                    Val::Str("enclosure".into()),
                )?,
                Val::Str("enclosure".into()),
            )?);
            fun41.call(args39, kw40)?
        });
        fun38.call(args36, kw37)?
    };
    {
        let fun44 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args42 = Vec::new();
        let mut kw43 = Vec::new();
        args42.push(Val::Int(0i64));
        args42.push({
            let fun47 = e.get("str")?;
            let mut args45 = Vec::new();
            let mut kw46 = Vec::new();
            args45.push(binary(
                "truediv",
                e.get("_here")?.attr("parent")?,
                Val::Str("valve-seat".into()),
            )?);
            fun47.call(args45, kw46)?
        });
        fun44.call(args42, kw43)?
    };
    {
        let fun50 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args48 = Vec::new();
        let mut kw49 = Vec::new();
        args48.push(Val::Int(0i64));
        args48.push({
            let fun53 = e.get("str")?;
            let mut args51 = Vec::new();
            let mut kw52 = Vec::new();
            args51.push(binary(
                "truediv",
                binary(
                    "truediv",
                    binary(
                        "truediv",
                        e.get("_here")?.attr("parents")?.get(Val::Int(1i64))?,
                        Val::Str("reference".into()),
                    )?,
                    Val::Str("g-ganen-pump".into()),
                )?,
                Val::Str("installation".into()),
            )?);
            fun53.call(args51, kw52)?
        });
        fun50.call(args48, kw49)?
    };
    {
        let fun56 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args54 = Vec::new();
        let mut kw55 = Vec::new();
        args54.push(Val::Int(0i64));
        args54.push({
            let fun59 = e.get("str")?;
            let mut args57 = Vec::new();
            let mut kw58 = Vec::new();
            args57.push(binary(
                "truediv",
                e.get("_here")?.attr("parents")?.get(Val::Int(1i64))?,
                Val::Str("cold-core-layout".into()),
            )?);
            fun59.call(args57, kw58)?
        });
        fun56.call(args54, kw55)?
    };
    e.set("fits", rt.import_module("fits")?)?;
    e.set("_valve_seat", rt.import_module("valve_seat")?)?;
    e.set("_above_mounts", rt.import_module("_above_core_mounts")?)?;
    let mod60 = rt.import_module("_stated_bounds")?;
    e.set("bound", rt.member("_stated_bounds", "bound")?)?;
    e.set("state", rt.member("_stated_bounds", "state")?)?;
    e.set("manifold_rise", Val::Float(hsm_enclosure_interface::MANIFOLD_RISE))?;
    e.set("inner_limb_drop", Val::Float(hsm_enclosure_interface::INNER_LIMB_DROP))?;
    e.set("rear_plane_y", Val::Float(hsm_enclosure_interface::REAR_PLANE_Y))?;
    e.set("rear_seam_clear", Val::Float(hsm_enclosure_interface::REAR_SEAM_CLEAR))?;
    let mod62 = rt.import_module("_carbonator_stock")?;
    e.set(
        "carbonator_outer_radius",
        rt.member("_carbonator_stock", "carbonator_outer_radius")?,
    )?;
    e.set(
        "carbonator_height",
        rt.member("_carbonator_stock", "carbonator_height")?,
    )?;
    let mod63 = rt.import_module("_cold_core_data")?;
    e.set("_read", rt.member("_cold_core_data", "read")?)?;
    let assigned64 = {
        let e = e.child();
        let out65 = Val::dict(vec![]);
        for item66 in {
            let mut s = Vec::new();
            s.push(Val::Str("running".into()));
            s.push(Val::Str("slip".into()));
            s.push(Val::Str("m5_thread_pass_dia".into()));
            s.push(Val::Str("supported_surface".into()));
            Val::tuple(s)
        }
        .iter()?
        {
            e.set("name", item66)?;
            out65.set(e.get("name")?, {
                let fun69 = e.get("getattr")?;
                let mut args67 = Vec::new();
                let mut kw68 = Vec::new();
                args67.push(e.get("fits")?);
                args67.push(e.get("name")?);
                fun69.call(args67, kw68)?
            })?;
        }
        out65
    };
    e.set("_interface_fits", assigned64.clone())?;
    let assigned70 = {
        let fun73 = e.get("_read")?;
        let mut args71 = Vec::new();
        let mut kw72 = Vec::new();
        args71.push(Val::Str("interface-base".into()));
        kw72.push(("fits".into(), e.get("_interface_fits")?));
        fun73.call(args71, kw72)?
    };
    e.set("_base_recipe", assigned70.clone())?;
    let assigned74 = {
        let fun77 = e.get("_base_recipe")?.attr("pop")?;
        let mut args75 = Vec::new();
        let mut kw76 = Vec::new();
        args75.push(Val::Str("_states".into()));
        fun77.call(args75, kw76)?
    };
    e.set("_base_states", assigned74.clone())?;
    {
        let fun80 = {
            let fun83 = e.get("globals")?;
            let mut args81 = Vec::new();
            let mut kw82 = Vec::new();
            fun83.call(args81, kw82)?
        }
        .attr("update")?;
        let mut args78 = Vec::new();
        let mut kw79 = Vec::new();
        args78.push(e.get("_base_recipe")?);
        fun80.call(args78, kw79)?
    };
    for item84 in {
        let mut s = Vec::new();
        s.push(Val::Str("reservoir_fill_port".into()));
        s.push(Val::Str("reservoir_draw_port".into()));
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("_name", item84)?;
        let assigned85 = {
            let e = e.child();
            let out86 = Val::dict(vec![]);
            for item87 in {
                let fun90 = {
                    let fun93 = e.get("globals")?;
                    let mut args91 = Vec::new();
                    let mut kw92 = Vec::new();
                    fun93.call(args91, kw92)?
                }
                .get(e.get("_name")?)?
                .attr("items")?;
                let mut args88 = Vec::new();
                let mut kw89 = Vec::new();
                fun90.call(args88, kw89)?
            }
            .iter()?
            {
                let unpack94 = unpack(item87, 2)?;
                e.set("side", unpack94[0].clone())?;
                e.set("xy", unpack94[1].clone())?;
                out86.set(
                    {
                        let fun97 = e.get("int")?;
                        let mut args95 = Vec::new();
                        let mut kw96 = Vec::new();
                        args95.push(e.get("side")?);
                        fun97.call(args95, kw96)?
                    },
                    {
                        let fun100 = e.get("tuple")?;
                        let mut args98 = Vec::new();
                        let mut kw99 = Vec::new();
                        args98.push(e.get("xy")?);
                        fun100.call(args98, kw99)?
                    },
                )?;
            }
            out86
        };
        {
            let fun103 = e.get("globals")?;
            let mut args101 = Vec::new();
            let mut kw102 = Vec::new();
            fun103.call(args101, kw102)?
        }
        .set(e.get("_name")?, assigned85.clone())?;
    }
    for item104 in {
        let mut s = Vec::new();
        s.push(Val::Str("reservoir_fill_sides".into()));
        s.push(Val::Str("top_lid_pour_xy".into()));
        s.push(Val::Str("carbonator_sensor_axis".into()));
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("_name", item104)?;
        let assigned105 = {
            let fun108 = e.get("tuple")?;
            let mut args106 = Vec::new();
            let mut kw107 = Vec::new();
            args106.push(
                {
                    let fun111 = e.get("globals")?;
                    let mut args109 = Vec::new();
                    let mut kw110 = Vec::new();
                    fun111.call(args109, kw110)?
                }
                .get(e.get("_name")?)?,
            );
            fun108.call(args106, kw107)?
        };
        {
            let fun114 = e.get("globals")?;
            let mut args112 = Vec::new();
            let mut kw113 = Vec::new();
            fun114.call(args112, kw113)?
        }
        .set(e.get("_name")?, assigned105.clone())?;
    }
    let assigned115 = {
        let fun118 = e.get("tuple")?;
        let mut args116 = Vec::new();
        let mut kw117 = Vec::new();
        args116.push({
            let e = e.child();
            let out119 = Val::list(vec![]);
            for item120 in e.get("bottom_pour_positions")?.iter()? {
                e.set("xy", item120)?;
                out119.attr("append")?.call(
                    vec![{
                        let fun123 = e.get("tuple")?;
                        let mut args121 = Vec::new();
                        let mut kw122 = Vec::new();
                        args121.push(e.get("xy")?);
                        fun123.call(args121, kw122)?
                    }],
                    vec![],
                )?;
            }
            out119
        });
        fun118.call(args116, kw117)?
    };
    e.set("bottom_pour_positions", assigned115.clone())?;
    for item124 in {
        let mut s = Vec::new();
        s.push(Val::Str("attachment_stations".into()));
        s.push(Val::Str("lid_attachment_stations".into()));
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("_name", item124)?;
        let assigned125 = {
            let fun128 = e.get("tuple")?;
            let mut args126 = Vec::new();
            let mut kw127 = Vec::new();
            args126.push({
                let e = e.child();
                let out129 = Val::list(vec![]);
                for item130 in {
                    let fun133 = e.get("globals")?;
                    let mut args131 = Vec::new();
                    let mut kw132 = Vec::new();
                    fun133.call(args131, kw132)?
                }
                .get(e.get("_name")?)?
                .iter()?
                {
                    let unpack134 = unpack(item130, 2)?;
                    e.set("xy", unpack134[0].clone())?;
                    e.set("wall", unpack134[1].clone())?;
                    out129.attr("append")?.call(
                        vec![{
                            let mut s = Vec::new();
                            s.push({
                                let fun137 = e.get("tuple")?;
                                let mut args135 = Vec::new();
                                let mut kw136 = Vec::new();
                                args135.push(e.get("xy")?);
                                fun137.call(args135, kw136)?
                            });
                            s.push(e.get("wall")?);
                            Val::tuple(s)
                        }],
                        vec![],
                    )?;
                }
                out129
            });
            fun128.call(args126, kw127)?
        };
        {
            let fun140 = e.get("globals")?;
            let mut args138 = Vec::new();
            let mut kw139 = Vec::new();
            fun140.call(args138, kw139)?
        }
        .set(e.get("_name")?, assigned125.clone())?;
    }
    for item141 in {
        let mut s = Vec::new();
        s.push(Val::Str("attachment_xy_positions".into()));
        s.push(Val::Str("lid_attachment_xy_positions".into()));
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("_name", item141)?;
        let assigned142 = {
            let e = e.child();
            let out143 = Val::list(vec![]);
            for item144 in {
                let fun147 = e.get("globals")?;
                let mut args145 = Vec::new();
                let mut kw146 = Vec::new();
                fun147.call(args145, kw146)?
            }
            .get(e.get("_name")?)?
            .iter()?
            {
                e.set("xy", item144)?;
                out143.attr("append")?.call(
                    vec![{
                        let fun150 = e.get("tuple")?;
                        let mut args148 = Vec::new();
                        let mut kw149 = Vec::new();
                        args148.push(e.get("xy")?);
                        fun150.call(args148, kw149)?
                    }],
                    vec![],
                )?;
            }
            out143
        };
        {
            let fun153 = e.get("globals")?;
            let mut args151 = Vec::new();
            let mut kw152 = Vec::new();
            fun153.call(args151, kw152)?
        }
        .set(e.get("_name")?, assigned142.clone())?;
    }
    for item154 in e.get("_base_states")?.iter()? {
        e.set("_row", item154)?;
        {
            let fun157 = e.get("state")?;
            let mut args155 = Vec::new();
            let mut kw156 = Vec::new();
            args155.extend(e.get("_row")?.iter()?);
            fun157.call(args155, kw156)?
        };
    }
    // reservoir_fill_conduit_xy
    e.set("reservoir_fill_conduit_xy", {
        let params = vec![("side".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun160 = e.get("tuple")?;
                let mut args158 = Vec::new();
                let mut kw159 = Vec::new();
                args158.push({
                    let fun163 = e.get("_read")?;
                    let mut args161 = Vec::new();
                    let mut kw162 = Vec::new();
                    args161.push(Val::Str("interface-reservoir-conduit".into()));
                    kw162.push(("kind".into(), Val::Str("fill".into())));
                    kw162.push(("side".into(), e.get("side")?));
                    fun163.call(args161, kw162)?
                });
                fun160.call(args158, kw159)?
            });
            Ok(Val::None)
        })
    })?;
    // reservoir_draw_conduit_xy
    e.set("reservoir_draw_conduit_xy", {
        let params = vec![("side".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun166 = e.get("tuple")?;
                let mut args164 = Vec::new();
                let mut kw165 = Vec::new();
                args164.push({
                    let fun169 = e.get("_read")?;
                    let mut args167 = Vec::new();
                    let mut kw168 = Vec::new();
                    args167.push(Val::Str("interface-reservoir-conduit".into()));
                    kw168.push(("kind".into(), Val::Str("draw".into())));
                    kw168.push(("side".into(), e.get("side")?));
                    fun169.call(args167, kw168)?
                });
                fun166.call(args164, kw165)?
            });
            Ok(Val::None)
        })
    })?;
    let assigned170 = {
        let fun173 = e.get("namedtuple")?;
        let mut args171 = Vec::new();
        let mut kw172 = Vec::new();
        args171.push(Val::Str("DeckMount".into()));
        args171.push(Val::Str("points standoff seat screw seat_min".into()));
        fun173.call(args171, kw172)?
    };
    e.set("DeckMount", assigned170.clone())?;
    let assigned174 = {
        let e = e.child();
        let out175 = Val::dict(vec![]);
        for item176 in {
            let fun179 = {
                let fun182 = e.get("_above_mounts")?.attr("deck_mounts")?;
                let mut args180 = Vec::new();
                let mut kw181 = Vec::new();
                fun182.call(args180, kw181)?
            }
            .attr("items")?;
            let mut args177 = Vec::new();
            let mut kw178 = Vec::new();
            fun179.call(args177, kw178)?
        }
        .iter()?
        {
            let unpack183 = unpack(item176, 2)?;
            e.set("name", unpack183[0].clone())?;
            e.set("row", unpack183[1].clone())?;
            out175.set(e.get("name")?, {
                let fun186 = e.get("DeckMount")?;
                let mut args184 = Vec::new();
                let mut kw185 = Vec::new();
                args184.extend(e.get("row")?.iter()?);
                fun186.call(args184, kw185)?
            })?;
        }
        out175
    };
    e.set("deck_mounts", assigned174.clone())?;
    // deck_mount_xy
    e.set("deck_mount_xy", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun189 = e.get("tuple")?;
                let mut args187 = Vec::new();
                let mut kw188 = Vec::new();
                args187.push({
                    let fun192 = e.get("sorted")?;
                    let mut args190 = Vec::new();
                    let mut kw191 = Vec::new();
                    args190.push({
                        let fun195 = e.get("set")?;
                        let mut args193 = Vec::new();
                        let mut kw194 = Vec::new();
                        args193.push(e.get("deck_mounts")?.get(e.get("name")?)?.attr("points")?);
                        fun195.call(args193, kw194)?
                    });
                    fun192.call(args190, kw191)?
                });
                fun189.call(args187, kw188)?
            });
            Ok(Val::None)
        })
    })?;
    // deck_mount_standoff
    e.set("deck_mount_standoff", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e
                .get("deck_mounts")?
                .get(e.get("name")?)?
                .attr("standoff")?);
            Ok(Val::None)
        })
    })?;
    // deck_mount_proud
    e.set("deck_mount_proud", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun198 = e.get("max")?;
                let mut args196 = Vec::new();
                let mut kw197 = Vec::new();
                args196.push({
                    let e = e.child();
                    let out199 = Val::list(vec![]);
                    for item200 in e.get("deck_mounts")?.iter()? {
                        e.set("name", item200)?;
                        out199.attr("append")?.call(
                            vec![{
                                let fun203 = e.get("deck_mount_standoff")?;
                                let mut args201 = Vec::new();
                                let mut kw202 = Vec::new();
                                args201.push(e.get("name")?);
                                fun203.call(args201, kw202)?
                            }],
                            vec![],
                        )?;
                    }
                    out199
                });
                kw197.push(("default".into(), Val::Float(0.0f64)));
                fun198.call(args196, kw197)?
            });
            Ok(Val::None)
        })
    })?;
    // deck_mount_reach
    e.set("deck_mount_reach", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned204 = e.get("deck_mounts")?.get(e.get("name")?)?;
            e.set("m", assigned204.clone())?;
            let assigned205 = e.get("m")?.attr("seat")?;
            e.set("over", assigned205.clone())?;
            if {
                let v206 = e.get("m")?.attr("standoff")?;
                let v207 = Val::Float(0.0f64);
                Val::Bool(compare("eq", v206.clone(), v207.clone())?.truthy()?)
            }
            .truthy()?
            {
                e.set(
                    "over",
                    binary(
                        "add",
                        e.get("over")?,
                        binary(
                            "add",
                            e.get("foam_cap_lid_height")?,
                            e.get("cap_lid_clearance")?,
                        )?,
                    )?,
                )?;
            }
            return Ok(binary("sub", e.get("m")?.attr("screw")?, e.get("over")?)?);
            Ok(Val::None)
        })
    })?;
    let assigned208 = {
        let fun211 = e.get("max")?;
        let mut args209 = Vec::new();
        let mut kw210 = Vec::new();
        args209.push(binary(
            "add",
            e.get("deck_mount_insert_length")?,
            e.get("deck_mount_bore_relief")?,
        )?);
        args209.push(binary(
            "add",
            {
                let fun214 = e.get("max")?;
                let mut args212 = Vec::new();
                let mut kw213 = Vec::new();
                args212.push({
                    let e = e.child();
                    let out215 = Val::list(vec![]);
                    for item216 in {
                        let fun219 = e.get("deck_mounts")?.attr("values")?;
                        let mut args217 = Vec::new();
                        let mut kw218 = Vec::new();
                        fun219.call(args217, kw218)?
                    }
                    .iter()?
                    {
                        e.set("m", item216)?;
                        out215.attr("append")?.call(
                            vec![binary(
                                "sub",
                                binary(
                                    "sub",
                                    e.get("m")?.attr("screw")?,
                                    e.get("m")?.attr("seat_min")?,
                                )?,
                                if {
                                    let v220 = e.get("m")?.attr("standoff")?;
                                    let v221 = Val::Float(0.0f64);
                                    Val::Bool(compare("eq", v220.clone(), v221.clone())?.truthy()?)
                                }
                                .truthy()?
                                {
                                    binary(
                                        "add",
                                        e.get("foam_cap_lid_height")?,
                                        e.get("cap_lid_clearance")?,
                                    )?
                                } else {
                                    Val::Float(0.0f64)
                                },
                            )?],
                            vec![],
                        )?;
                    }
                    out215
                });
                kw213.push(("default".into(), Val::Float(0.0f64)));
                fun214.call(args212, kw213)?
            },
            e.get("deck_mount_bore_relief")?,
        )?);
        fun211.call(args209, kw210)?
    };
    e.set("deck_mount_bore_depth", assigned208.clone())?;
    let assigned222 = {
        let fun225 = e.get("bound")?;
        let mut args223 = Vec::new();
        let mut kw224 = Vec::new();
        args223.push(Val::Str("deck-mount-reach".into()));
        args223.push(Val::Str(
            "Every deck mount's screw reaches the whole of its insert".into(),
        ));
        args223.push({
            let mut str226 = String::new();
            str226.push_str(&format(
                &e.get("deck_mount_insert_length")?,
                &val_string({
                    let mut str227 = String::new();
                    str227.push_str("g");
                    Val::Str(str227)
                })?,
            )?);
            str226.push_str(" mm into the column");
            Val::Str(str226)
        });
        fun225.call(args223, kw224)?
    };
    e.set("_mount_reach", assigned222.clone())?;
    for item228 in e.get("deck_mounts")?.iter()? {
        e.set("_name", item228)?;
        {
            let fun231 = e.get("_mount_reach")?;
            let mut args229 = Vec::new();
            let mut kw230 = Vec::new();
            args229.push({
                let v235 = {
                    let fun234 = e.get("deck_mount_reach")?;
                    let mut args232 = Vec::new();
                    let mut kw233 = Vec::new();
                    args232.push(e.get("_name")?);
                    fun234.call(args232, kw233)?
                };
                let v236 = e.get("deck_mount_insert_length")?;
                Val::Bool(compare("ge", v235.clone(), v236.clone())?.truthy()?)
            });
            args229.push({
                let mut str237 = String::new();
                str237.push_str("deck mount ");
                str237.push_str(&format(&e.get("_name")?, &String::new())?);
                str237.push_str(": an M3 × ");
                str237.push_str(&format(
                    &e.get("deck_mounts")?.get(e.get("_name")?)?.attr("screw")?,
                    &val_string({
                        let mut str238 = String::new();
                        str238.push_str("g");
                        Val::Str(str238)
                    })?,
                )?);
                str237.push_str(" through ");
                str237.push_str(&format(
                    &e.get("deck_mounts")?.get(e.get("_name")?)?.attr("seat")?,
                    &val_string({
                        let mut str239 = String::new();
                        str239.push_str("g");
                        Val::Str(str239)
                    })?,
                )?);
                str237.push_str(" mm of seat reaches ");
                str237.push_str(&format(
                    &{
                        let fun242 = e.get("deck_mount_reach")?;
                        let mut args240 = Vec::new();
                        let mut kw241 = Vec::new();
                        args240.push(e.get("_name")?);
                        fun242.call(args240, kw241)?
                    },
                    &val_string({
                        let mut str243 = String::new();
                        str243.push_str("g");
                        Val::Str(str243)
                    })?,
                )?);
                str237.push_str(" mm into the column, short of its ");
                str237.push_str(&format(
                    &e.get("deck_mount_insert_length")?,
                    &val_string({
                        let mut str244 = String::new();
                        str244.push_str("g");
                        Val::Str(str244)
                    })?,
                )?);
                str237.push_str(" mm insert");
                Val::Str(str237)
            });
            fun231.call(args229, kw230)?
        };
    }
    // deck_lid_hole_radius
    e.set("deck_lid_hole_radius", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v248 = {
                    let fun247 = e.get("deck_mount_standoff")?;
                    let mut args245 = Vec::new();
                    let mut kw246 = Vec::new();
                    args245.push(e.get("name")?);
                    fun247.call(args245, kw246)?
                };
                let v249 = Val::Float(0.0f64);
                Val::Bool(compare("eq", v248.clone(), v249.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("screw_clearance_radius")?);
            }
            return Ok(binary(
                "add",
                e.get("deck_mount_boss_radius")?,
                e.get("deck_mount_lid_slip")?,
            )?);
            Ok(Val::None)
        })
    })?;
    let assigned250 = {
        let fun253 = e.get("namedtuple")?;
        let mut args251 = Vec::new();
        let mut kw252 = Vec::new();
        args251.push(Val::Str("Cradle".into()));
        args251.push(Val::Str("centre yaw seat".into()));
        fun253.call(args251, kw252)?
    };
    e.set("Cradle", assigned250.clone())?;
    let assigned254 = {
        let d = Val::dict(vec![]);
        d
    };
    e.set("cap_cradles", assigned254.clone())?;
    let assigned255 = e.get("_valve_seat")?.attr("corner_inset_x")?;
    e.set("cap_cradle_corner_inset_x", assigned255.clone())?;
    let assigned256 = e.get("_valve_seat")?.attr("corner_inset_y")?;
    e.set("cap_cradle_corner_inset_y", assigned256.clone())?;
    let assigned257 = e.get("_valve_seat")?.attr("socket_radius")?;
    e.set("cap_cradle_socket_radius", assigned257.clone())?;
    let assigned258 = e.get("_valve_seat")?.attr("wall")?;
    e.set("cap_cradle_wall", assigned258.clone())?;
    let assigned259 = e.get("_valve_seat")?.attr("boss_radius")?;
    e.set("cap_cradle_boss_radius", assigned259.clone())?;
    let assigned260 = e.get("_valve_seat")?.attr("seat_half_x")?;
    e.set("cap_cradle_half_x", assigned260.clone())?;
    let assigned261 = e.get("_valve_seat")?.attr("seat_half_y")?;
    e.set("cap_cradle_half_y", assigned261.clone())?;
    let assigned262 = e.get("_valve_seat")?.attr("seat_corner_radius")?;
    e.set("cap_cradle_corner_radius", assigned262.clone())?;
    let assigned263 = Val::Float(hsm_cold_core_interface::CAP_CRADLE_ROOM_GAP);
    e.set("cap_cradle_room_gap", assigned263.clone())?;
    // cap_cradle_xy
    e.set("cap_cradle_xy", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned264 = e.get("cap_cradles")?.get(e.get("name")?)?.attr("centre")?;
            let unpack265 = unpack(assigned264.clone(), 2)?;
            e.set("cx", unpack265[0].clone())?;
            e.set("cy", unpack265[1].clone())?;
            let assigned266 = {
                let fun269 = e.get("math")?.attr("radians")?;
                let mut args267 = Vec::new();
                let mut kw268 = Vec::new();
                args267.push(binary(
                    "add",
                    e.get("cap_cradles")?.get(e.get("name")?)?.attr("yaw")?,
                    Val::Float(90.0f64),
                )?);
                fun269.call(args267, kw268)?
            };
            e.set("th", assigned266.clone())?;
            let assigned270 = {
                let mut s = Vec::new();
                s.push({
                    let fun273 = e.get("math")?.attr("cos")?;
                    let mut args271 = Vec::new();
                    let mut kw272 = Vec::new();
                    args271.push(e.get("th")?);
                    fun273.call(args271, kw272)?
                });
                s.push({
                    let fun276 = e.get("math")?.attr("sin")?;
                    let mut args274 = Vec::new();
                    let mut kw275 = Vec::new();
                    args274.push(e.get("th")?);
                    fun276.call(args274, kw275)?
                });
                Val::tuple(s)
            };
            let unpack277 = unpack(assigned270.clone(), 2)?;
            e.set("c", unpack277[0].clone())?;
            e.set("s", unpack277[1].clone())?;
            return Ok({
                let fun280 = e.get("tuple")?;
                let mut args278 = Vec::new();
                let mut kw279 = Vec::new();
                args278.push({
                    let e = e.child();
                    let out281 = Val::list(vec![]);
                    for item282 in {
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Int(1i64))?);
                        s.push(Val::Int(1i64));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("sx", item282)?;
                        for item283 in {
                            let mut s = Vec::new();
                            s.push(unary("neg", Val::Int(1i64))?);
                            s.push(Val::Int(1i64));
                            Val::tuple(s)
                        }
                        .iter()?
                        {
                            e.set("sy", item283)?;
                            out281.attr("append")?.call(
                                vec![{
                                    let mut s = Vec::new();
                                    s.push(binary(
                                        "sub",
                                        binary(
                                            "add",
                                            e.get("cx")?,
                                            binary(
                                                "mul",
                                                binary("mul", e.get("c")?, e.get("sx")?)?,
                                                e.get("cap_cradle_corner_inset_x")?,
                                            )?,
                                        )?,
                                        binary(
                                            "mul",
                                            binary("mul", e.get("s")?, e.get("sy")?)?,
                                            e.get("cap_cradle_corner_inset_y")?,
                                        )?,
                                    )?);
                                    s.push(binary(
                                        "add",
                                        binary(
                                            "add",
                                            e.get("cy")?,
                                            binary(
                                                "mul",
                                                binary("mul", e.get("s")?, e.get("sx")?)?,
                                                e.get("cap_cradle_corner_inset_x")?,
                                            )?,
                                        )?,
                                        binary(
                                            "mul",
                                            binary("mul", e.get("c")?, e.get("sy")?)?,
                                            e.get("cap_cradle_corner_inset_y")?,
                                        )?,
                                    )?);
                                    Val::tuple(s)
                                }],
                                vec![],
                            )?;
                        }
                    }
                    out281
                });
                fun280.call(args278, kw279)?
            });
            Ok(Val::None)
        })
    })?;
    // cap_cradle_half_extents
    e.set("cap_cradle_half_extents", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned284 = {
                let fun287 = e.get("math")?.attr("radians")?;
                let mut args285 = Vec::new();
                let mut kw286 = Vec::new();
                args285.push(binary(
                    "add",
                    e.get("cap_cradles")?.get(e.get("name")?)?.attr("yaw")?,
                    Val::Float(90.0f64),
                )?);
                fun287.call(args285, kw286)?
            };
            e.set("th", assigned284.clone())?;
            let assigned288 = {
                let mut s = Vec::new();
                s.push({
                    let fun291 = e.get("abs")?;
                    let mut args289 = Vec::new();
                    let mut kw290 = Vec::new();
                    args289.push({
                        let fun294 = e.get("math")?.attr("cos")?;
                        let mut args292 = Vec::new();
                        let mut kw293 = Vec::new();
                        args292.push(e.get("th")?);
                        fun294.call(args292, kw293)?
                    });
                    fun291.call(args289, kw290)?
                });
                s.push({
                    let fun297 = e.get("abs")?;
                    let mut args295 = Vec::new();
                    let mut kw296 = Vec::new();
                    args295.push({
                        let fun300 = e.get("math")?.attr("sin")?;
                        let mut args298 = Vec::new();
                        let mut kw299 = Vec::new();
                        args298.push(e.get("th")?);
                        fun300.call(args298, kw299)?
                    });
                    fun297.call(args295, kw296)?
                });
                Val::tuple(s)
            };
            let unpack301 = unpack(assigned288.clone(), 2)?;
            e.set("c", unpack301[0].clone())?;
            e.set("s", unpack301[1].clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(binary(
                    "add",
                    binary("mul", e.get("c")?, e.get("cap_cradle_half_x")?)?,
                    binary("mul", e.get("s")?, e.get("cap_cradle_half_y")?)?,
                )?);
                s.push(binary(
                    "add",
                    binary("mul", e.get("s")?, e.get("cap_cradle_half_x")?)?,
                    binary("mul", e.get("c")?, e.get("cap_cradle_half_y")?)?,
                )?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // cap_cradle_circle_gap
    e.set("cap_cradle_circle_gap", {
        let params = vec![
            ("name".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("radius".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned302 = e.get("cap_cradles")?.get(e.get("name")?)?;
            let unpack303 = unpack(assigned302.clone(), 3)?;
            let unpack304 = unpack(unpack303[0].clone(), 2)?;
            e.set("cx", unpack304[0].clone())?;
            e.set("cy", unpack304[1].clone())?;
            e.set("yaw", unpack303[1].clone())?;
            e.set("_seat", unpack303[2].clone())?;
            let assigned305 = {
                let fun308 = e.get("math")?.attr("radians")?;
                let mut args306 = Vec::new();
                let mut kw307 = Vec::new();
                args306.push(binary("add", e.get("yaw")?, Val::Float(90.0f64))?);
                fun308.call(args306, kw307)?
            };
            e.set("th", assigned305.clone())?;
            let assigned309 = {
                let mut s = Vec::new();
                s.push(binary("sub", e.get("x")?, e.get("cx")?)?);
                s.push(binary("sub", e.get("y")?, e.get("cy")?)?);
                Val::tuple(s)
            };
            let unpack310 = unpack(assigned309.clone(), 2)?;
            e.set("dx", unpack310[0].clone())?;
            e.set("dy", unpack310[1].clone())?;
            let assigned311 = {
                let fun314 = e.get("abs")?;
                let mut args312 = Vec::new();
                let mut kw313 = Vec::new();
                args312.push(binary(
                    "add",
                    binary(
                        "mul",
                        {
                            let fun317 = e.get("math")?.attr("cos")?;
                            let mut args315 = Vec::new();
                            let mut kw316 = Vec::new();
                            args315.push(e.get("th")?);
                            fun317.call(args315, kw316)?
                        },
                        e.get("dx")?,
                    )?,
                    binary(
                        "mul",
                        {
                            let fun320 = e.get("math")?.attr("sin")?;
                            let mut args318 = Vec::new();
                            let mut kw319 = Vec::new();
                            args318.push(e.get("th")?);
                            fun320.call(args318, kw319)?
                        },
                        e.get("dy")?,
                    )?,
                )?);
                fun314.call(args312, kw313)?
            };
            e.set("px", assigned311.clone())?;
            let assigned321 = {
                let fun324 = e.get("abs")?;
                let mut args322 = Vec::new();
                let mut kw323 = Vec::new();
                args322.push(binary(
                    "add",
                    binary(
                        "mul",
                        unary("neg", {
                            let fun327 = e.get("math")?.attr("sin")?;
                            let mut args325 = Vec::new();
                            let mut kw326 = Vec::new();
                            args325.push(e.get("th")?);
                            fun327.call(args325, kw326)?
                        })?,
                        e.get("dx")?,
                    )?,
                    binary(
                        "mul",
                        {
                            let fun330 = e.get("math")?.attr("cos")?;
                            let mut args328 = Vec::new();
                            let mut kw329 = Vec::new();
                            args328.push(e.get("th")?);
                            fun330.call(args328, kw329)?
                        },
                        e.get("dy")?,
                    )?,
                )?);
                fun324.call(args322, kw323)?
            };
            e.set("py", assigned321.clone())?;
            let assigned331 = binary(
                "sub",
                e.get("px")?,
                binary(
                    "sub",
                    e.get("cap_cradle_half_x")?,
                    e.get("cap_cradle_corner_radius")?,
                )?,
            )?;
            e.set("qx", assigned331.clone())?;
            let assigned332 = binary(
                "sub",
                e.get("py")?,
                binary(
                    "sub",
                    e.get("cap_cradle_half_y")?,
                    e.get("cap_cradle_corner_radius")?,
                )?,
            )?;
            e.set("qy", assigned332.clone())?;
            return Ok(binary(
                "sub",
                binary(
                    "sub",
                    binary(
                        "add",
                        {
                            let fun335 = e.get("math")?.attr("hypot")?;
                            let mut args333 = Vec::new();
                            let mut kw334 = Vec::new();
                            args333.push({
                                let fun338 = e.get("max")?;
                                let mut args336 = Vec::new();
                                let mut kw337 = Vec::new();
                                args336.push(e.get("qx")?);
                                args336.push(Val::Float(0.0f64));
                                fun338.call(args336, kw337)?
                            });
                            args333.push({
                                let fun341 = e.get("max")?;
                                let mut args339 = Vec::new();
                                let mut kw340 = Vec::new();
                                args339.push(e.get("qy")?);
                                args339.push(Val::Float(0.0f64));
                                fun341.call(args339, kw340)?
                            });
                            fun335.call(args333, kw334)?
                        },
                        {
                            let fun344 = e.get("min")?;
                            let mut args342 = Vec::new();
                            let mut kw343 = Vec::new();
                            args342.push({
                                let fun347 = e.get("max")?;
                                let mut args345 = Vec::new();
                                let mut kw346 = Vec::new();
                                args345.push(e.get("qx")?);
                                args345.push(e.get("qy")?);
                                fun347.call(args345, kw346)?
                            });
                            args342.push(Val::Float(0.0f64));
                            fun344.call(args342, kw343)?
                        },
                    )?,
                    e.get("cap_cradle_corner_radius")?,
                )?,
                e.get("radius")?,
            )?);
            Ok(Val::None)
        })
    })?;
    // cap_cradle_rectangle_gap
    e.set("cap_cradle_rectangle_gap", {
        let params = vec![
            ("name".into(), None, false),
            ("x0".into(), None, false),
            ("x1".into(), None, false),
            ("y0".into(), None, false),
            ("y1".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned348 = e.get("cap_cradles")?.get(e.get("name")?)?;
            let unpack349 = unpack(assigned348.clone(), 3)?;
            let unpack350 = unpack(unpack349[0].clone(), 2)?;
            e.set("cx", unpack350[0].clone())?;
            e.set("cy", unpack350[1].clone())?;
            e.set("yaw", unpack349[1].clone())?;
            e.set("_seat", unpack349[2].clone())?;
            if !{
                let fun353 = e.get("math")?.attr("isclose")?;
                let mut args351 = Vec::new();
                let mut kw352 = Vec::new();
                args351.push(binary("mod", e.get("yaw")?, Val::Float(90.0f64))?);
                args351.push(Val::Float(0.0f64));
                fun353.call(args351, kw352)?
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string(Val::Str(
                        "plinth rectangle reading needs an axial station".into()
                    ))?
                );
            }
            let assigned354 = {
                let fun357 = e.get("cap_cradle_half_extents")?;
                let mut args355 = Vec::new();
                let mut kw356 = Vec::new();
                args355.push(e.get("name")?);
                fun357.call(args355, kw356)?
            };
            let unpack358 = unpack(assigned354.clone(), 2)?;
            e.set("hx", unpack358[0].clone())?;
            e.set("hy", unpack358[1].clone())?;
            let assigned359 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("hx")?,
                    e.get("cap_cradle_corner_radius")?,
                )?);
                s.push(binary(
                    "sub",
                    e.get("hy")?,
                    e.get("cap_cradle_corner_radius")?,
                )?);
                Val::tuple(s)
            };
            let unpack360 = unpack(assigned359.clone(), 2)?;
            e.set("core_x", unpack360[0].clone())?;
            e.set("core_y", unpack360[1].clone())?;
            let assigned361 = {
                let fun364 = e.get("max")?;
                let mut args362 = Vec::new();
                let mut kw363 = Vec::new();
                args362.push(binary(
                    "sub",
                    e.get("x0")?,
                    binary("add", e.get("cx")?, e.get("core_x")?)?,
                )?);
                args362.push(binary(
                    "sub",
                    binary("sub", e.get("cx")?, e.get("core_x")?)?,
                    e.get("x1")?,
                )?);
                args362.push(Val::Float(0.0f64));
                fun364.call(args362, kw363)?
            };
            e.set("dx", assigned361.clone())?;
            let assigned365 = {
                let fun368 = e.get("max")?;
                let mut args366 = Vec::new();
                let mut kw367 = Vec::new();
                args366.push(binary(
                    "sub",
                    e.get("y0")?,
                    binary("add", e.get("cy")?, e.get("core_y")?)?,
                )?);
                args366.push(binary(
                    "sub",
                    binary("sub", e.get("cy")?, e.get("core_y")?)?,
                    e.get("y1")?,
                )?);
                args366.push(Val::Float(0.0f64));
                fun368.call(args366, kw367)?
            };
            e.set("dy", assigned365.clone())?;
            return Ok(binary(
                "sub",
                {
                    let fun371 = e.get("math")?.attr("hypot")?;
                    let mut args369 = Vec::new();
                    let mut kw370 = Vec::new();
                    args369.push(e.get("dx")?);
                    args369.push(e.get("dy")?);
                    fun371.call(args369, kw370)?
                },
                e.get("cap_cradle_corner_radius")?,
            )?);
            Ok(Val::None)
        })
    })?;
    // cap_cradle_room
    e.set("cap_cradle_room", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned372 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("room", assigned372.clone())?;
            for item373 in {
                let fun387 = e.get("cap_conduits")?.attr("items")?;
                let mut args385 = Vec::new();
                let mut kw386 = Vec::new();
                fun387.call(args385, kw386)?
            }
            .iter()?
            {
                let unpack388 = unpack(item373, 2)?;
                e.set("cname", unpack388[0].clone())?;
                let unpack389 = unpack(unpack388[1].clone(), 2)?;
                e.set("x", unpack389[0].clone())?;
                e.set("y", unpack389[1].clone())?;
                let assigned374 = {
                    let fun377 = e.get("cap_cradle_circle_gap")?;
                    let mut args375 = Vec::new();
                    let mut kw376 = Vec::new();
                    args375.push(e.get("name")?);
                    args375.push(e.get("x")?);
                    args375.push(e.get("y")?);
                    args375.push(e.get("cap_conduit_entry_relief_radius")?);
                    fun377.call(args375, kw376)?
                };
                e.set("gap", assigned374.clone())?;
                {
                    let fun380 = e.get("room")?.attr("append")?;
                    let mut args378 = Vec::new();
                    let mut kw379 = Vec::new();
                    args378.push({
                        let mut s = Vec::new();
                        s.push({
                            let fun383 = e.get("max")?;
                            let mut args381 = Vec::new();
                            let mut kw382 = Vec::new();
                            args381.push(e.get("gap")?);
                            args381.push(e.get("cap_cradle_room_gap")?);
                            fun383.call(args381, kw382)?
                        });
                        s.push({
                            let mut str384 = String::new();
                            str384.push_str("the ");
                            str384.push_str(&format(&e.get("cname")?, &String::new())?);
                            str384.push_str(" conduit passage");
                            Val::Str(str384)
                        });
                        Val::tuple(s)
                    });
                    fun380.call(args378, kw379)?
                };
            }
            for item390 in e.get("attachment_xy_positions")?.iter()? {
                let unpack397 = unpack(item390, 2)?;
                e.set("x", unpack397[0].clone())?;
                e.set("y", unpack397[1].clone())?;
                {
                    let fun393 = e.get("room")?.attr("append")?;
                    let mut args391 = Vec::new();
                    let mut kw392 = Vec::new();
                    args391.push({
                        let mut s = Vec::new();
                        s.push({
                            let fun396 = e.get("cap_cradle_circle_gap")?;
                            let mut args394 = Vec::new();
                            let mut kw395 = Vec::new();
                            args394.push(e.get("name")?);
                            args394.push(e.get("x")?);
                            args394.push(e.get("y")?);
                            args394.push(e.get("head_cbore_radius")?);
                            fun396.call(args394, kw395)?
                        });
                        s.push(Val::Str("a clamp screw's counterbore".into()));
                        Val::tuple(s)
                    });
                    fun393.call(args391, kw392)?
                };
            }
            for item398 in e.get("deck_mounts")?.iter()? {
                e.set("dname", item398)?;
                for item399 in {
                    let fun412 = e.get("deck_mount_xy")?;
                    let mut args410 = Vec::new();
                    let mut kw411 = Vec::new();
                    args410.push(e.get("dname")?);
                    fun412.call(args410, kw411)?
                }
                .iter()?
                {
                    let unpack413 = unpack(item399, 2)?;
                    e.set("x", unpack413[0].clone())?;
                    e.set("y", unpack413[1].clone())?;
                    {
                        let fun402 = e.get("room")?.attr("append")?;
                        let mut args400 = Vec::new();
                        let mut kw401 = Vec::new();
                        args400.push({
                            let mut s = Vec::new();
                            s.push({
                                let fun405 = e.get("cap_cradle_circle_gap")?;
                                let mut args403 = Vec::new();
                                let mut kw404 = Vec::new();
                                args403.push(e.get("name")?);
                                args403.push(e.get("x")?);
                                args403.push(e.get("y")?);
                                args403.push({
                                    let fun408 = e.get("deck_lid_hole_radius")?;
                                    let mut args406 = Vec::new();
                                    let mut kw407 = Vec::new();
                                    args406.push(e.get("dname")?);
                                    fun408.call(args406, kw407)?
                                });
                                fun405.call(args403, kw404)?
                            });
                            s.push({
                                let mut str409 = String::new();
                                str409.push_str("the ");
                                str409.push_str(&format(&e.get("dname")?, &String::new())?);
                                str409.push_str(" mount's lid hole");
                                Val::Str(str409)
                            });
                            Val::tuple(s)
                        });
                        fun402.call(args400, kw401)?
                    };
                }
            }
            let assigned414 = e.get("cap_cradles")?.get(e.get("name")?)?.attr("centre")?;
            let unpack415 = unpack(assigned414.clone(), 2)?;
            e.set("cx", unpack415[0].clone())?;
            e.set("cy", unpack415[1].clone())?;
            let assigned416 = {
                let fun419 = e.get("cap_cradle_half_extents")?;
                let mut args417 = Vec::new();
                let mut kw418 = Vec::new();
                args417.push(e.get("name")?);
                fun419.call(args417, kw418)?
            };
            let unpack420 = unpack(assigned416.clone(), 2)?;
            e.set("hx", unpack420[0].clone())?;
            e.set("hy", unpack420[1].clone())?;
            {
                let fun423 = e.get("room")?.attr("append")?;
                let mut args421 = Vec::new();
                let mut kw422 = Vec::new();
                args421.push({
                    let mut s = Vec::new();
                    s.push({
                        let fun426 = e.get("min")?;
                        let mut args424 = Vec::new();
                        let mut kw425 = Vec::new();
                        args424.push(binary(
                            "sub",
                            binary(
                                "sub",
                                binary(
                                    "truediv",
                                    e.get("outer_shell_x_length")?,
                                    Val::Float(2.0f64),
                                )?,
                                {
                                    let fun429 = e.get("abs")?;
                                    let mut args427 = Vec::new();
                                    let mut kw428 = Vec::new();
                                    args427.push(e.get("cx")?);
                                    fun429.call(args427, kw428)?
                                },
                            )?,
                            e.get("hx")?,
                        )?);
                        args424.push(binary(
                            "sub",
                            binary(
                                "sub",
                                binary(
                                    "truediv",
                                    e.get("outer_shell_y_length")?,
                                    Val::Float(2.0f64),
                                )?,
                                {
                                    let fun432 = e.get("abs")?;
                                    let mut args430 = Vec::new();
                                    let mut kw431 = Vec::new();
                                    args430.push(e.get("cy")?);
                                    fun432.call(args430, kw431)?
                                },
                            )?,
                            e.get("hy")?,
                        )?);
                        fun426.call(args424, kw425)?
                    });
                    s.push(Val::Str("the lid's own edge".into()));
                    Val::tuple(s)
                });
                fun423.call(args421, kw422)?
            };
            for item433 in {
                let fun452 = e.get("cap_cradles")?.attr("items")?;
                let mut args450 = Vec::new();
                let mut kw451 = Vec::new();
                fun452.call(args450, kw451)?
            }
            .iter()?
            {
                let unpack453 = unpack(item433, 2)?;
                e.set("other", unpack453[0].clone())?;
                e.set("station", unpack453[1].clone())?;
                if {
                    let v434 = e.get("other")?;
                    let v435 = e.get("name")?;
                    Val::Bool(compare("eq", v434.clone(), v435.clone())?.truthy()?)
                }
                .truthy()?
                {
                    continue;
                }
                let assigned436 = e.get("station")?.attr("centre")?;
                let unpack437 = unpack(assigned436.clone(), 2)?;
                e.set("ox", unpack437[0].clone())?;
                e.set("oy", unpack437[1].clone())?;
                let assigned438 = {
                    let fun441 = e.get("cap_cradle_half_extents")?;
                    let mut args439 = Vec::new();
                    let mut kw440 = Vec::new();
                    args439.push(e.get("other")?);
                    fun441.call(args439, kw440)?
                };
                let unpack442 = unpack(assigned438.clone(), 2)?;
                e.set("ohx", unpack442[0].clone())?;
                e.set("ohy", unpack442[1].clone())?;
                {
                    let fun445 = e.get("room")?.attr("append")?;
                    let mut args443 = Vec::new();
                    let mut kw444 = Vec::new();
                    args443.push({
                        let mut s = Vec::new();
                        s.push({
                            let fun448 = e.get("cap_cradle_rectangle_gap")?;
                            let mut args446 = Vec::new();
                            let mut kw447 = Vec::new();
                            args446.push(e.get("name")?);
                            args446.push(binary("sub", e.get("ox")?, e.get("ohx")?)?);
                            args446.push(binary("add", e.get("ox")?, e.get("ohx")?)?);
                            args446.push(binary("sub", e.get("oy")?, e.get("ohy")?)?);
                            args446.push(binary("add", e.get("oy")?, e.get("ohy")?)?);
                            fun448.call(args446, kw447)?
                        });
                        s.push({
                            let mut str449 = String::new();
                            str449.push_str("the ");
                            str449.push_str(&format(&e.get("other")?, &String::new())?);
                            str449.push_str(" plinth");
                            Val::Str(str449)
                        });
                        Val::tuple(s)
                    });
                    fun445.call(args443, kw444)?
                };
            }
            return Ok({
                let fun456 = e.get("min")?;
                let mut args454 = Vec::new();
                let mut kw455 = Vec::new();
                args454.push(e.get("room")?);
                fun456.call(args454, kw455)?
            });
            Ok(Val::None)
        })
    })?;
    let assigned457 = Val::Float(hsm_cold_core_interface::LLDPE_TUBE_OD);
    e.set("lldpe_tube_od", assigned457.clone())?;
    let assigned458 = Val::Float(hsm_cold_core_interface::CAP_CONDUIT_BORE_RADIUS);
    e.set("cap_conduit_bore_radius", assigned458.clone())?;
    let assigned459 = {
        let d = Val::dict(vec![]);
        for (name, radius) in hsm_cold_core_interface::CAP_CONDUIT_BORE_RADII {
            d.set(Val::Str(name.into()), Val::Float(radius))?;
        }
        d
    };
    e.set("cap_conduit_bore_radii", assigned459.clone())?;
    let assigned460 = Val::Float(hsm_cold_core_interface::CAP_CONDUIT_WALL);
    e.set("cap_conduit_wall", assigned460.clone())?;
    let assigned461 = Val::Float(hsm_cold_core_interface::CAP_CONDUIT_BOSS_RADIUS);
    e.set("cap_conduit_boss_radius", assigned461.clone())?;
    let assigned462 = Val::Float(hsm_cold_core_interface::cap_conduit_lid_slip(&crate::interface::module_fits(&e.get("_interface_fits")?)?));
    e.set("cap_conduit_lid_slip", assigned462.clone())?;
    let assigned463 = Val::Float(hsm_cold_core_interface::CAP_CONDUIT_ENTRY_SKEW);
    e.set("cap_conduit_entry_skew", assigned463.clone())?;
    let assigned464 = Val::Float(hsm_cold_core_interface::cap_conduit_entry_relief_radius());
    e.set("cap_conduit_entry_relief_radius", assigned464.clone())?;
    let assigned471 = Val::Float(hsm_cold_core_interface::cap_conduit_entry_skew_ceiling());
    e.set("cap_conduit_entry_skew_ceiling", assigned471.clone())?;
    {
        let fun480 = e.get("state")?;
        let mut args478 = Vec::new();
        let mut kw479 = Vec::new();
        args478.push(Val::Str("entry-passes-section".into()));
        args478.push(Val::Str(
            "The countersink's mouth passes the leaning tube's whole section".into(),
        ));
        args478.push({
            let mut str481 = String::new();
            str481.push_str("⌀");
            str481.push_str(&format(
                &binary("truediv", e.get("lldpe_tube_od")?, {
                    let fun484 = e.get("math")?.attr("cos")?;
                    let mut args482 = Vec::new();
                    let mut kw483 = Vec::new();
                    args482.push({
                        let fun487 = e.get("math")?.attr("radians")?;
                        let mut args485 = Vec::new();
                        let mut kw486 = Vec::new();
                        args485.push(e.get("cap_conduit_entry_skew")?);
                        fun487.call(args485, kw486)?
                    });
                    fun484.call(args482, kw483)?
                })?,
                &val_string({
                    let mut str488 = String::new();
                    str488.push_str(".2f");
                    Val::Str(str488)
                })?,
            )?);
            str481.push_str(" across the face");
            Val::Str(str481)
        });
        args478.push({
            let v495 = e.get("cap_conduit_entry_relief_radius")?;
            let v496 = binary(
                "sub",
                binary(
                    "truediv",
                    binary("mul", Val::Float(0.5f64), e.get("lldpe_tube_od")?)?,
                    {
                        let fun491 = e.get("math")?.attr("cos")?;
                        let mut args489 = Vec::new();
                        let mut kw490 = Vec::new();
                        args489.push({
                            let fun494 = e.get("math")?.attr("radians")?;
                            let mut args492 = Vec::new();
                            let mut kw493 = Vec::new();
                            args492.push(e.get("cap_conduit_entry_skew")?);
                            fun494.call(args492, kw493)?
                        });
                        fun491.call(args489, kw490)?
                    },
                )?,
                Val::Float(1e-09f64),
            )?;
            Val::Bool(compare("ge", v495.clone(), v496.clone())?.truthy()?)
        });
        args478.push({
            let mut str497 = String::new();
            str497.push_str("cap conduit entry: a ⌀");
            str497.push_str(&format(
                &e.get("lldpe_tube_od")?,
                &val_string({
                    let mut str498 = String::new();
                    str498.push_str("g");
                    Val::Str(str498)
                })?,
            )?);
            str497.push_str(" line leaning ");
            str497.push_str(&format(
                &e.get("cap_conduit_entry_skew")?,
                &val_string({
                    let mut str499 = String::new();
                    str499.push_str("g");
                    Val::Str(str499)
                })?,
            )?);
            str497.push_str("° reads ");
            str497.push_str(&format(
                &binary("truediv", e.get("lldpe_tube_od")?, {
                    let fun502 = e.get("math")?.attr("cos")?;
                    let mut args500 = Vec::new();
                    let mut kw501 = Vec::new();
                    args500.push({
                        let fun505 = e.get("math")?.attr("radians")?;
                        let mut args503 = Vec::new();
                        let mut kw504 = Vec::new();
                        args503.push(e.get("cap_conduit_entry_skew")?);
                        fun505.call(args503, kw504)?
                    });
                    fun502.call(args500, kw501)?
                })?,
                &val_string({
                    let mut str506 = String::new();
                    str506.push_str(".2f");
                    Val::Str(str506)
                })?,
            )?);
            str497.push_str(" mm across the lid's face, over the ⌀");
            str497.push_str(&format(
                &binary(
                    "mul",
                    Val::Float(2.0f64),
                    e.get("cap_conduit_entry_relief_radius")?,
                )?,
                &val_string({
                    let mut str507 = String::new();
                    str507.push_str(".2f");
                    Val::Str(str507)
                })?,
            )?);
            str497.push_str(" the relief opens to");
            Val::Str(str497)
        });
        fun480.call(args478, kw479)?
    };
    let assigned508 = Val::Float(hsm_cold_core_interface::CO2_LANE_X);
    e.set("co2_lane_x", assigned508.clone())?;
    let assigned509 = {
        let fun512 = e.get("_above_mounts")?.attr("gas_guide_xy")?;
        let mut args510 = Vec::new();
        let mut kw511 = Vec::new();
        fun512.call(args510, kw511)?
    }
    .get(Val::Int(0i64))?;
    e.set("co2_cap_x", assigned509.clone())?;
    let assigned513 = Val::Float(hsm_cold_core_interface::WATER_OUTLET_CLIMB_X);
    e.set("water_outlet_climb_x", assigned513.clone())?;
    let assigned514 = Val::Float(hsm_cold_core_interface::WATER_OUTLET_UPPER_CLIMB_X);
    e.set("water_outlet_upper_climb_x", assigned514.clone())?;
    let assigned515 = crate::interface::tuple(&hsm_cold_core_interface::WATER_OUTLET_DRIFT_Z);
    e.set("water_outlet_drift_z", assigned515.clone())?;
    let assigned516 = Val::Float(hsm_cold_core_interface::REED_CABLE_CONDUIT_X);
    e.set("reed_cable_conduit_x", assigned516.clone())?;
    let assigned517 = Val::Float(hsm_cold_core_interface::REED_CABLE_CONDUIT_Y);
    e.set("reed_cable_conduit_y", assigned517.clone())?;
    // reed_cable_conduit_xy
    e.set("reed_cable_conduit_xy", {
        let params = vec![("side".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let mut s = Vec::new();
                s.push(binary(
                    "mul",
                    unary("neg", e.get("side")?)?,
                    e.get("reed_cable_conduit_x")?,
                )?);
                s.push(unary("neg", e.get("reed_cable_conduit_y")?)?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    let assigned518 = {
        let d = Val::dict(vec![]);
        d.set(Val::Str("water-in".into()), {
            let fun521 = e.get("_above_mounts")?.attr("cap_guide_xy")?;
            let mut args519 = Vec::new();
            let mut kw520 = Vec::new();
            args519.push(Val::Str("water-in".into()));
            args519.push(crate::interface::tuple(&hsm_cold_core_interface::WATER_IN_CONDUIT_XY));
            fun521.call(args519, kw520)?
        })?;
        d.set(Val::Str("reservoir-a".into()), {
            let fun524 = e.get("reservoir_draw_conduit_xy")?;
            let mut args522 = Vec::new();
            let mut kw523 = Vec::new();
            args522.push(unary("pos", Val::Int(1i64))?);
            fun524.call(args522, kw523)?
        })?;
        d.set(Val::Str("reservoir-b".into()), {
            let fun527 = e.get("_above_mounts")?.attr("cap_guide_xy")?;
            let mut args525 = Vec::new();
            let mut kw526 = Vec::new();
            args525.push(Val::Str("B-draw".into()));
            args525.push({
                let fun530 = e.get("reservoir_draw_conduit_xy")?;
                let mut args528 = Vec::new();
                let mut kw529 = Vec::new();
                args528.push(unary("neg", Val::Int(1i64))?);
                fun530.call(args528, kw529)?
            });
            fun527.call(args525, kw526)?
        })?;
        d.set(Val::Str("reservoir-a-fill".into()), {
            let fun533 = e.get("_above_mounts")?.attr("cap_guide_xy")?;
            let mut args531 = Vec::new();
            let mut kw532 = Vec::new();
            args531.push(Val::Str("A-fill".into()));
            args531.push({
                let fun536 = e.get("reservoir_fill_conduit_xy")?;
                let mut args534 = Vec::new();
                let mut kw535 = Vec::new();
                args534.push(unary("pos", Val::Int(1i64))?);
                fun536.call(args534, kw535)?
            });
            fun533.call(args531, kw532)?
        })?;
        d.set(Val::Str("reservoir-b-fill".into()), {
            let fun539 = e.get("reservoir_fill_conduit_xy")?;
            let mut args537 = Vec::new();
            let mut kw538 = Vec::new();
            args537.push(unary("neg", Val::Int(1i64))?);
            fun539.call(args537, kw538)?
        })?;
        d.set(Val::Str("carb-water-out".into()), {
            let fun542 = e.get("_above_mounts")?.attr("cap_guide_xy")?;
            let mut args540 = Vec::new();
            let mut kw541 = Vec::new();
            args540.push(Val::Str("carb-water-out".into()));
            args540.push(crate::interface::tuple(&hsm_cold_core_interface::CARB_WATER_OUT_CONDUIT_XY));
            fun542.call(args540, kw541)?
        })?;
        d.set(Val::Str("co2-in".into()), {
            let fun545 = e.get("_above_mounts")?.attr("gas_guide_xy")?;
            let mut args543 = Vec::new();
            let mut kw544 = Vec::new();
            fun545.call(args543, kw544)?
        })?;
        d
    };
    e.set("cap_fluid_conduits", assigned518.clone())?;
    let assigned546 = {
        let d = Val::dict(vec![]);
        d.set(Val::Str("reed-cable-a".into()), {
            let fun549 = e.get("reed_cable_conduit_xy")?;
            let mut args547 = Vec::new();
            let mut kw548 = Vec::new();
            args547.push(unary("pos", Val::Int(1i64))?);
            fun549.call(args547, kw548)?
        })?;
        d.set(
            Val::Str("sensor-cable".into()),
            crate::interface::tuple(&hsm_cold_core_interface::SENSOR_CABLE_CONDUIT_XY),
        )?;
        d
    };
    e.set("cap_cable_floor_conduits", assigned546.clone())?;
    let assigned550 = {
        let e = e.child();
        let out551 = Val::dict(vec![]);
        for item552 in {
            let fun555 = e.get("cap_cable_floor_conduits")?.attr("items")?;
            let mut args553 = Vec::new();
            let mut kw554 = Vec::new();
            fun555.call(args553, kw554)?
        }
        .iter()?
        {
            let unpack556 = unpack(item552, 2)?;
            e.set("name", unpack556[0].clone())?;
            e.set("xy", unpack556[1].clone())?;
            out551.set(e.get("name")?, {
                let fun559 = e.get("_above_mounts")?.attr("cap_guide_xy")?;
                let mut args557 = Vec::new();
                let mut kw558 = Vec::new();
                args557.push(e.get("name")?);
                args557.push(e.get("xy")?);
                fun559.call(args557, kw558)?
            })?;
        }
        out551
    };
    e.set("cap_cable_conduits", assigned550.clone())?;
    let assigned560 = {
        let d = Val::dict(vec![]);
        dict_extend(&d, e.get("cap_fluid_conduits")?)?;
        dict_extend(&d, e.get("cap_cable_conduits")?)?;
        d
    };
    e.set("cap_conduits", assigned560.clone())?;
    let assigned561 = {
        let d = Val::dict(vec![]);
        dict_extend(&d, e.get("cap_conduits")?)?;
        dict_extend(&d, e.get("cap_cable_floor_conduits")?)?;
        d.set(Val::Str("water-in".into()), {
            let fun564 = e.get("_above_mounts")?.attr("water_in_floor_xy")?;
            let mut args562 = Vec::new();
            let mut kw563 = Vec::new();
            fun564.call(args562, kw563)?
        })?;
        d.set(Val::Str("reservoir-b".into()), {
            let fun567 = e.get("reservoir_draw_conduit_xy")?;
            let mut args565 = Vec::new();
            let mut kw566 = Vec::new();
            args565.push(unary("neg", Val::Int(1i64))?);
            fun567.call(args565, kw566)?
        })?;
        d.set(Val::Str("reservoir-a-fill".into()), {
            let fun570 = e.get("reservoir_fill_conduit_xy")?;
            let mut args568 = Vec::new();
            let mut kw569 = Vec::new();
            args568.push(unary("pos", Val::Int(1i64))?);
            fun570.call(args568, kw569)?
        })?;
        d.set(Val::Str("reservoir-b-fill".into()), {
            let fun573 = e.get("reservoir_fill_conduit_xy")?;
            let mut args571 = Vec::new();
            let mut kw572 = Vec::new();
            args571.push(unary("neg", Val::Int(1i64))?);
            fun573.call(args571, kw572)?
        })?;
        d.set(
            Val::Str("carb-water-out".into()),
            e.get("cap_conduits")?
                .get(Val::Str("carb-water-out".into()))?,
        )?;
        d
    };
    e.set("cap_conduit_floor_xy", assigned561.clone())?;
    let assigned574 = {
        let mut s = Vec::new();
        s.push(Val::Str("reservoir-a-fill".into()));
        Val::tuple(s)
    };
    e.set("cap_passive_guides", assigned574.clone())?;
    let assigned575 = {
        let fun578 = e.get("tuple")?;
        let mut args576 = Vec::new();
        let mut kw577 = Vec::new();
        args576.push(e.get("cap_cable_conduits")?);
        fun578.call(args576, kw577)?
    };
    e.set("cap_cable_guides", assigned575.clone())?;
    let assigned579 = {
        let mut s = Vec::new();
        Val::tuple(s)
    };
    e.set("cap_conduit_links", assigned579.clone())?;
    let assigned580 = Val::Float(hsm_cold_core_interface::CAP_CONDUIT_LINK_WIDTH);
    e.set("cap_conduit_link_width", assigned580.clone())?;
    let assigned581 = {
        let e = e.child();
        let out582 = Val::set_values(vec![]);
        for item583 in e.get("cap_conduits")?.iter()? {
            e.set("n", item583)?;
            if {
                let fun586 = e.get("n")?.attr("endswith")?;
                let mut args584 = Vec::new();
                let mut kw585 = Vec::new();
                args584.push(Val::Str("-fill".into()));
                fun586.call(args584, kw585)?
            }
            .truthy()?
            {
                out582.attr("add")?.call(vec![e.get("n")?], vec![])?;
            }
        }
        out582
    };
    e.set("_fill_conduits", assigned581.clone())?;
    let assigned587 = {
        let e = e.child();
        let out588 = Val::set_values(vec![]);
        for item589 in e.get("reservoir_fill_sides")?.iter()? {
            e.set("s", item589)?;
            out588.attr("add")?.call(
                vec![{
                    let mut str590 = String::new();
                    str590.push_str("reservoir-");
                    str590.push_str(&format(
                        &Val::Str("ab".into()).get({
                            let v591 = e.get("s")?;
                            let v592 = Val::Int(0i64);
                            Val::Bool(compare("lt", v591.clone(), v592.clone())?.truthy()?)
                        })?,
                        &String::new(),
                    )?);
                    str590.push_str("-fill");
                    Val::Str(str590)
                }],
                vec![],
            )?;
        }
        out588
    };
    e.set("_fill_wanted", assigned587.clone())?;
    {
        let fun595 = e.get("state")?;
        let mut args593 = Vec::new();
        let mut kw594 = Vec::new();
        args593.push(Val::Str("fill-conduits-paired".into()));
        args593.push(Val::Str(
            "Every fill bore has a conduit over it and every conduit a bore".into(),
        ));
        args593.push({
            let mut str596 = String::new();
            str596.push_str("the cap's fills naming ");
            str596.push_str(&format(
                &{
                    let fun599 = e.get("sorted")?;
                    let mut args597 = Vec::new();
                    let mut kw598 = Vec::new();
                    args597.push(e.get("_fill_wanted")?);
                    fun599.call(args597, kw598)?
                },
                &String::new(),
            )?);
            Val::Str(str596)
        });
        args593.push({
            let v600 = e.get("_fill_conduits")?;
            let v601 = e.get("_fill_wanted")?;
            Val::Bool(compare("eq", v600.clone(), v601.clone())?.truthy()?)
        });
        args593.push({let mut str602=String::new();str602.push_str("reservoir fills: ");str602.push_str(&format(&{let fun605=e.get("sorted")?;let mut args603=Vec::new();let mut kw604=Vec::new();args603.push(e.get("_fill_conduits")?);fun605.call(args603,kw604)?},&String::new())?);str602.push_str(" stand on the cap, but `reservoir_fill_sides` cuts ");str602.push_str(&format(&e.get("reservoir_fill_sides")?,&String::new())?);str602.push_str(" — a conduit with no bore under it is a hole into a sealed pocket, and a bore with no conduit over it is a blind one");Val::Str(str602)});
        fun595.call(args593, kw594)?
    };
    let assigned606 = Val::Float(hsm_cold_core_interface::CARBONATOR_TOP_PLATE_Z);
    e.set("carbonator_top_plate_z", assigned606.clone())?;
    let assigned607 = Val::Float(hsm_cold_core_interface::TOP_BAND_TO_CAP);
    e.set("top_band_to_cap", assigned607.clone())?;
    let assigned608 = Val::Float(hsm_cold_core_interface::LLDPE_BEND_RADIUS);
    e.set("lldpe_bend_radius", assigned608.clone())?;
    // cap_conduit_wall_neck
    e.set("cap_conduit_wall_neck", {
        let params = vec![("x".into(), None, false), ("y".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned609 = {
                let fun612 = e.get("min")?;
                let mut args610 = Vec::new();
                let mut kw611 = Vec::new();
                args610.push(binary(
                    "sub",
                    binary(
                        "truediv",
                        e.get("outer_shell_x_length")?,
                        Val::Float(2.0f64),
                    )?,
                    {
                        let fun615 = e.get("abs")?;
                        let mut args613 = Vec::new();
                        let mut kw614 = Vec::new();
                        args613.push(e.get("x")?);
                        fun615.call(args613, kw614)?
                    },
                )?);
                args610.push(binary(
                    "sub",
                    binary(
                        "truediv",
                        e.get("outer_shell_y_length")?,
                        Val::Float(2.0f64),
                    )?,
                    {
                        let fun618 = e.get("abs")?;
                        let mut args616 = Vec::new();
                        let mut kw617 = Vec::new();
                        args616.push(e.get("y")?);
                        fun618.call(args616, kw617)?
                    },
                )?);
                fun612.call(args610, kw611)?
            };
            e.set("to_outer", assigned609.clone())?;
            if {
                let v619 = binary("sub", e.get("to_outer")?, e.get("outer_shell_wall")?)?;
                let v620 = e.get("cap_conduit_boss_radius")?;
                Val::Bool(compare("ge", v619.clone(), v620.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok({
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        binary("sub", e.get("to_outer")?, e.get("outer_shell_wall")?)?,
                        e.get("cap_conduit_boss_radius")?,
                    )?);
                    s.push(Val::Str("the pour gap behind a standing column".into()));
                    Val::tuple(s)
                });
            }
            return Ok({
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("to_outer")?,
                    e.get("cap_conduit_bore_radius")?,
                )?);
                s.push(Val::Str("the wall left outboard of a merged bore".into()));
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    let assigned621 = {
        let fun624 = e.get("bound")?;
        let mut args622 = Vec::new();
        let mut kw623 = Vec::new();
        args622.push(Val::Str("cap-conduit-wall".into()));
        args622.push(Val::Str(
            "Every conduit column stands the pour gap off the wall or merges in".into(),
        ));
        args622.push({
            let mut str625 = String::new();
            str625.push_str("the pour gap apart or a ");
            str625.push_str(&format(
                &e.get("cap_conduit_wall")?,
                &val_string({
                    let mut str626 = String::new();
                    str626.push_str("g");
                    Val::Str(str626)
                })?,
            )?);
            str625.push_str(" mm neck");
            Val::Str(str625)
        });
        fun624.call(args622, kw623)?
    };
    e.set("_conduit_wall", assigned621.clone())?;
    for item627 in e.get("cap_conduits")?.iter()? {
        e.set("_name", item627)?;
        let assigned628 = {
            let fun631 = e.get("cap_conduit_wall_neck")?;
            let mut args629 = Vec::new();
            let mut kw630 = Vec::new();
            args629.extend(e.get("cap_conduits")?.get(e.get("_name")?)?.iter()?);
            fun631.call(args629, kw630)?
        };
        let unpack632 = unpack(assigned628.clone(), 2)?;
        e.set("_neck", unpack632[0].clone())?;
        e.set("_what", unpack632[1].clone())?;
        let assigned633 = if {
            let fun636 = e.get("_what")?.attr("startswith")?;
            let mut args634 = Vec::new();
            let mut kw635 = Vec::new();
            args634.push(Val::Str("the pour".into()));
            fun636.call(args634, kw635)?
        }
        .truthy()?
        {
            e.get("deck_mount_cap_gap")?
        } else {
            e.get("cap_conduit_wall")?
        };
        e.set("_want", assigned633.clone())?;
        {
            let fun639 = e.get("_conduit_wall")?;
            let mut args637 = Vec::new();
            let mut kw638 = Vec::new();
            args637.push({
                let v640 = e.get("_neck")?;
                let v641 = binary("sub", e.get("_want")?, Val::Float(1e-09f64))?;
                Val::Bool(compare("ge", v640.clone(), v641.clone())?.truthy()?)
            });
            args637.push({let mut str642=String::new();str642.push_str("cap conduit ");str642.push_str(&format(&e.get("_name")?,&String::new())?);str642.push_str(": ");str642.push_str(&format(&e.get("_what")?,&String::new())?);str642.push_str(" is ");str642.push_str(&format(&e.get("_neck")?,&val_string({let mut str643=String::new();str643.push_str(".3f");Val::Str(str643)})?)?);str642.push_str(" mm, under the ");str642.push_str(&format(&e.get("_want")?,&val_string({let mut str644=String::new();str644.push_str("g");Val::Str(str644)})?)?);str642.push_str(" mm it takes — a column either stands the pour gap off the wall or merges into it");Val::Str(str642)});
            fun639.call(args637, kw638)?
        };
    }
    // foam_cap_lid_pour_xy
    e.set("foam_cap_lid_pour_xy", {
        let params = vec![("top".into(), Some(Val::Bool(false)), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if e.get("top")?.truthy()? {
                return Ok(e.get("top_lid_pour_xy")?);
            }
            let assigned645 = binary(
                "sub",
                binary("truediv", e.get("outer_shell_x_length")?, Val::Int(2i64))?,
                e.get("foam_cap_lid_hole_inset")?,
            )?;
            e.set("x", assigned645.clone())?;
            let assigned646 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("bands", assigned646.clone())?;
            // fence
            e.set("fence", {
                let params = vec![
                    ("sx".into(), None, false),
                    ("sy".into(), None, false),
                    ("need".into(), None, false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned647 = binary(
                        "sub",
                        binary("pow", e.get("need")?, Val::Int(2i64))?,
                        binary(
                            "pow",
                            binary("sub", e.get("x")?, e.get("sx")?)?,
                            Val::Int(2i64),
                        )?,
                    )?;
                    e.set("reach", assigned647.clone())?;
                    if {
                        let v648 = e.get("reach")?;
                        let v649 = Val::Float(0.0f64);
                        Val::Bool(compare("gt", v648.clone(), v649.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        let assigned650 = {
                            let fun653 = e.get("math")?.attr("sqrt")?;
                            let mut args651 = Vec::new();
                            let mut kw652 = Vec::new();
                            args651.push(e.get("reach")?);
                            fun653.call(args651, kw652)?
                        };
                        e.set("half", assigned650.clone())?;
                        {
                            let fun656 = e.get("bands")?.attr("append")?;
                            let mut args654 = Vec::new();
                            let mut kw655 = Vec::new();
                            args654.push({
                                let mut s = Vec::new();
                                s.push(binary("sub", e.get("sy")?, e.get("half")?)?);
                                s.push(binary("add", e.get("sy")?, e.get("half")?)?);
                                Val::tuple(s)
                            });
                            fun656.call(args654, kw655)?
                        };
                    }
                    Ok(Val::None)
                })
            })?;
            for item657 in e.get("deck_mounts")?.iter()? {
                e.set("name", item657)?;
                for item658 in {
                    let fun664 = e.get("deck_mount_xy")?;
                    let mut args662 = Vec::new();
                    let mut kw663 = Vec::new();
                    args662.push(e.get("name")?);
                    fun664.call(args662, kw663)?
                }
                .iter()?
                {
                    let unpack665 = unpack(item658, 2)?;
                    e.set("sx", unpack665[0].clone())?;
                    e.set("sy", unpack665[1].clone())?;
                    {
                        let fun661 = e.get("fence")?;
                        let mut args659 = Vec::new();
                        let mut kw660 = Vec::new();
                        args659.push(e.get("sx")?);
                        args659.push(e.get("sy")?);
                        args659.push(binary(
                            "add",
                            binary(
                                "add",
                                e.get("foam_cap_lid_pour_radius")?,
                                e.get("screw_clearance_radius")?,
                            )?,
                            e.get("deck_mount_cap_gap")?,
                        )?);
                        fun661.call(args659, kw660)?
                    };
                }
            }
            for item666 in {
                let fun698 = e.get("cap_cradles")?.attr("items")?;
                let mut args696 = Vec::new();
                let mut kw697 = Vec::new();
                fun698.call(args696, kw697)?
            }
            .iter()?
            {
                let unpack699 = unpack(item666, 2)?;
                e.set("name", unpack699[0].clone())?;
                e.set("station", unpack699[1].clone())?;
                if !{
                    let fun669 = e.get("math")?.attr("isclose")?;
                    let mut args667 = Vec::new();
                    let mut kw668 = Vec::new();
                    args667.push(binary(
                        "mod",
                        e.get("station")?.attr("yaw")?,
                        Val::Float(90.0f64),
                    )?);
                    args667.push(Val::Float(0.0f64));
                    fun669.call(args667, kw668)?
                }
                .truthy()?
                {
                    anyhow::bail!("{}", val_string(Val::Str("assertion failed".into()))?);
                }
                let assigned670 = e.get("station")?.attr("centre")?;
                let unpack671 = unpack(assigned670.clone(), 2)?;
                e.set("cx", unpack671[0].clone())?;
                e.set("cy", unpack671[1].clone())?;
                let assigned672 = {
                    let fun675 = e.get("cap_cradle_half_extents")?;
                    let mut args673 = Vec::new();
                    let mut kw674 = Vec::new();
                    args673.push(e.get("name")?);
                    fun675.call(args673, kw674)?
                };
                let unpack676 = unpack(assigned672.clone(), 2)?;
                e.set("hx", unpack676[0].clone())?;
                e.set("hy", unpack676[1].clone())?;
                let assigned677 = {
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        e.get("hx")?,
                        e.get("cap_cradle_corner_radius")?,
                    )?);
                    s.push(binary(
                        "sub",
                        e.get("hy")?,
                        e.get("cap_cradle_corner_radius")?,
                    )?);
                    Val::tuple(s)
                };
                let unpack678 = unpack(assigned677.clone(), 2)?;
                e.set("core_x", unpack678[0].clone())?;
                e.set("core_y", unpack678[1].clone())?;
                let assigned679 = binary(
                    "add",
                    binary(
                        "add",
                        e.get("foam_cap_lid_pour_radius")?,
                        e.get("deck_mount_cap_gap")?,
                    )?,
                    e.get("cap_cradle_corner_radius")?,
                )?;
                e.set("reach", assigned679.clone())?;
                let assigned680 = {
                    let fun683 = e.get("max")?;
                    let mut args681 = Vec::new();
                    let mut kw682 = Vec::new();
                    args681.push(binary(
                        "sub",
                        {
                            let fun686 = e.get("abs")?;
                            let mut args684 = Vec::new();
                            let mut kw685 = Vec::new();
                            args684.push(binary("sub", e.get("x")?, e.get("cx")?)?);
                            fun686.call(args684, kw685)?
                        },
                        e.get("core_x")?,
                    )?);
                    args681.push(Val::Float(0.0f64));
                    fun683.call(args681, kw682)?
                };
                e.set("dx", assigned680.clone())?;
                if {
                    let v687 = e.get("dx")?;
                    let v688 = e.get("reach")?;
                    Val::Bool(compare("lt", v687.clone(), v688.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned689 = binary("add", e.get("core_y")?, {
                        let fun692 = e.get("math")?.attr("sqrt")?;
                        let mut args690 = Vec::new();
                        let mut kw691 = Vec::new();
                        args690.push(binary(
                            "sub",
                            binary("mul", e.get("reach")?, e.get("reach")?)?,
                            binary("mul", e.get("dx")?, e.get("dx")?)?,
                        )?);
                        fun692.call(args690, kw691)?
                    })?;
                    e.set("half", assigned689.clone())?;
                    {
                        let fun695 = e.get("bands")?.attr("append")?;
                        let mut args693 = Vec::new();
                        let mut kw694 = Vec::new();
                        args693.push({
                            let mut s = Vec::new();
                            s.push(binary("sub", e.get("cy")?, e.get("half")?)?);
                            s.push(binary("add", e.get("cy")?, e.get("half")?)?);
                            Val::tuple(s)
                        });
                        fun695.call(args693, kw694)?
                    };
                }
            }
            e.set("merged", {
                let mut s = Vec::new();
                Val::list(s)
            })?;
            for item700 in {
                let fun713 = e.get("sorted")?;
                let mut args711 = Vec::new();
                let mut kw712 = Vec::new();
                args711.push(e.get("bands")?);
                fun713.call(args711, kw712)?
            }
            .iter()?
            {
                let unpack714 = unpack(item700, 2)?;
                e.set("lo", unpack714[0].clone())?;
                e.set("hi", unpack714[1].clone())?;
                if {
                    let v703 = e.get("merged")?;
                    if v703.truthy()? {
                        {
                            let v701 = e.get("lo")?;
                            let v702 = e
                                .get("merged")?
                                .get(unary("neg", Val::Int(1i64))?)?
                                .get(Val::Int(1i64))?;
                            Val::Bool(compare("le", v701.clone(), v702.clone())?.truthy()?)
                        }
                    } else {
                        v703
                    }
                }
                .truthy()?
                {
                    let assigned704 = {
                        let fun707 = e.get("max")?;
                        let mut args705 = Vec::new();
                        let mut kw706 = Vec::new();
                        args705.push(
                            e.get("merged")?
                                .get(unary("neg", Val::Int(1i64))?)?
                                .get(Val::Int(1i64))?,
                        );
                        args705.push(e.get("hi")?);
                        fun707.call(args705, kw706)?
                    };
                    e.get("merged")?
                        .get(unary("neg", Val::Int(1i64))?)?
                        .set(Val::Int(1i64), assigned704.clone())?;
                } else {
                    {
                        let fun710 = e.get("merged")?.attr("append")?;
                        let mut args708 = Vec::new();
                        let mut kw709 = Vec::new();
                        args708.push({
                            let mut s = Vec::new();
                            s.push(e.get("lo")?);
                            s.push(e.get("hi")?);
                            Val::list(s)
                        });
                        fun710.call(args708, kw709)?
                    };
                }
            }
            let assigned715 = Val::Float(0.0f64);
            e.set("y", assigned715.clone())?;
            for item716 in e.get("merged")?.iter()? {
                let unpack723 = unpack(item716, 2)?;
                e.set("lo", unpack723[0].clone())?;
                e.set("hi", unpack723[1].clone())?;
                if {
                    let v717 = e.get("lo")?;
                    let v718 = e.get("y")?;
                    let v719 = e.get("hi")?;
                    Val::Bool(
                        compare("lt", v717.clone(), v718.clone())?.truthy()?
                            && compare("lt", v718.clone(), v719.clone())?.truthy()?,
                    )
                }
                .truthy()?
                {
                    let assigned720 = if {
                        let v721 = binary("sub", e.get("y")?, e.get("lo")?)?;
                        let v722 = binary("sub", e.get("hi")?, e.get("y")?)?;
                        Val::Bool(compare("le", v721.clone(), v722.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        e.get("lo")?
                    } else {
                        e.get("hi")?
                    };
                    e.set("y", assigned720.clone())?;
                    break;
                }
            }
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("x")?);
                s.push(e.get("y")?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // foam_cap_lid_vent_xy
    e.set("foam_cap_lid_vent_xy", {
        let params = vec![("top".into(), Some(Val::Bool(false)), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned724 = unary(
                "neg",
                binary(
                    "add",
                    binary(
                        "sub",
                        binary("truediv", e.get("outer_shell_x_length")?, Val::Int(2i64))?,
                        e.get("foam_cap_lid_hole_inset")?,
                    )?,
                    if e.get("top")?.truthy()? {
                        e.get("top_lid_vent_setback")?
                    } else {
                        Val::Float(0.0f64)
                    },
                )?,
            )?;
            e.set("x", assigned724.clone())?;
            let assigned725 = binary(
                "sub",
                binary("truediv", e.get("outer_shell_y_length")?, Val::Int(2i64))?,
                e.get("foam_cap_lid_hole_inset")?,
            )?;
            e.set("y", assigned725.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(unary("neg", e.get("y")?)?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    let assigned726 = {
        let fun729 = e.get("bound")?;
        let mut args727 = Vec::new();
        let mut kw728 = Vec::new();
        args727.push(Val::Str("cradle-room".into()));
        args727.push(Val::Str(
            "Every plinth clears the other openings on the lid".into(),
        ));
        args727.push({
            let mut str730 = String::new();
            str730.push_str(&format(
                &e.get("cap_cradle_room_gap")?,
                &val_string({
                    let mut str731 = String::new();
                    str731.push_str("g");
                    Val::Str(str731)
                })?,
            )?);
            str730.push_str(" mm off the nearest");
            Val::Str(str730)
        });
        fun729.call(args727, kw728)?
    };
    e.set("_cradle_room", assigned726.clone())?;
    for item732 in e.get("cap_cradles")?.iter()? {
        e.set("_name", item732)?;
        let assigned733 = {
            let fun736 = e.get("cap_cradle_room")?;
            let mut args734 = Vec::new();
            let mut kw735 = Vec::new();
            args734.push(e.get("_name")?);
            fun736.call(args734, kw735)?
        };
        let unpack737 = unpack(assigned733.clone(), 2)?;
        e.set("_room", unpack737[0].clone())?;
        e.set("_what", unpack737[1].clone())?;
        {
            let fun740 = e.get("_cradle_room")?;
            let mut args738 = Vec::new();
            let mut kw739 = Vec::new();
            args738.push({
                let v741 = e.get("_room")?;
                let v742 = binary("sub", e.get("cap_cradle_room_gap")?, Val::Float(1e-09f64))?;
                Val::Bool(compare("ge", v741.clone(), v742.clone())?.truthy()?)
            });
            args738.push({
                let mut str743 = String::new();
                str743.push_str("valve plinth ");
                str743.push_str(&format(&e.get("_name")?, &String::new())?);
                str743.push_str(": ");
                str743.push_str(&format(
                    &e.get("_room")?,
                    &val_string({
                        let mut str744 = String::new();
                        str744.push_str(".3f");
                        Val::Str(str744)
                    })?,
                )?);
                str743.push_str(" mm off ");
                str743.push_str(&format(&e.get("_what")?, &String::new())?);
                Val::Str(str743)
            });
            fun740.call(args738, kw739)?
        };
        for item745 in {
            let fun763 = e.get("cap_cradle_xy")?;
            let mut args761 = Vec::new();
            let mut kw762 = Vec::new();
            args761.push(e.get("_name")?);
            fun763.call(args761, kw762)?
        }
        .iter()?
        {
            let unpack764 = unpack(item745, 2)?;
            e.set("_sx", unpack764[0].clone())?;
            e.set("_sy", unpack764[1].clone())?;
            for item746 in {
                let fun759 = e.get("cap_conduits")?.attr("values")?;
                let mut args757 = Vec::new();
                let mut kw758 = Vec::new();
                fun759.call(args757, kw758)?
            }
            .iter()?
            {
                let unpack760 = unpack(item746, 2)?;
                e.set("_hx", unpack760[0].clone())?;
                e.set("_hy", unpack760[1].clone())?;
                let assigned747 = binary(
                    "sub",
                    binary(
                        "sub",
                        {
                            let fun750 = e.get("math")?.attr("hypot")?;
                            let mut args748 = Vec::new();
                            let mut kw749 = Vec::new();
                            args748.push(binary("sub", e.get("_sx")?, e.get("_hx")?)?);
                            args748.push(binary("sub", e.get("_sy")?, e.get("_hy")?)?);
                            fun750.call(args748, kw749)?
                        },
                        e.get("cap_cradle_boss_radius")?,
                    )?,
                    e.get("cap_conduit_entry_relief_radius")?,
                )?;
                e.set("_room", assigned747.clone())?;
                {
                    let fun753 = e.get("_cradle_room")?;
                    let mut args751 = Vec::new();
                    let mut kw752 = Vec::new();
                    args751.push({
                        let v754 = e.get("_room")?;
                        let v755 =
                            binary("sub", e.get("cap_cradle_room_gap")?, Val::Float(1e-09f64))?;
                        Val::Bool(compare("ge", v754.clone(), v755.clone())?.truthy()?)
                    });
                    args751.push({
                        let mut str756 = String::new();
                        str756.push_str("valve plinth ");
                        str756.push_str(&format(&e.get("_name")?, &String::new())?);
                        str756.push_str(": conduit passage preserves each socket wall");
                        Val::Str(str756)
                    });
                    fun753.call(args751, kw752)?
                };
            }
        }
    }
    let assigned765 = {
        let fun768 = e.get("namedtuple")?;
        let mut args766 = Vec::new();
        let mut kw767 = Vec::new();
        args766.push(Val::Str("CapAnchor".into()));
        args766.push(Val::Str("centre seat_r over_face along closure".into()));
        fun768.call(args766, kw767)?
    };
    e.set("CapAnchor", assigned765.clone())?;
    let assigned769 = {
        let mut s = Vec::new();
        s.push(Val::None);
        s.push(Val::Str("x".into()));
        s.push(Val::Str("tie".into()));
        Val::tuple(s)
    };
    e.get("CapAnchor")?
        .attr("__new__")?
        .setattr("__defaults__", assigned769.clone())?;
    let assigned770 = {
        let d = Val::dict(vec![]);
        d
    };
    e.set("cap_anchors", assigned770.clone())?;
    let assigned771 = Val::Float(hsm_cold_core_interface::CAP_ANCHOR_TIE_W);
    e.set("cap_anchor_tie_w", assigned771.clone())?;
    let assigned772 = Val::Float(hsm_cold_core_interface::cap_anchor_cav_buffer(&crate::interface::module_fits(&e.get("_interface_fits")?)?));
    e.set("cap_anchor_cav_buffer", assigned772.clone())?;
    let assigned773 = Val::Float(hsm_cold_core_interface::cap_anchor_cav_w(&crate::interface::module_fits(&e.get("_interface_fits")?)?));
    e.set("cap_anchor_cav_w", assigned773.clone())?;
    let assigned774 = Val::Float(hsm_cold_core_interface::CAP_ANCHOR_CAV_WALL);
    e.set("cap_anchor_cav_wall", assigned774.clone())?;
    let assigned775 = Val::Float(hsm_cold_core_interface::cap_anchor_len(&crate::interface::module_fits(&e.get("_interface_fits")?)?));
    e.set("cap_anchor_len", assigned775.clone())?;
    let assigned776 = e.get("cap_cradle_wall")?;
    e.set("cap_anchor_wall", assigned776.clone())?;
    let assigned777 = binary(
        "add",
        e.get("cap_anchor_wall")?,
        e.get("fits")?.attr("supported_surface")?,
    )?;
    e.set("cap_anchor_channel_height", assigned777.clone())?;
    // cap_anchor_axis_over_face
    e.set("cap_anchor_axis_over_face",{let params=vec![("name".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned778=e.get("cap_anchors")?.get(e.get("name")?)?;e.set("row",assigned778.clone())?;
let assigned779=e.get("row")?.attr("over_face")?;e.set("stated",assigned779.clone())?;
let assigned780=binary("add",binary("add",e.get("row")?.attr("seat_r")?,e.get("cap_anchor_wall")?)?,if {let v781=e.get("row")?.attr("closure")?;let v782=Val::Str("cap".into());Val::Bool(compare("eq",v781.clone(),v782.clone())?.truthy()?)}.truthy()? {Val::Float(0.0f64)} else {e.get("cap_anchor_channel_height")?})?;e.set("least",assigned780.clone())?;
if {let v783=e.get("stated")?;let v784=Val::None;Val::Bool(compare("is",v783.clone(),v784.clone())?.truthy()?)}.truthy()? {
return Ok(e.get("least")?);
}
if {let v785=e.get("stated")?;let v786=binary("sub",e.get("least")?,Val::Float(1e-09f64))?;Val::Bool(compare("lt",v785.clone(),v786.clone())?.truthy()?)}.truthy()? {
anyhow::bail!("{}",val_string({let fun789=e.get("ValueError")?;let mut args787=Vec::new();let mut kw788=Vec::new();args787.push({let mut str790=String::new();str790.push_str("cap_anchor_axis_over_face: ");str790.push_str(&format(&e.get("name")?,&String::new())?);str790.push_str(" states ");str790.push_str(&format(&e.get("stated")?,&val_string({let mut str791=String::new();str791.push_str(".3f");Val::Str(str791)})?)?);str790.push_str(" mm over the lid's face and the rib's own layers come to ");str790.push_str(&format(&e.get("least")?,&val_string({let mut str792=String::new();str792.push_str(".3f");Val::Str(str792)})?)?);str790.push_str(". A seat lower than that stands the body on the lid or on its own zip tie.");Val::Str(str790)});fun789.call(args787,kw788)?})?);
}
return Ok(e.get("stated")?);
Ok(Val::None)})})?;
    // cap_anchor_tie_loop
    e.set("cap_anchor_tie_loop", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned793 = e.get("cap_anchors")?.get(e.get("name")?)?.attr("seat_r")?;
            e.set("r", assigned793.clone())?;
            if {
                let v794 = e.get("name")?;
                let v795 = Val::Str("discharge-chain".into());
                Val::Bool(compare("eq", v794.clone(), v795.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned796 = {
                    let fun799 = e.get("_above_mounts")?.attr("check_support_datums")?;
                    let mut args797 = Vec::new();
                    let mut kw798 = Vec::new();
                    fun799.call(args797, kw798)?
                };
                e.set("data", assigned796.clone())?;
                let assigned800 = e.get("data")?.get(Val::Str("half_width_mm".into()))?;
                e.set("w", assigned800.clone())?;
                let assigned801 = binary(
                    "sub",
                    e.get("data")?
                        .get(Val::Str("centre_world_mm".into()))?
                        .get(Val::Int(2i64))?,
                    e.get("data")?.get(Val::Str("tie_route_z_mm".into()))?,
                )?;
                e.set("h", assigned801.clone())?;
                return Ok(binary(
                    "add",
                    binary(
                        "add",
                        binary("add", binary("add", e.get("w")?, e.get("h")?)?, {
                            let fun804 = e.get("math")?.attr("sqrt")?;
                            let mut args802 = Vec::new();
                            let mut kw803 = Vec::new();
                            args802.push(binary(
                                "sub",
                                binary("mul", e.get("w")?, e.get("w")?)?,
                                binary("mul", e.get("r")?, e.get("r")?)?,
                            )?);
                            fun804.call(args802, kw803)?
                        })?,
                        {
                            let fun807 = e.get("math")?.attr("sqrt")?;
                            let mut args805 = Vec::new();
                            let mut kw806 = Vec::new();
                            args805.push(binary(
                                "sub",
                                binary("mul", e.get("h")?, e.get("h")?)?,
                                binary("mul", e.get("r")?, e.get("r")?)?,
                            )?);
                            fun807.call(args805, kw806)?
                        },
                    )?,
                    binary(
                        "mul",
                        e.get("r")?,
                        binary(
                            "sub",
                            binary(
                                "sub",
                                binary("mul", Val::Float(1.5f64), e.get("math")?.attr("pi")?)?,
                                {
                                    let fun810 = e.get("math")?.attr("acos")?;
                                    let mut args808 = Vec::new();
                                    let mut kw809 = Vec::new();
                                    args808.push(binary("truediv", e.get("r")?, e.get("w")?)?);
                                    fun810.call(args808, kw809)?
                                },
                            )?,
                            {
                                let fun813 = e.get("math")?.attr("acos")?;
                                let mut args811 = Vec::new();
                                let mut kw812 = Vec::new();
                                args811.push(binary("truediv", e.get("r")?, e.get("h")?)?);
                                fun813.call(args811, kw812)?
                            },
                        )?,
                    )?,
                )?);
            } else {
                let assigned814 = binary("add", e.get("r")?, e.get("cap_anchor_wall")?)?;
                e.set("w", assigned814.clone())?;
                let assigned815 = binary(
                    "sub",
                    {
                        let fun818 = e.get("cap_anchor_axis_over_face")?;
                        let mut args816 = Vec::new();
                        let mut kw817 = Vec::new();
                        args816.push(e.get("name")?);
                        fun818.call(args816, kw817)?
                    },
                    e.get("cap_anchor_channel_height")?,
                )?;
                e.set("h", assigned815.clone())?;
            }
            return Ok(binary(
                "add",
                binary(
                    "add",
                    binary(
                        "add",
                        binary("mul", Val::Float(2.0f64), e.get("w")?)?,
                        binary("mul", Val::Float(2.0f64), e.get("h")?)?,
                    )?,
                    binary("mul", Val::Float(2.0f64), {
                        let fun821 = e.get("math")?.attr("sqrt")?;
                        let mut args819 = Vec::new();
                        let mut kw820 = Vec::new();
                        args819.push(binary(
                            "sub",
                            binary("mul", e.get("w")?, e.get("w")?)?,
                            binary("mul", e.get("r")?, e.get("r")?)?,
                        )?);
                        fun821.call(args819, kw820)?
                    })?,
                )?,
                binary(
                    "mul",
                    e.get("r")?,
                    binary(
                        "sub",
                        e.get("math")?.attr("pi")?,
                        binary("mul", Val::Float(2.0f64), {
                            let fun824 = e.get("math")?.attr("acos")?;
                            let mut args822 = Vec::new();
                            let mut kw823 = Vec::new();
                            args822.push(binary("truediv", e.get("r")?, e.get("w")?)?);
                            fun824.call(args822, kw823)?
                        })?,
                    )?,
                )?,
            )?);
            Ok(Val::None)
        })
    })?;
    // cap_anchor_slotted
    e.set("cap_anchor_slotted", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let v830 = {
                    let v831 = e.get("cap_anchors")?.get(e.get("name")?)?.attr("closure")?;
                    let v832 = Val::Str("cap".into());
                    Val::Bool(compare("eq", v831.clone(), v832.clone())?.truthy()?)
                };
                if v830.truthy()? {
                    {
                        let v828 = {
                            let fun827 = e.get("cap_anchor_axis_over_face")?;
                            let mut args825 = Vec::new();
                            let mut kw826 = Vec::new();
                            args825.push(e.get("name")?);
                            fun827.call(args825, kw826)?
                        };
                        let v829 = binary(
                            "sub",
                            Val::Float(hsm_enclosure_interface::anchor_cap::slot_top()),
                            binary(
                                "truediv",
                                Val::Float(hsm_enclosure_interface::anchor_cap::HEADROOM),
                                Val::Float(2.0f64),
                            )?,
                        )?;
                        Val::Bool(compare("lt", v828.clone(), v829.clone())?.truthy()?)
                    }
                } else {
                    v830
                }
            });
            Ok(Val::None)
        })
    })?;
    // cap_anchor_room
    e.set("cap_anchor_room", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned833 = e.get("cap_anchors")?.get(e.get("name")?)?;
            e.set("row", assigned833.clone())?;
            let assigned834 = e.get("row")?.attr("centre")?;
            let unpack835 = unpack(assigned834.clone(), 2)?;
            e.set("cx", unpack835[0].clone())?;
            e.set("cy", unpack835[1].clone())?;
            if {
                let v836 = e.get("row")?.attr("closure")?;
                let v837 = Val::Str("cap".into());
                Val::Bool(compare("eq", v836.clone(), v837.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned838 = Val::Float(hsm_enclosure_interface::anchor_cap::rib_len());
                e.set("length", assigned838.clone())?;
                let assigned839 = binary(
                    "add",
                    Val::Float(hsm_enclosure_interface::anchor_cap::rib_r()),
                    if {
                        let fun842 = e.get("cap_anchor_slotted")?;
                        let mut args840 = Vec::new();
                        let mut kw841 = Vec::new();
                        args840.push(e.get("name")?);
                        fun842.call(args840, kw841)?
                    }
                    .truthy()?
                    {
                        Val::Float(hsm_enclosure_interface::anchor_cap::slot_w())
                    } else {
                        Val::Float(0.0f64)
                    },
                )?;
                e.set("reach", assigned839.clone())?;
            } else {
                let assigned843 = {
                    let mut s = Vec::new();
                    s.push(e.get("cap_anchor_len")?);
                    s.push(binary(
                        "add",
                        e.get("row")?.attr("seat_r")?,
                        e.get("cap_anchor_wall")?,
                    )?);
                    Val::tuple(s)
                };
                let unpack844 = unpack(assigned843.clone(), 2)?;
                e.set("length", unpack844[0].clone())?;
                e.set("reach", unpack844[1].clone())?;
            }
            let assigned845 = if {
                let v846 = e.get("row")?.attr("along")?;
                let v847 = Val::Str("x".into());
                Val::Bool(compare("eq", v846.clone(), v847.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let mut s = Vec::new();
                    s.push(binary("truediv", e.get("length")?, Val::Float(2.0f64))?);
                    s.push(e.get("reach")?);
                    Val::tuple(s)
                }
            } else {
                {
                    let mut s = Vec::new();
                    s.push(e.get("reach")?);
                    s.push(binary("truediv", e.get("length")?, Val::Float(2.0f64))?);
                    Val::tuple(s)
                }
            };
            let unpack848 = unpack(assigned845.clone(), 2)?;
            e.set("along", unpack848[0].clone())?;
            e.set("across", unpack848[1].clone())?;
            let assigned849 = {
                let mut s = Vec::new();
                s.push(binary("sub", e.get("cx")?, e.get("along")?)?);
                s.push(binary("add", e.get("cx")?, e.get("along")?)?);
                Val::tuple(s)
            };
            let unpack850 = unpack(assigned849.clone(), 2)?;
            e.set("x0", unpack850[0].clone())?;
            e.set("x1", unpack850[1].clone())?;
            let assigned851 = {
                let mut s = Vec::new();
                s.push(binary("sub", e.get("cy")?, e.get("across")?)?);
                s.push(binary("add", e.get("cy")?, e.get("across")?)?);
                Val::tuple(s)
            };
            let unpack852 = unpack(assigned851.clone(), 2)?;
            e.set("y0", unpack852[0].clone())?;
            e.set("y1", unpack852[1].clone())?;
            // off
            e.set("off", {
                let params = vec![
                    ("px".into(), None, false),
                    ("py".into(), None, false),
                    ("r".into(), None, false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned853 = {
                        let fun856 = e.get("max")?;
                        let mut args854 = Vec::new();
                        let mut kw855 = Vec::new();
                        args854.push(binary("sub", e.get("x0")?, e.get("px")?)?);
                        args854.push(Val::Float(0.0f64));
                        args854.push(binary("sub", e.get("px")?, e.get("x1")?)?);
                        fun856.call(args854, kw855)?
                    };
                    e.set("dx", assigned853.clone())?;
                    let assigned857 = {
                        let fun860 = e.get("max")?;
                        let mut args858 = Vec::new();
                        let mut kw859 = Vec::new();
                        args858.push(binary("sub", e.get("y0")?, e.get("py")?)?);
                        args858.push(Val::Float(0.0f64));
                        args858.push(binary("sub", e.get("py")?, e.get("y1")?)?);
                        fun860.call(args858, kw859)?
                    };
                    e.set("dy", assigned857.clone())?;
                    return Ok(binary(
                        "sub",
                        {
                            let fun863 = e.get("math")?.attr("hypot")?;
                            let mut args861 = Vec::new();
                            let mut kw862 = Vec::new();
                            args861.push(e.get("dx")?);
                            args861.push(e.get("dy")?);
                            fun863.call(args861, kw862)?
                        },
                        e.get("r")?,
                    )?);
                    Ok(Val::None)
                })
            })?;
            let assigned864 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("room", assigned864.clone())?;
            for item865 in {
                let fun875 = e.get("cap_conduits")?.attr("items")?;
                let mut args873 = Vec::new();
                let mut kw874 = Vec::new();
                fun875.call(args873, kw874)?
            }
            .iter()?
            {
                let unpack876 = unpack(item865, 2)?;
                e.set("cname", unpack876[0].clone())?;
                let unpack877 = unpack(unpack876[1].clone(), 2)?;
                e.set("bx", unpack877[0].clone())?;
                e.set("by", unpack877[1].clone())?;
                {
                    let fun868 = e.get("room")?.attr("append")?;
                    let mut args866 = Vec::new();
                    let mut kw867 = Vec::new();
                    args866.push({
                        let mut s = Vec::new();
                        s.push({
                            let fun871 = e.get("off")?;
                            let mut args869 = Vec::new();
                            let mut kw870 = Vec::new();
                            args869.push(e.get("bx")?);
                            args869.push(e.get("by")?);
                            args869.push(e.get("cap_conduit_entry_relief_radius")?);
                            fun871.call(args869, kw870)?
                        });
                        s.push({
                            let mut str872 = String::new();
                            str872.push_str("the ");
                            str872.push_str(&format(&e.get("cname")?, &String::new())?);
                            str872.push_str(" conduit's entry");
                            Val::Str(str872)
                        });
                        Val::tuple(s)
                    });
                    fun868.call(args866, kw867)?
                };
            }
            for item878 in e.get("lid_attachment_xy_positions")?.iter()? {
                let unpack885 = unpack(item878, 2)?;
                e.set("bx", unpack885[0].clone())?;
                e.set("by", unpack885[1].clone())?;
                {
                    let fun881 = e.get("room")?.attr("append")?;
                    let mut args879 = Vec::new();
                    let mut kw880 = Vec::new();
                    args879.push({
                        let mut s = Vec::new();
                        s.push({
                            let fun884 = e.get("off")?;
                            let mut args882 = Vec::new();
                            let mut kw883 = Vec::new();
                            args882.push(e.get("bx")?);
                            args882.push(e.get("by")?);
                            args882.push(e.get("head_cbore_radius")?);
                            fun884.call(args882, kw883)?
                        });
                        s.push(Val::Str("a clamp screw's counterbore".into()));
                        Val::tuple(s)
                    });
                    fun881.call(args879, kw880)?
                };
            }
            for item886 in e.get("deck_mounts")?.iter()? {
                e.set("dname", item886)?;
                for item887 in {
                    let fun900 = e.get("deck_mount_xy")?;
                    let mut args898 = Vec::new();
                    let mut kw899 = Vec::new();
                    args898.push(e.get("dname")?);
                    fun900.call(args898, kw899)?
                }
                .iter()?
                {
                    let unpack901 = unpack(item887, 2)?;
                    e.set("dx", unpack901[0].clone())?;
                    e.set("dy", unpack901[1].clone())?;
                    {
                        let fun890 = e.get("room")?.attr("append")?;
                        let mut args888 = Vec::new();
                        let mut kw889 = Vec::new();
                        args888.push({
                            let mut s = Vec::new();
                            s.push({
                                let fun893 = e.get("off")?;
                                let mut args891 = Vec::new();
                                let mut kw892 = Vec::new();
                                args891.push(e.get("dx")?);
                                args891.push(e.get("dy")?);
                                args891.push({
                                    let fun896 = e.get("deck_lid_hole_radius")?;
                                    let mut args894 = Vec::new();
                                    let mut kw895 = Vec::new();
                                    args894.push(e.get("dname")?);
                                    fun896.call(args894, kw895)?
                                });
                                fun893.call(args891, kw892)?
                            });
                            s.push({
                                let mut str897 = String::new();
                                str897.push_str("the ");
                                str897.push_str(&format(&e.get("dname")?, &String::new())?);
                                str897.push_str(" mount's lid hole");
                                Val::Str(str897)
                            });
                            Val::tuple(s)
                        });
                        fun890.call(args888, kw889)?
                    };
                }
            }
            for item902 in e.get("cap_cradles")?.iter()? {
                e.set("vname", item902)?;
                {
                    let fun905 = e.get("room")?.attr("append")?;
                    let mut args903 = Vec::new();
                    let mut kw904 = Vec::new();
                    args903.push({
                        let mut s = Vec::new();
                        s.push({
                            let fun908 = e.get("cap_cradle_rectangle_gap")?;
                            let mut args906 = Vec::new();
                            let mut kw907 = Vec::new();
                            args906.push(e.get("vname")?);
                            args906.push(e.get("x0")?);
                            args906.push(e.get("x1")?);
                            args906.push(e.get("y0")?);
                            args906.push(e.get("y1")?);
                            fun908.call(args906, kw907)?
                        });
                        s.push({
                            let mut str909 = String::new();
                            str909.push_str("the ");
                            str909.push_str(&format(&e.get("vname")?, &String::new())?);
                            str909.push_str(" plinth");
                            Val::Str(str909)
                        });
                        Val::tuple(s)
                    });
                    fun905.call(args903, kw904)?
                };
            }
            {
                let fun912 = e.get("room")?.attr("append")?;
                let mut args910 = Vec::new();
                let mut kw911 = Vec::new();
                args910.push({
                    let mut s = Vec::new();
                    s.push({
                        let fun915 = e.get("min")?;
                        let mut args913 = Vec::new();
                        let mut kw914 = Vec::new();
                        args913.push(binary(
                            "sub",
                            binary(
                                "truediv",
                                e.get("outer_shell_x_length")?,
                                Val::Float(2.0f64),
                            )?,
                            {
                                let fun918 = e.get("abs")?;
                                let mut args916 = Vec::new();
                                let mut kw917 = Vec::new();
                                args916.push(e.get("x0")?);
                                fun918.call(args916, kw917)?
                            },
                        )?);
                        args913.push(binary(
                            "sub",
                            binary(
                                "truediv",
                                e.get("outer_shell_x_length")?,
                                Val::Float(2.0f64),
                            )?,
                            {
                                let fun921 = e.get("abs")?;
                                let mut args919 = Vec::new();
                                let mut kw920 = Vec::new();
                                args919.push(e.get("x1")?);
                                fun921.call(args919, kw920)?
                            },
                        )?);
                        args913.push(binary(
                            "sub",
                            binary(
                                "truediv",
                                e.get("outer_shell_y_length")?,
                                Val::Float(2.0f64),
                            )?,
                            {
                                let fun924 = e.get("abs")?;
                                let mut args922 = Vec::new();
                                let mut kw923 = Vec::new();
                                args922.push(e.get("y0")?);
                                fun924.call(args922, kw923)?
                            },
                        )?);
                        args913.push(binary(
                            "sub",
                            binary(
                                "truediv",
                                e.get("outer_shell_y_length")?,
                                Val::Float(2.0f64),
                            )?,
                            {
                                let fun927 = e.get("abs")?;
                                let mut args925 = Vec::new();
                                let mut kw926 = Vec::new();
                                args925.push(e.get("y1")?);
                                fun927.call(args925, kw926)?
                            },
                        )?);
                        fun915.call(args913, kw914)?
                    });
                    s.push(Val::Str("the lid's own edge".into()));
                    Val::tuple(s)
                });
                fun912.call(args910, kw911)?
            };
            return Ok({
                let fun930 = e.get("min")?;
                let mut args928 = Vec::new();
                let mut kw929 = Vec::new();
                args928.push(e.get("room")?);
                fun930.call(args928, kw929)?
            });
            Ok(Val::None)
        })
    })?;
    let assigned931 = {
        let fun934 = e.get("bound")?;
        let mut args932 = Vec::new();
        let mut kw933 = Vec::new();
        args932.push(Val::Str("anchor-room".into()));
        args932.push(Val::Str(
            "Every chain anchor stands its room off everything else the face opens".into(),
        ));
        args932.push({
            let mut str935 = String::new();
            str935.push_str(&format(
                &e.get("cap_cradle_room_gap")?,
                &val_string({
                    let mut str936 = String::new();
                    str936.push_str("g");
                    Val::Str(str936)
                })?,
            )?);
            str935.push_str(" mm off the nearest");
            Val::Str(str935)
        });
        fun934.call(args932, kw933)?
    };
    e.set("_anchor_room", assigned931.clone())?;
    for item937 in e.get("cap_anchors")?.iter()? {
        e.set("_name", item937)?;
        let assigned938 = {
            let fun941 = e.get("cap_anchor_room")?;
            let mut args939 = Vec::new();
            let mut kw940 = Vec::new();
            args939.push(e.get("_name")?);
            fun941.call(args939, kw940)?
        };
        let unpack942 = unpack(assigned938.clone(), 2)?;
        e.set("_room", unpack942[0].clone())?;
        e.set("_what", unpack942[1].clone())?;
        {
            let fun945 = e.get("_anchor_room")?;
            let mut args943 = Vec::new();
            let mut kw944 = Vec::new();
            args943.push({
                let v946 = e.get("_room")?;
                let v947 = binary("sub", e.get("cap_cradle_room_gap")?, Val::Float(1e-09f64))?;
                Val::Bool(compare("ge", v946.clone(), v947.clone())?.truthy()?)
            });
            args943.push({
                let mut str948 = String::new();
                str948.push_str("chain anchor ");
                str948.push_str(&format(&e.get("_name")?, &String::new())?);
                str948.push_str(": the rib stands ");
                str948.push_str(&format(
                    &e.get("_room")?,
                    &val_string({
                        let mut str949 = String::new();
                        str949.push_str(".3f");
                        Val::Str(str949)
                    })?,
                )?);
                str948.push_str(" mm off ");
                str948.push_str(&format(&e.get("_what")?, &String::new())?);
                str948.push_str(", inside the ");
                str948.push_str(&format(
                    &e.get("cap_cradle_room_gap")?,
                    &val_string({
                        let mut str950 = String::new();
                        str950.push_str("g");
                        Val::Str(str950)
                    })?,
                )?);
                str948.push_str(" mm this face keeps between two things it opens");
                Val::Str(str948)
            });
            fun945.call(args943, kw944)?
        };
    }
    let assigned951 = {
        let fun954 = e.get("namedtuple")?;
        let mut args952 = Vec::new();
        let mut kw953 = Vec::new();
        args952.push(Val::Str("SideAnchor".into()));
        args952.push(Val::Str("centre over_face seat_r axis_off depth".into()));
        fun954.call(args952, kw953)?
    };
    e.set("SideAnchor", assigned951.clone())?;
    let assigned955 = e.get("cap_anchor_wall")?;
    e.set("cap_side_wall", assigned955.clone())?;
    let assigned956 = Val::Float(hsm_cold_core_interface::cap_side_len(&crate::interface::module_fits(&e.get("_interface_fits")?)?));
    e.set("cap_side_len", assigned956.clone())?;
    let assigned957 = Val::Float(hsm_cold_core_interface::cap_side_cav_w(&crate::interface::module_fits(&e.get("_interface_fits")?)?));
    e.set("cap_side_cav_w", assigned957.clone())?;
    let assigned958 = Val::Float(hsm_cold_core_interface::cap_side_flank(&crate::interface::module_fits(&e.get("_interface_fits")?)?));
    e.set("cap_side_flank", assigned958.clone())?;
    let assigned959 = Val::Float(hsm_cold_core_interface::CAP_SIDE_TIE_T);
    e.set("cap_side_tie_t", assigned959.clone())?;
    let assigned960 = e.get("cap_side_wall")?;
    e.set("cap_side_cav_h", assigned960.clone())?;
    let assigned961 = Val::Float(hsm_cold_core_interface::CAP_SIDE_CAV_BACKING_MIN);
    e.set("cap_side_cav_backing_min", assigned961.clone())?;
    let assigned962 = Val::Float(hsm_cold_core_interface::CAP_SIDE_BACK_RELIEF);
    e.set("cap_side_back_relief", assigned962.clone())?;
    let assigned963 = e.get("cap_side_wall")?;
    e.set("cap_side_web", assigned963.clone())?;
    let assigned964 = {
        let d = Val::dict(vec![]);
        d
    };
    e.set("cap_side_anchors", assigned964.clone())?;
    // cap_side_axis_y
    e.set("cap_side_axis_y", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned965 = e.get("cap_side_anchors")?.get(e.get("name")?)?;
            e.set("a", assigned965.clone())?;
            return Ok(binary(
                "add",
                e.get("a")?.attr("centre")?.get(Val::Int(0i64))?,
                e.get("a")?.attr("axis_off")?,
            )?);
            Ok(Val::None)
        })
    })?;
    // cap_side_wrap_deg
    e.set("cap_side_wrap_deg", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned966 = e.get("cap_side_anchors")?.get(e.get("name")?)?;
            e.set("a", assigned966.clone())?;
            return Ok(binary("mul", Val::Float(2.0f64), {
                let fun969 = e.get("math")?.attr("degrees")?;
                let mut args967 = Vec::new();
                let mut kw968 = Vec::new();
                args967.push({
                    let fun972 = e.get("math")?.attr("acos")?;
                    let mut args970 = Vec::new();
                    let mut kw971 = Vec::new();
                    args970.push(binary(
                        "truediv",
                        e.get("a")?.attr("axis_off")?,
                        e.get("a")?.attr("seat_r")?,
                    )?);
                    fun972.call(args970, kw971)?
                });
                fun969.call(args967, kw968)?
            })?);
            Ok(Val::None)
        })
    })?;
    // cap_side_tunnel_roof
    e.set("cap_side_tunnel_roof", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned973 = e.get("cap_side_anchors")?.get(e.get("name")?)?;
            e.set("a", assigned973.clone())?;
            return Ok(binary(
                "sub",
                binary(
                    "sub",
                    e.get("a")?.attr("over_face")?,
                    e.get("a")?.attr("seat_r")?,
                )?,
                e.get("cap_side_wall")?,
            )?);
            Ok(Val::None)
        })
    })?;
    // cap_side_tunnel_h
    e.set("cap_side_tunnel_h", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned974 = {
                let fun977 = e.get("cap_side_tunnel_roof")?;
                let mut args975 = Vec::new();
                let mut kw976 = Vec::new();
                args975.push(e.get("name")?);
                fun977.call(args975, kw976)?
            };
            e.set("roof", assigned974.clone())?;
            if {
                let v978 = binary("sub", e.get("roof")?, e.get("cap_side_cav_h")?)?;
                let v979 = binary(
                    "sub",
                    e.get("cap_side_cav_backing_min")?,
                    Val::Float(1e-09f64),
                )?;
                Val::Bool(compare("ge", v978.clone(), v979.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("cap_side_cav_h")?);
            }
            return Ok(e.get("roof")?);
            Ok(Val::None)
        })
    })?;
    // cap_side_anchor_height
    e.set("cap_side_anchor_height", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned980 = e.get("cap_side_anchors")?.get(e.get("name")?)?;
            e.set("a", assigned980.clone())?;
            return Ok(binary(
                "add",
                binary(
                    "add",
                    binary(
                        "add",
                        e.get("a")?.attr("over_face")?,
                        e.get("a")?.attr("seat_r")?,
                    )?,
                    e.get("fits")?.attr("supported_surface")?,
                )?,
                e.get("cap_side_wall")?,
            )?);
            Ok(Val::None)
        })
    })?;
    // cap_side_anchor_holds
    e.set("cap_side_anchor_holds",{let params=vec![("name".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned981=e.get("cap_side_anchors")?.get(e.get("name")?)?;e.set("a",assigned981.clone())?;
let assigned982={let fun985=e.get("cap_side_tunnel_roof")?;let mut args983=Vec::new();let mut kw984=Vec::new();args983.push(e.get("name")?);fun985.call(args983,kw984)?};e.set("roof",assigned982.clone())?;
if {let v986=e.get("roof")?;let v987=binary("sub",e.get("cap_side_tie_t")?,Val::Float(1e-09f64))?;Val::Bool(compare("lt",v986.clone(),v987.clone())?.truthy()?)}.truthy()? {
anyhow::bail!("{}",val_string({let fun990=e.get("ValueError")?;let mut args988=Vec::new();let mut kw989=Vec::new();args988.push({let mut str991=String::new();str991.push_str("cap_side_anchor_holds: ");str991.push_str(&format(&e.get("name")?,&String::new())?);str991.push_str(" runs ");str991.push_str(&format(&e.get("a")?.attr("over_face")?,&val_string({let mut str992=String::new();str992.push_str(".3f");Val::Str(str992)})?)?);str991.push_str(" mm over the lid's face; the pipe takes ");str991.push_str(&format(&e.get("a")?.attr("seat_r")?,&val_string({let mut str993=String::new();str993.push_str(".3f");Val::Str(str993)})?)?);str991.push_str(" of that and one wall ");str991.push_str(&format(&e.get("cap_side_wall")?,&val_string({let mut str994=String::new();str994.push_str(".3f");Val::Str(str994)})?)?);str991.push_str(" more, leaving ");str991.push_str(&format(&e.get("roof")?,&val_string({let mut str995=String::new();str995.push_str(".3f");Val::Str(str995)})?)?);str991.push_str(" mm under it where the zip tie is ");str991.push_str(&format(&e.get("cap_side_tie_t")?,&val_string({let mut str996=String::new();str996.push_str("g");Val::Str(str996)})?)?);str991.push_str(" thick. What gives way here is the run's own lane, not the lid: route it further off that face.");Val::Str(str991)});fun990.call(args988,kw989)?})?);
}
let assigned997=binary("sub",binary("sub",binary("add",e.get("a")?.attr("depth")?,e.get("a")?.attr("axis_off")?)?,e.get("a")?.attr("seat_r")?)?,e.get("cap_side_back_relief")?)?;e.set("web",assigned997.clone())?;
if {let v998=e.get("web")?;let v999=binary("sub",e.get("cap_side_web")?,Val::Float(1e-09f64))?;Val::Bool(compare("lt",v998.clone(),v999.clone())?.truthy()?)}.truthy()? {
anyhow::bail!("{}",val_string({let fun1002=e.get("ValueError")?;let mut args1000=Vec::new();let mut kw1001=Vec::new();args1000.push({let mut str1003=String::new();str1003.push_str("cap_side_anchor_holds: the post runs ");str1003.push_str(&format(&e.get("a")?.attr("depth")?,&val_string({let mut str1004=String::new();str1004.push_str(".3f");Val::Str(str1004)})?)?);str1003.push_str(" mm back from its face; the pipe takes ");str1003.push_str(&format(&binary("sub",e.get("a")?.attr("seat_r")?,e.get("a")?.attr("axis_off")?)?,&val_string({let mut str1005=String::new();str1005.push_str(".3f");Val::Str(str1005)})?)?);str1003.push_str(" of that and the tie's channel ");str1003.push_str(&format(&e.get("cap_side_back_relief")?,&val_string({let mut str1006=String::new();str1006.push_str("g");Val::Str(str1006)})?)?);str1003.push_str(" more, leaving a web of ");str1003.push_str(&format(&e.get("web")?,&val_string({let mut str1007=String::new();str1007.push_str(".3f");Val::Str(str1007)})?)?);str1003.push_str(" where this face wants ");str1003.push_str(&format(&e.get("cap_side_web")?,&val_string({let mut str1008=String::new();str1008.push_str("g");Val::Str(str1008)})?)?);str1003.push_str(". What caps the depth is the body behind the post, so what gives is the pipe or the lane — not the web.");Val::Str(str1003)});fun1002.call(args1000,kw1001)?})?);
}
Ok(Val::None)})})?;
    // cap_side_anchor_tie_loop
    e.set("cap_side_anchor_tie_loop", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1009 = e.get("cap_side_anchors")?.get(e.get("name")?)?;
            e.set("a", assigned1009.clone())?;
            let assigned1010 = binary("add", e.get("a")?.attr("seat_r")?, e.get("cap_side_wall")?)?;
            e.set("w", assigned1010.clone())?;
            let assigned1011 = {
                let fun1014 = e.get("cap_side_tunnel_h")?;
                let mut args1012 = Vec::new();
                let mut kw1013 = Vec::new();
                args1012.push(e.get("name")?);
                fun1014.call(args1012, kw1013)?
            };
            e.set("tun_h", assigned1011.clone())?;
            let assigned1015 = binary("add", e.get("tun_h")?, e.get("w")?)?;
            e.set("axis", assigned1015.clone())?;
            let assigned1016 = binary(
                "add",
                e.get("tun_h")?,
                binary("mul", Val::Float(2.0f64), e.get("w")?)?,
            )?;
            e.set("crown", assigned1016.clone())?;
            let assigned1017 = {
                let fun1020 = e.get("math")?.attr("hypot")?;
                let mut args1018 = Vec::new();
                let mut kw1019 = Vec::new();
                args1018.push(e.get("a")?.attr("axis_off")?);
                args1018.push(e.get("axis")?);
                fun1020.call(args1018, kw1019)?
            };
            e.set("d_lo", assigned1017.clone())?;
            let assigned1021 = {
                let fun1024 = e.get("math")?.attr("hypot")?;
                let mut args1022 = Vec::new();
                let mut kw1023 = Vec::new();
                args1022.push(e.get("a")?.attr("axis_off")?);
                args1022.push(binary("sub", e.get("crown")?, e.get("axis")?)?);
                fun1024.call(args1022, kw1023)?
            };
            e.set("d_hi", assigned1021.clone())?;
            let assigned1025 = binary(
                "mod",
                binary(
                    "sub",
                    {
                        let fun1028 = e.get("math")?.attr("atan2")?;
                        let mut args1026 = Vec::new();
                        let mut kw1027 = Vec::new();
                        args1026.push(binary("sub", e.get("crown")?, e.get("axis")?)?);
                        args1026.push(unary("neg", e.get("a")?.attr("axis_off")?)?);
                        fun1028.call(args1026, kw1027)?
                    },
                    {
                        let fun1031 = e.get("math")?.attr("atan2")?;
                        let mut args1029 = Vec::new();
                        let mut kw1030 = Vec::new();
                        args1029.push(unary("neg", e.get("axis")?)?);
                        args1029.push(unary("neg", e.get("a")?.attr("axis_off")?)?);
                        fun1031.call(args1029, kw1030)?
                    },
                )?,
                binary("mul", Val::Float(2.0f64), e.get("math")?.attr("pi")?)?,
            )?;
            e.set("sweep", assigned1025.clone())?;
            return Ok(binary(
                "add",
                binary(
                    "add",
                    binary(
                        "add",
                        binary(
                            "add",
                            binary("mul", Val::Float(2.0f64), e.get("a")?.attr("depth")?)?,
                            e.get("crown")?,
                        )?,
                        {
                            let fun1034 = e.get("math")?.attr("sqrt")?;
                            let mut args1032 = Vec::new();
                            let mut kw1033 = Vec::new();
                            args1032.push(binary(
                                "sub",
                                binary("mul", e.get("d_lo")?, e.get("d_lo")?)?,
                                binary(
                                    "mul",
                                    e.get("a")?.attr("seat_r")?,
                                    e.get("a")?.attr("seat_r")?,
                                )?,
                            )?);
                            fun1034.call(args1032, kw1033)?
                        },
                    )?,
                    {
                        let fun1037 = e.get("math")?.attr("sqrt")?;
                        let mut args1035 = Vec::new();
                        let mut kw1036 = Vec::new();
                        args1035.push(binary(
                            "sub",
                            binary("mul", e.get("d_hi")?, e.get("d_hi")?)?,
                            binary(
                                "mul",
                                e.get("a")?.attr("seat_r")?,
                                e.get("a")?.attr("seat_r")?,
                            )?,
                        )?);
                        fun1037.call(args1035, kw1036)?
                    },
                )?,
                binary(
                    "mul",
                    e.get("a")?.attr("seat_r")?,
                    binary(
                        "sub",
                        binary("sub", e.get("sweep")?, {
                            let fun1040 = e.get("math")?.attr("acos")?;
                            let mut args1038 = Vec::new();
                            let mut kw1039 = Vec::new();
                            args1038.push(binary(
                                "truediv",
                                e.get("a")?.attr("seat_r")?,
                                e.get("d_lo")?,
                            )?);
                            fun1040.call(args1038, kw1039)?
                        })?,
                        {
                            let fun1043 = e.get("math")?.attr("acos")?;
                            let mut args1041 = Vec::new();
                            let mut kw1042 = Vec::new();
                            args1041.push(binary(
                                "truediv",
                                e.get("a")?.attr("seat_r")?,
                                e.get("d_hi")?,
                            )?);
                            fun1043.call(args1041, kw1042)?
                        },
                    )?,
                )?,
            )?);
            Ok(Val::None)
        })
    })?;
    // cap_side_anchor_room
    e.set("cap_side_anchor_room", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1044 = e.get("cap_side_anchors")?.get(e.get("name")?)?;
            e.set("a", assigned1044.clone())?;
            let assigned1045 = e.get("a")?.attr("centre")?;
            let unpack1046 = unpack(assigned1045.clone(), 2)?;
            e.set("cx", unpack1046[0].clone())?;
            e.set("cy", unpack1046[1].clone())?;
            let assigned1047 = {
                let mut s = Vec::new();
                s.push(binary("sub", e.get("cx")?, e.get("a")?.attr("depth")?)?);
                s.push(e.get("cx")?);
                Val::tuple(s)
            };
            let unpack1048 = unpack(assigned1047.clone(), 2)?;
            e.set("x0", unpack1048[0].clone())?;
            e.set("x1", unpack1048[1].clone())?;
            let assigned1049 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("cy")?,
                    binary("truediv", e.get("cap_side_len")?, Val::Float(2.0f64))?,
                )?);
                s.push(binary(
                    "add",
                    e.get("cy")?,
                    binary("truediv", e.get("cap_side_len")?, Val::Float(2.0f64))?,
                )?);
                Val::tuple(s)
            };
            let unpack1050 = unpack(assigned1049.clone(), 2)?;
            e.set("y0", unpack1050[0].clone())?;
            e.set("y1", unpack1050[1].clone())?;
            // off
            e.set("off", {
                let params = vec![
                    ("px".into(), None, false),
                    ("py".into(), None, false),
                    ("r".into(), None, false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned1051 = {
                        let fun1054 = e.get("max")?;
                        let mut args1052 = Vec::new();
                        let mut kw1053 = Vec::new();
                        args1052.push(binary("sub", e.get("x0")?, e.get("px")?)?);
                        args1052.push(Val::Float(0.0f64));
                        args1052.push(binary("sub", e.get("px")?, e.get("x1")?)?);
                        fun1054.call(args1052, kw1053)?
                    };
                    e.set("dx", assigned1051.clone())?;
                    let assigned1055 = {
                        let fun1058 = e.get("max")?;
                        let mut args1056 = Vec::new();
                        let mut kw1057 = Vec::new();
                        args1056.push(binary("sub", e.get("y0")?, e.get("py")?)?);
                        args1056.push(Val::Float(0.0f64));
                        args1056.push(binary("sub", e.get("py")?, e.get("y1")?)?);
                        fun1058.call(args1056, kw1057)?
                    };
                    e.set("dy", assigned1055.clone())?;
                    return Ok(binary(
                        "sub",
                        {
                            let fun1061 = e.get("math")?.attr("hypot")?;
                            let mut args1059 = Vec::new();
                            let mut kw1060 = Vec::new();
                            args1059.push(e.get("dx")?);
                            args1059.push(e.get("dy")?);
                            fun1061.call(args1059, kw1060)?
                        },
                        e.get("r")?,
                    )?);
                    Ok(Val::None)
                })
            })?;
            let assigned1062 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("room", assigned1062.clone())?;
            for item1063 in e.get("lid_attachment_xy_positions")?.iter()? {
                let unpack1070 = unpack(item1063, 2)?;
                e.set("bx", unpack1070[0].clone())?;
                e.set("by", unpack1070[1].clone())?;
                {
                    let fun1066 = e.get("room")?.attr("append")?;
                    let mut args1064 = Vec::new();
                    let mut kw1065 = Vec::new();
                    args1064.push({
                        let mut s = Vec::new();
                        s.push({
                            let fun1069 = e.get("off")?;
                            let mut args1067 = Vec::new();
                            let mut kw1068 = Vec::new();
                            args1067.push(e.get("bx")?);
                            args1067.push(e.get("by")?);
                            args1067.push(e.get("head_cbore_radius")?);
                            fun1069.call(args1067, kw1068)?
                        });
                        s.push(Val::Str("a clamp screw's counterbore".into()));
                        Val::tuple(s)
                    });
                    fun1066.call(args1064, kw1065)?
                };
            }
            for item1071 in {
                let fun1081 = e.get("cap_conduits")?.attr("items")?;
                let mut args1079 = Vec::new();
                let mut kw1080 = Vec::new();
                fun1081.call(args1079, kw1080)?
            }
            .iter()?
            {
                let unpack1082 = unpack(item1071, 2)?;
                e.set("cname", unpack1082[0].clone())?;
                let unpack1083 = unpack(unpack1082[1].clone(), 2)?;
                e.set("bx", unpack1083[0].clone())?;
                e.set("by", unpack1083[1].clone())?;
                {
                    let fun1074 = e.get("room")?.attr("append")?;
                    let mut args1072 = Vec::new();
                    let mut kw1073 = Vec::new();
                    args1072.push({
                        let mut s = Vec::new();
                        s.push({
                            let fun1077 = e.get("off")?;
                            let mut args1075 = Vec::new();
                            let mut kw1076 = Vec::new();
                            args1075.push(e.get("bx")?);
                            args1075.push(e.get("by")?);
                            args1075.push(e.get("cap_conduit_entry_relief_radius")?);
                            fun1077.call(args1075, kw1076)?
                        });
                        s.push({
                            let mut str1078 = String::new();
                            str1078.push_str("the ");
                            str1078.push_str(&format(&e.get("cname")?, &String::new())?);
                            str1078.push_str(" conduit's entry");
                            Val::Str(str1078)
                        });
                        Val::tuple(s)
                    });
                    fun1074.call(args1072, kw1073)?
                };
            }
            for item1084 in e.get("deck_mounts")?.iter()? {
                e.set("dname", item1084)?;
                for item1085 in {
                    let fun1098 = e.get("deck_mount_xy")?;
                    let mut args1096 = Vec::new();
                    let mut kw1097 = Vec::new();
                    args1096.push(e.get("dname")?);
                    fun1098.call(args1096, kw1097)?
                }
                .iter()?
                {
                    let unpack1099 = unpack(item1085, 2)?;
                    e.set("dx", unpack1099[0].clone())?;
                    e.set("dy", unpack1099[1].clone())?;
                    {
                        let fun1088 = e.get("room")?.attr("append")?;
                        let mut args1086 = Vec::new();
                        let mut kw1087 = Vec::new();
                        args1086.push({
                            let mut s = Vec::new();
                            s.push({
                                let fun1091 = e.get("off")?;
                                let mut args1089 = Vec::new();
                                let mut kw1090 = Vec::new();
                                args1089.push(e.get("dx")?);
                                args1089.push(e.get("dy")?);
                                args1089.push({
                                    let fun1094 = e.get("deck_lid_hole_radius")?;
                                    let mut args1092 = Vec::new();
                                    let mut kw1093 = Vec::new();
                                    args1092.push(e.get("dname")?);
                                    fun1094.call(args1092, kw1093)?
                                });
                                fun1091.call(args1089, kw1090)?
                            });
                            s.push({
                                let mut str1095 = String::new();
                                str1095.push_str("the ");
                                str1095.push_str(&format(&e.get("dname")?, &String::new())?);
                                str1095.push_str(" mount's lid hole");
                                Val::Str(str1095)
                            });
                            Val::tuple(s)
                        });
                        fun1088.call(args1086, kw1087)?
                    };
                }
            }
            for item1100 in e.get("cap_cradles")?.iter()? {
                e.set("vname", item1100)?;
                {
                    let fun1103 = e.get("room")?.attr("append")?;
                    let mut args1101 = Vec::new();
                    let mut kw1102 = Vec::new();
                    args1101.push({
                        let mut s = Vec::new();
                        s.push({
                            let fun1106 = e.get("cap_cradle_rectangle_gap")?;
                            let mut args1104 = Vec::new();
                            let mut kw1105 = Vec::new();
                            args1104.push(e.get("vname")?);
                            args1104.push(e.get("x0")?);
                            args1104.push(e.get("x1")?);
                            args1104.push(e.get("y0")?);
                            args1104.push(e.get("y1")?);
                            fun1106.call(args1104, kw1105)?
                        });
                        s.push({
                            let mut str1107 = String::new();
                            str1107.push_str("the ");
                            str1107.push_str(&format(&e.get("vname")?, &String::new())?);
                            str1107.push_str(" plinth");
                            Val::Str(str1107)
                        });
                        Val::tuple(s)
                    });
                    fun1103.call(args1101, kw1102)?
                };
            }
            for item1108 in e.get("cap_anchors")?.iter()? {
                e.set("aname", item1108)?;
                {
                    let fun1111 = e.get("room")?.attr("append")?;
                    let mut args1109 = Vec::new();
                    let mut kw1110 = Vec::new();
                    args1109.push({
                        let mut s = Vec::new();
                        s.push({
                            let fun1114 = e.get("off")?;
                            let mut args1112 = Vec::new();
                            let mut kw1113 = Vec::new();
                            args1112.extend(
                                e.get("cap_anchors")?
                                    .get(e.get("aname")?)?
                                    .attr("centre")?
                                    .iter()?,
                            );
                            args1112.push(binary(
                                "add",
                                e.get("cap_anchors")?.get(e.get("aname")?)?.attr("seat_r")?,
                                e.get("cap_anchor_wall")?,
                            )?);
                            fun1114.call(args1112, kw1113)?
                        });
                        s.push({
                            let mut str1115 = String::new();
                            str1115.push_str("the ");
                            str1115.push_str(&format(&e.get("aname")?, &String::new())?);
                            str1115.push_str(" rib");
                            Val::Str(str1115)
                        });
                        Val::tuple(s)
                    });
                    fun1111.call(args1109, kw1110)?
                };
            }
            return Ok({
                let fun1118 = e.get("min")?;
                let mut args1116 = Vec::new();
                let mut kw1117 = Vec::new();
                args1116.push(e.get("room")?);
                fun1118.call(args1116, kw1117)?
            });
            Ok(Val::None)
        })
    })?;
    let assigned1119 = {
        let fun1122 = e.get("bound")?;
        let mut args1120 = Vec::new();
        let mut kw1121 = Vec::new();
        args1120.push(Val::Str("cap-side-anchor-room".into()));
        args1120.push(Val::Str(
            "Every side post stands clear of what the lid's face opens".into(),
        ));
        args1120.push({
            let mut str1123 = String::new();
            str1123.push_str(&format(
                &e.get("cap_cradle_room_gap")?,
                &val_string({
                    let mut str1124 = String::new();
                    str1124.push_str("g");
                    Val::Str(str1124)
                })?,
            )?);
            str1123.push_str(" mm off the nearest");
            Val::Str(str1123)
        });
        fun1122.call(args1120, kw1121)?
    };
    e.set("_side_anchor_room", assigned1119.clone())?;
    for item1125 in e.get("cap_side_anchors")?.iter()? {
        e.set("_name", item1125)?;
        let assigned1126 = {
            let fun1129 = e.get("cap_side_anchor_room")?;
            let mut args1127 = Vec::new();
            let mut kw1128 = Vec::new();
            args1127.push(e.get("_name")?);
            fun1129.call(args1127, kw1128)?
        };
        let unpack1130 = unpack(assigned1126.clone(), 2)?;
        e.set("_room", unpack1130[0].clone())?;
        e.set("_what", unpack1130[1].clone())?;
        {
            let fun1133 = e.get("_side_anchor_room")?;
            let mut args1131 = Vec::new();
            let mut kw1132 = Vec::new();
            args1131.push({
                let v1134 = e.get("_room")?;
                let v1135 = binary("sub", e.get("cap_cradle_room_gap")?, Val::Float(1e-09f64))?;
                Val::Bool(compare("ge", v1134.clone(), v1135.clone())?.truthy()?)
            });
            args1131.push({let mut str1136=String::new();str1136.push_str("cap side anchor ");str1136.push_str(&format(&e.get("_name")?,&String::new())?);str1136.push_str(": its post stands ");str1136.push_str(&format(&e.get("_room")?,&val_string({let mut str1137=String::new();str1137.push_str(".3f");Val::Str(str1137)})?)?);str1136.push_str(" mm off ");str1136.push_str(&format(&e.get("_what")?,&String::new())?);str1136.push_str(", inside the ");str1136.push_str(&format(&e.get("cap_cradle_room_gap")?,&val_string({let mut str1138=String::new();str1138.push_str("g");Val::Str(str1138)})?)?);str1136.push_str(" mm this face keeps between two things it opens — a post over one of them is a body no plate reads as fouled");Val::Str(str1136)});
            fun1133.call(args1131, kw1132)?
        };
    }
    // cap_conduit_pair_neck
    e.set("cap_conduit_pair_neck", {
        let params = vec![("a".into(), None, false), ("b".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1139 = {
                let fun1142 = e.get("frozenset")?;
                let mut args1140 = Vec::new();
                let mut kw1141 = Vec::new();
                args1140.push({
                    let mut s = Vec::new();
                    s.push({
                        let fun1145 = e.get("tuple")?;
                        let mut args1143 = Vec::new();
                        let mut kw1144 = Vec::new();
                        args1143.push(e.get("a")?);
                        fun1145.call(args1143, kw1144)?
                    });
                    s.push({
                        let fun1148 = e.get("tuple")?;
                        let mut args1146 = Vec::new();
                        let mut kw1147 = Vec::new();
                        args1146.push(e.get("b")?);
                        fun1148.call(args1146, kw1147)?
                    });
                    Val::tuple(s)
                });
                fun1142.call(args1140, kw1141)?
            };
            e.set("pair", assigned1139.clone())?;
            for item1149 in e.get("cap_conduit_links")?.iter()? {
                let unpack1155 = unpack(item1149, 2)?;
                e.set("first", unpack1155[0].clone())?;
                e.set("second", unpack1155[1].clone())?;
                if {
                    let v1153 = e.get("pair")?;
                    let v1154 = {
                        let fun1152 = e.get("frozenset")?;
                        let mut args1150 = Vec::new();
                        let mut kw1151 = Vec::new();
                        args1150.push({
                            let mut s = Vec::new();
                            s.push(e.get("cap_conduits")?.get(e.get("first")?)?);
                            s.push(e.get("cap_conduits")?.get(e.get("second")?)?);
                            Val::tuple(s)
                        });
                        fun1152.call(args1150, kw1151)?
                    };
                    Val::Bool(compare("eq", v1153.clone(), v1154.clone())?.truthy()?)
                }
                .truthy()?
                {
                    return Ok({
                        let mut s = Vec::new();
                        s.push(e.get("cap_conduit_link_width")?);
                        s.push(Val::Str("the connecting web".into()));
                        Val::tuple(s)
                    });
                }
            }
            let assigned1156 = e.get("cap_conduit_boss_radius")?;
            e.set("r", assigned1156.clone())?;
            let assigned1157 = {
                let fun1160 = e.get("math")?.attr("hypot")?;
                let mut args1158 = Vec::new();
                let mut kw1159 = Vec::new();
                args1158.push(binary(
                    "sub",
                    e.get("a")?.get(Val::Int(0i64))?,
                    e.get("b")?.get(Val::Int(0i64))?,
                )?);
                args1158.push(binary(
                    "sub",
                    e.get("a")?.get(Val::Int(1i64))?,
                    e.get("b")?.get(Val::Int(1i64))?,
                )?);
                fun1160.call(args1158, kw1159)?
            };
            e.set("d", assigned1157.clone())?;
            if {
                let v1161 = e.get("d")?;
                let v1162 = binary("mul", Val::Float(2.0f64), e.get("r")?)?;
                Val::Bool(compare("ge", v1161.clone(), v1162.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok({
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        e.get("d")?,
                        binary("mul", Val::Float(2.0f64), e.get("r")?)?,
                    )?);
                    s.push(Val::Str("the pour gap between two standing columns".into()));
                    Val::tuple(s)
                });
            }
            return Ok({
                let mut s = Vec::new();
                s.push(binary("mul", Val::Float(2.0f64), {
                    let fun1165 = e.get("math")?.attr("sqrt")?;
                    let mut args1163 = Vec::new();
                    let mut kw1164 = Vec::new();
                    args1163.push({
                        let fun1168 = e.get("max")?;
                        let mut args1166 = Vec::new();
                        let mut kw1167 = Vec::new();
                        args1166.push(binary(
                            "sub",
                            binary("mul", e.get("r")?, e.get("r")?)?,
                            binary(
                                "pow",
                                binary("truediv", e.get("d")?, Val::Float(2.0f64))?,
                                Val::Int(2i64),
                            )?,
                        )?);
                        args1166.push(Val::Float(0.0f64));
                        fun1168.call(args1166, kw1167)?
                    });
                    fun1165.call(args1163, kw1164)?
                })?);
                s.push(Val::Str("the neck their lens leaves".into()));
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    let assigned1169 = {
        let fun1172 = e.get("bound")?;
        let mut args1170 = Vec::new();
        let mut kw1171 = Vec::new();
        args1170.push(Val::Str("cap-conduit-pair".into()));
        args1170.push(Val::Str(
            "Every pair of conduits stands apart or merges on a neck, never tangent".into(),
        ));
        args1170.push({
            let mut str1173 = String::new();
            str1173.push_str("the pour gap apart or a ");
            str1173.push_str(&format(
                &e.get("cap_conduit_wall")?,
                &val_string({
                    let mut str1174 = String::new();
                    str1174.push_str("g");
                    Val::Str(str1174)
                })?,
            )?);
            str1173.push_str(" mm neck");
            Val::Str(str1173)
        });
        fun1172.call(args1170, kw1171)?
    };
    e.set("_pair_neck", assigned1169.clone())?;
    for item1175 in {
        let fun1195 = e.get("itertools")?.attr("combinations")?;
        let mut args1193 = Vec::new();
        let mut kw1194 = Vec::new();
        args1193.push({
            let fun1198 = e.get("sorted")?;
            let mut args1196 = Vec::new();
            let mut kw1197 = Vec::new();
            args1196.push(e.get("cap_conduits")?);
            fun1198.call(args1196, kw1197)?
        });
        args1193.push(Val::Int(2i64));
        fun1195.call(args1193, kw1194)?
    }
    .iter()?
    {
        let unpack1199 = unpack(item1175, 2)?;
        e.set("_a", unpack1199[0].clone())?;
        e.set("_b", unpack1199[1].clone())?;
        let assigned1176 = {
            let fun1179 = e.get("cap_conduit_pair_neck")?;
            let mut args1177 = Vec::new();
            let mut kw1178 = Vec::new();
            args1177.push(e.get("cap_conduits")?.get(e.get("_a")?)?);
            args1177.push(e.get("cap_conduits")?.get(e.get("_b")?)?);
            fun1179.call(args1177, kw1178)?
        };
        let unpack1180 = unpack(assigned1176.clone(), 2)?;
        e.set("_neck", unpack1180[0].clone())?;
        e.set("_what", unpack1180[1].clone())?;
        let assigned1181 = if {
            let fun1184 = e.get("_what")?.attr("startswith")?;
            let mut args1182 = Vec::new();
            let mut kw1183 = Vec::new();
            args1182.push(Val::Str("the pour".into()));
            fun1184.call(args1182, kw1183)?
        }
        .truthy()?
        {
            e.get("deck_mount_cap_gap")?
        } else {
            e.get("cap_conduit_wall")?
        };
        e.set("_want", assigned1181.clone())?;
        {
            let fun1187 = e.get("_pair_neck")?;
            let mut args1185 = Vec::new();
            let mut kw1186 = Vec::new();
            args1185.push({
                let v1188 = e.get("_neck")?;
                let v1189 = binary("sub", e.get("_want")?, Val::Float(1e-09f64))?;
                Val::Bool(compare("ge", v1188.clone(), v1189.clone())?.truthy()?)
            });
            args1185.push({let mut str1190=String::new();str1190.push_str("cap conduits ");str1190.push_str(&format(&e.get("_a")?,&String::new())?);str1190.push_str(" and ");str1190.push_str(&format(&e.get("_b")?,&String::new())?);str1190.push_str(": ");str1190.push_str(&format(&e.get("_what")?,&String::new())?);str1190.push_str(" is ");str1190.push_str(&format(&e.get("_neck")?,&val_string({let mut str1191=String::new();str1191.push_str(".3f");Val::Str(str1191)})?)?);str1190.push_str(" mm, under the ");str1190.push_str(&format(&e.get("_want")?,&val_string({let mut str1192=String::new();str1192.push_str("g");Val::Str(str1192)})?)?);str1190.push_str(" mm it takes — a pair either stands the pour gap apart or merges on a neck a wall thick");Val::Str(str1190)});
            fun1187.call(args1185, kw1186)?
        };
    }
    // cap_conduit_shell_xy
    e.set("cap_conduit_shell_xy", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1200 = e.get("cap_conduits")?.get(e.get("name")?)?;
            let unpack1201 = unpack(assigned1200.clone(), 2)?;
            e.set("x", unpack1201[0].clone())?;
            e.set("y", unpack1201[1].clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(unary("neg", e.get("x")?)?);
                s.push(unary("neg", e.get("y")?)?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    let assigned1202 = {
        let mut s = Vec::new();
        s.push(Val::Float(0.0f64));
        s.push(Val::Float(0.0f64));
        s.push(Val::Float(1.0f64));
        Val::tuple(s)
    };
    e.set("cap_conduit_axis", assigned1202.clone())?;
    // cap_conduit_station
    e.set("cap_conduit_station", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1203 = e.get("cap_conduits")?.get(e.get("name")?)?;
            let unpack1204 = unpack(assigned1203.clone(), 2)?;
            e.set("x", unpack1204[0].clone())?;
            e.set("y", unpack1204[1].clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y")?);
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                });
                s.push(e.get("cap_conduit_axis")?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // make_box
    e.set("make_box", {
        let params = vec![
            ("x_range".into(), None, false),
            ("y_range".into(), None, false),
            ("z_range".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod1205 = rt.import_module("world_workplane")?;
            e.set(
                "xy_plane_z_up",
                rt.member("world_workplane", "xy_plane_z_up")?,
            )?;
            e.set(
                "WorldWorkplane",
                rt.member("world_workplane", "WorldWorkplane")?,
            )?;
            let assigned1206 = {
                let mut s = Vec::new();
                s.push({
                    let fun1209 = e.get("min")?;
                    let mut args1207 = Vec::new();
                    let mut kw1208 = Vec::new();
                    args1207.push(e.get("x_range")?);
                    fun1209.call(args1207, kw1208)?
                });
                s.push({
                    let fun1212 = e.get("max")?;
                    let mut args1210 = Vec::new();
                    let mut kw1211 = Vec::new();
                    args1210.push(e.get("x_range")?);
                    fun1212.call(args1210, kw1211)?
                });
                Val::tuple(s)
            };
            let unpack1213 = unpack(assigned1206.clone(), 2)?;
            e.set("x_min", unpack1213[0].clone())?;
            e.set("x_max", unpack1213[1].clone())?;
            let assigned1214 = {
                let mut s = Vec::new();
                s.push({
                    let fun1217 = e.get("min")?;
                    let mut args1215 = Vec::new();
                    let mut kw1216 = Vec::new();
                    args1215.push(e.get("y_range")?);
                    fun1217.call(args1215, kw1216)?
                });
                s.push({
                    let fun1220 = e.get("max")?;
                    let mut args1218 = Vec::new();
                    let mut kw1219 = Vec::new();
                    args1218.push(e.get("y_range")?);
                    fun1220.call(args1218, kw1219)?
                });
                Val::tuple(s)
            };
            let unpack1221 = unpack(assigned1214.clone(), 2)?;
            e.set("y_min", unpack1221[0].clone())?;
            e.set("y_max", unpack1221[1].clone())?;
            let assigned1222 = {
                let mut s = Vec::new();
                s.push({
                    let fun1225 = e.get("min")?;
                    let mut args1223 = Vec::new();
                    let mut kw1224 = Vec::new();
                    args1223.push(e.get("z_range")?);
                    fun1225.call(args1223, kw1224)?
                });
                s.push({
                    let fun1228 = e.get("max")?;
                    let mut args1226 = Vec::new();
                    let mut kw1227 = Vec::new();
                    args1226.push(e.get("z_range")?);
                    fun1228.call(args1226, kw1227)?
                });
                Val::tuple(s)
            };
            let unpack1229 = unpack(assigned1222.clone(), 2)?;
            e.set("z_min", unpack1229[0].clone())?;
            e.set("z_max", unpack1229[1].clone())?;
            return Ok({
                let fun1232 = {
                    let fun1235 = {
                        let fun1238 = {
                            let fun1241 = {
                                let fun1244 = {
                                    let fun1247 = e.get("WorldWorkplane")?;
                                    let mut args1245 = Vec::new();
                                    let mut kw1246 = Vec::new();
                                    args1245.push(e.get("xy_plane_z_up")?);
                                    fun1247.call(args1245, kw1246)?
                                }
                                .attr("workplane")?;
                                let mut args1242 = Vec::new();
                                let mut kw1243 = Vec::new();
                                kw1243.push(("offset".into(), e.get("z_min")?));
                                fun1244.call(args1242, kw1243)?
                            }
                            .attr("moveTo")?;
                            let mut args1239 = Vec::new();
                            let mut kw1240 = Vec::new();
                            args1239.push({
                                let mut s = Vec::new();
                                s.push(binary(
                                    "truediv",
                                    binary("add", e.get("x_min")?, e.get("x_max")?)?,
                                    Val::Int(2i64),
                                )?);
                                s.push(binary(
                                    "truediv",
                                    binary("add", e.get("y_min")?, e.get("y_max")?)?,
                                    Val::Int(2i64),
                                )?);
                                Val::tuple(s)
                            });
                            fun1241.call(args1239, kw1240)?
                        }
                        .attr("rect")?;
                        let mut args1236 = Vec::new();
                        let mut kw1237 = Vec::new();
                        args1236.push(binary("sub", e.get("x_max")?, e.get("x_min")?)?);
                        args1236.push(binary("sub", e.get("y_max")?, e.get("y_min")?)?);
                        fun1238.call(args1236, kw1237)?
                    }
                    .attr("extrude")?;
                    let mut args1233 = Vec::new();
                    let mut kw1234 = Vec::new();
                    args1233.push(binary("sub", e.get("z_max")?, e.get("z_min")?)?);
                    fun1235.call(args1233, kw1234)?
                }
                .attr("unwrap")?;
                let mut args1230 = Vec::new();
                let mut kw1231 = Vec::new();
                fun1232.call(args1230, kw1231)?
            });
            Ok(Val::None)
        })
    })?;
    // build_z_axis_hole_punch
    e.set("build_z_axis_hole_punch", {
        let params = vec![
            (
                "origin".into(),
                Some({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                }),
                true,
            ),
            ("hole_punch_radius".into(), None, true),
            ("hole_punch_height".into(), Some(Val::Int(40i64)), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let mod1248 = rt.import_module("world_workplane")?;
            e.set(
                "xy_plane_z_up",
                rt.member("world_workplane", "xy_plane_z_up")?,
            )?;
            let assigned1249 = e.get("origin")?;
            let unpack1250 = unpack(assigned1249.clone(), 3)?;
            e.set("x", unpack1250[0].clone())?;
            e.set("y", unpack1250[1].clone())?;
            e.set("z", unpack1250[2].clone())?;
            return Ok({
                let fun1253 = {
                    let fun1256 = {
                        let fun1259 = {
                            let fun1262 = e.get("cq")?.attr("Workplane")?;
                            let mut args1260 = Vec::new();
                            let mut kw1261 = Vec::new();
                            args1260.push(e.get("xy_plane_z_up")?);
                            fun1262.call(args1260, kw1261)?
                        }
                        .attr("workplane")?;
                        let mut args1257 = Vec::new();
                        let mut kw1258 = Vec::new();
                        kw1258.push(("origin".into(), {
                            let mut s = Vec::new();
                            s.push(e.get("x")?);
                            s.push(e.get("y")?);
                            s.push(Val::Int(0i64));
                            Val::tuple(s)
                        }));
                        kw1258.push(("offset".into(), e.get("z")?));
                        fun1259.call(args1257, kw1258)?
                    }
                    .attr("circle")?;
                    let mut args1254 = Vec::new();
                    let mut kw1255 = Vec::new();
                    args1254.push(e.get("hole_punch_radius")?);
                    fun1256.call(args1254, kw1255)?
                }
                .attr("extrude")?;
                let mut args1251 = Vec::new();
                let mut kw1252 = Vec::new();
                args1251.push(e.get("hole_punch_height")?);
                fun1253.call(args1251, kw1252)?
            });
            Ok(Val::None)
        })
    })?;
    // __getattr__
    e.set("__getattr__", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v1263 = e.get("name")?;
                let v1264 = Val::Str("cq".into());
                Val::Bool(compare("eq", v1263.clone(), v1264.clone())?.truthy()?)
            }
            .truthy()?
            {
                e.set("cadquery", rt.import_module("cadquery")?)?;
                return Ok(e.get("cadquery")?);
            }
            if {
                let v1265 = e.get("name")?;
                let v1266 = {
                    let mut s = Vec::new();
                    s.push(Val::Str("xy_plane_z_up".into()));
                    s.push(Val::Str("xz_plane_y_up".into()));
                    s.push(Val::Str("xz_plane_y_down".into()));
                    s.push(Val::Str("WorldWorkplane".into()));
                    Val::set_values(s)
                };
                Val::Bool(compare("in", v1265.clone(), v1266.clone())?.truthy()?)
            }
            .truthy()?
            {
                e.set("world_workplane", rt.import_module("world_workplane")?)?;
                return Ok({
                    let fun1269 = e.get("getattr")?;
                    let mut args1267 = Vec::new();
                    let mut kw1268 = Vec::new();
                    args1267.push(e.get("world_workplane")?);
                    args1267.push(e.get("name")?);
                    fun1269.call(args1267, kw1268)?
                });
            }
            anyhow::bail!(
                "{}",
                val_string({
                    let fun1272 = e.get("AttributeError")?;
                    let mut args1270 = Vec::new();
                    let mut kw1271 = Vec::new();
                    args1270.push({
                        let mut str1273 = String::new();
                        str1273.push_str("module ");
                        str1273.push_str(&format(
                            &builtin_call("repr", vec![e.get("__name__")?], vec![])?,
                            &String::new(),
                        )?);
                        str1273.push_str(" has no attribute ");
                        str1273.push_str(&format(
                            &builtin_call("repr", vec![e.get("name")?], vec![])?,
                            &String::new(),
                        )?);
                        Val::Str(str1273)
                    });
                    fun1272.call(args1270, kw1271)?
                })?
            );
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun1276 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args1274 = Vec::new();
        let mut kw1275 = Vec::new();
        args1274.push(Val::Int(0i64));
        args1274.push({
            let fun1279 = e.get("str")?;
            let mut args1277 = Vec::new();
            let mut kw1278 = Vec::new();
            args1277.push(binary(
                "truediv",
                {
                    let fun1282 = e.get("next")?;
                    let mut args1280 = Vec::new();
                    let mut kw1281 = Vec::new();
                    args1280.push({
                        let e = e.child();
                        let out1283 = Val::list(vec![]);
                        for item1284 in e.get("_here")?.attr("parents")?.iter()? {
                            e.set("p", item1284)?;
                            if {
                                let fun1287 = binary(
                                    "truediv",
                                    binary("truediv", e.get("p")?, Val::Str("tools".into()))?,
                                    Val::Str("docgen".into()),
                                )?
                                .attr("is_dir")?;
                                let mut args1285 = Vec::new();
                                let mut kw1286 = Vec::new();
                                fun1287.call(args1285, kw1286)?
                            }
                            .truthy()?
                            {
                                out1283.attr("append")?.call(vec![e.get("p")?], vec![])?;
                            }
                        }
                        out1283
                    });
                    fun1282.call(args1280, kw1281)?
                },
                Val::Str("tools".into()),
            )?);
            fun1279.call(args1277, kw1278)?
        });
        fun1276.call(args1274, kw1275)?
    };
    Ok(Val::None)
}
