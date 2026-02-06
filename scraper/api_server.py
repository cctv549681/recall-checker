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

# 导入 OCR 服务
try:
    from ocr_service import get_ocr_service
    OCR_AVAILABLE = True
    logger.info("OCR 服务模块加载成功")
except ImportError as e:
    OCR_AVAILABLE = False
    logger.warning(f"OCR 服务模块加载失败: {e}")


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


@app.route('/api/ocr/status', methods=['GET'])
def ocr_status():
    """
    获取 OCR 服务状态

    返回:
    {
        "success": true,
        "data": {
            "available": true/false,
            "provider": "baidu/glm",
            "configured": true/false,
            "uploader": "local/aliyun/tencent"
        }
    }
    """
    try:
        if not OCR_AVAILABLE:
            return jsonify({
                "success": True,
                "data": {
                    "available": False,
                    "provider": None,
                    "configured": False,
                    "uploader": None,
                    "message": "OCR 服务模块不可用"
                }
            }), 200

        ocr_service = get_ocr_service()

        return jsonify({
            "success": True,
            "data": {
                "available": True,
                "provider": ocr_service.provider,
                "configured": ocr_service.is_configured,
                "uploader": ocr_service._uploader.__class__.__name__ if ocr_service._uploader else None
            },
            "message": "获取 OCR 状态成功"
        }), 200

    except Exception as e:
        logger.error(f"获取 OCR 状态异常: {e}")
        return jsonify({
            "success": False,
            "message": f"获取 OCR 状态失败: {str(e)}"
        }), 500


@app.route('/api/ocr/switch', methods=['POST'])
def ocr_switch():
    """
    切换 OCR 提供商

    请求体:
    {
        "provider": "baidu/glm"
    }

    返回:
    {
        "success": true,
        "data": {
            "provider": "新的提供商"
        }
    }
    """
    try:
        if not OCR_AVAILABLE:
            return jsonify({
                "success": False,
                "message": "OCR 服务模块不可用"
            }), 400

        req_data = request.get_json()
        if not req_data:
            return jsonify({
                "success": False,
                "message": "请求数据为空"
            }), 400

        new_provider = req_data.get('provider', '').lower()
        if new_provider not in ['baidu', 'glm']:
            return jsonify({
                "success": False,
                "message": "不支持的 OCR 提供商，可选: baidu, glm"
            }), 400

        # 重置 OCR 服务（强制重新初始化）
        from ocr_service import reset_ocr_service
        reset_ocr_service()

        # 设置环境变量
        os.environ['OCR_PROVIDER'] = new_provider

        # 获取新的 OCR 服务
        ocr_service = get_ocr_service()

        logger.info(f"OCR 提供商已切换到: {ocr_service.provider}")

        return jsonify({
            "success": True,
            "data": {
                "provider": ocr_service.provider,
                "configured": ocr_service.is_configured
            },
            "message": f"已切换到 {ocr_service.provider} OCR"
        }), 200

    except Exception as e:
        logger.error(f"切换 OCR 提供商异常: {e}")
        return jsonify({
            "success": False,
            "message": f"切换 OCR 提供商失败: {str(e)}"
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


@app.route('/api/ocr', methods=['POST'])
def ocr_image():
    """
    OCR图片识别批次号（支持百度 OCR 和 GLM OCR）

    请求体:
    {
        "image_url": "图片URL",
        "image_base64": "图片Base64"
    }

    返回:
    {
        "success": true,
        "data": {
            "batch_code": "批次号",
            "confidence": 置信度,
            "text": "全部文本",
            "provider": "baidu/glm"
        },
        "message": "识别成功"
    }
    """
    try:
        req_data = request.get_json()
        if not req_data:
            return jsonify({
                "success": False,
                "message": "请求数据为空"
            }), 400

        image_url = req_data.get('image_url', '')
        image_base64 = req_data.get('image_base64', '')

        logger.info(f"OCR请求 - URL: {image_url[:50] if image_url else 'N/A'}, Base64: {'有' if image_base64 else '无'}")

        # 检查 OCR 服务是否可用
        if not OCR_AVAILABLE:
            logger.warning("OCR 服务模块不可用，使用模拟数据")

            # 模拟OCR结果（用于测试）
            mock_result = {
                "batch_code": "51450742F1",
                "confidence": 85,
                "text": "51450742F1",
                "provider": "mock"
            }

            result = {
                "success": True,
                "data": mock_result,
                "message": "识别成功（模拟，OCR 服务模块不可用）"
            }

            logger.info(f"OCR识别结果（模拟）: {mock_result}")
            return jsonify(result), 200

        # 使用 OCR 服务
        ocr_service = get_ocr_service()

        if not ocr_service.is_configured:
            logger.warning(f"OCR 服务未配置（{ocr_service.provider}），使用模拟数据")

            # 模拟OCR结果
            mock_result = {
                "batch_code": "51450742F1",
                "confidence": 85,
                "text": "51450742F1",
                "provider": ocr_service.provider
            }

            result = {
                "success": True,
                "data": mock_result,
                "message": f"识别成功（模拟，{ocr_service.provider} API Key 未配置）"
            }

            logger.info(f"OCR识别结果（模拟）: {mock_result}")
            return jsonify(result), 200

        # 判断使用 URL 还是 Base64
        if image_base64:
            ocr_result = ocr_service.recognize_base64(image_base64)
        elif image_url:
            ocr_result = ocr_service.recognize_url(image_url)
        else:
            return jsonify({
                "success": False,
                "message": "请提供 image_url 或 image_base64"
            }), 400

        # 返回结果
        if ocr_result['success']:
            result = {
                "success": True,
                "data": {
                    "batch_code": ocr_result['batch_code'],
                    "confidence": ocr_result['confidence'],
                    "text": ocr_result['text'],
                    "provider": ocr_result['provider']
                },
                "message": "识别成功"
            }

            logger.info(f"OCR识别结果（{ocr_result['provider']}）: batch_code={ocr_result['batch_code']}, confidence={ocr_result['confidence']}")
            return jsonify(result), 200
        else:
            return jsonify({
                "success": False,
                "message": f"识别失败: {ocr_result.get('error', '未知错误')}"
            }), 400

    except Exception as e:
        logger.error(f"OCR接口异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"OCR识别失败: {str(e)}"
        }), 500


