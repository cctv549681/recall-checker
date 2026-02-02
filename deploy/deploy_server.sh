#!/bin/bash
# deploy.sh - 服务器部署脚本
# 目标服务器: Ubuntu 24.04 @ 14.103.26.111

set -e

echo "=========================================="
echo "召回查询系统 - 服务器部署"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 服务器配置
SERVER_USER="root"
SERVER_HOST="14.103.26.111"
PROJECT_DIR="/root/recall-checker"
API_PORT=5001

echo -e "${BLUE}[1/6] 更新系统${NC}"
echo "执行命令: apt update && apt upgrade -y"

# 更新系统
apt update && apt upgrade -y

echo -e "\n${GREEN}✅ 系统更新完成${NC}\n"

echo -e "${BLUE}[2/6] 安装 Python 3 和依赖${NC}"
echo "执行命令: apt install python3 python3-pip python3-venv git nginx -y"

# 安装 Python 和依赖
apt install python3 python3-pip python3-venv git nginx -y

echo -e "\n${GREEN}✅ Python 和依赖安装完成${NC}\n"

echo -e "${BLUE}[3/6] 创建项目目录${NC}"
echo "执行命令: mkdir -p $PROJECT_DIR"

# 创建项目目录
mkdir -p $PROJECT_DIR

echo -e "\n${GREEN}✅ 项目目录创建完成: $PROJECT_DIR${NC}\n"

echo -e "${BLUE}[4/6] 配置 Nginx 反向代理${NC}"

# 创建 Nginx 配置
cat > /etc/nginx/sites-available/recall-checker << 'EOF'
server {
    listen 80;
    server_name 14.103.26.111;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:5001/api/health;
        proxy_set_header Host $host;
    }

    location /api {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
    }
}
EOF

# 启用配置
ln -sf /etc/nginx/sites-available/recall-checker /etc/nginx/sites-enabled/

# 删除默认配置
rm -f /etc/nginx/sites-enabled/default

# 测试配置
nginx -t

# 重启 Nginx
systemctl restart nginx

echo -e "\n${GREEN}✅ Nginx 配置完成${NC}\n"

echo -e "${BLUE}[5/6] 配置防火墙${NC}"

# 允许 HTTP 端口
ufw allow 80/tcp
ufw allow 5001/tcp

echo -e "\n${GREEN}✅ 防火墙配置完成${NC}\n"

echo -e "${BLUE}[6/6] 配置系统服务${NC}"

# 启用 Nginx
systemctl enable nginx

echo -e "\n${GREEN}✅ 系统服务配置完成${NC}\n"

echo "=========================================="
echo -e "${GREEN}✅ 服务器部署完成！${NC}"
echo "=========================================="
echo ""
echo "服务器信息:"
echo "  系统: Ubuntu 24.04"
echo "  IP: 14.103.26.111"
echo "  项目目录: $PROJECT_DIR"
echo "  API 端口: $API_PORT"
echo ""
echo "下一步:"
echo "  1. 上传代码到服务器"
echo "  2. 配置环境变量"
echo "  3. 安装 Python 依赖"
echo "  4. 启动 API 服务"
echo ""
echo "命令: bash deploy.sh"
