#!/usr/bin/env python3
"""Record manually identified photo landmarks and locally calibrated lengths."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SLEEVE_LENGTH = 30.7
GRIP_LENGTH = 83.
READINGS = [
    {'photo': 'IMG_7911.jpg', 'feature': 'exposed-copper-nozzle',
     'reference_mm': SLEEVE_LENGTH, 'reference': 'straight silver sleeve',
     'a': [445., 572.], 'b': [289.5, 595.5], 'c': [159.5, 615.]},
    {'photo': 'IMG_7915.jpg', 'feature': 'exposed-copper-nozzle',
     'reference_mm': SLEEVE_LENGTH, 'reference': 'straight silver sleeve',
     'a': [396., 703.], 'b': [222.5, 718.5], 'c': [86., 731.5]},
    {'photo': 'IMG_7910.jpg', 'feature': 'boot-cuff',
     'reference_mm': GRIP_LENGTH, 'reference': 'approximate grip-axis endpoints',
     'a': [1063., 514.], 'b': [1060., 868.], 'c': [1065., 1002.]}
]


def main():
    try:
        font = ImageFont.truetype('Arial.ttf', 22)
    except OSError:
        font = ImageFont.load_default(size=22)
    result = []
    for reading in READINGS:
        r = reading.copy()
        a, b, c = [np.array(r[key]) for key in ('a', 'b', 'c')]
        length = np.linalg.norm(b-a)
        axis = (b-a)/length
        r['reference_pixels'] = float(length)
        r['feature_projected_pixels'] = float((c-b) @ axis)
        r['length_estimate_mm'] = float(r['reference_mm']*(c-b) @ axis/length)
        result.append(r)
        im = Image.open(HERE/'photos'/r['photo']).convert('RGB')
        draw = ImageDraw.Draw(im)
        for p, label in [(a, 'A'), (b, 'B'), (c, 'C')]:
            x, y = p
            draw.ellipse([x-7, y-7, x+7, y+7], fill='#ffe680', outline='black', width=2)
            draw.text((x+10, y+10), label, fill='#ffe680', font=font,
                      stroke_width=2, stroke_fill='black')
        draw.line([tuple(a), tuple(b)], fill='#4edcff', width=4)
        draw.line([tuple(b), tuple(c)], fill='#ffe680', width=4)
        draw.rectangle((15, 15, 930, 100), fill='#182430')
        draw.text((30, 25), f"A-B: {r['reference_mm']:.1f} mm reference ({r['reference']})",
                  font=font, fill='white')
        draw.text((30, 58), f"B-C: {r['length_estimate_mm']:.1f} mm local photo estimate",
                  font=font, fill='#ffe680')
        im.save(HERE/'photos'/(Path(r['photo']).stem+'-measured.jpg'), quality=91)
    (HERE/'photo-measurements.json').write_text(json.dumps({
        'coordinates': 'pixels in the committed 1824 x 1368 images, origin top left',
        'method': 'Manual feature selection; project B-C onto A-B, scale by the '
                  'scanned local reference length. Adjacent axial features share '
                  'approximately the same foreshortening.',
        'readings': result,
        'limits': ['Photo measurements are estimates; landmark choice and perspective '
                   'are not a calibrated uncertainty distribution.',
                   'The cuff reference endpoints approximate the projected grip axis; '
                   'the boot shoulder is rounded and its boundary is gradual.']}, indent=2)+'\n')


if __name__ == '__main__':
    main()
