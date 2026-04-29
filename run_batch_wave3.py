import json
import time
import subprocess
import os

targets = [
    ("S076", "Automatic Pet Feeder", 0.1, 15.0),
    ("S123", "eInk Calendar", 0.05, 10.0),
    ("S124", "Smart Pomodoro Timer", 0.05, 5.0),
    ("S024", "Pelvic Floor Muscle Trainer", 0.05, 8.0),
    ("S060", "Laser Hair Removal Device", 0.1, 20.0),
    ("S142", "Window Cleaning Robot", 0.2, 35.0),
    ("S080", "Smart Dog Collar", 0.1, 12.0),
    ("S186", "Smart Fidget Toy", 0.01, 4.0),
    ("S187", "Smart Cube", 0.05, 8.0),
    ("S010", "Heated Gloves", 0.05, 6.0),
]

def run_cli_with_retry(cmd, retries=2):
    for attempt in range(retries):
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=40)
            if res.returncode != 0 or "fetch failed" in res.stderr:
                print(f"    [!] Attempt {attempt+1} failed: {res.stderr.strip()[:100]}")
                time.sleep(8)
                continue
            data = json.loads(res.stdout)
            return data.get("data", [])
        except Exception as e:
            print(f"    [!] Exception on attempt {attempt+1}: {e}")
            time.sleep(8)
    return []

for cid, kw, risk, pcba in targets:
    print(f"\n--- ⏳ Fetching {cid}: {kw} ---")
    
    # 1. Fetch L3 (ASINs)
    cmd3 = f"accio-mcp-cli call js_product_database_query --json '{{\"include_keywords\": [\"{kw}\"], \"marketplace\": \"us\", \"min_revenue\": 1000, \"page_size\": 30}}'"
    items3 = run_cli_with_retry(cmd3)
    if items3:
        out3 = []
        for it in items3:
            a = it.get("attributes", {})
            out3.append({
                "asin": it.get("id", "").split("/")[-1],
                "brand": a.get("brand"),
                "revenue": a.get("approximate_30_day_revenue") or a.get("revenue"),
                "reviews": a.get("reviews") or a.get("review_count"),
            })
        with open(f"v2/input/l3/{cid}_products.json", "w") as f:
            json.dump(out3, f, ensure_ascii=False, indent=2)
        print(f"    [OK] L3: Saved {len(out3)} products.")
    else:
        print("    [!] L3: No data returned after retries.")
        
    time.sleep(3)

    # 2. Fetch L2 (Keywords)
    cmd2 = f"accio-mcp-cli call js_keywords_by_keyword --json '{{\"search_terms\": \"{kw}\", \"marketplace\": \"us\", \"page_size\": 10}}'"
    items2 = run_cli_with_retry(cmd2)
    if items2:
        out2 = []
        for it in items2:
            a = it.get("attributes", {})
            out2.append({
                "keyword": a.get("name"),
                "search_volume_exact": a.get("monthly_search_volume_exact"),
                "ppc_bid_exact": a.get("exact_suggested_bid"),
                "relevancy_score": a.get("relevancy_score"),
            })
        with open(f"v2/input/l2/{cid}_keywords.json", "w") as f:
            json.dump(out2, f, ensure_ascii=False, indent=2)
        print(f"    [OK] L2: Saved {len(out2)} keywords.")
    else:
        print("    [!] L2: No data returned after retries.")
        
    time.sleep(3)
    
    # 3. Inject L1/L4 Baseline with specific Big Tech Risk
    l1 = {"category_id": cid, "big_tech_risk": risk, "ai_alignment": 0.5, "funding_usd_12m": 800000, "project_count_12m": 6, "youtube_views_90d": 3000000}
    with open(f"v2/input/l1/{cid}_signals.json", "w") as f:
        json.dump(l1, f)
        
    l4 = {"category_id": cid, "pcba_bom_usd": pcba, "mold_cost_usd": 15000, "cert_cost_usd": 6000, "needs_app": True, "saas_cost_per_mau_usd": 0.1}
    with open(f"v2/input/l4/{cid}_supply.json", "w") as f:
        json.dump(l4, f)

print("\n🚀 Batch fetch complete! Running Scoring Engine...")
