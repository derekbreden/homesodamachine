//! Guide recipe: `hardware/install-guide/_install_art_mesh.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("json", rt.import_module("json")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("struct", rt.import_module("struct")?)?;
    e.set("_mesh_payload", rt.import_module("_mesh_payload")?)?;
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    let mod2 = rt.import_module("_materials")?;
    e.set("linear", rt.member("_materials", "linear")?)?;
    // _read
    e.set("_read", {
        let params = vec![("path".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod3 = rt.import_module("_guide_native")?;
            e.set("read_meshes", rt.member("_guide_native", "read_meshes")?)?;
            return Ok({
                let fun6 = e.get("read_meshes")?;
                let mut args4 = Vec::new();
                let mut kw5 = Vec::new();
                args4.push(e.get("path")?);
                fun6.call(args4, kw5)?
            });
            Ok(Val::None)
        })
    })?;
    // payloads
    e.set("payloads", {
        let params = vec![
            ("art".into(), None, false),
            ("names".into(), None, false),
            ("work".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned7 = e.get("art")?.attr("HARDWARE")?;
            e.set("hardware", assigned7.clone())?;
            let assigned8 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("held", assigned8.clone())?;
            // source
            e.set("source", {
                let params = vec![
                    ("path".into(), None, false),
                    (
                        "keep".into(),
                        Some({
                            let params = vec![("name".into(), None, false)];
                            let outer = e.clone();
                            let runtime = rt.clone();
                            Val::function(move |args, kwargs| {
                                let rt = runtime.clone();
                                let e = bind(&outer, &params, args, kwargs, None, None)?;
                                let _frame = rt.frame(&outer);
                                return Ok(Val::Bool(true));
                                Ok(Val::None)
                            })
                        }),
                        false,
                    ),
                    ("move".into(), Some(Val::None), true),
                    ("color".into(), Some(Val::None), true),
                    ("rename".into(), Some(Val::None), true),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned9 = {
                        let fun12 = e.get("Path")?;
                        let mut args10 = Vec::new();
                        let mut kw11 = Vec::new();
                        args10.push(e.get("path")?);
                        fun12.call(args10, kw11)?
                    };
                    e.set("path", assigned9.clone())?;
                    if {
                        let v13 = e.get("path")?;
                        let v14 = e.get("held")?;
                        Val::Bool(compare("not_in", v13.clone(), v14.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        let assigned15 = {
                            let fun18 = e.get("_read")?;
                            let mut args16 = Vec::new();
                            let mut kw17 = Vec::new();
                            args16.push(e.get("path")?);
                            fun18.call(args16, kw17)?
                        };
                        e.get("held")?.set(e.get("path")?, assigned15.clone())?;
                    }
                    let assigned19 = {
                        let mut s = Vec::new();
                        Val::list(s)
                    };
                    e.set("selected", assigned19.clone())?;
                    for item20 in e.get("held")?.get(e.get("path")?)?.iter()? {
                        e.set("original", item20)?;
                        let assigned21 = {
                            let fun24 = e
                                .get("original")?
                                .get(Val::Str("name".into()))?
                                .attr("split")?;
                            let mut args22 = Vec::new();
                            let mut kw23 = Vec::new();
                            args22.push(Val::Str("/".into()));
                            fun24.call(args22, kw23)?
                        }
                        .get(Val::Int(0i64))?;
                        e.set("name", assigned21.clone())?;
                        if unary("not", {
                            let fun27 = e.get("keep")?;
                            let mut args25 = Vec::new();
                            let mut kw26 = Vec::new();
                            args25.push(e.get("name")?);
                            fun27.call(args25, kw26)?
                        })?
                        .truthy()?
                        {
                            continue;
                        }
                        let assigned28 = {
                            let fun31 = e.get("dict")?;
                            let mut args29 = Vec::new();
                            let mut kw30 = Vec::new();
                            args29.push(e.get("original")?);
                            fun31.call(args29, kw30)?
                        };
                        e.set("mesh", assigned28.clone())?;
                        if {
                            let v32 = e.get("move")?;
                            let v33 = Val::None;
                            Val::Bool(compare("is_not", v32.clone(), v33.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            let assigned34 = {
                                let e = e.child();
                                let out35 = Val::list(vec![]);
                                for item36 in {
                                    let fun39 = e.get("enumerate")?;
                                    let mut args37 = Vec::new();
                                    let mut kw38 = Vec::new();
                                    args37.push(e.get("mesh")?.get(Val::Str("pos".into()))?);
                                    fun39.call(args37, kw38)?
                                }
                                .iter()?
                                {
                                    let unpack40 = unpack(item36, 2)?;
                                    e.set("i", unpack40[0].clone())?;
                                    e.set("v", unpack40[1].clone())?;
                                    out35.attr("append")?.call(
                                        vec![binary(
                                            "add",
                                            {
                                                let fun43 = e.get("float")?;
                                                let mut args41 = Vec::new();
                                                let mut kw42 = Vec::new();
                                                args41.push(e.get("v")?);
                                                fun43.call(args41, kw42)?
                                            },
                                            e.get("move")?.get(binary(
                                                "mod",
                                                e.get("i")?,
                                                Val::Int(3i64),
                                            )?)?,
                                        )?],
                                        vec![],
                                    )?;
                                }
                                out35
                            };
                            e.get("mesh")?
                                .set(Val::Str("pos".into()), assigned34.clone())?;
                        }
                        if {
                            let v44 = e.get("color")?;
                            let v45 = Val::None;
                            Val::Bool(compare("is_not", v44.clone(), v45.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            let assigned46 = {
                                let fun49 = e.get("list")?;
                                let mut args47 = Vec::new();
                                let mut kw48 = Vec::new();
                                args47.push({
                                    let fun52 = e.get("linear")?;
                                    let mut args50 = Vec::new();
                                    let mut kw51 = Vec::new();
                                    args50.push(e.get("color")?);
                                    fun52.call(args50, kw51)?
                                });
                                fun49.call(args47, kw48)?
                            };
                            e.get("mesh")?
                                .set(Val::Str("color".into()), assigned46.clone())?;
                        }
                        if {
                            let v53 = e.get("rename")?;
                            let v54 = Val::None;
                            Val::Bool(compare("is_not", v53.clone(), v54.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            let assigned55 = binary(
                                "add",
                                e.get("rename")?,
                                e.get("original")?.get(Val::Str("name".into()))?.get(
                                    Val::Slice {
                                        start: Some(
                                            {
                                                let fun58 = e.get("len")?;
                                                let mut args56 = Vec::new();
                                                let mut kw57 = Vec::new();
                                                args56.push(e.get("name")?);
                                                fun58.call(args56, kw57)?
                                            }
                                            .integer()?,
                                        ),
                                        stop: None,
                                        step: 1,
                                    },
                                )?,
                            )?;
                            e.get("mesh")?
                                .set(Val::Str("name".into()), assigned55.clone())?;
                        }
                        {
                            let fun61 = e.get("selected")?.attr("append")?;
                            let mut args59 = Vec::new();
                            let mut kw60 = Vec::new();
                            args59.push(e.get("mesh")?);
                            fun61.call(args59, kw60)?
                        };
                    }
                    return Ok(e.get("selected")?);
                    Ok(Val::None)
                })
            })?;
            let assigned62 = binary(
                "truediv",
                e.get("hardware")?,
                Val::Str("faucet-layout/faucet-assembly.step.mesh".into()),
            )?;
            e.set("faucet", assigned62.clone())?;
            let assigned63 = binary(
                "and",
                {
                    let mut s = Vec::new();
                    s.push(Val::Str("opening".into()));
                    s.push(Val::Str("plate-sideways".into()));
                    Val::set_values(s)
                },
                {
                    let fun66 = e.get("set")?;
                    let mut args64 = Vec::new();
                    let mut kw65 = Vec::new();
                    args64.push(e.get("names")?);
                    fun66.call(args64, kw65)?
                },
            )?;
            e.set("crop_names", assigned63.clone())?;
            if e.get("crop_names")?.truthy()? {
                let assigned67 = {
                    let mut s = Vec::new();
                    s.push(Val::Str("westbrass".into()));
                    s.push(Val::Str("flavor_tube_pos_x".into()));
                    s.push(Val::Str("flavor_tube_neg_x".into()));
                    s.push(Val::Str("flavor_umbilical_tube_pos_x".into()));
                    s.push(Val::Str("flavor_umbilical_tube_neg_x".into()));
                    s.push(Val::Str("soda_umbilical_tube".into()));
                    s.push(Val::Str("drain_tube".into()));
                    s.push(Val::Str("display_signal_ribbon".into()));
                    s.push(Val::Str("under_counter_plate".into()));
                    Val::set_values(s)
                };
                e.set("selected", assigned67.clone())?;
                {
                    let fun70 = e.get("_mesh_payload")?.attr("write")?;
                    let mut args68 = Vec::new();
                    let mut kw69 = Vec::new();
                    args68.push({
                        let fun73 = e.get("source")?;
                        let mut args71 = Vec::new();
                        let mut kw72 = Vec::new();
                        args71.push(e.get("faucet")?);
                        args71.push(e.get("selected")?.attr("__contains__")?);
                        fun73.call(args71, kw72)?
                    });
                    args68.push(binary(
                        "truediv",
                        e.get("work")?,
                        Val::Str("faucet.mesh".into()),
                    )?);
                    fun70.call(args68, kw69)?
                };
            }
            let assigned74 = if e.get("crop_names")?.truthy()? {
                {
                    let fun77 = e
                        .get("art")?
                        .attr("_cad_art")?
                        .attr("_load_faucet_module")?;
                    let mut args75 = Vec::new();
                    let mut kw76 = Vec::new();
                    fun77.call(args75, kw76)?
                }
            } else {
                Val::None
            };
            e.set("fa", assigned74.clone())?;
            let assigned78 = if {
                let v79 = Val::Str("regulator".into());
                let v80 = e.get("names")?;
                Val::Bool(compare("in", v79.clone(), v80.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun83 = e.get("art")?.attr("_load_regulator")?;
                    let mut args81 = Vec::new();
                    let mut kw82 = Vec::new();
                    fun83.call(args81, kw82)?
                }
            } else {
                Val::None
            };
            e.set("reg", assigned78.clone())?;
            let assigned84 = {
                let e = e.child();
                let out85 = Val::dict(vec![]);
                for item86 in {
                    let mut s = Vec::new();
                    s.push(Val::Str("STONE".into()));
                    s.push(Val::Str("CABINET".into()));
                    s.push(Val::Str("CORAL".into()));
                    s.push(Val::Str("STEEL".into()));
                    s.push(Val::Str("WHITE_TUBE".into()));
                    s.push(Val::Str("RED_TUBE".into()));
                    s.push(Val::Str("BLUE_TUBE".into()));
                    s.push(Val::Str("BLACK_PART".into()));
                    s.push(Val::Str("BLACK_PART_LIT".into()));
                    s.push(Val::Str("CONCENTRATE".into()));
                    s.push(Val::Str("BOTTLE_PET".into()));
                    s.push(Val::Str("FILTER_BODY".into()));
                    s.push(Val::Str("FILTER_CAP".into()));
                    s.push(Val::Str("CYLINDER".into()));
                    s.push(Val::Str("CORDSET".into()));
                    s.push(Val::Str("NUT_STEEL".into()));
                    s.push(Val::Str("PLATE_STEEL".into()));
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("name", item86)?;
                    out85.set(e.get("name")?, {
                        let fun89 = e.get("list")?;
                        let mut args87 = Vec::new();
                        let mut kw88 = Vec::new();
                        args87.push({
                            let fun92 = e.get("linear")?;
                            let mut args90 = Vec::new();
                            let mut kw91 = Vec::new();
                            args90.push({
                                let fun95 = e.get("getattr")?;
                                let mut args93 = Vec::new();
                                let mut kw94 = Vec::new();
                                args93.push(e.get("art")?);
                                args93.push(e.get("name")?);
                                fun95.call(args93, kw94)?
                            });
                            fun92.call(args90, kw91)?
                        });
                        fun89.call(args87, kw88)?
                    })?;
                }
                out85
            };
            e.set("colors", assigned84.clone())?;
            let assigned96 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("scenes".into()), {
                    let fun99 = e.get("list")?;
                    let mut args97 = Vec::new();
                    let mut kw98 = Vec::new();
                    args97.push(e.get("names")?);
                    fun99.call(args97, kw98)?
                })?;
                d.set(Val::Str("colors".into()), e.get("colors")?)?;
                d.set(Val::Str("box".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("art")?.attr("BOX_X0")?);
                    s.push(e.get("art")?.attr("BOX_X1")?);
                    s.push(e.get("art")?.attr("BOX_Y0")?);
                    s.push(e.get("art")?.attr("BOX_Y1")?);
                    Val::list(s)
                })?;
                d.set(Val::Str("clearances".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("art")?.attr("CLEAR_SIDE")?);
                    s.push(e.get("art")?.attr("CLEAR_BEHIND")?);
                    s.push(e.get("art")?.attr("CYLINDER_LANE")?);
                    Val::list(s)
                })?;
                d.set(Val::Str("cylinder".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("art")?.attr("CYLINDER_D")?);
                    s.push(e.get("art")?.attr("CYLINDER_H")?);
                    Val::list(s)
                })?;
                d.set(Val::Str("filter".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("art")?.attr("FILTER_D")?);
                    s.push(e.get("art")?.attr("FILTER_L")?);
                    Val::list(s)
                })?;
                d.set(Val::Str("tube_d".into()), e.get("art")?.attr("TUBE_D")?)?;
                d.set(Val::Str("bottle".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("art")?.attr("BOTTLE_D")?);
                    s.push(e.get("art")?.attr("BOTTLE_H")?);
                    s.push(e.get("art")?.attr("BOTTLE_NECK_D")?);
                    s.push(e.get("art")?.attr("BOTTLE_NECK_H")?);
                    s.push(e.get("art")?.attr("BOTTLE_TIP")?);
                    s.push(e.get("art")?.attr("BOTTLE_CLEARANCE")?);
                    s.extend(e.get("art")?.attr("FUNNEL_MOUTH")?.iter()?);
                    s.push(e.get("art")?.attr("FUNNEL_BOUNDS")?.get(Val::Int(5i64))?);
                    Val::list(s)
                })?;
                d.set(Val::Str("c13".into()), {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("station".into()), {
                        let mut s = Vec::new();
                        s.extend(e.get("art")?.attr("C14_STATION")?.iter()?);
                        s.push(e.get("art")?.attr("REAR_FACE_Y")?);
                        Val::list(s)
                    })?;
                    d.set(Val::Str("slip".into()), e.get("art")?.attr("C13_SLIP")?)?;
                    d.set(Val::Str("wall".into()), e.get("art")?.attr("C13_WALL")?)?;
                    d.set(Val::Str("body".into()), e.get("art")?.attr("C13_BODY_LEN")?)?;
                    d.set(Val::Str("nose".into()), e.get("art")?.attr("C13_NOSE_LEN")?)?;
                    d.set(Val::Str("boot".into()), e.get("art")?.attr("C13_BOOT_LEN")?)?;
                    d.set(Val::Str("boot_d".into()), e.get("art")?.attr("C13_BOOT_D")?)?;
                    d.set(
                        Val::Str("cable_d".into()),
                        e.get("art")?.attr("C13_CABLE_D")?,
                    )?;
                    d.set(Val::Str("mouth".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("art")?.attr("_c14")?.attr("MOUTH_W")?);
                        s.push(e.get("art")?.attr("_c14")?.attr("MOUTH_H")?);
                        s.push(e.get("art")?.attr("_c14")?.attr("MOUTH_TOP_R")?);
                        Val::list(s)
                    })?;
                    d.set(
                        Val::Str("blades".into()),
                        e.get("art")?.attr("_c14")?.attr("BLADE_STATIONS")?,
                    )?;
                    d.set(Val::Str("blade_size".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("art")?.attr("_c14")?.attr("BLADE_T")?);
                        s.push(e.get("art")?.attr("_c14")?.attr("BLADE_W")?);
                        Val::list(s)
                    })?;
                    d
                })?;
                d
            };
            e.set("numbers", assigned96.clone())?;
            if {
                let v100 = e.get("fa")?;
                let v101 = Val::None;
                Val::Bool(compare("is_not", v100.clone(), v101.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned102 = {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("payload".into()), {
                        let fun105 = e.get("str")?;
                        let mut args103 = Vec::new();
                        let mut kw104 = Vec::new();
                        args103.push(binary(
                            "truediv",
                            e.get("work")?,
                            Val::Str("faucet.mesh".into()),
                        )?);
                        fun105.call(args103, kw104)?
                    })?;
                    d.set(Val::Str("counter".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("fa")?.attr("countertop_bottom_z")?);
                        s.push(e.get("fa")?.attr("countertop_thickness")?);
                        s.push(e.get("fa")?.attr("countertop_hole_center_y")?);
                        s.push(e.get("fa")?.attr("hole_radius")?);
                        Val::list(s)
                    })?;
                    d.set(
                        Val::Str("shank_length".into()),
                        e.get("fa")?.attr("shank_length")?,
                    )?;
                    d.set(
                        Val::Str("plate_x".into()),
                        e.get("art")?.attr("PLATE_STANDOFF_X")?,
                    )?;
                    d.set(Val::Str("washer_t".into()), e.get("art")?.attr("WASHER_T")?)?;
                    d.set(Val::Str("nut_h".into()), e.get("art")?.attr("NUT_H")?)?;
                    d
                };
                e.get("numbers")?
                    .set(Val::Str("faucet".into()), assigned102.clone())?;
            }
            if {
                let v106 = e.get("reg")?;
                let v107 = Val::None;
                Val::Bool(compare("is_not", v106.clone(), v107.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned108 = {
                    let d = Val::dict(vec![]);
                    d.set(
                        Val::Str("mouth".into()),
                        {
                            let fun111 = e.get("reg")?.attr("outlet")?;
                            let mut args109 = Vec::new();
                            let mut kw110 = Vec::new();
                            fun111.call(args109, kw110)?
                        }
                        .get(Val::Int(0i64))?,
                    )?;
                    d.set(
                        Val::Str("insert".into()),
                        e.get("art")?.attr("TETHER_IN_MOUTH")?,
                    )?;
                    d
                };
                e.get("numbers")?
                    .set(Val::Str("tether".into()), assigned108.clone())?;
            }
            let assigned112 = binary("truediv", e.get("work")?, Val::Str("props.json".into()))?;
            e.set("path", assigned112.clone())?;
            {
                let fun115 = e.get("path")?.attr("write_text")?;
                let mut args113 = Vec::new();
                let mut kw114 = Vec::new();
                args113.push(binary(
                    "add",
                    {
                        let fun118 = e.get("json")?.attr("dumps")?;
                        let mut args116 = Vec::new();
                        let mut kw117 = Vec::new();
                        args116.push(e.get("numbers")?);
                        kw117.push(("sort_keys".into(), Val::Bool(true)));
                        fun118.call(args116, kw117)?
                    },
                    Val::Str("\n".into()),
                )?);
                fun115.call(args113, kw114)?
            };
            {
                let fun121 = e.get("_rust_part")?.attr("run")?;
                let mut args119 = Vec::new();
                let mut kw120 = Vec::new();
                args119.push(Val::Str("tooling".into()));
                args119.push(Val::Str("install-art-props".into()));
                args119.push(e.get("path")?);
                args119.push(e.get("work")?);
                fun121.call(args119, kw120)?
            };
            let assigned122 = binary(
                "truediv",
                e.get("art")?.attr("PLUMBING_DIR")?,
                Val::Str("out".into()),
            )?;
            e.set("plumbing", assigned122.clone())?;
            let assigned123 = {
                let d = Val::dict(vec![]);
                d.set(
                    Val::Str("stop-open".into()),
                    Val::Str("plumbing-valve-on".into()),
                )?;
                d.set(
                    Val::Str("stop-closed".into()),
                    Val::Str("plumbing-valve-off".into()),
                )?;
                d.set(
                    Val::Str("tee-before".into()),
                    Val::Str("plumbing-pre-tee".into()),
                )?;
                d.set(
                    Val::Str("tee-after".into()),
                    Val::Str("plumbing-tee-installed".into()),
                )?;
                d.set(
                    Val::Str("kitchen-hose".into()),
                    Val::Str("plumbing-valve-on".into()),
                )?;
                d
            };
            e.set("plumbing_names", assigned123.clone())?;
            let assigned124 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("shown", assigned124.clone())?;
            for item125 in e.get("names")?.iter()? {
                e.set("name", item125)?;
                let assigned126 = {
                    let fun129 = e.get("_read")?;
                    let mut args127 = Vec::new();
                    let mut kw128 = Vec::new();
                    args127.push(binary("truediv", e.get("work")?, {
                        let mut str130 = String::new();
                        str130.push_str(&format(&e.get("name")?, &String::new())?);
                        str130.push_str(".props.mesh");
                        Val::Str(str130)
                    })?);
                    fun129.call(args127, kw128)?
                };
                e.set("meshes", assigned126.clone())?;
                if {
                    let v131 = e.get("name")?;
                    let v132 = {
                        let mut s = Vec::new();
                        s.push(Val::Str("cabinet-plan".into()));
                        s.push(Val::Str("bottle-in-funnel".into()));
                        s.push(Val::Str("nameplate".into()));
                        s.push(Val::Str("the-back-face".into()));
                        s.push(Val::Str("the-socket".into()));
                        Val::tuple(s)
                    };
                    Val::Bool(compare("in", v131.clone(), v132.clone())?.truthy()?)
                }
                .truthy()?
                {
                    if {
                        let v133 = e.get("name")?;
                        let v134 = Val::Str("cabinet-plan".into());
                        Val::Bool(compare("eq", v133.clone(), v134.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        let assigned135 = {
                            let params = vec![("body".into(), None, false)];
                            let outer = e.clone();
                            let runtime = rt.clone();
                            Val::function(move |args, kwargs| {
                                let rt = runtime.clone();
                                let e = bind(&outer, &params, args, kwargs, None, None)?;
                                let _frame = rt.frame(&outer);
                                return Ok(Val::Bool(true));
                                Ok(Val::None)
                            })
                        };
                        e.set("keep", assigned135.clone())?;
                    } else {
                        if {
                            let v136 = e.get("name")?;
                            let v137 = Val::Str("bottle-in-funnel".into());
                            Val::Bool(compare("eq", v136.clone(), v137.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            let assigned138 = {
                                let params = vec![("body".into(), None, false)];
                                let outer = e.clone();
                                let runtime = rt.clone();
                                Val::function(move |args, kwargs| {
                                    let rt = runtime.clone();
                                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                                    let _frame = rt.frame(&outer);
                                    return Ok({
                                        let v139 = e.get("body")?;
                                        let v140 = Val::Str("funnel-cover".into());
                                        Val::Bool(
                                            compare("ne", v139.clone(), v140.clone())?.truthy()?,
                                        )
                                    });
                                    Ok(Val::None)
                                })
                            };
                            e.set("keep", assigned138.clone())?;
                        } else {
                            let assigned141 = {
                                let params = vec![("body".into(), None, false)];
                                let outer = e.clone();
                                let runtime = rt.clone();
                                Val::function(move |args, kwargs| {
                                    let rt = runtime.clone();
                                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                                    let _frame = rt.frame(&outer);
                                    return Ok({
                                        let v145 = {
                                            let v146 = e.get("body")?;
                                            let v147 = e.get("art")?.attr("REAR_CHILDREN")?;
                                            Val::Bool(
                                                compare("in", v146.clone(), v147.clone())?
                                                    .truthy()?,
                                            )
                                        };
                                        if v145.truthy()? {
                                            v145
                                        } else {
                                            {
                                                let fun144 = e.get("body")?.attr("startswith")?;
                                                let mut args142 = Vec::new();
                                                let mut kw143 = Vec::new();
                                                args142
                                                    .push(e.get("art")?.attr("REAR_RING_PREFIX")?);
                                                fun144.call(args142, kw143)?
                                            }
                                        }
                                    });
                                    Ok(Val::None)
                                })
                            };
                            e.set("keep", assigned141.clone())?;
                        }
                    }
                    e.set(
                        "meshes",
                        binary("add", e.get("meshes")?, {
                            let fun150 = e.get("source")?;
                            let mut args148 = Vec::new();
                            let mut kw149 = Vec::new();
                            args148.push(e.get("art")?.attr("MACHINE_MESH")?);
                            args148.push(e.get("keep")?);
                            fun150.call(args148, kw149)?
                        })?,
                    )?;
                } else {
                    if {
                        let v151 = e.get("name")?;
                        let v152 = e.get("plumbing_names")?;
                        Val::Bool(compare("in", v151.clone(), v152.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        e.set(
                            "meshes",
                            binary("add", e.get("meshes")?, {
                                let fun155 = e.get("source")?;
                                let mut args153 = Vec::new();
                                let mut kw154 = Vec::new();
                                args153.push(binary("truediv", e.get("plumbing")?, {
                                    let mut str156 = String::new();
                                    str156.push_str(&format(
                                        &e.get("plumbing_names")?.get(e.get("name")?)?,
                                        &String::new(),
                                    )?);
                                    str156.push_str(".step.mesh");
                                    Val::Str(str156)
                                })?);
                                args153.push({
                                    let params = vec![("body".into(), None, false)];
                                    let outer = e.clone();
                                    let runtime = rt.clone();
                                    Val::function(move |args, kwargs| {
                                        let rt = runtime.clone();
                                        let e = bind(&outer, &params, args, kwargs, None, None)?;
                                        let _frame = rt.frame(&outer);
                                        return Ok({
                                            let v157 = e.get("body")?;
                                            let v158 = Val::Str("finished-wall".into());
                                            Val::Bool(
                                                compare("ne", v157.clone(), v158.clone())?
                                                    .truthy()?,
                                            )
                                        });
                                        Ok(Val::None)
                                    })
                                });
                                fun155.call(args153, kw154)?
                            })?,
                        )?;
                    } else {
                        if {
                            let v159 = e.get("name")?;
                            let v160 = Val::Str("kitchen-push".into());
                            Val::Bool(compare("eq", v159.clone(), v160.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            e.set(
                                "meshes",
                                binary("add", e.get("meshes")?, {
                                    let fun163 = e.get("source")?;
                                    let mut args161 = Vec::new();
                                    let mut kw162 = Vec::new();
                                    args161.push(binary(
                                        "truediv",
                                        e.get("art")?.attr("MODERN_DIR")?,
                                        Val::Str("out/modern-water-on.step.mesh".into()),
                                    )?);
                                    fun163.call(args161, kw162)?
                                })?,
                            )?;
                        } else {
                            if {
                                let v164 = e.get("name")?;
                                let v165 = Val::Str("two-tees".into());
                                Val::Bool(compare("eq", v164.clone(), v165.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                e.set(
                                    "meshes",
                                    binary("add", e.get("meshes")?, {
                                        let fun168 = e.get("source")?;
                                        let mut args166 = Vec::new();
                                        let mut kw167 = Vec::new();
                                        args166.push(binary(
                                            "truediv",
                                            e.get("hardware")?,
                                            Val::Str(
                                                "reference/jg-pp0208e-tee/jg-pp0208e-tee.step.mesh"
                                                    .into(),
                                            ),
                                        )?);
                                        kw167.push(("move".into(), {
                                            let mut s = Vec::new();
                                            s.push(Val::Float(30.0f64));
                                            s.push(Val::Float(0.0f64));
                                            s.push(Val::Float(0.0f64));
                                            Val::tuple(s)
                                        }));
                                        kw167.push((
                                            "color".into(),
                                            e.get("art")?.attr("BLACK_PART")?,
                                        ));
                                        kw167.push(("rename".into(), Val::Str("black-tee".into())));
                                        fun168.call(args166, kw167)?
                                    })?,
                                )?;
                                e.set(
                                    "meshes",
                                    binary("add", e.get("meshes")?, {
                                        let fun171 = e.get("source")?;
                                        let mut args169 = Vec::new();
                                        let mut kw170 = Vec::new();
                                        args169.push(binary(
                                            "truediv",
                                            e.get("plumbing")?,
                                            Val::Str("plumbing-pre-tee.step.mesh".into()),
                                        )?);
                                        args169.push({
                                            let params = vec![("body".into(), None, false)];
                                            let outer = e.clone();
                                            let runtime = rt.clone();
                                            Val::function(move |args, kwargs| {
                                                let rt = runtime.clone();
                                                let e = bind(
                                                    &outer, &params, args, kwargs, None, None,
                                                )?;
                                                let _frame = rt.frame(&outer);
                                                return Ok({
                                                    let fun174 =
                                                        e.get("body")?.attr("startswith")?;
                                                    let mut args172 = Vec::new();
                                                    let mut kw173 = Vec::new();
                                                    args172.push(Val::Str("tee-".into()));
                                                    fun174.call(args172, kw173)?
                                                });
                                                Ok(Val::None)
                                            })
                                        });
                                        kw170.push(("move".into(), {
                                            let mut s = Vec::new();
                                            s.push(unary("neg", Val::Float(57.0f64))?);
                                            s.push(unary("neg", Val::Float(77.0f64))?);
                                            s.push(unary("neg", Val::Float(182.8f64))?);
                                            Val::tuple(s)
                                        }));
                                        fun171.call(args169, kw170)?
                                    })?,
                                )?;
                            } else {
                                if {
                                    let v175 = e.get("name")?;
                                    let v176 = Val::Str("regulator".into());
                                    Val::Bool(compare("eq", v175.clone(), v176.clone())?.truthy()?)
                                }
                                .truthy()?
                                {
                                    e.set(
                                        "meshes",
                                        binary("add", e.get("meshes")?, {
                                            let fun179 = e.get("source")?;
                                            let mut args177 = Vec::new();
                                            let mut kw178 = Vec::new();
                                            args177.push(binary(
                                                "truediv",
                                                e.get("art")?.attr("REGULATOR_DIR")?,
                                                Val::Str("taprite-3741-regulator.step.mesh".into()),
                                            )?);
                                            fun179.call(args177, kw178)?
                                        })?,
                                    )?;
                                } else {
                                    if {
                                        let v180 = e.get("name")?;
                                        let v181 = Val::Str("collet-press".into());
                                        Val::Bool(
                                            compare("eq", v180.clone(), v181.clone())?.truthy()?,
                                        )
                                    }
                                    .truthy()?
                                    {
                                        e.set(
                                            "meshes",
                                            binary("add", e.get("meshes")?, {
                                                let fun184 = e.get("source")?;
                                                let mut args182 = Vec::new();
                                                let mut kw183 = Vec::new();
                                                args182.push({
                                                    let fun187 = e.get("Path")?;
                                                    let mut args185 = Vec::new();
                                                    let mut kw186 = Vec::new();
                                                    args185.push({
                                                        let mut str188 = String::new();
                                                        str188.push_str(&format(
                                                            &e.get("art")?.attr("COLLET_PRESS")?,
                                                            &String::new(),
                                                        )?);
                                                        str188.push_str(".mesh");
                                                        Val::Str(str188)
                                                    });
                                                    fun187.call(args185, kw186)?
                                                });
                                                kw183.push((
                                                    "color".into(),
                                                    e.get("art")?.attr("PRINTED")?,
                                                ));
                                                fun184.call(args182, kw183)?
                                            })?,
                                        )?;
                                    }
                                }
                            }
                        }
                    }
                }
                let assigned189 = binary("truediv", e.get("work")?, {
                    let mut str190 = String::new();
                    str190.push_str(&format(&e.get("name")?, &String::new())?);
                    str190.push_str(".step.mesh");
                    Val::Str(str190)
                })?;
                e.get("shown")?.set(e.get("name")?, assigned189.clone())?;
                {
                    let fun193 = e.get("_mesh_payload")?.attr("write")?;
                    let mut args191 = Vec::new();
                    let mut kw192 = Vec::new();
                    args191.push(e.get("meshes")?);
                    args191.push(e.get("shown")?.get(e.get("name")?)?);
                    fun193.call(args191, kw192)?
                };
            }
            return Ok(e.get("shown")?);
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
