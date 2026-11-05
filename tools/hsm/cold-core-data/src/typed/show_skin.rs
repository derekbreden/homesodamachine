//! Smooth cold-core casing surfaces, shared by shell, cups and lids.

use super::*;

/// Write the smooth B-rep surface at the shared absolute print tolerance.
pub fn write_bed_file(rt: &Runtime, solid: Val, path: Val) -> Result<Val> {
    let mesh = rt
        .pya("print_mesh", "write_print_stl")?
        .c(vec![solid, path.clone()])?;
    let facets = mesh.a("faces")?.len()?;
    rt.print(format!(
        "-> {} ({facets} facets, watertight)",
        fv(&path.a("name")?, "")?
    ))?;
    Ok(mesh)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    ns.python(rt, "piece_mesh", "print_mesh", "print_mesh")?;
    ns.python(rt, "write_print_stl", "print_mesh", "write_print_stl")?;
    ns.func(rt, "write_bed_file", |rt, c| {
        write_bed_file(rt, c.req(0, "solid")?, c.req(1, "path")?)
    });
    Ok(())
}

pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
