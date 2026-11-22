"""Compare both candidate fronts in consecutive native photographs of the same stationary fill."""
import argparse
import json
from pathlib import Path
import numpy as np

LABELS=('ladder2-down-low-00','ladder2-down-low-inside-hold5')
REGIONS=((990,1033,17),(990,1095,23),(1986,1066,23))


def pack(camera,out):
    from PIL import Image
    boxes=[(x-27,995,x+28,1131) for x in (990,1986)];images=[];times=[]
    for name in LABELS:
        folder=camera/'windows'/name
        with Image.open(folder/'average.png') as im:images.append([np.asarray(im.crop(box)) for box in boxes])
        times.append(json.loads((folder/'window.json').read_text())['mid']['pts_ns'])
    np.savez_compressed(out,native_crops=np.array(images),boxes=np.array(boxes),window_labels=np.array(LABELS),pts_ns=times)


def inspect(path):
    with np.load(path) as z:
        full=z['native_crops'];boxes=z['boxes'];times=z['pts_ns'];names=z['window_labels'].tolist()
    result={'windows':names,'native_average_mid_pts_ns':times.tolist(),'sites':{}}
    for x,y,half_width in REGIONS:
        i=0 if x==990 else 1
        x0,y0,x1,y1=boxes[i]
        native_rows=np.arange(y0,y1)
        cols=full[:,i,:,x-x0-4:x-x0+5].mean(axis=2)
        target=np.arange(y-half_width,y+half_width+1)
        a=cols[0,target-y0]
        shifts=np.arange(-6,6.001,.05);deviation=[]
        for s in shifts:
            b=np.interp(target+s,native_rows,cols[1])
            deviation.append(np.sum(((a-a.mean())/a.std()-(b-b.mean())/b.std())**2))
        actual=cols[1,target-y0]
        result['sites'][f'x{x}-y{y}']={'native_columns_inclusive':[x-4,x+4],'native_rows_inclusive':[int(target[0]),int(target[-1])],
            'apparent_dy_from_local_shape_px':round(float(shifts[np.argmin(deviation)]),2),
            'zero_shift_profile_correlation':float(np.corrcoef(a,actual)[0,1]),
            'zero_shift_luma_rms':float(np.sqrt(np.mean((a-actual)**2)))}
    return result


def plot(path,dest):
    import matplotlib
    matplotlib.use('Agg');import matplotlib.pyplot as plt
    with np.load(path) as z:
        im=z['native_crops'];boxes=z['boxes']
    fig,axes=plt.subplots(1,3,figsize=(8.8,3.7),layout='constrained',gridspec_kw={'width_ratios':[.75,.75,1.35]})
    for i,ax in enumerate(axes[:2]):
        ax.imshow(im[i,0],cmap='gray',vmin=16,vmax=155,extent=(962.5,1017.5,1130.5,994.5),aspect='auto')
        ax.axhline(1033,color='#ff7f0e',lw=.9);ax.axhline(1095,color='#59b9ff',lw=.9)
        ax.set(title=('Start photograph','5 s photograph')[i],xlabel='Native x (px)')
    axes[0].set_ylabel('Native y (px)');axes[1].tick_params(labelleft=False)
    ax=axes[2];r=np.arange(995,1131)
    for i,(descr,color,ls) in enumerate([('Start','#1c456b','-'),('5 s','#ca5d28','--')]):
        ax.plot(im[i,0,:,23:32].mean(axis=1),r,color=color,linestyle=ls,label=descr,lw=1.4)
    ax.axhline(1033,color='#e67c23',lw=.7);ax.axhline(1095,color='#428abd',lw=.7)
    ax.set(title='Mean luma across x990',xlabel='Camera luma',ylim=(1130.5,994.5));ax.legend(frameon=False)
    fig.suptitle('Two nearly stationary features at the low fill',fontsize=13)
    fig.savefig(dest,dpi=170);plt.close(fig)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('pack');p.add_argument('camera',type=Path);p.add_argument('out',type=Path)
    p=sub.add_parser('inspect');p.add_argument('recording',type=Path);p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('plot');p.add_argument('recording',type=Path);p.add_argument('out',type=Path)
    a=parser.parse_args()
    if a.action=='pack':pack(a.camera,a.out)
    elif a.action=='inspect':a.out.write_text(json.dumps(inspect(a.recording),indent=2)+'\n')
    else:plot(a.recording,a.out)
