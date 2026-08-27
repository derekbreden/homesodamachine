#!/usr/bin/env python3
"""Whether the release can take the next cut, and whether the site is reading it the fast way.

    tools/cad-venv/bin/python tools/check_release_room.py
    tools/cad-venv/bin/python tools/check_release_room.py selftest

THE PATH FROM A CHANGE TO THE SITE ENDS HERE. A cut is built, packed, and put on the
`cad-artifacts` release; the running container adopts the lock without a deploy. Two things
about that store decide how long the last leg takes, and neither was visible until it broke.

ROOM. GitHub takes 1000 assets on a release and refuses the 1001st, and the store is
append-only. A refused upload is indistinguishable from a network flake to the uploader, which
drops `release.objects` and carries on — so a full release announces itself by the fast path
going quiet, and the bundle, which has no fallback, is what fails next. `pack.py --room` reads
the headroom and `--retire` wins it back; this is that reading on the board, so the ceiling is
seen while there is still room to do something about it.

THE OBJECT PATH. `release.objects` is the claim that every member of this lock is on the
release under its own hash, so a deploy fetches the few hundred KB that moved rather than the
whole tarball. Absent, every deploy reads 144 MB for members it already has. That is not a
fault in the geometry and no other check asks about it — the artifacts are correct either way,
and the only thing wrong is how long the human waits to see them.

IT REPORTS AND HOLDS NOTHING, like every check here. Red is a thing to look at.

A READING IT COULD NOT TAKE IS NOT A RED READING. This one asks GitHub, and `gh` missing, a
release unreachable or a rate limit are all facts about this machine and not about the tree. A
check that reddens the board on a flat network is noise, and the board is how the tree's
condition reaches the site.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "tools" / "cad-artifacts"))

import pack  # noqa: E402


def reading(root: Path) -> tuple:
    """`(held, free, want, objects_on, retirable, by_name, by_bundle)` for release and lock."""
    assets = pack.release_assets(root)
    if not assets:
        return None
    size = {a["name"]: a["size"] for a in assets}
    on_release = set(size)
    lock = pack.read_lock(root)
    members = set((lock.get("solids") or {}).values()) | set((lock.get("sidecars") or {}).values())
    short = [sha for sha in members if pack.object_asset(sha) not in on_release]
    unreachable, superseded = pack.retirable(root)
    by_name = sum(size.get(pack.object_asset(sha), 0) for sha in members)
    return (len(on_release), pack.RELEASE_ASSET_CAP - len(on_release),
            1 + len(short), bool((lock.get("release") or {}).get("objects")),
            len(unreachable) + len(superseded),
            by_name, (lock.get("bundle") or {}).get("bytes", 0))


def main() -> int:
    got = reading(_ROOT)
    if got is None:
        print("check_release_room: the release did not answer — no reading taken")
        return 0
    held, free, want, objects_on, may_go, by_name, by_bundle = got
    red = []
    if free < want:
        red.append(f"the release holds {held} of {pack.RELEASE_ASSET_CAP} and the next cut wants "
                   f"{want}; {may_go} asset(s) may be retired for it")
    if not objects_on:
        red.append("the lock does not carry `release.objects`, so every deploy reads the whole "
                   "bundle for members it already has")
    # AND THE PREMISE `fetch-cad-artifacts.mjs` DROPPED ITS THRESHOLD ON. It asks for every
    # member by name because the whole lock by name reads less than the bundle does — each
    # member gzipped on its own, without the tar's framing. If that ever inverts, the worst
    # case stops being the cheaper read and the fetch wants its threshold back.
    if objects_on and by_bundle and by_name > by_bundle:
        red.append(f"the whole lock by name is {by_name / 1e6:.1f} MB against a bundle of "
                   f"{by_bundle / 1e6:.1f} MB, so a full move now reads more by object")
    for line in red:
        print(f"  {line}")
    if red:
        print(f"check_release_room: {len(red)} thing(s) stand between a cut and the site"
              "\n    tools/cad-venv/bin/python tools/cad-artifacts/pack.py --room")
        return 1
    print(f"check_release_room: {free} of {pack.RELEASE_ASSET_CAP} free, the next cut wants "
          f"{want}, and the whole lock reads by name in {by_name / 1e6:.1f} MB against "
          f"{by_bundle / 1e6:.1f} MB of bundle")
    return 0


def selftest() -> int:
    """The two readings that redden, and the one that does not, on figures rather than a release."""
    holds = []

    def hold(label: str, got: bool) -> None:
        holds.append((label, bool(got)))
        print(f"  {'ok  ' if got else 'FAIL'} {label}")

    def verdict(held, free, want, objects_on, by_name=143.0, by_bundle=144.2):
        out = []
        if free < want:
            out.append("room")
        if not objects_on:
            out.append("objects")
        if objects_on and by_bundle and by_name > by_bundle:
            out.append("cheaper")
        return out

    hold("a release with room and the object path on is green",
         verdict(795, 205, 43, True) == [])
    hold("a release that cannot take the next cut is red",
         verdict(990, 10, 43, True) == ["room"])
    hold("a lock without `release.objects` is red on its own",
         verdict(795, 205, 43, False) == ["objects"])
    hold("both at once name both", verdict(1000, 0, 86, False) == ["room", "objects"])
    hold("a cut wanting exactly the room left is not red",
         verdict(957, 43, 43, True) == [])
    hold("objects grown past the bundle is red, since the fetch asks for them all",
         verdict(795, 205, 43, True, by_name=200.0) == ["cheaper"])
    hold("objects exactly the bundle's size is not red",
         verdict(795, 205, 43, True, by_name=144.2) == [])
    # A LOCK THAT DOES NOT READ BY NAME CANNOT BE ASKED THE CHEAPER QUESTION, so the size
    # comparison stays quiet there and the missing `objects` is the whole of the finding.
    hold("no object path means no size finding to make",
         verdict(795, 205, 43, False, by_name=200.0) == ["objects"])
    # THE UNREADABLE CASE IS THE ONE THAT MUST NOT REDDEN, so it is held on the real function.
    hold("no answer from the release takes no reading", reading(Path("/nonexistent")) is None)
    bad = [label for label, got in holds if not got]
    print(f"check_release_room selftest {len(holds) - len(bad)}/{len(holds)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(selftest() if sys.argv[1:] == ["selftest"] else main())
