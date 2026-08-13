# 证监会批文进度追踪 Skill

**简体中文** | [English](README.en.md)

> 追踪证监会审核批文的全流程进度：初始披露 → 审核阶段 → 最终决定 —— 按类别分类统计，一目了然。

<p align="center">
  <img alt="stages" src="https://img.shields.io/badge/pipeline_stages-3-blue">
  <img alt="data source" src="https://img.shields.io/badge/data-Pandadata-ff69b4">
  <img alt="requires" src="https://img.shields.io/badge/requires-pandadata--api-7c3aed">
</p>

---

## 这是什么

`csrc-approval-pipeline` 是一个 **BUILD 技能**：输入日期范围，获取证监会审核批文公告，按 `01 初始披露 → 02 审核阶段 → 03 最终决定` 三级映射分类，提供批文进度追踪和统计汇总。

## 批文阶段映射

| 等级 | 含义 |
|---|---|
| `01` → **Initial Notice / Disclosure** | 初始披露阶段 |
| `02` → **Review Stage** | 审核阶段 |
| `03` → **Final Decision** | 最终决定 |

## 快速开始

```bash
# 设置凭据（首次）
export PANDA_DATA_USERNAME=your_phone
export PANDA_DATA_PASSWORD=your_password
export PANDA_DATA_BASE_URL=http://pandadata.pandaaiquant.com

# 运行
python scripts/build.py
```

### 自定义参数

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

### 输出字段

| 字段 | 说明 |
|---|---|
| `trade_date` | 发布日期 |
| `build_id` | `B02` |
| `build_name` | `csrc-approval-pipeline` |
| `target_id` | 公告编号 |
| `result_type` | `pipeline_stage` |
| `result_value` | 阶段描述（例：Review Stage） |
| `result_json` | 公告标题/链接等详情 |

## 目录结构

```
csrc-approval-pipeline/
├── SKILL.md                    # 技能入口
├── scripts/
│   ├── build.py                # BUILD 构建脚本
│   └── test.py                 # 单元测试
├── agents/
│   ├── openai.yaml
│   ├── cursor-rule.mdc
│   └── portable-loader.md
├── 生产产物/
│   ├── SKILL.md                # 生产版文档
│   └── 数据库.parquet          # 生产数据
└── skill.json                  # 技能元数据
```

## 免责声明

本技能输出为基于公开数据的统计分析结果，不构成任何投资建议。
