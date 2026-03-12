#!/bin/bash
# 模型切换脚本

CONFIG_FILE="/Users/kelvin/.openclaw/openclaw.json"

echo "====================="
echo "🔄 模型切换"
echo "====================="

CURRENT=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('agents', {}).get('defaults', {}).get('model', {}).get('primary', 'unknown'))")

echo "当前主模型: $CURRENT"
echo ""

case "$1" in
  gemini)
    echo "切换主模型到 Gemini..."
    python3 -c "import json; d=json.load(open('$CONFIG_FILE')); d.setdefault('agents', {}).setdefault('defaults', {}).setdefault('model', {})['primary'] = 'google/gemini-3.1-pro-preview'; json.dump(d, open('$CONFIG_FILE', 'w'), indent=2)"
    echo "✅ 已将主模型切换为 Gemini"
    ;;
  qwen)
    echo "切换主模型到 Qwen..."
    python3 -c "import json; d=json.load(open('$CONFIG_FILE')); d.setdefault('agents', {}).setdefault('defaults', {}).setdefault('model', {})['primary'] = 'dashscope/qwen3.5-plus'; json.dump(d, open('$CONFIG_FILE', 'w'), indent=2)"
    echo "✅ 已将主模型切换为 Qwen"
    ;;
  status)
    echo "当前主模型: $(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('agents', {}).get('defaults', {}).get('model', {}).get('primary', 'unknown'))")"
    ;;
  *)
    echo "用法：$0 {gemini|qwen|status}"
    echo "  gemini - 切换到 Gemini 主模型"
    echo "  qwen   - 切换到 Qwen 主模型"
    echo "  status - 查看当前状态"
    ;;
esac
