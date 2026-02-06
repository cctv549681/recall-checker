#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 API 服务器的 OCR 功能
"""
import requests
import base64
import sys

API_BASE_URL = "http://localhost:5001"


def test_health():
    """测试健康检查"""
    print("\n" + "=" * 70)
    print("测试 1: 健康检查")
    print("=" * 70)

    try:
        resp = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        data = resp.json()
        print(f"✅ 健康检查成功")
        print(f"   状态: {data.get('status')}")
        print(f"   时间: {data.get('timestamp')}")
        return True
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False


def test_ocr_status():
    """测试 OCR 状态"""
    print("\n" + "=" * 70)
    print("测试 2: OCR 服务状态")
    print("=" * 70)

    try:
        resp = requests.get(f"{API_BASE_URL}/api/ocr/status", timeout=5)
        data = resp.json()

        print(f"✅ OCR 状态查询成功")
        print(f"   可用: {data['data']['available']}")
        print(f"   提供商: {data['data']['provider']}")
        print(f"   已配置: {data['data']['configured']}")
        print(f"   上传器: {data['data'].get('uploader', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ OCR 状态查询失败: {e}")
        return False


def test_ocr_url():
    """测试 OCR URL 识别"""
    print("\n" + "=" * 70)
    print("测试 3: OCR URL 识别")
    print("=" * 70)

    # 测试图片 URL（智谱官方示例）
    test_url = "https://cdn.bigmodel.cn/static/logo/introduction.png"

    try:
        resp = requests.post(
            f"{API_BASE_URL}/api/ocr",
            json={"image_url": test_url},
            timeout=30
        )
        data = resp.json()

        if data.get("success"):
            print(f"✅ OCR URL 识别成功")
            print(f"   批次号: {data['data']['batch_code']}")
            print(f"   置信度: {data['data']['confidence']}")
            print(f"   提供商: {data['data']['provider']}")
            print(f"   消息: {data['message']}")
            return True
        else:
            print(f"❌ OCR URL 识别失败: {data.get('message')}")
            return False
    except Exception as e:
        print(f"❌ OCR URL 识别异常: {e}")
        return False


def test_ocr_base64():
    """测试 OCR Base64 识别"""
    print("\n" + "=" * 70)
    print("测试 4: OCR Base64 识别")
    print("=" * 70)

    # 创建简单的 Base64 图片（1x1 白色 PNG）
    white_png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z/C/HgAGgwJ/lK3Q6wAAAABJRU5ErkJggg=="

    try:
        resp = requests.post(
            f"{API_BASE_URL}/api/ocr",
            json={"image_base64": white_png_base64},
            timeout=30
        )
        data = resp.json()

        if data.get("success"):
            print(f"✅ OCR Base64 识别成功")
            print(f"   批次号: {data['data']['batch_code']}")
            print(f"   置信度: {data['data']['confidence']}")
            print(f"   提供商: {data['data']['provider']}")
            return True
        else:
            print(f"❌ OCR Base64 识别失败: {data.get('message')}")
            return False
    except Exception as e:
        print(f"❌ OCR Base64 识别异常: {e}")
        return False


def test_ocr_switch():
    """测试切换 OCR 提供商"""
    print("\n" + "=" * 70)
    print("测试 5: 切换 OCR 提供商")
    print("=" * 70)

    try:
        # 切换到百度
        resp = requests.post(
            f"{API_BASE_URL}/api/ocr/switch",
            json={"provider": "baidu"},
            timeout=5
        )
        data = resp.json()

        if data.get("success"):
            print(f"✅ 切换到百度 OCR 成功")
            print(f"   提供商: {data['data']['provider']}")
            print(f"   已配置: {data['data']['configured']}")
        else:
            print(f"❌ 切换失败: {data.get('message')}")
            return False

        # 切换到 GLM
        resp = requests.post(
            f"{API_BASE_URL}/api/ocr/switch",
            json={"provider": "glm"},
            timeout=5
        )
        data = resp.json()

        if data.get("success"):
            print(f"✅ 切换到 GLM OCR 成功")
            print(f"   提供商: {data['data']['provider']}")
            print(f"   已配置: {data['data']['configured']}")
            return True
        else:
            print(f"❌ 切换失败: {data.get('message')}")
            return False

    except Exception as e:
        print(f"❌ 切换 OCR 提供商异常: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("OCR API 测试")
    print("=" * 70)
    print(f"API 地址: {API_BASE_URL}")
    print("提示: 请确保 API 服务器已启动（python api_server.py）")

    results = []

    # 运行测试
    results.append(("健康检查", test_health()))
    results.append(("OCR 状态", test_ocr_status()))
    results.append(("OCR URL 识别", test_ocr_url()))
    results.append(("OCR Base64 识别", test_ocr_base64()))
    results.append(("切换 OCR 提供商", test_ocr_switch()))

    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:20s} {status}")

    print(f"\n通过: {passed}/{total}")

    if passed == total:
        print("✅ 所有测试通过")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
