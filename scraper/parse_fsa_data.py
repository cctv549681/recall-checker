"""
快速解析FSA召回页面数据（不使用Playwright）
"""

import re
from datetime import datetime


def parse_fsa_data():
    """解析FSA页面数据（之前获取的HTML内容）"""

    # 从web_fetch结果中提取的批次号数据
    fsa_data = """
    SMA Advanced First Infant Milk
    Pack size: 800g
    Batch code: 51450742F1, 52319722BA, 52819722AA
    Best before: May 2027

    SMA Advanced Follow-On Milk
    Pack size: 800g
    Batch code: 51240742F2
    Best before: May 2027
    Batch code: 51890742F2, 52879722AA
    Best before: July 2027

    SMA Anti Reflux
    Pack size: 800g
    Batch code: 51570742F3
    Best before: June 2027
    Batch code: 52099722BA
    Best before: April 2027
    Batch code: 52099722BB, 52739722BA
    Best before: June 2027

    SMA ALFAMINO
    Pack size: 400g
    Batch code: 51200017Y3
    Best before: April 2027
    Batch code: 51210017Y1, 51220017Y1
    Best before: May 2027
    Batch code: 51250017Y1, 51390017Y1, 51420017Y2, 51430017Y1, 51460017Y1
    Best before: May 2027
    Batch code: 51690017Y2, 51690017Y3, 51700017Y1, 51710017Y1, 51740017Y1
    Best before: June 2027
    Batch code: 52760017Y5, 52790017Y1, 52860017Y1
    Best before: October 2027
    Batch code: 53100017Y3, 53110017Y1, 53140017Y1, 53140017Y2, 53150017Y1
    Best before: November 2027

    SMA First Infant Milk
    Pack size: 800g
    Batch code: 51170346AA, 51170346AB
    Best before: April 2027
    Batch code: 51340346AB
    Best before: May 2027
    Batch code: 51580346AA, 51590346AA, 51590346AB
    Best before: June 2027
    Batch code: 52760346AB, 52760346AD, 52780346AA, 52750346AE
    Best before: October 2027

    SMA First Infant Milk
    Pack size: 400g
    Batch code: 51350346AA
    Best before: May 2027
    Batch code: 52750346AD
    Best before: October 2027

    SMA First Infant Milk
    Pack size: 1.2kg
    Batch code: 51340346BE
    Best before: November 2026
    Batch code: 52740346BA, 52750346BA
    Best before: April 2027

    SMA LITTLE STEPS First Infant Milk
    Pack size: 800g
    Batch code: 51220346AD
    Best before: May 2027
    Batch code: 51540346AC
    Best before: June 2027
    Batch code: 52740346AD
    Best before: October 2027

    SMA Comfort
    Pack size: 800g
    Batch code: 52620742F3
    Best before: September 2027
    Batch code: 51240742F3, 51439722BA, 51479722BA, 51769722BA, 52049722AA
    Best before: May 2027

    SMA First Infant Milk
    Pack size: 200ml
    Batch code: 52860295M, 52870295M, 52870295M, 53030295M, 53040295M
    Best before: October 2026
    Batch code: 53220295M, 53230295M, 53070295M, 53080295M
    Best before: November 2026

    SMA First Infant Milk
    Pack size: 70ml
    Batch code: 53170742B1
    Best before: November 2026

    SMA Lactose Free
    Pack size: 400g
    Batch code: 51500346AB
    Best before: May 2027
    Batch code: 53299722BA
    Best before: August 2027
    Batch code: 51150346AB, 51719722BA, 51759722BA, 51829722BA, 51979722BA, 52109722BA, 53459722BA
    Best before: April 2027
    """

    # 解析数据
    products = []
    lines = fsa_data.strip().split('\n')
    current_product = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 产品名称（第一列）
        if 'Pack size:' not in line and 'Batch code:' not in line and 'Best before:' not in line:
            # 新产品
            if current_product and current_product.get('batch_codes'):
                products.append(current_product)
            current_product = {
                'product_name': line,
                'brand': '雀巢 Nestlé',
                'brand_en': 'Nestlé',
                'sub_brand': line.split()[0] if ' ' in line else line,
                'batch_codes': [],
                'pack_size': None,
                'best_before': None,
                'region': 'UK',
                'recall_reason': 'Cereulide毒素（蜡样芽孢杆菌产生的耐热性呕吐毒素）',
                'risk_level': '高',
                'source_url': 'https://www.food.gov.uk/news-alerts/alert/fsa-prin-02-2026-update-1',
                'source_type': '政府平台',
                'published_date': '2026-01-09',
                'last_updated': datetime.now().isoformat(),
                'status': '召回中'
            }

        elif 'Pack size:' in line:
            if current_product:
                pack_size = line.replace('Pack size:', '').strip()
                current_product['pack_size'] = pack_size

        elif 'Batch code:' in line:
            if current_product:
                batch_codes_str = line.replace('Batch code:', '').strip()
                batch_codes = [code.strip() for code in batch_codes_str.split(',')]
                current_product['batch_codes'].extend(batch_codes)

        elif 'Best before:' in line:
            if current_product:
                best_before = line.replace('Best before:', '').strip()
                current_product['best_before'] = best_before

    # 添加最后一个产品
    if current_product and current_product.get('batch_codes'):
        products.append(current_product)

    return products


def main():
    """主函数"""
    print("=" * 70)
    print("解析雀巢召回数据（FSA）")
    print("=" * 70)

    products = parse_fsa_data()

    print(f"\n✅ 成功解析 {len(products)} 个召回产品\n")

    for i, product in enumerate(products, 1):
        print(f"{i}. {product['product_name']}")
        print(f"   子品牌: {product['sub_brand']}")
        print(f"   规格: {product['pack_size']}")
        print(f"   批次号: {len(product['batch_codes'])} 个")
        print(f"   有效期: {product['best_before']}")
        print(f"   批次号: {', '.join(product['batch_codes'][:3])}{'...' if len(product['batch_codes']) > 3 else ''}")
        print()

    # 统计
    total_batches = sum(len(p['batch_codes']) for p in products)
    print("=" * 70)
    print(f"📊 统计:")
    print(f"   产品数: {len(products)}")
    print(f"   批次号总数: {total_batches}")
    print("=" * 70)

    # 保存到JSON
    import json
    output_file = "/Users/jiang/clawd/recall-checker/data/nestle_recalls.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 数据已保存到: {output_file}")

    # 保存为CSV格式（便于导入飞书）
    import csv
    csv_file = "/Users/jiang/clawd/recall-checker/data/nestle_recalls.csv"

    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'brand', 'brand_en', 'product_name', 'sub_brand',
            'batch_codes', 'pack_size', 'best_before', 'region',
            'recall_reason', 'risk_level', 'source_url', 'source_type',
            'published_date', 'last_updated', 'status'
        ])

        for product in products:
            writer.writerow([
                product['brand'],
                product['brand_en'],
                product['product_name'],
                product['sub_brand'],
                ', '.join(product['batch_codes']),
                product['pack_size'],
                product['best_before'],
                product['region'],
                product['recall_reason'],
                product['risk_level'],
                product['source_url'],
                product['source_type'],
                product['published_date'],
                product['last_updated'],
                product['status']
            ])

    print(f"✅ CSV数据已保存到: {csv_file}")


if __name__ == "__main__":
    main()
