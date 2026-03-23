#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Gamma API 返回的数据结构
"""

import requests
import json

url = "https://gamma-api.polymarket.com/markets"
params = {'limit': 5}
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'application/json'
}

print("🔍 请求 Gamma API...")
response = requests.get(url, params=params, headers=headers, timeout=10)

print(f"状态码：{response.status_code}")
print()

if response.status_code == 200:
    data = response.json()
    
    print("📦 返回数据结构:")
    print(f"类型：{type(data)}")
    if isinstance(data, list):
        print(f"数量：{len(data)} 条")
        if data:
            print(f"\n第一条数据字段:")
            first = data[0]
            for key in list(first.keys())[:15]:
                value = first[key]
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                print(f"  {key}: {value}")
            
            print(f"\n完整第一条记录 (JSON):")
            print(json.dumps(first, indent=2, ensure_ascii=False)[:2000])
    elif isinstance(data, dict):
        print(f"键：{list(data.keys())}")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
else:
    print(f"错误：{response.text[:500]}")
