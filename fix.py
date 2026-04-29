import re
text = open("scripts/score.py").read()
# 找到 derive_decision 后面的 return dict
text = re.sub(
    r'return \{\s*"id": cid,.*?details": \{.*', 
    r'''return {
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
    }''', 
    text, flags=re.DOTALL
)

# 追加 main
main_block = """
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="只评分单个品类 (如 H03)")
    args = parser.parse_args()

    cats_doc = load_json(CATEGORIES_FILE)
    if not cats_doc:
        raise SystemExit(f"Missing {CATEGORIES_FILE}")
    cr3_index = load_json(CR3_FILE) or {"categories": {}}

    results = []
    for cat in cats_doc.get("categories", []):
        scored = score_category(cat, cr3_index, args.only)
        if scored:
            results.append(scored)

    output = {
        "schema_version": "2.1",
        "methodology_version": METHODOLOGY_VERSION,
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "categories": results,
    }
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"[OK] scored {len(results)} categories → {OUTPUT_FILE.relative_to(ROOT)}")
    for r in results:
        veto = " 🚫VETO" if r["veto_flag"] else ""
        print(
            f"  {r['id']:5s} {r.get('name_en','')[:35]:35s} "
            f"Now={r['now_score']:>5.2f} Trend={r['trend_score']:>5.2f}  "
            f"{r['decision']}{veto}"
        )

if __name__ == "__main__":
    main()
"""
with open("scripts/score.py", "w") as f:
    f.write(text + "\n" + main_block)
