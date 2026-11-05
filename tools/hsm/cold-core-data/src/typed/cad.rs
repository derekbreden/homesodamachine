//! CadQuery and OCP, the library the recipes build solids with. Shapes, workplanes and
//! vectors stay opaque handles in the Python process; the recipes compute every number
//! they pass.

use super::*;

pub struct Cq {
    pub m: Val,
}

impl Cq {
    pub fn new(rt: &Runtime) -> Result<Self> {
        Ok(Self {
            m: rt.py("cadquery")?,
        })
    }
    /// `cq.Vector(x, y, z)`.
    pub fn vector(&self, p: [f64; 3]) -> Result<Val> {
        self.m.a("Vector")?.c(args![p[0], p[1], p[2]])
    }
    /// `cq.Vector(*values)` from any Python sequence.
    pub fn vector_of(&self, values: &Val) -> Result<Val> {
        self.m.a("Vector")?.c(values.list()?)
    }
    /// `cq.Solid.<method>(*args)`.
    pub fn solid(&self, method: &str, args: Vec<Val>) -> Result<Val> {
        self.m.a("Solid")?.m(method, args)
    }
    pub fn solid_k(&self, method: &str, args: Vec<Val>, kwargs: Vec<(String, Val)>) -> Result<Val> {
        self.m.a("Solid")?.mk(method, args, kwargs)
    }
    /// `cq.Solid.makeBox(dx, dy, dz, cq.Vector(*origin))`.
    pub fn make_box(&self, size: [f64; 3], origin: [f64; 3]) -> Result<Val> {
        self.solid(
            "makeBox",
            args![size[0], size[1], size[2], self.vector(origin)?],
        )
    }
    /// `cq.Solid.makeCylinder(radius, height, cq.Vector(*base), cq.Vector(*axis))`.
    pub fn cylinder(&self, radius: f64, height: f64, base: [f64; 3], axis: [f64; 3]) -> Result<Val> {
        self.solid(
            "makeCylinder",
            args![radius, height, self.vector(base)?, self.vector(axis)?],
        )
    }
    /// `cq.Solid.makeCylinder(radius, height, cq.Vector(*base))`.
    pub fn cylinder_z(&self, radius: f64, height: f64, base: [f64; 3]) -> Result<Val> {
        self.solid("makeCylinder", args![radius, height, self.vector(base)?])
    }
    /// `cq.Workplane(*args, **kwargs)`.
    pub fn workplane(&self, args: Vec<Val>, kwargs: Vec<(String, Val)>) -> Result<Val> {
        self.m.a("Workplane")?.ck(args, kwargs)
    }
    /// `cq.Plane(**kwargs)`.
    pub fn plane(&self, kwargs: Vec<(String, Val)>) -> Result<Val> {
        self.m.a("Plane")?.ck(vec![], kwargs)
    }
    /// `cq.<class>.<method>(*args, **kwargs)`.
    pub fn class(
        &self,
        class: &str,
        method: &str,
        args: Vec<Val>,
        kwargs: Vec<(String, Val)>,
    ) -> Result<Val> {
        self.m.a(class)?.mk(method, args, kwargs)
    }
    /// `cq.Wire.makePolygon([cq.Vector(*p) for p in points], close=True)`.
    pub fn polygon(&self, points: &[[f64; 3]]) -> Result<Val> {
        let vectors = points
            .iter()
            .map(|p| self.vector(*p))
            .collect::<Result<Vec<_>>>()?;
        self.class(
            "Wire",
            "makePolygon",
            vec![Val::list(vectors)],
            kw!["close" => true],
        )
    }
    /// `cq.Solid.makeLoft(profiles, ruled=True)`.
    pub fn ruled_loft(&self, profiles: Vec<Val>) -> Result<Val> {
        self.solid_k("makeLoft", vec![Val::list(profiles)], kw!["ruled" => true])
    }
}

/// `shape.<method>(*args)` on a CadQuery object.
pub fn on(shape: &Val, method: &str, args: Vec<Val>) -> Result<Val> {
    shape.m(method, args)
}
/// `shape.cut(*tools)`.
pub fn cut(shape: &Val, tools: Vec<Val>) -> Result<Val> {
    shape.m("cut", tools)
}
/// `shape.fuse(*tools)`.
pub fn fuse(shape: &Val, tools: Vec<Val>) -> Result<Val> {
    shape.m("fuse", tools)
}
/// `shape.clean()`.
pub fn clean(shape: &Val) -> Result<Val> {
    shape.m("clean", vec![])
}
/// `shape.translate(v)`.
pub fn translate(shape: &Val, v: [f64; 3]) -> Result<Val> {
    shape.m("translate", args![v])
}
/// `shape.rotate(a, b, angle)`.
pub fn rotate(shape: &Val, a: [f64; 3], b: [f64; 3], angle: f64) -> Result<Val> {
    shape.m("rotate", args![a, b, angle])
}
/// `shape.moved(location)`.
pub fn moved(shape: &Val, location: &Val) -> Result<Val> {
    shape.m("moved", args![location])
}
