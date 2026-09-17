"""Compose the full geometry viewer from its saved geometry."""
from pathlib import Path
import argparse
import base64

def compose(output):
    here = Path(__file__).resolve().parent
    fragment = (here / 'enclosure-forms.template.html').read_text().replace(
        '__MODEL_DATA__', (here / 'models.b64').read_text())
    # The full fluted geometry belongs in the browser; the conversation comparison uses
    # rendered detail views. Mesh accuracy is independent of the conversation's byte budget.
    document = (here / 'viewer.template.html').read_text().replace('__VIEWER__', fragment)
    output.mkdir(parents=True, exist_ok=True)
    path = output / 'index.html'
    path.write_text(document)
    print(path)


def compose_corners(output):
    here = Path(__file__).resolve().parent
    fragment = (here / 'corner-comparison.template.html').read_text()
    for key in ('current', 'A', 'B', 'C'):
        image = base64.b64encode((here / 'renders' / f'corner-{key}.png').read_bytes()).decode()
        fragment = fragment.replace('__' + key.upper() + '_IMAGE__', 'data:image/png;base64,' + image)
    assert len(fragment.encode()) < 1_000_000
    output.mkdir(parents=True, exist_ok=True)
    path = output / 'enclosure-forms.html'
    path.write_text(fragment)
    print(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--corners', action='store_true', help='Compose the saved corner images for the conversation')
    args = parser.parse_args()
    (compose_corners if args.corners else compose)(args.output)
