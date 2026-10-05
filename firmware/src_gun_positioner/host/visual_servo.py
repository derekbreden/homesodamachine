"""Local response fitting and bounded correction; no camera or laser control."""
import math

def solve(matrix, rhs):
    n = len(rhs)
    a = [list(row) + [value] for row, value in zip(matrix, rhs)]
    if len(a) != n or any(len(row) != n + 1 for row in a):
        raise ValueError("Square response system required")
    scale = max((abs(v) for row in matrix for v in row), default=0)
    for column in range(n):
        pivot = max(range(column, n), key=lambda r: abs(a[r][column]))
        if abs(a[pivot][column]) <= max(1e-15, scale * 1e-10):
            raise ValueError("Response is rank-deficient; add observable independent features/trials")
        a[column], a[pivot] = a[pivot], a[column]
        divisor = a[column][column]
        a[column] = [v / divisor for v in a[column]]
        for row in range(n):
            if row == column:
                continue
            multiplier = a[row][column]
            a[row] = [v - multiplier * p for v, p in zip(a[row], a[column])]
    return [row[-1] for row in a]

def fit_jacobian(trials):
    """Each trial: {delta_mm:[6 signed screw changes], delta_feature:[N observed changes]}.

    Feature coordinates may be pixels or independently calibrated physical units.
    Fit compatible direction/history neighborhoods separately. A synthetic trial
    must retain its synthetic label in logs and cannot qualify physical motion.
    """
    if len(trials) < 6:
        raise ValueError("At least six independent signed trial vectors required")
    dimensions = len(trials[0]["delta_feature"])
    if dimensions < 6:
        raise ValueError("At least six independent observable feature coordinates required")
    for row in trials:
        if len(row["delta_mm"]) != 6 or len(row["delta_feature"]) != dimensions:
            raise ValueError("Inconsistent response-trial dimensions")
        if not all(math.isfinite(v) for v in row["delta_mm"] + row["delta_feature"]):
            raise ValueError("Finite measured response required")
    gram = [[sum(t["delta_mm"][i] * t["delta_mm"][j] for t in trials)
             for j in range(6)] for i in range(6)]
    result = []
    for feature in range(dimensions):
        rhs = [sum(t["delta_mm"][axis] * t["delta_feature"][feature] for t in trials)
               for axis in range(6)]
        result.append(solve(gram, rhs))
    return result

def correction(jacobian, feature_error, trust_mm=0.01):
    """Compute J*d≈error, then preserve its direction while bounding every screw change.

    No correction is issued here. Caller must check fresh paired frame times,
    detection confidence, current rig clearance and settled response after the move.
    """
    if len(jacobian) != len(feature_error) or len(jacobian) < 6 or trust_mm <= 0:
        raise ValueError("Observable Jacobian and positive trust region required")
    if any(len(row) != 6 for row in jacobian):
        raise ValueError("Jacobian must have six screw columns")
    if not all(math.isfinite(v) for row in jacobian for v in row) or not all(math.isfinite(v) for v in feature_error):
        raise ValueError("Finite observation error required")
    gram = [[sum(row[i] * row[j] for row in jacobian) for j in range(6)] for i in range(6)]
    rhs = [sum(row[i] * error for row, error in zip(jacobian, feature_error)) for i in range(6)]
    delta = solve(gram, rhs)
    scale = min(1.0, trust_mm / max(max(map(abs, delta)), 1e-15))
    return [v * scale for v in delta]
