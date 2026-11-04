use anyhow::{Context,Result};
use hsm_kernel::V3;
use serde_json::{Value,json};
pub fn number(v:&Value)->Result<f64>{
    if v["_hsm_float"].as_str()==Some("inf"){return Ok(f64::INFINITY)}
    if v["_hsm_float"].as_str()==Some("-inf"){return Ok(f64::NEG_INFINITY)}
    if v["_hsm_float"].as_str()==Some("nan"){return Ok(f64::NAN)}
    v.as_f64().or_else(||v.as_str().and_then(|s|s.parse().ok())).context("expected a number")
}
pub fn fvalue(v:f64)->Value{if v.is_finite(){json!(v)}else{json!({"_hsm_float":if v.is_nan(){"nan"}else if v.is_sign_negative(){"-inf"}else{"inf"}})}}
pub fn point(v:&Value)->Result<V3>{Ok(V3::from([number(&v[0])?,number(&v[1])?,number(&v[2])?]))}
pub fn points(v:&Value)->Result<Vec<V3>>{v.as_array().context("expected points")?.iter().map(point).collect()}
pub fn row(p:V3)->Value{json!([p.x,p.y,p.z])}
pub fn rows(p:&[V3])->Value{json!(p.iter().copied().map(row).collect::<Vec<_>>())}
pub fn text(v:&Value)->&str{v.as_str().unwrap_or("")}
pub fn array(v:&Value)->&[Value]{v.as_array().map(Vec::as_slice).unwrap_or(&[])}
pub fn format(v:f64,spec:&str)->String{hsm_documents::format_number(v,spec).expect("authored numeric format")}
pub fn py_tuple(p:V3,places:usize)->String{
    let values=[p.x,p.y,p.z].map(|v|{let s=format(v,&format!(".{places}f"));let v=s.parse::<f64>().unwrap();let s=v.to_string();if !s.contains(['.','e','E']){format!("{s}.0")}else{s}});format!("({})",values.join(", "))
}
