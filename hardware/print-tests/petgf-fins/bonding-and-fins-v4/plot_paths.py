"""Draw the reviewed G-code and coupon positions for this manual experiment."""
from pathlib import Path
import json
import zipfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from finish import HERE, segments, local, footprint


def load(printer):
    folder = HERE / printer
    spec = json.loads(next(folder.glob('*.print.json')).read_text())
    review = json.loads((folder / 'review.json').read_text())
    with zipfile.ZipFile(folder / review['archive']) as archive:
        paths = segments(archive.read('Metadata/plate_1.gcode').decode())
    return folder, spec, paths


def main():
    for printer in ('mark1', 'mark2'):
        folder, spec, paths = load(printer)
        fig, ax = plt.subplots(figsize=(9, 6), constrained_layout=True)
        for p in spec['parts']:
            a, b = p['plate_bounds_mm']
            ax.add_patch(Rectangle(a[:2], b[0]-a[0], b[1]-a[1],
                                  facecolor='#e7eef5', edgecolor='#334155'))
            ax.text((a[0]+b[0])/2, (a[1]+b[1])/2, p['id'],
                    ha='center', va='center', fontsize=11, weight='bold')
        ax.set(xlim=(110, 215), ylim=(110, 210) if printer == 'mark2' else (120, 185),
               xlabel='Bed X (mm)', ylabel='Bed Y (mm)',
               title=f'{spec["printer"]} · labels as viewed from above · front at bottom')
        ax.set_aspect('equal'); ax.grid(alpha=.15)
        fig.savefig(folder/'plate-map.png', dpi=160); plt.close(fig)

    folder, spec, paths = load('mark2')
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.8), constrained_layout=True)
    for ax, name in zip(axes, ('F12', 'Y12')):
        part = next(p for p in spec['parts'] if p['id'] == name)
        own = [local(p, part) for p in paths if p['object'] == part['identify_id']]
        prior = footprint([p for p in own if abs(p['z']-part['roof_bottom_z_mm']) < .0001])
        for polygon in getattr(prior, 'geoms', [prior]):
            x, y = polygon.exterior.xy
            ax.fill(x, y, color='#64748b', alpha=.85)
        raster = [p for p in own if abs(p['z']-part['first_roof_z_mm']) < .0001
                  and p['feature'] == 'Bridge' and abs(p['a'][1]-p['b'][1]) < .005
                  and min(p['a'][0], p['b'][0]) < 3.1 and max(p['a'][0], p['b'][0]) > 14.9]
        for p in raster:
            a, b = p['a'], p['b']
            ax.plot([a[0],b[0]], [a[1],b[1]], color='#ea580c', linewidth=1.2)
            ax.scatter([a[0],b[0]], [a[1],b[1]], s=10, color='#16a34a', zorder=5)
        ax.set(xlim=(-1.8,19.8), ylim=(-.5,12.6), xlabel='Local span direction (mm)',
               ylabel='Local depth (mm)', title=f'{name}: {part["bridge_axis"]} direction · 28 supported strokes')
        ax.set_aspect('equal'); ax.grid(alpha=.12)
    fig.suptitle('First bridge layer: orange paths, green endpoints, grey preceding fin beads\n'
                 'Bridge fill prints first. Both terminal 0.25 mm segments lie on preceding beads.', fontsize=13)
    fig.savefig(HERE/'fin-landings.png', dpi=180); plt.close(fig)


if __name__ == '__main__':
    main()
