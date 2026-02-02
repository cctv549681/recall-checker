# 召回数据爬虫系统

> 多品牌、多国家的婴幼儿配方奶粉召回数据采集系统

---

## 📋 系统概述

本系统支持从各个品牌的官方渠道和政府监管平台抓取召回数据，并自动写入飞书多维表格。

### 支持的品牌

| 品牌 | 中文名 | 子品牌 | 支持国家/地区 |
|------|--------|--------|---------------|
| Nestlé | 雀巢 | SMA, ALFAMINO, NAN, BEBA | UK |
| Abbott | 雅培 | Similac, Alimentum, EleCare, Go & Grow | US |
| Aptamil | 爱他美 | Aptamil, Aptamil Essensis, Aptamil Profutura | UK, DE, AU, CN |
| Feihe | 飞鹤 | 星飞帆, 臻稚, 臻爱, 臻高 | CN |
| Friso | 美素佳儿 | 美素佳儿, 皇家美素佳儿, 美素力, 佳贝艾特 | CN, NL |
| a2 | a2至初 | a2至初, a2 Platinum, a2 Smart Nutrition | CN, NZ, AU |
| Jinlingguan | 金领冠 | 金领冠, 珍护, 睿护, 育护 | CN |

### 数据源

- **政府平台**：英国 FSA、中国 SAMR、德国 BVL、新西兰 MPI、澳大利亚 FSANZ、荷兰 NVWA
- **官方网站**：各品牌官网的召回公告页面

---

## 📁 项目结构

```
scraper/
├── scrapers/
│   ├── __init__.py              # 模块初始化
│   ├── base_scraper.py          # 爬虫基类
│   ├── brand_config.py          # 品牌配置
│   ├── aptamil_scraper.py       # 爱他美爬虫
│   ├── feihe_scraper.py         # 飞鹤爬虫
│   ├── friso_scraper.py         # 美素佳儿爬虫
│   ├── a2_scraper.py            # a2至初爬虫
│   ├── jinlingguan_scraper.py   # 金领冠爬虫
│   └── nestle_scraper.py        # 雀巢爬虫（旧版）
├── utils/
│   ├── feishu_config.py         # 飞书配置
│   ├── feishu_client.py         # 飞书客户端
│   └── feishu_tables.py         # 飞书表格管理
├── run_scrapers.py              # 统一运行器
├── abbott_scraper.py            # 雅培爬虫（旧版）
└── nestle_scraper.py            # 雀巢爬虫（旧版）
```

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.9+
- 依赖包：requests, beautifulsoup4, PyPDF2

### 2. 安装依赖

```bash
cd scraper
pip install -r requirements.txt
```

### 3. 配置飞书

编辑 `utils/feishu_config.py`：

```python
APP_ID = "your_app_id"
APP_SECRET = "your_app_secret"
APP_TOKEN = "your_app_token"
TABLE_ID = "your_table_id"
```

### 4. 运行爬虫

#### 查看所有数据源

```bash
python run_scrapers.py --sources
```

#### 运行单个品牌

```bash
python run_scrapers.py --brand aptamil
```

#### 运行所有品牌

```bash
python run_scrapers.py --all
```

#### 运行并插入飞书

```bash
python run_scrapers.py --all --insert
```

#### 运行并保存结果

```bash
python run_scrapers.py --all --save
```

---

## 📖 使用指南

### 命令行参数

| 参数 | 说明 |
|------|------|
| `--brand <brand_key>` | 运行单个品牌的爬虫（如：aptamil, feihe, friso, a2, jinlingguan） |
| `--all` | 运行所有品牌的爬虫 |
| `--insert` | 将抓取的数据插入飞书表格 |
| `--save` | 保存抓取结果到 JSON 文件 |
| `--sources` | 显示所有数据源 |

### 示例

1. **抓取爱他美的召回数据**

```bash
python run_scrapers.py --brand aptamil
```

2. **抓取飞鹤的召回数据并插入飞书**

```bash
python run_scrapers.py --brand feihe --insert
```

3. **抓取所有品牌的召回数据**

```bash
python run_scrapers.py --all
```

4. **抓取所有品牌、插入飞书、保存结果**

```bash
python run_scrapers.py --all --insert --save
```

---

## 🔧 开发指南

### 创建新品牌爬虫

1. 在 `scrapers/` 目录下创建新的爬虫文件（如 `mybrand_scraper.py`）

2. 继承 `BaseScraper` 类

```python
from .base_scraper import BaseScraper
from typing import List, Dict, Any

class MyBrandScraper(BaseScraper):
    def __init__(self):
        super().__init__("品牌中文名", "BrandName")

    def scrape(self) -> List[Dict[str, Any]]:
        # 实现抓取逻辑
        products = []
        # ... 抓取代码 ...
        return products
```

3. 在 `brand_config.py` 中添加品牌配置

```python
"mybrand": {
    "name": "品牌中文名",
    "name_en": "BrandName",
    "sub_brands": ["子品牌1", "子品牌2"],
    "sources": [
        {
            "country": "CN",
            "source_type": "政府平台",
            "url": "https://example.com/recalls",
            "parser": "my_parser"
        }
    ]
}
```

4. 在 `run_scrapers.py` 中注册爬虫

```python
from scrapers.mybrand_scraper import MyBrandScraper

class RecallScraperRunner:
    def __init__(self):
        self.scrapers = {
            # ... 其他爬虫 ...
            "mybrand": MyBrandScraper
        }
```

### 数据格式

爬虫返回的产品数据格式：

```python
{
    "product_name": "产品名称",
    "sub_brand": "子品牌",
    "pack_size": "800g",
    "batch_codes": ["批次号1", "批次号2"],
    "best_before": 1736841600,  # 时间戳
    "region": "CN",
    "recall_reason": "召回原因",
    "risk_level": "高",
    "source_type": "政府平台",
    "published_date": 1736841600,
    "status": "召回中"
}
```

---

## 📊 飞书表格字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| brand | 文本 | 品牌（雀巢、Abbott等） |
| brand_en | 文本 | 品牌英文名 |
| product_name | 文本 | 产品名称 |
| sub_brand | 文本 | 子品牌（SMA、NAN） |
| batch_codes | 文本 | 批次号（逗号分隔） |
| pack_size | 文本 | 包装规格（800g、400g） |
| best_before | 日期时间 | 有效期 |
| region | 文本 | 受影响地区 |
| recall_reason | 文本 | 召回原因 |
| risk_level | 单选 | 风险等级（高/中/低） |
| source_url | 超链接 | 官方来源链接 |
| source_type | 单选 | 数据源类型 |
| published_date | 日期时间 | 发布日期 |
| last_updated | 日期时间 | 最后更新日期 |
| status | 单选 | 状态（召回中/已结束/待确认） |

---

## 🔍 常见问题

### Q: 为什么没有抓到数据？

A: 可能的原因：
1. 网站结构发生变化，需要更新解析逻辑
2. 网站反爬虫机制，需要添加请求头或使用代理
3. 该品牌当前没有召回信息

### Q: 如何处理动态加载的页面？

A: 使用 Playwright 或 Selenium：

```python
from playwright.sync_api import sync_playwright

def scrape_dynamic_page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('https://example.com')
        # 等待页面加载
        page.wait_for_selector('.recall-item')
        html = page.content()
        # 解析 HTML
        browser.close()
```

### Q: 如何避免被封IP？

A: 建议方法：
1. 添加随机延迟
2. 使用代理IP池
3. 设置合理的请求头
4. 控制爬取频率

### Q: 如何调试爬虫？

A: 查看日志和打印信息：

```python
# 在爬虫中添加调试信息
print(f"抓取URL: {url}")
print(f"HTML长度: {len(html)}")
print(f"找到的产品数: {len(products)}")
```

---

## 📝 注意事项

1. **遵守网站规则**：尊重网站的 robots.txt 和使用条款
2. **合理设置频率**：避免对目标网站造成过大压力
3. **数据验证**：抓取后验证数据准确性
4. **定期更新**：网站结构可能变化，需要定期维护爬虫
5. **免责声明**：本系统仅供参考，不构成法律依据

---

## 🤝 贡献指南

欢迎贡献代码和提出建议：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

MIT License

---

**版本**：v2.0
**最后更新**：2026-01-30
**维护者**：产品+开发团队
