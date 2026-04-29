from pathlib import Path

ROOT = Path("/Users/chenshangwei/code/smart-hardware-radar")
doc_path = ROOT / "docs/methodology-hardware.md"

amendment = """
### 10.3 [V1.2 修正案] 拓荒期豁免机制 (Emerging Market Exemption)
**问题背景**：对于极其新兴的品类（如月销刚起步），全网可能只有 2-3 个卖家，导致 CR3 必然 > 50%。原 V1.1 规则会将此类“真蓝海”误杀为“巨头垄断”。
**修订规则**：
当且仅当该品类 Top 30 ASIN 的总月营收 **< $100,000 (十万美金)** 时，判定该市场处于“拓荒期 (Emerging)”。
此时：
1. **取消 CR3 > 50% 的一票否决 (Veto = False)**。
2. L3a 维度（反垄断得分）强制记为中性分 **6 分**，不再因集中度高而罚到 0 分。
3. 最终决策完全交由 L1（社媒热度）和 L4（落地成本）来主导。
"""

content = doc_path.read_text(encoding="utf-8")
if "[V1.2 修正案]" not in content:
    doc_path.write_text(content + "\n" + amendment, encoding="utf-8")

print("V1.2 methodology documented.")
