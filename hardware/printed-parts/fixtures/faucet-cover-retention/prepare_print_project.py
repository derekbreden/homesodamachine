"""Verify the retained A–F print project and report its location.

The committed project contains the exact trial meshes and saved print profile.
The original preparation and slicing recipe is held at the source commit in
retained-artifacts.json. This entry point does not rebuild or slice the project.
"""

import argparse

from cover_retention_trial import HERE, verify


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    verify()
    print(HERE / "faucet-cover-retention-petgf.3mf")
    print("Verified retained A–F project; open this existing project for a reprint.")


if __name__ == "__main__":
    main()
