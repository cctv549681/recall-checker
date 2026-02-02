#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书查询功能测试脚本
"""
import sys
from pathlib import Path

# 添加 scraper 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

import requests
from utils.feishu_config import APP_ID, APP_SECRET, APP_TOKEN, TABLE_ID


class FeishuQueryTester:
    """飞书查询测试器"""

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

    def query_by_batch_code(self, batch_code: str) -> dict:
        """
        按批次号查询

        Args:
            batch_code: 批次号

        Returns:
            查询结果
        """
        token = self.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        url = f"{self.base_url}/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/search"

        data = {
            "field_name": "batch_codes",
            "query": batch_code
        }

        resp = requests.post(url, headers=headers, json=data)
        result = resp.json()

        if result.get("code") == 0:
            return {
                "success": True,
                "data": result.get("data", {}),
                "total": result.get("data", {}).get("total", 0)
            }
        else:
            return {
                "success": False,
                "error": result.get("msg"),
                "code": result.get("code")
            }

    def get_all_records(self, page_size: int = 100) -> list:
        """
        获取所有记录

        Args:
            page_size: 每页记录数

        Returns:
            记录列表
        """
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


def test_queries():
    """测试查询功能"""
    print("=" * 70)
    print("飞书查询功能测试")
    print("=" * 70)

    tester = FeishuQueryTester()

    # 测试1: 查询雀巢批次号
    print("\n测试1: 查询雀巢批次号")
    nestle_batch = "51450742F1"
    result = tester.query_by_batch_code(nestle_batch)
    print(f"  查询批次号: {nestle_batch}")
    print(f"  成功: {result['success']}")
    if result['success']:
        print(f"  找到 {result['total']} 条记录")
        records = result['data'].get('items', [])
        if records:
            r = records[0]
            print(f"  产品: {r['fields'].get('product_name')}")
            print(f"  品牌: {r['fields'].get('brand')}")
            print(f"  状态: {r['fields'].get('status')}")
    else:
        print(f"  错误: {result.get('error')}")

    # 测试2: 查询雅培批次号
    print("\n测试2: 查询雅培批次号")
    abbott_batch = "57713T260"
    result = tester.query_by_batch_code(abbott_batch)
    print(f"  查询批次号: {abbott_batch}")
    print(f"  成功: {result['success']}")
    if result['success']:
        print(f"  找到 {result['total']} 条记录")
        records = result['data'].get('items', [])
        if records:
            r = records[0]
            print(f"  产品: {r['fields'].get('product_name')}")
            print(f"  品牌: {r['fields'].get('brand')}")
            print(f"  状态: {r['fields'].get('status')}")
    else:
        print(f"  错误: {result.get('error')}")

    # 测试3: 查询不存在的批次号
    print("\n测试3: 查询不存在的批次号")
    fake_batch = "INVALID999"
    result = tester.query_by_batch_code(fake_batch)
    print(f"  查询批次号: {fake_batch}")
    print(f"  成功: {result['success']}")
    if result['success']:
        print(f"  找到 {result['total']} 条记录 (应为0)")
    else:
        print(f"  错误: {result.get('error')}")

    # 测试4: 获取所有记录统计
    print("\n测试4: 获取所有记录")
    records = tester.get_all_records(page_size=500)
    print(f"  总记录数: {len(records)}")

    if records:
        # 统计品牌分布
        brand_stats = {}
        for r in records:
            brand = r['fields'].get('brand', 'Unknown')
            brand_stats[brand] = brand_stats.get(brand, 0) + 1

        print("\n  品牌分布:")
        for brand, count in sorted(brand_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"    {brand}: {count} 条")

        # 统计状态分布
        status_stats = {}
        for r in records:
            status = r['fields'].get('status', 'Unknown')
            status_stats[status] = status_stats.get(status, 0) + 1

        print("\n  状态分布:")
        for status, count in sorted(status_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"    {status}: {count} 条")

    print("\n" + "=" * 70)
    print("✅ 查询测试完成")
    print("=" * 70)


def main():
    """主函数"""
    test_queries()


if __name__ == "__main__":
    main()
