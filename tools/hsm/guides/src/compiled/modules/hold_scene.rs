//! Guide recipe: `tools/install-guide/hold_scene.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("os", rt.import_module("os")?)?;
    e.set("re", rt.import_module("re")?)?;
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
                e.get("HARDWARE")?,
                Val::Str("install-guide".into()),
            )?);
            fun15.call(args13, kw14)?
        });
        fun12.call(args10, kw11)?
    };
    {
        let fun18 = e.get("os")?.attr("environ")?.attr("setdefault")?;
        let mut args16 = Vec::new();
        let mut kw17 = Vec::new();
        args16.push(Val::Str("HSM_NO_BUILD_LOCK".into()));
        args16.push(Val::Str("1".into()));
        fun18.call(args16, kw17)?
    };
    e.set("cq", rt.import_module("cadquery")?)?;
    let mod19 = rt.import_module("cadquery.occ_impl.exporters.svg")?;
    e.set(
        "getPaths",
        rt.member("cadquery.occ_impl.exporters.svg", "getPaths")?,
    )?;
    let mod20 = rt.import_module("OCP.BRepLib")?;
    e.set("BRepLib", rt.member("OCP.BRepLib", "BRepLib")?)?;
    let mod21 = rt.import_module("OCP.gp")?;
    e.set("gp_Ax2", rt.member("OCP.gp", "gp_Ax2")?)?;
    e.set("gp_Dir", rt.member("OCP.gp", "gp_Dir")?)?;
    e.set("gp_Pnt", rt.member("OCP.gp", "gp_Pnt")?)?;
    let mod22 = rt.import_module("OCP.HLRAlgo")?;
    e.set(
        "HLRAlgo_Projector",
        rt.member("OCP.HLRAlgo", "HLRAlgo_Projector")?,
    )?;
    let mod23 = rt.import_module("OCP.HLRBRep")?;
    e.set("HLRBRep_Algo", rt.member("OCP.HLRBRep", "HLRBRep_Algo")?)?;
    e.set(
        "HLRBRep_HLRToShape",
        rt.member("OCP.HLRBRep", "HLRBRep_HLRToShape")?,
    )?;
    let mod24 = rt.import_module("shapely")?;
    e.set("line_merge", rt.member("shapely", "line_merge")?)?;
    e.set("union_all", rt.member("shapely", "union_all")?)?;
    let mod25 = rt.import_module("shapely.geometry")?;
    e.set("LineString", rt.member("shapely.geometry", "LineString")?)?;
    e.set("Polygon", rt.member("shapely.geometry", "Polygon")?)?;
    e.set("art", rt.import_module("_cad_art")?)?;
    let assigned26 = binary(
        "truediv",
        e.get("ROOT")?,
        Val::Str(
            "ios/SodaMachine/SodaMachine/Assets.xcassets/HoldAtFaucet.imageset/HoldAtFaucet.svg"
                .into(),
        ),
    )?;
    e.set("ASSET", assigned26.clone())?;
    let assigned27 = Val::Float(15.0f64);
    e.set("ELEVATION", assigned27.clone())?;
    let assigned28 = {
        let mut s = Vec::new();
        s.push(Val::Float(71.6f64));
        s.push(Val::Float(147.6f64));
        s.push(Val::Float(7.8f64));
        Val::tuple(s)
    };
    e.set("PHONE", assigned28.clone())?;
    let assigned29 = Val::Float(34.0f64);
    e.set("TWIST", assigned29.clone())?;
    let assigned30 = Val::Float(20.0f64);
    e.set("GAP", assigned30.clone())?;
    let assigned31 = Val::Float(3.0f64);
    e.set("CORNER", assigned31.clone())?;
    let assigned32 = unary("neg", Val::Float(19.012f64))?;
    e.set("LEFT", assigned32.clone())?;
    let assigned33 = {
        let mut s = Vec::new();
        s.push(Val::Float(143.48f64));
        s.push(Val::Float(126.63f64));
        Val::tuple(s)
    };
    let unpack34 = unpack(assigned33.clone(), 2)?;
    e.set("WIDTH", unpack34[0].clone())?;
    e.set("HEIGHT", unpack34[1].clone())?;
    let assigned35 = {
        let mut s = Vec::new();
        s.push(Val::Float(0.58f64));
        s.push(Val::Float(0.78f64));
        Val::tuple(s)
    };
    e.set("PHONE_FADE", assigned35.clone())?;
    // projected
    e.set("projected", {
        let params = vec![("v".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned36 = {
                let fun39 = e.get("math")?.attr("radians")?;
                let mut args37 = Vec::new();
                let mut kw38 = Vec::new();
                args37.push(e.get("ELEVATION")?);
                fun39.call(args37, kw38)?
            };
            e.set("e", assigned36.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("v")?.attr("x")?);
                s.push(binary(
                    "add",
                    binary("mul", e.get("v")?.attr("y")?, {
                        let fun42 = e.get("math")?.attr("sin")?;
                        let mut args40 = Vec::new();
                        let mut kw41 = Vec::new();
                        args40.push(e.get("e")?);
                        fun42.call(args40, kw41)?
                    })?,
                    binary("mul", e.get("v")?.attr("z")?, {
                        let fun45 = e.get("math")?.attr("cos")?;
                        let mut args43 = Vec::new();
                        let mut kw44 = Vec::new();
                        args43.push(e.get("e")?);
                        fun45.call(args43, kw44)?
                    })?,
                )?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // polylines
    e.set("polylines", {
        let params = vec![("edges".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let fun48 = e.get("edges")?.attr("IsNull")?;
                let mut args46 = Vec::new();
                let mut kw47 = Vec::new();
                fun48.call(args46, kw47)?
            }
            .truthy()?
            {
                return Ok({
                    let mut s = Vec::new();
                    Val::list(s)
                });
            }
            {
                let fun51 = e.get("BRepLib")?.attr("BuildCurves3d_s")?;
                let mut args49 = Vec::new();
                let mut kw50 = Vec::new();
                args49.push(e.get("edges")?);
                args49.push(Val::Float(1e-07f64));
                fun51.call(args49, kw50)?
            };
            let assigned52 = {
                let fun55 = e.get("getPaths")?;
                let mut args53 = Vec::new();
                let mut kw54 = Vec::new();
                args53.push({
                    let mut s = Vec::new();
                    s.push({
                        let fun58 = e.get("cq")?.attr("Shape")?;
                        let mut args56 = Vec::new();
                        let mut kw57 = Vec::new();
                        args56.push(e.get("edges")?);
                        fun58.call(args56, kw57)?
                    });
                    Val::list(s)
                });
                args53.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                fun55.call(args53, kw54)?
            };
            let unpack59 = unpack(assigned52.clone(), 2)?;
            e.set("_", unpack59[0].clone())?;
            e.set("paths", unpack59[1].clone())?;
            return Ok({
                let e = e.child();
                let out60 = Val::list(vec![]);
                for item61 in e.get("paths")?.iter()? {
                    e.set("path", item61)?;
                    out60.attr("append")?.call(
                        vec![{
                            let e = e.child();
                            let out62 = Val::list(vec![]);
                            for item63 in {
                                let fun66 = e.get("re")?.attr("findall")?;
                                let mut args64 = Vec::new();
                                let mut kw65 = Vec::new();
                                args64.push(Val::Str("[ML]([-+\\d.eE]+),([-+\\d.eE]+)".into()));
                                args64.push(e.get("path")?);
                                fun66.call(args64, kw65)?
                            }
                            .iter()?
                            {
                                let unpack67 = unpack(item63, 2)?;
                                e.set("x", unpack67[0].clone())?;
                                e.set("y", unpack67[1].clone())?;
                                out62.attr("append")?.call(
                                    vec![{
                                        let mut s = Vec::new();
                                        s.push({
                                            let fun70 = e.get("float")?;
                                            let mut args68 = Vec::new();
                                            let mut kw69 = Vec::new();
                                            args68.push(e.get("x")?);
                                            fun70.call(args68, kw69)?
                                        });
                                        s.push({
                                            let fun73 = e.get("float")?;
                                            let mut args71 = Vec::new();
                                            let mut kw72 = Vec::new();
                                            args71.push(e.get("y")?);
                                            fun73.call(args71, kw72)?
                                        });
                                        Val::tuple(s)
                                    }],
                                    vec![],
                                )?;
                            }
                            out62
                        }],
                        vec![],
                    )?;
                }
                out60
            });
            Ok(Val::None)
        })
    })?;
    // visible_lines
    e.set("visible_lines", {
        let params = vec![("shapes".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned74 = {
                let fun77 = e.get("HLRBRep_Algo")?;
                let mut args75 = Vec::new();
                let mut kw76 = Vec::new();
                fun77.call(args75, kw76)?
            };
            e.set("hlr", assigned74.clone())?;
            for item78 in {
                let fun84 = e.get("shapes")?.attr("values")?;
                let mut args82 = Vec::new();
                let mut kw83 = Vec::new();
                fun84.call(args82, kw83)?
            }
            .iter()?
            {
                e.set("obj", item78)?;
                {
                    let fun81 = e.get("hlr")?.attr("Add")?;
                    let mut args79 = Vec::new();
                    let mut kw80 = Vec::new();
                    args79.push(e.get("obj")?.attr("wrapped")?);
                    fun81.call(args79, kw80)?
                };
            }
            let assigned85 = {
                let fun88 = e.get("math")?.attr("radians")?;
                let mut args86 = Vec::new();
                let mut kw87 = Vec::new();
                args86.push(e.get("ELEVATION")?);
                fun88.call(args86, kw87)?
            };
            e.set("e", assigned85.clone())?;
            {
                let fun91 = e.get("hlr")?.attr("Projector")?;
                let mut args89 = Vec::new();
                let mut kw90 = Vec::new();
                args89.push({
                    let fun94 = e.get("HLRAlgo_Projector")?;
                    let mut args92 = Vec::new();
                    let mut kw93 = Vec::new();
                    args92.push({
                        let fun97 = e.get("gp_Ax2")?;
                        let mut args95 = Vec::new();
                        let mut kw96 = Vec::new();
                        args95.push({
                            let fun100 = e.get("gp_Pnt")?;
                            let mut args98 = Vec::new();
                            let mut kw99 = Vec::new();
                            fun100.call(args98, kw99)?
                        });
                        args95.push({
                            let fun103 = e.get("gp_Dir")?;
                            let mut args101 = Vec::new();
                            let mut kw102 = Vec::new();
                            args101.push(Val::Int(0i64));
                            args101.push(unary("neg", {
                                let fun106 = e.get("math")?.attr("cos")?;
                                let mut args104 = Vec::new();
                                let mut kw105 = Vec::new();
                                args104.push(e.get("e")?);
                                fun106.call(args104, kw105)?
                            })?);
                            args101.push({
                                let fun109 = e.get("math")?.attr("sin")?;
                                let mut args107 = Vec::new();
                                let mut kw108 = Vec::new();
                                args107.push(e.get("e")?);
                                fun109.call(args107, kw108)?
                            });
                            fun103.call(args101, kw102)?
                        });
                        args95.push({
                            let fun112 = e.get("gp_Dir")?;
                            let mut args110 = Vec::new();
                            let mut kw111 = Vec::new();
                            args110.push(Val::Int(1i64));
                            args110.push(Val::Int(0i64));
                            args110.push(Val::Int(0i64));
                            fun112.call(args110, kw111)?
                        });
                        fun97.call(args95, kw96)?
                    });
                    fun94.call(args92, kw93)?
                });
                fun91.call(args89, kw90)?
            };
            {
                let fun115 = e.get("hlr")?.attr("Update")?;
                let mut args113 = Vec::new();
                let mut kw114 = Vec::new();
                fun115.call(args113, kw114)?
            };
            {
                let fun118 = e.get("hlr")?.attr("Hide")?;
                let mut args116 = Vec::new();
                let mut kw117 = Vec::new();
                fun118.call(args116, kw117)?
            };
            let assigned119 = {
                let fun122 = e.get("HLRBRep_HLRToShape")?;
                let mut args120 = Vec::new();
                let mut kw121 = Vec::new();
                args120.push(e.get("hlr")?);
                fun122.call(args120, kw121)?
            };
            e.set("lines", assigned119.clone())?;
            return Ok({
                let e = e.child();
                let out123 = Val::dict(vec![]);
                for item124 in {
                    let fun127 = e.get("shapes")?.attr("items")?;
                    let mut args125 = Vec::new();
                    let mut kw126 = Vec::new();
                    fun127.call(args125, kw126)?
                }
                .iter()?
                {
                    let unpack128 = unpack(item124, 2)?;
                    e.set("name", unpack128[0].clone())?;
                    e.set("obj", unpack128[1].clone())?;
                    out123.set(e.get("name")?, {
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("sharp".into()), {
                            let fun131 = e.get("polylines")?;
                            let mut args129 = Vec::new();
                            let mut kw130 = Vec::new();
                            args129.push({
                                let fun134 = e.get("lines")?.attr("VCompound")?;
                                let mut args132 = Vec::new();
                                let mut kw133 = Vec::new();
                                args132.push(e.get("obj")?.attr("wrapped")?);
                                fun134.call(args132, kw133)?
                            });
                            fun131.call(args129, kw130)?
                        })?;
                        d.set(Val::Str("outline".into()), {
                            let fun137 = e.get("polylines")?;
                            let mut args135 = Vec::new();
                            let mut kw136 = Vec::new();
                            args135.push({
                                let fun140 = e.get("lines")?.attr("OutLineVCompound")?;
                                let mut args138 = Vec::new();
                                let mut kw139 = Vec::new();
                                args138.push(e.get("obj")?.attr("wrapped")?);
                                fun140.call(args138, kw139)?
                            });
                            fun137.call(args135, kw136)?
                        })?;
                        d
                    })?;
                }
                out123
            });
            Ok(Val::None)
        })
    })?;
    // wire_lines
    e.set("wire_lines", {
        let params = vec![("wire".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned141 = {
                let fun144 = e.get("visible_lines")?;
                let mut args142 = Vec::new();
                let mut kw143 = Vec::new();
                args142.push({
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("wire".into()), e.get("wire")?)?;
                    d
                });
                fun144.call(args142, kw143)?
            }
            .get(Val::Str("wire".into()))?;
            e.set("lines", assigned141.clone())?;
            return Ok(binary(
                "add",
                e.get("lines")?.get(Val::Str("sharp".into()))?,
                e.get("lines")?.get(Val::Str("outline".into()))?,
            )?);
            Ok(Val::None)
        })
    })?;
    // front_face
    e.set("front_face", {
        let params = vec![("obj".into(), None, false), ("normal".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun147 = e.get("max")?;
                let mut args145 = Vec::new();
                let mut kw146 = Vec::new();
                args145.push({
                    let e = e.child();
                    let out148 = Val::list(vec![]);
                    for item149 in {
                        let fun152 = e.get("obj")?.attr("Faces")?;
                        let mut args150 = Vec::new();
                        let mut kw151 = Vec::new();
                        fun152.call(args150, kw151)?
                    }
                    .iter()?
                    {
                        e.set("face", item149)?;
                        if {
                            let v161 = {
                                let v165 = {
                                    let fun164 = e.get("face")?.attr("geomType")?;
                                    let mut args162 = Vec::new();
                                    let mut kw163 = Vec::new();
                                    fun164.call(args162, kw163)?
                                };
                                let v166 = Val::Str("PLANE".into());
                                Val::Bool(compare("eq", v165.clone(), v166.clone())?.truthy()?)
                            };
                            if v161.truthy()? {
                                {
                                    let v159 = {
                                        let fun155 = {
                                            let fun158 = e.get("face")?.attr("normalAt")?;
                                            let mut args156 = Vec::new();
                                            let mut kw157 = Vec::new();
                                            fun158.call(args156, kw157)?
                                        }
                                        .attr("dot")?;
                                        let mut args153 = Vec::new();
                                        let mut kw154 = Vec::new();
                                        args153.push(e.get("normal")?);
                                        fun155.call(args153, kw154)?
                                    };
                                    let v160 = Val::Float(0.999f64);
                                    Val::Bool(compare("gt", v159.clone(), v160.clone())?.truthy()?)
                                }
                            } else {
                                v161
                            }
                        }
                        .truthy()?
                        {
                            out148.attr("append")?.call(vec![e.get("face")?], vec![])?;
                        }
                    }
                    out148
                });
                kw146.push(("key".into(), {
                    let params = vec![("face".into(), None, false)];
                    let outer = e.clone();
                    let runtime = rt.clone();
                    Val::function(move |args, kwargs| {
                        let rt = runtime.clone();
                        let e = bind(&outer, &params, args, kwargs, None, None)?;
                        let _frame = rt.frame(&outer);
                        return Ok({
                            let fun169 = e.get("face")?.attr("Area")?;
                            let mut args167 = Vec::new();
                            let mut kw168 = Vec::new();
                            fun169.call(args167, kw168)?
                        });
                        Ok(Val::None)
                    })
                }));
                fun147.call(args145, kw146)?
            });
            Ok(Val::None)
        })
    })?;
    // silhouette
    e.set("silhouette", {
        let params = vec![("shapes".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned170 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("triangles", assigned170.clone())?;
            for item171 in e.get("shapes")?.iter()? {
                e.set("obj", item171)?;
                let assigned172 = {
                    let fun175 = e.get("obj")?.attr("tessellate")?;
                    let mut args173 = Vec::new();
                    let mut kw174 = Vec::new();
                    args173.push(Val::Float(0.025f64));
                    args173.push(Val::Float(0.04f64));
                    fun175.call(args173, kw174)?
                };
                let unpack176 = unpack(assigned172.clone(), 2)?;
                e.set("vertices", unpack176[0].clone())?;
                e.set("faces", unpack176[1].clone())?;
                let assigned177 = {
                    let e = e.child();
                    let out178 = Val::list(vec![]);
                    for item179 in e.get("vertices")?.iter()? {
                        e.set("v", item179)?;
                        out178.attr("append")?.call(
                            vec![{
                                let fun182 = e.get("projected")?;
                                let mut args180 = Vec::new();
                                let mut kw181 = Vec::new();
                                args180.push(e.get("v")?);
                                fun182.call(args180, kw181)?
                            }],
                            vec![],
                        )?;
                    }
                    out178
                };
                e.set("points", assigned177.clone())?;
                for item183 in e.get("faces")?.iter()? {
                    e.set("face", item183)?;
                    let assigned184 = {
                        let fun187 = e.get("Polygon")?;
                        let mut args185 = Vec::new();
                        let mut kw186 = Vec::new();
                        args185.push({
                            let e = e.child();
                            let out188 = Val::list(vec![]);
                            for item189 in e.get("face")?.iter()? {
                                e.set("i", item189)?;
                                out188
                                    .attr("append")?
                                    .call(vec![e.get("points")?.get(e.get("i")?)?], vec![])?;
                            }
                            out188
                        });
                        fun187.call(args185, kw186)?
                    };
                    e.set("triangle", assigned184.clone())?;
                    if {
                        let v190 = e.get("triangle")?.attr("area")?;
                        let v191 = Val::Float(1e-09f64);
                        Val::Bool(compare("gt", v190.clone(), v191.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun194 = e.get("triangles")?.attr("append")?;
                            let mut args192 = Vec::new();
                            let mut kw193 = Vec::new();
                            args192.push(e.get("triangle")?);
                            fun194.call(args192, kw193)?
                        };
                    }
                }
            }
            let assigned195 = {
                let fun198 = e.get("union_all")?;
                let mut args196 = Vec::new();
                let mut kw197 = Vec::new();
                args196.push(e.get("triangles")?);
                kw197.push(("grid_size".into(), Val::Float(0.001f64)));
                fun198.call(args196, kw197)?
            };
            e.set("merged", assigned195.clone())?;
            if {
                let v199 = e.get("merged")?.attr("geom_type")?;
                let v200 = Val::Str("MultiPolygon".into());
                Val::Bool(compare("eq", v199.clone(), v200.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned201 = {
                    let fun204 = e.get("max")?;
                    let mut args202 = Vec::new();
                    let mut kw203 = Vec::new();
                    args202.push(e.get("merged")?.attr("geoms")?);
                    kw203.push(("key".into(), {
                        let params = vec![("poly".into(), None, false)];
                        let outer = e.clone();
                        let runtime = rt.clone();
                        Val::function(move |args, kwargs| {
                            let rt = runtime.clone();
                            let e = bind(&outer, &params, args, kwargs, None, None)?;
                            let _frame = rt.frame(&outer);
                            return Ok(e.get("poly")?.attr("area")?);
                            Ok(Val::None)
                        })
                    }));
                    fun204.call(args202, kw203)?
                };
                e.set("merged", assigned201.clone())?;
            }
            return Ok({
                let fun207 = e.get("list")?;
                let mut args205 = Vec::new();
                let mut kw206 = Vec::new();
                args205.push(
                    {
                        let fun210 = e.get("merged")?.attr("exterior")?.attr("simplify")?;
                        let mut args208 = Vec::new();
                        let mut kw209 = Vec::new();
                        args208.push(Val::Float(0.008f64));
                        kw209.push(("preserve_topology".into(), Val::Bool(true)));
                        fun210.call(args208, kw209)?
                    }
                    .attr("coords")?,
                );
                fun207.call(args205, kw206)?
            });
            Ok(Val::None)
        })
    })?;
    // clip
    e.set("clip", {
        let params = vec![("line".into(), None, false), ("inside".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned211 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                s.push(
                    if {
                        let v215 = {
                            let fun214 = e.get("inside")?;
                            let mut args212 = Vec::new();
                            let mut kw213 = Vec::new();
                            args212.push(e.get("line")?.get(Val::Int(0i64))?);
                            fun214.call(args212, kw213)?
                        };
                        let v216 = Val::Int(0i64);
                        Val::Bool(compare("ge", v215.clone(), v216.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let mut s = Vec::new();
                            s.push(e.get("line")?.get(Val::Int(0i64))?);
                            Val::list(s)
                        }
                    } else {
                        {
                            let mut s = Vec::new();
                            Val::list(s)
                        }
                    },
                );
                Val::tuple(s)
            };
            let unpack217 = unpack(assigned211.clone(), 2)?;
            e.set("pieces", unpack217[0].clone())?;
            e.set("piece", unpack217[1].clone())?;
            for item218 in {
                let fun249 = e.get("zip")?;
                let mut args247 = Vec::new();
                let mut kw248 = Vec::new();
                args247.push(e.get("line")?);
                args247.push(e.get("line")?.get(Val::Slice {
                    start: Some(Val::Int(1i64).integer()?),
                    stop: None,
                    step: 1,
                })?);
                fun249.call(args247, kw248)?
            }
            .iter()?
            {
                let unpack250 = unpack(item218, 2)?;
                e.set("a", unpack250[0].clone())?;
                e.set("b", unpack250[1].clone())?;
                let assigned219 = {
                    let mut s = Vec::new();
                    s.push({
                        let fun222 = e.get("inside")?;
                        let mut args220 = Vec::new();
                        let mut kw221 = Vec::new();
                        args220.push(e.get("a")?);
                        fun222.call(args220, kw221)?
                    });
                    s.push({
                        let fun225 = e.get("inside")?;
                        let mut args223 = Vec::new();
                        let mut kw224 = Vec::new();
                        args223.push(e.get("b")?);
                        fun225.call(args223, kw224)?
                    });
                    Val::tuple(s)
                };
                let unpack226 = unpack(assigned219.clone(), 2)?;
                e.set("fa", unpack226[0].clone())?;
                e.set("fb", unpack226[1].clone())?;
                if {
                    let v231 = {
                        let v227 = e.get("fa")?;
                        let v228 = Val::Int(0i64);
                        Val::Bool(compare("ge", v227.clone(), v228.clone())?.truthy()?)
                    };
                    let v232 = {
                        let v229 = e.get("fb")?;
                        let v230 = Val::Int(0i64);
                        Val::Bool(compare("ge", v229.clone(), v230.clone())?.truthy()?)
                    };
                    Val::Bool(compare("ne", v231.clone(), v232.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned233 = binary(
                        "truediv",
                        e.get("fa")?,
                        binary("sub", e.get("fa")?, e.get("fb")?)?,
                    )?;
                    e.set("k", assigned233.clone())?;
                    let assigned234 = {
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            e.get("a")?.get(Val::Int(0i64))?,
                            binary(
                                "mul",
                                e.get("k")?,
                                binary(
                                    "sub",
                                    e.get("b")?.get(Val::Int(0i64))?,
                                    e.get("a")?.get(Val::Int(0i64))?,
                                )?,
                            )?,
                        )?);
                        s.push(binary(
                            "add",
                            e.get("a")?.get(Val::Int(1i64))?,
                            binary(
                                "mul",
                                e.get("k")?,
                                binary(
                                    "sub",
                                    e.get("b")?.get(Val::Int(1i64))?,
                                    e.get("a")?.get(Val::Int(1i64))?,
                                )?,
                            )?,
                        )?);
                        Val::tuple(s)
                    };
                    e.set("cut", assigned234.clone())?;
                    if {
                        let v235 = e.get("fa")?;
                        let v236 = Val::Int(0i64);
                        Val::Bool(compare("ge", v235.clone(), v236.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun239 = e.get("pieces")?.attr("append")?;
                            let mut args237 = Vec::new();
                            let mut kw238 = Vec::new();
                            args237.push(binary("add", e.get("piece")?, {
                                let mut s = Vec::new();
                                s.push(e.get("cut")?);
                                Val::list(s)
                            })?);
                            fun239.call(args237, kw238)?
                        };
                        let assigned240 = {
                            let mut s = Vec::new();
                            Val::list(s)
                        };
                        e.set("piece", assigned240.clone())?;
                    } else {
                        let assigned241 = {
                            let mut s = Vec::new();
                            s.push(e.get("cut")?);
                            Val::list(s)
                        };
                        e.set("piece", assigned241.clone())?;
                    }
                }
                if {
                    let v242 = e.get("fb")?;
                    let v243 = Val::Int(0i64);
                    Val::Bool(compare("ge", v242.clone(), v243.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun246 = e.get("piece")?.attr("append")?;
                        let mut args244 = Vec::new();
                        let mut kw245 = Vec::new();
                        args244.push(e.get("b")?);
                        fun246.call(args244, kw245)?
                    };
                }
            }
            {
                let fun253 = e.get("pieces")?.attr("append")?;
                let mut args251 = Vec::new();
                let mut kw252 = Vec::new();
                args251.push(e.get("piece")?);
                fun253.call(args251, kw252)?
            };
            return Ok({
                let e = e.child();
                let out254 = Val::list(vec![]);
                for item255 in e.get("pieces")?.iter()? {
                    e.set("p", item255)?;
                    if {
                        let v259 = {
                            let fun258 = e.get("len")?;
                            let mut args256 = Vec::new();
                            let mut kw257 = Vec::new();
                            args256.push(e.get("p")?);
                            fun258.call(args256, kw257)?
                        };
                        let v260 = Val::Int(1i64);
                        Val::Bool(compare("gt", v259.clone(), v260.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        out254.attr("append")?.call(vec![e.get("p")?], vec![])?;
                    }
                }
                out254
            });
            Ok(Val::None)
        })
    })?;
    e.set("Pen.__init__", {
        let params = vec![("self".into(), None, false), ("top".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned261 = e.get("top")?;
            e.get("self")?.setattr("top", assigned261.clone())?;
            let assigned262 = Val::None;
            e.get("self")?.setattr("occluder", assigned262.clone())?;
            Ok(Val::None)
        })
    })?;
    e.set("Pen.page", {
        let params = vec![("self".into(), None, false), ("p".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("p")?.get(Val::Int(0i64))?,
                    e.get("LEFT")?,
                )?);
                s.push(binary(
                    "sub",
                    e.get("self")?.attr("top")?,
                    e.get("p")?.get(Val::Int(1i64))?,
                )?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    e.set("Pen.curve", {
        let params = vec![
            ("self".into(), None, false),
            ("points".into(), None, false),
            ("closed".into(), Some(Val::Bool(false)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned263 = {
                let e = e.child();
                let out264 = Val::list(vec![]);
                for item265 in e.get("points")?.iter()? {
                    e.set("p", item265)?;
                    out264.attr("append")?.call(
                        vec![{
                            let fun268 = e.get("self")?.attr("page")?;
                            let mut args266 = Vec::new();
                            let mut kw267 = Vec::new();
                            args266.push(e.get("p")?);
                            fun268.call(args266, kw267)?
                        }],
                        vec![],
                    )?;
                }
                out264
            };
            e.set("points", assigned263.clone())?;
            if {
                let v274 = e.get("closed")?;
                if v274.truthy()? {
                    {
                        let v272 = {
                            let fun271 = e.get("math")?.attr("dist")?;
                            let mut args269 = Vec::new();
                            let mut kw270 = Vec::new();
                            args269.push(e.get("points")?.get(Val::Int(0i64))?);
                            args269.push(e.get("points")?.get(unary("neg", Val::Int(1i64))?)?);
                            fun271.call(args269, kw270)?
                        };
                        let v273 = Val::Float(0.01f64);
                        Val::Bool(compare("lt", v272.clone(), v273.clone())?.truthy()?)
                    }
                } else {
                    v274
                }
            }
            .truthy()?
            {
                let assigned275 = e.get("points")?.get(Val::Slice {
                    start: None,
                    stop: Some(unary("neg", Val::Int(1i64))?.integer()?),
                    step: 1,
                })?;
                e.set("points", assigned275.clone())?;
            }
            if {
                let v279 = {
                    let fun278 = e.get("len")?;
                    let mut args276 = Vec::new();
                    let mut kw277 = Vec::new();
                    args276.push(e.get("points")?);
                    fun278.call(args276, kw277)?
                };
                let v280 = Val::Int(2i64);
                Val::Bool(compare("lt", v279.clone(), v280.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(Val::Str("".into()));
            }
            let assigned281 = {
                let params = vec![("p".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    return Ok({
                        let mut str282 = String::new();
                        str282.push_str(&format(
                            &e.get("p")?.get(Val::Int(0i64))?,
                            &val_string({
                                let mut str283 = String::new();
                                str283.push_str(".3f");
                                Val::Str(str283)
                            })?,
                        )?);
                        str282.push_str(",");
                        str282.push_str(&format(
                            &e.get("p")?.get(Val::Int(1i64))?,
                            &val_string({
                                let mut str284 = String::new();
                                str284.push_str(".3f");
                                Val::Str(str284)
                            })?,
                        )?);
                        Val::Str(str282)
                    });
                    Ok(Val::None)
                })
            };
            e.set("fmt", assigned281.clone())?;
            let assigned285 = {
                let fun288 = e.get("len")?;
                let mut args286 = Vec::new();
                let mut kw287 = Vec::new();
                args286.push(e.get("points")?);
                fun288.call(args286, kw287)?
            };
            e.set("n", assigned285.clone())?;
            // tangent
            e.set("tangent", {
                let params = vec![("i".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    if {
                        let v291 = unary("not", e.get("closed")?)?;
                        if v291.truthy()? {
                            {
                                let v289 = e.get("i")?;
                                let v290 = {
                                    let mut s = Vec::new();
                                    s.push(Val::Int(0i64));
                                    s.push(binary("sub", e.get("n")?, Val::Int(1i64))?);
                                    Val::tuple(s)
                                };
                                Val::Bool(compare("in", v289.clone(), v290.clone())?.truthy()?)
                            }
                        } else {
                            v291
                        }
                    }
                    .truthy()?
                    {
                        let assigned292 = {
                            let mut s = Vec::new();
                            s.push(e.get("points")?.get({
                                let fun295 = e.get("max")?;
                                let mut args293 = Vec::new();
                                let mut kw294 = Vec::new();
                                args293.push(Val::Int(0i64));
                                args293.push(binary("sub", e.get("i")?, Val::Int(1i64))?);
                                fun295.call(args293, kw294)?
                            })?);
                            s.push(e.get("points")?.get({
                                let fun298 = e.get("min")?;
                                let mut args296 = Vec::new();
                                let mut kw297 = Vec::new();
                                args296.push(binary("add", e.get("i")?, Val::Int(1i64))?);
                                args296.push(binary("sub", e.get("n")?, Val::Int(1i64))?);
                                fun298.call(args296, kw297)?
                            })?);
                            Val::tuple(s)
                        };
                        let unpack299 = unpack(assigned292.clone(), 2)?;
                        e.set("a", unpack299[0].clone())?;
                        e.set("b", unpack299[1].clone())?;
                        let assigned300 = {
                            let fun303 = e.get("math")?.attr("dist")?;
                            let mut args301 = Vec::new();
                            let mut kw302 = Vec::new();
                            args301.push(e.get("a")?);
                            args301.push(e.get("b")?);
                            fun303.call(args301, kw302)?
                        };
                        e.set("length", assigned300.clone())?;
                        return Ok(if e.get("length")?.truthy()? {
                            {
                                let mut s = Vec::new();
                                s.push(binary(
                                    "truediv",
                                    binary(
                                        "sub",
                                        e.get("b")?.get(Val::Int(0i64))?,
                                        e.get("a")?.get(Val::Int(0i64))?,
                                    )?,
                                    e.get("length")?,
                                )?);
                                s.push(binary(
                                    "truediv",
                                    binary(
                                        "sub",
                                        e.get("b")?.get(Val::Int(1i64))?,
                                        e.get("a")?.get(Val::Int(1i64))?,
                                    )?,
                                    e.get("length")?,
                                )?);
                                Val::tuple(s)
                            }
                        } else {
                            {
                                let mut s = Vec::new();
                                s.push(Val::Int(0i64));
                                s.push(Val::Int(0i64));
                                Val::tuple(s)
                            }
                        });
                    }
                    let assigned304 = {
                        let mut s = Vec::new();
                        s.push(e.get("points")?.get(binary(
                            "mod",
                            binary("sub", e.get("i")?, Val::Int(1i64))?,
                            e.get("n")?,
                        )?)?);
                        s.push(e.get("points")?.get(e.get("i")?)?);
                        s.push(e.get("points")?.get(binary(
                            "mod",
                            binary("add", e.get("i")?, Val::Int(1i64))?,
                            e.get("n")?,
                        )?)?);
                        Val::tuple(s)
                    };
                    let unpack305 = unpack(assigned304.clone(), 3)?;
                    e.set("a", unpack305[0].clone())?;
                    e.set("b", unpack305[1].clone())?;
                    e.set("c", unpack305[2].clone())?;
                    let assigned306 = {
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary(
                                "sub",
                                e.get("b")?.get(Val::Int(0i64))?,
                                e.get("a")?.get(Val::Int(0i64))?,
                            )?);
                            s.push(binary(
                                "sub",
                                e.get("b")?.get(Val::Int(1i64))?,
                                e.get("a")?.get(Val::Int(1i64))?,
                            )?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary(
                                "sub",
                                e.get("c")?.get(Val::Int(0i64))?,
                                e.get("b")?.get(Val::Int(0i64))?,
                            )?);
                            s.push(binary(
                                "sub",
                                e.get("c")?.get(Val::Int(1i64))?,
                                e.get("b")?.get(Val::Int(1i64))?,
                            )?);
                            Val::tuple(s)
                        });
                        Val::tuple(s)
                    };
                    let unpack307 = unpack(assigned306.clone(), 2)?;
                    e.set("u", unpack307[0].clone())?;
                    e.set("v", unpack307[1].clone())?;
                    let assigned308 = {
                        let mut s = Vec::new();
                        s.push({
                            let fun311 = e.get("math")?.attr("hypot")?;
                            let mut args309 = Vec::new();
                            let mut kw310 = Vec::new();
                            args309.extend(e.get("u")?.iter()?);
                            fun311.call(args309, kw310)?
                        });
                        s.push({
                            let fun314 = e.get("math")?.attr("hypot")?;
                            let mut args312 = Vec::new();
                            let mut kw313 = Vec::new();
                            args312.extend(e.get("v")?.iter()?);
                            fun314.call(args312, kw313)?
                        });
                        Val::tuple(s)
                    };
                    let unpack315 = unpack(assigned308.clone(), 2)?;
                    e.set("lu", unpack315[0].clone())?;
                    e.set("lv", unpack315[1].clone())?;
                    if {
                        let v319 = {
                            let fun318 = e.get("min")?;
                            let mut args316 = Vec::new();
                            let mut kw317 = Vec::new();
                            args316.push(e.get("lu")?);
                            args316.push(e.get("lv")?);
                            fun318.call(args316, kw317)?
                        };
                        let v320 = Val::Float(1e-08f64);
                        Val::Bool(compare("lt", v319.clone(), v320.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        return Ok({
                            let mut s = Vec::new();
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(0i64));
                            Val::tuple(s)
                        });
                    }
                    if {
                        let v327 = binary(
                            "truediv",
                            binary(
                                "add",
                                binary(
                                    "mul",
                                    e.get("u")?.get(Val::Int(0i64))?,
                                    e.get("v")?.get(Val::Int(0i64))?,
                                )?,
                                binary(
                                    "mul",
                                    e.get("u")?.get(Val::Int(1i64))?,
                                    e.get("v")?.get(Val::Int(1i64))?,
                                )?,
                            )?,
                            binary("mul", e.get("lu")?, e.get("lv")?)?,
                        )?;
                        let v328 = {
                            let fun323 = e.get("math")?.attr("cos")?;
                            let mut args321 = Vec::new();
                            let mut kw322 = Vec::new();
                            args321.push({
                                let fun326 = e.get("math")?.attr("radians")?;
                                let mut args324 = Vec::new();
                                let mut kw325 = Vec::new();
                                args324.push(Val::Int(32i64));
                                fun326.call(args324, kw325)?
                            });
                            fun323.call(args321, kw322)?
                        };
                        Val::Bool(compare("lt", v327.clone(), v328.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        return Ok({
                            let mut s = Vec::new();
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(0i64));
                            Val::tuple(s)
                        });
                    }
                    if {
                        let v331 = {
                            let v332 = e.get("lu")?;
                            let v333 = Val::Float(1.25f64);
                            Val::Bool(compare("gt", v332.clone(), v333.clone())?.truthy()?)
                        };
                        if v331.truthy()? {
                            {
                                let v329 = e.get("lv")?;
                                let v330 = Val::Float(1.25f64);
                                Val::Bool(compare("lt", v329.clone(), v330.clone())?.truthy()?)
                            }
                        } else {
                            v331
                        }
                    }
                    .truthy()?
                    {
                        return Ok({
                            let mut s = Vec::new();
                            s.push(binary(
                                "truediv",
                                e.get("u")?.get(Val::Int(0i64))?,
                                e.get("lu")?,
                            )?);
                            s.push(binary(
                                "truediv",
                                e.get("u")?.get(Val::Int(1i64))?,
                                e.get("lu")?,
                            )?);
                            Val::tuple(s)
                        });
                    }
                    if {
                        let v336 = {
                            let v337 = e.get("lv")?;
                            let v338 = Val::Float(1.25f64);
                            Val::Bool(compare("gt", v337.clone(), v338.clone())?.truthy()?)
                        };
                        if v336.truthy()? {
                            {
                                let v334 = e.get("lu")?;
                                let v335 = Val::Float(1.25f64);
                                Val::Bool(compare("lt", v334.clone(), v335.clone())?.truthy()?)
                            }
                        } else {
                            v336
                        }
                    }
                    .truthy()?
                    {
                        return Ok({
                            let mut s = Vec::new();
                            s.push(binary(
                                "truediv",
                                e.get("v")?.get(Val::Int(0i64))?,
                                e.get("lv")?,
                            )?);
                            s.push(binary(
                                "truediv",
                                e.get("v")?.get(Val::Int(1i64))?,
                                e.get("lv")?,
                            )?);
                            Val::tuple(s)
                        });
                    }
                    let assigned339 = {
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            binary("truediv", e.get("u")?.get(Val::Int(0i64))?, e.get("lu")?)?,
                            binary("truediv", e.get("v")?.get(Val::Int(0i64))?, e.get("lv")?)?,
                        )?);
                        s.push(binary(
                            "add",
                            binary("truediv", e.get("u")?.get(Val::Int(1i64))?, e.get("lu")?)?,
                            binary("truediv", e.get("v")?.get(Val::Int(1i64))?, e.get("lv")?)?,
                        )?);
                        Val::tuple(s)
                    };
                    e.set("direction", assigned339.clone())?;
                    let assigned340 = {
                        let fun343 = e.get("math")?.attr("hypot")?;
                        let mut args341 = Vec::new();
                        let mut kw342 = Vec::new();
                        args341.extend(e.get("direction")?.iter()?);
                        fun343.call(args341, kw342)?
                    };
                    e.set("length", assigned340.clone())?;
                    return Ok({
                        let mut s = Vec::new();
                        s.push(binary(
                            "truediv",
                            e.get("direction")?.get(Val::Int(0i64))?,
                            e.get("length")?,
                        )?);
                        s.push(binary(
                            "truediv",
                            e.get("direction")?.get(Val::Int(1i64))?,
                            e.get("length")?,
                        )?);
                        Val::tuple(s)
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned344 = {
                let mut s = Vec::new();
                s.push(binary("add", Val::Str("M".into()), {
                    let fun347 = e.get("fmt")?;
                    let mut args345 = Vec::new();
                    let mut kw346 = Vec::new();
                    args345.push(e.get("points")?.get(Val::Int(0i64))?);
                    fun347.call(args345, kw346)?
                })?);
                Val::list(s)
            };
            e.set("out", assigned344.clone())?;
            for item348 in {
                let fun388 = e.get("range")?;
                let mut args386 = Vec::new();
                let mut kw387 = Vec::new();
                args386.push(if e.get("closed")?.truthy()? {
                    e.get("n")?
                } else {
                    binary("sub", e.get("n")?, Val::Int(1i64))?
                });
                fun388.call(args386, kw387)?
            }
            .iter()?
            {
                e.set("i", item348)?;
                let assigned349 = binary(
                    "mod",
                    binary("add", e.get("i")?, Val::Int(1i64))?,
                    e.get("n")?,
                )?;
                e.set("j", assigned349.clone())?;
                let assigned350 = {
                    let mut s = Vec::new();
                    s.push(e.get("points")?.get(e.get("i")?)?);
                    s.push(e.get("points")?.get(e.get("j")?)?);
                    Val::tuple(s)
                };
                let unpack351 = unpack(assigned350.clone(), 2)?;
                e.set("a", unpack351[0].clone())?;
                e.set("b", unpack351[1].clone())?;
                let assigned352 = {
                    let fun355 = e.get("math")?.attr("dist")?;
                    let mut args353 = Vec::new();
                    let mut kw354 = Vec::new();
                    args353.push(e.get("a")?);
                    args353.push(e.get("b")?);
                    fun355.call(args353, kw354)?
                };
                e.set("length", assigned352.clone())?;
                if {
                    let v356 = e.get("length")?;
                    let v357 = Val::Float(1.25f64);
                    Val::Bool(compare("gt", v356.clone(), v357.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun360 = e.get("out")?.attr("append")?;
                        let mut args358 = Vec::new();
                        let mut kw359 = Vec::new();
                        args358.push(binary("add", Val::Str("L".into()), {
                            let fun363 = e.get("fmt")?;
                            let mut args361 = Vec::new();
                            let mut kw362 = Vec::new();
                            args361.push(e.get("b")?);
                            fun363.call(args361, kw362)?
                        })?);
                        fun360.call(args358, kw359)?
                    };
                    continue;
                }
                let assigned364 = {
                    let mut s = Vec::new();
                    s.push({
                        let fun367 = e.get("tangent")?;
                        let mut args365 = Vec::new();
                        let mut kw366 = Vec::new();
                        args365.push(e.get("i")?);
                        fun367.call(args365, kw366)?
                    });
                    s.push({
                        let fun370 = e.get("tangent")?;
                        let mut args368 = Vec::new();
                        let mut kw369 = Vec::new();
                        args368.push(e.get("j")?);
                        fun370.call(args368, kw369)?
                    });
                    Val::tuple(s)
                };
                let unpack371 = unpack(assigned364.clone(), 2)?;
                e.set("ta", unpack371[0].clone())?;
                e.set("tb", unpack371[1].clone())?;
                let assigned372 = {
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("a")?.get(Val::Int(0i64))?,
                        binary(
                            "truediv",
                            binary("mul", e.get("ta")?.get(Val::Int(0i64))?, e.get("length")?)?,
                            Val::Int(3i64),
                        )?,
                    )?);
                    s.push(binary(
                        "add",
                        e.get("a")?.get(Val::Int(1i64))?,
                        binary(
                            "truediv",
                            binary("mul", e.get("ta")?.get(Val::Int(1i64))?, e.get("length")?)?,
                            Val::Int(3i64),
                        )?,
                    )?);
                    Val::tuple(s)
                };
                e.set("c1", assigned372.clone())?;
                let assigned373 = {
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        e.get("b")?.get(Val::Int(0i64))?,
                        binary(
                            "truediv",
                            binary("mul", e.get("tb")?.get(Val::Int(0i64))?, e.get("length")?)?,
                            Val::Int(3i64),
                        )?,
                    )?);
                    s.push(binary(
                        "sub",
                        e.get("b")?.get(Val::Int(1i64))?,
                        binary(
                            "truediv",
                            binary("mul", e.get("tb")?.get(Val::Int(1i64))?, e.get("length")?)?,
                            Val::Int(3i64),
                        )?,
                    )?);
                    Val::tuple(s)
                };
                e.set("c2", assigned373.clone())?;
                {
                    let fun376 = e.get("out")?.attr("append")?;
                    let mut args374 = Vec::new();
                    let mut kw375 = Vec::new();
                    args374.push(binary(
                        "add",
                        binary(
                            "add",
                            binary(
                                "add",
                                binary(
                                    "add",
                                    binary("add", Val::Str("C".into()), {
                                        let fun379 = e.get("fmt")?;
                                        let mut args377 = Vec::new();
                                        let mut kw378 = Vec::new();
                                        args377.push(e.get("c1")?);
                                        fun379.call(args377, kw378)?
                                    })?,
                                    Val::Str(" ".into()),
                                )?,
                                {
                                    let fun382 = e.get("fmt")?;
                                    let mut args380 = Vec::new();
                                    let mut kw381 = Vec::new();
                                    args380.push(e.get("c2")?);
                                    fun382.call(args380, kw381)?
                                },
                            )?,
                            Val::Str(" ".into()),
                        )?,
                        {
                            let fun385 = e.get("fmt")?;
                            let mut args383 = Vec::new();
                            let mut kw384 = Vec::new();
                            args383.push(e.get("b")?);
                            fun385.call(args383, kw384)?
                        },
                    )?);
                    fun376.call(args374, kw375)?
                };
            }
            if e.get("closed")?.truthy()? {
                {
                    let fun391 = e.get("out")?.attr("append")?;
                    let mut args389 = Vec::new();
                    let mut kw390 = Vec::new();
                    args389.push(Val::Str("Z".into()));
                    fun391.call(args389, kw390)?
                };
            }
            return Ok({
                let fun394 = Val::Str(" ".into()).attr("join")?;
                let mut args392 = Vec::new();
                let mut kw393 = Vec::new();
                args392.push(e.get("out")?);
                fun394.call(args392, kw393)?
            });
            Ok(Val::None)
        })
    })?;
    e.set("Pen.paths", {
        let params = vec![
            ("self".into(), None, false),
            ("lines".into(), None, false),
            ("simplify".into(), Some(Val::Float(0.009f64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned395 = {
                let e = e.child();
                let out396 = Val::list(vec![]);
                for item397 in e.get("lines")?.iter()? {
                    e.set("line", item397)?;
                    if {
                        let v403 = {
                            let v407 = {
                                let fun406 = e.get("len")?;
                                let mut args404 = Vec::new();
                                let mut kw405 = Vec::new();
                                args404.push(e.get("line")?);
                                fun406.call(args404, kw405)?
                            };
                            let v408 = Val::Int(1i64);
                            Val::Bool(compare("gt", v407.clone(), v408.clone())?.truthy()?)
                        };
                        if v403.truthy()? {
                            {
                                let v401 = {
                                    let fun400 = e.get("LineString")?;
                                    let mut args398 = Vec::new();
                                    let mut kw399 = Vec::new();
                                    args398.push(e.get("line")?);
                                    fun400.call(args398, kw399)?
                                }
                                .attr("length")?;
                                let v402 = Val::Float(0.05f64);
                                Val::Bool(compare("gt", v401.clone(), v402.clone())?.truthy()?)
                            }
                        } else {
                            v403
                        }
                    }
                    .truthy()?
                    {
                        out396.attr("append")?.call(
                            vec![{
                                let fun411 = e.get("LineString")?;
                                let mut args409 = Vec::new();
                                let mut kw410 = Vec::new();
                                args409.push(e.get("line")?);
                                fun411.call(args409, kw410)?
                            }],
                            vec![],
                        )?;
                    }
                }
                out396
            };
            e.set("lines", assigned395.clone())?;
            if unary("not", e.get("lines")?)?.truthy()? {
                return Ok({
                    let mut s = Vec::new();
                    Val::list(s)
                });
            }
            let assigned412 = {
                let fun415 = e.get("union_all")?;
                let mut args413 = Vec::new();
                let mut kw414 = Vec::new();
                args413.push(e.get("lines")?);
                kw414.push(("grid_size".into(), Val::Float(0.0005f64)));
                fun415.call(args413, kw414)?
            };
            e.set("merged", assigned412.clone())?;
            if {
                let v416 = e.get("self")?.attr("occluder")?;
                let v417 = Val::None;
                Val::Bool(compare("is_not", v416.clone(), v417.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned418 = {
                    let fun421 = e.get("merged")?.attr("difference")?;
                    let mut args419 = Vec::new();
                    let mut kw420 = Vec::new();
                    args419.push(e.get("self")?.attr("occluder")?);
                    fun421.call(args419, kw420)?
                };
                e.set("merged", assigned418.clone())?;
            }
            if e.get("merged")?.attr("is_empty")?.truthy()? {
                return Ok({
                    let mut s = Vec::new();
                    Val::list(s)
                });
            }
            let assigned422 = {
                let fun425 = e.get("line_merge")?;
                let mut args423 = Vec::new();
                let mut kw424 = Vec::new();
                args423.push(e.get("merged")?);
                fun425.call(args423, kw424)?
            };
            e.set("merged", assigned422.clone())?;
            let assigned426 = if {
                let v427 = e.get("merged")?.attr("geom_type")?;
                let v428 = Val::Str("LineString".into());
                Val::Bool(compare("eq", v427.clone(), v428.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let mut s = Vec::new();
                    s.push(e.get("merged")?);
                    Val::list(s)
                }
            } else {
                {
                    let fun431 = e.get("list")?;
                    let mut args429 = Vec::new();
                    let mut kw430 = Vec::new();
                    args429.push(e.get("merged")?.attr("geoms")?);
                    fun431.call(args429, kw430)?
                }
            };
            e.set("lines", assigned426.clone())?;
            let assigned432 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("result", assigned432.clone())?;
            for item433 in e.get("lines")?.iter()? {
                e.set("line", item433)?;
                if {
                    let v434 = e.get("line")?.attr("geom_type")?;
                    let v435 = Val::Str("LineString".into());
                    Val::Bool(compare("ne", v434.clone(), v435.clone())?.truthy()?)
                }
                .truthy()?
                {
                    continue;
                }
                let assigned436 = {
                    let fun439 = e.get("list")?;
                    let mut args437 = Vec::new();
                    let mut kw438 = Vec::new();
                    args437.push(
                        {
                            let fun442 = e.get("line")?.attr("simplify")?;
                            let mut args440 = Vec::new();
                            let mut kw441 = Vec::new();
                            args440.push(e.get("simplify")?);
                            fun442.call(args440, kw441)?
                        }
                        .attr("coords")?,
                    );
                    fun439.call(args437, kw438)?
                };
                e.set("points", assigned436.clone())?;
                {
                    let fun445 = e.get("result")?.attr("append")?;
                    let mut args443 = Vec::new();
                    let mut kw444 = Vec::new();
                    args443.push({
                        let fun448 = e.get("self")?.attr("curve")?;
                        let mut args446 = Vec::new();
                        let mut kw447 = Vec::new();
                        args446.push(e.get("points")?);
                        args446.push({
                            let v452 = {
                                let fun451 = e.get("math")?.attr("dist")?;
                                let mut args449 = Vec::new();
                                let mut kw450 = Vec::new();
                                args449.push(e.get("points")?.get(Val::Int(0i64))?);
                                args449.push(e.get("points")?.get(unary("neg", Val::Int(1i64))?)?);
                                fun451.call(args449, kw450)?
                            };
                            let v453 = Val::Float(0.015f64);
                            Val::Bool(compare("lt", v452.clone(), v453.clone())?.truthy()?)
                        });
                        fun448.call(args446, kw447)?
                    });
                    fun445.call(args443, kw444)?
                };
            }
            return Ok(e.get("result")?);
            Ok(Val::None)
        })
    })?;
    e.set("Pen.group", {
        let params = vec![
            ("self".into(), None, false),
            ("lines".into(), None, false),
            ("width".into(), None, false),
            ("opacity".into(), Some(Val::Int(1i64)), false),
            ("simplify".into(), Some(Val::Float(0.009f64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary(
                "add",
                binary(
                    "add",
                    {
                        let mut str454 = String::new();
                        str454.push_str("<g fill=\"none\" stroke=\"currentColor\" stroke-width=\"");
                        str454.push_str(&format(&e.get("width")?, &String::new())?);
                        str454.push_str("\" opacity=\"");
                        str454.push_str(&format(&e.get("opacity")?, &String::new())?);
                        str454.push_str("\">");
                        Val::Str(str454)
                    },
                    {
                        let fun457 = Val::Str("".into()).attr("join")?;
                        let mut args455 = Vec::new();
                        let mut kw456 = Vec::new();
                        args455.push({
                            let e = e.child();
                            let out458 = Val::list(vec![]);
                            for item459 in {
                                let fun462 = e.get("self")?.attr("paths")?;
                                let mut args460 = Vec::new();
                                let mut kw461 = Vec::new();
                                args460.push(e.get("lines")?);
                                args460.push(e.get("simplify")?);
                                fun462.call(args460, kw461)?
                            }
                            .iter()?
                            {
                                e.set("d", item459)?;
                                out458.attr("append")?.call(
                                    vec![{
                                        let mut str463 = String::new();
                                        str463.push_str("<path d=\"");
                                        str463.push_str(&format(&e.get("d")?, &String::new())?);
                                        str463.push_str("\"/>");
                                        Val::Str(str463)
                                    }],
                                    vec![],
                                )?;
                            }
                            out458
                        });
                        fun457.call(args455, kw456)?
                    },
                )?,
                Val::Str("</g>".into()),
            )?);
            Ok(Val::None)
        })
    })?;
    e.set("Pen.region", {
        let params = vec![("self".into(), None, false), ("region".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned464 = if {
                let v465 = e.get("region")?.attr("geom_type")?;
                let v466 = Val::Str("Polygon".into());
                Val::Bool(compare("eq", v465.clone(), v466.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let mut s = Vec::new();
                    s.push(e.get("region")?);
                    Val::list(s)
                }
            } else {
                {
                    let fun469 = e.get("list")?;
                    let mut args467 = Vec::new();
                    let mut kw468 = Vec::new();
                    args467.push(e.get("region")?.attr("geoms")?);
                    fun469.call(args467, kw468)?
                }
            };
            e.set("polygons", assigned464.clone())?;
            return Ok({
                let fun472 = Val::Str(" ".into()).attr("join")?;
                let mut args470 = Vec::new();
                let mut kw471 = Vec::new();
                args470.push({
                    let e = e.child();
                    let out473 = Val::list(vec![]);
                    for item474 in e.get("polygons")?.iter()? {
                        e.set("polygon", item474)?;
                        if {
                            let v475 = e.get("polygon")?.attr("geom_type")?;
                            let v476 = Val::Str("Polygon".into());
                            Val::Bool(compare("eq", v475.clone(), v476.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            for item477 in {
                                let mut s = Vec::new();
                                s.push(e.get("polygon")?.attr("exterior")?);
                                s.extend(e.get("polygon")?.attr("interiors")?.iter()?);
                                Val::tuple(s)
                            }
                            .iter()?
                            {
                                e.set("ring", item477)?;
                                out473.attr("append")?.call(
                                    vec![{
                                        let fun480 = e.get("self")?.attr("curve")?;
                                        let mut args478 = Vec::new();
                                        let mut kw479 = Vec::new();
                                        args478.push({
                                            let fun483 = e.get("list")?;
                                            let mut args481 = Vec::new();
                                            let mut kw482 = Vec::new();
                                            args481.push(e.get("ring")?.attr("coords")?);
                                            fun483.call(args481, kw482)?
                                        });
                                        args478.push(Val::Bool(true));
                                        fun480.call(args478, kw479)?
                                    }],
                                    vec![],
                                )?;
                            }
                        }
                    }
                    out473
                });
                fun472.call(args470, kw471)?
            });
            Ok(Val::None)
        })
    })?;
    e.set("Pen", rt.python_type("hold_scene", "Pen")?)?;
    // drawing
    e.set("drawing",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned484={let fun487=e.get("art")?.attr("_load_faucet_module")?;let mut args485=Vec::new();let mut kw486=Vec::new();fun487.call(args485,kw486)?};e.set("fa",assigned484.clone())?;
let assigned488={let fun491=e.get("fa")?.attr("load_shell_pieces")?;let mut args489=Vec::new();let mut kw490=Vec::new();fun491.call(args489,kw490)?};let unpack492=unpack(assigned488.clone(),2)?;e.set("_",unpack492[0].clone())?;e.set("tip",unpack492[1].clone())?;
let assigned493={let d=Val::dict(vec![]);d.set(Val::Str("tip".into()),{let fun496=e.get("tip")?.attr("val")?;let mut args494=Vec::new();let mut kw495=Vec::new();fun496.call(args494,kw495)?})?;d.set(Val::Str("cover".into()),{let fun499={let fun502=e.get("fa")?.attr("load_display_cover")?;let mut args500=Vec::new();let mut kw501=Vec::new();fun502.call(args500,kw501)?}.attr("val")?;let mut args497=Vec::new();let mut kw498=Vec::new();fun499.call(args497,kw498)?})?;d.set(Val::Str("display".into()),{let fun505={let fun508=e.get("fa")?.attr("build_display_body")?;let mut args506=Vec::new();let mut kw507=Vec::new();fun508.call(args506,kw507)?}.attr("val")?;let mut args503=Vec::new();let mut kw504=Vec::new();fun505.call(args503,kw504)?})?;d.set(Val::Str("screen".into()),{let fun511={let fun514=e.get("fa")?.attr("build_display_screen")?;let mut args512=Vec::new();let mut kw513=Vec::new();fun514.call(args512,kw513)?}.attr("val")?;let mut args509=Vec::new();let mut kw510=Vec::new();fun511.call(args509,kw510)?})?;d};e.set("head",assigned493.clone())?;
let assigned515={let fun518={let fun521={let fun524={let fun527=e.get("cq")?.attr("Workplane")?;let mut args525=Vec::new();let mut kw526=Vec::new();args525.push(Val::Str("XY".into()));fun527.call(args525,kw526)?}.attr("box")?;let mut args522=Vec::new();let mut kw523=Vec::new();args522.push(Val::Int(200i64));args522.push(Val::Int(100i64));args522.push(Val::Int(400i64));fun524.call(args522,kw523)?}.attr("translate")?;let mut args519=Vec::new();let mut kw520=Vec::new();args519.push({let mut s=Vec::new();s.push(Val::Int(0i64));s.push(unary("neg",Val::Int(150i64))?);s.push(Val::Int(150i64));Val::tuple(s)});fun521.call(args519,kw520)?}.attr("val")?;let mut args516=Vec::new();let mut kw517=Vec::new();fun518.call(args516,kw517)?};e.set("front",assigned515.clone())?;
for item528 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Str("soda".into()));s.push({let fun538=e.get("fa")?.attr("build_soda_faucet_tube")?;let mut args536=Vec::new();let mut kw537=Vec::new();fun538.call(args536,kw537)?});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("flavor_right".into()));s.push({let fun541=e.get("fa")?.attr("build_flavor_faucet_run")?;let mut args539=Vec::new();let mut kw540=Vec::new();args539.push(Val::Int(1i64));fun541.call(args539,kw540)?});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("flavor_left".into()));s.push({let fun544=e.get("fa")?.attr("build_flavor_faucet_run")?;let mut args542=Vec::new();let mut kw543=Vec::new();args542.push(unary("neg",Val::Int(1i64))?);fun544.call(args542,kw543)?});Val::tuple(s)});Val::tuple(s)}.iter()? {
let unpack545=unpack(item528,2)?;e.set("name",unpack545[0].clone())?;e.set("obj",unpack545[1].clone())?;let assigned529={let fun532={let fun535=e.get("obj")?.attr("val")?;let mut args533=Vec::new();let mut kw534=Vec::new();fun535.call(args533,kw534)?}.attr("intersect")?;let mut args530=Vec::new();let mut kw531=Vec::new();args530.push(e.get("front")?);fun532.call(args530,kw531)?};e.get("head")?.set(e.get("name")?,assigned529.clone())?;
}
let assigned546={let fun549=e.get("head")?.get(Val::Str("screen".into()))?.attr("BoundingBox")?;let mut args547=Vec::new();let mut kw548=Vec::new();fun549.call(args547,kw548)?};e.set("box",assigned546.clone())?;
let assigned550={let fun553=e.get("cq")?.attr("Vector")?;let mut args551=Vec::new();let mut kw552=Vec::new();args551.push(binary("truediv",binary("add",e.get("box")?.attr("xmin")?,e.get("box")?.attr("xmax")?)?,Val::Int(2i64))?);args551.push(binary("truediv",binary("add",e.get("box")?.attr("ymin")?,e.get("box")?.attr("ymax")?)?,Val::Int(2i64))?);args551.push(binary("truediv",binary("add",e.get("box")?.attr("zmin")?,e.get("box")?.attr("zmax")?)?,Val::Int(2i64))?);fun553.call(args551,kw552)?};e.set("centre",assigned550.clone())?;
let assigned554={let fun557={let fun560=e.get("cq")?.attr("Vector")?;let mut args558=Vec::new();let mut kw559=Vec::new();args558.push(Val::Int(0i64));args558.push(binary("sub",e.get("box")?.attr("ymax")?,e.get("box")?.attr("ymin")?)?);args558.push(binary("sub",e.get("box")?.attr("zmax")?,e.get("box")?.attr("zmin")?)?);fun560.call(args558,kw559)?}.attr("normalized")?;let mut args555=Vec::new();let mut kw556=Vec::new();fun557.call(args555,kw556)?};e.set("up",assigned554.clone())?;
let assigned561={let fun564=e.get("cq")?.attr("Vector")?;let mut args562=Vec::new();let mut kw563=Vec::new();args562.push(Val::Int(0i64));args562.push(unary("neg",e.get("up")?.attr("z")?)?);args562.push(e.get("up")?.attr("y")?);fun564.call(args562,kw563)?};e.set("normal",assigned561.clone())?;
let assigned565={let fun568=e.get("math")?.attr("degrees")?;let mut args566=Vec::new();let mut kw567=Vec::new();args566.push({let fun571=e.get("math")?.attr("atan2")?;let mut args569=Vec::new();let mut kw570=Vec::new();args569.push(e.get("up")?.attr("z")?);args569.push(e.get("up")?.attr("y")?);fun571.call(args569,kw570)?});fun568.call(args566,kw567)?};e.set("tilt",assigned565.clone())?;
let assigned572={let fun575=e.get("cq")?.attr("Vector")?;let mut args573=Vec::new();let mut kw574=Vec::new();args573.push(Val::Int(0i64));args573.push({let fun578=e.get("math")?.attr("sin")?;let mut args576=Vec::new();let mut kw577=Vec::new();args576.push({let fun581=e.get("math")?.attr("radians")?;let mut args579=Vec::new();let mut kw580=Vec::new();args579.push(e.get("ELEVATION")?);fun581.call(args579,kw580)?});fun578.call(args576,kw577)?});args573.push({let fun584=e.get("math")?.attr("cos")?;let mut args582=Vec::new();let mut kw583=Vec::new();args582.push({let fun587=e.get("math")?.attr("radians")?;let mut args585=Vec::new();let mut kw586=Vec::new();args585.push(e.get("ELEVATION")?);fun587.call(args585,kw586)?});fun584.call(args582,kw583)?});fun575.call(args573,kw574)?};e.set("view_y",assigned572.clone())?;
let assigned588=e.get("PHONE")?;let unpack589=unpack(assigned588.clone(),3)?;e.set("w",unpack589[0].clone())?;e.set("h",unpack589[1].clone())?;e.set("t",unpack589[2].clone())?;
// placed
e.set("placed",{let params=vec![("v".into(),None,false),("at".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned590={let mut s=Vec::new();s.push({let fun593=e.get("math")?.attr("radians")?;let mut args591=Vec::new();let mut kw592=Vec::new();args591.push(e.get("TWIST")?);fun593.call(args591,kw592)?});s.push({let fun596=e.get("math")?.attr("radians")?;let mut args594=Vec::new();let mut kw595=Vec::new();args594.push(e.get("tilt")?);fun596.call(args594,kw595)?});Val::tuple(s)};let unpack597=unpack(assigned590.clone(),2)?;e.set("tw",unpack597[0].clone())?;e.set("tl",unpack597[1].clone())?;
let assigned598=binary("sub",binary("mul",e.get("v")?.get(Val::Int(0i64))?,{let fun601=e.get("math")?.attr("cos")?;let mut args599=Vec::new();let mut kw600=Vec::new();args599.push(e.get("tw")?);fun601.call(args599,kw600)?})?,binary("mul",e.get("v")?.get(Val::Int(1i64))?,{let fun604=e.get("math")?.attr("sin")?;let mut args602=Vec::new();let mut kw603=Vec::new();args602.push(e.get("tw")?);fun604.call(args602,kw603)?})?)?;e.set("x",assigned598.clone())?;
let assigned605=binary("add",binary("mul",e.get("v")?.get(Val::Int(0i64))?,{let fun608=e.get("math")?.attr("sin")?;let mut args606=Vec::new();let mut kw607=Vec::new();args606.push(e.get("tw")?);fun608.call(args606,kw607)?})?,binary("mul",e.get("v")?.get(Val::Int(1i64))?,{let fun611=e.get("math")?.attr("cos")?;let mut args609=Vec::new();let mut kw610=Vec::new();args609.push(e.get("tw")?);fun611.call(args609,kw610)?})?)?;e.set("y",assigned605.clone())?;
return Ok(binary("add",{let fun614=e.get("cq")?.attr("Vector")?;let mut args612=Vec::new();let mut kw613=Vec::new();args612.push(e.get("x")?);args612.push(binary("sub",binary("mul",e.get("y")?,{let fun617=e.get("math")?.attr("cos")?;let mut args615=Vec::new();let mut kw616=Vec::new();args615.push(e.get("tl")?);fun617.call(args615,kw616)?})?,binary("mul",e.get("v")?.get(Val::Int(2i64))?,{let fun620=e.get("math")?.attr("sin")?;let mut args618=Vec::new();let mut kw619=Vec::new();args618.push(e.get("tl")?);fun620.call(args618,kw619)?})?)?);args612.push(binary("add",binary("mul",e.get("y")?,{let fun623=e.get("math")?.attr("sin")?;let mut args621=Vec::new();let mut kw622=Vec::new();args621.push(e.get("tl")?);fun623.call(args621,kw622)?})?,binary("mul",e.get("v")?.get(Val::Int(2i64))?,{let fun626=e.get("math")?.attr("cos")?;let mut args624=Vec::new();let mut kw625=Vec::new();args624.push(e.get("tl")?);fun626.call(args624,kw625)?})?)?);fun614.call(args612,kw613)?},e.get("at")?)?);
Ok(Val::None)})})?;
let assigned627=Val::Float(10.5f64);e.set("r",assigned627.clone())?;
let assigned628={let e=e.child();let out629=Val::list(vec![]);for item630 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Int(1i64));s.push(Val::Int(1i64));s.push(Val::Int(0i64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(unary("neg",Val::Int(1i64))?);s.push(Val::Int(1i64));s.push(Val::Int(90i64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(unary("neg",Val::Int(1i64))?);s.push(unary("neg",Val::Int(1i64))?);s.push(Val::Int(180i64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Int(1i64));s.push(unary("neg",Val::Int(1i64))?);s.push(Val::Int(270i64));Val::tuple(s)});Val::tuple(s)}.iter()? {let unpack631=unpack(item630,3)?;e.set("sx",unpack631[0].clone())?;e.set("sy",unpack631[1].clone())?;e.set("a0",unpack631[2].clone())?;for item632 in {let e=e.child();let out633=Val::list(vec![]);for item634 in {let fun637=e.get("range")?;let mut args635=Vec::new();let mut kw636=Vec::new();args635.push(Val::Int(0i64));args635.push(Val::Int(91i64));args635.push(Val::Int(3i64));fun637.call(args635,kw636)?}.iter()? {e.set("i",item634)?;out633.attr("append")?.call(vec![{let fun640=e.get("math")?.attr("radians")?;let mut args638=Vec::new();let mut kw639=Vec::new();args638.push(binary("add",e.get("a0")?,e.get("i")?)?);fun640.call(args638,kw639)?}],vec![])?;}out633}.iter()? {e.set("a",item632)?;out629.attr("append")?.call(vec![{let mut s=Vec::new();s.push(binary("add",binary("mul",e.get("sx")?,binary("sub",binary("truediv",e.get("w")?,Val::Int(2i64))?,e.get("r")?)?)?,binary("mul",e.get("r")?,{let fun643=e.get("math")?.attr("cos")?;let mut args641=Vec::new();let mut kw642=Vec::new();args641.push(e.get("a")?);fun643.call(args641,kw642)?})?)?);s.push(binary("add",binary("mul",e.get("sy")?,binary("sub",binary("truediv",e.get("h")?,Val::Int(2i64))?,e.get("r")?)?)?,binary("mul",e.get("r")?,{let fun646=e.get("math")?.attr("sin")?;let mut args644=Vec::new();let mut kw645=Vec::new();args644.push(e.get("a")?);fun646.call(args644,kw645)?})?)?);s.push(e.get("t")?);Val::tuple(s)}],vec![])?;}}out629};e.set("rim",assigned628.clone())?;
let assigned647=binary("add",e.get("centre")?,binary("mul",e.get("normal")?,e.get("GAP")?)?)?;e.set("at",assigned647.clone())?;
let assigned648={let fun651=e.get("min")?;let mut args649=Vec::new();let mut kw650=Vec::new();args649.push({let e=e.child();let out652=Val::list(vec![]);for item653 in e.get("rim")?.iter()? {e.set("v",item653)?;out652.attr("append")?.call(vec![{let fun656=e.get("projected")?;let mut args654=Vec::new();let mut kw655=Vec::new();args654.push({let fun659=e.get("placed")?;let mut args657=Vec::new();let mut kw658=Vec::new();args657.push(e.get("v")?);args657.push(e.get("at")?);fun659.call(args657,kw658)?});fun656.call(args654,kw655)?}],vec![])?;}out652});kw650.push(("key".into(),{let params=vec![("p".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok(e.get("p")?.get(Val::Int(0i64))?);
Ok(Val::None)})}));fun651.call(args649,kw650)?};e.set("left",assigned648.clone())?;
let assigned660={let fun663=e.get("projected")?;let mut args661=Vec::new();let mut kw662=Vec::new();args661.push(e.get("centre")?);fun663.call(args661,kw662)?};e.set("goal",assigned660.clone())?;
e.set("at",binary("add",e.get("at")?,binary("add",{let fun666=e.get("cq")?.attr("Vector")?;let mut args664=Vec::new();let mut kw665=Vec::new();args664.push(binary("sub",binary("add",e.get("goal")?.get(Val::Int(0i64))?,e.get("CORNER")?)?,e.get("left")?.get(Val::Int(0i64))?)?);args664.push(Val::Int(0i64));args664.push(Val::Int(0i64));fun666.call(args664,kw665)?},binary("mul",e.get("up")?,binary("truediv",binary("sub",e.get("goal")?.get(Val::Int(1i64))?,e.get("left")?.get(Val::Int(1i64))?)?,{let fun669=e.get("up")?.attr("dot")?;let mut args667=Vec::new();let mut kw668=Vec::new();args667.push(e.get("view_y")?);fun669.call(args667,kw668)?})?)?)?)?)?;
let assigned670={let fun673={let fun676={let fun679={let fun682={let fun685={let fun688={let fun691=e.get("cq")?.attr("Workplane")?;let mut args689=Vec::new();let mut kw690=Vec::new();args689.push(Val::Str("XY".into()));fun691.call(args689,kw690)?}.attr("box")?;let mut args686=Vec::new();let mut kw687=Vec::new();args686.push(e.get("w")?);args686.push(e.get("h")?);args686.push(e.get("t")?);kw687.push(("centered".into(),{let mut s=Vec::new();s.push(Val::Bool(true));s.push(Val::Bool(true));s.push(Val::Bool(false));Val::tuple(s)}));fun688.call(args686,kw687)?}.attr("edges")?;let mut args683=Vec::new();let mut kw684=Vec::new();args683.push(Val::Str("|Z".into()));fun685.call(args683,kw684)?}.attr("fillet")?;let mut args680=Vec::new();let mut kw681=Vec::new();args680.push(Val::Float(10.5f64));fun682.call(args680,kw681)?}.attr("edges")?;let mut args677=Vec::new();let mut kw678=Vec::new();args677.push(Val::Str(">Z or <Z".into()));fun679.call(args677,kw678)?}.attr("fillet")?;let mut args674=Vec::new();let mut kw675=Vec::new();args674.push(Val::Float(1.6f64));fun676.call(args674,kw675)?}.attr("val")?;let mut args671=Vec::new();let mut kw672=Vec::new();fun673.call(args671,kw672)?};e.set("phone",assigned670.clone())?;
let assigned692={let fun695={let fun698={let fun701=e.get("phone")?.attr("rotate")?;let mut args699=Vec::new();let mut kw700=Vec::new();args699.push({let mut s=Vec::new();s.push(Val::Int(0i64));s.push(Val::Int(0i64));s.push(Val::Int(0i64));Val::tuple(s)});args699.push({let mut s=Vec::new();s.push(Val::Int(0i64));s.push(Val::Int(0i64));s.push(Val::Int(1i64));Val::tuple(s)});args699.push(e.get("TWIST")?);fun701.call(args699,kw700)?}.attr("rotate")?;let mut args696=Vec::new();let mut kw697=Vec::new();args696.push({let mut s=Vec::new();s.push(Val::Int(0i64));s.push(Val::Int(0i64));s.push(Val::Int(0i64));Val::tuple(s)});args696.push({let mut s=Vec::new();s.push(Val::Int(1i64));s.push(Val::Int(0i64));s.push(Val::Int(0i64));Val::tuple(s)});args696.push(e.get("tilt")?);fun698.call(args696,kw697)?}.attr("translate")?;let mut args693=Vec::new();let mut kw694=Vec::new();args693.push(e.get("at")?);fun695.call(args693,kw694)?};e.set("phone",assigned692.clone())?;
let assigned702={let fun705=e.get("visible_lines")?;let mut args703=Vec::new();let mut kw704=Vec::new();args703.push({let d=Val::dict(vec![]);d.set(Val::Str("phone".into()),e.get("phone")?)?;d});fun705.call(args703,kw704)?}.get(Val::Str("phone".into()))?;e.set("phone_lines",assigned702.clone())?;
let assigned706={let fun709=e.get("Pen")?;let mut args707=Vec::new();let mut kw708=Vec::new();args707.push(binary("add",{let fun712=e.get("max")?;let mut args710=Vec::new();let mut kw711=Vec::new();args710.push({let e=e.child();let out713=Val::list(vec![]);for item714 in e.get("phone_lines")?.get(Val::Str("outline".into()))?.iter()? {e.set("line",item714)?;for item715 in e.get("line")?.iter()? {let unpack716=unpack(item715,2)?;e.set("_",unpack716[0].clone())?;e.set("y",unpack716[1].clone())?;out713.attr("append")?.call(vec![e.get("y")?],vec![])?;}}out713});fun712.call(args710,kw711)?},Val::Float(0.65f64))?);fun709.call(args707,kw708)?};e.set("pen",assigned706.clone())?;
let assigned717={let fun720=e.get("silhouette")?;let mut args718=Vec::new();let mut kw719=Vec::new();args718.push({let e=e.child();let out721=Val::list(vec![]);for item722 in {let mut s=Vec::new();s.push(Val::Str("tip".into()));s.push(Val::Str("cover".into()));s.push(Val::Str("display".into()));Val::tuple(s)}.iter()? {e.set("n",item722)?;out721.attr("append")?.call(vec![e.get("head")?.get(e.get("n")?)?],vec![])?;}out721});fun720.call(args718,kw719)?};e.set("head_outline",assigned717.clone())?;
let assigned723={let fun726=e.get("silhouette")?;let mut args724=Vec::new();let mut kw725=Vec::new();args724.push({let mut s=Vec::new();s.push(e.get("phone")?);Val::list(s)});fun726.call(args724,kw725)?};e.set("phone_outline",assigned723.clone())?;
let assigned727={let fun730=e.get("pen")?.attr("curve")?;let mut args728=Vec::new();let mut kw729=Vec::new();args728.push(e.get("phone_outline")?);args728.push(Val::Bool(true));fun730.call(args728,kw729)?};e.set("phone_path",assigned727.clone())?;
let assigned731={let fun734={let fun737=e.get("Polygon")?;let mut args735=Vec::new();let mut kw736=Vec::new();args735.push(e.get("phone_outline")?);fun737.call(args735,kw736)?}.attr("buffer")?;let mut args732=Vec::new();let mut kw733=Vec::new();args732.push(Val::Float(0.1f64));kw733.push(("join_style".into(),Val::Str("round".into())));fun734.call(args732,kw733)?};e.get("pen")?.setattr("occluder",assigned731.clone())?;
let assigned738={let fun741=e.get("pen")?.attr("region")?;let mut args739=Vec::new();let mut kw740=Vec::new();args739.push({let fun744={let fun747=e.get("Polygon")?;let mut args745=Vec::new();let mut kw746=Vec::new();args745.push(e.get("head_outline")?);fun747.call(args745,kw746)?}.attr("difference")?;let mut args742=Vec::new();let mut kw743=Vec::new();args742.push(e.get("pen")?.attr("occluder")?);fun744.call(args742,kw743)?});fun741.call(args739,kw740)?};e.set("head_fill",assigned738.clone())?;
let assigned748={let fun751=e.get("fa")?.attr("faucet_shell")?.attr("_tip_frame")?;let mut args749=Vec::new();let mut kw750=Vec::new();fun751.call(args749,kw750)?};let unpack752=unpack(assigned748.clone(),3)?;e.set("_",unpack752[0].clone())?;e.set("up_gooseneck",unpack752[1].clone())?;e.set("tip_normal",unpack752[2].clone())?;
let assigned753={let fun756=e.get("up_gooseneck")?.attr("multiply")?;let mut args754=Vec::new();let mut kw755=Vec::new();args754.push(unary("neg",Val::Int(1i64))?);fun756.call(args754,kw755)?};e.set("end_normal",assigned753.clone())?;
let assigned757={let fun760=e.get("front_face")?;let mut args758=Vec::new();let mut kw759=Vec::new();args758.push(e.get("head")?.get(Val::Str("cover".into()))?);args758.push(e.get("tip_normal")?);fun760.call(args758,kw759)?};e.set("bezel",assigned757.clone())?;
let assigned761={let fun764=e.get("front_face")?;let mut args762=Vec::new();let mut kw763=Vec::new();args762.push(e.get("head")?.get(Val::Str("screen".into()))?);args762.push(e.get("tip_normal")?);fun764.call(args762,kw763)?};e.set("glass",assigned761.clone())?;
let assigned765={let fun768=e.get("front_face")?;let mut args766=Vec::new();let mut kw767=Vec::new();args766.push(e.get("head")?.get(Val::Str("tip".into()))?);args766.push(e.get("end_normal")?);fun768.call(args766,kw767)?};e.set("cap",assigned765.clone())?;
let assigned769={let fun772=e.get("projected")?;let mut args770=Vec::new();let mut kw771=Vec::new();args770.push({let fun775={let fun778=e.get("cap")?.attr("outerWire")?;let mut args776=Vec::new();let mut kw777=Vec::new();fun778.call(args776,kw777)?}.attr("Center")?;let mut args773=Vec::new();let mut kw774=Vec::new();fun775.call(args773,kw774)?});fun772.call(args770,kw771)?};e.set("cap_centre",assigned769.clone())?;
let assigned779={let e=e.child();let out780=Val::list(vec![]);for item781 in {let fun784=e.get("wire_lines")?;let mut args782=Vec::new();let mut kw783=Vec::new();args782.push({let fun787=e.get("cap")?.attr("outerWire")?;let mut args785=Vec::new();let mut kw786=Vec::new();fun787.call(args785,kw786)?});fun784.call(args782,kw783)?}.iter()? {e.set("line",item781)?;for item788 in {let fun791=e.get("clip")?;let mut args789=Vec::new();let mut kw790=Vec::new();args789.push(e.get("line")?);args789.push({let params=vec![("p".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok(binary("sub",e.get("p")?.get(Val::Int(1i64))?,e.get("cap_centre")?.get(Val::Int(1i64))?)?);
Ok(Val::None)})});fun791.call(args789,kw790)?}.iter()? {e.set("piece",item788)?;out780.attr("append")?.call(vec![e.get("piece")?],vec![])?;}}out780};e.set("cap_back",assigned779.clone())?;
let assigned792={let e=e.child();let out793=Val::dict(vec![]);for item794 in {let mut s=Vec::new();s.push(Val::Str("soda".into()));s.push(Val::Str("flavor_left".into()));s.push(Val::Str("flavor_right".into()));Val::tuple(s)}.iter()? {e.set("name",item794)?;out793.set(e.get("name")?,{let fun797=e.get("front_face")?;let mut args795=Vec::new();let mut kw796=Vec::new();args795.push(e.get("head")?.get(e.get("name")?)?);args795.push(e.get("end_normal")?);fun797.call(args795,kw796)?})?;}out793};e.set("mouths",assigned792.clone())?;
let assigned798={let fun801=e.get("visible_lines")?;let mut args799=Vec::new();let mut kw800=Vec::new();args799.push(e.get("head")?);fun801.call(args799,kw800)?};e.set("faucet_lines",assigned798.clone())?;
let assigned802={let mut s=Vec::new();Val::list(s)};e.set("walls",assigned802.clone())?;
for item803 in {let fun848=e.get("mouths")?.attr("items")?;let mut args846=Vec::new();let mut kw847=Vec::new();fun848.call(args846,kw847)?}.iter()? {
let unpack849=unpack(item803,2)?;e.set("name",unpack849[0].clone())?;e.set("mouth",unpack849[1].clone())?;let assigned804={let fun807=e.get("projected")?;let mut args805=Vec::new();let mut kw806=Vec::new();args805.push({let fun810=e.get("mouth")?.attr("Center")?;let mut args808=Vec::new();let mut kw809=Vec::new();fun810.call(args808,kw809)?});fun807.call(args805,kw806)?};let unpack811=unpack(assigned804.clone(),2)?;e.set("cx",unpack811[0].clone())?;e.set("_",unpack811[1].clone())?;
for item812 in binary("add",e.get("faucet_lines")?.get(e.get("name")?)?.get(Val::Str("sharp".into()))?,e.get("faucet_lines")?.get(e.get("name")?)?.get(Val::Str("outline".into()))?)?.iter()? {
e.set("line",item812)?;let assigned813={let fun816=e.get("sum")?;let mut args814=Vec::new();let mut kw815=Vec::new();args814.push({let e=e.child();let out817=Val::list(vec![]);for item818 in {let fun821=e.get("zip")?;let mut args819=Vec::new();let mut kw820=Vec::new();args819.push(e.get("line")?);args819.push(e.get("line")?.get(Val::Slice{start:Some(Val::Int(1i64).integer()?),stop:None,step:1})?);fun821.call(args819,kw820)?}.iter()? {let unpack822=unpack(item818,2)?;e.set("a",unpack822[0].clone())?;e.set("b",unpack822[1].clone())?;out817.attr("append")?.call(vec![{let fun825=e.get("math")?.attr("dist")?;let mut args823=Vec::new();let mut kw824=Vec::new();args823.push(e.get("a")?);args823.push(e.get("b")?);fun825.call(args823,kw824)?}],vec![])?;}out817});fun816.call(args814,kw815)?};e.set("length",assigned813.clone())?;
if unary("not",{let v826=Val::Float(0.05f64);let v827=e.get("length")?;let v828=Val::Int(2i64);Val::Bool(compare("lt",v826.clone(),v827.clone())?.truthy()? && compare("lt",v827.clone(),v828.clone())?.truthy()?)})?.truthy()? {
continue;
}
if {let v840={let v841=e.get("name")?;let v842=Val::Str("soda".into());Val::Bool(compare("ne",v841.clone(),v842.clone())?.truthy()?)};if v840.truthy()? {{let v838=binary("mul",binary("sub",binary("truediv",{let fun831=e.get("sum")?;let mut args829=Vec::new();let mut kw830=Vec::new();args829.push({let e=e.child();let out832=Val::list(vec![]);for item833 in e.get("line")?.iter()? {let unpack834=unpack(item833,2)?;e.set("x",unpack834[0].clone())?;e.set("_",unpack834[1].clone())?;out832.attr("append")?.call(vec![e.get("x")?],vec![])?;}out832});fun831.call(args829,kw830)?},{let fun837=e.get("len")?;let mut args835=Vec::new();let mut kw836=Vec::new();args835.push(e.get("line")?);fun837.call(args835,kw836)?})?,e.get("cx")?)?,e.get("cx")?)?;let v839=Val::Int(0i64);Val::Bool(compare("le",v838.clone(),v839.clone())?.truthy()?)}} else {v840}}.truthy()? {
continue;
}
{let fun845=e.get("walls")?.attr("append")?;let mut args843=Vec::new();let mut kw844=Vec::new();args843.push(e.get("line")?);fun845.call(args843,kw844)?};
}
}
// phone_point
e.set("phone_point",{let params=vec![("x".into(),None,false),("y".into(),None,false),("z".into(),Some(e.get("t")?),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let fun852=e.get("pen")?.attr("page")?;let mut args850=Vec::new();let mut kw851=Vec::new();args850.push({let fun855=e.get("projected")?;let mut args853=Vec::new();let mut kw854=Vec::new();args853.push({let fun858=e.get("placed")?;let mut args856=Vec::new();let mut kw857=Vec::new();args856.push({let mut s=Vec::new();s.push(e.get("x")?);s.push(e.get("y")?);s.push(e.get("z")?);Val::tuple(s)});args856.push(e.get("at")?);fun858.call(args856,kw857)?});fun855.call(args853,kw854)?});fun852.call(args850,kw851)?});
Ok(Val::None)})})?;
let assigned859={let mut s=Vec::new();s.push({let fun862=e.get("phone_point")?;let mut args860=Vec::new();let mut kw861=Vec::new();args860.push(Val::Int(0i64));args860.push(binary("truediv",e.get("h")?,Val::Int(2i64))?);fun862.call(args860,kw861)?});s.push({let fun865=e.get("phone_point")?;let mut args863=Vec::new();let mut kw864=Vec::new();args863.push(Val::Int(0i64));args863.push(binary("truediv",unary("neg",e.get("h")?)?,Val::Int(2i64))?);fun865.call(args863,kw864)?});Val::tuple(s)};let unpack866=unpack(assigned859.clone(),2)?;e.set("top",unpack866[0].clone())?;e.set("bottom",unpack866[1].clone())?;
let assigned867={let fun870=e.get("phone_point")?;let mut args868=Vec::new();let mut kw869=Vec::new();args868.push(Val::Int(0i64));args868.push(Val::Int(0i64));args868.push(binary("add",e.get("t")?,Val::Float(0.025f64))?);fun870.call(args868,kw869)?};e.set("origin",assigned867.clone())?;
let assigned871={let mut s=Vec::new();s.push({let fun874=e.get("phone_point")?;let mut args872=Vec::new();let mut kw873=Vec::new();args872.push(Val::Int(1i64));args872.push(Val::Int(0i64));args872.push(binary("add",e.get("t")?,Val::Float(0.025f64))?);fun874.call(args872,kw873)?});s.push({let fun877=e.get("phone_point")?;let mut args875=Vec::new();let mut kw876=Vec::new();args875.push(Val::Int(0i64));args875.push(Val::Int(1i64));args875.push(binary("add",e.get("t")?,Val::Float(0.025f64))?);fun877.call(args875,kw876)?});Val::tuple(s)};let unpack878=unpack(assigned871.clone(),2)?;e.set("axis_x",unpack878[0].clone())?;e.set("axis_y",unpack878[1].clone())?;
let assigned879={let fun882=Val::Str(",".into()).attr("join")?;let mut args880=Vec::new();let mut kw881=Vec::new();args880.push({let e=e.child();let out883=Val::list(vec![]);for item884 in {let mut s=Vec::new();s.push(binary("sub",e.get("axis_x")?.get(Val::Int(0i64))?,e.get("origin")?.get(Val::Int(0i64))?)?);s.push(binary("sub",e.get("axis_x")?.get(Val::Int(1i64))?,e.get("origin")?.get(Val::Int(1i64))?)?);s.push(binary("sub",e.get("axis_y")?.get(Val::Int(0i64))?,e.get("origin")?.get(Val::Int(0i64))?)?);s.push(binary("sub",e.get("axis_y")?.get(Val::Int(1i64))?,e.get("origin")?.get(Val::Int(1i64))?)?);s.extend(e.get("origin")?.iter()?);Val::tuple(s)}.iter()? {e.set("v",item884)?;out883.attr("append")?.call(vec![{let mut str885=String::new();str885.push_str(&format(&e.get("v")?,&val_string({let mut str886=String::new();str886.push_str(".8f");Val::Str(str886)})?)?);Val::Str(str885)}],vec![])?;}out883});fun882.call(args880,kw881)?};e.set("matrix",assigned879.clone())?;
let assigned887={let params=vec![("f".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let mut s=Vec::new();s.push(binary("add",e.get("top")?.get(Val::Int(0i64))?,binary("mul",binary("sub",e.get("bottom")?.get(Val::Int(0i64))?,e.get("top")?.get(Val::Int(0i64))?)?,e.get("f")?)?)?);s.push(binary("add",e.get("top")?.get(Val::Int(1i64))?,binary("mul",binary("sub",e.get("bottom")?.get(Val::Int(1i64))?,e.get("top")?.get(Val::Int(1i64))?)?,e.get("f")?)?)?);Val::tuple(s)});
Ok(Val::None)})};e.set("along",assigned887.clone())?;
let assigned888={let e=e.child();let out889=Val::list(vec![]);for item890 in e.get("PHONE_FADE")?.iter()? {e.set("f",item890)?;out889.attr("append")?.call(vec![{let fun893=e.get("along")?;let mut args891=Vec::new();let mut kw892=Vec::new();args891.push(e.get("f")?);fun893.call(args891,kw892)?}],vec![])?;}out889};let unpack894=unpack(assigned888.clone(),2)?;e.set("hand0",unpack894[0].clone())?;e.set("hand1",unpack894[1].clone())?;
let assigned895={let mut str896=String::new();str896.push_str("maskUnits=\"userSpaceOnUse\" maskContentUnits=\"userSpaceOnUse\" x=\"0\" y=\"0\" width=\"");str896.push_str(&format(&e.get("WIDTH")?,&String::new())?);str896.push_str("\" height=\"");str896.push_str(&format(&e.get("HEIGHT")?,&String::new())?);str896.push_str("\" mask-type=\"luminance\"");Val::Str(str896)};e.set("mask_bounds",assigned895.clone())?;
return Ok({let fun899=Val::Str("\n".into()).attr("join")?;let mut args897=Vec::new();let mut kw898=Vec::new();args897.push({let mut s=Vec::new();s.push({let mut str900=String::new();str900.push_str("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"");str900.push_str(&format(&e.get("WIDTH")?,&String::new())?);str900.push_str("\" height=\"");str900.push_str(&format(&e.get("HEIGHT")?,&String::new())?);str900.push_str("\" viewBox=\"0 0 ");str900.push_str(&format(&e.get("WIDTH")?,&String::new())?);str900.push_str(" ");str900.push_str(&format(&e.get("HEIGHT")?,&String::new())?);str900.push_str("\" fill=\"none\">");Val::Str(str900)});s.push(Val::Str("<title>Hold an iPhone to the faucet display</title>".into()));s.push(Val::Str("<desc>A measured front view of the faucet, its tapered display bezel and three separate outlets. The phone is angled toward the display.</desc>".into()));s.push(Val::Str("<defs>".into()));s.push(Val::Str("<linearGradient id=\"stem-ink\" gradientUnits=\"userSpaceOnUse\" x1=\"0\" y1=\"1.4\" x2=\"0\" y2=\"8\"><stop stop-color=\"white\" stop-opacity=\"0\"/><stop offset=\"1\" stop-color=\"white\"/></linearGradient>".into()));s.push({let mut str901=String::new();str901.push_str("<mask id=\"stem-exit\" ");str901.push_str(&format(&e.get("mask_bounds")?,&String::new())?);str901.push_str("><rect width=\"160\" height=\"160\" fill=\"url(#stem-ink)\"/></mask>");Val::Str(str901)});s.push({let mut str902=String::new();str902.push_str("<linearGradient id=\"phone-ink\" gradientUnits=\"userSpaceOnUse\" x1=\"");str902.push_str(&format(&e.get("hand0")?.get(Val::Int(0i64))?,&String::new())?);str902.push_str("\" y1=\"");str902.push_str(&format(&e.get("hand0")?.get(Val::Int(1i64))?,&String::new())?);str902.push_str("\" x2=\"");str902.push_str(&format(&e.get("hand1")?.get(Val::Int(0i64))?,&String::new())?);str902.push_str("\" y2=\"");str902.push_str(&format(&e.get("hand1")?.get(Val::Int(1i64))?,&String::new())?);str902.push_str("\"><stop stop-color=\"white\"/><stop offset=\"1\" stop-color=\"white\" stop-opacity=\"0\"/></linearGradient>");Val::Str(str902)});s.push({let mut str903=String::new();str903.push_str("<mask id=\"phone-exit\" ");str903.push_str(&format(&e.get("mask_bounds")?,&String::new())?);str903.push_str("><rect width=\"170\" height=\"180\" fill=\"url(#phone-ink)\"/></mask>");Val::Str(str903)});s.push(Val::Str("</defs>".into()));s.push(Val::Str("<g stroke-linecap=\"round\" stroke-linejoin=\"round\">".into()));s.push(Val::Str("<g mask=\"url(#stem-exit)\">".into()));s.push({let mut str904=String::new();str904.push_str("<path d=\"");str904.push_str(&format(&e.get("head_fill")?,&String::new())?);str904.push_str("\" fill=\"currentColor\" fill-rule=\"evenodd\" fill-opacity=\".025\"/>");Val::Str(str904)});s.push({let fun907=e.get("pen")?.attr("group")?;let mut args905=Vec::new();let mut kw906=Vec::new();args905.push({let mut s=Vec::new();s.push(e.get("head_outline")?);Val::list(s)});args905.push(Val::Float(0.64f64));kw906.push(("simplify".into(),Val::Int(0i64)));fun907.call(args905,kw906)?});s.push({let fun910=e.get("pen")?.attr("group")?;let mut args908=Vec::new();let mut kw909=Vec::new();args908.push({let fun913=e.get("wire_lines")?;let mut args911=Vec::new();let mut kw912=Vec::new();args911.push({let fun916=e.get("bezel")?.attr("outerWire")?;let mut args914=Vec::new();let mut kw915=Vec::new();fun916.call(args914,kw915)?});fun913.call(args911,kw912)?});args908.push(Val::Float(0.46f64));args908.push(Val::Float(0.95f64));fun910.call(args908,kw909)?});s.push({let fun919=e.get("pen")?.attr("group")?;let mut args917=Vec::new();let mut kw918=Vec::new();args917.push({let e=e.child();let out920=Val::list(vec![]);for item921 in {let fun924=e.get("bezel")?.attr("innerWires")?;let mut args922=Vec::new();let mut kw923=Vec::new();fun924.call(args922,kw923)?}.iter()? {e.set("wire",item921)?;for item925 in {let fun928=e.get("wire_lines")?;let mut args926=Vec::new();let mut kw927=Vec::new();args926.push(e.get("wire")?);fun928.call(args926,kw927)?}.iter()? {e.set("line",item925)?;out920.attr("append")?.call(vec![e.get("line")?],vec![])?;}}out920});args917.push(Val::Float(0.3f64));args917.push(Val::Float(0.65f64));fun919.call(args917,kw918)?});s.push({let fun931=e.get("pen")?.attr("group")?;let mut args929=Vec::new();let mut kw930=Vec::new();args929.push({let fun934=e.get("wire_lines")?;let mut args932=Vec::new();let mut kw933=Vec::new();args932.push({let fun937=e.get("glass")?.attr("outerWire")?;let mut args935=Vec::new();let mut kw936=Vec::new();fun937.call(args935,kw936)?});fun934.call(args932,kw933)?});args929.push(Val::Float(0.38f64));args929.push(Val::Float(0.9f64));fun931.call(args929,kw930)?});s.push({let fun940=e.get("pen")?.attr("group")?;let mut args938=Vec::new();let mut kw939=Vec::new();args938.push(e.get("cap_back")?);args938.push(Val::Float(0.32f64));args938.push(Val::Float(0.72f64));fun940.call(args938,kw939)?});s.push({let fun943=e.get("pen")?.attr("group")?;let mut args941=Vec::new();let mut kw942=Vec::new();args941.push({let fun946=e.get("wire_lines")?;let mut args944=Vec::new();let mut kw945=Vec::new();args944.push({let fun949=e.get("mouths")?.get(Val::Str("soda".into()))?.attr("outerWire")?;let mut args947=Vec::new();let mut kw948=Vec::new();fun949.call(args947,kw948)?});fun946.call(args944,kw945)?});args941.push(Val::Float(0.4f64));args941.push(Val::Float(0.95f64));fun943.call(args941,kw942)?});s.push({let fun952=e.get("pen")?.attr("group")?;let mut args950=Vec::new();let mut kw951=Vec::new();args950.push({let e=e.child();let out953=Val::list(vec![]);for item954 in {let mut s=Vec::new();s.push(Val::Str("flavor_left".into()));s.push(Val::Str("flavor_right".into()));Val::tuple(s)}.iter()? {e.set("name",item954)?;for item955 in {let fun958=e.get("wire_lines")?;let mut args956=Vec::new();let mut kw957=Vec::new();args956.push({let fun961=e.get("mouths")?.get(e.get("name")?)?.attr("outerWire")?;let mut args959=Vec::new();let mut kw960=Vec::new();fun961.call(args959,kw960)?});fun958.call(args956,kw957)?}.iter()? {e.set("line",item955)?;out953.attr("append")?.call(vec![e.get("line")?],vec![])?;}}out953});args950.push(Val::Float(0.3f64));args950.push(Val::Float(0.95f64));fun952.call(args950,kw951)?});s.push({let fun964=e.get("pen")?.attr("group")?;let mut args962=Vec::new();let mut kw963=Vec::new();args962.push(e.get("walls")?);args962.push(Val::Float(0.24f64));args962.push(Val::Float(0.65f64));fun964.call(args962,kw963)?});s.push(Val::Str("</g>".into()));s.push(Val::Str("<g mask=\"url(#phone-exit)\">".into()));s.push({let mut str965=String::new();str965.push_str("<path d=\"");str965.push_str(&format(&e.get("phone_path")?,&String::new())?);str965.push_str("\" fill=\"currentColor\" fill-opacity=\".018\" stroke=\"currentColor\" stroke-width=\".60\"/>");Val::Str(str965)});s.push({let mut str966=String::new();str966.push_str("<rect x=\"-34.05\" y=\"-72.05\" width=\"68.1\" height=\"144.1\" rx=\"8.75\" transform=\"matrix(");str966.push_str(&format(&e.get("matrix")?,&String::new())?);str966.push_str(")\" stroke=\"currentColor\" stroke-width=\".27\" opacity=\".65\"/>");Val::Str(str966)});s.push({let mut str967=String::new();str967.push_str("<rect x=\"-9.75\" y=\"59.3\" width=\"19.5\" height=\"5.8\" rx=\"2.85\" transform=\"matrix(");str967.push_str(&format(&e.get("matrix")?,&String::new())?);str967.push_str(")\" stroke=\"currentColor\" stroke-width=\".38\" opacity=\".95\"/>");Val::Str(str967)});s.push(Val::Str("</g></g></svg>".into()));s.push(Val::Str("".into()));Val::list(s)});fun899.call(args897,kw898)?});
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    let assigned968 = if {
        let v972 = {
            let fun971 = e.get("len")?;
            let mut args969 = Vec::new();
            let mut kw970 = Vec::new();
            args969.push(e.get("sys")?.attr("argv")?);
            fun971.call(args969, kw970)?
        };
        let v973 = Val::Int(1i64);
        Val::Bool(compare("gt", v972.clone(), v973.clone())?.truthy()?)
    }
    .truthy()?
    {
        {
            let fun976 = e.get("Path")?;
            let mut args974 = Vec::new();
            let mut kw975 = Vec::new();
            args974.push(e.get("sys")?.attr("argv")?.get(Val::Int(1i64))?);
            fun976.call(args974, kw975)?
        }
    } else {
        e.get("ASSET")?
    };
    e.set("out", assigned968.clone())?;
    {
        let fun979 = e.get("out")?.attr("write_text")?;
        let mut args977 = Vec::new();
        let mut kw978 = Vec::new();
        args977.push({
            let fun982 = e.get("drawing")?;
            let mut args980 = Vec::new();
            let mut kw981 = Vec::new();
            fun982.call(args980, kw981)?
        });
        fun979.call(args977, kw978)?
    };
    {
        let fun985 = e.get("print")?;
        let mut args983 = Vec::new();
        let mut kw984 = Vec::new();
        args983.push(e.get("out")?);
        fun985.call(args983, kw984)?
    };
    Ok(Val::None)
}
