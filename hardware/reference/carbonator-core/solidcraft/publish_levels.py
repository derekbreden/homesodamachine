"""Publish shallow component manifests and the native project for the isolated assembly lab."""
import hashlib
import json
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parent
repo = root.parents[3]
web = repo / 'web/public/solidcraft-lab/carbonator'
native = root / 'native'
displays = json.loads((web / 'assets/native/index.json').read_text())['models']
labels = {
    'vessel-tube': 'Prepared carbonator tube', 'machined-cap': 'Machined endcap',
    'guide-rod': 'Float guide rod', 'upper-stop': 'Upper float stop',
    'float-shell': 'ASA Aero float shell', 'ring-magnet': 'RC62 ring magnet',
    'float': 'Magnetic level float', 'lower-cap': 'Bottom endcap and guide',
    'upper-cap': 'Top endcap and stop', 'weldment': 'Carbonator vessel weldment',
    'street-elbow': 'TAISHER street elbow', 'jet-cap': 'Water inlet jet cap',
    'inlet': 'Water-inlet jet elbow', 'pushfit-elbow': 'neoFit push-fit elbow',
    'relief-valve': 'SV125 pressure relief valve', 'prv-shroud': 'PRV shroud',
    'relief': 'Pressure-relief assembly', 'vessel': 'Carbonator vessel',
    'coil': 'Evaporator coil and tails', 'reed-bridge': 'Reed bridge',
    'probe': 'DS18B20 carbonator probe', 'probe-coil': 'DS18S20 coil probe',
    'reed': 'Carbonator reed switch', 'earth-screw': 'Earth clamp screw',
    'earth-washer': 'Earth lockwasher', 'earth-lead': 'Earth lead attachment',
    'instrumented': 'Instrumented carbonator and coil assembly',
    'instrumented-parent': 'Repeated assembly study',
}
refs = {'float', 'lower-cap', 'upper-cap', 'weldment', 'inlet', 'relief', 'vessel', 'instrumented'}
omit = {'float': ['RC62'], 'weldment': ['Vessel tube', 'Guide rod', 'Upper stop', 'ASA Aero']}
parameters = {'vessel-tube': ['length', 'outer_diameter', 'bore_diameter'],
              'machined-cap': ['thickness', 'cap_diameter', 'tap_pilot', 'register_diameter', 'register_depth'],
              'guide-rod': ['finished_length', 'diameter'], 'float-shell': ['diameter', 'height', 'guide_bore'],
              'weldment': ['float_z']}
fits = {
    'weldment': 'The caps retain their inset and port geometry. Open the cap groups or float to inspect their own parts. Section shows the saved shapes at this level.',
    'instrumented': 'The coil follows the vessel and lifts over the reed bridge. Its free tails stop at the assembly interface.',
    'earth-lead': 'The attached ring and crimp exit are shown. Free conductor dressing belongs to the installation.',
    'coil': 'The winding and tails retain the specified ACR tube wall. Its winding face boundaries retain the shape through native links.',
}
ids = {'vessel-tube':'tube', 'lower-cap-reference':'lower-cap', 'upper-cap-reference':'upper-cap',
       'float-reference':'float', 'weldment-reference':'weldment', 'vessel-reference':'vessel',
       'inlet-reference':'inlet', 'relief-reference':'relief', 'instrumented-reference':'module',
       'reed-bridge':'bridge', 'machined-cap':'cap', 'guide-rod':'rod', 'upper-stop':'stop',
       'float-shell':'shell', 'ring-magnet':'magnet'}
explodes = {'lower-cap': [0,0,-60], 'upper-cap': [0,0,60], 'float': [0,-85,0],
            'coil':[100,0,0], 'reed-bridge':[0,-65,0], 'probe':[-55,0,0], 'probe-coil':[0,55,0],
            'reed':[0,-65,0], 'earth-screw':[40,65,0], 'earth-washer':[25,45,0],
            'earth-lead':[20,30,0], 'inlet':[-35,35,40], 'relief':[0,45,40],
            'pushfit-elbow':[0,-45,-45], 'guide-rod':[0,0,55], 'upper-stop':[0,0,30],
            'machined-cap':[0,0,-35], 'ring-magnet':[0,0,35]}
models = {key: json.loads((native / f'{key}.json').read_text()) for key in labels}
digest = hashlib.sha256((root / 'contracts.json').read_bytes())
for key in labels:
    digest.update((native / f'{key}.json').read_bytes())
catalog = {'name': labels['instrumented'], 'sourceVersion':digest.hexdigest(), 'pitch':340, 'nodes':{}}
manifest_dir = web / 'levels'
manifest_dir.mkdir(exist_ok=True)
for key, model in models.items():
    name = f'{key}-reference' if key in refs else key
    if key == 'instrumented-parent': name = 'instrumented-reference'
    if key == 'probe-coil': name = 'probe'
    asset = web / 'assets' / f'{name}.glb'
    version = hashlib.sha256(asset.read_bytes()).hexdigest()[:16]
    node = {'label': labels[key], 'material':model.get('metadata',{}).get('part_number',''),
            'description': model.get('metadata',{}).get('description',''),
            'native':f'/labs/solidcraft/carbonator/native/{key}',
            'preview':f'/solidcraft-lab/carbonator/assets/{name}.glb?v={version}'}
    display = displays[name]
    node['display'] = {**display, 'url':f'/solidcraft-lab/carbonator/assets/native/{display["file"]}?v={display["sha256"][:16]}'}
    if key in parameters: node['parameters'] = parameters[key]
    if key in fits: node['fit'] = fits[key]
    if key in refs: node.update(reference=True, omit=omit.get(key,[]))
    if key == 'weldment': node['barrel'] = True
    links = model.get('links',{})
    if links:
        components = {item['id']: item for item in model['components']}
        entries, inputs, used = [], [], {}
        for occurrence in model['occurrences']:
            component = components[occurrence['component']]
            link = links[str(component['id'])]
            source = Path(link['path']).stem
            child = source.removesuffix('-reference')
            identifier = ids.get(source,child)
            if identifier in used:
                used[identifier] += 1
                identifier += f'-{used[identifier]}'
            else: used[identifier] = 1
            entries.append({'id':identifier,'node':child,'label':component['name'],
                            'transform':occurrence['transform'], 'explode':explodes.get(child,[0,0,35])})
            input_ = {'node':child,'component':component['name'],'source':source}
            if input_ not in inputs: inputs.append(input_)
        (manifest_dir / f'{key}.json').write_text(json.dumps({'occurrences':entries},indent=2)+'\n')
        node.update(children=f'/solidcraft-lab/carbonator/levels/{key}.json', inputs=inputs)
    catalog['nodes'][key] = node
(web / 'levels.json').write_text(json.dumps(catalog,indent=2)+'\n')
with zipfile.ZipFile(web / 'levels-project.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for key in labels:
        for suffix in ['json','sc']: archive.write(native / f'{key}.{suffix}',f'native/{key}.{suffix}')
        if key in refs:
            for suffix in ['json','sc']: archive.write(native / f'{key}-reference.{suffix}',f'native/{key}-reference.{suffix}')
    for file in ['README.md','contracts.json']:
        archive.write(root / file,file)
print('Published shallow assembly manifests and native project')
