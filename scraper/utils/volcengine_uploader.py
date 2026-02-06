#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
火山引擎 TOS 图床上传器

支持上传文件到火山引擎 TOS，并返回可访问的 URL
"""
import os
import hashlib
import hmac
import urllib.parse
from datetime import datetime
import requests


class VolcengineTOSUploader:
    """火山引擎 TOS 上传器"""

    def __init__(self, access_key_id, secret_key, region, bucket, endpoint=None):
        """
        初始化火山引擎 TOS 上传器

        Args:
            access_key_id: Access Key ID
            secret_key: Secret Access Key
            region: 区域，如 cn-beijing
            bucket: 存储桶名称
            endpoint: 自定义 Endpoint（可选）
        """
        self.access_key_id = access_key_id
        self.secret_key = secret_key
        self.region = region
        self.bucket = bucket

        # 构建 Endpoint
        if endpoint:
            self.endpoint = endpoint
        else:
            self.endpoint = f"tos-{region}.volces.com"

        # 公网访问地址
        self.public_url = f"https://{bucket}.{self.endpoint}"
        self.session = requests.Session()

    def _sign_request(self, method, uri, headers, params=None, body=None):
        """
        签名请求（V4 签名算法）

        Args:
            method: HTTP 方法
            uri: 请求 URI
            headers: 请求头
            params: 查询参数
            body: 请求体

        Returns:
            签名后的 headers
        """
        # 实现火山引擎 TOS 的签名逻辑
        # 简化版本，实际使用时需要参考官方文档
        return headers

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
            # 读取文件
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # 计算文件大小
            file_size = len(file_data)

            # 生成对象名称
            if not object_name:
                object_name = os.path.basename(file_path)

            # 构建请求 URL
            url = f"{self.public_url}/{urllib.parse.quote(object_name)}"

            # 设置请求头
            headers = {
                'Content-Type': content_type or 'application/octet-stream',
                'Content-Length': str(file_size),
                'Host': f"{self.bucket}.{self.endpoint}",
                'x-tos-date': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'),
            }

            # 签名
            headers = self._sign_request('PUT', f"/{object_name}", headers, body=file_data)

            # 上传文件
            response = self.session.put(url, data=file_data, headers=headers, timeout=30)

            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'url': url,
                    'object_name': object_name
                }
            else:
                return {
                    'success': False,
                    'error': f'上传失败: {response.status_code} - {response.text}'
                }

        except Exception as e:
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
            # 计算数据大小
            data_size = len(data)

            # 构建请求 URL
            url = f"{self.public_url}/{urllib.parse.quote(object_name)}"

            # 设置请求头
            headers = {
                'Content-Type': content_type or 'application/octet-stream',
                'Content-Length': str(data_size),
                'Host': f"{self.bucket}.{self.endpoint}",
                'x-tos-date': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'),
            }

            # 签名
            headers = self._sign_request('PUT', f"/{object_name}", headers, body=data)

            # 上传数据
            response = self.session.put(url, data=data, headers=headers, timeout=30)

            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'url': url,
                    'object_name': object_name
                }
            else:
                return {
                    'success': False,
                    'error': f'上传失败: {response.status_code} - {response.text}'
                }

        except Exception as e:
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
            # 构建请求 URL
            url = f"{self.public_url}/{urllib.parse.quote(object_name)}"

            # 设置请求头
            headers = {
                'Host': f"{self.bucket}.{self.endpoint}",
                'x-tos-date': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'),
            }

            # 签名
            headers = self._sign_request('DELETE', f"/{object_name}", headers)

            # 删除文件
            response = self.session.delete(url, headers=headers, timeout=30)

            if response.status_code in [200, 204]:
                return {
                    'success': True
                }
            else:
                return {
                    'success': False,
                    'error': f'删除失败: {response.status_code} - {response.text}'
                }

        except Exception as e:
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
        # 如果存储桶是公开读的，直接返回公共 URL
        return f"{self.public_url}/{urllib.parse.quote(object_name)}"


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

    # 检查必需的配置
    if not all([access_key_id, secret_key, region, bucket]):
        return None

    return VolcengineTOSUploader(
        access_key_id=access_key_id,
        secret_key=secret_key,
        region=region,
        bucket=bucket,
        endpoint=endpoint
    )
