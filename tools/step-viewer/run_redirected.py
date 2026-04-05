"""Run a CadQuery script with its output redirected to a different directory.

Usage: python run_redirected.py <script_path> <output_dir>

Sets __file__ to a path inside output_dir so that Path(__file__).parent
resolves there. Every CadQuery script in this project derives its output
path from __file__, so this redirects all STEP output without modifying
the source scripts.
"""
import sys, os

script_path = sys.argv[1]
out_dir = sys.argv[2]

os.makedirs(out_dir, exist_ok=True)

# Scripts compute import paths relative to __file__, which is faked to the
# output dir.  Add the real script's sibling directories to sys.path so
# cross-directory imports (e.g. pump-case importing from case-snaps) work.
real_dir = os.path.dirname(os.path.abspath(script_path))
real_parent = os.path.dirname(real_dir)
for entry in os.listdir(real_parent):
    full = os.path.join(real_parent, entry)
    if os.path.isdir(full) and full not in sys.path:
        sys.path.insert(0, full)

fake_file = os.path.join(out_dir, os.path.basename(script_path))

with open(script_path) as f:
    source = f.read()

code = compile(source, script_path, "exec")
exec(code, {"__file__": fake_file, "__name__": "__main__", "__builtins__": __builtins__})
