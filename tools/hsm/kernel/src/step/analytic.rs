//! Analytic manufacturing STEP for round stock with disjoint axial bores.
//!
//! The stock stands from Z=0 to `height`. A bore enters its +Z face and stops at
//! `floor`; zero makes a through bore. The STEP uses planes, cylinders, circles
//! and a closed B-rep. The fine model uses the kernel's ordinary mesh builders.
use super::{Entities, colour, product, string};
use crate::{Loop, Plane, Profile, Solid, V2, V3, v3};
use anyhow::{Result, ensure};

/// A straight bore from the stock's +Z face down to `floor`.
#[derive(Clone, Copy, Debug)]
pub struct AxialBore {
    pub center: V2,
    pub radius: f64,
    pub floor: f64,
}

/// Round stock whose axial bores are separate and strictly inside its rim.
#[derive(Clone, Debug)]
pub struct RoundStock {
    pub radius: f64,
    pub height: f64,
    pub bores: Vec<AxialBore>,
}

impl RoundStock {
    fn validate(&self) -> Result<()> {
        ensure!(self.radius.is_finite() && self.radius > 0.0, "round stock needs a positive finite radius");
        ensure!(self.height.is_finite() && self.height > 0.0, "round stock needs a positive finite height");
        for (i, bore) in self.bores.iter().enumerate() {
            ensure!(bore.center.x.is_finite() && bore.center.y.is_finite(), "bore {i} needs a finite centre");
            ensure!(bore.radius.is_finite() && bore.radius > 0.0, "bore {i} needs a positive finite radius");
            ensure!(bore.floor.is_finite() && bore.floor >= 0.0 && bore.floor < self.height, "bore {i} floor must be within the stock");
            ensure!(bore.center.norm() + bore.radius < self.radius, "bore {i} must be strictly inside the rim");
            for other in &self.bores[..i] {
                ensure!((bore.center - other.center).norm() > bore.radius + other.radius, "axial bores must be separate");
            }
        }
        Ok(())
    }

    /// The fine model, cut with the kernel's existing builders and tessellation rule.
    #[track_caller]
    pub fn solid(&self) -> Result<Solid> {
        self.validate()?;
        let mut profile = Profile::circle(V2::ZERO, self.radius);
        for bore in self.bores.iter().filter(|b| b.floor == 0.0) {
            profile = profile.with_hole(Loop::circle(bore.center, bore.radius));
        }
        let mut solid = Plane::XY.extrude(&profile, self.height)?;
        for bore in self.bores.iter().filter(|b| b.floor > 0.0) {
            let tool = Solid::cylinder(
                v3(bore.center.x, bore.center.y, bore.floor), V3::Z,
                bore.radius, self.height - bore.floor + 1.0,
            )?;
            solid = solid.cut(&tool)?;
        }
        Ok(solid)
    }

    /// A single named, coloured manufacturing solid in millimetres.
    ///
    /// All faces are exact cylinders or planes. This supports only the stock
    /// and separate through/blind bores this type describes.
    pub fn step_bytes(&self, name: &str, color: Option<[f64; 3]>) -> Result<Vec<u8>> {
        self.validate()?;
        let mut e = Entities { text: String::new(), next: 1 };
        e.add("APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#2)");
        let app = e.add("APPLICATION_CONTEXT('core data for automotive mechanical design processes')");
        let mm = e.add("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))");
        let angle = e.add("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))");
        let solid_angle = e.add("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())");
        let uncertainty = e.add(format!("UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),{mm},'distance_accuracy_value','confusion accuracy')"));
        let context = e.add(format!("(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT(({uncertainty}))GLOBAL_UNIT_ASSIGNED_CONTEXT(({mm},{angle},{solid_angle}))REPRESENTATION_CONTEXT('Context #1','3D Context with UNIT and UNCERTAINTY'))"));
        let origin = axis(&mut e, 0.0, 0.0, 0.0);
        let outer = wall(&mut e, V2::ZERO, self.radius, 0.0, self.height, true);
        let bores: Vec<Wall> = self.bores.iter().map(|b| wall(&mut e, b.center, b.radius, b.floor, self.height, false)).collect();
        let mut faces = outer.faces.to_vec();
        for bore in &bores {
            faces.extend(bore.faces.iter().cloned());
        }
        let bottom: Vec<&Ring> = bores.iter().zip(&self.bores).filter(|(_, b)| b.floor == 0.0).map(|(w, _)| &w.lower).collect();
        let top: Vec<&Ring> = bores.iter().map(|w| &w.upper).collect();
        faces.push(plane(&mut e, &outer.lower, &bottom, 0.0, false));
        faces.push(plane(&mut e, &outer.upper, &top, self.height, true));
        for (wall, bore) in bores.iter().zip(&self.bores) {
            if bore.floor > 0.0 {
                faces.push(plane(&mut e, &wall.lower, &[], bore.floor, true));
            }
        }
        let shell = e.add(format!("CLOSED_SHELL('',({}))", faces.join(",")));
        let solid = e.add(format!("MANIFOLD_SOLID_BREP({},{shell})", string(name)));
        let shape = e.add(format!("ADVANCED_BREP_SHAPE_REPRESENTATION('',({origin},{solid}),{context})"));
        let p = product(&mut e, &app, name, &shape);
        e.add(format!("PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,({}))", p.product));
        if let Some(rgb) = color {
            let c = e.add(format!("COLOUR_RGB('',{},{},{})", colour(rgb[0]), colour(rgb[1]), colour(rgb[2])));
            let fill = e.add(format!("FILL_AREA_STYLE_COLOUR('',{c})"));
            let area = e.add(format!("FILL_AREA_STYLE('',({fill}))"));
            let filled = e.add(format!("SURFACE_STYLE_FILL_AREA({area})"));
            let side = e.add(format!("SURFACE_SIDE_STYLE('',({filled}))"));
            let usage = e.add(format!("SURFACE_STYLE_USAGE(.BOTH.,{side})"));
            let assign = e.add(format!("PRESENTATION_STYLE_ASSIGNMENT(({usage}))"));
            let styled = e.add(format!("STYLED_ITEM('color',({assign}),{solid})"));
            e.add(format!("MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',({styled}),{context})"));
        }
        Ok(format!("ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('hsm analytic round stock'),'2;1');\nFILE_NAME({},'1970-01-01T00:00:00',(''),(''),'hsm-kernel','hsm-kernel','');\nFILE_SCHEMA(('AUTOMOTIVE_DESIGN {{ 1 0 10303 214 1 1 1 1 }}'));\nENDSEC;\nDATA;\n{}ENDSEC;\nEND-ISO-10303-21;\n", string(name), e.text).into_bytes())
    }
}

/// A STEP real retaining the input double's significant digits.
fn real(x: f64) -> String {
    if x == 0.0 {
        return "0.".into();
    }
    let mut s = x.to_string().replace('e', "E");
    if !s.contains('.') && !s.contains('E') {
        s.push('.');
    }
    s
}

fn point(e: &mut Entities, x: f64, y: f64, z: f64) -> String {
    e.add(format!("CARTESIAN_POINT('',({},{},{}))", real(x), real(y), real(z)))
}

fn axis(e: &mut Entities, x: f64, y: f64, z: f64) -> String {
    let p = point(e, x, y, z);
    let dz = e.add("DIRECTION('',(0.,0.,1.))");
    let dx = e.add("DIRECTION('',(1.,0.,0.))");
    e.add(format!("AXIS2_PLACEMENT_3D('',{p},{dz},{dx})"))
}

fn vertex(e: &mut Entities, x: f64, y: f64, z: f64) -> (String, String) {
    let p = point(e, x, y, z);
    (e.add(format!("VERTEX_POINT('',{p})")), p)
}

fn edge(e: &mut Entities, a: &str, b: &str, curve: &str) -> String {
    e.add(format!("EDGE_CURVE('',{a},{b},{curve},.T.)"))
}

fn edge_loop(e: &mut Entities, edges: &[(&str, bool)]) -> String {
    let oriented: Vec<String> = edges.iter().map(|(id, sense)| {
        e.add(format!("ORIENTED_EDGE('',*,*,{id},{})", if *sense { ".T." } else { ".F." }))
    }).collect();
    e.add(format!("EDGE_LOOP('',({}))", oriented.join(",")))
}

struct Ring {
    loop_id: String,
}

struct Wall {
    lower: Ring,
    upper: Ring,
    faces: [String; 2],
}

/// Each cylinder uses two half faces with shared straight side edges.
fn wall(e: &mut Entities, c: V2, r: f64, lo: f64, hi: f64, outside: bool) -> Wall {
    let (v0, p0) = vertex(e, c.x + r, c.y, lo);
    let (v1, p1) = vertex(e, c.x - r, c.y, lo);
    let (u0, _) = vertex(e, c.x + r, c.y, hi);
    let (u1, _) = vertex(e, c.x - r, c.y, hi);
    let low_axis = axis(e, c.x, c.y, lo);
    let high_axis = axis(e, c.x, c.y, hi);
    let low_circle = e.add(format!("CIRCLE('',{low_axis},{})", real(r)));
    let high_circle = e.add(format!("CIRCLE('',{high_axis},{})", real(r)));
    let lower = [edge(e, &v0, &v1, &low_circle), edge(e, &v1, &v0, &low_circle)];
    let upper = [edge(e, &u0, &u1, &high_circle), edge(e, &u1, &u0, &high_circle)];
    let dz = e.add("DIRECTION('',(0.,0.,1.))");
    let vector = e.add(format!("VECTOR('',{dz},1.)"));
    let line0 = e.add(format!("LINE('',{p0},{vector})"));
    let line1 = e.add(format!("LINE('',{p1},{vector})"));
    let sides = [edge(e, &v0, &u0, &line0), edge(e, &v1, &u1, &line1)];
    let surface = e.add(format!("CYLINDRICAL_SURFACE('',{low_axis},{})", real(r)));
    let faces = std::array::from_fn(|k| {
        let lp = edge_loop(e, &[
            (&lower[k], true), (&sides[1 - k], true),
            (&upper[k], false), (&sides[k], false),
        ]);
        let bound = e.add(format!("FACE_OUTER_BOUND('',{lp},.T.)"));
        e.add(format!("ADVANCED_FACE('',({bound}),{surface},{})", if outside { ".T." } else { ".F." }))
    });
    let lower_loop = edge_loop(e, &[(&lower[0], true), (&lower[1], true)]);
    let upper_loop = edge_loop(e, &[(&upper[0], true), (&upper[1], true)]);
    Wall { lower: Ring { loop_id: lower_loop }, upper: Ring { loop_id: upper_loop }, faces }
}

fn plane(e: &mut Entities, outer: &Ring, holes: &[&Ring], z: f64, up: bool) -> String {
    let at = axis(e, 0.0, 0.0, z);
    let surface = e.add(format!("PLANE('',{at})"));
    let mut bounds = vec![e.add(format!("FACE_OUTER_BOUND('',{},.T.)", outer.loop_id))];
    bounds.extend(holes.iter().map(|r| e.add(format!("FACE_BOUND('',{},.F.)", r.loop_id))));
    e.add(format!("ADVANCED_FACE('',({}),{surface},{})", bounds.join(","), if up { ".T." } else { ".F." }))
}
