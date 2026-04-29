import os
import openai

def extract_category_keyword_via_llm(raw_title: str) -> str:
    """
    使用 OpenAI 的大语言模型进行终极清洗。
    此方法极其聪明，能理解隐喻和变形，但需要消耗 API Token。
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    prompt = f"""
    You are an expert e-commerce and hardware analyst.
    I will give you a promotional title of a new hardware project from Kickstarter or Product Hunt.
    Your task is to strip away the brand name, marketing buzzwords (like 'World's first', 'revolutionary'), 
    and output ONLY the generic 2-to-4 word English category name for this product.
    For example:
    Input: "Oura Ring Gen 3: The Ultimate Health Tracking Smart Ring" -> Output: "Smart Ring Health Tracker"
    Input: "Plaud Note - ChatGPT AI Voice Recorder" -> Output: "AI Voice Recorder"
    
    Input: "{raw_title}"
    Output:
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", # 对于这个任务，3.5 完全足够且便宜
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=10
        )
        return response.choices[0].message['content'].strip().strip('"')
    except Exception as e:
        print(f"LLM API Error: {e}")
        return None
