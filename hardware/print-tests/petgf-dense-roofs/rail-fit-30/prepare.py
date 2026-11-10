"""prepare.py builds and slices the matching production rail coupons without printer submission."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
source = ROOT/'hardware/print-tests/enclosure-support-scenarios/prepare.py'
spec = importlib.util.spec_from_file_location('rail_plate',source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.HERE = HERE
module.RUN = ROOT/'.cache/runs/rail-fit-30-2026-11-09'
module.TITLE = '2026-11-09-rail-fit-pair-30-D-left04-z018-mark1'
module.EXAMPLE = 'rail-fit-30'

if __name__=='__main__':
    module.main()
