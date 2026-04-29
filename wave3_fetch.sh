#!/bin/bash
ROOT="/Users/chenshangwei/code/smart-hardware-radar"
cd $ROOT

declare -A KWS=(
  ["H11"]="smart meditation device"
  ["H12"]="smart plant monitor"
  ["H13"]="OTC hearing aid"
  ["H14"]="smart anti snoring device"
  ["H15"]="smart posture corrector"
)

# Function to parse product JSON securely
parse_products() {
  python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    items = data.get('data', [])
    out = []
    for it in items:
        a = it.get('attributes', {})
        out.append({
            'asin': it.get('id','').split('/')[-1],
            'title': a.get('title'),
            'brand': a.get('brand'),
            'revenue': a.get('approximate_30_day_revenue') or a.get('revenue'),
            'units_sold': a.get('approximate_30_day_units_sold') or a.get('units_sold'),
            'price': a.get('price'),
            'reviews': a.get('reviews') or a.get('review_count'),
            'rating': a.get('rating')
        })
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
except Exception as e:
    json.dump([], sys.stdout)
"
}

# Function to parse keywords JSON securely
parse_keywords() {
  python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    items = data.get('data', [])
    out = []
    for it in items:
        a = it.get('attributes', {})
        out.append({
            'keyword': a.get('name'),
            'search_volume_exact': a.get('monthly_search_volume_exact'),
            'ppc_bid_exact': a.get('exact_suggested_bid'),
            'relevancy_score': a.get('relevancy_score'),
        })
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
except Exception as e:
    json.dump([], sys.stdout)
"
}

for cid in "${!KWS[@]}"; do
  kw="${KWS[$cid]}"
  echo "Fetching L3 Products for $cid ($kw)..."
  accio-mcp-cli call js_product_database_query --json "{\"include_keywords\": [\"$kw\"], \"marketplace\": \"us\", \"min_revenue\": 1000, \"page_size\": 30}" | parse_products > "v2/input/l3/${cid}_products.json"
  
  echo "Fetching L2 Keywords for $cid ($kw)..."
  accio-mcp-cli call js_keywords_by_keyword --json "{\"search_terms\": \"$kw\", \"marketplace\": \"us\", \"page_size\": 10}" | parse_keywords > "v2/input/l2/${cid}_keywords.json"
done

echo "Fetch complete. Running scoring engine..."
python3 scripts/cr3.py
python3 scripts/score.py
