"""Embed theme/size-matched native CAD renders in the conversation fragment."""
from pathlib import Path
import argparse,base64,hashlib,io,json
from PIL import Image

HERE=Path(__file__).resolve().parent
VIEWS=[('overview','Above the cold core'),('top','Upper bay top'),('pump-water','Pump and water'),
       ('gas-water','CO₂ and carbonated water'),('electronics','Electronics and wiring'),
       ('mounts','Mounts and fasteners'),('rear','Rear connections'),
       ('funnel','Funnel and drain'),('enclosure','Enclosure and roof'),
       ('front-closure','Front closure staging'),('funnel-tooling','Funnel casting molds')]

def main(output):
    render_check=json.loads((HERE/'renders/gallery/check.json').read_text())
    viewer_sha=hashlib.sha256((HERE/'index.html').read_bytes()).hexdigest()
    if not render_check.get('pass') or render_check.get('viewer_sha256')!=viewer_sha:
        raise ValueError('Current successful native gallery rendering is required')
    funnel=json.loads((HERE/'funnel/candidate.json').read_text())
    readings=[f"{funnel['capacity_to_brim_ml']:.0f} mL to brim",
              f"{funnel['capacity_10mm_below_brim_ml']:.0f} mL at 10 mm headroom",'215 mm width']
    images=[];inputs={}
    for key,label in VIEWS:
        view={'id':key,'label':label,'description':label+' · Native geometry of the pump-first layout above the cold-core lid.','images':{}}
        for theme in ['light','dark']:
            for size in ['small','large']:
                path=HERE/f'renders/gallery/{key}-{theme}-{size}.png'
                inputs[str(path.relative_to(HERE))]=hashlib.sha256(path.read_bytes()).hexdigest()
                buffer=io.BytesIO()
                Image.open(path).save(buffer,format='WEBP',quality=70,method=6)
                view['images'][theme+'-'+size]='data:image/webp;base64,'+base64.b64encode(buffer.getvalue()).decode()
        images.append(view)
    data={'views':images,'readings':readings}
    fragment=(HERE/'gallery.template.html').read_text().replace('__NATIVE_GALLERY_DATA__',json.dumps(data,separators=(',',':')))
    if len(fragment.encode())>=1_000_000:raise ValueError('Inline gallery exceeds1MB: '+str(len(fragment.encode())))
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(fragment)
    (HERE/'renders/gallery/source.json').write_text(json.dumps({'inputs':inputs,'bytes':len(fragment.encode()),
        'image_format':'WEBP','image_quality':70,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'viewer_sha256':viewer_sha,'render_check_sha256':hashlib.sha256((HERE/'renders/gallery/check.json').read_bytes()).hexdigest()},indent=2)+'\n')
    print(json.dumps({'path':str(output),'bytes':len(fragment.encode())}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);main(p.parse_args().output)
