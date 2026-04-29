# L0 Discovery Pipeline v1.0 (自动化情绪发现漏斗)

> 智能硬件选品的核心不再是“人工拍脑袋”，而是让机器在全网自动嗅探“情绪指标”。
> L0 层负责：**广撒网 -> 抓情绪 -> 提炼品类词 -> 喂给 L1~L4 打分引擎**。

## 1. 数据源与情绪指标 (Sentiment Sources)

我们从三个维度捕获市场情绪，并将其量化为可追踪的数字。

### 源 A：极客与尝鲜情绪 (Geek Sentiment)
*   **目标平台**：Kickstarter / Indiegogo (Tech, Design 板块)
*   **抓取逻辑**：每日通过爬虫获取 `State: Live` 且 `Funded % > 300%` 的硬件项目。
*   **情绪指标**：
    *   `Velocity`（资金增速）：每小时新增 Backers 数量。
    *   若某项目上线 48 小时内突破 $1M，判定为**“一级情绪爆发”**。

### 源 B：大众社交病毒情绪 (Viral Sentiment)
*   **目标平台**：TikTok Creative Center (Trend Discovery) / YouTube
*   **抓取逻辑**：监控特定 Hashtags (`#techfinds`, `#smartgadgets`, `#amazonfinds`) 下，过去 7 天内播放量飙升的视频。
*   **情绪指标**：
    *   `Engagement Rate`（互动率 = 点赞数 / 播放量）。
    *   硬件类视频互动率若超过 8%（通常为 3-5%），说明具备极强的“视觉奇观”或击中了痛点（如 AI 宠物翻译器）。

### 源 C：电商真金白银情绪 (Buyer Sentiment)
*   **目标平台**：Amazon Movers & Shakers / New Releases (Electronics, Cell Phones, Health)
*   **抓取逻辑**：调用 Jungle Scout 或通过爬虫获取上架时间 `< 90 天` 且 `BSR 排名飙升`的 ASIN。
*   **情绪指标**：
    *   `BSR Momentum`（排名跃升斜率）。

---

## 2. 自动化工作流 (The Automated Cron Pipeline)

必须通过 `cron` 或 GitHub Actions 实现每日无人值守运行。

### Phase 1: 嗅探与提炼 (Scout & Extract)
1. 运行 `scripts/scout_l0.py`。
2. 爬虫并发访问三大数据源，拿到数百个高情绪的**原始标题/视频标签/ASIN**。
3. **LLM 清洗**：调用 LLM（如 Claude API），过滤掉非硬件（如软件软件、普通水杯），将剩余的硬件项目归一化为通用的**英文品类词**（Seed Keywords）。
   * *例：输入 "PLAUD NOTE - ChatGPT Voice Recorder", LLM 输出 -> "AI Voice Recorder"*。

### Phase 2: 剪刀差初筛 (Signal Check)
1. 对提炼出的品类词，调用 JS 获取亚马逊搜量 (L2)，调用 YouTube API 获取视频播放量 (L1)。
2. **过滤规则**：
   * 如果 L1 极高，L2 极高 -> 放入 `data/categories.json`。
   * 如果 L1 极高，L2 极低 -> 放入 `data/categories.json`（潜在蓝海）。
   * 否则，抛弃该词。

### Phase 3: 深度扫描与打分 (Deep Dive & Score)
1. 运行已有的 `scripts/cr3.py` 和 `scripts/score.py`，获取 CR3 反垄断指数和 L4 供应链估算。
2. 计算最终的 `Now Score` 和 `Trend Score`。

### Phase 4: 飞书报警 (Alerting)
如果计算出 `Total Score > 20` 或判定为 `🟢 核心推荐`，系统自动通过 Webhook 向飞书群发送带链接的研报。

---

## 3. 接棒指南 (Handover to Next Agent)
下一个 Agent 必须实现以下代码：
1. 编写针对 Kickstarter 的爬虫（无需登录）。
2. 编写针对 Amazon Movers & Shakers 的爬虫。
3. 对接一个基础的 LLM API 进行标题清洗，自动生成品类词库，喂入我们已建好的引擎中。
