#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雀巢召回数据爬虫（最终版 v3）
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
import sys
import re

# 添加 scraper 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.feishu_config import APP_ID, APP_SECRET, APP_TOKEN, TABLE_ID


class NestleScraper:
    """雀巢召回数据爬虫"""

    def __init__(self):
        self.base_url = "https://open.feishu.cn/open-apis"
        self.feishu_token = None
        self.feishu_token_expire = 0

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

    def scrape_fsa_alert(self, alert_id: str = "fsa-prin-02-2026-update-1") -> List[Dict[str, Any]]:
        """
        从 FSA 抓取召回信息

        Args:
            alert_id: FSA 警告 ID

        Returns:
            产品列表
        """
        print(f"\n抓取 FSA 警告: {alert_id}")

        url = f"https://www.food.gov.uk/news-alerts/alert/{alert_id}"

        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, 'html.parser')

            # 解析产品信息
            products = self._parse_all_products(soup)

            print(f"✅ 成功抓取，共 {len(products)} 个产品")

            return products

        except Exception as e:
            print(f"❌ 抓取失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _parse_all_products(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        解析所有产品信息

        策略：
        1. 找到所有 caption 标签（产品名称）
        2. 对每个 caption，找下面的 tbody 数据
        """
        products = []

        # 找到所有 caption 标签（包含产品名称）
        captions = soup.find_all('caption')

        for caption in captions:
            text = caption.get_text(strip=True)

            # 只处理包含 SMA 的产品
            if 'SMA' not in text:
                continue

            product_name = text

            # 找到下面的所有 tbody
            tbodies = []
            next_el = caption.find_next_sibling()
            while next_el and next_el.name == 'tbody':
                tbodies.append(next_el)
                next_el = next_el.find_next_sibling()

            if not tbodies:
                continue

            # 从所有 tbody 提取数据
            product_data = self._extract_from_tbodies(tbodies)
            product_data['product_name'] = product_name

            if product_data.get('batch_codes'):
                products.append(product_data)

        return products

    def _extract_from_tbodies(self, tbodies: list) -> Dict[str, Any]:
        """从多个 tbody 提取产品数据"""
        data = {
            'pack_size': '',
            'batch_codes': [],
            'best_before_dates': []
        }

        for tbody in tbodies:
            rows = tbody.find_all('tr')

            if len(rows) < 3:
                continue

            # 行1: Pack size
            pack_size_cell = rows[0].find('td')
            if pack_size_cell:
                ps = pack_size_cell.get_text(strip=True)
                if not data['pack_size']:
                    data['pack_size'] = ps

            # 行2: Batch code
            batch_code_cell = rows[1].find('td')
            if batch_code_cell:
                codes = [c.strip() for c in batch_code_cell.get_text(strip=True).split() if c.strip()]
                data['batch_codes'].extend(codes)

            # 行3: Best before
            best_before_cell = rows[2].find('td')
            if best_before_cell:
                bb = best_before_cell.get_text(strip=True)
                # 只取第一个日期，跳过 Updated 的
                if not data['best_before_dates'] and not bb.startswith('*'):
                    data['best_before_dates'].append(bb)

        # 取第一个日期
        if data['best_before_dates']:
            data['best_before'] = data['best_before_dates'][0]

        return data

    def parse_date(self, date_str: str) -> int:
        """解析日期字符串为时间戳"""
        if not date_str:
            return None

        # 去除 Updated 标记
        date_str = date_str.replace('*Updated ', '').strip()

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
                    dt = datetime(year, month_num, 1)
                    return int(dt.timestamp())

        return None

    def format_for_feishu(self, products: List[Dict[str, Any]], source_url: str) -> List[Dict[str, Any]]:
        """格式化产品数据为飞书记录格式"""
        records = []

        for product in products:
            batch_codes_str = ', '.join(product.get('batch_codes', []))

            record = {
                "brand": "雀巢 Nestlé",
                "brand_en": "Nestlé",
                "product_name": product.get('product_name', ''),
                "sub_brand": self._extract_sub_brand(product.get('product_name', '')),
                "batch_codes": batch_codes_str,
                "pack_size": product.get('pack_size', ''),
                "best_before": self.parse_date(product.get('best_before', '')),
                "region": "UK",
                "recall_reason": "Cereulide毒素",
                "risk_level": "高",
                "source_url": {"link": source_url},
                "source_type": "政府平台",
                "published_date": int(datetime(2026, 1, 6).timestamp()),
                "last_updated": int(datetime.now().timestamp()),
                "status": "召回中"
            }

            records.append(record)

        return records

    def _extract_sub_brand(self, product_name: str) -> str:
        """从产品名称提取子品牌"""
        sub_brands = ['SMA', 'ALFAMINO', 'NAN', 'BEBA']
        for sb in sub_brands:
            if sb in product_name.upper():
                return sb
        return ""

    def insert_to_feishu(self, records: List[Dict[str, Any]]) -> int:
        """将记录插入飞书表格"""
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
        for i, record in enumerate(records, 1):
            data = {"fields": record}

            try:
                resp = requests.post(url, headers=headers, json=data)
                result = resp.json()

                if result.get("code") == 0:
                    record_id = result["data"]["record"]["record_id"]
                    print(f"  {i}. ✅ {record['product_name'][:38]} ({record['pack_size']})")
                    success_count += 1
                else:
                    print(f"  {i}. ❌ {record['product_name'][:38]}: {result.get('msg')}")

            except Exception as e:
                print(f"  {i}. ❌ {record['product_name'][:38]}: {e}")

        print(f"\n✅ 成功插入 {success_count}/{len(records)} 条记录")
        return success_count


def main():
    """主函数"""
    print("=" * 70)
    print("雀巢召回数据爬虫")
    print("=" * 70)

    scraper = NestleScraper()

    # 抓取 FSA 数据
    print("\n1. 抓取 FSA 数据...")
    products = scraper.scrape_fsa_alert()

    if not products:
        print("❌ 未获取到数据")
        return

    source_url = "https://www.food.gov.uk/news-alerts/alert/fsa-prin-02-2026-update-1"

    # 格式化数据
    print(f"\n2. 格式化数据...")
    records = scraper.format_for_feishu(products, source_url)

    # 显示预览
    print("\n预览数据（前5条）:")
    for i, r in enumerate(records[:5], 1):
        print(f"  {i}. {r['product_name']}")
        print(f"     规格: {r['pack_size']}, 批次: {r['batch_codes'][:50]}...")
        print()

    # 确认
    print(f"\n共 {len(records)} 条记录")
    confirm = input(f"\n确认插入? (y/n): ").strip().lower()

    if confirm == 'y':
        print("\n3. 插入飞书表格...")
        count = scraper.insert_to_feishu(records)

        print("\n" + "=" * 70)
        print(f"✅ 爬虫完成！共插入 {count} 条召回记录")
        print("=" * 70)
    else:
        print("\n已取消插入")


if __name__ == "__main__":
    main()
