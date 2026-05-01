# Intelligence Sources

L0 now separates weak awareness sources from stronger behavior sources. A source can create `signals`, but only multi-source evidence can create a `category`.

The current product goal is a reliable trend radar, not an automatic SKU recommendation engine. `trend_clusters.json` is the primary output: it groups signals into Hot, Warming, Watch, or Noise based on source mix, behavior evidence, signal strength, and run history.

## Current Sources

| Source | Collection | Source type | Strength |
|---|---|---|---|
| Product Hunt | RSS | `product_launch` | Launch interest |
| Kickstarter Tech / Design | Atom | `crowdfunding` | Early willingness to pay |
| Indiegogo Tech | Public JSON API | `crowdfunding` | Early willingness to pay with backer/funding metrics |
| Hacker News Show | RSS | `community` | Builder interest |
| Reddit r/gadgets | JSON top posts | `community` | Consumer discussion with score/comments |
| Reddit r/hardware | JSON top posts | `community` | Technical buyer discussion |
| Reddit r/smarthome | JSON top posts | `community` | Home automation demand |
| Reddit r/wearabletech | JSON top posts | `community` | Wearable-specific demand |
| Google Trends Daily | RSS | `search` | Search demand spike, filtered through hardware gate |
| GitHub repository search | Search API | `developer` | AI project/model/big-tech peripheral adoption |
| OpenClaw Hardware News | Google News RSS site query | `media` | OpenClaw + hardware/edge/camera/robot intersection |
| Reddit OpenClaw Hardware Search | JSON search | `community` | Niche community mentions around OpenClaw hardware usage |
| Agentic Edge Hardware News | Google News RSS query | `media` | AI agent + local hardware/I/O intersection |
| Reddit Agentic Edge Hardware Search | JSON search | `community` | Niche community mentions around local AI hardware usage |
| 少数派 | RSS | `media` | Chinese consumer-tech and productivity signal |
| 36氪 | RSS | `media` | Chinese startup, AI, and hardware business signal |
| Yanko Design | RSS | `media` | Industrial design awareness |
| TechCrunch Hardware | RSS | `media` | Startup/funding awareness |
| The Verge / Engadget | RSS | `media` | Mainstream product awareness |
| Gizmodo | Google News RSS site query | `media` | Novel gadget awareness; direct Gizmodo RSS currently blocks automation |
| SlashGear | RSS | `media` | Novel gadget awareness |

## Reddit Contract

Reddit is treated as a stronger community signal only when the post has enough engagement:

- `reddit_score >= 50`, or
- `reddit_comments >= 10`

Each Reddit signal stores:

- `reddit_score`
- `reddit_comments`
- `reddit_upvote_ratio`
- `subreddit`
- `created_utc`

Reddit still does not create a category by itself. It must cross-match with another `source_type`, such as media, crowdfunding, search, or marketplace.

For reliable daily runs, configure Reddit OAuth credentials as described in `docs/data_source_credentials.md`. Without `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`, the scanner falls back to public JSON URLs, which can return HTTP 403.

## Watch Topics

`data/watch_topics.json` tracks themes we want to follow even before they become categories:

- Hot GitHub AI projects: agent, MCP, RAG, Ollama, vLLM, ONNX, TFLite, edge AI.
- AI model peripherals: Llama, Qwen, Gemma, DeepSeek, Whisper, CLIP, SAM, NPU.
- Big tech peripherals: OpenAI, Anthropic, Google, Meta, Apple, NVIDIA, Samsung, Amazon, Microsoft, Tesla.
- AI coding agent ecosystem: OpenClaw, Claude Code, OpenAI Codex, Gemini CLI / Gemini Code Assist, and related terminal/coding-agent tools.
- OpenClaw hardware bridge: OpenClaw with camera, robot, edge device, terminal box, keyboard, recorder, local device, gateway, node, ClawBox, or OpenClaw OS.
- Agentic edge hardware: AI agents moving into local hardware, physical I/O, local inference, or edge hubs.
- Local AI box / edge hub: local LLM boxes, AI gateways, NPU boxes, Jetson/Hailo/RK3588/Ryzen AI hubs.
- AI camera / vision node: local AI cameras, RTSP/ONVIF AI, no-cloud cameras, local recognition and recording.
- AI recorder / memory device: AI recorders, meeting recorders, offline transcription, voice memory devices.
- AI keyboard / command deck: AI keyboards, prompt keyboards, macro pads, MCP keyboards, agent command decks.
- Robot / embodied agent kit: robot agents, robot controllers, embodied AI kits, local robot vision/control.
- AI dev kit peripheral: NPU/dev boards, camera modules, sensor kits, MCP/agent dev kits.
- Hardware intersections: smart glasses, camera, robot, wearable, sensor, recorder, doorbell, lock, speaker.

Signals store matched topics in `matched_watch_topics` and `watch:*` tags.

Keywords can be English or Chinese. The matcher preserves Chinese characters during normalization, so topics such as `端侧AI`, `智能门锁`, `摄像头`, and `大模型` can match Chinese source titles without a separate tokenizer.

## Google Trends Contract

Google Trends is collected from the Trending Now RSS export:

- default geo is `US`.
- override with `GOOGLE_TRENDS_GEOS=US,SG,HK`.
- each trend stores `search_query`, `search_geo`, `google_trends_approx_traffic`, and normalized `google_trends_traffic_value`.
- broad non-hardware trends are filtered before signal creation.

Search signals are behavior signals, but they still need cross-source confirmation before a category is promoted.

## Crowdfunding Contract

Kickstarter is collected through Atom feeds. Indiegogo's legacy project RSS currently returns 403, so Indiegogo is collected through the public active crowdfunding projects JSON endpoint instead.

Each Indiegogo signal stores:

- `backers`
- `pledged_usd`
- `funding_goal`
- `currency`
- `comments`
- `updates`
- `rewards`
- campaign start/end dates

Only hardware-looking projects are allowed into `signals.json`.

## Chinese Source Contract

Chinese sources are intentionally a small whitelist:

- `少数派`: stable RSS, Chinese consumer-tech signal.
- `36氪`: stable RSS, Chinese startup/business signal.

Each item stores `source_language: zh`. These are media signals, so they cannot promote a category by themselves; they must combine with community, search, marketplace, crowdfunding, or another independent behavior source.

Unstable candidates such as 机器之心 `/rss` and 量子位 `/feed` were not enabled because they did not return a clean RSS response during verification.

## L0 Scores

Every signal includes `l0_scores`:

- `source_quality`
- `behavior_strength`
- `specificity`
- `watch_relevance`
- `diffusion_stage`
- `signal_strength`

These scores are for triage and explanation only. They do not replace L1-L4 scoring.

## Deduplication And Source Health

L0 is safe to run repeatedly. Signals are deduped by stable source URL hash:

- first sighting creates a new signal id.
- repeat sightings refresh `last_seen_at`, `metrics`, `l0_scores`, and `seen_count`.
- source collector status is stored in `data/source_health.json`, including status, HTTP code, item count, checked time, and rate-limit headers when available.
- source health distinguishes `ok`, `fetch_ok_zero_items`, `fetch_ok_parse_failed`, and `error`.
- extraction uses per-source quotas before applying the global scan limit, so noisy early feeds do not starve Google Trends, Reddit, or GitHub.

This separates "no demand found" from "collector failed".

## GitHub Contract

GitHub repository search is treated as a `developer` behavior signal when repos are popular and recently active.

For reliable daily runs, configure `GITHUB_TOKEN` or `GH_TOKEN`. Authenticated requests materially reduce rate-limit failures, but GitHub Search still has a separate search-rate bucket and can return 403 or 429 when exhausted.

AI coding-agent ecosystem searches are explicitly watch-only:

- OpenClaw ecosystem
- Claude Code ecosystem
- OpenAI Codex / Codex CLI ecosystem
- Gemini CLI / Gemini Code Assist ecosystem

These searches use a lower configurable star threshold, `GITHUB_TOOLCHAIN_MIN_STARS` (default `50`), because toolchain peripherals often emerge before they cross the main `GITHUB_MIN_STARS` threshold. They still do not create categories by themselves.

Each GitHub signal stores:

- `github_stars`
- `github_forks`
- `github_open_issues`
- `github_language`
- `github_pushed_at`
- `github_topics`

GitHub signals still do not create categories by themselves. A hot repo can indicate developer pull around an AI model or hardware-adjacent pattern, but it needs cross-source evidence before it becomes a candidate category.

Implementation note: GitHub signals are stored as `category_eligible: false` by default. They enrich the watch list and downstream analysis, but they do not count toward `categories.json` until explicitly promoted.

## Next Strong Sources

The next best additions are:

1. Kickstarter project metrics: pledged amount, backer count, funding ratio.
2. Product Hunt votes/comments if API access is available.
3. Jungle Scout / Amazon marketplace validation.
