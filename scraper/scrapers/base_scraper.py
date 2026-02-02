#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
召回数据爬虫基类
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# 添加 scraper 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.feishu_config import APP_ID, APP_SECRET, APP_TOKEN, TABLE_ID


class BaseScraper:
    """召回数据爬虫基类"""

    def __init__(self, brand: str, brand_en: str):
        """
        初始化爬虫

        Args:
            brand: 品牌中文名
            brand_en: 品牌英文名
        """
        self.brand = brand
        self.brand_en = brand_en
        self.base_url = "https://open.feishu.cn/open-apis"
        self.feishu_token = None
        self.feishu_token_expire = 0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def get_feishu_token(self) -> str:
        """获取飞书 tenant_access_token"""
        if self.feishu_token and datetime.now().timestamp() < self.feishu_token_expire:
            return self.feishu_token

        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        resp = requests.post(url, json={
            "app_id": APP_ID,
            "app_secret": APP_SECRET
        })

        result = resp.json()
        if result.get("code") != 0:
            raise Exception(f"获取飞书token失败: {result}")

        self.feishu_token = result["tenant_access_token"]
        self.feishu_token_expire = datetime.now().timestamp() + 7200

        return self.feishu_token

    def fetch_page(self, url: str, timeout: int = 30) -> Optional[str]:
        """
        获取页面内容

        Args:
            url: 页面URL
            timeout: 超时时间（秒）

        Returns:
            页面HTML内容
        """
        try:
            resp = requests.get(url, headers=self.headers, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"❌ 获取页面失败 {url}: {e}")
            return None

    def parse_page(self, html: str) -> BeautifulSoup:
        """解析HTML页面"""
        return BeautifulSoup(html, 'html.parser')

    def scrape(self) -> List[Dict[str, Any]]:
        """
        抓取召回数据（子类需实现）

        Returns:
            产品列表
        """
        raise NotImplementedError("子类需实现 scrape 方法")

    def format_for_feishu(self, products: List[Dict[str, Any]], source_url: str) -> List[Dict[str, Any]]:
        """
        格式化产品数据为飞书记录格式（子类可覆盖）

        Args:
            products: 产品列表
            source_url: 数据源URL

        Returns:
            飞书记录列表
        """
        records = []

        for product in products:
            # 批次号可能是列表，转换为字符串
            batch_codes = product.get('batch_codes', [])
            if isinstance(batch_codes, list):
                batch_codes_str = ', '.join(batch_codes)
            else:
                batch_codes_str = batch_codes

            record = {
                "brand": self.brand,
                "brand_en": self.brand_en,
                "product_name": product.get('product_name', ''),
                "sub_brand": product.get('sub_brand', ''),
                "batch_codes": batch_codes_str,
                "pack_size": product.get('pack_size', ''),
                "best_before": product.get('best_before'),
                "region": product.get('region', ''),
                "recall_reason": product.get('recall_reason', ''),
                "risk_level": product.get('risk_level', '高'),
                "source_url": {"link": source_url},
                "source_type": product.get('source_type', '官网'),
                "published_date": product.get('published_date', int(datetime.now().timestamp())),
                "last_updated": int(datetime.now().timestamp()),
                "status": product.get('status', '召回中')
            }

            records.append(record)

        return records

    def insert_to_feishu(self, records: List[Dict[str, Any]], batch_size: int = 50) -> int:
        """
        将记录插入飞书表格

        Args:
            records: 记录列表
            batch_size: 批量插入的大小

        Returns:
            成功插入的数量
        """
        if not records:
            print("没有记录需要插入")
            return 0

        print(f"\n准备插入 {len(records)} 条记录到飞书...")

        token = self.get_feishu_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        url = f"{self.base_url}/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"

        success_count = 0
        failed_records = []

        # 批量插入
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]

            for j, record in enumerate(batch, 1):
                data = {"fields": record}

                try:
                    resp = requests.post(url, headers=headers, json=data)
                    result = resp.json()

                    if result.get("code") == 0:
                        global_idx = i + j + 1
                        print(f"  {global_idx}. ✅ {record['product_name'][:30]} ({record['batch_codes'][:20]}...)")
                        success_count += 1
                    else:
                        global_idx = i + j + 1
                        print(f"  {global_idx}. ❌ {record['product_name'][:30]}: {result.get('msg')}")
                        failed_records.append(record)

                except Exception as e:
                    global_idx = i + j + 1
                    print(f"  {global_idx}. ❌ {record['product_name'][:30]}: {e}")
                    failed_records.append(record)

        print(f"\n✅ 成功插入 {success_count}/{len(records)} 条记录")

        if failed_records:
            print(f"\n失败的记录数: {len(failed_records)}")

        return success_count

    def parse_date(self, date_str: str) -> Optional[int]:
        """
        解析日期字符串为时间戳

        Args:
            date_str: 日期字符串

        Returns:
            时间戳
        """
        if not date_str:
            return None

        # 尝试解析常见日期格式
        import re

        # 格式1: 2026年1月6日
        match = re.match(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
        if match:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            return int(datetime(year, month, day).timestamp())

        # 格式2: 06 January 2026
        months = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        for month_name, month_num in months.items():
            if month_name in date_str:
                year_match = re.search(r'20\d{2}', date_str)
                if year_match:
                    year = int(year_match.group())
                    return int(datetime(year, month_num, 1).timestamp())

        # 格式3: 2026-01-06
        match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
        if match:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            return int(datetime(year, month, day).timestamp())

        return None

    def show_preview(self, records: List[Dict[str, Any]], limit: int = 5):
        """显示数据预览"""
        print(f"\n数据预览（前{min(limit, len(records))}条）:")
        print("=" * 70)

        for i, r in enumerate(records[:limit], 1):
            print(f"{i}. {r['product_name']}")
            print(f"   品牌: {r['brand']} | 规格: {r['pack_size']}")
            print(f"   批次: {r['batch_codes'][:60]}...")
            print(f"   地区: {r['region']} | 原因: {r['recall_reason'][:40]}...")
            print()
