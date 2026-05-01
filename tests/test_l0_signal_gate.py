import importlib.util
import os
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("scout_l0_advanced", ROOT / "scripts" / "scout_l0_advanced.py")
scout = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scout)


class L0SignalGateTest(unittest.TestCase):
    def signal(self, signal_id, source_type, category):
        return {
            "id": signal_id,
            "source_type": source_type,
            "source_name": source_type.title(),
            "source_url": f"https://example.com/{signal_id}",
            "source_title": f"{category} source",
            "raw_text": f"{category} source",
            "observed_at": "2026-04-30T00:00:00Z",
            "candidate_category": category,
            "candidate_key": scout.normalize_text(category),
            "extraction_engine": "TEST",
            "metrics": {},
            "tags": ["hardware_keyword_match"],
            "matched_watch_topics": [],
            "l0_scores": scout.l0_scores_for_signal(source_type, category, {}, []),
            "dedupe_key": signal_id,
        }

    def test_generic_categories_are_rejected(self):
        self.assertTrue(scout.is_generic_category("Smart Glasses"))
        self.assertTrue(scout.is_generic_category("Ai Glasses"))
        self.assertTrue(scout.is_generic_category("Smart Home Device"))
        self.assertTrue(scout.is_generic_category("Smartwatch"))
        self.assertTrue(scout.is_generic_category("智能设备"))
        self.assertTrue(scout.is_generic_category("机器人"))
        self.assertFalse(scout.is_generic_category("AI Meeting Recorder"))
        self.assertFalse(scout.is_generic_category("智能门锁"))

    def test_signal_quality_requires_specific_hardware_noun(self):
        self.assertTrue(scout.is_specific_hardware_category("AI Meeting Recorder"))
        self.assertTrue(scout.is_specific_hardware_category("Dictation Device"))
        self.assertTrue(scout.is_specific_hardware_category("Gaming Keyboard"))
        self.assertTrue(scout.is_specific_hardware_category("Outdoor Camera"))
        self.assertTrue(scout.is_specific_hardware_category("Smart Deadbolt"))
        self.assertTrue(scout.is_specific_hardware_category("智能门锁"))
        self.assertTrue(scout.is_specific_hardware_category("AI会议记录仪"))
        self.assertFalse(scout.is_specific_hardware_category("Task Manager For AI Agents"))
        self.assertFalse(scout.is_specific_hardware_category("Journey Through Chai Documentary"))
        self.assertFalse(scout.is_specific_hardware_category("Dreame, The Robot"))
        self.assertFalse(scout.is_specific_hardware_category("计划软件"))
        self.assertFalse(scout.is_specific_hardware_category("杭州为具身智能机器人立法，今起施行"))

    def test_candidate_normalization_strips_possessive_brand(self):
        self.assertEqual(scout.normalize_category_candidate("SpeakON’s Dictation Device"), "Dictation Device")
        self.assertEqual(scout.normalize_category_candidate("Logitech G512 X Gaming Keyboard"), "Gaming Keyboard")
        self.assertEqual(scout.normalize_category_candidate("Video doorbell with local recording"), "Video Doorbell Local Recording")
        self.assertEqual(scout.normalize_category_candidate(" 智能 门锁 "), "智能门锁")

    def test_chinese_feed_items_keep_language(self):
        items = []
        scout.append_hardware_item(
            items,
            "端侧 AI 摄像头进入量产阶段",
            "https://example.cn/edge-ai-camera",
            {"name": "中文源", "source_type": "media", "source_language": "zh"},
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["source_language"], "zh")
        signal = scout.signal_from_item(items[0], "端侧AI摄像头", "TEST", "2026-05-01T00:00:00Z", [])
        self.assertEqual(signal["source_language"], "zh")

    def test_targeted_feed_can_attach_watch_only_candidate(self):
        items = []
        scout.append_hardware_item(
            items,
            "Best hardware options for deploying OpenClaw",
            "https://example.com/openclaw-hardware",
            {
                "name": "OpenClaw Hardware News",
                "source_type": "media",
                "source_language": "en",
                "candidate_category": "OpenClaw Hardware Bridge",
                "category_eligible": False,
                "extraction_engine": "QUERY",
            },
        )

        self.assertEqual(items[0]["candidate_category"], "OpenClaw Hardware Bridge")
        self.assertFalse(items[0]["category_eligible"])

    def test_chinese_text_is_preserved_for_matching(self):
        self.assertEqual(scout.normalize_text("端侧 AI 摄像头"), "端侧 ai 摄像头")
        self.assertTrue(scout.contains_any("无订阅智能门锁方案", {"智能门锁", "门铃"}))

    def test_reddit_listing_requires_engagement_and_keeps_metrics(self):
        payload = {
            "data": {
                "children": [
                    {
                        "data": {
                            "title": "This AI meeting recorder solved my note taking problem",
                            "score": 120,
                            "num_comments": 36,
                            "upvote_ratio": 0.92,
                            "subreddit": "gadgets",
                            "created_utc": 1777500000,
                            "permalink": "/r/gadgets/comments/abc/ai_meeting_recorder/",
                        }
                    },
                    {
                        "data": {
                            "title": "A neat smart sensor nobody discussed",
                            "score": 4,
                            "num_comments": 1,
                            "permalink": "/r/gadgets/comments/def/quiet_sensor/",
                        }
                    },
                ]
            }
        }

        items = scout.parse_reddit_listing(payload, {"name": "Reddit r/gadgets"})

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["source_type"], "community")
        self.assertEqual(items[0]["metrics"]["reddit_score"], 120)
        self.assertEqual(items[0]["metrics"]["reddit_comments"], 36)
        self.assertIn("reddit_engagement", items[0]["tags"])

    def test_reddit_search_sources_can_lower_engagement_threshold(self):
        payload = {
            "data": {
                "children": [
                    {
                        "data": {
                            "title": "OpenClaw camera node on an edge device",
                            "score": 2,
                            "num_comments": 0,
                            "permalink": "/r/selfhosted/comments/abc/openclaw_camera/",
                        }
                    }
                ]
            }
        }

        items = scout.parse_reddit_listing(
            payload,
            {"name": "Reddit OpenClaw Hardware Search", "min_score": 1, "min_comments": 1},
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["source_type"], "community")

    def test_targeted_reddit_search_attaches_watch_only_candidate(self):
        payload = {
            "data": {
                "children": [
                    {
                        "data": {
                            "title": "OpenClaw robot camera gateway build",
                            "score": 1,
                            "num_comments": 0,
                            "permalink": "/r/homeassistant/comments/abc/openclaw_robot/",
                        }
                    }
                ]
            }
        }

        items = scout.parse_reddit_listing(
            payload,
            {
                "name": "Reddit OpenClaw Hardware Search",
                "min_score": 1,
                "min_comments": 1,
                "candidate_category": "OpenClaw Hardware Bridge",
                "category_eligible": False,
                "extraction_engine": "QUERY",
            },
        )

        self.assertEqual(items[0]["candidate_category"], "OpenClaw Hardware Bridge")
        self.assertFalse(items[0]["category_eligible"])

    def test_github_repositories_keep_developer_metrics(self):
        payload = {
            "items": [
                {
                    "full_name": "example/edge-ai-camera",
                    "description": "Edge AI camera pipeline using ONNX",
                    "html_url": "https://github.com/example/edge-ai-camera",
                    "stargazers_count": 1200,
                    "forks_count": 80,
                    "open_issues_count": 7,
                    "language": "Python",
                    "pushed_at": "2026-04-29T00:00:00Z",
                    "topics": ["edge-ai", "camera", "onnx"],
                },
                {
                    "full_name": "example/small",
                    "description": "Not enough stars",
                    "html_url": "https://github.com/example/small",
                    "stargazers_count": 12,
                },
            ]
        }

        items = scout.parse_github_repositories(
            payload,
            {"name": "GitHub Edge AI Camera", "candidate_category": "Edge AI Camera", "category_eligible": False},
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["source_type"], "developer")
        self.assertEqual(items[0]["candidate_category"], "Edge AI Camera")
        self.assertFalse(items[0]["category_eligible"])
        self.assertEqual(items[0]["metrics"]["github_stars"], 1200)
        self.assertIn("github_repo", items[0]["tags"])

    def test_github_repositories_can_use_source_specific_min_stars(self):
        payload = {
            "items": [
                {
                    "full_name": "example/claude-code-tool",
                    "description": "Claude Code helper for terminal agent workflows",
                    "html_url": "https://github.com/example/claude-code-tool",
                    "stargazers_count": 120,
                    "forks_count": 8,
                    "open_issues_count": 2,
                    "language": "TypeScript",
                    "pushed_at": "2026-04-29T00:00:00Z",
                    "topics": ["claude-code", "coding-agent"],
                }
            ]
        }

        items = scout.parse_github_repositories(
            payload,
            {
                "name": "GitHub Claude Code Ecosystem",
                "candidate_category": "AI Coding Agent Ecosystem",
                "category_eligible": False,
                "min_stars": 50,
            },
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["candidate_category"], "AI Coding Agent Ecosystem")
        self.assertEqual(items[0]["metrics"]["github_stars"], 120)

    def test_ai_coding_agent_watch_topic_matches_requested_tools(self):
        topics = [
            {
                "id": "ai_coding_agent_ecosystem",
                "keywords": ["openclaw", "claude code", "codex cli", "gemini cli", "代码智能体"],
            }
        ]

        self.assertEqual(scout.match_watch_topics("OpenClaw terminal workflow", topics), ["ai_coding_agent_ecosystem"])
        self.assertEqual(scout.match_watch_topics("Claude Code helper", topics), ["ai_coding_agent_ecosystem"])
        self.assertEqual(scout.match_watch_topics("Codex CLI extension", topics), ["ai_coding_agent_ecosystem"])
        self.assertEqual(scout.match_watch_topics("Gemini CLI automation", topics), ["ai_coding_agent_ecosystem"])
        self.assertEqual(scout.match_watch_topics("代码智能体周边工具", topics), ["ai_coding_agent_ecosystem"])

    def test_google_trends_rss_keeps_search_metrics(self):
        xml = b"""<?xml version="1.0" encoding="UTF-8"?>
        <rss xmlns:ht="https://trends.google.com/trends/trendingsearches/daily">
          <channel>
            <item>
              <title>outdoor security camera</title>
              <link>https://trends.google.com/trends/trendingsearches/daily?geo=US#outdoor-security-camera</link>
              <ht:approx_traffic>50K+</ht:approx_traffic>
              <ht:news_item_title>Outdoor camera with local recording is trending</ht:news_item_title>
            </item>
            <item>
              <title>football scores</title>
              <link>https://example.com/sports</link>
              <ht:approx_traffic>200K+</ht:approx_traffic>
            </item>
          </channel>
        </rss>"""

        items = scout.parse_google_trends_rss(
            xml,
            {"name": "Google Trends US Daily", "source_type": "search", "geo": "US"},
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["source_type"], "search")
        self.assertEqual(items[0]["metrics"]["search_query"], "outdoor security camera")
        self.assertEqual(items[0]["metrics"]["google_trends_traffic_value"], 50000)
        self.assertIn("google_trends_daily", items[0]["tags"])

    def test_google_trends_new_rss_namespace_is_supported(self):
        xml = b"""<?xml version="1.0" encoding="UTF-8"?>
        <rss xmlns:ht="https://trends.google.com/trending/rss">
          <channel>
            <item>
              <title>smart lock</title>
              <link>https://trends.google.com/trending/rss?geo=US</link>
              <ht:approx_traffic>10,000+</ht:approx_traffic>
              <ht:news_item>
                <ht:news_item_title>Best smart lock deals without subscriptions</ht:news_item_title>
                <ht:news_item_url>https://example.com/smart-lock-news</ht:news_item_url>
              </ht:news_item>
            </item>
          </channel>
        </rss>"""

        items = scout.parse_google_trends_rss(
            xml,
            {"name": "Google Trends US Daily", "source_type": "search", "geo": "US"},
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["link"], "https://example.com/smart-lock-news")
        self.assertEqual(items[0]["metrics"]["google_trends_traffic_value"], 10000)

    def test_gizmodo_uses_google_news_rss_fallback(self):
        gizmodo = next(feed for feed in scout.FEEDS if feed["name"] == "Gizmodo")

        self.assertEqual(gizmodo["source_type"], "media")
        self.assertIn("news.google.com/rss/search", gizmodo["url"])
        self.assertIn("site%3Agizmodo.com", gizmodo["url"])

    def test_indiegogo_projects_parse_from_public_api(self):
        payload = [
            {
                "projectName": "Local AI Doorbell",
                "projectHomeUrl": "https://www.indiegogo.com/projects/local-ai-doorbell/example",
                "shortDescription": "A smart doorbell camera with local recording and no subscription.",
                "backerCount": 142,
                "fundsGathered": 52000.5,
                "campaignGoal": 25000,
                "currencyShortName": "USD",
                "commentCount": 12,
                "updateCount": 3,
                "rewardCount": 4,
                "campaignStartDate": "2026-05-01T00:00:00Z",
                "campaignEndDate": "2026-06-01T00:00:00Z",
            },
            {
                "projectName": "Short Film",
                "projectHomeUrl": "https://www.indiegogo.com/projects/short-film/example",
                "shortDescription": "A documentary project with no hardware.",
            },
        ]

        items = scout.parse_indiegogo_projects(payload, {"name": "Indiegogo Tech", "source_language": "en"})

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["source_type"], "crowdfunding")
        self.assertEqual(items[0]["source_name"], "Indiegogo Tech")
        self.assertEqual(items[0]["metrics"]["backers"], 142)
        self.assertEqual(items[0]["metrics"]["pledged_usd"], 52000.5)
        self.assertIn("indiegogo_project", items[0]["tags"])

    def test_search_behavior_strength_uses_google_trends_traffic(self):
        self.assertEqual(scout.behavior_strength("search", {"google_trends_traffic_value": 120000}), 5)
        self.assertEqual(scout.behavior_strength("search", {"google_trends_traffic_value": 50000}), 4)
        self.assertEqual(scout.behavior_strength("search", {"google_trends_traffic_value": 1000}), 3)

    def test_watch_topics_are_tagged_on_signals(self):
        topics = [
            {"id": "github_ai_projects", "keywords": ["edge ai", "onnx"]},
            {"id": "hardware_intersections", "keywords": ["camera", "摄像头"]},
        ]
        item = {
            "title": "Edge AI camera pipeline using ONNX",
            "link": "https://github.com/example/edge-ai-camera",
            "source_name": "GitHub Edge AI Camera",
            "source_type": "developer",
            "metrics": {"github_topics": ["edge-ai", "camera", "onnx"]},
            "tags": ["github_repo"],
        }

        signal = scout.signal_from_item(item, "Edge AI Camera", "QUERY", "2026-04-30T00:00:00Z", topics)

        self.assertEqual(signal["matched_watch_topics"], ["github_ai_projects", "hardware_intersections"])
        self.assertIn("watch:github_ai_projects", signal["tags"])
        self.assertIn("watch:hardware_intersections", signal["tags"])
        self.assertEqual(signal["l0_scores"]["diffusion_stage"], "innovator")
        self.assertGreater(signal["l0_scores"]["signal_strength"], 0)
        self.assertEqual(signal["seen_count"], 1)

    def test_chinese_watch_topics_are_tagged_on_signals(self):
        topics = [
            {"id": "github_ai_projects", "keywords": ["端侧 ai"]},
            {"id": "hardware_intersections", "keywords": ["摄像头"]},
        ]
        item = {
            "title": "端侧 AI 摄像头项目，支持本地视觉识别",
            "link": "https://example.com/cn-edge-camera",
            "source_name": "Example",
            "source_type": "developer",
            "metrics": {},
            "tags": [],
        }

        signal = scout.signal_from_item(item, "端侧AI摄像头", "TEST", "2026-04-30T00:00:00Z", topics)

        self.assertEqual(signal["matched_watch_topics"], ["github_ai_projects", "hardware_intersections"])
        self.assertEqual(signal["candidate_key"], "端侧ai摄像头")

    def test_openclaw_hardware_topic_gets_trend_priority(self):
        signal = self.signal("S001", "developer", "OpenClaw Hardware Bridge")
        signal["category_eligible"] = False
        signal["matched_watch_topics"] = [
            "github_ai_projects",
            "hardware_intersections",
            "ai_coding_agent_ecosystem",
            "openclaw_hardware_bridge",
        ]

        self.assertEqual(scout.trend_key_for_signal(signal), "watch:openclaw_hardware_bridge")

    def test_agentic_edge_hardware_topic_gets_trend_priority(self):
        signal = self.signal("S001", "developer", "Agentic Edge Hardware")
        signal["category_eligible"] = False
        signal["matched_watch_topics"] = [
            "github_ai_projects",
            "hardware_intersections",
            "ai_coding_agent_ecosystem",
            "agentic_edge_hardware",
        ]

        self.assertEqual(scout.trend_key_for_signal(signal), "watch:agentic_edge_hardware")

    def test_agentic_edge_subtopic_labels_are_named(self):
        self.assertEqual(
            scout.trend_name_for_signals("watch:local_ai_box", []),
            "Local AI Box",
        )
        self.assertEqual(
            scout.trend_name_for_signals("watch:ai_camera_node", []),
            "AI Camera Node",
        )

    def test_llm_json_must_be_structured(self):
        accepted = scout.parse_llm_json(
            '{"decision":"accept","category":"AI Meeting Recorder","hardware_noun":"recorder","use_case":"meeting notes","confidence":0.82,"reject_reason":null}'
        )
        rejected = scout.parse_llm_json(
            '{"decision":"reject","category":null,"hardware_noun":null,"use_case":null,"confidence":0.91,"reject_reason":"software"}'
        )
        invalid = scout.parse_llm_json('"AI Meeting Recorder"')

        self.assertEqual(accepted["category"], "AI Meeting Recorder")
        self.assertEqual(accepted["decision"], "accept")
        self.assertEqual(rejected["decision"], "reject")
        self.assertIsNone(invalid)

    def test_llm_json_accepts_chinese_category(self):
        accepted = scout.parse_llm_json(
            '{"decision":"accept","category":"AI会议记录仪","hardware_noun":"记录仪","use_case":"会议纪要","confidence":0.88,"reject_reason":null}'
        )

        self.assertEqual(accepted["category"], "AI会议记录仪")

    def test_duplicate_signal_refreshes_without_new_row(self):
        item = {
            "title": "Outdoor camera for remote viewing without monthly fees?",
            "link": "https://www.reddit.com/r/smarthome/comments/abc/outdoor_camera/",
            "source_name": "Reddit r/smarthome",
            "source_type": "community",
            "metrics": {"reddit_score": 10, "reddit_comments": 20},
            "tags": ["reddit_engagement"],
        }
        signals_doc = {"signals": []}
        first = scout.signal_from_item(item, "Outdoor Camera", "NLP", "2026-04-30T00:00:00Z", [])
        added, refreshed = scout.append_new_signals(signals_doc, [first])
        second = scout.signal_from_item(
            {**item, "metrics": {"reddit_score": 40, "reddit_comments": 35}},
            "Outdoor Camera",
            "NLP",
            "2026-05-01T00:00:00Z",
            [],
        )
        added_again, refreshed_again = scout.append_new_signals(signals_doc, [second])

        self.assertEqual((added, refreshed), (1, 0))
        self.assertEqual((added_again, refreshed_again), (0, 1))
        self.assertEqual(len(signals_doc["signals"]), 1)
        self.assertEqual(signals_doc["signals"][0]["seen_count"], 2)
        self.assertEqual(signals_doc["signals"][0]["last_seen_at"], "2026-05-01T00:00:00Z")
        self.assertEqual(signals_doc["signals"][0]["metrics"]["reddit_comments"], 35)

    def test_existing_signals_are_schema_normalized(self):
        signals_doc = {
            "signals": [
                {
                    "id": "S001",
                    "observed_at": "2026-04-30T00:00:00Z",
                    "category_eligible": True,
                    "tags": ["hardware_keyword_match"],
                }
            ]
        }

        scout.normalize_signal_schema(signals_doc)

        signal = signals_doc["signals"][0]
        self.assertEqual(signal["first_seen_at"], "2026-04-30T00:00:00Z")
        self.assertEqual(signal["last_seen_at"], "2026-04-30T00:00:00Z")
        self.assertEqual(signal["seen_count"], 1)
        self.assertEqual(signal["gate_status"], "held")

    def test_invalid_existing_signals_are_pruned(self):
        valid = self.signal("S001", "media", "智能门锁")
        invalid = self.signal("S002", "media", "杭州为具身智能机器人立法，今起施行")
        signals_doc = {"signals": [valid, invalid]}

        removed = scout.prune_invalid_signals(signals_doc)

        self.assertEqual(removed, 1)
        self.assertEqual([signal["id"] for signal in signals_doc["signals"]], ["S001"])

    def test_source_health_prunes_stale_url_for_same_source(self):
        health_doc = {
            "sources": [
                {
                    "source_name": "Google Trends US Daily",
                    "url": "https://trends.google.com/old/rss",
                    "query": None,
                    "status": "error",
                }
            ]
        }
        updated = scout.update_source_health_doc(
            health_doc,
            [
                {
                    "source_name": "Google Trends US Daily",
                    "source_type": "search",
                    "url": "https://trends.google.com/trending/rss?geo=US&hl=en-US",
                    "query": None,
                    "status": "ok",
                    "checked_at": "2026-05-01T00:00:00Z",
                    "item_count": 0,
                }
            ],
        )

        self.assertEqual(len(updated["sources"]), 1)
        self.assertEqual(updated["sources"][0]["status"], "ok")
        self.assertEqual(updated["sources"][0]["url"], "https://trends.google.com/trending/rss?geo=US&hl=en-US")

    def test_parse_health_distinguishes_parse_failure_and_zero_items(self):
        parse_failed = scout.annotate_parse_health(
            {"status": "ok", "checked_at": "2026-05-01T00:00:00Z"},
            [],
            ValueError("bad xml"),
        )
        zero_items = scout.annotate_parse_health(
            {"status": "ok", "checked_at": "2026-05-01T00:00:00Z"},
            [],
            None,
        )

        self.assertEqual(parse_failed["status"], "fetch_ok_parse_failed")
        self.assertEqual(zero_items["status"], "fetch_ok_zero_items")

    def test_source_health_records_auth_mode_without_secret_material(self):
        entry = scout.source_health_entry(
            {"name": "GitHub Test", "source_type": "developer", "auth_mode": "token"},
            "https://api.github.com/search/repositories",
            "2026-05-01T00:00:00Z",
            "ok",
        )

        self.assertEqual(entry["auth_mode"], "token")
        self.assertNotIn("Authorization", entry)

    def test_github_auth_headers_use_github_token(self):
        old_token = os.environ.get("GITHUB_TOKEN")
        old_gh_token = os.environ.get("GH_TOKEN")
        os.environ["GITHUB_TOKEN"] = "test-token"
        os.environ.pop("GH_TOKEN", None)
        try:
            headers = scout.github_auth_headers()
        finally:
            if old_token is None:
                os.environ.pop("GITHUB_TOKEN", None)
            else:
                os.environ["GITHUB_TOKEN"] = old_token
            if old_gh_token is None:
                os.environ.pop("GH_TOKEN", None)
            else:
                os.environ["GH_TOKEN"] = old_gh_token

        self.assertEqual(headers["Authorization"], "Bearer test-token")
        self.assertEqual(headers["X-GitHub-Api-Version"], "2022-11-28")

    def test_reddit_oauth_url_keeps_path_and_query(self):
        url = scout.reddit_oauth_url("https://www.reddit.com/r/gadgets/top.json?t=week&limit=50")

        self.assertEqual(url, "https://oauth.reddit.com/r/gadgets/top.json?t=week&limit=50")

    def test_per_source_scan_limit_keeps_late_sources_visible(self):
        old_scan_limit = scout.SOURCE_SCAN_LIMIT
        old_per_source = scout.SOURCE_SCAN_PER_SOURCE_LIMIT
        scout.SOURCE_SCAN_LIMIT = 6
        scout.SOURCE_SCAN_PER_SOURCE_LIMIT = 2
        try:
            items = [
                {"source_name": "A", "title": f"A{i}", "link": f"https://a/{i}"}
                for i in range(10)
            ] + [
                {"source_name": "B", "title": f"B{i}", "link": f"https://b/{i}"}
                for i in range(10)
            ] + [
                {"source_name": "C", "title": f"C{i}", "link": f"https://c/{i}"}
                for i in range(10)
            ]

            selected = scout.select_items_for_scan(items)
        finally:
            scout.SOURCE_SCAN_LIMIT = old_scan_limit
            scout.SOURCE_SCAN_PER_SOURCE_LIMIT = old_per_source

        self.assertEqual(len(selected), 6)
        self.assertEqual({item["source_name"] for item in selected}, {"A", "B", "C"})

    def test_trend_clusters_build_status_and_run_history(self):
        signals_doc = {
            "signals": [
                self.signal("S001", "community", "Outdoor Camera"),
                self.signal("S002", "media", "Smart Deadbolt"),
                self.signal("S003", "crowdfunding", "Video Doorbell Local Recording"),
            ]
        }
        for signal in signals_doc["signals"]:
            signal["cluster_key"] = scout.cluster_key_for_signal(signal)
            signal["last_seen_at"] = "2026-05-01T00:00:00Z"
            signal["l0_scores"]["signal_strength"] = 3.2

        clusters_doc, runs_doc = scout.build_trend_clusters(
            signals_doc,
            {"runs": []},
            "2026-05-01T00:00:00Z",
        )

        self.assertEqual(len(runs_doc["runs"]), 1)
        cluster = clusters_doc["clusters"][0]
        self.assertEqual(cluster["trend_status"], "Hot")
        self.assertEqual(cluster["trend_key"], "cluster:smart_home_security")
        self.assertEqual(cluster["signal_count"], 3)

    def test_l0_scores_capture_community_behavior_strength(self):
        scores = scout.l0_scores_for_signal(
            "community",
            "Outdoor Camera",
            {"reddit_score": 16, "reddit_comments": 40},
            ["hardware_intersections"],
        )

        self.assertEqual(scores["source_quality"], 2)
        self.assertEqual(scores["behavior_strength"], 4)
        self.assertEqual(scores["specificity"], 2)
        self.assertEqual(scores["watch_relevance"], 1)
        self.assertEqual(scores["diffusion_stage"], "early_adopter")
        self.assertGreater(scores["signal_strength"], 2)

    def test_watch_only_signals_do_not_create_categories(self):
        cats_doc = {"schema_version": "2.1", "methodology_version": "1.0", "categories": []}
        signals_doc = {
            "schema_version": "1.0",
            "methodology_version": "1.0",
            "signals": [
                {
                    **self.signal("S001", "developer", "Edge AI Camera"),
                    "category_eligible": False,
                    "matched_watch_topics": ["github_ai_projects"],
                },
                self.signal("S002", "media", "Edge AI Camera"),
            ],
        }

        added, rejected = scout.build_categories_from_signals(cats_doc, signals_doc)

        self.assertEqual(added, 0)
        self.assertEqual(cats_doc["categories"], [])

    def test_watch_only_candidate_keeps_source_label(self):
        category = "On Device AI Project"
        category_eligible = False
        if category_eligible:
            category = scout.normalize_category_candidate(category)
        else:
            category = " ".join(category.split())

        self.assertEqual(category, "On Device AI Project")

    def test_single_source_type_waits_for_more_evidence(self):
        passed, reason = scout.category_gate(
            [
                self.signal("S001", "media", "AI Meeting Recorder"),
                self.signal("S002", "media", "AI Meeting Recorder"),
            ]
        )

        self.assertFalse(passed)
        self.assertEqual(reason, "needs_two_independent_source_types")

    def test_two_source_types_with_behavior_can_create_category(self):
        cats_doc = {"schema_version": "2.1", "methodology_version": "1.0", "categories": []}
        signals_doc = {
            "schema_version": "1.0",
            "methodology_version": "1.0",
            "signals": [
                self.signal("S001", "crowdfunding", "AI Meeting Recorder"),
                self.signal("S002", "media", "AI Meeting Recorder"),
            ],
        }

        added, rejected = scout.build_categories_from_signals(cats_doc, signals_doc)

        self.assertEqual(added, 1)
        self.assertEqual(rejected, 0)
        self.assertEqual(cats_doc["categories"][0]["name_en"], "AI Voice Capture Device")
        self.assertEqual(cats_doc["categories"][0]["evidence_signal_ids"], ["S001", "S002"])
        self.assertIn("Evidence-Gated", cats_doc["categories"][0]["tags"])
        self.assertEqual(cats_doc["categories"][0]["l0_evidence"]["cross_source_count"], 2)
        self.assertTrue(cats_doc["categories"][0]["l0_evidence"]["has_behavior_source"])
        self.assertGreater(cats_doc["categories"][0]["l0_evidence"]["l0_confidence"], 0)

    def test_semantic_cluster_can_promote_related_security_signals(self):
        cats_doc = {"schema_version": "2.1", "methodology_version": "1.0", "categories": []}
        signals_doc = {
            "schema_version": "1.0",
            "methodology_version": "1.0",
            "signals": [
                self.signal("S001", "media", "Outdoor Camera"),
                self.signal("S002", "community", "Smart Deadbolt"),
            ],
        }

        added, rejected = scout.build_categories_from_signals(cats_doc, signals_doc)

        self.assertEqual((added, rejected), (1, 0))
        self.assertEqual(cats_doc["categories"][0]["name_en"], "Smart Home Security Device")
        self.assertEqual(cats_doc["categories"][0]["name_zh"], "智能家居安防设备")
        self.assertEqual(cats_doc["categories"][0]["cluster_key"], "cluster:smart_home_security")
        self.assertEqual(cats_doc["categories"][0]["evidence_signal_ids"], ["S001", "S002"])
        self.assertEqual(signals_doc["signals"][0]["gate_status"], "promoted")
        self.assertEqual(signals_doc["signals"][1]["cluster_name"], "Smart Home Security Device")
        self.assertEqual(signals_doc["signals"][1]["cluster_name_zh"], "智能家居安防设备")

    def test_chinese_semantic_cluster_can_promote_related_security_signals(self):
        cats_doc = {"schema_version": "2.1", "methodology_version": "1.0", "categories": []}
        signals_doc = {
            "schema_version": "1.0",
            "methodology_version": "1.0",
            "signals": [
                self.signal("S001", "media", "户外摄像头"),
                self.signal("S002", "community", "智能门锁"),
            ],
        }

        added, rejected = scout.build_categories_from_signals(cats_doc, signals_doc)

        self.assertEqual((added, rejected), (1, 0))
        self.assertEqual(cats_doc["categories"][0]["name_zh"], "智能家居安防设备")

    def test_two_step_diffusion_stage_for_media_and_community(self):
        evidence = scout.l0_evidence_for_category(
            [
                self.signal("S001", "media", "Outdoor Camera"),
                self.signal("S002", "community", "Outdoor Camera"),
            ]
        )

        self.assertEqual(evidence["diffusion_stage"], "two_step_confirmed")
        self.assertEqual(evidence["source_types"], ["community", "media"])


if __name__ == "__main__":
    unittest.main()
