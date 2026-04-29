import re

# 1. 修正 cr3.py，记录是否豁免
with open("scripts/cr3.py", "r") as f:
    text = f.read()

# 替换 cr3 超过 0.5 时固定 veto 的逻辑
text = re.sub(
    r'"veto_flag": cr3 > 0.50,',
    r'"veto_flag": cr3 > 0.50 and total_revenue >= 100000,\n        "is_emerging": total_revenue < 100000 and total_revenue > 0,',
    text
)
with open("scripts/cr3.py", "w") as f:
    f.write(text)

# 2. 修正 score.py 中的 L3a 逻辑
with open("scripts/score.py", "r") as f:
    score_text = f.read()

new_l3a_logic = """
    # L3a: anti-monopoly band [V1.2] Emerging Exemption
    is_emerging = cr3_info.get("is_emerging", False)
    if cr3 is None:
        L3a = 0
    elif is_emerging:
        L3a = 6.0  # 拓荒期中立分，免除垄断罚分
    elif cr3 > 0.50:
        L3a = 0
    elif cr3 <= 0.20: L3a = 12
    elif cr3 <= 0.30: L3a = 10
    elif cr3 <= 0.40: L3a = 7
    else: L3a = 4
"""

score_text = re.sub(
    r'# L3a: anti-monopoly band\n.*?else: L3a = 4.*?\n',
    new_l3a_logic + "\n",
    score_text,
    flags=re.DOTALL
)

# 确保版本号更新为 1.2
score_text = score_text.replace('METHODOLOGY_VERSION = "1.1"', 'METHODOLOGY_VERSION = "1.2"')

with open("scripts/score.py", "w") as f:
    f.write(score_text)
print("Engines patched to V1.2.")
