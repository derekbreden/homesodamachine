"""Verify retained A–F artifacts and print records without evaluating current CAD.

fit-check.json is the geometric reading of the recorded tip at source_commit.
This command checks that the retained files still match their archived hashes;
it neither recomputes nor updates that reading.
"""

import json

from cover_retention_trial import verify


def main():
    result = verify()
    print(json.dumps({"passed": True, "scope": "retained artifact integrity", **result}, indent=2))


if __name__ == "__main__":
    main()
