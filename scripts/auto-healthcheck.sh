#!/bin/bash
# OpenClaw 自动健康检查脚本
# 每 30 分钟自动运行，检查关键服务状态

WORKSPACE=~/.openclaw/workspace
LOGFILE=$WORKSPACE/memory/healthcheck-$(date +%Y-%m-%d).log

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOGFILE
}

log "=== 健康检查开始 ==="

# 1. 检查看板服务
if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:5002/ | grep -q "200"; then
    log "❌ 看板服务异常，尝试重启..."
    cd $WORKSPACE/unified-trading-dashboard && ./manage.sh restart >> $LOGFILE 2>&1
    sleep 3
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5002/ | grep -q "200"; then
        log "✅ 看板服务已恢复"
    else
        log "❌ 看板服务重启失败，需要人工干预"
    fi
else
    log "✅ 看板服务正常"
fi

# 2. 检查 Gateway
if ! openclaw gateway status 2>&1 | grep -q "running"; then
    log "❌ Gateway 异常，尝试重启..."
    openclaw gateway restart >> $LOGFILE 2>&1
    sleep 3
    if openclaw gateway status 2>&1 | grep -q "running"; then
        log "✅ Gateway 已恢复"
    else
        log "❌ Gateway 重启失败，需要人工干预"
    fi
else
    log "✅ Gateway 正常"
fi

# 3. 检查 OKX API
if ! curl -s --max-time 10 "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT" | grep -q "code\":\"0"; then
    log "⚠️ OKX API 连接不稳定"
else
    log "✅ OKX API 正常"
fi

# 4. 检查定时任务
TASK_COUNT=$(openclaw cron list 2>/dev/null | grep -c "量化交易\|交易日报\|交易复盘")
if [ "$TASK_COUNT" -lt 3 ]; then
    log "❌ 定时任务数量异常（当前：$TASK_COUNT，预期：≥3）"
else
    log "✅ 定时任务正常（$TASK_COUNT 个）"
fi

log "=== 健康检查完成 ==="
log ""
