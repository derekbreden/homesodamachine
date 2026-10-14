"""Read the three exact native seam paths by hand; this never sends a print."""
from pathlib import Path
from zipfile import ZipFile
import csv,hashlib,json,re,sys
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/bambu_print.py').is_file())
sys.path.insert(0,str(ROOT/'hardware/scripts'))
from enclosure_support_audit import _arc_points
PARTS={1901:True}
WORD=re.compile(r'([XYZEFIJP])([-+]?(?:\d*\.\d+|\d+\.?\d*))')
def read_runs(archive, parts=None):
    """Follow emitted exterior-wall motions, joining numerical scarf connectors.

    ``parts`` selects identify IDs. This is a manual reader, never a send gate.
    Match the shared reader: a move with an E word continues the wall even
    when its flow rounds to zero. An E-less hop continues an existing wall
    only within 0.02 mm in XY and 0.002 mm in Z. Retractions end the run.
    """
    wanted_parts = PARTS if parts is None else set(parts)
    with ZipFile(archive) as z:
        gcode = z.read('Metadata/plate_1.gcode')
        # A one-object slice uses OBJECT_ID markers instead of named start blocks.
        import xml.etree.ElementTree as ET
        objects = ET.fromstring(z.read('Metadata/slice_info.config')).findall('.//object')
        single_label = int(objects[0].get('identify_id')) if len(objects) == 1 else None
    current = None
    feature = ''
    layer = None
    xyz = np.zeros(3)
    rel_e = True
    abs_xyz = True
    e = 0.0
    rows = []
    run = None
    def finish():
        nonlocal run
        if run is not None:
            pts = np.array(run['points'])
            run['points'] = pts
            run['length'] = float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())
            run['gap'] = float(np.linalg.norm(pts[-1] - pts[0]))
            run['z_range'] = float(np.ptp(pts[:, 2]))
            a, b = pts[-1, :2] - pts[-2, :2], pts[1, :2] - pts[0, :2]
            den = np.linalg.norm(a) * np.linalg.norm(b)
            run['seam_angle'] = float(180 - np.degrees(np.arccos(np.clip(a @ b / den, -1, 1)))) if den else None
            xy = pts[:, :2]
            run['area'] = float(0.5 * np.sum(xy[:, 0] * np.roll(xy[:, 1], -1) - xy[:, 1] * np.roll(xy[:, 0], -1)))
            rows.append(run)
            run = None
    for line_number, raw in enumerate(gcode.decode().splitlines(), 1):
        line = raw.strip()
        start = re.match(r'; start printing object, unique label id: (\d+)', line)
        if start:
            finish(); current = int(start.group(1))
        elif single_label is not None and line.startswith('; OBJECT_ID:'):
            finish(); current = single_label if int(line.split(':', 1)[1]) >= 0 else None
        elif line.startswith('; stop printing object'):
            finish(); current = None
        elif line.startswith('; Z_HEIGHT:'):
            finish(); current = None; layer = float(line.split(':', 1)[1])
        elif line.startswith('; FEATURE:'):
            new = line.split(':', 1)[1].strip()
            if new not in ('Outer wall', 'Overhang wall'):
                finish()
            feature = new
        code = line.split(';', 1)[0].strip()
        if not code:
            continue
        cmd = code.split()[0]
        w = {k: float(v) for k, v in WORD.findall(code)}
        if cmd in ('G90', 'G91'):
            abs_xyz = cmd == 'G90'
        elif cmd in ('M82', 'M83'):
            rel_e = cmd == 'M83'
        elif cmd == 'G92':
            xyz = np.array([w.get(k, xyz[i]) for i, k in enumerate('XYZ')])
            e = w.get('E', e)
        elif cmd in ('G0', 'G1', 'G2', 'G3'):
            nxt = np.array([w.get(k, xyz[i]) if abs_xyz else xyz[i] + w.get(k, 0) for i, k in enumerate('XYZ')])
            de = w.get('E', 0) if rel_e else w.get('E', e) - e
            step = np.linalg.norm(nxt[:2] - xyz[:2])
            moving_xy = step > 1e-9
            wanted = current in wanted_parts and layer is not None and feature in ('Outer wall', 'Overhang wall')
            extruding = 'E' in w and de >= 0
            connector = (run is not None and wanted and 'E' not in w
                         and 0 < step <= .02 and abs(nxt[2] - xyz[2]) <= .002)
            if wanted and moving_xy and (extruding or connector):
                if cmd in ('G2', 'G3'):
                    xy = _arc_points(tuple(xyz[:2]), tuple(nxt[:2]), w, cmd == 'G2')
                if run is None:
                    run = {'object': current, 'layer': layer, 'line': line_number,
                           'points': [xyz.copy()], 'point_lines': [line_number],
                           'features': [], 'numerical_connectors': 0}
                run['end_line'] = line_number
                if feature not in run['features']:
                    run['features'].append(feature)
                run['numerical_connectors'] += int(connector or ('E' in w and de == 0))
                if cmd in ('G2','G3'):
                    run['points'].extend(np.array([x,y,xyz[2]+(nxt[2]-xyz[2])*(i+1)/len(xy)]) for i,(x,y) in enumerate(xy))
                    run['point_lines'].extend([line_number] * len(xy))
                else:
                    run['points'].append(nxt.copy())
                    run['point_lines'].append(line_number)
            elif moving_xy or de < 0:
                finish()
            xyz = nxt
            if 'E' in w:
                e = e + w['E'] if rel_e else w['E']
    finish()
    return rows, hashlib.sha256(gcode).hexdigest()

def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    base=ROOT/'hardware/printed-parts/faucet/industrial/prints'
    latest=next((base/'2026-10-13-a2-back-mark2').glob('*.print.json'))
    report=json.loads(latest.read_text())
    p=next(p for p in report['parts'] if 'shell-base' in p['name'])
    rotation=np.array(p['build_transform'][:9]).reshape(3,3)
    trans=np.array(p['plate_translation_mm']);center=np.array(p['source_center_mm'])
    inputs={
        'older':next((base/'2026-10-11-scarf10-lift8-mark1').glob('*.gcode.3mf')),
        'printed':next((base/'2026-10-13-a2-back-mark2').glob('*.gcode.3mf')),
        'corrected':HERE/'2026-10-13-industrial-faucet-rear-seam-petgf-left04-z004-mark2.gcode.3mf',
    }
    data={};csv_rows=[]
    fig,ax=plt.subplots(figsize=(7.2,6.4))
    styles={'older':('#4169a1','Older print · Oct 11'),'printed':('#d66b24','Last print · Oct 13'),'corrected':('#27815e','Corrected slice · not printed')}
    for label,archive in inputs.items():
        runs,digest=read_runs(archive)
        largest={}
        for run in runs:
            z=run['layer']
            if z not in largest or abs(run['area'])>abs(largest[z]['area']):largest[z]=run
        rows=[]
        for z,run in sorted(largest.items()):
            pts=run['points'];start=(pts[0]-trans)@rotation.T+center;end=(pts[-1]-trans)@rotation.T+center
            if not 80<=start[2]<=237:continue
            rows.append({'print_z_mm':z,'gcode_line':run['line'],'start_plate_mm':pts[0].tolist(),'start_cad_mm':start.tolist(),'end_cad_mm':end.tolist(),'scarf_z_range_mm':run['z_range']})
            csv_rows.append([label,z,run['line'],*start,*end])
        peak=max(rows,key=lambda row:abs(row['start_cad_mm'][0]))
        data[label]={'archive':str(archive.relative_to(ROOT)),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'gcode_sha256':digest,'measured_contours':len(rows),'maximum_lateral_start_offset_mm':abs(peak['start_cad_mm'][0]),'maximum_offset_witness':peak}
        xy=np.array([row['start_cad_mm'] for row in rows]);color,title=styles[label]
        ax.plot(xy[:,0],xy[:,2],color=color,label=title,lw=2.2,alpha=.95)
    ax.axvline(0,color='#667085',lw=.9,ls='--',alpha=.6)
    ax.set_xlim(-3,15);ax.set_ylim(80,239)
    ax.set_xlabel('Lateral position from the rear centerline (mm)')
    ax.set_ylabel('Height above the base bottom, CAD Z (mm)')
    ax.set_title('Base gooseneck: actual outer-wall starts',loc='left',pad=16)
    ax.text(-2.7,234,'Rear center',fontsize=9,color='#667085')
    ax.annotate('12.3 mm swerve',xy=(12.278,165.364),xytext=(6.2,203),arrowprops={'arrowstyle':'->','color':'#d66b24'},color='#aa501e',fontsize=11)
    ax.legend(loc='lower right',frameon=True,fontsize=9)
    ax.grid(alpha=.15);fig.tight_layout();fig.savefig(HERE/'seam-comparison.png',dpi=180);plt.close(fig)
    with (HERE/'seam-starts.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['sample','print_z_mm','gcode_line','start_cad_x_mm','start_cad_y_mm','start_cad_z_mm','end_cad_x_mm','end_cad_y_mm','end_cad_z_mm']);writer.writerows(csv_rows)
    summary={'schema':1,'method':'Largest projected-area emitted outer-wall run at each layer, converted with the unchanged base build transform to assembly CAD coordinates. Start locations identify the start of the scarf ramp. End locations are retained in the CSV; they are not the same point for a long scarf.','cad_z_scope_mm':[80,237],'samples':data,'reference_task_id':'1329852853','printed_task_id':'1335906696','candidate_submitted':False}
    (HERE/'seam-review.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v['maximum_lateral_start_offset_mm'] for k,v in data.items()}))
if __name__=='__main__':main()
