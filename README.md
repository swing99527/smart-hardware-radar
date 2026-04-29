# Smart Hardware Radar

> **全球智能硬件选品与竞争情报系统** — 专注 AI Wearables, Productivity Tools & Smart Lifestyle 细分赛道的客观数据驱动平台。

该系统继承了 `toy-shopify` 的“数实分离 (Process-Data Separation)”架构，并针对智能硬件高客单价、软硬件结合、认证门槛高的特性进行了专门的**三层决策模型优化**（Macro Screening -> Micro Teardown -> Feasibility Audit）。

---

## 🎯 核心方法论：四维信号与智能硬件专有算法

系统对智能硬件品类进行评分，100% 依靠数据公式推导。

### 四层信号数据源 (Adapted for Hardware)
| 维度 | 含义 | 核心指标 | 数据源 |
|---|---|---|---|
| **L1 社交/极客 (Social)** | 早期极客市场红利 | Kickstarter 众筹金额与 YouTube 测评热度 | 爬虫 / Agent 调研 |
| **L2 需求 (Search)** | 亚马逊搜索容量 | Top 3 细分场景关键词月搜量 | Sorftime / Jungle Scout |
| **L3 市场 (Market)** | 市场真空与巨头垄断 | CR3 (前三品牌垄断率，一票否决巨头垄断赛道) | Sorftime / Jungle Scout |
| **L4 供链 (Supply)** | 软硬结合落地可行性 | 深圳 PCBA/开模成本、FCC/蓝牙认证壁垒、App SaaS费用 | 1688 / 供应链调研 |

### 纯客观决策算法 (Decision Engine)
系统算法同样分为即战力（重市场规模与垄断低）和潜力分（重早期众筹与创新），以指导“跟进现货”还是“开私模”。

- 🟢 **核心推荐 (Core)**：Now Score ≥ 21.0（供应链成熟，巨头垄断低，适合快速贴牌或微创新）
- 🟡 **潜力黑马 (Trend)**：Trend Score ≥ 18.0 且不满足核心推荐（早期众筹爆款，适合众筹首发或精品开模）
- ❌ **暂缓入场 (Skip)**：CR3 垄断极高（如 Apple/Samsung）或技术壁垒过高
- ⚪️ **持续观察 (Watch)**：其他品类

---

## 📂 目录结构与数据流转

本仓库基于 V1/V2 混合演进架构：
- `data/`：宏观大盘的分类与决策中心 (Sorftime 或线下离线导入)
- `v2/input/`：微观产品拆解数据 (Jungle Scout MCP 产出的具体 ASIN 和 PPC 竞价)
- `dashboard/`：纯静态 HTML 高密度指挥大屏

```text
├── .env                  # (需手动创建) 本地密钥与环境变量
├── README.md             # 项目简介
├── dashboard/            # (前端展现) 纯静态 HTML 大屏
├── data/                 # (数据库) 宏观 JSON 事实源
├── docs/                 # (文档) 系统架构与运维指南
├── v2/input/             # (离线输入层) JS 等工具拆解的具体 ASIN 和关键词数据
└── scripts/              # (核心引擎)
```
