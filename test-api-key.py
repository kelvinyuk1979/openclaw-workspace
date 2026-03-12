#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 密钥连通性测试
"""

import requests
import json

API_KEY = "AIzaSyCh7XMJ_P2x3l-01PFE3f-8YO1tIFM-RxA"

print("=" * 60)
print("🔑 API 密钥连通性测试")
print("=" * 60)
print(f"密钥：{API_KEY[:20]}...")
print()

# 测试 1: Google API 通用端点
print("📡 测试 1: Google API 通用端点...")
try:
    url = f"https://www.googleapis.com/discovery/v1/apis?key={API_KEY}"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        print("✅ 连通！密钥有效")
        data = response.json()
        print(f"   可用 API 数量：{len(data.get('items', []))}")
    elif response.status_code == 400:
        print("⚠️  密钥格式正确，但可能需要启用特定 API")
    elif response.status_code == 403:
        print("❌ 密钥无效或已被禁用")
    else:
        print(f"⚠️  响应状态码：{response.status_code}")
except requests.exceptions.Timeout:
    print("❌ 请求超时")
except Exception as e:
    print(f"❌ 错误：{e}")

print()

# 测试 2: YouTube Data API (常见用途)
print("📺 测试 2: YouTube Data API...")
try:
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&chart=mostPopular&maxResults=1&key={API_KEY}"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        print("✅ YouTube API 可用")
    elif response.status_code == 400:
        print("⚠️  YouTube API 未启用")
    elif response.status_code == 403:
        print("❌ YouTube API 访问被拒绝")
    else:
        print(f"⚠️  响应状态码：{response.status_code}")
except Exception as e:
    print(f"❌ 错误：{e}")

print()

# 测试 3: 检查密钥类型
print("🔍 密钥信息:")
print(f"   前缀：AIzaSy (Google API 密钥格式)")
print(f"   长度：{len(API_KEY)} 字符")
print(f"   状态：{'✅ 格式正确' if len(API_KEY) == 39 and API_KEY.startswith('AIzaSy') else '❌ 格式异常'}")

print()
print("=" * 60)
