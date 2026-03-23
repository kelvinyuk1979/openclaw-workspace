#!/bin/bash
# 统一交易系统看板 - 管理脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/web_server.pid"
PLIST_FILE="$HOME/Library/LaunchAgents/com.openclaw.trading-dashboard.plist"

case "$1" in
    start)
        echo "🚀 启动看板..."
        if [ -f "$PID_FILE" ] && ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
            echo "✅ 看板已在运行"
        else
            "$SCRIPT_DIR/start_dashboard.sh"
        fi
        ;;
    
    stop)
        echo "🛑 停止看板..."
        if [ -f "$PID_FILE" ]; then
            kill $(cat "$PID_FILE") 2>/dev/null
            rm -f "$PID_FILE"
            echo "✅ 看板已停止"
        else
            echo "⚠️  看板未在运行"
        fi
        ;;
    
    restart)
        echo "🔄 重启看板..."
        $0 stop
        sleep 1
        $0 start
        ;;
    
    status)
        if [ -f "$PID_FILE" ] && ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
            echo "✅ 看板运行中 (PID: $(cat $PID_FILE))"
            echo "📍 访问地址：http://localhost:5002"
        else
            echo "❌ 看板未运行"
        fi
        ;;
    
    enable-auto)
        echo "⚙️  启用开机自启动..."
        if [ -f "$PLIST_FILE" ]; then
            launchctl load "$PLIST_FILE" 2>/dev/null
            echo "✅ 已启用开机自启动"
        else
            echo "❌ 未找到配置文件"
        fi
        ;;
    
    disable-auto)
        echo "⚙️  禁用开机自启动..."
        launchctl unload "$PLIST_FILE" 2>/dev/null
        echo "✅ 已禁用开机自启动"
        ;;
    
    *)
        echo "用法：$0 {start|stop|restart|status|enable-auto|disable-auto}"
        echo ""
        echo "命令说明:"
        echo "  start        - 启动看板"
        echo "  stop         - 停止看板"
        echo "  restart      - 重启看板"
        echo "  status       - 查看状态"
        echo "  enable-auto  - 启用开机自启动"
        echo "  disable-auto - 禁用开机自启动"
        exit 1
        ;;
esac
