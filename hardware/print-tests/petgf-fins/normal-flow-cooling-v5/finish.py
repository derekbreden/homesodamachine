"""Apply the same reviewed first-roof extrusion/fan treatments to this new plate."""
from pathlib import Path
import importlib.util
import sys

HERE = Path(__file__).resolve().parent
source = HERE.parent / 'bonding-and-fins-v4/finish.py'
loader = importlib.util.spec_from_file_location('v4_treatments', source)
v4 = importlib.util.module_from_spec(loader)
loader.loader.exec_module(v4)


if __name__ == '__main__':
    v4.HERE = HERE
    sys.argv = [sys.argv[0], 'mark1']
    v4.main()
