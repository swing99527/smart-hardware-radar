import re
text = open("scripts/cr3.py").read()
# 给空数据分支补上确实的字段
text = text.replace(
    '            "data_quality": "no_revenue_data",',
    '            "brand_total_count": 0, "asin_total_count": 0, "data_quality": "no_revenue_data",'
)
with open("scripts/cr3.py", "w") as f:
    f.write(text)
