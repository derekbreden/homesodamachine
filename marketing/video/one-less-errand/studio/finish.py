#!/usr/bin/env python3
"""Assemble the connected errand story, or a full sound-and-picture animatic."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont
import carbonation
from timing import load_story

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OUT = HERE / 'out'
W, H, FPS = 1920, 1080, 24
COBALT, ICE, WHITE = (23,73,209), (220,230,255), (255,255,255)
FONT = HERE / 'fonts/Montserrat.ttf'
BRAND = REPO / 'web/public/brand'
COLOR = 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709,setsar=1'


def run(args):
    return subprocess.run(list(map(str,args)),check=True)


def ffmpeg(*args):
    return ['ffmpeg','-hide_banner','-loglevel','warning','-filter_complex_threads','2','-nostdin','-y',*map(str,args)]


def font(size,weight=500):
    result=ImageFont.truetype(str(FONT),size)
    result.set_variation_by_axes([weight])
    return result


def wordmark(target,width=340):
    code="const sharp=require(process.argv[1]);sharp(process.argv[2],{density:288}).trim({threshold:2}).resize({width:Number(process.argv[4])}).png().toFile(process.argv[3]);"
    run(['node','-e',code,REPO/'tools/render/node_modules/sharp',BRAND/'wordmark.svg',target,width])
    return Image.open(target).convert('RGBA')


def text_layer(lines,size,weight=500,color=COBALT,leading=1.05):
    face=font(size,weight)
    width=math.ceil(max(face.getlength(line) for line in lines))+12
    result=Image.new('RGBA',(width,round(size*leading*len(lines)+size*.5)))
    draw=ImageDraw.Draw(result)
    for i,line in enumerate(lines):
        draw.text((0,round(i*size*leading)),line,font=face,fill=color,anchor='lt',stroke_width=0)
    return result.crop(result.getbbox())


def assets(work,story):
    # Each overlay has one semantic entrance; picture stays visible underneath.
    logo=wordmark(work/'wordmark.png')
    def layer(content,xy):
        canvas=Image.new('RGBA',(W,H))
        canvas.alpha_composite(content,xy)
        return canvas
    data={
      'opening':[
        (layer(text_layer(['A glass','of soda.'],88,550,leading=1.02),(128,325)),.55,.22),
        (layer(text_layer(['IN DEVELOPMENT  ·  PRODUCT VISUALIZATION'],22,500,COBALT),(135,80)),0,.15)
      ],
      'case':[
        (layer(text_layer(['Somehow,'],92,550,WHITE),(128,325)),.08,.18),
        (layer(text_layer(['a trip to the store.'],38,450,ICE),(135,480)),story.get('type_timing',{}).get('case_store',1.05),.18)
      ],
      'car':[
        (layer(text_layer(['Into the car.'],64,500,WHITE),(128,380)),.02,.12)
      ],
      'kitchen':[
        (layer(text_layer(['Into the','kitchen.'],64,500,COBALT),(128,350)),.02,.12)
      ],
      'shelf':[
        (layer(text_layer(['Onto a shelf.'],64,500,WHITE),(128,380)),.02,.12)
      ],
      'repeat':[
        (layer(text_layer(['Another trip.'],78,500,WHITE),(128,300)),1.90,.12,2.50),
        (layer(text_layer(['And another.'],78,500,WHITE),(128,300)),3.00,.12,3.58),
        (layer(text_layer(['And another.'],78,500,WHITE),(128,300)),3.80,.12,4.45)
      ],
      'question':[
        (layer(text_layer(['What if the','next glass was','already waiting?'],62,500,WHITE,leading=1.15),(128,300)),.10,.20)
      ],
      'hero':[
        (layer(text_layer(['Already','here.'],112,550,leading=1.03),(128,314)),.08,.22),
        (layer(text_layer(['IN DEVELOPMENT  ·  PRODUCT VISUALIZATION'],22,500,COBALT),(135,80)),0,.15)
      ],
      'serve':[
        (layer(logo,(133,194)),0,.15),
        (layer(text_layer(['One less','errand.'],111,550,leading=1.03),(126,391)),1.65,.22),
        (layer(text_layer(['Explore the machine'],32,500,COBALT),(135,710)),2.40,.18),
        (layer(text_layer(['homesodamachine.com'],36,600,COBALT),(135,763)),2.40,.18),
        (layer(text_layer(['IN DEVELOPMENT  ·  PRODUCT VISUALIZATION'],22,500,COBALT),(135,80)),0,.15)
      ]
    }
    for shot,layers in data.items():
        for i,entry in enumerate(layers):
            entry[0].save(work/f'{shot}-type-{i}.png')
    return data


def encoder(draft=False):
    return ['-c:v','libx264','-preset','veryfast' if draft else 'slow','-crf','19' if draft else '16',
            '-threads','2' if draft else '0','-r',str(FPS),'-video_track_timescale','24000','-color_range','tv',
            '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart']


def encode_carbonation(shot, target):
    command=ffmpeg('-f','rawvideo','-pix_fmt','rgba','-s',f'{W}x{H}',
                  '-framerate',FPS,'-i','pipe:0','-an','-c:v','qtrle',
                  '-pix_fmt','argb','-threads','2',target)
    proc=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for i in range(shot['frames']):
            proc.stdin.write(carbonation.draw(shot['start']+i/FPS,width=W,height=H).tobytes())
        proc.stdin.close()
        if proc.wait():raise RuntimeError('Carbonation overlay encode failed')
    except BaseException:
        proc.kill();proc.wait();raise


def encode_picture(shot,target,args,work,type_assets):
    duration=shot['frames']/FPS
    rate=args.rates.get(shot['id'],args.fps)
    folder=args.frames/shot['id']
    files=sorted(folder.glob('[0-9]*.png'))
    prefix,source,input_count='','[0:v]',1
    if shot['kind']=='photograph':
        bubbles=work/f'{shot["id"]}-carbonation.mov'
        encode_carbonation(shot,bubbles)
        command=ffmpeg('-loop','1','-framerate',FPS,'-i',HERE/shot['asset'],'-i',bubbles)
        prefix=f'[0:v]scale={W}:{H}:flags=lanczos[plate];[plate][1:v]overlay=shortest=1:format=auto[animated];'
        source,input_count='[animated]',2
        base,travel,focus=(1.32,.028,.91) if shot['id']=='sensory' else (1.005,.018,.62)
        cadence=(f'scale=2304:1296:flags=lanczos,zoompan=z={base}+{travel}*on/{shot["frames"]}:'
                 f'x=(iw-iw/zoom)*{focus}:y=(ih-ih/zoom)*0.45:d=1:s={W}x{H}:fps={FPS},'
                 f'trim=duration={duration},setpts=PTS-STARTPTS')
    elif not files: raise SystemExit(f'No source frames for {shot["id"]}: {folder}')
    elif args.animatic or shot.get('hold'):
        command=ffmpeg('-loop','1','-framerate',FPS,'-i',files[len(files)//2])
        cadence=f'fps={FPS},trim=duration={duration},setpts=PTS-STARTPTS'
    else:
        needed=math.ceil(duration*rate)
        missing=[i for i in range(needed) if not (folder/f'{i:05d}.png').exists()]
        if missing: raise SystemExit(f'{shot["id"]}: missing source frame {missing[0]:05d}.png')
        command=ffmpeg('-framerate',rate,'-i',folder/'%05d.png')
        if rate<FPS:
            pre,post=2/rate,3/rate
            cadence=(f'tpad=start_mode=clone:start_duration={pre}:stop_mode=clone:stop_duration={post},'
              f'minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:me=epzs:mb_size=16:search_param=24:vsbmc=1,'
              f'trim=start={pre}:duration={duration},setpts=PTS-STARTPTS')
        else: cadence=f'fps={FPS},trim=duration={duration},setpts=PTS-STARTPTS'
    graph=prefix+f'{source}{cadence},scale={W}:{H}:flags=lanczos,setsar=1[p0];'
    previous='p0'
    for i,entry in enumerate(type_assets.get(shot['id'],[]),1):
        start,fade=entry[1:3]
        command+=['-loop','1','-framerate',str(FPS),'-i',str(work/f'{shot["id"]}-type-{i-1}.png')]
        type_filter=f'format=rgba,fade=t=in:st={start}:d={fade}:alpha=1'
        if len(entry)>3:
            type_filter+=f',fade=t=out:st={entry[3]-fade}:d={fade}:alpha=1'
        graph+=f'[{i+input_count-1}:v]{type_filter}[t{i}];'
        graph+=f'[{previous}][t{i}]overlay=shortest=1:format=auto[p{i}];'
        previous=f'p{i}'
    graph+=f'[{previous}]{COLOR}[out]'
    run(command+['-filter_complex',graph,'-map','[out]','-an','-frames:v',str(shot['frames']),*encoder(args.draft),str(target)])


def previews(args,story):
    closing=next(s for s in story['scenes'] if s['id']=='serve')
    poster_at=closing['start']+(closing['end']-closing['start'])*.75
    run(ffmpeg('-ss',poster_at,'-i',args.out/'film.mp4','-frames:v','1','-update','1','-q:v','2',args.out/'poster.jpg'))
    samples=[]
    for shot in story['scenes']:
        fractions={'case':[.25,.90],'repeat':[.15,.45,.85],'serve':[.15,.80]}.get(shot['id'],[.55])
        samples.extend(round((shot['start']+(shot['end']-shot['start'])*p)*FPS) for p in fractions)
    selected='+'.join(f'eq(n,{n})' for n in sorted(set(samples)))
    rows=math.ceil(len(set(samples))/3)
    run(ffmpeg('-i',args.out/'film.mp4','-vf',f"select='{selected}',scale=480:270,tile=3x{rows}",
               '-frames:v','1','-update','1','-q:v','2',args.out/'contact-sheet.jpg'))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--frames',type=Path,default=OUT/'frames')
    p.add_argument('--fps',type=float,default=24)
    p.add_argument('--source-fps',action='append',default=[])
    p.add_argument('--audio',type=Path,default=OUT/'mix-master.wav')
    p.add_argument('--out',type=Path,default=OUT)
    p.add_argument('--timing',type=Path,help='Optional processing-beat edit, applied to story.json')
    p.add_argument('--draft',action='store_true')
    p.add_argument('--force',action='store_true')
    p.add_argument('--animatic',action='store_true',help='Use a draft still for each CG shot with the complete timed audio and graphics')
    a=p.parse_args()
    a.rates={name:float(rate) for name,rate in (v.split('=',1) for v in a.source_fps)}
    a.out.mkdir(parents=True,exist_ok=True)
    work=a.out/'finish-assets';work.mkdir(exist_ok=True)
    segment_dir=a.out/'segments';segment_dir.mkdir(exist_ok=True)
    story=load_story(a.timing)
    typography=assets(work,story)
    if not a.audio.exists():p.error(f'Missing sound master: {a.audio}')
    cache_path=a.out/'.finish-cache.json'
    cache=json.loads(cache_path.read_text()) if cache_path.exists() else {}
    code_hash=hashlib.sha256(Path(__file__).read_bytes()+(HERE/'carbonation.py').read_bytes()).hexdigest()
    targets=[]
    for shot in story['scenes']:
        files=list((a.frames/shot['id']).glob('[0-9]*.png'))
        if shot['kind']=='photograph':files.append(HERE/shot['asset'])
        signature=hashlib.sha256(json.dumps({'shot':shot,'code':code_hash,'animatic':a.animatic,
          'rate':a.rates.get(shot['id'],a.fps),'draft':a.draft,'source':str(a.frames.resolve()),
          'type_timing':story.get('type_timing',{}),
          'frames':len(files),'modified':max((f.stat().st_mtime_ns for f in files),default=0)},sort_keys=True).encode()).hexdigest()
        target=segment_dir/f'{shot["id"]}.mp4'
        if a.force or cache.get(shot['id'])!=signature or not target.exists():
            print(f'Finishing {shot["id"]}: {shot["frames"]} frames',flush=True)
            encode_picture(shot,target,a,work,typography)
            cache[shot['id']]=signature;cache_path.write_text(json.dumps(cache,indent=2)+'\n')
        targets.append(target)
    sequence=work/'sequence.ffconcat'
    sequence.write_text('ffconcat version 1.0\n'+''.join("file '"+str(t.resolve()).replace("'","'\\''")+"'\n" for t in targets))
    run(ffmpeg('-f','concat','-safe','0','-i',sequence,'-i',a.audio,'-map','0:v:0','-map','1:a:0',
      '-c:v','copy','-c:a','aac','-b:a','320k','-ar','48000','-t',story['duration'],'-movflags','+faststart',
      '-metadata','title=One less errand. — Home Soda Machine',
      '-metadata','comment=In development · Product visualization',a.out/'film.mp4'))
    previews(a,story)
    for source,name in [(FONT,'Montserrat.ttf'),(BRAND/'wordmark-reverse.svg','brand.svg')]:
        shutil.copyfile(source,a.out/name)
    seconds=math.ceil(story['duration'])
    preview=(HERE/'preview.html').read_text().replace('{{DURATION}}',f'{seconds//60}:{seconds%60:02d}')
    (a.out/'index.html').write_text(preview)
    (a.out/'picture-clock.json').write_text(json.dumps(story,indent=2)+'\n')
    for name in ['film.vtt','film.srt']:
        source=a.audio.parent/name
        if source.exists() and source.resolve()!=(a.out/name).resolve():shutil.copyfile(source,a.out/name)
    print(a.out/'film.mp4',flush=True)

if __name__=='__main__':main()
