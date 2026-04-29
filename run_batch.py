import json
import os
import subprocess

targets = [
    ("S001", "Smart Ring"),
    ("S002", "Smart Glasses"),
    ("S003", "Audio Sunglasses"),
]

os.makedirs("v2/input/l2", exist_ok=True)
os.makedirs("v2/input/l3", exist_ok=True)

for cid, kw in targets:
    print(f"--- Processing {cid}: {kw} ---")
    
    # 解析 L3
    try:
        with open(f"raw_data/{cid}_L3.json", "r") as f:
            data = json.load(f)
            items = data.get("data", [])
            out3 = []
            for it in items:
                a = it.get("attributes", {})
                out3.append({
                    "asin": it.get("id", "").split("/")[-1],
                    "brand": a.get("brand"),
                    "revenue": a.get("approximate_30_day_revenue") or a.get("revenue"),
                    "reviews": a.get("reviews") or a.get("review_count"),
                })
            with open(f"v2/input/l3/{cid}_products.json", "w") as f2:
                json.dump(out3, f2, ensure_ascii=False, indent=2)
            print(f"  L3 -> {len(out3)} ASINs parsed.")
    except Exception as e:
        print(f"  L3 parse failed: {e}")

    # 解析 L2
    try:
        with open(f"raw_data/{cid}_L2.json", "r") as f:
            data = json.load(f)
            items = data.get("data", [])
            out2 = []
            for it in items:
                a = it.get("attributes", {})
                out2.append({
                    "keyword": a.get("name"),
                    "search_volume_exact": a.get("monthly_search_volume_exact"),
                    "ppc_bid_exact": a.get("exact_suggested_bid"),
                    "relevancy_score": a.get("relevancy_score"),
                })
            with open(f"v2/input/l2/{cid}_keywords.json", "w") as f2:
                json.dump(out2, f2, ensure_ascii=False, indent=2)
            print(f"  L2 -> {len(out2)} Keywords parsed.")
    except Exception as e:
        print(f"  L2 parse failed: {e}")

print("\n--- Running Scoring Engine ---")
subprocess.run("python3 scripts/cr3.py", shell=True)
subprocess.run("python3 scripts/score.py", shell=True)
