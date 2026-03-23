#!/bin/bash
# 统一交易系统看板 - 启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/web_server.pid"
LOG_FILE="$SCRIPT_DIR/web_server.log"

# 清理函数：杀掉占用端口的进程
cleanup_port() {
    # 查找并杀掉占用 5002 端口的 python 进程
    for pid in $(ps aux | grep -i "python.*web_server" | grep -v grep | awk '{print $2}'); do
        echo "清理旧进程：$pid"
        kill -9 $pid 2>/dev/null
    done
    rm -f "$PID_FILE"
}

# 检查是否已在运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "看板已在运行 (PID: $PID)"
        exit 0
    else
        echo "清理旧的 PID 文件"
        rm -f "$PID_FILE"
    fi
fi

# 先清理可能占用端口的旧进程
cleanup_port
sleep 1

# 启动 Web 服务器
echo "启动统一交易系统看板..."
cd "$SCRIPT_DIR"
nohup python3 web_server.py > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

sleep 2

if ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
    echo "✅ 看板已启动 (PID: $(cat $PID_FILE))"
    echo "📍 访问地址：http://localhost:5002"
else
    echo "❌ 启动失败，查看日志：$LOG_FILE"
    cat "$LOG_FILE"
    exit 1
fi
