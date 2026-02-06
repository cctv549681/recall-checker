#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
火山引擎 TOS 图床上传器

使用 boto3（S3 兼容 API）连接火山引擎 TOS
支持上传文件到火山引擎 TOS，并返回可访问的 URL
"""
import os
import logging
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class VolcengineTOSUploader:
    """火山引擎 TOS 上传器（使用 boto3）"""

    def __init__(self, access_key_id, secret_key, region, bucket, endpoint=None, base_path='ocr/'):
        """
        初始化火山引擎 TOS 上传器

        Args:
            access_key_id: Access Key ID
            secret_key: Secret Access Key
            region: 区域，如 cn-beijing
            bucket: 存储桶名称
            endpoint: 自定义 Endpoint（可选），如 https://tos-cn-beijing.volces.com
            base_path: 上传文件的基准路径
        """
        self.access_key_id = access_key_id
        self.secret_key = secret_key
        self.region = region
        self.bucket = bucket
        self.base_path = base_path

        # 构建 Endpoint
        if endpoint:
            self.endpoint = endpoint
        else:
            self.endpoint = f"https://tos-{region}.volces.com"

        # 公网访问地址
        self.public_url = f"https://{bucket}.{endpoint.replace('https://', '')}"

        # 创建 S3 客户端（TOS S3 兼容）
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_key,
            endpoint_url=self.endpoint,
            region_name=region,
            config=Config(
                signature_version='s3v4',  # TOS 支持 v4 签名
                max_pool_connections=50,
                retries={'max_attempts': 3}
            )
        )

        logger.info(f"火山引擎 TOS 上传器初始化成功: bucket={bucket}, region={region}")

    def _get_full_object_name(self, object_name):
        """获取完整的对象名称（包含基准路径）"""
        if self.base_path and not object_name.startswith(self.base_path):
            object_name = f"{self.base_path}{object_name}"
        return object_name

    def upload_file(self, file_path, object_name=None, content_type=None):
        """
        上传文件到火山引擎 TOS

        Args:
            file_path: 本地文件路径
            object_name: 对象名称（可选，默认使用文件名）
            content_type: 内容类型（可选）

        Returns:
            dict: {
                'success': bool,
                'url': str,
                'object_name': str,
                'error': str
            }
        """
        try:
            # 获取文件名
            if not object_name:
                object_name = os.path.basename(file_path)

            # 添加基准路径
            full_object_name = self._get_full_object_name(object_name)

            # 检测内容类型
            if not content_type:
                content_type = self._guess_content_type(file_path)

            # 上传文件
            logger.info(f"上传文件到 TOS: {file_path} -> {full_object_name}")
            self.s3_client.upload_file(
                file_path,
                self.bucket,
                full_object_name,
                ExtraArgs={
                    'ContentType': content_type,
                    'Metadata': {
                        'uploaded-by': 'recall-checker-api'
                    }
                }
            )

            # 构建访问 URL
            url = f"{self.public_url}/{self._url_encode(full_object_name)}"

            return {
                'success': True,
                'url': url,
                'object_name': full_object_name
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"上传文件失败 (ClientError): {error_code} - {error_message}")
            return {
                'success': False,
                'error': f"{error_code}: {error_message}"
            }
        except Exception as e:
            logger.error(f"上传文件失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def upload_bytes(self, data, object_name, content_type=None):
        """
        上传字节数据到火山引擎 TOS

        Args:
            data: 字节数据
            object_name: 对象名称
            content_type: 内容类型（可选）

        Returns:
            dict: {
                'success': bool,
                'url': str,
                'object_name': str,
                'error': str
            }
        """
        try:
            # 添加基准路径
            full_object_name = self._get_full_object_name(object_name)

            # 检测内容类型
            if not content_type:
                content_type = self._guess_content_type_from_name(object_name)

            # 上传数据
            logger.info(f"上传字节数据到 TOS: {len(data)} bytes -> {full_object_name}")
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=full_object_name,
                Body=data,
                ContentType=content_type,
                Metadata={
                    'uploaded-by': 'recall-checker-api'
                }
            )

            # 构建访问 URL
            url = f"{self.public_url}/{self._url_encode(full_object_name)}"

            return {
                'success': True,
                'url': url,
                'object_name': full_object_name
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"上传数据失败 (ClientError): {error_code} - {error_message}")
            return {
                'success': False,
                'error': f"{error_code}: {error_message}"
            }
        except Exception as e:
            logger.error(f"上传数据失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def delete_file(self, object_name):
        """
        删除火山引擎 TOS 中的文件

        Args:
            object_name: 对象名称

        Returns:
            dict: {
                'success': bool,
                'error': str
            }
        """
        try:
            # 添加基准路径
            full_object_name = self._get_full_object_name(object_name)

            # 删除文件
            logger.info(f"删除 TOS 文件: {full_object_name}")
            self.s3_client.delete_object(
                Bucket=self.bucket,
                Key=full_object_name
            )

            return {
                'success': True
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"删除文件失败 (ClientError): {error_code} - {error_message}")
            return {
                'success': False,
                'error': f"{error_code}: {error_message}"
            }
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_file_url(self, object_name, expires=3600):
        """
        获取文件的访问 URL

        Args:
            object_name: 对象名称
            expires: 过期时间（秒）

        Returns:
            str: 文件访问 URL
        """
        # 添加基准路径
        full_object_name = self._get_full_object_name(object_name)

        # 如果存储桶是公开读的，直接返回公共 URL
        return f"{self.public_url}/{self._url_encode(full_object_name)}"

    def _guess_content_type(self, file_path):
        """根据文件路径猜测内容类型"""
        import mimetypes
        mimetypes.init()
        content_type, encoding = mimetypes.guess_type(file_path)
        return content_type or 'application/octet-stream'

    def _guess_content_type_from_name(self, object_name):
        """根据对象名称猜测内容类型"""
        import mimetypes
        mimetypes.init()
        content_type, encoding = mimetypes.guess_type(object_name)
        return content_type or 'application/octet-stream'

    def _url_encode(self, string):
        """URL 编码"""
        from urllib.parse import quote
        return quote(string, safe='/')


def create_volcengine_uploader():
    """
    从环境变量创建火山引擎 TOS 上传器

    Returns:
        VolcengineTOSUploader: 上传器实例，如果配置不全则返回 None
    """
    access_key_id = os.getenv('VOLCENGINE_ACCESS_KEY_ID')
    secret_key = os.getenv('VOLCENGINE_SECRET_KEY')
    region = os.getenv('VOLCENGINE_REGION')
    bucket = os.getenv('VOLCENGINE_BUCKET')
    endpoint = os.getenv('VOLCENGINE_ENDPOINT')
    base_path = os.getenv('VOLCENGINE_BASE_PATH', 'ocr/')

    # 检查必需的配置
    if not all([access_key_id, secret_key, region, bucket]):
        logger.warning("火山引擎 TOS 配置不全")
        return None

    return VolcengineTOSUploader(
        access_key_id=access_key_id,
        secret_key=secret_key,
        region=region,
        bucket=bucket,
        endpoint=endpoint,
        base_path=base_path
    )
