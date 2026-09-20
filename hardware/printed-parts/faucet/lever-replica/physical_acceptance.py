"""Derek's physical observation, bound to the exact printed lever mesh.

Generators read this record; they never rewrite it or carry its acceptance onto
a changed mesh. The donor scan reconstruction is a separate comparison artifact.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECORD = HERE / "physical-acceptance.json"


def for_printed_model(stl_sha256=None):
    record = json.loads(RECORD.read_text())
    if stl_sha256 is None:
        stl = HERE / record["printed_stl"]
        stl_sha256 = hashlib.sha256(stl.read_bytes()).hexdigest() if stl.exists() else None
    matches = stl_sha256 == record["printed_stl_sha256"]
    return {
        "record": RECORD.name,
        "accepted_job_id": record["job_id"],
        "observed_date": record["observed_date"],
        "authority": record["authority"],
        "scope": record["scope"],
        "accepted_stl_sha256": record["printed_stl_sha256"],
        "current_stl_sha256": stl_sha256,
        "matches_accepted_geometry": matches,
        "physical_fit": record["physical_fit"] if matches else "unconfirmed for this mesh",
        "functional_operation": (record["functional_operation"] if matches
                                 else "unconfirmed for this mesh"),
        "quantified_strength": record["quantified_strength"],
        "quantified_endurance": record["quantified_endurance"],
    }
