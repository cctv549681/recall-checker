#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量数据插入优化版本 - 使用飞书批量API
"""
import sys
from pathlib import Path
from datetime import datetime
import json
import time

# 添加 scraper 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from abbott_scraper import AbbottScraper
from utils.feishu_config import APP_TOKEN, TABLE_ID
import requests


def batch_insert_to_feishu(scraper, records: list, batch_size: int = 500) -> int:
    """
    批量插入记录到飞书（优化版本）

    Args:
        scraper: 爬虫实例
        records: 记录列表
        batch_size: 每批插入的记录数

    Returns:
        成功插入的数量
    """
    if not records:
        print("没有记录需要插入")
        return 0

    print(f"\n准备批量插入 {len(records)} 条记录到飞书...")
    print(f"批次大小: {batch_size}")

    token = scraper.get_feishu_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    url = f"{scraper.base_url}/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/batch_create"

    success_count = 0
    failed_count = 0
    start_time = time.time()

    # 分批插入
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(records) + batch_size - 1) // batch_size

        print(f"\n处理批次 {batch_num}/{total_batches} ({len(batch)} 条记录)...")

        # 准备批量数据
        data = {
            "records": [
                {
                    "fields": record
                }
                for record in batch
            ]
        }

        try:
            resp = requests.post(url, headers=headers, json=data)
            result = resp.json()

            if result.get("code") == 0:
                # 批量创建成功
                created = len(result.get("data", {}).get("records", []))
                success_count += created
                print(f"  ✅ 成功插入 {created} 条记录")
            else:
                print(f"  ❌ 批次插入失败: {result.get('msg')}")
                failed_count += len(batch)

        except Exception as e:
            print(f"  ❌ 批次插入异常: {e}")
            failed_count += len(batch)

        # 显示进度
        elapsed = time.time() - start_time
        avg_time = elapsed / (i + 1) * batch_size if i > 0 else 0
        remaining = len(records) - i - len(batch)
        eta = remaining / batch_size * avg_time if avg_time > 0 else 0

        print(f"  进度: {success_count + failed_count}/{len(records)} ({(success_count + failed_count) * 100 // len(records)}%) | 耗时: {elapsed:.1f}s | 预计剩余: {eta:.1f}s")

    print(f"\n✅ 批量插入完成！")
    print(f"  成功: {success_count} 条")
    print(f"  失败: {failed_count} 条")
    print(f"  总耗时: {time.time() - start_time:.1f}s")

    return success_count


def main():
    """主函数"""
    print("=" * 70)
    print("雅培数据批量插入（优化版）")
    print("=" * 70)

    scraper = AbbottScraper()

    # 检查是否已有缓存数据
    cache_file = Path("/tmp/abbott_records.json")
    if cache_file.exists():
        print("\n发现缓存数据，使用缓存...")
        with open(cache_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        print(f"✅ 从缓存加载 {len(records)} 条记录")
    else:
        # 下载PDF
        print("\n下载雅培召回PDF...")
        pdf_path = '/tmp/SimilacLotList.pdf'
        if not scraper.download_pdf(pdf_path):
            print("❌ PDF下载失败")
            return

        # 解析PDF
        print("\n解析雅培召回PDF...")
        products = scraper.parse_pdf(pdf_path)

        if not products:
            print("❌ 未获取到雅培数据")
            return

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

        # 缓存数据
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"✅ 数据已缓存到: {cache_file}")

    # 确认插入
    print(f"\n共 {len(records)} 条记录待插入")
    confirm = input(f"\n确认插入飞书? (y/n): ").strip().lower()

    if confirm == 'y':
        count = batch_insert_to_feishu(scraper, records, batch_size=500)
        print(f"\n✅ 雅培数据插入完成！共插入 {count} 条记录")
    else:
        print("\n已取消插入")


if __name__ == "__main__":
    main()
