#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
召回查询API服务器 - 为小程序提供查询接口
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path
import logging
from datetime import datetime

# 添加 scraper 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

import requests
from utils.feishu_config import APP_ID, APP_SECRET, APP_TOKEN, TABLE_ID

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许跨域请求


class FeishuAPI:
    """飞书API封装"""

    def __init__(self):
        self.base_url = "https://open.feishu.cn/open-apis"
        self.token = None
        self.token_expire = 0

    def get_token(self):
        """获取访问令牌"""
        now = datetime.now().timestamp()
        if self.token and now < self.token_expire:
            return self.token

        try:
            url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
            resp = requests.post(url, json={
                "app_id": APP_ID,
                "app_secret": APP_SECRET
            }, timeout=10)
            result = resp.json()

            if result.get("code") == 0:
                self.token = result["tenant_access_token"]
                self.token_expire = now + 7200  # 2小时后过期
                logger.info("成功获取飞书token")
                return self.token
            else:
                raise Exception(f"获取token失败: {result}")
        except Exception as e:
            logger.error(f"获取飞书token异常: {e}")
            raise

    def get_all_records(self):
        """获取所有召回记录"""
        try:
            token = self.get_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8"
            }

            url = f"{self.base_url}/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"

            all_records = []
            page_token = None
            max_pages = 10  # 最多10页，防止死循环

            while len(all_records) < 10000 and max_pages > 0:  # 最多10000条记录
                max_pages -= 1

                params = {"page_size": 500}
                if page_token:
                    params["page_token"] = page_token

                resp = requests.get(url, headers=headers, params=params, timeout=10)
                result = resp.json()

                if result.get("code") == 0:
                    data = result.get("data", {})
                    records = data.get("items", [])
                    all_records.extend(records)

                    page_token = data.get("page_token")
                    if not page_token:
                        break
                else:
                    logger.error(f"获取记录失败: {result}")
                    break

            logger.info(f"成功获取 {len(all_records)} 条召回记录")
            return all_records

        except Exception as e:
            logger.error(f"获取所有记录异常: {e}")
            raise

    def search_by_batch_code(self, batch_code: str):
        """按批次号搜索"""
        try:
            token = self.get_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8"
            }

            url = f"{self.base_url}/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/search"

            data = {
                "filter": {
                    "conjunction": "and",
                    "conditions": [
                        {
                            "field_name": "batch_codes",
                            "operator": "contains",
                            "value": [batch_code]
                        }
                    ]
                }
            }

            resp = requests.post(url, headers=headers, json=data, timeout=10)
            result = resp.json()

            if result.get("code") == 0:
                items = result.get("data", {}).get("items", [])
                total = result.get("data", {}).get("total", 0)
                logger.info(f"批次号 {batch_code} 查询到 {total} 条记录")
                return {
                    "success": True,
                    "items": items,
                    "total": total
                }
            else:
                logger.error(f"查询失败: {result}")
                return {
                    "success": False,
                    "error": result.get("msg"),
                    "items": [],
                    "total": 0
                }
        except Exception as e:
            logger.error(f"查询批次号异常: {e}")
            return {
                "success": False,
                "error": str(e),
                "items": [],
                "total": 0
            }


# 全局API实例
feishu_api = FeishuAPI()


# 缓存所有记录（减少查询延迟）
records_cache = None
cache_timestamp = 0
CACHE_TTL = 300  # 5分钟缓存


def get_cached_records():
    """获取缓存的记录"""
    global records_cache, cache_timestamp

    now = datetime.now().timestamp()
    if records_cache and now - cache_timestamp < CACHE_TTL:
        return records_cache

    # 重新加载
    try:
        records_cache = feishu_api.get_all_records()
        cache_timestamp = now
        logger.info(f"更新缓存: {len(records_cache)} 条记录")
        return records_cache
    except Exception as e:
        logger.error(f"更新缓存失败: {e}")
        return records_cache if records_cache else []


def search_in_cache(batch_code: str) -> list:
    """在缓存中搜索批次号"""
    records = get_cached_records()
    matched = []

    for r in records:
        batch_codes = r['fields'].get('batch_codes', '')
        if batch_code in batch_codes:
            matched.append(r)

    return matched


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "recall-checker-api"
    })


@app.route('/api/query', methods=['POST'])
def query_batch_code():
    """
    查询批次号

    请求体:
    {
        "batch_code": "批次号"
    }

    返回:
    {
        "success": true,
        "data": {...},
        "message": "查询成功"
    }
    """
    try:
        # 获取请求参数
        req_data = request.get_json()
        if not req_data:
            return jsonify({
                "success": False,
                "message": "请求数据为空"
            }), 400

        batch_code = req_data.get('batch_code', '').strip()
        if not batch_code:
            return jsonify({
                "success": False,
                "message": "批次号不能为空"
            }), 400

        # 在缓存中搜索
        matched_records = search_in_cache(batch_code)

        # 格式化响应
        if matched_records:
            # 找到召回记录
            result = {
                "success": True,
                "status": "recalled",
                "data": [r['fields'] for r in matched_records],
                "message": f"找到 {len(matched_records)} 条召回记录"
            }
            logger.info(f"批次号 {batch_code} 查询结果: {len(matched_records)} 条召回")
            return jsonify(result), 200
        else:
            # 未找到召回记录
            result = {
                "success": True,
                "status": "not_found",
                "data": [],
                "message": "未找到召回记录"
            }
            logger.info(f"批次号 {batch_code} 查询结果: 未找到")
            return jsonify(result), 200

    except Exception as e:
        logger.error(f"查询异常: {e}")
        return jsonify({
            "success": False,
            "message": f"查询失败: {str(e)}"
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    获取数据统计

    返回:
    {
        "success": true,
        "data": {
            "total_records": 总记录数,
            "by_brand": 品牌分布,
            "by_status": 状态分布
        }
    }
    """
    try:
        records = get_cached_records()

        # 统计信息
        total = len(records)
        by_brand = {}
        by_status = {}

        for r in records:
            brand = r['fields'].get('brand', 'Unknown')
            status = r['fields'].get('status', 'Unknown')

            by_brand[brand] = by_brand.get(brand, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1

        result = {
            "success": True,
            "data": {
                "total_records": total,
                "by_brand": by_brand,
                "by_status": by_status
            },
            "message": "获取统计成功"
        }

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"获取统计异常: {e}")
        return jsonify({
            "success": False,
            "message": f"获取统计失败: {str(e)}"
        }), 500


@app.errorhandler(404)
def not_found(error):
    """404错误"""
    return jsonify({
        "success": False,
        "message": "接口不存在"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误"""
    return jsonify({
        "success": False,
        "message": "服务器内部错误"
    }), 500


def main():
    """启动服务器"""
    port = 5001
    logger.info(f"启动召回查询API服务器，端口: {port}")
    logger.info(f"飞书表格: {TABLE_ID}")

    # 预热缓存
    try:
        logger.info("预热缓存...")
        get_cached_records()
    except Exception as e:
        logger.warning(f"预热缓存失败: {e}")

    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    main()
