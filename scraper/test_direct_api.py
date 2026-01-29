"""
直接测试飞书API（不使用封装类）
"""

import requests
import json


def test_direct_api():
    """直接测试飞书API"""
    print("=" * 60)
    print("直接测试飞书API")
    print("=" * 60)

    app_id = "cli_a9f1919786f85cb3"
    app_secret = "BcrZvWWswquglP6DBkLlccnuDtP3u1do"
    app_token = "Af9TwoIEkiJwkhkq0YEcw3WRnMZ"

    base_url = "https://open.feishu.cn/open-apis"

    try:
        # 1. 获取access_token
        print("\n1. 获取access_token...")
        url = f"{base_url}/auth/v3/app_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {
            "app_id": app_id,
            "app_secret": app_secret
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

        if result.get("code") != 0:
            print(f"   ❌ 获取access_token失败")
            return

        access_token = result["app_access_token"]
        print(f"   ✅ 成功获取access_token")

        # 2. 列出表格
        print("\n2. 列出表格...")
        url = f"{base_url}/bitable/v1/apps/{app_token}/tables"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        response = requests.get(url, headers=headers)
        result = response.json()

        print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

        if result.get("code") != 0:
            print(f"   ❌ 列出表格失败")
            print(f"   错误码: {result.get('code')}")
            print(f"   错误信息: {result.get('msg')}")
        else:
            print(f"   ✅ 成功列出表格")
            tables = result.get("data", {}).get("items", [])
            print(f"   找到 {len(tables)} 个表格")

            for i, table in enumerate(tables, 1):
                print(f"\n   {i}. {table.get('name')}")
                print(f"      ID: {table.get('table_id')}")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")


if __name__ == "__main__":
    test_direct_api()
