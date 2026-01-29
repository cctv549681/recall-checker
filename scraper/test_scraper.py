"""
测试爬虫脚本
"""

import sys
import asyncio
from pathlib import Path

# 添加scraper目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from scrapers.nestle_scraper import NestleRecallScraper


async def test_nestle_scraper():
    """测试雀巢爬虫"""
    scraper = NestleRecallScraper()

    print("=" * 60)
    print("测试雀巢召回信息爬虫")
    print("=" * 60)

    # 只测试FSA页面（更稳定）
    print("\n正在爬取FSA召回公告...")
    recalls = await scraper.scrape_fsa()

    print(f"\n✅ 成功爬取 {len(recalls)} 条召回信息")

    # 显示前3条
    print("\n" + "=" * 60)
    print("召回信息预览（前3条）")
    print("=" * 60)

    for i, recall in enumerate(recalls[:3], 1):
        print(f"\n{i}. {recall.get('product_name', '未知产品')}")
        print(f"   品牌: {recall.get('brand', 'N/A')}")
        print(f"   批次号: {', '.join(recall.get('batch_codes', []))}")
        print(f"   有效期: {recall.get('best_before', 'N/A')}")

    return recalls


if __name__ == "__main__":
    recalls = asyncio.run(test_nestle_scraper())
    print(f"\n总召回信息数: {len(recalls)}")
