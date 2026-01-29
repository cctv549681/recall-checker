"""
查看表格字段结构
"""

import requests
import json


def get_table_fields():
    """查看表格字段"""
    print("=" * 60)
    print("查看表格字段结构")
    print("=" * 60)

    app_id = "cli_a9f1919786f85cb3"
    app_secret = "BcrZvWWswquglP6DBkLlccnuDtP3u1do"
    app_token = "AdcibdxG0atrMHsuIAzcz58jnng"
    table_id = "tblWSEVcPFLZkjxa"

    base_url = "https://open.feishu.cn/open-apis"

    try:
        # 获取access_token
        url = f"{base_url}/auth/v3/app_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {"app_id": app_id, "app_secret": app_secret}
        response = requests.post(url, headers=headers, json=data)
        access_token = response.json()["app_access_token"]

        print(f"\n1. 获取表格字段...")

        # 获取字段列表
        url = f"{base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        response = requests.get(url, headers=headers)
        result = response.json()

        if result.get("code") != 0:
            print(f"   ❌ 获取字段失败")
            print(f"   错误: {result.get('msg')}")
            return

        print(f"   ✅ 成功获取字段！")

        fields = result.get("data", {}).get("items", [])
        print(f"\n   当前共有 {len(fields)} 个字段:\n")

        for i, field in enumerate(fields, 1):
            print(f"   {i}. {field.get('field_name')}")
            print(f"      类型: {field.get('type')}")
            print(f"      ID: {field.get('field_id')}")
            if field.get('description'):
                print(f"      说明: {field.get('description')}")
            print()

        # 获取记录数
        print("2. 获取记录数...")
        url = f"{base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records?page_size=0"
        response = requests.get(url, headers=headers)
        result = response.json()

        if result.get("code") == 0:
            total = result.get("data", {}).get("total", 0)
            print(f"   ✅ 当前表格有 {total} 条记录")
        else:
            print(f"   ⚠️  无法获取记录数")

    except Exception as e:
        print(f"\n❌ 操作失败: {e}")


if __name__ == "__main__":
    get_table_fields()
