//! Prisms with rounded section corners, the form the frame, funnel and display cuts take, and
//! shapes carried by a rigid frame.
use crate::plan::{Bounds, Graph, Op, P2, P3, Shape};

/// A prism across `axis` over `lo..hi` whose named section vertices take a `radius` fillet.
pub fn corner_prism(g: &mut Graph, axis: usize, lo: f64, hi: f64, section: Vec<P2>, radius: f64,
                    corners: &[usize]) -> Shape {
    let span = if lo <= hi { [lo, hi] } else { [hi, lo] };
    let bounds = Graph::prism_bounds(axis, span, &section);
    g.add(Op::CornerPrism { axis, span, section, corners: corners.to_vec(), radius, offset: None },
          vec![], Some(bounds))
}

/// A box across `axis` whose section corners, counted round from its low-low corner, round.
pub fn rounded(g: &mut Graph, axis: usize, b: Bounds, radius: f64, corners: &[usize]) -> Shape {
    let other: Vec<usize> = (0..3).filter(|&k| k != axis).collect();
    let (a, c) = (other[0], other[1]);
    let section = vec![[b[2 * a], b[2 * c]], [b[2 * a + 1], b[2 * c]], [b[2 * a + 1], b[2 * c + 1]],
                       [b[2 * a], b[2 * c + 1]]];
    corner_prism(g, axis, b[2 * axis], b[2 * axis + 1], section, radius, corners)
}

/// A plan rectangle `w` by `d` about a centre, standing over a Z span, all four corners round.
pub fn rounded_prism(g: &mut Graph, w: f64, d: f64, r: f64, z0: f64, z1: f64, cx: f64, cy: f64) -> Shape {
    rounded(g, 2, [cx - w / 2.0, cx + w / 2.0, cy - d / 2.0, cy + d / 2.0, z0, z1], r, &[0, 1, 2, 3])
}

/// A shape carried by a rigid frame, bounded by its bounds' eight placed corners.
pub fn place(g: &mut Graph, shape: Shape, rotation: [P3; 3], translation: P3) -> Shape {
    let bounds = shape.bounds.map(|b| {
        let corners: Vec<P3> = (0..8)
            .map(|i| {
                let p = [b[(i >> 2) & 1], b[2 + ((i >> 1) & 1)], b[4 + (i & 1)]];
                std::array::from_fn(|k| {
                    let r = rotation[k];
                    r[0] * p[0] + r[1] * p[1] + r[2] * p[2] + translation[k]
                })
            })
            .collect();
        std::array::from_fn(|i| {
            let k = i / 2;
            let values = corners.iter().map(|p| p[k]);
            if i % 2 == 0 { values.fold(f64::INFINITY, f64::min) } else { values.fold(f64::NEG_INFINITY, f64::max) }
        })
    });
    g.placed(shape, rotation, translation, bounds)
}
/// A removable round tree supports an exposed shoulder without routing through fitted pockets.
pub fn removable_tree(spec: &serde_json::Value) -> anyhow::Result<hsm_kernel::Solid> {
    use hsm_kernel::{Solid,V3,v3};
    let root = &spec["root_source_mm"];
    let (x,y,z) = (root[0].as_f64().unwrap(),root[1].as_f64().unwrap(),root[2].as_f64().unwrap());
    let neck = spec["neck_length_mm"].as_f64().unwrap();
    let flare = spec["neck_flare_mm"].as_f64().unwrap();
    let r0 = spec["root_radius_mm"].as_f64().unwrap();
    let r = spec["trunk_radius_mm"].as_f64().unwrap();
    let inner = spec["inner_contact_x_mm"].as_f64().unwrap();
    let b:Vec<f64> = spec["contact_box_source_mm"].as_array().unwrap().iter().map(|v|v.as_f64().unwrap()).collect();
    let head = b[5];
    let parts = vec![
        Solid::cylinder(v3(x,y,z+0.01),-V3::Z,r0,neck+0.01)?,
        Solid::cone(v3(x,y,z-neck),-V3::Z,r0,r,flare)?,
        Solid::cylinder(v3(x,y,z-neck-flare),-V3::Z,r,z-neck-flare-head)?,
        Solid::cylinder(v3(x,y,head+x-inner),v3(-1.0,0.0,-1.0),r,(x-inner)*2f64.sqrt())?,
        Solid::cuboid(v3(b[0],b[2],b[4]),v3(b[1],b[3],b[5])),
    ];
    let tree = Solid::union_all(&parts)?;
    let bounds = tree.bounds();
    tree.intersect(&Solid::cuboid(v3(bounds.min.x-1.0,bounds.min.y-1.0,b[4]),bounds.max+v3(1.0,1.0,1.0)))?.simplified()
}
