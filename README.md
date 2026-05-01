# Smart Hardware Radar

> **全球智能硬件选品与竞争情报系统** — 专注 AI Wearables, Productivity Tools & Smart Lifestyle 细分赛道的客观数据驱动平台。

该系统继承了 `toy-shopify` 的“数实分离 (Process-Data Separation)”架构，并针对智能硬件高客单价、软硬件结合、认证门槛高的特性进行了专门的**三层决策模型优化**（Macro Screening -> Micro Teardown -> Feasibility Audit）。

---

## 🎯 核心方法论：四维信号与智能硬件专有算法

系统对智能硬件品类进行评分，100% 依靠数据公式推导。缺失维度记 0 分并写入 `data_quality`，不使用占位分数冒充真实信号。

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
- `data/signals.json`：L0 原始证据层，保存 source_url/source_title/source_type/raw_text/observed_at
- `data/trend_clusters.json`：可信趋势层，按语义聚类输出 Hot / Warming / Watch / Noise
- `data/trend_runs.json`：每次采集的趋势快照，用于观察趋势速度和重复出现
- `data/source_health.json`：每个采集源的最近状态、HTTP code、命中数量和限流信息
- `data/watch_topics.json`：长期关注关键词，覆盖热门 GitHub AI 项目、AI 模型周边、大厂周边和硬件交叉点
- `data/categories.json`：证据聚类后的候选类目层；当前不作为新品推荐结论，只作为后续 L1-L4 验证入口
- 中文支持：L0 normalization 会保留中文字符，watch topics 可混合中英文关键词，Dashboard 优先展示中文聚类名
- 中文媒体：已接入少数派和 36氪 RSS，信号会标记 `source_language: zh`
- 搜索热度：Google Trends Trending Now RSS 已作为 `search` 行为信号接入，默认 `US`，可用 `GOOGLE_TRENDS_GEOS=US,SG,HK` 扩展地区
- 众筹与媒体源：Indiegogo 改用 public JSON API；Gizmodo 改用 Google News 站内 RSS 查询，避免官方 RSS 403 让 source health 常红
- AI 编程工具周边：已加入 OpenClaw、Claude Code、OpenAI Codex、Gemini CLI / Gemini Code Assist 的 watch-only 监视，不直接生成硬件类目
- OpenClaw 硬件交叉：单独监控 OpenClaw + 摄像头、机器人、终端盒子、AI keyboard、AI recorder、edge/local device、ClawBox、OpenClaw OS 等组合
- Agentic edge hardware：扩展监控本地 AI 盒子、AI 摄像头、AI recorder、AI keyboard/command deck、机器人 agent kit、AI dev kit 等 agent + 物理 I/O 组合
- 数据源凭据：GitHub / Reddit / LLM 的 token 和 API key 配置见 `docs/data_source_credentials.md`
- `v2/input/`：微观产品拆解数据 (Jungle Scout MCP 产出的具体 ASIN 和 PPC 竞价)
- `docs/`：纯静态 HTML 高密度指挥大屏与 GitHub Pages 数据文件

```text
├── .env                  # (需手动创建) 本地密钥与环境变量
├── README.md             # 项目简介
├── data/                 # (数据库) 宏观 JSON 事实源
├── docs/                 # (文档 + 前端展现) GitHub Pages 大屏
├── v2/input/             # (离线输入层) JS 等工具拆解的具体 ASIN 和关键词数据
└── scripts/              # (核心引擎)
```
