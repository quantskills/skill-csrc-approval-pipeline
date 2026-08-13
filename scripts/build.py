import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, List, Dict, Any, Union

BUILD_ID = "B02"
BUILD_NAME = "csrc-approval-pipeline"
DATA_VERSION = "pandadata-csrc-approval-pipeline-v2"

# 证监会审批流程状态机：受理 -> 反馈 -> 核准 -> 发行
STAGE_ACCEPTANCE = "受理"
STAGE_FEEDBACK = "反馈"
STAGE_APPROVAL = "核准"
STAGE_ISSUANCE = "发行"
STAGE_OTHER = "其他/信息"

STAGE_ORDER = {
    STAGE_ACCEPTANCE: 1,
    STAGE_FEEDBACK: 2,
    STAGE_APPROVAL: 3,
    STAGE_ISSUANCE: 4,
    STAGE_OTHER: 0,
}

# 阶段判定关键词（按标题/内容命中）
STAGE_KEYWORDS = {
    STAGE_ACCEPTANCE: [
        "受理", "备案", "首次备案", "申请材料", "申报", "辅导",
        "统计", "名录", "基本情况表", "首次公开发行申请",
    ],
    STAGE_FEEDBACK: [
        "反馈", "问询", "征求意见", "审核意见", "回复意见",
        "现场检查", "聆讯", "上市委会议", "发审委", "初审",
    ],
    STAGE_APPROVAL: [
        "核准", "同意", "准予", "批准", "注册的批复",
        "行政许可", "通过审核",
    ],
    STAGE_ISSUANCE: [
        "发行", "挂牌", "上市交易", "募集资金", "发行批复",
    ],
}

CATEGORY_DESC = {
    "03": "Stock Issuance",
    "06": "Bond Issuance",
    "07": "Futures Market",
    "08": "Fund Market",
    "0402": "M&A Restructuring",
    "040110": "IPO Review",
    "1602": "Securities Firm",
    "1603": "Fund Firm",
}


def get_panda_client():
    import panda_data
    username = os.environ.get("PANDA_DATA_USERNAME")
    password = os.environ.get("PANDA_DATA_PASSWORD")
    base_url = os.environ.get("PANDA_DATA_BASE_URL", "http://pandadata.pandaaiquant.com")
    if not username or not password:
        raise ValueError(
            "请设置环境变量 PANDA_DATA_USERNAME 和 PANDA_DATA_PASSWORD"
        )
    panda_data.init_token(username=username, password=password, base_url=base_url)
    return panda_data


def validate_input(input_data: dict):
    if not isinstance(input_data, dict):
        raise TypeError(f"input_data must be dict, got {type(input_data)}")
    if "start_date" not in input_data:
        raise ValueError("start_date is required")
    if "end_date" not in input_data:
        raise ValueError("end_date is required")
    for key in ("start_date", "end_date"):
        val = input_data[key]
        if not isinstance(val, str) or len(val) != 8 or not val.isdigit():
            raise ValueError(f"{key} must be an 8-digit YYYYMMDD string, got {val!r}")


def categorize_category(cat: str) -> str:
    return CATEGORY_DESC.get(cat, f"Other ({cat})")


def infer_pipeline_stage(text: str) -> str:
    """按关键词命中顺序判定审批流程阶段（受理/反馈/核准/发行）。

    优先级从高到低：核准 -> 发行 -> 反馈 -> 受理，
    避免"核准...发行...批复"这类标题被误判为发行阶段的用手工亲和规则优化。
    未命中任何关键词时归入\"其他/信息\"。
    """
    if not text:
        return STAGE_OTHER

    for stage, kws in STAGE_KEYWORDS.items():
        for kw in kws:
            if kw in text:
                return stage
    return STAGE_OTHER


def get_csrc_approval_data(
    start_date=None, end_date=None, announcement_level=None,
):
    """从 panda_data.readers.market_reference_reader 导入 get_stock_csrc_approval。"""
    from panda_data.readers.market_reference_reader import get_stock_csrc_approval
    return get_stock_csrc_approval(
        start_date=start_date,
        end_date=end_date,
        announcement_level=announcement_level,
    )


def run(
    input_data: dict,
    config: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    validate_input(input_data)

    panda = get_panda_client()

    start_date = input_data["start_date"]
    end_date = input_data["end_date"]
    filters = input_data.get("filters", {})
    cfg = config or {}

    df = get_csrc_approval_data(
        start_date=start_date,
        end_date=end_date,
        announcement_level=filters.get("announcement_level"),
    )

    if df.empty:
        return pd.DataFrame(
            columns=[
                "trade_date", "build_id", "build_name", "target_id",
                "result_type", "result_value", "result_json",
                "data_version", "update_time",
            ]
        )

    df["pipeline_stage"] = df["announcement_title"].apply(infer_pipeline_stage)
    df["stage_order"] = df["pipeline_stage"].map(STAGE_ORDER).fillna(0).astype(int)
    df["category_desc"] = df["announcement_category"].map(categorize_category)

    df = df.sort_values(["publish_date", "stage_order"]).reset_index(drop=True)

    rows = []
    seq_counter = {"n": 0}
    last_date = {"d": None}
    for _, row in df.iterrows():
        result_json = {
            "announcement_title": row.get("announcement_title"),
            "announcement_number": row.get("announcement_number"),
            "announcement_link": row.get("announcement_link"),
            "attachment_link": row.get("attachment_link"),
            "category_desc": row.get("category_desc"),
        }
        ann_no = row.get("announcement_number")
        if ann_no and str(ann_no) and str(ann_no) != "无":
            target_id = str(ann_no)
        else:
            # 无编号公告：同一发布日多条时追加序号，保证主键唯一
            date_key = str(row.get("publish_date"))
            if date_key != last_date["d"]:
                last_date["d"] = date_key
                seq_counter["n"] = 0
            target_id = f"{date_key}_{seq_counter['n']}"
            seq_counter["n"] += 1
        rows.append({
            "trade_date": row["publish_date"],
            "build_id": BUILD_ID,
            "build_name": BUILD_NAME,
            "target_id": target_id,
            "result_type": "pipeline_stage",
            "result_value": row["pipeline_stage"],
            "result_json": json.dumps(result_json, ensure_ascii=False),
            "data_version": DATA_VERSION,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    return pd.DataFrame(rows)


def pipeline_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "level_distribution": pd.DataFrame(),
            "category_distribution": pd.DataFrame(),
            "daily_trend": pd.DataFrame(),
            "total": 0,
        }

    level_counts = (
        df.groupby(["announcement_level", "pipeline_stage"])
        .size()
        .reset_index(name="count")
    )

    category_counts = (
        df.groupby(["announcement_category", "category_desc"])
        .size()
        .reset_index(name="count")
    )

    daily_counts = (
        df.groupby("publish_date")
        .size()
        .reset_index(name="count")
        .sort_values("publish_date")
    )

    return {
        "level_distribution": level_counts,
        "category_distribution": category_counts,
        "daily_trend": daily_counts,
        "total": len(df),
    }


if __name__ == "__main__":
    result = run(
        {"start_date": "20250601", "end_date": "20250712"},
    )
    if not result.empty:
        print(f"Total: {len(result)} records")
        print(result.to_string())
    else:
        print("No data returned")
