import json
from pathlib import Path
import shutil

ROOT = Path("/Users/chenshangwei/code/smart-hardware-radar")

# 1. 清理 categories.json
cat_file = ROOT / "data/categories.json"
data = json.loads(cat_file.read_text())
cleaned_cats = [c for c in data["categories"] if c["id"] in ("H01", "H03")]
data["categories"] = cleaned_cats
cat_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
print(f"Purged categories.json. Remaining: {[c['id'] for c in cleaned_cats]}")

# 2. 清理 L1, L2, L3, L4 目录下的无用文件
directories = ["v2/input/l1", "v2/input/l2", "v2/input/l3", "v2/input/l4"]
for d in directories:
    dir_path = ROOT / d
    if not dir_path.exists():
        continue
    for file in dir_path.glob("*.json"):
        # 如果文件名不是 H01 或 H03 开头，全部删除
        if not file.name.startswith("H01_") and not file.name.startswith("H03_"):
            file.unlink()
            print(f"  Deleted: {file.relative_to(ROOT)}")

# 3. 清空生成的结果文件，强制下次重新跑
for res_file in ["data/cr3_index.json", "data/categories_scored.json"]:
    p = ROOT / res_file
    if p.exists():
        p.unlink()
        print(f"  Deleted generated file: {res_file}")

print("The Great Purge completed. System reset to true seed state.")
