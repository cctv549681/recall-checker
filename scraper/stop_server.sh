#!/bin/bash
# 停止API服务器

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"

# 停止Flask开发服务器
if [ -f "$SCRIPT_DIR/flask.pid" ]; then
    PID=$(cat "$SCRIPT_DIR/flask.pid")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "停止Flask服务器（PID: $PID）..."
        kill "$PID"
        rm "$SCRIPT_DIR/flask.pid"
        echo "✅ Flask服务器已停止"
    else
        echo "⚠️  Flask服务器未运行（PID: $PID）"
        rm "$SCRIPT_DIR/flask.pid"
    fi
fi

# 停止Gunicorn服务器
if [ -f "$LOG_DIR/gunicorn.pid" ]; then
    PID=$(cat "$LOG_DIR/gunicorn.pid")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "停止Gunicorn服务器（PID: $PID）..."
        kill "$PID"
        rm "$LOG_DIR/gunicorn.pid"
        echo "✅ Gunicorn服务器已停止"
    else
        echo "⚠️  Gunicorn服务器未运行（PID: $PID）"
        rm "$LOG_DIR/gunicorn.pid"
    fi
fi

# 额外清理：kill所有相关进程
echo "清理残留进程..."
pkill -f "python3.*api_server" 2>/dev/null
pkill -f "gunicorn.*api_server" 2>/dev/null

echo "✅ 清理完成"
