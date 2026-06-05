#!/usr/bin/env python3
"""Generate a read-only GitHub issue triage report for Humidity Intelligence."""

from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import subprocess
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


DEFAULT_REPOSITORY = "senyo888/humidity-intelligence"
DEFAULT_OUTPUT = ".codex/reports/issue_triage/daily_issue_triage.md"
DEFAULT_LOOKBACK_DAYS = 3
PER_PAGE = 100
CA_BUNDLE_CANDIDATES = (
    "/etc/ssl/cert.pem",
    "/etc/ssl/certs/ca-certificates.crt",
    "/opt/homebrew/etc/openssl@3/cert.pem",
    "/usr/local/etc/openssl@3/cert.pem",
)

TRIAGED_LABEL_HINTS = {
    "accepted",
    "confirmed",
    "duplicate",
    "invalid",
    "triaged",
    "wontfix",
}

UNTRIAGED_LABEL_HINTS = {
    "needs-triage",
    "triage",
    "untriaged",
}

OWNER_DESCRIPTIONS = {
    "Bella": "architecture, roadmap, governance, proposals, community ideas/proposals intake, coherence, documentation truth",
    "Aetherwing": "runtime safety, regression protection, release validation, deterministic lane logic, issue fixes",
    "Aetherbite": "UI ideas, visual polish, brainstorms, experimental UX proposals",
    "Human maintainer/Senyo": "unclear reports, repo policy decisions, community replies, release approval",
}

TEMPLATE_IMPROVEMENT_SUGGESTIONS = (
    "Bug, configuration-help, and feature templates now capture the affected area.",
    "Bug and configuration-help templates ask users to attach the downloaded Home Assistant diagnostics file.",
    "Issues that attach or mention the native Home Assistant diagnostics download are suggested for `has-diagnostics`; bug/support reports without one are suggested for `needs-bundle`.",
    "Bug and configuration-help templates now capture triage signals for safety, release-blocking, regression, duplicate, maintainer-reply, and proposal-review cases.",
    "Bug reports keep fallback version/check fields for users who cannot download diagnostics.",
    "Feature requests now capture proposal scope before implementation work is inferred.",
    "Community Ideas & Proposals form captures problem, affected area, avoided behavior, and user benefit without granting implementation authority.",
    "Submitting an idea does not guarantee implementation, release scheduling, or acceptance.",
    "Community ideas are intake signals only; reactions and comments inform visibility but never approve implementation.",
    "UI Gallery submissions now capture source layout, frontend dependencies, and whether YAML came from HI export or manual editing.",
)


@dataclass(frozen=True)
class AnalyzedIssue:
    """Structured triage output for one GitHub issue."""

    number: str
    title: str
    url: str
    author: str
    created_at: str
    updated_at: str
    current_labels: list[str]
    summary: str
    category: str
    priority: str
    owner: str
    suggested_labels: list[str]
    proposal_required: str
    release_blocker: str
    recommended_action: str
    confidence: str
    signals: list[str]
    diagnostics_bundle: str
    needs_human_decision: bool
    candidate: bool


@dataclass(frozen=True)
class FetchResult:
    """GitHub issue fetch result with enough context for the report."""

    issues: list[dict[str, Any]]
    api_status: str
    rate_limit_note: str
    source_note: str


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_github_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _format_date(value: Any) -> str:
    parsed = _parse_github_datetime(value)
    if parsed is None:
        return "unknown"
    return parsed.strftime("%Y-%m-%d %H:%M UTC")


def _label_names(issue: dict[str, Any]) -> list[str]:
    labels = issue.get("labels")
    if not isinstance(labels, list):
        return []

    names: list[str] = []
    for label in labels:
        if isinstance(label, dict):
            name = label.get("name")
        else:
            name = label
        if isinstance(name, str) and name.strip():
            names.append(name.strip())
    return names


def _normalise_text(*parts: Any) -> str:
    joined = " ".join(str(part or "") for part in parts)
    return re.sub(r"\s+", " ", joined).strip().lower()


def _contains_any(text: str, terms: tuple[str, ...] | set[str]) -> bool:
    return any(term in text for term in terms)


def _body_summary(body: Any, *, max_chars: int = 320) -> str:
    if not isinstance(body, str) or not body.strip():
        return "No issue body was provided."

    lines: list[str] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("###"):
            continue
        if line in {"_No response_", "No response"}:
            continue
        lines.append(re.sub(r"\s+", " ", line))
        if len(" ".join(lines)) >= max_chars:
            break

    summary = " ".join(lines) if lines else body.strip()
    summary = re.sub(r"\s+", " ", summary)
    if len(summary) > max_chars:
        return summary[: max_chars - 1].rstrip() + "..."
    return summary


def _issue_number(issue: dict[str, Any]) -> str:
    number = issue.get("number")
    if isinstance(number, int):
        return str(number)
    if isinstance(number, str) and number.strip():
        return number.strip()
    return "unknown"


def _issue_title(issue: dict[str, Any]) -> str:
    title = issue.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    return "Untitled issue"


def _issue_url(issue: dict[str, Any]) -> str:
    url = issue.get("html_url")
    if isinstance(url, str) and url.strip():
        return url.strip()
    return "unknown"


def _issue_author(issue: dict[str, Any]) -> str:
    user = issue.get("user")
    if isinstance(user, dict):
        login = user.get("login")
        if isinstance(login, str) and login.strip():
            return login.strip()
    return "unknown"


def _issue_signals(
    issue: dict[str, Any],
    *,
    now: datetime,
    lookback_days: int,
    labels_lower: set[str],
) -> tuple[list[str], bool]:
    created = _parse_github_datetime(issue.get("created_at"))
    updated = _parse_github_datetime(issue.get("updated_at"))
    cutoff = now - timedelta(days=lookback_days)

    signals: list[str] = []
    if created is not None and created >= cutoff:
        signals.append("new")
    if updated is not None and updated >= cutoff:
        signals.append("recently updated")
    if not labels_lower:
        signals.append("unlabelled")
    if labels_lower.intersection(UNTRIAGED_LABEL_HINTS):
        signals.append("explicit triage label")

    triaged = bool(labels_lower.intersection(TRIAGED_LABEL_HINTS))
    untriaged = "unlabelled" in signals or "explicit triage label" in signals
    candidate = bool({"new", "recently updated"}.intersection(signals)) or untriaged or not triaged
    return signals or ["open"], candidate


def _detect_category(text: str, labels_lower: set[str]) -> str:
    if "duplicate" in labels_lower or _contains_any(text, ("duplicate", "same as #")):
        return "duplicate"
    if labels_lower.intersection({"community-proposal"}) or _contains_any(
        text,
        (
            "community proposal",
            "community ideas",
            "community ideas & proposals",
            "what problem are you trying to solve",
            "what would you like hi to improve",
            "what should hi avoid doing",
            "community interest",
        ),
    ):
        return "community-proposal"
    if labels_lower.intersection({"question", "support"}) or _contains_any(
        text,
        (
            "config help",
            "configuration help",
            "how do i",
            "how can i",
            "setup help",
            "not sure",
            "unsure",
        ),
    ):
        return "support"
    if labels_lower.intersection({"documentation", "docs"}) or _contains_any(
        text,
        (
            "readme",
            "documentation",
            "docs",
            "changelog",
            "release notes",
            "migration guide",
            "wording",
            "typo",
        ),
    ):
        return "docs"
    if labels_lower.intersection({"governance", "proposal"}) or _contains_any(
        text,
        (
            "governance",
            "proposal",
            "roadmap",
            "bella",
            "aetherwing",
            "aetherbite",
            "aethermite",
            "codex",
            "version governance",
        ),
    ):
        return "governance"
    if labels_lower.intersection({"ui", "dashboard", "ui-gallery"}) or _contains_any(
        text,
        (
            "dashboard",
            "lovelace",
            "card",
            "chip",
            "reason panel",
            "ui ",
            "gallery",
            "visual",
            "frontend",
            "v2_tablet",
            "yaml",
            "orchestration display",
        ),
    ):
        return "UI"
    if _contains_any(
        text,
        (
            "co emergency",
            "runtime",
            "lane",
            "engine",
            "automation",
            "deterministic",
            "control",
            "fan",
            "humidifier",
            "boost",
            "gate",
            "humidity danger",
            "mould",
            "mold",
            "condensation",
            "service",
            "config flow",
            "options flow",
            "threshold",
        ),
    ):
        return "runtime"
    if labels_lower.intersection({"enhancement", "feature"}) or _contains_any(
        text,
        ("feature", "enhancement", "request", "suggestion", "future idea", "add support"),
    ):
        return "enhancement"
    if labels_lower.intersection({"bug"}) or _contains_any(
        text,
        ("bug", "broken", "error", "exception", "traceback", "fails", "failure", "regression"),
    ):
        return "bug"
    return "support"


def _detect_priority(text: str, category: str, labels_lower: set[str]) -> str:
    if labels_lower.intersection({"p0", "critical", "release-blocker"}) or _contains_any(
        text,
        (
            "co emergency",
            "carbon monoxide",
            "safety",
            "data loss",
            "cannot install",
            "broken install",
            "hacs-breaking",
            "hacs breaking",
            "release blocker",
            "release-blocker",
            "blocking release",
        ),
    ):
        return "P0"
    if labels_lower.intersection({"p1"}) or _contains_any(
        text,
        (
            "runtime correctness",
            "false ui state",
            "wrong state",
            "config flow broken",
            "broken config flow",
            "service broken",
            "major docs mismatch",
            "manifest mismatch",
            "hassfest",
            "version mismatch",
        ),
    ):
        return "P1"
    if category in {"runtime", "bug"} or labels_lower.intersection({"bug", "p2"}):
        return "P2"
    if category in {"enhancement", "UI", "docs", "governance", "community-proposal"}:
        return "P3"
    return "Watch"


def _detect_diagnostics_bundle(text: str, category: str) -> str:
    """Detect whether the issue body mentions an attached HI diagnostics file."""

    bundle_relevant = category in {"bug", "runtime", "UI", "support"}
    attachment_context = _contains_any(
        text,
        (
            "attach",
            "attached",
            "upload",
            "uploaded",
            "download",
            "downloaded",
            "file",
            "bundle",
            "diagnostic",
            "diagnostics",
        ),
    )
    native_diagnostics = _contains_any(
        text,
        (
            "home-assistant_humidity_intelligence",
            "home assistant diagnostics",
            "downloaded home assistant diagnostics",
            "downloaded diagnostics",
            "download diagnostics",
            "has-diagnostics",
        ),
    )
    generic_diagnostics_file = _contains_any(
        text,
        (
            "diagnostics file",
            "diagnostic file",
            "diagnostics bundle",
            ".json",
            ".txt",
            ".zip",
        ),
    )
    missing_native_bundle = _contains_any(
        text,
        (
            "unable to download diagnostics",
            "cannot download diagnostics",
            "can't download diagnostics",
            "could not download diagnostics",
            "failed to download diagnostics",
            "no diagnostics file",
            "no diagnostics bundle",
            "diagnostics unavailable",
            "unable to attach diagnostics",
        ),
    )
    local_debug_export = _contains_any(
        text,
        (
            "dump_diagnostics",
            "dump diagnostics",
            "humidity_intelligence_diagnostics.json",
        ),
    )

    if missing_native_bundle:
        return "missing" if bundle_relevant else "not applicable"
    if native_diagnostics and attachment_context:
        return "present"
    if generic_diagnostics_file and attachment_context and not local_debug_export:
        return "present"
    if bundle_relevant:
        return "missing"
    return "not applicable"


def _detect_owner(text: str, category: str, priority: str, confidence: str) -> str:
    if confidence == "low":
        return "Human maintainer/Senyo"
    if priority in {"P0", "P1"} and category in {"runtime", "bug", "UI"}:
        return "Aetherwing"
    if category == "community-proposal":
        return "Bella"
    if category in {"docs", "governance"} or _contains_any(
        text,
        ("architecture", "roadmap", "proposal", "coherence", "documentation truth", "release wording"),
    ):
        return "Bella"
    if category == "runtime" or category == "bug":
        return "Aetherwing"
    if category == "UI" and _contains_any(
        text,
        ("idea", "polish", "visual", "experimental", "future", "orchestration display", "dashboard"),
    ):
        return "Aetherbite"
    if category == "enhancement":
        return "Aetherbite"
    return "Human maintainer/Senyo"


def _proposal_required(text: str, category: str, priority: str) -> str:
    if priority == "P0":
        return "no"
    if category == "community-proposal":
        return "yes"
    if category in {"enhancement", "governance"}:
        return "yes"
    if category == "UI" and _contains_any(text, ("experimental", "future", "strategy", "orchestration")):
        return "yes"
    if _contains_any(
        text,
        (
            "architecture",
            "roadmap",
            "proposal",
            "v2.1",
            "runtime semantics",
            "new lane",
            "new service",
            "release process",
        ),
    ):
        return "yes"
    return "no"


def _release_blocker(text: str, priority: str, labels_lower: set[str]) -> str:
    if priority == "P0" or "release-blocker" in labels_lower:
        return "yes"
    if _contains_any(text, ("release", "hacs", "manifest", "hassfest", "install")):
        return "unknown" if priority in {"P1", "P2", "Watch"} else "no"
    return "no"


def _suggested_labels(
    *,
    category: str,
    priority: str,
    labels_lower: set[str],
    proposal_required: str,
    release_blocker: str,
    diagnostics_bundle: str,
) -> list[str]:
    labels: list[str] = []
    if not labels_lower:
        labels.append("needs-triage")
    if category == "community-proposal":
        labels.append("community-proposal")
    if category != "support":
        labels.append(category.lower())
    if category == "support":
        labels.append("question")
    if priority in {"P0", "P1", "P2", "P3"}:
        labels.append(priority.lower())
    if release_blocker == "yes":
        labels.append("release-blocker")
    if proposal_required == "yes":
        labels.append("proposal-review")
    if diagnostics_bundle == "present":
        labels.append("has-diagnostics")
    elif diagnostics_bundle == "missing":
        labels.append("needs-bundle")

    deduped: list[str] = []
    for label in labels:
        if label not in labels_lower and label not in deduped:
            deduped.append(label)
    return deduped or ["no label change suggested"]


def _confidence(
    issue: dict[str, Any],
    *,
    labels_lower: set[str],
    category: str,
    priority: str,
) -> str:
    has_title = bool(isinstance(issue.get("title"), str) and issue.get("title", "").strip())
    has_body = bool(isinstance(issue.get("body"), str) and issue.get("body", "").strip())
    has_number = isinstance(issue.get("number"), int)

    if not has_title or not has_number:
        return "low"
    if priority in {"P0", "P1"} or labels_lower:
        return "high"
    if has_body and category != "support":
        return "medium"
    return "low" if not has_body else "medium"


def _recommended_action(
    *,
    category: str,
    priority: str,
    owner: str,
    proposal_required: str,
    release_blocker: str,
    confidence: str,
    diagnostics_bundle: str,
) -> str:
    if confidence == "low":
        return "Ask Senyo to request reproduction detail, affected area, and the downloaded Home Assistant diagnostics file before routing."
    if release_blocker == "yes":
        if diagnostics_bundle == "missing":
            return "Create an Aetherwing release-blocker handoff and ask for the Home Assistant diagnostics file in parallel."
        return "Create an Aetherwing release-blocker handoff and validate before any release promotion."
    if category == "community-proposal":
        return "Triage as Community Ideas & Proposals intake for Bella/Senyo; create a formal HI proposal only if warranted and do not treat reactions as approval."
    if proposal_required == "yes":
        return f"Draft a bounded proposal/review note for {owner}; do not implement directly from the issue."
    if category == "duplicate":
        return "Have Senyo confirm duplication manually before closing or linking anything."
    if category == "support":
        if diagnostics_bundle == "missing":
            return "Ask for the downloaded Home Assistant diagnostics file, then prepare a community-facing support reply with redaction reminders."
        return "Have Senyo prepare a community-facing support reply with redaction reminders."
    if diagnostics_bundle == "missing" and category in {"bug", "runtime", "UI"}:
        return f"Ask for the downloaded Home Assistant diagnostics file before routing to {owner}, unless the issue is immediately reproducible."
    if priority in {"P1", "P2"}:
        return f"Route to {owner} for a constrained investigation and regression check."
    return f"Queue for {owner} review when active release-validation work allows."


def analyze_issue(
    issue: dict[str, Any],
    *,
    now: datetime | None = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
) -> AnalyzedIssue:
    """Analyze one GitHub issue without mutating GitHub state."""

    now = now or _utc_now()
    labels = _label_names(issue)
    labels_lower = {label.lower() for label in labels}
    title = _issue_title(issue)
    body = issue.get("body") if isinstance(issue, dict) else ""
    text = _normalise_text(title, body, " ".join(labels))

    category = _detect_category(text, labels_lower)
    priority = _detect_priority(text, category, labels_lower)
    diagnostics_bundle = _detect_diagnostics_bundle(text, category)
    confidence = _confidence(issue, labels_lower=labels_lower, category=category, priority=priority)
    owner = _detect_owner(text, category, priority, confidence)
    proposal_required = _proposal_required(text, category, priority)
    release_blocker = (
        "unknown"
        if confidence == "low" and priority == "Watch"
        else _release_blocker(text, priority, labels_lower)
    )
    suggested_labels = _suggested_labels(
        category=category,
        priority=priority,
        labels_lower=labels_lower,
        proposal_required=proposal_required,
        release_blocker=release_blocker,
        diagnostics_bundle=diagnostics_bundle,
    )
    signals, candidate = _issue_signals(
        issue,
        now=now,
        lookback_days=lookback_days,
        labels_lower=labels_lower,
    )
    if diagnostics_bundle == "present":
        signals.append("diagnostics attached or mentioned")
    elif diagnostics_bundle == "missing":
        signals.append("diagnostics bundle missing")
    needs_human_decision = (
        owner == "Human maintainer/Senyo"
        or confidence == "low"
        or proposal_required == "yes"
        or release_blocker in {"yes", "unknown"}
        or category == "duplicate"
    )

    return AnalyzedIssue(
        number=_issue_number(issue),
        title=title,
        url=_issue_url(issue),
        author=_issue_author(issue),
        created_at=_format_date(issue.get("created_at")),
        updated_at=_format_date(issue.get("updated_at")),
        current_labels=labels,
        summary=_body_summary(body),
        category=category,
        priority=priority,
        owner=owner,
        suggested_labels=suggested_labels,
        proposal_required=proposal_required,
        release_blocker=release_blocker,
        recommended_action=_recommended_action(
            category=category,
            priority=priority,
            owner=owner,
            proposal_required=proposal_required,
            release_blocker=release_blocker,
            confidence=confidence,
            diagnostics_bundle=diagnostics_bundle,
        ),
        confidence=confidence,
        signals=signals,
        diagnostics_bundle=diagnostics_bundle,
        needs_human_decision=needs_human_decision,
        candidate=candidate,
    )


def _markdown_list(items: list[str]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def _issue_anchor(issue: AnalyzedIssue) -> str:
    return f"#{issue.number} {issue.title}"


def _render_issue(issue: AnalyzedIssue) -> str:
    current_labels = ", ".join(issue.current_labels) if issue.current_labels else "none"
    suggested_labels = ", ".join(issue.suggested_labels)
    signals = ", ".join(issue.signals)

    return textwrap.dedent(
        f"""
        ### #{issue.number} {issue.title}

        - URL: {issue.url}
        - Author: {issue.author}
        - Created: {issue.created_at}
        - Updated: {issue.updated_at}
        - Current labels: {current_labels}
        - Triage signals: {signals}
        - Short summary: {issue.summary}
        - Detected category: {issue.category}
        - Suggested priority: {issue.priority}
        - Suggested owner: {issue.owner}
        - Suggested labels: {suggested_labels}
        - Diagnostics bundle: {issue.diagnostics_bundle}
        - Proposal required: {issue.proposal_required}
        - Release blocker: {issue.release_blocker}
        - Recommended action: {issue.recommended_action}
        - Confidence level: {issue.confidence}
        """
    ).strip()


def render_report(
    *,
    repo: str,
    analyzed_issues: list[AnalyzedIssue],
    generated_at: datetime,
    lookback_days: int,
    source_note: str,
    api_status: str,
    rate_limit_note: str,
    total_open_count: int | None = None,
) -> str:
    """Render the full Markdown triage report."""

    report_issues = analyzed_issues
    total_open = total_open_count if total_open_count is not None else len(report_issues)
    if report_issues:
        issue_sections = "\n\n".join(_render_issue(issue) for issue in report_issues)
    else:
        issue_sections = "No new, untriaged, or recently updated open issues matched this run."

    needs_human = [
        f"{_issue_anchor(issue)}: {issue.recommended_action}"
        for issue in report_issues
        if issue.needs_human_decision
    ]
    label_lines = [
        f"{_issue_anchor(issue)}: {', '.join(issue.suggested_labels)}"
        for issue in report_issues
        if issue.suggested_labels != ["no label change suggested"]
    ]

    handoff_lines: list[str] = []
    for owner in OWNER_DESCRIPTIONS:
        owned = [issue for issue in report_issues if issue.owner == owner]
        if not owned:
            continue
        issue_refs = ", ".join(f"#{issue.number} ({issue.priority}, {issue.category})" for issue in owned)
        handoff_lines.append(f"{owner}: {issue_refs}")

    next_actions: list[str] = [
        "Review P0/P1 and release-blocker candidates before any release promotion.",
        "Prioritise issues marked `has-diagnostics` after urgent safety/release blockers because they are faster to inspect.",
        "For bug/support reports marked `needs-bundle`, ask for the downloaded Home Assistant diagnostics file before deep investigation when practical.",
        "Community ideas are intake signals only; use interest/comments for visibility, not approval or release authority.",
        "Apply labels, owner handoffs, assignments, comments, closures, or duplicate links manually only after maintainer review.",
        "Convert community ideas into formal HI proposal or handoff notes only if warranted before implementation.",
    ]
    if not report_issues:
        next_actions.append("No issue handoff is required from this run unless GitHub API status needs investigation.")

    template_suggestions = list(TEMPLATE_IMPROVEMENT_SUGGESTIONS)

    generated = generated_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sections = [
        "# Report-Only GitHub Issue Triage",
        "",
        f"Generated: {generated}",
        f"Repository: {repo}",
        "Mode: report-only / dry-run",
        f"Lookback window: {lookback_days} day(s)",
        f"Source: {source_note}",
        f"API status: {api_status}",
        f"Rate limit: {rate_limit_note}",
        f"Open issues fetched: {total_open}",
        f"Triage candidates reported: {len(report_issues)}",
        "",
        "No GitHub issues were closed, edited, labelled, assigned, or commented on.",
        "This report is advisory governance/support output only and does not change",
        "Humidity Intelligence runtime, Home Assistant services, generated UI,",
        "integration metadata, release state, or public issue state.",
        "",
        "## Triage candidates",
        "",
        issue_sections,
        "",
        "## Recommended next actions",
        "",
        _markdown_list(next_actions),
        "",
        "## Needs human decision",
        "",
        _markdown_list(needs_human),
        "",
        "## Potential labels to apply manually",
        "",
        _markdown_list(label_lines),
        "",
        "## Possible owner handoff",
        "",
        _markdown_list(handoff_lines),
        "",
        "## Owner mapping",
        "",
        f"- Bella: {OWNER_DESCRIPTIONS['Bella']}",
        f"- Aetherwing: {OWNER_DESCRIPTIONS['Aetherwing']}",
        f"- Aetherbite: {OWNER_DESCRIPTIONS['Aetherbite']}",
        f"- Human maintainer/Senyo: {OWNER_DESCRIPTIONS['Human maintainer/Senyo']}",
        "",
        "## Issue template signal notes",
        "",
        _markdown_list(template_suggestions),
        "",
        "## Diagnostics bundle guidance",
        "",
        "- `has-diagnostics`: issue body mentions or links the downloaded native Home Assistant diagnostics file.",
        "- `needs-bundle`: bug, runtime, UI, or support issue lacks an attached or mentioned native diagnostics file.",
        "- `dump_diagnostics` exports are local maintainer/debug output and are not treated as the safe GitHub attachment path.",
        "- Suggested labels are advisory only; this script does not create, apply, or remove labels.",
    ]
    return "\n".join(sections).strip() + "\n"


def _repo_from_git_remote() -> str | None:
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None

    remote = result.stdout.strip()
    patterns = (
        r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
        r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
    )
    for pattern in patterns:
        match = re.search(pattern, remote)
        if match:
            return f"{match.group('owner')}/{match.group('repo')}"
    return None


def _resolve_repo(explicit_repo: str | None) -> str:
    return explicit_repo or os.getenv("GITHUB_REPOSITORY") or _repo_from_git_remote() or DEFAULT_REPOSITORY


def fetch_open_issues(repo: str, *, max_pages: int, token: str | None) -> FetchResult:
    """Fetch open GitHub issues using read-only REST API calls."""

    issues: list[dict[str, Any]] = []
    rate_limit_note = "not reported"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "humidity-intelligence-codex-issue-triage",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    for page in range(1, max_pages + 1):
        query = urllib.parse.urlencode(
            {
                "state": "open",
                "per_page": str(PER_PAGE),
                "sort": "updated",
                "direction": "desc",
                "page": str(page),
            }
        )
        url = f"https://api.github.com/repos/{repo}/issues?{query}"
        request = urllib.request.Request(url, headers=headers, method="GET")
        parsed_url = urllib.parse.urlparse(request.full_url)
        if parsed_url.scheme != "https":
            raise ValueError(f"Refusing non-HTTPS URL: {parsed_url.scheme}")

        try:
            # URL scheme is validated as HTTPS above.
            with urllib.request.urlopen(  # nosec B310
                request,
                timeout=20,
                context=_ssl_context(),
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
                remaining = response.headers.get("X-RateLimit-Remaining")
                reset = response.headers.get("X-RateLimit-Reset")
                if remaining is not None:
                    rate_limit_note = f"remaining={remaining}"
                    if reset and reset.isdigit():
                        reset_at = datetime.fromtimestamp(int(reset), tz=timezone.utc)
                        rate_limit_note += f", resets={reset_at.strftime('%Y-%m-%d %H:%M UTC')}"
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            return FetchResult(
                issues=issues,
                api_status=f"error: GitHub API HTTP {exc.code}: {detail[:240]}",
                rate_limit_note=rate_limit_note,
                source_note="GitHub REST API",
            )
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            return FetchResult(
                issues=issues,
                api_status=f"error: {exc}",
                rate_limit_note=rate_limit_note,
                source_note="GitHub REST API",
            )

        if not isinstance(payload, list):
            return FetchResult(
                issues=issues,
                api_status="error: GitHub API returned a non-list payload",
                rate_limit_note=rate_limit_note,
                source_note="GitHub REST API",
            )

        page_issues = [item for item in payload if isinstance(item, dict) and "pull_request" not in item]
        issues.extend(page_issues)

        if len(payload) < PER_PAGE:
            break

    auth_note = "authenticated" if token else "unauthenticated"
    return FetchResult(
        issues=issues,
        api_status=f"ok ({auth_note})",
        rate_limit_note=rate_limit_note,
        source_note="GitHub REST API",
    )


def _ssl_context() -> ssl.SSLContext:
    """Create a verifying SSL context, using common local CA bundles if needed."""

    env_cert_file = os.getenv("SSL_CERT_FILE")
    candidates = (env_cert_file,) if env_cert_file else ()
    for candidate in (*candidates, *CA_BUNDLE_CANDIDATES):
        if candidate and Path(candidate).exists():
            return ssl.create_default_context(cafile=candidate)
    return ssl.create_default_context()


def _load_issues_from_json(path: Path) -> FetchResult:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return FetchResult(
            issues=[],
            api_status=f"error: could not read input JSON: {exc}",
            rate_limit_note="not checked",
            source_note=f"local JSON fixture: {path}",
        )

    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        payload = payload["items"]
    if not isinstance(payload, list):
        return FetchResult(
            issues=[],
            api_status="error: input JSON must be a list of GitHub issue objects or an object with items",
            rate_limit_note="not checked",
            source_note=f"local JSON fixture: {path}",
        )

    issues = [item for item in payload if isinstance(item, dict) and "pull_request" not in item]
    return FetchResult(
        issues=issues,
        api_status="offline fixture",
        rate_limit_note="not checked",
        source_note=f"local JSON fixture: {path}",
    )


def _write_report(path: Path, report: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a read-only Humidity Intelligence GitHub issue triage report."
    )
    parser.add_argument(
        "--repo",
        help="GitHub repository in owner/name form. Defaults to GITHUB_REPOSITORY, git origin, then senyo888/humidity-intelligence.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Markdown report path. Default: {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=DEFAULT_LOOKBACK_DAYS,
        help=f"New/recently-updated window. Default: {DEFAULT_LOOKBACK_DAYS}",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=3,
        help="Maximum GitHub API issue pages to fetch. Default: 3",
    )
    parser.add_argument(
        "--include-all-open",
        action="store_true",
        help="Report every fetched open issue instead of only new, untriaged, or recently updated candidates.",
    )
    parser.add_argument(
        "--input-json",
        type=Path,
        help="Read a local GitHub issues JSON fixture instead of calling the GitHub API.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Explicit no-op compatibility flag. The script is always report-only and never mutates GitHub.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    now = _utc_now()
    repo = _resolve_repo(args.repo)
    lookback_days = max(0, args.lookback_days)
    max_pages = max(1, args.max_pages)

    if args.input_json:
        fetch_result = _load_issues_from_json(args.input_json)
    else:
        fetch_result = fetch_open_issues(
            repo,
            max_pages=max_pages,
            token=os.getenv("GITHUB_TOKEN"),
        )

    analyzed_all: list[AnalyzedIssue] = []
    for issue in fetch_result.issues:
        try:
            analyzed_all.append(analyze_issue(issue, now=now, lookback_days=lookback_days))
        except Exception as exc:  # Keep one malformed issue from killing the report.
            fallback = {
                "title": f"Malformed issue payload: {exc}",
                "body": "The script could not classify this issue payload. Senyo should inspect it manually.",
            }
            analyzed_all.append(analyze_issue(fallback, now=now, lookback_days=lookback_days))

    reported = analyzed_all if args.include_all_open else [issue for issue in analyzed_all if issue.candidate]
    report = render_report(
        repo=repo,
        analyzed_issues=reported,
        generated_at=now,
        lookback_days=lookback_days,
        source_note=fetch_result.source_note,
        api_status=fetch_result.api_status,
        rate_limit_note=fetch_result.rate_limit_note,
        total_open_count=len(fetch_result.issues),
    )

    output_path = Path(args.output)
    try:
        _write_report(output_path, report)
    except OSError as exc:
        print(f"Could not write triage report: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote report-only issue triage: {output_path}")
    print("No GitHub issues were closed, edited, labelled, assigned, or commented on.")
    if fetch_result.api_status.startswith("error:"):
        print(fetch_result.api_status, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
