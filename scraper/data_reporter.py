#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据汇总和统计报告
"""
import sys
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Any

# 添加 scraper 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from nestle_scraper import NestleScraper
from abbott_scraper import AbbottScraper


class DataReporter:
    """数据报告生成器"""

    def __init__(self):
        self.all_data = {}

    def collect_nestle_data(self) -> Dict[str, Any]:
        """收集雀巢数据"""
        print("\n收集雀巢召回数据...")

        scraper = NestleScraper()
        products = scraper.scrape_fsa_alert()

        if not products:
            return {"brand": "nestle", "count": 0, "products": []}

        source_url = "https://www.food.gov.uk/news-alerts/alert/fsa-prin-02-2026-update-1"
        records = scraper.format_for_feishu(products, source_url)

        return {
            "brand": "nestle",
            "brand_name": "雀巢",
            "count": len(records),
            "products": records
        }

    def collect_abbott_data(self) -> Dict[str, Any]:
        """收集雅培数据"""
        print("\n收集雅培召回数据...")

        scraper = AbbottScraper()

        pdf_path = '/tmp/SimilacLotList.pdf'
        if not scraper.download_pdf(pdf_path):
            return {"brand": "abbott", "count": 0, "products": []}

        products = scraper.parse_pdf(pdf_path)

        if not products:
            return {"brand": "abbott", "count": 0, "products": []}

        source_url = "https://www.cbsnews.com/htdocs/pdf/SimilacLotList.pdf"
        records = scraper.format_for_feishu(products, source_url)

        return {
            "brand": "abbott",
            "brand_name": "雅培",
            "count": len(records),
            "products": records
        }

    def analyze_batch_codes(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析批次号数据"""
        batch_analysis = {
            "total": len(records),
            "by_sub_brand": {},
            "by_pack_size": {},
            "by_region": {},
            "by_status": {},
            "batch_code_formats": []
        }

        for record in records:
            # 按子品牌统计
            sub_brand = record.get('sub_brand', 'Unknown')
            batch_analysis["by_sub_brand"][sub_brand] = batch_analysis["by_sub_brand"].get(sub_brand, 0) + 1

            # 按规格统计
            pack_size = record.get('pack_size', 'Unknown')
            batch_analysis["by_pack_size"][pack_size] = batch_analysis["by_pack_size"].get(pack_size, 0) + 1

            # 按地区统计
            region = record.get('region', 'Unknown')
            batch_analysis["by_region"][region] = batch_analysis["by_region"].get(region, 0) + 1

            # 按状态统计
            status = record.get('status', 'Unknown')
            batch_analysis["by_status"][status] = batch_analysis["by_status"].get(status, 0) + 1

            # 收集批次号格式
            batch_codes = record.get('batch_codes', '')
            if batch_codes:
                # 取第一个批次号作为示例
                first_batch = batch_codes.split(',')[0].strip()
                if len(first_batch) <= 20:
                    batch_analysis["batch_code_formats"].append(first_batch)

        return batch_analysis

    def generate_summary_report(self) -> Dict[str, Any]:
        """生成汇总报告"""
        print("\n" + "="*70)
        print("生成数据汇总报告")
        print("="*70)

        # 收集数据
        nestle_data = self.collect_nestle_data()
        abbott_data = self.collect_abbott_data()

        self.all_data = {
            "nestle": nestle_data,
            "abbott": abbott_data
        }

        # 生成报告
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_brands": len(self.all_data),
            "total_records": sum(d["count"] for d in self.all_data.values()),
            "brands": {}
        }

        for brand_key, data in self.all_data.items():
            if data["count"] > 0:
                analysis = self.analyze_batch_codes(data["products"])

                report["brands"][brand_key] = {
                    "name": data["brand_name"],
                    "count": data["count"],
                    "analysis": analysis
                }

        return report

    def print_report(self, report: Dict[str, Any]):
        """打印报告"""
        print("\n" + "="*70)
        print("召回数据汇总报告")
        print("="*70)
        print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        print(f"\n总体统计:")
        print(f"  品牌数: {report['total_brands']}")
        print(f"  总记录数: {report['total_records']}")

        print(f"\n各品牌详情:")
        for brand_key, brand_data in report["brands"].items():
            print(f"\n{brand_data['name']} ({brand_key.upper()}):")
            print(f"  记录数: {brand_data['count']}")

            analysis = brand_data['analysis']
            print(f"  子品牌分布:")
            for sub_brand, count in sorted(analysis['by_sub_brand'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    - {sub_brand}: {count}")

            print(f"  规格分布:")
            for size, count in sorted(analysis['by_pack_size'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    - {size}: {count}")

            print(f"  地区分布:")
            for region, count in analysis['by_region'].items():
                print(f"    - {region}: {count}")

            print(f"  状态分布:")
            for status, count in analysis['by_status'].items():
                print(f"    - {status}: {count}")

            if analysis['batch_code_formats']:
                print(f"  批次号示例: {', '.join(analysis['batch_code_formats'][:3])}")

    def save_report(self, report: Dict[str, Any], filename: str = None):
        """保存报告"""
        if filename is None:
            filename = f"recall_data_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = Path(__file__).parent.parent / "data" / filename
        filepath.parent.mkdir(exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 报告已保存: {filepath}")

    def export_sample_data(self, brand_key: str, limit: int = 20):
        """导出样本数据"""
        if brand_key not in self.all_data:
            print(f"❌ 未找到品牌: {brand_key}")
            return

        data = self.all_data[brand_key]
        if data["count"] == 0:
            print(f"❌ {brand_key} 没有数据")
            return

        samples = data["products"][:limit]

        filename = f"{brand_key}_sample_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = Path(__file__).parent.parent / "data" / filename

        output = {
            "brand": data["brand_name"],
            "brand_key": brand_key,
            "total_count": data["count"],
            "sample_count": len(samples),
            "samples": samples
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 样本数据已保存: {filepath}")
        print(f"   品牌名: {data['brand_name']}")
        print(f"   总记录: {data['count']}")
        print(f"   样本数: {len(samples)}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='生成召回数据汇总报告')
    parser.add_argument('--save', action='store_true', help='保存报告到文件')
    parser.add_argument('--export', type=str, help='导出指定品牌的样本数据 (nestle/abbott)')
    parser.add_argument('--limit', type=int, default=20, help='导出样本数据的数量限制')

    args = parser.parse_args()

    reporter = DataReporter()
    report = reporter.generate_summary_report()
    reporter.print_report(report)

    if args.save:
        reporter.save_report(report)

    if args.export:
        reporter.export_sample_data(args.export, args.limit)


if __name__ == "__main__":
    main()
