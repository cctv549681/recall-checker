#!/bin/bash
# generate-coverage-report.sh - 生成测试覆盖率报告

echo "生成测试覆盖率报告..."

cd /root/clawd/recall-checker/miniprogram

# 运行测试并生成覆盖率报告
npm test -- --coverage

# 检查覆盖率报告是否生成
if [ -d "coverage" ]; then
    echo ""
    echo "✅ 覆盖率报告已生成！"
    echo ""
    echo "查看报告："
    echo "  - HTML: file://$(pwd)/coverage/lcov-report/index.html"
    echo "  - LCOV: file://$(pwd)/coverage/lcov.info"
    echo ""
else
    echo ""
    echo "❌ 覆盖率报告生成失败"
    exit 1
fi
