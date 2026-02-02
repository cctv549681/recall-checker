#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
召回数据爬虫模块
"""

from .base_scraper import BaseScraper
from .brand_config import get_all_sources, get_brand_config, get_brands_list, BRAND_CONFIGS
from .aptamil_scraper import AptamilScraper
from .feihe_scraper import FeiheScraper
from .friso_scraper import FrisoScraper
from .a2_scraper import A2Scraper
from .jinlingguan_scraper import JinlingguanScraper

__all__ = [
    'BaseScraper',
    'AptamilScraper',
    'FeiheScraper',
    'FrisoScraper',
    'A2Scraper',
    'JinlingguanScraper',
    'get_all_sources',
    'get_brand_config',
    'get_brands_list',
    'BRAND_CONFIGS'
]
