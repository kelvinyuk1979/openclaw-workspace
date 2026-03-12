#!/bin/bash
# 小红书自动发布 - 快速启动脚本

cd "$(dirname "$0")"

echo "=============================================="
echo "📱 小红书自动发布"
echo "=============================================="
echo ""

case "$1" in
  generate|gen|g)
    echo "📝 生成内容..."
    python3 content_generator.py
    ;;
  publish|pub|p)
    echo "📤 发布笔记..."
    python3 publisher.py
    ;;
  remind|r)
    echo "🔔 发布提醒..."
    python3 reminder.py
    ;;
  install|i)
    echo "📦 安装依赖..."
    pip3 install playwright
    python3 -m playwright install chromium
    echo "✅ 安装完成"
    ;;
  *)
    echo "用法：$0 {generate|publish|remind|install}"
    echo ""
    echo "  generate  - 生成笔记内容"
    echo "  publish   - 发布笔记 (需要登录)"
    echo "  remind    - 查看发布提醒"
    echo "  install   - 安装依赖"
    ;;
esac
