#!/bin/bash
# Polymarket 天气交易机器人 - 一周模拟运行脚本
# 每天运行一次，连续运行 7 天，生成汇总报告

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "📅 Polymarket 天气机器人 - 7 天模拟测试"
echo "========================================"
echo ""

# 重置模拟账户
echo "🔄 重置模拟账户..."
python3 bot_v1.py --reset

# 创建日志目录
mkdir -p logs

# 运行 7 次模拟（模拟 7 天）
for day in {1..7}; do
    echo ""
    echo "========================================"
    echo "第 $day 天模拟运行"
    echo "========================================"
    
    # 运行机器人（观察模式）
    python3 bot_v1.py --quiet >> logs/day_$day.log 2>&1
    
    # 生成每日报告
    python3 bot_v1.py --report >> logs/day_$day.log 2>&1
    
    echo "✅ 第 $day 天完成"
done

echo ""
echo "========================================"
echo "📊 生成最终汇总报告"
echo "========================================"

python3 bot_v1.py --report

echo ""
echo "✅ 7 天模拟测试完成！"
echo "📄 日志文件：logs/"
echo "📄 模拟数据：simulation.json"
