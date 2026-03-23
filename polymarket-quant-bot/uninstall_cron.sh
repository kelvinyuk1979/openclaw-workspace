#!/bin/bash
# Polymarket 量化机器人 - Cron 卸载脚本

echo "🗑️  正在卸载 Cron 定时任务..."

# 备份现有 Cron
crontab -l > polymarket_cron_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null

# 移除所有 polymarket 相关任务
crontab -l | grep -v "polymarket" | crontab -

echo ""
echo "✅ Cron 任务已卸载！"
echo ""
echo "📋 剩余的 Cron 任务："
crontab -l

echo ""
echo "💾 备份已保存：polymarket_cron_backup_*.txt"
