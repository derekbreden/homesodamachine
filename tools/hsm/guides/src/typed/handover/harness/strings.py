"""Every string constant of a Python module that the Rust port does not contain verbatim."""
import ast, sys, re
py, rs = sys.argv[1], sys.argv[2]
tree = ast.parse(open(py).read())
rust = open(rs).read()
# Rust string literal contents, unescaped roughly
lits = set()
for m in re.finditer(r'"((?:[^"\\]|\\.)*)"', rust):
    s = m.group(1).replace('\\"', '"').replace('\\\\', '\\').replace('\\n', '\n')
    lits.add(s)
joined = "\n".join(lits)
doc = ast.get_docstring(tree)
missing = []
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        v = node.value
        if v == doc or len(v) < 2:
            continue
        # format-spec pieces appear inside f-strings; check substring presence in any literal
        if v not in joined:
            missing.append(v)
for v in sorted(set(missing)):
    print(repr(v))
