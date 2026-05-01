import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_source_health", ROOT / "scripts" / "check_source_health.py")
health = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(health)


class SourceHealthTest(unittest.TestCase):
    def test_required_source_failure_is_reported(self):
        report = health.evaluate_source_health(
            {
                "sources": [
                    {
                        "source_name": "GitHub Agentic Edge Hardware",
                        "status": "error",
                        "http_status": 403,
                        "auth_mode": "anonymous",
                        "error": "rate limit exceeded",
                    },
                    {"source_name": "Agentic Edge Hardware News", "status": "ok"},
                ]
            }
        )

        self.assertEqual(report["required_count"], 1)
        self.assertEqual(report["failure_count"], 1)
        self.assertEqual(report["failures"][0]["source_name"], "GitHub Agentic Edge Hardware")

    def test_required_ok_source_passes(self):
        report = health.evaluate_source_health(
            {
                "sources": [
                    {
                        "source_name": "Reddit r/hardware",
                        "status": "ok",
                        "auth_mode": "reddit_oauth",
                        "last_success_at": "2026-05-01T00:00:00+00:00",
                    }
                ]
            },
            max_stale_hours=10_000,
        )

        self.assertEqual(report["failure_count"], 0)

    def test_required_prefixes_are_configurable(self):
        report = health.evaluate_source_health(
            {"sources": [{"source_name": "GitHub Edge AI Camera", "status": "error"}]},
            required_prefixes=("Reddit",),
        )

        self.assertEqual(report["required_count"], 0)
        self.assertEqual(report["failure_count"], 0)


if __name__ == "__main__":
    unittest.main()
