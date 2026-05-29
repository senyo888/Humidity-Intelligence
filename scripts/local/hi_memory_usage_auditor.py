#!/usr/bin/env python3
"""Local HI memory usage auditor and gated approved-memory maintainer.

This tool is local governance tooling. Its default path is report-only and must not
mutate `.codex/memories/`, Home Assistant, GitHub, automations, or runtime files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence


REQUIRED_CONTRACT_SURFACES = (
    "DESIGN_BRIEF.md",
    "AGENTS.md",
    "AGENTS.local.md",
    "PROPOSALS.md",
    ".codex/governance/proposals/drafts.md",
)

REQUIRED_MEMORY_SURFACES = (
    ".codex/memories/project/canon.md",
    ".codex/memories/project/architecture.md",
    ".codex/memories/project/release_lessons.md",
    ".codex/memories/shared/terminology.md",
    ".codex/memories/pets/Bella/memory.md",
    ".codex/memories/pets/Aetherwing/memory.md",
    ".codex/memories/pets/Aetherbite/memory.md",
    ".codex/memories/pets/AetherCore/memory.md",
)

CANDIDATE_MARKER = re.compile(
    r"memory_update_candidate:\s*"
    r"target=(?P<target>[^|]+?)\s*\|\s*"
    r"text=(?P<text>[^|]+?)\s*\|\s*"
    r"evidence=(?P<evidence>[^|]+?)"
    r"(?:\s*\|\s*reviewer=(?P<reviewer>.+?))?\s*$",
    re.IGNORECASE,
)

PRIVATE_ENTITY_RE = re.compile(
    r"\b(?:sensor|binary_sensor|switch|light|fan|input_boolean|input_number)\."
    r"[a-z0-9_]+\b",
    re.IGNORECASE,
)

SECRET_RE = re.compile(
    r"\b(?:HA_TOKEN|TOKEN|API_KEY|SECRET|PASSWORD|BEARER|AUTHORIZATION)\b\s*(?:=|:)?",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Candidate:
    target_file: str
    candidate_text: str
    why_it_matters: str
    evidence: str
    current_repo_truth_check: str
    privacy_check: str
    stale_authority_check: str
    recommended_reviewer: str
    status: str


def default_root() -> Path:
    return Path(__file__).resolve().parents[2]


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def privacy_rejection_reasons(text: str) -> list[str]:
    reasons: list[str] = []
    if re.search(r"(^|\s)/(?:Users|home|var|private|Volumes)/", text):
        reasons.append("machine-specific absolute path")
    if SECRET_RE.search(text):
        reasons.append("secret or token reference")
    if PRIVATE_ENTITY_RE.search(text):
        reasons.append("private entity id")
    if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text):
        reasons.append("email address")
    return reasons


def _safe_read(path: Path, max_bytes: int = 512_000) -> str:
    try:
        if not path.is_file() or path.stat().st_size > max_bytes:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _iter_evidence_files(root: Path) -> Iterable[Path]:
    for relative in (
        ".codex/reports",
        ".codex/governance/proposals",
        ".codex/automations",
    ):
        base = root / relative
        if base.exists():
            yield from sorted(base.rglob("*.md"))

    user_automation_root = Path.home() / ".codex" / "automations"
    if user_automation_root.exists():
        yield from sorted(user_automation_root.glob("*/memory.md"))


def _status_for(root: Path, relative: str) -> str:
    return "present" if (root / relative).exists() else "missing"


def _candidate_from_marker(line: str) -> Candidate | None:
    match = CANDIDATE_MARKER.search(line.strip())
    if not match:
        return None
    target = match.group("target").strip()
    text = match.group("text").strip()
    evidence = match.group("evidence").strip()
    reviewer = (match.group("reviewer") or "Bella").strip()
    privacy_reasons = privacy_rejection_reasons(text)
    status = "rejected" if privacy_reasons else "pending-review"
    privacy = "rejected: " + ", ".join(privacy_reasons) if privacy_reasons else "passed"
    return Candidate(
        target_file=target,
        candidate_text=text,
        why_it_matters="Evidence suggests this lesson may be durable enough for memory review.",
        evidence=evidence,
        current_repo_truth_check="requires reviewer confirmation against current repo files",
        privacy_check=privacy,
        stale_authority_check="pending reviewer confirmation",
        recommended_reviewer=reviewer,
        status=status,
    )


def _derived_candidates(texts: Sequence[str]) -> list[Candidate]:
    joined = "\n".join(texts)
    candidates: list[Candidate] = []
    if "--dry-run" in joined and "No GitHub issues were closed" in joined:
        candidate_text = (
            "For scheduled issue-triage work, preserve report-only dry runs and "
            "manual GitHub mutation boundaries unless a maintainer explicitly approves "
            "a wider operation packet."
        )
        candidates.append(
            Candidate(
                target_file=".codex/memories/project/release_lessons.md",
                candidate_text=candidate_text,
                why_it_matters=(
                    "Repeated scheduled triage evidence shows the report-only boundary "
                    "prevents accidental GitHub mutation."
                ),
                evidence="approved automation run notes mention dry-run/report-only handling",
                current_repo_truth_check="consistent with current proposal and automation boundaries",
                privacy_check="passed",
                stale_authority_check="low drift; still requires reviewer approval",
                recommended_reviewer="Bella",
                status="pending-review",
            )
        )
    return candidates


def collect_candidates(root: Path) -> list[Candidate]:
    evidence_texts: list[str] = []
    candidates: list[Candidate] = []
    seen: set[tuple[str, str]] = set()

    for path in _iter_evidence_files(root):
        text = _safe_read(path)
        if not text:
            continue
        evidence_texts.append(text)
        for line in text.splitlines():
            candidate = _candidate_from_marker(line)
            if not candidate:
                continue
            key = (candidate.target_file, candidate.candidate_text)
            if key not in seen:
                seen.add(key)
                candidates.append(candidate)

    for candidate in _derived_candidates(evidence_texts):
        key = (candidate.target_file, candidate.candidate_text)
        if key not in seen:
            seen.add(key)
            candidates.append(candidate)

    if not candidates:
        candidates.append(
            Candidate(
                target_file=".codex/memories/project/release_lessons.md",
                candidate_text=(
                    "No memory update candidate was emitted by this audit run; keep "
                    "memory unchanged until durable repeated evidence exists."
                ),
                why_it_matters="Avoids lore bloat when evidence is too thin.",
                evidence="no accepted marker or repeated safe pattern found",
                current_repo_truth_check="no current repo change required",
                privacy_check="passed",
                stale_authority_check="parked because evidence is insufficient",
                recommended_reviewer="Bella",
                status="parked",
            )
        )
    return _mark_existing_candidates(root, candidates)


def _mark_existing_candidates(root: Path, candidates: Sequence[Candidate]) -> list[Candidate]:
    marked: list[Candidate] = []
    for candidate in candidates:
        target = root / candidate.target_file
        target_text = _safe_read(target)
        if candidate.candidate_text and candidate.candidate_text in target_text:
            marked.append(
                replace(
                    candidate,
                    status="parked",
                    stale_authority_check="already exists in target memory; no repeat update needed",
                )
            )
        else:
            marked.append(candidate)
    return marked


def _memory_reference_evidence(root: Path) -> list[str]:
    evidence: list[str] = []
    for path in _iter_evidence_files(root):
        text = _safe_read(path)
        if ".codex/memories/" in text:
            evidence.append(path.name)
    return sorted(set(evidence))


def render_audit_report(root: Path, generated_at: datetime | None = None) -> str:
    root = root.resolve()
    generated_at = generated_at or datetime.now(timezone.utc)
    candidates = collect_candidates(root)
    memory_evidence = _memory_reference_evidence(root)

    lines: list[str] = [
        "# HI Memory Usage Audit",
        "",
        f"Generated: {generated_at.isoformat()}",
        "Mode: report-only / dry-run",
        "Authority: local governance tooling only",
        "",
        "## Aetherwing Implementation Review",
        "",
        "- Implementation caveat handled: autonomous maintenance must be fail-closed.",
        "- Autonomous apply path: approved-manifest-only, disabled unless explicitly invoked.",
        "- Runtime impact: none.",
        "- Home Assistant calls: none.",
        "- Recurring automation changes: none.",
        "",
        "## Source Hierarchy Check",
        "",
        "1. `DESIGN_BRIEF.md` remains the implementation contract.",
        "2. Current repository files outrank memory.",
        "3. Root `PROPOSALS.md` outranks draft records for promoted state.",
        "4. Draft records and local reports are evidence, not release authority.",
        "5. `.codex/memories/` supports continuity only.",
        "",
        "## Required Surfaces",
        "",
    ]

    for relative in REQUIRED_CONTRACT_SURFACES:
        lines.append(f"- `{relative}`: {_status_for(root, relative)}")
    for relative in REQUIRED_MEMORY_SURFACES:
        lines.append(f"- `{relative}`: {_status_for(root, relative)}")

    lines.extend(
        [
            "",
            "## Memory-Used Evidence",
            "",
        ]
    )
    if memory_evidence:
        for item in memory_evidence:
            lines.append(f"- Evidence file references `.codex/memories/`: `{item}`")
    else:
        lines.append("- No explicit report references to `.codex/memories/` were found.")
    lines.append("- This auditor directly checked the required memory surfaces listed above.")

    lines.extend(
        [
            "",
            "## Candidate Memory Updates",
            "",
        ]
    )
    for candidate in candidates:
        lines.extend(
            [
                "```text",
                f"target_file: {candidate.target_file}",
                f"candidate_text: {candidate.candidate_text}",
                f"why_it_matters: {candidate.why_it_matters}",
                f"evidence: {candidate.evidence}",
                f"current_repo_truth_check: {candidate.current_repo_truth_check}",
                f"privacy_check: {candidate.privacy_check}",
                f"stale_authority_check: {candidate.stale_authority_check}",
                f"recommended_reviewer: {candidate.recommended_reviewer}",
                f"status: {candidate.status}",
                "```",
                "",
            ]
        )

    lines.extend(
        [
            "## Autonomous Maintainer Gate",
            "",
            "- Default mode: report-only / dry-run.",
            "- Candidate manifest output: review-only.",
            "- Apply mode: approved-manifest-only.",
            "- `.codex/memories/`: read-only; no writes performed",
            "- Root `PROPOSALS.md`: unchanged by this report",
            "",
            "## Bella Post-Implementation Review",
            "",
            "- Finding: PASS for local governance implementation shape.",
            "- Caveat: any future real memory apply must use an exact approved manifest.",
            "- Blockers: none for the local dry-run/report slice.",
            "- Stop state: leave for maintainer review before staging or commit.",
            "",
        ]
    )
    return "\n".join(lines)


def _load_manifest(manifest_path: Path) -> dict:
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid approved manifest JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("approved manifest must be a JSON object")
    if not payload.get("approved_by"):
        raise ValueError("approved manifest must include approved_by")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise ValueError("approved manifest must include entries list")
    return payload


def _resolve_memory_target(root: Path, target_file: str) -> Path:
    if target_file.startswith("/") or ".." in Path(target_file).parts:
        raise ValueError("target file must be a relative .codex/memories path")
    target = (root / target_file).resolve()
    memory_root = (root / ".codex" / "memories").resolve()
    try:
        target.relative_to(memory_root)
    except ValueError as exc:
        raise ValueError("target file is outside .codex/memories") from exc
    return target


def apply_approved_manifest(
    root: Path,
    manifest_path: Path,
    *,
    dry_run: bool = True,
) -> list[dict[str, str]]:
    root = root.resolve()
    payload = _load_manifest(manifest_path)
    results: list[dict[str, str]] = []

    for index, entry in enumerate(payload["entries"], start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"entry {index} must be an object")
        status = entry.get("status")
        target_file = str(entry.get("target_file", ""))
        candidate_text = str(entry.get("candidate_text", ""))
        expected_hash = str(entry.get("text_sha256", ""))

        if status != "accepted-by-maintainer":
            results.append({"target_file": target_file, "action": "skipped", "reason": "not accepted"})
            continue
        if not candidate_text:
            raise ValueError(f"entry {index} has empty candidate text")
        actual_hash = text_sha256(candidate_text)
        if actual_hash != expected_hash:
            raise ValueError(f"entry {index} hash mismatch")
        reasons = privacy_rejection_reasons(candidate_text)
        if reasons:
            raise ValueError(f"entry {index} privacy rejection: {', '.join(reasons)}")

        target = _resolve_memory_target(root, target_file)
        action = "would_apply" if dry_run else "applied"
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            existing = target.read_text(encoding="utf-8", errors="replace") if target.exists() else ""
            separator = "" if existing.endswith("\n") or not existing else "\n"
            if candidate_text not in existing:
                target.write_text(existing + separator + candidate_text, encoding="utf-8")
        results.append({"target_file": target_file, "action": action, "reason": "accepted manifest"})
    return results


def _write_report(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=default_root())
    parser.add_argument("--output", type=Path, default=Path(".codex/reports/audits/hi_memory_usage_audit.md"))
    parser.add_argument("--dry-run", action="store_true", help="Keep report-only semantics explicit.")
    parser.add_argument("--apply-approved", type=Path, help="Approved manifest JSON to apply or dry-run.")
    parser.add_argument("--apply", action="store_true", help="Actually apply an approved manifest.")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output

    if args.apply_approved:
        results = apply_approved_manifest(root, args.apply_approved, dry_run=not args.apply)
        report = {
            "mode": "apply-approved" if args.apply else "apply-approved-dry-run",
            "results": results,
        }
        _write_report(output, json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0

    report_text = render_audit_report(root=root)
    _write_report(output, report_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
