"""
测试飞书API连接
"""

import sys
from pathlib import Path

# 添加scraper目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.feishu_client import FeishuClient


def test_feishu_connection():
    """测试飞书API连接"""
    print("=" * 60)
    print("测试飞书API连接")
    print("=" * 60)

    # 使用提供的凭证
    app_id = "cli_a9f1919786f85cb3"
    app_secret = "BcrZvWWswquglP6DBkLlccnuDtP3u1do"

    client = FeishuClient(app_id, app_secret)

    try:
        print("\n1. 测试获取access_token...")
        token = client.get_access_token()
        print(f"   ✅ 成功获取access_token")
        print(f"   Token: {token[:30]}...")

        print("\n2. API连接测试通过！")
        print(f"   App ID: {app_id}")
        print(f"   Token过期时间: {client._token_expire_at}")

        print("\n" + "=" * 60)
        print("✅ 飞书API连接成功！")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("\n请检查:")
        print("1. App ID和App Secret是否正确")
        print("2. 网络连接是否正常")
        print("3. 飞书应用权限是否已配置")

        return False


if __name__ == "__main__":
    success = test_feishu_connection()

    if success:
        print("\n下一步: 创建数据表结构")
    else:
        print("\n请解决问题后重试")
