#!/bin/bash
# setup_env.sh - 环境配置脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "召回查询系统 - 环境配置"
echo "=========================================="

# 服务器配置
SERVER_USER="root"
SERVER_HOST="14.103.26.111"
PROJECT_DIR="/root/recall-checker"

echo -e "${BLUE}[1/6] 创建项目目录${NC}"

# 创建项目目录
ssh $SERVER_USER@$SERVER_HOST << 'ENDSSH'
mkdir -p $PROJECT_DIR
mkdir -p $PROJECT_DIR/logs
mkdir -p $PROJECT_DIR/data
ENDSSH

echo -e "\n${GREEN}✅ 目录创建完成${NC}\n"

echo -e "${BLUE}[2/6] 创建 Python 虚拟环境${NC}"

# 创建虚拟环境
ssh $SERVER_USER@$SERVER_HOST << 'ENDSSH'
cd $PROJECT_DIR
python3 -m venv venv
ENDSSH

echo -e "\n${GREEN}✅ 虚拟环境创建完成${NC}\n"

echo -e "${BLUE}[3/6] 激活虚拟环境${NC}"

# 激活虚拟环境（在后续脚本中使用）
echo -e "\n${YELLOW}提示：在运行其他脚本时，先运行以下命令激活虚拟环境：${NC}"
echo -e "  source $PROJECT_DIR/venv/bin/activate"
echo ""

echo -e "${BLUE}[4/6] 创建环境变量模板${NC}"

# 创建环境变量文件
ssh $SERVER_USER@$SERVER_HOST << 'ENDSSH'
cat > $PROJECT_DIR/scraper/.env << 'ENVEOF'
# ======================
# 飞书配置
# ======================
APP_ID=your_app_id_here
APP_SECRET=your_app_secret_here
APP_TOKEN=your_app_token_here
TABLE_ID=your_table_id_here

# ======================
# Flask 配置
# ======================
FLASK_APP=api_server.py
FLASK_ENV=production
FLASK_DEBUG=False

# ======================
# 服务器配置
# ======================
HOST=0.0.0.0
PORT=5001

# ======================
# 数据缓存配置
# ======================
CACHE_TTL=300  # 5分钟缓存

# ======================
# API 密钥（如果需要百度 OCR）
# ======================
# BAIDU_OCR_API_KEY=your_baidu_ocr_api_key_here
ENVEOF
ENDSSH

echo -e "\n${GREEN}✅ 环境变量模板创建完成${NC}\n"

echo -e "${BLUE}[5/6] 设置权限${NC}"

# 设置权限
ssh $SERVER_USER@$SERVER_HOST << 'ENDSSH'
chmod +x $PROJECT_DIR/scraper/*.sh
chmod 600 $PROJECT_DIR/scraper/.env
chmod 700 $PROJECT_DIR/logs
ENDSSH

echo -e "\n${GREEN}✅ 权限设置完成${NC}\n"

echo -e "${BLUE}[6/6] 创建启动脚本${NC}"

# 创建总启动脚本
ssh $SERVER_USER@$SERVER_HOST << 'ENDSSH'
cat > $PROJECT_DIR/start.sh << 'STARTEOF'
#!/bin/bash

set -e

PROJECT_DIR="/root/recall-checker"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON="$VENV_DIR/bin/python"
SCRAPER_DIR="$PROJECT_DIR/scraper"
LOG_DIR="$PROJECT_DIR/logs"

echo "=========================================="
echo "召回查询系统 - 启动"
echo "=========================================="

# 激活虚拟环境
echo "激活虚拟环境..."
source $VENV_DIR/bin/activate

# 切换到爬虫目录
cd $SCRAPER_DIR

# 安装依赖
echo "安装 Python 依赖..."
pip install -r requirements.txt

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "警告: .env 文件不存在，使用默认配置"
else
    echo "加载环境变量..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# 启动 API 服务
echo "启动 API 服务..."
cd $SCRAPER_DIR

# 检查端口占用
if lsof -Pi :5001 -sTCP:LISTEN -tPID | grep -q python3; then
    echo "警告: 端口 5001 已被占用，尝试停止..."
    pkill -f api_server.py
    sleep 2
fi

# 后台启动
nohup $PYTHON api_server.py > $LOG_DIR/api_server.log 2>&1 &
API_PID=$!

# 保存 PID
echo $API_PID > $PROJECT_DIR/api_server.pid

# 等待启动
sleep 3

# 检查服务状态
if ps -p $API_PID > /dev/null; then
    echo "✅ API 服务启动成功"
    echo "   PID: $API_PID"
    echo "   端口: 5001"
    echo "   日志: $LOG_DIR/api_server.log"
    echo ""
    echo "API 接口:"
    echo "   健康检查: http://14.103.26.111:5001/api/health"
    echo "   批次号查询: http://14.103.26.111:5001/api/query"
    echo "   数据统计: http://14.103.26.111:5001/api/stats"
else
    echo "❌ API 服务启动失败"
    echo "   请查看日志: $LOG_DIR/api_server.log"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 服务启动完成"
echo "=========================================="
STARTEOF

chmod +x $PROJECT_DIR/start.sh
ENDSSH

echo -e "\n${GREEN}✅ 启动脚本创建完成${NC}\n"

echo "=========================================="
echo "✅ 环境配置完成"
echo "=========================================="
echo ""
echo "配置文件:"
echo "  环境变量: $PROJECT_DIR/scraper/.env"
echo "  启动脚本: $PROJECT_DIR/start.sh"
echo ""
echo "下一步:"
echo "  1. 配置飞书凭证"
echo "     ssh $SERVER_USER@$SERVER_HOST"
echo "     nano $PROJECT_DIR/scraper/.env"
echo ""
echo "  2. 启动服务"
echo "     ssh $SERVER_USER@$SERVER_HOST"
echo "     cd $PROJECT_DIR"
echo "     bash start.sh"
echo ""
echo "命令: bash setup_env.sh"
