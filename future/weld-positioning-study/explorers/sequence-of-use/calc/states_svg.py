"""Session state chart: phases across, elements down. Text is the state each element must be in."""
phases = ['0 open\nsession', '1 load\ntube', '2 seat +\nindicate', '3 plate at\nrecess', '4 shoe +\ncontinuity',
          '5 tacks\n(8)', '6 hanger off,\nindex to tack 1', '7 aim +\ndot dry run', '8 weld\n380°', '9 stop /\nstuck wire',
          '10 gun\naway', '11 unload /\ninvert', '12 next\ntube']
C = {'F': '#dff2df', 'P': '#e6e6e6', 'S': '#c9d6ee', 'L': '#8fb0e0', 'X': '#f4d6d6', 'H': '#f6ecc8'}
rows = [
 ('A lid carrier', ['P park; set stickout', 'P lid open', 'P', 'P', 'P', 'L lid shut, fixture tacks*', 'L', 'L seated; Z dial or touch-off', 'L seated', 'L stays; snip', 'P lid open', 'P', 'P']),
 ('B gun stays', ['L aim set once', 'L (tube is out)', 'L', 'L', 'L', 'L fixture tacks*', 'L', 'L drawer in; verify', 'L', 'L stays; snip', 'L drawer out;\nstickout gauge', 'L', 'L']),
 ('C rim saddle', ['P park on balancer', 'P lifted off', 'P', 'P', 'P', 'S on rim, tacks*', 'S', 'S contacts loaded', 'S riding rim', 'S stays; snip', 'P lift off', 'P', 'P']),
 ('table', ['F set speed/dir', 'F hand-turn', 'F hand/pedal', 'F', 'F 2 dry revs', 'P stop at tack angles', 'P back to tack 1', 'F pedal, 1 rev', 'F pedal held', 'P stopped (free after 10 s)', 'P', 'F', 'F']),
 ('wire', ['H thread, trim', '', '', '', '', 'H short pulses', 'H on arriving side', 'H tip at corner', 'H feeding', 'X stuck? snip', 'H re-trim at gauge', '', '']),
 ('plate hanger', ['', '', '', 'H on: sets 6.35', 'H', 'H holds plate', 'H off (H1) / stays (H2)', '', '', '', '', 'P', '']),
 ('trigger', ['', '', '', '', '', 'H pulses', '', 'X must NOT fire', 'H held', 'H released', '', '', '']),
 ('eyes', ['screen, gauge', 'nest', 'indicator', 'depth gauge', 'meter', 'tack + index', 'index mark', 'dot vs corner (camera)', 'puddle + 20° pointer', 'wire at bead', 'stickout gauge', 'tube', '']),
 ('record', ['recipe card', 'tube id, length', 'radial TIR', 'face TIR', 'pass', 'tack angles', '', 'dot track video', 'degrees at release', 'stuck? where', 'stickout', '', '']),
]
cw, ch, lw, top = 92, 46, 110, 92
W = lw + cw * len(phases) + 20
H = top + 50 + ch * len(rows) + 90
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif" font-size="9.5">',
     '<rect width="100%" height="100%" fill="#fbfbf8"/>',
     '<text x="10" y="20" font-size="14" font-weight="bold">One session, phase by phase: what each element must be (sequence-of-use)</text>',
     '<text x="10" y="36" font-size="11">Gun rows: P parked/free of the work · S located by contact with the work · L located by a stored seat (frame reference). * fixture tacks need the stationary swivel hanger (H2).</text>',
     '<text x="10" y="50" font-size="11">Colours: green free/moving · grey parked · light blue contact-located · blue seat-locked · yellow hands-on step · red the risky moment.</text>']
for i, p in enumerate(phases):
    x = lw + i * cw
    for j, line in enumerate(p.split('\n')):
        o.append(f'<text x="{x+4}" y="{top+j*12}" font-weight="bold">{line}</text>')
for r, (name, cells) in enumerate(rows):
    y = top + 30 + r * ch
    o.append(f'<text x="10" y="{y+26}" font-weight="bold" font-size="11">{name}</text>')
    for i, c in enumerate(cells):
        x = lw + i * cw
        key = c[:1] if c[:2] in ('F ', 'P ', 'S ', 'L ', 'X ', 'H ') or c in ('F', 'P', 'S', 'L', 'X', 'H') else ''
        fill = C.get(key, '#ffffff')
        o.append(f'<rect x="{x}" y="{y}" width="{cw-2}" height="{ch-2}" fill="{fill}" stroke="#bbb"/>')
        txt = c[2:] if key and len(c) > 1 else ('' if key else c)
        lines = []
        for part in txt.split('\n'):
            words, cur = part.split(), ''
            for w in words:
                if len(cur) + len(w) + 1 > 17:
                    lines.append(cur); cur = w
                else:
                    cur = (cur + ' ' + w).strip()
            if cur: lines.append(cur)
        for k, ln in enumerate(lines[:3]):
            o.append(f'<text x="{x+3}" y="{y+13+k*11}">{ln}</text>')
y = top + 30 + len(rows) * ch + 20
o.append(f'<text x="10" y="{y}" font-size="11">Reading across: the gun needs to be completely out of the way (1–4, 11), precisely and stiffly located (7–8), perfectly still (9), and to return to a remembered pose (10→7).</text>')
o.append(f'<text x="10" y="{y+16}" font-size="11">In B the gun row is solid blue: the tube carries all the state changes. In A the gun alternates between two stored states. In C precision exists only while contacts are loaded.</text>')
o.append(f'<text x="10" y="{y+32}" font-size="11">Phase 5 is the collision point: any hanger that bridges the rim crosses the station when the table indexes between tacks.</text>')
o.append('</svg>')
open('../sketches/session-states.svg', 'w').write('\n'.join(o))
print('ok', W, H)
