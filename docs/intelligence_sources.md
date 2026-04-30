## 🛰️ 智能硬件全网首发情报源矩阵 (Intelligence Sources V2.0)

本系统已实现 **全频谱、零死角** 监控，确保不遗漏任何一个变异品种。

### 📡 当前已接入的 L0 实时嗅探源 (12条物理链路)

| 平台 | 监控深度 | 战略意图 |
| :--- | :--- | :--- |
| **Product Hunt** | 每日全量扫描 | 发现硅谷最新的软硬件结合方案 |
| **Kickstarter (Tech/Design)** | 全量 Atom 订阅 | 锁定最早期的众筹原型，领先亚马逊半年 |
| **Indiegogo** | 科技频道全覆盖 | 捕捉大量中国出海精品硬件的首发数据 |
| **Hacker News (Show HN)** | 实时 RSS | 监控硬核极客亲手打造的实验性设备 |
| **Yanko Design** | 全量订阅 | **[关键]** 监控尚未量产的工业设计趋势，寻找审美溢价机会 |
| **TechCrunch Hardware** | 行业深度流 | 监控获得风投支持的明星创业团队 |
| **The Verge / Engadget** | 全量 RSS | 锁定已经被主流媒体关注的爆发性单品 |
| **Gizmodo / SlashGear** | 科技潮流流 | 寻找具有猎奇属性、容易在 TikTok 传播的 Gadget |
| **Reddit (r/gadgets)** | 高热度 RSS | 聆听全球最挑剔消费者的真实痛点反馈 |


## 3. 主流科技媒体 (Tech Media)
当产品开始发公关稿（PR）或参加展会时，会在这里集中曝光。被他们报道，意味着即将面临大面积的流量曝光。
*   **TechCrunch (Hardware 专栏)**：硅谷风向标，重点报道拿了融资的硬件初创公司。
*   **The Verge / Engadget / Wired**：欧美主流数码消费品测评媒体。
*   **Gizmodo**：偏向猎奇、新奇特、甚至有点怪异的科技硬件。

## 4. 展会与供应链 (Exhibitions & Supply Chain)
从源头看趋势，B2B 端的风口往往比 B2C 早半年。
*   **CES (Las Vegas, 1月)**：全球最大消费电子展，一季度的风向标。
*   **IFA (Berlin, 9月)** / **MWC (Barcelona)**：欧洲和通讯类的顶级硬件展。
*   **Alibaba (新奇特馆/趋势榜)**：中国深圳/东莞/澄海供应链的源头，很多亚马逊爆款其实是工厂在这里先出的公模。

## 5. 社交媒体与评测端 (Social & Reviewers)
流量放大的引爆点。
*   **YouTube (Unbox Therapy, MKBHD 等大V)**：头部科技博主的开箱视频，能瞬间拉爆一个硬件在亚马逊的搜索量。
*   **TikTok (#TikTokMadeMeBuyIt, #TechGadgets)**：新奇特、低客单价（$50以下）、视觉冲击力强的硬件（如氛围灯、桌面玩具）的核心引爆点。

---

## 🛠️ 雷达扩展建议 (Next Steps)
目前 L0 引擎已接入 Kickstarter、Product Hunt 和 Reddit。
未来若需扩容，可通过获取 Indiegogo、TechCrunch 和 Engadget 的 RSS 订阅源，直接注入 `scout_l0_advanced.py` 的 `FEEDS` 列表中，无需更改任何清洗逻辑，大模型会自动处理。
