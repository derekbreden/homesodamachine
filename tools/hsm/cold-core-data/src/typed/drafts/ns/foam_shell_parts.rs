//! `_foam_shell`: the top-level foam-shell assembly. The wall builders are unioned, then every
//! port hole and channel opening is cut.

use super::above_core_mounts as mounts;
use super::cold_core_interface as core;
use super::foam_cap_parts as foam_cap;
use super::outer_shell;
use super::port_cuts;
use super::reed_b_outlet;
use super::reed_channels;
use super::reservoir_b_fill;
use super::reservoir_pocket_walls;
use super::support_ring;
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
        // The imported functions and `_reed_b_outlet` are members Python sees: the function and
        // module objects themselves. `build_full_shell` calls the typed functions.
        let pocket_walls = rt.import_module(reservoir_pocket_walls::NAME)?;
        let build_reservoir_pocket_walls = pocket_walls.a("build_reservoir_pocket_walls")?;
        let support = rt.import_module(support_ring::NAME)?;
        let build_carbonator_support_ring = support.a("build_carbonator_support_ring")?;
        let outer = rt.import_module(outer_shell::NAME)?;
        let build_outer_shell = outer.a("build_outer_shell")?;
        let cut_insert_pockets = outer.a("cut_insert_pockets")?;
        let ports = rt.import_module(port_cuts::NAME)?;
        let cut_copper_ports = ports.a("cut_copper_ports")?;
        let cut_prv_vent_port = ports.a("cut_prv_vent_port")?;
        let reeds = rt.import_module(reed_channels::NAME)?;
        let build_reed_channels = reeds.a("build_reed_channels")?;
        let cut_reed_channel_openings = reeds.a("cut_reed_channel_openings")?;
        let reed_b_outlet = rt.import_module(reed_b_outlet::NAME)?;
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
    let mut shell = reservoir_pocket_walls::build_reservoir_pocket_walls(rt)?;
    shell = shell.m("union", args![support_ring::build_carbonator_support_ring(rt)?])?;
    shell = shell.m("union", args![outer_shell::build_outer_shell(rt)?])?;
    for side in [1.0, -1.0] {
        let channels = reed_channels::build_reed_channels(rt, side)?;
        shell = shell.m("union", args![channels])?;
    }
    shell = outer_shell::cut_insert_pockets(rt, &shell)?;
    shell = port_cuts::cut_prv_vent_port(rt, &shell)?;
    shell = port_cuts::cut_copper_ports(rt, &shell)?;
    shell = reed_channels::cut_reed_channel_openings(rt, &shell)?;
    let top_cap_height = foam_cap::state(rt)?.top_cap_height;
    let entry_air = mounts::world_shape_in_cap(rt, &reservoir_b_fill::channel_air(rt)?)?
        .m("rotate", args![[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], 180.0])?
        .m(
            "translate",
            args![[0.0, 0.0, s.foam_shell_outer_height + top_cap_height]],
        )?;
    let cut = shell.m("cut", args![entry_air])?;
    reed_b_outlet::apply(rt, &cut)
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
