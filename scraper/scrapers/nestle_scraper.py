"""
雀巢召回信息爬虫
数据源：
1. 雀巢UK召回页面：https://www.nestle.co.uk/en-gb/media/sma-infant-formula-follow-on-formula-recall
2. FSA召回公告：https://www.food.gov.uk/news-alerts/alert/fsa-prin-02-2026-update-1
"""

import asyncio
import re
import json
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page
from bs4 import BeautifulSoup
import aiohttp


class NestleRecallScraper:
    """雀巢召回信息爬虫"""

    def __init__(self):
        self.base_urls = [
            "https://www.nestle.co.uk/en-gb/media/sma-infant-formula-follow-on-formula-recall",
        ]
        self.gov_urls = [
            "https://www.food.gov.uk/news-alerts/alert/fsa-prin-02-2026-update-1",
        ]

    async def scrape_all(self) -> List[Dict]:
        """爬取所有召回信息"""
        all_recalls = []

        # 爬取雀巢官网
        recalls = await self.scrape_nestle_uk()
        all_recalls.extend(recalls)

        # 爬取政府平台
        recalls = await self.scrape_fsa()
        all_recalls.extend(recalls)

        # 去重
        all_recalls = self.deduplicate(all_recalls)

        return all_recalls

    async def scrape_nestle_uk(self) -> List[Dict]:
        """爬取雀巢UK召回页面"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            recalls = []

            for url in self.base_urls:
                try:
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                    content = await page.content()

                    # 解析批次号信息
                    batch_codes = self.extract_batch_codes(content)

                    if batch_codes:
                        recalls.append({
                            "brand": "雀巢 Nestlé",
                            "brand_en": "Nestlé",
                            "source_url": url,
                            "source_type": "官网",
                            "batch_codes": batch_codes,
                            "scraped_at": datetime.now().isoformat(),
                        })

                except Exception as e:
                    print(f"爬取 {url} 失败: {e}")

            await browser.close()

        return recalls

    async def scrape_fsa(self) -> List[Dict]:
        """爬取FSA召回公告"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            recalls = []

            for url in self.gov_urls:
                try:
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                    content = await page.content()

                    # 使用BeautifulSoup解析
                    soup = BeautifulSoup(content, 'lxml')

                    # 提取所有产品信息
                    products = self.extract_products_from_fsa(soup)

                    recalls.extend(products)

                except Exception as e:
                    print(f"爬取FSA页面失败: {e}")

            await browser.close()

        return recalls

    def extract_batch_codes(self, html: str) -> List[str]:
        """从HTML中提取批次号"""
        batch_codes = []

        # FSA页面的批次号格式: 51450742F1, 52319722BA 等
        pattern = r'\b\d{8}[A-Z0-9]{1,2}\b'

        matches = re.findall(pattern, html)
        batch_codes.extend(matches)

        # 去重
        batch_codes = list(set(batch_codes))

        return batch_codes

    def extract_products_from_fsa(self, soup) -> List[Dict]:
        """从FSA页面提取产品信息"""
        products = []

        # 查找所有产品部分
        # FSA页面结构: 每个产品有 h3 标题 + 表格
        headings = soup.find_all('h3')

        for heading in headings:
            # 获取产品名称
            product_name = heading.get_text().strip()

            # 查找下一个表格
            table = heading.find_next('table')
            if not table:
                continue

            # 解析表格
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 2:
                    # 第一列通常是字段名，第二列是值
                    field = cols[0].get_text().strip()
                    value = cols[1].get_text().strip()

                    # 查找批次号
                    if 'Batch code' in field:
                        # 批次号可能用逗号分隔
                        batch_codes = [b.strip() for b in value.split(',')]

                        # 提取有效期
                        best_before = self.extract_best_before(row)

                        products.append({
                            "brand": "雀巢 Nestlé",
                            "brand_en": "Nestlé",
                            "product_name": product_name,
                            "batch_codes": batch_codes,
                            "best_before": best_before,
                            "source_url": "https://www.food.gov.uk/news-alerts/alert/fsa-prin-02-2026-update-1",
                            "source_type": "政府平台",
                            "scraped_at": datetime.now().isoformat(),
                        })

        return products

    def extract_best_before(self, row) -> Optional[str]:
        """从行中提取有效期"""
        cols = row.find_all(['td', 'th'])
        for col in cols:
            text = col.get_text().strip()
            # 查找包含"Best before"或"有效期"的列
            if 'Best before' in text or '有效期' in text:
                # 查找下一个单元格的值
                idx = cols.index(col)
                if idx + 1 < len(cols):
                    return cols[idx + 1].get_text().strip()

        return None

    def deduplicate(self, recalls: List[Dict]) -> List[Dict]:
        """去重"""
        seen = set()
        unique_recalls = []

        for recall in recalls:
            # 使用批次号组合作为唯一标识
            batch_codes_tuple = tuple(sorted(recall.get('batch_codes', [])))
            key = (recall.get('product_name', ''), batch_codes_tuple)

            if key not in seen:
                seen.add(key)
                unique_recalls.append(recall)

        return unique_recalls


async def main():
    """测试爬虫"""
    scraper = NestleRecallScraper()

    print("开始爬取雀巢召回信息...")
    recalls = await scraper.scrape_all()

    print(f"\n共爬取到 {len(recalls)} 条召回信息")
    for i, recall in enumerate(recalls, 1):
        print(f"\n{i}. 产品: {recall.get('product_name', 'N/A')}")
        print(f"   批次号: {', '.join(recall.get('batch_codes', []))}")
        print(f"   有效期: {recall.get('best_before', 'N/A')}")
        print(f"   数据源: {recall.get('source_url', 'N/A')}")

    # 保存到JSON
    output_file = "/root/clawd/recall-checker/data/nestle_recalls.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(recalls, f, ensure_ascii=False, indent=2)

    print(f"\n数据已保存到: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
