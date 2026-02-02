#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查飞书表格中的实际数据
"""
import sys
from pathlib import Path

# 添加 scraper 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

import requests
from utils.feishu_config import APP_ID, APP_SECRET, APP_TOKEN, TABLE_ID


class FeishuDataChecker:
    """飞书数据检查器"""

    def __init__(self):
        self.base_url = "https://open.feishu.cn/open-apis"
        self.token = None

    def get_token(self):
        """获取访问令牌"""
        if not self.token:
            url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
            resp = requests.post(url, json={
                "app_id": APP_ID,
                "app_secret": APP_SECRET
            })
            result = resp.json()
            if result.get("code") == 0:
                self.token = result["tenant_access_token"]
            else:
                raise Exception(f"获取token失败: {result}")
        return self.token

    def get_all_records(self, page_size: int = 100):
        """获取所有记录"""
        token = self.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        url = f"{self.base_url}/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"

        all_records = []
        page_token = None

        while True:
            params = {"page_size": page_size}
            if page_token:
                params["page_token"] = page_token

            resp = requests.get(url, headers=headers, params=params)
            result = resp.json()

            if result.get("code") == 0:
                data = result.get("data", {})
                records = data.get("items", [])
                all_records.extend(records)

                page_token = data.get("page_token")
                if not page_token:
                    break
            else:
                print(f"❌ 查询失败: {result}")
                break

        return all_records


def check_data():
    """检查数据"""
    print("=" * 70)
    print("飞书表格数据检查")
    print("=" * 70)

    checker = FeishuDataChecker()
    records = checker.get_all_records(page_size=500)

    print(f"\n总记录数: {len(records)}\n")

    if not records:
        print("表格为空")
        return

    # 显示前5条记录
    print("前5条记录:")
    for i, r in enumerate(records[:5], 1):
        fields = r['fields']
        print(f"\n{i}. 品牌: {fields.get('brand', 'N/A')}")
        print(f"   产品: {fields.get('product_name', 'N/A')}")
        print(f"   批次: {fields.get('batch_codes', 'N/A')}")
        print(f"   状态: {fields.get('status', 'N/A')}")

    # 统计品牌
    brand_stats = {}
    for r in records:
        brand = r['fields'].get('brand', 'Unknown')
        brand_stats[brand] = brand_stats.get(brand, 0) + 1

    print("\n\n品牌分布:")
    for brand, count in sorted(brand_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {brand}: {count} 条")

    # 统计状态
    status_stats = {}
    for r in records:
        status = r['fields'].get('status', 'Unknown')
        status_stats[status] = status_stats.get(status, 0) + 1

    print("\n状态分布:")
    for status, count in sorted(status_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {status}: {count} 条")

    # 查找雅培数据
    abbott_records = [r for r in records if '雅培' in str(r['fields'].get('brand', '')) or 'Abbott' in str(r['fields'].get('brand', ''))]

    print(f"\n雅培记录数: {len(abbott_records)}")

    if abbott_records:
        print("\n雅培记录示例:")
        for i, r in enumerate(abbott_records[:3], 1):
            fields = r['fields']
            print(f"\n{i}. 产品: {fields.get('product_name', 'N/A')}")
            print(f"   批次: {fields.get('batch_codes', 'N/A')}")
            print(f"   状态: {fields.get('status', 'N/A')}")
            if fields.get('published_date'):
                import datetime
                pub_date = datetime.datetime.fromtimestamp(fields['published_date'])
                print(f"   发布日期: {pub_date}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    check_data()
