'Shared vector page furniture for hand-authored Letter shop guides.\n\nManual document tools live outside the hardware generator inventory. Typography,\nprint calibration and drawing primitives are shared; operations and pictures are\nowned by each guide. No geometry or fabrication source is imported here.'
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def color(*args, **kwargs):
    return _compiled('common',path=('color',),args=args,kwargs=kwargs)

def box(*args, **kwargs):
    return _compiled('common',path=('box',),args=args,kwargs=kwargs)

def text(*args, **kwargs):
    return _compiled('common',path=('text',),args=args,kwargs=kwargs)

def paragraph(*args, **kwargs):
    return _compiled('common',path=('paragraph',),args=args,kwargs=kwargs)

class Art:
    'Top-left coordinates for vector pictures; text remains upright.'
    def __init__(self, *args, **kwargs):
        return _compiled('common',path=('Art.__init__',),args=(self,*args),kwargs=kwargs)

    def __enter__(self, *args, **kwargs):
        return _compiled('common',path=('Art.__enter__',),args=(self,*args),kwargs=kwargs)

    def __exit__(self, *args, **kwargs):
        return _compiled('common',path=('Art.__exit__',),args=(self,*args),kwargs=kwargs)

    def shape(self, *args, **kwargs):
        return _compiled('common',path=('Art.shape',),args=(self,*args),kwargs=kwargs)

    def line(self, *args, **kwargs):
        return _compiled('common',path=('Art.line',),args=(self,*args),kwargs=kwargs)

    def rect(self, *args, **kwargs):
        return _compiled('common',path=('Art.rect',),args=(self,*args),kwargs=kwargs)

    def ellipse(self, *args, **kwargs):
        return _compiled('common',path=('Art.ellipse',),args=(self,*args),kwargs=kwargs)

    def label(self, *args, **kwargs):
        return _compiled('common',path=('Art.label',),args=(self,*args),kwargs=kwargs)

    def arrow(self, *args, **kwargs):
        return _compiled('common',path=('Art.arrow',),args=(self,*args),kwargs=kwargs)

    def dim(self, *args, **kwargs):
        return _compiled('common',path=('Art.dim',),args=(self,*args),kwargs=kwargs)

def badge(*args, **kwargs):
    return _compiled('common',path=('badge',),args=args,kwargs=kwargs)

def page_backdrop(*args, **kwargs):
    'Paint the bleed independently of the centered instructional layer.'
    return _compiled('common',path=('page_backdrop',),args=args,kwargs=kwargs)

def header(*args, **kwargs):
    return _compiled('common',path=('header',),args=args,kwargs=kwargs)

def footer(*args, **kwargs):
    return _compiled('common',path=('footer',),args=args,kwargs=kwargs)

def panel(*args, **kwargs):
    return _compiled('common',path=('panel',),args=args,kwargs=kwargs)

def begin_page(*args, **kwargs):
    return _compiled('common',path=('begin_page',),args=args,kwargs=kwargs)

def end_page(*args, **kwargs):
    return _compiled('common',path=('end_page',),args=args,kwargs=kwargs)

def publish(*args, **kwargs):
    'Commit-ready PDF/thumbnail/catalog sidecar and a source-hash receipt.\n\n`pdf` is the output/pdf delivery file. `guide_dir` carries the identical\ncanonical document served by /drawings. Sources are explicitly selected\nlocal relative paths; hashing them does not evaluate the appliance build.'
    return _compiled('common',path=('publish',),args=args,kwargs=kwargs)

__all__ = ['annotations', 'hashlib', 'json', 'math', 'shutil', 'subprocess', 'Path', 'HexColor', 'ParagraphStyle', 'pdfmetrics', 'TTFont', 'canvas', 'Paragraph', 'ROOT', 'W', 'H', 'CONTENT_SCALE', 'BLEED_OVERHANG', 'BAND_INSET', 'INK', 'BLUE', 'ORANGE', 'PAPER', 'ICE', 'STEEL', 'MUTED', 'RULE', 'COPPER', 'GLOVE', 'FONT_DIR', 'color', 'box', 'text', 'paragraph', 'Art', 'badge', 'page_backdrop', 'header', 'footer', 'panel', 'begin_page', 'end_page', 'publish']
_bind('common',globals())

if __name__ == '__main__':
    _compiled('common','main')
