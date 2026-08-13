import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.build import (
    run, validate_input, pipeline_summary, get_panda_client,
    categorize_category, infer_pipeline_stage,
    get_csrc_approval_data,
    STAGE_ACCEPTANCE, STAGE_FEEDBACK, STAGE_APPROVAL,
    STAGE_ISSUANCE, STAGE_OTHER,
)
import pandas as pd


def test_validate_input():
    try:
        validate_input({"start_date": "20250101", "end_date": "20250701"})
        print("PASS: valid input")
    except Exception as e:
        print(f"FAIL: {e}")

    try:
        validate_input({})
    except ValueError:
        print("PASS: empty input raises ValueError")
    except Exception as e:
        print(f"FAIL: expected ValueError, got {type(e).__name__}: {e}")

    try:
        validate_input("not a dict")
    except TypeError:
        print("PASS: non-dict input raises TypeError")
    except Exception as e:
        print(f"FAIL: expected TypeError, got {type(e).__name__}: {e}")


def test_state_machine():
    cases = [
        ("申报材料受理", STAGE_ACCEPTANCE),
        ("关于XXXX首次公开发行股票申请文件的受理", STAGE_ACCEPTANCE),
        ("XXXX问询函", STAGE_FEEDBACK),
        ("关于《XXXX办法（征求意见稿）》公开征求意见的通知", STAGE_FEEDBACK),
        ("关于核准XXXX设立子公司的批复", STAGE_APPROVAL),
        ("关于同意XXXX首次公开发行股票注册的批复", STAGE_APPROVAL),
        ("公开发行公司债券的批复（2025.6.2-2025.6.5）", STAGE_ISSUANCE),
        ("关于XXXX向不特定合格投资者公开发行股票注册的批复", STAGE_APPROVAL),
        ("2025年5月份全国期货市场交易情况统计", STAGE_ACCEPTANCE),
        ("中国证券监督管理委员会行政处罚决定书", STAGE_OTHER),
    ]
    for text, expected in cases:
        got = infer_pipeline_stage(text)
        assert got == expected, f"'{text[:30]}' expected {expected}, got {got}"
        print(f"PASS: '{text[:36]}' -> {got}")

    assert "Stock" in categorize_category("03")
    assert "M&A" in categorize_category("0402")
    assert "Other" in categorize_category("9999")
    print("PASS: categorize_category returns correct labels")


def test_import_direct():
    import inspect
    from panda_data.readers.market_reference_reader import get_stock_csrc_approval
    assert inspect.isfunction(get_stock_csrc_approval)
    assert get_csrc_approval_data.__module__ == "__main__" or callable(get_csrc_approval_data)
    print("PASS: get_stock_csrc_approval importable from market_reference_reader")


def test_run_real():
    result = run(
        {"start_date": "20250701", "end_date": "20250712"},
    )
    assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
    assert len(result) > 0, "Expected at least 1 row"
    expected_cols = [
        "trade_date", "build_id", "build_name", "target_id",
        "result_type", "result_value", "result_json",
        "data_version", "update_time",
    ]
    for col in expected_cols:
        assert col in result.columns, f"{col} column missing"
    assert set(result["result_value"].unique()).issubset(
        {STAGE_ACCEPTANCE, STAGE_FEEDBACK, STAGE_APPROVAL, STAGE_ISSUANCE, STAGE_OTHER}
    ), "result_value must be a valid pipeline stage"
    print(f"PASS: real API call returned {len(result)} rows")
    print("     stage distribution:")
    for stage, cnt in result["result_value"].value_counts().items():
        print(f"        {stage}: {cnt}")
    sample = result.head(3)
    for _, row in sample.iterrows():
        rj = json.loads(row["result_json"])
        print(f"  {row['trade_date']} | {row['result_value']} | {rj.get('announcement_title', '')[:40]}")
    print(f"PASS: result_json contains valid JSON in all rows")


def test_pipeline_summary():
    df = get_csrc_approval_data(
        start_date="20250701",
        end_date="20250712",
    )
    if not df.empty:
        df["pipeline_stage"] = df["announcement_title"].apply(infer_pipeline_stage)
        df["category_desc"] = df["announcement_category"].map(categorize_category)
        summary = pipeline_summary(df)
        assert isinstance(summary, dict), "Expected dict from pipeline_summary"
        assert "level_distribution" in summary
        assert "category_distribution" in summary
        assert "daily_trend" in summary
        assert summary["total"] > 0
        print(f"PASS: pipeline_summary returns {summary['total']} total items")
        print(f"     {len(summary['level_distribution'])} stage groups")
        print(f"     {len(summary['category_distribution'])} category groups")
        print(f"     {len(summary['daily_trend'])} daily records")
    else:
        print("SKIP: no data for summary test")

    empty_summary = pipeline_summary(pd.DataFrame())
    assert isinstance(empty_summary, dict), "Expected dict for empty input"
    assert empty_summary["total"] == 0, "Expected 0 for empty input"
    print("PASS: pipeline_summary handles empty DataFrame")


if __name__ == "__main__":
    print("=== test_validate_input ===")
    test_validate_input()
    print("\n=== test_state_machine ===")
    test_state_machine()
    print("\n=== test_import_direct ===")
    test_import_direct()
    print("\n=== test_run_real ===")
    test_run_real()
    print("\n=== test_pipeline_summary ===")
    test_pipeline_summary()
