"Render the install guide's focused, customer-facing CAD pictures.\n\nThe production models carry more geometry than an instruction frame needs. This module keeps the\nexact touched parts and makes four deliberate presentation cuts:\n\n- the faucet's source lever is a union of rest + pressed states for collision checking, so the\n  customer views reconstruct one physical state at a time from the same dimensions;\n- invisible tube tails are clipped at the countertop for the user-side faucet views;\n- the mount sequence keeps the recognizable full faucet for the lowering event, then changes once\n  to a fixed, literal below-counter camera for the plate and retained-nut actions;\n- the retained donor washer and nut are plain visual stand-ins because the purchased hardware has\n  no source CAD. Their family installation geometry is shown without using them as dimensional\n  authority.\n\nThe scene payload intermediates live in a temporary directory under ``hardware/``.\nOnly the final PNGs land in ``art/``.\n\n``--mount-studies`` renders only the registered mount frames into ``out/mount-studies/`` for fast\nvisual review without touching the checked-in artwork."
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def _load_faucet_module(*args, **kwargs):
    return _compiled('_cad_art',path=('_load_faucet_module',),args=args,kwargs=kwargs)

def machine_bodies(*args, **kwargs):
    "The appliance's bodies whose top-level name `keep` takes, as its payload draws them.\n\nThe appliance is cut on the mesh kernel, so it has no solids a scene here can hold. Its\npayload is the form every scene can carry: these meshes, fluted skin and all, ride beside\nthe solids a scene builds (`borrow`, `_export_colored`)."
    return _compiled('_cad_art',path=('machine_bodies',),args=args,kwargs=kwargs)

def borrow(*args, **kwargs):
    "Stand the appliance's `bodies` in `assembly`'s scene."
    return _compiled('_cad_art',path=('borrow',),args=args,kwargs=kwargs)

def _export_colored(*args, **kwargs):
    "`assembly` as a STEP at `target`, with its payload beside it when `mesh` asks.\n\nA scene that borrowed the appliance's bodies is written whole from its meshes: the solids\nbuilt here tessellated, the appliance's own triangles beside them, the STEP as their\ntriangulated surface sets and the payload as what the page draws."
    return _compiled('_cad_art',path=('_export_colored',),args=args,kwargs=kwargs)

def _clip_z(*args, **kwargs):
    return _compiled('_cad_art',path=('_clip_z',),args=args,kwargs=kwargs)

def _moved(*args, **kwargs):
    return _compiled('_cad_art',path=('_moved',),args=args,kwargs=kwargs)

def _children_by_name(*args, **kwargs):
    return _compiled('_cad_art',path=('_children_by_name',),args=args,kwargs=kwargs)

def _add_child(*args, **kwargs):
    return _compiled('_cad_art',path=('_add_child',),args=args,kwargs=kwargs)

def _physical_levers(*args, **kwargs):
    'Return the source-dimensioned physical rest and pressed levers separately.'
    return _compiled('_cad_art',path=('_physical_levers',),args=args,kwargs=kwargs)

def _build_steps(*args, **kwargs):
    return _compiled('_cad_art',path=('_build_steps',),args=args,kwargs=kwargs)

def _build_connection_steps(*args, **kwargs):
    'Build the rear face and two connection states as literal CAD scenes.\n\nThe appliance exterior and every connection station come from the current enclosure payload\nand its generated facts.  All six tube collars are production solids, including their recessed\nlettering.  Only the field-cut tube lengths, the flat SIG-6 ribbon, and its\nmodular plug are constructed here because those flexible customer-routed bodies have no single\ninstalled pose in the product assembly.'
    return _compiled('_cad_art',path=('_build_connection_steps',),args=args,kwargs=kwargs)

def _job(*args, **kwargs):
    return _compiled('_cad_art',path=('_job',),args=args,kwargs=kwargs)

def _canonicalize_png(*args, **kwargs):
    'Write one byte-stable PNG, without host or wall-clock metadata.'
    return _compiled('_cad_art',path=('_canonicalize_png',),args=args,kwargs=kwargs)

def _crop(*args, **kwargs):
    return _compiled('_cad_art',path=('_crop',),args=args,kwargs=kwargs)

def _clear_connected_background(*args, **kwargs):
    'Remove only the white field connected to the picture edge.\n\nThe posed renderer deliberately emits an opaque page.  Instruction layouts need the CAD\nobject, not that rectangular page, but a global ``-transparent white`` would also erase real\nwhite parts such as the TAP collar.  Flood-filling alpha from a one-pixel white border clears\nonly the connected background and leaves enclosed highlights and labels intact.'
    return _compiled('_cad_art',path=('_clear_connected_background',),args=args,kwargs=kwargs)

def _shave_render_frame(*args, **kwargs):
    'Remove the frame anchors and their deliberately generous vertical review margin.'
    return _compiled('_cad_art',path=('_shave_render_frame',),args=args,kwargs=kwargs)

def _shave_under_render_frame(*args, **kwargs):
    'Remove only the four wide-frame anchors, preserving the installer-scale slab.'
    return _compiled('_cad_art',path=('_shave_under_render_frame',),args=args,kwargs=kwargs)

def _crop_registered_connection(*args, **kwargs):
    'Apply the same fixed viewport crop to both rear-connection states.'
    return _compiled('_cad_art',path=('_crop_registered_connection',),args=args,kwargs=kwargs)

def main(*args, **kwargs):
    return _compiled('_cad_art',path=('main',),args=args,kwargs=kwargs)

__all__ = ['annotations', 'importlib', 'json', 'os', 'shutil', 'subprocess', 'sys', 'tempfile', 'Path', 'cq', 'Image', 'HERE', 'HARDWARE', 'ROOT', 'ART', 'OUT', 'FAUCET_SOURCE', 'MACHINE_STEP', 'MACHINE_MESH', 'MACHINE_FACTS', 'TUBE_COLLAR_DIR', 'MOUNT_CAM', 'MOUNT_TARGET', 'MOUNT_FRAME_SHAVE', 'MOUNT_FRAME_TRIM_TOP', 'MOUNT_DROP_TRIM_TOP', 'MOUNT_FRAME_TRIM_BOTTOM', 'UNDER_MOUNT_CAM', 'UNDER_MOUNT_TARGET', 'UNDER_MOUNT_FRAME_SHAVE', 'PLATE_APPROACH_X', 'UNDER_COUNTERTOP_X', 'UNDER_COUNTERTOP_Y', 'CONNECT_CAM', 'CONNECT_TARGET', 'CONNECT_ORTHO_SPAN', 'CONNECT_RENDER_SIZE', 'CONNECT_OPEN_GAP', 'CONNECT_CROP', 'note_read', 'note_write', 'machine_bodies', 'borrow', 'main']
_bind('_cad_art',globals())

if __name__ == '__main__':
    _compiled('_cad_art','main')
