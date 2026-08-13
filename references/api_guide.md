# CSRC Approval Pipeline API Guide

## Data Source
- **API**: panda_data.readers.market_reference_reader.get_stock_csrc_approval()
- **Base URL**: http://pandadata.pandaaiquant.com (configurable via PANDA_DATA_BASE_URL)
- **Auth**: Environment variables (no hardcoded credentials)

## Authentication

Set these environment variables before use:

| Variable | Description |
|---|---|
| PANDA_DATA_USERNAME | PandaData account (phone number) |
| PANDA_DATA_PASSWORD | PandaData password |
| PANDA_DATA_BASE_URL | Base URL (default: http://pandadata.pandaaiquant.com) |

## Method Signature
```python
get_stock_csrc_approval(
    start_date: str = None,
    end_date: str = None,
    announcement_level: Optional[Union[int, List[int]]] = None,
    fields: Optional[Union[str, List[str]]] = None,
) -> pd.DataFrame
```

## BUILD Output Fields

The `run()` function returns a DataFrame with standard BUILD fields:

| Field | Type | Description |
|---|---|---|
| trade_date | str | Publication date (YYYYMMDD) |
| build_id | str | Build identifier (B02) |
| build_name | str | Build name (csrc-approval-pipeline) |
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

## Raw Returned Fields (from panda_data API)
| Field | Type | Description |
|---|---|---|
| publish_date | str | Publication date (YYYYMMDD) |
| publish_institution | str | Publishing institution |
| announcement_category | str | Category code |
| announcement_level | str | Announcement level (01/02/03) |
| announcement_title | str | Announcement title |
| announcement_number | str | Document number |
| announcement_content | str | Full text |
| attachment_link | str | Attachment URL |
| announcement_link | str | Announcement URL |

## Announcement Level Mapping
| Level | Stage | Description |
|---|---|---|
| 01 | Initial Notice / Disclosure | Initial disclosure or rule announcement |
| 02 | Review Stage | Under review or public consultation |
| 03 | Final Decision | Final approval or decision issued |

## Category Mapping (partial)
| Code | Description |
|---|---|
| 03 | Stock Issuance |
| 06 | Bond Issuance |
| 07 | Futures Market |
| 08 | Fund Market |
| 0402 | M&A Restructuring |
| 040110 | IPO Review |
| 1602 | Securities Firm Regulation |
| 1603 | Fund Firm Regulation |

## Pipeline Summary (works on raw DataFrame)
```python
pipeline_summary(df: pd.DataFrame) -> dict
```
Returns:
- `level_distribution`: DataFrame with level counts
- `category_distribution`: DataFrame with category counts
- `daily_trend`: DataFrame with daily publication trend
- `total`: Total record count
