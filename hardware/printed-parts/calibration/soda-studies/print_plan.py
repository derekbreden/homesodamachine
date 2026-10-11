"""Compose The Pour's explicit native print objects and material plate plan.

The geometry emitter supplies bed-normalized meshes, source-derived recipe
bands and manufacturing-frame review windows. This module adds no assembly
rotation, printer action or repository check. The completed faucet plan is an
input, so its four reviewed projects can retain their source recipes and layout.
"""
from __future__ import annotations

from copy import deepcopy


IDENTITY = [[1., 0., 0., 0.], [0., 1., 0., 0.],
            [0., 0., 1., 0.], [0., 0., 0., 1.]]
QUADRANTS = ("front-bottom", "front-top", "back-bottom", "back-top")


def native_object(part, *, cohort="rigid", object_id=None,
                  object_overrides=None, layer_ranges=(), modifiers=(),
                  native_review=None, volumes=None):
    """Declare one parent in its supplied manufacturing frame.

    Registered colour volumes and captive moving bodies must be supplied as
    named volumes in this same frame. Their transforms preserve the supplied
    relative positions; no individual body's minimum Z is changed.
    """
    frame = part.get("manufacturing_frame")
    if not frame or not frame.get("id"):
        raise ValueError(f"{part['id']}: an explicit manufacturing frame is required")
    if volumes is None:
        volumes = [dict(id=part["id"], part_id=part["id"],
                        transform_mm=deepcopy(IDENTITY), filament_slot=1)]
    return dict(id=object_id or part["id"], name=part["name"], cohort=cohort,
                manufacturing_frame=deepcopy(frame), volumes=deepcopy(list(volumes)),
                object_overrides=deepcopy(object_overrides or {}),
                layer_ranges=deepcopy(list(layer_ranges)),
                modifiers=deepcopy(list(modifiers)),
                native_review=deepcopy(native_review or {}))


def cabinet_object(part, *, quadrant, source_recipe, captive_parts=(),
                   support_blockers=(), native_review=None):
    """Declare a quadrant and optional captive bodies with one native schedule.

    source_recipe contains explicit object_overrides, layer_ranges and modifiers
    derived from the source preparation's datums and exact piece masks. Exterior
    paint is a per-volume mask; support blockers cover only supplied motion air.
    The body's automatic supports remain available for functional ceilings.
    """
    if quadrant not in QUADRANTS:
        raise ValueError(f"Unknown source quadrant: {quadrant}")
    volumes = [dict(id=part["id"], part_id=part["id"],
                    transform_mm=deepcopy(IDENTITY), filament_slot=1)]
    if source_recipe.get("support_paint"):
        volumes[0]["support_paint"] = deepcopy(source_recipe["support_paint"])
    for member in captive_parts:
        volumes.append(dict(id=member["id"], part_id=member["id"],
                            transform_mm=deepcopy(member.get("print_transform_mm", IDENTITY)),
                            filament_slot=1,
                            native_review=deepcopy(member.get("native_review", {}))))
    recipe_modifiers = [*source_recipe.get("modifiers", []), *support_blockers]
    obj = native_object(part, object_overrides=source_recipe["object_overrides"],
                        layer_ranges=source_recipe.get("layer_ranges", []),
                        modifiers=recipe_modifiers, volumes=volumes,
                        native_review=native_review or source_recipe.get("native_review", {}))
    obj["source_quadrant"] = quadrant
    obj["recipe_sources"] = deepcopy(source_recipe.get("sources", []))
    return obj


def source_z_band(band, manufacturing_frame):
    """Map an actual source Z interval into an axial +Z/-Z print frame.

    Oblique source bands require their own measured manufacturing endpoints;
    this helper does not turn an oblique band into an axis-aligned envelope.
    """
    matrix = manufacturing_frame["from_source_matrix_mm"]
    axis = matrix[2]
    if abs(axis[0]) > 1e-8 or abs(axis[1]) > 1e-8 or abs(abs(axis[2])-1.) > 1e-8:
        raise ValueError("A source-Z band needs an axial manufacturing frame")
    endpoints = [axis[2]*float(band[key])+axis[3]
                 for key in ("min_z_mm", "max_z_mm")]
    return {**deepcopy(band), "min_z_mm": min(endpoints), "max_z_mm": max(endpoints)}


def registered_volumes(part):
    """Return exact named material volumes without nozzle-registration shifts."""
    result = []
    for value in part["material_volumes"]:
        result.append({**deepcopy(value), "part_id": part["id"],
                       "transform_mm": deepcopy(value.get("transform_mm", IDENTITY))})
    return result


def bind_faucet_plan(faucet_plan, parts):
    """Bind the reviewed faucet recipes to the emitter's explicit source assets.

    Root part IDs are retained. A physical collar still has its registered body
    and letters as separate volumes. Display assembly matrices never enter this
    binding. Frozen source hash checks belong to the requested native preparation.
    """
    by_id = {part["id"]: part for part in parts}
    objects = deepcopy(faucet_plan["print_objects"])
    for obj in objects:
        physical_ids = {volume["part_id"] for volume in obj["volumes"]}
        if len(physical_ids) != 1:
            raise ValueError(f"{obj['id']}: the faucet plan expects one physical source part")
        part = by_id[next(iter(physical_ids))]
        obj["manufacturing_frame"] = deepcopy(part["manufacturing_frame"])
        if len(obj["volumes"]) == 1:
            volume = obj["volumes"][0]
            volume.update(stl=part["stl"], stl_sha256=part["stl_sha256"])
        else:
            assets = {value["id"]: value for value in registered_volumes(part)}
            for volume in obj["volumes"]:
                asset = assets[volume["id"]]
                for key in ("stl", "stl_sha256", "transform_mm", "filament_slot"):
                    volume[key] = deepcopy(asset[key])
    return dict(print_objects=objects,
                print_cohorts=deepcopy(faucet_plan["print_cohorts"]),
                print_plates=deepcopy(faucet_plan["print_plates"]))


def build_print_plan(parts, *, faucet_plan, cabinet_objects, small_objects=(),
                     material_sources=(), small_plates=()):
    """Combine a supplied source plan into explicit, editable native plates.

    Each large quadrant owns a plate. Other shared plates are explicit inputs,
    including the isolated uniform support ladder and separate 90A gasket. TPU
    and uniform multi-colour cohorts retain their actual profile/nozzle evidence.
    This function does not guess material, source orientation or plate capacity.
    """
    plan = bind_faucet_plan(faucet_plan, parts)
    cohorts = {row["id"]: row for row in plan["print_cohorts"]}
    for cohort in material_sources:
        if cohort["id"] in cohorts and cohort != cohorts[cohort["id"]]:
            raise ValueError(f"{cohort['id']}: a material cohort needs one explicit recipe")
        cohorts[cohort["id"]] = deepcopy(cohort)
    cabinets = list(cabinet_objects)
    for obj in cabinets:
        quadrant = obj["source_quadrant"]
        plan["print_plates"].append(dict(
            id="cabinet-"+quadrant, cohort=obj["cohort"], object_ids=[obj["id"]],
            filename="the-pour-v3-cabinet-"+quadrant,
            offsets_mm=[[0., 0.]], model_border_mm=20.))
    plan["print_objects"].extend(deepcopy([*cabinets, *small_objects]))
    plan["print_plates"].extend(deepcopy(list(small_plates)))
    plan["print_cohorts"] = list(cohorts.values())
    plan["print_plan_scope"] = (
        "Explicit manufacturing objects and material cohorts for one assembled Service Section. "
        "Native review reads model schedules, bead envelopes, contact air and exact material paths; "
        "physical surface, release, fit, seal, force and lifetime are unmeasured.")
    return plan
