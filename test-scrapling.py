#!/usr/bin/env python3
"""Scrapling 测试脚本 - 演示基础抓取和解析功能"""

from scrapling.fetchers import Fetcher

print("=" * 60)
print("🕷️  Scrapling 测试演示")
print("=" * 60)

# 测试 1: 基础 HTTP 请求
print("\n【测试 1】基础 HTTP 请求 + CSS 选择器")
print("-" * 60)

try:
    page = Fetcher.get('https://quotes.toscrape.com/', stealthy_headers=True)
    print(f"✅ 请求成功!")
    print(f"✅ 页面标题：{page.css('title::text').get()}")
    
    # 抓取名言
    quotes = page.css('.quote')
    print(f"\n📊 找到 {len(quotes)} 条名言\n")
    
    for i, quote in enumerate(quotes[:3], 1):
        text = quote.css('.text::text').get()
        author = quote.css('.author::text').get()
        tags = quote.css('.tag::text').get_all()
        
        print(f"{i}. \"{text}\"")
        print(f"   — {author}")
        print(f"   标签：{', '.join(tags)}\n")
    
    print("✅ 测试 1 通过!")
    
except Exception as e:
    print(f"❌ 测试 1 失败：{e}")

# 测试 2: XPath 选择器
print("\n【测试 2】XPath 选择器")
print("-" * 60)

try:
    authors = page.xpath('//span[@class="text"]/following-sibling::span/small/text()').get_all()
    print(f"✅ 用 XPath 找到 {len(authors)} 位作者")
    print(f"   前 3 位：{', '.join(authors[:3])}")
    print("✅ 测试 2 通过!")
except Exception as e:
    print(f"❌ 测试 2 失败：{e}")

# 测试 3: 元素导航
print("\n【测试 3】元素导航 (parent/find_similar)")
print("-" * 60)

try:
    first_quote = page.css('.quote')[0]
    parent = first_quote.parent
    
    print(f"✅ 第一个名言元素的父标签：<{parent.tag}>")
    
    # 查找相似元素
    similar = first_quote.find_similar()
    print(f"✅ 找到 {len(similar)} 个相似元素")
    print("✅ 测试 3 通过!")
except Exception as e:
    print(f"❌ 测试 3 失败：{e}")

# 测试 4: 导出为 JSON
print("\n【测试 4】数据导出为 JSON")
print("-" * 60)

try:
    data = []
    for quote in page.css('.quote')[:3]:
        data.append({
            'text': quote.css('.text::text').get(),
            'author': quote.css('.author::text').get(),
            'tags': quote.css('.tag::text').get_all()
        })
    
    import json
    print("✅ 导出 JSON 数据:")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print("✅ 测试 4 通过!")
except Exception as e:
    print(f"❌ 测试 4 失败：{e}")

# 测试 5: 查找类似元素
print("\n【测试 5】智能查找类似元素")
print("-" * 60)

try:
    # 基于第一个 quote 查找所有类似的
    first = page.css('.quote')[0]
    similar_elements = first.find_similar()
    print(f"✅ 基于第一个元素找到 {len(similar_elements)} 个相似元素")
    
    # 演示 below_elements
    below = first.below_elements
    print(f"✅ 第一个元素下方有 {len(below)} 个元素")
    print("✅ 测试 5 通过!")
except Exception as e:
    print(f"❌ 测试 5 失败：{e}")

print("\n" + "=" * 60)
print("🎉 所有测试完成!")
print("=" * 60)
