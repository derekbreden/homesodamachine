"""Compose the enclosure form comparison from its saved geometry."""
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path)
args = parser.parse_args()
here = Path(__file__).resolve().parent
fragment = (here / 'enclosure-forms.template.html').read_text().replace(
    '__MODEL_DATA__', (here / 'models.b64').read_text())
assert len(fragment.encode()) < 1_000_000
args.output.mkdir(parents=True, exist_ok=True)
path = args.output / 'enclosure-forms.html'
path.write_text(fragment)
print(path)
