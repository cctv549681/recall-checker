#!/bin/bash
# 快速启动脚本 - 召回数据爬虫

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 需要安装 Python 3"
    exit 1
fi

# 进入脚本目录
cd "$(dirname "$0")"

# 显示菜单
echo "======================================================================"
echo "召回数据爬虫 - 快速启动"
echo "======================================================================"
echo ""
echo "请选择操作:"
echo "1. 查看所有数据源"
echo "2. 抓取爱他美召回数据"
echo "3. 抓取飞鹤召回数据"
echo "4. 抓取美素佳儿召回数据"
echo "5. 抓取 a2至初召回数据"
echo "6. 抓取金领冠召回数据"
echo "7. 抓取所有品牌召回数据"
echo "8. 测试所有爬虫"
echo "9. 退出"
echo ""
read -p "请输入选项 (1-9): " choice

case $choice in
    1)
        python3 run_scrapers.py --sources
        ;;
    2)
        python3 run_scrapers.py --brand aptamil
        ;;
    3)
        python3 run_scrapers.py --brand feihe
        ;;
    4)
        python3 run_scrapers.py --brand friso
        ;;
    5)
        python3 run_scrapers.py --brand a2
        ;;
    6)
        python3 run_scrapers.py --brand jinlingguan
        ;;
    7)
        python3 run_scrapers.py --all --save
        ;;
    8)
        python3 test_scrapers.py --all
        ;;
    9)
        echo "退出"
        exit 0
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "✅ 操作完成"
