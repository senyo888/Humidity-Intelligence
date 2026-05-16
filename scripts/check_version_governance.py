#!/usr/bin/env python3
"""Validate Humidity Intelligence branch/version release governance."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


VERSION_PATTERN = re.compile(
    r"^(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<label>beta|rc)\.(?P<number>[1-9]\d*))?$"
)

TESTING_BRANCH_PREFIXES = (
    "Bella/",
    "codex/",
    "dev/",
    "feature/",
    "fix/",
    "patch/",
    "test/",
)


def _git_branch() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def _active_branch() -> str:
    return (
        os.getenv("VERSION_GOVERNANCE_BRANCH")
        or os.getenv("GITHUB_BASE_REF")
        or os.getenv("GITHUB_REF_NAME")
        or _git_branch()
    )


def _manifest_version() -> str:
    data = json.loads(Path("manifest.json").read_text(encoding="utf-8"))
    version = data.get("version")
    if not isinstance(version, str) or not version:
        raise SystemExit("manifest.json must define a non-empty string version.")
    return version


def _is_stable_branch(branch: str) -> bool:
    return branch == "main" or branch.startswith("release/")


def _is_testing_branch(branch: str) -> bool:
    return branch == "senyo888-patch-1" or branch.startswith(TESTING_BRANCH_PREFIXES)


def main() -> int:
    branch = _active_branch()
    version = _manifest_version()
    match = VERSION_PATTERN.fullmatch(version)

    if not match:
        print(
            "Invalid manifest version. Use MAJOR.MINOR.PATCH, "
            "MAJOR.MINOR.PATCH-beta.N, or MAJOR.MINOR.PATCH-rc.N.",
            file=sys.stderr,
        )
        print(f"Branch: {branch}", file=sys.stderr)
        print(f"Version: {version}", file=sys.stderr)
        return 1

    label = match.group("label")

    if _is_stable_branch(branch) and label:
        print(
            f"Stable branch '{branch}' must not use prerelease version '{version}'.",
            file=sys.stderr,
        )
        return 1

    if branch == "develop" and label not in {"beta", "rc"}:
        print(
            f"Develop branch must use beta or rc versioning, not '{version}'.",
            file=sys.stderr,
        )
        return 1

    if branch == "senyo888-patch-1" and label != "beta":
        print(
            f"Testing branch 'senyo888-patch-1' must use beta versioning, not '{version}'.",
            file=sys.stderr,
        )
        return 1

    if _is_testing_branch(branch) and not label:
        print(
            f"Testing branch '{branch}' must not carry stable version '{version}'.",
            file=sys.stderr,
        )
        return 1

    state = "stable" if not label else label
    print(f"Version governance OK: branch={branch} version={version} state={state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
