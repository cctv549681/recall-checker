#!/bin/bash
# run-tests.sh - 运行所有单元测试

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Recall Checker - 单元测试${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 Jest 是否安装
if ! command -v npm &> /dev/null; then
    echo -e "${RED}错误: npm 未安装${NC}"
    exit 1
fi

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}node_modules 不存在，正在安装依赖...${NC}"
    npm install
fi

# 运行测试
echo -e "${GREEN}开始运行测试...${NC}"
echo ""

npm test

# 检查测试结果
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 所有测试通过！${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ 测试失败${NC}"
    exit 1
fi
