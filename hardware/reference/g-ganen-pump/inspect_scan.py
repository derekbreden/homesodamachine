"""Plot preserved native observations in three orthographic views for region selection."""
from pathlib import Path
import argparse
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from scan_tools import load_cloud, transform_points


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cloud', type=Path)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--transform', type=Path,
                        help='JSON 4 by 4 proper rigid native-to-inspection transform')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--max-points', type=int, default=120000)
    args = parser.parse_args()
    points, _, metadata = load_cloud(args.cloud, args.sha256)
    if args.transform:
        points = transform_points(points, json.loads(args.transform.read_text()))
    step = max(1, int(np.ceil(len(points)/args.max_points)))
    shown = points[::step]
    fig, axes = plt.subplots(1, 3, figsize=(17, 6), constrained_layout=True)
    for ax, (a, b, depth) in zip(axes, ((0, 1, 2), (0, 2, 1), (1, 2, 0))):
        order = np.argsort(shown[:, depth])
        selected = shown[order]
        ax.scatter(selected[:, a], selected[:, b], c=selected[:, depth], s=.25,
                   cmap='viridis', rasterized=True, linewidths=0)
        ax.set_aspect('equal')
        ax.set_xlabel('XYZ'[a]+' (mm)')
        ax.set_ylabel('XYZ'[b]+' (mm)')
        ax.set_title('XYZ'[a]+' / '+'XYZ'[b]+'; color = '+'XYZ'[depth])
        ax.grid(alpha=.15)
    frame = 'inspection frame' if args.transform else 'native scanner frame'
    fig.suptitle(f"{args.cloud.parent.name} · {frame}\n"
                 f"{metadata['points']:,} preserved observations; display stride {step}; "
                 f"SHA-256 {metadata['sha256'][:16]}", fontsize=12)
    fig.savefig(args.out, dpi=180)
    plt.close(fig)
    print(json.dumps(metadata | {'display_stride': step, 'output': str(args.out)}, indent=2))


if __name__ == '__main__':
    main()
