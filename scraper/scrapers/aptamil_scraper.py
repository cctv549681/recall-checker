#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爱他美召回数据爬虫
"""
from .base_scraper import BaseScraper
from typing import List, Dict, Any
import re


class AptamilScraper(BaseScraper):
    """爱他美召回数据爬虫"""

    def __init__(self):
        super().__init__("爱他美", "Aptamil")

    def scrape_fsa_uk(self) -> List[Dict[str, Any]]:
        """
        从英国 FSA 抓取召回信息

        Returns:
            产品列表
        """
        print("\n抓取英国 FSA 爱他美召回信息...")

        # FSA 搜索爱他美相关的召回
        url = "https://www.food.gov.uk/news-alerts/search?q=aptamil"

        html = self.fetch_page(url)
        if not html:
            return []

        soup = self.parse_page(html)
        products = []

        # 解析召回列表
        alert_cards = soup.find_all('div', class_='alert-card')

        for card in alert_cards:
            title_elem = card.find('h3')
            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)

            # 只处理婴幼儿配方奶粉相关的召回
            keywords = ['infant formula', 'formula', 'baby milk', 'formula milk']
            if not any(kw.lower() in title.lower() for kw in keywords):
                continue

            link_elem = card.find('a')
            if not link_elem:
                continue

            alert_url = link_elem.get('href')
            if alert_url and not alert_url.startswith('http'):
                alert_url = f"https://www.food.gov.uk{alert_url}"

            # 获取详情页
            if alert_url:
                detail_products = self._parse_fsa_alert_detail(alert_url, title)
                products.extend(detail_products)

        print(f"✅ FSA UK: 共 {len(products)} 条记录")
        return products

    def _parse_fsa_alert_detail(self, url: str, title: str) -> List[Dict[str, Any]]:
        """解析 FSA 警告详情页"""
        html = self.fetch_page(url)
        if not html:
            return []

        soup = self.parse_page(html)
        products = []

        # 提取产品信息
        captions = soup.find_all('caption')

        for caption in captions:
            text = caption.get_text(strip=True)

            # 检查是否是爱他美产品
            if 'aptamil' not in text.lower() and 'aptamil' not in title.lower():
                continue

            product_name = text
            product_data = self._extract_product_data(caption)
            product_data['product_name'] = product_name

            if product_data.get('batch_codes'):
                products.append(product_data)

        return products

    def _extract_product_data(self, caption) -> Dict[str, Any]:
        """从 caption 中提取产品数据"""
        data = {
            'pack_size': '',
            'batch_codes': [],
            'best_before': None
        }

        # 找到下面的 tbody
        tbodies = []
        next_el = caption.find_next_sibling()
        while next_el and next_el.name == 'tbody':
            tbodies.append(next_el)
            next_el = next_el.find_next_sibling()

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
                if not data['best_before']:
                    data['best_before'] = bb

        return data

    def scrape_samr_cn(self) -> List[Dict[str, Any]]:
        """
        从中国国家市场监督管理总局抓取召回信息

        Returns:
            产品列表
        """
        print("\n抓取中国 SAMR 爱他美召回信息...")

        # SAMR 召回搜索页面
        url = "https://www.samr.gov.cn/zh/search/search.html?searchValue=爱他美&category=1005"

        html = self.fetch_page(url)
        if not html:
            return []

        soup = self.parse_page(html)
        products = []

        # 解析召回列表
        # 注意：SAMR 网站的结构可能需要根据实际情况调整
        recall_items = soup.find_all('div', class_='recall-item')

        for item in recall_items:
            title_elem = item.find('h3')
            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)

            # 检查是否是婴幼儿配方奶粉
            if '婴幼儿配方奶粉' not in title and '配方奶粉' not in title:
                continue

            # 提取产品信息
            product_data = self._extract_samr_product_data(item, title)
            products.append(product_data)

        print(f"✅ SAMR CN: 共 {len(products)} 条记录")
        return products

    def _extract_samr_product_data(self, item, title: str) -> Dict[str, Any]:
        """从 SAMR 召回项中提取产品数据"""
        data = {
            'product_name': title,
            'pack_size': '',
            'batch_codes': [],
            'best_before': None,
            'region': 'CN',
            'recall_reason': '',
            'risk_level': '高'
        }

        # 提取批次号（通常在"批次号"或"生产日期"字段中）
        batch_elem = item.find(text=re.compile(r'批次号|生产日期|Lot'))
        if batch_elem:
            batch_text = str(batch_elem)
            codes = [c.strip() for c in re.findall(r'[A-Z0-9]{4,}', batch_text)]
            data['batch_codes'] = codes

        # 提取规格
        size_elem = item.find(text=re.compile(r'规格|包装|Pack'))
        if size_elem:
            size_text = str(size_elem)
            size_match = re.search(r'\d+\s*(g|ml|kg|L)', size_text)
            if size_match:
                data['pack_size'] = size_match.group()

        # 提取召回原因
        reason_elem = item.find(text=re.compile(r'原因|问题|Reason'))
        if reason_elem:
            data['recall_reason'] = str(reason_elem).strip()

        return data

    def scrape(self) -> List[Dict[str, Any]]:
        """
        抓取所有数据源的爱他美召回信息

        Returns:
            所有产品列表
        """
        all_products = []

        # 抓取英国 FSA
        fsa_products = self.scrape_fsa_uk()
        all_products.extend(fsa_products)

        # 抓取中国 SAMR
        samr_products = self.scrape_samr_cn()
        all_products.extend(samr_products)

        return all_products


def main():
    """测试爬虫"""
    print("=" * 70)
    print("爱他美召回数据爬虫")
    print("=" * 70)

    scraper = AptamilScraper()

    # 抓取数据
    products = scraper.scrape()

    if not products:
        print("❌ 未获取到数据")
        return

    # 格式化数据
    source_url = "https://www.food.gov.uk"
    records = scraper.format_for_feishu(products, source_url)

    # 显示预览
    scraper.show_preview(records, limit=3)

    # 确认插入
    print(f"\n共 {len(records)} 条记录")
    confirm = input("\n确认插入飞书? (y/n): ").strip().lower()

    if confirm == 'y':
        scraper.insert_to_feishu(records)
        print("\n✅ 爬虫完成！")
    else:
        print("\n已取消插入")


if __name__ == "__main__":
    main()
