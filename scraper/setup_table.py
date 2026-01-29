"""
自动添加表格字段并测试数据写入
"""

import requests
import json
from datetime import datetime


# 飞书凭证
APP_ID = "cli_a9f1919786f85cb3"
APP_SECRET = "BcrZvWWswquglP6DBkLlccnuDtP3u1do"
APP_TOKEN = "AdcibdxG0atrMHsuIAzcz58jnng"
TABLE_ID = "tblWSEVcPFLZkjxa"

BASE_URL = "https://open.feishu.cn/open-apis"


def get_access_token():
    """获取access_token"""
    url = f"{BASE_URL}/auth/v3/app_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    data = {"app_id": APP_ID, "app_secret": APP_SECRET}

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if result.get("code") != 0:
        raise Exception(f"获取access_token失败: {result}")

    return result["app_access_token"]


def add_field(access_token, field_name, field_type, description=""):
    """添加字段"""
    url = f"{BASE_URL}/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    data = {
        "field_name": field_name,
        "type": field_type,
        "description": description
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if result.get("code") == 0:
        field_id = result["data"]["field"]["field_id"]
        print(f"  ✅ {field_name} (ID: {field_id})")
        return field_id
    elif "already exists" in str(result).lower() or result.get("code") == 1240004:
        print(f"  ⏸️  {field_name} (已存在)")
        return None
    else:
        print(f"  ❌ {field_name}: {result.get('msg')}")
        return None


def add_record(access_token, record_data):
    """添加记录"""
    url = f"{BASE_URL}/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    data = {"fields": record_data}

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if result.get("code") == 0:
        record_id = result["data"]["record"]["record_id"]
        return record_id
    else:
        raise Exception(f"添加记录失败: {result}")


def main():
    """主流程"""
    print("=" * 70)
    print("步骤1: 添加表格字段")
    print("=" * 70)

    access_token = get_access_token()
    print(f"✅ 获取access_token成功\n")

    # 需要添加的字段
    fields_config = [
        ("brand", 1, "品牌（雀巢、Abbott等）"),
        ("brand_en", 1, "品牌英文名"),
        ("product_name", 1, "产品名称"),
        ("sub_brand", 1, "子品牌（SMA、NAN）"),
        ("batch_codes", 1, "批次号列表（逗号分隔）"),
        ("pack_size", 1, "包装规格（800g、400g）"),
        ("best_before", 5, "有效期"),
        ("region", 1, "受影响地区（UK/US/EU/China）"),
        ("recall_reason", 1, "召回原因"),
        ("risk_level", 4, "风险等级（高/中/低）"),
        ("source_url", 15, "官方来源链接"),
        ("source_type", 4, "数据源类型（官网/政府平台）"),
        ("published_date", 5, "发布日期"),
        ("last_updated", 5, "最后更新日期"),
        ("status", 4, "状态（召回中/已结束/待确认）"),
    ]

    print("开始添加字段...\n")
    for field_name, field_type, desc in fields_config:
        add_field(access_token, field_name, field_type, desc)

    print("\n" + "=" * 70)
    print("步骤2: 测试添加召回数据")
    print("=" * 70)

    # 测试数据（雀巢召回数据）
    test_record = {
        "文本": f"测试记录-{datetime.now().strftime('%H%M%S')}",
        "brand": "雀巢 Nestlé",
        "brand_en": "Nestlé",
        "product_name": "SMA Advanced First Infant Milk",
        "sub_brand": "SMA",
        "batch_codes": "51450742F1,52319722BA",
        "pack_size": "800g",
        "best_before": 1800556800000,  # 2027-05-01
        "region": "UK",
        "recall_reason": "Cereulide毒素",
        "risk_level": "高",
        "source_url": "https://www.food.gov.uk/news-alerts/alert/fsa-prin-02-2026-update-1",
        "source_type": "政府平台",
        "published_date": 1736390400000,  # 2026-01-09
        "last_updated": 1738032000000,  # 2026-01-28
        "status": "召回中"
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
