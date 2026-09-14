from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Iterable


@dataclass(frozen=True)
class Finding:
    asset_id: str
    severity: str
    rule: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def timestamp(value: Any, field: str, asset_id: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{asset_id}: {field} must be an ISO 8601 timestamp.")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{asset_id}: {field} must be an ISO 8601 timestamp.") from error
    if parsed.tzinfo is None:
        raise ValueError(f"{asset_id}: {field} must include a timezone.")
    return parsed.astimezone(timezone.utc)


def validate_assets(
    assets: Iterable[dict[str, Any]],
    *,
    now: datetime | None = None,
    review_age_days: int = 180,
) -> list[Finding]:
    if review_age_days < 1:
        raise ValueError("review_age_days must be at least 1.")
    current_time = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    findings: list[Finding] = []

    for asset in assets:
        if not isinstance(asset, dict):
            raise ValueError("Each asset must be a JSON object.")
        asset_id = asset.get("id")
        if not isinstance(asset_id, str) or not asset_id.strip():
            raise ValueError("Each asset requires a non-empty id.")
        asset_id = asset_id.strip()
        owner = asset.get("owner")
        uses = asset.get("uses_last_30_days")
        if not isinstance(uses, int) or uses < 0:
            raise ValueError(f"{asset_id}: uses_last_30_days must be a non-negative integer.")
        reviewed = timestamp(asset.get("last_reviewed"), "last_reviewed", asset_id)
        age_days = (current_time - reviewed).days

        if not isinstance(owner, str) or not owner.strip():
            findings.append(Finding(asset_id, "high", "MISSING_OWNER", "No accountable owner is recorded."))
        if age_days > review_age_days and uses >= 10:
            findings.append(Finding(asset_id, "high", "STALE_HIGH_USE", "A frequently used asset is overdue for review."))
        elif age_days > review_age_days:
            findings.append(Finding(asset_id, "medium", "STALE_ASSET", "The asset is overdue for review."))
        if uses == 0 and age_days > 90:
            findings.append(Finding(asset_id, "medium", "UNUSED_ASSET", "The asset needs an archive, retain, or consolidation decision."))
        if asset.get("duplicate_of"):
            findings.append(Finding(asset_id, "medium", "DUPLICATE_CANDIDATE", "The asset has a declared duplicate candidate."))

    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(findings, key=lambda item: (order[item.severity], item.asset_id, item.rule))
