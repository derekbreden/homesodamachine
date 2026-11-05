//! Guide recipe: `hardware/install-guide/_install_art.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("json", rt.import_module("json")?)?;
    e.set("os", rt.import_module("os")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    e.set("tempfile", rt.import_module("tempfile")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("math", rt.import_module("math")?)?;
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
    .attr("parent")?;
    e.set("HERE", assigned2.clone())?;
    let assigned9 = {
        let fun12 = e.get("next")?;
        let mut args10 = Vec::new();
        let mut kw11 = Vec::new();
        args10.push({
            let e = e.child();
            let out13 = Val::list(vec![]);
            for item14 in e.get("HERE")?.attr("parents")?.iter()? {
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
    e.set("HARDWARE", assigned9.clone())?;
    let assigned17 = e.get("HARDWARE")?.attr("parent")?;
    e.set("ROOT", assigned17.clone())?;
    let assigned18 = binary("truediv", e.get("HERE")?, Val::Str("art".into()))?;
    e.set("ART", assigned18.clone())?;
    let assigned19 = binary("truediv", e.get("HERE")?, Val::Str("out".into()))?;
    e.set("OUT", assigned19.clone())?;
    {
        let fun22 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args20 = Vec::new();
        let mut kw21 = Vec::new();
        args20.push(Val::Int(0i64));
        args20.push({
            let fun25 = e.get("str")?;
            let mut args23 = Vec::new();
            let mut kw24 = Vec::new();
            args23.push(binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("scripts".into()),
            )?);
            fun25.call(args23, kw24)?
        });
        fun22.call(args20, kw21)?
    };
    {
        let fun28 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args26 = Vec::new();
        let mut kw27 = Vec::new();
        args26.push(Val::Int(0i64));
        args26.push({
            let fun31 = e.get("str")?;
            let mut args29 = Vec::new();
            let mut kw30 = Vec::new();
            args29.push(binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("install-guide".into()),
            )?);
            fun31.call(args29, kw30)?
        });
        fun28.call(args26, kw27)?
    };
    {
        let fun34 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args32 = Vec::new();
        let mut kw33 = Vec::new();
        args32.push(Val::Int(0i64));
        args32.push({
            let fun37 = e.get("str")?;
            let mut args35 = Vec::new();
            let mut kw36 = Vec::new();
            args35.push(binary(
                "truediv",
                binary(
                    "truediv",
                    e.get("HARDWARE")?,
                    Val::Str("printed-parts".into()),
                )?,
                Val::Str("cadlib".into()),
            )?);
            fun37.call(args35, kw36)?
        });
        fun34.call(args32, kw33)?
    };
    {
        let fun40 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args38 = Vec::new();
        let mut kw39 = Vec::new();
        args38.push(Val::Int(0i64));
        args38.push({
            let fun43 = e.get("str")?;
            let mut args41 = Vec::new();
            let mut kw42 = Vec::new();
            args41.push(binary(
                "truediv",
                binary("truediv", e.get("HARDWARE")?, Val::Str("reference".into()))?,
                Val::Str("iec-c14-inlet".into()),
            )?);
            fun43.call(args41, kw42)?
        });
        fun40.call(args38, kw39)?
    };
    e.set("cq", rt.import_module("cadquery")?)?;
    let mod44 = rt.import_module("_cadq_export")?;
    e.set("import_step", rt.member("_cadq_export", "import_step")?)?;
    e.set("note_read", rt.member("_cadq_export", "note_read")?)?;
    e.set("note_write", rt.member("_cadq_export", "note_write")?)?;
    let mod45 = rt.import_module("world_workplane")?;
    e.set(
        "xz_plane_y_up",
        rt.member("world_workplane", "xz_plane_y_up")?,
    )?;
    e.set("_c14", rt.import_module("iec_c14_inlet")?)?;
    e.set("_cad_art", rt.import_module("_cad_art")?)?;
    e.set("_hsm_render", rt.import_module("_hsm_render")?)?;
    let assigned46 = e.get("_cad_art")?.attr("MACHINE_MESH")?;
    e.set("MACHINE_MESH", assigned46.clone())?;
    let assigned47 = e.get("_cad_art")?.attr("MACHINE_FACTS")?;
    e.set("MACHINE_FACTS", assigned47.clone())?;
    let assigned48 = binary(
        "truediv",
        binary(
            "truediv",
            binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("printed-parts".into()),
            )?,
            Val::Str("collet-press".into()),
        )?,
        Val::Str("collet-press.step".into()),
    )?;
    e.set("COLLET_PRESS", assigned48.clone())?;
    let assigned49 = binary(
        "truediv",
        binary("truediv", e.get("HARDWARE")?, Val::Str("reference".into()))?,
        Val::Str("taprite-3741-regulator".into()),
    )?;
    e.set("REGULATOR_DIR", assigned49.clone())?;
    let assigned50 = binary(
        "truediv",
        binary(
            "truediv",
            e.get("HARDWARE")?,
            Val::Str("install-guide".into()),
        )?,
        Val::Str("plumbing".into()),
    )?;
    e.set("PLUMBING_DIR", assigned50.clone())?;
    let assigned51 = binary("truediv", e.get("PLUMBING_DIR")?, Val::Str("modern".into()))?;
    e.set("MODERN_DIR", assigned51.clone())?;
    let assigned52 = {
        let fun55 = {
            let fun58 = e.get("Path")?;
            let mut args56 = Vec::new();
            let mut kw57 = Vec::new();
            args56.push(e.get("_c14")?.attr("__file__")?);
            fun58.call(args56, kw57)?
        }
        .attr("resolve")?;
        let mut args53 = Vec::new();
        let mut kw54 = Vec::new();
        fun55.call(args53, kw54)?
    };
    e.set("C14_SOURCE", assigned52.clone())?;
    let assigned59 = {
        let mut s = Vec::new();
        s.push(unary("neg", Val::Float(113.5f64))?);
        s.push(Val::Float(107.5f64));
        Val::tuple(s)
    };
    let unpack60 = unpack(assigned59.clone(), 2)?;
    e.set("BOX_X0", unpack60[0].clone())?;
    e.set("BOX_X1", unpack60[1].clone())?;
    let assigned61 = {
        let mut s = Vec::new();
        s.push(Val::Float(5.0f64));
        s.push(Val::Float(467.0f64));
        Val::tuple(s)
    };
    let unpack62 = unpack(assigned61.clone(), 2)?;
    e.set("BOX_Y0", unpack62[0].clone())?;
    e.set("BOX_Y1", unpack62[1].clone())?;
    let assigned63 = {
        let mut s = Vec::new();
        s.push(unary("neg", Val::Float(6.0f64))?);
        s.push(Val::Float(361.0f64));
        Val::tuple(s)
    };
    let unpack64 = unpack(assigned63.clone(), 2)?;
    e.set("BOX_Z0", unpack64[0].clone())?;
    e.set("BOX_Z1", unpack64[1].clone())?;
    let assigned65 = binary(
        "truediv",
        binary("add", e.get("BOX_X0")?, e.get("BOX_X1")?)?,
        Val::Float(2.0f64),
    )?;
    e.set("BOX_MID_X", assigned65.clone())?;
    let assigned66 = {
        let fun69 = e.get("json")?.attr("loads")?;
        let mut args67 = Vec::new();
        let mut kw68 = Vec::new();
        args67.push({
            let fun72 = e.get("MACHINE_FACTS")?.attr("read_text")?;
            let mut args70 = Vec::new();
            let mut kw71 = Vec::new();
            fun72.call(args70, kw71)?
        });
        fun69.call(args67, kw68)?
    }
    .get(Val::Str("bodies".into()))?
    .get(Val::Str("funnel".into()))?;
    e.set("FUNNEL_BOUNDS", assigned66.clone())?;
    let assigned73 = {
        let fun76 = e.get("tuple")?;
        let mut args74 = Vec::new();
        let mut kw75 = Vec::new();
        args74.push(
            {
                let fun79 = e.get("json")?.attr("loads")?;
                let mut args77 = Vec::new();
                let mut kw78 = Vec::new();
                args77.push({
                    let fun82 = e.get("MACHINE_FACTS")?.attr("read_text")?;
                    let mut args80 = Vec::new();
                    let mut kw81 = Vec::new();
                    fun82.call(args80, kw81)?
                });
                fun79.call(args77, kw78)?
            }
            .get(Val::Str("box".into()))?
            .get(Val::Str("funnel".into()))?,
        );
        fun76.call(args74, kw75)?
    };
    e.set("FUNNEL_MOUTH", assigned73.clone())?;
    let assigned83 = Val::Float(476.5f64);
    e.set("PORT_FACE_Y", assigned83.clone())?;
    let assigned84 = {
        let mut s = Vec::new();
        s.push(Val::Float(336.2f64));
        s.push(Val::Float(273.8f64));
        Val::tuple(s)
    };
    let unpack85 = unpack(assigned84.clone(), 2)?;
    e.set("PORT_Z_UPPER", unpack85[0].clone())?;
    e.set("PORT_Z_LOWER", unpack85[1].clone())?;
    let assigned86 = {
        let mut s = Vec::new();
        s.push(unary("neg", Val::Float(78.1f64))?);
        s.push(unary("neg", Val::Float(37.8f64))?);
        Val::tuple(s)
    };
    let unpack87 = unpack(assigned86.clone(), 2)?;
    e.set("PORT_X_WEST", unpack87[0].clone())?;
    e.set("PORT_X_EAST", unpack87[1].clone())?;
    let assigned88 = {
        let mut s = Vec::new();
        s.push(Val::Float(60.0f64));
        s.push(Val::Float(40.0f64));
        Val::tuple(s)
    };
    let unpack89 = unpack(assigned88.clone(), 2)?;
    e.set("CLEAR_BEHIND", unpack89[0].clone())?;
    e.set("CLEAR_SIDE", unpack89[1].clone())?;
    let assigned90 = Val::Float(133.0f64);
    e.set("CYLINDER_LANE", assigned90.clone())?;
    let assigned91 = {
        let mut s = Vec::new();
        s.push(Val::Float(133.0f64));
        s.push(Val::Float(457.0f64));
        Val::tuple(s)
    };
    let unpack92 = unpack(assigned91.clone(), 2)?;
    e.set("CYLINDER_D", unpack92[0].clone())?;
    e.set("CYLINDER_H", unpack92[1].clone())?;
    let assigned93 = {
        let mut s = Vec::new();
        s.push(Val::Float(63.0f64));
        s.push(Val::Float(311.0f64));
        Val::tuple(s)
    };
    let unpack94 = unpack(assigned93.clone(), 2)?;
    e.set("FILTER_D", unpack94[0].clone())?;
    e.set("FILTER_L", unpack94[1].clone())?;
    let assigned95 = {
        let mut s = Vec::new();
        s.push(Val::Float(72.0f64));
        s.push(Val::Float(190.0f64));
        Val::tuple(s)
    };
    let unpack96 = unpack(assigned95.clone(), 2)?;
    e.set("BOTTLE_D", unpack96[0].clone())?;
    e.set("BOTTLE_H", unpack96[1].clone())?;
    let assigned97 = {
        let mut s = Vec::new();
        s.push(Val::Float(27.0f64));
        s.push(Val::Float(34.0f64));
        Val::tuple(s)
    };
    let unpack98 = unpack(assigned97.clone(), 2)?;
    e.set("BOTTLE_NECK_D", unpack98[0].clone())?;
    e.set("BOTTLE_NECK_H", unpack98[1].clone())?;
    let assigned99 = Val::Float(6.35f64);
    e.set("TUBE_D", assigned99.clone())?;
    let assigned100 = Val::Float(20.0f64);
    e.set("BOTTLE_TIP", assigned100.clone())?;
    let assigned101 = Val::Float(3.0f64);
    e.set("BOTTLE_CLEARANCE", assigned101.clone())?;
    let assigned102 = {
        let fun105 = e.get("cq")?.attr("Color")?;
        let mut args103 = Vec::new();
        let mut kw104 = Vec::new();
        args103.push(Val::Float(0.55f64));
        args103.push(Val::Float(0.55f64));
        args103.push(Val::Float(0.58f64));
        args103.push(Val::Float(1.0f64));
        fun105.call(args103, kw104)?
    };
    e.set("STONE", assigned102.clone())?;
    let assigned106 = {
        let fun109 = e.get("cq")?.attr("Color")?;
        let mut args107 = Vec::new();
        let mut kw108 = Vec::new();
        args107.push(Val::Float(0.74f64));
        args107.push(Val::Float(0.7f64));
        args107.push(Val::Float(0.64f64));
        args107.push(Val::Float(1.0f64));
        fun109.call(args107, kw108)?
    };
    e.set("CABINET", assigned106.clone())?;
    let assigned110 = {
        let fun113 = e.get("cq")?.attr("Color")?;
        let mut args111 = Vec::new();
        let mut kw112 = Vec::new();
        args111.push(Val::Float(0.84f64));
        args111.push(Val::Float(0.25f64));
        args111.push(Val::Float(0.31f64));
        args111.push(Val::Float(1.0f64));
        fun113.call(args111, kw112)?
    };
    e.set("CORAL", assigned110.clone())?;
    let assigned114 = {
        let fun117 = e.get("cq")?.attr("Color")?;
        let mut args115 = Vec::new();
        let mut kw116 = Vec::new();
        args115.push(Val::Float(0.78f64));
        args115.push(Val::Float(0.79f64));
        args115.push(Val::Float(0.82f64));
        args115.push(Val::Float(1.0f64));
        fun117.call(args115, kw116)?
    };
    e.set("STEEL", assigned114.clone())?;
    let assigned118 = {
        let fun121 = e.get("cq")?.attr("Color")?;
        let mut args119 = Vec::new();
        let mut kw120 = Vec::new();
        args119.push(Val::Float(0.72f64));
        args119.push(Val::Float(0.58f64));
        args119.push(Val::Float(0.28f64));
        args119.push(Val::Float(1.0f64));
        fun121.call(args119, kw120)?
    };
    e.set("BRASS", assigned118.clone())?;
    let assigned122 = {
        let fun125 = e.get("cq")?.attr("Color")?;
        let mut args123 = Vec::new();
        let mut kw124 = Vec::new();
        args123.push(Val::Float(0.9f64));
        args123.push(Val::Float(0.9f64));
        args123.push(Val::Float(0.93f64));
        args123.push(Val::Float(1.0f64));
        fun125.call(args123, kw124)?
    };
    e.set("WHITE_TUBE", assigned122.clone())?;
    let assigned126 = {
        let fun129 = e.get("cq")?.attr("Color")?;
        let mut args127 = Vec::new();
        let mut kw128 = Vec::new();
        args127.push(Val::Float(0.78f64));
        args127.push(Val::Float(0.2f64));
        args127.push(Val::Float(0.2f64));
        args127.push(Val::Float(1.0f64));
        fun129.call(args127, kw128)?
    };
    e.set("RED_TUBE", assigned126.clone())?;
    let assigned130 = {
        let fun133 = e.get("cq")?.attr("Color")?;
        let mut args131 = Vec::new();
        let mut kw132 = Vec::new();
        args131.push(Val::Float(0.16f64));
        args131.push(Val::Float(0.4f64));
        args131.push(Val::Float(0.75f64));
        args131.push(Val::Float(1.0f64));
        fun133.call(args131, kw132)?
    };
    e.set("BLUE_TUBE", assigned130.clone())?;
    let assigned134 = {
        let fun137 = e.get("cq")?.attr("Color")?;
        let mut args135 = Vec::new();
        let mut kw136 = Vec::new();
        args135.push(Val::Float(0.1f64));
        args135.push(Val::Float(0.1f64));
        args135.push(Val::Float(0.12f64));
        args135.push(Val::Float(1.0f64));
        fun137.call(args135, kw136)?
    };
    e.set("BLACK_PART", assigned134.clone())?;
    let assigned138 = {
        let fun141 = e.get("cq")?.attr("Color")?;
        let mut args139 = Vec::new();
        let mut kw140 = Vec::new();
        args139.push(Val::Float(0.3f64));
        args139.push(Val::Float(0.1f64));
        args139.push(Val::Float(0.13f64));
        args139.push(Val::Float(1.0f64));
        fun141.call(args139, kw140)?
    };
    e.set("CONCENTRATE", assigned138.clone())?;
    let assigned142 = {
        let fun145 = e.get("cq")?.attr("Color")?;
        let mut args143 = Vec::new();
        let mut kw144 = Vec::new();
        args143.push(Val::Float(0.86f64));
        args143.push(Val::Float(0.87f64));
        args143.push(Val::Float(0.9f64));
        args143.push(Val::Float(1.0f64));
        fun145.call(args143, kw144)?
    };
    e.set("BOTTLE_PET", assigned142.clone())?;
    let assigned146 = {
        let fun149 = e.get("cq")?.attr("Color")?;
        let mut args147 = Vec::new();
        let mut kw148 = Vec::new();
        args147.push(Val::Float(0.905f64));
        args147.push(Val::Float(0.915f64));
        args147.push(Val::Float(0.94f64));
        args147.push(Val::Float(1.0f64));
        fun149.call(args147, kw148)?
    };
    e.set("FILTER_BODY", assigned146.clone())?;
    let assigned150 = {
        let fun153 = e.get("cq")?.attr("Color")?;
        let mut args151 = Vec::new();
        let mut kw152 = Vec::new();
        args151.push(Val::Float(0.42f64));
        args151.push(Val::Float(0.45f64));
        args151.push(Val::Float(0.49f64));
        args151.push(Val::Float(1.0f64));
        fun153.call(args151, kw152)?
    };
    e.set("FILTER_CAP", assigned150.clone())?;
    let assigned154 = {
        let fun157 = e.get("cq")?.attr("Color")?;
        let mut args155 = Vec::new();
        let mut kw156 = Vec::new();
        args155.push(Val::Float(0.26f64));
        args155.push(Val::Float(0.27f64));
        args155.push(Val::Float(0.3f64));
        args155.push(Val::Float(1.0f64));
        fun157.call(args155, kw156)?
    };
    e.set("PRINTED", assigned154.clone())?;
    let assigned158 = {
        let fun161 = e.get("cq")?.attr("Color")?;
        let mut args159 = Vec::new();
        let mut kw160 = Vec::new();
        args159.push(Val::Float(0.4f64));
        args159.push(Val::Float(0.42f64));
        args159.push(Val::Float(0.47f64));
        args159.push(Val::Float(1.0f64));
        fun161.call(args159, kw160)?
    };
    e.set("CYLINDER", assigned158.clone())?;
    let assigned162 = {
        let fun165 = e.get("cq")?.attr("Color")?;
        let mut args163 = Vec::new();
        let mut kw164 = Vec::new();
        args163.push(Val::Float(0.43f64));
        args163.push(Val::Float(0.44f64));
        args163.push(Val::Float(0.43f64));
        args163.push(Val::Float(1.0f64));
        fun165.call(args163, kw164)?
    };
    e.set("ACETAL_GRAY", assigned162.clone())?;
    // _box
    e.set("_box", {
        let params = vec![
            ("x0".into(), None, false),
            ("y0".into(), None, false),
            ("z0".into(), None, false),
            ("sx".into(), None, false),
            ("sy".into(), None, false),
            ("sz".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun168 = {
                    let fun171 = e.get("cq")?.attr("Workplane")?;
                    let mut args169 = Vec::new();
                    let mut kw170 = Vec::new();
                    args169.push(Val::Str("XY".into()));
                    kw170.push(("origin".into(), {
                        let mut s = Vec::new();
                        s.push(e.get("x0")?);
                        s.push(e.get("y0")?);
                        s.push(e.get("z0")?);
                        Val::tuple(s)
                    }));
                    fun171.call(args169, kw170)?
                }
                .attr("box")?;
                let mut args166 = Vec::new();
                let mut kw167 = Vec::new();
                args166.push(e.get("sx")?);
                args166.push(e.get("sy")?);
                args166.push(e.get("sz")?);
                kw167.push(("centered".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Bool(false));
                    s.push(Val::Bool(false));
                    s.push(Val::Bool(false));
                    Val::tuple(s)
                }));
                fun168.call(args166, kw167)?
            });
            Ok(Val::None)
        })
    })?;
    // _cyl
    e.set("_cyl", {
        let params = vec![
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("z".into(), None, false),
            ("d".into(), None, false),
            ("length".into(), None, false),
            ("axis".into(), Some(Val::Str("Z".into())), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned172 = {
                let fun175 = {
                    let fun178 = {
                        let fun181 = e.get("cq")?.attr("Workplane")?;
                        let mut args179 = Vec::new();
                        let mut kw180 = Vec::new();
                        args179.push(Val::Str("XY".into()));
                        kw180.push(("origin".into(), {
                            let mut s = Vec::new();
                            s.push(e.get("x")?);
                            s.push(e.get("y")?);
                            s.push(e.get("z")?);
                            Val::tuple(s)
                        }));
                        fun181.call(args179, kw180)?
                    }
                    .attr("circle")?;
                    let mut args176 = Vec::new();
                    let mut kw177 = Vec::new();
                    args176.push(binary("truediv", e.get("d")?, Val::Float(2.0f64))?);
                    fun178.call(args176, kw177)?
                }
                .attr("extrude")?;
                let mut args173 = Vec::new();
                let mut kw174 = Vec::new();
                args173.push(e.get("length")?);
                fun175.call(args173, kw174)?
            };
            e.set("base", assigned172.clone())?;
            if {
                let v182 = e.get("axis")?;
                let v183 = Val::Str("Z".into());
                Val::Bool(compare("eq", v182.clone(), v183.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("base")?);
            }
            if {
                let v184 = e.get("axis")?;
                let v185 = Val::Str("Y".into());
                Val::Bool(compare("eq", v184.clone(), v185.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok({
                    let fun188 = e.get("base")?.attr("rotate")?;
                    let mut args186 = Vec::new();
                    let mut kw187 = Vec::new();
                    args186.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y")?);
                        s.push(e.get("z")?);
                        Val::tuple(s)
                    });
                    args186.push({
                        let mut s = Vec::new();
                        s.push(binary("add", e.get("x")?, Val::Float(1.0f64))?);
                        s.push(e.get("y")?);
                        s.push(e.get("z")?);
                        Val::tuple(s)
                    });
                    args186.push(unary("neg", Val::Float(90.0f64))?);
                    fun188.call(args186, kw187)?
                });
            }
            return Ok({
                let fun191 = e.get("base")?.attr("rotate")?;
                let mut args189 = Vec::new();
                let mut kw190 = Vec::new();
                args189.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y")?);
                    s.push(e.get("z")?);
                    Val::tuple(s)
                });
                args189.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(binary("add", e.get("y")?, Val::Float(1.0f64))?);
                    s.push(e.get("z")?);
                    Val::tuple(s)
                });
                args189.push(Val::Float(90.0f64));
                fun191.call(args189, kw190)?
            });
            Ok(Val::None)
        })
    })?;
    // _run
    e.set("_run", {
        let params = vec![
            ("points".into(), None, false),
            ("diameter".into(), Some(e.get("TUBE_D")?), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned192 = Val::None;
            e.set("solid", assigned192.clone())?;
            for item193 in {
                let fun244 = e.get("zip")?;
                let mut args242 = Vec::new();
                let mut kw243 = Vec::new();
                args242.push(e.get("points")?);
                args242.push(e.get("points")?.get(Val::Slice {
                    start: Some(Val::Int(1i64).integer()?),
                    stop: None,
                    step: 1,
                })?);
                fun244.call(args242, kw243)?
            }
            .iter()?
            {
                let unpack245 = unpack(item193, 2)?;
                e.set("a", unpack245[0].clone())?;
                e.set("b", unpack245[1].clone())?;
                let assigned194 = {
                    let e = e.child();
                    let out195 = Val::list(vec![]);
                    for item196 in {
                        let fun199 = e.get("range")?;
                        let mut args197 = Vec::new();
                        let mut kw198 = Vec::new();
                        args197.push(Val::Int(3i64));
                        fun199.call(args197, kw198)?
                    }
                    .iter()?
                    {
                        e.set("i", item196)?;
                        out195.attr("append")?.call(
                            vec![binary(
                                "sub",
                                e.get("b")?.get(e.get("i")?)?,
                                e.get("a")?.get(e.get("i")?)?,
                            )?],
                            vec![],
                        )?;
                    }
                    out195
                };
                e.set("deltas", assigned194.clone())?;
                let assigned200 = {
                    let e = e.child();
                    let out201 = Val::list(vec![]);
                    for item202 in {
                        let fun205 = e.get("enumerate")?;
                        let mut args203 = Vec::new();
                        let mut kw204 = Vec::new();
                        args203.push(e.get("deltas")?);
                        fun205.call(args203, kw204)?
                    }
                    .iter()?
                    {
                        let unpack206 = unpack(item202, 2)?;
                        e.set("i", unpack206[0].clone())?;
                        e.set("d", unpack206[1].clone())?;
                        if {
                            let v210 = {
                                let fun209 = e.get("abs")?;
                                let mut args207 = Vec::new();
                                let mut kw208 = Vec::new();
                                args207.push(e.get("d")?);
                                fun209.call(args207, kw208)?
                            };
                            let v211 = Val::Float(1e-06f64);
                            Val::Bool(compare("gt", v210.clone(), v211.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            out201.attr("append")?.call(vec![e.get("i")?], vec![])?;
                        }
                    }
                    out201
                };
                e.set("moving", assigned200.clone())?;
                if unary("not", e.get("moving")?)?.truthy()? {
                    continue;
                }
                if {
                    let v215 = {
                        let fun214 = e.get("len")?;
                        let mut args212 = Vec::new();
                        let mut kw213 = Vec::new();
                        args212.push(e.get("moving")?);
                        fun214.call(args212, kw213)?
                    };
                    let v216 = Val::Int(1i64);
                    Val::Bool(compare("ne", v215.clone(), v216.clone())?.truthy()?)
                }
                .truthy()?
                {
                    anyhow::bail!(
                        "{}",
                        val_string({
                            let fun219 = e.get("ValueError")?;
                            let mut args217 = Vec::new();
                            let mut kw218 = Vec::new();
                            args217.push({
                                let mut str220 = String::new();
                                str220.push_str(&format(&e.get("a")?, &String::new())?);
                                str220.push_str(" -> ");
                                str220.push_str(&format(&e.get("b")?, &String::new())?);
                                str220.push_str(" is not axis-aligned");
                                Val::Str(str220)
                            });
                            fun219.call(args217, kw218)?
                        })?
                    );
                }
                let assigned221 =
                    Val::Str("XYZ".into()).get(e.get("moving")?.get(Val::Int(0i64))?)?;
                e.set("axis", assigned221.clone())?;
                let assigned222 = e
                    .get("deltas")?
                    .get(e.get("moving")?.get(Val::Int(0i64))?)?;
                e.set("length", assigned222.clone())?;
                let assigned223 = {
                    let fun226 = e.get("list")?;
                    let mut args224 = Vec::new();
                    let mut kw225 = Vec::new();
                    args224.push(e.get("a")?);
                    fun226.call(args224, kw225)?
                };
                e.set("start", assigned223.clone())?;
                if {
                    let v227 = e.get("length")?;
                    let v228 = Val::Int(0i64);
                    Val::Bool(compare("lt", v227.clone(), v228.clone())?.truthy()?)
                }
                .truthy()?
                {
                    e.get("start")?.set(
                        e.get("moving")?.get(Val::Int(0i64))?,
                        binary(
                            "add",
                            e.get("start")?.get(e.get("moving")?.get(Val::Int(0i64))?)?,
                            e.get("length")?,
                        )?,
                    )?;
                }
                let assigned229 = {
                    let fun232 = e.get("_cyl")?;
                    let mut args230 = Vec::new();
                    let mut kw231 = Vec::new();
                    args230.push(e.get("start")?.get(Val::Int(0i64))?);
                    args230.push(e.get("start")?.get(Val::Int(1i64))?);
                    args230.push(e.get("start")?.get(Val::Int(2i64))?);
                    args230.push(e.get("diameter")?);
                    args230.push({
                        let fun235 = e.get("abs")?;
                        let mut args233 = Vec::new();
                        let mut kw234 = Vec::new();
                        args233.push(e.get("length")?);
                        fun235.call(args233, kw234)?
                    });
                    kw231.push(("axis".into(), e.get("axis")?));
                    fun232.call(args230, kw231)?
                };
                e.set("seg", assigned229.clone())?;
                let assigned236 = if {
                    let v237 = e.get("solid")?;
                    let v238 = Val::None;
                    Val::Bool(compare("is", v237.clone(), v238.clone())?.truthy()?)
                }
                .truthy()?
                {
                    e.get("seg")?
                } else {
                    {
                        let fun241 = e.get("solid")?.attr("union")?;
                        let mut args239 = Vec::new();
                        let mut kw240 = Vec::new();
                        args239.push(e.get("seg")?);
                        fun241.call(args239, kw240)?
                    }
                };
                e.set("solid", assigned236.clone())?;
            }
            for item246 in e
                .get("points")?
                .get(Val::Slice {
                    start: Some(Val::Int(1i64).integer()?),
                    stop: Some(unary("neg", Val::Int(1i64))?.integer()?),
                    step: 1,
                })?
                .iter()?
            {
                e.set("point", item246)?;
                let assigned247 = {
                    let fun250 = {
                        let fun253 = e.get("cq")?.attr("Workplane")?;
                        let mut args251 = Vec::new();
                        let mut kw252 = Vec::new();
                        args251.push(Val::Str("XY".into()));
                        kw252.push(("origin".into(), e.get("point")?));
                        fun253.call(args251, kw252)?
                    }
                    .attr("sphere")?;
                    let mut args248 = Vec::new();
                    let mut kw249 = Vec::new();
                    args248.push(binary("truediv", e.get("diameter")?, Val::Float(2.0f64))?);
                    fun250.call(args248, kw249)?
                };
                e.set("ball", assigned247.clone())?;
                let assigned254 = if {
                    let v255 = e.get("solid")?;
                    let v256 = Val::None;
                    Val::Bool(compare("is", v255.clone(), v256.clone())?.truthy()?)
                }
                .truthy()?
                {
                    e.get("ball")?
                } else {
                    {
                        let fun259 = e.get("solid")?.attr("union")?;
                        let mut args257 = Vec::new();
                        let mut kw258 = Vec::new();
                        args257.push(e.get("ball")?);
                        fun259.call(args257, kw258)?
                    }
                };
                e.set("solid", assigned254.clone())?;
            }
            return Ok(e.get("solid")?);
            Ok(Val::None)
        })
    })?;
    // _bend
    e.set("_bend", {
        let params = vec![
            ("points".into(), None, false),
            ("diameter".into(), Some(e.get("TUBE_D")?), false),
            ("radius".into(), Some(Val::Float(55.0f64)), false),
            ("steps".into(), Some(Val::Int(20i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned260 = {
                let mut s = Vec::new();
                s.push({
                    let fun263 = e.get("list")?;
                    let mut args261 = Vec::new();
                    let mut kw262 = Vec::new();
                    args261.push(e.get("points")?.get(Val::Int(0i64))?);
                    fun263.call(args261, kw262)?
                });
                Val::list(s)
            };
            e.set("samples", assigned260.clone())?;
            for item264 in {
                let fun327 = e.get("enumerate")?;
                let mut args325 = Vec::new();
                let mut kw326 = Vec::new();
                args325.push(e.get("points")?.get(Val::Slice {
                    start: Some(Val::Int(1i64).integer()?),
                    stop: Some(unary("neg", Val::Int(1i64))?.integer()?),
                    step: 1,
                })?);
                kw326.push(("start".into(), Val::Int(1i64)));
                fun327.call(args325, kw326)?
            }
            .iter()?
            {
                let unpack328 = unpack(item264, 2)?;
                e.set("i", unpack328[0].clone())?;
                e.set("corner", unpack328[1].clone())?;
                let assigned265 = {
                    let fun268 = e.get("_unit")?;
                    let mut args266 = Vec::new();
                    let mut kw267 = Vec::new();
                    args266.push({
                        let e = e.child();
                        let out269 = Val::list(vec![]);
                        for item270 in {
                            let fun273 = e.get("range")?;
                            let mut args271 = Vec::new();
                            let mut kw272 = Vec::new();
                            args271.push(Val::Int(3i64));
                            fun273.call(args271, kw272)?
                        }
                        .iter()?
                        {
                            e.set("k", item270)?;
                            out269.attr("append")?.call(
                                vec![binary(
                                    "sub",
                                    e.get("corner")?.get(e.get("k")?)?,
                                    e.get("points")?
                                        .get(binary("sub", e.get("i")?, Val::Int(1i64))?)?
                                        .get(e.get("k")?)?,
                                )?],
                                vec![],
                            )?;
                        }
                        out269
                    });
                    fun268.call(args266, kw267)?
                };
                e.set("u", assigned265.clone())?;
                let assigned274 = {
                    let fun277 = e.get("_unit")?;
                    let mut args275 = Vec::new();
                    let mut kw276 = Vec::new();
                    args275.push({
                        let e = e.child();
                        let out278 = Val::list(vec![]);
                        for item279 in {
                            let fun282 = e.get("range")?;
                            let mut args280 = Vec::new();
                            let mut kw281 = Vec::new();
                            args280.push(Val::Int(3i64));
                            fun282.call(args280, kw281)?
                        }
                        .iter()?
                        {
                            e.set("k", item279)?;
                            out278.attr("append")?.call(
                                vec![binary(
                                    "sub",
                                    e.get("points")?
                                        .get(binary("add", e.get("i")?, Val::Int(1i64))?)?
                                        .get(e.get("k")?)?,
                                    e.get("corner")?.get(e.get("k")?)?,
                                )?],
                                vec![],
                            )?;
                        }
                        out278
                    });
                    fun277.call(args275, kw276)?
                };
                e.set("v", assigned274.clone())?;
                if {
                    let v295 = {
                        let fun285 = e.get("abs")?;
                        let mut args283 = Vec::new();
                        let mut kw284 = Vec::new();
                        args283.push({
                            let fun288 = e.get("sum")?;
                            let mut args286 = Vec::new();
                            let mut kw287 = Vec::new();
                            args286.push({
                                let e = e.child();
                                let out289 = Val::list(vec![]);
                                for item290 in {
                                    let fun293 = e.get("zip")?;
                                    let mut args291 = Vec::new();
                                    let mut kw292 = Vec::new();
                                    args291.push(e.get("u")?);
                                    args291.push(e.get("v")?);
                                    fun293.call(args291, kw292)?
                                }
                                .iter()?
                                {
                                    let unpack294 = unpack(item290, 2)?;
                                    e.set("a", unpack294[0].clone())?;
                                    e.set("b", unpack294[1].clone())?;
                                    out289.attr("append")?.call(
                                        vec![binary("mul", e.get("a")?, e.get("b")?)?],
                                        vec![],
                                    )?;
                                }
                                out289
                            });
                            fun288.call(args286, kw287)?
                        });
                        fun285.call(args283, kw284)?
                    };
                    let v296 = Val::Float(1e-06f64);
                    Val::Bool(compare("gt", v295.clone(), v296.clone())?.truthy()?)
                }
                .truthy()?
                {
                    anyhow::bail!(
                        "{}",
                        val_string({
                            let fun299 = e.get("ValueError")?;
                            let mut args297 = Vec::new();
                            let mut kw298 = Vec::new();
                            args297.push(Val::Str("a bend turns a square corner".into()));
                            fun299.call(args297, kw298)?
                        })?
                    );
                }
                let assigned300 = {
                    let e = e.child();
                    let out301 = Val::list(vec![]);
                    for item302 in {
                        let fun305 = e.get("range")?;
                        let mut args303 = Vec::new();
                        let mut kw304 = Vec::new();
                        args303.push(Val::Int(3i64));
                        fun305.call(args303, kw304)?
                    }
                    .iter()?
                    {
                        e.set("k", item302)?;
                        out301.attr("append")?.call(
                            vec![binary(
                                "add",
                                binary(
                                    "sub",
                                    e.get("corner")?.get(e.get("k")?)?,
                                    binary("mul", e.get("u")?.get(e.get("k")?)?, e.get("radius")?)?,
                                )?,
                                binary("mul", e.get("v")?.get(e.get("k")?)?, e.get("radius")?)?,
                            )?],
                            vec![],
                        )?;
                    }
                    out301
                };
                e.set("centre", assigned300.clone())?;
                for item306 in {
                    let fun324 = e.get("range")?;
                    let mut args322 = Vec::new();
                    let mut kw323 = Vec::new();
                    args322.push(binary("add", e.get("steps")?, Val::Int(1i64))?);
                    fun324.call(args322, kw323)?
                }
                .iter()?
                {
                    e.set("step", item306)?;
                    let assigned307 = binary(
                        "truediv",
                        binary(
                            "mul",
                            binary("truediv", e.get("math")?.attr("pi")?, Val::Float(2.0f64))?,
                            e.get("step")?,
                        )?,
                        e.get("steps")?,
                    )?;
                    e.set("t", assigned307.clone())?;
                    {
                        let fun310 = e.get("samples")?.attr("append")?;
                        let mut args308 = Vec::new();
                        let mut kw309 = Vec::new();
                        args308.push({
                            let e = e.child();
                            let out311 = Val::list(vec![]);
                            for item312 in {
                                let fun315 = e.get("range")?;
                                let mut args313 = Vec::new();
                                let mut kw314 = Vec::new();
                                args313.push(Val::Int(3i64));
                                fun315.call(args313, kw314)?
                            }
                            .iter()?
                            {
                                e.set("k", item312)?;
                                out311.attr("append")?.call(
                                    vec![binary(
                                        "add",
                                        e.get("centre")?.get(e.get("k")?)?,
                                        binary(
                                            "mul",
                                            e.get("radius")?,
                                            binary(
                                                "add",
                                                binary(
                                                    "mul",
                                                    unary("neg", e.get("v")?.get(e.get("k")?)?)?,
                                                    {
                                                        let fun318 = e.get("math")?.attr("cos")?;
                                                        let mut args316 = Vec::new();
                                                        let mut kw317 = Vec::new();
                                                        args316.push(e.get("t")?);
                                                        fun318.call(args316, kw317)?
                                                    },
                                                )?,
                                                binary("mul", e.get("u")?.get(e.get("k")?)?, {
                                                    let fun321 = e.get("math")?.attr("sin")?;
                                                    let mut args319 = Vec::new();
                                                    let mut kw320 = Vec::new();
                                                    args319.push(e.get("t")?);
                                                    fun321.call(args319, kw320)?
                                                })?,
                                            )?,
                                        )?,
                                    )?],
                                    vec![],
                                )?;
                            }
                            out311
                        });
                        fun310.call(args308, kw309)?
                    };
                }
            }
            {
                let fun331 = e.get("samples")?.attr("append")?;
                let mut args329 = Vec::new();
                let mut kw330 = Vec::new();
                args329.push({
                    let fun334 = e.get("list")?;
                    let mut args332 = Vec::new();
                    let mut kw333 = Vec::new();
                    args332.push(e.get("points")?.get(unary("neg", Val::Int(1i64))?)?);
                    fun334.call(args332, kw333)?
                });
                fun331.call(args329, kw330)?
            };
            let assigned335 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("pieces", assigned335.clone())?;
            for item336 in {
                let fun357 = e.get("zip")?;
                let mut args355 = Vec::new();
                let mut kw356 = Vec::new();
                args355.push(e.get("samples")?);
                args355.push(e.get("samples")?.get(Val::Slice {
                    start: Some(Val::Int(1i64).integer()?),
                    stop: None,
                    step: 1,
                })?);
                fun357.call(args355, kw356)?
            }
            .iter()?
            {
                let unpack358 = unpack(item336, 2)?;
                e.set("a", unpack358[0].clone())?;
                e.set("b", unpack358[1].clone())?;
                let assigned337 = {
                    let fun340 = e.get("cq")?.attr("Vector")?;
                    let mut args338 = Vec::new();
                    let mut kw339 = Vec::new();
                    args338.push(binary(
                        "sub",
                        e.get("b")?.get(Val::Int(0i64))?,
                        e.get("a")?.get(Val::Int(0i64))?,
                    )?);
                    args338.push(binary(
                        "sub",
                        e.get("b")?.get(Val::Int(1i64))?,
                        e.get("a")?.get(Val::Int(1i64))?,
                    )?);
                    args338.push(binary(
                        "sub",
                        e.get("b")?.get(Val::Int(2i64))?,
                        e.get("a")?.get(Val::Int(2i64))?,
                    )?);
                    fun340.call(args338, kw339)?
                };
                e.set("span", assigned337.clone())?;
                if {
                    let v341 = e.get("span")?.attr("Length")?;
                    let v342 = Val::Float(1e-09f64);
                    Val::Bool(compare("lt", v341.clone(), v342.clone())?.truthy()?)
                }
                .truthy()?
                {
                    continue;
                }
                {
                    let fun345 = e.get("pieces")?.attr("append")?;
                    let mut args343 = Vec::new();
                    let mut kw344 = Vec::new();
                    args343.push({
                        let fun348 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                        let mut args346 = Vec::new();
                        let mut kw347 = Vec::new();
                        args346.push(binary("truediv", e.get("diameter")?, Val::Float(2.0f64))?);
                        args346.push(e.get("span")?.attr("Length")?);
                        args346.push({
                            let fun351 = e.get("cq")?.attr("Vector")?;
                            let mut args349 = Vec::new();
                            let mut kw350 = Vec::new();
                            args349.extend(e.get("a")?.iter()?);
                            fun351.call(args349, kw350)?
                        });
                        args346.push({
                            let fun354 = e.get("span")?.attr("normalized")?;
                            let mut args352 = Vec::new();
                            let mut kw353 = Vec::new();
                            fun354.call(args352, kw353)?
                        });
                        fun348.call(args346, kw347)?
                    });
                    fun345.call(args343, kw344)?
                };
            }
            for item359 in e
                .get("samples")?
                .get(Val::Slice {
                    start: Some(Val::Int(1i64).integer()?),
                    stop: Some(unary("neg", Val::Int(1i64))?.integer()?),
                    step: 1,
                })?
                .iter()?
            {
                e.set("point", item359)?;
                {
                    let fun362 = e.get("pieces")?.attr("append")?;
                    let mut args360 = Vec::new();
                    let mut kw361 = Vec::new();
                    args360.push({
                        let fun365 = e.get("cq")?.attr("Solid")?.attr("makeSphere")?;
                        let mut args363 = Vec::new();
                        let mut kw364 = Vec::new();
                        args363.push(binary("truediv", e.get("diameter")?, Val::Float(2.0f64))?);
                        args363.push({
                            let fun368 = e.get("cq")?.attr("Vector")?;
                            let mut args366 = Vec::new();
                            let mut kw367 = Vec::new();
                            args366.extend(e.get("point")?.iter()?);
                            fun368.call(args366, kw367)?
                        });
                        kw364.push(("angleDegrees1".into(), unary("neg", Val::Float(90.0f64))?));
                        fun365.call(args363, kw364)?
                    });
                    fun362.call(args360, kw361)?
                };
            }
            return Ok({
                let fun371 = e.get("cq")?.attr("Compound")?.attr("makeCompound")?;
                let mut args369 = Vec::new();
                let mut kw370 = Vec::new();
                args369.push(e.get("pieces")?);
                fun371.call(args369, kw370)?
            });
            Ok(Val::None)
        })
    })?;
    // _unit
    e.set("_unit", {
        let params = vec![("vec".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned372 = {
                let fun375 = e.get("math")?.attr("sqrt")?;
                let mut args373 = Vec::new();
                let mut kw374 = Vec::new();
                args373.push({
                    let fun378 = e.get("sum")?;
                    let mut args376 = Vec::new();
                    let mut kw377 = Vec::new();
                    args376.push({
                        let e = e.child();
                        let out379 = Val::list(vec![]);
                        for item380 in e.get("vec")?.iter()? {
                            e.set("c", item380)?;
                            out379
                                .attr("append")?
                                .call(vec![binary("mul", e.get("c")?, e.get("c")?)?], vec![])?;
                        }
                        out379
                    });
                    fun378.call(args376, kw377)?
                });
                fun375.call(args373, kw374)?
            };
            e.set("mag", assigned372.clone())?;
            return Ok({
                let e = e.child();
                let out381 = Val::list(vec![]);
                for item382 in e.get("vec")?.iter()? {
                    e.set("c", item382)?;
                    out381
                        .attr("append")?
                        .call(vec![binary("truediv", e.get("c")?, e.get("mag")?)?], vec![])?;
                }
                out381
            });
            Ok(Val::None)
        })
    })?;
    // _add
    e.set("_add", {
        let params = vec![
            ("assembly".into(), None, false),
            ("shape".into(), None, false),
            ("name".into(), None, false),
            ("color".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v383 = e.get("shape")?;
                let v384 = Val::None;
                Val::Bool(compare("is_not", v383.clone(), v384.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun387 = e.get("assembly")?.attr("add")?;
                    let mut args385 = Vec::new();
                    let mut kw386 = Vec::new();
                    args385.push(e.get("shape")?);
                    kw386.push(("name".into(), e.get("name")?));
                    kw386.push(("color".into(), e.get("color")?));
                    fun387.call(args385, kw386)?
                };
            }
            Ok(Val::None)
        })
    })?;
    // _machine
    e.set("_machine", {
        let params = vec![("assembly".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun390 = e.get("_cad_art")?.attr("borrow")?;
                let mut args388 = Vec::new();
                let mut kw389 = Vec::new();
                args388.push(e.get("assembly")?);
                args388.push({
                    let fun393 = e.get("_cad_art")?.attr("machine_bodies")?;
                    let mut args391 = Vec::new();
                    let mut kw392 = Vec::new();
                    fun393.call(args391, kw392)?
                });
                fun390.call(args388, kw389)?
            });
            Ok(Val::None)
        })
    })?;
    // _hex
    e.set("_hex", {
        let params = vec![
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("z".into(), None, false),
            ("across_flats".into(), None, false),
            ("length".into(), None, false),
            ("axis".into(), Some(Val::Str("Z".into())), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned394 = binary("truediv", e.get("across_flats")?, {
                let fun397 = e.get("math")?.attr("sqrt")?;
                let mut args395 = Vec::new();
                let mut kw396 = Vec::new();
                args395.push(Val::Float(3.0f64));
                fun397.call(args395, kw396)?
            })?;
            e.set("r", assigned394.clone())?;
            let assigned398 = {
                let e = e.child();
                let out399 = Val::list(vec![]);
                for item400 in {
                    let fun403 = e.get("range")?;
                    let mut args401 = Vec::new();
                    let mut kw402 = Vec::new();
                    args401.push(Val::Int(0i64));
                    args401.push(Val::Int(360i64));
                    args401.push(Val::Int(60i64));
                    fun403.call(args401, kw402)?
                }
                .iter()?
                {
                    e.set("a", item400)?;
                    out399.attr("append")?.call(
                        vec![{
                            let mut s = Vec::new();
                            s.push(binary("mul", e.get("r")?, {
                                let fun406 = e.get("math")?.attr("cos")?;
                                let mut args404 = Vec::new();
                                let mut kw405 = Vec::new();
                                args404.push({
                                    let fun409 = e.get("math")?.attr("radians")?;
                                    let mut args407 = Vec::new();
                                    let mut kw408 = Vec::new();
                                    args407.push(e.get("a")?);
                                    fun409.call(args407, kw408)?
                                });
                                fun406.call(args404, kw405)?
                            })?);
                            s.push(binary("mul", e.get("r")?, {
                                let fun412 = e.get("math")?.attr("sin")?;
                                let mut args410 = Vec::new();
                                let mut kw411 = Vec::new();
                                args410.push({
                                    let fun415 = e.get("math")?.attr("radians")?;
                                    let mut args413 = Vec::new();
                                    let mut kw414 = Vec::new();
                                    args413.push(e.get("a")?);
                                    fun415.call(args413, kw414)?
                                });
                                fun412.call(args410, kw411)?
                            })?);
                            Val::tuple(s)
                        }],
                        vec![],
                    )?;
                }
                out399
            };
            e.set("pts", assigned398.clone())?;
            let assigned416 = {
                let fun419 = {
                    let fun422 = {
                        let fun425 = {
                            let fun428 = e.get("cq")?.attr("Workplane")?;
                            let mut args426 = Vec::new();
                            let mut kw427 = Vec::new();
                            args426.push(Val::Str("XY".into()));
                            kw427.push(("origin".into(), {
                                let mut s = Vec::new();
                                s.push(e.get("x")?);
                                s.push(e.get("y")?);
                                s.push(e.get("z")?);
                                Val::tuple(s)
                            }));
                            fun428.call(args426, kw427)?
                        }
                        .attr("polyline")?;
                        let mut args423 = Vec::new();
                        let mut kw424 = Vec::new();
                        args423.push(e.get("pts")?);
                        fun425.call(args423, kw424)?
                    }
                    .attr("close")?;
                    let mut args420 = Vec::new();
                    let mut kw421 = Vec::new();
                    fun422.call(args420, kw421)?
                }
                .attr("extrude")?;
                let mut args417 = Vec::new();
                let mut kw418 = Vec::new();
                args417.push(e.get("length")?);
                fun419.call(args417, kw418)?
            };
            e.set("base", assigned416.clone())?;
            if {
                let v429 = e.get("axis")?;
                let v430 = Val::Str("Z".into());
                Val::Bool(compare("eq", v429.clone(), v430.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("base")?);
            }
            if {
                let v431 = e.get("axis")?;
                let v432 = Val::Str("Y".into());
                Val::Bool(compare("eq", v431.clone(), v432.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok({
                    let fun435 = e.get("base")?.attr("rotate")?;
                    let mut args433 = Vec::new();
                    let mut kw434 = Vec::new();
                    args433.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y")?);
                        s.push(e.get("z")?);
                        Val::tuple(s)
                    });
                    args433.push({
                        let mut s = Vec::new();
                        s.push(binary("add", e.get("x")?, Val::Float(1.0f64))?);
                        s.push(e.get("y")?);
                        s.push(e.get("z")?);
                        Val::tuple(s)
                    });
                    args433.push(unary("neg", Val::Float(90.0f64))?);
                    fun435.call(args433, kw434)?
                });
            }
            return Ok({
                let fun438 = e.get("base")?.attr("rotate")?;
                let mut args436 = Vec::new();
                let mut kw437 = Vec::new();
                args436.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y")?);
                    s.push(e.get("z")?);
                    Val::tuple(s)
                });
                args436.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(binary("add", e.get("y")?, Val::Float(1.0f64))?);
                    s.push(e.get("z")?);
                    Val::tuple(s)
                });
                args436.push(Val::Float(90.0f64));
                fun438.call(args436, kw437)?
            });
            Ok(Val::None)
        })
    })?;
    // _floor
    e.set("_floor", {
        let params = vec![
            ("x0".into(), None, false),
            ("y0".into(), None, false),
            ("sx".into(), None, false),
            ("sy".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun441 = e.get("_box")?;
                let mut args439 = Vec::new();
                let mut kw440 = Vec::new();
                args439.push(e.get("x0")?);
                args439.push(e.get("y0")?);
                args439.push(unary("neg", Val::Float(24.0f64))?);
                args439.push(e.get("sx")?);
                args439.push(e.get("sy")?);
                args439.push(Val::Float(18.0f64));
                fun441.call(args439, kw440)?
            });
            Ok(Val::None)
        })
    })?;
    let assigned442 = {
        let fun445 = e.get("frozenset")?;
        let mut args443 = Vec::new();
        let mut kw444 = Vec::new();
        args443.push({
            let mut s = Vec::new();
            s.push(Val::Str("bulkhead-drain".into()));
            s.push(Val::Str("c14-inlet".into()));
            s.push(Val::Str("keystone-jack".into()));
            s.push(Val::Str("co2-inlet".into()));
            s.push(Val::Str("bulkhead-water".into()));
            s.push(Val::Str("bulkhead-carb".into()));
            s.push(Val::Str("bulkhead-flavor-a".into()));
            s.push(Val::Str("bulkhead-flavor-b".into()));
            s.push(Val::Str("funnel".into()));
            s.push(Val::Str("funnel-cover".into()));
            s.push(Val::Str("nameplate".into()));
            s.push(Val::Str("nameplate-ink".into()));
                s.push(Val::Str("nameplate-screw-1".into()));
                s.push(Val::Str("nameplate-insert-1".into()));
                s.push(Val::Str("nameplate-screw-2".into()));
                s.push(Val::Str("nameplate-insert-2".into()));
                s.push(Val::Str("nameplate-screw-3".into()));
                s.push(Val::Str("nameplate-insert-3".into()));
                s.push(Val::Str("nameplate-screw-4".into()));
                s.push(Val::Str("nameplate-insert-4".into()));

            s.push(Val::Str("enclosure-back-bottom".into()));
            s.push(Val::Str("enclosure-back-top".into()));
            Val::set_values(s)
        });
        fun445.call(args443, kw444)?
    };
    e.set("REAR_CHILDREN", assigned442.clone())?;
    let assigned446 = Val::Str("bulkhead-ring-".into());
    e.set("REAR_RING_PREFIX", assigned446.clone())?;
    let assigned447 = {
        let fun450 = e.get("json")?.attr("loads")?;
        let mut args448 = Vec::new();
        let mut kw449 = Vec::new();
        args448.push({
            let fun453 = e.get("MACHINE_FACTS")?.attr("read_text")?;
            let mut args451 = Vec::new();
            let mut kw452 = Vec::new();
            fun453.call(args451, kw452)?
        });
        fun450.call(args448, kw449)?
    };
    e.set("_FACTS", assigned447.clone())?;
    let assigned454 = e
        .get("_FACTS")?
        .get(Val::Str("box".into()))?
        .get(Val::Str("outer".into()))?
        .get(Val::Int(3i64))?;
    e.set("REAR_FACE_Y", assigned454.clone())?;
    let assigned455 = {
        let fun458 = e.get("tuple")?;
        let mut args456 = Vec::new();
        let mut kw457 = Vec::new();
        args456.push(
            e.get("_FACTS")?
                .get(Val::Str("constants".into()))?
                .get(Val::Str("C14_STATION".into()))?,
        );
        fun458.call(args456, kw457)?
    };
    e.set("C14_STATION", assigned455.clone())?;
    let assigned459 = Val::Float(0.35f64);
    e.set("C13_SLIP", assigned459.clone())?;
    let assigned460 = Val::Float(3.5f64);
    e.set("C13_WALL", assigned460.clone())?;
    let assigned461 = Val::Float(31.0f64);
    e.set("C13_BODY_LEN", assigned461.clone())?;
    let assigned462 = Val::Float(9.5f64);
    e.set("C13_NOSE_LEN", assigned462.clone())?;
    let assigned463 = Val::Float(30.0f64);
    e.set("C13_BOOT_LEN", assigned463.clone())?;
    let assigned464 = {
        let mut s = Vec::new();
        s.push(Val::Float(14.5f64));
        s.push(Val::Float(9.0f64));
        Val::tuple(s)
    };
    e.set("C13_BOOT_D", assigned464.clone())?;
    let assigned465 = Val::Float(7.8f64);
    e.set("C13_CABLE_D", assigned465.clone())?;
    let assigned466 = {
        let fun469 = e.get("cq")?.attr("Color")?;
        let mut args467 = Vec::new();
        let mut kw468 = Vec::new();
        args467.push(Val::Float(0.035f64));
        args467.push(Val::Float(0.038f64));
        args467.push(Val::Float(0.043f64));
        args467.push(Val::Float(1.0f64));
        fun469.call(args467, kw468)?
    };
    e.set("CORDSET", assigned466.clone())?;
    // _rear_face
    e.set("_rear_face", {
        let params = vec![("assembly".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun472 = e.get("_cad_art")?.attr("borrow")?;
                let mut args470 = Vec::new();
                let mut kw471 = Vec::new();
                args470.push(e.get("assembly")?);
                args470.push({
                    let fun475 = e.get("_cad_art")?.attr("machine_bodies")?;
                    let mut args473 = Vec::new();
                    let mut kw474 = Vec::new();
                    args473.push({
                        let params = vec![("name".into(), None, false)];
                        let outer = e.clone();
                        let runtime = rt.clone();
                        Val::function(move |args, kwargs| {
                            let rt = runtime.clone();
                            let e = bind(&outer, &params, args, kwargs, None, None)?;
                            let _frame = rt.frame(&outer);
                            return Ok({
                                let v479 = {
                                    let v480 = e.get("name")?;
                                    let v481 = e.get("REAR_CHILDREN")?;
                                    Val::Bool(compare("in", v480.clone(), v481.clone())?.truthy()?)
                                };
                                if v479.truthy()? {
                                    v479
                                } else {
                                    {
                                        let fun478 = e.get("name")?.attr("startswith")?;
                                        let mut args476 = Vec::new();
                                        let mut kw477 = Vec::new();
                                        args476.push(e.get("REAR_RING_PREFIX")?);
                                        fun478.call(args476, kw477)?
                                    }
                                }
                            });
                            Ok(Val::None)
                        })
                    });
                    fun475.call(args473, kw474)?
                });
                fun472.call(args470, kw471)?
            });
            Ok(Val::None)
        })
    })?;
    // _prism
    e.set("_prism", {
        let params = vec![
            ("w".into(), None, false),
            ("h".into(), None, false),
            ("r".into(), None, false),
            ("length".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun484 = {
                    let fun487 = {
                        let fun490 = {
                            let fun493 = {
                                let fun496 = e.get("cq")?.attr("Workplane")?;
                                let mut args494 = Vec::new();
                                let mut kw495 = Vec::new();
                                args494.push(e.get("xz_plane_y_up")?);
                                fun496.call(args494, kw495)?
                            }
                            .attr("rect")?;
                            let mut args491 = Vec::new();
                            let mut kw492 = Vec::new();
                            args491.push(e.get("w")?);
                            args491.push(e.get("h")?);
                            fun493.call(args491, kw492)?
                        }
                        .attr("extrude")?;
                        let mut args488 = Vec::new();
                        let mut kw489 = Vec::new();
                        args488.push(e.get("length")?);
                        fun490.call(args488, kw489)?
                    }
                    .attr("edges")?;
                    let mut args485 = Vec::new();
                    let mut kw486 = Vec::new();
                    args485.push(Val::Str("|Y".into()));
                    fun487.call(args485, kw486)?
                }
                .attr("fillet")?;
                let mut args482 = Vec::new();
                let mut kw483 = Vec::new();
                args482.push(e.get("r")?);
                fun484.call(args482, kw483)?
            });
            Ok(Val::None)
        })
    })?;
    // _cable
    e.set("_cable", {
        let params = vec![
            ("points".into(), None, false),
            ("diameter".into(), None, false),
            ("tangents".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned497 = {
                let e = e.child();
                let out498 = Val::list(vec![]);
                for item499 in e.get("points")?.iter()? {
                    e.set("point", item499)?;
                    out498.attr("append")?.call(
                        vec![{
                            let fun502 = e.get("cq")?.attr("Vector")?;
                            let mut args500 = Vec::new();
                            let mut kw501 = Vec::new();
                            args500.extend(e.get("point")?.iter()?);
                            fun502.call(args500, kw501)?
                        }],
                        vec![],
                    )?;
                }
                out498
            };
            e.set("vectors", assigned497.clone())?;
            let assigned503 = {
                let fun506 = e.get("cq")?.attr("Edge")?.attr("makeSpline")?;
                let mut args504 = Vec::new();
                let mut kw505 = Vec::new();
                args504.push(e.get("vectors")?);
                kw505.push(("tangents".into(), {
                    let e = e.child();
                    let out507 = Val::list(vec![]);
                    for item508 in e.get("tangents")?.iter()? {
                        e.set("t", item508)?;
                        out507.attr("append")?.call(
                            vec![{
                                let fun511 = e.get("cq")?.attr("Vector")?;
                                let mut args509 = Vec::new();
                                let mut kw510 = Vec::new();
                                args509.extend(e.get("t")?.iter()?);
                                fun511.call(args509, kw510)?
                            }],
                            vec![],
                        )?;
                    }
                    out507
                }));
                kw505.push(("scale".into(), Val::Bool(false)));
                fun506.call(args504, kw505)?
            };
            e.set("path", assigned503.clone())?;
            let assigned512 = {
                let fun515 = e.get("cq")?.attr("Wire")?.attr("makeCircle")?;
                let mut args513 = Vec::new();
                let mut kw514 = Vec::new();
                args513.push(binary("truediv", e.get("diameter")?, Val::Float(2.0f64))?);
                args513.push(e.get("vectors")?.get(Val::Int(0i64))?);
                args513.push({
                    let fun518 = e.get("cq")?.attr("Vector")?;
                    let mut args516 = Vec::new();
                    let mut kw517 = Vec::new();
                    args516.extend(e.get("tangents")?.get(Val::Int(0i64))?.iter()?);
                    fun518.call(args516, kw517)?
                });
                fun515.call(args513, kw514)?
            };
            e.set("profile", assigned512.clone())?;
            return Ok({
                let fun521 = e.get("cq")?.attr("Solid")?.attr("sweep")?;
                let mut args519 = Vec::new();
                let mut kw520 = Vec::new();
                args519.push(e.get("profile")?);
                args519.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                args519.push(e.get("path")?);
                kw520.push(("makeSolid".into(), Val::Bool(true)));
                kw520.push(("isFrenet".into(), Val::Bool(false)));
                fun521.call(args519, kw520)?
            });
            Ok(Val::None)
        })
    })?;
    // _c13_cordset
    e.set("_c13_cordset", {
        let params = vec![("gap".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned522 = e.get("C14_STATION")?;
            let unpack523 = unpack(assigned522.clone(), 2)?;
            e.set("x", unpack523[0].clone())?;
            e.set("z", unpack523[1].clone())?;
            let assigned524 = binary("add", e.get("REAR_FACE_Y")?, e.get("gap")?)?;
            e.set("y0", assigned524.clone())?;
            let assigned525 = binary(
                "sub",
                e.get("_c14")?.attr("MOUTH_W")?,
                binary("mul", Val::Float(2.0f64), e.get("C13_SLIP")?)?,
            )?;
            e.set("nose_w", assigned525.clone())?;
            let assigned526 = binary(
                "sub",
                e.get("_c14")?.attr("MOUTH_H")?,
                binary("mul", Val::Float(2.0f64), e.get("C13_SLIP")?)?,
            )?;
            e.set("nose_h", assigned526.clone())?;
            let assigned527 = {
                let fun530 = e.get("_prism")?;
                let mut args528 = Vec::new();
                let mut kw529 = Vec::new();
                args528.push(binary(
                    "add",
                    e.get("nose_w")?,
                    binary("mul", Val::Float(2.0f64), e.get("C13_WALL")?)?,
                )?);
                args528.push(binary(
                    "add",
                    e.get("nose_h")?,
                    binary("mul", Val::Float(2.0f64), e.get("C13_WALL")?)?,
                )?);
                args528.push(Val::Float(3.0f64));
                args528.push(e.get("C13_BODY_LEN")?);
                fun530.call(args528, kw529)?
            };
            e.set("body", assigned527.clone())?;
            let assigned531 = {
                let fun534 = {
                    let fun537 = e.get("body")?.attr("faces")?;
                    let mut args535 = Vec::new();
                    let mut kw536 = Vec::new();
                    args535.push(Val::Str(">Y".into()));
                    fun537.call(args535, kw536)?
                }
                .attr("chamfer")?;
                let mut args532 = Vec::new();
                let mut kw533 = Vec::new();
                args532.push(Val::Float(1.2f64));
                fun534.call(args532, kw533)?
            };
            e.set("body", assigned531.clone())?;
            let assigned538 = {
                let fun541 = {
                    let fun544 = e.get("_prism")?;
                    let mut args542 = Vec::new();
                    let mut kw543 = Vec::new();
                    args542.push(e.get("nose_w")?);
                    args542.push(e.get("nose_h")?);
                    args542.push(binary(
                        "sub",
                        e.get("_c14")?.attr("MOUTH_TOP_R")?,
                        e.get("C13_SLIP")?,
                    )?);
                    args542.push(e.get("C13_NOSE_LEN")?);
                    fun544.call(args542, kw543)?
                }
                .attr("translate")?;
                let mut args539 = Vec::new();
                let mut kw540 = Vec::new();
                args539.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(unary("neg", e.get("C13_NOSE_LEN")?)?);
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                });
                fun541.call(args539, kw540)?
            };
            e.set("nose", assigned538.clone())?;
            let assigned545 = {
                let fun548 = e.get("body")?.attr("union")?;
                let mut args546 = Vec::new();
                let mut kw547 = Vec::new();
                args546.push(e.get("nose")?);
                fun548.call(args546, kw547)?
            };
            e.set("body", assigned545.clone())?;
            for item549 in {
                let fun563 = {
                    let fun566 = {
                        let fun569 = e.get("_c14")?.attr("build_blades")?;
                        let mut args567 = Vec::new();
                        let mut kw568 = Vec::new();
                        fun569.call(args567, kw568)?
                    }
                    .attr("val")?;
                    let mut args564 = Vec::new();
                    let mut kw565 = Vec::new();
                    fun566.call(args564, kw565)?
                }
                .attr("Solids")?;
                let mut args561 = Vec::new();
                let mut kw562 = Vec::new();
                fun563.call(args561, kw562)?
            }
            .iter()?
            {
                e.set("blade", item549)?;
                let assigned550 = {
                    let fun553 = e.get("blade")?.attr("BoundingBox")?;
                    let mut args551 = Vec::new();
                    let mut kw552 = Vec::new();
                    fun553.call(args551, kw552)?
                };
                e.set("bb", assigned550.clone())?;
                let assigned554 = {
                    let fun557 = e.get("body")?.attr("cut")?;
                    let mut args555 = Vec::new();
                    let mut kw556 = Vec::new();
                    args555.push({
                        let fun560 = e.get("_box")?;
                        let mut args558 = Vec::new();
                        let mut kw559 = Vec::new();
                        args558.push(binary(
                            "sub",
                            e.get("bb")?.attr("xmin")?,
                            Val::Float(0.3f64),
                        )?);
                        args558.push(binary(
                            "sub",
                            unary("neg", e.get("C13_NOSE_LEN")?)?,
                            Val::Float(0.5f64),
                        )?);
                        args558.push(binary(
                            "sub",
                            e.get("bb")?.attr("zmin")?,
                            Val::Float(0.3f64),
                        )?);
                        args558.push(binary(
                            "add",
                            e.get("bb")?.attr("xlen")?,
                            Val::Float(0.6f64),
                        )?);
                        args558.push(binary(
                            "add",
                            binary("add", e.get("C13_NOSE_LEN")?, Val::Float(0.5f64))?,
                            Val::Float(6.0f64),
                        )?);
                        args558.push(binary(
                            "add",
                            e.get("bb")?.attr("zlen")?,
                            Val::Float(0.6f64),
                        )?);
                        fun560.call(args558, kw559)?
                    });
                    fun557.call(args555, kw556)?
                };
                e.set("body", assigned554.clone())?;
            }
            let assigned570 = {
                let fun573 = {
                    let fun576 = {
                        let fun579 = {
                            let fun582 = {
                                let fun585 = {
                                    let fun588 = e.get("cq")?.attr("Workplane")?;
                                    let mut args586 = Vec::new();
                                    let mut kw587 = Vec::new();
                                    args586.push(e.get("xz_plane_y_up")?);
                                    fun588.call(args586, kw587)?
                                }
                                .attr("workplane")?;
                                let mut args583 = Vec::new();
                                let mut kw584 = Vec::new();
                                kw584.push(("offset".into(), e.get("C13_BODY_LEN")?));
                                fun585.call(args583, kw584)?
                            }
                            .attr("circle")?;
                            let mut args580 = Vec::new();
                            let mut kw581 = Vec::new();
                            args580.push(binary(
                                "truediv",
                                e.get("C13_BOOT_D")?.get(Val::Int(0i64))?,
                                Val::Float(2.0f64),
                            )?);
                            fun582.call(args580, kw581)?
                        }
                        .attr("workplane")?;
                        let mut args577 = Vec::new();
                        let mut kw578 = Vec::new();
                        kw578.push(("offset".into(), e.get("C13_BOOT_LEN")?));
                        fun579.call(args577, kw578)?
                    }
                    .attr("circle")?;
                    let mut args574 = Vec::new();
                    let mut kw575 = Vec::new();
                    args574.push(binary(
                        "truediv",
                        e.get("C13_BOOT_D")?.get(Val::Int(1i64))?,
                        Val::Float(2.0f64),
                    )?);
                    fun576.call(args574, kw575)?
                }
                .attr("loft")?;
                let mut args571 = Vec::new();
                let mut kw572 = Vec::new();
                fun573.call(args571, kw572)?
            };
            e.set("boot", assigned570.clone())?;
            let assigned589 = binary("add", e.get("C13_BODY_LEN")?, e.get("C13_BOOT_LEN")?)?;
            e.set("tail", assigned589.clone())?;
            let assigned590 = {
                let fun593 = e.get("_cable")?;
                let mut args591 = Vec::new();
                let mut kw592 = Vec::new();
                args591.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(e.get("tail")?);
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(binary("add", e.get("tail")?, Val::Float(26.0f64))?);
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(7.0f64));
                        s.push(binary("add", e.get("tail")?, Val::Float(48.0f64))?);
                        s.push(unary("neg", Val::Float(58.0f64))?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(11.0f64));
                        s.push(binary("add", e.get("tail")?, Val::Float(55.0f64))?);
                        s.push(unary("neg", Val::Float(175.0f64))?);
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                });
                args591.push(e.get("C13_CABLE_D")?);
                args591.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(1.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(unary("neg", Val::Float(1.0f64))?);
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                });
                fun593.call(args591, kw592)?
            };
            e.set("cord", assigned590.clone())?;
            let assigned594 = {
                let mut s = Vec::new();
                s.push({
                    let fun597 = e.get("body")?.attr("val")?;
                    let mut args595 = Vec::new();
                    let mut kw596 = Vec::new();
                    fun597.call(args595, kw596)?
                });
                s.push({
                    let fun600 = e.get("boot")?.attr("val")?;
                    let mut args598 = Vec::new();
                    let mut kw599 = Vec::new();
                    fun600.call(args598, kw599)?
                });
                s.push(e.get("cord")?);
                Val::list(s)
            };
            e.set("parts", assigned594.clone())?;
            return Ok({
                let fun603 = {
                    let fun606 = e.get("cq")?.attr("Compound")?.attr("makeCompound")?;
                    let mut args604 = Vec::new();
                    let mut kw605 = Vec::new();
                    args604.push(e.get("parts")?);
                    fun606.call(args604, kw605)?
                }
                .attr("translate")?;
                let mut args601 = Vec::new();
                let mut kw602 = Vec::new();
                args601.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y0")?);
                    s.push(e.get("z")?);
                    Val::tuple(s)
                });
                fun603.call(args601, kw602)?
            });
            Ok(Val::None)
        })
    })?;
    // s_cabinet_plan
    e.set("s_cabinet_plan", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned607 = {
                let fun610 = e.get("cq")?.attr("Assembly")?;
                let mut args608 = Vec::new();
                let mut kw609 = Vec::new();
                kw609.push(("name".into(), Val::Str("cabinet-plan-scene".into())));
                fun610.call(args608, kw609)?
            };
            e.set("a", assigned607.clone())?;
            {
                let fun613 = e.get("_machine")?;
                let mut args611 = Vec::new();
                let mut kw612 = Vec::new();
                args611.push(e.get("a")?);
                fun613.call(args611, kw612)?
            };
            let assigned614 = binary(
                "sub",
                binary(
                    "sub",
                    binary("sub", e.get("BOX_X0")?, e.get("CLEAR_SIDE")?)?,
                    e.get("CYLINDER_LANE")?,
                )?,
                Val::Float(30.0f64),
            )?;
            e.set("x0", assigned614.clone())?;
            let assigned615 = binary(
                "add",
                binary("add", e.get("BOX_X1")?, e.get("CLEAR_SIDE")?)?,
                Val::Float(30.0f64),
            )?;
            e.set("x1", assigned615.clone())?;
            {
                let fun618 = e.get("_add")?;
                let mut args616 = Vec::new();
                let mut kw617 = Vec::new();
                args616.push(e.get("a")?);
                args616.push({
                    let fun621 = e.get("_floor")?;
                    let mut args619 = Vec::new();
                    let mut kw620 = Vec::new();
                    args619.push(e.get("x0")?);
                    args619.push(binary("sub", e.get("BOX_Y0")?, Val::Float(40.0f64))?);
                    args619.push(binary("sub", e.get("x1")?, e.get("x0")?)?);
                    args619.push(binary(
                        "add",
                        binary(
                            "add",
                            binary("sub", e.get("BOX_Y1")?, e.get("BOX_Y0")?)?,
                            e.get("CLEAR_BEHIND")?,
                        )?,
                        Val::Float(80.0f64),
                    )?);
                    fun621.call(args619, kw620)?
                });
                args616.push(Val::Str("cabinet-floor".into()));
                args616.push(e.get("CABINET")?);
                fun618.call(args616, kw617)?
            };
            let assigned622 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("behind".into()));
                    s.push(e.get("BOX_X0")?);
                    s.push(e.get("BOX_Y1")?);
                    s.push(binary("sub", e.get("BOX_X1")?, e.get("BOX_X0")?)?);
                    s.push(e.get("CLEAR_BEHIND")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("side-west".into()));
                    s.push(binary("sub", e.get("BOX_X0")?, e.get("CLEAR_SIDE")?)?);
                    s.push(e.get("BOX_Y0")?);
                    s.push(e.get("CLEAR_SIDE")?);
                    s.push(binary("sub", e.get("BOX_Y1")?, e.get("BOX_Y0")?)?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("side-east".into()));
                    s.push(e.get("BOX_X1")?);
                    s.push(e.get("BOX_Y0")?);
                    s.push(e.get("CLEAR_SIDE")?);
                    s.push(binary("sub", e.get("BOX_Y1")?, e.get("BOX_Y0")?)?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            };
            e.set("pads", assigned622.clone())?;
            for item623 in e.get("pads")?.iter()? {
                let unpack631 = unpack(item623, 5)?;
                e.set("name", unpack631[0].clone())?;
                e.set("px", unpack631[1].clone())?;
                e.set("py", unpack631[2].clone())?;
                e.set("sx", unpack631[3].clone())?;
                e.set("sy", unpack631[4].clone())?;
                {
                    let fun626 = e.get("_add")?;
                    let mut args624 = Vec::new();
                    let mut kw625 = Vec::new();
                    args624.push(e.get("a")?);
                    args624.push({
                        let fun629 = e.get("_box")?;
                        let mut args627 = Vec::new();
                        let mut kw628 = Vec::new();
                        args627.push(e.get("px")?);
                        args627.push(e.get("py")?);
                        args627.push(unary("neg", Val::Float(6.0f64))?);
                        args627.push(e.get("sx")?);
                        args627.push(e.get("sy")?);
                        args627.push(Val::Float(10.0f64));
                        fun629.call(args627, kw628)?
                    });
                    args624.push({
                        let mut str630 = String::new();
                        str630.push_str("clear-");
                        str630.push_str(&format(&e.get("name")?, &String::new())?);
                        Val::Str(str630)
                    });
                    args624.push(e.get("CORAL")?);
                    fun626.call(args624, kw625)?
                };
            }
            let assigned632 = binary(
                "sub",
                binary("sub", e.get("BOX_X0")?, e.get("CLEAR_SIDE")?)?,
                binary("truediv", e.get("CYLINDER_LANE")?, Val::Float(2.0f64))?,
            )?;
            e.set("cx", assigned632.clone())?;
            {
                let fun635 = e.get("_add")?;
                let mut args633 = Vec::new();
                let mut kw634 = Vec::new();
                args633.push(e.get("a")?);
                args633.push({
                    let fun638 = e.get("_cyl")?;
                    let mut args636 = Vec::new();
                    let mut kw637 = Vec::new();
                    args636.push(e.get("cx")?);
                    args636.push(binary("add", e.get("BOX_Y0")?, Val::Float(150.0f64))?);
                    args636.push(unary("neg", Val::Float(6.0f64))?);
                    args636.push(e.get("CYLINDER_D")?);
                    args636.push(e.get("CYLINDER_H")?);
                    fun638.call(args636, kw637)?
                });
                args633.push(Val::Str("co2-cylinder".into()));
                args633.push(e.get("CYLINDER")?);
                fun635.call(args633, kw634)?
            };
            return Ok(e.get("a")?);
            Ok(Val::None)
        })
    })?;
    // s_opening
    e.set("s_opening", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned639 = {
                let fun642 = e.get("_cad_art")?.attr("_load_faucet_module")?;
                let mut args640 = Vec::new();
                let mut kw641 = Vec::new();
                fun642.call(args640, kw641)?
            };
            e.set("fa", assigned639.clone())?;
            let assigned643 = {
                let fun646 = e.get("_cad_art")?.attr("_children_by_name")?;
                let mut args644 = Vec::new();
                let mut kw645 = Vec::new();
                args644.push({
                    let fun649 = e.get("fa")?.attr("build_assembly")?;
                    let mut args647 = Vec::new();
                    let mut kw648 = Vec::new();
                    fun649.call(args647, kw648)?
                });
                fun646.call(args644, kw645)?
            };
            e.set("parts", assigned643.clone())?;
            let assigned650 = {
                let fun653 = e.get("cq")?.attr("Assembly")?;
                let mut args651 = Vec::new();
                let mut kw652 = Vec::new();
                kw652.push(("name".into(), Val::Str("opening-scene".into())));
                fun653.call(args651, kw652)?
            };
            e.set("a", assigned650.clone())?;
            let assigned654 = {
                let fun657 = {
                    let fun660 = {
                        let fun663 = {
                            let fun666 = e.get("cq")?.attr("Workplane")?;
                            let mut args664 = Vec::new();
                            let mut kw665 = Vec::new();
                            args664.push(Val::Str("XY".into()));
                            fun666.call(args664, kw665)?
                        }
                        .attr("workplane")?;
                        let mut args661 = Vec::new();
                        let mut kw662 = Vec::new();
                        kw662.push(("offset".into(), e.get("fa")?.attr("countertop_bottom_z")?));
                        fun663.call(args661, kw662)?
                    }
                    .attr("box")?;
                    let mut args658 = Vec::new();
                    let mut kw659 = Vec::new();
                    args658.push(Val::Float(320.0f64));
                    args658.push(Val::Float(210.0f64));
                    args658.push(e.get("fa")?.attr("countertop_thickness")?);
                    kw659.push(("centered".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Bool(true));
                        s.push(Val::Bool(true));
                        s.push(Val::Bool(false));
                        Val::tuple(s)
                    }));
                    fun660.call(args658, kw659)?
                }
                .attr("cut")?;
                let mut args655 = Vec::new();
                let mut kw656 = Vec::new();
                args655.push({
                    let fun669 = {
                        let fun672 = {
                            let fun675 = {
                                let fun678 = {
                                    let fun681 = e.get("cq")?.attr("Workplane")?;
                                    let mut args679 = Vec::new();
                                    let mut kw680 = Vec::new();
                                    args679.push(Val::Str("XY".into()));
                                    fun681.call(args679, kw680)?
                                }
                                .attr("workplane")?;
                                let mut args676 = Vec::new();
                                let mut kw677 = Vec::new();
                                kw677.push((
                                    "offset".into(),
                                    binary(
                                        "sub",
                                        e.get("fa")?.attr("countertop_bottom_z")?,
                                        Val::Float(1.0f64),
                                    )?,
                                ));
                                fun678.call(args676, kw677)?
                            }
                            .attr("center")?;
                            let mut args673 = Vec::new();
                            let mut kw674 = Vec::new();
                            args673.push(Val::Float(0.0f64));
                            args673.push(e.get("fa")?.attr("countertop_hole_center_y")?);
                            fun675.call(args673, kw674)?
                        }
                        .attr("circle")?;
                        let mut args670 = Vec::new();
                        let mut kw671 = Vec::new();
                        args670.push(e.get("fa")?.attr("hole_radius")?);
                        fun672.call(args670, kw671)?
                    }
                    .attr("extrude")?;
                    let mut args667 = Vec::new();
                    let mut kw668 = Vec::new();
                    args667.push(binary(
                        "add",
                        e.get("fa")?.attr("countertop_thickness")?,
                        Val::Float(2.0f64),
                    )?);
                    fun669.call(args667, kw668)?
                });
                fun657.call(args655, kw656)?
            };
            e.set("slab", assigned654.clone())?;
            {
                let fun684 = e.get("_add")?;
                let mut args682 = Vec::new();
                let mut kw683 = Vec::new();
                args682.push(e.get("a")?);
                args682.push(e.get("slab")?);
                args682.push(Val::Str("countertop".into()));
                args682.push(e.get("STONE")?);
                fun684.call(args682, kw683)?
            };
            let assigned685 = Val::Float(128.0f64);
            e.set("lift", assigned685.clone())?;
            for item686 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("flavor_tube_pos_x".into()));
                    s.push(e.get("BLACK_PART")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("flavor_tube_neg_x".into()));
                    s.push(e.get("BLACK_PART")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("soda_umbilical_tube".into()));
                    s.push(e.get("BLUE_TUBE")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("drain_tube".into()));
                    s.push(e.get("WHITE_TUBE")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("display_signal_ribbon".into()));
                    s.push(e.get("BLACK_PART")?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack702 = unpack(item686, 2)?;
                e.set("name", unpack702[0].clone())?;
                e.set("colour", unpack702[1].clone())?;
                let assigned687 = {
                    let fun690 = e.get("parts")?.attr("get")?;
                    let mut args688 = Vec::new();
                    let mut kw689 = Vec::new();
                    args688.push(e.get("name")?);
                    fun690.call(args688, kw689)?
                };
                e.set("child", assigned687.clone())?;
                if {
                    let v691 = e.get("child")?;
                    let v692 = Val::None;
                    Val::Bool(compare("is_not", v691.clone(), v692.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun695 = e.get("_add")?;
                        let mut args693 = Vec::new();
                        let mut kw694 = Vec::new();
                        args693.push(e.get("a")?);
                        args693.push({
                            let fun698 = {
                                let fun701 = e.get("_cad_art")?.attr("_clip_z")?;
                                let mut args699 = Vec::new();
                                let mut kw700 = Vec::new();
                                args699.push(e.get("child")?.attr("obj")?);
                                args699.push(unary("neg", Val::Float(70.0f64))?);
                                args699.push(Val::Float(40.0f64));
                                fun701.call(args699, kw700)?
                            }
                            .attr("translate")?;
                            let mut args696 = Vec::new();
                            let mut kw697 = Vec::new();
                            args696.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(0i64));
                                s.push(Val::Int(0i64));
                                s.push(e.get("lift")?);
                                Val::tuple(s)
                            });
                            fun698.call(args696, kw697)?
                        });
                        args693.push(e.get("name")?);
                        args693.push(e.get("colour")?);
                        fun695.call(args693, kw694)?
                    };
                }
            }
            let assigned703 = {
                let fun706 = e.get("parts")?.attr("get")?;
                let mut args704 = Vec::new();
                let mut kw705 = Vec::new();
                args704.push(Val::Str("westbrass".into()));
                fun706.call(args704, kw705)?
            };
            e.set("shank", assigned703.clone())?;
            if {
                let v707 = e.get("shank")?;
                let v708 = Val::None;
                Val::Bool(compare("is_not", v707.clone(), v708.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun711 = e.get("_add")?;
                    let mut args709 = Vec::new();
                    let mut kw710 = Vec::new();
                    args709.push(e.get("a")?);
                    args709.push({
                        let fun714 = {
                            let fun717 = e.get("_cad_art")?.attr("_clip_z")?;
                            let mut args715 = Vec::new();
                            let mut kw716 = Vec::new();
                            args715.push(e.get("shank")?.attr("obj")?);
                            args715.push(unary("neg", Val::Float(70.0f64))?);
                            args715.push(Val::Float(40.0f64));
                            fun717.call(args715, kw716)?
                        }
                        .attr("translate")?;
                        let mut args712 = Vec::new();
                        let mut kw713 = Vec::new();
                        args712.push({
                            let mut s = Vec::new();
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(0i64));
                            s.push(e.get("lift")?);
                            Val::tuple(s)
                        });
                        fun714.call(args712, kw713)?
                    });
                    args709.push(Val::Str("shank".into()));
                    args709.push(e.get("STEEL")?);
                    fun711.call(args709, kw710)?
                };
            }
            return Ok(e.get("a")?);
            Ok(Val::None)
        })
    })?;
    // s_filter_in_cabinet
    e.set("s_filter_in_cabinet", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned718 = {
                let fun721 = e.get("cq")?.attr("Assembly")?;
                let mut args719 = Vec::new();
                let mut kw720 = Vec::new();
                kw720.push(("name".into(), Val::Str("filter-scene".into())));
                fun721.call(args719, kw720)?
            };
            e.set("a", assigned718.clone())?;
            let assigned722 = binary("truediv", e.get("FILTER_D")?, Val::Float(2.0f64))?;
            e.set("z", assigned722.clone())?;
            let assigned723 = {
                let mut s = Vec::new();
                s.push(binary("truediv", e.get("FILTER_L")?, Val::Float(2.0f64))?);
                s.push(Val::Float(26.0f64));
                Val::tuple(s)
            };
            let unpack724 = unpack(assigned723.clone(), 2)?;
            e.set("half", unpack724[0].clone())?;
            e.set("cap", unpack724[1].clone())?;
            {
                let fun727 = e.get("_add")?;
                let mut args725 = Vec::new();
                let mut kw726 = Vec::new();
                args725.push(e.get("a")?);
                args725.push({
                    let fun730 = e.get("_cyl")?;
                    let mut args728 = Vec::new();
                    let mut kw729 = Vec::new();
                    args728.push(binary("add", unary("neg", e.get("half")?)?, e.get("cap")?)?);
                    args728.push(Val::Float(110.0f64));
                    args728.push(e.get("z")?);
                    args728.push(e.get("FILTER_D")?);
                    args728.push(binary(
                        "sub",
                        e.get("FILTER_L")?,
                        binary("mul", Val::Int(2i64), e.get("cap")?)?,
                    )?);
                    kw729.push(("axis".into(), Val::Str("X".into())));
                    fun730.call(args728, kw729)?
                });
                args725.push(Val::Str("cartridge".into()));
                args725.push(e.get("FILTER_BODY")?);
                fun727.call(args725, kw726)?
            };
            for item731 in {
                let mut s = Vec::new();
                s.push(unary("neg", Val::Float(1.0f64))?);
                s.push(Val::Float(1.0f64));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("side", item731)?;
                let assigned732 = if {
                    let v733 = e.get("side")?;
                    let v734 = Val::Int(0i64);
                    Val::Bool(compare("gt", v733.clone(), v734.clone())?.truthy()?)
                }
                .truthy()?
                {
                    binary("sub", e.get("half")?, e.get("cap")?)?
                } else {
                    unary("neg", e.get("half")?)?
                };
                e.set("end", assigned732.clone())?;
                {
                    let fun737 = e.get("_add")?;
                    let mut args735 = Vec::new();
                    let mut kw736 = Vec::new();
                    args735.push(e.get("a")?);
                    args735.push({
                        let fun740 = e.get("_cyl")?;
                        let mut args738 = Vec::new();
                        let mut kw739 = Vec::new();
                        args738.push(e.get("end")?);
                        args738.push(Val::Float(110.0f64));
                        args738.push(e.get("z")?);
                        args738.push(binary("mul", e.get("FILTER_D")?, Val::Float(0.62f64))?);
                        args738.push(e.get("cap")?);
                        kw739.push(("axis".into(), Val::Str("X".into())));
                        fun740.call(args738, kw739)?
                    });
                    args735.push({
                        let mut str741 = String::new();
                        str741.push_str("quick-connect-");
                        str741.push_str(&format(
                            &if {
                                let v742 = e.get("side")?;
                                let v743 = Val::Int(0i64);
                                Val::Bool(compare("gt", v742.clone(), v743.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                Val::Str("out".into())
                            } else {
                                Val::Str("in".into())
                            },
                            &String::new(),
                        )?);
                        Val::Str(str741)
                    });
                    args735.push(e.get("FILTER_CAP")?);
                    fun737.call(args735, kw736)?
                };
            }
            {
                let fun746 = e.get("_add")?;
                let mut args744 = Vec::new();
                let mut kw745 = Vec::new();
                args744.push(e.get("a")?);
                args744.push({
                    let fun749 = e.get("_bend")?;
                    let mut args747 = Vec::new();
                    let mut kw748 = Vec::new();
                    args747.push({
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(unary("neg", e.get("half")?)?);
                            s.push(Val::Float(110.0f64));
                            s.push(e.get("z")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(unary("neg", Val::Float(330.0f64))?);
                            s.push(Val::Float(110.0f64));
                            s.push(e.get("z")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(unary("neg", Val::Float(330.0f64))?);
                            s.push(unary("neg", Val::Float(40.0f64))?);
                            s.push(e.get("z")?);
                            Val::tuple(s)
                        });
                        Val::list(s)
                    });
                    fun749.call(args747, kw748)?
                });
                args744.push(Val::Str("white-run-in".into()));
                args744.push(e.get("WHITE_TUBE")?);
                fun746.call(args744, kw745)?
            };
            {
                let fun752 = e.get("_add")?;
                let mut args750 = Vec::new();
                let mut kw751 = Vec::new();
                args750.push(e.get("a")?);
                args750.push({
                    let fun755 = e.get("_bend")?;
                    let mut args753 = Vec::new();
                    let mut kw754 = Vec::new();
                    args753.push({
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("half")?);
                            s.push(Val::Float(110.0f64));
                            s.push(e.get("z")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(330.0f64));
                            s.push(Val::Float(110.0f64));
                            s.push(e.get("z")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(330.0f64));
                            s.push(unary("neg", Val::Float(40.0f64))?);
                            s.push(e.get("z")?);
                            Val::tuple(s)
                        });
                        Val::list(s)
                    });
                    fun755.call(args753, kw754)?
                });
                args750.push(Val::Str("white-run-out".into()));
                args750.push(e.get("WHITE_TUBE")?);
                fun752.call(args750, kw751)?
            };
            return Ok(e.get("a")?);
            Ok(Val::None)
        })
    })?;
    // s_collet_press
    e.set("s_collet_press", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned756 = {
                let fun759 = e.get("cq")?.attr("Assembly")?;
                let mut args757 = Vec::new();
                let mut kw758 = Vec::new();
                kw758.push(("name".into(), Val::Str("collet-press-scene".into())));
                fun759.call(args757, kw758)?
            };
            e.set("a", assigned756.clone())?;
            {
                let fun762 = e.get("a")?.attr("add")?;
                let mut args760 = Vec::new();
                let mut kw761 = Vec::new();
                args760.push({
                    let fun765 = e.get("import_step")?;
                    let mut args763 = Vec::new();
                    let mut kw764 = Vec::new();
                    args763.push({
                        let fun768 = e.get("str")?;
                        let mut args766 = Vec::new();
                        let mut kw767 = Vec::new();
                        args766.push(e.get("COLLET_PRESS")?);
                        fun768.call(args766, kw767)?
                    });
                    fun765.call(args763, kw764)?
                });
                kw761.push(("name".into(), Val::Str("collet-press".into())));
                kw761.push(("color".into(), e.get("PRINTED")?));
                fun762.call(args760, kw761)?
            };
            return Ok(e.get("a")?);
            Ok(Val::None)
        })
    })?;
    // s_the_back_face
    e.set("s_the_back_face", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun771 = e.get("_rear_face")?;
                let mut args769 = Vec::new();
                let mut kw770 = Vec::new();
                args769.push({
                    let fun774 = e.get("cq")?.attr("Assembly")?;
                    let mut args772 = Vec::new();
                    let mut kw773 = Vec::new();
                    kw773.push(("name".into(), Val::Str("the-back-face-scene".into())));
                    fun774.call(args772, kw773)?
                });
                fun771.call(args769, kw770)?
            });
            Ok(Val::None)
        })
    })?;
    // s_the_socket
    e.set("s_the_socket", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned775 = {
                let fun778 = e.get("_rear_face")?;
                let mut args776 = Vec::new();
                let mut kw777 = Vec::new();
                args776.push({
                    let fun781 = e.get("cq")?.attr("Assembly")?;
                    let mut args779 = Vec::new();
                    let mut kw780 = Vec::new();
                    kw780.push(("name".into(), Val::Str("the-socket-scene".into())));
                    fun781.call(args779, kw780)?
                });
                fun778.call(args776, kw777)?
            };
            e.set("a", assigned775.clone())?;
            {
                let fun784 = e.get("a")?.attr("add")?;
                let mut args782 = Vec::new();
                let mut kw783 = Vec::new();
                args782.push({
                    let fun787 = e.get("_c13_cordset")?;
                    let mut args785 = Vec::new();
                    let mut kw786 = Vec::new();
                    args785.push(Val::Float(0.5f64));
                    fun787.call(args785, kw786)?
                });
                kw783.push(("name".into(), Val::Str("c13-cordset".into())));
                kw783.push(("color".into(), e.get("CORDSET")?));
                fun784.call(args782, kw783)?
            };
            return Ok(e.get("a")?);
            Ok(Val::None)
        })
    })?;
    // s_nameplate
    e.set("s_nameplate", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned788 = {
                let fun791 = e.get("cq")?.attr("Assembly")?;
                let mut args789 = Vec::new();
                let mut kw790 = Vec::new();
                kw790.push(("name".into(), Val::Str("nameplate-scene".into())));
                fun791.call(args789, kw790)?
            };
            e.set("a", assigned788.clone())?;
            {
                let fun794 = e.get("_rear_face")?;
                let mut args792 = Vec::new();
                let mut kw793 = Vec::new();
                args792.push(e.get("a")?);
                fun794.call(args792, kw793)?
            };
            return Ok(e.get("a")?);
            Ok(Val::None)
        })
    })?;
    let assigned795 = unary("neg", Val::Float(44.0f64))?;
    e.set("PLATE_STANDOFF_X", assigned795.clone())?;
    let assigned796 = {
        let mut s = Vec::new();
        s.push(Val::Float(1.5f64));
        s.push(Val::Float(5.0f64));
        Val::tuple(s)
    };
    let unpack797 = unpack(assigned796.clone(), 2)?;
    e.set("WASHER_T", unpack797[0].clone())?;
    e.set("NUT_H", unpack797[1].clone())?;
    let assigned798 = {
        let fun801 = e.get("cq")?.attr("Color")?;
        let mut args799 = Vec::new();
        let mut kw800 = Vec::new();
        args799.push(Val::Float(0.43f64));
        args799.push(Val::Float(0.45f64));
        args799.push(Val::Float(0.48f64));
        args799.push(Val::Float(1.0f64));
        fun801.call(args799, kw800)?
    };
    e.set("NUT_STEEL", assigned798.clone())?;
    let assigned802 = {
        let fun805 = e.get("cq")?.attr("Color")?;
        let mut args803 = Vec::new();
        let mut kw804 = Vec::new();
        args803.push(Val::Float(0.91f64));
        args803.push(Val::Float(0.92f64));
        args803.push(Val::Float(0.94f64));
        args803.push(Val::Float(1.0f64));
        fun805.call(args803, kw804)?
    };
    e.set("PLATE_STEEL", assigned802.clone())?;
    let assigned806 = {
        let fun809 = e.get("cq")?.attr("Color")?;
        let mut args807 = Vec::new();
        let mut kw808 = Vec::new();
        args807.push(Val::Float(0.2f64));
        args807.push(Val::Float(0.205f64));
        args807.push(Val::Float(0.215f64));
        args807.push(Val::Float(1.0f64));
        fun809.call(args807, kw808)?
    };
    e.set("BLACK_PART_LIT", assigned806.clone())?;
    // s_plate_sideways
    e.set("s_plate_sideways", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned810 = {
                let fun813 = e.get("_cad_art")?.attr("_load_faucet_module")?;
                let mut args811 = Vec::new();
                let mut kw812 = Vec::new();
                fun813.call(args811, kw812)?
            };
            e.set("fa", assigned810.clone())?;
            let assigned814 = {
                let fun817 = e.get("_cad_art")?.attr("_children_by_name")?;
                let mut args815 = Vec::new();
                let mut kw816 = Vec::new();
                args815.push({
                    let fun820 = e.get("fa")?.attr("build_assembly")?;
                    let mut args818 = Vec::new();
                    let mut kw819 = Vec::new();
                    fun820.call(args818, kw819)?
                });
                fun817.call(args815, kw816)?
            };
            e.set("parts", assigned814.clone())?;
            let assigned821 = {
                let fun824 = e.get("cq")?.attr("Assembly")?;
                let mut args822 = Vec::new();
                let mut kw823 = Vec::new();
                kw823.push(("name".into(), Val::Str("plate-scene".into())));
                fun824.call(args822, kw823)?
            };
            e.set("a", assigned821.clone())?;
            let assigned825 = {
                let fun828 = {
                    let fun831 = {
                        let fun834 = {
                            let fun837 = {
                                let fun840 = e.get("cq")?.attr("Workplane")?;
                                let mut args838 = Vec::new();
                                let mut kw839 = Vec::new();
                                args838.push(Val::Str("XY".into()));
                                fun840.call(args838, kw839)?
                            }
                            .attr("workplane")?;
                            let mut args835 = Vec::new();
                            let mut kw836 = Vec::new();
                            kw836
                                .push(("offset".into(), e.get("fa")?.attr("countertop_bottom_z")?));
                            fun837.call(args835, kw836)?
                        }
                        .attr("center")?;
                        let mut args832 = Vec::new();
                        let mut kw833 = Vec::new();
                        args832.push(unary("neg", Val::Float(8.0f64))?);
                        args832.push(Val::Float(0.0f64));
                        fun834.call(args832, kw833)?
                    }
                    .attr("box")?;
                    let mut args829 = Vec::new();
                    let mut kw830 = Vec::new();
                    args829.push(Val::Float(142.0f64));
                    args829.push(Val::Float(68.0f64));
                    args829.push(e.get("fa")?.attr("countertop_thickness")?);
                    kw830.push(("centered".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Bool(true));
                        s.push(Val::Bool(true));
                        s.push(Val::Bool(false));
                        Val::tuple(s)
                    }));
                    fun831.call(args829, kw830)?
                }
                .attr("cut")?;
                let mut args826 = Vec::new();
                let mut kw827 = Vec::new();
                args826.push({
                    let fun843 = {
                        let fun846 = {
                            let fun849 = {
                                let fun852 = {
                                    let fun855 = e.get("cq")?.attr("Workplane")?;
                                    let mut args853 = Vec::new();
                                    let mut kw854 = Vec::new();
                                    args853.push(Val::Str("XY".into()));
                                    fun855.call(args853, kw854)?
                                }
                                .attr("workplane")?;
                                let mut args850 = Vec::new();
                                let mut kw851 = Vec::new();
                                kw851.push((
                                    "offset".into(),
                                    binary(
                                        "sub",
                                        e.get("fa")?.attr("countertop_bottom_z")?,
                                        Val::Float(1.0f64),
                                    )?,
                                ));
                                fun852.call(args850, kw851)?
                            }
                            .attr("center")?;
                            let mut args847 = Vec::new();
                            let mut kw848 = Vec::new();
                            args847.push(Val::Float(0.0f64));
                            args847.push(e.get("fa")?.attr("countertop_hole_center_y")?);
                            fun849.call(args847, kw848)?
                        }
                        .attr("circle")?;
                        let mut args844 = Vec::new();
                        let mut kw845 = Vec::new();
                        args844.push(e.get("fa")?.attr("hole_radius")?);
                        fun846.call(args844, kw845)?
                    }
                    .attr("extrude")?;
                    let mut args841 = Vec::new();
                    let mut kw842 = Vec::new();
                    args841.push(binary(
                        "add",
                        e.get("fa")?.attr("countertop_thickness")?,
                        Val::Float(2.0f64),
                    )?);
                    fun843.call(args841, kw842)?
                });
                fun828.call(args826, kw827)?
            };
            e.set("slab", assigned825.clone())?;
            {
                let fun858 = e.get("_add")?;
                let mut args856 = Vec::new();
                let mut kw857 = Vec::new();
                args856.push(e.get("a")?);
                args856.push(e.get("slab")?);
                args856.push(Val::Str("countertop".into()));
                args856.push(e.get("STONE")?);
                fun858.call(args856, kw857)?
            };
            for item859 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("westbrass".into()));
                    s.push(e.get("STEEL")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("flavor_tube_pos_x".into()));
                    s.push(e.get("BLACK_PART")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("flavor_tube_neg_x".into()));
                    s.push(e.get("BLACK_PART_LIT")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("flavor_umbilical_tube_pos_x".into()));
                    s.push(e.get("BLACK_PART")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("flavor_umbilical_tube_neg_x".into()));
                    s.push(e.get("BLACK_PART_LIT")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("soda_umbilical_tube".into()));
                    s.push(e.get("BLUE_TUBE")?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack879 = unpack(item859, 2)?;
                e.set("name", unpack879[0].clone())?;
                e.set("colour", unpack879[1].clone())?;
                let assigned860 = {
                    let fun863 = e.get("parts")?.attr("get")?;
                    let mut args861 = Vec::new();
                    let mut kw862 = Vec::new();
                    args861.push(e.get("name")?);
                    fun863.call(args861, kw862)?
                };
                e.set("child", assigned860.clone())?;
                if {
                    let v864 = e.get("child")?;
                    let v865 = Val::None;
                    Val::Bool(compare("is_not", v864.clone(), v865.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned866 = {
                        let fun869 = e.get("_cad_art")?.attr("_clip_z")?;
                        let mut args867 = Vec::new();
                        let mut kw868 = Vec::new();
                        args867.push(e.get("child")?.attr("obj")?);
                        args867.push(unary("neg", Val::Float(88.0f64))?);
                        args867.push(unary("neg", Val::Float(30.0f64))?);
                        fun869.call(args867, kw868)?
                    };
                    e.set("clipped", assigned866.clone())?;
                    if {
                        let fun872 = {
                            let fun875 = e.get("clipped")?.attr("solids")?;
                            let mut args873 = Vec::new();
                            let mut kw874 = Vec::new();
                            fun875.call(args873, kw874)?
                        }
                        .attr("size")?;
                        let mut args870 = Vec::new();
                        let mut kw871 = Vec::new();
                        fun872.call(args870, kw871)?
                    }
                    .truthy()?
                    {
                        {
                            let fun878 = e.get("_add")?;
                            let mut args876 = Vec::new();
                            let mut kw877 = Vec::new();
                            args876.push(e.get("a")?);
                            args876.push(e.get("clipped")?);
                            args876.push(e.get("name")?);
                            args876.push(e.get("colour")?);
                            fun878.call(args876, kw877)?
                        };
                    }
                }
            }
            let assigned880 = binary(
                "add",
                binary(
                    "add",
                    unary("neg", e.get("fa")?.attr("shank_length")?)?,
                    e.get("NUT_H")?,
                )?,
                e.get("WASHER_T")?,
            )?;
            e.set("washer_top", assigned880.clone())?;
            {
                let fun883 = e.get("_add")?;
                let mut args881 = Vec::new();
                let mut kw882 = Vec::new();
                args881.push(e.get("a")?);
                args881.push({
                    let fun886 = {
                        let fun889 = {
                            let fun892 = {
                                let fun895 = {
                                    let fun898 = e.get("cq")?.attr("Workplane")?;
                                    let mut args896 = Vec::new();
                                    let mut kw897 = Vec::new();
                                    args896.push(Val::Str("XY".into()));
                                    fun898.call(args896, kw897)?
                                }
                                .attr("workplane")?;
                                let mut args893 = Vec::new();
                                let mut kw894 = Vec::new();
                                kw894.push((
                                    "offset".into(),
                                    binary("sub", e.get("washer_top")?, e.get("WASHER_T")?)?,
                                ));
                                fun895.call(args893, kw894)?
                            }
                            .attr("circle")?;
                            let mut args890 = Vec::new();
                            let mut kw891 = Vec::new();
                            args890.push(Val::Float(12.0f64));
                            fun892.call(args890, kw891)?
                        }
                        .attr("circle")?;
                        let mut args887 = Vec::new();
                        let mut kw888 = Vec::new();
                        args887.push(Val::Float(6.1f64));
                        fun889.call(args887, kw888)?
                    }
                    .attr("extrude")?;
                    let mut args884 = Vec::new();
                    let mut kw885 = Vec::new();
                    args884.push(e.get("WASHER_T")?);
                    fun886.call(args884, kw885)?
                });
                args881.push(Val::Str("retained-washer".into()));
                args881.push(e.get("STEEL")?);
                fun883.call(args881, kw882)?
            };
            {
                let fun901 = e.get("_add")?;
                let mut args899 = Vec::new();
                let mut kw900 = Vec::new();
                args899.push(e.get("a")?);
                args899.push({
                    let fun904 = {
                        let fun907 = {
                            let fun910 = {
                                let fun913 = {
                                    let fun916 = e.get("cq")?.attr("Workplane")?;
                                    let mut args914 = Vec::new();
                                    let mut kw915 = Vec::new();
                                    args914.push(Val::Str("XY".into()));
                                    fun916.call(args914, kw915)?
                                }
                                .attr("workplane")?;
                                let mut args911 = Vec::new();
                                let mut kw912 = Vec::new();
                                kw912.push((
                                    "offset".into(),
                                    binary(
                                        "sub",
                                        binary("sub", e.get("washer_top")?, e.get("WASHER_T")?)?,
                                        e.get("NUT_H")?,
                                    )?,
                                ));
                                fun913.call(args911, kw912)?
                            }
                            .attr("polygon")?;
                            let mut args908 = Vec::new();
                            let mut kw909 = Vec::new();
                            args908.push(Val::Int(6i64));
                            args908.push(Val::Float(22.0f64));
                            fun910.call(args908, kw909)?
                        }
                        .attr("circle")?;
                        let mut args905 = Vec::new();
                        let mut kw906 = Vec::new();
                        args905.push(Val::Float(6.1f64));
                        fun907.call(args905, kw906)?
                    }
                    .attr("extrude")?;
                    let mut args902 = Vec::new();
                    let mut kw903 = Vec::new();
                    args902.push(e.get("NUT_H")?);
                    fun904.call(args902, kw903)?
                });
                args899.push(Val::Str("retained-nut".into()));
                args899.push(e.get("NUT_STEEL")?);
                fun901.call(args899, kw900)?
            };
            let assigned917 = {
                let fun920 = e.get("parts")?.attr("get")?;
                let mut args918 = Vec::new();
                let mut kw919 = Vec::new();
                args918.push(Val::Str("under_counter_plate".into()));
                fun920.call(args918, kw919)?
            };
            e.set("plate", assigned917.clone())?;
            if {
                let v921 = e.get("plate")?;
                let v922 = Val::None;
                Val::Bool(compare("is_not", v921.clone(), v922.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun925 = e.get("_add")?;
                    let mut args923 = Vec::new();
                    let mut kw924 = Vec::new();
                    args923.push(e.get("a")?);
                    args923.push({
                        let fun928 = e.get("plate")?.attr("obj")?.attr("translate")?;
                        let mut args926 = Vec::new();
                        let mut kw927 = Vec::new();
                        args926.push({
                            let mut s = Vec::new();
                            s.push(e.get("PLATE_STANDOFF_X")?);
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(0.0f64));
                            Val::tuple(s)
                        });
                        fun928.call(args926, kw927)?
                    });
                    args923.push(Val::Str("under-counter-plate".into()));
                    args923.push(e.get("PLATE_STEEL")?);
                    fun925.call(args923, kw924)?
                };
            }
            return Ok(e.get("a")?);
            Ok(Val::None)
        })
    })?;
    // s_bottle_in_funnel
    e.set("s_bottle_in_funnel", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned929 = {
                let fun932 = e.get("_cad_art")?.attr("borrow")?;
                let mut args930 = Vec::new();
                let mut kw931 = Vec::new();
                args930.push({
                    let fun935 = e.get("cq")?.attr("Assembly")?;
                    let mut args933 = Vec::new();
                    let mut kw934 = Vec::new();
                    kw934.push(("name".into(), Val::Str("bottle-scene".into())));
                    fun935.call(args933, kw934)?
                });
                args930.push({
                    let fun938 = e.get("_cad_art")?.attr("machine_bodies")?;
                    let mut args936 = Vec::new();
                    let mut kw937 = Vec::new();
                    args936.push({
                        let params = vec![("name".into(), None, false)];
                        let outer = e.clone();
                        let runtime = rt.clone();
                        Val::function(move |args, kwargs| {
                            let rt = runtime.clone();
                            let e = bind(&outer, &params, args, kwargs, None, None)?;
                            let _frame = rt.frame(&outer);
                            return Ok({
                                let v939 = e.get("name")?;
                                let v940 = Val::Str("funnel-cover".into());
                                Val::Bool(compare("ne", v939.clone(), v940.clone())?.truthy()?)
                            });
                            Ok(Val::None)
                        })
                    });
                    fun938.call(args936, kw937)?
                });
                fun932.call(args930, kw931)?
            };
            e.set("a", assigned929.clone())?;
            let assigned941 = e.get("BOTTLE_NECK_H")?;
            e.set("shoulder", assigned941.clone())?;
            let assigned942 = binary("add", e.get("shoulder")?, Val::Float(26.0f64))?;
            e.set("body", assigned942.clone())?;
            let assigned943 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push({
                        let fun946 = e.get("_cyl")?;
                        let mut args944 = Vec::new();
                        let mut kw945 = Vec::new();
                        args944.push(Val::Float(0.0f64));
                        args944.push(Val::Float(0.0f64));
                        args944.push(Val::Float(0.0f64));
                        args944.push(e.get("BOTTLE_NECK_D")?);
                        args944.push(e.get("BOTTLE_NECK_H")?);
                        fun946.call(args944, kw945)?
                    });
                    s.push(Val::Str("bottle-neck".into()));
                    s.push(e.get("BOTTLE_PET")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push({
                        let fun949 = {
                            let fun952 = {
                                let fun955 = {
                                    let fun958 = {
                                        let fun961 = e.get("cq")?.attr("Workplane")?;
                                        let mut args959 = Vec::new();
                                        let mut kw960 = Vec::new();
                                        args959.push(Val::Str("XY".into()));
                                        kw960.push(("origin".into(), {
                                            let mut s = Vec::new();
                                            s.push(Val::Float(0.0f64));
                                            s.push(Val::Float(0.0f64));
                                            s.push(e.get("shoulder")?);
                                            Val::tuple(s)
                                        }));
                                        fun961.call(args959, kw960)?
                                    }
                                    .attr("circle")?;
                                    let mut args956 = Vec::new();
                                    let mut kw957 = Vec::new();
                                    args956.push(binary(
                                        "truediv",
                                        e.get("BOTTLE_NECK_D")?,
                                        Val::Float(2.0f64),
                                    )?);
                                    fun958.call(args956, kw957)?
                                }
                                .attr("workplane")?;
                                let mut args953 = Vec::new();
                                let mut kw954 = Vec::new();
                                kw954.push(("offset".into(), Val::Float(26.0f64)));
                                fun955.call(args953, kw954)?
                            }
                            .attr("circle")?;
                            let mut args950 = Vec::new();
                            let mut kw951 = Vec::new();
                            args950.push(binary(
                                "truediv",
                                e.get("BOTTLE_D")?,
                                Val::Float(2.0f64),
                            )?);
                            fun952.call(args950, kw951)?
                        }
                        .attr("loft")?;
                        let mut args947 = Vec::new();
                        let mut kw948 = Vec::new();
                        fun949.call(args947, kw948)?
                    });
                    s.push(Val::Str("bottle-shoulder".into()));
                    s.push(e.get("BOTTLE_PET")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push({
                        let fun964 = e.get("_cyl")?;
                        let mut args962 = Vec::new();
                        let mut kw963 = Vec::new();
                        args962.push(Val::Float(0.0f64));
                        args962.push(Val::Float(0.0f64));
                        args962.push(e.get("body")?);
                        args962.push(e.get("BOTTLE_D")?);
                        args962.push(e.get("BOTTLE_H")?);
                        fun964.call(args962, kw963)?
                    });
                    s.push(Val::Str("bottle-body".into()));
                    s.push(e.get("CONCENTRATE")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push({
                        let fun967 = e.get("_cyl")?;
                        let mut args965 = Vec::new();
                        let mut kw966 = Vec::new();
                        args965.push(Val::Float(0.0f64));
                        args965.push(Val::Float(0.0f64));
                        args965.push(binary("add", e.get("body")?, e.get("BOTTLE_H")?)?);
                        args965.push(binary("mul", e.get("BOTTLE_D")?, Val::Float(0.62f64))?);
                        args965.push(Val::Float(4.0f64));
                        fun967.call(args965, kw966)?
                    });
                    s.push(Val::Str("bottle-base".into()));
                    s.push(e.get("BOTTLE_PET")?);
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("parts", assigned943.clone())?;
            let assigned968 = {
                let e = e.child();
                let out969 = Val::list(vec![]);
                for item970 in e.get("parts")?.iter()? {
                    let unpack971 = unpack(item970, 3)?;
                    e.set("shape", unpack971[0].clone())?;
                    e.set("name", unpack971[1].clone())?;
                    e.set("colour", unpack971[2].clone())?;
                    out969.attr("append")?.call(
                        vec![{
                            let mut s = Vec::new();
                            s.push({
                                let fun974 = e.get("shape")?.attr("rotate")?;
                                let mut args972 = Vec::new();
                                let mut kw973 = Vec::new();
                                args972.push({
                                    let mut s = Vec::new();
                                    s.push(Val::Int(0i64));
                                    s.push(Val::Int(0i64));
                                    s.push(Val::Int(0i64));
                                    Val::tuple(s)
                                });
                                args972.push({
                                    let mut s = Vec::new();
                                    s.push(Val::Int(1i64));
                                    s.push(Val::Int(0i64));
                                    s.push(Val::Int(0i64));
                                    Val::tuple(s)
                                });
                                args972.push(binary(
                                    "sub",
                                    Val::Float(90.0f64),
                                    e.get("BOTTLE_TIP")?,
                                )?);
                                fun974.call(args972, kw973)?
                            });
                            s.push(e.get("name")?);
                            s.push(e.get("colour")?);
                            Val::tuple(s)
                        }],
                        vec![],
                    )?;
                }
                out969
            };
            e.set("parts", assigned968.clone())?;
            let assigned975 = {
                let fun978 = e.get("min")?;
                let mut args976 = Vec::new();
                let mut kw977 = Vec::new();
                args976.push({
                    let e = e.child();
                    let out979 = Val::list(vec![]);
                    for item980 in e.get("parts")?.iter()? {
                        let unpack981 = unpack(item980, 3)?;
                        e.set("shape", unpack981[0].clone())?;
                        e.set("_", unpack981[1].clone())?;
                        e.set("_", unpack981[2].clone())?;
                        out979.attr("append")?.call(
                            vec![
                                {
                                    let fun984 = {
                                        let fun987 = e.get("shape")?.attr("val")?;
                                        let mut args985 = Vec::new();
                                        let mut kw986 = Vec::new();
                                        fun987.call(args985, kw986)?
                                    }
                                    .attr("BoundingBox")?;
                                    let mut args982 = Vec::new();
                                    let mut kw983 = Vec::new();
                                    fun984.call(args982, kw983)?
                                }
                                .attr("zmin")?,
                            ],
                            vec![],
                        )?;
                    }
                    out979
                });
                fun978.call(args976, kw977)?
            };
            e.set("lowest", assigned975.clone())?;
            let assigned988 = {
                let mut s = Vec::new();
                s.extend(e.get("FUNNEL_MOUTH")?.iter()?);
                s.push(binary(
                    "sub",
                    binary(
                        "add",
                        e.get("FUNNEL_BOUNDS")?.get(Val::Int(5i64))?,
                        e.get("BOTTLE_CLEARANCE")?,
                    )?,
                    e.get("lowest")?,
                )?);
                Val::tuple(s)
            };
            e.set("mouth", assigned988.clone())?;
            for item989 in e.get("parts")?.iter()? {
                let unpack996 = unpack(item989, 3)?;
                e.set("shape", unpack996[0].clone())?;
                e.set("name", unpack996[1].clone())?;
                e.set("colour", unpack996[2].clone())?;
                {
                    let fun992 = e.get("_add")?;
                    let mut args990 = Vec::new();
                    let mut kw991 = Vec::new();
                    args990.push(e.get("a")?);
                    args990.push({
                        let fun995 = e.get("shape")?.attr("translate")?;
                        let mut args993 = Vec::new();
                        let mut kw994 = Vec::new();
                        args993.push(e.get("mouth")?);
                        fun995.call(args993, kw994)?
                    });
                    args990.push(e.get("name")?);
                    args990.push(e.get("colour")?);
                    fun992.call(args990, kw991)?
                };
            }
            return Ok(e.get("a")?);
            Ok(Val::None)
        })
    })?;
    let assigned997 = Val::Float(4.0f64);
    e.set("TETHER_IN_MOUTH", assigned997.clone())?;
    // _load_regulator
    e.set("_load_regulator", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun1000 = e.get("_load")?;
                let mut args998 = Vec::new();
                let mut kw999 = Vec::new();
                args998.push(e.get("REGULATOR_DIR")?);
                args998.push(Val::Str("taprite_3741_regulator".into()));
                fun1000.call(args998, kw999)?
            });
            Ok(Val::None)
        })
    })?;
    // _co2_tether
    e.set("_co2_tether", {
        let params = vec![
            ("mouth".into(), None, false),
            ("drop".into(), None, false),
            ("run".into(), None, false),
            ("radius".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1001 = e.get("mouth")?;
            let unpack1002 = unpack(assigned1001.clone(), 3)?;
            e.set("x", unpack1002[0].clone())?;
            e.set("y", unpack1002[1].clone())?;
            e.set("z", unpack1002[2].clone())?;
            return Ok({
                let fun1005 = e.get("_bend")?;
                let mut args1003 = Vec::new();
                let mut kw1004 = Vec::new();
                args1003.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y")?);
                        s.push(binary("add", e.get("z")?, e.get("TETHER_IN_MOUTH")?)?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y")?);
                        s.push(binary("sub", e.get("z")?, e.get("drop")?)?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("add", e.get("x")?, e.get("run")?)?);
                        s.push(e.get("y")?);
                        s.push(binary("sub", e.get("z")?, e.get("drop")?)?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                kw1004.push(("radius".into(), e.get("radius")?));
                fun1005.call(args1003, kw1004)?
            });
            Ok(Val::None)
        })
    })?;
    // s_regulator
    e.set("s_regulator", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1006 = {
                let fun1009 = e.get("_load_regulator")?;
                let mut args1007 = Vec::new();
                let mut kw1008 = Vec::new();
                fun1009.call(args1007, kw1008)?
            };
            e.set("reg", assigned1006.clone())?;
            let assigned1010 = {
                let fun1013 = e.get("reg")?.attr("build_assembly")?;
                let mut args1011 = Vec::new();
                let mut kw1012 = Vec::new();
                fun1013.call(args1011, kw1012)?
            };
            e.set("a", assigned1010.clone())?;
            let assigned1014 = {
                let fun1017 = e.get("reg")?.attr("outlet")?;
                let mut args1015 = Vec::new();
                let mut kw1016 = Vec::new();
                fun1017.call(args1015, kw1016)?
            };
            let unpack1018 = unpack(assigned1014.clone(), 2)?;
            e.set("mouth", unpack1018[0].clone())?;
            e.set("_", unpack1018[1].clone())?;
            {
                let fun1021 = e.get("_add")?;
                let mut args1019 = Vec::new();
                let mut kw1020 = Vec::new();
                args1019.push(e.get("a")?);
                args1019.push({
                    let fun1024 = e.get("_co2_tether")?;
                    let mut args1022 = Vec::new();
                    let mut kw1023 = Vec::new();
                    args1022.push(e.get("mouth")?);
                    args1022.push(Val::Float(46.0f64));
                    args1022.push(Val::Float(120.0f64));
                    args1022.push(Val::Float(22.0f64));
                    fun1024.call(args1022, kw1023)?
                });
                args1019.push(Val::Str("red-tether".into()));
                args1019.push(e.get("RED_TUBE")?);
                fun1021.call(args1019, kw1020)?
            };
            return Ok(e.get("a")?);
            Ok(Val::None)
        })
    })?;
    // _load
    e.set("_load", {
        let params = vec![
            ("directory".into(), None, false),
            ("stem".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            rt.import_module("importlib.util")?;
            e.set("importlib", rt.import_module("importlib")?)?;
            let assigned1025 = binary("truediv", e.get("directory")?, {
                let mut str1026 = String::new();
                str1026.push_str(&format(&e.get("stem")?, &String::new())?);
                str1026.push_str(".py");
                Val::Str(str1026)
            })?;
            e.set("path", assigned1025.clone())?;
            {
                let fun1029 = e.get("note_read")?;
                let mut args1027 = Vec::new();
                let mut kw1028 = Vec::new();
                args1027.push(e.get("path")?);
                fun1029.call(args1027, kw1028)?
            };
            let assigned1030 = {
                let fun1033 = e
                    .get("importlib")?
                    .attr("util")?
                    .attr("spec_from_file_location")?;
                let mut args1031 = Vec::new();
                let mut kw1032 = Vec::new();
                args1031.push(e.get("stem")?);
                args1031.push(e.get("path")?);
                fun1033.call(args1031, kw1032)?
            };
            e.set("spec", assigned1030.clone())?;
            let assigned1034 = {
                let fun1037 = e.get("importlib")?.attr("util")?.attr("module_from_spec")?;
                let mut args1035 = Vec::new();
                let mut kw1036 = Vec::new();
                args1035.push(e.get("spec")?);
                fun1037.call(args1035, kw1036)?
            };
            e.set("module", assigned1034.clone())?;
            let assigned1038 = e.get("module")?;
            e.get("sys")?
                .attr("modules")?
                .set(e.get("stem")?, assigned1038.clone())?;
            {
                let fun1041 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args1039 = Vec::new();
                let mut kw1040 = Vec::new();
                args1039.push(Val::Int(0i64));
                args1039.push({
                    let fun1044 = e.get("str")?;
                    let mut args1042 = Vec::new();
                    let mut kw1043 = Vec::new();
                    args1042.push(e.get("directory")?);
                    fun1044.call(args1042, kw1043)?
                });
                fun1041.call(args1039, kw1040)?
            };
            let attempt1045 = (|| -> Result<Flow> {
                {
                    let fun1049 = e.get("spec")?.attr("loader")?.attr("exec_module")?;
                    let mut args1047 = Vec::new();
                    let mut kw1048 = Vec::new();
                    args1047.push(e.get("module")?);
                    fun1049.call(args1047, kw1048)?
                };
                Ok(Flow::Continue)
            })();
            let outcome1046 = (|| -> Result<Flow> {
                match attempt1045 {
                    Ok(flow @ (Flow::Return(_) | Flow::Break | Flow::Next)) => Ok(flow),
                    Ok(Flow::Continue) => Ok(Flow::Continue),
                    Err(error) => Err(error),
                }
            })();
            {
                let fun1052 = e.get("sys")?.attr("path")?.attr("remove")?;
                let mut args1050 = Vec::new();
                let mut kw1051 = Vec::new();
                args1050.push({
                    let fun1055 = e.get("str")?;
                    let mut args1053 = Vec::new();
                    let mut kw1054 = Vec::new();
                    args1053.push(e.get("directory")?);
                    fun1055.call(args1053, kw1054)?
                });
                fun1052.call(args1050, kw1051)?
            };
            match outcome1046? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
                Flow::Break => anyhow::bail!("break outside a loop"),
                Flow::Next => anyhow::bail!("continue outside a loop"),
            }
            return Ok(e.get("module")?);
            Ok(Val::None)
        })
    })?;
    let assigned1056 = {
        let d = Val::dict(vec![]);
        d.set(Val::Str("cabinet-plan".into()), {
            let mut s = Vec::new();
            s.push(e.get("s_cabinet_plan")?);
            s.push({
                let fun1059 = e.get("dict")?;
                let mut args1057 = Vec::new();
                let mut kw1058 = Vec::new();
                kw1058.push(("cam".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(1.0f64));
                    Val::tuple(s)
                }));
                kw1058.push(("up".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(1i64));
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                }));
                kw1058.push(("size".into(), Val::Str("1700x2000".into())));
                fun1059.call(args1057, kw1058)?
            });
            Val::tuple(s)
        })?;
        d.set(Val::Str("opening".into()), {
            let mut s = Vec::new();
            s.push(e.get("s_opening")?);
            s.push({
                let fun1062 = e.get("dict")?;
                let mut args1060 = Vec::new();
                let mut kw1061 = Vec::new();
                kw1061.push(("cam".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.42f64));
                    s.push(unary("neg", Val::Float(0.8f64))?);
                    s.push(Val::Float(0.95f64));
                    Val::tuple(s)
                }));
                kw1061.push(("target".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(24.0f64));
                    Val::tuple(s)
                }));
                kw1061.push(("span".into(), Val::Float(120.0f64)));
                kw1061.push(("size".into(), Val::Str("1900x1600".into())));
                fun1062.call(args1060, kw1061)?
            });
            Val::tuple(s)
        })?;
        d.set(Val::Str("filter-in-cabinet".into()), {
            let mut s = Vec::new();
            s.push(e.get("s_filter_in_cabinet")?);
            s.push({
                let fun1065 = e.get("dict")?;
                let mut args1063 = Vec::new();
                let mut kw1064 = Vec::new();
                kw1064.push(("cam".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.32f64));
                    s.push(unary("neg", Val::Float(1.0f64))?);
                    s.push(Val::Float(0.52f64));
                    Val::tuple(s)
                }));
                kw1064.push(("size".into(), Val::Str("2200x1200".into())));
                fun1065.call(args1063, kw1064)?
            });
            Val::tuple(s)
        })?;
        d.set(Val::Str("two-tees".into()), {
            let mut s = Vec::new();
            s.push(Val::None);
            s.push({
                let fun1068 = e.get("dict")?;
                let mut args1066 = Vec::new();
                let mut kw1067 = Vec::new();
                kw1067.push(("cam".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.25f64));
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.32f64));
                    Val::tuple(s)
                }));
                kw1067.push(("size".into(), Val::Str("1600x900".into())));
                fun1068.call(args1066, kw1067)?
            });
            Val::tuple(s)
        })?;
        d.set(Val::Str("nameplate".into()), {
            let mut s = Vec::new();
            s.push(e.get("s_nameplate")?);
            s.push({
                let fun1071 = e.get("dict")?;
                let mut args1069 = Vec::new();
                let mut kw1070 = Vec::new();
                kw1070.push(("cam".into(), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(0.14f64))?);
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.1f64));
                    Val::tuple(s)
                }));
                kw1070.push(("target".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(-45.4f64));
                    s.push(Val::Float(473.3f64));
                    s.push(Val::Float(217.0f64));
                    Val::tuple(s)
                }));
                kw1070.push(("span".into(), Val::Float(132.0f64)));
                kw1070.push(("size".into(), Val::Str("1600x1100".into())));
                fun1071.call(args1069, kw1070)?
            });
            Val::tuple(s)
        })?;
        d.set(Val::Str("plate-sideways".into()), {
            let mut s = Vec::new();
            s.push(e.get("s_plate_sideways")?);
            s.push({
                let fun1074 = e.get("dict")?;
                let mut args1072 = Vec::new();
                let mut kw1073 = Vec::new();
                kw1073.push(("cam".into(), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(0.85f64))?);
                    s.push(unary("neg", Val::Float(1.0f64))?);
                    s.push(unary("neg", Val::Float(0.85f64))?);
                    Val::tuple(s)
                }));
                kw1073.push(("target".into(), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(16.0f64))?);
                    s.push(Val::Float(0.0f64));
                    s.push(unary("neg", Val::Float(43.0f64))?);
                    Val::tuple(s)
                }));
                kw1073.push(("span".into(), Val::Float(88.0f64)));
                kw1073.push(("size".into(), Val::Str("1700x950".into())));
                fun1074.call(args1072, kw1073)?
            });
            Val::tuple(s)
        })?;
        d.set(Val::Str("stop-open".into()), {
            let mut s = Vec::new();
            s.push(Val::None);
            s.push({
                let fun1077 = e.get("dict")?;
                let mut args1075 = Vec::new();
                let mut kw1076 = Vec::new();
                kw1076.push(("cam".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(1.05f64));
                    s.push(Val::Float(1.7f64));
                    s.push(Val::Float(0.62f64));
                    Val::tuple(s)
                }));
                kw1076.push(("target".into(), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(6.0f64))?);
                    s.push(Val::Float(44.0f64));
                    s.push(Val::Float(96.0f64));
                    Val::tuple(s)
                }));
                kw1076.push(("span".into(), Val::Float(86.0f64)));
                kw1076.push(("size".into(), Val::Str("1250x1150".into())));
                kw1076.push(("trim".into(), Val::Bool(false)));
                fun1077.call(args1075, kw1076)?
            });
            Val::tuple(s)
        })?;
        d.set(Val::Str("stop-closed".into()), {
            let mut s = Vec::new();
            s.push(Val::None);
            s.push({
                let fun1080 = e.get("dict")?;
                let mut args1078 = Vec::new();
                let mut kw1079 = Vec::new();
                kw1079.push(("cam".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(1.05f64));
                    s.push(Val::Float(1.7f64));
                    s.push(Val::Float(0.62f64));
                    Val::tuple(s)
                }));
                kw1079.push(("target".into(), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(6.0f64))?);
                    s.push(Val::Float(44.0f64));
                    s.push(Val::Float(96.0f64));
                    Val::tuple(s)
                }));
                kw1079.push(("span".into(), Val::Float(86.0f64)));
                kw1079.push(("size".into(), Val::Str("1250x1150".into())));
                kw1079.push(("trim".into(), Val::Bool(false)));
                fun1080.call(args1078, kw1079)?
            });
            Val::tuple(s)
        })?;
        d.set(Val::Str("tee-before".into()), {
            let mut s = Vec::new();
            s.push(Val::None);
            s.push({
                let fun1083 = e.get("dict")?;
                let mut args1081 = Vec::new();
                let mut kw1082 = Vec::new();
                kw1082.push(("cam".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(1.05f64));
                    s.push(Val::Float(1.7f64));
                    s.push(Val::Float(0.62f64));
                    Val::tuple(s)
                }));
                kw1082.push(("target".into(), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(6.0f64))?);
                    s.push(Val::Float(44.0f64));
                    s.push(Val::Float(112.0f64));
                    Val::tuple(s)
                }));
                kw1082.push(("span".into(), Val::Float(132.0f64)));
                kw1082.push(("size".into(), Val::Str("1250x1150".into())));
                kw1082.push(("trim".into(), Val::Bool(false)));
                fun1083.call(args1081, kw1082)?
            });
            Val::tuple(s)
        })?;
        d.set(Val::Str("tee-after".into()), {
            let mut s = Vec::new();
            s.push(Val::None);
            s.push({
                let fun1086 = e.get("dict")?;
                let mut args1084 = Vec::new();
                let mut kw1085 = Vec::new();
                kw1085.push(("cam".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(1.05f64));
                    s.push(Val::Float(1.7f64));
                    s.push(Val::Float(0.62f64));
                    Val::tuple(s)
                }));
                kw1085.push(("target".into(), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(6.0f64))?);
                    s.push(Val::Float(44.0f64));
                    s.push(Val::Float(112.0f64));
                    Val::tuple(s)
                }));
                kw1085.push(("span".into(), Val::Float(132.0f64)));
                kw1085.push(("size".into(), Val::Str("1250x1150".into())));
                kw1085.push(("trim".into(), Val::Bool(false)));
                fun1086.call(args1084, kw1085)?
            });
            Val::tuple(s)
        })?;
        d.set(Val::Str("bottle-in-funnel".into()), {
            let mut s = Vec::new();
            s.push(e.get("s_bottle_in_funnel")?);
            s.push({
                let fun1089 = e.get("dict")?;
                let mut args1087 = Vec::new();
                let mut kw1088 = Vec::new();
                kw1088.push(("cam".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(1.0f64));
                    s.push(unary("neg", Val::Float(0.5f64))?);
                    s.push(Val::Float(0.45f64));
                    Val::tuple(s)
                }));
                kw1088.push(("target".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(20.0f64));
                    s.push(Val::Float(215.0f64));
                    s.push(Val::Float(190.0f64));
                    Val::tuple(s)
                }));
                kw1088.push(("span".into(), Val::Float(265.0f64)));
                kw1088.push(("size".into(), Val::Str("1500x1180".into())));
                fun1089.call(args1087, kw1088)?
            });
            Val::tuple(s)
        })?;
        d.set(Val::Str("kitchen-push".into()), {
            let mut s = Vec::new();
            s.push(Val::None);
            s.push({
                let fun1092 = e.get("dict")?;
                let mut args1090 = Vec::new();
                let mut kw1091 = Vec::new();
                kw1091.push(("cam".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(1.05f64));
                    s.push(unary("neg", Val::Float(1.72f64))?);
                    s.push(Val::Float(0.72f64));
                    Val::tuple(s)
                }));
                kw1091.push(("target".into(), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(46.0f64))?);
                    s.push(Val::Float(8.0f64));
                    s.push(Val::Float(100.0f64));
                    Val::tuple(s)
                }));
                kw1091.push(("span".into(), Val::Float(88.0f64)));
                kw1091.push(("size".into(), Val::Str("1500x980".into())));
                kw1091.push(("trim".into(), Val::Bool(false)));
                fun1092.call(args1090, kw1091)?
            });
            Val::tuple(s)
        })?;
        d.set(Val::Str("kitchen-hose".into()), {
            let mut s = Vec::new();
            s.push(Val::None);
            s.push({
                let fun1095 = e.get("dict")?;
                let mut args1093 = Vec::new();
                let mut kw1094 = Vec::new();
                kw1094.push(("cam".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(1.05f64));
                    s.push(Val::Float(1.7f64));
                    s.push(Val::Float(0.62f64));
                    Val::tuple(s)
                }));
                kw1094.push(("target".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(10.0f64));
                    s.push(Val::Float(53.0f64));
                    s.push(Val::Float(150.0f64));
                    Val::tuple(s)
                }));
                kw1094.push(("span".into(), Val::Float(88.0f64)));
                kw1094.push(("size".into(), Val::Str("1500x980".into())));
                kw1094.push(("trim".into(), Val::Bool(false)));
                fun1095.call(args1093, kw1094)?
            });
            Val::tuple(s)
        })?;
        d.set(Val::Str("regulator".into()), {
            let mut s = Vec::new();
            s.push(e.get("s_regulator")?);
            s.push({
                let fun1098 = e.get("dict")?;
                let mut args1096 = Vec::new();
                let mut kw1097 = Vec::new();
                kw1097.push(("cam".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.1f64));
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.16f64));
                    Val::tuple(s)
                }));
                kw1097.push(("size".into(), Val::Str("1700x1500".into())));
                fun1098.call(args1096, kw1097)?
            });
            Val::tuple(s)
        })?;
        d.set(Val::Str("collet-press".into()), {
            let mut s = Vec::new();
            s.push(e.get("s_collet_press")?);
            s.push({
                let fun1101 = e.get("dict")?;
                let mut args1099 = Vec::new();
                let mut kw1100 = Vec::new();
                kw1100.push(("cam".into(), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(0.5f64))?);
                    s.push(unary("neg", Val::Float(0.9f64))?);
                    s.push(Val::Float(0.85f64));
                    Val::tuple(s)
                }));
                kw1100.push(("size".into(), Val::Str("1700x1100".into())));
                fun1101.call(args1099, kw1100)?
            });
            Val::tuple(s)
        })?;
        d.set(Val::Str("the-back-face".into()), {
            let mut s = Vec::new();
            s.push(e.get("s_the_back_face")?);
            s.push({
                let fun1104 = e.get("dict")?;
                let mut args1102 = Vec::new();
                let mut kw1103 = Vec::new();
                kw1103.push(("cam".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.12f64));
                    Val::tuple(s)
                }));
                kw1103.push(("target".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(467.0f64));
                    s.push(Val::Float(268.0f64));
                    Val::tuple(s)
                }));
                kw1103.push(("span".into(), Val::Float(100.0f64)));
                kw1103.push(("size".into(), Val::Str("3200x2240".into())));
                fun1104.call(args1102, kw1103)?
            });
            Val::tuple(s)
        })?;
        d.set(Val::Str("the-socket".into()), {
            let mut s = Vec::new();
            s.push(e.get("s_the_socket")?);
            s.push({
                let fun1107 = e.get("dict")?;
                let mut args1105 = Vec::new();
                let mut kw1106 = Vec::new();
                kw1106.push(("cam".into(), {
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(0.26f64))?);
                    s.push(Val::Float(1.0f64));
                    s.push(Val::Float(0.16f64));
                    Val::tuple(s)
                }));
                kw1106.push(("target".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Float(5.0f64));
                    s.push(e.get("REAR_FACE_Y")?);
                    s.push(Val::Float(334.1f64));
                    Val::tuple(s)
                }));
                kw1106.push(("span".into(), Val::Float(31.7f64)));
                kw1106.push(("size".into(), Val::Str("2200x668".into())));
                fun1107.call(args1105, kw1106)?
            });
            Val::tuple(s)
        })?;
        d
    };
    e.set("SCENES", assigned1056.clone())?;
    // render
    e.set("render", {
        let params = vec![("names".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun1110 = e.get("ART")?.attr("mkdir")?;
                let mut args1108 = Vec::new();
                let mut kw1109 = Vec::new();
                kw1109.push(("parents".into(), Val::Bool(true)));
                kw1109.push(("exist_ok".into(), Val::Bool(true)));
                fun1110.call(args1108, kw1109)?
            };
            {
                let fun1113 = e.get("OUT")?.attr("mkdir")?;
                let mut args1111 = Vec::new();
                let mut kw1112 = Vec::new();
                kw1112.push(("parents".into(), Val::Bool(true)));
                kw1112.push(("exist_ok".into(), Val::Bool(true)));
                fun1113.call(args1111, kw1112)?
            };
            {
                let fun1116 = e.get("note_read")?;
                let mut args1114 = Vec::new();
                let mut kw1115 = Vec::new();
                args1114.push(e.get("MACHINE_MESH")?);
                fun1116.call(args1114, kw1115)?
            };
            {
                let fun1119 = e.get("note_read")?;
                let mut args1117 = Vec::new();
                let mut kw1118 = Vec::new();
                args1117.push(e.get("MACHINE_FACTS")?);
                fun1119.call(args1117, kw1118)?
            };
            {
                let fun1122 = e.get("note_read")?;
                let mut args1120 = Vec::new();
                let mut kw1121 = Vec::new();
                args1120.push(e.get("COLLET_PRESS")?);
                fun1122.call(args1120, kw1121)?
            };
            {
                let fun1125 = e.get("note_read")?;
                let mut args1123 = Vec::new();
                let mut kw1124 = Vec::new();
                args1123.push(e.get("C14_SOURCE")?);
                fun1125.call(args1123, kw1124)?
            };
            let context1126 = {
                let fun1129 = e.get("tempfile")?.attr("TemporaryDirectory")?;
                let mut args1127 = Vec::new();
                let mut kw1128 = Vec::new();
                kw1128.push(("prefix".into(), Val::Str("install-art-".into())));
                kw1128.push(("dir".into(), e.get("OUT")?));
                fun1129.call(args1127, kw1128)?
            };
            e.set(
                "directory",
                context1126.attr("__enter__")?.call(vec![], vec![])?,
            )?;
            let context_result1186 = (|| -> Result<Flow> {
                let assigned1130 = {
                    let fun1133 = e.get("Path")?;
                    let mut args1131 = Vec::new();
                    let mut kw1132 = Vec::new();
                    args1131.push(e.get("directory")?);
                    fun1133.call(args1131, kw1132)?
                };
                e.set("work", assigned1130.clone())?;
                let mod1134 = rt.import_module("_install_art_mesh")?;
                e.set("payloads", rt.member("_install_art_mesh", "payloads")?)?;
                let assigned1135 = {
                    let fun1138 = e.get("payloads")?;
                    let mut args1136 = Vec::new();
                    let mut kw1137 = Vec::new();
                    args1136.push(e.namespace());
                    args1136.push(e.get("names")?);
                    args1136.push(e.get("work")?);
                    fun1138.call(args1136, kw1137)?
                };
                e.set("shown", assigned1135.clone())?;
                let assigned1139 = {
                    let mut s = Vec::new();
                    Val::list(s)
                };
                e.set("jobs", assigned1139.clone())?;
                for item1140 in e.get("names")?.iter()? {
                    e.set("name", item1140)?;
                    let assigned1141 = e.get("SCENES")?.get(e.get("name")?)?;
                    let unpack1142 = unpack(assigned1141.clone(), 2)?;
                    e.set("_build", unpack1142[0].clone())?;
                    e.set("pose", unpack1142[1].clone())?;
                    let assigned1143 = binary("truediv", e.get("work")?, {
                        let mut str1144 = String::new();
                        str1144.push_str(&format(&e.get("name")?, &String::new())?);
                        str1144.push_str(".step");
                        Val::Str(str1144)
                    })?;
                    e.set("step", assigned1143.clone())?;
                    {
                        let fun1147 = e.get("jobs")?.attr("append")?;
                        let mut args1145 = Vec::new();
                        let mut kw1146 = Vec::new();
                        args1145.push({
                            let d = Val::dict(vec![]);
                            d.set(Val::Str("step".into()), {
                                let fun1150 = e.get("str")?;
                                let mut args1148 = Vec::new();
                                let mut kw1149 = Vec::new();
                                args1148.push({
                                    let fun1153 = e.get("step")?.attr("relative_to")?;
                                    let mut args1151 = Vec::new();
                                    let mut kw1152 = Vec::new();
                                    args1151.push(e.get("HARDWARE")?);
                                    fun1153.call(args1151, kw1152)?
                                });
                                fun1150.call(args1148, kw1149)?
                            })?;
                            d.set(Val::Str("payload".into()), {
                                let fun1156 = e.get("str")?;
                                let mut args1154 = Vec::new();
                                let mut kw1155 = Vec::new();
                                args1154.push(e.get("shown")?.get(e.get("name")?)?);
                                fun1156.call(args1154, kw1155)?
                            })?;
                            d.set(Val::Str("out".into()), {
                                let fun1159 = e.get("str")?;
                                let mut args1157 = Vec::new();
                                let mut kw1158 = Vec::new();
                                args1157.push(binary("truediv", e.get("ART")?, {
                                    let mut str1160 = String::new();
                                    str1160.push_str(&format(&e.get("name")?, &String::new())?);
                                    str1160.push_str(".png");
                                    Val::Str(str1160)
                                })?);
                                fun1159.call(args1157, kw1158)?
                            })?;
                            d.set(Val::Str("up".into()), {
                                let mut s = Vec::new();
                                s.push(Val::Int(0i64));
                                s.push(Val::Int(0i64));
                                s.push(Val::Int(1i64));
                                Val::tuple(s)
                            })?;
                            d.set(Val::Str("bg".into()), Val::Str("#ffffff".into()))?;
                            d.set(Val::Str("trim".into()), Val::Bool(true))?;
                            d.set(Val::Str("solid".into()), Val::Bool(true))?;
                            d.set(Val::Str("ortho".into()), Val::Bool(true))?;
                            d.set(Val::Str("ground".into()), Val::Bool(false))?;
                            d.set(Val::Str("fog".into()), Val::Bool(false))?;
                            dict_extend(&d, e.get("pose")?)?;
                            d
                        });
                        fun1147.call(args1145, kw1146)?
                    };
                    {
                        let fun1163 = e.get("print")?;
                        let mut args1161 = Vec::new();
                        let mut kw1162 = Vec::new();
                        args1161.push({
                            let mut str1164 = String::new();
                            str1164.push_str("  staged ");
                            str1164.push_str(&format(&e.get("name")?, &String::new())?);
                            Val::Str(str1164)
                        });
                        fun1163.call(args1161, kw1162)?
                    };
                }
                {
                    let fun1167 = e.get("_hsm_render")?.attr("render")?;
                    let mut args1165 = Vec::new();
                    let mut kw1166 = Vec::new();
                    args1165.push(e.get("jobs")?);
                    fun1167.call(args1165, kw1166)?
                };
                for item1168 in e.get("jobs")?.iter()? {
                    e.set("job", item1168)?;
                    let assigned1169 = {
                        let fun1172 = e.get("Path")?;
                        let mut args1170 = Vec::new();
                        let mut kw1171 = Vec::new();
                        args1170.push(e.get("job")?.get(Val::Str("out".into()))?);
                        fun1172.call(args1170, kw1171)?
                    };
                    e.set("out", assigned1169.clone())?;
                    {
                        let fun1175 = e.get("_cad_art")?.attr("_clear_connected_background")?;
                        let mut args1173 = Vec::new();
                        let mut kw1174 = Vec::new();
                        args1173.push(e.get("out")?);
                        fun1175.call(args1173, kw1174)?
                    };
                    {
                        let fun1178 = e.get("note_write")?;
                        let mut args1176 = Vec::new();
                        let mut kw1177 = Vec::new();
                        args1176.push(e.get("out")?);
                        fun1178.call(args1176, kw1177)?
                    };
                    {
                        let fun1181 = e.get("print")?;
                        let mut args1179 = Vec::new();
                        let mut kw1180 = Vec::new();
                        args1179.push({
                            let mut str1182 = String::new();
                            str1182.push_str("  -> art/");
                            str1182
                                .push_str(&format(&e.get("out")?.attr("name")?, &String::new())?);
                            str1182.push_str(" (");
                            str1182.push_str(&format(
                                &binary(
                                    "floordiv",
                                    {
                                        let fun1185 = e.get("out")?.attr("stat")?;
                                        let mut args1183 = Vec::new();
                                        let mut kw1184 = Vec::new();
                                        fun1185.call(args1183, kw1184)?
                                    }
                                    .attr("st_size")?,
                                    Val::Int(1024i64),
                                )?,
                                &String::new(),
                            )?);
                            str1182.push_str(" KB)");
                            Val::Str(str1182)
                        });
                        fun1181.call(args1179, kw1180)?
                    };
                }
                Ok(Flow::Continue)
            })();
            context1126
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            match context_result1186? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
                Flow::Break => anyhow::bail!("break outside a loop"),
                Flow::Next => anyhow::bail!("continue outside a loop"),
            }
            Ok(Val::None)
        })
    })?;
    // main
    e.set("main", {
        let params = vec![("argv".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v1187 = Val::Str("--list".into());
                let v1188 = e.get("argv")?;
                Val::Bool(compare("in", v1187.clone(), v1188.clone())?.truthy()?)
            }
            .truthy()?
            {
                for item1189 in e.get("SCENES")?.iter()? {
                    e.set("name", item1189)?;
                    {
                        let fun1192 = e.get("print")?;
                        let mut args1190 = Vec::new();
                        let mut kw1191 = Vec::new();
                        args1190.push(e.get("name")?);
                        fun1192.call(args1190, kw1191)?
                    };
                }
                return Ok(Val::Int(0i64));
            }
            let assigned1193 = {
                let v1197 = {
                    let e = e.child();
                    let out1198 = Val::list(vec![]);
                    for item1199 in e.get("argv")?.iter()? {
                        e.set("a", item1199)?;
                        if unary("not", {
                            let fun1202 = e.get("a")?.attr("startswith")?;
                            let mut args1200 = Vec::new();
                            let mut kw1201 = Vec::new();
                            args1200.push(Val::Str("-".into()));
                            fun1202.call(args1200, kw1201)?
                        })?
                        .truthy()?
                        {
                            out1198.attr("append")?.call(vec![e.get("a")?], vec![])?;
                        }
                    }
                    out1198
                };
                if v1197.truthy()? {
                    v1197
                } else {
                    {
                        let fun1196 = e.get("list")?;
                        let mut args1194 = Vec::new();
                        let mut kw1195 = Vec::new();
                        args1194.push(e.get("SCENES")?);
                        fun1196.call(args1194, kw1195)?
                    }
                }
            };
            e.set("wanted", assigned1193.clone())?;
            let assigned1203 = {
                let e = e.child();
                let out1204 = Val::list(vec![]);
                for item1205 in e.get("wanted")?.iter()? {
                    e.set("n", item1205)?;
                    if {
                        let v1206 = e.get("n")?;
                        let v1207 = e.get("SCENES")?;
                        Val::Bool(compare("not_in", v1206.clone(), v1207.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        out1204.attr("append")?.call(vec![e.get("n")?], vec![])?;
                    }
                }
                out1204
            };
            e.set("unknown", assigned1203.clone())?;
            if e.get("unknown")?.truthy()? {
                {
                    let fun1210 = e.get("print")?;
                    let mut args1208 = Vec::new();
                    let mut kw1209 = Vec::new();
                    args1208.push({
                        let mut str1211 = String::new();
                        str1211.push_str("unknown scene(s): ");
                        str1211.push_str(&format(
                            &{
                                let fun1214 = Val::Str(", ".into()).attr("join")?;
                                let mut args1212 = Vec::new();
                                let mut kw1213 = Vec::new();
                                args1212.push(e.get("unknown")?);
                                fun1214.call(args1212, kw1213)?
                            },
                            &String::new(),
                        )?);
                        Val::Str(str1211)
                    });
                    kw1209.push(("file".into(), e.get("sys")?.attr("stderr")?));
                    fun1210.call(args1208, kw1209)?
                };
                return Ok(Val::Int(1i64));
            }
            {
                let fun1217 = e.get("render")?;
                let mut args1215 = Vec::new();
                let mut kw1216 = Vec::new();
                args1215.push(e.get("wanted")?);
                fun1217.call(args1215, kw1216)?
            };
            return Ok(Val::Int(0i64));
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun1220 = e.get("_rust_part")?.attr("start")?;
        let mut args1218 = Vec::new();
        let mut kw1219 = Vec::new();
        fun1220.call(args1218, kw1219)?
    };
    {
        let fun1223 = e.get("sys")?.attr("exit")?;
        let mut args1221 = Vec::new();
        let mut kw1222 = Vec::new();
        args1221.push({
            let fun1226 = e.get("main")?;
            let mut args1224 = Vec::new();
            let mut kw1225 = Vec::new();
            args1224.push(e.get("sys")?.attr("argv")?.get(Val::Slice {
                start: Some(Val::Int(1i64).integer()?),
                stop: None,
                step: 1,
            })?);
            fun1226.call(args1224, kw1225)?
        });
        fun1223.call(args1221, kw1222)?
    };
    Ok(Val::None)
}
