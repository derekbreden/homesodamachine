"""Draw native sections of the two-piece coupon's entry and latched states."""
from pathlib import Path
import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import integral_latch_coupon as c

HERE=Path(__file__).resolve().parent


def section(ax,body,plane,height,axes,color,style='-'):
    shape=cq.Workplane(plane).newObject([body]).section(height).val()
    for edge in shape.Edges():
        vertices=edge.Vertices()
        if len(vertices)==2:
            pts=[v.toTuple() for v in vertices]
            ax.plot([p[axes[0]] for p in pts],[p[axes[1]] for p in pts],style,color=color,lw=1.5)


def main():
    fig,axs=plt.subplots(1,3,figsize=(14,6),gridspec_kw={'width_ratios':[1,1,.62]},constrained_layout=True)
    for ax,amount,shift,title in zip(axs[:2],(c.DEFLECTION,0.),(-c.v1.TRAVEL,0.),
            ('1  Existing forward entry','2  Existing outward slide')):
        section(ax,c.left_half(),'XY',14.3,(0,1),'#285F87')
        section(ax,c.right_half(amount).translate((shift,0,0)),'XY',14.3,(0,1),'#8A468D')
        ax.set_aspect('equal');ax.set_xlim(-7,15);ax.set_ylim(-6.5,9)
        ax.set_xlabel('Native X (mm)');ax.set_ylabel('Native Y (mm) · aft ↑');ax.set_title(title)
        ax.grid(alpha=.18)
    axs[0].annotate('Push receiver\ntoward the lap',xy=(10,4),xytext=(10,7.8),ha='center',va='top',fontsize=10,
        arrowprops={'arrowstyle':'->','color':'#8A468D'},color='#8A468D')
    axs[0].annotate('Key presses wall aft',xy=(1.8,4.25),xytext=(-5.7,7.5),
        arrowprops={'arrowstyle':'->','color':'#285F87'},color='#285F87')
    axs[1].annotate('3.25 mm outward',xy=(11,-2.2),xytext=(3,-2.2),va='center',
        arrowprops={'arrowstyle':'->','color':'#8A468D'},color='#8A468D')
    axs[1].annotate('Lip returns beside key;\n1.2 mm positive engagement',xy=(3.95,3.3),xytext=(2,7.5),ha='center',
        arrowprops={'arrowstyle':'->','color':'#8A468D'},color='#8A468D')
    ax=axs[2]
    section(ax,c.union([c.flexible_wall(),c.lip()]),'YZ',5.5,(1,2),'#8A468D')
    section(ax,c.union([c.flexible_wall(c.DEFLECTION),c.lip(c.DEFLECTION)]),'YZ',5.5,(1,2),'#CB7E34','--')
    ax.axhline(c.ROOT_Z,color='#555',lw=.8)
    ax.set_aspect(.42);ax.set_xlim(1.5,9);ax.set_ylim(9,49)
    ax.set_xlabel('Native Y (mm)\n1.35 mm tip travel');ax.set_ylabel('Native Z (mm)')
    ax.set_title('Broad wall side section\n13 mm wide · 1.3 mm thick\nEffective length 30.25 mm',fontsize=10)
    ax.grid(alpha=.18)
    fig.suptitle('Two pieces, one normal seating motion · blue: retained left · purple: integral receiver',fontsize=13)
    fig.text(.5,.006,'Native sections. Dashed orange is a prescribed clearance shape, not a force prediction. Side view expands horizontal scale.',ha='center',fontsize=9)
    fig.savefig(HERE/'motion.svg')
    svg=HERE/'motion.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    fig.savefig(HERE/'motion.png',dpi=150)
    plt.close(fig)


if __name__=='__main__':main()
