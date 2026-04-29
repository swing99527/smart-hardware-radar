text = open("scripts/score.py").read()

def replace_func(src):
    import re
    p = re.compile(r'def score_category\(.*?\n\ndef main', re.DOTALL)
    
    new_func = """def score_category(
    cat: dict, cr3_index: dict, only: str | None = None
) -> dict | None:
    cid = cat["id"]
    if only and cid != only:
        return None

    l1_raw = load_json(L1_DIR / f"{cid}_signals.json")
    l2_raw = load_json(L2_DIR / f"{cid}_keywords.json")
    l3_products = load_json(L3_DIR / f"{cid}_products.json")
    l4_raw = load_json(L4_DIR / f"{cid}_supply.json")

    L1, l1_meta = score_l1(l1_raw)
    L2, l2_meta = score_l2(l2_raw)
    cr3_info = (cr3_index.get("categories", {}) or {}).get(cid)
    L3, l3_meta, veto = score_l3(l3_products, cr3_info)
    L4, l4_meta = score_l4(l4_raw)

    now_score = round(L3 * 0.50 + L4 * 0.30 + L2 * 0.20, 2)
    trend_score = round(L1 * 0.40 + L3 * 0.40 + L2 * 0.20, 2)
    
    # [V1.1] Big Tech Risk
    big_tech_risk = float(l1_raw.get("big_tech_risk", 0.0)) if l1_raw else 0.0
    penalty = round(big_tech_risk * 15.0, 2)
    now_score = max(0.0, now_score - penalty)
    trend_score = max(0.0, trend_score - penalty)
    
    # [V1.1] Resonance Bonus
    resonance = False
    if L1 >= 15.0 and L2 >= 15.0:
        trend_score = round(trend_score * 1.1, 2)
        resonance = True

    decision, status = derive_decision(now_score, trend_score, veto)

    return {
        "id": cid, "name": cat.get("name"), "name_en": cat.get("name_en"), "tags": cat.get("tags", []),
        "scores": {"L1": L1, "L2": L2, "L3": L3, "L4": L4},
        "total": round(L1 + L2 + L3 + L4, 1),
        "now_score": round(now_score, 2), "trend_score": round(trend_score, 2),
        "decision": decision, "status": status, "veto_flag": veto,
        "methodology_version": METHODOLOGY_VERSION,
        "calculated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "details": {
            "v1_1_rules": {"big_tech_risk_penalty": penalty, "l1_l2_resonance_bonus": resonance},
            "L1": l1_meta, "L2": l2_meta, "L3": l3_meta, "L4": l4_meta
        }
    }

def main"""
    return p.sub(new_func, src)

with open("scripts/score.py", "w") as f:
    f.write(replace_func(text))
