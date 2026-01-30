"""
飞书多维表格客户端
使用飞书开放平台API操作多维表格
"""

import requests
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
import os


class FeishuClient:
    """飞书多维表格客户端"""

    def __init__(self, app_id: str, app_secret: str, app_token: str = None, table_ids: Dict[str, str] = None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_token = app_token
        self.table_ids = table_ids or {}

        # API基础URL
        self.base_url = "https://open.feishu.cn/open-apis"

        # access_token缓存
        self._access_token = None
        self._token_expire_at = 0

    def get_access_token(self) -> str:
        """获取tenant_access_token（带缓存）"""
        # 检查token是否过期
        if self._access_token and datetime.now().timestamp() < self._token_expire_at:
            return self._access_token

        # 请求新token - 使用 tenant_access_token
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {"app_id": self.app_id, "app_secret": self.app_secret}

        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()

            if result.get("code") != 0:
                raise Exception(f"获取tenant_access_token失败: {result}")

            self._access_token = result["tenant_access_token"]
            # token有效期2小时，提前10分钟刷新
            self._token_expire_at = datetime.now().timestamp() + 7000

            return self._access_token

        except Exception as e:
            raise Exception(f"请求飞书API失败: {e}")

    def _make_request(
        self, method: str, path: str, data: Dict = None, app_token: str = None
    ) -> Dict:
        """统一的API请求方法"""
        # 构建URL
        if app_token:
            url = f"{self.base_url}{path}"
        else:
            url = f"{self.base_url}{path}"

        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=data)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PATCH":
                response = requests.patch(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, json=data)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            result = response.json()

            if result.get("code") != 0:
                raise Exception(
                    f"API请求失败 [{result.get('code')}]: {result.get('msg')}"
                )

            return result.get("data", {})

        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {e}")

    def create_record(self, table_key: str, record: Dict) -> str:
        """
        创建记录

        Args:
            table_key: 表格key (recalled_batches / brand_config / query_logs)
            record: 记录数据

        Returns:
            record_id: 记录ID
        """
        if not self.app_token:
            raise ValueError("app_token未设置，请在初始化时传入")

        if table_key not in self.table_ids:
            raise ValueError(f"未知的表格key: {table_key}")

        table_id = self.table_ids[table_key]

        # 构造记录数据
        fields = {}
        for key, value in record.items():
            if value is not None and value != "":
                fields[key] = value

        data = {"fields": fields}

        # 正确的API路径: /bitable/v1/apps/{app_token}/tables/{table_id}/records
        result = self._make_request(
            "POST",
            f"/bitable/v1/apps/{self.app_token}/tables/{table_id}/records",
            data,
            app_token=self.app_token
        )

        return result["record"]["record_id"]

    def query_records(
        self, table_key: str, filter_condition: Dict = None, page_size: int = 20
    ) -> List[Dict]:
        """
        查询记录

        Args:
            table_key: 表格key
            filter_condition: 过滤条件
            page_size: 每页记录数

        Returns:
            records: 记录列表
        """
        if not self.app_token:
            raise ValueError("app_token未设置，请在初始化时传入")

        if table_key not in self.table_ids:
            raise ValueError(f"未知的表格key: {table_key}")

        table_id = self.table_ids[table_key]

        data = {"page_size": page_size}

        if filter_condition:
            data["filter"] = filter_condition

        result = self._make_request(
            "GET",
            f"/bitable/v1/apps/{self.app_token}/tables/{table_id}/records",
            data,
            app_token=self.app_token
        )

        return result.get("items", [])

    def update_record(self, table_key: str, record_id: str, record: Dict) -> bool:
        """
        更新记录

        Args:
            table_key: 表格key
            record_id: 记录ID
            record: 更新数据

        Returns:
            success: 是否成功
        """
        if not self.app_token:
            raise ValueError("app_token未设置，请在初始化时传入")

        if table_key not in self.table_ids:
            raise ValueError(f"未知的表格key: {table_key}")

        table_id = self.table_ids[table_key]

        # 构造记录数据
        fields = {}
        for key, value in record.items():
            if value is not None and value != "":
                fields[key] = value

        data = {"fields": fields}

        self._make_request(
            "PATCH",
            f"/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}",
            data,
            app_token=self.app_token
        )

        return True

    def delete_record(self, table_key: str, record_id: str) -> bool:
        """
        删除记录

        Args:
            table_key: 表格key
            record_id: 记录ID

        Returns:
            success: 是否成功
        """
        if not self.app_token:
            raise ValueError("app_token未设置，请在初始化时传入")

        if table_key not in self.table_ids:
            raise ValueError(f"未知的表格key: {table_key}")

        table_id = self.table_ids[table_key]

        self._make_request(
            "DELETE",
            f"/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}",
            app_token=self.app_token
        )

        return True


# 测试代码
if __name__ == "__main__":
    # 从环境变量读取
    app_id = os.getenv("FEISHU_APP_ID", "cli_a9f1f4887e38dcd2")
    app_secret = os.getenv("FEISHU_APP_SECRET", "aNhAQdFTDJSWaQZnj2dy7dXvDgOzdi7u")
    app_token = os.getenv("FEISHU_APP_TOKEN", "Af9TwoIEkiJwkhkq0YEcw3WRnMZ")

    client = FeishuClient(app_id, app_secret, app_token=app_token)

    print("测试飞书API连接...")

    try:
        # 测试获取access_token
        token = client.get_access_token()
        print(f"✅ 成功获取access_token: {token[:20]}...")

        # 测试创建记录
        test_record = {"品牌": "测试品牌", "批次号": "TEST123456"}

        print("测试创建记录...")
        record_id = client.create_record("recalled_batches", test_record)
        print(f"✅ 成功创建记录: {record_id}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
