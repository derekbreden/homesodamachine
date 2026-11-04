#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
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
    if {
        let v20 = {
            let fun19 = e.get("str")?;
            let mut args17 = Vec::new();
            let mut kw18 = Vec::new();
            args17.push(binary(
                "truediv",
                e.get("_hw")?,
                Val::Str("scripts".into()),
            )?);
            fun19.call(args17, kw18)?
        };
        let v21 = e.get("sys")?.attr("path")?;
        Val::Bool(compare("not_in", v20.clone(), v21.clone())?.truthy()?)
    }
    .truthy()?
    {
        {
            let fun24 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args22 = Vec::new();
            let mut kw23 = Vec::new();
            args22.push(Val::Int(0i64));
            args22.push({
                let fun27 = e.get("str")?;
                let mut args25 = Vec::new();
                let mut kw26 = Vec::new();
                args25.push(binary(
                    "truediv",
                    e.get("_hw")?,
                    Val::Str("scripts".into()),
                )?);
                fun27.call(args25, kw26)?
            });
            fun24.call(args22, kw23)?
        };
    }
    e.set("_mat", rt.import_module("_materials")?)?;
    e.set("_routing", rt.import_module("_routing")?)?;
    let assigned28 = {
        let d = Val::dict(vec![]);
        d.set(
            Val::Str("foam-shell".into()),
            e.get("_mat")?.attr("C_FOAM_SHELL")?,
        )?;
        d.set(
            Val::Str("foam-cap-lid-top".into()),
            e.get("_mat")?.attr("C_CAP_LID_TOP")?,
        )?;
        d.set(
            Val::Str("foam-cap-bottom".into()),
            e.get("_mat")?.attr("C_CAP_BOTTOM")?,
        )?;
        d
    };
    e.set("FOAM_COLORS", assigned28.clone())?;
    let assigned29 = {
        let d = Val::dict(vec![]);
        d.set(Val::Str("water-in".into()), Val::Str("white".into()))?;
        d.set(Val::Str("carb-water-out".into()), Val::Str("blue".into()))?;
        d.set(Val::Str("co2-in".into()), Val::Str("red".into()))?;
        d.set(Val::Str("prv-vent".into()), Val::Str("black".into()))?;
        d.set(Val::Str("reservoir-a".into()), Val::Str("black".into()))?;
        d.set(
            Val::Str("reservoir-a-fill".into()),
            Val::Str("black".into()),
        )?;
        d.set(Val::Str("reservoir-b".into()), Val::Str("black".into()))?;
        d.set(
            Val::Str("reservoir-b-fill".into()),
            Val::Str("black".into()),
        )?;
        d
    };
    e.set("ROUTE_SPOOLS", assigned29.clone())?;
    let assigned30 = {
        let e = e.child();
        let out31 = Val::dict(vec![]);
        for item32 in {
            let fun35 = e.get("ROUTE_SPOOLS")?.attr("items")?;
            let mut args33 = Vec::new();
            let mut kw34 = Vec::new();
            fun35.call(args33, kw34)?
        }
        .iter()?
        {
            let unpack36 = unpack(item32, 2)?;
            e.set("name", unpack36[0].clone())?;
            e.set("spool", unpack36[1].clone())?;
            out31.set(e.get("name")?, {
                let fun39 = e.get("_routing")?.attr("color")?;
                let mut args37 = Vec::new();
                let mut kw38 = Vec::new();
                args37.push(e.get("spool")?);
                fun39.call(args37, kw38)?
            })?;
        }
        out31
    };
    e.set("ROUTE_COLORS", assigned30.clone())?;
    // colour_for
    e.set("colour_for", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v40 = e.get("name")?;
                let v41 = Val::Str("digiten-flow".into());
                Val::Bool(compare("eq", v40.clone(), v41.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("C_DIGITEN")?);
            }
            if {
                let v42 = e.get("name")?;
                let v43 = Val::Str("reservoir-b-fill-guide".into());
                Val::Bool(compare("eq", v42.clone(), v43.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("M_PETGF_BLACK")?);
            }
            if {
                let fun46 = e.get("name")?.attr("startswith")?;
                let mut args44 = Vec::new();
                let mut kw45 = Vec::new();
                args44.push(Val::Str("cap-clamp-".into()));
                fun46.call(args44, kw45)?
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("M_DONOR_BLACK")?);
            }
            if {
                let v47 = e.get("name")?;
                let v48 = Val::Str("soda-bend-holder".into());
                Val::Bool(compare("eq", v47.clone(), v48.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("M_PETGF_BLACK")?);
            }
            if {
                let v49 = e.get("name")?;
                let v50 = Val::Str("soda-continuous-insulation".into());
                Val::Bool(compare("eq", v49.clone(), v50.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("M_NITRILE_BLACK")?);
            }
            if {
                let fun53 = e.get("name")?.attr("startswith")?;
                let mut args51 = Vec::new();
                let mut kw52 = Vec::new();
                args51.push(Val::Str("tube-soda-core-".into()));
                fun53.call(args51, kw52)?
            }
            .truthy()?
            {
                return Ok({
                    let fun56 = e.get("_routing")?.attr("color")?;
                    let mut args54 = Vec::new();
                    let mut kw55 = Vec::new();
                    args54.push(Val::Str("blue".into()));
                    fun56.call(args54, kw55)?
                });
            }
            if {
                let fun59 = e.get("name")?.attr("startswith")?;
                let mut args57 = Vec::new();
                let mut kw58 = Vec::new();
                args57.push(Val::Str("line-".into()));
                fun59.call(args57, kw58)?
            }
            .truthy()?
            {
                let assigned60 = {
                    let fun63 = e.get("name")?.attr("removeprefix")?;
                    let mut args61 = Vec::new();
                    let mut kw62 = Vec::new();
                    args61.push(Val::Str("line-".into()));
                    fun63.call(args61, kw62)?
                };
                e.set("route", assigned60.clone())?;
                let attempt64 = (|| -> Result<Flow> {
                    return Ok(Flow::Return(e.get("ROUTE_COLORS")?.get(e.get("route")?)?));
                    Ok(Flow::Continue)
                })();
                let outcome65 = (|| -> Result<Flow> {
                    match attempt64 {
                        Ok(flow @ (Flow::Return(_) | Flow::Break | Flow::Next)) => Ok(flow),
                        Ok(Flow::Continue) => Ok(Flow::Continue),
                        Err(error) => {
                            e.set("exc", Val::Str(error.to_string()))?;
                            anyhow::bail!(
                                "{}",
                                val_string({
                                    let fun68 = e.get("KeyError")?;
                                    let mut args66 = Vec::new();
                                    let mut kw67 = Vec::new();
                                    args66.push({
                                        let mut str69 = String::new();
                                        str69.push_str(&format(
                                            &builtin_call("repr", vec![e.get("name")?], vec![])?,
                                            &String::new(),
                                        )?);
                                        str69.push_str(": no cold-core route colour");
                                        Val::Str(str69)
                                    });
                                    fun68.call(args66, kw67)?
                                })?
                            );
                            Ok(Flow::Continue)
                        }
                    }
                })();
                match outcome65? {
                    Flow::Continue => {}
                    Flow::Return(value) => return Ok(value),
                    Flow::Break => anyhow::bail!("break outside a loop"),
                    Flow::Next => anyhow::bail!("continue outside a loop"),
                }
            }
            if {
                let v70 = e.get("name")?;
                let v71 = e.get("FOAM_COLORS")?;
                Val::Bool(compare("in", v70.clone(), v71.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("FOAM_COLORS")?.get(e.get("name")?)?);
            }
            if {
                let v72 = e.get("name")?;
                let v73 = Val::Str("reed-bridge".into());
                Val::Bool(compare("eq", v72.clone(), v73.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("M_PETG_BLACK")?);
            }
            if {
                let v74 = e.get("name")?;
                let v75 = Val::Str("prv-shroud".into());
                Val::Bool(compare("eq", v74.clone(), v75.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("C_SHROUD")?);
            }
            if {
                let v76 = e.get("name")?;
                let v77 = Val::Str("prv-sv125".into());
                Val::Bool(compare("eq", v76.clone(), v77.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("M_BRASS")?);
            }
            if {
                let fun80 = e.get("name")?.attr("startswith")?;
                let mut args78 = Vec::new();
                let mut kw79 = Vec::new();
                args78.push(Val::Str("endcap".into()));
                fun80.call(args78, kw79)?
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("M_STAINLESS")?);
            }
            if {
                let v81 = e.get("name")?;
                let v82 = {
                    let mut s = Vec::new();
                    s.push(Val::Str("carbonator-elbow-co2-in".into()));
                    s.push(Val::Str("carbonator-elbow-carb-water-out".into()));
                    Val::tuple(s)
                };
                Val::Bool(compare("in", v81.clone(), v82.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("M_NEOFIT_ACETAL")?);
            }
            if {
                let fun85 = e.get("name")?.attr("startswith")?;
                let mut args83 = Vec::new();
                let mut kw84 = Vec::new();
                args83.push(Val::Str("carbonator-elbow".into()));
                fun85.call(args83, kw84)?
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("M_STAINLESS")?);
            }
            if {
                let fun88 = e.get("name")?.attr("startswith")?;
                let mut args86 = Vec::new();
                let mut kw87 = Vec::new();
                args86.push(Val::Str("collet-".into()));
                fun88.call(args86, kw87)?
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("M_JG_BLACK_PP")?);
            }
            if {
                let fun91 = e.get("name")?.attr("endswith")?;
                let mut args89 = Vec::new();
                let mut kw90 = Vec::new();
                args89.push(Val::Str("-gasket".into()));
                fun91.call(args89, kw90)?
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("C_SILICONE")?);
            }
            if {
                let fun94 = e.get("name")?.attr("endswith")?;
                let mut args92 = Vec::new();
                let mut kw93 = Vec::new();
                args92.push(Val::Str("-cap".into()));
                fun94.call(args92, kw93)?
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("C_RES_CAP")?);
            }
            if {
                let fun97 = e.get("name")?.attr("startswith")?;
                let mut args95 = Vec::new();
                let mut kw96 = Vec::new();
                args95.push(Val::Str("reservoir-grip-".into()));
                fun97.call(args95, kw96)?
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("M_TPU_BLACK")?);
            }
            if {
                let fun100 = e.get("name")?.attr("startswith")?;
                let mut args98 = Vec::new();
                let mut kw99 = Vec::new();
                args98.push(Val::Str("tube-reservoir-air-".into()));
                fun100.call(args98, kw99)?
            }
            .truthy()?
            {
                return Ok({
                    let fun103 = e.get("_routing")?.attr("color")?;
                    let mut args101 = Vec::new();
                    let mut kw102 = Vec::new();
                    args101.push(Val::Str("drain-white".into()));
                    fun103.call(args101, kw102)?
                });
            }
            if {
                let fun106 = e.get("name")?.attr("startswith")?;
                let mut args104 = Vec::new();
                let mut kw105 = Vec::new();
                args104.push(Val::Str("reservoir".into()));
                fun106.call(args104, kw105)?
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("C_RESERVOIR")?);
            }
            if {
                let fun109 = e.get("name")?.attr("startswith")?;
                let mut args107 = Vec::new();
                let mut kw108 = Vec::new();
                args107.push(Val::Str("evap-".into()));
                fun109.call(args107, kw108)?
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("M_COPPER")?);
            }
            if {
                let fun112 = e.get("name")?.attr("startswith")?;
                let mut args110 = Vec::new();
                let mut kw111 = Vec::new();
                args110.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("float-rod".into()));
                    s.push(Val::Str("float-stop".into()));
                    Val::tuple(s)
                });
                fun112.call(args110, kw111)?
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("M_STAINLESS")?);
            }
            if {
                let fun115 = e.get("name")?.attr("startswith")?;
                let mut args113 = Vec::new();
                let mut kw114 = Vec::new();
                args113.push(Val::Str("float-".into()));
                fun115.call(args113, kw114)?
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("M_ASA_AERO_WHITE")?);
            }
            if {
                let fun118 = e.get("name")?.attr("startswith")?;
                let mut args116 = Vec::new();
                let mut kw117 = Vec::new();
                args116.push(Val::Str("reed-".into()));
                fun118.call(args116, kw117)?
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("C_REED")?);
            }
            if {
                let fun121 = e.get("name")?.attr("startswith")?;
                let mut args119 = Vec::new();
                let mut kw120 = Vec::new();
                args119.push(Val::Str("probe-".into()));
                fun121.call(args119, kw120)?
            }
            .truthy()?
            {
                return Ok(e.get("_mat")?.attr("M_EPOXY_BLACK")?);
            }
            return Ok(e.get("_mat")?.attr("M_STAINLESS")?);
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
