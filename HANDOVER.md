# Smart Hardware Radar - V2 Architecture Handover

## 1. Project Status: L0 Discovery Is Live, Decision Engine Is Being Hardened
**Repository**: `/Users/chenshangwei/code/smart-hardware-radar/`
**Current State**: 
- `data/categories.json` 当前没有可信类目。上一批 8 个泛泛的 L0 自动嗅探词已清空，因为缺少 source_url/source_title 证据和 L2/L3 校验数据。
- L0 主入口是 `scripts/scout_l0_advanced.py`。它现在先把可追溯来源写入 `data/signals.json`，再用证据 gate 聚类成 `data/categories.json`。
- 入库 gate：泛词会被拦截；同一候选类目必须有至少两个不同 `source_type`，且至少一个是行为型来源，才允许进入 `categories.json`。
- Reddit 已升级为 JSON 行为信号源，保存 `reddit_score`、`reddit_comments`、`reddit_upvote_ratio` 等指标；低互动帖子不会进入 `signals.json`。
- GitHub repo search 已作为 `developer` 行为信号源接入，用来跟踪热门 AI 项目、AI 模型周边、大厂周边和硬件交叉点。GitHub signals 默认 `category_eligible: false`，只做 watch-list intelligence，避免软件项目污染硬件类目库。
- `data/watch_topics.json` 是长期关注关键词配置；signals 会写入 `matched_watch_topics` 和 `watch:*` 标签。
- L0 已有传播学评分字段：每条 signal 写入 `l0_scores`，通过 gate 的类目会写入 `l0_evidence`，用于解释 source quality、behavior strength、diffusion stage 和 cross-source confidence。
- `scripts/score.py` 已回到 `docs/methodology-hardware.md` 的 0-25 Now/Trend 分制；缺失的 L1/L4 不再用假分数填充，而是在 `data_quality` 中标注 missing。
- `docs/index.html` 读取 `docs/data.json`；运行 `python scripts/sync_data.py` 可生成 GitHub Pages 数据文件。
- **缺失的环节 (The Blind Spot)**：L1 社媒/众筹数据、L4 供应链数据仍未自动化接入。L2/L3 依赖本地 Accio/Jungle Scout CLI，不能假定 GitHub Actions 环境可直接调用。

## 2. Immediate Next Steps (For Next Agent / Developer)

### **MISSION CRITICAL: 让评分闭环可信起来！**

**不要用占位分数制造推荐结论。**
你的头号任务，是让每个推荐都能追溯到真实数据、缺失数据、否决原因和同步时间。

### 🚨 具体开发清单：
1. **接入真实 L1 数据**：
   - Kickstarter / Indiegogo 项目金额与项目数。
   - YouTube 技术测评播放量。
   - 把这些原始事实先写入 `data/signals.json`，不要直接写 `categories.json`。
2. **接入真实 L4 数据**：
   - 使用 `docs/cost_library.md` 做基准库。
   - 对 PCBA、模具、认证、App/SaaS 成本给出可追溯字段。
3. **补强 L2/L3 数据质量**：
   - `fetch_js_data.py` 已避免 shell 注入，但仍需保存 keyword breadth、PPC、review count。
   - 每个缺失字段都必须出现在 `data_quality`。
4. **自动化串联 (The Cron Loop)**：
   - GitHub Actions 当前可运行 L0、score、sync 和单元测试。
   - L2/L3 仍需要本地 Accio CLI 或可用的云端数据源，不能在 CI 中假装已自动化。

## 3. The Prime Directive (铁律)
系统里存在的每一个赛道词，都必须能追溯到 `data/signals.json` 里的证据。**严禁人类在 `categories.json` 里手动打字。**
