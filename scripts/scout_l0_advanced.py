import urllib.request
import xml.etree.ElementTree as ET
import json
import re
import os
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAT_FILE = ROOT / "data" / "categories.json"

FEEDS = [
    {"name": "Product Hunt", "url": "https://www.producthunt.com/feed"},
    {"name": "Kickstarter Tech", "url": "https://www.kickstarter.com/projects/feed.atom?category_id=16"},
    {"name": "Kickstarter Design", "url": "https://www.kickstarter.com/projects/feed.atom?category_id=7"},
    # Reddit RSS 总是 403 封杀爬虫，我们加上伪装的 Header
    {"name": "Reddit Gadgets", "url": "https://www.reddit.com/r/gadgets/hot.rss"}
]

def fetch_rss(url):
    try:
        # 增加更真实的 User-Agent 以绕过 Reddit 等平台的反爬机制
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read()
    except Exception as e:
        print(f"[!] Error fetching {url}: {e}")
        return None

def parse_feed(xml_data, source_name):
    items = []
    if not xml_data: return items
    try:
        root = ET.fromstring(xml_data)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns):
            title_node = entry.find("atom:title", ns)
            if title_node is not None:
                title = title_node.text
                # 加入更严苛的硬件词性过滤，减少 LLM 处理非硬件新闻的成本
                if re.search(r'(device|wearable|hardware|smart|AI|gadget|robot|camera|sensor|audio|tracker|monitor)', title, re.IGNORECASE):
                    items.append(title)
    except Exception:
        pass
    return items

def llm_keyword_extraction(raw_title):
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key: return None
        
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1/chat/completions")
    if not base_url.endswith("/chat/completions"):
        base_url = base_url.rstrip("/") + "/chat/completions"
        
    model_name = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    
    # 增加更强烈的指令，让大模型直接过滤掉非硬件的垃圾项目（比如书、电影、保健品等）
    prompt = f"""You are an expert hardware analyst. 
Your task is to strip brand names and marketing buzzwords from this product title and return ONLY the generic 2-to-4 word English category name.
CRITICAL RULE: If the product is clearly NOT a physical technology hardware device (e.g. it is a book, a movie documentary, a software service, food, or a supplement), you MUST return the exact word "IGNORE".
Example 1: "Oura Ring Gen 3: The Ultimate Health Tracking Smart Ring" -> "Smart Ring Health Tracker"
Example 2: "Muslims in America Road Trip by Mahtab" -> "IGNORE"
Example 3: "Journey Through Chai Documentary" -> "IGNORE"
Example 4: "Plurai..." -> "IGNORE" (if it sounds like software or supplement)

Title: "{raw_title}"
Output:"""
    
    data = {"model": model_name, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1, "max_tokens": 10}
    
    try:
        req = urllib.request.Request(base_url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['choices'][0]['message']['content'].strip(' "\'.')
    except Exception as e:
        print(f"    [LLM API Error using {model_name} at {base_url}] {e}")
        return None

def heuristic_keyword_extraction(raw_title):
    parts = re.split(r'[:\|\-\u2013\u2014]', raw_title)
    target_part = max(parts, key=len).strip()
    bullshit_words = [r"world'?s\s+first", r"ultimate", r"smartest", r"best", r"revolutionary", r"innovative", r"next[-\s]gen(eration)?", r"100%", r"kickstarter", r"indiegogo", r"introducing"]
    for bw in bullshit_words:
        target_part = re.sub(bw, "", target_part, flags=re.IGNORECASE)
    target_part = re.sub(r'^[^\w\d]+|[^\w\d]+$', '', target_part).strip()
    words = target_part.split()
    if len(words) > 5:
        hw_nouns = ['tracker', 'monitor', 'camera', 'robot', 'wearable', 'headphones', 'earbuds', 'ring', 'glasses', 'device', 'sensor']
        for i, w in enumerate(words):
            if w.lower() in hw_nouns:
                start = max(0, i - 2)
                return " ".join(words[start:i+1]).title()
        return " ".join(words[:4]).title()
    elif len(words) >= 2:
        return target_part.title()
    return None

def clean_title_hybrid(raw_title):
    kw = llm_keyword_extraction(raw_title)
    if kw: 
        if kw.upper() == "IGNORE":
            return None, "FILTERED"
        return kw, "LLM"
    kw = heuristic_keyword_extraction(raw_title)
    if kw: return kw, "NLP"
    return None, None

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚜 Advanced LLM Excavator Activated...")
    if os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY"): print(f"  -> 🧠 LLM Brain Connected ({os.getenv('LLM_MODEL', 'gpt-4o-mini')} API detected)")
    else: print("  -> ⚠️ No LLM_API_KEY found. Running in NLP Heuristic Fallback mode.")
        
    raw_titles = []
    for feed in FEEDS:
        xml = fetch_rss(feed['url'])
        titles = parse_feed(xml, feed['name'])
        raw_titles.extend(titles)
        
    raw_titles = list(set(raw_titles))
    print(f"\n🎯 Total raw hardware-related mutants found today: {len(raw_titles)}")
    
    seed_keywords = set()
    print("⚙️ Running Hybrid Cleaning Engine...")
    for t in raw_titles[:20]:
        kw, engine = clean_title_hybrid(t)
        if engine == "FILTERED":
            print(f"  [🛡️ FILTERED] '{t[:40]}...' -> NOT HARDWARE")
            continue
            
        if kw and len(kw) > 3:
            print(f"  [{engine}] '{t[:40]}...' -> {kw}")
            seed_keywords.add(kw)
            
    if not CAT_FILE.exists():
        CAT_FILE.parent.mkdir(parents=True, exist_ok=True)
        CAT_FILE.write_text(json.dumps({"schema_version": "2.1", "categories": []}))
        
    cats_doc = json.loads(CAT_FILE.read_text())
    existing_kws = {c.get("name_en", "").lower() for c in cats_doc.get("categories", [])}
    
    next_id = len(cats_doc["categories"]) + 1
    new_added = 0
    
    print("\n📦 Injecting into Radar Pipeline:")
    for kw in seed_keywords:
        if kw.lower() not in existing_kws:
            new_id = f"A{next_id:03d}"
            cats_doc["categories"].append({
                "id": new_id, "name": f"【AI自动嗅探】{kw}", "name_en": kw,
                "status": "scouted", "tags": ["Auto-Discovered", "LLM-Processed"]
            })
            next_id += 1
            new_added += 1
            
    if new_added > 0:
        CAT_FILE.write_text(json.dumps(cats_doc, indent=2, ensure_ascii=False))
        print(f"\n✅ {new_added} new keywords firmly planted in categories.json.")
    else:
        print("\n😴 No new unique keywords found. Engine will rest.")

if __name__ == '__main__':
    main()
