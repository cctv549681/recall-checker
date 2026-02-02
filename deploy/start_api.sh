#!/bin/bash
# start_api.sh - API 服务启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "召回查询系统 - API 服务启动"
echo "=========================================="

# 配置
PROJECT_DIR="/root/recall-checker"
API_DIR="$PROJECT_DIR/scraper"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$PROJECT_DIR/api_server.pid"

# Python 路径
PYTHON=/usr/bin/python3
PIP=/usr/bin/pip3

echo -e "${BLUE}[1/5] 检查 Python 环境${NC}"

# 检查 Python
if ! command -v $PYTHON &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 未安装${NC}"
    echo -e "执行命令: apt install python3"
    exit 1
fi

echo -e "  Python 版本: $($PYTHON --version)"

echo -e "\n${BLUE}[2/5] 检查项目目录${NC}"

# 检查项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠️  项目目录不存在: $PROJECT_DIR${NC}"
    echo -e "执行命令: mkdir -p $PROJECT_DIR"
    exit 1
fi

echo -e "  ✅ 项目目录存在: $PROJECT_DIR"

echo -e "\n${BLUE}[3/5] 安装 Python 依赖${NC}"

# 安装依赖
if [ -f "$API_DIR/requirements.txt" ]; then
    $PIP install -r $API_DIR/requirements.txt
    echo -e "  ✅ 依赖安装完成"
else
    echo -e "${YELLOW}⚠️  依赖文件不存在${NC}"
fi

echo -e "\n${BLUE}[4/5] 创建日志目录${NC}"

# 创建日志目录
mkdir -p $LOG_DIR

echo -e "  ✅ 日志目录创建完成: $LOG_DIR"

echo -e "\n${BLUE}[5/5] 停止旧服务（如果有）${NC}"

# 停止旧服务
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat $PID_FILE)
    if ps -p $OLD_PID > /dev/null; then
        echo "  停止旧服务 (PID: $OLD_PID)"
        kill $OLD_PID
        sleep 2
    fi
fi

echo -e "\n${BLUE}[6/5] 启动 API 服务${NC}"

# 启动服务
cd $API_DIR

# 使用 nohup 后台运行
nohup $PYTHON api_server.py > $LOG_DIR/api_server.log 2>&1 &
API_PID=$!

# 保存 PID
echo $API_PID > $PID_FILE

# 等待启动
sleep 3

# 检查服务是否启动
if ps -p $API_PID > /dev/null; then
    echo -e "  ✅ API 服务启动成功"
    echo -e "  PID: $API_PID"
    echo -e "  日志文件: $LOG_DIR/api_server.log"
    echo -e "  健康检查: http://14.103.26.111/api/health"
    echo -e "  查询接口: http://14.103.26.111/api/query"
    echo -e "  统计接口: http://14.103.26.111/api/stats"
else
    echo -e "${YELLOW}⚠️  API 服务启动失败${NC}"
    echo -e "  请查看日志: $LOG_DIR/api_server.log"
    exit 1
fi

echo -e "\n${GREEN}✅ API 服务启动完成！${NC}"
echo "=========================================="
echo ""
echo "管理命令:"
echo "  查看日志: tail -f $LOG_DIR/api_server.log"
echo "  停止服务: kill $API_PID"
echo "  查看状态: ps aux | grep api_server"
echo "  测试服务: curl http://14.103.26.111/api/health"
echo ""
echo "命令: bash start_api.sh"
