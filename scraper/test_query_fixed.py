#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书查询功能测试脚本（修复版）
"""
import sys
from pathlib import Path

# 添加 scraper 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

import requests
from utils.feishu_config import APP_ID, APP_SECRET, APP_TOKEN, TABLE_ID


class FeishuQueryTester:
    """飞书查询测试器（修复版）"""

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

    def query_by_batch_code_v2(self, batch_code: str) -> dict:
        """
        按批次号查询（使用过滤器）

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

        # 使用filter代替search
        url = f"{self.base_url}/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/search"

        data = {
            "filter": {
                "conditions": [
                    {
                        "field_name": "batch_codes",
                        "operator": "contains",
                        "value": [batch_code]
                    }
                ]
            }
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

    def query_by_batch_code_exact(self, batch_code: str) -> dict:
        """
        按批次号精确查询（从所有记录中过滤）

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

        # 获取所有记录
        url = f"{self.base_url}/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"

        all_records = []
        page_token = None

        while True:
            params = {"page_size": 500}
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
                break

        # 在客户端过滤批次号
        matched = []
        for r in all_records:
            batch_codes = r['fields'].get('batch_codes', '')
            # 批次号可能是逗号分隔的字符串
            if batch_code in batch_codes:
                matched.append(r)

        return {
            "success": True,
            "data": {
                "items": matched,
                "total": len(matched)
            },
            "total": len(matched)
        }


def test_queries():
    """测试查询功能（修复版）"""
    print("=" * 70)
    print("飞书查询功能测试（修复版）")
    print("=" * 70)

    tester = FeishuQueryTester()

    # 测试1: 查询雀巢批次号（使用精确匹配）
    print("\n测试1: 查询雀巢批次号（精确匹配）")
    nestle_batch = "51450742F1"
    result = tester.query_by_batch_code_exact(nestle_batch)
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
            print(f"  批次号: {r['fields'].get('batch_codes')[:100]}")

    # 测试2: 查询雅培批次号（精确匹配）
    print("\n测试2: 查询雅培批次号（精确匹配）")
    abbott_batch = "57713T260"
    result = tester.query_by_batch_code_exact(abbott_batch)
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
            print(f"  批次号: {r['fields'].get('batch_codes')[:100]}")

    # 测试3: 查询不存在的批次号
    print("\n测试3: 查询不存在的批次号")
    fake_batch = "INVALID999"
    result = tester.query_by_batch_code_exact(fake_batch)
    print(f"  查询批次号: {fake_batch}")
    print(f"  成功: {result['success']}")
    if result['success']:
        print(f"  找到 {result['total']} 条记录 (应为0)")

    # 测试4: 部分批次号匹配
    print("\n测试4: 部分批次号匹配")
    partial_batch = "5145"
    result = tester.query_by_batch_code_exact(partial_batch)
    print(f"  查询批次号（部分）: {partial_batch}")
    print(f"  成功: {result['success']}")
    if result['success']:
        print(f"  找到 {result['total']} 条记录")
        if result['total'] > 0:
            records = result['data'].get('items', [])
            print(f"  示例产品: {records[0]['fields'].get('product_name')}")

    print("\n" + "=" * 70)
    print("✅ 查询测试完成")
    print("=" * 70)


def main():
    """主函数"""
    test_queries()


if __name__ == "__main__":
    main()
