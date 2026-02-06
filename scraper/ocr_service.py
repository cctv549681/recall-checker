#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR 服务集成模块
统一支持百度 OCR 和 GLM OCR
"""
import sys
from pathlib import Path
import os
import logging

# 添加 OCR 模块路径
ocr_module_path = Path(__file__).parent.parent.parent / "ocr"
sys.path.insert(0, str(ocr_module_path))

logger = logging.getLogger(__name__)


class OCRService:
    """OCR 服务类 - 统一接口"""

    def __init__(self):
        """初始化 OCR 服务"""
        self._client = None
        self._provider = None
        self._uploader = None

        # 初始化客户端
        self._init_client()

    def _init_client(self):
        """初始化 OCR 客户端"""
        from ocr import OCRClient, create_uploader

        # 从环境变量读取配置
        provider = os.environ.get('OCR_PROVIDER', 'baidu').lower()

        if provider == 'baidu':
            # 百度 OCR
            self._provider = 'baidu'
            api_key = os.environ.get('BAIDU_OCR_API_KEY', '')
            secret_key = os.environ.get('BAIDU_OCR_SECRET_KEY', '')

            self._client = OCRClient(
                provider='baidu',
                config={
                    'api_key': api_key,
                    'secret_key': secret_key
                }
            )
            logger.info(f"初始化百度 OCR 客户端")

        elif provider == 'glm':
            # GLM OCR（需要图片上传器）
            self._provider = 'glm'
            api_key = os.environ.get('ZHIPU_API_KEY', '')

            # 创建图片上传器
            uploader_type = os.environ.get('OCR_IMAGE_UPLOADER', 'local').lower()
            self._uploader = self._create_uploader(uploader_type)

            self._client = OCRClient(
                provider='glm',
                config={
                    'api_key': api_key,
                    'image_uploader': self._uploader
                }
            )
            logger.info(f"初始化 GLM OCR 客户端（上传器: {uploader_type}）")

        else:
            raise ValueError(f"不支持的 OCR 提供商: {provider}")

    def _create_uploader(self, uploader_type: str):
        """创建图片上传器"""
        from ocr import create_uploader

        if uploader_type == 'local':
            # 本地上传器
            return create_uploader('local', {
                'upload_dir': os.environ.get('OCR_UPLOAD_DIR', '/tmp/ocr_uploads'),
                'base_url': os.environ.get('OCR_BASE_URL', 'http://localhost:8000/uploads')
            })

        elif uploader_type == 'aliyun':
            # 阿里云 OSS
            return create_uploader('aliyun', {
                'access_key_id': os.environ.get('OSS_ACCESS_KEY_ID', ''),
                'access_key_secret': os.environ.get('OSS_ACCESS_KEY_SECRET', ''),
                'bucket': os.environ.get('OSS_BUCKET', ''),
                'endpoint': os.environ.get('OSS_ENDPOINT', ''),
                'base_path': os.environ.get('OSS_BASE_PATH', 'ocr/')
            })

        elif uploader_type == 'tencent':
            # 腾讯云 COS
            return create_uploader('tencent', {
                'secret_id': os.environ.get('COS_SECRET_ID', ''),
                'secret_key': os.environ.get('COS_SECRET_KEY', ''),
                'bucket': os.environ.get('COS_BUCKET', ''),
                'region': os.environ.get('COS_REGION', 'ap-guangzhou'),
                'base_path': os.environ.get('COS_BASE_PATH', 'ocr/')
            })

        else:
            raise ValueError(f"不支持的图床类型: {uploader_type}")

    def switch_provider(self, new_provider: str):
        """切换 OCR 提供商"""
        logger.info(f"切换 OCR 提供商: {self._provider} -> {new_provider}")

        # 更新环境变量
        os.environ['OCR_PROVIDER'] = new_provider

        # 重新初始化客户端
        self._init_client()

    def recognize_url(self, image_url: str) -> dict:
        """
        识别网络图片

        Args:
            image_url: 图片 URL

        Returns:
            {
                "success": True/False,
                "batch_code": "批次号",
                "confidence": 置信度,
                "text": "全部文本",
                "provider": "baidu/glm",
                "error": "错误信息"
            }
        """
        try:
            result = self._client.recognize_url(image_url)

            return {
                'success': result.get('success', False),
                'batch_code': result.get('batch_code', ''),
                'confidence': result.get('confidence', 0),
                'text': result.get('text', ''),
                'provider': self._provider,
                'raw_data': result.get('raw_data', {})
            }

        except Exception as e:
            logger.error(f"识别图片 URL 异常: {e}")
            return {
                'success': False,
                'batch_code': '',
                'confidence': 0,
                'text': '',
                'provider': self._provider,
                'error': str(e)
            }

    def recognize_base64(self, image_base64: str) -> dict:
        """
        识别 Base64 编码的图片

        Args:
            image_base64: Base64 编码的图片

        Returns:
            同 recognize_url
        """
        try:
            result = self._client.recognize_base64(image_base64)

            return {
                'success': result.get('success', False),
                'batch_code': result.get('batch_code', ''),
                'confidence': result.get('confidence', 0),
                'text': result.get('text', ''),
                'provider': self._provider,
                'raw_data': result.get('raw_data', {})
            }

        except Exception as e:
            logger.error(f"识别 Base64 图片异常: {e}")
            return {
                'success': False,
                'batch_code': '',
                'confidence': 0,
                'text': '',
                'provider': self._provider,
                'error': str(e)
            }

    def recognize_image(self, image_path: str) -> dict:
        """
        识别本地图片

        Args:
            image_path: 图片文件路径

        Returns:
            同 recognize_url
        """
        try:
            result = self._client.recognize_image(image_path)

            return {
                'success': result.get('success', False),
                'batch_code': result.get('batch_code', ''),
                'confidence': result.get('confidence', 0),
                'text': result.get('text', ''),
                'provider': self._provider,
                'raw_data': result.get('raw_data', {})
            }

        except Exception as e:
            logger.error(f"识别本地图片异常: {e}")
            return {
                'success': False,
                'batch_code': '',
                'confidence': 0,
                'text': '',
                'provider': self._provider,
                'error': str(e)
            }

    @property
    def provider(self) -> str:
        """获取当前 OCR 提供商"""
        return self._provider

    @property
    def is_configured(self) -> bool:
        """检查是否已配置"""
        if self._provider == 'baidu':
            return bool(os.environ.get('BAIDU_OCR_API_KEY') and
                       os.environ.get('BAIDU_OCR_SECRET_KEY'))
        elif self._provider == 'glm':
            return bool(os.environ.get('ZHIPU_API_KEY'))
        return False


# 全局单例
_ocr_service_instance = None


def get_ocr_service() -> OCRService:
    """获取 OCR 服务单例"""
    global _ocr_service_instance

    if _ocr_service_instance is None:
        _ocr_service_instance = OCRService()

    return _ocr_service_instance


def reset_ocr_service():
    """重置 OCR 服务单例（用于测试或重新初始化）"""
    global _ocr_service_instance
    _ocr_service_instance = None


if __name__ == '__main__':
    # 测试代码
    import logging

    logging.basicConfig(level=logging.INFO)

    service = get_ocr_service()

    print(f"OCR 提供商: {service.provider}")
    print(f"已配置: {service.is_configured}")

    # 测试识别 URL
    if service.is_configured:
        test_url = "https://cdn.bigmodel.cn/static/logo/introduction.png"
        result = service.recognize_url(test_url)

        print(f"\n识别结果:")
        print(f"  成功: {result['success']}")
        print(f"  批次号: {result['batch_code']}")
        print(f"  置信度: {result['confidence']}")
        if result.get('error'):
            print(f"  错误: {result['error']}")
