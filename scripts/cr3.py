"""
CR3 反垄断指数计算
==================

输入: v2/input/l3/{CATEGORY_ID}_products.json  (Top N ASIN，含 brand + revenue 字段)
输出: data/cr3_index.json

CR3 = sum(top3_brand_revenue) / sum(all_brand_revenue)
CR3 > 0.50 触发一票否决 (veto_flag = True)。

按方法论 v1.0 §5 实现。
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "v2" / "input" / "l3"
OUTPUT_FILE = ROOT / "data" / "cr3_index.json"

# 品牌名归一化：处理 "Generic" / "1MORE" 之类的常见噪声
BRAND_ALIAS = {
    "generic": "Generic (Unbranded)",
    "": "Generic (Unbranded)",
    None: "Generic (Unbranded)",
}


def normalize_brand(raw: str | None) -> str:
    if raw is None:
        return BRAND_ALIAS[None]
    s = raw.strip()
    key = s.lower()
    if key in BRAND_ALIAS:
        return BRAND_ALIAS[key]
    # 去掉常见后缀
    s = re.sub(r"\s+(inc|llc|ltd|co\.?|company)\.?$", "", s, flags=re.I).strip()
    return s or BRAND_ALIAS[None]


def compute_cr3(products: list[dict[str, Any]]) -> dict[str, Any]:
    """对单个品类的 ASIN 列表计算 CR3。"""
    brand_revenue: dict[str, float] = defaultdict(float)
    brand_asin_count: dict[str, int] = defaultdict(int)
    total_revenue = 0.0

    for p in products:
        rev = float(p.get("revenue") or 0)
        if rev <= 0:
            continue
        brand = normalize_brand(p.get("brand"))
        brand_revenue[brand] += rev
        brand_asin_count[brand] += 1
        total_revenue += rev

    if total_revenue <= 0:
        return {
            "cr3": None,
            "veto_flag": False,
            "total_revenue": 0,
            "top_brands": [],
            "brand_total_count": 0, "asin_total_count": 0, "data_quality": "no_revenue_data",
        }

    sorted_brands = sorted(
        brand_revenue.items(), key=lambda kv: kv[1], reverse=True
    )
    top3 = sorted_brands[:3]
    cr3 = sum(rev for _, rev in top3) / total_revenue

    return {
        "cr3": round(cr3, 4),
        "veto_flag": cr3 > 0.50 and total_revenue >= 100000,
        "is_emerging": total_revenue < 100000 and total_revenue > 0,
        "total_revenue": round(total_revenue, 2),
        "top_brands": [
            {
                "brand": b,
                "revenue": round(r, 2),
                "share": round(r / total_revenue, 4),
                "asin_count": brand_asin_count[b],
            }
            for b, r in sorted_brands[:5]
        ],
        "brand_total_count": len(brand_revenue),
        "asin_total_count": sum(brand_asin_count.values()),
        "data_quality": "ok" if len(products) >= 10 else "thin_sample",
    }


def main() -> None:
    if not INPUT_DIR.exists():
        raise SystemExit(f"Input dir missing: {INPUT_DIR}")

    results: dict[str, Any] = {}
    for fp in sorted(INPUT_DIR.glob("*_products.json")):
        category_id = fp.stem.replace("_products", "")
        try:
            products = json.loads(fp.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            results[category_id] = {"error": f"json_decode: {e}"}
            continue
        results[category_id] = compute_cr3(products)

    output = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "methodology_version": "1.0",
        "input_dir": str(INPUT_DIR.relative_to(ROOT)),
        "categories": results,
    }
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # CLI 友好输出
    print(f"[OK] CR3 index → {OUTPUT_FILE.relative_to(ROOT)}")
    for cid, info in results.items():
        if "error" in info:
            print(f"  {cid}: ERROR {info['error']}")
            continue
        cr3 = info.get("cr3")
        veto = "🚫VETO" if info.get("veto_flag") else "✓"
        print(
            f"  {cid}: CR3={cr3}  total_rev=${info['total_revenue']:>12,.0f}  "
            f"brands={info['brand_total_count']:>3}  {veto}"
        )


if __name__ == "__main__":
    main()
