#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品牌配置 - 召回数据源配置
"""

# 品牌召回数据源配置
BRAND_CONFIGS = {
    "nestle": {
        "name": "雀巢",
        "name_en": "Nestlé",
        "sub_brands": ["SMA", "ALFAMINO", "NAN", "BEBA"],
        "sources": [
            {
                "country": "UK",
                "source_type": "政府平台",
                "url": "https://www.food.gov.uk/news-alerts/alert/fsa-prin-02-2026-update-1",
                "parser": "fsa_alert"
            }
        ]
    },
    "abbott": {
        "name": "雅培",
        "name_en": "Abbott",
        "sub_brands": ["Similac", "Alimentum", "EleCare", "Go & Grow"],
        "sources": [
            {
                "country": "US",
                "source_type": "媒体PDF",
                "url": "https://www.cbsnews.com/htdocs/pdf/SimilacLotList.pdf",
                "parser": "pdf_lot_list"
            }
        ]
    },
    "aptamil": {
        "name": "爱他美",
        "name_en": "Aptamil",
        "sub_brands": ["Aptamil", "Aptamil Essensis", "Aptamil Profutura"],
        "sources": [
            {
                "country": "UK",
                "source_type": "政府平台",
                "url": "https://www.food.gov.uk/news-alerts",
                "parser": "fsa_recall"
            },
            {
                "country": "DE",
                "source_type": "政府平台",
                "url": "https://www.bvl.bund.de",
                "parser": "bvl_recall"
            },
            {
                "country": "AU",
                "source_type": "政府平台",
                "url": "https://www.foodstandards.gov.au",
                "parser": "fsanz_recall"
            },
            {
                "country": "CN",
                "source_type": "政府平台",
                "url": "https://www.samr.gov.cn",
                "parser": "samr_recall"
            }
        ]
    },
    "feihe": {
        "name": "飞鹤",
        "name_en": "Feihe",
        "sub_brands": ["星飞帆", "臻稚", "臻爱", "臻高"],
        "sources": [
            {
                "country": "CN",
                "source_type": "政府平台",
                "url": "https://www.samr.gov.cn",
                "parser": "samr_recall"
            },
            {
                "country": "CN",
                "source_type": "官网",
                "url": "https://www.feihe.com",
                "parser": "feihe_official"
            }
        ]
    },
    "friso": {
        "name": "美素佳儿",
        "name_en": "Friso",
        "sub_brands": ["美素佳儿", "皇家美素佳儿", "美素力", "佳贝艾特"],
        "sources": [
            {
                "country": "CN",
                "source_type": "政府平台",
                "url": "https://www.samr.gov.cn",
                "parser": "samr_recall"
            },
            {
                "country": "CN",
                "source_type": "官网",
                "url": "https://www.friso.com.cn",
                "parser": "friso_official"
            },
            {
                "country": "NL",
                "source_type": "政府平台",
                "url": "https://www.nvwa.nl",
                "parser": "nvwa_recall"
            }
        ]
    },
    "a2": {
        "name": "a2至初",
        "name_en": "a2",
        "sub_brands": ["a2至初", "a2 Platinum", "a2 Smart Nutrition"],
        "sources": [
            {
                "country": "CN",
                "source_type": "政府平台",
                "url": "https://www.samr.gov.cn",
                "parser": "samr_recall"
            },
            {
                "country": "CN",
                "source_type": "官网",
                "url": "https://www.a2nutrition.com.cn",
                "parser": "a2_official"
            },
            {
                "country": "NZ",
                "source_type": "政府平台",
                "url": "https://www.mpi.govt.nz",
                "parser": "mpi_recall"
            },
            {
                "country": "AU",
                "source_type": "政府平台",
                "url": "https://www.foodstandards.gov.au",
                "parser": "fsanz_recall"
            }
        ]
    },
    "jinlingguan": {
        "name": "金领冠",
        "name_en": "Jinlingguan",
        "sub_brands": ["金领冠", "珍护", "睿护", "育护"],
        "sources": [
            {
                "country": "CN",
                "source_type": "政府平台",
                "url": "https://www.samr.gov.cn",
                "parser": "samr_recall"
            },
            {
                "country": "CN",
                "source_type": "官网",
                "url": "https://www.yili.com",
                "parser": "yili_official"
            }
        ]
    }
}


def get_brands_list():
    """获取所有品牌列表"""
    return list(BRAND_CONFIGS.keys())


def get_brand_config(brand_key: str) -> dict:
    """获取品牌配置"""
    return BRAND_CONFIGS.get(brand_key)


def get_all_sources():
    """获取所有数据源"""
    sources = []
    for brand_key, config in BRAND_CONFIGS.items():
        for source in config["sources"]:
            sources.append({
                "brand_key": brand_key,
                "brand_name": config["name"],
                "brand_name_en": config["name_en"],
                **source
            })
    return sources
