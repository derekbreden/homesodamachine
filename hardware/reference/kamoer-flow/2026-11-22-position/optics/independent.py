#!/usr/bin/env python3
"""Locate the liquid on two independently searched flanks and measure it against the cup's front printing."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d, maximum_filter1d, uniform_filter1d

import register_cup

HERE = Path(__file__).resolve().parent
CROP = (950, 300, 2070, 1205)
CUP_ML = 236.5882365
OFFSETS = np.arange(-30, 134)
# The reference rows follow the near-wall contact on the focused calibration image.
# These column patches are disjoint from the operational reader on each side.
SITES = {
    "left": [(1045,861), (1056,862), (1067,864), (1078,863), (1108,858), (1121,855), (1134,853),
             (1228,842), (1240,840), (1252,838), (1276,836), (1288,836), (1300,835)],
    "right": [(1590,816), (1604,815), (1618,814), (1632,813), (1646,813), (1660,812), (1674,810),
              (1779,800), (1793,799), (1807,798), (1821,797), (1895,792), (1909,790), (1923,788),
              (1937,786), (1951,784), (1965,783), (1979,782)]
}
# The quarter-cup and third-cup scales bracket both camera sightlines.
STATIONS = {
    "left": (1180, [(684,1.5), (826,1.25), (980,1), (1128,.75)]),
    "right": (1730, [(542,5/3), (756,4/3), (965,1), (1176,2/3)])
}


def crop_frame(path):
    image = Image.open(path)
    if image.size == (2320,1744):
        return image.crop(CROP)
    if image.size == (CROP[2]-CROP[0], CROP[3]-CROP[1]):
        return image
    raise ValueError(f"Unrecognized sensor or crop dimensions {image.size}")


def anchor_rows(color, x, marks):
    red, green, blue = np.moveaxis(color.astype(float), 2, 0)
    ink = red - np.maximum(green, blue)
    observations = []
    for prior, cups in marks:
        rows = np.arange(prior-14, prior+15)
        centers = []
        for xx in range(x-22, x+23, 3):
            profile = ink[rows-CROP[1], xx-CROP[0]]
            weights = np.maximum(profile-np.percentile(profile,12), 0)
            if weights.max() < 5:
                continue
            weights[weights < .35 * weights.max()] = 0
            centers.append(float(rows @ weights / weights.sum()))
        if len(centers) < 7:
            raise ValueError(f"Unreadable graduation near x={x}, y={prior}")
        observations.append([float(np.median(centers)), cups, float(np.std(centers))])
    return observations


def make_reference(luma_path, color_path, destination):
    gray = np.asarray(crop_frame(luma_path).convert("L"))
    color = np.asarray(crop_frame(color_path).convert("RGB"), dtype=np.float32)
    red, green, blue = np.moveaxis(color, 2, 0)
    red_excess = (red-np.maximum(green,blue)) / (red+green+blue+18)
    background = uniform_filter1d(red_excess, 41, axis=0)
    ink = (red_excess-background > .045) & (red-np.maximum(green,blue) > 10)
    columns = sorted({x for points in SITES.values() for x,_ in points})
    masks, baseline = [], []
    for x in columns:
        strip = slice(x-CROP[0]-4, x-CROP[0]+5)
        masks.append(ink[:,strip].mean(1) > .4)
        baseline.append(gray[:,strip].mean(1))
    np.savez_compressed(destination, ink=masks, x=columns, baseline=np.asarray(baseline,dtype=np.float32))
    info = {
        "source": "balance-4600-return", "sensor_size": [2320,1744], "crop_ltrb": CROP,
        "cups_to_ml": CUP_ML, "graduations_row_cups_column_sd_px": {
            side:anchor_rows(color,x,marks) for side,(x,marks) in STATIONS.items()
        },
        "volume_basis": "Piecewise linear interpolation between front cup marks at each sightline. The kitchen cup has no independent volumetric calibration."
    }
    destination.with_suffix(".json").write_text(json.dumps(info,indent=2)+"\n")


def ink_state(path):
    if path is None:
        return {"method":"fixed camera pixels"}, {s:np.zeros(2) for s in SITES}
    tracks = register_cup.form(path, detail=True)
    fits, diagnostics = {}, {}
    for side, stamp in tracks.items():
        dry = stamp["observed_shifts_px"]["dry"]
        fits[side] = np.polyfit(list(dry), list(dry.values()), 1)
        diagnostics[side] = {
            "dry_fit_max_residual_px": stamp["dry_fit_max_residual_px"],
            "withheld_marks_minus_dry_px": stamp["lower_minus_dry_prediction_px"],
        }
    return {"method":"three dry front strokes per face", "checks":diagnostics}, fits


def clean_profile(profile, mask):
    y = np.arange(len(profile))
    return gaussian_filter1d(np.interp(y, y[~mask], profile[~mask]), 1.55)


def scoring_profiles(gray, reference, side, ink_fit):
    data = []
    rows = np.arange(gray.shape[0])
    for x, reference_row in SITES[side]:
        ix = x - CROP[0]
        current = gray[:,ix-4:ix+5].mean(1)
        ref_idx = int(np.flatnonzero(reference["x"]==x)[0])
        ink = reference["ink"][ref_idx]
        mask = maximum_filter1d(ink.astype(np.uint8),5).astype(bool)
        displacement = float(np.polyval(ink_fit, reference_row))
        raw_mask = mask[np.clip(np.rint(rows-displacement).astype(int), 0, len(rows)-1)]
        filtered = clean_profile(current, raw_mask)
        baseline = clean_profile(reference["baseline"][ref_idx], mask)
        reference_y = reference_row + OFFSETS
        now = np.rint(reference_y+displacement).astype(int) - CROP[1]
        source = reference_y - CROP[1]
        near = uniform_filter1d(filtered,10)
        far = uniform_filter1d(filtered,19)
        static_near = uniform_filter1d(baseline,10)
        drop = near[now-10] - near[now+10]
        changed_drop = drop - (static_near[source-10]-static_near[source+10])
        deep_drop = near[now-10] - far[now+24]
        score = .60*drop + .26*deep_drop + .62*changed_drop
        covered = uniform_filter1d(ink.astype(float),13)[source] > .23
        score[covered] = -10
        data.append((x, reference_row, displacement, filtered, score))
    return data


def local_crossings(station, offset):
    x, reference_row, displacement, profile, score = station
    nearby = np.flatnonzero(abs(OFFSETS-offset)<=14)
    k = nearby[np.argmax(score[nearby])]
    if score[k] < 5:
        return None
    seed = round(reference_row+OFFSETS[k]+displacement-CROP[1])
    bright = np.median(profile[seed-18:seed-7])
    dark = np.median(profile[seed+7:seed+19])
    if bright-dark < 6:
        return None
    bounds = np.arange(seed-11, seed+12)
    values = []
    for fraction in (.30,.50,.70):
        threshold = dark+fraction*(bright-dark)
        crossings = bounds[(profile[bounds]>=threshold) & (profile[bounds+1]<threshold)]
        if not len(crossings):
            return None
        i = crossings[np.argmin(abs(crossings-seed))]
        subpixel = i+(profile[i]-threshold)/(profile[i]-profile[i+1])
        values.append(float(subpixel+CROP[1]))
    return (x, values, float(bright-dark))


def fit_side(gray, reference, metadata, side, ink_fit):
    data = scoring_profiles(gray,reference,side,ink_fit)
    curves = np.stack([s[-1]/max(12.,np.percentile(s[-1],98)) for s in data])
    pooled = np.maximum.reduce([np.roll(curves,j,axis=1) for j in (-3,0,3)])
    offset = OFFSETS[np.argmax(np.median(pooled,axis=0))]
    stations = [v for station in data if (v:=local_crossings(station,offset)) is not None]
    if len(stations) < 4:
        raise ValueError(f"Insufficient contrast on the {side} contact")
    x0 = STATIONS[side][0]
    x = np.array([v[0] for v in stations])
    centered_x = x-x0
    levels = np.array([v[1] for v in stations])
    fit = np.polyfit(centered_x,levels[:,1],1)
    keep = np.ones(len(stations),dtype=bool)
    for _ in range(4):
        residual = levels[:,1] - np.polyval(fit,centered_x)
        error = abs(residual-np.median(residual))
        selected = error <= max(1.9,3.6*np.median(error))
        if selected.sum() < 3:
            break
        keep = selected
        fit = np.polyfit(centered_x[keep],levels[keep,1],1)
    raw = [float(np.polyfit(centered_x[keep],levels[keep,j],1)[1]) for j in range(3)]
    registered = [float(y-np.polyval(ink_fit,y)) for y in raw]
    marks = np.array(metadata["graduations_row_cups_column_sd_px"][side])
    volume = float(np.interp(registered[1],marks[:,0],marks[:,1]))*CUP_ML
    residual = levels[:,1]-np.polyval(fit,centered_x)
    return {
        "x":x0, "raw_row":raw[1], "row":registered[1], "print_dy":raw[1]-registered[1],
        "rows_at_brightness_fractions":registered, "nominal_ml":volume,
        "patches":int(keep.sum()), "span_x":[int(x[keep].min()),int(x[keep].max())],
        "interpolates_fixed_x":bool(x[keep].min()<=x0<=x[keep].max()),
        "median_patch_residual_px":float(np.median(abs(residual[keep]))),
        "samples":[{"x":xx,"raw_row":yy[1],"contrast":ct,"accepted":bool(ok)}
                   for (xx,yy,ct),ok in zip(stations,keep)]
    }


def read_image(path, reference, metadata, color=None):
    source = path/"average.png" if path.is_dir() else path
    if color is None and path.is_dir():
        color = path/"color.png"
    gray = np.asarray(crop_frame(source).convert("L"))
    registration, fits = ink_state(color)
    return {"registration":registration, "sightlines":{
        side:fit_side(gray,reference,metadata,side,fits[side]) for side in SITES
    }}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=["calibrate","crop","read"])
    parser.add_argument("image",type=Path)
    parser.add_argument("output",nargs="?",type=Path)
    parser.add_argument("--reference",type=Path,default=HERE/"registration.npz")
    parser.add_argument("--color",type=Path,help="full color sample or packed front-ink tiles")
    args=parser.parse_args()
    source = args.image/"average.png" if args.image.is_dir() else args.image
    color = args.color or (args.image/"color.png" if args.image.is_dir() else None)
    if args.action=="calibrate":
        if color is None:parser.error("calibration needs the focused color sample")
        make_reference(source,color,args.reference)
        return
    if args.action=="crop":
        if args.output is None:parser.error("crop requires an output path")
        crop_frame(source).convert("L").save(args.output,compress_level=6)
        return
    metadata=json.loads(args.reference.with_suffix(".json").read_text())
    with np.load(args.reference) as saved:
        result=read_image(source,dict(saved),metadata,color)
    encoded=json.dumps(result,indent=2)+"\n"
    if args.output:args.output.write_text(encoded)
    else:print(encoded,end="")


if __name__=="__main__":
    main()
