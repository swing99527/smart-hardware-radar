import json
import time
import subprocess
import os
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAT_FILE = ROOT / "data" / "categories.json"

def run_mcp(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if res.returncode != 0:
            # accio-mcp-cli 报错（可能包含 rate_limited 等）
            print(f"    [MCP Error] {res.stderr.strip()}")
            return None
        
        # 很多时候 cli 会打印多余信息，尝试找到 JSON 块
        output = res.stdout.strip()
        try:
            data = json.loads(output)
            return data.get("data", [])
        except json.JSONDecodeError:
            # 如果不完全是 json，可能是单行或包含警告
            start_idx = output.find('{')
            end_idx = output.rfind('}')
            if start_idx != -1 and end_idx != -1:
                return json.loads(output[start_idx:end_idx+1]).get("data", [])
            return None
    except subprocess.TimeoutExpired:
        print("    [MCP Timeout] Query took too long.")
        return None
    except Exception as e:
        print(f"    [Exception] {e}")
        return None

def fetch_category_data(cat):
    kw = cat.get("name_en", cat.get("name", "")).strip()
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔍 Fetching Data for: {kw} (ID: {cat['id']})")
    
    if not kw:
        print("    [!] Invalid keyword. Skipping.")
        cat['status'] = 'fetch_failed'
        return False

    # 1. Fetch L3 - Product Database (Sales/Revenue Data)
    cmd3 = f"accio-mcp-cli call js_product_database_query --json '{{\"include_keywords\": [\"{kw}\"], \"marketplace\": \"us\", \"min_revenue\": 1000, \"page_size\": 30}}'"
    print("    -> Querying Top 30 ASINs Revenue...")
    items3 = run_mcp(cmd3)
    
    if items3 is None:
        print("    [!] Failed to retrieve JS Product data. (Rate limit or API error)")
        return False
        
    total_revenue = 0
    brand_revenues = {}
    
    if items3:
        for it in items3:
            a = it.get("attributes", {})
            rev = float(a.get("approximate_30_day_revenue") or a.get("revenue") or 0)
            brand = a.get("brand", "Unknown")
            
            total_revenue += rev
            brand_revenues[brand] = brand_revenues.get(brand, 0) + rev
            
        # 计算 CR3 (Top 3 Brand Revenue)
        sorted_brands = sorted(brand_revenues.items(), key=lambda x: x[1], reverse=True)
        top_3_revenue = sum([v for k, v in sorted_brands[:3]])
        
        print(f"    ✅ Found {len(items3)} products. Total Rev: ${total_revenue:,.2f}, Top 3 Rev: ${top_3_revenue:,.2f}")
        cat['total_revenue'] = total_revenue
        cat['top_3_revenue'] = top_3_revenue
    else:
        print("    ⚠️ No products found for this keyword.")
        cat['total_revenue'] = 0
        cat['top_3_revenue'] = 0

    time.sleep(3) # 防熔断冷却

    # 2. Fetch L2 - Keyword Search Volume
    cmd2 = f"accio-mcp-cli call js_keywords_by_keyword --json '{{\"search_terms\": \"{kw}\", \"marketplace\": \"us\", \"page_size\": 5}}'"
    print("    -> Querying Search Volume...")
    items2 = run_mcp(cmd2)
    
    sv = 0
    if items2:
        # 取第一条数据的精确搜索量（通常是完全匹配词）
        first_attr = items2[0].get("attributes", {})
        sv = int(first_attr.get("monthly_search_volume_exact", 0))
        print(f"    ✅ Exact Search Volume: {sv}")
    else:
        print("    ⚠️ No exact keyword data found.")
        
    cat['js_search_volume'] = sv
    cat['status'] = 'data_fetched'
    
    return True

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📡 L2/L3 Jungle Scout Fetcher Started")
    
    if not CAT_FILE.exists():
        print("    [!] categories.json not found. Run L0 Scout first.")
        return
        
    try:
        data = json.loads(CAT_FILE.read_text())
    except json.JSONDecodeError:
        print("    [!] categories.json is corrupted.")
        return

    scouted_cats = [c for c in data.get('categories', []) if c.get('status') == 'scouted']
    if not scouted_cats:
        print("    😴 No newly 'scouted' categories found. Everything is up to date.")
        return
        
    print(f"    📦 Found {len(scouted_cats)} categories waiting for Jungle Scout API injection.")
    
    success_count = 0
    for c in scouted_cats:
        if fetch_category_data(c):
            success_count += 1
            # 每成功一条就立刻保存，防崩溃丢失
            CAT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        time.sleep(5) # 整体查询冷却 5 秒，防止封号
            
    print(f"\n🎯 Fetch run complete! {success_count}/{len(scouted_cats)} updated to 'data_fetched'.")
    print("    👉 Next step: Run L4 Scoring Engine (python scripts/score.py)")

if __name__ == "__main__":
    main()
