//! `_foam_shell`: the top-level foam-shell assembly. The wall builders are unioned, then every
//! port hole and channel opening is cut.

use super::above_core_mounts as mounts;
use super::cold_core_interface as core;
use super::foam_cap_parts as foam_cap;
use super::reservoir_b_fill;
use super::*;

pub const NAME: &str = "_foam_shell";

pub struct State {
    foam_shell_outer_height: f64,
    build_reservoir_pocket_walls: Val,
    build_carbonator_support_ring: Val,
    build_outer_shell: Val,
    cut_insert_pockets: Val,
    cut_copper_ports: Val,
    cut_prv_vent_port: Val,
    build_reed_channels: Val,
    cut_reed_channel_openings: Val,
    reed_b_outlet: Val,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let core = core::state(rt)?;
        let pocket_walls = rt.import_module("_reservoir_pocket_walls")?; // via namespace: _reservoir_pocket_walls
        let build_reservoir_pocket_walls = pocket_walls.a("build_reservoir_pocket_walls")?; // via namespace: _reservoir_pocket_walls
        let support_ring = rt.import_module("_support_ring")?; // via namespace: _support_ring
        let build_carbonator_support_ring = support_ring.a("build_carbonator_support_ring")?; // via namespace: _support_ring
        let outer_shell = rt.import_module("_outer_shell")?; // via namespace: _outer_shell
        let build_outer_shell = outer_shell.a("build_outer_shell")?; // via namespace: _outer_shell
        let cut_insert_pockets = outer_shell.a("cut_insert_pockets")?; // via namespace: _outer_shell
        let port_cuts = rt.import_module("_port_cuts")?; // via namespace: _port_cuts
        let cut_copper_ports = port_cuts.a("cut_copper_ports")?; // via namespace: _port_cuts
        let cut_prv_vent_port = port_cuts.a("cut_prv_vent_port")?; // via namespace: _port_cuts
        let reed_channels = rt.import_module("_reed_channels")?; // via namespace: _reed_channels
        let build_reed_channels = reed_channels.a("build_reed_channels")?; // via namespace: _reed_channels
        let cut_reed_channel_openings = reed_channels.a("cut_reed_channel_openings")?; // via namespace: _reed_channels
        let reed_b_outlet = rt.import_module("_reed_b_outlet")?; // via namespace: _reed_b_outlet
        Ok(Self {
            foam_shell_outer_height: core.base.foam_shell_outer_height,
            build_reservoir_pocket_walls,
            build_carbonator_support_ring,
            build_outer_shell,
            cut_insert_pockets,
            cut_copper_ports,
            cut_prv_vent_port,
            build_reed_channels,
            cut_reed_channel_openings,
            reed_b_outlet,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `build_full_shell()`: the foam shell with every wall, port and channel.
pub fn build_full_shell(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let mut shell = s.build_reservoir_pocket_walls.c(vec![])?; // via namespace: _reservoir_pocket_walls
    shell = shell.m("union", args![s.build_carbonator_support_ring.c(vec![])?])?; // via namespace: _support_ring
    shell = shell.m("union", args![s.build_outer_shell.c(vec![])?])?; // via namespace: _outer_shell
    for side in [1i64, -1] {
        let channels = s.build_reed_channels.ck(vec![], kw!["side" => side])?; // via namespace: _reed_channels
        shell = shell.m("union", args![channels])?;
    }
    shell = s.cut_insert_pockets.c(args![shell])?; // via namespace: _outer_shell
    for cut in [
        &s.cut_prv_vent_port,
        &s.cut_copper_ports,
        &s.cut_reed_channel_openings,
    ] {
        shell = cut.c(args![shell])?; // via namespace: _port_cuts, _reed_channels
    }
    let top_cap_height = foam_cap::state(rt)?.top_cap_height;
    let entry_air = mounts::world_shape_in_cap(rt, &reservoir_b_fill::channel_air(rt)?)?
        .m("rotate", args![[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], 180.0])?
        .m(
            "translate",
            args![[0.0, 0.0, s.foam_shell_outer_height + top_cap_height]],
        )?;
    let cut = shell.m("cut", args![entry_air])?;
    s.reed_b_outlet.a("apply")?.c(args![cut]) // via namespace: _reed_b_outlet
}

/// `import_shell(path)`: the shell's solid from its STEP, or rebuilt when the STEP holds
/// meshcad's tessellation.
pub fn import_shell(rt: &Runtime, path: &Val) -> Result<Val> {
    let cq = rt.py("cadquery")?;
    let import_step = rt.pya("_cadq_export", "import_step")?;
    let getattr = hsm_documents::interop::builtin("getattr").context("getattr")?;
    if !getattr.c(args![cq, "MESH", false])?.truthy()? {
        let open = hsm_documents::interop::builtin("open").context("open")?;
        let context = open.c(args![path, "rb"])?;
        let stream = context.m("__enter__", vec![])?;
        let read = (|| -> Result<bool> {
            let head = stream.m("read", args![200i64])?;
            hsm_documents::interop::compare(
                "in",
                Val::Bytes(b"meshcad tessellated".to_vec()),
                head,
            )?
            .truthy()
        })();
        context.m("__exit__", vec![Val::None, Val::None, Val::None])?;
        if read? {
            return build_full_shell(rt)?.m("val", vec![]);
        }
    }
    import_step.c(args![path.str()?])?.m("val", vec![])
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value(
        "foam_shell_outer_height",
        rt.import_module(core::NAME)?.a("foam_shell_outer_height")?,
    );
    ns.value(
        "build_reservoir_pocket_walls",
        s.build_reservoir_pocket_walls.clone(),
    );
    ns.value(
        "build_carbonator_support_ring",
        s.build_carbonator_support_ring.clone(),
    );
    ns.value("build_outer_shell", s.build_outer_shell.clone());
    ns.value("cut_insert_pockets", s.cut_insert_pockets.clone());
    ns.value("cut_copper_ports", s.cut_copper_ports.clone());
    ns.value("cut_prv_vent_port", s.cut_prv_vent_port.clone());
    ns.value("build_reed_channels", s.build_reed_channels.clone());
    ns.value("cut_reed_channel_openings", s.cut_reed_channel_openings.clone());
    ns.value("_reed_b_outlet", s.reed_b_outlet.clone());
    ns.func(rt, "build_full_shell", |rt, _| build_full_shell(rt));
    ns.func(rt, "import_shell", |rt, c| {
        import_shell(rt, &c.req::<Val>(0, "path")?)
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
