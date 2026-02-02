#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Abbott召回数据爬虫 - 解析CBS News提供的PDF批次号列表
"""
import PyPDF2
import requests
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
import sys
import re

# 添加 scraper 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.feishu_config import APP_ID, APP_SECRET, APP_TOKEN, TABLE_ID


class AbbottScraper:
    """Abbott召回数据爬虫"""

    def __init__(self):
        self.base_url = "https://open.feishu.cn/open-apis"
        self.feishu_token = None
        self.feishu_token_expire = 0
        self.pdf_url = "https://www.cbsnews.com/htdocs/pdf/SimilacLotList.pdf"

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

    def download_pdf(self, pdf_path: str = "/tmp/SimilacLotList.pdf") -> bool:
        """
        下载 Abbott 召回批次号 PDF

        Args:
            pdf_path: 本地保存路径

        Returns:
            是否下载成功
        """
        print(f"\n下载 PDF: {self.pdf_url}")

        try:
            resp = requests.get(self.pdf_url, timeout=30)
            resp.raise_for_status()

            with open(pdf_path, 'wb') as f:
                f.write(resp.content)

            print(f"✅ PDF 下载成功: {pdf_path}")
            return True

        except Exception as e:
            print(f"❌ PDF 下载失败: {e}")
            return False

    def parse_pdf(self, pdf_path: str = "/tmp/SimilacLotList.pdf") -> List[Dict[str, Any]]:
        """
        解析 PDF 提取批次号数据

        Args:
            pdf_path: PDF 文件路径

        Returns:
            产品列表
        """
        print(f"\n解析 PDF: {pdf_path}")

        products = []

        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)

                for page_num, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    products.extend(self._parse_page_text(text, page_num))

            print(f"✅ 解析完成，共 {len(products)} 条记录")
            return products

        except Exception as e:
            print(f"❌ PDF 解析失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _parse_page_text(self, text: str, page_num: int) -> List[Dict[str, Any]]:
        """
        解析单页文本

        PDF 格式示例：
        Product Description Lot Number
        Similac Advance LCP with Iron Powder 25.7 oz 57713T260
        Similac Advance LCP with Iron Powder 25.7 oz 57713T261
        """
        products = []

        # 跳过标题行
        lines = text.split('\n')

        for line in lines:
            line = line.strip()

            # 跳过空行、页眉、页脚
            if not line:
                continue
            if 'Abbott Voluntarily Recalls' in line:
                continue
            if '© 2010 Abbott Laboratories' in line:
                continue
            if 'Page' in line and 'of 38' in line:
                continue
            if 'To search for your Lot number' in line:
                continue
            if 'CTRL + F' in line:
                continue

            # 提取批次号（最后一部分，通常是8-10位数字字母混合）
            # 批次号格式：以数字开头，包含字母和数字，如 57713T260
            parts = line.rsplit(maxsplit=1)
            if len(parts) < 2:
                continue

            lot_number = parts[-1].strip()

            # 验证批次号格式（至少6位，以数字开头）
            if len(lot_number) < 6:
                continue
            if not lot_number[0].isdigit():
                continue

            # 提取产品描述（批次号前面的部分）
            product_desc = parts[0].strip()

            # 提取产品名称和规格
            product_name, pack_size = self._parse_product_desc(product_desc)

            products.append({
                'product_name': product_name,
                'pack_size': pack_size,
                'batch_code': lot_number,
                'page_num': page_num
            })

        return products

    def _parse_product_desc(self, desc: str) -> tuple:
        """
        解析产品描述，提取产品名称和规格

        示例：
        - "Similac Advance LCP with Iron Powder 25.7 oz" -> ("Similac Advance LCP with Iron Powder", "25.7 oz")
        - "Go & Grow Soy Powder 24 oz" -> ("Go & Grow Soy Powder", "24 oz")
        """
        # 查找规格（通常在末尾，如 "25.7 oz", "12.9 oz", "34 oz"）
        # 正则匹配数字 + oz
        match = re.search(r'(\d+\.?\d*)\s*oz\s*$', desc, re.IGNORECASE)

        if match:
            pack_size = match.group(0)
            product_name = desc[:match.start()].strip()
        else:
            # 没有规格信息
            pack_size = ""
            product_name = desc

        return product_name, pack_size

    def format_for_feishu(self, products: List[Dict[str, Any]], source_url: str) -> List[Dict[str, Any]]:
        """
        格式化产品数据为飞书记录格式

        注意：Abbott PDF 没有有效期信息，召回原因是 Cronobacter sakazakii 和 Salmonella Newport
        """
        records = []

        for product in products:
            # 按产品名称和规格分组，批次号用逗号分隔
            product_key = f"{product['product_name']}|{product['pack_size']}"

            record = {
                "brand": "雅培 Abbott",
                "brand_en": "Abbott",
                "product_name": product['product_name'],
                "sub_brand": self._extract_sub_brand(product['product_name']),
                "batch_codes": product['batch_code'],
                "pack_size": product['pack_size'],
                "best_before": None,  # PDF 中没有有效期信息
                "region": "US",
                "recall_reason": "Cronobacter sakazakii 和 Salmonella Newport 污染风险",
                "risk_level": "高",
                "source_url": {"link": source_url},
                "source_type": "媒体PDF",
                "published_date": int(datetime(2022, 2, 17).timestamp()),  # 2022年2月17日发布召回
                "last_updated": int(datetime.now().timestamp()),
                "status": "已结束"  # 2022年的召回，现在已结束
            }

            records.append(record)

        return records

    def _extract_sub_brand(self, product_name: str) -> str:
        """从产品名称提取子品牌"""
        # Abbott 子品牌列表
        sub_brands = [
            'Similac', 'Alimentum', 'EleCare', 'Go & Grow',
            'Isomil', 'Neosure', 'Total Comfort', 'Early Shield',
            'Sensitive', 'Organic', 'Pro-Total Comfort', 'Special Care'
        ]

        product_upper = product_name.upper()
        for sb in sub_brands:
            if sb.upper() in product_upper:
                return sb

        return ""

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
                        record_id = result["data"]["record"]["record_id"]
                        global_idx = i + j + 1
                        print(f"  {global_idx}. ✅ {record['product_name'][:30]} ({record['batch_codes']})")
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

    def get_statistics(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            'total': len(products),
            'by_product': {},
            'by_size': {},
            'unique_products': len(set(p['product_name'] for p in products)),
            'unique_batches': len(set(p['batch_code'] for p in products))
        }

        # 按产品统计
        for p in products:
            name = p['product_name']
            stats['by_product'][name] = stats['by_product'].get(name, 0) + 1

        # 按规格统计
        for p in products:
            size = p['pack_size'] or 'Unknown'
            stats['by_size'][size] = stats['by_size'].get(size, 0) + 1

        return stats


def print_statistics(stats: Dict[str, Any]):
    """打印统计信息"""
    print("\n" + "=" * 70)
    print("统计信息")
    print("=" * 70)
    print(f"总记录数: {stats['total']}")
    print(f"唯一产品数: {stats['unique_products']}")
    print(f"唯一批次号数: {stats['unique_batches']}")

    print("\n按产品统计（Top 10）:")
    sorted_products = sorted(stats['by_product'].items(), key=lambda x: x[1], reverse=True)
    for i, (name, count) in enumerate(sorted_products[:10], 1):
        print(f"  {i}. {name}: {count}")

    print("\n按规格统计:")
    sorted_sizes = sorted(stats['by_size'].items(), key=lambda x: x[1], reverse=True)
    for i, (size, count) in enumerate(sorted_sizes, 1):
        print(f"  {i}. {size}: {count}")


def main():
    """主函数"""
    print("=" * 70)
    print("Abbott召回数据爬虫")
    print("=" * 70)

    scraper = AbbottScraper()

    # 下载 PDF
    print("\n1. 下载 PDF...")
    if not scraper.download_pdf():
        print("❌ PDF 下载失败，退出")
        return

    # 解析 PDF
    print("\n2. 解析 PDF...")
    products = scraper.parse_pdf()

    if not products:
        print("❌ 未获取到数据")
        return

    # 统计信息
    stats = scraper.get_statistics(products)
    print_statistics(stats)

    source_url = "https://www.cbsnews.com/htdocs/pdf/SimilacLotList.pdf"

    # 格式化数据
    print(f"\n3. 格式化数据...")
    records = scraper.format_for_feishu(products, source_url)

    # 显示预览
    print("\n预览数据（前5条）:")
    for i, r in enumerate(records[:5], 1):
        print(f"  {i}. {r['product_name']}")
        print(f"     规格: {r['pack_size']}, 批次: {r['batch_codes']}")
        print()

    # 确认
    print(f"\n共 {len(records)} 条记录")
    confirm = input(f"\n确认插入? (y/n): ").strip().lower()

    if confirm == 'y':
        print("\n4. 插入飞书表格...")
        count = scraper.insert_to_feishu(records)

        print("\n" + "=" * 70)
        print(f"✅ 爬虫完成！共插入 {count} 条召回记录")
        print("=" * 70)
    else:
        print("\n已取消插入")


if __name__ == "__main__":
    main()
