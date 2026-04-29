#!/bin/bash
set -e

echo "=================================================="
echo "🛸 Smart Hardware Radar - Local Heavy Artillery"
echo "=================================================="

# 第一步：把云端昨晚抓出来的新品种拉回本地
echo "[1/5] 📥 正在从 GitHub 同步昨夜挖掘出来的新品类..."
git pull origin main || echo "  ⚠️ 同步遇到小阻力，但可以继续本地流..."

# 第二步：本地重火力爬虫，真实调用 Jungle Scout MCP
echo "[2/5] 📡 正在激活 L2/L3 本地 JS 穿透引擎..."
python3 scripts/fetch_js_data.py

# 第三步：L4 防御系统，计算垄断分、给出投资建议
echo "[3/5] ⚖️ 正在进行 L4 垄断度防御测试与最终评分..."
python3 scripts/score.py

# 第四步：推流到本地 Dashboard 的 data.json
echo "[4/5] 📊 正在同步数据看板 Dashboard..."
python3 scripts/sync_data.py

# 第五步：将最终结果（打完分的 JSON 和 Dashboard 数据）部署回 GitHub Pages
echo "[5/5] 🚀 正在将最终 Intelligence 面板推回云端..."
git add data/categories.json docs/data.json docs/index.html
# 仅仅提交这俩核心数据文件，忽略其他不相关的本地更改
if ! git diff --quiet --staged; then
  git commit -m "🚀 Local-Sync: 完成 JS 真实销量查询与 Dashboard 推流"
  git push origin main
  echo "✅ Dashboard 已上线！打开你的 GitHub Pages 开始看雷达吧！"
else
  echo "😴 没有任何新数据需要推流。引擎休息。"
fi

echo "=================================================="
