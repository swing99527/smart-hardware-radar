# Data Source Credentials

This radar can run without secrets, but the trustworthy trend layer depends on stable behavior sources. Configure these credentials for daily automation.

## Priority

| Priority | Source | Credential | Why it matters | Fallback without credential |
|---|---|---|---|---|
| P0 | GitHub Search API | `GITHUB_TOKEN` or `GH_TOKEN` | Developer behavior signal for AI projects, local AI hardware, agentic edge hardware, and device kits. | Anonymous GitHub API is heavily rate limited and can return 403 during one run. |
| P0 | Reddit API | `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` | Community behavior signal for buyer/user pain. | Public `www.reddit.com/*.json` often returns 403. |
| P1 | LLM extraction | `LLM_API_KEY`, optional `LLM_BASE_URL`, `LLM_MODEL` | Better structured category extraction from noisy titles. | Heuristic extraction still runs, but quality is lower. |
| P2 | Google Trends RSS | none | Search demand spikes. | No auth needed; source can still change or block because it is an RSS export. |
| P2 | Google News RSS queries | none | Media awareness and niche query coverage. | No auth needed; media-only signals stay Noise until behavior sources confirm. |
| P2 | Kickstarter / Indiegogo / RSS media | none | Crowdfunding, launch, and awareness signals. | No auth needed in the current implementation. |

## Local Setup

Create a local `.env` from `.env.example` and export it before running:

```bash
set -a
source .env
set +a
python3 scripts/scout_l0_advanced.py
```

## GitHub

Set one of:

```bash
GITHUB_TOKEN=...
GH_TOKEN=...
```

The scanner sends the token only as an `Authorization` header. It is not written to `data/source_health.json`; source health stores only `auth_mode: token`.

In GitHub Actions, the workflow passes the built-in `secrets.GITHUB_TOKEN` to the scout step. This improves reliability over anonymous requests, though GitHub Search still has its own tighter search bucket and secondary rate limits.

## Reddit

Set:

```bash
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=smart-hardware-radar/1.0 by your-reddit-username
```

When these are present, the scanner requests an application-only OAuth token with `client_credentials` and reads from `https://oauth.reddit.com/...`. If they are absent, it falls back to public JSON URLs.

## GitHub Actions Secrets

Add these repository secrets:

- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT`
- `LLM_API_KEY` if LLM extraction is desired
- `LLM_BASE_URL` and `LLM_MODEL` only if using a non-default provider/model

`GITHUB_TOKEN` does not need to be manually added for GitHub Actions; GitHub provides it automatically to the workflow.

## Source Health Expectations

`data/source_health.json` should make failures explicit:

- `auth_mode: token` for authenticated GitHub.
- `auth_mode: reddit_oauth` for authenticated Reddit.
- `auth_mode: public_json` for Reddit fallback.
- `status: error` with HTTP 403 or 429 when a source is blocked or rate limited.
- `rate_limit` fields when the upstream response includes rate-limit headers.

Trend labels should be interpreted with source health in mind. If Reddit or GitHub is unhealthy, a media-only trend should remain `Noise` rather than being promoted.

Run the health check after collection:

```bash
python3 scripts/check_source_health.py --warn-only
```

Use `--strict` only when you want CI to fail on required source failures. The daily workflow currently runs warn-only so that dashboard artifacts still publish even when a source is degraded.
