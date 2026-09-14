# Support Knowledge Hygiene

[![CI](https://github.com/jjoseph456/support-knowledge-hygiene/actions/workflows/test.yml/badge.svg)](https://github.com/jjoseph456/support-knowledge-hygiene/actions/workflows/test.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A dependency-free Python CLI that identifies support knowledge assets needing
an owner, review, archival decision, or duplicate-content review.

The tool is designed for runbooks, macros, internal articles, and similar
knowledge assets. It uses synthetic JSON examples and contains no employer
content, customer information, usage exports, or internal documentation.

## Quick Start

```bash
git clone https://github.com/jjoseph456/support-knowledge-hygiene.git
cd support-knowledge-hygiene
python -m pip install -e .
python -m support_knowledge_hygiene examples/assets.json
```

## What It Checks

| Rule | Severity | Meaning |
| --- | --- | --- |
| `MISSING_OWNER` | High | No accountable maintainer is recorded. |
| `STALE_HIGH_USE` | High | A frequently used asset is overdue for review. |
| `STALE_ASSET` | Medium | An asset has not been reviewed within the configured interval. |
| `UNUSED_ASSET` | Medium | A low-use asset needs an archive, retain, or consolidation decision. |
| `DUPLICATE_CANDIDATE` | Medium | An asset names a possible duplicate that needs review. |

Use `--format json` for automation or `--review-age-days` to set a different
freshness threshold. The command returns `2` when high-severity findings are
present, `1` for invalid input, and `0` otherwise.

## Input Format

```json
{
  "assets": [
    {
      "id": "KB-100",
      "kind": "runbook",
      "owner": "platform-support",
      "last_reviewed": "2026-08-01T09:00:00Z",
      "uses_last_30_days": 18,
      "duplicate_of": null
    }
  ]
}
```

## Why It Exists

Support knowledge gets weaker in predictable ways: ownership disappears,
high-use guidance becomes stale, low-use content accumulates without a
decision, and duplicate material creates inconsistent answers. This tool
turns those risks into explicit checks that teams can run consistently.

It demonstrates Python CLI design, validation, operational scoring,
machine-readable output, and privacy-safe examples.

## Development

```bash
python -m unittest discover -s tests -v
```
Score support knowledge assets for ownership, freshness, usage, and duplication risk
