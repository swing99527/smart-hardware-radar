# 🛰️ 智能硬件全网首发情报源矩阵 (Intelligence Sources)

智能硬件从“概念诞生”到“亚马逊红海厮杀”，通常会经历一个极其标准的生命周期。为了让我们的 **L0 挖掘机** 拥有最敏锐的嗅觉，我们需要在它的生命周期的最早期（概念期、众筹期、极客圈）就截获它。

以下是全球智能硬件产品发布和曝光的核心阵地矩阵：

## 1. 胚胎与验证期：众筹平台 (Crowdfunding)
这是 80% 创新智能硬件的诞生地。团队在这里验证市场需求（Get Funded），此时产品还没上亚马逊，是最高价值的情报源。
*   **Kickstarter (US)**：全球最大的硬核科技、设计硬件首发阵地。（*当前雷达已监控*）
*   **Indiegogo (US)**：Kickstarter 的最大竞品，硬件生态甚至更强，容忍度更高，很多中国出海硬件的首发地。
*   **Makuake / Campfire (Japan)**：日本最大的众筹平台，极度偏向“精巧、收纳、适老、个护”类硬件，是发现精细化微创新的宝库。
*   **Zeczec 啧啧 (Taiwan)**：台湾本土硬件和创意设计的首发站。
*   **Wadiz (Korea)**：韩国最大的众筹平台，偏向高颜值小家电和智能配件。

## 2. 极客与早期采用者社区 (Tech Communities)
这里聚集了最挑剔的早期使用者，产品通常已经有了可用的原型或初版。
*   **Product Hunt**：全球互联网新产品（包含软硬件）的每日打榜阵地。（*当前雷达已监控*）
*   **Hacker News (Y Combinator)**：硅谷极客大本营，如果一个硬件产品在 HN 冲上首页，大概率具备极强的技术壁垒或颠覆性。
*   **Reddit (r/gadgets, r/hardware, r/shutupandtakemymoney)**：欧美最真实的消费者讨论区，能看到未修饰的痛点。（*当前雷达已监控*）

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
