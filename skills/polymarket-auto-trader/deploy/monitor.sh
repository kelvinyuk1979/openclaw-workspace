#!/bin/bash
# Polymarket Auto-Trader Monitor
# Run this to check system status, recent trades, and P&L

echo "=============================================="
echo "📊 Polymarket Auto-Trader Monitor"
echo "=============================================="
echo ""

# Check if running
if pgrep -f "run_trade.py" > /dev/null; then
    echo "✅ Status: Running"
else
    echo "⚠️  Status: Not currently running (cron-based)"
fi
echo ""

# Check cron
echo "📅 Cron Schedule:"
crontab -l 2>/dev/null | grep run_trade.py || echo "  No cron job found"
echo ""

# Recent trades
echo "📜 Recent Trades (last 5):"
if [ -f /opt/trader/app/trades.jsonl ]; then
    tail -5 /opt/trader/app/trades.jsonl | while read line; do
        echo "  $line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(f\"  {d.get('ts','')[:19]} | {d.get('side','')} {d.get('shares',0)}sh @ \${d.get('price',0):.2f} | {d.get('market','')[:40]}\")"
    done
else
    echo "  No trades yet"
fi
echo ""

# P&L
echo "💰 P&L Summary:"
if [ -f /opt/trader/app/pnl_tracker.py ]; then
    /opt/trader/bin/python3 /opt/trader/app/pnl_tracker.py
else
    echo "  P&L tracker not found"
fi
echo ""

# Recent logs
echo "📝 Recent Logs (last 20 lines):"
if [ -f /opt/trader/logs/cron.log ]; then
    tail -20 /opt/trader/logs/cron.log
else
    echo "  No logs found"
fi
echo ""

# Disk space
echo "💾 Disk Usage:"
df -h /opt/trader 2>/dev/null || df -h /
echo ""

echo "=============================================="
echo "Quick Commands:"
echo "  tail -f /opt/trader/logs/cron.log  # Watch live logs"
echo "  ./pnl_tracker.py                   # Check P&L"
echo "  systemctl status cron              # Check cron service"
echo "=============================================="
