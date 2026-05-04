import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("market_thesis_engine", ROOT / "scripts" / "market_thesis_engine.py")
market = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(market)


def cluster(key, name, status, source_types, signal_count=2, strength=2.8):
    return {
        "trend_key": key,
        "name": name,
        "name_zh": None,
        "trend_status": status,
        "trend_reason": "test",
        "source_types": source_types,
        "source_names": [source_type.title() for source_type in source_types],
        "signal_count": signal_count,
        "avg_signal_strength": strength,
        "seen_count_total": signal_count,
        "matched_watch_topics": [],
        "evidence_signal_ids": [f"S{index:03d}" for index in range(1, signal_count + 1)],
        "top_signals": [
            {
                "id": "S001",
                "source_name": source_types[0].title(),
                "source_type": source_types[0],
                "source_title": f"{name} source",
                "source_url": "https://example.com/source",
                "signal_strength": strength,
            }
        ],
    }


class MarketThesisEngineTest(unittest.TestCase):
    def test_media_only_cluster_stays_noise(self):
        doc = {
            "clusters": [
                cluster("watch:openclaw_hardware_bridge", "OpenClaw Hardware Bridge", "Noise", ["media"], 1, 1.4)
            ]
        }

        result = market.build_market_theses(doc, observed_at="2026-05-01T00:00:00Z")
        thesis = result["theses"][0]

        self.assertEqual(thesis["id"], "M001")
        self.assertEqual(thesis["evidence_status"], "Noise")
        self.assertLessEqual(thesis["evidence_score"], 30)
        self.assertIn("demand_behavior", thesis["missing_evidence"])
        self.assertIn("market_validation", thesis["missing_evidence"])
        self.assertIn("supply_chain", thesis["missing_evidence"])
        self.assertNotEqual(thesis["evidence_status"], "Ready for Selection")

    def test_smart_home_cluster_maps_to_market_thesis(self):
        doc = {
            "clusters": [
                cluster("cluster:smart_home_security", "Smart Home Security Device", "Warming", ["community", "media"], 2, 3.1)
            ]
        }

        thesis = market.build_market_theses(doc, observed_at="2026-05-01T00:00:00Z")["theses"][0]

        self.assertEqual(thesis["thesis_key"], "local_first_smart_home_security")
        self.assertEqual(thesis["name_zh"], "本地优先智能家居安防")
        self.assertIn("outdoor camera", thesis["hardware_form_factors"])
        self.assertIn(thesis["evidence_status"], {"Watch", "Warming"})
        self.assertIn("amazon_keyword_scan", thesis["next_validation"])

    def test_geek_productivity_cluster_maps_to_specific_market_thesis(self):
        doc = {
            "clusters": [
                cluster(
                    "watch:geek_ai_productivity_hardware",
                    "Geek AI Productivity Hardware",
                    "Warming",
                    ["product_reference", "developer", "community"],
                    5,
                    3.0,
                )
            ]
        }

        thesis = market.build_market_theses(doc, observed_at="2026-05-04T00:00:00Z")["theses"][0]

        self.assertEqual(thesis["thesis_key"], "geek_ai_productivity_hardware")
        self.assertEqual(thesis["name_zh"], "极客 AI 生产力硬件")
        self.assertIn("programmable keyboard", thesis["hardware_form_factors"])
        self.assertNotIn("market_validation", thesis["missing_evidence"])
        self.assertIn("supply_chain", thesis["missing_evidence"])

    def test_market_and_demand_can_validate_but_not_select_without_supply(self):
        doc = {
            "clusters": [
                cluster(
                    "cluster:ai_voice_capture",
                    "AI Voice Capture Device",
                    "Hot",
                    ["community", "search", "marketplace", "crowdfunding"],
                    6,
                    3.6,
                )
            ]
        }

        thesis = market.build_market_theses(doc, observed_at="2026-05-01T00:00:00Z")["theses"][0]

        self.assertEqual(thesis["thesis_key"], "ai_voice_capture_workflow")
        self.assertEqual(thesis["evidence_status"], "Validated")
        self.assertIn("supply_chain", thesis["missing_evidence"])
        self.assertNotEqual(thesis["evidence_status"], "Ready for Selection")

    def test_ready_for_selection_requires_supply_chain_evidence(self):
        doc = {
            "clusters": [
                cluster(
                    "cluster:ai_voice_capture",
                    "AI Voice Capture Device",
                    "Hot",
                    ["community", "search", "marketplace", "supply_chain"],
                    8,
                    3.8,
                )
            ]
        }

        thesis = market.build_market_theses(doc, observed_at="2026-05-01T00:00:00Z")["theses"][0]

        self.assertEqual(thesis["evidence_status"], "Ready for Selection")
        self.assertNotIn("supply_chain", thesis["missing_evidence"])

    def test_ids_are_deterministic_after_sorting_and_merge(self):
        doc = {
            "clusters": [
                cluster("cluster:smart_home_security", "Smart Home Security Device", "Warming", ["community", "media"], 2, 2.9),
                cluster("cluster:ai_voice_capture", "AI Voice Capture Device", "Hot", ["community", "search", "marketplace"], 5, 3.3),
                cluster("cluster:smart_home_security", "Outdoor Camera", "Watch", ["media"], 1, 1.2),
            ]
        }

        theses = market.build_market_theses(doc, observed_at="2026-05-01T00:00:00Z")["theses"]

        self.assertEqual([thesis["id"] for thesis in theses], ["M001", "M002"])
        self.assertEqual(theses[0]["thesis_key"], "ai_voice_capture_workflow")
        self.assertEqual(theses[1]["thesis_key"], "local_first_smart_home_security")


if __name__ == "__main__":
    unittest.main()
