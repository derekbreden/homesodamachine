"""Build the landscape owner guide with its compiled composition program."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import main
if __name__ == "__main__":
    main("landscape")
