import urllib.request
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime

def fetch_rss(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_product_hunt(xml_data):
    items = []
    if not xml_data: return items
    try:
        root = ET.fromstring(xml_data)
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            title = entry.find("{http://www.w3.org/2005/Atom}title").text
            content = entry.find("{http://www.w3.org/2005/Atom}content").text or ""
            # 只过滤带有硬件特征的词
            if re.search(r'(device|wearable|hardware|smart|AI|gadget|physical)', title + content, re.IGNORECASE):
                items.append(title)
    except Exception as e:
        pass
    return items

def parse_kickstarter(xml_data):
    items = []
    if not xml_data: return items
    try:
        root = ET.fromstring(xml_data)
        # Kickstarter uses Atom format too
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            title = entry.find("{http://www.w3.org/2005/Atom}title").text
            items.append(title)
    except Exception as e:
        pass
    return items

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] L0 Live Scout Activated...")
    
    ph_xml = fetch_rss("https://www.producthunt.com/feed")
    ph_items = parse_product_hunt(ph_xml)
    
    ks_xml = fetch_rss("https://www.kickstarter.com/projects/feed.atom?category_id=16") # 16 is Technology
    ks_items = parse_kickstarter(ks_xml)
    
    raw_mutants = ph_items + ks_items
    
    print(f"--- 🎯 Found {len(raw_mutants)} potential hardware/tech mutants today ---")
    for i, title in enumerate(raw_mutants[:15]): # 打印前15个
        print(f" {i+1}. {title}")
        
    # 保存原始数据供大模型清洗
    with open("data/raw_mutants_today.json", "w") as f:
        json.dump(raw_mutants, f, ensure_ascii=False, indent=2)
        
    print("\n[Next Step] Feed these raw titles to an LLM to extract 'Seed Keywords'.")

if __name__ == "__main__":
    main()
