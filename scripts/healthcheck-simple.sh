#!/bin/bash
# 简化版健康检查 - 只检查最关键的

LOGFILE=~/.openclaw/workspace/memory/healthcheck-$(date +%Y-%m-%d).log

echo "[$(date '+%H:%M:%S')] 健康检查" >> $LOGFILE

# 检查看板
if ! curl -s --max-time 5 http://localhost:5002/api/okx/status | grep -q "ok"; then
    echo "[$(date '+%H:%M:%S')] ❌ 看板异常，重启..." >> $LOGFILE
    cd ~/.openclaw/workspace/unified-trading-dashboard && ./manage.sh restart >> $LOGFILE 2>&1
    sleep 3
    if curl -s --max-time 5 http://localhost:5002/api/okx/status | grep -q "ok"; then
        echo "[$(date '+%H:%M:%S')] ✅ 看板已恢复" >> $LOGFILE
    else
        echo "[$(date '+%H:%M:%S')] ❌ 看板重启失败" >> $LOGFILE
    fi
else
    echo "[$(date '+%H:%M:%S')] ✅ 看板正常" >> $LOGFILE
fi

# 检查 OKX API
if curl -s --max-time 10 "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT" | grep -q '"code":"0"'; then
    echo "[$(date '+%H:%M:%S')] ✅ OKX API 正常" >> $LOGFILE
else
    echo "[$(date '+%H:%M:%S')] ⚠️ OKX API 超时（使用缓存）" >> $LOGFILE
fi

echo "" >> $LOGFILE
