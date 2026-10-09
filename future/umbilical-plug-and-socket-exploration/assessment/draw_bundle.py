"""Render the nominal bundle study; dimensions are not a physical fit result."""
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import geometry_review as g

COLORS = {"soda": "#428dc5", "flavor-a": "#e8bd50", "flavor-b": "#e8bd50",
          "drain": "#d5d7dc"}


def section(ax, packed):
    review = g.bundle_review()
    soda = g.u.PORTS["soda"][:2]
    if packed:
        axes = g.PACK
        c = review["bare_pack_enclosing_diameter_mm"] / 2 - g.FOAM_R
        center = (soda[0], soda[1] + c)
        radius = review["proposed_outer_envelope_mm"] / 2
    else:
        axes = {n: p[:2] for n, p in g.u.PORTS.items()}
        b = axes["flavor-b"]
        length = math.dist(soda, b)
        bare = review["straight_foam_at_plug_pair_diameter_lower_bound_mm"] / 2
        factor = (bare - g.FOAM_R) / length
        center = tuple(a + (b - a) * factor for a, b in zip(soda, b))
        radius = bare + 1.3
    ax.add_patch(Circle((0, 0), g.u.COUNTER_HOLE / 2, fill=False,
                        lw=2, color="#395f6a", label="34.93 mm counter hole"))
    ax.add_patch(Circle((0, 0), radius, fill=False, linestyle="--",
                        lw=1.5, color="#955451", label="Nominal braid/cable allowance"))
    for n, (x, z) in axes.items():
        x, z = x - center[0], z - center[1]
        if n == "soda":
            ax.add_patch(Circle((x, z), g.FOAM_R, color="#727b81"))
        ax.add_patch(Circle((x, z), g.u.PORTS[n][2] / 2,
                            facecolor=COLORS[n], edgecolor="#4b5159", lw=.8))
        if n == "soda":
            ax.text(x, z - 6, "Soda foam", ha="center", color="white", fontsize=9)
    ax.set(xlim=(-24, 24), ylim=(-24, 24), aspect="equal")
    ax.axis("off")
    ax.set_title("Smaller tubes beside the foam" if packed else "Foam at the plug's tube positions",
                 fontsize=11, pad=5)
    description = ("34.61 mm nominal envelope\nCompression can add clearance" if packed else
                   "38.71 mm uncompressed, before braid/cable\nTry deliberate foam compression")
    ax.text(0, -24, description, ha="center", va="top", fontsize=10)


def main():
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 5.8))
    fig.patch.set_facecolor("#faf9f7")
    section(axes[0], False)
    section(axes[1], True)
    fig.suptitle("Foam compression may simplify the boot", fontsize=16, y=.96)
    fig.text(.5, .035, "Uncompressed cross sections at equal scale; neither predicts compressed foam shape.\n"
             "Solid circle: counter hole. Dashed: 1.3 mm braid/cable allowance. Test direct compression before a fan.",
             ha="center", fontsize=9, color="#4b5159")
    fig.subplots_adjust(top=.83, bottom=.22, left=.04, right=.96, wspace=.16)
    fig.savefig(HERE / "bundle-study.png", dpi=170, facecolor=fig.get_facecolor())


if __name__ == "__main__":
    main()
