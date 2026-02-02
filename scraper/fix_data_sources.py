#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源修复工具 - 探索和修复失效的数据源
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import List, Dict, Tuple
import time


class DataSourceFixer:
    """数据源修复器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5,zh-CN;q=0.3',
        })

    def test_url(self, url: str) -> Tuple[bool, str, int]:
        """测试URL是否可访问"""
        try:
            resp = self.session.get(url, timeout=10)
            return (True, resp.url, resp.status_code)
        except Exception as e:
            return (False, str(e), 0)

    def find_samr_recall_pages(self, base_url: str = "https://www.samr.gov.cn/") -> List[Dict[str, str]]:
        """
        查找SAMR产品召回相关页面

        策略：
        1. 访问首页
        2. 查找所有包含"召回"、"产品"、"通知"等关键词的链接
        3. 测试这些链接
        4. 返回可能有效的召回页面
        """
        print("\n" + "=" * 70)
        print("查找SAMR产品召回页面")
        print("=" * 70)

        recall_keywords = ["召回", "产品", "通知", "公告", "cp", "zc"]

        possible_urls = []

        # 尝试一些常见的召回页面URL模式
        patterns = [
            "/cpzljd/",
            "/cp/",
            "/zc/",
            "/tzgg/",
            "/cpc/",
            "/xzjd/",
            "/zhcp/",
            "/tz/",
            "/cpzljd/cpzhc/",
            "/cpzljd/tzgg/",
        ]

        print(f"\n1. 尝试常见URL模式...")
        for pattern in patterns:
            url = base_url.rstrip('/') + pattern
            success, result, status = self.test_url(url)

            if success and status == 200:
                print(f"  ✅ {url} (状态码: {status})")
                possible_urls.append({
                    'url': url,
                    'type': 'common_pattern',
                    'status': status
                })
            else:
                print(f"  ❌ {url} ({result})")

            time.sleep(0.5)

        # 如果上述方法失败，尝试从首页解析链接
        if not possible_urls:
            print(f"\n2. 从首页解析链接...")
            success, result, status = self.test_url(base_url)

            if success and status == 200:
                resp = self.session.get(base_url, timeout=10)
                soup = BeautifulSoup(resp.text, 'html.parser')

                # 查找所有链接
                links = soup.find_all('a', href=True)

                print(f"   找到 {len(links)} 个链接")

                for link in links[:50]:  # 限制检查数量
                    href = link.get('href', '')
                    text = link.get_text(strip=True)

                    # 检查是否包含召回相关关键词
                    if any(kw in href or kw in text for kw in recall_keywords):
                        full_url = urljoin(base_url, href)

                        # 测试URL
                        success, result, status = self.test_url(full_url)

                        if success and status == 200:
                            print(f"     ✅ {text[:30]}: {full_url}")
                            possible_urls.append({
                                'url': full_url,
                                'type': 'parsed_link',
                                'text': text,
                                'status': status
                            })
                            if len(possible_urls) >= 10:
                                break

                    time.sleep(0.2)

        return possible_urls

    def find_fda_recall_pages(self, base_url: str = "https://www.fda.gov/") -> List[Dict[str, str]]:
        """
        查找FDA产品召回页面

        策略：
        1. 尝试已知的召回页面URL
        2. 从首页解析链接
        """
        print("\n" + "=" * 70)
        print("查找FDA产品召回页面")
        print("=" * 70)

        possible_urls = []

        # 已知的FDA召回页面URL
        known_patterns = [
            "/food/recalls-outbreaks-contaminations",
            "/safety/recalls-market-withdrawals-safety-alerts",
            "/food/recalls",
            "/safety/recalls",
            "/industry/food-recall",
            "/for-industry/food-recall",
            "/food/food-recalls",
        ]

        print(f"\n1. 尝试已知召回页面URL...")
        for pattern in known_patterns:
            url = base_url.rstrip('/') + pattern
            success, result, status = self.test_url(url)

            if success and status == 200:
                print(f"  ✅ {url} (状态码: {status})")
                possible_urls.append({
                    'url': url,
                    'type': 'known_pattern',
                    'status': status
                })
            else:
                print(f"  ❌ {url} ({result})")

            time.sleep(0.5)

        # 从首页解析链接
        if not possible_urls:
            print(f"\n2. 从首页解析链接...")
            success, result, status = self.test_url(base_url)

            if success and status == 200:
                resp = self.session.get(base_url, timeout=10)
                soup = BeautifulSoup(resp.text, 'html.parser')

                # 查找所有链接
                links = soup.find_all('a', href=True)

                recall_keywords = ["recall", "food", "safety", "outbreak", "contamination"]

                for link in links[:50]:
                    href = link.get('href', '')
                    text = link.get_text(strip=True).lower()

                    if any(kw in href.lower() or kw in text for kw in recall_keywords):
                        full_url = urljoin(base_url, href)

                        # 测试URL
                        success, result, status = self.test_url(full_url)

                        if success and status == 200:
                            print(f"     ✅ {text[:30]}: {full_url}")
                            possible_urls.append({
                                'url': full_url,
                                'type': 'parsed_link',
                                'text': text,
                                'status': status
                            })
                            if len(possible_urls) >= 10:
                                break

                    time.sleep(0.2)

        return possible_urls

    def check_brand_websites(self, brand_urls: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """
        检查品牌官网及其召回页面

        Args:
            brand_urls: 品牌名称到官网URL的映射

        Returns:
            检查结果
        """
        print("\n" + "=" * 70)
        print("检查品牌官网")
        print("=" * 70)

        results = {}

        for brand, homepage_url in brand_urls.items():
            print(f"\n检查 {brand}:")

            # 1. 测试主页
            success, result, status = self.test_url(homepage_url)

            if not success:
                print(f"  ❌ 主页无法访问: {result}")
                results[brand] = {
                    'homepage': homepage_url,
                    'status': 'failed',
                    'error': result
                }
                continue

            print(f"  ✅ 主页可访问 (状态码: {status})")

            # 2. 查找召回相关页面
            recall_paths = [
                '/recall',
                '/recalls',
                '/news/recall',
                '/news/recalls',
                '/news',
                '/notices',
                '/公告',
                '/召回',
                '/news/recall/',
                '/recalls/',
            ]

            recall_pages = []

            for path in recall_paths:
                recall_url = homepage_url.rstrip('/') + path
                success, result, status = self.test_url(recall_url)

                if success and status == 200:
                    print(f"     ✅ {recall_url}")
                    recall_pages.append(recall_url)

            # 3. 从主页解析查找召回链接
            try:
                resp = self.session.get(homepage_url, timeout=10)
                soup = BeautifulSoup(resp.text, 'html.parser')

                recall_keywords = ["recall", "召回", "公告", "notice", "news"]

                links = soup.find_all('a', href=True)
                for link in links[:30]:
                    href = link.get('href', '')
                    text = link.get_text(strip=True).lower()

                    if any(kw in href.lower() or kw in text for kw in recall_keywords):
                        full_url = urljoin(homepage_url, href)

                        if full_url not in recall_pages and not full_url.endswith('.pdf'):
                            recall_pages.append(full_url)
                            print(f"     ✅ {link.get_text(strip=True)[:30]}: {full_url}")

                            if len(recall_pages) >= 5:
                                break
            except Exception as e:
                print(f"     ⚠️  解析主页链接失败: {e}")

            results[brand] = {
                'homepage': homepage_url,
                'status': 'success',
                'recall_pages': recall_pages
            }

            time.sleep(1)

        return results

    def generate_fix_report(self, samr_urls: List[Dict], fda_urls: List[Dict], brand_results: Dict):
        """生成修复报告"""
        print("\n" + "=" * 70)
        print("数据源修复报告")
        print("=" * 70)

        print("\n1. 中国SAMR:")
        if samr_urls:
            print(f"   ✅ 找到 {len(samr_urls)} 个可能有效的页面:")
            for url_info in samr_urls:
                print(f"      - {url_info['url']}")
        else:
            print("   ❌ 未找到有效的召回页面")

        print("\n2. 美国FDA:")
        if fda_urls:
            print(f"   ✅ 找到 {len(fda_urls)} 个可能有效的页面:")
            for url_info in fda_urls:
                print(f"      - {url_info['url']}")
        else:
            print("   ❌ 未找到有效的召回页面")

        print("\n3. 品牌官网:")
        for brand, result in brand_results.items():
            if result['status'] == 'success':
                print(f"   ✅ {brand}:")
                print(f"      主页: {result['homepage']}")
                if result['recall_pages']:
                    print(f"      召回页面 ({len(result['recall_pages'])}):")
                    for page in result['recall_pages'][:3]:
                        print(f"        - {page}")
                else:
                    print(f"      ⚠️  未找到召回页面")
            else:
                print(f"   ❌ {brand}: {result.get('error', 'Unknown error')}")

        print("\n" + "=" * 70)
        print("修复建议")
        print("=" * 70)

        if samr_urls:
            print("\n1. SAMR修复:")
            print("   建议更新爬虫配置使用以下URL:")
            for url_info in samr_urls[:3]:
                print(f"   - {url_info['url']}")

        if fda_urls:
            print("\n2. FDA修复:")
            print("   建议更新爬虫配置使用以下URL:")
            for url_info in fda_urls[:3]:
                print(f"   - {url_info['url']}")

        print("\n3. 品牌官网修复:")
        print("   对于找到召回页面的品牌，可以:")
        print("   - 直接访问这些页面检查召回信息")
        print("   - 使用爬虫抓取这些页面")
        print("   - 设置定时任务定期检查")


def main():
    """主函数"""
    print("=" * 70)
    print("数据源修复工具")
    print("自动探索和修复失效的数据源")
    print("=" * 70)

    fixer = DataSourceFixer()

    # 1. 查找SAMR召回页面
    samr_urls = fixer.find_samr_recall_pages()

    # 2. 查找FDA召回页面
    fda_urls = fixer.find_fda_recall_pages()

    # 3. 检查品牌官网
    brand_urls = {
        "雀巢": "https://www.nestle.com.cn/",
        "雅培": "https://www.abbott.com.cn/",
        "爱他美": "https://www.aptamil.cn/",
        "飞鹤": "https://www.feihe.com/",
        "美素佳儿": "https://www.friso.com.cn/",
        "a2至初": "https://www.a2nutrition.com.cn/",
        "金领冠": "https://www.yili.com/",
    }

    brand_results = fixer.check_brand_websites(brand_urls)

    # 生成报告
    fixer.generate_fix_report(samr_urls, fda_urls, brand_results)

    print("\n✅ 修复检查完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
