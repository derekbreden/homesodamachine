//! The machine display plane and the tangent curves surrounding it.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
    e.set("dims", rt.import_module("_enclosure_interface")?)?;
    let mod1 = rt.import_module("_enclosure_data")?;
    e.set("_read", rt.member("_enclosure_data", "read")?)?;
    let mod2 = rt.import_module("_enclosure_core_data")?;
    e.set("_tupled", rt.member("_enclosure_core_data", "tupled")?)?;
    let assigned3 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
            line!(),
        );
        {
            let fun6 = e.get("_read")?;
            let mut args4 = Vec::new();
            let mut kw5 = Vec::new();
            args4.push(Val::Str("swept-defaults".into()));
            kw5.push(("dimensions".into(), {
                let e = e.child();
                let out7 = Val::dict(vec![]);
                for item8 in {
                    let mut s = Vec::new();
                    s.push(Val::Str("show_corner_r".into()));
                    s.push(Val::Str("show_edge_r".into()));
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("name", item8)?;
                    out7.set(e.get("name")?, {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
                            line!(),
                        );
                        {
                            let fun11 = e.get("getattr")?;
                            let mut args9 = Vec::new();
                            let mut kw10 = Vec::new();
                            args9.push(e.get("dims")?);
                            args9.push(e.get("name")?);
                            fun11.call(args9, kw10)?
                        }
                    })?;
                }
                out7
            }));
            fun6.call(args4, kw5)?
        }
    };
    e.set("_values", assigned3.clone())?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
            line!(),
        );
        {
            let fun14 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
                    line!(),
                );
                {
                    let fun17 = e.get("globals")?;
                    let mut args15 = Vec::new();
                    let mut kw16 = Vec::new();
                    fun17.call(args15, kw16)?
                }
            }
            .attr("update")?;
            let mut args12 = Vec::new();
            let mut kw13 = Vec::new();
            args12.push(e.get("_values")?);
            fun14.call(args12, kw13)?
        }
    };
    // _parameters
    e.set("_parameters", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let e = e.child();
                let out18 = Val::dict(vec![]);
                for item19 in e.get("_values")?.iter()? {
                    e.set("name", item19)?;
                    out18.set(
                        e.get("name")?,
                        {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
                                line!(),
                            );
                            {
                                let fun22 = e.get("globals")?;
                                let mut args20 = Vec::new();
                                let mut kw21 = Vec::new();
                                fun22.call(args20, kw21)?
                            }
                        }
                        .get(e.get("name")?)?,
                    )?;
                }
                out18
            });
            Ok(Val::None)
        })
    })?;
    // profile
    e.set("profile", {
        let params = vec![("outer".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
                    line!(),
                );
                {
                    let fun25 = e.get("_tupled")?;
                    let mut args23 = Vec::new();
                    let mut kw24 = Vec::new();
                    args23.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
                            line!(),
                        );
                        {
                            let fun28 = e.get("_read")?;
                            let mut args26 = Vec::new();
                            let mut kw27 = Vec::new();
                            args26.push(Val::Str("swept-profile".into()));
                            kw27.push(("outer".into(), e.get("outer")?));
                            kw27.push(("parameters".into(), {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
                                    line!(),
                                );
                                {
                                    let fun31 = e.get("_parameters")?;
                                    let mut args29 = Vec::new();
                                    let mut kw30 = Vec::new();
                                    fun31.call(args29, kw30)?
                                }
                            }));
                            fun28.call(args26, kw27)?
                        }
                    });
                    fun25.call(args23, kw24)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // roof_fill_sections
    e.set("roof_fill_sections", {
        let params = vec![("outer".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod32 = rt.import_module("overhang_round")?;
            e.set(
                "OUTWARD_PER_HEIGHT",
                rt.member("overhang_round", "OUTWARD_PER_HEIGHT")?,
            )?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
                    line!(),
                );
                {
                    let fun35 = e.get("_tupled")?;
                    let mut args33 = Vec::new();
                    let mut kw34 = Vec::new();
                    args33.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
                            line!(),
                        );
                        {
                            let fun38 = e.get("_read")?;
                            let mut args36 = Vec::new();
                            let mut kw37 = Vec::new();
                            args36.push(Val::Str("swept-roof-fill".into()));
                            kw37.push(("outer".into(), e.get("outer")?));
                            kw37.push(("parameters".into(), {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
                                    line!(),
                                );
                                {
                                    let fun41 = e.get("_parameters")?;
                                    let mut args39 = Vec::new();
                                    let mut kw40 = Vec::new();
                                    fun41.call(args39, kw40)?
                                }
                            }));
                            kw37.push(("outward_per_height".into(), e.get("OUTWARD_PER_HEIGHT")?));
                            fun38.call(args36, kw37)?
                        }
                    });
                    fun35.call(args33, kw34)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // _roof_fill
    e.set("_roof_fill",{let params=vec![("outer".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let mod42=rt.import_module("OCP.BRepOffsetAPI")?;e.set("BRepOffsetAPI_ThruSections",rt.member("OCP.BRepOffsetAPI","BRepOffsetAPI_ThruSections")?)?;
let assigned43={let mut s=Vec::new();Val::list(s)};e.set("fills",assigned43.clone())?;
for item44 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun47=e.get("roof_fill_sections")?;let mut args45=Vec::new();let mut kw46=Vec::new();args45.push(e.get("outer")?);fun47.call(args45,kw46)?}}.iter()? {
e.set("sections",item44)?;let assigned48={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun51=e.get("BRepOffsetAPI_ThruSections")?;let mut args49=Vec::new();let mut kw50=Vec::new();args49.push(Val::Bool(true));args49.push(Val::Bool(true));args49.push(Val::Float(1e-06f64));fun51.call(args49,kw50)?}};e.set("loft",assigned48.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun54=e.get("loft")?.attr("CheckCompatibility")?;let mut args52=Vec::new();let mut kw53=Vec::new();args52.push(Val::Bool(false));fun54.call(args52,kw53)?}};
for item55 in e.get("sections")?.iter()? {
e.set("section",item55)?;let assigned56=e.get("section")?.get(Val::Str("x".into()))?;e.set("x",assigned56.clone())?;
let assigned57=e.get("section")?.get(Val::Str("centre".into()))?;let unpack58=unpack(assigned57.clone(),2)?;e.set("cy",unpack58[0].clone())?;e.set("cz",unpack58[1].clone())?;
let assigned59=e.get("section")?.get(Val::Str("ellipse".into()))?;let unpack60=unpack(assigned59.clone(),3)?;e.set("b",unpack60[0].clone())?;e.set("a",unpack60[1].clone())?;e.set("theta",unpack60[2].clone())?;
// v
e.set("v",{let params=vec![("point".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun63=e.get("cq")?.attr("Vector")?;let mut args61=Vec::new();let mut kw62=Vec::new();args61.push(e.get("x")?);args61.extend(e.get("point")?.iter()?);fun63.call(args61,kw62)?}});
Ok(Val::None)})})?;
let assigned64={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun67=e.get("cq")?.attr("Wire")?.attr("assembleEdges")?;let mut args65=Vec::new();let mut kw66=Vec::new();args65.push({let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun70=e.get("cq")?.attr("Edge")?.attr("makeLine")?;let mut args68=Vec::new();let mut kw69=Vec::new();args68.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun73=e.get("v")?;let mut args71=Vec::new();let mut kw72=Vec::new();args71.push(e.get("section")?.get(Val::Str("start".into()))?);fun73.call(args71,kw72)?}});args68.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun76=e.get("v")?;let mut args74=Vec::new();let mut kw75=Vec::new();args74.push(e.get("section")?.get(Val::Str("top_tangent".into()))?);fun76.call(args74,kw75)?}});fun70.call(args68,kw69)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun79=e.get("cq")?.attr("Edge")?.attr("makeEllipse")?;let mut args77=Vec::new();let mut kw78=Vec::new();args77.push(e.get("b")?);args77.push(e.get("a")?);args77.push({let mut s=Vec::new();s.push(e.get("x")?);s.push(e.get("cy")?);s.push(e.get("cz")?);Val::tuple(s)});args77.push({let mut s=Vec::new();s.push(Val::Int(1i64));s.push(Val::Int(0i64));s.push(Val::Int(0i64));Val::tuple(s)});args77.push({let mut s=Vec::new();s.push(Val::Int(0i64));s.push(Val::Int(0i64));s.push(Val::Int(1i64));Val::tuple(s)});args77.push(Val::Int(0i64));args77.push(e.get("theta")?);fun79.call(args77,kw78)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun82=e.get("cq")?.attr("Edge")?.attr("makeLine")?;let mut args80=Vec::new();let mut kw81=Vec::new();args80.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun85=e.get("v")?;let mut args83=Vec::new();let mut kw84=Vec::new();args83.push(e.get("section")?.get(Val::Str("upper_roof".into()))?);fun85.call(args83,kw84)?}});args80.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun88=e.get("v")?;let mut args86=Vec::new();let mut kw87=Vec::new();args86.push(e.get("section")?.get(Val::Str("upper_aft".into()))?);fun88.call(args86,kw87)?}});fun82.call(args80,kw81)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun91=e.get("cq")?.attr("Edge")?.attr("makeLine")?;let mut args89=Vec::new();let mut kw90=Vec::new();args89.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun94=e.get("v")?;let mut args92=Vec::new();let mut kw93=Vec::new();args92.push(e.get("section")?.get(Val::Str("upper_aft".into()))?);fun94.call(args92,kw93)?}});args89.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun97=e.get("v")?;let mut args95=Vec::new();let mut kw96=Vec::new();args95.push(e.get("section")?.get(Val::Str("lower_aft".into()))?);fun97.call(args95,kw96)?}});fun91.call(args89,kw90)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun100=e.get("cq")?.attr("Edge")?.attr("makeLine")?;let mut args98=Vec::new();let mut kw99=Vec::new();args98.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun103=e.get("v")?;let mut args101=Vec::new();let mut kw102=Vec::new();args101.push(e.get("section")?.get(Val::Str("lower_aft".into()))?);fun103.call(args101,kw102)?}});args98.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun106=e.get("v")?;let mut args104=Vec::new();let mut kw105=Vec::new();args104.push(e.get("section")?.get(Val::Str("lower_roof".into()))?);fun106.call(args104,kw105)?}});fun100.call(args98,kw99)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun109=e.get("cq")?.attr("Edge")?.attr("makeThreePointArc")?;let mut args107=Vec::new();let mut kw108=Vec::new();args107.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun112=e.get("v")?;let mut args110=Vec::new();let mut kw111=Vec::new();args110.push(e.get("section")?.get(Val::Str("lower_roof".into()))?);fun112.call(args110,kw111)?}});args107.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun115=e.get("v")?;let mut args113=Vec::new();let mut kw114=Vec::new();args113.push(e.get("section")?.get(Val::Str("inner_mid".into()))?);fun115.call(args113,kw114)?}});args107.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun118=e.get("v")?;let mut args116=Vec::new();let mut kw117=Vec::new();args116.push(e.get("section")?.get(Val::Str("inner_end".into()))?);fun118.call(args116,kw117)?}});fun109.call(args107,kw108)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun121=e.get("cq")?.attr("Edge")?.attr("makeLine")?;let mut args119=Vec::new();let mut kw120=Vec::new();args119.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun124=e.get("v")?;let mut args122=Vec::new();let mut kw123=Vec::new();args122.push(e.get("section")?.get(Val::Str("inner_end".into()))?);fun124.call(args122,kw123)?}});args119.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun127=e.get("v")?;let mut args125=Vec::new();let mut kw126=Vec::new();args125.push(e.get("section")?.get(Val::Str("inner_start".into()))?);fun127.call(args125,kw126)?}});fun121.call(args119,kw120)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun130=e.get("cq")?.attr("Edge")?.attr("makeLine")?;let mut args128=Vec::new();let mut kw129=Vec::new();args128.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun133=e.get("v")?;let mut args131=Vec::new();let mut kw132=Vec::new();args131.push(e.get("section")?.get(Val::Str("inner_start".into()))?);fun133.call(args131,kw132)?}});args128.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun136=e.get("v")?;let mut args134=Vec::new();let mut kw135=Vec::new();args134.push(e.get("section")?.get(Val::Str("start".into()))?);fun136.call(args134,kw135)?}});fun130.call(args128,kw129)?}});Val::list(s)});fun67.call(args65,kw66)?}};e.set("wire",assigned64.clone())?;
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun139=e.get("loft")?.attr("AddWire")?;let mut args137=Vec::new();let mut kw138=Vec::new();args137.push(e.get("wire")?.attr("wrapped")?);fun139.call(args137,kw138)?}};
}
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun142=e.get("loft")?.attr("Build")?;let mut args140=Vec::new();let mut kw141=Vec::new();fun142.call(args140,kw141)?}};
{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun145=e.get("fills")?.attr("append")?;let mut args143=Vec::new();let mut kw144=Vec::new();args143.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun148=e.get("cq")?.attr("Solid")?;let mut args146=Vec::new();let mut kw147=Vec::new();args146.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun151=e.get("loft")?.attr("Shape")?;let mut args149=Vec::new();let mut kw150=Vec::new();fun151.call(args149,kw150)?}});fun148.call(args146,kw147)?}});fun145.call(args143,kw144)?}};
}
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun154=e.get("cq")?.attr("Compound")?.attr("makeCompound")?;let mut args152=Vec::new();let mut kw153=Vec::new();args152.push(e.get("fills")?);fun154.call(args152,kw153)?}});
Ok(Val::None)})})?;
    // silhouette
    e.set("silhouette",{let params=vec![("outer".into(),None,false),("rounded_box".into(),None,false),("vertical_radius".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned155={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun158=e.get("profile")?;let mut args156=Vec::new();let mut kw157=Vec::new();args156.push(e.get("outer")?);fun158.call(args156,kw157)?}};e.set("p",assigned155.clone())?;
let assigned159=e.get("outer")?;let unpack160=unpack(assigned159.clone(),6)?;e.set("x0",unpack160[0].clone())?;e.set("x1",unpack160[1].clone())?;e.set("y0",unpack160[2].clone())?;e.set("y1",unpack160[3].clone())?;e.set("z0",unpack160[4].clone())?;e.set("z1",unpack160[5].clone())?;
let assigned161={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun164={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun167={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun170={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun173={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun176={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun179={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun182={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun185={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun188={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun191=e.get("cq")?.attr("Workplane")?;let mut args189=Vec::new();let mut kw190=Vec::new();args189.push(Val::Str("YZ".into()));kw190.push(("origin".into(),{let mut s=Vec::new();s.push(e.get("x0")?);s.push(Val::Int(0i64));s.push(Val::Int(0i64));Val::tuple(s)}));fun191.call(args189,kw190)?}}.attr("moveTo")?;let mut args186=Vec::new();let mut kw187=Vec::new();args186.push(e.get("y0")?);args186.push(e.get("z0")?);fun188.call(args186,kw187)?}}.attr("lineTo")?;let mut args183=Vec::new();let mut kw184=Vec::new();args183.extend(e.get("p")?.get(Val::Str("foot".into()))?.iter()?);fun185.call(args183,kw184)?}}.attr("threePointArc")?;let mut args180=Vec::new();let mut kw181=Vec::new();args180.push(e.get("p")?.get(Val::Str("front_mid".into()))?);args180.push(e.get("p")?.get(Val::Str("start".into()))?);fun182.call(args180,kw181)?}}.attr("lineTo")?;let mut args177=Vec::new();let mut kw178=Vec::new();args177.extend(e.get("p")?.get(Val::Str("end".into()))?.iter()?);fun179.call(args177,kw178)?}}.attr("threePointArc")?;let mut args174=Vec::new();let mut kw175=Vec::new();args174.push(e.get("p")?.get(Val::Str("top_mid".into()))?);args174.push(e.get("p")?.get(Val::Str("roof".into()))?);fun176.call(args174,kw175)?}}.attr("lineTo")?;let mut args171=Vec::new();let mut kw172=Vec::new();args171.push(e.get("y1")?);args171.push(e.get("z1")?);fun173.call(args171,kw172)?}}.attr("lineTo")?;let mut args168=Vec::new();let mut kw169=Vec::new();args168.push(e.get("y1")?);args168.push(e.get("z0")?);fun170.call(args168,kw169)?}}.attr("close")?;let mut args165=Vec::new();let mut kw166=Vec::new();fun167.call(args165,kw166)?}}.attr("val")?;let mut args162=Vec::new();let mut kw163=Vec::new();fun164.call(args162,kw163)?}};e.set("wire",assigned161.clone())?;
let assigned192={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun195=e.get("cq")?.attr("Solid")?.attr("extrudeLinear")?;let mut args193=Vec::new();let mut kw194=Vec::new();args193.push(e.get("wire")?);args193.push({let mut s=Vec::new();Val::list(s)});args193.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun198=e.get("cq")?.attr("Vector")?;let mut args196=Vec::new();let mut kw197=Vec::new();args196.push(binary("sub",e.get("x1")?,e.get("x0")?)?);args196.push(Val::Int(0i64));args196.push(Val::Int(0i64));fun198.call(args196,kw197)?}});fun195.call(args193,kw194)?}};e.set("envelope",assigned192.clone())?;
let assigned199=binary("add",e.get("y0")?,e.get("vertical_radius")?)?;e.set("fore_end",assigned199.clone())?;
let assigned200={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun203={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun206={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun209={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun212=e.get("cq")?.attr("Workplane")?;let mut args210=Vec::new();let mut kw211=Vec::new();args210.push(Val::Str("XY".into()));fun212.call(args210,kw211)?}}.attr("box")?;let mut args207=Vec::new();let mut kw208=Vec::new();args207.push(binary("sub",e.get("x1")?,e.get("x0")?)?);args207.push(binary("sub",e.get("y1")?,e.get("fore_end")?)?);args207.push(binary("sub",e.get("z1")?,e.get("z0")?)?);fun209.call(args207,kw208)?}}.attr("translate")?;let mut args204=Vec::new();let mut kw205=Vec::new();args204.push({let mut s=Vec::new();s.push(binary("truediv",binary("add",e.get("x0")?,e.get("x1")?)?,Val::Float(2.0f64))?);s.push(binary("truediv",binary("add",e.get("fore_end")?,e.get("y1")?)?,Val::Float(2.0f64))?);s.push(binary("truediv",binary("add",e.get("z0")?,e.get("z1")?)?,Val::Float(2.0f64))?);Val::tuple(s)});fun206.call(args204,kw205)?}}.attr("val")?;let mut args201=Vec::new();let mut kw202=Vec::new();fun203.call(args201,kw202)?}};e.set("rear_fill",assigned200.clone())?;
let assigned213={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun216={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun219=e.get("envelope")?.attr("intersect")?;let mut args217=Vec::new();let mut kw218=Vec::new();args217.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun222=e.get("rounded_box")?.attr("fuse")?;let mut args220=Vec::new();let mut kw221=Vec::new();args220.push(e.get("rear_fill")?);fun222.call(args220,kw221)?}});fun219.call(args217,kw218)?}}.attr("clean")?;let mut args214=Vec::new();let mut kw215=Vec::new();fun216.call(args214,kw215)?}};e.set("body",assigned213.clone())?;
let assigned223={let e=e.child();let out224=Val::list(vec![]);for item225 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun228=e.get("body")?.attr("Edges")?;let mut args226=Vec::new();let mut kw227=Vec::new();fun228.call(args226,kw227)?}}.iter()? {e.set("edge",item225)?;if {let v240={let v246={let v250={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun249=e.get("edge")?.attr("BoundingBox")?;let mut args247=Vec::new();let mut kw248=Vec::new();fun249.call(args247,kw248)?}}.attr("xmin")?;let v251=binary("sub",binary("sub",e.get("x1")?,e.get("vertical_radius")?)?,Val::Float(1e-05f64))?;Val::Bool(compare("ge",v250.clone(),v251.clone())?.truthy()?)};if v246.truthy()? {v246} else {{let v244={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun243=e.get("edge")?.attr("BoundingBox")?;let mut args241=Vec::new();let mut kw242=Vec::new();fun243.call(args241,kw242)?}}.attr("xmax")?;let v245=binary("add",binary("add",e.get("x0")?,e.get("vertical_radius")?)?,Val::Float(1e-05f64))?;Val::Bool(compare("le",v244.clone(),v245.clone())?.truthy()?)}}};if v240.truthy()? {{let v234={let v238={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun237=e.get("edge")?.attr("BoundingBox")?;let mut args235=Vec::new();let mut kw236=Vec::new();fun237.call(args235,kw236)?}}.attr("zmin")?;let v239=binary("sub",e.get("p")?.get(Val::Str("foot".into()))?.get(Val::Int(1i64))?,Val::Float(1e-05f64))?;Val::Bool(compare("ge",v238.clone(),v239.clone())?.truthy()?)};if v234.truthy()? {{let v232={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun231=e.get("edge")?.attr("BoundingBox")?;let mut args229=Vec::new();let mut kw230=Vec::new();fun231.call(args229,kw230)?}}.attr("ymin")?;let v233=binary("sub",e.get("y1")?,Val::Float(1.0f64))?;Val::Bool(compare("lt",v232.clone(),v233.clone())?.truthy()?)}} else {v234}}} else {v240}}.truthy()? {out224.attr("append")?.call(vec![e.get("edge")?],vec![])?;}}out224};e.set("side_edges",assigned223.clone())?;
let assigned252={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun255={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun258={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun261=e.get("body")?.attr("fillet")?;let mut args259=Vec::new();let mut kw260=Vec::new();args259.push(e.get("SIDE_RADIUS")?);args259.push(e.get("side_edges")?);fun261.call(args259,kw260)?}}.attr("intersect")?;let mut args256=Vec::new();let mut kw257=Vec::new();args256.push(e.get("rounded_box")?);fun258.call(args256,kw257)?}}.attr("clean")?;let mut args253=Vec::new();let mut kw254=Vec::new();fun255.call(args253,kw254)?}};e.set("rounded",assigned252.clone())?;
let mod262=rt.import_module("overhang_round")?;e.set("rectangular_edge_fill",rt.member("overhang_round","rectangular_edge_fill")?)?;
let assigned263={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun266=e.get("rectangular_edge_fill")?;let mut args264=Vec::new();let mut kw265=Vec::new();args264.push(e.get("x0")?);args264.push(e.get("x1")?);args264.push(e.get("p")?.get(Val::Str("roof".into()))?.get(Val::Int(0i64))?);args264.push(e.get("y1")?);args264.push(e.get("z1")?);args264.push(e.get("SIDE_RADIUS")?);fun266.call(args264,kw265)?}};e.set("aft_cap",assigned263.clone())?;
let assigned267={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun270=e.get("aft_cap")?.attr("intersect")?;let mut args268=Vec::new();let mut kw269=Vec::new();args268.push(e.get("rounded_box")?);fun270.call(args268,kw269)?}};e.set("aft_cap",assigned267.clone())?;
let assigned271={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun274={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun277={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun280=e.get("_roof_fill")?;let mut args278=Vec::new();let mut kw279=Vec::new();args278.push(e.get("outer")?);fun280.call(args278,kw279)?}}.attr("intersect")?;let mut args275=Vec::new();let mut kw276=Vec::new();args275.push(e.get("body")?);fun277.call(args275,kw276)?}}.attr("intersect")?;let mut args272=Vec::new();let mut kw273=Vec::new();args272.push(e.get("rounded_box")?);fun274.call(args272,kw273)?}};e.set("fore_cap",assigned271.clone())?;
let assigned281={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun284={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun287={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun290={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun293=e.get("rounded")?.attr("fuse")?;let mut args291=Vec::new();let mut kw292=Vec::new();args291.push(e.get("aft_cap")?);fun293.call(args291,kw292)?}}.attr("clean")?;let mut args288=Vec::new();let mut kw289=Vec::new();fun290.call(args288,kw289)?}}.attr("fuse")?;let mut args285=Vec::new();let mut kw286=Vec::new();args285.push(e.get("fore_cap")?);fun287.call(args285,kw286)?}}.attr("clean")?;let mut args282=Vec::new();let mut kw283=Vec::new();fun284.call(args282,kw283)?}};e.set("result",assigned281.clone())?;
let assigned294={let e=e.child();let out295=Val::list(vec![]);for item296 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun299=e.get("result")?.attr("Faces")?;let mut args297=Vec::new();let mut kw298=Vec::new();fun299.call(args297,kw298)?}}.iter()? {e.set("face",item296)?;if {let v311={let v315={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun314=e.get("face")?.attr("geomType")?;let mut args312=Vec::new();let mut kw313=Vec::new();fun314.call(args312,kw313)?}};let v316=Val::Str("PLANE".into());Val::Bool(compare("eq",v315.clone(),v316.clone())?.truthy()?)};if v311.truthy()? {{let v305={let v309={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun308=e.get("face")?.attr("normalAt")?;let mut args306=Vec::new();let mut kw307=Vec::new();fun308.call(args306,kw307)?}}.attr("z")?;let v310=binary("add",unary("neg",Val::Float(1.0f64))?,Val::Float(1e-06f64))?;Val::Bool(compare("lt",v309.clone(),v310.clone())?.truthy()?)};if v305.truthy()? {{let v303={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_swept_top.rs",line!());{let fun302=e.get("face")?.attr("Center")?;let mut args300=Vec::new();let mut kw301=Vec::new();fun302.call(args300,kw301)?}}.attr("z")?;let v304=binary("add",e.get("p")?.get(Val::Str("foot".into()))?.get(Val::Int(1i64))?,Val::Float(1e-05f64))?;Val::Bool(compare("gt",v303.clone(),v304.clone())?.truthy()?)}} else {v305}}} else {v311}}.truthy()? {out295.attr("append")?.call(vec![e.get("face")?],vec![])?;}}out295};e.set("undersides",assigned294.clone())?;
if !unary("not",e.get("undersides")?)?.truthy()? {anyhow::bail!("{}",val_string(Val::Str("the swept roof has an exposed flat underside".into()))?);}
return Ok(e.get("result")?);
Ok(Val::None)})})?;
    // rounded_prism
    e.set("rounded_prism", {
        let params = vec![
            ("width".into(), None, false),
            ("depth".into(), None, false),
            ("radius".into(), None, false),
            ("z0".into(), None, false),
            ("z1".into(), None, false),
            ("cx".into(), Some(Val::Float(0.0f64)), false),
            ("cy".into(), Some(Val::Float(0.0f64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned317 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
                    line!(),
                );
                {
                    let fun320 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
                            line!(),
                        );
                        {
                            let fun323 = {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
                                    line!(),
                                );
                                {
                                    let fun326 = e.get("cq")?.attr("Workplane")?;
                                    let mut args324 = Vec::new();
                                    let mut kw325 = Vec::new();
                                    args324.push(Val::Str("XY".into()));
                                    kw325.push(("origin".into(), {
                                        let mut s = Vec::new();
                                        s.push(e.get("cx")?);
                                        s.push(e.get("cy")?);
                                        s.push(e.get("z0")?);
                                        Val::tuple(s)
                                    }));
                                    fun326.call(args324, kw325)?
                                }
                            }
                            .attr("rect")?;
                            let mut args321 = Vec::new();
                            let mut kw322 = Vec::new();
                            args321.push(e.get("width")?);
                            args321.push(e.get("depth")?);
                            fun323.call(args321, kw322)?
                        }
                    }
                    .attr("val")?;
                    let mut args318 = Vec::new();
                    let mut kw319 = Vec::new();
                    fun320.call(args318, kw319)?
                }
            };
            e.set("wire", assigned317.clone())?;
            let assigned327 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
                    line!(),
                );
                {
                    let fun330 = e.get("wire")?.attr("fillet2D")?;
                    let mut args328 = Vec::new();
                    let mut kw329 = Vec::new();
                    args328.push(e.get("radius")?);
                    args328.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
                            line!(),
                        );
                        {
                            let fun333 = e.get("wire")?.attr("Vertices")?;
                            let mut args331 = Vec::new();
                            let mut kw332 = Vec::new();
                            fun333.call(args331, kw332)?
                        }
                    });
                    fun330.call(args328, kw329)?
                }
            };
            e.set("wire", assigned327.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
                    line!(),
                );
                {
                    let fun336 = e.get("cq")?.attr("Solid")?.attr("extrudeLinear")?;
                    let mut args334 = Vec::new();
                    let mut kw335 = Vec::new();
                    args334.push(e.get("wire")?);
                    args334.push({
                        let mut s = Vec::new();
                        Val::list(s)
                    });
                    args334.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_swept_top.rs",
                            line!(),
                        );
                        {
                            let fun339 = e.get("cq")?.attr("Vector")?;
                            let mut args337 = Vec::new();
                            let mut kw338 = Vec::new();
                            args337.push(Val::Int(0i64));
                            args337.push(Val::Int(0i64));
                            args337.push(binary("sub", e.get("z1")?, e.get("z0")?)?);
                            fun339.call(args337, kw338)?
                        }
                    });
                    fun336.call(args334, kw335)?
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
