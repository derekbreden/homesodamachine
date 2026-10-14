"""Plot the identified printed and corrected native seam starts manually."""
from pathlib import Path
import json, runpy
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
old = json.loads((HERE / 'printed-base-trace/trace.json').read_text())
new = json.loads((HERE / 'complete-trace/trace.json').read_text())
paths = runpy.run_path(str(HERE.parents[2] / 'faucet_paths.py'))
center = np.array([paths['WATER_Y'] - paths['WATER_RADIUS'], paths['ARC_START_Z']])
fig, (left, right) = plt.subplots(1, 2, figsize=(10.8, 6.3), gridspec_kw={'width_ratios': [1.05, 1]})
for data, color, label in [(old, '#ce7029', 'Printed base · task 1337160395'),
                           (new, '#27815e', 'Corrected native paths')]:
    rows = [r for r in data['runs'] if r['part'] == 'industrial-shell-base' and r['exposed_rear_seam_goal']]
    xyz = np.array([r['start_cad_mm'] for r in rows])
    left.plot(xyz[:, 0], xyz[:, 2], color=color, lw=1.8, label=label)
left.axvline(0, color='#667085', lw=.8, ls='--')
left.axhspan(0, 80, color='#dba250', alpha=.09)
left.text(-1.9, 75, 'Both lower transitions included', fontsize=9, color='#8b5d23')
left.set(xlabel='Lateral position from rear center (mm)', ylabel='Assembly height, CAD Z (mm)',
         title='Base: complete height', xlim=(-2.1, 1.8), ylim=(0, 240))
left.legend(loc='upper left', fontsize=8)
for part, color, label in [('industrial-shell-base', '#27815e', 'Base curved neck'),
                            ('faucet-shell-tip', '#4169a1', 'Tip curved neck')]:
    rows = [r for r in new['runs'] if r['part'] == part and r['exposed_rear_seam_goal']]
    xyz = np.array([r['start_cad_mm'] for r in rows])
    angles = np.degrees(np.arctan2(xyz[:, 2] - center[1], xyz[:, 1] - center[0]))
    keep = (angles >= 8) & (angles <= 127) & (xyz[:, 2] > paths['ARC_START_Z'])
    right.plot(angles[keep], xyz[keep, 0], color=color, lw=1.8, label=label)
right.axhline(0, color='#667085', lw=.8, ls='--')
right.axvline(70, color='#667085', lw=1, ls=':')
right.text(71.5, .47, 'Assembly joint', color='#667085', fontsize=9)
right.set(xlabel='Position around the gooseneck bend (degrees)',
          ylabel='Lateral position from rear center (mm)',
          title='Base and tip: the same rear meridian', xlim=(8, 127), ylim=(-.25, .62))
right.legend(loc='upper left', fontsize=8)
for ax in (left, right): ax.grid(alpha=.15)
fig.suptitle('Actual commanded seam starts', fontsize=15, x=.09, ha='left')
fig.tight_layout(rect=(0, 0, 1, .95))
fig.savefig(HERE / 'seam-comparison.png', dpi=180)
