#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美素佳儿召回数据爬虫
"""
from .base_scraper import BaseScraper
from typing import List, Dict, Any
import re


class FrisoScraper(BaseScraper):
    """美素佳儿召回数据爬虫"""

    def __init__(self):
        super().__init__("美素佳儿", "Friso")

    def scrape_samr_cn(self) -> List[Dict[str, Any]]:
        """
        从中国国家市场监督管理总局抓取召回信息

        Returns:
            产品列表
        """
        print("\n抓取中国 SAMR 美素佳儿召回信息...")

        # SAMR 搜索美素佳儿相关的召回
        url = "https://www.samr.gov.cn/zh/search/search.html?searchValue=美素佳儿&category=1005"

        html = self.fetch_page(url)
        if not html:
            return []

        soup = self.parse_page(html)
        products = []

        # 解析召回列表
        recall_items = soup.find_all('div', class_='recall-item')

        for item in recall_items:
            title_elem = item.find('h3')
            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)

            # 检查是否是美素佳儿产品
            if '美素佳儿' not in title and '皇家美素佳儿' not in title and '美素力' not in title:
                continue

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
            'risk_level': '高',
            'source_type': '政府平台'
        }

        # 提取子品牌
        sub_brands = ['皇家美素佳儿', '美素佳儿', '美素力', '佳贝艾特']
        for sb in sub_brands:
            if sb in title:
                data['sub_brand'] = sb
                break

        # 提取批次号
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

        # 提取发布日期
        date_elem = item.find(text=re.compile(r'日期|发布日期|Date'))
        if date_elem:
            date_text = str(date_elem)
            data['published_date'] = self.parse_date(date_text)

        return data

    def scrape_official(self) -> List[Dict[str, Any]]:
        """
        从美素佳儿官网抓取召回信息

        Returns:
            产品列表
        """
        print("\n抓取美素佳儿官网召回信息...")

        # 美素佳儿官网召回公告页面
        url = "https://www.friso.com.cn/news/recall"

        html = self.fetch_page(url)
        if not html:
            return []

        soup = self.parse_page(html)
        products = []

        # 解析召回公告列表
        news_items = soup.find_all('div', class_='news-item')

        for item in news_items:
            title_elem = item.find('h4')
            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)

            # 检查是否是召回相关的公告
            if '召回' not in title and 'notice' not in title.lower():
                continue

            # 获取详情链接
            link_elem = item.find('a')
            if not link_elem:
                continue

            detail_url = link_elem.get('href')
            if detail_url and not detail_url.startswith('http'):
                detail_url = f"https://www.friso.com.cn{detail_url}"

            # 获取详情页
            if detail_url:
                detail_products = self._parse_official_detail(detail_url, title)
                products.extend(detail_products)

        print(f"✅ 美素佳儿官网: 共 {len(products)} 条记录")
        return products

    def _parse_official_detail(self, url: str, title: str) -> List[Dict[str, Any]]:
        """解析官网召回公告详情页"""
        html = self.fetch_page(url)
        if not html:
            return []

        soup = self.parse_page(html)
        products = []

        # 提取产品信息
        content = soup.find('div', class_='news-content')

        if content:
            # 查找批次号
            batch_pattern = re.compile(r'批次号[::：]\s*([A-Z0-9,\s]+)')
            batch_match = batch_pattern.search(str(content))

            if batch_match:
                batch_codes = [c.strip() for c in batch_match.group(1).split(',')]

                # 查找规格信息
                size_pattern = re.compile(r'规格[::：]\s*(\d+\s*[gmlkgL])')
                size_match = size_pattern.search(str(content))
                pack_size = size_match.group(1) if size_match else ''

                # 查找有效期信息
                date_pattern = re.compile(r'有效期[::：]\s*(\d{4}[年\-]\d{1,2}[月\-]\d{1,2}[日]?)')
                date_match = date_pattern.search(str(content))
                best_before = self.parse_date(date_match.group(1)) if date_match else None

                # 提取子品牌
                sub_brands = ['皇家美素佳儿', '美素佳儿', '美素力', '佳贝艾特']
                sub_brand = ''
                for sb in sub_brands:
                    if sb in title or sb in str(content):
                        sub_brand = sb
                        break

                products.append({
                    'product_name': title,
                    'sub_brand': sub_brand,
                    'pack_size': pack_size,
                    'batch_codes': batch_codes,
                    'best_before': best_before,
                    'region': 'CN',
                    'recall_reason': '请参见官方公告详情',
                    'risk_level': '高',
                    'source_type': '官网'
                })

        return products

    def scrape_nvwa_nl(self) -> List[Dict[str, Any]]:
        """
        从荷兰 NVWA 抓取召回信息

        Returns:
            产品列表
        """
        print("\n抓取荷兰 NVWA 美素佳儿召回信息...")

        # NVWA 搜索美素佳儿相关的召回
        url = "https://www.nvwa.nl/onderwerpen/voedselveiligheid/product-recalls/search?q=friso"

        html = self.fetch_page(url)
        if not html:
            return []

        soup = self.parse_page(html)
        products = []

        # 解析召回列表
        recall_items = soup.find_all('div', class_='recall-item')

        for item in recall_items:
            title_elem = item.find('h3')
            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)

            # 检查是否是美素佳儿产品
            if 'friso' not in title.lower() and 'frieslandcampina' not in title.lower():
                continue

            # 提取产品信息
            product_data = self._extract_nvwa_product_data(item, title)
            products.append(product_data)

        print(f"✅ NVWA NL: 共 {len(products)} 条记录")
        return products

    def _extract_nvwa_product_data(self, item, title: str) -> Dict[str, Any]:
        """从 NVWA 召回项中提取产品数据"""
        data = {
            'product_name': title,
            'pack_size': '',
            'batch_codes': [],
            'best_before': None,
            'region': 'NL',
            'recall_reason': '',
            'risk_level': '高',
            'source_type': '政府平台'
        }

        # 提取批次号
        batch_pattern = re.compile(r'[Ll]ot[::：]?\s*([A-Z0-9,\s]+)')
        batch_match = batch_pattern.search(str(item))
        if batch_match:
            data['batch_codes'] = [c.strip() for c in batch_match.group(1).split(',')]

        # 提取规格
        size_pattern = re.compile(r'\d+\s*(g|ml|kg|L)', re.IGNORECASE)
        size_match = size_pattern.search(str(item))
        if size_match:
            data['pack_size'] = size_match.group()

        # 提取召回原因
        reason_pattern = re.compile(r'[Rr]eason[::：]?\s*([^\n]+)')
        reason_match = reason_pattern.search(str(item))
        if reason_match:
            data['recall_reason'] = reason_match.group(1).strip()

        return data

    def scrape(self) -> List[Dict[str, Any]]:
        """
        抓取所有数据源的美素佳儿召回信息

        Returns:
            所有产品列表
        """
        all_products = []

        # 抓取中国 SAMR
        samr_products = self.scrape_samr_cn()
        all_products.extend(samr_products)

        # 抓取美素佳儿官网
        official_products = self.scrape_official()
        all_products.extend(official_products)

        # 抓取荷兰 NVWA
        nvwa_products = self.scrape_nvwa_nl()
        all_products.extend(nvwa_products)

        return all_products


def main():
    """测试爬虫"""
    print("=" * 70)
    print("美素佳儿召回数据爬虫")
    print("=" * 70)

    scraper = FrisoScraper()

    # 抓取数据
    products = scraper.scrape()

    if not products:
        print("❌ 未获取到数据")
        return

    # 格式化数据
    source_url = "https://www.friso.com.cn"
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
