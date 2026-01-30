#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书表格管理器
提供表格创建、字段管理、数据查询等操作
"""
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime


class FeishuTableManager:
    """飞书多维表格管理器"""

    def __init__(self, app_id: str, app_secret: str, app_token: str, table_id: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_token = app_token
        self.table_id = table_id
        self.base_url = "https://open.feishu.cn/open-apis"

        # Token 缓存
        self.tenant_token = None
        self.token_expire = 0

    def get_tenant_token(self) -> str:
        """获取 tenant_access_token"""
        # 检查缓存
        if self.tenant_token and datetime.now().timestamp() < self.token_expire:
            return self.tenant_token

        # 获取新 token
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        resp = requests.post(url, json={
            "app_id": self.app_id,
            "app_secret": self.app_secret
        })

        result = resp.json()
        if result.get("code") != 0:
            raise Exception(f"获取飞书token失败: {result}")

        # 缓存2小时
        self.tenant_token = result["tenant_access_token"]
        self.token_expire = datetime.now().timestamp() + 7200

        return self.tenant_token

    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        token = self.get_tenant_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

    def create_field(self, field_name: str, field_type: int, description: str = "") -> Optional[str]:
        """
        创建字段
        
        Args:
            field_name: 字段名称
            field_type: 字段类型（1=Text, 3=SingleSelect, 5=DateTime, 15=Url）
            description: 字段描述
        
        Returns:
            字段ID（创建失败返回None）
        """
        url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/fields"
        headers = self.get_headers()

        data = {
            "field_name": field_name,
            "type": field_type
        }

        # 添加描述（可选）
        if description:
            data["description"] = description

        try:
            resp = requests.post(url, headers=headers, json=data)
            result = resp.json()

            if result.get("code") == 0:
                field_id = result["data"]["field"]["field_id"]
                print(f"✅ 创建字段成功: {field_name} ({field_id})")
                return field_id
            else:
                print(f"❌ 创建字段失败 {field_name}: {result.get('msg')}")
                return None

        except Exception as e:
            print(f"❌ 创建字段异常 {field_name}: {e}")
            return None

    def get_fields(self) -> List[Dict[str, Any]]:
        """获取所有字段"""
        url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/fields?page_size=100"
        headers = self.get_headers()

        try:
            resp = requests.get(url, headers=headers)
            result = resp.json()

            if result.get("code") == 0:
                fields = result.get("data", {}).get("items", [])
                print(f"✅ 获取到 {len(fields)} 个字段")
                return fields
            else:
                print(f"❌ 获取字段失败: {result.get('msg')}")
                return []

        except Exception as e:
            print(f"❌ 获取字段异常: {e}")
            return []

    def create_record(self, fields: Dict[str, Any]) -> Optional[str]:
        """
        创建记录
        
        Args:
            fields: 字段数据字典
        
        Returns:
            记录ID（创建失败返回None）
        """
        url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records"
        headers = self.get_headers()

        data = {"fields": fields}

        try:
            resp = requests.post(url, headers=headers, json=data)
            result = resp.json()

            if result.get("code") == 0:
                record_id = result["data"]["record"]["record_id"]
                print(f"✅ 创建记录成功")
                return record_id
            else:
                print(f"❌ 创建记录失败: {result.get('msg')}")
                return None

        except Exception as e:
            print(f"❌ 创建记录异常: {e}")
            return None

    def query_records(self, filter_field: str = None, filter_value: Any = None, page_size: int = 50) -> List[Dict[str, Any]]:
        """
        查询记录
        
        Args:
            filter_field: 过滤字段名
            filter_value: 过滤值
            page_size: 每页数量
        
        Returns:
            记录列表
        """
        url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records"
        headers = self.get_headers()

        data = {
            "page_size": page_size
        }

        # 添加过滤条件
        if filter_field and filter_value is not None:
            data["filter"] = {
                "conditions": [
                    {
                        "field_name": filter_field,
                        "operator": "is",
                        "value": [filter_value]
                    }
                ]
            }

        try:
            resp = requests.post(url, headers=headers, json=data)
            result = resp.json()

            if result.get("code") == 0:
                records = result.get("data", {}).get("items", [])
                print(f"✅ 查询到 {len(records)} 条记录")
                return records
            else:
                print(f"❌ 查询记录失败: {result.get('msg')}")
                return []

        except Exception as e:
            print(f"❌ 查询记录异常: {e}")
            return []

    def search_batch_code(self, batch_code: str) -> List[Dict[str, Any]]:
        """
        搜索批次号
        
        Args:
            batch_code: 批次号
        
        Returns:
            匹配的记录列表
        """
        # 标准化批次号
        normalized_batch = batch_code.strip().upper()

        url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records/search"
        headers = self.get_headers()

        data = {
            "filter": {
                "conditions": [
                    {
                        "field_name": "batch_codes",
                        "operator": "contains",
                        "value": [normalized_batch]
                    }
                ]
            },
            "page_size": 100
        }

        try:
            resp = requests.post(url, headers=headers, json=data)
            result = resp.json()

            if result.get("code") == 0:
                records = result.get("data", {}).get("items", [])
                print(f"✅ 搜索批次号 '{batch_code}' 找到 {len(records)} 条记录")
                return records
            else:
                print(f"❌ 搜索批次号失败: {result.get('msg')}")
                return []

        except Exception as e:
            print(f"❌ 搜索批次号异常: {e}")
            return []

    def get_record_count(self) -> int:
        """获取记录总数"""
        url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records"
        headers = self.get_headers()

        data = {
            "page_size": 1
        }

        try:
            resp = requests.post(url, headers=headers, json=data)
            result = resp.json()

            if result.get("code") == 0:
                total = result.get("data", {}).get("total", 0)
                print(f"✅ 记录总数: {total}")
                return total
            else:
                print(f"❌ 获取记录总数失败: {result.get('msg')}")
                return 0

        except Exception as e:
            print(f"❌ 获取记录总数异常: {e}")
            return 0


# 测试代码
if __name__ == "__main__":
    # 测试配置
    from feishu_config import APP_ID, APP_SECRET, APP_TOKEN, TABLE_ID

    print("=" * 70)
    print("飞书表格管理器测试")
    print("=" * 70)

    manager = FeishuTableManager(APP_ID, APP_SECRET, APP_TOKEN, TABLE_ID)

    # 测试1：获取所有字段
    print("\n测试1：获取所有字段")
    fields = manager.get_fields()
    if fields:
        print(f"字段列表：")
        for field in fields:
            print(f"  - {field.get('field_name')}: {field.get('type')}")

    # 测试2：搜索批次号
    print("\n测试2：搜索批次号")
    test_batch = "51450742F1"
    records = manager.search_batch_code(test_batch)
    if records:
        print(f"找到 {len(records)} 条匹配记录")
        for i, record in enumerate(records[:3], 1):
            fields = record.get('fields', {})
            print(f"  {i}. 品牌: {fields.get('brand')}, 产品: {fields.get('product_name')}")

    # 测试3：获取记录总数
    print("\n测试3：获取记录总数")
    count = manager.get_record_count()
    print(f"当前记录总数: {count}")

    print("\n" + "=" * 70)
    print("✅ 测试完成")
    print("=" * 70)
