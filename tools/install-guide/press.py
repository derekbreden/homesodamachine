"""Lulu Comic Book editions: four cover faces and twenty interior pages."""
from copy import deepcopy
import hashlib
import io
from pathlib import Path
import shutil
import subprocess
import zipfile

from PIL import Image, ImageCms
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import (
    ArrayObject, DecodedStreamObject, DictionaryObject, NameObject,
    NumberObject, RectangleObject,
)
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


TRIM_W, TRIM_H = 477, 738
BLEED = 9
INTERIOR_SIZE = (TRIM_W + 2*BLEED, TRIM_H + 2*BLEED)
COVER_SIZE = (2*TRIM_W + 2*BLEED, TRIM_H + 2*BLEED)


def boxes(page, width, height, inset=0):
    page.mediabox = RectangleObject((0, 0, width, height))
    page.cropbox = RectangleObject((0, 0, width, height))
    page.bleedbox = RectangleObject((0, 0, width, height))
    page.trimbox = RectangleObject((inset, inset, width-inset, height-inset))


def srgb(writer):
    """Calibrate RGB vectors and images with the standard sRGB profile."""
    profile = DecodedStreamObject()
    profile.set_data(ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes())
    profile[NameObject('/N')] = NumberObject(3)
    # Fix the ICC creation timestamp so repeated builds have identical bytes.
    data = bytearray(profile.get_data())
    data[24:36] = bytes.fromhex('07d000010001000000000000')
    profile.set_data(bytes(data))
    color_space = ArrayObject([NameObject('/ICCBased'), writer._add_object(profile)])
    for page in writer.pages:
        resources = page['/Resources'].get_object()
        spaces = resources.setdefault(NameObject('/ColorSpace'), DictionaryObject())
        spaces[NameObject('/DefaultRGB')] = color_space


def write_pdf(writer, path, title):
    writer.add_metadata({
        '/Title': title,
        '/Author': 'Derek Bredensteiner',
        '/Subject': 'Home Soda Machine install guide - Lulu Comic Book edition',
    })
    srgb(writer)
    with Path(path).open('wb') as stream:
        writer.write(stream)


def write_editions(data, reading_path, press_dir, output_dir, scratch_dir):
    for directory in (press_dir, output_dir, scratch_dir):
        directory.mkdir(parents=True, exist_ok=True)

    source = PdfReader(io.BytesIO(data))
    assert len(source.pages) == 24

    reading = PdfWriter()
    reading.clone_document_from_reader(source)
    for page in reading.pages:
        page.add_transformation(Transformation().translate(-BLEED, -BLEED))
        boxes(page, TRIM_W, TRIM_H)
        for reference in page.get('/Annots', []):
            annotation = reference.get_object()
            annotation[NameObject('/Rect')] = RectangleObject(
                [float(value)-BLEED for value in annotation['/Rect']]
            )
    write_pdf(reading, reading_path, 'Home Soda Machine - Install guide')

    interior = PdfWriter()
    for source_page in source.pages[2:22]:
        page = interior.add_page(source_page, excluded_keys=['/Annots'])
        boxes(page, *INTERIOR_SIZE, BLEED)
    interior_path = press_dir/'interior.pdf'
    write_pdf(interior, interior_path, 'Home Soda Machine - Lulu Comic Book interior')

    # Lulu's two cover pages are flat spreads: outside, then inside.
    cover = PdfWriter()
    for left, right in ((23, 0), (1, 22)):
        spread = cover.add_blank_page(*COVER_SIZE)
        for index, offset in ((left, 0), (right, TRIM_W)):
            panel = deepcopy(source.pages[index])
            panel.pop('/Annots', None)
            spread.merge_transformed_page(panel, Transformation().translate(offset, 0))
        boxes(spread, *COVER_SIZE, BLEED)
    vector_path = scratch_dir/'cover-vector.pdf'
    write_pdf(cover, vector_path, 'Home Soda Machine - Cover artwork')

    # Lulu requests flattened cover objects. Render both complete spreads at
    # 600 PPI, retaining the interior's embedded vector text separately.
    subprocess.run([
        'pdftoppm', '-r', '600', '-png', str(vector_path),
        str(scratch_dir/'cover-600'),
    ], check=True)
    flat_buffer = io.BytesIO()
    flat = canvas.Canvas(flat_buffer, pagesize=COVER_SIZE, pageCompression=1,
                         invariant=1, initialFontName='Regular')
    for number in (1, 2):
        image = Image.open(scratch_dir/f'cover-600-{number}.png').convert('RGB')
        assert image.size == (8100, 6300), image.size
        flat.drawImage(ImageReader(image), 0, 0, width=COVER_SIZE[0], height=COVER_SIZE[1])
        flat.showPage()
    flat.save()
    cover = PdfWriter()
    for page in PdfReader(io.BytesIO(flat_buffer.getvalue())).pages:
        page = cover.add_page(page)
        boxes(page, *COVER_SIZE, BLEED)
    cover_path = press_dir/'cover.pdf'
    write_pdf(cover, cover_path, 'Home Soda Machine - Lulu Comic Book cover')

    for source_path, name in (
        (reading_path, 'install-guide.pdf'),
        (interior_path, 'install-guide-lulu-interior.pdf'),
        (cover_path, 'install-guide-lulu-cover.pdf'),
    ):
        shutil.copy2(source_path, output_dir/name)
        print(f'{output_dir/name}: {source_path.stat().st_size//1024} KB')


def make_order_bundle(press_dir, output_dir):
    instructions = output_dir/'install-guide-lulu-order.md'
    shutil.copy2(press_dir/'ORDER.md', instructions)
    names = [instructions.name, 'install-guide-lulu-interior.pdf',
             'install-guide-lulu-cover.pdf', 'install-guide.pdf']
    checksums = output_dir/'install-guide-lulu-SHA256SUMS.txt'
    checksums.write_text(''.join(
        f'{hashlib.sha256((output_dir/name).read_bytes()).hexdigest()}  {name}\n'
        for name in names
    ))
    bundle = output_dir/'install-guide-lulu-order.zip'
    with zipfile.ZipFile(bundle, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in names + [checksums.name]:
            info = zipfile.ZipInfo(name, date_time=(2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (output_dir/name).read_bytes())
    print(f'{bundle}: {bundle.stat().st_size//1024} KB')
