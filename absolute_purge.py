import json
from pathlib import Path

ROOT = Path("/Users/chenshangwei/code/smart-hardware-radar")

# 1. 彻底清空 categories.json
cat_file = ROOT / "data/categories.json"
data = json.loads(cat_file.read_text())
data["categories"] = []
cat_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
print("categories.json is now 100% EMPTY.")

# 2. 清理 L1, L2, L3, L4 目录下的所有文件
for d in ["v2/input/l1", "v2/input/l2", "v2/input/l3", "v2/input/l4"]:
    dir_path = ROOT / d
    if not dir_path.exists():
        continue
    for file in dir_path.glob("*.json"):
        file.unlink()
        print(f"  Obliterated: {file.relative_to(ROOT)}")

# 3. 清理结果文件
for res_file in ["data/cr3_index.json", "data/categories_scored.json"]:
    p = ROOT / res_file
    if p.exists():
        p.unlink()
        print(f"  Obliterated: {res_file}")

print("Absolute Purge Complete. System is a blank slate. 0 categories remaining.")
