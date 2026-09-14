from __future__ import annotations

import argparse
import json
from pathlib import Path

from .guard import validate_assets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate support knowledge asset hygiene.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--review-age-days", type=int, default=180)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.input.read_text())
        if not isinstance(data, dict) or not isinstance(data.get("assets"), list):
            raise ValueError("Input must be a JSON object with an assets array.")
        findings = validate_assets(data["assets"], review_age_days=args.review_age_days)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"error: {error}")
        return 1
    if args.format == "json":
        print(json.dumps({"asset_count": len(data["assets"]), "findings": [item.to_dict() for item in findings]}, indent=2))
    else:
        for item in findings:
            print(f"{item.severity.upper():<7} {item.asset_id}  {item.rule}\n        {item.message}")
        if findings:
            print()
        print(f"Checked {len(data['assets'])} asset(s): {len(findings)} finding(s).")
    return 2 if any(item.severity == "high" for item in findings) else 0
