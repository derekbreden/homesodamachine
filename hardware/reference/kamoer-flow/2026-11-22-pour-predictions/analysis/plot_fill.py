"""Plot paired dose differences at the two cup levels against the preset equivalence limit."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


def plot(results, name):
    fig, ax = plt.subplots(figsize=(8.3, 4.6), layout='constrained')
    ax.axvspan(-1, 1, facecolor='#dff2eb')
    ax.axvline(0, color='#74828a', linewidth=.9)
    colors = {'x990':'#155876', 'x1986':'#9c5027'}
    yvalues, labels = [], []
    for i, head in enumerate(('A','B')):
        for j, site in enumerate(('x990','x1986')):
            y = 3 - (2*i+j)
            z = results[head][site]['paired']
            yvalues.append(y)
            labels.append(f'Pump {head} · '+('first sightline' if j==0 else 'second sightline'))
            diffs = z['high_minus_low_dose_ml']
            offsets = (0,.044,-.047,.085,-.08,.12)
            ax.scatter(diffs,[y+.15+offsets[k] for k in range(len(diffs))],
                       s=28,edgecolors='white',linewidths=.5,c=colors[site])
            if z['interval_90_ml']:
                lo,hi=z['interval_90_ml']
                ax.plot([lo,hi],[y-.10,y-.10],color=colors[site],linewidth=2.5,solid_capstyle='round')
                ax.scatter([z['mean_difference_ml']],[y-.10],marker='D',s=36,c=colors[site])
    ax.set_yticks(yvalues,labels)
    ax.set_ylim(-.55,3.65)
    ax.set_xlabel('Dose with cup high minus dose with cup low (nominal mL)')
    ax.set_title('Does cup level change a five-burst dose?',loc='left',fontweight='bold',fontsize=16,pad=12)
    ax.spines[['top','right','left']].set_visible(False)
    ax.tick_params(axis='y',length=0)
    ax.grid(axis='x',alpha=.18)
    ax.legend(handles=[Line2D([],[],marker='o',color='#52616b',linestyle='',label='Matched pair'),
                       Line2D([],[],color='#52616b',marker='D',label='Mean and 90% interval'),
                       Patch(facecolor='#dff2eb',label='Equivalence margin')],
              loc='upper center',bbox_to_anchor=(.5,-.16),ncols=3,frameon=False)
    fig.savefig(name,dpi=170)
    plt.close(fig)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('scores',type=Path)
    ap.add_argument('figure',type=Path)
    args=ap.parse_args()
    plot(json.loads(args.scores.read_text()),args.figure)
