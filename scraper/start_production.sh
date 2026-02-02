#!/bin/bash
# 生产环境启动脚本 - 使用Gunicorn

# 安装Gunicorn（如果未安装）
if ! command -v gunicorn &> /dev/null; then
    pip3 install gunicorn --break-system-packages
fi

# 配置
APP_DIR="/root/clawd/recall-checker/scraper"
APP_MODULE="api_server:app"
PORT=5001
WORKERS=4  # 工作进程数

# 日志目录
LOG_DIR="$APP_DIR/logs"
mkdir -p "$LOG_DIR"

# 启动Gunicorn
cd "$APP_DIR"

echo "启动API服务器（Gunicorn）..."
echo "端口: $PORT"
echo "工作进程数: $WORKERS"
echo "日志目录: $LOG_DIR"

nohup gunicorn \
    --bind "0.0.0.0:$PORT" \
    --workers "$WORKERS" \
    --worker-class sync \
    --timeout 120 \
    --access-logfile "$LOG_DIR/access.log" \
    --error-logfile "$LOG_DIR/error.log" \
    --log-level info \
    "$APP_MODULE" \
    > "$LOG_DIR/gunicorn.log" 2>&1 &

# 保存进程ID
echo $! > "$LOG_DIR/gunicorn.pid"

echo "✅ API服务器已启动（PID: $(cat $LOG_DIR/gunicorn.pid)）"
echo "📊 查看日志: tail -f $LOG_DIR/gunicorn.log"
echo "🛑 停止服务: kill $(cat $LOG_DIR/gunicorn.pid)"
