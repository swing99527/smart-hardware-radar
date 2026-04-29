import json
from pathlib import Path

ROOT = Path("/Users/chenshangwei/code/smart-hardware-radar")

# 1. 注入 L1 维度的 2026 大模型属性
risks = {
    "H01": {"big_tech_risk": 0.8, "ai_alignment": 0.9, "reason": "Apple iOS 18 原生录音摘要降维打击纯软件套壳硬件。"},
    "H02": {"big_tech_risk": 0.9, "ai_alignment": 0.3, "reason": "Samsung Galaxy Ring 已入场，Apple Ring 蓄势待发。"},
    "H03": {"big_tech_risk": 0.2, "ai_alignment": 0.2, "reason": "开放式物理形态是大厂 AirPods 的盲区，大厂不碰，适合中小品牌。"},
    "H04": {"big_tech_risk": 0.95, "ai_alignment": 0.9, "reason": "Meta Ray-Ban 绝对统治，Apple 眼镜研发中，小厂进场秒死。"},
    "H05": {"big_tech_risk": 0.1, "ai_alignment": 0.8, "reason": "长尾桌面伴侣形态，大厂利润看不上，完美承接开源 LLM。"},
    "H06": {"big_tech_risk": 0.4, "ai_alignment": 0.5, "reason": "非接触睡眠，Amazon/Google 尝试过但非主战线。"},
    "H07": {"big_tech_risk": 0.05, "ai_alignment": 0.1, "reason": "大厂不碰嗅觉硬件，物理护城河极深，SaaS订阅极佳。"},
    "H08": {"big_tech_risk": 0.1, "ai_alignment": 0.8, "reason": "垂直细分赛道，结合端侧视觉 AI 识别猫狗行为，高客单大厂盲区。"},
    "H09": {"big_tech_risk": 0.8, "ai_alignment": 0.8, "reason": "手机 App 翻译完美替代，离线硬件成伪需求。"},
    "H10": {"big_tech_risk": 0.1, "ai_alignment": 0.4, "reason": "康复医疗边缘地带，大厂合规嫌麻烦，中小卖家福地。"}
}

for cid, extra in risks.items():
    p = ROOT / f"v2/input/l1/{cid}_signals.json"
    if p.exists():
        data = json.loads(p.read_text())
        data.update(extra)
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False))

# 2. 追加宪法文档说明
doc_path = ROOT / "docs/methodology-hardware.md"
amendment = """
---
## 10. [V1.1 修正案] 2026 大模型时代生存法则

> 2026-04-29 更新：纯电商与纯众筹模型已不足以抵御“大厂降维打击”，特引入三维校验：

### 10.1 大厂射程惩罚 (Big Tech Blast Radius)
如果在 Apple / Meta / Samsung 的核心硬件路线图上（例如：系统级穿戴、手机原生功能平替），将面临巨大的降维打击风险。
**计算规则**：`big_tech_risk` (0~1.0) × 15 分，直接从 `Now Score` 和 `Trend Score` 中双双扣除。

### 10.2 流量溢出共振 (L1 / L2 Scissors)
电商存量 (L2) 很高但社媒冷清 (L1) = 传统红海；社媒极热 (L1) 但亚马逊搜量低 (L2) = 伪需求/教育期。
**计算规则**：只有当 `L1 ≥ 15` 且 `L2 ≥ 15` 时，证明社交病毒流量正疯狂转化为电商真实搜索，此时赋予 `Trend Score` **1.1x** 的乘数奖励。
"""
content = doc_path.read_text()
if "[V1.1 修正案]" not in content:
    doc_path.write_text(content + amendment)

print("V1.1 Patched L1 files and Docs.")
