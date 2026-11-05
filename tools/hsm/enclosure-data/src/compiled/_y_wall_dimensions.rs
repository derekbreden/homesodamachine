//! Doc-sync driver for hardware/printed-parts/enclosure/y-wall-of-back-top/README.md.
//!
//! Run: tools/cad-venv/bin/python hardware/printed-parts/enclosure/y-wall-of-back-top/_y_wall_dimensions.py
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let assigned2 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
            line!(),
        );
        {
            let fun5 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                    line!(),
                );
                {
                    let fun8 = e.get("Path")?;
                    let mut args6 = Vec::new();
                    let mut kw7 = Vec::new();
                    args6.push(e.get("__file__")?);
                    fun8.call(args6, kw7)?
                }
            }
            .attr("resolve")?;
            let mut args3 = Vec::new();
            let mut kw4 = Vec::new();
            fun5.call(args3, kw4)?
        }
    }
    .attr("parent")?;
    e.set("_here", assigned2.clone())?;
    let assigned9 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
            line!(),
        );
        {
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
        }
    };
    e.set("_hw", assigned9.clone())?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
            line!(),
        );
        {
            let fun19 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args17 = Vec::new();
            let mut kw18 = Vec::new();
            args17.push(Val::Int(0i64));
            args17.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",line!());{let fun22=e.get("str")?;let mut args20=Vec::new();let mut kw21=Vec::new();args20.push(binary("truediv",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",line!());{let fun25=e.get("next")?;let mut args23=Vec::new();let mut kw24=Vec::new();args23.push({let e=e.child();let out26=Val::list(vec![]);for item27 in e.get("_here")?.attr("parents")?.iter()? {e.set("p",item27)?;if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",line!());{let fun30=binary("truediv",binary("truediv",e.get("p")?,Val::Str("tools".into()))?,Val::Str("docgen".into()))?.attr("is_dir")?;let mut args28=Vec::new();let mut kw29=Vec::new();fun30.call(args28,kw29)?}}.truthy()? {out26.attr("append")?.call(vec![e.get("p")?],vec![])?;}}out26});fun25.call(args23,kw24)?}},Val::Str("tools".into()))?);fun22.call(args20,kw21)?}});
            fun19.call(args17, kw18)?
        }
    };
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
            line!(),
        );
        {
            let fun33 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args31 = Vec::new();
            let mut kw32 = Vec::new();
            args31.push(Val::Int(0i64));
            args31.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                    line!(),
                );
                {
                    let fun36 = e.get("str")?;
                    let mut args34 = Vec::new();
                    let mut kw35 = Vec::new();
                    args34.push(binary(
                        "truediv",
                        e.get("_hw")?,
                        Val::Str("manifold-layout".into()),
                    )?);
                    fun36.call(args34, kw35)?
                }
            });
            fun33.call(args31, kw32)?
        }
    };
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
            line!(),
        );
        {
            let fun39 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args37 = Vec::new();
            let mut kw38 = Vec::new();
            args37.push(Val::Int(0i64));
            args37.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                    line!(),
                );
                {
                    let fun42 = e.get("str")?;
                    let mut args40 = Vec::new();
                    let mut kw41 = Vec::new();
                    args40.push(binary(
                        "truediv",
                        e.get("_hw")?,
                        Val::Str("scripts".into()),
                    )?);
                    fun42.call(args40, kw41)?
                }
            });
            fun39.call(args37, kw38)?
        }
    };
    let mod44 = rt.import_module("_material_base")?;
    e.set("stock_srgb", rt.member("_material_base", "stock_srgb")?)?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
            line!(),
        );
        {
            let fun47 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args45 = Vec::new();
            let mut kw46 = Vec::new();
            args45.push(Val::Int(0i64));
            args45.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                    line!(),
                );
                {
                    let fun50 = e.get("str")?;
                    let mut args48 = Vec::new();
                    let mut kw49 = Vec::new();
                    args48.push(binary(
                        "truediv",
                        e.get("_hw")?,
                        Val::Str("printed-parts/enclosure/enclosure".into()),
                    )?);
                    fun50.call(args48, kw49)?
                }
            });
            fun47.call(args45, kw46)?
        }
    };
    let mod51 = rt.import_module("_enclosure_data")?;
    e.set("_read", rt.member("_enclosure_data", "read")?)?;
    let assigned52 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
            line!(),
        );
        {
            let fun55 = e.get("_read")?;
            let mut args53 = Vec::new();
            let mut kw54 = Vec::new();
            args53.push(Val::Str("rear".into()));
            kw54.push(("black_srgb".into(), {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                    line!(),
                );
                {
                    let fun58 = e.get("stock_srgb")?;
                    let mut args56 = Vec::new();
                    let mut kw57 = Vec::new();
                    args56.push(Val::Str("M_PETGF_BLACK".into()));
                    fun58.call(args56, kw57)?
                }
            }));
            fun55.call(args53, kw54)?
        }
    };
    e.set("_palette", assigned52.clone())?;
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
                let v59 = e.get("name")?;
                let v60 = Val::Str("M_PETGF_BLACK".into());
                Val::Bool(compare("eq", v59.clone(), v60.clone())?.truthy()?)
            }
            .truthy()?
            {
                let mod61 = rt.import_module("_material_base")?;
                e.set(
                    "M_PETGF_BLACK",
                    rt.member("_material_base", "M_PETGF_BLACK")?,
                )?;
                let assigned62 = e.get("M_PETGF_BLACK")?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                        line!(),
                    );
                    {
                        let fun65 = e.get("globals")?;
                        let mut args63 = Vec::new();
                        let mut kw64 = Vec::new();
                        fun65.call(args63, kw64)?
                    }
                }
                .set(e.get("name")?, assigned62.clone())?;
                return Ok(e.get("M_PETGF_BLACK")?);
            }
            anyhow::bail!(
                "{}",
                val_string({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                        line!(),
                    );
                    {
                        let fun68 = e.get("AttributeError")?;
                        let mut args66 = Vec::new();
                        let mut kw67 = Vec::new();
                        args66.push(e.get("name")?);
                        fun68.call(args66, kw67)?
                    }
                })?
            );
            Ok(Val::None)
        })
    })?;
    // __dir__
    e.set("__dir__",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",line!());{let fun71=e.get("sorted")?;let mut args69=Vec::new();let mut kw70=Vec::new();args69.push(binary("or",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",line!());{let fun74=e.get("set")?;let mut args72=Vec::new();let mut kw73=Vec::new();args72.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",line!());{let fun77=e.get("globals")?;let mut args75=Vec::new();let mut kw76=Vec::new();fun77.call(args75,kw76)?}});fun74.call(args72,kw73)?}},{let mut s=Vec::new();s.push(Val::Str("M_PETGF_BLACK".into()));Val::set_values(s)})?);fun71.call(args69,kw70)?}});
Ok(Val::None)})})?;
    // c14_rim_inset
    e.set("c14_rim_inset", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_ea", rt.import_module("enclosure_assembly")?)?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                    line!(),
                );
                {
                    let fun80 = e.get("_read")?;
                    let mut args78 = Vec::new();
                    let mut kw79 = Vec::new();
                    args78.push(Val::Str("rim-inset".into()));
                    kw79.push((
                        "rear_plane_y".into(),
                        e.get("_ea")?.attr("_enc")?.attr("rear_plane_y")?,
                    ));
                    kw79.push(("wall".into(), e.get("_ea")?.attr("_enc")?.attr("wall")?));
                    kw79.push(("seat_y".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                            line!(),
                        );
                        {
                            let fun83 = e.get("_ea")?.attr("c14_seat_y")?;
                            let mut args81 = Vec::new();
                            let mut kw82 = Vec::new();
                            fun83.call(args81, kw82)?
                        }
                    }));
                    fun80.call(args78, kw79)?
                }
            });
            Ok(Val::None)
        })
    })?;
    let assigned84 = {
        let e = e.child();
        let out85 = Val::dict(vec![]);
        for item86 in e
            .get("_palette")?
            .get(Val::Str("port_order".into()))?
            .iter()?
        {
            e.set("name", item86)?;
            out85.set(e.get("name")?, {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                    line!(),
                );
                {
                    let fun89 = e.get("tuple")?;
                    let mut args87 = Vec::new();
                    let mut kw88 = Vec::new();
                    args87.push(
                        e.get("_palette")?
                            .get(Val::Str("port_colors".into()))?
                            .get(e.get("name")?)?,
                    );
                    fun89.call(args87, kw88)?
                }
            })?;
        }
        out85
    };
    e.set("port_colors", assigned84.clone())?;
    let assigned90 = {
        let e = e.child();
        let out91 = Val::dict(vec![]);
        for item92 in e
            .get("_palette")?
            .get(Val::Str("filament_order".into()))?
            .iter()?
        {
            e.set("name", item92)?;
            out91.set(e.get("name")?, {
                let mut s = Vec::new();
                s.push(
                    e.get("_palette")?
                        .get(Val::Str("chip_filaments".into()))?
                        .get(e.get("name")?)?
                        .get(Val::Int(0i64))?,
                );
                s.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                        line!(),
                    );
                    {
                        let fun95 = e.get("tuple")?;
                        let mut args93 = Vec::new();
                        let mut kw94 = Vec::new();
                        args93.push(
                            e.get("_palette")?
                                .get(Val::Str("chip_filaments".into()))?
                                .get(e.get("name")?)?
                                .get(Val::Int(1i64))?,
                        );
                        fun95.call(args93, kw94)?
                    }
                });
                Val::tuple(s)
            })?;
        }
        out91
    };
    e.set("chip_filaments", assigned90.clone())?;
    let assigned96 = {
        let e = e.child();
        let out97 = Val::dict(vec![]);
        for item98 in e
            .get("_palette")?
            .get(Val::Str("filament_order".into()))?
            .iter()?
        {
            e.set("name", item98)?;
            out97.set(e.get("name")?, {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                    line!(),
                );
                {
                    let fun101 = e.get("tuple")?;
                    let mut args99 = Vec::new();
                    let mut kw100 = Vec::new();
                    args99.push(
                        e.get("_palette")?
                            .get(Val::Str("chip_word_colors".into()))?
                            .get(e.get("name")?)?,
                    );
                    fun101.call(args99, kw100)?
                }
            })?;
        }
        out97
    };
    e.set("chip_word_colors", assigned96.clone())?;
    // chip_color
    e.set("chip_color", {
        let params = vec![("fluid".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e
                .get("chip_filaments")?
                .get(e.get("fluid")?)?
                .get(Val::Int(1i64))?);
            Ok(Val::None)
        })
    })?;
    // word_color
    e.set("word_color", {
        let params = vec![("fluid".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("chip_word_colors")?.get(e.get("fluid")?)?);
            Ok(Val::None)
        })
    })?;
    // port_color_hex
    e.set("port_color_hex", {
        let params = vec![("fluid".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e
                .get("_palette")?
                .get(Val::Str("hex".into()))?
                .get(e.get("fluid")?)?);
            Ok(Val::None)
        })
    })?;
    // port_color_svg
    e.set("port_color_svg", {
        let params = vec![("fluid".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e
                .get("_palette")?
                .get(Val::Str("svg".into()))?
                .get(e.get("fluid")?)?);
            Ok(Val::None)
        })
    })?;
    // carb_union_end
    e.set("carb_union_end", {
        let params = vec![("panel_x".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                    line!(),
                );
                {
                    let fun104 = e.get("_read")?;
                    let mut args102 = Vec::new();
                    let mut kw103 = Vec::new();
                    args102.push(Val::Str("carb-union-end".into()));
                    kw103.push(("panel_x".into(), e.get("panel_x")?));
                    fun104.call(args102, kw103)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // dropped_union_end
    e.set("dropped_union_end", {
        let params = vec![
            ("panel_on_gate_lane".into(), None, false),
            ("panel_x".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                    line!(),
                );
                {
                    let fun107 = e.get("_read")?;
                    let mut args105 = Vec::new();
                    let mut kw106 = Vec::new();
                    args105.push(Val::Str("dropped-union-end".into()));
                    kw106.push(("lanes".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                            line!(),
                        );
                        {
                            let fun110 = e.get("list")?;
                            let mut args108 = Vec::new();
                            let mut kw109 = Vec::new();
                            args108.push(e.get("panel_on_gate_lane")?);
                            fun110.call(args108, kw109)?
                        }
                    }));
                    kw106.push(("panel_x".into(), e.get("panel_x")?));
                    fun107.call(args105, kw106)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // panel_hole_diameters
    e.set("panel_hole_diameters", {
        let params = vec![("ports".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                    line!(),
                );
                {
                    let fun113 = e.get("tuple")?;
                    let mut args111 = Vec::new();
                    let mut kw112 = Vec::new();
                    args111.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                            line!(),
                        );
                        {
                            let fun116 = e.get("_read")?;
                            let mut args114 = Vec::new();
                            let mut kw115 = Vec::new();
                            args114.push(Val::Str("panel-hole-diameters".into()));
                            kw115.push(("ports".into(), e.get("ports")?));
                            fun116.call(args114, kw115)?
                        }
                    });
                    fun113.call(args111, kw112)?
                }
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
            e.set("above_core", rt.import_module("above_core")?)?;
            let assigned117 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
                    line!(),
                );
                {
                    let fun120 = e.get("above_core")?.attr("specification")?;
                    let mut args118 = Vec::new();
                    let mut kw119 = Vec::new();
                    fun120.call(args118, kw119)?
                }
            }
            .get(Val::Str("rear_wall".into()))?
            .get(Val::Str("grid".into()))?
            .get(Val::Str("rows_z_mm".into()))?;
            e.set("rows", assigned117.clone())?;
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_y_wall_dimensions.rs",
            line!(),
        );
        {
            let fun132 = e.get("main")?;
            let mut args130 = Vec::new();
            let mut kw131 = Vec::new();
            fun132.call(args130, kw131)?
        }
    };
    Ok(Val::None)
}
