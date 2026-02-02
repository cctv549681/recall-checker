#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版数据源修复工具 - 快速检查关键URL
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time


def test_url(url, timeout=5):
    """测试URL是否可访问"""
    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=True)
        return (True, resp.url, resp.status_code)
    except Exception as e:
        return (False, str(e), 0)


def main():
    print("=" * 70)
    print("快速数据源检查")
    print("=" * 70)

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    # 1. SAMR关键URL
    print("\n1. 中国SAMR关键URL:")
    samr_urls = [
        "https://www.samr.gov.cn/",
        "https://www.samr.gov.cn/cpzljd/",
        "https://www.samr.gov.cn/tzgg/",
        "https://www.samr.gov.cn/cpzljd/cpzhc/",
        "https://www.samr.gov.cn/zw/cpzljd/",
        "https://www.samr.gov.cn/zljds/",
    ]

    working_samr = []
    for url in samr_urls:
        success, result, status = test_url(url, timeout=5)
        if success and status == 200:
            print(f"  ✅ {url}")
            working_samr.append(url)
        else:
            print(f"  ❌ {url} ({result})")
        time.sleep(0.3)

    # 2. FDA关键URL
    print("\n2. 美国FDA关键URL:")
    fda_urls = [
        "https://www.fda.gov/",
        "https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts",
        "https://www.fda.gov/food/recalls-outbreaks-contaminations",
        "https://www.fda.gov/food/recalls",
        "https://www.fda.gov/safety/recalls",
    ]

    working_fda = []
    for url in fda_urls:
        success, result, status = test_url(url, timeout=5)
        if success and status == 200:
            print(f"  ✅ {url}")
            working_fda.append(url)
        else:
            print(f"  ❌ {url} ({result})")
        time.sleep(0.3)

    # 3. 品牌官网关键URL
    print("\n3. 品牌官网:")
    brand_urls = {
        "爱他美": "https://www.aptamil.cn/",
        "美素佳儿": "https://www.friso.com.cn/",
        "a2": "https://www.a2nutrition.com.cn/",
    }

    working_brands = {}
    for brand, url in brand_urls.items():
        success, result, status = test_url(url, timeout=5)
        if success and status == 200:
            print(f"  ✅ {brand}: {url}")
            working_brands[brand] = url
        else:
            print(f"  ❌ {brand}: {url} ({result})")
        time.sleep(0.3)

    # 4. 替代数据源
    print("\n4. 替代数据源:")
    alt_sources = [
        "https://www.foodstandards.gov.au/pages/recalls/",
        "https://www.mpi.govt.nz/food-business/food-recalls",
        "https://ec.europa.eu/food/safety/rasff_en",
    ]

    working_alt = []
    for url in alt_sources:
        success, result, status = test_url(url, timeout=8)
        if success and status == 200:
            print(f"  ✅ {url}")
            working_alt.append(url)
        else:
            print(f"  ❌ {url} ({result})")
        time.sleep(0.5)

    # 生成总结
    print("\n" + "=" * 70)
    print("检查总结")
    print("=" * 70)

    print(f"\nSAMR可用: {len(working_samr)} 个")
    print(f"FDA可用: {len(working_fda)} 个")
    print(f"品牌官网: {len(working_brands)} 个")
    print(f"替代数据源: {len(working_alt)} 个")

    if working_samr or working_fda or working_alt:
        print("\n✅ 建议使用的URL:")
        for url in (working_samr + working_fda + working_alt)[:5]:
            print(f"  - {url}")
    else:
        print("\n⚠️  未找到可用的数据源，需要手动探索")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
