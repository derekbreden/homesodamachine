"""The built machine as one file, for whoever asks about it next.

`enclosure_assembly.py` stands every body of the appliance where it goes and runs its checks
on them. What it has built then is a list of meshes in world coordinates, each with a name, a
colour and the face records the kernel kept. `write` puts that list in one model file
(`write.write_model`'s layout, so the vertices are float64 and nothing is re-cut), with a JSON
document beside it for what the bodies alone do not say: the tube runs and where each one goes.

`load` reads it back as mesh solids a study can cut, measure and select faces on, in a second,
where building the machine again takes minutes:

    from meshcad import scene
    bodies = scene.load("hardware/manifold-layout/enclosure-assembly.scene.npz")
    back_top, rgb = bodies["enclosure-back-top"]

`hardware/scripts/_machine.py` reads the machine's own document back with it: its runs, ports
and box as the build's own objects.
"""

import itertools
import json

import numpy as np

from .write import model_items, text_array, write_npz


def write(bodies, path, document=None, *, preserve_partitions=False):
    """`bodies` is [(name, shape, linear rgb or None)], every shape standing where it stands.
    A body of several solids keeps one entry per solid under the same name.
    `preserve_partitions` keeps distinct native faces in separate record slots,
    including faces whose surface records are equal."""
    from .write import _solids
    solids, names, colors = [], [], []
    for name, shape, rgb in bodies:
        for s in _solids(shape):
            solids.append(s)
            names.append(name)
            colors.append(rgb)
    items = model_items(solids, names, colors, preserve_partitions=preserve_partitions)
    if document is not None:
        text = json.dumps(document, separators=(",", ":"), sort_keys=True)
        items = itertools.chain(items, [("document", text_array(text))])
    with open(path, "wb") as f:
        write_npz(f, items)


def load(path, *, snap=True, presentation=False, indices=None):
    """{name: (shape, linear rgb or None)}, in the order they were written. A name written
    for several solids comes back as one compound of them. `snap=False` retains the exact f64
    coordinates of an already placed model. `presentation=True` also carries its
    explicitly bound display surfaces through placement and export. `indices`
    selects archive entries in their source order without reading other geometry."""
    from .imports import load_model
    from .solids import MeshCompound
    from .write import model_identity
    if presentation and snap:
        raise ValueError("a paired presentation requires snap=False")
    selected = None if indices is None else set(indices)
    solids = load_model(path, snap=snap, indices=selected)
    if presentation:
        from .presentation import surfaces
        shown = surfaces(path)
        if shown is not None:
            if selected is not None:
                shown = [surface for i, surface in enumerate(shown) if i in selected]
            for solid, surface in zip(solids, shown, strict=True):
                solid._presentation = surface
    out = {}
    identity = model_identity(path)
    if selected is not None:
        identity = [row for i, row in enumerate(identity) if i in selected]
    for s, (name, rgb) in zip(solids, identity):
        out.setdefault(name, ([], rgb))[0].append(s)
    return {name: (ss[0] if len(ss) == 1 else MeshCompound(ss), rgb) for name, (ss, rgb) in out.items()}


def document(path):
    """The JSON document written beside the bodies, or None."""
    with np.load(path, allow_pickle=False) as z:
        return json.loads(bytes(z["document"]).decode()) if "document" in z.files else None
