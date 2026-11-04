#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("hashlib", rt.import_module("hashlib")?)?;
    e.set("json", rt.import_module("json")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
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
                    let fun17 = binary("truediv", e.get("p")?, Val::Str("tools/docgen".into()))?
                        .attr("is_dir")?;
                    let mut args15 = Vec::new();
                    let mut kw16 = Vec::new();
                    fun17.call(args15, kw16)?
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
    e.set("ROOT", assigned9.clone())?;
    let assigned18 = binary("truediv", e.get("ROOT")?, Val::Str("hardware".into()))?;
    e.set("HW", assigned18.clone())?;
    for item19 in {
        let mut s = Vec::new();
        s.push(binary("truediv", e.get("HW")?, Val::Str("scripts".into()))?);
        s.push(binary("truediv", e.get("ROOT")?, Val::Str("tools".into()))?);
        s.push(e.get("HERE")?.attr("parents")?.get(Val::Int(1i64))?);
        s.push(binary(
            "truediv",
            e.get("HERE")?.attr("parents")?.get(Val::Int(1i64))?,
            Val::Str("reservoir".into()),
        )?);
        s.push(binary(
            "truediv",
            e.get("HERE")?.attr("parents")?.get(Val::Int(1i64))?,
            Val::Str("reed-bridge".into()),
        )?);
        s.push(binary(
            "truediv",
            e.get("HW")?,
            Val::Str("cut-parts/carbonation/endcaps-circular".into()),
        )?);
        s.push(binary(
            "truediv",
            e.get("HW")?,
            Val::Str("assembly".into()),
        )?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("p", item19)?;
        {
            let fun22 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args20 = Vec::new();
            let mut kw21 = Vec::new();
            args20.push(Val::Int(0i64));
            args20.push({
                let fun25 = e.get("str")?;
                let mut args23 = Vec::new();
                let mut kw24 = Vec::new();
                args23.push(e.get("p")?);
                fun25.call(args23, kw24)?
            });
            fun22.call(args20, kw21)?
        };
    }
    e.set("f", rt.import_module("_float_interface")?)?;
    e.set("res", rt.import_module("reservoir")?)?;
    e.set("bridge", rt.import_module("reed_bridge")?)?;
    e.set("cap", rt.import_module("endcap_circular_dxf")?)?;
    e.set("pv", rt.import_module("_pressure_vessel_sync")?)?;
    let mod26 = rt.import_module("_reed_channels")?;
    e.set(
        "reed_y_center",
        rt.member("_reed_channels", "reed_y_center")?,
    )?;
    let mod27 = rt.import_module("_cold_core_interface")?;
    e.set(
        "reed_column_axis_x",
        rt.member("_cold_core_interface", "reed_column_axis_x")?,
    )?;
    e.set("_assembly_model", rt.import_module("_assembly_model")?)?;
    let mod28 = rt.import_module("docgen")?;
    e.set("substitute_md", rt.member("docgen", "substitute_md")?)?;
    // load
    e.set("load", {
        let params = vec![("path".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned29 = {
                let fun32 = e.get("Path")?;
                let mut args30 = Vec::new();
                let mut kw31 = Vec::new();
                args30.push(binary(
                    "add",
                    {
                        let fun35 = e.get("str")?;
                        let mut args33 = Vec::new();
                        let mut kw34 = Vec::new();
                        args33.push(e.get("path")?);
                        fun35.call(args33, kw34)?
                    },
                    Val::Str(".npz".into()),
                )?);
                fun32.call(args30, kw31)?
            };
            e.set("model", assigned29.clone())?;
            let assigned36 = {
                let fun39 = e.get("range")?;
                let mut args37 = Vec::new();
                let mut kw38 = Vec::new();
                args37.push({
                    let fun42 = e.get("len")?;
                    let mut args40 = Vec::new();
                    let mut kw41 = Vec::new();
                    args40.push({
                        let fun45 = e.get("_assembly_model")?.attr("identity")?;
                        let mut args43 = Vec::new();
                        let mut kw44 = Vec::new();
                        args43.push(e.get("model")?);
                        fun45.call(args43, kw44)?
                    });
                    fun42.call(args40, kw41)?
                });
                fun39.call(args37, kw38)?
            };
            e.set("indices", assigned36.clone())?;
            if unary("not", e.get("indices")?)?.truthy()? {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun48 = e.get("ValueError")?;
                        let mut args46 = Vec::new();
                        let mut kw47 = Vec::new();
                        args46.push({
                            let mut str49 = String::new();
                            str49.push_str(&format(&e.get("path")?, &String::new())?);
                            str49.push_str(": emitted CAD holds no solid");
                            Val::Str(str49)
                        });
                        fun48.call(args46, kw47)?
                    })?
                );
            }
            return Ok({
                let fun52 = e.get("_assembly_model")?.attr("instance")?;
                let mut args50 = Vec::new();
                let mut kw51 = Vec::new();
                args50.push(e.get("model")?);
                kw51.push(("indices".into(), e.get("indices")?));
                fun52.call(args50, kw51)?
            });
            Ok(Val::None)
        })
    })?;
    // translated
    e.set("translated", {
        let params = vec![
            ("reference".into(), None, false),
            ("xyz".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned53 = e.get("xyz")?;
            let unpack54 = unpack(assigned53.clone(), 3)?;
            e.set("x", unpack54[0].clone())?;
            e.set("y", unpack54[1].clone())?;
            e.set("z", unpack54[2].clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                dict_extend(&d, e.get("reference")?)?;
                d.set(Val::Str("transform".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(1.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(e.get("x")?);
                        Val::list(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(1.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(e.get("y")?);
                        Val::list(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(1.0f64));
                        s.push(e.get("z")?);
                        Val::list(s)
                    });
                    Val::list(s)
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // digest
    e.set("digest", {
        let params = vec![("path".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun57 = {
                    let fun60 = e.get("hashlib")?.attr("sha256")?;
                    let mut args58 = Vec::new();
                    let mut kw59 = Vec::new();
                    args58.push({
                        let fun63 = e.get("path")?.attr("read_bytes")?;
                        let mut args61 = Vec::new();
                        let mut kw62 = Vec::new();
                        fun63.call(args61, kw62)?
                    });
                    fun60.call(args58, kw59)?
                }
                .attr("hexdigest")?;
                let mut args55 = Vec::new();
                let mut kw56 = Vec::new();
                fun57.call(args55, kw56)?
            });
            Ok(Val::None)
        })
    })?;
    // main
    e.set("main",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned64=binary("truediv",e.get("HERE")?,Val::Str("float-aero.step".into()))?;e.set("float_path",assigned64.clone())?;
let assigned65={let fun68=e.get("load")?;let mut args66=Vec::new();let mut kw67=Vec::new();args66.push(e.get("float_path")?);fun68.call(args66,kw67)?};e.set("body",assigned65.clone())?;
let assigned69={let d=Val::dict(vec![]);d};e.set("guides",assigned69.clone())?;
let assigned70={let mut s=Vec::new();s.push(e.get("float_path")?);s.push(binary("truediv",e.get("HERE")?,Val::Str("float-aero.stl".into()))?);s.push(binary("truediv",e.get("HERE")?,Val::Str("design.json".into()))?);s.push(binary("truediv",e.get("HERE")?.attr("parents")?.get(Val::Int(1i64))?,Val::Str("_float_interface.py".into()))?);s.push(binary("truediv",e.get("HERE")?,Val::Str("physical-observations.json".into()))?);s.push(binary("truediv",e.get("HW")?,Val::Str("cut-parts/carbonation/endcaps-circular/endcap-circular-2hole.step".into()))?);s.push(binary("truediv",e.get("HW")?,Val::Str("cut-parts/carbonation/endcaps-circular/endcap-circular-2hole-drawing.pdf".into()))?);Val::list(s)};e.set("inputs",assigned70.clone())?;
let assigned71={let fun74=e.get("_assembly_model")?.attr("measure")?;let mut args72=Vec::new();let mut kw73=Vec::new();args72.push({let mut s=Vec::new();s.push(e.get("body")?);Val::list(s)});args72.push({let mut s=Vec::new();Val::tuple(s)});fun74.call(args72,kw73)?}.get(Val::Str("bodies".into()))?;e.set("bounds",assigned71.clone())?;
let assigned75={let e=e.child();let out76=Val::list(vec![]);for item77 in {let fun80=e.get("range")?;let mut args78=Vec::new();let mut kw79=Vec::new();args78.push(Val::Int(3i64));fun80.call(args78,kw79)?}.iter()? {e.set("i",item77)?;out76.attr("append")?.call(vec![{let fun83=e.get("min")?;let mut args81=Vec::new();let mut kw82=Vec::new();args81.push({let e=e.child();let out84=Val::list(vec![]);for item85 in e.get("bounds")?.iter()? {e.set("row",item85)?;out84.attr("append")?.call(vec![e.get("row")?.get(Val::Str("min".into()))?.get(e.get("i")?)?],vec![])?;}out84});fun83.call(args81,kw82)?}],vec![])?;}out76};e.set("lower",assigned75.clone())?;
let assigned86={let e=e.child();let out87=Val::list(vec![]);for item88 in {let fun91=e.get("range")?;let mut args89=Vec::new();let mut kw90=Vec::new();args89.push(Val::Int(3i64));fun91.call(args89,kw90)?}.iter()? {e.set("i",item88)?;out87.attr("append")?.call(vec![{let fun94=e.get("max")?;let mut args92=Vec::new();let mut kw93=Vec::new();args92.push({let e=e.child();let out95=Val::list(vec![]);for item96 in e.get("bounds")?.iter()? {e.set("row",item96)?;out95.attr("append")?.call(vec![e.get("row")?.get(Val::Str("max".into()))?.get(e.get("i")?)?],vec![])?;}out95});fun94.call(args92,kw93)?}],vec![])?;}out87};e.set("upper",assigned86.clone())?;
if !{let v100={let fun99=e.get("abs")?;let mut args97=Vec::new();let mut kw98=Vec::new();args97.push(binary("sub",binary("sub",e.get("upper")?.get(Val::Int(0i64))?,e.get("lower")?.get(Val::Int(0i64))?)?,e.get("f")?.attr("diameter")?)?);fun99.call(args97,kw98)?};let v101=Val::Float(1e-06f64);Val::Bool(compare("lt",v100.clone(),v101.clone())?.truthy()?)}.truthy()? {anyhow::bail!("{}",val_string(Val::Str("assertion failed".into()))?);}
if !{let v105={let fun104=e.get("abs")?;let mut args102=Vec::new();let mut kw103=Vec::new();args102.push(binary("sub",binary("sub",e.get("upper")?.get(Val::Int(2i64))?,e.get("lower")?.get(Val::Int(2i64))?)?,e.get("f")?.attr("height")?)?);fun104.call(args102,kw103)?};let v106=Val::Float(1e-06f64);Val::Bool(compare("lt",v105.clone(),v106.clone())?.truthy()?)}.truthy()? {anyhow::bail!("{}",val_string(Val::Str("assertion failed".into()))?);}
if !{let v110={let fun109=e.get("abs")?;let mut args107=Vec::new();let mut kw108=Vec::new();args107.push(binary("sub",binary("add",binary("mul",e.get("cap")?.attr("register_radius")?,Val::Float(25.4f64))?,e.get("f")?.attr("rod_axis_from_inner_wall")?)?,binary("truediv",binary("mul",e.get("cap")?.attr("tube_id")?,Val::Float(25.4f64))?,Val::Int(2i64))?)?);fun109.call(args107,kw108)?};let v111=Val::Float(1e-09f64);Val::Bool(compare("lt",v110.clone(),v111.clone())?.truthy()?)}.truthy()? {anyhow::bail!("{}",val_string(Val::Str("assertion failed".into()))?);}
if !{let v115={let fun114=e.get("abs")?;let mut args112=Vec::new();let mut kw113=Vec::new();args112.push(binary("sub",binary("add",e.get("res")?.attr("rod_position_x")?,e.get("f")?.attr("rod_axis_from_inner_wall")?)?,e.get("res")?.attr("inner_far_x_abs")?)?);fun114.call(args112,kw113)?};let v116=Val::Float(1e-09f64);Val::Bool(compare("lt",v115.clone(),v116.clone())?.truthy()?)}.truthy()? {anyhow::bail!("{}",val_string(Val::Str("assertion failed".into()))?);}
if !{let v120={let fun119=e.get("abs")?;let mut args117=Vec::new();let mut kw118=Vec::new();args117.push(binary("sub",e.get("reed_y_center")?,e.get("res")?.attr("rod_position_y")?)?);fun119.call(args117,kw118)?};let v121=Val::Float(1e-09f64);Val::Bool(compare("lt",v120.clone(),v121.clone())?.truthy()?)}.truthy()? {anyhow::bail!("{}",val_string(Val::Str("assertion failed".into()))?);}
let assigned122={let mut s=Vec::new();s.push({let d=Val::dict(vec![]);d});s.push({let mut s=Vec::new();Val::list(s)});s.push({let mut s=Vec::new();Val::list(s)});Val::tuple(s)};let unpack123=unpack(assigned122.clone(),3)?;e.set("references",unpack123[0].clone())?;e.set("queries",unpack123[1].clone())?;e.set("owners",unpack123[2].clone())?;
for item124 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Int(1i64));s.push(Val::Str("right".into()));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(unary("neg",Val::Int(1i64))?);s.push(Val::Str("left".into()));Val::tuple(s)});Val::tuple(s)}.iter()? {
let unpack185=unpack(item124,2)?;e.set("side",unpack185[0].clone())?;e.set("label",unpack185[1].clone())?;let assigned125=binary("truediv",binary("truediv",e.get("HERE")?.attr("parents")?.get(Val::Int(1i64))?,Val::Str("reservoir".into()))?,{let mut str126=String::new();str126.push_str("reservoir-");str126.push_str(&format(&e.get("label")?,&String::new())?);str126.push_str(".step");Val::Str(str126)})?;e.set("vessel_path",assigned125.clone())?;
let assigned127=binary("truediv",binary("truediv",e.get("HERE")?.attr("parents")?.get(Val::Int(1i64))?,Val::Str("reservoir".into()))?,{let mut str128=String::new();str128.push_str("reservoir-cap-");str128.push_str(&format(&e.get("label")?,&String::new())?);str128.push_str(".step");Val::Str(str128)})?;e.set("cap_path",assigned127.clone())?;
let assigned129={let fun132=e.get("load")?;let mut args130=Vec::new();let mut kw131=Vec::new();args130.push(e.get("vessel_path")?);fun132.call(args130,kw131)?};e.get("references")?.set(binary("add",e.get("label")?,Val::Str("-vessel".into()))?,assigned129.clone())?;
let assigned133={let fun136=e.get("translated")?;let mut args134=Vec::new();let mut kw135=Vec::new();args134.push({let fun139=e.get("load")?;let mut args137=Vec::new();let mut kw138=Vec::new();args137.push(e.get("cap_path")?);fun139.call(args137,kw138)?});args134.push({let mut s=Vec::new();s.push(Val::Int(0i64));s.push(Val::Int(0i64));s.push(e.get("res")?.attr("cap_assembly_lift")?);Val::tuple(s)});fun136.call(args134,kw135)?};e.get("references")?.set(binary("add",e.get("label")?,Val::Str("-lid".into()))?,assigned133.clone())?;
e.set("inputs",binary("add",e.get("inputs")?,{let mut s=Vec::new();s.push(e.get("vessel_path")?);s.push(e.get("cap_path")?);Val::list(s)})?)?;
let assigned140=Val::Int(0i64);e.set("count",assigned140.clone())?;
let assigned141=e.get("res")?.attr("float_magnet_travel_z")?;let unpack142=unpack(assigned141.clone(),2)?;e.set("lo",unpack142[0].clone())?;e.set("hi",unpack142[1].clone())?;
for item143 in {let mut s=Vec::new();s.push(Val::Int(0i64));s.push(Val::Float(0.25f64));s.push(Val::Float(0.5f64));s.push(Val::Float(0.75f64));s.push(Val::Int(1i64));Val::tuple(s)}.iter()? {
e.set("t",item143)?;let assigned144=binary("sub",binary("add",e.get("lo")?,binary("mul",binary("sub",e.get("hi")?,e.get("lo")?)?,e.get("t")?)?)?,e.get("f")?.attr("magnet_midplane")?)?;e.set("z",assigned144.clone())?;
for item145 in {let fun170=e.get("range")?;let mut args168=Vec::new();let mut kw169=Vec::new();args168.push(Val::Int(0i64));args168.push(Val::Int(360i64));args168.push(Val::Int(45i64));fun170.call(args168,kw169)?}.iter()? {
e.set("angle",item145)?;let assigned146=e.get("f")?.attr("guide_radial_clearance")?;e.set("r",assigned146.clone())?;
let assigned147={let mut s=Vec::new();s.push(binary("mul",e.get("r")?,{let fun150=e.get("math")?.attr("cos")?;let mut args148=Vec::new();let mut kw149=Vec::new();args148.push({let fun153=e.get("math")?.attr("radians")?;let mut args151=Vec::new();let mut kw152=Vec::new();args151.push(e.get("angle")?);fun153.call(args151,kw152)?});fun150.call(args148,kw149)?})?);s.push(binary("mul",e.get("r")?,{let fun156=e.get("math")?.attr("sin")?;let mut args154=Vec::new();let mut kw155=Vec::new();args154.push({let fun159=e.get("math")?.attr("radians")?;let mut args157=Vec::new();let mut kw158=Vec::new();args157.push(e.get("angle")?);fun159.call(args157,kw158)?});fun156.call(args154,kw155)?})?);Val::tuple(s)};let unpack160=unpack(assigned147.clone(),2)?;e.set("dx",unpack160[0].clone())?;e.set("dy",unpack160[1].clone())?;
let assigned161={let mut str162=String::new();str162.push_str(&format(&e.get("label")?,&String::new())?);str162.push_str("-float-");str162.push_str(&format(&e.get("count")?,&String::new())?);Val::Str(str162)};e.set("moved",assigned161.clone())?;
let assigned163={let fun166=e.get("translated")?;let mut args164=Vec::new();let mut kw165=Vec::new();args164.push(e.get("body")?);args164.push({let mut s=Vec::new();s.push(binary("add",binary("mul",e.get("side")?,e.get("res")?.attr("rod_position_x")?)?,e.get("dx")?)?);s.push(binary("add",e.get("res")?.attr("rod_position_y")?,e.get("dy")?)?);s.push(e.get("z")?);Val::tuple(s)});fun166.call(args164,kw165)?};e.get("references")?.set(e.get("moved")?,assigned163.clone())?;
for item167 in {let mut s=Vec::new();s.push(binary("add",e.get("label")?,Val::Str("-vessel".into()))?);s.push(binary("add",e.get("label")?,Val::Str("-lid".into()))?);Val::tuple(s)}.iter()? {
e.set("solid",item167)?;e.set("queries",binary("add",e.get("queries")?,{let mut s=Vec::new();s.push({let d=Val::dict(vec![]);d.set(Val::Str("a".into()),e.get("moved")?)?;d.set(Val::Str("b".into()),e.get("solid")?)?;d.set(Val::Str("kind".into()),Val::Str("common".into()))?;d.set(Val::Str("distribute_a".into()),Val::Bool(true))?;d});s.push({let d=Val::dict(vec![]);d.set(Val::Str("a".into()),e.get("moved")?)?;d.set(Val::Str("b".into()),e.get("solid")?)?;d.set(Val::Str("kind".into()),Val::Str("gap".into()))?;d});Val::list(s)})?)?;
e.set("owners",binary("add",e.get("owners")?,{let mut s=Vec::new();s.push(e.get("label")?);s.push(e.get("label")?);Val::list(s)})?)?;
}
e.set("count",binary("add",e.get("count")?,Val::Int(1i64))?)?;
}
let assigned171={let mut str172=String::new();str172.push_str(&format(&e.get("label")?,&String::new())?);str172.push_str("-float-");str172.push_str(&format(&e.get("count")?,&String::new())?);Val::Str(str172)};e.set("moved",assigned171.clone())?;
let assigned173={let fun176=e.get("translated")?;let mut args174=Vec::new();let mut kw175=Vec::new();args174.push(e.get("body")?);args174.push({let mut s=Vec::new();s.push(binary("mul",e.get("side")?,e.get("res")?.attr("rod_position_x")?)?);s.push(e.get("res")?.attr("rod_position_y")?);s.push(e.get("z")?);Val::tuple(s)});fun176.call(args174,kw175)?};e.get("references")?.set(e.get("moved")?,assigned173.clone())?;
for item177 in {let mut s=Vec::new();s.push(binary("add",e.get("label")?,Val::Str("-vessel".into()))?);s.push(binary("add",e.get("label")?,Val::Str("-lid".into()))?);Val::tuple(s)}.iter()? {
e.set("solid",item177)?;{let fun180=e.get("queries")?.attr("append")?;let mut args178=Vec::new();let mut kw179=Vec::new();args178.push({let d=Val::dict(vec![]);d.set(Val::Str("a".into()),e.get("moved")?)?;d.set(Val::Str("b".into()),e.get("solid")?)?;d.set(Val::Str("kind".into()),Val::Str("common".into()))?;d.set(Val::Str("distribute_a".into()),Val::Bool(true))?;d});fun180.call(args178,kw179)?};
{let fun183=e.get("owners")?.attr("append")?;let mut args181=Vec::new();let mut kw182=Vec::new();args181.push(e.get("label")?);fun183.call(args181,kw182)?};
}
e.set("count",binary("add",e.get("count")?,Val::Int(1i64))?)?;
}
let assigned184={let d=Val::dict(vec![]);d.set(Val::Str("rod_axis_xy_mm".into()),{let mut s=Vec::new();s.push(binary("mul",e.get("side")?,e.get("res")?.attr("rod_position_x")?)?);s.push(e.get("res")?.attr("rod_position_y")?);Val::list(s)})?;d.set(Val::Str("magnet_travel_z_mm".into()),{let mut s=Vec::new();s.push(e.get("lo")?);s.push(e.get("hi")?);Val::list(s)})?;d.set(Val::Str("upright_samples".into()),e.get("count")?)?;d.set(Val::Str("maximum_float_body_cap_overlap_mm3".into()),Val::Float(0.0f64))?;d.set(Val::Str("minimum_body_cap_distance_mm".into()),e.get("math")?.attr("inf")?)?;d.set(Val::Str("end_stops".into()),Val::Str("contact allowed at the lower/upper boss; no volume intrusion".into()))?;d};e.get("guides")?.set(e.get("label")?,assigned184.clone())?;
}
for item186 in {let fun208=e.get("zip")?;let mut args206=Vec::new();let mut kw207=Vec::new();args206.push(e.get("owners")?);args206.push({let fun211=e.get("_assembly_model")?.attr("measure_groups")?;let mut args209=Vec::new();let mut kw210=Vec::new();args209.push(e.get("references")?);args209.push(e.get("queries")?);fun211.call(args209,kw210)?});kw207.push(("strict".into(),Val::Bool(true)));fun208.call(args206,kw207)?}.iter()? {
let unpack212=unpack(item186,2)?;e.set("label",unpack212[0].clone())?;e.set("reading",unpack212[1].clone())?;if {let v187=Val::Str("error".into());let v188=e.get("reading")?;Val::Bool(compare("in",v187.clone(),v188.clone())?.truthy()?)}.truthy()? {
anyhow::bail!("{}",val_string({let fun191=e.get("ValueError")?;let mut args189=Vec::new();let mut kw190=Vec::new();args189.push(e.get("reading")?.get(Val::Str("error".into()))?);fun191.call(args189,kw190)?})?);
}
let assigned192=e.get("guides")?.get(e.get("label")?)?;e.set("guide",assigned192.clone())?;
if {let v193=e.get("reading")?.get(Val::Str("kind".into()))?;let v194=Val::Str("common".into());Val::Bool(compare("eq",v193.clone(),v194.clone())?.truthy()?)}.truthy()? {
let assigned195={let fun198=e.get("max")?;let mut args196=Vec::new();let mut kw197=Vec::new();args196.push(e.get("guide")?.get(Val::Str("maximum_float_body_cap_overlap_mm3".into()))?);args196.push(e.get("reading")?.get(Val::Str("common".into()))?.get(Val::Str("raw".into()))?.get(Val::Str("volume_mm3".into()))?);fun198.call(args196,kw197)?};e.get("guide")?.set(Val::Str("maximum_float_body_cap_overlap_mm3".into()),assigned195.clone())?;
}else{
let assigned199={let fun202=e.get("min")?;let mut args200=Vec::new();let mut kw201=Vec::new();args200.push(e.get("guide")?.get(Val::Str("minimum_body_cap_distance_mm".into()))?);args200.push({let fun205=e.get("max")?;let mut args203=Vec::new();let mut kw204=Vec::new();args203.push(Val::Float(0.0f64));args203.push(e.get("reading")?.get(Val::Str("value".into()))?);fun205.call(args203,kw204)?});fun202.call(args200,kw201)?};e.get("guide")?.set(Val::Str("minimum_body_cap_distance_mm".into()),assigned199.clone())?;
}
}
for item213 in {let fun218=e.get("guides")?.attr("items")?;let mut args216=Vec::new();let mut kw217=Vec::new();fun218.call(args216,kw217)?}.iter()? {
let unpack219=unpack(item213,2)?;e.set("label",unpack219[0].clone())?;e.set("guide",unpack219[1].clone())?;if !{let v214=e.get("guide")?.get(Val::Str("maximum_float_body_cap_overlap_mm3".into()))?;let v215=Val::Float(1e-06f64);Val::Bool(compare("lt",v214.clone(),v215.clone())?.truthy()?)}.truthy()? {anyhow::bail!("{}",val_string({let mut s=Vec::new();s.push(e.get("label")?);s.push(e.get("guide")?.get(Val::Str("maximum_float_body_cap_overlap_mm3".into()))?);Val::tuple(s)})?);}
}
let assigned220=binary("add",e.get("bridge")?.attr("carbonator_outer_radius")?,binary("truediv",e.get("f")?.attr("reed_mount_diameter")?,Val::Int(2i64))?)?;e.set("carb_reed_axis",assigned220.clone())?;
let assigned221=e.get("reed_column_axis_x")?;e.set("reservoir_reed_axis",assigned221.clone())?;
let assigned222={let d=Val::dict(vec![]);d.set(Val::Str("carbonator".into()),{let fun225=e.get("f")?.attr("reed_edge_distance")?;let mut args223=Vec::new();let mut kw224=Vec::new();args223.push(binary("mul",e.get("cap")?.attr("register_radius")?,Val::Float(25.4f64))?);args223.push(e.get("carb_reed_axis")?);fun225.call(args223,kw224)?})?;d.set(Val::Str("reservoir".into()),{let fun228=e.get("f")?.attr("reed_edge_distance")?;let mut args226=Vec::new();let mut kw227=Vec::new();args226.push(e.get("res")?.attr("rod_position_x")?);args226.push(e.get("reservoir_reed_axis")?);fun228.call(args226,kw227)?})?;d};e.set("paths",assigned222.clone())?;
let assigned229={let d=Val::dict(vec![]);d.set(Val::Str("carbonator".into()),{let fun232=e.get("f")?.attr("reed_float_edge_distance")?;let mut args230=Vec::new();let mut kw231=Vec::new();args230.push(binary("mul",e.get("cap")?.attr("register_radius")?,Val::Float(25.4f64))?);args230.push(e.get("carb_reed_axis")?);fun232.call(args230,kw231)?})?;d.set(Val::Str("reservoir".into()),{let fun235=e.get("f")?.attr("reed_float_edge_distance")?;let mut args233=Vec::new();let mut kw234=Vec::new();args233.push(e.get("res")?.attr("rod_position_x")?);args233.push(e.get("reservoir_reed_axis")?);fun235.call(args233,kw234)?})?;d};e.set("float_paths",assigned229.clone())?;
if !{let fun238=e.get("all")?;let mut args236=Vec::new();let mut kw237=Vec::new();args236.push({let e=e.child();let out239=Val::list(vec![]);for item240 in {let fun243=e.get("float_paths")?.attr("values")?;let mut args241=Vec::new();let mut kw242=Vec::new();fun243.call(args241,kw242)?}.iter()? {e.set("x",item240)?;out239.attr("append")?.call(vec![{let v244=Val::Int(0i64);let v245=e.get("x")?;let v246=e.get("f")?.attr("float_edge_design_maximum")?;Val::Bool(compare("lt",v244.clone(),v245.clone())?.truthy()? && compare("le",v245.clone(),v246.clone())?.truthy()?)}],vec![])?;}out239});fun238.call(args236,kw237)?}.truthy()? {anyhow::bail!("{}",val_string(Val::Str("assertion failed".into()))?);}
if !{let fun249=e.get("all")?;let mut args247=Vec::new();let mut kw248=Vec::new();args247.push({let e=e.child();let out250=Val::list(vec![]);for item251 in {let fun254=e.get("float_paths")?.attr("items")?;let mut args252=Vec::new();let mut kw253=Vec::new();fun254.call(args252,kw253)?}.iter()? {let unpack255=unpack(item251,2)?;e.set("name",unpack255[0].clone())?;e.set("distance",unpack255[1].clone())?;out250.attr("append")?.call(vec![{let v259={let fun258=e.get("abs")?;let mut args256=Vec::new();let mut kw257=Vec::new();args256.push(binary("sub",binary("sub",e.get("paths")?.get(e.get("name")?)?,e.get("distance")?)?,e.get("f")?.attr("magnet_edge_inset")?)?);fun258.call(args256,kw257)?};let v260=Val::Float(1e-09f64);Val::Bool(compare("lt",v259.clone(),v260.clone())?.truthy()?)}],vec![])?;}out250});fun249.call(args247,kw248)?}.truthy()? {anyhow::bail!("{}",val_string(Val::Str("assertion failed".into()))?);}
for item261 in {let mut s=Vec::new();s.push(e.get("bridge")?.attr("reed_low_z")?);s.push(e.get("bridge")?.attr("reed_high_z")?);Val::tuple(s)}.iter()? {
e.set("z",item261)?;if !{let v262=e.get("bridge")?.attr("magnet_lowest_z")?;let v263=e.get("z")?;let v264=e.get("bridge")?.attr("magnet_highest_z")?;Val::Bool(compare("lt",v262.clone(),v263.clone())?.truthy()? && compare("lt",v263.clone(),v264.clone())?.truthy()?)}.truthy()? {anyhow::bail!("{}",val_string(Val::Str("assertion failed".into()))?);}
}
if !{let v268=e.get("res")?.attr("float_magnet_travel_z")?.get(Val::Int(0i64))?;let v269={let fun267=e.get("min")?;let mut args265=Vec::new();let mut kw266=Vec::new();args265.push(e.get("res")?.attr("reservoir_reed_centres_z")?);fun267.call(args265,kw266)?};Val::Bool(compare("lt",v268.clone(),v269.clone())?.truthy()?)}.truthy()? {anyhow::bail!("{}",val_string(Val::Str("assertion failed".into()))?);}
if !{let v273={let fun272=e.get("max")?;let mut args270=Vec::new();let mut kw271=Vec::new();args270.push(e.get("res")?.attr("reservoir_reed_centres_z")?);fun272.call(args270,kw271)?};let v274=e.get("res")?.attr("float_magnet_travel_z")?.get(Val::Int(1i64))?;Val::Bool(compare("lt",v273.clone(),v274.clone())?.truthy()?)}.truthy()? {anyhow::bail!("{}",val_string(Val::Str("assertion failed".into()))?);}
let assigned275={let d=Val::dict(vec![]);d.set(Val::Str("FLOAT_SIZE".into()),{let mut str276=String::new();str276.push_str(&format(&e.get("f")?.attr("diameter")?,&val_string({let mut str277=String::new();str277.push_str("g");Val::Str(str277)})?)?);str276.push_str(" × ");str276.push_str(&format(&e.get("f")?.attr("height")?,&val_string({let mut str278=String::new();str278.push_str("g");Val::Str(str278)})?)?);str276.push_str(" mm");Val::Str(str276)})?;d.set(Val::Str("FLOAT_BORE".into()),{let mut str279=String::new();str279.push_str(&format(&e.get("f")?.attr("bore_diameter")?,&val_string({let mut str280=String::new();str280.push_str("g");Val::Str(str280)})?)?);str279.push_str(" mm");Val::Str(str279)})?;d.set(Val::Str("MAGNET_CENTER".into()),{let mut str281=String::new();str281.push_str(&format(&e.get("f")?.attr("magnet_midplane")?,&val_string({let mut str282=String::new();str282.push_str("g");Val::Str(str282)})?)?);str281.push_str(" mm");Val::Str(str281)})?;d.set(Val::Str("ROD_DIAMETER".into()),{let mut str283=String::new();str283.push_str(&format(&e.get("f")?.attr("guide_diameter")?,&val_string({let mut str284=String::new();str284.push_str("g");Val::Str(str284)})?)?);str283.push_str(" mm");Val::Str(str283)})?;d.set(Val::Str("WALL_DATUM".into()),{let mut str285=String::new();str285.push_str(&format(&e.get("f")?.attr("rod_axis_from_inner_wall")?,&val_string({let mut str286=String::new();str286.push_str("g");Val::Str(str286)})?)?);str285.push_str(" mm");Val::Str(str285)})?;d.set(Val::Str("CARB_RADIUS".into()),{let mut str287=String::new();str287.push_str(&format(&binary("mul",e.get("cap")?.attr("register_radius")?,Val::Float(25.4f64))?,&val_string({let mut str288=String::new();str288.push_str(".3f");Val::Str(str288)})?)?);str287.push_str(" mm");Val::Str(str287)})?;d.set(Val::Str("CARB_RADIUS_IN".into()),{let mut str289=String::new();str289.push_str(&format(&e.get("cap")?.attr("register_radius")?,&val_string({let mut str290=String::new();str290.push_str(".4f");Val::Str(str290)})?)?);str289.push_str(" in");Val::Str(str289)})?;d.set(Val::Str("RES_X".into()),{let mut str291=String::new();str291.push_str(&format(&e.get("res")?.attr("rod_position_x")?,&val_string({let mut str292=String::new();str292.push_str(".2f");Val::Str(str292)})?)?);str291.push_str(" mm");Val::Str(str291)})?;d.set(Val::Str("RES_Y".into()),{let mut str293=String::new();str293.push_str(&format(&e.get("res")?.attr("rod_position_y")?,&val_string({let mut str294=String::new();str294.push_str("g");Val::Str(str294)})?)?);str293.push_str(" mm");Val::Str(str293)})?;d.set(Val::Str("CARB_ROD_LENGTH".into()),{let mut str295=String::new();str295.push_str(&format(&binary("truediv",e.get("pv")?.attr("carbonator_rod_len")?,Val::Float(25.4f64))?,&val_string({let mut str296=String::new();str296.push_str(".3f");Val::Str(str296)})?)?);str295.push_str(" ±");str295.push_str(&format(&binary("truediv",e.get("pv")?.attr("carbonator_rod_tolerance")?,Val::Float(25.4f64))?,&val_string({let mut str297=String::new();str297.push_str(".3f");Val::Str(str297)})?)?);str295.push_str(" in (");str295.push_str(&format(&e.get("pv")?.attr("carbonator_rod_len")?,&val_string({let mut str298=String::new();str298.push_str(".2f");Val::Str(str298)})?)?);str295.push_str(" ±");str295.push_str(&format(&e.get("pv")?.attr("carbonator_rod_tolerance")?,&val_string({let mut str299=String::new();str299.push_str(".2f");Val::Str(str299)})?)?);str295.push_str(" mm)");Val::Str(str295)})?;d.set(Val::Str("RES_ROD_LENGTH".into()),{let mut str300=String::new();str300.push_str(&format(&e.get("res")?.attr("reservoir_rod_len")?,&val_string({let mut str301=String::new();str301.push_str(".3f");Val::Str(str301)})?)?);str300.push_str(" mm");Val::Str(str300)})?;d.set(Val::Str("RES_ROD_CLEARANCE".into()),{let mut str302=String::new();str302.push_str(&format(&e.get("res")?.attr("reservoir_rod_clearance")?,&val_string({let mut str303=String::new();str303.push_str("g");Val::Str(str303)})?)?);str302.push_str(" mm");Val::Str(str302)})?;d.set(Val::Str("GUIDE_SLOP".into()),{let mut str304=String::new();str304.push_str(&format(&e.get("f")?.attr("guide_radial_clearance")?,&val_string({let mut str305=String::new();str305.push_str("g");Val::Str(str305)})?)?);str304.push_str(" mm");Val::Str(str304)})?;d.set(Val::Str("WALL_CLEARANCE".into()),{let mut str306=String::new();str306.push_str(&format(&e.get("f")?.attr("wall_clearance")?,&val_string({let mut str307=String::new();str307.push_str("g");Val::Str(str307)})?)?);str306.push_str(" mm");Val::Str(str306)})?;d.set(Val::Str("WALL_CLEARANCE_RANGE".into()),{let mut str308=String::new();str308.push_str(&format(&e.get("f")?.attr("minimum_wall_clearance")?,&val_string({let mut str309=String::new();str309.push_str("g");Val::Str(str309)})?)?);str308.push_str("–");str308.push_str(&format(&e.get("f")?.attr("maximum_wall_clearance")?,&val_string({let mut str310=String::new();str310.push_str("g");Val::Str(str310)})?)?);str308.push_str(" mm");Val::Str(str308)})?;d.set(Val::Str("CARB_REED_PATH".into()),{let mut str311=String::new();str311.push_str(&format(&e.get("paths")?.get(Val::Str("carbonator".into()))?,&val_string({let mut str312=String::new();str312.push_str(".3f");Val::Str(str312)})?)?);str311.push_str(" mm");Val::Str(str311)})?;d.set(Val::Str("RES_REED_PATH".into()),{let mut str313=String::new();str313.push_str(&format(&e.get("paths")?.get(Val::Str("reservoir".into()))?,&val_string({let mut str314=String::new();str314.push_str(".3f");Val::Str(str314)})?)?);str313.push_str(" mm");Val::Str(str313)})?;d.set(Val::Str("CARB_FLOAT_REED_PATH".into()),{let mut str315=String::new();str315.push_str(&format(&e.get("float_paths")?.get(Val::Str("carbonator".into()))?,&val_string({let mut str316=String::new();str316.push_str(".3f");Val::Str(str316)})?)?);str315.push_str(" mm");Val::Str(str315)})?;d.set(Val::Str("RES_FLOAT_REED_PATH".into()),{let mut str317=String::new();str317.push_str(&format(&e.get("float_paths")?.get(Val::Str("reservoir".into()))?,&val_string({let mut str318=String::new();str318.push_str(".3f");Val::Str(str318)})?)?);str317.push_str(" mm");Val::Str(str317)})?;d.set(Val::Str("FLOAT_REED_DESIGN_MAX".into()),{let mut str319=String::new();str319.push_str(&format(&e.get("f")?.attr("float_edge_design_maximum")?,&val_string({let mut str320=String::new();str320.push_str("g");Val::Str(str320)})?)?);str319.push_str(" mm");Val::Str(str319)})?;d.set(Val::Str("FLOAT_REED_REPORTED_LIMIT".into()),{let mut str321=String::new();str321.push_str(&format(&e.get("f")?.attr("float_edge_reported_usable_limit")?,&val_string({let mut str322=String::new();str322.push_str("g");Val::Str(str322)})?)?);str321.push_str(" mm");Val::Str(str321)})?;d.set(Val::Str("CARB_WATER_LEVELS".into()),{let mut str323=String::new();str323.push_str(&format(&e.get("bridge")?.attr("low_level_z")?,&val_string({let mut str324=String::new();str324.push_str(".3f");Val::Str(str324)})?)?);str323.push_str(" / ");str323.push_str(&format(&e.get("bridge")?.attr("high_level_z")?,&val_string({let mut str325=String::new();str325.push_str(".3f");Val::Str(str325)})?)?);str323.push_str(" mm");Val::Str(str323)})?;d.set(Val::Str("CARB_REED_CENTERS".into()),{let mut str326=String::new();str326.push_str(&format(&e.get("bridge")?.attr("reed_low_z")?,&val_string({let mut str327=String::new();str327.push_str(".3f");Val::Str(str327)})?)?);str326.push_str(" / ");str326.push_str(&format(&e.get("bridge")?.attr("reed_high_z")?,&val_string({let mut str328=String::new();str328.push_str(".3f");Val::Str(str328)})?)?);str326.push_str(" mm");Val::Str(str326)})?;d.set(Val::Str("CARB_TRAVEL".into()),{let mut str329=String::new();str329.push_str(&format(&e.get("bridge")?.attr("magnet_lowest_z")?,&val_string({let mut str330=String::new();str330.push_str(".3f");Val::Str(str330)})?)?);str329.push_str("–");str329.push_str(&format(&e.get("bridge")?.attr("magnet_highest_z")?,&val_string({let mut str331=String::new();str331.push_str(".3f");Val::Str(str331)})?)?);str329.push_str(" mm");Val::Str(str329)})?;d.set(Val::Str("RES_TRAVEL".into()),{let mut str332=String::new();str332.push_str(&format(&e.get("res")?.attr("float_magnet_travel_z")?.get(Val::Int(0i64))?,&val_string({let mut str333=String::new();str333.push_str(".3f");Val::Str(str333)})?)?);str332.push_str("–");str332.push_str(&format(&e.get("res")?.attr("float_magnet_travel_z")?.get(Val::Int(1i64))?,&val_string({let mut str334=String::new();str334.push_str(".3f");Val::Str(str334)})?)?);str332.push_str(" mm");Val::Str(str332)})?;d.set(Val::Str("RES_REED_CENTERS".into()),binary("add",{let fun337=Val::Str(", ".into()).attr("join")?;let mut args335=Vec::new();let mut kw336=Vec::new();args335.push({let e=e.child();let out338=Val::list(vec![]);for item339 in e.get("res")?.attr("reservoir_reed_centres_z")?.iter()? {e.set("z",item339)?;out338.attr("append")?.call(vec![{let mut str340=String::new();str340.push_str(&format(&e.get("z")?,&val_string({let mut str341=String::new();str341.push_str(".3f");Val::Str(str341)})?)?);Val::Str(str340)}],vec![])?;}out338});fun337.call(args335,kw336)?},Val::Str(" mm".into()))?)?;d.set(Val::Str("RES_REED_PITCH".into()),{let mut str342=String::new();str342.push_str(&format(&e.get("res")?.attr("reservoir_reed_pitch")?,&val_string({let mut str343=String::new();str343.push_str("g");Val::Str(str343)})?)?);str342.push_str(" mm");Val::Str(str342)})?;d.set(Val::Str("MAGNET_SUBMERGENCE".into()),{let mut str344=String::new();str344.push_str(&format(&unary("neg",{let fun347=e.get("f")?.attr("magnet_above_waterline")?;let mut args345=Vec::new();let mut kw346=Vec::new();fun347.call(args345,kw346)?})?,&val_string({let mut str348=String::new();str348.push_str(".3f");Val::Str(str348)})?)?);str344.push_str(" mm");Val::Str(str344)})?;d};e.set("facts",assigned275.clone())?;
e.set("inputs",binary("add",e.get("inputs")?,{let e=e.child();let out349=Val::list(vec![]);for item350 in {let fun353=e.get("tuple")?;let mut args351=Vec::new();let mut kw352=Vec::new();args351.push(e.get("inputs")?);fun353.call(args351,kw352)?}.iter()? {e.set("p",item350)?;if {let v360={let v361=e.get("p")?.attr("suffix")?;let v362=Val::Str(".step".into());Val::Bool(compare("eq",v361.clone(),v362.clone())?.truthy()?)};if v360.truthy()? {{let fun356={let fun359=e.get("p")?.attr("with_name")?;let mut args357=Vec::new();let mut kw358=Vec::new();args357.push(binary("add",e.get("p")?.attr("name")?,Val::Str(".npz".into()))?);fun359.call(args357,kw358)?}.attr("is_file")?;let mut args354=Vec::new();let mut kw355=Vec::new();fun356.call(args354,kw355)?}} else {v360}}.truthy()? {out349.attr("append")?.call(vec![{let fun365=e.get("p")?.attr("with_name")?;let mut args363=Vec::new();let mut kw364=Vec::new();args363.push(binary("add",e.get("p")?.attr("name")?,Val::Str(".npz".into()))?);fun365.call(args363,kw364)?}],vec![])?;}}out349})?)?;
let assigned366={let d=Val::dict(vec![]);d.set(Val::Str("status".into()),Val::Str("geometric_datums_and_upright_sweep_pass".into()))?;d.set(Val::Str("float_cad_revision".into()),Val::Str("v2-upper-clearance".into()))?;d.set(Val::Str("float_dimensions_mm".into()),{let mut s=Vec::new();s.push(e.get("f")?.attr("diameter")?);s.push(e.get("f")?.attr("height")?);s.push(e.get("f")?.attr("bore_diameter")?);Val::list(s)})?;d.set(Val::Str("rod_axis_from_inside_wall_mm".into()),e.get("f")?.attr("rod_axis_from_inner_wall")?)?;d.set(Val::Str("carbonator_register_xy_mm".into()),{let fun369=e.get("list")?;let mut args367=Vec::new();let mut kw368=Vec::new();args367.push({let e=e.child();let out370=Val::list(vec![]);for item371 in e.get("cap")?.attr("register_position")?.iter()? {e.set("x",item371)?;out370.attr("append")?.call(vec![binary("mul",e.get("x")?,Val::Float(25.4f64))?],vec![])?;}out370});fun369.call(args367,kw368)?})?;d.set(Val::Str("carbonator_upright_wall_clearance_range_mm".into()),{let mut s=Vec::new();s.push(e.get("f")?.attr("minimum_wall_clearance")?);s.push(e.get("f")?.attr("maximum_wall_clearance")?);Val::list(s)})?;d.set(Val::Str("reservoirs".into()),e.get("guides")?)?;d.set(Val::Str("maximum_reed_center_to_nearest_rc62_edge_mm".into()),e.get("paths")?)?;d.set(Val::Str("maximum_float_edge_to_reed_center_mm".into()),e.get("float_paths")?)?;d.set(Val::Str("design_maximum_float_edge_to_reed_center_mm".into()),e.get("f")?.attr("float_edge_design_maximum")?)?;d.set(Val::Str("reported_usable_float_edge_to_reed_center_mm".into()),e.get("f")?.attr("float_edge_reported_usable_limit")?)?;d.set(Val::Str("radial_signal_evidence".into()),e.get("f")?.attr("float_edge_evidence")?)?;d.set(Val::Str("bare_rc62_bench_reference_magnet_edge_distance_mm".into()),e.get("f")?.attr("bench_edge_distance")?)?;d.set(Val::Str("reed_centers".into()),Val::Str("provisional geometry; installed directional liquid calibration pending".into()))?;d.set(Val::Str("scope".into()),Val::Str("Nominal upright CAD and horizontal bore play only; no foam expansion, tilted motion, installed switching, pressure, lifetime or wetted acceptance.".into()))?;d.set(Val::Str("files_sha256".into()),{let e=e.child();let out372=Val::dict(vec![]);for item373 in e.get("inputs")?.iter()? {e.set("p",item373)?;out372.set({let fun376=e.get("str")?;let mut args374=Vec::new();let mut kw375=Vec::new();args374.push({let fun379=e.get("p")?.attr("relative_to")?;let mut args377=Vec::new();let mut kw378=Vec::new();args377.push(e.get("ROOT")?);fun379.call(args377,kw378)?});fun376.call(args374,kw375)?},{let fun382=e.get("digest")?;let mut args380=Vec::new();let mut kw381=Vec::new();args380.push(e.get("p")?);fun382.call(args380,kw381)?})?;}out372})?;d};e.set("record",assigned366.clone())?;
{let fun385=binary("truediv",e.get("HERE")?,Val::Str("integration-check.json".into()))?.attr("write_text")?;let mut args383=Vec::new();let mut kw384=Vec::new();args383.push(binary("add",{let fun388=e.get("json")?.attr("dumps")?;let mut args386=Vec::new();let mut kw387=Vec::new();args386.push(e.get("record")?);kw387.push(("indent".into(),Val::Int(2i64)));fun388.call(args386,kw387)?},Val::Str("\n".into()))?);fun385.call(args383,kw384)?};
{let fun391=e.get("substitute_md")?;let mut args389=Vec::new();let mut kw390=Vec::new();args389.push(binary("truediv",e.get("HERE")?,Val::Str("installation.md".into()))?);kw390.push(("variables".into(),e.get("facts")?));fun391.call(args389,kw390)?};
{let fun394=e.get("print")?;let mut args392=Vec::new();let mut kw393=Vec::new();args392.push({let fun397=e.get("json")?.attr("dumps")?;let mut args395=Vec::new();let mut kw396=Vec::new();args395.push({let d=Val::dict(vec![]);d.set(Val::Str("reservoirs".into()),e.get("guides")?)?;d.set(Val::Str("rc62_edge_to_reed_center_mm".into()),e.get("paths")?)?;d.set(Val::Str("float_edge_to_reed_center_mm".into()),e.get("float_paths")?)?;d.set(Val::Str("design_maximum_float_edge_to_reed_center_mm".into()),e.get("f")?.attr("float_edge_design_maximum")?)?;d});kw396.push(("indent".into(),Val::Int(2i64)));fun397.call(args395,kw396)?});fun394.call(args392,kw393)?};
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun400 = e.get("_rust_part")?.attr("start")?;
        let mut args398 = Vec::new();
        let mut kw399 = Vec::new();
        fun400.call(args398, kw399)?
    };
    {
        let fun403 = e.get("main")?;
        let mut args401 = Vec::new();
        let mut kw402 = Vec::new();
        fun403.call(args401, kw402)?
    };
    Ok(Val::None)
}
