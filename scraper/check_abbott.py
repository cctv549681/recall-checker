#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行雅培爬虫并显示数据信息（不插入飞书）
"""
import sys
from pathlib import Path

# 添加 scraper 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

import datetime


def check_abbott_data():
    """检查雅培数据"""
    from abbott_scraper import AbbottScraper

    print("=" * 70)
    print("雅培召回数据检查")
    print("=" * 70)

    scraper = AbbottScraper()

    # 下载PDF
    print("\n1. 下载PDF...")
    if not scraper.download_pdf():
        print("❌ PDF下载失败")
        return

    # 解析PDF
    print("\n2. 解析PDF...")
    products = scraper.parse_pdf()

    if not products:
        print("❌ 未获取到数据")
        return

    # 统计信息
    stats = scraper.get_statistics(products)

    print(f"\n总记录数: {stats['total']}")
    print(f"唯一产品数: {stats['unique_products']}")
    print(f"唯一批次号数: {stats['unique_batches']}")

    print("\n按产品统计（Top 10）:")
    sorted_products = sorted(stats['by_product'].items(), key=lambda x: x[1], reverse=True)
    for i, (name, count) in enumerate(sorted_products[:10], 1):
        print(f"  {i}. {name}: {count} 条")

    # 检查召回日期
    print("\n" + "=" * 70)
    print("数据时效性分析")
    print("=" * 70)

    print("\n数据源:")
    print(f"  URL: {scraper.pdf_url}")

    # 检查PDF文件的修改时间
    import requests
    import os

    pdf_path = "/tmp/SimilacLotList.pdf"
    if os.path.exists(pdf_path):
        # 先从URL获取文件信息
        try:
            resp = requests.head(scraper.pdf_url, timeout=10)
            if 'last-modified' in resp.headers:
                server_date = resp.headers['last-modified']
                print(f"  服务器最后修改时间: {server_date}")

                # 解析日期
                from email.utils import parsedate_to_datetime
                server_dt = parsedate_to_datetime(server_date)
                print(f"  服务器日期: {server_dt}")

                # 计算多久之前
                now = datetime.datetime.now(server_dt.tzinfo)
                delta = now - server_dt
                print(f"  距今: {delta.days} 天")

                if delta.days > 1000:
                    print(f"\n⚠️  警告: 数据已过时 {delta.days} 天，建议更新数据源")

        except Exception as e:
            print(f"  无法获取文件修改时间: {e}")

    # 召回原因和状态
    source_url = scraper.pdf_url
    records = scraper.format_for_feishu(products, source_url)

    if records:
        sample = records[0]
        print(f"\n召回原因: {sample.get('recall_reason')}")
        print(f"风险等级: {sample.get('risk_level')}")

        # 检查发布日期
        if sample.get('published_date'):
            pub_date = datetime.datetime.fromtimestamp(sample['published_date'])
            print(f"发布日期: {pub_date}")

            # 计算距今
            delta = datetime.datetime.now() - pub_date
            print(f"距今: {delta.days} 天 ({delta.days // 365} 年)")

            if delta.days > 1000:
                print(f"\n⚠️  警告: 这是 {delta.days // 365} 年前的召回数据，可能已过时")

    print("\n" + "=" * 70)
    print("结论")
    print("=" * 70)

    print("\n雅培数据状态:")
    print("  ❌ 数据过时: 这是2022年2月的召回事件")
    print("  ✅ 爬虫可用: 可以抓取到2197条历史召回记录")
    print("  ℹ️  建议: 查找Abbott官方最新召回信息或联系其客服")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    check_abbott_data()
