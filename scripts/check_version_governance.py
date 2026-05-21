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
RELEASE_BRANCH_PATTERN = re.compile(
    r"^v(?P<version>(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*))$"
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

STABLE_ALLOWED_BRANCHES = {"senyo888-patch-1", "develop", "main"}


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


def _is_testing_branch(branch: str) -> bool:
    return branch.startswith(TESTING_BRANCH_PREFIXES)


def _release_branch_version(branch: str) -> str | None:
    match = RELEASE_BRANCH_PATTERN.fullmatch(branch)
    if not match:
        return None
    return match.group("version")


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
    release_branch_version = _release_branch_version(branch)

    if release_branch_version and version != release_branch_version:
        print(
            f"Release branch '{branch}' must carry matching stable version "
            f"'{release_branch_version}', not '{version}'.",
            file=sys.stderr,
        )
        return 1

    if branch == "main" and label:
        print(
            f"Main branch must use stable versioning, not '{version}'.",
            file=sys.stderr,
        )
        return 1

    if branch == "develop" and label == "beta":
        print(
            f"Develop branch must use rc or stable versioning, not '{version}'.",
            file=sys.stderr,
        )
        return 1

    if not label and branch not in STABLE_ALLOWED_BRANCHES and not release_branch_version:
        print(
            f"Branch '{branch}' must not carry stable version '{version}'.",
            file=sys.stderr,
        )
        return 1

    if _is_testing_branch(branch) and not label:
        print(
            f"Testing branch '{branch}' must use beta or rc versioning, not '{version}'.",
            file=sys.stderr,
        )
        return 1

    state = "stable" if not label else label
    print(f"Version governance OK: branch={branch} version={version} state={state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
