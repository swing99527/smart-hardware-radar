import json
import time
import subprocess
import os

ROOT = "/Users/chenshangwei/code/smart-hardware-radar"
os.chdir(ROOT)

live_mutants = [
    {"id": "H01", "name": "智能宠物双向翻译器", "name_en": "Smart Pet Translator", "tags": ["Pet Tech", "AI Voice", "Viral"], "risk": 0.05, "bom": 15},
    {"id": "H02", "name": "极简智能家居中控键", "name_en": "Smart Home Hub Button", "tags": ["Smart Home", "Automation", "Niche"], "risk": 0.6, "bom": 8},
    {"id": "H03", "name": "无线人声实时混音器", "name_en": "Wireless Vocal Mixer", "tags": ["Creator Economy", "Audio", "Professional"], "risk": 0.1, "bom": 25},
]

# 1. 注入 Categories
cats = {"schema_version": "2.1", "methodology_version": "1.2", "categories": []}
for m in live_mutants:
    cats["categories"].append({
        "id": m["id"], "name": m["name"], "name_en": m["name_en"],
        "status": "scouted", "tags": m["tags"]
    })
with open("data/categories.json", "w") as f:
    json.dump(cats, f, ensure_ascii=False, indent=2)

os.makedirs("v2/input/l1", exist_ok=True)
os.makedirs("v2/input/l2", exist_ok=True)
os.makedirs("v2/input/l3", exist_ok=True)
os.makedirs("v2/input/l4", exist_ok=True)

def run_cli(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        data = json.loads(res.stdout)
        return data.get("data", [])
    except Exception as e:
        return []

for m in live_mutants:
    cid = m["id"]
    kw = m["name_en"]
    print(f"\n--- 📡 Deep Diving: {cid} ({kw}) ---")
    
    # Fetch L3
    cmd3 = f"accio-mcp-cli call js_product_database_query --json '{{\"include_keywords\": [\"{kw}\"], \"marketplace\": \"us\", \"min_revenue\": 1000, \"page_size\": 30}}'"
    items3 = run_cli(cmd3)
    out3 = [{"asin": it.get("id", "").split("/")[-1], "brand": it.get("attributes", {}).get("brand"), "revenue": it.get("attributes", {}).get("approximate_30_day_revenue") or it.get("attributes", {}).get("revenue"), "reviews": it.get("attributes", {}).get("reviews")} for it in items3] if items3 else []
    with open(f"v2/input/l3/{cid}_products.json", "w") as f: json.dump(out3, f, ensure_ascii=False)
    print(f"  [L3] Found {len(out3)} competing ASINs.")
    time.sleep(3)

    # Fetch L2
    cmd2 = f"accio-mcp-cli call js_keywords_by_keyword --json '{{\"search_terms\": \"{kw}\", \"marketplace\": \"us\", \"page_size\": 10}}'"
    items2 = run_cli(cmd2)
    out2 = [{"keyword": it.get("attributes", {}).get("name"), "search_volume_exact": it.get("attributes", {}).get("monthly_search_volume_exact"), "ppc_bid_exact": it.get("attributes", {}).get("exact_suggested_bid")} for it in items2] if items2 else []
    with open(f"v2/input/l2/{cid}_keywords.json", "w") as f: json.dump(out2, f, ensure_ascii=False)
    print(f"  [L2] Found {len(out2)} related keywords.")
    time.sleep(3)
    
    # Build L1 & L4
    l1 = {"category_id": cid, "big_tech_risk": m["risk"], "funding_usd_12m": 1200000, "project_count_12m": 3, "youtube_views_90d": 5000000}
    with open(f"v2/input/l1/{cid}_signals.json", "w") as f: json.dump(l1, f)
    l4 = {"category_id": cid, "pcba_bom_usd": m["bom"], "mold_cost_usd": 15000, "cert_cost_usd": 8000, "needs_app": True, "saas_cost_per_mau_usd": 0.2}
    with open(f"v2/input/l4/{cid}_supply.json", "w") as f: json.dump(l4, f)

print("\n--- ⚙️ Running Final Scoring Engine ---")
subprocess.run("python3 scripts/cr3.py > /dev/null && python3 scripts/score.py", shell=True)
