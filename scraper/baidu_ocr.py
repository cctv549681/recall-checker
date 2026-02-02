#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度OCR集成模块
"""
import requests
import json
import base64
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaiduOCR:
    """百度OCR API封装"""

    def __init__(self, api_key: str = '', secret_key: str = ''):
        """
        初始化百度OCR客户端

        Args:
            api_key: API Key
            secret_key: Secret Key
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None
        self.token_expire = 0

        self.base_url = "https://aip.baidubce.com/oauth/2.0/token"
        self.ocr_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general"

    def get_access_token(self) -> str:
        """
        获取百度OCR访问令牌

        Returns:
            access_token: 访问令牌
        """
        # 如果未配置API Key，返回模拟令牌
        if not self.api_key or not self.secret_key:
            logger.warning("百度OCR API Key未配置，使用模拟令牌")
            return "mock_access_token_for_testing"

        # 检查令牌是否过期
        import time
        now = time.time()
        if self.access_token and now < self.token_expire:
            return self.access_token

        try:
            # 请求新令牌
            params = {
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.secret_key
            }

            resp = requests.post(self.base_url, data=params, timeout=10)
            result = resp.json()

            if "access_token" in result:
                self.access_token = result["access_token"]
                # 令牌有效期30天（减去1小时缓冲）
                self.token_expire = now + 29 * 24 * 3600 - 3600
                logger.info("成功获取百度OCR访问令牌")
                return self.access_token
            else:
                raise Exception(f"获取令牌失败: {result}")

        except Exception as e:
            logger.error(f"获取百度OCR令牌异常: {e}")
            raise

    def ocr_general(self, image_data: str) -> Dict[str, Any]:
        """
        通用文字识别（含位置信息）

        Args:
            image_data: 图片URL或Base64编码

        Returns:
            识别结果：{
                "log_id": "日志ID",
                "result": "识别结果",
                "error_code": "错误码",
                "error_msg": "错误信息"
            }
        """
        try:
            token = self.get_access_token()
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }

            data = {
                "access_token": token,
                "image": image_data,
                "language_type": "CHN_ENG",  # 中英文混合
                "detect_direction": "true",  # 检测图像朝向
                "probability": "true"  # 返回置信度
            }

            resp = requests.post(self.ocr_url, headers=headers, data=data, timeout=10)
            result = resp.json()

            logger.info(f"百度OCR识别完成: {result.get('error_code', 'success')}")

            return result

        except Exception as e:
            logger.error(f"百度OCR识别异常: {e}")
            raise

    def extract_batch_code(self, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        从OCR结果中提取批次号

        批次号格式规则：
        - 长度8-12位
        - 包含数字和大写字母
        - 可能包含特殊字符（如：51450742F1）

        Args:
            ocr_result: 百度OCR返回结果

        Returns:
            {
                "batch_code": 批次号,
                "confidence": 置信度
                "all_candidates": 所有候选批次号
            }
        """
        all_text = ocr_result.get("result", "")
        words_result = all_text.split("\n")

        # 提取所有可能的批次号
        candidates = []

        import re
        batch_pattern = r'[A-Z0-9]{8,12}'

        for line in words_result:
            # 清理文本
            line = line.strip()
            line = line.replace(" ", "").replace("O", "0").replace("I", "1")

            # 查找批次号
            matches = re.findall(batch_pattern, line)

            for match in matches:
                if match not in candidates:
                    candidates.append(match)

        # 按置信度排序（如果OCR返回了置信度信息）
        # 百度通用OCR不返回单个字置信度，使用匹配长度作为排序依据

        # 候选批次号排序：
        # 1. 优先选择长度10-12位的
        # 2. 优先选择以数字开头的
        # 3. 优先选择包含字母F/A/B/L的（常见批次号模式）

        scored_candidates = []
        for candidate in candidates:
            score = 0
            length = len(candidate)

            # 长度评分（10-12位最佳）
            if 10 <= length <= 12:
                score += 3
            elif 8 <= length <= 9:
                score += 2

            # 以数字开头
            if candidate[0].isdigit():
                score += 2

            # 包含常见字母
            if any(c in candidate for c in ['F', 'A', 'B', 'L', 'P', 'R']):
                score += 1

            # 包含混合字符（数字+字母）
            if any(c.isdigit() for c in candidate) and any(c.isalpha() for c in candidate):
                score += 2

            scored_candidates.append({
                "batch_code": candidate,
                "score": score
            })

        # 按分数排序
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)

        # 选择最佳候选
        best_batch = scored_candidates[0]["batch_code"] if scored_candidates else ""
        confidence = min(95, 60 + scored_candidates[0]["score"])  # 基础置信度60% + 分数

        return {
            "batch_code": best_batch,
            "confidence": confidence,
            "all_candidates": [c["batch_code"] for c in scored_candidates[:5]]  # 返回前5个候选
        }


def mock_ocr_result() -> Dict[str, Any]:
    """
    模拟OCR结果（用于测试）

    Returns:
        模拟的OCR结果
    """
    return {
        "log_id": "mock_log_id",
        "result": "51450742F1\n52319722BA",
        "error_code": "0",
        "error_msg": "success"
    }


# 使用示例
if __name__ == "__main__":
    # 测试代码
    ocr = BaiduOCR()

    # 获取访问令牌（需要API Key）
    # token = ocr.get_access_token()

    # 识别图片
    # result = ocr.ocr_general("base64_image_data")

    # 提取批次号
    # batch_info = ocr.extract_batch_code(result)
    # print(f"批次号: {batch_info['batch_code']}, 置信度: {batch_info['confidence']}")

    # 模拟OCR（用于测试）
    mock_result = mock_ocr_result()
    batch_info = ocr.extract_batch_code(mock_result)
    print(f"模拟识别结果: {batch_info}")
