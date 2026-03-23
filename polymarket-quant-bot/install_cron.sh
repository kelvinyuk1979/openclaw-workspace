#!/bin/bash
# Polymarket 量化机器人 - Cron 安装脚本

echo "🔧 正在配置 Cron 定时任务..."

# 获取项目路径
PROJECT_DIR="/Users/kelvin/.openclaw/workspace/polymarket-quant-bot"
PYTHON_BIN="/opt/homebrew/bin/python3"

# 创建日志目录
mkdir -p "$PROJECT_DIR/logs"

# 备份现有 Cron
crontab -l > "$PROJECT_DIR/crontab_backup_$(date +%Y%m%d_%H%M%S).txt" 2>/dev/null

# 创建新的 Cron 配置
CRON_FILE="$PROJECT_DIR/polymarket_cron.txt"

cat > "$CRON_FILE" << EOF
# Polymarket 量化机器人 - 定时任务
# 由 install_cron.sh 自动生成 - $(date +%Y-%m-%d %H:%M:%S)

# 每 15 分钟扫描一次市场
*/15 * * * * cd $PROJECT_DIR && $PYTHON_BIN scheduled_scan.py >> $PROJECT_DIR/logs/cron.log 2>&1

# 每天晚上 8 点生成详细报告
0 20 * * * cd $PROJECT_DIR && $PYTHON_BIN main.py >> $PROJECT_DIR/logs/daily.log 2>&1

# 每周日凌晨 2 点运行回测优化
0 2 * * 0 cd $PROJECT_DIR && $PYTHON_BIN backtest.py >> $PROJECT_DIR/logs/backtest.log 2>&1
EOF

# 安装 Cron
echo "📋 Cron 配置内容："
cat "$CRON_FILE"
echo ""

# 询问是否确认安装
read -p "确认安装 Cron 任务？(y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 合并现有 Cron 和新配置
    (crontab -l 2>/dev/null | grep -v "polymarket" ; cat "$CRON_FILE") | crontab -
    
    echo ""
    echo "✅ Cron 任务安装成功！"
    echo ""
    echo "📋 已配置的任务："
    echo "  ⏰ 每 15 分钟：市场扫描"
    echo "  🌙 每天 20:00：详细报告"
    echo "  📅 每周日 02:00：回测优化"
    echo ""
    echo "📝 查看日志："
    echo "  tail -f $PROJECT_DIR/logs/cron.log"
    echo ""
    echo "🔍 查看已安装的 Cron："
    echo "  crontab -l"
    echo ""
    echo "🗑️  卸载命令："
    echo "  crontab -l | grep -v polymarket | crontab -"
else
    echo "❌ 已取消安装"
fi
