#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if ! command -v gitleaks >/dev/null 2>&1; then
  cat >&2 <<'EOF'
gitleaks is required for the local secret scan.

Install it from:
https://github.com/gitleaks/gitleaks/releases

Then rerun:
scripts/security/scan_secrets.sh
EOF
  exit 127
fi

mode="${1:-tracked}"

case "$mode" in
  tracked)
    tmp_dir="$(mktemp -d)"
    trap 'rm -rf "$tmp_dir"' EXIT
    while IFS= read -r -d '' path; do
      [ -f "$path" ] || continue
      mkdir -p "$tmp_dir/$(dirname "$path")"
      cp -p "$path" "$tmp_dir/$path"
    done < <(git ls-files -z)
    gitleaks dir --redact --no-banner --config "$ROOT_DIR/.gitleaks.toml" "$tmp_dir"
    ;;
  full-history)
    gitleaks git --redact --no-banner --config .gitleaks.toml .
    ;;
  *)
    cat >&2 <<'EOF'
Usage: scripts/security/scan_secrets.sh [tracked|full-history]

tracked       Scan tracked repository files without reading ignored local credentials.
full-history  Scan git history before enabling Gitleaks as a required branch check.

All output must stay redacted. If a real secret is found, rotate the credential before
claiming remediation; deleting it from git history is not enough.
EOF
    exit 2
    ;;
esac
