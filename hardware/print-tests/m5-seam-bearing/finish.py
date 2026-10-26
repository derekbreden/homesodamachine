"""Package the reviewed slice and draw its actual coupon placement; never sends."""
from pathlib import Path
import json
import re
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from bambu_print_archive import package


def finish(folder):
    preparation = json.loads((folder / 'preparation.json').read_text())
    review = json.loads((folder / 'review.json').read_text())
    if not review['pass']:
        raise ValueError('Use a passing reviewed native slice.')
    archive = ROOT / preparation['archive']
    printable = folder / 'm5-seam-bearing-mark1-print-only.gcode.3mf'
    packaging = package(archive, printable)
    (folder / 'packaging.json').write_text(json.dumps(packaging, indent=2) + '\n')
    with zipfile.ZipFile(archive) as z:
        text = z.read('Metadata/plate_1.gcode').decode()
        mass = float(re.search(r'; total filament weight \[g\]\s*:\s*([\d.]+)', text)[1])
    job = dict(preparation=str(folder.relative_to(ROOT)),
               project=preparation['project'], archive=str(archive.relative_to(ROOT)),
               print_only_archive=str(printable.relative_to(ROOT)),
               printer='Mark1', connection_key='H2C', submitted=False,
               estimated_seconds=preparation['estimated_seconds'], filament_g=mass,
               objects=len(preparation['objects']), support_roads=review['support_roads'],
               minimum_bed_margin_mm=review['minimum_bed_margin_mm'],
               scope='Prepared offline for the requested Mark1 session. No printer command sent.')
    (HERE / 'print-job.json').write_text(json.dumps(job, indent=2) + '\n')

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle
    fig, ax = plt.subplots(figsize=(5, 7.8), dpi=150)
    for obj in preparation['objects']:
        match = re.fullmatch(r'm5-d(\d+)-h(\d+)', obj['name'])
        diameter, length = int(match[1]) / 10, int(match[2])
        cx, cy, _ = obj['translation_mm']
        ax.add_patch(Rectangle((cx - 10, cy - 7), 20, 14,
                              facecolor='#dedede' if length == 40 else '#f4f4f4',
                              edgecolor='#454545', linewidth=.8))
        ax.add_patch(Circle((cx - 3, cy), diameter / 2,
                           facecolor='white', edgecolor='#454545', linewidth=.8))
        ax.text(cx + 5, cy, f'{diameter:.1f}', ha='center', va='center', fontsize=11)
    ax.text(214, 196, '40 mm\nbearing', va='center', fontsize=11)
    ax.text(214, 124, '12 mm\nbearing', va='center', fontsize=11)
    ax.set(xlim=(112, 245), ylim=(80, 240), aspect='equal')
    ax.axis('off')
    ax.text(177, 238, 'Back of Mark1', ha='center', va='bottom', fontsize=12)
    ax.text(177, 82, 'Front of Mark1', ha='center', va='top', fontsize=12)
    fig.suptitle('M5 bore comparison', fontsize=15, y=.97)
    fig.tight_layout(rect=(0, 0, 1, .94))
    fig.savefig(HERE / 'plate-map.png', facecolor='white', dpi=150)
    plt.close(fig)
    print(json.dumps(job, indent=2))


if __name__ == '__main__':
    job = json.loads((HERE / 'print-job.json').read_text())
    finish(ROOT / job['preparation'])
