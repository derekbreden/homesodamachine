"""Render the two final PDFs for visual review and record that completed review.

Run with --render, inspect every contact sheet and the full critical pages,
then run --record after the entire latest output has been visually accepted.
No mechanical or electrical qualification is asserted by this document check.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
GUIDE=ROOT/'hardware/gun-positioner-guide'
OUT=GUIDE/'out/pdf-qa'
POPPLER=Path(os.environ.get('GP_PDFTOPPM',shutil.which('pdftoppm') or
    str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm')))
FILES={'guide':'gun-positioner-guide.pdf','templates':'gun-positioner-drill-templates.pdf'}


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def normalized(s):return re.sub(r'\s+',' ',s).strip()


def inspect(verify_sources=True):
    manifest=json.loads((GUIDE/'page-manifest.json').read_text())
    templates=json.loads((GUIDE/'drill-template-receipt.json').read_text())
    binding=json.loads((GUIDE/'source-receipt.json').read_text())
    if verify_sources:
        for p,h in binding['source_sha256'].items():
            if digest(ROOT/p)!=h:raise RuntimeError(f'Stale binding: {p}')
    if digest(GUIDE/FILES['guide'])!=binding['pdf_sha256']:raise RuntimeError('Guide PDF changed after binding')
    if digest(GUIDE/FILES['templates'])!=templates['pdf_sha256']:raise RuntimeError('Template PDF changed after binding')
    result={}
    for key,file in FILES.items():
        reader=PdfReader(GUIDE/file)
        expected=manifest['pages'] if key=='guide' else templates['pages']
        if len(reader.pages)!=expected:raise RuntimeError(f'{file}: wrong page count')
        font_names=set()
        for i,p in enumerate(reader.pages):
            if any(abs(float(v)-goal)>.02 for v,goal in zip(p.mediabox[2:],[612,792])):
                raise RuntimeError(f'{file} page{i+1}: not Letter')
            text=normalized(p.extract_text())
            if not text:raise RuntimeError(f'{file} page{i+1}: no vector text')
            # PDF text extraction can concatenate positioned lines; ignore only whitespace.
            if key=='guide' and re.sub(r'\s+','',manifest['leaves'][i]['title']) not in re.sub(r'\s+','',text):
                raise RuntimeError(f'{file} page{i+1}: wrong/missing operation title')
            for font in p['/Resources'].get('/Font',{}).get_object().values():
                font_names.add(str(font.get_object().get('/BaseFont','')))
        result[key]=dict(file=file,pages=len(reader.pages),pdf_sha256=digest(GUIDE/file),
                         page_inches=[8.5,11],all_titles_vector_text=True,
                         outline_items=len(reader.outline),fonts=sorted(font_names),
                         source_binding_checked=verify_sources)
    return result


def render(result):
    if not POPPLER.exists():raise RuntimeError(f'Missing Poppler: {POPPLER}')
    OUT.mkdir(parents=True,exist_ok=True)
    font=ImageFont.truetype(str(ROOT/'hardware/quickstart-codex/fonts/Plex-Regular.ttf'),18)
    for key,data in result.items():
        folder=OUT/key;folder.mkdir(exist_ok=True)
        for p in folder.glob('*.png'):p.unlink()
        subprocess.run([str(POPPLER),'-png','-r','110',str(GUIDE/data['file']),str(folder/'page')],check=True)
        pages=sorted(folder.glob('page-*.png'),key=lambda p:int(p.stem.split('-')[-1]))
        if len(pages)!=data['pages']:raise RuntimeError(f'Incomplete Poppler output: {key}')
        for first in range(0,len(pages),9):
            sheet=Image.new('RGB',(1830,2454),'#dce2eb');draw=ImageDraw.Draw(sheet)
            for j,p in enumerate(pages[first:first+9]):
                page=Image.open(p).convert('RGB');page.thumbnail((590,764))
                x=(j%3)*610+10;y=(j//3)*818+36
                sheet.paste(page,(x,y));draw.text((x,y-26),f'{key} / {first+j+1}',font=font,fill='#202337')
            sheet.save(folder/f'contact-{first//9+1:02d}.png')
        (folder/'render-receipt.json').write_text(json.dumps(dict(**data,
            renderer='Poppler pdftoppm -png -r110',
            page_png_sha256={p.name:digest(p) for p in pages}),indent=2)+'\n')
    print(json.dumps({key:dict(pages=d['pages'],contact_sheets=(d['pages']+8)//9) for key,d in result.items()}))


def record(result):
    for key,data in result.items():
        rendered=json.loads((OUT/key/'render-receipt.json').read_text())
        if data['pdf_sha256']!=rendered['pdf_sha256']:raise RuntimeError('Visual review belongs to an older PDF')
        if not rendered['source_binding_checked']:raise RuntimeError('Layout-only output cannot record final source-verified review')
        for p,h in rendered['page_png_sha256'].items():
            if digest(OUT/key/p)!=h:raise RuntimeError('A rendered review page changed')
    record=dict(schema=1,document_checks=result,
        inspection='Every final bound guide page and every final template tile rendered with Poppler and visually inspected. Critical assembly, electrical, force, camera and command leaves additionally inspected at full page scale.',
        accepted_layout=dict(clipping=False,overlapping_text=False,broken_images=False,
                             unreadable_glyphs=False,missing_pages=False,
                             consistent_numbering=True,letter_actual_size=True),
        source_binding='The guide build verified every used CAD PNG, vector schematic and template PDF against its current source/input hashes before binding.',
        scope='Document/artifact quality only. No printed part, received fit, actual load, camera hardware, powered controller, physical accuracy or live-weld qualification is asserted.',
        qa_source_sha256=digest(Path(__file__)))
    (GUIDE/'visual-qa-receipt.json').write_text(json.dumps(record,indent=2)+'\n')
    print('Recorded final PDF and template visual review')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--render',action='store_true');parser.add_argument('--record',action='store_true')
    parser.add_argument('--layout-only',action='store_true',help='Inspect a bound draft layout without accepting its changing source inputs; cannot record final review')
    args=parser.parse_args()
    if args.layout_only and args.record:parser.error('Layout-only mode cannot record final review')
    result=inspect(verify_sources=not args.layout_only)
    if args.render:render(result)
    if args.record:record(result)
    if not args.render and not args.record:print(json.dumps(result,indent=2))
