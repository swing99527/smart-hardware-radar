# Smart Hardware Radar — Methodology v1.0

> 北美智能硬件选品雷达的**评分宪法**。所有 `scripts/` 下的代码都必须严格遵循本文档的公式与阈值。
> 修改本文档需同步更新 `scripts/score.py` 与 `data/categories.json` 的 `methodology_version` 字段。

**版本**: 1.0
**生效日期**: 2026-04-29
**适用赛道**: 智能硬件 (AI Wearables / Productivity Tools / Smart Lifestyle / Smart Audio)

---

## 1. 总评分模型

每个品类有 4 个一级维度 (L1-L4)，每个维度满分 25，总分满分 100。

```
Total = L1 + L2 + L3 + L4
```

但 `Total` **不是决策依据**。真正用于决策的是两个合成分数：

```
Now Score   = L3 × 0.50 + L4 × 0.30 + L2 × 0.20      # 现状分（适合"跟现货/小规模试水"）
Trend Score = L1 × 0.40 + L3 × 0.40 + L2 × 0.20      # 潜力分（适合"开私模/长线投入"）
```

> **设计意图**：
> - Now Score 强调**反垄断 + 供应链落地**，因为现货跟卖最怕"做完就被巨头碾压"或"开模时间来不及"。
> - Trend Score 强调**社媒/众筹热度 + 反垄断**，因为长线投入需要赌"市场尚未被瓜分"且"有上升势能"。

---

## 2. 决策阈值

按 `max(Now Score, Trend Score)` 落入下列区间分类：

| 决策标签 | 区间 | 含义 |
|---|---|---|
| 🟢 核心推荐 | ≥ 21 | 立即立项，进入 04 供应链对接 |
| 🟡 潜力黑马 | 18 – 20.99 | 进入 watching，每月复评 |
| ⚪ 观察样本 | 15 – 17.99 | 仅记录，不投入资源 |
| ❌ 暂缓入场 | < 15 | 归档，半年内不再评估 |

> **CR3 一票否决**：无论 Now/Trend 多高，只要 L3 维度判定 `CR3 > 50%`，强制降为 ❌。

> **阈值校准说明**：当前阈值（21/18/15）从 toy-shopify 直接平移，待累计 ≥ 20 个真实评分品类后做分布校准（见 §7）。

---

## 3. L1 — 极客与社媒趋势 (满分 25)

**衡量目标**：早期需求信号 + 未来势能。

**数据源**：
- Kickstarter / Indiegogo（智能硬件 / Tech / Wearables 分类）
- YouTube Tech 测评博主（Marques Brownlee、Linus、MKBHD、Unbox Therapy 等）

**三个子维度**：

| 子维度 | 满分 | 数据获取 |
|---|---|---|
| L1a 众筹融资规模 (Funding) | 10 | Kickstarter API: 品类关键词近 12 个月已成功项目的众筹总金额 (USD) |
| L1b 众筹项目数量 (Velocity) | 8 | 同上接口：近 12 个月新发起的项目数 |
| L1c YouTube 测评热度 (Buzz) | 7 | YouTube Data API: 关键词近 90 天上传视频的总播放量 |

**归一化公式**（log 缩放，防止头部品类拉爆分布）：

```python
L1a = min(10, log10(max(funding_usd, 1)) × 1.6)         # $1M ≈ 9.6 分; $100k ≈ 8 分
L1b = min(8,  log10(max(project_count, 1)) × 4)         # 100 个项目 ≈ 8 分
L1c = min(7,  log10(max(youtube_views, 1)) × 1.0)       # 1000 万播放 ≈ 7 分

L1  = round(L1a + L1b + L1c, 1)
```

**冷启动兜底**：当某子维度数据缺失时，记 0 分并在 `data_quality` 字段标注 `"L1c": "missing"`，不允许人工估分。

---

## 4. L2 — 亚马逊场景搜量 (满分 25)

**衡量目标**：当前需求强度 + PPC 竞价友好度。

**数据源**：Jungle Scout `js_keywords_by_keyword`、`js_keywords_by_asin`

**三个子维度**：

| 子维度 | 满分 | 含义 |
|---|---|---|
| L2a 头部关键词月搜量 | 12 | Top 3 相关关键词 (relevancy_score > 80) 月搜量之和 |
| L2b 关键词宽度 | 8 | 月搜量 ≥ 1000 的相关词数量（衡量需求场景是否丰富） |
| L2c PPC 友好度 | 5 | 头部关键词的平均建议竞价 (USD)，**越低越好** |

**归一化公式**：

```python
L2a = min(12, log10(max(top3_volume, 1)) × 2.4)        # 100k 月搜 = 12 分

L2b = min(8, keyword_count_over_1k / 5)                # 40 个长尾词 = 8 分

# PPC：竞价越低越好，超过 $5 视为红海
if avg_ppc <= 0.5:   L2c = 5
elif avg_ppc <= 1.0: L2c = 4
elif avg_ppc <= 2.0: L2c = 3
elif avg_ppc <= 3.5: L2c = 2
elif avg_ppc <= 5.0: L2c = 1
else:                L2c = 0

L2 = round(L2a + L2b + L2c, 1)
```

**注意**：JS 接口 `ppc_bid_*` 字段经常返回 null，缺失时 L2c 记为 2.5（中性分），并在 `data_quality` 标注。

---

## 5. L3 — 市场真空度与反垄断 (满分 25) ⚠️ 含一票否决

**衡量目标**：市场是否被巨头瓜分；是否仍有切入空间。

**数据源**：Jungle Scout `js_product_database_query` (Top 30 ASIN by revenue) + 自研 `cr3.py` 聚合

**三个子维度**：

| 子维度 | 满分 | 含义 |
|---|---|---|
| L3a 反垄断指数 (Anti-Monopoly) | 12 | 基于 CR3 (Top 3 品牌营收占比) |
| L3b 市场容量 (Market Size) | 8 | Top 30 ASIN 月营收总和 (USD) |
| L3c 评论密度（红海稀疏度） | 5 | Top 30 ASIN 平均评论数（越少代表越未饱和） |

**CR3 计算（详见 `scripts/cr3.py`）**：

```
1. 取该品类在亚马逊 US 的 Top 30 ASIN（按月营收降序）
2. 按 brand 字段聚合，求每品牌月营收总和
3. CR3 = sum(top3_brand_revenue) / sum(top30_total_revenue)
```

**L3a 公式（含一票否决）**：

```python
if CR3 > 0.50:
    L3a = 0
    veto_flag = True              # 触发一票否决，最终决策强制 ❌
elif CR3 <= 0.20:  L3a = 12
elif CR3 <= 0.30:  L3a = 10
elif CR3 <= 0.40:  L3a = 7
else:              L3a = 4         # 0.40 < CR3 <= 0.50
```

**L3b / L3c 公式**：

```python
L3b = min(8, log10(max(top30_total_revenue, 1)) × 1.3)   # $1M/月 = 7.8 分

# 评论密度：越少越优
avg_reviews = mean(top30_review_count)
if avg_reviews <= 200:    L3c = 5
elif avg_reviews <= 500:  L3c = 4
elif avg_reviews <= 1500: L3c = 3
elif avg_reviews <= 5000: L3c = 2
else:                     L3c = 1

L3 = round(L3a + L3b + L3c, 1)
```

---

## 6. L4 — 软硬一体化落地门槛 (满分 25)

**衡量目标**：从设计到上市的实操难度（成本、周期、合规）。

**数据源**：`docs/cost_library.md`（基准成本库）+ 1688 选型 + 行业经验库

**四个子维度（注意是 4 个）**：

| 子维度 | 满分 | 含义 |
|---|---|---|
| L4a PCBA 成本与成熟度 | 8 | 主控+无线模组的 BOM 成本与方案商可得性 |
| L4b 模具与外壳复杂度 | 6 | 注塑/CNC 件数量及开模费 (USD) |
| L4c 合规认证负担 | 6 | FCC / CE / BQB / RoHS / FDA 累计费用 (USD) |
| L4d App / SaaS 成本 | 5 | 是否需自研 App、AI 推理 / 云存储月成本 |

**归一化公式**（成本越低/方案越成熟 → 分数越高）：

```python
# L4a PCBA: 基于 BOM 成本档位 (USD per unit @ MOQ 1000)
if pcba_bom <= 5:    L4a = 8
elif pcba_bom <= 12: L4a = 6
elif pcba_bom <= 25: L4a = 4
elif pcba_bom <= 50: L4a = 2
else:                L4a = 1

# L4b 模具：开模总费用 (USD)
if mold_cost <= 10000:  L4b = 6
elif mold_cost <= 30000: L4b = 4
elif mold_cost <= 80000: L4b = 2
else:                    L4b = 1

# L4c 认证费用
if cert_cost <= 5000:   L4c = 6
elif cert_cost <= 15000: L4c = 4
elif cert_cost <= 40000: L4c = 2
else:                    L4c = 0   # FDA 医疗类基本退出

# L4d App：是否需要 + 月活成本
if not needs_app:        L4d = 5
elif saas_cost_per_user_per_month <= 0.20: L4d = 4
elif saas_cost_per_user_per_month <= 1.00: L4d = 2
else:                    L4d = 0   # 重型 AI 推理 (>$1/MAU) 不做

L4 = round(L4a + L4b + L4c + L4d, 1)
```

各档位的具体成本数值见 `docs/cost_library.md`。

---

## 7. 阈值校准 (Calibration) 流程

阈值（21/18/15）必须在累计 ≥ 20 个真实品类评分后校准：

1. 计算所有品类 `max(Now, Trend)` 的分布。
2. 取分位数：P75 → 🟢 阈值；P50 → 🟡 阈值；P25 → ⚪ 阈值。
3. 把校准后的阈值写入本文档 §2 并升级 `methodology_version`。
4. 重跑历史品类，记录决策变更。

---

## 8. 数据质量与可追溯字段

每个品类的评分结果必须携带元数据：

```json
{
  "id": "H03",
  "scores": { "L1": 18.5, "L2": 22.0, "L3": 21.0, "L4": 22.0 },
  "now_score": 21.4,
  "trend_score": 19.7,
  "decision": "🟢 核心推荐",
  "veto_flag": false,
  "methodology_version": "1.0",
  "calculated_at": "2026-04-29T14:00:00+08:00",
  "data_sources": {
    "L1a": {"source": "kickstarter_api", "as_of": "2026-04-28", "raw": 1240000},
    "L1c": {"source": "youtube_data_api", "as_of": "2026-04-28", "raw": 8200000},
    "L2a": {"source": "js_keywords_by_keyword", "as_of": "2026-04-29", "raw": 47200},
    "L3a": {"source": "scripts/cr3.py", "cr3": 0.34}
  },
  "data_quality": {
    "L1a": "ok", "L1b": "ok", "L1c": "ok",
    "L2a": "ok", "L2b": "ok", "L2c": "missing_fallback",
    "L3a": "ok", "L3b": "ok", "L3c": "ok",
    "L4a": "library", "L4b": "library", "L4c": "library", "L4d": "library"
  }
}
```

> 字段缺失时**严禁人工估分**。统一记录 `"missing"` 或 `"missing_fallback"`，由后续数据补全。

---

## 9. 版本历史

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-04-29 | 首版定稿。L1-L4 全部维度落地为可量化公式；CR3 一票否决固化；引入 Now/Trend 双轨。 |

---
## 10. [V1.1 修正案] 2026 大模型时代生存法则

> 2026-04-29 更新：纯电商与纯众筹模型已不足以抵御“大厂降维打击”，特引入三维校验：

### 10.1 大厂射程惩罚 (Big Tech Blast Radius)
如果在 Apple / Meta / Samsung 的核心硬件路线图上（例如：系统级穿戴、手机原生功能平替），将面临巨大的降维打击风险。
**计算规则**：`big_tech_risk` (0~1.0) × 15 分，直接从 `Now Score` 和 `Trend Score` 中双双扣除。

### 10.2 流量溢出共振 (L1 / L2 Scissors)
电商存量 (L2) 很高但社媒冷清 (L1) = 传统红海；社媒极热 (L1) 但亚马逊搜量低 (L2) = 伪需求/教育期。
**计算规则**：只有当 `L1 ≥ 15` 且 `L2 ≥ 15` 时，证明社交病毒流量正疯狂转化为电商真实搜索，此时赋予 `Trend Score` **1.1x** 的乘数奖励。


### 10.3 [V1.2 修正案] 拓荒期豁免机制 (Emerging Market Exemption)
**问题背景**：对于极其新兴的品类（如月销刚起步），全网可能只有 2-3 个卖家，导致 CR3 必然 > 50%。原 V1.1 规则会将此类“真蓝海”误杀为“巨头垄断”。
**修订规则**：
当且仅当该品类 Top 30 ASIN 的总月营收 **< $100,000 (十万美金)** 时，判定该市场处于“拓荒期 (Emerging)”。
此时：
1. **取消 CR3 > 50% 的一票否决 (Veto = False)**。
2. L3a 维度（反垄断得分）强制记为中性分 **6 分**，不再因集中度高而罚到 0 分。
3. 最终决策完全交由 L1（社媒热度）和 L4（落地成本）来主导。
