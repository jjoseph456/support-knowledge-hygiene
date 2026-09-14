import unittest
from datetime import datetime, timezone

from support_knowledge_hygiene.guard import validate_assets


NOW = datetime(2026, 9, 14, tzinfo=timezone.utc)


def asset(**overrides):
    result = {
        "id": "KB-1",
        "kind": "runbook",
        "owner": "support",
        "last_reviewed": "2026-08-01T09:00:00Z",
        "uses_last_30_days": 2,
        "duplicate_of": None,
    }
    result.update(overrides)
    return result


class KnowledgeHygieneTests(unittest.TestCase):
    def test_missing_owner_is_high(self):
        findings = validate_assets([asset(owner="")], now=NOW)
        self.assertEqual("MISSING_OWNER", findings[0].rule)
        self.assertEqual("high", findings[0].severity)

    def test_stale_high_use_is_high(self):
        findings = validate_assets(
            [asset(last_reviewed="2025-01-01T09:00:00Z", uses_last_30_days=10)],
            now=NOW,
        )
        self.assertEqual("STALE_HIGH_USE", findings[0].rule)

    def test_unused_stale_asset_needs_decision(self):
        findings = validate_assets(
            [asset(last_reviewed="2025-01-01T09:00:00Z", uses_last_30_days=0)],
            now=NOW,
        )
        self.assertEqual(
            ["STALE_ASSET", "UNUSED_ASSET"],
            [item.rule for item in findings],
        )

    def test_duplicate_candidate_is_reported(self):
        findings = validate_assets([asset(duplicate_of="KB-2")], now=NOW)
        self.assertEqual("DUPLICATE_CANDIDATE", findings[0].rule)

    def test_timestamp_requires_timezone(self):
        with self.assertRaisesRegex(ValueError, "timezone"):
            validate_assets([asset(last_reviewed="2026-08-01T09:00:00")], now=NOW)
