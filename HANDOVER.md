# Smart Hardware Radar - V2 Architecture Handover

## 1. Project Status: "The Great Purge" is Complete
**Repository**: `/Users/chenshangwei/code/smart-hardware-radar/`
**Current State**: 
- **0 Categories, 0 Data, 0 Bullshit.** 我们已经物理清空了所有的“拍脑袋”品类和人工填入的脏数据。
- 评分引擎 (`scripts/score.py` V1.2) 和方法论 (`docs/methodology-hardware.md` V1.2) 已经经历了严苛的“假人碰撞测试”，并在算法中引入了 **“大厂射程一票否决”** 和 **“月销十万美金拓荒期豁免权”** 的底层修正。引擎完美闭环。
- **缺失的环节 (The Blind Spot)**：系统的感知系统 (L0 情绪发现层) 是瞎的。目前 `scripts/scout_l0.py` 只是一个空壳。

## 2. Immediate Next Steps (For Next Agent / Developer)

### **MISSION CRITICAL: 让 L0 层活起来！**

**不要再人工填品类！不要再去想“我要评测什么硬件”！**
你的头号任务，是接上互联网的“呼吸机”，让品类词从市场里自己流进来。

### 🚨 具体开发清单：
1. **实现 Kickstarter 爬虫 (`scripts/scout_l0.py`)**：
   - 使用 BeautifulSoup 或 Selenium 访问 Kickstarter 的 "Technology" 或 "Design" 板块。
   - 抓取过去 7 天内 `Funded > 300%` 或 `Backers > 1000` 的项目标题。
2. **实现 TikTok/YouTube 趋势 API**：
   - 接入 TikTok Creative Center 或 YouTube Trending 的非官方爬虫/API。
   - 检索带有 `#techfinds`, `#smartgadgets` 标签且互动率异常飙升的视频标题。
3. **对接 LLM 大模型进行品类提炼 (The AI Brain)**：
   - 调用一个 LLM API（如 Claude/OpenAI），输入那些杂乱的众筹标题和短视频标题。
   - 要求大模型输出一个泛化的英文品类词。
   - *Example: "PLAUD NOTE ChatGPT Voice Recorder" -> "AI Voice Recorder"*
   - 将该词自动写入 `categories.json`。
4. **自动化串联 (The Cron Loop)**：
   - 建立 Bash 脚本，实现每日凌晨：`scout_l0.py (抓取新词)` -> `accio-mcp-cli JS 接口 (查亚马逊 L2/L3)` -> `cr3.py (算垄断度)` -> `score.py (算总分)`。
   - 只有 `Now Score > 21` 或触发“拓荒期豁免”的新兴蓝海，才通过 webhook 发飞书报警。

## 3. The Prime Directive (铁律)
系统里存在的每一个赛道词，都必须是由脚本从互联网上自动闻出来的情绪。**严禁人类在 `categories.json` 里手动打字。**
