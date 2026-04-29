"""
Smart Hardware Radar — 评分引擎
==================================

读取 data/categories.json (品类清单) + v2/input/l*/ (原始数据) + data/cr3_index.json (CR3 结果)
按 docs/methodology-hardware.md v1.0 公式计算 L1-L4、Now/Trend Score、Decision。
输出: data/categories_scored.json (带可追溯字段)

Usage:
  python scripts/score.py
  python scripts/score.py --only H03
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES_FILE = ROOT / "data" / "categories.json"
CR3_FILE = ROOT / "data" / "cr3_index.json"
L1_DIR = ROOT / "v2" / "input" / "l1"
L2_DIR = ROOT / "v2" / "input" / "l2"
L3_DIR = ROOT / "v2" / "input" / "l3"
L4_DIR = ROOT / "v2" / "input" / "l4"
OUTPUT_FILE = ROOT / "data" / "categories_scored.json"

METHODOLOGY_VERSION = "1.2"

DECISION_BINS = [
    (21.0, "🟢 核心推荐", "active"),
    (18.0, "🟡 潜力黑马", "watching"),
    (15.0, "⚪ 观察样本", "observing"),
    (0.0,  "❌ 暂缓入场", "archived"),
]


def safe_log10(x: float, floor: float = 1.0) -> float:
    return math.log10(max(x, floor))


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# L1 — Geek / Crowdfunding (满分 25)
# ---------------------------------------------------------------------------
def score_l1(raw: dict | None) -> tuple[float, dict]:
    if not raw:
        return 0.0, {
            "L1a": 0, "L1b": 0, "L1c": 0,
            "data_quality": {"L1": "missing"},
            "raw": None,
        }
    funding = float(raw.get("funding_usd_12m") or 0)
    projects = int(raw.get("project_count_12m") or 0)
    youtube_views = float(raw.get("youtube_views_90d") or 0)

    L1a = min(10, safe_log10(funding) * 1.6) if funding > 0 else 0
    L1b = min(8, safe_log10(projects) * 4) if projects > 0 else 0
    L1c = min(7, safe_log10(youtube_views) * 1.0) if youtube_views > 0 else 0

    L1 = round(L1a + L1b + L1c, 1)
    return L1, {
        "L1a": round(L1a, 2),
        "L1b": round(L1b, 2),
        "L1c": round(L1c, 2),
        "data_quality": {
            "L1a": "ok" if funding > 0 else "missing",
            "L1b": "ok" if projects > 0 else "missing",
            "L1c": "ok" if youtube_views > 0 else "missing",
        },
        "raw": {
            "funding_usd_12m": funding,
            "project_count_12m": projects,
            "youtube_views_90d": youtube_views,
        },
    }


# ---------------------------------------------------------------------------
# L2 — Amazon Search (满分 25)
# ---------------------------------------------------------------------------
def score_l2(raw: list[dict] | None) -> tuple[float, dict]:
    if not raw:
        return 0.0, {
            "L2a": 0, "L2b": 0, "L2c": 0,
            "data_quality": {"L2": "missing"},
            "raw": None,
        }
    # L2a: top 3 by relevancy / search volume
    sorted_kw = sorted(
        raw, key=lambda k: (k.get("relevancy_score") or 0), reverse=True
    )
    top3 = sorted_kw[:3]
    top3_volume = sum(int(k.get("search_volume_exact") or 0) for k in top3)

    # L2b: long-tail count
    kw_over_1k = sum(
        1 for k in raw if (k.get("search_volume_exact") or 0) >= 1000
    )

    # L2c: avg PPC across top relevant kws (ignore null)
    bids = [
        float(k["ppc_bid_exact"])
        for k in sorted_kw[:5]
        if k.get("ppc_bid_exact") not in (None, 0)
    ]
    if bids:
        avg_ppc = statistics.mean(bids)
        ppc_quality = "ok"
    else:
        avg_ppc = None
        ppc_quality = "missing_fallback"

    L2a = min(12, safe_log10(top3_volume) * 2.4) if top3_volume > 0 else 0
    L2b = min(8, kw_over_1k / 5)
    if avg_ppc is None:
        L2c = 2.5  # neutral fallback per methodology §4
    elif avg_ppc <= 0.5: L2c = 5
    elif avg_ppc <= 1.0: L2c = 4
    elif avg_ppc <= 2.0: L2c = 3
    elif avg_ppc <= 3.5: L2c = 2
    elif avg_ppc <= 5.0: L2c = 1
    else: L2c = 0

    L2 = round(L2a + L2b + L2c, 1)
    return L2, {
        "L2a": round(L2a, 2),
        "L2b": round(L2b, 2),
        "L2c": round(L2c, 2),
        "data_quality": {
            "L2a": "ok" if top3_volume > 0 else "missing",
            "L2b": "ok",
            "L2c": ppc_quality,
        },
        "raw": {
            "top3_search_volume": top3_volume,
            "keyword_count_over_1k": kw_over_1k,
            "avg_ppc_top5": round(avg_ppc, 2) if avg_ppc else None,
            "keyword_sample_size": len(raw),
        },
    }


# ---------------------------------------------------------------------------
# L3 — Anti-Monopoly + Market Size (满分 25)
# ---------------------------------------------------------------------------
def score_l3(
    products: list[dict] | None, cr3_info: dict | None
) -> tuple[float, dict, bool]:
    if not products or not cr3_info:
        return 0.0, {
            "L3a": 0, "L3b": 0, "L3c": 0,
            "data_quality": {"L3": "missing"},
            "raw": None,
        }, False

    cr3 = cr3_info.get("cr3")
    veto = bool(cr3_info.get("veto_flag"))

    
    # L3a: anti-monopoly band [V1.2] Emerging Exemption
    is_emerging = cr3_info.get("is_emerging", False)
    if cr3 is None:
        L3a = 0
    elif is_emerging:
        L3a = 6.0  # 拓荒期中立分，免除垄断罚分
    elif cr3 > 0.50:
        L3a = 0
    elif cr3 <= 0.20: L3a = 12
    elif cr3 <= 0.30: L3a = 10
    elif cr3 <= 0.40: L3a = 7
    else: L3a = 4


    # L3b: market size (sum of top-N revenue, monthly)
    total_rev = float(cr3_info.get("total_revenue") or 0)
    L3b = min(8, safe_log10(total_rev) * 1.3) if total_rev > 0 else 0

    # L3c: review density (lower = better, less saturated)
    review_counts = [
        int(p["reviews"]) for p in products
        if p.get("reviews") not in (None, 0)
    ]
    if review_counts:
        avg_reviews = statistics.mean(review_counts)
        if avg_reviews <= 200: L3c = 5
        elif avg_reviews <= 500: L3c = 4
        elif avg_reviews <= 1500: L3c = 3
        elif avg_reviews <= 5000: L3c = 2
        else: L3c = 1
        rev_quality = "ok"
    else:
        avg_reviews = None
        L3c = 2.5
        rev_quality = "missing_fallback"

    L3 = round(L3a + L3b + L3c, 1)
    return L3, {
        "L3a": round(L3a, 2),
        "L3b": round(L3b, 2),
        "L3c": round(L3c, 2),
        "data_quality": {
            "L3a": "ok" if cr3 is not None else "missing",
            "L3b": "ok" if total_rev > 0 else "missing",
            "L3c": rev_quality,
        },
        "raw": {
            "cr3": cr3,
            "total_revenue_top_n": total_rev,
            "avg_reviews": round(avg_reviews, 1) if avg_reviews else None,
            "asin_sample_size": len(products),
            "top_brands": cr3_info.get("top_brands", []),
        },
    }, veto


# ---------------------------------------------------------------------------
# L4 — Supply Chain & Cost (满分 25)
# ---------------------------------------------------------------------------
def score_l4(raw: dict | None) -> tuple[float, dict]:
    if not raw:
        return 0.0, {
            "L4a": 0, "L4b": 0, "L4c": 0, "L4d": 0,
            "data_quality": {"L4": "missing"},
            "raw": None,
        }
    bom = float(raw.get("pcba_bom_usd") or 0)
    mold = float(raw.get("mold_cost_usd") or 0)
    cert = float(raw.get("cert_cost_usd") or 0)
    needs_app = bool(raw.get("needs_app", True))
    saas = float(raw.get("saas_cost_per_mau_usd") or 0)

    if bom <= 5: L4a = 8
    elif bom <= 12: L4a = 6
    elif bom <= 25: L4a = 4
    elif bom <= 50: L4a = 2
    else: L4a = 1

    if mold <= 10000: L4b = 6
    elif mold <= 30000: L4b = 4
    elif mold <= 80000: L4b = 2
    else: L4b = 1

    if cert <= 5000: L4c = 6
    elif cert <= 15000: L4c = 4
    elif cert <= 40000: L4c = 2
    else: L4c = 0

    if not needs_app: L4d = 5
    elif saas <= 0.20: L4d = 4
    elif saas <= 1.00: L4d = 2
    else: L4d = 0

    L4 = round(L4a + L4b + L4c + L4d, 1)
    return L4, {
        "L4a": L4a, "L4b": L4b, "L4c": L4c, "L4d": L4d,
        "data_quality": {k: "library" for k in ("L4a", "L4b", "L4c", "L4d")},
        "raw": {
            "pcba_bom_usd": bom,
            "mold_cost_usd": mold,
            "cert_cost_usd": cert,
            "needs_app": needs_app,
            "saas_cost_per_mau_usd": saas,
        },
    }


# ---------------------------------------------------------------------------
# Decision
# ---------------------------------------------------------------------------
def derive_decision(now_score: float, trend_score: float, veto: bool):
    if veto:
        return "❌ 暂缓入场 (CR3 VETO)", "archived"
    top = max(now_score, trend_score)
    for threshold, label, status in DECISION_BINS:
        if top >= threshold:
            return label, status
    return "❌ 暂缓入场", "archived"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def score_category(
    cat: dict, cr3_index: dict, only: str | None = None
) -> dict | None:
    cid = cat["id"]
    if only and cid != only:
        return None

    l1_raw = load_json(L1_DIR / f"{cid}_signals.json")
    l2_raw = load_json(L2_DIR / f"{cid}_keywords.json")
    l3_products = load_json(L3_DIR / f"{cid}_products.json")
    l4_raw = load_json(L4_DIR / f"{cid}_supply.json")

    L1, l1_meta = score_l1(l1_raw)
    L2, l2_meta = score_l2(l2_raw)
    cr3_info = (cr3_index.get("categories", {}) or {}).get(cid)
    L3, l3_meta, veto = score_l3(l3_products, cr3_info)
    L4, l4_meta = score_l4(l4_raw)

    now_score = round(L3 * 0.50 + L4 * 0.30 + L2 * 0.20, 2)
    trend_score = round(L1 * 0.40 + L3 * 0.40 + L2 * 0.20, 2)
    
    # [V1.1] Big Tech Risk
    big_tech_risk = float(l1_raw.get("big_tech_risk", 0.0)) if l1_raw else 0.0
    penalty = round(big_tech_risk * 15.0, 2)
    now_score = max(0.0, now_score - penalty)
    trend_score = max(0.0, trend_score - penalty)
    
    # [V1.1] Resonance Bonus
    resonance = False
    if L1 >= 15.0 and L2 >= 15.0:
        trend_score = round(trend_score * 1.1, 2)
        resonance = True

    decision, status = derive_decision(now_score, trend_score, veto)

    return {
        "id": cid, "name": cat.get("name"), "name_en": cat.get("name_en"), "tags": cat.get("tags", []),
        "scores": {"L1": L1, "L2": L2, "L3": L3, "L4": L4},
        "total": round(L1 + L2 + L3 + L4, 1),
        "now_score": round(now_score, 2), "trend_score": round(trend_score, 2),
        "decision": decision, "status": status, "veto_flag": veto,
        "methodology_version": METHODOLOGY_VERSION,
        "calculated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "details": {
            "v1_1_rules": {"big_tech_risk_penalty": penalty, "l1_l2_resonance_bonus": resonance},
            "L1": l1_meta, "L2": l2_meta, "L3": l3_meta, "L4": l4_meta
        }
    }

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="只评分单个品类 (如 H03)")
    args = parser.parse_args()

    cats_doc = load_json(CATEGORIES_FILE)
    if not cats_doc:
        raise SystemExit(f"Missing {CATEGORIES_FILE}")
    cr3_index = load_json(CR3_FILE) or {"categories": {}}

    results = []
    for cat in cats_doc.get("categories", []):
        scored = score_category(cat, cr3_index, args.only)
        if scored:
            results.append(scored)

    output = {
        "schema_version": "2.1",
        "methodology_version": METHODOLOGY_VERSION,
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "categories": results,
    }
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"[OK] scored {len(results)} categories → {OUTPUT_FILE.relative_to(ROOT)}")
    for r in results:
        veto = " 🚫VETO" if r["veto_flag"] else ""
        print(
            f"  {r['id']:5s} {r.get('name_en','')[:35]:35s} "
            f"Now={r['now_score']:>5.2f} Trend={r['trend_score']:>5.2f}  "
            f"{r['decision']}{veto}"
        )

if __name__ == "__main__":
    main()
