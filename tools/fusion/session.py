"""The enclosure assembly, in Fusion, as something to look at from any side.

This module runs INSIDE FUSION — its Python, not `tools/cad-venv`. Fusion's MCP server takes a
script as text and calls a `run(_context)` in it, so a caller sends this file's source with an
entry point appended:

    src = Path("tools/fusion/session.py").read_text()
    send(src + "\\n\\ndef run(_context):\\n    sync()\\n    look('iso-top-right')\\n")

WHAT IS HERE IS A VIEWER AND NOT A SOURCE. `manifold-layout/enclosure_assembly.py` places every
one of these bodies and `_scorecard.py` grades the placement — `clearance-floor` walks every body
pair at exact solid distance, `lines-clear` every routed tube, `port-leads` every port. This
module shows. It does not measure.

A pose taken here is a proposal. It goes back as numbers in the layout, and the gates decide.

Distances are mm, because the layout is mm. Fusion's API is cm and every crossing is in `_cm`.
"""

import json
import math
from fnmatch import fnmatchcase

import adsk.core
import adsk.fusion

STEP = ("/Users/derekbredensteiner/Developer/homesodamachine"
        "/hardware/manifold-layout/enclosure-assembly.step")

# Where `home` parks an occurrence's as-imported pose. A Fusion attribute rides the document, so
# `collapse` still answers after a save and a reopen.
HOME = "hsm-home"

# The panels that come off before there is anything to see.
SHELL = ("enclosure-front-top", "enclosure-front-bottom",
         "enclosure-back-top", "enclosure-back-bottom",
         "display-cover", "display-gasket")


def _cm(mm):
    return mm / 10.0


def _app():
    return adsk.core.Application.get()


def _design():
    design = adsk.fusion.Design.cast(_app().activeProduct)
    if not design:
        raise RuntimeError("no active design — call sync() first")
    return design


def _top():
    """The single occurrence the STEP import lands under."""
    root = _design().rootComponent
    if root.occurrences.count == 0:
        raise RuntimeError("the design holds no occurrence — call sync() first")
    return root.occurrences.item(0)


def parts():
    """Every top-level occurrence, in browser order."""
    top = _top()
    return [top.childOccurrences.item(i) for i in range(top.childOccurrences.count)]


def _pose(occ):
    """An occurrence's transform, through whichever accessor this Fusion exposes."""
    return getattr(occ, "transform2", None) or occ.transform


def _repose(occ, matrix):
    if hasattr(occ, "transform2"):
        occ.transform2 = matrix
    else:
        occ.transform = matrix


def _matrix(array):
    m = adsk.core.Matrix3D.create()
    m.setWithArray(array)
    return m


# --- getting it in ------------------------------------------------------------

def sync(path=STEP):
    """Open the STEP in a fresh direct-modelling document and mark every pose home.

    The document is direct, where `design.snapshots` is not there to ask.

    The import outruns the MCP's reply — ~27 MB and 194 products — so the call that sends this
    times out while Fusion finishes anyway. Ask `census()` after, rather than reading the timeout
    as a failure. A modal in front of Fusion stops the API dead, so nothing here can clear one.
    """
    app = _app()
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.DirectDesignType
    manager = app.importManager
    manager.importToTarget(manager.createSTEPImportOptions(path), design.rootComponent)
    home()
    return census()


def census():
    """What arrived, as a dict — enough to tell a finished import from a partial one."""
    design = _design()
    top = _top()
    return {"document": _app().activeDocument.name,
            "components": design.allComponents.count,
            "top": top.name,
            "parts": top.childOccurrences.count,
            "hidden": sum(1 for o in parts() if not o.isLightBulbOn)}


# --- moving it ----------------------------------------------------------------

def home():
    """Park every occurrence's current pose on itself, as the one `collapse` returns to."""
    for occ in parts():
        occ.attributes.add(HOME, "pose", json.dumps(list(_pose(occ).asArray())))


def explode(spread=140.0):
    """Push every part `spread` mm off the centre of the pack, along its own way out."""
    centres = {}
    for occ in parts():
        box = occ.boundingBox
        if box:
            centres[occ.name] = ((box.minPoint.x + box.maxPoint.x) / 2.0,
                                 (box.minPoint.y + box.maxPoint.y) / 2.0,
                                 (box.minPoint.z + box.maxPoint.z) / 2.0)
    if not centres:
        raise RuntimeError("nothing here has a bounding box to push off")
    mid = [sum(c[i] for c in centres.values()) / len(centres) for i in range(3)]

    moved = 0
    for occ in parts():
        centre = centres.get(occ.name)
        parked = occ.attributes.itemByName(HOME, "pose")
        if not centre or not parked:
            continue
        out = [centre[i] - mid[i] for i in range(3)]
        length = math.sqrt(sum(c * c for c in out))
        if length < 1e-6:
            continue
        step = _cm(spread) / length
        matrix = _matrix(json.loads(parked.value))
        shift = matrix.translation
        shift.x += out[0] * step
        shift.y += out[1] * step
        shift.z += out[2] * step
        matrix.translation = shift
        _repose(occ, matrix)
        moved += 1
    return moved


def collapse():
    """Every part back to the pose `home` parked, and every light back on."""
    back = 0
    for occ in parts():
        parked = occ.attributes.itemByName(HOME, "pose")
        if not parked:
            continue
        _repose(occ, _matrix(json.loads(parked.value)))
        occ.isLightBulbOn = True
        back += 1
    return back


# --- choosing what shows ------------------------------------------------------

def _hits(name, patterns):
    bare = name.split(":")[0]
    return any(fnmatchcase(bare, p) if ("*" in p or "?" in p) else p in bare
               for p in patterns)


def only(*patterns):
    """Show the parts a pattern names and hide the rest. `only('valve-*', 'coil-*')`."""
    shown = []
    for occ in parts():
        occ.isLightBulbOn = _hits(occ.name, patterns)
        if occ.isLightBulbOn:
            shown.append(occ.name.split(":")[0])
    return sorted(shown)


def hide(*patterns):
    """Hide the parts a pattern names, leaving everything else as it stands."""
    gone = []
    for occ in parts():
        if _hits(occ.name, patterns):
            occ.isLightBulbOn = False
            gone.append(occ.name.split(":")[0])
    return sorted(gone)


def every():
    """Every light back on, without touching a pose."""
    for occ in parts():
        occ.isLightBulbOn = True


def opened():
    """The shell off."""
    return hide(*SHELL)


# --- pointing the camera ------------------------------------------------------

EYES = {"front": (0, -1, 0), "back": (0, 1, 0), "left": (-1, 0, 0), "right": (1, 0, 0),
        "top": (0, 0, 1), "bottom": (0, 0, -1),
        "iso-top-right": (1, -1, 1), "iso-top-left": (-1, -1, 1),
        "iso-bottom-right": (1, -1, -1), "iso-bottom-left": (-1, -1, -1)}


def look(direction="iso-top-right", margin=1.06):
    """Put the eye on `direction` and fit what is lit.

    Fusion fits to the edge of the geometry, where an exploded pack meets the frame. `margin`
    stands the extents off it.
    """
    if direction not in EYES:
        raise ValueError(f"{direction!r} is not one of {sorted(EYES)}")
    view = _app().activeViewport
    camera = view.camera
    target = camera.target
    span = max(_design().rootComponent.boundingBox.maxPoint.asArray()[i]
               - _design().rootComponent.boundingBox.minPoint.asArray()[i] for i in range(3))
    way = EYES[direction]
    length = math.sqrt(sum(c * c for c in way)) or 1.0
    camera.eye = adsk.core.Point3D.create(*[target.asArray()[i] + way[i] / length * span * 2.0
                                            for i in range(3)])
    camera.upVector = adsk.core.Vector3D.create(0, 0, 1) if direction not in ("top", "bottom") \
        else adsk.core.Vector3D.create(0, 1, 0)
    camera.isFitView = True
    view.camera = camera
    view.fit()
    camera = view.camera
    camera.viewExtents = camera.viewExtents * margin
    view.camera = camera
    view.refresh()
    adsk.doEvents()
    return direction


def shot(path="/tmp/fusion.png", width=1400, height=1000):
    """Write what the viewport shows to a PNG at `path`.

    The viewport writes the file itself, so a shot arrives whether or not anything is proxying
    Fusion's MCP server at the other end.
    """
    if not _app().activeViewport.saveAsImageFile(path, width, height):
        raise RuntimeError(f"the viewport would not write {path}")
    return path
