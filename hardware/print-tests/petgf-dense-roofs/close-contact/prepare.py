"""prepare.py packages the close-contact ceiling experiment using the existing plate writer."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
source = HERE.parent/'prepare.py'
spec = importlib.util.spec_from_file_location('ceiling_plate',source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.HERE = HERE
module.TITLE = '2026-11-09-close-contact-DEF-left04-z018-mark1'

if __name__=='__main__':
    module.main()
