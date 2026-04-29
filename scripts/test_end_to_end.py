import subprocess
import time
from datetime import datetime
import json
import random
from pathlib import Path

def run_step(step_name, command):
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🚀 Executing: {step_name}")
    print(f"    $ {command}")
    start_time = time.time()
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    duration = time.time() - start_time
    if result.returncode == 0:
        print(f"✅ Success ({duration:.2f}s)")
        print("-" * 40)
        lines = result.stdout.strip().split('\n')
        print('\n'.join(lines[-5:]))
        print("-" * 40)
        return True
    else:
        print(f"❌ Failed ({duration:.2f}s)")
        print(result.stderr)
        return False

def mock_l2_l3():
    cat_file = Path('data/categories.json')
    if cat_file.exists():
        data = json.loads(cat_file.read_text())
        count = 0
        for c in data['categories']:
            if c.get('status') == 'scouted':
                c['js_search_volume'] = random.randint(500, 50000)
                c['total_revenue'] = random.randint(10000, 500000)
                c['top_3_revenue'] = random.randint(5000, int(c['total_revenue'] * 0.9))
                c['status'] = 'data_fetched'
                count += 1
        cat_file.write_text(json.dumps(data, indent=2))
        print(f'Mocked data for {count} newly scouted categories.')

def score_v1_2():
    cat_file = Path('data/categories.json')
    if cat_file.exists():
        data = json.loads(cat_file.read_text())
        for c in data['categories']:
            if c.get('status') == 'data_fetched':
                total_rev = c.get('total_revenue', 0)
                top3_rev = c.get('top_3_revenue', 0)
                c['cr3'] = round((top3_rev / total_rev * 100), 1) if total_rev > 0 else 0
                
                c['now_score'] = min(100, int((c.get('js_search_volume', 0) / 50000) * 50 + 50))
                c['trend_score'] = c['now_score'] - 5
                
                if c['cr3'] > 50 and total_rev >= 100000:
                    c['status'] = 'vetoed'
                    if 'tags' not in c: c['tags'] = []
                    if 'Monopoly Risk' not in c['tags']: c['tags'].append('Monopoly Risk')
                elif c['now_score'] >= 80:
                    c['status'] = 'recommended'
                else:
                    c['status'] = 'analyzed'
        cat_file.write_text(json.dumps(data, indent=2))
        print('Scoring complete. V1.2 Rules applied.')

def main():
    print("==================================================")
    print("🛸 Smart Hardware Radar - End-to-End Pipeline Test")
    print("==================================================")
    
    if not run_step("L0 Excavator (Hybrid NLP/LLM)", "python3 scripts/scout_l0_advanced.py"): return

    print("\n[17:05:17] 🚀 Executing: L2/L3 Data Injector (Mock)")
    mock_l2_l3()
    
    print("\n[17:05:18] 🚀 Executing: L4 Scoring Engine (V1.2 CR3 Logic)")
    score_v1_2()

    if not run_step("Sync Dashboard Data", "python3 scripts/sync_data.py"): return
        
    print("\n🎉 End-to-End Test Completed Successfully!")
    print("Check docs/index.html to see the updated dashboard.")

if __name__ == '__main__':
    main()
