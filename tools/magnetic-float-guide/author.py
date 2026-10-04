"""Author the current one-piece ASA Aero float guide from its design and evidence.

Run manually, then float_art.py and build.py. No printer submission is made.
"""

from __future__ import annotations

import hashlib
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / 'hardware/magnetic-float-guide'
FLOAT = ROOT / 'hardware/printed-parts/cold-core/magnetic-float/all-aero'
PUBLIC = 'https://raw.githubusercontent.com/derekbreden/homesodamachine/main/'


def figure(name, caption, size='tight'):
    return f'<figure class="{size}"><img src="art/{name}.png" alt="{escape(caption)}"><figcaption>{caption}</figcaption></figure>'


def actions(*items):
    return '<ol class="actions">' + ''.join(f'<li>{s}</li>' for s in items) + '</ol>'


def table(rows, compact=False):
    return ('<table' + (' class="compact"' if compact else '') + '>' +
            ''.join(f'<tr><td class="k">{k}</td><td>{v}</td></tr>' for k, v in rows) + '</table>')


def note(label, text):
    return f'<div class="mind"><span class="mind-label">{label}</span><p>{text}</p></div>'


def link(path, label):
    rel = path.relative_to(ROOT).as_posix()
    return f'<a href="{PUBLIC}{rel}">{label}</a>'


def leaf(number, slug, section, title, lede, body, extra_class=''):
    name = f'{number:02d}-{slug}.html'
    content = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{escape(title)}</title><link rel="stylesheet" href="style.css"></head>
<body><article class="card {extra_class}">
<header><span class="eyebrow"><b>{section}</b> &middot; build guide</span><h1>{title}</h1><i class="rule"></i><p class="lede">{lede}</p></header>
<main>{body}</main><footer><span>ASA Aero magnetic float &middot; Home Soda Machine</span><span class="folio">{number}</span></footer>
</article></body></html>'''
    (GUIDE / name).write_text(content)
    return name


def main():
    GUIDE.mkdir(exist_ok=True)
    design = json.loads((FLOAT / 'design.json').read_text())
    dims = design['dimensions_mm']
    magnet = design['magnet']
    preflight = json.loads((FLOAT / 'mark2-print/v1/float-preflight.json').read_text())
    observations = json.loads((FLOAT / 'physical-observations.json').read_text())
    integration = json.loads((FLOAT / 'integration-check.json').read_text())
    installation = json.loads((FLOAT / 'installation.figures.json').read_text())[
        '/hardware/printed-parts/cold-core/magnetic-float/all-aero/integration.py']
    recipe = preflight['recipe']
    mapping = preflight['material_mapping']
    next_trial = observations['next_trial']
    assert design['cad_revision'] == next_trial['cad_revision'] == integration['float_cad_revision']
    assert design['print_intent']['pause_before_layer_z_mm'] == next_trial['expected_first_covering_layer_z_mm']
    assert not next_trial['ready_archive_prepared'] and not next_trial['submitted'], 'Update the guide from the reviewed current slice before describing a prepared job'
    diameter, height, bore = (f'{dims[k]:g}' for k in ('diameter', 'height', 'guide_bore'))
    rod = f'{dims["bench_guide"]:g}'
    first_cover = f'{design["print_intent"]["pause_before_layer_z_mm"]:g}'
    layer = f'{recipe["layer_height_mm"]:g}'
    pause_layer = next_trial['expected_pause_before_layer']
    last_open = f'{design["print_intent"]["pause_before_layer_z_mm"] - recipe["layer_height_mm"]:g}'
    minutes = round(preflight['native_slice_summary']['estimated_time_s'] / 60)
    task_id = observations['paused_print_result']['task_id']
    page_count = 13
    guide_pages = []

    cover = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>ASA Aero magnetic float build guide</title><link rel="stylesheet" href="style.css"></head>
<body><article class="card cover"><header>
<span class="brand"><img src="../../ios/AppIcon.svg" alt="">Home Soda Machine</span>
<h1>Magnetic<br>float</h1><p class="sub">One ASA Aero body. One ring magnet.<br>Pause, seat the ring, and print the pocket closed.</p>
</header><main><figure><div class="plate"><img src="art/hero.png" alt="One-piece ASA Aero float beside a section showing its midplane RC62 ring"></div></figure></main>
<footer><span>ASA Aero White &middot; RC62 &middot; {diameter} &times; {height} mm</span><span>Illustrated build guide &middot; {page_count} pages</span></footer></article></body></html>'''
    (GUIDE / '01-cover.html').write_text(cover)
    guide_pages.append('01-cover.html')

    guide_pages.append(leaf(2, 'one-body-one-ring', 'The assembly', 'One body. One ring.',
        'The printer makes one connected foamed body. A pause lets the ring enter its annular pocket before the covering roads close it.',
        figure('exploded', 'The ASA Aero body and purchased RC62 ring are the complete assembly. The exploded view exposes the internal pocket; the covering body prints in the same job.', 'mid') +
        table([
            ('Float body', f'{diameter} &times; {height} mm &middot; ASA Aero throughout'),
            ('Open guide bore', f'{bore} mm on a {rod} mm rod'),
            ('Ring magnet', f'RC62 &middot; {magnet["od_mm"]:g} &times; {magnet["id_mm"]:g} &times; {magnet["thickness_mm"]:g} mm'),
            ('Magnet center', f'{dims["magnet_midplane"]:g} mm above the bottom'),
            ('Current pocket', f'{dims["pocket_depth"]:.2f} mm deep &middot; CAD {design["cad_revision"]}')]) +
        note('Three articles', 'The carbonator and both flavor reservoirs each use one of these floats. The central bore stays open; the ring pocket is enclosed.')))

    drying_art = '''<svg class="setup" viewBox="0 0 2100 460" role="img" aria-label="ASA Aero dries in SUNLU E2 then feeds from a sealed external drybox">
<rect x="20" y="20" width="900" height="400" rx="28" fill="var(--field-pale)"/><rect x="1180" y="20" width="900" height="400" rx="28" fill="var(--field-pale)"/>
<circle cx="190" cy="215" r="120" fill="#ede9df" stroke="var(--ink)" stroke-width="8"/><circle cx="190" cy="215" r="40" fill="white" stroke="var(--ink)" stroke-width="8"/>
<text x="365" y="145" class="label">SUNLU E2</text><text x="365" y="225" class="small">80 &deg;C &middot; 8 hours</text><text x="365" y="305" class="small">Forced-air drying</text>
<path d="M960 220H1130M1080 170L1130 220L1080 270" fill="none" stroke="var(--gauge)" stroke-width="12"/>
<text x="1240" y="145" class="label">POLYMAKER DRYBOX</text><text x="1240" y="225" class="small">Sealed &middot; below 20% RH</text><text x="1240" y="305" class="small">External right feed</text></svg>'''
    guide_pages.append(leaf(3, 'dry-the-filament', 'Prepare', 'Dry one Aero spool',
        'Use the selected ASA Aero White stock. Complete drying before loading the external feed.',
        drying_art + '<div class="numcards"><div class="numcard"><h2>Drying temperature</h2><div class="value">80 &deg;C</div><p>SUNLU E2 &middot; forced air</p></div><div class="numcard"><h2>Drying time</h2><div class="value">8 hours</div><p>Before transfer to the drybox</p></div></div>' +
        actions('Dry <b>Bambu ASA Aero White (GFB02 / 46100)</b> in the SUNLU E2 for the complete cycle.',
                'Transfer it to the sealed <b>Polymaker drybox</b>. Maintain <b>less than 20% RH</b> during storage and feeding.',
                'Connect that drybox to the printer\'s external right feed. Keep the filament dry through the print.') +
        note('Filament preparation', 'These are the ASA Aero manufacturer\'s forced-air drying conditions. They apply to filament before printing; the finished float and its magnet receive no drying bake.')))

    guide_pages.append(leaf(4, 'set-up-mark2', 'Prepare', 'Set up Mark2',
        'The selected H2C recipe uses its fixed right nozzle and a glued Engineering plate.',
        figure('plate-aero', 'One upright body on a cropped Engineering plate. The central bore is vertical and the bottom lies directly on the bed.', 'short') +
        table([
            ('Right nozzle', mapping['nozzle']),
            ('Filament feed', f'Polymaker drybox &middot; external right slot {mapping["external_slot"]}'),
            ('Send tile', '<b>Ext ASA-AERO R</b>'),
            ('Plate / trim', f'Engineering, Bambu liquid glue &middot; +{preflight["requested_z_trim_mm"]:.2f} mm user trim')], True) +
        actions('With the printer cool, confirm the <b>right hardened standard-flow 0.4 mm nozzle</b> and matching printer setup.',
                'Wash the Engineering plate with dish detergent and warm water. Rinse, dry, and apply a thin even coat of the owned Bambu liquid glue.',
                'Set one RC62 and a soft brush beside the printer. Keep the enclosure closed during printing and run the shop ventilation.') +
        note('Recipe scope', 'The recorded recipe is a trial process. It does not establish foam density, completed buoyancy or pressure life.')))

    guide_pages.append(leaf(5, 'prepare-the-current-slice', 'Current print preparation', 'Slice the current body',
        'Use the current v2 body and review its native slice before any submission.',
        table([
            ('Current geometry', link(FLOAT / 'float-aero.stl', 'float-aero.stl') + '<br>' + link(FLOAT / 'all_aero_float.py', 'all_aero_float.py')),
            ('Nozzle / bed / chamber', f'{recipe["nozzle_c"]} / {recipe["bed_c"]} / {recipe["chamber_c"]} &deg;C'),
            ('Flow / layer / line', f'{recipe["flow_ratio"]:g} / {layer} mm / {recipe["line_width_mm"]:g} mm'),
            ('Walls', f'{recipe["wall_loops"]} loops &middot; nested foaming perimeters'),
            ('Other paths', '0 sparse infill, top/bottom skin, skirt, brim and support')]) +
        actions('Open the current STL with the retained right-nozzle ASA Aero process. Keep the body upright on the plate.',
                'Use ' + link(FLOAT / 'prepare_print.py', 'prepare_print.py') + ' to prepare a separate v2 project and review record. It does not submit a print.',
                'Review the actual native geometry, recipe, pause and covering roads. Bind the reviewed project/archive to the current source hashes before submission.') +
        note('Current preparation state', 'The current CAD has a <b>3.60 mm pocket</b>. Its v2 native archive has not been prepared or submitted. The saved <b>all-aero-float.3mf</b> belongs to the identified v1 article and is listed as evidence on page 13.') +
        '<p class="dim">Nested perimeters include seams, wipes and short transitions. This process is not a zero-travel spiral.</p>'))

    guide_pages.append(leaf(6, 'review-the-insertion-pause', 'Native review', 'Keep the pocket open',
        'The pause must occur before the first extrusion that covers the ring pocket.',
        figure('paused-body', 'Current v2 geometry at the expected last open plane. The annular pocket receives the RC62 while the body stays attached to the plate.', 'mid') +
        table([
            ('Pocket floor / roof', f'Z{dims["magnet_seat"]:g} / Z{dims["pocket_roof"]:g} mm'),
            ('Expected last open layer', f'Z{last_open} mm'),
            ('Expected first covering layer', f'Layer {pause_layer} &middot; Z{first_cover} mm')], True) +
        actions('Inspect the <b>seat, last open pocket, pause command and first covering roads</b> in the new native slice.',
                'Confirm one insertion pause occurs before any covering extrusion. The guide bore must remain open.',
                'Confirm the seated ring lies below both pocket rims and the covering roads land on the inner collar and outer band.') +
        note('Expected, not a reviewed archive', f'The layer-{pause_layer} / Z{first_cover} position follows the current CAD and {layer} mm layer grid. A fresh native slice must verify the emitted moves; a CAD section alone does not authorize a print.')))

    guide_pages.append(leaf(7, 'seat-the-magnet', 'At the pause', 'Seat one RC62',
        'The printed body stays on the Engineering plate. Put only the ring magnet into the open pocket.',
        figure('magnet-seat', 'Lower the RC62 along the guide axis into the open annular pocket. Coral identifies the ring being added; the arrow shows its motion.', 'mid') +
        actions('Wait for the programmed pause and toolhead parking before reaching into the printer.',
                'Leave the sheet mounted and the float attached. Separate <b>one RC62</b> from the stack and lower it squarely into the pocket.',
                'Seat it fully on the pocket floor with its hole coaxial with the guide bore. Its flat faces lie horizontal, <b>below both pocket rims</b>.',
                'Clear loose strings without shifting the body. Keep the central guide bore open.') +
        note('Resume condition', 'The ring sits flat and fully down. Nothing projects into the covering path, and no hand or tool remains inside the printing area.')))

    guide_pages.append(leaf(8, 'resume-and-close', 'Complete the print', 'Resume over the ring',
        'The same ASA Aero job builds the material above the pocket and closes the ring inside the body.',
        figure('roof', 'Section through the current body. Coral shows the material printed above the pocket; the ring is centered at the body\'s axial midplane.', 'mid') +
        actions('Remove hands, tools and loose strings from the printer. Close the enclosure.',
                'Manually resume the same job. Let the printer restore its temperatures and continue the covering roads.',
                'Observe the initial covering layers for ring movement, dragging or lifting. Record the result with that article.') +
        note('What the existing print demonstrates', 'The identified v1 article supports paused insertion and the initial covering deposition. It does not establish the finished roof or retained signal for a cooled float.') +
        '<p class="dim">RC62 has an 80 &deg;C continuous operating limit. The 270 &deg;C nozzle setting does not tell us the magnet\'s actual temperature; retained field after insertion is unmeasured.</p>'))

    guide_pages.append(leaf(9, 'release-and-inspect', 'Finish', 'Release and inspect',
        'Let the print cool before removing it. Keep the foamed body and its open bore intact.',
        figure('finished', f'The complete {diameter} &times; {height} mm Aero body. The ring lies at Z{dims["magnet_midplane"]:g}; the through-bore remains open.', 'mid') +
        actions('Leave the enclosure closed for initial cooling. Use the shop handling threshold of <b>35 &deg;C or lower bed temperature</b> before releasing the part.',
                'Lift the Engineering sheet and flex it gently. Support the float rather than prying through its bore or pocket roof.',
                'Clip loose strings and brush away crumbs. Preserve the bore, pocket closure and cylindrical outside surface.',
                'Inspect the covering area and slide the finished float on its actual rod. Record the finished article\'s condition.') +
        note('Physical scope', 'Finished roof integrity, cooled removal, retained magnetic signal and sliding have no acceptance record. The cooling threshold is a conservative shop handling choice, not an ASA-specific manufacturer release limit.')))

    axis = f'{integration["rod_axis_from_inside_wall_mm"]:g}'
    wall_range = integration['carbonator_upright_wall_clearance_range_mm']
    reach = integration['maximum_float_edge_to_reed_center_mm']
    guide_pages.append(leaf(10, 'install-on-the-guide', 'Installation', 'Locate the guide rod',
        f'Each {rod} mm rod stands {axis} mm inward from the vessel\'s wet inside wall. Use the vessel datum, not the end-cap edge.',
        figure('guide-fit', f'An explanatory {rod} mm rod through the actual {bore} mm float bore. This picture shows the guide interface, not measured liquid performance.', 'short') +
        table([
            ('Rod / radial running play', f'{rod} / {dims["guide_radial_clearance"]:g} mm'),
            ('Body-to-wall clearance', f'2 mm nominal &middot; {wall_range[0]:g}-{wall_range[1]:g} mm upright range'),
            ('Carbonator rod blank', installation['CARB_ROD_LENGTH'] + ' &middot; hand-fit actual conical registers'),
            ('Reservoir rod cut', installation['RES_ROD_LENGTH'] + ' &middot; ' + installation['RES_ROD_CLEARANCE'] + ' axial clearance'),
            ('Greatest float-edge to reed distance', f'{reach["carbonator"]:.3f} mm carbonator / {reach["reservoir"]:.3f} mm reservoir')], True) +
        '<p>Use the ' + link(FLOAT / 'installation.md', 'installation record') + ' for the carbonator blind-drill coordinates and the matching reservoir body/cap bosses. Confirm free motion over the actual travel.</p>' +
        note('Carbonator capture', 'The 36 mm float is captured on the rod before final vessel closure. It cannot pass through the NPT ports. Welding exposure and post-closure function have no acceptance record.')))

    guide_pages.append(leaf(11, 'calibrate-the-reeds', 'Liquid levels', 'Calibrate the crossings',
        'The magnet midplane is not the liquid surface. Final reed heights come from the finished float in the actual liquid and wall fixture.',
        '<div class="numcards"><div class="numcard"><h2>Guide drilling datum</h2><div class="value">20 mm</div><p>Rod axis from the wet inside wall</p></div><div class="numcard"><h2>Reed design maximum</h2><div class="value">18 mm</div><p>Nearest float edge to reed center, including guide play</p></div></div>' +
        actions('Use the actual rod, finished float, MDSR-7-10-15 reeds, vessel wall, ruler or calipers, multimeter and existing measuring cup.',
                'In water and actual flavoring, record <b>a = magnet center minus liquid surface height</b>. Magnet center is float bottom plus 14 mm.',
                'Sweep slowly upward and downward past each reed. Record every closure and release as <b>d = magnet center minus reed center</b>, including separate activation lobes.',
                'Place each reed at <b>target liquid height + a - d</b>, using the closure in its operating direction. Repeat three cycles at nominal position and greatest permitted retreat.') +
        note('Placement acceptance', 'Intended crossings must occur in order before the travel stops, with no missed closure or unintended trigger. Repeated liquid crossing heights must span at most 2 mm. Use measured liquid volumes for reservoir quarter marks.') +
        '<p>Reeds pulse as the float passes. Reservoir control retains the last crossing and flow direction. Carbonator high inhibits refill even if low remains closed; a refill timeout still needs an explicit clear.</p>' +
        '<p class="dim">The ' + link(FLOAT / 'installation.md', 'calibration procedure') + ' defines the target levels and recording method. Those levels remain provisional until the liquid crossings are measured.</p>'))

    # Relative from hardware/magnetic-float-guide; this evidence image stays with its article.
    photo = '../printed-parts/cold-core/magnetic-float/all-aero/mark2-print/v1/evidence/magnet-insertion-overprint-2026-10-03.jpg'
    guide_pages.append(leaf(12, 'identified-print-evidence', 'Physical evidence', 'What is recorded',
        f'Mark2 task {task_id} identifies the paused v1 article. Its pocket and emitted pause belong to that frozen source.',
        f'<figure class="short"><img src="{photo}" alt="Operator photo of RC62 insertion and initial Aero covering beneath the toolhead"><figcaption>The operator photo partly obscures the covering roads. The report supports insertion and initial overprinting in this identified v1 trial.</figcaption></figure>' +
        table([
            ('v1 pocket', '3.40 mm &middot; frozen native source'),
            ('v1 insertion / first cover', 'After layer 79 at Z15.8 / layer 80 at Z16.0 mm'),
            ('v1 slice estimate', f'{minutes} minutes &middot; manual pause excluded'),
            ('Operator result', 'Ring insertion worked; first covering layer was tight, second deposited well'),
            ('Printed-float reed bench report', '20 mm usable; 21-24 mm intermittent; 25 mm absent<br>Datum: nearest float edge to reed center')], True) +
        note('Limits of these results', 'Final cooled roof, density, buoyancy, retained signal, liquid uptake, pressure life and flavor compatibility are unreported. The reed bench report does not identify its reed, wall fixture or repeat count.') +
        '<p>The current sizing model assumes 0.65 g/cm&sup3; Aero: about 22.75 g assembled mass and 5.23 g spare lift. These are calculations, not measurements.</p>'))

    refs = [
        ('Current body', FLOAT / 'all_aero_float.py', 'CAD source for the one-piece ASA Aero float.'),
        ('Current STL', FLOAT / 'float-aero.stl', 'Current v2 geometry; prepare and review a fresh native slice.'),
        ('Design and installation', FLOAT / 'README.md', 'Dimensions, selected process and qualification limits.'),
        ('Rod and reed datums', FLOAT / 'installation.md', 'Drilling, guide motion and directional liquid calibration.'),
        ('Print preparation', FLOAT / 'prepare_print.py', 'Writes a separate v2 project/review; submits no print.'),
        ('Identified v1 project', FLOAT / 'all-aero-float.3mf', 'Frozen v1 project, 3.40 mm pocket; evidence for task ' + str(task_id) + '.'),
        ('Identified v1 review', FLOAT / 'mark2-print/v1/float-preflight.json', 'Native paths, pause and source hashes for that article.'),
        ('Physical observations', FLOAT / 'physical-observations.json', 'Insertion, initial overprint and reported reed reach, with their scope.'),
    ]
    guide_pages.append(leaf(13, 'files-and-sources', 'Reference', 'Files and recipe sources',
        'Current geometry, print preparation and physical evidence are identified separately.',
        '<h2>Repository files</h2>' + table([(link(path, title), description) for title, path, description in refs], True) +
        '<h2>Manufacturer guidance</h2>' + table([
            ('<a href="https://store.bblcdn.com/2bb7c6814cdc42d19ffc62570cfc1fb2.pdf">Bambu ASA Aero TDS</a>', 'Filament drying, storage humidity and material descriptors.'),
            ('<a href="https://wiki.bambulab.com/en/filament-acc/filament/asa-aero-printing-guide">Bambu ASA Aero guide</a>', 'Foaming, plate selection and printing guidance.'),
            (f'<a href="{magnet["source"]}">K&amp;J RC62</a>', 'Ring dimensions, N42 grade and continuous operating limit.'),
            ('<a href="https://www.littelfuse.com/assetdocs/reed-switch-and-reed-sensor-activation-application-note?assetguid=fa9045a4-e577-4f55-9e9b-4232faacffd9">Littelfuse reed activation</a>', 'Closure, hold, release and orientation effects.')], True) +
        '<p class="dim">Prepared 3 October 2026. Illustrations derive from current v2 CAD. Warm white represents Aero and nickel the ring; coral marks the added ring or covering material. Cutaways, plate crops, rods and arrows explain geometry and motion.</p>', 'sources'))

    assert len(guide_pages) == page_count
    expected = set(guide_pages)
    for stale in GUIDE.glob('[0-9][0-9]-*.html'):
        if stale.name not in expected:
            stale.unlink()
    inputs = [FLOAT / name for name in [
        'design.json', 'all_aero_float.py', 'float-aero.stl', 'prepare_print.py',
        'README.md', 'installation.md', 'installation.figures.json',
        'physical-observations.json', 'integration-check.json',
        'all-aero-float.3mf', 'mark2-print/v1/float-preflight.json',
        'mark2-print/v1/float-mark2-launch.json',
        'mark2-print/v1/evidence/magnet-insertion-overprint-2026-10-03.jpg']]
    inputs.extend([Path(__file__), ROOT / 'hardware/printed-parts/cold-core/_float_interface.py',
                   ROOT / 'tools/magnetic-float-guide/build-recipe-sources.json'])
    manifest = {
        'title': 'ASA Aero magnetic float build guide',
        'current_cad_revision': design['cad_revision'],
        'current_native_slice_state': 'review_pending',
        'pages': guide_pages,
        'recipe_sources': '../../tools/magnetic-float-guide/build-recipe-sources.json',
        'inputs_sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs},
    }
    (GUIDE / 'guide-inputs.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Authored {len(guide_pages)} current ASA Aero pages; v2 native slice review pending.')


if __name__ == '__main__':
    main()
