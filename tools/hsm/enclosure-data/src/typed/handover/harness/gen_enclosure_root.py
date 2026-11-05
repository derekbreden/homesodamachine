"""Write the typed enclosure root ($T/enclosure.rs) and its five empty parts from the function map
and the generated namespace's probe.

usage: gen_enclosure_root.py <enclosure-functions.json> <probe generated.json> <out typed dir>
"""
import ast
import json
import keyword
import sys
from pathlib import Path

R = Path('/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/typed-enclosure-202611041700')
meta = json.load(open(sys.argv[1]))
probe = json.load(open(sys.argv[2]))['enclosure']
out = Path(sys.argv[3])
src = open(R / 'py/enclosure.py').read()
tree = ast.parse(src)
doc = ast.get_docstring(tree, clean=False) or ''
functions = sorted(meta['functions'], key=lambda f: f['py'][0])
fnames = {f['name'] for f in functions}
slots = set(meta['slots'])
RUST_KW = {'as', 'break', 'const', 'continue', 'crate', 'else', 'enum', 'extern', 'false', 'fn', 'for', 'if',
           'impl', 'in', 'let', 'loop', 'match', 'mod', 'move', 'mut', 'pub', 'ref', 'return', 'self', 'Self',
           'static', 'struct', 'super', 'trait', 'true', 'type', 'unsafe', 'use', 'where', 'while', 'async',
           'await', 'dyn', 'abstract', 'become', 'box', 'do', 'final', 'macro', 'override', 'priv', 'typeof',
           'unsized', 'virtual', 'yield', 'try', 'gen'}


def field(name):
    return f'r#{name}' if name in RUST_KW else name


def scalar(v):
    if isinstance(v, bool):
        return 'bool'
    if isinstance(v, int):
        return 'i64'
    if isinstance(v, float):
        return 'f64'
    if isinstance(v, str):
        return 'String'
    return None


def value_type(v):
    """The Rust type of one snapshot value, or None when it has no fixed typed shape."""
    k = scalar(v)
    if k:
        return k
    if isinstance(v, dict) and set(v) == {'$tuple'}:
        items = v['$tuple']
        if not items:
            return 'Tup<Val>'
        kinds = {value_type(x) for x in items}
        if None in kinds:
            return None
        if len(kinds) == 1:
            return f'[{kinds.pop()}; {len(items)}]'
        if kinds <= {'i64', 'f64'}:
            return f'[Num; {len(items)}]'
    return None


# Names the recorders and machine-data replace while they call the module: read from the namespace.
REPLACEABLE = {'cq', 'record_bound', '_teardrop_y'}


def rust_type(name, d):
    """The State field type for one probed value, or None when the name is not a constant."""
    if name in REPLACEABLE or 'callable' in d:
        return None
    if d.get('native') == 'callable':
        return None
    if 'module' in d or d.get('native') == 'namespace':
        return 'Val'
    if 'native' in d or 'opaque' in d or 'error' in d:
        return 'Val'
    t, v = d.get('type'), d.get('value')
    if t is None or t == 'NoneType' or 'value' not in d:
        return None
    return value_type(v) or 'Val'


fields = []
for name in probe['names']:
    if name in fnames or name in slots or name.startswith('__'):
        continue
    t = rust_type(name, probe['values'][name])
    if t:
        fields.append((name, t))
part_names = {1: '118–2116', 2: '2117–3500', 3: '3501–4993', 4: '4994–6595', 5: '6596–8543'}
doc_lines = '\n'.join(('//! ' + line).rstrip() for line in doc.strip('\n').split('\n'))
lines = [doc_lines, '//!',
         '//! The root: the module\'s typed constants (`State`), what every function receives (`Cx`), and the',
         '//! install. The functions are in five parts by Python line: `p1` ' + part_names[1] + ', `p2` ' + part_names[2]
         + ', `p3` ' + part_names[3] + ',',
         '//! `p4` ' + part_names[4] + ', `p5` ' + part_names[5] + '.',
         '#![allow(non_snake_case, non_upper_case_globals, dead_code, unused_imports)]',
         'use super::num::Num;',
         'use super::py::{self, Args, Kwargs, Py, Tup, Val};',
         'use super::rt::{Ns, Rt};',
         'use anyhow::{Context, Result};',
         'use std::rc::Rc;',
         '',
         'pub mod p1;', 'pub mod p2;', 'pub mod p3;', 'pub mod p4;', 'pub mod p5;',
         '',
         'pub const TYPED: bool = false;',
         'const MODULE: &str = "enclosure";',
         '',
         '/// What every typed function of the module receives: the registry, the module namespace (the',
         '/// names the recorders replace are read there at every use) and the module\'s constants.',
         'pub struct Cx {',
         '    pub rt: Rt,',
         '    pub ns: Ns,',
         '    pub s: State,',
         '}',
         '',
         '/// Every module constant, one field per Python name, as the top level leaves it.',
         'pub struct State {']
for name, t in fields:
    lines.append(f'    pub {field(name)}: {t},')
lines += ['}', '', 'impl State {',
          '    /// The constants as the generated top level left them.',
          '    #[cfg(feature = "hybrid")]',
          '    pub fn from_ns(ns: &Ns) -> Result<State> {',
          '        fn read<T: Py>(ns: &Ns, name: &str) -> Result<T> {',
          '            T::from_py(&ns.get(name)?).with_context(|| format!("enclosure.{name}"))',
          '        }',
          '        Ok(State {']
for name, t in fields:
    lines.append(f'            {field(name)}: read(ns, "{name}")?,')
lines += ['        })', '    }', '}', '',
          '/// Every function of the module in source order, with its part.',
          'pub const FUNCTIONS: &[(&str, u8)] = &[']
for f in functions:
    lines.append(f'    ("{f["name"]}", {f["part"]}),')
lines += ['];', '',
          'impl Cx {',
          '    /// A function no part has converted yet: its generated definition, called through the namespace,',
          '    /// with its result converted.',
          '    #[cfg(feature = "hybrid")]',
          '    pub fn generated<T: Py>(&self, name: &str, args: Vec<Val>, kwargs: Vec<(&str, Val)>) -> Result<T> {',
          '        let function = self.ns.get(name)?;',
          '        T::from_py(&py::call_kw(&function, args, kwargs)?).with_context(|| format!("enclosure.{name} result"))',
          '    }',
          '}',
          '',
          'fn part_function(cx: &Rc<Cx>, part: u8, name: &str) -> Option<Result<Val>> {',
          '    match part {',
          '        1 => p1::function(cx, name),',
          '        2 => p2::function(cx, name),',
          '        3 => p3::function(cx, name),',
          '        4 => p4::function(cx, name),',
          '        5 => p5::function(cx, name),',
          '        _ => None,',
          '    }',
          '}',
          'fn part_converted(part: u8, name: &str) -> bool {',
          '    match part {',
          '        1 => p1::CONVERTED.contains(&name),',
          '        2 => p2::CONVERTED.contains(&name),',
          '        3 => p3::CONVERTED.contains(&name),',
          '        4 => p4::CONVERTED.contains(&name),',
          '        5 => p5::CONVERTED.contains(&name),',
          '        _ => false,',
          '    }',
          '}',
          '',
          '/// The hybrid build: the generated module runs and its namespace becomes the module\'s; every',
          '/// function a part lists in `CONVERTED` is then replaced there by that part\'s typed wrapper.',
          '#[cfg(feature = "hybrid")]',
          'pub fn install(rt: &Rt, _ns: &Ns) -> Result<()> {',
          '    let base = rt.generated_base(MODULE)?;',
          '    let state = State::from_ns(&base)?;',
          '    let cx = rt.keep(MODULE, Cx { rt: rt.clone(), ns: base.clone(), s: state });',
          '    for &(name, part) in FUNCTIONS {',
          '        if part_converted(part, name) {',
          '            let function = part_function(&cx, part, name)',
          '                .with_context(|| format!("enclosure.{name} is converted but has no wrapper"))??;',
          '            base.set(name, function)?;',
          '        }',
          '    }',
          '    Ok(())',
          '}',
          '',
          '/// The final build: the whole top level, typed, in source order.',
          '#[cfg(not(feature = "hybrid"))]',
          'pub fn install(_rt: &Rt, _ns: &Ns) -> Result<()> {',
          '    anyhow::bail!("enclosure: the typed top level is not written")',
          '}',
          '',
          '/// `if __name__ == "__main__"`: the enclosure step.',
          'pub fn main_block(rt: &Rt) -> Result<()> {',
          '    let generate = rt.member("_enclosure_rust_driver", "main")?;',
          '    py::call(&generate, vec![])?;',
          '    Ok(())',
          '}',
          '']
(out / 'enclosure.rs').write_text('\n'.join(lines))
(out / 'enclosure').mkdir(exist_ok=True)
for k, rng in part_names.items():
    names = [f['name'] for f in functions if f['part'] == k]
    part = [f'//! Part {k} of `enclosure`: the functions whose first Python line is in {rng}:',
            '//! ' + ', '.join(f'`{n}`' for n in names[:6]) + (', ...' if len(names) > 6 else '') + f' ({len(names)}).',
            '#![allow(non_snake_case, non_upper_case_globals, dead_code, unused_imports)]',
            'use super::{Cx, State};',
            'use crate::typed::num::Num;',
            'use crate::typed::py::{self, Args, Kwargs, Py, Tup, Val};',
            'use anyhow::{Context, Result};',
            'use std::rc::Rc;',
            '',
            '/// The functions of this part that run typed: the hybrid build replaces exactly these.',
            'pub const CONVERTED: &[&str] = &[];',
            '',
            '/// A function of this part as a Python-callable value.',
            'pub fn function(cx: &Rc<Cx>, name: &str) -> Option<Result<Val>> {',
            '    let _ = cx;',
            '    match name {',
            '        _ => None,',
            '    }',
            '}',
            '']
    (out / 'enclosure' / f'p{k}.rs').write_text('\n'.join(part))
print('fields', len(fields), 'Val fields', sum(1 for _, t in fields if t == 'Val'), 'functions', len(functions))
