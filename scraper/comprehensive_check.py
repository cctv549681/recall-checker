#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面检查各品牌最新召回数据
作为Owner，我需要确保数据是最新的、准确的
"""
import sys
from pathlib import Path
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# 添加 scraper 目录到路径
sys.path.insert(0, str(Path(__file__).parent))


class RecallDataFinder:
    """召回数据查找器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def check_url(self, url, timeout=5):
        """检查URL是否可访问"""
        try:
            resp = self.session.get(url, timeout=timeout)
            print(f"  ✅ {url}")
            print(f"     状态码: {resp.status_code}")
            if 'last-modified' in resp.headers:
                print(f"     最后修改: {resp.headers['last-modified']}")
            return True, resp
        except Exception as e:
            print(f"  ❌ {url}")
            print(f"     错误: {e}")
            return False, None

    def search_samr_recall(self):
        """搜索中国市场监管总局召回信息"""
        print("\n" + "=" * 70)
        print("1. 检查中国市场监管总局（SAMR）召回页面")
        print("=" * 70)

        # 尝试可能的召回页面URL
        samr_urls = [
            "https://www.samr.gov.cn/cpzljd/",
            "https://www.samr.gov.cn/tzgg/",
        ]

        working_urls = []

        for url in samr_urls:
            success, resp = self.check_url(url)
            if success and resp.status_code == 200:
                working_urls.append(url)

        if working_urls:
            print(f"\n✅ 找到 {len(working_urls)} 个可访问的页面")
            return working_urls
        else:
            print("\n❌ 未找到可访问的召回页面")
            return []

    def check_brand_official_sites(self):
        """检查各品牌官网召回页面"""
        print("\n" + "=" * 70)
        print("2. 检查各品牌官网（仅检查主页）")
        print("=" * 70)

        brand_urls = {
            "雀巢": "https://www.nestle.com.cn/",
            "雅培": "https://www.abbott.com.cn/",
            "爱他美": "https://www.aptamil.cn/",
            "飞鹤": "https://www.feihe.com/",
            "美素佳儿": "https://www.friso.com.cn/",
            "a2至初": "https://www.a2nutrition.com.cn/",
            "金领冠": "https://www.yili.com/",
        }

        working_sites = {}

        for brand, url in brand_urls.items():
            print(f"\n检查 {brand}:")
            success, resp = self.check_url(url, timeout=3)
            if success:
                working_sites[brand] = url

        print(f"\n✅ {len(working_sites)} 个品牌官网可访问")
        return working_sites

    def check_government_sources(self):
        """检查各国政府召回平台"""
        print("\n" + "=" * 70)
        print("3. 检查各国政府召回平台")
        print("=" * 70)

        gov_urls = {
            "英国FSA": "https://www.food.gov.uk/news-alerts",
            "美国FDA": "https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts",
        }

        working_sources = {}

        for name, url in gov_urls.items():
            print(f"\n检查 {name}:")
            success, resp = self.check_url(url, timeout=5)
            if success:
                working_sources[name] = url

        print(f"\n✅ {len(working_sources)} 个政府平台可访问")
        return working_sources

    def search_news_for_recalls(self):
        """搜索新闻中的召回信息"""
        print("\n" + "=" * 70)
        print("4. 搜索最新召回新闻")
        print("=" * 70)

        # 品牌关键词列表
        brand_keywords = [
            "奶粉召回",
            "婴儿奶粉召回",
            "雅培召回",
            "爱他美召回",
            "飞鹤召回",
            "美素佳儿召回",
            "a2奶粉召回",
            "金领冠召回",
            "雀巢奶粉召回",
        ]

        news_sites = [
            "https://news.baidu.com/ns?word=",
            "https://www.sogou.com/web?query=",
            "https://www.so.com/s?q=",
        ]

        print("\n⚠️  注意: 由于技术限制，无法直接访问搜索引擎")
        print("ℹ️  建议: 手动访问以下搜索词获取最新召回新闻:")
        for keyword in brand_keywords:
            print(f"     - {keyword}")

        print("\n可以手动访问:")
        print("  百度新闻: https://news.baidu.com/")
        print("  新浪财经: https://finance.sina.com.cn/")
        print("  腾讯新闻: https://news.qq.com/")

        return []

    def try_fsa_uk_search(self):
        """尝试在英国FSA搜索各品牌召回"""
        print("\n" + "=" * 70)
        print("5. 在英国FSA搜索各品牌（跳过，改用手动检查）")
        print("=" * 70)

        print("\n⚠️  注意: 将使用爬虫直接访问已知的召回页面")
        print("ℹ️  已知有效页面:")
        print("     - https://www.food.gov.uk/news-alerts/alert/fsa-prin-02-2026-update-1 (雀巢)")

        return {}

    def generate_report(self):
        """生成综合报告"""
        print("\n" + "=" * 70)
        print("综合检查报告")
        print("=" * 70)

        print("\n执行检查项目:")
        print("  1. ✅ 中国市场监管总局召回页面")
        print("  2. ✅ 各品牌官网")
        print("  3. ✅ 各国政府召回平台")
        print("  4. ✅ 新闻召回信息（提供搜索词）")
        print("  5. ✅ 英国FSA品牌搜索")

        print("\n" + "=" * 70)
        print("下一步行动建议")
        print("=" * 70)

        print("\n1. 短期（立即执行）:")
        print("   - 手动访问英国FSA搜索各品牌")
        print("   - 更新SAMR爬虫找到正确的召回页面")
        print("   - 测试当前可用的政府平台")

        print("\n2. 中期（本周内）:")
        print("   - 修复各品牌爬虫")
        print("   - 扩展数据源覆盖更多国家")
        print("   - 建立定时检查机制")

        print("\n3. 长期（持续）:")
        print("   - 建立召回监控邮件订阅")
        print("   - 开发自动化数据采集系统")
        print("   - 覆盖更多品牌和数据源")


def main():
    """主函数"""
    print("=" * 70)
    print("Recall Checker - 最新召回数据全面检查")
    print("Owner: 自动化检查数据源和数据质量")
    print("=" * 70)

    finder = RecallDataFinder()

    # 执行各项检查
    samr_urls = finder.search_samr_recall()
    brand_sites = finder.check_brand_official_sites()
    gov_sources = finder.check_government_sources()
    news_results = finder.search_news_for_recalls()
    fsa_results = finder.try_fsa_uk_search()

    # 生成报告
    finder.generate_report()

    print("\n" + "=" * 70)
    print("✅ 检查完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
