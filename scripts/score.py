import json
import math
from copy import deepcopy
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAT_FILE = ROOT / "data" / "categories.json"
SCORED_FILE = ROOT / "data" / "categories_scored.json"
METHODOLOGY_VERSION = "1.0"


def log_score(value, cap, multiplier):
    return min(cap, math.log10(max(float(value or 0), 1)) * multiplier)


def existing_score(category, key):
    scores = category.get("scores")
    if isinstance(scores, dict) and isinstance(scores.get(key), (int, float)):
        return float(scores[key]), "provided"
    return None, "missing"


def score_l1(category):
    value, quality = existing_score(category, "L1")
    if value is not None:
        return round(min(25, value), 1), {"L1": quality}
    return 0.0, {"L1a": "missing", "L1b": "missing", "L1c": "missing"}


def score_l2(category):
    quality = {}

    top3_volume = category.get("top3_search_volume")
    if top3_volume is None:
        top3_volume = category.get("js_search_volume", 0)
        quality["L2a"] = "exact_keyword_fallback" if top3_volume else "missing"
    else:
        quality["L2a"] = "ok"
    l2a = log_score(top3_volume, 12, 2.4)

    keyword_count = category.get("keyword_count_over_1k")
    if keyword_count is None:
        quality["L2b"] = "missing"
        l2b = 0.0
    else:
        quality["L2b"] = "ok"
        l2b = min(8, float(keyword_count) / 5)

    avg_ppc = category.get("avg_ppc")
    if avg_ppc is None:
        quality["L2c"] = "missing_neutral"
        l2c = 2.5
    else:
        quality["L2c"] = "ok"
        avg_ppc = float(avg_ppc)
        if avg_ppc <= 0.5:
            l2c = 5
        elif avg_ppc <= 1.0:
            l2c = 4
        elif avg_ppc <= 2.0:
            l2c = 3
        elif avg_ppc <= 3.5:
            l2c = 2
        elif avg_ppc <= 5.0:
            l2c = 1
        else:
            l2c = 0

    return round(l2a + l2b + l2c, 1), quality


def score_l3(category):
    quality = {}
    total_rev = float(category.get("total_revenue") or 0)
    top3_rev = float(category.get("top_3_revenue") or 0)
    cr3 = round((top3_rev / total_rev * 100), 1) if total_rev > 0 else 0.0
    category["cr3"] = cr3

    if total_rev <= 0:
        quality["L3a"] = "missing"
        quality["L3b"] = "missing"
        l3a = 0.0
        l3b = 0.0
    else:
        quality["L3a"] = "ok"
        quality["L3b"] = "ok"
        if cr3 > 50:
            l3a = 0
        elif cr3 <= 20:
            l3a = 12
        elif cr3 <= 30:
            l3a = 10
        elif cr3 <= 40:
            l3a = 7
        else:
            l3a = 4
        l3b = log_score(total_rev, 8, 1.3)

    avg_reviews = category.get("avg_review_count")
    if avg_reviews is None:
        quality["L3c"] = "missing"
        l3c = 0.0
    else:
        quality["L3c"] = "ok"
        avg_reviews = float(avg_reviews)
        if avg_reviews <= 200:
            l3c = 5
        elif avg_reviews <= 500:
            l3c = 4
        elif avg_reviews <= 1500:
            l3c = 3
        elif avg_reviews <= 5000:
            l3c = 2
        else:
            l3c = 1

    return round(l3a + l3b + l3c, 1), quality


def score_l4(category):
    value, quality = existing_score(category, "L4")
    if value is not None:
        return round(min(25, value), 1), {"L4": quality}
    return 0.0, {"L4a": "missing", "L4b": "missing", "L4c": "missing", "L4d": "missing"}


def classify(category, l1, l2, l3, l4):
    now_score = round(l3 * 0.50 + l4 * 0.30 + l2 * 0.20, 1)
    trend_score = round(l1 * 0.40 + l3 * 0.40 + l2 * 0.20, 1)
    max_score = max(now_score, trend_score)
    cr3 = category.get("cr3", 0)

    if cr3 > 50:
        return now_score, trend_score, "vetoed", "❌ 暂缓入场", "Monopoly Risk"
    if now_score >= 21:
        return now_score, trend_score, "recommended", "🟢 核心推荐", None
    if trend_score >= 18:
        return now_score, trend_score, "trend", "🟡 潜力黑马", None
    if max_score >= 15:
        return now_score, trend_score, "watch", "⚪ 观察样本", None
    return now_score, trend_score, "analyzed", "❌ 暂缓入场", None


def score_category(category):
    scored = deepcopy(category)
    quality = {}

    l1, q1 = score_l1(scored)
    l2, q2 = score_l2(scored)
    l3, q3 = score_l3(scored)
    l4, q4 = score_l4(scored)
    for q in (q1, q2, q3, q4):
        quality.update(q)

    now_score, trend_score, status, decision, tag = classify(scored, l1, l2, l3, l4)
    scored["scores"] = {"L1": l1, "L2": l2, "L3": l3, "L4": l4}
    scored["now_score"] = now_score
    scored["trend_score"] = trend_score
    scored["status"] = status
    scored["decision"] = decision
    scored["data_quality"] = quality
    scored["methodology_version"] = METHODOLOGY_VERSION

    if tag:
        tags = scored.setdefault("tags", [])
        if tag not in tags:
            tags.append(tag)

    return scored


def should_score(category):
    return category.get("status") == "data_fetched" or "js_search_volume" in category or "total_revenue" in category


def main():
    if not CAT_FILE.exists():
        print("    [!] categories.json not found.")
        return

    try:
        data = json.loads(CAT_FILE.read_text())
    except json.JSONDecodeError:
        print("    [!] categories.json is corrupted.")
        return

    scored_list = []
    categories = data.get("categories", [])

    print("[OK] Starting Methodology v1.0 Scoring Engine")

    for index, category in enumerate(categories):
        if should_score(category):
            scored = score_category(category)
            categories[index] = scored
            scored_list.append(scored)
            name = scored.get("name_en") or scored.get("name") or "Unknown"
            print(
                f"  {scored.get('id', '')[:4]:<4}  {name[:30]:<30}  "
                f"Now={scored['now_score']:>4.1f} Trend={scored['trend_score']:>4.1f} "
                f"CR3={scored['cr3']:>4}%  {scored['decision']}"
            )

    data["methodology_version"] = METHODOLOGY_VERSION
    CAT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    generated_at = datetime.now().isoformat() + "Z"
    if SCORED_FILE.exists():
        try:
            previous = json.loads(SCORED_FILE.read_text())
            if previous.get("categories") == scored_list:
                generated_at = previous.get("generated_at", generated_at)
        except json.JSONDecodeError:
            pass

    scored_output = {
        "schema_version": data.get("schema_version", "2.1"),
        "methodology_version": METHODOLOGY_VERSION,
        "generated_at": generated_at,
        "categories": scored_list,
    }
    SCORED_FILE.write_text(json.dumps(scored_output, indent=2, ensure_ascii=False))
    print(f"\n[OK] scored {len(scored_list)} categories -> data/categories_scored.json")


if __name__ == "__main__":
    main()
