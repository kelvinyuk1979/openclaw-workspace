#!/usr/bin/env python3
import re

# 读取缓存数据
with open('/tmp/poly_test.txt', 'r') as f:
    content = f.read()

lines = content.split('\n')

print("查找市场标题和交易量:")
print("=" * 70)

current_title = None
for i, line in enumerate(lines):
    line = line.strip()
    
    # 找市场标题
    if '/event/' in line and '](' in line and line.startswith('['):
        title = line.split('](')[0].replace('[', '').strip()
        print(f"\n📍 市场：{title}")
        current_title = title
    
    # 找交易量
    if current_title and '$' in line and 'Vol' in line:
        print(f"   💰 {line.strip()}")
    
    # 找 outcomes
    if current_title and '](' in line and '%' in line and 'Image' not in line:
        matches = re.findall(r'\[([^\]]+)\]', line)
        for m in matches:
            if '%' in m:
                print(f"   📊 {m}")
