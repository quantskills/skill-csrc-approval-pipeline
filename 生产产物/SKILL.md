---
name: csrc-approval-pipeline-production
description: 生产环境的CSRC审批流程追踪数据读取和使用。从标准Parquet文件中读取审批流程数据，支持实时监控和生产报告生成。
tags: [quant, csrc, approval, pipeline, production, a-share]
---

# CSRC 审批流程追踪（生产）

## 数据读取

生产审批流程数据存储在：`生产产物/数据库.parquet`

**数据格式**：标准Parquet格式，包含标准BUILD字段

## 主键

- `trade_date`
- `build_id`
- `target_id`
- `result_type`

```python
import pandas as pd

# 读取生产数据
df = pd.read_parquet("生产产物/数据库.parquet")

# 筛选最新数据
latest_date = df['trade_date'].max()
latest_records = df[df['trade_date'] == latest_date].copy()
```

## 生产监控

### 质量监控

**每日监控指标**：
- 新增记录数量（应>0）
- 各审批阶段分布合理性
- 数据更新时间及时性
- result_json有效解析率

### 异常告警

**告警条件**：
- 连续3天无新增记录
- 某审批阶段数据异常缺失
- 数据延迟超过预期更新时间
- result_json解析失败

## 数据使用

### 实时流程获取

```python
import pandas as pd
from datetime import datetime, timedelta

df = pd.read_parquet("生产产物/数据库.parquet")

# 获取近7天审批记录
recent = df[df['trade_date'] >= (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')].copy()

# 按阶段分组统计
stage_counts = recent.groupby('result_value').size().sort_values(ascending=False)
```

### 输出字段使用

| 字段 | 用途 | 说明 |
|---|---|---|
| trade_date | 审批日期 | 公告发布日期 |
| build_id | 构建标识 | B02 |
| target_id | 目标标识 | 公告编号或日期 |
| result_type | 结果类型 | pipeline_stage |
| result_value | 审批阶段 | 受理 / 反馈 / 核准 / 发行 / 其他（按公告标题关键词推断） |
| result_json | 详细信息 | JSON含标题、编号、链接 |
| data_version | 数据版本 | 标识数据批次 |
| update_time | 更新时间 | 数据刷新时间 |

## 生产注意事项

1. **更新时机**：数据每日更新
2. **读取时机**：每日更新后即可读取
3. **数据验证**：使用前检查data_version和update_time
4. **JSON解析**：result_json需使用json.loads解析
5. **禁止重算**：生产环境禁止重新调用源API

## 风险边界

### 数据延迟

- 审批公告发布时间存在不确定性
- 数据更新可能受节假日影响
- 需监控数据更新延迟

### 数据依赖

- 依赖PandaData审批数据源
- 数据覆盖范围受PandaData限制
- 需监控数据源可用性

### 市场环境

- 审批节奏可能受政策影响
- 不同市场环境下审批数量可能变化
- 建议定期验证数据完整性

## 维护说明

### 更新机制

- **更新频率**：每日自动更新
- **数据保留**：保留最近1年数据
- **备份策略**：每日备份，保留7天

### 版本管理

- **data_version**: 标识数据版本
- **update_time**: 记录更新时间
- **版本追踪**: 支持历史版本回溯

## 故障处理

### 常见问题

1. **数据缺失**
   - 检查Parquet文件是否存在
   - 检查数据版本标识
   - 联系技术支持

2. **数据异常**
   - 检查更新时间是否正常
   - 验证数据版本一致性
   - 对比历史数据趋势

3. **性能下降**
   - 检查数据量级
   - 优化查询条件
   - 联系开发团队

### 恢复策略

- **自动重试**：读取失败自动重试
- **降级处理**：主数据源失败时使用缓存
- **人工介入**：严重问题时人工处理

## 联系支持

如有生产问题，请联系：
- 技术支持：量化研究团队
- 数据支持：PandaData技术支持
- 项目负责人：CSRC项目负责人

## 数据来源说明

**真实PandaData数据**：
- 数据源：panda_data.get_stock_csrc_approval()
- 数据版本：pandadata-csrc-approval-pipeline-v2
- 账号格式：需自行申请PandaData权限
- 声明：本数据仅供量化研究参考，不对数据准确性作任何保证
