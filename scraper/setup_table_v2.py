#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建字段并测试数据写入（修复版 - 不带 description）
"""
import requests
import json
from datetime import datetime

# 飞书凭证
APP_ID = "cli_a9f1f4887e38dcd2"
APP_SECRET = "aNhAQdFTDJSWaQZnj2dy7dXvDgOzdi7u"
APP_TOKEN = "R7cwbZ2Iaa4v0vs0Fh1cc5KUnEg"
TABLE_ID = "tblA1YqzSi4aaxeI"

BASE_URL = "https://open.feishu.cn/open-apis"


def get_tenant_token():
    """获取tenant_access_token"""
    url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    data = {"app_id": APP_ID, "app_secret": APP_SECRET}

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if result.get("code") != 0:
        raise Exception(f"获取tenant_access_token失败: {result}")

    return result["tenant_access_token"]


def add_field(access_token, field_name, field_type, options=None):
    """添加字段（不带 description）"""
    url = f"{BASE_URL}/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    data = {
        "field_name": field_name,
        "type": field_type,
    }

    # 如果有选项，添加到property中
    if options:
        data["property"] = {"options": [{"name": opt} for opt in options]}

    print(f"请求体: {json.dumps(data, ensure_ascii=False)}")

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    print(f"响应: {json.dumps(result, ensure_ascii=False)}")

    if result.get("code") == 0:
        field_id = result["data"]["field"]["field_id"]
        print(f"  ✅ {field_name} (ID: {field_id})\n")
        return field_id
    elif "already exists" in str(result).lower() or result.get("code") == 1240004:
        print(f"  ⏸️  {field_name} (已存在)\n")
        return None
    else:
        print(f"  ❌ {field_name}: {result.get('msg')}\n")
        return None


def get_fields(access_token):
    """获取表格所有字段"""
    url = f"{BASE_URL}/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields?page_size=100"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    response = requests.get(url, headers=headers)
    result = response.json()

    if result.get("code") == 0:
        fields = result.get("data", {}).get("items", [])
        print(f"\n当前表格已有 {len(fields)} 个字段：")
        for field in fields:
            print(f"  - {field['field_name']} (ID: {field['field_id']}, Type: {field['type']})")
        return fields
    else:
        print(f"获取字段失败: {result}")
        return []


def add_record(access_token, record_data):
    """添加记录"""
    url = f"{BASE_URL}/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    data = {"fields": record_data}

    print(f"添加记录请求体: {json.dumps(data, ensure_ascii=False)}")

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    print(f"添加记录响应: {json.dumps(result, ensure_ascii=False)}")

    if result.get("code") == 0:
        record_id = result["data"]["record"]["record_id"]
        return record_id
    else:
        raise Exception(f"添加记录失败: {result}")


def main():
    """主流程"""
    print("=" * 70)
    print("步骤0: 查看当前表格字段")
    print("=" * 70)

    access_token = get_tenant_token()
    print(f"✅ 获取tenant_access_token成功\n")

    get_fields(access_token)

    print("\n" + "=" * 70)
    print("步骤1: 添加表格字段")
    print("=" * 70)

    # 字段类型：1-文本, 3-单选, 5-日期, 13-URL, 18-日期时间

    fields_config = [
        ("brand", 1, None),
        ("brand_en", 1, None),
        ("product_name", 1, None),
        ("sub_brand", 1, None),
        ("batch_codes", 1, None),
        ("pack_size", 1, None),
        ("best_before", 18, None),
        ("region", 1, None),
        ("recall_reason", 1, None),
        ("risk_level", 3, ["高", "中", "低"]),
        ("source_url", 13, None),
        ("source_type", 3, ["官网", "政府平台", "FDA", "FSA"]),
        ("published_date", 18, None),
        ("last_updated", 18, None),
        ("status", 3, ["召回中", "已结束", "待确认"]),
    ]

    print("开始添加字段...\n")
    for field_config in fields_config:
        field_name, field_type, options = field_config
        add_field(access_token, field_name, field_type, options)

    print("\n" + "=" * 70)
    print("步骤2: 再次查看表格字段")
    print("=" * 70)

    get_fields(access_token)

    print("\n" + "=" * 70)
    print("步骤3: 测试添加召回数据")
    print("=" * 70)

    # 测试数据（雀巢召回数据）
    test_record = {
        "brand": "雀巢 Nestlé",
        "brand_en": "Nestlé",
        "product_name": "SMA Advanced First Infant Milk",
        "sub_brand": "SMA",
        "batch_codes": "51450742F1,52319722BA",
        "pack_size": "800g",
        "best_before": 1800556800000,  # 2027-05-01 00:00:00 UTC
        "region": "UK",
        "recall_reason": "Cereulide毒素",
        "risk_level": "高",
        "source_url": "https://www.food.gov.uk/news-alerts/alert/fsa-prin-02-2026-update-1",
        "source_type": "政府平台",
        "published_date": 1736390400000,  # 2026-01-09 00:00:00 UTC
        "last_updated": 1738032000000,  # 2026-01-28 00:00:00 UTC
        "status": "召回中",
    }

    try:
        record_id = add_record(access_token, test_record)
        print(f"\n✅ 测试记录添加成功！")
        print(f"   Record ID: {record_id}")
    except Exception as e:
        print(f"\n❌ 添加测试记录失败: {e}")

    print("\n" + "=" * 70)
    print("✅ 表格字段设置完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
