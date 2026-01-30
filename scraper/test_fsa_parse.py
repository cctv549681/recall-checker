#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试解析 FSA 页面数据
"""
import requests
from bs4 import BeautifulSoup


def test_fsa_parse():
    """测试 FSA 页面解析"""
    print("=" * 70)
    print("测试 FSA 页面解析")
    print("=" * 70)

    url = "https://www.food.gov.uk/news-alerts/alert/fsa-prin-02-2026-update-1"

    print(f"\n抓取页面: {url}")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    # 使用 BeautifulSoup 解析
    soup = BeautifulSoup(resp.text, 'html.parser')

    # 找到产品详情部分
    # FSA 页面中，产品信息在 h2 标签或类似结构中

    # 打印页面结构，找到产品信息的位置
    print("\n查找产品名称...")

    # 方法1: 查找所有 h2/h3 标签
    headings = soup.find_all(['h2', 'h3'])
    print(f"找到 {len(headings)} 个标题\n")

    for i, h in enumerate(headings[:15], 1):
        text = h.get_text(strip=True)
        if text and not text.startswith('Product details'):
            print(f"{i}. {text[:80]}")

    print("\n" + "=" * 70)
    print("查找产品详情结构...")
    print("=" * 70 + "\n")

    # 查找包含 "Pack size" 的部分
    for tag in soup.find_all(text=lambda text: text and 'Pack size' in text):
        parent = tag.parent
        print(f"找到 Pack size:")
        print(f"  标签: {parent.name}")
        print(f"  HTML: {str(parent)[:200]}")
        print()

        # 查找相邻的批次号
        next_sibling = parent.find_next_sibling()
        if next_sibling:
            print(f"  下一元素: {next_sibling.name} - {next_sibling.get_text(strip=True)[:100]}")
        print("-" * 70)


if __name__ == "__main__":
    test_fsa_parse()
