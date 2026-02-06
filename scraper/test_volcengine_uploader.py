#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
火山引擎 TOS 图床上传器测试
"""
import os
import sys
from pathlib import Path

# 添加 scraper 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.volcengine_uploader import create_volcengine_uploader


def test_volcengine_uploader():
    """测试火山引擎 TOS 上传器"""
    print("=== 火山引擎 TOS 图床上传器测试 ===\n")

    # 从环境变量创建上传器
    uploader = create_volcengine_uploader()

    if not uploader:
        print("❌ 火山引擎 TOS 上传器未配置")
        print("\n请设置以下环境变量：")
        print("  - VOLCENGINE_ACCESS_KEY_ID")
        print("  - VOLCENGINE_SECRET_KEY")
        print("  - VOLCENGINE_REGION")
        print("  - VOLCENGINE_BUCKET")
        print("\n可选：")
        print("  - VOLCENGINE_ENDPOINT")
        return False

    print(f"✅ 火山引擎 TOS 上传器初始化成功")
    print(f"  Bucket: {uploader.bucket}")
    print(f"  Region: {uploader.region}")
    print(f"  Endpoint: {uploader.endpoint}")
    print(f"  公网 URL: {uploader.public_url}")
    print()

    # 测试上传字节数据
    print("--- 测试上传字节数据 ---")
    test_data = b"Hello, Volcengine TOS!"
    test_object_name = f"test/{os.getpid()}.txt"

    result = uploader.upload_bytes(
        data=test_data,
        object_name=test_object_name,
        content_type='text/plain'
    )

    if result['success']:
        print(f"✅ 上传成功")
        print(f"  对象名称: {result['object_name']}")
        print(f"  访问 URL: {result['url']}")
        print()
    else:
        print(f"❌ 上传失败: {result['error']}")
        return False

    # 测试获取文件 URL
    print("--- 测试获取文件 URL ---")
    url = uploader.get_file_url(test_object_name)
    print(f"✅ 文件 URL: {url}")
    print()

    # 测试删除文件
    print("--- 测试删除文件 ---")
    delete_result = uploader.delete_file(test_object_name)
    if delete_result['success']:
        print(f"✅ 删除成功")
    else:
        print(f"❌ 删除失败: {delete_result['error']}")
        return False

    print()
    print("=== 所有测试通过 ===")
    return True


if __name__ == '__main__':
    success = test_volcengine_uploader()
    sys.exit(0 if success else 1)
