#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("_cold_core_interface")?;
    e.set(
        "front_wall_x",
        rt.member("_cold_core_interface", "front_wall_x")?,
    )?;
    e.set(
        "port_lane_mid_y",
        rt.member("_cold_core_interface", "port_lane_mid_y")?,
    )?;
    e.set(
        "west_lane_mid_y",
        rt.member("_cold_core_interface", "west_lane_mid_y")?,
    )?;
    let assigned2 = Val::Float(6.35f64);
    e.set("copper_outer_diameter", assigned2.clone())?;
    let assigned3 = Val::Float(3.75f64);
    e.set("hole_radius", assigned3.clone())?;
    let assigned4 = Val::Float(28.425f64);
    e.set("evap_cross_z", assigned4.clone())?;
    // stations
    e.set("stations", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("evap-inlet".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("front_wall_x")?);
                        s.push(e.get("port_lane_mid_y")?);
                        s.push(e.get("evap_cross_z")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Float(1.0f64))?);
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                })?;
                d.set(Val::Str("evap-outlet".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("front_wall_x")?);
                        s.push(e.get("west_lane_mid_y")?);
                        s.push(e.get("evap_cross_z")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Float(1.0f64))?);
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // station
    e.set("station", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun7 = e.get("stations")?;
                let mut args5 = Vec::new();
                let mut kw6 = Vec::new();
                fun7.call(args5, kw6)?
            }
            .get(e.get("name")?)?);
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
