import os
import json
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(ROOT_DIR, 'data', 'categories.json')
SIGNAL_FILE = os.path.join(ROOT_DIR, 'data', 'signals.json')
SOURCE_HEALTH_FILE = os.path.join(ROOT_DIR, 'data', 'source_health.json')
TREND_CLUSTER_FILE = os.path.join(ROOT_DIR, 'data', 'trend_clusters.json')
TREND_RUN_FILE = os.path.join(ROOT_DIR, 'data', 'trend_runs.json')
MARKET_THESIS_FILE = os.path.join(ROOT_DIR, 'data', 'market_theses.json')
DOCS_DIR = os.path.join(ROOT_DIR, 'docs')
DOCS_DATA_FILE = os.path.join(DOCS_DIR, 'data.json')

def comparable_payload(data):
    clean = dict(data)
    clean.pop('last_updated', None)
    return clean

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        
    if os.path.exists(DATA_FILE):
        data = load_json(DATA_FILE, {})
        signals = load_json(SIGNAL_FILE, {"signals": []})
        source_health = load_json(SOURCE_HEALTH_FILE, {"sources": []})
        trend_clusters = load_json(TREND_CLUSTER_FILE, {"clusters": []})
        trend_runs = load_json(TREND_RUN_FILE, {"runs": []})
        market_theses = load_json(MARKET_THESIS_FILE, {"theses": []})
        data['signals'] = signals.get('signals', [])
        data['source_health'] = source_health.get('sources', [])
        data['trend_clusters'] = trend_clusters.get('clusters', [])
        data['trend_runs'] = trend_runs.get('runs', [])
        data['market_theses'] = market_theses.get('theses', [])
            
        existing = None
        if os.path.exists(DOCS_DATA_FILE):
            try:
                with open(DOCS_DATA_FILE, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            except json.JSONDecodeError:
                existing = None

        if existing and comparable_payload(existing) == comparable_payload(data):
            print(f"✅ Dashboard data already up to date: {DOCS_DATA_FILE}")
            return

        data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(DOCS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Data synced to {DOCS_DATA_FILE} for GitHub Pages.")
    else:
        print("⚠️ No data/categories.json found to sync.")

if __name__ == '__main__':
    main()
