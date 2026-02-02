#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
召回数据爬虫测试脚本
"""
import sys
from pathlib import Path
from datetime import datetime

# 添加 scraper 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from scrapers.base_scraper import BaseScraper
from scrapers.aptamil_scraper import AptamilScraper
from scrapers.feihe_scraper import FeiheScraper
from scrapers.friso_scraper import FrisoScraper
from scrapers.a2_scraper import A2Scraper
from scrapers.jinlingguan_scraper import JinlingguanScraper


def test_scraper(scraper_class, brand_name: str):
    """测试单个爬虫"""
    print(f"\n{'='*70}")
    print(f"测试爬虫: {brand_name}")
    print(f"{'='*70}")

    try:
        scraper = scraper_class()
        print(f"✅ 爬虫实例化成功")
        print(f"   品牌: {scraper.brand}")
        print(f"   品牌英文名: {scraper.brand_en}")

        # 测试抓取
        print(f"\n开始抓取...")
        products = scraper.scrape()

        print(f"\n抓取结果:")
        print(f"   成功: {len(products) > 0}")
        print(f"   产品数量: {len(products)}")

        if len(products) > 0:
            # 显示第一个产品的信息
            print(f"\n第一个产品示例:")
            print(f"   产品名称: {products[0].get('product_name', 'N/A')}")
            print(f"   子品牌: {products[0].get('sub_brand', 'N/A')}")
            print(f"   规格: {products[0].get('pack_size', 'N/A')}")
            print(f"   批次号: {products[0].get('batch_codes', 'N/A')}")

            # 测试格式化
            print(f"\n测试格式化...")
            records = scraper.format_for_feishu(products, "https://example.com")
            print(f"   格式化记录数: {len(records)}")

            print(f"\n第一个记录示例:")
            r = records[0]
            print(f"   品牌: {r.get('brand', 'N/A')}")
            print(f"   产品名称: {r.get('product_name', 'N/A')}")
            print(f"   批次号: {r.get('batch_codes', 'N/A')}")
            print(f"   地区: {r.get('region', 'N/A')}")
            print(f"   风险等级: {r.get('risk_level', 'N/A')}")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_scrapers():
    """测试所有爬虫"""
    print(f"\n{'='*70}")
    print("召回数据爬虫 - 批量测试")
    print(f"{'='*70}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    scrapers = [
        (AptamilScraper, "爱他美"),
        (FeiheScraper, "飞鹤"),
        (FrisoScraper, "美素佳儿"),
        (A2Scraper, "a2至初"),
        (JinlingguanScraper, "金领冠")
    ]

    results = []

    for scraper_class, brand_name in scrapers:
        success = test_scraper(scraper_class, brand_name)
        results.append({
            "brand": brand_name,
            "success": success
        })

    # 打印汇总
    print(f"\n{'='*70}")
    print("测试汇总")
    print(f"{'='*70}")

    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count

    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['brand']}")

    print(f"\n总计: {len(results)} 个爬虫")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")

    if fail_count == 0:
        print(f"\n🎉 所有爬虫测试通过！")
    else:
        print(f"\n⚠️  有 {fail_count} 个爬虫测试失败，请检查错误日志")


def test_single_brand(brand_name: str):
    """测试单个品牌"""
    brand_map = {
        "aptamil": (AptamilScraper, "爱他美"),
        "feihe": (FeiheScraper, "飞鹤"),
        "friso": (FrisoScraper, "美素佳儿"),
        "a2": (A2Scraper, "a2至初"),
        "jinlingguan": (JinlingguanScraper, "金领冠")
    }

    if brand_name.lower() not in brand_map:
        print(f"❌ 未找到品牌: {brand_name}")
        print(f"可用品牌: {', '.join(brand_map.keys())}")
        return

    scraper_class, name = brand_map[brand_name.lower()]
    test_scraper(scraper_class, name)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='召回数据爬虫测试')
    parser.add_argument('--brand', type=str, help='测试单个品牌（如：aptamil, feihe, friso, a2, jinlingguan）')
    parser.add_argument('--all', action='store_true', help='测试所有品牌')

    args = parser.parse_args()

    if args.brand:
        test_single_brand(args.brand)
    elif args.all:
        test_all_scrapers()
    else:
        print("请指定 --brand 或 --all")
        parser.print_help()


if __name__ == "__main__":
    main()
