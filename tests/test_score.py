import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("score", ROOT / "scripts" / "score.py")
score = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(score)


class ScoreEngineTest(unittest.TestCase):
    def test_missing_l1_l4_are_zero_and_marked_missing(self):
        category = {
            "id": "T001",
            "name_en": "Desk Camera",
            "status": "data_fetched",
            "js_search_volume": 50000,
            "total_revenue": 100000,
            "top_3_revenue": 20000,
        }

        scored = score.score_category(category)

        self.assertEqual(scored["scores"]["L1"], 0.0)
        self.assertEqual(scored["scores"]["L4"], 0.0)
        self.assertEqual(scored["data_quality"]["L1a"], "missing")
        self.assertEqual(scored["data_quality"]["L4a"], "missing")
        self.assertLess(scored["now_score"], 21)
        self.assertNotEqual(scored["status"], "recommended")

    def test_cr3_above_50_forces_veto(self):
        category = {
            "id": "T002",
            "name_en": "Smart Ring",
            "status": "data_fetched",
            "scores": {"L1": 25, "L4": 25},
            "js_search_volume": 200000,
            "total_revenue": 1000000,
            "top_3_revenue": 600000,
        }

        scored = score.score_category(category)

        self.assertEqual(scored["cr3"], 60.0)
        self.assertEqual(scored["status"], "vetoed")
        self.assertEqual(scored["decision"], "❌ 暂缓入场")
        self.assertIn("Monopoly Risk", scored["tags"])

    def test_complete_high_quality_category_is_recommended(self):
        category = {
            "id": "T003",
            "name_en": "Open Ear Headphones",
            "status": "data_fetched",
            "scores": {"L1": 22, "L4": 22},
            "top3_search_volume": 120000,
            "keyword_count_over_1k": 40,
            "avg_ppc": 0.75,
            "total_revenue": 1000000,
            "top_3_revenue": 180000,
            "avg_review_count": 150,
        }

        scored = score.score_category(category)

        self.assertGreaterEqual(scored["now_score"], 21)
        self.assertEqual(scored["status"], "recommended")
        self.assertEqual(scored["decision"], "🟢 核心推荐")


if __name__ == "__main__":
    unittest.main()
