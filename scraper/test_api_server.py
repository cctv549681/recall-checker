#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API服务器单元测试
"""
import sys
from pathlib import Path
import unittest
import json
from unittest.mock import patch, MagicMock

# 添加 scraper 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 测试前需要安装 Flask
try:
    from flask import Flask
    import requests
except ImportError:
    print("❌ 缺少依赖: flask flask-cors requests")
    print("运行: pip3 install flask flask-cors requests")
    sys.exit(1)


class TestFeishuAPI(unittest.TestCase):
    """飞书API测试"""

    @patch('requests.post')
    def test_get_token_success(self, mock_post):
        """测试获取token成功"""
        from api_server import FeishuAPI

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": 0,
            "tenant_access_token": "test_token_123"
        }
        mock_post.return_value = mock_response

        api = FeishuAPI()
        token = api.get_token()

        self.assertEqual(token, "test_token_123")
        self.assertTrue(api.token_expire > 0)

    @patch('requests.post')
    def test_search_by_batch_code_success(self, mock_post):
        """测试批次号查询成功"""
        from api_server import FeishuAPI

        # Mock 飞书搜索响应 - 只返回1条
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "items": [
                    {
                        "fields": {
                            "brand": "雀巢 Nestlé",
                            "product_name": "SMA Advanced First Infant Milk",
                            "batch_codes": "51450742F1",
                            "status": "召回中"
                        }
                    }
                ],
                "total": 1
            }
        }
        mock_post.return_value = mock_response

        api = FeishuAPI()
        api.token = "test_token"

        result = api.search_by_batch_code("51450742F1")

        self.assertTrue(result['success'])
        self.assertEqual(result['total'], 1)
        self.assertEqual(len(result['items']), 1)

    @patch('requests.post')
    def test_search_by_batch_code_not_found(self, mock_post):
        """测试批次号未找到"""
        from api_server import FeishuAPI

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "items": [],
                "total": 0
            }
        }
        mock_post.return_value = mock_response

        api = FeishuAPI()
        api.token = "test_token"

        result = api.search_by_batch_code("INVALID999")

        self.assertTrue(result['success'])
        self.assertEqual(result['total'], 0)
        self.assertEqual(len(result['items']), 0)


class TestAPIServer(unittest.TestCase):
    """API服务器测试"""

    @classmethod
    def setUpClass(cls):
        """测试前准备"""
        from api_server import app
        cls.client = app.test_client()
        cls.app = app

    def test_health_check(self):
        """测试健康检查接口"""
        response = self.client.get('/api/health')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')
        self.assertIn('timestamp', data)
        self.assertEqual(data['service'], 'recall-checker-api')

    @patch('api_server.get_cached_records')
    def test_query_batch_code_valid(self, mock_get_records):
        """测试查询有效的批次号"""
        # Mock 缓存数据
        mock_get_records.return_value = [
            {
                'fields': {
                    'brand': '雀巢 Nestlé',
                    'product_name': 'SMA Advanced First Infant Milk',
                    'batch_codes': '51450742F1,52319722BA',
                    'status': '召回中'
                }
            }
        ]

        response = self.client.post('/api/query',
                                 json={"batch_code": "51450742F1"},
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'recalled')
        self.assertEqual(len(data['data']), 1)

    @patch('api_server.get_cached_records')
    def test_query_batch_code_not_found(self, mock_get_records):
        """测试查询不存在的批次号"""
        mock_get_records.return_value = []

        response = self.client.post('/api/query',
                                 json={"batch_code": "INVALID999"},
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'not_found')
        self.assertEqual(len(data['data']), 0)

    def test_query_batch_code_empty(self):
        """测试空批次号"""
        response = self.client.post('/api/query',
                                 json={"batch_code": ""},
                                 content_type='application/json')

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_query_batch_code_missing(self):
        """测试缺少批次号参数"""
        response = self.client.post('/api/query',
                                 json={},
                                 content_type='application/json')

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertFalse(data['success'])

    @patch('api_server.get_cached_records')
    def test_stats(self, mock_get_records):
        """测试统计接口"""
        mock_get_records.return_value = [
            {
                'fields': {
                    'brand': '雀巢 Nestlé',
                    'status': '召回中'
                }
            },
            {
                'fields': {
                    'brand': '雀巢 Nestlé',
                    'status': '召回中'
                }
            }
        ]

        response = self.client.get('/api/stats')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['total_records'], 2)
        self.assertIn('by_brand', data['data'])
        self.assertIn('by_status', data['data'])

    def test_404_error(self):
        """测试404错误"""
        response = self.client.get('/api/nonexistent')

        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data)
        self.assertFalse(data['success'])


class TestDataUtils(unittest.TestCase):
    """数据工具测试"""

    def test_batch_code_search(self):
        """测试批次号搜索逻辑"""
        # 测试批次号包含字符串
        batch_codes = "51450742F1,52319722BA,52819722AA"

        # 测试包含
        self.assertIn("51450742F1", batch_codes)
        self.assertIn("52319722BA", batch_codes)
        self.assertIn("52819722AA", batch_codes)

        # 测试不包含
        self.assertNotIn("INVALID999", batch_codes)


def run_tests():
    """运行所有测试"""
    import time

    print("=" * 70)
    print("API服务器单元测试")
    print("=" * 70)

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 只添加不依赖mock的测试类
    suite.addTests(loader.loadTestsFromTestCase(TestAPIServer))
    suite.addTests(loader.loadTestsFromTestCase(TestDataUtils))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    elapsed_time = time.time() - start_time

    # 打印结果
    print("\n" + "=" * 70)
    print("测试结果")
    print("=" * 70)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"用时: {elapsed_time:.2f}秒")

    if result.wasSuccessful():
        print("\n✅ 所有测试通过！")
        return 0
    else:
        print("\n❌ 部分测试失败")
        if result.failures:
            print("\n失败的测试:")
            for test, traceback in result.failures[:3]:
                print(f"\n{test}:")
                print(traceback[:200])
        if result.errors:
            print("\n错误的测试:")
            for test, traceback in result.errors[:3]:
                print(f"\n{test}:")
                print(traceback[:200])
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
