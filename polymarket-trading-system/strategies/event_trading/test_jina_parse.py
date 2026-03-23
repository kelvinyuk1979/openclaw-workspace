#!/usr/bin/env python3
import requests

# 抓取内容
url = "https://r.jina.ai/http://polymarket.com/search"
resp = requests.get(url, timeout=15)
content = resp.text

print("原始内容（前 5000 字符）:")
print("=" * 70)
print(content[:5000])
print("=" * 70)
print()

# 分析结构
lines = content.split('\n')
print(f"总行数：{len(lines)}")
print()

# 找包含%的行
print("包含百分比的行:")
for i, line in enumerate(lines):
    if '%' in line and '[' in line:
        print(f"行{i}: {line[:200]}")
