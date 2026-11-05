//! Tuple arithmetic for source-frame numbers; native builders retain their vectors.

use super::*;

pub fn add(a: &[f64], b: &[f64]) -> Vec<f64> {
    a.iter().zip(b).map(|(x, y)| x + y).collect()
}
pub fn sub(a: &[f64], b: &[f64]) -> Vec<f64> {
    a.iter().zip(b).map(|(x, y)| x - y).collect()
}
pub fn scale(a: &[f64], factor: f64) -> Vec<f64> {
    a.iter().map(|x| x * factor).collect()
}
pub fn unit(a: &[f64]) -> Vec<f64> {
    scale(a, 1.0 / fsum(a.iter().map(|x| x * x)).sqrt())
}
pub fn dot(a: &[f64], b: &[f64]) -> f64 {
    fsum(a.iter().zip(b).map(|(x, y)| x * y))
}
pub fn cross(a: &[f64], b: &[f64]) -> Vec<f64> {
    vec![
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}
pub fn turned(vector: &[f64], axis: &[f64], radians: f64) -> Vec<f64> {
    let (c, s) = (radians.cos(), radians.sin());
    add(
        &add(&scale(vector, c), &scale(&cross(axis, vector), s)),
        &scale(axis, dot(axis, vector) * (1.0 - c)),
    )
}

fn numbers(call: &mut Call, index: usize, name: &str) -> Result<Vec<f64>> {
    let value: Val = call.req(index, name)?;
    value.floats()
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    ns.module(rt, "math", "math")?;
    ns.func(rt, "add", |_, c| {
        Ok(tuple(&add(&numbers(c, 0, "a")?, &numbers(c, 1, "b")?)))
    });
    ns.func(rt, "sub", |_, c| {
        Ok(tuple(&sub(&numbers(c, 0, "a")?, &numbers(c, 1, "b")?)))
    });
    ns.func(rt, "scale", |_, c| {
        let a = numbers(c, 0, "a")?;
        Ok(tuple(&scale(&a, c.req(1, "factor")?)))
    });
    ns.func(rt, "unit", |_, c| Ok(tuple(&unit(&numbers(c, 0, "a")?))));
    ns.func(rt, "dot", |_, c| {
        Ok(Val::Float(dot(&numbers(c, 0, "a")?, &numbers(c, 1, "b")?)))
    });
    ns.func(rt, "cross", |_, c| {
        Ok(tuple(&cross(&numbers(c, 0, "a")?, &numbers(c, 1, "b")?)))
    });
    ns.func(rt, "turned", |_, c| {
        let vector = numbers(c, 0, "vector")?;
        let axis = numbers(c, 1, "axis")?;
        Ok(tuple(&turned(&vector, &axis, c.req(2, "radians")?)))
    });
    Ok(())
}

pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
