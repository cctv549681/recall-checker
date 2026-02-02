#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量数据插入脚本 - 将已验证的召回数据插入飞书
"""
import sys
from pathlib import Path
from datetime import datetime
import json

# 添加 scraper 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from nestle_scraper import NestleScraper
from abbott_scraper import AbbottScraper


def show_preview_simple(records, limit=3):
    """简单的预览函数（不依赖scraper对象）"""
    print("\n数据预览:")
    for i, r in enumerate(records[:limit], 1):
        print(f"{i}. {r.get('product_name', 'N/A')}")
        print(f"   品牌: {r.get('brand', 'N/A')} | 规格: {r.get('pack_size', 'N/A')}")
        batch_codes = r.get('batch_codes', '')
        batch_preview = batch_codes[:50] + '...' if len(batch_codes) > 50 else batch_codes
        print(f"   批次: {batch_preview}")
        print()


def insert_nestle_data():
    """插入雀巢召回数据"""
    print("\n" + "="*70)
    print("雀巢召回数据插入")
    print("="*70)

    scraper = NestleScraper()

    # 抓取数据
    print("\n抓取雀巢召回数据...")
    products = scraper.scrape_fsa_alert()

    if not products:
        print("❌ 未获取到雀巢数据")
        return 0

    print(f"✅ 成功抓取 {len(products)} 条产品数据")

    # 格式化数据
    source_url = "https://www.food.gov.uk/news-alerts/alert/fsa-prin-02-2026-update-1"
    records = scraper.format_for_feishu(products, source_url)

    # 显示预览
    show_preview_simple(records, limit=3)

    # 确认插入
    print(f"\n共 {len(records)} 条记录待插入")
    confirm = input("\n确认插入飞书? (y/n): ").strip().lower()

    if confirm == 'y':
        count = scraper.insert_to_feishu(records)
        print(f"\n✅ 雀巢数据插入完成！共插入 {count} 条记录")
        return count
    else:
        print("\n已取消插入")
        return 0


def insert_abbott_data():
    """插入雅培召回数据"""
    print("\n" + "="*70)
    print("雅培召回数据插入")
    print("="*70)

    scraper = AbbottScraper()

    # 下载PDF
    print("\n下载雅培召回PDF...")
    pdf_path = '/tmp/SimilacLotList.pdf'
    if not scraper.download_pdf(pdf_path):
        print("❌ PDF下载失败")
        return 0

    # 解析PDF
    print("\n解析雅培召回PDF...")
    products = scraper.parse_pdf(pdf_path)

    if not products:
        print("❌ 未获取到雅培数据")
        return 0

    print(f"✅ 成功解析 {len(products)} 条批次记录")

    # 显示统计信息
    stats = scraper.get_statistics(products)
    print("\n数据统计:")
    print(f"  总记录数: {stats['total']}")
    print(f"  唯一产品数: {stats['unique_products']}")
    print(f"  唯一批次号数: {stats['unique_batches']}")

    # 格式化数据
    source_url = "https://www.cbsnews.com/htdocs/pdf/SimilacLotList.pdf"
    records = scraper.format_for_feishu(products, source_url)

    # 显示预览
    print("\n数据预览:")
    show_preview_simple(records, limit=3)

    # 确认插入
    print(f"\n共 {len(records)} 条记录待插入")
    confirm = input(f"\n确认插入飞书? (y/n): ").strip().lower()

    if confirm == 'y':
        count = scraper.insert_to_feishu(records)
        print(f"\n✅ 雅培数据插入完成！共插入 {count} 条记录")
        return count
    else:
        print("\n已取消插入")
        return 0


def insert_all_data():
    """插入所有召回数据"""
    print("\n" + "="*70)
    print("批量数据插入 - 所有品牌")
    print("="*70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    # 插入雀巢数据
    try:
        nestle_count = insert_nestle_data()
        results["nestle"] = nestle_count
    except Exception as e:
        print(f"\n❌ 雀巢数据插入失败: {e}")
        import traceback
        traceback.print_exc()
        results["nestle"] = 0

    # 插入雅培数据
    try:
        abbott_count = insert_abbott_data()
        results["abbott"] = abbott_count
    except Exception as e:
        print(f"\n❌ 雅培数据插入失败: {e}")
        import traceback
        traceback.print_exc()
        results["abbott"] = 0

    # 打印汇总
    print("\n" + "="*70)
    print("插入汇总")
    print("="*70)

    total_inserted = sum(results.values())

    for brand, count in results.items():
        status = "✅" if count > 0 else "❌"
        print(f"{status} {brand.upper()}: {count} 条记录")

    print(f"\n总计插入: {total_inserted} 条记录")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 保存结果
    output = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_inserted": total_inserted,
            "brands_count": len(results)
        },
        "details": results
    }

    filepath = Path(__file__).parent.parent / "data" / "insertion_report.json"
    filepath.parent.mkdir(exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 插入报告已保存: {filepath}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='批量插入召回数据到飞书')
    parser.add_argument('--nestle', action='store_true', help='插入雀巢数据')
    parser.add_argument('--abbott', action='store_true', help='插入雅培数据')
    parser.add_argument('--all', action='store_true', help='插入所有品牌数据')

    args = parser.parse_args()

    if args.all:
        insert_all_data()
    elif args.nestle:
        insert_nestle_data()
    elif args.abbott:
        insert_abbott_data()
    else:
        print("请指定 --nestle, --abbott 或 --all")
        parser.print_help()


if __name__ == "__main__":
    main()
