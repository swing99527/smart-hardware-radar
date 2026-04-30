import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
CAT_FILE = ROOT / 'data' / 'categories.json'
SCORED_FILE = ROOT / 'data' / 'categories_scored.json'

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
    
    print("[OK] Starting V1.2 Scoring Engine (Direct JSON Parsing)")
    
    for c in data.get('categories', []):
        # We only score items that have been fetched (have JS search volume or total revenue)
        if c.get('status') == 'data_fetched' or 'js_search_volume' in c:
            
            # --- L2 Traffic Score (Search Volume) ---
            # Assume 50,000 monthly search volume is a perfect score of 25 for this layer
            sv = c.get('js_search_volume', 0)
            L2 = min(25, (sv / 50000) * 25)
            
            # --- L3 Monopoly Score (Revenue & CR3) ---
            total_rev = c.get('total_revenue', 0)
            top3_rev = c.get('top_3_revenue', 0)
            
            # Calculate CR3
            c['cr3'] = round((top3_rev / total_rev * 100), 1) if total_rev > 0 else 0
            cr3 = c['cr3']
            
            # CR3 Scoring Logic
            if total_rev == 0:
                L3 = 0
            elif total_rev < 100000 and cr3 > 50:
                # V1.2 Rule: Emerging Market Exemption (Total top 30 rev < 100k, tolerate monopoly)
                L3 = 20 
            elif cr3 > 50:
                # VETO! (Monopoly)
                L3 = 0
            elif cr3 < 20:
                L3 = 25 # Blue Ocean
            else:
                # 20% to 50% CR3 gives proportional score between 25 and 10
                L3 = 25 - ((cr3 - 20) / 30) * 15
                
            # Set default dummy scores for L1 and L4 (since we don't have separate crawler files for them yet)
            L1, L4 = 15.0, 15.0 
            
            # Weights: Now Score = L3(0.5) + L4(0.3) + L2(0.2)
            # Normalizing to 100 point scale (each max 25 -> total max 25. Multiply by 4)
            c['now_score'] = round((L3 * 0.5 + L4 * 0.3 + L2 * 0.2) * 4, 1)
            c['trend_score'] = round((L1 * 0.4 + L3 * 0.4 + L2 * 0.2) * 4, 1)
            
            # Decisions
            veto = (cr3 > 50 and total_rev >= 100000)
            if veto:
                c['decision'] = "❌ 暂缓入场"
                c['status'] = "vetoed"
                if 'tags' not in c: c['tags'] = []
                if "Monopoly Risk" not in c['tags']: c['tags'].append("Monopoly Risk")
            elif c['now_score'] >= 75:
                c['decision'] = "🟢 核心推荐"
                c['status'] = "recommended"
            else:
                c['decision'] = "🟡 保持观望"
                c['status'] = "analyzed"
                
            print(f"  {c['id'][:4]:<4}  {c['name_en'][:30]:<30}  Now={c['now_score']:>5.2f} Trend={c['trend_score']:>5.2f} CR3={c['cr3']:>4}%  {c['decision']}")
            scored_list.append(c)
        else:
            # Leave unscored/untouched items alone
            pass
            
    # Save back to categories.json
    CAT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
    # Save isolated scored file for frontend (similar to old structure)
    scored_output = {
        "schema_version": "2.1",
        "methodology_version": "1.2",
        "generated_at": datetime.now().isoformat() + "Z",
        "categories": scored_list
    }
    SCORED_FILE.write_text(json.dumps(scored_output, indent=2, ensure_ascii=False))
    print(f"\n[OK] scored {len(scored_list)} categories → data/categories_scored.json")

if __name__ == "__main__":
    main()
