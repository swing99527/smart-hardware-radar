import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE_HEALTH_FILE = ROOT / "data" / "source_health.json"
DEFAULT_REQUIRED_PREFIXES = ("GitHub", "Reddit")
OK_STATUSES = {"ok", "fetch_ok_zero_items"}


def parse_iso(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def required_prefixes_from_env():
    raw = os.getenv("SOURCE_HEALTH_REQUIRED_PREFIXES", ",".join(DEFAULT_REQUIRED_PREFIXES))
    return tuple(prefix.strip() for prefix in raw.split(",") if prefix.strip())


def is_required_source(source, required_prefixes):
    name = source.get("source_name", "")
    return any(name.startswith(prefix) for prefix in required_prefixes)


def evaluate_source_health(health_doc, required_prefixes=None, max_stale_hours=48):
    required_prefixes = required_prefixes or DEFAULT_REQUIRED_PREFIXES
    now = datetime.now(timezone.utc)
    failures = []
    warnings = []
    required_count = 0

    for source in health_doc.get("sources", []):
        if not is_required_source(source, required_prefixes):
            continue
        required_count += 1
        status = source.get("status")
        name = source.get("source_name", "unknown")
        auth_mode = source.get("auth_mode", "none")
        last_success_at = parse_iso(source.get("last_success_at"))
        rate_limit = source.get("rate_limit") or {}

        if status not in OK_STATUSES:
            failures.append(
                {
                    "source_name": name,
                    "status": status,
                    "http_status": source.get("http_status"),
                    "auth_mode": auth_mode,
                    "error": source.get("error"),
                    "last_success_at": source.get("last_success_at"),
                }
            )
            continue

        if not last_success_at:
            warnings.append(
                {
                    "source_name": name,
                    "status": status,
                    "auth_mode": auth_mode,
                    "warning": "no_last_success_at",
                }
            )
            continue

        age_hours = (now - last_success_at).total_seconds() / 3600
        if age_hours > max_stale_hours:
            warnings.append(
                {
                    "source_name": name,
                    "status": status,
                    "auth_mode": auth_mode,
                    "warning": "stale_last_success_at",
                    "age_hours": round(age_hours, 1),
                }
            )

        remaining = rate_limit.get("x-ratelimit-remaining")
        if remaining == "0":
            warnings.append(
                {
                    "source_name": name,
                    "status": status,
                    "auth_mode": auth_mode,
                    "warning": "rate_limit_remaining_zero",
                    "rate_limit": rate_limit,
                }
            )

    return {
        "required_count": required_count,
        "failure_count": len(failures),
        "warning_count": len(warnings),
        "failures": failures,
        "warnings": warnings,
    }


def load_health(path):
    if not path.exists():
        return {"sources": []}
    return json.loads(path.read_text())


def print_report(report):
    print(
        f"Source health: {report['required_count']} required sources, "
        f"{report['failure_count']} failures, {report['warning_count']} warnings"
    )
    for failure in report["failures"]:
        print(
            "  [FAIL] "
            f"{failure['source_name']} status={failure['status']} "
            f"http={failure['http_status']} auth={failure['auth_mode']} "
            f"last_success={failure['last_success_at']} error={failure['error']}"
        )
    for warning in report["warnings"]:
        print(
            "  [WARN] "
            f"{warning['source_name']} status={warning['status']} "
            f"auth={warning['auth_mode']} reason={warning['warning']}"
        )


def main():
    parser = argparse.ArgumentParser(description="Check required source health for the radar pipeline.")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when required sources have failures.")
    parser.add_argument("--warn-only", action="store_true", help="Always exit 0 after printing the report.")
    parser.add_argument("--max-stale-hours", type=int, default=int(os.getenv("SOURCE_HEALTH_MAX_STALE_HOURS", "48")))
    args = parser.parse_args()

    report = evaluate_source_health(
        load_health(SOURCE_HEALTH_FILE),
        required_prefixes_from_env(),
        max_stale_hours=args.max_stale_hours,
    )
    print_report(report)

    strict = args.strict and not args.warn_only
    if strict and report["failure_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
