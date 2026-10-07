"""Guarded, owner-scoped roof finishing pockets for held wire tools.

This fallback makes a simple pocket around a complete held cutter member.
It is intended only after the ordinary subtraction guard fails. Every tool
and component stays unchanged. The complete protected print hosts and stock
coupons must remain outside the new pocket. No tool clipping is performed.
"""
import cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.TopTools import TopTools_ListOfShape

from .received_native import full_material_coverage


def _bounds(shape):
    b = shape.BoundingBox()
    return [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax]


def _volume(shape):
    return sum(abs(s.Volume(tol=1e-9)) for s in shape.Solids())


def _valid(shape, label, require_material=True):
    solids = shape.Solids()
    if (not shape.isValid() or any(not s.isValid() for s in solids)
            or (require_material and not solids)):
        raise ValueError('Invalid complete native material: ' + label)
    return shape


def _one_common(first, second, tolerance):
    operation = BRepAlgoAPI_Common()
    arguments, tools = TopTools_ListOfShape(), TopTools_ListOfShape()
    arguments.Append(first.copy(mesh=False).wrapped)
    tools.Append(second.copy(mesh=False).wrapped)
    operation.SetArguments(arguments)
    operation.SetTools(tools)
    operation.SetNonDestructive(True)
    operation.SetRunParallel(False)
    operation.SetFuzzyValue(tolerance)
    operation.Build()
    if not operation.IsDone():
        raise ValueError('Native roof material Common did not complete')
    native = operation.Shape()
    if native.IsNull():
        return [], {'completed': True, 'empty': True, 'solid_count': 0,
                    'volume_mm3': 0.}
    shape = cq.Shape.cast(native)
    _valid(shape, 'roof material Common', require_material=False)
    solids = shape.Solids()
    return solids, {'completed': True, 'empty': not solids,
                    'solid_count': len(solids), 'volume_mm3': _volume(shape)}


def _common_material(left, right, tolerance):
    pieces, witnesses = [], []
    for first_index, first in enumerate(left.Solids()):
        for second_index, second in enumerate(right.Solids()):
            a, b = _bounds(first), _bounds(second)
            separated = any(a[i + 3] < b[i] or b[i + 3] < a[i]
                            for i in range(3))
            if separated:
                witnesses.append({'solid_indices': [first_index, second_index],
                                  'native_bounds_separated': True,
                                  'volume_mm3': 0.})
                continue
            solids, witness = _one_common(first, second, tolerance)
            if witness['volume_mm3'] > min(_volume(first), _volume(second)) + .001:
                raise ValueError('Roof Common exceeds complete operand material')
            pieces.extend(solids)
            witnesses.append({'solid_indices': [first_index, second_index],
                              **witness})
    result = cq.Compound.makeCompound(pieces)
    return result, {'tolerance_mm': tolerance,
                    'common_volume_mm3': sum(r['volume_mm3'] for r in witnesses),
                    'per_solid_commons': witnesses}


def _coverage(first, second, label):
    witness = full_material_coverage(first, second)
    if not witness['pass']:
        raise ValueError('Incomplete roof material witness ' + label + ': ' + str(witness))
    return witness


def make_roof_finish(stock, held_member, protected_shapes, *, additional_air_mm=.02):
    """Return ``(retained_stock, finishing_tool, certificate)``.

    ``protected_shapes`` maps every complete printed host and bearing/pilot/
    bridge coupon to its received native shape. The caller owns its read-time
    native/source bindings and exports the explicit enclosure-back-top tool.
    A failure refuses the correction rather than cropping the tool or stock.
    """
    _valid(stock, 'complete source stock')
    _valid(held_member, 'unchanged held cutter member')
    if len(stock.Solids()) != 1 or len(held_member.Solids()) != 1:
        raise ValueError('Roof finish requires one complete stock and cutter solid')
    if additional_air_mm != .02:
        raise ValueError('The supported roof finishing air is exactly0.02mm')
    if not protected_shapes:
        raise ValueError('Complete protected roof hosts/coupons are required')
    b = held_member.BoundingBox()
    a = additional_air_mm
    tool = cq.Solid.makeBox(b.xlen + 2*a, b.ylen + 2*a, b.zlen + 2*a,
                            cq.Vector(b.xmin-a, b.ymin-a, b.zmin-a))
    _valid(tool, 'whole finishing pocket')
    box = _bounds(tool)
    # Fixed product bounds:215mm width,355mm roof,471.3mm outer rear.
    # No below-cap interface or stock outside the upper bay may be altered.
    skin = {'west': box[0] + 107.5, 'east': 107.5 - box[3],
            'roof': 355. - box[5], 'rear': 471.3 - box[4]}
    if min(skin.values()) < 3. or box[1] < 200. or box[2] < 253.4:
        raise ValueError('Whole roof pocket crosses fixed bay or minimum3mm exterior stock')
    tool_coverage = _coverage(held_member, tool, 'complete original tool in finish')
    protection = []
    for name, shape in sorted(protected_shapes.items()):
        _valid(shape, 'protected stock ' + name)
        material, witness = _common_material(shape, tool, 0.)
        amount = _volume(material)
        row = {'part': name, 'received_bounds_mm': _bounds(shape),
               'finishing_pocket_common_mm3': amount,
               'complete_native_witness': witness, 'pass': amount < .001}
        protection.append(row)
        if not row['pass']:
            raise ValueError('Roof finishing pocket removes complete protected stock ' + name)
    attempts = []
    for tolerance in [0., .0001, .00001]:
        try:
            removed, removed_witness = _common_material(stock, tool, tolerance)
            retained = stock.copy(mesh=False).cut(tool.copy(mesh=False), tol=tolerance)
            _valid(retained, 'whole retained stock')
            if len(retained.Solids()) != 1:
                raise ValueError('Roof pocket disconnects complete source stock')
            retained_in_source = _coverage(retained, stock, 'all retained stock in source')
            source_volume, retained_volume = _volume(stock), _volume(retained)
            removed_volume = _volume(removed)
            conservation_error = abs(source_volume-retained_volume-removed_volume)
            if conservation_error >= .001:
                raise ValueError('Roof cut loses material outside its complete pocket')
            original_residue, original_witness = _common_material(retained, held_member, tolerance)
            pocket_residue, pocket_witness = _common_material(retained, tool, tolerance)
            if max(_volume(original_residue), _volume(pocket_residue)) >= .001:
                raise ValueError('Complete original tool or finishing pocket remains in stock')
            removal_checks = {}
            if removed.Solids():
                removal_checks['removed_material_in_source'] = _coverage(removed, stock, 'removed stock in source')
                removal_checks['removed_material_in_finish'] = _coverage(removed, tool, 'removed stock in exact pocket')
                complement = stock.copy(mesh=False).cut(retained.copy(mesh=False), tol=tolerance)
                _valid(complement, 'independent source minus retained')
                removal_checks['complement_in_removed'] = _coverage(complement, removed, 'independent removal in source-pocket Common')
                removal_checks['removed_in_complement'] = _coverage(removed, complement, 'source-pocket Common in independent removal')
            row = {'tolerance_mm': tolerance, 'pass': True,
                   'source_volume_mm3': source_volume,
                   'retained_volume_mm3': retained_volume,
                   'removed_volume_mm3': removed_volume,
                   'material_conservation_error_mm3': conservation_error,
                   'source_pocket_complete_common': removed_witness,
                   'retained_material_in_source': retained_in_source,
                   'original_tool_exclusion': original_witness,
                   'finishing_pocket_exclusion': pocket_witness,
                   **removal_checks}
            attempts.append(row)
            return retained, tool, {
                'pass': True, 'print_owner': 'enclosure-back-top',
                'additional_air_mm': a, 'held_member_bounds_mm': _bounds(held_member),
                'finishing_tool_bounds_mm': box, 'minimum_exterior_stock_mm': skin,
                'original_full_tool_containment': tool_coverage,
                'complete_protected_stock': protection, 'native_attempts': attempts,
                'scope': 'Whole unchanged held cutter member receives an explicit simple pocket with0.02mm additional air. Independent valid per-solid Commons establish complete tool containment, protected stock preservation, retained-in-source material, exact removed material and final original-tool exclusion. No invalid result is accepted and no tool or stock is clipped.'}
        except (ValueError, RuntimeError) as error:
            attempts.append({'tolerance_mm': tolerance, 'pass': False, 'error': str(error)})
    raise ValueError('Cannot certify complete roof finishing subtraction: ' + str(attempts))
