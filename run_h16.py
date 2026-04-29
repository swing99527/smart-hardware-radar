import json, subprocess, sys

kw = "smart posture corrector"
cid = "H16"

print(f"[L2/L3] Deep diving into Amazon data for '{kw}'...")

def run_js(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        data = json.loads(res.stdout)
        return data.get("data", [])
    except Exception as e:
        print(f"Error calling JS: {e}")
        return []

# 1. Fetch L3
cmd3 = f"accio-mcp-cli call js_product_database_query --json '{{\"include_keywords\": [\"{kw}\"], \"marketplace\": \"us\", \"min_revenue\": 1000, \"page_size\": 30}}'"
items = run_js(cmd3)
out3 = []
for it in items:
    a = it.get('attributes', {})
    out3.append({
        'asin': it.get('id','').split('/')[-1],
        'title': a.get('title'),
        'brand': a.get('brand'),
        'revenue': a.get('approximate_30_day_revenue') or a.get('revenue'),
        'units_sold': a.get('approximate_30_day_units_sold') or a.get('units_sold'),
        'price': a.get('price'),
        'reviews': a.get('reviews') or a.get('review_count'),
        'rating': a.get('rating')
    })
with open(f"v2/input/l3/{cid}_products.json", "w") as f:
    json.dump(out3, f, ensure_ascii=False, indent=2)
print(f"  -> L3 mapped: {len(out3)} ASINs.")

# 2. Fetch L2
cmd2 = f"accio-mcp-cli call js_keywords_by_keyword --json '{{\"search_terms\": \"{kw}\", \"marketplace\": \"us\", \"page_size\": 10}}'"
kws = run_js(cmd2)
out2 = []
for it in kws:
    a = it.get('attributes', {})
    out2.append({
        'keyword': a.get('name'),
        'search_volume_exact': a.get('monthly_search_volume_exact'),
        'ppc_bid_exact': a.get('exact_suggested_bid'),
        'relevancy_score': a.get('relevancy_score'),
    })
with open(f"v2/input/l2/{cid}_keywords.json", "w") as f:
    json.dump(out2, f, ensure_ascii=False, indent=2)
print(f"  -> L2 mapped: {len(out2)} keywords.")

