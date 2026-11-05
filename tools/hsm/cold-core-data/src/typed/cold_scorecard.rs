//! `_cold_scorecard`: the cold core's arrangement as a scorecard, written beside its STEP.
//! The `Scorecard` dataclass and the `Check` rows stay Python objects; this module reads them.

use super::*;

pub const NAME: &str = "_cold_scorecard";

pub const DETAIL_MAX: i64 = 8;
pub const FOCUS_DETAIL_MAX: i64 = 24;
pub const FOCUS_IDS: [&str; 4] = [
    "bom-covered",
    "mounted",
    "inlet-jet-qualified",
    "gas-adapter-envelope",
];
pub const TOUCH_VOLUME: f64 = 0.1;

pub struct State {
    pub sys: Val,
    pub dataclass: Val,
    pub field: Val,
    pub here: PathBuf,
    pub hw: PathBuf,
    pub repo: PathBuf,
    /// `_card.Check`, the row type every check is.
    pub check: Val,
    /// `_card.verdict`.
    pub verdict: Val,
    /// The Python `Scorecard` dataclass.
    pub scorecard: Val,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let sys = rt.py("sys")?;
        let dataclasses = rt.py("dataclasses")?;
        let dataclass = dataclasses.a("dataclass")?;
        let field = dataclasses.a("field")?;
        let here = resolve(&rt.file(NAME));
        let hw = ancestor(&here, "hardware")?;
        let repo = hw.parent().map(PathBuf::from).unwrap_or_default();
        let scripts = hw.join("scripts");
        if !sys.a("path")?.contains(&Val::Str(ps(&scripts)))? {
            rt.sys_path_insert(0, &scripts)?;
        }
        let card = rt.py("_card")?;
        let check = card.a("Check")?;
        let verdict = card.a("verdict")?;
        let scorecard = rt.py(NAME)?.a("Scorecard")?;
        Ok(Self {
            sys,
            dataclass,
            field,
            here,
            hw,
            repo,
            check,
            verdict,
            scorecard,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

fn focus(id: &Val) -> bool {
    matches!(id, Val::Str(s) if FOCUS_IDS.contains(&s.as_str()))
}

fn is_str(value: &Val, text: &str) -> bool {
    matches!(value, Val::Str(s) if s == text)
}

/// A string formatted as an f-string replacement field writes it.
fn fs(text: &str, spec: &str) -> Result<String> {
    fv(&Val::Str(text.into()), spec)
}

/// `Scorecard.gates_pass`: no gate row failed.
pub fn gates_pass(sc: &Val) -> Result<bool> {
    let mut held = vec![];
    for c in sc.a("checks")?.list()? {
        if is_str(&c.a("kind")?, "gate") {
            held.push(!is_str(&c.a("status")?, "fail"));
        }
    }
    Ok(held.into_iter().all(|ok| ok))
}

/// `to_dict(sc)`: the sidecar the 3D viewer reads.
pub fn to_dict(_rt: &Runtime, sc: &Val) -> Result<Val> {
    let mut checks = vec![];
    for c in sc.a("checks")?.list()? {
        let mut row = Dict::new();
        row.set("id", c.a("id")?)
            .set("label", c.a("label")?)
            .set("kind", c.a("kind")?)
            .set("status", c.a("status")?)
            .set("value", c.a("value")?)
            .set("target", c.a("target")?)
            .set("detail", Val::list(c.a("detail")?.list()?));
        let active = if is_str(&c.a("kind")?, "goal") {
            let active = c.a("active")?;
            if active.truthy()? {
                Val::Bool(focus(&c.a("id")?))
            } else {
                active
            }
        } else {
            c.a("active")?
        };
        row.set("active", active);
        checks.push(row.val());
    }
    Ok(Dict::new()
        .with("gatesPass", gates_pass(sc)?)
        .with("checks", Val::list(checks))
        .with("bodies", sc.a("bodies")?)
        .with("bends", sc.a("bends")?)
        .val())
}

/// `write(sc, step)`: the scorecard beside its STEP, as `<stem>.scorecard.json`.
pub fn write(rt: &Runtime, sc: &Val, step: &Path) -> Result<PathBuf> {
    let stem = step
        .file_stem()
        .map(|s| s.to_string_lossy().into_owned())
        .unwrap_or_default();
    let out = step
        .parent()
        .map(PathBuf::from)
        .unwrap_or_default()
        .join(format!("{stem}.scorecard.json"));
    let text = json_dumps(&to_dict(rt, sc)?, kw!["indent" => 1i64])? + "\n";
    write_text(&out, &text)?;
    Ok(out)
}

/// `report(sc)`: the card on the terminal.
pub fn report(rt: &Runtime, sc: &Val) -> Result<()> {
    rt.print("\nscorecard")?;
    for c in sc.a("checks")?.list()? {
        let status = c.a("status")?;
        let mark = match &status {
            Val::Str(s) if s == "pass" => "OK  ",
            Val::Str(s) if s == "fail" => "FAIL",
            Val::Str(s) if s == "warn" => "    ",
            _ => bail!("KeyError: {}", status.repr()?),
        };
        let id = c.a("id")?;
        rt.print(format!(
            "  {mark} {} {} {}",
            fv(&id, "14")?,
            fv(&c.a("value")?, "34")?,
            fv(&c.a("label")?, "")?
        ))?;
        let limit = if focus(&id) {
            FOCUS_DETAIL_MAX
        } else {
            DETAIL_MAX
        } as usize;
        let detail = c.a("detail")?.list()?;
        for line in detail.iter().take(limit) {
            rt.print(format!("         {}", fv(line, "")?))?;
        }
        if detail.len() > limit {
            rt.print(format!("         … {} more", detail.len() - limit))?;
        }
    }
    let bends = sc.a("bends")?;
    if bends.truthy()? {
        rt.print("\nlines")?;
        rt.print(format!(
            "  {} {} {} {} {} {} corners",
            fs("line", "18")?,
            fs("grade", "7")?,
            fs("length", ">8")?,
            fs("reach", ">8")?,
            fs("detour", ">7")?,
            fs("tightest", ">9")?
        ))?;
        for d in bends.list()? {
            let det = d.k("need")?.k("detour")?;
            let reach = d.k("reach")?;
            let reach = if matches!(reach, Val::None) {
                "—".to_owned()
            } else {
                fv(&reach, ".1f")?
            };
            let grade = d.k("grade")?;
            let grade = if grade.truthy()? {
                grade.str()?
            } else {
                "straight".to_owned()
            };
            let detour = if matches!(det, Val::None) {
                "    — ".to_owned()
            } else {
                format!("{}x", fv(&det, "5.2f")?)
            };
            rt.print(format!(
                "  {} {} {} {} {} {} {}",
                fv(&d.k("id")?, "18")?,
                fs(&grade, "7")?,
                fv(&d.k("length")?, "8.1f")?,
                fs(&reach, ">8")?,
                detour,
                fv(&d.k("radius")?, "9.2f")?,
                d.k("corners")?.len()?
            ))?;
        }
    }
    Ok(())
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "json", "json")?;
    ns.value("sys", s.sys.clone());
    ns.value("dataclass", s.dataclass.clone());
    ns.value("field", s.field.clone());
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("_here", Val::Path(s.here.clone()));
    ns.value("_hw", Val::Path(s.hw.clone()));
    ns.value("_repo", Val::Path(s.repo.clone()));
    ns.value("Check", s.check.clone());
    ns.value("verdict", s.verdict.clone());
    ns.value("DETAIL_MAX", DETAIL_MAX);
    ns.value("FOCUS_DETAIL_MAX", FOCUS_DETAIL_MAX);
    ns.value("FOCUS_IDS", FOCUS_IDS);
    ns.value("TOUCH_VOLUME", TOUCH_VOLUME);
    ns.func(rt, "Scorecard.gates_pass", |_, c| {
        Ok(Val::Bool(gates_pass(&c.req::<Val>(0, "self")?)?))
    });
    ns.value("Scorecard", s.scorecard.clone());
    ns.func(rt, "to_dict", |rt, c| to_dict(rt, &c.req::<Val>(0, "sc")?));
    ns.func(rt, "write", |rt, c| {
        let sc = c.req::<Val>(0, "sc")?;
        let step = c.req::<PathBuf>(1, "step")?;
        Ok(Val::Path(write(rt, &sc, &step)?))
    });
    ns.func(rt, "report", |rt, c| {
        report(rt, &c.req::<Val>(0, "sc")?)?;
        Ok(Val::None)
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
