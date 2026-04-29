import os

filepath = 'scripts/scout_l0_advanced.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换 LLM 提取函数，使其支持通用的 LLM_BASE_URL 和 LLM_MODEL
new_func = """def llm_keyword_extraction(raw_title):
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key: return None
        
    # 通用化配置：支持 DeepSeek, 硅基流动, 通义千问等任何兼容 OpenAI 格式的 API
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1/chat/completions")
    if not base_url.endswith("/chat/completions"):
        base_url = base_url.rstrip("/") + "/chat/completions"
        
    model_name = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    prompt = f'You are an expert hardware analyst. Strip brand names and marketing buzzwords from this product title and return ONLY the generic 2-to-4 word English category name.\\nExample: "Oura Ring Gen 3: The Ultimate Health Tracking Smart Ring" -> "Smart Ring Health Tracker"\\nTitle: "{raw_title}"\\nOutput:'
    
    data = {"model": model_name, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1, "max_tokens": 10}
    
    try:
        req = urllib.request.Request(base_url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['choices'][0]['message']['content'].strip(' "\\\'.')
    except Exception as e:
        print(f"    [LLM API Error using {model_name} at {base_url}] {e}")
        return None"""

# 使用正则表达式替换旧的函数
import re
content = re.sub(r'def llm_keyword_extraction\(raw_title\):.*?return None(?=\n\ndef heuristic_keyword_extraction)', new_func, content, flags=re.DOTALL)

# 替换 print 提示信息
content = content.replace('if os.getenv("OPENAI_API_KEY"): print("  -> 🧠 LLM Brain Connected (OpenAI API Key detected)")', 'if os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY"): print(f"  -> 🧠 LLM Brain Connected ({os.getenv(\'LLM_MODEL\', \'gpt-4o-mini\')} API detected)")')
content = content.replace('else: print("  -> ⚠️ No OPENAI_API_KEY found. Running in NLP Heuristic Fallback mode.")', 'else: print("  -> ⚠️ No LLM_API_KEY found. Running in NLP Heuristic Fallback mode.")')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("scout_l0_advanced.py patched for universal LLM support.")
