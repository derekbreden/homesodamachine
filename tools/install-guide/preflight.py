#!/usr/bin/env python3
"""Check the Comic Book PDFs with pypdf, pdfplumber and Poppler pdfimages."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import pdfplumber
from pypdf import PdfReader
from pypdf.generic import ArrayObject, IndirectObject


ROOT = Path(__file__).resolve().parents[2]
TOC = [
    (4, 'Mount the faucet'),
    (6, 'Add the cold-water tee'),
    (11, 'Match the rear connections'),
    (13, 'Prepare the cylinder'),
    (15, 'Water, then gas, then power'),
    (18, 'Fill both flavors'),
    (20, 'Chill. Choose. Pour.'),
]


@dataclass(frozen=True)
class Spec:
    filename: str
    pages: int
    media: tuple[float, float, float, float]
    trim: tuple[float, float, float, float]
    press: bool = False
    raster: bool = False


SPECS = [
    Spec('install-guide.pdf', 24, (0, 0, 477, 738), (0, 0, 477, 738)),
    Spec('press/interior.pdf', 20, (0, 0, 495, 756), (9, 9, 486, 747), True),
    Spec('press/cover.pdf', 2, (0, 0, 972, 756), (9, 9, 963, 747), True, True),
]


def dereference(value):
    return value.get_object() if hasattr(value, 'get_object') else value


def object_key(value):
    reference = value if isinstance(value, IndirectObject) else getattr(value, 'indirect_reference', None)
    return (reference.idnum, reference.generation) if reference else id(value)


def normalized(text):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', text)).strip()


def same_box(actual, expected):
    return len(actual) == 4 and all(abs(float(a) - e) < .01 for a, e in zip(actual, expected))


class Preflight:
    def __init__(self, directory):
        self.directory = directory
        self.errors = []
        self.files = []
        self.readers = {}

    def fail(self, filename, page, message):
        location = f'{filename}, page {page}' if page else filename
        self.errors.append(f'{location}: {message}')

    def resource_checks(self, resources, spec, page, fonts, visited):
        resources = dereference(resources) or {}
        for reference in dereference(resources.get('/Font', {})).values():
            font = dereference(reference)
            name = str(font.get('/BaseFont', '(unnamed font)'))
            fonts.add(name)
            descendants = dereference(font.get('/DescendantFonts', []))
            for candidate in descendants or [font]:
                candidate = dereference(candidate)
                descriptor = dereference(candidate.get('/FontDescriptor', {}))
                embedded = any(descriptor.get(key) for key in ('/FontFile', '/FontFile2', '/FontFile3'))
                if not embedded:
                    self.fail(spec.filename, page, f'font {name} is not embedded')
        if not spec.press:
            return
        for name, reference in dereference(resources.get('/ExtGState', {})).items():
            state = dereference(reference)
            for key in ('/ca', '/CA'):
                if abs(float(state.get(key, 1)) - 1) > .000001:
                    self.fail(spec.filename, page, f'{name} has active alpha {key}={state[key]}')
            if state.get('/SMask', '/None') != '/None':
                self.fail(spec.filename, page, f'{name} contains a soft mask')
            mode = state.get('/BM', '/Normal')
            modes = mode if isinstance(mode, ArrayObject) else [mode]
            if any(value not in ('/Normal', '/Compatible') for value in modes):
                self.fail(spec.filename, page, f'{name} uses blend mode {mode}')
        for name, reference in dereference(resources.get('/XObject', {})).items():
            key = object_key(reference)
            if key in visited:
                continue
            visited.add(key)
            obj = dereference(reference)
            for mask in ('/SMask', '/Mask'):
                if obj.get(mask) is not None:
                    self.fail(spec.filename, page, f'{name} contains {mask}')
            if dereference(obj.get('/Group', {})).get('/S') == '/Transparency':
                self.fail(spec.filename, page, f'{name} contains a transparency group')
            if obj.get('/Subtype') == '/Form':
                self.resource_checks(obj.get('/Resources', {}), spec, page, fonts, visited)

    def image_checks(self, path, spec):
        if not shutil.which('pdfimages'):
            self.fail(spec.filename, None, 'pdfimages is required to measure effective image resolution')
            return []
        run = subprocess.run(['pdfimages', '-list', str(path)], capture_output=True, text=True)
        if run.returncode:
            self.fail(spec.filename, None, f'pdfimages failed: {run.stderr.strip()}')
            return []
        images = []
        for line in run.stdout.splitlines()[2:]:
            fields = line.split()
            if not fields:
                continue
            if len(fields) < 14:
                self.fail(spec.filename, None, f'unrecognized pdfimages row: {line}')
                continue
            page, number = map(int, fields[:2])
            kind = fields[2]
            if kind != 'image':
                if spec.press:
                    self.fail(spec.filename, page, f'image {number} is a {kind}, not an opaque image')
                continue
            image = {
                'page': page, 'number': number,
                'width': int(fields[3]), 'height': int(fields[4]),
                'color': fields[5], 'x_ppi': float(fields[12]), 'y_ppi': float(fields[13]),
            }
            images.append(image)
            minimum = 599 if spec.raster else 300
            if min(image['x_ppi'], image['y_ppi']) < minimum:
                self.fail(spec.filename, page, f'image {number} is {fields[12]} x {fields[13]} PPI; minimum {minimum}')
            if spec.press and (fields[5] not in ('rgb', 'icc') or fields[6] != '3'):
                self.fail(spec.filename, page, f'image {number} is {fields[5]} with {fields[6]} components; expected RGB')
        if spec.raster:
            for page in range(1, spec.pages + 1):
                if not any(image['page'] == page for image in images):
                    self.fail(spec.filename, page, 'flattened cover image is missing')
        return images

    def check_file(self, spec):
        path = self.directory / spec.filename
        if not path.is_file():
            self.fail(spec.filename, None, 'file is missing')
            return
        try:
            reader = PdfReader(path, strict=True)
        except Exception as error:
            self.fail(spec.filename, None, f'cannot read PDF: {error}')
            return
        if reader.is_encrypted:
            self.fail(spec.filename, None, 'PDF is encrypted')
            return
        self.readers[spec.filename] = reader
        if len(reader.pages) != spec.pages:
            self.fail(spec.filename, None, f'has {len(reader.pages)} pages; expected {spec.pages}')
        fonts = set()
        for index, page in enumerate(reader.pages, 1):
            boxes = {'MediaBox': (page.mediabox, spec.media), 'CropBox': (page.cropbox, spec.media),
                     'TrimBox': (page.trimbox, spec.trim)}
            if spec.press:
                boxes['BleedBox'] = (page.bleedbox, spec.media)
            for name, (actual, expected) in boxes.items():
                if not same_box(actual, expected):
                    self.fail(spec.filename, index, f'{name} is {list(actual)}; expected {list(expected)} pt')
            if int(page.get('/Rotate', 0)) % 360:
                self.fail(spec.filename, index, f'page rotation is {page.get("/Rotate")}')
            if float(page.get('/UserUnit', 1)) != 1:
                self.fail(spec.filename, index, f'UserUnit is {page.get("/UserUnit")}; expected 1')
            if spec.press:
                if page.get('/Annots'):
                    self.fail(spec.filename, index, f'contains {len(page["/Annots"])} annotations')
                if dereference(page.get('/Group', {})).get('/S') == '/Transparency':
                    self.fail(spec.filename, index, 'page has a transparency group')
            self.resource_checks(page.get('/Resources', {}), spec, index, fonts, set())
            if spec.raster and normalized(page.extract_text() or ''):
                self.fail(spec.filename, index, 'cover contains unflattened text')
        images = self.image_checks(path, spec)
        self.files.append({
            'file': spec.filename, 'pages': len(reader.pages),
            'media_box_pt': list(spec.media), 'trim_box_pt': list(spec.trim),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'fonts': sorted(fonts), 'images': images,
            'minimum_image_ppi': min((min(i['x_ppi'], i['y_ppi']) for i in images), default=None),
        })

    def check_navigation(self):
        reader = self.readers.get('install-guide.pdf')
        if reader is None or len(reader.pages) != 24:
            return

        def outlines(items):
            for item in items:
                if isinstance(item, list):
                    yield from outlines(item)
                else:
                    yield item

        destinations = list(outlines(reader.outline))
        if len(destinations) != 24:
            self.fail('install-guide.pdf', None, f'has {len(destinations)} bookmarks; expected 24')
        for index, destination in enumerate(destinations):
            actual = reader.get_destination_page_number(destination)
            if actual != index:
                self.fail('install-guide.pdf', index + 1, f'bookmark targets page {None if actual is None else actual + 1}')
        page_numbers = {object_key(page): index for index, page in enumerate(reader.pages)}

        def destination_page(destination):
            if isinstance(destination, (str, bytes)):
                named = reader.named_destinations.get(str(destination))
                return reader.get_destination_page_number(named) if named else None
            destination = dereference(destination)
            if isinstance(destination, ArrayObject) and destination:
                return page_numbers.get(object_key(destination[0]))
            return None

        links = []
        for reference in reader.pages[1].get('/Annots', []):
            annotation = dereference(reference)
            if annotation.get('/Subtype') != '/Link':
                continue
            action = dereference(annotation.get('/A', {}))
            destination = annotation.get('/Dest', action.get('/D') if action.get('/S') == '/GoTo' else None)
            if destination is not None:
                links.append((list(map(float, annotation['/Rect'])), destination_page(destination)))
        links.sort(key=lambda link: -link[0][3])
        if len(links) != len(TOC):
            self.fail('install-guide.pdf', 2, f'has {len(links)} TOC links; expected {len(TOC)}')
        with pdfplumber.open(self.directory / 'install-guide.pdf') as document:
            page = document.pages[1]
            words = page.extract_words()
            word_text = [word['text'] for word in words]
            for (rect, actual), (expected, label) in zip(links, TOC):
                if actual != expected:
                    self.fail('install-guide.pdf', 2, f'TOC "{label}" targets page {None if actual is None else actual + 1}; expected {expected + 1}')
                phrase = label.split()
                matches = [words[i:i + len(phrase)] for i in range(len(words)) if word_text[i:i + len(phrase)] == phrase]
                if len(matches) != 1:
                    self.fail('install-guide.pdf', 2, f'cannot locate the visible TOC label "{label}" once')
                elif not all(rect[0] <= (word['x0'] + word['x1']) / 2 <= rect[2]
                             and rect[1] <= page.height - (word['top'] + word['bottom']) / 2 <= rect[3]
                             for word in matches[0]):
                    self.fail('install-guide.pdf', 2, f'TOC link rectangle does not cover "{label}"')

    def check_text_margins(self):
        for spec in SPECS:
            if spec.raster or spec.filename not in self.readers:
                continue
            measurements = []
            with pdfplumber.open(self.directory / spec.filename) as document:
                for number, page in enumerate(document.pages, 1):
                    chars = [char for char in page.chars if char['text'].strip()]
                    if not chars:
                        continue
                    left, bottom, right, top = spec.trim

                    def margins(char):
                        return (char['x0'] - left, right - char['x1'],
                                char['top'] - (page.height - top), page.height - bottom - char['bottom'])

                    values = [margins(char) for char in chars]
                    minimum = dict(zip(('left', 'right', 'top', 'bottom'),
                                       (round(min(value[i] for value in values), 3) for i in range(4))))
                    measurements.append({'page': number, **minimum})
                    outside = [char for char, value in zip(chars, values) if min(value) < 35.99]
                    if outside:
                        text = ''.join(char['text'] for char in outside)
                        self.fail(spec.filename, number,
                                  f'text enters the 36 pt trim safety margin: {text!r}; margins {minimum}')
            record = next(file for file in self.files if file['file'] == spec.filename)
            record['text_margins_pt'] = measurements

    def check_interior_text(self):
        reading = self.readers.get('install-guide.pdf')
        interior = self.readers.get('press/interior.pdf')
        if reading is None or interior is None or len(reading.pages) != 24 or len(interior.pages) != 20:
            return
        for index, page in enumerate(interior.pages):
            expected = normalized(reading.pages[index + 2].extract_text() or '')
            actual = normalized(page.extract_text() or '')
            if not expected:
                self.fail('install-guide.pdf', index + 3, 'no text was extracted')
            if actual != expected:
                at = next((i for i, pair in enumerate(zip(actual, expected)) if pair[0] != pair[1]), min(len(actual), len(expected)))
                self.fail('press/interior.pdf', index + 1,
                          f'text differs from reading page {index + 3} near character {at}: '
                          f'{actual[max(0, at - 30):at + 70]!r}; expected {expected[max(0, at - 30):at + 70]!r}')

    def run(self):
        for spec in SPECS:
            self.check_file(spec)
        self.check_navigation()
        self.check_text_margins()
        self.check_interior_text()
        return {'passed': not self.errors, 'files': self.files, 'errors': self.errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=ROOT / 'hardware/install-guide')
    parser.add_argument('--json', type=Path, help='write the artifact measurements and errors as JSON')
    args = parser.parse_args()
    report = Preflight(args.directory).run()
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + '\n')
    for error in report['errors']:
        print(f'FAIL {error}', file=sys.stderr)
    for file in report['files']:
        resolution = file['minimum_image_ppi']
        print(f'{file["file"]}: {file["pages"]} pages, {len(file["images"])} images, '
              f'minimum {resolution:g} PPI' if resolution is not None else f'{file["file"]}: no images')
    print('PASS Comic Book print preflight' if report['passed'] else f'FAIL {len(report["errors"])} preflight issue(s)')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
