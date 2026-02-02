#!/bin/bash
# upload_code.sh - 代码上传脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "召回查询系统 - 代码上传"
echo "=========================================="

# 服务器配置
SERVER_USER="root"
SERVER_HOST="14.103.26.111"
LOCAL_PROJECT_DIR="/root/clawd/recall-checker"
REMOTE_PROJECT_DIR="/root/recall-checker"

# 文件列表（排除）
EXCLUDE_FILES=(
    ".git"
    "__pycache__"
    "*.pyc"
    ".DS_Store"
    "node_modules"
    ".vscode"
    "*.log"
    "*.tmp"
    "venv"
    "env"
    ".env.local"
)

echo -e "${BLUE}[1/5] 打包项目文件${NC}"
echo "执行命令: cd $LOCAL_PROJECT_DIR && tar -czvf /tmp/recall-checker.tar.gz --exclude-vcs"

cd $LOCAL_PROJECT_DIR

# 打包项目
tar -czvf /tmp/recall-checker.tar.gz --exclude-vcs \
    --exclude=.git \
    --exclude=__pycache__ \
    --exclude='*.pyc' \
    --exclude=.DS_Store \
    --exclude=node_modules \
    --exclude=.vscode \
    --exclude='*.log' \
    --exclude='*.tmp' \
    --exclude=venv \
    --exclude=.env \
    --exclude=.env.local \
    .

echo -e "\n${GREEN}✅ 项目打包完成${NC}\n"

echo -e "${BLUE}[2/5] 上传到服务器${NC}"
echo "执行命令: scp /tmp/recall-checker.tar.gz $SERVER_USER@$SERVER_HOST:/tmp/"

# 上传到服务器
scp /tmp/recall-checker.tar.gz $SERVER_USER@$SERVER_HOST:/tmp/

echo -e "\n${GREEN}✅ 代码上传完成${NC}\n"

echo -e "${BLUE}[3/5] 在服务器上解压${NC}"
echo "执行命令: ssh $SERVER_USER@$SERVER_HOST 'cd /tmp && tar -xzf /tmp/recall-checker.tar.gz -C /root && mv /tmp/recall-checker /root/recall-checker'"

# 在服务器上解压
ssh $SERVER_USER@$SERVER_HOST << 'ENDSSH'
cd /tmp
tar -xzf /tmp/recall-checker.tar.gz -C /root
rm -rf /root/recall-checker
mv /tmp/recall-checker /root/recall-checker
ENDSSH

echo -e "\n${GREEN}✅ 代码解压完成${NC}\n"

echo -e "${BLUE}[4/5] 安装 Python 依赖${NC}"
echo "执行命令: ssh $SERVER_USER@$SERVER_HOST 'cd /root/recall-checker/scraper && pip3 install -r requirements.txt'"

# 安装依赖
ssh $SERVER_USER@$SERVER_HOST 'cd /root/recall-checker/scraper && pip3 install -r requirements.txt'

echo -e "\n${GREEN}✅ 依赖安装完成${NC}\n"

echo -e "${BLUE}[5/5] 配置环境变量${NC}"
echo "执行命令: ssh $SERVER_USER@$SERVER_HOST 'cat > /root/recall-checker/scraper/.env'"

# 配置环境变量
ssh $SERVER_USER@$SERVER_HOST << 'ENDSSH'
cat > /root/recall-checker/scraper/.env << 'ENVFILE'
# 飞书配置（需要从本地复制）
# APP_ID=your_app_id
# APP_SECRET=your_app_secret
# APP_TOKEN=your_app_token
# TABLE_ID=your_table_id

# Python 环境
PYTHONPATH=/root/recall-checker/scraper:/root/.local/lib/python3.9/site-packages
FLASK_APP=api_server.py
FLASK_ENV=production
ENVFILE
ENDSSH

echo -e "\n${YELLOW}⚠️  请手动配置 .env 文件${NC}"
echo -e "${YELLOW}⚠️  将本地的飞书配置复制到服务器${NC}\n"

echo "=========================================="
echo -e "${GREEN}✅ 代码部署完成！${NC}"
echo "=========================================="
echo ""
echo "服务器信息:"
echo "  项目目录: $REMOTE_PROJECT_DIR"
echo "  文件已上传: /root/recall-checker"
echo "  依赖已安装: Python 3 + Flask"
echo ""
echo "下一步:"
echo "  1. 手动配置 .env 文件"
echo "     ssh $SERVER_USER@$SERVER_HOST"
echo "     nano /root/recall-checker/scraper/.env"
echo ""
echo "  2. 测试 API 服务"
echo "     ssh $SERVER_USER@$SERVER_HOST"
echo "     cd /root/recall-checker/scraper"
echo "     python3 api_server.py"
echo ""
echo "  3. 配置 Nginx 反向代理"
echo "     ssh $SERVER_USER@$SERVER_HOST"
echo "     bash /root/recall-checker/deploy/setup_server.sh"
echo ""
echo "  4. 启动 API 服务"
echo "     ssh $SERVER_USER@$SERVER_HOST"
echo "     bash /root/recall-checker/deploy/start_api.sh"
echo ""
echo "命令: bash upload_code.sh"
