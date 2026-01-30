#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度OCR集成工具
提供图片识别、批次号提取等功能
"""
import requests
import base64
from typing import Dict, Optional, List, Any


class BaiduOCRClient:
    """百度OCR客户端"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.access_token = None
        self.expire_time = 0

        # API 地址
        self.ocr_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"

    def get_token(self) -> str:
        """获取访问令牌"""
        # 检查缓存
        if self.access_token and datetime.now().timestamp() < self.expire_time:
            return self.access_token

        # 获取新令牌
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_key
        }

        try:
            resp = requests.post(url, data=params)
            result = resp.json()

            if "access_token" in result:
                self.access_token = result["access_token"]
                # 缓存30天
                self.expire_time = datetime.now().timestamp() + 2592000
                return self.access_token
            else:
                raise Exception(f"获取令牌失败: {result}")

        except Exception as e:
            print(f"❌ 获取令牌异常: {e}")
            raise e

    def recognize_text(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        识别图片中的文字
        
        Args:
            image_path: 图片路径
        
        Returns:
            识别结果（包含文字和置信度）
        """
        token = self.get_token()

        # 读取图片
        try:
            with open(image_path, 'rb') as f:
                img_data = f.read()

            # Base64编码
            img_base64 = base64.b64encode(img_data).decode()

            # 请求参数
            data = {
                "image": img_base64,
                "language_type": "CHN_ENG",
                "detect_direction": "true",
                "probability": "true"
            }

            # 发送请求
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {token}"
            }

            resp = requests.post(self.ocr_url, data=data, headers=headers)
            result = resp.json()

            if "error_code" in result and result["error_code"] != 0:
                error_msg = result.get("error_msg", "未知错误")
                print(f"❌ OCR识别失败: {error_msg}")
                return None

            # 解析结果
            words_result = result.get("words_result", [])

            # 提取批次号
            batch_code = self.extract_batch_code(words_result)

            return {
                "success": True,
                "batch_code": batch_code,
                "confidence": self.calc_confidence(words_result),
                "all_text": " ".join([w.get("words") for w in words_result]),
                "word_count": len(words_result)
            }

        except FileNotFoundError:
            print(f"❌ 文件不存在: {image_path}")
            return None
        except Exception as e:
            print(f"❌ OCR识别异常: {e}")
            return None

    def recognize_url(self, image_url: str) -> Optional[Dict[str, Any]]:
        """
        通过URL识别图片
        
        Args:
            image_url: 图片URL
        
        Returns:
            识别结果
        """
        token = self.get_token()

        # 请求参数
        data = {
            "url": image_url,
            "language_type": "CHN_ENG",
            "detect_direction": "true",
            "probability": "true"
        }

        # 发送请求
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {token}"
        }

        resp = requests.post(self.ocr_url, data=data, headers=headers)
        result = resp.json()

        if "error_code" in result and result["error_code"] != 0:
            error_msg = result.get("error_msg", "未知错误")
            print(f"❌ OCR识别失败: {error_msg}")
            return None

        # 解析结果
        words_result = result.get("words_result", [])

        # 提取批次号
        batch_code = self.extract_batch_code(words_result)

        return {
            "success": True,
            "batch_code": batch_code,
            "confidence": self.calc_confidence(words_result),
            "all_text": " ".join([w.get("words") for w in words_result]),
            "word_count": len(words_result)
        }

    def extract_batch_code(self, words_result: List[Dict]) -> str:
        """
        从识别结果中提取批次号
        
        Args:
            words_result: 识别的词语列表
        
        Returns:
            批次号字符串
        """
        if not words_result:
            return ""

        # 批次号模式（雀巢：6-12位数字字母）
        # 例如：51450742F1, 52319722BA

        # 收集所有可能的批次号
        candidates = []

        for word_data in words_result:
            word = word_data.get("words", "").strip()
            
            # 跳过太短或太长的词
            if len(word) < 4 or len(word) > 12:
                continue

            # 检查是否符合批次号格式
            if self.is_batch_code(word):
                candidates.append(word)

        # 如果没有找到，尝试组合
        if not candidates:
            # 合并相邻的词
            for i in range(len(words_result) - 1):
                word1 = words_result[i].get("words", "")
                word2 = words_result[i + 1].get("words", "")
                
                if self.is_batch_code(word1) and self.is_batch_code(word2):
                    combined = word1 + word2
                    if len(combined) <= 12:
                        candidates.append(combined)

        # 返回最可能的一个
        if candidates:
            # 优先选择最长的（包含更多信息的）
            return max(candidates, key=len)
        
        return ""

    def is_batch_code(self, text: str) -> bool:
        """
        判断是否符合批次号格式
        
        Args:
            text: 待检查的文本
        
        Returns:
            是否是批次号
        """
        # 批次号特征：
        # 1. 数字和字母的组合
        # 2. 长度 6-12 位
        # 3. 可能包含大写字母
        # 4. 可能包含特殊字符（F、G、Z 等）

        # 检查长度
        if not (6 <= len(text) <= 12):
            return False

        # 检查是否包含至少一个数字
        if not any(char.isdigit() for char in text):
            return False

        # 检查是否包含至少一个字母
        if not any(char.isalpha() for char in text):
            return False

        return True

    def calc_confidence(self, words_result: List[Dict]) -> float:
        """
        计算平均置信度
        
        Args:
            words_result: 识别的词语列表
        
        Returns:
            置信度（0-100）
        """
        if not words_result:
            return 0.0

        total_confidence = 0.0
        word_count = 0

        for word_data in words_result:
            confidence = word_data.get("probability", 0)
            total_confidence += confidence
            word_count += 1

        if word_count > 0:
            return (total_confidence / word_count) * 100

        return 0.0


# 测试代码
if __name__ == "__main__":
    # 测试配置（需要在项目中替换真实的 API Key）
    API_KEY = "YOUR_BAIDU_OCR_API_KEY"

    client = BaiduOCRClient(API_KEY)

    # 测试1：模拟识别
    print("=" * 70)
    print("百度 OCR 测试")
    print("=" * 70)

    # 测试提取批次号逻辑
    test_words = [
        {"words": "51450742", "probability": 0.95},
        {"words": "F1", "probability": 0.98},
        {"words": "2026", "probability": 0.99}
    ]

    print("\n测试批次号提取:")
    print(f"输入: {[w['words'] for w in test_words]}")
    result = client.extract_batch_code(test_words)
    print(f"输出: {result}")

    print("\n" + "=" * 70)
    print("✅ 测试完成")
    print("使用说明:")
    print("1. 替换 API_KEY 为真实的百度 OCR API Key")
    print("2. 在小程序中调用 recognize_text() 或 recognize_url()")
    print("3. 解析返回的 batch_code")
    print("=" * 70)
