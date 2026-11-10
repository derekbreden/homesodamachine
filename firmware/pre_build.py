"""PlatformIO passes its SCons build context to the native firmware preparer."""
Import("env")

import os
import subprocess

subprocess.run(
    [
        os.environ.get("HSM_PERIPHERAL_BIN", "hsm-peripheral"),
        "--root",
        env.subst("$PROJECT_DIR"),
        "firmware-pre-build",
        "--environment",
        env["PIOENV"],
        "--build-dir",
        env.subst("$BUILD_DIR"),
    ],
    check=True,
)
