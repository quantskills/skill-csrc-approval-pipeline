# CSRC Approval Pipeline Skill

[简体中文](README.md) | **English**

> Track the full CSRC approval pipeline: Initial Notice/Disclosure → Review Stage → Final Decision — categorized and summarized at a glance.

<p align="center">
  <img alt="stages" src="https://img.shields.io/badge/pipeline_stages-3-blue">
  <img alt="data source" src="https://img.shields.io/badge/data-Pandadata-ff69b4">
  <img alt="requires" src="https://img.shields.io/badge/requires-pandadata--api-7c3aed">
</p>

---

## What is this

`csrc-approval-pipeline` is a **BUILD skill**: input a date range, fetch CSRC approval announcements, map them to `01 Initial Notice/Disclosure → 02 Review Stage → 03 Final Decision`, and provide pipeline tracking and summary statistics.

## Pipeline Stage Mapping

| Level | Meaning |
|---|---|
| `01` → **Initial Notice / Disclosure** | Initial disclosure stage |
| `02` → **Review Stage** | Review stage |
| `03` → **Final Decision** | Final decision |

## Quick Start

```bash
# Set credentials (first time)
export PANDA_DATA_USERNAME=your_phone
export PANDA_DATA_PASSWORD=your_password
export PANDA_DATA_BASE_URL=http://pandadata.pandaaiquant.com

# Run
python scripts/build.py
```

### Custom Parameters

```python
from scripts.build import run, pipeline_summary

result = run(
    {"start_date": "20250601", "end_date": "20250712"},
)
print(f"Total: {len(result)} records")

stats = pipeline_summary(...)
print(stats["level_distribution"])
print(stats["category_distribution"])
```

### Output Fields

| Field | Description |
|---|---|
| `trade_date` | Publish date |
| `build_id` | `B02` |
| `build_name` | `csrc-approval-pipeline` |
| `target_id` | Announcement number |
| `result_type` | `pipeline_stage` |
| `result_value` | Stage description (e.g. Review Stage) |
| `result_json` | Announcement title/link details |

## Directory Layout

```
csrc-approval-pipeline/
├── SKILL.md                    # Skill entry
├── scripts/
│   ├── build.py                # BUILD script
│   └── test.py                 # Unit tests
├── agents/
│   ├── openai.yaml
│   ├── cursor-rule.mdc
│   └── portable-loader.md
├── 生产产物/
│   ├── SKILL.md                # Production doc
│   └── 数据库.parquet          # Production data
└── skill.json                  # Skill metadata
```

## Disclaimer

This skill produces statistical analysis based on public data. Nothing here constitutes investment advice.
