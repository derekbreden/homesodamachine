//! `coil_mandrel`: the hollow PETG mandrel the 1/4" copper evaporator coil is hand-wound on,
//! its datums from the Rust cold-core recipe (`crate::mandrel`).

use super::cold_core_interface as core;
use super::*;

pub const NAME: &str = "coil_mandrel";

/// The datums the module turns into tuples after `globals().update(...)`.
const RANGES: [&str; 5] = [
    "mandrel_r_range",
    "mandrel_z_range",
    "lower_handle_z_range",
    "wind_z_range",
    "upper_handle_z_range",
];

pub struct State {
    here: PathBuf,
    layout: PathBuf,
    pub evap_tail_low_z: f64,
    pub evap_tail_high_z: f64,
    /// `_recipe('mandrel')`, as the recipe returns it.
    datums: Value,
    /// The same datums as module globals, in the dict's order, the ranges as tuples.
    globals: Vec<(String, Val)>,
    pub pitch: f64,
    pub tube_radius: f64,
    pub wrap_length: f64,
}

impl State {
    /// One numeric datum of `_recipe('mandrel')`.
    pub fn datum(&self, key: &str) -> Result<f64> {
        self.datums[key]
            .as_f64()
            .with_context(|| format!("coil mandrel datum {key}"))
    }
    /// One of the module globals `_recipe('mandrel')` sets, as Python reads it.
    pub fn global(&self, name: &str) -> Result<Val> {
        self.globals
            .iter()
            .find(|(key, _)| key == name)
            .map(|(_, value)| value.clone())
            .with_context(|| format!("coil mandrel global {name}"))
    }
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let here = resolve(&rt.file(NAME));
        let hardware = ancestor(&here, "hardware")?;
        rt.sys_path_insert(0, &hardware.join("scripts"))?;
        let docgen = ancestor_where(&here, |p| p.join("tools").join("docgen").is_dir())?;
        rt.sys_path_insert(0, &docgen.join("tools"))?;
        rt.sys_path_insert(0, &ancestor(&here, "printed-parts")?.join("cadlib"))?;
        rt.sys_path_insert(0, &parent_n(&here, 1))?;
        let core = core::state(rt)?;
        let (evap_tail_low_z, evap_tail_high_z) =
            (core.base.evap_tail_low_z, core.base.evap_tail_high_z);
        let layout = hardware.join("cold-core-layout");
        if !rt.pya("sys", "path")?.contains(&Val::Str(ps(&layout)))? {
            rt.sys_path_insert(0, &layout)?;
        }
        rt.py("_cold_core_data")?;
        // `globals().update(_recipe('mandrel'))`, then the ranges become tuples.
        let datums = crate::mandrel::datums(evap_tail_low_z, evap_tail_high_z);
        let mut globals = vec![];
        for (name, value) in Val::decode(datums.clone())?.items()? {
            let name = name.str()?;
            let value = if RANGES.contains(&name.as_str()) {
                Val::Tuple(value.list()?)
            } else {
                value
            };
            globals.push((name, value));
        }
        let number = |key: &str| {
            datums[key]
                .as_f64()
                .with_context(|| format!("coil mandrel datum {key}"))
        };
        let (pitch, tube_radius, wrap_length) =
            (number("pitch")?, number("tube_radius")?, number("wrap_length")?);
        Ok(Self {
            here,
            layout,
            evap_tail_low_z,
            evap_tail_high_z,
            datums,
            globals,
            pitch,
            tube_radius,
            wrap_length,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `numbers()`: the figures the kernel's coil-mandrel recipe cuts from.
pub fn numbers(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let colour = rt.pya("_materials", "M_PETG_BLACK")?;
    let linear = rt.pya("_materials", "linear")?;
    let color = Val::list(linear.c(vec![colour])?.list()?);
    Val::decode(crate::mandrel::numbers(
        s.evap_tail_low_z,
        s.evap_tail_high_z,
        &color.encode()?,
    ))
}

/// `body['min']` or `body['max']`, unpacked into three.
fn three(value: &Val) -> Result<[Val; 3]> {
    let items = value.iter()?;
    ensure!(items.len() == 3, "unpack: expected 3, got {}", items.len());
    let mut items = items.into_iter();
    Ok(std::array::from_fn(|_| items.next().unwrap()))
}

/// The Python `main()`: reports the winding, cuts the mandrel on the kernel and fills this
/// file's comments.
pub fn write(rt: &Runtime) -> Result<()> {
    let s = state(rt)?;
    let report = crate::mandrel::report(s.evap_tail_low_z, s.evap_tail_high_z);
    rt.pya("builtins", "print")?
        .ck(args![report], kw!["end" => ""])?;
    let said = rt.py("_rust_part")?.m(
        "cut",
        args!["cold-core", "coil-mandrel", numbers(rt)?, parent_n(&s.here, 0)],
    )?;
    let body = said.k("bodies")?.i(0)?;
    let (low, high) = (body.k("min")?, body.k("max")?);
    let [xmin, ymin, zmin] = three(&low)?;
    let [xmax, ymax, zmax] = three(&high)?;
    rt.print(format!(
        "\nResult: X[{},{}] Y[{},{}] Z[{},{}], V={} mm^3, {} triangles",
        fv(&xmin, ".1f")?,
        fv(&xmax, ".1f")?,
        fv(&ymin, ".1f")?,
        fv(&ymax, ".1f")?,
        fv(&zmin, ".1f")?,
        fv(&zmax, ".1f")?,
        fv(&body.k("volume")?, ".0f")?,
        fv(&body.k("triangles")?, "")?
    ))?;
    let files = said
        .k("files")?
        .list()?
        .iter()
        .map(Val::str)
        .collect::<Result<Vec<_>>>()?;
    rt.print(format!("-> {}", files.join(", ")))?;
    let variables = Val::decode(crate::mandrel::variables(
        s.evap_tail_low_z,
        s.evap_tail_high_z,
    ))?;
    let mut values = vec![];
    for (key, value) in variables.items()? {
        values.push((key.str()?, value.str()?));
    }
    let file = rt.file(NAME);
    rt.substitute_py_comments(&file, &values, Some(NAME))?;
    let name = file.file_name().map(|n| n.to_string_lossy().into_owned());
    rt.print(format!("-> {}", name.unwrap_or_default()))
}

/// The native `substitute_py_comments(path, variables)` this module imported from docgen.
fn substitute_py_comments(rt: &Runtime, c: &mut Call) -> Result<Val> {
    let path = PathBuf::from(c.req::<Val>(0, "path")?.str()?);
    let variables: Val = c.req(1, "variables")?;
    let mut values = vec![];
    for key in variables.iter()? {
        values.push((key.str()?, variables.get(key)?.str()?));
    }
    rt.substitute_py_comments(&path, &values, Some(NAME))?;
    Ok(Val::None)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "sys", "sys")?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("_here", s.here.clone());
    ns.func(rt, "substitute_py_comments", substitute_py_comments);
    ns.value("evap_tail_low_z", s.evap_tail_low_z);
    ns.value("evap_tail_high_z", s.evap_tail_high_z);
    ns.value("_layout", s.layout.clone());
    ns.python(rt, "_read", "_cold_core_data", "read")?;
    // `_recipe(op, **inputs)`: `_read(op, evap_tail_low_z=..., evap_tail_high_z=..., **inputs)`.
    let read = rt.pya("_cold_core_data", "read")?;
    let (low, high) = (s.evap_tail_low_z, s.evap_tail_high_z);
    ns.value(
        "_recipe",
        Val::function(move |args, mut kwargs| {
            let mut args = args.into_iter();
            let op = match args.next() {
                Some(op) => op,
                None => {
                    let at = kwargs
                        .iter()
                        .position(|(k, _)| k == "op")
                        .context("missing argument op")?;
                    kwargs.remove(at).1
                }
            };
            ensure!(args.next().is_none(), "too many positional arguments");
            let mut inputs = vec![
                ("evap_tail_low_z".to_owned(), Val::Float(low)),
                ("evap_tail_high_z".to_owned(), Val::Float(high)),
            ];
            inputs.extend(kwargs);
            read.call(vec![op], inputs)
        }),
    );
    for (name, value) in &s.globals {
        ns.value(name, value.clone());
    }
    ns.value("_name", RANGES[RANGES.len() - 1]);
    ns.func(rt, "__getattr__", |rt, c| {
        let name = c.req::<String>(0, "name")?;
        if name == "M_PETG_BLACK" || name == "linear" {
            return rt.pya("_materials", &name);
        }
        bail!("{name}")
    });
    ns.func(rt, "numbers", |rt, _| numbers(rt));
    ns.func(rt, "main", |rt, _| {
        write(rt)?;
        Ok(Val::None)
    });
    Ok(())
}

/// The `__main__` block.
pub fn main(rt: &Runtime) -> Result<()> {
    rt.py("_rust_part")?.m("start", vec![])?;
    write(rt)
}
