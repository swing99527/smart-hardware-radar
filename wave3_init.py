import json
from pathlib import Path

ROOT = Path("/Users/chenshangwei/code/smart-hardware-radar")

new_cats = [
    {"id": "H11", "name": "AI 冥想吐纳石", "name_en": "Smart Meditation Device", "tags": ["Wellness", "Mental Health", "Niche"]},
    {"id": "H12", "name": "AI 植物情绪伴侣", "name_en": "Smart Plant Monitor AI", "tags": ["Home", "Viral TikTok", "Subscription"]},
    {"id": "H13", "name": "OTC AI 辅听耳机", "name_en": "OTC Hearing Aid AI", "tags": ["Silver Economy", "FDA OTC", "High AOV"]},
    {"id": "H14", "name": "AI 物理止鼾干预带", "name_en": "Smart Anti Snoring Mask", "tags": ["Sleep", "Health", "Painkiller"]},
    {"id": "H15", "name": "桌面 AI 坐姿监督员", "name_en": "Smart Posture Corrector Vision", "tags": ["Desk", "Vision AI", "Productivity"]},
]

cat_file = ROOT / "data/categories.json"
data = json.loads(cat_file.read_text())
existing_ids = {c["id"] for c in data["categories"]}
for nc in new_cats:
    if nc["id"] not in existing_ids:
        nc["status"] = "watching"
        data["categories"].append(nc)
cat_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))

# --- L1 Signals (High Social, Low Big Tech Risk) ---
l1_data = {
    "H11": {"big_tech_risk": 0.05, "ai_alignment": 0.8, "funding_usd_12m": 2500000, "project_count_12m": 8, "youtube_views_90d": 5000000},
    "H12": {"big_tech_risk": 0.01, "ai_alignment": 0.95, "funding_usd_12m": 3800000, "project_count_12m": 12, "youtube_views_90d": 28000000},
    "H13": {"big_tech_risk": 0.3, "ai_alignment": 0.8, "funding_usd_12m": 8500000, "project_count_12m": 15, "youtube_views_90d": 4500000},
    "H14": {"big_tech_risk": 0.1, "ai_alignment": 0.6, "funding_usd_12m": 4200000, "project_count_12m": 9, "youtube_views_90d": 8800000},
    "H15": {"big_tech_risk": 0.05, "ai_alignment": 0.9, "funding_usd_12m": 1800000, "project_count_12m": 6, "youtube_views_90d": 12000000},
}
for cid, info in l1_data.items():
    info["as_of"] = "2026-04-29"
    (ROOT / f"v2/input/l1/{cid}_signals.json").write_text(json.dumps(info, indent=2, ensure_ascii=False))

# --- L4 Supply Chain Costs ---
l4_data = {
    "H11": {"pcba_bom_usd": 8.0, "mold_cost_usd": 15000, "cert_cost_usd": 8000, "needs_app": True, "saas_cost_per_mau_usd": 0.50},
    "H12": {"pcba_bom_usd": 12.0, "mold_cost_usd": 25000, "cert_cost_usd": 6000, "needs_app": True, "saas_cost_per_mau_usd": 0.30},
    "H13": {"pcba_bom_usd": 25.0, "mold_cost_usd": 40000, "cert_cost_usd": 15000, "needs_app": True, "saas_cost_per_mau_usd": 0.10},
    "H14": {"pcba_bom_usd": 18.0, "mold_cost_usd": 20000, "cert_cost_usd": 12000, "needs_app": True, "saas_cost_per_mau_usd": 0.20},
    "H15": {"pcba_bom_usd": 22.0, "mold_cost_usd": 30000, "cert_cost_usd": 12000, "needs_app": True, "saas_cost_per_mau_usd": 0.80},
}
for cid, info in l4_data.items():
    info["category_id"] = cid
    info["as_of"] = "2026-04-29"
    (ROOT / f"v2/input/l4/{cid}_supply.json").write_text(json.dumps(info, indent=2, ensure_ascii=False))

print("Wave 3 Initialized: Categories, L1 (Low Risk) and L4 created.")
