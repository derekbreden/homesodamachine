'Draw the faucet shop book and its rear-display wiring plate by hand.\n\nThis is a manual document tool. It has no CAD imports or build-system target.\nThe PDF and SVG share one wiring illustration; the source receipt records the\nprocedures and firmware reviewed for this edition.'
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def figure(*args, **kwargs):
    return _compiled('faucet_book',path=('figure',),args=args,kwargs=kwargs)

class SvgArt:
    'The same top-left drawing primitives as the PDF illustration.'
    def __init__(self, *args, **kwargs):
        return _compiled('faucet_book',path=('SvgArt.__init__',),args=(self,*args),kwargs=kwargs)

    def shape(self, *args, **kwargs):
        return _compiled('faucet_book',path=('SvgArt.shape',),args=(self,*args),kwargs=kwargs)

    def line(self, *args, **kwargs):
        return _compiled('faucet_book',path=('SvgArt.line',),args=(self,*args),kwargs=kwargs)

    def rect(self, *args, **kwargs):
        return _compiled('faucet_book',path=('SvgArt.rect',),args=(self,*args),kwargs=kwargs)

    def ellipse(self, *args, **kwargs):
        return _compiled('faucet_book',path=('SvgArt.ellipse',),args=(self,*args),kwargs=kwargs)

    def label(self, *args, **kwargs):
        return _compiled('faucet_book',path=('SvgArt.label',),args=(self,*args),kwargs=kwargs)

    def arrow(self, *args, **kwargs):
        return _compiled('faucet_book',path=('SvgArt.arrow',),args=(self,*args),kwargs=kwargs)

def board(*args, **kwargs):
    'Rear component view, USB-C at top. P1 odds left, evens right.'
    return _compiled('faucet_book',path=('board',),args=args,kwargs=kwargs)

def installed_orientation_art(*args, **kwargs):
    'Side section: USB at the outlet, opposite end up the gooseneck.'
    return _compiled('faucet_book',path=('installed_orientation_art',),args=args,kwargs=kwargs)

def wiring_art(*args, **kwargs):
    return _compiled('faucet_book',path=('wiring_art',),args=args,kwargs=kwargs)

def write_wiring_svg(*args, **kwargs):
    return _compiled('faucet_book',path=('write_wiring_svg',),args=args,kwargs=kwargs)

def note(*args, **kwargs):
    return _compiled('faucet_book',path=('note',),args=args,kwargs=kwargs)

def steps(*args, **kwargs):
    return _compiled('faucet_book',path=('steps',),args=args,kwargs=kwargs)

def start(*args, **kwargs):
    return _compiled('faucet_book',path=('start',),args=args,kwargs=kwargs)

def page(*args, **kwargs):
    return _compiled('faucet_book',path=('page',),args=args,kwargs=kwargs)

def path(*args, **kwargs):
    return _compiled('faucet_book',path=('path',),args=args,kwargs=kwargs)

def screw(*args, **kwargs):
    return _compiled('faucet_book',path=('screw',),args=args,kwargs=kwargs)

def insert(*args, **kwargs):
    return _compiled('faucet_book',path=('insert',),args=args,kwargs=kwargs)

def bundle(*args, **kwargs):
    return _compiled('faucet_book',path=('bundle',),args=args,kwargs=kwargs)

def prep_art(*args, **kwargs):
    return _compiled('faucet_book',path=('prep_art',),args=args,kwargs=kwargs)

def cad_image(*args, **kwargs):
    return _compiled('faucet_book',path=('cad_image',),args=args,kwargs=kwargs)

def donor_art(*args, **kwargs):
    return _compiled('faucet_book',path=('donor_art',),args=args,kwargs=kwargs)

def thimble_art(*args, **kwargs):
    return _compiled('faucet_book',path=('thimble_art',),args=args,kwargs=kwargs)

def sleeve_insert_art(*args, **kwargs):
    return _compiled('faucet_book',path=('sleeve_insert_art',),args=args,kwargs=kwargs)

def shell_insertion_art(*args, **kwargs):
    return _compiled('faucet_book',path=('shell_insertion_art',),args=args,kwargs=kwargs)

def route_tip_art(*args, **kwargs):
    return _compiled('faucet_book',path=('route_tip_art',),args=args,kwargs=kwargs)

def closure_art(*args, **kwargs):
    return _compiled('faucet_book',path=('closure_art',),args=args,kwargs=kwargs)

def solder_art(*args, **kwargs):
    return _compiled('faucet_book',path=('solder_art',),args=args,kwargs=kwargs)

def display_art(*args, **kwargs):
    return _compiled('faucet_book',path=('display_art',),args=args,kwargs=kwargs)

def mount_art(*args, **kwargs):
    return _compiled('faucet_book',path=('mount_art',),args=args,kwargs=kwargs)

def supply_art(*args, **kwargs):
    return _compiled('faucet_book',path=('supply_art',),args=args,kwargs=kwargs)

def plug_art(*args, **kwargs):
    return _compiled('faucet_book',path=('plug_art',),args=args,kwargs=kwargs)

def sig6_table(*args, **kwargs):
    return _compiled('faucet_book',path=('sig6_table',),args=args,kwargs=kwargs)

def plug_page(*args, **kwargs):
    return _compiled('faucet_book',path=('plug_page',),args=args,kwargs=kwargs)

def write_connector_svg(*args, **kwargs):
    return _compiled('faucet_book',path=('write_connector_svg',),args=args,kwargs=kwargs)

def sleeve_art(*args, **kwargs):
    return _compiled('faucet_book',path=('sleeve_art',),args=args,kwargs=kwargs)

def final_art(*args, **kwargs):
    return _compiled('faucet_book',path=('final_art',),args=args,kwargs=kwargs)

def cover(*args, **kwargs):
    return _compiled('faucet_book',path=('cover',),args=args,kwargs=kwargs)

def wiring_page(*args, **kwargs):
    return _compiled('faucet_book',path=('wiring_page',),args=args,kwargs=kwargs)

def sources_page(*args, **kwargs):
    return _compiled('faucet_book',path=('sources_page',),args=args,kwargs=kwargs)

def build(*args, **kwargs):
    return _compiled('faucet_book',path=('build',),args=args,kwargs=kwargs)

__all__ = ['annotations', 'html', 'json', 'math', 're', 'sys', 'Path', 'ROOT', 'GUIDE', 'PDF', 'SITE', 'DOCS', 'VENDOR', 'SCHEMATIC', 'INTERFACE', 'JACK', 'USOC', 'MODULAR_VIEW', 'FU', 'SHELL', 'OBSERVATIONS', 'INSERTION', 'INSERTION_PDF', 'N', 'GREEN', 'BRASS', 'PAD', 'PCB', 'WIRE', 'SIG6', 'SOURCES', 'figure', 'SvgArt', 'board', 'installed_orientation_art', 'wiring_art', 'write_wiring_svg', 'note', 'steps', 'start', 'page', 'path', 'screw', 'insert', 'bundle', 'prep_art', 'cad_image', 'donor_art', 'thimble_art', 'sleeve_insert_art', 'shell_insertion_art', 'route_tip_art', 'closure_art', 'solder_art', 'display_art', 'mount_art', 'supply_art', 'plug_art', 'sig6_table', 'plug_page', 'write_connector_svg', 'sleeve_art', 'final_art', 'cover', 'wiring_page', 'sources_page', 'build']
_bind('faucet_book',globals())

if __name__ == '__main__':
    _compiled('faucet_book','main')
