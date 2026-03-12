#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书发布提醒
定时生成内容并提醒发布
"""

import json
import os
import subprocess
from datetime import datetime

CONFIG_FILE = "config.json"
OUTPUT_DIR = "posts"

def load_config():
    """加载配置"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"bestTimes": ["08:00", "12:30", "21:00"]}

def generate_content():
    """调用内容生成器"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    generator = os.path.join(script_dir, "content_generator.py")
    
    try:
        result = subprocess.run(
            ["python3", generator],
            capture_output=True,
            text=True,
            cwd=script_dir
        )
        return result.stdout
    except Exception as e:
        return f"生成失败：{e}"

def get_latest_post():
    """获取最新生成的笔记"""
    if not os.path.exists(OUTPUT_DIR):
        return None
    
    files = sorted(os.listdir(OUTPUT_DIR), reverse=True)
    if files:
        return os.path.join(OUTPUT_DIR, files[0])
    return None

def send_reminder():
    """发送提醒"""
    config = load_config()
    
    # 生成内容
    print("📝 正在生成今日内容...")
    gen_result = generate_content()
    print(gen_result)
    
    # 获取最新笔记
    latest = get_latest_post()
    
    now = datetime.now()
    time_str = now.strftime("%H:%M")
    
    # 检查是否在建议发布时间
    best_times = config.get("bestTimes", [])
    is_best_time = time_str in best_times
    
    print()
    print("=" * 60)
    print("🔔 小红书发布提醒")
    print("=" * 60)
    print(f"⏰ 当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 流量时段：{'✅ 是' if is_best_time else '⚠️ 非最佳'}")
    print()
    
    if latest:
        print(f"📄 最新笔记：{latest}")
        print()
        print("📋 发布步骤:")
        print("  1. 打开笔记文件查看内容")
        print("  2. 打开小红书 APP")
        print("  3. 点击 + 发布笔记")
        print("  4. 粘贴文案，添加图片")
        print("  5. 添加标签后发布")
    else:
        print("⚠️ 暂无笔记，请先生成内容")
    
    print()
    print("=" * 60)
    print("💡 发布命令:")
    print("   cd xiaohongshu-auto && ./run.sh publish")
    print()
    print("   或：python3 publisher.py")
    print("=" * 60)
    
    return {
        "time": now.isoformat(),
        "is_best_time": is_best_time,
        "latest_post": latest
    }

if __name__ == "__main__":
    send_reminder()
