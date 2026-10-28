#!/usr/bin/env python3
"""Manually check the app's pure experience models without a simulator."""

from pathlib import Path
import subprocess
import tempfile


def main() -> None:
    checks = Path(__file__).resolve().parent
    core = checks.parent / "SodaMachine" / "Core"
    sources = [
        core / "Navigation.swift",
        core / "EditSessions.swift",
        core / "Management.swift",
        core / "MachineModel.swift",
        core / "Firmware.swift",
        checks / "NavigationChecks.swift",
        checks / "FirmwareChecks.swift",
        checks / "ExperienceChecks.swift",
    ]
    with tempfile.TemporaryDirectory(prefix="soda-experience-") as temporary:
        executable = Path(temporary) / "experience-checks"
        subprocess.run(
            [
                "swiftc",
                "-parse-as-library",
                "-default-isolation",
                "MainActor",
                *map(str, sources),
                "-o",
                str(executable),
            ],
            check=True,
        )
        subprocess.run([str(executable)], check=True)


if __name__ == "__main__":
    main()
