import json
from datetime import datetime
from pathlib import Path

ROOT = Path("/Users/chenshangwei/code/smart-hardware-radar")
CAT_FILE = ROOT / "data" / "categories.json"

def main():
    print(f"[{datetime.now().isoformat()}] Starting L0 Scout Pipeline...")
    
    # 模拟从外网抓取并被 LLM 提炼出的新爆点
    raw_titles = ["AI-Powered Ergonomic Posture Corrector with Biofeedback"]
    seed_keywords = {"smart posture corrector"}
    
    cats_doc = json.loads(CAT_FILE.read_text())
    existing_kws = {c.get("name_en", "").lower() for c in cats_doc.get("categories", [])}
    
    new_added = 0
    next_id = len(cats_doc["categories"]) + 1
    
    for kw in seed_keywords:
        if kw.lower() not in existing_kws:
            new_id = f"H{next_id:02d}"
            new_cat = {
                "id": new_id,
                "name": f"【L0自动发现】{kw}",
                "name_en": kw,
                "status": "scouted",
                "tags": ["Auto-Discovered", "Health", "Desk"]
            }
            cats_doc["categories"].append(new_cat)
            print(f"  -> [+] Scouted new category: {new_id} - {kw}")
            
            # 自动生成基础 L1 和 L4 模板（后续可接入爬虫/API）
            l1 = {"category_id": new_id, "big_tech_risk": 0.05, "ai_alignment": 0.6, "funding_usd_12m": 1200000, "project_count_12m": 4, "youtube_views_90d": 3500000}
            (ROOT / f"v2/input/l1/{new_id}_signals.json").write_text(json.dumps(l1, indent=2))
            
            l4 = {"category_id": new_id, "pcba_bom_usd": 6.0, "mold_cost_usd": 12000, "cert_cost_usd": 6000, "needs_app": True, "saas_cost_per_mau_usd": 0.10}
            (ROOT / f"v2/input/l4/{new_id}_supply.json").write_text(json.dumps(l4, indent=2))
            
            next_id += 1
            new_added += 1
            
    if new_added > 0:
        CAT_FILE.write_text(json.dumps(cats_doc, indent=2, ensure_ascii=False))
        print(f"[L0] Successfully appended {new_added} new categories to JSON.")
    else:
        print("[L0] No *new* categories discovered today.")

if __name__ == "__main__":
    main()
