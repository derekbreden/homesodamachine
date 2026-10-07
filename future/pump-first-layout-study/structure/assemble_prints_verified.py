"""Assemble the declared prints and certify their final material union.

The original assembler owns the root graph, exact recuts and stock coupons.
This producer changes only its process-local join callback. Each stage admits
a valid, nonempty fuse within the operand volume bounds; the complete exported
article then receives an independent material certificate using the original
native parents, hosts and exact declared cutters.
"""
from contextlib import redirect_stdout
from pathlib import Path
import hashlib
import importlib.util
import inspect
import io
import json
import math
import sys
import time
import argparse

from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut
from OCP.BOPAlgo import BOPAlgo_CellsBuilder
from OCP.TopTools import TopTools_ListOfShape

import cadquery as cq

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
ORIGINAL = HERE / "assemble_prints.py"
REPORT = HERE / "print-material-union-check.json"
PRINT_REPORT = HERE / "print-parts.json"
LIMIT_MM3 = .001
TOLERANCES_MM = (.0001, 0., .00001)
sys.path.insert(0, str(STUDY))
from evidence_binding import content_sha256, manifest_content_sha256


class MaterialCertificateError(ValueError):
    """A native material comparison did not establish its required result."""


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def volume(shape):
    value = shape.Volume(tol=1e-9)
    if not math.isfinite(value) or value < -1e-9:
        raise MaterialCertificateError("Invalid native material volume")
    return max(0., value)


class ExactNativeExtrema:
    """Retain exact native extrema only during immutable material proof.

    Native hash buckets are an index, never an identity certificate. A hit
    requires the retained TopoDS identity and location. The retained shallow
    handles prevent identity reuse and preserve each location independently.
    All reused extrema receive a fresh native query before publication.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.enabled = False
        self.buckets = {}
        self.entries = []
        self.hits = 0
        self.misses = 0

    @staticmethod
    def retained(shape):
        return cq.Shape.cast(shape.wrapped.Located(shape.wrapped.Location()))

    @classmethod
    def topology(cls, shape):
        return {kind: tuple(cls.retained(part).wrapped for part in getattr(shape, kind)())
                for kind in ("Solids", "Shells", "Faces", "Edges", "Vertices")}

    @staticmethod
    def values(bounds):
        return tuple(getattr(bounds, field) for field in
                     ("xmin", "ymin", "zmin", "xmax", "ymax", "zmax"))

    def begin(self):
        # Original unions/root/coupon checks have finished. They are never
        # admitted through this cache and cannot mutate a retained entry.
        self.reset()
        self.enabled = True

    def bounds(self, shape):
        if not self.enabled:
            return shape.BoundingBox()
        key = shape.hashCode()
        for entry in self.buckets.get(key, ()):
            native = entry["shape"].wrapped
            if native.IsSame(shape.wrapped) and native.Location().IsEqual(shape.wrapped.Location()):
                self.hits += 1
                entry["hits"] += 1
                return entry["bounds"]
        bounds = shape.BoundingBox()
        retained = self.retained(shape)
        entry = {"shape": retained, "bounds": bounds, "values": self.values(bounds),
                 "topology": self.topology(retained), "hits": 0}
        self.misses += 1
        self.entries.append(entry)
        self.buckets.setdefault(key, []).append(entry)
        return bounds

    def finish(self):
        self.enabled = False
        checks = []
        for index, entry in enumerate(self.entries):
            row = {"entry": index, "hits": entry["hits"],
                   "cached_native_extrema_mm": entry["values"],
                   "retained_topology_counts": {key: len(items) for key, items in entry["topology"].items()}}
            try:
                current = self.topology(entry["shape"])
                same = all(len(current[key]) == len(old)
                           and all(first.IsSame(second) and first.Location().IsEqual(second.Location())
                                   for first, second in zip(old, current[key]))
                           for key, old in entry["topology"].items())
                row["retained_native_topology_unchanged"] = same
                fresh_equal = True
                if entry["hits"]:
                    fresh = self.values(entry["shape"].BoundingBox())
                    fresh_equal = fresh == entry["values"]
                    row.update({"fresh_native_extrema_mm": fresh,
                                "fresh_exact_extrema_equal": fresh_equal})
                row["pass"] = same and fresh_equal
            except Exception as error:
                row.update({"pass": False, "error": str(error)})
            checks.append(row)
        return {"pass": all(row["pass"] for row in checks),
                "hits": self.hits, "misses": self.misses,
                "retained_entries": len(self.entries), "checks": checks,
                "scope": "Exact unrounded native BoundingBox queries, identity/location guarded with retained TopoDS handles. Cache starts after original unions/root/coupon checks. Certificate Boolean operations use independent geometry copies; retained topology and every reused native extremum are independently checked before publication."}


EXACT_EXTREMA = ExactNativeExtrema()


def separated(left, right):
    """Exact native extrema can establish separation without a Boolean."""
    a, b = EXACT_EXTREMA.bounds(left), EXACT_EXTREMA.bounds(right)
    return any(getattr(a, axis + "max") < getattr(b, axis + "min") - .0001
               or getattr(b, axis + "max") < getattr(a, axis + "min") - .0001
               for axis in ("x", "y", "z"))


def native_operation(left, right, operation, tolerance):
    """Build a completed, independent operation on actual native operands."""
    maker = operation()
    arguments, tools = TopTools_ListOfShape(), TopTools_ListOfShape()
    arguments.Append(left.copy(mesh=False).wrapped)
    tools.Append(right.copy(mesh=False).wrapped)
    maker.SetArguments(arguments)
    maker.SetTools(tools)
    maker.SetFuzzyValue(tolerance)
    maker.SetRunParallel(True)
    maker.Build()
    if not maker.IsDone() or (hasattr(maker, "HasErrors") and maker.HasErrors()):
        raise MaterialCertificateError("Native material operation did not complete without errors")
    if maker.Shape().IsNull():
        return None
    result = cq.Shape.cast(maker.Shape())
    if not result.isValid():
        raise MaterialCertificateError("Invalid completed native material operation")
    return result


def common_pair(left, right, tolerance):
    """A solid-to-solid common cannot contain more than either operand."""
    if separated(left, right):
        return 0., {"method": "native_extrema_separated", "common_mm3": 0.}
    result = native_operation(left, right, BRepAlgoAPI_Common, tolerance)
    common = 0. if result is None else sum(volume(solid) for solid in result.Solids())
    if common > min(volume(left), volume(right)) + LIMIT_MM3:
        raise MaterialCertificateError("Native common exceeds an operand's material")
    return common, {"method": "completed_independent_solid_common", "common_mm3": common,
                    "tolerance_mm": tolerance, "completed": True,
                    "empty_native_result": result is None or not result.Solids()}


def common_by_solid(left, right, label, require_full=False):
    """Use independent native solid pairs; never classify a whole compound.

    Complete containment sums common material only after proving the target
    solids do not overlap. Exclusion uses a conservative sum of individual
    commons, so overlapping target tools cannot conceal an intersection.
    """
    measurements, attempts = [], []
    targets = right.Solids()
    for tolerance in TOLERANCES_MM:
        try:
            target_pairs = []
            if require_full and len(targets) > 1:
                for index, first in enumerate(targets):
                    for second_index in range(index + 1, len(targets)):
                        second = targets[second_index]
                        if separated(first, second):
                            continue
                        amount, witness = common_pair(first, second, tolerance)
                        target_pairs.append({"indices": [index, second_index], **witness})
                        if amount >= LIMIT_MM3:
                            raise MaterialCertificateError("Overlapping target solids cannot certify a union by summed commons")
            measurements = []
            for index, solid in enumerate(left.Solids()):
                pairs = []
                for target_index, target in enumerate(targets):
                    if separated(solid, target):
                        continue
                    amount, witness = common_pair(solid, target, tolerance)
                    pairs.append({"target_solid": target_index, **witness})
                common = sum(row["common_mm3"] for row in pairs)
                source = volume(solid)
                if require_full and abs(source - common) >= LIMIT_MM3:
                    raise MaterialCertificateError("Native common does not contain the complete source solid")
                measurements.append({"solid": index, "source_volume_mm3": source,
                                     "common_mm3": common, "tolerance_mm": tolerance,
                                     "method": "independent_native_solid_pairs", "pairs": pairs})
            return {"label": label, "solids": measurements, "target_nonoverlap_checks": target_pairs,
                    "volume_mm3": sum(row["common_mm3"] for row in measurements)}
        except Exception as error:
            attempts.append({"tolerance_mm": tolerance, "error": str(error)})
    raise MaterialCertificateError(f"Common not established for {label}: {attempts}")


def contained_by_common(left, right, label):
    certificate = common_by_solid(left, right, label, require_full=True)
    certificate["missing_mm3"] = sum(abs(item["source_volume_mm3"] - item["common_mm3"])
                                        for item in certificate["solids"])
    certificate["pass"] = certificate["missing_mm3"] < LIMIT_MM3
    return certificate


def single_difference(left, right, label):
    """Certify one solid cut by one tool solid, including actual empty cuts."""
    source = volume(left)
    if separated(left, right):
        return left, {"label": label, "source_volume_mm3": source, "kept_volume_mm3": source,
                      "removed_volume_mm3": 0., "conservation_error_mm3": 0.,
                      "method": "native_extrema_separated", "pass": True}
    attempts = []
    for tolerance in TOLERANCES_MM:
        try:
            removed, witness = common_pair(left, right, tolerance)
            if removed == 0.:
                # A completed independent Solid-to-Solid Common certifies
                # this exact identity. Preserve the original object; no cut,
                # clone, export or byte change participates in the shortcut.
                return left, {"label": label, "empty": False,
                              "source_volume_mm3": source, "kept_volume_mm3": source,
                              "removed": witness, "removed_volume_mm3": 0.,
                              "conservation_error_mm3": 0.,
                              "method": "exact_zero_common_identity",
                              "original_source_object_preserved": True,
                              "identical_native_source": left.wrapped.IsSame(left.wrapped),
                              "kept_inside_source": {"method": "identical_native_source",
                                                     "missing_mm3": 0., "pass": True},
                              "tool_excluded": {"native_common": witness, "volume_mm3": 0., "pass": True},
                              "pass": True}
            result = native_operation(left, right, BRepAlgoAPI_Cut, tolerance)
            empty = result is None or not result.Solids()
            if empty:
                full = contained_by_common(left, right, label + "/empty_certificate")
                if not full["pass"] or abs(source - removed) >= LIMIT_MM3:
                    raise MaterialCertificateError("Empty cut lacks complete independent common material")
                return None, {"label": label, "empty": True, "source_volume_mm3": source,
                              "removed": witness, "empty_certificate": full,
                              "conservation_error_mm3": abs(source - removed), "pass": True}
            kept = volume(result)
            error = abs(kept - (source - removed))
            if error >= LIMIT_MM3 or kept > source + LIMIT_MM3:
                raise MaterialCertificateError("Difference does not conserve native material")
            inside = contained_by_common(result, left, label + "/kept_inside_source")
            exclusion = common_by_solid(result, right, label + "/tool_exclusion")
            if not inside["pass"] or exclusion["volume_mm3"] >= LIMIT_MM3:
                raise MaterialCertificateError("Difference lies outside source or inside tool")
            return result, {"label": label, "empty": False, "source_volume_mm3": source,
                            "kept_volume_mm3": kept, "removed": witness,
                            "tolerance_mm": tolerance, "conservation_error_mm3": error,
                            "kept_inside_source": inside, "tool_excluded": exclusion, "pass": True}
        except Exception as error:
            attempts.append({"tolerance_mm": tolerance, "error": str(error)})
    raise MaterialCertificateError(f"Difference not established for {label}: {attempts}")


def checked_difference(left, right, label):
    """Sequentially subtract individual tool solids with complete certificates.

    Union subtraction is associative. Overlapping tools are removed only from
    the material retained by prior steps; no compound common or double-counted
    removed volume participates in admission.
    """
    kept = list(left.Solids())
    steps = []
    for tool_index, tool in enumerate(right.Solids()):
        next_kept = []
        for source_index, solid in enumerate(kept):
            if separated(solid, tool):
                next_kept.append(solid)
                continue
            result, certificate = single_difference(solid, tool,
                label + f"/tool-{tool_index}/retained-solid-{source_index}")
            steps.append(certificate)
            if result is not None:
                next_kept.extend(result.Solids())
        kept = next_kept
        if not kept:
            break
    result = None if not kept else kept[0] if len(kept) == 1 else cq.Compound.makeCompound(kept)
    cumulative_error = sum(row.get("conservation_error_mm3", 0.) for row in steps)
    if cumulative_error >= LIMIT_MM3:
        raise MaterialCertificateError("Sequential recuts exceed the complete material-conservation limit")
    source_volume = volume(left)
    kept_volume = 0. if result is None else volume(result)
    certificate = {"label": label, "empty": result is None,
                   "source_volume_mm3": source_volume, "kept_volume_mm3": kept_volume,
                   "removed_volume_mm3": source_volume - kept_volume,
                   "conservation_error_mm3": cumulative_error,
                   "method": "sequential_independent_native_tool_solids", "steps": steps, "pass": True}
    return result, certificate


def two_source_union_certificate(retained, final, source_missing_total, label):
    """Bound outside material from two complete, single-solid sources.

    Inclusion-exclusion gives their exact union volume. The sum of the
    independently measured source-containment errors bounds the union
    material that can be missing from the final article. Therefore the
    union/final volume discrepancy plus that sum bounds all final material
    outside the union. The 0.001 mm3 material limit is unchanged.
    """
    if len(retained) != 2 or any(len(shape.Solids()) != 1 for _, shape in retained):
        raise MaterialCertificateError("Two-source union proof requires two complete single-solid retained operands")
    (first_name, first), (second_name, second) = retained
    attempts = []
    for tolerance in TOLERANCES_MM:
        try:
            intersection = native_operation(first.Solids()[0], second.Solids()[0],
                                            BRepAlgoAPI_Common, tolerance)
            if intersection is None or len(intersection.Solids()) != 1:
                raise MaterialCertificateError("Two-source union proof requires a completed one-solid positive material Common")
            common_volume = sum(volume(solid) for solid in intersection.Solids())
            first_volume, second_volume, final_volume = volume(first), volume(second), volume(final)
            if not 0. < common_volume <= min(first_volume, second_volume) + LIMIT_MM3:
                raise MaterialCertificateError("Two-source intersection exceeds an operand or has no material")
            intersection_nonoverlap = common_by_solid(intersection, intersection,
                                                      label + "/intersection_nonoverlap", require_full=True)
            in_first = contained_by_common(intersection, first, label + "/intersection_inside_first")
            in_second = contained_by_common(intersection, second, label + "/intersection_inside_second")
            intersection_error = in_first["missing_mm3"] + in_second["missing_mm3"]
            union_volume = first_volume + second_volume - common_volume
            conservation_error = abs(final_volume - union_volume)
            outside_upper_bound = conservation_error + source_missing_total + intersection_error
            if outside_upper_bound >= LIMIT_MM3 or not in_first["pass"] or not in_second["pass"]:
                raise MaterialCertificateError("Complete two-source union does not meet the final material limit")
            return {"method": "complete_two_source_inclusion_exclusion",
                    "retained_source_names": [first_name, second_name],
                    "retained_source_volumes_mm3": [first_volume, second_volume],
                    "completed_positive_intersection": True,
                    "intersection_volume_mm3": common_volume,
                    "intersection_tolerance_mm": tolerance,
                    "intersection_nonoverlap": intersection_nonoverlap,
                    "intersection_inside_first": in_first,
                    "intersection_inside_second": in_second,
                    "union_volume_mm3": union_volume, "final_volume_mm3": final_volume,
                    "union_final_conservation_error_mm3": conservation_error,
                    "source_containment_error_sum_mm3": source_missing_total,
                    "intersection_containment_error_sum_mm3": intersection_error,
                    "outside_union_upper_bound_mm3": outside_upper_bound,
                    "limit_mm3": LIMIT_MM3, "attempts": attempts, "pass": True}
        except Exception as error:
            attempts.append({"tolerance_mm": tolerance, "error": str(error)})
    raise MaterialCertificateError(f"Two-source union not established for {label}: {attempts}")


def grouped_original_source_common(final, original_solids, label):
    """Compute final intersect union(original solids) using exact cells.

    Every original source is a complete independent native operand. Selecting
    final-and-source cells once per source, with one material identifier,
    takes their OR union. Removing internal boundaries joins only those
    selected cells. This is a full native Boolean, not a clipped or summed
    approximation to coverage.
    """
    if len(final.Solids()) != 1 or not original_solids:
        raise MaterialCertificateError("Grouped source Common requires one final solid and complete original solids")
    builder = BOPAlgo_CellsBuilder()
    final_copy = final.copy(mesh=False)
    source_copies = [solid.copy(mesh=False) for solid in original_solids]
    builder.AddArgument(final_copy.wrapped)
    for solid in source_copies:
        builder.AddArgument(solid.wrapped)
    builder.SetNonDestructive(True)
    builder.SetFuzzyValue(0.)
    builder.SetRunParallel(True)
    builder.Perform()
    if builder.HasErrors() or builder.GetAllParts().IsNull():
        raise MaterialCertificateError("Exact grouped native partition did not complete without errors")
    partition = cq.Shape.cast(builder.GetAllParts())
    if not partition.isValid() or not partition.Solids():
        raise MaterialCertificateError("Exact grouped native partition has no valid solid material")
    empty = TopTools_ListOfShape()
    for solid in source_copies:
        take = TopTools_ListOfShape()
        take.Append(final_copy.wrapped)
        take.Append(solid.wrapped)
        builder.AddToResult(take, empty, 1, False)
    builder.RemoveInternalBoundaries()
    if builder.HasErrors() or builder.Shape().IsNull():
        raise MaterialCertificateError("Exact grouped source Common did not complete with material")
    result = cq.Shape.cast(builder.Shape())
    if not result.isValid():
        raise MaterialCertificateError("Invalid exact grouped source Common")
    return result, {"label": label, "method": "exact_native_cells_final_intersect_original_source_union",
                    "completed": True, "valid": True, "tolerance_mm": 0.,
                    "original_source_solids": len(original_solids),
                    "partition_solids": len(partition.Solids()),
                    "selected_material": 1, "internal_boundaries_removed": True,
                    "result_solids": len(result.Solids())}


def grouped_source_semantics_witnesses():
    """Independently establish OR tool-group semantics on complete solids."""
    cases = [
        ("overlapping_tools", cq.Solid.makeBox(3, 1, 1),
         [cq.Solid.makeBox(2, 1, 1), cq.Solid.makeBox(2, 1, 1, cq.Vector(1, 0, 0))], 3., 1),
        ("separated_tools", cq.Solid.makeBox(5, 1, 1),
         [cq.Solid.makeBox(1, 1, 1), cq.Solid.makeBox(1, 1, 1, cq.Vector(4, 0, 0))], 2., 2),
        ("external_tool", cq.Solid.makeBox(3, 1, 1),
         [cq.Solid.makeBox(2, 1, 1), cq.Solid.makeBox(1, 1, 1, cq.Vector(10, 0, 0))], 2., 1),
    ]
    witnesses = []
    for name, argument, tools, expected_volume, expected_solids in cases:
        result, operation = grouped_original_source_common(argument, tools, "OR semantics/" + name)
        error = abs(sum(volume(solid) for solid in result.Solids()) - expected_volume)
        passed = error < 1e-10 and len(result.Solids()) == expected_solids
        witnesses.append({"case": name, "operation": operation,
                          "expected_union_common_volume_mm3": expected_volume,
                          "volume_error_mm3": error, "expected_solids": expected_solids, "pass": passed})
        if not passed:
            raise MaterialCertificateError("Grouped native source Common did not establish OR semantics")
    return witnesses


def grouped_source_coverage_certificate(final, original_solids, source_missing_total, label):
    """Certify full final coverage without unstable sequential residues."""
    semantics = grouped_source_semantics_witnesses()
    coverage, operation = grouped_original_source_common(final, original_solids, label)
    if len(coverage.Solids()) != 1:
        raise MaterialCertificateError("Complete original-source coverage must be one valid solid")
    final_volume, coverage_volume = volume(final), volume(coverage)
    volume_error = abs(final_volume - coverage_volume)
    forward_amount, forward_operation = common_pair(final.Solids()[0], coverage.Solids()[0], 0.)
    reverse_amount, reverse_operation = common_pair(coverage.Solids()[0], final.Solids()[0], 0.)
    forward_error = abs(final_volume - forward_amount)
    reverse_error = abs(coverage_volume - reverse_amount)
    outside_upper_bound = volume_error + forward_error + reverse_error + source_missing_total
    if outside_upper_bound >= LIMIT_MM3:
        raise MaterialCertificateError("Complete grouped original-source coverage does not meet the final material limit")
    return {"method": "complete_grouped_original_source_native_common_coverage",
            "source_union_OR_semantics_witnesses": semantics, "operation": operation,
            "final_volume_mm3": final_volume, "coverage_volume_mm3": coverage_volume,
            "coverage_final_volume_error_mm3": volume_error,
            "final_in_coverage_common": {**forward_operation, "missing_mm3": forward_error},
            "coverage_in_final_common": {**reverse_operation, "missing_mm3": reverse_error},
            "source_containment_error_sum_mm3": source_missing_total,
            "outside_union_upper_bound_mm3": outside_upper_bound,
            "limit_mm3": LIMIT_MM3, "pass": True}

def exact_cutters(snapshot, owner):
    selected = []
    for label, manifest in snapshot["manifests"].items():
        for name, record in manifest.get("pilot_cutters", {}).items():
            target = snapshot["pilot_overrides"].get(
                name, record.get("print_owner", "cold-core-lid" if name.startswith("relay-") else None))
            if target == owner:
                selected.append((label + "/pilot_cutters/" + name, record))
        for name, record in manifest.get("clearance_cutters", {}).items():
            if record.get("print_owner") == owner:
                selected.append((label + "/clearance_cutters/" + name, record))
    return selected


def received_snapshot():
    """Recreate the original input graph and inspect the held 17 articles.

    This path performs no article fuse, recut, export, or byte rewrite. It
    reconstructs the unchanged original assembler's ownership and coupon
    checks from the currently captured manifest/native inputs.
    """
    held_raw = PRINT_REPORT.read_bytes()
    held = json.loads(held_raw)
    previous = json.loads(REPORT.read_bytes())
    unchanged_check_sources = {}
    for source in (ORIGINAL, STUDY / "evidence_binding.py"):
        relative = str(source.relative_to(ROOT))
        actual = digest(source.read_bytes())
        if held["source_inputs"].get(relative) != actual:
            raise MaterialCertificateError("Original root/coupon check source changed: " + relative)
        unchanged_check_sources[relative] = actual
    if (not previous["source_binding_pass"] or previous.get("native_drift")
            or previous.get("source_drift") or previous.get("manifest_drift")):
        raise MaterialCertificateError("Held original checks do not have a complete stable input receipt")
    files = {folder: STUDY / folder / "candidate.json"
             for folder in ("funnel", "pump", "routing", "structure", "mounts", "wiring")
             if (STUDY / folder / "candidate.json").exists()}
    for label, path in (("fluid-mounts", STUDY / "mounts/fluid-candidate.json"),
                        ("body-mounts", STUDY / "mounts/body-candidate.json"),
                        ("water5-mounts", STUDY / "mounts/water5-hosts.json"),
                        ("tube-hosts", STUDY / "routing/tube-hosts.json"),
                        ("roof-hatch", HERE / "roof-hatch.json")):
        if path.exists():
            files[label] = path
    raw_inputs = {label: path.read_bytes() for label, path in files.items()}
    manifests = {label: json.loads(raw) for label, raw in raw_inputs.items()}
    content_hashes = {str(files[label].relative_to(ROOT)): content_sha256(manifests[label])
                      for label in files}
    for path, sha in content_hashes.items():
        if held["manifest_content_sha256"].get(path) != sha:
            raise MaterialCertificateError("Held articles have different substantive input: " + path)
    parts = {}
    for manifest in manifests.values():
        parts.update(manifest.get("parts", {}))
    source_records = dict(parts)
    for label, manifest in manifests.items():
        for key in ("pilot_cutters", "clearance_cutters", "joined_root_coupons"):
            source_records.update({label + "/" + key + "/" + name: record
                                   for name, record in manifest.get(key, {}).items()})
    native_bytes, native_inputs, loaded = {}, {}, {}
    for name, record in source_records.items():
        path = record["brep"]
        raw = native_bytes.setdefault(path, (ROOT / path).read_bytes())
        sha = digest(raw)
        declared = record.get("sha256")
        if isinstance(declared, dict):
            declared = declared.get(path, declared.get("brep"))
        if declared and declared != sha:
            raise MaterialCertificateError("Changed native input: " + name)
        if held["native_inputs"].get(name) != {"brep": path, "sha256": sha}:
            raise MaterialCertificateError("Held article's original native input differs: " + name)
        native_inputs[name] = {"brep": path, "sha256": sha}
    def load(record):
        path = record["brep"]
        if path not in loaded:
            loaded[path] = cq.Shape.importBrep(io.BytesIO(native_bytes[path]))
            if loaded[path].wrapped.IsNull() or not loaded[path].isValid():
                raise MaterialCertificateError("Invalid received source: " + path)
        return loaded[path]
    names = {
        "enclosure-back-top": {"controller-roof-boss-" + str(i) for i in range(1, 5)}
                              | {"ground-roof-boss", "discharge-chain-anchor"},
        "cold-core-lid": {"supply-lid-boss-" + str(i) for i in range(1, 5)}
                         | {"supply-lid-web-1", "supply-lid-web-2", "vk-cradle",
                            "source-a-cradle", "source-b-cradle", "suction-chain-anchor"},
        "enclosure-front-top": set(), "funnel-frame": set(), "cold-core-cap": set(),
        "discharge-chain-lower-key": set(), "suction-chain-upper-key": set()}
    rootkeys = {"shell_fuse_part_names": "enclosure-back-top", "lid_fuse_part_names": "cold-core-lid",
                "front_shell_fuse_part_names": "enclosure-front-top", "cap_fuse_part_names": "cold-core-cap",
                "frame_fuse_part_names": "funnel-frame"}
    for manifest in manifests.values():
        for key, owner in rootkeys.items():
            names[owner].update(manifest.get(key, []))
    base = {"enclosure-back-top": "enclosure-back-top", "enclosure-front-top": "enclosure-front-top",
            "cold-core-lid": "cold-core/foam-cap-lid-top", "cold-core-cap": "cold-core/foam-cap-top",
            "funnel-frame": "funnel-frame", "discharge-chain-lower-key": "discharge-chain-lower-key",
            "suction-chain-upper-key": "suction-chain-upper-key"}
    if "asse-drip-pan" in parts:
        base["asse-drip-pan"] = "asse-drip-pan"
        names["asse-drip-pan"] = set()
    for manifest in manifests.values():
        for name, record in manifest.get("standalone_print_parts", {}).items():
            base[name] = record.get("source_part", name)
            names[name] = set(record.get("fuse_part_names", []))
    for manifest in manifests.values():
        for host, owner in manifest.get("root_owner_overrides", {}).items():
            for group in names.values():
                group.discard(host)
            if owner not in names:
                raise MaterialCertificateError("Undeclared print owner: " + owner)
            names[owner].add(host)
    pilot_overrides = {}
    for manifest in manifests.values():
        pilot_overrides.update(manifest.get("pilot_owner_overrides", {}))
    if set(base) != set(held["parts"]) or len(base) != 17:
        raise MaterialCertificateError("Held article membership differs from the original 17-article graph")
    checks, tracked, held_byte_hashes = [], {}, {}
    for owner, source in base.items():
        prior = previous["owners"][owner]
        expected_hosts = {row["name"] for row in prior["source_operands"] if row["kind"] == "host"}
        if prior["source_part"] != source or expected_hosts != names[owner]:
            raise MaterialCertificateError("Held article original parent/host graph differs: " + owner)
        record = held["parts"][owner]
        raw = (ROOT / record["brep"]).read_bytes()
        sha = digest(raw)
        if sha != record["sha256"] or sha != prior["final_sha256"]:
            raise MaterialCertificateError("Held printed article bytes changed: " + owner)
        held_byte_hashes[record["brep"]] = sha
        final = cq.Shape.importBrep(io.BytesIO(raw))
        base_shape = load(parts[source])
        hosts = {name: load(parts[name]) for name in sorted(names[owner])}
        tracked[owner] = {"source_part": source, "parent": base_shape, "hosts": hosts}
        original_check = next(row for row in held["checks"] if row["part"] == owner)
        for key in ("valid_single_solid", "all_roots_reach_parent", "all_post_cut_witnesses_preserved"):
            if not original_check[key]:
                raise MaterialCertificateError("Original held root/coupon check failed: " + owner + "/" + key)
        if {row["name"] for row in record["native_host_roots"]} != names[owner]:
            raise MaterialCertificateError("Held native root evidence differs from current ownership: " + owner)
        if not all(row["native_parent_reached"] for row in record["native_host_roots"]):
            raise MaterialCertificateError("A held root does not reach its parent: " + owner)
        coupon_names = {name for manifest in manifests.values()
                        for name, coupon in manifest.get("joined_root_coupons", {}).items()
                        if coupon["print_owner"] == owner}
        if {row["coupon"] for row in record["post_cut_stock_witnesses"]} != coupon_names:
            raise MaterialCertificateError("Held coupon evidence differs from the current declared coupons: " + owner)
        if not all(row["pass"] for row in record["post_cut_stock_witnesses"]):
            raise MaterialCertificateError("A held declared stock coupon failed: " + owner)
        checks.append({"part": owner, "valid_single_solid": final.isValid() and len(final.Solids()) == 1,
                       "all_roots_reach_parent": original_check["all_roots_reach_parent"],
                       "all_post_cut_witnesses_preserved": original_check["all_post_cut_witnesses_preserved"]})
    receipt_path = ROOT / ".cache/pump-first-layout/structure/held-original-print-checks.json"
    # This immutable metadata receipt preserves the actual original graph and
    # coupon evidence. No printed native file is written in verify-only mode.
    if receipt_path.exists() and receipt_path.read_bytes() != held_raw:
        receipt_path = receipt_path.with_name("held-original-print-checks-" + digest(held_raw)[:12] + ".json")
    receipt_path.write_bytes(held_raw)
    reused = {"pass": True, "receipt": str(receipt_path.relative_to(ROOT)),
              "receipt_sha256": digest(held_raw),
              "unchanged_check_sources_sha256": unchanged_check_sources,
              "native_inputs_sha256": {name: row["sha256"] for name, row in native_inputs.items()},
              "manifest_content_sha256": content_hashes,
              "article_sha256": held_byte_hashes,
              "scope": "Reuse only the held passing original root/contact/coupon evidence after independently verifying every original native input, substantive manifest, unchanged check producer and every printed article byte. Final material certificates and scene-parent correspondence execute freshly."}
    sources = {str(path.relative_to(ROOT)): digest(path.read_bytes())
               for path in (Path(__file__), ORIGINAL, STUDY / "evidence_binding.py")}
    pending = {"parts": held["parts"], "checks": checks,
               "pass": all(row["valid_single_solid"] and row["all_roots_reach_parent"]
                           and row["all_post_cut_witnesses_preserved"] for row in checks),
               "inputs_sha256": {str(files[label].relative_to(ROOT)): digest(raw) for label, raw in raw_inputs.items()},
               "native_inputs": native_inputs, "source_inputs": sources,
               "manifest_content_sha256": content_hashes, "source_drift": [], "manifest_drift": [],
               "scope": held["scope"], "original_check_reuse": reused}
    snapshot = {"base": base, "names": names, "parts": parts, "manifests": manifests,
                "pilot_overrides": pilot_overrides, "native_bytes": native_bytes}
    return pending, snapshot, tracked, previous["stage_join_checks"], held_byte_hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true", help="Verify the 17 already exported articles without fusing, recutting or exporting them")
    args = parser.parse_args()
    EXACT_EXTREMA.reset()
    initial_sources = {str(path.relative_to(ROOT)): digest(path.read_bytes())
                       for path in (Path(__file__), ORIGINAL, STUDY / "evidence_binding.py")}
    scene_path = HERE / "scene-stock.json"
    scene_raw = scene_path.read_bytes()
    scene = json.loads(scene_raw)
    scene_content = content_sha256(scene)
    scene_bytes = {name: (ROOT / record["brep"]).read_bytes()
                   for name, record in scene["parts"].items()}
    scene_sources = {}
    for name, record in scene["parts"].items():
        actual = digest(scene_bytes[name])
        if record.get("sha256") != actual:
            raise MaterialCertificateError("Scene parent differs from its declared native hash: " + name)
        scene_sources["scene-parent/" + name] = {"brep": record["brep"], "sha256": actual}
    spec = importlib.util.spec_from_file_location("_unchanged_print_assembler", ORIGINAL)
    original = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(original)
    strong_joined = original.joined
    progress_stream = sys.stdout
    stages = []
    tracked_operands = {}
    pending = {}
    snapshot = {}
    original_write = Path.write_text

    def stage_joined(left, right, owner, name):
        frame = inspect.currentframe().f_back
        if frame.f_code is not original.main.__code__:
            raise MaterialCertificateError("Unexpected join caller")
        local = frame.f_locals
        tracked = tracked_operands.setdefault(owner, {"source_part": local["source"],
                                                       "parent": local["base_shape"], "hosts": {}})
        if tracked["source_part"] != local["source"]:
            raise MaterialCertificateError("Original parent changed inside its assembly")
        tracked["hosts"][name] = right
        started = time.monotonic()
        left_volume, right_volume = volume(left), volume(right)
        attempts = []
        for tolerance in TOLERANCES_MM:
            try:
                result = left.copy(mesh=False).fuse(right.copy(mesh=False), tol=tolerance)
                valid = not result.wrapped.IsNull() and result.isValid() and bool(result.Solids())
                result_volume = volume(result) if valid else None
                admitted = valid and max(left_volume, right_volume) - LIMIT_MM3 <= result_volume <= left_volume + right_volume + LIMIT_MM3
                attempts.append({"tolerance_mm": tolerance, "valid_nonempty": valid,
                                 "left_volume_mm3": left_volume, "right_volume_mm3": right_volume,
                                 "result_volume_mm3": result_volume, "volume_bounds_pass": admitted})
                if admitted:
                    stages.append({"owner": owner, "host": name, "attempts": attempts,
                                   "strong_fallback": False, "elapsed_seconds": time.monotonic() - started})
                    print(f"Joined {owner}: {name} ({time.monotonic() - started:.2f}s)",
                          file=progress_stream, flush=True)
                    return result
            except Exception as error:
                attempts.append({"tolerance_mm": tolerance, "error": str(error)})
        fallback_certificate = None
        strong_error = None
        try:
            result = strong_joined(left, right, owner, name)
        except Exception as error:
            strong_error = str(error)
            certificates = []
            for direction, contained, container in (
                    ("right_material_contained_in_left", right, left),
                    ("left_material_contained_in_right", left, right)):
                try:
                    certificate = contained_by_common(contained, container,
                                                      owner + "/" + name + "/" + direction)
                    certificates.append({"direction": direction, "certificate": certificate})
                    if certificate["pass"]:
                        result = container.copy(mesh=False)
                        fallback_certificate = {"direction": direction, "certificate": certificate}
                        break
                except Exception as certificate_error:
                    certificates.append({"direction": direction, "pass": False,
                                         "error": str(certificate_error)})
            else:
                raise MaterialCertificateError(
                    f"Original strong join failed for {owner}/{name}: {strong_error}; "
                    f"neither complete material containment was certified: {certificates}") from error
        stages.append({"owner": owner, "host": name, "attempts": attempts,
                       "strong_fallback": True, "strong_fallback_error": strong_error,
                       "certified_containment_fallback": fallback_certificate,
                       "elapsed_seconds": time.monotonic() - started})
        print(f"Joined {owner}: {name}, original strong fallback ({time.monotonic() - started:.2f}s)",
              file=progress_stream, flush=True)
        return result

    def capture_report(path, data, *args, **kwargs):
        if path == PRINT_REPORT:
            frame = inspect.currentframe().f_back
            if frame.f_code is not original.main.__code__ or pending:
                raise MaterialCertificateError("Unexpected original print report writer")
            local = frame.f_locals
            pending.update(json.loads(data))
            # These are the exact mappings and bytes read by the original main,
            # including standalone articles, ownership overrides and recuts.
            snapshot.update({"base": dict(local["base"]),
                             "names": {owner: set(names) for owner, names in local["names"].items()},
                             "parts": dict(local["parts"]), "manifests": dict(local["manifests"]),
                             "pilot_overrides": dict(local["pilot_overrides"]),
                             "native_bytes": dict(local["native_bytes"])})
            return len(data)
        return original_write(path, data, *args, **kwargs)

    held_byte_hashes = {}
    if args.verify_only:
        pending, snapshot, tracked_operands, stages, held_byte_hashes = received_snapshot()
    else:
        original.joined = stage_joined
        Path.write_text = capture_report
        try:
            # Do not publish the original provisional pass before material proof.
            # Its original checks remain in the captured report without alteration.
            with redirect_stdout(io.StringIO()):
                original.main()
        finally:
            Path.write_text = original_write
            original.joined = strong_joined
    if not pending or not snapshot:
        raise MaterialCertificateError("Original assembler produced no authoritative report")

    sources = dict(initial_sources)
    for path, sha in pending["source_inputs"].items():
        if path in sources and sources[path] != sha:
            raise MaterialCertificateError("Original assembler source changed before its own snapshot: " + path)
        sources[path] = sha
    native_inputs = {**pending["native_inputs"], **scene_sources}
    pending["manifest_content_sha256"][str(scene_path.relative_to(ROOT))] = scene_content
    pending["inputs_sha256"][str(scene_path.relative_to(ROOT))] = digest(scene_raw)
    received = {}

    def load_source(record):
        path = record["brep"]
        if path not in received:
            received[path] = cq.Shape.importBrep(io.BytesIO(snapshot["native_bytes"][path]))
            if not received[path].isValid() or received[path].wrapped.IsNull():
                raise MaterialCertificateError("Invalid received original source " + path)
        return received[path]

    EXACT_EXTREMA.begin()
    owners = {}
    scene_seen = set()
    for owner, source_name in snapshot["base"].items():
        started = time.monotonic()
        record = pending["parts"][owner]
        raw_final = (ROOT / record["brep"]).read_bytes()
        final_hash = digest(raw_final)
        native_inputs["verified-print/" + owner] = {"brep": record["brep"], "sha256": final_hash}
        evidence = {"source_part": source_name, "final_brep": record["brep"],
                    "final_sha256": final_hash, "source_operands": [], "declared_cutters": [],
                    "kept_source_checks": [], "cutter_exclusion_checks": [], "outside_source_steps": []}
        owners[owner] = evidence
        try:
            if final_hash != record["sha256"]:
                raise MaterialCertificateError("Exported article changed before material proof")
            final = cq.Shape.importBrep(io.BytesIO(raw_final))
            if not final.isValid() or len(final.Solids()) != 1:
                raise MaterialCertificateError("Final received article is not a valid single solid")
            host_names = sorted(snapshot["names"][owner])
            if host_names:
                tracked = tracked_operands.get(owner)
                if not tracked or tracked["source_part"] != source_name or sorted(tracked["hosts"]) != host_names:
                    raise MaterialCertificateError("Original parent/host capture disagrees with original main")
            original_sources = [("parent", source_name, snapshot["parts"][source_name])]
            original_sources.extend(("host", name, snapshot["parts"][name]) for name in host_names)
            operands = []
            for kind, name, source_record in original_sources:
                shape = load_source(source_record)
                evidence["source_operands"].append({"kind": kind, "name": name,
                                                     "brep": source_record["brep"],
                                                     "sha256": digest(snapshot["native_bytes"][source_record["brep"]]),
                                                     "solids": len(shape.Solids()), "volume_mm3": volume(shape)})
                operands.extend((kind, name, index, solid) for index, solid in enumerate(shape.Solids()))
            tools = []
            for name, tool_record in exact_cutters(snapshot, owner):
                tool = load_source(tool_record)
                tools.append((name, tool))
                evidence["declared_cutters"].append({"name": name, "brep": tool_record["brep"],
                                                      "sha256": digest(snapshot["native_bytes"][tool_record["brep"]])})
            missing_total = 0.
            kept_parent_solids = []
            retained_sources = []
            for kind, name, index, solid in operands:
                relevant = [(tool_name, tool) for tool_name, tool in tools if not separated(solid, tool)]
                kept = solid
                recut = None
                if relevant:
                    tool_shape = relevant[0][1] if len(relevant) == 1 else cq.Compound.makeCompound([tool for _, tool in relevant])
                    kept, recut = checked_difference(solid, tool_shape, owner + "/" + name + f"/solid-{index}/declared_recuts")
                if kept is None:
                    containment = {"missing_mm3": 0., "pass": True,
                                   "scope": "Entire source removed by independently certified declared cutters"}
                else:
                    containment = contained_by_common(kept, final, owner + "/" + name + f"/solid-{index}/retained_material")
                    retained_sources.append((name, kept))
                    if kind == "parent":
                        kept_parent_solids.extend(kept.Solids())
                missing_total += containment["missing_mm3"]
                evidence["kept_source_checks"].append({"source": name, "solid": index,
                                                         "relevant_cutters": [key for key, _ in relevant],
                                                         "recut": recut, "containment": containment,
                                                         "pass": containment["pass"]})
            if source_name in scene["parts"]:
                if not kept_parent_solids:
                    raise MaterialCertificateError("Retained original parent has no material for its scene correspondence")
                kept_parent = cq.Compound.makeCompound(kept_parent_solids)
                scene_parent = cq.Shape.importBrep(io.BytesIO(scene_bytes[source_name]))
                if not scene_parent.isValid() or len(scene_parent.Solids()) != 1:
                    raise MaterialCertificateError("Scene parent is not a valid single solid")
                scene_in_parent = contained_by_common(scene_parent, kept_parent,
                                                     owner + "/scene_parent_in_retained_original")
                parent_in_scene = contained_by_common(kept_parent, scene_parent,
                                                     owner + "/retained_original_in_scene_parent")
                volume_error = abs(volume(scene_parent) - volume(kept_parent))
                scene_certificate = {"scene_part": source_name,
                                     **scene_sources["scene-parent/" + source_name],
                                     "retained_original_parent_volume_mm3": volume(kept_parent),
                                     "scene_parent_volume_mm3": volume(scene_parent),
                                     "volume_error_mm3": volume_error,
                                     "scene_in_retained_parent": scene_in_parent,
                                     "retained_parent_in_scene": parent_in_scene,
                                     "pass": scene_in_parent["pass"] and parent_in_scene["pass"]
                                             and volume_error < LIMIT_MM3}
                evidence["scene_parent_correspondence"] = scene_certificate
                scene_seen.add(source_name)
                if not scene_certificate["pass"]:
                    raise MaterialCertificateError("Scene parent differs from the retained original parent material")
            excluded_total = 0.
            for name, tool in tools:
                exclusion = common_by_solid(final, tool, owner + "/" + name + "/final_tool_exclusion")
                excluded_total += exclusion["volume_mm3"]
                evidence["cutter_exclusion_checks"].append({"cutter": name, "common": exclusion,
                                                             "pass": exclusion["volume_mm3"] < LIMIT_MM3})
            outside_alternative = None
            try:
                outside = final
                for kind, name, index, solid in operands:
                    if outside is None:
                        break
                    outside, subtraction = checked_difference(outside, solid, owner + "/outside/" + name + f"/solid-{index}")
                    evidence["outside_source_steps"].append({"source": name, "solid": index,
                                                               "difference": subtraction})
                outside_volume = 0. if outside is None else volume(outside)
            except MaterialCertificateError as difference_error:
                if owner == "enclosure-front-top":
                    outside_alternative = two_source_union_certificate(retained_sources, final, missing_total,
                                                                       owner + "/complete_retained_union")
                elif owner == "cold-core-lid":
                    outside_alternative = grouped_source_coverage_certificate(
                        final, [solid for _, _, _, solid in operands], missing_total,
                        owner + "/complete_original_source_coverage")
                else:
                    raise
                outside_volume = outside_alternative["outside_union_upper_bound_mm3"]
                evidence["outside_source_difference_error"] = str(difference_error)
                evidence["outside_source_alternative"] = outside_alternative
            evidence.update({"valid_single_solid": True, "source_missing_total_mm3": missing_total,
                             "declared_cutter_common_total_mm3": excluded_total,
                             "outside_all_original_sources_mm3": outside_volume if outside_alternative is None else None,
                             "outside_all_original_sources_upper_bound_mm3": outside_volume,
                             "pass": missing_total < LIMIT_MM3 and excluded_total < LIMIT_MM3
                                     and outside_volume < LIMIT_MM3
                                     and all(item["pass"] for item in evidence["kept_source_checks"])
                                     and all(item["pass"] for item in evidence["cutter_exclusion_checks"])})
        except Exception as error:
            evidence.update({"pass": False, "error": str(error)})
        evidence["elapsed_seconds"] = time.monotonic() - started
        print(f"Final material {owner}: {'PASS' if evidence['pass'] else 'FAIL'} ({evidence['elapsed_seconds']:.2f}s)", flush=True)

    extrema_certificate = EXACT_EXTREMA.finish()
    held_article_drift = [path for path, sha in held_byte_hashes.items()
                          if digest((ROOT / path).read_bytes()) != sha]
    native_drift = [name for name, record in native_inputs.items()
                    if digest((ROOT / record["brep"]).read_bytes()) != record["sha256"]]
    source_drift = [path for path, sha in sources.items() if digest((ROOT / path).read_bytes()) != sha]
    manifest_drift = [path for path, sha in pending["manifest_content_sha256"].items()
                      if manifest_content_sha256(ROOT / path) != sha]
    scene_complete = scene_seen == set(scene["parts"]) and len(scene_seen) == 6
    material_pass = bool(owners) and len(owners) == len(pending["parts"]) and all(item["pass"] for item in owners.values()) and scene_complete and extrema_certificate["pass"]
    stable = not held_article_drift and not native_drift and not source_drift and not manifest_drift and not pending["source_drift"] and not pending["manifest_drift"]
    report = {"pass": material_pass and stable, "source_binding_pass": stable, "limit_mm3": LIMIT_MM3,
              "scene_parent_correspondence_complete": scene_complete,
              "scene_parent_names": sorted(scene_seen),
              "owners": owners, "stage_join_checks": stages,
              "exact_native_extrema_cache": extrema_certificate,
              "native_inputs": native_inputs, "source_inputs": sources,
              "inputs_sha256": pending["inputs_sha256"],
              "manifest_content_sha256": pending["manifest_content_sha256"],
              "native_drift": native_drift, "source_drift": source_drift,
              "held_article_sha256": held_byte_hashes, "held_article_drift": held_article_drift,
              "verification_only": args.verify_only, "original_check_reuse": pending.get("original_check_reuse"),
              "manifest_drift": manifest_drift,
              "scope": "Final cold-imported native material equals all original parent and host solids minus the exact declared cutters, within 0.001 mm3. Original root graph and recut stock coupon checks are preserved. This does not qualify loads, lifetime or support-removal effort."}
    original_pass = pending["pass"]
    pending["source_inputs"] = sources
    pending["source_drift"] = sorted(set(pending["source_drift"] + native_drift + source_drift))
    pending["manifest_drift"] = sorted(set(pending["manifest_drift"] + manifest_drift))
    pending["material_union_check"] = {"report": str(REPORT.relative_to(ROOT)), "pass": report["pass"]}
    for check in pending["checks"]:
        check["final_material_union_preserved"] = owners.get(check["part"], {}).get("pass", False)
    pending["pass"] = original_pass and report["pass"]
    pending["verified_producer"] = str(Path(__file__).relative_to(ROOT))
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    PRINT_REPORT.write_text(json.dumps(pending, indent=2) + "\n")
    print(json.dumps({"pass": pending["pass"], "original_checks_pass": original_pass,
                      "final_material_union_pass": report["pass"],
                      "owners": {name: item["pass"] for name, item in owners.items()},
                      "native_drift": native_drift, "source_drift": source_drift,
                      "manifest_drift": manifest_drift}, indent=2), flush=True)
    if not pending["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
