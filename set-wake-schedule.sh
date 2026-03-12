#!/bin/bash
# 设置 macOS 定时开机 - 工作日早上 8:30

echo "🔧 设置定时开机..."
echo "⏰ 时间：周一到周五 08:30"
echo ""

# 取消现有定时设置
sudo pmset repeat cancel

# 设置工作日 8:30 自动开机
sudo pmset repeat wake MTWRF 08:30:00

echo ""
echo "✅ 设置完成！"
echo ""
echo "查看当前设置："
sudo pmset -g sched

echo ""
echo "💡 提示："
echo "   - 取消定时开机：sudo pmset repeat cancel"
echo "   - 电脑需要插电才能自动开机"
echo "   - 首次设置后建议测试一次"
