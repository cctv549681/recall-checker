#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书API测试工具
整合所有飞书API测试功能
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.feishu_config import APP_ID, APP_SECRET, APP_TOKEN
from utils.feishu_client import FeishuClient


def test_connection():
    """测试API连接"""
    print("=" * 60)
    print("1. 测试API连接")
    print("=" * 60)

    client = FeishuClient(APP_ID, APP_SECRET, APP_TOKEN)

    try:
        token = client.get_access_token()
        print(f"✅ 获取token成功: {token[:20]}...")
        return True
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False


def list_tables():
    """列出所有表格"""
    print("\n" + "=" * 60)
    print("2. 列出所有表格")
    print("=" * 60)

    client = FeishuClient(APP_ID, APP_SECRET, APP_TOKEN)

    try:
        tables = client._make_request(
            "GET",
            f"/bitable/v1/apps/{APP_TOKEN}/tables",
            app_token=APP_TOKEN
        )

        items = tables.get("items", [])
        print(f"\n共 {len(items)} 个表格:\n")

        for i, table in enumerate(items, 1):
            print(f"{i}. {table.get('name')}")
            print(f"   ID: {table.get('table_id')}")

        return {t["name"]: t["table_id"] for t in items}

    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return {}


def list_fields(table_id, table_name=""):
    """列出表格字段"""
    if not table_id:
        print("❌ 需要提供表格ID")
        return

    print("\n" + "=" * 60)
    print(f"3. 列出字段: {table_name}")
    print("=" * 60)

    client = FeishuClient(APP_ID, APP_SECRET, APP_TOKEN)

    try:
        fields = client._make_request(
            "GET",
            f"/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/fields",
            app_token=APP_TOKEN
        )

        items = fields.get("items", [])
        print(f"\n共 {len(items)} 个字段:\n")

        for i, field in enumerate(items, 1):
            print(f"{i}. {field.get('field_name')}")
            print(f"   ID: {field.get('field_id')}")
            print(f"   类型: {field.get('type')}")

    except Exception as e:
        print(f"❌ 查询失败: {e}")


def list_records(table_id, table_name="", limit=5):
    """列出记录"""
    if not table_id:
        print("❌ 需要提供表格ID")
        return

    print("\n" + "=" * 60)
    print(f"4. 列出记录: {table_name} (最多{limit}条)")
    print("=" * 60)

    client = FeishuClient(APP_ID, APP_SECRET, APP_TOKEN)

    try:
        result = client._make_request(
            "GET",
            f"/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/records",
            {"page_size": limit},
            app_token=APP_TOKEN
        )

        records = result.get("items", [])
        print(f"\n共 {len(records)} 条记录:\n")

        for i, record in enumerate(records, 1):
            print(f"记录 {i} (ID: {record.get('record_id')}):")
            fields = record.get("fields", {})
            for key, value in fields.items():
                print(f"  {key}: {value}")
            print()

    except Exception as e:
        print(f"❌ 查询失败: {e}")


def insert_record(table_id, data):
    """插入记录"""
    if not table_id:
        print("❌ 需要提供表格ID")
        return

    print("\n" + "=" * 60)
    print("5. 插入记录")
    print("=" * 60)
    print(f"数据: {data}")

    client = FeishuClient(APP_ID, APP_SECRET, APP_TOKEN, table_ids={"test": table_id})

    try:
        record_id = client.create_record("test", data)
        print(f"\n✅ 插入成功!")
        print(f"   Record ID: {record_id}")
        return record_id

    except Exception as e:
        print(f"\n❌ 插入失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主菜单"""
    print("\n" + "=" * 60)
    print("飞书API测试工具")
    print("=" * 60)

    # 1. 测试连接
    if not test_connection():
        return

    # 2. 列出表格
    tables = list_tables()
    if not tables:
        return

    # 选择表格
    table_names = list(tables.keys())
    print("\n选择表格 (输入序号):")
    for i, name in enumerate(table_names, 1):
        print(f"  {i}. {name}")

    choice = input("\n请选择 (或回车跳过): ").strip()
    if choice and choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(table_names):
            table_name = table_names[idx]
            table_id = tables[table_name]

            # 3. 列出字段
            list_fields(table_id, table_name)

            # 4. 列出记录
            list_records(table_id, table_name, limit=3)

            # 5. 可选：插入记录
            insert_choice = input("\n是否插入测试记录? (y/n): ").strip().lower()
            if insert_choice == 'y':
                # 获取第一个字段名
                client = FeishuClient(APP_ID, APP_SECRET, APP_TOKEN)
                fields = client._make_request(
                    "GET",
                    f"/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/fields",
                    app_token=APP_TOKEN
                )
                first_field = fields.get("items", [{}])[0].get("field_name", "字段")

                test_data = {first_field: f"测试记录 {__import__('time').time()}"}
                insert_record(table_id, test_data)


if __name__ == "__main__":
    main()
