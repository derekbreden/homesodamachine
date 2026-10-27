#!/usr/bin/env python3
"""Manually render the proposal's screen/viewport matrix with native SwiftUI.

Requires Xcode, XcodeGen, and an installed iOS 18.5 Simulator runtime.
No production app, connected accessory, or physical device is used.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
BUNDLE = "com.derekbreden.SodaMachineStudy"
NAME = "Soda layout study"


def run(*args, capture=False, check=True):
    return subprocess.run(args, check=check, text=True, capture_output=capture)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true", help="Render home, sound and crop at three sizes")
    parser.add_argument("--routes", help="Comma-separated route names for a focused capture")
    options = parser.parse_args()
    device_groups = json.loads(run("xcrun", "simctl", "list", "devices", "available", "-j", capture=True).stdout)["devices"]
    device = next((d for group in device_groups.values() for d in group if d["name"] == NAME), None)
    if device is None:
        identifier = run("xcrun", "simctl", "create", NAME, "com.apple.CoreSimulator.SimDeviceType.iPhone-16-Pro",
                         "com.apple.CoreSimulator.SimRuntime.iOS-18-5", capture=True).stdout.strip()
    else:
        identifier = device["udid"]
    run("xcrun", "simctl", "bootstatus", identifier, "-b")
    run("xcodegen", "generate", "--spec", str(HERE / "project.yml"))
    build = Path(tempfile.gettempdir()) / "hsm-adaptive-study-build"
    run("xcodebuild", "-project", str(HERE / "SodaMachineStudy.xcodeproj"), "-scheme", "SodaMachineStudy",
        "-destination", f"platform=iOS Simulator,id={identifier}", "-configuration", "Debug",
        "-derivedDataPath", str(build), "build", "CODE_SIGNING_ALLOWED=NO", "-quiet")
    run("xcrun", "simctl", "terminate", identifier, BUNDLE, check=False, capture=True)
    run("xcrun", "simctl", "install", identifier, str(build / "Build/Products/Debug-iphonesimulator/SodaMachineStudy.app"))
    data = Path(run("xcrun", "simctl", "get_app_container", identifier, BUNDLE, "data", capture=True).stdout.strip())
    source = data / "Documents/renders"
    # This is the study app's own generated directory.
    if source.exists():
        shutil.rmtree(source)
    run("xcrun", "simctl", "launch", identifier, BUNDLE, "--render", *(["--quick"] if options.quick else []),
        *(["--routes", options.routes] if options.routes else []))
    deadline = time.monotonic() + 180
    while not (source / "COMPLETE.txt").exists():
        if time.monotonic() > deadline:
            raise RuntimeError("The study did not finish rendering within three minutes")
        time.sleep(0.5)
    destination = HERE / "renders"
    old_manifest = json.loads((destination / "manifest.json").read_text()) if (destination / "manifest.json").exists() else []
    captured = json.loads((source / "manifest.json").read_text())
    shutil.copytree(source, destination, dirs_exist_ok=True)
    merged = {item["file"]: item for item in old_manifest}
    merged.update({item["file"]: item for item in captured})
    (destination / "manifest.json").write_text(json.dumps(list(merged.values()), indent=2) + "\n")
    print(f"Rendered {len(captured)} native screens to {destination}; {len(merged)} total captures")


if __name__ == "__main__":
    main()
