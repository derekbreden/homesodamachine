"""Producer surfaces and authored illustration props for the customer pictures."""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import _mesh_payload
import _rust_part
from _occt_color import rgba
from _install_art_mesh import _read


def _select(meshes, keep=lambda name: True, *, move=None, colors=None, rename=None):
    out = []
    for original in meshes:
        name = original["name"].split("/")[0]
        if not keep(name):
            continue
        mesh = dict(original)
        if move is not None:
            mesh["pos"] = (np.asarray(mesh["pos"]).reshape(-1, 3) + move).ravel()
        if colors and name in colors:
            mesh["color"] = colors[name]
        if rename and name in rename:
            mesh["name"] = rename[name] + original["name"][len(name):]
        out.append(mesh)
    return out


def _color(*values):
    return list(rgba((*values, 1.0), {})[:3])


def _props(numbers, colors, work):
    path = work / "cad-art.numbers.json"
    path.write_text(json.dumps({"cad_art": numbers, "colors": colors}, sort_keys=True) + "\n")
    _rust_part.run("tooling", "install-art-props", path, work)


def _write(work, name, meshes):
    step = work / f"{name}.step"
    _mesh_payload.write(meshes, Path(f"{step}.mesh"))
    return step


def _anchors(camera, target, across, rise):
    def unit(v):
        length = math.sqrt(sum(x * x for x in v))
        return [x / length for x in v]
    def cross(a, b):
        return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
    view = unit(camera)
    right = unit(cross(view, (0., 0., 1.)))
    up = unit(cross(right, view))
    return [[target[k] + a*across*right[k] + b*rise*up[k] for k in range(3)]
            for a, b in ((-1., -1.), (-1., 1.), (1., -1.), (1., 1.))]


def build_steps(art, work):
    """The existing faucet and mount states, without rebuilding the faucet."""
    fa = art._load_faucet_module()
    source = _read(art.HARDWARE / "faucet-layout/faucet-assembly.step.mesh")
    above = {"westbrass", "drain_tube", "soda_faucet_tube", "tpu_o_ring",
             "flavor_tube_pos_x", "flavor_tube_neg_x", "lever", "above_counter_plate",
             "above_counter_gasket", "shell_base", "shell_tip", "faucet-display-cover-seated",
             "faucet_display", "faucet_display_screen"}
    clipped_above = {"westbrass", "drain_tube", "flavor_tube_pos_x", "flavor_tube_neg_x"}
    flavors = {f"{body}_{side}": side for body in ("flavor_tube", "flavor_umbilical_tube")
               for side in ("pos_x", "neg_x")}
    tails = {*flavors, "soda_umbilical_tube", "drain_tube"}
    mounted = above | set(flavors) | {"soda_umbilical_tube"}
    input_names = tails | clipped_above | {"display_signal_ribbon"}
    _mesh_payload.write(_select(source, input_names.__contains__), work / "faucet-crops.mesh")
    inherited = {m["name"].split("/")[0]: m["color"] for m in source}
    colors = {"lever": inherited["lever"], "counter": _color(.55, .55, .58),
              "plate": _color(.91, .92, .94), "washer": _color(.82, .83, .84),
              "nut": _color(.43, .45, .48), "flavor_a": _color(.025, .027, .031),
              "flavor_b": _color(.20, .205, .215), "signal": _color(.035, .038, .043),
              "stripe": _color(.16, .17, .19), "anchor": _color(.95, .04, .82)}
    flavor_colors = {name: colors["flavor_a" if side == "pos_x" else "flavor_b"]
                     for name, side in flavors.items()}
    captive = -fa.shank_length + 5. + 1.5
    final = fa.countertop_bottom_z - fa.under_counter_plate_thickness
    scenes = [
        {"name": "faucet-user", "kind": "user", "pressed": False},
        {"name": "faucet-user-pressed", "kind": "user", "pressed": True},
        {"name": "faucet-full", "kind": "full"},
        {"name": "mount-drop", "kind": "mount", "lift": 35., "washer": captive+35.},
        *[{"name": name, "kind": "mount", "lift": 0., "washer": captive}
          for name in ("mount-seated", "mount-lowered-clean")],
        *[{"name": name, "kind": "mount", "lift": 0., "washer": captive,
           "plate": art.PLATE_APPROACH_X} for name in ("mount-slide", "mount-slide-clean")],
        *[{"name": name, "kind": "mount", "lift": 0., "washer": final, "plate": 0.}
          for name in ("mount-tighten", "mount-final-clean")],
        {"name": "mount-under-slide-clean", "kind": "under", "washer": captive,
         "plate": art.PLATE_APPROACH_X},
        {"name": "mount-under-tighten-clean", "kind": "under", "washer": final, "plate": 0.},
    ]
    shell = fa.faucet_shell
    numbers = {"kind": "faucet", "scenes": scenes, "input": str(work / "faucet-crops.mesh"),
               "counter": [fa.countertop_bottom_z, fa.countertop_thickness,
                           fa.countertop_hole_center_y, fa.hole_radius,
                           art.UNDER_COUNTERTOP_X, art.UNDER_COUNTERTOP_Y],
               "top_z": fa.countertop_top_z,
               "lever": [fa.plateau_z, fa.port_center_depth, fa.soda_faucet_tube_r,
                         fa.lever_pivot_y, fa.lever_pivot_z, fa.lever_press_angle_deg],
               "signal_legs": [{kind: list(points)} for kind, *points in fa._step_legs(+1, -123.)],
               "signal_origin": [shell.signal_lower_exit_x, shell.signal_lower_exit_y,
                                 fa.under_counter_plate_bottom_z],
               "signal_size": [shell.signal_ribbon_max_width, shell.signal_ribbon_max_depth],
               "frame": _anchors(art.MOUNT_CAM, art.MOUNT_TARGET, 118., 235.),
               "under_frame": _anchors(art.UNDER_MOUNT_CAM, art.UNDER_MOUNT_TARGET, 137., 58.)}
    _props(numbers, colors, work)
    out = {}
    for row in scenes:
        name, kind = row["name"], row["kind"]
        meshes = _read(work / f"{name}.props.mesh")
        if kind == "full":
            meshes += source
        elif kind == "user":
            meshes += _select(source, lambda body: body in above-clipped_above-{"lever"})
        elif kind == "mount":
            meshes += _select(source, lambda body: body in mounted-tails-{"lever"},
                              move=(0., 0., row["lift"]), colors=flavor_colors)
        if "plate" in row:
            plate_name = ("under-open-plate" if row["plate"] else "under-seated-plate") if kind == "under" else "under_counter_plate"
            meshes += _select(source, lambda body: body == "under_counter_plate",
                              move=(row["plate"], 0., 0.), colors={"under_counter_plate": colors["plate"]},
                              rename={"under_counter_plate": plate_name})
        out[name] = _write(work, name, meshes)
    return out


def build_connection_steps(art, work):
    """The same rear face, six leads and SIG-6 plug in the two registered poses."""
    facts = json.loads(art.MACHINE_FACTS.read_text())
    keep = {"c14-inlet", "keystone-jack", "co2-inlet", "bulkhead-water", "bulkhead-flavor-a",
            "bulkhead-flavor-b", "bulkhead-carb", "bulkhead-drain", "funnel", "nameplate",
            "nameplate-ink", "enclosure-back-bottom", "enclosure-back-top"}
    rear = _select(_read(art.MACHINE_MESH), lambda name: name in keep or name.startswith("bulkhead-ring-"))
    missing = keep - {entry["name"].split("/")[0] for entry in rear}
    if missing:
        raise RuntimeError(f"{art.MACHINE_MESH.name} has no {sorted(missing)} for the rear scene")
    keys = {"tap": ("bulkhead-water", "outboard"), "carb": ("bulkhead-carb", "tube-out"),
            "co2": ("gas-regulator", "outboard"), "flavor-a": ("bulkhead-flavor-a", "tube-out"),
            "flavor-b": ("bulkhead-flavor-b", "tube-out"), "drain": ("bulkhead-drain", "outboard")}
    pack = {"tap": (-60., 322.), "co2": (-40., 322.), "carb": (-50., 312.),
            "flavor-a": (-40., 302.), "flavor-b": (-60., 302.), "drain": (-50., 292.)}
    fluids = {"tap": "water", "carb": "carb", "co2": "co2", "flavor-a": "flavor",
              "flavor-b": "flavor", "drain": "drain"}
    colors = {"tap": _color(.82, .84, .87), "drain": _color(.82, .84, .87),
              "carb": _color(.035, .31, .82), "co2": _color(.67, .042, .042),
              "flavor-a": _color(.025, .027, .031), "flavor-b": _color(.115, .12, .13),
              "signal": _color(.035, .038, .043), "stripe": _color(.16, .17, .19),
              "plug": _color(.72, .74, .78), "latch": _color(.86, .87, .89),
              "gold": _color(.73, .49, .14)}
    tubes, collars = [], []
    for which, (body, port) in keys.items():
        station = facts["card_ports"][body][port]
        x, y, z = station["pos"]; px, pz = pack[which]
        tubes.append({"name": which, "diameter": station["diam"], "points": [
            [x, y, z], [x, 560., z], [x, 578., z], [(2*x+px)/3., 598., (2*z+pz)/3.],
            [px, 626., pz], [px, 940., pz]]})
        station_name = "water" if which == "tap" else which
        original = f"tube-collar-{station_name}"
        fluid = fluids[which]
        collar_colors = {original: _color(*(c/255. for c in art._rear.chip_color(fluid))),
                         original+"-word": _color(*(c/255. for c in art._rear.word_color(fluid)))}
        collars += _select(_read(art.TUBE_COLLAR_DIR / f"{original}.step.mesh"),
                           move=(x, y+47.5, z), colors=collar_colors,
                           rename={original: f"wall-end-collar-{which}",
                                   original+"-word": f"wall-end-collar-{which}-word"})
    jack_x, station_z = facts["constants"]["KEYSTONE_STATION"]
    jack_z = station_z-1.; y0 = facts["bodies"]["keystone-jack"][4]-6.2
    numbers = {"kind": "rear", "tubes": tubes, "plug": [jack_x, y0, jack_z],
               "ribbon_points": [[jack_x, y0+26.5, jack_z], [jack_x, 548., jack_z],
                                 [-42., 590., 298.], [-48.5, 626., 294.], [-48.5, 940., 294.]]}
    _props(numbers, colors, work)
    leads = _read(work / "rear-leads.props.mesh") + collars
    return {"the-back-face": _write(work, "the-back-face", rear),
            **{name: _write(work, name, rear+_select(leads, move=(0., y, 0.)))
               for name, y in (("connect-rear-open", art.CONNECT_OPEN_GAP),
                               ("connect-rear-connected", 0.))}}
