# L0 Discovery Pipeline v1.1

> L0 不直接生产“可投类目”。L0 先收集可追溯信号，再把多源证据聚类成候选类目。

## 1. Two-Layer Contract

```text
RSS / launch / community / marketplace sources
  -> data/signals.json       # raw evidence, source-linked
  -> data/watch_topics.json  # tracked themes and keywords
  -> data/trend_runs.json    # per-run snapshots for velocity
  -> data/trend_clusters.json # current Hot/Warming/Watch/Noise radar
  -> data/market_theses.json # market thesis, evidence gaps, next validation
  -> evidence gate
  -> data/categories.json    # later enrichment candidates only after gate
```

`data/signals.json` 是事实层。每条 signal 必须包含：

- `source_type`
- `source_name`
- `source_url`
- `source_title`
- `raw_text`
- `observed_at`
- `candidate_category`
- `extraction_engine`
- `metrics`
- `matched_watch_topics`
- `l0_scores`

`data/trend_clusters.json` 是当前产品的主视图。它不输出“上新品推荐”，只解释哪些智能硬件方向正在变热、证据来自哪里、可信度为什么足够或不足。

`data/market_theses.json` 是战略层。它把 trend cluster 翻译成“智能硬件细分市场假设”：用户任务、硬件形态、买家段、证据状态、缺失证据和下一步验证动作。当前版本是 deterministic rules，不用 LLM 作结论；媒体-only 或 supply 缺失的方向不能进入 `Ready for Selection`。

`data/categories.json` 是后续选品验证入口。类目只有在通过 gate 后才能写入，但当前阶段不把它当作最终推荐。

## 2. Evidence Gate

候选类目写入 `categories.json` 前必须满足：

1. 不是泛词。`Smartphone`、`Smartwatch`、`Smart Glasses`、`Robot`、`Wearable Device` 等直接拦截。
2. 至少 2 个不同 `source_type` 命中同一候选类目。
3. 至少 1 个命中来自行为型来源：`crowdfunding`、`product_launch`、`community`、`marketplace`、`search`。
4. 每个证据都必须有 `source_url` 和 `source_title`。
5. LLM 只能提炼候选词，不能单独作为证据。

重复运行策略：

- 同一个 `source_url` / `dedupe_key` 不新增第二条 signal。
- 重复命中会刷新 `last_seen_at`、`metrics`、`l0_scores`，并累加 `seen_count`。
- 历史 signal 会自动补齐 `first_seen_at`、`last_seen_at`、`seen_count` 和 gate 状态。
- 每次运行都会写入 `trend_runs.json`，记录当前 run 的 cluster 数量、source mix 和平均强度，供趋势速度判断使用。

## 3. Current Source Types

| Source type | Examples | Role |
|---|---|---|
| `crowdfunding` | Kickstarter, Indiegogo | Early willingness to pay |
| `product_launch` | Product Hunt | Launch velocity proxy |
| `community` | Reddit, Hacker News | Pain/discussion proxy |
| `developer` | GitHub repository search | Hot AI project / developer adoption proxy |
| `product_reference` | Stream Deck, ZSA, Keychron, Wooting, Loupedeck, Work Louder, CharaChorder, Naya, Glove80 | First-party incumbent/productization context |
| `media` | The Verge, Engadget, TechCrunch | Weak awareness signal |
| `marketplace` | Amazon / Jungle Scout | Commercial validation |
| `search` | Google Trends / keyword tools | Demand validation |

Reddit is collected through JSON listing endpoints, not RSS, so signals preserve `reddit_score`, `reddit_comments`, `reddit_upvote_ratio`, `subreddit`, and `created_utc`. Low-engagement Reddit posts are dropped before they reach `signals.json`.

GitHub repository search is collected through the public Search API. It preserves `github_stars`, `github_forks`, `github_open_issues`, `github_language`, `github_pushed_at`, and `github_topics`. GitHub signals are useful for AI project/model/big-tech periphery tracking, but they still need cross-source confirmation before a category is created.

GitHub signals are currently `category_eligible: false` by default. They are watch-list intelligence, not category evidence, because most hot AI repos are software projects. Promote a GitHub source to category-eligible only when the query and parser are proven hardware-specific.

AI coding-agent ecosystem monitoring is also watch-only. It tracks OpenClaw, Claude Code, OpenAI Codex / Codex CLI, and Gemini CLI / Gemini Code Assist using a lower `GITHUB_TOOLCHAIN_MIN_STARS` threshold so emerging peripheral tools can show up in the Signal Inbox before they become large repositories.

Agentic edge hardware monitoring is the broader version of that watch-list. It tracks AI agents combined with physical I/O or local inference hardware: local AI boxes, AI cameras, AI recorders, AI keyboards/command decks, robot agent kits, and AI dev kit peripherals. These signals stay watch-only until independent behavior sources prove real demand.

Geek AI productivity hardware monitoring tracks the smaller high-ticket segment around programmable keyboards, macro pads, creative consoles, workflow controllers and AI coding workflow entry points. Its source mix intentionally uses first-party DTC product sites, QMK/ZMK/VIA firmware ecosystems, Kickstarter/Indiegogo projects, Reddit keyboard/workspace communities, and developer workflow/plugin ecosystems instead of IDC-style category reports.

Media-only signals are useful, but they do not create categories by themselves.

## 4. Daily Flow

```text
scripts/scout_l0_advanced.py
  1. fetch RSS feeds, JSON sources, Reddit listings, and GitHub repository searches
  2. keep source-linked hardware-looking items with per-source quotas, avoiding fixed source-order bias
  3. tag matched watch topics from data/watch_topics.json
  4. extract specific category candidate
  5. write new evidence to data/signals.json
  6. cluster existing signals into data/trend_clusters.json
  7. generate data/market_theses.json with evidence gaps and next validation actions
  8. write categories only when the evidence gate passes, for later L1-L4 validation
```

Google Trends RSS is included as a `search` source. It is not treated as an absolute demand number; the normalized traffic field is a behavior-strength proxy and still requires cross-source confirmation before promotion.

Indiegogo is collected through its public active crowdfunding projects JSON endpoint because the legacy project RSS endpoint returns 403. Gizmodo is collected through a Google News RSS site query because direct Gizmodo RSS endpoints currently block automated fetches.

Clustering is intentionally two-stage:

1. Deterministic alias/rule clusters merge obvious demand families, such as lock/deadbolt/doorbell/outdoor camera into smart-home security.
2. LLM extraction may suggest a normalized category, but LLM output is structured JSON and must still pass schema validation plus evidence gate. LLM is not allowed to directly promote a category.

中文支持：

- `normalize_text` 保留中文字符，避免中文标题、关键词、类目在去重和聚类时被清空。
- 硬件词、泛词、限定词支持中文，例如 `智能门锁`、`户外摄像头`、`AI会议记录仪`。
- `watch_topics.json` 可以混合配置英文和中文关键词。
- 已验证中文 RSS 源会写入 `source_language: zh`，当前启用少数派和 36氪。
- Dashboard 优先展示 `name_zh` / `cluster_name_zh`，没有中文名时回退到英文名。

Downstream:

```text
data/categories.json
  -> scripts/fetch_js_data.py   # L2/L3 marketplace data
  -> scripts/score.py           # methodology v1.0 scores
  -> scripts/sync_data.py       # docs/data.json for dashboard
```

## 5. L0 Scoring

L0 scores are not commercial scores. They translate communication theory into machine-readable sorting fields.

Each signal gets:

| Field | Meaning |
|---|---|
| `source_quality` | Source role strength. Media is weak awareness; search/marketplace is strongest behavior. |
| `behavior_strength` | Observable action intensity, such as Reddit comments or GitHub stars. |
| `specificity` | Whether the candidate names a concrete hardware use case rather than a broad category. |
| `watch_relevance` | How many configured watch topics matched. |
| `diffusion_stage` | Communication stage: `innovator`, `early_adopter`, `opinion_leader`, `early_majority`, etc. |
| `signal_strength` | Weighted L0 sort score for triage. |

Categories that pass the evidence gate get `l0_evidence`:

```json
{
  "source_types": ["community", "media"],
  "cross_source_count": 2,
  "has_behavior_source": true,
  "diffusion_stage": "two_step_confirmed",
  "avg_signal_strength": 2.4,
  "matched_watch_topics": ["hardware_intersections"],
  "l0_confidence": 0.62
}
```

This maps communication theory to rules:

- Innovation diffusion: developer/product launch signals are `innovator`; community/crowdfunding are early adopter signals; search/marketplace are early majority signals.
- Two-step flow: media + community becomes `two_step_confirmed`.
- Agenda setting: media-only remains awareness and does not create categories.
- Social proof: comments, stars, backers, search, and marketplace metrics increase behavior strength.

## 6. Prime Directive

Do not manually add categories. Add better signal collectors and better trend evidence.

If a category cannot answer “which signals created this and where are their URLs?”, it does not belong in `categories.json`.

If a trend cannot answer “which run snapshots prove this is recurring or warming?”, it should stay `Watch`, not `Hot`.
