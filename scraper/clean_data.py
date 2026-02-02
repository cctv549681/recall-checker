#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清理脚本 - 删除过时的召回数据
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import requests

# 添加 scraper 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.feishu_config import APP_ID, APP_SECRET, APP_TOKEN, TABLE_ID


class DataCleaner:
    """数据清理器"""

    def __init__(self):
        self.base_url = "https://open.feishu.cn/open-apis"
        self.token = None

        # 数据保留策略
        self.retention_days = 365  # 保留365天内的召回数据
        self.cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        self.cutoff_timestamp = int(self.cutoff_date.timestamp())

    def get_token(self):
        """获取飞书token"""
        if not self.token:
            url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
            resp = requests.post(url, json={
                "app_id": APP_ID,
                "app_secret": APP_SECRET
            })
            result = resp.json()
            if result.get("code") == 0:
                self.token = result["tenant_access_token"]
            else:
                raise Exception(f"获取token失败: {result}")
        return self.token

    def get_all_records(self):
        """获取所有记录"""
        token = self.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        url = f"{self.base_url}/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"

        all_records = []
        page_token = None

        while True:
            params = {"page_size": 500}
            if page_token:
                params["page_token"] = page_token

            resp = requests.get(url, headers=headers, params=params)
            result = resp.json()

            if result.get("code") == 0:
                data = result.get("data", {})
                records = data.get("items", [])
                all_records.extend(records)

                page_token = data.get("page_token")
                if not page_token:
                    break
            else:
                break

        return all_records

    def identify_obsolete_records(self, records: list) -> dict:
        """
        识别过时的记录

        Args:
            records: 所有记录

        Returns:
            {
                "obsolete": 需要删除的记录列表,
                "keep": 保留的记录列表,
                "stats": 统计信息
            }
        """
        obsolete = []
        keep = []

        brands_stats = {}

        for record in records:
            fields = record.get('fields', {})
            record_id = record.get('record_id')

            brand = fields.get('brand', 'Unknown')
            status = fields.get('status', '')
            published_date = fields.get('published_date')
            best_before = fields.get('best_before')

            # 判断是否过时
            is_obsolete = False
            reason = ""

            # 情况1: 召回状态是"已结束"且发布时间早于截止期
            if status == '已结束' and published_date:
                if published_date < self.cutoff_timestamp:
                    is_obsolete = True
                    reason = f"召回已结束超过{self.retention_days}天"

            # 情况2: 有效期早于截止期
            if best_before and best_before < self.cutoff_timestamp:
                is_obsolete = True
                reason = f"有效期已过{self.retention_days}天"

            # 情况3: 雅培 Abbott 的所有数据（全部是2022年的）
            if 'Abbott' in brand:
                is_obsolete = True
                reason = "雅培召回事件为2022年，产品已过期"

            # 统计品牌信息
            if brand not in brands_stats:
                brands_stats[brand] = {
                    "total": 0,
                    "obsolete": 0,
                    "keep": 0
                }

            brands_stats[brand]["total"] += 1

            if is_obsolete:
                obsolete.append({
                    "record_id": record_id,
                    "brand": brand,
                    "product_name": fields.get('product_name', ''),
                    "published_date": fields.get('published_date'),
                    "best_before": best_before,
                    "status": status,
                    "reason": reason
                })
                brands_stats[brand]["obsolete"] += 1
            else:
                keep.append({
                    "record_id": record_id,
                    "brand": brand,
                    "product_name": fields.get('product_name', ''),
                    "published_date": published_date,
                    "best_before": best_before,
                    "status": status
                })
                brands_stats[brand]["keep"] += 1

        return {
            "obsolete": obsolete,
            "keep": keep,
            "stats": {
                "total": len(records),
                "obsolete_count": len(obsolete),
                "keep_count": len(keep),
                "by_brand": brands_stats,
                "cutoff_date": self.cutoff_date.isoformat()
            }
        }

    def delete_records(self, record_ids: list, batch_size: int = 100) -> int:
        """
        批量删除记录

        Args:
            record_ids: 记录ID列表
            batch_size: 每批删除的记录数

        Returns:
            成功删除的数量
        """
        if not record_ids:
            print("没有记录需要删除")
            return 0

        token = self.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        url = f"{self.base_url}/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/batch_delete"

        success_count = 0
        failed_records = []

        # 分批删除
        for i in range(0, len(record_ids), batch_size):
            batch_ids = record_ids[i:i+batch_size]

            data = {
                "records": batch_ids
            }

            try:
                resp = requests.post(url, headers=headers, json=data)
                result = resp.json()

                if result.get("code") == 0:
                    deleted = len(result.get("data", {}).get("records", []))
                    success_count += deleted
                    print(f"  [{i+len(batch_ids)-1}/{len(record_ids)}] ✅ 已删除 {deleted} 条记录")
                else:
                    print(f"  [{i+len(batch_ids)-1}/{len(record_ids)}] ❌ 删除失败: {result.get('msg')}")
                    failed_records.extend(batch_ids)

            except Exception as e:
                print(f"  [{i+len(batch_ids)-1}/{len(record_ids)}] ❌ 删除异常: {e}")
                failed_records.extend(batch_ids)

        print(f"\n✅ 删除完成！成功删除 {success_count}/{len(record_ids)} 条记录")

        if failed_records:
            print(f"\n失败的记录数: {len(failed_records)}")

        return success_count

    def clean_data(self, dry_run: bool = False) -> dict:
        """
        清理过时数据

        Args:
            dry_run: 是否只模拟运行（不实际删除）

        Returns:
            清理结果
        """
        print("\n" + "=" * 70)
        print("数据清理脚本")
        print("=" * 70)
        print(f"保留策略: 最近 {self.retention_days} 天内的召回数据")
        print(f"截止日期: {self.cutoff_date.strftime('%Y-%m-%d')}")
        print(f"模式: {'模拟运行（不删除）' if dry_run else '实际删除数据'}")
        print()

        # 1. 获取所有记录
        print("1. 获取所有记录...")
        records = self.get_all_records()
        print(f"   ✅ 共获取 {len(records)} 条记录")

        # 2. 识别过时记录
        print("\n2. 识别过时记录...")
        result = self.identify_obsolete_records(records)

        # 3. 显示统计
        print("\n3. 统计信息:")
        print(f"   总记录数: {result['stats']['total']}")
        print(f"   需要删除: {result['stats']['obsolete_count']}")
        print(f"   需要保留: {result['stats']['keep_count']}")

        print("\n   按品牌统计:")
        for brand, stats in sorted(result['stats']['by_brand'].items()):
            print(f"   - {brand}:")
            print(f"     总数: {stats['total']}")
            print(f"     删除: {stats['obsolete']}")
            print(f"     保留: {stats['keep']}")

        # 4. 显示需要删除的样本
        if result['obsolete']:
            print(f"\n4. 删除样本（前10条）:")
            for i, r in enumerate(result['obsolete'][:10], 1):
                print(f"   {i}. {r['brand']} | {r['product_name']}")
                print(f"      原因: {r['reason']}")
                if r['published_date']:
                    pub_date = datetime.fromtimestamp(r['published_date']).strftime('%Y-%m-%d')
                    print(f"      发布日期: {pub_date}")

        # 5. 确认并删除
        if dry_run:
            print("\n⚠️  这是模拟运行，不会实际删除数据")
            return {
                "success": True,
                "dry_run": True,
                "result": result
            }

        print(f"\n共 {len(result['obsolete'])} 条记录将被删除")
        confirm = input("\n确认删除这些过时记录? (yes/no): ").strip().lower()

        if confirm != 'yes':
            print("\n已取消删除")
            return {
                "success": False,
                "message": "用户取消"
            }

        # 6. 执行删除
        print("\n5. 执行删除...")
        record_ids = [r['record_id'] for r in result['obsolete']]
        deleted_count = self.delete_records(record_ids, batch_size=100)

        return {
            "success": True,
            "deleted_count": deleted_count,
            "kept_count": result['stats']['keep_count'],
            "stats": result['stats']
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='清理过时的召回数据')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行，不实际删除')
    parser.add_argument('--yes', action='store_true', help='跳过确认，直接删除')

    args = parser.parse_args()

    cleaner = DataCleaner()

    if args.yes:
        # 跳过确认，直接删除
        result = cleaner.identify_obsolete_records(cleaner.get_all_records())

        print(f"\n共 {len(result['obsolete'])} 条记录将被删除")
        record_ids = [r['record_id'] for r in result['obsolete']]

        if not args.dry_run:
            deleted_count = cleaner.delete_records(record_ids)
            print(f"\n✅ 清理完成！删除了 {deleted_count} 条过时记录")
    else:
        # 正常流程（包含确认）
        result = cleaner.clean_data(dry_run=args.dry_run)

        if result.get('success') and not args.dry_run:
            print("\n" + "=" * 70)
            print("✅ 数据清理完成！")
            print("=" * 70)
            print(f"删除了 {result.get('deleted_count', 0)} 条过时记录")
            print(f"保留了 {result.get('kept_count', 0)} 条有效记录")
            print(f"\n建议:")
            print("- 定期运行清理脚本（每月一次）")
            print("- 调整数据保留策略（根据实际情况）")
            print("- 添加新召回数据的及时性")


if __name__ == "__main__":
    main()
