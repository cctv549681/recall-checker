"""
测试读取飞书已有表格信息
"""

import sys
from pathlib import Path

# 添加scraper目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.feishu_client import FeishuClient


def test_list_tables():
    """测试列出已有表格"""
    print("=" * 60)
    print("测试列出飞书已有表格")
    print("=" * 60)

    # 飞书凭证
    app_id = "cli_a9f1919786f85cb3"
    app_secret = "BcrZvWWswquglP6DBkLlccnuDtP3u1do"

    # app_token从URL解析
    app_token = "Af9TwoIEkiJwkhkq0YEcw3WRnMZ"

    client = FeishuClient(app_id, app_secret)

    try:
        print("\n尝试获取表格列表...")

        # 列出所有表格
        result = client._make_request(
            "GET",
            f"/bitable/v1/apps/{app_token}/tables",
            None,
            app_token
        )

        print(f"\n✅ 成功获取表格列表！")
        print(f"\n找到 {len(result.get('items', []))} 个表格:\n")

        for i, table in enumerate(result.get('items', []), 1):
            print(f"{i}. {table.get('name', '未命名')} (ID: {table.get('table_id')})")

        return result.get('items', [])

    except Exception as e:
        print(f"\n❌ 读取失败: {e}")
        print("\n可能原因:")
        print("1. 应用需要 bitable:app:readonly 权限")
        print("2. app_token不正确")
        print("3. 应用未发布或权限未生效")

        return []


if __name__ == "__main__":
    tables = test_list_tables()

    if tables:
        print("\n✅ 可以读取已有表格！")
        print("\n下一步:")
        print("- 在已有表格中手动添加字段")
        print("- 或者删除所有表格，重新尝试创建")
    else:
        print("\n⚠️  无法读取表格，可能需要调整权限")
