#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
召回数据爬虫统一运行器
"""
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import json

# 添加 scraper 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from scrapers.base_scraper import BaseScraper
from scrapers.brand_config import get_all_sources, get_brand_config

# 导入各个品牌的爬虫
from scrapers.aptamil_scraper import AptamilScraper
from scrapers.feihe_scraper import FeiheScraper
from scrapers.friso_scraper import FrisoScraper
from scrapers.a2_scraper import A2Scraper
from scrapers.jinlingguan_scraper import JinlingguanScraper


class RecallScraperRunner:
    """召回数据爬虫运行器"""

    def __init__(self):
        self.scrapers = {
            "aptamil": AptamilScraper,
            "feihe": FeiheScraper,
            "friso": FrisoScraper,
            "a2": A2Scraper,
            "jinlingguan": JinlingguanScraper
        }
        self.all_results = {}

    def run_single_brand(self, brand_key: str, insert_to_feishu: bool = False) -> Dict[str, Any]:
        """
        运行单个品牌的爬虫

        Args:
            brand_key: 品牌标识符（如 'aptamil', 'feihe'）
            insert_to_feishu: 是否插入飞书表格

        Returns:
            抓取结果
        """
        if brand_key not in self.scrapers:
            print(f"❌ 未找到品牌爬虫: {brand_key}")
            return {"success": False, "message": f"未找到品牌爬虫: {brand_key}"}

        print("\n" + "=" * 70)
        print(f"开始抓取品牌: {brand_key}")
        print("=" * 70)

        try:
            scraper_class = self.scrapers[brand_key]
            scraper = scraper_class()

            # 运行爬虫
            products = scraper.scrape()

            if not products:
                print(f"⚠️  {brand_key}: 未获取到召回数据")
                return {
                    "success": True,
                    "brand": brand_key,
                    "count": 0,
                    "message": "未获取到召回数据"
                }

            # 获取数据源URL
            config = get_brand_config(brand_key)
            source_url = config["sources"][0]["url"] if config["sources"] else ""

            # 格式化数据
            records = scraper.format_for_feishu(products, source_url)

            result = {
                "success": True,
                "brand": brand_key,
                "count": len(records),
                "records": records,
                "message": f"成功抓取 {len(records)} 条记录"
            }

            # 保存到结果字典
            self.all_results[brand_key] = result

            # 显示预览
            scraper.show_preview(records, limit=3)

            # 插入飞书
            if insert_to_feishu:
                confirm = input(f"\n确认插入 {len(records)} 条记录到飞书? (y/n): ").strip().lower()
                if confirm == 'y':
                    success_count = scraper.insert_to_feishu(records)
                    result["inserted_count"] = success_count
                else:
                    result["inserted_count"] = 0
                    print("\n已取消插入")

            print(f"\n✅ {brand_key} 爬虫完成！")
            return result

        except Exception as e:
            print(f"❌ {brand_key} 爬虫运行失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "brand": brand_key,
                "message": f"运行失败: {e}"
            }

    def run_all_brands(self, brands: List[str] = None, insert_to_feishu: bool = False) -> Dict[str, Any]:
        """
        运行所有品牌或指定品牌的爬虫

        Args:
            brands: 要运行的品牌列表，None 表示运行所有品牌
            insert_to_feishu: 是否插入飞书表格

        Returns:
            所有抓取结果
        """
        if brands is None:
            brands = list(self.scrapers.keys())

        print("\n" + "=" * 70)
        print("召回数据爬虫 - 批量运行")
        print("=" * 70)
        print(f"计划运行 {len(brands)} 个品牌的爬虫:")
        for brand in brands:
            print(f"  - {brand}")
        print()

        all_results = {}
        success_count = 0
        fail_count = 0
        total_records = 0

        for i, brand_key in enumerate(brands, 1):
            print(f"\n进度: {i}/{len(brands)}")

            result = self.run_single_brand(brand_key, insert_to_feishu=False)

            if result["success"]:
                success_count += 1
                total_records += result["count"]
            else:
                fail_count += 1

            all_results[brand_key] = result

        # 批量插入飞书
        if insert_to_feishu and total_records > 0:
            print("\n" + "=" * 70)
            print("批量插入飞书表格")
            print("=" * 70)

            for brand_key, result in all_results.items():
                if result["success"] and result["count"] > 0:
                    print(f"\n插入 {brand_key}: {result['count']} 条记录")
                    scraper_class = self.scrapers[brand_key]
                    scraper = scraper_class()
                    inserted = scraper.insert_to_feishu(result["records"])
                    result["inserted_count"] = inserted

        # 打印汇总
        print("\n" + "=" * 70)
        print("运行汇总")
        print("=" * 70)
        print(f"总品牌数: {len(brands)}")
        print(f"成功: {success_count}")
        print(f"失败: {fail_count}")
        print(f"总记录数: {total_records}")

        print("\n各品牌结果:")
        for brand_key, result in all_results.items():
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {brand_key}: {result['count']} 条记录")

        return {
            "success": True,
            "total_brands": len(brands),
            "success_count": success_count,
            "fail_count": fail_count,
            "total_records": total_records,
            "results": all_results
        }

    def save_results(self, filename: str = None):
        """
        保存抓取结果到 JSON 文件

        Args:
            filename: 文件名，None 表示使用默认名称
        """
        if filename is None:
            filename = f"recall_scraper_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # 转换为可序列化的格式
        serializable_results = {}
        for brand_key, result in self.all_results.items():
            serializable_results[brand_key] = {
                "success": result["success"],
                "brand": result["brand"],
                "count": result["count"],
                "message": result["message"],
                "records": result.get("records", [])[:10]  # 只保存前10条作为示例
            }

        # 添加汇总信息
        output = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_brands": len(self.all_results),
                "total_records": sum(r.get("count", 0) for r in self.all_results.values())
            },
            "results": serializable_results
        }

        filepath = Path(__file__).parent.parent / "data" / filename
        filepath.parent.mkdir(exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 结果已保存到: {filepath}")

    def show_data_sources(self):
        """显示所有数据源"""
        sources = get_all_sources()

        print("\n" + "=" * 70)
        print("所有数据源")
        print("=" * 70)

        grouped = {}
        for source in sources:
            brand_key = source["brand_key"]
            if brand_key not in grouped:
                grouped[brand_key] = {
                    "brand_name": source["brand_name"],
                    "brand_name_en": source["brand_name_en"],
                    "sources": []
                }
            grouped[brand_key]["sources"].append({
                "country": source["country"],
                "source_type": source["source_type"],
                "url": source["url"]
            })

        for brand_key, info in grouped.items():
            print(f"\n{info['brand_name']} ({info['brand_name_en']})")
            for source in info["sources"]:
                print(f"  - {source['country']} | {source['source_type']}")
                print(f"    {source['url']}")

        print(f"\n总计 {len(grouped)} 个品牌，{len(sources)} 个数据源")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='召回数据爬虫运行器')
    parser.add_argument('--brand', type=str, help='运行单个品牌的爬虫（如：aptamil, feihe, friso, a2, jinlingguan）')
    parser.add_argument('--all', action='store_true', help='运行所有品牌的爬虫')
    parser.add_argument('--insert', action='store_true', help='插入飞书表格')
    parser.add_argument('--save', action='store_true', help='保存结果到文件')
    parser.add_argument('--sources', action='store_true', help='显示所有数据源')

    args = parser.parse_args()

    runner = RecallScraperRunner()

    # 显示数据源
    if args.sources:
        runner.show_data_sources()
        return

    # 运行单个品牌
    if args.brand:
        result = runner.run_single_brand(args.brand, insert_to_feishu=args.insert)
        if args.save:
            runner.save_results()
        return

    # 运行所有品牌
    if args.all:
        result = runner.run_all_brands(insert_to_feishu=args.insert)
        if args.save:
            runner.save_results()
        return

    # 默认：显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()
