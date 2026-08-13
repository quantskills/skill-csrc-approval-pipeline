---
name: csrc-approval-pipeline
description: A-share CSRC approval pipeline tracking skill — monitors regulatory approval progress, categorizes by announcement level, and generates pipeline status reports. Use when the user asks to track CSRC approval progress, monitor regulatory announcements, check approval pipeline status, or generate approval progress reports.
license: GPL-3.0-only
metadata:
  organization: QuantSkills
  organization_url: https://github.com/quantskills
  repository: skill-csrc-approval-pipeline
  repository_url: https://github.com/quantskills/skill-csrc-approval-pipeline
  project_type: skill
  collection: csrc-approval-pipeline
  creator: fuzijun
  maintainer: fuzijun
quantSkills:
  project_type: skill
  category: tooling
  tags:
    - a-share
    - csrc
    - approval
    - pipeline
    - pandadata
  platforms:
    - claude-code
    - codex
    - openclaw
    - cursor
  status: draft
  requires:
    - skill-pandadata-api
  validation_level: listed
  maintainer_type: community
  summary_zh: "A 股证监会批文进度追踪：按公告级别分类、审批流程监控、批文状态报告生成。"
  summary_en: "A-share CSRC approval pipeline tracking: categorization by announcement level, approval flow monitoring, and status report generation."
---

# CSRC Approval Pipeline

Use this skill to track CSRC (China Securities Regulatory Commission) approval pipeline progress. This BUILD monitors regulatory announcements, categorizes them by approval stage, and generates structured pipeline reports.

## Authentication

Set environment variables before use:

| Variable | Description |
|---|---|
| `PANDA_DATA_USERNAME` | PandaData account (phone number) |
| `PANDA_DATA_PASSWORD` | PandaData password |
| `PANDA_DATA_BASE_URL` | Base URL (default: `http://pandadata.pandaaiquant.com`) |

```powershell
$env:PANDA_DATA_USERNAME = "your_phone"
$env:PANDA_DATA_PASSWORD = "your_password"
```

## Tool Positioning
- Tool type: 进度追踪工具 (Pipeline Tracking BUILD)
- Problem solved: 跟踪证监会批文审核进度，掌握各阶段公告分布
- User: agent / 人工分析

## Applicable Scenarios
- When the user needs to track CSRC approval progress
- When monitoring regulatory announcement pipeline
- When generating approval status reports
- When analyzing approval trends by category and level

## Input
| Field | Type | Description |
|---|---|---|
| start_date | str | Data start date, format "YYYYMMDD" |
| end_date | str | Data end date, format "YYYYMMDD" |
| filters | dict | Optional: announcement_level, announcement_category |
| config | dict | Optional: group_by, output_format |

## Output (BUILD Fields)
| Field | Type | Description |
|---|---|---|
| trade_date | str | Publication date |
| build_id | str | Build identifier (B02) |
| build_name | str | Build name |
| target_id | str | Announcement number or date |
| result_type | str | Result type (pipeline_stage) |
| result_value | str | Pipeline stage label |
| result_json | str | JSON with title, number, links, category |
| data_version | str | Data version identifier |
| update_time | str | Record update timestamp |

### result_json Fields
| Field | Type | Description |
|---|---|---|
| announcement_title | str | Announcement title |
| announcement_number | str | Document number |
| announcement_link | str | Announcement URL |
| attachment_link | str | Attachment URL |
| category_desc | str | Category description |

## Usage
```python
from scripts.build import run, validate_input

# 输入校验：缺字段、空数据、类型错误会抛出明确异常
validate_input({"start_date": "20250601", "end_date": "20250712"})

result = run({
    "start_date": "20250601",
    "end_date": "20250712"
})
# result has columns: trade_date, build_id, build_name, target_id,
#                     result_type, result_value, result_json, data_version, update_time
```

## Data Source
- 数据来源：PandaAI data 数据拉取库（panda_data）
- 额定接口：`panda_data.readers.market_reference_reader.get_stock_csrc_approval`
- 输入必须来自 PandaAI data、调用方传入的标准结构化数据或项目指定数据源

### Pipeline Summary (works on raw DataFrame)
```python
from scripts.build import run, pipeline_summary, get_panda_client, categorize_level, categorize_category

# Get raw data for summary
panda = get_panda_client()
raw_df = panda.get_stock_csrc_approval(start_date="20250601", end_date="20250712")
raw_df["pipeline_stage"] = raw_df["announcement_level"].map(categorize_level)
raw_df["category_desc"] = raw_df["announcement_category"].map(categorize_category)

summary = pipeline_summary(raw_df)
# summary contains: level_distribution, category_distribution, daily_trend, total
```

## Can Be Called by Alpha
- Yes
- Call method: `run(input_data, config)` + `validate_input(input_data)`
- Dependency: panda_data（PandaAI data），`get_stock_csrc_approval`

## Production Result
- Generates `生产产物/数据库.parquet` with daily pipeline snapshot
- See [生产产物/SKILL.md](生产产物/SKILL.md) for production usage
- Update frequency: daily

## Dependencies
- panda_data >= 0.0.12
- numpy, pandas
