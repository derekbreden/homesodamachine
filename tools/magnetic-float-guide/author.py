"""Author the float booklet's HTML leaves from current geometry and print projects.

Run manually, then float_art.py and build.py. No publish/build-graph dependency.
"""

from __future__ import annotations

import hashlib
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / 'hardware/magnetic-float-guide'
FLOAT = ROOT / 'hardware/printed-parts/cold-core/magnetic-float'
PROJECT_BASE = 'https://raw.githubusercontent.com/derekbreden/homesodamachine/main/hardware/printed-parts/cold-core/magnetic-float/'


def figure(name, caption, size='tight'):
    return f'<figure class="{size}"><img src="art/{name}.png" alt="{escape(caption)}"><figcaption>{caption}</figcaption></figure>'


def actions(*items):
    return '<ol class="actions">' + ''.join(f'<li>{s}</li>' for s in items) + '</ol>'


def table(rows, compact=False):
    return ('<table' + (' class="compact"' if compact else '') + '>' +
            ''.join(f'<tr><td class="k">{k}</td><td>{v}</td></tr>' for k, v in rows) + '</table>')


def note(label, text):
    return f'<div class="mind"><span class="mind-label">{label}</span><p>{text}</p></div>'


def project(filename):
    return f'<a class="file" href="{PROJECT_BASE}{filename}">{filename}</a>'


def duration(seconds):
    mins = round(seconds / 60)
    return f'{mins // 60} h {mins % 60:02d} min' if mins >= 60 else f'{mins} min'


def leaf(number, slug, section, title, lede, body, extra_class=''):
    name = f'{number:02d}-{slug}.html'
    content = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{escape(title)}</title><link rel="stylesheet" href="style.css"></head>
<body><article class="card {extra_class}">
<header><span class="eyebrow"><b>{section}</b> &middot; build guide</span><h1>{title}</h1><i class="rule"></i><p class="lede">{lede}</p></header>
<main>{body}</main><footer><span>Magnetic float &middot; Home Soda Machine</span><span class="folio">{number}</span></footer>
</article></body></html>'''
    (GUIDE / name).write_text(content)
    return name


def main():
    GUIDE.mkdir(exist_ok=True)
    design = json.loads((FLOAT / 'design.json').read_text())
    dims = design['dimensions_mm']
    profile = json.loads((FLOAT / 'print-profile.json').read_text())
    verification = json.loads((FLOAT / 'verification.json').read_text())
    aero, petg = profile['jobs']['aero'], profile['jobs']['petg']
    core_time, insert_time = [duration(p['estimated_seconds']) for p in aero['plates']]
    shell_time = duration(petg['plates'][0]['estimated_seconds'])
    active_time = duration(sum(p['estimated_seconds'] for j in (aero, petg) for p in j['plates']))
    roof_minutes = verification['jobs']['petg']['plates'][0]['insertion_pauses'][0]['slicer_remaining_minutes_at_pause']
    height = f"{dims['height']:g}"
    guide_pages = []

    cover = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Magnetic float build guide</title><link rel="stylesheet" href="style.css"></head>
<body><article class="card cover"><header>
<span class="brand"><img src="../../ios/AppIcon.svg" alt="">Home Soda Machine</span>
<h1>Magnetic<br>float</h1><p class="sub">Dry the filament. Print the foam. Seat the magnet.<br>Build the PETG shell around all three pieces.</p>
</header><main><figure><div class="plate"><img src="art/hero.png" alt="Finished clear PETG float beside a cutaway of its foam core and ring magnet"></div></figure></main>
<footer><span>PETG Translucent Clear &middot; ASA Aero &middot; RC62</span><span>Illustrated build guide &middot; 16 pages</span></footer></article></body></html>'''
    (GUIDE / '01-cover.html').write_text(cover)
    guide_pages.append('01-cover.html')

    guide_pages.append(leaf(2, 'the-whole-build', 'The assembly', 'Three prints. One magnet.',
        f'A {dims["diameter"]:g} mm &times; {height} mm float with a continuous PETG envelope. The printer closes the roof after the foam and magnet go in.',
        figure('exploded', 'Parts from bottom to top: open PETG shell, tall foam core, RC62 ring and short foam insert. Seat the ring in the core on the bench before insertion. The roof prints in place.', 'mid') +
        table([
            ('Tall white core', 'ASA Aero, plate 1. Pocket faces upward.'),
            ('Short white insert', 'ASA Aero, plate 2. Chamfered edges face downward.'),
            ('One RC62 ring', 'K&amp;J, nickel plated; 19.05 &times; 9.525 &times; 3.175 mm.'),
            ('Clear shell', 'Bambu PETG Translucent Clear 32101, one plate with a programmed insertion pause.')]) +
        '<div class="legend"><span><i style="background:#aac4d1"></i>Clear PETG, shaded blue</span><span><i style="background:#ede9df"></i>Aero foam</span><span><i style="background:#d64050"></i>Part being added</span></div>' +
        note('Build order', f'Dry overnight. Print and prepare both Aero pieces. Seat the magnet on the bench. Print PETG, insert the prepared pieces at the pause, and resume. Allow about <b>{active_time} of printing</b>, plus heating, cooling and insertion.')))

    drying_art = '''<svg class="setup" viewBox="0 0 2100 470" role="img" aria-label="Two spools dry at the same time in separate AMS units">
<rect x="20" y="20" width="960" height="410" rx="28" fill="#f1ede7"/><rect x="1120" y="20" width="960" height="410" rx="28" fill="#f1ede7"/>
<circle cx="205" cy="220" r="138" fill="#ded7cd" stroke="#1a1a2e" stroke-width="10"/><circle cx="205" cy="220" r="48" fill="#fff" stroke="#1a1a2e" stroke-width="10"/>
<circle cx="1305" cy="220" r="138" fill="#aac4d1" stroke="#1a1a2e" stroke-width="10"/><circle cx="1305" cy="220" r="48" fill="#fff" stroke="#1a1a2e" stroke-width="10"/>
<text x="410" y="145" class="label">WHITE ASA AERO</text><text x="410" y="225" class="small">AMS HT</text><text x="410" y="305" class="small">Right nozzle feed</text>
<text x="1510" y="145" class="label">CLEAR PETG</text><text x="1510" y="225" class="small">AMS 2 Pro</text><text x="1510" y="305" class="small">Left nozzle feed</text></svg>'''
    guide_pages.append(leaf(3, 'dry-the-filament', 'Prepare', 'Start both dryers tonight',
        'Use the two different AMS units already in the shop. The cycles run at the same time; the longer PETG cycle sets the overnight schedule.',
        drying_art + '<div class="numcards"><div class="numcard"><h2>ASA Aero</h2><div class="value">80 &deg;C</div><div class="time">8 hours</div><p>AMS HT &middot; White 46100</p></div><div class="numcard"><h2>PETG Translucent</h2><div class="value">65 &deg;C</div><div class="time">12 hours</div><p>AMS 2 Pro &middot; Clear 32101</p></div></div>' +
        actions('Load the ASA Aero into an <b>AMS HT</b> and the PETG Translucent into an <b>AMS 2 Pro</b>. Connect the AMS HT\'s own power cable. Remove PLA and other lower-temperature spools from that AMS 2 Pro.',
                'Latch both lids. Set <b>static drying</b> to the temperatures and durations above, then start both cycles.',
                'Complete both cycles before printing. Leave each spool in the same closed AMS for storage and printing.') +
        note('Keep the material names exact', '<b>ASA Aero</b> is the white foaming material. <b>Bambu PETG Translucent Clear (32101)</b> is the shell material, the same clear filament used for the flavor reservoirs. Select those names in the supplied projects.')))

    setup_art = '''<svg class="setup" viewBox="0 0 2100 820" role="img" aria-label="H2C seen from the front, PETG left 0.6 mm and Aero right 0.4 mm">
<rect x="60" y="40" width="1980" height="710" rx="28" fill="#f1ede7" stroke="#b9b1a4" stroke-width="6"/>
<rect x="155" y="330" width="1790" height="55" rx="10" fill="#1a1a2e"/>
<rect x="475" y="290" width="250" height="205" rx="12" fill="#303138"/><path d="M535 495H665L622 565H578Z" fill="#b08a2c"/>
<rect x="1375" y="290" width="250" height="205" rx="12" fill="#303138"/><path d="M1435 495H1565L1522 565H1478Z" fill="#b08a2c"/>
<text x="600" y="140" text-anchor="middle" class="label">LEFT &middot; PETG TRANSLUCENT</text><text x="600" y="220" text-anchor="middle" class="small">AMS 2 Pro &rarr; 0.6 mm</text>
<text x="1500" y="140" text-anchor="middle" class="label">RIGHT &middot; ASA AERO</text><text x="1500" y="220" text-anchor="middle" class="small">AMS HT &rarr; 0.4 mm</text>
<text x="1050" y="680" text-anchor="middle" class="small">H2C FRONT VIEW &middot; STANDARD-FLOW HOTENDS</text></svg>'''
    guide_pages.append(leaf(4, 'set-up-the-h2c', 'Prepare', 'Set up one H2C',
        'The whole build uses the same nozzle pair. Foam prints on the right; the shell prints on the left.',
        setup_art + actions('With the printer cool, fit the <b>left 0.6 mm standard-flow</b> hotend and the <b>right 0.4 mm standard-flow</b> induction hotend.',
                'In the printer setup, select those nozzle sizes. Route the ASA Aero AMS HT to the right feed and the PETG AMS 2 Pro to the left feed.',
                'Set out the Engineering plate, Textured PEI plate, Bambu liquid glue, one RC62, flush cutters, a craft knife, a soft brush and a clean flat plastic scraper.',
                'Open the supplied <b>3MF as a project</b> in Bambu Studio. Keep its printer, material and process settings when prompted; map its material to the matching AMS spool.') +
        note('The two projects', project('magnetic-float-aero.3mf') + '<br>Two foam plates, printed separately.<br><br>' + project('magnetic-float.3mf') + '<br>One PETG plate, with its insertion pause already included.')))

    guide_pages.append(leaf(5, 'print-the-core', 'Foam &middot; plate 1', 'Print the tall core',
        'The flat end sits on the Engineering plate. The circular magnet pocket faces upward.',
        figure('plate-core', 'Tall core, upright. Print this plate by itself; its geometry and small brim are already placed in the project.', 'mid') +
        '<div class="split"><div>' + table([('Project', 'magnetic-float-aero.3mf'), ('Plate', '1 &middot; tall core'), ('Nozzle / bed', '270 / 90 &deg;C'), ('Chamber', '60 &deg;C'), ('Flow / layer', '0.52 / 0.20 mm')], True) + f'<p class="timing">Printing: about {core_time}</p></div><div>' +
        actions('Wash the Engineering plate with dish detergent and warm water. Rinse and dry it.',
                'Apply a thin, even coat of <b>Bambu liquid glue</b> over the print area and let it dry.',
                'Select <b>plate 1</b> and the right ASA Aero feed. Close the door and lid, run room ventilation, and print.') + '</div>'))

    guide_pages.append(leaf(6, 'print-the-insert', 'Foam &middot; plate 2', 'Print the short insert',
        'This second foam piece becomes the support directly beneath the PETG roof.',
        figure('plate-insert', 'Short insert, upright. Its two lower chamfers start the fit into the shell; its full, flat upper face supports the roof.', 'mid') +
        actions('After the core finishes, leave the enclosure closed for the initial cooldown. Remove the plate once the bed reaches <b>35 &deg;C or below</b>.',
                'Gently flex the sheet to release the core. Set it upright on a clean surface.',
                'Renew the thin glue coat in the print area and reinstall the Engineering plate.',
                'In the same Aero project, select <b>plate 2</b>. Print with the same right nozzle and Aero settings.',
                'Cool to <b>35 &deg;C or below</b> and release the insert the same way.') +
        f'<p class="timing">Printing: about {insert_time}</p>'))

    guide_pages.append(leaf(7, 'prepare-the-foam', 'Prepare the inserts', 'Clean the entry edges',
        'Both pieces have a chamfer on the lower outside edge and the lower bore edge. These ends enter the shell first.',
        figure('lead-in-detail', 'Underside shown upward for clarity; insert the chamfered ends downward. The two 0.5 mm chamfers guide the foam around the bore sleeve and inside the outer wall.', 'tight') +
        actions('Clip the thin brim from each cooled foam piece. Work around the edge with flush cutters.',
                'Pare away the remaining brim lip with a sharp craft knife, following the printed edge. Leave the cylindrical fitting surfaces and the chamfers intact.',
                'Clip loose strings from the central bores and the core\'s magnet pocket. Brush away all loose crumbs.',
                'Keep the pieces dry and covered on the bench until the shell is ready.') +
        note('Orientation', '<b>Tall core:</b> magnet pocket up, chamfered end down.<br><b>Short insert:</b> chamfered end down, broad flat face up.')))

    guide_pages.append(leaf(8, 'seat-the-magnet', 'Bench assembly', 'Put the magnet in now',
        'Prepare the core before starting PETG. At the printer, the core and magnet will go in together.',
        figure('magnet-seat', 'Lower one RC62 into the circular pocket on top of the core. The pocket has clearance for the plated ring.', 'tight') +
        actions('Stand the core on its flat bottom, pocket upward.',
                'Separate <b>one RC62</b> from its stack. Hold it by the edges and lower it squarely into the pocket.',
                'Seat the ring flat against the pocket floor with light fingertip pressure. Either flat face can point upward for the reed-switch application.',
                'Keep the prepared core upright beside the printer. Set the short insert beside it, chamfers downward.') +
        note('Captured by the insert', 'Use the ring as supplied. The printed pocket and upper insert hold it inside the finished float; assembly requires no adhesive.')))

    guide_pages.append(leaf(9, 'prepare-for-petg', 'Shell setup', 'Change to PETG',
        'Let the warm Aero chamber cool, then fit the clean Textured PEI plate.',
        '<div class="numcards"><div class="numcard"><h2>Before starting</h2><div class="value">&le;35 &deg;C</div><p>Chamber temperature after the Aero jobs.</p></div><div class="numcard"><h2>During PETG</h2><div class="value">70 &deg;C</div><p>Textured PEI bed. Chamber heater off.</p></div></div>' +
        actions('Let the chamber cool to <b>35 &deg;C or below</b>. Wash the Textured PEI sheet with dish detergent and warm water, rinse and dry.',
                'Install the Textured PEI sheet, holding it by the edges. Use its clean texture directly for this PETG job.',
                'Open ' + project('magnetic-float.3mf') + ' as a project. Keep the project\'s supplied <b>PETG Translucent settings</b> and map its material to the dried PETG Translucent in the left AMS feed.',
                'Leave the prepared core, short insert and plastic scraper beside the printer. Read the insertion pages before starting.') +
        table([('Left nozzle', '0.6 mm standard flow'), ('Nozzle, first / remaining', '255 / 260 &deg;C'), ('Flow / layer', '1.02 / 0.18 mm'), ('First layer', '0.30 mm'), ('Ordinary part fan', '10-20%; auxiliary fan off')], True)))

    guide_pages.append(leaf(10, 'print-the-shell', 'Shell &middot; plate 1', 'Print to the built-in pause',
        'Start the single PETG plate. The shell stays fixed to the bed throughout insertion and roof printing.',
        figure('paused-shell', 'Cutaway view. At the pause, the outer wall and central bore sleeve both end at 57 mm. The open annular space receives the foam.', 'tight') +
        actions('Print <b>plate 1</b> using the left PETG feed. The job builds the 3 mm floor and both upright walls.',
                'When the programmed pause occurs, let the toolhead finish parking. Open the door to reach the shell.',
                'Leave the bed at <b>70 &deg;C</b> and the sheet mounted. Keep the shell and the printer axes in place.') +
        note('The next printed layer', 'The pause is after <b>Z57.00 mm</b>, before the first roof layer at <b>Z57.18 mm</b>. Insert the prepared core and upper insert, then resume the same job.') +
        f'<p class="timing">Whole PETG job: about {shell_time}, plus your insertion time</p>'))

    guide_pages.append(leaf(11, 'lower-the-core', 'At the pause &middot; 1', 'Lower the prepared core',
        'Hold it upright with the magnet at the top. The centre hole slides over the PETG bore sleeve.',
        figure('core-in', 'Cutaway view. Core and seated magnet enter as one prepared assembly. The lower chamfers guide both circular fits.', 'tall') +
        actions('Centre the core over the sleeve. Lower it vertically, chamfered end first.',
                'Press evenly around its outer top face to start it into the shell. Keep it square as it descends.',
                'Keep the magnet seated in its pocket. Use the short insert for the final push on the next page.')))

    guide_pages.append(leaf(12, 'press-the-insert', 'At the pause &middot; 2', 'Press the insert flush',
        'The short insert pushes the core home, captures the magnet and supplies a flat surface for the roof.',
        '<div class="assembly-pair">' +
        figure('insert-push', '<b>Press down.</b> The insert pushes the prepared core into its seat. Cutaway view.', '') +
        figure('flush-detail', '<b>Fully seated.</b> The flat foam face is level with both PETG rims. Cutaway detail.', '') + '</div>' +
        actions('Lower the short insert over the bore sleeve with its <b>chamfered end down</b>. Rest it on the core.',
                'Press downward evenly on opposite sides. Use the flat face of the clean plastic scraper to spread the last push across the insert.',
                'Seat the insert with its flat upper face <b>level with the PETG outer rim and bore rim</b>. The core rests on the shell floor beneath it.',
                'Lift the scraper clear. Brush or lift away any loose string from the top surface.') +
        note('The seating surface', 'The roof prints across the whole foam annulus. Leave the upper face flat and level with the two PETG rims, and keep the central guide bore open.')))

    guide_pages.append(leaf(13, 'print-the-roof', 'At the pause &middot; 3', 'Close the door and resume',
        'The remaining 17 PETG layers make the 3.06 mm roof and enclose the complete assembly.',
        figure('roof', f'Cutaway view. The coral roof joins the outer wall to the bore sleeve over the seated foam. About {roof_minutes} minutes of printing remain after the pause.', 'tall') +
        actions('Remove your hands and the scraper from the printer.',
                'Close the enclosure and press <b>Resume</b>. Let the printer restore its nozzle temperature and finish the roof.',
                'Leave the float on the sheet until the bed reaches <b>35 &deg;C or below</b>.') +
        note('One continuous shell', 'The final roof is part of the PETG print. There is no separate lid to glue on and no adhesive cure after printing.')))

    guide_pages.append(leaf(14, 'finish-the-float', 'Finish', 'Release and finish',
        'The cooled print is the completed float. Keep the roof uppermost when fitting it to its guide.',
        figure('finished', 'Finished PETG float. The open centre bore passes through the body; the magnet remains enclosed near the top.', 'tall') +
        actions('Lift the cooled Textured PEI sheet out of the printer. Flex it gently to release the float.',
                'Clip off the outer brim and pare its remaining lip flush with the bottom edge.',
                'Clip loose strings at the bore entrances and brush the exterior clean. Keep the printed PETG bore and shell walls intact.',
                'Slide the <b>3.175 mm guide rod</b> through the <b>4.8 mm central bore</b>, with the printed roof facing upward.') +
        note('Top and bottom', 'The roof is the smooth, printed top surface above the magnet. The bottom carries the Textured PEI imprint. Keep that orientation when installing the float.')))

    guide_pages.append(leaf(15, 'bench-reference', 'Keep beside the printer', 'The build at a glance',
        'Dry both spools overnight, finish the white pieces, then make the clear PETG shell around them.',
        table([('ASA Aero drying', 'AMS HT &middot; <b>80 &deg;C &times; 8 h</b>'), ('PETG Translucent drying', 'AMS 2 Pro &middot; <b>65 &deg;C &times; 12 h</b>'),
            ('Aero project', project('magnetic-float-aero.3mf')), ('Aero nozzle / bed / chamber', 'Right 0.4 mm &middot; 270 / 90 / 60 &deg;C'),
            ('Aero plate', 'Engineering plate, thin Bambu liquid glue'), ('Aero print order', f'Plate 1 core: {core_time}<br>Plate 2 insert: {insert_time}'),
            ('Before PETG', 'Cool pieces and chamber to &le;35 &deg;C.<br>Trim both pieces and seat the RC62 in the core.'),
            ('PETG project', project('magnetic-float.3mf')), ('PETG nozzle / bed', 'Left 0.6 mm &middot; 255/260 &deg;C nozzle, 70 &deg;C bed'),
            ('PETG plate / chamber', 'Clean Textured PEI &middot; chamber heater off'), ('PETG printing time', f'{shell_time}, plus insertion'),
            ('Pause', 'After 57.00 mm, before 57.18 mm'), ('Final closure', '17 roof layers &middot; 3.06 mm'), ('Release', 'Bed &le;35 &deg;C; flex sheet, remove brim')], True) +
        '<div class="assembly-strip"><div><b>1 &middot; Core</b>Magnet already seated.<br>Chamfers down.</div><div><b>2 &middot; Insert</b>Chamfers down.<br>Press level with both rims.</div><div><b>3 &middot; Resume</b>Tools clear.<br>Close enclosure.</div></div>'))

    refs = [
        ('Drying cycles', 'https://wiki.bambulab.com/en/filament-acc/filament/dry-filament', 'Bambu drying table: AMS HT / ASA Aero and AMS 2 Pro / PETG.'),
        ('ASA Aero process', 'https://wiki.bambulab.com/en/filament-acc/filament/asa-aero-printing-guide', 'Bambu ASA Aero guide and H2C filament preset.'),
        ('Clear PETG material', 'https://us.store.bambulab.com/products/petg-translucent', 'Bambu PETG Translucent, Clear 32101; same stock as the flavor reservoirs.'),
        ('Engineering plate', 'https://wiki.bambulab.com/en/general/engineering-plate-not-working-as-expected', 'Cleaning and use of Bambu liquid glue.'),
        ('Textured PEI plate', 'https://us.store.bambulab.com/products/bambu-textured-pei-plate', 'Plate preparation and removal at 35 &deg;C or below.'),
        ('RC62 ring', 'https://www.kjmagnetics.com/rc62-neodymium-ring-magnet', 'Magnet dimensions, coating and material specification.'),
    ]
    guide_pages.append(leaf(16, 'files-and-sources', 'Reference', 'Files and recipe sources',
        'Use the supplied projects for this geometry. Their nozzle assignments, fit compensation and insertion pause are included.',
        '<h2>Print projects</h2>' + table([('Foam parts', project('magnetic-float-aero.3mf')), ('PETG shell', project('magnetic-float.3mf'))]) +
        '<p>The projects sit together under <span class="file">hardware/printed-parts/cold-core/magnetic-float/</span> in this repository.</p>' +
        '<h2>Recipe basis</h2><table>' + ''.join(f'<tr><td class="k"><a href="{u}">{t}</a></td><td>{d}</td></tr>' for t,u,d in refs) + '</table>' +
        '<p>The shell uses Bambu PETG Translucent Clear (32101), with sealing settings derived from the water-holding reservoir recipe and adapted to this float. Aero uses the Bambu filament preset with solid foam fill. The 35 &deg;C Aero handling/chamber changeover point is the selected shop procedure.</p>' +
        '<p class="dim">Prepared 1 October 2026. Illustrations are drawn from the float CAD. Clear PETG is shaded pale blue for clarity; warm white is Aero, and coral marks the part being added. Cutaway faces and insertion arrows explain assembly; they are not extra parts.</p>', 'sources'))

    expected = set(guide_pages)
    for stale in GUIDE.glob('[0-9][0-9]-*.html'):
        if stale.name not in expected:
            stale.unlink()
    inputs = ['design.json', 'print-profile.json', 'verification.json', 'magnetic-float-aero.3mf', 'magnetic-float.3mf']
    manifest = {'title':'Magnetic float build guide', 'pages': guide_pages,
                'recipe_sources':'../../tools/magnetic-float-guide/build-recipe-sources.json',
                'inputs_sha256': {str((FLOAT / name).relative_to(ROOT)): hashlib.sha256((FLOAT / name).read_bytes()).hexdigest() for name in inputs}}
    (GUIDE / 'guide-inputs.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Authored {len(guide_pages)} pages; printing times {core_time}, {insert_time}, {shell_time}.')


if __name__ == '__main__':
    main()
