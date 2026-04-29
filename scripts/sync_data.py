import os
import json
import shutil
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(ROOT_DIR, 'data', 'categories.json')
DOCS_DIR = os.path.join(ROOT_DIR, 'docs')
DOCS_DATA_FILE = os.path.join(DOCS_DIR, 'data.json')

def main():
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 添加最后更新时间戳，让前端面板显示
        data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(DOCS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Data synced to {DOCS_DATA_FILE} for GitHub Pages.")
    else:
        print("⚠️ No data/categories.json found to sync.")

if __name__ == '__main__':
    main()
