#!/bin/bash
# API 密钥切换脚本

CONFIG_FILE="/Users/kelvin/.openclaw/workspace/api-keys.json"

echo "当前 API 密钥配置:"
echo "================"
python3 << 'PYEOF'
import json
with open("/Users/kelvin/.openclaw/workspace/api-keys.json") as f:
    d = json.load(f)
print(f"当前使用：{d['active']}")
print(f"Primary: {d['keys']['primary'][:20]}...")
backup = d['keys']['backup']
print(f"Backup:  {backup[:20]}..." if backup else "Backup:  (未设置)")
PYEOF
echo ""

case "$1" in
  primary)
    echo "切换到 Primary 密钥..."
    python3 -c "import json; d=json.load(open('$CONFIG_FILE')); d['active']='primary'; json.dump(d,open('$CONFIG_FILE','w'),indent=2)"
    echo "✅ 已切换到 Primary"
    ;;
  backup)
    echo "切换到 Backup 密钥..."
    python3 -c "import json; d=json.load(open('$CONFIG_FILE')); d['active']='backup'; json.dump(d,open('$CONFIG_FILE','w'),indent=2)"
    echo "✅ 已切换到 Backup"
    ;;
  set-backup)
    echo "设置 Backup 密钥 (请输入新密钥):"
    read -r NEW_KEY
    python3 -c "import json; d=json.load(open('$CONFIG_FILE')); d['keys']['backup']='$NEW_KEY'; json.dump(d,open('$CONFIG_FILE','w'),indent=2)"
    echo "✅ Backup 密钥已更新"
    ;;
  status)
    echo "查看当前状态"
    ;;
  *)
    echo "用法：$0 {primary|backup|set-backup|status}"
    echo ""
    echo "  primary     - 切换到主密钥"
    echo "  backup      - 切换到备用密钥"
    echo "  set-backup  - 设置新的备用密钥"
    echo "  status      - 查看当前状态"
    ;;
esac
